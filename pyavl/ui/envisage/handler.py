'''
Created on Jul 4, 2009

@author: pankaj
'''

from pyavl.utils.traitstools import get_file_from_user
from pyavl.runutils import RunConfig

from enthought.traits.api import String, Int, List, Instance
from enthought.traits.ui.api import View, Item, Tabbed, TableEditor, ListEditor, Handler
from enthought.traits.ui.menu import ToolBar, Action, Menu

import logging
# Logging.
logger = logging.getLogger(__name__)

class AVLHandler(Handler):
    '''
    Handler for all gui events
    '''
    toolbar_actions = List(Action,[Action(name = "Load Case",
                        action = "load_case",
                        toolip = "Load an AVL case from file"),
                    Action(name = "Save Case",
                        action = "save_case",
                        toolip = "Save AVL case to file"),
                    Action(name = "Run...",
                        action = "run_config",
                        toolip = "Recalculate the results"),
                    ])
    #def object_runcases_changed(self, uiinfo):
    #    print uiinfo.object, 'runcase name changed'
    def run_config(self, info):
        print 'running...'
        runcase = info.object.avl.run_cases[0]
        runcaseconfig = RunConfig(runcase=runcase)
        out = runcaseconfig.configure_traits(kind='livemodal')
        if not out:
            return
        output = runcaseconfig.run()
        runcase.runoutput.variable_names = output.variable_names
        runcase.runoutput.variable_values = output.variable_values
        runcase.runoutput.eigenmodes = output.eigenmodes
        runcase.runoutput.eigenmatrix = output.eigenmatrix

    
    def load_case(self, info):
        avl = info.object.avl
        filename = get_file_from_user(cwd=avl.case_filename, filter=['AVL case files (*.avl)|*.avl'])
        if filename:
            avl.load_case_from_file(filename)
            logger.info('loading case from file : %s' %str(filename))
    
    # NOTE: it also reloads the case into avl
    def save_case(self, info):
        case = info.object.avl.case
        filename = get_file_from_user(cwd=case.case_filename, filter=['AVL case files (*.avl)|*.avl'])
        if filename:
            f = open(filename, 'w')
            case.write_input_file(f)
            f.flush()
            f.close()
        logger.info('saving case to file : %s' %str(filename))
        info.object.avl.load_case_from_file(filename)
        logger.info('reloading case into avl : %s' %str(filename))
        
    
    def object_avl_case_changed(self, info):
        logger.info('handler : object_avl_case_changed')