from pydoc import cli
import re
from turtle import color
from idna import valid_contextj
import nextcord
from nextcord.ext import commands
import wavelink
import datetime

client = commands.Bot(command_prefix='/')

#Muitos erros precisam ser corrigidos aqui em baixo :( 
'''
class ControlPanel(nextcord.ui.View):
  def __init__(self, vc, ctx):
    super().__init__()
    self.vc = vc
    self.ctx = ctx

  @nextcord.ui.button(label="⏯️", style=nextcord.ButtonStyle.gray)
  async def resume_e_pause(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    if not interaction.user == self.ctx.author:
      return await interaction.response.send_message("Você não pode fazer isso, roda o comando sozinho", ephemeral=True)
    for child in self.children:
      child.disabled = False
    if self.vc.is_playing() is True:
      await self.vc.resume()
      await interaction.message.edit(content="Voltou a tocar", view=self)
    else:
      await self.vc.pause()
      await interaction.message.edit(content="Pausado", view=self)
  
  @nextcord.ui.button(label="🎶", style=nextcord.ButtonStyle.blurple)
  async def queue(self, button: nextcord.Button, interaction: nextcord.Interaction):
    if not interaction.user == self.ctx.author:
      return await interaction.response.send_message("Você não pode fazer isso, roda o comando sozinho", ephemeral=True)
    for child in self.children:
      child.disabled = False
    button.disabled = False
    if self.vc.queue.is_empty:
      return await interaction.response.send_message("Playlist vazia", ephemeral=True)
    
    em = nextcord.Embed(title="Playlist", color=nextcord.Color.magenta())
    queue = self.vc.queue.copy()
    songCount = 0

    for song in queue:
      songCount += 1
      em.add_field(name=f"Número {str(songCount)}", value=f"{song}")
    await interaction.message.edit(embed=em, view=self)

  @nextcord.ui.button(label="⏭", style=nextcord.ButtonStyle.blurple)
  async def skip(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    if not interaction.user == self.ctx.author:
      return await interaction.response.send_message("Você não pode fazer isso, roda o comando sozinho", ephemeral=True)
    for child in self.children:
      child.disabled = False
    button.disabled = True
    if self.vc.queue.is_empty:
      return await interaction.response.send_message("Playlist vazia", ephemeral=True)
    
    try:
      next_song = self.vc.queue.get()
      await self.vc.play(next_song)
      await interaction.message.edit(content=f"Tocando `{next_song}`", view=self)
    except Exception:
      return await interaction.response.send_message("A playlist ta vazia!", ephemeral=True)
  
  @nextcord.ui.button(label="🛑", style=nextcord.ButtonStyle.red)
  async def disconnect(self, button: nextcord.ui.button, interaction: nextcord.Interaction):
    if not interaction.user == self.ctx.author:
      return await interaction.response.send_message("Você não pode fazer isso, roda o comando sozinho", ephemeral=True)
    for child in self.children:
      child.disabled = True
    await self.vc.disconnect()
    await interaction.message.edit(content="Saí :D", view=self)
'''

@client.event
async def on_ready():
  print('massa!')
  client.loop.create_task(node_connect())  

@client.command(description='Mostra meu tempo de resposta')
async def ping(ctx):
    await ctx.send(f'Pong!  🏓\nPing de {round(client.latency * 1000)} ms!')
    await ctx.message.add_reaction("🏓")

@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
  print(f"Node {node.identifier} is ready!")

async def node_connect():
  await client.wait_until_ready()
  await wavelink.NodePool.create_node(bot=client, host='lavalinkinc.ml', port=443, password='incognito', https=True)

@client.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track, reason):
  ctx = player.ctx
  vc: player = ctx.voice_client
    
  if vc.loop:
    return await vc.play(track)
    
  next_song = vc.queue.get()
  await vc.play(next_song)
  emb = nextcord.Embed(description=f"Now playing **{next_song.title}**",color=nextcord.Color.magenta())
  emb.set_image(url=next_song.thumbnail)
  await ctx.send(embed=emb) 


@client.command(aliases=['join', 'summon', 'entra', 'oi'])
async def entre(ctx):
    voicetrue = ctx.author.voice
    if voicetrue is None:
        await ctx.message.add_reaction("😔")
        return await ctx.send('Mas eu nao quero ficar sozinho :(')
    await ctx.author.voice.channel.connect()
    vc: wavelink.Player = ctx.voice_client
    await ctx.message.add_reaction("😊")
    await ctx.send('Entrei, oláaaa :D')
    

@client.command(aliases=['p'])
async def play(ctx: commands.Context, *, search: wavelink.YouTubeTrack):
  if not ctx.voice_client:
    vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro! :D")
  else:
    vc: wavelink.Player = ctx.voice_client
    
  if vc.queue.is_empty and not vc.is_playing():
    await vc.play(search)
    embe = nextcord.Embed(description=f"Now playing [{search.title}]({search.uri}) ",color=nextcord.Color.magenta())
    embe.set_image(url=search.thumbnail)
    await ctx.send(embed=embe)
  else:
    await vc.queue.put_wait(search)
    emb = nextcord.Embed(description=f"Added [{search.title}]({search.uri}) to the queue.",color=nextcord.Color.magenta())
  
    emb.set_image(url=search.thumbnail)
    await ctx.send(embed=emb)
    
  vc.ctx = ctx
  setattr(vc, "loop", False)


@client.command()
async def pause(ctx: commands.Context):
  if not ctx.voice_client:
    return await ctx.send("No music")
  elif not getattr(ctx.author.voice, "channel", None):
    return await ctx.send("Não ta num canal")
  else:
    vc: wavelink.player = ctx.voice_client
    if vc.is_playing() is False:
      await ctx.send("sla")    
    else:
      await vc.pause()
      await ctx.send("pausado")
    
      
@client.command()
async def resume(ctx:commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description=f"Não tem nada tocando...",color=nextcord.Color.magenta())
    return await ctx.send(embed=embed)
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro! :D")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.resume()
  await ctx.send(f"{vc.track.title} voltou a tocar")

@client.command()
async def stop(ctx:commands.Context):
  if not ctx.voice_client:
    return await ctx.send("nada tocando")
  elif not getattr(ctx.author.voice, "channel", None):
    return await ctx.send("nao ta num canal")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.stop()
  await ctx.send("parou de tocar")
  await vc.disconnect()

@client.command()
async def d(ctx:commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    return await ctx.send("nao ta num canal")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.disconnect()
  await ctx.send("xau")

@client.command()
async def loop(ctx: commands.Context):
  if not ctx.voice_client:
    return await ctx.send("naum to num canal")
  elif not ctx.author.voice:
    return await ctx.send("entra num canal primeiro")
  else:
    vc: wavelink.Player = ctx.voice_client
  try:
    vc.loop ^= True
  except Exception:
    setattr(vc, "loop", False)
  if vc.loop:
    return await ctx.send("Loop habilitado")
  else:
    return await ctx.send("Loop desabilitado")

@client.command()
async def queue(ctx: commands.Context):
  if not ctx.voice_client:
    return await ctx.send("naum to num canal")
  elif not ctx.author.voice:
    return await ctx.send("entra num canal primeiro")
  else:
    vc: wavelink.Player = ctx.voice_client
  if vc.queue.is_empty:
    return await ctx.send("Fila vazia")
  em = nextcord.Embed(title="Playlist", color=nextcord.Color.magenta())
  queue = vc.queue.copy()
  song_count = 0
  for song in queue:
    song_count += 1
    em.add_field(name=f"Número {song_count}", value=f"`{song.title}`")
  return await ctx.send(embed=em)

@client.command()
async def volume(ctx: commands.Context, volume: int):
  if not ctx.voice_client:
    return await ctx.send("Não to num canal")
  elif not getattr(ctx.voice_client, "channel", None):
    return await ctx.send("vc nem ta num canal")
  else:
    vc: wavelink.Player = ctx.voice_client
  
  if volume>100:
    return await ctx.send("Isso é muuuuito alto")
  elif volume<0:
    return await ctx.send("Isso é muuuuito baixo")
  await ctx.send(f"Volume mudado para `{volume}%`")
  return await vc.set_volume(volume)

@client.command()
async def tocando(ctx: commands.Context):
  if not ctx.voice_client:
    return await ctx.send("Não to num canal")
  elif not getattr(ctx.voice_client, "channel", None):
    return await ctx.send("vc nem ta num canal")
  else:
    vc: wavelink.Player = ctx.voice_client
  if not vc.is_playing():
    return await ctx.send("Nada tocando agora")
  
  em = nextcord.Embed(title=f"Tocando: **{vc.track.title}**", description=f"Artista: **{vc.track.author}**", color=nextcord.Color.magenta())
  em.add_field(name="Duração:", value=f"{str(datetime.timedelta(seconds=vc.track.length ))}")
  em.add_field(name="Source:", value=f"Link: [Click me]({str(vc.track.uri)})")
  return await ctx.send(embed=em)
 
#Aqui também
'''
@client.command()
async def painel(ctx: commands.Context):
  if not ctx.voice_client:
    return await ctx.send("Não to num canal")
  elif not getattr(ctx.voice_client, "channel", None):
    return await ctx.send("vc nem ta num canal")
  else:
    vc: wavelink.Player = ctx.voice_client
  if not vc.is_playing():
    return await ctx.send("Nada tocando agora")
  
  em = nextcord.Embed(title=f"Painel de música", description="Controla a música pelos botões", color=nextcord.Color.magenta())
  view = ControlPanel(vc, ctx)
  await ctx.send(embed=em, view=view)
'''

#Token:
client.run("Token")

