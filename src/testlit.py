import os
import streamlit as st
import pandas as pd
import sqlite3
 
print('running from ' + os.getcwd())
st.write("""
# My first app
Hello *world!*
""")
         
text_search = st.text_input('Search')

#test to see if the input is read correctly
st.write('You searched for: ', text_search)

