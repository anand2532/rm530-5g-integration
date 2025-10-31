RM530 5G Integration Documentation
==================================

Welcome to the rm530-5g-integration documentation!

This package provides integration tools for Quectel RM530 5G modem with Raspberry Pi using ECM (Ethernet Control Model) mode.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   cli
   configuration
   troubleshooting

Installation
------------

.. code-block:: bash

   pip install rm530-5g-integration

Quick Start
-----------

.. code-block:: python

   from rm530_5g_integration import RM530Manager

   manager = RM530Manager()
   manager.setup(apn="airtelgprs.com")
   status = manager.status()

Features
--------

* ECM mode setup
* NetworkManager integration
* Signal quality monitoring
* Connection statistics
* Health monitoring
* Configuration management

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

