# -*- coding: utf-8 -*-
"""Ai2d3djobtabelle — Reiter „Jobs“ auf `/2d-3d-AI/` (24.10.2026): die Tabelle von Mesh3D-AI (`Mesh3daitabelle`), Spalte für Spalte, mit den Exporten (`Ai2d3djobs.exporte`) als Zeilen.

Edgar: „Ich sagte eine Kopie der Mesh3d-Ai jobs, http://127.0.0.1:8081/2d-3d-AI/ hat schon mal keine Gerechnet Spalten, keine Jobauswahl zum Löschen usw“ — die erste Fassung hatte eigene sechs Spalten.
Jetzt dieselben zwölf, gebaut mit denselben Zellen (`wahl_zelle`, `_paartraining`, `_gerechnet`, `laufzeit_zelle`, `_zahl`). Woher die Werte kommen:
- **Zuletzt trainiert, Gerechnet am, Uhrzeit, Laufzeit**: vom Mesh3D-AI-Job zum selben Export (`paar`) — sein Ergebnis ist heute das Genesis-Modell der Seite (Messlatte A: Tripo-Netz → Mesh3D-AI).
- **Proben**: die Fotos des Jobs. **Training, Prüfposen, Datensatz**: „—“ — 2d-3d-AI hat noch keine eigene KI und keinen Datensatz (Weg B).
"""

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mesh3daiattrappe import Mesh3daiattrappe
from .mesh3dailaufzeit import Mesh3dailaufzeit
from .mesh3daitabelle import Mesh3daitabelle

__all__ = ['Ai2d3djobtabelle']


class Ai2d3djobtabelle:
    SCHLUESSEL = 'ai2d3d'
    MESSLATTE = 'Messlatte A (Mesh3D-AI zum selben Export, Tripo-Netz → KI): '
    #: Tooltips je Spalte, wo der Wert hier etwas anderes bedeutet als auf /mesh-3D-AI/; die übrigen Spalten übernehmen den Tooltip von dort.
    TITEL = {'modell': 'Die Genesis-Figur des Exports (`figur` in der JSON) — aus ihr sind die Fotos gerendert',
             'proben': 'Fotos des Jobs (Exporte: vorne, links, rechts, hinten)',
             'training': '2d-3d-AI hat noch keine eigene KI (Weg B des Konzepts) — kein Training',
             'pruefung': '2d-3d-AI hat noch keine eigene KI — keine Prüfposen',
             'datensatz': '2d-3d-AI hat noch keinen Datensatz',
             'status': 'Woher das Genesis-Modell der Jobseite kommt'}
    LEER = mark_safe('<td class="num" data-sort="0">—</td>')

    @classmethod
    def spalten(cls):
        aus = []
        for s in Mesh3daitabelle.SPALTEN:
            s = dict(s)
            if s['key'] in cls.TITEL:
                s['titel'] = cls.TITEL[s['key']]
            elif s['key'] in ('trainiert', 'gerechnet', 'gerechnet_uhrzeit', 'laufzeit'):
                s['titel'] = cls.MESSLATTE + s.get('titel', '')
            aus.append(s)
        return aus

    @staticmethod
    def adresse(job):
        return '/2d-3d-AI/%s/' % job['id']

    @classmethod
    def zeile(cls, job):
        paar = Mesh3daiattrappe.job(job['paar']['kennung']) if job['paar'] else None
        name = format_html('<td data-sort="{}"><a href="{}">{}</a>{}</td>', job['name'].lower(), cls.adresse(job), job['name'],
                           format_html(' <a class="hb-hinweis" href="/mesh-3D-AI/{}/" title="Der Mesh3D-AI-Job zum selben Export">· Mesh3D-AI</a>', paar['id']) if paar else '')
        if paar:
            messlatte = (Mesh3daitabelle._paartraining(paar), Mesh3daitabelle._gerechnet(paar), Mesh3daitabelle.laufzeit_zelle(Mesh3dailaufzeit.job(paar)))
            status = 'Messlatte A (Mesh3D-AI)'
        else:
            messlatte = (mark_safe('<td data-sort="0">—</td>'), Mesh3daitabelle.datum_zellen(None), Mesh3daitabelle.laufzeit_zelle(None))
            status = 'nur Fotos'
        zellen = (
            Mesh3daitabelle.wahl_zelle(job['id']),
            name,
            format_html('<td data-sort="{}">{}</td>', job['figur'].lower(), job['figur'] or '—'),
            *messlatte,
            Mesh3daitabelle._zahl(len(job['fotos'])),
            cls.LEER, cls.LEER, cls.LEER,
            format_html('<td data-sort="{}" title="{}">{}</td>', status.lower(), cls.MESSLATTE.rstrip(': ') if paar else 'Noch kein Genesis-Modell', status),
        )
        return {'id': job['id'], 'klasse': 'mesh3dai-zeile-job', 'html': mark_safe(''.join(zellen))}
