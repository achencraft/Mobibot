#######################################################################################
#                                                                                     #
#                                   Classe Ligne                                      #
#                                                                                     #
#######################################################################################
import os, json

class Ligne():

    def __init__(self,compagnie, nom,ref,type,textcolor,routecolor):
        self.nom = nom
        self.ref = ref
        self.type = type
        self.text_color = textcolor
        self.route_color = routecolor
        self.emoji = ""

        if os.path.exists('data/LineEmoji.json'):
            data = json.load(open('data/LineEmoji.json'))
            for comp in data['emojis']:                
                if(comp['compagnie'] == compagnie):
                    if ref in comp:
                        self.emoji = comp[ref]


#######################################################################################
#                                                                                     #
#                                  Classe Ligne_CTS                                   #
#                                                                                     #
#######################################################################################

class Ligne_CTS(Ligne):
    
    def __init__(self,*args):

        if len(args) > 1:
            Ligne.__init__(self,args[0],args[1],args[2],args[3],args[4],args[5]) #compagnie, nom, ref, type, textcolor, routecolor

            
        else:
            self.__dict__.update(args[0]) #dict
