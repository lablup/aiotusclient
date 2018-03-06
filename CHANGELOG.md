Changes
=======

1.1.11 (2018-03-07)
-------------------

 - Change StreamPty methods to become coroutines to match with aiohttp v3
   API changes.

1.1.10 (2018-03-04)
-------------------

 - Fix file upload handling in the asyncio version.

 - Stringifying exception classes now use the output of "repr()".

1.1.9 (2018-03-02)
------------------

 - Improve asyncio exception handling.
   Now it does NOT silently swallow CancelledError/TimeoutError and other
   non-aiohttp errors!

1.1.8 (2018-03-01)
------------------

 - Upgrade to use aiohttp v3 series.

 - Improve handling of base directories outside the current working directory
   when uploading files for the batch mode execution.

 - Display exit code if available in the batch mode execution.

1.1.7 (2018-01-09)
------------------

 - Hotfix: Add missing "ai.backend.client.cli.admin" module in the package.

1.1.6 (2018-01-06)
------------------

 - Apply authentication to websocket requests as well.

 - Fix the client-side validation of client token length.

1.1.5 (2018-01-05)
------------------

 - Relicensed to MIT License to motivate integration with commercial/proprietary
   software products.

 - Lots of CLI improvements!

   - Add "terminate" command.

   - Add more "run" command options.  Now it does NOT terminate the session after
     execution by default, and you can force it using "--rm" option.

   - Add "admin keypairs" command and its subcommands for managing keypairs.

   - Add "admin agents" command to list agent instances.

   - "ps" and "admin session" commands now correctly show the client-given session ID
     token instead of the master kernel ID of the session.

   - Add "logs" command.

 - Fix a continuation bug of the "run" command when using the batch-mode, which
   has caused a mismatch of run ID management of the agent and the internal task
   queue of the kernel runner, resulting an indefinite hang up with two legitimate
   subsequent requesting of batch-mode executions.

   As being a reference implementation of the execution loop, all API users are
   advised to review and fix their client-side codes.

 - Now the client sets a custom User-Agent header value as follows:
   "Backend.AI Client for Python X.X.X" where X.X.X is the version.

1.1.1 (2017-12-04)
------------------

 - Add mount ("-m"), environment variable ("-e") arguments to CLI "run" command
   which can be specified multiple times.
   This deprecates "-b" and "-e" abbreviations for "--build" and "--exec".

 - Fix garbled tabular outputs of CLI commands in Python versions less than 3.6
   due to non-preserved dictionary ordering.

1.1.0 (2017-11-17)
------------------

**NEW**

 - Now the CLI supports "vfolder" subcommands.

1.0.6 (2017-11-16)
------------------

**CHANGES**

 - Now it uses "api.backend.ai" as the default endpoint.

 - It also searches `BACKEND_`-prefixed environment variables first and then
   falls back to `SORNA_`-prefixed environment variables as legacy.

1.0.5 (2017-11-02)
------------------

**CHANGE**

 - Remove `simplejson` from our dependencies.

1.0.4 (2017-10-31)
------------------

**NEW**

 - Add "-s" / "--stats" option to the CLI "run" command.
   When specified, the CLI shows resource usage statistics after session termination.

1.0.3 (2017-10-18)
------------------

**NEW**

 - Now you can run the CLI commands using "backend.ai"
   instead of "python -m ai.backend.client.cli"

 - Add a few new CLI commands: config, help, ps

 - Running "backend.ai" without any args shows the help message
   instead of an error.

**FIX**

 - Fix colored terminal output in *NIX (#12)

1.0.2 (2017-10-07)
------------------

**FIX**

 - Make the colored terminal output working on Windows (#12)

1.0.1 (2017-10-06)
------------------

**FIXES**

 - Include missing dependencies: multidict

 - Improve Windows platform supports (#12)

**CHANGES**

 - Install asyncio-based dependencies by default (aiohttp and async_timeout)

1.0.0 (2017-09-20)
------------------

**CHANGES**

 - Rename the product name "Sorna" to "Backend.AI".
   - Package import path: "sorna" → "ai.backend.client"
   - Class names: "SornaError" / "SornaAPIError" → "BackendError" / "BackendAPIError"
   - Any mention of "Sorna" in the API headers → "BackendAI".
     e.g., "X-Sorna-Version" API request header → "X-BackendAI-Version"

 - Refactor the internal structure for sync/async API functions.

 - Add support for the Admin API based on GraphQL both in the CLI and the functions.
   Now you can list up details of your compute sessions with ease.

0.9.7 (2017-08-25)
------------------

**FIX**

 - Missing sorna.cli module in distribution.


0.9.6 (2017-08-25)
------------------

**NEW**

 - Add console scripts "lcc" and "lpython" which are aliases
   of "python -m sorna.cli run c" and "python -m sorna.cli run python".

 - Add explicit "--build" and "--exec" option for batch-mode
   customization.

0.9.5 (2017-06-30)
------------------

**FIX**

 - Fix support for interactive inputs in the batch mode.

0.9.4 (2017-06-29)
------------------

**CHANGES**

 - The `run` command now prints the build status in the batch mode.

0.9.3 (2017-06-29)
------------------

**NEW**

 - The command-line interface.  Try `python -m sorna.cli run` command.

 - It supports the batch-mode API with source file uploads.

 - The client now now runs on Python 3.5 as well as Python 3.6.
   (Debian 9 / Ubuntu 16.04 users can install the client without
   searching for Google!)

0.9.2 (2017-04-20)
------------------

**NEW**

 - It supports the draft auto-completion API.

**FIX**

 - Now compatible with aiohttp 2.0+

0.9.1 (2017-03-14)
------------------

**FIX**

 - Fix a bogus error when given empty codes for continuation.

0.9.0 (2017-03-14)
------------------

**NEW**

 - New object-style API: Kernel objects.
   You can still use the legacy (but deprecated) function API.

 - Add support for APIv2.20170315
   (vfolder API is coming soon!)

**CHANGES**

 - Now requires Python 3.6 or higher.

 - Improved exception handling.

   Now it uses a common base exception called "SornaError"
   and reports client-side errors as "SornaClientError"
   while server-side errors as "SornaAPIError".

0.8.3 (2017-01-13)
------------------

**FIX**

 - Web terminal now works via SSL-enabled API servers.

0.8.2 (2017-01-11)
------------------

**FIXES**

 - Add missing proxy method for exception() to StreamPty.

 - Fix broken async_timeout checks due to pre-mature optimization,
   by reverting the optimization (thread-local HTTP sessions).

0.8.0 (2017-01-10)
------------------

**NEW**

 - Add support for (now implemented) HTTP-based web terminal API.

0.7.0 (2016-12-14)
------------------

**NEW**

 - First "usable" release.

0.1.1 (2016-11-23)
------------------

**FIXES**

 - Add a missing package dependency (requests).

0.1.0 (2016-11-23)
------------------

**NEW**

 - First public release.

