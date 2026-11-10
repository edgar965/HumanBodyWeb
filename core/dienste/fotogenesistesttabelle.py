# -*- coding: utf-8 -*-
"""Fotogenesistesttabelle — Reiter „Test“ auf `/foto-genesis/` (24.10.2026): die Testtabelle von Mesh-Genesis (`Meshgenesistesttabelle`), Spalte für Spalte, mit den echten Fotos (`Fotogenesisjobs.tests`) als Zeilen.

Wie bei Mesh-Genesis: Jobs haben eine Wahrheit (Exporte), Tests nicht (echte Fotos — Randy, Ed 2026, Zauberer). Die Zellen kommen aus `Meshgenesistesttabelle`/`Meshgenesistabelle`; die Werte von
Gerechnet, Laufzeit, Punkte, Lauf und Figur gehören zum Mesh-Genesis-Test zum selben Netz (`meshgenesis_test` in der `job.json`) — Messlatte A. Ohne solchen Test: „—“.
Seit 25.10.2026 gilt vorher der jüngste Lauf der Foto-Kette, wenn der Job einen hat (`Fotogenesislaeufe`, `<Job>/laeufe/`; Edgar: „hier sehe ich keine aktuellen Läufe“): Ende (oder Start,
solange er läuft), Laufzeit der Stufen, Stand, Formrest/Kopf/Größe und als Status die Abnahme; alle Läufe im Tooltip von Lauf und Status.
"""

from pathlib import Path

from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .fotogenesisadresse import Fotogenesisadresse
from .fotogenesislaeufe import Fotogenesislaeufe
from .meshgenesisrechendatum import Meshgenesisrechendatum
from .meshgenesistabelle import Meshgenesistabelle
from .meshgenesistest import Meshgenesistest
from .meshgenesistesttabelle import Meshgenesistesttabelle

__all__ = ['Fotogenesistesttabelle']


class Fotogenesistesttabelle:
    SCHLUESSEL = 'fotogenesis-test'
    MESSLATTE = 'Jüngster Lauf der Foto-Kette (<Job>/laeufe/), ohne ihn Messlatte A (Mesh-Genesis-Test zum selben Netz): '
    TITEL = {'mesh': 'Das Netz aus diesen Fotos (Tripo3D/Hunyuan3D-2mv), falls eines zugeordnet ist; die Zahl der Fotos steht im Tooltip'}

    @classmethod
    def spalten(cls):
        aus = []
        for s in Meshgenesistesttabelle.SPALTEN:
            s = dict(s)
            if s['key'] in cls.TITEL:
                s['titel'] = cls.TITEL[s['key']]
            elif s['key'] not in ('wahl', 'name'):
                s['titel'] = cls.MESSLATTE + s.get('titel', '')
            aus.append(s)
        return aus

    @staticmethod
    def adresse(job):
        return Fotogenesisadresse.seite(job)

    @classmethod
    def zeilen(cls, jobs):
        """Jüngste zuerst (04.11.2026, Edgar: „immer die neuesten jobs am Anfang“) — nach der Zeit der
        Spalte „Gerechnet“ (`zeile` → `zeit`)."""
        meshgenesis = {t['kennung']: t for t in Meshgenesistest.alle(mit_tripo=False)} if any(j['test'] for j in jobs) else {}
        zeilen = [cls.zeile(j, meshgenesis.get(j['test'])) for j in jobs]
        return sorted(zeilen, key=lambda z: z['zeit'] or 0, reverse=True)

    @staticmethod
    def _ohne_lauf(job):
        """(Zeit, Text) für einen Job ohne Lauf und ohne Mesh-Genesis-Test (04.11.2026, Edgar: „es fehlen die
        Zeiten / Datum“): PSHuman fertig (`pshuman/befund.json`), sonst angelegt (Erstellzeit des
        Jobordners)."""
        from .fotogenesispshuman import Fotogenesispshuman
        if not job.get('ordner'):
            return None, ''
        ordner = Path(job['ordner'])
        pshuman = Fotogenesislaeufe.zeit(Fotogenesispshuman.gerechnet(ordner))
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
                           format_html(' <a class="hb-hinweis" href="/mesh-genesis/test/{}/" title="Der Mesh-Genesis-Test zum selben Netz">· Mesh-Genesis</a>', job['test']) if t else '')
        zellen = [Meshgenesistabelle.wahl_zelle(job['id']), name,
                  format_html('<td data-sort="{}" title="{} · {}">{}</td>', Path(netz).name.lower() if netz else '', str(netz or 'kein Netz'), fotos, Path(netz).name if netz else '—')]
        laeufe = Fotogenesislaeufe.alle(job.get('ordner'))
        verlauf = Fotogenesislaeufe.verlauf(laeufe)
        if laeufe:
            status = Fotogenesislaeufe.status(laeufe[0])
            zellen += cls._lauf_zellen(laeufe[0], verlauf)
            zeit = cls._lauf_zeit(laeufe[0])
        elif t:
            status = 'Fehler: %s' % t['fehler'] if t.get('fehler') else ('Messlatte A fertig' if t.get('fertig') else 'Messlatte A nicht fertig')
            letztes = Meshgenesisrechendatum.test(t['kennung'])
            zeit = letztes['zeit'] if letztes else Meshgenesistesttabelle._zeit(t.get('gerechnet'))
            punkte = int(t.get('netz_punkte') or 0)
            zellen += [Meshgenesistesttabelle._gerechnet(t), Meshgenesistabelle.laufzeit_zelle(Meshgenesistesttabelle._laufzeit(t)),
                       format_html('<td class="num" data-sort="{}">{}</td>', punkte, f'{punkte:,}'.replace(',', '.')),
                       format_html('<td data-sort="{}">{}</td>', str(t.get('lauf') or ''), str(t.get('lauf') or '—')),
                       format_html('<td data-sort="{}">{}</td>', str(t.get('figur') or ''), str(t.get('figur') or '—'))]
        else:
            status = 'nur Fotos' + (' und Netz' if netz else '')
            zeit, was = cls._ohne_lauf(job)
            titel = 'Kein Lauf der Foto-Kette — %s' % was if zeit else ''
            zellen += [Meshgenesistabelle.datum_zellen(zeit, titel, was),
                       Meshgenesistabelle.laufzeit_zelle(None), mark_safe('<td class="num" data-sort="0">—</td>'),
                       mark_safe('<td data-sort="">—</td>'), mark_safe('<td data-sort="">—</td>')]
        zellen.append(format_html('<td data-sort="{}" title="{}">{}</td>', status, verlauf, status))
        return {'id': job['id'], 'klasse': 'meshgenesis-zeile-test', 'html': mark_safe(''.join(zellen)),
                'zeit': zeit}

    @staticmethod
    def _lauf_zeit(lauf):
        laeuft = lauf.get('status') == 'läuft'
        return Fotogenesislaeufe.zeit(lauf.get('start') if laeuft else (lauf.get('ende') or lauf.get('start')))

    @classmethod
    def _lauf_zellen(cls, lauf, verlauf):
        """Gerechnet, Uhrzeit, Laufzeit, Punkte, Lauf, Figur aus dem jüngsten Lauf der Foto-Kette."""
        laeuft = lauf.get('status') == 'läuft'
        zeit = cls._lauf_zeit(lauf)
        stand, figur = str(lauf.get('stand') or ''), Fotogenesislaeufe.figur(lauf)
        return [Meshgenesistabelle.datum_zellen(zeit, ('Gestartet' if laeuft else 'Fertig') + ' — Foto-Kette, Stand %s' % stand, 'läuft' if laeuft else 'Foto-Kette'),
                Meshgenesistabelle.laufzeit_zelle(Fotogenesislaeufe.laufzeit(lauf)),
                mark_safe('<td class="num" data-sort="0" title="Punkte zählen die eines Netzes — die Foto-Kette rechnet ohne Netz">—</td>'),
                format_html('<td data-sort="{}" title="{}">{}</td>', stand, verlauf, stand or '—'),
                format_html('<td data-sort="{}">{}</td>', figur, figur)]
