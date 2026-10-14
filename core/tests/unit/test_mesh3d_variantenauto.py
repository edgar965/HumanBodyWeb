# -*- coding: utf-8 -*-
"""Die automatische Vergleichsvariante des Wegs „netz“ (13.10.2026, Edgar: „baue zumindest eine Variante“ — „Automatisch mit jedem Lauf“). Nicht gelaufen — läuft nur auf Ansage.

Ohne Blender, GPU und Datenbank: die Aufträge sind Ordner unter einer umgebogenen `OBJECTS_ROOT` (`_Ablage` aus `test_mesh3d_varianten`); der Auftrag „Mesh to 3D“ der Variante und der Prozess sind Attrappen.

    AnlegenTest      `Mesh3dvariantenauto.anlegen`: Gegenwert je Stoffzug, Einstellung aus, Weg „teile“, Hauptausgabe nicht fertig, Wert schon da, Prozess läuft schon, `sicher` wirft nie
    EntfernenTest    `entfernen`: nur die automatischen Varianten, der Prozess wird vorher angehalten
    WartenTest       `Mesh3dvariantenlauf._abwarten`: wartet, solange ein ANDERER Import rechnet
    VerdrahtungTest  Wächter (Quelltext gelesen): Ende des Imports, Start eines neuen Laufs, Kommandozeile, Einstellung, Karte

Sabotage-Gegenprobe: in `Mesh3dvariantenauto.GEGENWERT` `'nah': 'ignorieren'` zu `'nah': 'nah'` → `test_gegenwert_*` rot; die Prüfung `vergleichsvariante` streichen → `test_einstellung_aus_*` rot; in `entfernen` `if e.get('automatisch')`
weglassen → `test_entfernen_nimmt_nur_die_automatischen` rot; den Aufruf `Mesh3dvariantenauto.sicher(` aus `Blendimportlauf.ausfuehren` nehmen → `VerdrahtungTest` rot.
"""

from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.blendimporteinstellungen import Blendimporteinstellungen
from core.dienste.mesh3dvarianten import Mesh3dvarianten
from core.dienste.mesh3dvariantenauto import Mesh3dvariantenauto
from core.dienste.mesh3dvariantenlauf import Mesh3dvariantenlauf

from .test_mesh3d_varianten import KENNUNG, _Ablage

WEB = Path(__file__).resolve().parents[3]
LAUF = 'core.dienste.mesh3dvariantenlauf.Mesh3dvariantenlauf'


def _einstellungen(zug, **mehr):
    return {'kleidung_zug': zug, 'basis': 'feminine', 'pose': 'sam', **mehr}


class AnlegenTest(_Ablage):
    def setUp(self):
        super().setUp()
        self.starten = mock.patch(LAUF + '.starten').start()
        self.lebt = mock.patch(LAUF + '.lebt', return_value=False).start()
        mock.patch.object(Mesh3dvarianten, '_hauptauftrag', return_value=None).start()
        mock.patch.object(Mesh3dvarianten, '_eintrag', side_effect=lambda ablage, stand, f, wert: {'id': 'v-' + wert, 'kennung': 'k-' + wert, 'feld': f['schluessel'], 'wert': wert, 'titel': wert}).start()
        self.addCleanup(mock.patch.stopall)

    def _gegenwert(self, zug):
        self._stand(einstellungen=_einstellungen(zug))
        return Mesh3dvariantenauto.anlegen(KENNUNG)

    def test_gegenwert_von_nah_ist_ignorieren(self):
        eintrag = self._gegenwert('nah')
        self.assertEqual((eintrag['wert'], eintrag['automatisch']), ('ignorieren', True))
        self.assertEqual([e['wert'] for e in Mesh3dvarianten.lesen(KENNUNG)['eintraege']], ['ignorieren'])
        self.assertTrue(Mesh3dvarianten.lesen(KENNUNG)['eintraege'][0]['automatisch'])

    def test_gegenwert_von_ignorieren_ist_nah(self):
        self.assertEqual(self._gegenwert('ignorieren')['wert'], 'nah')

    def test_gegenwert_von_weich_ist_nah(self):
        self.assertEqual(self._gegenwert('weich')['wert'], 'nah')

    def test_der_prozess_wartet_auf_andere_importe(self):
        self._gegenwert('nah')
        self.starten.assert_called_once_with(KENNUNG, warten=True)

    def test_ein_laufender_prozess_nimmt_den_eintrag_selbst_mit(self):
        self.lebt.return_value = True
        self._gegenwert('nah')
        self.starten.assert_not_called()
        self.assertEqual(len(Mesh3dvarianten.lesen(KENNUNG)['eintraege']), 1)

    def test_einstellung_aus_legt_nichts_an(self):
        self._stand(einstellungen=_einstellungen('nah', vergleichsvariante='aus'))
        self.assertIsNone(Mesh3dvariantenauto.anlegen(KENNUNG))
        self.assertFalse(Mesh3dvarianten.pfad(KENNUNG).exists())
        self.starten.assert_not_called()

    def test_ohne_die_einstellung_gilt_an(self):
        self._stand(einstellungen=_einstellungen('nah'))                              # ein Auftrag von vor dem Umbau kennt den Schlüssel nicht
        self.assertIsNotNone(Mesh3dvariantenauto.anlegen(KENNUNG))

    def test_weg_teile_legt_nichts_an(self):
        self._stand(weg='teile', einstellungen=_einstellungen('nah'))
        self.assertIsNone(Mesh3dvariantenauto.anlegen(KENNUNG))
        self.assertFalse(Mesh3dvarianten.pfad(KENNUNG).exists())

    def test_ohne_fertige_hauptausgabe_nichts(self):
        self._stand(einstellungen=_einstellungen('nah'))
        with mock.patch.object(Mesh3dvarianten, '_hauptauftrag', side_effect=ValueError('noch nicht gerechnet')):
            self.assertIsNone(Mesh3dvariantenauto.anlegen(KENNUNG))
        self.assertFalse(Mesh3dvarianten.pfad(KENNUNG).exists())

    def test_ein_vorhandener_wert_wird_nicht_doppelt_gerechnet(self):
        self._stand(einstellungen=_einstellungen('nah'))
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': [{'id': 'a', 'kennung': 'ka', 'feld': 'kleidung_zug', 'wert': 'ignorieren', 'titel': 'x'}]})
        self.assertIsNone(Mesh3dvariantenauto.anlegen(KENNUNG))

    def test_der_wert_des_ersten_laufs_nach_dem_uebernehmen_zaehlt_als_vorhanden(self):
        self._stand(einstellungen=_einstellungen('ignorieren'))                       # „nah“ war der erste Lauf, „ignorieren“ ist übernommen: der Gegenwert „nah“ steht schon in der Hauptausgabe
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': [{'id': 'a', 'kennung': 'ka', 'feld': 'kleidung_zug', 'wert': 'ignorieren', 'titel': 'x'}], 'haupt': 'a', 'vorher': {'kleidung_zug': 'nah'}})
        self.assertIsNone(Mesh3dvariantenauto.anlegen(KENNUNG))

    def test_die_grenze_der_varianten_gilt(self):
        self._stand(einstellungen=_einstellungen('nah'))
        voll = [{'id': str(i), 'kennung': 'k%d' % i, 'feld': 'basis', 'wert': 'x', 'titel': 't'} for i in range(Mesh3dvarianten.HOECHSTENS)]
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': voll})
        self.assertIsNone(Mesh3dvariantenauto.anlegen(KENNUNG))

    def test_sicher_wirft_nie(self):
        with mock.patch.object(Mesh3dvariantenauto, 'anlegen', side_effect=RuntimeError('kaputt')):
            self.assertIsNone(Mesh3dvariantenauto.sicher(KENNUNG))


class EntfernenTest(_Ablage):
    def setUp(self):
        super().setUp()
        self.loeschen = mock.patch.object(Mesh3dvarianten, 'loeschen').start()
        self.anhalten = mock.patch(LAUF + '.anhalten').start()
        self.lebt = mock.patch(LAUF + '.lebt', return_value=False).start()
        self.addCleanup(mock.patch.stopall)
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': [
            {'id': 'hand', 'kennung': 'kh', 'feld': 'basis', 'wert': 'masculine', 'titel': 'von Hand'},
            {'id': 'auto', 'kennung': 'ka', 'feld': 'kleidung_zug', 'wert': 'ignorieren', 'titel': 'automatisch', 'automatisch': True}]})

    def test_entfernen_nimmt_nur_die_automatischen(self):
        self.assertEqual(Mesh3dvariantenauto.entfernen(KENNUNG), 1)
        self.loeschen.assert_called_once_with(KENNUNG, 'auto')

    def test_ein_rechnender_prozess_wird_vorher_angehalten(self):
        self.lebt.return_value = True
        Mesh3dvariantenauto.entfernen(KENNUNG)
        self.anhalten.assert_called_once_with(KENNUNG)

    def test_ohne_automatische_passiert_nichts(self):
        Mesh3dvarianten.schreiben(KENNUNG, {'eintraege': [{'id': 'hand', 'kennung': 'kh', 'feld': 'basis', 'wert': 'masculine', 'titel': 'von Hand'}]})
        self.assertEqual(Mesh3dvariantenauto.entfernen(KENNUNG), 0)
        self.loeschen.assert_not_called()
        self.anhalten.assert_not_called()


class WartenTest(SimpleTestCase):
    def test_wartet_bis_der_andere_import_fertig_ist(self):
        with mock.patch('core.dienste.blendimportarbeiter.Blendimportarbeiter.laufender', side_effect=['2026.10.13.09.00.00', '2026.10.13.09.00.00', None]) as laufender, \
                mock.patch('core.dienste.mesh3dvariantenlauf.time.sleep') as schlaf:
            Mesh3dvariantenlauf._abwarten(KENNUNG)
        self.assertEqual(schlaf.call_count, 2)
        laufender.assert_called_with(ausser=KENNUNG)                                # der eigene Import zählt nicht

    def test_ohne_anderen_import_sofort(self):
        with mock.patch('core.dienste.blendimportarbeiter.Blendimportarbeiter.laufender', return_value=None), mock.patch('core.dienste.mesh3dvariantenlauf.time.sleep') as schlaf:
            Mesh3dvariantenlauf._abwarten(KENNUNG)
        schlaf.assert_not_called()


class VerdrahtungTest(SimpleTestCase):
    @staticmethod
    def _text(*teile):
        return WEB.joinpath(*teile).read_text(encoding='utf-8')

    def test_der_import_ruft_die_variante_nach_dem_fertig(self):
        text = self._text('core', 'dienste', 'blendimportlauf.py')
        self.assertIn('Mesh3dvariantenauto.sicher(self.ablage.kennung)', text)
        self.assertLess(text.index("logger.info('Blender-Import %s: fertig'"), text.index('Mesh3dvariantenauto.sicher('))

    def test_ein_neuer_lauf_entfernt_die_alte_automatische_variante(self):
        text = self._text('core', 'dienste', 'blendimportarbeiter.py')
        self.assertIn('Mesh3dvariantenauto.entfernen(ablage.kennung)', text)
        self.assertLess(text.index('Mesh3dvariantenauto.entfernen('), text.index('Mesh3dvarianten.haupt_loesen('))

    def test_der_befehl_kennt_warten(self):
        text = self._text('core', 'management', 'commands', 'mesh3d_varianten.py')
        self.assertIn("'--warten'", text)
        self.assertIn("warten=options['warten']", text)

    def test_die_einstellung_steht_im_katalog_und_auf_der_jobseite(self):
        eintrag = Blendimporteinstellungen.eintrag('vergleichsvariante')
        self.assertEqual((eintrag['vorgabe'], [w for w, _ in eintrag['werte']]), ('an', ['an', 'aus']))
        self.assertEqual(Blendimporteinstellungen.pruefen({})['vergleichsvariante'], 'an')
        self.assertEqual(Blendimporteinstellungen.pruefen({'vergleichsvariante': 'quatsch'})['vergleichsvariante'], 'an')
        self.assertIn("'vergleichsvariante'", self._text('static', 'viewer', 'mesh3d', 'mesh3dquelle.js'))


class KennzeichnungTest(SimpleTestCase):
    """Eine automatisch angelegte Variante heißt in Spalte und Ausgabe-Auswahl „(automatisch)“ — das Merkmal geht vom Eintrag bis in die Oberfläche."""

    KOPF = {'id': 'x', 'titel': 'Stoff beim Anpassen: nah', 'rolle': 'variante', 'feld': 'kleidung_zug', 'wert': 'nah'}

    def test_die_spalte_traegt_das_merkmal(self):
        from core.dienste.mesh3dvergleich import Mesh3dvergleich

        self.assertTrue(Mesh3dvergleich._spalte_aus_job(None, {**self.KOPF, 'automatisch': True}, False)['automatisch'])
        self.assertFalse(Mesh3dvergleich._spalte_aus_job(None, self.KOPF, False)['automatisch'])

    def test_die_oberflaeche_nennt_es_in_spaltentitel_und_ausgabe(self):
        text = VerdrahtungTest._text('static', 'viewer', 'mesh3d', 'mesh3dvarianten.js')
        self.assertIn("s.automatisch ? 'Variante (automatisch)'", text)
        self.assertIn("e.automatisch ? ' (automatisch)'", text)
