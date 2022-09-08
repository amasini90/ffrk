from secrets import choice
import streamlit as st
import numpy as np
import pandas as pd
import plot,analysis
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
local_data_path = 'data/ffrk.csv'

def main():
    # Page configuration
    st.set_page_config(page_title="FFRK Helper")

    # Using object notation
    page = st.sidebar.radio(
        "Page",
    ("Relics","Accessories")
    )
    
    # Weights and Elements for Tiers
    #weights = {"Unique":0.536, "SSB":1.072, "BSB":0.625, "OSB":0.625, "GL":1.25, "GL2":1.5, "ASB":1.75,
    #        "AD":2.5, "Chain":1.25, "Chain2":1.75, "Chain3":1.8, "Chain4":2.5, "USB":1, "AW":2.25, "Sync":2.5,
    #        "OLB":1.75, "GLB":1, "Guardian":2, "DuAW":2.75}
    #weights_lm = {5:0.625, 6:1.5}

    weights = {"Unique":0.1, "SSB":0.5, "BSB":0.75, "OSB":1.0, "GL":1.25, "GL2":1.5, "ASB":2.0,
            "AD":2.75, "Chain":1.5, "Chain2":3.0, "Chain3":3.5, "Chain4":4.5, "USB":1.75, "AW":2.5, "Sync":3.0,
            "OLB":1.75, "GLB":1.0, "Guardian":2.0, "DuAW":4.0, "CLB":4.25}
    weights_lm = {5:0.5, 6:1.5}

    Elements = ["Fire","Ice","Lightning","Wind","Earth","Water","Holy","Dark"]
    MagiciteNames = ["Mateus","Syldra","Famfrit","Hecatoncheir","Quetzalcoatl","Phoenix","Deathgaze","Lakshmi","Manticore","Typhon","Geosgaeno","Adamantoise","Behemoth King","Belias","Ark","Madeen"]
    Magicite = pd.DataFrame({"PHY":MagiciteNames[:8], "MAG":MagiciteNames[8:]}, index=Elements)

    # Title of the App
    st.title('FFRK Helper')

    
    if page == 'Relics':
        # Read in the data
        df = pd.read_csv('./data/ffrk_sb.csv', header=0, index_col=0)
        df_lm = pd.read_csv('./data/ffrk_lm.csv', header=0, index_col=0)
        df_jobs = pd.read_csv('./data/ffrk_jobs.csv', header=0, index_col=0)

        # To see which realms have the most complete HA sets of heroes
        #df_ha = pd.read_csv('./data/heroartifacts.csv', header=0, index_col=0)
        #df_ha['Sum'] = df_ha.sum(axis=1)
        #agg = df_ha[df_ha['Sum']==199].groupby('Realm').count()
        #st.write(agg.sort_values(by='Sum',ascending=False))

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
        col1,col2=st.columns(2)
        OwnedFrac = round(100.*(Owned/(NotOwned+Owned)),1)
        col1.metric('Owned',str(Owned)+' ('+str(OwnedFrac)+'%)')
        col2.metric('Not Owned',str(NotOwned)+' ('+str(100-OwnedFrac)+'%)')

        with st.expander("Detailed breakdown of relics by Tier and Type"):
            RelicsbyTierandType = df.groupby(['Tier','Type'])['Tier'].count()
            RelicsbyTierandType_owned = df[df.Owned==True].groupby(['Tier','Type'])['Tier'].count()
            FractionbyTierandType = round(RelicsbyTierandType_owned/RelicsbyTierandType,3)
            FractionbyTierandType.rename("Fraction (%)", inplace=True)
            dff = FractionbyTierandType.to_frame()
            df7 = dff.style.format("{:.1%}", na_rep="-").background_gradient()
            st.table(df7)

        # Useful commands in case numbers do not round
        #st.table(df_lm[df_lm.Owned==True].groupby(['Realm',"Owned"])['Realm'].count())
        #st.table(df[(df.Owned==True) & (df.Tier == 'GL')].groupby(['Realm',"Owned"])['Realm'].count())

        st.header('My Legend Materia Overview:')
        col1,col2=st.columns(2)
        OwnedFrac_lm = round(100.*(Owned_lm/(NotOwned_lm+Owned_lm)),1)
        col1.metric('Owned',str(Owned_lm)+' ('+str(OwnedFrac_lm)+'%)')
        col2.metric('Not Owned',str(NotOwned_lm)+' ('+str(100-OwnedFrac_lm)+'%)')
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

        # Display Chains situation
        st.subheader('Chains')
        # Realm Chains
        with st.expander("Missing Realm Chains by lower Score"):
            RealmsWithChain = df[(df.Owned==True) & ((df.Tier=='Chain2') | (df.Tier=='Chain3') | (df.Tier=='Chain4')) & (df.Element=='ALL')].Realm.values
            RealmsMissingChain = set(df[(~df.Realm.isin(RealmsWithChain)) & (df.Realm!='KH') & (df.Realm!='FFBe')].Realm.values)
            maskedRealmDF = pd.Series(maskedScores, index=maskedRealms)
            if len(maskedRealmDF[maskedRealmDF.index.isin(RealmsMissingChain)].index) != 0:
                st.table(maskedRealmDF[maskedRealmDF.index.isin(RealmsMissingChain)].index)
            else:
                st.write('All the Realms are covered. Good!')
                
        # Elemental Chains
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

        with st.expander("Top 10 characters"):

            topRel = df[df.Owned==True].groupby("Character")['Weight'].sum()
            topLM = df_lm[df_lm.Owned==True].groupby("Character")['Weight'].sum()
            top10 = topRel.add(topLM, fill_value=0)

            st.table(top10.sort_values(axis=0,ascending=False).head(10))
        
        includeHAbonus = True
        disableHA = st.checkbox('Disable Hero Artifact Bonus?')
        if disableHA:
            includeHAbonus = False
        
        ##########################
        # Create the Character DF
        charDF = analysis.get_char_df(df,df_lm,includeHAbonus)
        ##########################

        Choice = st.radio('Which kind of party do you want to build?', ["5 Star Magicite","Realm","Elemental","Job"])

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

        elif Choice == "Job":
            ChosenJob = st.selectbox('Choose Job', ["Black Magic","White Magic","Summoning","Spellblade","Combat","Support","Celerity","Dragoon","Monk","Thief","Knight","Samurai","Ninja","Bard","Dancer","Machinist","Darkness","Sharpshooter","Witch","Heavy Physical"], format_func=lambda x: 'Select job' if x == '' else x)
            workers = df_jobs[df_jobs[ChosenJob]==6]
            
            inn = pd.merge(charDF, workers, left_index=True, right_index=True)
            orderedDF = inn.sort_values(by=['TotWeight','Score'],ascending=False)
            
            for i in range(5):
                col1,col2= st.columns([1,20])
                char = orderedDF.index[i].replace(" ", "")
                col1.image('./Images/Characters/'+char+'.png',width=50)
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
            orderedDF = outDF.sort_values(by=['Echain','TotWeight','Rank'],ascending=[False,False,True])
            
            if len(orderedDF[orderedDF.Echain==True]) > 1:
                # If more than one Chain is available, choose best
                neworder = []
                ChainCarrier = analysis.best_chain(df,orderedDF)
                neworder.append(ChainCarrier)
                for ix in outDF.sort_values(by=['TotWeight','Rank'],ascending=[False,True]).index:
                    if ix != ChainCarrier:
                        neworder.append(ix)

                for i in range(5):    
                    col3,col4 = st.columns([1,20])
                    char = neworder[i].replace(" ", "")
                    col3.image('./Images/Characters/'+char+'.png',width=50)
                    if i==0:
                        col4.write(neworder[i]+' [CHAIN]')
                    else:
                        col4.write(neworder[i])        
            else:

                for i in range(5):    
                    col3,col4 = st.columns([1,20])
                    char = orderedDF.index[i].replace(" ", "")
                    col3.image('./Images/Characters/'+char+'.png',width=50)
                    if (orderedDF['Echain'][i] == True) and (i==0):
                        col4.write(orderedDF.index[i]+' [CHAIN]')
                    else:
                        col4.write(orderedDF.index[i])
            
        ####
    elif page == 'Accessories':
        st.markdown('## Accessories Explorer')
        # Read in the data
        df = pd.read_csv('./data/ffrk_accessories.csv', header=0, index_col=0)
        df.fillna(0, inplace=True)
        cols=[i for i in df.columns if i not in ["Realm"]]
        for col in cols:
            df[col]=df[col].astype(int)
        df = df.reset_index()

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()

        AgGrid(df,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT', 
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=False,
        theme='blue', #Add theme color to the table
        enable_enterprise_modules=True,
        height=350, 
        width='100%',
        reload_data=True)

    # Footer
    link = '[Alberto Masini](http://www.linkedin.com/in/almasini/)'
    st.write('Author: '+link+' (2021); License CC BY-NC-ND 3.0')
    st.image('by-nc-nd.eu.png', width=60)

if __name__ == '__main__':
    main()