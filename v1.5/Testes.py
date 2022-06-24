from pydoc import cli
import nextcord
from nextcord.ext import commands
import wavelink

client = commands.Bot(command_prefix='/')

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
  await ctx.send(f"Now playing: {next_song.title}")


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
    return await ctx.send("You need to join a VC to play music.")
  else:
    vc: wavelink.Player = ctx.voice_client
    
  if vc.queue.is_empty and not vc.is_playing():
    await vc.play(search)
    await ctx.send(f"Now Playing: {search.title}")
  else:
    await vc.queue.put_wait(search)
    await ctx.send(f"Added `{search.title}` to the queue")
    
  vc.ctx = ctx
  setattr(vc, "loop", False)
    
  print("Playing a song")


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
    return await ctx.send("nada tocando")
  elif not getattr(ctx.author.voice, "channel", None):
    return await ctx.send("nao ta num canal")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.resume()
  await ctx.send("voltou a tocar")

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
  em = nextcord.Embed(title="Playlist")
  queue = vc.queue.copy()
  song_count = 0
  for song in queue:
    song_count += 1
    em.add_field(name=f"Número {song_count}", value=f"`{song.title}`")
  return await ctx.send(embed=em)

#Token:
client.run('ODg3ODQzNjM4OTg4NjQwMzA2.YUKC0g.wumQs4Hr8qjwYc8dSN9bnbWtelE')

