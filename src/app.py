import logging
import shutil
import os

from typing import List, Dict

import gnupg

import common.generate_keys as generate_keys
import common.decrypt_handler as decrypt_handler
import common.encrypt_handler as encrypt_handler
import common.secret_manager as secret_manager

import settings

logger = logging.getLogger(__name__)

GPG = shutil.which('gpg')
GPG_OPTION = {
    'gnupghome': '.',
    'options': ['--lock-never']
}

if GPG:
    GPG_OPTION['gpgbinary'] = GPG


def __set_gpg(**kwargs) -> gnupg.GPG:
    gpg = gnupg.GPG(
        **kwargs
    )
    gpg.encoding = 'utf-8'

    return gpg


def generate_gnupg_keys(company_name: str, target_folder: str) -> str:
    logger.info('Start generate keys')

    generate_keys.generate_keys(
        gpg=__set_gpg(**GPG_OPTION),
        company_name=company_name,
        targer_folder=target_folder
    )


def decrypt_gnupg_file(target_folder: str):
    logger.info('Start decrypt files')

    decrypt_handler.decrypt_file(
        gpg=__set_gpg(**GPG_OPTION),
        targer_folder=target_folder
    )


def encrypt_gnupg_file(target_folder: str):
    logger.info('Start encrypt files')
    encrypt_handler.encrypt_file(
        gpg=__set_gpg(**GPG_OPTION),
        targer_folder=target_folder
    )


def save_to_ssm(target_folder: str, secret_key: str):
    logger.info('Start encrypt files')
    secret_manager.save_to_ssm(
        targer_folder=target_folder,
        secret_key=secret_key
    )


def main():
    settings.parse_flags()

    if settings.arguments.operation == settings.OPERATION_GENERATE_KEY:
        generate_gnupg_keys(
            company_name=settings.arguments.company_name,
            target_folder=settings.arguments.target_folder
        )

    if settings.arguments.operation == settings.OPERATION_DECRYPT:
        decrypt_gnupg_file(
            target_folder=settings.arguments.target_folder
        )

    if settings.arguments.operation == settings.OPERATION_ENCRYPT:
        encrypt_gnupg_file(
            target_folder=settings.arguments.target_folder
        )

    if settings.arguments.operation == settings.OPERATION_SSM:
        save_to_ssm(
            target_folder=settings.arguments.target_folder,
            secret_key=settings.arguments.secret_key
        )


if __name__ == '__main__':
    main()
