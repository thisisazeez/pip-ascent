import re
from collections import OrderedDict

from colorclass import Color
from terminaltables import AsciiTable


def user_input(prompt=None):  # pragma: nocover
    try:
        input_func = raw_input
    except NameError:
        input_func = input
    return input_func(prompt)


class InteractivePackageSelector(object):
    packages_for_upgrade = OrderedDict()
    selected_packages = []

    def __init__(self, packages_map, options):
        self.selected_packages = []
        self.packages_for_upgrade = {}

        # Create a map with index numbers for later selection
        i = 1
        for package in packages_map.values():
            if package['upgrade_available']:
                self.packages_for_upgrade[i] = package.copy()
                i += 1

        # Check if all packages are up-to-date
        if not self.packages_for_upgrade:
            print(Color('{autogreen}All packages are up-to-date.{/autogreen}'))
            raise KeyboardInterrupt()

        # Choose which packages to upgrade (interactive or not)
        if '-p' in options and options['-p']:
            if options['-p'] == ['all']:
                self._select_packages(self.packages_for_upgrade.keys())
            else:
                for index, package in self.packages_for_upgrade.items():
                    for chosen_package in options['-p']:
                        if chosen_package.lower().strip() == package['name'].lower().strip():
                            self._select_packages([index])
                        else:
                            # Check with regex if no match
                            if re.search(chosen_package, package['name'].lower().strip()):
                                self._select_packages([index])
        else:
            self.ask_for_packages()

    def get_packages(self):
        return self.selected_packages

    def ask_for_packages(self):
        data = [[
            Color('{autoblue}No.{/autoblue}'),
            Color('{autoblue}Package{/autoblue}'),
            Color('{autoblue}Current version{/autoblue}'),
            Color('{autoblue}Latest version{/autoblue}'),
            Color('{autoblue}Release date{/autoblue}'),
        ]]

        for i, package in self.packages_for_upgrade.items():
            data.append([Color('{{autobgblack}}{{autogreen}} {} {{/autogreen}}{{/bgblack}}'.format(i)),
                         Color('{{autogreen}} {} {{/autogreen}}'.format(package['name'])),
                         package['current_version'],
                         package['latest_version'],
                         package['upload_time']])

        print('')
        print(Color('{autogreen}Available upgrades:{/autogreen}'))
        table = AsciiTable(data)
        print(table.table)
        print('')

        print(
            'Please choose which packages should be upgraded. '
            'Choices: "all -1 -2 -3", "q" (quit), "x" (exit) or "1 2 3"'
        )
        choice = user_input('Choice: ').strip()

        if not choice and not choice.strip():
            print(Color('{autored}No choice selected.{/autored}'))
            raise KeyboardInterrupt()

        choice = choice.strip()

        if choice == 'q':  # pragma: nocover
            print(Color('{autored}Quit.{/autored}'))
            raise KeyboardInterrupt()

        if choice == 'x':  # pragma: nocover
            print(Color('{autored}Exit.{/autored}'))
            raise KeyboardInterrupt()

        try:
            include = []

            if choice.startswith("all"):
                # Create an iterator on stripped choices
                exclude_it = map(str.strip, choice[3:].split(" "))
                # Filter out empty strings and create a set of excluded indices
                exclude = frozenset(map(int, filter(len, exclude_it)))

                # Include packages with keys not in the excluded set
                include = [
                    i for i in self.packages_for_upgrade.keys()
                    if -i not in exclude
                ]

            else:
                include = [int(index.strip()) for index in choice.split(' ')]

            selected = list(self._select_packages(include))

            if not any(selected):
                print(Color('{autored}No valid choice selected.{/autored}'))
                raise KeyboardInterrupt()

        except ValueError:  # pragma: nocover
            print(Color('{autored}Invalid choice{/autored}'))
            raise KeyboardInterrupt()

    def _select_packages(self, indexes):
        selected = []

        for index in indexes:
            if index in self.packages_for_upgrade:
                self.selected_packages.append(self.packages_for_upgrade[index].copy())
                selected.append(True)

        return selected
