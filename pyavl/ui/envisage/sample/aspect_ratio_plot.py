'''
Created on Jun 25, 2009

@author: pankaj
'''
#!/usr/bin/env python# Major library imports
from itertools import chain
from numpy import sort, isfinite, sin, linspace
from numpy.random import random


# Enthought library imports
from enthought.enable.api import ComponentEditor
from enthought.traits.api import Any, Bool, BaseFloat, HasTraits
from enthought.traits.ui.api import Item, HGroup, VGroup, View

# Chaco imports
from enthought.chaco.api import ArrayPlotData, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool

class AspectRatio(BaseFloat):
    "A new Trait for defining aspect ratios"

    default_value = 1.0
    
    info_text = "a nonzero floating point number"

    def validate(self, object, name, value):
        value = super(AspectRatio, self).validate(object, name, value)
        if value != 0.0 and isfinite(value):
            return value
        else:
            self.error(object, name, value)


class MyPlot(HasTraits):

    plot = Any()
    screen_enabled = Bool(False)
    screen_aspect = AspectRatio()
    fixed_x = Bool(False)
    fixed_y = Bool(False)
    traits_view = View(
                    VGroup(
                        HGroup(
                            Item("screen_enabled", label="Screen"),
                            Item("screen_aspect", label="aspect ratio (w/h)")
                            ),
                        HGroup(
                            Item("fixed_x", label="Data X fixed"),
                            Item("fixed_y", label="Data Y fixed")
                            ),
                        Item("plot", editor=ComponentEditor(size=(100,100)), 
                             show_label=False)
                        ),
                    width=600, height=600, resizable=True,
                    title="Aspect Ratio Example")


    def __init__(self, *args, **kw):
        HasTraits.__init__(self, *args, **kw)
        numpoints = 200
        x = linspace(0.0,2.0,numpoints)
        plotdata = ArrayPlotData(x=x, y=sin(x))
        plot = Plot(plotdata)
        plot.plot(("x", "y"), type="scatter")
        plot.tools.append(PanTool(plot))
        plot.overlays.append(ZoomTool(plot))
        self.plot = plot

    def _screen_enabled_changed(self):
        if self.screen_enabled:
            self.plot.aspect_ratio = self.screen_aspect
        else:
            self.plot.aspect_ratio = None
        self.plot.request_redraw()

    def _screen_aspect_changed(self):
        if self.screen_enabled:
            self.plot.aspect_ratio = self.screen_aspect
            self.plot.request_redraw()

    def _fixed_x_changed(self):
        self.plot.x_mapper.stretch_data = not self.fixed_x
        # Also have to change all the renderers' mappers
        for renderer in chain(*self.plot.plots.values()):
            renderer.index_mapper.stretch_data = not self.fixed_x
        self.plot.request_redraw()

    def _fixed_y_changed(self):
        self.plot.y_mapper.stretch_data = not self.fixed_y
        for renderer in chain(*self.plot.plots.values()):
            renderer.value_mapper.stretch_data = not self.fixed_y
        self.plot.request_redraw()

#===============================================================================
# # Create the demo object to be used by the demo.py application.
#===============================================================================
demo = myplot = MyPlot()

if __name__ == "__main__":
    myplot.configure_traits()

# EOF