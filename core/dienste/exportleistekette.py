# -*- coding: utf-8 -*-
"""Exportleistekette — die Stücke der Seite mit Stoff oder Haar aus der Mesh-Genesis-Kette für den Render der Exportleiste auflösen (20.11.2026, Edgar „ja, Weg 2“: Testseite und
Render zeigen dasselbe Ergebnis).

Die Seite schickt je Stück der Kleiderbibliothek `{name, adresse, art}` in `stellung.kette` (`Meshgenesisexportquelle`): `name` = Knoten in der GLB (`ki_<id>`), `adresse` = Netz-Adresse
des Stücks (`/api/meshgenesis/test/<kennung>/kleid/<g>/<weg>/<stück>`). Hier werden daraus geprüfte Dateien (Anzeigenetz, Stoff- und Haar-Ablage zur BVH des Renders, wie sie die Seite
über `…/stoff/` und `…/haar/` bekommt: `Meshgenesisteststoff.dateien`, `Meshgenesistesthaar.dateien`); der Render (`Figurfilm.Kettenfilm`) liest sie aus `<glb>.stellung.json`.
Fehlt die Ablage für die BVH des Renders, rechnet der Render-Prozess sie vorher mit denselben Kettenschritten (`Exportleistekettenlauf`, Edgar: „rechnet sonst mit demselben Code“) — seit
25.11.2026 ist das der einzige Ort (Edgar: „physik muss doch erst beim export in mp4 berechnet werden“), der Job rechnet keine Physik mehr. Was danach noch fehlt, bleibt im Render gehäutet.

Weicht ein Wind-, Stoff- oder Haar-Regler des Renders von der Vorgabe ab (`regler`: `Kettenregler`, 20.11.2026, Edgar: „die sollen wirken, wenn der Render eingestellt ist“), gilt die
Ablage mit seinem Zeichen (`<Kategorie>__<Name>__<Zeichen>`); fehlt sie, wird sie gerechnet, und nie die Ablage der Seite genommen.

    stellung = Exportleistekette.aufloesen(stellung, bvh_pfad, regler)
    fehlt = Exportleistekette.fehlend(stellung, bvh_pfad, regler)       # [(kennung, g, 'stoff'|'haar', stück)]
"""

import logging
import os
import re
import sys
from pathlib import Path

from django.conf import settings

from .meshgenesistestkleider import Meshgenesistestkleider
from .meshgenesisteststoff import Meshgenesisteststoff
from .meshgenesistesthaar import Meshgenesistesthaar
from KoerperKI_alle.npztorch import Npztorch  # noqa: E402 — den Pfad dahin setzt `meshgenesisteststoff`

logger = logging.getLogger('core')

__all__ = ['Exportleistekette']


class Exportleistekette:
    ADRESSE = re.compile(r'^/api/meshgenesis/test/(?P<kennung>[A-Za-z0-9_\-]+)/kleid/(?P<g>[a-z]+)/(?P<weg>[a-z]+)/(?P<stueck>[A-Za-z0-9_\-]+)/?$')
    NAME = re.compile(r'^[A-Za-z0-9_\-.]{1,120}$')

    @staticmethod
    def wahl(bvh_pfad):
        """'Ordner/Name' der BVH — so benennen die Läufe ihre Ablage (`Kleiderstofflauf.name`: `<Ordner>__<Name>`), für die Bibliothek ist das 'Kategorie/Name' der Seite.
        None ohne Pfad; Namen, die keine Ablage tragen dürfen, weist `Meshgenesisteststoff.name` ab."""
        p = Path(str(bvh_pfad or ''))
        return '%s/%s' % (p.parent.name, p.stem) if p.stem and p.parent.name else None

    @classmethod
    def seite(cls, stellung):
        """Die geprüften Angaben der Seite: [(Eintrag {name, adresse, art}, (kennung, g, weg, stück))] — aus `kette_seite` (schon aufgelöst) oder `kette` (wie gesendet)."""
        roh = stellung.get('kette_seite') if 'kette_seite' in stellung else stellung.get('kette')
        aus = []
        for e in roh if isinstance(roh, list) else []:
            if not isinstance(e, dict) or not cls.NAME.match(str(e.get('name') or '')):
                continue
            m = cls.ADRESSE.match(str(e.get('adresse') or ''))
            teile = (m['kennung'], m['g'], m['weg'], m['stueck']) if m else None
            if teile and Meshgenesistestkleider.stueck_ordner(*teile) is not None:
                aus.append(({'name': e['name'], 'adresse': e['adresse'], 'art': str(e.get('art') or '')[:20]}, teile))
        return aus

    SCHRITTE = (('stoff', Meshgenesisteststoff), ('haar', Meshgenesistesthaar))

    @staticmethod
    def dateien(quelle, teile, wahl, zusatz=''):
        """(npz, json) oder None — ohne `zusatz` die Ablage der Seite (`quelle.dateien`), mit `zusatz` die mit Reglern des Renders (`<Kategorie>__<Name>__<Zeichen>`)."""
        if not zusatz:
            return quelle.dateien(*teile, wahl)
        name = quelle.name(wahl)
        if name is None or Meshgenesistestkleider.stueck_ordner(*teile) is None:
            return None
        ordner = Meshgenesistestkleider.ordner(teile[0], teile[1]) / teile[2] / teile[3] / quelle.ORDNER
        feld, kopf = ordner / ('%s__%s.npz' % (name, zusatz)), ordner / ('%s__%s.json' % (name, zusatz))
        return (feld, kopf) if kopf.is_file() and Npztorch.da(feld) and not quelle.veraltet(ordner, feld) else None

    @classmethod
    def fehlend(cls, stellung, bvh_pfad, regler=None):
        """[(kennung, g, Schritt 'stoff'|'haar', stück)] ohne gültige Ablage für diese BVH (und die Regler) — nur Stücke, die der Kettenschritt rechnet (`rechenbar`; ein Schuh nicht)."""
        wahl = cls.wahl(bvh_pfad)
        aus = []
        for _e, teile in cls.seite(stellung or {}) if wahl else ():
            for schritt, quelle in cls.SCHRITTE:
                zusatz = regler.zeichen(schritt) if regler else ''
                if cls.dateien(quelle, teile, wahl, zusatz) is None and (teile[2], teile[3]) in cls.rechenbar(teile[0], teile[1], schritt):
                    aus.append((teile[0], teile[1], schritt, teile[3]))
        return aus

    @staticmethod
    def rechenbar(kennung, g, schritt):
        """{(weg, stück)}, die der Kettenschritt „stoff“ bzw. „haar“ an diesem Test rechnet — seine eigene Wahl (`Kleiderstofflauf.stuecke`, `Kleiderhaarlauf.stuecke`). Nur im Render-Prozess
        (lädt die Kettenmodule). Bis 25.11.2026 zählte, ob der Job das Stück schon einmal gerechnet hatte; seit er keine Physik mehr rechnet, wäre das keins."""
        kette = os.path.join(str(settings.TOOLS_ROOT), 'meshgenesis')
        if kette not in sys.path:
            sys.path.append(kette)
        if schritt == 'stoff':
            from meshgenesis_kleiderstoff_lauf import Kleiderstofflauf as Lauf
        else:
            from meshgenesis_kleiderhaar_lauf import Kleiderhaarlauf as Lauf
        return {(weg, Path(ordner).name) for _id, weg, ordner in Lauf(kennung, g).stuecke()}

    @classmethod
    def aufloesen(cls, stellung, bvh_pfad, regler=None):
        """Kopie der Stellung, `kette` = [{name, art, netz, stoff: [npz, json] | None, haar: [npz, json] | None}] — nur Stücke mit mindestens einer Ablage; die Angaben der Seite
        bleiben als `kette_seite` (zum Nachrechnen für eine andere BVH, `Exportleistekettenlauf`)."""
        aus = dict(stellung or {})
        seite = cls.seite(aus)
        aus.pop('kette', None)
        aus['kette_seite'] = [e for e, _t in seite]
        wahl = cls.wahl(bvh_pfad)
        if not seite or wahl is None:
            return aus
        kette = []
        zusatz = {s: regler.zeichen(s) if regler else '' for s, _q in cls.SCHRITTE}
        for e, teile in seite:
            m = {'kennung': teile[0], 'g': teile[1], 'weg': teile[2], 'stueck': teile[3]}
            stoff, haar = (cls.dateien(q, teile, wahl, zusatz[s]) for s, q in cls.SCHRITTE)
            if stoff is None and haar is None:
                continue
            netz = Meshgenesistestkleider.ordner(m['kennung'], m['g']) / m['weg'] / m['stueck'] / 'anzeige' / 'netz.npz'
            kette.append({'name': e['name'], 'art': e['art'], 'netz': str(netz),
                          'stoff': [str(p) for p in stoff] if stoff else None, 'haar': [str(p) for p in haar] if haar else None})
        aus['kette'] = kette
        logger.info('Exportleistekette: %d von %d Stücken mit Ablage für %s %s (%s)', len(kette), len(seite), wahl, zusatz, ', '.join(k['name'] for k in kette))
        return aus
