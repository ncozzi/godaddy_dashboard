# dashboard
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np




train_df = pd.read_csv('data/train_backup.csv')
test_df = pd.read_csv('data/test_backup.csv')
dash_df = pd.read_csv('data/dash_df.csv')



dates = pd.Series(list(set(dash_df.first_day_of_month) & set(train_df.first_day_of_month))).sort_values(ignore_index=True)
daterange = [x for x in range(len(dates))]


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Kaggle: GoDaddy Microbusiness by ncozzi"
app.layout = html.Div([html.H1("MBD growth forecasts")])



all_states = list(train_df.state.unique())
app.layout = html.Div([
    # html.Title('Kaggle: GoDaddy Microbusiness Growth forecasts by ncozzi'),
    html.H1(children='Kaggle: GoDaddy Microbusiness Growth forecasts'),
    html.H2(children='Created by @ncozzi'),
    html.P('Dashboard for visualizing microbusiness density + forecasts of 3135 USA counties'),
    html.A('Link to Jupyter notebook explaining the methodology behind the predictions:', href='https://github.com/ncozzi/kaggle_godaddy', target="_blank"),
    # html.P('https://github.com/ncozzi/kaggle_godaddy'),
    html.Hr(),
    html.H3(children='Box plot of MBD per date'),
    dcc.Slider(min=daterange[0], #the first date
               max=daterange[-1], #the last date
               value=daterange[-1], #default: the first,
               step=1,
               marks = {numd:date for numd,date in zip(daterange, list(dates))
                        if numd==max(daterange) or (numd-1)%3==0},
               id='slider-date'
               ),
    dcc.Graph(id='dd-boxplot'),
    html.Hr(),
    html.H3(children='MBD forecast per state/county'),
    dcc.Dropdown(all_states,
                 value='California',
                 id='dropdown_state'),
    dcc.Graph(id='dd-output-state'),
    dcc.Dropdown(id='dropdown_cfips',
                 value='Calaveras County'),
    dcc.Graph(id='dd-output-cfips')
])


# plot_df = dash_df[pd.to_datetime(dash_df['first_day_of_month'])==daterange[0]]



unique_states = dash_df.state.sort_values().unique()
@app.callback(
    Output('dd-boxplot', 'figure'),
    Input('slider-date', 'value'))
def boxplot_date(date):
    plot_df = dash_df[pd.to_datetime(dash_df['first_day_of_month'])==dates[date]]
    fig = go.Figure()
    for state in unique_states:
        y_array = np.array(plot_df[(plot_df.state==state)]['microbusiness_density'])
        fig.add_trace(go.Box(
            y=list(y_array),
            name=state,
            boxpoints='all'
            # marker_color='#3D9970'
        ))
    
    fig.update_yaxes(type='log')
    fig.update_layout(
        # width=1000,
        height=600,
        title='Box plot of microbusiness density, per state and date',
        xaxis_title="state",
        yaxis_title="Log-microbusiness density",
        # legend_title="Legend Title",
        legend = dict(font = dict(family = "Courier", size = 8, color = "black")),
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )
    
    return fig





# filtering the state options
@app.callback(
    Output('dropdown_cfips', 'options'),
    Input('dropdown_state', 'value'))
def set_cities_options(selected_state):
    all_county_names = list(train_df[train_df.state==selected_state].county.unique())
    return all_county_names


# function for state graph
@app.callback(
    Output('dd-output-state', 'figure'),
    Input('dropdown_state', 'value'))
def update_figure1(state):
 
    plot_df = dash_df[dash_df['state']==state]

    fig = go.Figure()
    for cfips in plot_df.cfips.unique():
        plot_df_cfips = plot_df[plot_df.cfips==cfips]
        cfips_name = plot_df_cfips.county.unique()[0]
        fig.add_scattergl(y=plot_df_cfips['microbusiness_density'],
                          x=plot_df_cfips['first_day_of_month'].where(plot_df['first_day_of_month'].isin(
                              list(train_df.first_day_of_month) + [test_df.first_day_of_month[0]])),
                          line={'color': 'black'},
                          mode='lines+markers',
                         name="Observed, "+cfips_name)

        # Above threshhgold
        fig.add_scattergl(y=plot_df_cfips['microbusiness_density'],
                          x=plot_df_cfips['first_day_of_month'].where(
                              plot_df['first_day_of_month'].isin(test_df.first_day_of_month)),
                          line={'color': 'red'},
                          mode='lines+markers',
                         name="Forecasted, "+cfips_name)

    fig.update_yaxes(type='log')
    
    fig.update_layout(
        # width=1000,
        height=600,
        title="MBD forecast (2023) for state {}".format(state),
        xaxis_title="Date",
        yaxis_title="Microbusiness density",
        # legend_title="Legend Title",
        legend = dict(font = dict(family = "Courier", size = 8, color = "black")),
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )
    
    return fig


# function for county graph
@app.callback(
    Output('dd-output-cfips', 'figure'),
    Input('dropdown_state', 'value'),
    Input('dropdown_cfips', 'value'))
def update_figure2(state, county):
    plot_df = dash_df[(dash_df['state']==state) & \
                              (dash_df['county']==county)]

    fig = go.Figure()
    fig.add_scattergl(y=plot_df['microbusiness_density'],
                      x=plot_df['first_day_of_month'].where(plot_df['first_day_of_month'].isin(
                              list(train_df.first_day_of_month) + [test_df.first_day_of_month[0]])),
                      line={'color': 'black'},
                     name="Observed")

    # Above threshhgold
    fig.add_scattergl(y=plot_df['microbusiness_density'],
                      x=plot_df['first_day_of_month'].where(
                          plot_df['first_day_of_month'].isin(test_df.first_day_of_month)),
                      line={'color': 'red'},
                     name="Forecasted")


    fig.update_layout(
        height=600,
        title="MBD forecast (2023) for {}".format(str(county)),
        xaxis_title="Date",
        yaxis_title="Microbusiness density",
        # legend_title="Legend Title",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )

    return fig



if __name__ == '__main__':
    app.run_server(port=1234, debug=True, use_reloader=True)
