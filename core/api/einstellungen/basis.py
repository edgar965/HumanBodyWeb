# -*- coding: utf-8 -*-
"""Einstellungsseite — der Ablauf, den alle sechs Seiten teilen.

WARUM (Umbau 17.08.2026)
========================
`core/api/einstellungen.py` hatte 332 Zeilen und sechs freie Funktionen mit
demselben Rumpf:

    def app_settings_X(request):
        s = AppSettings.load()
        if request.method == 'POST':
            try:
                … Felder …
                s.save()
                messages.success(request, 'Settings saved.')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid value.')
            return redirect('settings_X')
        return render(request, 'settings_X.html', { … })

Gemeldet von `freie-funktionen` (Kriterium 1), `dateigroesse` (Kriterium 2) und
`doppelcode` (Kriterium 6) gleichzeitig. Der Rumpf steht jetzt hier, und jede
Seite sagt nur noch, WAS sie übernimmt und WAS ihre Vorlage braucht.

Die Bauform ist dieselbe wie bei `TheatreEinstellungenSeite` (17.08.2026):
Djangos `View` mit `get` und `post`, dazu ein `as_view()` mit gesetztem
`__name__` — ohne den heißen alle Ansichten in Berichten `view`.
"""

import logging

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from ...models import AppSettings

logger = logging.getLogger('core')


class Einstellungsseite(View):
    """GET zeigt das Formular, POST übernimmt die Felder und leitet zurück."""

    #: Vorlage der Seite.
    VORLAGE = ''
    #: Name der URL, auf die nach dem Speichern umgeleitet wird.
    ROUTE = ''
    #: Meldung nach erfolgreichem Speichern.
    ERFOLG = 'Settings saved.'

    def get(self, request):
        s = AppSettings.load()
        return render(request, self.VORLAGE, {'settings': s, **self.kontext(s)})

    def post(self, request):
        s = AppSettings.load()
        try:
            self.uebernehmen(s, request.POST)
            s.save()
            messages.success(request, self.ERFOLG)
        except (ValueError, TypeError):
            logger.debug('%s: unbrauchbarer Wert', self.ROUTE, exc_info=True)
            messages.error(request, 'Invalid value.')
        return redirect(self.ROUTE)

    # ------------------------------------------------------ je Seite besetzen

    def uebernehmen(self, s, post):
        """Formularfelder in die Einstellungen schreiben (ohne `save`)."""
        raise NotImplementedError

    def kontext(self, s):
        """Zusätzliches für die Vorlage — `settings` steht schon drin."""
        return {}

    # ---------------------------------------------------------------- Anmeldung

    @classmethod
    def ansicht(cls, name):
        """`as_view()` mit sprechendem `__name__` für urls.py und Berichte."""
        ziel = cls.as_view()
        ziel.__name__ = name
        return ziel
