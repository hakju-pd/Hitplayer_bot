# Hitplayer Bot 🎵

A Discord bot that allows you to play songs from Spotify directly in your Discord voice channels!

## Features

- 🎵 Play songs from Spotify using song names or Spotify URLs
- ⏸️ Pause/Resume playback
- ⏭️ Skip songs
- 📜 Queue management
- 🎶 Now playing information
- 🔊 Multiple server support

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.8 or higher** installed
2. **FFmpeg** installed on your system
   - Ubuntu/Debian: `sudo apt-get install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
3. **Discord Bot Token** - [Create a Discord Application](https://discord.com/developers/applications)
4. **Spotify API Credentials** - [Create a Spotify App](https://developer.spotify.com/dashboard)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/hakju-pd/Hitplayer_bot.git
cd Hitplayer_bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file and add your credentials:

```env
DISCORD_TOKEN=your_discord_bot_token_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
```

#### Getting Discord Bot Token:

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Under "Token", click "Copy" to get your bot token
6. Enable "Message Content Intent" and "Voice States" under "Privileged Gateway Intents"

#### Getting Spotify API Credentials:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create an App"
3. Fill in the app name and description
4. Copy the "Client ID" and "Client Secret"

### 4. Invite Bot to Your Server

1. In Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes: `bot`, `applications.commands`
3. Select bot permissions: `Send Messages`, `Connect`, `Speak`, `Use Voice Activity`
4. Copy the generated URL and open it in your browser
5. Select your server and authorize the bot

### 5. Run the Bot

```bash
python bot.py
```

## Usage

Once the bot is running and in your server, use these commands:

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!play <song or URL>` | Play a song from Spotify | `!play Bohemian Rhapsody` or `!play https://open.spotify.com/track/...` |
| `!pause` | Pause the current song | `!pause` |
| `!resume` | Resume the paused song | `!resume` |
| `!skip` | Skip the current song | `!skip` |
| `!stop` | Stop playing and clear the queue | `!stop` |
| `!queue` | Show the current music queue | `!queue` |
| `!nowplaying` or `!np` | Show currently playing song | `!np` |
| `!leave` | Make the bot leave the voice channel | `!leave` |
| `!help_music` | Show all available commands | `!help_music` |

### Example Workflow

1. Join a voice channel in Discord
2. Type `!play Never Gonna Give You Up` to play a song
3. Type `!queue` to see what's coming up
4. Type `!skip` to skip to the next song
5. Type `!pause` to pause playback
6. Type `!resume` to continue playing
7. Type `!stop` to stop and clear the queue

## How It Works

1. **Spotify Integration**: The bot searches for songs on Spotify using the Spotipy library
2. **YouTube Download**: Since Spotify doesn't provide direct audio streams, the bot finds the song on YouTube using yt-dlp
3. **Audio Playback**: The bot streams the audio from YouTube to your Discord voice channel using FFmpeg

## Troubleshooting

### Bot doesn't join voice channel
- Make sure you're in a voice channel before running commands
- Check that the bot has "Connect" and "Speak" permissions

### "Could not find the song on Spotify" error
- Verify your Spotify API credentials are correct
- Try using a direct Spotify track URL instead of a search query

### FFmpeg errors
- Ensure FFmpeg is properly installed and in your system PATH
- Try reinstalling FFmpeg

### Bot is slow to respond
- This is normal as the bot needs to search Spotify, find the YouTube video, and start streaming
- Typically takes 5-10 seconds per song

## Dependencies

- `discord.py` - Discord API wrapper
- `py-cord` - Enhanced Discord library
- `spotipy` - Spotify API wrapper
- `yt-dlp` - YouTube video/audio downloader
- `python-dotenv` - Environment variable management
- `PyNaCl` - Voice support for Discord
- `aiohttp` - Async HTTP client

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Disclaimer

This bot is for educational purposes. Make sure to comply with Discord's Terms of Service, Spotify's Terms of Service, and YouTube's Terms of Service when using this bot.