#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from .model import *

import logging as _logging
import requests as _requests

_log = _logging.getLogger("blinky.jenkins")

_status_mapping = {
    "SUCCESS": PASSED,
    "FAILURE": FAILED,
    "UNSTABLE": FAILED,
}

class JenkinsAgent(HttpAgent):
    def __init__(self, model, name, url):
        super().__init__(model, name)

        self.html_url = url
        self.data_url = "{}/api/json".format(self.html_url)

class JenkinsJob(HttpJob):
    def __init__(self, model, group, component, environment, agent, name,
                 slug):
        super().__init__(model, group, component, environment, agent, name)

        self.slug = slug

        self.html_url = "{}/job/{}".format(self.agent.html_url, self.slug)
        self.data_url = "{}/api/json?{}".format(self.html_url, _rest_api_qs)
        self.fetch_url = "{}/lastBuild/api/json?{}".format(self.html_url, _rest_api_qs)

    def convert_result(self, data):
        number = data["number"]

        status = data["result"]
        status = _status_mapping.get(status, status)

        html_url = "{}/{}".format(self.html_url, number)
        data_url = "{}/api/json?{}".format(html_url, _rest_api_qs)
        tests_url = None

        for action in data["actions"]:
            if action.get("_class") == "hudson.tasks.junit.TestResultAction":
                tests_url = "{}/testReport".format(html_url)
                break

        result = JobResult()
        result.number = number
        result.status = status
        result.start_time = data["timestamp"] / 1000.0
        result.duration = data["duration"] / 1000.0
        result.html_url = html_url
        result.data_url = data_url
        result.tests_url = tests_url

        return result

# Fetch only as much data as we need
_rest_api_qs = "tree=number,result,actions,timestamp,duration"
