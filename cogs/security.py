import discord
from discord.ext import commands
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import os

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

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = defaultdict(list)
        self.join_cache = defaultdict(list)
        self.spam_warnings = defaultdict(int)
        
        # Anti-spam settings
        self.spam_threshold = 5  # messages
        self.spam_interval = 5  # seconds
        self.spam_mute_duration = 300  # 5 minutes
        
        # Anti-raid settings
        self.raid_threshold = 5  # joins
        self.raid_interval = 10  # seconds
        
        # Load banned words from database
        from database import db
        self.db = db
        self.banned_words = self.db.get_banned_words()
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        if message.guild.id != GUILD_ID:
            return
        
        # Skip authorized users
        if is_authorized(message.author):
            return
        
        # Check for banned words
        if await self.check_banned_words(message):
            return
        
        # Check for spam
        await self.check_spam(message)
        
        # Check for mass mentions
        if len(message.mentions) > 5:
            await message.delete()
            await message.channel.send(f'⚠️ {message.author.mention} Mass mentions are not allowed!', delete_after=5)
            await self.log_action('Mass Mention', message.author, f'Mentioned {len(message.mentions)} users')
    
    async def check_banned_words(self, message):
        """Check for banned words"""
        content_lower = message.content.lower()
        for word in self.banned_words:
            if word in content_lower:
                await message.delete()
                await message.channel.send(f'⚠️ {message.author.mention} Your message contained prohibited content!', delete_after=5)
                await self.log_action('Banned Word', message.author, f'Used banned word: {word}')
                return True
        return False
    
    async def check_spam(self, message):
        """Check for spam messages"""
        user_id = message.author.id
        current_time = datetime.now()
        
        # Add message to cache
        self.message_cache[user_id].append(current_time)
        
        # Remove old messages from cache
        self.message_cache[user_id] = [
            msg_time for msg_time in self.message_cache[user_id]
            if current_time - msg_time < timedelta(seconds=self.spam_interval)
        ]
        
        # Check if spam threshold exceeded
        if len(self.message_cache[user_id]) >= self.spam_threshold:
            self.spam_warnings[user_id] += 1
            
            try:
                await message.channel.purge(limit=self.spam_threshold, check=lambda m: m.author == message.author)
                
                if self.spam_warnings[user_id] >= 3:
                    # Timeout user
                    timeout_until = discord.utils.utcnow() + timedelta(seconds=self.spam_mute_duration)
                    await message.author.timeout(timeout_until, reason='Spam detected')
                    await message.channel.send(f'🔇 {message.author.mention} has been timed out for spam!', delete_after=10)
                    await self.log_action('Timeout', message.author, f'Spam detected - {self.spam_mute_duration}s timeout')
                else:
                    await message.channel.send(f'⚠️ {message.author.mention} Stop spamming! Warning {self.spam_warnings[user_id]}/3', delete_after=5)
                    await self.log_action('Spam Warning', message.author, f'Warning {self.spam_warnings[user_id]}/3')
                
                self.message_cache[user_id].clear()
            except discord.Forbidden:
                pass
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != GUILD_ID:
            return
        
        # Check for raid
        await self.check_raid(member)
        
        # Check for suspicious accounts
        account_age = (datetime.now() - member.created_at.replace(tzinfo=None)).days
        if account_age < 7:
            await self.log_action('Suspicious Join', member, f'Account age: {account_age} days')
    
    async def check_raid(self, member):
        """Check for raid attempts"""
        guild_id = member.guild.id
        current_time = datetime.now()
        
        # Add join to cache
        self.join_cache[guild_id].append(current_time)
        
        # Remove old joins from cache
        self.join_cache[guild_id] = [
            join_time for join_time in self.join_cache[guild_id]
            if current_time - join_time < timedelta(seconds=self.raid_interval)
        ]
        
        # Check if raid threshold exceeded
        if len(self.join_cache[guild_id]) >= self.raid_threshold:
            await self.log_action('Raid Detected', member, f'{len(self.join_cache[guild_id])} joins in {self.raid_interval}s')
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != GUILD_ID:
            return
        await self.log_action('Member Left', member, 'Left the server')
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if guild.id != GUILD_ID:
            return
        await self.log_action('Member Banned', user, 'Banned from server')
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if guild.id != GUILD_ID:
            return
        await self.log_action('Member Unbanned', user, 'Unbanned from server')
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id != GUILD_ID or message.author.bot:
            return
        await self.log_action('Message Deleted', message.author, f'Content: {message.content[:100]}')
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.guild.id != GUILD_ID or before.author.bot:
            return
        if before.content != after.content:
            await self.log_action('Message Edited', before.author, f'Before: {before.content[:50]}\nAfter: {after.content[:50]}')
    
    async def log_action(self, action, user, details):
        """Log security actions to a channel and database"""
        # Log to database
        self.db.add_security_log(GUILD_ID, user.id, action, details)
        
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        
        log_channel = discord.utils.get(guild.channels, name='security-logs')
        if not log_channel:
            return
        
        embed = discord.Embed(
            title=f'🔒 {action}',
            description=details,
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=f'{user.name} ({user.id})', icon_url=user.avatar.url if user.avatar else None)
        
        try:
            await log_channel.send(embed=embed)
        except:
            pass
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx):
        """Lock all channels"""
        if not is_authorized(ctx.author):
            return await ctx.send('❌ You are not authorized to use this command!')
        
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            except:
                pass
        
        await ctx.send('🔒 Server is now in lockdown mode!')
        await self.log_action('Lockdown', ctx.author, 'Server locked down')
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx):
        """Unlock all channels"""
        if not is_authorized(ctx.author):
            return await ctx.send('❌ You are not authorized to use this command!')
        
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=None)
            except:
                pass
        
        await ctx.send('🔓 Server lockdown has been lifted!')
        await self.log_action('Unlock', ctx.author, 'Server unlocked')
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addbadword(self, ctx, *, word: str):
        """Add a banned word"""
        if not is_authorized(ctx.author):
            return await ctx.send('❌ You are not authorized to use this command!')
        
        if self.db.add_banned_word(word, ctx.author.id):
            self.banned_words = self.db.get_banned_words()
            await ctx.send(f'✅ Added "{word}" to banned words list!')
            await self.log_action('Banned Word Added', ctx.author, f'Word: {word}')
        else:
            await ctx.send('❌ This word is already banned!')
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removebadword(self, ctx, *, word: str):
        """Remove a banned word"""
        if not is_authorized(ctx.author):
            return await ctx.send('❌ You are not authorized to use this command!')
        
        if self.db.remove_banned_word(word):
            self.banned_words = self.db.get_banned_words()
            await ctx.send(f'✅ Removed "{word}" from banned words list!')
            await self.log_action('Banned Word Removed', ctx.author, f'Word: {word}')
        else:
            await ctx.send('❌ This word is not in the banned list!')

async def setup(bot):
    await bot.add_cog(Security(bot))
