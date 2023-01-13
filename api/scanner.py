import app
import io
import os
import pyclamd
import requests
import subprocess

from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent


class Scanner:
    def __init__(self):
        self.collection_api_url = os.getenv("COLLECTION_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def __signal_file_scanned(self, mediafile, clamav_version, scan_result):
        attributes = {"type": "dams.file_scanned", "source": "dams"}
        data = {
            "mediafile_id": mediafile.get("_key", mediafile["_id"]),
            "clamav_version": clamav_version,
            "infected": scan_result is not None,
        }
        if scan_result:
            data["infection_info"] = scan_result
        event = to_dict(CloudEvent(attributes, data))
        app.rabbit.send(event, routing_key="dams.file_scanned")

    def scan_file(self, url, mediafile):
        scan = pyclamd.ClamdAgnostic()
        with io.BytesIO(requests.get(url).content) as file:
            scan_result = scan.scan_stream(file)
        if scan_result:
            app.logger.error(f'VIRUS DETECTED IN {mediafile["filename"]} {scan_result}')
        self.__signal_file_scanned(mediafile, scan.version(), scan_result)

    def update(self):
        subprocess.run(["/usr/bin/freshclam"])
