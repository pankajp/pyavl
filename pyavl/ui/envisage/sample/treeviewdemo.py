#-------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
# 
#  Author: David C. Morrill
#  Date:   09/15/2005
#  
#-------------------------------------------------------------------------------

""" A Traits UI demo that borrows heavily from the design of the wxPython demo.
"""

#-------------------------------------------------------------------------------
#  Imports:  
#-------------------------------------------------------------------------------

from pyavl.case import *
from pyavl.geometry import *

import sys
import glob
from configobj import ConfigObj
                
from enthought.pyface.timer.api import do_later

from enthought.traits.api \
    import HasTraits, HasPrivateTraits, Str, Instance, Property, Any, \
           Code, HTML, true, false, cached_property, Dict
           
from enthought.traits.ui.api \
    import TreeEditor, ObjectTreeNode, TreeNodeObject, View, Item, VSplit, \
           Tabbed, VGroup, HGroup, Heading, Handler, UIInfo, InstanceEditor, \
           Include, spring

from os \
    import listdir
    
from os.path \
    import join, isdir, split, splitext, dirname, basename, abspath, exists, isabs


class GeometryTraitsNode(TraitsNode):
    geometry = Instance(Geometry)
    allows_children = false

class CaseTraitsNode(TraitsNode):
    case = Instance(Case)
    allows_children = true
    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        return True
    def get_children ( self ):
        """ Gets the object's children.
        """
        return [GeometryTraitsNode(self.case.geometry)]

                   
demo_tree_editor = TreeEditor(
    nodes = [
        ObjectTreeNode( node_for = [ CaseTraitsNode ],
                        label    = 'nice_name',
                        view     = View([ 'name','mach_no']) ),
        ObjectTreeNode( node_for = [ GeometryTraitsNode ],
                        label    = 'nice_name',
                        view     = View([ 'surfaces','geometries']) )
    ],
    show_icons=False
)

class CaseTreeView(HasTraits):
    case = Instance(Case)
    casetreenode = Instance(CaseTraitsNode)
    
    view = View( 
        Item( name       = 'casetreenode',   
              editor     = demo_tree_editor, 
              show_label = False
        ),
        title     = 'AVL Case',
        buttons   = [ 'OK' ],
        resizable = True,
        style     = 'custom',
        width     = .3,
        height    = .3
    )

if __name__ == '__main__':
    file = open('/opt/idearesearch/avl/runs/vanilla.avl')
    case = Case.case_from_input_file(file)
    file.close()
    tv = CaseTreeView(casetreenode=CaseTraitsNode(case=case))
    tv.configure_traits(view='view')


