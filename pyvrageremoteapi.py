#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This file is part of pyvrageremoteapi
#
# MIT License
#
# Copyright (c) 2020 chris007de
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# html requests
import requests
# htmldate
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
# nonce
import time
from itertools import count
# hmac
import hmac
import hashlib
# basee64 conversions
import base64
# json
import json
# argparse
import argparse

NONCE_COUNTER = count(int(time.time() * 1000))


class pyvrageremoteAPI(object):
    """Class for getting a response from the vrageremote API"""

    def __get_htmldate(self):
        """Get current timestamp in HTML date format (RFC1123)"""
        now = datetime.now()
        stamp = mktime(now.timetuple())
        return format_date_time(stamp)  # --> Wed, 22 Oct 2008 10:52:40 GMT

    def __get_nonce(self):
        """Get a unique nonce"""
        return str(next(NONCE_COUNTER))

    def __build_message(self, method_url, nonce, htmldate):
        """Build the message to be sent to the API server"""
        return method_url + "\r\n" + nonce + "\r\n" + htmldate + "\r\n"

    def __build_hash(self, message):
        """Compute hash from the message to be sent"""
        key_decoded = base64.b64decode(self.key)
        signature = hmac.new(key_decoded, message.encode('utf-8'),
                             hashlib.sha1)
        return base64.b64encode(signature.digest()).decode()

    def __build_request(self, resource):
        """Build a custom request according to the vrageremote API spec"""
        method_url = self.remote_url + resource
        full_url = self.url + method_url
        nonce = self.__get_nonce()
        htmldate = self.__get_htmldate()

        message = self.__build_message(method_url, nonce, htmldate)
        hmac_hash = self.__build_hash(message)

        headers = {'Date': '',
                   'Authorization': ''}
        headers['Date'] = htmldate
        headers['Authorization'] = nonce + ":" + hmac_hash

        request = requests.Request('GET', full_url, headers=headers)
        return request

    def get_resource_by_name(self, resource):
        """Get a resource from API, e.g. 'server', returns JSON data"""
        request = self.__build_request(resource)
        prepped_request = request.prepare()

        with requests.Session() as session:
            response = session.send(prepped_request)
            json_data = json.loads(response.text)
            print(json_data)
            return json_data

    def get_resource_server(self):
        """Get resource 'server'"""
        return self.get_resource_by_name('server')

    def __init__(self, url, key):
        self.url = url
        self.key = key

        self.remote_url = "/vrageremote/v1/"


def setup_parser():
    parser = argparse.ArgumentParser(description='Get data from a \
            vrageremote API server')
    parser.add_argument('--url', required=True,
                        help='of the remote server, \
                        e.g. http://localhost:8080')
    parser.add_argument('--key', required=True,
                        help='secret key for the remote API, \
                        e.g. XKb8xk7vrKaq+BpallYnGA==')
    parser.add_argument('--resource', required=True,
                        help='resource to be fetched, e.g. server/ping')
    return parser


def parse_arguments(parser):
    args = parser.parse_args()

    url = args.url
    key = args.key
    resource = args.resource
    return url, key, resource


if __name__ == '__main__':
    parser = setup_parser()
    url, key, resource = parse_arguments(parser)
    api = pyvrageremoteAPI(url, key)
    api.get_resource_by_name(resource)
