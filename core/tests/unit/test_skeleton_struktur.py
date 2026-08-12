# -*- coding: utf-8 -*-
"""Wächter für die Klassenstruktur von `humanbody_core.skeleton.skeleton`.

WARUM DIESER TEST EXISTIERT (12.08.2026)
----------------------------------------
In dieser Datei stand `_delta_normalize_bvh` ohne Einrückung mitten in der Klasse
`Skeleton` (eingefügt mit Commit `bc384f8`). Damit endete die Klasse dort, und
alles Folgende — `__init__`, die vier IK-Properties, `bone_names` und die rund
120 Zeilen von `conversion_map` — lag als lokale Funktion INNERHALB dieser
Modulfunktion. Rund 300 Zeilen waren unerreichbar.

Python meldet das nicht: Die Datei übersetzt fehlerfrei, die Anwendung läuft,
und `hasattr(Skeleton, 'conversion_map')` ist einfach `False`. Aufgefallen ist es
erst zufällig beim Aufräumen der `except`-Blöcke, Monate später.

Dieser Test prüft die Erreichbarkeit. Er kostet Millisekunden und schlägt an,
sobald wieder eine Funktion ohne Einrückung in den Klassenkörper gerät.

Aufruf:  python manage.py test core
"""
from django.test import SimpleTestCase

from humanbody_core.skeleton.skeleton import Skeleton, SkeletonRigify, SkeletonMeta


class SkeletonStrukturTest(SimpleTestCase):
    """Die Methoden der Klasse müssen Methoden der Klasse sein."""

    #: Was durch den Einrückungsfehler verschluckt worden war.
    ERWARTET = ('conversion_map', 'bone_names', 'deformation_bone_map',
                'left_arm_ik', 'right_arm_ik', 'left_leg_ik', 'right_leg_ik')

    def test_alle_methoden_sind_erreichbar(self):
        fehlend = [n for n in self.ERWARTET if not hasattr(Skeleton, n)]
        self.assertEqual(
            fehlend, [],
            'Unerreichbar: %s — steht wieder eine Funktion ohne Einrueckung im '
            'Klassenkoerper? Siehe Docu/befund_skeleton_einrueckung.md' % fehlend)

    def test_klasse_hat_eigenen_konstruktor(self):
        """`Skeleton.__init__` war der von `object` — der eigene lief nie."""
        self.assertIsNot(Skeleton.__init__, object.__init__)

    def test_modulfunktion_liegt_nicht_im_klassenkoerper(self):
        """`_delta_normalize_bvh` muss eine Modulfunktion bleiben.

        Als Attribut der Klasse wäre sie wieder an der falschen Stelle."""
        from humanbody_core.skeleton import skeleton as modul
        self.assertTrue(callable(getattr(modul, '_delta_normalize_bvh', None)),
                        'die Modulfunktion fehlt')
        self.assertFalse(hasattr(Skeleton, '_delta_normalize_bvh'),
                         '_delta_normalize_bvh haengt an der Klasse — steht sie '
                         'wieder im Klassenkoerper?')

    def test_unterklassen_bleiben_baubar(self):
        """Der wieder aktive `__init__` darf die Unterklassen nicht stören.

        Sie rufen `super().__init__()` nicht auf, und mit `preset=None` tut der
        Konstruktor nichts — geprüft, damit das so bleibt."""
        for kls in (SkeletonRigify, SkeletonMeta):
            with self.subTest(klasse=kls.__name__):
                self.assertIsNotNone(kls())

    def test_formatklassen_bleiben_baubar(self):
        """Die acht Quellformate haben keinen eigenen Konstruktor — sie laufen
        jetzt durch `Skeleton.__init__(preset=None)`."""
        from humanbody_core.skeleton import formats
        gebaut = 0
        for name in dir(formats):
            kls = getattr(formats, name)
            if isinstance(kls, type) and issubclass(kls, Skeleton) and kls is not Skeleton:
                with self.subTest(klasse=name):
                    self.assertIsNotNone(kls())
                    gebaut += 1
        self.assertGreaterEqual(gebaut, 8, 'weniger Formatklassen gefunden als erwartet')
