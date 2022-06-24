import discord
from discord.ext import commands
import musica

#Dar uma olhada depois, talvez possa ser atualizado

cogs = [musica]

client = commands.Bot(command_prefix='/', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

client.run("token")
