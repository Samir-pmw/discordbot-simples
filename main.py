import discord
import os
import asyncio
import logging
from discord.ext import commands
from dotenv import load_dotenv

from utils import (
    LOG_FILE_PATH,
    ensure_appdata_dirs,
    APPDATA_BASE,
    get_appdata_locations,
)

# --- Configuração Inicial ---
# Carrega variáveis de ambiente do .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
TENOR_TOKEN = os.getenv('TENOR_TOKEN')
# Carrega as credenciais do Spotify do .env
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Configura o logging
logging.basicConfig(
    filename=str(LOG_FILE_PATH),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

dirs = ensure_appdata_dirs()
logging.info("Diretórios de dados inicializados: %s", {name: str(path) for name, path in dirs.items()})
locations = get_appdata_locations()
print(f"AppData do bot configurado em: {APPDATA_BASE}")
if locations["is_virtualized"]:
    print(
        "Aviso: este ambiente está virtualizando o AppData. Dados reais em: "
        f"{locations['resolved']}"
    )
    logging.warning(
        "Ambiente virtualizado detectado. O AppData real fica em %s",
        locations["resolved"],
    )

# Define as intenções (Intents)
intents = discord.Intents.default()
intents.message_content = True

# --- Classe do Bot customizada ---
# Usamos commands.Bot para facilitar o uso de Cogs
# Também armazenamos as chaves de API aqui para que os Cogs possam acessá-las
class PeniBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Armazena tokens e configurações na instância do bot
        # Os Cogs podem acessar isso via self.bot.config
        self.config = {
            'openai_token': OPENAI_TOKEN,
            'tenor_token': TENOR_TOKEN,
            'spotify_id': SPOTIFY_CLIENT_ID,
            'spotify_secret': SPOTIFY_CLIENT_SECRET
        }
        # Flag para garantir que os comandos só sejam sincronizados uma vez
        self.synced = False

# Cria a instância do bot
# O prefixo de comando é necessário, mas não será usado para slash commands
bot = PeniBot(command_prefix="!", intents=intents)

# Lista de Cogs (módulos) para carregar
# A sintaxe 'cogs.nome' assume que eles estão na pasta 'cogs/'
cogs_list = [
    'cogs.core',
    'cogs.chat',
    'cogs.rpg',
    'cogs.moderation',
    'cogs.fun',
    'cogs.music'
]

# --- Função Principal (Main) ---
async def main():
    async with bot:
        # Carrega todos os Cogs da lista
        for cog in cogs_list:
            try:
                await bot.load_extension(cog)
                print(f"Cog '{cog}' carregado com sucesso.")
            except Exception as e:
                print(f"Falha ao carregar o cog '{cog}': {e}")
                logging.error(f"Falha ao carregar o cog '{cog}': {e}")
        
        # Inicia o bot
        await bot.start(TOKEN)

# Ponto de entrada do script
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot desligado.")