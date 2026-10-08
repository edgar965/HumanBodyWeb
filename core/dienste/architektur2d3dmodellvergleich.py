# -*- coding: utf-8 -*-
"""Architektur2d3dmodellvergleich — Tabelle „Modelle im Vergleich" auf Hilfe → Architektur → 2D3D (08.10.2026).

Edgar, 08.10.2026: „Mach [...] eine Tabelle im djangoBase Stil mit allen Modellen, trellis, meshy, mit Daten wie
auflösung, geschwindigkeit, qualität, größe der Modelle, Speed usw." — im Anschluss an die Recherche auf
Hilfe → Recherche → meshy.ai (`core/dienste/recherchemeshy.py`).

Auflösung, Geschwindigkeit und Qualität werden bei den UNS UNBEKANNTEN Modellen (Meshy, Tripo3D, Rodin, Hunyuan3D 2.5,
Direct3D-S2) aus fremden Quellen zitiert, nicht selbst gemessen — anders als bei TRELLIS.2 und Pixal3D, deren Zahlen
aus den eigenen Messungen in `architektur2d3dfaktennetz.py` stammen. Die Spalte `quelle` sagt bei jeder Zeile, welcher
Fall vorliegt. „Qualität" ist in JEDEM Fall eine Einordnung der zitierten Quelle, keine eigene Messung — darum ohne
Sortierung (unterschiedliche Maßstäbe, nicht vergleichbare Zahlen).

Sortierbar nach Zahlen sind nur Spalten mit EINER Einheit über alle Zeilen: Größe (GB) und Geschwindigkeit (s). Die
Spalte Auflösung bleibt Text (Voxel³, Textur-K und Polygonzahl sind keine vergleichbare Größe — ein gemeinsames
Sortiermaß wäre eine erfundene Vergleichbarkeit, `keine-unbelegten-zahlen.md`).
"""

__all__ = ['Architektur2d3dmodellvergleich']


class Architektur2d3dmodellvergleich:
    STAND = '08.10.2026'

    #: Je Zeile: (modell, offen, parameter, aufloesung, geschwindigkeit, geschwindigkeit_s, groesse, groesse_gb,
    #: qualitaet, bei_uns, quelle). `geschwindigkeit_s`/`groesse_gb` sind der Rohwert fürs Sortieren (`data-sort`),
    #: `None` wenn keine einheitliche Zahl vorliegt — dann landet die Zeile beim Sortieren am Ende, nicht bei 0.
    ZEILEN = [
        ('TRELLIS.2 (microsoft/TRELLIS.2-4B)', 'Ja — MIT, HF-Gewichte + Space', '4 Mrd. Parameter',
         'bis 1536³ Voxel (O-Voxel-Darstellung); unsere Vorgabe 1536 („hoch" = 1536_cascade), Space-Vorgabe 1024',
         'bei uns gemessen 428–753 s für den Schritt „netz" (8 Aufträge); Vergleichsquelle nennt 1–3 Min. '
         '(vermutlich nur Kerninferenz, ohne Export)', 590, '14 GB', 14.0,
         'Vergleichsquelle: schneller und günstiger als Hunyuan3D, PBR immer dabei — insgesamt niedriger eingeordnet '
         'als Hunyuan3D, wenn „Qualität und Kontrolle" zählen (Einordnung der Quelle, nicht eigene Messung)',
         'Ja — Hauptmodell Schritt „netz", wählbar im Schritt „kopf" (Wahl „trellis2")',
         'eigene Messung (architektur2d3dfaktennetz.py); huggingface.co/microsoft/TRELLIS.2-4B; triposr.org-Vergleich'),
        ('Hunyuan3D-2.0 / 2mv', 'Ja — offen (Tencent)', 'nicht recherchiert',
         '512³-Klasse (Stand vor Version 2.5, laut Quelle)',
         'Vergleichsquelle nennt 2–6 Min. (nicht an unseren Fotos nachgemessen)', None, 'nicht recherchiert', None,
         'Vergleichsquelle: höhere Gesamtqualität, mehr Eingabemöglichkeiten (Text, Bild, Mehrbild) als TRELLIS.2, '
         'wenn Qualität/Kontrolle zählen',
         'Ja — Schritt „kopf" (Wahl „hunyuan3d_2mv"/„hunyuan3d_2"), früher Hauptmodell vor der Umstellung auf TRELLIS.2',
         'arxiv.org/pdf/2501.12202; triposr.org „Hunyuan3D 2.1 vs TRELLIS.2 vs TripoSR"'),
        ('Hunyuan3D 2.1', 'Ja — vollständig offen seit Juni 2025 (inkl. Trainingscode, VAE, PBR-Pipeline)',
         'nicht recherchiert', '512³-Klasse wie 2.0, zusätzlich volle PBR-Multiview-Diffusion '
         '(Albedo/Normal/Metallic/Roughness gemeinsam)',
         'nicht recherchiert', None, 'nicht recherchiert', None,
         'eigener Papertitel: „production-ready PBR material" (Eigenangabe, nicht unabhängig geprüft)',
         'Ja — Wahlmöglichkeit im Schritt „kopf"',
         'arxiv.org/html/2506.15442; huggingface.co/papers/2506.15442'),
        ('Hunyuan3D 2.5', 'Gewichte: Nein. Nutzung: Ja — eigene Web-Plattform 3d.hunyuan.tencent.com (Gratisstufe + '
         'Abo 25–80 $/Monat) und kostenpflichtige Tencent-Cloud-API (Korrektur 08.10.2026, Edgar: „ist zugänglich!")',
         'bis 10 Mrd. Parameter (Formmodell „LATTICE")', '1024³ (von 512³ erhöht)',
         '8–20 s auf einer RTX 4090 (vermutlich nur Form-Inferenz ohne vollständige Textur-Pipeline; nicht an '
         'unseren Fotos geprüft)', 14, 'nicht veröffentlicht', None,
         'eigene Paperangabe: „scharfe, detaillierte 3D-Formen" (Eigenangabe, nicht unabhängig geprüft)',
         'Nein — keine eigenen Gewichte, kein eigener Lauf auf unserer Hardware',
         'github.com/Tencent-Hunyuan/Hunyuan3D-2.1 Issue #111; arxiv.org/html/2506.15442 (Technical Report); '
         'datayuan.substack.com „Hunyuan 3D Studio"; intl.cloud.tencent.com/document/product/1284'),
        ('Meshy.ai (Meshy-7)', 'Nein — vollständig geschlossen, kein technisches Paper', 'nicht veröffentlicht',
         '2K-Texturen laut Vergleichsquelle (Geometrieauflösung nicht veröffentlicht)',
         'nicht recherchiert', None, 'nicht veröffentlicht', None,
         'Quellen widersprechen sich: eine nennt saubere, produktionsreife Topologie als Stärke, eine andere „oft '
         'unsaubere Meshes, die manuelle Retopologie brauchen" — siehe Hilfe → Recherche → meshy.ai',
         'Nein', 'digitalcitizen.life Meshy-Review; 3daistudio.com; meshy.ai-Blog'),
        ('Tripo3D (Tripo AI)', 'Nein — geschlossen', 'nicht veröffentlicht', 'bis 4K-Texturen laut Vergleichsquelle',
         'rund 20 s laut Vergleichsquelle', 20, 'nicht veröffentlicht', None,
         'Vergleichsquelle: führend bei Auflösung und Vielseitigkeit, starke geometrische Präzision',
         'Nein', 'medium.com „best ai 3d model generators in 2026"; pasqualepillitteri.it Tripo-AI-Review'),
        ('Rodin Gen-2.5 (Hyper3D)', 'Nein — geschlossen', 'nicht veröffentlicht',
         'Widerspruch zwischen Quellen: eine nennt zweistellige Mio. Polygone, eine andere nur „1080p-äquivalente" '
         'Auflösung als Höchstwert',
         'rund 4 s laut einer Quelle (nur Geometrie, nicht die vollständige Textur-Pipeline)', 4,
         'nicht veröffentlicht', None,
         'Fokus Fotorealismus/Charaktere; eine Quelle: kein Generalist für ganze Spielumgebungen',
         'Nein', 'neural4d.com/zh/features-Vergleich; droid.tools „Best ai 3d modeling tool 2026"'),
        ('Direct3D-S2 (Forschungsmodell, offen)', 'Ja — Code + Gewichte frei (Mai 2025, NeurIPS 2025), Demo-Space',
         'nicht recherchiert', '1024³-Volumen („Spatial Sparse Attention")',
         '3,9×/9,6× schnellerer Vorwärts-/Rückwärtsdurchlauf als die Vorgängerarchitektur bei 1024³ auf 8 statt '
         '≥ 32 GPUs; Version 1.1 nochmals 12,2×/19,7× schneller als FlashAttention-2 — Trainings-/Inferenz-Geschwindigkeit, '
         'keine Sekundenzahl je Modell', None, 'nicht veröffentlicht', None,
         'eigener Papertitel: „überlegene Ausgabequalität" (Eigenangabe, nicht unabhängig geprüft)',
         'Nein — ungetestet, siehe Hilfe → Recherche → meshy.ai', 'arxiv.org/html/2505.17412; NeurIPS-2025-Poster'),
        ('Pixal3D (TencentARC)', 'Ja — MIT', 'nicht recherchiert (TRELLIS.2-Backbone + Rückprojektion)',
         'TRELLIS.2-Backbone; bei uns neu gerechnet mit 8192er Textur, 300.000 Flächen',
         'bei uns gemessen 254–444 s je Auftrag (GPU-Modus)', 349, '46 GB gesamt (Einzelbild ~24 GB, Multi-View ~22 GB)',
         46.0,
         'Autoren: „präzisere Kanten, weniger Halluzinationen" — an unseren eigenen Fotos NICHT geprüft (eigene '
         'Einordnung in architektur2d3dfaktennetz.py)',
         'Ja — wählbar als Formmodell „mesh" (Pixal3D / Pixal3D Mehrbild)', 'eigene Messung (architektur2d3dfaktennetz.py)'),
    ]

    @classmethod
    def zeilen(cls):
        felder = ('modell', 'offen', 'parameter', 'aufloesung', 'geschwindigkeit', 'geschwindigkeit_s', 'groesse',
                  'groesse_gb', 'qualitaet', 'bei_uns', 'quelle')
        return [dict(zip(felder, z)) for z in cls.ZEILEN]

    @classmethod
    def kontext(cls):
        return {'modellvergleich_stand': cls.STAND, 'modellvergleich': cls.zeilen()}
