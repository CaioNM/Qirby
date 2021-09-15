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
      await ctx.send('Entrei! Oláaaaaa :D')

#Comando para disconectar:  
  @commands.command()
  async def saia(self, ctx):
    await ctx.voice_channel.disconnect()
    #Comando para o bot enviar mensagem:
    await ctx.send('Tchau tchau! Até a próxima... 👋')
  
#Comando para tocar música:
  @commands.command()
  async def p(self, ctx):
    ctx.voice_client.stop()
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 - reconnect_delay_max 2', 'options': '-vn'}
    YDL_OPTIONS = {'format': "bestaudio"}
    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(url, download = False)
      url2 = info['formats'][0]['url']
      source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
      vc.play(souce)
      await ctx.send('Tocando: ', cogs, '🎶')

#Comando para pausar a música:
  @commands.command()
  async def pause(self, ctx):
    await ctx.voice_client.pause()
    await ctx.send('Pausado! ⏸️')

#Comando para voltar a tocar:
  @commands.command()
  async def play(self, ctx):
    await ctx.voice_client.resume()
    await ctx.send('Tocando de novo! 🎶')

#Comando Mostrar os comandos:
  @commands.command()
  async def help(self, ctx):
    await ctx.send('Oi, ' + "<@{}>".format(userid) + ' tudo bem?\nEstes são os meus comandos até o momento:\n1. Antes de tudo, envie **/entre** para me chamar ao canal e eu chegarei rapidinho\n2. Use **/p** seguido do link da música no youtube para toca-la\n3. Use **/pause** para pausar a sua música\n4. Use **/play** para retomar uma música que esta pausada\n5. E por fim, use **/saia** para que eu vá embora!\nPor enquanto é isto, estou sempre a disposição, lembre-se de enviar **/help** caso esqueça de algum comando, e até a próxima! 😘')


  def setup(client):
    client.add_cog(music(client))