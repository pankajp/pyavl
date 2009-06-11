'''
Created on Jun 8, 2009

@author: pankaj
'''

import pexpect
import os

class AVL(object):
    '''
    A class representing an avl program instance.
    '''
    patterns = {'/':'AVL   c>  '}

    def __init__(self, path='', logfile='/opt/idearesearch/avllog'):
        '''
        Constructor
        path is the directory where avl binary is found
        logfile is where all output is to be logged
        '''
        self.avl = pexpect.spawn(os.path.join(path, 'avl'), logfile=open(logfile,'w'))
        self.disable_plotting()
        
    def disable_plotting(self):
        self.avl.sendline('plop')
        self.avl.sendline('g')
        self.avl.sendline('')
        