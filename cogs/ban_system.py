import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
from datetime import datetime, timedelta
import json

# ==================== CONFIGURATION ====================
BANNED_ROLE_ID = 1440569094394085474  # Role to give when banned
BAN_LOG_CHANNEL = 1440569096809877559  # Channel to log bans
ADMIN_ROLE_ID = 1234567890123456789  # Administrator role ID
ASSIGNED_ROLE_ID = 1234567890123456789  # Assigned role ID (can view ban history)


class BanDatabase:
    """Database handler for ban system"""
    
    def __init__(self, db_name='bot_database.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create ban tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS temp_bans (
                ban_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                reason TEXT,
                banned_by INTEGER NOT NULL,
                banned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                unban_at DATETIME NOT NULL,
                original_roles TEXT,
                active INTEGER DEFAULT 1
            )
        ''')
        self.conn.commit()
    
    def add_ban(self, user_id, username, reason, banned_by, unban_at, original_roles):
        """Add a new temporary ban"""
        roles_json = json.dumps(original_roles)
        self.cursor.execute('''
            INSERT INTO temp_bans (user_id, username, reason, banned_by, unban_at, original_roles)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, reason, banned_by, unban_at, roles_json))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_active_bans(self):
        """Get all active bans"""
        self.cursor.execute('''
            SELECT * FROM temp_bans 
            WHERE active = 1
            ORDER BY unban_at ASC
        ''')
        return self.cursor.fetchall()
    
    def get_user_ban(self, user_id):
        """Get active ban for a user"""
        self.cursor.execute('''
            SELECT * FROM temp_bans 
            WHERE user_id = ? AND active = 1
        ''', (user_id,))
        return self.cursor.fetchone()
    
    def deactivate_ban(self, ban_id):
        """Mark ban as inactive"""
        self.cursor.execute('''
            UPDATE temp_bans 
            SET active = 0
            WHERE ban_id = ?
        ''', (ban_id,))
        self.conn.commit()
    
    def get_ban_history(self, user_id):
        """Get ban history for a user"""
        self.cursor.execute('''
            SELECT * FROM temp_bans 
            WHERE user_id = ?
            ORDER BY banned_at DESC
        ''', (user_id,))
        return self.cursor.fetchall()


class BanSystem(commands.Cog):
    """Ban System with temporary bans and role restoration"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = BanDatabase()
        self.check_bans.start()
    
    def cog_unload(self):
        """Stop the ban check loop when cog is unloaded"""
        self.check_bans.cancel()
    
    @tasks.loop(minutes=1)
    async def check_bans(self):
        """Check for expired bans every minute"""
        try:
            active_bans = self.db.get_active_bans()
            current_time = datetime.now()
            
            for ban in active_bans:
                ban_id, user_id, username, reason, banned_by, banned_at, unban_at, original_roles, active = ban
                
                unban_time = datetime.fromisoformat(unban_at)
                
                if current_time >= unban_time:
                    # Time to unban
                    await self.unban_user(user_id, ban_id, original_roles)
        
        except Exception as e:
            print(f"Error checking bans: {e}")
    
    @check_bans.before_loop
    async def before_check_bans(self):
        """Wait until bot is ready before starting the loop"""
        await self.bot.wait_until_ready()
    
    async def unban_user(self, user_id, ban_id, original_roles_json):
        """Unban a user and restore their roles"""
        try:
            # Get all guilds the bot is in
            for guild in self.bot.guilds:
                member = guild.get_member(user_id)
                if member:
                    # Remove banned role
                    banned_role = guild.get_role(BANNED_ROLE_ID)
                    if banned_role and banned_role in member.roles:
                        await member.remove_roles(banned_role)
                    
                    # Restore original roles
                    original_roles = json.loads(original_roles_json)
                    for role_id in original_roles:
                        role = guild.get_role(role_id)
                        if role and role not in member.roles:
                            try:
                                await member.add_roles(role)
                            except:
                                pass
                    
                    # Send DM
                    try:
                        dm_embed = discord.Embed(
                            title="✅ Ban Expired",
                            description=f"Your temporary ban in **{guild.name}** has expired. Your roles have been restored.",
                            color=discord.Color.green()
                        )
                        await member.send(embed=dm_embed)
                    except:
                        pass
                    
                    # Log unban
                    log_channel = guild.get_channel(BAN_LOG_CHANNEL)
                    if log_channel:
                        log_embed = discord.Embed(
                            title="🔓 Automatic Unban",
                            description=f"{member.mention} has been automatically unbanned.",
                            color=discord.Color.green(),
                            timestamp=datetime.now()
                        )
                        log_embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=True)
                        log_embed.add_field(name="Roles Restored", value=f"{len(original_roles)} roles", inline=True)
                        await log_channel.send(embed=log_embed)
                    
                    print(f"✅ Unbanned user {member.name} (ID: {user_id})")
            
            # Mark ban as inactive
            self.db.deactivate_ban(ban_id)
        
        except Exception as e:
            print(f"Error unbanning user {user_id}: {e}")
    
    def parse_time(self, time_str):
        """Parse time string like '1d', '2h', '30m' into timedelta"""
        time_str = time_str.lower().strip()
        
        if time_str.endswith('d'):
            days = int(time_str[:-1])
            return timedelta(days=days)
        elif time_str.endswith('h'):
            hours = int(time_str[:-1])
            return timedelta(hours=hours)
        elif time_str.endswith('m'):
            minutes = int(time_str[:-1])
            return timedelta(minutes=minutes)
        elif time_str.endswith('w'):
            weeks = int(time_str[:-1])
            return timedelta(weeks=weeks)
        else:
            raise ValueError("Invalid time format. Use: 1d, 2h, 30m, 1w")
    
    @app_commands.command(name="ban", description="Temporarily ban a user and remove their roles")
    @app_commands.describe(
        user="The user to ban",
        time="Ban duration (e.g., 1d, 2h, 30m, 1w)",
        reason="Reason for the ban"
    )
    @commands.has_permissions(ban_members=True)
    async def ban_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        time: str,
        reason: str = "No reason provided"
    ):
        """Ban a user temporarily"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Check if user is already banned
            existing_ban = self.db.get_user_ban(user.id)
            if existing_ban:
                embed = discord.Embed(
                    title="❌ Already Banned",
                    description=f"{user.mention} is already banned.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Parse time
            try:
                duration = self.parse_time(time)
            except ValueError as e:
                embed = discord.Embed(
                    title="❌ Invalid Time Format",
                    description=str(e),
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Calculate unban time
            unban_at = datetime.now() + duration
            
            # Save current roles (exclude @everyone and banned role)
            original_roles = [role.id for role in user.roles if role.id != interaction.guild.default_role.id and role.id != BANNED_ROLE_ID]
            
            # Remove all roles except @everyone
            roles_to_remove = [role for role in user.roles if role.id != interaction.guild.default_role.id]
            if roles_to_remove:
                await user.remove_roles(*roles_to_remove, reason=f"Banned by {interaction.user.name}: {reason}")
            
            # Add banned role
            banned_role = interaction.guild.get_role(BANNED_ROLE_ID)
            if banned_role:
                await user.add_roles(banned_role, reason=f"Banned by {interaction.user.name}")
            
            # Save to database
            ban_id = self.db.add_ban(
                user.id,
                user.name,
                reason,
                interaction.user.id,
                unban_at,
                original_roles
            )
            
            # Send DM to banned user
            try:
                dm_embed = discord.Embed(
                    title="🔨 You Have Been Banned",
                    description=f"You have been temporarily banned from **{interaction.guild.name}**.",
                    color=discord.Color.red()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Duration", value=time, inline=True)
                dm_embed.add_field(name="Unbanned At", value=f"<t:{int(unban_at.timestamp())}:F>", inline=True)
                dm_embed.add_field(name="Banned By", value=interaction.user.mention, inline=True)
                await user.send(embed=dm_embed)
            except:
                pass
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ User Banned",
                description=f"{user.mention} has been temporarily banned.",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="Duration", value=time, inline=True)
            embed.add_field(name="Banned By", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Roles Removed", value=f"{len(original_roles)} roles saved", inline=True)
            embed.add_field(name="Unban At", value=f"<t:{int(unban_at.timestamp())}:R>", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log to ban channel
            log_channel = interaction.guild.get_channel(BAN_LOG_CHANNEL)
            if log_channel:
                log_embed = discord.Embed(
                    title="🔨 User Banned",
                    description=f"{user.mention} has been temporarily banned.",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
                log_embed.add_field(name="Duration", value=time, inline=True)
                log_embed.add_field(name="Banned By", value=interaction.user.mention, inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.add_field(name="Unban At", value=f"<t:{int(unban_at.timestamp())}:F>", inline=False)
                await log_channel.send(embed=log_embed)
        
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to ban user: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            print(f"Ban error: {e}")
            import traceback
            traceback.print_exc()
    
    @app_commands.command(name="unban", description="Manually unban a user and restore their roles")
    @app_commands.describe(user="The user to unban")
    @commands.has_permissions(ban_members=True)
    async def manual_unban(self, interaction: discord.Interaction, user: discord.Member):
        """Manually unban a user"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Check if user is banned
            ban_data = self.db.get_user_ban(user.id)
            if not ban_data:
                embed = discord.Embed(
                    title="❌ Not Banned",
                    description=f"{user.mention} is not currently banned.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            ban_id, user_id, username, reason, banned_by, banned_at, unban_at, original_roles, active = ban_data
            
            # Unban the user
            await self.unban_user(user_id, ban_id, original_roles)
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ User Unbanned",
                description=f"{user.mention} has been manually unbanned and their roles restored.",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="Unbanned By", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log to ban channel
            log_channel = interaction.guild.get_channel(BAN_LOG_CHANNEL)
            if log_channel:
                log_embed = discord.Embed(
                    title="🔓 Manual Unban",
                    description=f"{user.mention} has been manually unbanned.",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
                log_embed.add_field(name="Unbanned By", value=interaction.user.mention, inline=True)
                await log_channel.send(embed=log_embed)
        
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to unban user: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
    
    @app_commands.command(name="baninfo", description="View ban information for a user")
    @app_commands.describe(user="The user to check")
    async def ban_info(self, interaction: discord.Interaction, user: discord.Member):
        """View ban information"""
        ban_data = self.db.get_user_ban(user.id)
        
        if not ban_data:
            embed = discord.Embed(
                title="ℹ️ Ban Information",
                description=f"{user.mention} is not currently banned.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        ban_id, user_id, username, reason, banned_by, banned_at, unban_at, original_roles, active = ban_data
        
        original_roles_list = json.loads(original_roles)
        unban_time = datetime.fromisoformat(unban_at)
        
        embed = discord.Embed(
            title="🔨 Ban Information",
            description=f"Ban details for {user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.fromisoformat(banned_at)
        )
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
        embed.add_field(name="Banned By", value=f"<@{banned_by}>", inline=True)
        embed.add_field(name="Status", value="🔴 Active" if active else "🟢 Inactive", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned At", value=f"<t:{int(datetime.fromisoformat(banned_at).timestamp())}:F>", inline=True)
        embed.add_field(name="Unban At", value=f"<t:{int(unban_time.timestamp())}:R>", inline=True)
        embed.add_field(name="Roles Saved", value=f"{len(original_roles_list)} roles", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="banlist", description="View all active bans")
    @commands.has_permissions(ban_members=True)
    async def ban_list(self, interaction: discord.Interaction):
        """View all active bans"""
        active_bans = self.db.get_active_bans()
        
        if not active_bans:
            embed = discord.Embed(
                title="📋 Active Bans",
                description="No active bans.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Active Bans",
            description=f"Total: **{len(active_bans)}** active bans",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        for ban in active_bans[:10]:  # Show first 10
            ban_id, user_id, username, reason, banned_by, banned_at, unban_at, original_roles, active = ban
            unban_time = datetime.fromisoformat(unban_at)
            
            embed.add_field(
                name=f"👤 {username}",
                value=f"**ID:** {user_id}\n**Unban:** <t:{int(unban_time.timestamp())}:R>\n**Reason:** {reason[:50]}...",
                inline=True
            )
        
        if len(active_bans) > 10:
            embed.set_footer(text=f"Showing 10 of {len(active_bans)} bans")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="banhistory", description="View complete ban history for a user")
    @app_commands.describe(person="The user to check ban history for")
    async def ban_history(self, interaction: discord.Interaction, person: discord.Member):
        """View complete ban history for a user - Admin and Assigned roles only"""
        
        # Check if user has required roles
        admin_role = interaction.guild.get_role(ADMIN_ROLE_ID)
        assigned_role = interaction.guild.get_role(ASSIGNED_ROLE_ID)
        
        has_permission = False
        if admin_role and admin_role in interaction.user.roles:
            has_permission = True
        if assigned_role and assigned_role in interaction.user.roles:
            has_permission = True
        if interaction.user.guild_permissions.administrator:
            has_permission = True
        
        if not has_permission:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to view ban history. This command requires Administrator or Assigned role.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get ban history
        ban_history = self.db.get_ban_history(person.id)
        
        if not ban_history:
            embed = discord.Embed(
                title="📋 Ban History",
                description=f"{person.mention} has no ban history.",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=person.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create embed with ban history
        embed = discord.Embed(
            title="📋 Ban History",
            description=f"Complete ban history for {person.mention}",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=person.display_avatar.url)
        embed.add_field(name="User", value=f"{person.mention} ({person.id})", inline=True)
        embed.add_field(name="Total Bans", value=f"**{len(ban_history)}**", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        
        # Add each ban to the embed
        for idx, ban in enumerate(ban_history[:10], 1):  # Show last 10 bans
            ban_id, user_id, username, reason, banned_by, banned_at, unban_at, original_roles, active = ban
            
            banned_time = datetime.fromisoformat(banned_at)
            unban_time = datetime.fromisoformat(unban_at)
            
            # Status indicator
            if active:
                status = "🔴 Active"
            else:
                status = "🟢 Completed"
            
            # Calculate duration
            duration = unban_time - banned_time
            days = duration.days
            hours = duration.seconds // 3600
            
            if days > 0:
                duration_str = f"{days}d {hours}h"
            else:
                duration_str = f"{hours}h"
            
            field_value = (
                f"**Status:** {status}\n"
                f"**Reason:** {reason}\n"
                f"**Duration:** {duration_str}\n"
                f"**Banned By:** <@{banned_by}>\n"
                f"**Date:** <t:{int(banned_time.timestamp())}:D>\n"
                f"**Unbanned:** <t:{int(unban_time.timestamp())}:R>"
            )
            
            embed.add_field(
                name=f"Ban #{ban_id} - {status}",
                value=field_value,
                inline=False
            )
        
        if len(ban_history) > 10:
            embed.set_footer(text=f"Showing 10 of {len(ban_history)} bans")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(BanSystem(bot))
