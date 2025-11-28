import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
import regex as re
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


class ImageCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # ============= FANCY FONT MAPPINGS =============
        self.fonts = {
            'bold': {
                'normal': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
                'fancy': "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
                         "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘶𝘃𝘄𝘅𝘆𝘇"
                         "𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
            },

            'italic': {
                'normal': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                'fancy': "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡"
                         "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"
            },

            'bolditalic': {
                'normal': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
                'fancy': "𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕"
                         "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯"
            },

            'boldtitalic': {
                'normal': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
                'fancy': "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉"
                         "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣"
                         "𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
            },

            'normal': {
                'normal': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
                'fancy': "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            }
        }

    # Normalize all fancy fonts back to normal
    def normalize_text(self, text):
        for style, maps in self.fonts.items():
            table = str.maketrans(maps["fancy"], maps["normal"])
            text = text.translate(table)
        return text

    # Convert letters & numbers only
    def convert_to_fancy_text(self, text, font_style='bold'):
        if font_style not in self.fonts:
            font_style = 'bold'
        font = self.fonts[font_style]
        table = str.maketrans(font['normal'], font['fancy'])

        def replace(match):
            return match.group(0).translate(table)

        return re.sub(r"[A-Za-z0-9]", replace, text)

    # ============== TEST COMMAND ==============
    @commands.command()
    async def test(self, ctx, *, message="Hello"):
        clean = self.normalize_text(message)
        fancy = self.convert_to_fancy_text(clean, 'bold')
        await ctx.send(fancy)

    @app_commands.command(name="test")
    async def slash_test(self, interaction: discord.Interaction, message: str = "Hello"):
        clean = self.normalize_text(message)
        fancy = self.convert_to_fancy_text(clean, 'bold')
        await interaction.response.send_message(fancy)

    # ============== CHANGE CATEGORY NAMES ==============
    @app_commands.command(name="changecategories", description="Change all category names to fancy font")
    async def slash_changecategories(self, interaction: discord.Interaction, font_style: str = "bold"):

        if not is_authorized(interaction.user):
            return await interaction.response.send_message("❌ Not authorized!", ephemeral=True)

        categories = interaction.guild.categories
        await interaction.response.send_message("🔄 Updating category names...")

        changed = 0

        for cat in categories:
            try:
                clean = self.normalize_text(cat.name)
                new_name = self.convert_to_fancy_text(clean, font_style)
                final = new_name + " ꧂"

                if final != cat.name:
                    await cat.edit(name=final)
                    changed += 1

                await asyncio.sleep(3)

            except Exception as e:
                print("Rename Error:", e)

        await interaction.edit_original_response(
            content=f"✅ Successfully updated {changed} categories!"
        )

    # ============== REMOVE SUFFIX ꧂ FROM ALL CATEGORIES ==============
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def removecategorysuffix(self, ctx):

        removed = 0

        for c in ctx.guild.categories:
            try:
                if "꧂" in c.name:
                    await c.edit(name=c.name.replace("꧂", "").strip())
                    removed += 1

                await asyncio.sleep(3)

            except Exception as e:
                print(e)

        await ctx.send(f"✅ Removed ꧂ from {removed} categories")

    @app_commands.command(name="removecategorysuffix", description="Remove ꧂ from all category names")
    async def slash_removecategorysuffix(self, interaction: discord.Interaction):

        if not is_authorized(interaction.user):
            return await interaction.response.send_message("❌ Not authorized!", ephemeral=True)

        categories = interaction.guild.categories
        removed = 0

        await interaction.response.send_message("🔍 Removing suffix from all categories...")

        for c in categories:
            try:
                if "꧂" in c.name:
                    await c.edit(name=c.name.replace("꧂", "").strip())
                    removed += 1

                await asyncio.sleep(20)

            except Exception as e:
                print(e)

        await interaction.edit_original_response(
            content=f"✅ Removed ꧂ from **{removed}** categories!"
        )

    # ============== CHANGE EMOJIES OF ONE CHANNEL ==============
    @app_commands.command(
        name="changec",
        description="Change emojis of a channel name (remove old emojis and set new ones)"
    )
    async def slash_changec(
        self,
        interaction: discord.Interaction,
        channel: discord.abc.GuildChannel,
        newemojies: str
    ):
        if not is_authorized(interaction.user):
            return await interaction.response.send_message("❌ Not authorized!", ephemeral=True)

        old_name = channel.name

        clean_name = re.sub(r"[^\w\s\-]", "", old_name).strip()
        clean_name = re.sub(r"\s+", " ", clean_name)

        final_name = f"{newemojies} {clean_name}"

        try:
            await channel.edit(name=final_name)
            await interaction.response.send_message(
                f"✅ Updated channel name!\n**{old_name} → {final_name}**"
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to update channel: `{e}`",
                ephemeral=True
            )

    # ============== MULTIPLE CHANNELS (CATEGORY MODE) ==============
    @app_commands.command(
        name="changecmulti",
        description="Change emojis for ALL channels inside a category"
    )
    async def changecmulti(
        self,
        interaction: discord.Interaction,
        category: discord.CategoryChannel,
        newemojies: str
    ):
        if not is_authorized(interaction.user):
            return await interaction.response.send_message("❌ Not authorized!", ephemeral=True)

        channels = category.channels
        changed = 0

        await interaction.response.send_message(
            f"🔄 Updating **{len(channels)}** channels in `{category.name}`..."
        )

        for channel in channels:
            old = channel.name

            clean_name = re.sub(r"[^\w\s\-]", "", old).strip()
            clean_name = re.sub(r"\s+", " ", clean_name)

            new_name = f"{newemojies} {clean_name}"

            if new_name != old:
                try:
                    await channel.edit(name=new_name)
                    changed += 1
                    await asyncio.sleep(0)
                except Exception as e:
                    print("Rename Error:", e)

        await interaction.edit_original_response(
            content=f"✅ Updated **{changed}** channels in category **{category.name}**!"
        )


async def setup(bot):
    await bot.add_cog(ImageCommands(bot))
