# -*- coding: utf-8 -*-
u"""Der Dienst gegen die ECHTEN Daten: exportiertes Skelett, echtes Netz.

WARUM COMPONENT UND NICHT UNIT (05.09.2026)
===========================================
`core.tests.unit.test_gelenkanpassung` rechnet die Regel an einem Würfel
nach — nachvollziehbar, aber ohne Aussage darüber, ob sie zu DIESEM Projekt
passt. Hier hängt genau das dran:

* Gehört `def_skeleton.json` überhaupt zu dem Netz, das `CharacterState`
  bei Morph 0 liefert? Wenn nicht, verschiebt sich das Skelett schon beim
  ersten Seitenaufruf — und niemand sieht es, weil eine leicht versetzte
  Figur immer noch wie eine Figur aussieht.
* Bewegt sich am Größenregler wirklich etwas, und zwar in der richtigen
  Größenordnung?

Ohne Datenbank (`databases = []` ist die Vorgabe von `SimpleTestCase`): Der
Dienst liest Dateien, keine Tabellen.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.charakterdaten import Charakterdaten
from core.dienste.skelettnachfuehrung import Skelettnachfuehrung
from humanbody_core import CharacterState


class Bezug:
    u"""Was jeder Fall hier braucht: die Anpassung und ein gemorphtes Netz.

    Als Klasse und nicht als zwei freie Funktionen — das Werkzeug
    `freie-funktionen` sucht genau danach.
    """

    @staticmethod
    def anpassung():
        u"""Die Anpassung — und ein klarer Abbruch, wenn es keine gibt.

        `Skelettnachfuehrung.fuer` darf `None` liefern (kein exportiertes
        Skelett). Ein Test, der darauf einfach zugreift, scheitert dann mit
        `AttributeError: 'NoneType' has no attribute 'namen'` — eine
        Meldung, die nach einem Fehler in der Anpassung aussieht statt nach
        einer fehlenden Datei. Der Language Server meldet dieselbe Stelle
        als `reportOptionalSubscript`.
        """
        anpassung = Skelettnachfuehrung.fuer('female')
        assert anpassung is not None, 'kein exportiertes DEF-Skelett gefunden'
        return anpassung

    @staticmethod
    def netz(**morphs):
        u"""Das gemorphte Grundnetz — und ein klarer Abbruch ohne Morphdaten.

        `CharacterState.compute` gibt `None` zurueck, wenn die Basis nicht
        geladen ist. Ohne diese Zeile scheitert der Fall weiter unten mit
        `TypeError: 'NoneType' object is not subscriptable` und liest sich
        wie ein Rechenfehler statt wie eine fehlende Datei.
        """
        zustand = CharacterState(Charakterdaten.morphdaten(),
                                 Charakterdaten.voreinstellungen())
        zustand.set_body_type('Female_Caucasian')
        for schluessel, wert in morphs.items():
            zustand.set_morph(schluessel, wert)
        netz = zustand.compute()
        assert netz is not None, 'Morphdaten nicht geladen'
        return netz


class DerDienstFindetDasSkelett(SimpleTestCase):

    def test_es_gibt_eine_anpassung_fuer_weiblich(self):
        self.assertIsNotNone(Skelettnachfuehrung.fuer('female'))

    def test_sie_kennt_alle_176_knochen(self):
        u"""Weniger hieße, dass ein Teil des Rigs stehen bleibt — sichtbar
        erst dann, wenn jemand genau diesen Körperteil animiert."""
        self.assertEqual(len(Bezug.anpassung().namen), 176)

    def test_und_die_punktzahl_des_grundnetzes(self):
        self.assertEqual(Bezug.anpassung().punktzahl, 18210)

    def test_zweimal_fragen_gibt_dasselbe_objekt(self):
        u"""Der Aufbau kostet 27 ms und einen KD-Baum. Je Regleranschlag
        wäre das die teuerste Zeile im ganzen Ablauf."""
        self.assertIs(Skelettnachfuehrung.fuer('female'),
                      Skelettnachfuehrung.fuer('female'))


class DieRuhelageBewegtNichts(SimpleTestCase):
    u"""Der wichtigste Fall: Ohne Regler darf sich NICHTS ändern."""

    def test_kein_einziger_knochen_meldet_sich(self):
        self.assertEqual(Skelettnachfuehrung.bewegte('female', Bezug.netz()), {})

    def test_und_die_lagen_sind_die_der_datei(self):
        u"""Zahl für Zahl — nicht „ungefähr". Jede Abweichung hier wäre ein
        stiller Versatz zwischen Haut und Rig."""
        anpassung = Bezug.anpassung()
        lagen = anpassung.lokale_positionen(Bezug.netz())
        for knochen in anpassung.knochen:
            self.assertEqual(lagen[knochen['name']], knochen['local_position'],
                             knochen['name'])


class DerGroessenreglerBewegtDasSkelett(SimpleTestCase):
    u"""Der gemeldete Fall vom 05.09.2026."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.anpassung = Bezug.anpassung()
        cls.ruhe = Bezug.netz()
        cls.gross = Bezug.netz(Body_Size=1.0)

    def test_fast_alle_knochen_wandern(self):
        bewegte = Skelettnachfuehrung.bewegte('female', self.gross)
        self.assertGreater(len(bewegte), 170)

    def test_das_skelett_waechst_wie_der_koerper(self):
        u"""Gemessen wird Kopf gegen Fuß im Skelett und die Netzhöhe.

        Beide dürfen nicht auf denselben Faktor festgenagelt werden — der
        Kopfknochen sitzt im Schädel, der Scheitel des Netzes darüber.
        Verlangt ist, dass sie zusammen wachsen, nicht dass sie gleich sind.
        """
        anpassung = Bezug.anpassung()

        def kopf_zu_fuss(netz):
            koepfe = anpassung.weltkoepfe(netz)
            oben = koepfe[anpassung.namen.index('DEF-spine.006')][2]
            unten = koepfe[anpassung.namen.index('DEF-foot.L')][2]
            return oben - unten

        netzwuchs = float(np.ptp(self.gross[:, 2]) / np.ptp(self.ruhe[:, 2]))
        skelettwuchs = float(kopf_zu_fuss(self.gross) / kopf_zu_fuss(self.ruhe))
        self.assertAlmostEqual(skelettwuchs, netzwuchs, delta=0.05)

    def test_und_zwar_nach_oben(self):
        u"""Ein Vorzeichenfehler ergäbe ein schrumpfendes Skelett im
        wachsenden Körper — die Vertauschung, die man am Bildschirm für
        einen Darstellungsfehler halten würde."""
        anpassung = Bezug.anpassung()
        koepfe_ruhe = anpassung.weltkoepfe(self.ruhe)
        koepfe_gross = anpassung.weltkoepfe(self.gross)
        kopf = anpassung.namen.index('DEF-spine.006')
        self.assertGreater(koepfe_gross[kopf][2], koepfe_ruhe[kopf][2])


class EinFremdesNetzBekommtNichts(SimpleTestCase):
    u"""Der Testcharakter hat 17.996 Punkte statt 18.210."""

    def test_die_punktzahl_entscheidet(self):
        self.assertEqual(
            Skelettnachfuehrung.bewegte('female', np.zeros((17996, 3))), {})

    def test_und_gar_kein_netz_ebenso(self):
        self.assertEqual(Skelettnachfuehrung.bewegte('female', None), {})
