# -*- coding: utf-8 -*-
"""Blendimportsegmentierung — Schritt „segmentierung“ des Wegs „netz“: Sapiens trennt Haut, Kleidung und Haar am verschmolzenen Netz (11.10.2026).

Edgar am Zauberer (`2026.10.11.20.03.34`), dessen Figur die Form der Robe trug: „Womit machst du die Kleiderabschätzung, Sapiens hat doch schon mal besser funktioniert für Kleider und Haare??“ — und
die Figur sei viel zu dick, „du hast ja Abmessungen des Meshes“. Gemessen am Lauf: „Mesh to 3D“ nimmt den Hautton von den KAHLEN Stellen (Gesicht, Hände, Unterarme, Unterschenkel); beim Zauberer liegt keine
davon frei (Robe bis zum Boden, Bart, Handschuhe) — „Kein Hautmodell“, es galt die alte Regel mit dem Hautton des Rumpfs, also der Robe (44, 41, 40). Die Robe war damit „Haut“, die Figur wurde an ihre
Außenseite gezogen: massig, 189,3 cm, mit dem Umriss der Robe. Die Maße des Netzes sind die der Robe — sie sagen nichts über den Körper darunter.

Was „2D3D Kleider“ dagegen hat, ist der Schritt „Segmentierung“ (`Engine2d3dKleidersegmentierung`, Regel `engine2d3dkleider-segmentierung.md`): Sapiens zerlegt Fotos in 28 Klassen, die Etiketten gehen
mit der Fotoprojektion und Verdeckung auf die Flächen des Netzes (`arbeit/sapiens_flaechen.npz`). Ein verschmolzenes Netz hat keine Fotos — aber Bilder aus bekannter Kamera: dieser Schritt rendert das Netz
mit seiner Textur aus den vier Ansichten der Fotoprojektion (`Mesh3dansicht.rundum`, orthografisch, Alpha = Netz) und gibt sie derselben Rechnung. Das Modell ist Sapiens2 0.4B (`sapiens2-0.4b`): am
Zauberer ließ Sapiens-1B 96,6 % der freigestellten Robe ohne Etikett, Sapiens2 5,1 % (gemessen 09.10.2026, `segmentierung-fashn-sapiens2.md`, an Renderings eines früheren Auftrags).

Die Stimmen nutzt danach der Auftrag „Mesh to 3D“ (`uebernehmen`/`fuer_figur`): die Kleidungsmaske (`Meshfigurkleidung._sapiens`), die Haarmaske (`Sapienshaar`, Quelle „beide“) und — neu — der Hautton, wenn die
kahlen Stellen nicht reichen (`Meshfigurhautmodell.aus_flaechen`, `Meshfigurdaten.hautkarte`). Ablage: `arbeit/segmentierung/` (Renderings `<rolle>.png`, Überlagerungen `ueberlagerung_<rolle>.webp`,
`segmentierung.json`, `sapiens_flaechen.npz`, `auftrag.json`). Fehlt etwas oder passt es nicht zum Netz im Eingang, steht der Grund im Bericht und „Mesh to 3D“ rechnet wie vorher — nie ein stilles Zurückfallen.
"""

import json
import logging
import os
from types import SimpleNamespace

import numpy as np
from django.conf import settings
from django.utils import timezone

from .blendimportbegriffe import Blendimportbegriffe
from .engine2d3dkleidersegmentierung import Engine2d3dKleidersegmentierung
from .engine2d3dkleidersegmentierungsoptionen import Engine2d3dKleidersegmentierungsoptionen
from .mesh3dansicht import Mesh3dansicht
from .mesh3dnetzansicht import Mesh3dnetzansicht

logger = logging.getLogger('core')

__all__ = ['Blendimportsegmentierung']


class Blendimportsegmentierung(Engine2d3dKleidersegmentierung):
    ORDNER = 'segmentierung'
    DATEI = 'sapiens_flaechen.npz'
    #: Das Modell und die Wahlen für den Weg „netz“: Kleidung und Haar aus Sapiens (Haar „beide“: Farbe ODER Sapiens, die geschützten Zonen bleiben geschützt), Sapiens2 0.4B für gerenderte Kleidung.
    EINSTELLUNGEN = {'verwenden': 'an', 'haar': 'beide', 'modell': 'sapiens2-0.4b'}

    def __init__(self, ablage, melden, angehalten=lambda: False, abbrechen=RuntimeError):      # noqa: D107 — kein `super().__init__`: der liest den Auftrag „2D3D Kleider“
        self.ablage = ablage
        self.optionen = Engine2d3dKleidersegmentierungsoptionen.pruefen(self.EINSTELLUNGEN)
        self.job = SimpleNamespace(kennung=ablage.kennung)
        self.lauf = SimpleNamespace(melden=melden, angehalten=angehalten, Angehalten=abbrechen, ab=None)
        self._ergebnis = None
        self._glb = None
        #: Das Netz, über das der Runner abstimmt (`_glb` selbst oder sein Abstimm-Netz), und der Ordner, in den er die Stimmen schreibt.
        self._netz = None
        self._arbeit = None
        self._bilder = []
        #: Bericht von `Blendimportbegriffe` (SAM 3): `{begriffe: {…}, …}` oder `{fehler: …}`; None, solange er nicht lief.
        self._begriffe = None

    def ordner(self):
        return self.ablage.arbeit(self.ORDNER)

    def auftragsdatei(self):
        return self.ordner() / 'auftrag.json'

    # ---------------------------------------------------------------- Ablauf

    def rechnen(self, glb):
        """Das Netz aus vier Ansichten rendern, Sapiens darüber laufen lassen, die Stimmen auf die Flächen legen → der Bericht für `stand.ergebnis.segmentierung`.

        Ein sehr dichtes Netz (Tripo: 1,9 Mio. Dreiecke, jedes kleiner als ein Pixel — gemessen am Zauberer: 28.872 von 1.935.797 Flächen bekamen die nötigen 4 Pixel Stimme, 1,5 %) stimmt über ein
        vereinfachtes Abstimm-Netz ab (`PROXY_FLAECHEN`, dieselben Koordinaten); jede Fläche des vollen Netzes übernimmt die Stimmen der nächsten Fläche des Abstimm-Netzes (`_uebertragen`)."""
        ordner = self.ordner()
        ordner.mkdir(parents=True, exist_ok=True)
        self._glb = glb
        self.lauf.melden(0.0, 'Segmentierung: Netz aus vier Ansichten rendern')
        ziele = {rolle: ordner / ('%s.png' % rolle) for rolle in self.ROLLEN}
        Mesh3dansicht.rundum(glb, ziele)
        self._bilder = [{'datei': '%s.png' % rolle, 'stamm': rolle, 'rolle': rolle, 'png': str(pfad)} for rolle, pfad in ziele.items()]
        self._netz, self._arbeit, proxy = glb, ordner, None
        if self.flaechen_von(glb) > self.PROXY_AB:
            self.lauf.melden(0.05, 'Segmentierung: Abstimm-Netz mit %d Flächen' % self.PROXY_FLAECHEN)
            self._netz, self._arbeit = ordner / 'abstimmnetz.glb', ordner / 'abstimmnetz'
            self._arbeit.mkdir(exist_ok=True)
            proxy = self._abstimmnetz(glb)
        self.lauf.melden(0.1, 'Segmentierung: Sapiens')
        self.ausfuehren()
        # Die Bestandteile über Textbegriffe (SAM 3, `Blendimportbegriffe`): Stab, Bart, Tasche … — dasselbe Abstimm-Netz, dieselben Renderings. Ein Zusatz: scheitert er, steht der Grund im Bericht.
        self.lauf.melden(0.88, 'Segmentierung: Bestandteile (SAM 3)')
        self._begriffe = Blendimportbegriffe(self).ausfuehren()
        if proxy is not None:
            self.lauf.melden(0.97, 'Segmentierung: Stimmen auf das volle Netz übertragen')
            self._uebertragen(glb)
        return self._bericht(proxy)

    #: Ab so vielen Dreiecken stimmt ein Abstimm-Netz ab (darunter deckt jede Fläche mehrere Pixel), und so viele hat es (Setzung: bei 56.560 cm² Netzfläche rund 3,8 cm² je Fläche, ~100 Pixel).
    PROXY_AB = 400_000
    PROXY_FLAECHEN = 150_000
    #: Fassung des Verfahrens, das das Abstimm-Netz baut (zusammen mit `Mesh3dnetzansicht.FASSUNG` im Stempel von `abstimmnetz.json`).
    PROXY_FASSUNG = 1

    def _abstimmnetz(self, glb):
        """`(Dreiecke, Punkte)` des Abstimm-Netzes. Es ist eine reine Funktion des Körpernetzes (pymeshlab, EIN Kern: am Zauberer rund 40–60 s im Lauf, 12.10.2026, py-spy): gehört `abstimmnetz.glb` schon zu
        DIESEM Netz und diesen Maßen (`abstimmnetz.json`: Stempel von `glb`, Flächenzahl, Fassungen), wird es nicht noch einmal gebaut. Sonst vereinfachen und den Stempel ablegen — der Stempel nach der Datei, damit
        ein abgebrochener Bau nie als fertig gilt."""
        stempel = {'glb': self.stempel(glb), 'flaechen': self.PROXY_FLAECHEN, 'fassung': [self.PROXY_FASSUNG, Mesh3dnetzansicht.FASSUNG]}
        vermerk = self.ordner() / 'abstimmnetz.json'
        if self._netz.is_file() and vermerk.is_file():
            try:
                gemerkt = json.loads(vermerk.read_text(encoding='utf-8'))
                if gemerkt.get('stempel') == stempel:
                    return int(gemerkt['groesse'][0]), int(gemerkt['groesse'][1])
            except (OSError, ValueError, KeyError, IndexError, TypeError):
                pass
        vermerk.unlink(missing_ok=True)
        proxy = Mesh3dnetzansicht.vereinfachen(glb, self._netz, self.PROXY_FLAECHEN, farben=False)
        teil = vermerk.with_name(vermerk.name + '.teil')
        teil.write_text(json.dumps({'stempel': stempel, 'groesse': [proxy[0], proxy[1]]}), encoding='utf-8')
        os.replace(teil, vermerk)
        return proxy

    @staticmethod
    def flaechen_von(glb):
        """Zahl der Dreiecke einer GLB — aus dem JSON-Block (Indexzahl der Primitive), ohne das Netz zu laden."""
        from .blendimportweg import Blendimportweg

        daten = Blendimportweg.glb_json(glb)
        zugriffe = daten.get('accessors') or []
        return sum(zugriffe[p['indices']]['count'] // 3 for m in daten.get('meshes') or [] for p in m.get('primitives') or [] if 'indices' in p)

    def beschreibung(self):
        return {
            'kennung': self.ablage.kennung, 'netz': str(self._netz), 'bilder': self._bilder, 'hf_home': str(settings.HF_HOME_DIR),
            'ordner': {'segmentierung': str(self.ordner()), 'arbeit': str(self._arbeit)},
            'optionen': Engine2d3dKleidersegmentierungsoptionen.rechenoptionen(self.optionen),
        }

    def _uebertragen(self, glb):
        """Die Stimmen des Abstimm-Netzes (`abstimmnetz/sapiens_flaechen.npz`) auf die Flächen des vollen Netzes legen → `sapiens_flaechen.npz` im Ordner des Schritts, Stempel auf `glb`.
        Je Fläche des vollen Netzes die nächste Flächenmitte des Abstimm-Netzes; eine Fläche, die dort ungesehen blieb, bleibt es."""
        from scipy.spatial import cKDTree

        voll, klein = self._flaechenmitten(glb), self._flaechenmitten(self._netz)
        _, nah = cKDTree(klein).query(voll, workers=-1)
        # Sapiens-Stimmen und die Stimmen der Begriffe (SAM 3, `teile_flaechen.npz`) gehen auf dieselbe Weise vom Abstimm-Netz auf das volle Netz.
        for datei, felder in ((self.DATEI, ('klassen', 'stimmen', 'hintergrund', 'ansichten')), (Blendimportbegriffe.DATEI, ('stimmen', 'pixel', 'ansichten'))):
            if not (self._arbeit / datei).is_file():
                continue
            with np.load(self._arbeit / datei) as d:
                kopie = {k: d[k] for k in d.files}
            for feld in felder:
                kopie[feld] = kopie[feld][nah]
            kopie['netz'] = np.array(self.stempel(glb))
            kopie['flaechen'] = len(voll)
            np.savez_compressed(self.ordner() / datei, **kopie)

    @staticmethod
    def _flaechenmitten(glb):
        """(F, 3) Flächenmitten in der Reihenfolge der Flächen, die der Runner liest (`_run_sapiens._netz`: trimesh, ohne Zusammenführen, mit den Knoten-Transformationen)."""
        import trimesh

        roh = trimesh.load(str(glb), force='scene', process=False)
        netz = roh.to_geometry() if hasattr(roh, 'to_geometry') else roh.dump(concatenate=True)
        return np.asarray(netz.vertices, dtype=np.float64)[np.asarray(netz.faces)].mean(axis=1)

    def _abschluss(self):
        kennzahlen = (self._ergebnis or {}).get('kennzahlen') or {}
        logger.info('Mesh-3D %s: Segmentierung fertig (%s Fotos, %s von %s Flächen gesehen)', self.ablage.kennung, self._ergebnis.get('bilder'),
                    kennzahlen.get('flaechen_gesehen'), kennzahlen.get('flaechen_gesamt'))

    def _bericht(self, proxy=None):
        """Was die Karte der Jobseite zeigt: je Ansicht Silhouetten-IoU, gesehene Flächen, Anteile und die Überlagerung; dazu die Kennzahlen des Runners (bei einem Abstimm-Netz an DEM gerechnet:
        `abstimmnetz` nennt seine Flächen und Punkte)."""
        stand = json.loads((self.ordner() / 'segmentierung.json').read_text(encoding='utf-8'))
        ansichten = [{k: e.get(k) for k in ('rolle', 'iou', 'sichtbar', 'anteile', 'ueberlagerung', 'haarfarbe')} for e in stand.get('bilder', [])]
        return {'stand': timezone.now().isoformat(), 'optionen': dict(self.optionen), 'ansichten': ansichten, 'kennzahlen': stand.get('kennzahlen') or {},
                'abstimmnetz': {'flaechen': proxy[0], 'punkte': proxy[1]} if proxy else None,
                'begriffe': self._begriffe,
                'quelle': {'koerper': self.stempel(self._glb)}, 'datei': self.DATEI}

    # --------------------------------------------------- Stempel und Auftrag

    @staticmethod
    def stempel(pfad):
        """`[Bytes, Änderungszeit]` — woran die Stimmen erkennen, zu welchem Netz sie gehören (`Sapiensstand.quelle`)."""
        stat = os.stat(str(pfad))
        return [stat.st_size, stat.st_mtime_ns]

    @classmethod
    def fuer_figur(cls, ablage, stand, job_ablage, glb):
        """Die Stimmen in den Auftrag „Mesh to 3D“ legen (`arbeit/sapiens_flaechen.npz`, Stempel auf das Netz in SEINEM Eingang) → die Einstellungen für seinen Lauf (`lauf.sapiens_*`) oder `None`.

        `None` mit Grund im Protokoll, wenn der Schritt nicht lief, die Stimmen fehlen oder nicht zu `glb` (dem Körpernetz dieses Imports) gehören — „Mesh to 3D“ rechnet dann wie bisher
        (Farbe und Lage, nur kahle Stellen). Das Netz im Eingang ist eine Kopie von `glb`; die Größe muss gleich sein, die Änderungszeit ersetzt den Stempel."""
        bericht = (stand.get('ergebnis') or {}).get('segmentierung')
        if not isinstance(bericht, dict) or not bericht.get('datei'):
            logger.warning('Mesh-3D %s: keine Segmentierung — „Mesh to 3D“ rechnet ohne Sapiens', ablage.kennung)
            return None
        quelle = ablage.arbeit(cls.ORDNER) / bericht['datei']
        eingang = job_ablage.netzdatei('koerper')
        grund = ''
        if not quelle.is_file():
            grund = 'Datei fehlt'
        elif eingang is None:
            grund = 'kein Netz im Eingang des Auftrags'
        elif bericht.get('quelle', {}).get('koerper') != cls.stempel(glb):
            grund = 'das Körpernetz hat sich seit der Segmentierung geändert'
        elif cls.stempel(eingang)[0] != cls.stempel(glb)[0]:
            grund = 'das Netz im Eingang weicht vom Körpernetz ab'
        if grund:
            logger.warning('Mesh-3D %s: Segmentierung nicht benutzt (%s) — „Mesh to 3D“ rechnet ohne Sapiens', ablage.kennung, grund)
            return None
        with np.load(quelle) as d:
            daten = {k: d[k] for k in d.files}
        daten['netz'] = np.array(cls.stempel(eingang))
        ziel = job_ablage.arbeit(cls.DATEI)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(ziel, **daten)
        # Die Stimmen der Begriffe (SAM 3) gehören zum selben Netz und gehen mit — fehlen sie, rechnet „Mesh to 3D“ ohne Bestandteile (kein Fehler).
        teile = ablage.arbeit(cls.ORDNER) / Blendimportbegriffe.DATEI
        if teile.is_file():
            with np.load(teile) as d:
                gleiche = {k: d[k] for k in d.files}
            gleiche['netz'] = daten['netz']
            np.savez_compressed(job_ablage.arbeit(Blendimportbegriffe.DATEI), **gleiche)
        return dict(bericht.get('optionen') or {})
