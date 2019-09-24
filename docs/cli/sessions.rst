Compute Sessions
================

.. note::

   Please consult the detailed usage in the help of each command
   (use ``-h`` or ``--help`` argument to display the manual).


Listing sessions
----------------

List the session owned by you with various status filters.
The most recently status-changed sessions are listed first.

.. code-block:: shell

  backend.ai ps

The ``ps`` command is an alias of the following ``admin sessions`` command.
If you have the administrator privilege, you can list sessions owned by
other users by adding ``--access-key`` option.

.. code-block:: shell

  backend.ai admin sessions

Both commands offers options to set the status filter as follows.
For other options, please consult the output of ``--help``.

.. list-table::
   :widths: 15 85
   :header-rows: 1

   * - Option
     - Effect

   * - (no option)
     - Include ``PENDING``, ``PREPARING``, ``RUNNING``, ``RESTARTING``,
       ``TERMINATING``, ``RESIZING``, ``SUSPENDED``, and ``ERROR``.

   * - ``--running``
     - Include only ``PREPARING``, ``PULLING``, and ``RUNNING``.

   * - ``--dead``
     - Include only ``CANCELLED`` and ``TERMINATED``.


Running simple sessions
-----------------------

The following command spawns a Python session and executes
the code passed as ``-c`` argument immediately.
``--rm`` option states that the client automatically terminates
the session after execution finishes.

.. code-block:: shell

  backend.ai run --rm -c 'print("hello world")' python:3.6-ubuntu18.04

.. note::

   By default, you need to specify language with full version tag like
   ``python:3.6-ubuntu18.04``. Depending on the Backend.AI admin's language
   alias settings, this can be shortened just as ``python``. If you want
   to know defined language aliases, contact the admin of Backend.AI server.


The following command spawns a Python session and executes
the code passed as ``./myscript.py`` file, using the shell command
specified in the ``--exec`` option.

.. code-block:: shell

  backend.ai run --rm --exec 'python myscript.py arg1 arg2' \
             python:3.6-ubuntu18.04 ./myscript.py


Running sessions with accelerators
----------------------------------

The following command spawns a Python TensorFlow session using a half
of virtual GPU device and executes ``./mygpucode.py`` file inside it.

.. code-block:: shell

  backend.ai run --rm -r gpu=0.5 \
             python-tensorflow:1.12-py36 ./mygpucode.py


Terminating running sessions
----------------------------

Without ``--rm`` option, your session remains alive for a configured
amount of idle timeout (default is 30 minutes).
You can see such sessions using the ``backend.ai ps`` command.
Use the following command to manually terminate them via their session
IDs.  You may specifcy multiple session IDs to terminate them at once.

.. code-block:: shell

  backend.ai rm <sessionID>
