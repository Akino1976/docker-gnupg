import logging
import shutil
import os

from typing import List, Dict, Tuple

import gnupg

import common.secret_manager as secret_manager
import common.utils as utils

import settings
logger = logging.getLogger(__name__)


def _clean_directory(path: str):
    all_files = utils.get_all_files(
        path=path,
        exclude=('.py', '.txt', 'Dockerfile', '.asc', 'yaml', 'yml')
    )
    all_dirs = utils.get_all_directories(path=path)

    for file in all_files:
        if os.path.exists(file):
            logger.info(f'rm file {file}')
            os.remove(file)

    for dirs in all_dirs:
        if os.path.exists(dirs) and not 'common' in dirs:
            logger.info(f'rm directory {dirs}')
            shutil.rmtree(dirs, ignore_errors=True)


def __get_absolut_filepath(company_name) -> Tuple[str, str, str]:
    upper_company_name =  company_name.upper()
    company_path = os.path.join(
        settings.GNUPG_KEYS,
        upper_company_name
    )
    file_name_convention = f'{upper_company_name}_{settings.ENVIRONMENT}'

    public_file_name = os.path.join(
        company_path,
        f'{file_name_convention}_{settings.VERSION}_keys.asc'
    )
    secret_file_name = os.path.join(
        company_path,
        f'{file_name_convention}_{settings.VERSION}_secret_keys.asc'
    )

    return company_path, public_file_name, secret_file_name


def generate_keys(gpg: gnupg.GPG, company_name: str, targer_folder: str):
    company_path, public_file_name, secret_file_name = __get_absolut_filepath(
        company_name=company_name
    )

    configuration_kwargs = utils.get_configuratation(
        path=os.path.join(
            targer_folder,
            'configuration'
        )
    )
    os.makedirs(company_path, exist_ok=True)

    gpg_keys = gpg.gen_key_input(**configuration_kwargs.get('array'))
    key = gpg.gen_key(gpg_keys)

    ascii_armored_public_keys = gpg.export_keys(key.fingerprint)
    ascii_armored_private_keys = gpg.export_keys(
        key.fingerprint,
        secret=True,
        passphrase=configuration_kwargs.get('array')['passphrase'],
    )


    with open(public_file_name, 'w') as file:
        file.write(ascii_armored_public_keys)

        logger.info(f'Generate file to export to customer done')

    with open(secret_file_name, 'w') as file:
        file.write(ascii_armored_public_keys)
        file.write(ascii_armored_private_keys)

        logger.info(f'Generate file to use done')

    _clean_directory(path=settings.PROJECT_NAME)
