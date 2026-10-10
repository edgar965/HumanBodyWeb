# -*- coding: utf-8 -*-
"""Blendimportfuss — die Absatzhaltung der Füße aus der .blend, als Haltung der Figur beim Tragen der Schuhe.

Warum (09.10.2026, „Asian girl", Edgar: „schuhe pose"): Das Modell steht auf Absätzen — die Füße stehen in der Haltung des Netzes
47° und 65° unter der Waagrechten (Längsachse des Körperfußes, gemessen an den Körperpunkten, die zum Fuß gehören), die Schuhe
sitzen auf diesem Fuß. Rechnet man Körper und Schuhe in die Ruhelage zurück, wird der Fuß flach (Genesis' Ruhe) und der Schuh
mit ihm — der Absatz hängt unter dem Boden (tiefste Punkte −5,8 cm, Schuhachse −34° statt der des Fußes). Daz löst das bei den
Genesis-8-Schuhen so: Der Schuh steht in der Ruhelage schon in der Haltung, die er am Fuß hat, und die Figur stellt ihren Fuß
dazu (`!FootPose`, `G9autofit.figurpose`). Hier ebenso:

    Haltung    Der Fuß dreht sich gegen den Unterschenkel um `Q = R_unterschenkelᵀ · R_fuß` (Drehungen Ruhe → Haltung des Netzes aus
               je einer Starrkörperanpassung der Käfigpunkte; die des Fußes nachgezogen auf die Körperpunkte, ICP, damit sie dem
               Fuß der .blend folgt und nicht dem Käfig, den „Mesh to 3D" nur grob gestellt hat)
    Sohle      (Edgar, 09.10.2026: „der Stiefel soll flach am Boden sitzen") Das Original steht auf Zehenspitzen: gemessen im Browser
               stand die Sohle des Stiefels 28–31° geneigt (Ferse 9 cm in der Luft, Spitze am Boden), der Fuß 55° gegen den Unterschenkel.
               Mit den Schuhpunkten wird `Q` deshalb um die Neigung zurückgedreht, bei der Absatz und Ballen gleich tief stehen
               (`waagrecht`, aus der Form des Schuhs: `Blendimportsohle`): der Fuß steht im Schuh so, wie der Schuh es verlangt (Keilwinkel Fuß/Sohle),
               und der Schuh flach auf dem Boden. Eine Sohle, die schon flach steht (unter `SOHLE_TOLERANZ`), ändert nichts.
               Der Käfig-Kabsch stellt die Sohle nicht ganz wie die starre Rechnung (Ferse und Knöchel mischen die Drehung des Unterschenkels
               ein: Edgar sah „immer noch nicht horizontal", links stand die Ferse 2 cm tiefer als der Ballen) — `stueck_ruhelage` misst die
               Sohle am Ergebnis und stellt `Q` nach (`nachstellen`, höchstens drei Runden, unter 1° bleibt es).
    Käfig      `ruhe_kaefig()`: der Käfig der Figur mit `griff()` (Füße um `Q` gedreht, gehäutet wie beim Tragen) — das Ziel, in das die
               Schuhe zurückgerechnet werden (`Blendimportlage.stueck_ruhelage(ruhe=…)`)
    Griff      `griff()`: dieselbe Drehung als Knochendrehung `l_foot`/`r_foot` (Daz' Achsen, Reihenfolge des Knochens) — das Stück
               schreibt sie neben die `.duf` (`G9stueckersatz`), die Figur stellt beim Tragen ihre Füße

    Ohne Fuß  (09.10.2026, drittes Modell „Fallout ranger": flache Stiefel an einem Körper, der bei den Knöcheln endet — 333 Körperpunkte im Fußteil gegen 2.166
               Käfigpunkte, ICP-Rest 1,9 h; der Körper endet 127 mm über der Sohle, bei Asian Female 9 mm) ist der Fußwinkel aus dem Körper kein Fuß im Schuh (57°,
               Fußknochen im Browser 75° unter der Waagrechten). `FUSS_DECKUNG_MIN`/`FUSS_REST_H_MAX` erkennen es; der Bericht des Schuhs sagt es (`hinweise`).
               NICHT behoben, am Browser gemessen: ein flacher Fuß (Q = 1, der Käfig in der Haltung mit nach dem Schuh gestellten Füßen neu gebaut) legte die Sohle 141 mm
               statt 41 mm unter die Haut — die Figur wurde an einem Körper ohne Füße angepasst, ihre Beine sind um das fehlende Stück zu kurz, und der erfundene Fuß
               gleicht es teilweise aus (der Käfig reicht 80 mm unter das Körperende; Vermutung, nicht weiter geprüft). Die Abhilfe gehört in die Anpassung (Körper ohne Füße).
    Ganz ohne Fuß (10.10.2026, Rainy: der Körper endet bei 0,911 m, kein einziger Körperpunkt im Fußteil; Beine und Füße kommen aus Hose und Stiefel,
               `Blendimportkoerperergaenzung`): bis dahin gab es keine Seite, keinen Griff, keine waagrechte Sohle — im Browser stand der Stiefel mit dem tiefsten
               Punkt 62 mm unter dem Boden, Sohle Ferse → Spitze −62 … +7 mm. Jetzt kommt die Seite mit Schuhen aus dem Käfig der Figur (Ruhe → Haltung, kein
               Nachzug an Körperpunkten), die Sohle stellt `waagrecht`: Fuß 21,9° / 22,7°, im Browser (`boot_browser_nachbau.py`) tiefster Punkt −13 / −16 mm, Sohle
               −12 … −13 mm (Ballenwölbung −2). Der Rest (13–16 mm unter der Haut-Unterkante) ist die Bodenregel des Viewers, die Schuhe nicht kennt.

Strümpfe bleiben flach: Sie folgen der Figur über ihre Haut und drehen mit dem Fuß mit, wenn die Schuhe die Haltung setzen.
"""

import logging

import numpy as np

from .blendimportsohle import Blendimportsohle

logger = logging.getLogger('core')

__all__ = ['Blendimportfuss']


class Blendimportfuss:
    #: (Seite, Teil Fuß, Teil Unterschenkel, Knochen).
    SEITEN = (('l', 'l_fuss', 'l_unterschenkel', 'l_foot'), ('r', 'r_fuss', 'r_unterschenkel', 'r_foot'))
    ICP_RUNDEN = 12
    #: Anteil der Käfigpunkte mit dem kleinsten Abstand, der die Anpassung bestimmt (der Rest sind Zehen und Ränder ohne Gegenstück).
    ICP_ANTEIL = 0.9
    #: Eine kleinere Drehung gegen den Unterschenkel (Grad) braucht weder Griff noch gedrehten Käfig.
    MINDEST_GRAD = 4.0

    #: Die Punkte eines Schuhs zählen für den Fuß, wenn sie höchstens so weit (in Käfigeinheiten `h`) von dessen Käfigpunkten liegen (Absatz bis
    #: ~10 cm unter der Haut: 37,5 h = 15 cm bei h = 4 mm).
    SCHUH_REICHWEITE_H = 37.5
    #: Mindestens so viele Punkte je Fuß, damit die Sohle gemessen wird (zufällige 10 % eines Stiefels — 800 bis 1.200 Punkte — trafen die Neigung auf ±1°,
    #: 2 % — 185 bis 280 — nur auf ±2 bis 9°, gemessen 09.10.2026 an Asian Female und Fallout ranger).
    SCHUH_MINDEST = 200
    #: Dicke des Streifens über der Sohle, in dem Punkte „auf ihr stehen" (`Blendimportsohle`): 1 h. Größer zieht eine nach oben gebogene Spitze mit
    #: (Fallout: 1 h −0,9°, 2 h +2,1°, 4 h +4,5° an einer flachen Sohle).
    SOHLE_BAND_H = 1.0
    #: Eine Sohle gilt als waagrecht, wenn die Nachstellung unter diesem Winkel (Grad) bleibt; höchstens so viele Nachstellungen je Schuh.
    SOHLE_TOLERANZ = 1.0
    NACHSTELL_RUNDEN = 3
    #: Der Körperfuß der .blend taugt als Fußwinkel nur, wenn der Körper den Fuß trägt: Körperpunkte im Fußteil je Käfigpunkt des Fußes mindestens so viele
    #: UND der ICP-Rest höchstens so viele `h`. Gemessen 09.10.2026: cute girl 1,81 / 0,6 h, Asian Female 1,46 / 0,9 h, Fallout ranger (Körper ohne Füße) 0,15 / 1,9 h.
    FUSS_DECKUNG_MIN = 0.5
    FUSS_REST_H_MAX = 1.4

    def __init__(self, lage, koerper_netz, koerper_teile, schuh_netz=None):
        """`koerper_netz` (M, 3): die Körperpunkte in der Haltung des Netzes (`Blendimportlage.ins_netz`); `koerper_teile` (M,):
        ihr Körperteil (`Blendimportlage.koerper_ruhelage(mit_teilen=True)`); `schuh_netz` (S, 3): die Punkte der Schuhe in derselben
        Lage — mit ihnen steht die Sohle waagrecht (`waagrecht`), ohne gilt die Drehung des Körperfußes."""
        from Genesis9.koerperteile import G9koerperteile

        self.lage = lage
        self.netz = np.asarray(koerper_netz, dtype=np.float64)
        self.teile = np.asarray(koerper_teile)
        self.schuhe = None if schuh_netz is None else np.asarray(schuh_netz, dtype=np.float64)
        self.nummer = G9koerperteile.NUMMER
        self._seiten = None

    @staticmethod
    def kabsch(a, b):
        """`(R, ma, mb)` mit `b ≈ R·(a − ma) + mb` (Starrkörper ohne Maßstab, Spiegelung ausgeschlossen)."""
        ma, mb = a.mean(axis=0), b.mean(axis=0)
        u, _, vt = np.linalg.svd((a - ma).T @ (b - mb))
        d = np.sign(np.linalg.det(vt.T @ u.T)) or 1.0
        return vt.T @ np.diag([1.0, 1.0, d]) @ u.T, ma, mb

    def _fuss(self, rest, kaefig_posiert, koerper):
        """Drehung Ruhe → Haltung des Fußes, auf die Körperpunkte nachgezogen; `(R, rest_vorher_mm, rest_nachher_mm)`."""
        from scipy.spatial import cKDTree

        r, ma, mb = self.kabsch(rest, kaefig_posiert)
        baum = cKDTree(koerper)
        vorher = None
        for _ in range(self.ICP_RUNDEN):
            d, i = baum.query((rest - ma) @ r.T + mb)
            if vorher is None:
                vorher = float(np.sqrt((d ** 2).mean())) * 1000.0
            behalten = d <= np.quantile(d, self.ICP_ANTEIL)
            r, ma, mb = self.kabsch(rest[behalten], koerper[i[behalten]])
        d, _ = baum.query((rest - ma) @ r.T + mb)
        return r, vorher, float(np.sqrt((d[d <= np.quantile(d, self.ICP_ANTEIL)] ** 2).mean())) * 1000.0

    def waagrecht(self, schuh):
        """Um wie viel (Grad, + = Spitze nach unten) der Fuß samt Schuh gegen den Unterschenkel gedreht wird, damit die Sohle waagrecht steht — 0, wenn der
        Schuh keine Sohle hat. `schuh` (S, 3): die Schuhpunkte des Fußes mit senkrechtem Unterschenkel (Netzlage mal `R_unterschenkel`, Zeilenform).
        Die Sohle liest `Blendimportsohle` aus der Form des Schuhs, nicht aus der Fußachse des Körpers (die erste Fassung teilte die Schuhlänge entlang
        dieser Achse: beim Fallout ranger, dessen Körper keine Füße hat, zerstörte sie die flache Sohle)."""
        w = Blendimportsohle.neigung(schuh, self.SOHLE_BAND_H * self.lage.h)
        return 0.0 if w is None else w

    @staticmethod
    def _dreh_x(grad):
        """Drehung um die Querachse, Spitze nach unten positiv."""
        c, s = np.cos(np.radians(grad)), np.sin(np.radians(grad))
        return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])

    def _zuordnung(self, punkte, fuesse):
        """`{seite: Maske}` — welche Schuhpunkte zu dem Fuß gehören, dem sie am nächsten liegen (höchstens `SCHUH_REICHWEITE`)."""
        from scipy.spatial import cKDTree

        abstand = np.stack([cKDTree(f['punkte']).query(punkte)[0] for f in fuesse])
        nah, eigen = abstand.min(axis=0) <= self.SCHUH_REICHWEITE_H * self.lage.h, abstand.argmin(axis=0)
        return {f['seite']: nah & (eigen == i) for i, f in enumerate(fuesse)}

    def _schuh_je_fuss(self, fuesse):
        """`{seite: (S_i, 3)}` — die Schuhpunkte je Fuß (`_zuordnung`)."""
        if self.schuhe is None or not fuesse:
            return {}
        return {seite: self.schuhe[maske] for seite, maske in self._zuordnung(self.schuhe, fuesse).items()}

    def _drehen(self, s, grad):
        """Den Fuß `s` um `grad` weiter drehen (Spitze unten +) — `q`, `winkel` und die Summe der Zusatzdrehung fortschreiben."""
        s['q'] = self._dreh_x(grad) @ s['q']
        s['winkel'] = float(np.degrees(np.arccos(np.clip((np.trace(s['q']) - 1.0) / 2.0, -1.0, 1.0))))
        s['waagrecht_grad'] = round(s['waagrecht_grad'] + grad, 1)

    def nachstellen(self, schuh_netz, schuh_ruhe):
        """Misst die Sohle des Schuhs, wie sie nach dem Käfig-Kabsch in der Ruhelage steht (`schuh_ruhe`, Punkt für Punkt zu `schuh_netz`), und
        dreht `Q` um den Rest nach — True, wenn ein Fuß nachgestellt wurde. Die starre Vorhersage (`waagrecht` auf den Netzpunkten) trifft die
        Sohle nicht ganz: an Ferse und Knöchel mischt der Käfig-Kabsch die Drehung des Unterschenkels ein (gemessen am Stiefel, 09.10.2026:
        links Ferse 2 cm tiefer als der Ballen = 6°, rechts 2°). Unter `SOHLE_TOLERANZ` Grad bleibt es."""
        aus = self.seiten()
        masken = self._zuordnung(np.asarray(schuh_netz, dtype=np.float64), aus) if aus else {}
        ruhe = np.asarray(schuh_ruhe, dtype=np.float64)
        geaendert = False
        for s in aus:
            if s['seite'] not in masken or masken[s['seite']].sum() < self.SCHUH_MINDEST:
                continue
            rest = self.waagrecht(ruhe[masken[s['seite']]])
            if abs(rest) >= self.SOHLE_TOLERANZ:
                self._drehen(s, rest)
                geaendert = True
        return geaendert

    def stueck_ruhelage(self, punkte, dreiecke, erlaubt):
        """Die Ruhelage eines Schuhs im Käfig mit den Füßen in Absatzhaltung — mit höchstens `NACHSTELL_RUNDEN` Nachstellungen der Sohle.
        `punkte`: die Schuhpunkte wie aus dem Export (Blender-Lage)."""
        ruhe = self.lage.stueck_ruhelage(punkte, dreiecke, erlaubt, ruhe_kaefig=self.ruhe_kaefig())
        netz = self.lage.ins_netz(punkte)                       # `punkte` liegen in der Blender-Lage, der Käfig in der Haltung des Netzes
        for _ in range(self.NACHSTELL_RUNDEN):
            if not self.nachstellen(netz, ruhe):
                break
            ruhe = self.lage.stueck_ruhelage(punkte, dreiecke, erlaubt, ruhe_kaefig=self.ruhe_kaefig())
        return ruhe

    def seiten(self):
        """`[{seite, knochen, fuss, q, winkel, winkel_koerper, waagrecht_grad, rest_vorher_mm, rest_nachher_mm}]` — je Seite die Drehung des
        Fußes gegen den Unterschenkel (`Q`, in Achsen der Ruhelage). Mit Schuhen (`schuh_netz`) ist es die Drehung, bei der die Sohle
        waagrecht steht: das Original steht auf Zehenspitzen (die Sohle des Stiefels 21–33° geneigt), die Figur soll flach stehen —
        `winkel_koerper` ist die Drehung des Körperfußes im Original, `waagrecht_grad` die Zusatzdrehung dazwischen."""
        if self._seiten is not None:
            return self._seiten
        aus = []
        lage = self.lage
        for seite, teil_fuss, teil_bein, knochen in self.SEITEN:
            fuss = lage.teil == self.nummer[teil_fuss]
            bein = lage.teil == self.nummer[teil_bein]
            koerper = self.netz[self.teile == self.nummer[teil_fuss]]
            if fuss.sum() < 10 or bein.sum() < 10:
                continue
            if len(koerper) >= 10:
                r_fuss, vorher, nachher = self._fuss(lage.kaefig_ruhe[fuss], lage.kaefig_posiert[fuss], koerper)
            elif self.schuhe is not None:
                # Körper ohne Füße (Rainy, 10.10.2026: der Körper endet bei 0,911 m, Beine und Füße kommen aus Hose und Stiefel — `Blendimportkoerperergaenzung`):
                # bis dahin gab es keine Seite, keinen Griff und keine waagrechte Sohle — gemessen an Rainys Schuhen im Browser: tiefster Punkt 62 mm unter
                # dem Boden, Sohle Ferse → Spitze −62 … +7 mm (rund 16° geneigt; Asian Female ±5 mm). Der Fußwinkel kommt dann aus dem Käfig der Figur
                # (Ruhe → Haltung, ohne Nachzug an Körperpunkten, die es nicht gibt); die Sohle stellt `waagrecht` am Schuh.
                r_fuss, vorher, nachher = self.kabsch(lage.kaefig_ruhe[fuss], lage.kaefig_posiert[fuss])[0], 0.0, 0.0
            else:
                continue
            r_bein = self.kabsch(lage.kaefig_ruhe[bein], lage.kaefig_posiert[bein])[0]
            q = r_bein.T @ r_fuss
            winkel = float(np.degrees(np.arccos(np.clip((np.trace(q) - 1.0) / 2.0, -1.0, 1.0))))
            deckung = len(koerper) / max(int(fuss.sum()), 1)
            aus.append({'seite': seite, 'knochen': knochen, 'fuss': fuss, 'q': q, 'winkel': winkel, 'winkel_koerper': winkel,
                        'waagrecht_grad': 0.0, 'r_bein': r_bein, 'punkte': lage.kaefig_posiert[fuss], 'ohne_koerper': len(koerper) < 10,
                        'rest_vorher_mm': round(vorher, 2), 'rest_nachher_mm': round(nachher, 2), 'deckung': round(deckung, 2),
                        'verlaesslich': deckung >= self.FUSS_DECKUNG_MIN and nachher <= self.FUSS_REST_H_MAX * lage.h * 1000.0})
        je_fuss = self._schuh_je_fuss(aus)
        for s in aus:
            schuh = je_fuss.get(s['seite'])
            if schuh is None or len(schuh) < self.SCHUH_MINDEST:
                continue
            zusatz = self.waagrecht(schuh @ s['r_bein'])
            if abs(zusatz) >= self.SOHLE_TOLERANZ:
                self._drehen(s, zusatz)
        self._seiten = aus
        return aus

    def hinweise(self):
        """Texte für den Bericht des Schuhs: wo der Körper den Fuß nicht trägt, ist der Fußwinkel keine Messung am Fuß im Schuh (Fallout ranger)."""
        seite = lambda s: 'Linker' if s['seite'] == 'l' else 'Rechter'  # noqa: E731
        ohne = ['%s Fuß: der Körper der .blend hat keine Füße — Fußwinkel %.0f° aus dem Käfig der Figur, die Sohle des Schuhs steht waagrecht; ob der Fuß im Schuh '
                'sitzt, ist nicht gemessen' % (seite(s), s['winkel']) for s in self.seiten() if s.get('ohne_koerper')]
        return ohne + ['%s Fuß: der Körper der .blend trägt ihn nicht (%.0f %% der Käfigpunkte, ICP-Rest %.1f mm) — Fußwinkel %.0f° vermutlich Ausgleich für das fehlende Stück '
                       'Bein (der Körper endet bei den Knöcheln), kein Fuß im Schuh' % (seite(s), 100.0 * s['deckung'], s['rest_nachher_mm'], s['winkel'])
                       for s in self.seiten() if not s['verlaesslich'] and not s.get('ohne_koerper')]

    def aktiv(self):
        """Die Seiten, deren Fuß sich um mehr als `MINDEST_GRAD` gegen den Unterschenkel dreht."""
        return [s for s in self.seiten() if s['winkel'] >= self.MINDEST_GRAD]

    def ruhe_kaefig(self):
        """Der Käfig in Ruhe mit den Füßen in Absatzhaltung — der Käfig der Figur MIT `griff()`, gehäutet wie beim Tragen (`G9formung`),
        Füße 0 der Ruhe: das Ziel ist damit genau das, was der Browser zeigt. Bis 09.10.2026 drehte diese Funktion die Fußpunkte starr um
        das Fußgelenk (`Skelett kopf − Boden`), und das war zweifach falsch (gemessen `ProjektTemp/_wegwerf/fuss_achse_pruefen.py`,
        `boot_haltung_versatz.py`, `schuh_kaefig_lbs.py`): (1) das Skelett der Formung liegt schon im Raum „Füße 0" — der abgezogene Boden
        (−9,2 mm) setzte den Drehpunkt 9 mm über das echte Gelenk (Achspunkt der Drehung mit Griff 0,0738 m, Skelett 0,0736, Rechnung 0,0827),
        der Schuh saß um ~8 mm (+4 oben, −7 hinten) neben dem Fuß mit Griff; (2) die starre Drehung ließ den Käfig am Knöchel reißen (Fuß und
        Unterschenkel an der Grenze verschieden bewegt): Kantenverzerrung des Stiefels 1,67 % gegen 0,12 % mit dem gehäuteten Käfig, größte
        Streckung 2,4 gegen 1,6. Die Füße selbst stimmen mit beiden überein (0,00 mm), der Unterschenkel am Knöchel nicht (p90 7,5 mm)."""
        from Genesis9.formung import G9formung

        regler = dict(self.lage.stellung())
        boden = G9formung.aus_abfrage(dict(regler), {}).boden()
        return G9formung.aus_abfrage(regler, self.griff()).punkte() - np.array([0.0, boden, 0.0])

    def griff(self):
        """`{l_foot: {'rotation/x': Grad, …}, r_foot: …}` — `Q` in den Achsen und der Reihenfolge des Genesis-Knochens
        (`E = Oᵀ·Q·O`, wie `G9autofit.umrechnen`); leer, wenn kein Fuß sich genug dreht."""
        return {s['knochen']: self._kanaele(s['knochen'], s['q']) for s in self.aktiv()}

    @staticmethod
    def _kanaele(knochen, q):
        """Die Drehung `q` als Kanalwerte des Genesis-Knochens `knochen` (`E = Oᵀ·Q·O`, in der Reihenfolge des Knochens)."""
        from Genesis9.knochenmatrizen import G9knochenmatrizen
        from Genesis9.skelett import G9skelett
        from scipy.spatial.transform import Rotation

        k = next(k for k in G9skelett.roh() if k['name'] == knochen)
        o = G9knochenmatrizen.euler(k.get('orientation', (0.0, 0.0, 0.0)), 'XYZ')
        reihenfolge = str(k.get('reihenfolge') or 'XYZ').lower()
        grad = Rotation.from_matrix(o.T @ q @ o).as_euler(reihenfolge, degrees=True)
        return {'rotation/%s' % a: round(float(w), 4) for a, w in zip(reihenfolge, grad, strict=True) if abs(float(w)) > 1e-6}

    def bericht(self):
        return {'seiten': [{'seite': s['seite'], 'winkel_grad': round(s['winkel'], 1), 'winkel_koerper_grad': round(s['winkel_koerper'], 1),
                            'waagrecht_grad': s['waagrecht_grad'], 'rest_vorher_mm': s['rest_vorher_mm'],
                            'rest_nachher_mm': s['rest_nachher_mm'], 'deckung': s['deckung'], 'verlaesslich': s['verlaesslich']}
                           for s in self.seiten()],
                'griff': self.griff()}
