import argparse
import json
import logging
import os
from urllib.request import urlopen
from urllib.parse import urlencode

DREAMHOST_API_KEY = os.environ["DREAMHOST_API_KEY"]


def cfg_logger(level="info"):
    level = level.upper() # logging expects DEBUG, INFO, etc
    logging.basicConfig(
        level=level,
        format="%(asctime)s|%(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _call(cmd, **params):
    params['cmd'] = cmd
    params['key'] = DREAMHOST_API_KEY
    params['format'] = 'json'
    qs = urlencode(params)
    url = f"https://api.dreamhost.com?{qs}"
    logging.info('loading %s', url)
    resp = urlopen(url)

    resp_text = resp.read().decode()
    try:
        resp_data = json.loads(resp_text)
    except json.decoder.JSONDecodeError:
        logging.error('Non-JSON response from %s', url)
        logging.error(resp_text)
        resp_data = None

    if resp_data.get('result') =='error':
        logging.error(resp_data)
    return resp_data


def dns_list_records():
    cmd = 'dns-list_records'
    resp = _call(cmd, type='A')
    return resp


def dns_add_record(current_ip, record):
    cmd = 'dns-add_record'
    logging.info('creating record for %s', current_ip)
    resp = _call(cmd, record=record, type='A', value=current_ip)
    logging.info('attempted to create dns %r', resp)


def dns_remove_record(ip, hostname):
    cmd = 'dns-remove_record'
    resp = _call(cmd, value=ip, type='A', record=hostname)
    logging.info('attempted to remove dns record %r', resp)


def _get_current_ip(records, hostname):
    rec_type = 'A'
    for record in records['data']:
        if record['type'] != rec_type:
            continue
        if record['record'] == hostname:
            return record['value']
    logging.error('cannot find %s record for %s', rec_type, DREAMHOST_DNS_DOMAIN)


def update_ip(hostname, new_ip):
    records = dns_list_records()
    dns_ip = _get_dns_ip(records, hostname)
    if dns_ip == new_ip:
        message = f'dns_ip and new_ip match {new_ip}. No need to update'
    elif not dns_ip:
        dns_add_record(new_ip, hostname)
        message = f'dns record added {new_ip}'
    else:
        dns_remove_record(dns_ip, hostname)
        dns_add_record(new_ip, hostname)
        message =  f'dns record updated {new_ip}'
    logging.info(message)


def main():
    parser = argparse.ArgumentParser("""
    Update DreamHost DNS records
    """)
    # TODO


if __name__ == '__main__':
    main()
