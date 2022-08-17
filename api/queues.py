import app

from scanner import Scanner


@app.rabbit.queue("dams.file_uploaded")
def scan_file(routing_key, body, message_id):
    data = body["data"]
    if "mediafile" not in data or "mimetype" not in data or "url" not in data:
        return
    try:
        Scanner().scan_file(data["url"], data["mediafile"])
    except Exception as ex:
        app.logger.error(f'Failed to scan {data["mediafile"]["filename"]}: {ex}')
