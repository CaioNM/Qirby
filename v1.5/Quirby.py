import discord
import random
from discord.ext import commands
from discord.ext.commands.core import command

#Prefixo dos comando
# OBS.: tem um modo de mudar o prefixo pra um servidor específico, mas por padrão é melhor deixar o mesmo, caso mude de ideia: Episode 6 - Server Prefixes!!!
# Link: https://youtu.be/glo9R7JGkRE
client = commands.Bot(command_prefix='/')

#Remove o comando help pre-definido pela biblioteca para poder usar personalizados
client.remove_command("help")

#Teste de funcionamento do bot
@client.event
async def on_ready():
    print('Funcionando!')

#Colocar "aliases" no argumento do client de uma função, reduz o tamanho do comando, por exemplo, 
# em vez de escrever /play, o user escreve /p e o comando funciona perfeitamente
@client.command(aliases=['p'])
#Condiçao pra nao spamar comando, recebe a quantidade de vezes que o usuário pode mandar o comando e depois que esse limite é alcançado
#entra num cooldown de X segundos, no caso "@commands.cooldown(<quantidade>, <seg de espera>, commands.cooldowns.BucketType.user)"
@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
#O argumento "ctx" é usado quando o bot manda mensagens de texto
async def ping(ctx):
    await ctx.send('Pong!  🏓')

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
    if(not ctx.author.guild_permissions.manage_messages):
        await ctx.send('Você não tem a permissão necessária para isso...')
        return
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


@client.command(aliases=['ajuda'])
@commands.cooldown(4, 45, commands.cooldowns.BucketType.user)
async def help(ctx):
    await ctx.send('ajuda go brrrrr uiiiuuu uiiuuu 🚑\n\n\n\n Meme, tem q arrumar dps :)')


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

#Mensagem de erro, mostra os segundos restantes para poder mandar mensagem
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