'''
Created on Jul 3, 2009

@author: pankaj
'''

from numpy import float
from enthought.traits.api import HasTraits, Tuple, List, Float, String, on_trait_change
from enthought.traits.ui.api import View, Item, ListEditor, TupleEditor, TextEditor

#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.# Imports:
from enthought.traits.api import HasStrictTraits, Str, Int, Regex, List, Instance, cached_property, Property, Dict
    
from enthought.traits.ui.api \
    import TreeEditor, TreeNodeObject, ObjectTreeNode, View, Item, Tabbed, TableEditor, ListEditor, Handler, Group
from enthought.traits.ui.menu import ToolBar, Action, Menu, Separator
from enthought.traits.ui.table_column \
    import ObjectColumn
    
from enthought.traits.ui.table_filter \
    import RuleTableFilter, RuleFilterTemplate, \
           MenuFilterTemplate, EvalFilterTemplate

class Parameter(HasTraits):
    name = String('name')
    value = Float
    def __str__(self): return '{%s:%f}' %(self.name,self.value)
    def __repr__(self): return '{%s:%f}' %(self.name,self.value)
    editor = TableEditor(
        auto_size=False,
        columns=[ObjectColumn(name='name', label='Name', editable=False),
                 ObjectColumn(name='value', label='Value',
            editor=TextEditor(evaluate=float, enter_set=True, auto_set=False)),
            ])
class C(HasTraits):
    d = Dict(String, Instance(Parameter), {'p1':Parameter(name='p1',value=0.1),
                                           'p2':Parameter(name='p2',value=0.2)})
    d_view = List(Instance(Parameter))
    def _d_view_default(self):
        return self.d.values()
    @on_trait_change('d.value')
    def update_view(self):
        print 'updating view'
        self.d_view = self.d.values()
    @on_trait_change('d_view.value')
    def update_d(self):
        print 'updating d'
    
    view = View(Item('d_view', editor=Parameter.editor))

c = C()
c.configure_traits()
print c.d, c.d_view
c.d['p1'].value = 1.2
print c.d, c.d_view
c.d_view[0].value = 1.2
print c.d, c.d_view
