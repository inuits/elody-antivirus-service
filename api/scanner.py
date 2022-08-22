import app
import io
import json
import os
import pyclamd
import requests

from cloudevents.conversion import to_json
from cloudevents.http import CloudEvent


class Scanner:
    def __init__(self):
        self.collection_api_url = os.getenv("COLLECTION_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def __get_raw_id(self, item):
        return item["_key"] if "_key" in item else item["_id"]

    def __signal_virus_detected(self, mediafile, scan_result):
        attributes = {"type": "dams.virus_detected", "source": "dams"}
        data = {
            "filename": mediafile["filename"],
            "mediafile_id": self.__get_raw_id(mediafile),
            "scan_result": scan_result,
        }
        event = CloudEvent(attributes, data)
        message = json.loads(to_json(event))
        app.rabbit.send(message, routing_key="dams.virus_detected")

    def scan_file(self, url, mediafile):
        scan = pyclamd.ClamdAgnostic()
        with io.BytesIO(requests.get(url).content) as file:
            scan_result = scan.scan_stream(file)
        if scan_result:
            app.logger.error(f'VIRUS DETECTED IN {mediafile["filename"]} {scan_result}')
            self.__signal_virus_detected(mediafile, scan_result)
