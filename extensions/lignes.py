#######################################################################################
#                                                                                     #
#                                Fonction lignes                                      #
#                                                                                     #
#######################################################################################
import interactions, copy
from shared.config import Config
from shared.reseaux import Reseaux



class Lignes(interactions.Extension):
    def __init__(self, client):
        self.client: interactions.Client = client

        self.buttons = []
        self.buttons.append(
            interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Première page",
            custom_id="Ligne_First_Page",
            )
        )
        self.buttons.append(
            interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Page précédente",
            custom_id="Ligne_Prev_Page",
            )
        )
        self.buttons.append(
            interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Page suivante",
            custom_id="Ligne_Next_Page",
            )
        )
        self.buttons.append(
            interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Dernière Page",
            custom_id="Ligne_Last_Page",
            )
        )



#######################################################################################
#                               Commande station                                      #
#######################################################################################


    @interactions.slash_command(
        name="lignes",
        description="Obtenir la liste des lignes d'une compagnie")    
    @interactions.slash_option(
        name="compagnie",
        description="Compagnie de transport",
        opt_type=interactions.OptionType.STRING,
        required=True,
        autocomplete=True
    )
    @interactions.slash_option(
        name="public",
        description="Réponse visible de tous",
        opt_type=interactions.OptionType.BOOLEAN,
        required=False
    )
    async def Lignes(self, ctx: interactions.SlashContext, compagnie: str, public: bool = False ):

        lignesList = []
        reseau = ""

        (lignesList, reseau) = self.get_LignesReseau_from_compagnie(compagnie)

   

        if(len(lignesList) > 0):
            nbr_line_per_page = int(Config.LIGNE_NBR_LIGNE_PAR_PAGE)
            nbr_page = len(lignesList)//nbr_line_per_page
            if(len(lignesList)%nbr_line_per_page > 0):
                nbr_page = nbr_page+1

            titre = f"Liste des lignes {reseau}"        
            titre = titre + f" - page 1/{nbr_page}"

            content = ""
            line_to_show = [s for  s in lignesList[:nbr_line_per_page]]
            for line in line_to_show:
                if not line.emoji == "":
                    content += '\n {}'.format(line.emoji+" - "+line.nom)
                else:
                    content += '\n {}'.format(line.ref+" - "+line.nom)


            embed = interactions.Embed(title=titre, description=content)

            footer = 'linelist_'+reseau
            footer = footer + ':1'

            embed.set_footer(text=footer)

            boutons = copy.deepcopy(self.buttons)
            if nbr_page == 1:
                boutons = []
            else:
                boutons[0].disabled = True
                boutons[1].disabled = True

            if public:
                await ctx.send(embeds=embed, components=boutons, ephemeral=False)
            else:
                await ctx.send(embeds=embed, components=boutons, ephemeral=True)

        else:
            text = "Aucune ligne pour "+reseau+"\nContactez le support du bot"
            await ctx.send(content=text, ephemeral=True)





    @Lignes.autocomplete("compagnie")
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


#######################################################################################
#                              Changement de page                                     #
#######################################################################################

    async def change_page(self, ctx, mode):

        data = ctx.message.embeds[0]
        boutons = copy.deepcopy(self.buttons)
        footer = data.footer.text
        compagnie = footer.split(':')[0].split('_')[1]
        page_actuelle =  int(footer.split(':')[1])
        lignesList = []
        reseau = ""


        (lignesList, reseau) = self.get_LignesReseau_from_compagnie(compagnie)


        nbr_line_per_page = int(Config.LIGNE_NBR_LIGNE_PAR_PAGE)
        nbr_page = len(lignesList)//nbr_line_per_page
        if(len(lignesList)%nbr_line_per_page > 0):
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
            boutons[0].disabled = True
            boutons[1].disabled = True
            boutons[2].disabled = False
            boutons[3].disabled = False
        elif nouvelle_page == nbr_page:
            boutons[0].disabled = False
            boutons[1].disabled = False
            boutons[2].disabled = True
            boutons[3].disabled = True
        else:
            boutons[0].disabled = False
            boutons[1].disabled = False
            boutons[2].disabled = False
            boutons[3].disabled = False


        debut = (nouvelle_page - 1)*nbr_line_per_page
        fin = debut + nbr_line_per_page

        titre = f"Liste des lignes {reseau}"
        titre = titre + f" - page {nouvelle_page}/{nbr_page}"

        content = ""
        line_to_show = [s for  s in lignesList[debut:fin]]
        for line in line_to_show:
            if not line.emoji == "":
                content += '\n {}'.format(line.emoji+" - "+line.nom)
            else:
                content += '\n {}'.format(line.ref+" - "+line.nom)

        embed = interactions.Embed(title=titre, description=content)

        footer = 'linelist_'+reseau
        footer = footer + f':{nouvelle_page}'

        embed.set_footer(text=footer)
        await ctx.edit_origin(embeds=embed, components=boutons)
             

#######################################################################################
#                               Listeners BOUTONS                                     #
#######################################################################################


    @interactions.component_callback("Ligne_First_Page")
    async def FirstPageButton(self,ctx: interactions.ComponentContext):
        await self.change_page(ctx, "First")
        
    @interactions.component_callback("Ligne_Prev_Page")
    async def PrevPageButton(self,ctx: interactions.ComponentContext):
        await self.change_page(ctx, "Prev")

    @interactions.component_callback("Ligne_Next_Page")
    async def NextPageButton(self,ctx: interactions.ComponentContext):
        await self.change_page(ctx, "Next")

    @interactions.component_callback("Ligne_Last_Page")
    async def LastPageButton(self,ctx: interactions.ComponentContext):
        await self.change_page(ctx, "Last")


#######################################################################################
#                                      Utils                                          #
#######################################################################################

    def get_LignesReseau_from_compagnie(self,compagnie):
        LignesList = Reseaux.Get_Lignes_From_Compagnie(compagnie)
        reseau = Reseaux.Get_Compagnie_Name(compagnie)
        return (LignesList,reseau)



def setup(client):
    Lignes(client)
