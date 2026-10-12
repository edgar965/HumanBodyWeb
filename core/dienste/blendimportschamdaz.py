# -*- coding: utf-8 -*-
"""Blendimportschamdaz — die Scham-Methode „DAZ" am Ende eines Blender-Imports (Einstellungen → Genesis, `Schamwahl`).

Der Import baut das Eigen-Stück „<Name> Scham" immer (`Blendimportstuecke`, Einstellung `scham = objekt`): es ist die Vorgabe der Anpassung. Ist „DAZ" gewählt, folgt danach
`Dazgeograftangepasst` — dieselbe Kette wie `manage.py dazgeograft_anpassen --modell <Name> --scham "<Name> Scham" --ziel-modell <Name> --ableiten` (Zuschnitt auf Umriss und Loch des
Eigen-Stücks, Regler der alten Scham übernommen, Messung `Schammessung`): das Modell des Imports trägt dann das Stück „<Name> Daz Scham" statt des Eigen-Stücks. Das Eigen-Stück bleibt
in der Bibliothek. Ein Fehler beendet den Import nie — das Modell behält dann das Eigen-Stück, der Grund steht im Ergebnis des Schritts „modell".

Nur für die weibliche Scham (`Dazgeograft` kennt „Anatomical Elements" Frau): bei `scham = mann` oder einer anderen Einstellung als `objekt` passiert nichts.
"""

import logging

from .schamwahl import Schamwahl

logger = logging.getLogger('core')

__all__ = ['Blendimportschamdaz']


class Blendimportschamdaz:
    @classmethod
    def bauen(cls, name, einstellungen, melden=None):
        """`None`, wenn die Methode Eigen gilt; sonst `{'stueck', 'modell', 'punkte', 'abweichungen'}` oder `{'aus': Grund}` / `{'fehler': Text}`."""
        if Schamwahl.gewaehlt() != Schamwahl.DAZ:
            return None
        if einstellungen.get('scham') != 'objekt':
            return {'aus': 'Die Daz-Scham ersetzt nur das Eigen-Stück (Einstellung scham = objekt, nicht „%s")' % einstellungen.get('scham')}
        from .dazgeograftangepasst import Dazgeograftangepasst
        from .schammessung import Schammessung

        if melden:
            melden(0.0, 'Daz-Scham anpassen (einige Minuten)')
        try:
            bau = Dazgeograftangepasst(name, '%s Scham' % name)
            bilanz = bau.bauen()
            bau.modell_ableiten(name)
            bau.modell_abgleichen(name)
        except Exception as fehler:  # noqa: BLE001 — Zusatzschritt: das Modell behält das Eigen-Stück
            logger.exception('Blender-Import: Daz-Scham für %s gescheitert', name)
            return {'fehler': str(fehler)[:300]}
        abweichungen = [z.strip() for z in Schammessung.zeilen(bilanz['bericht']['messung']) if z.strip().startswith('- ')]
        return {'stueck': bilanz['stueck'], 'modell': name, 'punkte': bilanz['punkte'], 'abweichungen': abweichungen}
