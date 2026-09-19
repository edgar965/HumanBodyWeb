# -*- coding: utf-8 -*-
"""Bildmodellfototextur — Textur Stufe 2: Fotofarben je Käfigpunkt und je Texel, als UDIM gebacken.

Edgar (19.09.2026): „Überlege auch ob eine Textur möglich wäre. Du hast doch
aus unterschiedlichen Bereichen Textur infos." — und abends: „warum ist das
Modell noch mit dieser miserablen Textur? … mach ca. 10 Nahaufnahmen von
Ursula mit HD aus unterschiedlichen Winkeln". Stufe 1 tönt die Daz-Haut
(`Bildmodelltextur`, Hautton). Stufe 2 nimmt die Farbe der Fotos selbst:

  1. `_run_fotofarben.py` (python10): je Bild mit Häkchen „Textur" das Netz ins
     Bild projizieren — ein Körper-Hauptbild mit seinem SMPLest-X-Netz und
     dessen Kamera; jedes andere Bild (Nahaufnahme, Kopfbild, Nebenbild mit
     Körperteil) über sein RIG gegen das Netz des Referenz-Hauptbilds
     (`Nahaufnahme`: PnP, Brennweitensuche — SMPLest-X schätzt auf einem
     Detail einen ganzen Körper, auf Ursulas Fuß standen 0 Punkte). Tiefen-
     test, Personenmaske, Sichtwinkel, Haut → Farbe und Gewicht je SMPL-X-
     Punkt, und je TEXEL der fünf Kacheln (`Fototextur`, Abtastung von
     `G9texturabtastung`, 2048²) — die Nahaufnahme schlägt das Ganzkörperbild
     über die absolute Pixeldichte. Ein Nebenbild mit Körperteil färbt nur
     dieses Teil (`punkte`).
     Die Texel liegen über `G9flaechenpaarung` AUF dem SMPL-X-Netz (Dreieck +
     Anteile je Käfigpunkt; der nächste Punkt allein macht ein Mosaik).
  2. Punkte auf den Genesis-Käfig über die Netzpaarung (`zuordnung`), Lücken
     über die Käfigkanten füllen (`G9restmorph.glaetten`) — die Füllschicht
     unter der HD-Schicht.
  3. `G9texturbacken`: Albedo der Grundhaut (auf den Stufe-1-Ton getönt),
     darüber die Punktfarben (Gouraud), darüber die Texelfarben; dazu je
     Kachel die Herkunftskarte (welches Bild welche Stelle liefert).

Ergebnis `ergebnis.fototextur = {kacheln: {1001: 'fototextur_1001.jpg', …},
herkunft: {1001: 'fototextur_herkunft_1001.png'}, bilder, je_bild, texel,
punkte_mit_farbe, deckung, hautton, seite, stand}`; die Seite legt die
Kacheln als `map` auf das Modell (`texturauflage.js`) und zeigt sie unten im
Bereich „Textur" (`texturansicht.js`). Eigener Schritt `textur` im Lauf.
"""

import json
import logging
import os
import subprocess
import time

import numpy as np
from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellbildtypen import Bildmodellbildtypen
from .bildmodellmehrbild import Bildmodellmehrbild
from .bildmodelltextur import Bildmodelltextur

logger = logging.getLogger('core')

__all__ = ['Bildmodellfototextur']


class Bildmodellfototextur:
    """Fotofarben holen, paaren, backen — Schritt „textur"."""

    RUNNER = '_run_fotofarben.py'
    AUFTRAG = 'fotofarben_auftrag.json'
    FARBEN = 'fotofarben.npz'
    TEXEL = 'fototextur.npz'
    PAARUNG = 'fotofarben_paarung.npz'
    WARTEZEIT = 1800
    #: Ein Käfigpunkt gilt als gedeckt, wenn sein SMPL-X-Punkt so viel Gewicht hat.
    GEWICHT_AB = 0.05
    #: Reihenfolge, in der ein Körper-Hauptbild Referenz für die Nahaufnahmen wird.
    REFERENZ = ('vorne', 'dreiviertel', 'hinten', 'seite')

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen

    # -------------------------------------------------------------- Bilder

    @staticmethod
    def eigenes_netz(b):
        """Hat das Bild ein SMPLest-X-Netz mit Kamera (Körper-Hauptbild)?"""
        s = b.get('schaetzung') or {}
        return bool(s.get('posed_vertices_path') and s.get('backend') == 'smplest_x'
                    and s.get('cam_focal') and s.get('processed_bbox'))

    def referenz(self):
        """Das Körper-Hauptbild, gegen dessen Netz die Nahaufnahmen registriert werden."""
        kandidaten = [b for b in self.job.bilder
                      if b.get('kategorie') == 'koerper' and self.eigenes_netz(b)
                      and Bildmodellbildtypen.fuer_form(b)]
        if not kandidaten:
            return None
        rang = {a: i for i, a in enumerate(self.REFERENZ)}
        kandidaten.sort(key=lambda b: (rang.get(b.get('ansicht'), 9), -float(b.get('gewicht') or 0)))
        return kandidaten[0]

    def bilder(self):
        """Alle gewählten Bilder, die projizierbar sind: eigenes Netz oder ein Rig."""
        aus = []
        for b in self.job.bilder:
            if b.get('video') or not Bildmodelltextur.gewaehlt(b):
                continue
            if b.get('kategorie') == 'neben' and not Bildmodellbildtypen.textur_teile(b):
                continue
            if not (self.eigenes_netz(b) or (b.get('rigs') or {}) or b.get('gesicht68')):
                continue
            aus.append(b)
        return aus

    @staticmethod
    def punkte_je_teil(paarung, teile):
        """Die SMPL-X-Punkte der Körperteile (`G9koerperteile.TEILE`) — für ein Nebenbild."""
        from Genesis9.koerperteile import G9koerperteile

        nummern = [G9koerperteile.NUMMER[t] for t in teile if t in G9koerperteile.NUMMER]
        teil = np.asarray(paarung.neutral.teil)
        return [int(i) for i in np.where(np.isin(teil, nummern))[0]]

    # ------------------------------------------------------------- Runner

    def _eintrag(self, b, paarung):
        e = {
            'datei': str(self.ablage.zuschnitt() / b['datei']),
            'gewicht': float(b.get('gewicht') or 1.0) or 1.0,
            'rigs': {k: v for k, v in (b.get('rigs') or {}).items() if v},
            'gesicht68': b.get('gesicht68'),
            'haende': [{k: h.get(k) for k in ('seite', 'guete', 'bild')}
                       for h in (b.get('haende_punkte') or [])],
            'breite': int(b.get('breite') or 0),
            'hoehe': int(b.get('hoehe') or 0),
            'eigene': bool(b.get('kategorie') == 'koerper' and self.eigenes_netz(b)),
        }
        if self.eigenes_netz(b):
            e['posed'] = str(self.ablage.schaetzung() / b['schaetzung']['posed_vertices_path'])
            e['schaetzung'] = b['schaetzung']
        teile = Bildmodellbildtypen.textur_teile(b)
        if teile:
            # Ein Nebenbild färbt nur die Punkte seines Teils (Oberkörper, Rücken, Hände …).
            e['punkte'] = self.punkte_je_teil(paarung, teile)
        return e

    def _auftrag(self, bilder, paarung, abtastung):
        from Genesis9.flaechenpaarung import G9flaechenpaarung

        ordner = self.ablage.ergebnis()
        G9flaechenpaarung.holen().speichern(ordner / self.PAARUNG)
        auftrag = {
            'bilder': [self._eintrag(b, paarung) for b in bilder],
            'ausgabe': str(ordner / self.FARBEN),
        }
        ref = self.referenz()
        if ref is not None:
            auftrag['referenz'] = {
                'datei': ref['datei'],
                'posed': str(self.ablage.schaetzung() / ref['schaetzung']['posed_vertices_path']),
            }
        if abtastung is not None:
            auftrag['abtastung'] = str(abtastung.pfad(abtastung.seite))
            auftrag['paarung'] = str(ordner / self.PAARUNG)
            auftrag['ausgabe_textur'] = str(ordner / self.TEXEL)
        pfad = ordner / self.AUFTRAG
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump(auftrag, f)
        return pfad

    def fotofarben(self, bilder, paarung, abtastung, melder=None):
        """`(farbe (10475, 3), gewicht (10475,), antwort)` aus dem python10-Lauf."""
        pfad = self._auftrag(bilder, paarung, abtastung)
        prozess = subprocess.Popen(
            [settings.PIPELINE_PYTHON, os.path.join(Wrapperpfad.pfad(), self.RUNNER), str(pfad)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=Wrapperpfad.pfad(),
        )
        try:
            aus, fehler = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired:
            prozess.kill()
            raise RuntimeError('Fotofarben: keine Antwort nach %d s' % self.WARTEZEIT) from None
        antwort = Bildmodellmehrbild.antwort(aus)
        if not antwort or 'error' in antwort:
            raise RuntimeError('Fotofarben: %s' % ((antwort or {}).get('error') or (fehler or '')[-400:]))
        with np.load(self.ablage.ergebnis() / self.FARBEN) as d:
            return d['farbe'].astype(float), d['gewicht'].astype(float), antwort

    # ------------------------------------------------------------- Backen

    def backen(self, melder=None):
        """Alles in einem: Runner, Paarung, Kacheln. None ohne taugliche Bilder."""
        from Genesis9.netzpaarung import G9netzpaarung
        from Genesis9.restmorph import G9restmorph
        from Genesis9.texturabtastung import G9texturabtastung
        from Genesis9.texturbacken import G9texturbacken

        bilder = self.bilder()
        if not bilder:
            return None
        if melder:
            melder(0.02, 'Texturabtastung (%d²)' % G9texturabtastung.SEITE)
        abtastung = G9texturabtastung.holen()
        paarung = G9netzpaarung.holen()
        if melder:
            melder(0.05, 'Fotofarben aus %d Bildern (python10)' % len(bilder))
        farbe, gewicht, antwort = self.fotofarben(bilder, paarung, abtastung, melder)
        zu = np.asarray(paarung.zuordnung, dtype=np.int64)
        gepaart = np.asarray(paarung.gewicht, dtype=float) > 0
        kaefig = np.where(gepaart[:, None], farbe[np.clip(zu, 0, len(farbe) - 1)], 0.0)
        deckung = np.where(gepaart, gewicht[np.clip(zu, 0, len(gewicht) - 1)], 0.0)
        gedeckt = deckung >= self.GEWICHT_AB
        if melder:
            melder(0.6, 'Lücken füllen (%d von %d Punkten gedeckt)' % (int(gedeckt.sum()), len(gedeckt)))
        # Lücken: ungedeckte Punkte nehmen den Mittelwert ihrer Nachbarn (Kanten des Käfigs);
        # die Deckung läuft über dieselben Kanten aus (weicher Rand statt harter Kante).
        gewicht_feld = gedeckt.astype(float)
        gefuellt = G9restmorph.glaetten(kaefig, gewicht_feld, schritte=0)
        feder = G9restmorph.glaetten(np.repeat(gewicht_feld[:, None], 3, axis=1), gewicht_feld,
                                     schritte=0)[:, 0]
        alpha = np.clip((feder - 0.2) / 0.8, 0.0, 1.0)
        hautton = Bildmodelltextur.hautton(self.job.bilder).get('hautton')
        hd = None
        texel_pfad = self.ablage.ergebnis() / self.TEXEL
        if antwort.get('texel') and texel_pfad.is_file():
            with np.load(texel_pfad) as d:
                hd = {k: d[k] for k in d.files}
        if melder:
            melder(0.7, 'Kacheln backen (%d²)' % abtastung.seite)
        kacheln, herkunft = G9texturbacken(abtastung.seite).backen(
            gefuellt, alpha, self.ablage.ergebnis(), 'fototextur', hautton, hd)
        texel = antwort.get('texel') or {}
        aus = {
            'kacheln': {str(k): os.path.basename(v) for k, v in kacheln.items()},
            'herkunft': {str(k): os.path.basename(v) for k, v in herkunft.items()},
            'bilder': len(bilder),
            'referenz': (self.referenz() or {}).get('datei'),
            'je_bild': antwort.get('je_bild'),
            'punkte_mit_farbe': int(antwort.get('punkte_mit_farbe') or 0),
            'deckung': round(float(gedeckt.mean()), 3),
            'deckung_hd': round(float(texel.get('gedeckt', 0)) / max(1, int(texel.get('gesamt', 0) or 1)), 3),
            'seite': abtastung.seite,
            'hautton': hautton,
            'stand': int(time.time()),
        }
        logger.info('Bildmodell %s: Fototextur %s', self.job.kennung,
                    {k: v for k, v in aus.items() if k != 'je_bild'})
        return aus
