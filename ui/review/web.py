# -*- coding: utf-8 -*-
"""Review-Bereiche: Django-Teil (Seiten, Infrastruktur, Routen)

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte
965 Zeilen und 59 Bereiche in einer Liste — der Spitzenbefund von
`dateigroesse`. Am 30.08.2026 ein zweites Mal geteilt: Die acht
Endpunkt-Bereiche stehen jetzt in `web_api.py`.
"""
BEREICHE = [
    {'slug': 'views_serve', 'name': 'Web: Auslieferung von Dateien und Overlays',
     'dateien': [{'pfad': 'HumanBodyWeb/core/api/dateien.py',
                  'funktionen': ['serve_bvh_file', 'serve_bvh_face',
                                 'video_thumbnail', 'serve_detection_data',
                                 'save_rig_video', 'save_overlay_video']}],
     'hinweis': ('KEINE ANMELDUNG, KEIN MEHRBENUTZERBETRIEB — bitte NICHT als Befund '
                 'melden: Das ist ein Einzelplatz-Entwicklungssystem auf localhost '
                 '(DJANGOBASE zugriff="none"). Fehlende Eigentumspruefung an einer '
                 'Auftrags-Kennung (IDOR) ist deshalb kein Fall. Liefert '
                 'Ergebnisdateien eines Auftrags aus (BVH, Video, Vorschaubild, '
                 'Erkennungsdaten) und zeichnet Skelett-Overlays. Die Pfade entstehen '
                 'aus der Auftrags-Kennung; Pfade aus Anfragedaten gehen sonst durch '
                 'SafePath. Vorschaubilder und Overlays werden gecacht.'),
     'fragen': [
         'Kann eine Anfrage eine Datei ausliefern, die nicht zu ihrem Auftrag gehoert? '
         'Wie wird der Pfad gebildet?',
         'Cache der Vorschaubilder: Woran wird erkannt, dass er veraltet ist?',
         'Werden grosse Dateien gestreamt oder in den Speicher geladen? Was, wenn die '
         'Datei mitten im Ausliefern ersetzt wird?',
     ]},
    {'slug': 'views_pipelines', 'name': 'Web: Pipeline-Laeufe und Fortschritt',
     'dateien': ['HumanBodyWeb/core/pipelines/erkennung2d.py',
                 {'pfad': 'HumanBodyWeb/core/pipelines/mocapnet4.py',
                  'funktionen': ['_run_v4_pipeline']}],
     'hinweis': ('Die vier Pipeline-Laeufe. Sie starten Subprozesse ueber '
                 'PipelineProzess (Zeichensatz, stderr, Stille-Timeout sind dort seit '
                 '12./13.08.2026 geloest — NICHT nochmal melden) und deuten deren '
                 'Ausgabe: TOTAL:, STATUS:, Frame-Zaehler. Hier geht es um DIESE '
                 'Deutung und um den Fortschritt in der Datenbank.'),
     'fragen': [
         'Welche Ausgabe faehrt den Fortschrittszaehler falsch (mehrere TOTAL-Zeilen, '
         'Zahlen im Dateinamen, Fortschritt rueckwaerts)?',
         'Wie oft wird job.save() gerufen — was kostet das bei 20.000 Frames?',
         'Was passiert, wenn die erwartete Ausgabedatei fehlt, der Rueckgabewert aber '
         '0 ist?',
     ]},
    {'slug': 'web_infra', 'name': 'Web: Einstellungen, Middleware, ASGI',
     'dateien': ['HumanBodyWeb/ui/settings/__init__.py',
                 'HumanBodyWeb/ui/same_origin.py',
                 'HumanBodyWeb/ui/asgi.py'],
     'hinweis': ('Grundeinstellungen und drei Middleware-Schichten. Bekannt und '
                 'gewollt: DEBUG=True, keine Anmeldung, ALLOWED_HOSTS nur localhost, '
                 'DATA_UPLOAD_MAX_MEMORY_SIZE 500 MB (ganze Bildfolgen in einer '
                 'Anfrage), Cache-Header aus djangoBase (HTML nie aus dem Cache, '
                 'versionierte Statik lange — die eigene pauschale No-Cache-Schicht '
                 'ist am 28.08.2026 entfallen), Ursprungspruefung fuer schreibende '
                 'Methoden (neu am 13.08.2026). Einzelplatz-Entwicklungssystem, kein '
                 'Produktivbetrieb — bewerte danach.'),
     'fragen': [
         'Die Ursprungspruefung: Welcher Browser-Ablauf kommt trotzdem durch, welcher '
         'legitime wird faelschlich abgewiesen?',
         'Cache-Header: Kommt eine geaenderte JS-Datei beim Browser wirklich an, seit '
         'die pauschale No-Cache-Schicht weg ist?',
         'Wo widersprechen sich Einstellungen (Zeichensatz, Zeitzone, Sprachcode, '
         'MEDIA-/STATIC-Wurzeln)?',
         'Was ist hier gefaehrlich, WENN das System eines Tages nicht mehr nur lokal '
         'laeuft?',
     ]},
    {'slug': 'web_schutz',
     'name': 'Web: die Schutzschicht selbst (Pfade, atomares Schreiben)',
     'dateien': ['HumanBodyWeb/core/safe_paths.py', 'HumanBodyWeb/core/atomic_write.py',
                 'HumanBodyWeb/core/projekt_temp.py'],
     'hinweis': ('DIESE DREI DATEIEN SIND DIE ABSICHERUNG SELBST — hier zaehlt jeder '
                 'Fehler '
                 'doppelt, weil andere Stellen sich darauf verlassen. SafePath.pruefe '
                 'entscheidet, ob ein Pfad aus einer Anfrage erlaubt ist; '
                 'AtomarSchreiber '
                 'schreibt ueber eine Nebendatei und os.replace; ProjektTemp legt '
                 'Zwischendateien unter MEDIA_ROOT/tmp an (nie im System-Temp — dort '
                 'sind '
                 'einmal 100 GB Muell entstanden). Windows-Besonderheiten sind bekannt '
                 'und '
                 'behandelt: Datenstroeme mit Doppelpunkt, abschliessende '
                 'Punkte/Leerzeichen, '
                 'Gross-/Kleinschreibung, reservierte Namen. Ich kann alles ausfuehren '
                 'und '
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
     'dateien': ['HumanBodyWeb/core/consumers.py', 'HumanBodyWeb/core/apps.py',
                 'HumanBodyWeb/core/logging_utils.py'],
     'hinweis': ('CharacterConsumer haelt je Verbindung einen eigenen Morph-Zustand '
                 'und '
                 'schickt Vertices als Rohbytes; ProgressConsumer verteilt '
                 'Fortschrittsmeldungen. apps.ready laeuft beim Start (und bei jedem '
                 'Autoreload). logging_utils enthaelt TimestampedStream, der '
                 'sys.stdout '
                 'ersetzt und je Zeile einen Zeitstempel voranstellt — WICHTIG: '
                 'derselbe Code '
                 'steht auch in djangobase/jobctx.py; die Doppelung ist Teil der '
                 'Frage.'),
     'fragen': [
         ('CharacterConsumer: Was, wenn zwei Nachrichten gleichzeitig eintreffen und '
             'beide rechnen? Wo wird ein interner Puffer gehalten, der beim naechsten '
             'compute() ueberschrieben wird?'),
         ('TimestampedStream ersetzt sys.stdout. Was passiert bei einer Ausnahme '
          'darin, '
             'bei Teilzeilen ohne Umbruch und bei mehreren Faeden gleichzeitig? Und '
             'was, '
             'wenn Zeitstempelausgabe.einhaengen zweimal laeuft (Autoreload)?'),
         ('apps.ready: Was gehoert dort nicht hin, weil es bei jedem Reload nochmal '
             'passiert?'),
     ]},
    {'slug': 'web_urls', 'name': 'Web: Routen-Tabelle (139 Endpunkte)',
     'dateien': ['HumanBodyWeb/core/urls.py'],
     'hinweis': ('Die vollstaendige Routen-Tabelle. Hier sieht man auf einen Blick, '
                 'was ohne '
                 'Absicherung erreichbar ist: Welche Endpunkte schreiben, obwohl sie '
                 'per GET '
                 'erreichbar sind (require_POST fehlt), welche Namen doppelt vergeben '
                 'sind '
                 '(der letzte gewinnt, reverse() zeigt woanders hin), welche Muster '
                 'sich '
                 'ueberdecken. Am 13.08.2026 wurden start_processing/stop_processing '
                 'auf POST '
                 'begrenzt und zwei Pfad-Luecken geschlossen; die Tabelle ist der Ort, '
                 'an dem '
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
