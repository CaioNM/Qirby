import discord
from discord.ext import commands
import music

cogs = [music]

client = commands.Bot(commands_prefix=/, intents=discord.Intents.all())

for i in range(len(cogs)):
	cogs[i].setup(client)

client.run('#Aqui é o token do discord q pega no site dps')