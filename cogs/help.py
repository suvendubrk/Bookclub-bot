import discord
import discord.ext
from discord.ext import commands

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def help(self,ctx):
        embed = discord.Embed(
            colour=discord.Colour.blue(),
            timestamp=ctx.message.created_at

        )

        embed.set_author(name="Book Club Bot", icon_url="https://cdn.discordapp.com/attachments/742125990876151818/750062904757452820/bookclub_logo.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/742125990876151818/750062904757452820/bookclub_logo.png")
        embed.add_field(name=".disconnect", value="Stops and disconnect the bot.", inline=False)

        embed.add_field(name=".pause", value="Pauses Voice Activity.", inline=False)

        embed.add_field(name=".resume", value="Resumes if the bot is paused.", inline=False)
        embed.add_field(name=".stream_play [YouTube URL]", value="Plays video from YouTube don't play long files or it might stop.", inline=False)
        embed.add_field(name=".volume [Integer]", value="Raises or lowers the Voice specifed by the user.", inline=False)

        embed.set_footer(text="Mods and BookKeeper please use .sp_help to get help with special access commands. | ")

        await ctx.send(embed=embed)




    @commands.command()
    @commands.has_any_role("BookKeeper","Mod")
    async def sp_help(self,ctx):
        embed = discord.Embed (
            color=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/742125990876151818/750062904757452820/bookclub_logo.png")

        embed.set_author(name="Book Club Bot",
                         icon_url="https://cdn.discordapp.com/attachments/742125990876151818/750062904757452820/bookclub_logo.png")

        embed.add_field(name=".join[channel name]", value="Joins the channel specifed by the user.", inline=False)
        embed.add_field(name=".play[audio file with extension]", value="Plays the audio from local system of bot.",
                        inline=False)
        embed.add_field(name=".yt [URL]", value="Plays from a url (for audio books or long audio clips.)", inline=False)

        await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(events(bot))