#######################################################################################
#                                                                                     #
#                            Déclarations des réseaux                                 #
#                                                                                     #
#######################################################################################
from reseaux.cts import Cts


class Reseaux():

    Compagnies = ['CTS'] #LUXTRAM, TCL


    #Lancé depuis le Bot
    def Charger_reseaux(config):
        Reseaux.config = config
        Cts(config)




    #Lancé depuis le script de mise à jour
    def Creer_reseaux(config):
        Cts.Update(config)



#######################################################################################
#                                     Getter                                          #
#######################################################################################

    #Obtenir les prochains passages à un arrêt
    def get_Passages_Live(compagnie, station):
        match compagnie:
            case "CTS":
                passages = Cts.GetProchainPassage(Reseaux.config,station)
            case _:
                passages = []       
        return passages


    #Obtenir les arrêts d'une compagnie
    def Get_Stations_From_Compagnie(compagnie, ville):
        match compagnie:
            case "CTS":
                stopList = Cts.GetStops(ville)
            case _:
                stopList = []       
        return stopList

    #Obtenir les lignes d'une compagnie
    def Get_Lignes_From_Compagnie(compagnie):
        match compagnie:
            case "CTS":
                stopList = Cts.GetLines()
            case _:
                stopList = []       
        return stopList


    #Obtenir le nom de la compagnie (vraiment utile ?)
    def Get_Compagnie_Name(compagnie):
        match compagnie:
            case "CTS":
                reseau = Cts.Name.split('-')[0].strip()
            case _:
                reseau = compagnie
        return reseau


    #Obtenir les villes desservies par la compagnie
    def Get_Cities_From_Compagnie(compagnie):
        match compagnie:
            case "CTS":
                villes = Cts.GetCities()
            case _:
                villes = compagnie
        return villes


    #Obtenir la liste des compagnies
    def Get_Compagnies():
        return Reseaux.Compagnies