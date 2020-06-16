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
    base_name = base_name.split('.gpg')[0]

    return base_name


def _get_decryption(gpg: gnupg.GPG, configuration_kwargs: Dict) -> gnupg.GPG:
    ssm_name = '{environment}.{name}-{company_name}'.format(
        environment=settings.ENVIRONMENT,
        name=configuration_kwargs.get('secret_name'),
        company_name=configuration_kwargs.get('company_name')
    )
    secret_key = []
    for key in ['public','private']:
        logger.info(f'Handling {key} for decryption')

        ssm_name_extended = f'{ssm_name}-{key}'
        value = parameter_store.get_keys(
            profile_name='ssm', name=ssm_name_extended
        )

        secret_key.append(value)

    secret_keys = ''.join(secret_key)
    gpg.import_keys(secret_keys)
    keys = gpg.list_keys(True)

    gpg.trust_keys(
        keys.fingerprints,
        'TRUST_ULTIMATE'
    )

    return gpg

def decrypt_file(gpg: gnupg.GPG,
                 targer_folder: str):
    configuration_kwargs = utils.get_configuratation(
        path=os.path.join(
            targer_folder,
            'configuration'
        )
    )
    gpg = _get_decryption(
        gpg=gpg,
        configuration_kwargs=configuration_kwargs
    )

    encrypted_filepaths = utils.get_files(
        path=os.path.join(
            targer_folder,
            'encrypted_files'
        )
    )

    decrypted_path = os.path.join(
        targer_folder,
        'decrypted_files'
    )
    password = configuration_kwargs.get('array')['passphrase'] \
        if settings.ENVIRONMENT == 'prod' else 'wow'

    for encryped_file in encrypted_filepaths:
        base_name = __set_file_name(path=encryped_file)

        logger.info(f'Decrypting file {base_name}')

        output_file = os.path.join(decrypted_path, base_name)

        with open(encryped_file, 'rb') as connection:
            status = gpg.decrypt_file(
                file=connection,
                passphrase=password,
                output=output_file
            )
            logger.info(f'Decrypting done')

        if not status.ok:
            logger.info(f'{status.stderr}')
        else:
            logger.info(f'Status [{status.status}]')
