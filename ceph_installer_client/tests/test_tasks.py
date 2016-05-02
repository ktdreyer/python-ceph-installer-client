import json

import httpretty

from ceph_installer_client import CephInstallerClient

INSTALL_HOST = 'installer.example.com'

ALL_TASKS_EXPECTED_RESPONSE = [
    {
        'endpoint': '/api/osd/install/',
        'succeeded': False,
        'stdout': None,
        'started': None,
        'exit_code': None,
        'ended': None,
        'command': None,
        'stderr': None,
        'identifier': '47f60562-a96b-4ac6-be07-71726b595793'
    },
    {
        'endpoint': '/api/osd/install/',
        'succeeded': False,
        'stdout': None,
        'started': None,
        'exit_code': None,
        'ended': None,
        'command': None,
        'stderr': None,
        'identifier': 'cfda82b5-19bd-43fa-b997-bc1058291703'
    },
]

ONE_TASK_EXPECTED_RESPONSE = {
    'endpoint': '/api/osd/install/',
    'succeeded': False,
    'stdout': None,
    'started': None,
    'exit_code': None,
    'ended': None,
    'command': None,
    'stderr': None,
    'identifier': 'cfda82b5-19bd-43fa-b997-bc1058291703'
}


def setup_module(module):
    httpretty.enable()
    httpretty.register_uri(
        httpretty.GET, 'http://%s:8181/api/tasks/' % INSTALL_HOST,
        body=json.dumps(ALL_TASKS_EXPECTED_RESPONSE),
        content_type='application/json')

    httpretty.register_uri(
        httpretty.GET,
        'http://%s:8181/api/tasks/cfda82b5-19bd-43fa-b997-bc1058291703/'
        % INSTALL_HOST,
        body=json.dumps(ONE_TASK_EXPECTED_RESPONSE),
        content_type='application/json')


class TestTasks(object):

    def test_list_all(self):
        c = CephInstallerClient(INSTALL_HOST)
        assert c.tasks() == ALL_TASKS_EXPECTED_RESPONSE

    def test_get_one(self):
        c = CephInstallerClient(INSTALL_HOST)
        task = c.tasks('cfda82b5-19bd-43fa-b997-bc1058291703')
        assert task == ONE_TASK_EXPECTED_RESPONSE
