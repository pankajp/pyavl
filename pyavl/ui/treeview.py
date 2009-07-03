'''
Created on Jun 30, 2009

@author: pankaj
'''

from pyavl.avl import AVL, RunCase
from pyavl.case import Case
from pyavl.geometry import Geometry, Surface, Section, Body

from enthought.traits.api import HasTraits, Instance, List
from enthought.traits.trait_handlers import TraitListObject
from enthought.traits.ui.api import TreeEditor, TreeNode, TreeNodeObject, Item, View, \
    ListEditor, ObjectTreeNode, MultiTreeNode
from enthought.traits.ui.value_tree import ObjectNode, TraitsNode 
no_view = View()


AVL_tree_editor = TreeEditor( 
    nodes = [
        TreeNode( node_for  = [ AVL ],
                  auto_open = True,
                  children  = 'run_cases',
                  label     = '=pyAVL',
                  view      = View( [ 'selected_runcase'] )
        ),
        TreeNode( node_for  = [ RunCase ],
                  auto_open = True,
                  children  = '',
                  label     = 'name',
                  view      = View( [ 'name','number','parameters','constraints'] )
        ),
        TreeNode( node_for  = [ Case ],
                  auto_open = True,
                  children  = 'geometries',
                  label     = 'name',
                  view      = View( [ 'name','mach_no'] )
        ),
        TreeNode( node_for  = [ Geometry ],
                  auto_open = True,
                  children  = 'things',
                  label     = '=Geometry',
                  view      = View(['geometry'])#Item('controls', editor=ListEditor(style='readonly')),style='readonly'),
        ),
        TreeNode( node_for  = [ TraitListObject ],
                  auto_open = True,
                  children  = 'sections',
                  label     = '=Surface',
                  view      = no_view
        )
    ],
    orientation='vertical'
)

class AVLTreeView(HasTraits):
    avl = Instance(AVL)
    
    traits_view = View( 
        Item( name       = 'avl',   
              editor     = AVL_tree_editor, 
              show_label = False
        ),
        title     = 'pyAVL',
        buttons   = [ 'OK' ],
        resizable = True,
        style     = 'custom',
        width     = .3,
        height    = .3
    )


if __name__ == '__main__':
    file = open('/opt/idearesearch/avl/runs/vanilla.avl')
    avl = AVL(cwd='/opt/idearesearch/avl/runs/')
    avl.load_case_from_file('/opt/idearesearch/avl/runs/vanilla.avl')
    tv = AVLTreeView(avl=avl)
    tv.configure_traits()

