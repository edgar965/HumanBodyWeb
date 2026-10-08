# -*- coding: utf-8 -*-
"""Hilfe → Architektur → 2D3D, Reiter „Workflow": der Abschnitt „Technische Details", die Bäume „Kleidung", „Sitz" und „Drapieren" (06.10.2026).

WARUM (Edgar, 06.10.2026): „Blender und Newton sind doch nur Ausnahmen, oder? Standard ist Stoffsolver? Kennzeichne das" und „mach auch möglichst viele technische Details … damit wir später nicht von neuem
anfangen und Fehler nicht wiederholen". Gelesen im Code: der Standard eines Laufs ist KEIN Drapieren, die Vorgabe der Zeile ist newton, Blender und Stoffsolver laufen nur von Hand. Die Tests halten diese
Kennzeichnung an die Vorgaben des Codes — ändert jemand die Vorgabe von `kleid_drapieren` oder von `koerper.oberteil`, muss die Seite mitziehen.

Gegenprobe (nicht gelaufen, Sabotage): `motor='stoffsolver'` als Vorgabe in `ModellFormMixin.kleid_drapieren` → `test_die_vorgabe_der_zeile_ist_der_markierte_motor` rot; `Engine2d3dKleiderkoerperoptionen`
Vorgabe `oberteil` auf `foto` → `test_das_oberteil_der_vorgabe_ist_im_baum_kleidung_als_vorgabe_markiert` rot; ein Eintrag ohne Quelle in `Architektur2d3dfaktennetz.EINTRAEGE` → `test_jeder_eintrag_hat_art_thema_befund_und_quelle` rot.
"""

import inspect

from django.test import Client, SimpleTestCase
from django.urls import reverse

from core.dienste.architektur2d3dtechnik import Architektur2d3dtechnik
from core.dienste.architektur2d3dworkflow import Architektur2d3dworkflow
from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from core.dienste.workflowknoten import Workflowknoten
from core.dienste.workflowstrecke import Workflowstrecke


class TechnischeDetails(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.technik = Architektur2d3dtechnik.kontext()
        cls.text = Client(HTTP_HOST='127.0.0.1').get(reverse('hilfe_architektur_2d3d')).content.decode('utf-8')

    def test_jeder_eintrag_hat_art_thema_befund_und_quelle(self):
        arten = {a['art'] for a in self.technik['arten']}
        for bereich in self.technik['bereiche']:
            for e in bereich['eintraege']:
                self.assertIn(e['art'], arten, e['thema'])
                for feld in ('thema', 'befund', 'quelle'):
                    self.assertTrue(e[feld], '%s: %s fehlt' % (e['thema'], feld))

    def test_die_themen_eines_bereichs_sind_eindeutig(self):
        for bereich in self.technik['bereiche']:
            themen = [e['thema'] for e in bereich['eintraege']]
            self.assertEqual(len(themen), len(set(themen)), bereich['bereich'])

    def test_jede_optionsgruppe_des_codes_hat_ihre_tabelle(self):
        gruppen = {g['gruppe']: g for g in self.technik['optionen']}
        self.assertEqual(list(gruppen), list(Engine2d3dKleideroptionen.GRUPPEN))
        for name, g in gruppen.items():
            self.assertGreater(g['anzahl'], 0, name)
            self.assertIn('id="technik"', self.text)

    def test_die_sampler_von_trellis_stehen_mit_ihrer_vorgabe_in_der_tabelle(self):
        zeilen = {z['schluessel']: z for g in self.technik['optionen'] if g['gruppe'] == 'mesh' for z in g['zeilen']}
        for schluessel in ('ss_fuehrung', 'ss_rescale', 'ss_schritte', 'form_fuehrung', 'tex_fuehrung', 'seed', 'flaechen', 'texturgroesse'):
            self.assertIn(schluessel, zeilen)
        vorgaben = Engine2d3dKleideroptionen.pruefen({})['mesh']
        for schluessel in ('ss_fuehrung', 'flaechen', 'texturgroesse', 'seed'):
            self.assertEqual(zeilen[schluessel]['vorgabe'], self._text(vorgaben[schluessel]), schluessel)

    @staticmethod
    def _text(wert):
        """Der Text, den die Tabelle für einen Vorgabewert zeigt (`Architektur2d3doptionen._text`)."""
        from core.dienste.architektur2d3doptionen import Architektur2d3doptionen
        return Architektur2d3doptionen._text(wert)

    def test_abweichende_vorgaben_dieses_bereichs_sind_in_der_tabelle_markiert(self):
        zeilen = {z['schluessel']: z for g in self.technik['optionen'] if g['gruppe'] == 'figur' for z in g['zeilen']}
        self.assertEqual(zeilen['kopfhaut']['vorgabe'], 'haut')
        self.assertTrue(zeilen['kopfhaut']['abweichung'])
        self.assertEqual(zeilen['modell']['vorgabe'], 'aus')

    def test_die_gruppe_netz_nennt_weder_umgezogene_noch_fremde_felder(self):
        netz = next(g for g in self.technik['optionen'] if g['gruppe'] == 'netz')
        schluessel = {z['schluessel'] for z in netz['zeilen']}
        for umgezogen in Engine2d3dKleideroptionen.UEBERNAHME:
            self.assertNotIn(umgezogen, schluessel)
        self.assertNotIn('formmodell', schluessel)
        self.assertEqual(netz['umgezogen'], len(Engine2d3dKleideroptionen.UEBERNAHME))
        for z in netz['zeilen']:
            self.assertNotIn('hunyuan', (z['titel'] + z['hinweis'] + z['werte']).lower(), z['schluessel'])


class BaeumeKennzeichnung(SimpleTestCase):
    """Vorgabe und Ausnahme in den Bäumen „Drapieren" und „Kleidung" sind die des Codes."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.baeume = {b.kennung: b for b in Architektur2d3dworkflow.baeume()}

    def knoten(self, kennung, teil):
        return [k for k in self.baeume[kennung].wurzel.alle() if teil in k.titel]

    def test_der_standard_ist_kein_drapieren_und_als_vorgabe_markiert(self):
        keins = self.knoten('drapieren', 'Kein Drapieren')
        self.assertEqual(len(keins), 1)
        self.assertTrue(keins[0].vorgabe)
        self.assertFalse(keins[0].ausnahme)

    def test_die_vorgabe_der_zeile_ist_der_markierte_motor(self):
        from Genesis9.modellform import ModellFormMixin
        from Genesis9.rezeptumgebung import Rezeptumgebung

        vorgabe = inspect.signature(ModellFormMixin.kleid_drapieren).parameters['motor'].default
        self.assertIn(vorgabe, Rezeptumgebung.MOTOREN)
        markiert = [k for k in self.baeume['drapieren'].wurzel.alle() if k.art == Workflowknoten.TAT and k.vorgabe]
        self.assertEqual(len(markiert), 1)
        self.assertIn(vorgabe, markiert[0].kante)
        ausnahmen = ' '.join(k.kante for k in self.baeume['drapieren'].wurzel.alle() if k.ausnahme)
        for motor in Rezeptumgebung.MOTOREN:
            if motor != vorgabe:
                self.assertIn(motor, ausnahmen)

    def test_das_oberteil_der_vorgabe_ist_im_baum_kleidung_als_vorgabe_markiert(self):
        from core.dienste.engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen

        vorgabe = Engine2d3dKleiderkoerperoptionen.vorgaben()['oberteil']
        hemd = [k for k in self.baeume['kleidung'].wurzel.alle() if vorgabe in k.kante and k.art == Workflowknoten.TAT]
        self.assertEqual(len(hemd), 1)
        self.assertTrue(hemd[0].vorgabe)

    def test_garmentcode_und_bibliotheksstuecke_sind_ausnahmen(self):
        garmentcode = self.knoten('kleidung', 'GarmentCode')
        self.assertTrue(garmentcode and all(k.ausnahme for k in garmentcode))

    def test_jeder_schritt_der_runde_mit_bauen_verweist_auf_kleidung_und_sitz(self):
        iterationen = next(s for s in Workflowstrecke.SCHRITTE if s[0] == 'iterationen')
        for kennung in ('kleidung', 'sitz', 'drapieren'):
            self.assertIn(kennung, iterationen[4])

    def test_die_marken_stehen_auf_der_seite(self):
        text = Client(HTTP_HOST='127.0.0.1').get(reverse('hilfe_architektur_2d3d')).content.decode('utf-8')
        self.assertIn('wf-marke-vorgabe', text)
        self.assertIn('wf-marke-ausnahme', text)
