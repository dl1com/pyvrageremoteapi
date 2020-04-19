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

# argparse
import argparse
# time
import datetime
import pytz
# Influx
from influxdb import InfluxDBClient

from pyvrageremoteapi import pyvrageremoteAPI


class SpaceEngineersMetrics(object):
    """Get Metrics from a Space Engineers Remote API and store to InfluxDB"""

    def __setup_parser(self):
        self.parser = argparse.ArgumentParser(description='Get data from a \
                vrageremote API server')
        self.parser.add_argument('--url', required=True,
                                 help='of the remote server, \
                                 e.g. http://localhost:8080')
        self.parser.add_argument('--key', required=True,
                                 help='secret key for the remote API, \
                                 e.g. XKb8xk7vrKaq+BpallYnGA==')
        self.parser.add_argument('--db_host', required=True,
                                 help='Hostname of the InfluxDB Server, \
                                 example: http://localhost')
        self.parser.add_argument('--db_port',
                                 help='Port of the InfluxDB Server \
                                 (default: ' + str(self.db_port) + ')')
        self.parser.add_argument('--db_name',
                                 help='Name of the InfluxDB database \
                                 (default: ' + self.db_name + ')')

    def __parse_arguments(self):
        args = self.parser.parse_args()

        self.url = args.url
        self.key = args.key
        self.db_host = args.db_host

        if args.db_port is not None:
            self.db_port = args.db_port
        if args.db_name is not None:
            self.db_name = args.db_name

    def __connect_to_InfluxDB(self):
        """Establish connection to InfluxDB and return client object"""
        try:
            client = InfluxDBClient(host=self.db_host, port=self.db_port)
        except:
            print("Could not connect to InfluxDB on " + self.db_host
                  + ":" + str(self.db_port))
            exit()
        client.create_database(self.db_name)
        client.switch_database(self.db_name)
        return client

    def __get_timestamp(self):
        timestamp = datetime.datetime.now()
        timestamp = pytz.timezone('Europe/Berlin').localize(timestamp)
        timestamp = timestamp.astimezone(pytz.utc)
        return str(timestamp)

    def __convert_data_to_influx_json(self, json_data):
        """ Format JSON object for insertion to InfluxDB"""
        timestamp = self.__get_timestamp()
        print(timestamp)
        json_body = [
            {
                "measurement": "server",
                "time": timestamp,
                "fields": {
                    "TotalTime": int(json_data['data']['TotalTime']),
                    "IsReady": bool(json_data['data']['IsReady']),
                    "PirateUsedPCU": int(json_data['data']['PirateUsedPCU']),
                    "SimulationCpuLoad": float(json_data['data']['SimulationCpuLoad']),
                    "ServerName": json_data['data']['ServerName'].encode('utf-8'),
                    "WorldName": json_data['data']['WorldName'],
                    "SimSpeed": float(json_data['data']['SimSpeed']),
                    "Players": int(json_data['data']['Players']),
                    "Game": json_data['data']['Game'],
                    "Version": json_data['data']['Version'],
                    "UsedPCU": int(json_data['data']['UsedPCU']),
                    "ServerId": int(json_data['data']['ServerId'])
                }
            }
        ]
        return json_body

    def __write_entries_to_InfluxDB(self, client, influx_json):
        """Write the list of entries into the database"""
        print("Writing entries to InfluxDB")
        client.write_points(influx_json)

    def run(self):
        self.__setup_parser()
        self.__parse_arguments()

        api = pyvrageremoteAPI(self.url, self.key)
        result = api.get_resource_server()
        client = self.__connect_to_InfluxDB()
        influx_json = (self.__convert_data_to_influx_json(result))
        print(influx_json)
        self.__write_entries_to_InfluxDB(client, influx_json)
        client.close()
        exit()

    def __init__(self):
        """Default settings"""
        self.url = ""
        self.key = ""
        self.db_host = ""
        self.db_port = 8086
        self.db_name = "spaceengineers"


if __name__ == '__main__':
    spaceengineersmetrics = SpaceEngineersMetrics()
    spaceengineersmetrics.run()
