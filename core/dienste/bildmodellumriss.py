# -*- coding: utf-8 -*-
"""Bildmodellumriss — die Silhouetten der Fotos formen das Zielnetz Zeile für Zeile.

Edgar (19.09.2026, Testfall Ursula, „mach"): Nach den 19 Fotomaßen stimmten
die Zahlen, nicht die Form (RMS 11,5 mm, Brust kleiner, Rumpf weniger rund).
`G9umrissformung` überträgt den ganzen Umriss — Breitenprofil von vorn und
hinten, Vorder- und Rückkante von der Seite — auf den Käfig (Wahrheitsprobe
an Ursulas eigenem Umriss, Grundfigur → Ursula, Flächenabstand: Rumpf 10,2 →
5,2 mm, Becken 9,9 → 5,6, Oberschenkel 7,5 → 5,8, Unterschenkel 2,9 → 1,4).

Diese Klasse sucht die Fotos heraus (Hauptbilder des Körpers, neutral stehend,
für die Form gewählt: vorn/hinten für die Breiten, Seite für die Tiefen), baut
aus jedem Sichtungseintrag das Profil, wie die Formung es braucht, und SPERRT
Zeilen, in denen ein Arm die Silhouette macht:

  vorn/hinten   Zeilen, in denen die Arm-Kette (Schulter–Ellbogen–Handgelenk,
                um eine Handlänge verlängert) oder ein Handpunkt im Rumpfsegment
                liegt (`G9silhouettenmasse._arm_im_segment`, je Zeile)
  seite         Zeilen, in denen Ellbogen oder Handgelenk näher als 3 % der
                Höhe an der Vorder- oder Rückkante steht — dort ist die Kante
                der Arm, nicht der Rumpf; wohin die Person schaut, sagt die
                Nase gegen die Schulter (`front_links`)

Läuft im Schritt „Anpassung" VOR den Proportionen (Option `umriss`, Vorgabe
an); Bericht in `ergebnis.anpassung.umriss`.
"""

import logging

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellbildtypen import Bildmodellbildtypen

logger = logging.getLogger('core')

__all__ = ['Bildmodellumriss']


class Bildmodellumriss:
    OPTION = 'umriss'
    SICHT = 0.3
    NASE, SCHULTERN, ARMPUNKTE = 0, (5, 6), (7, 8, 9, 10)
    KANTENRAND = 0.03

    def __init__(self, job, optionen):
        self.job = job
        self.optionen = optionen or {}

    @classmethod
    def an(cls, optionen, job=None):
        wert = (optionen or {}).get(cls.OPTION)
        if wert is None and job is not None:
            wert = (job.optionen or {}).get(cls.OPTION)
        return (wert or 'an') != 'aus'

    # ------------------------------------------------------------- Fotos

    def bilder(self, ansichten):
        return [
            b for b in self.job.bilder
            if b.get('kategorie') == 'koerper' and b.get('ansicht') in ansichten
            and b.get('haltung') == 'neutral' and Bildmodellbildtypen.fuer_form(b)
            and (b.get('textur') or {}).get('profil') and b.get('hoehe') and b.get('breite')
        ]

    @staticmethod
    def _rig(b):
        return ((b.get('rigs') or {}).get('yolo') or {}).get('punkte')

    def profil_vorn(self, b):
        """Profil eines Vorder-/Rückbildes mit gesperrten Zeilen (Arm im Segment)."""
        from Genesis9.silhouettenmasse import G9silhouettenmasse

        profil = dict(b['textur']['profil'])
        profil.update({'breite': b['breite'], 'hoehe': b['hoehe'], 'gesperrt': set()})
        rig = self._rig(b)
        if not rig:
            return profil
        n = len(profil['breiten'])
        hoch = float(profil['unten'] - profil['oben'] + 1)
        haende = [h.get('bild') or [] for h in (b.get('haende_punkte') or [])]
        for i in range(n):
            if G9silhouettenmasse._arm_im_segment(profil, rig, float(b['hoehe']), hoch, i / n, (i + 1) / n,
                                                  haende):
                profil['gesperrt'].add(i)
        return profil

    def profil_seite(self, b):
        """Profil eines Seitenbildes: `front_links` aus Nase und Schulter; ein Arm an der Kante sperrt."""
        profil = dict(b['textur']['profil'])
        profil.update({'breite': b['breite'], 'hoehe': b['hoehe'], 'gesperrt': set(), 'front_links': True})
        rig = self._rig(b)
        if not rig:
            return profil
        nase = rig[self.NASE] if rig[self.NASE][2] >= self.SICHT else None
        schultern = [rig[i][0] for i in self.SCHULTERN if rig[i][2] >= self.SICHT]
        if nase is None or not schultern:
            lm = b.get('landmarken') or []
            if len(lm) >= 13 and lm[0][2] >= self.SICHT:
                nase, schultern = lm[0], [lm[11][0], lm[12][0]]
        if nase is not None and schultern:
            profil['front_links'] = nase[0] < float(np.mean(schultern))
        from Genesis9.fotoproportionen import G9fotoproportionen

        n = len(profil['breiten'])
        hoch = float(profil['unten'] - profil['oben'] + 1)
        rand = self.KANTENRAND * hoch / float(b['breite'])  # als Bildbreitenanteil
        # Handpunkte (MediaPipe) an der Kante: der Daumen der A-Stellung ragt vor das Gesaess.
        profil['gesperrt'] |= G9fotoproportionen(b).hand_an_kante(self.KANTENRAND)
        for i in self.ARMPUNKTE:
            x, y, c = rig[i]
            if c < self.SICHT:
                continue
            zeile = int((y * float(b['hoehe']) - profil['oben']) / hoch * n)
            for j in range(max(0, zeile - 1), min(n, zeile + 2)):
                links, rechts = profil['links'][j], profil['rechts'][j]
                if links is None:
                    continue
                if abs(x - links) < rand or abs(x - rechts) < rand:
                    profil['gesperrt'].add(j)
        return profil

    # ------------------------------------------------------------- Formen

    def formen(self, punkte, gelenke):
        """`(punkte, gelenke, bericht)` — unverändert und `bericht` None, wenn aus oder ohne Fotos."""
        if not self.an(self.optionen, self.job):
            return punkte, gelenke, None
        vorn = [self.profil_vorn(b) for b in self.bilder(('vorne', 'hinten'))]
        seite = [self.profil_seite(b) for b in self.bilder(('seite',))]
        if not vorn and not seite:
            return punkte, gelenke, None
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile
        from Genesis9.umrissformung import G9umrissformung

        hoehe = ((self.job.ergebnis or {}).get('ziel') or {}).get('hoehe_ziel_cm')
        with Wrapperpfad():
            teil = G9koerperteile.genesis_punkte(G9haut.holen())
            p, g, bericht = G9umrissformung(teil).formen(
                punkte, gelenke, vorn=vorn, seite=seite, hoehe_m=(hoehe / 100.0) if hoehe else None)
        bericht['gesperrt'] = {'vorn': [len(pr['gesperrt']) for pr in vorn],
                               'seite': [len(pr['gesperrt']) for pr in seite]}
        logger.info('Bildmodell %s: Umriss geformt: %s', self.job.kennung, bericht)
        return p, g, bericht
