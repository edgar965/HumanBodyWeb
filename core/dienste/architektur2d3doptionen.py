# -*- coding: utf-8 -*-
"""Architektur2d3doptionen — ALLE Einstellungen eines Auftrags „2D3D Kleider" mit Vorgabe, Werten und Hinweis, gelesen beim Aufruf der Seite aus den Katalogen des Codes (06.10.2026).

Edgar, 06.10.2026: „mach auch möglichst viele technische Details im unteren Bereich hinein, zu den Trellis Parametern usw." Die Tabelle wird NICHT von Hand gepflegt: sie liest dieselben Prüferklassen,
die auch den Auftrag prüfen (`Engine2d3dKleideroptionen.PRUEFER`), samt den Vorgaben, die dieser Bereich von der Vorlage abweichen lässt (`ABWEICHUNGEN`). So steht dort immer, was der Code heute
tut — und ein Feld, das im Formular der Seite fehlt, aber wirkt (`im_formular` = nein), fällt auf. Die Hinweise der Felder tragen die Messwerte, die beim Bau des Feldes gelten; die Fakten dazu
und die Fallen stehen in `Architektur2d3dfaktennetz` und `Architektur2d3dfaktenkoerper`.
"""

import logging

from .engine2d3dkleidernurtrellis import Engine2d3dKleidernurtrellis
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen

__all__ = ['Architektur2d3doptionen']

logger = logging.getLogger('core')


class Architektur2d3doptionen:
    #: (Gruppe, Überschrift, welcher Schritt sie liest)
    GRUPPEN = {
        'figur': ('Figur (Schritt koerper und grundfigur)', 'Genesis-9-Figur: Basis, Größe, Fit, Textur, Kopfhaut, Kleidung'),
        'vorbereitung': ('Vorbereitung (Schritt vorbereitung)', 'Fotos aufbereiten'),
        'netz': ('Netz — Freistellen, Textur, Licht (Schritt netz)', 'Meshoptionen, Hunyuan gestrichen'),
        'mesh': ('Mesh — TRELLIS.2 / Pixal3D (Schritt netz)', 'das Interface des Hugging-Face-Space, alle Regler'),
        'kopf': ('Kopf — eigener Hunyuan3D-Lauf (Schritt kopf)', 'Häkchen, Modell, Flächen'),
        'segmentierung': ('Segmentierung — Sapiens (Schritt segmentierung)', 'Kleidungsmaske, Haar, Modellgröße'),
        'koerper': ('Körper (Schritt koerper)', 'woher die Figur kommt, Netztiefe, Oberteil'),
        'iterationen': ('Iterationen (Schritt iterationen)', 'Modus, Runden, Auflösung der Note, Haarumbau, Licht, Belichtung'),
        'film': ('Film (Schritt film)', 'BVH, Bilder, Größe'),
        'renderqualitaet': ('Render: Qualität', 'Figurfilm.Filmregler, Film und Standbild'),
        'renderlicht': ('Render: Licht', 'Figurfilm.Filmregler'),
        'renderhaut': ('Render: Haut und Material', 'Figurfilm.Filmregler'),
        'renderphysik': ('Render: Physik', 'Figurfilm.Filmregler'),
        'rendermimik': ('Render: Mimik', 'Figurfilm.Filmregler'),
    }

    @staticmethod
    def _text(wert):
        if isinstance(wert, bool):
            return 'ja' if wert else 'nein'
        if wert is None or wert == '':
            return '–'
        return str(wert).replace('.', ',') if isinstance(wert, float) else str(wert)

    @classmethod
    def _werte(cls, feld):
        """Die erlaubten Werte als Text: „a · b · c", „min–max" oder die Art des Feldes."""
        werte = feld.get('werte')
        if werte:
            namen = []
            for w in werte:
                namen.append(str(w.get('wert') if isinstance(w, dict) else (w[0] if isinstance(w, (list, tuple)) else w)))
            return ' · '.join(namen)
        if feld.get('min') is not None and feld.get('max') is not None:
            return '%s–%s' % (cls._text(feld['min']), cls._text(feld['max']))
        return str(feld.get('art') or '')

    @classmethod
    def _fremd(cls, feld):
        """Ein Feld des Katalogs der Seite „Mesh", das nur für das andere Formmodell gilt (Edgar, 02.10.2026: „NUR trellis in dem Workflow") — erkannt am Namen des Modells in Titel, Hinweis oder Werten."""
        text = ' '.join([str(feld.get('titel', '')), str(feld.get('hinweis', '')), cls._werte(feld)]).lower()
        return 'hunyuan' in text

    @classmethod
    def zeilen(cls, gruppe, pruefer, gezaehlt=None):
        """Die Felder der Gruppe als Zeilen. Gruppe `netz`: ohne die drei Felder, die seit 02.10.2026 in `mesh` stehen (`UEBERNAHME`), und ohne Felder des anderen Formmodells —
        sie werden nur GEZÄHLT (`gezaehlt['umgezogen']`, `gezaehlt['fremd']`), die Seite nennt die Zahl."""
        gezaehlt = gezaehlt if gezaehlt is not None else {}
        sichtbar = Engine2d3dKleideroptionen.SICHTBAR.get(gruppe)
        abweichung = Engine2d3dKleideroptionen.ABWEICHUNGEN.get(gruppe, {})
        aus = []
        for feld in pruefer.katalog().get('optionen') or []:
            schluessel = feld.get('schluessel', '')
            if gruppe == 'netz':
                if schluessel in Engine2d3dKleideroptionen.UEBERNAHME:
                    gezaehlt['umgezogen'] = gezaehlt.get('umgezogen', 0) + 1
                    continue
                feld = Engine2d3dKleidernurtrellis.katalogfeld(feld)
                if cls._fremd(feld):
                    gezaehlt['fremd'] = gezaehlt.get('fremd', 0) + 1
                    continue
            abgeleitet = schluessel in abweichung
            aus.append({
                'schluessel': schluessel,
                'titel': feld.get('titel', ''),
                'vorgabe': cls._text(abweichung.get(schluessel, feld.get('vorgabe'))),
                'abweichung': abgeleitet,
                'werte': cls._werte(feld),
                'hinweis': feld.get('hinweis', '') or '',
                'im_formular': sichtbar is None or schluessel in sichtbar,
                'gilt': feld.get('gilt'),
            })
        return aus

    @classmethod
    def kontext(cls):
        """`[{gruppe, titel, hinweis, zeilen, anzahl, verborgen}]` in der Reihenfolge von `Engine2d3dKleideroptionen.GRUPPEN`."""
        pruefer = dict(Engine2d3dKleideroptionen.PRUEFER)
        gruppen = []
        for name in Engine2d3dKleideroptionen.GRUPPEN:
            titel, hinweis = cls.GRUPPEN.get(name, (name, ''))
            gezaehlt = {}
            try:
                zeilen = cls.zeilen(name, pruefer[name], gezaehlt)
            except Exception as fehler:      # eine kaputte Gruppe darf die Seite nicht kippen — sie steht dann leer da, mit Grund
                logger.warning('Architektur 2D3D: Optionsgruppe %s nicht lesbar: %s', name, fehler)
                zeilen = []
            gruppen.append({
                'gruppe': name,
                'titel': titel,
                'hinweis': hinweis,
                'zeilen': zeilen,
                'anzahl': len(zeilen),
                'verborgen': sum(1 for z in zeilen if not z['im_formular']),
                'umgezogen': gezaehlt.get('umgezogen', 0),
                'fremd': gezaehlt.get('fremd', 0),
            })
        return gruppen
