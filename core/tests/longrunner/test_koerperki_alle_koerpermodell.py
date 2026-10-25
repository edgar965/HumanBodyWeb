# -*- coding: utf-8 -*-
"""Tests für `KoerperKI_alle.koerpermodell.Koerpermodell` (24.10.2026, Besitzer 2d-3d-AI) an einer echten gebauten Figur (`unit/_gebautefigur.py`) — im LongRunner (Genesis und Formmass2 ~5 s).

WARUM: Das Einpassen in die Fotos (`KoerperKI_Fotos.Fotoeinpassung`) bewegt Körperregler über diese Klasse, linear um die gebaute Figur. Zugesagt ist: an den Reglern der Figur IST es die Figur,
die Häutung ist dieselbe wie in `Koerpernetz`, frei sind nur wirksame Körperregler — „den Kopf formt hier die KopfKI“ —, und die Näherung liegt nahe an der echten Formung.
Im ersten EdgarTrip-Lauf (24.10.2026 14:26) waren 74 von 216 freien Reglern solche, die auch die Kopfform ändern (`uma:Face_headSize` 19 mm, `uma:Body_height` 48 mm, Alter, Kind; gemessen
`ProjektTemp/_wegwerf/ai2d3d/kopfwirkung_probe.py`); Runde 1 setzte `uma:Face_headSize` auf +0,97, und die Figur wurde von 1,710 m auf 1,463 m kleiner (`figurgroesse_probe.py`).
"""
import unittest

import numpy as np
import torch

from ..unit._gebautefigur import Gebautefigur


class DasKoerpermodell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Gebautefigur.da():
            raise unittest.SkipTest('keine gebaute Figur unter %s' % Gebautefigur.QUELLE)
        from KoerperKI_alle.koerpermodell import Koerpermodell
        from KoerperKI_alle.koerpernetz import Koerpernetz
        cls.ordner, cls.regler = Gebautefigur.kopieren()
        cls.n = Koerpernetz(cls.ordner, cls.regler, geraet='cpu')
        cls.km = Koerpermodell(cls.n, cls.regler, mit_form=True)
        cls.kb = Koerpermodell(cls.n, cls.regler, mit_form=False)
        cls.K = Koerpermodell

    @classmethod
    def tearDownClass(cls):
        Gebautefigur.weg(cls.ordner)

    def haltung(self, km):
        """Eine gebeugte Haltung: Vorbelegung ohne Winkel, Wurzel in Ruhe, dazu feste Ausschläge auf den freien Kanälen."""
        roh = km.roh(np.zeros((len(self.n.namen), 3)), np.eye(3), self.n.zentren[0].numpy())
        f = len(km.kin.frei)
        roh[:f] = roh[:f] + 0.8 * torch.sin(torch.arange(f, dtype=torch.float32))
        return roh

    def frei(self):
        return torch.nonzero(self.km.maske).reshape(-1).tolist()

    def test_an_den_reglern_der_figur_ist_es_die_figur(self):
        p, c = self.km.ruhe(self.km.r0)
        self.assertLess(float((p - self.n.ruhe[self.km.wahl]).abs().max()), 1e-6)
        self.assertLess(float((c - self.n.zentren).abs().max()), 1e-6)

    def test_haeutung_wie_koerpernetz(self):
        for km, auswahl in ((self.kb, slice(None)), (self.km, self.km.wahl)):
            roh = self.haltung(km)
            x, p, _e, d, _w = km.koerper(km.r0, roh, mit_gelenken=True)
            self.assertLess(float((x - self.n.haeuten(p, d)[auswahl]).abs().max()), 1e-5, km.mit_form)
            self.assertGreater(float((x - self.n.ruhe[auswahl]).norm(dim=1).max()), 0.05)          # die Haltung ist wirklich gebeugt

    def test_frei_nur_wirksame_koerperregler(self):
        frei = self.frei()
        self.assertGreater(len(frei), 50)
        for i in frei:
            r = self.km.fm.liste[i]
            self.assertNotIn(r.get('bereich'), self.K.AUS_BEREICHE, r['name'])
            self.assertGreaterEqual(float(r.get('wirkung_mm') or 0), self.K.WIRKUNG_MIN_MM, r['name'])

    def test_kein_freier_regler_formt_den_kopf(self):
        """Kopfform = Formmass2-Kopfteil, Lage abgezogen, RMS über die Kopfpunkte, Regler von der Figur bis an seine Grenze (größere Seite)."""
        self.assertLessEqual(self.K.KOPF_MAX_MM, 2.0)
        fm, r0 = self.km.fm, self.km.r0
        frei = self.frei()
        v = r0.repeat(2 * len(frei), 1)
        for k, i in enumerate(frei):
            v[2 * k, i], v[2 * k + 1, i] = fm.hi[i], fm.lo[i]
        with torch.no_grad():
            kopf = np.asarray(fm.kopf_mm(v.numpy(), r0.repeat(len(v), 1).numpy())['kopf_form']).reshape(-1, 2).max(1)
        zu_viel = [(fm.namen[i], round(float(kopf[k]), 1)) for k, i in enumerate(frei) if float(kopf[k]) > self.K.KOPF_MAX_MM]
        self.assertEqual(zu_viel, [])

    def test_klemmen_haelt_die_festen_und_die_grenzen(self):
        frei = torch.zeros(len(self.km.r0), dtype=torch.bool)
        frei[self.frei()] = True
        for schub in (5.0, -5.0):
            r = self.km.klemmen(self.km.r0 + schub)
            self.assertTrue(torch.equal(r[~frei], self.km.r0[~frei].clamp(self.km.fm.lo[~frei], self.km.fm.hi[~frei])))
            self.assertTrue(bool(((r[frei] >= self.km.fm.lo[frei]) & (r[frei] <= self.km.fm.hi[frei])).all()))
            self.assertTrue(torch.equal(r[frei], (self.km.fm.hi if schub > 0 else self.km.fm.lo)[frei]))

    def test_regler_zurueck_ins_woerterbuch(self):
        aus = self.km.regler(self.km.r0, self.regler)
        self.assertEqual(sorted(aus), sorted(self.regler))
        for n, v in self.regler.items():
            self.assertAlmostEqual(aus[n], v, delta=1e-4, msg=n)
        i = next(j for j in self.frei() if float(self.km.r0[j]) + 0.1 <= float(self.km.fm.hi[j]))
        r = self.km.r0.clone()
        r[i] = r[i] + 0.1
        neu = self.km.regler(r, self.regler)
        geaendert = [n for n in set(neu) | set(self.regler) if abs(neu.get(n, 0.0) - self.regler.get(n, 0.0)) > 1e-4]
        self.assertEqual(geaendert, [self.km.fm.namen[i]])

    def test_lineare_naeherung_nah_an_der_formung(self):
        """Der freie Regler mit der größten Wirkung, ± 0,1 um die Figur: Vorhersage gegen `G9formung` an den 4.000 Punkten (RMS)."""
        from Genesis9.formung import G9formung
        fm, km = self.km.fm, self.km
        i = max(self.frei(), key=lambda j: float(fm.liste[j].get('wirkung_mm') or 0))
        for delta in (0.1, -0.1):
            r = km.r0.clone()
            r[i] = r[i] + delta
            r = km.klemmen(r)
            if float((r - km.r0).abs().max()) == 0:
                continue
            vor = km.ruhe(r)[0] - self.n.ruhe[km.wahl]
            f = G9formung(dict(self.regler, **{fm.namen[i]: float(r[i])}))
            echt = np.array(f.punkte(), dtype=np.float64)[:len(self.n.ruhe)]
            echt[:, 1] -= f.boden()
            soll = torch.as_tensor(echt, dtype=torch.float32)[km.wahl] - self.n.ruhe[km.wahl]
            wirkung, fehler = float(soll.norm(dim=1).pow(2).mean().sqrt()), float((vor - soll).norm(dim=1).pow(2).mean().sqrt())
            self.assertGreater(wirkung, 0.005, fm.namen[i])
            self.assertLess(fehler, 0.1 * wirkung, (fm.namen[i], delta, wirkung, fehler))

    @staticmethod
    def volumen(x, dreiecke):
        x, d = torch.as_tensor(x, dtype=torch.float64), dreiecke.long()
        return float((x[d[:, 0]] * torch.linalg.cross(x[d[:, 1]], x[d[:, 2]], dim=1)).sum() / 6)

    def test_volumen_an_den_reglern_der_figur_ist_das_der_figur(self):
        """Gewicht je Job (Edgar 24.10.2026: „ca. 86 kg“): bei r = Figur genau das Volumen des gebauten Käfigs (Divergenzsatz wie `nurfotos_einpassen.masse`)."""
        self.assertAlmostEqual(float(self.km.volumen(self.km.r0)), self.volumen(self.n.ruhe, self.n.dreiecke), delta=1e-6)

    def test_volumen_naeherung_folgt_der_formung(self):
        """Der freie Regler mit der größten Wirkung, + 0,1: vorhergesagte Volumenänderung gegen den echt geformten Käfig — höchstens 20 % der Änderung daneben (Setzung)."""
        from Genesis9.formung import G9formung
        fm, km = self.km.fm, self.km
        i = max(self.frei(), key=lambda j: float(fm.liste[j].get('wirkung_mm') or 0))
        r = km.r0.clone()
        r[i] = r[i] + 0.1
        r = km.klemmen(r)
        f = G9formung(dict(self.regler, **{fm.namen[i]: float(r[i])}))
        echt = np.array(f.punkte(), dtype=np.float64)[:len(self.n.ruhe)]
        echt[:, 1] -= f.boden()
        v0 = self.volumen(self.n.ruhe, self.n.dreiecke)
        soll, vor = self.volumen(echt, self.n.dreiecke) - v0, float(km.volumen(r)) - v0
        self.assertGreater(abs(soll), 1e-4, fm.namen[i])
        self.assertLess(abs(vor - soll), 0.2 * abs(soll), (fm.namen[i], soll, vor))

    def test_kopfform_null_an_der_figur_spuerbar_fuer_einen_kopfregler(self):
        """Den Kopf formt die KopfKI: `kopfform` misst, was die Regler zusammen am Kopf ändern (Lauf 5: 145 Regler, jeder ≤ 2 mm, zusammen im Gesicht bis 10 mm)."""
        fm, km = self.km.fm, self.km
        self.assertLess(float(km.kopfform(km.r0)), 1e-5)
        i = max((j for j, r in enumerate(fm.liste) if r.get('bereich') == 'kopf'), key=lambda j: float(fm.liste[j].get('wirkung_mm') or 0))
        r = km.r0.clone()
        r[i] = fm.hi[i] if float(fm.hi[i] - km.r0[i]) > float(km.r0[i] - fm.lo[i]) else fm.lo[i]
        self.assertGreater(float(km.kopfform(r)), 0.001, fm.namen[i])
