import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput, Select
import sqlite3
from datetime import datetime, timedelta
import os
import re
from PIL import Image, ImageDraw, ImageFont
import io

# ==================== CONFIGURATION ====================
# Fill in these IDs for your server
APPLICATION_ONLY_CHANNEL = 1440569097694744671  # Channel where applications are allowed
APPLICANT_ROLE_ID = 1234567890123456789  # Role given when someone applies
APPROVED_ROLE_ID = 1234567890123456789  # Role given when approved
REJECTED_ROLE_ID = None  # Optional: Role given when rejected (set to None if not used)
STAFF_REVIEW_CHANNEL = 1234567890123456789  # Channel where staff reviews applications
ANNOUNCEMENT_CHANNEL = 1440569097694744673  # Channel where accepted applications are announced
OPENAI_API_KEY = None  # Optional: Set your OpenAI API key for AI reviews, or leave None

# Cooldown settings
COOLDOWN_DAYS = 0

# Emoji Configuration (can be changed with /channelemoji command)
EMOJIS = {
    "apply": "📝",
    "applicant": "👤",
    "age": "🎂",
    "score": "📊",
    "reason": "📝",
    "ai": "🤖",
    "status": "📌",
    "applied": "📅",
    "reviewed_by": "👮",
    "reviewed_at": "🕒",
    "pending": "⏳",
    "accepted": "✅",
    "rejected": "❌",
    "cooldown": "⏰",
    "dashboard": "📊",
    "history": "📋",
    "warning": "⚠️",
    "error": "❌",
    "success": "✅",
    "info": "ℹ️"
}


class ApplicationDatabase:
    """Database handler for application system"""
    
    def __init__(self, db_name='bot_database.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create application tables"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                app_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                age INTEGER,
                reason TEXT,
                score INTEGER,
                ai_summary TEXT,
                status TEXT DEFAULT 'pending',
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed_by INTEGER,
                reviewed_at DATETIME
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_cooldowns (
                user_id INTEGER PRIMARY KEY,
                last_application DATETIME NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_messages (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                channel_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def add_application(self, user_id, username, age, reason, score, ai_summary, status):
        """Add a new application"""
        self.cursor.execute('''
            INSERT INTO applications (user_id, username, age, reason, score, ai_summary, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, age, reason, score, ai_summary, status))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_application_status(self, app_id, status, reviewed_by):
        """Update application status"""
        self.cursor.execute('''
            UPDATE applications 
            SET status = ?, reviewed_by = ?, reviewed_at = ?
            WHERE app_id = ?
        ''', (status, reviewed_by, datetime.now(), app_id))
        self.conn.commit()
    
    def get_application(self, app_id):
        """Get application by ID"""
        self.cursor.execute('SELECT * FROM applications WHERE app_id = ?', (app_id,))
        return self.cursor.fetchone()
    
    def get_user_applications(self, user_id):
        """Get all applications for a user"""
        self.cursor.execute('''
            SELECT * FROM applications 
            WHERE user_id = ? 
            ORDER BY applied_at DESC
        ''', (user_id,))
        return self.cursor.fetchall()
    
    def get_last_application_time(self, user_id):
        """Get last application time for cooldown check"""
        self.cursor.execute('''
            SELECT last_application FROM application_cooldowns 
            WHERE user_id = ?
        ''', (user_id,))
        result = self.cursor.fetchone()
        return datetime.fromisoformat(result[0]) if result else None
    
    def set_cooldown(self, user_id):
        """Set cooldown for user"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO application_cooldowns (user_id, last_application)
            VALUES (?, ?)
        ''', (user_id, datetime.now()))
        self.conn.commit()
    
    def get_dashboard_stats(self):
        """Get statistics for dashboard"""
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                AVG(score) as avg_score
            FROM applications
        ''')
        return self.cursor.fetchone()
    
    def get_apply_message(self):
        """Get stored apply message ID"""
        self.cursor.execute('SELECT channel_id, message_id FROM application_messages WHERE id = 1')
        return self.cursor.fetchone()
    
    def set_apply_message(self, channel_id, message_id):
        """Store apply message ID"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO application_messages (id, channel_id, message_id)
            VALUES (1, ?, ?)
        ''', (channel_id, message_id))
        self.conn.commit()
    
    def get_all_applications(self, status=None):
        """Get all applications, optionally filtered by status"""
        if status:
            self.cursor.execute('''
                SELECT * FROM applications 
                WHERE status = ?
                ORDER BY applied_at DESC
            ''', (status,))
        else:
            self.cursor.execute('''
                SELECT * FROM applications 
                ORDER BY applied_at DESC
            ''')
        return self.cursor.fetchall()
    
    def get_pending_applications(self):
        """Get all pending applications"""
        return self.get_all_applications('pending')


class ApplicationModal(Modal, title="Server Application"):
    """Modal for application form"""
    
    name_input = TextInput(
        label="Full Name",
        placeholder="Enter your name...",
        required=True,
        max_length=100
    )
    
    age_input = TextInput(
        label="Age",
        placeholder="Enter your age...",
        required=True,
        max_length=3
    )
    
    reason_input = TextInput(
        label="Why do you want to join?",
        placeholder="Tell us why you want to join our server...",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=1000
    )
    
    def __init__(self, cog):
        super().__init__()
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle application submission"""
        await interaction.response.defer(ephemeral=True)
        
        # Validate age
        try:
            age = int(self.age_input.value)
            if age < 1 or age > 120:
                raise ValueError
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Age",
                description="Please enter a valid age between 1 and 120.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Process application
        await self.cog.process_application(
            interaction,
            self.name_input.value,
            age,
            self.reason_input.value
        )


class ApplicationView(View):
    """View with Apply button"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label=f"{EMOJIS['apply']} Apply Now", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def apply_button(self, interaction: discord.Interaction, button: Button):
        """Handle apply button click"""
        # Check if in correct channel
        if interaction.channel_id != APPLICATION_ONLY_CHANNEL:
            embed = discord.Embed(
                title="❌ Wrong Channel",
                description=f"Applications can only be submitted in <#{APPLICATION_ONLY_CHANNEL}>",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check cooldown
        last_app = self.cog.db.get_last_application_time(interaction.user.id)
        if last_app:
            time_passed = datetime.now() - last_app
            if time_passed < timedelta(days=COOLDOWN_DAYS):
                time_left = timedelta(days=COOLDOWN_DAYS) - time_passed
                days_left = time_left.days
                hours_left = time_left.seconds // 3600
                
                embed = discord.Embed(
                    title="⏰ Application Cooldown",
                    description=f"You can apply again in **{days_left} days and {hours_left} hours**.",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Last Application", value=f"<t:{int(last_app.timestamp())}:R>")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Show application modal
        modal = ApplicationModal(self.cog)
        await interaction.response.send_modal(modal)


class ApplicationSelect(Select):
    """Dropdown to select an application to review"""
    
    def __init__(self, cog, applications):
        self.cog = cog
        self.applications = {str(app[0]): app for app in applications}  # app_id -> app data
        
        options = []
        for app in applications[:25]:  # Discord limit is 25 options
            app_id, user_id, username, age, reason, score, ai_summary, status, applied_at, reviewed_by, reviewed_at = app
            
            # Status emoji
            status_emoji = {"accepted": "✅", "rejected": "❌", "pending": "⏳"}.get(status, "❓")
            
            # Score color indicator
            if score >= 70:
                score_indicator = "🟢"
            elif score >= 50:
                score_indicator = "🟡"
            else:
                score_indicator = "🔴"
            
            options.append(
                discord.SelectOption(
                    label=f"{username} - Score: {score}/100",
                    description=f"{status_emoji} {status.upper()} | Applied: {applied_at[:10]}",
                    value=str(app_id),
                    emoji=score_indicator
                )
            )
        
        super().__init__(
            placeholder="Select an application to review...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle application selection"""
        app_id = int(self.values[0])
        app_data = self.applications[self.values[0]]
        
        # Show the selected application
        await self.cog.show_application_detail(interaction, app_data)


class ApplicationListView(View):
    """View with dropdown for application selection"""
    
    def __init__(self, cog, applications):
        super().__init__(timeout=300)  # 5 minute timeout
        self.add_item(ApplicationSelect(cog, applications))


class ReviewView(View):
    """View for staff to review applications"""
    
    def __init__(self, cog, app_id, user_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.app_id = app_id
        self.user_id = user_id
    
    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.success, custom_id="accept_app")
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        """Accept application"""
        await self.cog.handle_review(interaction, self.app_id, self.user_id, "accepted")
    
    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger, custom_id="reject_app")
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        """Reject application"""
        await self.cog.handle_review(interaction, self.app_id, self.user_id, "rejected")
    
    @discord.ui.button(label="📋 View History", style=discord.ButtonStyle.secondary, custom_id="view_history")
    async def history_button(self, interaction: discord.Interaction, button: Button):
        """View application history"""
        await self.cog.show_user_history(interaction, self.user_id)


class ApplicationSystem(commands.Cog):
    """Application System Cog"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = ApplicationDatabase()
        
        # Add persistent view
        self.bot.add_view(ApplicationView(self))
    
    async def cog_load(self):
        """Called when cog is loaded - check and setup apply message"""
        await self.bot.wait_until_ready()
        await self.ensure_apply_message()
    
    async def ensure_apply_message(self):
        """Ensure apply message exists in the application channel"""
        try:
            channel = self.bot.get_channel(APPLICATION_ONLY_CHANNEL)
            if not channel:
                print(f"⚠️ Application channel {APPLICATION_ONLY_CHANNEL} not found!")
                return
            
            # Check if we have a stored message
            stored = self.db.get_apply_message()
            message_exists = False
            
            if stored:
                stored_channel_id, stored_message_id = stored
                # Check if message still exists
                try:
                    message = await channel.fetch_message(stored_message_id)
                    message_exists = True
                    print(f"✅ Apply message found in channel {channel.name}")
                except:
                    print(f"⚠️ Stored apply message not found, creating new one...")
            
            # Create new message if needed
            if not message_exists:
                embed = discord.Embed(
                    title="📝 Server Applications",
                    description="Click the button below to submit your application to join our server!",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="📋 Requirements",
                    value="• Be honest in your application\n• Provide detailed answers\n• Meet our age requirements",
                    inline=False
                )
                embed.add_field(
                    name="⏰ Cooldown",
                    value=f"You can apply once every **{COOLDOWN_DAYS} days**",
                    inline=False
                )
                
                view = ApplicationView(self)
                message = await channel.send(embed=embed, view=view)
                
                # Store message ID
                self.db.set_apply_message(channel.id, message.id)
                print(f"✅ Created new apply message in {channel.name} (ID: {message.id})")
        
        except Exception as e:
            print(f"❌ Error ensuring apply message: {e}")
    
    def calculate_score(self, age, reason):
        """Calculate application score based on various factors"""
        score = 0
        
        # Age scoring (max 25 points)
        if 16 <= age <= 25:
            score += 25
        elif 13 <= age <= 30:
            score += 20
        elif age > 30:
            score += 15
        else:
            score += 5
        
        # Answer length scoring (max 25 points)
        reason_length = len(reason)
        if reason_length >= 200:
            score += 25
        elif reason_length >= 100:
            score += 20
        elif reason_length >= 50:
            score += 15
        else:
            score += 10
        
        # Keyword scoring (max 30 points)
        positive_keywords = [
            'community', 'friends', 'learn', 'help', 'contribute', 'active',
            'participate', 'enjoy', 'passion', 'interested', 'love', 'excited',
            'experience', 'grow', 'support', 'collaborate', 'share'
        ]
        
        reason_lower = reason.lower()
        keyword_count = sum(1 for keyword in positive_keywords if keyword in reason_lower)
        score += min(keyword_count * 5, 30)
        
        # Grammar and effort (max 20 points)
        # Check for proper sentences
        sentences = reason.split('.')
        if len(sentences) >= 3:
            score += 10
        
        # Check for capitalization
        if reason[0].isupper():
            score += 5
        
        # Check for no excessive caps
        if not re.search(r'[A-Z]{5,}', reason):
            score += 5
        
        return min(score, 100)
    
    def get_ai_summary(self, name, age, reason, score):
        """Get AI summary of application (or fallback to heuristics)"""
        if OPENAI_API_KEY:
            try:
                import openai
                openai.api_key = OPENAI_API_KEY
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are reviewing a server application. Provide a brief 2-sentence summary of the application quality."},
                        {"role": "user", "content": f"Name: {name}\nAge: {age}\nReason: {reason}\nScore: {score}"}
                    ],
                    max_tokens=100
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"AI Summary error: {e}")
        
        # Fallback to heuristic summary
        if score >= 70:
            return "Strong application with detailed reasoning and good engagement indicators. Recommended for approval."
        elif score >= 50:
            return "Moderate application. Shows interest but could provide more detail. Review carefully."
        else:
            return "Basic application. Lacks detail and engagement indicators. Consider requesting more information."
    
    async def process_application(self, interaction, name, age, reason):
        """Process and score application"""
        # Calculate score
        score = self.calculate_score(age, reason)
        
        # Get AI summary
        ai_summary = self.get_ai_summary(name, age, reason, score)
        
        # All applications go to staff review (no auto-accept/reject)
        status = "pending"
        
        # Save to database
        app_id = self.db.add_application(
            interaction.user.id,
            interaction.user.name,
            age,
            reason,
            score,
            ai_summary,
            status
        )
        
        # Set cooldown
        self.db.set_cooldown(interaction.user.id)
        
        # Create application embed
        embed = self.create_application_embed(app_id, name, age, reason, score, ai_summary, status)
        
        # Send all applications for staff review
        await self.send_for_review(interaction, app_id, embed)
    
    def create_application_embed(self, app_id, name, age, reason, score, ai_summary, status):
        """Create beautiful card-style application embed"""
        # Color based on score (for staff reference only)
        if score >= 70:
            color = discord.Color.green()
        elif score >= 50:
            color = discord.Color.orange()
        else:
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="📋 Application Submission",
            description=f"**Application ID:** `{app_id}`",
            color=color,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="👤 Name", value=name, inline=True)
        embed.add_field(name="🎂 Age", value=str(age), inline=True)
        embed.add_field(name="📊 Score", value=f"**{score}/100**", inline=True)
        embed.add_field(name="📝 Reason for Joining", value=reason[:1024], inline=False)
        embed.add_field(name="🤖 AI Summary", value=ai_summary, inline=False)
        embed.add_field(name="📌 Status", value=f"**{status.upper()}**", inline=False)
        
        return embed
    
    async def send_for_review(self, interaction, app_id, embed):
        """Send application for staff review"""
        guild = interaction.guild
        member = interaction.user
        
        # Add applicant role
        applicant_role = guild.get_role(APPLICANT_ROLE_ID)
        if applicant_role:
            await member.add_roles(applicant_role)
        
        # Send DM
        dm_embed = discord.Embed(
            title="⏳ Application Under Review",
            description="Your application is being reviewed by our staff team.",
            color=discord.Color.orange()
        )
        dm_embed.add_field(name="Application ID", value=f"`{app_id}`")
        dm_embed.add_field(name="What's Next?", value="You'll receive a notification once your application is reviewed.")
        
        try:
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Respond to interaction
        response_embed = discord.Embed(
            title="📋 Application Submitted",
            description="Your application is under review. You'll be notified once it's processed.",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=response_embed, ephemeral=True)
        
        # Send to staff channel with review buttons
        staff_channel = guild.get_channel(STAFF_REVIEW_CHANNEL)
        if staff_channel:
            embed.title = "⏳ Application Pending Review"
            embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=False)
            view = ReviewView(self, app_id, member.id)
            await staff_channel.send(embed=embed, view=view)
    
    async def handle_review(self, interaction, app_id, user_id, decision):
        """Handle staff review decision"""
        await interaction.response.defer()
        
        guild = interaction.guild
        member = guild.get_member(user_id)
        
        # Update database
        self.db.update_application_status(app_id, decision, interaction.user.id)
        
        if decision == "accepted":
            # Add approved role, remove applicant role
            approved_role = guild.get_role(APPROVED_ROLE_ID)
            applicant_role = guild.get_role(APPLICANT_ROLE_ID)
            
            if member:
                if approved_role:
                    await member.add_roles(approved_role)
                if applicant_role and applicant_role in member.roles:
                    await member.remove_roles(applicant_role)
            
            # Send DM
            if member:
                dm_embed = discord.Embed(
                    title="✅ Application Accepted!",
                    description="Congratulations! Your application has been accepted by our staff team.",
                    color=discord.Color.green()
                )
                dm_embed.add_field(name="Application ID", value=f"`{app_id}`")
                dm_embed.add_field(name="Reviewed By", value=interaction.user.mention)
                dm_embed.add_field(name="Reviewed At", value=f"<t:{int(datetime.now().timestamp())}:F>")
                
                try:
                    await member.send(embed=dm_embed)
                except:
                    pass
            
            # Update staff message
            response_embed = discord.Embed(
                title="✅ Application Accepted",
                description=f"Application `{app_id}` has been accepted",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            response_embed.add_field(name="👮 Reviewed By", value=interaction.user.mention, inline=True)
            response_embed.add_field(name="👤 Applicant", value=f"<@{user_id}>", inline=True)
            response_embed.add_field(name="🕒 Time", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=True)
            
            await interaction.followup.send(embed=response_embed)
            
            # Send announcement to announcement channel
            await self.send_acceptance_announcement(guild, member, app_id)
            
        else:  # rejected
            # Add rejected role if configured, remove applicant role
            applicant_role = guild.get_role(APPLICANT_ROLE_ID)
            
            if member:
                if REJECTED_ROLE_ID:
                    rejected_role = guild.get_role(REJECTED_ROLE_ID)
                    if rejected_role:
                        await member.add_roles(rejected_role)
                if applicant_role and applicant_role in member.roles:
                    await member.remove_roles(applicant_role)
            
            # Send DM
            if member:
                dm_embed = discord.Embed(
                    title="❌ Application Rejected",
                    description="Unfortunately, your application has been rejected.",
                    color=discord.Color.red()
                )
                dm_embed.add_field(name="Application ID", value=f"`{app_id}`")
                dm_embed.add_field(name="Reviewed By", value=interaction.user.mention)
                dm_embed.add_field(name="Reapply", value=f"You can reapply in {COOLDOWN_DAYS} days.")
                
                try:
                    await member.send(embed=dm_embed)
                except:
                    pass
            
            # Update staff message
            response_embed = discord.Embed(
                title="❌ Application Rejected",
                description=f"Application `{app_id}` has been rejected",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            response_embed.add_field(name="👮 Reviewed By", value=interaction.user.mention, inline=True)
            response_embed.add_field(name="👤 Applicant", value=f"<@{user_id}>", inline=True)
            response_embed.add_field(name="🕒 Time", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=True)
            
            await interaction.followup.send(embed=response_embed)
            
            # Send rejection announcement to rejection channel
            await self.send_rejection_announcement(guild, member, app_id)
    
    async def create_acceptance_image(self, member):
        """Load the boarding pass template and add applicant name and time"""
        try:
            # Load the existing boarding pass image (2850x1200)
            img_path = "cogs/assest/dx_visa_accept.png"
            img = Image.open(img_path)
            draw = ImageDraw.Draw(img)
            
            # Load bold fonts
            try:
                name_font = ImageFont.truetype("arialbd.ttf", 70)
                date_font = ImageFont.truetype("arialbd.ttf", 70)
                time_font = ImageFont.truetype("arialbd.ttf", 70)
            except:
                name_font = ImageFont.load_default()
                date_font = ImageFont.load_default()
                time_font = ImageFont.load_default()
            
            # Get user avatar
            avatar_bytes = None
            try:
                avatar_url = member.display_avatar.url
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(avatar_url) as resp:
                        if resp.status == 200:
                            avatar_bytes = await resp.read()
            except Exception as e:
                print(f"Error fetching avatar: {e}")
            
            # Add avatar to image if available
            if avatar_bytes:
                try:
                    avatar_img = Image.open(io.BytesIO(avatar_bytes))
                    # Resize avatar to fit the boarding pass (adjust size as needed)
                    avatar_size = (250, 250)  # Increased avatar size
                    avatar_img = avatar_img.resize(avatar_size, Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if not already
                    if avatar_img.mode != 'RGBA':
                        avatar_img = avatar_img.convert('RGBA')
                    
                    # Paste avatar onto boarding pass (adjust position as needed) - Square shape
                    avatar_position = (1617, 295)  # Adjust position based on your template
                    img.paste(avatar_img, avatar_position, avatar_img)
                except Exception as e:
                    print(f"Error processing avatar: {e}")
            
            # Text color #EB3900 (orange-red)
            text_color = (235, 57, 0)
            # Shadow color (light gray/black with transparency)
            shadow_color = (0, 0, 0, 100)  # Black with 100/255 opacity
            shadow_offset = 2  # Shadow offset in pixels
            
            # Add applicant name with shadow
            # NAME - Draw shadow first, then text on top
            draw.text((412 + shadow_offset, 587 + shadow_offset), member.display_name, fill=shadow_color, font=name_font)
            draw.text((412, 575), member.display_name, fill=text_color, font=name_font)
            
            # DATE - Draw shadow first, then text on top
            acceptance_date = datetime.now().strftime("%d %b %Y")
            draw.text((1095, 601), acceptance_date, fill=text_color, font=date_font)
            
            

            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
        except Exception as e:
            print(f"Error creating acceptance image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def create_rejection_image(self, member):
        """Load the rejection boarding pass template and add applicant name and time"""
        try:
            # Load the rejection boarding pass image
            img_path = "cogs/assest/dx_visa_reject.png"
            img = Image.open(img_path)
            draw = ImageDraw.Draw(img)
            
            # Load bold fonts
            try:
                name_font = ImageFont.truetype("arialbd.ttf", 70)
                date_font = ImageFont.truetype("arialbd.ttf", 70)
                time_font = ImageFont.truetype("arialbd.ttf", 70)
            except:
                name_font = ImageFont.load_default()
                date_font = ImageFont.load_default()
                time_font = ImageFont.load_default()
            
            # Get user avatar
            avatar_bytes = None
            try:
                avatar_url = member.display_avatar.url
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(avatar_url) as resp:
                        if resp.status == 200:
                            avatar_bytes = await resp.read()
            except Exception as e:
                print(f"Error fetching avatar: {e}")
            
            # Add avatar to image if available
            if avatar_bytes:
                try:
                    avatar_img = Image.open(io.BytesIO(avatar_bytes))
                    # Resize avatar to fit the boarding pass
                    avatar_size = (300, 300)
                    avatar_img = avatar_img.resize(avatar_size, Image.Resampling.LANCZOS)
                    
                    # Convert to RGBA if not already
                    if avatar_img.mode != 'RGBA':
                        avatar_img = avatar_img.convert('RGBA')
                    
                    # Paste avatar onto boarding pass - Square shape
                    avatar_position = (1622, 212)
                    img.paste(avatar_img, avatar_position, avatar_img)
                except Exception as e:
                    print(f"Error processing avatar: {e}")
            
            # Text color #EB3900 (orange-red)
            text_color = (235, 57, 0)
            # Shadow color (light gray/black with transparency)
            shadow_color = (0, 0, 0, 100)
            shadow_offset = 2
            
            # Add applicant name with shadow
            
            draw.text((400,583), member.display_name, fill=text_color, font=name_font)
            
            # DATE - Draw shadow first, then text on top
            rejection_date = datetime.now().strftime("%d %b %Y")
           
            draw.text((10589, 591), rejection_date, fill=text_color, font=date_font)
            
            # Save to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
        except Exception as e:
            print(f"Error creating rejection image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def send_acceptance_announcement(self, guild, member, app_id):
        """Send announcement to announcement channel when application is accepted"""
        try:
            announcement_channel = guild.get_channel(ANNOUNCEMENT_CHANNEL)
            if not announcement_channel:
                print(f"⚠️ Announcement channel {ANNOUNCEMENT_CHANNEL} not found!")
                return
            
            # Create the image
            img_bytes = await self.create_acceptance_image(member)
            
            # Send with image if available
            if img_bytes:
                file = discord.File(img_bytes, filename="welcome.png")
                await announcement_channel.send(
                    content=f"🎉 Please welcome {member.mention} to our community!",
                    file=file
                )
            else:
                # Send without image if creation failed
                await announcement_channel.send(
                    content=f"🎉 Please welcome {member.mention} to our community!"
                )
            
            print(f"✅ Sent acceptance announcement for {member.name} to {announcement_channel.name}")
        
        except Exception as e:
            print(f"❌ Error sending acceptance announcement: {e}")
    
    async def send_rejection_announcement(self, guild, member, app_id):
        """Send announcement to rejection channel when application is rejected"""
        try:
            rejection_channel = guild.get_channel(1440569097694744672)
            if not rejection_channel:
                print(f"⚠️ Rejection channel 1440569097694744672 not found!")
                return
            
            # Create the rejection image
            img_bytes = await self.create_rejection_image(member)
            
            # Send with image if available
            if img_bytes:
                file = discord.File(img_bytes, filename="rejection.png")
                await rejection_channel.send(
                    content=f"❌ Application rejected for {member.mention}",
                    file=file
                )
            else:
                # Send without image if creation failed
                await rejection_channel.send(
                    content=f"❌ Application rejected for {member.mention}"
                )
            
            print(f"✅ Sent rejection announcement for {member.name} to {rejection_channel.name}")
        
        except Exception as e:
            print(f"❌ Error sending rejection announcement: {e}")
    
    async def show_user_history(self, interaction, user_id):
        """Show application history for a user"""
        applications = self.db.get_user_applications(user_id)
        
        if not applications:
            embed = discord.Embed(
                title="📋 Application History",
                description="No applications found for this user.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 Application History",
            description=f"User: <@{user_id}> ({user_id})\nTotal Applications: **{len(applications)}**",
            color=discord.Color.blue()
        )
        
        for app in applications[:10]:  # Show last 10
            app_id, uid, username, age, reason, score, ai_summary, status, applied_at, reviewed_by, reviewed_at = app
            
            status_emoji = {"accepted": "✅", "rejected": "❌", "pending": "⏳"}.get(status, "❓")
            
            field_value = f"**Score:** {score}/100\n**Status:** {status_emoji} {status.upper()}\n**Date:** <t:{int(datetime.fromisoformat(applied_at).timestamp())}:R>"
            
            embed.add_field(
                name=f"Application #{app_id}",
                value=field_value,
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def show_application_detail(self, interaction, app_data):
        """Show detailed view of a single application with review buttons"""
        app_id, user_id, username, age, reason, score, ai_summary, status, applied_at, reviewed_by, reviewed_at = app_data
        
        # Color based on status
        if status == "accepted":
            color = discord.Color.green()
        elif status == "rejected":
            color = discord.Color.red()
        else:
            # Color based on score for pending
            if score >= 70:
                color = discord.Color.green()
            elif score >= 50:
                color = discord.Color.orange()
            else:
                color = discord.Color.red()
        
        embed = discord.Embed(
            title="📋 Application Details",
            description=f"**Application ID:** `{app_id}`",
            color=color,
            timestamp=datetime.fromisoformat(applied_at)
        )
        
        # User info
        embed.add_field(name="� Applicantv", value=f"<@{user_id}>\n`{username}`", inline=True)
        embed.add_field(name="🎂 Age", value=str(age), inline=True)
        embed.add_field(name="📊 Score", value=f"**{score}/100**", inline=True)
        
        # Status
        status_emoji = {"accepted": "✅", "rejected": "❌", "pending": "⏳"}.get(status, "❓")
        embed.add_field(name="📌 Status", value=f"{status_emoji} **{status.upper()}**", inline=True)
        
        # Applied date
        embed.add_field(name="📅 Applied", value=f"<t:{int(datetime.fromisoformat(applied_at).timestamp())}:R>", inline=True)
        
        # Reviewed info - show who and when if reviewed
        if reviewed_by and reviewed_at:
            embed.add_field(
                name="👮 Reviewed By", 
                value=f"<@{reviewed_by}>", 
                inline=True
            )
            embed.add_field(
                name="🕒 Reviewed At",
                value=f"<t:{int(datetime.fromisoformat(reviewed_at).timestamp())}:R>",
                inline=True
            )
        elif reviewed_by:
            # Just in case reviewed_at is missing
            embed.add_field(name="👮 Reviewed By", value=f"<@{reviewed_by}>", inline=True)
        
        # Add empty field for spacing if reviewed (to make it look better)
        if reviewed_by:
            embed.add_field(name="\u200b", value="\u200b", inline=True)
        
        # Reason
        embed.add_field(name="📝 Reason for Joining", value=reason[:1024], inline=False)
        
        # AI Summary
        embed.add_field(name="🤖 AI Summary", value=ai_summary, inline=False)
        
        # Add review buttons only if pending, otherwise show view history button
        if status == "pending":
            view = ReviewView(self, app_id, user_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            # For accepted/rejected, show a view with just history button
            view = View(timeout=300)
            history_button = Button(label="📋 View User History", style=discord.ButtonStyle.secondary)
            
            async def history_callback(button_interaction: discord.Interaction):
                await self.show_user_history(button_interaction, user_id)
            
            history_button.callback = history_callback
            view.add_item(history_button)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @commands.command(name='dashboard')
    async def dashboard(self, ctx):
        """Show application dashboard statistics"""
        stats = self.db.get_dashboard_stats()
        total, accepted, rejected, pending, avg_score = stats
        
        embed = discord.Embed(
            title="📊 Application Dashboard",
            description="Overview of all applications",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="📋 Total Applications", value=f"**{total or 0}**", inline=True)
        embed.add_field(name="✅ Accepted", value=f"**{accepted or 0}**", inline=True)
        embed.add_field(name="❌ Rejected", value=f"**{rejected or 0}**", inline=True)
        embed.add_field(name="⏳ Pending", value=f"**{pending or 0}**", inline=True)
        embed.add_field(name="📊 Average Score", value=f"**{avg_score:.1f}/100**" if avg_score else "**N/A**", inline=True)
        
        # Calculate acceptance rate
        if total and total > 0:
            acceptance_rate = (accepted / total) * 100 if accepted else 0
            embed.add_field(name="📈 Acceptance Rate", value=f"**{acceptance_rate:.1f}%**", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='apphistory')
    @commands.has_permissions(manage_guild=True)
    async def app_history(self, ctx, member: discord.Member):
        """Show full application history for a user"""
        await self.show_user_history(ctx, member.id)
    
    @app_commands.command(name="find", description="Find and review a user's application")
    @app_commands.describe(user="The user to search for")
    async def find_application(self, interaction: discord.Interaction, user: discord.Member):
        """Find a user's most recent application"""
        
        # Get user's applications
        applications = self.db.get_user_applications(user.id)
        
        if not applications:
            embed = discord.Embed(
                title="❌ No Applications Found",
                description=f"{user.mention} has not submitted any applications.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Get most recent application
        most_recent = applications[0]  # Already sorted by applied_at DESC
        
        # Show the application detail
        await self.show_application_detail(interaction, most_recent)
    
    @app_commands.command(name="application", description="View and manage applications")
    @app_commands.describe(
        person="Optional: View specific user's applications",
        status="Filter by status (pending/accepted/rejected)"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="Pending", value="pending"),
        app_commands.Choice(name="Accepted", value="accepted"),
        app_commands.Choice(name="Rejected", value="rejected"),
        app_commands.Choice(name="All", value="all")
    ])
    async def application_slash(
        self, 
        interaction: discord.Interaction, 
        person: discord.Member = None,
        status: app_commands.Choice[str] = None
    ):
        """View and manage applications"""
        
        # If person is specified, show their history
        if person:
            await self.show_user_history(interaction, person.id)
            return
        
        # Get applications based on status filter
        if status and status.value != "all":
            applications = self.db.get_all_applications(status.value)
            status_text = status.value.upper()
        else:
            applications = self.db.get_all_applications()
            status_text = "ALL"
        
        if not applications:
            embed = discord.Embed(
                title="📋 Applications",
                description=f"No {status_text.lower()} applications found.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create embed with application list
        embed = discord.Embed(
            title=f"📋 {status_text} Applications",
            description=f"Total: **{len(applications)}** applications\nSelect an application from the dropdown below to review.",
            color=discord.Color.blue()
        )
        
        # Add summary stats
        pending_count = sum(1 for app in applications if app[7] == "pending")
        accepted_count = sum(1 for app in applications if app[7] == "accepted")
        rejected_count = sum(1 for app in applications if app[7] == "rejected")
        
        embed.add_field(name="⏳ Pending", value=str(pending_count), inline=True)
        embed.add_field(name="✅ Accepted", value=str(accepted_count), inline=True)
        embed.add_field(name="❌ Rejected", value=str(rejected_count), inline=True)
        
        # Create view with dropdown
        view = ApplicationListView(self, applications)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @commands.command(name='setupapply')
    @commands.has_permissions(administrator=True)
    async def setup_apply(self, ctx):
        """Setup the apply button in the current channel"""
        if ctx.channel.id != APPLICATION_ONLY_CHANNEL:
            embed = discord.Embed(
                title="⚠️ Warning",
                description=f"This command should be used in <#{APPLICATION_ONLY_CHANNEL}>",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        # Delete old message if exists
        stored = self.db.get_apply_message()
        if stored:
            stored_channel_id, stored_message_id = stored
            try:
                old_message = await ctx.channel.fetch_message(stored_message_id)
                await old_message.delete()
                print(f"🗑️ Deleted old apply message")
            except:
                pass
        
        embed = discord.Embed(
            title="📝 Server Applications",
            description="Click the button below to submit your application to join our server!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Requirements",
            value="• Be honest in your application\n• Provide detailed answers\n• Meet our age requirements",
            inline=False
        )
        embed.add_field(
            name="⏰ Cooldown",
            value=f"You can apply once every **{COOLDOWN_DAYS} days**",
            inline=False
        )
        
        view = ApplicationView(self)
        message = await ctx.send(embed=embed, view=view)
        
        # Store message ID in database
        self.db.set_apply_message(ctx.channel.id, message.id)
        
        # Send confirmation
        confirm_embed = discord.Embed(
            title="✅ Setup Complete",
            description=f"Apply button has been set up! Message ID: `{message.id}`",
            color=discord.Color.green()
        )
        await ctx.send(embed=confirm_embed, delete_after=5)


    @app_commands.command(name="testimage", description="Test the acceptance boarding pass image")
    @commands.has_permissions(administrator=True)
    async def test_image(self, interaction: discord.Interaction):
        """Test the acceptance image generation"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Create test image with the user who ran the command
            img_bytes = await self.create_acceptance_image(interaction.user)
            
            if img_bytes:
                file = discord.File(img_bytes, filename="test_boarding_pass.png")
                
                embed = discord.Embed(
                    title="✅ Test Image Generated",
                    description="Here's how the acceptance boarding pass will look:",
                    color=discord.Color.green()
                )
                embed.set_image(url="attachment://test_boarding_pass.png")
                embed.add_field(name="Name", value=interaction.user.display_name, inline=True)
                embed.add_field(name="Date", value=datetime.now().strftime("%d %b %Y"), inline=True)
                embed.add_field(name="Time", value=datetime.now().strftime("%H:%M"), inline=True)
                
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)
            else:
                error_embed = discord.Embed(
                    title="❌ Error",
                    description="Failed to generate test image. Check console for errors.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
        
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to generate test image:\n```{str(e)}```",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            print(f"Test image error: {e}")
            import traceback
            traceback.print_exc()
    
    @app_commands.command(name="testreject", description="Test the rejection boarding pass image")
    @commands.has_permissions(administrator=True)
    async def test_reject_image(self, interaction: discord.Interaction):
        """Test the rejection image generation"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Create test rejection image with the user who ran the command
            img_bytes = await self.create_rejection_image(interaction.user)
            
            if img_bytes:
                file = discord.File(img_bytes, filename="test_rejection_pass.png")
                
                embed = discord.Embed(
                    title="❌ Test Rejection Image Generated",
                    description="Here's how the rejection boarding pass will look:",
                    color=discord.Color.red()
                )
                embed.set_image(url="attachment://test_rejection_pass.png")
                embed.add_field(name="Name", value=interaction.user.display_name, inline=True)
                embed.add_field(name="Date", value=datetime.now().strftime("%d %b %Y"), inline=True)
                embed.add_field(name="Time", value=datetime.now().strftime("%H:%M"), inline=True)
                
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)
            else:
                error_embed = discord.Embed(
                    title="❌ Error",
                    description="Failed to generate test rejection image. Check console for errors.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)
        
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to generate test rejection image:\n```{str(e)}```",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            print(f"Test rejection image error: {e}")
            import traceback
            traceback.print_exc()
    
    @app_commands.command(name="channelemoji", description="Change emojis used in application embeds")
    @app_commands.describe(emoji_type="Type of emoji to change", new_emoji="New emoji to use")
    @app_commands.choices(emoji_type=[
        app_commands.Choice(name="Apply Button (📝)", value="apply"),
        app_commands.Choice(name="Applicant (👤)", value="applicant"),
        app_commands.Choice(name="Age (🎂)", value="age"),
        app_commands.Choice(name="Score (📊)", value="score"),
        app_commands.Choice(name="Reason (📝)", value="reason"),
        app_commands.Choice(name="AI Summary (🤖)", value="ai"),
        app_commands.Choice(name="Status (📌)", value="status"),
        app_commands.Choice(name="Applied Date (📅)", value="applied"),
        app_commands.Choice(name="Reviewed By (👮)", value="reviewed_by"),
        app_commands.Choice(name="Reviewed At (🕒)", value="reviewed_at"),
        app_commands.Choice(name="Pending (⏳)", value="pending"),
        app_commands.Choice(name="Accepted (✅)", value="accepted"),
        app_commands.Choice(name="Rejected (❌)", value="rejected"),
        app_commands.Choice(name="Cooldown (⏰)", value="cooldown"),
        app_commands.Choice(name="Dashboard (📊)", value="dashboard"),
        app_commands.Choice(name="History (📋)", value="history"),
        app_commands.Choice(name="Warning (⚠️)", value="warning"),
        app_commands.Choice(name="Error (❌)", value="error"),
        app_commands.Choice(name="Success (✅)", value="success"),
        app_commands.Choice(name="Info (ℹ️)", value="info")
    ])
    @commands.has_permissions(administrator=True)
    async def change_emoji(
        self,
        interaction: discord.Interaction,
        emoji_type: app_commands.Choice[str],
        new_emoji: str
    ):
        """Change an emoji used in application embeds"""
        global EMOJIS
        
        old_emoji = EMOJIS.get(emoji_type.value, "❓")
        EMOJIS[emoji_type.value] = new_emoji
        
        embed = discord.Embed(
            title="✅ Emoji Updated",
            description=f"Successfully changed **{emoji_type.name}** emoji",
            color=discord.Color.green()
        )
        embed.add_field(name="Old Emoji", value=old_emoji, inline=True)
        embed.add_field(name="New Emoji", value=new_emoji, inline=True)
        embed.add_field(name="Type", value=f"`{emoji_type.value}`", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Update the apply button message if it exists
        try:
            stored = self.db.get_apply_message()
            if stored:
                channel_id, message_id = stored
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        message = await channel.fetch_message(message_id)
                        
                        # Recreate embed with new emojis
                        new_embed = discord.Embed(
                            title=f"{EMOJIS['apply']} Server Applications",
                            description="Click the button below to submit your application to join our server!",
                            color=discord.Color.blue()
                        )
                        new_embed.add_field(
                            name=f"{EMOJIS['history']} Requirements",
                            value="• Be honest in your application\n• Provide detailed answers\n• Meet our age requirements",
                            inline=False
                        )
                        new_embed.add_field(
                            name=f"{EMOJIS['cooldown']} Cooldown",
                            value=f"You can apply once every **{COOLDOWN_DAYS} days**",
                            inline=False
                        )
                        
                        view = ApplicationView(self)
                        await message.edit(embed=new_embed, view=view)
                        
                        confirm_embed = discord.Embed(
                            title=f"{EMOJIS['success']} Apply Message Updated",
                            description="The apply button message has been updated with new emojis!",
                            color=discord.Color.green()
                        )
                        await interaction.followup.send(embed=confirm_embed, ephemeral=True)
                    except:
                        pass
        except:
            pass


async def setup(bot):
    await bot.add_cog(ApplicationSystem(bot))
