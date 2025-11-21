import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import re

# Load DataFrame
df = pd.read_csv('stm_topic.csv')
all_topics = sorted(df['topic_name'].unique())
min_year, max_year = df['year'].min(), df['year'].max()

app = Dash(__name__, server=False, url_base_pathname='/dash/')
app.title = "TED Topic Explorer"

# Add underline style for all anchor tags
download_link_style = {'color': '#bbbbbb', 'textDecoration': 'underline'}
speaker_link_style = {'color': '#cda4f7', 'textDecoration': 'underline'}

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>TED Topic Explorer</title>
        {%favicon%}
        {%css%}
        <style>
            .speaker-link {
                color: #cda4f7;               
                text-decoration: none;
            }
            .speaker-link:hover {
                color: #7c4dff;           
                text-decoration: underline;
            }
            .download-link {
                color: #bbbbbb;
                text-decoration: none;
            }
            .download-link:hover {
                color: #888888;
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    html.H1("🎤 TED Talk Topic Explorer", style={'textAlign': 'center', 'color': '#ffffff', 'marginTop': '20px'}),

    html.Div([
        html.Label("📅 Year Range", style={'color': '#ffffff'}),
        dcc.RangeSlider(
            min=min_year,
            max=max_year,
            value=[min_year, max_year],
            marks={i: str(i) for i in range(min_year, max_year+1, 2)},
            id='year-slider'
        )
    ], style={'width': '80%', 'display': 'inline-block', 'padding': '20px'}),

    html.Div([
        dcc.Graph(id='trend-graph')
    ]),

    html.Div([
        html.Div([
            html.Label("🧠 Select Topic", style={'color': '#ffffff'}),
            dcc.Dropdown(
                options=[{'label': t, 'value': t} for t in all_topics],
                value=all_topics[0],
                id='topic-dropdown'
            )
        ], style={'marginBottom': '20px'}),

        html.H3("🔠 Keyword Word Cloud", style={'textAlign': 'center', 'color': '#ffffff'}),

        html.Img(
            id='wordcloud',
            style={
                'height': '600px',
                'width': '800px',
                'display': 'block',
                'margin': '0 auto'
            }
        )

    ], style={
        'marginTop': '30px',
        'backgroundColor': '#2a2a40',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0px 0px 10px rgba(255, 255, 255, 0.1)'
    }),

    html.Div(id='sample-texts', style={'padding': '30px', 'color': '#ffffff'})
], style={
    'backgroundColor': '#1e1e2f',
    'minHeight': '100vh',
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
})

@app.callback(
    Output('trend-graph', 'figure'),
    Input('year-slider', 'value'),
)
def update_trend(year_range):
    filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    trend = filtered.groupby(['year', 'topic_name']).size().reset_index(name='count')
    fig = px.line(
        trend,
        x="year", y="count", color="topic_name", markers=True,
        title="📈 Topic Trend Over Time"
    )
    fig.update_layout(xaxis=dict(dtick=1), xaxis_tickangle=-45)
    return fig

@app.callback(
    Output('wordcloud', 'src'),
    Input('topic-dropdown', 'value')
)
def update_wordcloud(topic_name):
    import ast
    keywords_list = df[df['topic_name'] == topic_name]['keywords'].tolist()
    keywords_flat = []
    for kw in keywords_list:
        try:
            kws = ast.literal_eval(kw)
            keywords_flat.extend(kws)
        except:
            continue
    freq = pd.Series(keywords_flat).value_counts().to_dict()

    wordcloud = WordCloud(width=800, height=600, background_color='white', max_words=200).generate_from_frequencies(freq)

    buf = BytesIO()
    plt.figure(figsize=(10, 8), dpi=300)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()

    encoded = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"

@app.callback(
    Output('sample-texts', 'children'),
    Input('topic-dropdown', 'value')
)
def show_samples(topic_name):
    import re
    def camel_to_snake(name):
        parts = re.findall(r'[A-Z][a-z]*', name)
        return '_'.join(p.lower() for p in parts)

    samples = df[df['topic_name'] == topic_name].sample(3, random_state=1)
    children = []
    for _, row in samples.iterrows():
        snippet = row['text'][:300].replace('\n', ' ') + "..."
        clean_snippet = row['clean_text'][:300].replace('\n', ' ') + "..."
        base_name = row['file_name'].split('_')[0]
        speaker_url = f"https://www.ted.com/speakers/{camel_to_snake(base_name)}"
        children.append(html.Div([
            html.H4([
                "🎙️ ",
                # html.A(f"{row['file_name']} ({row['year']})", href=speaker_url, target="_blank")
                html.A(f"{row['file_name']} ({row['year']})", href=speaker_url, target="_blank", className="speaker-link")
            ]),
            html.P(snippet),
            html.P(f"🔑 Keywords: {', '.join(eval(row['keywords']))}", style={'color': 'gray'}),
            html.P("🧹 Cleaned Text:", style={'fontWeight': 'bold', 'marginTop': '10px', 'color': '#FFD700'}),
            html.P(clean_snippet, style={'fontStyle': 'italic', 'color': '#DDDDDD'}),
            # html.A("📎 Download STM", href=f"/static/stm/{row['file_name']}", target="_blank")
            html.A("📎 Download STM", href=f"/static/stm/{row['file_name']}", target="_blank", className="download-link")
        ], style={'marginBottom': '30px'}))
    return children
