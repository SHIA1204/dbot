import os
import shutil
from os import system

import discord
import asyncio
import os.path
import linecache
import datetime

import urllib

import requests
from bs4 import BeautifulSoup

from discord.utils import get
from discord.ext import commands


from discord.ext.commands import CommandNotFound
import logging
import itertools
import sys
import traceback
import random
import itertools
import math
from async_timeout import timeout
from functools import partial
import functools
from youtube_dl import YoutubeDL
import youtube_dl
from io import StringIO
import time
import urllib.request
from gtts import gTTS

##################### 로깅 ###########################
log_stream = StringIO()    
logging.basicConfig(stream=log_stream, level=logging.WARNING)

#ilsanglog = logging.getLogger('discord')
#ilsanglog.setLevel(level = logging.WARNING)
#handler = logging.StreamHandler()
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#ilsanglog.addHandler(handler)
#####################################################

def init():
	global command

	command = []
	fc = []

	command_inidata = open('command.ini', 'r', encoding = 'utf-8')
	command_inputData = command_inidata.readlines()

	############## 뮤직봇 명령어 리스트 #####################
	for i in range(len(command_inputData)):
		tmp_command = command_inputData[i][12:].rstrip('\n')
		fc = tmp_command.split(', ')
		command.append(fc)
		fc = []

	del command[0]

	command_inidata.close()

	#print (command)

init()

#mp3 파일 생성함수(gTTS 이용, 남성목소리)
async def MakeSound(saveSTR, filename):
	
	tts = gTTS(saveSTR, lang = 'ko')
	tts.save('./' + filename + '.wav')
	'''
	try:
		encText = urllib.parse.quote(saveSTR)
		urllib.request.urlretrieve("https://clova.ai/proxy/voice/api/tts?text=" + encText + "%0A&voicefont=1&format=wav",filename + '.wav')
	except Exception as e:
		print (e)
		tts = gTTS(saveSTR, lang = 'ko')
		tts.save('./' + filename + '.wav')
		pass
	'''
#mp3 파일 재생함수	
async def PlaySound(voiceclient, filename):
	source = discord.FFmpegPCMAudio(filename)
	try:
		voiceclient.play(source)
	except discord.errors.ClientException:
		while voiceclient.is_playing():
			await asyncio.sleep(1)
	while voiceclient.is_playing():
		await asyncio.sleep(1)
	voiceclient.stop()
	source.cleanup()

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''


class VoiceError(Exception):
	pass


class YTDLError(Exception):
	pass


class YTDLSource(discord.PCMVolumeTransformer):
	YTDL_OPTIONS = {
		'format': 'bestaudio/best',
		'extractaudio': True,
		'audioformat': 'mp3',
		'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
		'restrictfilenames': True,
		'noplaylist': False,
		'nocheckcertificate': True,
		'ignoreerrors': False,
		'logtostderr': False,
		'quiet': True,
		'no_warnings': True,
		'default_search': 'auto',
		'source_address': '0.0.0.0',
		'force-ipv4' : True,
    		'-4': True
	}

	FFMPEG_OPTIONS = {
		'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
		'options': '-vn',
	}

	ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)

	def __init__(self, ctx: commands.Context, source: discord.FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
		super().__init__(source, volume)
		self.requester = ctx.author
		self.channel = ctx.channel
		self.data = data

		self.uploader = data.get('uploader')
		self.uploader_url = data.get('uploader_url')
		date = data.get('upload_date')
		self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
		self.title = data.get('title')
		self.thumbnail = data.get('thumbnail')
		self.description = data.get('description')
		self.duration = self.parse_duration(int(data.get('duration')))
		self.tags = data.get('tags')
		self.url = data.get('webpage_url')
		self.views = data.get('view_count')
		self.likes = data.get('like_count')
		self.dislikes = data.get('dislike_count')
		self.stream_url = data.get('url')

	def __str__(self):
		return '**{0.title}** by **{0.uploader}**'.format(self)

	@classmethod
	async def create_source(cls, bot, ctx: commands.Context, search: str, *, loop: asyncio.BaseEventLoop = None):
		loop = loop or asyncio.get_event_loop()

		if "http" not in search:
			partial = functools.partial(cls.ytdl.extract_info, f"ytsearch5:{search}", download=False, process=False)

			data = await loop.run_in_executor(None, partial)

			if data is None:
				raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

			emoji_list : list = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "🚫"]
			song_list_str : str = ""
			cnt : int = 0
			song_index : int = 0

			for data_info in data["entries"]:
				cnt += 1
				if 'title' not in data_info:
					data_info['title'] = f"{search} - 제목 정보 없음"
				song_list_str += f"`{cnt}.` [**{data_info['title']}**](https://www.youtube.com/watch?v={data_info['url']})\n"

			embed = discord.Embed(description= song_list_str)
			embed.set_footer(text=f"10초 안에 미선택시 취소됩니다.")

			song_list_message = await ctx.send(embed = embed)

			for emoji in emoji_list:
				await song_list_message.add_reaction(emoji)

			def reaction_check(reaction, user):
				return (reaction.message.id == song_list_message.id) and (user.id == ctx.author.id) and (str(reaction) in emoji_list)
			try:
				reaction, user = await bot.wait_for('reaction_add', check = reaction_check, timeout = 10)
			except asyncio.TimeoutError:
				reaction = "🚫"

			for emoji in emoji_list:
				await song_list_message.remove_reaction(emoji, bot.user)

			await song_list_message.delete(delay = 10)
			
			if str(reaction) == "1️⃣":
				song_index = 0
			elif str(reaction) == "2️⃣":
				song_index = 1
			elif str(reaction) == "3️⃣":
				song_index = 2
			elif str(reaction) == "4️⃣":
				song_index = 3
			elif str(reaction) == "5️⃣":
				song_index = 4
			else:
				return False
			
			result_url = f"https://www.youtube.com/watch?v={data['entries'][song_index]['url']}"
		else:
			result_url = search

		webpage_url = result_url
		partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
		processed_info = await loop.run_in_executor(None, partial)
		if processed_info is None:
			raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))
		
		if 'entries' not in processed_info:
			info = processed_info
		else:
			info = None
			while info is None:
				try:
					info = processed_info['entries'].pop(0)
				except IndexError:
					raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

		return cls(ctx, discord.FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

	@staticmethod
	def parse_duration(duration: int):
		return time.strftime('%H:%M:%S', time.gmtime(duration))


class Song:
	__slots__ = ('source', 'requester')

	def __init__(self, source: YTDLSource):
		self.source = source
		self.requester = source.requester

	def create_embed(self):
		embed = (discord.Embed(title='Now playing',
							description='**```fix\n{0.source.title}\n```**'.format(self),
							color=discord.Color.blurple())
				.add_field(name='Duration', value=self.source.duration)
				.add_field(name='Requested by', value=self.requester.mention)
				.add_field(name='Uploader', value='[{0.source.uploader}]({0.source.uploader_url})'.format(self))
				.add_field(name='URL', value='[Click]({0.source.url})'.format(self))
				.set_thumbnail(url=self.source.thumbnail))

		return embed


class SongQueue(asyncio.Queue):
	def __getitem__(self, item):
		if isinstance(item, slice):
			return list(itertools.islice(self._queue, item.start, item.stop, item.step))
		else:
			return self._queue[item]

	def __iter__(self):
		return self._queue.__iter__()

	def __len__(self):
		return self.qsize()

	def clear(self):
		self._queue.clear()

	def shuffle(self):
		random.shuffle(self._queue)

	def select(self, index : int, loop : bool = False):
		for i in range(index-1):
			if not loop:
				del self._queue[0]
			else:
				self._queue.append(self._queue[0])
				del self._queue[0]

	def remove(self, index: int):
		del self._queue[index]


class VoiceState:
	def __init__(self, bot: commands.Bot, ctx: commands.Context):
		self.bot = bot
		self._ctx = ctx
		self._cog = ctx.cog

		self.current = None
		self.voice = None
		self.next = asyncio.Event()
		self.songs = SongQueue()

		self._loop = False
		self._volume = 0.5
		self.skip_votes = set()

		self.audio_player = bot.loop.create_task(self.audio_player_task())

	def __del__(self):
		self.audio_player.cancel()

	@property
	def loop(self):
		return self._loop

	@loop.setter
	def loop(self, value: bool):
		self._loop = value

	@property
	def volume(self):
		return self._volume

	@volume.setter
	def volume(self, value: float):
		self._volume = value

	@property
	def is_playing(self):
		return self.voice and self.current

	async def audio_player_task(self):
		while True:
			self.next.clear()

			if self.loop and self.current is not None:
				source1 = await YTDLSource.create_source(self.bot, self._ctx, self.current.source.url, loop=self.bot.loop)
				song1 = Song(source1)
				await self.songs.put(song1)
			else:
				pass

			try:
				async with timeout(180):  # 3 minutes
					self.current = await self.songs.get()
			except asyncio.TimeoutError:
				self.bot.loop.create_task(self.stop())
				return

			self.current.source.volume = self._volume
			self.voice.play(self.current.source, after=self.play_next_song)
			play_info_msg = await self.current.source.channel.send(embed=self.current.create_embed())
#			await play_info_msg.delete(delay = 20)

			await self.next.wait()

	def play_next_song(self, error=None):
		if error:
			raise VoiceError(str(error))

		self.next.set()

	def skip(self):
		self.skip_votes.clear()

		if self.is_playing:
			self.voice.stop()

	async def stop(self):
		self.songs.clear()

		if self.voice:
			await self.voice.disconnect()
			self.voice = None

		self.bot.loop.create_task(self._cog.cleanup(self._ctx))

class Music(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.voice_states = {}

	def get_voice_state(self, ctx: commands.Context):
		state = self.voice_states.get(ctx.guild.id)
		if not state:
			state = VoiceState(self.bot, ctx)
			self.voice_states[ctx.guild.id] = state

		return state

	def cog_unload(self):
		for state in self.voice_states.values():
			self.bot.loop.create_task(state.stop())

	def cog_check(self, ctx: commands.Context):
		if not ctx.guild:
			raise commands.NoPrivateMessage('This command can\'t be used in DM channels.')

		return True

	async def cog_before_invoke(self, ctx: commands.Context):
		ctx.voice_state = self.get_voice_state(ctx)

	async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
		await ctx.send('에러 : {}'.format(str(error)))
	'''
	@commands.command(name='join', invoke_without_subcommand=True)
	async def _join(self, ctx: commands.Context):
		destination = ctx.author.voice.channel
		if ctx.voice_state.voice:
			await ctx.voice_state.voice.move_to(destination)
			return
		ctx.voice_state.voice = await destination.connect()
	'''
	async def cleanup(self, ctx: commands.Context):
		del self.voice_states[ctx.guild.id]

	@commands.command(name=command[0][0], aliases=command[0][1:]) #음성 채널 입장
	#@commands.has_permissions(manage_guild=True)
	async def _summon(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
		channel = ctx.message.author.voice.channel
		if not channel and not ctx.author.voice:
			raise VoiceError(':no_entry_sign: 현재 접속중인 음악채널이 없습니다.')

		destination = channel or ctx.author.voice.channel
		if ctx.voice_state.voice:
			await ctx.voice_state.voice.move_to(destination)
			return

		ctx.voice_state.voice = await destination.connect()

	@commands.command(name=command[1][0], aliases=command[1][1:]) #음성 채널 퇴장
	#@commands.has_permissions(manage_guild=True)
	async def _leave(self, ctx: commands.Context):
		if not ctx.voice_state.voice:
			return await ctx.send(embed=discord.Embed(title=":no_entry_sign: 현재 접속중인 음악채널이 없습니다.",colour = 0x2EFEF7))

		await ctx.voice_state.stop()
		del self.voice_states[ctx.guild.id]

	@commands.command(name=command[8][0], aliases=command[8][1:]) #볼륨 조절
	async def _volume(self, ctx: commands.Context, *, volume: int):
		vc = ctx.voice_client

		if not ctx.voice_state.is_playing:
			return await ctx.send(embed=discord.Embed(title=":mute: 현재 재생중인 음악이 없습니다.",colour = 0x2EFEF7))

		if not 0 < volume < 101:
			return await ctx.send(embed=discord.Embed(title=":no_entry_sign: 볼륨은 1 ~ 100 사이로 입력 해주세요.",colour = 0x2EFEF7))

		if vc.source:
			vc.source.volume = volume / 100

		ctx.voice_state.volume = volume / 100
		await ctx.send(embed=discord.Embed(title=f":loud_sound: 볼륨을 {volume}%로 조정하였습니다.",colour = 0x2EFEF7))

	@commands.command(name=command[7][0], aliases=command[7][1:]) #현재 재생 중인 목록
	async def _now(self, ctx: commands.Context):
		await ctx.send(embed=ctx.voice_state.current.create_embed())

	@commands.command(name=command[3][0], aliases=command[3][1:]) #음악 일시 정지
	#@commands.has_permissions(manage_guild=True)
	async def _pause(self, ctx: commands.Context):
		if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
			ctx.voice_state.voice.pause()
			await ctx.message.add_reaction('⏸')

	@commands.command(name=command[4][0], aliases=command[4][1:]) #음악 다시 재생
	#@commands.has_permissions(manage_guild=True)
	async def _resume(self, ctx: commands.Context):
		if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
			ctx.voice_state.voice.resume()
			await ctx.message.add_reaction('⏯')

	@commands.command(name=command[9][0], aliases=command[9][1:]) #음악 정지
	#@commands.has_permissions(manage_guild=True)
	async def _stop(self, ctx: commands.Context):
		ctx.voice_state.songs.clear()

		if ctx.voice_state.is_playing:
			ctx.voice_state.voice.stop()
			await ctx.message.add_reaction('⏹')

	@commands.command(name=command[5][0], aliases=command[5][1:]) #현재 음악 스킵
	async def _skip(self, ctx: commands.Context, *, args: int = 1):
		if not ctx.voice_state.is_playing:
			return await ctx.send(embed=discord.Embed(title=':mute: 현재 재생중인 음악이 없습니다.',colour = 0x2EFEF7))

		await ctx.message.add_reaction('⏭')

		if args != 1:
			ctx.voice_state.songs.select(args, ctx.voice_state.loop)

		ctx.voice_state.skip()
		'''	
		voter = ctx.message.author
		if voter == ctx.voice_state.current.requester:
			await ctx.message.add_reaction('⏭')
			ctx.voice_state.skip()
		elif voter.id not in ctx.voice_state.skip_votes:
			ctx.voice_state.skip_votes.add(voter.id)
			total_votes = len(ctx.voice_state.skip_votes)
			if total_votes >= 3:
				await ctx.message.add_reaction('⏭')
				ctx.voice_state.skip()
			else:
				await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))
		else:
			await ctx.send('```이미 투표하셨습니다.```')
		'''
	@commands.command(name=command[6][0], aliases=command[6][1:]) #재생 목록
	async def _queue(self, ctx: commands.Context, *, page: int = 1):

		if len(ctx.voice_state.songs) == 0:
			return await ctx.send(embed=discord.Embed(title=':mute: 재생목록이 없습니다.',colour = 0x2EFEF7))
		
		items_per_page = 10
		pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

		start = (page - 1) * items_per_page
		end = start + items_per_page

		queue = ''
		for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
			queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

		if ctx.voice_state.loop:
			embed = discord.Embed(title = '🔁  Now playing', description='**```fix\n{0.source.title}\n```**'.format(ctx.voice_state.current))
		else:
			embed = discord.Embed(title = 'Now playing', description='**```fix\n{0.source.title}\n```**'.format(ctx.voice_state.current))
		embed.add_field(name ='\u200B\n**{} tracks:**\n'.format(len(ctx.voice_state.songs)), value = f"\u200B\n{queue}")
		embed.set_thumbnail(url=ctx.voice_state.current.source.thumbnail)
		embed.set_footer(text='Viewing page {}/{}'.format(page, pages))
		await ctx.send(embed=embed)

	@commands.command(name=command[11][0], aliases=command[11][1:]) #음악 셔플
	async def _shuffle(self, ctx: commands.Context):
		if len(ctx.voice_state.songs) == 0:
			return await ctx.send(embed=discord.Embed(title=':mute: 재생목록이 없습니다.',colour = 0x2EFEF7))

		ctx.voice_state.songs.shuffle()
		result = await ctx.send(embed=discord.Embed(title=':twisted_rightwards_arrows: 셔플 완료!',colour = 0x2EFEF7))
		await result.add_reaction('🔀')

	@commands.command(name=command[10][0], aliases=command[10][1:]) #음악 삭제
	async def _remove(self, ctx: commands.Context, index: int):
		if len(ctx.voice_state.songs) == 0:
			return ctx.send(embed=discord.Embed(title=':mute: 재생목록이 없습니다.',colour = 0x2EFEF7))
		
#		remove_result = '`{0}.` [**{1.source.title}**] 삭제 완료!\n'.format(index, ctx.voice_state.songs[index - 1])
		result = await ctx.send(embed=discord.Embed(title='`{0}.` [**{1.source.title}**] 삭제 완료!\n'.format(index, ctx.voice_state.songs[index - 1]),colour = 0x2EFEF7))
		ctx.voice_state.songs.remove(index - 1)
		await result.add_reaction('✅')


	@commands.command(name=command[14][0], aliases=command[14][1:]) #음악 반복
	async def _loop(self, ctx: commands.Context):
		if not ctx.voice_state.is_playing:
			return await ctx.send(embed=discord.Embed(title=':mute: 현재 재생중인 음악이 없습니다.',colour = 0x2EFEF7))

		# Inverse boolean value to loop and unloop.
		ctx.voice_state.loop = not ctx.voice_state.loop
		if ctx.voice_state.loop :
			result = await ctx.send(embed=discord.Embed(title=':repeat: 반복재생이 설정되었습니다!',colour = 0x2EFEF7))
		else:
			result = await ctx.send(embed=discord.Embed(title=':repeat_one: 반복재생이 취소되었습니다!',colour = 0x2EFEF7))
		await result.add_reaction('🔁')

	@commands.command(name=command[2][0], aliases=command[2][1:]) #음악 재생
	async def _play(self, ctx: commands.Context, *, search: str):
		if not ctx.voice_state.voice:
			await ctx.invoke(self._summon)

		async with ctx.typing():
			try:
				source = await YTDLSource.create_source(self.bot, ctx, search, loop=self.bot.loop)
				if not source:
					return await ctx.send(f"노래 재생/예약이 취소 되었습니다.")
			except YTDLError as e:
				await ctx.send('에러가 발생했습니다 : {}'.format(str(e)))
			else:
				song = Song(source)

				await ctx.channel.purge(limit=1)
				await ctx.voice_state.songs.put(song)
				await ctx.send(embed=discord.Embed(title=f':musical_note: 재생목록 추가 : {str(source)}',colour = 0x2EFEF7))

#	@commands.command(name=command[13][0], aliases=command[13][1:]) #지우기
#	async def clear_channel_(self, ctx: commands.Context, *, msg: int = 1):
#		try:
#			msg = int(msg)
#		except:
#			await ctx.send(f"```지우고 싶은 줄수는 [숫자]로 입력해주세요!```")
#		await ctx.channel.purge(limit = msg)

	@_summon.before_invoke
	@_play.before_invoke
	async def ensure_voice_state(self, ctx: commands.Context):
		if not ctx.author.voice or not ctx.author.voice.channel:
			raise commands.CommandError('음성채널에 접속 후 사용해주십시오.')

		if ctx.voice_client:
			if ctx.voice_client.channel != ctx.author.voice.channel:
				raise commands.CommandError('봇이 이미 음성채널에 접속해 있습니다.')

#	@commands.command(name=command[12][0], aliases=command[12][1:])   #도움말
#	async def menu_(self, ctx):
#		command_list = ''
#		command_list += '!인중 : 봇상태가 안좋을 때 쓰세요!'     #!
#		command_list += ','.join(command[0]) + '\n'     #!들어가자
#		command_list += ','.join(command[1]) + '\n'     #!나가자
#		command_list += ','.join(command[2]) + ' [검색어] or [url]\n'     #!재생
#		command_list += ','.join(command[3]) + '\n'     #!일시정지
#		command_list += ','.join(command[4]) + '\n'     #!다시재생
#		command_list += ','.join(command[5]) + ' (숫자)\n'     #!스킵
#		command_list += ','.join(command[6]) + ' 혹은 [명령어] + [숫자]\n'     #!목록
#		command_list += ','.join(command[7]) + '\n'     #!현재재생
#		command_list += ','.join(command[8]) + ' [숫자 1~100]\n'     #!볼륨
#		command_list += ','.join(command[9]) + '\n'     #!정지
#		command_list += ','.join(command[10]) + '\n'     #!삭제
#		command_list += ','.join(command[11]) + '\n'     #!섞기
#		command_list += ','.join(command[14]) + '\n'     #!
#		command_list += ','.join(command[13]) + ' [숫자]\n'     #!경주
#		embed = discord.Embed(
#				title = "----- 명령어 -----",
#				description= '```' + command_list + '```',
#				color=0xff00ff
#				)
#		await ctx.send( embed=embed, tts=False)

	################ 음성파일 생성 후 재생 ################ 			
	@commands.command(name="==인중")
	async def playText_(self, ctx):
		#msg = ctx.message.content[len(ctx.invoked_with)+1:]
		#sayMessage = msg
		await MakeSound('뮤직봇이 많이 아파요. 잠시 후 사용해주세요.', './say' + str(ctx.guild.id))
		await ctx.send("```뮤직봇이 많이 아파요. 잠시 후 사용해주세요.```", tts=False)
		
		if not ctx.voice_state.voice:
			await ctx.invoke(self._summon)
			
		if ctx.voice_state.is_playing:
			ctx.voice_state.voice.stop()
		
		await PlaySound(ctx.voice_state.voice, './say' + str(ctx.guild.id) + '.wav')


		await ctx.voice_state.stop()
		del self.voice_states[ctx.guild.id]



#client = commands.Bot(command_prefix='==', help_command = None)
client = commands.Bot('', help_command = None)
client.add_cog(Music(client))

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

@client.event 
async def on_command_error(ctx, error):
	if isinstance(error, CommandNotFound):
		return
	elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
		return
	raise error

@client.command(pass_context = True, aliases=['==명령어'])
async def cmd(ctx):
    embed = discord.Embed(title = "캬루봇 명령어 목록", colour = 0x2EFEF7)
    embed.add_field(name = '==지우기 <숫자>', value = '최근 1~99개의 메세지를 삭제합니다.', inline = False)
    embed.add_field(name = '==내정보', value = '자신의 디스코드 정보를 보여줍니다.', inline = False)
    embed.add_field(name = '==실검', value = '네이버의 급상승 검색어 TOP10을 보여줍니다.', inline = False)
    embed.add_field(name = '==날씨 <지역>', value = '<지역>의 날씨를 알려줍니다.', inline = False)
    embed.add_field(name = '==말해 <내용>', value = '<내용>을 말합니다.', inline = False)
    embed.add_field(name = '==T정보, ==ts', value = 'TruckersMP의 접속자 정보를 보여줍니다.', inline = False)
    embed.add_field(name = '==T트래픽순위, ==ttr', value = 'TruckersMP의 트래픽 순위 TOP5를 보여줍니다.', inline = False)
    embed.add_field(name = '==들어와', value = '봇이 음성 통화방에 들어옵니다.', inline = False)
    embed.add_field(name = '==나가', value = '봇이 음성 통화방에서 나갑니다.', inline = False)
    embed.add_field(name = '==재생', value = '봇이 음악을 재생합니다.', inline = False)
    embed.add_field(name = '==일시정지', value = '현재 재생 중인 음악을 일시 정지합니다.', inline = False)
    embed.add_field(name = '==다시재생', value = '일시 정지한 음악을 다시 재생합니다.', inline = False)
    embed.add_field(name = '==스킵', value = '현재 재생 중인 음악을 스킵합니다.', inline = False)
    embed.add_field(name = '==목록', value = '재생 목록을 보여줍니다.', inline = False)
    embed.add_field(name = '==현재재생', value = '현재 재생 중인 음악을 보여줍니다.', inline = False)
    embed.add_field(name = '==볼륨', value = '봇의 볼륨을 조절합니다.', inline = False)
    embed.add_field(name = '==정지', value = '현재 재생 중인 음악을 정지합니다.', inline = False)
    embed.add_field(name = '==삭제 <트랙 번호>', value = '재생 목록에 있는 특정 음악을 삭제합니다.', inline = False)
    embed.add_field(name = '==섞기', value = '재생 목록을 섞습니다.', inline = False)
    embed.add_field(name = '==반복', value = '현재 재생 중인 음악을 반복 재생합니다.', inline = False)
    await ctx.channel.send(embed = embed)

@client.command(pass_context = True, aliases=['==지우기'])
@commands.has_permissions(administrator=True)
async def clear(ctx, amount):
    amount = int(amount)
    if amount < 100:
        await ctx.channel.purge(limit=amount)
        await ctx.channel.send(embed=discord.Embed(title=f":warning: {amount}개의 채팅을 삭제했어요.",colour = 0x2EFEF7))
    else:
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(embed=discord.Embed(title=f":no_entry_sign: 숫자를 99 이하로 입력해 주세요.",colour = 0x2EFEF7)) 

@client.command(pass_context = True, aliases=['==내정보'])
async def myprofile(ctx):
    date = datetime.datetime.utcfromtimestamp(((int(ctx.author.id) >> 22) + 1420070400000) / 1000)
    embed = discord.Embed(title = ctx.author.display_name + "님의 정보", colour = 0x2EFEF7)
    embed.add_field(name = '사용자명', value = ctx.author.name, inline = False)
    embed.add_field(name = '가입일', value = str(date.year) + "년" + str(date.month) + "월" + str(date.day) + "일", inline = False)
    embed.add_field(name = '아이디', value = ctx.author.id, inline = False)
    embed.set_thumbnail(url = ctx.author.avatar_url)
    await ctx.channel.send(embed = embed)

@client.command(pass_context = True, aliases=['==카페'])
async def cafe(ctx):
    embed = discord.Embed(title = "KCTG 공식 카페", colour = 0x2EFEF7)
    embed.add_field(name = 'https://cafe.naver.com/kctgofficial', value = "\n\u200b", inline = False)
    embed.set_thumbnail(url = "https://cdn.discordapp.com/attachments/740877681209507880/744451389396353106/KCTG_Wolf_1.png")
    await ctx.channel.send(embed = embed)

@client.command(pass_context = True, aliases=['==실검'])
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

@client.command(pass_context = True, aliases=['==날씨'])
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

@client.command(pass_context = True, aliases=['==말해'])
async def tell(ctx, *, arg):
    tell = str(arg)
    await ctx.channel.purge(limit=1)
    await ctx.channel.send(tell)

@client.command(pass_context = True, aliases=['==유튜브'])
async def search_youtube(ctx, *, arg):
    arg_title = str(arg)
    arg = str(arg).replace(" ", "%20")
    
    browser = webdriver.Chrome('SHIA1204/dbot/chromedriver.exe')
    browser.maximize_window()

    url = f"https://www.youtube.com/results?search_query={arg}"
#    headers = {
#        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Whale/2.8.105.22 Safari/537.36",
#        "Accept-Language":"ko-KR,ko"
#        }
    #페이지 이동
    browser.get(url)

    #지정한 위치로 스크롤 내리기
    #browser.execute_script("Window.scrollTo(0, 1080)") # 1920 x 1080
    #browser.execute_script("Window.scrollTo(0, 2080)")

    #화면 가장 아래로 스크롤 내리기
    #browser.execute_script("Window.scrollTo(0, document.body.scrollHeight)")

    interval = 0.01 # ?초에 한 번씩 스크롤 내림

    #현재 문서 높이를 가져와서 저장
    prev_height = browser.execute_script("return document.body.scrollHeight")

    #반복
    while True:
        #스크롤 가장 아래로 내림
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        #페이지 로딩 대기
        time.sleep(interval)

        #현재 문서 높이를 가져와서 저장
        curr_height = browser.execute_script("return document.body.scrollHeight")
        if curr_height == prev_height:
            break

        prev_height == curr_height
    
    print("스크롤 완료")

    soup = BeautifulSoup(browser.page_source, 'lxml')

    #제목 검색
    title_one = soup.find_all("h3", attrs={"class":"title-and-badge style-scope ytd-video-renderer"})[0].get_text().strip()
    title_two = soup.find_all("h3", attrs={"class":"title-and-badge style-scope ytd-video-renderer"})[1].get_text().strip()
    title_three = soup.find_all("h3", attrs={"class":"title-and-badge style-scope ytd-video-renderer"})[2].get_text().strip()
    title_four = soup.find_all("h3", attrs={"class":"title-and-badge style-scope ytd-video-renderer"})[3].get_text().strip()
    title_five = soup.find_all("h3", attrs={"class":"title-and-badge style-scope ytd-video-renderer"})[4].get_text().strip()
    #url 탐색
    glink_one = soup.find_all("a", attrs={"class": "yt-simple-endpoint inline-block style-scope ytd-thumbnail"})[0]
    link_one = "https://www.youtube.com/" + glink_one.get("href")
    glink_two = soup.find_all("a", attrs={"class": "yt-simple-endpoint inline-block style-scope ytd-thumbnail"})[1]
    link_two = "https://www.youtube.com/" + glink_two.get("href")
    glink_three = soup.find_all("a", attrs={"class": "yt-simple-endpoint inline-block style-scope ytd-thumbnail"})[2]
    link_three = "https://www.youtube.com/" + glink_three.get("href")
    glink_four = soup.find_all("a", attrs={"class": "yt-simple-endpoint inline-block style-scope ytd-thumbnail"})[3]
    link_four = "https://www.youtube.com/" + glink_four.get("href")
    glink_five = soup.find_all("a", attrs={"class": "yt-simple-endpoint inline-block style-scope ytd-thumbnail"})[4]
    link_five = "https://www.youtube.com/" + glink_five.get("href")
    #첫번째 이미지 불러오기
    glink_one = soup.find_all("a", attrs={"class": "yt-simple-endpoint inline-block style-scope ytd-thumbnail"})[0]
    img = glink_one.find("img", attrs={"class": "style-scope yt-img-shadow"})
    top_image = img.get("src")
    #검색 결과 출력
    embed = discord.Embed(title = f":movie_camera: {arg_title} 검색 결과", colour = 0x2EFEF7)
    embed.set_author(name = '더보기', url = url)
    embed.add_field(name = f'1. {title_one}', value = f'└ {link_one}', inline = False)
    embed.add_field(name = f'2. {title_two}', value = f'└ {link_two}', inline = False)
    embed.add_field(name = f'3. {title_three}', value = f'└ {link_three}', inline = False)
    embed.add_field(name = f'4. {title_four}', value = f'└ {link_four}', inline = False)
    embed.add_field(name = f'5. {title_five}', value = f'└ {link_five}', inline = False)
    embed.set_thumbnail(url=top_image)
    await ctx.channel.send(embed = embed)

@client.command(pass_context = True, aliases=['==T정보', '==TS', '==t정보', '==ts'])
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

@client.command(pass_context = True, aliases=['==T트래픽순위', '==TTR', '==t트래픽순위', '==ttr'])
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


access_token = os.environ["BOT_TOKEN"]
client.run(access_token)
