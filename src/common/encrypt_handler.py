import os
import logging

from typing import List, Dict, Tuple

import yaml
import gnupg

import common.utils as utils
import common.parameter_store as parameter_store

import settings
logger = logging.getLogger(__name__)


def __set_file_name(path: str) -> str:
    base_name = os.path.basename(path)
    base_name = f'{base_name}.gpg'

    return base_name


def _get_decryption(configuration_kwargs: Dict) -> str:
    ssm_name = '{environment}.{name}-{company_name}-public'.format(
        environment=settings.ENVIRONMENT,
        name=configuration_kwargs.get('secret_name'),
        company_name=configuration_kwargs.get('company_name')
    )

    value = parameter_store.get_keys(
        profile_name='ssm', name=ssm_name
    )

    return value

def encrypt_file(gpg: gnupg.GPG,
                 targer_folder: str):
    configuration_kwargs = utils.get_configuratation(
        path=os.path.join(
            targer_folder,
            'configuration'
        )
    )
    value = _get_decryption(configuration_kwargs=configuration_kwargs)

    gpg.import_keys(value)
    keys = gpg.list_keys()

    gpg.trust_keys(
        keys.fingerprints,
        'TRUST_ULTIMATE'
    )

    decrypted_filepaths = utils.get_files(
        path=os.path.join(
            targer_folder,
            'decrypted_files'
        )
    )

    encrypted_path = os.path.join(
        targer_folder,
        'encrypted_files'
    )

    for decryped_file in decrypted_filepaths:
        base_name = __set_file_name(path=decryped_file)

        logger.info(f'encrypting file {base_name}')

        output_file = os.path.join(
            encrypted_path,
            base_name
        )

        with open(decryped_file, 'rb') as connection:
            status = gpg.encrypt_file(
                file=connection,
                recipients=keys.fingerprints,
                output=output_file,
            )

            logger.info(f'encrypting done')

        if not status.ok:
            logger.info(f'{status.stderr}')
        else:
            logger.info(f'Status [{status.status}]')
