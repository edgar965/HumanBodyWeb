# -*- coding: utf-8 -*-
"""„Mesh to 3D" / „2D3D Kleider": Kopfnetz und Körpernetz am Hals nähen (`Meshfigurnaht`, 07.10.2026).

Edgar: „baue die Pipeline um, so dass der Kopf an den Körper ‚genäht' wird." Gemessen an `Edgar - Hunyan Kopf`: Das Kopfnetz endet in einer
geschlossenen, geneigten Kappe, `Meshfigurzielnetz` behielt ihren vorderen Teil als Innenfläche im Hals, und zwischen Körper und Kopf klaffte
eine Lücke. Kunstnetze (Zylinder), keine Grafikkarte, kein Django.
"""

import unittest

import numpy as np

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

N = 48


def _orientiert(punkte, flaechen, nach_aussen):
    """Dreiecke so drehen, dass ihre Normale zu `nach_aussen(mitte)` zeigt (Vorzeichen > 0)."""
    flaechen = np.array(flaechen)
    p = punkte[flaechen]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    falsch = np.einsum('fc,fc->f', n, nach_aussen(p.mean(1))) < 0
    flaechen[falsch] = flaechen[falsch][:, ::-1]
    return flaechen


def _mantel(radius, y0, y1, ringe=4, mit_unterkante=True):
    """Zylindermantel um die Achse x = z = 0, Normalen nach außen; `(punkte, flaechen)`."""
    w = np.linspace(0, 2 * np.pi, N, endpoint=False)
    ys = np.linspace(y0, y1, ringe)
    punkte = np.array([[radius * np.cos(a), y, radius * np.sin(a)] for y in ys for a in w])
    flaechen = []
    for r in range(ringe - 1):
        for i in range(N):
            j = (i + 1) % N
            a, b, c, d = r * N + i, r * N + j, (r + 1) * N + i, (r + 1) * N + j
            flaechen += [[a, b, c], [b, d, c]]
    flaechen = _orientiert(punkte, flaechen, lambda m: m * np.array([1.0, 0, 1.0]))
    return punkte, flaechen


def _kappe(radius, y, nach_unten=True):
    """Scheibe bei Höhe `y`, Normale nach unten (die Kappe am Hals) oder nach oben; `(punkte, flaechen)`."""
    w = np.linspace(0, 2 * np.pi, N, endpoint=False)
    punkte = np.concatenate([[[0.0, y, 0.0]], [[radius * np.cos(a), y, radius * np.sin(a)] for a in w]])
    flaechen = [[0, 1 + i, 1 + (i + 1) % N] for i in range(N)]
    vorzeichen = -1.0 if nach_unten else 1.0
    return punkte, _orientiert(punkte, flaechen, lambda m: np.tile([0.0, vorzeichen, 0.0], (len(m), 1)))


def _ring(innen, aussen, y, nach_unten=True):
    """Kreisring bei Höhe `y` zwischen den Radien `innen` und `aussen` (wie die Unterseite von Kinn und Hinterkopf, berührt die Achse nicht); `(punkte, flaechen)`."""
    w = np.linspace(0, 2 * np.pi, N, endpoint=False)
    punkte = np.array([[radius * np.cos(a), y, radius * np.sin(a)] for radius in (innen, aussen) for a in w])
    flaechen = []
    for i in range(N):
        j = (i + 1) % N
        flaechen += [[i, j, N + i], [j, N + j, N + i]]
    vorzeichen = -1.0 if nach_unten else 1.0
    return punkte, _orientiert(punkte, flaechen, lambda m: np.tile([0.0, vorzeichen, 0.0], (len(m), 1)))


def _zusammen(*teile):
    """Mehrere `(punkte, flaechen)` zu einem Netz."""
    punkte, flaechen, versatz = [], [], 0
    for p, f in teile:
        punkte.append(p)
        flaechen.append(np.asarray(f) + versatz)
        versatz += len(p)
    return np.concatenate(punkte), np.concatenate(flaechen)


def _scan(punkte, flaechen, farbe):
    from meshfigur_scan import Meshfigurscan

    return Meshfigurscan(punkte, flaechen, punktfarben=np.tile(np.asarray(farbe, dtype=np.uint8), (len(punkte), 1)))


class DieKappe(unittest.TestCase):
    def setUp(self):
        from meshfigur_naht import Meshfigurnaht

        self.naht = Meshfigurnaht([0, 1.5, 0], [0, 1, 0])

    def test_nur_die_scheibe_mit_der_normale_nach_unten(self):
        mantel = _mantel(0.05, 1.55, 1.75)
        punkte, flaechen = _zusammen(mantel, _kappe(0.05, 1.55))
        kappe = self.naht.kappe(punkte, flaechen, self.naht.OHNE_KINN)
        self.assertEqual(int(kappe.sum()), N, 'genau die Scheibe')
        self.assertTrue(kappe[len(mantel[1]):].all())

    def test_gegenprobe_eine_scheibe_nach_oben_ist_keine_kappe(self):
        """Sabotage: dreht man die Normale um, darf nichts mehr als Kappe gelten — sonst prüfte der Test die Richtung nicht."""
        punkte, flaechen = _zusammen(_mantel(0.05, 1.55, 1.75), _kappe(0.05, 1.55, nach_unten=False))
        self.assertEqual(int(self.naht.kappe(punkte, flaechen, self.naht.OHNE_KINN).sum()), 0)

    def test_ueber_dem_kinn_bleibt_alles(self):
        """Eine Fläche mit der Normale nach unten, aber über der Grenze (Kinn-Unterseite), ist keine Kappe."""
        punkte, flaechen = _kappe(0.05, 1.75)
        self.assertEqual(int(self.naht.kappe(punkte, flaechen, 0.06).sum()), 0)

    def test_die_unterseite_von_kinn_und_hinterkopf_bleibt(self):
        """07.10.2026: Der Deckel berührt die Halsachse; ein Ring aus Flächen mit Normale nach unten weiter außen (Unterseite des Kopfes) gehört zum Kopf. Die alte Regel nahm beides —
        am Auftrag `2026.10.07.19.52.48` fiel so der Nacken weg (12.516 von 20.996 Flächen)."""
        deckel = _kappe(0.05, 1.55)
        ring = _ring(0.065, 0.10, 1.53)
        self.naht.KERN = 0.04          # die Fächerdreiecke dieser Scheibe liegen mit ihrer Mitte bei 3,3 cm; die echte Kappe hat Flächen bei r ≈ 1 mm (`KERN` 3 cm)
        punkte, flaechen = _zusammen(_mantel(0.05, 1.55, 1.75), deckel, ring)
        kappe = self.naht.kappe(punkte, flaechen, self.naht.OHNE_KINN)
        n_mantel = len(_mantel(0.05, 1.55, 1.75)[1])
        self.assertEqual(int(kappe.sum()), N, 'nur die Scheibe')
        self.assertTrue(kappe[n_mantel:n_mantel + N].all(), 'die Scheibe')
        self.assertFalse(kappe[n_mantel + N:].any(), 'der Ring bleibt')

    def test_gegenprobe_ohne_kern_gilt_die_alte_regel(self):
        """Sabotage: Ohne Kern (`KERN` 0) berührt keine Fläche die Achse — dann bleibt es bei der alten Regel (alles mit Normale nach unten), und der Ring wäre mit weg. Der Test davor sieht also den Unterschied."""
        punkte, flaechen = _zusammen(_mantel(0.05, 1.55, 1.75), _kappe(0.05, 1.55), _ring(0.065, 0.10, 1.53))
        self.naht.KERN = 0.0
        self.assertEqual(int(self.naht.kappe(punkte, flaechen, self.naht.OHNE_KINN).sum()), N + 2 * N)

    def test_ein_ring_allein_ist_ohne_deckel_die_alte_regel(self):
        """Findet sich kein Deckel an der Achse (nur Ring), fällt es auf die alte Regel zurück: nichts wird verschont, was vorher weg war."""
        punkte, flaechen = _ring(0.065, 0.10, 1.53)
        self.assertEqual(int(self.naht.kappe(punkte, flaechen, self.naht.OHNE_KINN).sum()), 2 * N)


class DieRinge(unittest.TestCase):
    def setUp(self):
        from meshfigur_naht import Meshfigurnaht

        self.naht = Meshfigurnaht([0, 1.5, 0], [0, 1, 0])

    def test_koerperring_misst_den_abstand_und_nennt_die_flaeche(self):
        punkte, flaechen = _mantel(0.06, 1.2, 1.78, ringe=7)            # die Ebene y = 1,5 trifft keinen Punktring
        r, flaeche = self.naht.koerperring(punkte, flaechen)
        np.testing.assert_allclose(r, 0.06, atol=1e-3)
        self.assertEqual(len(flaeche), N)
        self.assertTrue(((flaeche >= 0) & (flaeche < len(flaechen))).all())

    def test_kopfring_ist_der_rand_der_roehre_nicht_das_loch_im_gesicht(self):
        roehre = _mantel(0.05, 1.55, 1.95)
        loch_punkte, loch_flaechen = _mantel(0.01, 1.90, 1.92, ringe=2)           # ein kleines offenes Rohr, über der Grenze
        punkte, flaechen = _zusammen(roehre, (loch_punkte, loch_flaechen))
        ring = self.naht.kopfring(punkte, flaechen, self.naht.OHNE_KINN)
        self.assertIsNotNone(ring)
        np.testing.assert_allclose(ring[0], 0.05, atol=1e-3)
        np.testing.assert_allclose(ring[1], 0.05, atol=1e-3, err_msg='Höhe über der Ebene')

    def test_ohne_rand_kein_ring(self):
        """Ein geschlossenes Netz (Oktaeder mit gemeinsamen Punkten) hat keine Randkante, also keinen Ring."""
        punkte = np.array([[0.05, 1.55, 0], [-0.05, 1.55, 0], [0, 1.55, 0.05], [0, 1.55, -0.05], [0, 1.60, 0], [0, 1.50, 0]])
        flaechen = np.array([[4, 0, 2], [4, 2, 1], [4, 1, 3], [4, 3, 0], [5, 2, 0], [5, 1, 2], [5, 3, 1], [5, 0, 3]])
        self.assertIsNone(self.naht.kopfring(punkte, flaechen, self.naht.OHNE_KINN))


class DieBruecke(unittest.TestCase):
    def test_band_mit_normalen_nach_aussen_und_geschlossen(self):
        from meshfigur_naht import Meshfigurnaht

        naht = Meshfigurnaht([0, 1.5, 0], [0, 1, 0])
        # Höhe des Kopfrings überall über 0: ein Dreieck, dessen drei Punkte in der Ebene liegen (Kopfring bei Höhe 0), ist flach, seine Normale steht senkrecht und hat zur Achse hin kein Vorzeichen
        hoehe = 0.02 + 0.01 * np.sin(np.linspace(0.0, 2 * np.pi, naht.BINS, endpoint=False))
        punkte, flaechen = naht.bruecke(np.full(naht.BINS, 0.07), np.full(naht.BINS, 0.05), hoehe)
        self.assertEqual(len(flaechen), 2 * naht.BINS)
        p = punkte[flaechen]
        n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
        quer = p.mean(1) - np.array([0, 1.5, 0])
        quer[:, 1] = 0
        self.assertTrue((np.einsum('fc,fc->f', n, quer) > 0).all(), 'jede Normale zeigt von der Achse weg')
        kanten = np.sort(np.concatenate([flaechen[:, [0, 1]], flaechen[:, [1, 2]], flaechen[:, [2, 0]]]), axis=1)
        _, anzahl = np.unique(kanten, axis=0, return_counts=True)
        # Ein Band ist ein Ring: innen hängt jede Kante an zwei Flächen, nur die beiden Ränder an einer.
        self.assertEqual(int((anzahl == 1).sum()), 2 * naht.BINS)


class DasZielnetz(unittest.TestCase):
    """Körper und Kopf als EIN Ziel: ohne Kappe, mit Band, Farbe des Bandes vom Körper."""

    @staticmethod
    def _netze(kopf_unten=1.55, kopf_geschlossen=False):
        """Körper: Zylinder 1,2–1,78 m; Kopf: Röhre ab `kopf_unten` mit Kappe unten (Normale nach unten), optional oben geschlossen."""
        koerper = _scan(*_mantel(0.07, 1.2, 1.78, ringe=7), (200, 150, 120))
        teile = [_mantel(0.05, kopf_unten, 1.95), _kappe(0.05, kopf_unten)]
        if kopf_geschlossen:
            teile.append(_kappe(0.05, 1.95, nach_unten=False))
        return koerper, _scan(*_zusammen(*teile), (100, 100, 100))

    def _ziel(self, **kopf):
        from meshfigur_zielnetz import Meshfigurzielnetz

        koerper, netz = self._netze(**kopf)
        return Meshfigurzielnetz(koerper, netz, [0, 1.5, 0], [0, 1, 0], 0.25)

    def test_kappe_weg_und_band_da(self):
        ziel = self._ziel()
        self.assertEqual(ziel.teile['kappe_weg'], N)
        self.assertTrue(ziel.teile['naht']['koerperring'] and ziel.teile['naht']['kopfring'])
        self.assertEqual(ziel.teile['naht']['flaechen'], 2 * 48)
        self.assertEqual(len(ziel.index_koerper), ziel.teile['koerper_flaechen'] + 2 * 48, 'die Bandflächen zählen zum Körper')

    def test_das_band_traegt_die_koerperfarbe(self):
        ziel = self._ziel()
        band = np.arange(ziel.teile['koerper_flaechen'], len(ziel.index_koerper))
        farben = ziel.farben(band, np.full((len(band), 3), 1 / 3))
        koerper = ziel.farben(np.array([0]), np.full((1, 3), 1 / 3))[0]
        np.testing.assert_array_equal(farben, np.tile(koerper, (len(band), 1)))

    def test_naht_aus_ist_der_stand_vom_06_10_2026(self):
        """Option `koerper.naht` = aus: die Kappe bleibt, es gibt kein Band — und die Kappe über der Ebene zählt zum Kopf."""
        from meshfigur_zielnetz import Meshfigurzielnetz

        koerper, netz = self._netze()
        ziel = Meshfigurzielnetz(koerper, netz, [0, 1.5, 0], [0, 1, 0], 0.25, naht=False)
        self.assertEqual(ziel.teile['kappe_weg'], 0)
        self.assertEqual(ziel.teile['naht'], {'aus': True})
        self.assertEqual(len(ziel.index_koerper), ziel.teile['koerper_flaechen'])
        self.assertEqual(ziel.teile['kopf_weg'], 0, 'alles liegt über der Ebene, auch die Kappe')

    def test_ohne_rand_am_kopf_bleibt_das_ziel_wie_zuvor_ohne_band(self):
        """Ein geschlossenes Kopfnetz, dessen Unterseite über der Halsgrenze liegt (keine Kappe, kein Rand), bekommt kein Band — das Ziel entsteht trotzdem."""
        ziel = self._ziel(kopf_unten=1.70, kopf_geschlossen=True)
        self.assertFalse(ziel.teile['naht']['kopfring'])
        self.assertEqual(len(ziel.index_koerper), ziel.teile['koerper_flaechen'])


if __name__ == '__main__':
    unittest.main()
