"""Basis-Klassen für die Oberflächenfälle.

TestCase: repräsentiert einen einzelnen Fall.
TestCategory: Sammlung zusammengehöriger Fälle.

UMBAU 17.08.2026 (Ansage: „Halte dich an die djangoBase test implementierung und
baue nichts neues, leite nur ab")
=====================================================================
Diese Fälle liefen über einen eigenen Läufer und eine eigene API. Sie sind jetzt
reguläre Django-Tests: `core/tests/ui/test_oberflaeche.py` macht aus jeder
Kategorie eine `django.test.TestCase`-Klasse mit je einer Methode pro Fall.
Damit fährt `manage.py test` sie mit, djangoBases Hilfe → Tests listet sie, die
Laufzeiten stehen in `Testhistorie`, und `skills.testdeckung` findet sie.

Übrig bleibt hier, was die Fälle SELBST brauchen: das Sammeln der `test_*`-
Methoden und das Ergebnis eines Falls. Wie der Fall den Server erreicht, steht in
`kanal.py` — in-process im Testlauf, über das Netz beim Lauf gegen den echten
Server.
"""

from .kanal import Kanal


class Netzruf:
    """Der Weg zum Server — in-process im Testlauf, sonst ueber das Netz.

    Als Klasse statt einer freien Funktion (Befund `freie-funktionen`,
    27.08.2026). Welcher Kanal gilt, entscheidet `kanal.Kanal`.
    """

    #: Sekunden, die eine Antwort hoechstens brauchen darf.
    FRIST_S = 15

    @classmethod
    def senden(cls, pfad, method='GET', data=None, files=None, timeout=None):
        """Anfrage ueber den gerade gueltigen Kanal -> `(Status, Woerterbuch)`."""
        return Kanal.aktueller().senden(
            pfad, method=method, data=data, files=files,
            timeout=cls.FRIST_S if timeout is None else timeout)


class TestCase:
    """Ein einzelner Fall. Jedes fn liefert einen Bool oder (bool, detail)."""

    def __init__(self, name, fn, description=''):
        self.name = name
        self.fn = fn
        self.description = description

    def run(self):
        """Fuehrt den Fall aus; liefert das Woerterbuch aus `Fallergebnis`."""
        from ._fallergebnis import Fallergebnis
        try:
            return Fallergebnis.aus_rueckgabe(self.fn(), self.name,
                                              self.description).als_dict()
        except Exception as fehler:                               # noqa: BLE001
            # Absichtlich jede Ausnahme: Ein Fall darf den ganzen Lauf nicht
            # mitnehmen — sein Fehler ist sein Ergebnis.
            return Fallergebnis.aus_ausnahme(fehler, self.name,
                                             self.description).als_dict()


class TestCategory:
    """Basis-Klasse für Kategorien. Unterklassen definieren test_*-Methoden."""

    name = 'Unbenannte Kategorie'
    description = ''

    @classmethod
    def cases(cls):
        """Sammelt alle test_*-Methoden als `TestCase`-Objekte."""
        faelle = []
        for name in dir(cls):
            if not name.startswith('test_'):
                continue
            fn = getattr(cls, name)
            if not callable(fn):
                continue
            faelle.append(TestCase(
                name=name.replace('test_', '').replace('_', ' ').title(),
                fn=fn,
                description=fn.__doc__.strip() if fn.__doc__ else ''))
        return faelle

    @classmethod
    def run_all(cls):
        """Führt alle Fälle der Kategorie aus; liefert die Ergebnisliste."""
        return [fall.run() for fall in cls.cases()]
