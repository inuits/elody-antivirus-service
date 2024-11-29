import app
import io
import os
import pyclamd
import requests
import subprocess

from cloudevents.conversion import to_dict
from cloudevents.http import CloudEvent


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Scanner(metaclass=Singleton):
    def __init__(self):
        self.collection_api_url = os.getenv("COLLECTION_API_URL")

    def __signal_file_scanned(
        self, mediafile, clamav_version, scan_result, ticket=None
    ):
        attributes = {"type": "dams.file_scanned", "source": "dams"}
        filename = mediafile.get("filename")
        if "/" in ticket.get("location", ""):
            filename = f"{ticket.get('location').split('/')[0]}/{filename}"
        data = {
            "mediafile_id": mediafile.get("_key", mediafile["_id"]),
            "clamav_version": clamav_version,
            "infected": scan_result is not None,
            "filename": filename,
        }
        if scan_result:
            data["infection_info"] = scan_result
        event = to_dict(CloudEvent(attributes, data))
        app.rabbit.send(event, routing_key="dams.file_scanned")

    def scan_file(self, url, mediafile, headers, ticket=None):
        scan = pyclamd.ClamdAgnostic()
        with io.BytesIO(requests.get(url, headers=headers).content) as file:
            scan_result = scan.scan_stream(file)
        if scan_result:
            app.logger.error(f'VIRUS DETECTED IN {mediafile["filename"]} {scan_result}')
        self.__signal_file_scanned(mediafile, scan.version(), scan_result, ticket)

    def update(self):
        subprocess.run(["/usr/bin/freshclam"])
