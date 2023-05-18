#######################################################################################
#                                                                                     #
#                               Fonction horaires                                     #
#                                                                                     #
#######################################################################################
import interactions, copy
import itertools, arrow, re
from shared.reseaux import Reseaux
from shared.ligne import Ligne



class Horaires(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

        self.button = interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Actualiser",
            custom_id="Reload",
            )




    @interactions.slash_command(
        name="horaires",
        description="Obtenir le prochain passage en station")
    @interactions.slash_option(
        name="compagnie",
        description="Compagnie de transport",
        opt_type=interactions.OptionType.STRING,
        required=True,
        autocomplete=True
    )
    @interactions.slash_option(
        name="station",
        description="Station",
        opt_type=interactions.OptionType.STRING,
        required=True,
        autocomplete=True
    )
    @interactions.slash_option(
        name="mode",
        description="Théorique ou Temps Réel",
        opt_type=interactions.OptionType.STRING,
        choices=[
            interactions.SlashCommandChoice(name="Live", value="Live"),
            interactions.SlashCommandChoice(name="Théorique", value="PDF")
            ], #Live par défaut
        required=False,
    )
    @interactions.slash_option(
        name="public",
        description="Réponse visible de tous",
        opt_type=interactions.OptionType.BOOLEAN,
        required=False
    )
    async def Horaires(self, ctx: interactions.SlashContext, compagnie: str, station: str, mode: str = "Live", public: bool = False):

        embeds = []
        bouton = copy.deepcopy(self.button)

        pattern = re.compile(r"[0-9]+[a-zA-Z]", re.IGNORECASE)
        if station.isnumeric():
            stop = list(filter(lambda x: x.logicalStopCode == station,Reseaux.Get_Stations_From_Compagnie(compagnie,"")))[0]
        elif pattern.match(station):
            stop = list(filter(lambda x: x.logicalStopCode == station[:-1],Reseaux.Get_Stations_From_Compagnie(compagnie,"")))[0]
        else:
            stop = list(filter(lambda x: x.nom == station,Reseaux.Get_Stations_From_Compagnie(compagnie,"")))[0]
            station = stop.logicalStopCode

        if mode == "Live":
            
            embeds = await self.GetAttente(compagnie, station)

            titre = stop.nom
            now = arrow.utcnow().to('Europe/Paris').format('DD/MM/YY HH:mm')
            if len(embeds) == 0 :
                embed = interactions.Embed(title=titre,description="Aucun passage pour la station "+stop.nom)
                embed.set_footer(text=compagnie+"_"+station)
                await ctx.send(embeds=embed,components=bouton,ephemeral=True)
            else:
                embeds[-1].set_footer(text=compagnie+"_"+station+"\nmis à jour le "+now)
                embeds[0].title = titre+"\n"+embeds[0].title

            if public:
                await ctx.send(embeds=embeds, components=bouton)
            else:
                await ctx.send(embeds=embeds, components=bouton, ephemeral=True)
        else:
            #Reseaux.get_Passages_PDF(compagnie,station)
            await ctx.send("Option à venir",ephemeral=True)




    @Horaires.autocomplete("compagnie")
    async def autocomplete_compagnie(self, ctx: interactions.AutocompleteContext):
        liste_compagnie = Reseaux.Get_Compagnies()
        liste_choix = []

        if ctx.input_text == "":
            for compagnie in liste_compagnie:
                liste_choix.append(interactions.SlashCommandChoice(name=compagnie, value=compagnie))
        else:
            for compagnie in liste_compagnie:                
                if ctx.input_text in compagnie.lower():
                    liste_choix.append(interactions.SlashCommandChoice(name=compagnie, value=compagnie))
        await ctx.send(liste_choix[:20])

    @Horaires.autocomplete("station")
    async def autocomplete_station(self, ctx: interactions.AutocompleteContext):

        compagnie = ctx.kwargs['compagnie']

        liste_stations = Reseaux.Get_Stations_From_Compagnie(compagnie,"")

        liste_choix = []

        if ctx.input_text == "":
            for station in liste_stations:
                liste_choix.append(interactions.SlashCommandChoice(name=station.nom, value=station.logicalStopCode))
        else:
            for station in liste_stations:                
                if ctx.input_text in station.nom.lower():
                    liste_choix.append(interactions.SlashCommandChoice(name=station.nom, value=station.logicalStopCode))

        
        await ctx.send(liste_choix[:20])

#######################################################################################
#                      Fonction de récupération des temps                             #
#######################################################################################

    async def GetAttente(self, compagnie, station):
        embeds = []
        passages = Reseaux.get_Passages_Live(compagnie,station)
        lignes = Reseaux.Get_Lignes_From_Compagnie(compagnie)
        for key, group in itertools.groupby(sorted(passages,key= lambda y: y.ligne),lambda x: x.ligne):

            emoji = list(filter(lambda x : x.ref == key,lignes))
            if len(emoji) == 0:
                titre = f"Ligne {key}"
            else:
                color = titre = f"Ligne {emoji[0].emoji}"
            
            content = ""

            group = sorted(group,key= lambda y: y.heure)
            group = sorted(group,key= lambda y: y.destination)

            for dest, group2 in itertools.groupby(group,lambda x: x.destination):

                content += "\n **"+dest+"**: "

                for p in group2:

                    if not p.heure == "":
                        temps = arrow.get(p.heure)
                        utc = arrow.utcnow()
                        now = utc.to('Europe/Paris')
                        diff = temps - now
                        if(diff.seconds > 0):
                            temps_attente = str(diff.seconds//60)
                        else:
                            temps_attente = "0"

                        if temps_attente == "1439": #bug ?
                            temps_attente = "0"
                    else:
                        temps_attente = "-1"

                    content += " "+temps_attente+"min"


                    

            color_code = list(filter(lambda x : x.ref == key,lignes))
            if len(color_code) == 0:
                color = 0
            else:
                color = int(color_code[0].route_color,16)


            embed = interactions.Embed(color=color,title=titre, description=content)
            embeds.append(embed)
            
        return embeds


#######################################################################################
#                                Actualisation                                       #
#######################################################################################

    async def Actualiser(self, ctx):
        
        data = ctx.message.embeds[-1]
        bouton = copy.deepcopy(self.button)
        footer = data.footer.text
        compagnie = footer.split('_')[0]
        station =  footer.split('_')[1].split('\n')[0]

        embeds = []
        stop = list(filter(lambda x: x.logicalStopCode == station,Reseaux.Get_Stations_From_Compagnie(compagnie,"")))[0]
        titre = stop.nom

        embeds = await self.GetAttente(compagnie, station)
        now = arrow.utcnow().to('Europe/Paris').format('DD/MM/YY HH:mm')

        if len(embeds) == 0 :
            embed = interactions.Embed(title=titre,description="Aucun passage pour la station "+stop.nom)
            embed.set_footer(text=compagnie+"_"+station+"\nmis à jour le "+now)
            await ctx.send(embeds=embed,components=bouton,ephemeral=True)
        else:
            embeds[-1].set_footer(text=compagnie+"_"+station+"\nmis à jour le "+now)
            embeds[0].title = titre+"\n"+embeds[0].title


        
        await ctx.edit_origin(embeds=embeds, components=bouton)


#######################################################################################
#                               Listeners BOUTONS                                     #
#######################################################################################


    @interactions.component_callback("Reload")
    async def reload(self,ctx: interactions.ComponentContext):
        await self.Actualiser(ctx)



def setup(client):
    Horaires(client)



