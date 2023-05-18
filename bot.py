#######################################################################################
#                                   MOBIBOT                                           #
#                                                                                     #
#                                   Imports                                           #
#######################################################################################
from dotenv import dotenv_values
import interactions
from shared.config import Config
from shared.reseaux import Reseaux
import asyncio


#######################################################################################
#                                 Définitions                                         #
#######################################################################################
config = dotenv_values(".env")
TOKEN = config['BOT_TOKEN']

EXTENSIONS = [
    'extensions.horaires',
    'extensions.stations',
    'extensions.lignes'
    ]


#######################################################################################
#                               Initialisations                                       #
#######################################################################################
Reseaux.Charger_reseaux(config)
Config.Creer_config(config)
bot = interactions.Client(token=TOKEN, activity="Guess The Station")


#######################################################################################
#                          chargement des extensions                                  #
#######################################################################################
for ext in EXTENSIONS:
    bot.load_extension(ext)


#######################################################################################
#                                     Démarrage                                       #
#######################################################################################
bot.start()
    

