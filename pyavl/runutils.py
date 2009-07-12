'''
Created on Jul 8, 2009

@author: pankaj
'''

import numpy

from pyavl.outpututils import RunOutput
from pyavl.avl import RunCase, Parameter, Constraint, TrimCase
from pyavl.avl import AVL

from enthought.pyface.api import ProgressDialog, GUI, ApplicationWindow
from enthought.traits.api import HasTraits, Instance, Trait, Property, String, \
    cached_property, Enum, Float, Int, Array, List, Any, on_trait_change, Expression, \
    PrototypedFrom, DelegatesTo, Button, Bool
from enthought.traits.ui.api import View, Item, Group, ListEditor, EnumEditor, \
    InstanceEditor, HGroup, TableEditor, TextEditor, Include, HSplit, VSplit, ButtonEditor, spring
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.menu import Action, OKButton, CancelButton, CloseAction

import logging
# Logging.
logger = logging.getLogger(__name__)

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

class RunOptionsConfig(HasTraits):
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
                                    Item('x_range_max', label='To'),
                                    Item('x_num_pts', label='Points'),
                                    Item('x_range_type', label='Spacing')), label='Variable x'),
                        Item()
                       )

class AdvCaseConfig(RunOptionsConfig):
    parameter_config = Property(List(ParameterConfig), depends_on='runcase.parameters[]')
    @cached_property
    def _get_parameter_config(self):
        params = sorted(self.runcase.parameters.values(), key=lambda x:x.name.upper())
        return [ParameterConfig(parameter=p) for p in params]
    custom_group = Group(Item('parameter_config', editor=ParameterConfig.editor, show_label=False), label='Parameters')
    

class TrimCaseConfig(RunOptionsConfig):
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
    
class RunConfig(HasTraits):
    runcase = Instance(RunCase)
    runcase_config = Instance(RunOptionsConfig)
    def _runcase_config_default(self):
        return AdvCaseConfig(runcase=self.runcase)
    runtype = Trait('advanced', {'trim flight':'c', 'advanced':'m'})
    eigenmode = Bool(False)
    eigenmatrix = Bool(False)
    def _eigenmatrix_changed(self):
        if self.eigenmatrix:
            self.eigenmode = True
    def _eigenmode_changed(self):
        if not self.eigenmode:
            self.eigenmode = False
    
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
    
    run_button = Button(label='Run Calculation')
    view = View(Item('runtype'),
                Group(Item('runcase_config', editor=InstanceEditor(), style='custom', show_label=False)),
                HGroup(Item('eigenmode'), Item('eigenmatrix')),
                       #spring, Item('run_button', show_label=False)),
                buttons=['OK','Close'],
                resizable=True)
    
    def get_constraints(self):
        consts, vars = {}, {}
        for cc in self.runcase_config.constraint_config:
            cmd = '%s %s {0}' % (cc.constraint.cmd, self.runcase.constraint_variables[cc.constraint.constraint_name].cmd)
            if 'x' in cc.expr_.co_names:
                vars[cmd] = cc.expr_
            else:
                consts[cmd] = cc.expr_
        return consts, vars
    
    def get_parameters(self):
        consts, vars = {}, {}
        if self.runtype_ == 'm':
            type = 'm'
            for pc in self.runcase_config.parameter_config:
                cmd = '%s {0}' % pc.parameter.cmd
                if 'x' in pc.expr_.co_names:
                    vars[cmd] = pc.expr_
                else:
                    consts[cmd] = pc.expr_
        else:
            type = self.runcase_config.trimcase.type_ # type of parameter, cmd to be set in oper menu to set the parameter
            vpn = self.runcase_config.varying_param # varying parameter name
            for n, p in self.runcase_config.trimcase.parameters.iteritems(): # name, parameter
                if n != vpn:
                    consts['%s {0}' % p.cmd] = compile(str(p.value), '<string>', 'eval')
            vp = self.runcase_config.trimcase.parameters[vpn]
            vars['%s {0}' % vp.cmd] = self.runcase_config.varying_expr_
        return type, consts, vars
    
    
    @on_trait_change('run_button')
    def run(self):
        consts_c, vars_c = self.get_constraints()
        type_p, consts_p, vars_p = self.get_parameters()
        # confirm that we are in good state
        avl = self.runcase.avl
        avl.sendline()
        avl.expect(AVL.patterns['/'])
        avl.sendline('oper')
        avl.expect(AVL.patterns['/oper'])
        # first set the constants once and for all
        # constraints
        for c, v in consts_c.iteritems():
            avl.sendline(c.format(eval(v)))
        # paramters
        avl.sendline(type_p)
        for p, v in consts_p.iteritems():
            avl.sendline(p.format(eval(v)))
        avl.sendline()
        avl.sendline()
        avl.expect(AVL.patterns['/'])
        
        outs, modes, matrices = [], [], []
        # now run the case and get output while changing the vars each time
        progress = ProgressDialog(title="progress", message="calculating...", max=self.runcase_config.x.shape[0] - 1, show_time=True, can_cancel=True)
        try:
            progress.open()
        except Exception, e:
            logger.critical(e)
        print 'x[] = ', self.runcase_config.x
        for i, x in enumerate(self.runcase_config.x):
            # set the variables
            avl.sendline('oper')
            avl.expect(AVL.patterns['/oper'])
            # constraints
            print 'running case %d for x=%f' %(i+1,x)
            for c, v in vars_c.iteritems():
                avl.sendline(c.format(eval(v)))
            # paramters
            avl.sendline(type_p)
            for p, v in vars_p.iteritems():
                avl.sendline(p.format(eval(v)))
            avl.sendline()
            
            # go back to home state
            avl.sendline()
            avl.expect(AVL.patterns['/'])
            # get the output
            try:
                outs.append(self.runcase.get_run_output())
                
                if self.eigenmode:
                    modes.append(self.runcase.get_modes())
                if self.eigenmatrix:
                    matrices.append(self.runcase.get_system_matrix())
                
            except AttributeError, e:
                print logger.critical(e)
            #cont, skip = progress.update(i)
            #if not cont or skip:
            #    break
        
        out = RunOutput()
        var_names = {}
        num_vars = 0
        if len(outs) > 0:
            # get output variables
            for i, n in enumerate(outs[0].keys()):
                var_names[n] = i
            num_vars = i+1
            variable_names = sorted(var_names.keys(), key=lambda x:var_names[x])
            vars = numpy.empty((len(outs),num_vars))
            for i,out in enumerate(outs):
                for n,v in out.iteritems():
                    vars[i,var_names[n]] = v
        
        output = RunOutput(variable_names=variable_names, variable_values=vars, eigenmodes=modes, eigenmatrices=matrices)
        
        return output

if __name__ == '__main__':
    avl = AVL(cwd='/opt/idearesearch/avl/runs/')
    filename = '/opt/idearesearch/avl/runs/allegro.avl'
    avl.load_case_from_file(filename)
    rv = RunConfig(runcase=RunCase.get_case_from_avl(avl.avl))
    print rv.configure_traits(kind='livemodal')
    print 'rv configured'
    #gui = GUI()
    #window = ApplicationWindow()
    #window.open()
    #print 'window opened'
    output = rv.run()
    print output
    print 'rv ran'
    #gui.start_event_loop()
    #print 'main loop finished'