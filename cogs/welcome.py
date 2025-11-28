import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io

# Configuration
WELCOME_CHANNEL_ID = 1440569097514647728  # Change this to your welcome channel ID

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def create_welcome_image(self):
        """Load welcome image without any text"""
        try:
            img_path = "cogs/assest/dx_welcome_2.png"
            with open(img_path, 'rb') as f:
                img_bytes = io.BytesIO(f.read())
            img_bytes.seek(0)
            return img_bytes
        except Exception as e:
            print(f"Error loading welcome image: {e}")
            return None
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when member joins"""
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            print(f"⚠️ Welcome channel {WELCOME_CHANNEL_ID} not found!")
            return
        
        try:
            img_bytes = await self.create_welcome_image()
            
            # Create formatted welcome message with emojis
            welcome_text = f"""Welcome {member.mention} to {member.guild.name}!

─────────────────────────────────

• Read Discord Rules:  <#1234567890123456789>
• Read Roleplay Rules:  <#1234567890123456789>
• Apply for Whitelist: <#1440569097694744671>
• Explore our server information and events.

─────────────────────────────────"""
            
            if img_bytes:
                file = discord.File(img_bytes, filename="welcome.png")
                await channel.send(content=welcome_text, file=file)
            else:
                await channel.send(content=welcome_text)
            
            print(f"✅ Sent welcome message for {member.name}")
        
        except Exception as e:
            print(f"❌ Error sending welcome message: {e}")
    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.mention}!')
    
    @commands.command()
    async def testwelcome(self, ctx):
        """Test the welcome message"""
        img_bytes = await self.create_welcome_image()
        
        welcome_text = f"""Welcome {ctx.author.mention} to {ctx.guild.name}!

─────────────────────────────────

• Read Discord Rules: # 📘 | <#1440569097514647734>
• Read Roleplay Rules: # 📘 | <#1440569097694744668>
• Apply for Whitelist: # 📋 | <#1440569097694744671>
• Explore our server information and events.

─────────────────────────────────"""
        
        if img_bytes:
            file = discord.File(img_bytes, filename="test_welcome.png")
            await ctx.send(content=welcome_text, file=file)
        else:
            await ctx.send(content=welcome_text)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
