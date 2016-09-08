Kernel Management
=================

All JSON responses described here are only for successful returns (HTTP status 2xx).
For failures (HTTP status 4xx/5xx), the JSON response is an object that contains at least two keys: ``type`` which uniquely identifies the failure reason as an URI and ``title`` for human-readable error messages.
Some failures may return extra structured information as additional key-value pairs.

Creating a kernel session
-------------------------

* URI: ``/v1/kernel/create``
* Method: ``POST``

Creates a kernel session to run user-input code snippets.

Parameters
""""""""""

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Parameter
     - Description
   * - ``lang``
     - The kernel type, usually a name of our supported programming languages.

Example:

.. code-block:: json

   {
     "lang": "python3"
   }


Response
""""""""

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - HTTP Status Code
     - Description
   * - 201 Created
     - The kernel is successfully created.

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Parameter
     - Description
   * - ``kernelId``
     - The kernel ID used for later API calls.


Example:

.. code-block:: json

   {
     "kernelId": "aaaaa"
   }

Getting kernel information
--------------------------

* URI: ``/v1/kernel/:id``
* Method: ``GET``

Retrieves information about a kernel session.

Parameters
""""""""""

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Parameter
     - Description
   * - ``kernelId``
     - The kernel ID.

Example:

.. code-block:: json

   {
     "kernelId": "aaaaa"
   }


Response
""""""""

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - HTTP Status Code
     - Description
   * - 200 OK
     - The information is successfully returned.
   * - 404 Not Found
     - There is no such kernel.

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Parameter
     - Description
   * - ``lang``
     - The kernel type.
   * - ``age``
     - The time elapsed since the kernel has started in milliseconds.
   * - ``idle``
     - The time elapsed since the kernel has generated any output in milliseconds.
   * - ``queryTimeout``
     - The timeout for executing each query (the time between accepting a query and receiving the output) in milliseconds.
       If exceeded, the kernel is automatically destroyed.
   * - ``idleTimeout``
     - The maximum duration between queries in milliseconds.
       If exceeded, the kernel is automatically destroyed.
   * - ``maxCpuCredit``
     - The maximum amount of CPU time that this kernel can use in milliseconds.
       If exceeded, the kernel is automatically destroyed.
       If zero, there is no limit imposed.
   * - ``numQueriesExecuted``
     - The total number of queries executed after start-up.
   * - ``memoryUsed``
     - The amount of memory that this kernel is using now in KB.
   * - ``cpuCreditUsed``
     - The amount of CPU time that this kernel has used so far in milliseconds.

Example:

.. code-block:: json

   {
     "lang": "python3",
     "age": 30220,
     "idle": 1204,
     "queryTimeout": 15000,
     "idleTimeout": 3600000,
     "maxCpuCredit": 0,
     "numQueriesExecuted": 12,
     "memoryUsed": 6531,
     "cpuCreditUsed": 102
   }

Destroying a kernel session
---------------------------

* URI: ``/v1/kernel/:id``
* Method: ``DELETE``

Terminates a kernel session.

Parameters
""""""""""

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Parameter
     - Description
   * - ``kernelId``
     - The kernel ID.

Example:

.. code-block:: json

   {
     "kernelId": "aaaaa"
   }


Response
""""""""

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - HTTP Status Code
     - Description
   * - 204 No Content
     - The kernel is successfully destroyed.
   * - 404 Not Found
     - There is no such kernel.

Restarting a kernel session
---------------------------

* URI: ``/v1/kernel/:id``
* Method: ``PATCH``

Restarts a kernel session.
The idle time of the kernel will be reset, but other properties such as the age and CPU credit will continue to accumulate.

Parameters
""""""""""

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Parameter
     - Description
   * - ``kernelId``
     - The kernel ID.

Example:

.. code-block:: json

   {
     "kernelId": "aaaaa"
   }

Response
""""""""

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - HTTP Status Code
     - Description
   * - 204 No Content
     - The kernel is successfully destroyed.
   * - 404 Not Found
     - There is no such kernel.
