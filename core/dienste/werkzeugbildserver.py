# -*- coding: utf-8 -*-
"""Werkzeugbildserver — Gruppe „Bildvergleich: Server-Endpunkte (/api/engine2d3dkleider/…)“ des Reiters „Tools“ (03.10.2026).

Schema und Leser: `Architektur2d3dwerkzeuge`. Gelesen im Code: `core/urls_engine2d3dkleider.py` (Adressen), `core/api/engine2d3dkleider.py`,
`core/api/engine2d3dkleiderbegutachtung.py`, `Engine2d3dKleiderarbeiter`, `Engine2d3dKleidergpu`, `Engine2d3dKleiderserverstart`. Die Fotoendpunkte
stehen in der Gruppe „Fotos und Blickwinkel“, die Optionen in „Auflösungsstufen“, die Datei-Auslieferung in „Prüfbilder“. Nicht aufgenommen
(kein Bildvergleich): modell/, standmodell/, animexport/, malen/, formen/, loeschen/, runden/loeschen/. Gelaufen ist hier nichts.
"""

__all__ = ['Werkzeugbildserver']


class Werkzeugbildserver:
    A = 'HumanBodyWeb/core/api/'
    D = 'HumanBodyWeb/core/dienste/'
    END = ('HumanBodyWeb/core/api/engine2d3dkleider.py', 'Engine2d3dKleiderendpunkte')
    BEG = ('HumanBodyWeb/core/api/engine2d3dkleiderbegutachtung.py', 'Engine2d3dKleiderbegutachtungsendpunkte')
    ARBEITER = ('HumanBodyWeb/core/dienste/engine2d3dkleiderarbeiter.py', 'Engine2d3dKleiderarbeiter')
    GPU = ('HumanBodyWeb/core/dienste/engine2d3dkleidergpu.py', 'Engine2d3dKleidergpu')
    RUNDE = ('HumanBodyWeb/core/dienste/begutachtungsrunde.py', 'Begutachtungsrunde')
    KENNUNG = 'bildserver'
    TITEL = 'Bildvergleich: Server-Endpunkte (/api/engine2d3dkleider/…)'
    EINLEITUNG = (
        'Der Server ist der EINZIGE Weg, einen Lauf zu starten (Regel in der Gruppe „Regeln, Befehle und Seiten“). Reihenfolge: 1. Auftrag '
        'anlegen (Zeile 1), 2. Fotos und Rollen prüfen (Gruppe „Fotos und Blickwinkel“), 3. die Kette bis „grundfigur“ rechnen lassen '
        '(Zeile 3), 4. eine Runde starten (Zeilen 5–7), 5. den Zustand abfragen, bis status „wartet“ oder „fertig“ ist (Zeile 2), 6. Tafeln '
        'ansehen (Gruppe „Prüfbilder“). Basis: http://127.0.0.1:8081 (nie localhost, zeit-messen.md; Engine2d3dKleiderserverstart.BASIS). '
        'In den Adressen steht <id> für die UUID des Auftrags (Feld id), nicht für die Kennung. ALLE POST brauchen die CSRF-Marke wie ein '
        'Browser: GET /2d3dKleider/ (setzt das Cookie csrftoken), dann die Header X-CSRFToken (Wert des Cookies) und Referer '
        '(http://127.0.0.1:8081/2d3dKleider/) und Content-Type application/json mitsenden — fertig gebaut in '
        'Engine2d3dKleiderserverstart._post. Es rechnet eine GPU: Läuft ein anderer Auftrag (auch BlenderModel, Mesh, Mesh to 3D), '
        'antwortet der Server mit 409.'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Auftrag anlegen',
         'Legt einen Auftrag „2D3D Kleider“ mit Fotos an (oder übernimmt Fotos und Körper aus einem Auftrag „Mesh to 3D“).',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/anlegen/            multipart/form-data',
             '  name=<Text>   bilder=<Datei> (mehrfach)   rollen={"vorne.jpg": "vorne", …} (JSON)   optionen={…} (JSON)   starten=0|1',
             '  meshfigur=<Kennung eines Auftrags „Mesh to 3D“>        # statt bilder: Fotos und Körper von dort',
             '→ {ok, id, kennung, bilder, url, gestartet, hinweis}',
         )),
         [END, ('HumanBodyWeb/core/daten/engine2d3dkleiderablage.py', 'Engine2d3dKleiderablage'), ARBEITER, GPU],
         'name ist Pflicht (400 „Name fehlt“); ohne Bilder und ohne meshfigur 400. Dateitypen JPG, PNG, WebP, BMP, TIFF. rollen ordnet Dateinamen '
         'eine Rolle zu (auto, vorne, hinten, links, rechts, gesicht, detail, aus; Unbekanntes wird auto). starten ist standardmäßig 1: Der '
         'Server startet dann sofort den GANZEN Lauf, wenn die GPU frei ist (sonst gestartet=false und hinweis) — nur Fotos ablegen: '
         'starten=0. Die Schritte: netz (TRELLIS.2, 428,3–752,6 s je Auftrag; Workflowzeiten.NETZ, Datenbank, 8 Aufträge, 02.10.2026), koerper, '
         'grundfigur, iterationen, export, film, speichern. Die Kennung ist ein Zeitstempel (2026.10.03.00.45.27; Ordner, Seitenadresse), die '
         'id eine UUID (API). Quelle: Engine2d3dKleiderendpunkte.anlegen.'),

        ('Zustand lesen',
         'Status, Fortschritt, Bildauswahl und alle Ergebnisse eines Auftrags — auch die Noten und Rezepte der Runden.',
         'api',
         '\n'.join((
             'GET /api/engine2d3dkleider/<id>/zustand/',
             '→ {id, kennung, name, status, schritt, progress, progress_detail, error, optionen, bilder, ergebnis, stellung, standmodell,',
             '   laeuft, schritte, pfade, started_at, finished_at, updated_at, …}',
             'status: laeuft | wartet | fertig | gescheitert | angehalten',
         )),
         [END, ('HumanBodyWeb/core/dienste/engine2d3dkleiderzustand.py', 'Engine2d3dKleiderzustand'), ARBEITER],
         'ergebnis trägt iterationen[], kreislauf{}, begutachtung{zustand, runde, rezept[], fehler}, fotopruefung u. a. (Wo die Noten stehen: Gruppe '
         '„Maske, Umriss, Farbe und Noten“.) Die Seite fragt alle zwei Sekunden; der Endpunkt ist asynchron. Steht laeuft, aber der Prozess ist '
         'tot, setzt er den Auftrag auf „gescheitert“ („Arbeitsprozess lebt nicht mehr (auftrag.log)“). progress_detail trägt den Text der '
         'Runde („Runde 7: Rendern 2 von 3“). Das Log des Prozesses liegt im Auftragsordner als auftrag.log, die Abschnittszeiten als „<s> s '
         'Runde <n>: <Abschnitt>“ (Begutachtungswerkzeug.takt). Quelle: Engine2d3dKleiderendpunkte.zustand, Engine2d3dKleiderzustand.von.'),

        ('Lauf starten (Schritte, ganze Kette)',
         'Startet den Arbeitsprozess für einen Schrittbereich; „Weiter iterieren“ der Seite ist {ab: iterationen, bis: iterationen}.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/starten/',
             '{"ab": "iterationen", "bis": "iterationen", "optionen": {…}}      # alles optional',
             '→ {ok, pid}      # 409: läuft schon | GPU belegt | keine Grundfigur (ab nach „grundfigur“, ohne arbeit/grundkoerper.glb)',
         )),
         [END, ARBEITER, GPU, ('HumanBodyWeb/core/dienste/engine2d3dkleiderlauf.py', 'Engine2d3dKleiderlauf'),
          ('HumanBodyWeb/core/dienste/iterationskreislauf.py', 'Iterationskreislauf'), RUNDE],
         'Schritte (Engine2d3dKleiderlauf.SCHRITTE): netz, koerper, grundfigur, iterationen, export, film, speichern; ohne bis rechnet er bis zum '
         'Ende. {ab, bis: iterationen} heißt im Modus „Begutachtung“ EINE Runde OHNE Rezept (Ausgangslage oder Messung). Der Arbeitsprozess ist ein '
         'eigener Prozess (manage.py engine2d3dkleider_fahren) als Kind des Dev-Servers; ein Neustart des Servers reißt ihn nicht mit. Status '
         'danach: laeuft → wartet (Rezept von Hand), fertig (automatisch), gescheitert, angehalten. Der Lauf endet bei fehlender Grundfigur '
         'mit „Keine Grundfigur — erst den Schritt „Grundfigur“ rechnen“. Quelle: Engine2d3dKleiderendpunkte.starten, '
         'Engine2d3dKleiderlauf.ausfuehren.'),

        ('Lauf anhalten',
         'Bricht den Arbeitsprozess eines Auftrags ab.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/anhalten/        {}',
             '→ {ok}',
         )),
         [END, ARBEITER],
         'Setzt den Status „angehalten“ und beendet den Prozess samt Kindprozessen hart (taskkill /T /F; die Runner in python10 halten die '
         'GPU). Eine halb gerechnete Runde geht verloren, abgelegt sind nur fertige Runden. Ein von Hand außerhalb des Servers gestarteter '
         'Prozess wird nicht erkannt (Gruppe „Regeln, Befehle und Seiten“). Quelle: Engine2d3dKleiderarbeiter.anhalten.'),

        ('Runde mit Rezept von Hand',
         'Die Vorgabe-Runde: Fable schreibt nach dem Ansehen der Tafel ein Rezept (Aufrufe an ModellMitKleidern) und startet genau eine Runde.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/begutachtung/',
             '''{"aufrufe": "m.kleid_nur('g9_base_shirt')\\nm.haar_anteil('toulouse_hair', 0.3)", "kommentar": "Warum dieses Rezept"}''',
             '→ {ok, pid}      # 400 {error: "Rezept: Zeile n: …"} | 409 wie bei starten',
         )),
         [BEG, ('Genesis9/modellrezept.py', 'G9rezept'), ARBEITER, GPU, RUNDE],
         'aufrufe höchstens 20.000 Zeichen, kommentar 4.000 (länger wird gekürzt). Eine Zeile je Aufruf m.<funktion>(literale); der Server prüft '
         'nur Syntax, erlaubte Funktionen und Literale (G9rezept.pruefen über den Syntaxbaum, kein exec). Fehler beim ANWENDEN (unbekanntes '
         'Stück u. ä.) stehen erst in der Runde (Eintrag fehler), das Modell bleibt. Die Runde rechnet im Arbeitsprozess und endet mit '
         'Status „wartet“ — Dauer eines Laufs mit einer Runde 116–126 s (Workflowzeiten.LAUF_EINE_RUNDE, auftrag.log …20.10.04, Runden '
         '20–23, 02.10.2026). Die Rezeptzeilen selbst stehen in den Gruppen für Körper, Gesicht, Kleider und Haar. Quelle: '
         'Engine2d3dKleiderbegutachtungsendpunkte.runde.'),

        ('Runden automatisch rechnen',
         'Lässt IterationModell die Rezepte selbst schreiben, n Runden nacheinander in einem Lauf — ersetzt die Prüfung durch Fable NICHT.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/begutachtung/',
             '{"automatisch": true, "runden": 10, "kommentar": "…"}',
             '→ {ok, pid}',
         )),
         [BEG, RUNDE, ('2d3DIterationen/iterationen2d3d/iterationmodell.py', 'IterationModell'), ARBEITER, GPU],
         'runden 1–50 (Begutachtungsrunde.RUNDEN_HOECHSTENS; mehr kappt der Server stumm). Je Runde schreibt IterationModell das Rezept aus '
         'dem Befund der letzten (nur Messwerte, das Bild sieht niemand an); der Stufenwechsel der Auflösung gilt nur hier; der Block endet '
         '„fertig“ (nach „Anhalten“ oder wenn auf der höchsten Stufe nichts mehr zu ändern ist). Zeiten (Workflowzeiten, auftrag.log '
         '…20.10.04, 02.10.2026): Folgerunde im selben Lauf 27,7–28,8 s, erste Runde eines Laufs kalt 100,5–118,8 s. engine2d3dkleider.md '
         '(02.10.2026): Blöcke von 3–40 Runden ohne Prüfung dazwischen waren gegen die Vorgabe — nur zum Feinstellen zwischen zwei '
         'Prüfungen, und NUR auf Ansage von Edgar. Quelle: Begutachtungsrunde.ausfuehren.'),

        ('Runde ohne Rezept: der kleinste Weg zu einer Messung',
         'Es gibt KEINEN Einzelaufruf „vergleiche dieses Foto mit dem Modell“; der kleinste vorhandene Weg über den Server ist eine Runde ohne Rezeptzeilen.',
         'api',
         '\n'.join((
             'POST /api/engine2d3dkleider/<id>/begutachtung/   {"aufrufe": "", "kommentar": "Messung ohne Änderung"}',
             'oder',
             'POST /api/engine2d3dkleider/<id>/starten/        {"ab": "iterationen", "bis": "iterationen"}',
         )),
         [BEG, RUNDE, ('HumanBodyWeb/core/dienste/begutachtungsstand.py', 'Begutachtungsstand'),
          ('2d3DIterationen/iterationen2d3d/rundenauswahl.py', 'Rundenauswahl')],
         'Die Runde baut das Modell der besten Runde (oder der laufenden Probe) neu, rendert es aus allen Blickwinkeln, benotet es gegen alle '
         'Fotos, misst den Befund und legt Tafeln an: 116–126 s je Lauf (Quelle wie oben). Nebenwirkungen: Sie wird als neue Runde in '
         'ergebnis.iterationen abgelegt, der Status wird „wartet“, die Rundenauswahl rechnet sie ein (ein leeres Rezept ist „verworfen“, '
         'solange es nicht um mehr als 0,002 besser ausfällt; so gelesen, nicht ausprobiert). Grep über A:\\3DTools (03.10.2026): '
         'Iterationsnote.vergleichen wird nur von Begutachtungsrunde und der alten Optimierer-Schleife gerufen, kein Endpunkt, kein '
         'manage.py-Befehl rechnet Noten außerhalb einer Runde. Zwei fertige Bilder ohne Lauf: Gruppe „Maske, Umriss, Farbe und Noten“, '
         'Zeile 2; zwei Gesichter: Gruppe „Gesichtsmaße und Befundmessung“, Zeile 2.'),

        ('Rezept aller Runden lesen',
         'Die wirksamen Aufrufe aller übernommenen Runden als Text — der wiederverwendbare Weg zu diesem Modell.',
         'api',
         '\n'.join((
             'GET /api/engine2d3dkleider/<id>/rezept/            → text/plain: „# Rezept …“, „# m = ModellMitKleidern()“, je Runde „# Runde N — Kommentar“ + Aufrufe',
             'GET /api/engine2d3dkleider/<id>/rezept/?laden=1    → als Datei rezept_<kennung>.py',
         )),
         [BEG],
         'Nur Runden, deren Rezept ohne Fehler übernommen wurde (begutachtung.rezept). Der Text lässt sich Zeile für Zeile wieder einreichen — '
         'auch an einer anderen Figur. Quelle: Engine2d3dKleiderbegutachtungsendpunkte.rezept.'),

        ('Funktionen von ModellMitKleidern lesen',
         'Die erlaubten Rezeptfunktionen mit Signatur und Kurztext — die Quelle der Wahrheit für jede Rezeptzeile.',
         'api',
         '\n'.join((
             'GET /api/engine2d3dkleider/funktionen/',
             '→ {objekt: "m", funktionen: [{name, signatur, text}, …]}',
         )),
         [BEG, ('Genesis9/modellmitkleidern.py', 'ModellMitKleidern'), ('Genesis9/modellrezept.py', 'G9rezept')],
         'Ohne <id>: gilt für alle Aufträge. Die Liste ist ModellMitKleidern.hilfe() (aus den Docstrings). Wer eine Rezeptzeile braucht, fragt '
         'hier nach Name und Signatur statt aus dem Gedächtnis zu schreiben; G9rezept.pruefen lässt nur m.<funktion>(literale) zu. '
         'Dieselbe Liste steht aufklappbar im Formular „Begutachtung“ der Auftragsseite.'),

        ('Optionskatalog lesen',
         'Alle einstellbaren Optionen mit Vorgaben, Grenzen und Texten — in sechs Gruppen.',
         'api',
         '\n'.join((
             'GET /api/engine2d3dkleider/katalog/',
             '→ {figur: {optionen}, netz, mesh, koerper, iterationen, film, rollen: [{wert, text}]}',
         )),
         [END, ('HumanBodyWeb/core/dienste/engine2d3dkleideroptionen.py', 'Engine2d3dKleideroptionen')],
         'Die Gruppe iterationen enthält bildbreite, stufe_stillstand, tafelbreite (Gruppe „Auflösungsstufen“), modus, runden, form, '
         'pruefki u. a. Widerspruch im Code: Der Docstring von Engine2d3dKleiderendpunkte nennt nur „Gruppen figur, iterationen, film“, '
         'Engine2d3dKleideroptionen.GRUPPEN hat sechs. Quelle: Engine2d3dKleideroptionen.katalog.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleiderarbeiter', 'starten(job, ab, bis), anhalten(job), lebt(job)'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleidergpu', 'belegt_durch(job): 409, wenn ein anderer Bereich die GPU hält'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleiderzustand', 'von(job)'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleideroptionen', 'katalog(), pruefen(), mischen()'),
        ('Engine2d3dKleiderendpunkte', 'ruft', 'Engine2d3dKleiderablage', 'eingang_ablegen(), arbeit(): Fotos ablegen, Grundfigur prüfen'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'G9rezept', 'pruefen(aufrufe): 400, wenn das Rezept nicht lesbar ist'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'Engine2d3dKleiderarbeiter', 'starten(job, ab="iterationen", bis="iterationen")'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'Engine2d3dKleidergpu', 'belegt_durch(job)'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'Begutachtungsrunde', 'liest RUNDEN_HOECHSTENS (50): Obergrenze für runden'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'ModellMitKleidern', 'hilfe(): Name, Signatur, Kurztext der Funktionen'),
        ('Engine2d3dKleiderarbeiter', 'ruft', 'Engine2d3dKleiderlauf',
         'startet manage.py engine2d3dkleider_fahren <id>; der Befehl ruft Engine2d3dKleiderlauf(id).ausfuehren(ab, bis)'),
        ('Engine2d3dKleiderlauf', 'ruft', 'Iterationskreislauf', 'im Schritt „iterationen“'),
        ('Iterationskreislauf', 'ruft', 'Begutachtungsrunde', 'im Modus „begutachtung“: Begutachtungsrunde(lauf).ausfuehren()'),
        ('Begutachtungsrunde', 'ruft', 'IterationModell', 'rezept(): das Rezept der Automatik aus dem Befund'),
        ('Begutachtungsrunde', 'ruft', 'Begutachtungsstand', 'fortschreiben(): Gesamtnote, Auswahl, Stand'),
        ('Begutachtungsstand', 'ruft', 'Rundenauswahl', 'nach_runde(runde, gesamt, rezept)'),
    ]
