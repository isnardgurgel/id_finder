# Streamlit-Google Sheet
## Modules
import streamlit as st 
from pandas import DataFrame
import pandas as pd
import unicodedata
from sys import exit
from PIL import Image

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from gspread_pandas import Spread,Client
from google.oauth2 import service_account

# 
import networkx as nx
import matplotlib.pyplot as plt

from datetime import datetime

# Disable certificate verification (Not necessary always)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Create a Google Authentication connection object
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes = scope)
client = Client(scope=scope,creds=credentials)
spreadsheetname = "base_id_finder"
spread = Spread(spreadsheetname,client = client)

#setup do título da página
st.set_page_config(page_title="ID Finder", page_icon=None, layout='centered', initial_sidebar_state='collapsed', menu_items=None)

#call para abrir a imagem da loft na página
foto = Image.open('RGB_logoslaranja_pack_prioritario.png')
st.image(foto)

# Título da página centralizado e na cor cinza
st.markdown("<h1 style='text-align: center; color: DimGrey;'>ID Finder para consultores e parceiros</h1>", unsafe_allow_html=True)

# Check the connection
#st.write(spread.url)
#@st.cache(ttl=600)
sh = client.open(spreadsheetname)
worksheet_list = sh.worksheets()

# Functions 
# Get our worksheet names

def worksheet_names():
    sheet_names = []   
    for sheet in worksheet_list:
        sheet_names.append(sheet.title)  
    return sheet_names

# Get the sheet as dataframe
@st.cache(ttl=600)
def load_the_spreadsheet(spreadsheetname):
    worksheet = sh.worksheet(spreadsheetname)
    df = DataFrame(worksheet.get_all_records())
    return df


# Check whether the sheets exists
what_sheets = worksheet_names()
#st.sidebar.write(what_sheets)
ws_choice = st.radio('Você deseja consultar a ID de consultor ou parceiro?',what_sheets)
#df = load_the_spreadsheet(ws_choice)
df = DataFrame(sh.worksheet(ws_choice).get_all_records())
#sheets = ws_choice



def string_treat(string):
  import re
  pattern = re.compile(r'(?<!^)(?=[A-Z])')
  # remove ascents
  outputString = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode("utf-8")
  return pattern.sub('', outputString).lower()

def mobile_treat(string):
  new_string = string.strip()
  new_string = new_string.replace("(","")
  new_string = new_string.replace(")","")
  new_string = new_string.replace("-","")
  # remove ascents
  return new_string

id = ""  

with st.form('search form', clear_on_submit=True):

    #st.write(df.iloc[:,-1])
    # #st.write(df)
    lista = list(df.columns)
    lista_1 = list().clear()
    lista_1 = []
    #restrict = ['partner_id', 'ID']
    restrict = ['id']
    for i in lista:
        if i not in restrict:
            lista_1.append(i)
    #st.write(lista_1)

    st.write("Qual campo deseja usar na busca pela ID?")
    campo_consulta = st.radio('', lista_1)
    consulta = st.text_input('Insira os dados conforme as instruções de cada campo e aperte o botão Enviar', value='')
    submitted = st.form_submit_button("Enviar")
    if submitted:
        st.write('Estamos consultando: ', campo_consulta.split()[0],': ', consulta)
        df2 = df.copy()
        df2.iloc[:,0] = df2.iloc[:,0].apply(string_treat)
        if ws_choice == 'parceiro':
            df2.iloc[:,2] = df2.iloc[:,2].str.replace("(", "")
            df2.iloc[:,2] = df2.iloc[:,2].str.replace(")", '')
            df2.iloc[:,2] = df2.iloc[:,2].str.replace("-", '')
            df2.iloc[:,2] = df2.iloc[:,2].str.replace(" ", '')
            df2.iloc[:,2] = df2.iloc[:,2].str.strip()
        else:
            df2.iloc[:,2] = df2.iloc[:,2].astype(str)
            df2.iloc[:,2] = df2.iloc[:,2].str[-11:]
        
        
        df2.set_index(campo_consulta, inplace=True)
        if consulta not in set(df2.index):
            st.markdown("<h2 style='text-align: center; color: Red;'>Este dado não consta na base!</h1>", unsafe_allow_html=True)
            exit()
            

        #st.write(df2)
        id = df2.loc[consulta][-1]


if id != '':
    st.markdown(f"<h3 style='text-align: center; color: Green;'> O ID de {ws_choice} buscado é: {id} </h1>", unsafe_allow_html=True)       
        