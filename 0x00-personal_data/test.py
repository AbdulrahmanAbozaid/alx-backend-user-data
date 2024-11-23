#!/usr/bin/env python3
"""
Logging PII
"""
import re
import logging
import typing
import mysql.connector
import os


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


class RedactingFormatter(logging.Formatter):
    """Redacting Formatter class"""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        return filter_datum(self.fields, self.REDACTION, msg, self.SEPARATOR)


def filter_datum(
    fields: typing.Iterable, redaction: str, message: str, separator: str
) -> str:
    pattern = f"({'|'.join(fields)})=([^ {separator}]*)"
    return re.sub(pattern, lambda m: f"{m.group(1)}={redaction}", message)


def get_logger() -> logging.Logger:
    """Get Custom Logger"""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)

    stream_handle = logging.StreamHandler()
    stream_handle.setLevel(logging.INFO)
    stream_handle.setFormatter(RedactingFormatter(PII_FIELDS))

    logger.addHandler(stream_handle)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Get Database Object

    Returns: (MySQLConnection): db connection
    """
    return mysql.connector.connect(
        host=os.environ.get("PERSONAL_DATA_DB_HOST", default="localhost"),
        user=os.environ.get("PERSONAL_DATA_DB_USERNAME", default="root"),
        password=os.environ.get("PERSONAL_DATA_DB_PASSWORD", default=""),
        database=os.environ.get("PERSONAL_DATA_DB_NAME"),
    )
