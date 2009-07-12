'''
Created on Jul 11, 2009

@author: pankaj
'''

from pyavl.outpututils import RunOutput
from pyavl.avl import RunCase
from pyavl.utils.traitstools import CustomSaveTool, get_file_from_user

import numpy

from enthought.traits.api import HasTraits, Instance, String, on_trait_change, Property, List, cached_property, Button
from enthought.traits.ui.api import View, Group, Item, EnumEditor, HGroup, TabularEditor
from enthought.traits.ui.tabular_adapter import TabularAdapter
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.chaco_plot_editor import ChacoPlotItem
from enthought.chaco.tools.api import PanTool, ZoomTool, DragZoom, TraitsTool, SaveTool
from enthought.chaco.api import ArrayPlotData, Plot, create_line_plot, ScatterPlot, DataRange2D, PlotLabel

class OutputPlotViewer(HasTraits):
    runoutput = Instance(RunOutput)
    plot = Instance(Plot)
    #data = Property(Array, depends_on='runoutput.variable_values,var_x,var_y')
    plotdata = Instance(ArrayPlotData, kw={'x':numpy.array([]), 'y':numpy.array([])})
    var_names_view = Property(List(String), depends_on='runoutput.variable_names')
    @cached_property
    def _get_var_names_view(self):
        return sorted(self.runoutput.variable_names, key=lambda x:x.lower())
    
    @on_trait_change('runoutput.variable_values,var_x,var_y')
    def set_plotdata(self):
        var_names = self.runoutput.variable_names
        self.plot.x_axis.title = self.var_x
        self.plot.y_axis.title = self.var_y
        #try:
        self.plotdata.set_data('x', self.runoutput.variable_values[:, var_names.index(self.var_x)])
        self.plotdata.set_data('y', self.runoutput.variable_values[:, var_names.index(self.var_y)])
        #except ValueError, e:
        #    pass
        self.replot()
    
    #@on_trait_change('data')
    def replot(self):
        print 'in OutputPlotViewer.plot'
        self.plot.title = 'Output'
        self.plot.request_redraw()
    
    var_x = String('Alpha')
    var_y = String('CLtot')
    
    def __init__(self, *l, **kw):
        # TODO: implement aspect ratio maintaining
        HasTraits.__init__(self, *l, **kw)
        #self.plotdata = ArrayPlotData(x=self.pointsx, y=self.pointsy)
        plot = Plot(self.plotdata)
        plot.plot(("x", "y"))
        
        plot.tools.append(PanTool(plot, drag_button='left'))
        plot.tools.append(ZoomTool(plot, tool_mode='box'))
        plot.tools.append(DragZoom(plot, tool_mode='box', drag_button='right'))
        plot.tools.append(CustomSaveTool(plot))#, filename='/home/pankaj/Desktop/file.png'))
        plot.tools.append(TraitsTool(plot))
        self.plot = plot
        self.set_plotdata()
        
    
    view_variables = View(Item('plot', editor=ComponentEditor(), show_label=False, resizable=True,),
                          HGroup(Item('var_x', editor=EnumEditor(name='var_names_view')),
                                 Item('var_y', editor=EnumEditor(name='var_names_view'))),
                          resizable=True
                        )


class OutputVariablesAdapter(TabularAdapter):
    def _columns_default(self):
        var_names = sorted(self.object.variable_names, key=lambda x:x.lower())
        ret = [(var_name, self.object.variable_names.index(var_name)) for var_name in var_names]
        return ret
    width = 80

class OutputVariablesViewer(HasTraits):
    runoutput = Instance(RunOutput)
    save_data = Button('')
    def _save_data_fired(self):
        filename = get_file_from_user()
        if filename:
            f = open(filename, 'w')
            self.runoutput.save_variables(f)
            f.close()
    
    view = View(Item('save_data', show_label=False),
                Item('object.runoutput.variable_values',
                     editor=TabularEditor(adapter=OutputVariablesAdapter(), operations=[], editable=False),
                     show_label=False),
                resizable=True
                )

if __name__ == '__main__':
    from pyavl.avl import AVL
    from pyavl.runutils import RunConfig
    avl = AVL(cwd='/opt/idearesearch/avl/runs/')
    filename = '/opt/idearesearch/avl/runs/allegro.avl'
    avl.load_case_from_file(filename)
    rv = RunConfig(runcase=RunCase.get_case_from_avl(avl.avl))
    print rv.configure_traits(kind='livemodal')
    print 'rv configured'
    output = rv.run()
    print output
    print 'rv ran'
    opv = OutputPlotViewer(runoutput=output)
    opv.configure_traits()
    
    ovv = OutputVariablesViewer(runoutput=output)
    ovv.configure_traits()
    