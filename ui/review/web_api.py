# -*- coding: utf-8 -*-
"""Review-Bereiche: die Django-ENDPUNKTE.

Aus `web.py` herausgeloest (30.08.2026, Befund `dateigroesse`): Die
Datei war auf 361 Zeilen gewachsen und trug beides — die Endpunkte,
die Daten an den Browser liefern, und die Seiten und Infrastruktur
dahinter. Ihr eigener Kopf sagte schon „waechst mit dem Projekt — bei
Bedarf weiter teilen".

Hier stehen die acht Bereiche mit `api_`- und Datenbezug; die
Web-Seiten, Middleware, Sockets und Routen bleiben in `web.py`.
"""
BEREICHE = [
    {'slug': 'mesh_api', 'name': 'Mesh-Auslieferung und Zwischenspeicher',
     'dateien': ['HumanBodyWeb/core/dienste/charakterdaten.py',
                 {'pfad': 'HumanBodyWeb/core/api/netz.py',
                  'funktionen': ['Netzendpunkte']},
                 {'pfad': 'HumanBodyWeb/core/api/kleidung.py',
                  'funktionen': ['Kleidung']},
                 {'pfad': 'HumanBodyWeb/core/api/mhproxy.py',
                  'funktionen': ['Mhproxy']},
                 {'pfad': 'HumanBodyWeb/core/api/kleidungsbibliothek.py',
                  'funktionen': ['Kleiderbibliothek']}],
     'hinweis': (
         'Django-Endpunkte, die Netzdaten an den Browser liefern: Vertices und '
         'Indizes als base64-kodierte Float32/Uint32-Blöcke. Darunter liegen '
         'Modul-Zwischenspeicher (`_rig_hull_cache`, `_skel_geometry_cache` und '
         'die `_get_*`-Funktionen), die beim ersten Zugriff laden und danach im '
         'Prozess bleiben. Der Server ist Daphne (ASGI) und beantwortet Anfragen '
         'NEBENLÄUFIG in Fäden — die Zwischenspeicher werden also von mehreren '
         'Anfragen gleichzeitig benutzt. Die Morphdaten (.npy) sind '
         'unersetzliche Produktivdaten und werden read-only gehalten. Ein Fehler '
         'hier ist entweder ein zerstörtes Netz für alle folgenden Anfragen oder '
         'ein Speicherfresser, der über Tage wächst.'),
     'fragen': [
         'Die Zwischenspeicher sind Modul-Variablen ohne Sperre. Welcher Ablauf '
         'mit zwei gleichzeitigen Anfragen liefert falsche Daten oder lädt '
         'doppelt — und welcher verändert einen zwischengespeicherten Wert für '
         'alle folgenden Anfragen?',
         'Wo wird ein zwischengespeichertes NumPy-Array an den Aufrufer '
         'zurückgegeben, das dieser verändern kann (kein copy, kein '
         'writeable=False)? Nenne die Stelle.',
         'Die base64-Kodierung: Wo kann die Byte-Reihenfolge, der Datentyp oder '
         'die Anzahl der Elemente zwischen Server und Browser auseinanderlaufen, '
         'ohne dass es einen Fehler gibt?',
         'Was wächst unbegrenzt? Achte auf Zwischenspeicher mit Schlüsseln aus '
         'Anfragedaten.',
         'Welche Anfrage kann den Server für alle anderen blockieren (langer '
         'Rechenweg im Anfrage-Faden)?',
     ]},
    {'slug': 'jobstate', 'name': 'Job-Zustandsmaschine (Start, Stopp, Aufräumen)',
     'dateien': [{'pfad': 'HumanBodyWeb/core/api/auftraege.py',
                  'funktionen': ['Auftragsendpunkte']},
                 'HumanBodyWeb/core/dienste/auftragssteuerung.py',
                 {'pfad': 'HumanBodyWeb/core/models/auftrag.py',
                  'funktionen': ['BVHJob']}],
     'hinweis': (
         'Ein Auftrag (BVHJob) durchläuft Zustände in der Datenbank (pending, '
         'uploading, mediapipe, … , done, failed) und hat gleichzeitig einen '
         'Subprozess auf der Grafikkarte. Zwei Wahrheiten also: die Zeile in der '
         'Datenbank und der laufende Prozess. Gestoppt wird über eine '
         'STOP_FLAG-Datei im Ausgabeverzeichnis (die Pipeline prüft sie je '
         'Frame) UND über ein Verzeichnis `_active_procs` im Speicher; für '
         'Läufe, die einen Server-Neustart überleben sollen, zusätzlich über '
         'eine PID-Datei. Der Entwicklungsserver lädt bei jeder Code-Änderung '
         'neu — dann ist `_active_procs` leer, der Prozess aber noch da.'),
     'fragen': [
         'Nenne die Abläufe, nach denen Datenbank und Wirklichkeit '
         'auseinanderlaufen: Auftrag steht auf „läuft", es läuft nichts — und '
         'umgekehrt.',
         'Stoppen: Welcher der drei Wege (Datei, Speicher, PID-Datei) greift '
         'wann nicht, und was bleibt dann übrig?',
         'Was passiert bei zwei Stopp-Anfragen kurz hintereinander, und was '
         'beim Stoppen eines Auftrags, der gerade fertig wird?',
         'Die PID-Datei: Was, wenn das Betriebssystem die PID inzwischen neu '
         'vergeben hat?',
     ]},
    {'slug': 'foto3d', 'name': 'Foto-nach-3D: Ausrichtung und Textur',
     'dateien': ['HumanBodyWeb/core/dienste/fotoausrichtung.py',
                 {'pfad': 'HumanBodyWeb/core/api/fotoauftraege.py',
                  'funktionen': ['Fotoauftraege']},
                 {'pfad': 'HumanBodyWeb/core/api/fotoabgleich.py',
                  'funktionen': ['Fotoabgleich']},
                 {'pfad': 'HumanBodyWeb/core/api/smplx_ausgabe.py',
                  'funktionen': ['SmplxAusgabe']}],
     'hinweis': (
         'Aus einem Foto wird über SMPLest-X/PyMAF-X ein SMPL-X-Körper '
         'geschätzt, auf den eigenen Charakter ausgerichtet und dessen Textur '
         'aus dem Foto projiziert. EIN FEHLER, DER HIER DREIMAL GEFUNDEN WURDE '
         'und den ich NICHT nochmal hören will, weil er längst behoben ist: '
         'PyMAF-X liefert 6890 SMPL-Vertices, SMPL-X hat 10475 — die Topologien '
         'sind unvereinbar, und der Code fängt das über einen Längenvergleich '
         'ab. Suche etwas anderes: die Ausrichtung (Maßstab, Drehung, '
         'Verschiebung), die Projektion ins Bild und was bei einem schlecht '
         'erkannten Foto passiert.'),
     'fragen': [
         '_compute_auto_alignment: Woran scheitert die Ausrichtung stillschweigend '
         '(Person angeschnitten, seitlich, sitzend, mehrere Personen)?',
         'Die Projektion vom 3D-Punkt ins Bild: Passen Bildgröße, Hauptpunkt und '
         'Brennweite zu dem Bild, das der Nutzer hochgeladen hat — auch nach '
         'Skalierung oder Drehung durch EXIF?',
         'Textur: Was passiert mit Flächen, die im Foto gar nicht sichtbar sind '
         '(Rückseite, verdeckt)? Wird das erkannt oder mit Vordergrund gefüllt?',
         'Wo wird eine Division ohne Prüfung auf Null gerechnet?',
     ]},
    {'slug': 'video', 'name': 'Video-Ausgabe (Theatre, ffmpeg)',
     'dateien': [{'pfad': 'HumanBodyWeb/core/api/studio_video.py',
                  'funktionen': ['Theatrevideo']},
                 'HumanBodyWeb/core/cloth_export_api.py'],
     'hinweis': (
         'Der Browser schickt gerenderte Einzelbilder (base64-PNG) an den '
         'Server, dort werden sie mit ffmpeg zu einem Video zusammengesetzt; '
         'ein zweiter Weg rendert serverseitig mit pyrender. ffmpeg ist ein '
         'externes Programm und wird als Subprozess gestartet. '
         'Vorgeschichte, die du wissen musst: Ausgabepfad und Dateiname gehen '
         'seit dem 12.08.2026 durch SafePath (Wurzelprüfung, keine '
         'Doppelpunkte, kein führender Bindestrich), und `DATA_UPLOAD_MAX_'
         'MEMORY_SIZE` steht bewusst auf 500 MB, weil ganze Bildfolgen in '
         'einer Anfrage kommen. Suche etwas anderes.'),
     'fragen': [
         'Wo bleiben Zwischendateien liegen — bei Erfolg, bei Fehler, bei '
         'Abbruch der Anfrage mitten im Hochladen?',
         'ffmpeg: Was passiert, wenn es fehlt, wenn es einen Fehler meldet, '
         'wenn es nie zurückkommt? Wird die Ausgabe gelesen, und kann sie den '
         'Puffer füllen?',
         'Die Bildfolge: Wie wird die Reihenfolge bestimmt, und was passiert '
         'bei einem fehlenden oder doppelten Index? Was bei einem Bild, das '
         'kein PNG ist?',
         'Zwei gleichzeitige Ausgaben desselben Nutzers in dasselbe Ziel — was '
         'gewinnt, und was bleibt übrig?',
     ]},
    {'slug': 'web_models', 'name': 'Web: Datenmodell und Einstellungen',
     'dateien': ['HumanBodyWeb/core/models/auftrag.py',
                 'HumanBodyWeb/core/models/bvhdatei.py',
                 'HumanBodyWeb/core/models/einstellungen.py',
                 'HumanBodyWeb/core/models/fotoauftrag.py'],
     'hinweis': ('Die Django-Modelle: BVHJob (Auftraege mit Zustand und Fortschritt), '
                 'BVHFile (Bibliothek mit Pfad und Zeitstempel), PhotoAnalysisJob, '
                 'AppSettings (ein Singleton mit ui_prefs als JSON). Datenbank ist '
                 'SQLite und bei gleichzeitigen Schreibvorgaengen empfindlich '
                 '("database is locked"). AppSettings wird von der Pfadpruefung '
                 'SafePath gelesen, also in jedem Datei-Endpunkt.'),
     'fragen': [
         'AppSettings.load(): Was passiert bei zwei gleichzeitigen Aufrufen, wenn die '
         'Zeile noch nicht existiert?',
         'ui_prefs als JSON-Feld: Wo wird gelesen-geaendert-geschrieben, und was geht '
         'dabei verloren?',
         'BVHFile.path ist eindeutig — was beim Umbenennen einer Datei auf der Platte, '
         'was beim Wiedereinlesen?',
         'Welche Felder haben keine Begrenzung, obwohl sie aus Anfragedaten gefuellt '
         'werden?',
     ]},
    {'slug': 'api_bvh', 'name': 'API: BVH-Bibliothek und Studio-Bearbeitung',
     # Das Paket muss SELBSTTRAGEND sein: Nemotron hat am 18.08.2026 die
     # Antwort verweigert, weil `_bvh_bearbeiten`, `Retargetdaten`,
     # `Bvhverwaltung` und der BVH-Schreiber fehlten — zu Recht, ohne sie ist
     # jede Aussage zur Glaettung geraten. Jetzt liegen sie bei.
     'dateien': ['HumanBodyWeb/core/api/bvhtext.py',
                 {'pfad': 'HumanBodyWeb/core/api/retarget.py',
                  'funktionen': ['bvh_verwalten']},
                 'HumanBodyWeb/core/api/studio_projekt.py',
                 'HumanBodyWeb/core/dienste/bvh_datei.py',
                 'HumanBodyWeb/core/dienste/bvhverwaltung.py',
                 'HumanBodyWeb/core/dienste/retargetdaten.py'],
     'hinweis': ('Verwaltung und Bearbeitung der BVH-Bibliothek. ERLEDIGT und nicht '
                 'nochmal zu melden: Pfadpruefung ueber SafePath, unteilbares '
                 'Schreiben ueber AtomarSchreiber, Ursprungs- und Methodenpruefung '
                 'fuer schreibende Anfragen. Suche die BEARBEITUNG selbst: Glaetten, '
                 'Effekte, Textumwandlung.'),
     'fragen': [
         'smooth_bvh und save_bvh_effects rechnen auf Bewegungsdaten. Wo kippt das '
         'Ergebnis (Fenster groesser als die Animation, erste/letzte Frames, '
         'Quaternionen komponentenweise geglaettet)?',
         'Wird beim Glaetten ueber Quaternionen komponentenweise gemittelt? Was macht '
         'das mit der Drehung?',
         'Was passiert mit Bildrate und Kopf der BVH-Datei beim Zurueckschreiben?',
     ]},
    {'slug': 'api_pattern', 'name': 'API: Schnittmuster-Editor',
     'dateien': [{'pfad': 'HumanBodyWeb/core/api/schnittmuster.py',
                  'funktionen': ['Schnittmuster']},
                 {'pfad': 'HumanBodyWeb/core/api/schnittmuster_ablage.py',
                  'funktionen': ['Schnittmusterablage']},
                 {'pfad': 'HumanBodyWeb/core/api/netzbearbeitung.py',
                  'funktionen': ['Netzbearbeitung']},
                 'HumanBodyWeb/core/dienste/kleidungswerkzeuge.py'],
     'hinweis': ('Aus 2D-Umrissen (Bezier-Kanten) werden Kleidungsteile im Raum '
                 'platziert und zu einem Netz verbunden. Reine Geometrie, viel NumPy. '
                 'Fehler zeigen sich als Loecher, umgeklappte Flaechen oder Teile an '
                 'der falschen Stelle.'),
     'fragen': [
         'Wo wird ein 2D-Umriss als geschlossen angenommen, ohne es zu pruefen?',
         'Selbstueberschneidende oder entartete Umrisse (drei Punkte auf einer Linie, '
         'doppelte Punkte): Was passiert?',
         'Die Platzierung im Raum: Woran haengt die Orientierung, und wann zeigt ein '
         'Teil nach innen?',
     ]},
    {'slug': 'api_smpl', 'name': 'API: SMPL-Koerper und Kleidungsbibliothek',
     'dateien': ['HumanBodyWeb/core/api/smpl.py',
                 {'pfad': 'HumanBodyWeb/core/api/kleidungsbibliothek.py',
                  'funktionen': ['Kleiderendpunkte']}],
     'hinweis': ('SMPL-Koerper aus Formparametern (betas) erzeugen und Kleidung '
                 'anpassen; dazu eine Bibliothek, die das Dateisystem durchsucht. '
                 'BEKANNT UND ERLEDIGT, nicht nochmal melden: SMPL (6890 Vertices) und '
                 'SMPL-X (10475) haben unvereinbare Topologien, der Code faengt das '
                 'ueber einen Laengenvergleich ab.'),
     'fragen': [
         'Neu-Einlesen durchsucht das Dateisystem — wie lange dauert das, blockiert es '
         'die Anfrage, und was bei einem tiefen oder verknuepften Verzeichnis?',
         'betas: Werden Anzahl und Wertebereich geprueft, bevor gerechnet wird?',
         'Vorschaubilder: Wo erzeugt, wo abgelegt, wann veraltet?',
     ]},
]
