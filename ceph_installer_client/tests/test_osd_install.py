import json

import httpretty

from ceph_installer_client import CephInstallerClient

INSTALL_HOST = 'installer.example.com'

EXPECTED_IDENTIFIER = '47f60562-a96b-4ac6-be07-71726b595793'

EXPECTED_RESPONSE = {
    'endpoint': '/api/osd/install/',
    'succeeded': False,
    'stdout': None,
    'started': None,
    'exit_code': None,
    'ended': None,
    'command': None,
    'stderr': None,
    'identifier': EXPECTED_IDENTIFIER
}


class TestOSD(object):

    def setup_method(self, method):
        httpretty.enable()
        httpretty.register_uri(
            httpretty.POST, 'http://%s:8181/api/osd/install/' % INSTALL_HOST,
            body=self.post_request_callback, content_type='application/json')

    def post_request_callback(self, request, uri, headers):
        client_payload = json.loads(request.body.decode('utf-8'))
        # We're asserting outside of a test class, which is a little weird.
        assert client_payload == self.expected_payload
        return (200, headers, json.dumps(EXPECTED_RESPONSE))


class TestOSDBasic(TestOSD):

    expected_payload = {'hosts': ['myosd1']}

    def test_basic(self):
        c = CephInstallerClient(INSTALL_HOST)
        assert c.osd.install(['myosd1']) == EXPECTED_IDENTIFIER


class TestOSDRedHatStorage(TestOSD):

    expected_payload = {'hosts': ['myosd1'],
                        'redhat_storage': True}

    def test_redhat_storage(self):
        c = CephInstallerClient(INSTALL_HOST)
        payload = {'redhat_storage': True}
        assert c.osd.install(['myosd1'], payload) == EXPECTED_IDENTIFIER
