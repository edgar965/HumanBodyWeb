# -*- coding: utf-8 -*-
"""Der Körper der Genesis-Figur der Mesh-Methode (Jobseite, oberste Zeile, Feld 3) liegt unter den Hüllen über Haar und Kleidung — er sticht nicht hindurch und liegt nicht auf ihnen.

WARUM: Edgar, 30.10.2026, mit einem Bild der Figur von schräg hinten (Lauf 2026.10.29.23.02): „Textur T-Shirt hinten kaputt“, „Füße vorne kaputt“, „texturfehler am Hals und
oberen T-shirt (weisse flecken)“. Nachgestellt (`ProjektTemp/_wegwerf/fotogenesis/diag_genesis_ansicht.py 3 --dreh=-35`): die Flecken sind der Körper, der auf oder vor der Hülle liegt
und mit seinen eigenen Farben durchscheint — am Rücken, an Schulter und Kragen, an Gesäß und Hüfte, an den Zehen (aus der Socke). `Hautgleich` setzt unter der Hülle jeden Punkt, der
hinausragt, genau auf seinen Partner — also AUF die Hülle. Gemessen vorher mit diesem Maß: 426.237 mm² in 1.018 Zellen über 12 Ansichten (Raster 1:5).

Maß: `Fotogenesisdurchstoss` — je Foto und um ±45° gedreht: Körper (samt Augäpfeln) und Hülle bis 0,5 mm gleich tief, oder ein bedeckter Körperpunkt (Haar, Kleidung)
weniger als 6 mm vor der Hülle; Fehler = Zelle von 30 mm mit mindestens 100 mm². Seit 30.10.2026 abends ohne die Fehlalarme durch die Augenlöcher und an Haut vor der
Hülle (Lippe vor dem Schnurrbart, Ohr vor dem Haar) — zwei Gegenproben unten.

    manage.py test core.tests.automated.test_fotogenesis_genesis_durchstoss
"""
import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from .fotogenesis_durchstoss import Fotogenesisdurchstoss
from .fotogenesis_figurprobe import Fotogenesisfigurprobe
from .fotogenesis_genesisansicht import Fotogenesisgenesisansicht


class FotogenesisGenesisDurchstoss(SimpleTestCase):
    databases = set()
    JOB = 'EdgarTrip'
    MASSSTAB = 0.2

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.probe = Fotogenesisfigurprobe(settings.OBJECTS_ROOT, cls.JOB)
        cls.ansicht = Fotogenesisgenesisansicht(cls.probe, cls.MASSSTAB) if cls.probe.figur and cls.probe.figur.get('genesis') else None

    def _mass(self):
        if self.ansicht is None or self.probe.training is None:
            self.skipTest('kein Lauf mit Genesis-Figur: training_figur.json ohne genesis')
        self.assertGreater(len(self.ansicht.namen), 2, 'Genesis-Figur ohne Hüllen: %s' % self.ansicht.namen)
        return Fotogenesisdurchstoss(self.ansicht)

    @staticmethod
    def _text(erg):
        return '%d mm² durchgestoßen; %d Zellen: %s' % (erg['mm2'], len(erg['zellen']), '; '.join('%s %+d° bei %s px %d mm²' % z for z in erg['zellen'][:10]))

    def test_koerper_liegt_unter_den_huellen(self):
        mass = self._mass()
        erg = mass.messen()
        self.assertFalse(erg['zellen'], 'Lauf %s — %s' % (self.probe.figur['lauf'], self._text(erg)))

    @staticmethod
    def _versetzt(teile, mm, nur):
        """Die Stücke `nur` je Punkt um `mm` längs ihrer Normale verschoben (+ = nach außen)."""
        aus = []
        for name, x, tri, fa in teile:
            if name in nur:
                n = np.cross(x[tri[:, 1]] - x[tri[:, 0]], x[tri[:, 2]] - x[tri[:, 0]])
                vn = np.zeros_like(x)
                for i in range(3):
                    np.add.at(vn, tri[:, i], n)
                x = x + vn / np.linalg.norm(vn, axis=1, keepdims=True).clip(1e-12) * mm / 1000
            aus.append((name, x, tri, fa))
        return aus

    @staticmethod
    def _zur_kamera(x, tri, f):
        """(T,) bool: Dreiecke, deren Normale (Wicklung, nach außen) zur Kamera des Fotos zeigt."""
        n = np.cross(x[tri[:, 1]] - x[tri[:, 0]], x[tri[:, 2]] - x[tri[:, 0]])
        return ((np.asarray(f['kamera']['ort'], dtype=np.float64) - x[tri].mean(1)) * n).sum(1) > 0

    def test_gegenprobe_koerper_innen_besteht(self):
        """Der Körper 4 mm unter der Hülle: die zur Kamera gewandte Seite einer Hülle, 4 mm nach innen versetzt, als Körper, gegen eben diese Seite (wie das Gegenstück unten).
        Bis 30.10.2026 nachmittags war es der Körper der Figur 4 mm nach innen — das fiel an allen Läufen des Tages durch (08.57 bis 09.22, `probe_gegenprobe_innen.ps1`), weil der
        Körper dort, wo er wirklich herausragt (Scheitel, Kragen), auch 4 mm tiefer noch herausragt: ein Befund über die Figur, keiner über das Maß. Nur die zugewandte Seite,
        weil eine Hülle offen ist: durch das Gesicht sieht die Kamera die Innenseite der Haarkappe am Hinterkopf, und die versetzte Kopie liegt dort 4 mm NÄHER
        (`diag_gegenprobe_innen.py`: Median −3,8 mm) — im echten Maß verdeckt das Gesicht diese Stelle."""
        mass = self._mass()
        mass.DREHUNGEN = (0,)

        def stuecke(nr, f):
            name, x, tri, fa = next(t for t in self.ansicht.stuecke(nr) if t[0] not in mass.HUELLE_NICHT)
            vorn = tri[self._zur_kamera(x, tri, f)]
            innen = self._versetzt([(name, x, vorn, fa)], -4.0, (name,))[0][1]
            return [(name, x, vorn, fa), ('koerper', innen, vorn, fa)]
        erg = mass.messen(stuecke)
        self.assertFalse(erg['zellen'], self._text(erg))

    def test_gegenprobe_koerper_auf_der_huelle_faellt_durch(self):
        """Der Körper 1 mm vor der Hülle: eine Hülle als zweiter Körper."""
        mass = self._mass()
        mass.DREHUNGEN = (0,)

        def stuecke(nr, _f):
            teile = self.ansicht.stuecke(nr)
            huelle = next(t for t in teile if t[0] not in mass.HUELLE_NICHT)
            vor = self._versetzt([huelle], 1.0, (huelle[0],))[0]
            return [t for t in teile if t[0] not in mass.KOERPER] + [('koerper', vor[1], vor[2], vor[3])]
        erg = mass.messen(stuecke, bedeckt=True)        # die Kopie ist ganz Hülle, also ganz bedeckt
        self.assertTrue(erg['zellen'], self._text(erg))

    def test_gegenprobe_haut_vor_der_huelle_besteht(self):
        """Haut darf vor der Hülle liegen (Lippe vor dem Schnurrbart, Ohr vor dem Haar): dieselbe Kopie 1 mm vor der Hülle, aber kein Punkt bedeckt — keine Zelle."""
        mass = self._mass()
        mass.DREHUNGEN = (0,)

        def stuecke(nr, _f):
            teile = self.ansicht.stuecke(nr)
            huelle = next(t for t in teile if t[0] not in mass.HUELLE_NICHT)
            vor = self._versetzt([huelle], 1.0, (huelle[0],))[0]
            return [t for t in teile if t[0] not in mass.KOERPER] + [('koerper', vor[1], vor[2], vor[3])]
        erg = mass.messen(stuecke, bedeckt=np.zeros(1, dtype=bool))
        self.assertFalse(erg['zellen'], self._text(erg))

    def test_gegenprobe_gleich_tief_faellt_auch_an_haut_durch(self):
        """Gleich tief ist immer ein Fehler (Flecken): die Hülle selbst als Körper, kein Punkt bedeckt — Zellen."""
        mass = self._mass()
        mass.DREHUNGEN = (0,)

        def stuecke(nr, _f):
            teile = self.ansicht.stuecke(nr)
            huelle = next(t for t in teile if t[0] not in mass.HUELLE_NICHT)
            return [t for t in teile if t[0] not in mass.KOERPER] + [('koerper', huelle[1], huelle[2], huelle[3])]
        erg = mass.messen(stuecke, bedeckt=np.zeros(1, dtype=bool))
        self.assertTrue(erg['zellen'], self._text(erg))
