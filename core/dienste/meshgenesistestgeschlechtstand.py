# -*- coding: utf-8 -*-
"""Meshgenesistestgeschlechtstand — stammen die Kleider des eingestellten Geschlechts aus dem letzten Lauf? (06.11.2026)

Die Kette rechnet Einpassung, Figur, Haut und Kleider nur für das eingestellte Geschlecht (`Kostuemlauf`). Die Wahl oben auf der Testseite rechnet nichts. Nach dem Umstellen zeigt die Seite also den Stand
eines früheren Laufs oder keine Kleider. Das meldet diese Klasse: Sie vergleicht den Lauf in `kleider_<g>/ki.json` beider Geschlechter.

Tests aus der Zeit, als der Kostüm-Weg beide baute, tragen zweimal denselben Lauf und gelten als aktuell. Ihre Figur kann trotzdem älter sein (n2_mesh_genesis, gesehen 06.11.2026: `form_maennlich` 15:46, `form_weiblich` 17:21).

    Meshgenesistestgeschlechtstand.fuer(ordner, 'maennlich') -> None | {'geschlecht', 'anderes', 'lauf', 'lauf_anderes'}      (lauf: `YYYY.MM.DD.HH.MM`, None ohne Kostüm-Lauf)
    Meshgenesistestgeschlechtstand.text(ordner, 'maennlich') -> None | Satz für Test- und Jobseite
"""

import json
import re

__all__ = ['Meshgenesistestgeschlechtstand']


class Meshgenesistestgeschlechtstand:
    NAMEN = {'weiblich': 'weiblich', 'maennlich': 'männlich'}

    @staticmethod
    def _datum(zeit):
        """`2026.11.06.17.23` → `06.11.2026 17:23`."""
        return re.sub(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d+)$', r'\3.\2.\1 \4:\5', zeit)

    @classmethod
    def text(cls, ordner, geschlecht):
        """Der Satz für die Seite oder None, wenn es nichts zu sagen gibt."""
        s = cls.fuer(ordner, geschlecht)
        if s is None:
            return None
        name = cls.NAMEN[geschlecht]
        lage = 'stammen die Kleider aus einem älteren Lauf (%s)' % cls._datum(s['lauf']) if s['lauf'] else 'gibt es noch keine Kleider aus einem Lauf'
        return 'Für %s %s, zuletzt gerechnet wurde %s (%s). Neu rechnen baut sie für %s.' % (name, lage, cls.NAMEN[s['anderes']], cls._datum(s['lauf_anderes']), name)

    @staticmethod
    def _zeit(ordner, geschlecht):
        """Zeit des letzten Kostüm-Laufs dieses Geschlechts (`<Zeit>_kostuem_stufe<n>`, als Text sortierbar) oder None."""
        try:
            lauf = json.loads((ordner / ('kleider_%s' % geschlecht) / 'ki.json').read_text(encoding='utf-8'))['kostuem']['lauf']
        except (OSError, ValueError, KeyError, TypeError):
            return None
        return str(lauf).split('_kostuem_')[0]

    @classmethod
    def fuer(cls, ordner, geschlecht):
        """None, wenn dieses Geschlecht den jüngsten Kostüm-Lauf trägt oder es keinen gibt; sonst, was die Seite dazu sagt."""
        anderes = 'maennlich' if geschlecht == 'weiblich' else 'weiblich'
        eigen, fremd = cls._zeit(ordner, geschlecht), cls._zeit(ordner, anderes)
        if fremd is None or (eigen is not None and eigen >= fremd):
            return None
        return {'geschlecht': geschlecht, 'anderes': anderes, 'lauf': eigen, 'lauf_anderes': fremd}
