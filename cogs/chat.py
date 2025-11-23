import discord
from discord.ext import commands
import random

# Importa de seus arquivos customizados
from constants import (
    XINGAMENTOS, RESPOSTAS, gifs_peni_parker_brava, 
    SAUDACOES, respostas_saudacao
)
from utils import obter_resposta, registrar_log

class Chat(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listener para mensagens que mencionam o bot."""
        # Ignora mensagens do próprio bot
        if message.author == self.bot.user:
            return

        # Verifica se o bot foi mencionado na mensagem
        if self.bot.user.mentioned_in(message):
            
            # 1. Verifica xingamentos
            if any(xingamento in message.content.lower() for xingamento in XINGAMENTOS):
                xingamento_encontrado = next(x for x in XINGAMENTOS if x in message.content.lower())
                resposta = f"{random.choices([f'{xingamento_encontrado.title()}!? ', ''], weights=[0.35, 0.65])[0]}{random.choice(RESPOSTAS)}"
                
                try:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} {resposta}", delete_after=5)
                    await message.channel.send(random.choice(gifs_peni_parker_brava), delete_after=4.5)
                except discord.Forbidden:
                    registrar_log(f"Sem permissão para deletar xingamento em '{message.guild.name}'", 'warning')
                    # Apenas responde à mensagem original
                    await message.reply(resposta, delete_after=5)
                    await message.channel.send(random.choice(gifs_peni_parker_brava), delete_after=4.5)
                except Exception as e:
                    registrar_log(f"Erro ao responder xingamento: {e}", 'error')

            # 2. Verifica saudações
            elif any(saudacao in message.content.lower() for saudacao in SAUDACOES):
                saudacao_encontrada = next(s for s in SAUDACOES if s in message.content.lower())
                
                if saudacao_encontrada == "bom dia":
                    await message.reply(random.choice(["Bom dia! Ou seria 'bom café'? Porque sem café, nem funciona direito.", "Bom dia.", "Bom dia, me faz um café?"]), mention_author=True)
                else:
                    await message.reply(f"{random.choice(respostas_saudacao)}", mention_author=True)
            
            # 3. Fallback para OpenAI
            else:
                # Pega o token do OpenAI da configuração do bot
                openai_token = self.bot.config['openai_token']
                if not openai_token:
                    registrar_log("Token da OpenAI não configurado.", 'error')
                    await message.reply("Tô sem cabeça pra isso, desculpa mano.")
                    return
                    
                # Mostra "digitando..."
                async with message.channel.typing():
                    resposta = obter_resposta(message.content, openai_token)
                    await message.reply(resposta)

# Função 'setup' obrigatória
async def setup(bot: commands.Bot):
    await bot.add_cog(Chat(bot))