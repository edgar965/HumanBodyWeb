# -*- coding: utf-8 -*-
"""Bildmodellfototextur — Textur Stufe 2: Fotofarben je Käfigpunkt, als UDIM gebacken.

Edgar (19.09.2026): „Überlege auch ob eine Textur möglich wäre. Du hast doch
aus unterschiedlichen Bereichen Textur infos." Stufe 1 tönt die Daz-Haut
(`Bildmodelltextur`, Hautton). Stufe 2 nimmt die Farbe der Fotos selbst:

  1. `_run_fotofarben.py` (python10): je Hauptbild mit Häkchen „Textur" das
     posierte SMPL-X-Netz des Schätzers ins Bild projizieren, Tiefentest,
     Personenmaske, Sichtwinkel → Farbe und Gewicht je SMPL-X-Punkt. Ein
     Nebenbild mit Körperteil (`Bildmodellbildtypen`, 19.09.2026) geht mit
     seiner Punktmenge (`punkte`) hinein und färbt nur dieses Teil.
  2. Auf den Genesis-Käfig über die Netzpaarung (`zuordnung`: je Käfigpunkt
     sein SMPL-X-Punkt), Lücken über die Käfigkanten aus den Nachbarn füllen
     (`G9restmorph.nachbarmittel`, wie beim Restmorph).
  3. `G9texturbacken`: je UDIM-Kachel die Käfigdreiecke im UV-Raum mit
     Punktfarben rastern, Deckung als Alpha, Rand ausgeweitet; darüber die
     Daz-Albedo der Grundhaut (Stufe-1-Ton auf den ungedeckten Stellen).

Ergebnis `ergebnis.fototextur = {kacheln: {1001: 'fototextur_1001.jpg', …},
bilder, punkte_mit_farbe, deckung}`; die Seite legt die Kacheln als `map`
auf die Gruppen des Modells (`texturauflage.js`), das Modell trägt sie in
`figur.fototextur` (Pfade im Auftrag). Option `textur = foto`.
"""

import json
import logging
import os
import subprocess

import numpy as np
from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellbildtypen import Bildmodellbildtypen
from .bildmodellmehrbild import Bildmodellmehrbild
from .bildmodelltextur import Bildmodelltextur

logger = logging.getLogger('core')

__all__ = ['Bildmodellfototextur']


class Bildmodellfototextur:
    """Fotofarben holen, paaren, backen — im Schritt Vorschau."""

    RUNNER = '_run_fotofarben.py'
    AUFTRAG = 'fotofarben_auftrag.json'
    FARBEN = 'fotofarben.npz'
    WARTEZEIT = 900
    #: Ein Käfigpunkt gilt als gedeckt, wenn sein SMPL-X-Punkt so viel Gewicht hat.
    GEWICHT_AB = 0.05

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen

    def bilder(self):
        """Die Hauptbilder mit Häkchen und posiertem Netz — und die Nebenbilder mit Körperteil."""
        aus = []
        for b in self.job.bilder:
            s = b.get('schaetzung') or {}
            if not Bildmodelltextur.gewaehlt(b) or not s.get('posed_vertices_path'):
                continue
            if s.get('backend') != 'smplest_x' or not s.get('cam_focal') or not s.get('processed_bbox'):
                continue
            if b.get('kategorie') == 'neben' and not Bildmodellbildtypen.textur_teile(b):
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

    def _auftrag(self, bilder):
        from Genesis9.netzpaarung import G9netzpaarung

        eintraege = []
        for b in bilder:
            e = {
                'datei': str(self.ablage.zuschnitt() / b['datei']),
                'posed': str(self.ablage.schaetzung() / b['schaetzung']['posed_vertices_path']),
                'schaetzung': b['schaetzung'],
                'gewicht': float(b.get('gewicht') or 1.0) or 1.0,
            }
            teile = Bildmodellbildtypen.textur_teile(b)
            if teile:
                # Ein Nebenbild färbt nur die Punkte seines Teils (Oberkörper, Rücken, Hände …).
                e['punkte'] = self.punkte_je_teil(G9netzpaarung.holen(), teile)
            eintraege.append(e)
        pfad = self.ablage.ergebnis() / self.AUFTRAG
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump({'bilder': eintraege, 'ausgabe': str(self.ablage.ergebnis() / self.FARBEN)}, f)
        return pfad

    def fotofarben(self, bilder, melder=None):
        """`(farbe (10475, 3), gewicht (10475,), antwort)` aus dem python10-Lauf."""
        pfad = self._auftrag(bilder)
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
        from Genesis9.texturbacken import G9texturbacken

        bilder = self.bilder()
        if not bilder:
            return None
        if melder:
            melder(0.05, 'Fotofarben aus %d Bildern (python10)' % len(bilder))
        farbe, gewicht, antwort = self.fotofarben(bilder, melder)
        paarung = G9netzpaarung.holen()
        zu = np.asarray(paarung.zuordnung, dtype=np.int64)
        gepaart = np.asarray(paarung.gewicht, dtype=float) > 0
        kaefig = np.where(gepaart[:, None], farbe[np.clip(zu, 0, len(farbe) - 1)], 0.0)
        deckung = np.where(gepaart, gewicht[np.clip(zu, 0, len(gewicht) - 1)], 0.0)
        gedeckt = deckung >= self.GEWICHT_AB
        if melder:
            melder(0.55, 'Lücken füllen (%d von %d Punkten gedeckt)' % (int(gedeckt.sum()), len(gedeckt)))
        # Lücken: ungedeckte Punkte nehmen den Mittelwert ihrer Nachbarn (Kanten des Käfigs);
        # die Deckung läuft über dieselben Kanten aus (weicher Rand statt harter Kante).
        gewicht_feld = gedeckt.astype(float)
        gefuellt = G9restmorph.glaetten(kaefig, gewicht_feld, schritte=0)
        feder = G9restmorph.glaetten(np.repeat(gewicht_feld[:, None], 3, axis=1), gewicht_feld,
                                     schritte=0)[:, 0]
        alpha = np.clip((feder - 0.2) / 0.8, 0.0, 1.0)
        hautton = Bildmodelltextur.hautton(self.job.bilder).get('hautton')
        if melder:
            melder(0.7, 'Kacheln backen')
        kacheln = G9texturbacken().backen(gefuellt, alpha, self.ablage.ergebnis(), 'fototextur', hautton)
        aus = {
            'kacheln': {str(k): os.path.basename(v) for k, v in kacheln.items()},
            'bilder': len(bilder),
            'je_bild': antwort.get('je_bild'),
            'punkte_mit_farbe': int(antwort.get('punkte_mit_farbe') or 0),
            'deckung': round(float(gedeckt.mean()), 3),
            'hautton': hautton,
        }
        logger.info('Bildmodell %s: Fototextur %s', self.job.kennung,
                    {k: v for k, v in aus.items() if k != 'je_bild'})
        return aus
