# -*- coding: utf-8 -*-
"""MhProxyAnpassung — ein MakeHuman-Kleidungsstueck auf den Koerper legen.

Aus `mh_proxy_fit` herausgeloest (Umbau 15.08.2026, 204 Zeilen Endpunkt). Der
Weg ist eine feste Folge von Schritten, und genau so steht er jetzt da:

    Zuordnung laden -> Anpasskoerper waehlen -> Netz rechnen -> glaetten ->
    abruecken -> skalieren -> heben -> von T- auf A-Pose -> aus dem Koerper
    schieben

Statt Shrinkwrap benutzt MakeHuman eine feste Zuordnung: Jeder Kleidungsvertex
haengt an drei Koerpervertices mit Gewichten und einem Versatz. Deshalb sitzt
das Ergebnis nur dann richtig, wenn der Anpasskoerper dem entspricht, fuer den
das Stueck entworfen wurde — der MakeHuman-Basiskoerper in T-Pose.
"""
import logging
import os

import numpy as np
from django.conf import settings

from .charakterdaten import Charakterdaten
from .kleidungswerkzeuge import Kleidungswerkzeuge

logger = logging.getLogger('core')


class MhProxyFehler(RuntimeError):
    """Zuordnung fehlt oder ist unbrauchbar."""

    def __init__(self, text, status=400):
        super().__init__(text)
        self.status = status


class MhProxyAnpassung:
    """Passt ein .mhclo-Kleidungsstueck an einen Koerper an."""

    #: Massstab der MakeHuman-Einheiten (Dezimeter) auf Meter.
    MH_MASSSTAB = 0.1
    #: Glaettung nach der T-zu-A-Verschiebung: feste, milde Werte — sie soll
    #: nur die Spruenge an den Knochengrenzen (Schulterspalt) ausbuegeln.
    NACHGLAETTUNG = (3, 0.5)

    def __init__(self, garment_id, geschlecht):
        self.garment_id = garment_id
        self.geschlecht = geschlecht
        self.verzeichnis = self._verzeichnis(garment_id)
        self.proxy = self._proxy_laden()

    # ------------------------------------------------------------------ laden

    @staticmethod
    def _verzeichnis(garment_id):
        name = garment_id.split('/')[-1] if '/' in garment_id else garment_id
        return os.path.join(str(settings.HUMANBODY_DATA_DIR), '..',
                            'garment_library', '.cache', name)

    def _proxy_laden(self):
        from tools.mhclo_proxy import MHCLOProxy
        if not os.path.isdir(self.verzeichnis):
            raise MhProxyFehler('Kleidungsverzeichnis nicht gefunden: %s'
                                % os.path.basename(self.verzeichnis), 404)
        try:
            proxy = MHCLOProxy.from_directory(self.verzeichnis)
        except FileNotFoundError as e:
            raise MhProxyFehler(str(e), 404) from e
        if proxy.vertex_count == 0:
            raise MhProxyFehler('Keine Vertex-Zuordnung in der .mhclo-Datei', 400)
        return proxy

    # -------------------------------------------------------- Anpasskoerper

    def anpasskoerper(self, koerper_vertices, mh_koerper=True):
        """Der Koerper, GEGEN den angepasst wird.

        Mit `mh_koerper` der MakeHuman-Basiskoerper (dafuer sind die Stuecke
        gemacht, sitzt perfekt, kennt aber keine Morph-Regler), sonst der
        gerechnete Koerper (folgt den Reglern, sitzt ungenauer)."""
        if not mh_koerper:
            return koerper_vertices, self._koerperzuordnung()
        pfad = os.path.join(str(settings.HUMANBODY_ROOT), 'MakeHuman',
                            'base_vertices.npy')
        if not os.path.isfile(pfad):
            return koerper_vertices, None
        roh = np.load(pfad)
        anzahl = min(roh.shape[0], koerper_vertices.shape[0])
        # MakeHuman ist Y-oben, das Projekt Z-oben — und in Dezimetern.
        umgerechnet = np.column_stack([roh[:anzahl, 0] * self.MH_MASSSTAB,
                                       -roh[:anzahl, 2] * self.MH_MASSSTAB,
                                       roh[:anzahl, 1] * self.MH_MASSSTAB])
        umgerechnet[:, 2] -= umgerechnet[:, 2].min()
        umgerechnet[:, 2] += koerper_vertices[:, 2].min()
        return umgerechnet, None

    @staticmethod
    def _koerperzuordnung():
        pfad = os.path.join(str(settings.HUMANBODY_ROOT), 'MakeHuman',
                            'mh_to_body_map.npy')
        return np.load(pfad) if os.path.isfile(pfad) else None

    # ----------------------------------------------------------------- rechnen

    def anpassen(self, koerper_vertices, regler):
        """Kleidungsvertices nach allen Schritten — `regler` ist ein
        `Anpassungsregler`."""
        fit_koerper, zuordnung = self.anpasskoerper(koerper_vertices,
                                                    regler.mh_koerper)
        verts = self.proxy.fit_vectorized(fit_koerper, mh_to_body_map=zuordnung)
        verts = self._glaetten(verts, regler)
        verts = self._abruecken(verts, regler.abstand)
        verts = self._skalieren(verts, regler.skalierung)
        verts = self._heben(verts, regler.hoehenversatz)
        if regler.mh_koerper and regler.tpose_verschiebung:
            verts = self._tpose_zu_apose(verts, koerper_vertices)
        verts = self._aus_koerper_schieben(verts, koerper_vertices,
                                           regler.ausschieben_m)
        logger.info('MH-Proxy: %s (%s), Steifigkeit %.2f, Ausschieben %.1f mm, '
                    '%d Vertices', self.garment_id, self.geschlecht,
                    regler.steifigkeit, regler.ausschieben_m * 1000, len(verts))
        return verts

    def _glaetten(self, verts, regler):
        if not regler.glaettet:
            return verts
        return Kleidungswerkzeuge.glaetten(verts, self.proxy.triangulate_faces(),
                                           regler.glaettungsschritte,
                                           regler.glaettungsstaerke)

    @staticmethod
    def _abruecken(verts, abstand):
        """Alle Vertices vom Schwerpunkt weg schieben — Luft zwischen Haut und
        Stoff."""
        if abstand <= 0.0001:
            return verts
        mitte = verts.mean(axis=0)
        richtung = verts - mitte
        laenge = np.linalg.norm(richtung, axis=1, keepdims=True)
        laenge[laenge < 1e-6] = 1.0
        return verts + (richtung / laenge) * abstand

    @staticmethod
    def _skalieren(verts, faktor):
        if abs(faktor - 1.0) <= 0.001:
            return verts
        mitte = verts.mean(axis=0)
        return (verts - mitte) * faktor + mitte

    @staticmethod
    def _heben(verts, versatz):
        if abs(versatz) <= 0.0001:
            return verts
        verts = verts.copy()
        verts[:, 2] += versatz                      # Z ist oben
        return verts

    def _tpose_zu_apose(self, verts, koerper_vertices):
        verschoben = Kleidungswerkzeuge.tpose_zu_apose(verts, koerper_vertices,
                                                       self.geschlecht)
        schritte, staerke = self.NACHGLAETTUNG
        return Kleidungswerkzeuge.glaetten(verschoben,
                                           self.proxy.triangulate_faces(),
                                           iterations=schritte, factor=staerke)

    def _aus_koerper_schieben(self, verts, koerper_vertices, abstand):
        if abstand <= 0.0001:
            return verts
        from GarmentFitter.fitter import _push_outside_body, _compute_vertex_normals
        netz = Charakterdaten.netzdaten(self.geschlecht)
        normalen = _compute_vertex_normals(koerper_vertices, netz.faces)
        return _push_outside_body(verts.astype(np.float64), koerper_vertices,
                                  min_dist=abstand, body_normals=normalen)

    # ------------------------------------------------------------------ Netz

    def dreiecke(self):
        return self.proxy.triangulate_faces()

    def normalen(self, verts):
        return self.proxy.compute_normals(verts).astype(np.float32)
