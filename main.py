import discord
from dotenv import load_dotenv
import asyncio
from discord.ext import commands
import os
import requests
import aiohttp
import logging
from discord import app_commands, ui
from typing import Optional
import activetrackfile
import atcnotifyfile as atcnotifyfile
import atcinfo
import departure_arrivalboard

# sleep
load_dotenv(".env")
token = os.getenv("DISCORD_TOKEN")
channel_id = int(os.getenv("CHANNEL_ID"))
# guildid = os.getenv("guildid") - use it if you need to test commands with guilds

logging.basicConfig(filename="discord.log",filemode="w", level=logging.ERROR)
intents = discord.Intents.default()
# Guild = discord.Object(id=guildid)

bot = commands.Bot(command_prefix="/", intents=intents)

activetrackfile.activetrackcommand(bot)
atcnotifyfile.atcnotifycommands(bot)
atcinfo.atcinfocommand(bot)
departure_arrivalboard.departure_arrival_board_commands(bot)

@bot.event
async def on_ready():
    print(f"VatTracker is ready to operate!")
    channel = bot.get_channel(channel_id)
    await bot.tree.sync()
    activetrackfile.starttrackloop(bot)
    atcnotifyfile.atcnotifyloop(bot)
    if channel:
        await channel.send("hello world! run /help to look for commands!")
    else:
        print("channel not found")

@bot.tree.command(name="credits", description="Who built and supported this bot")
async def credits(interaction: discord.Interaction):
    creditsembed = discord.Embed(title="Credits")
    creditsembed.add_field(name="Creator", value="yourlunch321", inline=False)
    creditsembed.add_field(name="Friends who helped me along the way", value="**Argon** - thank u for server hosting and being a good friend \n**thereal** - the person who inspired me to learn programming\n**alphagolfcharlie** - help on the code")
    await interaction.response.send_message(embed=creditsembed)

@bot.tree.command(name="weather", description="Shows METAR data from an airport")
async def weather(interaction: discord.Interaction, airport: str):
    weatherwebsite = (f"https://aviationweather.gov/api/data/metar?ids={airport.upper()}&format=json")
    weatherdataraw = requests.get(weatherwebsite)
    if requests.get(weatherwebsite).status_code != 200:
        invalidairportembed = discord.Embed(title=f"{airport.upper()} is not an airport, or has no weather data.")
        await interaction.response.send_message(embed=invalidairportembed)
    else:
        weatherdatajson = weatherdataraw.json()
        weatherdata = weatherdatajson[0]
        weatherembed = discord.Embed(
            title=f"Weather data for {airport.upper()}",
            description=f"{weatherdata["name"]}, {weatherdata["lat"]}, {weatherdata["lon"]}",
            colour=discord.Color.dark_green()
        )
        weatherembed.add_field(name="Raw METAR", value=f"{weatherdata["rawOb"]}", inline=True)
        weatherembed.add_field(name="Flight Category", value=f"{weatherdata["fltCat"]}", inline=False)

        #winds and gusts
        gusts = weatherdata.get("wgst", None)
        if gusts is not None:
            weatherembed.add_field(name="Winds", value=f"{weatherdata["wdir"]}° at {weatherdata["wspd"]}kts, Gusting {weatherdata["wgst"]}kts", inline=False)
        else:
            weatherembed.add_field(name="Winds", value=f"{weatherdata["wdir"]}° at {weatherdata["wspd"]}kts", inline=False)
        
        #temperature and dew point
        weatherembed.add_field(name="Temperature", value=f"{weatherdata["temp"]}°C", inline=True)
        weatherembed.add_field(name="Dew Point", value=f"{weatherdata["dewp"]}°C", inline=True)

        #clouds
        cloudembedvalue = ""
        clouds_check = weatherdata.get("clouds", None)
        clouds_check_length = len(clouds_check)
        if clouds_check_length == 0:
            weatherembed.add_field(name="Clouds", value="No Clouds", inline=False)
        else:
            for clouds in weatherdata["clouds"]:
                cloudcover = clouds["cover"]
                cloudbase = clouds["base"]
                cloudembedvalue += f"{cloudcover} at {cloudbase}ft, "
            cloudembedvalue[:-2]
            weatherembed.add_field(name="Clouds", value=cloudembedvalue, inline=False)

        # inhg altimeter math
        inhgaltimeterunrounded = weatherdata["altim"] * 0.029529983071445
        inhgaltimeter = round(inhgaltimeterunrounded, 2)
        finalinhg = str(inhgaltimeter)
        # HPA altimeter rounding
        hparounded = round(int(weatherdata["altim"]), 0)
        hparoundedstr = str(hparounded)
        #altimeter input
        weatherembed.add_field(name="Altimeter - inHG", value=f"{finalinhg}", inline=True)
        weatherembed.add_field(name="Altimeter - hPA", value=f"{hparoundedstr}", inline=True)


        await interaction.response.send_message(embed=weatherembed)
        

@bot.tree.command(name="aircraftinfo", description="Shows information about an aircraft - fill in one search")
async def aircraftinfo(interaction: discord.Interaction, callsign:Optional[str] = None, cid:Optional[str] = None):
    #aircraftinfo was changed from /info cuz of stupid rhythm
    if callsign is None and cid is None:
        nocidorcallsignembed = discord.Embed(title="No CID or callsign input", description="Please input either a CID or callsign")
        await interaction.response.send_message(embed=nocidorcallsignembed)
    elif callsign is not None and cid is not None:
        bothcidandcallsignembed = discord.Embed(title="Both fields are filled in, please only fill in one")
        await interaction.response.send_message(embed=bothcidandcallsignembed)
    else:
        rawdata = requests.get('https://data.vatsim.net/v3/vatsim-data.json')
        data = rawdata.json()
        found_pilot = None
        if callsign is not None:
            for pilot in data["pilots"]:
                if pilot["callsign"].upper() == callsign.upper():
                    found_pilot = pilot
                    break
        elif cid is not None:
            for pilot in data["pilots"]:
                if pilot["cid"] == int(cid):
                    found_pilot = pilot
                    break
        if found_pilot: 
            flight_plan = found_pilot.get("flight_plan", {})
            longitude = found_pilot.get("longitude", {}) # done
            latitude = found_pilot.get("latitude", {}) # done
            realalt = found_pilot.get("altitude", {}) # done
            pilotname = found_pilot.get("name", {}) # done
            pilotCID = found_pilot.get("cid", {}) # done
            cruisespeed = flight_plan["cruise_tas"] # done
            longtype = flight_plan["aircraft_faa"] # done
            type = flight_plan["aircraft_short"] # done
            filedalt = flight_plan["altitude"] # done
            route = flight_plan["route"] # done
            depairport = flight_plan["departure"] # done
            ariairport = flight_plan["arrival"] # done

            # redefine callsign so i can use it for embed making
            callsign1 = found_pilot.get("name", {})
            
            # info collection done, now i format the embed

            infoembed = discord.Embed(
                title=f"Information about **{callsign1.upper()}**'s flight on VATSIM",
                description=f"{pilotname} - {pilotCID}",
                color=discord.Color.dark_purple()
            )
            infoembed.add_field(name=f"Callsign", value=f"{callsign1.upper()}", inline=True)
            infoembed.add_field(name=f"Aircraft Type", value=f"{type}", inline=True)
            infoembed.add_field(name=f"Aircraft Type - FAA", value=f"{longtype}", inline=True)
            infoembed.add_field(name=f"Route", value=f"{depairport} - {ariairport}", inline=True)
            infoembed.add_field(name=f"Filed Altitude", value=f"{filedalt}ft", inline=True)
            infoembed.add_field(name=f"Cruise Speed", value=f"{cruisespeed}kts", inline=True)
            infoembed.add_field(name=f"Filed Route", value=f"{route}", inline=False)
            infoembed.add_field(name=f"Longitude", value=f"{longitude}", inline=True)
            infoembed.add_field(name=f"Latitude", value=f"{latitude}", inline=True)
            infoembed.add_field(name=f"Real Altitude", value=f"{realalt}ft", inline=True)

            #the info embed is filled in and defined
            
            await interaction.response.send_message(embed=infoembed)
        else:
            if callsign is not None:
                noaircraftembed = discord.Embed(
                    title=f"No aircraft found",
                    description=f"{callsign.upper()} is not currently on the network."
                )
                await interaction.response.send_message(embed=noaircraftembed)
            elif cid is not None:
                cidstr = str(cid)
                noaicraftembedcid = discord.Embed(
                    title=f"No aicraft found",
                    description=f"{cidstr} is not currently on the network."
                )
                await interaction.response.send_message(embed=noaicraftembedcid)

bot.run(token)