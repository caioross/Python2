import config 
import pandas as pd
import sqlite3
import os
from flask import Flask, request, jsonify, render_template_string
import dash
from dash import Dash, html, dcc
import plotly.graph_objs as go
import numpy as np 
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

DB_PATH = config.DB_PATH

# Função para inicializar o banco de dados SQL
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inadimplencia(
                mes TEXT PRIMARY KEY,
                inadimplencia REAL 
                )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS selic (
                mes TEXT PRIMARY KEY,
                selic_diaria REAL
                )
        ''')
        conn.commit()

#EM breve =)
vazio = 0
@app.route('/')
def index():
    return render_template_string('''
        <h1>Upload de dados Economicos</h1>
        <form action='/upload' method='POST' enctype='multipart/form-data'>
            <label for='campo_inadimplencia'>Arquivo de Inadimplencia</label>
            <input name='campo_inadimplencia' type='file' required><br><br>
            
            <label for='campo_selic'>Arquivo Taxa Selic</label>
            <input type='file' name='campo_selic' required><br><br>
            <input type='submit' value='Fazer Upload'>    
        </form>
        <br><br><hr>
        <a href='/consultar'> Consultar Dados <br>
        <a href='/graficos'> Visualizar Graficos <br>
        <a href='/editar_inadimplencia'> Editar dados de Inadimplencia <br>
        <a href='/correlacao'> Analisar a Correlação <br>
    ''')

@app.route('/upload', methods=['POST','GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')
    # verificar se os arquivos de fato foram enviados
    if not inad_file or not selic_file:
        return jsonify({'Erro':'Ambos os arquivos devem ser enviados'})
    
    inad_df = pd.read_csv(
        inad_file,
        sep = ';',
        names=['data','inadimplencia'],
        header = 0
    )

    selic_df = pd.read_csv(
        selic_file,
        sep = ';',
        names = ['data','selic_diaria'],
        header = 0
    )
    # formata o campo de data como datahora padrão
    inad_df['data'] = pd.to_datetime(inad_df['data'], format="%d/%m/%Y")
    selic_df['data'] = pd.to_datetime(selic_df['data'], format="%d/%m/%Y")
    # gera uma coluna nova mes e preenche de acordo com a data
    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)
    #limpa as duplicatas e agrupa conjuntos
    inad_mensal = inad_df[['mes','inadimplencia']].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    # agora com tudo limpo e ordenado vamos armazenar no banco de dados
    with sqlite3.connect(DB_PATH) as conn:
        inad_mensal.to_sql('inadimplencia', conn, if_exists='replace', index=False)
        selic_mensal.to_sql('selic', conn, if_exists='replace', index=False)
    return jsonify({'Mensagem':'Dados inseridos com sucesso!'})

@app.route('/consultar', methods=['POST','GET'])
def consultar():
    # Resultado se a pagina for carregada recebendo POST
    if request.method == 'POST':
        tabela = request.form.get('campo_tabela')
        if tabela not in ['inadimplencia','selic']:
            return jsonify({'Erro':'Tabela é invalida'})
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(f'SELECT * FROM {tabela}', conn)
        return df.to_html(index=False)

    #Resultado sem receber um POST, ou seja, primeiro carregamento da pagina de consulta
    return render_template_string('''
        <h1> Consultar Tabelas </h1>
        <form action='/consultar' method='POST'>
            <label for='campo_tabela'> Escolha a tabela: </label>
            <select name='campo_tabela'>
                <option value='inadimplencia'>Inadimplencia</option>
                <option value='selic'>Selic</option>
            </select>
            <input type="submit" value='Consultar'>
        </form>
        <br>
        <a href='/'>Voltar</a>
    ''')

@app.route('/graficos')
def graficos():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query('SELECT * FROM inadimplencia', conn)
        selic_df = pd.read_sql_query('SELECT * FROM selic', conn)
# Criaremos nosso proimeiro grafico de Inadimplencia
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
            x = inad_df['mes'],
            y = inad_df['inadimplencia'],
            mode = 'lines+markers',
            name = 'Inadimplencia'
        )
    )
# ggplot2, seaborn, simple_white, plotly, plotly_white, presentation, xgridoff, ygridoff, gridon, none, plotly_dark
    fig1.update_layout(
        title = "Evolução da Inadimplencia",
        xaxis_title = "Mês",
        yaxis_title = "%",
        template = "plotly_dark"
    )
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x = selic_df['mes'],
        y = selic_df['selic_diaria'],
        mode = 'lines+markers',
        name = 'Selic'
        )
    )
    fig2.update_layout(
        title = 'Média Mensal da Selic',
        xaxis_title = "Mês",
        yaxis_title = "Taxa",
        template = "plotly_dark"
    )

    graph_html_1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    graph_html_2 = fig2.to_html(full_html=False, include_plotlyjs='cdn')

    return render_template_string('''
        <html>
            <head>
                <title> Graficos Economicos </title>
                <style>
                    .container{
                        display:flex;
                        justify-content:space-around;      
                        }
                    .graph{
                        width: 48%;
                        }
                </style>
                <h1>Graficos Economicos</h1>
                <div class='container'>
                    <div class='graph'>{{ grafico1 | safe }}</div>
                    <div class='graph'>{{ grafico2 | safe }}</div>
                </div>
            </head>
        </html>
    ''', grafico1 = graph_html_1, grafico2 = graph_html_2)

# Rota para editar a tabela de inadimplencia
@app.route('/editar_inadimplencia', methods=['POST','GET'])
def editar_inadimplencia():
    # Bloco que será carregado apenas quando receber o post
    if request.method == 'POST':
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({'Erro':'Valor Invalido'})
        
        # atualizar os dados do banco
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE inadimplencia SET inadimplencia = ? WHERE mes = ?", (novo_valor, mes))
            conn.commit()
        return jsonify({'Mensagem:':f'Dados do mês {mes} atualizados com sucesso'})
        
    # Bloco que será carregado a primeira vez que a pagina abrir (sem receber post)
    return render_template_string('''
        <h1> Editar Inadimplencia</h1>
        <form method="POST" action='/editar_inadimplencia'>
            <label>Mês (AAAA-MM):</label>
            <input type='text' name='campo_mes'><br>   

            <label>Novo valor de Inadimplencia:</label>
            <input type='text' name='campo_valor'><br>

            <input type='submit' value='Atualizar dados'>
        </form>
        <a href='/'>Voltar</a>
    ''')



if __name__ == '__main__' :
    init_db()
    app.run(debug=True)
