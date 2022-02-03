import streamlit as st
from streamlit import legacy_caching
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.dates as mdates
from matplotlib import rc
register_matplotlib_converters()
myFmt = mdates.DateFormatter('%d/%m')
font = {'family' : 'serif'}
rc('font', **font)

local_data_path = 'data/ffrk.csv'

def main():
    # Page configuration
    st.set_page_config(page_title="FFRK Helper")

    # Title of the App
    st.title('FFRK Helper')

    if st.button('Aggiorna'):
        legacy_caching.clear_cache()
    
    
    
    link = '[Alberto Masini](http://www.linkedin.com/in/almasini/)'
    st.write('Autore: '+link+' (2021); Licenza CC BY-NC-ND 3.0')
    st.image('by-nc-nd.eu.png', width=60)

if __name__ == '__main__':
    main()