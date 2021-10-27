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
my_secret1 = ''
client = discord.Client()
bot = commands.Bot(command_prefix='.')
guildIds = ['901567864639725588', '900593820738125855', '900592595120574475', '447868326820184074', '902107837910618142', '902108674431012894', '902033574637752321', '902032500023521301']
emojiDictionary = {}
itemEmojiDictionary = {}
items = {}
itemsTestStatements = {}
summonerIndex = range(10)
itemIndex = range(7)
print(summonerIndex)
itemApi = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()

async def matchhistory(ctx, arg):
    for gId in guildIds:
        abc = await bot.fetch_guild(gId)
        for emote in abc.emojis:
            emojiDictionary[str(emote.name)] = str(emote.id)

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
    winLossBlue = json.loads(responseLastPlayed.text)['info']['teams'][0]
    winLossRed = json.loads(responseLastPlayed.text)['info']['teams'][1]

    def blueSideResult():
        if winLossBlue['win'] == True:
            return " <WIN>"
        elif winLossBlue['win'] == False:
            return " <LOSS>"

    def redSideResult():
        if winLossRed['win'] == True:
            return " <WIN>"
        elif winLossRed['win'] == False:
            return " <LOSS>"
    print(str(datetime.fromtimestamp(lastPlayedDate / 1000).strftime("%b %d %y, %H:%M:%S")))
    d = datetime.fromtimestamp(lastPlayedDate / 1000)
    tz = pytz.timezone("UTC")
    d_tz = tz.normalize(tz.localize(d))
    eastern = pytz.timezone('US/Eastern')
    eastern_time = d_tz.astimezone(eastern)
    # timeStamp = str(datetime.fromtimestamp(lastPlayedDate/1000).strftime("%b %d %y, %H:%M:%S"))
    easternTimeStamp = eastern_time.strftime("%b %d %Y")

    itemString = {}

    for i in summonerIndex:
        itemsTestStatements[str(i)] = [str(lastMatchPlayer[i]['item0']), str(lastMatchPlayer[i]['item1']), str(lastMatchPlayer[i]['item2']),
        str(lastMatchPlayer[i]['item3']), str(lastMatchPlayer[i]['item4']), str(lastMatchPlayer[i]['item5']), str(lastMatchPlayer[i]['item6'])]
        for m in itemIndex:
            if itemsTestStatements[str(i)][m] == '0':
                itemsTestStatements[str(i)][m] = "bnk"
            else:
                continue

    for o in range(10):
        itemString[str(o)] = [str(discord.utils.get(bot.emojis, name=str(itemsTestStatements[str(o)][0]))),
        str(discord.utils.get(bot.emojis, name=str(itemsTestStatements[str(o)][1]))),
        str(discord.utils.get(bot.emojis, name=str(itemsTestStatements[str(o)][2]))),
        str(discord.utils.get(bot.emojis, name=str(itemsTestStatements[str(o)][3]))),
        str(discord.utils.get(bot.emojis, name=str(itemsTestStatements[str(o)][4]))),
        str(discord.utils.get(bot.emojis, name=str(itemsTestStatements[str(o)][5]))),
        str(discord.utils.get(bot.emojis, name=str(itemsTestStatements[str(o)][6])))]
        i += 1
    print(str(discord.utils.get(bot.emojis, name=str(lastMatchPlayer[0]['item1']))))
    print(itemString)
    print(itemsTestStatements)
    print(itemString['0'][1], itemString['0'][2])
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

    embed = discord.Embed(
        title="",
        description="",
        colour=discord.Colour.blue()
    )
    # embed = discord.Embed(
    #     title="Last Game Played",
    #     description=lastMatchType + "\n" + str(easternTimeStamp),
    #     colour=discord.Colour.blue()
    # )

    embed.set_footer(text="This is a footer.")
    embed.set_image(url=championIcon)
    embed.set_thumbnail(url="https://static.u.gg/assets/lol/riot_static/11.20.1/img/champion/Xayah.png")
    embed.set_author(name=summonerName + " " + "<Level " + str(summonerLevel) + ">", icon_url=profileIconImage)
    embed.add_field(name = "Last Game Played",
                    value = lastMatchType + "\n" + str(easternTimeStamp),
                    inline=False)
    embed.add_field(name="Blue Side" + blueSideResult(),
                    value=str(discord.utils.get(bot.emojis, name=lastMatchPlayer[0]['championName'])) + " " + lastMatchPlayer[0]['summonerName'] + "\n"
                    + str(discord.utils.get(bot.emojis, name=lastMatchPlayer[1]['championName'])) + " " + lastMatchPlayer[1]['summonerName'] + "\n"
                    + str(discord.utils.get(bot.emojis, name=lastMatchPlayer[2]['championName'])) + " " + lastMatchPlayer[2]['summonerName'] + "\n"
                    + str(discord.utils.get(bot.emojis, name=lastMatchPlayer[3]['championName'])) + " " + lastMatchPlayer[3]['summonerName'] + "\n"
                    + str(discord.utils.get(bot.emojis, name=lastMatchPlayer[4]['championName'])) + " " + lastMatchPlayer[4]['summonerName'],
                    inline=True)

    embed.add_field(name="K/D/A",
                   value=str(lastMatchPlayer[0]['kills']) + "/" + str(lastMatchPlayer[0]['deaths']) + "/" + str(lastMatchPlayer[0]['assists']) + "\n"
                   + str(lastMatchPlayer[1]['kills']) + "/" + str(lastMatchPlayer[1]['deaths']) + "/" + str(lastMatchPlayer[1]['assists']) + "\n"
                   + str(lastMatchPlayer[2]['kills']) + "/" + str(lastMatchPlayer[2]['deaths']) + "/" + str(lastMatchPlayer[2]['assists']) + "\n"
                   + str(lastMatchPlayer[3]['kills']) + "/" + str(lastMatchPlayer[3]['deaths']) + "/" + str(lastMatchPlayer[3]['assists']) + "\n"
                   + str(lastMatchPlayer[4]['kills']) + "/" + str(lastMatchPlayer[4]['deaths']) + "/" + str(lastMatchPlayer[4]['assists']),
                   inline=True)

    embed.add_field(name = "Items",
                    value = itemString[str(0)][0] + itemString[str(0)][1] +
                            itemString[str(0)][2] + itemString[str(0)][3] +
                            itemString[str(0)][4] + itemString[str(0)][5] +
                            itemString[str(0)][6] + "\n" +
                            itemString[str(1)][0] + itemString[str(1)][1] +
                            itemString[str(1)][2] + itemString[str(1)][3] +
                            itemString[str(1)][4] + itemString[str(1)][5] +
                            itemString[str(1)][6] + "\n" +
                            itemString[str(2)][0] + itemString[str(2)][1] +
                            itemString[str(2)][2] + itemString[str(2)][3] +
                            itemString[str(2)][4] + itemString[str(2)][5] +
                            itemString[str(2)][6] + "\n" +
                            itemString[str(3)][0] + itemString[str(3)][1] +
                            itemString[str(3)][2] + itemString[str(3)][3] +
                            itemString[str(3)][4] + itemString[str(3)][5] +
                            itemString[str(3)][6] + "\n" +
                            itemString[str(4)][0] + itemString[str(4)][1] +
                            itemString[str(4)][2] + itemString[str(4)][3] +
                            itemString[str(4)][4] + itemString[str(4)][5] +
                            itemString[str(4)][6],
                    inline = True)

    embed.add_field(name="Red Side" + redSideResult(),
                    value=str(discord.utils.get(bot.emojis, name=lastMatchPlayer[5]['championName'])) + " " + lastMatchPlayer[5]['summonerName'] + "\n"
                    + str(discord.utils.get(bot.emojis, name=lastMatchPlayer[6]['championName'])) + " " + lastMatchPlayer[6]['summonerName'] + "\n"
                    + str(discord.utils.get(bot.emojis, name=lastMatchPlayer[7]['championName'])) + " " + lastMatchPlayer[7]['summonerName'] + "\n"
                    + str(discord.utils.get(bot.emojis, name=lastMatchPlayer[8]['championName'])) + " " + lastMatchPlayer[8]['summonerName'] + "\n"
                    + str(discord.utils.get(bot.emojis, name=lastMatchPlayer[9]['championName'])) + " " + lastMatchPlayer[9]['summonerName'],
                    inline=True)

    embed.add_field(name="K/D/A",
                   value=str(lastMatchPlayer[5]['kills']) + "/" + str(lastMatchPlayer[5]['deaths']) + "/" + str(lastMatchPlayer[5]['assists']) + "\n"
                   + str(lastMatchPlayer[6]['kills']) + "/" + str(lastMatchPlayer[6]['deaths']) + "/" + str(lastMatchPlayer[6]['assists']) + "\n"
                   + str(lastMatchPlayer[7]['kills']) + "/" + str(lastMatchPlayer[7]['deaths']) + "/" + str(lastMatchPlayer[7]['assists']) + "\n"
                   + str(lastMatchPlayer[8]['kills']) + "/" + str(lastMatchPlayer[8]['deaths']) + "/" + str(lastMatchPlayer[8]['assists']) + "\n"
                   + str(lastMatchPlayer[9]['kills']) + "/" + str(lastMatchPlayer[9]['deaths']) + "/" + str(lastMatchPlayer[9]['assists']),
                   inline=True)

    embed.add_field(name = "Items",
                    value = itemString[str(5)][0] + itemString[str(5)][1] +
                            itemString[str(5)][2] + itemString[str(5)][3] +
                            itemString[str(5)][4] + itemString[str(5)][5] +
                            itemString[str(5)][6] + "\n" +
                            itemString[str(6)][0] + itemString[str(6)][1] +
                            itemString[str(6)][2] + itemString[str(6)][3] +
                            itemString[str(6)][4] + itemString[str(6)][5] +
                            itemString[str(6)][6] + "\n" +
                            itemString[str(7)][0] + itemString[str(7)][1] +
                            itemString[str(7)][2] + itemString[str(7)][3] +
                            itemString[str(7)][4] + itemString[str(7)][5] +
                            itemString[str(7)][6] + "\n" +
                            itemString[str(8)][0] + itemString[str(8)][1] +
                            itemString[str(8)][2] + itemString[str(8)][3] +
                            itemString[str(8)][4] + itemString[str(8)][5] +
                            itemString[str(8)][6] + "\n" +
                            itemString[str(9)][0] + itemString[str(9)][1] +
                            itemString[str(9)][2] + itemString[str(9)][3] +
                            itemString[str(9)][4] + itemString[str(9)][5] +
                            itemString[str(9)][6],
                    inline = True)

    await ctx.send(embed=embed)



# @bot.command()
# async def getGuildId(ctx):
#     await ctx.send(ctx.message.guild.id)

# @bot.command()
# async def getEmojiDictionary1(ctx):
#     for gId in guildIds:
#         abc = await bot.fetch_guild(gId)
#         for emote in abc.emojis:
#             #bot.fetch_guild(gId).emoji[emote]
#             print(":" + str(emote.name) + ":" + str(emote.id))

bot.run(discordKey)
