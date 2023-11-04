# Pybricks BLE server (broadcaster) and client (observer)
import datetime
import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] [%(name)-20s] [%(levelname)-8s] %(message)s",
)

# ISO8601 dateformat for logging including milliseconds
logging.Formatter.formatTime = (
    lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(
        record.created, datetime.timezone.utc
    )
    .astimezone()
    .isoformat(sep="T", timespec="milliseconds")
)
