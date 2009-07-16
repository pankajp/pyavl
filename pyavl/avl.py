'''
Created on Jun 8, 2009

@author: pankaj
'''

import pexpect
import os
import re
import numpy

#from pyavl.runcase import RunCase, TrimCase
from pyavl.outpututils import EigenMatrix, EigenMode, RunOutput
from pyavl.case import Case
from pyavl.mass import Mass

from enthought.traits.api import HasTraits, List, Float, Dict, String, Int, Tuple, \
    Enum, cached_property, Python, Property, on_trait_change, Complex, Array, Instance, \
    Directory, ReadOnly, DelegatesTo, Any, Trait, Bool, File
from enthought.traits.ui.api import View, Item, Group, VGroup, ListEditor, TupleEditor, \
    TextEditor, TableEditor, EnumEditor
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.menu import Action, ToolBar
#from pyavl.runcase import RunCase

import logging
# Logging.
logger = logging.getLogger(__name__)


class Parameter(HasTraits):
    name = String
    value = Float
    unit = String
    pattern = String
    cmd = String
    editor = TableEditor(
        auto_size=False,
        #row_height=20,
        columns=[ObjectColumn(name='name', editable=False, label='Parameter'),
                     ObjectColumn(name='value', label='Value', editor=TextEditor(evaluate=float, enter_set=True, auto_set=False)),
                     ObjectColumn(name='unit', editable=False, label='Unit')
                    ])

# This is the object which is constrained
# example alpha is constrained by the condition elevator = 1
# the in this case constrained=elevator
class ConstraintVariable(HasTraits):
    name = String
    pattern = String
    cmd = String

class Constraint(HasTraits):
    name = String
    runcase = Any
    constraint_variables_available = Property(List(String), depends_on='runcase.constraint_variables')
    @cached_property
    def _get_constraint_variables_available(self):
        return self.runcase.constraint_variables.keys()
    #constraint = Instance(ConstraintVariable)
    constraint_name = String
    value = Float
    pattern = String
    cmd = String
    editor = TableEditor(
        auto_size=False,
        columns=[ ObjectColumn(name='name', editable=False, label='Parameter'),
                     ObjectColumn(name='constraint_name', label='Constraint', editor=EnumEditor(name='constraint_variables_available')),
                     ObjectColumn(name='value', label='Value', editor=TextEditor(evaluate=float, enter_set=True, auto_set=False))
                    ])

class TrimCase(HasTraits):
    # Instance(RunCase)
    runcase = Any()
    type = Trait('horizontal flight', {'horizontal flight':'c1',
                  'looping flight':'c2'})
    parameters = Dict(String, Instance(Parameter))
    parameter_view = List(Parameter, [])
    traits_view = View(Group(Item('type')),
                       Group(Item('parameter_view', editor=Parameter.editor, show_label=False), label='Parameters'),
                        Item(), # so that groups are not tabbed
                        kind='livemodal',
                        buttons=['OK']
                       )
    
    #@on_trait_change('type,parameters.value')
    def update_parameters_from_avl(self):
        #print 'in update_parameters_from_avl'
        avl = self.runcase.avl
        avl.sendline('oper')
        avl.expect(AVL.patterns['/oper'])
        avl.sendline(self.type_)
        avl.expect(AVL.patterns['/oper/m'])
        
        constraint_lines = [line.strip() for line in avl.before.splitlines()]
        i1 = constraint_lines.index('=================================================')
        constraint_lines = constraint_lines[i1:]
        #print constraint_lines
        groups = [re.search(RunCase.patterns['parameter'], line) for line in constraint_lines]
        params = {}
        for group in groups:
            if group is not None:
                group = group.groupdict()
                pattern = group['pattern']
                name = pattern
                unit = group.get('unit', '')
                unit = unit if unit is not None else ''
                params[name] = Parameter(name=name, pattern=pattern, cmd=group['cmd'], unit=unit, value=float(group['val']))
        AVL.goto_state(avl)
        self.parameters = params
        self.parameter_view = sorted(params.values(), key=lambda x:x.name.upper())
        return self

class RunCase(HasTraits):
    patterns = {'name':re.compile(r"""Operation of run case (?P<case_num>\d+)/(?P<num_cases>\d+):\s*(?P<case_name>.+?)\ *?\n"""),
                'constraint':re.compile(r"""(?P<cmd>[A-Z0-9]+)\s+(?P<pattern>.+?)\s+->\s+(?P<constraint>\S+)\s+=\s+(?P<val>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)"""),
                'constraint_variable':re.compile(r"""(?P<sel>->)?\s*(?P<cmd>[A-Z0-9]+)\s+(?P<pattern>.+?)\s+=\s+(?P<val>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)"""),
                'parameter':re.compile(r"""(?P<cmd>[A-Z]+)\s+(?P<pattern>.+?)\s+=\s+(?P<val>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)(\ +(?P<unit>\S+))?"""),
                'var':re.compile(r"""(?P<name>\S+?)\s*?=\s*?(?P<value>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)"""),
                'float':re.compile(r'(?P<value>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)'),
                'mode' :re.compile(r"""mode (\d+?):\s*?(?P<real>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)\s+(?P<imag>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)"""),
                'modeveccomp': re.compile(r"""(?P<name>[a-z]+?)(\s*?):\s*(?P<real>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)\s+(?P<imag>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)""")
                }
    number = Int
    name = String
    runoutput = Instance(RunOutput, RunOutput())# Dict(String, Float, {})
    #not to be used separately apart from modal gui
    #trim_runcase = Instance(TrimCase, TrimCase())
    set_trim_case_action = Action(name='Set Trim Condition', action='set_trimcase', \
                tooltip='Set the runcase conditions for horizontal(+banked) or looping trim condition')
    parameter_view = Property(List(Parameter), depends_on='parameters[]')
    constraint_view = Property(List(Constraint), depends_on='constraints[]')
    @cached_property
    def _get_parameter_view(self):
        return sorted(self.parameters.values(), key=lambda x:x.name.upper())
    @cached_property
    def _get_constraint_view(self):
        return sorted(self.constraints.values(), key=lambda x:x.name.upper())
    
    traits_view = View(Group(Item('number', style='readonly'),
                             Item('name')),
                       Group(Item('parameter_view', editor=Parameter.editor, show_label=False), label='Parameters'),
                       Group(Item('constraint_view', editor=Constraint.editor, show_label=False), label='Constraints'),
                        Item(), # so that groups are not tabbed
                        toolbar=ToolBar(set_trim_case_action)
                       )
    
    # name, value
    parameters = Dict(String, Instance(Parameter), {})
    # pattern:name ; Predefined parameters to have good names
    parameter_names = Dict(String, String, {})
    
    
    
    # constraints are corresponding to to the params in constraint_names
    # constrained : constraint_name, value
    constraints = Dict(String, Instance(Constraint), {})
    
    # pattern:name
    constraint_names = Dict(String, String, {'lpha':'alpha', 'eta':'beta',
                            'oll  rate':'roll rate', 'itch rate':'pitch rate',
                            'aw   rate':'yaw rate'})
    
    constraint_variables = Dict(String, Instance(ConstraintVariable), {})
    
    constraint_variable_names = Dict(String, String, {'CL': 'lift coeff',
                                             'CY': 'side force coeff',
                                             'Cl roll mom': 'roll coeff',
                                             'Cm pitchmom': 'pitch coeff',
                                             'Cn yaw  mom': 'yaw coeff',
                                             'alpha': 'alpha',
                                             'beta': 'beta',
                                             'pb/2V': 'roll rate',
                                             'qc/2V': 'pitch rate',
                                             'rb/2V': 'yaw rate'})
    
    trimcase = Instance(TrimCase, TrimCase())
    
    def set_trimcase(self, info=None):
        #print self
        self.trimcase = TrimCase(runcase=self)
        self.trimcase.update_parameters_from_avl()
        self.trimcase.edit_traits()
        self.get_parameters_info_from_avl(self.avl)
    
    @on_trait_change('trimcase.parameter_view.value,trimcase.type')
    def on_trimcase_changed(self, object, name, old, new):
        #print object, name, old, new
        print 'trimcase_changed'
        if name == 'value':
            self.update_trim_case(self.trimcase, object)
            self.trimcase.update_parameters_from_avl()
        elif name == 'type':
            self.trimcase.update_parameters_from_avl()
    
    # send changed value of trimcase to avl, parameter is Parameter instance
    def update_trim_case(self, trimcase, parameter):
        #print 'update_trim_case'
        self.get_parameters_info_from_avl(self.avl)
        self.avl.sendline('oper')
        self.avl.sendline(trimcase.type_)
        self.avl.expect(AVL.patterns['/oper/m'])
        #print self.parameters.keys()
        #for p, v in trimcase.parameters.iteritems():
        self.avl.sendline('%s %f' % (parameter.cmd, parameter.value))
        AVL.goto_state(self.avl)
    
    @on_trait_change('constraints.value,constraints.constraint_name')
    def update_constraints(self):
        print 'constraints changed'
        #self.avl.sendline('oper')
        #self.avl.sendline()
        #self.avl.expect(AVL.patterns['/'])
        for name, constraint in self.constraints.iteritems():
            ccmd = constraint.cmd
            vcmd = self.constraint_variables[constraint.constraint_name].cmd
            val = constraint.value
            self.avl.sendline('oper')
            self.avl.expect(AVL.patterns['/oper'])
            self.avl.sendline('%s %s %f' % (ccmd, vcmd, val))
            self.avl.expect(AVL.patterns['/oper'])
        AVL.goto_state(self.avl)
    
    @on_trait_change('parameters.value')
    def update_parameters(self):
        print 'parameters changed'
        self.avl.sendline('oper')
        self.avl.sendline('m')
        self.avl.expect(AVL.patterns['/oper/m'])
        #print self.parameters.keys()
        try:
            tmpv = self.parameters['velocity'].value
            if tmpv < 0.00001:
                tmpv = 1.0
        except KeyError:
            tmpv = 1.0
        self.avl.sendline('V %f' % tmpv)
        for p, v in self.parameters.iteritems():
            cmd = self.parameters[p].cmd
            if cmd != 'V':
                self.avl.sendline('%s %f' % (cmd, v.value))
        AVL.goto_state(self.avl)
    
    #returns pattern:cmd
    @classmethod
    def get_constraint_variables_from_avl(cls, avl, case_num=1):
        avl.sendline('oper')
        avl.expect(AVL.patterns['/oper'])
        avl.sendline(str(case_num))
        avl.expect(AVL.patterns['/oper'])
        avl.sendline('a')
        avl.expect(AVL.patterns['/oper/a'])
        if avl.match.groups('case_num') != str(case_num):
            #raise Exception('could not get case information for case num %d' % case_num)
            pass
        lines = avl.before.splitlines()
        lines = [line.strip() for line in lines]
        i1 = lines.index('- - - - - - - - - - - - - - - - -')
        i2 = lines.index('', i1 + 1)
        constraint_lines = lines[i1 + 1:i2]
        groups = [re.search(RunCase.patterns['constraint_variable'], line).groupdict() for line in constraint_lines]
        params = {}
        for group in groups:
            params[group['pattern']] = group['cmd']
        avl.sendline()
        AVL.goto_state(avl)
        return params
    
    # return pattern:cmd,con_pattern,value
    @classmethod
    def get_constraints_from_avl(cls, avl, case_num=1):
        avl.sendline('oper')
        avl.expect(AVL.patterns['/oper'])
        avl.sendline(str(case_num))
        avl.expect(AVL.patterns['/oper'])
        if avl.match.groups('case_num') != str(case_num):
            #raise Exception('could not get case information for case num %d' % case_num)
            pass
        lines = avl.before.splitlines()
        lines = [line.strip() for line in lines]
        i1 = lines.index('------------      ------------------------')
        i2 = lines.index('------------      ------------------------', i1 + 1)
        constraint_lines = lines[i1 + 1:i2]
        groups = [re.match(RunCase.patterns['constraint'], line).groupdict() for line in constraint_lines]
        params = {}
        for group in groups:
            params[group['pattern']] = (group['cmd'], group['constraint'], group['val'])
        AVL.goto_state(avl)
        return params
    
    @classmethod
    def get_case_from_avl(cls, avl, case_num=1):
        # TODO: parse constraints and parameters from avl
        avl.sendline('oper')
        avl.expect(AVL.patterns['/oper'])
        avl.sendline(str(case_num))
        avl.expect(AVL.patterns['/oper'])
        match = re.search((RunCase.patterns['name']), avl.before)
        name = match.group('case_name').strip()
        AVL.goto_state(avl)
        runcase = RunCase(name=name, number=case_num)
        runcase.avl = avl
        
        constraint_vars = RunCase.get_constraint_variables_from_avl(avl, case_num)
        for constraint_var in constraint_vars:
            if constraint_var not in runcase.constraint_variable_names:
                runcase.constraint_variable_names[constraint_var] = constraint_var
            constraint_name = runcase.constraint_variable_names[constraint_var]
            runcase.constraint_variables[constraint_name] = ConstraintVariable(
                                name=constraint_name, pattern=constraint_var,
                                cmd=constraint_vars[constraint_var])
        
        constraints = RunCase.get_constraints_from_avl(avl, case_num)
        rc_constraints = {}
        for constraint_pattern, constraint_info in constraints.iteritems():
            if constraint_pattern not in runcase.constraint_names:
                runcase.constraint_names[constraint_pattern] = constraint_pattern
            constraint_name = runcase.constraint_names[constraint_pattern]
            rc_constraints[constraint_name] = Constraint(name=constraint_name,
                                pattern=constraint_pattern, cmd=constraint_info[0],
                                constraint_name=runcase.constraint_variable_names[constraint_info[1]],
                                value=float(constraint_info[2]), runcase=runcase)
        runcase.constraints.update(rc_constraints)
        RunCase.get_parameters_info_from_avl(runcase, avl)
        AVL.goto_state(avl)
        return runcase
        
    def get_parameters_info_from_avl(self, avl):
        avl.sendline('oper')
        avl.expect(AVL.patterns['/oper'])
        avl.sendline('m')
        avl.expect(AVL.patterns['/oper/m'])
        avl.sendline()
        lines = avl.before.splitlines()
        lines = [line.strip() for line in lines if len(line.strip()) > 0]
        l2 = [line.startswith('Parameters') for line in lines]
        i1 = l2.index(True)
        i2 = - 1
        constraint_lines = lines[i1 + 1:i2]
        groups = [re.search(RunCase.patterns['parameter'], line).groupdict() for line in constraint_lines]
        params = {}
        AVL.goto_state(avl)
        #params.update(self.parameters)
        for group in groups:
            pattern = group['pattern']
            name = self.parameter_names.get(pattern, pattern)
            unit = group.get('unit', '')
            unit = unit if unit is not None else ''
            params[name] = Parameter(name=name, pattern=pattern, cmd=group['cmd'], unit=unit, value=float(group['val']))
        #self.parameters[name] = float(group['val'])
        AVL.goto_state(avl)
        self.parameters.update(params)
        #self.parameters = params
        
    def get_run_output(self):
        self.avl.sendline('oper')
        self.avl.expect(AVL.patterns['/oper'])
        self.avl.sendline('x')
        self.avl.expect(AVL.patterns['/oper'])
        ret = {}
        #print self.avl.before
        i1 = re.search(r"""Run case:\s*?.*?\n""", self.avl.before).end()
        i2 = re.search(r"""---------------------------------------------------------------""", self.avl.before[i1:]).start()
        text = self.avl.before[i1:i1 + i2]
        AVL.goto_state(self.avl)
        for match in re.finditer(RunCase.patterns['var'], text):
            ret[match.group('name')] = float(match.group('value'))
        #self.output = ret
        AVL.goto_state(self.avl)
        return ret
    
    def get_modes(self):
        self.avl.sendline('mode')
        self.avl.expect(AVL.patterns['/mode'])
        self.avl.sendline('n')
        self.avl.expect(AVL.patterns['/mode'])
        if re.search(r'Eigenmodes not computed for run case', self.avl.before):
            print 'Error : \n', self.avl.before
            AVL.goto_state(avl)
            return
        ret = {}
        i1 = re.search(r"""Run case\s*?\d+?:.*?\n""", self.avl.before).end()
        i2 = re.search(r"""Run-case parameters for eigenmode analyses""", self.avl.before[i1:]).start()
        text = self.avl.before[i1 : i1 + i2]
        modes = []
        for mode_eval in re.finditer(RunCase.patterns['mode'], text):
            eigenvalue = float(mode_eval.group('real')) + 1j * float(mode_eval.group('imag'))
            mode = EigenMode(eigenvalue=eigenvalue)
            i = 0
            for match in re.finditer(RunCase.patterns['modeveccomp'], text[mode_eval.end():]):
                i += 1
                mode.eigenvector[mode.order.index(match.group('name'))] = float(mode_eval.group('real')) + 1j * float(mode_eval.group('imag'))
                if i > 11:
                    break
            modes.append(mode)
        AVL.goto_state(self.avl)
        return modes
    
    def get_system_matrix(self):
        self.avl.sendline('mode')
        self.avl.expect(AVL.patterns['/mode'])
        self.avl.sendline('n')
        self.avl.expect(AVL.patterns['/mode'])
        self.avl.sendline('s')
        self.avl.expect(AVL.patterns['/mode/s'])
        lines = [line for line in self.avl.before.splitlines()[3: - 1] if len(line) > 0]
        lines = [line.replace('**********', '      nan ') for line in lines]
        #print lines
        # fortran format to deceode
        # FORMAT(1X,12F10.4,3X,12G12.4)
        # 1 space, 12 floats of fixed width 10, 3 spaces 12 exponents of fixed width 12
        order = lines[0].replace('|', ' ').split()
        mat = numpy.empty((12, len(order)))
        for i, line in enumerate(lines[1:]):
            l1 = line[1:121]
            for j in xrange(12):
                mat[i, j] = float(l1[j * 10:(j + 1) * 10])
            l2 = line[124:]
            for j in xrange(len(l2) / 12):
                mat[i, 12 + j] = float(l2[j * 12:(j + 1) * 12])
        ret = EigenMatrix(order=order, matrix=mat)
        AVL.goto_state(self.avl)
        return ret


class AVL(HasTraits):
    '''
    A class representing an avl program instance.
    '''
    patterns = {'/'     : 'AVL   c>  ',
                '/oper' : re.compile(r"""\.OPER \(case (?P<case_num>\d)/(?P<num_cases>\d)\)   c>  """),
                '/plop' : r'Option, Value   \(or <Return>\)    c>  ',
                '/oper/a': re.compile(r"""Select new  constraint,value  for (?P<param>.*?)\s+c>  """),
                '/oper/m': r'Enter parameter, value  \(or  # - \+ N \)   c>  ',
                '/mode' : r'\.MODE   c>  ',
                '/mode/s': r'Enter output filename \(or <Return>\):',
                'num'   : r'(?P<val>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)'
                }
    run_cases = List(RunCase, [])
    state = String('/')
    selected_runcase = Int(1)
    case = Instance(Case)
    case_filename = File()
    mass = Instance(Mass)
    cwd = Directory
    #runoutput = Instance(RunOutput)
    
    traits_view = View(Item('selected_runcase'))
    
    def _selected_case_changed(self):
        self.avl.sendline('oper')
        self.avl.sendline(str(self.selected_case))
        AVL.goto_state(self.avl)
    
    def __init__(self, path='', cwd='', logfile='avl.log'):
        '''
        Constructor
        path is the directory where avl binary is found
        cwd is the working dir, where all the case related files are expected to be found (eg airfoil files)
        logfile is where all output is to be logged
        '''
        self.avl = pexpect.spawn(os.path.join(path, 'avl'), logfile=open(logfile, 'w'), cwd=cwd)
        self.avl.timeout = 10
        self.cwd = cwd
        self.disable_plotting()
        
    def execute_case(self, case_num=None):
        # TODO: implement
        if case_num is None:
            case_num = self.selected_case
        self.avl.sendline('oper')
        self.avl.expect(AVL.patterns['/oper'])
        self.avl.sendline(str(case_num))
        self.avl.expect(AVL.patterns['/oper'])
        self.avl.sendline('x')
        AVL.goto_state(self.avl)
        
        
    def disable_plotting(self):
        self.avl.sendline('plop')
        self.avl.sendline('g')
        AVL.goto_state(self.avl)
    
    @classmethod
    def goto_state(cls, avl, state='/'):
        for i in xrange(6):
            avl.sendline('')
            try:
                avl.expect(AVL.patterns['/'], timeout=1)
                return
            except pexpect.TIMEOUT:
                pass
        raise Exception('Can\'t reach base state')
    
    
    def populate_runcases(self):
        self.avl.sendline('oper')
        self.avl.expect(AVL.patterns['/oper'])
        num_cases = int(self.avl.match.group('num_cases'))
        AVL.goto_state(self.avl)
        runcases = []
        for case_num in xrange(1, num_cases + 1):
            runcases.append(RunCase.get_case_from_avl(self.avl, case_num))
        self.run_cases = runcases
        self.selected_case = 1
    
    def load_case_from_file(self, filename):
        self.avl.sendline('load %s' % filename)
        self.case_filename = filename
        if os.path.isabs(filename):
            f = open(filename)
        else:
            f = open(os.path.join(self.cwd, filename))
        self.case = Case.case_from_input_file(f, cwd=self.cwd)
        f.close()
        AVL.goto_state(self.avl)
        self.populate_runcases()
    
    def load_mass_from_file(self, filename):
        self.mass = Mass.mass_from_file(filename)

def create_default_avl(*args, **kwargs):
    avl = AVL(cwd='/opt/idearesearch/avl/runs/')
    avl.load_case_from_file('/opt/idearesearch/avl/runs/vanilla.avl')
    from pyavl.runutils import RunConfig
    rc = RunConfig(runcase=RunCase.get_case_from_avl(avl.avl))
    runoutput = rc.run(progressbar=False)
    avl.run_cases[0].runoutput = runoutput
    return avl


if __name__ == '__main__':
    tc = TrimCase()
    print '{'
    for k, v in tc.parameters.iteritems():
        print '"' + k + '" : Parameter(name="' + v.name + '",value="' + str(v.value) + '",pattern="' + v.pattern + '",cmd="' + v.cmd + '",unit="' + v.unit + '"),'
    print '}'
