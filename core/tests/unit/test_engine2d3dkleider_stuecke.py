# -*- coding: utf-8 -*-
"""Der Schritt „Kleiderstücke" von „2D3D Kleider" (04.10.2026): Fotostücke vor den Iterationen bauen, messen (`Kleiderstuecknote`) und ans Standmodell hängen (`Standvorabkleider`).

DER ANLASS
==========
Edgar (04.10.2026): „die Kleider sind im 3D View noch nicht wegklickbar … wie ich das einbauen kann vor den Iterationen" und „ein Schritt, der Modell und Kleider ‚besser als Assets' macht: dafür fehlt mir
eine Messgröße". Die Stücke (`Fotostuecke`) entstanden erst in Runde 1 der Iterationen; davor trug das Standmodell keine Kleider.

WAS DIESE PRÜFUNG NICHT IST
===========================
Kunstdaten (ebene Gitter, Würfel), keine Figur, kein Foto-Netz, keine Garderobe: Dass `Kleiderstueckbezug` ein echtes Netz in die Ruhelage zurückrechnet, `Fotostuecke` Stücke baut und das Standmodell die GLB
mit den Stücken schreibt, zeigt nur der Lauf (Auftrag 2026.10.04.11.11.44: Kleiderstücke Oberteil F 0,915, Hose 0,736, Socken 0,790; Stand-GLB 18,0 MB mit 16 Netzen gegen 4,2 MB mit 13).
Geschrieben am 04.10.2026; gelaufen am 04.10.2026 auf Edgars Ansage: 22 Tests, alle grün.

BDD - GEGEBEN / DANN
====================
    Ein Stück, das der Bezug trifft        ... Deckung und Treue 1, Abweichung 0
    Ein Stück, das nur die Hälfte deckt    ... Deckung ≈ 0,5, Treue ≈ 1 — Stoff fehlt, aber nichts ist erfunden
    Ein Stück 30 mm neben dem Bezug        ... beide ≈ 0 (Schwelle 15 mm)
    Ein offenes Netz                       ... Randschleifen zählen die offenen Ränder, Inseln die Teile
    Das Standmodell vor den Iterationen    ... nur die Fotostücke, das Standardhemd aus; mit Iterationen bleibt die Fassung dieselbe
"""

from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from core.dienste.engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodell
from core.dienste.engine2d3dkleiderstuecke import Engine2d3dKleiderstuecke
from core.dienste.kleiderstueckmessung import Kleiderstueckmessung
from core.dienste.kleiderstuecknote import Kleiderstuecknote
from core.dienste.standvorabkleider import Standvorabkleider


def gitter(nx=20, ny=20, groesse=0.30, z=0.0, x0=0.0):
    """Ein ebenes Gitter `groesse` × `groesse` Meter bei Höhe z → `(punkte, flaechen)`."""
    xs, ys = np.linspace(0.0, groesse, nx + 1), np.linspace(0.0, groesse, ny + 1)
    punkte = np.array([[x0 + x, y, z] for y in ys for x in xs])
    flaechen = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            flaechen += [[a, a + 1, a + nx + 1], [a + 1, a + nx + 2, a + nx + 1]]
    return punkte, np.array(flaechen, dtype=np.int64)


class DieNote(SimpleTestCase):
    def test_ein_stueck_auf_dem_bezug_hat_deckung_und_treue_eins(self):
        netz = gitter()
        note = Kleiderstuecknote.vergleichen(netz, netz)
        self.assertEqual((note['deckung'], note['treue'], note['f'], note['abweichung']), (1.0, 1.0, 1.0, 0.0))

    def test_ein_halbes_stueck_deckt_die_haelfte_und_erfindet_nichts(self):
        bezug = gitter(40, 20, 0.30)                       # 0,30 m breit
        stueck = gitter(20, 20, 0.15)                      # die linke Hälfte, gleiche Höhe 0,15 → nur die halbe Breite UND halbe Höhe: darum gleich hoch bauen
        stueck = gitter(20, 20, 0.30)
        stueck = (stueck[0] * np.array([0.5, 1.0, 1.0]), stueck[1])      # 0,15 m breit, 0,30 m hoch — links im Bezug
        note = Kleiderstuecknote.vergleichen(bezug, stueck)
        self.assertAlmostEqual(note['deckung'], 0.5, delta=0.05)
        self.assertGreater(note['treue'], 0.95)
        self.assertLess(note['f'], 0.75)

    def test_ein_stueck_30_mm_neben_dem_bezug_zaehlt_nicht(self):
        bezug, (p, f) = gitter(), gitter()
        note = Kleiderstuecknote.vergleichen(bezug, (p + np.array([0.0, 0.0, 0.030]), f))
        self.assertLess(note['f'], 0.05)
        self.assertGreater(note['abweichung'], 0.95)
        self.assertAlmostEqual(note['abstand_mm'], 30.0, delta=1.0)

    def test_innerhalb_der_schwelle_zaehlt_es_voll(self):
        bezug, (p, f) = gitter(), gitter()
        note = Kleiderstuecknote.vergleichen(bezug, (p + np.array([0.0, 0.0, 0.005]), f))
        self.assertEqual(note['f'], 1.0)

    def test_ohne_flaeche_ist_die_abweichung_eins(self):
        self.assertEqual(Kleiderstuecknote.vergleichen(None, gitter())['abweichung'], 1.0)
        self.assertEqual(Kleiderstuecknote.vergleichen(gitter(), (np.zeros((0, 3)), np.zeros((0, 3), dtype=np.int64)))['f'], 0.0)

    def test_der_koerper_gegen_die_haut_misst_den_abstand_in_millimetern(self):
        haut, (p, f) = gitter(), gitter()
        aus = Kleiderstuecknote.haut_abstand(haut, (p + np.array([0.0, 0.0, 0.005]), f))
        self.assertAlmostEqual(aus['haut_mm'], 5.0, delta=0.5)
        self.assertEqual(aus['deckung'], 1.0)
        self.assertIsNone(Kleiderstuecknote.haut_abstand(None, gitter())['haut_mm'])


class DerAufbau(SimpleTestCase):
    def test_ein_gitter_hat_eine_insel_und_eine_randschleife(self):
        aus = Kleiderstuecknote.aufbau(*gitter(4, 4))
        self.assertEqual((aus['inseln'], aus['randschleifen'], aus['flaechen']), (1, 1, 32))
        self.assertAlmostEqual(aus['cm2'], 900.0, delta=1.0)             # 0,30 m × 0,30 m

    def test_zwei_getrennte_gitter_sind_zwei_inseln_mit_zwei_randschleifen(self):
        a, fa = gitter(3, 3)
        b, fb = gitter(3, 3, x0=1.0)
        aus = Kleiderstuecknote.aufbau(np.vstack([a, b]), np.vstack([fa, fb + len(a)]))
        self.assertEqual((aus['inseln'], aus['randschleifen']), (2, 2))

    def test_ein_geschlossener_koerper_hat_keine_randschleife(self):
        würfel = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], dtype=float)
        seiten = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        flaechen = np.array([f for a, b, c, d in seiten for f in ((a, b, c), (a, c, d))], dtype=np.int64)
        aus = Kleiderstuecknote.aufbau(würfel, flaechen)
        self.assertEqual((aus['inseln'], aus['randschleifen']), (1, 0))

    def test_eine_flaeche_ohne_inhalt_ist_entartet(self):
        p, f = gitter(2, 2)
        p = p.copy()
        p[1] = p[0]                                                      # eine Kante fällt zusammen → angrenzende Flächen ohne Inhalt
        aus = Kleiderstuecknote.aufbau(p, f)
        self.assertGreater(aus['entartet'], 0.0)


class _Bezug:
    """Ein Bezug aus Kunstdaten: je Stücknummer ein Gitter, dazu Haut und Körper."""

    def __init__(self, je_nummer):
        self.je_nummer = je_nummer

    def stueck(self, nummer):
        return self.je_nummer.get(nummer)

    def haut(self):
        return gitter()

    def koerper_netz(self):
        return gitter()


class DieMessung(SimpleTestCase):
    def test_die_note_je_stueck_und_die_gewogene_gesamtabweichung(self):
        gross, klein = gitter(20, 20, 0.30), gitter(20, 20, 0.10)
        bezug = _Bezug({1: gross, 2: klein})
        netze = {'eigen_oberteil': gross, 'eigen_hose': (klein[0] + np.array([0.0, 0.0, 0.05]), klein[1])}     # Oberteil trifft, Hose 50 mm daneben
        with mock.patch('core.dienste.kleiderstueckmessung.Kleiderstueckobjekt.laden', side_effect=lambda k: netze[k]):
            aus = Kleiderstueckmessung.messen(bezug, {'oberteil': 'eigen_oberteil', 'hose': 'eigen_hose'})
        self.assertEqual(aus['stuecke']['oberteil']['note']['abweichung'], 0.0)
        self.assertGreater(aus['stuecke']['hose']['note']['abweichung'], 0.9)
        # Gewogen nach der Fläche der Stücke: das große Oberteil (900 cm²) zählt neunmal so viel wie die kleine Hose (100 cm²).
        soll = (0.0 * 900.0 + aus['stuecke']['hose']['note']['abweichung'] * 100.0) / 1000.0
        self.assertAlmostEqual(aus['abweichung'], soll, delta=0.01)
        self.assertEqual(aus['nah_mm'], 15.0)

    def test_ein_stueck_ohne_netz_wird_als_fehler_gemeldet_und_zaehlt_nicht(self):
        bezug = _Bezug({1: gitter()})
        with mock.patch('core.dienste.kleiderstueckmessung.Kleiderstueckobjekt.laden', return_value=None):
            aus = Kleiderstueckmessung.messen(bezug, {'oberteil': 'weg'})
        self.assertIn('fehler', aus['stuecke']['oberteil'])
        self.assertIsNone(aus['abweichung'])


class DerSchritt(SimpleTestCase):
    @staticmethod
    def _schritt():
        meldungen = []
        job = SimpleNamespace(kennung='x', ergebnis={})
        lauf = SimpleNamespace(job=job, ablage=object(), melden=lambda a, t: meldungen.append((a, t)))
        return Engine2d3dKleiderstuecke(lauf), job, meldungen

    def test_ohne_koerper_gibt_es_keine_stuecke_aber_keinen_fehler(self):
        schritt, job, meldungen = self._schritt()
        with mock.patch('core.dienste.engine2d3dkleiderstuecke.Kleiderstueckbezug') as bezug:
            bezug.return_value.fehlt.return_value = 'genesis_ende.npz fehlt (Schritt „Körper")'
            schritt.ausfuehren()
        self.assertEqual(job.ergebnis['kleiderstuecke']['stuecke'], {})
        self.assertIn('genesis_ende.npz', job.ergebnis['kleiderstuecke']['grund'])
        self.assertEqual(meldungen[-1][0], 1.0)

    def test_baut_fotostuecke_nichts_nennt_der_bericht_den_grund(self):
        schritt, job, _ = self._schritt()
        job.ergebnis['fotostuecke'] = {'bericht': {'fehler': 'Netz ohne Textur'}}
        with mock.patch('core.dienste.engine2d3dkleiderstuecke.Kleiderstueckbezug') as bezug, mock.patch('core.dienste.engine2d3dkleiderstuecke.Fotostuecke') as foto:
            bezug.return_value.fehlt.return_value = None
            foto.return_value.holen.return_value = {}
            schritt.ausfuehren()
        self.assertEqual(job.ergebnis['kleiderstuecke'], {'stuecke': {}, 'grund': 'Netz ohne Textur'})

    def test_mit_stuecken_steht_die_messung_samt_sitz_und_anker_im_ergebnis(self):
        schritt, job, _ = self._schritt()
        job.ergebnis['fotostuecke'] = {'bericht': {'oberteil': {'angezogen': {'median_mm': 0.0, 'p99_mm': 3.2, 'max_mm': 12.0}}}}
        messung = {'stuecke': {'oberteil': {'kennung': 'k', 'note': {'abweichung': 0.1}, 'aufbau': {'cm2': 100.0}}}, 'koerper': {}, 'abweichung': 0.1, 'nah_mm': 15.0}
        with mock.patch('core.dienste.engine2d3dkleiderstuecke.Kleiderstueckbezug') as bezug, mock.patch('core.dienste.engine2d3dkleiderstuecke.Fotostuecke') as foto, \
                mock.patch('core.dienste.engine2d3dkleiderstuecke.Kleiderstueckmessung') as mess, mock.patch('core.dienste.engine2d3dkleiderstuecke.Seitentiefemessung') as tiefe:
            bezug.return_value.fehlt.return_value = None
            foto.return_value.holen.return_value = {'oberteil': 'k'}
            tiefe.messen.return_value = {'grund': 'kein Seitenfoto'}
            mess.messen.return_value = messung
            mess.bibliothek.return_value = {'oberteil': {'sorte': 'g9_base_shirt', 'abweichung': 0.28, 'f': 0.72}}
            schritt.ausfuehren()
        k = job.ergebnis['kleiderstuecke']
        self.assertEqual(k['stuecke']['oberteil']['angezogen']['p99_mm'], 3.2)
        self.assertEqual(k['bibliothek']['oberteil']['abweichung'], 0.28)
        self.assertEqual(k['seitentiefe'], {'grund': 'kein Seitenfoto'})                 # die Rumpftiefe gegen das Seitenfoto steht neben der Note
        self.assertEqual(set(k['sekunden']), {'bauen', 'messen'})


class DerLauf(SimpleTestCase):
    def test_der_schritt_steht_hinter_der_grundfigur_und_vor_den_iterationen(self):
        s = Engine2d3dKleiderlauf.SCHRITTE
        self.assertEqual((s[s.index('grundfigur') + 1], s[s.index('iterationen') - 1]), ('kleiderstuecke', 'kleiderstuecke'))

    def test_die_baender_decken_den_balken_ohne_luecke_ab(self):
        b, s = Engine2d3dKleiderlauf.BAENDER, Engine2d3dKleiderlauf.SCHRITTE
        self.assertEqual(set(b), set(s))
        self.assertEqual(b[s[0]][0], 0)
        self.assertEqual(b[s[-1]][1], 100)
        for vorher, nachher in zip(s, s[1:], strict=False):
            self.assertEqual(b[vorher][1], b[nachher][0], '%s → %s' % (vorher, nachher))

    def test_die_schrittfolge_kennt_den_schritt(self):
        self.assertIn('kleiderstuecke', Engine2d3dKleiderlauf.schrittfolge(SimpleNamespace()))


class DasStandmodell(SimpleTestCase):
    @staticmethod
    def _job(stuecke=None, kreislauf=None, oberteil='foto'):
        """`oberteil`: die Option `koerper.oberteil` — „foto" wie vor dem 04.10.2026 (Vorgabe ist seitdem „bibliothek": `DasOberteilDerBibliothek`)."""
        ergebnis = {}
        if stuecke is not None:
            ergebnis['fotostuecke'] = {'stuecke': stuecke, 'stand': [20, ['maske', 1]]}
        if kreislauf is not None:
            ergebnis['kreislauf'] = {'modell': kreislauf, 'runde_bester': 3}
        return SimpleNamespace(kennung='x', ergebnis=ergebnis, stellung=lambda: {'FBMHeavy': 0.5}, optionen={'koerper': {'oberteil': oberteil}})

    def test_die_stuecke_in_der_reihenfolge_der_kleiderwahl(self):
        job = self._job({'socken': 'eigen_foto_s', 'oberteil': 'eigen_foto_o', 'hose': 'eigen_foto_h'})
        self.assertEqual(Standvorabkleider.stuecke(job), ['eigen_foto_o', 'eigen_foto_h', 'eigen_foto_s'])
        self.assertEqual(Standvorabkleider.stuecke(self._job()), [])

    def test_das_vorab_modell_traegt_nur_die_fotostuecke_und_legt_das_standardhemd_ab(self):
        modell = Standvorabkleider.modell(self._job({'oberteil': 'eigen_foto_o', 'hose': 'eigen_foto_h'}))
        regler = modell['kleidung']
        self.assertEqual(regler['sorte.eigen_foto_o'], 1.0)
        self.assertEqual(regler['sorte.eigen_foto_h'], 1.0)
        self.assertEqual(regler['sorte.g9_base_shirt'], 0.0)       # `kleid_nur` lässt es auf einem frischen Modell sonst stehen
        self.assertIsNone(Standvorabkleider.modell(self._job()))

    def test_die_fassung_aendert_sich_vor_den_iterationen_mit_den_stuecken(self):
        mit, ohne = self._job({'oberteil': 'eigen_foto_o'}), self._job()
        with mock.patch.object(Engine2d3dKleiderstandmodell, '_zubehoer', return_value=[]):
            f_mit = Engine2d3dKleiderstandmodell(mit, object()).fassung()
            f_ohne = Engine2d3dKleiderstandmodell(ohne, object()).fassung()
            f_neu = Engine2d3dKleiderstandmodell(self._job({'oberteil': 'eigen_foto_o2'}), object()).fassung()
        self.assertNotEqual(f_mit, f_ohne)
        self.assertNotEqual(f_mit, f_neu)

    def test_mit_iterationen_bleibt_die_fassung_dieselbe(self):
        """Aufträge mit Iterationen bestimmt deren Modell — die Stücke ändern die Fassung nicht (sonst baute jeder alte Auftrag sein Standmodell neu)."""
        daten = {'koerper': {}, 'kleidung': {}, 'haar': {}, 'farben': {}, 'haltung': {}}
        with mock.patch.object(Engine2d3dKleiderstandmodell, '_zubehoer', return_value=[]):
            a = Engine2d3dKleiderstandmodell(self._job({'oberteil': 'eigen_foto_o'}, daten), object()).fassung()
            b = Engine2d3dKleiderstandmodell(self._job(None, daten), object()).fassung()
        self.assertEqual(a, b)


class DieUhrImVorabModell(SimpleTestCase):
    """Edgar 05.10.2026 („hast du kein Daz-Objekt für Uhr?"): das Startrezept von Sapiens 2 trug keine Uhr, obwohl die Fotos eine zeigen und `eigen_uhr_l` in der Garderobe liegt."""

    def setUp(self):
        Standvorabkleider._UHREN.clear()
        self.addCleanup(Standvorabkleider._UHREN.clear)

    def test_die_uhr_der_fotos_kommt_ins_modell_und_aendert_die_fassung(self):
        job = DasStandmodell._job({'oberteil': 'eigen_foto_o', 'hose': 'eigen_foto_h'})
        with mock.patch.object(Standvorabkleider, 'uhren', return_value=['eigen_uhr_l']):
            regler = Standvorabkleider.modell(job)['kleidung']
            mit = Standvorabkleider.fingerabdruck(job)
        with mock.patch.object(Standvorabkleider, 'uhren', return_value=[]):
            ohne = Standvorabkleider.fingerabdruck(job)
        self.assertEqual(regler['sorte.eigen_uhr_l'], 1.0)
        self.assertNotEqual(mit, ohne)

    def test_die_uhr_kommt_aus_dem_zubehoer_der_fotos_und_wird_gemerkt(self):
        job = DasStandmodell._job({'oberteil': 'eigen_foto_o'})
        with mock.patch('core.dienste.iterationsreferenz.Iterationsreferenz.laden', return_value=([], [])), \
                mock.patch('core.daten.engine2d3dkleiderablage.Engine2d3dKleiderablage'), \
                mock.patch('core.dienste.begutachtungswerkzeug.Begutachtungswerkzeug.zubehoer', return_value={'uhr': ['l']}) as zubehoer:
            self.assertEqual(Standvorabkleider.uhren(job), ['eigen_uhr_l'])
            self.assertEqual(Standvorabkleider.uhren(job), ['eigen_uhr_l'])
        zubehoer.assert_called_once()

    def test_ohne_uhr_oder_bei_einem_fehler_bleibt_die_liste_leer(self):
        job = DasStandmodell._job({'oberteil': 'eigen_foto_o'})
        with mock.patch('core.dienste.iterationsreferenz.Iterationsreferenz.laden', side_effect=OSError('weg')):
            self.assertEqual(Standvorabkleider.uhren(job), [])
        self.assertEqual(Standvorabkleider._UHREN, {})        # ein Fehler wird nicht gemerkt: der nächste Aufruf probiert es wieder
