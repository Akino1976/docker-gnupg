import os
import logging
import configparser

from typing import (
    Any,
    Dict,
    List
)

import boto3
import botocore.config

import settings

logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)

logger = logging.getLogger(__name__)


def get_client(service_name: str) -> boto3.session.Session.client:
    session = boto3.session.Session()

    client = session.client(
        service_name=service_name,
        region_name=settings.REGION,
    )

    return client
