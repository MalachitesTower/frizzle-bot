import discord
from discord.ext import tasks
import os
from dotenv import load_dotenv
from datetime import datetime
from location import get_location, save_location, to_ebird_region, to_latlng, to_inaturalist_params
from ebird import get_recent_observations, get_rarebirds, get_historicbirds, format_observations
from synthesize import synthesize_ebird

import logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"{datetime.now()} — Logged in as {client.user}")
    if not weekly_ping.is_running():
        weekly_ping.start()

@tasks.loop(hours=168) #debug = seconds=30
async def weekly_ping():
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found. Check your CHANNEL_ID.")
        return
    await channel.send("Test ping — bot is alive.")
    print(f"{datetime.now()} — Weekly ping sent.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # ignore the bot's own messages

    # --- !setlocation ---
    if message.content.lower().startswith("!setlocation"):
        parts = message.content.split(" ", 1)
        if len(parts) < 2:
            await message.channel.send(
                "Please include a location. Examples:\n"
                "`!setlocation Hartford CT`\n"
                "`!setlocation 06101`\n"
                "`!setlocation 41.76,-72.68`"
            )
            return
        raw = parts[1].strip()
        success, response = save_location(message.author.id, raw)
        await message.channel.send(response)
    
    # --- !report ---
    if message.content.lower() == "!report":
        loc = get_location(message.author.id)
        if loc is None:
            await message.channel.send(
                "No location set. Use `!setlocation Hartford CT` first."
            )
            return

        lat, lng = to_latlng(loc)
        region = to_ebird_region(loc)
        today = datetime.now()
        sections = []

        obs, err = get_recent_observations(lat, lng)
        sections.append(format_observations(obs, title="Recent bird sightings (past 7 days)") if not err else f"Recent sightings unavailable: {err}")

        rare, err = get_rarebirds(lat, lng)
        sections.append(format_observations(rare, title="Rare birds observed in your area") if not err else f"Rare sightings unavailable: {err}")

        historic, err = get_historicbirds(region, today.year - 1, today.month, today.day)
        sections.append(format_observations(historic, title="Birds observed on this date last year in your area") if not err else f"Historic sightings unavailable: {err}")

        result = "\n\n".join(sections)
        result = synthesize_ebird(result)
        await message.channel.send(result)


    # --- !ping ---
    if message.content.lower() == "!ping":
        await message.channel.send("Pong.")

client.run(TOKEN)
