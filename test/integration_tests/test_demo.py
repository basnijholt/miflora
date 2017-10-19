import subprocess
import os
import pytest
import unittest


class TestDemoPy(unittest.TestCase):
    """End-to-End tests for demo.py"""

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @pytest.mark.usefixtures("mac")
    def test_bluepy(self):
        self.assertIsNotNone(self.mac)
        cmd = './demo.py --backend bluepy {}'.format(self.mac)
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)

    @pytest.mark.usefixtures("mac")
    def test_gatttool(self):
        self.assertIsNotNone(self.mac)
        cmd = './demo.py --backend gatttool {}'.format(self.mac)
        subprocess.check_call(cmd, shell=True, cwd=self.root_dir)
