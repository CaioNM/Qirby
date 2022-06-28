from ast import alias
import re
from turtle import color
from idna import valid_contextj
import nextcord
from nextcord.ext import commands
import wavelink
import datetime
from wavelink.ext import spotify
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel


client = commands.Bot(command_prefix='/')

class ControlPanel(nextcord.ui.View):
  def __init__(self, vc, ctx):
        super().__init__()
        self.vc = vc
        self.ctx = ctx
    
  @nextcord.ui.button(label="Pause/Play", style=nextcord.ButtonStyle.blurple)
  async def resume_and_pause(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    if not interaction.user == self.ctx.author:
      return await interaction.response.send_message("Você não pode usar o painel de outra pessoa! ❌", ephemeral=True)
    for child in self.children:
      child.disabled = False
    if self.vc.is_paused():
      await self.vc.resume()
      await interaction.message.edit(content="Voltou a tocar! ⏯️", view=self)
    else:
      await self.vc.pause()
      await interaction.message.edit(content="Pausado! ⏸️", view=self)

  @nextcord.ui.button(label="Playlist", style=nextcord.ButtonStyle.green)
  async def queue(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    if not interaction.user == self.ctx.author:
      return await interaction.response.send_message("Você não pode usar o painel de outra pessoa! ❌", ephemeral=True)
    for child in self.children:
      child.disabled = False
    button.disabled = True
    if self.vc.queue.is_empty:
      return await interaction.response.send_message("A playlist ta vazia ❌", ephemeral=True)
    
    em = nextcord.Embed(title="🎶 Playlist do Qirby 🎶", color=nextcord.Color.magenta())
    queue = self.vc.queue.copy()
    songCount = 0

    for song in queue:
      songCount += 1
      em.add_field(name=f"Música nº {str(songCount)}.", value=f"`{song}`")
    await interaction.message.edit(embed=em, view=self)
    
  @nextcord.ui.button(label="Skip", style=nextcord.ButtonStyle.blurple)
  async def skip(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    if not interaction.user == self.ctx.author:
      return await interaction.response.send_message("Você não pode usar o painel de outra pessoa! ❌", ephemeral=True)
    for child in self.children:
      child.disabled = False
    button.disabled = True
    if self.vc.queue.is_empty:
      return await interaction.response.send_message("A playlist ta vazia ❌", ephemeral=True)
      

    try:
      await self.vc.stop()
    except Exception:
      return await interaction.response.send_message("A playlist ta vazia ❌", ephemeral=True)
     
    
  @nextcord.ui.button(label="Disconnect", style=nextcord.ButtonStyle.red)
  async def disconnect(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
    if not interaction.user == self.ctx.author:
      return await interaction.response.send_message("Você não pode usar o painel de outra pessoa! ❌", ephemeral=True)
    for child in self.children:
      child.disabled = True
    await self.vc.disconnect()
    await interaction.message.edit(content="Sai, até a próxima! 👋", view=self)

async def node_connect():
  await client.wait_until_ready()
  await wavelink.NodePool.create_node(bot=client, host='lavalink.oops.wtf', port=443, password='www.freelavalink.ga', https=True, spotify_client=spotify.SpotifyClient(client_id="19103c83806b46918d9a49eb18f5bb7c", client_secret="d2031ed7a5b3456a93168c70f0fe2242"))

@client.event
async def on_ready():
  print('massa!')
  client.loop.create_task(node_connect())  

@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
  print(f"Node {node.identifier} is ready!")

@client.command(description='Mostra meu tempo de resposta')
async def ping(ctx):
    await ctx.send(f'Pong!  🏓\nPing de {round(client.latency * 1000)} ms!')
    await ctx.message.add_reaction("🏓")


@client.event
async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.YouTubeTrack, reason):
      try:
        ctx = player.ctx
        vc: player = ctx.voice_client
        
      except nextcord.HTTPException:
        interaction = player.interaction
        vc: player = interaction.guild.voice_client
    
      if vc.loop:
        return await vc.play(track)
    
      if vc.queue.is_empty:
        pass

      next_song = vc.queue.get()
      await vc.play(next_song)
      try:
        embe = nextcord.Embed(description=f"Tocando: [{next_song.title}]({next_song.uri})",color=nextcord.Color.magenta())
        embe.set_image(url=next_song.thumbnail)
        await ctx.send(embed=embe)
        await ctx.message.add_reaction("🎶")
        #await ctx.send(f"Now playing: {next_song.title}")
      except nextcord.HTTPException:
        await interaction.send(f"Now playing: {next_song.title}")


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
    await ctx.message.add_reaction("😊")
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro! :D")
  else:
    vc: wavelink.Player = ctx.voice_client
    
  if vc.queue.is_empty and not vc.is_playing():
    await vc.play(search)
    embe = nextcord.Embed(description=f"Tocando: [{search.title}]({search.uri})",color=nextcord.Color.magenta())
    embe.set_image(url=search.thumbnail)
    await ctx.send(embed=embe)
    await ctx.message.add_reaction("🎶")
  else:
    await vc.queue.put_wait(search)
    emb = nextcord.Embed(description=f"[{search.title}]({search.uri}) foi adicionado a playlist!",color=nextcord.Color.magenta())
    await ctx.send(embed=emb)
    await ctx.message.add_reaction("🎶")
    
  vc.ctx = ctx
  setattr(vc, "loop", False)

#SlashCommands, pra quando for necessário:
'''
@client.slash_command(description="Toca muisiquinha", guild_ids=[761657280457342997])
async def play(interaction: Interaction, search: str = SlashOption(description="Nome da música")):
  search = await wavelink.YouTubeTrack.search(query=search, return_first=True)
  if not interaction.guild.voice_client:
    vc: wavelink.Player = await interaction.GuildChannel.connect(cls=wavelink.Player)
  elif not getattr(interaction.author.voice, "channel", None):
    await interaction.send(f"{interaction.author.mention}, você preicsa entrar no canal primeiro! :D")
  else:
    vc: wavelink.Player = interaction.guild.voice_client

  if vc.queue.is_empty and not vc.is_playing():
    await vc.play(search)
    embe = nextcord.Embed(description=f"Now playing [{search.title}]({search.uri}) ",color=nextcord.Color.magenta())
    embe.set_image(url=search.thumbnail)
    await interaction.send(embed=embe)
  else:
    await vc.queue.put_wait(search)
    emb = nextcord.Embed(description=f"Added [{search.title}]({search.uri}) to the queue.",color=nextcord.Color.magenta())
  
    emb.set_image(url=search.thumbnail)
    await interaction.send(embed=emb)
  vc.interaction = interaction
  if vc.loop: return
  setattr(vc, "loop", False) 
'''

@client.command()
async def pause(ctx: commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("❌")
    
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
  else:
    vc: wavelink.player = ctx.voice_client
    if vc.is_playing() is False:
      embed=nextcord.Embed(description="Não foi possível pausar",color=nextcord.Color.magenta())
      await ctx.send(embed=embed)
      return await ctx.message.add_reaction("❌")  
    else:
      await vc.pause()
      embed=nextcord.Embed(description=f"`{vc.track.title}` foi pausado, use `/resume` para voltar a tocar",color=nextcord.Color.magenta())
      await ctx.send(embed=embed)
      return await ctx.message.add_reaction("⏸️")
    
      
@client.command(aliases=["unpause"])
async def resume(ctx:commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("❌")
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.resume()
  embed=nextcord.Embed(description=f"`{vc.track.title}` voltou a tocar!",color=nextcord.Color.magenta())
  await ctx.send(embed=embed)
  return await ctx.message.add_reaction("⏯️")

@client.command()
async def skip(ctx:commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("❌")
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.stop()
  await ctx.message.add_reaction("⏩")


@client.command()
async def stop(ctx:commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("❌")
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.stop()
  embed=nextcord.Embed(description="Parei a música e limpei a playlist!",color=nextcord.Color.magenta())
  await ctx.send(embed=embed)
  await ctx.message.add_reaction("🟥")
  await vc.disconnect()

@client.command(aliases=['disconnect', 'd', 'leave', 'sair', 'tchau'])
async def saia(ctx:commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
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

@client.command()
async def splay(ctx: commands.Context, *, search: str):
        if not ctx.voice_client:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        elif not getattr(ctx.author.voice, "channel", None):
            return await ctx.send("join a voice channel first lol")
        else:
            vc: wavelink.Player = ctx.voice_client
            
        if vc.queue.is_empty and not vc.is_playing():
            try:
                track = await spotify.SpotifyTrack.search(query=search, return_first=True)
                await vc.play(track)
                await ctx.send(f'Playing `{track.title}`')
            except Exception as e:
                await ctx.send("Please enter a spotify **song url**.")
                return print(e)
        else:
            await vc.queue.put_wait(search)
            await ctx.send(f'Added `{search.title}` to the queue...')
        vc.ctx = ctx
        try:
            if vc.loop: return
        except Exception:
            setattr(vc, "loop", False) 

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


#Token:
client.run("token")

