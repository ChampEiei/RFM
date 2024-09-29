import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State

# สมมติว่าคุณมีข้อมูล rfm และ k_range, sse
rfm = pd.read_excel('RFM.xlsx')  # ตัวอย่างการอ่านข้อมูลจากไฟล์
k_range = range(1, 11)
sse = [
    428.99999999999994, 245.30411208806478, 133.78674291671692, 107.4648386269977,
    88.31541170025612, 67.55134545296497, 48.897540405130165, 43.52660193638751,
    41.30611529443592, 28.31420745735582
]

# Create the elbow method figure
fig_elbow = px.line(x=k_range, y=sse, markers=True, title='Elbow Method For Optimal k')
fig_elbow.update_layout(xaxis_title='Number of Clusters', yaxis_title='SSE')

# Create the cluster scatter matrix figure
fig_scatter = px.scatter_matrix(rfm, dimensions=['Recency', 'Frequency', 'Monetary'], color='Cluster', title='Cluster Scatter Matrix')

# Create the bar chart figure
group = rfm.groupby(['Cluster'])['Monetary'].sum().reset_index()
fig_bar = px.bar(group, x='Cluster', y='Monetary', color='Cluster', title='Total Monetary by Cluster')

# Create the scatter plot for Monetary vs Frequency
fig_monetary_vs_frequency = px.scatter(rfm, x='Frequency', y='Monetary', color='Cluster', size='Monetary',
                                       title='Monetary vs Frequency Scatter Plot', size_max=100)

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Define the layout for password input
app.layout = html.Div(id='page-content', children=[
    html.H1('Cluster Analysis Dashboard', style={'textAlign': 'center', 'color': '#003366'}),
    html.Div(id='password-screen', children=[
        html.H2('Please enter the password to access the dashboard:', style={'textAlign': 'center'}),
        dcc.Input(id='password-input', type='password', placeholder='Enter password', style={'textAlign': 'center'}),
        html.Button('Submit', id='submit-button', n_clicks=0, style={'display': 'block', 'margin': '10px auto'}),
        html.Div(id='output-message', style={'textAlign': 'center', 'color': 'red'})
    ]),
    html.Div(id='dashboard-content', style={'display': 'none'}, children=[
        # Dashboard content here
        html.Div(children=[
            html.H1(children='Cluster Analysis Dashboard', style={'textAlign': 'center', 'color': '#003366'}),
            html.Div(children='''
                This dashboard shows the Elbow Method and Cluster Scatter Matrix.
            ''', style={'textAlign': 'center', 'color': '#003366'}),

            # Dropdown for selecting cluster
            html.Div([
                html.Label('Select Cluster:', style={'color': '#003366'}),
                dcc.Dropdown(
                    id='cluster-dropdown',
                    options=[{'label': str(cluster), 'value': cluster} for cluster in sorted(rfm['Cluster'].unique())],
                    value=None,
                    multi=True,
                    placeholder="Select clusters to filter..."
                ),
            ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            # Container for the graphs
            html.Div(
                children=[
                    html.Div(children=[dcc.Graph(id='elbow-graph', figure=fig_elbow)], style={'width': '50%', 'display': 'inline-block'}),
                    html.Div(children=[dcc.Graph(id='scatter-graph', figure=fig_scatter)], style={'width': '50%', 'display': 'inline-block'}),
                ],
                style={'display': 'flex', 'flex-wrap': 'wrap'}
            ),

            # Container for the bar graph, scatter plot, and table
            html.Div(
                children=[
                    html.Div(children=[dcc.Graph(id='bar-graph', figure=fig_bar)], style={'width': '50%', 'display': 'inline-block'}),
                    html.Div(children=[
                        dcc.Graph(id='monetary-frequency-scatter', figure=fig_monetary_vs_frequency)
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    html.Div(children=[
                        dash_table.DataTable(
                            id='rfm-table',
                            columns=[{"name": i, "id": i} for i in rfm.columns],
                            data=rfm.to_dict('records'),
                            page_size=10,
                            style_table={'overflowX': 'auto'},
                            style_cell={'textAlign': 'left', 'padding': '5px'},
                            style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'}
                        )
                    ], style={'width': '100%', 'display': 'inline-block', 'verticalAlign': 'top'})
                ],
                style={'display': 'flex', 'flex-wrap': 'wrap'}
            )
        ])
    ])
])

# Callback to verify the password and show/hide the dashboard content
@app.callback(
    [Output('dashboard-content', 'style'),
     Output('password-screen', 'style'),
     Output('output-message', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('password-input', 'value')]
)
def verify_password(n_clicks, password_input):
    if n_clicks > 0:
        if password_input == 'mca13':
            return {'display': 'block'}, {'display': 'none'}, ''
        else:
            return {'display': 'none'}, {'display': 'block'}, 'Incorrect password, please try again.'
    return {'display': 'none'}, {'display': 'block'}, ''


if __name__ == '__main__':
    app.run_server(debug=True)
