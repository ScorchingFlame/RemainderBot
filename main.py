import asyncio
from datetime import date
from discord import ChannelType
from nextcord import Interaction, SlashOption
from nextcord.ext import tasks
import nextcord, json
from nextcord.ext import commands
from keep_alive import db, data
import datetime
from dotenv import dotenv_values

with open("settings.json", "r") as settings:
    settings = json.loads(settings.read())

async def save_settings():
    with open("settings.json", "w") as setting:
        setting.write(json.dumps(settings, indent=4))

TESTING_GUILD_ID = 864733894817611817  # Replace with your testing guild id

bot = commands.Bot(command_prefix="$")

# command will be global if guild_ids is not specified
@bot.slash_command(guild_ids=[TESTING_GUILD_ID], description="Ping command")
async def ping(interaction: Interaction):
    await interaction.response.send_message(f"Pong! 🏓 ({round(bot.latency * 1000, 1)}ms)")


@bot.slash_command(guild_ids=[TESTING_GUILD_ID], description="remainder")
async def remainder(interaction: Interaction):
    """
    This is the main slash command that will be the prefix of all commands below.
    This will never get called since it has subcommands.
    """
    pass


@remainder.subcommand(description="Sets the remainder Channel", name="set_channel")
async def sub1(
    interaction: Interaction,
    channel : nextcord.abc.GuildChannel = SlashOption(description="Select a Channel",required=True, channel_types=[ChannelType.text])):
    """
    This is a subcommand of the '/main' slash command.
    It will appear in the menu as '/main sub1'.
    """
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(f"Uh okay", ephemeral=True)
    settings["channel"] = channel.id
    await save_settings()
    await interaction.response.send_message(f"Remainders Log Changed to {channel.mention}", ephemeral=True)

@remainder.subcommand(description="Manage Da Stuff")
async def manage(interaction: Interaction):
    """
    This is a subcommand group of the '/main' slash command.
    All subcommands of this group will be prefixed with '/main main_group'.
    This will never get called since it has subcommands.
    """
    pass

@manage.subcommand(description="Create")
async def create(
    interaction: Interaction,
    title: str = SlashOption(required=True),
    description: str = SlashOption(required=True),
    duration_in_days: int = SlashOption(required=True),
    ping_everyone : bool = SlashOption(required=True)
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(f"Sorry, You Dont Have Access To Do this Command!")
        return
    channel = bot.get_channel(settings["channel"])
    if channel is None:
        await interaction.response.send_message(f"No Remainder Logs Channel Set, use `/reminder set_channel` to set the channel")
        return
    if duration_in_days > 3000:
        await interaction.response.send_message(f"Duration Is Too Long")
        return
    now = datetime.datetime.utcnow() + datetime.timedelta(days=duration_in_days)
    db.session.add(data(title=title, description=description, date=now.day, month=now.month, year=now.year, ping=ping_everyone, time=int(datetime.datetime.utcnow().timestamp())))
    db.session.commit()
    await interaction.response.send_message(
        content=f"The Remainder is Saved and Will Remaind You At <t:{int(now.timestamp())}:R> in {channel.mention}",
        embed=nextcord.Embed(
            color=0x2F3136,
            title=title,
            description=description,
            timestamp=now
        ).set_footer(text=f"Requested By {interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar)
        )

@tasks.loop(hours=2)
async def remainder_check():
    channel = bot.get_channel(settings["channel"])
    if channel is None:
        return
    now = datetime.datetime.utcnow()
    for x in data.query.all():
        if x.date == now.day and x.month == now.month and x.year == now.year:
            await channel.send(
                    content="@everyone" if x.ping else "@here",
                    embed=nextcord.Embed(
                        color=0x2F3136,
                        title=x.title,
                        description=x.description + f"\nCreated at <t:{x.time}:R>"
                    )
                )
            db.session.delete(x)
    db.session.commit()

@remainder.subcommand(description="Checks For Current Remainder", name="check_now")
async def sub2(
    interaction: Interaction,
    ):
    """
    This is a subcommand of the '/main' slash command.
    It will appear in the menu as '/main sub1'.
    """
    async def idk():
        channel = bot.get_channel(settings["channel"])
        if channel is None:
            return
        now = datetime.datetime.utcnow()
        for x in data.query.all():
            if x.date == now.day and x.month == now.month and x.year == now.year:
                await channel.send(
                        content="@everyone" if x.ping else "@here",
                        embed=nextcord.Embed(
                            color=0x2F3136,
                            title=x.title,
                            description=x.description + f"\nCreated at <t:{x.time}:R>"
                        )
                    )
                db.session.delete(x)
        db.session.commit()

    bot.loop.create_task(idk())
    await interaction.response.send_message("Done!")


remainder_check.start()
bot.run(dotenv_values(".env")["TOKEN"])