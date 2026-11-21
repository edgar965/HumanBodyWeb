"""Tests für die Zeile „gebaut mit: …“ (`Kleidregelnstand`) und die Prüfsumme der Stufe
„Kleidungsregeln“ (`Kleidstueck`), 21.11.2026."""
import json
import tempfile
import unittest
from pathlib import Path

from core.dienste.kleidregelnstand import Kleidregelnstand
from core.dienste.meshgenesissuchpfad import Meshgenesissuchpfad

#: Eintrag `regeln`, wie die Stufe ihn an der Eigen-Robe von zauberer_mesh_genesis_37 geschrieben hat (Auszug)
REGELN = {
    'oeffnungen': {'stand': 'läuft im Weg', 'weg': 'gebaut'},
    'fetzen': {'stand': 'angewandt', 'inseln': 41, 'fetzen': 31, 'flaechen': 912, 'cm2': 145.2},
    'rand_glatt': {
        'stand': 'angewandt', 'zacken_vorher_mm': 3.63, 'zacken_nachher_mm': 1.79,
        'randpunkte': 1379, 'runden': 3,
    },
    'rock': {'stand': 'angewandt, ohne Wirkung'},
}


def _stueck(wurzel, weg, regeln):
    ordner = Path(wurzel) / weg / 'ki_oberteil'
    ordner.mkdir(parents=True)
    eintrag = {'id': 'ki_oberteil', 'regeln': regeln}
    (ordner / 'eintrag.json').write_text(json.dumps(eintrag), encoding='utf-8')


class KleidregelnstandTest(unittest.TestCase):
    def test_angewandte_regeln_in_kurz_alle_im_titel(self):
        with tempfile.TemporaryDirectory() as t:
            _stueck(t, 'e', REGELN)
            eintrag = {'e': {'anzeige_name': 'Robe'}}
            Kleidregelnstand.ergaenzen(eintrag, Path(t), 'ki_oberteil')
        text = eintrag['e']['regeln_text']
        erwartet = 'gebaut mit: Fetzen weg (31 Inseln, 145 cm²) · Glatter Rand (Zacken 3,63 → 1,79 mm)'
        self.assertEqual(erwartet, text['kurz'])
        self.assertIn('Öffnungen nach Art: läuft im Weg', text['titel'])
        self.assertIn('Rock an beiden Beinen: angewandt, ohne Wirkung', text['titel'])

    def test_ohne_wirksame_regel_kein_kurz(self):
        with tempfile.TemporaryDirectory() as t:
            _stueck(t, 'z', {'fetzen': {'stand': 'aus'}})
            eintrag = {'z': {'anzeige_name': 'Robe'}}
            Kleidregelnstand.ergaenzen(eintrag, Path(t), 'ki_oberteil')
        self.assertEqual('', eintrag['z']['regeln_text']['kurz'])
        self.assertIn('Fetzen weg: aus', eintrag['z']['regeln_text']['titel'])

    def test_oeffnungen_und_abschluss_im_kurztext(self):
        regeln = {'oeffnungen': {'stand': 'angewandt', 'deckel': 2, 'punkte': 128},
                  'abschluss': {'stand': 'angewandt', 'saum_raender': 7, 'punkte': 1568}}
        with tempfile.TemporaryDirectory() as t:
            _stueck(t, 'z', regeln)
            eintrag = {'z': {'anzeige_name': 'Robe'}}
            Kleidregelnstand.ergaenzen(eintrag, Path(t), 'ki_oberteil')
        erwartet = ('gebaut mit: Öffnungen nach Art (2 Löcher geschlossen)'
                    ' · Abschluss mit Stoffdicke (Saum an 7 Rändern)')
        self.assertEqual(erwartet, eintrag['z']['regeln_text']['kurz'])

    def test_ohne_eintrag_oder_mit_fehler_bleibt_alles(self):
        with tempfile.TemporaryDirectory() as t:
            _stueck(t, 'f', REGELN)
            eintrag = {'z': {'anzeige_name': 'Robe'}, 'f': {'fehler': 'kein Netz'}}
            Kleidregelnstand.ergaenzen(eintrag, Path(t), 'ki_oberteil')
        erwartet = {'z': {'anzeige_name': 'Robe'}, 'f': {'fehler': 'kein Netz'}}
        self.assertEqual(erwartet, eintrag)


class KleidstueckPruefsummeTest(unittest.TestCase):
    """Ein neu gebautes `netz.pt` (anderer Inhalt oder keine Notiz) gilt als neues Original."""

    def test_netz_der_stufe_gilt_nur_mit_passender_pruefsumme(self):
        Meshgenesissuchpfad.einhaengen()
        from meshgenesis_kleidstueck import Kleidstueck
        with tempfile.TemporaryDirectory() as t:
            ordner = Path(t)
            (ordner / 'anzeige').mkdir()
            netz = ordner / 'anzeige' / 'netz.pt'
            netz.write_bytes(b'stueck der stufe')
            eintrag = {Kleidstueck.SUMME: Kleidstueck.pruefsumme(netz)}
            self.assertTrue(Kleidstueck.von_der_stufe(ordner, eintrag))
            self.assertFalse(Kleidstueck.von_der_stufe(ordner, {}))
            netz.write_bytes(b'neu gebautes stueck')
            self.assertFalse(Kleidstueck.von_der_stufe(ordner, eintrag))


if __name__ == '__main__':
    unittest.main()
