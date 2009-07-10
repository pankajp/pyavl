'''
Created on Jul 8, 2009

@author: pankaj
'''

import numpy

from pyavl.avl import AVL, RunCase, Parameter, Constraint, TrimCase

from enthought.traits.api import HasTraits, Instance, Trait, Property, String, \
    cached_property, Enum, Float, Int, Array, List, Any, on_trait_change, Expression, \
    PrototypedFrom, DelegatesTo
from enthought.traits.ui.api import View, Item, Group, ListEditor, EnumEditor, \
    InstanceEditor, HGroup, TableEditor, TextEditor, Include, HSplit, VSplit
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.menu import Action

class ParameterConfig(HasTraits):
    parameter = Instance(Parameter)
    expr = Expression()
    def __init__(self, *args, **kwargs):
        super(ParameterConfig, self).__init__(*args, **kwargs)
        self.expr = str(self.parameter.value)
    editor = TableEditor(
        auto_size=False,
        columns=[ ObjectColumn(name='parameter.name', editable=False, label='Parameter'),
                     ObjectColumn(name='expr', label='Expression'),
                     ObjectColumn(name='parameter.unit', editable=False, label='Unit')
                    ])

class ConstraintConfig(HasTraits):
    constraint = Instance(Constraint)
    expr = Expression()
    def __init__(self, *args, **kwargs):
        super(ConstraintConfig, self).__init__(*args, **kwargs)
        self.expr = str(self.constraint.value)
    constraint_variables_available = DelegatesTo('constraint')
    editor = TableEditor(
        auto_size=False,
        columns=[ ObjectColumn(name='constraint.name', editable=False, label='Parameter'),
                     ObjectColumn(name='constraint.constraint_name', label='Constraint', editor=EnumEditor(name='constraint_variables_available')),
                     ObjectColumn(name='expr', label='Expression')
                    ])

class CaseConfig(HasTraits):
    runcase = Instance(RunCase)
    constraint_config = Property(List(ConstraintConfig), depends_on='runcase.constraints[]')
    @cached_property
    def _get_constraint_config(self):
        constraints = sorted(self.runcase.constraints.values(), key=lambda x:x.name.upper())
        return [ConstraintConfig(constraint=c) for c in constraints]
    x_range_min = Float(0)
    x_range_max = Float(1)
    x_num_pts = Int(2)
    x_range_type = Trait('Linear', {'Linear':numpy.linspace, 'Log':numpy.logspace})
    x = Property(Array(numpy.float), depends_on='x_range_min,x_range_max,x_num_pts,x_range_type')
    @cached_property
    def _get_x(self):
        return self.x_range_type_(self.x_range_min, self.x_range_max, self.x_num_pts)
    traits_view = View(HGroup(Include('custom_group'),
                                     Group(Item('constraint_config', editor=ConstraintConfig.editor, show_label=False), label='Constraints')),
                        Group(HGroup(Item('x_range_min', label='From'),
                                    Item('x_range_max', label='To')),
                                    HGroup(Item('x_num_pts', label='Points'),
                                    Item('x_range_type', label='Spacing')), label='Variable x'),
                        Item()
                       )

class AdvCaseConfig(CaseConfig):
    parameter_config = Property(List(ParameterConfig), depends_on='runcase.parameters[]')
    @cached_property
    def _get_parameter_config(self):
        params = sorted(self.runcase.parameters.values(), key=lambda x:x.name.upper())
        return [ParameterConfig(parameter=p) for p in params]
    custom_group = Group(Item('parameter_config', editor=ParameterConfig.editor, show_label=False), label='Parameters')
    

class TrimCaseConfig(CaseConfig):
    trimcase = Instance(TrimCase, TrimCase())
    #runcase = DelegatesTo('trimcase')
    varying_param = String
    varying_expr = Expression
    param_name_list = Property(List(String), depends_on='trimcase.parameters')
    @cached_property
    def _get_param_name_list(self):
        return sorted(self.trimcase.parameters.keys(), key=lambda x:x.lower())
    
    @on_trait_change('trimcase.parameter_view.value,trimcase.type')
    def on_trimcase_changed(self, object, name, old, new):
        print object, name, old, new
        print 'trimcase_changed'
        if name == 'value':
            self.trimcase.runcase.update_trim_case(self.trimcase, object)
            self.trimcase.update_parameters_from_avl()
        elif name == 'type':
            self.trimcase.update_parameters_from_avl()
            self.param_name_list[0]
    
    # send changed value of trimcase to avl, parameter is Parameter instance
    def update_trim_case(self, trimcase, parameter):
        print 'update_trim_case'
        self.get_parameters_info_from_avl(self.avl)
        self.avl.sendline('oper')
        self.avl.sendline(trimcase.type_)
        self.avl.expect(AVL.patterns['/oper/m'])
        #print self.parameters.keys()
        #for p, v in trimcase.parameters.iteritems():
        self.avl.sendline('%s %f' % (parameter.cmd, parameter.value))
        AVL.goto_state(self.avl)
    
    custom_group = Group(Item('object.trimcase.type'),
                         Group(Item('object.trimcase.parameter_view', editor=Parameter.editor, show_label=False, height=0.4), label='Parameters', scrollable=True),
                         #Item('trimcase', style='custom', show_label=False),
                         Group(Item('varying_param', editor=EnumEditor(name='param_name_list')),
                               Item('varying_expr', label='Expression')))
    
class RunView(HasTraits):
    runcase = Instance(RunCase)
    runcase_config = Instance(CaseConfig)
    def _runcase_config_default(self):
        return AdvCaseConfig(runcase=self.runcase)
    runtype = Trait('advanced', {'trim flight':'c', 'advanced':'m'})
    
    def _runtype_changed(self, name, old, new):
        if self.runtype_ == 'm':
            self.runcase_config = AdvCaseConfig(runcase=self.runcase)
        else:
            if isinstance(self.runcase_config, TrimCaseConfig):
                self.runcase_config.trimcase.type = new
            else:
                trimcase = TrimCase(runcase=self.runcase)
                trimcase.update_parameters_from_avl()
                self.runcase_config = TrimCaseConfig(runcase=self.runcase, trimcase=trimcase)
    
    run_action = Action(action='run')
    
    #option_view = Property(Any, depends_on='option_type')
    view = View(Item('runtype'),
                Group(Item('runcase_config', editor=InstanceEditor(), style='custom', show_label=False)),
                resizable=True)
    
if __name__ == '__main__':
    avl = AVL(cwd='/opt/idearesearch/avl/runs/')
    filename = '/opt/idearesearch/avl/runs/allegro.avl'
    avl.load_case_from_file(filename)
    rv = RunView(runcase=RunCase.get_case_from_avl(avl.avl))
    rv.configure_traits()