"""Test demo.py functionality.

This is also some end-to-end testing.
"""
import os
import subprocess
import time
import unittest

import pytest


class TestDemoPy(unittest.TestCase):
    """End-to-End tests for demo.py"""

    # pylint does not understand pytest fixtures, so we have to disable the warning
    # pylint: disable=no-member

    root_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    def setUp(self):
        """Wait some time before polling the same sensor with different backends."""
        time.sleep(0.6)

    @pytest.mark.usefixtures("mac")
    def test_bluepy_poll(self):
        """Test polling via bluepy."""
        self.assertIsNotNone(self.mac)
        cmd = f"./demo.py --backend bluepy poll {self.mac}"
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)

    @pytest.mark.usefixtures("mac")
    def test_gatttool_poll(self):
        """Test polling via gatttool."""
        self.assertIsNotNone(self.mac)
        cmd = f"./demo.py --backend gatttool poll {self.mac}"
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)

    @pytest.mark.usefixtures("mac")
    def test_pygatt_poll(self):
        """Test polling via pygatt."""
        self.assertIsNotNone(self.mac)
        cmd = f"./demo.py --backend pygatt poll {self.mac}"
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)

    def test_bluepy_scan(self):
        """Test scanning via bluepy."""
        cmd = "./demo.py --backend bluepy scan"
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)

    def test_list_backends(self):
        """Test the list backends subcommand."""
        cmd = "./demo.py backends"
        stdout = subprocess.check_output(cmd, shell=True, cwd=self.root_dir)
        stdout = stdout.decode("utf-8")
        self.assertIn("BluepyBackend", stdout)
        self.assertIn("GatttoolBackend", stdout)

    @pytest.mark.usefixtures("mac")
    def test_history(self):
        """Test the list backends subcommand."""
        cmd = f"./demo.py history {self.mac}"
        stdout = subprocess.check_output(cmd, shell=True, cwd=self.root_dir)
        stdout = stdout.decode("utf-8")
        self.assertIn("Getting history", stdout)
