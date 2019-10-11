Compute Sessions
================

.. note::

   Please consult the detailed usage in the help of each command
   (use ``-h`` or ``--help`` argument to display the manual).


Listing sessions
----------------

List the session owned by you with various status filters.
The most recently status-changed sessions are listed first.
To prevent overloading the server, the result is limited to the first 10 sessions and
it provides a separate ``--all`` option to paginate further sessions.

.. code-block:: shell

  backend.ai ps

The ``ps`` command is an alias of the following ``admin sessions`` command.
If you have the administrator privilege, you can list sessions owned by
other users by adding ``--access-key`` option here.

.. code-block:: shell

  backend.ai admin sessions

Both commands offers options to set the status filter as follows.
For other options, please consult the output of ``--help``.

.. list-table::
   :widths: 15 85
   :header-rows: 1

   * - Option
     - Included Session Status

   * - (no option)
     - ``PENDING``, ``PREPARING``, ``RUNNING``, ``RESTARTING``,
       ``TERMINATING``, ``RESIZING``, ``SUSPENDED``, and ``ERROR``.

   * - ``--running``
     - ``PREPARING``, ``PULLING``, and ``RUNNING``.

   * - ``--dead``
     - ``CANCELLED`` and ``TERMINATED``.


.. _simple-execution:

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


Please note that your ``run`` command may hang up for a very long time
due to queueing when the cluster resource is not sufficiently available.

To avoid indefinite waiting, you may add ``--enqueue-only`` to return
immediately after posting the session creation request.

.. note::

   When using ``--enqueue-only``, the codes are *NOT* executed and relevant
   options are ignored.
   This makes the ``run`` command to the same of the ``start`` command.

Or, you may use ``--max-wait`` option to limit the maximum waiting time.
If the session starts within the given ``--max-wait`` seconds, it works
normally, but if not, it returns without code execution like when used
``--enqueue-only``.

To watch what is happening behind the scene until the session starts,
try ``backend.ai events <sessionID>`` to receive the lifecycle events
such as its scheduling and preparation steps.


Accessing sessions via SSH/SFTP
-------------------------------

Backend.AI offers direct access to compute sessions (containers) via SSH and SFTP,
by auto-generating host identity and user keypairs for all sessions.

In a terminal, prepare your session and download an auto-generated SSH keypair named ``id_container``.
Then start the service port proxy ("app" command) to open a local TCP port
that proxies the SSH/SFTP traffic to the compute sessions:

.. code-block:: console

  $ backend.ai start -t mysess ...
  $ backend.ai download mysess id_container
  $ mv id_container ~/.ssh
  $ backend.ai app mysess sshd -b 9922

In another terminal on the same PC, run your ssh client like:

.. code-block:: console

  $ ssh -o StrictHostKeyChecking=no \
  >     -o UserKnownHostsFile=/dev/null \
  >     -i ~/.ssh/id_container \
  >     work@localhost -p 9922
  Warning: Permanently added '[127.0.0.1]:9922' (RSA) to the list of known hosts.
  f310e8dbce83:~$

This SSH port is also compatible with SFTP to browse the container's filesystem and to upload/download
large-sized files.

You could add the following to your ``~/.ssh/config`` to avoid type
extra options every time.

.. code-block:: text

  Host localhost
    User work
    IdentityFile ~/.ssh/id_container
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null

.. code-block:: console

  $ ssh localhost -p 9922

.. warning::

   Since the SSH keypair is auto-generated every time when your launch a new compute session,
   you need to download and keep it separately for each session.

To use your own SSH private key across all your sessions without downloading the auto-generated one every
time, create a vfolder named ``.ssh`` and put the ``authorized_keys`` file that includes the public key.
The keypair and ``.ssh`` directory permissions will be automatically updated by Backend.AI when the
session launches.

.. code-block:: console

  $ ssh-keygen -t rsa -b 2048 -f id_container
  $ cat id_container.pub > authorized_keys
  $ backend.ai vfolder create .ssh
  $ backend.ai vfolder upload .ssh authorized_keys


Running sessions with accelerators
----------------------------------

The following command spawns a Python TensorFlow session using a half
of virtual GPU device and executes ``./mygpucode.py`` file inside it.

.. code-block:: shell

  backend.ai run --rm -r gpu=0.5 \
             python-tensorflow:1.12-py36 ./mygpucode.py


Terminating or cancelling sessions
----------------------------------

Without ``--rm`` option, your session remains alive for a configured
amount of idle timeout (default is 30 minutes).
You can see such sessions using the ``backend.ai ps`` command.
Use the following command to manually terminate them via their session
IDs.  You may specifcy multiple session IDs to terminate them at once.

.. code-block:: shell

  backend.ai rm <sessionID> [<sessionID>...]

If you terminate ``PENDING`` sessions which are not scheduled yet, they are cancelled.
