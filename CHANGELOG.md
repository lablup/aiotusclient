Changes
=======

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

