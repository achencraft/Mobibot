#######################################################################################
#                                                                                     #
#                               Fonction stations                                     #
#                                                                                     #
#######################################################################################
import interactions
from shared.config import Config
from shared.reseaux import Reseaux

#from reseaux.cts import Cts


class Stations(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

        self.buttons = []
        self.buttons.append(
            interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Première page",
            custom_id="Stop_First_Page",
            )
        )
        self.buttons.append(
            interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Page précédente",
            custom_id="Stop_Prev_Page",
            )
        )
        self.buttons.append(
            interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Page suivante",
            custom_id="Stop_Next_Page",
            )
        )
        self.buttons.append(
            interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Dernière Page",
            custom_id="Stop_Last_Page",
            )
        )



#######################################################################################
#                               Commande station                                      #
#######################################################################################

    @interactions.extension_autocomplete(command="stations", name="ville")
    async def autocomplete_ville(self, ctx, user_input: str = ""):

        options = ctx.data.options
        for option in options:
            if option.name == "compagnie":
                compagnie = option.value

        liste_ville = Reseaux.Get_Cities_From_Compagnie(compagnie)
        liste_choix = []

        if user_input == "":
            for ville in liste_ville:
                liste_choix.append(interactions.Choice(name=ville, value=ville))
        else:
            for ville in liste_ville:                
                if user_input in ville.lower():
                    liste_choix.append(interactions.Choice(name=ville, value=ville))
        await ctx.populate(liste_choix[:20])

    @interactions.extension_autocomplete(command="stations", name="compagnie")
    async def autocomplete_compagnie(self, ctx, user_input: str = ""):
        liste_compagnie = Reseaux.Get_Compagnies()
        liste_choix = []

        if user_input == "":
            for compagnie in liste_compagnie:
                liste_choix.append(interactions.Choice(name=compagnie, value=compagnie))
        else:
            for compagnie in liste_compagnie:                
                if user_input in compagnie.lower():
                    liste_choix.append(interactions.Choice(name=compagnie, value=compagnie))
        await ctx.populate(liste_choix[:20])


    @interactions.extension_command(
        name="stations",
        description="Obtenir la liste des stations d'une compagnie",
        options=[
            interactions.Option(
                name="compagnie",
                description="Compagnie de transport",
                type=interactions.OptionType.STRING,
                required=True,
                autocomplete=True
            ),
            interactions.Option(
                name="ville",
                description="Ville",
                type=interactions.OptionType.STRING,
                required=False,
                autocomplete=True
            ),
            interactions.Option(
                name="public",
                description="Réponse visible de tous",
                type=interactions.OptionType.BOOLEAN,
                required=False
            )
        ],
    )
    async def Stations(self, ctx: interactions.CommandContext, compagnie: str, ligne: str = "", ville: str = "", public: bool = False ):

        stopList = []
        reseau = ""
        (stopList, reseau) = self.get_StopsReseau_from_compagnie(compagnie, ville)
        if(len(stopList) > 0):
            nbr_stop_per_page = int(Config.STATION_NBR_STOP_PAR_PAGE)
            nbr_page = len(stopList)//nbr_stop_per_page
            if(len(stopList)%nbr_stop_per_page > 0):
                nbr_page = nbr_page+1

            titre = f"Liste des stations {reseau}"
            if not ville == "":
                titre = titre + f" à {ville}"           
            titre = titre + f" - page 1/{nbr_page}"

            content = ""
            stop_to_show = [s for  s in stopList[:nbr_stop_per_page]]
            for stop in stop_to_show:
                content += f'\n {stop.nom}'


            embed = interactions.Embed(title=titre, description=content)

            footer = 'stoplist_'+reseau
            if not ville == "":
                footer = footer + '_' + ville
            else:
                footer = footer + '_'
            footer = footer + ':1'

            embed.set_footer(text=footer)

            boutons = self.buttons
            if nbr_page == 1:
                boutons = []
            else:
                boutons[1].disabled = True

            if public:
                await ctx.send(embeds=embed, components=boutons, ephemeral=False)
            else:
                await ctx.send(embeds=embed, components=boutons, ephemeral=True)

        else:
            text = "Aucune station pour "+reseau+" "+ville+"\nContactez le support du bot"
            await ctx.send(content=text, ephemeral=True)


#######################################################################################
#                              Changement de page                                     #
#######################################################################################

    async def change_page(self, ctx, mode):

        data = ctx.message.embeds[0]
        footer = data.footer.text
        compagnie = footer.split(':')[0].split('_')[1]
        ville = footer.split(':')[0].split('_')[2]
        page_actuelle =  int(footer.split(':')[1])
        stopList = []
        reseau = ""


        (stopList, reseau) = self.get_StopsReseau_from_compagnie(compagnie, ville)



        nbr_stop_per_page = int(Config.STATION_NBR_STOP_PAR_PAGE)
        nbr_page = len(stopList)//nbr_stop_per_page
        if(len(stopList)%nbr_stop_per_page > 0):
            nbr_page = nbr_page+1

        match mode:
            case "First":
                nouvelle_page = 1
            case "Prev":
                nouvelle_page = page_actuelle - 1
            case "Next":
                nouvelle_page = page_actuelle + 1
            case "Last":
                nouvelle_page = nbr_page

        if nouvelle_page == 1:
            self.buttons[1].disabled = True
            self.buttons[2].disabled = False
        elif nouvelle_page == nbr_page:
            self.buttons[2].disabled = True
            self.buttons[1].disabled = False
        else:
            self.buttons[1].disabled = False
            self.buttons[2].disabled = False


        debut = (nouvelle_page - 1)*nbr_stop_per_page
        fin = debut + nbr_stop_per_page

        titre = f"Liste des stations {reseau}"
        if not ville == "":
            titre = titre + f" à {ville}"           
        titre = titre + f" - page {nouvelle_page}/{nbr_page}"

        content = ""
        stop_to_show = [s.nom for  s in stopList[debut:fin]]
        for stop in stop_to_show:
            content += '\n {}'.format(stop)

        embed = interactions.Embed(title=titre, description=content)

        footer = 'stoplist_'+reseau
        if not ville == "":
            footer = footer + f"_{ville}"
        else:
            footer = footer + '_'
        footer = footer + f':{nouvelle_page}'

        embed.set_footer(text=footer)
        await ctx.edit(embeds=embed, components=self.buttons)
             

#######################################################################################
#                               Listeners BOUTONS                                     #
#######################################################################################


    @interactions.extension_component(
        interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="",
            custom_id="Stop_First_Page",
        )
    )
    async def FirstPageButton(self,ctx: interactions.ComponentContext):
        await self.change_page(ctx, "First")
        
    
    @interactions.extension_component(
        interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="",
            custom_id="Stop_Prev_Page",
        )
    )
    async def PrevPageButton(self,ctx):
        await self.change_page(ctx, "Prev")

    @interactions.extension_component(
        interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="",
            custom_id="Stop_Next_Page",
        )
    )
    async def NextPageButton(self,ctx):
        await self.change_page(ctx, "Next")

    @interactions.extension_component(
        interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="",
            custom_id="Stop_Last_Page",
        )
    )
    async def LastPageButton(self,ctx):
        await self.change_page(ctx, "Last")


#######################################################################################
#                                      Utils                                          #
#######################################################################################

    def get_StopsReseau_from_compagnie(self,compagnie, ville):

        stopList = Reseaux.Get_Stations_From_Compagnie(compagnie,ville)
        reseau = Reseaux.Get_Compagnie_Name(compagnie)



        return (stopList,reseau)



def setup(client):
    Stations(client)



