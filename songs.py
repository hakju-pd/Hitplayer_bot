# Song-Klasse und Liste für das hitplayer-Spiel


class Song:
    """Repräsentiert einen Song mit Metadaten."""
    
    def __init__(self, title: str, artist: str, year: int, genre: str):
        # TODO: Attribute speichern
        pass
    
    def get_search_query(self) -> str:
        """Gibt den Suchbegriff für Deezer zurück."""
        # TODO: Format: "{artist} {title}"
        pass
    
    def __str__(self) -> str:
        # TODO: Format: "{title} - {artist} ({year})"
        pass


class Playlist:
    """Gruppiert mehrere Songs zu einer Playlist."""
    
    def __init__(self, name: str):
        # TODO: Name und leere Song-Liste initialisieren
        pass
    
    def add_song(self, song: Song):
        """Fügt einen Song zur Playlist hinzu."""
        # TODO: Song zur Liste hinzufügen
        pass
    
    def get_random_song(self) -> Song:
        """Gibt einen zufälligen Song aus der Playlist zurück."""
        # TODO: random.choice() verwenden
        pass
    
    def __len__(self) -> int:
        # TODO: Anzahl der Songs zurückgeben
        pass


# Song-Liste - mindestens 10 Songs hinzufügen!
SONGS = []


# Globale Playlists-Liste
# Die Schüler sollen hier ihre erstellten Playlists hinzufügen
PLAYLISTS = []

# Beispiel wenn Playlists implementiert sind:
# playlist_80s = Playlist("80s Hits")
# playlist_80s.add_song(Song("Take On Me", "a-ha", 1985, "Pop"))
# ... weitere Songs ...
# 
# playlist_rock = Playlist("Rock Classics")
# playlist_rock.add_song(Song("Bohemian Rhapsody", "Queen", 1975, "Rock"))
# ... weitere Songs ...
#
# PLAYLISTS = [playlist_80s, playlist_rock]