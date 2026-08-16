# -*- coding: utf-8 -*-
"""Codebereiche fuer Hilfe -> Review.

Aus ui/settings.py herausgeloest (Umbau 15.08.2026): 953 der 1364 Zeilen
dieser Datei waren Bereichsbeschreibungen mit Hinweisen und Fragen. Die
Einstellungsdatei beschreibt, wie der Server laeuft — nicht, welche 40
Codebereiche man mit einem zweiten Modell besprechen kann.

Die Pfade sind relativ zu DJANGOBASE["review_wurzel"] (dem Arbeitsverzeichnis);
ein Bereich darf mit "wurzel" eine eigene angeben (djangoBase liegt daneben).
"""
REVIEW_BEREICHE = [
    {'slug': 'retarget', 'name': 'Retarget-Mathematik',
     'dateien': ['HumanBody/humanbody_core/skeleton/retarget.py'],
     'hinweis': (
         'BVH-Animationen werden auf das DEF-Skelett (Rigify, 176 Knochen) '
         'übertragen. Quaternionen [w,x,y,z] in NumPy, Y ist oben. Zwei '
         'Betriebsarten: Standard (desiredWorldQ = bvhWeltQ x offsetQ) und '
         'Delta (Frame-0-Drehung abziehen, für AIST/Bandai/SMPL). '
         'Richtungskorrektur richtet BVH-Knochenrichtungen an DEF-Richtungen '
         'aus. Füße und Hals überspringen sie, weil die Topologien nicht '
         'zusammenpassen. Fehler hier sehen im Bild nach „unsauberer '
         'Animation" aus, nicht nach einem Fehler.'),
     'fragen': [
         'Wo kippt die Quaternionen-Kette, ohne dass es auffällt? Achte auf '
         'Vorzeichen, Reihenfolge der Multiplikation und den doppelten '
         'Überzug (q und -q sind dieselbe Drehung).',
         'parse_bvh: Welche gültige BVH-Datei wird falsch gelesen? '
         '(Kanal-Reihenfolge, Euler-Konvention, End Sites, Frame-Zeit)',
         'Die Höhenskalierung nimmt die Ausdehnung in Y aus Frame 0. Wann '
         'ist das falsch?',
         'Was passiert bei Knochen, die in der Zuordnung fehlen?',
     ]},
    {'slug': 'geometrie', 'name': 'Geometrie & Unterteilung',
     'dateien': ['HumanBody/humanbody_core/catmull_clark.py'],
     'hinweis': (
         'Catmull-Clark-Unterteilung des Körpernetzes (18k Basis-Vertices → '
         '70k). WICHTIG: Blenders ausgewertetes Netz hat eine ANDERE '
         'Vertex-Reihenfolge als diese Implementierung — Skin-Weights werden '
         'deshalb auf dem Basisnetz exportiert und hier durchgereicht. Eine '
         'Abweichung in der Reihenfolge zerstört die Gewichte, fällt in der '
         'Ruhepose aber nicht auf (dort sind alle Knochenmatrizen die '
         'Einheitsmatrix).'),
     'fragen': [
         'Wo weicht diese Implementierung von der Catmull-Clark-Definition '
         'ab (Randkanten, Ecken, Nicht-Vierecke, Vertices mit Valenz 3)?',
         'Ist die Reihenfolge der erzeugten Vertices deterministisch — auch '
         'bei anderer Reihenfolge der Eingabeflächen?',
         'Wo ist die Laufzeit quadratisch, wo werden Kanten doppelt gesucht?',
     ]},
    {'slug': 'morph', 'name': 'Morph-System',
     'dateien': ['HumanBody/humanbody_core/morphing.py',
                 'HumanBody/humanbody_core/character.py'],
     'hinweis': (
         'Morph-Ziele (.npy) verformen das Basisnetz über Regler. '
         'Voll-Morphs betreffen alle Vertices, Teil-Morphs nur einen Index-'
         'Ausschnitt. MinMax-Morphs mischen zwei Richtungen um eine Mitte. '
         'Die .npy-Dateien sind unersetzliche Produktivdaten.'),
     'fragen': [
         'Wo kann ein Regler die Basis-Vertices dauerhaft verändern statt '
         'eine Kopie zu verformen? (In-place-Addition, geteilte Arrays)',
         'Was passiert bei Reglerwerten ausserhalb des Bereichs, bei NaN, '
         'bei float32 gegen float64?',
         'Ist die Reihenfolge der angewandten Morphs bedeutsam — und ist sie '
         'stabil?',
     ]},
    # ----- zweite Runde, 13.08.2026: andere Bereiche ------------------
    {'slug': 'stoff', 'name': 'Stoff- und Kleidungsgeometrie',
     'dateien': ['HumanBody/humanbody_core/cloth.py'],
     'hinweis': (
         'Erzeugt Kleidungsnetze aus dem Körpernetz: Ringe um den Körper '
         'messen, Ringe zu Flächen verbrücken, doppelte Vertices verschmelzen '
         '(Union-Find), Laplace-glätten, aus dem Körper herausdrücken. Alles '
         'reine NumPy-Geometrie ohne Physik. Y ist oben, Maße in Metern, '
         'Vierecke (Quads) als Flächen. Fehler zeigen sich als Löcher, '
         'umgeklappte Normalen oder Kleidung, die im Körper steckt — nicht '
         'als Absturz.'),
     'fragen': [
         '_remove_doubles nutzt Union-Find mit einem Abstand von 8 mm. Wo '
         'verschmilzt es Vertices, die getrennt bleiben müssten, und wo '
         'hängt das von der Reihenfolge der Eingabe ab?',
         '_laplacian_smooth: Was passiert an Rändern und an Vertices ohne '
         'Nachbarn? Wird über die Iterationen der ursprüngliche oder der '
         'schon geglättete Stand gelesen — und ist das gewollt?',
         '_push_outside_body prüft gegen Körper-Vertices. Wann drückt es in '
         'den Körper hinein statt heraus (dünne Stellen, Achseln, zwischen '
         'den Beinen)?',
         '_compute_normals: Wo kann die Orientierung umklappen, ohne dass es '
         'in der Ruhelage auffällt?',
     ]},
    {'slug': 'pose', 'name': 'Pose-System und Koordinaten-Umrechnung',
     'dateien': ['HumanBody/humanbody_core/pose/pose_data.py',
                 'HumanBody/humanbody_core/coordinates.py'],
     'hinweis': (
         'Lädt Posen aus CharMorph und MB-Lab (JSON: '
         '{Kontrollknochen: [w,x,y,z]}) und rechnet sie auf das DEF-Skelett '
         'um. Drei Konventionen treffen aufeinander: Blender [w,x,y,z] mit Z '
         'oben, Three.js [x,y,z,w] mit Y oben, und die DEF-Knochen mit eigenen '
         'lokalen Achsen. Bekannte Grenze: Ruheposen (T-Pose) sitzen, komplexe '
         'Posen zeigen Rig/Netz-Versatz, weil CharMorph/MB-Lab andere lokale '
         'Knochenachsen benutzen als Rigify.\n'
         'ACHTUNG, KORREKTUR (13.08.2026): Ein früherer Hinweis hier nannte '
         'einen "leg_multiplier=2.5". Den gibt es im Code NICHT (mehr) — die '
         'Notiz stammte aus einer veralteten Projektaufzeichnung. Ein '
         'Hinweistext, der Code beschreibt, den es nicht gibt, erzeugt '
         'Befunde zu Code, den es nicht gibt.'),
     'fragen': [
         'to_threejs bildet [w,x,y,z] auf [x,z,-y,w] ab. Ist diese Abbildung '
         'für eine DREHUNG korrekt, oder nur für einen Punkt? Prüfe an einer '
         'konkreten Drehung um 90 Grad, und achte auf die Händigkeit.',
         'Wo wird ein Faktor auf eine Quaternion angewandt, statt auf einen '
         'Winkel (leg_multiplier)? Was ist daran mathematisch falsch, und '
         'wann fällt es nicht auf?',
         'Was passiert mit Kontrollknochen, die in CONTROL_TO_DEF fehlen, und '
         'mit Posen, die nur einen Teil der Knochen setzen?',
     ]},
    {'slug': 'skelett', 'name': 'Skelett-Klasse und IK',
     'dateien': ['HumanBody/humanbody_core/skeleton/skeleton.py',
                 'HumanBody/humanbody_core/skeleton/skeleton_geometry.py'],
     'hinweis': (
         'Vorgeschichte, die du wissen musst: In dieser Datei standen ~300 '
         'Zeilen der Klasse monatelang UNERREICHBAR, weil eine nicht '
         'eingerückte Funktion mitten in der Klasse den Klassenkörper beendet '
         'hat. Python meldet das nicht. Repariert am 12.08.2026 mit einem '
         'Golden-Master-Vergleich (Retarget-Ausgabe vorher/nachher identisch). '
         'Genau diese Sorte Fehler suche ich hier: Code, der aussieht als '
         'liefe er, und es nicht tut.'),
     'fragen': [
         'Gibt es weitere Stellen, die nie ausgeführt werden — unerreichbare '
         'Zweige, Methoden die von niemandem gerufen werden, Rückgaben nach '
         'einem return?',
         'Die IK fängt jetzt KeyError statt allem. Welcher Fehler wird dadurch '
         'sichtbar, den vorher der nackte except geschluckt hat — und ist die '
         'Behandlung danach richtig?',
         'Wo wird ein veränderbarer Zustand über Aufrufe hinweg gehalten, der '
         'zwischen zwei Skeletten geteilt werden kann?',
     ]},
    {'slug': 'frontend', 'name': 'Frontend: Szene-Zustand und Retarget-Brücke',
     'dateien': ['HumanBodyWeb/static/viewer/scene_state.js',
                 'HumanBodyWeb/static/viewer/retarget_hybrid.js'],
     'hinweis': (
         'ES-Module ohne Bundler, Three.js über Import-Maps. scene_state.js '
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
    # ----- dritte Runde, 13.08.2026 -----------------------------------
    {'slug': 'warp', 'name': 'Stoffsimulation (Warp, GPU)',
     'dateien': ['HumanBody/collision/warp_sim.py',
                 'HumanBody/collision/warp_only.py'],
     'hinweis': (
         'Läuft als eigener Prozess in Python 3.10 (warp-lang 1.4.2, letzte '
         'Fassung mit warp.sim) und wird von Django (3.14) gestartet. Simuliert '
         'Kleidung auf dem Körper: Partikel mit Federn, Kollision gegen das '
         'Körpernetz, Zeitschritte mit Unterschritten. Maße in Metern, Y ist '
         'oben, ein Zeitschritt ist typisch 1/30 s mit mehreren Unterschritten. '
         'Fehler zeigen sich als explodierendes Netz, durchfallender Stoff oder '
         'als Simulation, die scheinbar läuft und nichts bewegt.'),
     'fragen': [
         'Wo hängt das Ergebnis von der Schrittweite ab, ohne dass es soll — '
         'und welche Kombination aus Zeitschritt, Unterschritten und '
         'Federsteifigkeit lässt es explodieren?',
         'Kollision: Wird gegen Dreiecke oder nur gegen Vertices geprüft? Was '
         'passiert bei schnellen Bewegungen (Durchtunneln)?',
         'Was passiert, wenn die Grafikkarte den Speicher nicht hergibt oder '
         'Warp fehlt — bricht es ab oder liefert es stillschweigend die '
         'Eingabe zurück?',
         'Welche Einheiten werden gemischt (Meter/Zentimeter, Sekunden/Frames)?',
     ]},
    {'slug': 'zuordnung', 'name': 'Formaterkennung und Knochen-Zuordnung',
     'dateien': ['HumanBody/humanbody_core/skeleton/formats.py',
                 'HumanBody/humanbody_core/skeleton/retarget_mappings.py',
                 'HumanBody/humanbody_core/skeleton/mapping.py'],
     'hinweis': (
         'Erkennt am Knochennamen, aus welcher Quelle eine BVH-Datei kommt '
         '(CMU, Mixamo, MocapNET, OpenPose, Bandai, SMPL, AIST) und wählt die '
         'passende Zuordnungstabelle BVH-Knochen → DEF-Knochen (Rigify, 176 '
         'Knochen). EIN falscher Tabelleneintrag oder eine Erkennung, die auf '
         'das falsche Format fällt, ruiniert die ganze Animation — sichtbar '
         'als „verdrehte Figur", nicht als Fehlermeldung. Genau deshalb dieser '
         'Bereich: Hier ist ein Fehler billig zu machen und teuer zu finden.'),
     'fragen': [
         'Die Formaterkennung arbeitet mit Namensmerkmalen. Welche echte '
         'BVH-Datei fällt auf das falsche Format, und was ist die '
         'Reihenfolge-Abhängigkeit der Prüfungen?',
         'Gibt es in den Tabellen doppelte Ziele (zwei BVH-Knochen auf '
         'denselben DEF-Knochen) oder Ziele, die es im DEF-Skelett nicht gibt? '
         'Nenne sie konkret, das ist prüfbar.',
         'Wo unterscheiden sich links/rechts-Suffixe zwischen den Formaten, und '
         'wo könnte eine Seite vertauscht sein?',
         'Was passiert, wenn kein Format erkannt wird?',
     ]},
    {'slug': 'lifting', 'name': 'Video-nach-BVH: 3D-Lifting (GVHMR)',
     'dateien': ['VideoToBVH/wrappers/gvhmr_lift.py'],
     'hinweis': (
         'Nimmt die Ausgabe von GVHMR (SMPL-Parameter je Frame, Weltkoordinaten '
         'aus einem Video) und schreibt daraus eine BVH-Datei. Zwei Dinge sind '
         'hier historisch schmerzhaft: Die Frame-0-Drehungen werden auf die '
         'Einheitsdrehung normalisiert (Delta), damit das Retarget damit '
         'umgehen kann — und die Konventionen (Y-oben gegen Z-oben, Grad gegen '
         'Radiant, Euler-Reihenfolge, Bildrate) müssen zwischen SMPL, GVHMR und '
         'BVH zusammenpassen. Ein Vorzeichen daneben und die Figur läuft '
         'rückwärts oder liegt.'),
     'fragen': [
         'Prüfe die Achsen- und Vorzeichen-Umrechnung Schritt für Schritt. Wo '
         'wird eine Drehung wie ein Punkt behandelt (oder umgekehrt)?',
         'Die Delta-Normalisierung auf Frame 0: Was passiert, wenn Frame 0 '
         'unbrauchbar ist (Person halb im Bild, Erkennung wackelt)?',
         'Bildrate und Frame-Zeit: Woher kommt der Wert, und was passiert bei '
         'variabler Bildrate im Video?',
         'Wurzel-Verschiebung: Wird sie skaliert, und passt die Einheit zum '
         'BVH-Kopf?',
     ]},
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
    # ----- vierte Runde, 13.08.2026 -----------------------------------
    # Ausschnitt aus der 6.400-Zeilen-Datei: die Kette, über die JEDE
    # Mesh-Anfrage läuft, plus die Modul-Zwischenspeicher darunter.
    {'slug': 'mesh_api', 'name': 'Mesh-Auslieferung und Zwischenspeicher',
     'dateien': [{'pfad': 'HumanBodyWeb/core/character_api.py',
                  'funktionen': ['_get_morph_data', '_get_char_defaults',
                                 '_get_mesh_data', '_get_cc_subdivider',
                                 '_get_base_skin_weights', '_get_base_skin_arrays',
                                 '_get_garment_library', '_generate_rig_hull',
                                 'character_mesh', 'character_cloth',
                                 'garment_fit', 'mh_proxy_fit']}],
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
    # ----- fünfte Runde, 13.08.2026 -----------------------------------
    {'slug': 'blender', 'name': 'Blender-Addon: Rig und Operatoren',
     'dateien': ['HumanBodyBlender/rig.py', 'HumanBodyBlender/operators.py'],
     'hinweis': (
         'Blender-5.0-Addon (bpy), das dieselbe Kern-Bibliothek benutzt wie die '
         'Webapp (`sys.path.insert` auf HumanBody/). Operatoren laufen im '
         'Blender-Hauptfaden; ein Fehler darin reisst im besten Fall den '
         'Aufruf ab, im schlechteren hinterlaesst er die Szene halb verändert — '
         'Blender kennt keine Transaktion. Wichtig zu wissen: KEIN Operator in '
         'diesen beiden Dateien hat eine `poll`-Methode (11 von 11 geprüft), '
         'die Knöpfe sind also immer klickbar, auch ohne passende Auswahl. '
         'Ich kann hier NICHT ausführen — es gibt kein bpy ausserhalb von '
         'Blender. Argumentiere aus dem Code, und sag es, wenn du etwas nur '
         'in Blender selbst entscheiden könntest.'),
     'fragen': [
         'Welcher Operator hinterlässt die Szene halb verändert, wenn er '
         'mittendrin scheitert? Nenne den Ablauf: was ist dann angelegt, was '
         'fehlt, und was passiert beim zweiten Klick darauf?',
         'Fehlendes `poll()`: Bei welchem Operator ist der Absturz bei falscher '
         'Auswahl (kein aktives Objekt, falscher Objekttyp, Objekt versteckt) am '
         'wahrscheinlichsten — und was wäre die richtige Bedingung?',
         'Wo wird der Zustand der Szene angefasst, ohne den Modus zu prüfen '
         '(Object/Edit/Pose)? Bewege-, Lösch- und Datenzugriffe verhalten sich '
         'je Modus verschieden.',
         'Wo werden Objekte, Meshes oder Armaturen erzeugt und bei einem Fehler '
         'nicht wieder entfernt (verwaiste Datenblöcke in der .blend-Datei)?',
     ]},
    {'slug': 'jobstate', 'name': 'Job-Zustandsmaschine (Start, Stopp, Aufräumen)',
     'dateien': [{'pfad': 'HumanBodyWeb/core/views.py',
                  'funktionen': ['job_status_api', '_monitor_pipeline_log',
                                 'start_processing', '_write_stop_flags',
                                 '_kill_by_pid_file', 'stop_processing',
                                 'api_stop_processing']},
                 {'pfad': 'HumanBodyWeb/core/models.py',
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
     'dateien': [{'pfad': 'HumanBodyWeb/core/character_api.py',
                  'funktionen': ['analyze_photo', '_compute_auto_alignment',
                                 'photo_silhouette_data', 'smplx_mesh',
                                 'smplx_texture', 'photo_save_projection']}],
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
    # ----- sechste Runde, 13.08.2026 ----------------------------------
    {'slug': 'blender_cloth', 'name': 'Blender-Addon: Kleidungsbau',
     'dateien': [{'pfad': 'HumanBodyBlender/cloth_builder.py',
                  'funktionen': ['_create_garment', '_add_cloth', '_add_pin',
                                 '_bmesh_body_ring', '_transfer_bone_weights',
                                 '_create_prim_puffer', '_create_tpl_pants',
                                 'HUMANBODY_OT_cloth_prim_create']},
                 'HumanBodyBlender/wardrobe.py'],
     'hinweis': (
         'Baut Kleidung im Blender-Addon: Ringe aus dem Körpernetz über bmesh '
         'abnehmen, daraus ein Kleidungsnetz erzeugen, Blenders Cloth-Modifier '
         'und Pin-Vertexgruppen anlegen, Knochengewichte vom Körper übertragen. '
         'bmesh muss von Hand freigegeben werden (`bm.free()`), sonst bleibt '
         'Speicher liegen; ein `bmesh.from_edit_mesh` darf nicht wie ein '
         '`bmesh.new` behandelt werden. Blender kennt keine Transaktion: Was '
         'ein Operator bis zum Fehler angelegt hat, bleibt in der Datei. '
         'Ich kann hier NICHT ausführen (kein bpy ausserhalb von Blender) — '
         'argumentiere aus dem Code.'),
     'fragen': [
         'bmesh: Wo fehlt ein `free()` auf einem Fehlerpfad, und wo wird ein '
         'Edit-Mesh-bmesh falsch behandelt?',
         'Pin-Gruppen und Gewichtsübertragung: Was passiert, wenn Körper und '
         'Kleidung unterschiedlich viele Vertices haben oder die Zuordnung '
         'leer ausfällt?',
         '_create_garment ist die längste Funktion. Welcher Zwischenzustand '
         'bleibt bei einem Fehler in ihrer Mitte in der Szene stehen?',
         'Wo wird ein Name für ein Objekt oder eine Vertexgruppe gebildet, der '
         'kollidieren kann — und was macht Blender dann daraus?',
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
    {'slug': 'video', 'name': 'Video-Ausgabe (Theatre, ffmpeg)',
     'dateien': [{'pfad': 'HumanBodyWeb/core/character_api.py',
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
    # ===== Runden 1-20 (13.08.2026): die verbleibenden Bereiche =====
    {'slug': 'blender_ui', 'name': 'Blender: Bedienfelder, Timer, Handler',
     'dateien': [{'pfad': 'HumanBodyBlender/ui.py', 'funktionen': ['HUMANBODY_OT_pick_part', '_deferred_mesh_update', '_on_depsgraph_update', 'register', 'unregister', '_draw_cloth_builder_body', '_draw_parts_body']}],
     'hinweis': ('Blender-Bedienfelder. Zwei Dinge laufen NEBEN der Bedienung: ein Timer (bpy.app.timers.register, entprellte Morph-Aktualisierung) und ein depsgraph_update_post-Handler; beide werden in register() angehaengt. Ein Handler, der bei jeder Szenenaenderung laeuft und selbst die Szene aendert, ruft sich wieder auf. Ein Timer, der beim Deaktivieren des Addons nicht abgemeldet wird, laeuft weiter und greift auf entfernte Klassen zu. Ich kann hier NICHT ausfuehren (kein bpy ausserhalb von Blender).'),
     'fragen': [
         'Wird der Timer beim Deaktivieren zuverlaessig abgemeldet? Was, wenn er feuert, nachdem das Objekt geloescht oder der Modus gewechselt wurde?',
         'Wo kann sich der depsgraph-Handler selbst ausloesen, und was kostet er bei jeder Mausbewegung?',
         'HUMANBODY_OT_pick_part ist die laengste Funktion — welcher Zwischenzustand bleibt bei einem Fehler darin stehen?',
     ]},
    {'slug': 'blender_anim', 'name': 'Blender: Animation und BVH-Import',
     'dateien': [{'pfad': 'HumanBodyBlender/animation.py', 'funktionen': ['HUMANBODY_OT_load_bvh_native', '_load_cached_action', '_cleanup_old_anim', 'HUMANBODY_OT_load_animation', '_gen_walk']}],
     'hinweis': ('Laedt BVH ueber Blenders eigenen Importer, legt Actions an, raeumt alte auf und erzeugt einfache Bewegungen rechnerisch. Actions und NLA-Streifen sind eigene Datenbloecke: Wer sie nicht loest, sammelt sie in der .blend-Datei. Ich kann hier NICHT ausfuehren.'),
     'fragen': [
         '_cleanup_old_anim: Was wird NICHT geloescht (Actions ohne Nutzer, NLA-Streifen, Fake-User)?',
         'Der Import laeuft ueber bpy.ops — was passiert bei einer Datei, die Blender nicht mag, und was bleibt dann in der Szene?',
         'Was, wenn die BVH-Frame-Zeit nicht zur Szenen-Bildrate passt?',
     ]},
    {'slug': 'blender_retarget', 'name': 'Blender: eigener Retargeter',
     'dateien': ['HumanBodyBlender/retarget.py'],
     'hinweis': ('Der DRITTE Retargeter im Projekt (neben humanbody_core/skeleton/retarget.py und der JS-Seite). Ordnet BVH-Knochen den DEF-Knochen zu und setzt Pose-Bone-Rotationen. In Blender sind Knochendrehungen lokal in der Elternachse; matrix_basis, matrix_channel und matrix_world sind verschiedene Dinge. Fehler sehen wie eine unsaubere Animation aus, nicht wie ein Fehler.'),
     'fragen': [
         'Wo wird eine Weltdrehung wie eine lokale behandelt (oder umgekehrt)?',
         'Wo weicht dieser Retargeter inhaltlich von der Python-Kernfassung ab — gleiche Zuordnung, gleiche Richtungskorrektur, gleicher Delta-Weg?',
         'Was passiert bei fehlenden Knochen und bei einer Armatur, die nicht im Pose-Modus ist?',
     ]},
    {'slug': 'blender_hair', 'name': 'Blender: Haare, Morphing, Charakteraufbau',
     'dateien': ['HumanBodyBlender/hair.py', 'HumanBodyBlender/morphing.py', 'HumanBodyBlender/human_body.py'],
     'hinweis': ('Haare als Partikel-/Kurvenobjekte, Morph-Anwendung im Addon, Aufbau des Charakters. morphing.py benutzt dieselbe Kern-Bibliothek wie die Webapp; dort ist bekannt, dass CharacterState.compute() einen INTERNEN Puffer zurueckgibt, der beim naechsten Aufruf ueberschrieben wird. Ich kann hier NICHT ausfuehren.'),
     'fragen': [
         'Wird das Ergebnis von compute() irgendwo festgehalten, obwohl es beim naechsten Aufruf ueberschrieben wird?',
         'Haare: Was bleibt liegen, wenn ein Haar-Objekt ersetzt wird?',
         'Wo werden Vertex-Zahlen von Basisnetz und unterteiltem Netz verwechselt?',
     ]},
    {'slug': 'fe_modelgen', 'name': 'Frontend: Modellgenerator',
     'dateien': ['HumanBodyWeb/static/viewer/model_generator.js'],
     'hinweis': ('Erzeugt aus dem Skelett ein Netz im Browser (Three.js, ES-Module, kein Bundler). Ersetzt Geometrien und Materialien bei jeder Aenderung; Three.js gibt Grafikspeicher nur bei dispose() frei. Bekannt aus einer frueheren Runde: Die Geometrie von state.bodyMesh wird an sechs Stellen freigegeben, Material und Texturen nicht.'),
     'fragen': [
         'Wo wird eine Geometrie, ein Material oder eine Textur ersetzt, ohne die alte freizugeben? Nenne die Stelle.',
         'Wo wird in einer Schleife pro Vertex ein neues Objekt erzeugt (Vector3, Matrix4) — und wie oft laeuft das?',
         'Was passiert bei zwei schnellen Aufrufen hintereinander?',
     ]},
    {'slug': 'fe_animations', 'name': 'Frontend: Animations-Bibliothek',
     'dateien': ['HumanBodyWeb/static/viewer/animations.js'],
     'hinweis': ('Die BVH-Bibliothek im Browser: Liste laden, Verwaltung (loeschen, umbenennen, verschieben), Abspielen ueber AnimationMixer. Enthaelt base64ToFloat32 — geprueft am 13.08.2026: Ausrichtung in Ordnung, eine falsche Byte-Anzahl faellt laut auf (RangeError). Das ist erledigt, suche anderes.'),
     'fragen': [
         'AnimationMixer und Clips: Was wird beim Wechsel der Animation nicht gestoppt oder nicht freigegeben?',
         'Die Verwaltungsaufrufe aendern die Liste — was, wenn die Antwort spaeter kommt als ein zweiter Klick?',
         'Wo wird eine Fehlerantwort des Servers stillschweigend als Erfolg behandelt?',
     ]},
    {'slug': 'fe_compare', 'name': 'Frontend: Vergleich und Skelett-Test',
     'dateien': ['HumanBodyWeb/static/viewer/viewer_compare.js', 'HumanBodyWeb/static/viewer/skeleton_test.js'],
     'hinweis': ('Zwei Seiten, die ZWEI Skelette bzw. Modelle gleichzeitig zeigen — doppelte Szenen, doppelte Renderer, doppelte Ressourcen. Genau dort schlagen fehlende dispose()-Aufrufe und doppelte requestAnimationFrame-Schleifen am haertesten zu.'),
     'fragen': [
         'Wie viele requestAnimationFrame-Schleifen laufen nach zwei Ladevorgaengen?',
         'Wo werden Renderer oder Szenen neu angelegt, ohne die alten abzubauen (renderer.dispose, forceContextLoss)?',
         'Der Vergleich laeuft ueber Knochennamen — wo laeuft er ins Leere, ohne dass es auffaellt?',
     ]},
    {'slug': 'fe_studio_tracks', 'name': 'Frontend: BVH-Studio Spuren',
     'dateien': ['HumanBodyWeb/static/viewer/bvh_studio/tracks.js'],
     'hinweis': ('Verwaltet die Spuren des BVH-Studios: Ausschnitte, Verschiebungen, Ueberblendungen. Rechnet mit Frame-Indizes UND Sekunden; die Bildrate steckt in den Daten. Fehler zeigen sich als ruckelnde oder um Frames verschobene Wiedergabe.'),
     'fragen': [
         'Wo werden Frames und Sekunden vermischt, und wo wird gerundet statt abgeschnitten (oder umgekehrt)?',
         'Was passiert am Rand: erster Frame, letzter Frame, Ausschnitt der Laenge 0, Ueberblendung laenger als der Ausschnitt?',
         'Wo wird eine Spur veraendert, waehrend die Wiedergabe laeuft?',
     ]},
    {'slug': 'vtb_detect', 'name': 'VideoToBVH: 2D-Erkennung und Lifting-Wrapper',
     'dateien': ['VideoToBVH/wrappers/detect_2d.py', 'VideoToBVH/wrappers/yolo_det.py', 'VideoToBVH/wrappers/wham_lift.py'],
     'hinweis': ('Diese Skripte laufen als Subprozess in Python 3.10 und schreiben ihren Fortschritt auf stdout, den Django zeilenweise liest (TOTAL:/STATUS:). Sie erwarten Modellgewichte auf der Platte. Seit 13.08.2026 gilt: Bleibt die Ausgabe zu lange aus, beendet die aufrufende Seite den Prozess.'),
     'fragen': [
         'Fortschrittsausgabe: Wird sie zuverlaessig geleert (flush), und gibt es Phasen, in denen minutenlang nichts kommt?',
         'Was passiert bei einem Video ohne erkannte Person, bei einem Frame ohne Erkennung, und bei mehreren Personen?',
         'Kann das Skript mit Rueckgabewert 0 enden, ohne eine brauchbare Ausgabe geschrieben zu haben?',
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
    {'slug': 'hb_mesh', 'name': 'Kern: Netzdaten, Voreinstellungen, Gesichts-Blendshapes',
     'dateien': ['HumanBody/humanbody_core/mesh.py', 'HumanBody/humanbody_core/skeleton/presets.py', 'HumanBody/humanbody_core/skeleton/face_blendshapes.py'],
     'hinweis': ('mesh.py laedt das Basisnetz (Vertices, Vierecke, UVs, Material-Gruppen) aus .npy/.npz — unersetzliche Produktivdaten, read-only zu behandeln. presets.py haelt Skelett-Voreinstellungen, face_blendshapes bildet Gesichtsausdruecke auf Knochen ab.'),
     'fragen': [
         'Wo wird ein geladenes Array veraendert oder ohne Schreibschutz weitergegeben?',
         'Was passiert bei einer fehlenden oder halb geschriebenen Datendatei — klare Meldung oder spaeterer Folgefehler?',
         'Werden Datentyp und Form der geladenen Daten geprueft, bevor damit gerechnet wird?',
     ]},
    {'slug': 'web_models', 'name': 'Web: Datenmodell und Einstellungen',
     'dateien': ['HumanBodyWeb/core/models.py'],
     'hinweis': ('Die Django-Modelle: BVHJob (Auftraege mit Zustand und Fortschritt), BVHFile (Bibliothek mit Pfad und Zeitstempel), PhotoAnalysisJob, AppSettings (ein Singleton mit ui_prefs als JSON). Datenbank ist SQLite und bei gleichzeitigen Schreibvorgaengen empfindlich ("database is locked"). AppSettings wird von der Pfadpruefung SafePath gelesen, also in jedem Datei-Endpunkt.'),
     'fragen': [
         'AppSettings.load(): Was passiert bei zwei gleichzeitigen Aufrufen, wenn die Zeile noch nicht existiert?',
         'ui_prefs als JSON-Feld: Wo wird gelesen-geaendert-geschrieben, und was geht dabei verloren?',
         'BVHFile.path ist eindeutig — was beim Umbenennen einer Datei auf der Platte, was beim Wiedereinlesen?',
         'Welche Felder haben keine Begrenzung, obwohl sie aus Anfragedaten gefuellt werden?',
     ]},
    {'slug': 'api_bvh', 'name': 'API: BVH-Bibliothek und Studio-Bearbeitung',
     'dateien': [{'pfad': 'HumanBodyWeb/core/character_api.py', 'funktionen': ['bvh_manage', 'smooth_bvh', 'save_bvh_effects', 'retarget_bvh_text', 'studio_project_save', 'studio_project_load', 'studio_project_list']}],
     'hinweis': ('Verwaltung und Bearbeitung der BVH-Bibliothek. ERLEDIGT und nicht nochmal zu melden: Pfadpruefung ueber SafePath, unteilbares Schreiben ueber AtomarSchreiber, Ursprungs- und Methodenpruefung fuer schreibende Anfragen. Suche die BEARBEITUNG selbst: Glaetten, Effekte, Textumwandlung.'),
     'fragen': [
         'smooth_bvh und save_bvh_effects rechnen auf Bewegungsdaten. Wo kippt das Ergebnis (Fenster groesser als die Animation, erste/letzte Frames, Quaternionen komponentenweise geglaettet)?',
         'Wird beim Glaetten ueber Quaternionen komponentenweise gemittelt? Was macht das mit der Drehung?',
         'Was passiert mit Bildrate und Kopf der BVH-Datei beim Zurueckschreiben?',
     ]},
    {'slug': 'api_pattern', 'name': 'API: Schnittmuster-Editor',
     'dateien': [{'pfad': 'HumanBodyWeb/core/character_api.py', 'funktionen': ['pattern_generate', 'pattern_save', 'pattern_specification', 'pattern_region_generate', '_laplacian_smooth_garment', 'vertex_edit_smooth']}],
     'hinweis': ('Aus 2D-Umrissen (Bezier-Kanten) werden Kleidungsteile im Raum platziert und zu einem Netz verbunden. Reine Geometrie, viel NumPy. Fehler zeigen sich als Loecher, umgeklappte Flaechen oder Teile an der falschen Stelle.'),
     'fragen': [
         'Wo wird ein 2D-Umriss als geschlossen angenommen, ohne es zu pruefen?',
         'Selbstueberschneidende oder entartete Umrisse (drei Punkte auf einer Linie, doppelte Punkte): Was passiert?',
         'Die Platzierung im Raum: Woran haengt die Orientierung, und wann zeigt ein Teil nach innen?',
     ]},
    {'slug': 'api_smpl', 'name': 'API: SMPL-Koerper und Kleidungsbibliothek',
     'dateien': [{'pfad': 'HumanBodyWeb/core/character_api.py', 'funktionen': ['smpl_body_mesh', 'smpl_garment_mesh', 'smpl_garment_fit', 'smpl_garment_thumbnail', 'garment_library', 'garment_library_rescan', 'smpl_settings_save']}],
     'hinweis': ('SMPL-Koerper aus Formparametern (betas) erzeugen und Kleidung anpassen; dazu eine Bibliothek, die das Dateisystem durchsucht. BEKANNT UND ERLEDIGT, nicht nochmal melden: SMPL (6890 Vertices) und SMPL-X (10475) haben unvereinbare Topologien, der Code faengt das ueber einen Laengenvergleich ab.'),
     'fragen': [
         'garment_library_rescan durchsucht das Dateisystem — wie lange dauert das, blockiert es die Anfrage, und was bei einem tiefen oder verknuepften Verzeichnis?',
         'betas: Werden Anzahl und Wertebereich geprueft, bevor gerechnet wird?',
         'Vorschaubilder: Wo erzeugt, wo abgelegt, wann veraltet?',
     ]},
    {'slug': 'views_serve', 'name': 'Web: Auslieferung von Dateien und Overlays',
     'dateien': [{'pfad': 'HumanBodyWeb/core/views.py', 'funktionen': ['serve_bvh_file', 'serve_bvh_face', 'video_thumbnail', 'video_thumbnail', 'serve_detection_data', 'save_rig_video', 'save_overlay_video']}],
     'hinweis': ('Liefert Ergebnisdateien eines Auftrags aus (BVH, Video, Vorschaubild, Erkennungsdaten) und zeichnet Skelett-Overlays. Die Pfade entstehen aus der Auftrags-Kennung; Pfade aus Anfragedaten gehen sonst durch SafePath. Vorschaubilder und Overlays werden gecacht.'),
     'fragen': [
         'Kann eine Anfrage eine Datei ausliefern, die nicht zu ihrem Auftrag gehoert? Wie wird der Pfad gebildet?',
         'Cache der Vorschaubilder: Woran wird erkannt, dass er veraltet ist?',
         'Werden grosse Dateien gestreamt oder in den Speicher geladen? Was, wenn die Datei mitten im Ausliefern ersetzt wird?',
     ]},
    {'slug': 'views_pipelines', 'name': 'Web: Pipeline-Laeufe und Fortschritt',
     'dateien': [{'pfad': 'HumanBodyWeb/core/views.py', 'funktionen': ['_run_mediapipe_to_csv', '_run_openpose_to_csv', '_run_new_2d_detector', '_run_v4_pipeline']}],
     'hinweis': ('Die vier Pipeline-Laeufe. Sie starten Subprozesse ueber PipelineProzess (Zeichensatz, stderr, Stille-Timeout sind dort seit 12./13.08.2026 geloest — NICHT nochmal melden) und deuten deren Ausgabe: TOTAL:, STATUS:, Frame-Zaehler. Hier geht es um DIESE Deutung und um den Fortschritt in der Datenbank.'),
     'fragen': [
         'Welche Ausgabe faehrt den Fortschrittszaehler falsch (mehrere TOTAL-Zeilen, Zahlen im Dateinamen, Fortschritt rueckwaerts)?',
         'Wie oft wird job.save() gerufen — was kostet das bei 20.000 Frames?',
         'Was passiert, wenn die erwartete Ausgabedatei fehlt, der Rueckgabewert aber 0 ist?',
     ]},
    {'slug': 'web_infra', 'name': 'Web: Einstellungen, Middleware, ASGI',
     'dateien': ['HumanBodyWeb/ui/settings.py', 'HumanBodyWeb/ui/no_cache.py', 'HumanBodyWeb/ui/same_origin.py', 'HumanBodyWeb/ui/asgi.py'],
     'hinweis': ('Grundeinstellungen und drei Middleware-Schichten. Bekannt und gewollt: DEBUG=True, keine Anmeldung, ALLOWED_HOSTS nur localhost, DATA_UPLOAD_MAX_MEMORY_SIZE 500 MB (ganze Bildfolgen in einer Anfrage), NoCache auf ALLEN Antworten (Absicht: kein Browser-Cache), Ursprungspruefung fuer schreibende Methoden (neu am 13.08.2026). Einzelplatz-Entwicklungssystem, kein Produktivbetrieb — bewerte danach.'),
     'fragen': [
         'Die Ursprungspruefung: Welcher Browser-Ablauf kommt trotzdem durch, welcher legitime wird faelschlich abgewiesen?',
         'NoCache auf allen Antworten: Wo schadet das (Grafiken, Vorschaubilder, grosse Dateien), und was kostet es?',
         'Wo widersprechen sich Einstellungen (Zeichensatz, Zeitzone, Sprachcode, MEDIA-/STATIC-Wurzeln)?',
         'Was ist hier gefaehrlich, WENN das System eines Tages nicht mehr nur lokal laeuft?',
     ]},
    {'slug': 'coll_bridge', 'name': 'Kollision: Brücke vom Browser zur Pipeline',
     'dateien': ['HumanBody/collision/bridge.py', 'HumanBody/collision/scene_input.py'],
     'hinweis': ('Der Browser schickt eine ganze Szene als JSON: Netze base64-kodiert '
                 '(Float32/Uint32), Skelett-Matrizen, Animationsspuren, Kleidungsteile. '
                 'bridge.payload_to_scene_input baut daraus SceneInput; das wird als .npz '
                 'gespeichert und von einem Python-3.10-Unterprozess wieder geladen. Alles '
                 'hier kommt aus einer HTTP-Anfrage. Ich kann diesen Code ausfuehren (NumPy '
                 'vorhanden) und Messungen machen.'),
     'fragen': [
         ('Welche Eingabe laesst _b64_to_f32 oder _b64_to_u32 abstuerzen oder '
             'stillschweigend Unsinn liefern (Laenge kein Vielfaches von 4, falsches '
             'base64, leerer String)? Ich pruefe das nach.'),
         ('Wo werden Feldlaengen NICHT gegeneinander geprueft (Vertexzahl gegen '
             'Gewichte, Knochenzahl gegen Matrizen, Framezahl gegen Spuren)?'),
         ('save_npz: Was passiert bei ungleich langen Spuren, und was liest der '
             'Unterprozess dann?'),
     ]},
    {'slug': 'coll_splitter', 'name': 'Kollision: Szene aufteilen, Ton anhängen',
     'dateien': ['HumanBody/collision/splitter.py', 'HumanBody/collision/audio_mux.py'],
     'hinweis': ('splitter.split_scene trennt die Szene in Koerper und Stoff und bestimmt die '
                 'Pins (die festgehaltenen Stoffpunkte). audio_mux.mux_audio ruft ffmpeg auf, '
                 'um Tonspuren unter das gerenderte Video zu legen; _resolve_url macht aus '
                 'einer URL aus dem Browser einen Pfad auf der Platte. Ausfuehrbar.'),
     'fragen': [
         ('_resolve_url: Welche URL fuehrt aus dem Medienverzeichnis heraus? Nenne die '
             'Zeichenkette, ich probiere sie aus.'),
         ('compute_pin_group: Was, wenn keine Pins gefunden werden oder alle Punkte '
             'Pins sind — merkt das jemand, oder simuliert die GPU dann Unsinn?'),
         ('mux_audio ruft ffmpeg mit Werten aus dem Browser auf. Wo landet etwas in '
             'einer Kommandozeile, das dort nicht hingehoert?'),
     ]},
    {'slug': 'coll_skinning', 'name': 'Kollision: rigides Skinning und Body-Push-Out',
     'dateien': ['HumanBody/collision/skinning_only.py', 'HumanBody/collision/skinning_blender.py'],
     'hinweis': ('Die schnellste der vier Pipelines: keine Stoffsimulation, sondern der Stoff '
                 'wird mitbewegt (rigid skinning) und danach aus dem Koerper geschoben '
                 '(_push_outside_body). Die Kernrechnung ist reines NumPy und laeuft je Frame '
                 'ueber alle Vertices. Ausfuehrbar und MESSBAR — nenne Groessen, ich messe.'),
     'fragen': [
         ('_skin_rigid_frame: Ist die Reihenfolge inv_bind mal frame_mat richtig, oder '
             'ist sie vertauscht? Woran wuerde man es im Bild sehen?'),
         ('_push_outside_body arbeitet mit Normalen des Koerpers und einer Marge. In '
             'welcher Lage schiebt das den Stoff IN den Koerper statt heraus?'),
         ('Wo ist die Schleife unnoetig quadratisch, und was kostet das bei 70.000 '
             'Vertices und 300 Frames?'),
     ]},
    {'slug': 'coll_render', 'name': 'Kollision: Bilder rendern (pyrender und Blender)',
     'dateien': ['HumanBody/collision/warp_render.py', 'HumanBody/collision/blender_render_from_bake.py'],
     'hinweis': ('Zwei Renderwege aus derselben Bake-Datei: pyrender offscreen (Python 3.14) '
                 'und Blender im Hintergrund. Beide bauen Kamera und Licht aus derselben '
                 'Nutzlast, und beide rechnen zwischen Y-oben (Three.js) und Z-oben (Blender) '
                 'um. Zwei Wege, dieselbe Kamera — wenn die Umrechnung an einer Stelle anders '
                 'ist, sehen die Videos verschieden aus. warp_render ist ausfuehrbar.'),
     'fragen': [
         ('Vergleiche _pose_from_camera_matrix (pyrender) mit _yup_to_zup_mat44 und '
             'setup_camera_from_payload (Blender): Wo weichen sie inhaltlich ab?'),
         ('_fit_camera bei entarteten Eingaben (ein Punkt, NaN, leere Liste) — was '
             'kommt heraus?'),
         ('mux_ffmpeg und render_bake: Was bleibt liegen, wenn der Aufruf mitten drin '
             'abbricht (Frames, Prozesse, Speicher)?'),
     ]},
    {'slug': 'studio_timeline', 'name': 'BVH-Studio: Zeitleiste (Zeichnen und Maus)',
     'dateien': ['HumanBodyWeb/static/viewer/bvh_studio/timeline.js'],
     'hinweis': ('1.176 Zeilen: zeichnet Spuren, Clips, Schlüsselbilder auf ein Canvas und '
                 'behandelt Ziehen, Zuschneiden, Auswahl. renderTimeline laeuft bei jeder '
                 'Mausbewegung. Die Zeilen 21-56 rechnen zwischen Zeile-auf-dem-Schirm und '
                 'Spur-im-Modell um; wenn diese Umrechnung und das Zeichnen verschiedene '
                 'Annahmen haben, greift man neben den Clip. Ich kann im Browser messen '
                 '(Chrome-Fernsteuerung) und die Seite bedienen.'),
     'fragen': [
         ('_rowAtY und _rowYForTrackIdx sind Hin- und Rueckrechnung. Sind sie '
             'zueinander invers, auch bei zusammengeklappten Spuren und beim Scrollen?'),
         ('Wo werden in renderTimeline Objekte je Bild neu angelegt, die man einmal '
             'anlegen koennte — und wie viele sind es bei 30 Spuren?'),
         'Welche Ereignis-Zuhoerer werden angemeldet, aber nie abgemeldet?',
     ]},
    {'slug': 'studio_props', 'name': 'BVH-Studio: Eigenschaften-Bedienfeld',
     'dateien': ['HumanBodyWeb/static/viewer/bvh_studio/properties.js'],
     'hinweis': ('updateProperties (Zeile 54) ist eine einzige Funktion von ueber 700 Zeilen: '
                 'Sie baut das rechte Bedienfeld je nach ausgewaehlter Spur neu auf — Lichter, '
                 'Kameras, Charaktere, Boden. _changeLightType tauscht den Lichttyp im Modell '
                 'UND in der Szene. Solche Funktionen halten Zustand doppelt: im Modell und im '
                 'DOM.'),
     'fragen': [
         ('Wo wird im DOM etwas gesetzt, ohne dass das Modell mitgeht (oder umgekehrt) '
             '— also nach welcher Bedienung zeigt das Feld etwas anderes als die Szene?'),
         ('_changeLightType: Was bleibt von der alten Lichtquelle uebrig (Objekt in der '
             'Szene, Hilfsobjekt, Schattenkarte)?'),
         ('Wie oft wird updateProperties bei einer Auswahl gerufen, und was kostet der '
             'Neuaufbau des ganzen Bedienfelds?'),
     ]},
    {'slug': 'studio_tools', 'name': 'BVH-Studio: Werkzeuge (Glättung, Bodenfix)',
     'dateien': ['HumanBodyWeb/static/viewer/bvh_studio/tools.js'],
     'hinweis': ('Die Werkzeugleiste: Gauss-Glaettung ueber alle Clips, feste Position, '
                 'Bodenfix. _gaussSmooth.origClips haelt die Originaldaten in einer Map, damit '
                 'man die Glaettung zurueckdrehen kann — der Schluessel ist '
                 '`trackIdx_clipIdx`. Beim Verschieben oder Loeschen von Spuren aendern sich '
                 'diese Indizes. _gaussFilter glaettet Quaternion-Komponenten einzeln und '
                 'normiert danach; das ist eine Annaeherung, aber eine bekannte.'),
     'fragen': [
         ('origClips-Schluessel aus Indizes: Welche Bedienreihenfolge (Spur loeschen, '
             'verschieben, Clip einfuegen) macht die Wiederherstellung falsch?'),
         ('_gaussFilter am Rand des Fensters und bei stride-Werten, die nicht passen — '
             'was passiert bei einem Clip mit zwei Frames?'),
         ('applyGaussToAllClips und reloadAllClipAnimations: Wo wird doppelt geglaettet '
             'oder auf schon geglaetteten Daten weitergerechnet?'),
     ]},
    {'slug': 'studio_project', 'name': 'BVH-Studio: Projekt speichern, laden, wiederherstellen',
     'dateien': ['HumanBodyWeb/static/viewer/bvh_studio/project.js'],
     'hinweis': ('buildProjectData sammelt den Zustand, restoreProjectData baut ihn wieder '
                 'auf, saveSessionState/restoreSessionState machen dasselbe fuer localStorage. '
                 'Solche Paare veralten getrennt: Was neu gespeichert wird, wird beim Laden '
                 'vergessen — und umgekehrt. previewAnimation legt eine zweite Three.js-Szene '
                 'fuer die Vorschau an.'),
     'fragen': [
         ('Vergleiche buildProjectData mit restoreProjectData Feld fuer Feld: Was wird '
             'gespeichert, aber nie wiederhergestellt (oder umgekehrt)?'),
         ('previewAnimation/closePreview: Was wird nicht freigegeben (Renderer, '
             'Geometrien, Schleifen, Canvas)?'),
         ('Was passiert beim Laden eines Projekts aus einer aelteren Fassung — gibt es '
             'eine Fassungsnummer, und was macht ein fehlendes Feld?'),
     ]},
    {'slug': 'scene_mhproxy', 'name': 'Szene: MakeHuman-Proxy anpassen (Browser-Seite)',
     'dateien': ['HumanBodyWeb/static/viewer/scene/mh_proxy.js'],
     'hinweis': ('Die Browser-Seite des Proxy-Fits: Der Nutzer waehlt ein MH-Kleidungsstueck, '
                 'die Seite schickt es an /api/character/mh-proxy/fit/ und baut das Ergebnis '
                 'in die Szene. GEMESSEN am 13.08.2026: Der Serverteil rechnet 1,14 s IM '
                 'Anfrage-Faden. Interessant ist hier die Browser-Seite: Zustand in '
                 'localStorage (_saveMHState/_loadMHState), Kontextmenue, Liste, und ein Fit, '
                 'der laenger dauert als ein Klick.'),
     'fragen': [
         ('Was passiert bei zwei Klicks auf "Anpassen" hintereinander (Doppelklick, '
             'oder waehrend der erste Fit laeuft)? Gibt es eine Sperre, und wenn ja, wird '
             'sie bei einem Fehler wieder gelöst?'),
         ('_saveMHState/_loadMHState: Was, wenn localStorage voll ist, der Eintrag von '
             'einer aelteren Fassung stammt oder ungueltiges JSON enthaelt?'),
         ('Wird das alte Netz beim Ersetzen freigegeben (dispose), und welche '
             'Ereignis-Zuhoerer haengen nach dem Schliessen des Kontextmenues noch dran?'),
     ]},
    {'slug': 'scene_kleider', 'name': 'Szene: Kleidung anlegen und anpassen',
     'dateien': ['HumanBodyWeb/static/viewer/scene/kleider.js', 'HumanBodyWeb/static/viewer/scene/garments.js'],
     'hinweis': ('Zwei Wege fuer Kleidung in der Mehr-Charakter-Szene: _doKleiderStage1 '
                 '(grobes Anlegen) und _doKleiderFit (Anpassen an die Figur), dazu die Liste '
                 'und das Kontextmenue. Beide rufen den Server und tauschen Netze in der Szene '
                 'aus. Wiederholtes Anlegen/Anpassen ist der Normalfall der Bedienung.'),
     'fragen': [
         ('Was passiert, wenn Stufe 2 (Fit) ohne Stufe 1 gerufen wird oder Stufe 1 '
             'zweimal laeuft?'),
         ('Wo bleiben Geometrien, Materialien oder Texturen liegen, wenn ein '
             'Kleidungsstueck ersetzt oder entfernt wird?'),
         ('Die Liste wird bei jeder Aenderung neu gebaut (_renderKleiderList): Wo gehen '
             'dabei Zuhoerer oder Auswahlzustand verloren?'),
     ]},
    {'slug': 'scene_saveload', 'name': 'Szene: speichern, laden, Charaktere',
     'dateien': ['HumanBodyWeb/static/viewer/scene/save_load.js', 'HumanBodyWeb/static/viewer/scene/character.js'],
     'hinweis': ('gatherSceneState sammelt, loadSceneFromData baut auf — dasselbe '
                 'Veralterungsrisiko wie beim Studio-Projekt. Dazu Datei-Auswahl ueber die '
                 'Dateisystem-API des Browsers (_saveJsonWithPicker) mit Rueckfall auf einen '
                 'Download-Link, und das Anlegen von Charakteren.'),
     'fragen': [
         ('Feld fuer Feld: Was sammelt gatherSceneState, das loadSceneFromData nicht '
             'wiederherstellt?'),
         ('_saveJsonWithPicker: Was passiert, wenn der Nutzer den Dialog abbricht, und '
             'was, wenn die API fehlt (Firefox)? Wird der Rueckfall-Link je aufgeraeumt?'),
         ('resetScene/newScene: Was bleibt von der alten Szene im Speicher und in der '
             'Renderschleife?'),
     ]},
    {'slug': 'viewer_editors', 'name': 'Viewer: Schnittmuster- und Vertex-Editor',
     'dateien': ['HumanBodyWeb/static/viewer/viewer/pattern_editor.js', 'HumanBodyWeb/static/viewer/viewer/vertex_editor.js'],
     'hinweis': ('Zwei Werkzeuge, die direkt auf Geometrie schreiben. Der Schnittmuster-Editor '
                 'zeichnet auf ein 2D-Canvas mit eigener Umrechnung Welt<->Canvas '
                 '(peWorldToCanvas/peCanvasToWorld, Zeilen 37/38) und Treffertests mit '
                 'Schwellen in Pixeln. Der Vertex-Editor verschiebt Vertices am 3D-Netz. Beide '
                 'Male gilt: Wenn Hin- und Rueckrechnung nicht zueinander passen, greift man '
                 'neben den Punkt — und bei Zoom faellt das zuerst auf.'),
     'fragen': [
         ('Sind peWorldToCanvas und peCanvasToWorld exakt invers? Pruefe die Vorzeichen '
             'von y und die Rolle von peZoom in den Treffertests.'),
         ('Treffertest-Schwellen in Pixeln bei starkem Zoom: Wann wird der falsche '
             'Punkt oder gar keiner getroffen?'),
         ('Vertex-Editor: Wird nach dem Verschieben alles aktualisiert, was von der '
             'Geometrie abhaengt (Normalen, Begrenzungskugel, Skinning)?'),
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
    {'slug': 'vtb_smplestx', 'name': 'VideoToBVH: SMPLest-X (Körperschätzung)',
     'dateien': ['VideoToBVH/wrappers/smplest_x_wrapper.py', 'VideoToBVH/wrappers/_run_smplest_x.py'],
     'hinweis': ('Der Wrapper startet einen Unterprozess (Python 3.10, CUDA) und liest dessen '
                 'Ausgabe; das Ergebnis sind SMPL-X-Parameter je Frame. Bekannt und mehrfach '
                 'gefunden: SMPL hat 6.890 Vertices, SMPL-X 10.475 — die Topologien sind '
                 'unvereinbar, und ein Netz mit der falschen Zahl darf nicht durchrutschen. '
                 'Ebenfalls bekannt: Ein Unterprozess, dessen Ausgabe niemand abholt, laeuft '
                 'in einen vollen Puffer und haengt (im Projekt schon einmal passiert, behoben '
                 'durch einen Leerlese-Faden).'),
     'fragen': [
         ('Wird die Ausgabe des Unterprozesses waehrend des Laufs abgeholt, oder erst '
             'am Ende? Wo kann er haengen bleiben?'),
         ('Wo wird die Vertex- oder Gelenkzahl NICHT geprueft, bevor damit gerechnet '
             'wird?'),
         ('Was passiert bei einem Video ohne erkannte Person, bei mehreren Personen und '
             'bei einem Frame ohne Erkennung — Luecke, Sprung oder Absturz?'),
     ]},
    {'slug': 'vtb_foto', 'name': 'VideoToBVH: Foto-Analyse und 2D-Erkennung',
     'dateien': ['VideoToBVH/wrappers/mediapipe_photo.py', 'VideoToBVH/wrappers/photo_analyzer.py', 'VideoToBVH/wrappers/rtmpose_det.py'],
     'hinweis': ('Aus einem Foto Koerpermasse schaetzen: MediaPipe findet Landmarken, '
                 'photo_analyzer rechnet daraus Masse, rtmpose_det ist der zweite '
                 'Erkennungsweg (ONNX Runtime GPU). MediaPipe hat mp.solutions ab 0.10.30 '
                 'entfernt; dafuer gibt es hier eine eigene Anpassung (mediapipe_compat, '
                 'Tasks-API). Landmarken sind normiert (0..1) — wer sie mit Pixeln '
                 'verwechselt, bekommt Masse, die um Faktor Bildbreite falsch sind.'),
     'fragen': [
         ('Wo werden normierte Koordinaten und Pixel verwechselt, und wo fehlt die '
             'Umrechnung mit dem Seitenverhaeltnis?'),
         ('photo_analyzer rechnet Masse aus Abstaenden. Welche Annahme ueber die '
             'Koerperhaltung steckt darin, und was liefert sie bei einem schraegen oder '
             'sitzenden Menschen?'),
         ('Was passiert bei einem Foto ohne Person, mit zwei Personen oder mit '
             'abgeschnittenen Beinen?'),
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
