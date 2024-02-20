import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash_bootstrap_templates import load_figure_template

###### Build our app  
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
template = "darkly"
load_figure_template(template)

###### Loading data and making Group index for performance                   
df = pd.read_parquet("gtd_clean_dataset_pqt.parquet")
df.set_index('Group', inplace=True)

'''
data = {
    'Group': ['A', 'B', 'A', 'B'],
    'NVictimsKilled': [10, 15, 8, 12],
    'NVictimsWounded': [5, 10, 4, 8],
    'Country': ['USA', 'Canada', 'Mexico', 'USA']
}
df = pd.DataFrame(data)
df.set_index('Group', inplace=True)
'''


######## Build the Navbar
navbar = dbc.NavbarSimple(
    children=[
        dcc.Dropdown(
            id='group-dropdown',
            options=[{'label': group, 'value': group} for group in df.index.unique()],
            value=df.index.unique()[0],  # Default to the first value
            style={'width': '400px'}
        ),
        dbc.NavItem(dbc.NavLink("Group Overview", href="/page1", active=True, id='page1-link')),
        dbc.NavItem(dbc.NavLink("Attack Methodology", href="/page2", active=False, id='page2-link')),
        dbc.NavItem(dbc.NavLink("Geographical", href="/page3", active=False, id='page3-link')),
    ],
    brand="Global Terrorism Perpetrators",
    brand_href="/page1",
    color="dark",
    dark=True,
    style={'borderBottom': '1px solid white'}  # Add a border to the bottom of the navbar
)

########## Page layout
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False, pathname='/page1'),  # Set default page to "/page1"
        navbar,
        html.Div(id='page-content')
    ],
    fluid=False,
    className="dbc"
)

################ Callback to update page content based on URL and dropdown value
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'),
               Input('group-dropdown', 'value')])
def update_page_content(pathname, selected_group):
    if selected_group == 'ALL':
        selected_group = None

    filtered_df = df[df.index == selected_group]

    if pathname == '/page1':
        # Page 1 content
        fig1 = px.bar(filtered_df, x='Country', y='NVictimsKilled', title='Group Overview - Value1',template=template)
        fig2 = px.bar(filtered_df, x='Country', y='NVictimsWounded', title='Group Overview - Value2',template=template)
        
        return [
            dbc.Row([
                dbc.Col(html.Div("Hello sailor. this is alex speaking")),
                dbc.Col(dcc.Graph(figure=fig1)),
                dbc.Col(dcc.Graph(figure=fig2)),
            ])
        ]
        #return [dcc.Graph(figure=fig1), dcc.Graph(figure=fig2)]

    elif pathname == '/page2':
        # Page 2 content
        fig3 = px.pie(filtered_df, names='Country', values='NVictimsKilled', title='Attack Methodology - Value1',template=template)
        fig4 = px.pie(filtered_df, names='Country', values='NVictimsWounded', title='Attack Methodology - Value2')
        return [dcc.Graph(figure=fig3), dcc.Graph(figure=fig4)]

    elif pathname == '/page3':
        # Page 3 content
        fig5 = px.scatter_geo(filtered_df, locations='Country', size='NVictimsKilled', title='Geographical - Value1')
        fig6 = px.scatter_geo(filtered_df, locations='Country', size='NVictimsWounded', title='Geographical - Value2')
        return [dcc.Graph(figure=fig5), dcc.Graph(figure=fig6)]

################ Callback to update active state of NavLinks and highlight them
@app.callback(
    [Output('page1-link', 'active'),
     Output('page2-link', 'active'),
     Output('page3-link', 'active')],
    [Input('url', 'pathname')]
)
def update_active_links(pathname):
    return pathname == '/page1', pathname == '/page2', pathname == '/page3'


if __name__ == '__main__':
    #port must match Dockerfile
    app.run_server(debug=True, host='0.0.0.0', port=8050)