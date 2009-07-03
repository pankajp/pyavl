'''
Created on Jul 3, 2009

@author: pankaj
'''

from numpy import float
from enthought.traits.api import HasTraits, Tuple, List, Float, String
from enthought.traits.ui.api import View, Item, ListEditor, TupleEditor, TextEditor

#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.# Imports:  
from enthought.traits.api \
    import HasStrictTraits, Str, Int, Regex, List, Instance
    
from enthought.traits.ui.api \
    import View, Item, Tabbed, TableEditor, ListEditor
    
from enthought.traits.ui.table_column \
    import ObjectColumn
    
from enthought.traits.ui.table_filter \
    import RuleTableFilter, RuleFilterTemplate, \
           MenuFilterTemplate, EvalFilterTemplate

class A(HasTraits):
    l = List(Tuple(String,Float,String))
    traits_view = View(Item('l', editor=ListEditor(mutable=False,
                    editor=TupleEditor(cols=3, editors=[TextEditor(),
                            TextEditor(evaluate=float), TextEditor()]))))
    def update(self,l):
        for t in l:
            self.add_trait(t[0], Tuple(Float,String))
            self.trait_setq({l[0]:(t[1],t[2])})
    
a = A()
a.update([('Mach No',1.6,''),('Temperature',380,'K')])
a.configure_traits()
