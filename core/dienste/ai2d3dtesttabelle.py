# -*- coding: utf-8 -*-
"""Ai2d3dtesttabelle — Reiter „Test“ auf `/2d-3d-AI/` (24.10.2026): die Testtabelle von Mesh3D-AI (`Mesh3daitesttabelle`), Spalte für Spalte, mit den echten Fotos (`Ai2d3djobs.tests`) als Zeilen.

Wie bei Mesh3D-AI: Jobs haben eine Wahrheit (Exporte), Tests nicht (echte Fotos — Randy, Ed 2026, Zauberer). Die Zellen kommen aus `Mesh3daitesttabelle`/`Mesh3daitabelle`; die Werte von
Gerechnet, Laufzeit, Punkte, Lauf und Figur gehören zum Mesh3D-AI-Test zum selben Netz (`mesh3dai_test` in der `job.json`) — Messlatte A. Ohne solchen Test: „—“.
"""

from pathlib import Path

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .mesh3daitabelle import Mesh3daitabelle
from .mesh3daitest import Mesh3daitest
from .mesh3daitesttabelle import Mesh3daitesttabelle

__all__ = ['Ai2d3dtesttabelle']


class Ai2d3dtesttabelle:
    SCHLUESSEL = 'ai2d3d-test'
    MESSLATTE = 'Messlatte A (Mesh3D-AI-Test zum selben Netz): '
    TITEL = {'mesh': 'Das Netz aus diesen Fotos (Tripo3D/Hunyuan3D-2mv), falls eines zugeordnet ist; die Zahl der Fotos steht im Tooltip'}

    @classmethod
    def spalten(cls):
        aus = []
        for s in Mesh3daitesttabelle.SPALTEN:
            s = dict(s)
            if s['key'] in cls.TITEL:
                s['titel'] = cls.TITEL[s['key']]
            elif s['key'] not in ('wahl', 'name'):
                s['titel'] = cls.MESSLATTE + s.get('titel', '')
            aus.append(s)
        return aus

    @staticmethod
    def adresse(job):
        return '/2d-3d-AI/test/%s/' % job['id']

    @classmethod
    def zeilen(cls, jobs):
        mesh3dai = {t['kennung']: t for t in Mesh3daitest.alle(mit_tripo=False)} if any(j['test'] for j in jobs) else {}
        return [cls.zeile(j, mesh3dai.get(j['test'])) for j in jobs]

    @classmethod
    def zeile(cls, job, t):
        netz = job['netze'][0]['pfad'] if job['netze'] else None
        fotos = '%d Fotos' % len(job['fotos'])
        name = format_html('<td data-sort="{}"><a href="{}">{}</a>{}</td>', job['name'].lower(), cls.adresse(job), job['name'],
                           format_html(' <a class="hb-hinweis" href="/mesh-3D-AI/test/{}/" title="Der Mesh3D-AI-Test zum selben Netz">· Mesh3D-AI</a>', job['test']) if t else '')
        zellen = [Mesh3daitabelle.wahl_zelle(job['id']), name,
                  format_html('<td data-sort="{}" title="{} · {}">{}</td>', Path(netz).name.lower() if netz else '', str(netz or 'kein Netz'), fotos, Path(netz).name if netz else '—')]
        if t:
            status = 'Fehler: %s' % t['fehler'] if t.get('fehler') else ('Messlatte A fertig' if t.get('fertig') else 'Messlatte A nicht fertig')
            punkte = int(t.get('netz_punkte') or 0)
            zellen += [Mesh3daitesttabelle._gerechnet(t), Mesh3daitabelle.laufzeit_zelle(Mesh3daitesttabelle._laufzeit(t)),
                       format_html('<td class="num" data-sort="{}">{}</td>', punkte, f'{punkte:,}'.replace(',', '.')),
                       format_html('<td data-sort="{}">{}</td>', str(t.get('lauf') or ''), str(t.get('lauf') or '—')),
                       format_html('<td data-sort="{}">{}</td>', str(t.get('figur') or ''), str(t.get('figur') or '—'))]
        else:
            status = 'nur Fotos' + (' und Netz' if netz else '')
            zellen += [Mesh3daitabelle.datum_zellen(None), Mesh3daitabelle.laufzeit_zelle(None), mark_safe('<td class="num" data-sort="0">—</td>'),
                       mark_safe('<td data-sort="">—</td>'), mark_safe('<td data-sort="">—</td>')]
        zellen.append(format_html('<td data-sort="{}">{}</td>', status, status))
        return {'id': job['id'], 'klasse': 'mesh3dai-zeile-test', 'html': mark_safe(''.join(zellen))}
