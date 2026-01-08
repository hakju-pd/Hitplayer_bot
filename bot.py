import discord
from discord.ext import commands
import shutil
import asyncio
import aiohttp

from game import get_game
from songs import Song, PLAYLISTS

# --- Voice dependency check ---
try:
    import nacl  # noqa: F401
    VOICE_ENABLED = True
except Exception:
    VOICE_ENABLED = False

PERMISSION_INTEGER = 3145728


def _ffmpeg_on_path() -> bool:
    return shutil.which("ffmpeg") is not None


# TODO: Playlists importieren wenn implementiert
# from songs import playlist_80s, playlist_rock


async def search_deezer(song: Song) -> str | None:
    """Sucht einen Song auf Deezer und gibt die Preview-URL zurück."""
    query = song.get_search_query()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.deezer.com/search?q={query}") as resp:
            data = await resp.json()
    
    if data.get("data"):
        return data["data"][0].get("preview")
    return None


class HitplayerBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self._register_app_commands()

    async def setup_hook(self) -> None:
        await self.tree.sync()

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    def _register_app_commands(self) -> None:
        
        # --- Helper: Runde auflösen und Nachricht erstellen ---
        def build_reveal_message(game) -> str:
            song = game.current_song
            category_name = game.get_category_name()
            correct_answer = game.get_correct_answer()
            results = game.end_round()
            
            msg = f"🎉 **Auflösung!**\n\n"
            msg += f"🎵 **{song.title}** von **{song.artist}**\n"
            msg += f"📅 Jahr: **{song.year}** | 🎸 Genre: **{song.genre}**\n\n"
            msg += f"❓ Gesucht war **{category_name}**: **{correct_answer}**\n\n"
            
            if results:
                msg += "**Ergebnisse:**\n"
                for user_id, data in results.items():
                    player_name = game.players[user_id]["name"]
                    msg += f"• {player_name}: \"{data['guess']}\" → +{data['points']} Punkte\n"
            else:
                msg += "Niemand hat geraten!\n"
            
            return msg

        # --- Helper: Nächste Runde starten ---
        async def start_next_round(channel, vc, game):
            try:
                song, category = game.next_round()
            except ValueError as e:
                await channel.send(f"❌ {str(e)}")
                return
            
            # Preview URL von Deezer holen
            preview_url = await search_deezer(song)
            if not preview_url:
                await channel.send(f"⚠️ Kein Preview für {song} gefunden, überspringe...")
                return await start_next_round(channel, vc, game)
            
            # Audio abspielen
            if vc.is_playing():
                vc.stop()
            
            source = discord.FFmpegPCMAudio(preview_url)
            vc.play(source)
            
            category_name = game.get_category_name()
            await channel.send(
                f"🎵 **Nächste Runde!**\n\n"
                f"❓ Ratet: **{category_name}**\n\n"
                f"Nutzt `/guess <antwort>` um zu raten!"
            )

        # --- INVITE COMMAND ---
        @self.tree.command(name="invite", description="Bot Einladungslink")
        async def invite(interaction: discord.Interaction):
            invite_url = discord.utils.oauth_url(
                self.user.id,
                permissions=discord.Permissions(permissions=PERMISSION_INTEGER),
            )
            await interaction.response.send_message(f"Invite me: {invite_url}", ephemeral=True)

        # --- hitplayer: START ---
        @self.tree.command(name="hitplayer_start", description="Startet ein neues hitplayer-Spiel")
        async def hitplayer_start(interaction: discord.Interaction):
            await interaction.response.defer()
            
            # Voice-Checks
            if not VOICE_ENABLED:
                return await interaction.followup.send("PyNaCl nicht installiert!", ephemeral=True)
            if not _ffmpeg_on_path():
                return await interaction.followup.send("FFmpeg nicht gefunden!", ephemeral=True)
            
            member = interaction.user
            if not isinstance(member, discord.Member) or not member.voice:
                return await interaction.followup.send("Du musst in einem Voice-Channel sein!", ephemeral=True)
            
            # Spiel starten (ohne Playlist)
            game = get_game(interaction.channel_id)
            game.start_game()
            game.add_player(interaction.user.id, interaction.user.display_name)
            
            # Voice verbinden
            vc = interaction.guild.voice_client if interaction.guild else None
            if vc is None:
                vc = await member.voice.channel.connect()
            
            await interaction.followup.send(
                "🎮 **hitplayer-Spiel gestartet!**\n"
                "Andere Spieler: `/hitplayer_join` um mitzuspielen.\n"
                "Dann: `/hitplayer_round` für die erste Runde!\n"
                "Beenden mit: `/hitplayer_finish`"
            )

        # --- hitplayer: START MIT PLAYLIST ---
        @self.tree.command(name="hitplayer_start_playlist", description="Startet ein hitplayer-Spiel mit einer Playlist")
        async def hitplayer_start_playlist(interaction: discord.Interaction, playlist_name: str):
            await interaction.response.defer()
            
            # Voice-Checks
            if not VOICE_ENABLED:
                return await interaction.followup.send("PyNaCl nicht installiert!", ephemeral=True)
            if not _ffmpeg_on_path():
                return await interaction.followup.send("FFmpeg nicht gefunden!", ephemeral=True)
            
            member = interaction.user
            if not isinstance(member, discord.Member) or not member.voice:
                return await interaction.followup.send("Du musst in einem Voice-Channel sein!", ephemeral=True)
            
            # Playlist finden
            if not PLAYLISTS:
                return await interaction.followup.send(
                    "❌ Keine Playlists verfügbar!\n"
                    "Füge Playlists zur PLAYLISTS-Liste in songs.py hinzu.",
                    ephemeral=True
                )
            
            selected_playlist = None
            for playlist in PLAYLISTS:
                # TODO: playlist.name verwenden wenn Playlist-Klasse implementiert ist
                if hasattr(playlist, 'name') and playlist.name == playlist_name:
                    selected_playlist = playlist
                    break
            
            if not selected_playlist:
                return await interaction.followup.send(
                    f"❌ Playlist '{playlist_name}' nicht gefunden!",
                    ephemeral=True
                )
            
            # Spiel mit Playlist starten
            game = get_game(interaction.channel_id)
            game.start_game(playlist=selected_playlist)
            game.add_player(interaction.user.id, interaction.user.display_name)
            
            # Voice verbinden
            vc = interaction.guild.voice_client if interaction.guild else None
            if vc is None:
                vc = await member.voice.channel.connect()
            
            await interaction.followup.send(
                f"🎮 **hitplayer-Spiel mit Playlist '{playlist_name}' gestartet!**\n"
                f"Andere Spieler: `/hitplayer_join` um mitzuspielen.\n"
                f"Dann: `/hitplayer_round` für die erste Runde!\n"
                f"Beenden mit: `/hitplayer_finish`"
            )
        
        # Autocomplete für Playlist-Namen
        @hitplayer_start_playlist.autocomplete('playlist_name')
        async def playlist_autocomplete(
            interaction: discord.Interaction,
            current: str,
        ) -> list[discord.app_commands.Choice[str]]:
            if not PLAYLISTS:
                return []
            
            choices = []
            for playlist in PLAYLISTS:
                # TODO: playlist.name verwenden wenn Playlist-Klasse implementiert ist
                if hasattr(playlist, 'name'):
                    name = playlist.name
                    if current.lower() in name.lower():
                        choices.append(discord.app_commands.Choice(name=name, value=name))
            
            return choices[:25]  # Discord erlaubt max 25 Choices

        # --- hitplayer: JOIN ---
        @self.tree.command(name="hitplayer_join", description="Tritt dem hitplayer-Spiel bei")
        async def hitplayer_join(interaction: discord.Interaction):
            game = get_game(interaction.channel_id)
            
            if not game.is_running:
                return await interaction.response.send_message(
                    "Kein Spiel aktiv! Starte eines mit `/hitplayer_start`", ephemeral=True
                )
            
            game.add_player(interaction.user.id, interaction.user.display_name)
            await interaction.response.send_message(
                f"✅ **{interaction.user.display_name}** ist dem Spiel beigetreten!"
            )

        # --- hitplayer: ERSTE RUNDE ---
        @self.tree.command(name="hitplayer_round", description="Startet die erste Runde")
        async def hitplayer_round(interaction: discord.Interaction):
            await interaction.response.defer()
            
            game = get_game(interaction.channel_id)
            
            if not game.is_running:
                return await interaction.followup.send("Kein Spiel aktiv! Starte eines mit `/hitplayer_start`", ephemeral=True)
            
            if len(game.players) == 0:
                return await interaction.followup.send("Keine Spieler! Nutzt `/hitplayer_join`", ephemeral=True)
            
            vc = interaction.guild.voice_client if interaction.guild else None
            if vc is None:
                return await interaction.followup.send("Bot ist nicht im Voice-Channel!", ephemeral=True)
            
            # Erste Runde starten
            try:
                song, category = game.next_round()
            except ValueError as e:
                return await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)
            
            # Preview URL von Deezer holen
            preview_url = await search_deezer(song)
            if not preview_url:
                return await interaction.followup.send(f"⚠️ Kein Preview für {song} gefunden!", ephemeral=True)
            
            source = discord.FFmpegPCMAudio(preview_url)
            vc.play(source)
            
            category_name = game.get_category_name()
            await interaction.followup.send(
                f"🎵 **Runde 1!**\n\n"
                f"❓ Ratet: **{category_name}**\n\n"
                f"Nutzt `/guess <antwort>` um zu raten!"
            )

        # --- GUESS COMMAND ---
        @self.tree.command(name="guess", description="Rate die aktuelle Kategorie")
        async def guess(interaction: discord.Interaction, antwort: str):
            game = get_game(interaction.channel_id)
            
            if not game.is_active:
                return await interaction.response.send_message(
                    "Keine aktive Runde!", ephemeral=True
                )
            
            # Nur registrierte Spieler dürfen raten
            if interaction.user.id not in game.players:
                return await interaction.response.send_message(
                    "Du bist nicht im Spiel! Nutze `/hitplayer_join`", ephemeral=True
                )
            
            # Schon geraten?
            if interaction.user.id in game.guesses:
                return await interaction.response.send_message(
                    "Du hast schon geraten!", ephemeral=True
                )
            
            game.submit_guess(interaction.user.id, antwort)
            
            # Prüfen ob alle geraten haben
            if game.all_players_guessed():
                # Auflösung
                msg = build_reveal_message(game)
                await interaction.response.send_message(f"📝 **{interaction.user.display_name}** hat geraten!\n\n" + msg)
                
                # Kurze Pause
                await asyncio.sleep(3)
                
                # Nächste Runde automatisch starten (wenn Spiel noch läuft)
                if game.is_running:
                    vc = interaction.guild.voice_client if interaction.guild else None
                    if vc:
                        await start_next_round(interaction.channel, vc, game)
            else:
                # Warten auf andere Spieler
                remaining = len(game.players) - len(game.guesses)
                await interaction.response.send_message(
                    f"📝 **{interaction.user.display_name}** hat geraten! (Noch {remaining} Spieler)"
                )

        # --- hitplayer: FINISH ---
        @self.tree.command(name="hitplayer_finish", description="Beendet das Spiel und zeigt Endergebnis")
        async def hitplayer_finish(interaction: discord.Interaction):
            game = get_game(interaction.channel_id)
            
            if not game.is_running:
                return await interaction.response.send_message("Kein Spiel aktiv!", ephemeral=True)
            
            game.stop_game()
            scoreboard = game.get_scoreboard()
            
            msg = "🏁 **Spiel beendet!**\n\n🏆 **Endergebnis:**\n\n"
            
            if scoreboard:
                for i, (user_id, data) in enumerate(scoreboard, 1):
                    emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    msg += f"{emoji} **{data['name']}**: {data['points']} Punkte\n"
            else:
                msg += "Keine Spieler!\n"
            
            # Voice verlassen
            vc = interaction.guild.voice_client if interaction.guild else None
            if vc:
                await vc.disconnect()
            
            await interaction.response.send_message(msg)

        # --- hitplayer: SCOREBOARD ---
        @self.tree.command(name="hitplayer_score", description="Zeigt die aktuelle Rangliste")
        async def hitplayer_score(interaction: discord.Interaction):
            game = get_game(interaction.channel_id)
            scoreboard = game.get_scoreboard()
            
            if not scoreboard:
                return await interaction.response.send_message("Noch keine Spieler!", ephemeral=True)
            
            msg = "🏆 **Aktuelle Rangliste:**\n\n"
            for i, (user_id, data) in enumerate(scoreboard, 1):
                emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                msg += f"{emoji} **{data['name']}**: {data['points']} Punkte\n"
            
            await interaction.response.send_message(msg)

        # --- LEAVE VOICE ---
        @self.tree.command(name="leave", description="Bot verlässt den Voice-Channel")
        async def leave(interaction: discord.Interaction):
            vc = interaction.guild.voice_client if interaction.guild else None
            if vc:
                await vc.disconnect()
                await interaction.response.send_message("👋 Tschüss!")
            else:
                await interaction.response.send_message("Ich bin in keinem Channel!", ephemeral=True)