import logging
import os
import secrets

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from elody.observability import init_observability
from flask import Flask
from healthcheck import HealthCheck
from rabbit import get_rabbit, init_rabbit
from scanner import Scanner

if os.getenv("GLITCH_TIP_ENABLED", False) in ["True", "true", True]:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(
        dsn=os.getenv("GLITCH_TIP_DSN"),
        integrations=[FlaskIntegration()],
        environment=os.getenv("NOMAD_NAMESPACE"),
    )

app = Flask(__name__)
init_observability(app)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))

logging.basicConfig(
    format="%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

init_rabbit(app)
health = HealthCheck()


def rabbit_available():
    connection = get_rabbit().get_connection()
    if connection.is_open:
        return True, "Successfully reached RabbitMQ"
    return False, "Failed to reach RabbitMQ"


def schedule_db_update():

    def update_db():

        Scanner().update()

    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(update_db, CronTrigger().from_crontab("0 0 * * *"))


if os.getenv("HEALTH_CHECK_EXTERNAL_SERVICES", True) in ["True", "true", True]:
    health.add_check(rabbit_available)

app.add_url_rule("/health", "healthcheck", view_func=lambda: health.run())
schedule_db_update()

import queues  # noqa: F401

if __name__ == "__main__":
    app.run()
