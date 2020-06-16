import os
import logging

from typing import (
    Any,
    Dict,
    List,
    Tuple
)

import boto3
import botocore.config
import gnupg
import yaml

import common.aws as aws
import common.utils as utils

import settings

logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


def _extract_keys(secret_key: str) -> Dict[str, str]:
    gnupg_files = [
        os.path.join(secret_key, file)
        for file in os.listdir(secret_key)
        if settings.ENVIRONMENT in file
    ]

    encrypted_keys = {}
    for gnupg_file in gnupg_files:
        with open(gnupg_file, 'r') as connection:
            import_result = connection.read()
            if 'secret' in gnupg_file:
                encrypted_keys['private'] = import_result
            else:
                encrypted_keys['public'] = import_result

    return encrypted_keys


def _upload_secrets(secret_blob: str, name: str, type: str) -> str:
    tags: Dict[List[str]] = [
        {
            'Key': 'Name',
            'Value': 'medhelp-fuse'
        },
        {
            'Key': 'InfrastructureType',
            'Value': 'Application/Service'
        },
    ]
    name = f'{name}-{type}'

    client = aws.get_client(service_name='ssm')
    secret_kwargs = {
        'Name': name,
        'Type': 'String',
        'Overwrite': True,
        'Description': f'{type} key',
        'Value': secret_blob,
        'Tier': 'Advanced',
        'DataType': 'text'
    }

    response = client.put_parameter(**secret_kwargs)

    return name


def save_to_ssm(targer_folder: str,
                secret_key: str):
    configuration_kwargs = utils.get_configuratation(
        path=os.path.join(
            targer_folder,
            'configuration'
        )
    )

    encryption_keys = _extract_keys(
        secret_key=secret_key
    )

    ssm_name = '{environment}.{name}-{company_name}'.format(
        environment=settings.ENVIRONMENT,
        name= configuration_kwargs.get('secret_name'),
        company_name=configuration_kwargs.get('company_name')
    )

    for key, value in encryption_keys.items():

        logger.info(f'Upload of {key} key')

        response = _upload_secrets(
            secret_blob=str(value),
            name=ssm_name,
            type=key
        )

        logger.info(f'Done with {response}')

