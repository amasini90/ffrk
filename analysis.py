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

def get_char_df(df,df_lm,includeHAbonus):
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
        TotWeight = df['Weight'][(df.Character==char) & (df.Owned==True)].sum()
        TotWeight += df_lm['Weight'][(df_lm.Character==char) & (df_lm.Owned==True)].sum()
        Score = TotWeight/(df['Weight'][df.Character==char].sum()+df_lm['Weight'][df_lm.Character==char].sum())
        if includeHAbonus == True:
            TotWeight += BonusHA(char)
        WeightChar[char] = [realm,elem,typ,Score,TotWeight,Rchain]
    
    # Create the DFs
    df6 = pd.DataFrame.from_dict(WeightChar, orient='index', columns=['Realm','Element','Type','Score','TotWeight','Rchain'])
    return df6

# TODO change the rank stuff - expand the DF list of elements in columns (example Ultimecia for Wind/Dark)
def get_ranked_chars(df,charDF,ChosenElem,ChosenType,includeHAbonus):
    '''
    Takes the Relics and Character DFs, and ranks the Characters based
    on a chosen Elem and type (PHY/MAG). Returns a new DF.
    '''
    output = {}
    usefulChar = charDF[(charDF.Score > 0) & (charDF.Type == ChosenType)]
    for char in usefulChar.index:
        if ChosenElem in usefulChar["Element"][char]:
            rank = (np.where(charDF["Element"][char]==ChosenElem)[0]+1)[0]
            # Weight and score must be computed based on relics of that ELEM only
            viewDF = df[(df.Character == char) & (df.Owned == True)]
            totweight = 0
            Echain = False
            for i in range(len(viewDF["Element"])):
                # If this row contains 'elem' I'm interested in it
                if ChosenElem in viewDF["Element"].iloc[i]:
                    totweight += viewDF["Weight"].iloc[i]
                    # See if Character has Chain of this ELEM
                    Echain = util.has_Echain(viewDF,ChosenElem)
            if includeHAbonus == True:
                totweight += BonusHA(char)
            output[char] = [rank,totweight,Echain]
    outDF = pd.DataFrame.from_dict(output, orient='index', columns=['Rank','TotWeight','Echain'])
    return outDF

def best_chain(df,orderedDF):
    '''
    When more than one Character have an Elem chain, choose the best one based on
    Chain rank and on Character Total Weight. Returns the name of the Character with 
    the best chain.
    '''
    charsWithChains = orderedDF[orderedDF.Echain==True]
    out = df[(df.Character.isin(list(charsWithChains.index.values))) & (df.Tier.str.contains('Chain'))].sort_values(by='Weight', ascending=False)
    if len(out[out.Weight == max(out.Weight)]) > 1:
        # TODO if 2 characters have same tier of chain, choose the best one
        ChainCarrier = out.Character[0]
    else:
        ChainCarrier = out.Character[0]
    return ChainCarrier
