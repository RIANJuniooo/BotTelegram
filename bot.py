import websocket
import json
import telegram
import time

# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = '7714700345:AAGdioVJEBbTVv8RjBNAjUtgBczjxc89sC0'  # Coloque seu token aqui
CHAT_ID = '1002988216'      # Coloque seu chat_id aqui
URL_WS = 'wss://squid-app-67gkf.ondigitalocean.app/ws'  # URL WebSocket detectada

# === INICIALIZA O BOT ===
bot = telegram.Bot(token=TELEGRAM_TOKEN)
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

# Função para enviar mensagem formatada
def enviar_alerta():
    if not historico:
        return

    contagem_duzias = [0, 0, 0]
    for numero in historico:
        duzia = get_duzia(numero)
        if duzia:
            contagem_duzias[duzia - 1] += 1

    duzia_mais_frequente = contagem_duzias.index(max(contagem_duzias)) + 1
    ultimos_numeros = ' ➔ '.join(map(str, historico[-5:]))

    mensagem = f"""
🚨 ENTRADA CONFIRMADA 🚨

🎰 Roleta: EVOLUTION LIVE
🏁 Sinal: {duzia_mais_frequente}ª Dúzia com tendência!

📋 Últimos resultados:
{ultimos_numeros}

⚡ Alerta: Dois últimos números na mesma dúzia!
🔔 Sugestão: Cobrir as outras duas dúzias.

💬 Clique aqui para abrir a roleta (em breve seu link!)
🏆 Gestão de banca sempre!
"""

    bot.send_message(chat_id=CHAT_ID, text=mensagem)

# Função principal de WebSocket
def on_message(ws, message):
    global historico
    try:
        data = json.loads(message)
        if 'event' in data and data['event'] == 'liveGameFullData':
            payload = data.get('data', {})
            if payload.get('type') == 'roulette':
                resultados = payload.get('result', [])
                for item in resultados:
                    numero = item.get('n')
                    if isinstance(numero, int) and numero > 0:
                        historico.append(numero)
                        if len(historico) > 50:
                            historico.pop(0)
                        print(f"Número capturado: {numero}")

                        if len(historico) >= 2:
                            if get_duzia(historico[-1]) == get_duzia(historico[-2]):
                                enviar_alerta()
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")


def on_error(ws, error):
    print(f"Erro no WebSocket: {error}")


def on_close(ws, close_status_code, close_msg):
    print("WebSocket fechado")


def on_open(ws):
    print("Conectado ao WebSocket!")


# === LOOP PRINCIPAL ===
if __name__ == "__main__":
    while True:
        try:
            websocket.enableTrace(False)
            ws = websocket.WebSocketApp(
                URL_WS,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.on_open = on_open
            ws.run_forever()
        except Exception as e:
            print(f"Erro geral: {e}")
            time.sleep(5)  # Espera antes de tentar reconectar
