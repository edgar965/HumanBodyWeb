# -*- coding: utf-8 -*-
"""Gelenknamen — die EINE Liste der 2D-Gelenke und ihrer Verbindungen.

`BODY_JOINT_NAMES` stand wortgleich in `dienste/keypoints.py` UND
`dienste/keypoints_quellen.py`; die Verbindungslinien und die OpenPose-Namen
standen ebenfalls doppelt (einmal in der Überlagerungs-Antwort, einmal im
Videorenderer), dort sogar in zwei Längen: 15 Namen in der einen Fassung, 25 in
der anderen. Wer ein Gelenk ergänzt, hätte drei Stellen ändern müssen —
gefunden von `doppelcode` (Kriterium 6).

DIE REIHENFOLGE IST DER VERTRAG
===============================
`OPENPOSE_BODY25` wird über den INDEX gelesen: OpenPose liefert eine flache
Liste `[x, y, conf, x, y, conf, …]`, die Position bestimmt das Gelenk. Ein
eingeschobener Name verschiebt alle folgenden — das Skelett bleibt sichtbar,
zeigt aber Unsinn. Deshalb steht die Liste hier einmal und wird nur ergänzt,
nie umsortiert.
"""


class Gelenknamen:
    """Namen, Reihenfolge und Verbindungen der 2D-Gelenke."""

    #: Die Gelenke, die aus einer MocapNET-CSV gelesen werden
    #: (`2DX_<name>`, `2DY_<name>`, `visible_<name>`).
    GELENKE = (
        'head', 'neck', 'rshoulder', 'relbow', 'rhand',
        'lshoulder', 'lelbow', 'lhand', 'hip',
        'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot',
        'endsite_eye.r', 'endsite_eye.l', 'rear', 'lear',
    )

    #: Die Linien der Überlagerung — Rumpf, Arme, Beine.
    VERBINDUNGEN = (
        ('head', 'neck'),
        ('neck', 'rshoulder'), ('rshoulder', 'relbow'), ('relbow', 'rhand'),
        ('neck', 'lshoulder'), ('lshoulder', 'lelbow'), ('lelbow', 'lhand'),
        ('neck', 'hip'),
        ('hip', 'rhip'), ('rhip', 'rknee'), ('rknee', 'rfoot'),
        ('hip', 'lhip'), ('lhip', 'lknee'), ('lknee', 'lfoot'),
    )

    #: OpenPose BODY_25 in seiner Reihenfolge — der Index ist die Kennung.
    OPENPOSE_BODY25 = (
        'nose', 'neck', 'rshoulder', 'relbow', 'rhand',
        'lshoulder', 'lelbow', 'lhand', 'midhip',
        'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot',
        'reye', 'leye', 'rear', 'lear',
        'lbigtoe', 'lsmalltoe', 'lheel',
        'rbigtoe', 'rsmalltoe', 'rheel',
    )

    #: OpenPose-Name -> unser Name. Nur zwei weichen ab.
    OPENPOSE_UMBENENNEN = {'nose': 'head', 'midhip': 'hip'}

    #: Kopf und Ohren — die zeichnet nur das Skelettvideo, die Überlagerung
    #: nicht. Zwei Schreibweisen für die Augen, weil OpenPose `reye`/`leye`
    #: liefert und die MocapNET-CSV `endsite_eye.r`/`endsite_eye.l`.
    KOPFVERBINDUNGEN = (
        ('head', 'reye'), ('head', 'leye'),
        ('reye', 'rear'), ('leye', 'lear'),
        ('head', 'endsite_eye.r'), ('head', 'endsite_eye.l'),
        ('endsite_eye.r', 'rear'), ('endsite_eye.l', 'lear'),
    )

    @classmethod
    def alle_verbindungen(cls):
        """Rumpf, Arme, Beine PLUS Kopf/Augen/Ohren — fürs Skelettvideo.

        Vorher stand diese Liste in `dienste/skelettvideo.py` und führte jede
        Kante ZWEIMAL: einmal mit `midhip`/`nose` (OpenPose) und einmal mit
        `hip`/`head` (MocapNET). Seit die OpenPose-Namen beim Lesen umgeschrieben
        werden (`Gelenkquelle.aus_openpose`), gibt es nur noch eine Schreibweise.
        """
        return list(cls.VERBINDUNGEN) + list(cls.KOPFVERBINDUNGEN)

    @classmethod
    def verbindungsliste(cls):
        """Die Verbindungen als Listen — so erwartet sie das JavaScript."""
        return [list(paar) for paar in cls.VERBINDUNGEN]

    @classmethod
    def umbenannt(cls, punkte):
        """OpenPose-Namen auf unsere umschreiben — `nose` -> `head`."""
        for alt, neu in cls.OPENPOSE_UMBENENNEN.items():
            if alt in punkte:
                punkte[neu] = punkte.pop(alt)
        return punkte
