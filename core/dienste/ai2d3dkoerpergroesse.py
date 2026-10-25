# -*- coding: utf-8 -*-
"""Ai2d3dkoerpergroesse — die Körpergröße der Person eines Fototests (24.10.2026, Edgar: „körpergröße kann ich angeben im Job oben, erstmal, mach ein UI dazu, 1,85 m“).

Echte Fotos tragen keinen Maßstab. Die Fotoeinpassung (`KoerperKI_Fotos.Fotoeinpassung`, orthografisch, ein Maßstab je Foto aus dem Kopf) kann die Größe der Figur deshalb frei wählen — im
dritten Lauf am 24.10.2026 (15:14) schrumpfte sie von 1,710 auf 1,435 m, und die Umriss-Deckung stieg dabei. Die Angabe der Person ist ein Wert von außen, kein Wert aus dem Netz.

Sie steht in `3DObjects/ai2d3d/<Name>/job.json` als `koerpergroesse_m` (Meter, Scheitel bis Sohle; fehlt oder `null` = unbekannt). Exporte (mit Wahrheit) haben keine: Ihre Figur ist bekannt.

    POST /api/2d3dai/<job>/koerpergroesse/   {koerpergroesse_m: 1.85 | null}   → {ok, koerpergroesse_m}
"""

import json
import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dkoerpergroesse']


class Ai2d3dkoerpergroesse:
    FELD = 'koerpergroesse_m'
    #: Spanne, die eine Angabe haben darf (m) — außerhalb ist es ein Tippfehler (185 statt 1,85), keine Person.
    KLEINSTE, GROESSTE = 1.0, 2.3

    @classmethod
    def lesen(cls, info):
        """Die Angabe aus einer gelesenen job.json, `None` ohne Angabe; eine unbrauchbare wird gemeldet und gilt als unbekannt."""
        wert = info.get(cls.FELD)
        if wert is None:
            return None
        try:
            return cls.pruefen(wert)
        except ValueError as fehler:
            logger.warning('Ai2d3dkoerpergroesse: %s — gilt als unbekannt', fehler)
            return None

    @classmethod
    def pruefen(cls, wert):
        """`None`/leer → `None`; sonst Meter als Zahl in der Spanne, auf Zentimeter gerundet. Ein Komma als Dezimalzeichen ist erlaubt („1,85“)."""
        if wert is None or (isinstance(wert, str) and not wert.strip()):
            return None
        if isinstance(wert, bool):
            raise ValueError('Körpergröße %r ist keine Zahl' % (wert,))
        try:
            meter = float(wert.strip().replace(',', '.')) if isinstance(wert, str) else float(wert)
        except (TypeError, ValueError):
            raise ValueError('Körpergröße %r ist keine Zahl' % (wert,)) from None
        if not cls.KLEINSTE <= meter <= cls.GROESSTE:
            raise ValueError('Körpergröße %s m liegt außerhalb %.2f–%.2f m' % (wert, cls.KLEINSTE, cls.GROESSTE))
        return round(meter, 2)

    @classmethod
    def setzen(cls, job, wert):
        """Schreibt die Angabe in die job.json des Tests (mischend: alle anderen Felder bleiben). Gibt den gespeicherten Wert zurück; `ValueError` bei Export oder falschem Wert."""
        if job.get('art') != 'foto':
            raise ValueError('Nur Tests aus echten Fotos haben eine Körpergröße — die Figur eines Exports ist bekannt')
        meter = cls.pruefen(wert)
        datei = job['ordner'] / 'job.json'
        info = json.loads(datei.read_text(encoding='utf-8'))
        if meter is None:
            info.pop(cls.FELD, None)
        else:
            info[cls.FELD] = meter
        neu = datei.with_name('job.json.neu')
        neu.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding='utf-8')
        neu.replace(datei)
        logger.info('Ai2d3dkoerpergroesse: %s → %s', datei, meter)
        return meter
