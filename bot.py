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

async def set_activity():
    activity = interactions.PresenceActivity(name="Guess The Station",type=0)
    await bot.change_presence(interactions.ClientPresence(activities=[activity]))


#######################################################################################
#                               Initialisations                                       #
#######################################################################################
Reseaux.Charger_reseaux(config)
Config.Creer_config(config)
bot = interactions.Client(token=TOKEN)
asyncio.run(set_activity())


#######################################################################################
#                          chargement des extensions                                  #
#######################################################################################
for ext in EXTENSIONS:
    bot.load(ext)


#######################################################################################
#                                     Démarrage                                       #
#######################################################################################
bot.start()
    

