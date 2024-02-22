import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go


######################################################################################## Build our app  
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
template = "darkly"
load_figure_template(template)

############################################################################# Loading data and making Group index for performance                   
raw_df = pd.read_parquet("gtd_clean_dataset_pqt.parquet")
raw_df.set_index('Group', inplace=True)

#################################################################################### build overview

def victims_killed_indicator(df):
    total_victims_killed = df['NVictimsKilled'].sum(skipna=True)
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number",
        value=total_victims_killed,
        title={"text": "Victims Killed"}
    ))

    return fig

def years_active_indicator(df):
    years_active = df['Year'].max() - df['Year'].min()
    if years_active == 0:
        years_active = 1
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=years_active,
        title={"text": "Years Active"}
    ))
    return fig

def number_of_attacks_indicator(df):
    num_attacks = len(df)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=num_attacks,
        title={"text": "Attacks"}
    ))
    return fig

def victims_wounded_indicator(df):
    total_wounded = df['NVictimsWounded'].sum(skipna=True)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=total_wounded,
        title={"text": "Victims Wounded"}
    ))
    return fig

def countries_affected_indicator(df):
    countries_affected = df['Country'].nunique()
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=countries_affected,
        title={"text": "Countries Affected"}
    ))
    return fig

def BuildGetOverviewLayout(filtered_df,template):
    victims_killed_ind = victims_killed_indicator(filtered_df)
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=number_of_attacks_indicator(filtered_df))),
            dbc.Col(dcc.Graph(figure=years_active_indicator(filtered_df))),
            dbc.Col(dcc.Graph(figure=countries_affected_indicator(filtered_df))),
            dbc.Col(dcc.Graph(figure=victims_killed_indicator(filtered_df))),
            dbc.Col(dcc.Graph(figure=victims_wounded_indicator(filtered_df))),
        ])
    ]

##################################################################################### Build the Navbar
navbar = dbc.NavbarSimple(
    children=[
        dcc.Dropdown(
            id='group-dropdown',
            options=[{'label': group, 'value': group} for group in raw_df.index.unique()],
            value=raw_df.index.unique()[0],  # Default to the first value
            style={'width': '400px'}
        ),
        dbc.NavItem(dbc.NavLink("Group Overview", href="/overview", active=True, id='overview-link')),
        dbc.NavItem(dbc.NavLink("Attack Methodology", href="/attackmethod", active=False, id='attackmethod-link')),
        dbc.NavItem(dbc.NavLink("Geographical", href="/geo", active=False, id='geo-link')),
    ],
    brand="Global Terrorism Perpetrators",
    brand_href="/overview",
    color="dark",
    dark=True,
    style={'borderBottom': '1px solid white'}  # Add a border to the bottom of the navbar
)

######################################################################################## Page layout
app.layout = dbc.Container(
    [
        dcc.Location(id='url', refresh=False, pathname='/overview'),  # Set default page to "/page1"
        navbar,
        html.Div(id='page-content')
    ],
    fluid=False,
    className="dbc"
)

########################################### Callback to update page content based on URL and dropdown value
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'),
               Input('group-dropdown', 'value')])
def update_page_content(pathname, selected_group):
    if selected_group == 'ALL':
        selected_group = None
    filtered_df = raw_df[raw_df.index == selected_group]

    if pathname == '/overview':
        # Page 1 content
        #return overview.update_get_figure_layout(filtered_df)
        #ov_Fig1Test(filtered_df,template)
        return BuildGetOverviewLayout(filtered_df,template)

    elif pathname == '/attackmethod':
        # Page 2 content
        fig3 = px.pie(filtered_df, names='Country', values='NVictimsKilled', title='Attack Methodology - Value1',template=template)
        fig4 = px.pie(filtered_df, names='Country', values='NVictimsWounded', title='Attack Methodology - Value2')
        return [dcc.Graph(figure=fig3), dcc.Graph(figure=fig4)]

    elif pathname == '/geo':
        # Page 3 content
        fig5 = px.scatter_geo(filtered_df, locations='Country', size='NVictimsKilled', title='Geographical - Value1')
        fig6 = px.scatter_geo(filtered_df, locations='Country', size='NVictimsWounded', title='Geographical - Value2')
        return [dcc.Graph(figure=fig5), dcc.Graph(figure=fig6)]

############################################ Callback to update active state of NavLinks and highlight them
@app.callback(
    [Output('overview-link', 'active'),
     Output('attackmethod-link', 'active'),
     Output('geo-link', 'active')],
    [Input('url', 'pathname')]
)
def update_active_links(pathname):
    return pathname == '/overview', pathname == '/attackmethod', pathname == '/geo'


if __name__ == '__main__':
    #port must match Dockerfile
    app.run_server(debug=True, host='0.0.0.0', port=8050)