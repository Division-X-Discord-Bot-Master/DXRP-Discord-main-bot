import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

GUILD_ID = int(os.getenv('GUILD_ID'))

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.check
async def globally_block_other_guilds(ctx):
    return ctx.guild and ctx.guild.id == GUILD_ID

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    await bot.load_extension('cogs.errorhandler')
    await bot.load_extension('cogs.welcome')
    await bot.load_extension('cogs.moderation')
    await bot.load_extension('cogs.slashcommands')
    await bot.load_extension('cogs.security')
    await bot.load_extension('cogs.database_commands')
    await bot.load_extension('cogs.image_commands')
    await bot.load_extension('cogs.application_system')
    
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f'All cogs loaded and slash commands synced to guild {GUILD_ID}!')

bot.run(os.getenv('DISCORD_TOKEN'))
