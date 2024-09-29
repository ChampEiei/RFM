import dash
from dash import dcc, html, dash_table
import plotly.express as px
import pandas as pd

# สมมติว่าคุณมีข้อมูล rfm และ k_range, sse
rfm = pd.read_excel('RFM.xlsx') # ตัวอย่างการอ่านข้อมูลจากไฟล์
# k_range = [1, 2, 3, 4, 5, 6] # ตัวอย่างของ k_range
# sse = [100, 80, 60, 40, 30, 20] # ตัวอย่างของ sse
k_range = range(1, 11)
sse=[428.99999999999994,
 245.30411208806478,
 133.78674291671692,
 107.4648386269977,
 88.31541170025612,
 67.55134545296497,
 48.897540405130165,
 43.52660193638751,
 41.30611529443592,
 28.31420745735582]
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
server=app.server
# Define the layout of the app
app.layout = html.Div(children=[
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
], style={'backgroundColor': '#E6F0FF', 'font-family': 'Arial'})

# Callback to update the table and graphs based on the selected cluster
@app.callback(
    [dash.dependencies.Output('scatter-graph', 'figure'),
     dash.dependencies.Output('bar-graph', 'figure'),
     dash.dependencies.Output('monetary-frequency-scatter', 'figure'),
     dash.dependencies.Output('rfm-table', 'data')],
    [dash.dependencies.Input('cluster-dropdown', 'value')]
)
def update_output(selected_clusters):
    if selected_clusters is None or len(selected_clusters) == 0:
        filtered_rfm = rfm
    else:
        filtered_rfm = rfm[rfm['Cluster'].isin(selected_clusters)]
    
    # Update scatter matrix
    fig_scatter = px.scatter_matrix(filtered_rfm, dimensions=['Recency', 'Frequency', 'Monetary'], color='Cluster', title='Cluster Scatter Matrix')

    # Update scatter plot for Monetary vs Frequency
    fig_monetary_vs_frequency = px.scatter(filtered_rfm, x='Frequency', y='Monetary', color='Cluster', size='Monetary', 
                                           title='Monetary vs Frequency Scatter Plot', size_max=100)

    # Update bar chart
    group = filtered_rfm.groupby(['Cluster'])['Monetary'].sum().reset_index()
    fig_bar = px.bar(group, x='Cluster', y='Monetary', color='Cluster', title='Total Monetary by Cluster')

    # Update table
    table_data = filtered_rfm.to_dict('records')
    
    return fig_scatter, fig_bar, fig_monetary_vs_frequency, table_data



if __name__ == '__main__':
    # Run the Dash app in a separate thread
    threading.Timer(1, open_browser).start()
    app.run_server(debug=True) 
