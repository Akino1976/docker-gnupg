import datetime
import logging
import os

from argparse import ArgumentParser, ArgumentTypeError

PROJECT_NAME = os.path.dirname(os.path.abspath(__file__))
APP_PATH = os.path.dirname(os.path.realpath(PROJECT_NAME))
GNUPG_KEYS = os.path.realpath(
    os.path.join(
        APP_PATH,
        'GNUPG_KEYS'
    )
)
GNUPG_ASSETS = os.path.realpath(
    os.path.join(
        APP_PATH,
        'GNUPG_ASSETS'
    )
)

os.makedirs(GNUPG_KEYS, exist_ok=True)

APP_NAME = os.getenv('APP_NAME')
APP_COMPONENT = os.getenv('APP_COMPONENT')

REGION = 'eu-west-1'
VERSION = os.getenv('VERSION')
ENVIRONMENT = os.getenv('ENVIRONMENT')

OPERATION_GENERATE_KEY = 'generate-keys'
OPERATION_DECRYPT = 'decrypt-file'
OPERATION_ENCRYPT = 'encrypt-file'
OPERATION_SSM = 'save_ssm'

OPERATIONS = [
    OPERATION_GENERATE_KEY,
    OPERATION_DECRYPT,
    OPERATION_ENCRYPT,
    OPERATION_SSM,
]

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(logging.StreamHandler())

arguments = object()


def parse_flags():
    global arguments

    parser = ArgumentParser()

    parser.add_argument(
        'operation',
        action='store',
        type=str,
        choices=OPERATIONS,
    )

    parser.add_argument(
        '--target-folder',
        action='store',
        type=str,
        dest='target_folder',
    )

    parser.add_argument(
        '--company-name',
        action='store',
        type=str,
        dest='company_name',
    )

    parser.add_argument(
        '--secret-key',
        action='store',
        type=str,
        dest='secret_key',
    )

    arguments = parser.parse_args()
