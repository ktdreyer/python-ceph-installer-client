import json

import httpretty

from ceph_installer_client import CephInstallerClient

INSTALL_HOST = 'installer.example.com'

EXPECTED_RESPONSE = {
    'endpoint': '/api/mon/install/',
    'succeeded': False,
    'stdout': None,
    'started': None,
    'exit_code': None,
    'ended': None,
    'command': None,
    'stderr': None,
    'identifier': '47f60562-a96b-4ac6-be07-71726b595793'
}


class TestMon(object):

    def setup_method(self, method):
        httpretty.enable()
        httpretty.register_uri(
            httpretty.POST, 'http://%s:8181/api/mon/install/' % INSTALL_HOST,
            body=self.post_request_callback, content_type='application/json')

    def post_request_callback(self, request, uri, headers):
        client_payload = json.loads(request.body)
        # We're asserting outside of a test class, which is a little weird.
        assert client_payload == self.expected_payload
        return (200, headers, json.dumps(EXPECTED_RESPONSE))


class TestMonBasic(TestMon):

    expected_payload = {'hosts': ['mymon1']}

    def test_basic(self):
        c = CephInstallerClient(INSTALL_HOST)
        assert c.mon.install(['mymon1']) == EXPECTED_RESPONSE


class TestMonRedHatStorage(TestMon):

    expected_payload = {'hosts': ['mymon1'],
                        'redhat_storage': True}

    def test_redhat_storage(self):
        c = CephInstallerClient(INSTALL_HOST)
        payload = {'redhat_storage': True}
        assert c.mon.install(['mymon1'], payload) == EXPECTED_RESPONSE


class TestMonRedHatStorageAndCalamari(TestMon):

    expected_payload = {'hosts': ['mymon1'],
                        'calamari': True,
                        'redhat_storage': True}

    def test_redhat_storage_and_calamari(self):
        c = CephInstallerClient(INSTALL_HOST)
        payload = {'redhat_storage': True, 'calamari': True}
        assert c.mon.install(['mymon1'], payload) == EXPECTED_RESPONSE
