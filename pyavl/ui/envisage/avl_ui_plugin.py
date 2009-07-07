'''
Created on Jul 2, 2009

@author: pankaj

The pyAVL UI plugin.
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


class AVLPerspective(Perspective):
    """ A perspective containing the default Lorenz views. """
    
    name = 'PyAVL'
    show_editor_area = False

    contents = [
        PerspectiveItem(id='pyavl.tree'),
        #PerspectiveItem(id='lorenz.plot2d')
    ]


class AVLUIPlugin(Plugin):
    """ The AVL UI plugin.

    This plugin is part of the 'pyAVL' application.

    """

    # Extension points Ids.
    PERSPECTIVES = 'enthought.envisage.ui.workbench.perspectives'
    VIEWS = 'enthought.envisage.ui.workbench.views'

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = 'pyavl.ui.envisage.ui'

    # The plugin's name (suitable for displaying to the user).
    name = 'PyAVL UI'

    #### Contributions to extension points made by this plugin ################

    # Perspectives.
    perspectives = List(contributes_to=PERSPECTIVES)

    def _perspectives_default(self):
        """ Trait initializer. """

        return [AVLPerspective]

    # Views.
    views = List(contributes_to=VIEWS)

    def _views_default(self):
        """ Trait initializer. """
        
        return [self._create_tree_view, self._create_geometry_view, self._create_section_view]#, self._create_plot2d_view]
    
    avl = Any()
    
    def _avl_default(self):
        return self.application.get_service('pyavl.avl.AVL')
    
    tree_view = Any()
    geometry_view = Any()
    section_view = Any()
    
    def _tree_view_default(self):
        from pyavl.ui.envisage.treepipeline import AVLTreeBrowser
        from pyavl.ui.envisage.avl_tree_ui_view import AVLTreeUIView
        obj = AVLTreeBrowser(avl=self.avl)
        tree_view = AVLTreeUIView(
            id='pyavl.tree',
            name='Tree View',
            view=obj.view,
            obj=obj
        )
        return tree_view
    
    #@on_trait_change('avl.case.geometry')
    #def update_geometry_view(self):
    #    self.geometry_view.obj.geometry = self.avl.case.geometry
    
    def _geometry_view_default(self):
        from pyavl.ui.geometry_viewer import GeometryViewer
        geometry_view = TraitsUIView(
            id='pyavl.geometry',
            name='Geometry View',
            obj=GeometryViewer(geometry=self.avl.case.geometry)
        )
        return geometry_view
    
    @on_trait_change('avl.case.geometry')
    def update_geometry_view(self):
        self.geometry_view.obj.geometry = self.avl.case.geometry
    
    def _section_view_default(self):
        from pyavl.ui.section_viewer import SectionViewer
        section_view = TraitsUIView(
            id='pyavl.section',
            name='Section View',
            obj=SectionViewer(section=None)
        )
        return section_view
    
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

    def _create_tree_view(self, **traits):
        """ Factory method for the data view. """
        return self.tree_view
    
    def _create_geometry_view(self, **traits):
        return self.geometry_view
    
    
    def _create_section_view(self, **traits):
        return self.section_view
    
    
#### EOF ######################################################################



