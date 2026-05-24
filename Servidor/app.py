from flask import Flask, render_template, request
from datetime import datetime
import sqlite3



app = Flask(__name__)


DB = 'bomba.db'

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS registros (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora    TEXT,
            modo_economia TEXT,
            tempo_ligado  INTEGER
        )''')

init_db()


historico_dados = []

@app.route('/', methods=['GET'])
def index():
    with sqlite3.connect(DB) as con:
        con.row_factory = sqlite3.Row
        historico = con.execute(
            'SELECT * FROM registros ORDER BY id DESC'
        ).fetchall()
    return render_template('index.html', historico=historico)


@app.route('/', methods=['POST'])
def receber_sinal():
    conteudo = request.data.decode('utf-8').strip()
    agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    try:
        if ',' in conteudo:
            modo_sinal, tempo_sinal = conteudo.split(',', 1)
            tempo_total = int(tempo_sinal)
        else:
            modo_sinal = conteudo
            tempo_total = 0

        # Aceita tanto "true"/"false" (novo) quanto "1"/"0" (legado)
        modo_sinal = modo_sinal.strip().lower()
        if modo_sinal in ("true", "1"):
            modo_economia = "TRUE"
        elif modo_sinal in ("false", "0"):
            modo_economia = "FALSE"
        else:
            raise ValueError(f"Valor de modo inválido: '{modo_sinal}'")
        

        with sqlite3.connect(DB) as con:
            con.execute(
                'INSERT INTO registros (data_hora, modo_economia, tempo_ligado) VALUES (?,?,?)',
                (agora, modo_economia, tempo_total)
            )


        novo_registro = {
            "data_hora": agora,
            "modo_economia": modo_economia,
            "tempo_ligado": tempo_total
        }
        
        historico_dados.insert(0, novo_registro)
        print(f"[WOKWI] {agora} | Modo Economia: {modo_economia} | Tempo: {tempo_total}s")
        return "Dados Processados", 200

    except Exception as e:
        print(f"[ERRO] Payload recebido: '{conteudo}' | Falha: {e}")
        return "Erro Interno", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
