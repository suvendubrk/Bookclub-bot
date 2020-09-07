import discord
from discord import reaction, message, member, user
import discord.ext
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('reactions.db')

c = conn.cursor()

alphabets = ('🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷'
                                                                                                                   '🇸',
             '🇹', '🇺', '🇻', '🇼', '🇽', '🇿')

image_types = "mp3"

# The poll command is in development

def is_suv(): # so that Suvendu can use the commands
    def predicate(ctx):
        return ctx.author.id == 598230772960460815

    return commands.check(predicate)


class reaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='create poll', aliases=['cp'])
    @commands.check_any(commands.has_any_role("Mod", "BookKeeper"), is_suv())
    async def create_poll(self, ctx, question, *options):
        member = ctx.message.author
        member_name = member.name
        member_avatar = member.avatar_url
        print(member_name)

        embed = discord.Embed(
            colour=discord.Colour.green(),
            title=question
        )

        embed.set_author(name=member_name, icon_url=member_avatar)

        fields = [("Options", "\n".join([f"{alphabets[idx]} {option}" for idx, option in enumerate(options)]), False),
                  ("Instructions", "React slowly and on one option.", False)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        sent_message = await ctx.send(embed=embed)

        for emote in alphabets[:len(options)]:
            await sent_message.add_reaction(emote)

        channel_id = sent_message.channel.id
        message_id = sent_message.id

        c.execute("INSERT INTO reactions (channel_id, message_id) VALUES (?, ?)", (channel_id, message_id))
        conn.commit()
        c.execute("SELECT * FROM reactions")
        b = c.fetchone()
        print(b)

    @create_poll.error
    async def create_poll_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("You don't have the role to run the command")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        member = payload.user_id
        c.execute("SELECT user_id FROM reactions WHERE user_id = ?", (member,))
        users = c.fetchone()
        c.execute("SELECT message_id FROM reactions")
        poll_message = c.fetchall()
        for message_P in poll_message:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            for reaction in message.reactions:
                if payload.message_id in message_P:
                    if (not payload.member.bot and users == None and payload.member in await reaction.users().flatten()
                    ):
                        c.execute("INSERT INTO reactions (user_id) VALUES (?)", (member,))
                        await payload.member.send("Your reaction is recorded")
                        await message.remove_reaction(reaction.emoji, payload.member)
                        conn.commit()
                    elif users != None:
                        await payload.member.send("You can't vote again")
                        await message.remove_reaction(reaction.emoji, payload.member)


@commands.command()
@commands.check_any(commands.has_any_role("Mod", "BookKeeper"), is_suv())
async def save(self, ctx):
    for attachment in ctx.message.attachments:
        print("hello")
        if any(attachment.filename.lower().endswith(image) for image in image_types):
            for attachment in ctx.message.attachments:
                await attachment.save(attachment.filename)
                await ctx.send(f"Saved {attachment.filename}")


@save.error
async def save_error(self, ctx, error):
    if isinstance(error, commands.MissingAnyRole):
        await ctx.send("You don't have the role to run the command")


def setup(bot):
    bot.add_cog(reaction(bot))
