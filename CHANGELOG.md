# Changelog

<!--
    You should *NOT* be adding new change log entries to this file, this
    file is managed by towncrier. You *may* edit previous change logs to
    fix problems like typo corrections or such.

    To add a new change log entry, please refer
    https://pip.pypa.io/en/latest/development/contributing/#news-entries

    We named the news folder "changes".

    WARNING: Don't drop the last line!
-->

.. towncrier release notes start

## 20.03.0a1 (2020-04-07)

### Breaking Changes
* Breaking Changes without explicit PR/issue numbers
  Now the client SDK runs on Python 3.6, 3.7, and 3.8 and dropped support for Python 3.5.
* All functional API classes are moved into the `ai.backend.client.func` sub-package.
  [(#82)](https://github.com/lablup/backend.ai-client-py/issues/82)
  - `Kernel` is changed to `Session`.
  - The session ID field name in the response of `Session` objects
    is now `session_id` instead of `kernel_id`.
  - Except above, this would not introduce big changes in the SDK user
    codes since they use `AsyncSession` and `Session` in the
    `ai.backend.client.session` module.

### Features
* Features without explicit PR/issue numbers
  - Add SDK API (`SessionTemplate`) and CLI command set (`backend.ai sesstpl`)
* Support for unmanaged vfolders and token-based download API
  [(#77)](https://github.com/lablup/backend.ai-client-py/issues/77)
* `backend.ai config` command now displays the server/client component and API versions with negotiated API version if available.
  [(#79)](https://github.com/lablup/backend.ai-client-py/issues/79)
* Add `--format` and `--plain` options to `backend.ai ps` command to customize the output table format
  [(#80)](https://github.com/lablup/backend.ai-client-py/issues/80)
* Perform automatic API version negotiation when entering session contexts while keeping the functional API same
  [(#82)](https://github.com/lablup/backend.ai-client-py/issues/82)
* Support dotfiles management API and CLI
  [(#85)](https://github.com/lablup/backend.ai-client-py/issues/85)

### Fixes
* Refine details of the `app` command such as error handling
  [(#90)](https://github.com/lablup/backend.ai-client-py/issues/90)
* Improve exception handling in ``backend.ai app`` command and update backend.ai-cli package
  [(#94)](https://github.com/lablup/backend.ai-client-py/issues/94)

### Miscellaneous
* Adopt [towncrier](https://github.com/twisted/towncrier) for changelog management
  [(#95)](https://github.com/lablup/backend.ai-client-py/issues/95)
