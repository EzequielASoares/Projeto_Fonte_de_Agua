#include <WiFi.h>
#include <HTTPClient.h>

const int PIR_PIN    = 14;
const int OUTPUT_PIN = 25;
const int BUTTON_PIN = 12;

String url_destino = "https://forty-bags-prove.loca.lt/";

// ── Estado ────────────────────────────────────────────────────────
bool sessaoAtiva       = false;
unsigned long inicioSessao = 0;

bool botaoAnterior     = false;
bool modoContinuo      = false;
unsigned long inicioModoContinuo = 0;

// ── WiFi ──────────────────────────────────────────────────────────
void conectar_wifi() {
  WiFi.begin("Wokwi-GUEST", "", 6);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("Conectando...");
    delay(500);
  }
  Serial.println("Conectado!");
}

// ── Envia registro: data/hora, modo, tempo ────────────────────────
void enviarDados(bool modoEconomia, unsigned long tempoSegundos) {
  if (WiFi.status() != WL_CONNECTED) return;

  // Monta payload: "modo_economia,tempo_segundos"
  // Ex: "true,45"  ou  "false,12"
  String payload = String(modoEconomia ? "true" : "false")
                   + "," + String(tempoSegundos);

  HTTPClient http;
  http.begin(url_destino);
  http.addHeader("Content-Type", "text/plain");

  int code = http.POST(payload);
  Serial.printf("[HTTP] Enviado: %s | Resposta: %d\n",
                payload.c_str(), code);
  http.end();
}

// ── Inicia sessão (liga saída) ────────────────────────────────────
void iniciarSessao() {
  if (sessaoAtiva) return;
  sessaoAtiva  = true;
  inicioSessao = millis();
  digitalWrite(OUTPUT_PIN, HIGH);
  Serial.println("[Sistema] Saida LIGADA.");
}

// ── Encerra sessão (desliga saída e envia dados) ──────────────────
void encerrarSessao(bool modoEconomia) {
  if (!sessaoAtiva) return;
  sessaoAtiva = false;
  digitalWrite(OUTPUT_PIN, LOW);

  unsigned long tempo = (millis() - inicioSessao) / 1000;
  if (tempo == 0) tempo = 1;

  Serial.printf("[Sistema] Saida DESLIGADA. Duracao: %lus\n", tempo);
  enviarDados(modoEconomia, tempo);
}

void setup() {
  Serial.begin(115200);

  pinMode(PIR_PIN,    INPUT);
  pinMode(BUTTON_PIN, INPUT);
  pinMode(OUTPUT_PIN, OUTPUT);

  conectar_wifi();
}

void loop() {
  bool botaoAtual = (digitalRead(BUTTON_PIN) == HIGH);
  bool pir        = (digitalRead(PIR_PIN)    == HIGH);

  // ── Lógica do botão (hold = modo contínuo) ──────────────────────
  if (botaoAtual && !botaoAnterior) {
    // Pressionou → ativa modo contínuo
    modoContinuo = true;
    Serial.println("[Botao] Modo Continuo ATIVADO.");

    // Se havia sessão PIR em andamento, encerra ela primeiro
    if (sessaoAtiva) encerrarSessao(true);

    inicioModoContinuo = millis();
    iniciarSessao();
  }

  if (!botaoAtual && botaoAnterior) {
    // Soltou → desativa modo contínuo
    modoContinuo = false;
    Serial.println("[Botao] Modo Continuo DESATIVADO.");

    unsigned long tempo = (millis() - inicioModoContinuo) / 1000;
    if (tempo == 0) tempo = 1;

    sessaoAtiva = true;          // garante que encerrarSessao vai rodar
    inicioSessao = inicioModoContinuo;
    encerrarSessao(false);       // false = não era modo economia
  }

  botaoAnterior = botaoAtual;

  // ── Lógica do PIR (só age se não estiver no modo contínuo) ───────
  if (!modoContinuo) {
    if (pir && !sessaoAtiva) {
      Serial.println("[PIR] Movimento detectado!");
      iniciarSessao();
    }

    if (!pir && sessaoAtiva) {
      encerrarSessao(true);      // true = era modo economia
    }
  }

  delay(10);
}
