# -*- coding: utf-8 -*-
"""Blendimportlage — Punkte aus der .blend in die Ruhelage der Genesis-Figur, und die Figur selbst als Netz.

Drei Abbildungen, alle aus dem fertigen Auftrag „Mesh to 3D" (`Blendimportfigur`):

    ins_netz   Blender-Achsen → glTF-Achsen (`Blendimportkoerper.gltf`) → Lage der Erkennung (`arbeit/scan_lage.npz`,
               dieselbe Matrix, mit der „Mesh to 3D" das Körpernetz gedreht, gestellt und skaliert hat)
    ruhelage   von dort in die Ruhelage der Figur — `Kleidungsentposen` mit dem Käfig in Ruhe (`genesis_ende.npz`) und in
               der Haltung des Netzes (`posiert.npy`), wie `Meshfigurkleidung.objekt` und `Fotostuecke`
    kopf_starr wie `ruhelage`, aber EINE Starrkörperbewegung (Kabsch) aus den Kopfpunkten des Käfigs — für das Haar, das
               nur am Kopfknochen hängt (alle Punkte, Gewicht 0,77–0,85, gemessen 08.10.2026): die Nachbarschaft von `Kleidungsentposen` zöge lange Strähnen an Schultern
               und Rücken mit (`haar.md`: Haar folgt dem Kopf)

Dazu `genesis`: die fertige Figur (Regler samt Eigenmorph, `G9formung`) auf Stufe 1 — Punkte in Ruhe (Meter, Y oben,
Füße 0), Dreiecke, UV mit der UDIM-Kachel der Gruppe im ganzzahligen Teil (Genesis führt UV je Gruppe in 0..1 und die
Kachel an der Gruppe: Head/Mouth Cavity 1001, Body 1002, Legs 1003, Arms 1004, Nägel 1005 — gelesen 08.10.2026).
"""

import logging

import numpy as np

from .blendimportkoerper import Blendimportkoerper

logger = logging.getLogger('core')

__all__ = ['Blendimportlage']


class Blendimportlage:
    STUFE = 1
    #: Kacheln, die NICHT gebacken werden: 1005 (Finger- und Zehennägel). Gemessen am ersten Import (2026.10.08.11.28.06):
    #: nur 30,4 % der Kachel getroffen bei 52,4 % Inselfläche, die Normalen im Median 32° gekippt — die Nägel des Originals
    #: liegen nicht auf denen der Figur. Ohne Fototextur für 1005 gelten die Genesis-Nägel und der Nagellack-Preset färbt sie
    #: (Edgar, 08.10.2026: „Nägel färben sich nicht, wenn ich die über Genesis setze").
    NICHT_GEBACKEN = (1005,)

    def __init__(self, job, zusatz=None, finger=True):
        """`finger`: den Käfig der Haltung mit der Fingerhaltung des Originals rechnen (`Blendimportfinger`, wenn der Auftrag sie führt) — nur
        der Schritt „finger" selbst fragt ohne sie (er beginnt bei der gestreckten Hand)."""
        from ..daten.meshfigurablage import Meshfigurablage
        from .blendimportfinger import Blendimportfinger

        self.job = job
        #: Weitere Regler der Stellung (die Nachformung der Scham, `Blendimportnachformung.zusatzregler`) — `{eigen:…: 1.0}`.
        self.zusatz = dict(zusatz or {})
        self.ablage = Meshfigurablage(job.kennung)
        with np.load(self.ablage.arbeit('scan_lage.npz')) as d:
            self.matrix = np.asarray(d['matrix'], dtype=np.float64)
        with np.load(self.ablage.arbeit('genesis_ende.npz')) as d:
            self.kaefig_ruhe = np.asarray(d['punkte'], dtype=np.float64)
            self.teil = np.asarray(d['teil'])
        self.kaefig_posiert = np.load(self.ablage.arbeit('posiert.npy')).astype(np.float64)
        #: Fingerhaltung der Hände im Original (10.10.2026): die Käfigpunkte, die sie bewegt (mehr als 1 mm), und ihre Winkel `{knochen: {kanal: Grad}}`.
        #: Die Ruhelage bleibt die gestreckte Hand; `kaefig_posiert` trägt die Finger, wie das Original sie hält — das Entposen führt sie zurück.
        self.finger_bewegt = np.zeros(len(self.kaefig_posiert), dtype=bool)
        self.finger_drehung = {}
        korrektur = Blendimportfinger.kaefig(self.ablage) if finger else None
        if korrektur is not None and len(self.kaefig_posiert) > int(korrektur[0].max(initial=-1)):
            idx, delta = korrektur
            self.kaefig_posiert[idx] += delta
            self.finger_bewegt[idx] = np.linalg.norm(delta, axis=1) > 0.001
            self.finger_drehung = Blendimportfinger.haltung(self.ablage)
        self._entposen = None
        self._kaefig_normalen = None
        self._h = None

    def stellung(self):
        """Die Regler der Figur: die der Anpassung samt Eigenmorph plus die Zusatzregler der Nachformung."""
        return {**(self.job.stellung() or {}), **self.zusatz}

    def ins_netz(self, punkte_blender):
        p = Blendimportkoerper.gltf(punkte_blender)
        return p @ self.matrix[:3, :3].T + self.matrix[:3, 3]

    def entposen(self):
        from Genesis9.koerperteile import G9koerperteile
        from Kleidung.kleidungsentposen import Kleidungsentposen

        if self._entposen is None:
            self._entposen = Kleidungsentposen(self.kaefig_ruhe, self.kaefig_posiert, self.teil, G9koerperteile.nachbarn())
        return self._entposen

    def ruhelage(self, punkte_blender):
        """Ohne Teile — jeder Punkt sieht die nächsten Käfigpunkte, gleich welchen Teils (`koerper_ruhelage` und
        `stueck_ruhelage` trennen die Teile; hier bleibt, wie es war)."""
        return self.entposen().ruhelage(self.ins_netz(punkte_blender))

    #: LÄNGEN IN EINHEITEN DES KÄFIGS (`h`, Median des Punktabstands des posierten Käfigs: 4,0 mm bei 1,66 m, 4,3 mm bei 1,75 m, gemessen
    #: 09.10.2026) statt in Millimetern: ein anderer Käfig oder eine andere Körpergröße verschiebt alle Schwellen mit. Die Faktoren
    #: sind die an „Asian Female" (h = 4,0 mm) abgestimmten Millimeterwerte, geteilt durch `h` — dort ändert sich nichts.
    #:
    #: Gewicht, mit dem ein Stoffpunkt sein eigenes Teil behält: `exp(−(Abstand / (HAFT_H · h))²)` — nah an der Haut stark (1), bei
    #: 2,5 h 0,64, bei 5 h 0,17, bei 7,5 h 0,02; frei hängender Stoff übernimmt das Teil seiner Nachbarn auf dem Stoff. (Bis 09.10.2026
    #: `exp(−Abstand / 1 cm)`: die Strapse, 7–13 mm von der Haut des Oberschenkels, wurden mit 60 Runden vom Teil ihres oberen
    #: Endes überstimmt und hingen am „rumpf", obwohl jeder ihrer Punkte den Oberschenkel als nächsten Käfigpunkt hatte.)
    HAFT_H = 3.75
    GLAETTEN_STOFF = 60
    GLAETTEN_KOERPER = 3
    #: Zusammenhängende Flecken mit einem Teil übernehmen das Teil ihrer Nachbarn (`teile_inseln`), wenn sie kleiner sind als
    #: `INSEL_E2` Punkte — in Einheiten der Stückkante `e` (Median der Kantenlängen: 0,5 mm beim BH, 11 mm beim Pullover, 13 mm bei einer
    #: Socke; 150 Punkte sind 0,3 cm² beim BH und 230 cm² bei der Socke), und die Fläche daraus bleibt zwischen den Grenzen in `h²`
    #: (25 h² ≈ 4 cm², 940 h² ≈ 150 cm² bei h = 4 mm): ein Fleck, der kleiner als eine Handfläche ist, ist keine eigene Zuteilung.
    INSEL_E2 = 150
    INSEL_FLAECHE_H2 = (25.0, 940.0)
    #: … aber nur, wenn sie im Mittel mindestens so weit vom Käfig hängen (Kleider; Pullover-Saum 17 mm = 4,3 h, Strapse 8 mm = 2 h).
    INSEL_AB_H = 3.0

    @property
    def h(self):
        """Der Punktabstand des posierten Käfigs (m): Median des Abstands zum nächsten Nachbarn."""
        if self._h is None:
            from scipy.spatial import cKDTree

            self._h = float(np.median(cKDTree(self.kaefig_posiert).query(self.kaefig_posiert, k=2)[0][:, 1]))
        return self._h

    def insel_punkte(self, netz, dreiecke):
        """Inselgrenze (Punkte) für ein Netz in Lage des Käfigs — siehe `INSEL_E2`."""
        d = np.asarray(dreiecke, dtype=np.int64)
        kante = float(np.median(np.linalg.norm(netz[d[:, 0]] - netz[d[:, 1]], axis=1)))
        je_punkt = 0.87 * max(kante, 1e-6) ** 2                      # Fläche je Punkt eines Dreiecksnetzes (2 Dreiecke, ½ · e² · sin 60°)
        flaeche = min(max(self.INSEL_E2 * je_punkt, self.INSEL_FLAECHE_H2[0] * self.h ** 2), self.INSEL_FLAECHE_H2[1] * self.h ** 2)
        return max(3, int(round(flaeche / je_punkt)))

    def kaefig_normalen(self):
        """Punktnormalen des posierten Käfigs (am ungeteilten Genesis-Netz)."""
        if self._kaefig_normalen is None:
            from Genesis9.basisnetz import G9basisnetz

            self._kaefig_normalen = G9basisnetz.holen().normalen(self.kaefig_posiert)
        return self._kaefig_normalen

    @staticmethod
    def netz_normalen(punkte, dreiecke):
        """Punktnormalen eines Dreiecksnetzes, nach Fläche gewichtet."""
        d = np.asarray(dreiecke, dtype=np.int64)
        n = np.cross(punkte[d[:, 1]] - punkte[d[:, 0]], punkte[d[:, 2]] - punkte[d[:, 0]])
        aus = np.zeros_like(punkte)
        for ecke in range(3):
            np.add.at(aus, d[:, ecke], n)
        laenge = np.linalg.norm(aus, axis=1, keepdims=True)
        laenge[laenge < 1e-12] = 1.0
        return aus / laenge

    def koerper_ruhelage(self, punkte_blender, dreiecke, mit_teilen=False):
        """Der Körper der .blend in der Ruhelage — jeder Punkt nur mit den Käfigpunkten SEINES Teils und der angrenzenden
        (`Kleidungsentposen.teile_von`, mit Normale: die Hand auf der Hüfte trägt die Hüfte nicht). `mit_teilen`: dazu
        die Teilnummer je Punkt."""
        ent = self.entposen()
        netz = self.ins_netz(punkte_blender)
        normalen = self.netz_normalen(netz, dreiecke)
        kaefig = self.kaefig_normalen()
        _, nah = ent.baum.query(netz)
        if float(np.einsum('ij,ij->i', normalen, kaefig[nah]).mean()) < 0.0:      # Umlauf des Exports gegen den des Käfigs
            normalen = -normalen
        teile = ent.teile_von(netz, None, normalen, kaefig)
        teile = ent.teile_inseln(teile, dreiecke, self.insel_punkte(netz, dreiecke))
        teile = ent.teile_glaetten(teile, dreiecke, 0.6, runden=self.GLAETTEN_KOERPER)
        ruhe = ent.ruhelage(netz, teile)
        return (ruhe, teile) if mit_teilen else ruhe

    def entposen_zu(self, ruhe_kaefig):
        """Dieselbe Rückrechnung gegen einen anderen Käfig in Ruhe (Füße in Absatzhaltung, `Blendimportfuss.ruhe_kaefig`)."""
        from Genesis9.koerperteile import G9koerperteile
        from Kleidung.kleidungsentposen import Kleidungsentposen

        return Kleidungsentposen(ruhe_kaefig, self.kaefig_posiert, self.teil, G9koerperteile.nachbarn())

    #: Entzerren (`Kleidungsentposen.entzerren`): Anker an die Käfiglage (200, Reichweite 2,5 h = 10 mm), Punkte, die in der Haltung höchstens
    #: 1 h = 4 mm auseinander liegen, bleiben gekoppelt. Gemessen an Pullover, Höschen mit Strapsen, Shorts, Stiefeln, Socken (Anteil der
    #: Kanten außerhalb 0,75–1,33, vorher → nachher): 6,49 → 6,02, 2,43 → 0,66, 1,98 → 0,02, 4,42 → 1,37, 2,47 → 2,13 % — keines schlechter.
    #: Die Kopplung war an die Käfigeinheit gebunden, nicht an die Stückkante: beim BH (Kante 0,5 mm = 8 e) koppelte sie ganze Nachbarschaften (rund 230
    #: Punkte je Punkt), bei noch dichteren Netzen wüchse der Speicher mit dem Quadrat der Dichte. Jetzt höchstens `KOPPELN_E` Stückkanten `e`: gemessen
    #: 09.10.2026 an allen Stücken dreier Modelle (`ProjektTemp/_wegwerf/offene_punkte_probe.py koppeln`) ändert sich nur der BH (1,3 → 0,6 s, Abstand
    #: Median 0,10 / p99 0,31 / max 0,8 mm, Kantenverzerrung 0,05 → 0,06 %, größte Streckung 1,43 → 1,58×) — alle anderen (e ≥ 1,3 mm) bitgleich.
    ANKER = 200.0
    ANKER_H = 2.5
    KOPPELN_H = 1.0
    KOPPELN_E = 3.0

    #: Befund des letzten `stueck_ruhelage`: `{h_mm, kante_mm, insel_punkte, abstand_median_mm, frei_anteil, frei_median_mm}` — der Anteil
    #: Punkte, die weiter als `INSEL_AB_H · h` vom Käfig hängen (frei hängender Stoff: dort taugt die Käfigbewegung nicht, siehe Konzept).
    befund = None

    def stueck_ruhelage(self, punkte_blender, dreiecke, erlaubt, mit_teilen=False, ruhe_kaefig=None, entzerren=True):
        """Ein Kleidungsstück in der Ruhelage: seine Punkte suchen ihr Teil nur unter `erlaubt` (`Blendimportteile`) und
        nur unter Käfigpunkten, deren Normale zur des Stoffs passt (der Unterarm, der auf der Hüfte liegt, trägt den
        Saum nicht); frei hängender Stoff übernimmt das Teil von seinen Nachbarn auf dem Stoff, danach die Rückrechnung
        mit den Teilen und `Kleidungsentposen.entzerren` (frei hängender Stoff behält die Kantenlängen des Originals: Strapse,
        der Schritt zwischen gekreuzten Beinen). `ruhe_kaefig`: der Käfig, in den zurückgerechnet wird (Vorgabe: die Ruhe der Figur)."""
        ent = self.entposen() if ruhe_kaefig is None else self.entposen_zu(ruhe_kaefig)
        netz = self.ins_netz(punkte_blender)
        normalen = self.netz_normalen(netz, dreiecke)
        kaefig = self.kaefig_normalen()
        _, nah = ent.baum.query(netz)
        if float(np.einsum('ij,ij->i', normalen, kaefig[nah]).mean()) < 0.0:      # Umlauf des Exports gegen den des Käfigs
            normalen = -normalen
        h = self.h
        d = np.asarray(dreiecke, dtype=np.int64)
        kante = float(np.median(np.linalg.norm(netz[d[:, 0]] - netz[d[:, 1]], axis=1)))
        teile, abstand = ent.teile_von(netz, erlaubt, normalen, kaefig, abstand=True)
        insel = self.insel_punkte(netz, dreiecke)
        teile = ent.teile_inseln(teile, dreiecke, insel, abstand=abstand, ab=self.INSEL_AB_H * h)
        haft = np.exp(-(abstand / (self.HAFT_H * h)) ** 2)
        teile = ent.teile_glaetten(teile, dreiecke, haft, runden=self.GLAETTEN_STOFF)
        ruhe = ent.ruhelage(netz, teile)
        if entzerren:
            ruhe = ent.entzerren(ruhe, netz, dreiecke, abstand, min(self.KOPPELN_H * h, self.KOPPELN_E * kante), self.ANKER, self.ANKER_H * h)
        frei = abstand > self.INSEL_AB_H * h
        self.befund = {'h_mm': round(h * 1000.0, 2), 'kante_mm': round(kante * 1000.0, 2), 'insel_punkte': insel, 'abstand_median_mm': round(float(np.median(abstand)) * 1000.0, 1),
                       'frei_anteil': round(float(frei.mean()), 3),
                       'frei_median_mm': round(float(np.median(abstand[frei])) * 1000.0, 1) if frei.any() else None}
        return (ruhe, teile) if mit_teilen else ruhe

    def kopf_starr(self, punkte_blender):
        """Haar: Kabsch (ohne Maßstab) über die Kopfpunkte des Käfigs, Haltung → Ruhe."""
        from Genesis9.koerperteile import G9koerperteile

        kopf = self.teil == G9koerperteile.NUMMER['kopf']
        a, b = self.kaefig_posiert[kopf], self.kaefig_ruhe[kopf]
        ma, mb = a.mean(axis=0), b.mean(axis=0)
        u, _, vt = np.linalg.svd((a - ma).T @ (b - mb))
        d = np.sign(np.linalg.det(vt.T @ u.T)) or 1.0
        r = vt.T @ np.diag([1.0, 1.0, d]) @ u.T
        rest = np.linalg.norm((a - ma) @ r.T + mb - b, axis=1) * 1000.0
        self.kopf_befund = {'punkte': int(kopf.sum()), 'rest_rms_mm': round(float(np.sqrt((rest ** 2).mean())), 2)}
        return (self.ins_netz(punkte_blender) - ma) @ r.T + mb

    # ----------------------------------------------------------------- Figur

    def genesis(self):
        """`{punkte, dreiecke, uv, kachel_je_dreieck}` — die fertige Figur auf Stufe 1 in Ruhe."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        kaefig, _, _ = G9reglerableitung.lage(G9formung(self.stellung()))
        stufe = G9basisnetz.holen().netzstufe(self.STUFE)
        punkte = np.asarray(stufe.punkte(np.asarray(kaefig, dtype=np.float64)), dtype=np.float64)
        dreiecke = np.asarray(stufe.dreiecke, dtype=np.int64).reshape(-1, 3)
        kachel = np.zeros(len(dreiecke), dtype=np.int64)
        for g in stufe.gruppen:
            ab = int(g['index_ab']) // 3
            kachel[ab:ab + int(g['dreiecke'])] = int(g['kachel'])
        uv = np.asarray(stufe.uv, dtype=np.float64)
        return {'punkte': punkte, 'dreiecke': dreiecke, 'uv': uv, 'kachel': kachel,
                'gruppen': [(g['name'], int(g['kachel'])) for g in stufe.gruppen]}

    def genesis_objs(self, ordner):
        """Je Kachel ein OBJ der Figur (`genesis_<kachel>.obj`) in BLENDER-Achsen (Z oben), UV wie Genesis (0..1) —
        `blendbacken.py` backt jede Kachel in ein eigenes Bild (außer `NICHT_GEBACKEN`). Gibt `{kachel: Datei}`."""
        g = self.genesis()
        blender = self.blender(g['punkte'])
        aus = {}
        for kachel in sorted({int(k) for k in g['kachel']} - set(self.NICHT_GEBACKEN)):
            dreiecke = g['dreiecke'][g['kachel'] == kachel]
            genutzt, neu = np.unique(dreiecke.reshape(-1), return_inverse=True)
            uv = g['uv'][dreiecke.reshape(-1)]
            zeilen = ['o Genesis_%d' % kachel] + ['v %.6f %.6f %.6f' % tuple(v) for v in blender[genutzt]]
            zeilen += ['vt %.6f %.6f' % tuple(t) for t in uv]
            zeilen += ['f %d/%d %d/%d %d/%d' % (a + 1, 3 * i + 1, b + 1, 3 * i + 2, c + 1, 3 * i + 3)
                       for i, (a, b, c) in enumerate(neu.reshape(-1, 3))]
            pfad = ordner / ('genesis_%d.obj' % kachel)
            pfad.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
            aus[kachel] = str(pfad)
        return aus

    @staticmethod
    def blender(punkte_ruhe):
        """Ruhelage (Y oben) → Blender-Achsen (Z oben): die Umkehr von `Blendimportkoerper.gltf`."""
        p = np.asarray(punkte_ruhe, dtype=np.float64)
        return np.column_stack([p[:, 0], -p[:, 2], p[:, 1]])
