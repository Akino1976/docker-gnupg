import os

from glob import glob
from typing import (
    Any,
    Dict,
    List,
    Tuple
)

import yaml


def get_all_files(path: str, exclude=Tuple[str]) -> List[str]:
    if not os.path.exists:
        raise ValueError(f'Not a valid path {path}')

    all_files = [
        base_path for filepath in os.walk(path)
        for base_path in glob(os.path.join(filepath[0], '*'))
        if os.path.isfile(base_path) and not base_path.endswith(exclude)
    ]

    extra_files = [
        _file for _file in os.listdir(path)
        if _file.startswith('S.gpg')
    ]

    return [*all_files, *extra_files]


def get_files(path: str) -> List[str]:
    if not os.path.exists:
        raise ValueError(f'Not a valid path {path}')

    all_files = [
        os.path.join(path, _file) for _file in os.listdir(path)
        if os.path.isfile(os.path.join(path, _file))
    ]

    return all_files


def get_all_directories(path: str) -> List[str]:
    if not os.path.exists:
        raise ValueError(f'Not a valid path {path}')

    all_dirs = [
        os.path.join(path, objects) for objects in os.listdir(path)
        if os.path.isdir(os.path.join(path, objects))
    ]

    return all_dirs


def get_configuratation(path: str) -> Dict[str, Any]:
    files = get_files(
        path=path
    )[0]

    with open(files, 'r') as connection:
        yaml_file = yaml.load(connection, Loader=yaml.FullLoader)

    return yaml_file.get('key_configuration')
