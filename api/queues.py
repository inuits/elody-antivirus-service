import app

from scanner import Scanner
from os import getenv
from rabbit import get_rabbit

ROUTING_KEY_PREFIX = getenv("ROUTING_KEY_PREFIX", "dams")


@get_rabbit().queue(f"{ROUTING_KEY_PREFIX}.file_uploaded.#")
def scan_uploaded_file(routing_key, body, message_id):
    data = body["data"]
    if "mediafile" not in data or "mimetype" not in data or "url" not in data:
        return
    try:
        Scanner().scan_file(
            data["url"], data["mediafile"], data["headers"], data.get("ticket")
        )
    except Exception as ex:
        app.logger.error(f"Failed to scan {data['mediafile']['filename']}: {ex}")


@get_rabbit().queue(f"{ROUTING_KEY_PREFIX}.update_clamav")
def update_clamav_version(routing_key, body, message_id):
    Scanner().update()
