# -*- coding: utf-8 -*-
"""Review-Bereiche: djangoBase (geteilte Bibliothek)

Läuft in sechs Projekten — eine Änderung hier wirkt überall.

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte 965 Zeilen und 59
Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.
"""
BEREICHE = [
    {'slug': 'werkzeug', 'name': 'Das Review-Werkzeug selbst (djangoBase)',
     'wurzel': r'A:\shared\djangoBase',
     'dateien': ['djangobase/review/partner.py',
                 'djangobase/review/lauf.py',
                 'djangobase/review/faden.py',
                 'djangobase/review/register.py',
                 'djangobase/views/review.py',
                 'djangobase/aktuell.py'],
     'hinweis': (
         'Das ist der Code, der DICH gerade aufruft — heute geschrieben, in '
         'sechs Projekten eingebunden (geteiltes Paket, editable install: eine '
         'Änderung wirkt sofort überall). Django-Views plus Hintergrund-Fäden; '
         'die Läufe leben im Arbeitsspeicher, die Mitschriften auf der Platte. '
         'Geschrieben wird in den Feed nur über einen Verwaltungsbefehl, damit '
         'es keinen offenen Schreib-Endpunkt gibt. Sei hier besonders '
         'unfreundlich: Ein Werkzeug, das Fehler finden soll, darf keine haben.'),
     'fragen': [
         'Nebenläufigkeit: Was passiert bei zwei gleichzeitigen Läufen, bei '
         'zwei Nachfragen an denselben Faden, und beim Neuladen des Servers '
         'mitten in einer Runde?',
         'Der Speicherverbrauch: Ein Lauf hält den kompletten Quelltext im '
         'Verlauf. Wo wächst etwas unbegrenzt?',
         'Die Wurzelprüfung in _datei_lesen soll verhindern, dass fremde '
         'Dateien an ein Online-Modell gehen. Welche Eingabe kommt trotzdem '
         'durch (Verknüpfungen, Groß-/Kleinschreibung, UNC)?',
         'AktuellFeed schreibt eine JSON-Zeile je Eintrag und schneidet die '
         'Datei danach zurück. Was passiert bei zwei gleichzeitigen Schreibern?',
     ]},
    {'slug': 'djangobase_infra', 'name': 'djangoBase: Einstellungs-Speicher und Log-Einordnung',
     'wurzel': r'A:\shared\djangoBase',
     'dateien': ['djangobase/store.py', 'djangobase/log_classifier.py'],
     'hinweis': (
         'Geteilte Infrastruktur, in SECHS Projekten als editable install '
         'eingebunden — ein Fehler hier wirkt sofort überall, ohne dass ein '
         'Projekt etwas geändert hat. `store.py` hält die Laufzeit-'
         'Einstellungen als JSON-Datei (bewusst keine Datenbank, damit es auch '
         'ohne Migration läuft) und wird bei JEDEM Aufruf von `conf()` gelesen, '
         'also mehrmals je Anfrage. `log_classifier.py` ordnet Log-Zeilen für '
         'die Seite Hilfe→Logs ein (Ausnahmen gegen Allgemeines). Django '
         'bearbeitet Anfragen in Fäden; beide Module werden also gleichzeitig '
         'benutzt.'),
     'fragen': [
         'store.py: Was passiert bei zwei gleichzeitigen Speichervorgängen, und '
         'was, wenn der Prozess beim Schreiben stirbt? Wird die Datei bei jedem '
         'Lesen neu geparst — und was kostet das je Anfrage?',
         'Welche Eingabe in den Einstellungen kann die Datei so hinterlassen, '
         'dass die Seite danach nicht mehr lädt?',
         'log_classifier: Welche echte Log-Zeile wird falsch eingeordnet? Achte '
         'auf mehrzeilige Tracebacks, Zeilen ohne Zeitstempel und auf Zeilen, '
         'die selbst wie ein Zeitstempel aussehen.',
         'Wo ist die Laufzeit von der Länge der Log-Datei abhängig, ohne dass '
         'es begrenzt ist?',
     ]},
    {'slug': 'db_logs', 'name': 'djangoBase: Logs-Seite',
     'wurzel': r'A:\shared\djangoBase',
     'dateien': ['djangobase/views/logs.py'],
     'hinweis': ('Zeigt rotierende Logdateien in zwei Reitern (Ausnahmen/Allgemeines), mit Quellenauswahl und Filtern. Die Dateien koennen hunderte Megabyte gross sein und WACHSEN, waehrend die Seite sie liest. In sechs Projekten im Einsatz. Die Einordnung selbst (log_classifier) wurde am 13.08.2026 schon geprueft und nachgebessert — hier geht es um die SEITE.'),
     'fragen': [
         'Wie viel Speicher braucht ein Aufruf bei einer 500-MB-Datei? Wird von hinten gelesen oder alles eingelesen?',
         'Was passiert bei einer Datei, die gerade rotiert wird, und bei einer mit kaputtem Zeichensatz?',
         'Der Modus "alle Quellen chronologisch": Wie wird sortiert, was kostet das, und was passiert mit Zeilen ohne Zeitstempel?',
     ]},
    {'slug': 'db_versions', 'name': 'djangoBase: Versionen-Seite (GitHub)',
     'wurzel': r'A:\shared\djangoBase',
     'dateien': ['djangobase/views/versions.py'],
     'hinweis': ('Holt Commit-Listen aus der GitHub-API und zeigt sie je Repo — ein fremder Dienst im Anfrage-Weg: langsam, gedrosselt (403 Ratelimit), fehlerhaft oder stumm. Der Repo-Slug wird aus dem lokalen git-origin abgeleitet, wenn er nicht konfiguriert ist. In sechs Projekten im Einsatz.'),
     'fragen': [
         'Was passiert bei Drosselung, ohne Netz und bei einer Antwort, die kein JSON ist? Bleibt die Seite benutzbar?',
         'Gibt es eine Zeitgrenze fuer den Abruf, und blockiert das Warten die Anfrage?',
         'Wird gecacht? Was passiert beim Cache-Miss unter Last?',
         'Kommt ein Token zum Einsatz, und kann es in einer Fehlermeldung oder im Protokoll landen?',
     ]},
    {'slug': 'db_stats', 'name': 'djangoBase: Auslastungsanzeige, Jobs, Verkehr',
     'wurzel': r'A:\shared\djangoBase',
     'dateien': ['djangobase/system_stats.py', 'djangobase/jobs.py', 'djangobase/traffic.py'],
     'hinweis': ('system_stats liefert die Zahlen der Auslastungsleiste (GPU ueber nvidia-smi als Subprozess, CPU/RAM/Netz/Platten ueber psutil) und wird im Sekundentakt von mehreren Tabs abgefragt; dafuer gibt es HintergrundCache (stale-while-revalidate). jobs.py ist eine Registry wiederkehrender Aufgaben, traffic.py zaehlt Besuche (Middleware, opt-in).'),
     'fragen': [
         'Wo kostet ein Abruf trotz Zwischenspeicher Zeit IN der Anfrage?',
         'nvidia-smi als Subprozess: Was ohne NVIDIA-Karte, was bei einem haengenden Aufruf, und wie oft wird er wirklich gestartet?',
         'traffic: Was schreibt die Middleware je Anfrage, was kostet das bei vielen Aufrufen, und werden IP-Adressen gespeichert?',
         'jobs: Was passiert, wenn zwei Prozesse dieselbe Aufgabe starten?',
     ]},
    {'slug': 'db_benutzer', 'name': 'djangoBase: Benutzerverwaltung und Rollen',
     'wurzel': 'A:\\shared\\djangoBase',
     'dateien': ['djangobase/views/benutzer.py', 'djangobase/forms.py', 'djangobase/mixins.py'],
     'hinweis': ('GETEILTER CODE — dieselbe Datei laeuft in sechs Projekten, ein Fehler wirkt '
                 'ueberall. Die Benutzerliste zeigt Rollen, Online-Zustand und Sitzungen; '
                 '_sitzungen_map liest die Sitzungstabelle und dekodiert jede Sitzung, um den '
                 'Benutzer zu finden. BenutzerStatusView schaltet Benutzer aktiv/inaktiv. '
                 'ZugriffMixin in mixins.py entscheidet, WER diese Seiten sehen darf — das ist '
                 'die eigentliche Frage.'),
     'fragen': [
         ('ZugriffMixin: Welcher Fall kommt durch, ohne angemeldet oder berechtigt zu '
             'sein? Was ist die Vorgabe, wenn ein Projekt nichts konfiguriert?'),
         ('_sitzungen_map dekodiert Sitzungen in einer Schleife: Was kostet das bei '
             '10.000 Sitzungen, und was macht eine unlesbare Sitzung?'),
         ('BenutzerStatusView/BenutzerBearbeitenView: Darf ein Benutzer sich selbst '
             'oder einen Höherberechtigten ändern? Wo fehlt die Prüfung?'),
     ]},
    {'slug': 'db_uebersetzung', 'name': 'djangoBase: Übersetzungs-Katalog',
     'wurzel': 'A:\\shared\\djangoBase',
     'dateien': ['djangobase/uebersetzung.py', 'djangobase/templatetags/uebersetzung.py', 'djangobase/views/uebersetzung.py'],
     'hinweis': ('GETEILTER CODE. Texte werden zur Laufzeit uebersetzt und in einem Katalog in '
                 'der Datenbank gehalten; _katalog_laden haelt ihn im Modul-Speicher, '
                 'text_holen liefert aus dem Katalog oder registriert einen neuen Text. Der '
                 'Template-Tag laeuft OFT — je Seitenaufbau hunderte Male. lauf_starten '
                 'startet einen Hintergrundlauf, der fehlende Uebersetzungen holt. Zwei Fallen '
                 'liegen hier nebeneinander: ein Modul-Cache, den mehrere Faeden benutzen, und '
                 'ein Hintergrundlauf, der in die Datenbank schreibt.'),
     'fragen': [
         ('Der Modul-Cache: Was passiert bei mehreren Arbeiter-Faeden (Daphne) und wann '
             'wird er ungueltig? Kann er halb gefuellt gelesen werden?'),
         ('lauf_starten zweimal gleichzeitig: Gibt es eine Sperre, und was macht der '
             'Lauf mit der Datenbankverbindung eines Hintergrund-Fadens?'),
         ('text_holen wird je Seitenaufbau hundertfach gerufen — welche Abfrage steckt '
             'darin, und wie oft trifft sie die Datenbank?'),
     ]},
    {'slug': 'db_cache_signale', 'name': 'djangoBase: Hintergrund-Cache, Signale, Online-Zustand',
     'wurzel': 'A:\\shared\\djangoBase',
     'dateien': ['djangobase/hintergrund_cache.py', 'djangobase/signals.py', 'djangobase/online.py'],
     'hinweis': ('GETEILTER CODE. HintergrundCache liefert einen alten Wert sofort und '
                 'erneuert in einem Faden (dasselbe Muster habe ich am 13.08.2026 in die '
                 'Versionen-Seite eingebaut, nachdem sie 4,9 s in der Anfrage rechnete). '
                 'signals.py haengt an Login/Logout/Signup und schreibt dabei in die '
                 'Datenbank; online.py haelt "wer ist online" im Django-Cache und hat eine '
                 'Middleware, die bei JEDER Anfrage laeuft.'),
     'fragen': [
         ('HintergrundCache: Kann derselbe Bau zweimal gleichzeitig laufen, und was '
             'passiert bei einer Ausnahme im Faden — steht der alte Wert noch, oder ist '
             'der Cache danach fuer immer "baut gerade"?'),
         ('django_db=True heisst, der Faden benutzt die Datenbank. Wer schliesst diese '
             'Verbindung, und was passiert bei einem Faden, der oft startet?'),
         ('OnlineMiddleware laeuft bei jeder Anfrage: Wie oft schreibt sie, und was '
             'kostet das bei jedem Bild und jeder statischen Datei?'),
     ]},
]
