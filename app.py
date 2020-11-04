import pandas as pd
import streamlit as st
import altair as alt


session = st.sidebar.selectbox("Which session to Look at?", ["Overview", "Recipients"])
st.title('PhDs awarded in the US')

if session == "Overview":
    df = pd.read_excel("overview.xlsx", skiprows = 4)
    df = df.iloc[:,:3]
    df.columns = ["Year", "Doctorate-granting institutions", "Doctorate recipients"]
    df["Institutions - Percentage change"] = (df.iloc[:,1] - df.iloc[:,1].shift(1) )/df.iloc[:,1].shift(1) * 100
    df["Recipients - Percentage change"] = (df.iloc[:,2] - df.iloc[:,2].shift(1) )/df.iloc[:,2].shift(1) * 100
    
    #sidebar
    st.sidebar.subheader("Overview")
    year_range =  st.sidebar.slider('Select a range of years',
        min(df.Year+1), max(df.Year), (1997, 2010))
    cols = st.sidebar.multiselect('Which feature to look at', df.columns[-2:].to_list(), 
                              default = df.columns[-2:].to_list())

    years = [i in range(year_range[0],year_range[1]+1) for i in df.Year]
    filtered = df[years]
    col_fil = filtered[cols]
    col_fil["Year"] = filtered.Year
    
    #graph:refer to https://altair-viz.github.io/gallery/multiline_tooltip.html
    source = col_fil.melt("Year", var_name='category', value_name='y')
    source["y"] = round(source.y,3)
    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['Year'], empty='none')
    
    line = alt.Chart(source).mark_line().encode(
        x='Year',
        y=alt.Y('y:Q', axis=alt.Axis(title='Percentage Change')),
        color='category:N'
    )
    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart(source).mark_point().encode(
        x='Year',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'y:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart(source).mark_rule(color='gray').encode(
        x='Year',
    ).transform_filter(
        nearest
    )

    # Put the five layers into a chart and bind the data
    output = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=600, height=300
    )
    
    #show graph
    st.subheader('Overview of Percentage Change Over Years')
    st.altair_chart(output, use_container_width = True)
    
    with st.beta_expander("See explanation"):
         st.write("""
             The percentage change was calculated by   
             First: work out the difference between the two numbers we are comparing.   
             Then: divide the difference by the original number and multiply the answer by 100.   
             %Change = Difference ÷ Original Number × 100
         """)

if session == "Recipients": 
    re = pd.read_excel("re.xlsx", skiprows = 4)
    re.iloc[0,0] = "United States"
    re.columns = ["State", "Total Male", "Total Female", "Life_sciences Male", "Life_sciences Female",
                 "Physical/earth_sciences Male", "Physical/earth_sciences Female",
                 "Math/CS Male", "Math/CS Female", "Psychology/social_sciences Male",
                 "Psychology/social_sciences Female", "Engineering Male", "Engineering Female",
                 "Education Male", "Education Female", "Humanities/arts Male", "Humanities/arts Female",
                 "Others Male", "Others Female"]
    re.iloc[:,1:] = re.iloc[:,1:].apply(pd.to_numeric, errors = "coerce") 
    melted = re.melt(id_vars = "State", var_name='category', value_name='Number of People')
    cat_split = melted.category.str.split().apply(pd.Series)
    melted["Field of Study"] = cat_split.iloc[:,0]
    melted["Sex"] = cat_split.iloc[:,1]
    state = melted[["State", "Field of Study", "Sex", "Number of People"]]
    
    #sidebar
    st.sidebar.subheader("Pick A State")
    s = st.sidebar.selectbox(
        "Choose a state from the following List",
         re.State.to_list()
    )
    m = st.sidebar.multiselect('Choose which field of study',['Engineering','Humanities/arts','Math/CS','Education',                                               'Psychology/social_sciences','Physical/earth_sciences','Life_sciences','Others'], 
                               default =['Engineering','Humanities/arts','Math/CS','Education',
                                         'Psychology/social_sciences','Physical/earth_sciences','Life_sciences','Others'])
    #filter
    f = [i in m for i in state["Field of Study"]]
    filtered2 = state[f&(state.State == s)]
    fig1 = alt.Chart(filtered2).mark_bar().encode(
        x='Sex:O',
        y='Number of People:Q',
        color='Sex:N',
        column= alt.Column('Field of Study:N', header=alt.Header(labelAngle=-90, labelAlign='right'))
    )
    st.header(s)
    st.subheader('Number of Recipients by Field of Study and Sex')
    st.altair_chart(fig1, use_container_width = False)
