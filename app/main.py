import datetime
import json
import os
import re
import time
import uuid

from redis import StrictRedis
from flask import Flask, request, render_template, jsonify, redirect
from flask_migrate import Migrate
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import WebDriverException

from fuzzywuzzy import process as fuzzy_process
from werkzeug.exceptions import BadRequest

from model import db, Domain

app = Flask(__name__, static_url_path='')
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

rs = StrictRedis(host='redis', decode_responses=True)


@app.route('/push', methods=['POST'])
def push():
    dn = Domain()
    dn.uid = str(uuid.uuid4())
    dn.name = request.form['domain']
    dn.status = "legitimate"

    if not re.match(r'^[a-zA-Z0-9-_\\.]+$', dn.name):
        raise BadRequest('Invalid domain name')

    while dn.name.startswith('*.'):
        dn.name = dn.name.split('.', 1)[1]

    keywords = app.config['SUSPICIOUS_KEYWORDS']
    matches = []

    for k in keywords:
        matches.extend([{"keyword": k, "matched": word, "score": score}
                        for word, score in fuzzy_process.extractBests(k, (dn.name,), score_cutoff=70)])

    if matches or request.form.get('from-ui'):
        dn.status = "check-queued"

    try:
        db.session.add(dn)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if request.form.get('from-ui'):
            return redirect('/')

        return jsonify({"status": "already-exists", "matches": matches})
    else:
        if matches or request.form.get('from-ui'):
            rs.rpush('screen-jobs', json.dumps({"uid": dn.uid}))

        if request.form.get('from-ui'):
            return redirect('/')

        return jsonify({"status": dn.status, "matches": matches})


@app.route('/set_status/<domain_uid>', methods=['POST'])
def vote(domain_uid):
    dn = Domain.query.get(domain_uid)
    dn.status = request.form['status']
    db.session.merge(dn)
    db.session.flush()
    db.session.commit()

    return redirect('/')


@app.route('/')
def main():
    check_later = db.session.query(Domain.uid).filter(Domain.status == "check-later").count()
    check_queued = db.session.query(Domain.uid).filter(Domain.status == "check-queued").count()
    domains = Domain.query.filter(Domain.status == "manual-check").order_by(Domain.time_added.asc()).limit(1).all()
    return render_template('domains.html', domains=domains, check_later=check_later, check_queued=check_queued)


@app.route('/all')
def all_domains():
    domains = Domain.query.order_by(Domain.time_added.asc()).all()
    keywords = ', '.join(app.config['SUSPICIOUS_KEYWORDS'])

    return render_template('all.html', domains=domains, keywords=keywords)


@app.route('/malicious')
def malicious_domains():
    domains = Domain.query.filter(Domain.status == "malicious").order_by(Domain.time_added.asc()).all()

    return render_template('malicious.html', domains=domains)


@app.cli.command('requeue-worker')
def requeue_worker():
    while True:
        print('Running requeue...')
        time.sleep(2.0)

        recheck_interval = datetime.timedelta(seconds=app.config['RECHECK_TIME_SEC'])
        requeue_domains = Domain.query.filter(and_(
            Domain.status == "check-later",
            Domain.last_checked < datetime.datetime.utcnow() - recheck_interval)).all()

        for dn in requeue_domains:
            print('Requeue domain: {}'.format(dn.name))
            dn.status = "check-queued"
            db.session.merge(dn)
            rs.rpush('screen-jobs', json.dumps({"uid": dn.uid}))

        db.session.flush()
        db.session.commit()


@app.cli.command('screenshot-worker')
def screenshot_worker():
    while True:
        print('Waiting for a new job...')

        driver = None
        data = rs.blpop('screen-jobs', timeout=30)

        if not data:
            continue

        job = json.loads(data[1])
        dn = Domain.query.get(job['uid'])
        dn.last_checked = datetime.datetime.utcnow()
        print('Fetching website: {}'.format(dn.name))

        try:
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub',
                                      desired_capabilities=DesiredCapabilities.CHROME)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(30)
            driver.get('http://' + dn.name)
            domain_root = os.path.join('/app/static/screenshots', dn.uid)
            os.makedirs(domain_root, exist_ok=True)
            driver.save_screenshot(os.path.join(domain_root, 'screenshot.png'))
            dn.status = "manual-check"
        except WebDriverException as e:
            print('WebDriverException: ' + str(e))
            dn.status = "fetch-error"
        finally:
            db.session.merge(dn)
            db.session.flush()
            db.session.commit()

            if driver:
                driver.quit()
