# -*- coding: utf-8 -*-
# Copyright (c) 2011, Sebastian Wiesner <lunaryorn@gmail.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function, division, absolute_import

import unittest
import os.path

from sphinxcontrib.programoutput import Command, program_output

class TestCommand(unittest.TestCase):

    def test_new_with_string_command(self):
        cmd = 'echo "spam with eggs"'
        assert Command(cmd).command == cmd
        assert Command(cmd, shell=True).command == cmd


    def test_new_with_list(self):
        cmd = Command(['echo', 'spam'])
        assert cmd.command == ('echo', 'spam')


    def test_new_with_list_hashable(self):
        """
        Test that Command objects are hashable even when passed a non-hashable
        list.  Important for caching!
        """
        hash(Command(['echo', 'spam']))


    def test_from_programoutput_node(self):
        node = program_output()
        node['command'] = 'echo spam'
        node['use_shell'] = False
        node['hide_standard_error'] = False
        node['working_directory'] = '/spam/with/eggs'
        command = Command.from_program_output_node(node)
        assert command.command == 'echo spam'
        assert command.working_directory == '/spam/with/eggs'
        assert not command.shell
        assert not command.hide_standard_error
        node['use_shell'] = True
        assert Command.from_program_output_node(node).shell
        assert not Command.from_program_output_node(node).hide_standard_error
        node['hide_standard_error'] = True
        assert Command.from_program_output_node(node).hide_standard_error


    def test_from_programoutput_node_extraargs(self):
        node = program_output()
        node['command'] = 'echo spam'
        node['use_shell'] = False
        node['hide_standard_error'] = False
        node['extraargs'] = 'with eggs'
        node['working_directory'] = '/'
        command = Command.from_program_output_node(node)
        assert command.command == 'echo spam with eggs'


    def test_execute(self):
        process = Command('echo spam').execute()
        assert process.stderr is None
        assert not process.stdout.closed
        assert process.wait() == 0


    def test_execute_with_shell(self):
        process = Command('echo spam', shell=True).execute()
        assert process.stderr is None
        assert not process.stdout.closed
        assert process.wait() == 0


    def test_execute_with_hidden_standard_error(self):
        process = Command('echo spam', hide_standard_error=True).execute()
        assert not process.stderr.closed
        assert process.wait() == 0


    def test_get_output(self):
        returncode, output = Command('echo spam').get_output()
        assert returncode == 0
        assert output == 'spam'


    def test_get_output_non_zero(self):
        returncode, output = Command(
            'python -c "import sys; print(\'spam\'); sys.exit(1)"').get_output()
        assert returncode == 1
        assert output == 'spam'


    def test_get_output_with_hidden_standard_error(self):
        returncode, output = Command(
            'python -c "import sys; sys.stderr.write(\'spam\')"',
            hide_standard_error=True).get_output()
        assert returncode == 0
        assert output == ''


    def test_get_output_with_working_directory(self):
        import tempfile, shutil
        tmpdir = tempfile.mkdtemp()
        cwd = os.path.realpath(str(tmpdir))
        returncode, output = Command(
            'python -c "import sys, os; sys.stdout.write(os.getcwd())"',
            working_directory=cwd).get_output()
        assert returncode == 0
        assert output == cwd
        shutil.rmtree(tmpdir)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
