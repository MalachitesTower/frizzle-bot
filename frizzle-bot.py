import asyncio
import discord
from discord.ext import tasks
import os
from dotenv import load_dotenv
from datetime import datetime
from location import get_location, save_location, to_ebird_region, to_latlng, to_inaturalist_params
from ebird import get_ebird_recent_obs, get_ebird_rare_birds as get_ebird_rare_obs, get_ebird_historic_birds as get_ebird_historic_obs, format_ebird_obs
from inat import get_inat_recent_obs, get_inat_rare_obs, get_inat_historic_obs, format_inat_obs
from synthesize import synthesize_ebird, synthesize_inat, synthesize_all

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

    # --- !bird ---
    if message.content.lower() == "!bird":
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

        status = await message.channel.send("Fetching eBird observations...")

        obs, err = await asyncio.to_thread(get_ebird_recent_obs, lat, lng)
        sections.append(format_ebird_obs(obs, title="Recent bird sightings (past 7 days)") if not err else f"Recent sightings unavailable: {err}")

        rare, err = await asyncio.to_thread(get_ebird_rare_obs, lat, lng)
        sections.append(format_ebird_obs(rare, title="Rare birds observed in your area") if not err else f"Rare sightings unavailable: {err}")

        historic, err = await asyncio.to_thread(get_ebird_historic_obs, region, today.year - 1, today.month, today.day)
        sections.append(format_ebird_obs(historic, title="Birds observed on this date last year in your area") if not err else f"Historic sightings unavailable: {err}")

        status = await message.channel.send("Synthesizing natural language output..")
        result = "\n\n".join(sections)
        result = await asyncio.to_thread(synthesize_ebird, result)
        status = await message.channel.send("Done.")
        await message.channel.send(result)

    # --- !inat ---
    if message.content.lower() == "!inat":
        loc = get_location(message.author.id)
        if loc is None:
            await message.channel.send(
                "No location set. Use `!setlocation Hartford CT` first."
            )
            return

        inat_params = to_inaturalist_params(loc)
        sections = []

        status = await message.channel.send("Fetching iNaturalist observations...")

        inat_obs, err = await asyncio.to_thread(get_inat_recent_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"])
        sections.append(format_inat_obs(inat_obs, title="Recent nature observations near you (past 7 days)") if not err else f"iNaturalist observations unavailable: {err}")

        inat_obs, err = await asyncio.to_thread(get_inat_rare_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"])
        sections.append(format_inat_obs(inat_obs, title="Threatened species observed near you (past 7 days)") if not err else f"iNaturalist observations unavailable: {err}")

        inat_obs, err = await asyncio.to_thread(get_inat_historic_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"])
        sections.append(format_inat_obs(inat_obs, title="Nature observations observed this week one year ago near you") if not err else f"iNaturalist observations unavailable: {err}")

        status = await message.channel.send("Synthesizing natural language output...")
        result = "\n\n".join(sections)
        result = await asyncio.to_thread(synthesize_inat, result)
        status = await message.channel.send("Done.")
        await message.channel.send(result)

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
        inat_params = to_inaturalist_params(loc)
        today = datetime.now()
        sections = []

        status = await message.channel.send("Fetching eBird observations...")

        obs, err = await asyncio.to_thread(get_ebird_recent_obs, lat, lng)
        sections.append(format_ebird_obs(obs, title="Recent bird observations near you (past 7 days)") if not err else f"Recent sightings unavailable: {err}")

        rare, err = await asyncio.to_thread(get_ebird_rare_obs, lat, lng)
        sections.append(format_ebird_obs(rare, title="Rare birds observed in your area") if not err else f"Rare sightings unavailable: {err}")

        historic, err = await asyncio.to_thread(get_ebird_historic_obs, region, today.year - 1, today.month, today.day)
        sections.append(format_ebird_obs(historic, title="Birds observed on this date last year in your area") if not err else f"Historic sightings unavailable: {err}")

        status = await message.channel.send("Fetching iNaturalist observations...")

        inat_obs, err = await asyncio.to_thread(get_inat_recent_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"])
        sections.append(format_inat_obs(inat_obs, title="Recent nature observations near you (past 7 days)") if not err else f"iNaturalist observations unavailable: {err}")

        inat_obs, err = await asyncio.to_thread(get_inat_rare_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"])
        sections.append(format_inat_obs(inat_obs, title="Threatened species observed near you (past 7 days)") if not err else f"iNaturalist observations unavailable: {err}")

        inat_obs, err = await asyncio.to_thread(get_inat_historic_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"])
        sections.append(format_inat_obs(inat_obs, title="Nature observations observed this week one year ago near you") if not err else f"iNaturalist observations unavailable: {err}")

        status = await message.channel.send("Synthesizing natural language output...")
        result = "\n\n".join(sections)
        result = await asyncio.to_thread(synthesize_all, result)
        status = await message.channel.send(content="Done.")
        await message.channel.send(result)


# --- !stats ---
    if message.content.lower().startswith("!stats"):
        loc = get_location(message.author.id)
        if loc is None:
            await message.channel.send(
                "No location set. Use `!setlocation Hartford CT` first."
            )
            return

        parts = message.content.strip().split()
        filter_key = parts[1].lower() if len(parts) > 1 else "all"

        valid_keys = {"ebird_recent", "ebird_rare", "ebird_historic", "inat_recent", "inat_rare", "inat_historic"}
        if filter_key != "all" and filter_key not in valid_keys:
            await message.channel.send(
                f"Unknown source `{filter_key}`. Valid options: `all`, `ebird_recent`, `ebird_rare`, `ebird_historic`, `inat_recent`, `inat_rare`, `inat_historic`"
            )
            return

        def run(key):
            return filter_key == "all" or filter_key == key

        lat, lng = to_latlng(loc)
        region = to_ebird_region(loc)
        inat_params = to_inaturalist_params(loc)
        today = datetime.now()
        lines = []

        def fmt_stats(label, stats, err):
            if err:
                return f"**{label}**: unavailable — {err}"
            p = stats["params"]
            dr = stats["date_range"]
            date_str = f"{dr['earliest']} to {dr['latest']}" if dr else "n/a"
            pages_str = f"\n  Pages fetched: {stats['pages_fetched']}" if "pages_fetched" in stats else ""
            return (
                f"**{label}**\n"
                f"  Params: {p}\n"
                f"  Observations: {stats['num_observations']} across {stats['num_locations']} location(s){pages_str}\n"
                f"  Date range: {date_str}"
            )

        status = await message.channel.send("Fetching stats...")

        if run("ebird_recent"):
            stats, err = await asyncio.to_thread(get_ebird_recent_obs, lat, lng, stats_only=True)
            lines.append(fmt_stats("eBird recent", stats, err))

        if run("ebird_rare"):
            stats, err = await asyncio.to_thread(get_ebird_rare_obs, lat, lng, stats_only=True)
            lines.append(fmt_stats("eBird rare", stats, err))

        if run("ebird_historic"):
            stats, err = await asyncio.to_thread(get_ebird_historic_obs, region, today.year - 1, today.month, today.day, stats_only=True)
            lines.append(fmt_stats("eBird historic", stats, err))

        if run("inat_recent"):
            stats, err = await asyncio.to_thread(get_inat_recent_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"], stats_only=True)
            lines.append(fmt_stats("iNaturalist recent", stats, err))

        if run("inat_rare"):
            stats, err = await asyncio.to_thread(get_inat_rare_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"], stats_only=True)
            lines.append(fmt_stats("iNaturalist rare", stats, err))

        if run("inat_historic"):
            stats, err = await asyncio.to_thread(get_inat_historic_obs, inat_params["lat"], inat_params["lng"], radius_km=inat_params["radius"], stats_only=True)
            lines.append(fmt_stats("iNaturalist historic", stats, err))

        status = await message.channel.send("Done.")
        await message.channel.send("\n\n".join(lines))

    # --- !ping ---
    if message.content.lower() == "!ping":
        await message.channel.send("Pong.")

client.run(TOKEN)