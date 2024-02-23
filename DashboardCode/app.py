import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go
from plotly.subplots import make_subplots

######################################################################################## Build our app  
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
template = "darkly"
load_figure_template(template)

############################################################################# Loading data and making Group index for performance                   
raw_df = pd.read_parquet("gtd_clean_dataset_pqt.parquet")
raw_df.set_index('Group', inplace=True)

#################################################################################### build overview
ov_ind_margin = 5
def ov_years_active_indicator(df):
    min_year = df['Year'].min()
    max_year = df['Year'].max()
    years_active = max_year - min_year
    if years_active == 0:
        years_active = 1
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=years_active,
        title={"text": "Years Active", 'font': {'size': 26}},
        number={'font': {'size': 24}}
    ))
    fig.update_layout(
    margin=dict(l=ov_ind_margin, r=ov_ind_margin, t=ov_ind_margin, b=ov_ind_margin)
    )
    return fig

def ov_num_attacks_indicator(df):
    num_attacks = len(df)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=num_attacks,
        title={"text": "Attacks", 'font': {'size': 26}},
        number={'font': {'size': 24}}
    ))
    fig.update_layout(
    margin=dict(l=ov_ind_margin, r=ov_ind_margin, t=ov_ind_margin, b=ov_ind_margin)
    )
    return fig

def ov_victims_wounded_indicator(df):
    total_wounded = df['NVictimsWounded'].sum(skipna=True)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=total_wounded,
        title={"text": "Wounded", 'font': {'size': 26}},
        number={'font': {'size': 24}}
    ))
    fig.update_layout(
    margin=dict(l=ov_ind_margin, r=ov_ind_margin, t=ov_ind_margin, b=ov_ind_margin)
    )
    return fig

def ov_countries_affected_indicator(df):
    num_countries_affected = df['Country'].nunique()
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=num_countries_affected,
        title={"text": "Countries Affected", 'font': {'size': 26}},
        number={'font': {'size': 24}}
    ))
    fig.update_layout(
    margin=dict(l=ov_ind_margin, r=ov_ind_margin, t=ov_ind_margin, b=ov_ind_margin)
    )
    return fig

def ov_victims_killed_indicator(df):
    total_victims_killed = df['NVictimsKilled'].sum(skipna=True)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=total_victims_killed,
        title={"text": "Killed", 'font': {'size': 26}},
        number={'font': {'size': 24}}
    ))
    fig.update_layout(
    margin=dict(l=ov_ind_margin, r=ov_ind_margin, t=ov_ind_margin, b=ov_ind_margin)
    )
    return fig

def ov_stacked_area_chart_casualties2(df, template):
    df_summed = df.groupby('Year').agg({'NVictimsWounded': 'sum', 'NVictimsKilled': 'sum'}).reset_index()
    df_attacks = df.groupby('Year').size().reset_index(name='Attacks')

    fig = px.area(df_summed, x='Year', y=['NVictimsWounded', 'NVictimsKilled'],
                  labels={'value': 'Number of Victims', 'variable': 'Type'},
                  title='Casualties over Time',
                  color_discrete_sequence=['yellow', 'red'],
                  template=template)

    for trace in fig.data:
        trace.name = trace.name.replace("NVictims", "")
    '''
    # Add line trace for attacks per year
    fig.add_trace(px.line(df_attacks, x='Year', y='Attacks', labels={'Attacks': 'Number of Attacks'}).data[0])

    # Update layout to show secondary y-axis
    fig.update_layout(
        yaxis2=dict(
            title='Number of Attacks',
            overlaying='y',
            side='right'
        ),
        showlegend=True,
        height=400
    )
    '''
    return fig
'''
def ov_stacked_bar_attacks_by_year(df, template):
    df_grouped = df.groupby(['Year', 'AttackSuccess']).size().reset_index(name='Count')

    fig = px.bar(df_grouped, x='Year', y='Count', color='AttackSuccess',
                 title='Stacked Bar Plot of Attacks by Year',
                 labels={'Count': 'Number of Attacks'},
                 template=template)

    fig.update_layout(barmode='stack')

    return fig
'''
def line_polar_attack_types(df,template):
    # Melt the DataFrame
    df_melted = pd.melt(df, value_vars=['AttackType1', 'AttackType2', 'AttackType3'],
                        var_name='AttackType', value_name='AttackTypeValue')

    # Drop rows with NaN values
    df_melted = df_melted.dropna(subset=['AttackTypeValue'])
    grp = df_melted.groupby("AttackTypeValue").size().reset_index(name="frequency")

    grp  = grp[grp['AttackTypeValue'] != 'Unknown']
    # Create the line polar plot
    fig = px.line_polar(grp, r="frequency",theta='AttackTypeValue',
                        line_close=True,
                        
                        title = 'Attack Method Profile',
                        color_discrete_sequence = px.colors.sequential.Plasma_r, template=template
                        )

    fig.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=False)), showlegend=False)
    return fig

def ov_attack_success_gauge(df, template):
    # Calculate attack success rate (assuming 'AttackSuccess' is a column in the DataFrame)
    success_rate = (df['AttackSuccess'].sum() / len(df)) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=success_rate,
        number=dict(suffix='%'),
        title={'text': "Attack Success Rate"},
        #domain={'x': [0, 1], 'y': [0, 1]},
        gauge=dict(
            axis=dict(range=[0, 100]),
            bar=dict(color="red"),
        )
    ))
    fig.update_layout(
        template=template,
        margin=dict(l=ov_ind_margin, r=ov_ind_margin, t=ov_ind_margin, b=ov_ind_margin)
    )

    return fig

def ov_targetTypeBar(df,template):
    # Melt the DataFrame
    df_melted = pd.melt(df, value_vars=['TargetType1', 'TargetType2', 'TargetType3'],
                        var_name='TargTypeCol', value_name='TargTypeValue')

    # Drop rows with NaN values
    df_melted = df_melted.dropna(subset=['TargTypeValue'])
    grp = df_melted.groupby("TargTypeValue").size().reset_index(name="frequency")
    top_targets = grp.sort_values(by='frequency', ascending=False).head(5)
    fig = px.bar(top_targets, x='frequency', y='TargTypeValue',
                 title='Top 5 Targets',
                 orientation='h', template=template)
    fig.update_layout(yaxis_categoryorder='total ascending')
    return fig



def BuildGetOverviewLayout(filtered_df,template):
    row_marg ='20px'
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=ov_num_attacks_indicator(filtered_df))),
            dbc.Col(dcc.Graph(figure=ov_years_active_indicator(filtered_df))),
            dbc.Col(dcc.Graph(figure=ov_victims_killed_indicator(filtered_df))),
            dbc.Col(dcc.Graph(figure=ov_victims_wounded_indicator(filtered_df))),
            dbc.Col(dcc.Graph(figure=ov_attack_success_gauge(filtered_df, template))),
        ],style={'margin-top': row_marg}), 

        dbc.Row([
            dbc.Col(dcc.Graph(figure=ov_stacked_area_chart_casualties2(filtered_df,template))),
            dbc.Col(dcc.Graph(figure=line_polar_attack_types(filtered_df,template))),
        ], style={'margin-top': row_marg}),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=ov_targetTypeBar(filtered_df,template))),
        ], style={'margin-top': row_marg}),  
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