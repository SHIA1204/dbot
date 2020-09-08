import os
import shutil
from os import system

import discord
import asyncio
import os.path
import linecache
import youtube_dl
import datetime

import urllib

import requests
from bs4 import BeautifulSoup

from discord.utils import get
from discord.ext import commands

client = commands.Bot(command_prefix='==')

def create_soup(url, headers):
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    return soup

@client.event
async def on_ready():
    print(f'로그인 성공: {client.user.name}!')
    game = discord.Game("==명령어")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.command(pass_context = True, aliases=['명령어'])
async def cmd(ctx):
    await ctx.channel.send(
        '```'
        '\n==지우기\n'
        '==내정보\n'
        '==실검\n'
        '==날씨 <지역>\n'
        '==T정보(==ts)\n'
        '```'
    )

@client.command(pass_context = True, aliases=['지우기'])
@commands.has_permissions(administrator=True)
async def clear(ctx, amount):
    amount = int(amount)
    if amount < 100:
        await ctx.channel.purge(limit=amount)
        await ctx.channel.send(embed=discord.Embed(title=f":warning: {amount}개의 채팅을 삭제했어요.",colour = 0x2EFEF7))
    else:
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(embed=discord.Embed(title=f":no_entry_sign: 숫자를 99 이하로 입력해 주세요.",colour = 0x2EFEF7)) 

@client.command(pass_context = True, aliases=['내정보'])
async def myprofile(ctx):
    date = datetime.datetime.utcfromtimestamp(((int(ctx.author.id) >> 22) + 1420070400000) / 1000)
    embed = discord.Embed(title = ctx.author.display_name + "님의 정보", colour = 0x2EFEF7)
    embed.add_field(name = '사용자명', value = ctx.author.name, inline = False)
    embed.add_field(name = '가입일', value = str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline = False)
    embed.add_field(name = '아이디', value = ctx.author.id, inline = False)
    embed.set_thumbnail(url = ctx.author.avatar_url)
    await ctx.channel.send(embed = embed)

@client.command(pass_context = True, aliases=['카페'])
async def cafe(ctx):
    embed = discord.Embed(title = "KCTG 공식 카페", colour = 0x2EFEF7)
    embed.add_field(name = 'https://cafe.naver.com/kctgofficial', value = "\n\u200b", inline = False)
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/740877681209507880/744451389396353106/KCTG_Wolf_1.png")
    await ctx.channel.send(embed = embed)

@client.command(pass_context = True, aliases=['실검'])
async def search_rank(ctx):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Whale/2.8.105.22 Safari/537.36'}
    url = "https://datalab.naver.com/keyword/realtimeList.naver?where=main"
    soup = create_soup(url, headers)
    rank_list = soup.find("ul", attrs={"class":"ranking_list"})
    one = rank_list.find_all("span", attrs={"class":"item_title"})[0].get_text().strip().replace("1", "") #순서대로 실검 1~10위
    two = rank_list.find_all("span", attrs={"class":"item_title"})[1].get_text().strip().replace("2", "")
    three = rank_list.find_all("span", attrs={"class":"item_title"})[2].get_text().strip().replace("3", "")
    four = rank_list.find_all("span", attrs={"class":"item_title"})[3].get_text().strip().replace("4", "")
    five = rank_list.find_all("span", attrs={"class":"item_title"})[4].get_text().strip().replace("5", "")
    six = rank_list.find_all("span", attrs={"class":"item_title"})[5].get_text().strip().replace("6", "")
    seven = rank_list.find_all("span", attrs={"class":"item_title"})[6].get_text().strip().replace("7", "")
    eight = rank_list.find_all("span", attrs={"class":"item_title"})[7].get_text().strip().replace("8", "")
    nine = rank_list.find_all("span", attrs={"class":"item_title"})[8].get_text().strip().replace("9", "")
    ten = rank_list.find_all("span", attrs={"class":"item_title"})[9].get_text().strip().replace("10", "")
    time = soup.find("span", attrs={"class":"time_txt _title_hms"}).get_text() #현재 시간
    await ctx.channel.send(f'Ⅰ ``{one}``\nⅡ ``{two}``\nⅢ ``{three}``\nⅣ ``{four}``\nⅤ ``{five}``\nⅥ ``{six}``\nⅦ ``{seven}``\nⅧ ``{eight}``\nⅨ ``{nine}``\nⅩ ``{ten}``\n\n``Time[{time}]``')

@client.command(pass_context = True, aliases=['날씨'])
async def weather(ctx, arg1):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Whale/2.8.105.22 Safari/537.36'}
    url = f"https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&query={arg1}+날씨&oquery=날씨&tqi=U1NQ%2FsprvmsssUNA1MVssssssPN-224813"
    soup = create_soup(url, headers)
    rotate = soup.find("span", attrs={"class":"btn_select"}).get_text() #지역
    cast = soup.find("p", attrs={"class":"cast_txt"}).get_text() #맑음, 흐림 같은거
    curr_temp = soup.find("p", attrs={"class":"info_temperature"}).get_text().replace("도씨", "") #현재 온도
    sen_temp = soup.find("span", attrs={"class":"sensible"}).get_text().replace("체감온도", "체감") #체감 온도
    min_temp = soup.find("span", attrs={"class":"min"}).get_text() #최저 온도
    max_temp = soup.find("span", attrs={"class":"max"}).get_text() #최고 온도
    # 오전, 오후 강수 확률
    morning_rain_rate = soup.find("span", attrs={"class":"point_time morning"}).get_text().strip() #오전
    afternoon_rain_rate = soup.find("span", attrs={"class":"point_time afternoon"}).get_text().strip() #오후

    # 미세먼지, 초미세먼지
    dust = soup.find("dl", attrs={"class":"indicator"})
    pm10 = dust.find_all("dd")[0].get_text() #미세먼지
    pm25 = dust.find_all("dd")[1].get_text() #초미세먼지

    daylist = soup.find("ul", attrs={"class":"list_area _pageList"})
    tomorrow = daylist.find_all("li")[1]
    #내일 온도
    to_min_temp = tomorrow.find_all("span")[12].get_text() #최저
    to_max_temp = tomorrow.find_all("span")[14].get_text() #최고
    #내일 강수
    to_morning_rain_rate = daylist.find_all("span", attrs={"class":"point_time morning"})[1].get_text().strip() #오전
    to_afternoon_rain_rate = daylist.find_all("span", attrs={"class":"point_time afternoon"})[1].get_text().strip() #오후

    await ctx.channel.send((rotate) + f'\n오늘의 날씨 ``' + (cast) + f'``\n__기온__ ``현재 {curr_temp}({sen_temp}) 최저 {min_temp} 최고 {max_temp}``\n__강수__ ``오전 {morning_rain_rate}`` ``오후 {afternoon_rain_rate}``\n__대기__ ``미세먼지 {pm10}`` ``초미세먼지 {pm25})``\n\n내일의 날씨\n__기온__ ``최저 {to_min_temp}˚`` ``최고 {to_max_temp}˚``\n__강수__ ``오전 {to_morning_rain_rate}`` ``오후 {to_afternoon_rain_rate}``')

@client.command(pass_context = True, aliases=['T정보', 'TS', 't정보', 'ts'])
async def tmp_server_status(ctx):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Whale/2.8.105.22 Safari/537.36'}
    url = "https://truckersmp.com/status"
    soup = create_soup(url, headers)
    #현재 접속중인 플레이어
    curr_status = soup.find("div", attrs={"class":"row margin-bottom-40 margin-top-20"})
    sim1 = curr_status.find_all("h4")[0].get_text().strip().replace("No players in queue", "")
    sim2 = curr_status.find_all("h4")[1].get_text().strip().replace("No players in queue", "")
    sim_us = curr_status.find_all("h4")[2].get_text().strip().replace("No players in queue", "")
    sim_sgp = curr_status.find_all("h4")[3].get_text().strip().replace("No players in queue", "")
    arc = curr_status.find_all("h4")[4].get_text().strip().replace("No players in queue", "")
    pro = curr_status.find_all("h4")[5].get_text().strip().replace("No players in queue", "")
    pro_arc = curr_status.find_all("h4")[6].get_text().strip().replace("No players in queue", "")

    embed = discord.Embed(title = "[ETS2] TruckersMP 접속자 현황", colour = 0x2EFEF7)
    embed.add_field(name = 'Simulation 1', value = f"{sim1}", inline = False)
    embed.add_field(name = 'Simulation 2', value = f"{sim2}", inline = False)
    embed.add_field(name = '[US] Simulation`', value = f"{sim_us}", inline = False)
    embed.add_field(name = '[SGP] Simulation', value = f"{sim_sgp}", inline = False)
    embed.add_field(name = 'Arcade', value = f"{arc}", inline = False)
    embed.add_field(name = 'ProMods', value = f"{pro}", inline = False)
    embed.add_field(name = 'ProMods Arcade', value = f"{pro_arc}", inline = False)
    await ctx.channel.send(embed = embed)

@client.command(pass_context = True, aliases=['T트래픽순위', 'TTR', 't트래픽순위', 'ttr'])
async def tmp_traffic(ctx):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Whale/2.8.105.22 Safari/537.36'}
    url = "https://traffic.krashnz.com/"
    soup = create_soup(url, headers)
    #실시간 트래픽 순위
    traffic_top = soup.find("ul", attrs={"class":"list-group mb-3"})
    rank1 = traffic_top.find_all("div")[1].get_text().strip()
    rank2 = traffic_top.find_all("div")[2].get_text().strip()
    rank3 = traffic_top.find_all("div")[3].get_text().strip()
    rank4 = traffic_top.find_all("div")[4].get_text().strip()
    rank5 = traffic_top.find_all("div")[5].get_text().strip()
    g_set = soup.find("div", attrs={"class":"row text-center mb-2"})
    g_player = g_set.find_all("span", attrs={"class":"stats-number"})[0].get_text().strip()
    g_time = g_set.find_all("span", attrs={"class":"stats-number"})[1].get_text().strip()

    embed = discord.Embed(title = "[ETS2] TruckersMP 실시간 트래픽 TOP5", colour = 0x2EFEF7)
    embed.add_field(name = f'{rank1}', value = "\n\u200b", inline = False)
    embed.add_field(name = f'{rank2}', value = "\n\u200b", inline = False)
    embed.add_field(name = f'{rank3}', value = "\n\u200b", inline = False)
    embed.add_field(name = f'{rank4}', value = "\n\u200b", inline = False)
    embed.add_field(name = f'{rank5}', value = f"\n{g_player} players tracked / {g_time} in-game time", inline = False)
    await ctx.channel.send(embed = embed)

@client.command(pass_context = True, aliases=['j', '들어와'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"채널 연결\n")

    await ctx.channel.send(embed=discord.Embed(title=":inbox_tray: 음성 채널에 들어갑니다.",colour = 0x2EFEF7))


@client.command(pass_context = True, aliases=['l', '나가'])
async def leave(ctx):
	voice_client = ctx.guild.voice_client

	if voice_client == None: #봇이 음성채널에 접속해있지 않았을 때
		await ctx.channel.send(embed=discord.Embed(title=":no_entry_sign: 봇이 음성 채널에 없어요.",colour = 0x2EFEF7))
		return
		
	await ctx.channel.send(embed=discord.Embed(title=":mute: 채널에서 나갑니다.",colour = 0x2EFEF7)) #봇이 음성채널에 접속해있을 때
	await ctx.voice_client.disconnect()

@client.command(pass_context=True, aliases=['p', '재생'])
async def play(ctx, url: str):

    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"채널 연결\n")

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") + "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.1

            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")



    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(embed=discord.Embed(title=":dvd: 음악이 재생 중이에요.", description="==queue <url>", colour = 0x2EFEF7))
        return


    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_folder = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.channel.purge(limit=1)
    await ctx.channel.send(embed=discord.Embed(title=":dvd: 음악 재생을 준비하는 중이에요.",colour = 0x2EFEF7))

    voice = get(client.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("Downloading audio now\n")
            ydl.download([url])
    except:
        print("FALLBACK: youtube-dl does not support this URL, using Spotify (This is normal if spotify URL)")
        c_path = os.path.dirname(os.path.realpath(__file__))
        system("spotdl -f " + '"' + c_path + '"' + " -s " + url)  # make sure there are spaces in the -s

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.1

    nname = name.rsplit("-", 2)
    await ctx.channel.send(embed=discord.Embed(title=":dvd: 음악을 재생합니다.", description=f"{nname[0]}", colour = 0x2EFEF7))
    print("playing\n")

@client.command(pass_context=True, aliases=['pa', '일시정지'])
async def pause(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
    else:
        print("Music not playing failed pause")
        await ctx.send("Music not playing failed pause")


@client.command(pass_context=True, aliases=['r', '다시재생'])
async def resume(ctx):

    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.channel.send(embed=discord.Embed(title=":dvd: 음악을 다시 재생합니다.", colour = 0x2EFEF7))
    else:
        print("Music is not paused")
        await ctx.channel.send(embed=discord.Embed(title=":no_entry_sign: 일시 정지된 음악이 없어요.",colour = 0x2EFEF7))


@client.command(pass_context=True, aliases=['st', '중지'])
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    queues.clear()

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("Music stopped")
    else:
        print("No music playing failed to stop")
        await ctx.send("No music playing failed to stop")


queues = {}

@client.command(pass_context=True, aliases=['q', '예약'])
async def queue(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])
    await ctx.channel.purge(limit=1)
    await ctx.channel.send(embed=discord.Embed(title=":cd: 대기열에 음악을 " + str(q_num) + "개 추가했어요.", colour = 0x2EFEF7))

    print("Song added to queue\n")

@client.command(pass_context=True, aliases=['s', '스킵'])
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing Next Song")
        voice.stop()
        await ctx.channel.send(embed=discord.Embed(title=":dvd: 다음 음악을 재생합니다.", colour = 0x2EFEF7))
    else:
        print("No music playing")
        await ctx.send("No music playing failed")


client.run(token)
