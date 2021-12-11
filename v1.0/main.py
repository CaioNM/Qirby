import discord
from discord.ext import commands
import musica

#Dar uma olhada depois, talvez possa ser atualizado

cogs = [musica]

client = commands.Bot(command_prefix='/', intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)

client.run("ODg3ODQzNjM4OTg4NjQwMzA2.YUKC0g.wumQs4Hr8qjwYc8dSN9bnbWtelE")