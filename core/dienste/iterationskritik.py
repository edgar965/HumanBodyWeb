# -*- coding: utf-8 -*-
"""Iterationskritik — Weg B der Iterationen: eine lokale KI sieht Vorlage und Render und schlägt Werte vor
(30.09.2026).

Der Optimierer (Weg A) sieht nur Zahlen; er merkt nicht, DASS ein Teil fehlt oder ein Ausschnitt zu flach
ist. Die Prüf-KI bekommt die Vergleichstafel der besten Runde (`Iterationstafel`: oben Vorlage, unten Render,
je Blickwinkel) und die Liste aller Werte mit Grenzen und Bedeutung. Zurück kommt JSON: ein Urteil
(Ähnlichkeit 1–10 mit einem Satz — die Tabelle „Iterationen" zeigt es; eine Einschätzung des Modells, keine
Messung), bis zu `HOECHSTENS` Änderungen und eine Begründung. Sie darf NUR Werte des Schemas ändern und
Teile des Katalogs schalten — keinen Code schreiben; alles wird auf die Grenzen gezogen
(`Haarparameter.pruefen`). Ob der Vorschlag übernommen wird, entscheidet danach dieselbe Note wie beim
Optimierer, mit einer Toleranz (Option „Toleranz der Prüf-KI"): sonst könnte eine inhaltlich richtige
Änderung — ein Detail, das den Umriss kaum ändert — nie gegen die Zahl gewinnen.

Der Text der Frage ist allgemein gehalten (Frisur an einer Figur). Gegenüber BlenderModel fehlen das
zweite Bild (Ausschnitte der Vorderansicht) und die Liste der Einzelheiten dieses einen Kostüms; beides
gehört zu den Einzelheiten der Engine (`DETAILS`).
"""

import base64

from .haarparameter import Haarparameter
from .ollamamodelle import Ollamamodelle

__all__ = ['Iterationskritik']


class Iterationskritik:
    HOECHSTENS = 6
    #: Zuerst das Urteil (1–10), dann die Einzelurteile und die Liste dessen, was dem Modell fehlt — die Tabelle „Iterationen" zeigt es;
    #: dann die Änderungen.
    SCHEMA = {
        'type': 'object',
        'properties': {
            'aehnlichkeit': {'type': 'integer', 'enum': list(range(1, 11))},
            'urteil': {'type': 'string'},
            'details': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'bereich': {'type': 'string'},
                        'passt': {'type': 'integer', 'enum': list(range(1, 11))},
                        'abweichung': {'type': 'string'},
                    },
                    'required': ['bereich', 'passt', 'abweichung'],
                },
            },
            'fehlt_im_modell': {'type': 'array', 'items': {'type': 'string'}},
            'aenderungen': {'type': 'object', 'additionalProperties': {'type': 'number'}},
            'begruendung': {'type': 'string'},
        },
        'required': ['aehnlichkeit', 'urteil', 'details', 'fehlt_im_modell', 'aenderungen', 'begruendung'],
    }
    #: Worauf die Prüf-KI achten soll — allgemein, bis die Engine ihre Teile kennt.
    DETAILS = (
        'Frisur und Schnitt, Länge, Fülle und Volumen, Scheitel und Haaransatz, Locken und Strähnen, '
        'Farbton und Glanz'
    )

    def __init__(self, modell):
        self.modell = modell

    def frage(self, werte):
        schema = Haarparameter.schema()
        zeilen = [
            '%s = %s  (%s … %s)  %s' % (k, werte[k], e['min'], e['max'], e['titel'])
            for k, e in schema.items()
        ]
        kopf = (
            'Du bist Friseur und vergleichst eine Vorlage (Frisur an einer Figur) mit einem 3D-Modell.\n'
            'Das Bild zeigt OBEN die Vorlage aus mehreren Blickwinkeln und DARUNTER das aktuelle 3D-Modell aus genau '
            'denselben Blickwinkeln (Winkel und Übereinstimmung des Umrisses stehen darunter).\n'
            'Achte auf ALLE Details und beurteile jedes einzeln: %s.\n'
            'Antworte als JSON:\n'
            '- "aehnlichkeit": 1 (völlig anders) bis 10 (kaum zu unterscheiden), "urteil": ein Satz auf Deutsch.\n'
            '- "details": je Bereich der Liste oben ein Eintrag mit "bereich", "passt" (1–10) und "abweichung" '
            '(kurz und konkret, was anders ist — Größe, Form, Farbton).\n'
            '- "fehlt_im_modell": Details der Vorlage, die das Modell GAR NICHT hat und die keiner der Werte '
            'unten erzeugen kann.\n'
            '- "aenderungen": höchstens %d Änderungen, die das Modell der Vorlage am deutlichsten ähnlicher machen '
            '— zuerst fehlende oder überzählige Teile, dann Längen und Weiten. Farben (farbe.*) nur, wenn ein '
            'Farbton deutlich von der Vorlage abweicht. Nur Schlüssel aus der Liste, Werte innerhalb der Grenzen.\n'
            '- "begruendung": ein bis drei Sätze auf Deutsch.\n\n'
            'Das Modell wird nur über die folgenden Werte gesteuert (Schlüssel = aktueller Wert (Grenzen) '
            'Bedeutung). Schalter sind 1 (an) oder 0 (aus); Farben sind sRGB-Anteile von 0 bis 1.\n\n'
        )
        return kopf % (self.DETAILS, self.HOECHSTENS) + '\n'.join(zeilen)

    @staticmethod
    def _kodieren(pfad):
        with open(pfad, 'rb') as f:
            return base64.b64encode(f.read()).decode('ascii')

    def vorschlagen(self, werte, tafel):
        """→ (neuer Wertesatz, {begruendung, aenderungen, verworfen, modell, sekunden})."""
        antwort, zahlen = Ollamamodelle.fragen(
            self.modell, self.frage(werte), [self._kodieren(tafel)], self.SCHEMA
        )
        schema = Haarparameter.schema()
        roh = antwort.get('aenderungen') if isinstance(antwort.get('aenderungen'), dict) else {}
        gueltig = {k: v for k, v in roh.items() if k in schema and isinstance(v, (int, float))}
        verworfen = sorted(set(roh) - set(gueltig))
        gueltig = dict(list(gueltig.items())[: self.HOECHSTENS])
        neu = Haarparameter.pruefen({**werte, **gueltig})
        stufe = antwort.get('aehnlichkeit')
        return neu, {
            'modell': self.modell,
            'aehnlichkeit': stufe if isinstance(stufe, int) and 1 <= stufe <= 10 else None,
            'urteil': str(antwort.get('urteil') or '')[:500],
            'details': self._details(antwort.get('details')),
            'fehlt': [str(x)[:120] for x in (antwort.get('fehlt_im_modell') or []) if isinstance(x, str)][
                :12
            ],
            'begruendung': str(antwort.get('begruendung') or '')[:1000],
            'aenderungen': Haarparameter.unterschiede(werte, neu),
            'verworfen': verworfen,
            'sekunden': round((zahlen.get('total_duration') or 0) / 1e9, 1),
        }

    @staticmethod
    def _details(roh):
        """[{bereich, passt, abweichung}] — nur wohlgeformte Einträge, gekürzt."""
        aus = []
        for e in roh if isinstance(roh, list) else []:
            if isinstance(e, dict) and isinstance(e.get('passt'), int) and 1 <= e['passt'] <= 10:
                aus.append(
                    {
                        'bereich': str(e.get('bereich') or '')[:60],
                        'passt': e['passt'],
                        'abweichung': str(e.get('abweichung') or '')[:240],
                    }
                )
        return aus[:16]
