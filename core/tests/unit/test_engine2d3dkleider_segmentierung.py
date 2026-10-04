# -*- coding: utf-8 -*-
"""Der Schritt „Segmentierung" von „2D3D Kleider" (04.10.2026): Sapiens zerlegt die Fotos, die Etiketten gehen auf die Netzflächen und — bei Option „An" — in die Kleidungsmaske.

DER ANLASS
==========
Edgar (04.10.2026): „baue das ein in den 2d3dKleider jobs — optional nach der Mesh erzeugung". Probelauf an seinen Fotos: die Maske nach Farbe und Lage hatte Ärmel 2–4 cm zu kurz und Socken
3–9 cm zu niedrig; im Auftrag 2026.10.01.20.10.04 fand sie die Shorts gar nicht (Hose 0 Flächen), die Sapiens-Fassung 2.284 cm².

WAS DIESE PRÜFUNG NICHT IST
===========================
Sie läuft ohne GPU und ohne die 4,7 GB Gewichte an Kunstdaten (ein Streifen aus 400 Flächen mit Kettennachbarschaft). Dass die Etiketten auf echten Fotos stimmen, zeigt nur der Lauf
(Überlagerung auf der Seite); die Projektion auf das Netz (`Sapiensflaechen`) braucht Hunyuans Rasterizer-freie PIL-Zeichnung, aber ein Netz mit Foto — sie ist hier NICHT geprüft.
Gelaufen am 04.10.2026 (auf Ansage, `manage.py test core.tests.unit.test_engine2d3dkleider_segmentierung`): alle 21 grün; danach `DieHaut` (2) dazu, siehe unten. Sabotage-Gegenprobe im Prozess (Patch, kein Quelltext;
`ProjektTemp/_wegwerf/sapiens/sabotage_nah.py`): `NAH_M = 0` → `test_eine_ungesehene_flaeche_dicht_hinter_einer_gesehenen_uebernimmt_deren_stueck` rot; `MIN_STIMMEN = 1e9` → drei Maskentests rot;
`GLAETTUNG = 0` → derselbe Übernahme-Test rot. Nicht von diesen Tests gedeckt: `Sapiensflaechen`/`_run_sapiens.py` (GPU, Gewichte) — das zeigt nur der Lauf.

BDD - GEGEBEN / DANN
====================
    Ein Auftrag ohne Angabe        ... `segmentierung.verwenden` ist aus; im vollen Lauf entfällt der Schritt, ausdrücklich gestartet läuft er
    Die Klassenliste               ... Oberteil/Hose/Füße/Zubehör tragen die Nummern der Kleidungsmaske
    Stimmen für einen Streifen     ... gesehene Flächen folgen den Stimmen, ungesehene dicht dahinter übernehmen, weit entfernte behalten die Regel, Inseln und der Kopf fallen weg
    Stimmen eines anderen Netzes   ... `Sapiensmaske.laden` verweigert mit Grund — die Regel gilt
"""

import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from core.dienste.engine2d3dkleidersegmentierung import Engine2d3dKleidersegmentierung

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
from Kleidung.kleidungsmaske import Kleidungsmaske  # noqa: E402
from Kleidung.sapiensmaske import Sapiensmaske  # noqa: E402
from sapiens_klassen import Sapiensklassen  # noqa: E402
from sapiens_stand import Sapiensstand  # noqa: E402
from scipy.sparse import diags  # noqa: E402


class Pfadkarte:
    """Eine Kette aus n Flächen — jede grenzt an die nächste (die Nachbarschaft, die `Sapiensmaske` von der `Meshfigurhautkarte` braucht)."""

    def __init__(self, n):
        self._a = diags([np.ones(n - 1), np.ones(n - 1)], [-1, 1], format='csr')

    def nachbarn(self):
        return self._a


class DieOption(SimpleTestCase):
    def test_ohne_angabe_ist_sie_aus_und_ein_unsinniger_wert_wird_zur_vorgabe(self):
        self.assertEqual(Engine2d3dKleideroptionen.segmentierung({}), {'verwenden': 'aus'})
        self.assertEqual(Engine2d3dKleideroptionen.segmentierung({'segmentierung': {'verwenden': 'vielleicht'}}), {'verwenden': 'aus'})
        self.assertEqual(Engine2d3dKleideroptionen.segmentierung({'segmentierung': {'verwenden': 'an'}}), {'verwenden': 'an'})

    def test_die_gruppe_steht_im_katalog_und_im_formular(self):
        katalog = Engine2d3dKleideroptionen.katalog()
        felder = [f['schluessel'] for f in katalog['segmentierung']['optionen']]
        self.assertEqual(felder, ['verwenden'])
        self.assertIn('segmentierung', Engine2d3dKleideroptionen.GRUPPEN)

    def test_mischen_aendert_nur_die_geschickte_gruppe(self):
        alt = Engine2d3dKleideroptionen.pruefen({'iterationen': {'runden': 55}})
        neu = Engine2d3dKleideroptionen.mischen(alt, {'segmentierung': {'verwenden': 'an'}})
        self.assertEqual((neu['segmentierung']['verwenden'], neu['iterationen']['runden']), ('an', 55))


class DerSchritt(SimpleTestCase):
    @staticmethod
    def _schritt(verwenden, ab):
        job = SimpleNamespace(kennung='x', optionen={'segmentierung': {'verwenden': verwenden}}, ergebnis={}, bilder=[])
        lauf = SimpleNamespace(job=job, ablage=mock.MagicMock(), ab=ab, melden=lambda *a: None)
        return Engine2d3dKleidersegmentierung(lauf)

    def test_der_schritt_steht_zwischen_netz_und_koerper(self):
        s = Engine2d3dKleiderlauf.SCHRITTE
        self.assertEqual((s[s.index('netz') + 1], s[s.index('koerper') - 1]), ('segmentierung', 'segmentierung'))

    def test_bei_option_aus_entfaellt_er_im_vollen_lauf(self):
        with mock.patch('core.dienste.engine2d3dkleidersegmentierung.PipelineProzess') as pp:
            self._schritt('aus', None).ausfuehren()
            self._schritt('aus', 'netz').ausfuehren()           # „ab Netz" ist KEIN ausdrücklicher Start dieses Schritts
        pp.starten.assert_not_called()

    def test_ausdruecklich_gestartet_laeuft_er_auch_bei_option_aus(self):
        schritt = self._schritt('aus', 'segmentierung')
        with mock.patch.object(schritt, 'beschreibung', side_effect=RuntimeError('Kein Netz')) as beschreibung:
            with self.assertRaises(RuntimeError):
                schritt.ausfuehren()
        beschreibung.assert_called_once()

    def test_bei_option_an_laeuft_er_im_vollen_lauf(self):
        schritt = self._schritt('an', None)
        with mock.patch.object(schritt, 'beschreibung', side_effect=RuntimeError('Kein Netz')) as beschreibung:
            with self.assertRaises(RuntimeError):
                schritt.ausfuehren()
        beschreibung.assert_called_once()

    def test_die_rolle_bei_automatisch_kommt_aus_der_vorbereitung_und_nur_ansichten_zaehlen(self):
        with Pruefablage.ordner() as ordner:
            for name in ('a.png', 'b.png', 'c.png'):
                open(os.path.join(ordner, name), 'wb').close()
            with open(os.path.join(ordner, 'vorbereitung.json'), 'w', encoding='utf-8') as f:
                json.dump({'bilder': [{'datei': 'a.jpg', 'rolle': 'hinten'}, {'datei': 'b.jpg', 'rolle': 'gesicht'}]}, f)
            ablage = SimpleNamespace(unter=lambda name: Path(ordner))
            eintraege = [{'datei': 'a.jpg', 'rolle': 'auto'}, {'datei': 'b.jpg', 'rolle': 'auto'}, {'datei': 'c.jpg', 'rolle': 'links'},
                         {'datei': 'd.jpg', 'rolle': 'vorne'}]            # d.png fehlt
            job = SimpleNamespace(bilder=[])
            with mock.patch('core.dienste.engine2d3dkleidersegmentierung.Engine2d3dKleidernetz.bilder_fuer', return_value=eintraege):
                bilder = Engine2d3dKleidersegmentierung.bilder_fuer(job, ablage)
        self.assertEqual([(b['datei'], b['rolle']) for b in bilder], [('a.jpg', 'hinten'), ('c.jpg', 'links')])


class DieKlassen(SimpleTestCase):
    def test_die_stuecke_tragen_die_nummern_der_kleidungsmaske(self):
        self.assertEqual((Sapiensklassen.OBERTEIL, Sapiensklassen.HOSE, Sapiensklassen.FUESSE, Sapiensklassen.ZUBEHOER),
                         (Kleidungsmaske.OBERTEIL, Kleidungsmaske.HOSE, Kleidungsmaske.FUESSE, Kleidungsmaske.ZUBEHOER))
        self.assertEqual(Sapiensklassen.BEZEICHNUNG[1:], tuple(Kleidungsmaske.NAMEN[n] for n in (1, 2, 3, 4)))

    def test_die_zuordnung_der_klassen(self):
        def stueck(name):
            return int(Sapiensklassen.stueck_je_klasse()[Sapiensklassen.NAMEN.index(name)])
        self.assertEqual(stueck('Upper_Clothing'), 1)
        self.assertEqual(stueck('Lower_Clothing'), 2)
        for name in ('Left_Shoe', 'Right_Shoe', 'Left_Sock', 'Right_Sock'):
            self.assertEqual(stueck(name), 3, name)
        self.assertEqual(stueck('Apparel'), 4)
        for name in ('Face_Neck', 'Hair', 'Torso', 'Left_Hand', 'Right_Upper_Leg', 'Left_Foot'):
            self.assertEqual(stueck(name), 0, name)
        self.assertEqual(stueck('Background'), Sapiensklassen.HINTERGRUND)

    def test_die_fassungen_von_runner_und_maske_sind_gleich(self):
        self.assertEqual(Sapiensstand.FASSUNG, Sapiensmaske.FASSUNG)


class DieMaske(SimpleTestCase):
    N = 400

    @classmethod
    def _stimmen(cls):
        """Streifen aus 400 Flächen (2 cm² je Fläche, Mitten im Abstand von 1 cm nach oben): 0–99 Füße, 100–179 ungesehen (die Regel sagt Hose), 180–259 Oberteil,
        260–299 keine Kleidung mit einer Insel Oberteil (270–274), 300–399 Oberteil — davon der Kopf (ab Fläche 351, `kopf_ab` 3,505 m)."""
        s = np.zeros((cls.N, 5))
        s[0:100, Sapiensklassen.FUESSE] = 10
        s[180:260, Sapiensklassen.OBERTEIL] = 10
        s[260:300, Sapiensklassen.KEINE] = 10
        s[270:275, Sapiensklassen.KEINE] = 0
        s[270:275, Sapiensklassen.OBERTEIL] = 10
        s[300:400, Sapiensklassen.OBERTEIL] = 10
        return s

    def _verbinden(self):
        mitte = np.zeros((self.N, 3))
        mitte[:, 1] = np.arange(self.N) * 0.01
        regel = np.zeros(self.N, dtype=np.int8)
        regel[100:180] = Sapiensklassen.HOSE
        maske = Sapiensmaske(self._stimmen(), Pfadkarte(self.N), np.full(self.N, 2e-4), mitte, kopf_ab=3.505)
        return maske.verbinden(regel)

    def test_gesehene_flaechen_folgen_den_stimmen(self):
        stueck, _ = self._verbinden()
        self.assertTrue((stueck[0:100] == Sapiensklassen.FUESSE).all())
        self.assertTrue((stueck[180:260] == Sapiensklassen.OBERTEIL).all())
        self.assertTrue((stueck[260:270] == 0).all())

    def test_eine_ungesehene_flaeche_dicht_hinter_einer_gesehenen_uebernimmt_deren_stueck(self):
        stueck, bericht = self._verbinden()
        # Die Fläche am Rand der Lücke stimmt über die Stimme ihres Nachbarn mit (100: Füße, 179: Oberteil), die nächste übernimmt von ihr (101, 178).
        self.assertTrue((stueck[100:102] == Sapiensklassen.FUESSE).all())
        self.assertTrue((stueck[178:180] == Sapiensklassen.OBERTEIL).all())
        self.assertEqual(bericht['flaechen_von_sichtbaren'], 2)

    def test_eine_ungesehene_flaeche_weit_weg_behaelt_die_regel(self):
        stueck, _ = self._verbinden()
        self.assertTrue((stueck[102:178] == Sapiensklassen.HOSE).all())

    def test_eine_kleine_insel_faellt_weg_und_der_kopf_ist_nie_kleidung(self):
        stueck, bericht = self._verbinden()
        self.assertTrue((stueck[270:275] == 0).all())
        self.assertTrue((stueck[300:351] == Sapiensklassen.OBERTEIL).all())
        self.assertTrue((stueck[351:] == 0).all())
        self.assertGreaterEqual(bericht['inseln_entfernt_flaechen'], 5)

    def test_der_bericht_nennt_je_stueck_regel_und_sapiens(self):
        _, bericht = self._verbinden()
        self.assertTrue(bericht['verwendet'])
        hose = bericht['je_stueck']['Hose / Rock']
        self.assertGreater(hose['regel_cm2'], 0)
        self.assertGreater(hose['sapiens_cm2'], 0)
        self.assertLess(hose['sapiens_cm2'], hose['regel_cm2'] + 1e-9)     # die Regel-Hose verlor ihre Enden an die Nachbarn


class DasLaden(SimpleTestCase):
    @staticmethod
    def _ablegen(ordner, netz, flaechen=10, fassung=None, netz_stand=None):
        stat = os.stat(netz)
        np.savez_compressed(os.path.join(ordner, Sapiensmaske.DATEI), stimmen=np.ones((flaechen, 5)), flaechen=flaechen,
                            fassung=Sapiensmaske.FASSUNG if fassung is None else fassung,
                            netz=np.array(netz_stand or [stat.st_size, stat.st_mtime_ns]))

    def _netz(self, ordner):
        pfad = os.path.join(ordner, 'mesh.glb')
        with open(pfad, 'wb') as f:
            f.write(b'netz')
        return pfad

    def test_passende_stimmen_werden_geladen(self):
        with Pruefablage.ordner() as ordner:
            netz = self._netz(ordner)
            self._ablegen(ordner, netz)
            self.assertEqual(Sapiensmaske.laden(ordner, netz, 10).shape, (10, 5))

    def test_ohne_datei_mit_anderer_flaechenzahl_fassung_oder_netz_verweigert_sie_mit_grund(self):
        with Pruefablage.ordner() as ordner:
            netz = self._netz(ordner)
            with self.assertRaisesRegex(Sapiensmaske.Unbrauchbar, 'nicht gelaufen'):
                Sapiensmaske.laden(ordner, netz, 10)
            self._ablegen(ordner, netz)
            with self.assertRaisesRegex(Sapiensmaske.Unbrauchbar, 'Flächen'):
                Sapiensmaske.laden(ordner, netz, 11)
            self._ablegen(ordner, netz, fassung=Sapiensmaske.FASSUNG + 1)
            with self.assertRaisesRegex(Sapiensmaske.Unbrauchbar, 'Fassung'):
                Sapiensmaske.laden(ordner, netz, 10)
            self._ablegen(ordner, netz, netz_stand=[1, 2])
            with self.assertRaisesRegex(Sapiensmaske.Unbrauchbar, 'Netz geändert'):
                Sapiensmaske.laden(ordner, netz, 10)

    def test_der_stand_der_ablage_fragt_netz_und_fotos(self):
        with Pruefablage.ordner() as ordner:
            netz, png = self._netz(ordner), os.path.join(ordner, 'vorne.png')
            with open(png, 'wb') as f:
                f.write(b'png')
            self.assertFalse(Sapiensstand.aktuell(ordner, netz, {'vorne.jpg': png})[0])             # noch nichts abgelegt
            Sapiensstand.schreiben(ordner, netz, 10, [{'datei': 'vorne.jpg', 'quelle': Sapiensstand.quelle(png)}], {})
            self.assertEqual(Sapiensstand.aktuell(ordner, netz, {'vorne.jpg': png}), (True, ''))
            with open(png, 'wb') as f:
                f.write(b'anderes png')
            self.assertIn('geändert', Sapiensstand.aktuell(ordner, netz, {'vorne.jpg': png})[1])


class DerHaken(SimpleTestCase):
    """`Meshfigurkleidung._sapiens`: „Mesh to 3D" hat kein `sapiens_maske` und rechnet wie bisher; „2D3D Kleider" ohne passende Stimmen sagt den Grund."""

    @staticmethod
    def _kleidung(lauf):
        from core.dienste.meshfigurkleidung import Meshfigurkleidung
        k = Meshfigurkleidung.__new__(Meshfigurkleidung)
        k.lauf, k.job = lauf, SimpleNamespace(kennung='x', ergebnis={})
        return k

    def test_ohne_das_attribut_bleibt_die_maske_wie_sie_ist(self):
        maske = {'stueck': np.zeros(3, dtype=np.int8)}
        gleiche, bericht = self._kleidung(SimpleNamespace())._sapiens(None, maske, None, None, None)
        self.assertIs(gleiche, maske)
        self.assertIsNone(bericht)

    def test_ohne_passende_stimmen_gilt_die_regel_und_der_grund_steht_im_bericht(self):
        with Pruefablage.ordner() as ordner:
            k = self._kleidung(SimpleNamespace(sapiens_maske=True))
            k.ablage = SimpleNamespace(arbeit=lambda *a: ordner)
            maske = {'stueck': np.zeros(3, dtype=np.int8)}
            gleiche, bericht = k._sapiens(None, maske, None, SimpleNamespace(flaechen=[0, 1, 2]), SimpleNamespace(auftrag={'netz': 'x'}))
        self.assertIs(gleiche, maske)
        self.assertFalse(bericht['verwendet'])
        self.assertIn('nicht gelaufen', bericht['grund'])


class DieHaut(SimpleTestCase):
    """`Kleidungsmaske.abschliessen`: Hautton nur dort, wo kein Stück gilt (04.10.2026) — sonst fehlte `Fotostuecke` die Hose (`haut` auf 85 % der Sapiens-Hosenflächen)."""

    @staticmethod
    def _regel(haut):
        regel = Kleidungsmaske.__new__(Kleidungsmaske)
        regel.haut = np.asarray(haut, dtype=bool)
        return regel

    def test_ein_stueck_ist_nie_haut_und_die_nichtkleidung_behaelt_ihren_hautton(self):
        regel = self._regel([True, True, False, False, True])
        with mock.patch.object(Kleidungsmaske, '_steckbriefe', return_value=[]), mock.patch.object(Kleidungsmaske, '_kopf_ab', return_value=1.5):
            maske = regel.abschliessen(np.array([2, 0, 1, 0, 3]))
        self.assertEqual(maske['haut'].tolist(), [False, True, False, False, False])
        self.assertFalse((maske['haut'] & maske['kleidung']).any())

    def test_fuer_die_regel_ist_es_eine_identitaet(self):
        """Die Regel setzt Stücke nur auf `~haut` — dann ändert `abschliessen` am Hautton nichts."""
        haut = [True, False, True, False]
        regel = self._regel(haut)
        with mock.patch.object(Kleidungsmaske, '_steckbriefe', return_value=[]), mock.patch.object(Kleidungsmaske, '_kopf_ab', return_value=1.5):
            maske = regel.abschliessen(np.array([0, 1, 0, 2]))
        self.assertEqual(maske['haut'].tolist(), haut)
