# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
# FIX: Wrap children in a list []
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        style={'width': '80%', 'padding': '3px', 'color': '#503D36'}
    ),
    html.Br(),

    # TASK 2: Add a container for the Pie Chart
    # FIX: Use html.Div with id 'success-pie-chart' to hold the graph
    html.Div(id='success-pie-chart'),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Add a container for the Scatter Chart
    html.Div(id='success-payload-scatter-chart')
])

# ---------------------------------------------------------
# CALLBACKS (Must be OUTSIDE app.layout)
# ---------------------------------------------------------

# TASK 2: Callback for the Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='children'), # Changed to 'children' to wrap Graph
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        filtered_df = spacex_df
        title_text = 'Total Successful Launches by Site'
        
        # Group by Launch Site and sum the 'class' column
        pie_data = filtered_df.groupby('Launch Site')['class'].sum().reset_index()
        pie_data.columns = ['Launch Site', 'Success Count']
        
        fig = px.pie(
            pie_data, 
            values='Success Count', 
            names='Launch Site', 
            title=title_text
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        title_text = f'Success vs. Failed for {selected_site}'
        
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failed_count = filtered_df[filtered_df['class'] == 0].shape[0]
        
        pie_data = pd.DataFrame({
            'Outcome': ['Success', 'Failed'],
            'Count': [success_count, failed_count]
        })
        
        fig = px.pie(
            pie_data, 
            values='Count', 
            names='Outcome', 
            title=title_text,
            color_discrete_sequence=['#00FF00', '#FF0000']
        )
    
    # Return the Graph component wrapped in the div
    return dcc.Graph(figure=fig)

# TASK 4: Callback for the Scatter Chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='children'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter by Payload Range
    min_val, max_val = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= min_val) & 
        (spacex_df['Payload Mass (kg)'] <= max_val)
    ]
    
    # Filter by Site if not ALL
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Create Scatter Plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='Launch Site', # Or 'class' if you want to see success/fail distribution
        color='class',
        color_discrete_map={0: 'red', 1: 'green'},
        title=f'Payload Mass vs Launch Site (Success: Green, Fail: Red)',
        labels={'class': 'Outcome (1=Success, 0=Fail)'}
    )
    
    return dcc.Graph(figure=fig)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)