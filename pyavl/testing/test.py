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
    import HasStrictTraits, Str, Int, Regex, List, Instance, cached_property, Property, Dict
    
from enthought.traits.ui.api \
    import View, Item, Tabbed, TableEditor, ListEditor
    
from enthought.traits.ui.table_column \
    import ObjectColumn
    
from enthought.traits.ui.table_filter \
    import RuleTableFilter, RuleFilterTemplate, \
           MenuFilterTemplate, EvalFilterTemplate

class C(HasTraits):
    a = String
    def __repr__(self):
        return '<Instance class C>(a=%s)' % self.a

class A(HasTraits):
    d = Dict(String,Instance(C),{})
    p = Property(List(String), depends_on='d')
    @cached_property
    def _get_p(self):
        return self.d.keys()
    traits_view = View(['d','p'])
    def update(self,l):
        for t in l:
            self.d[t[0]] = C(a=t[2])
    
a = A()
print a.d
print a.p
a.update([('Mach No',1.6,''),('Temperature',380,'K')])
print a.d
print a.p
a.configure_traits()
print a.d
print a.p
