# -*- coding: utf-8 -*-
"""Begutachtungsautomatik — das Rezept der nächsten automatischen Runde (aus `Begutachtungsrunde._automatisch` herausgelöst, 05.10.2026, als Iteration 0 die Datei über 300 Zeilen brachte).

`IterationModell` (Ordner `2d3DIterationen`) schreibt das Rezept aus dem Befund der letzten Runde, ergänzt um die Prüf-KI, wenn sie fällig ist (`Begutachtungskritik`).
"""

from .begutachtungskritik import Begutachtungskritik
from .begutachtungsstand import Begutachtungsstand

__all__ = ['Begutachtungsautomatik']


class Begutachtungsautomatik:
    def __init__(self, runde):
        self.r = runde

    def rezept(self, modell, z, referenzen):
        """Das Rezept der nächsten Runde aus dem Befund der letzten (`IterationModell`), ergänzt um die Prüf-KI, wenn sie fällig ist → (aufrufe, Zusatz zum Kommentar, fertig)."""
        from Genesis9.rezeptumgebung import Rezeptumgebung
        from iterationen2d3d.iterationmodell import IterationModell
        job, werkzeug = self.r.job, self.r.werkzeug
        kandidaten = [k.get('kennung') for k in (job.ergebnis.get('frisur') or {}).get('kandidaten') or [] if k.get('kennung')]
        befund = dict(Begutachtungsstand.befund_fuer_regeln(z) or {}, haltung_foto=z.get('haltung_foto'))
        # Was nicht vom Render abhängt, gilt schon für Runde 1 (Edgar: „beim nächsten Modell in Runde 1"): Fotostücke,
        # Uhr, Bart — vorher trug Runde 1 Bibliotheksshirt und -shorts (Wiederholungsauftrag 2026.10.01.19.21.30).
        befund['zubehoer'] = werkzeug.zubehoer(referenzen)     # immer frisch: ein gespeicherter Befund kennt neue
        befund['fotostuecke'] = werkzeug.fotostuecke()        # Erkenner nicht (Bart, 01.10.2026 abends)
        befund['haarzonen'] = dict(job.ergebnis.get('haarzonen') or {})      # Fotofarbe je Kopfzone
        if not befund.get('teile'):
            befund['haar_netzfarbe'] = werkzeug.haarfarbe()
        rezept = IterationModell(modell, befund, z.get('verlauf_befunde'), kandidaten, form=self.r.o.get('form') == 'an',
                                 auftrag=Rezeptumgebung.kuerzel(job.kennung)).rezept()
        rezept = Begutachtungsstand.ohne_gesperrte(rezept, z)        # Zeilen, die aus dieser Lage schon verworfen sind
        rezept, zusatz, fertig = Begutachtungskritik(self.r.o, self.r.ablage).ergaenzen(rezept, modell, z)
        if not fertig and not rezept:
            return '', 'Rundenauswahl: aus der besten Runde %s geht keine Änderung mehr' % z.get('runde_bester'), True
        return rezept, zusatz, fertig
