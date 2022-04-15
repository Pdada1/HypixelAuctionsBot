import aiohttp
import discord
from discord.ext import commands
from datetime import datetime
from prettytable import PrettyTable
import asyncio
import operator
import bisect
from bisect import bisect_left
import time
from tabulate import tabulate

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

@client.command()
async def flip(ctx, look):
    session=aiohttp.ClientSession()
    j = 0
    await ctx.send("This may take up to a minute.")
    binitems, nbinitems = await find(look, session)
    await ctx.send('Auction Prices')
    while j != 5:
        print(j)
        try:
            await convert_to_username(nbinitems[j][1], session)
        except IndexError:
            print("no auctions")
        try:
            await convert_to_username(binitems[j][1],session)
        except IndexError:
            print("no BIN auctions")
        j += 1
    t = PrettyTable(["Item Name", "Name", "Price", "Time Left", "Item Tier"])
    try:
        t.add_row([nbinitems[0][0], nbinitems[0][1], str(nbinitems[0][2]), nbinitems[0][3], nbinitems[0][4]])
    except IndexError:
        print()
    try:
        t.add_row([nbinitems[1][0], nbinitems[1][1], str(nbinitems[1][2]), nbinitems[1][3], nbinitems[1][4]])
    except IndexError:
        print()
    try:
        t.add_row([nbinitems[2][0], nbinitems[2][1], str(nbinitems[2][2]), nbinitems[2][3], nbinitems[2][4]])
    except IndexError:
        print()
    try:
        t.add_row([nbinitems[3][0], nbinitems[3][1], str(nbinitems[3][2]), nbinitems[3][3], nbinitems[3][4]])
    except IndexError:
        print()
    try:
        t.add_row([nbinitems[4][0], nbinitems[4][1], str(nbinitems[4][2]), nbinitems[4][3], nbinitems[4][4]])
    except IndexError:
        print()
    await ctx.send(t)
    await ctx.send("-")
    await ctx.send("Bin Prices")
    v = PrettyTable(["Item Name", "Name", "Price", "Time Left", "Item Tier"])
    try:
        v.add_row([binitems[0][0], binitems[0][1], str(binitems[0][2]), binitems[0][3], binitems[0][4]])
    except IndexError:
        print()
    try:
        v.add_row([binitems[1][0], binitems[1][1], str(binitems[1][2]), binitems[1][3], binitems[1][4]])
    except IndexError:
        print()
    try:
        v.add_row([binitems[2][0], binitems[2][1], str(binitems[2][2]), binitems[2][3], binitems[2][4]])
    except IndexError:
        print()
    try:
        v.add_row([binitems[3][0], binitems[3][1], str(binitems[3][2]), binitems[3][3], binitems[3][4]])
    except IndexError:
        print()
    try:
        v.add_row([binitems[4][0], binitems[4][1], str(binitems[4][2]), binitems[4][3], binitems[4][4]])
    except IndexError:
        print()
    await ctx.send(v)
    await session.close()


async def find(look, session):
    look = look.replace('+', '✪')
    async with session.get("https://api.hypixel.net/skyblock/auctions?page=0") as js:
        data = await js.json(content_type=None)
        testing = data["totalPages"]
    i = 0
    binitems = []
    nbinitems = []
    while i != testing:
        async with session.get("https://api.hypixel.net/skyblock/auctions?page=" + str(i)) as js:
            try:
                response_dict = await js.json()
            except ContentTypeError:
                async with session.get("https://api.hypixel.net/skyblock/auctions?page=" + str(i)) as js:
                    response_dict = await js.json()
        auctionsss = response_dict["auctions"]
        i += 1
        for auction in auctionsss:
            try:
                if auction["bin"] and str(auction["item_name"]).upper() == str(look).upper():
                    binitems.append([auction["item_name"], auction["auctioneer"], auction["starting_bid"], datetime.fromtimestamp(auction["end"] / 1000).strftime('%H:%M:%S'), auction["tier"]])
            except KeyError:
                if str(auction["item_name"]).upper() == str(look).upper():
                    nbinitems.append([auction["item_name"], auction["auctioneer"], auction["highest_bid_amount"], datetime.fromtimestamp(auction["end"] / 1000).strftime('%H:%M:%S'), auction["tier"]])
    binitems.sort(key=lambda x: x[2])
    nbinitems.sort(key=lambda x: x[2])
    return binitems, nbinitems

@client.command()
async def bestflip(ctx):
    start_time = time.time()
    session = aiohttp.ClientSession()
    best = [0]*10
    itemnames = []
    binitems=[]
    nbinitems=[]
    auctions = []
    anums = []
    final=[]
    async with session.get("https://api.hypixel.net/skyblock/auctions?page=" + str(0)) as js:
        response_dict = await js.json()
    pages = response_dict["totalPages"]
    print("pages counted")
    auctions, itemnames= map(list, zip(*await asyncio.gather(*[gatherpageitems(session, x)for x in range(0, pages)])))
    print('auctions gathered')
    itemnames=flatten(itemnames)
    itemnames = list(dict.fromkeys(itemnames))
    for auction in auctions:
        for x in range(0, len(auction)):
                if auction[x]["bin"]is True:
                    binitems.append([auction[x]["item_name"], auction[x]["auctioneer"], auction[x]["starting_bid"],
                                 datetime.fromtimestamp(auction[x]["end"] / 1000).strftime('%H:%M:%S'), auction[x]["tier"]])
                else:
                    print("enters")
                    nbinitems.append([auction[x]["item_name"], auction[x]["auctioneer"], auction[x]["highest_bid_amount"],
                                datetime.fromtimestamp(auction[x]["end"] / 1000).strftime('%H:%M:%S'), auction[x]["tier"]])
    nbinitems.sort(key=operator.itemgetter(0, 2))
    binitems.sort(key=operator.itemgetter(0, 2))
    print("auctions sorted")
    print(nbinitems)
    binitems = removedupes(binitems)
    nbinitems = removedupes(nbinitems)
    print("starting the search")
    for x in range(0,len(nbinitems)):
        nnum=binary_search(nbinitems, itemnames[x])
        if nnum!=-1:
            bnum=binary_search(binitems, itemnames[x])
            if bnum!=-1:
                num=[]
                num+=bnum, nnum
                anums.append(num)
    for x in range(0, len(anums)):
        n=[]
        n=abs(binitems[anums[x][0]][2]-nbinitems[anums[x][1]][2]),binitems[anums[x][0]], nbinitems[anums[x][1]]
        final.append(n)
    w=await bestflipcomplete(final,session)
    print("My program took", time.time() - start_time, "to run")
    await ctx.send(w)
    await session.close()
    await ctx.send("done")

async def bestflipcomplete(final,session):
    final.sort(key=operator.itemgetter(0, 0), reverse=True)
    headings=["Profit",["Item 1 Name", "Name", "Price", "Time Left", "Item Tier"],["Item2 Name", "Name", "Price", "Time Left", "Item Tier"]]
    final=final[:5]
    for x in range(0,len(final)):
        final[x][1][1]=await convert_to_username(final[x][1][1],session)
        final[x][2][1]=await convert_to_username(final[x][2][1],session)
    return tabulate(final,headings)


def flatten(t):
    return [item for sublist in t for item in sublist]


def binary_search(arr, x):
    l = 0
    r = len(arr) - 1
    while (l <= r):
        m = (l + r) // 2
        if (arr[m][0] == x):
            return m
        elif (arr[m][0] < x):
            l = m + 1
        else:
            r = m - 1
    return -1  # If element is not found  then it will return -1


def removedupes(list):
    first=list[0][0]
    newlist=[]
    newlist.append(list[0])
    for x in range(1,len(list)):
        if first!=list[x][0]:
            first=list[x][0]
            newlist.append(list[x])
    return newlist

async def gatherpageitems(session, x):
    itemnames=[]
    async with session.get("https://api.hypixel.net/skyblock/auctions?page=" + str(x)) as js:
        s = await js.json()
        s2 = s["auctions"]
        n = len(s["auctions"])
        for y in range(0, n):
            itemnames.append(s2[y]["item_name"])
        itemnames = list(dict.fromkeys(itemnames))
        print(len(itemnames))
        return s2, itemnames

async def convert_to_username(uuid, session):
    print(uuid)
    async with session.get('https://sessionserver.mojang.com/session/minecraft/profile/' + str(uuid)) as js:
        response = await js.json()
        print(response["name"])
        return(response["name"])

async def liquidity():
    session = aiohttp.ClientSession()
    while True:
        async with session.get("https://api.hypixel.net/skyblock/auctions_ended") as js:



@client.event
async def on_ready():
    print('Bot is Ready')


@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}')


client.run('ODMzNDg1MjY4ODA2Nzk1MzI2.YHzBpQ.S7FWfxstByeZPgvM1YR7Et0y_d8')


