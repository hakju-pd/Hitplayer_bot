import discord
from discord.ext import commands
import aiohttp

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

@bot.command()
async def play(ctx, *, query):
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
    
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    
    source = discord.FFmpegPCMAudio(preview_url)
    ctx.voice_client.play(source)
    
    await ctx.send(f"Playing 30s preview: **{track['title']}** by {track['artist']['name']}")

# Read token from file
with open('token.txt', 'r') as f:
    token = f.read().strip()

bot.run(token)
