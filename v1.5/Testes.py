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
    

@tasks.loop(seconds=120)
async def status_swap():
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=next(status)))

@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
@client.slash_command(description='Mostra meu tempo de resposta')
async def ping(interaction: Interaction):
    await interaction.response.send_message(f'Pong!  🏓\nPing de {round(client.latency * 1000)} ms!')

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

@client.slash_command(description='Mostra meu tempo de atividade')
async def stats(ctx:nextcord.Interaction):
    global ts, tm, th, td
    embed = nextcord.Embed(title="🕓 Meus status! :D 🕓", color=nextcord.Color.magenta())
    embed.add_field(name="Dias:", value=td, inline=True)
    embed.add_field(name="Horas:", value=th, inline=True)
    embed.add_field(name="Minutos:", value=tm, inline=True)
    embed.add_field(name="Segundos:", value=ts, inline=True)
    embed.add_field(name="CPU:", value=f"{psutil.cpu_percent()}%", inline=True)
    embed.add_field(name="RAM:", value=f"{psutil.virtual_memory()[2]}%", inline=True)
    await ctx.send(embed=embed)


@client.slash_command(description='Me coloca na chamada')
async def entre(ctx:nextcord.Interaction):
    voicetrue = ctx.user.voice
    if voicetrue is None:
        return await ctx.send('Mas eu nao quero ficar sozinho 😔')
    await ctx.user.voice.channel.connect()
    emb = nextcord.Embed(description=f"Entrei, oláaaa 😊",color=nextcord.Color.magenta())
    await ctx.send(embed=emb)
    
@client.slash_command()
async def slashteste(ctx: nextcord.Interaction):
  await ctx.response.send_message("teste feito, funcionando")

@client.slash_command(name="repeat", description="repete oq vc mandar")
async def repeat(interaction: Interaction, message:str):
  await interaction.response.send_message(f'vc disse `{message}`')

#Token:
client.run('token')