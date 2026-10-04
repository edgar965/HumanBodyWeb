# -*- coding: utf-8 -*-
"""Architektur2d3dwerkzeuge — die Daten des Reiters „Tools" der Seite Hilfe → Architektur → 2D3D (03.10.2026).

Edgar: „schreibe alle lokalen Tools für die Anpassung des Modells auf die Hilfeseite, damit andere Sessions das lesen können … Mach auch ein
Klassenmodell für diese Tools, also welche Klassen, welche Aufrufe im unteren Bereich der Seite." Die Gruppen stehen je in einer Datei
`werkzeug<name>.py` (Klasse `Werkzeug<Name>`, Schema in `ZEILEN`/`BEZIEHUNGEN`); diese Klasse findet sie über den Dateinamen, prüft jede genannte Klasse
gegen den Code (`Architektur2d3dklassen.zeile`) und baut daraus zwei Teile: je Gruppe die Tabelle der Werkzeuge (Wofür, Aufruf, Klassen, Hinweis) und
unten das Klassenmodell (je Klasse ein Kasten mit öffentlichen Methoden, den Aufrufen von außen und den Beziehungen zu anderen Klassen der Gruppe).
Was nicht stimmt (Klasse fehlt, Beziehung zeigt ins Leere, unbekannte Art), steht als Befund auf der Seite statt still zu verschwinden.
"""

import importlib
import logging
from pathlib import Path

from .architektur2d3dklassen import Architektur2d3dklassen

logger = logging.getLogger('core')

__all__ = ['Architektur2d3dwerkzeuge']


class Architektur2d3dwerkzeuge:
    #: Art des Aufrufs → Beschriftung (Schema: `ZEILEN` der Gruppen).
    ARTEN = {
        'rezept': 'Rezeptzeile',
        'api': 'Server-API',
        'cli': 'Befehl',
        'python': 'Python',
        'seite': 'Seite',
        'regel': 'Regel',
    }
    PFAD = Path(__file__).resolve().parent
    #: Die Bereiche der Seite in Edgars Reihenfolge (03.10.2026): (Titel, Hinweis, Kennungen der Gruppen). Gruppen, die hier fehlen, stehen unter „Weitere".
    BEREICHE = [
        ('Genesis: Körper, Gesicht, Haut', 'Morphs und Regler des Körpers einschließlich Gesicht, Haltung, Haut — die Form der Figur.',
         ['koerper', 'proportionen', 'meshfigur', 'haltung', 'gesicht', 'haut']),
        ('Genesis: Kleider und Kleider-Morphs', 'Kleidung generisch, Morphe, Garderobe, GarmentCode, Fototextur, Fotostücke, die Wahl des Drapierers.',
         ['rezeptkleidung', 'kleidform', 'kleidgenerisch', 'garderobe', 'garmentcode', 'kleidtextur', 'fotostuecke', 'drapieren', 'kleidbau',
          'kleiderautomatik', 'kleidunghilfe']),
        ('Genesis: Haar', 'Haar generisch, Haare formen, Haar aus Fotos.', ['haar', 'haarform', 'haarfoto']),
        ('Aus Blender übernommen: der Stoffsolver', 'Blenders Cloth, Haar-Dynamik und UV als Python/Warp-Paket, mit den Vergleichswerkzeugen.',
         ['stoffsolver', 'stofffedern', 'stofffelder', 'stoffhaar', 'stoffuv', 'stoffvergleich']),
        ('Bildvergleich mit den Fotos aus allen Seiten', 'Erst gering aufgelöst, höhere Auflösung, wenn die Unterschiede klein sind.',
         ['bildfotos', 'bildrender', 'bildnote', 'bildstufen', 'bildtafeln', 'bildbefund', 'bildserver', 'bildlauf']),
        ('Schleifen über Blender (nur nach Ansage)', 'Der Blender-Weg, wenn der Stoffsolver nicht funktioniert — nur nach Ansage von Edgar.',
         ['blenderschleife', 'blenderweitere']),
    ]
    WEITERE = ('Weitere', 'Gruppen, die keinem Bereich zugeordnet sind.')
    #: Was jede Session beim Benutzen der Tools wissen muss — jede Zeile steht an anderer Stelle des Codes oder der Regeln, hier nur gesammelt.
    REGELN = [
        ('Schleifen und Runden nur nach Ansage',
         'Eine Runde oder eine Folge automatischer Runden startet nur Edgar oder ein ausdrücklicher Auftrag, immer über die Server-API '
         '(Reiter „Ablauf und Klassen", „Festgelegt von Edgar": „Nichts rechnet ohne Auftrag"). Nach jeder Runde prüft Fable das Ergebnis.'),
        ('Schleifen über Blender nur nach Ansage',
         'Blender (`Engine2d3dKleiderblender`, `motor=\'blender\'`) ist der Weg, wenn der Stoffsolver nicht funktioniert oder keine CUDA-GPU da ist. '
         'Die Pipeline wählt ihn nie selbst; er kommt nur per Rezeptzeile und nur, wenn Edgar es sagt (Edgar, 03.10.2026).'),
        ('Bildvergleich erst gering aufgelöst',
         'Zuerst der kleine Template-Vergleich, höhere Auflösung erst, wenn die Unterschiede nicht mehr groß sind — inkrementell bis zur '
         'Auflösung der Fotos (`Aufloesungsstufe`, Reiter „Ablauf und Klassen", „Festgelegt von Edgar").'),
        ('Der Stoffsolver wird nur per Rezeptzeile gewählt',
         '`motor=\'stoffsolver\'` beim Drapieren und `m.haar_dynamik(sorte)` für die Haar-Dynamik; die Automatik nimmt Newton und rechnet kein Haar. '
         'Er braucht eine CUDA-GPU, ohne sie wird abgelehnt (Reiter „Workflow", Tabelle „Der Stoffsolver gegen Blender").'),
        ('Tests und Dev-Server nur nach Ansage',
         'Keine Testläufe und kein Neustart des Dev-Servers ohne Ansage; der Server lädt gespeicherte Python-Dateien selbst neu.'),
    ]

    @classmethod
    def gruppenklassen(cls):
        """Die Klassen der Gruppen: jede Datei `werkzeug<name>.py` mit der Klasse `Werkzeug<Name>` (Schema siehe Moduldocstring)."""
        gefunden = []
        for datei in sorted(cls.PFAD.glob('werkzeug*.py')):
            stem = datei.stem
            try:
                modul = importlib.import_module('.' + stem, __package__)
            except Exception as fehler:    # noqa: BLE001 — eine kaputte Gruppe darf die Seite nicht kippen; sie steht als Befund darin
                logger.warning('Architektur 2D3D Tools: %s nicht ladbar: %s', stem, fehler)
                gefunden.append((stem, None, str(fehler)))
                continue
            klasse = getattr(modul, stem.capitalize(), None)
            if klasse is None or not hasattr(klasse, 'KENNUNG'):
                logger.warning('Architektur 2D3D Tools: %s hat keine Klasse %s mit KENNUNG', stem, stem.capitalize())
                gefunden.append((stem, None, 'Klasse %s mit KENNUNG fehlt' % stem.capitalize()))
                continue
            gefunden.append((stem, klasse, ''))
        rang = {k: i for i, k in enumerate(kennung for _t, _h, kennungen in cls.BEREICHE for kennung in kennungen)}
        return sorted(gefunden, key=lambda g: (rang.get(getattr(g[1], 'KENNUNG', ''), len(rang)), g[0]))

    @classmethod
    def klasse_von(cls, eintrag, geprueft):
        """`eintrag` = (Datei, Klasse); `geprueft` merkt, was schon gelesen wurde (dieselbe Klasse steht oft in mehreren Zeilen)."""
        if eintrag not in geprueft:
            geprueft[eintrag] = Architektur2d3dklassen.zeile(*eintrag)
        return geprueft[eintrag]

    @classmethod
    def zeile(cls, kennung, roh, geprueft, befunde):
        werkzeug, wofuer, art, aufruf, klassen, hinweis = roh
        if art not in cls.ARTEN:
            befunde.append('%s / %s: unbekannte Art „%s"' % (kennung, werkzeug, art))
        karten = []
        for eintrag in klassen:
            info = cls.klasse_von(tuple(eintrag), geprueft)
            if info['fehlt']:
                befunde.append('%s / %s: %s (%s)' % (kennung, werkzeug, info['klasse'], info['fehlt']))
            karten.append({'klasse': info['klasse'], 'modul': info['modul'], 'anker': 't-%s-%s' % (kennung, info['klasse']),
                           'fehlt': info['fehlt']})
        return {'werkzeug': werkzeug, 'wofuer': wofuer, 'art': art, 'art_text': cls.ARTEN.get(art, art), 'aufruf': aufruf,
                'klassen': karten, 'hinweis': hinweis}

    @classmethod
    def modell(cls, kennung, roh_zeilen, beziehungen, geprueft, befunde):
        """Das Klassenmodell einer Gruppe: je Klasse Kasten mit Methoden, Aufrufen von außen und Beziehungen."""
        reihe, modul_von = [], {}
        for z in roh_zeilen:
            for datei, klasse in z[4]:
                if klasse not in modul_von:
                    modul_von[klasse] = datei
                    reihe.append(klasse)
        for von, _wie, nach, _womit in beziehungen:
            for name in (von, nach):
                if name not in modul_von:
                    befunde.append('%s: Beziehung nennt %s, das in keiner Zeile der Gruppe steht' % (kennung, name))
        karten = {}
        for name in reihe:
            info = cls.klasse_von((modul_von[name], name), geprueft)
            karten[name] = dict(info, anker='t-%s-%s' % (kennung, name), aufrufe=[], ruft=[], gerufen_von=[],
                                methoden_gezeigt=info['methoden'][:8], methoden_mehr=max(0, len(info['methoden']) - 8))
        for z in roh_zeilen:
            for stelle, (_datei, klasse) in enumerate(z[4]):
                karten[klasse]['aufrufe'].append({'werkzeug': z[0], 'art_text': cls.ARTEN.get(z[2], z[2]),
                                                  'einstieg': stelle == 0})
        for von, _wie, nach, womit in beziehungen:
            if von in karten and nach in karten:
                karten[von]['ruft'].append({'klasse': nach, 'anker': karten[nach]['anker'], 'womit': womit})
                karten[nach]['gerufen_von'].append({'klasse': von, 'anker': karten[von]['anker'], 'womit': womit})
        return [karten[name] for name in reihe]

    @classmethod
    def gruppe(cls, stem, klasse, fehler, geprueft):
        if klasse is None:
            return {'kennung': stem, 'titel': stem, 'einleitung': '', 'zeilen': [], 'modell': [], 'beziehungen': 0,
                    'befunde': ['%s: %s' % (stem, fehler)]}
        befunde = []
        roh = list(klasse.ZEILEN)
        beziehungen = list(getattr(klasse, 'BEZIEHUNGEN', []))
        zeilen = [cls.zeile(klasse.KENNUNG, z, geprueft, befunde) for z in roh]
        modell = cls.modell(klasse.KENNUNG, roh, beziehungen, geprueft, befunde)
        return {'kennung': klasse.KENNUNG, 'titel': klasse.TITEL, 'einleitung': klasse.EINLEITUNG, 'zeilen': zeilen, 'modell': modell,
                'beziehungen': len(beziehungen), 'befunde': befunde}

    @classmethod
    def bereiche(cls, gruppen):
        """Die Gruppen je Bereich in der Reihenfolge von `BEREICHE`; was in keinem steht, kommt unter „Weitere" ans Ende."""
        vergeben = {k for _t, _h, kennungen in cls.BEREICHE for k in kennungen}
        eintraege = [(t, h, kennungen) for t, h, kennungen in cls.BEREICHE]
        eintraege.append((cls.WEITERE[0], cls.WEITERE[1], [g['kennung'] for g in gruppen if g['kennung'] not in vergeben]))
        aus = []
        for titel, hinweis, kennungen in eintraege:
            vorhanden = [g for g in gruppen if g['kennung'] in kennungen]
            if vorhanden:
                aus.append({'titel': titel, 'hinweis': hinweis, 'gruppen': vorhanden, 'werkzeuge': sum(len(g['zeilen']) for g in vorhanden)})
        return aus

    @classmethod
    def kontext(cls):
        geprueft = {}
        gruppen = [cls.gruppe(stem, klasse, fehler, geprueft) for stem, klasse, fehler in cls.gruppenklassen()]
        befunde = [b for g in gruppen for b in g['befunde']]
        return {
            'gruppen': gruppen,
            'bereiche': cls.bereiche(gruppen),
            'regeln': [{'regel': r, 'umsetzung': u} for r, u in cls.REGELN],
            'zaehlung': {'gruppen': len(gruppen), 'werkzeuge': sum(len(g['zeilen']) for g in gruppen),
                         'klassen': sum(len(g['modell']) for g in gruppen), 'beziehungen': sum(g['beziehungen'] for g in gruppen)},
            'befunde': befunde,
        }
