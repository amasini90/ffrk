import streamlit as st
from streamlit import legacy_caching
import numpy as np
import pandas as pd
import plot
local_data_path = 'data/ffrk.csv'

def main():
    # Page configuration
    st.set_page_config(page_title="FFRK Helper")

    # Title of the App
    st.title('FFRK Helper')

    if st.button('Aggiorna'):
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
    
    st.subheader('My Relics Overview:')
    col1,col2=st.columns(2)
    col1.metric('Owned',Owned)
    col2.metric('Not Owned',NotOwned)

    # Compute the total Scores by REALM grouping by the appropriate keys
    ww = df.groupby(["Realm","Owned"]).sum()
    scores={}
    for realm,owned in ww.index:
        if realm not in scores:
            scores[realm] = ww.loc[realm].loc[True]/(ww.loc[realm].loc[False]+ww.loc[realm].loc[True])
    df3 = pd.DataFrame(scores)
    df3 = df3.T

    # Results of the REALM check: which ones I should focus on first?
    st.subheader('Sorted scores by Realm:')
    #st.table(df3.sort_values(by="Weight", axis=0))
    realms,scores=[],[]
    for item in df3.sort_values(by="Weight", axis=0).index:
        realms.append(item)
    for item in df3.sort_values(by="Weight", axis=0).values:
        scores.append(item[0])
    # Plotly Figure here
    fig = plot.plot_realms(realms,scores)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Sorted scores by Element:')
    # Elemental part, split by PHY and MAG types; here is more complicated - I need to look for 'elem' in the Element
    # string and then look up if it's PHY or MAG (or both)
    # First, I create 2 dictionaries (one PHY, one MAG)
    PHYelem_dict, MAGelem_dict = {},{}
    # Then, I loop on Elements
    for elem in Elements:
        scoreTot, score1 = 0,0
        scoreTotMag, score1Mag = 0,0
        # I loop on the whole df
        for i in range(len(df["Element"])):
            
            # If this row contains 'elem' (or "ALL") and Type is not NaN, I'm interested in it
            if (type(df["Type"].iloc[i]) == str) and ((elem in df["Element"].iloc[i]) or ("ALL" in df["Element"].iloc[i])):
                
                # PHY part
                if "PHY" in df["Type"].iloc[i]:

                    scoreTot += df["Weight"].iloc[i]
                    if df["Owned"].iloc[i] == True:
                        score1 += df["Weight"].iloc[i]
                        
                # MAG part
                if "MAG" in df["Type"].iloc[i]:
                
                    scoreTotMag += df["Weight"].iloc[i]
                    if df["Owned"].iloc[i] == True:
                        score1Mag += df["Weight"].iloc[i]
        
        # Update the dictionaries
        PHYelem_dict[elem] = score1/scoreTot
        MAGelem_dict[elem] = score1Mag/scoreTotMag

    # Create the DFs
    df4 = pd.Series(PHYelem_dict)
    df5 = pd.Series(MAGelem_dict)

    # Elements
    fig = plot.plot_elements(df4.sort_values().index,df4.sort_values().values,df5.sort_values().index,df5.sort_values().values)
    st.plotly_chart(fig, use_container_width=True)


    link = '[Alberto Masini](http://www.linkedin.com/in/almasini/)'
    st.write('Autore: '+link+' (2021); Licenza CC BY-NC-ND 3.0')
    st.image('by-nc-nd.eu.png', width=60)

if __name__ == '__main__':
    main()