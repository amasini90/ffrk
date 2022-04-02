from secrets import choice
import streamlit as st
from streamlit import legacy_caching
import numpy as np
import pandas as pd
import plot,analysis
local_data_path = 'data/ffrk.csv'

def main():
    # Page configuration
    st.set_page_config(page_title="FFRK Helper")

    # Weights and Elements for Tiers
    weights = {"Unique":0.536, "SSB":1.072, "BSB":0.625, "OSB":0.625, "GL":1.25, "GL2":1.5, "ASB":1.75,
            "AD":2.5, "Chain":1.25, "Chain2":1.75, "Chain3":1.8, "Chain4":2.5, "USB":1, "AW":2.25, "Sync":2.5,
            "OLB":1.75, "GLB":1, "Guardian":2, "DuAW":2.75}
    weights_lm = {5:0.625, 6:1.5}
    Elements = ["Fire","Ice","Lightning","Wind","Earth","Water","Holy","Dark"]
    MagiciteNames = ["Mateus","Syldra","Famfrit","Hecatoncheir","Quetzalcoatl","Phoenix","Deathgaze","Lakshmi","Manticore","Typhoon","Geosgaeno","Adamantoise","Behemoth King","Belias","Ark","Madeen"]
    Magicite = pd.DataFrame({"PHY":MagiciteNames[:8], "MAG":MagiciteNames[8:]}, index=Elements)

    # Title of the App
    st.title('FFRK Helper')

    if st.button('Update/Refresh'):
        legacy_caching.clear_cache()
    
    # Read in the data
    df = pd.read_csv('./data/ffrk_sb.csv', header=0, index_col=0)
    df_lm = pd.read_csv('./data/ffrk_lm.csv', header=0, index_col=0)

    # Apply weights as a new column
    df['Weight'] = df['Tier'].map(weights)
    df_lm["Weight"] = df_lm['Tier'].map(weights_lm)

    # Total number of Owned VS Not-Owned SBs
    NotOwned = df.groupby(["Owned"]).count().values[0][0]
    Owned = df.groupby(["Owned"]).count().values[1][0]

    # Total number of Owned VS Not-Owned LMs
    NotOwned_lm = df_lm.groupby(["Owned"]).count().values[0][0]
    Owned_lm = df_lm.groupby(["Owned"]).count().values[1][0]

    #### Overview of Relics and LM situation
    st.header('My Relics Overview:')
    col1,col2,col3=st.columns(3)
    col1.metric('Owned',Owned)
    col2.metric('Not Owned',NotOwned)
    col3.metric('Fraction',str(round(100.*(Owned/(NotOwned+Owned)),1))+'%')

    with st.expander("Detailed breakdown of relics by Tier and Type"):
        RelicsbyTierandType = df.groupby(['Tier','Type'])['Tier'].count()
        RelicsbyTierandType_owned = df[df.Owned==True].groupby(['Tier','Type'])['Tier'].count()
        FractionbyTierandType = round(RelicsbyTierandType_owned/RelicsbyTierandType,3)
        FractionbyTierandType.rename("Fraction (%)", inplace=True)
        dff = FractionbyTierandType.to_frame()
        df7 = dff.style.format("{:.1%}", na_rep="-").background_gradient()
        st.table(df7)

    # Useful commands in case numbers do not round
    #st.table(df[df.Owned==True].groupby(['Tier',"Owned"])['Tier'].count())
    #st.table(df[(df.Owned==True) & (df.Tier == 'AW')].groupby(['Realm',"Owned"])['Realm'].count())

    st.header('My Legend Materia Overview:')
    col1,col2,col3=st.columns(3)
    col1.metric('Owned',Owned_lm)
    col2.metric('Not Owned',NotOwned_lm)
    col3.metric('Fraction',str(round(100.*(Owned_lm/(NotOwned_lm+Owned_lm)),1))+'%')
    #####

    #### Scores and Recommendations
    st.header('Recommended pulls:')
    # Compute the total Scores by REALM grouping by the appropriate keys
    ww = df.groupby(["Realm","Owned"]).sum()
    ww_lm = df_lm.groupby(["Realm","Owned"]).sum()
    scores={}
    for realm,owned in ww.index:
        if realm not in scores:
            try:
                lmScore = ww_lm.loc[realm]["Weight"].loc[True]
                lmTotScore = ww_lm.loc[realm]["Weight"].loc[False]+lmScore
                relicScore = ww.loc[realm]["Weight"].loc[True]
                relicTotScore = relicScore+ww.loc[realm]["Weight"].loc[False]

                scores[realm] = (relicScore/relicTotScore + lmScore/lmTotScore)/2.
            except Exception:
                scores[realm] = relicScore/relicTotScore
    
    df3 = pd.Series(scores,index=scores.keys(),name="Weight")
    df3 = df3.sort_values()

    # Realms analysis
    realms = df3.index.values
    scores = df3.values
    maskRealms = (realms != 'KH') & (realms != 'FFBe')
    maskedRealms = realms[maskRealms]
    maskedScores = scores[maskRealms]
    # Elemental analysis
    df4,df5 = analysis.get_elem_scores(df,Elements)
    avg = (df4+df5)/2

    # Display suggested pulls
    WeakestElem = avg[avg==np.min(avg)].index[0]
    WeakestRealm = maskedRealms[maskedScores==np.min(maskedScores)][0]

    col1,col2=st.columns(2)
    col1.metric('Realm',WeakestRealm)
    col2.metric('Element',WeakestElem)
    empty,colb=st.columns(2)
    colb.image('./Images/Elements/FFRK_'+WeakestElem+'_Element.png', width=30)

    # Display LV2 Chains situation
    st.subheader('Chains')
    # Realm LV2 Chains
    with st.expander("Missing Realm Chains by lower Score"):
        RealmsWithChain = df[(df.Owned==True) & ((df.Tier=='Chain2') | (df.Tier=='Chain3') | (df.Tier=='Chain4')) & (df.Element=='ALL')].Realm.values
        RealmsMissingChain = set(df[(~df.Realm.isin(RealmsWithChain)) & (df.Realm!='KH') & (df.Realm!='FFBe')].Realm.values)
        maskedRealmDF = pd.Series(maskedScores, index=maskedRealms)
        if len(maskedRealmDF[maskedRealmDF.index.isin(RealmsMissingChain)].index) != 0:
            st.table(maskedRealmDF[maskedRealmDF.index.isin(RealmsMissingChain)].index)
        else:
            st.write('All the Realms are covered. Good!')
            
    # Elemental LV2 Chains
    with st.expander("Missing Elemental Chains by lower Score"):
        mis = 0
        for typ in ["PHY", "MAG"]:
            for el in Elements: 
                view = df[(df.Owned==True) & ((df.Tier=='Chain2') | (df.Tier=='Chain3') | (df.Tier=='Chain4')) & (df.Element==el) & (df.Type==typ)]
                if len(view) == 0:
                    mis += 1
                    st.write(el,typ)
        if mis == 0:
            st.write('All the Elements are Types are covered. Good!')
     
      
    # Optionally display figures
    st.subheader('Scores')
    with st.expander("Distributions of scores across Realms and Elements"):
        fig = plot.plot_realms(realms,scores)
        st.plotly_chart(fig, use_container_width=True)

        fig = plot.plot_elements(df4.sort_values().index,df4.sort_values().values,df5.sort_values().index,df5.sort_values().values)
        st.plotly_chart(fig, use_container_width=True)
    ####

    #### Party composition
    st.subheader('Party suggestions:')
    st.markdown('Healers not included. Hero Artifact bonus is included by default.')
    includeHAbonus = True
    disableHA = st.checkbox('Disable Hero Artifact Bonus?')
    if disableHA:
        includeHAbonus = False
    
    # Create the Character DF
    charDF = analysis.get_char_df(df,includeHAbonus)
    #st.write(charDF)

    Choice = st.selectbox('Which kind of party do you want to build?', ["5 Star Magicite","Realm","Elemental"])

    if Choice == "Realm":

        ChosenRealm = st.selectbox('Choose Realm', ['I',"II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII",'XIV',"XV","FFT","T-0","Core","FFBe"], format_func=lambda x: 'Select realm' if x == '' else x)
        orderedDF = charDF[charDF.Realm == ChosenRealm].sort_values(by=['Rchain','TotWeight','Score'],ascending=False)
        
        for i in range(5):
            col1,col2= st.columns([1,20])
            char = orderedDF.index[i].replace(" ", "")
            col1.image('./Images/Characters/'+char+'.png',width=50)
            if orderedDF['Rchain'][i] == True:
                col2.write(orderedDF.index[i]+' [CHAIN]')
            else:
                col2.write(orderedDF.index[i])
    
    else:
        if Choice == "Elemental":

            ChosenElem = st.selectbox('Choose Element', Elements, format_func=lambda x: 'Select element' if x == '' else x)
            ChosenType = st.selectbox('Choose Type', ["PHY","MAG"], format_func=lambda x: 'Select type' if x == '' else x)

        elif Choice == "5 Star Magicite":
        
            ChosenEnemy = st.selectbox('Choose Magicite', sorted(MagiciteNames), format_func=lambda x: 'Select Enemy' if x == '' else x)
            if ChosenEnemy:
                ChosenElem = Magicite[Magicite.values == ChosenEnemy].index.values[0]
                ChosenType = Magicite.T[Magicite.T.values == ChosenEnemy].index.values[0]

        outDF = analysis.get_ranked_chars(df,charDF,ChosenElem,ChosenType,includeHAbonus)
        orderedDF = outDF.sort_values(by=['Echain','Rank','TotWeight'],ascending=[False,True,False])
        
        for i in range(5):    
            col3,col4 = st.columns([1,20])
            char = orderedDF.index[i].replace(" ", "")
            col3.image('./Images/Characters/'+char+'.png',width=50)
            if orderedDF['Echain'][i] == True:
                col4.write(orderedDF.index[i]+' [CHAIN]')
            else:
                col4.write(orderedDF.index[i])
        
    ####

    # Footer
    link = '[Alberto Masini](http://www.linkedin.com/in/almasini/)'
    st.write('Author: '+link+' (2021); License CC BY-NC-ND 3.0')
    st.image('by-nc-nd.eu.png', width=60)

if __name__ == '__main__':
    main()