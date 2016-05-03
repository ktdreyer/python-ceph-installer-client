import json
import logging
import posixpath

import six
from six.moves.urllib.request import Request, urlopen
from six.moves.urllib.error import HTTPError

__version__ = '0.0.3'

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

    def _parse_json(self, response):
        """
        Return a dict from JSON data in a urllib.response object.

        :param response: a urllib.response object
        :returns: ``dict``
        """
        if six.PY2:
            encoding = response.headers.getparam('charset') or 'utf-8'
            # if encoding is None:
            #    encoding = 'utf-8'
        else:
            encoding = response.headers.get_content_charset(failobj='utf-8')
        return json.loads(response.read().decode(encoding))

    def _get(self, endpoint):
        url = self._api_url(endpoint)
        log.debug('GETing %s' % url)
        response = urlopen(Request(url))
        return self._parse_json(response)

    def _post(self, endpoint, payload):
        url = self._api_url(endpoint)
        log.debug('POSTing %s to %s' % (payload, url))
        post_payload = json.dumps(payload).encode('utf-8')
        response = urlopen(Request(url, post_payload))
        return self._parse_json(response)

    def _monitors_payload(self, mon_hosts, exclude):
        """
        Return a list of monitor host dicts, except the one to "exclude".

        :param mon_hosts: ``list`` of dicts
        :param exclude: ``dict`` of a host to exclude from mon_hosts.

        :returns: ``list`` of dicts
        """
        data = []
        for mon in mon_hosts:
            if mon['host'] != exclude['host']:
                data.append(mon)
        return data

    def install(self, hosts, options={}):
        """
        Install ceph-mon or ceph-osd to a list of hosts.

        :param hosts: A list of hosts to which to install.

        :returns: A task ID (str).
        """
        payload = {'hosts': hosts}
        payload.update(options)
        result = self._post('install/', payload)
        return result['identifier']


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

    def configure(self, hosts, options):
        """
        Configure a list of Monitor hosts.

        :param hosts: list of monitor dicts

        :returns: list of task IDs
        """
        for required in ['fsid', 'monitor_secret', 'public_network']:
            if options.get(required, None) is None:
                raise ValueError('"options" must contain a %s key' % required)
        task_ids = []
        for host in hosts:
            payload = host.copy()
            payload.update(options)
            monitors = self._monitors_payload(hosts, host)
            if len(monitors) > 0:
                payload['monitors'] = monitors
            result = self._post('configure/', payload)
            task_ids.append(result['identifier'])
        return task_ids


class OSD(CephInstallerClientBase):
    """ Object for the /api/osd endpoints """

    def configure(self, hosts, options):
        """
        Configure a list of OSD hosts.

        :returns: list of task IDs
        """
        # Sanity-check that options has the minimum required keys.
        for required in ['devices', 'fsid', 'journal_size', 'monitors',
                         'public_network']:
            if options.get(required, None) is None:
                raise ValueError('"options" must contain a %s key' % required)
        task_ids = []
        for ip in hosts:
            payload = {'host': ip}
            payload.update(options)
            result = self._post('configure/', payload)
            task_ids.append(result['identifier'])
        return task_ids


class CephInstallerClientError(RuntimeError):
    pass
