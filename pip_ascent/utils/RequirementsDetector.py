import mimetypes
import os


class RequirementsDetector(object):
    """
    This class is responsible for detecting and discovering all the requirements files.
    """

    filenames = []

    def __init__(self, requirements_arg):
        """
        Initializes the RequirementsDetector instance.

        :param requirements_arg: List of raw requirements arguments.
        """
        self.filenames = []

        if not requirements_arg:
            self.autodetect_files()
        else:
            self.detect_files(requirements_arg)

    def get_filenames(self):
        """
        Returns a list of all filenames detected as proper requirements files.

        :return: A list of filenames.
        """
        return self.filenames

    def detect_files(self, requirements_arg):
        """
        Detects and adds valid requirements files to the filenames list.

        :param requirements_arg: List of raw requirements arguments.
        """
        for argument in requirements_arg:
            if self._is_valid_requirements_file(argument):
                self.filenames.append(argument)
            else:
                print('Invalid requirements file: {}'.format(argument))
        self._check_inclusions_recursively()

    def autodetect_files(self):
        """ Attempt to detect requirements files in the current working directory """
        if self._is_valid_requirements_file('requirements.txt'):
            self.filenames.append('requirements.txt')

        if self._is_valid_requirements_file('requirements.pip'):
            self.filenames.append('requirements.pip')

        if os.path.isdir('requirements'):
            for filename in os.listdir('requirements'):
                file_path = os.path.join('requirements', filename)
                if self._is_valid_requirements_file(file_path):
                    self.filenames.append(file_path)
        self._check_inclusions_recursively()

    @staticmethod
    def _is_valid_requirements_file(filename):
        """
        Check if a filename is a valid requirements file.

        :param filename: The name of the file to check.
        :return: True if the file is valid, otherwise False.
        """
        extension_ok = filename.endswith('txt') or filename.endswith('pip')
        return extension_ok and os.path.isfile(filename) and mimetypes.guess_type(filename)[0] in ['text/plain', None]

    def _check_inclusions_recursively(self):
        for filename in self.filenames:
            self._detect_inclusion(filename)

    def _detect_inclusion(self, filename):
        with open(filename) as fh:
            for line in fh:
                if line.strip().startswith('-r '):
                    included_filename = line.split('-r ')[1].strip()
                    included_filename = os.path.join(os.path.dirname(filename), included_filename)
                    if self._is_valid_requirements_file(included_filename) and included_filename not in self.filenames:
                        self.filenames.append(included_filename)
                        # Recursively, check if the included file contains other inclusions
                        self._detect_inclusion(included_filename)
