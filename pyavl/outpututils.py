'''
Created on Jul 9, 2009

@author: pankaj
'''


import numpy

from enthought.traits.api import HasTraits, List, String, Array, Instance, Complex
from enthought.traits.ui.api import TableEditor, View, Item, Group


class EigenMode(HasTraits):
    eigenvalue = Complex()
    # the = theta
    order = ['u', 'w', 'q', 'the', 'v', 'p', 'r', 'phi', 'x', 'y', 'z', 'psi']
    eigenvector = Array(numpy.complex, shape=(12,))
    
    editor = Instance(TableEditor)
    def _editor_default(self):
        cols = [ObjectColumn(name='eigenvalue', label='EigenValue')]
        cols += [ObjectColumn(name='name', label=s) for s in self.order]
        ret = TableEditor(
            auto_size=False,
            editable=False,
            columns=None)

class EigenMatrix(HasTraits):
    # include the control vector
    matrix = Array(numpy.float, shape=(12, (12, None)))
    order = ['u', 'w', 'q', 'the', 'v', 'p', 'r', 'phi', 'x', 'y', 'z', 'psi']

class RunOutput(HasTraits):
    '''class to store the output if a sequence of runcases'''
    # the names of the variables
    variable_names = List(String)
    # 2d array
    variable_values = Array(numpy.float, shape=(None, None))
    eigenmodes = List(EigenMode)
    eigenmatrix = List(EigenMatrix)
    output_view = Instance(View)
    eigenmode_view = Instance(View)
    
    
    
    