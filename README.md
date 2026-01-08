# 🎵 hitplayer Discord Bot - Programmieraufgabe

## Übersicht

In dieser Aufgabe erweitert ihr einen Discord Bot, der das Musikquiz-Spiel "Hitster" simuliert. Der Bot spielt Song-Previews ab und die Spieler müssen Informationen wie Jahr, Künstler, Titel oder Genre erraten.

---

## 📁 Projektstruktur

```
hitplayer/
├── main.py      # Einstiegspunkt (nicht verändern)
├── bot.py       # Discord Bot Logik
├── game.py      # Spiellogik (hitplayerGame Klasse)
├── songs.py     # Song-Klasse und Songliste 
└── token.txt    # Discord Bot Token (nicht committen!)
```

---

## ✅ Pflichtaufgaben (60 Punkte)

### Aufgabe 1: Song-Klasse implementieren (15 Punkte)

Implementiere die Klasse `Song` in `songs.py`.

**Anforderungen:**
- Attribute: `title`, `artist`, `year`, `genre`
- Methode `get_search_query()`: Gibt `"{artist} {title}"` zurück
- Methode `__str__()`: Gibt einen lesbaren String zurück, z.B. `"Bohemian Rhapsody - Queen (1975)"`


---

### Aufgabe 2: Songliste befüllen (5 Punkte)

Füge mindestens **10 Songs** zur `SONGS`-Liste in `songs.py` hinzu.

**Anforderungen:**
- Mindestens 3 verschiedene Genres
- Mindestens 3 verschiedene Jahrzehnte
- Alle Songs müssen auf Deezer verfügbar sein (Preview vorhanden)


---

### Testung von Aufgaben 1 & 2 via Discord
1. Starte den Bot mit `python main.py`.
2. Verbinde dich mit einem Discord-Server, auf dem der Bot eingeladen ist.
3. Verbinde dich mit einem Voice-Channel.
4. Nutze den Command `/hitplayer_start`, um ein Spiel zu starten.
5. Starte eine Runde mit `/hitplayer_round`.
6. Der Bot sollte einen Song abspielen


### Aufgabe 3: Punktevergabe implementieren (25 Punkte)

Implementiere die Methode `end_round()` in der Klasse `hitplayerGame` in `game.py`.

**Punktesystem:**
| Kategorie | Bedingung | Punkte |
|-----------|-----------|--------|
| Jahr | Exakt richtig | 3 |
| Jahr | ±2 Jahre | 1 |
| Künstler | Richtig | 2 |
| Titel | Richtig | 2 |
| Genre | Richtig | 1 |

**Hinweise:**
- Die aktuelle Kategorie steht in `self.current_category`
- Der aktuelle Song steht in `self.current_song`
- Die Tipps der Spieler stehen in `self.guesses` (Dictionary: `{user_id: guess_value}`)
- Nutze `.lower()` für case-insensitive Vergleiche
- Nutze `in` für Teilstring-Matching beim Künstler/Titel

### Testung von Aufgabe 3 via Discord
1. Starte den Bot mit `python main.py`.
2. Verbinde dich mit einem Discord-Server, auf dem der Bot eingeladen ist. 
3. Verbinde dich mit einem Voice-Channel.
4. Nutze den Command `/hitplayer_start`, um ein Spiel zu starten.
5. Starte eine Runde mit `/hitplayer_round`.
6. Der Bot sollte einen Song abspielen
7. Spieler können ihre Tipps mit `/guess <Text>` abgeben.
8. Beende die Runde mit `/hitplayer_finish`.
9. Der Bot sollte die Punktevergabe korrekt durchführen und im Chat anzeigen.

### Aufgabe 4: Playlist-Klasse erstellen (15 Punkte)

Erstelle eine Klasse `Playlist` in `songs.py`, die mehrere Songs gruppiert.

**Anforderungen:**
- Attribute: `name`, `songs` (Liste von Song-Objekten)
- Methode `add_song(song)`: Fügt einen Song hinzu
- Methode `get_random_song()`: Gibt einen zufälligen Song zurück
- Methode `__len__()`: Gibt die Anzahl der Songs zurück


**Zusätzlich:** Erstelle mindestens **2 verschiedene Playlists** (z.B. "80s Hits", "Rock Classics").


### Testung von Aufgabe 4 via Discord
1. Starte den Bot mit `python main.py`.
2. Verbinde dich mit einem Discord-Server, auf dem der Bot eingeladen ist.
3. Verbinde dich mit einem Voice-Channel.
4. Nutze den Command `/hitplayer_start_playlist <playlist_name>`, um ein Spiel mit der angegebenen Playlist zu starten.
5. Starte eine Runde mit `/hitplayer_round`.
6. Der Bot sollte einen Song aus der gewählten Playlist abspielen.

## ⭐ Optionale Aufgaben

### Tipps zum Erstellen eigener Commands:
- Nutze `@self.tree.command(...)` in `bot.py`, um neue Commands zu erstellen.
- Beispiel:
  ```python
  @self.tree.command(name="mein_command", description="Beschreibung")
  async def mein_command(interaction: discord.Interaction, parameter: str):
      await interaction.response.send_message(f"Du hast {parameter} eingegeben!")
  ```
- Die Nachricht, die der Bot sendet, kann mit `interaction.response.send_message(...)` angepasst werden.
- Kopiere am besten die Struktur der bestehenden Commands um leicht neue Commands zu erstellen.

### Option A: Bot mit Logo (10 Punkte)

Gib dem Bot ein eigenes Profilbild und einen benutzerdefinierten Status.

**Anforderungen:**
- Eigenes Bot-Profilbild im Discord Developer Portal
- Der Bot besitzt ein Custom Bild

**Implementierungshinweise:**
- Das Profilbild wird im Discord Developer Portal hochgeladen (nicht im Code)
- Für den Status: Nutze `activity` in der `on_ready()`-Methode in `bot.py`
- Beispiel: `await self.change_presence(activity=discord.Game(name="Hitplayer 🎵"))`

---

### Option B: Bestimmte Anzahl an Songs vor Ende (20 Punkte)
Ermögliche es, eine bestimmte Anzahl an Songs pro Spiel festzulegen.

**Anforderungen:**
- Command: `/hitplayer_start <anzahl_songs>`
- Spiel endet automatisch nach der angegebenen Anzahl
- Zeige aktuelle Runde und Gesamtrunden an

**Implementierungshinweise:**
- Füge ein Attribut `max_rounds` zur `hitplayerGame`-Klasse hinzu
- Füge ein Attribut `current_round` zur `hitplayerGame`-Klasse hinzu
- Modifiziere `hitplayer_start` in `bot.py` um einen optionalen Parameter `anzahl_songs` hinzuzufügen
- Prüfe in `start_next_round()` ob `current_round >= max_rounds`, dann automatisch `/hitplayer_finish` ausführen

---

### Option C: Schwierigkeitsgrade (20 Punkte)

Implementiere verschiedene Schwierigkeitsgrade.

| Schwierigkeit | Jahr-Toleranz | Kategorien |
|---------------|---------------|------------|
| Leicht | ±5 Jahre | Nur Jahr und Genre |
| Normal | ±2 Jahre | Alle |
| Schwer | ±1 Jahr | Alle |

**Anforderungen:**
- Command: `/hitplayer_start <difficulty>`
- Anpassung der Punktevergabe

**Implementierungshinweise:**
- Füge ein Attribut `difficulty` zur `hitplayerGame`-Klasse hinzu
- Passe `YEAR_TOLERANCE` in `hitplayerGame` dynamisch basierend auf `difficulty` an
- Filtere `CATEGORIES` basierend auf `difficulty` in der `next_round()`-Methode
- Modifiziere `hitplayer_start` in `bot.py` um einen Parameter `difficulty` hinzuzufügen
- Nutze Discord Choices für die Schwierigkeitsauswahl: `["leicht", "normal", "schwer"]`

---

### Option D: Timer pro Runde (20 Punkte)

Implementiere einen Countdown-Timer für jede Runde.

**Anforderungen:**
- Spieler haben z.B. 30 Sekunden Zeit zum Raten
- Timer wird im Chat angezeigt (z.B. "⏱️ Noch 10 Sekunden!")
- Nach Ablauf wird automatisch aufgelöst
- Command: `/hitplayer_start <sekunden>` zum Einstellen der Zeit

**Implementierungshinweise:**
- Füge ein Attribut `round_timer` zur `hitplayerGame`-Klasse hinzu
- Erstelle eine async-Funktion `start_timer()` in `bot.py`, die mit `asyncio.sleep()` arbeitet
- Starte den Timer nach `game.next_round()` im Hintergrund mit `asyncio.create_task()`
- Prüfe nach Ablauf ob `game.is_active` noch True ist, dann rufe `build_reveal_message()` auf
- Zeige Countdown-Updates im Chat (z.B. bei 30s, 10s, 5s)

---

### Option E: Hint-System (10 Punkte)

Füge einen Command `/hint` hinzu, der einen Hinweis gibt.

**Anforderungen:**
- Bei "Jahr": Zeigt das Jahrzehnt (z.B. "80er Jahre")
- Bei "Artist": Zeigt den ersten Buchstaben
- Bei "Title": Zeigt die Anzahl der Wörter
- Bei "Genre": Keine Hints verfügbar
- Hint kostet 1 Punkt Abzug bei richtiger Antwort

**Implementierungshinweise:**
- Erstelle einen neuen Command `@self.tree.command(name="hint", ...)` in `bot.py`
- Füge ein Dictionary `hint_used` zur `hitplayerGame`-Klasse hinzu: `{user_id: bool}`
- Prüfe `game.current_category` und generiere den passenden Hint
- In `end_round()`: Prüfe ob `hint_used[user_id]` True ist, dann ziehe 1 Punkt ab

---

### Option F: Skip-Voting (10 Punkte)

Implementiere ein System zum Überspringen eines Songs.

**Anforderungen:**
- Command: `/skip`
- Song wird übersprungen wenn ein einzelner Spieler /skip aufruft


**Implementierungshinweise:**
- Erstelle einen Command `@self.tree.command(name="skip", ...)` in `bot.py`
- Beim `/skip`-Aufruf: Rufe `start_next_round()` direkt auf ohne Punktevergabe

---

### Option G: Keine Doppelten Songs (10 Punkte)
Stelle sicher, dass in einem Spiel keine Songs doppelt gespielt werden.

**Implementierungshinweise:**
- Füge ein Set `played_songs` zur `hitplayerGame`-Klasse hinzu
- In `next_round()`: Wähle nur Songs die nicht in `played_songs` sind
- Füge den gewählten Song zu `played_songs` hinzu
- Bei Playlist: Erstelle eine temporäre Liste ohne bereits gespielte Songs
- Tipp: `available_songs = [s for s in SONGS if s not in self.played_songs]`
- Prüfe ob noch Songs verfügbar sind, sonst Fehlermeldung

---

### Option H: Song-Statistiken (10 Punkte)
Füge eine Statistikfunktion hinzu, die Informationen über gespielte Songs anzeigt.

**Anforderungen:**
- Command: `/stats`
- Zeige die gesamtzahl der gespielten Songs
- Zeige die Gesamtpunktzahl aller Spieler

**Implementierungshinweise:**
- Erstelle zwei Variablen in `hitplayerGame`: `total_songs_played`, `total_points`
- In `end_round()`: Erhöhe `total_songs_played` um 1 und addiere die Punkte aller Spieler zu `total_points`
- Erstelle einen Command `@self.tree.command(name="stats", ...)` in `bot.py`
- Sende eine formatierte Nachricht mit den Statistiken

---

### Option I: Help Befehl (5 Punkte)
Füge einen `/help` Command hinzu, der alle verfügbaren Commands und deren Beschreibung anzeigt.

**Implementierungshinweise:**
- Erstelle einen Command `@self.tree.command(name="help", ...)` in `bot.py`
- Erstelle einen formatierten String mit allen Commands:
  ```python
  msg = "📖 **Verfügbare Commands:**\n\n"
  msg += "`/hitplayer_start` - Startet ein neues Spiel\n"
  msg += "`/hitplayer_join` - Tritt dem Spiel bei\n"
  # ... weitere Commands ...
  ```
- Sende die Nachricht als Antwort

---

## 📝 Bewertungskriterien

**Notenschlüssel:**
| Punkte | Note |
|--------|------|
| 100+ | 1 (Sehr Gut) |
| 80-90 | 2 (Gut) |
| 70-80 | 3 (Befriedigend) |
| 60-70 | 4 (Genügend) |
| <60 | 5 (Nicht Genügend) |

---

### Abgabe

- **Deadline:** 30.01.2026
- **Format:** Uplaod der Daten auf Github Classroom
- **WICHTIG:** `token.txt` NICHT mit abgeben!

---

## 💡 Tipps

1. **Testen:** Teste jede Funktion einzeln bevor du weitermachst
2. **Print-Debugging:** Nutze `print()` um Zwischenergebnisse zu prüfen
3. **Deezer testen:** Prüfe ob deine Songs auf Deezer verfügbar sind
4. **Discord.py Docs:** https://discordpy.readthedocs.io/
5. **Fragen:** Bei Unklarheiten fragen!

---

Viel Erfolg! 🎮🎵