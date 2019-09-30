import os

from redis import StrictRedis
from tempfile import NamedTemporaryFile
from flask import Flask, escape, request, send_file, after_this_request, render_template, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import WebDriverException

from model import db, Domain

app = Flask(__name__, static_url_path='')
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

rs = StrictRedis(host='redis', decode_responses=True)

@app.route('/screenshot')
def screenshot():
    @after_this_request
    def cleanup(response):
        tmpf.close()
        return response

    tmpf = NamedTemporaryFile(suffix='.png', delete=False)

    try:
        driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
        driver.get(request.args.get('url'))
        driver.save_screenshot(tmpf.name)
    except WebDriverException as e:
        raise RuntimeError(str(e))
    finally:
        driver.quit()

    return send_file(tmpf.name, as_attachment=False)


@app.route('/push', methods=['POST'])
def push():
    dn = Domain()
    dn.name = request.form['domain']

    try:
        db.session.add(dn)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"status": "already-exists"})
    else:
        rs.rpush('screen-jobs', dn.name)
        return jsonify({"status": "new"})


@app.route('/')
def main():
    domains = Domain.query.all()

    return render_template('domains.html', domains=domains)


@app.cli.command('screenshot-worker')
def screenshot_worker():
    while True:
        job = rs.blpop('screen-jobs')[1]
        try:
            driver = webdriver.Remote(command_executor='http://hub:4444/wd/hub', desired_capabilities=DesiredCapabilities.CHROME)
            driver.get('http://' + job)
            driver.save_screenshot(os.path.join('/app/static/screenshots', job + '.png'))
        except WebDriverException as e:
            print('WebDriverException: ' + str(e))
        finally:
            driver.quit()

