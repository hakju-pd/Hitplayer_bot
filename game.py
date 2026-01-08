import random
from songs import SONGS


class hitplayerGame:
    """Verwaltet ein hitplayer-Spiel in einem Discord-Channel."""
    
    # Kategorien die geraten werden können
    CATEGORIES = ["year", "artist", "title", "genre"]
    
    def __init__(self):
        self.players = {}          # {user_id: {"name": ..., "points": ...}}
        self.current_song = None   # Der aktuelle Song
        self.current_category = None  # Die aktuelle Kategorie zum Raten
        self.is_active = False     # Läuft gerade eine Runde?
        self.is_running = False    # Läuft das Spiel insgesamt?
        self.guesses = {}          # {user_id: guess_value}
        self.playlist = None       # Optional: Playlist für das Spiel
    
    def start_game(self, playlist=None):
        """Startet ein neues Spiel."""
        self.players = {}
        self.current_song = None
        self.current_category = None
        self.is_active = False
        self.is_running = True
        self.guesses = {}
        self.playlist = playlist
    
    def stop_game(self):
        """Beendet das Spiel."""
        self.is_running = False
        self.is_active = False
    
    def add_player(self, user_id: int, username: str):
        """Fügt einen Spieler hinzu."""
        if user_id not in self.players:
            self.players[user_id] = {"name": username, "points": 0}
    
    def next_round(self) -> tuple[dict, str]:
        """Startet eine neue Runde mit einem zufälligen Song und Kategorie."""
        # Playlist oder SONGS verwenden
        if self.playlist:
            # TODO: Playlist.get_random_song() verwenden wenn implementiert
            # song = self.playlist.get_random_song()
            raise ValueError("Playlist-Klasse ist noch nicht implementiert!")
        else:
            if not SONGS:
                raise ValueError("Keine Songs verfügbar! Füge Songs zur SONGS-Liste hinzu.")
            self.current_song = random.choice(SONGS)
        
        self.current_category = random.choice(self.CATEGORIES)
        self.is_active = True
        self.guesses = {}
        return self.current_song, self.current_category
    
    def submit_guess(self, user_id: int, value: str) -> bool:
        """Speichert einen Tipp eines Spielers."""
        if not self.is_active:
            return False
        
        self.guesses[user_id] = value
        return True
    
    def all_players_guessed(self) -> bool:
        """Prüft ob alle Spieler geraten haben."""
        if not self.players:
            return False
        for user_id in self.players:
            if user_id not in self.guesses:
                return False
        return True
    
    def end_round(self) -> dict:
        """Beendet die Runde und berechnet die Punkte."""
        if not self.is_active or not self.current_song:
            return {}
        
        self.is_active = False
        results = {}
        
        for user_id, guess in self.guesses.items():
            points = 0
            
            if self.current_category == "year":
                # TODO: Jahr-Kategorie implementieren
                # Konvertiere die Eingabe in eine Zahl und berechne die Differenz zum tatsächlichen Jahr
                # Bei exakter Übereinstimmung: Setze points auf den Wert für exakte Treffer
                # Bei geringer Abweichung: Setze points auf den Wert für nahe Treffer
                # Beachte: Die Eingabe könnte ungültig sein
                pass
                    
            elif self.current_category == "artist":
                # TODO: Artist-Kategorie implementieren
                # Prüfe ob die Eingabe im Künstlernamen vorkommt
                # Groß-/Kleinschreibung soll ignoriert werden
                # Wenn richtig: Setze points auf den entsprechenden Wert
                pass
                    
            elif self.current_category == "title":
                # Beispiel: Titel-Kategorie (Die anderen Kategorien analog implementieren)
                if guess.lower() in self.current_song.title.lower():
                    points = 10
                    
            elif self.current_category == "genre":
                # TODO: Genre-Kategorie implementieren
                # Prüfe ob die Eingabe exakt mit dem Genre übereinstimmt
                # Groß-/Kleinschreibung soll ignoriert werden
                # Wenn richtig: Setze points auf den entsprechenden Wert
                pass
            
            # Punkte zum Spieler addieren
            if user_id in self.players:
                self.players[user_id]["points"] += points
            
            results[user_id] = {"points": points, "guess": guess}
        
        return results
    
    def get_scoreboard(self) -> list:
        """Gibt die Rangliste zurück."""
        sorted_players = sorted(
            self.players.items(),
            key=lambda x: x[1]["points"],
            reverse=True
        )
        return sorted_players
    
    def get_category_name(self) -> str:
        """Gibt den deutschen Namen der aktuellen Kategorie zurück."""
        names = {
            "year": "Jahr",
            "artist": "Künstler",
            "title": "Titel",
            "genre": "Genre"
        }
        return names.get(self.current_category, self.current_category)
    
    def get_correct_answer(self) -> str:
        """Gibt die richtige Antwort für die aktuelle Kategorie zurück."""
        if not self.current_song or not self.current_category:
            return ""
        return str(getattr(self.current_song, self.current_category))


# Speichert alle aktiven Spiele pro Channel
active_games = {}


def get_game(channel_id: int) -> hitplayerGame:
    """Holt oder erstellt ein Spiel für einen Channel."""
    if channel_id not in active_games:
        active_games[channel_id] = hitplayerGame()
    return active_games[channel_id]