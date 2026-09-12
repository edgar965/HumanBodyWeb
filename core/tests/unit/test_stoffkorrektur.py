# -*- coding: utf-8 -*-
u"""`Stoffkorrektur`: eingesunkene Stoffpunkte aus dem Koerper holen.

WARUM (06.09.2026, Edgar: „das T-Shirt geht IN den Koerper hinein"):
Die Simulation haelt 2,5 mm Abstand (`body_collision_thickness`), und alles,
was spitzer aus dem MB-Lab-Netz ragt, steht hindurch. Auf GarmentCodes glattem
`mean_all` passiert das nicht — dort stecken 2 von 4.556 Punkten im Stoff, bei
uns waren es 228 von 1.159.

Geprueft wird an einer KUGEL, nicht am echten Koerper: Bei einer Kugel ist die
richtige Antwort ausrechenbar (Abstand zum Mittelpunkt), und der Test bleibt
unabhaengig von Morphdaten und Netzdateien.

    1. Ein Punkt IM Koerper kommt heraus — und zwar auf die geforderte Hoehe.
    2. Ein Punkt weit AUSSERHALB bleibt, wo er ist. Sonst wuerde die
       Korrektur die Falten der Simulation glattziehen.
    3. Kein Punkt wandert weiter als `HUB_MAX_MM`. Ohne diesen Deckel
       schob ein Kragenpunkt 123,65 mm weit, weil ZAEHNE im Kopf in seinen
       Umkreis fielen.
    4. Die Korrektur laesst das Netz zusammenhaengend: Nachbarpunkte duerfen
       nicht auseinanderreissen (dagegen glaettet `_verteilen`).
"""
import sys

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

sys.path.insert(0, str(settings.HUMANBODY_ROOT)) if hasattr(
    settings, 'HUMANBODY_ROOT') else None

from GarmentCode.stoffkorrektur import Stoffkorrektur      # noqa: E402


def kugel(radius=0.5, feinheit=16):
    u"""Eine Kugel als Koerper: Punkte, Vierecke, Normalen nach aussen."""
    theta = np.linspace(0.001, np.pi - 0.001, feinheit)
    phi = np.linspace(0, 2 * np.pi, feinheit, endpoint=False)
    t, p = np.meshgrid(theta, phi, indexing='ij')
    punkte = np.stack([np.sin(t) * np.cos(p), np.sin(t) * np.sin(p),
                       np.cos(t)], axis=-1).reshape(-1, 3) * radius
    flaechen = []
    for i in range(feinheit - 1):
        for j in range(feinheit):
            a = i * feinheit + j
            b = i * feinheit + (j + 1) % feinheit
            # Wickelrichtung nach AUSSEN: `[a, b, b+n, a+n]` ergaebe
            # e_phi x e_theta = -e_r, also Normalen nach innen — daran ist
            # die erste Fassung dieses Tests gescheitert.
            flaechen.append([a, a + feinheit, b + feinheit, b])
    return punkte, np.array(flaechen)


class StoffkorrekturTest(SimpleTestCase):
    u"""Die Korrektur an einem Fall, dessen Antwort ausrechenbar ist."""

    databases = set()
    RADIUS = 0.5

    def setUp(self):
        self.koerper, self.flaechen = kugel(self.RADIUS)

    def _korrektur(self, stoffpunkte, dreiecke):
        return Stoffkorrektur.aus_netz(self.koerper, self.flaechen, dreiecke)

    def _drei_punkte(self, tiefe):
        u"""Einer `tiefe` Meter im Koerper, zwei sauber aussen."""
        return (np.array([[0.0, 0.0, self.RADIUS - tiefe],
                          [0.06, 0.0, self.RADIUS + 0.01],
                          [-0.06, 0.0, self.RADIUS + 0.01]]),
                np.array([[0, 1, 2]]))

    def test_eingesunkener_punkt_kommt_heraus(self):
        u"""Ein normal tief eingesunkener Punkt landet VOR der Oberflaeche.

        8 mm ist der realistische Fall: Am echten Koerper lag der mittlere
        Durchstich bei 2,7 mm, der tiefste bei 22 mm.
        """
        punkte, dreiecke = self._drei_punkte(0.008)
        neu, bilanz = self._korrektur(punkte, dreiecke).anwenden(
            neu_punkte(punkte))

        self.assertGreaterEqual(bilanz['eingesunken'], 1,
                                'der eingesunkene Punkt wurde nicht erkannt')
        abstand = np.linalg.norm(neu[0]) - self.RADIUS
        self.assertGreater(abstand, 0,
                           'der Punkt steckt nach der Korrektur immer noch drin')

    def test_sehr_tiefer_punkt_kommt_wenigstens_naeher(self):
        u"""Bei 20 mm greift der Deckel — dann zaehlt die Richtung.

        Vollstaendig herauszuholen waeren 23 mm noetig, erlaubt sind
        `HUB_MAX_MM`. Der Punkt muss dann wenigstens deutlich naeher an die
        Oberflaeche kommen und darf auf keinen Fall tiefer sinken (genau das
        tat er, solange entlang der STOFFnormale geschoben wurde: aus 20 mm
        wurden 35 mm).
        """
        punkte, dreiecke = self._drei_punkte(0.020)
        neu, _ = self._korrektur(punkte, dreiecke).anwenden(neu_punkte(punkte))
        vorher = self.RADIUS - float(np.linalg.norm(punkte[0]))
        nachher = self.RADIUS - float(np.linalg.norm(neu[0]))
        self.assertLess(nachher, vorher,
                        'der Punkt ist nicht naeher an die Oberflaeche gekommen')
        self.assertLess(nachher, 0.006,
                        'der Deckel haette mehr als 14 mm hergeben muessen')

    def test_falsch_gewickeltes_netz_wird_erkannt(self):
        u"""Auch ein nach INNEN gewickelter Koerper wird richtig behandelt.

        Die Wickelrichtung sieht man einem Netz nicht an, und `vertex_normals`
        folgt ihr blind. Zeigen die Normalen nach innen, schiebt die Korrektur
        den Stoff HINEIN: aus 20 mm Einsinken wurden 35 mm. Genau daran ist
        die erste Fassung dieses Tests gescheitert — mit einer Kugel, die
        versehentlich falsch gewickelt war.
        """
        # Dieselbe Kugel, Wickelrichtung umgedreht.
        punkte_k, flaechen = kugel(self.RADIUS)
        verdreht = flaechen[:, ::-1]
        punkte, dreiecke = self._drei_punkte(0.008)
        korrektur = Stoffkorrektur.aus_netz(punkte_k, verdreht, dreiecke)
        neu, _ = korrektur.anwenden(neu_punkte(punkte))
        abstand = np.linalg.norm(neu[0]) - self.RADIUS
        self.assertGreater(abstand, 0,
                           'bei umgekehrter Wickelrichtung schiebt die '
                           'Korrektur den Stoff in den Koerper')

    def test_freier_punkt_bleibt_liegen(self):
        u"""Was weit weg haengt, wird nicht angefasst — sonst Falten weg."""
        frei = np.array([[0.0, 0.0, self.RADIUS + 0.30]])
        dreiecke = np.zeros((0, 3), dtype=int)
        neu, _ = self._korrektur(frei, dreiecke).anwenden(neu_punkte(frei))
        self.assertLess(float(np.linalg.norm(neu[0] - frei[0])), 1e-9)

    def test_niemand_wandert_weiter_als_der_deckel(self):
        u"""Auch ein Punkt tief im Inneren bleibt am Deckel."""
        tief = np.array([[0.0, 0.0, 0.0],                 # Mittelpunkt
                         [0.0, 0.0, self.RADIUS + 0.01]])
        dreiecke = np.zeros((0, 3), dtype=int)
        neu, bilanz = self._korrektur(tief, dreiecke).anwenden(neu_punkte(tief))
        weg = np.linalg.norm(neu - tief, axis=1) * 1000
        self.assertLessEqual(float(weg.max()),
                             Stoffkorrektur.HUB_MAX_MM + 1e-6)
        self.assertLessEqual(bilanz['groesster_weg_mm'],
                             Stoffkorrektur.HUB_MAX_MM + 0.01)

    def test_netz_reisst_nicht_auf(self):
        u"""Nachbarn bleiben Nachbarn — die Verschiebung wird verteilt."""
        # Eine Reihe von Punkten dicht ueber der Kugel; einer steckt drin.
        winkel = np.linspace(-0.3, 0.3, 9)
        punkte = np.stack([np.sin(winkel) * (self.RADIUS + 0.005),
                           np.zeros_like(winkel),
                           np.cos(winkel) * (self.RADIUS + 0.005)], axis=-1)
        punkte[4] *= (self.RADIUS - 0.015) / (self.RADIUS + 0.005)
        dreiecke = np.array([[i, i + 1, (i + 2) % len(punkte)]
                             for i in range(len(punkte) - 2)])
        vorher = np.linalg.norm(np.diff(punkte, axis=0), axis=1)
        neu, _ = self._korrektur(punkte, dreiecke).anwenden(neu_punkte(punkte))
        nachher = np.linalg.norm(np.diff(neu, axis=0), axis=1)
        # Keine Kante darf sich mehr als verdoppeln.
        self.assertLess(float((nachher / vorher).max()), 2.0,
                        'die Korrektur reisst das Netz auseinander')


def neu_punkte(a):
    u"""Kopie, damit ein Test die Vorlage des naechsten nicht veraendert."""
    return np.asarray(a, dtype=np.float64).copy()
