# -*- coding: utf-8 -*-
"""Bildmodelltestfall — das Ergebnis gegen eine bekannte Referenzfigur messen.

Edgar (19.09.2026): „als Testcase erstelle ein neues Projekt: Ursula …
dann versuchst du aus dem Genesis9-Modell das Ursula-Modell zu erstellen.
Dafür oben, wo das 3D-Modell ist, mit dem erzeugten Modell zuschaltbar
(Button „Testcase") das Ursula9-Modell, zum Vergleich."

Ein Testfall ist ein Auftrag mit `optionen.testfall = {figur}` — einem
Bibliothekseintrag des Genesis-9-Katalogs (`G9charaktere`, etwa
`p3d_ursula`). Die Bilder dazu rendert die Seite aus genau dieser Figur
(`testfallbilder.js`), der Lauf kennt die Referenz nicht. Hier, im Schritt
Vorschau, wird gemessen, wie nah das Ergebnis kommt: beide als Genesis-
Käfig (25.182 Punkte, Füße auf 0, `G9reglerableitung.lage`), Abstand je
Punkt → RMS und Maximum in mm, RMS je Körperteil (`G9koerperteile`), Höhe
beider, und die 19 Proportionen (`G9proportionen`) nebeneinander.
Ergebnis in `ergebnis.testfall`; die Seite zeigt die Zahlen und schaltet
die Referenzfigur in der 3D-Ansicht zu.

Die Zahl ist ehrlich nur, wenn die Höhe der Referenz bekannt ist: die
Rechnung skaliert das Ziel auf `person.groesse_cm`, fehlt die Angabe, gilt
die des Schätzers. Darum steht die Referenzhöhe mit im Ergebnis.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Bildmodelltestfall']


class Bildmodelltestfall:
    def __init__(self, job, optionen):
        self.job = job
        self.optionen = optionen or {}

    @staticmethod
    def figur(optionen):
        """Der Name der Referenzfigur — oder None."""
        t = (optionen or {}).get('testfall')
        return t.get('figur') if isinstance(t, dict) and t.get('figur') else None

    def eintrag(self):
        from Genesis9.charaktere import G9charaktere

        name = self.figur(self.optionen)
        return G9charaktere.eintrag(name) if name else None

    # ------------------------------------------------------------ Messen

    @staticmethod
    def kaefig(stellung):
        """`(punkte (N, 3), gelenke {name: kopf})` der Stellung, Füße auf 0."""
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        f = G9formung(dict(stellung))
        p, _, _ = G9reglerableitung.lage(f)
        gelenke = {e['name']: np.asarray(e['kopf'], float) for e in f.skelett().gelenkknochen()}
        return np.asarray(p, float), gelenke

    @staticmethod
    def flaechenabstand(punkte, referenz):
        """Abstand jedes Modellpunkts zur FLÄCHE der Referenz (nächstes Dreieck), Meter.

        Punkt gegen Punkt zählt auch, wo ein Punkt nur auf der Fläche verrutscht ist
        (Ursulas Morph schiebt Punkte entlang der Haut) — nach der Umrissformung stimmte
        die Silhouette auf 5 mm, der Punktabstand blieb bei 11 mm. Die Fläche misst die Form.
        """
        import trimesh
        from Genesis9.kaefigumriss import G9kaefigumriss

        netz = trimesh.Trimesh(np.asarray(referenz, float), G9kaefigumriss.dreiecke(), process=False)
        _, abstand, _ = trimesh.proximity.closest_point(netz, np.asarray(punkte, float))
        return np.asarray(abstand, float)

    @staticmethod
    def je_teil(abstand):
        """RMS in mm je Körperteil (`G9koerperteile.TEILE`)."""
        from Genesis9.haut import G9haut
        from Genesis9.koerperteile import G9koerperteile

        teil = G9koerperteile.genesis_punkte(G9haut.holen())
        aus = {}
        for i, name in enumerate(G9koerperteile.TEILE):
            drin = teil == i
            if drin.any():
                aus[name] = round(float(np.sqrt((abstand[drin] ** 2).mean())) * 1000.0, 2)
        return aus

    def vergleichen(self, stellung, melder=None):
        """`ergebnis.testfall` — None ohne Referenz."""
        from Genesis9.proportionen import G9proportionen

        eintrag = self.eintrag()
        if eintrag is None:
            return None
        if melder:
            melder(0.1, 'Testfall: Referenz %s bauen' % eintrag.get('anzeige', eintrag['name']))
        ref_p, ref_g = self.kaefig(eintrag['regler'])
        mod_p, mod_g = self.kaefig(stellung)
        abstand = np.linalg.norm(mod_p - ref_p, axis=1)
        flaeche = self.flaechenabstand(mod_p, ref_p)
        pr = G9proportionen()
        if melder:
            melder(0.6, 'Testfall: Proportionen beider Figuren')
        aus = {
            'figur': eintrag['name'],
            'anzeige': eintrag.get('anzeige') or eintrag['name'],
            'punkte': int(len(abstand)),
            'rms_mm': round(float(np.sqrt((abstand ** 2).mean())) * 1000.0, 2),
            'max_mm': round(float(abstand.max()) * 1000.0, 1),
            'je_teil': self.je_teil(abstand),
            'flaeche_mm': round(float(np.sqrt((flaeche ** 2).mean())) * 1000.0, 2),
            'flaeche_max_mm': round(float(flaeche.max()) * 1000.0, 1),
            'flaeche_je_teil': self.je_teil(flaeche),
            'hoehe_cm': {
                'referenz': round(float(ref_p[:, 1].max()) * 100.0, 1),
                'modell': round(float(mod_p[:, 1].max()) * 100.0, 1),
            },
            'proportionen': {
                'referenz': G9proportionen.in_cm(pr.messen(ref_p, ref_g)),
                'modell': G9proportionen.in_cm(pr.messen(mod_p, mod_g)),
            },
        }
        logger.info(
            'Bildmodell %s: Testfall %s — RMS %.2f mm, max %.1f, Fläche %.2f mm, Höhe %s',
            self.job.kennung, aus['figur'], aus['rms_mm'], aus['max_mm'], aus['flaeche_mm'], aus['hoehe_cm'],
        )
        return aus
