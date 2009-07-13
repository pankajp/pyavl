'''
Created on Jun 15, 2009

@author: pankaj
'''

import numpy


from pyavl.geometry import Geometry, Surface, Body


from enthought.traits.api import HasTraits, Range, Instance, on_trait_change, Array, Property, cached_property, List, Int, Tuple, Float
from enthought.traits.ui.api import View, Item, Group
from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.mayavi.tools.mlab_scene_model import MlabSceneModel
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene
from enthought.chaco.api import ArrayPlotData, Plot, create_line_plot, ScatterPlot, DataRange2D, PlotLabel
from enthought.enable.component_editor import ComponentEditor
from enthought.chaco.chaco_plot_editor import ChacoPlotItem
from enthought.chaco.tools.api import PanTool, ZoomTool, DragZoom, TraitsTool, SaveTool


from numpy import linspace


class BodyViewer(HasTraits):
    body = Instance(Body)
    # x,dia
    diameters = Property(Array(numpy.float), depends_on='_cp,num_pts')
    num_pts = Int(20)
    # numpoints, xyx radius
    bodydata = Property(Array(dtype=numpy.float, shape=(None, 4)), depends_on='diameters')
    # inflexion_pt, min, max of the x coordinates
    data_props = Property(Tuple(Int, Float, Float), depends_on='body.data')
    @cached_property
    def _get_data_props(self):
        x = self.body.data[:, 0]
        if x[1] > x[0]:
            return numpy.argmax(x), numpy.min(x), numpy.max(x)
        else:
            return numpy.argmin(x), numpy.min(x), numpy.max(x)
    @cached_property
    def _get_diameters(self):
        x = numpy.linspace(numpy.min(self.data_props[2]), numpy.min(self.data_props[1]), self.num_pts)
        # datax, datay
        dxu, dyu = self.body.data[:self.data_props[0], 0], self.body.data[:self.data_props[0], 1]
        dxl, dyl = self.body.data[self.data_props[0] - 1:, 0], self.body.data[self.data_props[0] - 1:, 1]
        #iu, il = numpy.searchsorted(dxu, x), numpy.searchsorted(dxl, x)
        #yu = dyu[iu] - (dyu[iu] - dyu[iu - 1]) * (dxu[iu]-x) / (dxu[iu]-dx[iu-1])
        #yl = dyl[il] - (dyl[il] - dyl[il - 1]) * (dxl[il]-x) / (dxl[il]-dx[il-1])
        yu = numpy.interp(x, dxu, dyu)
        yl = numpy.interp(x, dxl, dyl)
        return numpy.array([x,abs(yu-yl)]).T
    # superior will take care of yduplicate
    @cached_property
    def _get_bodydata(self):
        ret = numpy.empty((self.num_pts, 4))
        # y,z coords are 0
        ret[:,1:3] = 0.0
        # scale : radii (by sqrt(y*z)) and x
        # set the radii
        ret[:,3] = self.diameters[:,1]/2 * (self.body.scale[1]*self.body.scale[2])**0.5
        # set the radii centers
        ret[:,0] = self.diameters[:,0] * self.body.scale[0]
        # translate
        ret[:,:3] += self.body.translate
        return ret
    
class SurfaceViewer(HasTraits):
    # sorted by span y coordinate
    surface = Instance(Surface)
    # section chords : leading edge, trailing edge -> to be set by sectiondata
    section_chords = Array(dtype=numpy.float, shape=(None, 2, 3))
    # min 2 points in a section
    # List : section , point , xyz
    sectiondata = Property(List(Array(dtype=numpy.float, shape=((2, None), 3)), depends_on='surface'))
    # array : section , num_pts, xyz
    surfacedata = Property(Array(dtype=numpy.float, shape=(None, None, 3)), depends_on='sectiondata')
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
            data[:, 0], data[:, 2] = data[:, 0] * c + data[:, 2] * s, data[:, 2] * c - data[:, 0] * s
            # translate to the leading edge
            data += section.leading_edge
            # transformations inherited from surface
            data *= self.surface.scale
            data += self.surface.translate
            
            ret.append(data)
            # get trailing edge
            te = numpy.array([section.chord * c,
                              0,
                              - section.chord * s])
            te += section.leading_edge
            #assert data[1,2] == te[2]
            chords.append(numpy.array([section.leading_edge, te]))
            if numpy.isfinite(self.surface.yduplicate):
                #print 'ydup'
                data2 = numpy.empty(shape=data.shape)
                data2[:, 0] = data[:, 0]
                data2[:, 2] = data[:, 2]
                data2[:, 1] = self.surface.yduplicate - data[:, 1]
                le2 = numpy.array([section.leading_edge[0], self.surface.yduplicate - section.leading_edge[1], section.leading_edge[2]])
                te2 = numpy.array([te[0], self.surface.yduplicate - te[1], te[2]])
                #print data[:,1], data2[:,1]
                ret.append(data2)
                chords.append(numpy.array([le2, te2]))
        ret.sort(key=lambda x: x[0, 1])
        chords.sort(key=lambda x: x[0, 1])
        chords = numpy.array(chords)
        chords *= self.surface.scale
        chords += self.surface.translate
        self.section_chords = chords
        assert len(self.section_chords) == len(ret)
        return ret
    
    @cached_property
    def _get_surfacedata(self, num_sectionpts=6):
        ret = numpy.empty((len(self.sectiondata), num_sectionpts, 3))
        for i, section in enumerate(self.section_chords):
            r = linspace(0, 1, num_sectionpts).reshape(num_sectionpts, 1)
            ret[i, :, :] = section[0, :] + numpy.dot(r, (section[1, :] - section[0, :]).reshape(1, 3))
        return ret
    
    traits_view = View()

class GeometryViewer(HasTraits):
    meridional = Range(1, 30, 6)
    transverse = Range(0, 30, 11)
    scene = Instance(MlabSceneModel, ())
    geometry = Instance(Geometry)
    bodies = Property(List(Instance(BodyViewer)), depends_on='geometry.refresh_geometry_view,geometry.bodies[]')
    surfaces = Property(List(Instance(SurfaceViewer)), depends_on='geometry.refresh_geometry_view,geometry.surfaces[]')
    @cached_property
    def _get_surfaces(self):
        ret = []
        for surface in self.geometry.surfaces:
            ret.append(SurfaceViewer(surface=surface))
        return ret
    
    @cached_property
    def _get_bodies(self):
        ret = []
        for body in self.geometry.bodies:
            ret.append(BodyViewer(body=body))
        return ret
    
    def section_points(self, sections, yduplicate):
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
        #print ret.shape, len(ret2)
        if len(ret2) > 0:
            ret = numpy.concatenate((ret, numpy.array(ret2)))
        return ret
    
    def section_points_old(self, sections, yduplicate):
        ret = []
        for section in sections:
            pt = numpy.empty((2, 3))
            pt[0, :] = section.leading_edge
            pt[1, :] = section.leading_edge
            pt[1, 0] += section.chord * numpy.cos(section.angle * numpy.pi / 180)
            pt[1, 2] -= section.chord * numpy.sin(section.angle * numpy.pi / 180)
            ret.append(pt)
            if yduplicate is not numpy.nan:
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

    @on_trait_change('geometry,geometry.refresh_geometry_view')
    def update_plot(self):
        self.plots = []
        #self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)
        self.scene.mlab.clf()
        # plot the axes
        
        for surface in self.surfaces:
            section_pts = surface.sectiondata
            for i, section_pt in enumerate(section_pts):
                if len(section_pt)==2:
                    #tube_radius = 0.02 * abs(section_pt[-1,0]-section_pt[0,0])
                    tube_radius = None
                else:
                    tube_radius = None
                self.plots.append(self.scene.mlab.plot3d(section_pt[:, 0], section_pt[:, 1], section_pt[:, 2], tube_radius=tube_radius))
            self.plots.append(self.scene.mlab.mesh(surface.surfacedata[:, :, 0], surface.surfacedata[:, :, 1], surface.surfacedata[:, :, 2]))
        for body in self.bodies:
            width = (body.data_props[2]-body.data_props[1])/body.num_pts * 0.15
            for data in body.bodydata:
                c = numpy.empty((2,3))
                c[:] = data[:3]
                c[0,0] -= width/2
                c[1,0] += width/2
                #print c, width
                self.plots.append(self.scene.mlab.plot3d(c[:,0], c[:, 1], c[:, 2], tube_radius=data[3], tube_sides=24))
                if numpy.isfinite(body.body.yduplicate):
                    c[:,1] = body.body.yduplicate - c[:,1]
                    self.plots.append(self.scene.mlab.plot3d(c[:,0], c[:, 1], c[:, 2], tube_radius=data[3], tube_sides=24))
        #print 'numplots = ', len(self.plots)
    
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
    file = open('/opt/idearesearch/avl/runs/bd.avl')
    case = Case.case_from_input_file(file)
    g = GeometryViewer(geometry=case.geometry)
    g.configure_traits()
    #print g.surfaces[2].sectiondata
    