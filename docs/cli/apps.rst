Container Applications
======================

.. note::

   Please consult the detailed usage in the help of each command
   (use ``-h`` or ``--help`` argument to display the manual).


Starting a session and connecting to its Jupyter Notebook
---------------------------------------------------------

The following command first spawns a Python session named "mysession"
without running any code immediately, and then executes a local proxy which connects
to the "jupyter" service running inside the session via the local TCP port 9900.
The ``start`` command shows application services provided by the created compute
session so that you can choose one in the subsequent ``app`` command.
In the ``start`` command, you can specify detailed resource options using ``-r``
and storage mounts using ``-m`` parameter.

.. code-block:: shell

  backend.ai start -t mysession python
  backend.ai app -p 9900 mysession jupyter

Once executed, the ``app`` command waits for the user to open the displayed
address using appropriate application.
For the jupyter service, use your favorite web browser just like the
way you use Jupyter Notebooks.
To stop the ``app`` command, press ``Ctrl+C`` or send the ``SIGINT`` signal.

Accessing the shell (terminal) of sessions
------------------------------------------

All Backend.AI sessions expose an intrinsic application named "ttyd".

.. code-block:: shell

   backend.ai start -t mysession ...
   backend.ai app -p 9900 mysession ttyd

Then open ``http://localhost:9900`` to access the shell in a fully functional web terminal using
browsers.
The default shell is ``/bin/bash`` for Ubuntu/CentOS-based images and ``/bin/ash`` for Alpine-based
images with a fallback to ``/bin/sh``.

.. note::

   This shell access does *NOT* grant your root access.
   All compute session processes are executed as the user privilege.
