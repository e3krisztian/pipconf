#!/usr/bin/env python
'''
Work on pip config file
'''

import os.path
import sys
import platform
import shutil
import pipes
import glob
from mando import command, main


ERROR_MISSING_COMMAND = 1
ERROR_UNKNOWN_COMMAND = 2
ERROR_MISSING_PARAM = 3


IS_WINDOWS = platform.system() == 'Windows'


def platform_choice(posix, windows):
    return windows if IS_WINDOWS else posix


def config_file(posix, windows):
    return os.path.expanduser(platform_choice(posix, windows))


def pip_config():
    return config_file('~/.pip/pip.conf', windows='~/pip/pip.ini')


PIP_CONF_TEMPLATE = '''\
[global]
# Base URL of Python Package Index

index-url = https://pypi.python.org/simple/


# Extra URLs of package indexes to use in addition to --index-url.

extra-index-url =


# Ignore package index (only looking at --find-links URLs instead).

no-index = false


# If a url or path to an html file, then parse for links to archives.
# If a local path or file:// url that's a directory, then look for archives
# in the directory listing.

find-links =
'''


@command
def create():
    '''
    Create a pip config file with defaults
    '''
    pip_config_file = pip_config()
    pip_config_dir = os.path.dirname(pip_config_file)
    try:
        os.makedirs(pip_config_dir)
    except OSError:
        pass
    with open(pip_config_file, 'w') as pip_conf:
        pip_conf.write(PIP_CONF_TEMPLATE)


@command('ed')
def edit():
    '''
    Edit user's pip config file with the default text editor
    '''
    default_editor = platform_choice('/usr/bin/vi', windows='notepad.exe')
    editor = os.environ.get('EDITOR') or default_editor
    os.system(
        '{} {}'.format(
            editor,
            pipes.quote(pip_config())))


def file_version(filename, version):
    return '{}.{}'.format(filename, version)


def copy(cmd, source, destination):
    print('(command "{}") {} -> {}'.format(cmd, source, destination))
    shutil.copy2(source, destination)


@command('cp')
def copy_cmd(version):
    '''
    Make a copy of the config with VERSION suffix.

    pip.conf -> pip.conf[version]
    '''
    pip_conf = pip_config()
    copy('copy', pip_conf, file_version(pip_conf, version))


@command
def use(version):
    '''
    Copy the saved config with suffix VERSION over the config file

    pip.conf[version] -> pip.conf
    :param version:
    '''
    pip_conf = pip_config()
    copy('use', file_version(pip_conf, version), pip_conf)


@command('ls')
def list_cmd():
    '''List known config <VERSION>s'''
    pip_conf = pip_config()
    configs = glob.glob('{}.*'.format(pip_conf))
    versions = [config[len(pip_conf) + 1:] for config in configs]
    print('Saved versions:')
    print('  ' + '\n  '.join(sorted(versions)))


@command('cat')
def print_cmd(version=None):
    '''
    Print config to stdout

    :param version: version to dump, defaults to current config
    '''
    if version:
        filename = file_version(pip_config(), version)
    else:
        filename = pip_config()
    with open(filename) as config:
        sys.stdout.write(config.read())


@command('rm')
def delete(version):
    '''ReMove saved config <VERSION>

    :param version: remove pip.conf saved as <VERSION>
    '''
    os.remove(file_version(pip_config(), version))


if __name__ == '__main__':
    main()
