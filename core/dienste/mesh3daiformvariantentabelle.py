# -*- coding: utf-8 -*-
"""Mesh3daiformvariantentabelle — die Formvarianten (synthetische Figuren des Formtrainings) im Reiter „Formtraining“ auf /mesh-3D-AI/ als djangoBase-Tabelle (18.10.2026).

Eine Zeile je `3DObjects/mesh3dai/FormNNN/` (`Mesh3daiformvarianten`): Figur, Datenstand (MIA und Wolken Fassung 9 je Probe), der jüngste fertige Formlauf mit ihrem Formfehler.
Gleiche Bauart wie `Mesh3daitabelle`; eine Zeile öffnet die Seite der Variante (`/mesh-3D-AI/formvariante/<Name>/`, seit 18.10.2026 abends — Klasse `mesh3daitabelle`, Link in der ersten Zelle).
"""

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mesh3daiformzellen import Mesh3daiformzellen as Z

__all__ = ['Mesh3daiformvariantentabelle']


class Mesh3daiformvariantentabelle:
    SCHLUESSEL = 'mesh3dai-formvarianten'
    ZUSTAND = {'fertig': 'Daten Fassung 9 fertig', 'wird gerechnet': 'wird gerechnet', 'mia': 'MIA fertig, Wolken fehlen', 'unvollständig': 'unvollständig', 'offen': 'offen'}
    SPALTEN = (
        {'label': 'Formvariante', 'key': 'name', 'titel': 'Ordner unter 3DObjects/mesh3dai'},
        {'label': 'Grundlage', 'key': 'grundlage', 'titel': 'Der Job, dessen Figur und Kleidung die Variante abwandelt (modell.json → grundlage)'},
        {'label': 'Letzter Lauf', 'key': 'lauf',
         'titel': 'Ende des jüngsten fertigen Formlaufs, der diese Variante trainiert oder gemessen hat (formen_ergebnis.json → varianten; Probeläufe zählen nicht). Lauf und Rolle im Tooltip'},
        {'label': 'Figur', 'key': 'figur', 'titel': 'Geschlecht aus modell.json; „Kind“, wenn die Figur Regler der Genesis-1-Kinder (g1:…) trägt'},
        {'label': 'Gruppe', 'key': 'gruppe', 'titel': 'Training oder Prüfform (nie trainiert, nur gemessen) — modell.json → gruppe'},
        {'label': 'Posen', 'key': 'posen', 'num': True, 'titel': 'Geplante Proben (Einträge in proben.json)'},
        {'label': 'MIA', 'key': 'mia', 'num': True, 'titel': 'Proben mit einer Datei mia_v*_*.npz (Make-It-Animatable, Phase B des Datenlaufs) von den geplanten'},
        {'label': 'Wolken v9', 'key': 'wolken', 'num': True, 'titel': 'Proben mit einer Datei apose_v9_*.npz (A-Pose-Wolke Fassung 9, Phase C — die liest das Formtraining) von den geplanten'},
        {'label': 'Daten zuletzt', 'key': 'daten', 'titel': 'Jüngste Datei mia_v* oder apose_v9_* der Variante'},
        {'label': 'Formfehler (mm)', 'key': 'form', 'num': True, 'titel': 'form_mm der Variante im letzten Lauf (formen_ergebnis.json → varianten → form → <Gruppe>)'},
        {'label': 'Kopf-Form (mm)', 'key': 'kopf', 'num': True, 'titel': 'kopf_form_mm der Variante im letzten Lauf (erst seit Formtraining 2)'},
        {'label': 'Status', 'key': 'status',
         'titel': 'Nur von der Platte: fertig = jede geplante Probe hat eine Wolke v9; wird gerechnet = jüngste Datei unter 30 min alt; MIA fertig = Wolken fehlen noch (Phase C kommt nach allen Blöcken)'},
    )

    def tabelle(self, varianten):
        return {'key': self.SCHLUESSEL, 'spalten': list(self.SPALTEN), 'zeilen': [self.zeile(v) for v in varianten],
                'klasse': 'auftragstabelle mesh3daitabelle mesh3daiformtabelle', 'leer': 'Keine Formvariante unter 3DObjects/mesh3dai (Ordner FormNNN mit modell.json).'}

    def zeile(self, v):
        lauf = v['lauf'] or {}
        rolle = 'trainiert' if lauf.get('gruppe') == 'training' else 'nur gemessen (Prüfform)'
        figur = {'maennlich': 'männlich'}.get(v['geschlecht'], v['geschlecht'] or '—') + (' · Kind' if v['kind'] else '')
        gruppe = {'training': 'Training', 'pruefung': 'Prüfform'}.get(v['gruppe'], v['gruppe'] or '—')
        zellen = (
            format_html('<td data-sort="{}"><a href="/mesh-3D-AI/formvariante/{}/">{}</a></td>', v['name'].lower(), v['name'], v['name']),
            Z.text(v['grundlage'] or '—'),
            Z.zeit(lauf.get('zeit'), titel='%s — %s' % (lauf['lauf'], rolle)) if lauf else Z.LEER,
            Z.text(figur),
            Z.text(gruppe),
            Z.zahlzelle(v['geplant']),
            Z.anteil(v['mia'], v['geplant']),
            Z.anteil(v['wolken'], v['geplant']),
            Z.zeit(v['daten_zeit']),
            Z.mmzelle(lauf.get('form_mm')),
            Z.mmzelle(lauf.get('kopf_mm')),
            Z.text(self.ZUSTAND.get(v['zustand'], v['zustand'])),
        )
        klasse = 'mesh3dai-zeile-formvariante' + (' mesh3dai-laeuft' if v['zustand'] == 'wird gerechnet' else '')
        return {'id': v['name'], 'klasse': klasse, 'html': mark_safe(''.join(zellen))}
