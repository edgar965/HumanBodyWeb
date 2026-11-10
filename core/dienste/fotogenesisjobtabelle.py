# -*- coding: utf-8 -*-
"""Fotogenesisjobtabelle — Reiter „Jobs“ auf `/foto-genesis/` (24.10.2026): die Tabelle von Mesh-Genesis (`Meshgenesistabelle`), Spalte für Spalte, mit den Exporten (`Fotogenesisjobs.exporte`) als Zeilen.

Edgar: „Ich sagte eine Kopie der Mesh3d-Ai jobs, http://127.0.0.1:8081/2d-3d-AI/ hat schon mal keine Gerechnet Spalten, keine Jobauswahl zum Löschen usw“ — die erste Fassung hatte eigene sechs Spalten.
Jetzt dieselben zwölf, gebaut mit denselben Zellen (`wahl_zelle`, `_paartraining`, `_gerechnet`, `laufzeit_zelle`, `_zahl`). Woher die Werte kommen:
- **Zuletzt trainiert, Gerechnet am, Uhrzeit, Laufzeit**: vom Mesh-Genesis-Job zum selben Export (`paar`) — sein Ergebnis ist heute das Genesis-Modell der Seite (Messlatte A: Tripo-Netz → Mesh-Genesis).
- **Proben**: die Fotos des Jobs. **Training, Prüfposen, Datensatz**: „—“ — Foto-Genesis hat noch keine eigene KI und keinen Datensatz (Weg B).
"""

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .meshgenesisattrappe import Meshgenesisattrappe
from .meshgenesislaufzeit import Meshgenesislaufzeit
from .meshgenesistabelle import Meshgenesistabelle

__all__ = ['Fotogenesisjobtabelle']


class Fotogenesisjobtabelle:
    SCHLUESSEL = 'fotogenesis'
    MESSLATTE = 'Messlatte A (Mesh-Genesis zum selben Export, Tripo-Netz → KI): '
    #: Tooltips je Spalte, wo der Wert hier etwas anderes bedeutet als auf /mesh-genesis/; die übrigen Spalten übernehmen den Tooltip von dort.
    TITEL = {'modell': 'Die Genesis-Figur des Exports (`figur` in der JSON) — aus ihr sind die Fotos gerendert',
             'proben': 'Fotos des Jobs (Exporte: vorne, links, rechts, hinten)',
             'training': 'Foto-Genesis hat noch keine eigene KI (Weg B des Konzepts) — kein Training',
             'pruefung': 'Foto-Genesis hat noch keine eigene KI — keine Prüfposen',
             'datensatz': 'Foto-Genesis hat noch keinen Datensatz',
             'status': 'Woher das Genesis-Modell der Jobseite kommt'}
    LEER = mark_safe('<td class="num" data-sort="0">—</td>')

    @classmethod
    def spalten(cls):
        aus = []
        for s in Meshgenesistabelle.SPALTEN:
            s = dict(s)
            if s['key'] in cls.TITEL:
                s['titel'] = cls.TITEL[s['key']]
            elif s['key'] in ('trainiert', 'gerechnet', 'gerechnet_uhrzeit', 'laufzeit'):
                s['titel'] = cls.MESSLATTE + s.get('titel', '')
            aus.append(s)
        return aus

    @staticmethod
    def adresse(job):
        return '/foto-genesis/%s/' % job['id']

    @classmethod
    def zeile(cls, job):
        paar = Meshgenesisattrappe.job(job['paar']['kennung']) if job['paar'] else None
        name = format_html('<td data-sort="{}"><a href="{}">{}</a>{}</td>', job['name'].lower(), cls.adresse(job), job['name'],
                           format_html(' <a class="hb-hinweis" href="/mesh-genesis/{}/" title="Der Mesh-Genesis-Job zum selben Export">· Mesh-Genesis</a>', paar['id']) if paar else '')
        if paar:
            messlatte = (Meshgenesistabelle._paartraining(paar), Meshgenesistabelle._gerechnet(paar), Meshgenesistabelle.laufzeit_zelle(Meshgenesislaufzeit.job(paar)))
            status = 'Messlatte A (Mesh-Genesis)'
        else:
            messlatte = (mark_safe('<td data-sort="0">—</td>'), Meshgenesistabelle.datum_zellen(None), Meshgenesistabelle.laufzeit_zelle(None))
            status = 'nur Fotos'
        zellen = (
            Meshgenesistabelle.wahl_zelle(job['id']),
            name,
            format_html('<td data-sort="{}">{}</td>', job['figur'].lower(), job['figur'] or '—'),
            *messlatte,
            Meshgenesistabelle._zahl(len(job['fotos'])),
            cls.LEER, cls.LEER, cls.LEER,
            format_html('<td data-sort="{}" title="{}">{}</td>', status.lower(), cls.MESSLATTE.rstrip(': ') if paar else 'Noch kein Genesis-Modell', status),
        )
        return {'id': job['id'], 'klasse': 'meshgenesis-zeile-job', 'html': mark_safe(''.join(zellen))}
