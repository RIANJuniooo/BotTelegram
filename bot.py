import requests
import time
import telegram
import json
import websocket
from threading import Thread

# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = '7714700345:AAGdioVJEBbTVv8RjBNAjUtgBczjxc89sC0'  # Coloque seu token aqui
CHAT_ID = '1002988216'       # Coloque seu chat_id aqui
WEBSOCKET_URL = 'wss://squid-app-g67gkf.ondigitalocean.app/ws'

# === INICIALIZA O BOT ===
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

# Função para analisar e enviar o alerta
def analisar_e_alertar():
    global historico
    alertar = False

    if len(historico) >= 2:
        if get_duzia(historico[-1]) == get_duzia(historico[-2]):
            alertar = True

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

# Função para tratar mensagens recebidas do WebSocket
def on_message(ws, message):
    try:
        data = json.loads(message)

        if data.get('type') == 'LiveGame' and data.get('event') == 'liveGameFullData':
            result_data = data['data']['result']
            if 'ips' in result_data:
                numeros = [int(n) for n in result_data['ips']]
                print(f"Números capturados: {numeros}")

                for numero in numeros:
                    historico.append(numero)
                    if len(historico) > 50:
                        historico.pop(0)

                analisar_e_alertar()

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

# Função ao abrir a conexão
def on_open(ws):
    print("Conectado no WebSocket!")
    msg = {
        "type": "common",
        "event": "changePage",
        "data": {
            "from": "null",
            "to": "evolution-roleta-ao-vivo"
        }
    }
    ws.send(json.dumps(msg))
    print("Mensagem de entrada enviada para a roleta Evolution!")

# Função principal de WebSocket
def iniciar_websocket():
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_open=on_open,
        on_message=on_message
    )
    ws.run_forever()

# === INICIAR ===
def main():
    print("Bot iniciado...")
    websocket.enableTrace(False)
    t = Thread(target=iniciar_websocket)
    t.start()

if __name__ == "__main__":
    main()
