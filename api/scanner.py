import app
import io
import json
import pyclamd
import requests

from cloudevents.http import CloudEvent, to_json


def __signal_virus_detected(signature, url):
    attributes = {"type": "dams.virus_detected", "source": "dams"}
    data = {"signature": signature, "url": url}
    event = CloudEvent(attributes, data)
    message = json.loads(to_json(event))
    app.rabbit.send(message, routing_key="dams.mediafile_changed")


def scan_file(url):
    scan = pyclamd.ClamdAgnostic()
    with io.BytesIO(requests.get(url).content) as file:
        scan_result = scan.scan_stream(file)
    if scan_result:
        __signal_virus_detected(scan_result, url)
