import app
import io
import os
import pyclamd
import requests


class Scanner:
    def __init__(self):
        self.collection_api_url = os.getenv("COLLECTION_API_URL")
        self.headers = {"Authorization": f'Bearer {os.getenv("STATIC_JWT")}'}

    def __get_raw_id(self, item):
        return item["_key"] if "_key" in item else item["_id"]

    def __remove_infected_mediafile(self, mediafile):
        req = requests.delete(
            f"{self.collection_api_url}/mediafiles/{self.__get_raw_id(mediafile)}",
            headers=self.headers,
        )
        if req.status_code != 204:
            app.logger.error(
                f'FAILED TO DELETE {mediafile["filename"]}: {req.text.strip()}'
            )

    def scan_file(self, url, mediafile):
        scan = pyclamd.ClamdAgnostic()
        with io.BytesIO(requests.get(url).content) as file:
            scan_result = scan.scan_stream(file)
        if scan_result:
            app.logger.error(f'VIRUS DETECTED IN {mediafile["filename"]} {scan_result}')
            self.__remove_infected_mediafile(mediafile)
