import os
import locale

# Remove system environment variables that could override the default test locale
for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
    os.environ.pop(var, None)

# Globally mock locale.getdefaultlocale to return an English locale.
# This simulates running the test suite on an English OS, which keeps all
# legacy English-asserting tests green while allowing individual tests to
# monkeypatch the settings for testing other locales.
locale.getdefaultlocale = lambda: ("en_US", "UTF-8")
