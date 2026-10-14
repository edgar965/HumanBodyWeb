# -*- coding: utf-8 -*-
"""Mesh3dvariantenauto — die Vergleichsvariante, die ein fertiger Lauf des Wegs „netz“ von selbst mitrechnet (13.10.2026).

Edgar: „baue zumindest eine Variante“ — auf die Frage, ob eine zweite Ausgabe ohne Klick mitlaufen soll: „Automatisch mit jedem Lauf“. Gerechnet wird EINE Variante des Stoffzugs (`kleidung_zug`), der Einstellung, die sich an den
bisherigen Modellen am stärksten unterschied (Robe: Oberschenkel 103,5 / 72,2 / 51,4 cm für weich / nah / ignorieren; Edgar: nah ≈ weich). Der Gegenwert zum Wert des Auftrags: `nah` → `ignorieren`, `ignorieren` → `nah`,
`weich` → `nah`. Es ist eine gewöhnliche Variante (`Mesh3dvarianten`: eigener Auftrag „Mesh to 3D“, Vergleich, Übernehmen, Löschen) mit dem Merkmal `automatisch` in `varianten.json`.

* **Wann:** am Ende von `Blendimportlauf.ausfuehren`, wenn der Weg „netz“ ohne Fehler durch ist und die Einstellung `vergleichsvariante` nicht auf „aus“ steht (fehlt sie, gilt „an“ — wie die Vorgabe des Katalogs).
* **Warten:** der Arbeitsprozess des Imports lebt in diesem Augenblick noch; die Variante rechnet in ihrem eigenen Prozess (`Mesh3dvariantenlauf`, `warten = True`) und wartet, solange ein ANDERER Import rechnet (GPU und Kerne gehören ihm).
* **Neuer Lauf:** die automatische Variante verglich sich mit der alten Hauptausgabe — `Blendimportarbeiter.starten` entfernt sie (`entfernen`), der neue Lauf legt eine neue an. Von Hand angelegte Varianten bleiben, wie sie sind.
* **Wirft nie:** ein Fehler hier lässt den fertigen Import fertig (`sicher`), er steht im Log.
"""

import logging

from ..daten.blendimportablage import Blendimportablage
from .mesh3dvarianten import Mesh3dvarianten

logger = logging.getLogger('core')

__all__ = ['Mesh3dvariantenauto']


class Mesh3dvariantenauto:
    FELD = 'kleidung_zug'
    #: Der Gegenwert zum Stoffzug des Auftrags (eine Setzung, siehe Kopf).
    GEGENWERT = {'nah': 'ignorieren', 'ignorieren': 'nah', 'weich': 'nah'}

    @classmethod
    def sicher(cls, kennung):
        """Wie `anlegen`, aber ein Fehler wird nur protokolliert (Aufruf am Ende des Imports)."""
        try:
            return cls.anlegen(kennung)
        except Exception:  # noqa: BLE001 — Zusatz: der Import ist fertig, was auch passiert
            logger.exception('Mesh-3D %s: Vergleichsvariante nicht angelegt', kennung)
            return None

    @classmethod
    def anlegen(cls, kennung):
        """Die Vergleichsvariante anlegen und starten → ihr Eintrag, oder `None` (kein Weg „netz“, Einstellung aus, Hauptausgabe nicht fertig, Wert schon vorhanden, Grenze erreicht)."""
        from .mesh3dvariantenlauf import Mesh3dvariantenlauf

        ablage = Blendimportablage(kennung)
        stand = ablage.stand()
        if not stand or (stand.get('weg') or 'teile') != 'netz':
            return None
        if (stand.get('einstellungen') or {}).get('vergleichsvariante', 'an') != 'an':
            return None
        wert = cls.GEGENWERT.get(Mesh3dvarianten.aktuell(stand, cls.FELD))
        daten = Mesh3dvarianten.lesen(kennung)
        vorhanden = {e['wert'] for e in daten['eintraege'] if e['feld'] == cls.FELD} | {daten['vorher'].get(cls.FELD)}
        if wert is None or wert in vorhanden or len(daten['eintraege']) >= Mesh3dvarianten.HOECHSTENS:
            return None
        try:
            Mesh3dvarianten._hauptauftrag(stand)
        except ValueError as grund:
            logger.info('Mesh-3D %s: keine Vergleichsvariante — %s', kennung, grund)
            return None
        eintrag = {**Mesh3dvarianten._eintrag(ablage, stand, Mesh3dvarianten.feld(cls.FELD), wert), 'automatisch': True}
        daten['eintraege'].append(eintrag)
        Mesh3dvarianten.schreiben(kennung, daten)
        if not Mesh3dvariantenlauf.lebt(kennung):                      # ein rechnender Prozess nimmt den neuen Eintrag selbst mit
            Mesh3dvariantenlauf.starten(kennung, warten=True)
        logger.info('Mesh-3D %s: Vergleichsvariante %s = %s angelegt', kennung, cls.FELD, wert)
        return eintrag

    @classmethod
    def entfernen(cls, kennung):
        """Vor einem neuen Lauf des Imports: die automatischen Varianten samt Auftrag und Ordner entfernen (sie verglichen sich mit der alten Hauptausgabe) → Anzahl."""
        from .mesh3dvariantenlauf import Mesh3dvariantenlauf

        try:
            automatisch = [e for e in Mesh3dvarianten.lesen(kennung)['eintraege'] if e.get('automatisch')]
            if not automatisch:
                return 0
            if Mesh3dvariantenlauf.lebt(kennung):
                Mesh3dvariantenlauf.anhalten(kennung)
            for eintrag in automatisch:
                Mesh3dvarianten.loeschen(kennung, eintrag['id'])
            return len(automatisch)
        except (OSError, ValueError):
            logger.exception('Mesh-3D %s: automatische Varianten nicht entfernt', kennung)
            return 0
