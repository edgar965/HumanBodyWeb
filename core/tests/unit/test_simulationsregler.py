# -*- coding: utf-8 -*-
"""Die 42 Simulationsregler: Angaben, Prüfung, Sortierung nach Ziel.

Ein Wert im falschen Abschnitt kommt in der Simulation nicht an und meldet
auch nichts — deshalb prüft das meiste hier die Zuordnung, nicht die Zahl.
"""
import os
import re
from unittest import TestCase

from GarmentCode.simulationsfelder import Simulationsfelder
from GarmentCode.simulationsregler import Simulationsregler


class DieAngabenSindVollstaendigUndWiderspruchsfrei(TestCase):

    def test_jedes_feld_liegt_in_genau_einer_gruppe(self):
        """Ein Feld ohne Gruppe erschiene im Reiter nirgends."""
        alle = {f['schluessel'] for f in Simulationsfelder.alle()}
        gruppiert = [f['schluessel'] for g in Simulationsfelder.nach_gruppen()
                     for f in g['felder']]
        self.assertEqual(alle, set(gruppiert))
        self.assertEqual(len(gruppiert), len(set(gruppiert)),
                         'Ein Feld steht in zwei Gruppen')

    def test_keine_doppelten_schluessel(self):
        schluessel = [f['schluessel'] for f in Simulationsfelder.alle()]
        self.assertEqual(len(schluessel), len(set(schluessel)))

    def test_jedes_ziel_ist_bekannt(self):
        """Ein unbekanntes Ziel landete stumm nirgends."""
        erlaubt = {'material', 'optionen', 'konfig', 'korrektur'}
        for feld in Simulationsfelder.alle():
            self.assertIn(feld['ziel'], erlaubt, feld['schluessel'])

    def test_jede_vorgabe_liegt_in_ihren_eigenen_grenzen(self):
        """Sonst klemmt der erste Bau die Vorgabe weg und aendert stumm das
        Verhalten."""
        for feld in Simulationsfelder.alle():
            if feld['schalter']:
                continue
            self.assertGreaterEqual(feld['vorgabe'], feld['min'],
                                    feld['schluessel'])
            self.assertLessEqual(feld['vorgabe'], feld['max'],
                                 feld['schluessel'])

    def test_jedes_feld_hat_einen_hinweis(self):
        """Ein Regler ohne Hover-Text ist ein Regler, den niemand benutzt."""
        for feld in Simulationsfelder.alle():
            self.assertTrue((feld['hinweis'] or '').strip(),
                            'ohne Hinweis: %s' % feld['schluessel'])

    def test_zahlenfelder_haben_grenzen_und_schritt(self):
        for feld in Simulationsfelder.alle():
            if feld['schalter']:
                continue
            for name in ('min', 'max', 'schritt'):
                self.assertIsNotNone(feld[name],
                                     '%s ohne %s' % (feld['schluessel'], name))
            self.assertGreater(feld['max'], feld['min'], feld['schluessel'])
            self.assertGreater(feld['schritt'], 0, feld['schluessel'])

    def test_schalter_haben_wahrheitswerte_als_vorgabe(self):
        for feld in Simulationsfelder.alle():
            if feld['schalter']:
                self.assertIsInstance(feld['vorgabe'], bool,
                                      feld['schluessel'])


class NurAbweichendesWirdWeitergereicht(TestCase):

    def test_ohne_angabe_bleibt_alles_leer(self):
        self.assertTrue(Simulationsregler.aus_anfrage({}).leer)

    def test_ein_wert_auf_der_vorgabe_wird_nicht_uebernommen(self):
        """Sonst überschriebe der Auftrag auch, was niemand angefasst hat —
        und verdeckte jede spätere Änderung an den Vorgaben."""
        vorgabe = Simulationsfelder.vorgabe('garment_edge_ke')
        regler = Simulationsregler.aus_anfrage(
            {'sim_garment_edge_ke': str(vorgabe)})
        self.assertTrue(regler.leer)

    def test_ein_abweichender_wert_kommt_an(self):
        regler = Simulationsregler.aus_anfrage(
            {'sim_garment_edge_ke': '50'})
        self.assertEqual(regler.fuer('material'), {'garment_edge_ke': 50.0})

    def test_leerer_text_gilt_als_keine_angabe(self):
        self.assertTrue(Simulationsregler.aus_anfrage(
            {'sim_garment_edge_ke': ''}).leer)


class JederWertLandetImRichtigenAbschnitt(TestCase):

    def setUp(self):
        self.regler = Simulationsregler.aus_anfrage({
            'sim_garment_edge_ke': '50',
            # NICHT 0.05 — das ist seit dem 09.09.2026 die Vorgabe, und
            # Vorgabewerte werden absichtlich uebergangen.
            'sim_body_collision_thickness': '0.30',
            'sim_max_sim_steps': '4000',
            'sim_umkreis_cm': '8',
        })

    def test_material_bekommt_nur_material(self):
        self.assertEqual(self.regler.fuer('material'),
                         {'garment_edge_ke': 50.0})

    def test_optionen_bekommt_nur_optionen(self):
        self.assertEqual(self.regler.fuer('optionen'),
                         {'body_collision_thickness': 0.30})

    def test_konfig_bekommt_nur_konfig(self):
        self.assertEqual(self.regler.fuer('konfig'), {'max_sim_steps': 4000.0})

    def test_die_korrektur_geht_nicht_in_die_simulation(self):
        """`UMKREIS_M` ist eine Nachbearbeitung — in `sim.config` wäre sie
        ein unbekannter Schlüssel."""
        for ziel in ('material', 'optionen', 'konfig'):
            self.assertNotIn('umkreis_cm', self.regler.fuer(ziel))

    def test_der_umkreis_wird_in_meter_umgerechnet(self):
        """Der Reiter zeigt Zentimeter, die Klasse rechnet in Metern."""
        self.assertEqual(self.regler.korrekturwerte(), {'UMKREIS_M': 0.08})

    def test_korrekturnamen_heissen_wie_in_der_stoffkorrektur(self):
        from GarmentCode.stoffkorrektur import Stoffkorrektur
        regler = Simulationsregler.aus_anfrage({
            'sim_glaettschritte': '5', 'sim_hub_max_mm': '20',
            'sim_durchgaenge': '4', 'sim_umkreis_cm': '8'})
        for name in regler.korrekturwerte():
            self.assertIn(name, Stoffkorrektur.EINSTELLBAR)

    def test_ganzzahlen_bleiben_ganzzahlig(self):
        """`range(3.0)` wirft — die Durchgänge müssen `int` sein."""
        werte = Simulationsregler.aus_anfrage(
            {'sim_durchgaenge': '4', 'sim_glaettschritte': '5'}
        ).korrekturwerte()
        self.assertIsInstance(werte['DURCHGAENGE'], int)
        self.assertIsInstance(werte['GLAETTSCHRITTE'], int)


class WerteAusDemNetzWerdenGeprueft(TestCase):

    def test_zu_gross_wird_geklemmt(self):
        regler = Simulationsregler.aus_anfrage(
            {'sim_body_collision_thickness': '99'})
        self.assertEqual(regler.fuer('optionen')['body_collision_thickness'],
                         1.0)

    def test_unlesbarer_wert_wird_uebergangen(self):
        """Nicht auf die Vorgabe fallen: Der Regler stünde sichtbar woanders,
        gebaut würde mit dem alten Wert."""
        self.assertTrue(Simulationsregler.aus_anfrage(
            {'sim_garment_edge_ke': 'weich'}).leer)

    def test_nan_wird_uebergangen(self):
        self.assertTrue(Simulationsregler.aus_anfrage(
            {'sim_garment_edge_ke': 'nan'}).leer)

    def test_unbekannter_schluessel_wird_ignoriert(self):
        self.assertTrue(Simulationsregler.aus_anfrage(
            {'sim_gibt_es_nicht': '5'}).leer)

    def test_ein_schalter_liest_wahrheitswerte(self):
        an = Simulationsregler.aus_anfrage({'sim_enable_body_smoothing': 'true'})
        self.assertIs(an.fuer('optionen')['enable_body_smoothing'], True)

    def test_ein_schalter_auf_der_vorgabe_kommt_nicht_mit(self):
        aus = Simulationsregler.aus_anfrage({'sim_enable_body_smoothing': 'false'})
        self.assertTrue(aus.leer)

    def test_schrittzahlen_kommen_als_ganze_zahl_an(self):
        """BELEGT (09.09.2026): `max_sim_steps: 8000.0` liess die Simulation
        abstürzen — `stats.fails.crashes` gesetzt, `fin_frame: -1`. Nach
        aussen sah das nach einem schlechten Ergebnis aus („steht 166 mm
        ab"), nicht nach einem Absturz."""
        werte = Simulationsregler.aus_anfrage(
            {'sim_max_sim_steps': '8000', 'sim_attachment_frames': '200',
             'sim_zero_gravity_steps': '20'})
        self.assertIsInstance(werte.fuer('konfig')['max_sim_steps'], int)
        for name in ('attachment_frames', 'zero_gravity_steps'):
            wert = werte.fuer('optionen').get(name,
                                              werte.fuer('konfig').get(name))
            self.assertIsInstance(wert, int, name)

    def test_kommazahlen_bleiben_kommazahlen(self):
        """Die Ruheschwelle 0,003 als `int` wäre 0 — und damit ein Lauf,
        der nie zur Ruhe kommt."""
        wert = Simulationsregler.aus_anfrage(
            {'sim_static_threshold': '0.003'}).fuer('konfig')['static_threshold']
        self.assertIsInstance(wert, float)
        self.assertEqual(wert, 0.003)

    def test_jedes_ganzzahlige_feld_gibt_es_auch(self):
        """Ein Tippfehler in der Liste bliebe sonst folgenlos — und der
        Wert ginge weiter als Float hinaus."""
        vorhanden = {f['schluessel'] for f in Simulationsfelder.alle()}
        for name in Simulationsfelder.GANZZAHLIG:
            self.assertIn(name, vorhanden)

    def test_die_ankersteifigkeit_wird_zur_liste(self):
        """Die Simulation erwartet dort einen Wert je Ankerart."""
        regler = Simulationsregler.aus_anfrage(
            {'sim_attachment_stiffness': '2000'})
        self.assertEqual(regler.fuer('optionen')['attachment_stiffness'],
                         [2000.0] * 4)


class DieKetteReichtBisInDieSimulation(TestCase):

    @staticmethod
    def _quelle(*teile):
        from django.conf import settings
        stamm = os.path.dirname(os.path.abspath(str(settings.BASE_DIR)))
        with open(os.path.join(stamm, *teile), 'r', encoding='utf-8') as datei:
            return datei.read()

    @classmethod
    def _ohne_kommentare(cls, quelle):
        ohne = re.sub(r'"""..*?"""', '', quelle, flags=re.S)
        ohne = re.sub(r"'''..*?'''", '', ohne, flags=re.S)
        return re.sub(r'#.*', '', ohne)

    def test_der_dienst_reicht_alle_drei_abschnitte_durch(self):
        quelle = self._ohne_kommentare(
            self._quelle('Assets', 'GarmentCode', 'drapierdienst.py'))
        for abschnitt in ('optionen', 'material', 'konfig'):
            self.assertIn("sim.fuer('%s')" % abschnitt, quelle)
        self.assertIn('sim.korrekturwerte()', quelle)

    def test_die_drapierung_schreibt_konfig_in_den_auftrag(self):
        """`konfig` war der einzige Abschnitt ohne Weg von aussen — und ein
        Feld, das nur in `__init__` steht, kommt nie an (06.09.2026)."""
        quelle = self._ohne_kommentare(
            self._quelle('Assets', 'GarmentCode', 'drapierung.py'))
        self.assertIn("'konfig': self.konfig", quelle)

    def test_der_lauf_wendet_konfig_an(self):
        quelle = self._ohne_kommentare(
            self._quelle('Assets', 'GarmentCode', 'drapierlauf.py'))
        self.assertIn("auftrag.get('konfig')", quelle)

    def test_die_stoffkorrektur_nimmt_einstellungen(self):
        quelle = self._quelle('Assets', 'GarmentCode', 'stoffkorrektur.py')
        self.assertIn('EINSTELLBAR', quelle)
        self.assertIn('einstellungen=einstellungen', quelle)

    def test_das_js_haengt_die_abweichenden_werte_an(self):
        quelle = self._quelle('HumanBodyWeb', 'static', 'viewer', 'scene',
                              'garmentcode_drapieren.js')
        self.assertIn('GarmentcodeSimulation.anhaengen(daten)', quelle)

    def test_die_vorsilbe_ist_auf_beiden_seiten_dieselbe(self):
        """`sim_` im JS und `'sim_' + schluessel` in Python — laufen sie
        auseinander, kommt kein einziger Wert an."""
        quelle = self._quelle('HumanBodyWeb', 'static', 'viewer', 'scene',
                              'garmentcode_simulation.js')
        self.assertIn("VORSILBE = 'sim_'", quelle)
        python = self._quelle('Assets', 'GarmentCode', 'simulationsregler.py')
        self.assertIn("'sim_' + feld['schluessel']", python)

    def test_die_vorlage_hat_den_aufklappbereich(self):
        quelle = self._quelle('HumanBodyWeb', 'templates',
                              '_garmentcode_panel.html')
        self.assertIn('gc-simulation', quelle)
