# -*- coding: utf-8 -*-
"""Architekturmeshgenesistestnetze — die Testnetze (Reiter „Test“ von `/mesh-genesis/`) auf Hilfe → Architektur → Mesh-Genesis (16.10.2026 abends).

Fremde Netze ohne Soll (Königin, Zauberer, Spiralballerina …): das Netz sagt Gelenke und Formregler voraus, je Geschlecht wird aus den Reglern eine eigene Figur gebaut
(`ProjektTemp/_wegwerf/meshgenesis_test_form.py`, `meshgenesis_formfigur.py`) und die Haltung an ihr Skelett angepasst. GELESEN beim Aufruf: `Meshgenesistest.alle()` (je Test `test.json`)
und je Geschlecht `_test/<kennung>/form_<g>/modell.json` (gesetzte Regler, umgelegte Charaktere des anderen Geschlechts).
"""

import json

__all__ = ['Architekturmeshgenesistestnetze']


class Architekturmeshgenesistestnetze:
    GESCHLECHTER = ('weiblich', 'maennlich')

    @classmethod
    def _figur(cls, p, g, form):
        f = (form or {}).get(g)
        if not isinstance(f, dict):
            return None
        modell = {}
        try:
            modell = json.loads((p / ('form_%s' % g) / 'modell.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            pass
        # `anderes_geschlecht_umgelegt` = Summe der Charakter-Werte des anderen Geschlechts, die `meshgenesis_formfigur.regler_fuer` umgelegt hat (eine Zahl, keine Liste).
        umgelegt = modell.get('anderes_geschlecht_umgelegt') if modell else None
        return {'rest_mm': f.get('rest_mm'), 'hoehe_m': f.get('hoehe_m'), 'regler': len(((modell.get('figur') or {}).get('regler')) or {}) if modell else None,
                'umgelegt': float(umgelegt) if isinstance(umgelegt, (int, float)) else None}

    @classmethod
    def kontext(cls):
        from .meshgenesistest import Meshgenesistest
        zeilen = []
        for info in Meshgenesistest.alle():
            kennung = info.get('kennung') or info.get('name')
            p = Meshgenesistest.pfad(kennung) if kennung else None
            form = info.get('form') or {}
            g = info.get('geschlecht')
            zeilen.append({'kennung': kennung, 'name': info.get('name', kennung), 'geschlecht': 'männlich' if g == 'maennlich' else g, 'figur': info.get('figur'), 'fehler': info.get('fehler'),
                           'lauf': form.get('lauf'), 'regler_gesetzt': form.get('regler_gesetzt'),
                           'figuren': [cls._figur(p, g, form) if p else None for g in cls.GESCHLECHTER]})
        return {'zeilen': zeilen, 'mit_form': sum(1 for z in zeilen if any(z['figuren']))}
