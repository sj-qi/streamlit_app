import dash
import pandas as pd
import plotly.express as px
from config import CSV_FILE_PATH
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Load initial data
def load_data():
    file_path = CSV_FILE_PATH
    return pd.read_csv(file_path)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Real-Time Trading Log Monitoring"

# Layout
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '20px'}, children=[
    html.H1("Trading Log Monitoring Dashboard", style={'textAlign': 'center', 'color': '#4CAF50'}),
    
    # Filters Section
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 'paddingBottom': '20px'}, children=[
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label("Filter by Severity"),
            dcc.Dropdown(id='severity-filter', options=[], multi=True, placeholder="Select Severity", style={'width': '100%'})
        ]),
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label("Filter by Host"),
            dcc.Dropdown(id='host-filter', options=[], multi=True, placeholder="Select Host", style={'width': '100%'})
        ]),
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label("Filter by Status"),
            dcc.Dropdown(id='status-filter', options=[], multi=True, placeholder="Select Status", style={'width': '100%'})
        ]),
        html.Div(style={'flex': '1', 'padding': '10px'}, children=[
            html.Label("Filter by Problem"),
            dcc.Dropdown(id='problem-filter', options=[], multi=True, placeholder="Select Problem", style={'width': '100%'})
        ])
    ]),
    
    # Error Table
    html.H3("Recent Issues", style={'paddingTop': '20px'}),
    dash_table.DataTable(
        id='error-table',
        columns=[{"name": col, "id": col} for col in ["problem_time", "severity_name", "hostname", "full_problem_description", "status"]],
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={'padding': '10px', 'textAlign': 'center'},
        style_header={'fontWeight': 'bold', 'backgroundColor': '#f5f5f5'},
    ),
    
    # Severity Breakdown
    html.H3("Severity Breakdown", style={'paddingTop': '30px'}),
    dcc.Graph(id='severity-breakdown', config={'displayModeBar': False}),
    
    # Issue Trend Graph
    html.H3("Issues Over Time (Per Minute)"),
    dcc.Graph(id='issue-trend-graph', config={'displayModeBar': False}),
    
    # Time-to-Resolution Histogram
    html.H3("Time-to-Resolution Histogram (Seconds)"),
    dcc.Graph(id='time-resolution-histogram', config={'displayModeBar': False}),
])

# Callbacks to update data
@app.callback(
    [
        Output('error-table', 'data'),
        Output('issue-trend-graph', 'figure'),
        Output('severity-breakdown', 'figure'),
        Output('time-resolution-histogram', 'figure'),
        Output('severity-filter', 'options'),
        Output('host-filter', 'options'),
        Output('status-filter', 'options'),
        Output('problem-filter', 'options')
    ],
    [
        Input('severity-filter', 'value'),
        Input('host-filter', 'value'),
        Input('status-filter', 'value'),
        Input('problem-filter', 'value')
    ]
)
def update_dashboard(selected_severity, selected_host, selected_status, selected_problem):
    df = load_data()
    
    if selected_severity:
        df = df[df['severity_name'].isin(selected_severity)]
    if selected_host:
        df = df[df['hostname'].isin(selected_host)]
    if selected_status:
        df = df[df['status'].isin(selected_status)]
    if selected_problem:
        df = df[df['full_problem_description'].isin(selected_problem)]
    
    # Table Data
    recent_issues = df.sort_values("problem_time", ascending=False).head(10).to_dict('records')
    
    # Severity Breakdown (Color-coded)
    severity_colors = {
        'Not classified': 'grey',
        'Information': 'blue',
        'Warning': 'orange',
        'Average': 'yellow',
        'High Disaster': 'red'
    }
    
    severity_breakdown_fig = px.pie(df, names="severity_name", title="Severity Distribution", 
                                    color='severity_name', color_discrete_map=severity_colors)

    # Issue Trend (Per Minute)
    df["problem_time"] = pd.to_datetime(df["problem_time"])
    df["minute"] = df["problem_time"].dt.floor('T')  # Round time to the nearest minute
    issue_trend_fig = px.line(df.groupby('minute').size().reset_index(name='count'), x="minute", y="count", 
                              title="Issues by Minute", markers=True)
    
    # Time-to-Resolution Histogram (Seconds)
    df['duration'] = pd.to_timedelta(df['duration']).dt.total_seconds()  # Convert to seconds
    resolution_fig = px.histogram(df, x='duration', title='Time-to-Resolution Histogram (Seconds)', nbins=20, 
                                   color_discrete_sequence=px.colors.qualitative.Plotly)
    
    # Dropdown options
    severity_options = [{'label': sev, 'value': sev} for sev in df['severity_name'].unique()]
    host_options = [{'label': host, 'value': host} for host in df['hostname'].unique()]
    status_options = [{'label': status, 'value': status} for status in df['status'].unique()]
    problem_options = [{'label': prob, 'value': prob} for prob in df['full_problem_description'].unique()]
    
    return recent_issues, issue_trend_fig, severity_breakdown_fig, resolution_fig, severity_options, host_options, status_options, problem_options

# Run app
if __name__ == '__main__':
    app.run_server(debug=False)