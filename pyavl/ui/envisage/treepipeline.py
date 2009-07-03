'''
Created on Jul 1, 2009

@author: pankaj
'''

# Idea + major component of code taken from below signed
 
# Author: Prabhu Ramachandran <prabhu_r@users.sf.net>
# Copyright (c) 2005, Enthought, Inc.
# License: BSD Style.

# Standard library imports.
import re

import logging
# Logging.
logger = logging.getLogger(__name__)


from pyavl.avl import AVL, RunCase
from pyavl.case import Case
from pyavl.geometry import Geometry, Surface, Section, Body

# Enthought library imports.
from enthought.traits.api import HasTraits, Property, Any, Float, Instance, \
                             Trait, List, Str, Dict, Python
from enthought.traits.ui.api import \
     TreeEditor, TreeNodeObject, ObjectTreeNode, View, Item, Group, UI
from enthought.traits.ui.menu import Menu, Action

from enthought.tvtk.api import tvtk
from enthought.tvtk import messenger
from enthought.tvtk.tvtk_base import TVTKBase
from enthought.tvtk.tvtk_base_handler import TVTKBaseHandler
from enthought.tvtk.common import camel2enthought


######################################################################
# Utility functions.
######################################################################
def is_iterable(x):
    return hasattr(x, '__iter__')


def get_icon(object_name):
    """Given the name of the object, this function returns an
    appropriate icon image name.  If no icon is appropriate it returns
    the empty string."""

    # The mapping from names to icons.
    icon_map = {'actor': 'actor.png',
                'camera': 'camera.png',
                'coordinate': 'coordinate.png',
                'filter': 'filter.png',
                'lookuptable': 'lookuptable.png',
                'mapper': 'mapper.png',
                'polydata': 'polydata.png',
                'property': 'property.png',
                'reader': 'reader.png',
                'renderer': 'renderer.png',
                'rendererwindowinteractor': 'rendererwindowinteractor.png',
                'source': 'source.png',
                'texture': 'texture.png',
                'window': 'window.png',
                'writer': 'writer.png',
                }

    # Lower case the name.
    name = object_name.lower()
    
    for key in icon_map:
        if name.endswith(key):
            return icon_map[key]

    # No valid icon for this object.
    return ''


######################################################################
# `TreeGenerator` class.
######################################################################
class TreeGenerator(HasTraits):
    """Encapsulates the methods that generate the tree via the
    `get_children` method."""

    def has_children(self, obj):
        """Returns True if object `obj` has children."""
        raise NotImplementedError

    def get_children(self, obj):
        """Returns a dictionary containing the children of the object
        `obj`."""
        raise NotImplementedError

    def get_node(self, obj):
        """Get a node object representing this object."""
        raise NotImplementedError

    def get_nodes(self, menu):
        """Returns a list of nodes for the tree editor.  The menu
        entries to use for the nodes are passed as `menu`."""
        raise NotImplementedError


######################################################################
# `SimpleTreeGenerator` class.
######################################################################
class SimpleTreeGenerator(TreeGenerator):
    """This particular class generates a simple pipeline
    representation.  Not every possible object is obtained."""

    def has_children(self, obj):
        """Returns true of the object has children, false if not.  This is
        very specific to tvtk objects."""
        if isinstance(obj, (AVL,Case,Geometry,Surface, RunCase)):
            return True
        return False

    def get_children(self, obj):
        """Returns the child objects of a particular tvtk object in a
        dictionary, the keys are the trait names.  This is used to
        generate the tree in the browser."""
        kids = {}
        def _add_kid(key, x):
            if x is None:
                kids[key] = None
            else:
                if type(x) in (type([]), type(())):
                    x1 = [i for i in x]
                    if x1:
                        kids[key] = x1
                else:
                    kids[key] = x

        if isinstance(obj, AVL):
            return {'run_cases':obj.run_cases,'case':obj.case}
        elif isinstance(obj, Case):
            return {'geometry':obj.geometry}
        elif isinstance(obj, RunCase):
            return {}
        elif isinstance(obj, Geometry):
            return {'surfaces':obj.surfaces, 'bodies':obj.bodies}
        elif isinstance(obj, Surface):
            return {'sections':obj.sections}
        
        #if isinstance(obj, tvtk.Collection):
        #    _add_kid(obj)
        
        return kids

    def get_node(self, obj):
        """Get a node object representing the object passed."""
        if self.has_children(obj):
            return TreeBranchNode(object=obj, tree_generator=self)
        else:
            return TreeLeafNode(object=obj)

    def get_nodes(self, menu):
        """Returns a list of nodes for the tree editor.  The menu
        entries to use are given as `menu`"""
        nodes = [ObjectTreeNode(node_for=[TreeBranchNode],
                                view=View(Group(Item('object', style='custom'),
                                                show_labels=False)),
                                auto_open=False,
                                children='children', label='name', menu=menu,
                                rename=False, delete=False, copy=False,
                                insert=False),
                 ObjectTreeNode(node_for=[TreeLeafNode],
                                view=View(Group(Item('object', style='custom'),
                                                show_labels=False)),
                                auto_open=False,
                                label='name', menu=menu, rename=False,
                                delete=False, copy=False, insert=False),
                 ObjectTreeNode(node_for=[TreeCollectionNode],
                                auto_open=True, children='children',
                                label='name', menu=menu, rename=False,
                                delete=False, copy=False, insert=False),
                 ]
        return nodes


######################################################################
# `CompositeIterable` class.
######################################################################
class CompositeIterable(HasTraits):

    """This class allows one to iterate over a bunch of disparate
    objects treating them as one single iterable.  Each of the
    iterated objects is wrapped with a suitable Node class so that the
    object may be used in a Traits Tree Editor.
    """

    tree_generator = Instance(TreeGenerator)
    
    def __init__(self, args, **traits):
        super(CompositeIterable, self).__init__(**traits)
        self.args = args

    def __iter__(self):
        tg = self.tree_generator
        for arg in self.args:
            if is_iterable(arg):
                for x in arg:
                    yield tg.get_node(x)
            else:
                yield tg.get_node(arg)

    def __len__(self):
        x = 0
        for arg in self.args:
            if is_iterable(arg):
                x += len(arg)
            else:
                x += 1
        return x


######################################################################
# `TVTKLeafNode` class.
######################################################################
class TreeLeafNode(TreeNodeObject):
    """Represents a leaf in the tree view."""
    
    # The tvtk object being wrapped.
    object = Instance(HasTraits)
    # Name to show on the view.
    name = Property(Str, depends_on='object.name?')

    # Work around problem with HasPrivateTraits.
    __ = Python

    #def __hash__(self):
    #    return hash(tvtk.to_vtk(self.object))
        
    def _get_name(self):
        if isinstance(self.object, AVL):
            return 'pyAVL'
        elif isinstance(self.object, (Case,RunCase,Surface,Body)):
            return self.object.name
        elif isinstance(self.object, Geometry):
            pass
        return self.object.__class__.__name__

    ######################################################################
    # `TreeNodeObject` interface
    ######################################################################
    def tno_get_icon(self, node, is_expanded):
        """ Returns the icon for a specified object.
        """
        icon = get_icon(self.name)
        if icon:
            return icon
        else:
            return super(TreeLeafNode, self).tno_get_icon(node, is_expanded)


######################################################################
# `TVTKBranchNode` class.
######################################################################
class TreeBranchNode(TreeNodeObject):
    """Represents a branch in the tree view.  The `children` trait
    produces an iterable that represents the children of the branch.
    """
    # The tvtk object being wrapped.
    object = Instance(HasTraits)
    # Children of the object.
    children = Property
    # Name to show on the view.
    name = Property(Str, depends_on='object.name?')
    # Tree generator to use.
    tree_generator = Instance(TreeGenerator)
    # Cache of children.
    children_cache = Dict

    # Work around problem with HasPrivateTraits.
    __ = Python

    def __init__(self, **traits):
        super(TreeBranchNode, self).__init__(**traits)

    def __del__(self):
        try:
            self._remove_listners()
        except:
            pass

    #def __hash__(self):
    #    return hash(tvtk.to_vtk(self.object))

    def _get_children_from_cache(self):
        return [x for x in self.children_cache.values() if x is not None]

    def _create_children(self):
        kids = self.tree_generator.get_children(self.object)
        self.children_cache = kids
        #self._setup_listners()

    #def _setup_listners(self):
    #    object = self.object
    #    kids = self.children_cache
    #    for key, val in kids.items():
    #        if isinstance(val, tvtk.Collection):
    #            vtk_obj = tvtk.to_vtk(val)
    #            messenger.connect(vtk_obj, 'ModifiedEvent',
    #                              self._notify_children)
    #        else:
    #            object.on_trait_change(self._notify_children, key)

    #def _remove_listners(self):
    #    object = self.object
    #    kids = self.children_cache
    #    for key, val in kids.items():
    #        if isinstance(val, tvtk.Collection):
    #            vtk_obj = tvtk.to_vtk(val)
    #            messenger.disconnect(vtk_obj, 'ModifiedEvent',
    #                                 self._notify_children)
    #        else:
    #            object.on_trait_change(self._notify_children, key, remove=True)

    def _notify_children(self, obj=None, name=None, old=None, new=None):
        old_val = self._get_children_from_cache()
        self._remove_listners()
        self._create_children()
        new_val = self._get_children_from_cache()
        self.trait_property_changed('children', old_val, new_val)

    def _get_children(self):
        if not self.children_cache:
            self._create_children()
        kids = self._get_children_from_cache()
        tg = self.tree_generator
        return CompositeIterable(kids, tree_generator=tg)

    def _get_name(self):
        if isinstance(self.object, AVL):
            return 'pyAVL'
        elif isinstance(self.object, (Case,RunCase,Surface,Body)):
            return self.object.name
        elif isinstance(self.object, Geometry):
            pass
        return self.object.__class__.__name__

    ######################################################################
    # `TreeNodeObject` interface
    ######################################################################
    def tno_get_icon(self, node, is_expanded):
        """ Returns the icon for a specified object.
        """
        icon = get_icon(self.name)
        if icon:
            return icon
        else:
            return super(TreeBranchNode, self).tno_get_icon(node, is_expanded)


######################################################################
# `TVTKCollectionNode` class.
######################################################################
class TreeCollectionNode(TreeNodeObject):
    """Represents a collection of typically unconnected roots in the
    tree view.
    """
    # List of child nodes.
    object = List()
    # Children of the object.
    children = Property 
    # Name to show on the view.
    name = Str
    # Tree generator to use.
    tree_generator = Instance(TreeGenerator)

    # Work around problem with HasPrivateTraits.
    __ = Python

    def __init__(self, **traits):
        super(TreeCollectionNode, self).__init__(**traits)

    def _get_children(self):
        tg = self.tree_generator
        return CompositeIterable(self.object, tree_generator=tg)


######################################################################
# `CloseHandler` class.
######################################################################
class UICloseHandler(TVTKBaseHandler):
    """This class cleans up after the UI for the object is closed."""
    # The browser associated with this UI.
    browser = Any
    
    def close(self, info, is_ok):
        """This method is invoked when the user closes the UI."""
        obj = info.object
        #obj.on_trait_change(self.browser.render, remove=True)
        return True    


######################################################################
# `PipelineBrowser` class.
######################################################################
class AVLTreeBrowser(HasTraits):
    # The tree generator to use.
    tree_generator = Trait(SimpleTreeGenerator(),
                           Instance(TreeGenerator))

    # The TVTK render window(s) associated with this browser.
    avl = Instance(AVL)

    # The root object to view in the pipeline.  If None (default), the
    # root object is the render_window of the Scene instance passed at
    # object instantiation time.
    root_object = List()
    
    # Private traits.
    # The root of the tree to display.
    _root = Any

    ###########################################################################
    # `object` interface.
    ###########################################################################
    def __init__(self, avl=None, **traits):
        """Initializes the object.

        Parameters
        ----------

        - renwin: `Scene` instance.  Defaults to None.

          This may be passed in addition to the renwins attribute
          which can be a list of scenes.

        """
        super(AVLTreeBrowser, self).__init__(**traits)
        self.ui = None
        self.view = None
        if avl:
            self.avl = avl

        self._root_object_changed(self.root_object)
        menu = Menu(Action(name='Refresh', action='editor.update_editor'),
                    Action(name='Expand all', action='editor.expand_all'))
        self.menu = menu

        nodes = self.tree_generator.get_nodes(menu)
        
        self.tree_editor = TreeEditor(nodes=nodes,
                                      orientation='vertical',
                                      hide_root=True,
                                      on_dclick=self._on_dclick)
        self.view = View(Group(Item(name='_root',
                                    editor=self.tree_editor,
                                    resizable=True),
                               show_labels=False,
                               show_border=False,
                               orientation='vertical'),
                         title='pyAVL',
                         help=False,
                         resizable=True, undo=False, revert=False,
                         width=.3, height=.3)

    ###########################################################################
    # `PipelineBrowser` interface.
    ###########################################################################
    def show(self, parent=None):
        """Show the tree view if not already show.  If optional
        `parent` widget is passed, the tree is displayed inside the
        passed parent widget."""
        # If UI already exists, raise it and return.
        if self.ui and self.ui.control:
            try:
                self.ui.control.Raise()
            except AttributeError:
                pass
            else:
                return
        else:
            # No active ui, create one.
            if parent:
                self.ui = self.view.ui(self, parent=parent, kind='subpanel')
            else:
                self.ui = self.view.ui(self, parent=parent)
                
    def update(self):
        """Update the tree view."""
        # This is a hack.
        if self.ui and self.ui.control:
            try:
                ed = self.ui._editors[0]
                ed.update_editor()
                self.ui.control.Refresh()
            except (AttributeError, IndexError):
                pass
    # Another name for update.
    refresh = update

    ###########################################################################
    # Non-public interface.
    ###########################################################################
    def _make_default_root(self):
        tree_gen = self.tree_generator
        objs = [self.avl]
        node = TreeCollectionNode(object=objs, name="Root",
                                  tree_generator=tree_gen)
        return node

    def _tree_generator_changed(self, tree_gen):
        """Traits event handler."""
        if self._root:
            root_obj = self._root.object
        else:
            root_obj = self.root_object
        if root_obj:
            ro = root_obj
            if not hasattr(root_obj, '__len__'):
                ro = [root_obj]
                
            self._root = TreeCollectionNode(object=ro,
                                            name="Root",
                                            tree_generator=tree_gen)
        else:
            self._root = self._make_default_root()

        self.tree_editor.nodes = tree_gen.get_nodes(self.menu)
        self.update()

    def _root_object_changed(self, root_obj):
        """Trait handler called when the root object is assigned to."""
        tg = self.tree_generator
        if root_obj:
            self._root = TreeCollectionNode(object=root_obj, name="Root",
                                            tree_generator=tg)
        else:
            self._root = self._make_default_root()
            self.root_object = self._root.object
        self.update()

    def _root_object_items_changed(self, list_event):
        """Trait handler called when the items of the list change."""
        self._root_object_changed(self.root_object)
    
    def _on_dclick(self, obj):
        """Callback that is called when nodes are double-clicked."""
        if hasattr(obj, 'object') and hasattr(obj.object, 'edit_traits'):
            object = obj.object
            view = object.trait_view()
            view.handler = UICloseHandler(browser=self)
            #object.on_trait_change(self.render)
            ui = object.edit_traits(view=view)
            
    #view = View()


if __name__ == '__main__':
    file = open('/opt/idearesearch/avl/runs/vanilla.avl')
    avl = AVL(cwd='/opt/idearesearch/avl/runs/')
    avl.load_case_from_file('/opt/idearesearch/avl/runs/vanilla.avl')
    #tv = AVLTreeView(avl=avl)
    tv = AVLTreeBrowser(avl)
    #gui = GUI()
    #tv.show()
    #gui.start_event_loop()
    
    tv.configure_traits(view=tv.view)

