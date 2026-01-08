import discord
from discord.ext import commands
import aiohttp
import shutil
import os

# --- add: runtime voice dependency check (PyNaCl) ---
try:
    import nacl  # noqa: F401
    VOICE_ENABLED = True
except Exception:
    VOICE_ENABLED = False
# --- end add ---

permission_integer = 3145728  # Voice permissions
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def invite(ctx):
    """Generate an invite link for the bot"""
    invite_url = discord.utils.oauth_url(
        bot.user.id, 
        permissions=discord.Permissions(permissions=permission_integer)
    )
    await ctx.send(f"Invite me: {invite_url}")

def _ffmpeg_on_path() -> bool:
    return shutil.which("ffmpeg") is not None

@bot.command()
async def play(ctx, *, query):
    # --- add: fail fast when voice dependencies are missing ---
    if not VOICE_ENABLED:
        return await ctx.send(
            "Voice is not available because **PyNaCl** isn't installed.\n"
            "Install it and restart the bot:\n"
            "`py -m pip install -U PyNaCl`"
        )
    # --- end add ---

    # --- add: fail fast when ffmpeg is missing ---
    if not _ffmpeg_on_path():
        return await ctx.send(
            "FFmpeg was not found.\n"
            "Windows: download FFmpeg, then add its **bin** folder to PATH (so `ffmpeg.exe` is reachable).\n"
            "Quick check: open a new terminal and run `ffmpeg -version`.\n"
            "Example bin path: `C:\\ffmpeg\\bin` (contains `ffmpeg.exe`)."
        )
    # --- end add ---

    if not ctx.author.voice:
        return await ctx.send("Join a voice channel first.")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.deezer.com/search?q={query}') as resp:
            data = await resp.json()
    
    if not data['data']:
        return await ctx.send("Nothing found.")
    
    track = data['data'][0]
    preview_url = track.get('preview')
    
    if not preview_url:
        return await ctx.send("No preview available.")
    
    # --- change: wrap voice connect/play to report runtime errors cleanly ---
    try:
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
    
        source = discord.FFmpegPCMAudio(preview_url)
        ctx.voice_client.play(source)
    except RuntimeError as e:
        return await ctx.send(f"Voice failed to start: `{e}`")
    # --- end change ---
    
    await ctx.send(f"Playing 30s preview: **{track['title']}** by {track['artist']['name']}")

# Read token from file
with open('token.txt', 'r') as f:
    token = f.read().strip()

bot.run(token)
