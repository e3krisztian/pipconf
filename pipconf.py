#!/usr/bin/env python
import os.path
import sys
import platform
import subprocess
import shutil
import glob


ERROR_MISSING_COMMAND = 1
ERROR_UNKNOWN_COMMAND = 2
ERROR_MISSING_PARAM = 3


is_windows = platform.system() == u'Windows'


def platform_choice(posix, windows):
    return windows if is_windows else posix


def config_file(posix, windows):
    return os.path.expanduser(platform_choice(posix, windows))


def pip_config():
    return config_file(u'~/.pip/pip.conf', windows=u'~/pip/pip.ini')


PIP_CONF_TEMPLATE = u'''\
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

# Enable the processing of dependency links (in setup.py).
process-dependency-links = false
'''


def create_cmd(cmdline):
    pip_config_file = pip_config()
    pip_config_dir = os.path.dirname(pip_config_file)
    try:
        os.makedirs(pip_config_dir)
    except OSError:
        pass
    with open(pip_config_file, u'w') as pip_conf:
        pip_conf.write(PIP_CONF_TEMPLATE)


def edit_cmd(cmdline):
    u'''Edit user's pip config file'''
    default_editor = platform_choice(u'/usr/bin/vi', windows=u'notepad.exe')
    editor = os.environ.get(u'EDITOR') or default_editor
    subprocess.call([editor, pip_config()])


def file_version(filename, version):
    return u'{}.{}'.format(filename, version)


def copy(cmd, source, destination):
    print(u'(command "{}") {} -> {}'.format(cmd, source, destination))
    shutil.copy2(source, destination)


def get_version(cmdline):
    try:
        _cmd, version = cmdline
        return version
    except:
        print_usage()
        if len(cmdline) > 2:
            msg = u'Too many parameters'
        else:
            msg = u'Missing version'
        print(u'ERROR: {}: "{}"'.format(msg, u''.join(cmdline)))
        sys.exit(ERROR_MISSING_PARAM)


def save_cmd(cmdline):
    u'''pip.conf -> pip.conf[version]'''
    version = get_version(cmdline)
    pip_conf = pip_config()
    copy(u'save', pip_conf, file_version(pip_conf, version))


def use_cmd(cmdline):
    u'''pip.conf[version] -> pip.conf'''
    version = get_version(cmdline)
    pip_conf = pip_config()
    copy(u'use', file_version(pip_conf, version), pip_conf)


def list_cmd(cmdline):
    u'''list all known config versions'''
    pip_conf = pip_config()
    configs = glob.glob(u'{}.*'.format(pip_conf))
    versions = [config[len(pip_conf) + 1:] for config in configs]
    print(u'Saved versions:')
    print(u'  ' + u'\n  '.join(sorted(versions)))


def print_cmd(cmdline):
    u'''print config to stdout'''
    with open(pip_config()) as config:
        sys.stdout.write(config.read())


def delete_cmd(cmdline):
    u'''delete named version'''
    os.remove(file_version(pip_config(), get_version(cmdline)))


COMMANDS = [
    # cmd, cli_name, param_help, help
    (create_cmd, (u'create', u'init'), u'',
        u'Create a pip config file with defaults'),
    (edit_cmd, (u'edit', u'ed', u'e'), u'',
        u'Edit the config file with the default text editor'),
    (save_cmd, (u'save', u's'), u'VERSION',
        u'Make a copy of the config with VERSION suffix'),
    (use_cmd, (u'use', u'get', u'restore'), u'VERSION',
        u'Copy the saved config with suffix VERSION over the config file'),
    (list_cmd, (u'list', u'ls'), u'',
        u'List known versions'),
    (print_cmd, (u'print', u'view', u'cat'), u'',
        u'Print current config to stdout'),
    (delete_cmd, (u'delete', u'del', u'remove', u'rm'), u'VERSION',
        u'Delete VERSION'),
]


def print_usage():
    print(u'Work on pip config file')
    print(u'')
    print(u'Usage:')
    print(u'')
    for cmd, cmd_names, param_help, help in COMMANDS:
        print(u'pipconf {} {}'.format(cmd_names[0], param_help))
        print(u'    {}'.format(help))
        aliases = u', '.join(cmd_names[1:])
        if aliases:
            print(u'    * aliases for <{}>: {}'.format(cmd_names[0], aliases))
        print(u'')


def unknown_cmd(cmdline):
    print_usage()
    print(u'ERROR: unknown command "{}"'.format(u' '.join(cmdline)))
    sys.exit(ERROR_UNKNOWN_COMMAND)


def get_command(cmdline):
    name = cmdline[0]
    for cmd, cmd_names, param_help, help in COMMANDS:
        if name in cmd_names:
            return cmd
    return unknown_cmd


def main():
    cmdline = sys.argv[1:]
    if not cmdline:
        print_usage()
        sys.exit(ERROR_MISSING_COMMAND)
    command = get_command(cmdline)
    command(cmdline)


if __name__ == u'__main__':
    main()


# unit tests
import unittest


class Test_get_command(unittest.TestCase):

    def test_unknown_command(self):
        self.assertEqual(unknown_cmd, get_command([object()]))

    def test_main_name_create(self):
        self.assertEqual(create_cmd, get_command([u'create']))

    def test_alias_for_edit(self):
        self.assertEqual(edit_cmd, get_command([u'ed']))


class Test_get_version(unittest.TestCase):

    def test_version(self):
        version = object()
        self.assertEqual(version, get_version([u'cmd', version]))

    def check_raises_systemexit(self, params):
        with self.assertRaises(SystemExit):
            get_version(params)

    def test_missing_version_raises_systemexit(self):
        self.check_raises_systemexit([u'cmd'])

    def test_too_many_param_raises_systemexit(self):
        self.check_raises_systemexit([u'cmd', u'version', u'extra'])


class Test_print_usage(unittest.TestCase):

    def test_runs_without_exception(self):
        print_usage()
