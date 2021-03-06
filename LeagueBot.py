import discord
import os
import requests
import json

from datetime import datetime
import pytz

from discord.ext import commands

my_secret = ''
my_secret1 = 'RGAPI-0830d0d7-afdb-4c38-ac77-8e5d74b3f3dc'

# client = discord.Client()
bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
#     if message.content.startswith('$info'):
#         query = message.content.replace('$info ', "")
#         responseSummonerName = requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + query,
#         headers={
#             "X-Riot-Token": my_secret1
#         }
#         )
#         await message.channel.send(json.loads(responseSummonerName.text))

# @bot.command(pass_context=True)
# async def clear(ctx, amount=100):
#     channel = ctx.message.channel
#     messages = []
#     async for message in bot.logs_from(channel, limit=int(amount)):
#         messages.append(message)
#     await bot.delete_messages(messages)


@bot.command()
async def stats(ctx, arg):
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
    embed.add_field(name=soloQueue['queueType'],
                    value=soloQueue['tier'] + " " + soloQueue['rank'] + "\n" + str(soloQueue['leaguePoints']) + " LP",
                    inline=True)
    embed.add_field(name=flexQueue['queueType'],
                    value=flexQueue['tier'] + " " + flexQueue['rank'] + "\n" + str(flexQueue['leaguePoints']) + " LP",
                    inline=True)
    embed.add_field(name="Last Game Played", value=str(easternTimeStamp) + "\n" + lastMatchType, inline=False)

    # embed.add_field(name= "Test", value = "test\ntest\ntest", inline = True)

    await ctx.send(embed=embed)

    aatrox = requests.get("http://ddragon.leagueoflegends.com/cdn/11.20.1/data/en_US/champion/Aatrox.json")
    print(json.loads(aatrox.text)['data']['Aatrox']['image']['sprite'])

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     if message.content.startswith('!'):
#         #gold = "<:2005_Gold:899465447563493427>"
#         gold = discord.utils.get(message.guild.emojis, name = 'Grandmaster'.lower())
#         await message.channel.send(gold)
#         #await message.add_reaction(gold)

bot.run(my_secret)

