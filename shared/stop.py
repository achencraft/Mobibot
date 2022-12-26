#######################################################################################
#                                                                                     #
#                                   Classe Stop                                       #
#                                                                                     #
#######################################################################################
from geopy.geocoders import Nominatim



class Stop():

    def __init__(self,nom,latitude,longitude):
        self.nom = nom
        self.latitude = latitude
        self.longitude = longitude
        self.pays = ""
        self.ville = ""
        self.postalcode = ""


    def Find_Adress_From_Coord(self):
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse(str(self.latitude)+","+str(self.longitude))
        address = location.raw['address']

        self.pays = address.get('country', '')
        self.postalcode = address.get('postcode', '')

        if address.get('town', '') != "":
            self.ville = address.get('town', '')
        elif address.get('village', '') != "":
            self.ville = address.get('village', '')
        else:
            self.ville = address.get('city', '')



#######################################################################################
#                                 Classe Stop_CTS                                     #
#######################################################################################

class Stop_CTS(Stop):
    
    def __init__(self,*args):

        if len(args) > 1:
            Stop.__init__(self,args[0],args[1],args[2]) #nom, latitude, longitude
            self.stopCode = args[3] #stopCode
            self.logicalStopCode = args[4] #logicalStopCode
            self.IsFlexhop = args[5] #IsFlexhop
            self.stopPointRef = args[6] #StopPointRef
        else:
            self.__dict__.update(args[0]) #dict
