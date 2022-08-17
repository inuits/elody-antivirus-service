import app
import scanner


@app.rabbit.queue("dams.file_uploaded")
def start_file_transcode(routing_key, body, message_id):
    data = body["data"]
    if "mediafile" not in data or "mimetype" not in data or "url" not in data:
        return
    try:
        scanner.scan_file(data["url"])
    except Exception as ex:
        app.logger.error(f'Failed to scan {data["mediafile"]["filename"]}: {ex}')
