import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import asyncio
from collections import deque
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hitplayer_bot')

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Spotify setup
spotify_client_credentials_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
)
sp = spotipy.Spotify(client_credentials_manager=spotify_client_credentials_manager)

# Music queue for each guild
music_queues = {}

# yt-dlp options
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extract_flat': False,
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class MusicQueue:
    """Music queue handler for a guild"""
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.voice_client = None
        self.is_playing = False
        self.is_paused = False
        self.retry_count = 0
        self.max_retries = 3
        
    def add(self, song_info):
        self.queue.append(song_info)
        
    def get_next(self):
        if self.queue:
            return self.queue.popleft()
        return None
    
    def clear(self):
        self.queue.clear()
        self.current = None
        self.is_playing = False
        self.is_paused = False
        self.retry_count = 0


def get_music_queue(guild_id):
    """Get or create music queue for a guild"""
    if guild_id not in music_queues:
        music_queues[guild_id] = MusicQueue()
    return music_queues[guild_id]


def search_spotify_track(query):
    """Search for a track on Spotify and get its info"""
    try:
        # Check if it's a Spotify URL
        if 'spotify.com/track/' in query:
            track_id = query.split('track/')[-1].split('?')[0]
            track = sp.track(track_id)
        else:
            # Search for the track
            results = sp.search(q=query, limit=1, type='track')
            if not results['tracks']['items']:
                return None
            track = results['tracks']['items'][0]
        
        # Extract track information
        track_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        search_query = f"{track_name} {artists}"
        
        return {
            'title': track_name,
            'artist': artists,
            'search_query': search_query,
            'spotify_url': track['external_urls']['spotify'],
            'duration': track['duration_ms'] // 1000
        }
    except Exception as e:
        logger.error(f"Error searching Spotify: {e}")
        return None


async def get_youtube_url(search_query):
    """Get YouTube URL from search query"""
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, f"ytsearch:{search_query}", download=False)
            if 'entries' in info and info['entries']:
                video = info['entries'][0]
                return {
                    'url': video['url'],
                    'title': video.get('title', 'Unknown'),
                    'duration': video.get('duration', 0)
                }
    except Exception as e:
        logger.error(f"Error getting YouTube URL: {e}")
    return None


async def play_next(guild_id):
    """Play the next song in the queue"""
    queue = get_music_queue(guild_id)
    
    if not queue.voice_client or not queue.voice_client.is_connected():
        queue.is_playing = False
        return
    
    next_song = queue.get_next()
    if not next_song:
        queue.is_playing = False
        queue.current = None
        queue.retry_count = 0
        return
    
    queue.current = next_song
    queue.is_playing = True
    queue.is_paused = False
    
    try:
        # Get YouTube URL
        yt_info = await get_youtube_url(next_song['search_query'])
        if not yt_info:
            # Failed to get YouTube URL
            if queue.retry_count < queue.max_retries:
                queue.retry_count += 1
                logger.warning(f"Failed to get YouTube URL, retry {queue.retry_count}/{queue.max_retries}")
            else:
                logger.error(f"Skipping song after {queue.max_retries} failed attempts")
                queue.retry_count = 0
            await play_next(guild_id)
            return
        
        # Reset retry count on success
        queue.retry_count = 0
        
        # Play audio
        source = discord.FFmpegPCMAudio(yt_info['url'], **FFMPEG_OPTIONS)
        
        def after_playing(error):
            if error:
                logger.error(f"Error playing audio: {error}")
            asyncio.run_coroutine_threadsafe(play_next(guild_id), bot.loop)
        
        queue.voice_client.play(source, after=after_playing)
        
    except Exception as e:
        logger.error(f"Error playing song: {e}")
        # Only retry if we haven't exceeded max retries
        if queue.retry_count < queue.max_retries:
            queue.retry_count += 1
        else:
            logger.error(f"Skipping song after {queue.max_retries} failed attempts")
            queue.retry_count = 0
        await play_next(guild_id)


@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is ready to play music from Spotify!')
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready to play music from Spotify!')


@bot.command(name='play', help='Play a song from Spotify. Usage: !play <song name or Spotify URL>')
async def play(ctx, *, query: str):
    """Play a song from Spotify"""
    # Check if user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("❌ You need to be in a voice channel to play music!")
        return
    
    # Search Spotify
    await ctx.send(f"🔍 Searching for: {query}")
    track_info = search_spotify_track(query)
    
    if not track_info:
        await ctx.send("❌ Could not find the song on Spotify!")
        return
    
    # Get music queue
    queue = get_music_queue(ctx.guild.id)
    
    # Connect to voice channel if not connected
    if not queue.voice_client or not queue.voice_client.is_connected():
        channel = ctx.author.voice.channel
        queue.voice_client = await channel.connect()
    
    # Add to queue
    queue.add(track_info)
    
    if queue.is_playing:
        position = len(queue.queue)
        await ctx.send(f"✅ Added to queue (Position #{position}): **{track_info['title']}** by {track_info['artist']}")
    else:
        await ctx.send(f"🎵 Now playing: **{track_info['title']}** by {track_info['artist']}")
        await play_next(ctx.guild.id)


@bot.command(name='pause', help='Pause the current song')
async def pause(ctx):
    """Pause the current song"""
    queue = get_music_queue(ctx.guild.id)
    
    if queue.voice_client and queue.voice_client.is_playing():
        queue.voice_client.pause()
        queue.is_paused = True
        await ctx.send("⏸️ Paused the music")
    else:
        await ctx.send("❌ Nothing is playing right now")


@bot.command(name='resume', help='Resume the paused song')
async def resume(ctx):
    """Resume the paused song"""
    queue = get_music_queue(ctx.guild.id)
    
    if queue.voice_client and queue.is_paused:
        queue.voice_client.resume()
        queue.is_paused = False
        await ctx.send("▶️ Resumed the music")
    else:
        await ctx.send("❌ Music is not paused")


@bot.command(name='skip', help='Skip the current song')
async def skip(ctx):
    """Skip the current song"""
    queue = get_music_queue(ctx.guild.id)
    
    if queue.voice_client and queue.voice_client.is_playing():
        queue.voice_client.stop()
        await ctx.send("⏭️ Skipped the current song")
    else:
        await ctx.send("❌ Nothing is playing right now")


@bot.command(name='stop', help='Stop playing and clear the queue')
async def stop(ctx):
    """Stop playing and clear the queue"""
    queue = get_music_queue(ctx.guild.id)
    
    if queue.voice_client:
        queue.clear()
        queue.voice_client.stop()
        await ctx.send("⏹️ Stopped playing and cleared the queue")
    else:
        await ctx.send("❌ Nothing is playing right now")


@bot.command(name='queue', help='Show the current music queue')
async def show_queue(ctx):
    """Display the current music queue"""
    queue = get_music_queue(ctx.guild.id)
    
    if not queue.current and not queue.queue:
        await ctx.send("📭 The queue is empty")
        return
    
    embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.green())
    
    if queue.current:
        status = "⏸️ Paused" if queue.is_paused else "▶️ Playing"
        embed.add_field(
            name=f"Now Playing {status}",
            value=f"**{queue.current['title']}** by {queue.current['artist']}",
            inline=False
        )
    
    if queue.queue:
        upcoming = "\n".join([
            f"{i+1}. **{song['title']}** by {song['artist']}"
            for i, song in enumerate(list(queue.queue)[:10])
        ])
        embed.add_field(name="Up Next", value=upcoming, inline=False)
        
        if len(queue.queue) > 10:
            embed.set_footer(text=f"... and {len(queue.queue) - 10} more songs")
    
    await ctx.send(embed=embed)


@bot.command(name='nowplaying', aliases=['np'], help='Show the currently playing song')
async def now_playing(ctx):
    """Display the currently playing song"""
    queue = get_music_queue(ctx.guild.id)
    
    if not queue.current:
        await ctx.send("❌ Nothing is playing right now")
        return
    
    status = "⏸️ Paused" if queue.is_paused else "▶️ Playing"
    embed = discord.Embed(title=f"{status} Now Playing", color=discord.Color.blue())
    embed.add_field(name="Title", value=queue.current['title'], inline=False)
    embed.add_field(name="Artist", value=queue.current['artist'], inline=False)
    embed.add_field(name="Spotify", value=queue.current['spotify_url'], inline=False)
    
    await ctx.send(embed=embed)


@bot.command(name='leave', help='Make the bot leave the voice channel')
async def leave(ctx):
    """Disconnect from voice channel"""
    queue = get_music_queue(ctx.guild.id)
    
    if queue.voice_client:
        queue.clear()
        await queue.voice_client.disconnect()
        queue.voice_client = None
        await ctx.send("👋 Left the voice channel")
    else:
        await ctx.send("❌ I'm not in a voice channel")


@bot.command(name='help_music', help='Show all music commands')
async def help_music(ctx):
    """Display help for music commands"""
    embed = discord.Embed(
        title="🎵 Hitplayer Bot - Music Commands",
        description="A Discord bot that plays songs from Spotify!",
        color=discord.Color.purple()
    )
    
    commands_list = [
        ("!play <song or URL>", "Play a song from Spotify"),
        ("!pause", "Pause the current song"),
        ("!resume", "Resume the paused song"),
        ("!skip", "Skip the current song"),
        ("!stop", "Stop playing and clear the queue"),
        ("!queue", "Show the current music queue"),
        ("!nowplaying (or !np)", "Show the currently playing song"),
        ("!leave", "Make the bot leave the voice channel"),
    ]
    
    for cmd, desc in commands_list:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    await ctx.send(embed=embed)


def main():
    """Run the bot"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your Discord token.")
        return
    
    bot.run(token)


if __name__ == '__main__':
    main()
