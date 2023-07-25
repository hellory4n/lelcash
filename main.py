import disnake as discord
from disnake import app_commands
from disnake.ext import commands, tasks
import os
import asyncio
import json
import random
from keep_alive import keep_alive

epic_cool_intents = discord.Intents.default()
epic_cool_intents.message_content = True
client = commands.Bot(command_prefix=commands.when_mentioned_or("l."), intents=epic_cool_intents)
client.remove_command("help")

@client.event
async def on_ready():
    await suffering.start()
    print("hi")

@client.command()
async def ping(ctx):
    await ctx.send(f"i'm definitely alive: latency is {round(client.latency * 1000)} ms")

@client.command()
async def help(ctx):
    cool_embed = discord.Embed(
        title="Cool lelclub bot™",
        description="`l.ping`: yeah\n`l.help`: this command\n`l.nominate`: become a candidate\n`l.dismiss`: stop being a candidate\n`l.vote`: vote omgogmogmg"
    )
    await ctx.send(embed=cool_embed)

cool_token = os.getenv("TOKEN")
version = os.getenv("VERSION")

# it's a loop :)
@tasks.loop(seconds = 30)
async def suffering():
    pain = [
        "Wii Are Resorting to Violence",
        "Mining & Crafting",
        "UnderCroch",
        "Overlook",
        "Galaxy Citizen",
        "Power Distance 5",
        "Pablo",
        "Squilliam Fancyson",
        "MOMAZOS DIEGO ADVENTURE 2",
        "Funcade",
        "Funcade Adventures"
    ]
    await client.change_presence(activity=discord.Game(f"{random.choice(pain)} on Is Tim"))

async def main():
    # create cool election data
    if version == "release":
        if not os.path.exists("/data/"):
            os.makedirs("/data/")
    
        if not os.path.exists("/data/election.json"):
            init = {"started": False, "candidates": {}, "votes": {}}
            with open("/data/election.json", "w") as json_file:
                json.dump(init, json_file)

    # now we actually run the bot
    client.load_extensions("./modules/")
    keep_alive()
    await client.start(cool_token)

asyncio.run(main())