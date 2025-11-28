import discord
from discord.ext import commands
from discord import app_commands

VOICE_PROCESS_CHANNEL = 1440569097694744674   # your channel ID


class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # /announce command
    # -------------------------
    @app_commands.command(
        name="announce",
        description="Send an announcement to a specific channel."
    )
    @app_commands.describe(
        channel="Select the channel to send the announcement",
        message="Enter the announcement message"
    )
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):

        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Announced by {interaction.user.display_name}")

        await channel.send(embed=embed)
        await interaction.response.send_message(f"✅ Announcement sent to {channel.mention}", ephemeral=True)

    # -------------------------
    # /vp start or stop command
    # -------------------------
    @app_commands.command(
        name="vp",
        description="Voice process control — start or stop."
    )
    @app_commands.describe(
        action="Choose start or stop"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="start", value="start"),
            app_commands.Choice(name="stop", value="stop")
        ]
    )
    async def vp(self, interaction: discord.Interaction, action: app_commands.Choice[str]):

        channel = interaction.guild.get_channel(VOICE_PROCESS_CHANNEL)

        if channel is None:
            return await interaction.response.send_message("❌ Voice process channel not found.", ephemeral=True)

        if action.value == "start":
            message = "🎙️ **Voice process going to start**"
        else:
            message = "🛑 **Voice process stopped**"

        await channel.send(message)
        await interaction.response.send_message(f"✅ VP status sent: `{action.value}`", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Announce(bot))
