# -*- coding: utf-8 -*-
"""Review-Bereiche: Browser-Module der Viewer-Seiten

Alles, was im Browser läuft: Szene, Modellgenerator,
Animationsbibliothek, Kleidung, Editoren.

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte 965 Zeilen und 59
Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.
"""
BEREICHE = [
    {'slug': 'frontend', 'name': 'Frontend: Szene-Zustand und Retarget-Brücke',
     'dateien': ['HumanBodyWeb/static/viewer/scene/state.js',
                 'HumanBodyWeb/static/viewer/retarget_hybrid.js'],
     'hinweis': (
         'ES-Module ohne Bundler, Three.js über Import-Maps. scene/state.js '
         'hält den Zustand der Szene und spricht mit den API-Endpunkten; '
         'retarget_hybrid.js baut aus den Retarget-Daten des Servers einen '
         'Three.js-AnimationClip für das DEF-Skelett (176 Knochen, Namen mit '
         'Punkten werden von Three.js zu Unterstrichen). Three.js gibt '
         'Grafikspeicher nur frei, wenn dispose() aufgerufen wird — vergessene '
         'Geometrien und Texturen sammeln sich unsichtbar an.'),
     'fragen': [
         'Wo werden Three.js-Objekte, Texturen oder Geometrien ersetzt, ohne '
         'das alte dispose() aufzurufen? Nenne die Stelle, nicht das Prinzip.',
         'Wo bleiben Event-Zuhörer oder Zeitgeber nach einem Szenenwechsel '
         'hängen?',
         'Der Knochenname wird von DEF-spine.004 zu DEF-spine_004. Wo kann '
         'diese Umbenennung zwei verschiedene Knochen auf denselben Namen '
         'abbilden oder eine Spur ins Leere laufen lassen?',
         'Was passiert bei zwei schnell aufeinanderfolgenden Ladevorgängen — '
         'kann eine späte Antwort einen neueren Zustand überschreiben?',
     ]},
    {'slug': 'fe_modelgen', 'name': 'Frontend: Modellgenerator',
     'dateien': ['HumanBodyWeb/static/viewer/modellbau/modellnetz.js',
                 'HumanBodyWeb/static/viewer/modellbau/formenbauer.js',
                 'HumanBodyWeb/static/viewer/modellbau/netzverschmelzung.js'],
     'hinweis': ('Erzeugt aus dem Skelett ein Netz im Browser (Three.js, ES-Module, '
                 'kein Bundler). Ersetzt Geometrien und Materialien bei jeder '
                 'Aenderung; Three.js gibt Grafikspeicher nur bei dispose() frei. '
                 'Bekannt aus einer frueheren Runde: Die Geometrie von state.bodyMesh '
                 'wird an sechs Stellen freigegeben, Material und Texturen nicht.'),
     'fragen': [
         'Wo wird eine Geometrie, ein Material oder eine Textur ersetzt, ohne die alte '
         'freizugeben? Nenne die Stelle.',
         'Wo wird in einer Schleife pro Vertex ein neues Objekt erzeugt (Vector3, '
         'Matrix4) — und wie oft laeuft das?',
         'Was passiert bei zwei schnellen Aufrufen hintereinander?',
     ]},
    {'slug': 'fe_animations', 'name': 'Frontend: Animations-Bibliothek',
     'dateien': ['HumanBodyWeb/static/viewer/animations.js'],
     'hinweis': ('Die BVH-Bibliothek im Browser: Liste laden, Verwaltung (loeschen, '
                 'umbenennen, verschieben), Abspielen ueber AnimationMixer. Enthaelt '
                 'base64ToFloat32 — geprueft am 13.08.2026: Ausrichtung in Ordnung, '
                 'eine falsche Byte-Anzahl faellt laut auf (RangeError). Das ist '
                 'erledigt, suche anderes.'),
     'fragen': [
         'AnimationMixer und Clips: Was wird beim Wechsel der Animation nicht gestoppt '
         'oder nicht freigegeben?',
         'Die Verwaltungsaufrufe aendern die Liste — was, wenn die Antwort spaeter '
         'kommt als ein zweiter Klick?',
         'Wo wird eine Fehlerantwort des Servers stillschweigend als Erfolg behandelt?',
     ]},
    {'slug': 'fe_compare', 'name': 'Frontend: Vergleich und Skelett-Test',
     'dateien': ['HumanBodyWeb/static/viewer/viewer_compare.js',
                 'HumanBodyWeb/static/viewer/skeleton_test.js'],
     'hinweis': ('Zwei Seiten, die ZWEI Skelette bzw. Modelle gleichzeitig zeigen — '
                 'doppelte Szenen, doppelte Renderer, doppelte Ressourcen. Genau dort '
                 'schlagen fehlende dispose()-Aufrufe und doppelte '
                 'requestAnimationFrame-Schleifen am haertesten zu.'),
     'fragen': [
         'Wie viele requestAnimationFrame-Schleifen laufen nach zwei Ladevorgaengen?',
         'Wo werden Renderer oder Szenen neu angelegt, ohne die alten abzubauen '
         '(renderer.dispose, forceContextLoss)?',
         'Der Vergleich laeuft ueber Knochennamen — wo laeuft er ins Leere, ohne dass '
         'es auffaellt?',
     ]},
    {'slug': 'scene_mhproxy', 'name': 'Szene: MakeHuman-Proxy anpassen (Browser-Seite)',
     'dateien': ['HumanBodyWeb/static/viewer/scene/mh_proxy.js',
                 'HumanBodyWeb/static/viewer/scene/mhproxy_anpassen.js',
                 'HumanBodyWeb/static/viewer/scene/mhproxynetz.js'],
     'hinweis': ('Die Browser-Seite des Proxy-Fits: Der Nutzer waehlt ein '
                 'MH-Kleidungsstueck, '
                 'die Seite schickt es an /api/character/mh-proxy/fit/ und baut das '
                 'Ergebnis '
                 'in die Szene. GEMESSEN am 13.08.2026: Der Serverteil rechnet 1,14 s '
                 'IM '
                 'Anfrage-Faden. Interessant ist hier die Browser-Seite: Zustand in '
                 'localStorage (_saveMHState/_loadMHState), Kontextmenue, Liste, und '
                 'ein Fit, '
                 'der laenger dauert als ein Klick.'),
     'fragen': [
         ('Was passiert bei zwei Klicks auf "Anpassen" hintereinander (Doppelklick, '
             'oder waehrend der erste Fit laeuft)? Gibt es eine Sperre, und wenn ja, '
             'wird '
             'sie bei einem Fehler wieder gelöst?'),
         ('_saveMHState/_loadMHState: Was, wenn localStorage voll ist, der Eintrag von '
             'einer aelteren Fassung stammt oder ungueltiges JSON enthaelt?'),
         ('Wird das alte Netz beim Ersetzen freigegeben (dispose), und welche '
             'Ereignis-Zuhoerer haengen nach dem Schliessen des Kontextmenues noch '
             'dran?'),
     ]},
    {'slug': 'scene_kleider', 'name': 'Szene: Kleidung anlegen und anpassen',
     'dateien': ['HumanBodyWeb/static/viewer/scene/kleider.js',
                 'HumanBodyWeb/static/viewer/scene/garments.js'],
     'hinweis': ('Zwei Wege fuer Kleidung in der Mehr-Charakter-Szene: '
                 '_doKleiderStage1 '
                 '(grobes Anlegen) und _doKleiderFit (Anpassen an die Figur), dazu die '
                 'Liste '
                 'und das Kontextmenue. Beide rufen den Server und tauschen Netze in '
                 'der Szene '
                 'aus. Wiederholtes Anlegen/Anpassen ist der Normalfall der '
                 'Bedienung.'),
     'fragen': [
         ('Was passiert, wenn Stufe 2 (Fit) ohne Stufe 1 gerufen wird oder Stufe 1 '
             'zweimal laeuft?'),
         ('Wo bleiben Geometrien, Materialien oder Texturen liegen, wenn ein '
             'Kleidungsstueck ersetzt oder entfernt wird?'),
         ('Die Liste wird bei jeder Aenderung neu gebaut (_renderKleiderList): Wo '
          'gehen '
             'dabei Zuhoerer oder Auswahlzustand verloren?'),
     ]},
    {'slug': 'scene_saveload', 'name': 'Szene: speichern, laden, Charaktere',
     'dateien': ['HumanBodyWeb/static/viewer/scene/save_load.js',
                 'HumanBodyWeb/static/viewer/scene/character.js'],
     'hinweis': ('gatherSceneState sammelt, loadSceneFromData baut auf — dasselbe '
                 'Veralterungsrisiko wie beim Studio-Projekt. Dazu Datei-Auswahl ueber '
                 'die '
                 'Dateisystem-API des Browsers (_saveJsonWithPicker) mit Rueckfall auf '
                 'einen '
                 'Download-Link, und das Anlegen von Charakteren.'),
     'fragen': [
         ('Feld fuer Feld: Was sammelt gatherSceneState, das loadSceneFromData nicht '
             'wiederherstellt?'),
         ('_saveJsonWithPicker: Was passiert, wenn der Nutzer den Dialog abbricht, und '
             'was, wenn die API fehlt (Firefox)? Wird der Rueckfall-Link je '
             'aufgeraeumt?'),
         ('resetScene/newScene: Was bleibt von der alten Szene im Speicher und in der '
             'Renderschleife?'),
     ]},
    {'slug': 'viewer_editors', 'name': 'Viewer: Schnittmuster- und Vertex-Editor',
     'dateien': ['HumanBodyWeb/static/viewer/viewer/pattern_editor.js',
                 'HumanBodyWeb/static/viewer/viewer/vertex_editor.js'],
     'hinweis': ('Zwei Werkzeuge, die direkt auf Geometrie schreiben. Der '
                 'Schnittmuster-Editor '
                 'zeichnet auf ein 2D-Canvas mit eigener Umrechnung Welt<->Canvas '
                 '(peWorldToCanvas/peCanvasToWorld, Zeilen 37/38) und Treffertests mit '
                 'Schwellen in Pixeln. Der Vertex-Editor verschiebt Vertices am '
                 '3D-Netz. Beide '
                 'Male gilt: Wenn Hin- und Rueckrechnung nicht zueinander passen, '
                 'greift man '
                 'neben den Punkt — und bei Zoom faellt das zuerst auf.'),
     'fragen': [
         ('Sind peWorldToCanvas und peCanvasToWorld exakt invers? Pruefe die '
          'Vorzeichen '
             'von y und die Rolle von peZoom in den Treffertests.'),
         ('Treffertest-Schwellen in Pixeln bei starkem Zoom: Wann wird der falsche '
             'Punkt oder gar keiner getroffen?'),
         ('Vertex-Editor: Wird nach dem Verschieben alles aktualisiert, was von der '
             'Geometrie abhaengt (Normalen, Begrenzungskugel, Skinning)?'),
     ]},
]
