# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkoerperlauf — die Schrittklassen von „Mesh to 3D" auf einem Auftrag „2D3D Kleider" (30.09.2026).

`Meshfigurkette`, `Meshfigurende`, `Meshfigurhaar`, `Meshfigurkleidung`, `Meshfigurvorschau` sprechen nur mit
`lauf.job`, `lauf.ablage`, `lauf.optionen`, `lauf.melden`, `lauf.runner`, `lauf.zusatz`, `lauf.vorlage` —
dieselbe Beobachtung wie bei BlenderModel (`blendermodell.md`). Diese Klasse ERBT von `Meshfigurlauf`
(`auftrag()`, `runner()`, `umgebung()`, `_erkennung`, `_kalibrierung`, `vorlage()` bleiben) und ersetzt nur
den Aufbau: der Auftrag und die Ablage sind die von „2D3D Kleider", der Fortschritt geht in das Band des
Schritts „koerper" des äußeren Laufs.

Nicht ersetzt: `runner()` prüft „angehalten" gegen die Tabelle von „Mesh to 3D" (findet dort nichts) — der
äußere Lauf prüft zwischen den Schritten, und „Anhalten" beendet den Arbeitsprozess samt Runner ohnehin
(`Engine2d3dKleiderarbeiter.anhalten`, `taskkill /T`).

NICHT GELAUFEN (Stand 30.09.2026): Der erste Auftrag übernahm den Körper (`koerper.quelle = uebernehmen`); dieser
Weg ist geschrieben, aber ohne Lauf — rund 15 Minuten Grafikkarte.
"""

from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .meshfigurlauf import Meshfigurlauf
from .meshfiguroptionen import Meshfiguroptionen

__all__ = ['Engine2d3dKleiderkoerperlauf']


class Engine2d3dKleiderkoerperlauf(Meshfigurlauf):
    def __init__(self, aussen, koerperoptionen):        # noqa: D107 — kein `super().__init__`: der lädt Meshfigurauftrag
        self.aussen = aussen
        self.job = aussen.job
        self.ablage = aussen.ablage
        figur = dict(koerperoptionen or {})
        figur['basis'] = (aussen.optionen or {}).get('basis') or figur.get('basis') or 'masculine'
        figur['modell'] = 'aus'
        figur['haarkarten'] = 'aus'                      # die Frisurwahl ja, Haarkarten braucht 2D3D Kleider nicht
        self.optionen = Meshfiguroptionen.pruefen(figur)
        # Die Kleidungsmaske aus der Sapiens-Segmentierung statt aus Farbe und Lage (Option `segmentierung.verwenden`, 04.10.2026);
        # `Meshfigurkleidung._sapiens` liest es — „Mesh to 3D" hat das Attribut nicht und rechnet wie bisher.
        self.sapiens_einstellungen = Engine2d3dKleideroptionen.segmentierung(self.job.optionen)
        self.sapiens_maske = self.sapiens_einstellungen.get('verwenden') == 'an'
        # Die Haarmaske aus der Sapiens-Klasse „Hair" (Option `segmentierung.haar`, 05.10.2026) — `Meshfigurhaar` liest es (`Sapienshaar`); „Mesh to 3D" hat das Attribut nicht.
        self.sapiens_haar = self.sapiens_einstellungen.get('haar') or 'farbe'
        # Das Körper-Tor (Option `koerper.tor`, 04.10.2026): „anhalten" (Vorgabe) stoppt die Kette nach dem Körper, „melden" lässt sie weiterlaufen — `Meshfigurkette.koerper` liest es.
        self.tor = (koerperoptionen or {}).get('tor') or 'anhalten'
        # Option `koerper.naht` (07.10.2026): „aus" lässt die Kappe des Kopfnetzes stehen und näht nicht — `Meshfigurdaten._zielnetz` liest es aus `auftrag.json`.
        self.zusatz = {'naht': ((koerperoptionen or {}).get('naht') or 'an') != 'aus'}
        # Option `koerper.landmarkmorphe` (07.10.2026): Augen-, Mund- und Nasenmorph aus den Landmarken (`Meshfigurlandmarkmorphe`) — `Meshfigurende.rest` ruft `landmarkmorphe`.
        self.landmarkmorphe_an = ((koerperoptionen or {}).get('landmarkmorphe') or 'an') != 'aus'
        self._von, self._bis = 0.0, 1.0
        self._letzte_db = 0.0
        self.Angehalten = aussen.Angehalten

    def landmarkmorphe(self, rest, gewicht, name, stellung):
        """Augen-, Mund- und Nasenmorph aus den Landmarken (`Meshfigurlandmarkmorphe`, im Schritt „rest") — `{}` ohne die Option `koerper.landmarkmorphe`."""
        if not self.landmarkmorphe_an:
            return {}
        from .meshfigurlandmarkmorphe import Meshfigurlandmarkmorphe

        return Meshfigurlandmarkmorphe(self.job, self.ablage).bauen(rest, gewicht, name, stellung)

    def kopfnetz(self):
        """Das Kopfnetz des Schritts „kopf" (Häkchen `kopf.rechnen` an und Netz gerechnet), sonst None — „Mesh to 3D" liest es aus `eingang['kopf']`, das hat dieser Auftrag nicht (07.10.2026)."""
        from .engine2d3dkleiderkopf import Engine2d3dKleiderkopf
        return Engine2d3dKleiderkopf.netz_fuer(self.job, self.ablage)

    def schrittfolge(self):
        from .meshfigurende import Meshfigurende
        from .meshfigurfrisur import Meshfigurfrisur
        from .meshfigurhaar import Meshfigurhaar
        from .meshfigurkette import Meshfigurkette
        from .meshfigurkleidung import Meshfigurkleidung
        from .meshfigurvorschau import Meshfigurvorschau

        return {
            'erkennung': self._erkennung,
            'haar': lambda: Meshfigurhaar(self).ausfuehren(),
            'kleidung': lambda: Meshfigurkleidung(self).ausfuehren(),
            'kalibrierung': self._kalibrierung,
            'koerper': lambda: Meshfigurkette(self).koerper(),
            'gesicht': lambda: Meshfigurkette(self).gesicht(),
            'rest': lambda: Meshfigurende(self).rest(),
            'textur': lambda: Meshfigurende(self).textur(),
            'vorschau': lambda: Meshfigurvorschau(self).ausfuehren(),
            'frisur': lambda: Meshfigurfrisur(self).ausfuehren(),
        }

    def band(self, von, bis, name):
        """Der Anteil des Bands „koerper", in dem dieser Teilschritt läuft."""
        self._von, self._bis = von, bis
        self.aussen.melden(von, 'Körper: %s' % name)

    def melden(self, anteil, text):
        self.aussen.melden(self._von + (self._bis - self._von) * max(0.0, min(1.0, anteil)), 'Körper: %s' % text)

    def sichern(self, *felder):
        self.aussen.sichern(*felder)
