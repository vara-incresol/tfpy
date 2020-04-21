from pathlib import Path

import yaml


class StackVars:
    def __init__(self, stack, environment="", var_dir="."):
        """."""
        self.stack = stack
        self.environment = environment
        self.var_dir = Path(var_dir) / "vars"
        self.vars = {}

    def list_variable_files(self):
        """List the variable files that have been detected for the stack."""
        # Load the common variables.
        var_files = list(self.var_dir.glob("all/*.yml"))

        # Load the common stack variables.
        s = self.var_dir / "all" / self.stack
        var_files += list(s.glob("*.yml"))

        # Load the stack environment specific variables if any.
        if self.environment:
            e = self.var_dir / self.environment / self.stack
            if not e.exists():
                raise ValueError(
                    f'cannot find variables for the stack "{self.stack}" in the "{self.environment}" environment'
                )
            var_files += list(e.glob("**/*.yml"))

        return var_files

    def load(self):
        """Load the stack variables."""
        files = self.list_variable_files()
        d = {}
        for f in files:
            d = {**d, **yaml.safe_load(f.read_text())}
        self.vars = d

    def get(self, var, default=None, silent_fail=True, separator="."):
        """
        Retrieves a value matching a key in the config file.

        :param var: the var to look for
        :param default: the default value to return if the key is not found
        :param silent_fail: if true, returns the default value if the key is not found, otherwise raises an exception
        :return: the value matching the key
        """
        # Ensure we have a configuration.
        if not self.vars:
            raise ValueError("no variable files were loaded")

        # Split the keys.
        key_list = var.split(separator)

        # Create a copy of the configuration to iterate through it.
        d = self.vars

        for dict_key in key_list:
            # Retrieve the value of the key in the configuration file.
            value = d.get(dict_key)

            # Keep iterating if there is value.
            if value:
                d = value
            else:
                break

        # Return the value matching the key if we found it.
        if value:
            return value

        # Otherwise return the default value.
        if silent_fail:
            return default

        # Or raise an exception.
        raise ValueError(f"variable {var} not found.")
