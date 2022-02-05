import numpy as np
import pandas as pd
import streamlit as st 

def get_type(df,character):
    typ = df['Type'][df.Character==character].values
    x = [yy for yy in typ if type(yy)==str]
    values, counts = np.unique(x, return_counts=True)
    if len(counts) == 1:
        out = str(values[0])
        return out
    elif len(counts) == 0:
        return 'HEAL'
    else:
        out = str(values[counts == max(counts)][0])
        return out

def get_elem(df,character):
    elem = df['Element'][(df.Character==character) & (df.Owned==True)].values
    elementi = []
    for el in elem:
        xx = el.split()
        for x in xx:
            elementi.append(x)
    values, counts = np.unique(elementi, return_counts=True)
    sorted_indexes = np.argsort(counts)[::-1]
    out = values[sorted_indexes]
    if len(out) > 0:
        return out
    else:
        return [' ']