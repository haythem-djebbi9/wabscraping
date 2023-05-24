from bs4 import BeautifulSoup
import pandas as pd
import requests
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

# Configuration de l'URL de scraping
url = 'https://www.jumia.com.tn/smartphones/'
# Récupération des données à partir de l'URL de scraping
response = requests.get(url)

if response.ok:
    soup = BeautifulSoup(response.text, 'lxml')
    
    elements = soup.find_all('article', {'class': 'prd _fb col c-prd'})
    data_list = []
    
    for el in elements:
        price = el.find('div', {'class': 'prc'}).text.strip()
        name = el.find('h3', {'class': 'name'}).text.strip()
        image = el.find('img')['data-src']

        data_list.append({'Nom': name, 'Prix': price, 'Lien': image})
        
        
else:
    print("Erreur lors de la récupération des données")

# Conversion des données en DataFrame pour faciliter le filtrage
df = pd.DataFrame(data_list)

# Obtention de la liste des marques uniques
marques = df['Nom'].apply(lambda x: x.split()[0]).unique()

# Initialisation de l'application Dash
app = dash.Dash(__name__)

# Création de la mise en page de l'application
app.layout = html.Div([
    html.H3("Liste des smartphones :"),
    html.Div([
        html.Label('Filtrer par marque :'),
        dcc.Dropdown(
            id='dropdown-marque',
            options=[{'label': marque, 'value': marque} for marque in marques],
            multi=True
        ),
        html.Br(),
        html.Label('Filtrer par prix (en DT) :'),
        dcc.Input(id='input-prix', type='number', value=''),
        html.Br(),
        html.Button('Filtrer', id='button-filtrer', n_clicks=0)
    ]),
    html.Table(
        id='table-smartphones',
        className='table',
        children=[
            html.Thead(
                html.Tr([
                    html.Th("Nom"),
                    html.Th("Prix"),
                    html.Th("Image")
                ])
            ),
            html.Tbody(id='table-body')
        ]
    )
])

@app.callback(
    Output('table-body', 'children'),
    Input('button-filtrer', 'n_clicks'),
    State('dropdown-marque', 'value'),
    State('input-prix', 'value')
)
def update_table(n_clicks, marques, prix):
    filtered_data = df.copy()
    
    if marques:
        filtered_data = filtered_data[filtered_data['Nom'].apply(lambda x: x.split()[0] in marques)]
    
    if prix:
        filtered_data = filtered_data[filtered_data['Prix'].str.extract('(\d+\.?\d*)', expand=False).astype(float) <= float(prix)]
    
    table_rows = []
    for index, row in filtered_data.iterrows():
        table_row = html.Tr([
            html.Td(row['Nom']),
            html.Td(row['Prix']),
            html.Td(html.Img(src=row['Lien'], height=100, width=100))
        ])
        table_rows.append(table_row)
    return table_rows

if __name__ == '__main__':
    app.run_server(debug=True)

