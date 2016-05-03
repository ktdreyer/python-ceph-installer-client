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

Examples
========

In this example, let's say that you've set up the ceph-installer software on
``192.0.2.1``:

.. code-block:: python

    from ceph_installer_client import CephInstallerClient

    # This host is running the installer webservice on TCP port 8181.
    c = CephInstallerClient('192.0.2.1')

    # Check the status:
    assert c.status() is True

    # Get a list of tasks:
    for task in c.tasks():
        print(vars(task))

    # Get information for a particular task:
    print(c.tasks('cb484401-b3ad-4cfa-8725-d6495713c451'))

    # Install ceph-mon software on monitors:
    c.mon.install(['mymonitor1', 'mymonitor2'])

    # Or specify extra options:
    c.mon.install(['mymonitor1'], {'redhat_storage': True, 'calamari': True})

    # Install ceph-osd software on OSDs:
    c.osd.install(['myosd1', 'myosd2'])

.. _`ceph-installer`: https://pypi.python.org/pypi/ceph-installer
