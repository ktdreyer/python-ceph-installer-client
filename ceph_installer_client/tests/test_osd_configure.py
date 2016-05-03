import json

import httpretty

from ceph_installer_client import CephInstallerClient

INSTALL_HOST = 'installer.example.com'

EXPECTED_IDENTIFIER = '47f60562-a96b-4ac6-be07-71726b595793'

EXPECTED_RESPONSE = {
    'endpoint': '/api/osd/configure/',
    'succeeded': False,
    'stdout': None,
    'started': None,
    'exit_code': None,
    'ended': None,
    'command': None,
    'stderr': None,
    'identifier': EXPECTED_IDENTIFIER
}


OPTIONS = {
    'devices': {'/dev/vdb': '/dev/vdc'},
    'fsid': 'deedcb4c-a67a-4997-93a6-92149ad2622a',
    'journal_size': 5120,
    'monitors': [{'host': 'mymon1', 'interface': 'eth0'},
                 {'host': 'mymon2', 'interface': 'eth0'}],
    'public_network': '172.16.0.0/12',
}


class TestOSDConfigure(object):

    def setup_method(self, method):
        httpretty.enable()
        httpretty.reset()
        httpretty.register_uri(
            httpretty.POST, 'http://%s:8181/api/osd/configure/' % INSTALL_HOST,
            body=self.post_request_callback, content_type='application/json')
        self.requests = []

    def post_request_callback(self, request, uri, headers):
        self.requests.append(request)
        return (200, headers, json.dumps(EXPECTED_RESPONSE))


class TestOSDConfigureBasic(TestOSDConfigure):

    def test_basic(self):
        c = CephInstallerClient(INSTALL_HOST)
        result_task_id = c.osd.configure(['myosd1'], OPTIONS)
        assert result_task_id == [EXPECTED_IDENTIFIER]
        expected_body = OPTIONS.copy()
        expected_body['host'] = 'myosd1'
        result_body = json.loads(httpretty.last_request().body.decode('utf-8'))
        assert result_body == expected_body


class TestOSDConfigureMultiple(TestOSDConfigure):

    def test_multiple(self):
        c = CephInstallerClient(INSTALL_HOST)
        osds = ['myosd1', 'myosd2', 'myosd3']
        c.osd.configure(osds, OPTIONS) == [EXPECTED_IDENTIFIER] * 3
        assert len(self.requests) == 3
        for i in range(0, 3):
            expected_body = OPTIONS.copy()
            expected_body['host'] = 'myosd%d' % (i + 1)
            result_body = json.loads(self.requests[i].body.decode('utf-8'))
            assert result_body == expected_body
