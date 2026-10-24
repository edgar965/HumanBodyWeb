# -*- coding: utf-8 -*-
"""Architekturmesh3daischicht — Abschnitt „Kleider wie das Ziel: der Schichtkopf“ der Seite Hilfe → Architektur → Mesh3DAI (21.10.2026).

Edgar, 21.10.2026: „das ist doch gaga, wie sieht die KI nicht, welches Zielstück sie bauen soll?? wie trainierst du denn??“ → „mach, und update auch die Hilfe dateien“.
Konzept `Docu/konzepte/2026-10-21_mesh3dai-kleider-wie-das-ziel-konzept.md`, Code `ProjektTemp/_wegwerf/mesh3dai_schicht_*.py`.
Gelesen beim Aufruf (alles unter `3DObjects/mesh3dai/_schicht/`): `darstellbar_v1.json` (Rückbau ohne Netz, `mesh3dai_schicht_darstellbar.py`), der gewählte Lauf (`gewaehlt.json` → `laeufe/<Lauf>/
lauf_ergebnis.json`, `mesh3dai_schicht_training.py` bzw. `…_training3.py`), `gegen_ziel.json` (Wege gegen die Zielstücke, `flaeche_gegen_ziel.py --ablegen`) und `pruefung.json`
(Prüfung nach Fehlerklassen, `schicht_pruefung_lauf.py --ablegen`, Konzept Abschnitt 8). Fehlt eine Datei, steht der Teil leer und sagt es.
"""

import json
import statistics
from pathlib import Path

from django.conf import settings

__all__ = ['Architekturmesh3daischicht']


class Architekturmesh3daischicht:
    WEGTEXT = {'k': 'k — aus dem Netz geschnitten', 's': 's — GarmentCode-Schnitt', 'f': 'f — Schnitt aus der Fläche', 'g': 'g — Schicht aus der KI (neu)', 'ki': 'Körper der KI'}

    #: (Schritt, Eingabe, was passiert, Ausgabe) — aus dem Code gelesen
    SCHRITTE = (
        ('Soll (je Trainingsfigur)', 'Zielfigur in Ruhelage: Körper (Genesis-Käfig, 25.182 Punkte) und ihre Stücke mit Art je Dreieck',
         'Von jedem Käfigpunkt ein Strahl entlang der Normale (GPU, Warp): trifft er ein Stück der Art, bevor er den Körper trifft, ist der Punkt gedeckt; gemerkt werden innerste und äußerste Lage. '
         'Ein Treffer zählt nur, wenn der Stoff dort diesem Punkt gehört (Abstand zur Haut höchstens 1,25 × Abstand zum nächsten Körperpunkt + 15 mm) — sonst ist es das andere Hosenbein '
         'oder ein Ärmel (Fassung 2; Haar ohne diese Prüfung).',
         'je Punkt und Art: gedeckt ja/nein, Abstand der Außenseite'),
        ('Beobachtung', 'die Punkte der Eingangsfläche (im Training: die Wolke der Figur; im Einsatz: das Eingangsnetz, wie Weg k an den Körper der KI gebunden)',
         'je Käfigpunkt die 16 nächsten Punkte im Umkreis 5 cm: Lage zur Normale, Abstand, Farbe, Art aus der Zerlegung',
         'Merkmal je Käfigpunkt'),
        ('Schichtkopf', 'Merkmale je Käfigpunkt',
         'Punktnetz über die Nachbarn (Maximum und Mittel), Faltungen über den Käfig fein (8 Nachbarn) und grob (1.500 Knoten — sieht unter das Shirt und zwischen die Beine), wieder fein',
         'je Punkt und Art: Deckung (0–1) und Abstand'),
        ('Stück bauen', 'Deckung, Abstand, Käfig der KI-Figur',
         'Nur Arten, die die Zerlegung auf mindestens 0,5 % der Eingangsfläche sieht. Käfigdreiecke an der Linie Deckung = 0,5 geschnitten (glatter Saum), um den Abstand nach außen '
         'verschoben; Haut wie die Käfigpunkte darunter',
         'ein Stück je Art, geschlossen, folgt dem Körper'),
    )

    @staticmethod
    def wurzel():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_schicht'

    @classmethod
    def _json(cls, name):
        p = cls.wurzel() / name
        return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else None

    #: Messungen der Darstellbarkeit, neueste Fassung zuerst (Fassung = `Schichtdaten.FASSUNG` des Solls, das sie zurückbaut)
    DARSTELLBAR = (('darstellbar_v2.json', 2), ('darstellbar_v1.json', 1))

    @classmethod
    def darstellbar(cls):
        zeilen, fassung = None, None
        for name, f in cls.DARSTELLBAR:
            zeilen = cls._json(name)
            if zeilen:
                fassung = f
                break
        if not zeilen:
            return None
        je = {}
        for z in zeilen:
            if z.get('weg_ziel') and z.get('ziel_weg'):
                je.setdefault(z['art'], []).append(z)
        aus = []
        for art, liste in sorted(je.items(), key=lambda kv: -len(kv[1])):
            aus.append({'art': art, 'stuecke': len(liste), 'weg_ziel': statistics.median(z['weg_ziel'][0] for z in liste),
                        'ziel_weg': statistics.median(z['ziel_weg'][0] for z in liste), 'loecher': 100 * statistics.median(z['loecher'] for z in liste),
                        'loecher_max': 100 * max(z['loecher'] for z in liste),
                        'ueberschuss': 100 * statistics.median(z['ueberschuss'] for z in liste) if all('ueberschuss' in z for z in liste) else None})
        return {'zeilen': aus, 'figuren': len({z['figur'] for z in zeilen}), 'fassung': fassung}

    @classmethod
    def lauf(cls):
        g = cls._json('gewaehlt.json')
        if not g:
            return None
        e = json.loads((cls.wurzel() / 'laeufe' / g['lauf'] / 'lauf_ergebnis.json').read_text(encoding='utf-8'))
        if 'job_training' in e:         # seit 22.10.2026 gewählt: der Basislauf auf den sechs Tripo-Jobs nachtrainiert (eigenes Format, ohne `schritte` oben — die Seite warf KeyError)
            j = e['job_training']
            return {'name': g['lauf'], 'grund': g.get('grund', ''), 'job': True, 'text': e.get('text', ''), 'basislauf': e.get('basislauf'), 'jobs': j.get('jobs', []),
                    'schritte': j.get('schritte'), 'messung': [{'test': t, 'iou': m.get('iou', {}), 'mm': m.get('abstand_mm_median')} for t, m in (j.get('messung') or {}).items()],
                    'fassung': 0}
        letzte = {}
        for v in e.get('verlauf', []):
            letzte[v.get('messung', 'sauber')] = v
        messungen, fassung = [], int(e.get('fassung_daten', 2))
        for name, v in letzte.items():
            if fassung >= 3:        # Fassung 3: eine Zeile je Größe (Bedeckung, Art außen, Haar, Lage), nicht je Art
                zeilen = [{'groesse': cls.GROESSEN.get(k, k), 'netz': w, 'basis': v['naechster'].get(k)} for k, w in v['netz'].items()]
            else:
                zeilen = [{'art': art, 'netz': w, 'basis': v['naechster'].get(art, {})} for art, w in v['netz'].items()]
            messungen.append({'name': name, 'schritt': v['schritt'], 'zeilen': zeilen})
        return {'name': g['lauf'], 'grund': g.get('grund', ''), 'schritte': e['schritte'], 'sekunden': e['sekunden'], 'gewichte': e.get('gewichte'),
                'pruefwolken': e['pruefwolken'], 'messungen': messungen, 'fassung': fassung}

    #: Namen der Größen eines Laufs der Fassung 3 (`Schichttraining3.messen`)
    GROESSEN = {'bedeckt_iou': 'Bedeckung (IoU)', 'nackt_wo_bedeckt': 'nackt, wo das Ziel bedeckt (Anteil)', 'art_aussen': 'Art außen getroffen (Anteil)', 'haar_iou': 'Haar (IoU)',
                'mm_median': 'Lage, Median (mm)', 'mm_p90': 'Lage, 90 %-Wert (mm)'}
    #: Fehlerklassen der Prüfung (`Kleiderpruefung`): Schlüssel → Spaltenkopf
    KLASSEN = (('luecke', 'Lücke'), ('fahne', 'Fahne'), ('durchstich', 'Durchstich'), ('zacken', 'Zacken'), ('mulde', 'Mulde'), ('haar', 'Haar'),
               ('luecke_ziel', 'Lücke gegen Ziel'), ('fahne_ziel', 'Fahne gegen Ziel'))

    @classmethod
    def pruefung(cls):
        """Prüfung nach Fehlerklassen (`pruefung.json`, `ProjektTemp/_wegwerf/schicht_pruefung_lauf.py --ablegen`): je Job, Probe und Weg eine Zeile, das Ziel als Bezug."""
        d = cls._json('pruefung.json')
        if not d:
            return None
        aus = []
        for job, proben in d.items():
            for probe, e in proben.items():
                zeilen = []
                for weg, b in list(e.get('wege', {}).items()) + [('ziel', e.get('ziel') or {})]:
                    werte = [None if b.get(k) is None else round(100 * b[k], 1) if k != 'zacken' else round(b[k], 2) for k, _n in cls.KLASSEN]
                    stellen = b.get('stellen') or {}
                    zeilen.append({'weg': 'Ziel (Bezug)' if weg == 'ziel' else cls.WEGTEXT.get(weg, weg), 'werte': werte, 'neu': weg == 'g',
                                   'ruecken': round(100 * stellen['Rücken unten']['luecke_ziel'], 1) if 'Rücken unten' in stellen and 'luecke_ziel' in stellen['Rücken unten'] else None})
                aus.append({'job': job, 'probe': probe, 'gemessen': e.get('gemessen'), 'zeilen': zeilen})
        return {'klassen': [n for _k, n in cls.KLASSEN], 'jobs': aus}

    @classmethod
    def gegen_ziel(cls):
        d = cls._json('gegen_ziel.json')
        if not d:
            return None
        aus = []
        for job, eintrag in d.items():
            zeilen = []
            for z in eintrag['zeilen']:
                zeilen.append({'art': z['art'], 'weg': cls.WEGTEXT.get(z['weg'], z['weg']), 'neu': z['weg'] == 'g', 'weg_ziel': z['weg_ziel'], 'ziel_weg': z['ziel_weg'],
                               'loecher': round(100 * z['loecher'], 1) if z.get('loecher') is not None else None})
            aus.append({'job': job, 'probe': eintrag['probe'], 'gemessen': eintrag['gemessen'], 'zeilen': zeilen})
        return aus

    @classmethod
    def kontext(cls):
        return {'schritte': cls.SCHRITTE, 'darstellbar': cls.darstellbar(), 'lauf': cls.lauf(), 'gegen_ziel': cls.gegen_ziel(), 'pruefung': cls.pruefung()}
