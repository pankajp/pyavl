'''
Created on Jul 2, 2009

@author: pankaj

The AVL plugin
'''

# Enthought library imports.
from enthought.envisage.api import Plugin, ServiceOffer
from enthought.traits.api import List


class AVLPlugin(Plugin):
    """ The pyAVL plugin.

    This plugin is part of the 'pyAVL' application.

    """

    # Extension points Ids.
    SERVICE_OFFERS = 'enthought.envisage.service_offers'

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = 'pyavl.ui.envisage'

    # The plugin's name (suitable for displaying to the user).
    name = 'pyAVL'

    #### Contributions to extension points made by this plugin ################

    # Service offers.
    service_offers = List(contributes_to=SERVICE_OFFERS)

    def _service_offers_default(self):
        """ Trait initializer. """
        avl_service_offer = ServiceOffer(
            protocol='pyavl.avl.AVL',
            factory='pyavl.avl.create_default_avl'
        )
        
        def create_default_runoutput(*args, **kwargs):
            avl = AVL(cwd='/opt/idearesearch/avl/runs/')
            avl.load_case_from_file('/opt/idearesearch/avl/runs/vanilla.avl')
            return avl
        
        #avl_runoutput_service_offer = ServiceOffer(
        #    protocol='pyavl.outpututils.RunOutput',
        #    factory=self.create_default_runoutput,
        #    )
        
        return [avl_service_offer]#, avl_runoutput_service_offer]
    
    # deprecated
    def create_default_runoutput(self, *args, **kwargs):
        from pyavl.runutils import RunCase, RunConfig
        avl = self.application.get_service('pyavl.avl.AVL')
        rc = RunConfig(runcase=RunCase.get_case_from_avl(avl.avl))
        runoutput = rc.run(progressbar=False)
        return runoutput
    
#### EOF ######################################################################

