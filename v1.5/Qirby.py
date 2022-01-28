#from functools import _Descriptor, update_wrapper
from asyncio.events import TimerHandle
import discord
import nextcord
import random
from nextcord import voice_client
from nextcord import member
from nextcord.channel import VoiceChannel
from nextcord.colour import Color
from nextcord.embeds import Embed
from nextcord.ext import commands, tasks
from nextcord.ext.commands.core import command
from itertools import count, cycle
from io import BytesIO
import psutil
import time
import aiohttp
import urllib
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
Coisas Legais pra atualizações futuras:
Observação: Se o Qirby ficar instalado em mts bots, usar o Shards vai melhorar o desempenho:
client = commands.AutoShardedBot(shard_count=10, command_prefix='/')

'''
'''
    'Oi :D',
    'So no meme :P',
    'Ouvindo Música',
    'Dizendo como a Bebel é linda',
    'Assistindo todos os filmes do Homem-Aranha, de novo',
    '/help | /ajuda... ou chama o Moura ai',
    'https://youtu.be/dQw4w9WgXcQ'
'''
#Lista de Status diferentes do Kirby
status = cycle([
    "O que aconteceu com a sua irmã, Arthur?",
    "Qual foi a última vez que você viu os olhos da Larissa, Levy?",
    "Espero que sinta falta da Rafaela, Maethe",
    "Alexandre... Cadê a Ester?",
    "Eu sempre estive observando",
    "O tempo de vocês tá acabando",
    "Quem é a Corvo?",
    "Onde tá o Elias?",
    "Você sente falta da sua irmã, Rafael?",
    "Você se lembra da Ana, Pandora? Ela ainda fala com você na sua cabeça?",
    "Corram.",
    "Cadê a Isis?",
    '👁️',
])

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
async def saia(ctx):
    voicetrue = ctx.author.voice
    mevoicetrue = ctx.guild.me.voice
    if voicetrue is None:
        return await ctx.send('Você não está na call')
    if mevoicetrue is None:
        return await ctx.send('Mas eu nao to em um canal... ue')
    await ctx.voice_client.disconnect()
    await ctx.send('Sai, até a próxima!')
    await ctx.message.add_reaction("👋") 

#play
@client.command(aliases=['p'])
async def play(ctx, *, url):
    player = music.get_player(guild_id=ctx.guild.id)
    mevoicetrue = ctx.guild.me.voice
    if mevoicetrue is None:
        await ctx.author.voice.channel.connect()
        await ctx.message.add_reaction("😊")
    if not player:
        player = music.create_player(ctx, ffmpeg_error_betterfix=True)
    if not ctx.voice_client.is_playing():
        await player.queue(url, search=True)
        song = await player.play()
        await ctx.send(f"Tocando `{song.name}`!")
        await ctx.message.add_reaction("🎶")
    else:
        song = await player.queue(url, search=True)
        await ctx.reply(f"`{song.name}` foi adicionado a fila")
        await ctx.message.add_reaction("🎶") 

@client.command(aliases=['playlist', 'q'])
async def queue(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    await ctx.send(f"{'   ➡️   '.join([song.name for song in player.current_queue()])}")

@client.command()
async def pause(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.pause()
    await ctx.send(f'`{song.name}` foi pausado(a)! :pause_button:')
    await ctx.message.add_reaction("⏸️") 

@client.command(aliases=['toque'])
async def resume(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.resume()
    await ctx.send(f'`{song.name}` voltou a tocar!')
    await ctx.message.add_reaction("⏯️") 

@client.command()
async def loop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = await player.toggle_song_loop()
    if song.is_looping:
        await ctx.message.add_reaction("♾️") 
        return await ctx.send(f'{song.name} está em loop! :infinity:')
        
    else:
        await ctx.message.add_reaction("🛑") 
        return await ctx.send(f'{song.name} não está em loop! 🛑')

@client.command(aliases=['playing'])
async def tocando(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    song = player.now_playing()
    if song is None:
        await ctx.send('Não tem nada tocando...')
    await ctx.send(song.name)
    await ctx.message.add_reaction("🎧") 

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
        await ctx.send(f"Pulei `{song.name}`!")
        await ctx.message.add_reaction("⏩")

@client.command()
async def stop(ctx):
    player = music.get_player(guild_id=ctx.guild.id)
    player.queue = []
    await player.stop()
    await ctx.send("Parei a música e limpei a playlist!")
    await ctx.message.add_reaction("🟥") 

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
        await ctx.send('**Limpo!** 🧹')
        await ctx.message.add_reaction("🧹")

@client.command()
async def tormenta(ctx):
    await ctx.send('https://tormenta.analuiza84.repl.co/')
    
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
    await ctx.author.send('**AJUDA DO QIRBY**\nuiuuuu uiuuuuu\n**Lista dos meus comandos:**\n\n- `/ping` -> Mostra meu ping, meu tempo de resposta...\n- `/stats` -> Mostra meus status, o tempo que estou ligado e os dados da máquina que me hospeda\n- `/entre [join, summon, entra, oi]` -> Me coloca na chamada :D\n- `/saia [disconnect, d, leave, sair, tchau]` -> Me manda embora da conversa :(\n- `/play [p] <link ou nome>` -> Toco a música que quiser\n- `/queue [playlist, q]` -> Mostra todas as músicas que armazenei, desde a que está tocando agora, até a última da fila\n- `/pause` -> Pausa a música\n- `/resume [toque]` -> Volta a tocar a música que estava pausada\n- `/loop` - Coloca a música atual em modo loop, ou seja, vai ficar repetindo até que alguem pule ou mande parar\n- `/tocando [playing]` -> Mostra o nome da música atual\n- `/remove <numero>` -> Tira uma das músicas da playlist que criei, mas deve ser colocado um numero a menos, por exemplo, se você quiser tirar a segunda música da playlist, o comando seria: `/remove 1`, já que a contagem começa com 0\n- `/skip` -> Pula pra próxima música\n- `/stop` -> Para de tocar e limpa completamente a playlist\n- `/bolaoito [8ball, 8b] <pergunta>` -> Responde mágicamente uma pergunta de sim ou não que fizer para ela\n- `/pp` -> 👀')
    await ctx.author.send('\n- `/clear <número>` -> Apaga um certo número de mensagens do chat de texto, se não for especificado, 10 mensagens serão apagadas por padrão\n- `/help [ajuda]` -> **Sou eeeu! :D**, vou mandar uma mensagem pra você com todos os meus comandos!\n- `/level [nivel, lvl] <Membro>` -> Mostro o nível de alguem do server, a especificação so é necessária se quiser ver o nível de outra pessoa, para isso, precisa menciona-la. Mas se não mencionar, será exibido o seu nível\n- `/emoji <url> <nível>` -> Rouba, de outro server, ou adiciona um emoji no server, colocando primeiro o link de origem e logo depois, o nome que deseja\n- `/meme` -> Envia um meme no chat\n- `/bebel` -> 🥰\n- `/role [roll] <numero de dados> <numero do dado>` -> Rola quantos dados, de qualquer número, que você quiser, por exemplo, para rolar 4d5 seria `/role 4 5`\n- `/jogodavelha [jdv, v, velha] <Player 1> <Player 2>` -> Como o próprio nome ja diz, é o jogo da velha... Pra começar o jogo, basta chamar o comando e marcar ambos os jogadores logo depois. O jogo funciona com o comando abaixo\n- `/jogar [j] <posição>` -> Um complemento do jogo da velha, você usa esse comando pra dizer pra mim onde quer jogar...\n\nBom, é isso... Qualquer dúvida pode chamar o <@319850719228329985> caso tenha alguma dúvida. Até a próxima :D')
    await ctx.message.add_reaction("🚑")

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
        xp=users[str(id)]['xp']
        await ctx.send(f' Você está no nível {lvl} com {xp} de xp. Você mandou {xp/5} mensagens! :O')
        await ctx.message.add_reaction("🥳")
    else:
        id = member.id
        with open('users.json', 'r') as f:
            users = json.load(f)
        lvl = users[str(id)]['level']
        await ctx.send(f'{member} está no nível {lvl}!')
        await ctx.message.add_reaction("⬆️")

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
        
#Mensagens de possíveis erros de usuarios nos comandos:
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.DisabledCommand):
        await ctx.send('Esse comando foi desativado pelo <@319850719228329985>. Chame ele pra ver isso, se precisar...')
        await ctx.message.add_reaction("❌")
        return

@jogodavelha.error
async def jogodavelha_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Por favor mencione os dois players que irão jogar")
        await ctx.message.add_reaction("❌")
    if isinstance(error, commands.BadArgument):
        await ctx.send("Por favor, mencione o segundo player!")
        await ctx.message.add_reaction("❌")

@jogar.error
async def jogar_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Por favor, mande a posição em que deseja jogar")
        await ctx.message.add_reaction("❌")
    if isinstance(error, commands.BadArgument):
        await ctx.send("Por favor, mande um número inteiro!")
        await ctx.message.add_reaction("❌")

@bolaoito.error
async def bolaoito_error(ctx, error):
    #Se o usuario não mandar uma pergunta:
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Se você não pergutar, não posso responder :eye:")
        await ctx.message.add_reaction("❌")

@role.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.BadArgument):
        await ctx.send("Não conheço esse número, mande `/role <quantidade> <dado>`, por favor...")
        await ctx.message.add_reaction("❌")

@clear.error
async def clear_error(ctx, error):
    #Se o usuario não passar um número de mensagens a ser apagadas:
    if isinstance(error, commands.errors.BadArgument):
        await ctx.send("Por favor, digite o **número** de mensagens que quer apagar.")
        await ctx.message.add_reaction("❌")

@level.error
async def level_error(ctx, error):
    if isinstance(error, commands.errors.MemberNotFound):
        await ctx.send("Hmmm não faço ideia de quem seja essa")
        await ctx.message.add_reaction("❌")

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
        if isinstance(error, commands.errors.CommandNotFound):
            await ctx.send("Desculpa, não conheço esse comando... :pensive:")
'''

#Token:
client.run('ODg3ODQzNjM4OTg4NjQwMzA2.YUKC0g.wumQs4Hr8qjwYc8dSN9bnbWtelE')