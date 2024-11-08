#!/usr/bin/env python3
"""
This module contains functionality for filtering PII in logs,
setting up a logger, and securely connecting to a database.
"""

import re
import logging
from typing import List
import os
import mysql.connector


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """
    Obfuscate fields in a log message.
    """
    pattern = f"({'|'.join(fields)})=([^ {separator}]*)"
    return re.sub(pattern, lambda x: f"{x.group(1)}={redaction}", message)


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Filter values in log records using filter_datum.
        """
        original_message = super().format(record)
        return filter_datum(self.fields, self.REDACTION,
                            original_message, self.SEPARATOR)


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def get_logger() -> logging.Logger:
    """
    Create a logger named 'user_data' with a specific formatter.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(fields=PII_FIELDS))
    logger.addHandler(stream_handler)
    return logger


def get_db():
    """
    Connect to the MySQL database using environment variables for credentials.
    """
    user = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD', '')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')

    return mysql.connector.connect(
        user=user,
        password=password,
        host=host,
        database=db_name
    )


def main():
    """
    Main function to fetch and display user data with obfuscation.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, email, phone, ssn, password, ip,\
                   last_login, user_agent FROM users;")
    logger = get_logger()

    for row in cursor:
        message = f"name={row[0]}; email={row[1]}; phone={row[2]};\
        ssn={row[3]}; password={row[4]}; ip={row[5]};\
        last_login={row[6]}; user_agent={row[7]};"
        logger.info(message)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
