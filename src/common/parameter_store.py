import os
import logging
import time

import boto3
import botocore.config

import common.aws as aws

import settings

logger = logging.getLogger(__name__)

def get_keys(profile_name: str=None, name: str=None) -> str:
    if name is None:
        raise Exception(f'No name, please set a name to ssm')

    client = aws.get_client(
        service_name='ssm'
    )

    logger.info(f'Getting key from parameter store')

    parameters = client.get_parameters(
        Names=[name],
        WithDecryption=True
    )

    return parameters.get('Parameters')[0].get('Value')
