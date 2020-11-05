import pandas as pd
import streamlit as st
import altair as alt


session = st.sidebar.selectbox("Which session to Look at?", ["Overview", "Recipients", "Institutions"])
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
    st.write("This session will provide detailed information of recipients in 2017.")
    st.header(s)
    st.subheader('Number of Recipients by Field of Study and Sex')
    st.altair_chart(fig1, use_container_width = False)
    total_plt = st.checkbox('Show me the data')
    if total_plt:
        col1, col2 = st.beta_columns([2, 3]) 
        col1.subheader("Total Number of Recipients")
        total = state[state["Field of Study"] == "Total"]
        total1 = total[state.State == s]
        total_s = alt.Chart(total1).mark_bar().encode(x="Sex",y='Number of People',color = "Sex")
        col1.altair_chart(total_s, use_container_width = True)
        col2.subheader("Recipient Data ")
        col2.write(state[state.State == s].iloc[:,1:].reset_index(drop=True))
        
    with st.beta_expander("See explanation for Missing Data"):
         st.write("""
        Missing data is recorded as NaN. It is because some data was suppressed to avoid disclosure of 
        confidential information. If the data for certain field of study is missing, the bar plot will not show that field 
        of study even if you selected it manually. Please note that 0s just means 0 person, it is different from missing data.
         """)
            
    #comparing states 
    st.sidebar.subheader("Compare with another state")
    s2 = st.sidebar.selectbox(
            "Choose a state to compare with",
             re.State.to_list()
        )
    compare = st.checkbox('Compare with another state')
    if compare:
        st2 = state[f&(state.State == s2)]  
        col1, col2 = st.beta_columns([3,3])
        ori = alt.Chart(filtered2).mark_bar().encode(
            x='Field of Study:O',
            y='sum(Number of People)',
            color= alt.Color('Sex:N',scale = alt.Scale(range=['lightcoral', 'powderblue']))
        )
        col1.write(s)
        col1.altair_chart(ori, use_container_width = True)
        
        st2_out = alt.Chart(st2).mark_bar().encode(
            x='Field of Study:O',
            y='sum(Number of People)',
           color= alt.Color('Sex:N',scale = alt.Scale(range=['lightcoral', 'powderblue'])
        ))
        col2.write(s2)
        col2.altair_chart(st2_out, use_container_width = True)

if session == "Institutions":
    ins = pd.read_excel("institution.xlsx", skiprows = 3)
    subjects_all = list(set(ins[ins.Rank == "-"]["Field and institution"].values))
    subjects = [i for i in subjects_all if "From" not in i]
    ins.loc[:,"Study Area"] = 0
    for i in subjects:
        a1 = ins[ins["Field and institution"] == i]
        idx = int(a1.index.values)
        if "20" in ins.loc[idx+1,"Field and institution"]:
            ins.loc[idx+2:idx+21,"Study Area"] = i
        else:
            ins.loc[idx+2:idx+22,"Study Area"] = i
    ins_total = ins[ins["Study Area"] == 0]
    ins_sep = ins[ins["Study Area"] != 0]
    
    #sidebar
    st.sidebar.subheader("Find Top Universities in field")
    f_select = st.sidebar.selectbox("Choose a Field:",
         list(set(ins_sep["Study Area"]))
             )
    top_num = st.sidebar.number_input("Number of Top Universities by Recipients(Max 20):", 1, 20)
    
    st.sidebar.subheader("Comparing Universities")
    u = st.sidebar.multiselect('Choose Some Universities: ',list(set(ins_sep["Field and institution"])), 
                               default = ["Harvard U.", "U. Michigan, Ann Arbor"]) 
   

    st.write("This session enables you to find out top 20/21 universities according to the number of recipients in different fields. Note that all data is constraint to top 20/21 in each field.")
    #search function:
    st.header("Information of the Field and Top Universities")
    string1 = "Total number of Doctorate recipients in " + f_select + " field of study is: " + str(int(ins_total[ins_total["Field and institution"] == f_select]["Doctorate recipients"]))
    st.write(string1)
    string2 = "Top " + str(top_num) + " Universities in " + f_select
    st.write(string2)
    top_u = ins_sep[ins_sep["Study Area"] == f_select].reset_index(drop=True).head(top_num)
    st.write(top_u)
    with st.beta_expander("See explanation for Ranking"):
         st.markdown("""
         Universities are ranked by number of Doctorate recipients in an descending order. Universities with same amount of recipients are ranked by alphabetical order. The variable **Rank** skips positions after equal ranking. 
         """)
            
    #Comparing Universites
    st.header("Comparing Top Universities")
    filter_u = [i in u for i in ins_sep["Field and institution"] ]
    ins_fil = ins_sep[filter_u]
    brush = alt.selection(type='interval')

    points = alt.Chart(ins_fil).mark_point().encode(
        x='Study Area',
        y='Doctorate recipients:Q',
        color=alt.condition(brush, 'Field and institution:N', alt.value('lightgray')),
        tooltip = ["Field and institution", "Study Area", "Doctorate recipients", "Rank"]
    ).properties(
        width=400,
        height=300
    ).add_selection(brush
    )
    bars = alt.Chart(ins_fil).mark_bar().encode(
        y='Field and institution:N',
        color='Field and institution:N',
        x='sum(Doctorate recipients):Q'
    ).transform_filter(
        brush
    )
    st.altair_chart(points & bars, use_container_width = True)
    with st.beta_expander("See explanation"):
         st.markdown("""
         Notice that some Universities does not have a value for certain Study Area, this does not mean that they do not have recipients in that area. Instead, it means they fail to be in top 20/21 universities for that specific field of study. 
         """)