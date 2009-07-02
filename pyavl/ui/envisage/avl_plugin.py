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
            protocol = 'pyavl.avl.AVL',
            factory  = 'pyavl.avl.create_default_avl'
        )

        return [avl_service_offer]
    
#### EOF ######################################################################

