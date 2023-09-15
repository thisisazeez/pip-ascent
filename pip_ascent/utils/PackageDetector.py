class PackageDetector(object):
    """ 
    This class takes a list of requirements files and returns the list of packages from all of them.
    """

    packages = []

    def __init__(self, requirements_files):
        """
        Initializes the PackageDetector instance.

        :param requirements_files: A list of requirement file names.
        """
        self.packages = []
        self.detect_packages(requirements_files)

    def get_packages(self):
        """
        Get the list of packages detected from the requirements files.

        :return: List of package names.
        """
        return self.packages

    def detect_packages(self, requirements_files):
        """
        Detect packages from the given requirements files.

        :param requirements_files: A list of requirement file names.
        """
        for filename in requirements_files:
            with open(filename) as fh:
                for line in fh:
                    self._process_req_line(line)

    def _process_req_line(self, line):
        """
        Process a line from a requirements file and extract package names.

        :param line: A line from a requirements file.
        """
        if not line or not line.strip():
            return
        line = line.strip()

        if line.startswith('#'):
            return

        if line.startswith('-f') or line.startswith('--find-links') or \
                line.startswith('-i') or line.startswith('--index-url') or \
                line.startswith('--extra-index-url') or \
                line.startswith('--no-index') or \
                line.startswith('-r') or \
                line.startswith('-Z') or line.startswith('--always-unzip'):
            # Private repositories or special flags
            return

        if '#' in line:  # Inline comment in file
            line = line.split('#')[0].strip()

        self.packages.append(line)
