""" Run the Lorenz example application. """


# Standard library imports.
import logging

# Enthought plugins.
from enthought.envisage.core_plugin import CorePlugin
from enthought.envisage.ui.workbench.workbench_plugin import WorkbenchPlugin


from enthought.envisage.developer.ui.developer_ui_plugin import DeveloperUIPlugin

from enthought.plugins.ipython_shell.ipython_shell_plugin import IPythonShellPlugin
PythonShellPlugin = IPythonShellPlugin
#from enthought.plugins.python_shell.python_shell_plugin import PythonShellPlugin

from enthought.plugins.text_editor.text_editor_plugin import TextEditorPlugin
from enthought.logger.plugin.logger_plugin import LoggerPlugin

from enthought.chaco.plugin.chaco_plugin import ChacoPlugin

# Example imports.
from pyavl.ui.envisage.sample.lorenz_application import LorenzApplication
from pyavl.ui.envisage.sample.lorenz_plugin import LorenzPlugin
from pyavl.ui.envisage.sample.lorenz_ui_plugin import LorenzUIPlugin


# Do whatever you want to do with log messages! Here we create a log file.
logger = logging.getLogger()
#logger.addHandler(logging.StreamHandler(file('lorenz.log', 'w')))
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def main():
    """ Run the application. """

    # Create an application with the specified plugins.
    lorenz_application = LorenzApplication(
        plugins=[
            CorePlugin(), WorkbenchPlugin(),
            LorenzPlugin(),
            LorenzUIPlugin(),
            LoggerPlugin(),
            PythonShellPlugin(),
            TextEditorPlugin(),
            ChacoPlugin(),
            
            DeveloperUIPlugin()
        ]
    )

    # Run it! This starts the application, starts the GUI event loop, and when
    # that terminates, stops the application.
    lorenz_application.run()

    return


if __name__ == '__main__':
    main()

#### EOF ######################################################################
