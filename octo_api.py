import requests
from functools import partial


class OctoApi(object):
    def __init__(self, url, api_key):
        self.base_url = url
        self.api_key = api_key

    def call_api(self, command):
        response = requests.get("{}/{}".format(self.base_url, command), headers={"X-Api-Key":self.api_key}, timeout=2)

        if response.status_code != 200:
            print("Something went wrong: {}".format(response.content))

        return response.json()

    def connection_status(self):
        return self.call_api("connection")

    def printer_status(self):
        return self.call_api("printer")

    def job_status(self):
        return self.call_api("job")
