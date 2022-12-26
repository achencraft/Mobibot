#######################################################################################
#                        Script de mise à jour MOBIBOT                                #
#                                                                                     #
#                                   Imports                                           #
#######################################################################################
from shared.reseaux import Reseaux
from dotenv import dotenv_values


config = dotenv_values(".env")

Reseaux.Creer_reseaux(config)





