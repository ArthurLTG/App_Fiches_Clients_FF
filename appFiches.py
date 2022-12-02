from emoji import emojize
from datetime import datetime, timedelta, date
import re
import pandas as pd 
import streamlit as st
import streamlit.components.v1 as components
from app_Fiches_BACK import *






# -------------------------------------------------------------------------------------------------------------------

def Display(df):
    list_groupe = sorted(df.Groupe.unique())
    list_mag = sorted(df.MagasinCreation.unique())
    list_date = sorted(df.MoisCreation.unique())

    with st.sidebar:
        
        select_mag = st.multiselect("MAGASIN", list_mag, list_mag)

        select_date = st.multiselect("DATE (Mois)", list_date, list_date)




    df2 = df[df.MagasinCreation.isin(select_mag) & df.MoisCreation.isin(select_date)]



    cols = df2.columns

    arr = []
    for col in cols:
        if (re.search(".*Complet*", col)) :
            arr.append(col)

    #st.warning("Modifier le fichier de base -> Exclure les magasins qui ne sont pas pertinents \n Détails sur le magasin 0")

    st.write(" ")
    st.write(" ")
    st.title("👥 Fiches Clients ")
    st.write(" ")

    colA, colB, colC= st.columns([1,1,1])
    with colA:
        st.metric(label="Taux de Completion (en %)",value= round(df2["Tx_Complet"].mean()*100,1))
        

    with colB:
        st.metric(label="Nombre de Clients créés",value= df2["Client"].count())

    with colC:
        Taux_PubEmail_OK = df2[df2["PubEmail"]==1]["PubEmail"].count()*100/ df2["Email"].count()
        st.metric(label="Taux_PubEmail_OK (en %)",value= round(Taux_PubEmail_OK, 0))

    #with colD:
        #dfgb_Tx_Complet = round(df2.groupby(["MagasinCreation","Type_client"])["Tx_Complet"].mean()*100,0)
        #Taux_Known_New = df2[df2["Type_client"]=="Known"]["Client"].count()*100 /df2["Client"].count()
        #st.metric(label="Taux_Clients_Connus (en %)",value=round(Taux_Known_New,0))


    # ----------------------------------------------------------------------
    st.markdown("---")
    df_Anonym = df2[df2["Nom"] == "A"][["MagasinCreation","Nom"]]
    df_Anonym = df_Anonym.groupby(["MagasinCreation"]).count()


    dfVolume_Fiche = df2[["MagasinCreation","Client"]].groupby(["MagasinCreation"]).count()
    dfVolume_Fiche = dfVolume_Fiche.merge(df_Anonym, on="MagasinCreation")
    dfVolume_Fiche["% Anonyme"] = (dfVolume_Fiche["Nom"]*100 / dfVolume_Fiche["Client"]).astype(int)



    arr.insert(0,"MagasinCreation")
    dfNote_Fiche = df2[arr].groupby(by="MagasinCreation").mean().apply(lambda x : round(x*100,0)).astype(int)

    df_PubEmail = df2[["MagasinCreation","PubEmail","Client"]].groupby(by="MagasinCreation",as_index=False).aggregate({"PubEmail":"sum","Client":"count"})
    df_PubEmail["% PubEmail"] = ((df_PubEmail["PubEmail"] / df_PubEmail["Client"])*100).astype(int)

    dfNote_Fiche = dfNote_Fiche.merge(dfVolume_Fiche["% Anonyme"], on="MagasinCreation", how='left')
    dfNote_Fiche = dfNote_Fiche.merge(df_PubEmail[["MagasinCreation","% PubEmail"]], on="MagasinCreation")







    colAA, colBB, colCC = st.columns([1,1,1])
    with colAA:
        st.info("Level 1 : Nom / Prenom / Email / Civilite")
        st.metric("Tx Complet lvl 1",round(df2["Tx_Complet_lvl1"].mean()*100,0))
        

    with colBB:
        st.warning("Level 2 : Code Postal / Pays / Portable")
        st.metric("Tx Complet lvl 2",round(df2["Tx_Complet_lvl2"].mean()*100,0))

    with colCC:
        st.success("Level 3 : Date de Naissance / Adresse")
        st.metric("Tx Complet lvl 3",round(df2["Tx_Complet_lvl3"].mean()*100,0))

    #st.table(dfRETAIL)

    
    def color_survived(val):
    
        if val <= 25:
            color = 'red'
        elif val > 25 and val <= 50:
            color = 'orange'
        elif val > 50 and val <= 75:
            color = 'yellow'
        else:
            color = 'green'
        
        return f'color: {color}'

    st.write(" ")
    st.write(" ")

    with st.expander("Details par Magasin"):
        #dfNote_Fiche = dfNote_Fiche.style.applymap(color_survived, subset=[['Tx_Complet_lvl1','Tx_Complet_lvl2']])
        
        st.table(dfNote_Fiche.set_index("MagasinCreation").style.applymap(color_survived, subset=['Tx_Complet_lvl1','Tx_Complet_lvl2','Tx_Complet_lvl3']))

    st.write(" ")
    st.write(" ")


    # ----------------------------------------------------------------------
    #st.markdown("---")


        


    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Par Magasin")
        st.write(" ")
        st.write("Taux de completion des fiches client")
        total_parMag_TxComplet = df2.groupby(["MagasinCreation"])["Tx_Complet"].mean().apply(lambda x: x*100)
        st.bar_chart(total_parMag_TxComplet, y="Tx_Complet")
        st.markdown("---")

        total_parMag_NbCreation = df2.groupby(["MagasinCreation"])["Email"].count()
        st.bar_chart(total_parMag_NbCreation, y="Email")
        st.markdown("---")
    
        st.bar_chart(df_PubEmail.set_index("MagasinCreation"), y="% PubEmail")
        st.markdown("---")

        #dfVolClientKnown2 = df2[df2["Type_client"]=="Known"].groupby(["MagasinCreation"])["Client"].count()
        #dfVolClient = df2[df2["Type_client"]=="New"].groupby(["MagasinCreation"])["Client"].count()
        #dfVolClientKnown2 = pd.merge(dfVolClient,dfVolClientKnown2, on="MagasinCreation")
        #dfVolClientKnown2["% Known"] = (dfVolClientKnown2["Client_y"]*100 / dfVolClientKnown2["Client_x"]).astype(int)
        #st.bar_chart(dfVolClientKnown2, y="% Known")
        
    

    with col2:
        st.subheader("Par Date")
        st.write(" ")
        st.write(" ")
        total_parDate_TxComplet = df2.groupby(["MoisCreation"])["Tx_Complet"].mean().apply(lambda x: x*100)
        st.line_chart(total_parDate_TxComplet, y="Tx_Complet")
        st.markdown("---")

        total_parDate_Nb_Creation = df2.groupby(["MoisCreation"])["Email"].count()
        st.line_chart(total_parDate_Nb_Creation, y="Email")
        st.markdown("---")

        df_PubEmail_Date = df2[["MoisCreation","PubEmail","Client"]].groupby(by="MoisCreation",as_index=False).aggregate({"PubEmail":"sum","Client":"count"})
        df_PubEmail_Date["% PubEmail"] = ((df_PubEmail_Date["PubEmail"] / df_PubEmail_Date["Client"])*100).astype(int)
        st.line_chart(df_PubEmail_Date.set_index("MoisCreation"), y="% PubEmail")
        st.markdown("---")

        #dfVolClientKnown = df2[df2["Type_client"]=="Known"].groupby(["MoisCreation"])["Client"].count()
        #dfVolClient = df2[df2["Type_client"]=="New"].groupby(["MoisCreation"])["Client"].count()
        #dfVolClientKnown = pd.merge(dfVolClient,dfVolClientKnown, on="MoisCreation")
        #dfVolClientKnown["% Known"] = (dfVolClientKnown["Client_y"]*100 / dfVolClientKnown["Client_x"]).astype(int)
        #st.line_chart(dfVolClientKnown, y="% Known")
        
    # ----------------------------------------------------------------------
    st.markdown("---")

    st.subheader("Détails des fiches client")
    st.dataframe(df2[["Nom","Prenom","Email","Civilite","codepostal","Pays","Portable","Adresse1","DateNaissance","Tx_Complet"]])

    st.date_input('lol')

    #with open( "style.css" ) as css:
        #st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


    # ---------------------------------------------------------------------------------------------------------------------




# -------------------------------------------------------------------------------------------------------------------








# -------------------------------------------------------------------------------------------------------------------
st.set_page_config(layout="wide")
c1, c2 = st.columns([1,5])

with c1:
    st.image("https://d3k81ch9hvuctc.cloudfront.net/company/KyNgj5/images/83d8ac85-eb81-466f-bd68-3ab849e4a9ba.png", width=300)

with c2:
    st.title("Base Clients & Magasins")


  




#select_mag = st.selectbox("STORE", sorted(df.Magasin.unique()))






# ----------------------------------------------------------------------



st.markdown("---")





file = st.file_uploader(label="Importer le fichier de création (.csv)", type='.csv', key='fileUpload')
if file is not None:
    st.success("Upload ✅")
    df = pd.read_csv(file)
    df = Traitement(df)
    df = df[df["Groupe"]=="RETAIL"]
    Display(df)
   
    

st.markdown("---")







#df["Date Dernier Achat"] = df["Date Dernier Achat"].apply(lambda x: datetime.strptime(str(x), '%Y-%m-%d').date())
#df["temps_depuis_achat"] = df["Date Dernier Achat"].apply(lambda x : date.today() - x)
#df["temps_depuis_achat_numeric"] = df["temps_depuis_achat"].apply(lambda x : int(str(x).split(" ")[0]))
#del df["temps_depuis_achat"]



#df.Date = df.Date.apply(lambda x: x.date())






