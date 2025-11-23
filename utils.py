import logging
import os
from pathlib import Path

import discord
import asyncio
import requests
import random
import openai
from constants import PERSONALIDADE_PENI

APP_NAME = "PeniBot"


def _resolve_appdata_base() -> Path:
    base = os.getenv("APPDATA") or os.getenv("LOCALAPPDATA")
    if not base:
        base = os.path.join(Path.home(), ".config")
    base_path = Path(base) / APP_NAME
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path


APPDATA_BASE = _resolve_appdata_base()
APPDATA_BASE_RESOLVED = APPDATA_BASE.resolve()
APPDATA_IS_VIRTUALIZED = APPDATA_BASE_RESOLVED != APPDATA_BASE
MUSIC_CACHE_DIR = APPDATA_BASE / "music_cache"
FICHAS_DIR = APPDATA_BASE / "fichas"
INVENTARIOS_DIR = APPDATA_BASE / "inventarios"
LOG_DIR = APPDATA_BASE / "logs"


def ensure_appdata_dirs():
    created = {}
    for directory in (MUSIC_CACHE_DIR, FICHAS_DIR, INVENTARIOS_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        created[directory.name] = directory
    return created


ensure_appdata_dirs()

LOG_FILE_PATH = LOG_DIR / "bot_logs.txt"


def get_appdata_locations():
    return {
        "logical": APPDATA_BASE,
        "resolved": APPDATA_BASE_RESOLVED,
        "is_virtualized": APPDATA_IS_VIRTUALIZED,
    }

def registrar_log(mensagem: str, nivel: str = 'info'):
    """Registra uma mensagem no arquivo de log."""
    if nivel.lower() == 'info':
        logging.info(mensagem)
    elif nivel.lower() == 'warning':
        logging.warning(mensagem)
    elif nivel.lower() == 'error':
        logging.error(mensagem)
    else:
        logging.info(mensagem)  # Padrão para 'info'

async def send_temp_message(channel, content, delete_after=3):
    """Envia uma mensagem temporária em um canal."""
    msg = await channel.send(content)
    await asyncio.sleep(delete_after)
    try:
        await msg.delete()
    except discord.NotFound:
        pass
    except discord.Forbidden:
        pass

async def send_temp_followup(interaction: discord.Interaction, content: str, delete_after: int = 3):
    """Envia um followup de interação temporário."""
    msg = await interaction.followup.send(content, ephemeral=False)
    await asyncio.sleep(delete_after)
    try:
        await msg.delete()
    except discord.NotFound:
        pass
    except discord.Forbidden:
        print("Sem permissão para deletar a mensagem de followup.")

def buscar_gif(TENOR_TOKEN, search_term, limit=5):
    """
    Busca um GIF no Tenor com base no termo de pesquisa e escolhe aleatoriamente.
    """
    if not TENOR_TOKEN:
        registrar_log("Chave de API do Tenor não fornecida.", 'error')
        return None
    
    url = "https://tenor.googleapis.com/v2/search"
    params = {
        'q': search_term,
        'key': TENOR_TOKEN,
        'client_key': "peni_parker_bot",  # Chave de cliente
        'limit': limit,
        'media_filter': 'gif',
        'random': False
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        gifs = response.json()
        
        if 'results' in gifs and gifs['results']:
            top_gifs = gifs['results'][:limit]
            random_gif = random.choice(top_gifs)
            if 'media_formats' in random_gif and 'gif' in random_gif['media_formats']:
                return random_gif['media_formats']['gif']['url']
        return None
    except requests.exceptions.RequestException as e:
        registrar_log(f"Erro ao buscar GIFs: {e}", 'error')
        return None

def obter_resposta(entrada, OPENAI_TOKEN):
    """
    Obtém uma resposta do GPT-3.5-turbo com a personalidade da Peni Parker.
    """
    # Define a chave de API (compatível com a versão antiga do SDK openai)
    openai.api_key = OPENAI_TOKEN
    
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
        registrar_log(f"Erro ao contatar OpenAI: {e}", 'error')
        return random.choice([
            'Estou sem bateria social -.-', 
            'Tô com soninho, me deixa dormir', 
            'Não tô afim de falar com você.', 
            'Me deixa quieta...',
            'Zzzzzzzzzzzzzzzzzzzzzzzzzz'
        ])