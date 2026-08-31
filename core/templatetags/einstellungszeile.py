# -*- coding: utf-8 -*-
u"""`{% zahl %}` und `{% kaestchen %}` — eine Einstellungszeile aus dem Register.

WARUM (30.08.2026, Befund `jsbefunde`/lange Zeilen)
===================================================
Als `{% include %}` mit benannten Angaben war eine Einstellungszeile 215 bis
310 Zeichen lang::

    {% include "_einstellungen_zahl.html" with titel="MediaPipe Tracking
       Confidence" beschriftung="Mindest-Konfidenz für das Pose-Tracking
       (0.0–1.0). Niedrig = weniger Redetections." feld="mp_min_tracking_
       confidence" wert=settings.mp_min_tracking_confidence min="0.0"
       max="1.0" schritt="0.05" %}

Umbrechen geht nicht (Djangos Lexer kennt kein DOTALL, siehe `regler.py`).
Die Länge steckt aber gar nicht in der Zeile, sondern in dem, was doppelt
darin steht: Titel, Erklärung und Grenzen, die es am Model-Feld schon gibt.
Seit sie im Register stehen (`core/daten/einstellungsfelder.py`), bleibt::

    {% zahl "mp_min_tracking_confidence" %}

DER WERT KOMMT AUS DEM KONTEXT, nicht als Angabe: `takes_context` holt ihn
mit `getattr(settings, kennung)`. Wer ihn übergeben müsste, könnte ein Feld
mit dem Wert eines anderen zeigen — und die Seite sähe richtig aus.

DER ERSTE PARAMETER HEISST `context`, englisch: Django prüft den NAMEN und
lehnt die Marke sonst ab („is decorated with takes_context=True so it must
have a first argument of 'context'"). Das ist keine Stilentscheidung.
"""
from django import template

from ..daten.einstellungsfelder import Einstellungsfelder

register = template.Library()


class Einstellungszeile:
    u"""Was beide Marken gemeinsam haben: Register nachschlagen, Wert holen."""

    @staticmethod
    def kontext(context, kennung):
        u"""Der Vorlagen-Kontext einer Zeile: Register plus aktueller Wert.

        FEHLT `settings` IM KONTEXT, IST DAS EIN FEHLER — eine Zeile ohne
        Wert zeigt den Anfangswert des Feldes und sieht dabei aus wie eine
        gespeicherte Einstellung. Wer sie speichert, überschreibt still den
        echten Wert.
        """
        einstellungen = context.get('settings')
        if einstellungen is None:
            raise KeyError(
                u'`settings` fehlt im Kontext — `{%% zahl "%s" %%}` kann '
                u'seinen Wert nicht lesen' % kennung)
        return Einstellungsfelder.feld(kennung).als_kontext(
            kennung, getattr(einstellungen, kennung))


@register.inclusion_tag('_einstellungen_zahl.html', takes_context=True)
def zahl(context, kennung):
    u"""Eine Einstellungszeile mit Zahlenfeld.

    @param kennung Feldname in `AppSettings`; Titel, Text und Grenzen
                   kommen aus `Einstellungsfelder`
    """
    # Dictionary gewollt: Es IST der Kontext der eingebundenen Vorlage.
    return Einstellungszeile.kontext(context, kennung)


@register.inclusion_tag('_einstellungen_animation.html', takes_context=True)
def animation(context, kennung, auswahl, wertformat=''):
    """Eine Einstellungszeile mit Animations-Auswahlfeld.

    @param kennung   Feldname in `AppSettings`
    @param auswahl   `id` des Auswahlfelds — das JS spricht es darüber an,
                     und zwei Felder auf einer Seite brauchen zwei Kennungen
    @param wertformat wahlweise `pfad`, wenn der Wert ein Dateipfad ist
    """
    # Dictionary gewollt: Es IST der Kontext der eingebundenen Vorlage.
    daten = Einstellungszeile.kontext(context, kennung)
    # Die Namen, unter denen `_anim_selector.html` sie erwartet. Dadurch
    # kommt der Baustein ohne `{% include … with … %}` aus — und genau das
    # Tag war es, das sich NICHT umbrechen laesst (Djangos Lexer kennt kein
    # DOTALL; ein Tag ueber zwei Zeilen wird still zu Text).
    daten['field_name'] = kennung
    daten['current_value'] = daten['wert']
    daten['selector_id'] = auswahl
    daten['wertformat'] = wertformat
    # WAS DIE SEITE MITBRINGT, muss ausdruecklich durchgereicht werden: Ein
    # `{% include %}` erbt den Seitenkontext, ein `inclusion_tag` NICHT.
    # Ohne `anim_kategorien` zeigt das Auswahlfeld keine einzige Animation
    # mehr — und die Seite kommt trotzdem mit 200.
    for name in ('anim_kategorien', 'anim_fehlt'):
        daten[name] = context.get(name)
    return daten


@register.inclusion_tag('_einstellungen_kaestchen.html', takes_context=True)
def kaestchen(context, kennung):
    u"""Eine Einstellungszeile mit Ankreuzfeld.

    @param kennung Feldname in `AppSettings`; Titel, Text und die Aufschrift
                   neben dem Kästchen kommen aus `Einstellungsfelder`
    """
    # Dictionary gewollt: Es IST der Kontext der eingebundenen Vorlage.
    return Einstellungszeile.kontext(context, kennung)
