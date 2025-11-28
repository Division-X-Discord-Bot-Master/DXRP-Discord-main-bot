import discord
from discord.ext import commands
import os
from database import db

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

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = db
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send('❌ You cannot kick someone with equal or higher role!')
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send('❌ I cannot kick someone with equal or higher role than me!')
        
        reason = reason or "No reason provided"
        
        # Log to database
        self.db.add_kick(member.id, ctx.guild.id, ctx.author.id, reason)
        self.db.add_security_log(ctx.guild.id, member.id, 'Kick', f'Kicked by {ctx.author.name}. Reason: {reason}')
        
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title='👢 User Kicked',
            description=f'{member.mention} has been kicked!',
            color=discord.Color.orange()
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Moderator', value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f'👢 You have been kicked from {ctx.guild.name}\nReason: {reason}')
        except:
            pass
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member.top_role >= ctx.author.top_role:
            return await ctx.send('❌ You cannot ban someone with equal or higher role!')
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send('❌ I cannot ban someone with equal or higher role than me!')
        
        reason = reason or "No reason provided"
        
        # Log to database
        self.db.add_ban(member.id, ctx.guild.id, ctx.author.id, reason)
        self.db.add_security_log(ctx.guild.id, member.id, 'Ban', f'Banned by {ctx.author.name}. Reason: {reason}')
        
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title='🔨 User Banned',
            description=f'{member.mention} has been banned!',
            color=discord.Color.red()
        )
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.add_field(name='Moderator', value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(f'🔨 You have been banned from {ctx.guild.name}\nReason: {reason}')
        except:
            pass
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            return await ctx.send('❌ Amount must be between 1 and 100!')
        
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'✅ Cleared {amount} messages!', delete_after=3)
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx, channel: discord.TextChannel, *, message: str):
        if not is_authorized(ctx.author):
            return await ctx.send('❌ You are not authorized to use this command!')
        
        try:
            await channel.send(message)
            await ctx.send(f'✅ Announcement sent to {channel.mention}!')
        except discord.Forbidden:
            await ctx.send('❌ I don\'t have permission to send messages in that channel!')
    
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def edit(self, ctx, channel: discord.TextChannel, message_id: int, *, new_message: str):
        if not is_authorized(ctx.author):
            return await ctx.send('❌ You are not authorized to use this command!')
        
        try:
            message = await channel.fetch_message(message_id)
            
            if message.author.id != self.bot.user.id:
                return await ctx.send('❌ I can only edit my own messages!')
            
            await message.edit(content=new_message)
            await ctx.send(f'✅ Message edited successfully!')
        except discord.NotFound:
            await ctx.send('❌ Message not found!')
        except discord.Forbidden:
            await ctx.send('❌ I don\'t have permission to edit that message!')

async def setup(bot):
    await bot.add_cog(Moderation(bot))
