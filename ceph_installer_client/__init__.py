import json
import logging
import posixpath

import six
from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.error import HTTPError

__version__ = '0.0.1'

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
log = logging.getLogger('ceph-installer-client')


class CephInstallerClientBase(object):
    """ Base object for the API endpoints """

    def __init__(self, base_url):
        """
        :param base_url: The Base URL for this API object
        :type base_url: str
        """
        self.base_url = base_url

    def _api_url(self, endpoint):
        return posixpath.join(self.base_url, endpoint)

    def _get(self, endpoint):
        url = self._api_url(endpoint)
        log.debug('GETing %s' % url)
        response = urlopen(Request(url))
        if six.PY2:
            encoding = response.headers.getparam('charset') or 'utf-8'
            # if encoding is None:
            #    encoding = 'utf-8'
        else:
            encoding = response.headers.get_content_charset(failobj='utf-8')
        return json.loads(response.read().decode(encoding))

    def _post(self, endpoint, payload):
        url = self._api_url(endpoint)
        log.debug('POSTing %s to %s' % (payload, url))
        post_payload = json.dumps(payload).encode('utf-8')
        response = urlopen(Request(url, post_payload))
        if six.PY2:
            encoding = response.headers.getparam('charset') or 'utf-8'
            # if encoding is None:
            #    encoding = 'utf-8'
        else:
            encoding = response.headers.get_content_charset(failobj='utf-8')
        return json.loads(response.read().decode(encoding))

    def _monitors_payload(self, mon_hosts, exclude=None):
        data = []
        for host in mon_hosts:
            if host != exclude:
                data.append({'host': host, 'interface': 'eth0'})
        return data

    def install(self, hosts, options={}):
        """
        Install ceph-mon or ceph-osd to a list of hosts.

        :param hosts: A list of hosts to which to install.
        :type base_url: str
        """
        payload = {'hosts': hosts}
        payload.update(options)
        return self._post('install/', payload)


class CephInstallerClient(CephInstallerClientBase):
    """ Object for the /api/ endpoints """

    def __init__(self, host):
        """
        Return new CephInstallerClient object

        :param host: host that is running the ceph-installer service on TCP
                     port 8181
        :type host: str
        """
        base_url = 'http://%s:8181/api/' % host
        self.mon = Mon(base_url + 'mon/')
        self.osd = OSD(base_url + 'osd/')
        super(CephInstallerClient, self).__init__(base_url)

    def status(self):
        """
        Check the /api/status endpoint.

        :returns: True if successful
        :raises: CephInstallerClientError if unsuccessful
        """
        try:
            status = self._get('status/')
            return status['message'] == 'ok'
        except HTTPError as e:
            if six.PY2:
                encoding = e.headers.getparam('charset') or 'utf-8'
            else:
                encoding = e.headers.get_content_charset(failobj='utf-8')
            status = json.loads(e.read().decode(encoding))
            raise CephInstallerClientError(status['message'])

    def tasks(self, task_id=None):
        """
        Get data from the /api/tasks endpoint.

        :param task_id: The UUID corresponding to a particular task (optional).
        :type base_url: str

        :returns: A dict that corresponds to a task_id. If no task_id is
                  specified, returns list of all task dicts.
        """
        if task_id is not None:
            return self._get(posixpath.join('tasks', task_id + '/'))
        return self._get('tasks/')


class Mon(CephInstallerClientBase):
    """ Object for the /api/mon endpoints """

    def configure(self, hosts, options={}):
        for ip in hosts:
            payload = {
                'host': ip,
                'interface': 'eth0',
                'fsid': 'deedcb4c-a67a-4997-93a6-92149ad2622a',
                'monitor_secret': 'AQA7P8dWAAAAABAAH/tbiZQn/40Z8pr959UmEA==',
                'cluster_network': '172.16.0.0/12',
                'public_network': '172.16.0.0/12',
                'redhat_storage': True,
            }
            monitors = self._monitors_payload(hosts, ip)
            if len(monitors) > 0:
                payload['monitors'] = monitors
            self._post('configure/', payload)


class OSD(CephInstallerClientBase):
    """ Object for the /api/osd endpoints """

    def configure(self, hosts, mon_hosts):
        monitors = self._monitors_payload(mon_hosts)
        # XXX: Don't hard-code redhat_storage (and others) here.
        for ip in hosts:
            payload = {
                'host': ip,
                'devices': {'/dev/vdb': '/dev/vdc'},
                'journal_size': 5120,
                'fsid': 'deedcb4c-a67a-4997-93a6-92149ad2622a',
                'cluster_network': '172.16.0.0/12',
                'public_network': '172.16.0.0/12',
                'monitors': monitors,
                'redhat_storage': True,
            }
            self._post('configure/', payload)


class CephInstallerClientError(RuntimeError):
    pass
