import discord
from discord import app_commands
from discord.ext import commands
import os
from database import db

GUILD_ID = int(os.getenv('GUILD_ID', 1440569094394085467))
ALLOWED_USER_IDS = [int(id) for id in os.getenv('ALLOWED_USER_IDS', '').split(',') if id]
ALLOWED_ROLE_IDS = [int(id) for id in os.getenv('ALLOWED_ROLE_IDS', '').split(',') if id]

def is_authorized(user):
    """Check if user is authorized (by ID or role)"""
    if user.id in ALLOWED_USER_IDS:
        return True
    if user.guild_permissions.administrator:
        return True
    if any(role.id in ALLOWED_ROLE_IDS for role in user.roles):
        return True
    return False

class SlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.guild_id != GUILD_ID:
            await interaction.response.send_message('❌ This bot only works in the authorized server!', ephemeral=True)
            return False
        return True
    
    @app_commands.command(name="hello", description="Say hello!")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Hello {interaction.user.mention}! 👋')
    
    @app_commands.command(name="userinfo", description="Get info about a user")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(
            title=f"User Info - {member.name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Get server information")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"Server Info - {guild.name}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message('❌ You cannot kick someone with equal or higher role!', ephemeral=True)
        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message('❌ I cannot kick someone with equal or higher role than me!', ephemeral=True)
        
        # Log to database
        self.db.add_kick(member.id, interaction.guild.id, interaction.user.id, reason)
        self.db.add_security_log(interaction.guild.id, member.id, 'Kick', f'Kicked by {interaction.user.name}. Reason: {reason}')
        
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title='👢 User Kicked',
            description=f'{member.mention} has been kicked!',
            color=discord.Color.orange()
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Moderator', value=interaction.user.mention, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        try:
            await member.send(f'👢 You have been kicked from {interaction.guild.name}\nReason: {reason}')
        except:
            pass
    
    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message('❌ You cannot ban someone with equal or higher role!', ephemeral=True)
        if member.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message('❌ I cannot ban someone with equal or higher role than me!', ephemeral=True)
        
        # Log to database
        self.db.add_ban(member.id, interaction.guild.id, interaction.user.id, reason)
        self.db.add_security_log(interaction.guild.id, member.id, 'Ban', f'Banned by {interaction.user.name}. Reason: {reason}')
        
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title='🔨 User Banned',
            description=f'{member.mention} has been banned!',
            color=discord.Color.red()
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Moderator', value=interaction.user.mention, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        try:
            await member.send(f'🔨 You have been banned from {interaction.guild.name}\nReason: {reason}')
        except:
            pass
    
    @app_commands.command(name="clear", description="Clear messages")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            return await interaction.response.send_message('❌ Amount must be between 1 and 100!', ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f'✅ Cleared {amount} messages!', ephemeral=True)
    
    @app_commands.command(name="announce", description="Send an announcement to a channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        if not is_authorized(interaction.user):
            return await interaction.response.send_message('❌ You are not authorized to use this command!', ephemeral=True)
        
        try:
            await channel.send(message)
            await interaction.response.send_message(f'✅ Announcement sent to {channel.mention}!', ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message('❌ I don\'t have permission to send messages in that channel!', ephemeral=True)
    
    @app_commands.command(name="edit", description="Edit a bot message")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def edit(self, interaction: discord.Interaction, channel: discord.TextChannel, message_id: str, new_message: str):
        if not is_authorized(interaction.user):
            return await interaction.response.send_message('❌ You are not authorized to use this command!', ephemeral=True)
        
        try:
            message = await channel.fetch_message(int(message_id))
            
            if message.author.id != self.bot.user.id:
                return await interaction.response.send_message('❌ I can only edit my own messages!', ephemeral=True)
            
            await message.edit(content=new_message)
            await interaction.response.send_message(f'✅ Message edited successfully!', ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message('❌ Message not found!', ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message('❌ I don\'t have permission to edit that message!', ephemeral=True)
        except ValueError:
            await interaction.response.send_message('❌ Invalid message ID!', ephemeral=True)

async def setup(bot):
    await bot.add_cog(SlashCommands(bot))
