'''
Created on Jul 4, 2009

@author: pankaj
'''

from enthought.traits.api import String, Int, List, Instance
from enthought.traits.ui.api import View, Item, Tabbed, TableEditor, ListEditor, Handler
from enthought.traits.ui.menu import ToolBar, Action, Menu

from pyavl.utils.traitstools import get_file_from_user

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
                    Action(name = "tp",
                        action = "do_it",
                        toolip = "Recalculate the results"),
                    ])
    #def object_runcases_changed(self, uiinfo):
    #    print uiinfo.object, 'runcase name changed'
    def do_it(self, info):
        print 'doing...'
    
    def load_case(self, info):
        avl = info.object.avl
        filename = get_file_from_user(cwd=avl.cwd, filter=['AVL case files (*.avl)|*.avl'])
        if filename:
            avl.load_case_from_file(filename)
            logger.info('loading case from file : %s' %str(filename))
    
    def save_case(self, info):
        case = info.object.avl.case
        filename = get_file_from_user(cwd=case.cwd, filter=['AVL case files (*.avl)|*.avl'])
        if filename:
            f = open(filename, 'w')
            case.write_input_file(f)
        logger.info('saving case to file : %s' %str(filename))
    
    def object_avl_case_changed(self, info):
        logger.info('handler : object_avl_case_changed')