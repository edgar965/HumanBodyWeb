# -*- coding: utf-8 -*-
"""`{% zahl %}` und `{% kaestchen %}` — eine Einstellungszeile aus dem Register.

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
    """Was beide Marken gemeinsam haben: Register nachschlagen, Wert holen."""

    @staticmethod
    def kontext(context, kennung):
        """Der Vorlagen-Kontext einer Zeile: Register plus aktueller Wert.

        FEHLT `settings` IM KONTEXT, IST DAS EIN FEHLER — eine Zeile ohne
        Wert zeigt den Anfangswert des Feldes und sieht dabei aus wie eine
        gespeicherte Einstellung. Wer sie speichert, überschreibt still den
        echten Wert.
        """
        einstellungen = context.get('settings')
        if einstellungen is None:
            raise KeyError(
                '`settings` fehlt im Kontext — `{%% zahl "%s" %%}` kann seinen Wert nicht lesen' % kennung
            )
        return Einstellungsfelder.feld(kennung).als_kontext(kennung, getattr(einstellungen, kennung))


@register.inclusion_tag('_einstellungen_zahl.html', takes_context=True)
def zahl(context, kennung):
    """Eine Einstellungszeile mit Zahlenfeld.

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


@register.inclusion_tag('_einstellungen_modell.html', takes_context=True)
def modell(context, kennung, leer='', figurarten=False):
    """Eine Einstellungszeile „Standard-Modell" mit dem Figurwahl-Dialog.

    Edgar (21.09.2026): „bei Modellauswahl standard bitte den neuen
    Modellauswahldialog von /settings/scene/. Korrigiere das auch bei den
    anderen." Bis dahin: `<select>` mit `Modellfeld` auf vier Seiten, ein
    `<select>` aus `Modellvorlagen.namen()` auf drei weiteren — sieben
    Fassungen, keine kannte die Körpertypen.

    @param kennung    Feldname in `AppSettings`; der Wert ist der Modellname
    @param leer       Anzeigetext für „kein Modell" — wenn gesetzt, darf das
                      Feld leer sein und bekommt einen Knopf zum Leeren
    @param figurarten True nur für die Szene: sie lädt jede Figurart, die
                      Wahl trägt dann Figurart und Bereich in `ui_prefs`
                      (`<kennung>_quelle`, `<kennung>_bereich`) mit
    """
    # Dictionary gewollt: Es IST der Kontext der eingebundenen Vorlage.
    daten = Einstellungszeile.kontext(context, kennung)
    daten['leer'] = leer
    daten['figurarten'] = figurarten
    prefs = context['settings'].ui_prefs or {}
    daten['quelle'] = prefs.get(kennung + '_quelle') or 'modell'
    daten['bereich'] = prefs.get(kennung + '_bereich') or 'gespeichert'
    return daten


@register.inclusion_tag('_einstellungen_kaestchen.html', takes_context=True)
def kaestchen(context, kennung):
    """Eine Einstellungszeile mit Ankreuzfeld.

    @param kennung Feldname in `AppSettings`; Titel, Text und die Aufschrift
                   neben dem Kästchen kommen aus `Einstellungsfelder`
    """
    # Dictionary gewollt: Es IST der Kontext der eingebundenen Vorlage.
    return Einstellungszeile.kontext(context, kennung)
