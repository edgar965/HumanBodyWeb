"""`Fotogenesisjoblauf` und `Meshgenesisrechenmessung`: Schritte eines Jobs, Fehler aus den Zeilen, Wartezeit und Proben. Ohne Datenbank, ohne Karte."""
import unittest
from types import SimpleNamespace
from unittest import mock

from core.dienste.fotogenesisjoblauf import Fotogenesisjoblauf
from core.dienste.meshgenesisrechenmessung import Meshgenesisrechenmessung
from core.dienste.meshgenesisrechenschlange import Meshgenesisrechenschlange


class JoblaufTest(unittest.TestCase):
    databases = []

    @staticmethod
    def _job(foto):
        return {'id': 'n2', 'ordner': r'A:\gibt\es\nicht\n2', 'pshuman': {'genesis_aus_foto': foto}, 'geschlecht': 'weiblich'}

    def test_immer_foto_mesh_dann_mesh_genesis(self):
        # Seit 09.11.2026 ohne Foto-Kette, auch wenn eine alte job.json noch `genesis_aus_foto: true` trägt (Edgar: „die foto-genesis jobs nutzen IMMER den mesh-genesis code“)
        for foto in (False, True):
            self.assertEqual(Fotogenesisjoblauf(self._job(foto)).schritte(), ('fotomesh', 'meshgenesis'))

    def test_fehlerzeile_zaehlt_auch_bei_code_null(self):
        # `pshuman_job_rechnen.py` fängt Fehler je Job ab und endet mit 0
        self.assertIn('FEHLER', Fotogenesisjoblauf.fehler(['n2 FEHLER Keine Person'], 0))

    def test_ohne_fehler_nichts(self):
        self.assertIsNone(Fotogenesisjoblauf.fehler(['n2 schon gerechnet'], 0))

    def test_fehlercode_nennt_letzte_zeilen(self):
        self.assertIn('Fehlercode 2', Fotogenesisjoblauf.fehler(['a', 'b'], 2))

    def test_unerwarteter_fehler_kommt_in_den_stand(self):
        lauf = Fotogenesisjoblauf(self._job(True))
        with mock.patch.object(lauf, '_rechnen', side_effect=TypeError('kaputt')):
            self.assertEqual(lauf._schritt('genesis', None, None, {}), 'TypeError: kaputt')

    def _stand_fuer_seite(self, status, aktiv):
        lauf = Fotogenesisjoblauf(self._job(True))
        with mock.patch.object(lauf, 'stand', return_value={'status': status}), mock.patch.object(Meshgenesisrechenschlange, 'job_aktiv', return_value=aktiv):
            return lauf.stand_fuer_seite()

    def test_ohne_arbeitsprozess_gilt_der_lauf_als_abgebrochen(self):
        self.assertEqual(self._stand_fuer_seite('laeuft', False)['status'], 'fehler')
        self.assertEqual(self._stand_fuer_seite('wartet', False)['status'], 'fehler')

    def test_laufender_und_fertiger_job_bleiben(self):
        self.assertEqual(self._stand_fuer_seite('laeuft', True)['status'], 'laeuft')
        self.assertEqual(self._stand_fuer_seite('fertig', False)['status'], 'fertig')


class MessungCpuTest(unittest.TestCase):
    databases = []

    @staticmethod
    def _prozess(pid, cpu, kinder=()):
        p = mock.Mock(pid=pid)
        p.cpu_times.return_value = SimpleNamespace(user=cpu, system=0.0)
        p.children.return_value = list(kinder)
        return p

    def test_zaehlt_den_interpreter_hinter_dem_starter(self):
        # Unter Windows ist `Scripts\python.exe` der venv nur ein Starter, der Interpreter läuft als Kind
        messung = Meshgenesisrechenmessung()
        messung.prozess_holen = lambda: 1
        with mock.patch('core.dienste.meshgenesisrechenmessung.psutil.Process', return_value=self._prozess(1, 0.1, [self._prozess(2, 5.0)])):
            messung._cpu_lesen()
        self.assertEqual(messung.bericht(10.0)['cpu_s'], 5.0)

    def test_der_dienst_zaehlt_erst_ab_dem_schritt(self):
        messung = Meshgenesisrechenmessung()
        messung.prozess_holen = lambda: 1
        for wert in (100.0, 103.0):
            with mock.patch('core.dienste.meshgenesisrechenmessung.psutil.Process', return_value=self._prozess(1, wert)):
                messung._cpu_lesen()
        self.assertEqual(messung.bericht(10.0)['cpu_s'], 3.0)


class MessungTest(unittest.TestCase):
    databases = []

    def test_wartezeit_von_wartet_bis_gehalten(self):
        m = Meshgenesisrechenmessung()
        m.zeile('wartet auf einen Platz: x — beide Plätze belegt', 10.0)
        m.zeile('wartet auf einen Platz: x — an der Reihe ist y', 20.0)
        m.zeile('  [mia] gehalten: x (Platz 2)', 25.0)
        self.assertEqual(m.bericht(40.0)['warte_s'], 15.0)
        self.assertEqual(m.bericht(40.0)['rechen_s'], 25.0)

    def test_gehalten_ohne_warten_zaehlt_nicht(self):
        m = Meshgenesisrechenmessung()
        m.zeile('gehalten: x (Platz 1)', 5.0)
        self.assertEqual(m.bericht(10.0)['warte_s'], 0.0)

    def test_proben_werden_gemittelt(self):
        m = Meshgenesisrechenmessung()
        m.probe('80, 10240\n')
        m.probe('40, 20480\n')
        b = m.bericht(10.0)
        self.assertEqual((b['karte_pct'], b['vram_spitze_gb'], b['vram_grund_gb']), (60.0, 20.0, 10.0))

    def test_waehrend_des_wartens_keine_probe(self):
        m = Meshgenesisrechenmessung()
        m.zeile('wartet auf einen Platz: x', 1.0)
        m.probe('99, 30000\n')
        self.assertNotIn('karte_pct', m.bericht(2.0))

    def test_vram_des_dienstes_steht_im_bericht(self):
        m = Meshgenesisrechenmessung()
        m.dienst({'code': 0, 'sekunden': 3.0, 'vram_prozess_gb': 9.2})
        b = m.bericht(3.0)
        self.assertEqual(b['vram_prozess_gb'], 9.2)
        self.assertNotIn('code', b)

    def test_kaputte_zeile_faellt_weg(self):
        m = Meshgenesisrechenmessung()
        m.probe('[N/A], [N/A]\n')
        self.assertNotIn('karte_pct', m.bericht(1.0))
