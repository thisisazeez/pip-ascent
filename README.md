A versatile tool for effortlessly updating pip requirements while keeping your requirements.txt file in sync with the latest package versions. No more tedious manual package-by-package upgrades; this tool handles it for you and updates your requirements.txt file accordingly.

## Purpose

This command-line tool allows you to interactively (or non-interactively) upgrade packages from your requirements file. It also enables you to update the pinned version in your requirements file(s). If no requirements are specified, the tool will attempt to detect the requirements file(s) in the current directory.

## Installation

```bash
pip install pip-ascent
```

**Note:** This package installs the following dependencies: `'docopt', 'packaging', 'requests', 'terminaltables', 'colorclass'`. To avoid installing these dependencies in your project, you can install `pip-ascent` in your system rather than your virtual environment. If you install it in your system and need to upgrade it, run `pip install -U pip-ascent`.

## Usage

```bash
pip-ascent [<requirements_file>] ... [--prerelease] [-pk=<package>...] [--dry-run] [--check-greater-equal] [--skip-virtualenv-check] [--skip-package-installation] [--use-default-index]
```

**Activate your virtual environment** (important because it will also install the new versions of upgraded packages in the current virtual environment).

**Change directory into your project.** Then:

```bash
$ pip-ascent
```

Arguments:

- `requirements_file`: Specifies the requirement file or uses a wildcard path to multiple files.
- `--prerelease`: Includes prerelease versions for upgrades when querying PyPI repositories.
- `-pk <package>`: Pre-selects packages for an upgrade, bypassing any prompts. You can also utilize regular expressions to filter packages for upgrading.
- `--dry-run`: Simulates the upgrade but does not perform the actual upgrade.
- `--check-greater-equal`: Also checks packages with minimum version pinning (package>=version).
- `--skip-package-installation`: Upgrades the version in requirement files only; it does not install the new package.
- `--skip-virtualenv-check`: Disables virtual environment check, permitting the installation of new packages outside the virtual environment.
- `--use-default-index`: Skips searching for a custom index URL in pip configuration file(s).

Examples:

```bash
pip-ascent             # Automatically discovers the requirements file
pip-ascent requirements.txt
pip-ascent requirements/dev.txt requirements/production.txt
pip-ascent requirements.txt -pk django -p celery
pip-ascent requirements.txt -pk all
pip-ascent requirements.txt --dry-run  # Runs everything as a simulation (does not perform the actual upgrade)
```

## 💖 Like this project?

Leave a ⭐ if you find this project cool.

[Share with the world](https://twitter.com/intent/tweet?url=https%3A%2F%2Fgithub.com%thisisazeez%2Fpip-ascent&via=sifusherif&text=Check%20out%20this%20awesome%20pip-ascent%20tool%20for%20easily%20upgrading%20your%20pip%20requirements%20and%20keeping%20your%20requirements.txt%20file%20in%20sync%20with%20the%20latest%20package%20versions%21%20%F0%9F%9A%80%20%23Python%20%23Pip%20%23PackageManagement%20%23DevelopmentTools%20%23OpenSource%20%23DevOps%20%23Coding%20%23Programming%20%23Tech%20%23CLI%20%23DeveloperTools%20%23Upgrade&hashtags=python%2Cpip%2Crequirements%2Cdevtools%2Copensource%2Cdevops%2Ccoding%2Cprogramming%2Ctech%2Ccli%2Cdevtools%2Cupgrade) ✨

## 👨‍💻 Author

### Abdulazeez Sherif

[Twitter](https://twitter.com/sifusherif "Abdulazeez Sherif")

## 🍁 License

**MIT**