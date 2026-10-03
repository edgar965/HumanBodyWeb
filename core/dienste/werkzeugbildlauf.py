# -*- coding: utf-8 -*-
"""Werkzeugbildlauf — Gruppe „Bildvergleich: Regeln, Befehle und Seiten“ des Reiters „Tools“ (03.10.2026).

Schema und Leser: `Architektur2d3dwerkzeuge`. Gelesen im Code und in den Regeln: `Architektur2d3d.REGELN/VORGABE/PRUEFSCHLEIFE`,
`engine2d3dkleider.md` (Abschnitte „VORGABE“ und „Arbeitsprozesse nur über die Server-API“), `Engine2d3dKleiderserverstart`,
`manage.py engine2d3dkleider_fahren` und `engine2d3dkleider_pruefreihe`, `templates/engine2d3dkleider*.html`. Gelaufen ist hier nichts.
"""

__all__ = ['Werkzeugbildlauf']


class Werkzeugbildlauf:
    A = 'HumanBodyWeb/core/api/'
    D = 'HumanBodyWeb/core/dienste/'
    END = ('HumanBodyWeb/core/api/engine2d3dkleider.py', 'Engine2d3dKleiderendpunkte')
    BEG = ('HumanBodyWeb/core/api/engine2d3dkleiderbegutachtung.py', 'Engine2d3dKleiderbegutachtungsendpunkte')
    ARBEITER = ('HumanBodyWeb/core/dienste/engine2d3dkleiderarbeiter.py', 'Engine2d3dKleiderarbeiter')
    START = ('HumanBodyWeb/core/dienste/engine2d3dkleiderserverstart.py', 'Engine2d3dKleiderserverstart')
    ARCH = ('HumanBodyWeb/core/dienste/architektur2d3d.py', 'Architektur2d3d')
    KENNUNG = 'bildlauf'
    TITEL = 'Bildvergleich: Regeln, Befehle und Seiten'
    EINLEITUNG = (
        'Was jede Session wissen muss, bevor sie den Bildvergleich benutzt. 1. Wer starten darf (Zeile 1): nur Edgar oder ein ausdrücklicher '
        'Auftrag von ihm, immer über die Server-API. 2. Was nach jeder Runde geschieht (Zeile 2): Fable sieht die Tafeln an und verbessert den '
        'CODE. 3. Ob es einen Einzelvergleich gibt (Zeile 3): nein — der kleinste vorhandene Weg und die Alternativen stehen dort. Die '
        'übrigen Zeilen sind die Befehle und Seiten der Kette. Die Aufrufe der Endpunkte stehen in der Gruppe „Server-Endpunkte“.'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Wer die Schleife starten darf',
         'Eine Runde oder eine Folge automatischer Runden startet nur auf Ansage — über die Server-API, nie als Prozess eines Skripts.',
         'regel',
         'Kein Aufruf. Runden startet nur Edgar oder ein ausdrücklicher Auftrag von ihm — immer über POST …/begutachtung/ oder POST …/starten/.',
         [ARCH, END, BEG, ARBEITER, ('HumanBodyWeb/core/dienste/engine2d3dkleidergpu.py', 'Engine2d3dKleidergpu')],
         'Quelle: Architektur2d3d.REGELN „Nichts rechnet ohne Auftrag“ (Hilfe → Architektur → 2D3D, 02.10.2026). Warum über die API: Ein '
         'Arbeitsprozess, den ein Skript per Engine2d3dKleiderarbeiter.starten anstößt, stirbt mit dem Skript — der Fusion-Lauf endete am '
         '01.10.2026 um 00:41 mit dem Zeitlimit des Hintergrund-Runners, der Auftrag blieb auf „laeuft“ mit toter PID, und die GPU-Sperre sah '
         'die Karte frei (engine2d3dkleider.md). Über die API ist der Prozess Kind des Dev-Servers. Dazu: Die Prüfreihe mit --starten '
         '(rund eine halbe Stunde GPU je Auftrag, Docstring) und alles, was Blender aufruft, laufen ebenfalls nur auf Ansage; Tests '
         'nur auf Ansage (testsuite-nur-auf-ansage.md); schwere Rechnungen nicht nebenbei, wenn der Rechner belegt ist (nur-echter-chrome.md). '
         'Eine GPU: ein Lauf zur Zeit (409). Ein automatischer Block ersetzt die Prüfung nicht (nächste Zeile).'),

        ('Nach jeder Runde prüft Fable',
         'Die Vorgabe von Edgar: Runde rechnen, Tafel ansehen, benennen, den Code verbessern, festhalten — dann erst die nächste Runde.',
         'regel',
         '\n'.join((
             '1. Runde rechnen — genau eine (Reiter „Iterationen“ → „Runde rechnen“ bzw. POST …/begutachtung/)',
             '2. Ansehen — runde_NNN_vergleich.png und runde_NNN_kopf.png (Gruppe „Prüfbilder“)',
             '3. Benennen — was nicht wie auf dem Foto aussieht, mit Ort (Blickwinkel, Körperteil)',
             '4. Code verbessern — die Klasse, die den Fehler erzeugt (2d3DIterationen/, Genesis9/, core/dienste/); nur bei einem Einzelfall ein Rezept m.xxx(…)',
             '5. Festhalten — im Kommentar der Runde: was gesehen, was geändert; zurück zu 1.',
         )),
         [ARCH, ('HumanBodyWeb/core/dienste/begutachtungsrunde.py', 'Begutachtungsrunde'), BEG],
         'Edgar, 30.09.2026: „jede iteration wird von dir begutachtet, und dann neuer Code erzeugt“; 02.10.2026: „Vorgabe ist, du überprüfst und '
         'optimierst den Code, was daran ist unklar, warum steht das da nicht???“. Automatische Blöcke (IterationModell, „Weiterrechnen“, '
         '„Automatisch“) sind KEIN Ersatz: Dort liest die Regel nur Messwerte, das Bild sieht niemand an; am 01./02.10.2026 liefen Blöcke von '
         '3–40 Runden ohne Prüfung dazwischen — gegen die Vorgabe. Der Fehler wird im Code behoben, damit er beim nächsten Modell schon in '
         'Runde 1 nicht mehr entsteht; die Korrektur steht als Kommentar an der Stelle im Code. Keine lokale Prüf-KI (Edgar, 01.10.2026: '
         '„mach keine prüfung über lokale KI, die Prüfung sollst du machen!“): iterationen.pruefki steht auf aus (Vorgabe). Quelle: '
         'engine2d3dkleider.md („VORGABE“), Architektur2d3d.VORGABE und PRUEFSCHLEIFE.'),

        ('Einen Vergleich ohne die ganze Runde: was es gibt',
         'Antwort auf „kann ich EINEN Vergleich Foto gegen Modell rechnen?“: ein fertiger Einzelaufruf existiert nicht; drei Wege, vom kleinsten.',
         'regel',
         '\n'.join((
             'Kein Einzelaufruf: weder ein Endpunkt noch ein manage.py-Befehl noch eine öffentliche Methode „vergleiche dieses Foto mit dem Modell“.',
             '1. Zwei fertige Bilder: Iterationsbild.aus_render(…) + Iterationsnote.vergleichen(…)   → Gruppe „Maske, Umriss, Farbe und Noten“, Zeile 2   (Millisekunden, keine GPU)',
             '2. Zwei Gesichter: Fotolandmarken.holen(…) + Gesichtsmasse.masse(…)   → Gruppe „Gesichtsmaße und Befundmessung“, Zeile 2   (≈ 2 s + 0,3 s je Bild)',
             '3. Das Modell neu rendern und benoten: eine Runde ohne Rezept (POST …/begutachtung/ {"aufrufe": ""})   → Gruppe „Server-Endpunkte“, Zeile 7   (116–126 s, GPU)',
         )),
         [('HumanBodyWeb/core/dienste/iterationsnote.py', 'Iterationsnote'), ('HumanBodyWeb/core/dienste/gesichtsmasse.py', 'Gesichtsmasse'),
          ('HumanBodyWeb/core/dienste/begutachtungsrunde.py', 'Begutachtungsrunde')],
         'Belegt durch Grep über A:\\3DTools (03.10.2026): Iterationsnote.vergleichen wird nur von Begutachtungsrunde._runde und '
         'Iterationsrunde.bewerten (alte Optimierer-Schleife) gerufen; core/management/commands/ hat nur engine2d3dkleider_fahren, '
         'engine2d3dkleider_pruefreihe und engine2d3dkleider_standmodell. Das Modell ohne Runde rendern: Gruppe „Render aus den Blickwinkeln der '
         'Fotos“, Zeile 1 (GPU, Django, nur wenn kein Lauf die Karte hält). Die Runde misst gegen ALLE Fotos mit Winkel auf einmal; ein '
         'Vergleich nur gegen EIN Foto ist nicht vorgesehen. Die Zeiten stammen aus Workflowzeiten (auftrag.log …20.10.04, 02.10.2026).'),

        ('Arbeitsprozess von Hand starten (nicht der Weg)',
         'Der Befehl hinter dem Arbeitsprozess; der Server ruft ihn selbst. Von Hand aufrufbar, aber gegen die Regel „nur über die API“.',
         'cli',
         'A:\\3DTools\\python14\\Scripts\\python.exe A:\\3DTools\\HumanBodyWeb\\manage.py engine2d3dkleider_fahren <id> --ab iterationen --bis iterationen',
         [ARBEITER, ('HumanBodyWeb/core/dienste/engine2d3dkleiderlauf.py', 'Engine2d3dKleiderlauf')],
         '<id> ist die UUID. --ab und --bis nehmen einen Schritt aus netz, koerper, grundfigur, iterationen, export, film, speichern. Der '
         'Docstring nennt den Aufruf „von Hand aufrufbar“ (etwa --ab iterationen --bis iterationen: weitere Runden). ABER: Ein so gestarteter '
         'Prozess hängt nicht am Dev-Server — „Anhalten“ und die GPU-Sperre sehen ihn nicht, und er stirbt mit dem Skript (siehe Zeile 1). '
         'Nur auf ausdrückliche Ansage von Edgar. Quelle: Docstring des Befehls, engine2d3dkleider.md (01.10.2026).'),

        ('Prüfreihe: gespeicherte Ergebnisse gegen Sollbereiche',
         'Prüft feste Aufträge gegen Sollbereiche (Gesamtnote, Farbe je Teil, Regler am Anschlag, Messgüte, Fotos …); mit --starten rechnet sie neu.',
         'cli',
         '\n'.join((
             'A:\\3DTools\\python14\\Scripts\\python.exe A:\\3DTools\\HumanBodyWeb\\manage.py engine2d3dkleider_pruefreihe [--kennung <kennung>]',
             '… engine2d3dkleider_pruefreihe --starten       # NUR auf Ansage: rechnet jeden Auftrag erst neu (Server-API, GPU)',
         )),
         [('HumanBodyWeb/core/dienste/engine2d3dkleiderpruefreihe.py', 'Engine2d3dKleiderpruefreihe'), START],
         'Ohne --starten werden nur gespeicherte Ergebnisse gelesen und gegen die Sollbereiche aus core/daten/engine2d3dkleiderpruefreihe.json '
         'geprüft (Sekunden, keine Grafikkarte): gesamt_hoechstens, farbe_teile_hoechstens, anschlag_hoechstens, messguete, fotos_ausgelassen, '
         'frisur_kandidaten_mindestens, standmodell, ohne_fehler; Ausgabe „ok“ oder „FEHL“ je Prüfpunkt. Mit --starten je Auftrag rund eine halbe '
         'Stunde Grafikkarte (Docstring, nicht nachgemessen). Anlass (Docstring, 01.10.2026): Jede Änderung '
         'an der Pipeline läuft, auf Ansage, erst über diese Aufträge, bevor Edgar ein Ergebnis sieht. Der Befehl ruft für --starten '
         'Engine2d3dKleiderserverstart (Zeile „Server-API aus Python bedienen“). Quelle: Docstrings von Engine2d3dKleiderpruefreihe und des Befehls.'),

        ('Server-API aus Python bedienen',
         'Der fertige Client: CSRF-Marke holen, Lauf starten, auf das Ende warten.',
         'python',
         '\n'.join((
             'from core.dienste.engine2d3dkleiderserverstart import Engine2d3dKleiderserverstart',
             'start = Engine2d3dKleiderserverstart()               # BASIS http://127.0.0.1:8081; holt die CSRF-Marke selbst',
             "start.starten(job, 'iterationen', 'iterationen')     # POST …/starten/ → {ok, pid}",
             'start.automatisch(job, 10)                           # POST …/begutachtung/ {automatisch: true, runden: 10}',
             'start.warten(job)                                    # fragt alle 15 s die Datenbank → status: fertig | gescheitert | angehalten | wartet',
         )),
         [START, ARBEITER, END, BEG],
         'job ist ein Engine2d3dKleiderauftrag (Django-Kontext: warten liest job.refresh_from_db). Ein Rezept von Hand hat keine öffentliche '
         'Methode: start._post("/api/engine2d3dkleider/%s/begutachtung/" % job.id, {"aufrufe": text, "kommentar": …}) (privat). Ein kleiner '
         'Client ohne Django liegt als Wegwerfskript unter ProjektTemp/_wegwerf/trellis_hf/api2d3d.py (urllib, CSRF-Cookie von /2d3dKleider/, '
         'Wiederholung bei Neustart des Servers; Klasse Api mit hole, sende, sende_dateien) — nicht gesichert, kann verschwinden. Auch hier gilt '
         'Zeile 1: nur auf Ansage. Quelle: Docstring und Code von Engine2d3dKleiderserverstart.'),

        ('Auftragsseite, Reiter „Iterationen“',
         'Die Oberfläche der Runden: Rezept eintragen, Runde rechnen, Tabelle, Bilder ansehen.',
         'seite',
         '\n'.join((
             'http://127.0.0.1:8081/2d3dKleider/<kennung>/   → Reiter „Iterationen“',
             'Formular „Begutachtung — nächste Runde“: Rezept, Kommentar, Knöpfe „Runde rechnen“ und „Automatisch“ (Feld „Runden“), Link „Rezept aller Runden“',
             'Knöpfe „Weiter iterieren“ und „Anhalten“; Tabelle der Runden mit Unterzeile „Bilder“ (Vorlage und Render je Blickwinkel, Tafel, Kopftafel)',
         )),
         [END, ('HumanBodyWeb/core/dienste/engine2d3dkleiderzustand.py', 'Engine2d3dKleiderzustand'), BEG],
         'Das Formular „Begutachtung“ erscheint nur im Modus „Begutachtung“ (Option iterationen.modus, Vorgabe). „Runde rechnen“ schickt '
         'POST …/begutachtung/ {aufrufe, kommentar}, „Automatisch“ dasselbe mit {automatisch: true, runden} (1–50, Vorgabe im Feld 3), „Weiter '
         'iterieren“ POST …/starten/ {ab, bis: iterationen}. „Funktionen von ModellMitKleidern“ ist aufklappbar (GET …/funktionen/). Die '
         'Spalte „Abweichung“ der Tabelle ist note.abweichung (Foto plus Netz), nicht die Gesamtnote; ihr Tooltip nennt nur „(1 − '
         'Umriss-IoU) + Farbabstand“ — Widerspruch (Gruppe „Maske, Umriss, Farbe und Noten“). „Zeige nur jede x-te Iteration“ dünnt nur die '
         'Anzeige aus. Quelle: templates/engine2d3dkleider_auftrag.html, engine2d3dkleiderbegutachtung.js, engine2d3dkleiderrundenzeilen.js.'),

        ('Auftragsliste: neuer Auftrag und „Weiterrechnen“',
         'Die Liste der Aufträge: Auftrag aus Fotos anlegen, einen bestehenden um automatische Runden weiterrechnen.',
         'seite',
         '\n'.join((
             'http://127.0.0.1:8081/2d3dKleider/',
             'Formular „Neuer Auftrag“ (Name, Fotos mit Rollen; startet nicht von selbst)',
             'Feld „Runden“ (1–50, Vorgabe 10) + Knopf „Weiterrechnen“ → POST …/begutachtung/ {automatisch: true, runden}',
         )),
         [('HumanBodyWeb/core/api/engine2d3dkleiderdashboard.py', 'Engine2d3dKleiderdashboard'), BEG],
         '„Weiterrechnen“ ist nur bei genau EINEM gewählten Auftrag aktiv (die GPU rechnet einen Lauf zur Zeit) und setzt beim besten '
         'bisherigen Modell an, egal ob der Auftrag „Fertig“, „Angehalten“ oder „Wartet“ ist (engine2d3dkleiderweiter.js). Der Knopf '
         'schickt als Kommentar „Weiterrechnen aus der Liste“ und KEIN Rezept — ein automatischer Block, nicht die Prüfung (Zeile 2). '
         'Quelle: templates/engine2d3dkleider.html, engine2d3dkleiderweiter.js.'),

        ('Hilfe → Architektur → 2D3D',
         'Die Seite mit der Runde in 22 Schritten, den Entscheidungsbäumen, den Zeiten und den Klassen der Iterationen.',
         'seite',
         'http://127.0.0.1:8081/hilfe/architektur/2d3d/   → Reiter „Ablauf und Klassen“, „Workflow“, „Tools“',
         [('HumanBodyWeb/core/api/hilfe_architektur_2d3d.py', 'HilfeArchitektur2d3d'), ARCH],
         'Jede Klasse dort wird beim Aufruf der Seite gegen den Code gelesen (erster Docstring-Satz, Zeilenzahl, „fehlt“ rot). Die Zeiten '
         'je Abschnitt einer Runde stehen im Reiter „Workflow“ (Workflowzeiten, Quelle je Zahl). Quelle: Architektur2d3d, '
         'HilfeArchitektur2d3d.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Engine2d3dKleiderserverstart', 'ruft', 'Engine2d3dKleiderendpunkte', 'POST …/starten/ über HTTP (CSRF-Marke von /2d3dKleider/)'),
        ('Engine2d3dKleiderserverstart', 'ruft', 'Engine2d3dKleiderbegutachtungsendpunkte', 'POST …/begutachtung/ {automatisch, runden} über HTTP'),
        ('Engine2d3dKleiderserverstart', 'ruft', 'Engine2d3dKleiderarbeiter', 'warten(): lebt(job)'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleiderzustand', 'von(job): der Zustand für Seite und Abfrage'),
        ('Engine2d3dKleiderdashboard', 'ruft', 'Engine2d3dKleiderbegutachtungsendpunkte', 'die Seite schickt POST …/begutachtung/ (engine2d3dkleiderweiter.js)'),
        ('HilfeArchitektur2d3d', 'ruft', 'Architektur2d3d', 'kontext(): die Daten der Seite'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'Engine2d3dKleiderarbeiter', 'starten(job, ab="iterationen", bis="iterationen")'),
        ('Engine2d3dKleiderarbeiter', 'ruft', 'Engine2d3dKleiderlauf', 'startet manage.py engine2d3dkleider_fahren, der Engine2d3dKleiderlauf ausführt'),
    ]
