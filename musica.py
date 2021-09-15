import discord
from discord.ext import commands
import youtube_dl

class musica(commands.Cog):
  def __init__(self, client):
    self.client = client

#Comando para entrar na call:
  @commands.command()
  async def entre(self, ctx):
    if ctx.author.voice is None:
      #Comando para o bot enviar mensagem:
      await ctx.send('Mas você não está em nenhum canal... :(')
    voice_channel = ctx.author.voice.voice_channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
      await ctx.send('Entrei! :D')

#Comando para disconectar:  
  @commands.command()
  async def saia(self, ctx):
    await ctx.voice_channel.disconnect()
    #Comando para o bot enviar mensagem:
    await ctx.send('Tchau tchau! Até a próxima... 👋')
  
#Comando para tocar música:
  @commands.command()
  async def play(self, ctx):
    ctx.voice_client.stop()
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 - reconnect_delay_max 2', 'options': '-vn'}
    YDL_OPTIONS = {'format': "bestaudio"}
    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(url, download = False)
      url2 = info['formats'][0]['url']
      source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
      vc.play(souce)
      await ctx.send('Tocando', source, '🎶')