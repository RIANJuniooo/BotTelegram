import asyncio
import websockets
import json
import telegram

# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = '7714700345:AAGdioVJEBbTVv8RjBNAjUtgBczjxc89sC0'  # Seu token aqui
CHAT_ID = '1002988216'  # Seu chat_id aqui
WS_URL = 'wss://squid-app-67gkf.ondigitalocean.app/ws'  # URL do WebSocket

bot = telegram.Bot(token=TELEGRAM_TOKEN)
historico = []

# === Funções de Análise ===
def get_duzia(numero):
    if 1 <= numero <= 12:
        return 1
    elif 13 <= numero <= 24:
        return 2
    elif 25 <= numero <= 36:
        return 3
    else:
        return None

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
🏑 Sinal: {duzia_mais_frequente}ª Dúzia com tendência!

📋 Últimos resultados:
{ultimos_numeros}

🔦 Alerta: Dois últimos números na mesma dúzia!
🔔 Sugestão: Cobrir as outras duas dúzias.

💬 Clique aqui para abrir a roleta (em breve seu link!)

🏆 Gestão de banca sempre!
"""

    if alertar:
        bot.send_message(chat_id=CHAT_ID, text=mensagem)

# === Conexão WebSocket ===
async def escutar_websocket():
    async with websockets.connect(WS_URL) as websocket:
        print("Conectado ao WebSocket!")
        while True:
            mensagem = await websocket.recv()
            try:
                dados = json.loads(mensagem)
                if isinstance(dados, list):
                    for item in dados:
                        if item.get('type') == 'LiveGame' and item.get('event') == 'liveGameFullData':
                            data = item.get('data', {})
                            game_type = data.get('t')
                            if game_type == 'roulette':
                                resultados = data.get('r', [])
                                numeros = [x.get('n') for x in resultados if 'n' in x]

                                print(f"Números capturados: {numeros}")

                                for numero in numeros:
                                    historico.append(numero)
                                    if len(historico) > 50:
                                        historico.pop(0)
                                analisar_e_alertar()
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")

# === Executa o bot ===
async def main():
    print("Bot iniciado...")
    while True:
        try:
            await escutar_websocket()
        except Exception as e:
            print(f"Erro na conexão WebSocket: {e}")
            await asyncio.sleep(5)  # Espera antes de tentar reconectar

if __name__ == "__main__":
    asyncio.run(main())
