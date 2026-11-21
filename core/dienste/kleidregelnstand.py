# -*- coding: utf-8 -*-
"""Kleidregelnstand — der Eintrag „regeln“ der Stücke von Kleiderbibliothek (z), Eigen (e) und Drapieren (f)
für die Kleiderliste der Testseite (21.11.2026, Edgar: „wo ist jetzt deine neue Kleider Auswahl im UI?“;
Konzept `Docu/konzepte/2026-11-21_bibliothek-anpassen-konzept.md`, Abschnitt 11: „die Seite zeigt den
Eintrag `regeln` am Stück noch nicht an“).

Die Stufe „Kleidungsregeln“ (`meshgenesis/meshgenesis_kleidstufe.py`) schreibt je Stück in
`kleider_<g>/<weg>/<id>/eintrag.json` → `regeln` den Stand je Regel. `ergaenzen` hängt an die Einträge
z, e, f einer Zeile den Schlüssel `regeln_text` = {'kurz': 'gebaut mit: Fetzen weg (31 Inseln) · …',
'titel': Stand je Regel, eine Zeile je Regel}; `Meshgenesistestkleidregeln` (JS) zeigt beides. Namen der
Regeln aus dem Katalog (`Kleidregelnkatalog`). Ohne Eintrag oder ohne wirksame Regel: kein `kurz`.
"""
import json

from .kleidregelnkatalog import Kleidregelnkatalog

__all__ = ['Kleidregelnstand']


def _de(zahl, stellen=0):
    return f'{zahl:,.{stellen}f}'.replace(',', '\0').replace('.', ',').replace('\0', '.')


class Kleidregelnstand:
    WEGE = ('z', 'e', 'f', 'p')

    @staticmethod
    def _zusatz(kennung, b):
        """Kurzer Zusatz zu einer angewandten Regel aus ihrem Befund."""
        if kennung == 'fetzen':
            return f"{b['fetzen']} Inseln, {_de(b['cm2'], 0)} cm²"
        if kennung == 'rand_glatt':
            return f"Zacken {_de(b['zacken_vorher_mm'], 2)} → {_de(b['zacken_nachher_mm'], 2)} mm"
        if kennung == 'rock':
            return f"{_de(b['punkte'])} Punkte"
        if kennung == 'oeffnungen':
            return f"{b['deckel']} Löcher geschlossen"
        if kennung == 'abschluss':
            return f"Saum an {b['saum_raender']} Rändern"
        return ''

    @classmethod
    def _text(cls, regeln):
        """{'kurz', 'titel'} aus dem Eintrag `regeln` eines Stücks oder None."""
        katalog = {r['kennung']: r['name'] for r in Kleidregelnkatalog._laden('kleidregeln.json')['regeln']}
        kurz, titel = [], []
        for kennung, name in katalog.items():
            b = regeln.get(kennung)
            if not isinstance(b, dict):
                continue
            stand = b.get('stand', '')
            if stand == 'angewandt':
                zusatz = cls._zusatz(kennung, b)
                kurz.append(f'{name} ({zusatz})' if zusatz else name)
                titel.append(f'{name}: angewandt' + (f' ({zusatz})' if zusatz else ''))
            else:
                titel.append(f'{name}: {stand}' + (f" — {b['text']}" if b.get('text') else ''))
        if not titel:
            return None
        kopf = 'Kleidungsregeln dieses Stücks (Stufe „Kleidungsregeln“)\n'
        return {'kurz': ('gebaut mit: ' + ' · '.join(kurz)) if kurz else '', 'titel': kopf + '\n'.join(titel)}

    @classmethod
    def ergaenzen(cls, eintrag, ordner, stueck_id):
        """Hängt an `eintrag[weg]` (z, e, f) den Schlüssel `regeln_text`, wo die Stufe das Stück bearbeitet
        hat; `ordner` = `kleider_<g>`."""
        for weg in cls.WEGE:
            e = eintrag.get(weg)
            if not isinstance(e, dict) or e.get('fehler'):
                continue
            datei = ordner / weg / stueck_id / 'eintrag.json'
            try:
                regeln = json.loads(datei.read_text(encoding='utf-8')).get('regeln')
            except (OSError, ValueError):
                continue
            text = cls._text(regeln) if isinstance(regeln, dict) else None
            if text:
                eintrag[weg] = dict(e, regeln_text=text)
