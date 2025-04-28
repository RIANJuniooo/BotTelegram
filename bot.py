import requests
import time
import telegram
from bs4 import BeautifulSoup

# === CONFIGURAÇÕES ===
TELEGRAM_TOKEN = '7714700345:AAGdioVJEBbTVv8RjBNAjUtgBczjxc89sC0'  # Coloque seu token aqui
CHAT_ID = '1002988216'       # Coloque seu chat_id aqui
URL_SITE = 'https://gamblingcounting.com/pt-BR/evolution-roleta-ao-vivo'
INTERVALO = 15  # Tempo entre checagens em segundos

# === INICIALIZA O BOT ===
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Histórico dos últimos números
historico = []

# Função para buscar resultados da roleta
def buscar_resultados():
    try:
        response = requests.get(URL_SITE)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        resultados_html = soup.select('.number')
        resultados = [int(r.text.strip()) for r in resultados_html if r.text.strip().isdigit()]
        
        return resultados
    except Exception as e:
        print(f"Erro ao buscar resultados: {e}")
        return []

# Função para saber a dúzia de um número
def get_duzia(numero):
    if 1 <= numero <= 12:
        return 1
    elif 13 <= numero <= 24:
        return 2
    elif 25 <= numero <= 36:
        return 3
    else:
        return None  # 0 ou inválido

# Função para analisar e enviar o alerta
def analisar_e_alertar(novos_numeros):
    global historico
    alertar = False

    # Atualiza histórico com novos números
    for numero in novos_numeros:
        historico.append(numero)
        if len(historico) > 50:
            historico.pop(0)

    # Verifica se os dois últimos números foram da mesma dúzia
    if len(historico) >= 2:
        if get_duzia(historico[-1]) == get_duzia(historico[-2]):
            alertar = True

    # Calcula a dúzia mais frequente
    contagem_duzias = [0, 0, 0]
    for numero in historico:
        duzia = get_duzia(numero)
        if duzia:
            contagem_duzias[duzia - 1] += 1

    duzia_mais_frequente = contagem_duzias.index(max(contagem_duzias)) + 1

    # Últimos 5 números para mostrar
    ultimos_numeros = ' ➔ '.join(map(str, historico[-5:]))

    # Monta a mensagem estilo VIP
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

# === LOOP PRINCIPAL ===
def main():
    print("Bot iniciado...")
    while True:
        novos_numeros = buscar_resultados()
        if novos_numeros:
            analisar_e_alertar(novos_numeros)
        time.sleep(INTERVALO)

if __name__ == "__main__":
    main()
