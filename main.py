# -*- coding: utf-8 -*-
"""
Created on Mon May  2 10:21:25 2022

@author: stark
Things are working with this simple dashboard.
Prices are updating but I am not seeing the immediate price change.
Must be something that CoinMarketCap.com does in order to get you buy their API subscription
TODO: Think about getting an API key.
TODO: Need to think about more functionality
TODO: Need to think about alerts
TODO: Time to deploy the first version to my raspberry-pi
"""

from packages import *
from functions import *

if not os.path.exists("images"):
    os.mkdir("images")
ts = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
all_data = []
for x in urls_dict.keys():
    tmp = make_request_v2(x)
    all_data.append(tmp)
    print(tmp)
df = pd.DataFrame(all_data)
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
assets = load_assets('assets.csv')
test = compute_spot_returns(assets, df)


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    dbc.Row([
    html.Div(children=[
        html.H1(children='Crypto Dashboard'),
        html.Div(children="""
                 Monitoring Performance of Crypto Investments
                 """),
        html.Div(id='time'),
        dcc.Interval(
            id='time-interval-component',
            interval=1*1000,
            n_intervals=0
            ),
        html.Div(id='time-last-update', children=f"Last Updated: {ts}"),
        dcc.Interval(
            id='time-last-interval',
            interval=15*1000,
            n_intervals=0)
        ], style={'padding': 10, 'flex': 1})
    ]),
    dbc.Row([ 
        dbc.Col([
            html.Div(children=[
                dash_table.DataTable(#data=test.to_dict('records'),
                                     id='main-tbl',
                                     columns=[{"name":i, "id":i} for i in test.columns],
                                     style_data_conditional=[
                                         {'if':{
                                             'filter_query': '{perc_return} < 0',
                                             'column_id': 'perc_return'},
                                             'backgroundColor':'red',
                                             'color':'white'},
                                         {'if':{
                                             'filter_query': '{perc_return} > 0',
                                             'column_id': 'perc_return'},
                                            'backgroundColor':'green',
                                            'color':'white' }
                                     ]),
                dcc.Interval(
                    id='main-update2',
                    interval=15*1000,
                    n_intervals=0
                    )
                ])
            ]),
        dbc.Col([
            html.Div(
                children=[
                    dash_table.DataTable(#data=df.to_dict('records'),
                                         id='spot-price-tbl',
                                         columns=[{"name":i, "id":i} for i in df.columns],
                                         ),
                    dcc.Interval(
                        id='main-update3',
                        interval=15*1000,
                        n_intervals=0
                        )
                ])
            ])
        ])
    ])

@app.callback(Output('time', 'children'),
              [Input('time-interval-component', 'n_intervals')]
              )
def first_callback(n):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d, %H:%M:%S")
    return "Current Time: " + current_time

@app.callback(
    Output('time-last-update', 'children'),
    Input('time-last-interval', 'n_intervals'),

    )
def update_time(n):
    ts = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    return "Last Updated: " + ts

@app.callback(
        Output('spot-price-tbl','data'),
        Output('spot-price-tbl', 'columns'),
        Input('main-update3', 'n_intervals')
    )
def update_spot_price_tbl(n):
    all_data = []
    for x in urls_dict.keys():
        tmp = make_request_v2(x)
        all_data.append(tmp)
        #print(tmp)
    df = pd.DataFrame(all_data)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df.to_dict('records'), [{"name":i, "id":i} for i in df.columns]

@app.callback(
        Output('main-tbl','data'),
        Output('main-tbl', 'columns'),
        Input('main-update2', 'n_intervals')
    )
def update_main_tbl(n):
    all_data = []
    for x in urls_dict.keys():
        tmp = make_request_v2(x)
        all_data.append(tmp)
        #print(tmp)
    df = pd.DataFrame(all_data)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    test = compute_spot_returns(assets, df)
    return test.to_dict('records'), [{"name":i, "id":i} for i in test.columns]


if __name__ == "__main__":
    app.run_server(debug=True)