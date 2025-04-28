import websocket
import json
import telegram
import threading
import time

# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = '7714700345:AAGdioVJEBbTVv8RjBNAjUtgBczjxc89sC0'  # <-- Coloque seu token do Bot aqui
CHAT_ID = '1002988216'       # <-- Coloque seu Chat ID aqui
URL_WS = 'wss://squid-app-67gkfodnqidtlacean.app/ws'

# Inicializa o bot do Telegram
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Histórico dos últimos números
historico = []

# Função para saber a dúzia de um número
def get_duzia(numero):
    if 1 <= numero <= 12:
        return 1
    elif 13 <= numero <= 24:
        return 2
    elif 25 <= numero <= 36:
        return 3
    else:
        return None

# Função para analisar e enviar alerta
def analisar_e_alertar():
    if len(historico) < 2:
        return

    alertar = False

    # Verifica se dois últimos números foram da mesma dúzia
    if get_duzia(historico[-1]) == get_duzia(historico[-2]):
        alertar = True

    # Calcula a dúzia mais frequente
    contagem_duzias = [0, 0, 0]
    for numero in historico:
        duzia = get_duzia(numero)
        if duzia:
            contagem_duzias[duzia - 1] += 1

    duzia_mais_frequente = contagem_duzias.index(max(contagem_duzias)) + 1

    # Monta a mensagem
    ultimos_numeros = ' ➔ '.join(map(str, historico[-5:]))
    mensagem = f"""
⚠️ ENTRADA CONFIRMADA ⚠️

🌀 Roleta: EVOLUTION LIVE
🏑 Sinal: {duzia_mais_frequente}ª Dúzia com tendência!

📋 Últimos resultados:
{ultimos_numeros}

{'⚡ Dois números seguidos na mesma dúzia! Aproveite!' if alertar else ''}

💬 Clique aqui para abrir a roleta (link em breve!)
🏆 Gestão de banca sempre!
"""

    bot.send_message(chat_id=CHAT_ID, text=mensagem)

# Função chamada toda vez que chegar mensagem do WebSocket
def on_message(ws, message):
    try:
        data = json.loads(message)

        if data.get('type') == 'LiveGame' and data.get('event') == 'liveGameFullData':
            resultados = data['data'].get('result', [])
            if resultados:
                for numero in resultados:
                    historico.append(numero)
                    if len(historico) > 50:
                        historico.pop(0)
                print(f"Números capturados: {resultados}")
                analisar_e_alertar()
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

# Função chamada se der erro no WebSocket
def on_error(ws, error):
    print(f"Erro no WebSocket: {error}")

# Função chamada se o WebSocket fechar
def on_close(ws, close_status_code, close_msg):
    print("Conexão WebSocket fechada. Tentando reconectar...")
    time.sleep(5)
    iniciar_websocket()

# Função chamada quando o WebSocket abrir
def on_open(ws):
    print("Conectado no WebSocket!")

# Função para iniciar a conexão WebSocket
def iniciar_websocket():
    ws = websocket.WebSocketApp(
        URL_WS,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()

# === MAIN ===
if __name__ == "__main__":
    print("Iniciando bot...")
    iniciar_websocket()
    while True:
        time.sleep(1)  # Mantém o bot rodando
