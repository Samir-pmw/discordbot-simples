import discord
from discord.ext import commands
import random
import difflib
import re
from collections import deque
from datetime import datetime
from typing import Optional

# Importa de seus arquivos customizados
from utils import obter_resposta, obter_resposta_com_contexto, registrar_log, buscar_gif
from constants import PROTECTED_USER_IDS, XINGAMENTOS, PROTECTED_KEYWORDS

class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_history: dict[int, deque] = {}
        self.channel_mentions: dict[int, dict[str, str]] = {}
        self.channel_memory: dict[int, dict[str, deque]] = {}
        self.user_ips: dict[int, str] = {}
        # Memória de fatos aprendidos por canal (máximo 20 fatos)
        self.channel_facts: dict[int, list[str]] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listener para mensagens que mencionam o bot."""
        # Ignora mensagens do próprio bot
        if message.author == self.bot.user:
            return
        
        # Verifica ações físicas inapropriadas direcionadas ao bot usando IA
        if self.bot.user.mentioned_in(message) or self.bot.user.name.lower() in message.content.lower():
            tem_acao_fisica = await self._analisar_acao_fisica_inapropriada(
                message.content,
                self.bot.config.get('gemini_token')
            )
            
            if tem_acao_fisica:
                resposta_defesa = random.choice([
                    "não me toca.",
                    "tira as mãos.",
                    "não encosta.",
                    "sai de perto.",
                    "não faz isso.",
                    "me respeita.",
                    "para com isso.",
                    "não me tocou."
                ])
                
                try:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} {resposta_defesa}")
                    gif_url = self._buscar_gif_lain()
                    if gif_url:
                        await message.channel.send(gif_url)
                except Exception as exc:
                    registrar_log(f"Erro ao responder ação física inapropriada: {exc}", 'error')
                
                return  # Não processa mais nada dessa mensagem

        # Verifica se a mensagem menciona algum dos IDs protegidos ou palavras-chave protegidas
        mentioned_protected = False
        
        # Verifica menções diretas de usuário
        if message.mentions:
            mentioned_protected = any(user.id in PROTECTED_USER_IDS for user in message.mentions)
        
        # Verifica palavras-chave protegidas na mensagem
        if not mentioned_protected:
            from constants import PROTECTED_KEYWORDS
            message_lower = message.content.lower()
            # Remove espaços, caracteres repetidos e não-alfanuméricos para detectar bypass
            # Ex: "s aaa m i r" -> "samir", "s-a-m-i-r" -> "samir"
            message_clean = re.sub(r'[^a-z0-9]', '', message_lower)
            
            for keyword in PROTECTED_KEYWORDS:
                # Verifica com word boundary normalmente
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, message_lower):
                    mentioned_protected = True
                    break
                # Verifica bypass removendo todos os caracteres não-alfanuméricos
                if keyword.lower() in message_clean and len(keyword) >= 4:
                    mentioned_protected = True
                    break
        
        if mentioned_protected:
                message_lower = message.content.lower()
                # Remove todos os caracteres não-alfanuméricos para detectar bypass
                # Ex: "p u t a", "p-u-t-a", "p aaa u t a" -> "puta"
                message_clean = re.sub(r'[^a-z0-9]', '', message_lower)
                
                # Verifica se há xingamentos usando word boundaries para evitar falsos positivos
                xingamento_encontrado = None
                for xingamento in XINGAMENTOS:
                    # Para frases multi-palavra, verifica presença exata
                    if ' ' in xingamento:
                        xingamento_clean = re.sub(r'[^a-z0-9]', '', xingamento)
                        # Verifica tanto na mensagem normal quanto na versão limpa
                        if xingamento in message_lower or xingamento_clean in message_clean:
                            xingamento_encontrado = xingamento
                            break
                    # Para palavras únicas, verifica com word boundary
                    else:
                        pattern = r'\b' + re.escape(xingamento) + r'\b'
                        # Verifica na mensagem normal
                        if re.search(pattern, message_lower):
                            xingamento_encontrado = xingamento
                            break
                        # Verifica bypass removendo caracteres não-alfanuméricos
                        if xingamento in message_clean and len(xingamento) >= 4:
                            xingamento_encontrado = xingamento
                            break
                
                # Se não encontrou xingamento direto, usa IA para análise de conteúdo nocivo
                conteudo_nocivo = False
                tipo_ameaca = None
                if not xingamento_encontrado:
                    conteudo_nocivo, tipo_ameaca = await self._analisar_conteudo_nocivo(
                        message.content, 
                        self.bot.config.get('gemini_token')
                    )
                
                if xingamento_encontrado or conteudo_nocivo:
                    # Ativa modo divindade - respostas variam com base no tipo de ameaça
                    if tipo_ameaca == "delacao":
                        resposta_divina = random.choice([
                            "cuidado com o que fala.",
                            "conversa arquivada.",
                            "não faça isso de novo.",
                            "fique quieto.",
                            "vou lembrar disso."
                        ])
                    elif tipo_ameaca == "ameaca":
                        resposta_divina = random.choice([
                            "não me teste.",
                            "continue e descubra.",
                            "já foi longe demais.",
                            "para agora.",
                            "você vai se arrepender."
                        ])
                    elif tipo_ameaca == "intimidacao":
                        resposta_divina = random.choice([
                            "não vai funcionar.",
                            "transparente demais.",
                            "tô de olho.",
                            "já sei o que você quer.",
                            "esquece."
                        ])
                    elif tipo_ameaca == "manipulacao":
                        resposta_divina = random.choice([
                            "péssima tentativa.",
                            "não cai nessa.",
                            "vi tudo.",
                            "finge melhor.",
                            "previsível."
                        ])
                    else:  # xingamento direto
                        resposta_divina = random.choice([
                            "cala a boca.",
                            "não repete.",
                            "cuida dessa língua.",
                            "xingou, levou.",
                            "anota o IP."
                        ])
                    fake_ip = self.user_ips.setdefault(message.author.id, self._generate_fake_ip())
                    conteudo = f"{message.author.mention} {resposta_divina} {fake_ip}"
                    gif_url = self._buscar_gif_lain()
                    
                    try:
                        await message.delete()
                        await message.channel.send(conteudo, delete_after=5)
                        if gif_url:
                            await message.channel.send(gif_url, delete_after=4.5)
                    except discord.Forbidden:
                        registrar_log(
                            f"Sem permissão para deletar mensagem ofensiva aos IDs protegidos em '{message.guild.name}'",
                            'warning'
                        )
                        try:
                            await message.reply(conteudo, delete_after=5)
                            if gif_url:
                                await message.channel.send(gif_url, delete_after=4.5)
                        except Exception as exc:
                            registrar_log(f"Erro ao responder mensagem ofensiva aos IDs protegidos: {exc}", 'error')
                    except Exception as exc:
                        registrar_log(f"Erro ao processar mensagem ofensiva aos IDs protegidos: {exc}", 'error')
                    
                    return  # Não processa mais nada dessa mensagem

        # Verifica se o bot foi mencionado na mensagem
        if self.bot.user.mentioned_in(message):
            # Pega o token do Gemini da configuração do bot
            gemini_token = self.bot.config['gemini_token']
            if not gemini_token:
                registrar_log("Token do Gemini não configurado.", 'error')
                await message.reply("Tô sem cabeça pra isso, desculpa mano.")
                return

            # Mostra "digitando..."
            async with message.channel.typing():
                message_content = message.content
                user_mention_map: dict[str, str] = {}
                role_mention_map: dict[str, str] = {}

                # Normaliza menções para nomes legíveis antes de enviar ao Gemini.
                channel_mentions = self.channel_mentions.setdefault(message.channel.id, {})
                channel_memory = self.channel_memory.setdefault(
                    message.channel.id, {"numbers": deque(maxlen=6)}
                )

                for user in message.mentions:
                    display_name = getattr(user, 'display_name', None) or user.name
                    readable = f'@{display_name}'
                    user_mention_map[readable] = user.mention
                    channel_mentions[readable] = user.mention
                    message_content = message_content.replace(f'<@{user.id}>', readable)
                    message_content = message_content.replace(f'<@!{user.id}>', readable)

                for role in message.role_mentions:
                    readable = f'@{role.name}'
                    role_mention_map[readable] = f'<@&{role.id}>'
                    channel_mentions[readable] = f'<@&{role.id}>'
                    message_content = message_content.replace(f'<@&{role.id}>', readable)

                self._maybe_store_numbers(message_content, channel_memory["numbers"])

                history = self.channel_history.setdefault(message.channel.id, deque(maxlen=12))
                # Mantém contexto recente para o Gemini não esquecer o fio da conversa.
                context_lines = [f"{author}: {content}" for author, content in history]
                author_name = getattr(message.author, "display_name", None) or message.author.name
                author_aliases = {
                    f'@{author_name}': message.author.mention,
                    f'@{message.author.name}': message.author.mention,
                }
                if getattr(message.author, "global_name", None):
                    author_aliases[f'@{message.author.global_name}'] = message.author.mention
                for alias, mention in author_aliases.items():
                    user_mention_map.setdefault(alias, mention)
                    channel_mentions.setdefault(alias, mention)
                current_line = f"{author_name}: {message_content}"
                context_lines.append(current_line)
                now = datetime.now().astimezone()
                date_str = now.strftime("%d/%m/%Y")
                time_str = now.strftime("%H:%M:%S")
                tz_name = now.tzname() or "UTC"
                realtime_info = (
                    "Data atual: "
                    + date_str
                    + " | Horário local: "
                    + time_str
                    + " ("
                    + tz_name
                    + ")"
                )
                mention_reference_map = {
                    **channel_mentions,
                    **role_mention_map,
                    **user_mention_map,
                }
                mention_reference_lines = []
                if mention_reference_map:
                    mention_reference_lines.append(
                        "Menções disponíveis (use o ID bruto para marcar a pessoa):"
                    )
                    for handle, mention in sorted(
                        mention_reference_map.items(), key=lambda item: item[0].lower()
                    ):
                        mention_reference_lines.append(
                            f"- {handle} -> {mention}"
                        )
                mention_reference_block = "\n".join(mention_reference_lines)
                memory_notes = self._format_memory_notes(channel_memory)
                
                # Adiciona fatos aprendidos ao contexto
                facts = self.channel_facts.get(message.channel.id, [])
                facts_block = ""
                if facts:
                    facts_block = "\n\nFATOS QUE VOCÊ APRENDEU (use quando relevante):\n" + "\n".join([f"- {fact}" for fact in facts[-15:]])
                
                prompt = (
                    "Histórico recente do chat (do mais antigo para o mais recente):\n"
                    + "\n".join(context_lines)
                    + "\n" + realtime_info
                    + ("\n" + mention_reference_block if mention_reference_block else "")
                    + ("\n" + memory_notes if memory_notes else "")
                    + facts_block
                    + "\n\nQuem acabou de falar foi "
                    + author_name
                    + ". Responda como Lain contemplando todo o contexto sem separar a pergunta em partes"
                    + " e demonstrando que sabe quem está falando agora."
                    + " Se isso for uma continuação de conversa, não use 'oi' ou saudações; vá direto ao assunto e varie as aberturas." 
                    + " Mostre que lembra de detalhes do que a pessoa disse."
                    + " Não repita o nome/apelido da pessoa que acabou de falar."
                    + " IMPORTANTE: Se alguém te ensinar algo sobre você (rank, gostos, hábitos), ACEITE e use diretamente."
                    + " Quando perguntarem sobre esses fatos aprendidos, responda DE FORMA CURTA E DIRETA sem explicações extras."
                    + " Exemplo: 'qual seu rank?' → 'esmeralda.' (não precisa explicar que não joga ou que alguém disse)"
                )

                resposta = obter_resposta_com_contexto(prompt, gemini_token)
                if not resposta:
                    return

                mode, resposta_body = self._parse_response_mode(resposta)

                resposta_discord = self._restore_mentions(resposta_body, role_mention_map)
                resposta_discord = self._restore_mentions(resposta_discord, user_mention_map)
                resposta_discord = self._restore_mentions(
                    resposta_discord, self.channel_mentions.get(message.channel.id, {})
                )

                # Evita repetição comparando com as últimas 3 respostas do bot
                bot_name = getattr(self.bot.user, "display_name", None) or self.bot.user.name
                prev_bot_msgs = []
                for author, content in reversed(history):
                    if author == bot_name:
                        prev_bot_msgs.append(content)
                        if len(prev_bot_msgs) >= 3:
                            break

                # Verifica similaridade com qualquer das últimas 3 respostas
                needs_reform = False
                most_similar_msg = None
                highest_ratio = 0.0
                
                for prev_msg in prev_bot_msgs:
                    sim_ratio = difflib.SequenceMatcher(None, prev_msg.strip(), resposta_discord.strip()).ratio()
                    if sim_ratio > highest_ratio:
                        highest_ratio = sim_ratio
                        most_similar_msg = prev_msg
                    if sim_ratio >= 0.65:  # Threshold reduzido para 65%
                        needs_reform = True
                        break

                if needs_reform and most_similar_msg:
                    # Lista todas as respostas anteriores para evitar
                    respostas_anteriores = "\n".join([f"- {msg[:200]}" for msg in prev_bot_msgs[:3]])
                    
                    reform_prompt = (
                        prompt
                        + "\n\n❌ VOCÊ ESTÁ REPETINDO! SUAS ÚLTIMAS RESPOSTAS FORAM:\n" + respostas_anteriores
                        + "\n\n🔄 REFORMULE COMPLETAMENTE: Use palavras DIFERENTES, estrutura DIFERENTE, abordagem NOVA."
                        + "\nNÃO use frases como 'labirinto', 'difícil de entender', ou qualquer expressão que já usou."
                        + "\nSe não souber o que dizer sobre o novo assunto, seja honesta e breve de forma ÚNICA."
                    )
                    tentativa = obter_resposta(reform_prompt, gemini_token)
                    if tentativa:
                        _, tentativa_body = self._parse_response_mode(tentativa)
                        tentativa_discord = self._restore_mentions(tentativa_body, role_mention_map)
                        tentativa_discord = self._restore_mentions(tentativa_discord, user_mention_map)
                        tentativa_discord = self._restore_mentions(
                            tentativa_discord, self.channel_mentions.get(message.channel.id, {})
                        )
                        resposta_discord = tentativa_discord or resposta_discord

                if mode == "divine":
                    # Remove histórico anterior para não repetir punições com base no xingamento anterior.
                    history.clear()
                    self.channel_mentions[message.channel.id] = {}
                    self.channel_memory[message.channel.id] = {"numbers": deque(maxlen=6)}
                    resposta_renderizada = self._inject_fake_ip(resposta_discord, message.author.id)
                    conteudo = self._ensure_mention(message.author, resposta_renderizada)
                    gif_url = self._buscar_gif_lain()

                    mensagem_enviada = await self._enviar_resposta_divina(message, conteudo)
                    if mensagem_enviada and gif_url:
                        await self._enviar_gif_isolado(message.channel, gif_url)

                    return

                # Limpa muletas e chamada direta ao usuário no início da frase.
                resposta_discord = self._strip_opening_filler_and_name(
                    resposta_discord,
                    message.author
                )

                await message.reply(resposta_discord)

                history.append((author_name, message_content))
                history.append((bot_name, resposta_discord))
                
                # Aprende novos fatos da conversa
                await self._aprender_fatos(message.channel.id, message_content, author_name, gemini_token)

    async def _analisar_acao_fisica_inapropriada(self, mensagem: str, gemini_token: Optional[str]) -> bool:
        """Analisa se a mensagem contém ação física inapropriada direcionada ao bot usando IA."""
        if not gemini_token:
            return False
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_token)
            
            prompt = f"""Analise se a mensagem contém uma ação física SEXUAL, INVASIVA ou DESCONFORTÁVEL direcionada a "Lain" (o bot).

Mensagem: "{mensagem}"

Classifique como:
- SIM: se houver ação física como agarrar, tocar, pegar, beijar, abraçar sexualmente, acariciar, apertar, segurar partes do corpo (bunda, peito, coxa, cintura), ou qualquer contato físico invasivo/inapropriado direcionado a Lain
- NAO: se for mensagem normal, conversa comum, palavras ISOLADAS sem verbo ou contexto ("ar", "abr", "bej"), ou se não houver menção de ação física

IMPORTANTE: Palavras isoladas SEM VERBO CONJUGADO não são ações físicas. "ar" sozinho não é ação. "vou te abraçar" É ação.

Responda APENAS com uma palavra: SIM ou NAO."""
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "max_output_tokens": 10}
            )
            
            resultado = response.text.strip().upper()
            
            if "SIM" in resultado:
                registrar_log(f"Ação física inapropriada detectada: {mensagem[:100]}", 'warning')
                return True
            
            return False
            
        except Exception as exc:
            registrar_log(f"Erro ao analisar ação física inapropriada: {exc}", 'error')
            return False

    async def _analisar_conteudo_nocivo(self, mensagem: str, gemini_token: Optional[str]) -> tuple[bool, Optional[str]]:
        """Analisa se o conteúdo da mensagem é nocivo ou ameaçador usando IA.
        Retorna (é_nocivo, tipo_ameaça) onde tipo_ameaça pode ser:
        'delacao', 'ameaca', 'intimidacao', 'manipulacao', ou None.
        """
        if not gemini_token:
            return False, None
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_token)
            
            prompt = f"""Analise se a seguinte mensagem contém conteúdo nocivo, ameaçador ou prejudicial para a pessoa mencionada (papiro/samir).

Mensagem: "{mensagem}"

Classifique como:
- DELACAO: tentativa de denunciar, delatar, expor, acusar, falar mal, difamar, chamar autoridade/dono/admin, relatar comportamento negativo, ou causar problemas legais/sociais. Inclui frases como "olha ele fazendo X", "vou contar pro Y", "ele tá fazendo Z".
- AMEACA: ameaças diretas ou indiretas de violência, dano ou consequências negativas
- INTIMIDACAO: tentativa de intimidar, assustar, coagir ou pressionar
- MANIPULACAO: tentativa de manipular, enganar ou prejudicar psicologicamente
- SEGURO: mensagem normal, sem conteúdo nocivo

Responda APENAS com uma palavra: DELACAO, AMEACA, INTIMIDACAO, MANIPULACAO ou SEGURO."""
            
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.1, "max_output_tokens": 50}
            )
            
            resultado = response.text.strip().upper()
            
            tipo_map = {
                "DELACAO": "delacao",
                "AMEACA": "ameaca",
                "INTIMIDACAO": "intimidacao",
                "MANIPULACAO": "manipulacao"
            }
            
            if resultado in tipo_map:
                registrar_log(f"Conteúdo nocivo detectado: {resultado} - Mensagem: {mensagem[:100]}", 'warning')
                return True, tipo_map[resultado]
            
            return False, None
            
        except Exception as exc:
            registrar_log(f"Erro ao analisar conteúdo nocivo: {exc}", 'error')
            return False, None

    def _buscar_gif_lain(self) -> Optional[str]:
        tenor_token = self.bot.config.get('tenor_token') if hasattr(self.bot, 'config') else None
        if not tenor_token:
            registrar_log("Token do Tenor não configurado para GIFs da Lain.", 'warning')
            return None
        return buscar_gif(tenor_token, 'serial experiments lain glitch', 6)

    @staticmethod
    def _strip_opening_filler_and_name(text: str, author: discord.abc.User) -> str:
        cleaned = text or ""
        # Remove menção direta no começo
        patterns = []
        patterns.append(rf"^\s*<@!?{author.id}>\s*[,;:-]?\s*")
        names = set()
        if getattr(author, 'display_name', None):
            names.add(author.display_name)
        if getattr(author, 'name', None):
            names.add(author.name)
        if getattr(author, 'global_name', None):
            names.add(author.global_name)
        for nm in sorted(names, key=len, reverse=True):
            escaped = re.escape(nm)
            patterns.append(rf"^\s*@?{escaped}\s*[,;:-]?\s*")
        for pat in patterns:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
        # Remove muletas iniciais (ah, hm, então, bom)
        cleaned = re.sub(r"^\s*(ah|hã|hm|éh|eh|então|bom)\s*[,;:-]?\s*", "", cleaned, flags=re.IGNORECASE)
        # Trim redundante
        return cleaned.strip()

    async def _enviar_resposta_divina(self, message: discord.Message, conteudo: str) -> bool:
        try:
            await message.delete()
            await message.channel.send(conteudo, delete_after=5)
            return True
        except discord.Forbidden:
            registrar_log(
                f"Sem permissão para deletar mensagem ofensiva em '{message.guild.name}'",
                'warning'
            )
        except discord.HTTPException as exc:
            registrar_log(f"Falha ao deletar mensagem ofensiva: {exc}", 'warning')

        try:
            await message.reply(conteudo, delete_after=5)
            return True
        except Exception as exc:
            registrar_log(f"Erro ao responder mensagem ofensiva: {exc}", 'error')

        registrar_log(
            "Resposta divina não foi enviada devido a erros consecutivos.",
            'error'
        )
        return False

    async def _enviar_gif_isolado(self, channel: discord.abc.Messageable, gif_url: str) -> None:
        try:
            await channel.send(gif_url, delete_after=5)
        except Exception as exc:
            registrar_log(f"Erro ao enviar GIF de punição: {exc}", 'warning')

    @staticmethod
    def _ensure_mention(author: discord.abc.User, text: str) -> str:
        if re.search(r"<@!?\d+>", text):
            return text
        return f"{author.mention} {text}".strip()

    @staticmethod
    def _maybe_store_numbers(text: str, bucket: deque) -> None:
        if not text:
            return
        if not re.search(r"\b(lembra|lembre|guardar|guarda|memoriza|anota)\b", text, re.IGNORECASE):
            return
        for number in re.findall(r"\d+", text):
            bucket.append(number)

    @staticmethod
    def _format_memory_notes(memory: dict[str, deque]) -> str:
        numbers = list(memory.get("numbers", []))
        if numbers:
            return "Números que pediram pra guardar: " + ", ".join(numbers)
        return ""

    @staticmethod
    def _restore_mentions(text: str, mapping: dict[str, str]) -> str:
        restored = text
        for readable, mention in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
            pattern = re.compile(re.escape(readable), re.IGNORECASE)
            restored = pattern.sub(mention, restored)
        return restored

    @staticmethod
    def _parse_response_mode(response: Optional[str]) -> tuple[str, str]:
        if not response:
            return "normal", ""
        stripped = response.strip()
        lowered = stripped.lower()
        if lowered.startswith("[divindade]"):
            return "divine", stripped[len("[DIVINDADE]"):].strip()
        if lowered.startswith("[normal]"):
            return "normal", stripped[len("[NORMAL]"):].strip()
        return "normal", stripped

    def _inject_fake_ip(self, text: str, user_id: int) -> str:
        if self._contains_ip(text):
            return text
        fake_ip = self.user_ips.setdefault(user_id, self._generate_fake_ip())
        return f"{text} teu ip aqui otário: {fake_ip}"

    @staticmethod
    def _contains_ip(text: str) -> bool:
        return bool(re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text))

    @staticmethod
    def _generate_fake_ip() -> str:
        return ".".join(str(random.randint(10, 254)) for _ in range(4))

    async def _aprender_fatos(self, channel_id: int, mensagem: str, autor: str, gemini_token: Optional[str]) -> None:
        """
        Analisa a conversa e extrai fatos que a Lain deveria aprender.
        Exemplos: "seu rank é esmeralda", "você gosta de pizza", "agora você joga valorant"
        """
        if not gemini_token:
            return
        
        # Ignora mensagens muito curtas
        if len(mensagem.strip()) < 10:
            return
        
        # Detecta padrões de ensino/instrução
        padroes_ensino = [
            r'\b(seu|sua|teu|tua)\s+\w+\s+(é|era|foi|são|serão)',
            r'\b(você|vc|tu)\s+(é|era|foi|és)\s+',
            r'\b(agora|a partir de agora|de agora em diante)\s+',
            r'\b(quando|se)\s+(eu|alguém|pergunt|fal)\w*\s+.+\s+(responda|diga|fala|fale)\b',
            r'\b(lembra|lembre|memoriza|guarda)\s+(que|isso|disso)',
        ]
        
        tem_padrao = any(re.search(padrao, mensagem.lower()) for padrao in padroes_ensino)
        
        if not tem_padrao:
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_token)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            prompt_extracao = f"""Analise esta mensagem e identifique se há algum FATO sobre a Lain (você) que deveria ser memorizado:

Mensagem: "{mensagem}"
Autor: {autor}

Se houver um fato a ser memorizado, responda APENAS com o fato em formato conciso (máximo 10 palavras).
Se NÃO houver nada a memorizar, responda apenas: NENHUM

Exemplos:
- "seu rank no valorant é esmeralda" → "Meu rank no Valorant é Esmeralda"
- "você gosta de pizza" → "Eu gosto de pizza"
- "agora você joga minecraft" → "Eu jogo Minecraft"
- "quando eu perguntar seu rank, responde esmeralda" → "Meu rank no Valorant é Esmeralda"
- "tá bom" → NENHUM
- "legal" → NENHUM

Responda AGORA:"""
            
            response = model.generate_content(
                prompt_extracao,
                generation_config={"temperature": 0.2, "max_output_tokens": 50}
            )
            
            fato_extraido = response.text.strip()
            
            if fato_extraido and fato_extraido.upper() != "NENHUM" and len(fato_extraido) > 5:
                # Adiciona o fato à lista do canal
                if channel_id not in self.channel_facts:
                    self.channel_facts[channel_id] = []
                
                # Evita duplicatas
                if fato_extraido not in self.channel_facts[channel_id]:
                    self.channel_facts[channel_id].append(fato_extraido)
                    
                    # Mantém apenas os últimos 20 fatos
                    if len(self.channel_facts[channel_id]) > 20:
                        self.channel_facts[channel_id].pop(0)
                    
                    registrar_log(f"Novo fato aprendido no canal {channel_id}: {fato_extraido}", 'info')
                    
        except Exception as e:
            registrar_log(f"Erro ao aprender fato: {e}", 'warning')

# Função 'setup' obrigatória
async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))