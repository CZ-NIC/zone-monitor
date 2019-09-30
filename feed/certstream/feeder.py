#!/usr/local/bin/python3

import logging
import sys
import datetime
import certstream
import requests

def print_callback(message, context):
    logging.debug("Message -> {}".format(message))

    if message['message_type'] == "heartbeat":
        return

    if message['message_type'] == "certificate_update":
        all_domains = message['data']['leaf_cert']['all_domains']

        if len(all_domains) == 0:
            return

        filtered = [dn for dn in all_domains if dn.endswith('.cz')]

        if not filtered:
            return

        for dn in filtered:
            res = requests.post('http://app/push', data={'domain': dn})
            res.raise_for_status()

        sys.stdout.write(u"[{}] {}\n".format(datetime.datetime.now().strftime('%m/%d/%y %H:%M:%S'), ",".join(filtered)))
        sys.stdout.flush()

logging.basicConfig(format='[%(levelname)s:%(name)s] %(asctime)s - %(message)s', level=logging.INFO)

certstream.listen_for_events(print_callback, url='ws://certstream-server:8080/')

