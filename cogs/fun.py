import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

from utils import registrar_log, buscar_gif
from constants import dados_regex # Para ignorar rolagens de dados no listener

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listener para a palavra 'duvido'."""
        # Ignora o bot, menções e comandos
        if (message.author == self.bot.user or 
            self.bot.user.mentioned_in(message) or
            message.content.startswith('/')):
            return
        
        # Ignora rolagens de dados (tratadas pelo RPG)
        if dados_regex.match(message.content.lower()):
            return

        if 'duvido' in message.content.lower():
            try:
                await message.reply("Meu p## no seu ouvido KKKKKKKKKKK, mentira, eu não sou real", mention_author=True, delete_after=3.58)
                await message.channel.send('https://tenor.com/bbPNvlEPvvL.gif', delete_after=3.3)
            except discord.Forbidden:
                pass # Ignora se não puder responder

    @app_commands.command(name='spam_singed_gremista', description='Spamma singed gremista no pv de alguém.')
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: i.user.id) # Cooldown de 60s por usuário
    async def singed_gremista(self, interaction: discord.Interaction, user: discord.User, vezes: int):
        """Spamma o usuário com uma imagem."""
        if vezes > 20:
            await interaction.response.send_message("Coloquei um limite de 20. Não vamos exagerar, né? 😅", ephemeral=False)
            vezes = 20 # Limita a 20
        elif vezes < 1:
            await interaction.response.send_message("Tem que ser pelo menos 1 vez.", ephemeral=True)
            return

        await interaction.response.send_message(f"Vou tentar mandar {vezes} singeds gremistas. :p", ephemeral=False)
        
        # Pega o token do Tenor
        tenor_token = self.bot.config['tenor_token']
        gif_url = buscar_gif(tenor_token, 'peni parker happy', 3)
        
        count = 0
        for i in range(vezes):
            try:
                await user.send('https://static-cdn.jtvnw.net/jtv_user_pictures/d00aa4af-f29b-4030-b844-5d1d576f7a1d-profile_image-300x300.png')
                count += 1
                await asyncio.sleep(1) # Pausa para evitar rate limit
            except discord.errors.Forbidden:
                await interaction.followup.send(f"Não consegui enviar mensagens para {user.mention}. Ele(a) me bloqueou? 😢", ephemeral=False)
                break
            except Exception as e:
                registrar_log(f"Erro ao spammar singed: {e}", 'error')
                break

        # Envia a mensagem de desculpas
        try:
            if count > 0:
                await user.send('Desculpa pelos Singeds Gremistas, mas alguém realmente quis fazer você passar por essa experiência :p')
                if gif_url:
                    await user.send(gif_url)
        except discord.errors.Forbidden:
            pass # Usuário já bloqueou, não há o que fazer

        # Resposta final no canal
        if count == 1:
            await interaction.followup.send(f"{count} singed gremista enviado para {user.mention}.", ephemeral=False)
        elif count > 1:
            await interaction.followup.send(f"{count} singeds gremistas enviados para {user.mention}.", ephemeral=False)

    @singed_gremista.error
    async def on_singed_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Trata erros do comando singed, especialmente cooldown."""
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Calma aí, apressado! Tenta de novo em {error.retry_after:.1f} segundos.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Deu um erro estranho: {error}", ephemeral=True)
            registrar_log(f"Erro no /singed_gremista: {error}", 'error')

    @app_commands.command(name="moeda", description="Jogue uma moeda e veja o resultado (cara ou coroa).")
    async def moeda(self, interaction: discord.Interaction):
        """Joga uma moeda."""
        resultado = random.choice(["Cara", "Coroa"])
        registrar_log(f"[MOEDA] {interaction.user} jogou moeda: {resultado}", 'info')
        await interaction.response.send_message(f"🪙 **Resultado:** `{resultado}`")

# Função 'setup' obrigatória
async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))