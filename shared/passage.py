#######################################################################################
#                                                                                     #
#                                   Classe Passage                                    #
#                                                                                     #
#######################################################################################
class Passage():

    def __init__(self,ligne,type,destination,via,heure,realtime):
        self.ligne = ligne
        self.type = type
        self.destination = destination
        self.via = via
        self.heure = heure
        self.realtime = realtime