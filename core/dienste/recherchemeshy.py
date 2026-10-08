# -*- coding: utf-8 -*-
"""Recherchemeshy — Hilfe → Recherche → meshy.ai: was Meshy.ai anders macht als TRELLIS.2/Hunyuan3D, und ob es offene
Modelle mit höherer Auflösung gibt (08.10.2026).

Edgar, 08.10.2026: „schaue nach, was meshy.ai oder trellis / hunyan auf Hugging face besser machen, [...] Edgar kriegt
sowas raus aus den bildern, das ist eine andere, viel besser liga! [...] Was machen die anders?", danach „gibt es
andere Modelle die eine höhere Auflösung haben". Die Renderings, die den Anstoß gaben, liegen unter
`A:\\3DTools\\3DObjects\\models\\Meshy\\Edgar\\` (lokale Dateien, nicht Teil dieser Seite).

Meshy.ai ist geschlossen (kein Quelltext, kein technisches Paper) — anders als TRELLIS.2/Hunyuan3D, die in diesem
Projekt gegen den tatsächlichen Quelltext geprüft werden (`quelltext-vor-nachbau.md`). Jeder Eintrag hier stammt aus
einer Web-Recherche, nicht aus eigenem Code-Lesen; `art` trennt deshalb strikt zwischen `beleg` (mit Quelle, so in der
Quelle wörtlich oder sinngemäß behauptet) und `vermutung` (eigene Einordnung oder ein Widerspruch zwischen Quellen,
nicht aufgelöst — `gemessen-oder-geschlossen.md`).

Eintrag: `(bereich, art, thema, befund, quelle)`.
"""

__all__ = ['Recherchemeshy']


class Recherchemeshy:
    STAND = '08.10.2026'
    ANLASS = ('Edgar, 08.10.2026: Renderings in A:\\3DTools\\3DObjects\\models\\Meshy\\Edgar\\ wirken „eine andere, '
              'viel bessere Liga" als unsere TRELLIS.2-/Hunyuan3D-Ergebnisse — Frage: baut Meshy.ai nur auf TRELLIS '
              'oder Hunyuan auf, und wenn nicht, was macht es anders?')

    ARTEN = [
        ('beleg', 'Beleg', 'mit Quelle belegt — so in der Quelle behauptet, nicht selbst nachgeprüft'),
        ('vermutung', 'Vermutung', 'eigene Einordnung oder ein Widerspruch zwischen Quellen, nicht aufgelöst'),
    ]

    EINTRAEGE = [
        # ------------------------------------------------------------------ Meshy.ai
        ('Meshy.ai', 'beleg', 'Kein Wrapper um TRELLIS oder Hunyuan3D',
         'Meshy ist eine eigene, seit 2021/2023 von Ethan Hu (MIT-PhD, Erfinder der Taichi-GPU-Sprache) entwickelte, '
         'geschlossene Modellreihe (Meshy-1 bis Meshy-7). Keine der gefundenen Quellen nennt TRELLIS oder Hunyuan3D '
         'als Grundlage.',
         '80.lv-Interview mit Ethan Hu; meshy.ai-Blog „Meshy-1"'),
        ('Meshy.ai', 'beleg', 'Mehrstufige Pipeline statt ein Durchlauf',
         'Grobe Form → eigene Verfeinerung → eigene, separat buchbare Textur-Stufe („AI Texturing": Base Color, '
         'Metallic, Roughness, Normal; auch auf fremde Meshes anwendbar). Unsere TRELLIS.2-/Hunyuan3D-Läufe sind EIN '
         'Vorwärtsdurchlauf.',
         'digitalcitizen.life Meshy-Review; meshy.ai-Blog'),
        ('Meshy.ai', 'beleg', 'Mehrbild-Eingabe seit Meshy-5 Standard',
         'Mehrbild-Konditionierung „für genauere Proportionen" ist bei Meshy seit Version 5 die Regel, nicht wie bei '
         'uns gerade erst für den Kopf nachgerüstet (`Trellismehrbild`, Hilfe → Architektur → 2D3D).',
         '3daistudio.com, „meshy ai vs trellis vs tripo"'),
        ('Meshy.ai', 'beleg', 'Rückseiten-Vervollständigung aus riesigem Trainingsdatensatz',
         'Diffusionsbasiertes Modell, „trainiert auf Millionen Meshes", ergänzt die Rückseite aus einem gelernten '
         'Prior statt reiner geometrischer Extrapolation.',
         'meshy.ai-Blog'),
        ('Meshy.ai', 'beleg', 'Compute-Investition',
         'Training auf NVIDIA-H100-Clustern über Lambda; Hu selbst: „the more compute and the more data, the better '
         'the model is trained" — eine Firma mit Millionen-Investment, kein offenes Forschungsmodell.',
         'Lambda-Case-Study (PDF)'),
        ('Meshy.ai', 'vermutung', 'Saubere Topologie — widersprüchliche Quellenlage',
         'Eine Quelle nennt saubere, produktionsreife Topologie als Meshys Stärke gegenüber TRELLIS\u2019 '
         'Gaussian-Splatting-Fokus; eine andere berichtet von oft unsauberen Meshes, die manuelle Retopologie '
         'brauchen. Beide Quellen sind SEO-Vergleichsblogs, keine unabhängige Prüfung gefunden — Widerspruch steht '
         'offen.',
         '3daistudio.com (sauber) gegen digitalcitizen.life (unsauber)'),
        ('Meshy.ai', 'vermutung', 'Warum Ganzkörper-Menschen bei Meshy so viel besser aussehen',
         'Nicht belegt: naheliegend wäre ein eigener, kuratierter Datensatz speziell für bekleidete Menschen (Falten, '
         'Haar, Proportionen) — in keiner Quelle offiziell bestätigt. Meshy hat kein technisches Paper '
         'veröffentlicht.',
         'eigene Einordnung, keine Quelle bestätigt dies'),
        # ------------------------------------------------------------------ Andere Modelle mit hoeherer Aufloesung
        ('Andere Modelle: höhere Auflösung', 'beleg', 'TRELLIS.2 — was wir selbst einsetzen',
         '4 Mrd. Parameter, O-Voxel-Darstellung + Sparse Compression VAE, bis 1536³ Voxelauflösung (unsere Vorgabe '
         'Resolution 1536 = „hoch", Space-Vorgabe 1024 — siehe Hilfe → Architektur → 2D3D).',
         'huggingface.co/microsoft/TRELLIS.2-4B; github.com/microsoft/TRELLIS.2'),
        ('Andere Modelle: höhere Auflösung', 'beleg', 'Hunyuan3D 2.5 — zugänglich, aber ohne eigene Gewichte (Korrektur 08.10.2026)',
         'Released 23.04.2025: eigenes Formmodell „LATTICE" (bis 10 Mrd. Parameter), Geometrieauflösung von 512³ '
         '(Vorgängerversion) auf 1024³ erhöht, 4K-Texturen, Multi-View-PBR. KEINE Gewichte zum Herunterladen (Tencents '
         'GitHub hat nur bis 2.1, auf Hugging Face kein Treffer für 2.5; GitHub-Issues fragen seit Monaten ohne '
         'Antwort nach) — Edgar wies zu Recht darauf hin, dass das NICHT „nicht verfügbar" heißt: Tencent betreibt '
         'unter 3d.hunyuan.tencent.com eine eigene Web-Plattform „Hunyuan 3D Studio" (Text-zu-3D UND Bild-zu-3D, '
         'PBR-Texturen, riggbar, Export FBX/GLB/OBJ/STL) mit einer kostenlosen Stufe und Abos 25–80 $/Monat; '
         'zusätzlich über Tencent Cloud als kostenpflichtige API nutzbar (`SubmitHunyuanTo3DProJob`/'
         '`QueryHunyuanTo3DProJob`, async), auch über Reseller wie Atlas Cloud (rund 0,02 $/Bild). „Nicht offen" '
         'heißt hier also „keine eigenen Gewichte, kein eigener Lauf auf unserer Hardware" — nicht „nicht benutzbar".',
         'github.com/Tencent-Hunyuan/Hunyuan3D-2.1 Issue #111; triposr.org „Hunyuan3D 2.1 vs 2.5 vs 3.0 vs TripoSR"; '
         'datayuan.substack.com „Hunyuan 3D Studio"; rits.shanghai.nyu.edu Hunyuan3D-Überblick; '
         'intl.cloud.tencent.com/document/product/1284; atlascloud.ai/providers/tencent'),
        ('Andere Modelle: höhere Auflösung', 'vermutung', '1536³ gegen 1024³ ist kein direkter Vergleich',
         'Die Kantenlänge eines sparsen Voxelgitters (TRELLIS.2) und Tencents „Geometrieauflösung" eines eigenen '
         'Formmodells (Hunyuan3D 2.5) sind unterschiedliche Architekturen mit unterschiedlicher Messmethode. Welches '
         'Verfahren an unseren eigenen Fotos feinere Ergebnisse liefert, ist NICHT geprüft.',
         'eigene Einordnung'),
        ('Andere Modelle: höhere Auflösung', 'beleg', 'Direct3D-S2 — offen und bislang ungenutzt',
         'Mai 2025 veröffentlicht (NeurIPS 2025), Code und Gewichte frei auf GitHub/Hugging Face, Demo-Space '
         'vorhanden. „Spatial Sparse Attention" erlaubt Training/Inferenz bei 1024³-Volumen auf 8 statt sonst '
         'mindestens 32 GPUs (3,9×/9,6× schnellerer Vorwärts-/Rückwärtsdurchlauf); Version 1.1 nochmals 12,2×/19,7× '
         'schneller als FlashAttention-2. Bislang nicht in unsere Pipeline eingebaut oder an unseren Fotos getestet.',
         'arxiv.org/html/2505.17412 „Direct3D-S2"; NeurIPS-2025-Poster; Hugging-Face-Spaces-Demo'),
        # ------------------------------------------------------------------ Kommerzielle Alternativen
        ('Kommerzielle Alternativen', 'beleg', 'Tripo3D (Tripo AI)',
         'Wirbt mit bis zu 4K-Texturauflösung gegenüber Meshys 2K, Erzeugungszeit rund 20 s; eine Vergleichsquelle '
         'bewertet Tripo als führend bei Auflösung und Vielseitigkeit, Meshy als Spezialist für Texturierung.',
         'medium.com „best ai 3d model generators in 2026"; pasqualepillitteri.it Tripo-AI-Review'),
        ('Kommerzielle Alternativen', 'beleg', 'Rodin Gen-2.5 (Hyper3D)',
         'Eine Quelle nennt zweistellige Millionen Polygone in rund 4 Sekunden (extreme Netzdichte, Fokus '
         'Fotorealismus/Charaktere); eine andere Quelle nennt für dieselbe Firma nur „1080p-äquivalente" Auflösung '
         'als Höchstwert — Widerspruch, nicht aufgelöst.',
         'neural4d.com/zh/features-Vergleich; droid.tools „Best ai 3d modeling tool 2026"'),
        # ------------------------------------------------------------------ Einordnung
        ('Einordnung für unser Projekt', 'vermutung', 'Direct3D-S2 als möglicher nächster Testkandidat',
         'Von allen geprüften Kandidaten ist Direct3D-S2 der einzige, der zugleich offen UND bislang ungenutzt ist. '
         'Das ist ein Fundhinweis für eine mögliche künftige Prüfung, keine Empfehlung — an unseren eigenen Fotos '
         'nicht getestet, kein Vergleichslauf gemacht.',
         'eigene Einordnung, siehe Eintrag oben'),
        ('Einordnung für unser Projekt', 'vermutung', 'Der Rückstand zu Meshy ist vermutlich strukturell',
         'Der sichtbare Qualitätsunterschied (A:\\3DTools\\3DObjects\\models\\Meshy\\Edgar) liegt mutmaßlich vor '
         'allem an Trainingsmaßstab und -daten einer kommerziellen Firma, nicht an einer einzelnen Technik, die sich '
         'kopieren ließe. Nicht geprüft, nur Einordnung aus den obigen Belegen.',
         'eigene Einordnung'),
    ]

    @classmethod
    def eintraege(cls):
        return [{'bereich': b, 'art': a, 'thema': t, 'befund': f, 'quelle': q} for b, a, t, f, q in cls.EINTRAEGE]

    @classmethod
    def kontext(cls):
        eintraege = cls.eintraege()
        reihenfolge, bereiche = [], {}
        for e in eintraege:
            if e['bereich'] not in bereiche:
                reihenfolge.append(e['bereich'])
                bereiche[e['bereich']] = []
            bereiche[e['bereich']].append(e)
        arten = [{'art': a, 'text': text, 'was': was, 'anzahl': sum(1 for e in eintraege if e['art'] == a)}
                 for a, text, was in cls.ARTEN]
        return {
            'stand': cls.STAND, 'anlass': cls.ANLASS, 'anzahl': len(eintraege), 'arten': arten,
            'bereiche': [{'bereich': b, 'eintraege': bereiche[b]} for b in reihenfolge],
        }
