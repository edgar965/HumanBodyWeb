# -*- coding: utf-8 -*-
"""Meshfigurteile — die Bestandteile des Netzes (Stab, Bart, Tasche …) als eigene Objekte in der Ruhelage der Figur (12.10.2026).

Edgar: Bart, Stab und Robe des Zauberers werden nicht erkannt — und: „ich möchte nicht für jedes Modell eine eigene Suchklasse … generischen Code, der solche Sachen beim nächsten Mal automatisch erkennt."
Die Erkennung ist offen (SAM 3 mit Textbegriffen, `Blendimportbegriffe`, Vorrat `Kleidung/begriffsvorrat.json`), die Zerlegung gilt für jeden Begriff gleich (`Kleidung/bestandteile.py`). Diese Klasse entscheidet
an der FIGUR, was aus einem Bestandteil wird — wieder ohne Wissen über einen Gegenstand, nur nach dem Abstand zum Käfig der Figur (derselbe Gedanke und derselbe Code wie beim Blender-Import,
`Blendimportrequisit`):

    flach     liegt an der Oberfläche (Median höchstens `FLACH_M` vom Käfig): Haut, Stoppeln, eine Uhr — kein Objekt; er bleibt, wo er war (ein zweites Netz im Millimeterabstand der Haut flimmerte)
    starr     hängt weit vom Körper und berührt ein Körperteil (ein Stab in der Hand): EINE Starrkörperbewegung dieses Teils, Haltung → Ruhe
    folgt     steht vom Körper ab, hängt aber an ihm (Bart, Tasche): Käfig-Nachbarschaft mit Körperteilen wie die Kleidung (`Meshfigurkleidungsruhelage`)

Je Bestandteil ein Objekt `ergebnis/teil_<begriff>.glb`; die Liste steht in `ergebnis.teile` (Name, Gruppe, Bewegung, Kontaktteil, Datei). Die Objekte der Kleidung und des Haars lassen ihre Flächen weg
(`maske_eigene`), sonst stünde der Stab doppelt in der Bühne. Die Rechnung läuft einmal je Lauf (drei Fäden der Vorschau fragen sie), mit Sperre.
"""

import logging
import threading
from types import SimpleNamespace

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurteile']


class Meshfigurteile:
    DATEI = 'teile_flaechen.npz'
    #: Ein Bestandteil, dessen Punkte im Median näher als das am Käfig der Figur liegen, ist Oberfläche und kein Objekt.
    FLACH_M = 0.008
    _sperre = threading.Lock()
    _vorrat = {}

    # ------------------------------------------------------------- Auswahl

    @classmethod
    def holen(cls, lauf):
        """Die Bestandteile dieses Laufs mit `maske` (F,) bool und `objekt` (`{datei, …}`, `{hinweis}` oder `{fehler}`) — leer, wenn es keine Stimmen gibt. Schreibt die Objekte beim ersten Aufruf."""
        ablage = lauf.ablage
        dateien = [ablage.arbeit(cls.DATEI), ablage.arbeit('genesis_ende.npz'), ablage.arbeit('posiert.npy')]
        if not all(p.is_file() for p in dateien):
            return []
        schluessel = tuple((p.stat().st_size, p.stat().st_mtime_ns) for p in dateien)
        with cls._sperre:
            gemerkt = cls._vorrat.get(lauf.job.kennung)
            if gemerkt and gemerkt[0] == schluessel:
                return gemerkt[1]
            try:
                teile = cls._rechnen(lauf)
            except Exception:  # noqa: BLE001 — ein Zusatz: Kleidung und Haar laufen wie vorher, der Grund steht im Log und im Ergebnis
                logger.exception('Mesh to 3D %s: Bestandteile gescheitert', lauf.job.kennung)
                lauf.job.ergebnis['teile'] = [{'fehler': 'Bestandteile gescheitert, siehe Log'}]
                teile = []
            cls._vorrat[lauf.job.kennung] = (schluessel, teile)
            return teile

    @staticmethod
    def maske_eigene(teile, gruppen=None):
        """(F,) bool — die Flächen der Bestandteile, die ein eigenes Objekt haben (`gruppen`: nur diese Gruppen); None ohne solche."""
        gewaehlt = [t['maske'] for t in teile if (t.get('objekt') or {}).get('datei') and (gruppen is None or t['gruppe'] in gruppen)]
        if not gewaehlt:
            return None
        return np.logical_or.reduce(gewaehlt)

    # ------------------------------------------------------------- Rechnung

    @classmethod
    def _rechnen(cls, lauf):
        from Kleidung.bestandteile import Bestandteile

        from .meshfigurkleidung import Meshfigurkleidung
        from .meshfigurkleidungsruhelage import Meshfigurkleidungsruhelage

        ablage = lauf.ablage
        scan, _ = Meshfigurkleidung(lauf).koerpernetz()
        daten = Bestandteile.laden(ablage.arbeit(cls.DATEI), len(scan.flaechen))
        if daten is None:
            lauf.job.ergebnis['teile'] = []
            return []
        teile = Bestandteile.zerlegen(daten, scan.flaechen, scan.flaecheninhalte() * 1e4)
        with np.load(ablage.arbeit('genesis_ende.npz')) as d:
            kaefig_ruhe = np.asarray(d['punkte'], dtype=np.float64)
            teil = np.asarray(d['teil']) if 'teil' in d.files else None
        ruhelage = Meshfigurkleidungsruhelage(kaefig_ruhe, np.load(ablage.arbeit('posiert.npy')).astype(np.float64), teil)
        lage = SimpleNamespace(h=ruhelage.h, teil=ruhelage.teil, kaefig_posiert=ruhelage.posiert, kaefig_ruhe=ruhelage.entposen.ruhe,
                               finger_bewegt=np.zeros(len(ruhelage.posiert), dtype=bool), ins_netz=lambda p: np.asarray(p, dtype=np.float64), entposen=lambda: ruhelage.entposen)
        from .meshfighaltung import Meshfighaltung

        haltung = Meshfighaltung.holen(lauf)
        from .meshfigurtanzpruefung import Meshfigurtanzpruefung

        pruefung = Meshfigurtanzpruefung.fuer(lauf)
        halter = cls._halterdaten(ablage, len(scan.flaechen), ruhelage)
        for t in teile:
            t['objekt'] = cls._objekt(t, scan, ruhelage, lage, ablage, haltung, pruefung, halter)
        lauf.job.ergebnis['teile'] = [cls._eintrag(t) for t in teile]
        logger.info('Mesh to 3D %s: Bestandteile %s', lauf.job.kennung, ', '.join('%s (%s)' % (t['name'], (t['objekt'] or {}).get('bewegung') or 'Oberfläche') for t in teile) or 'keine')
        return teile

    @staticmethod
    def _halterdaten(ablage, flaechen, ruhelage):
        """`(klassen (F, 28), {'r': Handmitte, 'l': Handmitte})` für `Meshfigurhalter` — die Sapiens-Stimmen des Netzes und die Handmitten der Figur in der Haltung; None ohne Stimmen für dieses Netz."""
        from Genesis9.koerperteile import G9koerperteile

        pfad = ablage.arbeit('sapiens_flaechen.npz')
        if not pfad.is_file():
            return None
        with np.load(pfad) as d:
            klassen = np.asarray(d['klassen']) if 'klassen' in d.files else None
        if klassen is None or len(klassen) != flaechen or ruhelage.teil is None:
            return None
        haende = {s: np.asarray(ruhelage.posiert)[np.asarray(ruhelage.teil) == G9koerperteile.NUMMER[s + '_hand']].mean(axis=0) for s in ('r', 'l')}
        return klassen, haende

    @classmethod
    def _objekt(cls, t, scan, ruhelage, lage, ablage, haltung=None, pruefung=None, halter=None):
        """Das Objekt eines Bestandteils (oder warum keines); `haltung` (`Meshfighaltung`): dazu dasselbe Stück unverändert in der Haltung des Netzes; `pruefung` (`Meshfigurtanzpruefung`): wählt die Gewichte eines mitgehenden Stücks nach der Dehnung im Tanz;
        `halter` (`_halterdaten`): Sapiens-Stimmen und Handmitten — damit entscheidet das Netz, welche Hand ein Stück hält (`Meshfigurhalter`)."""
        from Genesis9.koerperteile import G9koerperteile
        from Kleidung.kleidungsobjekt import Kleidungsobjekt

        from .blendimportrequisit import Blendimportrequisit
        from .blendimportteile import Blendimportteile
        from .meshfigurhalter import Meshfigurhalter

        if not scan.hat_aussehen():
            return {'fehler': 'Netz ohne Textur und ohne Farben je Punkt'}
        genutzt, neu = np.unique(scan.flaechen[t['maske']].reshape(-1), return_inverse=True)
        dreiecke = neu.reshape(-1, 3)
        punkte = scan.punkte[genutzt]
        abstand, _ = ruhelage.entposen.baum.query(punkte, workers=-1)
        t['abstand_median_mm'] = round(float(np.median(abstand)) * 1000.0, 1)
        if float(np.median(abstand)) < cls.FLACH_M:
            return {'hinweis': 'liegt an der Oberfläche (Median %.1f mm vom Käfig)' % t['abstand_median_mm']}
        from .meshfigurhautgewichte import Meshfigurhautgewichte

        requisit = Blendimportrequisit(lage)
        erkannt = requisit.erkennen(punkte)
        if erkannt:
            # Welche Hand hält es? Das Netz entscheidet (Handflächen, die es berühren), nicht das nächste Körperteil der Figur — die Hand der Anpassung steht von Lauf zu Lauf bis zu 8 cm anders (`Meshfigurhalter`).
            haelt = Meshfigurhalter.pruefen(scan, halter[0], punkte, halter[1]) if halter is not None else None
            if haelt:
                name = haelt['seite'] + '_hand'
                erkannt = {**erkannt, 'teil': name, 'nummer': G9koerperteile.NUMMER[name], 'knochen': Blendimportteile.KNOCHEN[name]}
            # Ein langer, dünner Gegenstand in der Hand hängt an der Schwerkraft: die Ausrichtung bleibt, nur die Lage folgt der Hand (`ruhelage_gehalten`); ein Schild oder eine Tasche dreht mit dem Arm.
            gehalten = bool(haelt and haelt['stabfoermig'] and erkannt['teil'] in Blendimportrequisit.TRAEGER)
            ruhe, mass = (requisit.ruhelage_gehalten if gehalten else requisit.ruhelage)(punkte, erkannt['nummer'])
            bewegung = {'bewegung': 'starr', 'kontakt': erkannt['teil'], 'gehalten': gehalten, ('verschiebung_mm' if gehalten else 'rundlauf_mm'): mass}
            if haelt:
                bewegung['haelt'] = {'seite': haelt['seite'], 'zentrum': haelt['zentrum'], 'handflaechen': haelt['flaechen']}
            haut = Meshfigurhautgewichte.starr_von(ablage, len(punkte), erkannt['knochen'])             # ein Stab hängt ganz an dem Knochen, der das Teil führt, das er berührt
        else:
            ruhe = ruhelage.punkte(punkte, dreiecke)
            bewegung = {'bewegung': 'folgt'}
            haut = Meshfigurhautgewichte.kaefig_von(ablage, ruhelage, punkte, pruefung, 'teil_%s' % t['name'], dreiecke, ruhe)
        datei = 'teil_%s.glb' % t['name']
        from .meshfigurobjektflaechen import Meshfigurobjektflaechen

        Meshfigurobjektflaechen.schreiben(ablage, 'teil_%s' % t['name'], t['maske'])      # für die Abnahme: welche Flächen dieses Objekt trägt
        steckbrief = Kleidungsobjekt.schreiben(ablage.ergebnis(datei), ruhe, dreiecke, haut=haut, **scan.aussehen(t['maske'], genutzt))
        objekt = {'datei': datei, **steckbrief, **bewegung}
        if haltung is not None:
            datei_haltung = 'teil_%s_haltung.glb' % t['name']
            objekt['haltung'] = {'datei': datei_haltung, **Kleidungsobjekt.schreiben(ablage.ergebnis(datei_haltung), haltung.punkte(punkte), dreiecke, **scan.aussehen(t['maske'], genutzt))}
        return objekt

    @staticmethod
    def _eintrag(t):
        """Der Teil des Bestandteils, der in `ergebnis.teile` steht (ohne die Maske)."""
        return {k: t[k] for k in ('name', 'begriff', 'gruppe', 'flaechen', 'cm2', 'stuecke', 'treffer', 'bestwert', 'abstand_median_mm', 'objekt') if k in t}
