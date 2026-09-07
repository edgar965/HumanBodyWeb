# -*- coding: utf-8 -*-
u"""Mhmakrowerte — die Umrechnung der neun Makroregler in Zielfaktoren.

Portiert aus `MakeHuman/makehuman/apps/human.py`. Hier stehen die Zahlen fest,
die MakeHumans Kommentar selbst nennt (`_setAgeVals`):

    1 Jahr     10 Jahre    25 Jahre           90 Jahre
    baby        child       young              old
    |-------------|------------|-----------------|
    0          0,1875        0,5                1

Warum das eigene Faelle braucht: Die Alterskurve ist die einzige der neun, die
nicht symmetrisch ist, und ihre Knickstellen sind der Grund, warum ein Kind
von 10 Jahren (`age = 0,1875`) rein aus `child` besteht und nicht aus einer
Mischung. Wer die 5,333 oder die 3,2 vertippt, bekommt eine Figur, die überall
ein bisschen falsch ist — und nirgends erkennbar.
"""

import unittest

from core.dienste.mhmakrowerte import Mhmakrowerte


class MhmakrowerteTest(unittest.TestCase):

    databases = []

    def _faktoren(self, **werte):
        return Mhmakrowerte(werte).faktoren()

    # ------------------------------------------------------------ Geschlecht

    def test_geschlecht_ist_linear(self):
        self.assertAlmostEqual(self._faktoren(gender=1.0)['male'], 1.0)
        self.assertAlmostEqual(self._faktoren(gender=1.0)['female'], 0.0)
        mitte = self._faktoren(gender=0.5)
        self.assertAlmostEqual(mitte['male'], 0.5)
        self.assertAlmostEqual(mitte['female'], 0.5)

    # ------------------------------------------------------------------ Alter

    def test_alter_null_ist_ganz_baby(self):
        f = self._faktoren(age=0.0)
        self.assertAlmostEqual(f['baby'], 1.0)
        self.assertAlmostEqual(f['child'], 0.0)
        self.assertAlmostEqual(f['young'], 0.0)
        self.assertAlmostEqual(f['old'], 0.0)

    def test_alter_am_knick_ist_ganz_kind(self):
        u"""0,1875 = zehn Jahre — der Knickpunkt aus MakeHumans Kommentar."""
        f = self._faktoren(age=0.1875)
        self.assertAlmostEqual(f['child'], 1.0, places=2)
        self.assertLess(f['baby'], 0.01)
        self.assertAlmostEqual(f['young'], 0.0)

    def test_alter_mitte_ist_ganz_jung(self):
        f = self._faktoren(age=0.5)
        self.assertAlmostEqual(f['young'], 1.0)
        self.assertAlmostEqual(f['old'], 0.0)
        self.assertAlmostEqual(f['baby'], 0.0)
        self.assertAlmostEqual(f['child'], 0.0)

    def test_alter_eins_ist_ganz_alt(self):
        f = self._faktoren(age=1.0)
        self.assertAlmostEqual(f['old'], 1.0)
        self.assertAlmostEqual(f['young'], 0.0)

    def test_alter_summiert_sich_immer_auf_eins(self):
        for schritt in range(0, 101):
            f = self._faktoren(age=schritt / 100.0)
            summe = f['baby'] + f['child'] + f['young'] + f['old']
            self.assertAlmostEqual(summe, 1.0, places=6,
                                   msg='age=%.2f' % (schritt / 100.0))

    # ------------------------------------------------------------ dreiteilig

    def test_gewicht_in_der_mitte_ist_durchschnitt(self):
        f = self._faktoren(weight=0.5)
        self.assertAlmostEqual(f['averageweight'], 1.0)
        self.assertAlmostEqual(f['minweight'], 0.0)
        self.assertAlmostEqual(f['maxweight'], 0.0)

    def test_gewicht_an_den_enden(self):
        self.assertAlmostEqual(self._faktoren(weight=1.0)['maxweight'], 1.0)
        self.assertAlmostEqual(self._faktoren(weight=0.0)['minweight'], 1.0)

    def test_dreiteilige_summieren_sich_auf_eins(self):
        for regler in Mhmakrowerte.DREITEILIG:
            for schritt in (0, 25, 50, 75, 100):
                f = self._faktoren(**{regler: schritt / 100.0})
                klein, mitte, gross, _ = Mhmakrowerte.DREITEILIG[regler]
                self.assertAlmostEqual(f[klein] + f[mitte] + f[gross], 1.0,
                                       places=6,
                                       msg='%s=%d' % (regler, schritt))

    # ----------------------------------------------------------------- Rasse

    def test_rassen_werden_auf_eins_normiert(self):
        u"""Das Verhältnis bleibt, die Summe wird 1.

        Die Werte liegen absichtlich UNTER 1: Gekappt wird zuerst (wie in
        `MacroModifier.clampValue`), erst danach normiert. Mit 1/1/2 käme
        deshalb 1/1/1 heraus und der Fall prüfte nichts.
        """
        f = self._faktoren(african=0.2, asian=0.2, caucasian=0.4)
        self.assertAlmostEqual(f['african'], 0.25)
        self.assertAlmostEqual(f['asian'], 0.25)
        self.assertAlmostEqual(f['caucasian'], 0.5)

    def test_rassen_alle_null_ergibt_drittel(self):
        f = self._faktoren(african=0.0, asian=0.0, caucasian=0.0)
        for rasse in Mhmakrowerte.RASSEN:
            self.assertAlmostEqual(f[rasse], 1.0 / 3)

    def test_vorgabe_ist_je_ein_drittel(self):
        f = self._faktoren()
        for rasse in Mhmakrowerte.RASSEN:
            self.assertAlmostEqual(f[rasse], 1.0 / 3)

    # ------------------------------------------------------------- Robustheit

    def test_werte_werden_gekappt_und_unbekanntes_faellt_weg(self):
        werte = Mhmakrowerte({'gender': 5.0, 'age': -3.0, 'quatsch': 1.0}).werte
        self.assertEqual(werte['gender'], 1.0)
        self.assertEqual(werte['age'], 0.0)
        self.assertNotIn('quatsch', werte)

    def test_unlesbares_bleibt_bei_der_vorgabe(self):
        werte = Mhmakrowerte({'gender': 'viel'}).werte
        self.assertEqual(werte['gender'], 0.5)


if __name__ == '__main__':
    unittest.main()
