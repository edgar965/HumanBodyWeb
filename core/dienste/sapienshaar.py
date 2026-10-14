# -*- coding: utf-8 -*-
"""Sapienshaar — die Haarmaske aus der Sapiens-Klasse „Hair" statt (oder zusätzlich zu) der Farbe (05.10.2026).

Edgar (05.10.2026, am Bild der Seitenansicht): „Haar textur noch auf dem Kopf" und „die Haare sind bei Sapiens noch keine Objekte". Sapiens kennt das Haar als eigene Klasse (`Hair`); der Schritt
„Segmentierung" legt die Stimmen je Klasse auf die Flächen des Netzes (`arbeit/sapiens_flaechen.npz`, `klassen`), und `Sapiensmaske` macht daraus je Fläche „Haar" (Mehrheit nach dem Glätten über die
Kantennachbarn). Der Schritt „haar" der Körper-Kette (`Meshfigurhaar`) rechnet seine Maske bisher nur aus Farbe und Lage (`Haar.haarmaske.Haarmaske`: Helligkeit gegen Hautton, Gesichtszone, Bartzone);
diese Klasse legt Sapiens darüber, je nach Option `segmentierung.haar`:

    farbe     nichts — die Maske der Farbe gilt (Vorgabe, wie bisher)
    sapiens   wo Sapiens die Fläche sieht (genug Stimmen), entscheidet Sapiens; sonst die Farbe
    beide     Haar ist, was die Farbe ODER Sapiens als Haar sieht

Geschützt bleibt in jedem Fall, was die Haarmaske selbst schützt: das Innere des Gesichts (`geschuetzt`), die Bartzone (`bart` — der Bart ist KEIN Haar), alles unter der Schnittebene des Kopfnetzes
(`unten`). Fehlen die Stimmen oder gehören sie nicht zu diesem Netz und diesen Einstellungen, gilt die Farbe und der Grund steht im Bericht (`ergebnis.haar.sapiens.grund`) — nie ein stilles Zurückfallen
(`artefakte-benennen.md`). Der Bericht nennt beide Flächen (cm²) und ihre Überschneidung: ob Sapiens das Haar besser trifft als die Farbe, ist damit sichtbar, aber nicht entschieden.
"""

import logging
from pathlib import Path

import numpy as np

from .engine2d3dkleidersegmentierungsoptionen import Engine2d3dKleidersegmentierungsoptionen

logger = logging.getLogger('core')

__all__ = ['Sapienshaar']


class Sapienshaar:
    QUELLEN = Engine2d3dKleidersegmentierungsoptionen.HAAR_QUELLEN

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    def quelle(self):
        """`farbe` | `sapiens` | `beide` — „Mesh to 3D" hat `sapiens_haar` nicht und bleibt bei der Farbe."""
        wahl = getattr(self.lauf, 'sapiens_haar', 'farbe')
        return wahl if wahl in self.QUELLEN else 'farbe'

    def anwenden(self, maske, haarmaske, anzahl_flaechen):
        """Ändert `maske['haar']` an Ort und Stelle und gibt den Bericht zurück (None bei Quelle „farbe"). `haarmaske`: die `Haarmaske` (Kantennachbarn, Flächeninhalt)."""
        wahl = self.quelle()
        if wahl == 'farbe':
            return None
        from Kleidung.sapiensmaske import Sapiensmaske
        from Kleidung.sapienszuordnung import Sapienszuordnung

        einstellungen = getattr(self.lauf, 'sapiens_einstellungen', None) or {}
        netz = self.ablage.netzdatei(original=True)             # die Stimmen gehören zum Netz des Schritts „netz", nicht zum Tiefennetz
        try:
            klassen = Sapiensmaske.laden(self.ablage.arbeit(), netz, anzahl_flaechen, Engine2d3dKleidersegmentierungsoptionen.rechenoptionen(einstellungen))
        except Sapiensmaske.Unbrauchbar as grund:
            logger.warning('Haar %s: Sapiens-Haar nicht benutzt (%s) — die Farbe gilt', self.job.kennung, grund)
            return {'quelle': wahl, 'verwendet': False, 'grund': str(grund)}
        stimmen = Sapienszuordnung.stimmen(klassen, einstellungen)
        sapiens, gesehen = Sapiensmaske.haar_aus(stimmen, haarmaske.nachbarn(), **{k: v for k, v in Sapiensmaske.aus_optionen(einstellungen).items() if k != 'nah_m'})
        alt = np.asarray(maske['haar'], dtype=bool)
        erlaubt = ~np.asarray(maske['geschuetzt'], dtype=bool) & ~np.asarray(maske['bart'], dtype=bool) & ~np.asarray(maske['unten'], dtype=bool)
        sapiens = sapiens & erlaubt                                 # geschützte Zonen sind auch für Sapiens kein Haar
        # „sapiens": wo Sapiens die Fläche sieht, entscheidet es; sonst die Farbe. „beide": die Vereinigung.
        neu = np.where(gesehen, sapiens, alt) if wahl == 'sapiens' else (alt | sapiens)
        cm2 = np.asarray(haarmaske.inhalt, dtype=np.float64) * 1e4
        hut = self.kopfbedeckung(neu & gesehen, klassen, cm2)
        hut = self.ausbreiten(hut, neu & ~gesehen, haarmaske.nachbarn(), np.asarray(haarmaske.mitte)[:, 1])
        # Kopfschmuck, den SAM 3 als Bestandteil der Gruppe „kopf" nennt (Hut, Helm, Krone): seine Rück- und Innenseiten sieht Sapiens nicht, sie hängen aber an ihm — sie sind kein Haar.
        kopf = self.kopf_anker(haarmaske, anzahl_flaechen)
        if kopf.any():
            # Kandidaten: alles in der Haarmaske, was Sapiens NICHT eindeutig als Haar sieht (stärkste Klasse `Hair` mit genug Pixeln) — die Farbregel nennt auch Hutflächen Haar, und das Glätten der Stimmen lässt
            # ungesehene Flächen neben gesehenen als „gesehen" gelten (Spiralballerina: von 899 Haar-Objekt-Flächen berührten 379 den Kopfschmuck, 277 sind klares `Hair`).
            nr = Sapienszuordnung.NAMEN.index('Hair')
            klar_haar = (np.asarray(klassen).argmax(axis=1) == nr) & (np.asarray(klassen)[:, nr] >= Sapiensmaske.MIN_STIMMEN)
            hut = hut | (self.ausbreiten(kopf, neu & ~klar_haar, haarmaske.nachbarn(), np.asarray(haarmaske.mitte)[:, 1]) & ~kopf)
        maske['kopfbedeckung'] = hut                                 # steht in `haar_maske.npz`; der Schritt „kleidung" macht daraus Zubehör
        neu = neu & ~hut
        maske['haar'] = neu
        # Ein Bart, der unter die Schnittebene des Kopfes hängt (Zauberer: bis zur Brust), ist weder Hals noch Kleidung — er kommt NUR ins Haar-Objekt (`Meshfigurhaar.objekt`), nicht in die Frisurwahl.
        bart = self.langer_bart(klassen, np.asarray(maske['unten'], dtype=bool) & ~np.asarray(maske['haut'], dtype=bool),
                                neu | np.asarray(maske['bart'], dtype=bool) | np.asarray(maske['geschuetzt'], dtype=bool), haarmaske.nachbarn(), cm2)
        maske['langer_bart'] = bart
        return {'quelle': wahl, 'verwendet': True, 'flaechen_gesehen': int(gesehen.sum()),
                'farbe': self._zahlen(alt, cm2), 'sapiens': self._zahlen(sapiens, cm2), 'ergebnis': self._zahlen(neu, cm2),
                'kopfbedeckung': self._zahlen(hut, cm2), 'langer_bart': self._zahlen(bart, cm2),
                'beide_flaechen': int((alt & sapiens).sum()), 'geaendert_flaechen': int((neu != alt).sum()),
                'hinzu_flaechen': int((neu & ~alt).sum()), 'weg_flaechen': int((~neu & alt).sum())}

    #: Eine „Haarfläche", auf der Sapiens `Apparel` mehr als so viel stärker sieht als `Hair`, ist eine Kopfbedeckung — und erst ab `HUT_MIN_CM2` zusammen (ein Haarreif oder ein einzelner Fleck ist keine).
    HUT_VERHAELTNIS = 1.5
    HUT_MIN_CM2 = 200.0

    @classmethod
    def kopfbedeckung(cls, kandidaten, klassen, cm2):
        """(F,) bool — die Flächen der Haarmaske (`kandidaten`: Haar UND von Sapiens gesehen), die Sapiens als `Apparel` statt `Hair` sieht: ein Hut. Zauberer (12.10.2026): die Farbregel hielt ihn für Haar
        (Hutkegel und Krempe 125.597 + 34.238 Flächen), Sapiens nennt sie zu 88 % `Apparel`; das Haar-Objekt war ein Hut mit Strähnen, und die Kopfhaut bekam die Hutfarbe (graue Kappe). Ohne Hut: alles False."""
        from Kleidung.sapienszuordnung import Sapienszuordnung

        klassen = np.asarray(klassen, dtype=np.float32)
        apparel, haar = klassen[:, Sapienszuordnung.NAMEN.index('Apparel')], klassen[:, Sapienszuordnung.NAMEN.index('Hair')]
        hut = np.asarray(kandidaten, dtype=bool) & (apparel > cls.HUT_VERHAELTNIS * haar)
        return hut if float(np.asarray(cm2)[hut].sum()) >= cls.HUT_MIN_CM2 else np.zeros_like(hut)

    #: Hutflächen, die Sapiens nicht sieht (Rückseite, Innenseite der Krempe), hängen an gesehenen — gerechnet wird ab dieser Höhe: das 2. Perzentil der Hutflächen minus 2 cm (die Krempe).
    HUT_KREMPE_PROZENT = 2.0
    HUT_KREMPE_PUFFER_M = 0.02

    @classmethod
    def ausbreiten(cls, hut, kandidaten, nachbarn, hoehe):
        """(F,) bool — `hut` plus die zusammenhängenden `kandidaten` (Haarflächen, die Sapiens NICHT sieht) oberhalb der Krempe. Zauberer (12.10.2026): ohne das blieben 44.889 Hutflächen (974 cm²,
        61 % ohne jede Sapiens-Stimme) als Punktwolke im Haar-Objekt. Haar, das Sapiens SIEHT, bleibt Haar; unter der Krempe ändert sich nichts (die Haare und der Bart sind dort). Ohne Hut: unverändert."""
        from scipy.sparse.csgraph import connected_components

        hut = np.asarray(hut, dtype=bool)
        if not hut.any():
            return hut
        hoehe = np.asarray(hoehe, dtype=np.float64)
        grenze = float(np.percentile(hoehe[hut], cls.HUT_KREMPE_PROZENT)) - cls.HUT_KREMPE_PUFFER_M
        frei = hut | (np.asarray(kandidaten, dtype=bool) & (hoehe >= grenze))
        ids = np.flatnonzero(frei)
        _, komponente = connected_components(nachbarn[ids][:, ids], directed=False)
        mit_hut = np.unique(komponente[hut[ids]])
        aus = np.zeros(len(hut), dtype=bool)
        aus[ids[np.isin(komponente, mit_hut)]] = True
        return aus

    def kopf_anker(self, haarmaske, anzahl_flaechen):
        """(F,) bool — die Flächen der Bestandteile der Gruppe „kopf" (SAM 3, `Kleidung/bestandteile.py`; Spiralballerina: 2.695 Flächen Kopfschmuck), wenn der Schritt „segmentierung" sie für DIESES Netz abgelegt hat —
        sonst alles False und es bleibt bei den Sapiens-Stimmen. Der Anker ist der Begriff, nicht ein Gegenstand: jede Zeile der Gruppe „kopf" im Vorrat (`Kleidung/begriffsvorrat.json`) zählt."""
        aus = np.zeros(anzahl_flaechen, dtype=bool)
        datei = Path(self.ablage.arbeit('teile_flaechen.npz'))
        if not datei.is_file():
            return aus
        from Kleidung.bestandteile import Bestandteile

        daten = Bestandteile.laden(datei, anzahl_flaechen)
        if daten is None:
            return aus
        for teil in Bestandteile.zerlegen(daten, haarmaske.flaechen, np.asarray(haarmaske.inhalt, dtype=np.float64) * 1e4):
            if teil['gruppe'] == 'kopf':
                aus |= teil['maske']
        return aus

    #: Ein langer Bart muss zusammen mindestens so viel Fläche haben (cm²) — ein paar Flächen unter dem Kinn sind kein Bart.
    BART_MIN_CM2 = 100.0

    @classmethod
    def langer_bart(cls, klassen, kandidaten, anker, nachbarn, cm2):
        """(F,) bool — die `kandidaten` (Flächen unter der Schnittebene des Kopfes, nicht Haut), die Sapiens (Mehrheit der Stimmen) als `Face_Neck` sieht und die über solche Flächen mit dem `anker` (Haar, Bart, inneres Gesicht
        über der Schnittebene) zusammenhängen. Unter dem Halsansatz gibt es keinen Hals mehr: `Face_Neck` unter der Ebene, das nicht Haut ist, ist ein Bart. Zauberer (12.10.2026): 13.206 Flächen / 279 cm² von y 132 bis 156 cm,
        vorher in keinem Objekt (nicht Haar — unter der Ebene —, nicht Kleidung — Sapiens sagt Gesicht); Edgar (Stoppelbart): nichts. Ohne ausreichend Fläche: alles False."""
        from scipy.sparse.csgraph import connected_components

        from Kleidung.sapienszuordnung import Sapienszuordnung

        klassen = np.asarray(klassen, dtype=np.float32)
        gesehen = klassen.sum(axis=1) > 0
        hals = gesehen & (klassen.argmax(axis=1) == Sapienszuordnung.NAMEN.index('Face_Neck'))
        anker = np.asarray(anker, dtype=bool)
        kandidat = np.asarray(kandidaten, dtype=bool) & hals
        ids = np.flatnonzero(kandidat | anker)
        aus = np.zeros(len(kandidat), dtype=bool)
        if not kandidat.any() or not anker.any():
            return aus
        _, komponente = connected_components(nachbarn[ids][:, ids], directed=False)
        mit_anker = np.unique(komponente[anker[ids]])
        aus[ids[np.isin(komponente, mit_anker) & kandidat[ids]]] = True
        return aus if float(np.asarray(cm2)[aus].sum()) >= cls.BART_MIN_CM2 else np.zeros_like(aus)

    @staticmethod
    def _zahlen(wahl, cm2):
        return {'flaechen': int(wahl.sum()), 'cm2': round(float(cm2[wahl].sum()), 0)}
