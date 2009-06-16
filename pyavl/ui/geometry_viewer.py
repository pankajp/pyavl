'''
Created on Jun 15, 2009

@author: pankaj
'''

import numpy
from pyavl.geometry import Geometry, SectionData
from enthought.traits.api import HasTraits
from enthought.traits.ui.api import View, Item, Group

from enthought.traits.api import HasTraits, Range, Instance, \
                    on_trait_change
from enthought.traits.ui.api import View, Item, HGroup
from enthought.tvtk.pyface.scene_editor import SceneEditor
from enthought.mayavi.tools.mlab_scene_model import \
                    MlabSceneModel
from enthought.mayavi.core.ui.mayavi_scene import MayaviScene

from numpy import linspace, pi, cos, sin

def curve(n_mer, n_long):
    phi = linspace(0, 2*pi, 2000)
    return [ cos(phi*n_mer) * (1 + 0.5*cos(n_long*phi)),
            sin(phi*n_mer) * (1 + 0.5*cos(n_long*phi)),
            0.5*sin(n_long*phi),
            sin(phi*n_mer)]


class GeometryViewer(HasTraits):
    meridional = Range(1, 30,  6)
    transverse = Range(0, 30, 11)
    scene      = Instance(MlabSceneModel, ())
    geometry = Instance(Geometry)
    
    def section_points(self, section):
        pt = numpy.empty((2,3))
        pt[0,:] = section.leading_edge
        pt[1,:] = section.leading_edge
        pt[1,0] += section.chord * numpy.cos(section.angle*numpy.pi/180)
        pt[1,2] -= section.chord * numpy.sin(section.angle*numpy.pi/180)
        return pt
    
    def __init__(self, **args):
        # Do not forget to call the parent's __init__
        HasTraits.__init__(self, **args)
        x, y, z, t = curve(self.meridional, self.transverse)
        
        #self.plot = self.scene.mlab.plot3d(x, y, z, t, colormap='Spectral')
        self.update_plot()
    
    @on_trait_change('geometry')
    def update_plot(self):
        x, y, z, t = curve(self.meridional, self.transverse)
        self.plots = []
        #self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)
        self.scene.mlab.clf()
        for surface in self.geometry.surfaces:
            section_pts = []
            for section in surface.sections:
                pts = self.section_points(section)
                section_pts.append(pts)
                self.plots.append(self.scene.mlab.plot3d(pts[:,0], pts[:,1], pts[:,2]))
        print 'numplots = ', len(self.plots)

    # the layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                    height=250, width=300, show_label=False),
                Group(
                        '_', 'meridional', 'transverse', '_',
                    ),
                Item('geometry', style='custom'),
                resizable=True
                )

if __name__ == '__main__':
    visualization = GeometryViewer()
    visualization.configure_traits()


