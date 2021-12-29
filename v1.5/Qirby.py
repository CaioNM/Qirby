#from functools import _Descriptor, update_wrapper
import discord
import nextcord
import random
from nextcord import voice_client
from nextcord import member
from nextcord.channel import VoiceChannel
from nextcord.embeds import Embed
from nextcord.ext import commands, tasks
from nextcord.ext.commands.core import command
from itertools import cycle
from io import BytesIO
import psutil
#Imports que talvez sejam usados no futuro, não sei
from typing import ValuesView
import asyncio
from nextcord.user import User
import json
import DiscordUtils
#from discord_slash import SlashCommand
# Testes:
import youtube_dl
import os
#C:\Users\caion\AppData\Local\Programs\Python\Python38-32\Lib\site-packages\DiscordUtils

#Instalaçoes Manuais:
#pip install DiscordUtils[voice]
#pip install DiscordUtils

#Prefixo dos comando
# OBS.: tem um modo de mudar o prefixo pra um servidor específico, mas por padrão é melhor deixar o mesmo, caso mude de ideia: Episode 6 - Server Prefixes!!!
# Link: https://youtu.be/glo9R7JGkRE
client = commands.Bot(command_prefix='/')

music = DiscordUtils.Music()

#Remove o comando help pre-definido pela biblioteca para poder usar personalizados
client.remove_command("help")

#slash = SlashCommand(client, sync_commands=True)

'''
Coisas Legais pra atualizações futuras
Observação: Se o Qirby ficar instalado em mts bots, usar o Shards vai melhorar o desempenho:
client = commands.AutoShardedBot(shard_count=10, command_prefix='/')

Comando de ligar ou desligar outros comandos se eu decidir:
- https://www.youtube.com/watch?v=hPEDR30SZ8M&list=PLW4Cg4G29vz0enf3ZeqWPPd_-Z3YK8mH4&index=34

Comando pra pegar emojis de outros servidores:
- https://www.youtube.com/watch?v=sskPcO1WLnE&list=PLW4Cg4G29vz0enf3ZeqWPPd_-Z3YK8mH4&index=35
'''

#Lista de Status diferentes do Kirby
status = cycle([
    "Kirby's Return to Dream Land",
    'Oi :D',
    'So no meme :P',
    'Ouvindo Música',
    'Dizendo como a Bebel é linda',
    'Assistindo todos os filmes do Homem-Aranha, de novo',
    '/help | /ajuda... ou chama o Moura ai',
    'Observando você 👁',
    'https://youtu.be/dQw4w9WgXcQ'
])

'''
To do:
- Mensagens de afeto
- Comandos de erro
- Colocar nome e descrição nos comandos
'''

#Teste de funcionamento do bot
@client.event
async def on_ready():
    print('Funcionando!')
    status_swap.start()
    uptimeCounter.start()

#Loop de status, recebe a lista acima e muda a cada 120 segundos
@tasks.loop(seconds=120)
async def status_swap():
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=next(status)))

#Colocar "aliases" no argumento do client de uma função, reduz o tamanho do comando, por exemplo, 
# em vez de escrever /play, o user escreve /p e o comando funciona perfeitamente
@client.command()
#Condiçao pra nao spamar comando, recebe a quantidade de vezes que o usuário pode mandar o comando e depois que esse limite é alcançado
#entra num cooldown de X segundos, no caso "@commands.cooldown(<quantidade>, <seg de espera>, commands.cooldowns.BucketType.user)"
@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
#O argumento "ctx" é usado quando o bot manda mensagens de texto
async def ping(ctx):
    await ctx.send(f'Pong!  🏓\nPing de {round(client.latency * 1000)} ms!')

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
    embed = nextcord.Embed(title="Meus status! :D")
    embed.add_field(name="Dias:", value=td, inline=True)
    embed.add_field(name="Horas:", value=th, inline=True)
    embed.add_field(name="Minutos:", value=tm, inline=True)
    embed.add_field(name="Segundos:", value=ts, inline=True)
    embed.add_field(name="CPU:", value=f"{psutil.cpu_percent()}%", inline=True)
    embed.add_field(name="RAM:", value=f"{psutil.virtual_memory()[2]}%", inline=True)
    await ctx.send(embed=embed)

@client.command(aliases=['join', 'summon', 'entra', 'oi'])
async def entre(ctx):
    voicetrue = ctx.author.voice
    if voicetrue is None:
        return await ctx.send('Mas eu nao quero ficar sozinho :(')
    await ctx.author.voice.channel.connect()
    await ctx.send('Entrei :D')

@client.command(aliases=['disconnect', 'd', 'leave', 'sair', 'tchau'])
async def saia(ctx):
    voicetrue = ctx.author.voice
    mevoicetrue = ctx.guild.me.voice
    if voicetrue is None:
        return await ctx.send('Você não está na call')
    if mevoicetrue is None:
        return await ctx.send('Mas eu nao to em um canal... ue')
    await ctx.voice_client.disconnect()
    await ctx.send('Sai D:')

#play
@client.command(aliases=['p'])
async def play(ctx, *, url):
    player = music.get_player(guild_id=ctx.guild.id)
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        song = await player.play()
        await ctx.send(f"Tocando `{song.name}`!")
    else:
        song = await player.queue(url, search=True)
        await ctx.reply(f"`{song.name}` foi adicionado a fila")

@client.command(aliases=['playlist'])
async def queue(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await ctx.send(f"{'   ➡️   '.join([song.name for song in player.current_queue()])}")

@client.command()
async def pause(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.pause()
    await ctx.send(f'`{song.name}` foi pausado(a)! :pause_button:')

@client.command(aliases=['toque'])
async def resume(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.resume()
    await ctx.send(f'`{song.name}` voltou a tocar! :play_pause:')

@client.command()
async def loop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.toggle_song_loop()
    if song.is_looping:
        return await ctx.send(f'{song.name} está em loop! :infinity:')
    else:
        return await ctx.send(f'{song.name} não está em loop! :octagonal_sign:')

@client.command()
async def tocando(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = player.now_playing()
    if song is None:
        await ctx.send('Não tem nada tocando...')
    await ctx.send(song.name)

@client.command()
async def remove(ctx, index):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.remove_from_queue(int(index))
    await ctx.send(f'Removi `{song.name}` da playlist!')

@client.command()
async def skip(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    data = await player.skip(force=True)
    song = player.now_playing()
    if len(data) == 2:
        await ctx.send(f"Pulei `{song.name}`! ⏩")

@client.command()
async def stop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    player.queue = []
    await player.stop()
    await ctx.send("Parei a música e limpei a playlist! 🟥 ")  

'''
@slash.slash(description="Mostra a latência do bot")
async def latencia(ctx):
    await ctx.send(f'Ping de {round(client.latency * 1000)} ms!')
'''

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

'''
#Os comandos abaixo servem pra kickar e banir do servidor, não da chamada... Achei interessante então fiz, mas é poderoso demais,
#não vou aplicar na versão final, por agora. Quem sabe tenha um de disconectar que tenha a mesma estrutura...
#Sintaxe: /kick(ou ban) <@usuário> <possível justificatica, se houver>
@client.command()
async def kick(ctx, member:discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member.member} foi chutado pra fora!')
@client.command()
async def ban(ctx, member:discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member.member} foi **BANIDO!**')
#Comando que retira o ban de um usuário
#Sintaxe: /unban <NomeUsuário#Tag>
@client.command()
async def unban(ctx, *, member):
    membros_banidos = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')
    for ban_entry in membros_banidos:
        user = ban_entry.user
        if(user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            #Menciona um usuário :D
            await ctx.send(f'{user.mention} foi desbanido do servidor')
            return
'''

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
        await ctx.send('Limpo! 🧹')

'''
#Essa parte do código não é tao importante, teoriacamente ele mutaria um usuário do server criando um cargo, mas n funciona e eu nao acho tao necessária agora.
# Acho que nem ta funcionando direito pra ser sincero e eu não quero arrumar. Tem algumas partes importantes tipo mandar mensagem privada, que eu vou acabar usando
# depois, e criação/atribuição de cargo ao user. Por enquanto vai ficar aqui, quem sabe eu tire depois. Caso mude de ideia no futuro, tmb tem o comando de unban.
#Link: https://youtu.be/l_pxUTDlzaM
@client.command()
async def mute(ctx, member:discord.Member, *, reason='Não justificado'):
    #Checagem de permissão:
    if(not ctx.author.guild_permissions.manage_messages):
        await ctx.send('Você não tem a permissão necessária para isso...')
        return
    guild = ctx.guild
    muteRole = discord.utils.get(guild.roles, name="muted")
    #Cria um novo cargo
    if not muteRole:
        muteRole = await guild.create_role(name="Muted")
    #As permissões do cargo criado:
        for channel in guild.channels:
            await ctx.send('Nenhum cargo foi achado. Criando....')
            await channel.set_permissions(muteRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)
    #Adiciona cargo ao usuário:
    await member.add_roles(muteRole, reason = reason)
    
    #Manda mensagem privada pro usuário, isso é bom :D
    await member.send(f'Você foi mutado do **{guild.name}** | Justificativa: **{reason}**')
'''
    
#Comando de ajuda, depois atualizar e mandar mensagem privada com os comandos pra quem pediu
@client.command(aliases=['ajuda'])
@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
async def help(ctx):
    embed = nextcord.Embed(title="Ajuda do Qirby! 🚑", description='uiuuuu uiuuuu')
    for command in client.walk_commands():
        description = command.description
        if not description or description is None or description == "":
            description = "Sem descrição ainda"
        embed.add_field(name=f"`/{command.name}{command.signature if command.signature is not None else ''}`", value=description)
    await ctx.author.send(embed=embed)
    await ctx.message.add_reaction("✅")
    

@client.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    await update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

@client.event
async def on_message(message):
    if message.author.bot == False:
        with open('users.json', 'r') as f:
            user = json.load(f)
    
        await update_data(user, message.author)
        await add_xp(user, message.author, 5)
        await level_up(user, message.author, message)

        with open('users.json', 'w') as f:
            json.dump(user, f, indent=4)

        await client.process_commands(message)


async def update_data(users, user):
    if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']['xp'] = 0
        users[f'{user.id}']['level'] = 1

async def add_xp(users, user, exp):
    users[f'{user.id}']['xp'] += exp

async def level_up(users, user, message):
    with open('levels.json', 'r') as g:
        levels = json.load(g)
    xp = users[f'{user.id}']['xp']
    lvl_start = users[f'{user.id}']['level']
    lvl_end = int(xp ** (1/4))
    if lvl_start < lvl_end:
        await message.channel.send(f'🎉 {user.mention} subiu de nível!!! Nível - {lvl_end} 🎉')
        users[f'{user.id}']['level'] = lvl_end

@client.command(aliases=['nivel','lvl'])
async def level(ctx, member: nextcord.Member = None):
    if not member:
        id = ctx.message.author.id
        with open('users.json', 'r') as f:
            users = json.load(f)
        lvl = users[str(id)]['level']
        await ctx.send(f' Você está no nível {lvl}!')
    else:
        id = member.id
        with open('users.json', 'r') as f:
            users = json.load(f)
        lvl = users[str(id)]['level']
        await ctx.send(f'{member} está no nível {lvl}!')

#Mensagens de possíveis erros de usuarios nos comandos:
@bolaoito.error
async def bolaoito_error(ctx, error):
    #Se o usuario não mandar uma pergunta:
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Se você não pergutar, não posso responder :eye:")

@clear.error
async def clear_error(ctx, error):
    #Se o usuario não passar um número de mensagens a ser apagadas:
    if isinstance(error, commands.BadArgument):
        await ctx.send("Por favor, digite o **número** de mensagens que quer apagar.")

#Mensagem de erro em caso spamming, mostra os segundos restantes para poder mandar mensagem
@ping.error
@clear.error
@bolaoito.error
async def error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        mensagem = ":x:**Relaxa brother**:x:, sem spammar... Manda mais daqui {:.2f} seg :clock5:" .format(error.retry_after)
        await ctx.send(mensagem)
'''
@client.error
async def command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Desculpa, não conheço esse comando... :pensive:")
'''

#Token:
client.run('ODg3ODQzNjM4OTg4NjQwMzA2.YUKC0g.wumQs4Hr8qjwYc8dSN9bnbWtelE')