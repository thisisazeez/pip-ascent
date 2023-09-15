import os
import re
import requests
import sys

from configparser import ConfigParser, NoOptionError, NoSectionError
from urllib.parse import urljoin

from colorclass import Color
from packaging import version
from packaging.utils import canonicalize_name
from requests import HTTPError

# Try to import site_config_files from pip locations; if not available, set it to None
try:
    from pip.locations import site_config_files
except ImportError:
    try:
        from pip._internal.locations import site_config_files
    except ImportError:  # Coverage testing pragma: this branch is for exception handling
        site_config_files = None

class PackageStatusDetector(object):
    # Initialize class variables
    packages = []
    packages_status_map = {}
    PYPI_API_URL = None
    PYPI_API_TYPE = None
    pip_config_locations = [
        '~/.pip/pip.conf',
        '~/.pip/pip.ini',
        '~/.config/pip/pip.conf',
        '~/.config/pip/pip.ini',
    ]

    check_gte = False
    _prerelease = False

    def __init__(self, packages, options):
        # Initialize instance variables
        self.packages = packages
        self.packages_status_map = {}
        self.PYPI_API_URL = 'https://pypi.python.org/pypi/{package}/json'
        self.PYPI_API_TYPE = 'pypi_json'

        # Check if the '--use-default-index' option is not set and update the index URL from configurations
        if not options.get('--use-default-index'):
            self._update_index_url_from_configs()

        self.check_gte = options['--check-greater-equal']
        self._prerelease = False

    def _update_index_url_from_configs(self):
        """ Checks for an alternative index-url in pip configuration files """
        
        # Check if VIRTUAL_ENV is set in the environment variables and add its configuration files
        if 'VIRTUAL_ENV' in os.environ:
            self.pip_config_locations.append(os.path.join(os.environ['VIRTUAL_ENV'], 'pip.conf'))
            self.pip_config_locations.append(os.path.join(os.environ['VIRTUAL_ENV'], 'pip.ini'))

        # Extend the pip_config_locations with site-specific configuration files
        if site_config_files:
            self.pip_config_locations.extend(site_config_files)

        index_url = None
        custom_config = None

        # Check if PIP_INDEX_URL is set in the environment variables and prioritize it
        if 'PIP_INDEX_URL' in os.environ and os.environ['PIP_INDEX_URL']:
            index_url = os.environ['PIP_INDEX_URL']
            custom_config = 'PIP_INDEX_URL environment variable'
        else:
            # Iterate through pip configuration files to find 'index-url' setting
            for pip_config_filename in self.pip_config_locations:
                if pip_config_filename.startswith('~'):
                    pip_config_filename = os.path.expanduser(pip_config_filename)

                if os.path.isfile(pip_config_filename):
                    config = ConfigParser()
                    config.read([pip_config_filename])
                    try:
                        index_url = config.get('global', 'index-url')
                        custom_config = pip_config_filename
                        break  # Stop on first detected, as config locations have priority
                    except (NoOptionError, NoSectionError):  # Coverage testing pragma: handling potential errors
                        pass

        if index_url:
            self.PYPI_API_URL = self._prepare_api_url(index_url)
            print(Color('Setting API url to {{autoyellow}}{}{{/autoyellow}} as found in {{autoyellow}}{}{{/autoyellow}}'
                        '. Use --default-index-url to use PyPI default index'.format(self.PYPI_API_URL, custom_config)))

    def _prepare_api_url(self, index_url):
        """ Prepares the API URL based on the index URL """
        if not index_url.endswith('/'):
            index_url += '/'

        if index_url.endswith('/simple/'):
            self.PYPI_API_TYPE = 'simple_html'
            return urljoin(index_url, '{package}/')

        if index_url.endswith('/+simple/'):
            self.PYPI_API_TYPE = 'simple_html'
            return urljoin(index_url, '{package}/')

        if '/pypi/' in index_url:
            base_url = index_url.split('/pypi/')[0]
            return urljoin(base_url, '/pypi/{package}/json')

        return urljoin(index_url, '/pypi/{package}/json')


   def detect_available_upgrades(self, options):
    # Set the 'prerelease' flag based on the '--prerelease' option
    self._prerelease = options.get('--prerelease', False)

    # Initialize variable for explicitly selected packages in lowercase
    explicit_packages_lower = None
    if options['-p'] and options['-p'] != ['all']:
        explicit_packages_lower = [pack_name.lower() for pack_name in options['-p']]

    # Iterate through packages for upgrade detection
    for i, package in enumerate(self.packages):
        try:
            # Extract package name and pinned version
            package_name, pinned_version = self._expand_package(package)

            # Skip if package_name or pinned_version is missing
            if not package_name or not pinned_version:
                continue

            # Check if package_name should be explicitly upgraded
            if explicit_packages_lower and package_name.lower() not in explicit_packages_lower:
                found = False
                for option_package in explicit_packages_lower:
                    if re.search(option_package, package_name.lower()):
                        found = True
                if not found:
                    # Skip if explicit and not chosen
                    continue

            current_version = version.parse(pinned_version)

            if pinned_version and isinstance(current_version, version.Version):
                # Fetch package status and reason
                package_status, reason = self._fetch_index_package_info(package_name, current_version)
                if not package_status:
                    print(package, reason)
                    continue

                print('{}/{}: {} ... '.format(i + 1, len(self.packages), package_name), end='')
                sys.stdout.flush()

                # Compare versions and print upgrade information
                if current_version < package_status['latest_version']:
                    print('upgrade available: {} ==> {} (uploaded on {})'.format(current_version,
                                                                                 package_status['latest_version'],
                                                                                 package_status['upload_time']))
                else:
                    print('up to date: {}'.format(current_version))
                sys.stdout.flush()

                self.packages_status_map[package_name] = package_status
        except Exception as e:
            print('Error while parsing package {} (skipping). \nException: '.format(package), e)

    return self.packages_status_map

def _fetch_index_package_info(self, package_name, current_version):
    """
    :type package_name: str
    :type current_version: version.Version
    """

    try:
        package_canonical_name = package_name
        if self.PYPI_API_TYPE == 'simple_html':
            package_canonical_name = canonicalize_name(package_name)
        response = requests.get(self.PYPI_API_URL.format(package=package_canonical_name), timeout=15)
    except HTTPError as e:
        return False, e.message

    if not response.ok:
        return False, 'API error: {}'.format(response.reason)

    if self.PYPI_API_TYPE == 'pypi_json':
        return self._parse_pypi_json_package_info(package_name, current_version, response)
    elif self.PYPI_API_TYPE == 'simple_html':
        return self._parse_simple_html_package_info(package_name, current_version, response)
    else:
        raise NotImplementedError('This type of PYPI_API_TYPE is not supported')

def _expand_package(self, package_line):
    # Define pin types to check
    pin_types = ['==', '>='] if self.check_gte else ['==']

    for pin_type in pin_types:
        if pin_type in package_line:
            name, vers = package_line.split(pin_type)

            if '[' in name and name.strip().endswith(']'):
                name = name.split('[')[0]

            return name, vers

    return None, None

def _parse_pypi_json_package_info(self, package_name, current_version, response):
    """
    :type package_name: str
    :type current_version: version.Version
    :type response: requests.models.Response
    """

    data = response.json()
    all_versions = [version.parse(vers) for vers in data['releases'].keys()]
    if not self._prerelease:
        filtered_versions = [vers for vers in all_versions if not vers.is_prerelease and not vers.is_postrelease]
    else:
        filtered_versions = all_versions

    if not filtered_versions:
        return False, 'error while parsing version'

    latest_version = max(filtered_versions)

    # Even if the user did not choose prerelease, if the package from requirements is pre/post release, use it
    if self._prerelease or current_version.is_postrelease or current_version.is_prerelease:
        prerelease_versions = [vers for vers in all_versions if vers.is_prerelease or vers.is_postrelease]
        if prerelease_versions:
            if max(prerelease_versions) > latest_version:
                latest_version = max(prerelease_versions)
    try:
        try:
            latest_version_info = data['releases'][str(latest_version)][0]
        except KeyError:
            # Non-RFC versions, get the latest from pypi response
            latest_version = version.parse(data['info']['version'])
            latest_version_info = data['releases'][str(latest_version)][0]
    except Exception:
        return False, 'error while parsing version'

    upload_time = latest_version_info['upload_time'].replace('T', ' ')

    return {
        'name': package_name,
        'current_version': current_version,
        'latest_version': latest_version,
        'upgrade_available': current_version < latest_version,
        'upload_time': upload_time
    }, 'success'

def _parse_simple_html_package_info(self, package_name, current_version, response):
    """
    :type package_name: str
    :type current_version: version.Version
    :type response: requests.models.Response
    """
    pattern = r'<a.*>.*{name}-([A-z0-9\.-]*)(?:-py|\.tar).*<\/a>'.format(name=re.escape(package_name))
    versions_match = re.findall(pattern, response.content.decode('utf-8'), flags=re.IGNORECASE)

    all_versions = [version.parse(vers) for vers in versions_match]
    filtered_versions = [vers for vers in all_versions if not vers.is_prerelease and not vers.is_postrelease]

    if not filtered_versions:
        return False, 'error while parsing version'

    latest_version = max(filtered_versions)

    # Even if the user did not choose prerelease, if the package from requirements is pre/post release, use it
    if self._prerelease or current_version.is_postrelease or current_version.is_prerelease:
        prerelease_versions = [vers for vers in all_versions if vers.is_prerelease or vers.is_postrelease]
        if prerelease_versions:
            latest_version = max(prerelease_versions)

    return {
       'name': package_name,
       'current_version': current_version,
       'latest_version': latest_version,
       'upgrade_available': current_version < latest_version,
       'upload_time': '-'
    }, 'success'
