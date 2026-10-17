# -*- coding: utf-8 -*-
"""Blendimportrequisit — ein Stück, das zu weit vom Körper hängt für die Käfig-Nachbarschaft, geht starr mit dem Teil, das es berührt.

Die vierte Klasse des Konzepts (`Docu/konzepte/2026-10-09_blend-import-kleidung-in-die-ruhelage-konzept.md`, Abschnitt 2): starr an EINEM Teil,
erkennbar am Abstand zum Käfig, nicht am Namen. Anlass (09.10.2026, drittes Modell „Fallout ranger"): die Laserwaffe in der Hand hängt zu 98 %
mehr als 3 h (12 mm) vom Käfig, im Median 77 mm; ihre nächsten Käfigpunkte liegen am Rumpf, nicht an der Hand — die Käfig-Nachbarschaft
(Kabsch über 40 posierte Käfigpunkte, σ 5 cm) stellte sie an den Rumpf zurück: Haltungstreue Median 3,9 mm, p90 35,5, max 90,9 mm
(18 % über 25 mm), in der Ruhe ein Ding vor der Brust statt in der Hand. Der Helm (105 mm im Median) ging bisher über dieselbe Nachbarschaft
am Kopf; Haar und Augen sind starr am Kopf (`Blendimportlage.kopf_starr`), das gilt hier für alles, was so weit abhängt.

    erkennen   mindestens `FREI_ANTEIL` der Punkte weiter als `FREI_H · h` vom Käfig UND Abstand im Median ab `ABSTAND_H · h` →
               das Teil ist das, dem ein Punkt am nächsten kommt: unter den `NAH_ANTEIL` nächsten Punkten das häufigste (die
               Berührung zählt, nicht der Mittelwert). Gemessen: die Waffe des „Fallout ranger" berührt den RUMPF (nicht die Hand, Rundlauf
               6,8 mm); an „Asian Female" und „cute girl" erkennt es nichts, am Helm auch nicht (er liegt am Kopf an, im Käfig nahe genug)
    ruhelage   EINE Starrkörperbewegung (Kabsch ohne Maßstab) über die Käfigpunkte dieses Teils, Haltung → Ruhe
    Bindung    das Stück hängt ganz an dem Knochen, der das Teil führt (`Blendimportteile.KNOCHEN`, wie das Haar an `head`)
"""

import numpy as np
from Genesis9.koerperteile import G9koerperteile

__all__ = ['Blendimportrequisit']


class Blendimportrequisit:
    FREI_H = 3.0
    #: 0,9 → 0,75 (10.10.2026): das Katana von Rosemary Winters (115 cm, Griff dicht vernetzt IN der Hand) hat 19 % seiner Punkte näher als 3 h am Käfig
    #: (frei 0,812, Median 16,0 h) und lief darum als Kleid durch die Käfig-Nachbarschaft — Klinge am Oberschenkel mitgezogen, Kanten 3,1 % gedehnt.
    #: Gemessen an acht Importen (`ProjektTemp/_wegwerf/requisit_kalibrierung.py`): außer dem Katana liegt kein gesundes Stück (Rolle nicht Haar) mit
    #: Median ≥ 8 h unter 0,9 frei; die größten Kleider (Mantel 4,9 h, Rüstung, Seil 5,2 h, Hemd 6,0 h) bleiben weit unter 8 h.
    FREI_ANTEIL = 0.75
    ABSTAND_H = 8.0
    NAH_ANTEIL = 0.02
    #: Mindestzahl Käfigpunkte des Handtellers für die Starrkörperbewegung (sonst alle Punkte des Teils).
    HANDTELLER_MIN = 100

    def __init__(self, lage):
        self.lage = lage

    def erkennen(self, punkte_blender):
        """`{teil, nummer, knochen, abstand_median_mm, frei_anteil}` für ein Requisit, sonst None."""
        from .blendimportteile import Blendimportteile

        lage = self.lage
        netz = lage.ins_netz(punkte_blender)
        d, i = lage.entposen().baum.query(netz, workers=-1)
        h = lage.h
        frei = float((d > self.FREI_H * h).mean())
        if frei < self.FREI_ANTEIL or float(np.median(d)) < self.ABSTAND_H * h:
            return None
        nah = np.argsort(d)[:max(10, int(self.NAH_ANTEIL * len(d)))]
        teile = lage.teil[i[nah]]
        teile = teile[teile >= 0]
        if not len(teile):
            return None
        nummer = int(np.bincount(teile).argmax())
        name = G9koerperteile.TEILE[nummer]
        knochen = Blendimportteile.KNOCHEN.get(name)
        if knochen is None:
            return None
        return {'teil': name, 'nummer': nummer, 'knochen': knochen,
                'abstand_median_mm': round(float(np.median(d)) * 1000.0, 1), 'frei_anteil': round(frei, 3)}

    def anteil_teil(self, punkte_blender, nummer):
        """Anteil (0…1) der Punkte, deren nächster Käfigpunkt zum Körperteil `nummer` gehört — wie weit ein Stück wirklich an EINEM Teil hängt (`erkennen` nimmt nur die 2 % nächsten Punkte: ein langer Bart, dessen
        Kinn am Kopf und dessen Hälfte auf der Brust liegt, galt als „am Kopf" und kippte mit jeder Kopfhaltung von der Brust weg)."""
        lage = self.lage
        _, i = lage.entposen().baum.query(lage.ins_netz(punkte_blender), workers=-1)
        teile = lage.teil[i]
        teile = teile[teile >= 0]
        return float((teile == nummer).mean()) if len(teile) else 0.0

    def ruhelage(self, punkte_blender, nummer):
        """`(Punkte in der Ruhelage, Rundlauf des Teils in mm RMS)` — Starrkörperbewegung des Käfigteils (ohne Maßstab)."""
        lage = self.lage
        teil = lage.teil == nummer
        # Ohne die Punkte, die die Fingerhaltung bewegt (`Blendimportfinger`): Handteller und Handgelenk sind starr, die gebeugten Finger nicht —
        # sie bogen die Starrkörperbewegung der Hand (Käfig der Haltung mit Faust, Ruhe mit gestreckter Hand).
        handteller = teil & ~lage.finger_bewegt
        if handteller.sum() >= self.HANDTELLER_MIN:
            teil = handteller
        r, ma, mb, rms = self._starr(lage.kaefig_posiert[teil], lage.kaefig_ruhe[teil])
        return (lage.ins_netz(punkte_blender) - ma) @ r.T + mb, round(rms, 2)

    @staticmethod
    def _starr(a, b):
        """`(R, Mitte a, Mitte b, Rundlauf mm)` — die Starrkörperbewegung a → b (Kabsch ohne Maßstab): `(x − Mitte a) @ R.T + Mitte b`."""
        ma, mb = a.mean(axis=0), b.mean(axis=0)
        u, _, vt = np.linalg.svd((a - ma).T @ (b - mb))
        s = np.sign(np.linalg.det(vt.T @ u.T)) or 1.0
        r = vt.T @ np.diag([1.0, 1.0, s]) @ u.T
        return r, ma, mb, float(np.sqrt((np.linalg.norm((a - ma) @ r.T + mb - b, axis=1) ** 2).mean())) * 1000.0

    #: Teile, die einen Gegenstand tragen können (Stab, Schwert, Schirm, Flasche): die Hände.
    TRAEGER = ('l_hand', 'r_hand')

    def ruhelage_gehalten(self, punkte_blender, nummer):
        """`(Punkte in der Ruhelage, Verschiebung in mm)` für einen Gegenstand in der HAND (14.10.2026, Edgar: „der Zauberstab geht durch den Körper bei der Animation").

        `ruhelage` dreht den Gegenstand mit der Hand zurück in die Ruhe. Die Hand steht im Foto vorn gehoben (Drehung bis zur Ruhe 130°), in der Ruhe (A-Haltung) hängt sie seitlich: Der Stab des Zauberers, im Foto senkrecht (Achse y 0,997),
        lag in der Ruhelage mit der Achse (0,874; 0,459; −0,158) — 63° zur Senkrechten, nach innen; 4,0 % seiner Punkte (2.267 von 57.081) lagen binnen 2 cm des Rumpf-, Kopf- und Gegenarm-Käfigs (gemessen `stab_ruhe_probe.py`).
        Ein Gegenstand in der Hand hängt aber an der Schwerkraft, nicht am Handgelenk: er behält seine Ausrichtung und wandert nur mit der Hand, die Handmitte bleibt der Drehpunkt (der Abstand zur Hand ist derselbe: 42 mm von der
        Stabachse). **Nicht** nach dem Becken ausgerichtet: die Anpassung kippt das Becken des Zauberers um 32,6° (der Rumpf nur 8,2°), der Stab hinge dann 29° schräg (0 Punkte im Körper, aber eine Schräge, die im Foto nicht steht).
        Ohne genug Handpunkte (`HANDTELLER_MIN`) gilt die Starrkörperbewegung der Hand. Nur für Gegenstände, die der Lauf als Bestandteil (`Meshfigurteile`) in der Hand findet; der Blender-Import behält `ruhelage` (dort schließt die Figur
        beim Tragen die Faust um das Stück, die Fingerwinkel gelten in der Handlage)."""
        lage = self.lage
        hand = lage.teil == nummer
        handteller = hand & ~lage.finger_bewegt
        if handteller.sum() >= self.HANDTELLER_MIN:
            hand = handteller
        if hand.sum() < self.HANDTELLER_MIN:
            return self.ruhelage(punkte_blender, nummer)
        schritt = lage.kaefig_ruhe[hand].mean(axis=0) - lage.kaefig_posiert[hand].mean(axis=0)
        return lage.ins_netz(punkte_blender) + schritt, round(float(np.linalg.norm(schritt)) * 1000.0, 1)
