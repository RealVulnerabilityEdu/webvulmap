import os
import streamlit as st
import pandas as pd
 
print('running from ' + os.getcwd())
st.write("""
# My first app
Hello *world!*
""")
 
df = pd.read_csv("data/my_data.csv")
st.line_chart(df)
