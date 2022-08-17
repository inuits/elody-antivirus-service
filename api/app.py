import json
import logging
import os

from flask import Flask
from rabbitmq_pika_flask import RabbitMQ
from healthcheck import HealthCheck

app = Flask(__name__)
app.config.update(
    {
        "MQ_EXCHANGE": os.getenv("RABMQ_SEND_EXCHANGE_NAME"),
        "MQ_URL": os.getenv("RABMQ_RABBITMQ_URL"),
        "SECRET_KEY": "SomethingNotEntirelySecret",
        "TESTING": True,
        "DEBUG": True,
    }
)

logging.basicConfig(
    format="%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

rabbit = RabbitMQ()
rabbit.init_app(app, "basic", json.loads, json.dumps)

health = HealthCheck()


def rabbit_available():
    return True, rabbit.get_connection().is_open


if os.getenv("HEALTH_CHECK_EXTERNAL_SERVICES", True) in ["True", "true", True]:
    health.add_check(rabbit_available)

app.add_url_rule("/health", "healthcheck", view_func=lambda: health.run())

import queues

if __name__ == "__main__":
    app.run(debug=True)
