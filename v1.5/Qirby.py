import nextcord
import random
from nextcord.ext import commands, tasks
from nextcord.ext.commands.core import command
from itertools import count, cycle
from io import BytesIO
import psutil
import aiohttp
import urllib
import aiosqlite
#from replit import db
import asyncio
import json
from easy_pil import *
#C:\Users\caion\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\DiscordUtils
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

#Remove o comando help pre-definido pela biblioteca para poder usar personalizados
client.remove_command("help")

#slash = SlashCommand(client, sync_commands=True)

'''
Coisas Legais pra atualizações futuras:
Observação: Se o Qirby ficar instalado em mts servers, usar o Shards vai melhorar o desempenho:
client = commands.AutoShardedBot(shard_count=10, command_prefix='/')
'''

#Lista de Status diferentes do Kirby
status = cycle([
    'Oi :D',
    'Ouvindo Música',
    'Dizendo como a Bebel é linda',
    ';help',
    '👁️',
])

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

#Teste de funcionamento do bot
@client.event
async def on_ready():
    print('Qirby está online!')
    status_swap.start()
    uptimeCounter.start()
    setattr(client, "db", await aiosqlite.connect('level.db'))
    await asyncio.sleep(3)
    async with client.db.cursor() as cursor:
        await cursor.execute("CREATE TABLE IF NOT EXISTS levels (level INTEGER, xp INTEGER, user INTEGER, guild)")
    client.loop.create_task(node_connect())  

@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
  print(f"Node {node.identifier} is ready!")

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
  except nextcord.HTTPException:
    await interaction.send(f"Now playing: {next_song.title}")
    

#Loop de status, recebe a lista acima e muda a cada 120 segundos
@tasks.loop(seconds=120)
async def status_swap():
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=next(status)))

#Colocar "aliases" no argumento do client de uma função, reduz o tamanho do comando, por exemplo, 
# em vez de escrever /play, o user escreve /p e o comando funciona perfeitamente
@client.command(description='Mostra meu tempo de resposta')
#Condiçao pra nao spamar comando, recebe a quantidade de vezes que o usuário pode mandar o comando e depois que esse limite é alcançado
#entra num cooldown de X segundos, no caso "@commands.cooldown(<quantidade>, <seg de espera>, commands.cooldowns.BucketType.user)"
@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
#O argumento "ctx" é usado quando o bot manda mensagens de texto
async def ping(ctx):
    await ctx.send(f'Pong!  🏓\nPing de {round(client.latency * 1000)} ms!')
    await ctx.message.add_reaction("🏓")

#Dados do Bot:
ts = 0
tm = 0
th = 0
td = 0

@tasks.loop(seconds=2.0)
async def uptimeCounter():
    global ts, tm, th, td
    ts += 2
    if ts == 60:
        ts = 0
        tm += 1
        if tm == 60:
            tm = 0
            th += 1
            if th == 24:
                th = 0
                td += 1
#Essa parte garante que o contador nao vai começar antes do bot estar online
@uptimeCounter.before_loop
async def beforeUptimeCounter():
    await client.wait_until_ready()

@client.command()
async def stats(ctx):
    global ts, tm, th, td
    embed = nextcord.Embed(title="Meus status! :D", color=nextcord.Color.magenta())
    embed.add_field(name="Dias:", value=td, inline=True)
    embed.add_field(name="Horas:", value=th, inline=True)
    embed.add_field(name="Minutos:", value=tm, inline=True)
    embed.add_field(name="Segundos:", value=ts, inline=True)
    embed.add_field(name="CPU:", value=f"{psutil.cpu_percent()}%", inline=True)
    embed.add_field(name="RAM:", value=f"{psutil.virtual_memory()[2]}%", inline=True)
    await ctx.send(embed=embed)
    await ctx.message.add_reaction("🕓")



@client.command(aliases=['join', 'summon', 'entra', 'oi'])
async def entre(ctx):
    voicetrue = ctx.author.voice
    if voicetrue is None:
        await ctx.message.add_reaction("😔")
        return await ctx.send('Mas eu nao quero ficar sozinho :(')
    await ctx.author.voice.channel.connect()
    await ctx.message.add_reaction("😊")
    await ctx.send('Entrei, oláaaa :D')
    

@client.command(aliases=['disconnect', 'd', 'leave', 'sair', 'tchau'])
async def saia(ctx:commands.Context):
  if not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.disconnect()
  await ctx.send("Sai, até a próxima!")
  await ctx.message.add_reaction("👋") 

#play
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

@client.command()
async def pause(ctx: commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("🔇")
    
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
      embed=nextcord.Embed(description=f"[{vc.track.title}]({vc.track.uri}) foi pausado, use `/resume` para voltar a tocar",color=nextcord.Color.magenta())
      await ctx.send(embed=embed)
      return await ctx.message.add_reaction("⏸️")

@client.command(aliases=["unpause"])
async def resume(ctx:commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("🔇")
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.resume()
  embed=nextcord.Embed(description=f"[{vc.track.title}]({vc.track.uri}) voltou a tocar!",color=nextcord.Color.magenta())
  await ctx.send(embed=embed)
  return await ctx.message.add_reaction("⏯️") 

@client.command()
async def loop(ctx: commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("🔇")
  elif not ctx.author.voice:
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
  else:
    vc: wavelink.Player = ctx.voice_client
  try:
    vc.loop ^= True
  except Exception:
    setattr(vc, "loop", False)
  if vc.loop:
    embed=nextcord.Embed(description=f"[{vc.track.title}]({vc.track.uri}) está em loop!",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("♾️")
  else:
    embed=nextcord.Embed(description=f"Loop foi desabilitado!",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("🛑")

@client.command()
async def tocando(ctx: commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    await ctx.message.add_reaction("🔇")
  elif not getattr(ctx.author.voice, "channel", None):
    await ctx.send(f"{ctx.author.mention}, você preicsa entrar no canal primeiro!")
    return await ctx.message.add_reaction("❌")
  else:
    vc: wavelink.Player = ctx.voice_client
  if not vc.is_playing():
    embed=nextcord.Embed(description=f"Não tem nada tocando agora...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    await ctx.message.add_reaction("🔇")
  
  em = nextcord.Embed(title=f"Tocando: **{vc.track.title}**", description=f"Artista: **{vc.track.author}**", color=nextcord.Color.magenta())
  em.add_field(name="Duração:", value=f"{str(datetime.timedelta(seconds=vc.track.length ))}")
  em.add_field(name="Source:", value=f"Link: [Click me]({str(vc.track.uri)})")
  await ctx.message.add_reaction("🎧") 
  return await ctx.send(embed=em)

@client.command()
async def skip(ctx:commands.Context):
  if not ctx.voice_client:
    embed=nextcord.Embed(description="Não tem nada tocando...",color=nextcord.Color.magenta())
    await ctx.send(embed=embed)
    return await ctx.message.add_reaction("🔇")
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
    return await ctx.message.add_reaction("🔇")
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
  
#Comando bola oito funciona como aquela "bola mágica" que responde uma pergunta que o usuário faça
@client.command(aliases=['8ball','8b'])
@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
#Recebe a chamada do comando e uma pergunta com o atributo "question"
#Estrutura do comando: "/bolaoito(ou variaçoes) <pergunta><'?'> é opcional
async def bolaoito(ctx, *, question):
    #Lista de respostas possíveis
    responses = ["É certo que sim.",
                "Sem dúvidas.",
                "Sim - confia.",
                "Provavelmente.",
                "Parece uma boa ideia.",
                "Sim.",
                "Os sinais indicam que sim.",
                "Você é fraco, lhe falta concentração, tenta de novo.",
                "Pergunta depois na moral, to com preguiça agora.",
                "É melhor você não saber.",
                "Vish sei não :(",
                "Se concentra ai e tenta de novo.",
                "Não conte com isso.",
                "Não.",
                "As vozes na minha cabeça tão falando que não.",
                "Não parece uma boa ideia.",
                "Duvido muito."]
    #Pega a pergunta e com o random, escolhe uma das respostas da lista acima:
    await ctx.send(f'Pergunta: {question}\n:8ball:: {random.choice(responses)}')
    await ctx.message.add_reaction("🎱")

@client.command()
async def pp(ctx):
    pp = ["8D - Mini pipi ):",
                "8=D",
                "8====D",
                "8=======D",
                "8==========D",
                "8=============D",
                "8================D - **MEGA PIPI** 💪"]
    #Pega a pergunta e com o random, escolhe uma das respostas da lista acima:
    await ctx.reply(f'Tamanho da 🍆 GIROMBA 🍆: {random.choice(pp)}')
    await ctx.message.add_reaction("🍆")

@client.command()
async def casada(ctx):
    casada = ["0% - **RESPEITOSO**",
                "10% comedor",
                "20% comedor",
                "30% comedor",
                "40% comedor",
                "50% - Só as vezes",
                "60% comedor",
                "70% comedor",
                "80% comedor",
                "90% comedor",
                "100% - Comedor de casadas",
                "10000% - Protejam as mamães o **COME CASADAS ESTÁ A SOLTA**"]
    #Pega a pergunta e com o random, escolhe uma das respostas da lista acima:
    await ctx.reply(f'Qual a chance de ser um comedor de casadas? {random.choice(casada)}')
    await ctx.message.add_reaction("💪")

@client.command(aliases=['lukk','pedro'])
async def noia(ctx):
    noia = ["0% - Nada noia :D",
                "10% noia",
                "25% noia",
                "50% noia - Meio Noia",
                "75% noia",
                "100% - Completamente noia",
                "1000% - **MEGA NOIA**"]
    #Pega a pergunta e com o random, escolhe uma das respostas da lista acima:
    await ctx.reply(f'Quão noia você é? {random.choice(noia)}')
    await ctx.message.add_reaction("😎")

#Comando /clear vai apagar um número especíco de mensagens no canal de texto, por padrão é 10
#O usuário pode escolher a quantidade, desde que não passe de 100
@client.command()
@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
async def clear(ctx, quantidade=11):
    #Essa linha de código é importante, so permite que o usuário com uma permissão específica apague as mensagens, talvez possa ser usado com cargos?
    #Para banir seria "ctx.author.guild_permissions.ban_members", por exemplo. Kick = kick_members
    quantidade = quantidade+1
    if quantidade > 101:
        await ctx.send('Não posso deletar mais de 100 mensagens, desculpe :(')
    else:
        await ctx.channel.purge(limit=quantidade)
        await ctx.send('**Limpo!** 🧹')
        await ctx.message.add_reaction("🧹")
    
    
#Comando de ajuda, depois atualizar e mandar mensagem privada com os comandos pra quem pediu
@client.command(aliases=['ajuda'])
@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
async def help(ctx):
    await ctx.author.send('**AJUDA DO QIRBY**\nuiuuuu uiuuuuu\n**Lista dos meus comandos:**\n\n- `/ping` -> Mostra meu ping, meu tempo de resposta...\n- `/stats` -> Mostra meus status, o tempo que estou ligado e os dados da máquina que me hospeda\n- `/entre [join, summon, entra, oi]` -> Me coloca na chamada :D\n- `/saia [disconnect, d, leave, sair, tchau]` -> Me manda embora da conversa :(\n- `/play [p] <link ou nome>` -> Toco a música que quiser\n- `/queue [playlist, q]` -> Mostra todas as músicas que armazenei, desde a que está tocando agora, até a última da fila\n- `/pause` -> Pausa a música\n- `/resume [toque]` -> Volta a tocar a música que estava pausada\n- `/loop` - Coloca a música atual em modo loop, ou seja, vai ficar repetindo até que alguem pule ou mande parar\n- `/tocando [playing]` -> Mostra o nome da música atual\n- `/remove <numero>` -> Tira uma das músicas da playlist que criei, mas deve ser colocado um numero a menos, por exemplo, se você quiser tirar a segunda música da playlist, o comando seria: `/remove 1`, já que a contagem começa com 0\n- `/skip` -> Pula pra próxima música\n- `/stop` -> Para de tocar e limpa completamente a playlist\n- `/bolaoito [8ball, 8b] <pergunta>` -> Responde mágicamente uma pergunta de sim ou não que fizer para ela\n- `/pp` -> 👀')
    await ctx.author.send('\n- `/clear <número>` -> Apaga um certo número de mensagens do chat de texto, se não for especificado, 10 mensagens serão apagadas por padrão\n- `/help [ajuda]` -> **Sou eeeu! :D**, vou mandar uma mensagem pra você com todos os meus comandos!\n- `/level [nivel, lvl] <Membro>` -> Mostro o nível de alguem do server, a especificação so é necessária se quiser ver o nível de outra pessoa, para isso, precisa menciona-la. Mas se não mencionar, será exibido o seu nível\n- `/emoji <url> <nível>` -> Rouba, de outro server, ou adiciona um emoji no server, colocando primeiro o link de origem e logo depois, o nome que deseja\n- `/meme` -> Envia um meme no chat\n- `/bebel` -> 🥰\n- `/role [roll] <numero de dados> <numero do dado>` -> Rola quantos dados, de qualquer número, que você quiser, por exemplo, para rolar 4d5 seria `/role 4 5`\n- `/jogodavelha [jdv, v, velha] <Player 1> <Player 2>` -> Como o próprio nome ja diz, é o jogo da velha... Pra começar o jogo, basta chamar o comando e marcar ambos os jogadores logo depois. O jogo funciona com o comando abaixo\n- `/jogar [j] <posição>` -> Um complemento do jogo da velha, você usa esse comando pra dizer pra mim onde quer jogar...\n\nBom, é isso... Qualquer dúvida pode chamar o <@319850719228329985> caso tenha alguma dúvida. Até a próxima :D')
    await ctx.message.add_reaction("🚑")


#Nova versão do sistema de nível:
@client.event
async def on_message(message):
    if message.author.bot:
        return
    await client.process_commands(message)
    author = message.author
    async with client.db.cursor() as cursor:
        await cursor.execute("SELECT xp FROM levels WHERE user = ?", (author.id,))
        xp = await cursor.fetchone()
        await cursor.execute("SELECT level FROM levels WHERE user = ?", (author.id,))
        level = await cursor.fetchone()
        
        if not xp or not level:
            await cursor.execute("INSERT INTO levels(level, xp, user) VALUES (?, ?, ?)", (0, 0, author.id,))

        try:
            xp = xp[0]
            level = level[0]
        except TypeError:
            xp = 0
            level = 0

        if level < 5:
            xp += random.randint(1,3)
            await cursor.execute("UPDATE levels SET xp = ? WHERE user = ?", (xp, author.id))
        else:
            rand = random.randint(1, (level//4))
            if rand == 1:
                xp += random.randint(1,3)
                await cursor.execute("UPDATE levels SET xp = ? WHERE user = ?", (xp, author.id))
        if xp >= 100:
            level = level+1
            await cursor.execute("UPDATE levels SET level = ? WHERE user = ?", (level, author.id,))
            await cursor.execute("UPDATE levels SET xp = ? WHERE user = ?", (0, author.id,))
            await message.channel.send(f'🎉 {author.mention} subiu de nível!!! Nível - {level} 🎉')
    await client.db.commit()

@client.command(aliases=['lvl'])
async def level(ctx, member:nextcord.Member = None):
    if member is None:
        member = ctx.author
    async with client.db.cursor() as cursor:
        await cursor.execute("SELECT xp FROM levels WHERE user = ?", (member.id,))
        xp = await cursor.fetchone()
        await cursor.execute("SELECT level FROM levels WHERE user = ?", (member.id,))
        level = await cursor.fetchone()
        
        if not xp or not level:
            await cursor.execute("INSERT INTO levels(level, xp, user) VALUES (?, ?, ?)", (0, 0, member.id,))
        try:
            xp = xp[0]
            level = level[0]
        except TypeError:
            xp = 0
            level = 0
    
    userData = {
        "name": f"{member.name}#{member.discriminator}",
        "xp": xp,
        "level": level,
        "next_level_xp": 100,
        "porcentagem": xp,
    }

    background = Editor(Canvas((900, 300), color="#FF69B4"))
    profile_picture = await load_image_async(str(member.avatar.url))
    profile = Editor(profile_picture).resize((150, 150)).circle_image()
    
    fonte = Font.poppins(size=40)
    fonte_size = Font.poppins(size=30)

    card_right_shape = [(600, 0), (750, 300), (900,300), (900, 0)]
    background.polygon(card_right_shape, color="#FFFFFF")
    background.paste(profile, (30, 30))

    background.rectangle((30, 220), width=650, height=40, color="#FFFFFF", radius=30,)
    background.bar((30, 220), max_width=650, height=40, percentage=userData['porcentagem'], color="#F61E61", radius=30,)
    background.text((200,40), userData['name'], font=fonte_size, color="#FFFFFF")

    background.rectangle((200, 100), width=350, height=2, fill="#FFFFFF")
    background.text(
        (200, 130), 
        f"Nível - {userData['level']} | XP - {userData['xp']}/{userData['next_level_xp']}",
        font = fonte_size,
        color="#FFFFFF",)
    arquivo = nextcord.File(fp=background.image_bytes, filename="levelcard.png")
    await ctx.send(file=arquivo)


@client.command(aliases=['lb', 'lvlboard'])
async def leaderboard(ctx):
    async with client.db.cursor() as cursor:
        await cursor.execute("SELECT level, xp, user FROM levels WHERE guild=? ORDER BY level DESC, xp DESC LIMIT 5", (ctx.guild.id,))
        data = await cursor.fetchall()
        if data:
            em = nextcord.Embed(title='LeaderBoard')
            count = 0
            for table in data:
                count += 1
                user = ctx.guild.get_member(table[2])
                em.add_field(name=f"{count}. {user.name}", value=f"Level - **{table[0]}** | XP - **{table[1]}**", inline=False)
            return await ctx.send(embed=em)
        return await ctx.send('no bitches?')


@client.command()
async def emoji(ctx, url:str, *,name):
    guild = ctx.guild
    async with aiohttp.ClientSession() as ses:
        async with ses.get(url) as r:
            try:
                imgOrGif = BytesIO(await r.read())
                bValue = imgOrGif.getvalue()
                if r.status in range(200, 299):
                    emoji = await guild.create_custom_emoji(image=bValue, name=name)
                    await ctx.send('Emoji adicionado! :D')
                    await ctx.message.add_reaction("😋")
                    await ses.close()
                else:
                    await ctx.send(f'Não funcionou D: | {r.status}')
                    await ctx.message.add_reaction("❌")
            except nextcord.HTTPException:
                await ctx.send('o arquivo é  P E S A D Ã O')
                await ctx.message.add_reaction("❗")

@client.command()
async def meme(ctx):
    memeApi = urllib.request.urlopen('https://meme-api.herokuapp.com/gimme')
    memeData = json.load(memeApi)

    memeUrl = memeData['url']
    memeName = memeData['title']
    memePoster = memeData['author']
    memeSub = memeData['subreddit']
    memeLink = memeData['postLink']

    embed = nextcord.Embed(title=memeName, color=nextcord.Color.magenta())
    embed.set_image(url=memeUrl)
    embed.set_footer(text=f'Meme by: {memePoster} | Subreddit: {memeSub} | Post: {memeLink}')
    await ctx.send(embed=embed)
    await ctx.message.add_reaction("🤣")

@client.command()
async def gatinho(ctx):
    c = 0
    while True:
        emoji = client.get_emoji('<931359027898761287>')
        await ctx.send(f'{emoji}')
        c+=1
        if c==5:
            break 

@client.command()
async def horademimir(ctx):
    await ctx.send('Boa noite princesa, te amo <3, tenha uma boa noite de sono :D')
    await ctx.message.add_reaction("😴")
    
@client.command()
async def bebel(ctx):
    await ctx.send('😍 <@544290205226762244> 😍\nO amor da minha vida, a garota mais linda do planeta')
    await ctx.message.add_reaction("🥰")

@client.command()
async def acabou(ctx):
    await ctx.send('E é aqui, que a gente vai terminar por hoje, muito obrigada por todos que participaram :)')
    await ctx.message.add_reaction("🙏")
    
@client.command()
async def primeiroencontro(ctx):
    await ctx.send('Oi meu amor, vc descobriu o segredo... Parabens! :D\nMeu amor, eu deixei esse pequeno segredinho nas linhas de código do bot para te dizer o quanto eu te amo... Esse bot foi contruido principalmente pra vc... eu fiz ele em sua homenagem. Vc com certeza é a pessoa que eu mais amo nesse mundo... Amo seu jeito, seu cabelo, o jeito que vc sorri, como se veste, seus olhos... tudo, tudo em vc é perfeito. Vc com certeza é a melhor pessoa que ja apareceu na minha vida. A cada vez que eu recebo o seu bom dia no whatsapp, a cada dia que eu recebo a benção de poder ver seu sorriso e escutar sua voz, eu me apaixono mais e mais. Eu nao tenho palavras pra expressar o quao importante vc eh pra mim e como eu sou grato por ter vc... Vc eh incrivel bel, te amo muitao minha princesa... Espero poder passar o resto da minha vida com vc. Espero tmb que vc goste desse botzinho e que vc se divirta muito tocando suas musicas favoritas. Obrigado por tudo Bel, te amo :)')
    await ctx.message.add_reaction("❤️")

@client.command(aliases=['roll'])
async def role(ctx, quantidade=0, *, numero=0):
    i=1
    await ctx.message.add_reaction("🎲")
    while i<=quantidade:
        i+=1
        await ctx.send(f'{quantidade}d{numero} - **[{random.randint(1, numero)}]**')

player1 = ""
player2 = ""
vez = ""
gameOver = True
tabuleiro = [] 

vencedor = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

@client.command(aliases=['jdv', 'v', 'velha'])
async def jogodavelha(ctx, p1:nextcord.Member, p2:nextcord.Member):
    global player1, player2, vez, gameOver, count
    await ctx.message.add_reaction("🎮")

    if gameOver:
        global tabuleiro
        tabuleiro = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        vez = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        # Manda o tabuleiro
        line = ""
        for x in range(len(tabuleiro)):
            if x == 2 or x == 5 or x == 8:
                line += " " + tabuleiro[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + tabuleiro[x]

        # Determina quem vai primeiro
        num = random.randint(1, 2)
        if num == 1:
            vez = player1
            await ctx.send("É a vez do(a) <@" + str(player1.id) + ">!")
        elif num == 2:
            vez = player2
            await ctx.send("É a vez do(a) <@" + str(player2.id) + ">'!")
    else:
        await ctx.send('Já tem alguem jogando! Espera esse jogo acabar')

@client.command(aliases=['j'])
async def jogar(ctx, pos: int):
    global vez, player1, player2, tabuleiro, count, gameOver

    if not gameOver:
        mark = ""
        if vez == ctx.author:
            if vez == player1:
                mark = ":regional_indicator_x:"
            elif vez == player2:
                mark = ":o2:"
            if 0 < pos < 10 and tabuleiro[pos - 1] == ":white_large_square:" :
                tabuleiro[pos - 1] = mark
                count += 1

                # Mandando o tabuleiro
                line = ""
                for x in range(len(tabuleiro)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + tabuleiro[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + tabuleiro[x]

                checarVencedor(vencedor, mark)
                if gameOver == True:
                    await ctx.send(mark + " **ganhou!**")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("**Empatou!**")

                # Trocando turno
                if vez == player1:
                    vez = player2
                elif vez == player2:
                    vez = player1
            else:
                await ctx.send('Escolha uma posição entre 1 e 9 que ainda não foi jogada :D')
        else:
            await ctx.send('Não é a sua vez!')
    else:
        await ctx.send('Comece um jogo usando o comando `/jogodavelha`!')

def checarVencedor(vencedor, mark):
    global gameOver
    for condicao in vencedor:
        if tabuleiro[condicao[0]] == mark and tabuleiro[condicao[1]] == mark and tabuleiro[condicao[2]] == mark:
            gameOver = True

@client.command(aliases=['on', 'off', 'liga', 'desliga'])
async def toggle(ctx, *, command):
    command = client.get_command(command)
    if ctx.author.id != 319850719228329985:
        ctx.send('Você não tem autorização pra isso.')
        await ctx.message.add_reaction("❌")
        return
    if command == None:
        ctx.send('Não conheço esse comando...')
        await ctx.message.add_reaction("🤔")
    elif ctx.command == command:
        await ctx.send('Você não pode desativar esse comando...!')
        await ctx.message.add_reaction("❌")
    else:
        command.enabled = not command.enabled
        situacao = 'habilitado' if command.enabled else 'desabilitado'
        await ctx.send(f'Comando `{command.qualified_name}` foi **`{situacao}`**')

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
client.run('token')