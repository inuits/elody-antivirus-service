import app

from scanner import Scanner


@app.rabbit.queue("dams.file_uploaded")
def scan_uploaded_file(routing_key, body, message_id):
    data = body["data"]
    if "mediafile" not in data or "mimetype" not in data or "url" not in data:
        return
    try:
        Scanner().scan_file(data["url"], data["mediafile"], data["headers"])
    except Exception as ex:
        app.logger.error(f'Failed to scan {data["mediafile"]["identifier"]}: {ex}')


@app.rabbit.queue("dams.update_clamav")
def update_clamav_version(routing_key, body, message_id):
    Scanner().update()
