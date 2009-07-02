'''
Created on Jul 2, 2009

@author: pankaj

The pyAVL UI plugin.
'''


# Enthought library imports.
from enthought.envisage.api import Plugin
from enthought.pyface.workbench.api import Perspective, PerspectiveItem
from enthought.pyface.workbench.api import TraitsUIView
from enthought.traits.api import List


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

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_tree_view(self, **traits):
        """ Factory method for the data view. """

        from pyavl.ui.envisage.treepipeline import AVLTreeBrowser
        from pyavl.ui.envisage.avl_tree_ui_view import AVLTreeUIView
        #from pyavl.ui.envisage.treepipeline import AVLTreeBrowserView
        obj = AVLTreeBrowser(avl=self.application.get_service('pyavl.avl.AVL'))
        tree_view = AVLTreeUIView(
            id='pyavl.tree',
            name='Tree View',
            view=obj.view,
            obj=obj,
            **traits
        )

        return tree_view
    
    def _create_geometry_view(self, **traits):
        from pyavl.ui.geometry_viewer import GeometryViewer
        geometry_view = TraitsUIView(
            id='pyavl.geometry',
            name='Geometry View',
            obj=GeometryViewer(geometry=self.application.get_service('pyavl.avl.AVL').case.geometry),
            **traits
        )

        return geometry_view
    
    
    def _create_section_view(self, **traits):
        from pyavl.ui.section_viewer import SectionViewer
        section_view = TraitsUIView(
            id='pyavl.section',
            name='Section View',
            obj=SectionViewer(section=None),
            **traits
        )

        return section_view
    
    
#### EOF ######################################################################



