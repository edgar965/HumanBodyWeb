# -*- coding: utf-8 -*-
"""Fotogenesisnormalen — die Normalen-Engine eines Foto-Genesis-Jobs (03.11.2026).

Edgar: „bei den jobs möchte ich eine Combo box haben, wo ich die engine auswählen kann. Default: Econ“,
„mach 2 Optionen: aus einem Foto (per UI wählbar) oder aus mehreren“,
„zu Econs registrierung - auch hier beides, per default deine Empfehlung aber mach als vergleich auch die
exakte portierung“.
Konzept `Docu/konzepte/2026-11-02_normalen-zwei-quellen-konzept.md`.

In `3DObjects/fotogenesis/<Name>/job.json` als `normalen`: {engine, foto, zusammen}; fehlt es, gelten die Vorgaben.
Gelesen von der Kette beim nächsten Lauf (`KoerperKI_Fotos.normalenwahl.Normalenwahl`, Stufe „koerper“ in
`Fotoauswendig`) — ein gerechneter Lauf bleibt, wie er ist.

    POST /api/fotogenesis/<job>/normalen/   {engine, foto, zusammen}   → {ok, normalen}
"""

import json
import logging

logger = logging.getLogger('core')

__all__ = ['Fotogenesisnormalen']


class Fotogenesisnormalen:
    FELD = 'normalen'
    VORGABE = {'engine': 'econ', 'foto': None, 'zusammen': 'chamfer'}  # noqa: RUF012 — nur gelesen
    ENGINES = (('econ', 'ECON (d-BiNI)'), ('pshuman', 'PSHuman'), ('bini', 'BiNI (perspektivisch)'),
               ('eigen', 'eigen (Fotonormalen)'), ('aus', 'aus'))
    ZUSAMMEN = (('chamfer', 'Chamfer-Term in der Einpassung'), ('tiefe', 'Tiefenterm je Pixel'),
                ('register', 'ECONs register (exakt)'))
    BESCHREIBUNG = {  # noqa: RUF012 — nur gelesen
        'econ': 'ECONs d-BiNI (Port, Tiefen bitgleich zum Original): Relief aus den Normalen, verankert an '
                'der Tiefe der Figur. Mehrere Fotos: je Gegenpaar (vorn/hinten, die beiden Profile), '
                'Rückseite aus dem Gegenfoto '
                '(Weg von MExECON); ein Foto: Rückseite aus ECONs Normalennetz.',
        'pshuman': 'PSHumans Verlust: Normalen aller Fotos gegen die Figur, gewichtet nach Blickwinkel '
                   '(vorn/hinten 1, Seite 0,8). Aus einem Foto nur dessen Ansicht.',
        'bini': 'BiNI (Cao 2022, Vorlage von ECONs d-BiNI): Relief je Foto mit der echten Perspektive der '
                'Kamera, verankert an der Tiefe der Figur; nur die sichtbare Seite je Foto.',
        'eigen': 'Der eigene Normalenverlust je Foto auf Figur ∩ Person (Fotonormalen), Gewicht 100 '
                 '(02.11.2026 gemessen: 11.815 statt 12.034 abweichende Pixel).',
        'aus': 'Keine Normalen — nur die Umrisse.',
    }

    @classmethod
    def lesen(cls, info):
        """Die Wahl aus einer job.json samt Vorgaben; Unbrauchbares gilt als Vorgabe (mit Warnung)."""
        roh = info.get(cls.FELD) or {}
        w = dict(cls.VORGABE)
        for k in w:
            if k in roh:
                w[k] = roh[k]
        if w['engine'] not in dict(cls.ENGINES) or w['zusammen'] not in dict(cls.ZUSAMMEN):
            logger.warning('Fotogenesisnormalen: %r unbrauchbar — Vorgabe', roh)
            return dict(cls.VORGABE)
        return w

    @classmethod
    def setzen(cls, job, rumpf):
        """Schreibt die Wahl in die job.json (mischend, alle anderen Felder bleiben).

        `ValueError` bei unbekannter Engine, Zusammenführung oder einem Foto, das der Job nicht hat.
        """
        if job.get('art') != 'foto':
            raise ValueError('Nur Tests aus echten Fotos haben eine Normalen-Wahl')
        engine, foto = rumpf.get('engine', 'econ'), rumpf.get('foto') or None
        zusammen = rumpf.get('zusammen', 'chamfer')
        if engine not in dict(cls.ENGINES):
            raise ValueError('Unbekannte Engine %r' % (engine,))
        if zusammen not in dict(cls.ZUSAMMEN):
            raise ValueError('Unbekannte Zusammenführung %r' % (zusammen,))
        namen = [f['original'].name for f in job.get('fotos') or []]
        if foto is not None and foto not in namen:
            raise ValueError('Foto %r gehört nicht zum Job (%s)' % (foto, ', '.join(namen)))
        datei = job['ordner'] / 'job.json'
        info = json.loads(datei.read_text(encoding='utf-8'))
        info[cls.FELD] = {'engine': engine, 'foto': foto, 'zusammen': zusammen}
        neu = datei.with_name('job.json.neu')
        neu.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        neu.replace(datei)
        logger.info('Fotogenesisnormalen: %s → %s', datei, info[cls.FELD])
        return info[cls.FELD]
