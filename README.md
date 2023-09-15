A dynamic tool for upgrading pip requirements that seamlessly synchronizes
 the version changes within your requirements.txt file. Because upgrading
requirements, package by package, is a pain in the ass. It also updates
the version in your requirements.txt file.

## Purpose

This cli tools helps you interactively(or not) upgrade packages from
requirements file, and also **update the pinned version from
requirements file(s)**.

If no requirements are given, the command **attempts to detect the
requirements file(s)** in the current directory.

## Installation

    pip install pip-ascent

**Note:** this packages installs the following requirements: `'docopt',
'packaging', 'requests', 'terminaltables', 'colorclass'`

To avoid installing all these dependencies in your project, you can
install `pip-ascent` in your system, rather than your virtualenv. If
you install it in your system, and need to upgrade it, run `pip install
-U pip-ascent`

## Usage

    pip-ascent [<requirements_file>] ... [--prerelease] [-pk=<package>...] [--dry-run] [--check-greater-equal] [--skip-virtualenv-check] [--skip-package-installation] [--use-default-index]

**Activate your virtualenv** (important, because it will also install
the new versions of upgraded packages in current virtualenv)

**CD into your project.** Then: :

    $ pip-ascent

Arguments: :

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