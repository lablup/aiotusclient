Changes
=======

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

