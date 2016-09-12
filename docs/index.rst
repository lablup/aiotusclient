.. Sorna API Library documentation master file, created by
   sphinx-quickstart on Tue Mar  1 21:26:20 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Sorna API Library
=================

Sorna is an online code execution service that runs arbitrary user codes
safely in resource-constrained environments, using Docker and our own sandbox
wrapper.
It currently supports Python 2/3, R, PHP and NodeJS, with more being added.
Sorna's primary target is to provide a zero-configuration evaluation tool for
short-running programs used in education and scientific researches, such as
problem solving and plotting.


.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   gsg/registration
   gsg/clientlib

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/convention
   api/auth
   api/ratelimit
   api/kernels
   api/exec
   api/stream


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

