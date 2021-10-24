import discord
import os
import requests
import json
from discord.ext import commands
from discord.utils import get
from datetime import datetime
import pytz
import asyncio

discordKey = ''
my_secret1 = 'RGAPI-5ca291bd-bd74-4e3f-b97c-7c6ee3c8d201'
client = discord.Client()
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def matchhistory(ctx, arg):
    embed = discord.Embed(
        title="Title",
        description="This is a description",
        colour=discord.Colour.blue()
    )

    responseSummonerName = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + arg,
                                        headers={
                                            "X-Riot-Token": my_secret1
                                        }
                                        )
    hiddenId = json.loads(responseSummonerName.text)['id']
    puuId = json.loads(responseSummonerName.text)['puuid']

    responseLol = requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + hiddenId,
                               headers={
                                   "X-Riot-Token": my_secret1
                               }
                               )

    lastMatch = requests.get(
        "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuId + "/ids?start=0&count=20",
        headers={
            "X-Riot-Token": my_secret1
        }
        )

    lastTimePlayedTS = json.loads(lastMatch.text)[0]

    responseLastPlayed = requests.get("https://americas.api.riotgames.com/lol/match/v5/matches/" + lastTimePlayedTS,
                                      headers={
                                          "X-Riot-Token": my_secret1
                                      }
                                      )

    # This whole section is to last game played info [date/kda/match type]
    lastPlayedDate = json.loads(responseLastPlayed.text)['info']['gameEndTimestamp']
    lastMatchType = json.loads(responseLastPlayed.text)['info']['gameMode']
    lastMatchPlayer = json.loads(responseLastPlayed.text)['info']['participants']
    print(str(datetime.fromtimestamp(lastPlayedDate / 1000).strftime("%b %d %y, %H:%M:%S")))
    d = datetime.fromtimestamp(lastPlayedDate / 1000)
    tz = pytz.timezone("UTC")
    d_tz = tz.normalize(tz.localize(d))
    eastern = pytz.timezone('US/Eastern')
    eastern_time = d_tz.astimezone(eastern)
    # timeStamp = str(datetime.fromtimestamp(lastPlayedDate/1000).strftime("%b %d %y, %H:%M:%S"))
    easternTimeStamp = eastern_time.strftime("%b %d %Y")

    def matchedPuuId():
        matchedPuu = json.loads(responseLastPlayed.text)
        for id in range(0, len(matchedPuu['metadata']['participants'])):
            if matchedPuu['metadata']['participants'][id] != puuId:
                pass
            else:
                idTemp = id
        return matchedPuu['info']['participants'][idTemp]

    championIcon = "http://ddragon.leagueoflegends.com/cdn/11.20.1/img/champion/" + matchedPuuId()[
        'championName'] + ".png"

    summonerName = json.loads(responseSummonerName.text)['name']
    summonerLevel = json.loads(responseSummonerName.text)['summonerLevel']
    profileIcon = str(json.loads(responseSummonerName.text)['profileIconId'])
    gameVersion = json.loads(requests.get("https://ddragon.leagueoflegends.com/api/versions.json").text)[0]
    print(gameVersion)
    profileIconImage = "http://ddragon.leagueoflegends.com/cdn/11.20.1/img/profileicon/" + profileIcon + ".png"
    soloQueue = json.loads(responseLol.text)[1]
    flexQueue = json.loads(responseLol.text)[0]

    #This will create an emoji of the rank note: name of emoji has to match rank
    gold = discord.utils.get(ctx.guild.emojis, name=soloQueue['tier'].lower())


    embed.set_footer(text="This is a footer.")
    embed.set_image(url=championIcon)
    embed.set_thumbnail(url="https://static.u.gg/assets/lol/riot_static/11.20.1/img/champion/Xayah.png")
    embed.set_author(name=summonerName + " " + "Level - " + str(summonerLevel), icon_url=profileIconImage)
    embed.add_field(name="Blue Side",
                    value=str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[0]['championName'])) + " " + lastMatchPlayer[0]['summonerName'] + "\n"
                    + str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[1]['championName'])) + " " + lastMatchPlayer[1]['summonerName'] + "\n"
                    + str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[2]['championName'])) + " " + lastMatchPlayer[2]['summonerName'] + "\n"
                    + str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[3]['championName'])) + " " + lastMatchPlayer[3]['summonerName'] + "\n"
                    + str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[4]['championName'])) + " " + lastMatchPlayer[4]['summonerName'],
                    inline=True)

    embed.add_field(name="K/D/A",
                   value=str(lastMatchPlayer[0]['kills']) + "/" + str(lastMatchPlayer[0]['deaths']) + "/" + str(lastMatchPlayer[0]['assists']) + "\n"
                   + str(lastMatchPlayer[1]['kills']) + "/" + str(lastMatchPlayer[1]['deaths']) + "/" + str(lastMatchPlayer[1]['assists']) + "\n"
                   + str(lastMatchPlayer[2]['kills']) + "/" + str(lastMatchPlayer[2]['deaths']) + "/" + str(lastMatchPlayer[2]['assists']) + "\n"
                   + str(lastMatchPlayer[3]['kills']) + "/" + str(lastMatchPlayer[3]['deaths']) + "/" + str(lastMatchPlayer[3]['assists']) + "\n"
                   + str(lastMatchPlayer[4]['kills']) + "/" + str(lastMatchPlayer[4]['deaths']) + "/" + str(lastMatchPlayer[4]['assists']),
                   inline=True)

    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(name="Red Side",
                    value=str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[5]['championName'])) + " " + lastMatchPlayer[5]['summonerName'] + "\n"
                    + str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[6]['championName'])) + " " + lastMatchPlayer[6]['summonerName'] + "\n"
                    + str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[7]['championName'])) + " " + lastMatchPlayer[7]['summonerName'] + "\n"
                    + str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[8]['championName'])) + " " + lastMatchPlayer[8]['summonerName'] + "\n"
                    + str(discord.utils.get(ctx.guild.emojis, name=lastMatchPlayer[9]['championName'])) + " " + lastMatchPlayer[9]['summonerName'],
                    inline=True)

    embed.add_field(name="K/D/A",
                   value=str(lastMatchPlayer[5]['kills']) + "/" + str(lastMatchPlayer[5]['deaths']) + "/" + str(lastMatchPlayer[5]['assists']) + "\n"
                   + str(lastMatchPlayer[6]['kills']) + "/" + str(lastMatchPlayer[6]['deaths']) + "/" + str(lastMatchPlayer[6]['assists']) + "\n"
                   + str(lastMatchPlayer[7]['kills']) + "/" + str(lastMatchPlayer[7]['deaths']) + "/" + str(lastMatchPlayer[7]['assists']) + "\n"
                   + str(lastMatchPlayer[8]['kills']) + "/" + str(lastMatchPlayer[8]['deaths']) + "/" + str(lastMatchPlayer[8]['assists']) + "\n"
                   + str(lastMatchPlayer[9]['kills']) + "/" + str(lastMatchPlayer[9]['deaths']) + "/" + str(lastMatchPlayer[9]['assists']),
                   inline=True)

    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(name="Last Game Played", value=str(easternTimeStamp) + "\n" + lastMatchType, inline=False)

    # embed.add_field(name= "Test", value = "test\ntest\ntest", inline = True)

    f = discord.guild.Guild.emojis
    print(f)
    await ctx.send(embed=embed)
    msg = await ctx.send(f"<:JarvanIV:900593440620961852>")
    await msg.add_reaction("<:JarvanIV:900593440620961852>")

    checkmark = str(discord.utils.get(bot.emojis, name='Xayah'))
    await ctx.send(checkmark)


async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('.'):
        emoji = discord.utils.get(bot.emojis, name='Sejuani')
        await message.channel.send(str(emoji))


bot.run(discordKey)
