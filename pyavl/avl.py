'''
Created on Jun 8, 2009

@author: pankaj
'''

import pexpect
import os
from enthought.traits.api import HasTraits, List, Float, Dict, String, Int, Tuple, Enum, cached_property, Python, Property, on_trait_change
from enthought.traits.ui.api import EnumEditor
import re

class RunCase(HasTraits):
    patterns = {'constrained':re.compile(r"""(?P<cmd>[A-Z0-9]+)\s+(?P<pattern>.+?)\s+->\s+(?P<constraint>\S+)\s+=\s+(?P<val>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)"""),
                'constraint':re.compile(r"""(?P<sel>->)?\s*(?P<cmd>[A-Z0-9])+\s+(?P<pattern>.+?)\s+=\s+(?P<val>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)"""),
                'parameter':re.compile(r"""(?P<cmd>[A-Z]+)\s+(?P<pattern>.+?)\s+=\s+(?P<val>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)(\ +(?P<unit>\S+))?"""),
                'var':re.compile(r"""(?P<name>\S+?)\s*?=\s*?(?P<value>[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)""")
                }
    number = Int
    name = String
    output = Dict(String, Float, {})
    
    # name, value
    parameters = Dict(String, Float, {})
    # pattern:name
    parameter_names = Dict(String, String, {})
    # name:(cmd,pattern,unit)
    parameters_info = Dict(String, Tuple(String, String, String), {})
    
    # name:pattern
    constrained_params = Property(Dict(String, String), depends_on='constrained_patterns')
    @cached_property
    def _get_constrained_params(self):
        return self.constrained_patterns.keys()
    
    constrained_patterns = Dict(String, String, {'alpha':'lpha', 'beta':'eta',
                            'roll rate':'oll  rate', 'pitch rate':'itch rate',
                            'yaw rate':'aw   rate'})
    # auto-detect cmd from patterns
    #constrained_cmd = Dict(String, String, {'alpha':'A', 'beta':'B', 'roll rate':'R',
    #                        'pitch rate':'P', 'yaw rate':'Y'})
    constrained_cmd = Property(Dict, depends_on='constrained_patterns')
    @cached_property
    def _get_constrained_cmd(self):
        self.avl.sendline('oper')
        self.avl.expect(AVL.patterns['/oper'])
        self.avl.sendline(str(self.number))
        self.avl.expect(AVL.patterns['/oper'])
        lines = avl.before.readlines()
        lines = [line.strip() for line in lines]
        i1 = lines.index('------------      ------------------------')
        i2 = lines.index('------------      ------------------------', i1 + 1)
        constraint_lines = lines[i1 + 1:i2]
        groups = [re.match(RunCase.patterns['constrained'], line).groupdict() for line in constraint_lines]
        cmds = {}
        patterns = {}
        for group in groups:
            patterns[group['pattern']] = group['cmd']
        for param, pattern in self.constrained_params.iteritems():
            cmds[param] = patterns[pattern]
        AVL.goto_state(self.avl)
        return cmds
    
    # name:pattern
    constraint_vars = Property(Dict(String, String), depends_on='constraint_patterns')
    @cached_property
    def _get_constraint_vars(self):
        return self.constraint_patterns.keys()
    constraint_patterns = Dict(String, String, {'alpha':'alpha', 'beta':'beta',
                            'roll rate':'pb/2V', 'yaw rate':'rb/2V', 'pitch rate':'qc/2V',
                            'lift coeff':'CL', 'side force coeff':'CY', 'roll coeff':'Cl roll mom',
                            'pitch coeff':'Cm pitchmom', 'yaw coeff':'Cn yaw  mom'})
    constraint_cmd = Property(Dict, depends_on='constraint_patterns')
    @cached_property
    def _get_constraint_cmd(self):
        self.avl.sendline('oper')
        self.avl.expect(AVL.patterns['/oper'])
        self.avl.sendline(str(self.number))
        self.avl.expect(AVL.patterns['/oper'])
        self.avl.sendline('a')
        self.avl.expect(AVL.patterns['/oper/a'])
        lines = avl.before.readlines()
        lines = [line.strip() for line in lines]
        i1 = lines.index('- - - - - - - - - - - - - - - - -')
        i2 = lines.index('', i1 + 1)
        constraint_lines = lines[i1 + 1:i2]
        groups = [re.match(RunCase.patterns['constraint'], line).groupdict() for line in constraint_lines]
        cmds = {}
        patterns = {}
        for group in groups:
            patterns[group['pattern']] = group['cmd']
        for param, pattern in self.constrained_params.iteritems():
            cmds[param] = patterns[pattern]
        AVL.goto_state(self.avl)
        return cmds
    
    # constraints are corresponding to to the params in constraint_params
    # constrained, constraint_in, value
    constraints = List(Tuple(String, String, Float),
                                [('alpha', 'alpha', 0.0),
                                ('beta', 'beta', 0.0),
                                ('roll rate', 'roll rate', 0.0),
                                ('yaw rate', 'yaw rate', 0.0),
                                ('pitch rate', 'pitch rate', 0.0),
                            ])
    
    @on_trait_change('constraints')
    def update_constraints(self):
        self.avl.sendline('oper')
        for p, c, v in self.constraints:
            p1 = self.constraint_cmd[p]
            c1 = self.constrained_cmd[c]
            self.avl.sendline('%s %s %f' % (p1, c1, v))
            self.avl.expect(AVL.patterns['/oper'])
        AVL.goto_state(self.avl)
    
    @on_trait_change('parameters')
    def update_parameters(self):
        self.avl.sendline('oper')
        self.avl.sendline('m')
        self.avl.expect(AVL.patterns['/oper/m'])
        for p, v in self.parameters.iteritems():
            cmd = self.parameters_info[p][0]
            self.avl.sendline('%s %f' % (cmd, v))
        AVL.goto_state(self.avl)
    
    @classmethod
    def get_constraint_params_from_avl(cls, avl, case_num=1):
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
        params = [re.search(RunCase.patterns['constraint'], line).group('pattern') for line in constraint_lines]
        AVL.goto_state(avl)
        return params
    
    @classmethod
    def get_constrained_params_from_avl(cls, avl, case_num=1):
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
        params = [re.match(RunCase.patterns['constrained'], line).group('pattern') for line in constraint_lines]
        AVL.goto_state(avl)
        return params
    
    @classmethod
    def get_case_from_avl(cls, avl, case_num):
        # todo: parse constraints and parameters from avl
        constrained_params = RunCase.get_constrained_params_from_avl(avl, case_num)
        runcase = RunCase()
        runcase.avl = avl
        for constrained_param in constrained_params:
            if constrained_param not in runcase.constrained_patterns.values():
                runcase.constrained_patterns[constrained_param] = constrained_param
        constraint_params = RunCase.get_constraint_params_from_avl(avl, case_num)
        for constraint_param in constraint_params:
            if constraint_param not in runcase.constraint_patterns.values():
                runcase.constraint_patterns[constraint_param] = constraint_param
        RunCase.get_parameters_info_from_avl(runcase, avl)
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
        for group in groups:
            pattern = group['pattern']
            name = self.parameter_names.get(pattern, pattern)
            unit = group.get('unit', '')
            unit = unit if unit is not None else ''
            self.parameters_info[name] = (group['cmd'], pattern, unit)
            self.parameters[name] = float(group['val'])
        AVL.goto_state(avl)
        
    def get_output(self):
        self.avl.sendline('oper')
        self.avl.expect(AVL.patterns['/oper'])
        self.avl.sendline('x')
        self.avl.expect(AVL.patterns['/oper'])
        ret = {}
        #print self.avl.before
        i1 = re.search(r"""Run case:\s*?.*?\n""", self.avl.before).end()
        i2 = re.search(r"""---------------------------------------------------------------""", self.avl.before[i1:]).start()
        text = self.avl.before[i1:i1 + i2]
        for match in re.finditer(RunCase.patterns['var'], text):
            ret[match.group('name')] = float(match.group('value'))
        self.output = ret
        return ret
    
class AVL(HasTraits):
    '''
    A class representing an avl program instance.
    '''
    patterns = {'/'     : 'AVL   c>  ',
                '/oper' : re.compile(r"""\.OPER \(case (?P<case_num>\d)/(?P<num_cases>\d)\)   c>  """),
                '/plop' : r'Option, Value   \(or <Return>\)    c>  ',
                '/oper/a': re.compile(r"""Select new  constraint,value  for (?P<param>.*?)\s+c>  """),
                '/oper/m': r'Enter parameter, value  \(or  # - \+ N \)   c>  '
                }
    run_cases = List(RunCase, [])
    state = String('/')
    selected_case = Int
    
    def __init__(self, path='', logfile='/opt/idearesearch/avllog'):
        '''
        Constructor
        path is the directory where avl binary is found
        logfile is where all output is to be logged
        '''
        self.avl = pexpect.spawn(os.path.join(path, 'avl'), logfile=open(logfile, 'w'))
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
        
        
    def disable_plotting(self):
        self.avl.sendline('plop')
        self.avl.sendline('g')
        self.avl.sendline()
        self.avl.expect(AVL.patterns['/'])
    
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
    
    def get_output(self):
        #FIXME: implement
        pass
    
    def populate_runcases(self):
        self.avl.sendline('oper')
        self.avl.expect(AVL.patterns['/oper'])
        num_cases = int(self.avl.match.group('num_cases'))
        AVL.goto_state(self.avl)
        for case_num in xrange(1, num_cases + 1):
            self.run_cases.append(RunCase.get_case_from_avl(self.avl, case_num))
    
    def load_case_from_file(self, filename):
        self.avl.sendline('load %s' % filename)
        AVL.goto_state(self.avl)
        self.populate_runcases()
        