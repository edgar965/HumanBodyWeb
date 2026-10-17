# -*- coding: utf-8 -*-
"""Engine2d3dKleiderposetiefe — die Tiefe der SAM-Gelenke an Händen und Füßen entlang der Kette, nicht nur aus der Mitte der Dicke (17.10.2026).

Anlass (Mesh3D-AI, Vorstufe „Nur Rig“): an zwei Posen zeigte der linke Fuß der Rig-Figur 124° bzw. 151° falsch. SAM 3D Body hatte die Tiefe richtig (sitzend: Zeh 0,19 m VOR dem Knöchel,
laufend: Zeh hinter dem Knöchel — wie das Ziel), verloren ging sie beim Legen ins Netz: die Mitte der Netzpunkte im Strahl ist nur dann das Gelenk, wenn das Glied quer zum Strahl liegt.
Zeigt der Fuß zur Kamera, landen Ferse und Zeh am selben Punkt; liegt das Schienbein im Strahl der Zehenspitze, landet die Zehe auf dem Schienbein (`ProjektTemp/_wegwerf/mesh3dai_fuesse_schichten.py`).

Die Regel: Die Gelenke in `KETTE` hängen an ihrem Elterngelenk: Vorhersage = Tiefe des Elterngelenks im Netz + Tiefenunterschied bei SAM (k3; die Kamera blickt nach +z, das Netz zeigt zur Kamera)
× Maßstab SAM → Netz. Bereich = vorderste bis hinterste Netzfläche im Strahl (2.–98. Perzentil, wie die Mitte). Ist er kurz (Glied quer zum Strahl, bis `KURZ` Radien), gilt seine Mitte wie bisher;
ist er lang (ab `LANG` Radien), die Vorhersage in den Bereich geklemmt; dazwischen gemischt. Liegt die Vorhersage weiter als `WEIT` Radien außerhalb, trifft der Strahl ein anderes Glied als das
Gelenk (SAM setzte die Zehenspitze des laufenden Fußes 10 cm zu tief, der Strahl traf das Schienbein): das Gelenk fällt weg — eine falsche Landmarke dreht den Fuß, eine fehlende überlässt ihn der Fläche.
Alle übrigen Gelenke (Rumpf, Gesicht, Schultern, Hüften, Ellbogen, Knie, Knöchel) behalten die Mitte — an ihr ist die SAM-Tabelle (`Samkalibrierung`, A-Pose) gemessen.

Was gemessen wurde (12 Mesh-3D-Aufträge mit Ziel, `mesh3dai_fuesse_rig_messen.py`; Tagebuch 2026-10-17, Abschnitt „Füße"): die Kette auch an Knien/Knöcheln/Ellbogen machte die Landmarken genauer
(Tiefe Ø 37,3 → 16,5 mm), zog aber die Anpassung einer sitzenden Figur ins Becken (Rumpf 7 → 38 mm; mit Hüften an den Schultern 57 mm) — die Fläche hielt Knie und Becken vorher selbst richtig, nur die
Füße und Hände drehte sie mit den falschen Spitzen. Schichten (Lücken im Strahl) taugen NICHT als Glieder: das Netz ist hohl, ein dickes Glied zerfällt in Vorder- und Rückseite.
"""

import numpy as np

__all__ = ['Engine2d3dKleiderposetiefe']


class Engine2d3dKleiderposetiefe:
    #: Elterngelenk je Gelenk an Armen und Beinen (MHR-Namen).
    ELTERN = {
        'left-elbow': 'left-shoulder', 'right-elbow': 'right-shoulder', 'left-wrist': 'left-elbow', 'right-wrist': 'right-elbow',
        'left-knee': 'left-hip', 'right-knee': 'right-hip', 'left-ankle': 'left-knee', 'right-ankle': 'right-knee',
        'left-heel': 'left-ankle', 'right-heel': 'right-ankle', 'left-big-toe-tip': 'left-ankle', 'right-big-toe-tip': 'right-ankle',
        'left-hip': 'left-shoulder', 'right-hip': 'right-shoulder',
    }
    #: Die Gelenke, deren Tiefe die Kette rechnet: Hüften (an den Schultern), Arme ab dem Ellbogen, Beine ab dem Knie; Schultern und Gesicht behalten die Mitte. Gemessen an 12 Mesh-3D-Aufträgen mit Ziel
    #: (`mesh3dai_fuesse_rig_messen.py`, Rig gegen Ziel Ø 138 Gelenke): alle Gelenke Mitte 21,2 mm · ohne die Hüften 12,7 · mit 12,3 · nur Ferse/Zehe/Handgelenk 17,2 mm (der laufende Fuß wieder 151°
    #: verdreht: der Knöchel lag in der Mitte 23 cm neben dem Gelenk). Die Hüften gehören dazu, seit MannLaufen mit Stiefeln neu gebaut war: dort lag die Mitte der linken Hüfte 29 cm hinter dem Gelenk
    #: (der Strahl lief durch das nach hinten gestreckte Bein), Knie und Fuß folgten ihr (Fuß 70° verdreht). Preis: das Becken der sitzenden Figur liegt 57 statt 38 mm neben dem Ziel (Ursache offen).
    KETTE = ('left-hip', 'right-hip', 'left-elbow', 'right-elbow', 'left-wrist', 'right-wrist', 'left-knee', 'right-knee', 'left-ankle', 'right-ankle',
             'left-heel', 'right-heel', 'left-big-toe-tip', 'right-big-toe-tip')
    #: Eigene Grenzen (kurz, lang in Radien) für die Hüften: der Rumpf ist dick (stehend 6–7,5 Radien vorn bis hinten — dort bleibt die Mitte). Hüften fallen nie weg, sie werden geklemmt.
    BEREICH = {'left-hip': (8.0, 12.0), 'right-hip': (8.0, 12.0)}
    #: Steht im Ergebnis des Pose-Schritts (`ergebnis.pose.abbildung.tiefe_fassung`): Läufe mit einer anderen Fassung sind nicht vergleichbar.
    FASSUNG = 2
    #: Bereich bis so viele Radien = Glied quer zum Strahl → Mitte; ab `LANG` die Vorhersage (Setzungen: 4 × 0,033 m ≈ 13 cm, 8 × ≈ 27 cm).
    KURZ = 4.0
    LANG = 8.0
    #: Vorhersage weiter als so viele Radien außerhalb des Bereichs → der Strahl trifft ein anderes Glied, das Gelenk fällt weg (Setzung; gemessen 7,3 Radien am laufenden Fuß).
    WEIT = 3.0

    def __init__(self, k3, namen, radius, massstab):
        """`k3` (70, 3) SAM 3D Body in Metern (Kamera: x rechts, y unten, z in die Szene), `namen` die MHR-Namen, `radius` des Strahlrohrs und `massstab` (Netzeinheiten je Meter) aus der Abbildung."""
        self.k3 = np.asarray(k3, dtype=np.float64)
        self.index = {n: i for i, n in enumerate(namen)}
        self.radius = float(radius)
        self.massstab = float(massstab)

    @classmethod
    def massstab_aus(cls, xy_netz, k3_xy):
        """Netzeinheiten je Meter: Streuung der Gelenke in der Bildebene (Netz) ÷ dieselbe Streuung bei SAM — unabhängig von einer Drehung im Bild (Drehungen 90/180/270)."""
        a = np.asarray(xy_netz, dtype=np.float64)
        b = np.asarray(k3_xy, dtype=np.float64)
        return float(np.sqrt(((a - a.mean(0)) ** 2).sum() / max(((b - b.mean(0)) ** 2).sum(), 1e-12)))

    def kette(self, name):
        return self.ELTERN.get(name)

    def zaehlt(self, name, tiefen):
        """Rechnet die Kette dieses Gelenk? Nur die in `KETTE`, und nur, wenn ihr Elterngelenk eine Tiefe hat."""
        return name in self.KETTE and self.ELTERN.get(name) in tiefen

    def tiefe(self, name, z_strahl, z_eltern):
        """`(z, art, vorhersage)`: `art` = `mitte` (kurzer Bereich), `sam` (langer Bereich, Vorhersage darin), `gemischt`, `verworfen` (`z` = NaN)."""
        vorhersage = float(z_eltern) - self.massstab * (self.k3[self.index[name], 2] - self.k3[self.index[self.ELTERN[name]], 2])
        z = np.asarray(z_strahl, dtype=np.float64)
        lo, hi = float(np.percentile(z, 2)), float(np.percentile(z, 98))
        aussen = max(lo - vorhersage, vorhersage - hi, 0.0)
        if aussen > self.WEIT * self.radius and name not in self.BEREICH:
            return float('nan'), 'verworfen', vorhersage
        mitte = (lo + hi) / 2.0
        kurz, lang = self.BEREICH.get(name, (self.KURZ, self.LANG))
        w = float(np.clip(((hi - lo) / self.radius - kurz) / (lang - kurz), 0.0, 1.0))
        art = 'mitte' if w == 0.0 else ('sam' if w == 1.0 else 'gemischt')
        return (1.0 - w) * mitte + w * float(np.clip(vorhersage, lo, hi)), art, vorhersage
