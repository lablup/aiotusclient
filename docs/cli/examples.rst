Examples
========

.. note::

   Please consult the detailed usage in the help of each command
   (use ``-h`` or ``--help`` argument to display the manual).

Running simple sessions
-----------------------

.. code-block:: shell

  backend.ai run --rm -c 'print("hello world")' python

.. code-block:: shell

  backend.ai run --rm --exec 'python myscript.py arg1 arg2' \
             python ./myscript.py


Running sessions with accelerators
----------------------------------

.. code-block:: shell

  backend.ai run --rm -r gpu=0.5 \
             python-tensorflow ./mygpucode.py


Starting a session and connecting to its Jupyter Notebook
---------------------------------------------------------

.. code-block:: shell

  backend.ai start -t mysession python
  backend.ai app -p 9900 mysession jupyter

Then open ``http://localhost:9900`` to access the Jupyter Notebook running
on the ``mysession`` compute session.


Running sessions with vfolders
------------------------------

.. code-block:: shell

  backend.ai vfolder create mydata1
  backend.ai vfolder upload mydata1 ./bigdata.csv
  backend.ai run --rm -m mydata1 python ...
  backend.ai vfolder download mydata1 ./bigresult.txt


Running parallel experiment sessions
------------------------------------

(TODO)
