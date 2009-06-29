'''
Created on Jun 15, 2009

@author: pankaj
'''

import numpy
from pyavl.geometry import Geometry, SectionData, Section, Surface

from enthought.traits.api import HasTraits, Range, Instance, on_trait_change, Array, Property, cached_property, List
from enthought.traits.ui.api import View, Item, Group
from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.mayavi.tools.mlab_scene_model import MlabSceneModel
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene
from enthought.chaco.api import ArrayPlotData, Plot, create_line_plot, ScatterPlot
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.chaco_plot_editor import ChacoPlotItem
from enthought.chaco.tools.api import PanTool, ZoomTool

from numpy import linspace, pi, cos, sin


class SectionViewer(HasTraits):
    section = Instance(Section)
    plot = Instance(Plot)
    data = Property(Array, depends_on='section.data')
    @on_trait_change('section.data')
    def _get_data(self):
        ret = self.section.data.get_data_points()
        return ret
    
    pointsx = Property(Array, depends_on='section.data')
    @on_trait_change('data')
    def _get_pointsx(self):
        return self.data[:, 0]
    
    pointsy = Property(Array, depends_on='section.data')
    @on_trait_change('data')
    def _get_pointsy(self):
        return self.data[:, 1]
    
    def __init__(self, *l, **kw):
        HasTraits.__init__(self, *l, **kw)
        plotdata = ArrayPlotData(x=self.pointsx, y=self.pointsy)
        plot = Plot(plotdata)
        plot.plot(("x", "y"))
        
        #lineplot = create_line_plot((self.pointsx,self.pointsy), width=2.0)
        #lineplot.tools.append(PanTool(lineplot, drag_button='middle'))
        #lineplot.tools.append(ZoomTool(lineplot, tool_mode='box'))
        plot.tools.append(PanTool(plot, drag_button='middle'))
        plot.tools.append(ZoomTool(plot, tool_mode='range', axis='value'))
        #plot.tools.append(ZoomTool(plot, tool_mode='box', axis='index', drag_button='right', always_on=True))
        plot.aspect_ratio = 3
        #plot.request_redraw()
        self.plot = plot
    
    view = View(Item('plot', editor=ComponentEditor(),
                        show_label=False,
                        resizable=True,),
                resizable=True
            )

class SurfaceViewer(HasTraits):
    # sorted by span y coordinate
    surface = Instance(Surface)
    # section chords : leading edge,trailing edge to be set by sectiondata
    section_chords = Array(dtype=numpy.float, shape=(None,2,3))
    # min 2 points in a section
    # array : section : point : xyz
    sectiondata = Property(Array(dtype=numpy.float, shape=(None,(2, None), 3)), depends_on='surface')
    surfacedata = Property(Array(dtype=numpy.float, shape=(None,None,3)), depends_on='sectiondata')
    @cached_property
    def _get_sectiondata(self):
        ret = []
        chords = []
        for section in self.surface.sections:
            # FIXME: Assumption: section data is from x=0 to x=1
            dataxz = section.data.get_data_points()
            data = numpy.empty((dataxz.shape[0], 3))
            data[:, 0] = dataxz[:, 0]
            data[:, 1] = 0
            data[:, 2] = dataxz[:, 1]
            # scale
            data *= section.chord
            # rotate by the angle = section+surface angle
            angle = section.angle + self.surface.angle
            c, s = numpy.cos(angle * numpy.pi / 180), numpy.sin(angle * numpy.pi / 180)
            data[:,0], data[:,2] =  data[:,0]*c + data[:,2]*s, data[:,2]*c - data[:,0]*s
            # translate to the leading edge
            data += section.leading_edge
            ret.append(data)
            # get trailing edge
            te = numpy.array([section.chord*c,
                              0,
                              -section.chord*s])
            te += section.leading_edge
            #assert data[1,2] == te[2]
            chords.append(numpy.array([section.leading_edge, te]))
            if numpy.isfinite(self.surface.yduplicate):
                #print 'ydup'
                data2 = numpy.empty(shape=data.shape)
                data2[:,0] = data[:,0]
                data2[:,2] = data[:,2]
                data2[:,1] = self.surface.yduplicate - data[:,1]
                le2 = numpy.array([section.leading_edge[0], self.surface.yduplicate-section.leading_edge[1], section.leading_edge[2]])
                te2 = numpy.array([te[0], self.surface.yduplicate-te[1], te[2]])
                #print data[:,1], data2[:,1]
                ret.append(data2)
                chords.append(numpy.array([le2, te2]))
        #print ret
        out = numpy.array(ret)
        # sort by y position of the section
        arg_sort = numpy.argsort(out[:,0,1])
        out = out[arg_sort]
        chords = numpy.array(chords)[arg_sort]
        # surface transforms
        #print('Scale : %s' %str(self.surface.scale))
        #assert all(self.surface.scale > 0)
        out *= self.surface.scale
        out += self.surface.translate
        chords *= self.surface.scale
        chords += self.surface.translate
        # angle rotation done for each section separately
        self.section_chords = chords
        assert len(self.section_chords) == len(out)
        return out
    
    @cached_property
    def _get_surfacedata(self, num_sectionpts=6):
        ret = numpy.empty((self.sectiondata.shape[0], num_sectionpts, 3))
        for i,section in enumerate(self.section_chords):
            r = linspace(0,1,num_sectionpts).reshape(num_sectionpts,1)
            ret[i,:,:] = section[0,:] + numpy.dot(r,(section[1,:]-section[0,:]).reshape(1,3))
        return ret
    
    traits_view = View()

class GeometryViewer(HasTraits):
    meridional = Range(1, 30, 6)
    transverse = Range(0, 30, 11)
    scene = Instance(MlabSceneModel, ())
    geometry = Instance(Geometry)
    surfaces = Property(List(Instance(SurfaceViewer)), depends_on='geometry')
    @cached_property
    def _get_surfaces(self):
        ret = []
        for surface in self.geometry.surfaces:
            ret.append(SurfaceViewer(surface=surface))
        return ret
    
    def section_points(self, sections, yduplicate):
        # TODO: sort the array
        ret = numpy.empty((len(sections * 2), 3))
        ret2 = []
        for sno, section in enumerate(sections):
            pno = sno * 2
            pt = ret[pno:pno + 2, :]
            pt[0, :] = section.leading_edge
            pt[1, :] = section.leading_edge
            pt[1, 0] += section.chord * numpy.cos(section.angle * numpy.pi / 180)
            pt[1, 2] -= section.chord * numpy.sin(section.angle * numpy.pi / 180)
            if yduplicate is not numpy.nan:
                pt2 = numpy.copy(pt)
                pt2[:, 1] = yduplicate - pt2[:, 1]
                ret2.append(pt2[0, :])
                ret2.append(pt2[1, :])
        print ret.shape, len(ret2)
        if len(ret2) > 0:
            ret = numpy.concatenate((ret, numpy.array(ret2)))
        print ret
        return ret
    
    def section_points_old(self, sections, yduplicate):
        #FIXME: take care of scale and translate keywords
        ret = []
        for section in sections:
            pt = numpy.empty((2, 3))
            pt[0, :] = section.leading_edge
            pt[1, :] = section.leading_edge
            pt[1, 0] += section.chord * numpy.cos(section.angle * numpy.pi / 180)
            pt[1, 2] -= section.chord * numpy.sin(section.angle * numpy.pi / 180)
            ret.append(pt)
            if yduplicate is not numpy.nan:
                print 'ydup'
                pt2 = numpy.copy(pt)
                pt2[:, 1] = yduplicate - pt2[:, 1]
                ret.append(pt2)
        ret = numpy.concatenate(ret)
        return ret
    
    def __init__(self, **args):
        # Do not forget to call the parent's __init__
        HasTraits.__init__(self, **args)
        #self.plot = self.scene.mlab.plot3d(x, y, z, t, colormap='Spectral')
        self.update_plot()

    @on_trait_change('surfaces')
    def update_plot(self):
        self.plots = []
        #self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)
        self.scene.mlab.clf()
        for surface in self.surfaces:
            section_pts = surface.sectiondata
            print section_pts
            for i in xrange(0, section_pts.shape[0]):
                self.plots.append(self.scene.mlab.plot3d(section_pts[i, :, 0], section_pts[i, :, 1], section_pts[i, :, 2]))
            self.plots.append(self.scene.mlab.mesh(surface.surfacedata[:,:,0], surface.surfacedata[:,:,1], surface.surfacedata[:,:,2]))
        print 'numplots = ', len(self.plots)
    
    #@on_trait_change('geometry')
    def update_plot_old(self):
        self.plots = []
        #self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)
        self.scene.mlab.clf()
        for surface in self.geometry.surfaces:
            yduplicate = surface.yduplicate
            section_pts = self.section_points(surface.sections, yduplicate)
            for i in xrange(0, section_pts.shape[0], 2):
                self.plots.append(self.scene.mlab.plot3d(section_pts[i:i + 2, 0], section_pts[i:i + 2, 1], section_pts[i:i + 2, 2], tube_radius=0.1))
        print 'numplots = ', len(self.plots)

    # the layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                    height=250, width=300, show_label=False),
                #Item('geometry', style='custom'),
                resizable=True
                )

if __name__ == '__main__':
    from pyavl.case import Case
    file = open('/opt/idearesearch/avl/runs/h.avl.mod')
    case = Case.case_from_input_file(file)
    g = GeometryViewer(geometry=case.geometry)
    #print g.surfaces[2].sectiondata
    g.configure_traits()
    #sections = case.geometry.surfaces[2].sections
    section = None
    for s in sections:
        if s.type == 'airfoil data file':
            section = s
            break
    print section, [s.data for s in sections]
    SectionViewer(section=section).configure_traits()

