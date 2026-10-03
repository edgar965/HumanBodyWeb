# -*- coding: utf-8 -*-
"""Begutachtungsprompt — die Frage an die Prüf-KI nach einer Runde von „2D3D Kleider" (01.10.2026).

Edgar: „Es soll ein 3D-Modell herauskommen, das genau den Fotos entspricht, mit Kleidern, Haaren, die animiert werden
können. Textur perfekt so wie auf den Fotos von allen Seiten. Bei der Animation soll die Haut nicht durch die Kleider
schimmern. Mach ein Prompt, so dass es funktioniert, und du so lange iterierst, bis das Ergebnis OK ist."

Die Automatik (`IterationModell`) regelt, was sich messen lässt (Abstände zum Netz, zur Haut, zum Umriss, Farben,
Kanten); die Prüf-KI (lokal, Ollama, ein Modell mit Bildverständnis) sieht die Vergleichstafel und urteilt über das, was
keine Zahl sagt: falsches Stück, falscher Schnitt, Falten, Frisurform, Muster, Durchschimmern — und ob das Ergebnis OK
ist (`fertig`). Sie antwortet mit REZEPTZEILEN (`m.<funktion>(…)`, `G9rezept`), nicht mit Werten eines Schemas wie
`Iterationskritik` (Weg B der 2D3D Kleider). Der Text steht als Klasse, damit er versioniert und im Test prüfbar ist;
Zahlen, Zustand, Funktionsliste und Garderobe kommen je Runde dazu (`text`).
"""

__all__ = ['Begutachtungsprompt']


class Begutachtungsprompt:
    #: Ab dieser Ähnlichkeit darf die Prüf-KI „fertig" sagen — darunter zählt es nicht (`Begutachtungskritik`).
    FERTIG_AB = 8
    JE_KATEGORIE = 40
    MORPHE_HOECHSTENS = 30
    BEREICHE = (
        ('stuecke', 'Kleidungsstücke: Sind es die richtigen Stücke (Shirt, Bluse, Jacke, Kleid, Rock, Hose, Shorts, '
                    'Schuhe)? Fehlt eines, ist eines zu viel? Schnitt: Ärmellänge, Kragen und Ausschnitt, Saumhöhe, '
                    'Beinlänge.'),
        ('passform', 'Passform und Falten: Sitzt jedes Stück wie im Foto (eng oder locker, Bund, Ärmel)? Große Falten, '
                     'Bausch, Raffung, Fall des Stoffs.'),
        ('frisur', 'Frisur: Form, Scheitel, Pony, Länge je Seite, Volumen, Locken oder glatt, hinter dem Ohr oder ins '
                   'Gesicht.'),
        ('koerper', 'Körper: Proportionen, Bauch, Po, Brust, Schultern, Taille, Beine — was im Foto sichtbar anders '
                    'ist.'),
        ('textur', 'Farben und Textur: Farbton, Muster, Aufdruck, Nähte, Glanz — je Stück und am Haar, von allen '
                   'Seiten.'),
        ('haut', 'Durchschimmern: Wo liegt Haut sichtbar durch oder vor der Kleidung (Rumpf, Ärmel, Bund, Saum)? Das '
                 'darf nirgends sein.'),
    )
    LANDMARKEN = ('bauch', 'becken', 'brust', 'huefte_l', 'huefte_r', 'kinn', 'kopf', 'nacken', 'ohr_l', 'ohr_r', 'po',
                  'ruecken', 'rumpf', 'scheitel', 'schlaefe_l', 'schlaefe_r', 'schulter_l', 'schulter_r', 'stirn',
                  'taille_l', 'taille_r')
    ZIEL = (
        'Du bist Schneider, Friseur und Prüfer für 3D-Figuren. Ziel: Eine Genesis-9-Figur (3D, mit Rig, animierbar) '
        'soll der Person auf den Fotos GENAU entsprechen — Körperform, Kleidungsstücke (Art, Schnitt, Länge, Weite, '
        'Falten), Frisur (Form, Länge, Volumen, Farbe) sowie Farben und Textur von allen Seiten. Kleider und Haar '
        'müssen sich mit der Figur bewegen lassen, und bei der Bewegung darf keine Haut durch die Kleidung schimmern.')
    BILD = (
        'Das Bild zeigt OBEN die Fotos der Person aus mehreren Blickwinkeln und DARUNTER das aktuelle 3D-Modell aus '
        'genau denselben Blickwinkeln (Winkel und Übereinstimmung des Umrisses stehen darunter). Das Modell steht '
        'bauartbedingt in der A-Pose (Arme schräg vom Körper weg), die Fotos zeigen die Arme meist hängend — diesen '
        'Unterschied NICHT beanstanden und keine Haltung ändern. Vergleiche nur, was beide zeigen.')
    AUTOMATIK = (
        'Was die Automatik jede Runde selbst regelt und du deshalb NICHT vorschlägst (nur, wenn es grob falsch ist): '
        'Weite der Kleider gegen das Fotonetz, Morphe je Höhenband und Sektor, Luft zwischen Stoff und Haut, Hülle an '
        'den Fotoumriss, Stoffsimulation (Drapieren), Fotoprojektion auf die Kleider, Farbton von Kleidung und Haar '
        'aus den Fotopixeln, Haarlänge, Anlegen abstehender Haare, Körperbänder mit sichtbarer Haut an den '
        'Fotoumriss.\nZahlen der letzten Runde (gemessen, nicht geschätzt):\n%s')
    BEURTEILEN = (
        'Was DU beurteilst — das kann keine Zahl. Sieh jeden Bereich einzeln an und benenne konkret, was anders ist '
        '(was, wo, wie viel):\n%s')
    ANTWORT = (
        'Antworte als JSON:\n'
        '- "fertig": true NUR, wenn das Modell den Fotos in ALLEN Bereichen so nahe kommt, dass du nichts Wesentliches '
        'mehr ändern würdest (Ähnlichkeit mindestens %d). Sonst false.\n'
        '- "aehnlichkeit": 1 (völlig anders) bis 10 (kaum zu unterscheiden); "urteil": ein Satz auf Deutsch.\n'
        '- "bereiche": je Bereich ein Eintrag {"bereich": Schlüssel, "passt": 1 bis 10, "abweichung": kurz und '
        'konkret}; die Schlüssel sind %s.\n'
        '- "fehlt_im_modell": Einzelheiten der Fotos, die keine Funktion unten erzeugen kann (Logo, Schnürung, '
        'Muster, Accessoire).\n'
        '- "rezept": höchstens %d Zeilen, jede Zeile GENAU EIN Aufruf m.<funktion>(…) aus der Liste unten — Argumente '
        'nur Zahlen, Zeichenketten, Wörterbücher und Tupel. Reihenfolge: zuerst falsche oder fehlende Stücke '
        '(kleid_nur / kleid_anteil / kleid_aus mit Kennungen aus der Garderobe unten, haar_nur mit einer Frisur der '
        'Liste), dann Form (morph_ort, kleid_ring, kleid_welle, kleid_falten, haar_biegen, haar_clump, haar_noise, '
        'haar_straighten, haar_trim, koerper_ort), dann Farben und Muster (kleid_farbe, haar_farbe, kleid_decal) nur '
        'bei deutlicher Abweichung. Kleine Schritte: weg_cm 1 bis 3, wert 0,3 bis 1. Keine Zeile für etwas, das die '
        'Automatik regelt. Würdest du nichts ändern, ist "rezept" eine leere Liste.\n'
        '- "begruendung": ein bis drei Sätze auf Deutsch.')
    ORTE = (
        "Orte (Argument ort, kombinierbar): {'band': (von, bis)} Höhenanteil des Stücks, 0 unten bis 1 oben; "
        "{'sektor': (a, b)} Grad um die senkrechte Achse, 0 = vorn, 90 = links, 180 oder -180 = hinten, -90 = rechts; "
        "{'landmarke': Name, 'radius_cm': r} mit Name aus %s; {'kugel': [x, y, z], 'radius_cm': r} in Metern, Füße auf "
        "0. Beispiele: m.morph_ort('kleidung', 'g9_base_shirt', 'bauch_weiter', {'landmarke': 'bauch', "
        "'radius_cm': 10}, weg_cm=2.0, richtung='haut', wert=1.0) · m.haar_biegen('kin_hair', 'pony', "
        "{'landmarke': 'stirn', 'radius_cm': 6}, richtung='vorn', weg_cm=3.0) · "
        "m.kleid_welle('angie_jeans', 'knie', {'band': (0.3, 0.5)}, "
        "laenge_cm=5.0, tiefe_cm=1.0) · m.koerper_ort('bauch', {'landmarke': 'bauch', 'radius_cm': 8}, weg_cm=1.5) · "
        "m.kleid_decal('g9_base_shirt', 'aufdruck', {'band': (0.5, 0.8), 'sektor': (-40, 40)}, farbe='#c0392b', "
        "deckung=0.9)")

    def __init__(self, garderobe, frisuren):
        """`garderobe`: [(Kategorie, [Kennung, …])], `frisuren`: [Kennung, …] — was ein Rezept nennen darf."""
        self.garderobe_liste = [(str(k), [str(i) for i in ids]) for k, ids in garderobe]
        self.frisuren = [str(f) for f in frisuren]

    @classmethod
    def aus_bibliothek(cls):
        from Genesis9.haargenerisch import G9haargenerisch
        from Genesis9.kleidgenerisch import G9kleidgenerisch
        garderobe = [(kategorie, [e['id'] for e in stuecke]) for kategorie, stuecke in G9kleidgenerisch.gruppen()]
        return cls(garderobe, [e['id'] for e in G9haargenerisch.frisuren()])

    def garderobe_ids(self):
        return {i for _k, ids in self.garderobe_liste for i in ids}

    def frisur_ids(self):
        return set(self.frisuren)

    # ------------------------------------------------------------------ Text

    def text(self, modell, befund, note, runde, hoechstens):
        from Genesis9.modellrezept import G9rezept
        bereiche = '\n'.join('%d. %s' % (i + 1, text) for i, (_k, text) in enumerate(self.BEREICHE))
        return '\n\n'.join([
            self.ZIEL, self.BILD,
            self.AUTOMATIK % self.zahlen(befund or {}, note or {}, runde),
            self.BEURTEILEN % bereiche,
            self.ANTWORT % (self.FERTIG_AB, ', '.join(k for k, _t in self.BEREICHE), hoechstens),
            self.ORTE % ', '.join(self.LANDMARKEN),
            'Funktionen (m.<name>(Signatur) — Bedeutung):\n' + G9rezept.hilfetext(),
            self.zustand(modell), self.garderobe()])

    @staticmethod
    def _z(wert):
        return '?' if wert is None else str(round(float(wert), 3))

    def zahlen(self, befund, note, runde):
        from iterationen2d3d.kleiderwahl import Kleiderwahl
        zeilen = ['Runde %s: Gesamtabweichung %s (Umriss IoU %s, Fotofarbe %s; kleiner ist besser)' % (
            runde, self._z(note.get('abweichung')), self._z(note.get('iou')), self._z(note.get('farbe')))]
        for sorte, e in (befund.get('teile') or {}).items():
            art = e.get('art')
            if art == 'koerper':
                zeilen.append('Körper: %s mm zum Fotonetz (+ außen)' % self._z(e.get('netz_mm')))
            elif art == 'kleidung':
                innen = None if e.get('haut_innen') is None else 100.0 * float(e['haut_innen'])
                zeilen.append('%s: Stoff %s mm zum Fotonetz, der Körper darunter %s mm; Luft zur Haut mindestens '
                              '%s mm, %s %% der Stoffpunkte in der Haut'
                              % (sorte, self._z(e.get('netz_mm')), self._z(e.get('grund_mm')),
                                 self._z(e.get('haut_min_mm')), self._z(innen)))
            elif art == 'haar':
                zeilen.append('%s (Frisur): %s mm zum Fotonetz (Betrag)' % (sorte, self._z(e.get('netz_abs_mm'))))
        baender = befund.get('koerper_baender') or {}
        if baender:
            zeilen.append('Im Foto je Körperband: ' + ', '.join(
                '%s = %s' % (b, 'Haut' if Kleiderwahl.haut(rgb) else 'Stoff') for b, rgb in baender.items() if rgb))
        return '\n'.join(zeilen)

    def zustand(self, modell):
        from Genesis9.kleidgenerisch import G9kleidgenerisch
        from iterationen2d3d.iterationkleider import IterationKleider
        passform = G9kleidgenerisch.PASSFORM
        kleider = IterationKleider.sorten(modell.kleidung, modell.SORTE)
        frisuren = IterationKleider.sorten(modell.haar, modell.SORTE)
        eigen = [(k, v) for werte in (modell.kleidung, modell.haar) for k, v in sorted(werte.items())
                 if ('.' + modell.EIGEN) in str(k)]
        bild = getattr(modell, 'BILD', None)
        schichten = sorted(k for k in modell.kleidung if bild and ('.' + bild) in str(k))
        morphe = ', '.join('%s = %s' % (k, v) for k, v in eigen[:self.MORPHE_HOECHSTENS])
        if len(eigen) > self.MORPHE_HOECHSTENS:
            morphe += ' … und %d weitere' % (len(eigen) - self.MORPHE_HOECHSTENS)
        return '\n'.join([
            'Das Modell jetzt:',
            'Kleidung: ' + (', '.join('%s (Anteil %s)' % (k, a) for k, a in kleider) or 'keine'),
            'Frisur: ' + (', '.join('%s (Anteil %s)' % (k, a) for k, a in frisuren) or 'keine'),
            'Tönung Kleidung %s, Haar %s; Passform Weite %s cm, Länge %s cm' % (
                modell.farben.get('kleidung'), modell.farben.get('haar'),
                modell.kleidung.get(passform + 'weite', 0), modell.kleidung.get(passform + 'laenge', 0)),
            'Gesetzte eigene Morphe (mit morph_wert umstellbar): ' + (morphe or 'keine'),
            'Texturschichten (mit bild_wert umstellbar): ' + (', '.join(schichten) or 'keine')])

    def garderobe(self):
        zeilen = ['Garderobe — Kennungen für kleid_nur / kleid_anteil / kleid_aus, je Kategorie:']
        for kategorie, ids in self.garderobe_liste:
            rest = len(ids) - self.JE_KATEGORIE
            zeilen.append('  %s: %s%s' % (kategorie, ', '.join(ids[:self.JE_KATEGORIE]),
                                          ' … und %d weitere' % rest if rest > 0 else ''))
        zeilen.append('Frisuren — Kennungen für haar_nur / haar_anteil: ' + (', '.join(self.frisuren) or 'keine'))
        return '\n'.join(zeilen)
