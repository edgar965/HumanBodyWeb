# -*- coding: utf-8 -*-
"""Blendimportquelle — welche .blend ein Import liest und wie die Figur heißt.

Edgar (08.10.2026): „die letzte blender Datei (mit der aktuellsten Version)" und „name wie der Ordner". Im Ordner von
„cute girl" liegen `cute girl 4.0.blend`, `cute girl 4.5.blend`, `cute girl 5.0.blend` — die Fassung steht im Namen,
nicht in der Änderungszeit (alle drei am 07.07.2026 binnen drei Minuten geschrieben). Deshalb entscheidet die höchste
Zahl im Dateinamen; ohne Zahl die jüngste Datei. Blenders Sicherungen (`.blend1`, `.blend2`) zählen nicht.
"""

import re
from pathlib import Path

__all__ = ['Blendimportquelle']


class Blendimportquelle:
    _FASSUNG = re.compile(r'(\d+(?:\.\d+)*)\s*$')

    #: Längster eigener Name — er wird Dateiname der Stücke und Eintrag in den Listen.
    NAME_MAX = 60

    def __init__(self, pfad, namensart='ordner', eigener_name='', endung='.blend'):
        """`endung`: `.blend` (Vorgabe), `.obj` oder `.fbx` — `Blendimportformate`. Alles andere (Fassung im Namen, Name der
        Figur) gilt für alle Formate gleich."""
        text = str(pfad or '').strip().strip('"').strip("'").strip()
        self.endung = str(endung).lower()
        if not text:
            raise ValueError('Pfad fehlt: ein Ordner mit %s-Dateien oder eine %s' % (self.endung, self.endung))
        self.eingabe = Path(text).expanduser()
        self.namensart = namensart
        self.eigener_name = str(eigener_name or '')

    @classmethod
    def fassung(cls, datei):
        """`(5, 0)` aus `cute girl 5.0.blend`, `()` ohne Zahl am Ende des Stamms."""
        treffer = cls._FASSUNG.search(Path(datei).stem)
        return tuple(int(t) for t in treffer.group(1).split('.')) if treffer else ()

    def kandidaten(self):
        if self.eingabe.is_file():
            if self.eingabe.suffix.lower() != self.endung:
                raise ValueError('Keine %s: %s' % (self.endung, self.eingabe.name))
            return [self.eingabe]
        if not self.eingabe.is_dir():
            raise ValueError('Nicht gefunden: %s' % self.eingabe)
        dateien = [p for p in self.eingabe.iterdir() if p.is_file() and p.suffix.lower() == self.endung]
        if not dateien:
            raise ValueError('Keine %s im Ordner %s' % (self.endung, self.eingabe))
        return sorted(dateien, key=lambda p: (self.fassung(p), p.stat().st_mtime), reverse=True)

    def datei(self):
        """Die .blend, die gelesen wird."""
        return self.kandidaten()[0]

    def name(self):
        """Der Name der Figur: `eigen` = der Text aus dem Namensfeld, `ordner` = wie der Ordner der Datei, sonst der
        Dateistamm ohne Fassung. Sonderzeichen entfallen (der Name wird Teil von Dateinamen)."""
        if self.namensart == 'eigen':
            name = re.sub(r'\s+', ' ', re.sub(r'[^\w\s\-]', '', self.eigener_name)).strip()[:self.NAME_MAX].strip()
            if not name:
                raise ValueError('Eigener Name fehlt: Namen ins Textfeld schreiben (Buchstaben, Ziffern, Leerzeichen, Bindestrich)')
            return name
        datei = self.datei()
        if self.namensart == 'ordner':
            roh = datei.parent.name
        else:
            roh = self._FASSUNG.sub('', datei.stem)
        return re.sub(r'[^\w\s\-]', '', roh).strip() or ('Blender Modell' if self.endung == '.blend' else 'Modell')

    def steckbrief(self):
        kandidaten = self.kandidaten()
        return {
            'datei': str(kandidaten[0]),
            'format': self.endung.lstrip('.'),
            'name': self.name(),
            'kandidaten': [{'datei': p.name, 'fassung': '.'.join(map(str, self.fassung(p))) or '—',
                            'mb': round(p.stat().st_size / 1e6, 1)} for p in kandidaten],
        }
