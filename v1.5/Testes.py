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

@client.command(aliases=['join', 'summon', 'entra', 'oi'])
async def entre(ctx):
    voicetrue = ctx.author.voice
    if voicetrue is None:
        await ctx.message.add_reaction("😔")
        return await ctx.send('Mas eu nao quero ficar sozinho :(')
    await ctx.author.voice.channel.connect()
    await ctx.message.add_reaction("😊")
    await ctx.send('Entrei, oláaaa :D')
    

@client.command()
async def play(ctx: commands.Context, *, search: wavelink.YouTubeMusicTrack):
  if not ctx.voice_client:
    vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
  elif not getattr(ctx.author.voice, "channel", None):
    return await ctx.send("not in a channel")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.play(search)
  await ctx.send(f"playin: `{search.title}`")

@client.command()
async def pause(ctx: commands.Context):
  if not ctx.voice_client:
    return await ctx.send("No music")
  elif not getattr(ctx.author.voice, "channel", None):
    return await ctx.send("Não ta num canal")
  else:
    vc: wavelink.player = ctx.voice_client
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
 
#Token:
client.run('ODg3ODQzNjM4OTg4NjQwMzA2.YUKC0g.wumQs4Hr8qjwYc8dSN9bnbWtelE')