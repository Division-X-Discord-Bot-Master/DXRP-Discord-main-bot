import discord
from discord.ext import commands
from discord import app_commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f'❌ You lack permissions: {", ".join(error.missing_permissions)}')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'❌ Missing argument: {error.param.name}')
        elif isinstance(error, commands.BadArgument):
            await ctx.send('❌ Invalid argument provided!')
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send('❌ Member not found!')
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'⏰ Command on cooldown. Try again in {error.retry_after:.2f}s')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f'❌ I lack permissions: {", ".join(error.missing_permissions)}')
        else:
            await ctx.send(f'❌ An error occurred: {str(error)}')
            print(f'Error: {error}')
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                f'❌ You lack permissions: {", ".join(error.missing_permissions)}',
                ephemeral=True
            )
        elif isinstance(error, app_commands.BotMissingPermissions):
            await interaction.response.send_message(
                f'❌ I lack permissions: {", ".join(error.missing_permissions)}',
                ephemeral=True
            )
        elif isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f'⏰ Command on cooldown. Try again in {error.retry_after:.2f}s',
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'❌ An error occurred: {str(error)}',
                ephemeral=True
            )
            print(f'Slash command error: {error}')

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
