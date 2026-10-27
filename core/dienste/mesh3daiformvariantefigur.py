# -*- coding: utf-8 -*-
"""Mesh3daiformvariantefigur — Ziel und Ergebnis einer Formvariante als Genesis-Körper, bei Bedarf gerechnet (18.10.2026 abends, `Mesh3daiformvariante`).

Kein Anzeigenetz je Variante nötig: alle Figuren tragen denselben Körper (Netzstufe 0, 27.087 Browserpunkte über `ursprung` auf 25.182 Daz-Punkte, 50.312 Dreiecke) — gemessen 18.10.2026
(`ProjektTemp/_wegwerf/formvariante_reihenfolge_probe.py`): die ersten 27.087 Punkte des Anzeigenetzes der vier Jobs liegen 0,00 mm neben `G9formung(regler).punkte()[ursprung]`, die ersten
50.312 Dreiecke sind der Körper. Also schickt der Server Dreiecke, UV und Material EINMAL (aus dem Anzeigenetz der Grundlage: deren Haut) und je Figur nur die Lage der Punkte.

    Mesh3daiformvariantefigur.regler(vektor, liste)              -> {Name: Wert} geklemmt auf [min, max], |Wert| < 0,01 weg (wie `mesh3dai_form_pruefen.py`)
    Mesh3daiformvariantefigur.paket(lauf, name, was, liste, proben) -> bytes | None   was = 'ziel' | 'mittel' | Probennummer
    Mesh3daiformvariantefigur.koerper(grundlage)                   -> bytes | None   Dreiecke, UV, Material des Körpers

Figur: `G9formung(regler).punkte()` minus `boden()` (steht auf y = 0), in der Ruhelage — dieselbe Rechnung wie die echte Nachrechnung des Laufs. Rund 0,1 s je Figur (gemessen, warm), die erste
nach dem Serverstart lädt Genesis (~1 s). Gemerkt je Lauf, Stand der Vorhersagedatei, Figur und Wahl (`MAX` Einträge, je 0,6 MB).
Abstand Ergebnis ↔ Ziel über die 25.182 Daz-Punkte (RMS, Median, 95 %-Wert in mm) — dieselbe Messgröße wie `formen_pruefung_echt.json`, aber mit dem HEUTIGEN Stand der Morphe gerechnet.

Paket (little endian): uint32 Länge des Kopfes · Kopf (JSON, auf 4 aufgefüllt) · float32 Lage (V·3) bzw. beim Körper uint32 Dreiecke (F·3) · float32 UV (V·2) · int16 Material (F, auf 4 aufgefüllt).
"""

import json
import logging
import struct
import threading
from collections import OrderedDict

import numpy as np

from .mesh3daiflaechennetz import Mesh3daiflaechennetz

logger = logging.getLogger('core')

__all__ = ['Mesh3daiformvariantefigur']


class Mesh3daiformvariantefigur:
    VORHERSAGEN = 'formen_vorhersagen.npz'
    GRUPPEN = ('training', 'pruefung')
    SCHWELLE = 0.01
    MAX = 48
    _ablage = OrderedDict()
    _koerper = {}
    _ursprung = None
    _schloss = threading.Lock()

    @classmethod
    def ursprung(cls):
        if cls._ursprung is None:
            from Genesis9.basisnetz import G9basisnetz

            cls._ursprung = np.asarray(G9basisnetz.netzstufe(0).ursprung, dtype=np.int64)
        return cls._ursprung

    @classmethod
    def regler(cls, vektor, liste):
        """`schwelle` und `faktor` je Regler, wo die Liste sie trägt (Regler-KI: Anfasser im Vektor in cm, in G9formung in m, `mesh3dai_reglerki_ablage.py`)."""
        aus = {}
        for v, r in zip(vektor, liste, strict=True):
            v = float(np.clip(v, r['min'], r['max']))
            if abs(v) >= r.get('schwelle', cls.SCHWELLE):
                aus[r['name']] = v * r.get('faktor', 1.0)
        return aus

    @classmethod
    def vektor(cls, z, name, was, proben):
        """Der Reglervektor zu `was` aus der offenen Vorhersagedatei; None, wenn es ihn nicht gibt (Probe ohne Zeile)."""
        if was == 'ziel':
            return z['%s_soll_form' % name]
        zeilen = {g: z['%s_%s_form' % (name, g)] for g in cls.GRUPPEN if '%s_%s_form' % (name, g) in z.files}
        if not zeilen:
            return None
        if was == 'mittel':
            return np.concatenate(list(zeilen.values())).astype(np.float64).mean(axis=0)
        probe = next((p for p in proben if str(p['nr']) == str(was)), None)
        if probe is None or probe.get('zeile') is None or probe['gruppe'] not in zeilen:
            return None
        return zeilen[probe['gruppe']][probe['zeile']]

    @classmethod
    def punkte(cls, lauf, name, was, liste, proben):
        """(25.182, 3) float64 auf dem Boden und die Zahl der gesetzten Regler — oder (None, 0)."""
        datei = lauf / cls.VORHERSAGEN
        try:
            stand = datei.stat().st_mtime_ns
        except OSError:
            return None, 0
        schluessel = (str(lauf), stand, name, str(was))
        with cls._schloss:
            gemerkt = cls._ablage.get(schluessel)
            if gemerkt is not None:
                cls._ablage.move_to_end(schluessel)
                return gemerkt
        with np.load(datei) as z:
            vektor = cls.vektor(z, name, was, proben)
        if vektor is None or len(vektor) != len(liste):
            if vektor is not None:
                logger.warning('Mesh3daiformvariantefigur: %s hat %d Regler, die Liste des Laufs %d — keine Figur', name, len(vektor), len(liste))
            return None, 0
        from Genesis9.formung import G9formung

        regler = cls.regler(vektor, liste)
        with cls._schloss:
            f = G9formung(regler)
            p = np.asarray(f.punkte(), dtype=np.float64).copy()
            p[:, 1] -= f.boden()
            cls._ablage[schluessel] = (p, len(regler))
            while len(cls._ablage) > cls.MAX:
                cls._ablage.popitem(last=False)
        return p, len(regler)

    @staticmethod
    def abstand(a, b):
        d = 1000.0 * np.linalg.norm(a - b, axis=1)
        return {'rms_mm': round(float(np.sqrt((d ** 2).mean())), 1), 'median_mm': round(float(np.median(d)), 1), 'p95_mm': round(float(np.percentile(d, 95)), 1)}

    @staticmethod
    def _kopf(kopf):
        text = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        return struct.pack('<I', len(text)) + text

    @classmethod
    def paket(cls, lauf, name, was, liste, proben):
        p, gesetzt = cls.punkte(lauf, name, was, liste, proben)
        if p is None:
            return None
        ursprung = cls.ursprung()
        kopf = {'was': str(was), 'punkte': int(len(ursprung)), 'hoehe_m': round(float(p[:, 1].max()), 3), 'regler_gesetzt': gesetzt}
        if was != 'ziel':
            ziel, _ = cls.punkte(lauf, name, 'ziel', liste, proben)
            if ziel is not None:
                kopf['abstand'] = cls.abstand(p, ziel)
                kopf['hoehe_ziel_m'] = round(float(ziel[:, 1].max()), 3)
        return cls._kopf(kopf) + p[ursprung].astype('<f4').tobytes()

    @classmethod
    def koerper(cls, grundlage):
        """Dreiecke, UV und Material des Körpers aus dem Anzeigenetz der Grundlage (Haut des Jobs, dessen Kleider die Variante trägt) — None, wenn es fehlt oder nicht passt."""
        d = Mesh3daiflaechennetz.laden(grundlage)
        if d is None:
            return None
        gemerkt = cls._koerper.get(grundlage)
        if gemerkt and gemerkt[0] is d:
            return gemerkt[1]
        n = len(cls.ursprung())
        koerper = d['etikett'] == 0
        f = int(np.argmin(koerper)) if not koerper.all() else len(koerper)
        dreiecke = d['dreiecke'][:f]
        if f == 0 or len(d['uv']) < n or int(dreiecke.max()) >= n:
            logger.warning('Mesh3daiformvariantefigur: Anzeigenetz von %s passt nicht zum Körper (%d Dreiecke, größter Index %s, %d Punkte)', grundlage, f,
                           int(dreiecke.max()) if f else '—', n)
            return None
        material = d['material'][:f].astype('<i2')
        genutzt = sorted(int(i) for i in np.unique(material) if i >= 0)
        kopf = {'punkte': n, 'dreiecke': f, 'grundlage': grundlage,
                'materialien': [{'name': m.get('name'), 'bild': m.get('bild'), 'farbe': m.get('farbe'), 'genutzt': i in genutzt} for i, m in enumerate(d['materialien'])]}
        roh = material.tobytes()
        paket = cls._kopf(kopf) + dreiecke.astype('<u4').tobytes() + d['uv'][:n].astype('<f4').tobytes() + roh + b'\0' * (-len(roh) % 4)
        cls._koerper[grundlage] = (d, paket)
        return paket
