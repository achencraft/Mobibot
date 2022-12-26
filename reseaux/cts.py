#######################################################################################
#                                                                                     #
#                     Compagnie des Transports Strasbourgeois                         #
#                                       CTS                                           #
#                                                                                     #
#######################################################################################
from reseaux.compagnie import Compagnie
from shared.stop import Stop_CTS
from shared.ligne import Ligne_CTS
from shared.passage import Passage
import json, requests, os


class Cts(Compagnie):


#######################################################################################
#                                 Définitions                                         #
#######################################################################################
    Name = "CTS-Strasbourg"
    Token = ""
    session = requests.Session()


#######################################################################################
#                        Initialisation depuis le bot                                 #
#######################################################################################
    
    #Point d'entrée du Bot
    def __init__(self,config):
      
        Cts.Token = config['CTS_TOKEN']         
        Cts.session.auth = (Cts.Token, "")
        Cts.LoadFromFile()


    #Appelée par le bot. Donne les prochains passages à un arrêt depuis l'OpenData
    def GetProchainPassage(config,station):

        passagesList = []
        url = config['CTS_NEXT_REQUEST']
        url += f"?MaximumStopVisits=3&MinimumStopVisitsPerLine=1&IncludeFLUO67=true&MonitoringRef={station}"

        ans = Cts.session.get(url).text

        if not ans == "":
            passages = json.loads(ans)["ServiceDelivery"]["StopMonitoringDelivery"][0]['MonitoredStopVisit']

            for p in passages:
                passage = Passage(
                    p['MonitoredVehicleJourney']['PublishedLineName'],
                    p['MonitoredVehicleJourney']['VehicleMode'],
                    p['MonitoredVehicleJourney']['DestinationName'],
                    p['MonitoredVehicleJourney']['Via'],
                    p['MonitoredVehicleJourney']['MonitoredCall']['ExpectedDepartureTime'],
                    p['MonitoredVehicleJourney']['MonitoredCall']['Extension']['IsRealTime'],
                )
                passagesList.append(passage)
        else:
            passagesList.append(Passage("00","rien","Temps réel indisponible pour cette station","","",False))
            
        return(passagesList)



#######################################################################################
#                           Fonctions de mise à jour                                  #
#######################################################################################
    
    #Point d'entrée du script de mise à jour
    def Update(config):
        Compagnie.Update(Cts.Name)
        Cts.Token = config['CTS_TOKEN']         
        Cts.session.auth = (Cts.Token, "")
        Cts.Creer_Stations(config['CTS_STOPLIST_REQUEST'])
        Cts.Creer_Lignes(config['CTS_LINES_REQUEST'])
        Cts.CalculateAdress()
        #Cts.LoadFromFile()  #debug
        Cts.Renommer_doublons()
        Cts.SaveToFile()
        


    #Récupération des arrêts depuis l'OpenData
    def Creer_Stations(url):
        Cts.log.info(Cts.Name+' | Création de la liste des stations')
        data = json.loads(Cts.session.get(url).text)["StopPointsDelivery"]["AnnotatedStopPointRef"]

        for i,stop in enumerate(data):
            station = Stop_CTS(
                stop['StopName'],                
                stop['Location']['Latitude'],
                stop['Location']['Longitude'],
                stop['Extension']['StopCode'],
                stop["Extension"]['LogicalStopCode'],
                stop["Extension"]['IsFlexhopStop'],
                stop['StopPointRef']
            )

            Cts.StopList.append(station)
        
        Cts.StopList = sorted(Cts.StopList, key=lambda stop: stop.nom) #tri alphabetique
        Cts.log.info(Cts.Name+' | Liste des stations créée')


    #Récupération des lignes depuis l'OpenData
    def Creer_Lignes(url):
        Cts.log.info(Cts.Name+' | Création de la liste des lignes')
        data = json.loads(Cts.session.get(url).text)["LinesDelivery"]["AnnotatedLineRef"]

        for i,ligne in enumerate(data):

            station = Ligne_CTS(
                "CTS",
                ligne['LineName'],                
                ligne['LineRef'],
                ligne['Extension']['RouteType'],
                ligne['Extension']['RouteTextColor'],
                ligne["Extension"]['RouteColor']
            )

            Cts.LignesList.append(station)
        
        Cts.LignesList = sorted(Cts.LignesList, key=lambda ligne: ligne.ref) #tri alphabetique
        Cts.log.info(Cts.Name+' | Liste des lignes créée')


    #Récupération de la topologie depuis un fichier
    def LoadFromFile():
        if os.path.exists('data/topology/'+Cts.Name+'.json'):
            data = json.load(open('data/topology/'+Cts.Name+'.json'))
            for stop in data['stops']:
                Cts.StopList.append(Stop_CTS(stop))
            for ligne in data['lignes']:
                Cts.LignesList.append(Ligne_CTS(ligne))
            Cts.log.info(Cts.Name+' | Données chargées ')
        else:
            Cts.log.info(Cts.Name+' | Aucun fichier de donnée. Lancez le programme update.py ')


