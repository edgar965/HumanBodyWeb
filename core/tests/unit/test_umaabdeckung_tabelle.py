# -*- coding: utf-8 -*-
"""Jedes Gegenstueck der Abdeckungstabelle existiert, jede Probe auch.

Herausgeloest aus `test_umaabdeckung` (12.09.2026, sieben Klassen in
einer Datei); die Tabelle gegen den C#-Quelltext prueft dort weiter
`Vollstaendig`.
"""

import unittest

from ._umaabdeckung import Abdeckung, Umaquelle


class TabelleIstBelegt(unittest.TestCase):
    """Jedes Gegenstück existiert, jede Probe auch."""

    databases = set()

    @staticmethod
    def _hat(klasse, name):
        """Gibt es das Attribut — auch, wenn es erst `__init__` setzt?

        `hasattr` allein reicht nicht: `Bindung.ausgangslage` und
        `Kleidungskonformer._baum` entstehen im Rumpf und stehen der
        KLASSE nicht an. Ein Test, der nur `hasattr` fragt, meldete
        neun echte Gegenstücke als fehlend.
        """
        if hasattr(klasse, name):
            return True
        import inspect

        try:
            quelle = inspect.getsource(klasse)
        # stumm gewollt: ohne Quelltext (eingebaute Klasse) gibt es kein Feld zu finden
        except OSError, TypeError:
            return False
        return ('self.%s =' % name) in quelle or ('self.%s:' % name) in quelle

    def test_jedes_gegenstueck_existiert(self):
        fehlt = []
        for eintrag in Abdeckung.eintraege():
            if not eintrag.gegenstueck:
                continue
            klasse, _, name = eintrag.gegenstueck.partition('.')
            ziel = Umaquelle.KLASSEN.get(klasse)
            if ziel is None or not self._hat(ziel, name):
                fehlt.append('%s -> %s' % (eintrag.uma, eintrag.gegenstueck))
        self.assertEqual(fehlt, [], 'Gegenstücke, die es nicht gibt: %s' % ', '.join(fehlt))

    def test_jede_probe_ist_eine_echte_testmethode(self):
        """Eine Probe, die es nicht gibt, ist eine Behauptung.

        Aufgelöst wird über das Testpaket dieses Ordners — `Bindung` und
        `Kleidungskonformer` sind Instanzattribute, deshalb steht ihr
        Nachweis über `hasattr` in `test_jedes_gegenstueck_existiert`
        getrennt.
        """
        import importlib

        fehlt = []
        for eintrag in Abdeckung.eintraege():
            if not eintrag.probe:
                continue
            modul, klasse, methode = eintrag.probe.split('.')
            try:
                geladen = importlib.import_module('core.tests.unit.%s' % modul)
            # stumm gewollt: ein fehlendes Modul wird in `fehlt` gesammelt und unten zugesichert
            except ImportError:
                fehlt.append('%s (Modul %s)' % (eintrag.probe, modul))
                continue
            ziel = getattr(geladen, klasse, None)
            if ziel is None or not hasattr(ziel, methode):
                fehlt.append(eintrag.probe)
        self.assertEqual(fehlt, [], 'Proben, die es nicht gibt: %s' % ', '.join(fehlt))

    def test_nichts_ist_unbegruendet_weggelassen(self):
        """`unity` und `intern` brauchen einen Grund — die Klasse erzwingt
        das schon beim Bauen; hier steht die Gegenprobe dazu."""
        from UMA_Python.abdeckung import Eintrag

        with self.assertRaises(ValueError):
            Eintrag('Irgendwas', 'unity')
        with self.assertRaises(ValueError):
            Eintrag('Irgendwas', 'portiert', 'Netzgeometrie.seite')
        with self.assertRaises(ValueError):
            Eintrag('Irgendwas', 'zauberei')

    def test_die_anteile_stimmen(self):
        """Eine Zahl, die man in den Bericht schreiben kann — und die rot
        wird, wenn jemand einen Eintrag stumm auf `unity` setzt."""
        gerechnet = len(Abdeckung.nach_art('portiert')) + len(Abdeckung.nach_art('anders'))
        self.assertGreaterEqual(gerechnet, 45)
        self.assertLessEqual(len(Abdeckung.nach_art('intern')), 5)


# ===================================================================== Proben
