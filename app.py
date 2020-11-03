#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import streamlit as st


# In[3]:


st.title('My first app')
st.text('Streamlit is great')


# In[ ]:


df = pd.read_excel("change_over_years.xlsx", skiprows = 3)
df["% change from previous year"] = pd.to_numeric(df['% change from previous year'], errors = 'coerce')
df = df.fillna(method = "ffill")
cols = st.sidebar.multiselect('Select countries', df.columns[1:].to_list(), default = "% change from previous year")
values = st.sidebar.slider(
    'Select a range of values',
    min(df.Year), max(df.Year), (1997, 2010))
col_fil = df[cols]
years = [i in range(values[0],values[1]+1) for i in df.Year]
filtered = col_fil[years]
st.line_chart(filtered)
