# -*- coding: utf-8 -*-
"""Review-Bereiche: Django-Teil (Endpunkte, Aufträge, Web)

Der grösste Block: Endpunkte, Auftragslauf, Schutzschicht,
Routen. Wächst mit dem Projekt — bei Bedarf weiter teilen.

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte 965 Zeilen und 59
Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.
"""
BEREICHE = [
    {'slug': 'mesh_api', 'name': 'Mesh-Auslieferung und Zwischenspeicher',
     'dateien': ['HumanBodyWeb/core/dienste/charakterdaten.py',
                 {'pfad': 'HumanBodyWeb/core/api/netz.py',
                  'funktionen': ['character_mesh']},
                 {'pfad': 'HumanBodyWeb/core/api/kleidung.py',
                  'funktionen': ['character_cloth', 'garment_fit']},
                 {'pfad': 'HumanBodyWeb/core/api/mhproxy.py',
                  'funktionen': ['mh_proxy_fit']},
                 {'pfad': 'HumanBodyWeb/core/api/kleidungsbibliothek.py',
                  'funktionen': ['_get_garment_library']}],
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
                  'funktionen': ['job_status_api', 'start_processing',
                                 'stop_processing', 'api_stop_processing']},
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
                  'funktionen': ['analyze_photo']},
                 {'pfad': 'HumanBodyWeb/core/api/fotoabgleich.py',
                  'funktionen': ['photo_silhouette_data',
                                 'photo_save_projection']},
                 {'pfad': 'HumanBodyWeb/core/api/smplx_ausgabe.py',
                  'funktionen': ['smplx_mesh', 'smplx_texture']}],
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
                  'funktionen': ['theatre_render_video', 'theatre_encode_frames',
                                 'theatre_convert_video']},
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
     'hinweis': ('Die Django-Modelle: BVHJob (Auftraege mit Zustand und Fortschritt), BVHFile (Bibliothek mit Pfad und Zeitstempel), PhotoAnalysisJob, AppSettings (ein Singleton mit ui_prefs als JSON). Datenbank ist SQLite und bei gleichzeitigen Schreibvorgaengen empfindlich ("database is locked"). AppSettings wird von der Pfadpruefung SafePath gelesen, also in jedem Datei-Endpunkt.'),
     'fragen': [
         'AppSettings.load(): Was passiert bei zwei gleichzeitigen Aufrufen, wenn die Zeile noch nicht existiert?',
         'ui_prefs als JSON-Feld: Wo wird gelesen-geaendert-geschrieben, und was geht dabei verloren?',
         'BVHFile.path ist eindeutig — was beim Umbenennen einer Datei auf der Platte, was beim Wiedereinlesen?',
         'Welche Felder haben keine Begrenzung, obwohl sie aus Anfragedaten gefuellt werden?',
     ]},
    {'slug': 'api_bvh', 'name': 'API: BVH-Bibliothek und Studio-Bearbeitung',
     # Das Paket muss SELBSTTRAGEND sein: Nemotron hat am 18.08.2026 die
     # Antwort verweigert, weil `_bvh_bearbeiten`, `Retargetdaten`,
     # `Bvhverwaltung` und der BVH-Schreiber fehlten — zu Recht, ohne sie ist
     # jede Aussage zur Glaettung geraten. Jetzt liegen sie bei.
     'dateien': ['HumanBodyWeb/core/api/bvhtext.py',
                 {'pfad': 'HumanBodyWeb/core/api/retarget.py',
                  'funktionen': ['bvh_manage']},
                 'HumanBodyWeb/core/api/studio_projekt.py',
                 'HumanBodyWeb/core/dienste/bvh_datei.py',
                 'HumanBodyWeb/core/dienste/bvhverwaltung.py',
                 'HumanBodyWeb/core/dienste/retargetdaten.py'],
     'hinweis': ('Verwaltung und Bearbeitung der BVH-Bibliothek. ERLEDIGT und nicht nochmal zu melden: Pfadpruefung ueber SafePath, unteilbares Schreiben ueber AtomarSchreiber, Ursprungs- und Methodenpruefung fuer schreibende Anfragen. Suche die BEARBEITUNG selbst: Glaetten, Effekte, Textumwandlung.'),
     'fragen': [
         'smooth_bvh und save_bvh_effects rechnen auf Bewegungsdaten. Wo kippt das Ergebnis (Fenster groesser als die Animation, erste/letzte Frames, Quaternionen komponentenweise geglaettet)?',
         'Wird beim Glaetten ueber Quaternionen komponentenweise gemittelt? Was macht das mit der Drehung?',
         'Was passiert mit Bildrate und Kopf der BVH-Datei beim Zurueckschreiben?',
     ]},
    {'slug': 'api_pattern', 'name': 'API: Schnittmuster-Editor',
     'dateien': [{'pfad': 'HumanBodyWeb/core/api/schnittmuster.py',
                  'funktionen': ['pattern_generate', 'pattern_region_generate']},
                 {'pfad': 'HumanBodyWeb/core/api/schnittmuster_ablage.py',
                  'funktionen': ['pattern_save', 'pattern_specification']},
                 {'pfad': 'HumanBodyWeb/core/api/netzbearbeitung.py',
                  'funktionen': ['vertex_edit_smooth']},
                 'HumanBodyWeb/core/dienste/kleidungswerkzeuge.py'],
     'hinweis': ('Aus 2D-Umrissen (Bezier-Kanten) werden Kleidungsteile im Raum platziert und zu einem Netz verbunden. Reine Geometrie, viel NumPy. Fehler zeigen sich als Loecher, umgeklappte Flaechen oder Teile an der falschen Stelle.'),
     'fragen': [
         'Wo wird ein 2D-Umriss als geschlossen angenommen, ohne es zu pruefen?',
         'Selbstueberschneidende oder entartete Umrisse (drei Punkte auf einer Linie, doppelte Punkte): Was passiert?',
         'Die Platzierung im Raum: Woran haengt die Orientierung, und wann zeigt ein Teil nach innen?',
     ]},
    {'slug': 'api_smpl', 'name': 'API: SMPL-Koerper und Kleidungsbibliothek',
     'dateien': ['HumanBodyWeb/core/api/smpl.py',
                 {'pfad': 'HumanBodyWeb/core/api/kleidungsbibliothek.py',
                  'funktionen': ['garment_library', 'garment_library_rescan']}],
     'hinweis': ('SMPL-Koerper aus Formparametern (betas) erzeugen und Kleidung anpassen; dazu eine Bibliothek, die das Dateisystem durchsucht. BEKANNT UND ERLEDIGT, nicht nochmal melden: SMPL (6890 Vertices) und SMPL-X (10475) haben unvereinbare Topologien, der Code faengt das ueber einen Laengenvergleich ab.'),
     'fragen': [
         'garment_library_rescan durchsucht das Dateisystem — wie lange dauert das, blockiert es die Anfrage, und was bei einem tiefen oder verknuepften Verzeichnis?',
         'betas: Werden Anzahl und Wertebereich geprueft, bevor gerechnet wird?',
         'Vorschaubilder: Wo erzeugt, wo abgelegt, wann veraltet?',
     ]},
    {'slug': 'views_serve', 'name': 'Web: Auslieferung von Dateien und Overlays',
     'dateien': [{'pfad': 'HumanBodyWeb/core/api/dateien.py',
                  'funktionen': ['serve_bvh_file', 'serve_bvh_face',
                                 'video_thumbnail', 'serve_detection_data',
                                 'save_rig_video', 'save_overlay_video']}],
     'hinweis': ('KEINE ANMELDUNG, KEIN MEHRBENUTZERBETRIEB — bitte NICHT als Befund melden: Das ist ein Einzelplatz-Entwicklungssystem auf localhost (DJANGOBASE zugriff="none"). Fehlende Eigentumspruefung an einer Auftrags-Kennung (IDOR) ist deshalb kein Fall. Liefert Ergebnisdateien eines Auftrags aus (BVH, Video, Vorschaubild, Erkennungsdaten) und zeichnet Skelett-Overlays. Die Pfade entstehen aus der Auftrags-Kennung; Pfade aus Anfragedaten gehen sonst durch SafePath. Vorschaubilder und Overlays werden gecacht.'),
     'fragen': [
         'Kann eine Anfrage eine Datei ausliefern, die nicht zu ihrem Auftrag gehoert? Wie wird der Pfad gebildet?',
         'Cache der Vorschaubilder: Woran wird erkannt, dass er veraltet ist?',
         'Werden grosse Dateien gestreamt oder in den Speicher geladen? Was, wenn die Datei mitten im Ausliefern ersetzt wird?',
     ]},
    {'slug': 'views_pipelines', 'name': 'Web: Pipeline-Laeufe und Fortschritt',
     'dateien': ['HumanBodyWeb/core/pipelines/erkennung2d.py',
                 {'pfad': 'HumanBodyWeb/core/pipelines/mocapnet4.py',
                  'funktionen': ['_run_v4_pipeline']}],
     'hinweis': ('Die vier Pipeline-Laeufe. Sie starten Subprozesse ueber PipelineProzess (Zeichensatz, stderr, Stille-Timeout sind dort seit 12./13.08.2026 geloest — NICHT nochmal melden) und deuten deren Ausgabe: TOTAL:, STATUS:, Frame-Zaehler. Hier geht es um DIESE Deutung und um den Fortschritt in der Datenbank.'),
     'fragen': [
         'Welche Ausgabe faehrt den Fortschrittszaehler falsch (mehrere TOTAL-Zeilen, Zahlen im Dateinamen, Fortschritt rueckwaerts)?',
         'Wie oft wird job.save() gerufen — was kostet das bei 20.000 Frames?',
         'Was passiert, wenn die erwartete Ausgabedatei fehlt, der Rueckgabewert aber 0 ist?',
     ]},
    {'slug': 'web_infra', 'name': 'Web: Einstellungen, Middleware, ASGI',
     'dateien': ['HumanBodyWeb/ui/settings/__init__.py',
                 'HumanBodyWeb/ui/no_cache.py',
                 'HumanBodyWeb/ui/same_origin.py',
                 'HumanBodyWeb/ui/asgi.py'],
     'hinweis': ('Grundeinstellungen und drei Middleware-Schichten. Bekannt und gewollt: DEBUG=True, keine Anmeldung, ALLOWED_HOSTS nur localhost, DATA_UPLOAD_MAX_MEMORY_SIZE 500 MB (ganze Bildfolgen in einer Anfrage), NoCache auf ALLEN Antworten (Absicht: kein Browser-Cache), Ursprungspruefung fuer schreibende Methoden (neu am 13.08.2026). Einzelplatz-Entwicklungssystem, kein Produktivbetrieb — bewerte danach.'),
     'fragen': [
         'Die Ursprungspruefung: Welcher Browser-Ablauf kommt trotzdem durch, welcher legitime wird faelschlich abgewiesen?',
         'NoCache auf allen Antworten: Wo schadet das (Grafiken, Vorschaubilder, grosse Dateien), und was kostet es?',
         'Wo widersprechen sich Einstellungen (Zeichensatz, Zeitzone, Sprachcode, MEDIA-/STATIC-Wurzeln)?',
         'Was ist hier gefaehrlich, WENN das System eines Tages nicht mehr nur lokal laeuft?',
     ]},
    {'slug': 'web_schutz', 'name': 'Web: die Schutzschicht selbst (Pfade, atomares Schreiben)',
     'dateien': ['HumanBodyWeb/core/safe_paths.py', 'HumanBodyWeb/core/atomic_write.py', 'HumanBodyWeb/core/projekt_temp.py'],
     'hinweis': ('DIESE DREI DATEIEN SIND DIE ABSICHERUNG SELBST — hier zaehlt jeder Fehler '
                 'doppelt, weil andere Stellen sich darauf verlassen. SafePath.pruefe '
                 'entscheidet, ob ein Pfad aus einer Anfrage erlaubt ist; AtomarSchreiber '
                 'schreibt ueber eine Nebendatei und os.replace; ProjektTemp legt '
                 'Zwischendateien unter MEDIA_ROOT/tmp an (nie im System-Temp — dort sind '
                 'einmal 100 GB Muell entstanden). Windows-Besonderheiten sind bekannt und '
                 'behandelt: Datenstroeme mit Doppelpunkt, abschliessende Punkte/Leerzeichen, '
                 'Gross-/Kleinschreibung, reservierte Namen. Ich kann alles ausfuehren und '
                 'nachmessen — nenne konkrete Zeichenketten.'),
     'fragen': [
         ('Nenne eine Eingabe, die pruefe() durchlaesst und ausserhalb der Wurzeln '
             'landet. Beachte, dass _grobpruefung und die Prüfung je Pfadteil davor '
             'stehen. Ich probiere jede Zeichenkette aus.'),
         ('AtomarSchreiber: Was, wenn os.replace scheitert (Datei offen, andere '
             'Partition, Rechte) — bleibt die Nebendatei liegen, und ist das Ziel dann '
             'noch heil?'),
         ('ProjektTemp.hausmeister loescht nach Alter. Was passiert, wenn eine Datei '
             'noch benutzt wird, und wer ruft den Hausmeister eigentlich?'),
     ]},
    {'slug': 'web_sockets', 'name': 'Web: WebSockets, App-Start, Job-Protokoll',
     'dateien': ['HumanBodyWeb/core/consumers.py', 'HumanBodyWeb/core/apps.py', 'HumanBodyWeb/core/logging_utils.py'],
     'hinweis': ('CharacterConsumer haelt je Verbindung einen eigenen Morph-Zustand und '
                 'schickt Vertices als Rohbytes; ProgressConsumer verteilt '
                 'Fortschrittsmeldungen. apps.ready laeuft beim Start (und bei jedem '
                 'Autoreload). logging_utils enthaelt TimestampedStream, der sys.stdout '
                 'ersetzt und je Zeile einen Zeitstempel voranstellt — WICHTIG: derselbe Code '
                 'steht auch in djangobase/jobctx.py; die Doppelung ist Teil der Frage.'),
     'fragen': [
         ('CharacterConsumer: Was, wenn zwei Nachrichten gleichzeitig eintreffen und '
             'beide rechnen? Wo wird ein interner Puffer gehalten, der beim naechsten '
             'compute() ueberschrieben wird?'),
         ('TimestampedStream ersetzt sys.stdout. Was passiert bei einer Ausnahme darin, '
             'bei Teilzeilen ohne Umbruch und bei mehreren Faeden gleichzeitig? Und was, '
             'wenn install_stdout_timestamps zweimal laeuft (Autoreload)?'),
         ('apps.ready: Was gehoert dort nicht hin, weil es bei jedem Reload nochmal '
             'passiert?'),
     ]},
    {'slug': 'web_urls', 'name': 'Web: Routen-Tabelle (139 Endpunkte)',
     'dateien': ['HumanBodyWeb/core/urls.py'],
     'hinweis': ('Die vollstaendige Routen-Tabelle. Hier sieht man auf einen Blick, was ohne '
                 'Absicherung erreichbar ist: Welche Endpunkte schreiben, obwohl sie per GET '
                 'erreichbar sind (require_POST fehlt), welche Namen doppelt vergeben sind '
                 '(der letzte gewinnt, reverse() zeigt woanders hin), welche Muster sich '
                 'ueberdecken. Am 13.08.2026 wurden start_processing/stop_processing auf POST '
                 'begrenzt und zwei Pfad-Luecken geschlossen; die Tabelle ist der Ort, an dem '
                 'man weitere findet.'),
     'fragen': [
         ('Welche Route zeigt auf eine Funktion, die schreibt oder loescht, ist aber '
             'per GET erreichbar? Nenne Name und Zeile — ich pruefe jeden Fall am '
             'laufenden Server.'),
         ('Gibt es doppelte Routennamen oder zwei Muster, die dieselbe Anfrage fangen? '
             'Der erste Treffer gewinnt in Django.'),
         ('Welche Endpunkte nehmen einen Dateinamen oder Pfad als Teil der URL, und '
             'welche davon fehlen in der Liste der abgesicherten?'),
     ]},
    {'slug': 'jobs', 'name': 'Job- und Prozess-Lebenszyklus',
     'dateien': ['HumanBodyWeb/core/pipeline_process.py'],
     'hinweis': (
         'Django (3.14) startet ML-Pipelines als Subprozess in einer zweiten '
         'Umgebung (3.10) und liest deren stdout zeilenweise als '
         'Fortschrittskanal. Sechs Aufrufstellen benutzen diese Klasse. '
         'Vorgeschichte: Zeichensatz und stderr-Abräumen waren an je einer '
         'Stelle richtig und an den übrigen nicht; deshalb dieser Helfer.'),
     'fragen': [
         'Welcher Ablauf lässt einen Prozess oder einen Faden zurück?',
         'stdout_zeilen bricht bei Stille ab und beendet den Prozess. Welche '
         'legitime Pipeline trifft das zu Unrecht?',
         'Was passiert bei zwei gleichzeitigen Läufen, was beim '
         'Django-Autoreload mitten im Lauf?',
     ]},
]
