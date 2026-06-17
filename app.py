from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3
import pytz
from flask_socketio import SocketIO
from contextlib import closing
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
DB = 'dados.db'

def init_db():
    with closing(sqlite3.connect(DB, timeout=10)) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS registros (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora    TEXT,
            modo_economia TEXT,
            tempo_ligado  INTEGER
        )''')

init_db()

@app.route('/', methods=['GET'])
def index():
    with closing(sqlite3.connect(DB, timeout=10)) as con:
        con.row_factory = sqlite3.Row
        historico = con.execute(
            'SELECT * FROM registros ORDER BY id DESC LIMIT 50'
        ).fetchall()
    return render_template('index.html', historico=historico)


@app.route('/api/dados', methods=['POST'])
def receber_sinal():
    try:
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "JSON inválido ou ausente"}), 400

        modo_sinal = dados.get('modo_economia')
        tempo_total = dados.get('tempo_total', 0)

        if modo_sinal is True or modo_sinal == 'true' or modo_sinal == '1':
            modo_economia = "TRUE"
        elif modo_sinal is False or modo_sinal == 'false' or modo_sinal == '0':
            modo_economia = "FALSE"
        else:
            return jsonify({"erro": f"Valor de modo inválido: '{modo_sinal}'"}), 400
        
        fuso_sp = pytz.timezone('America/Sao_Paulo')
        agora = datetime.now(fuso_sp).strftime('%d/%m/%Y %H:%M:%S')

        with closing(sqlite3.connect(DB, timeout=10)) as con:
            cursor = con.execute(
                'INSERT INTO registros (data_hora, modo_economia, tempo_ligado) VALUES (?,?,?)',
                (agora, modo_economia, tempo_total)
            )
            novo_id = cursor.lastrowid

        socketio.emit('novo_dado', {
            "id": novo_id,
            "data_hora": agora,
            "modo_economia": modo_economia,
            "tempo_ligado": tempo_total
        })

        print(f"[ESP32] {agora} | Modo Economia: {modo_economia} | Tempo: {tempo_total}s")
        return jsonify({"mensagem": "Dados Processados"}), 200

    except Exception as e:
        print(f"[ERRO] Falha no processamento: {e}")
        return jsonify({"erro": "Erro Interno"}), 500

@app.route('/api/limpar', methods=['POST'])
def limpar_dados():
    try:
        with closing(sqlite3.connect(DB, timeout=10)) as con:
            con.execute('DELETE FROM registros')
        socketio.emit('limpar_tabela')
        return jsonify({"mensagem": "Histórico limpo com sucesso"}), 200
    except Exception as e:
        print(f"[ERRO] Falha ao limpar: {e}")
        return jsonify({"erro": "Erro Interno"}), 500

@app.route('/api/dados/<int:registro_id>', methods=['DELETE'])
def deletar_dado(registro_id):
    try:
        with closing(sqlite3.connect(DB, timeout=10)) as con:
            con.execute('DELETE FROM registros WHERE id = ?', (registro_id,))
        socketio.emit('remover_linha', {"id": registro_id})
        return jsonify({"mensagem": "Registro apagado"}), 200
    except Exception as e:
        print(f"[ERRO] Falha ao deletar {registro_id}: {e}")
        return jsonify({"erro": "Erro Interno"}), 500
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5020))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
