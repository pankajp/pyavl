'''
Created on Jul 1, 2009

@author: pankaj
'''

from logging import DEBUG

# Enthought library imports.
from enthought.envisage.ui.workbench.api import WorkbenchApplication
from enthought.pyface.api import AboutDialog, ImageResource, SplashScreen

class PyAVLApplication(WorkbenchApplication):
    id = 'pyavl.ui.envisage'
    icon = ImageResource('pyAVL.ico')
    name = 'pyAVL'
    
    ###########################################################################
    # 'WorkbenchApplication' interface.
    ###########################################################################

    def _about_dialog_default(self):
        """ Trait initializer. """

        about_dialog = AboutDialog(
            parent = self.workbench.active_window.control,
            image  = ImageResource('about')
        )
    
        return about_dialog
    
    def _splash_screen_default(self):
        """ Trait initializer. """

        splash_screen = SplashScreen(
            image             = ImageResource('splash'),
            show_log_messages = True,
            log_level         = DEBUG
        )
        
        return splash_screen
    
#### EOF ######################################################################
