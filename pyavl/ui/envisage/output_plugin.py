'''
Created on Jul 11, 2009

@author: pankaj

The avl output viewer plugin
'''


# Enthought library imports.
from enthought.envisage.api import Plugin
from enthought.pyface.workbench.api import Perspective, PerspectiveItem
from enthought.pyface.workbench.api import TraitsUIView
from enthought.traits.api import List, Any, Instance, on_trait_change
#from pyavl.avl import AVL
from pyavl.geometry import Section

import logging
# Logging.
logger = logging.getLogger(__name__)


class AVLOutputPerspective(Perspective):
    """ A perspective containing the default AVL output views. """
    
    name = 'PyAVL output'
    show_editor_area = False

    contents = [
        PerspectiveItem(id='pyavl.output_plot'),
        PerspectiveItem(id='pyavl.output_variables'),
        PerspectiveItem(id='pyavl.output_system'),
        #PerspectiveItem(id='lorenz.plot2d')
    ]


class AVLOutputPlugin(Plugin):
    """ The AVL Output plugin.

    This plugin is part of the 'pyAVL' application.

    """

    # Extension points Ids.
    PERSPECTIVES = 'enthought.envisage.ui.workbench.perspectives'
    VIEWS = 'enthought.envisage.ui.workbench.views'

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = 'pyavl.ui.envisage.ui.output'

    # The plugin's name (suitable for displaying to the user).
    name = 'PyAVL Output UI'

    #### Contributions to extension points made by this plugin ################

    # Perspectives.
    perspectives = List(contributes_to=PERSPECTIVES)

    def _perspectives_default(self):
        """ Trait initializer. """

        return [AVLOutputPerspective]

    # Views.
    views = List(contributes_to=VIEWS)

    def _views_default(self):
        """ Trait initializer. """
        
        return [self._create_output_plot_view, self._create_output_variables_view, self._create_output_system_view]#, self._create_plot2d_view]
    
    runoutput = Any()
    
    def _runoutput_default(self):
        ret = self.application.get_service('pyavl.avl.AVL').run_cases[0].runoutput
        logger.info('in _runoutput_default : '+str(ret))
        return ret
    
    output_plot_view = Any()
    output_variables_view = Any()
    output_system_view = Any()
    
    def _output_plot_view_default(self):
        from pyavl.ui.output_viewer import OutputPlotViewer
        obj = OutputPlotViewer(runoutput=self.runoutput)
        plot_view = TraitsUIView(
            id='pyavl.output_plot',
            name='Output Plot View',
            obj=obj
        )
        return plot_view
    
    #@on_trait_change('avl.case.geometry')
    #def update_geometry_view(self):
    #    self.geometry_view.obj.geometry = self.avl.case.geometry
    
    def _output_variables_view_default(self):
        from pyavl.ui.output_viewer import OutputVariablesViewer
        output_variables_view = TraitsUIView(
            id='pyavl.output_variables',
            name='Output Variables View',
            obj=OutputVariablesViewer(runoutput=self.runoutput)
        )
        return output_variables_view
    
    @on_trait_change('avl.case.geometry')
    def update_geometry_view(self):
        self.geometry_view.obj.geometry = self.avl.case.geometry
    
    def _output_system_view_default(self):
        from pyavl.ui.output_viewer import OutputSystemViewer
        output_system_view = TraitsUIView(
            id='pyavl.output_system',
            name='Output System View',
            obj=OutputSystemViewer(runoutput=self.runoutput)
        )
        return output_system_view
    
    @on_trait_change('tree_view.obj.selected')
    def update_section_view(self):
        selected = self.tree_view.obj.selected.object
        logger.info('in update_section_view :' + str(selected))
        if isinstance(selected, Section):
            logger.info('updating view')
            self.section_view.obj.section = selected
    
    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_output_plot_view(self, **traits):
        """ Factory method for the output view. """
        return self.output_plot_view
    
    def _create_output_variables_view(self, **traits):
        return self.output_variables_view
    
    
    def _create_output_system_view(self, **traits):
        return self.output_system_view
    
    
#### EOF ######################################################################

