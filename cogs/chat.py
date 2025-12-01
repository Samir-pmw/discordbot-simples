import discord
from discord.ext import commands
import random
import difflib
import re
from collections import deque
from datetime import datetime
from typing import Optional

# Importa de seus arquivos customizados
from utils import obter_resposta, registrar_log, buscar_gif

class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_history: dict[int, deque] = {}
        self.channel_mentions: dict[int, dict[str, str]] = {}
        self.channel_memory: dict[int, dict[str, deque]] = {}
        self.user_ips: dict[int, str] = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listener para mensagens que mencionam o bot."""
        # Ignora mensagens do próprio bot
        if message.author == self.bot.user:
            return

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
                prompt = (
                    "Histórico recente do chat (do mais antigo para o mais recente):\n"
                    + "\n".join(context_lines)
                    + "\n" + realtime_info
                    + ("\n" + mention_reference_block if mention_reference_block else "")
                    + ("\n" + memory_notes if memory_notes else "")
                    + "\n\nQuem acabou de falar foi "
                    + author_name
                    + ". Responda como Lain contemplando todo o contexto sem separar a pergunta em partes"
                    + " e demonstrando que sabe quem está falando agora."
                    + " Se isso for uma continuação de conversa, não use 'oi' ou saudações; vá direto ao assunto e varie as aberturas." 
                    + " Mostre que lembra de detalhes do que a pessoa disse."
                    + " Não repita o nome/apelido da pessoa que acabou de falar."
                )

                resposta = obter_resposta(prompt, gemini_token)
                if not resposta:
                    return

                mode, resposta_body = self._parse_response_mode(resposta)

                resposta_discord = self._restore_mentions(resposta_body, role_mention_map)
                resposta_discord = self._restore_mentions(resposta_discord, user_mention_map)
                resposta_discord = self._restore_mentions(
                    resposta_discord, self.channel_mentions.get(message.channel.id, {})
                )

                # Evita repetição quase idêntica à última resposta do bot.
                bot_name = getattr(self.bot.user, "display_name", None) or self.bot.user.name
                prev_bot_msg: Optional[str] = None
                for author, content in reversed(history):
                    if author == bot_name:
                        prev_bot_msg = content
                        break

                if prev_bot_msg:
                    sim_ratio = difflib.SequenceMatcher(None, prev_bot_msg.strip(), resposta_discord.strip()).ratio()
                    if sim_ratio >= 0.88:
                        reform_prompt = (
                            prompt
                            + " Reformule sua resposta sem repetir a anterior. "
                            + "Resposta anterior foi: '''" + prev_bot_msg[:600] + "''' . "
                            + "Responda apenas ao novo pedido, de forma direta e diferente."
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

# Função 'setup' obrigatória
async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))