# -*- coding: utf-8 -*-
"""Mesh3dmodellspeichern — das Genesis-Modell eines Mesh-3D-Auftrags (eines Modell-Imports) speichern, und zwar nur auf Klick (15.10.2026).

Edgar: „die neuen Modelle, z.B. bei dir und bei den Jobs von Mesh-3D sollen nicht automatisch gespeichert werden, nur wenn ich das im jeweiligen Jobfenster anklicke.“
Bis dahin schrieb jeder Lauf `data/models/<Name>.json` selbst — der Schritt „modell“ beim Weg „teile“, „Mesh to 3D“ (Option `modell = an`) beim Weg „netz“; aus Probe-
und Neuläufen standen so Modelle wie „Zauberer Mesh 12“ in der Liste.

- **Schritt „modell“** (`schritt`, aus `Blendimportlauf._modell`): schreibt nur, wenn der Stand `modell_speichern` trägt. Das setzt allein „Datei → Modell importieren…“ der
  Charakter-Seite (`Blendimportendpunkte.starten`): dort IST der Klick auf „Importieren“ der Auftrag, ein Modell zu bauen, und der Dialog lädt es danach in die Szene.
  Sonst hält der Schritt nur fest, dass das Modell gespeichert werden kann (`ergebnis.modell = {name: None, bereit: True}`). Beim Weg „netz“ steuert dasselbe Feld die Option
  `modell` von „Mesh to 3D“ (`Blendimportfigur`).
- **Knopf „Als Modell speichern“** der Jobseite (`speichern`, `POST /api/mesh3d/<kennung>/modell/`): Weg „teile“ = derselbe Bau wie der Schritt (`Blendimportmodell`, braucht den
  fertigen Lauf: Stücke, Haut, Augen); Weg „netz“ = `Meshfigurspeichern.modell_speichern` des Auftrags „Mesh to 3D“ — bei einer übernommenen Variante der ihre (die Seite zeigt sie).
  Ein zweiter Klick schreibt das Modell unter demselben Namen neu; eine FREMDE Figur gleichen Namens wird nie überschrieben (beide Wege nummerieren dann weiter).
"""

import logging

from .blendimportweg import Blendimportweg

logger = logging.getLogger('core')

__all__ = ['Mesh3dmodellspeichern']


class Mesh3dmodellspeichern:
    @classmethod
    def schritt(cls, lauf):
        """Schritt „modell“ des Imports (`lauf`: `Blendimportlauf`)."""
        if lauf.stand.get('modell_speichern'):
            cls._teile(lauf, lauf.melden)
            return
        lauf.ergebnis('modell', {'name': None, 'bereit': True})

    @staticmethod
    def _teile(lauf, melden):
        from .blendimportmodell import Blendimportmodell
        from .blendimportschamdaz import Blendimportschamdaz

        e = lauf.stand.get('ergebnis') or {}
        modell = Blendimportmodell(lauf.ablage, lauf.job(), lauf.stand['quelle']['datei'],
                                   lauf.stand['einstellungen']['browser_px'], lauf.zusatzregler())
        name = modell.schreiben(lauf.stand['quelle']['name'], (e.get('haut') or {}).get('kacheln') or {},
                                (e.get('augen') or {}).get('pfad'), (e.get('stuecke') or {}).get('stuecke') or {})
        daz = Blendimportschamdaz.bauen(name, lauf.stand['einstellungen'], melden)      # nur bei „DAZ“ (Einstellungen → Genesis)
        lauf.ergebnis('modell', {'name': name, **({'daz': daz} if daz else {})})
        return name

    @classmethod
    def speichern(cls, kennung):
        """Knopf der Jobseite → Name des gespeicherten Modells. `LookupError` ohne Auftrag, `ValueError` mit Grund, wenn (noch) nichts zu speichern ist."""
        from .blendimportarbeiter import Blendimportarbeiter
        from .blendimportlauf import Blendimportlauf

        lauf = Blendimportlauf(kennung)
        if not lauf.stand:
            raise LookupError('Kein Auftrag %s' % kennung)
        if lauf.stand.get('status') == 'laeuft' or Blendimportarbeiter.lebt(lauf.ablage):
            raise ValueError('Der Auftrag rechnet — gespeichert wird nach dem Lauf')
        if not ((lauf.stand.get('ergebnis') or {}).get('figur') or {}).get('id'):
            raise ValueError('Noch keine Figur — erst rechnen')
        if lauf.weg() == Blendimportweg.NETZ:
            name = cls._netz(lauf, kennung)
        else:
            if lauf.stand.get('status') != 'fertig':
                raise ValueError('Der Lauf ist nicht bis zum Ende gekommen — ohne Stücke, Haut und Augen wäre das Modell unvollständig')
            name = cls._teile(lauf, lambda *_: None)
        logger.info('Mesh-3D %s: Modell „%s" auf Klick gespeichert', kennung, name)
        return name

    @staticmethod
    def _netz(lauf, kennung):
        from .mesh3dvarianten import Mesh3dvarianten
        from .meshfigurspeichern import Meshfigurspeichern

        variante = Mesh3dvarianten.haupt_job(kennung)
        job = variante or lauf.job()
        if job.status != 'fertig':
            raise ValueError('Die Figur ist nicht fertig gerechnet')
        name = Meshfigurspeichern.fuer(job).modell_speichern()
        if variante is None:
            lauf.ergebnis('modell', {'name': name, 'weg': Blendimportweg.NETZ})
        return name
