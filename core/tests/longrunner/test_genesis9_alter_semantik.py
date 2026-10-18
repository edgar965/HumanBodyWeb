# -*- coding: utf-8 -*-
u"""Lebensalter, Alter und die Familienregler am Ergebnis gemessen (17.10.2026): macht „jung" kleiner, macht „alt" keinen Bauch, wirkt jeder Regler.

Edgar, 17.10.2026: „lebensalter Regler jung funktioniert nicht. Teste alle Morphs, mach dir UI testcases, ob die funktionieren. Denk dir was aus, dass zum Beispiel ein lebensalter Regler kleinere
Figuren macht für ein kleines Alter und so weiter. Lebensalter Älter macht bei Ursula einen dicken Bauch, korrigiere das. … Alter regler für Jung funktioniert etwas besser als der andere, aber die
Figur sollte kleiner sein."

Gemessen wird nicht, ob eine Zahl im Regler steht, sondern was der Körper danach ist: Höhe, Bauchtiefe (Vorderkante der Mittelebene im Band 55–62 % der Höhe), Kopflage. Jede Aussage gilt für drei
Grundfiguren (Ursula, Feminine, Masculine) — die Fehler dieses Tages stammten aus EINER Grundfigur (der weiblichen Tabelle von HumanBody).

1. LEBENSALTER JUNG IST KLEINER, ABER NICHT UNTER 18 JAHREN (seit 18.10.2026, Edgar: „nur von dem untersten Bereich, wofür sie implementiert sind, also circa 18 Jahre“; Kinder kommen
   aus Genesis 1): Höhe beim Anschlag −0,29 (18 Jahre) rund 90 %, bei −0,15 (21 Jahre) rund 95 % der Vorgabe (MakeHumans Kurve; Ursula 18.10.2026: 90,3 / 95,0 %, `alter_ab18.py`);
   ein alter Wert darunter (−1 = früher 1 Jahr) gilt als 18 Jahre; bei 0 ist nichts verändert. Baby und Kind selbst prüft Fall 5b über die MakeHuman-Regler.
2. LEBENSALTER ALT IST KEIN BAUCH: bei +1 höchstens +35 mm Bauchtiefe (Ursula vorher +92 mm, jetzt +21), die Höhe sinkt höchstens 4 % und steigt nicht.
3. „WIRKT ÄLTER / JÜNGER“ (`alter:gesamt`) ÄNDERT DIE GRÖSSE NICHT (Vorschlag A, 17.10.2026 „ein Alter, ein Aussehen“; vorher −1 = 89,6 %): bei ±1 bleibt die Höhe innerhalb ±2 % der Vorgabe,
   bei +1 höchstens +25 mm Bauch (vorher +80 mm). Größe und Proportionen kommen allein vom Lebensalter.
4. BEIDE SCHIEBER STAPELN NICHT ÜBER DIE GRENZEN: Lebensalter am Anschlag und Alter −1 zusammen ergibt das Kind-Gewicht von 18 Jahren und nichts darüber (vorher 0,462 m: ein zweites Kind auf dem Baby).
5. MAKEHUMAN-MAKROS: Größe + macht größer, Größe − kleiner; Gewicht + macht die Taille breiter, − schmaler; Geschlecht + (männlich) macht größer und die Schultern breiter.
6. JEDER REGLER JEDER FAMILIE WIRKT: `hb:`, `mh:`, `sx:`, `uma:` — mindestens ein Punkt mit ≥ 0,1 mm Verschiebung in einer Richtung, keine NaN, keine Verschiebung über 3 m. (Die Regler,
   die Gelenke ohne Käfigpunkt stellen, gibt es nicht: `*_bauen` überspringt sie.)

Braucht die gebauten Ablagen (`hbmorphe_bauen` … `umamorphe_bauen`) und die Daz-Bibliothek; läuft ohne Server und ohne Browser. Geschrieben und am 17.10.2026 gefahren (Ergebnis im Bericht).
"""
import unittest

import numpy as np
from django.test import SimpleTestCase
from Genesis9.charaktere import G9charaktere
from Genesis9.formung import G9formung
from Genesis9.garderobe import G9garderobe
from Genesis9.mhmorphe import G9mhmorphe
from Genesis9.morphfamilien import G9morphfamilien
from Genesis9.pfade import G9pfade
from Genesis9.stueckstarr import G9stueckstarr

DA = G9pfade.vorhanden() and G9mhmorphe.vorhanden('mh:macro_Alter_Kind')
GRUNDFIGUREN = ('p3d_ursula', 'feminine', 'masculine')


def koerper(name, **extra):
    u"""`(Höhe, Bauchtiefe vorn, Schulterbreite)` einer Grundfigur mit zusätzlichen Reglern, in Metern."""
    regler = dict(G9charaktere.eintrag(name)['regler'])
    regler.update(extra)
    p = np.asarray(G9formung(regler).punkte())
    y0, y1 = float(p[:, 1].min()), float(p[:, 1].max())
    rel = (p[:, 1] - y0) / (y1 - y0)
    mitte = np.abs(p[:, 0]) < 0.06
    bauch = float(p[mitte & (rel > 0.55) & (rel < 0.62), 2].max())
    taille = p[(rel > 0.58) & (rel < 0.64) & (np.abs(p[:, 0]) < 0.25)]       # nur der Rumpf: die Arme der A-Haltung liegen bei dieser Höhe weiter außen
    schulter = p[(rel > 0.79) & (rel < 0.83)]
    return y1 - y0, bauch, float(np.ptp(taille[:, 0])), float(np.ptp(schulter[:, 0]))


@unittest.skipUnless(DA, 'Daz-Bibliothek oder gebaute MakeHuman-Morphs fehlen')
class AlterSemantikTest(SimpleTestCase):
    databases = set()

    def test_1_lebensalter_jung_ist_kleiner_aber_nicht_unter_18_jahren(self):
        for name in GRUNDFIGUREN:
            h0, _b, _t, _s = koerper(name)
            verhaeltnis = {v: koerper(name, **{'alter:jahre': v})[0] / h0 for v in (-1.0, -0.29, -0.15, 0.0)}
            self.assertAlmostEqual(verhaeltnis[0.0], 1.0, delta=0.002, msg='%s: Lebensalter 0 verändert nichts' % name)
            self.assertTrue(0.86 <= verhaeltnis[-0.29] <= 0.95, '%s: 18 Jahre %.3f' % (name, verhaeltnis[-0.29]))
            self.assertTrue(0.92 <= verhaeltnis[-0.15] <= 0.98, '%s: 21 Jahre %.3f' % (name, verhaeltnis[-0.15]))
            self.assertAlmostEqual(verhaeltnis[-1.0], verhaeltnis[-0.29], delta=0.001, msg='%s: −1 (früher 1 Jahr) gilt als 18 Jahre' % name)
            self.assertTrue(verhaeltnis[-0.29] < verhaeltnis[-0.15] < verhaeltnis[0.0], '%s: die Höhe wächst mit dem Alter: %s' % (name, verhaeltnis))

    def test_2_lebensalter_alt_ist_kein_bauch(self):
        for name in GRUNDFIGUREN:
            h0, b0, _t, _s = koerper(name)
            for v in (0.5, 1.0):
                h, b, _t, _s = koerper(name, **{'alter:jahre': v})
                self.assertLessEqual((b - b0) * 1000, 35.0, '%s Lebensalter %+.1f: Bauch %+.0f mm' % (name, v, (b - b0) * 1000))
                self.assertTrue(0.96 <= h / h0 <= 1.005, '%s Lebensalter %+.1f: Höhe %.3f' % (name, v, h / h0))

    def test_3_wirkt_aelter_juenger_aendert_die_groesse_nicht_und_macht_keinen_bauch(self):
        for name in GRUNDFIGUREN:
            h0, b0, _t, _s = koerper(name)
            for wert in (-1.0, 1.0):
                verhaeltnis = koerper(name, **{'alter:gesamt': wert})[0] / h0
                self.assertTrue(0.98 <= verhaeltnis <= 1.02, '%s: Alter %+.0f Höhe %.3f (nur das Aussehen, nie die Größe)' % (name, wert, verhaeltnis))
            alt = koerper(name, **{'alter:gesamt': 1.0})[1] - b0
            self.assertLessEqual(alt * 1000, 25.0, '%s: Alter +1 Bauch %+.0f mm' % (name, alt * 1000))

    def test_4_beide_schieber_stapeln_nicht_ueber_die_grenzen(self):
        f = G9formung({'alter:jahre': -0.29, 'alter:gesamt': -1.0})
        self.assertAlmostEqual(f.regler.get('mh:macro_Alter_Kind', 0.0), 0.29 / 0.625, places=6, msg='Alter −1 legt kein Kind dazu: nur das von 18 Jahren')
        self.assertEqual(f.regler.get('mh:macro_Alter_Baby', 0.0), 0.0, 'kein Baby mehr im Lebensalter')
        for name in GRUNDFIGUREN:
            h0, _b, _t, _s = koerper(name)
            beide = koerper(name, **{'alter:jahre': -0.29, 'alter:gesamt': -1.0})[0] / h0
            allein = koerper(name, **{'alter:jahre': -0.29})[0] / h0
            self.assertAlmostEqual(beide, allein, delta=0.002, msg='%s: die Höhe hängt nur am Lebensalter (0,462 m statt 0,637 m war der Fehler)' % name)

    def test_5_makehuman_makros_wirken_in_die_richtige_richtung(self):
        for name in GRUNDFIGUREN:
            h0, _b, t0, s0 = koerper(name)
            gross = koerper(name, **{'mh:macro_Groesse': 1.0})[0]
            klein = koerper(name, **{'mh:macro_Groesse': -1.0})[0]
            self.assertGreater(gross, h0 * 1.15, '%s: Größe + (%.3f gegen %.3f)' % (name, gross, h0))
            self.assertLess(klein, h0 * 0.90, '%s: Größe − (%.3f gegen %.3f)' % (name, klein, h0))
            dick = koerper(name, **{'mh:macro_Gewicht': 1.0})[2]
            duenn = koerper(name, **{'mh:macro_Gewicht': -1.0})[2]
            self.assertGreater(dick, t0 * 1.03, '%s: Gewicht + macht die Taille nicht breiter (%.3f gegen %.3f)' % (name, dick, t0))
            self.assertLess(duenn, t0 * 0.99, '%s: Gewicht − macht die Taille nicht schmaler (%.3f gegen %.3f)' % (name, duenn, t0))
            mann = koerper(name, **{'mh:macro_Geschlecht': 1.0})
            self.assertGreater(mann[0], h0 * 1.04, '%s: Geschlecht + nicht größer' % name)
            self.assertGreater(mann[3], s0 * 1.04, '%s: Geschlecht + Schultern nicht breiter (%.3f gegen %.3f)' % (name, mann[3], s0))

    def test_5b_kinder_stehen_gerade_und_ihre_anatomie_folgt_dem_becken(self):
        u"""Baby und Kind stehen gerade (Kopfknochen gegen Hüfte höchstens 30 mm von der Grundfigur, vorher +39 und +128 mm) und das starre Geograft liegt am Becken des Kindes, nicht in
        der Höhe des Erwachsenen (vorher 0,80–0,88 m über dem Boden bei einem Baby von 0,73 m; Edgar, 17.10.2026: Lebensalter −0,95). Seit das Lebensalter bei 18 Jahren beginnt
        (18.10.2026), stellt der Fall Baby und Kind direkt über die MakeHuman-Regler (Bereich „MakeHuman“)."""
        baby, kind = 'mh:macro_Alter_Baby', 'mh:macro_Alter_Kind'
        for name in GRUNDFIGUREN:
            regler = dict(G9charaktere.eintrag(name)['regler'])
            basis = {k['name']: k for k in G9formung(regler).skelett().gelenkknochen()}
            lage0 = basis['head']['kopf'][2] - basis['hip']['kopf'][2]
            for stellung in ({baby: 1.0}, {baby: 0.5, kind: 0.5}, {kind: 1.0}, {kind: 0.48}):
                f = G9formung(dict(regler, **stellung))
                k = {b['name']: b for b in f.skelett().gelenkknochen()}
                aenderung = (k['head']['kopf'][2] - k['hip']['kopf'][2]) - lage0
                self.assertLess(abs(aenderung) * 1000, 30.0, '%s %s: Kopfknochen %+.0f mm gegen die Hüfte' % (name, stellung, aenderung * 1000))
        if G9garderobe.eintrag('daz_anatomie_frau'):
            regler = dict(G9charaktere.eintrag('p3d_ursula')['regler'])
            f = G9formung(dict(regler, **{baby: 0.87, kind: 0.13}))                 # früher Lebensalter −0,95
            teile = G9garderobe.teile('daz_anatomie_frau')
            hoehe = float(np.asarray(f.punkte())[:, 1].max() - f.boden())
            y = np.vstack(G9stueckstarr.punkte(teile, f))[:, 1]
            self.assertLess(float(y.max()), 0.75 * hoehe, 'das Geograft liegt unter 75 %% der Körperhöhe (Becken), nicht über dem Kopf: %.3f gegen %.3f m' % (float(y.max()), hoehe))

    def test_6_jeder_regler_jeder_familie_wirkt(self):
        zu_klein, nan, riesig = [], [], []
        zahl = 0
        for familie in G9morphfamilien.alle():
            for r in familie.liste():
                name = r['name']
                groesste = 0.0
                for wert in (1.0, -1.0):
                    d = familie.deltas(name, wert)
                    if d is None:
                        continue
                    delta = np.asarray(d[1], dtype=float)
                    zahl += 1
                    if not np.isfinite(delta).all():
                        nan.append(name)
                        continue
                    if len(delta):
                        groesste = max(groesste, float(np.abs(delta).max()))
                if groesste > 3.0:
                    riesig.append(name)
                if groesste < 1e-4:
                    zu_klein.append(name)
        self.assertGreater(zahl, 600, 'es wurden zu wenige Richtungen geprüft')
        self.assertEqual(nan, [], 'Verschiebungen mit NaN')
        self.assertEqual(riesig, [], 'Verschiebungen über 3 m')
        self.assertEqual(zu_klein, [], 'Regler ohne Wirkung ab 0,1 mm: %s' % zu_klein[:10])
