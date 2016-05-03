Python ceph-installer-client
============================

.. image:: https://travis-ci.org/ktdreyer/python-ceph-installer-client.svg?branch=master
          :target: https://travis-ci.org/ktdreyer/python-ceph-installer-client

A Python library for accessing the ceph-installer REST API service.

This is useful for testing the `ceph-installer`_ application.

Installing from GitHub
======================

The module is not yet on PyPI, so please just clone from Git and install::

  virtualenv venv
  . venv/bin/activate
  git clone https://github.com/ktdreyer/python-ceph-installer-client.git
  python setup.py develop

Example: Install and configure a cluster
========================================

In this example, let's say that you've set up the ceph-installer software on
``192.0.2.1``:

.. code-block:: python

    from ceph_installer_client import CephInstallerClient

    # This host is running the installer webservice on TCP port 8181.
    c = CephInstallerClient('192.0.2.1')

    # Check the status:
    assert c.status() is True

    # Install ceph-mon software on monitors:
    c.mon.install(['mymonitor1', 'mymonitor2'])

    # Or specify extra options:
    c.mon.install(['mymonitor1'], {'redhat_storage': True,
                                             'calamari': True})

    # Install ceph-osd software on OSDs:
    c.osd.install(['myosd1', 'myosd2'])

    # Configure the monitors
    monitors = [{'host': 'mymon1', 'interface': 'eth0'},
                {'host': 'mymon2', 'interface': 'eth0'}]
    options = {
        'fsid': 'deedcb4c-a67a-4997-93a6-92149ad2622a',
        'monitor_secret': 'AQA7P8dWAAAAABAAH/tbiZQn/40Z8pr959UmEA==',
        'public_network': '192.0.2.0/24',
    }
    c.mon.configure(monitors, options)

    # Configure the OSDs
    options = {'devices': {'/dev/vdb': '/dev/vdc'},
               'fsid': 'deedcb4c-a67a-4997-93a6-92149ad2622a',
               'journal_size': 5120,
               'monitors': monitors
               'public_network': '172.16.0.0/12'}
    c.osd.configure(osds, options)

Example: Handling tasks
=======================

.. code-block:: python

    # Get a list of tasks in the queue:
    for task in c.tasks():
        print(vars(task))

    # Get information for a particular task:
    print(c.tasks('cb484401-b3ad-4cfa-8725-d6495713c451'))

    # Submit an OSD install task, then check its status.
    task_id = c.osd.install(['myosd1', 'myosd2'])
    task = c.tasks(task_id)
    print task['started'] # "None" if the server has not yet started the task.

    # The configure() calls will return multiple task IDs.
    task_ids = c.osd.configure(osds, options)

.. _`ceph-installer`: https://pypi.python.org/pypi/ceph-installer
