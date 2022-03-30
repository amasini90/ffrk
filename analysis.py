import pandas as pd
import util 
import numpy as np

def get_elem_scores(df,Elements):
    '''
    Computes the scores (summing weights) for each Element and Type, 
    and returns two dataframes, one for PHY and one for MAG.
    '''
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

    return df4,df5

def BonusHA(char):
    '''
    Compute the bonus for a character given by the amount and level
    of their Hero Artifacts
    '''
    df_ha = pd.read_csv("data/heroartifacts.csv", header=0, index_col=0)
    aux_df = df_ha[df_ha.index == char]
    if len(aux_df) > 0:
        output = aux_df.drop("Realm", axis=1).values.sum()/199.0
        # Should take into account if there is the whole set.
        ll = len(aux_df[aux_df.drop("Realm", axis=1).values != 0])
    else:
        output = 0.
        ll = 0.
    return output*ll

def get_char_df(df,includeHAbonus=True):
    '''
    Computes the total weight associated to the relics I have for each character.
    Also, assess wheter the character has a Realm (>= LV2) Chain.
    '''
    WeightChar = {}
    for item in df.groupby(df.Character):
        char = item[0]
        realm = df['Realm'][df.Character==char].values[0]
        typ = util.get_type(df,char)
        elem = util.get_elem(df,char)
        Rchain = util.has_Rchain(df,char)
        ww = df['Weight'][(df.Character==char) & (df.Owned==True)].sum()/df['Weight'][df.Character==char].sum()
        if includeHAbonus == True:
            ww += BonusHA(char)
        WeightChar[char] = [realm,elem,typ,ww,df['Weight'][(df.Character==char) & (df.Owned==True)].sum(),Rchain]
    
    # Create the DFs
    df6 = pd.DataFrame.from_dict(WeightChar, orient='index', columns=['Realm','Element','Type','Score','TotWeight','Rchain'])
    return df6

def get_ranked_chars(df,charDF,ChosenElem,ChosenType,includeHAbonus=True):
    '''
    Takes the Relics and Character DFs, and ranks the Characters based
    on a chosen Elem and type (PHY/MAG). Returns a new DF.
    '''
    output = {}
    for char in charDF.index:
        if charDF.Score[char] > 0:
            if (charDF["Type"][char] == ChosenType) and (ChosenElem in charDF["Element"][char]):
                rank = (np.where(charDF["Element"][char]==ChosenElem)[0]+1)[0]
                # Ideally, weight and score should be computed based on relics of that ELEM only.
                viewDF = df[(df.Character == char) & (df.Owned == True)]
                totweight = 0
                Echain = False
                for i in range(len(viewDF["Element"])):
                    # If this row contains 'elem' I'm interested in it
                    if ChosenElem in viewDF["Element"].iloc[i]:
                        totweight += viewDF["Weight"].iloc[i]
                        # See if Character has Chain of this ELEM
                        Echain = util.has_Echain(viewDF,ChosenElem)
                # Add the bonus from Hero Artifact
                if includeHAbonus == True:
                    bonus = BonusHA(char)
                    totweight += bonus
                output[char] = [rank,totweight,Echain]
    outDF = pd.DataFrame.from_dict(output, orient='index', columns=['Rank','TotWeight','Echain'])
    return outDF    