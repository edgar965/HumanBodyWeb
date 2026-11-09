# -*- coding: utf-8 -*-
"""Ai2d3dtesttabelle — Reiter „Test“ auf `/2d-3d-AI/` (24.10.2026): die Testtabelle von Mesh3D-AI (`Mesh3daitesttabelle`), Spalte für Spalte, mit den echten Fotos (`Ai2d3djobs.tests`) als Zeilen.

Wie bei Mesh3D-AI: Jobs haben eine Wahrheit (Exporte), Tests nicht (echte Fotos — Randy, Ed 2026, Zauberer). Die Zellen kommen aus `Mesh3daitesttabelle`/`Mesh3daitabelle`; die Werte von
Gerechnet, Laufzeit, Punkte, Lauf und Figur gehören zum Mesh3D-AI-Test zum selben Netz (`mesh3dai_test` in der `job.json`) — Messlatte A. Ohne solchen Test: „—“.
Seit 25.10.2026 gilt vorher der jüngste Lauf der Foto-Kette, wenn der Job einen hat (`Ai2d3dlaeufe`, `<Job>/laeufe/`; Edgar: „hier sehe ich keine aktuellen Läufe“): Ende (oder Start,
solange er läuft), Laufzeit der Stufen, Stand, Formrest/Kopf/Größe und als Status die Abnahme; alle Läufe im Tooltip von Lauf und Status.
"""

from pathlib import Path

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .ai2d3dadresse import Ai2d3dadresse
from .ai2d3dlaeufe import Ai2d3dlaeufe
from .mesh3dairechendatum import Mesh3dairechendatum
from .mesh3daitabelle import Mesh3daitabelle
from .mesh3daitest import Mesh3daitest
from .mesh3daitesttabelle import Mesh3daitesttabelle

__all__ = ['Ai2d3dtesttabelle']


class Ai2d3dtesttabelle:
    SCHLUESSEL = 'ai2d3d-test'
    MESSLATTE = 'Jüngster Lauf der Foto-Kette (<Job>/laeufe/), ohne ihn Messlatte A (Mesh3D-AI-Test zum selben Netz): '
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
        return Ai2d3dadresse.seite(job)

    @classmethod
    def zeilen(cls, jobs):
        """Jüngste zuerst (04.11.2026, Edgar: „immer die neuesten jobs am Anfang“) — nach der Zeit der
        Spalte „Gerechnet“ (`zeile` → `zeit`)."""
        mesh3dai = {t['kennung']: t for t in Mesh3daitest.alle(mit_tripo=False)} if any(j['test'] for j in jobs) else {}
        zeilen = [cls.zeile(j, mesh3dai.get(j['test'])) for j in jobs]
        return sorted(zeilen, key=lambda z: z['zeit'] or 0, reverse=True)

    @staticmethod
    def _ohne_lauf(job):
        """(Zeit, Text) für einen Job ohne Lauf und ohne Mesh3D-AI-Test (04.11.2026, Edgar: „es fehlen die
        Zeiten / Datum“): PSHuman fertig (`pshuman/befund.json`), sonst angelegt (Erstellzeit des
        Jobordners)."""
        from .ai2d3dpshuman import Ai2d3dpshuman
        if not job.get('ordner'):
            return None, ''
        ordner = Path(job['ordner'])
        pshuman = Ai2d3dlaeufe.zeit(Ai2d3dpshuman.gerechnet(ordner))
        if pshuman:
            return pshuman, 'PSHuman'
        try:
            st = ordner.stat()
        except OSError:
            return None, ''
        return getattr(st, 'st_birthtime', st.st_ctime), 'angelegt'

    @classmethod
    def zeile(cls, job, t):
        netz = job['netze'][0]['pfad'] if job['netze'] else None
        fotos = '%d Fotos' % len(job['fotos'])
        name = format_html('<td data-sort="{}"><a href="{}">{}</a>{}</td>', job['name'].lower(), cls.adresse(job), job['name'],
                           format_html(' <a class="hb-hinweis" href="/mesh-3D-AI/test/{}/" title="Der Mesh3D-AI-Test zum selben Netz">· Mesh3D-AI</a>', job['test']) if t else '')
        zellen = [Mesh3daitabelle.wahl_zelle(job['id']), name,
                  format_html('<td data-sort="{}" title="{} · {}">{}</td>', Path(netz).name.lower() if netz else '', str(netz or 'kein Netz'), fotos, Path(netz).name if netz else '—')]
        laeufe = Ai2d3dlaeufe.alle(job.get('ordner'))
        verlauf = Ai2d3dlaeufe.verlauf(laeufe)
        if laeufe:
            status = Ai2d3dlaeufe.status(laeufe[0])
            zellen += cls._lauf_zellen(laeufe[0], verlauf)
            zeit = cls._lauf_zeit(laeufe[0])
        elif t:
            status = 'Fehler: %s' % t['fehler'] if t.get('fehler') else ('Messlatte A fertig' if t.get('fertig') else 'Messlatte A nicht fertig')
            letztes = Mesh3dairechendatum.test(t['kennung'])
            zeit = letztes['zeit'] if letztes else Mesh3daitesttabelle._zeit(t.get('gerechnet'))
            punkte = int(t.get('netz_punkte') or 0)
            zellen += [Mesh3daitesttabelle._gerechnet(t), Mesh3daitabelle.laufzeit_zelle(Mesh3daitesttabelle._laufzeit(t)),
                       format_html('<td class="num" data-sort="{}">{}</td>', punkte, f'{punkte:,}'.replace(',', '.')),
                       format_html('<td data-sort="{}">{}</td>', str(t.get('lauf') or ''), str(t.get('lauf') or '—')),
                       format_html('<td data-sort="{}">{}</td>', str(t.get('figur') or ''), str(t.get('figur') or '—'))]
        else:
            status = 'nur Fotos' + (' und Netz' if netz else '')
            zeit, was = cls._ohne_lauf(job)
            titel = 'Kein Lauf der Foto-Kette — %s' % was if zeit else ''
            zellen += [Mesh3daitabelle.datum_zellen(zeit, titel, was),
                       Mesh3daitabelle.laufzeit_zelle(None), mark_safe('<td class="num" data-sort="0">—</td>'),
                       mark_safe('<td data-sort="">—</td>'), mark_safe('<td data-sort="">—</td>')]
        zellen.append(format_html('<td data-sort="{}" title="{}">{}</td>', status, verlauf, status))
        return {'id': job['id'], 'klasse': 'mesh3dai-zeile-test', 'html': mark_safe(''.join(zellen)),
                'zeit': zeit}

    @staticmethod
    def _lauf_zeit(lauf):
        laeuft = lauf.get('status') == 'läuft'
        return Ai2d3dlaeufe.zeit(lauf.get('start') if laeuft else (lauf.get('ende') or lauf.get('start')))

    @classmethod
    def _lauf_zellen(cls, lauf, verlauf):
        """Gerechnet, Uhrzeit, Laufzeit, Punkte, Lauf, Figur aus dem jüngsten Lauf der Foto-Kette."""
        laeuft = lauf.get('status') == 'läuft'
        zeit = cls._lauf_zeit(lauf)
        stand, figur = str(lauf.get('stand') or ''), Ai2d3dlaeufe.figur(lauf)
        return [Mesh3daitabelle.datum_zellen(zeit, ('Gestartet' if laeuft else 'Fertig') + ' — Foto-Kette, Stand %s' % stand, 'läuft' if laeuft else 'Foto-Kette'),
                Mesh3daitabelle.laufzeit_zelle(Ai2d3dlaeufe.laufzeit(lauf)),
                mark_safe('<td class="num" data-sort="0" title="Punkte zählen die eines Netzes — die Foto-Kette rechnet ohne Netz">—</td>'),
                format_html('<td data-sort="{}" title="{}">{}</td>', stand, verlauf, stand or '—'),
                format_html('<td data-sort="{}">{}</td>', figur, figur)]
