import os
import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import pytz
from pytz import country_timezones

TOKEN = os.environ['DISCORD_TOKEN']

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Country to timezone mapping (simplified common countries)
COUNTRY_TIMEZONES = {
    'usa': 'America/New_York',
    'united states': 'America/New_York',
    'us': 'America/New_York',
    'america': 'America/New_York',
    'uk': 'Europe/London',
    'united kingdom': 'Europe/London',
    'england': 'Europe/London',
    'britain': 'Europe/London',
    'canada': 'America/Toronto',
    'australia': 'Australia/Sydney',
    'germany': 'Europe/Berlin',
    'france': 'Europe/Paris',
    'spain': 'Europe/Madrid',
    'italy': 'Europe/Rome',
    'netherlands': 'Europe/Amsterdam',
    'sweden': 'Europe/Stockholm',
    'norway': 'Europe/Oslo',
    'denmark': 'Europe/Copenhagen',
    'finland': 'Europe/Helsinki',
    'poland': 'Europe/Warsaw',
    'russia': 'Europe/Moscow',
    'turkey': 'Europe/Istanbul',
    'japan': 'Asia/Tokyo',
    'china': 'Asia/Shanghai',
    'india': 'Asia/Kolkata',
    'south korea': 'Asia/Seoul',
    'korea': 'Asia/Seoul',
    'singapore': 'Asia/Singapore',
    'thailand': 'Asia/Bangkok',
    'philippines': 'Asia/Manila',
    'indonesia': 'Asia/Jakarta',
    'malaysia': 'Asia/Kuala_Lumpur',
    'vietnam': 'Asia/Ho_Chi_Minh',
    'brazil': 'America/Sao_Paulo',
    'mexico': 'America/Mexico_City',
    'argentina': 'America/Buenos_Aires',
    'chile': 'America/Santiago',
    'colombia': 'America/Bogota',
    'peru': 'America/Lima',
    'south africa': 'Africa/Johannesburg',
    'egypt': 'Africa/Cairo',
    'nigeria': 'Africa/Lagos',
    'israel': 'Asia/Jerusalem',
    'saudi arabia': 'Asia/Riyadh',
    'uae': 'Asia/Dubai',
    'emirates': 'Asia/Dubai',
    'dubai': 'Asia/Dubai',
    'new zealand': 'Pacific/Auckland',
    'serbia': 'Europe/Belgrade'
}

def fmt(t):
    return t.strftime("%A at %-I:%M %p (%Z)")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🤖 Bot is ready and online!")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s).")
        print(f"📋 Available commands: /ping, /kingdom")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# Error handling
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"Command error for user {interaction.user}: {error}")
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    elif isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        await interaction.response.send_message("❌ I don't have the required permissions to run this command.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ An error occurred while processing the command.", ephemeral=True)
        print(f"Detailed error: {type(error).__name__}: {error}")

@bot.tree.command(name="ping", description="Test if the bot is responding")
async def ping(interaction: discord.Interaction):
    print(f"Ping command used by {interaction.user}")
    await interaction.response.send_message("🏓 Pong! Bot is online and working!")

@bot.tree.command(name="help", description="Show available commands and what they do")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Here are all the available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🏓 /ping", 
        value="Test if the bot is responding", 
        inline=False
    )
    embed.add_field(
        name="🏰 /kingdom", 
        value="Predict when the next kingdom will open based on current kingdom status", 
        inline=False
    )
    embed.add_field(
        name="❓ /help", 
        value="Show this help message", 
        inline=False
    )
    embed.set_footer(text="Kingdom prediction bot is ready to help!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kingdom", description="Calculate when a specific Rise of Kingdoms kingdom will open")
async def kingdom(interaction: discord.Interaction):
    print(f"Kingdom command used by {interaction.user}")
    await interaction.response.send_message("🌍 What country are you from?")

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    # Step 1: Get country
    try:
        country_msg = await bot.wait_for("message", check=check, timeout=60)
    except:
        await interaction.followup.send("⌛ You took too long to reply.")
        return

    country_input = country_msg.content.strip().lower()

    # Find timezone from country
    user_timezone = None
    for country_name, tz_name in COUNTRY_TIMEZONES.items():
        if country_name in country_input or country_input in country_name:
            user_timezone = pytz.timezone(tz_name)
            break

    if not user_timezone:
        await interaction.followup.send("❌ Sorry, I don't recognize that country. Please try a common country name like 'USA', 'UK', 'Germany', etc.")
        return

    # Step 2: Get latest kingdom number
    await interaction.followup.send("📢 What is the latest kingdom number that opened?")
    try:
        kingdom_msg = await bot.wait_for("message", check=check, timeout=60)
        latest_kingdom = int(kingdom_msg.content.strip())
    except:
        await interaction.followup.send("❌ Please enter a valid kingdom number.")
        return

    # Step 3: Get target kingdom number
    await interaction.followup.send("🎯 What kingdom number do you want to see the opening time for?")
    try:
        target_msg = await bot.wait_for("message", check=check, timeout=60)
        target_kingdom = int(target_msg.content.strip())
    except:
        await interaction.followup.send("❌ Please enter a valid kingdom number.")
        return

    if target_kingdom <= latest_kingdom:
        await interaction.followup.send(f"❌ Kingdom {target_kingdom} has already opened! Please choose a kingdom number higher than {latest_kingdom}.")
        return

    # Step 4: Get how long the kingdom has been open
    await interaction.followup.send("⏰ How long has the latest kingdom been open? (Reply like `19h6m`, `2h`, `45m`, or `1h30m`)")
    try:
        time_msg = await bot.wait_for("message", check=check, timeout=60)
    except:
        await interaction.followup.send("⌛ You took too long to reply.")
        return

    # Parse time input
    text = time_msg.content.lower().strip()
    hours, minutes = 0, 0

    try:
        if "h" in text and "m" in text:
            # Format like "19h6m" or "1h30m"
            h_part = text.split("h")[0]
            m_part = text.split("h")[1].replace("m", "")
            hours = int(h_part) if h_part.isdigit() else 0
            minutes = int(m_part) if m_part.isdigit() else 0
        elif "h" in text:
            # Format like "2h"
            hours = int(text.replace("h", ""))
        elif "m" in text:
            # Format like "45m"
            minutes = int(text.replace("m", ""))
        else:
            # Try to parse as just a number (assume hours)
            hours = int(text)
    except:
        await interaction.followup.send("❌ Invalid time format. Please use formats like `19h6m`, `2h`, `45m`, or `1h30m`")
        return

    elapsed_hours = hours + (minutes / 60.0)  # Convert to decimal hours
    now_utc = datetime.now(timezone.utc)

    # Calculate how many kingdoms ahead we need to go
    kingdoms_ahead = target_kingdom - latest_kingdom

    # Step 4: Subtract elapsed time from the first cycle
    first_cycle_earliest = 32 - elapsed_hours
    first_cycle_likely = 36 - elapsed_hours
    first_cycle_latest = 38 - elapsed_hours

    # Step 5: Add full cycles for extra kingdoms (if any)
    extra_kingdoms = kingdoms_ahead - 1  # First kingdom is already calculated above

    if extra_kingdoms > 0:
        # Add full cycles for each extra kingdom
        total_earliest = first_cycle_earliest + (extra_kingdoms * 32)
        total_likely = first_cycle_likely + (extra_kingdoms * 36)
        total_latest = first_cycle_latest + (extra_kingdoms * 38)
    else:
        total_earliest = first_cycle_earliest
        total_likely = first_cycle_likely
        total_latest = first_cycle_latest

    # Step 6: Convert into real-world time
    target_earliest = now_utc + timedelta(hours=total_earliest)
    target_likely = now_utc + timedelta(hours=total_likely)
    target_latest = now_utc + timedelta(hours=total_latest)

    # Convert to user's timezone
    earliest_local = target_earliest.astimezone(user_timezone)
    likely_local = target_likely.astimezone(user_timezone)
    latest_local = target_latest.astimezone(user_timezone)

    # Create detailed embed with specific dates
    embed = discord.Embed(
        title=f"🏰 Kingdom {target_kingdom} Opening Prediction",
        description=f"Based on Kingdom {latest_kingdom} being open for {hours}h {minutes}m\n({kingdoms_ahead} kingdoms ahead)",
        color=discord.Color.gold()
    )


    # Format dates with full details (12-hour format)
    earliest_formatted = earliest_local.strftime("%A, %B %d at %I:%M %p (%Z)")
    likely_formatted = likely_local.strftime("%A, %B %d at %I:%M %p (%Z)")
    latest_formatted = latest_local.strftime("%A, %B %d at %I:%M %p (%Z)")

    embed.add_field(name="🟢 Earliest (32h cycles)", value=earliest_formatted, inline=False)
    embed.add_field(name="🟡 Most Likely (36h cycles)", value=likely_formatted, inline=False)  
    embed.add_field(name="🔴 Latest (38h cycles)", value=latest_formatted, inline=False)

    # Add time until opening
    time_until_likely = target_likely - now_utc
    days = time_until_likely.days
    hours_until = time_until_likely.seconds // 3600
    minutes_until = (time_until_likely.seconds % 3600) // 60

    if days > 0:
        time_str = f"{days} days, {hours_until} hours, {minutes_until} minutes"
    else:
        time_str = f"{hours_until} hours, {minutes_until} minutes"

    embed.add_field(name="⏱️ Time Until Opening (Most Likely)", value=time_str, inline=False)
    embed.set_footer(text=f"Rise of Kingdoms Calculator • Times in {user_timezone.zone}")

    await interaction.followup.send(embed=embed)

bot.run(TOKEN)
