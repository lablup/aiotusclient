Code Exectuion and Monitoring (Streaming Mode)
==============================================

The streaming mode allows the clients to interact with the kernel session in real-time.
For example, a front-end service may provide an input field for CLI prompts of the user program or a complete terminal emulation.

Common URI
----------

All the APIs for the streaming mode use a single URI for each kernel session, while the server distinguishes different type of messages by inspecting their content.

* URI: ``/v1/stream/kernel/:id``
* Method: WebSockets

Common Parameters
"""""""""""""""""

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Parameter
     - Description
   * - ``:id``
     - The kernel ID.

Interacting with the user program
---------------------------------




Monitoring events from the kernel session
-----------------------------------------



Rate limiting
-------------

The streaming mode uses the same rate limiting policy as other APIs use.
The limitation only applies to client-generated messages but not to the server-generated messages.

Usage metrics
-------------

The streaming mode uses the same method that the query mode uses to measure the usage metrics such as the memory and CPU time used.
