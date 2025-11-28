import discord
from discord import app_commands
from discord.ext import commands
import os
from database import db

GUILD_ID = int(os.getenv('GUILD_ID', 1440569094394085467))
ALLOWED_USER_IDS = [int(id) for id in os.getenv('ALLOWED_USER_IDS', '').split(',') if id]
ALLOWED_ROLE_IDS = [int(id) for id in os.getenv('ALLOWED_ROLE_IDS', '').split(',') if id]

def is_authorized(user):
    """Check if user is authorized"""
    if user.id in ALLOWED_USER_IDS:
        return True
    if user.guild_permissions.administrator:
        return True
    if any(role.id in ALLOWED_ROLE_IDS for role in user.roles):
        return True
    return False

class DatabaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Warn a user"""
        db.add_warning(member.id, ctx.guild.id, ctx.author.id, reason)
        warning_count = db.get_warning_count(member.id, ctx.guild.id)
        
        embed = discord.Embed(
            title='⚠️ User Warned',
            description=f'{member.mention} has been warned!',
            color=discord.Color.orange()
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Total Warnings', value=warning_count, inline=False)
        embed.add_field(name='Moderator', value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f'⚠️ You have been warned in {ctx.guild.name}\nReason: {reason}\nTotal warnings: {warning_count}')
        except:
            pass
    
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        """Check user warnings"""
        warnings = db.get_warnings(member.id, ctx.guild.id)
        
        if not warnings:
            return await ctx.send(f'{member.mention} has no warnings!')
        
        embed = discord.Embed(
            title=f'⚠️ Warnings for {member.name}',
            description=f'Total: {len(warnings)} warnings',
            color=discord.Color.orange()
        )
        
        for i, warning in enumerate(warnings[:10], 1):
            moderator = ctx.guild.get_member(warning[3])
            mod_name = moderator.name if moderator else f'ID: {warning[3]}'
            embed.add_field(
                name=f'Warning #{i}',
                value=f'**Reason:** {warning[4]}\n**By:** {mod_name}\n**Date:** {warning[5]}',
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearwarnings(self, ctx, member: discord.Member):
        """Clear all warnings for a user"""
        db.clear_warnings(member.id, ctx.guild.id)
        await ctx.send(f'✅ Cleared all warnings for {member.mention}!')
    
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def userinfo(self, ctx, member: discord.Member = None):
        """Get detailed user information"""
        member = member or ctx.author
        
        # Get database stats
        user_stats = db.get_user_stats(member.id, ctx.guild.id)
        warning_count = db.get_warning_count(member.id, ctx.guild.id)
        
        embed = discord.Embed(
            title=f'User Info - {member.name}',
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name='ID', value=member.id, inline=True)
        embed.add_field(name='Joined Server', value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name='Account Created', value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name='Warnings', value=warning_count, inline=True)
        
        if user_stats:
            embed.add_field(name='Total Messages', value=user_stats[4], inline=True)
            embed.add_field(name='Last Seen', value=user_stats[6] or 'N/A', inline=True)
        
        roles = [role.mention for role in member.roles[1:]]
        if roles:
            embed.add_field(name='Roles', value=', '.join(roles[:10]), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def modlogs(self, ctx, limit: int = 10):
        """View recent moderation logs"""
        if not is_authorized(ctx.author):
            return await ctx.send('❌ You are not authorized to use this command!')
        
        logs = db.get_security_logs(ctx.guild.id, limit)
        
        if not logs:
            return await ctx.send('No logs found!')
        
        embed = discord.Embed(
            title='📋 Recent Moderation Logs',
            color=discord.Color.blue()
        )
        
        for log in logs:
            user = ctx.guild.get_member(log[2])
            user_name = user.name if user else f'ID: {log[2]}'
            embed.add_field(
                name=f'{log[3]} - {user_name}',
                value=f'{log[4]}\n{log[5]}',
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def slash_warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Warn a user (slash command)"""
        db.add_warning(member.id, interaction.guild.id, interaction.user.id, reason)
        warning_count = db.get_warning_count(member.id, interaction.guild.id)
        
        embed = discord.Embed(
            title='⚠️ User Warned',
            description=f'{member.mention} has been warned!',
            color=discord.Color.orange()
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Total Warnings', value=warning_count, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        try:
            await member.send(f'⚠️ You have been warned in {interaction.guild.name}\nReason: {reason}\nTotal warnings: {warning_count}')
        except:
            pass
    
    @app_commands.command(name="warnings", description="Check user warnings")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def slash_warnings(self, interaction: discord.Interaction, member: discord.Member):
        """Check user warnings (slash command)"""
        warnings = db.get_warnings(member.id, interaction.guild.id)
        
        if not warnings:
            return await interaction.response.send_message(f'{member.mention} has no warnings!', ephemeral=True)
        
        embed = discord.Embed(
            title=f'⚠️ Warnings for {member.name}',
            description=f'Total: {len(warnings)} warnings',
            color=discord.Color.orange()
        )
        
        for i, warning in enumerate(warnings[:10], 1):
            moderator = interaction.guild.get_member(warning[3])
            mod_name = moderator.name if moderator else f'ID: {warning[3]}'
            embed.add_field(
                name=f'Warning #{i}',
                value=f'**Reason:** {warning[4]}\n**By:** {mod_name}',
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(DatabaseCommands(bot))
