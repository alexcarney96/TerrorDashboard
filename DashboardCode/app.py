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
import plotly.subplots as sp
import colorsys
import numpy as np


######################################Build and define some custom colors
t_green = '#47ed05'
t_light_green = '#b1dba0'
t_bluegray ='#36413e'
t_colors = [t_green,t_light_green,t_bluegray]

color_scale = [
        [0, t_light_green],
        [1, t_green]
    ]

######################################################################################## Build our app  
dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
template = "darkly" #"cyborg"
load_figure_template(template)

############################################################################# Loading data and making Group index for performance                   
raw_df = pd.read_parquet("gtd_clean_dataset_pqt.parquet")
raw_df.set_index('Group', inplace=True)

#################################################################################### build overview
ov_ind_margin = 0
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
        number={'font': {'size': 24}, 'font_color' : t_green}
    ))
    return fig

def ov_num_attacks_indicator(df):
    num_attacks = len(df)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=num_attacks,
        title={"text": "Attacks", 'font': {'size': 26}},
        number={'font': {'size': 24}, 'font_color' : t_green}
    ))

    return fig

def ov_victims_wounded_indicator(df):
    total_wounded = df['NVictimsWounded'].sum(skipna=True)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=total_wounded,
        title={"text": "Wounded", 'font': {'size': 26}},
        number={'font': {'size': 24}, 'font_color' : t_green}
    ))
    return fig

def ov_countries_affected_indicator(df):
    num_countries_affected = df['Country'].nunique()
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=num_countries_affected,
        title={"text": "Countries", 'font': {'size': 26}},
        number={'font': {'size': 24}, 'font_color' : t_green}
    ))

    return fig

def ov_victims_killed_indicator(df):
    total_victims_killed = df['NVictimsKilled'].sum(skipna=True)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=total_victims_killed,
        title={"text": "Killed", 'font': {'size': 26}},
        number={'font': {'size': 24}, 'font_color' : t_green}
    ))

    return fig


def ov_kill_wounded(df, template):
    # Todo can do this with one dataset
    df_summed = df.groupby('Year').agg({'NVictimsWounded': 'sum', 'NVictimsKilled': 'sum'}).reset_index()
    df_attacks = df.groupby('Year').size().reset_index(name='Attacks')

    fig_line = px.line(df_summed, x='Year', y=['NVictimsWounded', 'NVictimsKilled'],
                       labels={'value': 'Number of Victims', 'variable': 'Type'},
                       title='', color_discrete_sequence=[t_light_green, t_green],
                       template=template)

    for trace in fig_line.data:
        trace.name = trace.name.replace("NVictims", "")

    fig_bar = go.Figure(go.Bar(x=df_attacks['Year'],
                               y=df_attacks['Attacks'], name='Events', marker_color=t_bluegray))
    fig_bar.update_layout(showlegend=False)

    subplot = sp.make_subplots(rows=2, cols=1, shared_xaxes=True,
                               vertical_spacing=0.2, subplot_titles=['Casualties', 'Attack Frequency'])

    for trace in fig_line.data:
        subplot.add_trace(trace, row=1, col=1)
    subplot.add_trace(fig_bar.data[0], row=2, col=1)

    subplot.update_layout(template=template, margin={"r": 5, "t": 20, "l": 5, "b": 5})
    return subplot

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
                        title = 'Attack Method',
                        color_discrete_sequence=[t_green], template=template
                        )

    fig.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=False)), 
                      showlegend=False,
                      margin={"r":50,"t":30,"l":50,"b":30}
                      )
    return fig

def ov_attack_success_gauge(df, template):
    # Calculate attack success rate (assuming 'AttackSuccess' is a column in the DataFrame)
    success_rate = (df['AttackSuccess'].sum() / len(df)) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=success_rate,
        number=dict(suffix='%'),
        title={'text': "Attack Success Rate"},
        gauge=dict(
            axis=dict(range=[0, 100]),
            bar=dict(color=t_green),
        )
    ))
    fig.update_layout(
        template=template,
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
                 title='Top 5 Target Types',color_discrete_sequence=[t_green],
                template=template) 
    fig.update_layout(yaxis_categoryorder='total ascending',yaxis=dict(title=''),
                      margin={"r":5,"t":40,"l":5,"b":5}
                      )
    return fig

def ov_attacks_by_country_choropleth(df, template):


    # Calculate the attack count by country
    attacks_df = df.groupby("Country").size().reset_index(name="attacks")
    attacks_df = attacks_df[attacks_df['attacks'] > 0]

    # Calculate the sum of killed and wounded by country
    victims_df = df.groupby("Country").agg({
        'NVictimsKilled': 'sum',
        'NVictimsWounded': 'sum'
    }).reset_index()

    # Merge the two dataframes on 'Country'
    grouped_df = attacks_df.merge(victims_df, on='Country', how='left')

    # Create a choropleth map
    fig = px.choropleth(grouped_df,
                        locations='Country',
                        locationmode='country names',
                        color='attacks',
                        title='Attacks by Country',
                        color_continuous_scale=color_scale,
                        range_color=(0, grouped_df['attacks'].max()),
                        template=template,
                        hover_data=['NVictimsKilled', 'NVictimsWounded', 'Country'])

    fig.update_layout(
        template=template,
        coloraxis_showscale=False,
        margin={"r": 5, "t": 30, "l": 5, "b": 5}
    )

    return fig


def BuildGetOverviewLayout(filtered_df,template):
    row_marg ='25px'
    ind_height = '100px'
    meth_height = '450px'
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=ov_years_active_indicator(filtered_df), style={'height': ind_height}),width=2),
            dbc.Col(dcc.Graph(figure=ov_countries_affected_indicator(filtered_df), style={'height': ind_height}),width=2),
            dbc.Col(dcc.Graph(figure=ov_num_attacks_indicator(filtered_df), style={'height': ind_height}),width=4),
            dbc.Col(dcc.Graph(figure=ov_victims_killed_indicator(filtered_df), style={'height': ind_height}),width=2),
            dbc.Col(dcc.Graph(figure=ov_victims_wounded_indicator(filtered_df), style={'height': ind_height}),width=2),
        ],style={'margin-top': row_marg}), 

        dbc.Row([
            dbc.Col(dcc.Graph(figure=ov_kill_wounded(filtered_df,template), style={'height': '250px'}),width=9),
            dbc.Col(dcc.Graph(figure=ov_attack_success_gauge(filtered_df, template), style={'height': '250px'}),width=3),
        ], style={'margin-top': row_marg}),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=ov_attacks_by_country_choropleth(filtered_df,template), style={'height': meth_height}),width=8),
            dbc.Col(
                children = [
                dcc.Graph(figure=line_polar_attack_types(filtered_df,template), style={'height': '225px'}),
                dcc.Graph(figure=ov_targetTypeBar(filtered_df,template), style={'height': '225px'})
                ],width=4),
            
            
        ], style={'margin-top': row_marg}),
    ]



#####################################################################################Build Attack page
def at_area_chart(df,template,c_val):
    val_vars, _title,_legend_title = None,None,None
    if (c_val == 'Weapon'):
        val_vars = ['WeaponType1','WeaponType2','WeaponType3']
        _title = 'Top 5 Most Used Weapons Over Time'
        _legend_title = 'Weapons Choice Evolution'
    if (c_val == 'Attack'):
        val_vars = ['AttackType1','AttackType2','AttackType3']
        _title = 'Top 5 Attack Methods Over Time'
        _legend_title = 'Attack Method Evolution'
    if (c_val == 'Target'):
        val_vars = ['TargetType1','TargetType2','TargetType3']
        _title = 'Top 5 Targets Over Time'
        _legend_title = 'Target Method Evolution'

    df_melted = pd.melt(df,id_vars=['Year'],value_vars=val_vars,
                        var_name='TypeCol', value_name='TypeValue')
    df_melted = df_melted.dropna(subset=['TypeValue'])
    df_melted = df_melted[df_melted['TypeValue']!='Unknown']
    df_melted = df_melted[df_melted['TypeValue']!='Other']

    top_5_df = df_melted.groupby('TypeValue').size().reset_index(name='NumAttacks').sort_values(by='NumAttacks', ascending=False).head(5)
    top_5 = top_5_df['TypeValue'].unique()

    grouped_df = df_melted.groupby(['Year', 'TypeValue']).size().reset_index(name='NumAttacks')
    grouped_df = grouped_df[grouped_df['TypeValue'].isin(top_5)]

    fig = px.area(grouped_df, x='Year', y='NumAttacks', color='TypeValue',
                    title=_title,
                    template=template)
    fig.update_layout(legend_title_text=_legend_title,yaxis_title='Attacks',margin={"r": 5, "t": 30, "l": 5, "b": 5})
    return fig

def at_area_chart_tabs(filtered_df,template,height):
    return dbc.Tabs([
        dbc.Tab(label='Attack Method Evolution',tab_id='Attack',active_label_style={'color' : t_green}, children=[
            dcc.Graph(figure=at_area_chart(filtered_df, template,'Attack'),style={'height': height}),
        ]),

        dbc.Tab(label='Target Selection Evolution',tab_id='Target',active_label_style={'color' : t_green}, children=[
            dcc.Graph(figure=at_area_chart(filtered_df, template,'Target'),style={'height': height})
        ]),
        #dbc.Tab(label='Weapon Usage Evolution',tab_id='Weapon',active_label_style={'color' : t_green}, children=[
        #    dcc.Graph(figure=at_area_chart(filtered_df, template,'Weapon'),style={'height': height})
        #]), 
    ],active_tab='Attack')

def at_sui_attack_gauge(df, template):
    # Calculate attack success rate (assuming 'AttackSuccess' is a column in the DataFrame)
    success_rate = (df['SuicideAttack'].sum() / len(df)) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=success_rate,
        number=dict(suffix='%'),
        title={'text': "Suicide Attack Rate"},
        gauge=dict(
            axis=dict(range=[0, 100]),
            bar=dict(color=t_green),
        )
    ))
    fig.update_layout(
        template=template,margin={"r": 10, "t": 55, "l": 10, "b": 10}
    )

    return fig


def at_cas_stacked_bar_chart(filtered_df, template):
    df_melted = pd.melt(filtered_df, id_vars=['NVictimsKilled', 'NVictimsWounded', 'Casualties'],
                        value_vars=['AttackType1', 'AttackType2', 'AttackType3'],
                        var_name='AttackTypeCol', value_name='AttackType')
    df_melted = df_melted.dropna(subset=['AttackType'])
    df_melted = df_melted[df_melted['AttackType'] != 'Unknown']
    df_melted = df_melted[df_melted['AttackType'] != 'Other']
    df_summed = df_melted.groupby('AttackType').agg({'NVictimsWounded': 'sum',
                                                      'NVictimsKilled': 'sum',
                                                      'Casualties': 'sum'}).reset_index()
    top_5_df = df_melted.groupby('AttackType').size().reset_index(name='NumAttacks').sort_values(by='NumAttacks',
                                                                                                   ascending=False).head(
        5)
    top_5 = top_5_df['AttackType'].unique()
    df_summed = df_summed[df_summed['AttackType'].isin(top_5)]
    df_summed = df_summed[(df_summed['NVictimsKilled'] > 0) | (df_summed['NVictimsWounded'] > 0)]

    #percentage of killed and wounded relative to total casualties
    df_summed['PercentKilled'] = (df_summed['NVictimsKilled'] / (df_summed['NVictimsKilled']+df_summed['NVictimsWounded'])) * 100
    df_summed['PercentWounded'] = (df_summed['NVictimsWounded'] / (df_summed['NVictimsKilled']+df_summed['NVictimsWounded'])) * 100

    fig = px.bar(df_summed, y="AttackType", x=['PercentKilled', 'PercentWounded'],
                 title="Lethality of Top 5 Attack Methods",
                 color_discrete_map={'PercentWounded': t_light_green, 'PercentKilled': t_green}
                 )
    for trace in fig.data:
        trace.name = trace.name.replace("Percent", "% ")

    fig.update_layout(
        yaxis_title='',
        xaxis_title='% of Total Casualties',
        legend_title='',
        template=template,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(0, 101, 10)),
            ticktext=[f"{percent}%" for percent in range(0, 101, 10)],
            tickfont=dict(size=10)
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 5}
    )
    return fig

def at_atts_per_yr_indicator(df):
    attacks_per_year = df['Year'].value_counts().reset_index()
    attacks_per_year.columns = ['Year', 'NumAttacks']
    average_attacks_per_year = attacks_per_year['NumAttacks'].mean()
    rounded_average_attacks = round(average_attacks_per_year, 1)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=rounded_average_attacks,
        title={"text": "Attacks per Year", 'font': {'size': 20}},
        number={'font': {'size': 20}, 'font_color' : t_green}
    ))
    return fig

def at_claimed_perc_indicator(df):
    _df = df[df['GroupClaimed']>=0]
    claimed_attacks = _df['GroupClaimed'].sum()
    total_attacks = len(_df)
    percentage_claimed = (claimed_attacks / total_attacks) * 100
    percentage_claimed = round(percentage_claimed, 1)
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="number",
        value=percentage_claimed,
        title={"text": "Attacks Claimed", 'font': {'size': 20}},
        number={'suffix':'%','font': {'size': 20}, 'font_color' : t_green}
    ))
    return fig

def at_kpa_wpa_indicator(df,k_or_a):
    rounded_average_killed_per_attack = None
    _title = ''
    if (k_or_a == 'Killed'):
        average_killed_per_attack = df['NVictimsKilled'].mean()
        rounded_average_killed_per_attack = round(average_killed_per_attack, 1)
        _title = 'Killed Per Attack'
    if (k_or_a == 'Wounded'):
        average_killed_per_attack = df['NVictimsWounded'].mean()
        rounded_average_killed_per_attack = round(average_killed_per_attack, 1)
        _title = 'Wounded Per Attack'     
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode="number",
        value=rounded_average_killed_per_attack,
        #number=dict(suffix='%'),
        title={"text": _title, 'font': {'size': 20}},
        number={'font': {'size': 20}, 'font_color' : t_green}
    ))
    return fig

#constant is Targets, Target Type, Attack Method
#values = num events, color = casualties
def at_treemap(df,template):
    _df = df.copy()
    _df['row_counter'] = 1
    df_melted = pd.melt(_df, id_vars=['NVictimsKilled', 'NVictimsWounded', 'Casualties','row_counter'],
                        value_vars=['AttackType1', 'AttackType2', 'AttackType3'],
                        var_name='AttackTypeCol', value_name='AttackType')
    df_melted = df_melted.dropna(subset=['AttackType'])
    df_melted = df_melted[df_melted['AttackType'] != 'Unknown']
    df_melted = df_melted[df_melted['AttackType'] != 'Other']
    df_summed = df_melted.groupby('AttackType').agg({'NVictimsWounded': 'sum',
                                                      'NVictimsKilled': 'sum',
                                                      'Casualties': 'sum'}).reset_index()
    top_5_df = df_melted.groupby('AttackType').size().reset_index(name='NumAttacks').sort_values(by='NumAttacks',
                                                                                                   ascending=False).head(5)
    top_5 = top_5_df['AttackType'].unique()
    df_summed = df_summed[df_summed['AttackType'].isin(top_5)]
    df_summed = df_summed[(df_summed['NVictimsKilled'] > 0) | (df_summed['NVictimsWounded'] > 0)]


def at_treemap_helper(df,in_str):
    #just melts
    val_vars,var_nm,value_nm = [],'',''
    if (in_str == 'AttackType'): 
        val_vars = ['AttackType1', 'AttackType2', 'AttackType3']
        var_nm ='AttackTypeCol'
        value_nm ='AttackType'
    if (in_str == 'TargetType'): 
        val_vars = ['TargetType1', 'TargetType2', 'TargetType3']
        var_nm ='TargetTypeCol'
        value_nm ='TargetType'
    ret = pd.melt(df, id_vars=['EventID','Casualties','AttackSuccess'],
                        value_vars=val_vars,
                        var_name=var_nm, value_name=value_nm)
    ret = ret.dropna(subset=[value_nm])
    return ret
    

def at_TreeMap(df,template):
    '''
    px.Constant(Targets)v
    TargetType, AttackType,NumEvents|Casualties values=Numevents, colored by Casualties (merged on eventid)
    '''
    #TARG_DF cols : TargetType, EventID, Casualties
    #ATT_DF cols : AttackType, EventID, Casualties
    targ_df = at_treemap_helper(df,'TargetType')# 
    att_df = at_treemap_helper(df,'AttackType')
    targ_df = targ_df[targ_df['TargetType'] != 'Unknown']
    targ_df = targ_df[targ_df['TargetType'] != 'Other']
    att_df = att_df[att_df['AttackType'] != 'Unknown']
    att_df = att_df[att_df['AttackType'] != 'Other']

    #top 5 targets only
    top_5_df = targ_df.groupby('TargetType').size().reset_index(name='NumAttacks').sort_values(by='NumAttacks',
                                                                                           ascending=False).head(5)
    top_5_targs = top_5_df['TargetType'].unique()
    targ_df = targ_df[targ_df['TargetType'].isin(top_5_targs)]
    
    #join on the attack data
    merged_df = pd.merge(targ_df, att_df[['EventID', 'AttackType']], on='EventID', how='left')
    merged_df['Casualties'] = merged_df['Casualties'].fillna(0)
    #MERGED_DF : EventID, TargetType, AttackType, Casualties
    grouped_df = merged_df.groupby(['TargetType', 'AttackType']).agg({
    'Casualties': 'sum',
    'EventID': 'count'
    }).reset_index()

    grouped_df = grouped_df.rename(columns={'EventID': 'Attacks'})
    print(grouped_df)
    #GROUPED_DF has columns : TargetType,AttackType,Casualties,NumOccurences
    fig = px.treemap(grouped_df, path=[px.Constant("Top 5 Targets"), 'TargetType', 'AttackType'], values='Attacks',
                  color='Casualties',
                  color_continuous_scale='Viridis',#'Viridis',#'RdBu',
                  color_continuous_midpoint=np.average(grouped_df['Casualties'], weights=grouped_df['Attacks']))
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25),template=template,title='Attack Profile of Top 5 Targets')
    return fig   
#######

def at_bar_polar(df,template,in_str):
    _title = ''
    _col = ''
    if(in_str == 'AttackType'):
        _title = 'Top 5 Methods'
        _col = 'AttackType'
    if(in_str == 'TargetType'):
        _title = 'Top 5 Targets'
        _col = 'TargetType'
    grp = at_treemap_helper(df,in_str)
    grp  = grp[grp[_col] != 'Unknown']
    grp  = grp[grp[_col] != 'Other']
    top_5_df = grp.groupby(_col).size().reset_index(name='NumAttacks').sort_values(by='NumAttacks',
                                                                                           ascending=False).head(5)
    top_5_targs = top_5_df[_col].unique()
    _df = grp[grp[_col].isin(top_5_targs)]

    _df = _df.groupby(_col).size().reset_index(name="frequency")

    #only inlcude the top 5
    fig = px.bar_polar(_df, r="frequency",theta=_col,
                        title = _title,
                        color_discrete_sequence=[t_green], template=template
                        )

    fig.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=False)), 
                      showlegend=False,
                      margin={"r":75,"t":30,"l":75,"b":30}
                      )
    return fig



def BuildGetAttackLayout(filtered_df,template):
    row_marg ='25px'
    ind_height = '125px'#
    meth_height = '450px'
    pie_height= '350px'
    bar_height = '215px'
    return [
        dbc.Row([
            dbc.Col(dcc.Graph(figure=at_atts_per_yr_indicator(filtered_df), style={'height': ind_height}),width=2),
            dbc.Col(dcc.Graph(figure=at_claimed_perc_indicator(filtered_df), style={'height': ind_height}),width=2),
            dbc.Col(dcc.Graph(figure=at_sui_attack_gauge(filtered_df, template), style={'height': ind_height}),width=4),
            dbc.Col(dcc.Graph(figure=at_kpa_wpa_indicator(filtered_df,'Killed'), style={'height': ind_height}),width=2),
            dbc.Col(dcc.Graph(figure=at_kpa_wpa_indicator(filtered_df,'Wounded'), style={'height': ind_height}),width=2),
            
        ], style={'margin-top': row_marg}),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=at_bar_polar(filtered_df,template,'TargetType'), style={'height': bar_height}),width=4),
            dbc.Col(dcc.Graph(figure=at_bar_polar(filtered_df,template,'AttackType'), style={'height': bar_height}),width=4),
            dbc.Col(dcc.Graph(figure=at_cas_stacked_bar_chart(filtered_df,template), style={'height': bar_height}),width=4)
            
        ], style={'margin-top': row_marg}),
        
        dbc.Row([ 
            dbc.Col(at_area_chart_tabs(filtered_df,template,'270px'),width=12),
        ], style={'margin-top': row_marg}),

        dbc.Row([
            dbc.Col(dcc.Graph(figure=at_TreeMap(filtered_df,template), style={'height': '400px'}),width=12),
            
        ], style={'margin-top': row_marg}),

    ]




#####################################################################################Build Geo page
def BuildGetGeoLayout(filtered_df,template):
    row_marg ='25px'
    return [
        dbc.Row([ 
            #dbc.Col(dcc.Graph(figure=ov_stacked_area_chart_casualties2(filtered_df,template), style={'height': '250px'}),width=9),
            dbc.Col(dcc.Graph(figure=ov_attack_success_gauge(filtered_df, template), style={'height': '250px'}),width=3),
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
        dbc.NavItem(dbc.NavLink("Attack Profile", href="/attackmethod", active=False, id='attackmethod-link')),
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
        dcc.Location(id='url', refresh=False, pathname='/overview'),  # Set default page to "/overview"
        navbar,
        html.Div(id='page-content')
    ],
    fluid=False,className="dbc"
)

########################################### Callback to update page content based on URL and dropdown value
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname'),
               Input('group-dropdown', 'value')])
def update_page_content(pathname, selected_group):
    filtered_df = raw_df[raw_df.index == selected_group]
    if pathname == '/overview':
        return BuildGetOverviewLayout(filtered_df,template)

    elif pathname == '/attackmethod':
        return BuildGetAttackLayout(filtered_df,template)

    elif pathname == '/geo':
        return BuildGetGeoLayout(filtered_df,template)

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