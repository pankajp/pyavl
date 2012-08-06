'''
Created on Jul 2, 2009

@author: pankaj
'''

import numpy
from pyavl.geometry import Section, SectionAIRFOILData
from pyavl.utils.traitstools import CustomSaveTool
from itertools import chain

from enthought.traits.api import HasTraits, Range, Instance, on_trait_change, Array, Property, cached_property, List, Int, Tuple, Float
from enthought.traits.ui.api import View, Item, Group
from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.mayavi.tools.mlab_scene_model import MlabSceneModel
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene
from enthought.chaco.api import ArrayPlotData, Plot, create_line_plot, ScatterPlot, DataRange2D, PlotLabel
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.chaco_plot_editor import ChacoPlotItem
from enthought.chaco.tools.api import PanTool, ZoomTool, DragZoom, TraitsTool, SaveTool



class SectionViewer(HasTraits):
    section = Instance(Section)
    plot = Instance(Plot)
    plotdata = Instance(ArrayPlotData, kw={'x':numpy.array([]), 'y':numpy.array([])})
    #pointsx = Array(numpy.float, value=numpy.array([]))
    #pointsy = Array(numpy.float, value=numpy.array([]))
    data = Property(Array, depends_on='section.data.data_points')
    @cached_property
    def _get_data(self):
        try:
            ret = self.section.data.data_points
            #self.pointsx = ret[:, 0]
            #self.pointsy = ret[:, 1]
            self.plotdata.set_data('x', ret[:, 0])
            self.plotdata.set_data('y', ret[:, 1])
            return ret
        except AttributeError:
            return numpy.Array([[], []])
    
    @on_trait_change('data')
    def replot(self):
        # FIXME: handle aspect ratio correctness
        print 'in SectionViewer.plot'
        self.plot.title = 'Section : %s' % self.section.type
        self.plot.request_redraw()
        
    def __init__(self, *l, **kw):
        # TODO: implement aspect ratio maintaining
        HasTraits.__init__(self, *l, **kw)
        #self.plotdata = ArrayPlotData(x=self.pointsx, y=self.pointsy)
        plot = Plot(self.plotdata)
        renderer = plot.plot(("x", "y"))
        
        #lineplot = create_line_plot((self.pointsx,self.pointsy), width=2.0)
        #lineplot.tools.append(PanTool(lineplot, drag_button='middle'))
        #lineplot.tools.append(ZoomTool(lineplot, tool_mode='box'))
        plot.tools.append(PanTool(plot, drag_button='left'))
        plot.tools.append(ZoomTool(plot, tool_mode='box'))
        plot.tools.append(DragZoom(plot, tool_mode='box', drag_button='right'))
        plot.tools.append(CustomSaveTool(plot))#, filename='/home/pankaj/Desktop/file.png'))
        #plot.overlays.append(PlotLabel('Section : %s' % self.section.type,component=plot))
        
        #plot.tools.append(PlotToolbar(plot))
        plot.tools.append(TraitsTool(plot))
        #plot.tools.append(ZoomTool(plot, tool_mode='box', axis='index', drag_button='right', always_on=True))
        #plot.aspect_ratio = 3
        #plot.request_redraw()
        #print plot.bounds
        #plot.aspect_ratio = 1
        #plot.bounds = [500,300]
        #print plot.bounds
        #plot.range2d = DataRange2D(low=(0,-.5), high=(1,0.5))
        #print plot.bounds
        for renderer in chain(*plot.plots.values()):
            renderer.index_mapper.stretch_data = False
            renderer.value_mapper.stretch_data = False
            
            renderer.index_mapper.range.low = 0
            renderer.index_mapper.range.high = 1
            renderer.value_mapper.range.low = - 3 / 8.
            renderer.value_mapper.range.high = 3 / 8.
        self.plot = plot
        
    
    view = View(Item('plot', editor=ComponentEditor(),
                        show_label=False,
                        resizable=True,),
                resizable=True
            )
    

if __name__ == '__main__':
    from pyavl.case import Case
    from pyavl import runs_dir, join
    file = open(join(runs_dir, 'ow.avl'))
    case = Case.case_from_input_file(file)
    #g = GeometryViewer(geometry=case.geometry)
    #g.configure_traits()
    #print g.surfaces[2].sectiondata
    sections = case.geometry.surfaces[2].sections
    section = sections[0]
    section.type = 'NACA'
    section.data.number = 4412
    #for s in sections:
    #    if s.type == 'airfoil data file':
    #        section = s
    #        break
    #print section, [s.data for s in sections]
    sv = SectionViewer(section=section)
    sv.configure_traits()
    
    #section = sections[0]
    sectiondata = SectionAIRFOILData.get_clipped_section_data(section.data, 0.1, 135)
    section2 = Section(type=sectiondata.type)
    section2.data = sectiondata
    #section.type = sectiondata.type
    #section.data = sectiondata
    sv = SectionViewer(section=section2)
    sv.configure_traits()
    