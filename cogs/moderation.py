import discord
from discord.ext import commands
from discord import app_commands

from utils import registrar_log, send_temp_followup

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='limpar', description='Apaga mensagens (requer permissão)')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def limpar_mensagens(self, interaction: discord.Interaction, quantidade: int):
        """Apaga um número de mensagens no canal."""
        # Limita a quantidade para evitar abusos/erros
        quantidade = max(1, min(quantidade, 300))
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=quantidade)
        
        # Usa a função de followup temporário
        await send_temp_followup(
            interaction, 
            f"Apaguei {len(deleted)} mensagensss. Espero que tenha sido útil boboca :p", 
            delete_after=3
        )

    @limpar_mensagens.error
    async def limpar_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Você não tem permissão para gerenciar mensagens!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ocorreu um erro: {error}", ephemeral=True)


    @app_commands.command(name='ban', description='Banir um usuário.')
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.User, motivo: str = "Motivo não fornecido."):
        """Bane um usuário do servidor."""
        # A lógica original de verificação de nome de usuário é
        # insegura e não é uma boa prática. A permissão (acima) é o correto.
        # Eu removi a verificação de 'vezkalin' e substituí por permissões.
        
        try:
            member = await interaction.guild.fetch_member(user.id)
            if member == interaction.user:
                await interaction.response.send_message("Você não pode se banir.", ephemeral=True)
                return
            if member == self.bot.user:
                await interaction.response.send_message("Eu não posso me banir.", ephemeral=True)
                return
            
            await interaction.guild.ban(member, reason=f"Banido por {interaction.user.name}: {motivo}")
            registrar_log(f"[BAN] {user} foi banido por {interaction.user}.", 'info')
            await interaction.response.send_message(f'{user.mention} foi banido do servidor. Boboca não tem vez aqui :p', ephemeral=True)
        
        except discord.Forbidden:
            await interaction.response.send_message('Eu não tenho permissão para banir este usuário.', ephemeral=True)
        except discord.HTTPException as error:
            await interaction.response.send_message(f'Erro ao banir: {error}', ephemeral=True)

    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Você não tem permissão para banir membros!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ocorreu um erro: {error}", ephemeral=True)

# Função 'setup' obrigatória
async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))