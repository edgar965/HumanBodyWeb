# -*- coding: utf-8 -*-
"""Mesh3daiformlauffiguren — Ergebnis je Figur, Kopfmessung und Verlauf als Tabellen für /mesh-3D-AI/formtraining/<lauf>/ (18.10.2026).

  * je Figur: djangoBase-Tabelle (sortierbar), Zeile je Figur und Gruppe aus `lauf_ergebnis.json` → `je_figur`; verschachtelte Zahlen (Vorstufe: `je_gruppe_mm`) als eigene Spalten; mit
    echter Nachrechnung (`formen_pruefung_echt.json`), wenn sie für die Figur in derselben Gruppe vorliegt. Sortierschlüssel ganze Zahlen (mm × 10, m × 1.000 — `Mesh3daiformzellen`).
  * Kopfmessung: `kopffehler_<lauf>.json` → `mittel_training` / `mittel_pruefung` (RMS je Region, Vorhersage gegen mittlere Form); hat der Vorgänger eine, steht seine Vorhersage daneben.
  * Verlauf: jede Zwischenmessung als Zeile (Textabelle, zum Aufklappen).
"""

import re

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mesh3daiformlaufgruppen import Mesh3daiformlaufgruppen as G
from .mesh3daiformlaufnamen import Mesh3daiformlaufnamen as N
from .mesh3daiformzellen import Mesh3daiformzellen as Z

__all__ = ['Mesh3daiformlauffiguren']


class Mesh3daiformlauffiguren:
    SCHLUESSEL = 'mesh3dai-formlauf-figuren'
    FORMVARIANTE = re.compile(r'^Form\d{3}$')
    REGIONEN = ('koerper', 'kopf', 'kopf_form', 'gesicht', 'gesicht_form', 'nase', 'nase_form', 'mund', 'mund_form', 'augen', 'augen_form', 'ohren', 'ohren_form', 'kopfhaut', 'kopfhaut_form')
    REGIONSNAMEN = {'koerper': 'Körper (ohne Kopf)', 'kopf': 'Kopf, mit seiner Lage', 'gesicht': 'Gesicht, mit Lage', 'nase': 'Nase, mit Lage', 'mund': 'Mund, mit Lage',
                    'augen': 'Augen, mit Lage', 'ohren': 'Ohren, mit Lage', 'kopfhaut': 'Kopfhaut, mit Lage'}
    ECHT = (('vorhersage', 'Echt: Vorhersage (mm)'), ('mittlere_form', 'Echt: mittlere Form (mm)'), ('grundfigur', 'Echt: Grundfigur (mm)'))

    @classmethod
    def figuren(cls, ergebnis, echt, lauf=None, seiten=frozenset()):
        """`seiten`: Figuren mit Formvorhersage in diesem Lauf — ihr Name verlinkt auf `/mesh-3D-AI/formvariante/<Figur>/?lauf=<lauf>` (18.10.2026 abends)."""
        je =ergebnis.get('je_figur') or {}
        if not isinstance(je, dict) or not je:
            return None
        echt = (echt or {}).get('ergebnis') or {}
        reihen = [(name, g, werte) for name, gruppen in je.items() if isinstance(gruppen, dict) for g, werte in gruppen.items() if isinstance(werte, dict)]
        schluessel = []
        for _, _, werte in reihen:
            for k in N.flach(werte):
                if k not in schluessel:
                    schluessel.append(k)
        mit_echt = any((echt.get(name) or {}).get('gruppe') == g for name, g, _ in reihen)
        spalten = [{'label': 'Figur', 'key': 'figur'}, {'label': 'Art', 'key': 'art'}, {'label': 'Gruppe', 'key': 'gruppe'}]
        spalten += [{'label': N.name(k), 'key': k, 'num': True, 'titel': k} for k in schluessel]
        if mit_echt:
            spalten += [{'label': t, 'key': 'echt_' + k, 'num': True, 'titel': 'formen_pruefung_echt.json: Figur aus den Reglern gebaut, RMS über alle Körperpunkte'} for k, t in cls.ECHT]
            spalten += [{'label': 'Höhe Soll (m)', 'key': 'hoehe_soll', 'num': True}, {'label': 'Höhe Vorhersage (m)', 'key': 'hoehe_vor', 'num': True}]
        zeilen = []
        for name, g, werte in reihen:
            flach = N.flach(werte)
            variante = bool(cls.FORMVARIANTE.match(name))
            gruppe = {'training': 'Training', 'pruefung': 'Prüfform (nie trainiert)' if variante else 'Prüfposen'}.get(g, g)
            erste = (format_html('<td data-sort="{}"><a href="/mesh-3D-AI/formvariante/{}/?lauf={}">{}</a></td>', name.lower(), name, lauf, name)
                     if lauf and name in seiten else Z.text(name))
            zellen = [erste, Z.text('Formvariante' if variante else 'Job'), Z.text(gruppe, sort=g)]
            zellen += [cls._zelle(k, flach.get(k)) for k in schluessel]
            if mit_echt:
                e = echt.get(name) or {}
                passt = e.get('gruppe') == g
                zellen += [Z.mmzelle((e.get(k) or {}).get('rms_mm')) if passt else Z.LEER for k, _ in cls.ECHT]
                zellen += [cls._meter(e.get('hoehe_soll_m') if passt else None), cls._meter(e.get('hoehe_vorhersage_m') if passt else None)]
            zeilen.append({'id': '%s|%s' % (name, g), 'klasse': 'mesh3dai-figur-' + ('variante' if variante else 'job'), 'html': mark_safe(''.join(zellen))})
        return {'key': cls.SCHLUESSEL, 'spalten': spalten, 'zeilen': zeilen, 'klasse': 'auftragstabelle mesh3dai-figurtabelle', 'spaltenwahl': True,
                'leer': 'Der Lauf hat kein Ergebnis je Figur.'}

    @classmethod
    def kopf(cls, kopf, vorher=None):
        if not isinstance(kopf, dict):
            return None
        mt, mp = kopf.get('mittel_training') or {}, kopf.get('mittel_pruefung') or {}
        vp = ((vorher or {}).get('mittel_pruefung') or {}).get('vorhersage') or {}
        spalten = []
        if mt:
            spalten += [('Training: Vorhersage', mt.get('vorhersage') or {}, ''), ('Training: mittlere Form', mt.get('mittlere_form') or {}, 'mesh3dai-bezug')]
        if mp:
            spalten += [('Prüfformen: Vorhersage', mp.get('vorhersage') or {}, ''), ('Prüfformen: mittlere Form', mp.get('mittlere_form') or {}, 'mesh3dai-bezug')]
        if vp:
            spalten.append(('Prüfformen: Vorhersage des vorigen Laufs', vp, 'mesh3dai-bezug'))
        if not spalten:
            return None
        regionen = [r for r in cls.REGIONEN if any(r in werte for _, werte, _ in spalten)]
        zeilen = [[{'text': cls._region(r), 'titel': r}] + [{'text': G.zahl((werte.get(r) or {}).get('rms_mm')), 'klasse': ('num ' + k).strip()} for _, werte, k in spalten]
                  for r in regionen]
        return {'kopf': ['Region (RMS, mm)'] + [t for t, _, _ in spalten], 'zeilen': zeilen,
                'varianten': {'training': mt.get('varianten'), 'pruefung': mp.get('varianten')}}

    @staticmethod
    def verlauf(verlauf):
        schluessel = []
        for v in verlauf:
            for k in v:
                if k not in schluessel:
                    schluessel.append(k)
        if not verlauf or not schluessel:
            return None
        kopf = [N.name(k) if k not in ('epoche', 's') else {'epoche': 'Epoche', 's': 'Sekunden'}[k] for k in schluessel]
        zeilen = [[{'text': G.zahl(v.get(k)), 'klasse': 'num'} for k in schluessel] for v in verlauf]
        return {'kopf': kopf, 'zeilen': zeilen}

    @classmethod
    def _region(cls, r):
        if r.endswith('_form'):
            basis = r[:-5]
            return '%s-Form (Lage abgezogen)' % cls.REGIONSNAMEN.get(basis, basis).split(',')[0]
        return cls.REGIONSNAMEN.get(r, r)

    @staticmethod
    def _zelle(k, v):
        if v is None:
            return Z.LEER
        return Z.zahlzelle(v) if isinstance(v, int) and not k.endswith(('_mm', '_jahre')) else Z.mmzelle(v)

    @staticmethod
    def _meter(v):
        if v is None:
            return Z.LEER
        return format_html('<td class="num" data-sort="{}">{}</td>', int(round(float(v) * 1000)), ('%.3f' % float(v)).replace('.', ','))
