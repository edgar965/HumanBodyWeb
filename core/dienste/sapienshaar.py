# -*- coding: utf-8 -*-
"""Sapienshaar — die Haarmaske aus der Sapiens-Klasse „Hair" statt (oder zusätzlich zu) der Farbe (05.10.2026).

Edgar (05.10.2026, am Bild der Seitenansicht): „Haar textur noch auf dem Kopf" und „die Haare sind bei Sapiens noch keine Objekte". Sapiens kennt das Haar als eigene Klasse (`Hair`); der Schritt
„Segmentierung" legt die Stimmen je Klasse auf die Flächen des Netzes (`arbeit/sapiens_flaechen.npz`, `klassen`), und `Sapiensmaske` macht daraus je Fläche „Haar" (Mehrheit nach dem Glätten über die
Kantennachbarn). Der Schritt „haar" der Körper-Kette (`Meshfigurhaar`) rechnet seine Maske bisher nur aus Farbe und Lage (`Haar.haarmaske.Haarmaske`: Helligkeit gegen Hautton, Gesichtszone, Bartzone);
diese Klasse legt Sapiens darüber, je nach Option `segmentierung.haar`:

    farbe     nichts — die Maske der Farbe gilt (Vorgabe, wie bisher)
    sapiens   wo Sapiens die Fläche sieht (genug Stimmen), entscheidet Sapiens; sonst die Farbe
    beide     Haar ist, was die Farbe ODER Sapiens als Haar sieht

Geschützt bleibt in jedem Fall, was die Haarmaske selbst schützt: das Innere des Gesichts (`geschuetzt`), die Bartzone (`bart` — der Bart ist KEIN Haar), alles unter der Schnittebene des Kopfnetzes
(`unten`). Fehlen die Stimmen oder gehören sie nicht zu diesem Netz und diesen Einstellungen, gilt die Farbe und der Grund steht im Bericht (`ergebnis.haar.sapiens.grund`) — nie ein stilles Zurückfallen
(`artefakte-benennen.md`). Der Bericht nennt beide Flächen (cm²) und ihre Überschneidung: ob Sapiens das Haar besser trifft als die Farbe, ist damit sichtbar, aber nicht entschieden.
"""

import logging

import numpy as np

from .engine2d3dkleidersegmentierungsoptionen import Engine2d3dKleidersegmentierungsoptionen

logger = logging.getLogger('core')

__all__ = ['Sapienshaar']


class Sapienshaar:
    QUELLEN = Engine2d3dKleidersegmentierungsoptionen.HAAR_QUELLEN

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    def quelle(self):
        """`farbe` | `sapiens` | `beide` — „Mesh to 3D" hat `sapiens_haar` nicht und bleibt bei der Farbe."""
        wahl = getattr(self.lauf, 'sapiens_haar', 'farbe')
        return wahl if wahl in self.QUELLEN else 'farbe'

    def anwenden(self, maske, haarmaske, anzahl_flaechen):
        """Ändert `maske['haar']` an Ort und Stelle und gibt den Bericht zurück (None bei Quelle „farbe"). `haarmaske`: die `Haarmaske` (Kantennachbarn, Flächeninhalt)."""
        wahl = self.quelle()
        if wahl == 'farbe':
            return None
        from Kleidung.sapiensmaske import Sapiensmaske
        from Kleidung.sapienszuordnung import Sapienszuordnung

        einstellungen = getattr(self.lauf, 'sapiens_einstellungen', None) or {}
        netz = self.ablage.netzdatei(original=True)             # die Stimmen gehören zum Netz des Schritts „netz", nicht zum Tiefennetz
        try:
            klassen = Sapiensmaske.laden(self.ablage.arbeit(), netz, anzahl_flaechen, Engine2d3dKleidersegmentierungsoptionen.rechenoptionen(einstellungen))
        except Sapiensmaske.Unbrauchbar as grund:
            logger.warning('Haar %s: Sapiens-Haar nicht benutzt (%s) — die Farbe gilt', self.job.kennung, grund)
            return {'quelle': wahl, 'verwendet': False, 'grund': str(grund)}
        stimmen = Sapienszuordnung.stimmen(klassen, einstellungen)
        sapiens, gesehen = Sapiensmaske.haar_aus(stimmen, haarmaske.nachbarn(), **{k: v for k, v in Sapiensmaske.aus_optionen(einstellungen).items() if k != 'nah_m'})
        alt = np.asarray(maske['haar'], dtype=bool)
        erlaubt = ~np.asarray(maske['geschuetzt'], dtype=bool) & ~np.asarray(maske['bart'], dtype=bool) & ~np.asarray(maske['unten'], dtype=bool)
        sapiens = sapiens & erlaubt                                 # geschützte Zonen sind auch für Sapiens kein Haar
        # „sapiens": wo Sapiens die Fläche sieht, entscheidet es; sonst die Farbe. „beide": die Vereinigung.
        neu = np.where(gesehen, sapiens, alt) if wahl == 'sapiens' else (alt | sapiens)
        maske['haar'] = neu
        cm2 = np.asarray(haarmaske.inhalt, dtype=np.float64) * 1e4
        return {'quelle': wahl, 'verwendet': True, 'flaechen_gesehen': int(gesehen.sum()),
                'farbe': self._zahlen(alt, cm2), 'sapiens': self._zahlen(sapiens, cm2), 'ergebnis': self._zahlen(neu, cm2),
                'beide_flaechen': int((alt & sapiens).sum()), 'geaendert_flaechen': int((neu != alt).sum()),
                'hinzu_flaechen': int((neu & ~alt).sum()), 'weg_flaechen': int((~neu & alt).sum())}

    @staticmethod
    def _zahlen(wahl, cm2):
        return {'flaechen': int(wahl.sum()), 'cm2': round(float(cm2[wahl].sum()), 0)}
