# -*- coding: utf-8 -*-
"""Einen Effektauftrag ueber die Seite starten, ohne dass ein Lauf beginnt.

Stand zweimal gleich in `test_effekte` und `test_effekte_figur` (Befund
`doppelrumpf`, 17.09.2026): `Effektlauf.starten` wird abgefangen, die
Antwort des Endpunkts und die Attrappe kommen zurueck.
"""

import json
from unittest import mock

from django.urls import reverse

from core.effekte.effektlauf import Effektlauf


class Effektstart:
    @staticmethod
    def senden(client, nutzlast):
        """`(antwort, start)` — `start` ist die Attrappe von `Effektlauf.starten`."""
        with mock.patch.object(Effektlauf, "starten") as start:
            antwort = client.post(
                reverse("effekte_start"), data=json.dumps(nutzlast), content_type="application/json"
            )
        return antwort, start
