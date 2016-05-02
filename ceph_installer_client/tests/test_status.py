import httpretty
import pytest

from ceph_installer_client import CephInstallerClient, CephInstallerClientError

INSTALL_HOST = 'installer.example.com'


class TestStatus(object):

    @httpretty.activate
    def test_status_ok(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://%s:8181/api/status/' % INSTALL_HOST,
            body='{"message": "ok"}',
            content_type='application/json')
        c = CephInstallerClient(INSTALL_HOST)
        assert c.status() is True

    @httpretty.activate
    def test_status_failure(self):
        httpretty.register_uri(
            httpretty.GET,
            'http://%s:8181/api/status/' % INSTALL_HOST,
            status=500,
            body='{"message": "RabbitMQ is not running or not reachable"}',
            content_type='application/json')
        c = CephInstallerClient(INSTALL_HOST)
        with pytest.raises(CephInstallerClientError):
            c.status()
