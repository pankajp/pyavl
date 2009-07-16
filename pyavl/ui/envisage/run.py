""" Run the Lorenz example application. """


# Standard library imports.
import logging

# pyavl imports
from pyavl.ui.envisage.avl_plugin import AVLPlugin
from pyavl.ui.envisage.avl_ui_plugin import AVLUIPlugin
from pyavl.ui.envisage.output_plugin import AVLOutputPlugin
from pyavl.ui.envisage.application import PyAVLApplication


# Enthought plugins.
from enthought.envisage.core_plugin import CorePlugin
from enthought.envisage.ui.workbench.workbench_plugin import WorkbenchPlugin

from enthought.envisage.developer.ui.developer_ui_plugin import DeveloperUIPlugin

use_ipython_plugin = True

if use_ipython_plugin:
    from enthought.plugins.ipython_shell.ipython_shell_plugin import IPythonShellPlugin
    PythonShellPlugin = IPythonShellPlugin
else:
    from enthought.plugins.python_shell.python_shell_plugin import PythonShellPlugin

from enthought.plugins.text_editor.text_editor_plugin import TextEditorPlugin
from enthought.logger.plugin.logger_plugin import LoggerPlugin

from enthought.chaco.plugin.chaco_plugin import ChacoPlugin


# Do whatever you want to do with log messages! Here we create a log file.
logger = logging.getLogger()
#logger.addHandler(logging.StreamHandler(file('lorenz.log', 'w')))
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def main():
    """ Run the application. """

    # Create an application with the specified plugins.
    application = PyAVLApplication(
        plugins=[
            CorePlugin(), WorkbenchPlugin(),
            AVLPlugin(),
            AVLUIPlugin(),
            LoggerPlugin(),
            PythonShellPlugin(),
            TextEditorPlugin(),
            ChacoPlugin(),
            
            DeveloperUIPlugin(),
            
            AVLOutputPlugin(),
        ]
    )

    # Run it! This starts the application, starts the GUI event loop, and when
    # that terminates, stops the application.
    application.run()

    return


if __name__ == '__main__':
    main()

#### EOF ######################################################################
