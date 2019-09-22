Configuration
=============

.. note::

   Please consult the detailed usage in the help of each command
   (use ``-h`` or ``--help`` argument to display the manual).

Check out :ref:`gsg/config` for configurations via environment variables.

Session Mode
------------

When the endpoint type is ``"session"``, you must explicitly login and logout
into/from the console server.

.. code-block:: console

   $ backend.ai login
   Username: myaccount@example.com
   Password:
   ✔ Login succeeded.

   $ backend.ai ...  # any commands

   $ backend.ai logout
   ✔ Logout done.


API Mode
--------

After setting up the environment variables, just run any command:

.. code-block:: console

   $ backend.ai ...
