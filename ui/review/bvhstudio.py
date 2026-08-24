# -*- coding: utf-8 -*-
"""Review-Bereiche: BVH Studio

Zeitleiste, Spuren, Eigenschaften, Werkzeuge, Projektdateien.

Aus ui/review_bereiche.py herausgeloest (17.08.2026): Die Datei hatte 965 Zeilen und 59
Bereiche in einer Liste — der Spitzenbefund von `dateigroesse`.

Heisst `bvhstudio.py` und nicht `studio.py`, weil es `core/api/studio.py` schon
gibt: Zwei gleichnamige Dateien im selben Projekt sind beim Suchen und in
Fehlermeldungen nicht auseinanderzuhalten (`namens-dubletten`, Kriterium 7).
"""
BEREICHE = [
    {'slug': 'fe_studio_tracks', 'name': 'Frontend: BVH-Studio Spuren',
     # `tracks.js` ist seit dem 18.08.2026 nur noch die Registrierung; die
     # Arbeit steht in diesen vier Klassen.
     'dateien': ['HumanBodyWeb/static/viewer/bvh_studio/spurerzeugung.js',
                 'HumanBodyWeb/static/viewer/bvh_studio/spurabbau.js',
                 'HumanBodyWeb/static/viewer/bvh_studio/kameraschluessel.js',
                 'HumanBodyWeb/static/viewer/bvh_studio/audiospur.js'],
     'hinweis': ('Verwaltet die Spuren des BVH-Studios: Ausschnitte, Verschiebungen, Ueberblendungen. Rechnet mit Frame-Indizes UND Sekunden; die Bildrate steckt in den Daten. Fehler zeigen sich als ruckelnde oder um Frames verschobene Wiedergabe.'),
     'fragen': [
         'Wo werden Frames und Sekunden vermischt, und wo wird gerundet statt abgeschnitten (oder umgekehrt)?',
         'Was passiert am Rand: erster Frame, letzter Frame, Ausschnitt der Laenge 0, Ueberblendung laenger als der Ausschnitt?',
         'Wo wird eine Spur veraendert, waehrend die Wiedergabe laeuft?',
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
]
