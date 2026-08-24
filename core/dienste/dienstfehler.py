# -*- coding: utf-8 -*-
"""Eine Ablehnung mit HTTP-Kennzahl — die gemeinsame Basis der Verwaltungsdienste.

WARUM (17.08.2026): `BvhFehler` und `KleiderFehler` waren Zeile für Zeile
dieselbe Klasse — Werkzeug `doppelrumpf` meldete beide Rümpfe UND beide
`__init__` als Gruppe. Die zweite entstand, weil die erste als Vorlage diente;
so wächst dieselbe Klasse mit jedem neuen Dienst noch einmal.

Die Unterklassen bleiben, denn ein Aufrufer will unterscheiden können, was
schiefging: `except BvhFehler` fängt nicht die Kleiderverwaltung mit. Sie
erben aber nur noch, statt sich zu wiederholen.

WOZU DIE KENNZAHL: Der Endpunkt macht daraus JSON —
`JsonResponse({'error': e.text}, status=e.kennzahl)`. Damit steht die
Entscheidung „400 oder 404 oder 409" im Dienst, wo sie hingehört, und nicht in
der HTTP-Schale, die den Fall nicht kennt.
"""


class DienstFehler(Exception):
    """Ablehnung mit HTTP-Kennzahl. Vorgabe 400 — die Anfrage war falsch."""

    #: Wenn kein Aufrufer etwas anderes sagt: „so nicht" statt „gibt es nicht".
    VORGABE = 400

    def __init__(self, text, kennzahl=VORGABE):
        super().__init__(text)
        self.text = text
        self.kennzahl = kennzahl
