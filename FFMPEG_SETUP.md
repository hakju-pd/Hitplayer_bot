# FFmpeg Setup (Windows) für Hitplayer_bot

Dein Bot nutzt Discord-Voice. Dafür muss **FFmpeg** installiert sein und in deiner **PATH**-Umgebungsvariable liegen, sodass der Befehl `ffmpeg` in jedem Terminal funktioniert.

## 1) FFmpeg herunterladen

1. Öffne: https://www.gyan.dev/ffmpeg/builds/
2. Lade **ffmpeg-release-essentials.zip** herunter (für die meisten Nutzer empfohlen).
3. Entpacke die ZIP-Datei.

Nach dem Entpacken solltest du einen Ordner haben, der ein `bin`-Verzeichnis enthält, z. B.:
- `C:\ffmpeg\bin\ffmpeg.exe`

## 2) In einen festen Ordner verschieben (empfohlen)

Verschiebe/benenne den entpackten Ordner in einen stabilen Pfad um, z. B.:
- `C:\ffmpeg\`

Stelle sicher, dass diese Datei existiert:
- `C:\ffmpeg\bin\ffmpeg.exe`

## 3) FFmpeg zu PATH hinzufügen

1. Drücke **Win** und suche nach: **Umgebungsvariablen**
2. Öffne **Systemumgebungsvariablen bearbeiten**
3. Klicke **Umgebungsvariablen...**
4. Unter **Benutzervariablen** (oder **Systemvariablen**, wenn es für alle Benutzer gelten soll) wähle **Path** → **Bearbeiten**
5. Klicke **Neu**
6. Füge diesen Ordner hinzu (der Ordner, in dem `ffmpeg.exe` liegt):
   - `C:\ffmpeg\bin`
7. Mit **OK** in allen Fenstern bestätigen/speichern.

Wichtig: Öffne danach ein **neues** Terminal (bereits offene Terminals übernehmen die PATH-Änderung nicht).

## 4) Prüfen, ob FFmpeg funktioniert

Öffne **Eingabeaufforderung** oder **PowerShell** und führe aus:

```bat
ffmpeg -version
```

Wenn PATH korrekt ist, siehst du Versionsinformationen.

Wenn die Meldung kommt, dass der Befehl nicht gefunden wurde (“not recognized as an internal or external command”), ist PATH nicht korrekt gesetzt — prüfe, dass du wirklich den **bin**-Ordner hinzugefügt hast und nicht den übergeordneten Ordner.

## 5) Bot neu starten

Schließe den Bot und starte ihn neu, nachdem FFmpeg installiert wurde und PATH aktualisiert ist.

## Fehlerbehebung

### Ich habe PATH hinzugefügt, aber es klappt trotzdem nicht
- Stelle sicher, dass du das Terminal neu geöffnet / VS Code neu gestartet / den Bot-Prozess neu gestartet hast.
- Stelle sicher, dass der PATH-Eintrag auf den Ordner zeigt, der `ffmpeg.exe` enthält:
  - Richtig: `C:\ffmpeg\bin`
  - Falsch: `C:\ffmpeg`

### Ich habe mehrere FFmpeg-Installationen
- `where ffmpeg` (Eingabeaufforderung) zeigt, welche `ffmpeg.exe` verwendet wird.
- Entferne ggf. alte PATH-Einträge.
