import json

import httpretty

from ceph_installer_client import CephInstallerClient

INSTALL_HOST = 'installer.example.com'

EXPECTED_IDENTIFIER = '47f60562-a96b-4ac6-be07-71726b595793'

EXPECTED_RESPONSE = {
    'endpoint': '/api/mon/configure/',
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
    'interface': 'eth0',
    'fsid': 'deedcb4c-a67a-4997-93a6-92149ad2622a',
    'monitor_secret': 'AQA7P8dWAAAAABAAH/tbiZQn/40Z8pr959UmEA==',
    'public_network': '172.16.0.0/12',
}


class TestMonConfigure(object):

    def setup_method(self, method):
        httpretty.enable()
        httpretty.reset()
        httpretty.register_uri(
            httpretty.POST, 'http://%s:8181/api/mon/configure/' % INSTALL_HOST,
            body=self.post_request_callback, content_type='application/json')
        self.requests = []

    def post_request_callback(self, request, uri, headers):
        self.requests.append(request)
        return (200, headers, json.dumps(EXPECTED_RESPONSE))


class TestMonConfigureBasic(TestMonConfigure):

    def test_basic(self):
        c = CephInstallerClient(INSTALL_HOST)
        monitors = [{'host': 'mymon1', 'interface': 'eth0'}]
        assert c.mon.configure(monitors, OPTIONS) == [EXPECTED_IDENTIFIER]
        expected_body = OPTIONS.copy()
        expected_body['host'] = 'mymon1'
        expected_body['interface'] = 'eth0'
        result_body = json.loads(httpretty.last_request().body.decode('utf-8'))
        assert result_body == expected_body


class TestMonConfigureMultiple(TestMonConfigure):

    # XXX: this depends on dict ordering :(
    expected_payloads = [
        {
            'host': 'mymon1', 'interface': 'eth0',
            'monitors': [{'host': 'mymon2', 'interface': 'eth0'},
                         {'host': 'mymon3', 'interface': 'eth0'}]
        },
        {
            'host': 'mymon2', 'interface': 'eth0',
            'monitors': [{'host': 'mymon1', 'interface': 'eth0'},
                         {'host': 'mymon3', 'interface': 'eth0'}]
        },
        {
             'host': 'mymon3', 'interface': 'eth0',
             'monitors': [{'host': 'mymon1', 'interface': 'eth0'},
                          {'host': 'mymon2', 'interface': 'eth0'}]
        },
    ]

    def test_multiple(self):
        c = CephInstallerClient(INSTALL_HOST)
        monitors = [{'host': 'mymon1', 'interface': 'eth0'},
                    {'host': 'mymon2', 'interface': 'eth0'},
                    {'host': 'mymon3', 'interface': 'eth0'}]
        assert c.mon.configure(monitors, OPTIONS) == [EXPECTED_IDENTIFIER] * 3
        assert len(self.requests) == 3
        for i in range(0, 3):
            expected_body = self.expected_payloads[i]
            expected_body.update(OPTIONS)
            result_body = json.loads(self.requests[i].body.decode('utf-8'))
            assert result_body == expected_body
