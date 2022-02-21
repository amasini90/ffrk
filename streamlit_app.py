import streamlit as st
from streamlit import legacy_caching
import numpy as np
import pandas as pd
import plot,analysis
from PIL import Image
local_data_path = 'data/ffrk.csv'

def main():
    # Page configuration
    st.set_page_config(page_title="FFRK Helper")

    # Title of the App
    st.title('FFRK Helper')

    if st.button('Update/Refresh'):
        legacy_caching.clear_cache()
    
    # Read in the data
    df = pd.read_csv('ffrk_sb.csv', header=0, index_col=0)
    # Weights and Elements for Tiers
    weights = {"Unique":0.536, "SSB":1.072, "BSB":0.625, "OSB":0.625, "GL":1.25, "GL2":1.5, "ASB":1.75,
            "AD":2.5, "Chain":1.25, "Chain2":1.75, "Chain3":1.8, "Chain4":2.5, "USB":1, "AW":2.25, "Sync":2.5,
            "OLB":1.75, "GLB":1, "Guardian":2, "DuAW":2.75}
    Elements = ["Fire","Ice","Lightning","Wind","Earth","Water","Holy","Dark"]
    
    # Apply weights as a new column
    df['Weight'] = df['Tier'].map(weights)

    # Total number of Owned VS Not-Owned SBs
    NotOwned = df.groupby(["Owned"]).count().values[0][0]
    Owned = df.groupby(["Owned"]).count().values[1][0]
    
    #### Overview of Relics situation
    st.header('My Relics Overview:')
    col1,col2,col3=st.columns(3)
    col1.metric('Owned',Owned)
    col2.metric('Not Owned',NotOwned)
    col3.metric('Fraction',str(round(100.*(Owned/(NotOwned+Owned)),1))+'%')
    #####

    #### Scores and Recommendations
    st.header('Scores')
    st.subheader('Recommended pulls:')
    # Compute the total Scores by REALM grouping by the appropriate keys
    ww = df.groupby(["Realm","Owned"]).sum()
    scores={}
    for realm,owned in ww.index:
        if realm not in scores:
            scores[realm] = ww.loc[realm].loc[True]/(ww.loc[realm].loc[False]+ww.loc[realm].loc[True])
    df3 = pd.DataFrame(scores)
    df3 = df3.T
    
    # Realms analysis
    realms,scores = analysis.get_realm_scores(df3)
    realms = np.array(realms)
    scores = np.array(scores)
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

    #col2.metric('PHY Elem',df4[df4==np.min(df4)].index[0])
    #col3.metric('MAG Elem',df5[df5==np.min(df5)].index[0])

    # Display figures
    fig = plot.plot_realms(realms,scores)
    st.plotly_chart(fig, use_container_width=True)

    fig = plot.plot_elements(df4.sort_values().index,df4.sort_values().values,df5.sort_values().index,df5.sort_values().values)
    st.plotly_chart(fig, use_container_width=True)
    ####

    #### Party composition
    st.subheader('Party suggestions:')
    st.markdown('Healers not included.')

    st.markdown('Which kind of party do you want to build?')
    ChooseRealm = st.checkbox('Realm')
    ChooseElem = st.checkbox('Element')

    # Create the Character DF
    charDF = analysis.get_char_df(df)
    #st.table(charDF)

    if ChooseRealm:
        ChosenRealm = st.selectbox('Realm', ['I',"II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII",'XIV',"XV","FFT","T-0","Core","FFBe"], format_func=lambda x: 'Select realm' if x == '' else x)
        for i in range(5):
            orderedDF = charDF[charDF.Realm == ChosenRealm].sort_values(by=['Rchain','TotWeight','Score'],ascending=False)
            col1,col2 = st.columns([1,20])
            char = orderedDF.index[i].replace(" ", "")
            col1.image('./Images/Characters/'+char+'.png',width=50)
            if orderedDF['Rchain'][i] == True:
                col2.write(orderedDF.index[i]+' [CHAIN]')
            else:
                col2.write(orderedDF.index[i])
            

    if ChooseElem:
        st.markdown('Of which type (PHY/MAG) and element will it be?')
        ChosenElem = st.selectbox('Element', Elements, format_func=lambda x: 'Select element' if x == '' else x)
        ChosenType = st.selectbox('Type', ["PHY","MAG"], format_func=lambda x: 'Select type' if x == '' else x)

        outDF = analysis.get_ranked_chars(df,charDF,ChosenElem,ChosenType)

        for i in range(5):
            orderedDF = outDF.sort_values(by=['Echain','Rank','TotWeight'],ascending=[False,True,False])
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