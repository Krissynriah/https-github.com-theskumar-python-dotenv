# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import dirname, join

import sh
import dotenv
import warnings

here = dirname(__file__)
dotenv_path = join(here, '.env')


def test_get_key():
    sh.touch(dotenv_path)
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
    stored_value = dotenv.get_key(dotenv_path, 'HELLO')
    assert stored_value == 'WORLD'
    sh.rm(dotenv_path)
    assert dotenv.get_key(dotenv_path, 'HELLO') is None
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
    assert success is None


def test_get_quoted_key():
    sh.touch(dotenv_path)
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', '"WORLD')
    stored_value = dotenv.get_key(dotenv_path, 'HELLO')
    assert stored_value == 'WORLD'
    sh.rm(dotenv_path)
    assert dotenv.get_key(dotenv_path, 'HELLO') is None


def test_commented_line():
    sh.touch(dotenv_path)
    my_line = """#this is a comment
    HELLO = WORLD
    #this is another comment
    """
    with open(dotenv_path, 'w') as f:
        f.write(my_line)

    stored_value = dotenv.get_key(dotenv_path, 'HELLO')
    assert stored_value == 'WORLD'
    sh.rm(dotenv_path)
    assert dotenv.get_key(dotenv_path, 'HELLO') is None


def test_boolean_values():
    sh.touch(dotenv_path)
    my_line = """HELLO = True
    WORLD = False
    """

    with open(dotenv_path, 'w') as f:
        f.write(my_line)

    stored_value = dotenv.get_key(dotenv_path, 'HELLO')
    assert stored_value
    stored_value = dotenv.get_key(dotenv_path, 'WORLD')
    assert not stored_value
    sh.rm(dotenv_path)
    assert dotenv.get_key(dotenv_path, 'HELLO') is None
    assert dotenv.get_key(dotenv_path, 'WORLD') is None


def test_unset():
    sh.touch(dotenv_path)
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
    stored_value = dotenv.get_key(dotenv_path, 'HELLO')
    assert stored_value == 'WORLD'
    success, key_to_unset = dotenv.unset_key(dotenv_path, 'HELLO')
    assert dotenv.get_key(dotenv_path, 'HELLO') is None
    sh.rm(dotenv_path)
    success, key_to_unset = dotenv.unset_key(dotenv_path, 'HELLO')
    assert success is None


def test_unset_warnings():
    sh.touch(dotenv_path)
    success, key_to_set, value_to_set = dotenv.set_key(dotenv_path, 'HELLO', 'WORLD')
    with warnings.catch_warnings(record=True) as w:
            dotenv.unset_key(dotenv_path, 'DOESNOTEXIST')

            assert len(w) == 1
            assert w[0].category == UserWarning
            error_message = "key DOESNOTEXIST not removed from %s - key doesn't exist." % (dotenv_path)
            assert str(w[0].message) == error_message

    sh.rm(dotenv_path)


def test_console_script(cli):
    with cli.isolated_filesystem():
        sh.touch(dotenv_path)
        sh.dotenv('-f', dotenv_path, 'set', 'HELLO', 'WORLD')
        output = sh.dotenv('-f', dotenv_path, 'get', 'HELLO', )
        assert output == 'HELLO="WORLD"\n'
        sh.rm(dotenv_path)

    # should fail for not existing file
    result = cli.invoke(dotenv.set, ['my_key', 'my_value'])
    assert result.exit_code != 0

    # should fail for not existing file
    result = cli.invoke(dotenv.get, ['my_key'])
    assert result.exit_code != 0

    # should fail for not existing file
    result = cli.invoke(dotenv.list, [])
    assert result.exit_code != 0


def test_default_path(cli):
    with cli.isolated_filesystem():
        sh.touch(dotenv_path)
        sh.cd(here)
        sh.dotenv('set', 'HELLO', 'WORLD')
        output = sh.dotenv('get', 'HELLO')
        assert output == 'HELLO="WORLD"\n'
        sh.rm(dotenv_path)
