# 🐾 Servidor Alimentador Automático para Pets

Servidor backend e painel de controle (dashboard) desenvolvido em Flask para monitorar e registrar a atividade de um alimentador automático para pets baseado em ESP32. O sistema suporta comunicação via JSON e atualizações em tempo real (WebSockets).

## 🚀 Como Rodar o Servidor

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Inicie o servidor:**
   ```bash
   python app.py
   ```

3. **Acesse o painel web:**
   Abra o navegador em `http://localhost:5020` (ou no IP da sua máquina). O painel é atualizado instantaneamente quando novos dados chegam.

## 🔌 Conectando o ESP32

Para que o seu ESP32 envie dados para este painel, altere a variável da URL no código do Arduino para apontar para este servidor.

Exemplo de configuração no C++ (substitua pelo IP correto da máquina que roda o Flask):
```cpp
String serverURL = "http://192.168.1.50:5020/api/dados";
```

### Formato do Payload (JSON)
O ESP32 deve enviar uma requisição `POST` contendo um JSON com a seguinte estrutura:
```json
{
  "modo_economia": true,
  "tempo_total": 45
}
```

## 🛠️ Tecnologias
- **Flask:** API e roteamento.
- **SQLite:** Banco de dados local (`dados.db`).
- **Flask-SocketIO:** Atualizações bidirecionais em tempo real (WebSockets).
- **Bootstrap 5:** Estilização do dashboard (Frontend).

---
🔗 **Link do Projeto no Wokwi (Simulação Antiga):** [Acessar Simulação](https://wokwi.com/projects/464292992764214273)
