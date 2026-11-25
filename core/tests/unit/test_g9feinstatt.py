# -*- coding: utf-8 -*-
u"""`G9feinstatt` — liegt die gewählte Stufe fertig im Vorrat, geht sie statt des Käfigs hinaus (24.11.2026, Edgar: „EdgarNeu laden … muss in 2 s laden“).

Durch `G9antworten.liefern`, mit eigener Ablage unter einem Wegwerfordner:

1. Käfig-Anfrage mit `X-G9-Fein-Gern: 1`, fein liegt: die feine Antwort, Antwortkopf `X-G9-Fein`, nichts wird gerechnet; der Nachlauf nach einem Neustart merkt sie ohne `stufen=0`.
2. Fein liegt nicht: der Käfig wie bisher, kein Kopf, die Stufe der Anfrage bleibt 0.
3. `leer` (der Körper, dessen gewählte Stufe schon bestellt ist): 204 mit `X-G9-Fein` — ohne feine Antwort der Käfig.
4. Ohne Kopf oder auf einer anderen Stufe als dem Käfig: wie bisher, auch wenn fein liegt.
5. Im dauerhaften Vorrat zählt nur ein Eintrag des JETZIGEN Codes.

Sabotage-Gegenprobe (nicht gefahren): in `_liegt` den Vergleich mit der Fassung streichen → Fall 5 rot; `reset(marke)` streichen → Fall 2 rot; `request.g9_abfrage` streichen → Fall 1 rot.
"""
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import RequestFactory, SimpleTestCase

from core.dienste.g9antworten import G9antworten
from core.dienste.g9feinstatt import G9feinstatt
from core.dienste.g9modellvorrat import G9modellvorrat
from core.dienste.g9neustartnachlauf import G9neustartnachlauf
from core.dienste.netzstufenwahl import Netzstufenwahl


class G9feinstattTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        wurzel = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / '_wegwerf'
        wurzel.mkdir(parents=True, exist_ok=True)
        self.ordner = tempfile.TemporaryDirectory(prefix='_test_g9feinstatt_', dir=wurzel)
        self._patches = [
            mock.patch('Genesis9.pfade.G9pfade.ablage', staticmethod(lambda *a: Path(self.ordner.name))),
            mock.patch.object(G9antworten, '_speicher', type(G9antworten._speicher)()),
            mock.patch.object(G9antworten, '_fassung', 'jetzt'),
            mock.patch.object(G9antworten, 'voraus_an', False),
            mock.patch.object(G9modellvorrat, '_speicher', type(G9modellvorrat._speicher)()),
            mock.patch.object(G9neustartnachlauf, '_an', False),
            mock.patch('core.dienste.g9feinstatt.Netzvorratwahl.behalten', return_value=True),
        ]
        for p in self._patches:
            p.start()
        self.gerechnet = []
        self.rumpf = {'regler': {'a': 0.5}}

    def tearDown(self):
        for p in self._patches:
            p.stop()
        self.ordner.cleanup()

    def _liefern(self, stufe, **kopf):
        anfrage = RequestFactory().post('/x/netz/' + ('?stufen=%d' % stufe if stufe is not None else ''), data=b'{}', content_type='application/json',
                                        **{'HTTP_' + k.upper().replace('-', '_'): v for k, v in kopf.items()})
        marke = Netzstufenwahl._gewaehlt.set(stufe)
        try:
            antwort = G9antworten.liefern('kleid', 'x', self.rumpf, lambda: self.gerechnet.append(Netzstufenwahl.gewaehlt()) or {'stufe': Netzstufenwahl.gewaehlt()}, request=anfrage)
        finally:
            Netzstufenwahl._gewaehlt.reset(marke)
        return antwort, anfrage

    def _fein_ablegen(self):
        G9antworten.merken(G9antworten.schluessel('kleid', 'x', self.rumpf, None), b'{"fein": 1}', platte=False)

    def test_1_fein_statt_kaefig(self):
        self._fein_ablegen()
        antwort, anfrage = self._liefern(0, **{G9feinstatt.KOPF: '1'})
        self.assertEqual((antwort.content, antwort[G9feinstatt.KOPF_ANTWORT], self.gerechnet), (b'{"fein": 1}', '1', []))
        self.assertEqual(anfrage.g9_abfrage, '')

    def test_2_fein_fehlt(self):
        antwort, anfrage = self._liefern(0, **{G9feinstatt.KOPF: '1'})
        self.assertFalse(antwort.has_header(G9feinstatt.KOPF_ANTWORT))
        self.assertEqual(self.gerechnet, [0])
        self.assertFalse(hasattr(anfrage, 'g9_abfrage'))

    def test_3_leer_gibt_nur_bescheid(self):
        antwort, _ = self._liefern(0, **{G9feinstatt.KOPF: G9feinstatt.LEER})
        self.assertEqual((antwort.status_code, self.gerechnet), (200, [0]))
        self._fein_ablegen()
        antwort, _ = self._liefern(0, **{G9feinstatt.KOPF: G9feinstatt.LEER})
        self.assertEqual((antwort.status_code, antwort[G9feinstatt.KOPF_ANTWORT], self.gerechnet), (204, '1', [0]))

    def test_4_ohne_wunsch_wie_bisher(self):
        self._fein_ablegen()
        antwort, _ = self._liefern(0)
        self.assertEqual(self.gerechnet, [0])
        self.assertFalse(antwort.has_header(G9feinstatt.KOPF_ANTWORT))
        antwort, _ = self._liefern(3, **{G9feinstatt.KOPF: '1'})
        self.assertEqual(self.gerechnet, [0, 3])
        self.assertFalse(antwort.has_header(G9feinstatt.KOPF_ANTWORT))

    def test_5_dauerhafter_vorrat_nur_mit_jetzigem_code(self):
        stabil = G9antworten.schluessel('kleid', 'x', self.rumpf, None, fassung='stabil')
        G9modellvorrat._im_speicher(stabil, (b'{"alt": 1}', 'frueher'))
        self._liefern(0, **{G9feinstatt.KOPF: '1'})
        self.assertEqual(self.gerechnet, [0])
        G9modellvorrat._im_speicher(stabil, (b'{"neu": 1}', 'jetzt'))
        with mock.patch('core.dienste.g9vorratanfrage.Netzvorratwahl.behalten', return_value=True):
            antwort, _ = self._liefern(0, **{G9feinstatt.KOPF: '1'})
        self.assertEqual((antwort.content, self.gerechnet), (b'{"neu": 1}', [0]))
