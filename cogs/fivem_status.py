import discord
import json
import os
from requests import get
from discord.ext import commands, tasks

# ==================== CONFIGURATION ====================
GUILD_ID = 1234567890123456789  # Your server ID
FIVEM_STATUS_CHANNEL_ID = 1234567890123456789  # Channel for FiveM status
FIVEM_SERVER_IP = "your.server.ip"  # Your FiveM server IP
FIVEM_SERVER_PORT = "30120"  # Your FiveM server port
CONNECT_CODE = "md3qkv"  # Your FiveM connect code
EMBED_COLOR = "#EB3900"  # Embed color when online
STATUS_IMAGE_URL = ""
UPDATE_INTERVAL = 5  # Minutes between updates


class FivemStatus(commands.Cog):
    """FiveM Server Status Monitor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.fivem_status_channel = None
        self.lbmsg = None
        self.msg_board_status = False
        self.message_file = "configuration/message.json"
        
        # Ensure configuration directory exists
        os.makedirs("configuration", exist_ok=True)
        
        # Initialize message file if it doesn't exist
        if not os.path.exists(self.message_file):
            with open(self.message_file, "w") as f:
                json.dump({"leadboard_message_main": None}, f)
        
        self.fivem_status.start()
    
    def cog_unload(self):
        """Stop the status loop when cog is unloaded"""
        self.fivem_status.cancel()
    
    async def get_leadboard_msg(self):
        """Get the existing status message"""
        with open(self.message_file, "r") as f1:
            messages = json.load(f1)
        
        try:
            message_id = messages.get('leadboard_message_main')
            if message_id:
                self.lbmsg = await self.fivem_status_channel.fetch_message(message_id)
                self.msg_board_status = True
            else:
                await self.set_leadboard_msg()
        except:
            await self.set_leadboard_msg()
    
    async def set_leadboard_msg(self):
        """Create a new status message"""
        embed = discord.Embed(
            title="Division - X Status",
            color=discord.Color.red()
        )
        embed.set_image(url=STATUS_IMAGE_URL)
        
        # Clear channel and send new message
        await self.fivem_status_channel.purge(limit=None)
        msg = await self.fivem_status_channel.send(embed=embed)
        
        # Save message ID
        with open(self.message_file, "r") as f1:
            messages = json.load(f1)
        
        messages["leadboard_message_main"] = msg.id
        
        with open(self.message_file, "w") as f2:
            json.dump(messages, f2)
        
        await self.get_leadboard_msg()
    
    @tasks.loop(minutes=UPDATE_INTERVAL)
    async def fivem_status(self):
        """Check FiveM server status and update embed"""
        # Initialize guild and channel if not set
        if not self.guild:
            self.guild = self.bot.get_guild(GUILD_ID)
            if not self.guild:
                print(f"⚠️ Guild {GUILD_ID} not found!")
                return
        
        if not self.fivem_status_channel:
            self.fivem_status_channel = self.guild.get_channel(FIVEM_STATUS_CHANNEL_ID)
            if not self.fivem_status_channel:
                print(f"⚠️ Channel {FIVEM_STATUS_CHANNEL_ID} not found!")
                return
        
        # Check if message board is set up
        if not self.msg_board_status:
            await self.get_leadboard_msg()
        
        # Try to get server status
        try:
            Get_players = get(f'http://{FIVEM_SERVER_IP}:{FIVEM_SERVER_PORT}/players.json', timeout=5)
            Get_dynamic = get(f'http://{FIVEM_SERVER_IP}:{FIVEM_SERVER_PORT}/dynamic.json', timeout=5)
            players = Get_players.json()
            dynamic = Get_dynamic.json()
            status = "Online"
        except Exception as e:
            status = "Offline"
            players = []
            dynamic = {}
            print(f"FiveM server check error: {e}")
        
        # Create embed based on status
        if status == "Online":
            embed = discord.Embed(
                title="Division - X Status",
                color=discord.Color.from_str(EMBED_COLOR)
            )
            embed.add_field(name="Server Status", value="```🟩 Online```", inline=False)
            
            try:
                embed.add_field(
                    name="Players",
                    value=f"```{len(players)}/{dynamic.get('sv_maxclients', 'N/A')}```",
                    inline=True
                )
                embed.add_field(
                    name="Host Name",
                    value=f"```{dynamic.get('hostname', 'Division - X')}```",
                    inline=True
                )
            except:
                pass
            
            embed.set_image(url=STATUS_IMAGE_URL)
            embed.set_footer(text=f"The panel will be updated every {UPDATE_INTERVAL} minutes")
            
            # Add player list if there are players
            if len(players) > 0:
                str25 = ""
                str50 = ""
                str75 = ""
                str100 = ""
                str125 = ""
                str150 = ""
                
                for i, player in enumerate(players):
                    player_line = f"[{player['id']}] {player['name']}\n"
                    
                    if i < 25:
                        str25 += player_line
                    elif i < 50:
                        str50 += player_line
                    elif i < 75:
                        str75 += player_line
                    elif i < 100:
                        str100 += player_line
                    elif i < 125:
                        str125 += player_line
                    elif i < 150:
                        str150 += player_line
                
                # Add player lists to embed
                str_list = [str25, str50, str75, str100, str125, str150]
                for player_str in str_list:
                    if player_str != "":
                        embed.add_field(name="᲼", value=player_str, inline=False)
            
            embed.add_field(
                name="Connect Directly Using F8 Console",
                value=f"```connect {CONNECT_CODE}```",
                inline=False
            )
        
        else:  # Offline
            embed = discord.Embed(
                title="Division - X Status",
                description=f"Connect Directly Using F8 Console\n```connect {CONNECT_CODE}```",
                color=discord.Color.brand_red()
            )
            embed.add_field(name="Server Status", value="```🟥 Offline```", inline=False)
            embed.set_image(url=STATUS_IMAGE_URL)
            embed.set_footer(text=f"The panel will be updated every {UPDATE_INTERVAL} minutes")
        
        # Update the message
        try:
            if self.lbmsg:
                # Only update if embed changed
                if embed.to_dict() != self.lbmsg.embeds[0].to_dict():
                    await self.lbmsg.edit(embed=embed)
        except:
            # If message was deleted or error, recreate it
            await self.set_leadboard_msg()
            if embed.to_dict() != self.lbmsg.embeds[0].to_dict():
                await self.lbmsg.edit(embed=embed)
    
    @fivem_status.before_loop
    async def before_fivem_status(self):
        """Wait until bot is ready before starting the loop"""
        await self.bot.wait_until_ready()
    
    def find_user(self, identifiers):
        """Find Discord user from FiveM identifiers"""
        for identifier in identifiers:
            if str(identifier).startswith('discord:'):
                discord_id = str(identifier)[8:]
                member = self.bot.get_user(int(discord_id))
                return member
        return None


async def setup(bot):
    await bot.add_cog(FivemStatus(bot))
