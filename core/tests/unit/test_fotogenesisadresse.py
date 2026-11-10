"""Die Adresse eines Tests von Foto-Genesis folgt seinem Namen (`Fotogenesisadresse`, 07.11.2026). Ohne Datenbank, ohne Dateien."""
import unittest

from core.dienste.fotogenesisadresse import Fotogenesisadresse
from core.dienste.kennungsstamm import Kennungsstamm


def job(kennung, name=None, vorgabe=None):
    aus = {'id': kennung, 'name': name or kennung}
    if vorgabe is not None or name is not None:
        aus['name_vorgabe'] = vorgabe or kennung
    return aus


class KennungsstammTest(unittest.TestCase):
    databases = []

    def test_umlaute_und_zeichen(self):
        self.assertEqual(Kennungsstamm.aus_name('Königin 1 (neu)', 96), 'koenigin_1_neu')
        self.assertEqual(Kennungsstamm.aus_name('Session3dTools', 96), 'session3dtools')

    def test_laenge_ohne_unterstrich_am_ende(self):
        self.assertEqual(Kennungsstamm.aus_name('abc def', 4), 'abc')

    def test_nichts_uebrig(self):
        self.assertEqual(Kennungsstamm.aus_name('...', 96), '')
        self.assertEqual(Kennungsstamm.aus_name(None, 96), '')


class AdresseTest(unittest.TestCase):
    databases = []

    def test_eigener_name_gibt_die_adresse(self):
        jobs = Fotogenesisadresse.vergeben([job('pshuman_beispiel--session3dtools', 'Session3dTools', 'Probe')])
        self.assertEqual(jobs[0]['adresse'], 'session3dtools')
        self.assertEqual(jobs[0]['id'], 'pshuman_beispiel--session3dtools')
        self.assertEqual(Fotogenesisadresse.seite(jobs[0]), '/foto-genesis/test/session3dtools/')

    def test_name_aus_der_job_json_zaehlt_auch(self):
        self.assertEqual(Fotogenesisadresse.vergeben([job('pshuman_x--session3dtools', 'Session3dTools', 'Session3dTools')])[0]['adresse'], 'session3dtools')

    def test_name_wie_der_ordner_laesst_die_kennung(self):
        self.assertEqual(Fotogenesisadresse.vergeben([job('edgar_fotos', 'Edgar Fotos', 'Edgar Fotos')])[0]['adresse'], 'edgar_fotos')

    def test_exporte_ohne_vorgabe_bleiben(self):
        self.assertEqual(Fotogenesisadresse.vergeben([{'id': 'matt1', 'name': 'Matt 1'}])[0]['adresse'], 'matt1')

    def test_kennung_eines_anderen_jobs_ist_vergeben(self):
        jobs = Fotogenesisadresse.vergeben([job('a', 'Randy', 'A'), job('randy')])
        self.assertEqual([j['adresse'] for j in jobs], ['a', 'randy'])

    def test_gleicher_name_nur_einmal(self):
        jobs = Fotogenesisadresse.vergeben([job('a', 'Probe', 'A'), job('b', 'Probe', 'B')])
        self.assertEqual([j['adresse'] for j in jobs], ['probe', 'b'])

    def test_name_ohne_buchstaben_behaelt_die_kennung(self):
        self.assertEqual(Fotogenesisadresse.vergeben([job('a', '...', 'A')])[0]['adresse'], 'a')


if __name__ == '__main__':
    unittest.main()
