#Importing basic libraries 
import pandas as pd
import numpy as np

#libraries for matplotlib charts
#from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams

#libraries for Plotly graphs
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

import json

#building the app
import streamlit as st #creating an app
from streamlit_folium import folium_static 
import folium #using folium on 

#import pydeck as pdk

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import holoviews as hv
hv.extension("bokeh")


# set page layout
st.set_page_config(
    page_title="World Data Food Hub",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)



# HEADER
#st.write('<style>body { margin: 0; font-family: Helvetica; font-size:20px} .header{padding: 20px 16px; background: #555; color: #f1f1f1; position:fixed;top:0;} .sticky { position: fixed; top: 0; width: 100%;} </style><div class="header" id="myHeader">'+str("Data Rural Hub")+'</div>', unsafe_allow_html=True)

#IMAGE IN THE SIDEBAR
from PIL import Image
st.sidebar.image('images_foodtech/logoPNG.png', width=110)

st.sidebar.title('Data Rural Hub')
st.sidebar.markdown('''Explore digital solutions and issues towards sustainable Food Systems''')
st.sidebar.subheader('''Navigation''')

# Navigation buttoms
st.sidebar.button("1. Food Issues", key="1")
st.sidebar.button("2. Digital solutions", key="2")
st.sidebar.button("3. Tools", key="2")
st.sidebar.button("4. About", key="2")


st.sidebar.markdown("ℹ️ All the Charts are interactive. Scroll the mouse over the Charts to feel the interactive features like Tool tip, Zoom, Pan")

st.sidebar.markdown ('---')

# Footer
st.sidebar.markdown('''Designed by: **Merlyn J. Hurtado**  ''')
st.sidebar.markdown(''' Supported by ''')
st.sidebar.image('images_foodtech/200px-CRI-logo-sq.svg.png', width=50)


# STEP 1. READING THE DATA

st.cache(allow_output_mutation=True)
def load_data():
    #DF shapes of countries for mapping
    # Columns  in country_shapes
    skipcols =['ID', 'HRinfo ID', 'RW ID', 'm49 numerical code', 'FTS API ID',
       'Appears in UNTERM list', 'Appears in DGACM list',
       'ISO 3166-1 Alpha 2-Codes',
       'x Alpha2 codes', 'x Alpha3 codes', 'Preferred Term', 'm49 Alt Term',
       'ISO Alt Term', 'UNTERM Alt Term', 'FTS Alt Term', 'HRinfo Alt Term',
       'RW Short Name', 'RW API Alt Term', 'French Short',
       'Spanish Short', 'Russian Short', 'Chinese Short', 'Arabic Short',
       'Admin Level', 'Intermediate Region Code',
       'Intermediate Region Name', 'Regex', 'Concatenation']
    country_shapes = json.load(open('data/world-countries.json'))
    
    # Main Dataset 
    # Columns in Foodtech
    skipcols_tech = ['Comparison Tech',
                                    'Tech', 'Tech2', 'Tech3', 'Tech4',
                                    'info additional',
                                    'Donor1', 'Donor2', 'Donor3', 'Donor 4', 'Donor5','OThers donors',
                                    'Unnamed: 25', 'Unnamed: 26',
                                     'Level1', 'Level2', 'Level3', 'Level4','Level5',
                                     'Issues', 'Donors double chekc']
    foodtech = pd.read_csv('data/food_tech.csv', usecols=lambda x: x not in skipcols_tech, index_col=0).reset_index()
    foodtech.rename(columns = {'Origin_country':'Country','App Name':'App_name'}, inplace = True)
    # Dataset countries coordinates from Google Drive
    countries =pd.read_csv('data/Countries & Territories Taxonomy MVP - C&T Taxonomy with HXL Tags.csv',  usecols=lambda x: x not in skipcols, index_col=0).reset_index()
    #Changing column name to be equal to the names in df country_shapes and df foodtech
    countries.rename(columns = {'ISO 3166-1 Alpha 3-Codes':'ISO3'}, inplace = True)
    countries.rename(columns = {'English Short':'Country'}, inplace = True)
    # dataset Donors class
    donorsclass = pd.read_csv('data/food_tech_donors.csv', usecols=lambda x: x not in skipcols_tech, index_col=0).reset_index()
   
    return country_shapes, foodtech,countries, donorsclass
country_shapes,foodtech, countries, donorsclass = load_data()


#This row doesn't have relevant information
countries_coordinates = countries.drop(0, axis=0)


# STEP 2. CREATION DATAFRAMES

#TECHNOLOGIES 
# DF DUMMIES-Technologies by App, getting the dummies
dummie_tech = foodtech['all_tech'].str.get_dummies(sep=',')
# DF CHART Technologies vs Total
tech_total = dummie_tech[['AI & Machine learning', 'Big data',
       'Blockchain', 'Chatbot', 'Data Analytics', 'Data Visualization',
       'GIS/RemoteSensing', 'IVR', 'IoT', 'Machinery', 'Management Software',
       'Mobile - Advisory', 'Platform data-sharing', 'Precision Farming ',
       'QR Codes', 'SMS', 'Sensors', 'Smart appliance',
       'Smart equipment & Hardware', 'Social Media', 'UAV / Drones', 'USSD',
       'Video', 'Weareables', 'Website ']].sum(axis=0)
tech_total.to_frame()
tech_total1= tech_total.reset_index()
# This DF is the list for charts
tech_total1.rename(columns = {0: "Total",'index': "Tech" }, inplace=True)
tech_total3 = tech_total1.sort_values(by= "Total", ascending=True)


# This DF is the list for selectbox
tech_total2 = tech_total1.sort_values(by= "Tech", ascending=True)


# LEVELS
#DF DUMMIES- Level by App, getting dummies
dummie_level = foodtech['all_levels'].str.get_dummies(sep=',')

#DF CHART Level deployment vs total
#Creating the dataframe only for level and number of technologies inside 
level_total = dummie_level[['Organizations', 'Business', 'Community', 'Family', 'Government',
       'Individual']].sum(axis=0)
level_total.to_frame()
level_total1= level_total.reset_index()
level_total1.rename(columns = {0: "Total",'index': "Level" }, inplace=True)
level = level_total1.sort_values(by= "Total", ascending=True)


# DONORS
#DF Donors vs Total
dummie_donor = foodtech['all_donors'].str.get_dummies(sep=',')
donors_total = dummie_donor[['1to4 Foundation', 'AIR cargo', 'AK Impact Investors',
       'Accion Venture Lab', 'Acumen', 'Adobe', 'AgReliant Genetics',
       'Anonymous x 3', 'Australian Goverment', 'BRAC Humanitarian Program',
       'Bangladesh Centre for Advanced Studies', 'Barn Investments',
       'Bharti Airtel', 'Bill and Melinda Gates Foundation', 'Breed Reply',
       'CNH Industrial', 'Carasso ', 'Catalyst Fund', 'Cibus Fund',
       'Climate Corporation', 'CoresStudio ', 'Crowfunding', 'Crowfunding ',
       'DRK Foundations', 'Digifarm', 'Dutch Ministry of Foreign Affairs',
       'EIT Food ', 'Elixir Capital Managment',
       'Engineer Without Borders Canada', 'FAO', 'FMO',
       'Federal Government of Nigeria ', 'Geodata for Agriculture and Water',
       'Global Index Insurance Facility', 'Google', 'Google ',
       'Goverment of India', 'Grameen Credit Agricole Microcredit Foundations',
       'Grammen Foundation', 'Gray Matters Capital', 'GrowMark', 'IDH FArmit',
       'IIFCCO', 'Ile de France', 'Innovate UK',
       'International Development Research Centre  of Canada ',
       'International Food Policy Research Institute (IFPRI) ',
       'International Fund for Agricultural Development (IFAD)', 'KCB Bank ',
       'MACIF Fondation', 'Mastercard Foundation', 'Mercy Corps Ventures',
       'Mercy Crops', 'Montpelier Foundation', 'OLAM Kellog', 'ORACLE',
       'Omidyar Network', 'Opus Insights ', 'Propeller Fish ',
       'Qualcomm’s Wireless Reach', 'Safaricom', 'Self Help Afica',
       'Square Peg Capital', 'Sunu Capital', 'Syngenta Foundation',
       'Systema_VC', 'TL.com Capital Partners', 'Technoserve', 'TerraSphere',
       'The Global Competitiveness Facility',
       'The InsuResilience Investment Fund', 'The Lakes Charitable',
       'The Lundin Foundation',
       'The United Kingdom’s Department for International Development ',
       'USAID', 'United Nations', 'VideoMaker', 'Voltaic Sytems',
       'Wageningen University', 'Wilbur-Ellis Company',
       "Women's World banking", 'World Bank', 'World Summit Award',
       'mPower Social Enterprises']].sum(axis=0)
donors_total.to_frame()
donors_total1= donors_total.reset_index()
donors_total1.rename(columns = {0: "Total",'index': "all_donors" }, inplace=True)
donors = donors_total1.sort_values(by= "Total", ascending=True).reset_index(drop=True)
# DF List of donors with the class
total_donors = donors.merge(donorsclass, on = "all_donors", how = "inner" )
total_donors1 = total_donors.drop(['number'],axis = 1)
# Total of donor class vs Total
df_donors = total_donors1.groupby("class")['Total'].sum()
#df chart  Y=class donors  X= Total
df_donors1 = df_donors.to_frame().sort_values(by= "Total", ascending=True).reset_index()


# PRO-POOR
pro_poor = foodtech.groupby("Pro_poor focus?").sum().reset_index()




# STEP 3. CREATION OF MAIN DATAFRAME Apps vs Information-It has all the variables
df_total = pd.concat([foodtech, dummie_tech,dummie_donor, dummie_level ],axis=1)


## STEP 4. CREATION OF DF COUNTRIES, TECHNOLOGIES AND COORDINATES

# DF all Apps, countries vs total all variables + lat, long
total_map = df_total.merge(countries_coordinates, on = "Country", how = "inner" )


# 2 CONTAINER. MAPPING TECHNOLOGIES BY KEY PRINCIPLE AND TECHNOLOGY- All countries and all technologie
all_countries = total_map.groupby(['Country', 'App_name', 'Key Action', 'Latitude', 'Longitude']).agg({
                                                  'AI & Machine learning': 'sum',
                                                  'Big data': 'sum',
                                                  'Blockchain': 'sum',
                                                  'Chatbot':'sum',
                                                   'Data Analytics': 'sum', 
                                                  'Data Visualization': 'sum',
                                                  'GIS/RemoteSensing': 'sum',
                                                  'IVR': 'sum',
                                                  'IoT': 'sum',
                                                   'Machinery': 'sum',
                                                  'Management Software': 'sum', 
                                                  'Mobile - Advisory': 'sum',
                                                   'Platform data-sharing': 'sum', 
                                                  'Precision Farming ': 'sum',
                                                  'QR Codes': 'sum',
                                                  'SMS': 'sum',
                                                    'Sensors': 'sum',
                                                  'Smart appliance': 'sum', 
                                                  'Smart equipment & Hardware': 'sum',
                                                   'Social Media': 'sum', 
                                                  'UAV / Drones': 'sum', 
                                                  'USSD': 'sum',
                                                  'Video': 'sum', 
                                                  'Weareables': 'sum',
                                                    'Website ': 'sum' }).reset_index()

all_countries["Latitude"] = all_countries["Latitude"].astype(float)
all_countries["Longitude"] = all_countries["Longitude"].astype(float)

#DF Tech by country
all_countries_tech =  all_countries.groupby(['Country', 'Latitude', 'Longitude']).agg({'App_name':'count', 'Key Action':'count',
                                                  'AI & Machine learning': 'sum',
                                                  'Big data': 'sum',
                                                  'Blockchain': 'sum',
                                                  'Chatbot':'sum',
                                                   'Data Analytics': 'sum', 
                                                  'Data Visualization': 'sum',
                                                  'GIS/RemoteSensing': 'sum',
                                                  'IVR': 'sum',
                                                  'IoT': 'sum',
                                                   'Machinery': 'sum',
                                                  'Management Software': 'sum', 
                                                  'Mobile - Advisory': 'sum',
                                                   'Platform data-sharing': 'sum', 
                                                  'Precision Farming ': 'sum',
                                                  'QR Codes': 'sum',
                                                  'SMS': 'sum',
                                                    'Sensors': 'sum',
                                                  'Smart appliance': 'sum', 
                                                  'Smart equipment & Hardware': 'sum',
                                                   'Social Media': 'sum', 
                                                  'UAV / Drones': 'sum', 
                                                  'USSD': 'sum',
                                                  'Video': 'sum', 
                                                  'Weareables': 'sum',
                                                    'Website ': 'sum' }).reset_index()




# 🌎 MAP ORTHOGRAPHIC. World Chart 1

fig = go.Figure(data=go.Scattergeo(
        locationmode = 'country names',
        lon = all_countries_tech['Longitude'],
        lat = all_countries_tech['Latitude'],
        mode = 'markers',
        text = all_countries_tech['Country'], 
        
        #textposition="bottom center",
        #textfont=dict( family="sans serif", size=10, color="white"),
        #marker_color = tech_countries_map['innovation'], SCALE FOR VALUES
        marker = dict(
            #size = 16,
            size = all_countries_tech['App_name']*4, #SIZE OF THE CIRCLE 
            opacity = 0.9,
            reversescale = True,
            autocolorscale = False,
            symbol = "circle", #"circle-open",
            color = "#e51858", #ee4dee'
            line = dict(
                width=1,
                color= "#e51858"), #ee4dee'
            sizemode = 'diameter')
           )
        )

fig.update_traces(hoverinfo= ['text'], selector=dict(type='scattergeo'))
#Fig.update_geos(fitbounds="locations")
#Fig.update_traces(textposition="top left", selector=dict(type='scattergl'))
#fig.update_traces(hovertext= "Country: {Country}", selector=dict(type='scattergeo'))

fig.update_layout(
        title = ' ',
        geo = dict(
            scope='world',
            projection_type=  'orthographic',
            showland = True,
            oceancolor = "#2a2b5a",
            framewidth = 0.3,
            #landcolor = "rgb(144,165,210)",
            landcolor ="#00cc99",
            subunitcolor = "rgb(244,249,249)",
            countrycolor = "rgb(244,249,249)",
            countrywidth = 0.5,
            subunitwidth = 0.5,
            visible = True,
            showcountries = True,
            showocean = True,
            
        ),height=400, margin={"r":1,"t":1,"l":1,"b":1},
    )


# TITLE AND HEADER

# framework in columns
col1, col2, col3 = st.beta_columns([3, 0.5, 5])

with col1:
    st.title("Digital Agri-Food Solutions")
    st.markdown ('<p style= "font-family:Verdana; color:Black; font-size: 20px;">Interactive Dashboards </p>', unsafe_allow_html=True)
    st.write(':chart_with_upwards_trend: A total of 67 data-driven innovations were selected, which were narrowed down to those with relevant actions in the transformation of the food systems. Below is the distribution based on countries')
             
with col2:
    st.write(" ")
    
with col3:
    st.plotly_chart(fig) #use_container_width=True


st.markdown ('---')
# KEY PRINCIPLES 
st.subheader('Key principles for sustainability in food and agriculture')
st.write('Principle 1.Improving efficiency in the use of resources is crucial  to sustainable agriculture')
st.write('Principle 2. Sustainability requires direct action to conserve, protect  and enhance natural resources')
st.write('Principle 3.Agriculture that fails to protect and improve rural  livelihoods, equity and social well-being is unsustainable')
st.write('Principle 4. Enhanced resilience of people, communities and ecosystems  is key to sustainable agriculture')

st.markdown ('---')

# CONTAINER 2
st.title("Geographical Profile of  the Digital Technologies analysed")
st.write('In this section you can located the technological solutions that works under the fundamental Principles of the trasnformation of Food Systems.')
#st.text (' Select a TECHNOLOGY, the solutions using this technology will show on the map.')
#st.write ('If you want to know more about specific country or specific technology keep going, there are more interactive dashboards!')
#The data considered for this analysis is collected from different sources (papers, oficial reports and websites) during 2021')

df_total = all_countries.groupby(['Country', 'Latitude', 'Longitude', 'Key Action'])['App_name'].count().reset_index()

map_all = px.scatter_mapbox(
                            df_total, 
                            lat='Latitude', 
                            lon='Longitude', 
                            hover_name='Country', 
                            hover_data=["App_name"],
                            color_discrete_sequence=["fuchsia"], 
                            zoom=1, 
                            width = 800, height=500,
                            size="App_name",              
                            )

map_all.update_layout(mapbox_style="open-street-map")

map_all.update_layout(title_text = ' ', 
                       title_font_size = 20,
                       #title_font=dict( size=20, family='Verdana', color='Black'),
                      showlegend = True,  legend_title=dict(text='<b>Key Principles</b>- Click to toggle the key principles'), 
                       legend = {'xanchor':'auto', 'font':{'size':10}},
                      margin={"r":0,"t":60,"l":0,"b":1})




# Barchart Y= Coutries X= Total
df_total_sorted = df_total.sort_values(by= "App_name", ascending=True)
bar_all = px.bar(df_total_sorted, x="App_name", y="Country", width= 450, height=500, )
bar_all .update_layout(plot_bgcolor= "white")
bar_all .update_layout(title = "  ", title_font_size = 20)
bar_all .update_traces(marker_color='#00aae6', opacity = 0.8)
bar_all .update_yaxes(tickmode="array", title_text= " ")
bar_all .update_xaxes(title_text = 'Number of Digital Technologies by Country',
                range = (0,15), 
                title_font=dict( size=15, family='Verdana', color='Black'), 
                tickfont=dict( size=15, family='Verdana', color='Black'),
                tickmode="array",
                visible= True,
                color= 'black',
                showgrid = True,
                gridcolor = '#abd3df')



# CONTAINER MAIN


col1, col2, col3 = st.beta_columns([3,0.5,2])
with col1:
    st.plotly_chart(map_all, unsafe_allow_html=True)
    
with col2:
    st.write(" ")
with col3:
    st.plotly_chart(bar_all, unsafe_allow_html=True)

st.markdown ('---')
# SELECTORS 

#  SELECTING TECHNOLOGIES

st.title("Techologies by key principle")
st.write('In this section you select the technological solutions and see what are the key principles.')

tech = st.selectbox("SELECT A TECHNOLOGY", tech_total2['Tech'].unique(), key ='map')

col = ['Country', 'Latitude', 'Longitude', tech, 'Key Action']
all_countries_col =  all_countries[col].reset_index(drop = True)
all_countries_col.rename(columns={ all_countries_col.columns[3]: "tech" }, inplace = True)

# MAP_WORLDWIDE SELECTING TECHNOLOGIES 
map_tech = px.scatter_mapbox(all_countries_col, 
                            lat='Latitude', 
                            lon='Longitude', 
                            color= 'Key Action',
                            hover_name='Country', 
                            hover_data=["Country", "tech"],
                            zoom=1, 
                            opacity = 0.6,
                            width = 1000, height=500,
                            size="tech",              
                            )

map_tech.update_layout(mapbox_style="open-street-map")
map_tech.update_layout(title_text = '', 
                       title_font_size = 20,
                       #title_font=dict( size=20, family='Verdana', color='Black'),
                      showlegend = True,  legend_title=dict(text='<b>Key Principles</b>- Click to toggle the key principles'), 
                       legend = {'xanchor':'auto', 'font':{'size':10}},
                      margin={"r":0,"t":60,"l":0,"b":1})


       
st.plotly_chart(map_tech, unsafe_allow_html=True)
# Data Source
st.write("Source: Hurtado, M. (2021). Data-driven solutions towards sustainable agri-food systems. Dataset Available here: [link](https://github.com/merlynjocol/DataRuralHub_Data_driven_Solutions_Transforming_Food_systems/blob/bed77e92d26426d5e64cfee13ecd9305ba5db68a/data/food_tech.csv)")


st.markdown ('---')        


# THIRD CONTAINER  TYPES OF TECHNOLOGY WORDCLOUD
st.markdown ('---')

st.title('What Digital Technologies are driven the transformation of Food Systems?')
st.write('This section you can find the technologies most used in each country ')

# SELECTING VARIABLES
col1, col2, col3 = st.beta_columns([1,1,1])
with col1:
    country = st.selectbox("Select a Country", all_countries['Country'].unique(), key= 'tech')
with col2:
    st.write(" ")
    #principle= st.selectbox("Select a Principle of Transformation", all_countries['Key Action'].unique(), key= 'tech')
with col3:
    st.write(" ")



#CHARTS WORDCLOUD
data1 = tech_total1.set_index('Tech').to_dict()['Total']

wc1 = WordCloud(width = 300,   
                  background_color ='white',
                 max_words=200, colormap="cool_r").generate_from_frequencies(data1)
    
    
# plot the WordCloud image                        
wc = plt.figure(figsize = (20,10), facecolor = None) 
wc = plt.imshow(wc1, interpolation = 'nearest') 
wc = plt.axis("off") 
wc = plt.tight_layout(pad = 0) 

#eliminate the error deprecation from matplotlib
st.set_option('deprecation.showPyplotGlobalUse', False)


#CHART BUBBLE

buble1 = px.scatter(tech_total3, x = 'Total', y = 'Tech', size = 'Total', height=400)
buble1.update_layout(plot_bgcolor= "white", title = "Which technologies are using in the Food Systems?", title_font_size = 20)
buble1.update_traces(marker_color='#00aae6', opacity = 0.8)
buble1.update_yaxes(tickmode="array", title_text= " ")
buble1.update_xaxes(title_text = 'Number of Digital Technologies',
                range = (0,15), 
                title_font=dict( size=15, family='Verdana', color='Black'), 
                tickfont=dict( size=15, family='Verdana', color='Black'),
                tickmode="array",
                visible= True,
                color= 'black',
                showgrid = True,
                gridcolor = '#abd3df')
#fig3.update_layout(autosize= True)



fig3 = go.Figure()
#sizeref = 2.*max(tech_total1['Country'])*2

fig3.add_trace(go.Scatter(
                          x = tech_total3['Total'], y = tech_total3['Tech'],
                          mode = 'markers',
                          name = 'Number of solutions',
                          marker = dict(colorscale = 'magma',
                            cmax=40,
                            cmin=0,
                          opacity = 0.8, size = tech_total1['Total']*25,
                          symbol =  "circle",
                          sizemode = 'area', 
                          showscale = False
                          )))
                        
fig3.update_layout(plot_bgcolor= "white", title = "Which technologies are using in the Food Systems?", title_font_size = 20)
fig3.update_traces(marker_color='#00aae6', opacity = 0.8)
fig3.update_yaxes(tickmode="array", title_text= " ")
fig3.update_layout(legend=dict(
                               yanchor="top", y=0.99,
                               xanchor="left",x=0.01),
                               legend_font_size= 20,
                               showlegend = False)

fig3.update_xaxes(title_text = 'Number of Digital Solutions',range = (0,30), title_font=dict(size=15, family='Verdana', 
                                  color='Black'), tickfont=dict(family='Calibri', color='black', 
                                 size=15))

fig3.update_yaxes(title_text = " ", title_font=dict(size=30, family='Verdana', 
                                  color='orange'),tickfont=dict(family='Calibri', color='black', 
                                size=15))
fig3.update_xaxes(title_text = 'Number of Digital Technologies',
                range = (0,15), 
                title_font=dict( size=15, family='Verdana', color='Black'), 
                tickfont=dict( size=15, family='Verdana', color='Black'),
                tickmode="array",
                visible= True,
                color= 'black',
                showgrid = True,
                gridcolor = '#abd3df')

col1, col2, col3 = st.beta_columns([2,0.5,2])
with col1:
    st.pyplot(wc, unsafe_allow_html=True)
    
with col2:
    st.write(" ")
with col3:
    st.plotly_chart(fig3, unsafe_allow_html=True)

st.markdown ('---')



#CHART LEVEL

figlevel = px.bar(level, x="Total", y="Level", width= 450)
figlevel.update_layout(plot_bgcolor= "white")
figlevel.update_layout(title = "  ", title_font_size = 20)
figlevel.update_traces(marker_color='#00aae6', opacity = 0.8)
figlevel.update_yaxes(tickmode="array", title_text= " ")
figlevel.update_xaxes(title_text = 'Number of Digital Technologies',
                range = (0,65), 
                title_font=dict( size=15, family='Verdana', color='Black'), 
                tickfont=dict( size=15, family='Verdana', color='Black'),
                tickmode="array",
                visible= True,
                color= 'black',
                showgrid = True,
                gridcolor = '#abd3df')


#fig3.update_layout(autosize= True)

pro_poor = foodtech.groupby("Pro_poor focus?").sum().reset_index()


fig_pie = px.pie(foodtech, values='No', names='Pro_poor focus?', color='Pro_poor focus?',
             color_discrete_map={'Yes':'royalblue',
                                 'No ':"#2a2b5a",
                                 'Not sure': '#e51858' #0bca9b'
                                }, opacity =0.8, width=500,
    height=500 )


#fig.update_traces(textposition='inside', textinfo='percent+text')
fig_pie.update_traces(pull=[1,1,0.05])



#CHART ONNERSHIP

col1, col2, col3 = st.beta_columns([2,0.5,2])

with col1:
    country = st.selectbox("Select a Country", all_countries['Country'].unique(), key= 'level')
    st.title('level/scale of deployment')
    st.plotly_chart(figlevel,unsafe_allow_html=True )
    
with col2:
    st.write(" ")
with col3:
    country = st.selectbox("Select a Country", all_countries['Country'].unique(), key= 'pro-poor')
    st.title('Pro-poor focus solutions')
    st.plotly_chart(fig_pie, unsafe_allow_html=True)

st.markdown ('---')

#df_donors = total_donors1.groupby("class")['Total'].sum()
#df_donors1 = df_donors.to_frame().sort_values(by= "Total", ascending=True).reset_index()

figDonors = px.bar(df_donors1, x="Total", y="class",width = 700, height = 400)
figDonors.update_layout(plot_bgcolor= "white")
figDonors.update_layout(title = "  ", title_font_size = 20)
figDonors.update_traces(marker_color='#00aae6', opacity = 0.8)
figDonors.update_yaxes(tickmode="array", title_text= " ")
figDonors.update_xaxes(title_text = 'Number of Digital Technologies',
                range = (0,40), 
                title_font=dict( size=15, family='Verdana', color='Black'), 
                tickfont=dict( size=15, family='Verdana', color='Black'),
                tickmode="array",
                visible= True,
                color= 'black',
                showgrid = True,
                gridcolor = '#abd3df')


#principles
tech_principles = total_map.groupby('Key Action').agg({'App_name': 'count', 
                                                  'AI & Machine learning': 'sum',
                                                  'Big data': 'sum',
                                                  'Blockchain': 'sum',
                                                  'Chatbot':'sum',
                                                   'Data Analytics': 'sum', 
                                                  'Data Visualization': 'sum',
                                                  'GIS/RemoteSensing': 'sum',
                                                  'IVR': 'sum',
                                                  'IoT': 'sum',
                                                   'Machinery': 'sum',
                                                  'Management Software': 'sum', 
                                                  'Mobile - Advisory': 'sum',
                                                   'Platform data-sharing': 'sum', 
                                                  'Precision Farming ': 'sum',
                                                  'QR Codes': 'sum',
                                                  'SMS': 'sum',
                                                    'Sensors': 'sum',
                                                  'Smart appliance': 'sum', 
                                                  'Smart equipment & Hardware': 'sum',
                                                   'Social Media': 'sum', 
                                                  'UAV / Drones': 'sum', 
                                                  'USSD': 'sum',
                                                  'Video': 'sum', 
                                                  'Weareables': 'sum',
                                                    'Website ': 'sum' }).reset_index()



tech_owner = total_map.groupby('Ownership').agg({'App_name': 'count', 
                                                  'AI & Machine learning': 'sum',
                                                  'Big data': 'sum',
                                                  'Blockchain': 'sum',
                                                  'Chatbot':'sum',
                                                   'Data Analytics': 'sum', 
                                                  'Data Visualization': 'sum',
                                                  'GIS/RemoteSensing': 'sum',
                                                  'IVR': 'sum',
                                                  'IoT': 'sum',
                                                   'Machinery': 'sum',
                                                  'Management Software': 'sum', 
                                                  'Mobile - Advisory': 'sum',
                                                   'Platform data-sharing': 'sum', 
                                                  'Precision Farming ': 'sum',
                                                  'QR Codes': 'sum',
                                                  'SMS': 'sum',
                                                    'Sensors': 'sum',
                                                  'Smart appliance': 'sum', 
                                                  'Smart equipment & Hardware': 'sum',
                                                   'Social Media': 'sum', 
                                                  'UAV / Drones': 'sum', 
                                                  'USSD': 'sum',
                                                  'Video': 'sum', 
                                                  'Weareables': 'sum',
                                                    'Website ': 'sum' }).reset_index()

owner = tech_owner.sort_values(by= "App_name", ascending=True)

figO = go.Figure()

figO.add_trace(go.Bar(
    x=owner['App_name'],
    y = owner['Ownership'], 
    orientation='h', 
    opacity = 0.8
))

figO.update_layout(
    autosize=False,
    width=500,
    height=500,
    yaxis=dict(
        title_text=" ",
        #ticktext=["Very long label", "long label", "3", "label"],
        #tickvals=[1, 2, 3, 4,5,6],
        tickmode="array",
        titlefont=dict(size=30),
    )
)

                 

figO.update_layout(title = "Who is the owner of the digital solutions?",
                   title_font_size = 20, template = 'plotly_white',
                   width = 600, height = 400)

figO.update_xaxes(
        title_text = 'Number of digital technolgies',
        range = (0,10), 
        title_font=dict(
                        size=15, 
                        family='Verdana', 
                        color='Black'), 
        tickfont=dict(
                        family='Calibri',
                        color='black', 
                        size=15),
        tickmode="array",
        showgrid = True
        )

figO.update_yaxes(
                    #title_text = " Deployment Level", 
                    title_font=dict(
                                    size=30, 
                                    family='Verdana', 
                                    color='orange'),
                    tickfont=dict(
                                family='Calibri', 
                                color='black', 
                                size=15),
                    )

figO.update_layout(legend=dict(
                               yanchor="top", y=0.99,
                               xanchor="left",x=0.01),
                               legend_font_size= 20,
                               showlegend = False)

#PRINCIPLES
principle = tech_principles.sort_values(by= "App_name", ascending=True)
figP = go.Figure()

figP.add_trace(go.Bar(
    x=principle['App_name'],
    y = principle['Key Action'], 
    orientation='h', 
    opacity = 0.8
))

figP.update_layout(
    autosize=False,
    width=500,
    height=500,
    yaxis=dict(
        title_text=" ",
        #ticktext=["Very long label", "long label", "3", "label"],
        #tickvals=[1, 2, 3, 4,5,6],
        tickmode="array",
        titlefont=dict(size=30),
    )
)

                 

figP.update_layout(title = "Which of the following actions the digital technologies support?",
                   title_font_size = 20, template = 'plotly_white',
                   width = 1100, height = 400)

figP.update_xaxes(
        title_text = 'Number of digital technolgies',
        range = (0,50), 
        title_font=dict(
                        size=15, 
                        family='Verdana', 
                        color='Black'), 
        tickfont=dict(
                        family='Calibri',
                        color='black', 
                        size=15),
        tickmode="array",
        showgrid = True
        )
figP.update_yaxes(
                    #title_text = " Deployment Level", 
                    title_font=dict(
                                    size=30, 
                                    family='Verdana', 
                                    color='orange'),
                    tickfont=dict(
                                family='Calibri', 
                                color='black', 
                                size=15),
                    )

figP.update_layout(legend=dict(
                               yanchor="top", y=0.99,
                               xanchor="left",x=0.01),
                               legend_font_size= 20,
                               showlegend = False)






st.markdown ('---')
country = st.selectbox("Select a Country", all_countries['Country'].unique(), key= 'owner')
st.title('Owner of the digital solutions?')
st.plotly_chart(figO,unsafe_allow_html=True )
    
st.markdown ('---')

country = st.selectbox("Select a Country", all_countries['Country'].unique(), key= 'actions')
st.title('Actions supported by digital technologies')
st.plotly_chart(figP, unsafe_allow_html=True)


# https://www.linkedin.com/pulse/streamlit-enables-sharing-data-impactful-way-kennedy-selvadurai/



st.markdown ('---')


new_donor = total_map[['App_name', '1to4 Foundation', 'AIR cargo', 'AK Impact Investors',
       'Accion Venture Lab', 'Acumen', 'Adobe', 'AgReliant Genetics',
       'Anonymous x 3', 'Australian Goverment', 'BRAC Humanitarian Program',
       'Bangladesh Centre for Advanced Studies', 'Barn Investments',
       'Bharti Airtel', 'Bill and Melinda Gates Foundation', 'Breed Reply',
       'CNH Industrial', 'Carasso ', 'Catalyst Fund', 'Cibus Fund',
       'Climate Corporation', 'CoresStudio ', 'Crowfunding', 'Crowfunding ',
       'DRK Foundations', 'Digifarm', 'Dutch Ministry of Foreign Affairs',
       'EIT Food ', 'Elixir Capital Managment',
       'Engineer Without Borders Canada', 'FAO', 'FMO',
       'Federal Government of Nigeria ', 'Geodata for Agriculture and Water',
       'Global Index Insurance Facility', 'Google', 'Google ',
       'Goverment of India', 'Grameen Credit Agricole Microcredit Foundations',
       'Grammen Foundation', 'Gray Matters Capital', 'GrowMark', 'IDH FArmit',
       'IIFCCO', 'Ile de France', 'Innovate UK',
       'International Development Research Centre  of Canada ',
       'International Food Policy Research Institute (IFPRI) ',
       'International Fund for Agricultural Development (IFAD)', 'KCB Bank ',
       'MACIF Fondation', 'Mastercard Foundation', 'Mercy Corps Ventures',
       'Mercy Crops', 'Montpelier Foundation', 'OLAM Kellog', 'ORACLE',
       'Omidyar Network', 'Opus Insights ', 'Propeller Fish ',
       'Qualcomm’s Wireless Reach', 'Safaricom', 'Self Help Afica',
       'Square Peg Capital', 'Sunu Capital', 'Syngenta Foundation',
       'Systema_VC', 'TL.com Capital Partners', 'Technoserve', 'TerraSphere',
       'The Global Competitiveness Facility',
       'The InsuResilience Investment Fund', 'The Lakes Charitable',
       'The Lundin Foundation',
       'The United Kingdom’s Department for International Development ',
       'USAID', 'United Nations', 'VideoMaker', 'Voltaic Sytems',
       'Wageningen University', 'Wilbur-Ellis Company',
       "Women's World banking", 'World Bank', 'World Summit Award',
       'mPower Social Enterprises']].copy()

new_donor

#df_donor = new_donor.reset_index('App_name')
donor_melt= new_donor.melt(id_vars='App_name')
donor_meltsorted = donor_melt.sort_values(by= "App_name", ascending=True)

chord1 = hv.Chord(donor_meltsorted )
st.plotly_chart(chord1,unsafe_allow_html=True )










'''

SELECTING PRINICPLES

# CONTAINER 2

#col1, col2 = st.beta_columns([3, 1])
#with col1:
#    principle= st.selectbox("Select a Fundamental Principle of Food System Transformation", all_countries['Key Action'].unique(), key ='map')
#with col2: 
principle= st.selectbox("Select a Fundamental Principle of Food System Transformation", all_countries['Key Action'].unique(), key ='map2')
    
#  SELECTING PRINCIPLES 
df_principle = all_countries[all_countries['Key Action'] == principle ].groupby(['Country', 'Latitude', 'Longitude'])['App_name'].count().reset_index()


# MAP_WORLDWIDE SELECTING PRINCIPLES-Mapping technologies
fig2 = px.scatter_mapbox(   df_principle, 
                            lat='Latitude', 
                            lon='Longitude', 
                            hover_name='Country', 
                            hover_data=["Country", "App_name"],
                            color_discrete_sequence=["fuchsia"], 
                            zoom=1, 
                            width = 1000, height=300,
                            size="App_name")
fig2.update_layout(mapbox_style="open-street-map", 
                   margin={"r":1,"t":1,"l":1,"b":1})


# BARCHART. SELECTING PRINCIPLES 
# Barchart Y= Coutries X= Total
df_principle_sorted = df_principle.sort_values(by= "App_name", ascending=True)
figtech = px.bar(df_principle_sorted, x="App_name", y="Country", width= 450)
             # height=500, )
figtech.update_layout(plot_bgcolor= "white")
figtech.update_layout(title = "  ", title_font_size = 20)
figtech.update_traces(marker_color='#00aae6', opacity = 0.8)
figtech.update_yaxes(tickmode="array", title_text= " ")
figtech.update_xaxes(title_text = 'Number of Digital Technologies',
                range = (0,15), 
                title_font=dict( size=15, family='Verdana', color='Black'), 
                tickfont=dict( size=15, family='Verdana', color='Black'),
                tickmode="array",
                visible= True,
                color= 'black',
                showgrid = True,
                gridcolor = '#abd3df')



# BARCHART. SELECTING PRINCIPLES 
# Barchart Y= Coutries X= Total
alltech_sorted = all_countries_col.sort_values(by= "tech", ascending=True)
alltech_sorted.drop(alltech_sorted.index[alltech_sorted['tech'] == 0], inplace = True)

# Barchart Y= Coutries X= Total
bar_tech = px.bar(alltech_sorted , x="tech", y="Country", width= 450)
             # height=500, )
bar_tech.update_layout(plot_bgcolor= "white")
bar_tech.update_layout(title = "  ", title_font_size = 20)
bar_tech.update_traces(marker_color='#ffdb00', opacity = 0.8)
bar_tech.update_yaxes(tickmode="array", title_text= " ")
bar_tech.update_xaxes(title_text = 'Number of Digital Technologies',
                range = (0,15), 
                title_font=dict( size=15, family='Verdana', color='Black'), 
                tickfont=dict( size=15, family='Verdana', color='Black'),
                tickmode="array",
                visible= True,
                color= 'black',
                showgrid = True,
                gridcolor = '#abd3df')

# CONTAINER 2

col1, col2, col3 = st.beta_columns([3,0.5,2])
with col1:
    st.plotly_chart(fig2, unsafe_allow_html=True)
    
with col2:
    st.write(" ")
with col3:
    st.plotly_chart(figtech, unsafe_allow_html=True)


'''
