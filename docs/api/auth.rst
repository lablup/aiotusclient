Authentication
==============

Access Tokens and Secret Key
----------------------------

To make requests to the API server, you need to get a pair of an access token and a secret key as sepcified in :doc:`/gsg/registration`.
The server uses access tokens to identify each client and secret keys to verify integrity of API requests as well as to authenticate clients.

For local deployments, you may create a master dummy pair in the configuration (TODO).

Common Structure of API Requests
--------------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - HTTP Headers
     - Values
   * - Method
     - GET / POST / PUT / PATCH / DELETE
   * - ``Content-Type``
     - Always should be ``application/json``
   * - ``Date``
     - The date/time of the request formatted in RFC 8022 or ISO 8601.
       If no timezone is specified, UTC is assumed.
       The deviation with the server-side clock must be within 15-minutes.
   * - ``X-Sorna-Date``
     - Same as ``Date``. May be omitted if ``Date`` is present.
   * - ``X-Sorna-Version``
     - ``vX.yyymmdd`` where ``X`` is the major version and                    
       ``yyyymmdd`` is the minor release date of the specified API version.
       (e.g., 20160915)
   * - ``X-Sorna-Signature``
     - Signature generated as `Signing the Requests`_.
   * - ``X-Sorna-Signing-Method``
     - Specifies the signature algorithm. (Default: HMAC-SHA1)
   * - ``X-Sorna-Client-Token``
     - An optional, client-generated random string to allow the server to distinguish repeated duplicate requests.
       It is important to keep idempotent semantics with multiple retries for intermittent failures.
       (Not implemented yet)
   * - Body
     - JSON-encoded request parameters


Common Structure of API Responses
---------------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - HTTP Headers
     - Values
   * - Status code
     - API-specific HTTP-standard status codes. Responses commonly used throughout all APIs include 200, 201, 2014, 400, 401, 403, 404, 429, and 500, but not limited to.
   * - ``Content-Type``
     - ``application/json`` and its variants (e.g., ``application/problem+json`` for errors)
   * - ``Link``
     - Web link headers specified as in `RFC 5988 <https://tools.ietf.org/html/rfc5988>`_. Only optionally used when returning a collection of objects.
   * - ``X-RateLimit-Limit``
     - The maximum allowed number of requests per hour.
   * - ``X-RateLimit-Remaining``
     - The number of requests left for the time window. If zero, you should wait for the time specified by ``X-RateLimit-Reset``. Otherwise you will get HTTP 429 "Too Many Requests".
   * - ``X-RateLimit-Reset``
     - The time to wait until the current rate limit window resets, in milli-seconds.
   * - Body
     - JSON-encoded results

We use `RFC 7807 <https://tools.ietf.org/html/rfc7807>`_-style problem detail description returned in JSON of the response body.


Signing the Requests
--------------------

Each API requests must be signed with the following signature: (TODO)

The signature type may be specified using the HTTP header ``X-Sorna-Signing-Method``.

