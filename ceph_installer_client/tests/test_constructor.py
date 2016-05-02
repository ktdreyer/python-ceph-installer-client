import pytest

from ceph_installer_client import CephInstallerClient


class TestConstructor(object):

    def test_constructor_missing_host(self):
        with pytest.raises(TypeError):
            CephInstallerClient()

    def test_constructor(self):
        c = CephInstallerClient('installer.example.com')
        assert type(c) is CephInstallerClient
