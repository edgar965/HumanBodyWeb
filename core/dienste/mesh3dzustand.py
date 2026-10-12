# -*- coding: utf-8 -*-
"""Mesh3dzustand — der Stand EINES Imports als ein Wörterbuch für die Jobseite „Mesh-3D“ (11.10.2026).

Die Seite fragt alle paar Sekunden `GET /api/mesh3d/<kennung>/zustand/` und zeichnet daraus Laufleiste und Karten. Kopf (Name, Status,
Fortschritt), Schritte (`Mesh3dschritte`) und die Ergebnisse je Karte (`Mesh3dergebnisse`) kommen aus `stand.json`; „läuft“, ohne dass der
Arbeitsprozess noch lebt, gilt als gescheitert (wie `Blendimportendpunkte.zustand`) — sonst bliebe die Seite ewig auf „Berechnet …“.
"""

from ..daten.blendimportablage import Blendimportablage
from .blendimportarbeiter import Blendimportarbeiter
from .mesh3dbewegung import Mesh3dbewegung
from .mesh3dergebnisse import Mesh3dergebnisse
from .mesh3dnetzansicht import Mesh3dnetzansicht
from .mesh3dschritte import Mesh3dschritte

__all__ = ['Mesh3dzustand']


class Mesh3dzustand:
    @classmethod
    def stand(cls, kennung):
        """`stand.json` mit der Prüfung auf einen toten Arbeitsprozess; `None`, wenn es den Import nicht gibt."""
        try:
            ablage = Blendimportablage(kennung)
        except ValueError:
            return None
        stand = ablage.stand()
        if not stand:
            return None
        if stand.get('status') == 'laeuft' and not Blendimportarbeiter.lebt(ablage):
            stand = ablage.stand()
            if stand.get('status') == 'laeuft':
                stand.update(status='gescheitert', fehler=stand.get('fehler') or 'Arbeitsprozess lebt nicht mehr (auftrag.log)')
                ablage.stand_schreiben(stand)
        return cls._mit_figurlauf(stand)

    @staticmethod
    def _mit_figurlauf(stand):
        """Im Schritt „figur“ schreibt der Arbeitsprozess nichts mehr in `stand.json`: er wartet auf den Auftrag „Mesh to 3D“ (der Wert 16 % blieb
        über Stunden stehen, gemessen 12.10.2026 am Zauberer, während der Auftrag bei 57 % rechnete). Fortschritt und Text kommen deshalb vom
        Auftrag selbst, auf das Band des Wegs umgerechnet — für die Liste, ihren Takt und die Jobseite gleich. Geschrieben wird nichts."""
        lauf = (Mesh3dergebnisse(stand)._figurlauf() or {}).get('lauf')
        if not lauf:
            return stand
        live = dict(stand, fortschritt=max(int(stand.get('fortschritt') or 0), int(lauf['fortschritt'])))
        if lauf.get('detail'):
            live['detail'] = str(lauf['detail'])[:200]
        return live

    @classmethod
    def von(cls, kennung):
        stand = cls.stand(kennung)
        if stand is None:
            return None
        quelle = stand.get('quelle') or {}
        e = Mesh3dergebnisse(stand)
        figur = e.figur()
        fortschritt = (figur or {}).get('lauf', {}).get('fortschritt') or 0
        return {
            'kennung': kennung,
            'name': quelle.get('name') or kennung,
            'format': quelle.get('format') or 'blend',
            'bereich': stand.get('bereich'),
            'weg': stand.get('weg') or 'teile',
            'weg_grund': stand.get('weg_grund') or '',
            'status': stand.get('status'),
            'fehler': stand.get('fehler') or '',
            'schritt': stand.get('schritt'),
            'detail': stand.get('detail') or '',
            'fortschritt': max(int(stand.get('fortschritt') or 0), int(fortschritt) if stand.get('schritt') == 'figur' else 0),
            'angelegt': stand.get('angelegt'),
            'gestartet': stand.get('gestartet'),
            'beendet': stand.get('beendet'),
            'dauer_s': stand.get('dauer_s'),
            'ab': stand.get('ab'),
            'quelle': {'datei': quelle.get('datei'), 'format': quelle.get('format'), 'kandidaten': quelle.get('kandidaten') or []},
            'einstellungen': stand.get('einstellungen') or {},
            'schritte': Mesh3dschritte.liste(stand),
            #: die Schritte, ab denen ein Lauf beginnen darf (die Kette kennt sie auch dann, wenn ein alter Stand sie nicht nennt)
            'moegliche': [{'schluessel': s, 'titel': Mesh3dschritte.TITEL.get(s, s)} for s in Mesh3dschritte.namen(stand)],
            'rollen': e.rollen(),
            'umposen': e.umposen(),
            'pose': e.pose(),
            'segmentierung': e.segmentierung(),
            'koerper': e.koerper(),
            'figur': figur,
            'finger': e.finger(),
            'stuecke': e.stuecke(),
            'haut': e.haut(),
            'augen': e.augen(),
            'modell': e.modell(),
            #: die schon gerechnete Bewegung für die Animationsleiste der 3D-Ansicht (`Mesh3dbewegung`), sonst `None`
            'bewegung': Mesh3dbewegung(kennung).stand(),
            #: die vereinfachte Netz-Kopie für die 3D-Ansicht (`Mesh3dnetzansicht`): `status` keine · unnoetig · bereit · baut · fehlt · fehler
            'netzansicht': Mesh3dnetzansicht(kennung).zustand(),
        }
