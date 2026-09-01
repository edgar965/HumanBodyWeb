# -*- coding: utf-8 -*-
u"""`humanbody_core.quaternion.Quat` gegen SciPy prüfen.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`_qmul`, `_qinv`, `_qnorm` und `_qrotate` standen Zeichen für Zeichen in
ZWEI Dateien: `skeleton/retarget.py` und `skeleton/skeleton_geometry.py`.
Beide speisen dasselbe Skelett. Ein Vorzeichenfehler, in nur einer Kopie
berichtigt, hätte sich als verdrehter Knochen gezeigt — nicht als roter
Test, denn geprüft wurde keine der beiden.

Zusammengelegt sind sie jetzt in `humanbody_core/quaternion.py`. Damit
das Zusammenlegen belegt ist und bleibt, rechnet dieser Test die
Ergebnisse gegen `scipy.spatial.transform.Rotation` nach — eine fremde
Umsetzung derselben Mathematik. Ein Test, der `Quat.mul` gegen `Quat.mul`
hält, würde jeden Vorzeichenfehler mitmachen.

ACHTUNG BEIM VERGLEICH: `q` und `-q` bezeichnen dieselbe Drehung. Verglichen
wird deshalb über die gedrehten Vektoren oder über den Betrag des
Skalarprodukts, nie über die vier Zahlen roh.

Aufruf:  python manage.py test core.tests.unit.test_quaternion
"""
import numpy as np
from django.test import SimpleTestCase
from scipy.spatial.transform import Rotation

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402


def _zufallsdrehungen(anzahl, keim=20260831):
    """Reproduzierbare Einheitsquaternionen [x,y,z,w]."""
    zufall = np.random.default_rng(keim)
    roh = zufall.normal(size=(anzahl, 4))
    return roh / np.linalg.norm(roh, axis=1, keepdims=True)


class QuatGegenScipyTest(SimpleTestCase):
    u"""Jede Rechnung gegen eine fremde Umsetzung derselben Mathematik."""

    def test_mul_entspricht_scipy_verkettung(self):
        u"""`Quat.mul(a, b)` dreht wie erst b, dann a."""
        for a, b in zip(_zufallsdrehungen(12), _zufallsdrehungen(12, 7)):
            eigen = Quat.mul(a, b)
            fremd = (Rotation.from_quat(a) * Rotation.from_quat(b)).as_quat()
            # Über das Skalarprodukt, weil q und -q dieselbe Drehung sind.
            self.assertAlmostEqual(abs(float(np.dot(eigen, fremd))), 1.0,
                                   places=10)

    def test_rotate_dreht_wie_scipy(self):
        u"""Der gedrehte Vektor ist das, was zählt — dort gibt es kein Vorzeichen."""
        punkte = _zufallsdrehungen(8, 3)[:, :3]
        for q, v in zip(_zufallsdrehungen(8, 11), punkte):
            np.testing.assert_allclose(
                Quat.rotate(q, v), Rotation.from_quat(q).apply(v), atol=1e-12)

    def test_mul_reihe_ist_mul_in_einem_zug(self):
        u"""Die vektorisierte Form muss dasselbe rechnen wie die einzelne.

        Sie existiert, weil `mul` bei einem (N,4)-Feld ein (4,N)-Feld
        zurückgäbe — still transponiert. Genau daran scheiterte
        `_delta_normalize_bvh`, das sich deshalb eine eigene Kopie des
        Hamilton-Produkts schrieb.
        """
        a = _zufallsdrehungen(1, 31)[0]
        reihe = _zufallsdrehungen(9, 37)
        zusammen = Quat.mul_reihe(a, reihe)
        self.assertEqual(zusammen.shape, reihe.shape,
                         'Die Form muss (N, 4) bleiben, nicht (4, N)')
        for i, b in enumerate(reihe):
            np.testing.assert_allclose(zusammen[i], Quat.mul(a, b), atol=1e-12)

    def test_mul_reihe_nimmt_auch_links_eine_reihe(self):
        u"""Beide Seiten Reihen — der Fall aus `retarget/motor.py`.

        Dort werden die Welt-Quaternionen aller Bilder auf einen Schlag
        aus denen des Elternknochens gebildet. Das war die sechste
        handgeschriebene Fassung des Hamilton-Produkts.
        """
        links = _zufallsdrehungen(11, 51)
        rechts = _zufallsdrehungen(11, 53)
        zusammen = Quat.mul_reihe(links, rechts)
        self.assertEqual(zusammen.shape, rechts.shape)
        for i in range(11):
            np.testing.assert_allclose(zusammen[i],
                                       Quat.mul(links[i], rechts[i]),
                                       atol=1e-12)

    def test_mul_reihe_laesst_die_eingabe_unberuehrt(self):
        a = _zufallsdrehungen(1, 41)[0]
        reihe = _zufallsdrehungen(5, 43)
        vorher = reihe.copy()
        Quat.mul_reihe(a, reihe)
        np.testing.assert_allclose(reihe, vorher, atol=0)

    def test_inv_macht_die_drehung_rueckgaengig(self):
        for q in _zufallsdrehungen(8, 5):
            np.testing.assert_allclose(
                Quat.mul(q, Quat.inv(q)), Quat.ID, atol=1e-12)

    def test_norm_liefert_einheitslaenge(self):
        for q in _zufallsdrehungen(6, 13) * 7.5:
            self.assertAlmostEqual(
                float(np.linalg.norm(Quat.norm(q))), 1.0, places=12)

    def test_norm_faengt_den_nullvektor_ab(self):
        u"""Ohne die Abfrage käme hier eine Division durch fast Null."""
        np.testing.assert_allclose(
            Quat.norm(np.zeros(4)), Quat.ID, atol=0)

    def test_from_unit_vectors_trifft_das_ziel(self):
        richtungen = _zufallsdrehungen(8, 17)[:, :3]
        richtungen /= np.linalg.norm(richtungen, axis=1, keepdims=True)
        for a, b in zip(richtungen, np.roll(richtungen, 1, axis=0)):
            np.testing.assert_allclose(Quat.rotate(Quat.from_unit_vectors(a, b), a),
                                       b, atol=1e-10)

    def test_from_unit_vectors_gegenrichtung(self):
        u"""Antiparallel hat keine eindeutige Antwort — aber eine gültige."""
        a = np.array([0.0, 1.0, 0.0])
        gedreht = Quat.rotate(Quat.from_unit_vectors(a, -a), a)
        np.testing.assert_allclose(gedreht, -a, atol=1e-10)

    def test_from_unit_vectors_gleichrichtung_ist_identitaet(self):
        a = np.array([0.0, 0.0, 1.0])
        np.testing.assert_allclose(Quat.from_unit_vectors(a, a), Quat.ID,
                                   atol=0)

    def test_slerp_endpunkte_und_mitte(self):
        a, b = _zufallsdrehungen(2, 23)
        np.testing.assert_allclose(Quat.rotate(Quat.slerp(a, b, 0.0), [1, 0, 0]),
                                   Quat.rotate(a, [1, 0, 0]), atol=1e-10)
        np.testing.assert_allclose(Quat.rotate(Quat.slerp(a, b, 1.0), [1, 0, 0]),
                                   Quat.rotate(b, [1, 0, 0]), atol=1e-10)
        # Die Mitte liegt von beiden Enden gleich weit weg.
        mitte = Quat.slerp(a, b, 0.5)
        self.assertAlmostEqual(abs(float(np.dot(mitte, a))),
                               abs(float(np.dot(mitte, b))), places=10)


class QuatIdTest(SimpleTestCase):
    u"""`Quat.ID` ist EIN geteiltes Array — wer es verändert, verändert es überall."""

    def test_id_ist_die_identitaet(self):
        np.testing.assert_allclose(Quat.ID, [0.0, 0.0, 0.0, 1.0], atol=0)

    def test_norm_gibt_eine_kopie_zurueck(self):
        u"""Sonst schriebe ein Aufrufer versehentlich in die geteilte Konstante."""
        ergebnis = Quat.norm(np.zeros(4))
        ergebnis[0] = 99.0
        self.assertEqual(float(Quat.ID[0]), 0.0)

    def test_from_unit_vectors_gibt_eine_kopie_zurueck(self):
        a = np.array([1.0, 0.0, 0.0])
        ergebnis = Quat.from_unit_vectors(a, a)
        ergebnis[0] = 99.0
        self.assertEqual(float(Quat.ID[0]), 0.0)


class QuatEinzigeFassungTest(SimpleTestCase):
    u"""Diese Rechnung darf nicht wieder in zwei Dateien wandern.

    NACH NAMEN, NICHT NACH NAMENSMUSTER (31.08.2026): Der erste Entwurf
    suchte `def _q…` und meldete prompt `_qrotation` und `_quat_mat_mul`
    aus `pose/pose_data.py`. Die sind KEINE zweite Fassung: sie rechnen
    scalar-first `[w, x, y, z]` mit 4×4-Matrizen im Quaternionenraum
    (die MB-Lab-/CharMorph-Konvention), `Quat` rechnet scalar-last
    `[x, y, z, w]` mit Hamilton-Produkten. Gleicher Anfangsbuchstabe,
    andere Mathematik.

    Dass beide Konventionen im selben Paket leben, ist für sich schon
    unschön — aber es ist eine Frage der Umrechnung an der Grenze
    (`humanbody_core.coordinates`), nicht der doppelten Rechnung.
    """

    #: Genau die Namen, die am 31.08.2026 aus zwei Dateien hierher zogen.
    GEZOGEN = ('_qmul', '_qinv', '_qnorm', '_qrotate', '_qslerp',
               '_qfrom_unit_vectors', '_IDQ')

    def test_keine_zweite_fassung_im_paket(self):
        from pathlib import Path

        import humanbody_core

        wurzel = Path(humanbody_core.__file__).parent
        treffer = []
        for pfad in wurzel.rglob('*.py'):
            if pfad.name == 'quaternion.py' or '__pycache__' in pfad.parts:
                continue
            for zeile in pfad.read_text(encoding='utf-8').splitlines():
                for name in self.GEZOGEN:
                    if (zeile.startswith('def %s(' % name)
                            or zeile.startswith('%s =' % name)):
                        treffer.append('%s: %s' % (pfad.name, zeile.strip()))
        self.assertEqual(treffer, [],
                         'Quaternion-Mathematik steht wieder doppelt im Paket')
