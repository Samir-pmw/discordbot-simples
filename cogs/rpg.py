import json
import random
from pathlib import Path
from typing import Optional, Tuple

import discord
from discord import app_commands
from discord.ext import commands

from constants import (
    dados_regex,
    gifs_anime,
    gifs_um_natural,
    numero_max_de_campanhas,
    respostas_lain_limite,
)
from utils import FICHAS_DIR, INVENTARIOS_DIR, registrar_log, buscar_gif

LEO_USER_ID = 605425112744984596
LEO_NAT1_PIADAS = [
    "Leo, você está colecionando? Vou parar de colocar suas rolagens nos logs kkkkkkkkkkk",
    "Outro um natural, Leo? Santo gap.",
    "Sei que é você, Leo. O dado me contou antes de cair no 1. KKKKKKKKKKKKKKKKKKKKKK",
]


class CampanhaStore:
    """Persistência simplificada em um único arquivo por usuário."""

    def __init__(self):
        self._cache: dict[int, dict] = {}

    def _player_data_path(self, user_id: int) -> Path:
        return INVENTARIOS_DIR / f"{user_id}_campanhas.json"

    @staticmethod
    def _default_data() -> dict:
        return {"campanhas": {}, "selecionada": None}

    def _load_player_data(self, user_id: int) -> dict:
        data = self._cache.get(user_id)
        if data is not None:
            return data

        path = self._player_data_path(user_id)
        if path.exists():
            try:
                with path.open("r", encoding="utf-8") as arquivo:
                    data = json.load(arquivo)
            except (json.JSONDecodeError, OSError):
                data = self._default_data()
        else:
            data = self._migrate_from_legacy(user_id)
            self._save_player_data(user_id, data)

        if not isinstance(data, dict):
            data = self._default_data()

        data.setdefault("campanhas", {})
        data.setdefault("selecionada", None)
        self._cache[user_id] = data
        return data

    def _save_player_data(self, user_id: int, data: dict):
        path = self._player_data_path(user_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as arquivo:
            json.dump(data, arquivo, ensure_ascii=False, indent=2)

    def _migrate_from_legacy(self, user_id: int) -> dict:
        data = self._default_data()
        prefixo = f"inventario_{user_id}_"
        for arquivo in INVENTARIOS_DIR.glob(f"{prefixo}*.txt"):
            campanha = arquivo.stem[len(prefixo):]
            if not campanha:
                continue

            inventario: dict[str, int] = {}
            try:
                with arquivo.open("r", encoding="utf-8") as handler:
                    for linha in handler:
                        try:
                            item, quantidade = linha.strip().split(":", 1)
                            inventario[normalizar_nome_item(item)] = int(quantidade)
                        except (ValueError, TypeError):
                            continue
            except OSError:
                inventario = {}

            ficha_path = FICHAS_DIR / f"ficha_{user_id}_{campanha}.txt"
            ficha_texto = ""
            if ficha_path.exists():
                try:
                    ficha_texto = ficha_path.read_text(encoding="utf-8").strip()
                except OSError:
                    ficha_texto = ""

            data["campanhas"][campanha] = {"inventario": inventario, "ficha": ficha_texto}

        return data

    def list_campaigns(self, user_id: int) -> list[str]:
        data = self._load_player_data(user_id)
        return sorted(data["campanhas"].keys())

    def get_selected_campaign(self, user_id: int) -> Optional[str]:
        data = self._load_player_data(user_id)
        selecionada = data.get("selecionada")
        if selecionada and selecionada not in data["campanhas"]:
            data["selecionada"] = None
            self._save_player_data(user_id, data)
            selecionada = None
        return selecionada

    def require_selected_campaign(self, user_id: int) -> str:
        selecionada = self.get_selected_campaign(user_id)
        if not selecionada:
            raise ValueError("Nenhuma campanha selecionada. Abra o /painel_rpg e escolha uma na lista.")
        return selecionada

    def set_selected_campaign(self, user_id: int, nome: str):
        data = self._load_player_data(user_id)
        if nome not in data["campanhas"]:
            raise ValueError(f"Campanha '{nome}' não encontrada.")
        data["selecionada"] = nome
        self._save_player_data(user_id, data)

    def create_campaign(self, user_id: int, nome: str) -> str:
        nome = nome.strip()
        if not nome:
            raise ValueError("Escolhe um nome de verdade pra campanha.")

        data = self._load_player_data(user_id)
        if len(data["campanhas"]) >= numero_max_de_campanhas:
            raise ValueError(f"Você já atingiu o limite de {numero_max_de_campanhas} campanhas.")

        if nome in data["campanhas"]:
            raise ValueError(f"Já existe uma campanha chamada '{nome}'.")

        data["campanhas"][nome] = {"inventario": {}, "ficha": ""}
        data["selecionada"] = nome
        self._save_player_data(user_id, data)
        return nome

    def delete_campaign(self, user_id: int, nome: str):
        data = self._load_player_data(user_id)
        if nome not in data["campanhas"]:
            raise ValueError(f"Campanha '{nome}' não encontrada.")

        del data["campanhas"][nome]
        if data.get("selecionada") == nome:
            data["selecionada"] = None
        self._save_player_data(user_id, data)

    def _get_campaign(self, data: dict, nome: str) -> dict:
        try:
            return data["campanhas"][nome]
        except KeyError as exc:
            raise ValueError(f"Campanha '{nome}' não encontrada.") from exc

    def get_inventory(self, user_id: int, campanha: str) -> dict[str, int]:
        data = self._load_player_data(user_id)
        campanha_data = self._get_campaign(data, campanha)
        return dict(campanha_data["inventario"])

    def get_sheet(self, user_id: int, campanha: str) -> str:
        data = self._load_player_data(user_id)
        campanha_data = self._get_campaign(data, campanha)
        return campanha_data.get("ficha", "")

    def set_sheet(self, user_id: int, campanha: str, texto: str):
        data = self._load_player_data(user_id)
        campanha_data = self._get_campaign(data, campanha)
        campanha_data["ficha"] = texto.strip()
        self._save_player_data(user_id, data)

    def change_item_quantity(self, user_id: int, campanha: str, nome: str, delta: int) -> Tuple[str, int]:
        if delta == 0:
            raise ValueError("Quantidade zero não muda nada, né?")

        data = self._load_player_data(user_id)
        campanha_data = self._get_campaign(data, campanha)
        inventario = campanha_data.setdefault("inventario", {})

        item_normalizado = normalizar_nome_item(nome)
        atual = inventario.get(item_normalizado, 0)

        if delta < 0 and atual < abs(delta):
            raise ValueError(f"Você não tem {abs(delta)}x {item_normalizado} pra remover.")

        novo_total = atual + delta
        if novo_total <= 0:
            inventario.pop(item_normalizado, None)
            novo_total = 0
        else:
            inventario[item_normalizado] = novo_total

        self._save_player_data(user_id, data)
        return item_normalizado, novo_total


def _gif_lain_alerta(tenor_token: Optional[str]) -> Optional[str]:
    if tenor_token:
        gif_url = buscar_gif(tenor_token, 'serial experiments lain glitch', 6)
        if gif_url:
            return gif_url
    registrar_log("Não foi possível buscar GIF de alerta da Lain (Tenor).", "warning")
    return None


def _gif_lain_riso(tenor_token: Optional[str]) -> Optional[str]:
    if tenor_token:
        gif_url = buscar_gif(tenor_token, 'lain iwakura smile', 4)
        if gif_url:
            return gif_url
    registrar_log("Não foi possível buscar GIF de riso da Lain (Tenor).", "warning")
    return None


def _is_leo(user_id: Optional[int]) -> bool:
    return user_id == LEO_USER_ID


async def _responder_natural_um(
    *,
    interaction: Optional[discord.Interaction],
    message: Optional[discord.Message],
    roller_id: Optional[int],
    tenor_token: Optional[str],
):
    texto = None
    gif_url = None

    if _is_leo(roller_id):
        texto = random.choice(LEO_NAT1_PIADAS)
        gif_url = _gif_lain_riso(tenor_token)
        if not gif_url and gifs_um_natural:
            gif_url = random.choice(gifs_um_natural)
    else:
        gif_url = random.choice(gifs_um_natural)

    if interaction:
        if texto:
            await interaction.followup.send(texto)
        if gif_url:
            await interaction.followup.send(gif_url)
    elif message:
        if texto:
            await message.channel.send(texto)
        if gif_url:
            await message.channel.send(gif_url)


async def processar_rolagem(
    dados: str,
    interaction: Optional[discord.Interaction] = None,
    message: Optional[discord.Message] = None,
    tenor_token: Optional[str] = None,
    roller_id: Optional[int] = None,
):
    """Processa uma string de rolagem de dados (ex: 2d20+5)."""
    try:
        if not any("d" in parte[0] for parte in dados_regex.findall(dados)):
            return

        if message:
            registrar_log(f"Processando rolagem: {dados} por {message.author}", "info")

        partes = dados_regex.findall(dados)
        total = 0
        detalhes: list[str] = []
        primeiro_dado = True
        natural_20 = False
        natural_1 = False

        for rolagem, numero in partes:
            if rolagem:
                operador = "+"
                if rolagem.startswith(("+", "-")):
                    operador = rolagem[0]
                    rolagem = rolagem[1:]

                qtd, faces = map(int, rolagem.split("d"))

                if qtd > 100 or faces > 1000:
                    resposta_erro = random.choice(respostas_lain_limite)
                    if interaction and not interaction.response.is_done():
                        await interaction.response.send_message(resposta_erro, ephemeral=False)
                    elif message:
                        await message.reply(resposta_erro, mention_author=True)

                    canal = interaction.channel if interaction else message.channel if message else None
                    alerta = _gif_lain_alerta(tenor_token)
                    if canal and alerta:
                        await canal.send(alerta)
                    return

                resultados = sorted(random.randint(1, faces) for _ in range(qtd))
                soma_rolagem = sum(resultados)

                if rolagem == "1d20" and 20 in resultados:
                    natural_20 = True
                if rolagem == "1d20" and 1 in resultados:
                    natural_1 = True

                total = total + soma_rolagem if operador == "+" else total - soma_rolagem

                detalhe_str = f"{rolagem}: {resultados} = ``{soma_rolagem}``"
                if qtd > 100:
                    detalhe_str = f"{rolagem}: ``{soma_rolagem}`` (dados demais...)"

                if primeiro_dado:
                    detalhes.append(detalhe_str)
                    primeiro_dado = False
                else:
                    detalhes.append(f"{operador}{detalhe_str}")

            elif numero:
                valor = int(numero)
                sinal = "+" if valor >= 0 else "-"
                total += valor
                detalhes.append(f"{sinal}``{abs(valor)}``")

        total_final = max(total, 1)
        resposta = f"🎲 **Resultado das rolagens:**\n{''.join(detalhes)}\n**Total:** ``{total_final}``"

        if natural_20:
            resposta += "\n\n🎉 **VINTE NATURAL!** 🎉"
        if natural_1:
            resposta += "\n\n**UM NATURALKKKKKKKKKKKKKKKKKKKK, lastimável**"

        if interaction:
            if not interaction.response.is_done():
                await interaction.response.send_message(resposta)
            else:
                await interaction.followup.send(resposta)

            if natural_20:
                await interaction.followup.send(random.choice(gifs_anime))
            if natural_1:
                await _responder_natural_um(
                    interaction=interaction,
                    message=None,
                    roller_id=roller_id,
                    tenor_token=tenor_token,
                )
        elif message:
            await message.reply(resposta)
            if natural_20:
                await message.channel.send(random.choice(gifs_anime))
            if natural_1:
                await _responder_natural_um(
                    interaction=None,
                    message=message,
                    roller_id=roller_id,
                    tenor_token=tenor_token,
                )

    except Exception as exc:  # pylint: disable=broad-except
        registrar_log(f"Erro ao processar rolagem '{dados}': {exc}", "error")
        gif_riso = "https://media.tenor.com/4OPvDDTjWhEAAAAd/lain-lain-iwakura.gif"
        mensagem_404 = "Deu errado isso ai kkkkkkkkkk"

        if interaction:
            if not interaction.response.is_done():
                await interaction.response.send_message(mensagem_404, ephemeral=False)
                if gif_riso:
                    await interaction.followup.send(gif_riso)
            else:
                await interaction.followup.send(mensagem_404)
                if gif_riso:
                    await interaction.followup.send(gif_riso)
        elif message:
            await message.reply(mensagem_404)
            if gif_riso:
                await message.channel.send(gif_riso)


def normalizar_nome_item(nome: str) -> str:
    return nome.lower().strip().title()


class RPG(commands.Cog):
    """Comandos de suporte à mesa de RPG."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.store = CampanhaStore()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if self.bot.user and self.bot.user.mentioned_in(message):
            return

        if message.content.startswith('/'):
            return

        if dados_regex.match(message.content.lower()):
            await processar_rolagem(
                message.content,
                message=message,
                tenor_token=self.bot.config.get('tenor_token') if hasattr(self.bot, 'config') else None,
                roller_id=message.author.id,
            )

    @app_commands.command(name="painel_rpg", description="Abre um painel visual para gerenciar campanhas, itens e fichas.")
    async def painel_rpg(self, interaction: discord.Interaction):
        view = CampanhaDashboard(self, interaction.user)
        embed = view.build_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        try:
            original = await interaction.original_response()
            view.message_id = original.id
        except Exception:  # pylint: disable=broad-except
            view.message_id = None

    @app_commands.command(name="rolar", description="Rola dados no formato XdY+Z ou XdY-Z")
    async def rolar_dados(self, interaction: discord.Interaction, dados: str):
        await processar_rolagem(
            dados,
            interaction=interaction,
            tenor_token=self.bot.config.get('tenor_token') if hasattr(self.bot, 'config') else None,
            roller_id=interaction.user.id,
        )


class CampanhaDashboard(discord.ui.View):
    """Interface visual simples para gerenciar campanhas e inventários."""

    TAB_ORDER = ("overview", "inventory", "sheet")

    def __init__(self, cog: "RPG", user: discord.abc.User, *, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.user_id = user.id
        self.username = getattr(user, "display_name", user.name)
        self.current_tab = "overview"
        self.status_message: Optional[str] = None
        self.message_id: Optional[int] = None
        self._rebuild_components()

    def set_status(self, message: str):
        self.status_message = message.strip()

    async def update_view(self, interaction: discord.Interaction, *, status: Optional[str] = None):
        if status:
            self.set_status(status)
        self._rebuild_components()
        embed = self.build_embed()
        if interaction.response.is_done():
            target_id = None
            if interaction.message:
                target_id = interaction.message.id
            elif getattr(self, "message_id", None):
                target_id = self.message_id
            else:
                try:
                    target_id = (await interaction.original_response()).id
                except Exception:  # pylint: disable=broad-except
                    target_id = None

            if target_id:
                await interaction.followup.edit_message(message_id=target_id, embed=embed, view=self)
            else:
                await interaction.followup.send(embed=embed, view=self, ephemeral=True)
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    def build_embed(self) -> discord.Embed:
        campanhas = self.cog.store.list_campaigns(self.user_id)
        selecionada = self.cog.store.get_selected_campaign(self.user_id)
        tab = self.current_tab
        color_map = {
            "overview": discord.Color.purple(),
            "inventory": discord.Color.dark_teal(),
            "sheet": discord.Color.dark_magenta(),
        }

        title_map = {
            "overview": "🧠 Painel de Campanhas",
            "inventory": f"📦 Inventário — {selecionada or 'nenhuma'}",
            "sheet": f"🗒️ Ficha — {selecionada or 'nenhuma'}",
        }

        embed = discord.Embed(
            title=title_map.get(tab, title_map["overview"]),
            color=color_map.get(tab, discord.Color.purple()),
        )
        embed.set_author(name=f"Modo atual: {self._tab_label(tab)}")

        if tab == "overview":
            embed.description = (
                "Tudo que você precisa em um lugar só. Use a lista para escolher a campanha e os botões para mexer."  # noqa: E501
            )
            embed.add_field(name="Campanhas", value=self._format_campaigns(campanhas), inline=False)

            if selecionada:
                inventario = self.cog.store.get_inventory(self.user_id, selecionada)
                embed.add_field(
                    name=f"Inventário ativo ({selecionada})",
                    value=self._format_inventory_preview(inventario),
                    inline=False,
                )
                ficha = self.cog.store.get_sheet(self.user_id, selecionada)
                embed.add_field(
                    name="Ficha (prévia)",
                    value=self._format_sheet_preview(ficha),
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Sem campanha selecionada",
                    value="Escolha uma usando a lista acima ou crie algo novo.",
                    inline=False,
                )

        elif tab == "inventory":
            if not selecionada:
                embed.description = "Selecione uma campanha para abrir o inventário."
            else:
                inventario = self.cog.store.get_inventory(self.user_id, selecionada)
                embed.description = self._format_inventory_full(inventario)

        elif tab == "sheet":
            if not selecionada:
                embed.description = "Selecione uma campanha para visualizar a ficha."
            else:
                ficha = self.cog.store.get_sheet(self.user_id, selecionada)
                embed.description = self._format_sheet_block(ficha)

        # "Atualização recente" foi removida — mantemos o status internamente
        # caso outras partes do código queiram setar mensagens, mas não
        # exibimos mais esse campo no painel para evitar poluição visual.

        embed.set_footer(text=f"{len(campanhas)}/{numero_max_de_campanhas} campanhas | {self.username}")
        return embed

    def _format_campaigns(self, campanhas: list[str]) -> str:
        if not campanhas:
            return "Nenhuma campanha ainda. Clique em **Criar Campanha**."

        linhas = [f"- {nome}" for nome in campanhas[:10]]
        if len(campanhas) > 10:
            linhas.append(f"… +{len(campanhas) - 10} campanhas")
        return "\n".join(linhas)

    def _format_inventory_preview(self, inventario: dict[str, int]) -> str:
        if not inventario:
            return "Inventário vazio."
        itens = sorted(inventario.items())
        linhas = [f"{item}: {qtd}x" for item, qtd in itens[:10]]
        if len(itens) > 10:
            linhas.append(f"… +{len(itens) - 10} itens")
        return "\n".join(linhas)

    @staticmethod
    def _tab_label(tab: str) -> str:
        return {
            "overview": "Visão Geral",
            "inventory": "Inventário Completo",
            "sheet": "Ficha Detalhada",
        }.get(tab, "Visão Geral")

    def _format_inventory_full(self, inventario: dict[str, int]) -> str:
        if not inventario:
            return "*Inventário vazio por enquanto.*"
        linhas = [f"• **{item}** ×{qtd}" for item, qtd in sorted(inventario.items())]
        return "\n".join(linhas)

    @staticmethod
    def _format_sheet_preview(ficha: str | None) -> str:
        if not ficha:
            return "Nenhuma ficha cadastrada."
        preview = ficha.strip()
        if len(preview) > 350:
            preview = preview[:347] + "…"
        return preview or "Nenhuma ficha cadastrada."

    @staticmethod
    def _format_sheet_block(ficha: str | None) -> str:
        if not ficha:
            return "Nenhuma ficha cadastrada ainda."
        texto = ficha.strip()
        if not texto:
            return "Nenhuma ficha cadastrada ainda."
        if len(texto) > 1900:
            texto = texto[:1900] + "…"
        return f"```\n{texto}\n```"

    def _rebuild_components(self):
        for child in list(self.children):
            self.remove_item(child)

        # O seletor de campanha é mostrado apenas na aba 'overview', conforme
        # preferência do usuário — nas outras abas removemos o select para
        # reduzir poluição visual.
        if self.current_tab == "overview":
            self.add_item(CampanhaSelect(self))
            self.add_item(self.btn_criar)
            self.add_item(self.btn_excluir)
        elif self.current_tab == "inventory":
            self.add_item(self.btn_add_item)
            self.add_item(self.btn_remove_item)
        elif self.current_tab == "sheet":
            self.add_item(self.btn_registrar_ficha)

        self.add_item(self.btn_prev_tab)
        self.btn_tab_label.label = self._tab_label(self.current_tab)
        self.add_item(self.btn_tab_label)
        self.add_item(self.btn_next_tab)
        self.add_item(self.btn_atualizar)

    async def _switch_tab(self, interaction: discord.Interaction, tab: str):
        if tab in {"inventory", "sheet"} and not self.cog.store.get_selected_campaign(self.user_id):
            await self._respond_no_selection(interaction)
            return
        self.current_tab = tab
        await self.update_view(interaction)

    async def _cycle_tab(self, interaction: discord.Interaction, direction: int):
        idx = self.TAB_ORDER.index(self.current_tab)
        new_tab = self.TAB_ORDER[(idx + direction) % len(self.TAB_ORDER)]
        await self._switch_tab(interaction, new_tab)

    def _campaign_hint(self) -> str:
        campanhas = self.cog.store.list_campaigns(self.user_id)
        if not campanhas:
            return "Crie uma campanha primeiro."
        sugestao = ", ".join(campanhas[:5])
        return sugestao[:95]

    async def _respond_no_selection(self, interaction: discord.Interaction) -> None:
        await self.update_view(interaction, status="⚠️ Selecione uma campanha na lista primeiro.")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:  # type: ignore[override]
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Esse painel é privado. Usa o seu próprio comando /painel_rpg.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Criar Campanha", style=discord.ButtonStyle.success, row=1)
    async def btn_criar(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(CriarCampanhaModal(self))

    @discord.ui.button(label="Excluir Campanha", style=discord.ButtonStyle.danger, row=1)
    async def btn_excluir(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not self.cog.store.list_campaigns(self.user_id):
            await self.update_view(interaction, status="⚠️ Crie uma campanha antes de tentar excluir.")
            return
        await interaction.response.send_modal(RemoverCampanhaModal(self))

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary, row=2)
    async def btn_prev_tab(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._cycle_tab(interaction, -1)

    @discord.ui.button(label="Modo", style=discord.ButtonStyle.secondary, disabled=True, row=2)
    async def btn_tab_label(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.update_view(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary, row=2)
    async def btn_next_tab(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._cycle_tab(interaction, 1)

    @discord.ui.button(label="+ Item", style=discord.ButtonStyle.success, row=3)
    async def btn_add_item(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not self.cog.store.get_selected_campaign(self.user_id):
            await self._respond_no_selection(interaction)
            return
        await interaction.response.send_modal(ItemModal(self, modo="add"))

    @discord.ui.button(label="- Item", style=discord.ButtonStyle.danger, row=3)
    async def btn_remove_item(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not self.cog.store.get_selected_campaign(self.user_id):
            await self._respond_no_selection(interaction)
            return
        await interaction.response.send_modal(ItemModal(self, modo="remove"))

    @discord.ui.button(label="Registrar Ficha", style=discord.ButtonStyle.primary, row=3)
    async def btn_registrar_ficha(self, interaction: discord.Interaction, _: discord.ui.Button):
        if not self.cog.store.get_selected_campaign(self.user_id):
            await self._respond_no_selection(interaction)
            return
        await interaction.response.send_modal(FichaModal(self))

    @discord.ui.button(label="🔄 Atualizar painel", style=discord.ButtonStyle.primary, row=4)
    async def btn_atualizar(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.update_view(interaction, status="Painel sincronizado com seus dados.")


class CampanhaSelect(discord.ui.Select):
    def __init__(self, dashboard: CampanhaDashboard):
        self.dashboard = dashboard
        store = dashboard.cog.store
        campanhas = store.list_campaigns(dashboard.user_id)
        selecionada = store.get_selected_campaign(dashboard.user_id)

        options: list[discord.SelectOption]
        disabled = False
        if campanhas:
            options = [
                discord.SelectOption(
                    label=nome,
                    description="Selecionada" if nome == selecionada else None,
                    default=nome == selecionada,
                )
                for nome in campanhas[:25]
            ]
        else:
            options = [
                discord.SelectOption(
                    label="Nenhuma campanha disponível",
                    value="__none",
                    description="Use 'Criar Campanha' para começar",
                    default=True,
                )
            ]
            disabled = True

        placeholder = "Selecione uma campanha" if campanhas else "Crie uma campanha primeiro"
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
            disabled=disabled,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):  # type: ignore[override]
        if not self.values or self.values[0] == "__none":
            await self.dashboard.update_view(interaction, status="⚠️ Nada selecionado.")
            return

        selecionada = self.values[0]
        try:
            self.dashboard.cog.store.set_selected_campaign(self.dashboard.user_id, selecionada)
        except ValueError as exc:
            await self.dashboard.update_view(interaction, status=f"⚠️ {exc}")
            return

        self.dashboard.current_tab = "overview"
        await self.dashboard.update_view(interaction, status=f"Campanha '{selecionada}' ativada.")


class BaseDashboardModal(discord.ui.Modal):
    def __init__(self, dashboard: CampanhaDashboard, *, title: str):
        super().__init__(title=title, timeout=None)
        self.dashboard = dashboard

    @property
    def store(self) -> CampanhaStore:
        return self.dashboard.cog.store

    async def _finish(self, interaction: discord.Interaction, message: str, *, success: bool):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)
        prefix = "✅" if success else "⚠️"
        self.dashboard.set_status(f"{prefix} {message}")
        await self.dashboard.update_view(interaction)


class CriarCampanhaModal(BaseDashboardModal):
    def __init__(self, dashboard: CampanhaDashboard):
        super().__init__(dashboard, title="Criar nova campanha")
        self.nome = discord.ui.TextInput(
            label="Nome",
            max_length=40,
            placeholder="Ex: Nexus do Porão",
        )
        self.add_item(self.nome)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            criada = self.store.create_campaign(self.dashboard.user_id, self.nome.value)
        except ValueError as exc:
            await self._finish(interaction, str(exc), success=False)
            return

        await self._finish(
            interaction,
            f"Campanha '{criada}' criada e definida como ativa.",
            success=True,
        )


class RemoverCampanhaModal(BaseDashboardModal):
    def __init__(self, dashboard: CampanhaDashboard):
        super().__init__(dashboard, title="Excluir campanha")
        placeholder = dashboard._campaign_hint()
        self.nome = discord.ui.TextInput(
            label="Nome",
            max_length=40,
            placeholder=placeholder,
        )
        self.add_item(self.nome)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.store.delete_campaign(self.dashboard.user_id, self.nome.value.strip())
        except ValueError as exc:
            await self._finish(interaction, str(exc), success=False)
            return

        await self._finish(
            interaction,
            f"Campanha '{self.nome.value.strip()}' deletada.",
            success=True,
        )


class ItemModal(BaseDashboardModal):
    def __init__(self, dashboard: CampanhaDashboard, *, modo: str):
        titulo = "Adicionar item" if modo == "add" else "Remover item"
        super().__init__(dashboard, title=titulo)
        self.modo = modo
        self.item = discord.ui.TextInput(label="Item", max_length=60)
        self.quantidade = discord.ui.TextInput(label="Quantidade", default="1", max_length=4)
        self.add_item(self.item)
        self.add_item(self.quantidade)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            quantidade = int(self.quantidade.value)
        except ValueError:
            await self._finish(interaction, "Quantidade inválida.", success=False)
            return

        if quantidade <= 0:
            await self._finish(interaction, "Use números positivos.", success=False)
            return

        try:
            campanha = self.store.require_selected_campaign(self.dashboard.user_id)
        except ValueError as exc:
            await self._finish(interaction, str(exc), success=False)
            return

        delta = quantidade if self.modo == "add" else -quantidade
        try:
            item, total = self.store.change_item_quantity(
                self.dashboard.user_id, campanha, self.item.value, delta
            )
        except ValueError as exc:
            await self._finish(interaction, str(exc), success=False)
            return

        if self.modo == "add":
            mensagem = f"Adicionado {quantidade}x {item} em '{campanha}'. Total: {total}."
        else:
            restante = "acabou" if total == 0 else f"restaram {total}x"
            mensagem = f"Removido {quantidade}x {item} de '{campanha}', {restante}."

        await self._finish(interaction, mensagem, success=True)


class FichaModal(BaseDashboardModal):
    def __init__(self, dashboard: CampanhaDashboard):
        super().__init__(dashboard, title="Registrar/atualizar ficha")
        self.texto = discord.ui.TextInput(
            label="Ficha",
            style=discord.TextStyle.paragraph,
            max_length=1500,
            placeholder="Resumo rápido da ficha...",
        )
        self.add_item(self.texto)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            campanha = self.store.require_selected_campaign(self.dashboard.user_id)
        except ValueError as exc:
            await self._finish(interaction, str(exc), success=False)
            return

        self.store.set_sheet(self.dashboard.user_id, campanha, self.texto.value)
        await self._finish(
            interaction,
            f"Ficha da campanha '{campanha}' atualizada.",
            success=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(RPG(bot))