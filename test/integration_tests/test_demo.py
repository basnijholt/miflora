import subprocess
import os
import pytest
import unittest


class TestDemoPy(unittest.TestCase):
    """End-to-End tests for demo.py"""

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @pytest.mark.usefixtures("mac")
    def test_bluepy_poll(self):
        self.assertIsNotNone(self.mac)
        cmd = './demo.py --backend bluepy poll {}'.format(self.mac)
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)

    @pytest.mark.usefixtures("mac")
    def test_gatttool_poll(self):
        self.assertIsNotNone(self.mac)
        cmd = './demo.py --backend gatttool poll {}'.format(self.mac)
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)

    def test_bluepy_scan(self):
        cmd = './demo.py --backend bluepy scan'
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)
