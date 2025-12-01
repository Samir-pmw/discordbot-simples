import logging
import os
from pathlib import Path
from typing import Optional

import discord
import asyncio
import requests
import random
import google.generativeai as genai
from constants import PERSONALIDADE_LAIN

# Nome exibido em pastas/arquivos locais
APP_NAME = "LainBot"


def _normalize_model_name(raw_name: Optional[str]) -> str:
    default = "gemini-2.5-flash-lite"
    if not raw_name:
        return default
    cleaned = raw_name.strip()
    if not cleaned:
        return default
    if not cleaned.startswith("models/"):
        cleaned = f"models/{cleaned}"
    return cleaned


GEMINI_MODEL_NAME = _normalize_model_name(os.getenv("GEMINI_MODEL"))


def _safe_float(env_name: str, default: float) -> float:
    raw = os.getenv(env_name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        logging.warning(f"Valor inválido para {env_name}={raw}, usando {default}.")
        return default


def _safe_int(env_name: str, default: int, min_value: int, max_value: int) -> int:
    raw = os.getenv(env_name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        logging.warning(f"Valor inválido para {env_name}={raw}, usando {default}.")
        return default
    return max(min_value, min(max_value, value))


def _load_generation_config() -> dict:
    """Carrega configuração de geração do Gemini com overrides via .env."""
    return {
        "temperature": _safe_float("GEMINI_TEMPERATURE", 0.6),
        "top_p": _safe_float("GEMINI_TOP_P", 0.9),
        "top_k": _safe_int("GEMINI_TOP_K", 40, 1, 128),
        "max_output_tokens": _safe_int("GEMINI_MAX_OUTPUT_TOKENS", 150, 32, 2048),
    }


GENERATION_CONFIG = _load_generation_config()


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
        'client_key': "lain_iwakura_bot",  # Identificação no Tenor
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

def _extrair_texto_gemini(resposta) -> str:
    """Concatena os trechos de texto das candidates válidas do Gemini."""
    partes: list[str] = []
    finish_reasons: list[str] = []
    for candidate in getattr(resposta, "candidates", []) or []:
        finish_reason = getattr(candidate, "finish_reason", None)
        reason_val = getattr(finish_reason, "name", finish_reason)
        reason_text = str(reason_val or "").upper()
        finish_reasons.append(reason_text or "DESCONHECIDO")
        if reason_text == "SAFETY" or reason_text.endswith("_SAFETY"):
            # Pulamos candidatos bloqueados por segurança mas registramos no log.
            registrar_log(
                "Candidate do Gemini bloqueado por segurança; tentando próximo.",
                "warning",
            )
            continue
        content = getattr(candidate, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []) or []:
            texto = None
            if isinstance(part, dict):
                texto = part.get("text")
            else:
                texto = getattr(part, "text", None)
            if texto:
                partes.append(texto)
        if partes:
            break
    if not partes and finish_reasons:
        registrar_log(
            f"Nenhum texto extraído dos candidates. finish_reasons={finish_reasons}",
            "warning",
        )
    return "\n".join(partes).strip()


def obter_resposta(entrada: str, gemini_token: str):
    """Obtém uma resposta do Gemini usando a persona contemplativa da Lain."""
    if not gemini_token:
        registrar_log("Token do Gemini não configurado.", 'error')
        return random.choice([
            "tô meio cansada agora... posso falar depois?",
            "mto sono, desculpa ai..",
        ])

    try:
        genai.configure(api_key=gemini_token)
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL_NAME,
            system_instruction=PERSONALIDADE_LAIN,
        )
        resposta = model.generate_content(
            [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": entrada.strip(),
                        }
                    ],
                }
            ],
            generation_config=GENERATION_CONFIG,
        )

        feedback = getattr(resposta, "prompt_feedback", None)
        if feedback and getattr(feedback, "block_reason", None):
            registrar_log(
                f"Gemini bloqueou a resposta: {feedback.block_reason}",
                'warning',
            )
            if getattr(feedback, "safety_ratings", None):
                registrar_log(
                    f"Safety ratings: {feedback.safety_ratings}",
                    'warning',
                )

        texto = _extrair_texto_gemini(resposta)
        if texto:
            return texto

        registrar_log("Resposta vazia recebida do Gemini.", 'warning')
    except Exception as e:
        registrar_log(f"Erro ao contatar Gemini: {e}", 'error')

    return random.choice([
        "o sinal tá fraco e eu tô com sono... tenta de novo.",
        "acho que exagerei no café... preciso respirar antes de responder.",
        "minha cabeça tá pesada agora. repete mais tarde, por favor.",
    ])