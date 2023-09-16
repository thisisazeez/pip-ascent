"""
pip-ascent

Usage:
  pip-ascent [<requirements_file>] ... [--prerelease] [-pk=<package>...] [--dry-run] [--check-greater-equal] [--skip-virtualenv-check] [--skip-package-installation] [--use-default-index]

Arguments:
    requirements_file             Specifies the requirement FILE or uses a WILDCARD PATH to multiple files.
    --prerelease                  Includes prerelease versions for upgrades when querying PyPI repositories.
    -pk <package>                  Pre-selects packages for upgrade, bypassing any prompts. You can also utilize regular expressions to filter packages for upgrading.
    --dry-run                     Simulates the upgrade but does not perform the actual upgrade.
    --check-greater-equal         Also checks packages with minimum version pinning (package>=version).
    --skip-package-installation   Upgrades the version in requirement files only; it does not install the new package.
    --skip-virtualenv-check       Disables virtualenv check, permitting the installation of new packages outside the virtualenv.
    --use-default-index           Skips searching for a custom index-url in pip configuration file(s).

Examples:
  pip-ascent             # Automatically discovers the requirements file
  pip-ascent requirements.txt
  pip-ascent requirements/dev.txt requirements/production.txt
  pip-ascent requirements.txt -pk django -p celery
  pip-ascent requirements.txt -pk all
  pip-ascent requirements.txt --dry-run  # Runs everything as a simulation (does not perform the actual upgrade)

Help:
  Interactively upgrades packages from a requirements file and updates the pinned version in requirement file(s).
  If no requirements are provided, the command attempts to detect the requirements file(s) in the current directory.

  https://github.com/thisisazeez/pip-ascent
"""

from colorclass import Windows, Color
from docopt import docopt

from pip_ascent import __version__ as VERSION
from pip_ascent.PackageDetector import PackageDetector
from pip_ascent.InteractivePackageSelector import InteractivePackageSelector
from pip_ascent.PackageStatusDetector import PackageStatusDetector
from pip_ascent.PackageUpgrader import PackageUpgrader
from pip_ascent.RequirementsDetector import RequirementsDetector
from pip_ascent.virtualenv_checker import check_for_virtualenv


def get_options():
    return docopt(__doc__, version=VERSION)


def main():
    """ Main CLI entrypoint. """
    options = get_options()
    Windows.enable(auto_colors=True, reset_atexit=True)

    try:
        # Maybe check if the virtualenv is not activated
        check_for_virtualenv(options)

        # 1. Detect requirements files
        filenames = RequirementsDetector(options.get('<requirements_file>')).get_filenames()
        if filenames:
            print(Color('{{autogreen}}Found valid requirements file(s):{{/autogreen}} '
                        '{{autoyellow}}\n{}{{/autoyellow}}'.format('\n'.join(filenames))))
        else:
            print(Color('{autored}No requirements files found in the current directory. Change directory to your project '
                        'or manually specify requirements files as arguments.{/autored}'))
            return
        # 2. Detect all packages inside requirements
        packages = PackageDetector(filenames).get_packages()

        # 3. Query PyPI API to see which packages have newer versions compared to the ones in requirements (or the current environment)
        packages_status_map = PackageStatusDetector(
            packages, options).detect_available_upgrades(options)

        # 4. [Optionally], display an interactive screen where the user can choose which packages to upgrade
        selected_packages = InteractivePackageSelector(packages_status_map, options).get_packages()

        # 5. With the list of packages, perform the actual upgrade and replace the version inside all filenames
        upgraded_packages = PackageUpgrader(selected_packages, filenames, options).do_upgrade()

        print(Color('{{autogreen}}Successfully upgraded (and updated requirements) for the following packages: '
                    '{}{{/autogreen}}'.format(','.join([package['name'] for package in upgraded_packages]))))
        if options['--dry-run']:
            print(Color('{automagenta}Actually, no, because this was a simulation using --dry-run{/automagenta}'))

    except KeyboardInterrupt:
        print(Color('\n{autored}Upgrade interrupted.{/autored}'))


if __name__ == '__main__':
    main()
