# -*- coding: utf-8 -*-
"""Architekturai2d3dandere — wie andere aus Fotos 3D-Menschen machen, und wo 2d-3d-AI dagegen steht (24.10.2026), für Hilfe → Architektur → 2d-3d-AI.

Edgar: „schau auch nach, wie andere das machen, z.B. tripo, hunyan, meshai, wir hatten doch schon eine Recherche. ist das durch die mesh3d-AI Erkenntnisse besser geworden, haben wir eine Chance
gegen die?“ Quellen: die eigene Recherche (Hilfe → Recherche → meshy.ai, Stand 08.10.2026; `mesh3dai-ki-ergebnis.md`, 23.10.2026) und eine Websuche am 24.10.2026. Alles hier ist BEHAUPTUNG
der Quelle (Herstellerseiten, Testberichte), nicht bei uns nachgemessen — außer, wo `gemessen` steht.

Eintrag: `(name, liefert, genesis, offen, beleg, quelle_text, quelle_url)`.
"""

__all__ = ['Architekturai2d3dandere']


class Architekturai2d3dandere:
    EINTRAEGE = (
        ('Tripo3D (H3.1, März 2026)', 'Netz mit Textur aus einem oder mehreren Bildern; automatisches Rig (eigenes Skelett, Hautgewichte)', 'nein', 'geschlossen',
         'gemessen an OlesiaWalk (23.10.2026): Netz → Wahrheit Mittel 6,6 mm, p95 13,0 mm', 'Tripo-AI-Review 2026', 'https://pasqualepillitteri.it/en/news/7811/tripo-ai-review-3d-model-generator'),
        ('Meshy 6', 'Netz mit Textur aus Text, einem Bild oder bis zu vier Ansichten; Auto-Rig für Menschen, A-/T-Pose wählbar', 'nein', 'geschlossen',
         'Angabe Dritter (Summer Engine, Meshy-Seiten)', 'Meshy 6 (Summer Engine)', 'https://www.summerengine.com/models/meshy-6.md'),
        ('Hunyuan3D-2mv (Tencent)', 'Netz aus mehreren Ansichten; läuft bei uns lokal (python10), Hunyuan3D 2.5/3.x nur als Dienst ohne Gewichte', 'nein', 'offen (2mv)',
         'gemessen an OlesiaWalk (23.10.2026): Mittel 11,4 mm, p95 32,8 mm; rund 150 s je Netz', 'Hunyuan3D-2 MV', 'https://www.pixelsham.com/2025/06/14/tencent-hunyuan3d-2-0-adds-mv-multi-view-and-mv-mini'),
        ('Daz Face Transfer 2', 'aus EINEM Foto Kopfform, Gesichtstextur und Hautton einer Genesis-9-Figur (nur der Kopf, 49,95 $)', 'ja, nur Kopf', 'geschlossen',
         'Herstellerseite; ein Zusatzpaket wirbt damit, dass die Gesichter zu breit und im Profil zu flach werden', 'Daz Face Transfer 2', 'https://www.daz3d.com/face-transfer-2'),
        ('Reallusion Headshot 2', 'Kopf aus einem Foto; aus einem Netz (Scan) eine Character-Creator-Figur, der Körper wird über Regler von Hand angepasst', 'nein (CC4)', 'geschlossen',
         'Testbericht 2023', 'CG Channel: Headshot 2.0', 'https://www.cgchannel.com/2023/06/reallusion-ships-headshot-2-0'),
        ('SAM 3D Body (Meta, CVPR 2026)', 'Haltung und Körperform eines Menschen aus EINEM Bild als parametrisches Modell (MHR), ohne Kleider', 'nein (MHR)', 'offen',
         'eine unabhängige Prüfung findet Schwächen bei besonderen Körperformen', 'SAM 3D Body, CVPR 2026', 'https://cvpr.thecvf.com/virtual/2026/oral/40311'),
    )
    #: Die Einordnung (24.10.2026) — eigene Einschätzung, als solche gekennzeichnet.
    EINORDNUNG = (
        ('Auf ihrem Feld — ein Netz, das aussieht wie das Foto — nicht.', 'Tripo und Meshy sind Firmen mit großen Datenmengen (Tripo: Finanzierungsrunde 150 Mio. $, Juli 2026, laut Bericht). '
         'Ein Genesis-Modell kann dem Foto nie näher kommen, als der Raum aus Reglern, Posen und Katalogkleidern erlaubt.'),
        ('Auf unserem Feld — ein bearbeitbares Genesis-9-Modell mit Daz-Rig, Reglern, Haut und Kleidern aus Fotos, ganzer Körper — fanden Recherche und Websuche kein Produkt.',
         'Daz Face Transfer 2 macht nur den Kopf, Headshot 2 macht CC-Figuren, Tripo und Meshy ein eigenes Rig ohne Regler. Darum sind Tripo und Hunyuan Bausteine (Weg A, Messlatte), keine Gegner.'),
        ('Was Mesh3D-AI dazu beiträgt', 'Bausteine, die es vorher nicht gab: die Wirkung jedes Formreglers, Daz-Winkel in den Grenzen von Genesis, Hautkopf, Datengenerator mit Wahrheit, Prüfsatz der '
         'sechs Tripo-Jobs, Genesis-Teile auf der GPU. Ob das Ergebnis besser ist als bei den Wegen vom September (Modell aus Bildern, 2D3D Kleider), ist NICHT vergleichbar gemessen — dort gab es keine Wahrheit.'),
        ('Unser Vorteil, wenn er trägt', 'Die Fotos der Exporte sind selbst Genesis-Renderings mit bekannter Kamera: Trainingsdaten mit Wahrheit kosten Sekunden (ein Bildersatz 1,7 s) statt Minuten '
         '(ein Hunyuan-Netz rund 150 s). Das gilt für Exporte; für echte Fotos (Licht, Hintergrund, unbekannte Kamera) ist es eine Vermutung, nicht gemessen.'),
    )

    @classmethod
    def eintraege(cls):
        return [dict(zip(('name', 'liefert', 'genesis', 'offen', 'beleg', 'quelle', 'adresse'), e, strict=True)) for e in cls.EINTRAEGE]
