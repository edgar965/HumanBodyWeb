# -*- coding: utf-8 -*-
"""Werkzeugbildrender — Gruppe „Bildvergleich: Render aus den Blickwinkeln der Fotos“ des Reiters „Tools“ (03.10.2026).

Schema und Leser: `Architektur2d3dwerkzeuge`. Gelesen im Code: `Begutachtungsrunde._runde` (Abschnitte „Modell bauen“ bis „Rendern“),
`Genesishaarrender`, `Mitsubaszene`, `Renderwahl`, `Kleidermodellbau`. Die Zeiten stammen aus `Workflowzeiten` (auftrag.log des
Auftrags 2026.10.01.20.10.04, 02.10.2026) und den Docstrings der genannten Klassen; gelaufen ist hier nichts.
"""

__all__ = ['Werkzeugbildrender']


class Werkzeugbildrender:
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    G = 'Genesis9/'
    RENDER = ('HumanBodyWeb/core/dienste/genesishaarrender.py', 'Genesishaarrender')
    KENNUNG = 'bildrender'
    TITEL = 'Bildvergleich: Render aus den Blickwinkeln der Fotos'
    EINLEITUNG = (
        'Das Modell wird aus denselben Winkeln gerendert wie die Fotos. 1. Teile des Modells bauen (Kleidermodellbau), 2. in die Haltung der '
        'Fotos häuten (G9haltungshaut), 3. rendern (Genesishaarrender): Mitsuba 3 auf der Grafikkarte, pyrender als Rückfall. Der Render ist '
        'orthografisch und freigestellt (Alpha = Figur); die Kamera ist für Fotos und Renders dieselbe, sonst stimmt die Note nicht (letzte '
        'Zeile). Das alles läuft im Arbeitsprozess (python14 mit Django), nie im Dev-Server, und es gibt eine GPU: ein Lauf zur Zeit '
        '(Engine2d3dKleidergpu). Das Rendern selbst ist billig, der Bau davor und die Messungen danach sind es nicht — Zahlen je Zeile.'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Render einer Ansicht aus einem Wertesatz',
         'Der Weg einer Runde bis zum Bild, ohne Note: Modell aus Werten bauen, in die Haltung der Fotos häuten, aus einem Winkel rendern.',
         'python',
         '\n'.join((
             'from Genesis9.modellmitkleidern import ModellMitKleidern',
             'from Genesis9.haltungshaut import G9haltungshaut',
             'from core.dienste.kleidermodellbau import Kleidermodellbau',
             'from core.dienste.begutachtungswerkzeug import Begutachtungswerkzeug',
             'from core.dienste.haarzonen import Haarzonen',
             'from core.dienste.genesishaarrender import Genesishaarrender',
             "modell = ModellMitKleidern.aus(job.ergebnis['kreislauf']['modell'])   # oder ergebnis['iterationen'][i]['werte']",
             'bau = Kleidermodellbau(job.stellung(), None, koerper=modell.koerper, kacheln=Begutachtungswerkzeug(job, ablage).kacheln())',
             'teile = G9haltungshaut(bau.stellung, modell.drehung(), bau.boden).posieren(Haarzonen.anwenden(bau.teile(modell), modell.farben))',
             'render = Genesishaarrender(None)',
             "render.bild_teile([(t['punkte'], t['dreiecke'], t['farbe'], Genesishaarrender.extra(t)) for t in teile],",
             "                  0.0, Path('ansicht_+000.png'), groesse=(384, 576))   # winkel in Grad, → pfad (RGBA, Alpha = Figur)",
             'render.schliessen()',
         )),
         [RENDER, (D + 'kleidermodellbau.py', 'Kleidermodellbau'), (D + 'teilevorrat.py', 'Teilevorrat'),
          (D + 'koerperanhaenge.py', 'Koerperanhaenge'), (G + 'haltungshaut.py', 'G9haltungshaut'), (D + 'haarzonen.py', 'Haarzonen'),
          (G + 'modellmitkleidern.py', 'ModellMitKleidern'), (D + 'begutachtungswerkzeug.py', 'Begutachtungswerkzeug')],
         'KEIN fertiger Einzelaufruf: Das ist der Ablauf aus Begutachtungsrunde._runde (von „Modell bauen“ bis „Rendern“), auf das Nötigste '
         'gekürzt; als Einzelaufruf nicht gelaufen. Nur im Stil des Arbeitsprozesses (Django + GPU, nie im Dev-Server) und nur, wenn kein '
         'Lauf die GPU hält. koerper=modell.koerper ist Pflicht, sonst erreichen Körperregler des Rezepts den Bau nicht (engine2d3dkleider.md, '
         '01.10.2026). Gebaut wird in der A-Pose, gerendert in der Haltung der Fotos (G9haltungshaut häutet auch Kurven und Normalen). '
         'Kosten (Workflowzeiten, auftrag.log …20.10.04, 02.10.2026): Abschnitt „Modell bauen“ (Bau, Haarzonen, Häutung, Kennfarben-Render je '
         'Blickwinkel) kalt 47,9–62,4 s, warm 5,2–5,3 s; der Vorrat von Kleidung und Haar allein kalt 41,7 s (Kleidung 28,9 s, Haar 10,9 s); '
         'Abschnitt „Rendern 1 von 3“ (Render + Note) kalt 8,7–10,5 s mit Szenenaufbau, warm 2,7–3,4 s; jede weitere Ansicht 0,1–0,2 s.'),

        ('Kopf-Render',
         'Nur der Kopf aus einem Winkel — für Gesichtslandmarken, Kopftafel und Haarvergleich.',
         'python',
         '\n'.join((
             "# render = Genesishaarrender(None) und teile wie in der Zeile oben (gehäutet); dann:",
             "render.bild_kopf([(t['punkte'], t['dreiecke'], t['farbe'], Genesishaarrender.extra(t)) for t in teile],",
             "                 0.0, Path('kopf.png'), groesse=(512, 512), saat=0, kennung=False)   # → pfad, RGB auf weißem Grund",
             'Genesishaarrender.KOPF_HOEHE, Genesishaarrender.KOPF_UNTER_SCHEITEL   # 0,34 m Bildhöhe; Mitte 0,13 m unter dem Scheitel',
         )),
         [RENDER, (D + 'mitsubaszene.py', 'Mitsubaszene')],
         'Das Ergebnis ist RGB mit WEISSEM Grund (der Detektor liest Fotos, keine Alphakanäle). saat ist Mitsubas Zufallsfolge (Gesichtsmasse '
         'mittelt über vier); kennung=True liefert Kennfarben (Haarabgleich). Nutzer in der Runde: Gesichtsmasse (1024², vier Saaten), '
         'Pruefbilder.kopf (384²), Haarabgleich (256², Kennfarben). Kosten: Kopf 512² mit Strähnenkurven 1,1 s bei neuer Szene, 0,11 s für die '
         'zweite Ansicht (Mitsubaszene-Docstring, 01.10.2026, Szene mit Pixie-Strähnen); je Render ≈ 0,45 s bei 1024² (Kommentar bei '
         'Gesichtsmasse.SAATEN, nicht nachgemessen). Der Ausschnitt muss zum Foto passen: Pruefbilder.kopfausschnitt schneidet das Foto '
         'mit denselben Maßen (Gruppe „Prüfbilder“).'),

        ('Renderer wählen: Mitsuba oder pyrender',
         'Womit die Runden, die Fotoprojektion und der Film rendern — Einstellung der Seite und der Zugriff im Code.',
         'seite',
         '\n'.join((
             'Einstellungen → 2D3D Kleider (/settings/2d3dkleider/): „Mitsuba 3 (Pfadverfolgung auf der Grafikkarte)“ oder „pyrender (OpenGL)“',
             "# gespeichert in AppSettings.ui_prefs['kleider2d3d_renderer']; im Code:",
             "Renderwahl.gewaehlt()                      # 'mitsuba' | 'pyrender'",
             "Genesishaarrender(None, motor='pyrender')   # überschreibt die Einstellung für diesen Renderer",
         )),
         [(A + 'seite_kleider2d3d_einstellungen.py', 'Kleider2d3dEinstellungenSeite'), (D + 'renderwahl.py', 'Renderwahl'), RENDER],
         'Vorgabe ist Mitsuba. Fehlt Mitsuba oder CUDA, rendert pyrender weiter (Warnung im Log); render.motor sagt, wer das letzte Bild '
         'gerendert hat, und steht im Befund (befund.motor). Gelesen wird die Wahl beim Anlegen jedes Renderers; ein laufender Arbeitsprozess '
         'behält seine Wahl bis zum nächsten Renderer. Noten verschiedener Renderer sind nicht vergleichbar: dieselbe Runde ergab pyrender '
         '1,820 und Mitsuba 1,725 bei gleicher IoU (Docstring Renderwahl, 01.10.2026); Begutachtungsstand.befund_fuer_regeln wirft die '
         'Renderfarben eines fremden Renderers weg. Dieselbe Runde warm, abwechselnd: pyrender 62,2 s, Mitsuba 72,1 s, davon Rendern 11,3 '
         'und 12,1 s (Docstring Renderwahl, ortsmorphe.md). Nur Mitsuba zeigt Stranghaar als Strähnen. Widerspruch im Code: Der Docstring '
         'von Renderwahl sagt, pyrender bekomme Normalkarten nicht mitgegeben — Genesishaarrender._textur gibt sie ihm mit.'),

        ('Mitsuba-Szene',
         'Die Teile als Mitsuba-3-Szene auf der Grafikkarte (Pfadverfolgung); normalerweise nur über Genesishaarrender benutzt.',
         'python',
         '\n'.join((
             'from core.dienste.mitsubaszene import Mitsubaszene',
             'Mitsubaszene.mitsuba()                     # Mitsuba-Modul oder None (Grund in Mitsubaszene._fehler und im Log)',
             'szene = Mitsubaszene(teile, kennung=False)   # teile: [(punkte, dreiecke, farbe, extra)]',
             'szene.rendern(mitte, halb, winkel, (breite, hoehe), spp=None, saat=0)   # → (H, B, 4) float 0…1',
         )),
         [(D + 'mitsubaszene.py', 'Mitsubaszene'), (D + 'mitsubamaterial.py', 'Mitsubamaterial'), RENDER],
         'Variante cuda_ad_rgb (OptiX): braucht eine CUDA-GPU; ohne sie liefert mitsuba() None und Genesishaarrender nimmt pyrender. 64 '
         'Abtastungen je Pixel (SPP), Himmel 0,8 plus Richtlicht 1,4, Pfadtiefe 6; das Kennbild (kennung=True) ist die Albedo mit einer '
         'Abtastung — genau die Kennfarben. Genesishaarrender baut die Szene einmal je Teilesatz und tauscht bei gleichen Dreiecken nur die '
         'Punkte (punkte_setzen). Der Dr.Jit-Cache gehört nach settings.MITSUBA_CACHE (DRJIT_CACHE_DIR vor dem Import setzen), sonst landet '
         'er im System-Temp auf C:. Mitsubas hair-Material staucht Farben (Soll 0,10 → 0,23; 0,85 → 0,60; ortsmorphe.md, 01.10.2026); '
         'Mavick mit Daz-Bild kam als 131/109/84 gegen 152/140/124 unter pyrender (Mehrfachstreuung zwischen den Haarkarten). Zeit '
         '(Docstring, 01.10.2026, Grundfigur mit Pixie-Strähnen): Szene 0,3 s, erstes Bild 0,6 s (Kernel), danach 1024 × 1536 mit 64 '
         'Abtastungen 0,04 s; gegen pyrender IoU der Umrisse 0,984–0,988, Schwerpunkt ≤ 0,3 Pixel daneben.'),

        ('Kamera und Winkel: dieselbe für Foto und Render',
         'Die Regel hinter jedem Vergleich: Winkel in Grad ab vorn, positiv zur LINKEN Seite der Figur, orthografische Kamera.',
         'regel',
         'Kein Aufruf. Kamera bei (sin w, 0, cos w) × Abstand, Blick auf die Mitte der Figur; Winkel w: 0 = von vorn, +90 = linke Seite, '
         '180 = hinten (Genesishaarrender._szene, Mitsubaszene.sensor).',
         [RENDER, (D + 'iterationsbild.py', 'Iterationsbild'), (D + 'mitsubaszene.py', 'Mitsubaszene')],
         'Die Note vergleicht Umrisse, nachdem Iterationsbild beide Bilder an der Figur ausgerichtet hat (Höhe und Schwerpunkt des Rumpfbands). '
         'Eine perspektivische Kamera verschöbe Kopf und Füße je nach Abstand gegeneinander, das ließe sich nicht herausrechnen — deshalb '
         'orthografisch (Docstring Genesishaarrender). Standardgröße des Bildes 512 × 768, Rand 0,06 der Figurhöhe; in den Runden das '
         'Größere von Stufenbreite und Prüfbreite (Vorgabe 384) mal 1,5 als Höhe (Begutachtungsrunde._runde). Mitsuba und pyrender haben '
         'dieselbe Kamera (die erste Probe nahm die halbe Höhe auch für y und stauchte die Figur um 1,5, bis es gemessen wurde; '
         'ortsmorphe.md, 01.10.2026). Fotoprojektion und Sichtkoerper rechnen diese Abbildung nach (Docstring Mitsubaszene): Wer die '
         'Kamera ändert, ändert beide mit.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Genesishaarrender', 'ruft', 'Renderwahl', 'gewaehlt(): der Motor, wenn kein motor= übergeben wurde'),
        ('Genesishaarrender', 'ruft', 'Mitsubaszene', 'mitsuba(), Mitsubaszene(teile, kennung), punkte_setzen(), rendern(): GPU-Bild; None → pyrender'),
        ('Mitsubaszene', 'ruft', 'Mitsubamaterial', 'textur(), flach(), kennung(), haar(), gruppen(), normalen(): das Material je Teilnetz'),
        ('Kleider2d3dEinstellungenSeite', 'ruft', 'Renderwahl', 'aus(prefs), WAHLEN, SCHLUESSEL: zeigt und speichert die Wahl'),
        ('Kleidermodellbau', 'ruft', 'Teilevorrat', 'antwort(art, rumpf, rechnen, roh): Kleidung und Haar aus dem Vorrat, solange ihr Bauplan gleich bleibt'),
        ('Kleidermodellbau', 'ruft', 'Koerperanhaenge', 'teile(bau, modell): Augen, Mund, Wimpern, Brauen'),
        ('Begutachtungswerkzeug', 'ruft', 'Kleidermodellbau', 'sichtkoerper(): koerper(); bestes_glb(): teile(modell), glb(teile, pfad)'),
        ('Begutachtungswerkzeug', 'ruft', 'Haarzonen', 'bestes_glb(): anwenden(teile, farben); _haarzonen(): messen()'),
    ]
