#######################################################################################
#                                                                                     #
#                               Classe Compagnie                                      #
#                                                                                     #
#######################################################################################
import json,structlog
import progressbar
from itertools import groupby


class Compagnie(object):


#######################################################################################
#                                 Définitions                                         #
#######################################################################################
    Name = ""
    StopList = []
    LignesList = []
    log = structlog.get_logger()    


#######################################################################################
#                        Initialisation depuis le bot                                 #
#######################################################################################
    
    #Point d'entrée du Bot
    def __init__(self):
        #à implémenter dans les compagnies
        return




#######################################################################################
#                           Fonctions de mise à jour                                  #
#######################################################################################
    
    #Point d'entrée du script de mise à jour
    def Update(name):
        #à implémenter dans les compagnies
        Compagnie.Name = name


    #Récupération des arrêts depuis l'OpenData
    def Creer_Stations(url):
        #à implémenter dans les compagnies
        return


    #Calcul de l'adresse des arrêts depuis leur coordonnées
    def CalculateAdress():


        Compagnie.log.info(Compagnie.Name+' | Calcul des adresses ')
        lastStop = Compagnie.StopList[-1]
        bar = progressbar.ProgressBar(maxval=len(Compagnie.StopList), \
            widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
        bar.start()

        for i,stop in enumerate(Compagnie.StopList):
            if not lastStop.logicalStopCode == stop.logicalStopCode:
                stop.Find_Adress_From_Coord()
            else:
                stop.ville = lastStop.ville
                stop.pays = lastStop.pays
                stop.postalcode = lastStop.postalcode
            lastStop = stop
            bar.update(i+1)
        bar.finish()
        Compagnie.log.info(Compagnie.Name+' | Calcul des adresses terminé')


    #Ajoute la ville devant le nom des stations ayant un nom identique
    def Renommer_doublons():
        out = []
        grouped_by_name = [list(result) for key, result in groupby(sorted(Compagnie.StopList, key=lambda stop: stop.nom), key=lambda x: x.nom)]
        for group in grouped_by_name:
            ville = group[0].ville
            doublon = False
            for s in group:
                if not s.ville == ville:
                    doublon = True
            for s in group:
                if doublon:
                    s.nom = s.ville+" "+s.nom
                out.append(s)
        Compagnie.StopList = sorted(out, key=lambda stop: stop.nom)


    #Sauvegarde de la topologie dans un fichier
    def SaveToFile():
        StopList = []
        LignesList = []
        for stop in sorted(Compagnie.StopList, key=lambda stop: stop.nom):
            StopList.append(stop.__dict__)
        for ligne in sorted(Compagnie.LignesList, key=lambda ligne: ligne.ref):
            LignesList.append(ligne.__dict__)
        
        out = { 'stops': StopList, 'lignes' : LignesList }
        with open('data/topology/'+Compagnie.Name+'.json', 'w') as f:
            json.dump(out, f)
        Compagnie.log.info(Compagnie.Name+' | Données sauvegardées ')



    #Récupération des arrêts depuis un fichier
    def LoadFromFile():
        #à implémenter dans les compagnies
        return




#######################################################################################
#                                     Getters                                         #
#######################################################################################
    
    #Retourne la liste des arrêts Distinct par nom
    def GetStops(ville):        
        distinctStopList = []
        distinctAttr = []

        if ville == "":
            for s in Compagnie.StopList:
                if (s.nom,s.ville) not in distinctAttr:
                    distinctStopList.append(s)
                    distinctAttr.append((s.nom,s.ville))
        else:
            for s in Compagnie.StopList:
                if (s.nom,s.ville) not in distinctAttr and s.ville == ville:
                    distinctStopList.append(s)
                    distinctAttr.append((s.nom,s.ville))

        return  sorted(distinctStopList, key=lambda s: s.nom)

    #Retourne la liste des lignes Distinct par ref
    def GetLines():
        distinctLigneList = []
        distinctAttr = []
        for l in Compagnie.LignesList:
                if l.ref not in distinctAttr:
                    distinctLigneList.append(l)
                    distinctAttr.append(l.ref)
        return distinctLigneList

    #Retourne la liste des villes desservies 
    def GetCities():
        villes = []
        for stop in Compagnie.StopList:
            if stop.ville not in villes:
                villes.append(stop.ville)
        return sorted(villes) 

        