# -*- coding: utf-8 -*-
"""Hybridhaende: GEM-X als Fingerquelle des Hybridlaufs.

Auftrag Edgar (12.09.2026): „baue beides … dann kann ich einmal mit einmal
ohne diese zusatzoptionen erzeugen". Der Hybrid holt Gesicht und Hände von
MocapNET v4 (MediaPipe-Hände). GEM-X (NVIDIA, SOMA mit 77 Gelenken, davon
38 Finger) liefert Finger aus derselben Modellfamilie wie der GEM-SMPL-Körper;
`retarget-job` setzt sie auf 30 Fingerspuren des Rigs um (gemessen
12.09.2026). Wählt der Auftrag `hands_source: gemx`, fährt der Hybridlauf
GEM-X als DRITTEN Unterlauf — nach dem Körper, nicht gleichzeitig: beide
brauchen die GPU (GEM 3 GB + 5,5 GB Checkpoint, GEM-X 6,7 GB Gewichte), und
zwei Modelle nebeneinander machen beide langsamer, ohne Zeit zu sparen.

Die Zusammenführung (`Handspuren`) legt die Fingerknochen dieser BVH über
Körper und v4-Gesicht; die v4-BVH läuft weiter mit, sie führt das Gesicht.

Eigene Datei, weil `hybridlauf.py` an der Grenze von 300 Zeilen steht.
"""
from .teilauftrag import Teilauftrag


class Hybridhaende:
    """Der Finger-Unterauftrag: was GEM-X dafür braucht, und ob er bestellt ist."""

    QUELLE = 'gemx'
    ORDNER = 'hands'
    ANZEIGE = 'GEM-X'

    def __init__(self, job, params, einstellungen):
        self.job = job
        self.params = params
        self.einstellungen = einstellungen

    @classmethod
    def bestellt(cls, params):
        return (params or {}).get('hands_source') == cls.QUELLE

    def auftrag(self):
        """`None`, wenn die Hände nicht von GEM-X kommen sollen.

        Feste Kamera wie der Körper, Glättung aus der GEM-X-Einstellung
        (4 seit dem 12.09.2026), Gerät wie der Körper.
        """
        if not self.bestellt(self.params):
            return None
        s, p = self.einstellungen, self.params
        werte = {
            'static_cam': p.get('static_cam', s.gemx_static_cam),
            'smooth_sigma': p.get('hands_smooth_sigma', s.gemx_smooth_sigma),
            'device': p.get('body_device', s.smpl_device),
        }
        return Teilauftrag(self.QUELLE, werte, self.job.name,
                           '%s_%s' % (self.job.id, self.ORDNER),
                           anzeige=self.ANZEIGE)
