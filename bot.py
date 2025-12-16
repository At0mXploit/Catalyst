import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

COGS = [
    "cogs.task_cog",
    "cogs.leave_cog",
    "cogs.reports_cog",
    "cogs.status_cog"
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Bot is ready and serving {len(bot.guilds)} guild(s)")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"{ctx.author.mention} Command not found. Type `!help` for available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{ctx.author.mention} Missing required arguments. Type `!help` for command usage.")
    else:
        await ctx.send(f"{ctx.author.mention} An error occurred: {str(error)}")

async def load_extensions():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"Loaded {cog}")
        except Exception as e:
            print(f"Failed to load {cog}: {e}")
            import traceback
            traceback.print_exc()

@bot.event
async def setup_hook():
    await load_extensions()

bot.run(TOKEN)
