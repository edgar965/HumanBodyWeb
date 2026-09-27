# -*- coding: utf-8 -*-
u"""Exportfleckenprüfung — steckt eine ANDERE Farbe im eigenen Umriss?

WOZU (27.09.2026, Edgar mit Nahaufnahme der Schuhe: „regression — im obj ist
die Textur der Haut wieder weg und die gleichen Fehler bei den Schuhen! …
teste wieder, passe deine testcases an, die müssen das alles erkennen"):

Ein Werkstoff OHNE Bildkarte (`Kd` allein, z. B. der Schuh `mat_16`) sieht im
Rendern unter reinem Umgebungslicht ÜBERALL, wo er die Fläche stellt, GENAU
EINE Farbe — es gibt nichts, was sie ändern könnte. Sticht die verdeckte Haut
durch den Schuh (`Hauteinzug` reicht nicht überall), erscheinen an genau
diesen Stellen hautfarbene Flecken MITTEN im Schuh-Umriss.

`Exportbildpruefung` (farblose Stellen) sieht das nicht — die Flecken sind
farbig, nur die FALSCHE Farbe. Diese Prüfung braucht deshalb ZWEI Bilder:

- das VERGLEICHSBILD: NUR Körper + der geprüfte Teil
  (`blender/exportbild.py --nur genesis9_koerper,<teil>`) — NICHT die volle
  Szene mit Haaren/Kleid: Haare, die legitim vor einem Schulterausschnitt
  hängen, sähen sonst wie ein Fleck aus (Fund 27.09.2026 am Kleid: 9,5 %
  „Flecken", die beim Ausschluss der Haare auf 0,45 % fielen — derselbe
  Fund war blank falsch, bis die Szene auf Körper+Teil verkleinert wurde);
- eine ISOLIERTE Silhouette NUR des geprüften Teils (`--nur <namensteil>`,
  mit demselben Bildrahmen — `exportbild.py` sorgt dafür, `--nur` nimmt
  mehrere kommagetrennte Namensteile).

Innerhalb der Silhouette wird im Vollbild gemessen, wie viele Bildpunkte von
der HÄUFIGSTEN Farbe der Silhouette abweichen. Ein sauberer flacher Werkstoff
liegt nahe 0 % (das Kleid `mat_15`: 0,8 % Kantenrauschen, gemessen 26.09.2026).
Skin, das durch den Schuh sticht, lag bei 17,3 % (Damira1/DanceKurz,
27.09.2026) — weit über jeder Kantentoleranz.

GRENZEN: Nur sinnvoll für WERKSTOFFE OHNE eigene Bildkarte (sonst ist
Farbvielfalt im Umriss gewollt). Sagt nicht, WESSEN Farbe da durchsticht —
dafür reicht der Augenschein am Fund (hier: Hautton).

FALSCHER ALARM AM SILHOUETTENRAND (27.09.2026, Damira1/Flats, nach dem
Hautmaske-Fix): Der Schuh maß weiterhin 6,0 % — visuell aber sauber. Die
markierten Punkte lagen alle (98 von 312 direkt, 288 von 312 innerhalb
3 Pixel) auf einer dünnen Linie GENAU am oberen Schuhrand: Silhouette
(Schuh allein vor leerem Hintergrund) und Vollbild (Schuh neben Haut) glätten
denselben Rand geometrisch identisch, aber MIT VERSCHIEDENEM NACHBARN — das
Antialiasing mischt dort mit Schwarz/Transparent statt mit Hautfarbe, eine
andere Mischfarbe als `GLEICH` vorsieht. Bei einer großen Fläche (Kleid,
165.884 Silhouettenpunkte) geht dieser 1–3 Pixel breite Rand in 0,45 % unter;
beim kleinen Schuh (5.175 Punkte, weil die Kamera auf die GANZE Figur rahmt,
nicht auf den Schuh) macht er allein 6 % aus. Deshalb wird die Silhouette vor
der Auswertung um `RAND_PX` erodiert — ein echter Fund (17,3 % in der Fläche,
nicht am Rand) bleibt davon unberührt, siehe `test_5_...` unten.
"""
from pathlib import Path


class Exportfleckenpruefung:

    #: Zwei Bildpunkte gelten als „gleiche Farbe", wenn die Summe der
    #: Kanaldifferenzen (R+G+B) höchstens so groß ist — deckt Kanten-
    #: Antialiasing ab (gemessen: dessen Nachbarn liegen bei 0–12).
    GLEICH = 16

    #: So viele Pixel wird die Silhouette vor der Auswertung eingezogen —
    #: nimmt den Antialiasing-Rand zwischen Silhouette und Vollbild heraus
    #: (gemessen am Schuh-Fehlalarm: 288 von 312 Punkten lagen innerhalb
    #: dieser Tiefe). Ein Fund MITTEN im Umriss bleibt davon unberührt.
    RAND_PX = 3

    #: Ab diesem Anteil abweichender Punkte gilt die Silhouette als fleckig.
    #: Das Kleid (sauber) maß 0,8 %; der durchstechende Fuß 17,3 % — die
    #: Schwelle liegt bewusst weit dazwischen, nicht knapp am Fund.
    SCHWELLE = 0.05

    def __init__(self, vollbild_pfad, silhouette_pfad):
        self.vollbild_pfad = Path(vollbild_pfad)
        self.silhouette_pfad = Path(silhouette_pfad)

    def bericht(self):
        u"""`{punkte, hauptfarbe, hauptanteil, fleckig, fleckenanteil, fleckig_bool}`.

        `punkte` = Größe der Silhouette (Bildpunkte mit Alpha > 128).
        `hauptfarbe` = häufigste RGB-Farbe darin (das, was der Werkstoff
        eigentlich überall zeigen sollte). `fleckenanteil` = Anteil der
        Silhouetten-Punkte, die weiter als `GLEICH` davon abweichen.
        """
        import numpy as np
        from PIL import Image
        from scipy import ndimage

        voll = np.asarray(Image.open(self.vollbild_pfad).convert('RGBA'), dtype=np.int16)
        sil = np.asarray(Image.open(self.silhouette_pfad).convert('RGBA'), dtype=np.int16)
        if voll.shape[:2] != sil.shape[:2]:
            raise ValueError(
                'Vollbild (%s) und Silhouette (%s) haben verschiedene Größen — '
                'beide müssen mit demselben Bildrahmen gerendert sein.'
                % (voll.shape[:2], sil.shape[:2]))

        roh = sil[:, :, 3] > 128
        # Randerosion (siehe Docstring „FALSCHER ALARM AM SILHOUETTENRAND"):
        # bleibt nach dem Einziehen nichts übrig (ein sehr dünnes Teil), gilt
        # die ungeschmälerte Maske — sonst würde jedes schmale Teil als leer
        # gemeldet statt als das, was es ist.
        eng = ndimage.binary_erosion(roh, iterations=self.RAND_PX)
        maske = eng if eng.any() else roh
        punkte = int(maske.sum())
        if punkte == 0:
            return {'punkte': 0, 'hauptfarbe': None, 'hauptanteil': 0.0,
                    'fleckenanteil': 0.0, 'fleckig': False}

        farben = voll[:, :, :3][maske]
        hauptfarbe = self._haeufigste(farben)
        abstand = np.abs(farben - hauptfarbe).sum(axis=1)
        fleckig_n = int((abstand > self.GLEICH).sum())
        fleckenanteil = fleckig_n / punkte

        return {
            'punkte': punkte,
            'hauptfarbe': tuple(int(x) for x in hauptfarbe),
            'hauptanteil': round(1 - fleckenanteil, 4),
            'fleckenanteil': round(fleckenanteil, 4),
            'fleckig': fleckenanteil > self.SCHWELLE,
        }

    @staticmethod
    def _haeufigste(farben):
        u"""Die häufigste Farbe — gerundet auf 4er-Schritte, damit
        Antialiasing-Nachbarn (149,62,58 / 150,63,58 / …) nicht als lauter
        eigene Einzelfarben zählen und die echte Mehrheit verdecken."""
        import numpy as np

        grob = (farben // 4 * 4)
        eindeutig, anzahl = np.unique(grob, axis=0, return_counts=True)
        grobfarbe = eindeutig[anzahl.argmax()]
        # Zurück zur ECHTEN Mehrheitsfarbe unter den Punkten, die in diesen
        # groben Kübel fallen — sonst wäre `hauptfarbe` selbst schon gerundet.
        in_kuebel = (grob == grobfarbe).all(axis=1)
        echte, echte_n = np.unique(farben[in_kuebel], axis=0, return_counts=True)
        return echte[echte_n.argmax()]
