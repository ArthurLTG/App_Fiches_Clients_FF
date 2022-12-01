# %% [markdown]
# # Traitement des Fiches Clients

# %% [markdown]
# ## Fonctions de Support

# %%
from datetime import datetime, date
import re
import numpy as np

# ----------------------------------------------------------
# Convertit en DATE la donnée "Month dans DateCreation"
def convert2Date(x) :
    #x = "01/"+ x
    y = datetime.strptime(x, '%d/%m/%Y').date()
    return y



# ----------------------------------------------------------
# Repartir les magasins ECOM vs RETAIL

def Def_Groupe(x):
    if x == "WEB":
         x = "ECOM"
    else:
        x = "RETAIL"
    
    return x



# ----------------------------------------------------------
# Verifie les ADRESSES EMAIL
def checkEmail(x):

    regex_Email = re.search("([A-Z0-9a-z\-]*)@([A-Z0-9a-z\-\_\.]*)\.(.*)",x)

    if x in [None,"","-",np.nan]:
        x = 1
        
    elif regex_Email:
        x = 0

    else:
        x = 1
        
    return x



# ----------------------------------------------------------
# Verifie la CIVILITE
def checkCivilite(x):

    regex_Civilite = re.search("([A-Za-z\-]*)",x)

    if x in [None,"Nan","-","","nan",np.nan]:
        x = 1
        
    elif regex_Civilite:
        x = 0

    else:
        x = 1
        
    return x 



# ----------------------------------------------------------
# Verifie la DATE DE NAISSANCE
def checkDateNaissance(x):
    if x == "01/01/1900":
        x = 1
    else:
        x = 0
    
    return x
    

# ----------------------------------------------------------
# Verification BASIQUE
def checkBasic(x):
    
    if x in [None,"Nan","-","","nan","A","NaN",np.nan]:
        x=1
    else:
        x=0

    return x




# ----------------------------------------------------------
# Verification de l'OPTIN EMAIL
# Par défaut 0 donc on le sort de la notation de la fiche client, on remplace par le taux global d'acceptation
def CheckOptInEmail(x):

    if x == 1:
        x=0
    else:
        x=1
    
    return x


# ----------------------------------------------------------
# Calcule le taux de completion des collones renseignées
def Calcul_Tx_Completion(arr, df, level):
    for a in arr:
        df["total"+level] = df["total"+level] + df[a]

    df["Tx_Erreur"+level] = df["total"+level] / len(arr)
    df["Tx_Complet"+level] = (1 - df["Tx_Erreur"+level])
    return df


# %% [markdown]
# ## Traitement Principal

# %%


from xmlrpc.client import _iso8601_format
import pandas as pd
import re
import numpy as np



def Traitement(df):
    print(df.columns)


    
    df["Nb Ticket Vente > 0"] = df["Nb Ticket Vente > 0"].fillna(0)
    df["MagasinCreation"] = df["MagasinCreation"].fillna("0")
    df.rename(columns = {'Days dans DateNaissance':'DateNaissance',
                        "PubParEMail": "PubEmail"}, 
                        inplace = True)
                        
    df["Days dans DateCreation"] = df["Days dans DateCreation"].apply(lambda x : convert2Date(x) )
    df["MoisCreation"] = df["Days dans DateCreation"].apply(lambda x : x.month )
    df["Days dans DateCreation"] = df["Days dans DateCreation"].apply(lambda x : x.isoformat() )

    df["Date Dernier Achat"] = df["Date Dernier Achat"].apply(lambda x : str(datetime.strptime(str(x), '%Y%m%d').date())) 
    df["PM Client"] = df["PM Client"].apply(lambda x : float(str(x).replace(",",".")))

    df["Groupe"] = df["MagasinCreation"].apply( lambda x : Def_Groupe(x))

    df["Check_Nom"] = df["Nom"].apply(lambda x : checkBasic(x))
    df["Check_Prenom"] = df["Prenom"].apply(lambda x : checkBasic(x))
    df["Check_Email"] = df["Email"].apply(lambda x : checkEmail(x))
    df["Check_Civilite"] = df["Civilite"].apply(lambda x : checkBasic(x))

    df["Type_client"] = df["Nb Ticket Vente > 0"].apply(lambda x :"New" if x == 1 else "Known")

    df["Check_DateNaissance"] = df["DateNaissance"].apply(lambda x : checkDateNaissance(x))
    df["Check_Pays"] = df["Pays"].apply(lambda x : checkBasic(x))
    #df_mag["Check_Ville"] = df_mag["Ville"].apply(lambda x : checkBasic(x))
    df["Check_codepostal"] = df["codepostal"].apply(lambda x : checkBasic(x))
    df["Check_Portable"] = df["Portable"].apply(lambda x : checkBasic(x))
    #df["Check_PubEmail"] = df["PubEmail"].apply(lambda x : CheckOptInEmail(x))
    #df_mag["temps_depuis_achat"] = df_mag["Date Dernier Achat"].apply(lambda x : date.today() - x)
    #df["Date Dernier Achat"] = df["Date Dernier Achat"].apply(lambda x : date.today())
    #df["Nouveau_Client"] = df["Nb Ticket Vente > 0"].apply(lambda x : isNewCustomer(x) )
    df["Check_Adresse"] = df["Adresse1"].apply(lambda x : checkBasic(x))

    #( df[df["Client"]==133993][["Adresse1","Check_Adresse"]] ) 


    # %% [markdown]
    # ## Calcul des Notes de Fiches Client

    # %%
    print(df.columns)


    cols = df.columns


    # Note Fiche : Level 0 = Global --------------------------------------------------------------------------------
    arr = []
    for col in cols:
        if (re.search("^Check.*", col)) :
            arr.append(col)

    niveau = ""
    df["total"+niveau] = 0
    df = Calcul_Tx_Completion(arr,df,niveau)
    print(df)


    # Note Fiche : Level 1 = ".*Nom.*|.*Civilite.*|.*Prenom.*|.*Email.*" ----------------------------------------------
    arr = []
    for col in cols:
        if (re.search("^Check.*", col)) and (re.search(".*Nom.*|.*Civilite.*|.*Prenom.*|.*Email.*", col)) :
            arr.append(col)

    niveau = "_lvl1"
    df["total"+niveau] = 0
    df = Calcul_Tx_Completion(arr, df, niveau)


    # Note Fiche : Level 2 = ".*codepostal.*|.*Portable.*|.*Pays.*" ----------------------------------------------
    arr = []
    for col in cols:
        if (re.search("^Check.*", col)) and (re.search(".*codepostal.*|.*Portable.*|.*Pays.*", col)) :
            arr.append(col)

    niveau = "_lvl2"
    df["total"+niveau] = 0
    df = Calcul_Tx_Completion(arr, df, niveau)


    # Note Fiche : Level 3 = ".*DateNaissance.*|.*Adresse.*" ----------------------------------------------
    arr = []
    for col in cols:
        if (re.search("^Check.*", col)) and (re.search(".*DateNaissance.*|.*Adresse.*", col)) :
            arr.append(col)

    niveau = "_lvl3"
    df["total"+niveau] = 0
    df = Calcul_Tx_Completion(arr, df, niveau)



    """
    for a in arr:
        df["total"] = df["total"] + df[a]

    df["Tx_Erreur"] = df["total"] / len(arr)
    df["Tx_Complet"] = 1 - df["Tx_Erreur"]
    """

    
    return df






