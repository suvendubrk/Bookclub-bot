import asyncio
import itertools

import discord
from discord.ext import commands
from discord.utils import get
from discord import client, voice_client, VoiceClient, File, Attachment
import youtube_dl
import os
import typing
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, timestamp=0):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        ffmpeg_options = {
            'options': f'-vn -ss {timestamp}'
        }

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("BookKeeper")
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel if specifed"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        embed = discord.Embed(
            colour=discord.Colour.green(),
            description=("**Joined the channel.**")
        )

        await ctx.send(embed=embed)

        await channel.connect()

    @join.error
    async def join_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**You need bookeeper role to access the command.**")
            )

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**Please specify a channel to join.**")
            )

            await ctx.send(embed=embed)

        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**The specifed Voice channel does not exist.**")
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("BookKeeper")
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem(of the bot) only for BookKeeper"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        embed = discord.Embed(
            colour=discord.Colour.green(),
            description=("Now playing: {} ".format(query))
        )

        await ctx.send(embed=embed)

    @play.error
    async def play_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**You need bookeeper role to access the command.**")
            )

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**Either the file doesn't exist or you did not specify the music.**")
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("bookclub")
    async def pause(self, ctx):
        """Pauses the voice activity."""

        embed_error = discord.Embed(
            colour=discord.Colour.green(),
            description="**Please connect to a voice channel First.**"
        )

        if ctx.voice_client is None:
            return await ctx.send(embed=embed_error)

        ctx.voice_client.pause()

        pause_embed = discord.Embed(
            colour=discord.Colour.green(),
            description="**Paused.**"
        )

        await ctx.send(embed=pause_embed)

    @pause.error
    async def pause_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**You need bookclub role to access the command."
                             "To do so go to <#749884357963153716> and type"
                             "`-role bookclub`.**")
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("bookclub")
    async def resume(self, ctx):
        """Resumes if paused"""
        embed_error = discord.Embed(
            colour=discord.Colour.green(),
            description="**Please connect to a voice channel First.**"
        )

        if ctx.voice_client is None:
            return await ctx.send(embed=embed_error)

        ctx.voice_client.resume()

        pause_embed = discord.Embed(
            colour=discord.Colour.green(),
            description="**Resumed.**"
        )

        await ctx.send(embed=pause_embed)

    @resume.error
    async def resume_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**You need bookclub role to access the command."
                             "To do so go to <#749884357963153716> and type"
                             "`-role bookclub`.**")
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("BookKeeper")
    async def yt(self, ctx, *, url):
        """Plays from a url (only for audiobooks and for bookeeper)"""

        song_there = os.path.isfile("song.webm")
        song = "song.webm"
        try:
            if song_there:
                os.remove("song.webm")
                print("Removed old song file")
        except PermissionError:
            print("Trying to delete song file, but it's being played")
            await ctx.send("ERROR: Music playing")
            return

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(discord.FFmpegPCMAudio("song.webm"), after=lambda e: print("Song done!"))

        for file in os.listdir("./"):
            if file.endswith(".webm"):
                name = file
                print(f"Renamed File: {file}\n")
                os.rename(file, "song.webm")

        embed = discord.Embed(
            colour=discord.Colour.green(),
            description=('Now playing: {}'.format(player.title))
        )

        await ctx.send(embed=embed)

    @yt.error
    async def yt_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**You need bookeeper role to access the command.**")
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("bookclub")
    async def pdf(self, ctx):
        await ctx.send(file=File("deepwork.pdf"))

    @commands.command()
    @commands.has_role("bookclub")
    async def stream_play(self, ctx,timestamp: typing.Optional[int]=0,*,search: str):
        """Streams from a YouTube URL."""
        async with ctx.typing():
            player = await YTDLSource.from_url(search, loop=self.bot.loop, stream=True,timestamp=timestamp)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=('Now playing: {}'.format(player.title))
            )

        await ctx.send(embed=embed)

    @stream_play.error
    async def stream_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**You need bookclub role to access the command."
                             "To do so go to <#749884357963153716> and type"
                             "`-role bookclub`.**")
            )

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**Please specify video or a URL.**")
            )

            await ctx.send(embed=embed)


    @commands.command()
    @commands.has_role("bookclub")
    async def volume(self, ctx, volume: int):
        """Changes the volume"""

        embed_error = discord.Embed(
            colour=discord.Colour.green(),
            description="**Please connect to a voice channel First.**"
        )

        embed = discord.Embed(
            colour=discord.Colour.green(),
            description=('Changed Volume to {}%'.format(volume))
        )

        if ctx.voice_client is None:
            return await ctx.send(embed=embed_error)

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(embed=embed)

    @volume.error
    async def volume_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**You need bookclub role to access the command."
                             " To do so go to <#749884357963153716> and type"
                             "`-role bookclub`.**")
            )

            await ctx.send(embed=embed)

        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**Please enter an integer.**")
            )

            await ctx.send(embed=embed)

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**Please enter an integer.**")
            )

            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role("bookclub")
    async def disconnect(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
        embed = discord.Embed(
            colour=discord.Colour.green(),
            description="**Disconnected.**"
        )

        await ctx.send(embed=embed)

    @disconnect.error
    async def disconnect_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                colour=discord.Colour.green(),
                description=("**You need bookclub role to access the command."
                             " To do so go to <#749884357963153716> and type"
                             "`-role bookclub`.**")
            )

            await ctx.send(embed=embed)

    @play.before_invoke
    @yt.before_invoke
    @stream_play.before_invoke
    async def ensure_voice(self, ctx):
        embed = discord.Embed(
            colour=discord.Colour.green(),
            description="**You are not connected to a voice channel.**"
        )
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(embed=embed)
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.command()
    async def send_dm(self,ctx):
        embed1 = discord.Embed(
            colour=discord.Colour.green(),
            description="Good Luck for The VC today!"
        )


        user = self.bot.get_user(id = 738845880899076139)
        user1 = self.bot.get_user(id=692410976976240650)
        user2 = self.bot.get_user(id=688446359761846297)
        user3 = self.bot.get_user(id=701132254486855700)
        user4 = self.bot.get_user(id=633235535711830066)

        await user.send(embed=embed1)
        await user1.send(embed=embed1)
        await user2.send(embed=embed1)
        await user3.send(embed=embed1)
        await user4.send(embed=embed1)


def setup(bot):
    bot.add_cog(Music(bot))
