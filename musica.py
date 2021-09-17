import discord
from discord.ext import commands
import youtube_dl

class music(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command()
    async def entre(self,ctx):
        if ctx.author.voice is None:
            await ctx.send('Mas você não está em nenhum canal... 😔')
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            await ctx.send('Entrei! Oláaaaaa :D')
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command()
    async def saia(self,ctx):
        await ctx.voice_client.disconnect()
        await ctx.send('Tchau tchau! Até a próxima... 👋')

    @commands.command()
    async def play(self,ctx,url):
        ctx.voice_client.stop()
        await ctx.send('Tocando! 🎶')
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format':"bestaudio"}
        vc = ctx.voice_client

        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source)
    
    @commands.command()
    async def pause(self,ctx):
        await ctx.send('Pausado! ⏸')
        await ctx.voice_client.pause()
    
    @commands.command()
    async def resume(self,ctx):
        await ctx.channel.send("Tocando de novo! 🎶")
        await ctx.voice_client.resume()

    @commands.command()
    async def ajuda(self, ctx):
        await ctx.send('Oi, tudo bem?\nEstes são os meus comandos até o momento:\n1. Antes de tudo, envie **/entre** para me chamar ao canal e eu chegarei rapidinho\n2. Use **/play** seguido do link da música no youtube para toca-la\n3. Use **/pause** para pausar a sua música\n4. Use **/resume** para retomar uma música que esta pausada\n5. E por fim, use **/saia** para que eu vá embora!\nPor enquanto é isto, estou sempre a disposição, lembre-se de enviar **/ajuda** caso esqueça de algum comando, e até a próxima! 😘\n\n\n\n\n16/11')

    @commands.command()
    async def primeiroencontro(self, ctx):
      await ctx.send('Oi meu amor, vc descobriu o segredo... Parabens! :D\nMeu amor, eu deixei esse pequeno segredinho nas linhas de código do bot para te dizer o quanto eu te amo... Esse bot foi contruido principalmente pra vc... eu fiz ele em sua homenagem. Vc com certeza é a pessoa que eu mais amo nesse mundo... Amo seu jeito, seu cabelo, o jeito que vc sorri, como se veste, seus olhos... tudo, tudo em vc é perfeito. Vc com certeza é a melhor pessoa que ja apareceu na minha vida. A cada vez que eu recebo o seu bom dia no whatsapp, a cada dia que eu recebo a benção de poder ver seu sorriso e escutar sua voz, eu me apaixono mais e mais. Eu nao tenho palavras pra expressar o quao importante vc eh pra mim e como eu sou grato por ter vc... Vc eh incrivel bel, te amo muitao minha princesa... Espero poder passar o resto da minha vida com vc. Espero tmb que vc goste desse botzinho e que vc se divirta muito tocando suas musicas favoritas. Obrigado por tudo Bel, te amo :)')

def setup(client):
    client.add_cog(music(client))