# -*- coding: utf-8 -*-
"""Die djangoBase-Konfiguration — Menü, Themen, Logs, Tests, Review, Skills.

Aus `ui/settings.py` herausgelöst (17.08.2026): 148 Zeilen ein einziges
Wörterbuch. Es beschreibt, was djangoBase für dieses Projekt anzeigt — mit dem
Menü, den fünf Themen-Paletten, den Logquellen, den Testbefehlen je Art, den
Review-Partnern und den Ausschlusslisten der Analysewerkzeuge.

Die Kommentare im Wörterbuch bleiben, wo sie sind: Jede der Listen hat einen
Grund, und der steht neben dem Eintrag, nicht in einer Datei daneben.
"""

from .protokoll import LOG_DIR
from .djangobase_menue import EINSTELLUNGEN_EXTRA, MENUE
from .djangobase_tests import TEST_BEFEHLE, TEST_BEREICHE
from ..review import REVIEW_BEREICHE
from .wurzeln import (BASE_DIR, HUMANBODY_ROOT, TOOLS_ROOT, VERSION,
                      VIDEOTOBVH_ROOT)

# djangoBase — wiederverwendbare Infra (Sidebar-Layout, Hilfe: Logs/Versionen/
# Tests, Einstellungen). Installiert als editable Package aus A:\shared\djangoBase.
# Repos mit absolutem Pfad + leerem Slug ("") -> djangoBase leitet den GitHub-
# Slug aus dem lokalen origin-Remote ab (keine Slugs hardcodiert).
DJANGOBASE = {
    'titel': 'HumanBody',
    # Die aktuelle Version steht immer im UI (Projektkonvention) — djangoBase
    # zeigt sie unten in der Seitenleiste. Sie kam bis zum 28.08.2026 nicht
    # hier an: `wurzeln.VERSION` war gesetzt, die Sidebar zeigte trotzdem
    # nichts (Konformitätsprüfung `test_version_ist_gesetzt`).
    'version': VERSION,
    # Ziehgriff an der Seitenleiste. djangoBase bringt ihn fertig mit; ohne
    # den Schalter ließ sich die Leiste nicht in der Breite ziehen.
    'resizable_sidebar': True,
    'logo_icon': 'bi-person-walking',
    # Das Tab-/Lesezeichen-Symbol. `logo_icon` ist NUR das Sidebar-Zeichen
    # (Bootstrap-Icon-Schrift) — der Browser braucht eine echte Bilddatei, sonst
    # zeigt er sein graues Ersatzblatt. djangoBase haengt daraus in _shell.html
    # ein <link rel="icon"> ein. Die Fassung steckt im DATEINAMEN, nicht in einer
    # `?v=`-Anhaengung: `{% static %}` kodiert das Fragezeichen zu %3F. Chrome
    # merkt sich Symbole je Seiten-URL sehr lange — auch das FEHLENDE; nur eine
    # neue Adresse holt es sicher neu. Bei Aenderungen am Bild hochzaehlen.
    'favicon': 'img/favicon-v1.svg',
    # Hilfe -> Skills: Ordner, die die Analysewerkzeuge auslassen. Ohne diese
    # Liste kommen die meisten Befunde aus fremdem Referenzcode (CharMorph,
    # MB-Lab) und aus alten Staenden — die eigenen gehen darin unter.
    # 'vendor' ist three.js (Fremdbibliothek), 'theatre' die Vite-Ausgabe
    # (static/theatre/theatre-app.js entsteht aus TheatreJS/src/) — beides ist
    # kein eigener Quelltext und darf in den Befunden nicht auftauchen.
    #
    # DER SCHLUESSEL HIESS BIS ZUM 18.08.2026 `skills_ausser` — UND DEN LIEST
    # djangoBase NIRGENDS (`grep -rn skills_ausser` in A:\shared\djangoBase:
    # kein Treffer). Gewirkt hat nur `skills_ignorieren`, und dort stand allein
    # 'TestCharakter'. Die Werkzeuge haben also die ganze Zeit three.js, die
    # Vite-Ausgabe, Backups und alte Staende mitgemessen; `doppelcode` meldete
    # deshalb Bloecke aus `static/theatre/theatre-app.js` — dem Bundler-Ergebnis.
    #
    # `TestCharakter/` ist ein Vergleichs-Sandkasten, kein Quelltext dieses
    # Projekts: `charmorph_ref/` ist eine HERUNTERGELADENE Kopie des
    # CharMorph-Addons, `humanbody_core/` ein alter Stand unserer eigenen
    # Bibliothek — beides, um sie gegen die heutige Fassung zu halten. Ohne den
    # Ausschluss meldete `doppelrumpf` vier von sechs Gruppen genau dort
    # (17.08.2026). Fremdcode in der Befundliste verdeckt die eigenen Funde.
    #
    # `idol`, `sith`, `texformer`, `textured_smplx` (31.08.2026): vier
    # EINGELAGERTE Forschungsprojekte unter `HumanBody/PhotoToTexture/`,
    # zusammen 135 der 142 Python-Dateien dieses Ordners. Eigen sind dort
    # nur die sieben Wrapper daneben (`*_wrapper.py`, `bake_texture.py`).
    # Ohne den Ausschluss stammten die ersten vier Befunde des Werkzeugs
    # `protokoll` aus `idol/lib/models/renderers/` und `textured_smplx/` —
    # fremder Code, den zu aendern niemand vorhat.
    # `skeleton_presets` (31.08.2026): 13 Dateien in `HumanBody/data/`, die
    # zwar auf `.py` enden, aber kein Programm sind — Vorgabedateien fuer ein
    # Blender-Addon, die mit `import bpy` beginnen und im ganzen Projekt
    # NIRGENDS erwaehnt werden. Jede von ihnen ordnet dieselben Rigify-Knochen
    # einem anderen Fremdformat zu; sie sehen sich deshalb notwendig aehnlich.
    # `doppelcode` meldete daraus 20 von 68 Befunden — an Dateien, die unter
    # `data/` liegen und laut CLAUDE.md ohnehin nicht angefasst werden duerfen.
    'skills_ignorieren': ['TestCharakter', 'alt', '_merge_tmp2', 'Backup',
                          'ProjektTemp', 'debug', 'tools', 'vendor', 'theatre',
                          'theatre-studio', 'skeleton_presets',
                          'idol', 'sith', 'texformer', 'textured_smplx'],
    # WELCHE MODULFUNKTIONEN EIN FREMDER RAHMEN BEIM NAMEN RUFT
    # ========================================================
    # `freie-funktionen` meldete zehn Module des Blender-Addons, weil dort
    # `register`/`unregister` auf Modulebene stehen — mit dem Vorschlag,
    # sie in eine Klasse zu heben. Wer dem folgt, macht das Addon kaputt:
    # Blender ruft genau diese beiden Namen AM MODUL auf (das Addon-
    # Protokoll, `bpy.utils.register_class` haengt darunter), und
    # `HumanBodyBlender/__init__.py` reicht sie an die zehn Teilmodule
    # weiter. Als Methoden ruft sie niemand mehr.
    #
    # Dieselbe Fehlerklasse wie „`Command` 23x vergeben" — ein Befund, der
    # zum Kaputtmachen auffordert. Django-Einstellungen koennen von Blender
    # nichts wissen; deshalb steht die Angabe hier.
    'rahmenfunktionen': ['register', 'unregister'],
    # WELCHE VERZEICHNISSE NUR GELESEN WERDEN DUERFEN (Werkzeug `nur-lesen`)
    # ======================================================================
    # Aus CLAUDE.md: „NEVER write to `HumanBody/data/` or
    # `HumanBodyBlender/data/` — these are production assets (morphs, meshes,
    # weights, skeleton). Read only." Belegter Schaden: Die maennlichen `.npy`
    # schrumpften einmal von 437 KB auf 218 KB — halbe Vertexzahl, Charakter
    # zerstoert, ohne Fehlermeldung.
    #
    # `ausser` nennt die Unterordner, die der Benutzer ueber die Oberflaeche
    # SEHR WOHL fuellt: gespeicherte Figuren, die BVH-Bibliothek, Studio-
    # Projekte, Foto-Ergebnisse, Posen, Kleider. Ohne diese Liste meldete das
    # Werkzeug jeden Speichern-Knopf des Projekts.
    'daten_nur_lesen': {
        'wurzeln': ['HumanBody/data', 'HumanBodyBlender/data'],
        'ausser': ['models', 'animations', 'studio_projects', 'assetsInstance',
                   'photoTo3D', 'poseData', 'garment_library',
                   'theatre_presets', 'hairstyles', 'output', 'tmp',
                   'TestCharakter', 'charmorph_data', 'music', 'test'],
        'einstellungen': ['HUMANBODY_DATA_DIR', 'HUMANBODY_BVH_DIR',
                          'BLENDER_BVH_DIR'],
    },
    'farben': {
        'sidebar_bg': '#1a1a2e',     # = --bg-secondary (style.css)
        'sidebar_light': '#16213e',  # = --bg-card  (Hover/Active-Fill)
        'sidebar_dark': '#0f0f1a',   # = --bg-primary (Topbar)
    },
    # 5-Modi-Theme-Palette (slug, label, Akzent-Punkt im Dropdown). Aktiviert
    # den Theme-Switcher im Topbar (base_app.html). Die Farben pro Modus liegen
    # in static/css/theme.css (body[data-theme="X"]) — sie überschreiben die
    # gleichnamigen Variablen aus style.css:root, sodass ALLE Seiten umfärben.
    'theme_modes': [
        ('dark',   'Dark',   '#e94560'),   # HumanBody-Akzent
        ('light',  'Light',  '#1976d2'),
        ('cyber',  'Cyber',  '#00f0ff'),
        ('forest', 'Forest', '#4caf50'),
        ('sunset', 'Sunset', '#ff7a45'),
    ],
    'theme_default': 'dark',
    # theme.css auch auf die djangoBase-eigenen Seiten (Hilfe/Einstellungen)
    # laden, damit der Theme-Switch dort genauso wirkt (?v={{ JS_VERSION }}).
    'extra_css': ['css/theme.css'],
    'log_verzeichnis': LOG_DIR,
    'log_sources': [
        ('all', 'Alle Quellen — chronologisch', None, None),
        ('django', 'Django-Server', 'django.log', None),
        ('core', 'Character / API', 'core.log', None),
        ('pipeline', 'Video-to-BVH', 'pipeline.log', None),
        ('client', 'Client (JS)', 'client.log', None),
        # 'error.log', NICHT 'errors.log' (Befund 30.08.2026). Seit der
        # Umstellung auf dblog.config am 28.08.2026 schreibt der Handler
        # 'error_file' nach error.log; hier stand weiter der alte Name.
        # Gemessen: Die Quelle zeigte 3.268 Bloecke aus einem
        # 19-Minuten-Fenster vom 27.08. und nichts danach, waehrend die
        # 317 Eintraege des laufenden Tages in KEINER Quelle standen.
        # Eine Fehlerseite, die alte Fehler zeigt, ist schlimmer als eine
        # leere - sie sieht gefuellt aus.
        ('errors', 'Fehler (aggregiert)', 'error.log', None),
    ],
    'version_pakete': ['django', 'channels', 'daphne', 'numpy', 'scipy', 'trimesh'],
    'repos': [
        ('HumanBodyWeb', '', str(BASE_DIR)),
        ('HumanBody', '', str(HUMANBODY_ROOT)),
        ('HumanBodyBlender', '', str(TOOLS_ROOT / 'HumanBodyBlender')),
        ('VideoToBVH', '', str(VIDEOTOBVH_ROOT)),
    ],
    'test_befehle': TEST_BEFEHLE,
    'tests_djangobase_sichtbar': True,
    'test_bereiche': TEST_BEREICHE,
    # `TestCategory` (tests/base.py) erbt von nichts — `test_pruefcode` hielt
    # die 16 Kategorien deshalb für verwaist („unittest führt sie NIE aus").
    # Tatsächlich macht `core/tests/ui/test_oberflaeche.py` aus jeder eine
    # `django.test.TestCase`-Klasse; die 127 Fälle laufen über die Art `ui`
    # mit (Befund 27.08.2026).
    'test_basen': ['TestCategory'],
    # ----- Hilfe -> Werkzeuge: wo die Proben liegen ------------------------
    # Die Gegenproben (Seitenaufrufe, Cache-Header, LOGGING-Gleichheit,
    # Szenenwerte im Browser) liegen unter `A:/3DTools/Docu/umbau` — eine
    # Ebene ÜBER dem Repo `HumanBodyWeb`, weil sich vier Repos diesen
    # Arbeitsplatz teilen und die Proben über mehrere davon laufen.
    'proben_ordner': [str(TOOLS_ROOT / 'Docu' / 'umbau')],
    # ----- Hilfe -> Review: Code-Review im Gespräch mit einem zweiten Modell --
    # Nemotron ist der starke, kostenpflichtige Partner (~0,6 $/Mio. Token, ein
    # Code-Paket kostet unter einem Cent); Gemma läuft lokal und schickt nichts
    # aus dem Haus, findet dafür deutlich weniger.
    'review_partner': [
        {'slug': 'nemotron', 'name': 'Nemotron 550B', 'ziel': 'online',
         'modell': 'nvidia/nemotron-3-ultra-550b-a55b'},
        {'slug': 'gemma', 'name': 'Gemma 4 26B (lokal)', 'ziel': 'lokal',
         'modell': 'gemma4:26b-a4b-it-qat', 'num_ctx': 32768},
        {'slug': 'qwen', 'name': 'Qwen 3.6 27B (lokal)', 'ziel': 'lokal',
         'modell': 'qwen3.6:27b', 'num_ctx': 32768},
    ],
    # Die Dateien liegen teils im Django-Teil, teils in der Kern-Bibliothek
    # daneben — deshalb ist die Wurzel das gemeinsame Arbeitsverzeichnis.
    'review_wurzel': str(TOOLS_ROOT),
    'review_bereiche': REVIEW_BEREICHE,
    'menu': MENUE,
    'einstellungen_menu': True,
    'hilfe_menu': True,
    'benutzer_verwaltung': False,
    'einstellungen_extra': EINSTELLUNGEN_EXTRA,
    'zugriff': 'none',   # HumanBodyWeb hat (noch) keine Auth -> Hilfe offen
}
