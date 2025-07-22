# 03_grafico.py
import dash 
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Dicionarios com as Informações da Caixa Dropdown
dados_conceitos = {
    'java':{'Variaveis':8, 'Condicionais':10, 'loops':4, 'poo':3, 'funções':4},
    'python':{'Variaveis':9, 'Condicionais':7, 'loops':8, 'poo':7, 'funções':2},
    'sql':{'Variaveis':10, 'Condicionais':9, 'loops':1, 'poo':6, 'funções':8},
    'golang':{'Variaveis':7, 'Condicionais':5, 'loops':3, 'poo':5, 'funções':3},
    'javascript':{'Variaveis':6, 'Condicionais':2, 'loops':4, 'poo':4, 'funções':6}
}


cores_map = dict(
    java='red',
    python='green',
    sql='yellow',
    golang='blue',
    javascript='pink'
)


app = dash.Dash(__name__)

app.layout = html.Div([
    html.H4('Cursos de TI', style={'textAlign':'center'}),
    html.Div(
        dcc.Dropdown(
            id = 'dropdown_linguagens',
            options = [
                {'label':'Java','value':'java'},{'label':'Python','value':'python'},
                {'label':'SQL','value':'sql'},
                {'label':'GoLang','value':'golang'},
                {'label':'JavaScript','value':'javascript'}
            ],
            value=['java'],
            multi=True,
            style={'width':'50%', 'margin':'0 auto'}
        )
    ),
    dcc.Graph(id='grafico_linguagem')
], style={'width':'80%', 'margin': '0 auto'}
)

# Uma função que vai ser chamada atravez do evento
@app.callback(
    Output('grafico_linguagem','figure'),
    [Input('dropdown_linguagens','value')]
)

def scarter_linguagens(linguagens_selecionadas):
    scarter_trace=[]

    for linguagem in linguagens_selecionadas:
        dados_linguagem = dados_conceitos[linguagem]
        for conceito, conhecimento in dados_linguagem.items():
            scarter_trace.append(
                go.Scatter(
                    x=[conceito],
                    y=[conhecimento],
                    mode = 'markers',
                    name=linguagem.title(),
                    marker={'size':15,'color':cores_map[linguagem]},
                    showlegend=False
                )
            )
    scarter_layout = go.Layout(
        title="Meus conhecimento em Linguagens",
        xaxis=dict(title = 'Conceitos', showgrid=False),
        yaxis=dict(title = 'Niveis de Conhecimento', showgrid=False)
    )
    return {'data':scarter_trace, 'layout': scarter_layout}
if __name__ == '__main__':
    app.run(debug=True)