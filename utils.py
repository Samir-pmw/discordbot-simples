import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any

import discord
import asyncio
import requests
from bs4 import BeautifulSoup
import random
import google.generativeai as genai
from constants import PERSONALIDADE_LAIN
import re
import time

# Estado de uso por modelo para aplicar cooldown baseado em consumo estimado de tokens
_MODEL_USAGE: dict[str, dict] = {}

# Limites conhecidos por modelo (por minuto/por dia)
MODEL_LIMITS = {
    "models/gemini-2.5-pro": {"tpm_per_min": 125_000, "rpm_per_min": 2, "rpd_per_day": 50},
    "models/gemini-2.5-flash": {"tpm_per_min": 250_000, "rpm_per_min": 10, "rpd_per_day": 250},
    "models/gemini-2.5-flash-lite": {"tpm_per_min": 250_000, "rpm_per_min": 15, "rpd_per_day": 1000},
    "models/gemini-2.0-flash": {"tpm_per_min": 1_000_000, "rpm_per_min": 15, "rpd_per_day": 200},
    "models/gemini-2.0-flash-lite": {"tpm_per_min": 1_000_000, "rpm_per_min": 30, "rpd_per_day": 200},
    "models/gemini-3-pro": {"tpm_per_min": 125_000, "rpm_per_min": 2, "rpd_per_day": 50},  # conservador
}

def _get_model_state(model_name: str) -> dict:
    st = _MODEL_USAGE.get(model_name)
    if not st:
        st = {
            "window_tokens": 0,
            "window_start": time.time(),
            "cooldown_until": 0.0,
        }
        _MODEL_USAGE[model_name] = st
    return st

def _is_on_cooldown(model_name: str) -> bool:
    st = _get_model_state(model_name)
    return time.time() < st.get("cooldown_until", 0.0)

def _note_model_usage(model_name: str, est_tokens: int, window_seconds: int = 300, threshold_tokens: int = 10000, cooldown_seconds: int = 600) -> None:
    """Registra uso estimado de tokens e aplica cooldown se exceder limite.
    - window_seconds: janela de tempo para acumular tokens (default 5 min)
    - threshold_tokens: limite de tokens na janela para aplicar cooldown
    - cooldown_seconds: tempo de cooldown quando limiar é atingido
    """
    now = time.time()
    st = _get_model_state(model_name)
    # Reset janela se passou
    if now - st["window_start"] > window_seconds:
        st["window_start"] = now
        st["window_tokens"] = 0
    st["window_tokens"] += max(0, est_tokens)
    if st["window_tokens"] >= threshold_tokens:
        st["cooldown_until"] = now + cooldown_seconds
        pct = (st["window_tokens"] / threshold_tokens) * 100 if threshold_tokens else 0
        registrar_log(
            f"Cooldown ativado: {model_name} tokens_window={st['window_tokens']} threshold={threshold_tokens} ({pct:.1f}%)", 'warning'
        )
        try:
            print(
                f"[COOLDOWN] {model_name} ativado | usados {st['window_tokens']}/{threshold_tokens} ({pct:.1f}%) | duração {cooldown_seconds}s | janela {window_seconds}s"
            )
        except Exception:
            pass

# Nome exibido em pastas/arquivos locais
APP_NAME = "LainBot"


def _normalize_model_name(raw_name: Optional[str]) -> str:
    default = "gemini-2.5-flash-live"
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
        "max_output_tokens": _safe_int("GEMINI_MAX_OUTPUT_TOKENS", 600, 32, 2048),
    }


GENERATION_CONFIG = _load_generation_config()
# ====== Região op.gg ======
def normalize_opgg_region(region: str) -> str:
    """Normaliza códigos de servidor para slugs de região do op.gg.
    Exemplos: BR1/BR/br1 -> br, NA1/NA -> na, EUW1/EUW -> euw, EUN1/EUNE -> eune,
    KR -> kr, LAN/LA1 -> lan, LAS/LA2 -> las, OCE/OC1 -> oce, JP -> jp, RU -> ru, TR -> tr.
    """
    r = (region or "br").strip().lower()
    mapping = {
        "br": "br", "br1": "br",
        "na": "na", "na1": "na",
        "euw": "euw", "euw1": "euw",
        "eune": "eune", "eun1": "eune",
        "kr": "kr",
        "lan": "lan", "la1": "lan",
        "las": "las", "la2": "las",
        "oce": "oce", "oc1": "oce",
        "jp": "jp",
        "ru": "ru",
        "tr": "tr",
    }
    return mapping.get(r, r)


# ====== OPGG SCRAPER ======
def _http_get(url: str, params: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None, timeout: int = 8) -> Optional[str]:
    try:
        default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        if headers:
            default_headers.update(headers)
        resp = requests.get(url, params=params or {}, headers=default_headers, timeout=timeout)
        # Retornamos None em 404 para o chamador decidir marcar como privado/indisponível
        if resp.status_code == 404:
            registrar_log(f"HTTP 404 em {url}", 'warning')
            return None
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        registrar_log(f"HTTP GET falhou em {url}: {e}", 'warning')
        return None


def _parse_lol_opgg(html: str, summoner_name: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    data: Dict[str, Any] = {"summoner_name": summoner_name}
    # Nome do invocador na página
    page_name = soup.select_one(".summoner-name, .profile__name, h1")
    if page_name:
        txt = page_name.get_text(strip=True)
        if txt:
            data["summoner_name"] = txt
    # Avatar
    avatar = soup.select_one("img.profile-icon, img.summoner-profile-icon, .profile-icon img")
    if avatar and avatar.get("src"):
        data["avatar_url"] = avatar.get("src")
    else:
        # Tenta og:image
        og_img = soup.select_one('meta[property="og:image"]')
        if og_img and og_img.get('content'):
            data["avatar_url"] = og_img.get('content')
    # Rank info
    tier_el = soup.select_one(".tier, .rank, .summary__tier, .tier__rank")
    if tier_el:
        data["rank"] = tier_el.get_text(strip=True)
    # LP
    lp_text_el = soup.find(string=lambda s: isinstance(s, str) and "LP" in s)
    if lp_text_el:
        lp_val = str(lp_text_el).strip()
        # Só adicionar se tiver números (evitar só "LP")
        import re as _re
        if _re.search(r"\d", lp_val):
            data["lp"] = lp_val
    # Winrate via regex
    import re as _re
    win_text = None
    for el in soup.find_all(string=True):
        s = str(el)
        m = _re.search(r"Win\s*Rate\s*[:\-]?\s*(\d{1,3}%)", s, flags=_re.I)
        if m:
            win_text = m.group(1)
            break
        m2 = _re.search(r"\b(\d{1,3}%)\b", s)
        if m2 and "win" in s.lower():
            win_text = m2.group(1)
            break
    if win_text:
        data["winrate"] = win_text
    # Partidas recentes (heurística)
    games = soup.select(".game-item, .match__item, .recent-game-item")
    if games:
        data["matches"] = f"{len(games)} últimas partidas analisadas"
    # Marcar como privado se sinais comuns aparecerem
    private_texts = [
        "summoner is private",
        "profile is private",
        "perfil privado",
        "privado",
        "비공개",
    ]
    page_text = soup.get_text(" ", strip=True).lower()
    if not data.get("rank") and any(t in page_text for t in private_texts):
        data["private"] = True
    return data


def _parse_valorant_opgg(html: str, riot_id: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    data: Dict[str, Any] = {"riot_id": riot_id}
    # Rank/MMR
    rank_el = soup.select_one(".rank, .mmr, .summary__tier")
    mmr_el = soup.find(string=lambda s: isinstance(s, str) and "MMR" in s)
    # KDA com regex para evitar capturar textos genéricos com '/'
    import re as _re
    kda_val = None
    for el in soup.find_all(string=True):
        s = str(el)
        m = _re.search(r"\b\d+(?:\.\d+)?/\d+(?:\.\d+)?/\d+(?:\.\d+)?\b", s)
        if m:
            kda_val = m.group(0)
            break
    winrate_el = soup.find(string=lambda s: isinstance(s, str) and "%" in s and "Win" in s)
    if rank_el:
        data["rank"] = rank_el.get_text(strip=True)
    if mmr_el:
        data["mmr"] = str(mmr_el).strip()
    if kda_val:
        data["kda"] = kda_val
    if winrate_el:
        data["winrate"] = str(winrate_el).strip()
    return data


def obter_opgg_resumo(summoner_name: str, region: str, riot_id: str | None) -> Optional[Dict[str, Any]]:
    """Obtém resumo do op.gg para LoL e (se disponível) Valorant.
    Usa requests + BeautifulSoup (biblioteca confiável e famosa) para parsing básico.
    """
    result: Dict[str, Any] = {}
    # LoL URL (prefixo /lol). Se houver Riot ID (nome#tag), op.gg usa nome-tag.
    opgg_name = summoner_name
    if riot_id and "#" in riot_id:
        game_name, tag = riot_id.split("#", 1)
        opgg_name = f"{game_name}-{tag}"
    lol_url = f"https://www.op.gg/lol/summoners/{region}/{requests.utils.quote(opgg_name)}"
    html = _http_get(lol_url)
    if html:
        lol_data = _parse_lol_opgg(html, opgg_name)
        if lol_data:
            result["lol"] = lol_data
    else:
        # 404 pode ser perfil inexistente, erro temporário ou rate limit; NÃO assumir privado
        result["lol"] = {"summoner_name": summoner_name, "not_found": True}
        registrar_log(f"Falha ao obter página LoL op.gg para {summoner_name}", 'warning')

    # Valorant URL (best effort). op.gg Valorant usa Riot ID nome#tag
    if riot_id and "#" in riot_id:
        game_name, tag = riot_id.split("#", 1)
        val_url = f"https://valorant.op.gg/profile/{requests.utils.quote(game_name)}-{requests.utils.quote(tag)}"
        vhtml = _http_get(val_url)
        if vhtml:
            val_data = _parse_valorant_opgg(vhtml, riot_id)
            if val_data:
                # Se não há campos relevantes, marcar como privado
                has_info = any(val_data.get(k) for k in ("rank", "mmr", "kda", "winrate"))
                if not has_info:
                    val_data["private"] = True
                result["valorant"] = val_data
        else:
            registrar_log(f"Falha ao obter página Valorant op.gg para {riot_id}", 'warning')

    return result if result else None


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
    """Registra em logging e imprime com prefixo de nível."""
    lvl = (nivel or 'info').lower()
    prefix = {'info': '[INFO]', 'warning': '[WARN]', 'error': '[ERROR]'}.get(lvl, '[INFO]')
    try:
        print(f"{prefix} {mensagem}")
    except Exception:
        # Em ambientes sem stdout, ignore o print
        pass
    if lvl == 'info':
        logging.info(mensagem)
    elif lvl == 'warning':
        logging.warning(mensagem)
    elif lvl == 'error':
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

def _extrair_texto_gemini(resposta, model_name: str = None) -> tuple[str, bool]:
    """Concatena os trechos de texto das candidates válidas do Gemini.
    Retorna (texto, deve_cooldown) onde deve_cooldown indica se houve MAX_TOKENS ou SAFETY."""
    partes: list[str] = []
    finish_reasons: list[str] = []
    deve_cooldown = False
    
    for candidate in getattr(resposta, "candidates", []) or []:
        finish_reason = getattr(candidate, "finish_reason", None)
        reason_val = getattr(finish_reason, "name", finish_reason)
        reason_text = str(reason_val or "").upper()
        finish_reasons.append(reason_text or "DESCONHECIDO")
        
        # MAX_TOKENS indica que o modelo está sobrecarregado ou precisa cooldown
        if reason_text == "MAX_TOKENS":
            deve_cooldown = True
            registrar_log(
                f"MAX_TOKENS detectado em {model_name or 'modelo'} - ativando cooldown",
                "warning",
            )
        
        if reason_text == "SAFETY" or reason_text.endswith("_SAFETY"):
            # Pulamos candidatos bloqueados por segurança mas registramos no log.
            deve_cooldown = True
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
    return "\n".join(partes).strip(), deve_cooldown


def _tentar_gerar_resposta(entrada: str, gemini_token: str, model_name: str) -> Optional[str]:
    """
    Tenta gerar uma resposta usando um modelo específico do Gemini.
    Retorna o texto da resposta ou None se falhar.
    """
    # Verifica cooldown do modelo
    if _is_on_cooldown(model_name):
        st = _get_model_state(model_name)
        remaining = max(0, int(st.get("cooldown_until", 0) - time.time()))
        registrar_log(
            f"Pulando {model_name}: cooldown ativo ({remaining}s restantes, tokens_window={st.get('window_tokens', 0)})",
            'warning'
        )
        try:
            print(
                f"[SKIP-COOLDOWN] {model_name} restante={remaining}s | tokens_window={st.get('window_tokens', 0)}"
            )
        except Exception:
            pass
        return None
    try:
        genai.configure(api_key=gemini_token)
        model = genai.GenerativeModel(
            model_name=model_name,
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
                f"Gemini ({model_name}) bloqueou a resposta: {feedback.block_reason}",
                'warning',
            )
            if getattr(feedback, "safety_ratings", None):
                registrar_log(
                    f"Safety ratings: {feedback.safety_ratings}",
                    'warning',
                )
            # Ativar cooldown em bloqueios de segurança
            limits = MODEL_LIMITS.get(model_name)
            if limits:
                threshold = int(0.7 * limits.get("tpm_per_min", 100000))
                # Força cooldown com tokens estimados altos
                _note_model_usage(model_name, threshold, window_seconds=60, threshold_tokens=threshold, cooldown_seconds=180)
            return None

        texto, deve_cooldown = _extrair_texto_gemini(resposta, model_name)
        
        # Estimar tokens usados: prompt + resposta em caracteres ~ tokens
        est_tokens = int((len(entrada) + len(texto if texto else entrada)) * 0.25)
        
        # Se MAX_TOKENS ou SAFETY, aplicar cooldown mais longo
        limits = MODEL_LIMITS.get(model_name)
        if limits:
            threshold = int(0.7 * limits.get("tpm_per_min", 100000))
            if deve_cooldown:
                # Cooldown de 5 minutos para MAX_TOKENS/SAFETY
                _note_model_usage(model_name, threshold, window_seconds=60, threshold_tokens=threshold, cooldown_seconds=300)
                registrar_log(f"Cooldown de 5min aplicado a {model_name} devido a MAX_TOKENS/SAFETY", 'warning')
            else:
                # Cooldown normal de 30s
                _note_model_usage(model_name, est_tokens, window_seconds=60, threshold_tokens=threshold, cooldown_seconds=30)
        else:
            _note_model_usage(model_name, est_tokens)
        
        if texto:
            return texto

        registrar_log(f"Resposta vazia recebida do Gemini ({model_name}).", 'warning')
        return None
        
    except Exception as e:
        erro_str = str(e)
        registrar_log(f"Erro ao contatar Gemini ({model_name}): {erro_str}", 'warning')
        
        # Ativar cooldown em erros de quota (429) ou rate limit (503)
        if "429" in erro_str or "quota" in erro_str.lower() or "503" in erro_str:
            limits = MODEL_LIMITS.get(model_name)
            if limits:
                threshold = int(0.7 * limits.get("tpm_per_min", 100000))
                # Cooldown de 10 minutos para quota excedida
                _note_model_usage(model_name, threshold, window_seconds=60, threshold_tokens=threshold, cooldown_seconds=600)
                registrar_log(f"Cooldown de 10min aplicado a {model_name} devido a quota/rate limit", 'error')
        return None


def obter_resposta(entrada: str, gemini_token: str):
    """
    Obtém uma resposta do Gemini usando a persona contemplativa da Lain.
    Sistema de fallback: tenta múltiplos modelos em ordem de prioridade até conseguir resposta.
    """
    if not gemini_token:
        registrar_log("Token do Gemini não configurado.", 'error')
        return random.choice([
            "tô meio cansada agora... posso falar depois?",
            "mto sono, desculpa ai..",
        ])

    # Lista de modelos para tentar em ordem de prioridade (melhor para pior)
    modelos = [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",           # Rápido e eficiente
        "models/gemini-2.5-flash-lite",       # Versão lite da 2.5
        "models/gemini-2.0-flash",            # 2.0 estável
        "models/gemini-2.0-flash-lite",       # 2.0 lite
    ]
    
    for i, modelo in enumerate(modelos):
        if i == 0:
            registrar_log(f"Tentando gerar resposta com modelo primário: {modelo}", 'info')
        else:
            registrar_log(f"Tentando modelo fallback #{i}: {modelo}", 'info')
            
        texto = _tentar_gerar_resposta(entrada, gemini_token, modelo)
        
        if texto:
            if i > 0:
                registrar_log(f"✓ Resposta gerada com sucesso usando fallback: {modelo}", 'info')
            else:
                registrar_log(f"✓ Resposta gerada com modelo primário", 'info')
            return texto
        
        if i < len(modelos) - 1:
            registrar_log(f"✗ Falha com {modelo}, tentando próximo...", 'warning')

    # Se todos os modelos falharam
    registrar_log("✗ CRÍTICO: Todos os modelos Gemini falharam!", 'error')
    return random.choice([
        "o sinal tá fraco e eu tô com sono... tenta de novo.",
        "acho que exagerei no café... preciso respirar antes de responder.",
        "minha cabeça tá pesada agora. repete mais tarde, por favor.",
    ])


def buscar_wikipedia(termo: str, lang: str = 'pt', gemini_token: Optional[str] = None) -> Optional[str]:
    """
    Busca um termo na Wikipedia e retorna um resumo inteligente.
    Se gemini_token for fornecido, usa IA para extrair informações mais relevantes.
    Retorna None se não encontrar nada.
    """
    try:
        # API da Wikipedia para buscar o termo
        search_url = f"https://{lang}.wikipedia.org/w/api.php"
        search_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': termo,
            'srlimit': 1
        }
        
        headers = {'User-Agent': 'LainBot/1.0 (Discord Bot; Python/requests)'}
        search_response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
        search_response.raise_for_status()
        search_data = search_response.json()
        
        if not search_data.get('query', {}).get('search'):
            # Tenta em inglês se não encontrar em português
            if lang == 'pt':
                return buscar_wikipedia(termo, 'en', gemini_token)
            return None
        
        # Pega o título da primeira página encontrada
        page_title = search_data['query']['search'][0]['title']
        
        # Busca o conteúdo completo da introdução (não só 3 sentenças)
        summary_params = {
            'action': 'query',
            'format': 'json',
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'titles': page_title
        }
        
        summary_response = requests.get(search_url, params=summary_params, headers=headers, timeout=5)
        summary_response.raise_for_status()
        summary_data = summary_response.json()
        
        pages = summary_data.get('query', {}).get('pages', {})
        if not pages:
            return None
        
        # Pega o primeiro (e único) resultado
        page_id = list(pages.keys())[0]
        extract = pages[page_id].get('extract', '')
        
        if not extract:
            return None
        
        # Se tem token do Gemini, usa IA para resumir de forma mais inteligente
        if gemini_token:
            try:
                # Pega até 2000 caracteres do artigo para análise
                texto_completo = extract[:2000]
                
                prompt_resumo = f"""Analise este texto da Wikipedia sobre "{termo}" e extraia as informações MAIS IMPORTANTES e RELEVANTES em um resumo conciso de 3-5 frases:

{texto_completo}

Foque em: O QUE É, PARA QUE SERVE, CARACTERÍSTICAS PRINCIPAIS, CONTEXTO RELEVANTE.
Seja direto e informativo. Não use introduções como "o texto fala sobre"."""

                genai.configure(api_key=gemini_token)
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(
                    prompt_resumo,
                    generation_config={"temperature": 0.3, "max_output_tokens": 200}
                )
                
                resumo_ia = response.text.strip()
                if resumo_ia:
                    registrar_log(f"Wikipedia: resumo IA para '{termo}' ({lang})", 'info')
                    return resumo_ia
                    
            except Exception as e:
                registrar_log(f"Erro ao usar IA para resumir Wikipedia: {e}", 'warning')
                # Continua com método tradicional se IA falhar
        
        # Método tradicional: pega mais sentenças (5-7 em vez de 3)
        sentences = re.split(r'(?<=[.!?])\s+', extract)
        # Pega as primeiras sentenças até atingir ~600 caracteres
        selected_sentences = []
        char_count = 0
        for sentence in sentences[:10]:  # Máximo 10 sentenças
            if char_count + len(sentence) > 800:  # Limite aumentado
                break
            selected_sentences.append(sentence)
            char_count += len(sentence)
            
            # Garante pelo menos 3 sentenças
            if len(selected_sentences) >= 3 and char_count > 300:
                break
        
        short_summary = ' '.join(selected_sentences)
        
        registrar_log(f"Wikipedia: resumo tradicional para '{termo}' ({lang})", 'info')
        return short_summary
        
    except Exception as e:
        registrar_log(f"Erro ao buscar na Wikipedia: {e}", 'error')
        return None


def obter_resposta_com_contexto(entrada: str, gemini_token: str) -> str:
    """
    Busca contexto na Wikipedia ANTES de responder para garantir conhecimento.
    Se encontrar termos potencialmente desconhecidos, enriquece com Wikipedia automaticamente.
    """
    # Lista extensa de palavras comuns em português que não precisam de busca
    palavras_comuns = {
        # Pronomes e artigos
        'você', 'vocês', 'ele', 'ela', 'eles', 'elas', 'nós', 'meu', 'minha', 'seu', 'sua',
        'dele', 'dela', 'nosso', 'nossa', 'esse', 'essa', 'isso', 'aquele', 'aquela', 'aquilo',
        'este', 'esta', 'isto', 'qual', 'quais', 'quem', 'cujo', 'cuja', 'algo', 'alguém',
        
        # Verbos comuns (conjugações principais)
        'ser', 'está', 'estar', 'estava', 'esteve', 'sido', 'sendo', 'estão', 'eram',
        'ter', 'tem', 'teve', 'tinha', 'tendo', 'tido', 'temos', 'têm',
        'fazer', 'faz', 'fez', 'fazia', 'feito', 'fazendo', 'fazem',
        'dizer', 'disse', 'diz', 'dizia', 'dito', 'dizendo', 'dizem',
        'ir', 'vai', 'foi', 'ido', 'indo', 'vão', 'foram', 'vamos',
        'ver', 'vê', 'viu', 'visto', 'vendo', 'veem', 'viram',
        'dar', 'dá', 'deu', 'dado', 'dando', 'dão', 'deram',
        'saber', 'sabe', 'sabia', 'soube', 'sabido', 'sabendo',
        'poder', 'pode', 'pôde', 'podia', 'podido', 'podendo', 'podem',
        'querer', 'quer', 'quis', 'queria', 'querido', 'querendo', 'querem',
        'achar', 'acha', 'achou', 'achava', 'achado', 'achando',
        'ficar', 'fica', 'ficou', 'ficava', 'ficado', 'ficando',
        'vir', 'vem', 'veio', 'vinha', 'vindo', 'vêm', 'vieram',
        'pegar', 'pega', 'pegou', 'pegava', 'pegado', 'pegando',
        'levar', 'leva', 'levou', 'levava', 'levado', 'levando',
        'olhar', 'olha', 'olhou', 'olhava', 'olhado', 'olhando',
        'falar', 'fala', 'falou', 'falava', 'falado', 'falando',
        
        # Advérbios e preposições
        'sobre', 'para', 'com', 'sem', 'por', 'em', 'de', 'do', 'da', 'dos', 'das',
        'no', 'na', 'nos', 'nas', 'ao', 'aos', 'à', 'às', 'pelo', 'pela', 'pelos', 'pelas',
        'muito', 'pouco', 'mais', 'menos', 'bem', 'mal', 'melhor', 'pior',
        'sempre', 'nunca', 'jamais', 'às vezes', 'talvez', 'quase', 'apenas', 'só', 'somente',
        'ainda', 'já', 'agora', 'depois', 'antes', 'logo', 'então', 'porém', 'mas',
        'também', 'demais', 'bastante', 'meio', 'tanto', 'quanto', 'tão',
        'aqui', 'aí', 'ali', 'lá', 'cá', 'onde', 'aonde', 'quando', 'enquanto',
        'sim', 'não', 'nem', 'ou', 'e', 'porque', 'porquê', 'pois', 'senão',
        
        # Substantivos comuns
        'coisa', 'coisas', 'pessoa', 'pessoas', 'gente', 'mundo', 'vida', 'vez', 'vezes',
        'dia', 'dias', 'hora', 'horas', 'tempo', 'lugar', 'casa', 'parte', 'partes',
        'forma', 'modo', 'jeito', 'maneira', 'lado', 'tipo', 'tipos', 'caso', 'casos',
        'nome', 'nomes', 'ano', 'anos', 'mês', 'meses', 'semana', 'hoje', 'ontem', 'amanhã',
        
        # Adjetivos comuns
        'bom', 'boa', 'ruim', 'grande', 'pequeno', 'pequena', 'novo', 'nova', 'velho', 'velha',
        'outro', 'outra', 'outros', 'outras', 'mesmo', 'mesma', 'mesmos', 'mesmas',
        'certo', 'certa', 'errado', 'errada', 'diferente', 'igual', 'importante',
        
        # Números e quantificadores
        'um', 'uma', 'dois', 'duas', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove', 'dez',
        'primeiro', 'primeira', 'segundo', 'segunda', 'terceiro', 'terceira',
        'todo', 'toda', 'todos', 'todas', 'cada', 'vários', 'várias', 'algum', 'alguma',
        'nenhum', 'nenhuma', 'poucos', 'poucas', 'muitos', 'muitas',
        
        # Palavras relacionadas a comunicação digital
        'emoji', 'emojis', 'boneco', 'carinha', 'emoticon', 'símbolo', 'símbolos', 
        'ícone', 'ícones', 'imagem', 'imagens', 'foto', 'fotos', 'gif', 'gifs',
        'mensagem', 'mensagens', 'texto', 'textos', 'palavra', 'palavras',
        'chat', 'conversa', 'conversas', 'histórico', 'recente', 'recentes',
        
        # Interjeições e expressões
        'sim', 'não', 'talvez', 'claro', 'nossa', 'cara', 'mano', 'tipo',
        'né', 'oi', 'olá', 'tchau', 'obrigado', 'obrigada', 'desculpa', 'desculpe',
        
        # Palavras interrogativas
        'o que', 'que', 'quê', 'como', 'quando', 'onde', 'quanto', 'quanta', 'por que', 'porque',
        
        # Conectivos
        'se', 'caso', 'embora', 'apesar', 'contudo', 'todavia', 'entretanto', 'porém',
        'portanto', 'assim', 'logo', 'enfim', 'afinal', 'além disso', 'aliás'
    }
    
    # Extrai termos potencialmente desconhecidos (4+ letras para pegar mais termos)
    palavras = re.findall(r'\b[a-záàâãéèêíïóôõöúçñ]{4,}\b', entrada.lower())
    termos_busca = [p for p in palavras if p not in palavras_comuns]
    
    # Remove duplicatas mantendo ordem
    termos_busca = list(dict.fromkeys(termos_busca))
    
    # Se encontrou termos relevantes, busca contexto ANTES de responder
    contextos_encontrados = []
    if termos_busca:
        # Tenta buscar até 3 termos diferentes, usando IA para resumir
        for termo in termos_busca[:3]:
            contexto_wiki = buscar_wikipedia(termo, 'pt', gemini_token)
            if contexto_wiki:
                contextos_encontrados.append(f"- {termo}: {contexto_wiki}")
                registrar_log(f"Contexto encontrado na Wikipedia para: {termo}", 'info')
                
                # Se já encontrou 2 contextos, para para não sobrecarregar
                if len(contextos_encontrados) >= 2:
                    break
    
    # Se encontrou contextos, enriquece a entrada
    if contextos_encontrados:
        contexto_completo = "\n".join(contextos_encontrados)
        entrada_enriquecida = f"""CONHECIMENTO VERIFICADO (base de dados consultada com sucesso):
{contexto_completo}

PERGUNTA DO USUÁRIO: {entrada}

INSTRUÇÕES CRÍTICAS:
1. Você TEM informação completa acima. Não invente, não hesite, USE O QUE ESTÁ ESCRITO.
2. Para perguntas como "como pega X?", "o que faz Y?", "onde fica Z?": responda com DETALHES ESPECÍFICOS do conhecimento acima.
3. Se o conhecimento menciona requisitos, números, passos - INCLUA ISSO na resposta.
4. NÃO use frases vazias: "acho que você precisa...", "talvez alguns...", "parece que...".
5. SUBSTITUA por respostas concretas: "você precisa [lista específica]", "são necessários [detalhes exatos]".
6. Mantenha 1-3 frases, tom suave, mas seja INFORMATIVA e PRECISA.
7. Varie aberturas naturalmente, evite sempre começar com "hum...".

EXEMPLO DO QUE FAZER:
Pergunta: "como pega strong left?"
Conhecimento: "Strong Left é um talento que requer 40 de Strength e 25 de Medium Weapon. Permite..."
Resposta BOA: "strong left precisa de 40 strength e 25 medium weapon. é um talento que melhora ataques com a mão esquerda."
Resposta RUIM: "acho que você precisa ter strength alto e alguns talentos."

Responda AGORA usando o conhecimento acima:"""
        
        resposta = obter_resposta(entrada_enriquecida, gemini_token)
        return resposta
    
    # Se não encontrou contexto relevante, responde normalmente
    return obter_resposta(entrada, gemini_token)