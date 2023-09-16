import os
import sys

from colorclass import Color


def is_virtualenv():  # pragma: nocover (This function is mocked and cannot be tested)
    """
    Check if the current environment is a virtual environment.

    :return: True if it's a virtual environment, False otherwise.
    """
    if getattr(sys, 'base_prefix', sys.prefix) != sys.prefix:
        return True

    if hasattr(sys, 'real_prefix'):
        return True

    if os.environ.get('VIRTUAL_ENV'):
        return True

    return False


def check_for_virtualenv(options):
    """
    Check for a virtual environment and provide instructions if not activated.

    :param options: Command-line options.
    """
    if options.get('--skip-virtualenv-check', False) or options.get('--skip-package-installation', False):
        return  # No check needed

    if not is_virtualenv():
        print(Color("{autored}It appears that you haven't activated a virtual environment.\n"
                    "Installing packages directly in the system is not recommended.\n"
                    "Please {automagenta}activate your project's virtual environment{/automagenta} "
                    "or {automagenta}rerun this command{/automagenta} with one of the following options:\n"
                    "--skip-virtualenv-check (install the packages anyway)\n"
                    "--skip-package-installation (don't install any packages, just update the requirements file(s))."
                    "{/autored}"))
        raise KeyboardInterrupt()
