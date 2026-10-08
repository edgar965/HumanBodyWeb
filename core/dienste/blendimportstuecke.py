# -*- coding: utf-8 -*-
"""Blendimportstuecke — Kleider und Haar einer .blend als eigene Genesis-9-Stücke in der Bibliothek.

Derselbe Weg wie `Fotostuecke` (Form „netz"): Punkte des Stücks → Ruhelage der Figur (`Blendimportlage`) → OBJ mit
Textur → `G9eigenstueck.schreiben` (Gewichte der 3 nächsten Hautpunkte; die Gewichte der .blend gehören zu einem
anderen Rig und fallen weg) → Ruhelage auf der GRUNDFIGUR zurückrechnen (`G9gcfigurbau.ruhelage`) → neu schreiben. So
passt das Stück jeder Genesis-Figur und folgt allen Körpermorphs (`G9folger`); Kleider bekommen die Passform-Regler
(Länge, Weite), Frisuren die Haarachsen — beides von selbst über die Garderobe.

Das Haar hängt im Original nur am Kopfknochen (alle 34.637 Punkte tragen Gewicht allein in `head.x`, 0,77–0,85, gemessen
08.10.2026): Es geht starr mit dem Kopf in die Ruhelage
(`Blendimportlage.kopf_starr`) und wird ganz an `head` gebunden, Art `Hair` — wie `Herrenhaarstueck`. Sein Alpha-Bild
kommt als `alpha_bild` ins Material.

Kategorie: Kleider über `G9mbkategorien.fuer(ordner, Name)` (Ordner aus `Blendimportrollen.kategorie`), das Haar
`Follower/Hair`. Namen: „<Figur> <Art>" (z. B. „cute girl Shorts") — die Namensregel von `G9dazkategorien` greift.
"""

import logging

import numpy as np

from .blendimportlage import Blendimportlage

logger = logging.getLogger('core')

__all__ = ['Blendimportstuecke']


class Blendimportstuecke:
    HAAR_KATEGORIE = ('Follower/Hair', '/Default/Hair')
    #: Name des Stücks je Rolle/Art: „<Figur> <Zusatz>".
    HAAR_ZUSATZ = 'Haar'

    def __init__(self, ablage, job, inventar, rollen, figurname, melden=None):
        self.ablage = ablage
        self.job = job
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        self.figurname = figurname
        self.melden = melden or (lambda anteil, text: None)
        self.lage = Blendimportlage(job)

    def _netz(self, name):
        with np.load(self.ablage.export(self.inventar[name]['datei'])) as d:
            return {k: d[k] for k in d.files}

    def bauen(self):
        """`({rolle_name: garderobenkennung}, bericht)` für alle Kleider und das Haar."""
        wahl = [r for r in self.rollen if r['rolle'] in ('kleid', 'haar')]
        stuecke, bericht = {}, {}
        for i, rolle in enumerate(wahl):
            self.melden(i / max(len(wahl), 1), 'Stück %s' % rolle['name'])
            try:
                kennung, b = self.stueck(rolle)
            except Exception as fehler:  # noqa: BLE001 — ein Stück darf scheitern, die Figur bleibt
                logger.exception('Blender-Import %s: Stück %s gescheitert', self.ablage.kennung, rolle['name'])
                bericht[rolle['name']] = {'fehler': str(fehler)[:300]}
                continue
            stuecke[rolle['name']] = kennung
            bericht[rolle['name']] = b
        return stuecke, bericht

    def anzeige(self, rolle):
        zusatz = self.HAAR_ZUSATZ if rolle['rolle'] == 'haar' else rolle.get('art') or rolle['name']
        return '%s %s' % (self.figurname, zusatz)

    def stueck(self, rolle):
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.gcfigurbau import G9gcfigurbau
        from Genesis9.mbkategorien import G9mbkategorien
        from Genesis9.objleser import G9objleser

        haar = rolle['rolle'] == 'haar'
        d = self._netz(rolle['name'])
        punkte = self.lage.kopf_starr(d['punkte']) if haar else self.lage.ruhelage(d['punkte'])
        kennung, anzeige = G9eigenstueck.kennung_und_name(self.anzeige(rolle))
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        material = self.material(kennung, (self.inventar[rolle['name']]['materialien'] or [{}])[0] or {}, ordner)
        obj = self.obj(ordner, punkte, d['dreiecke'], d['uv_ecken'], material)
        netz = G9objleser.lesen(str(obj))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        if haar:
            kategorie, art, knochen = self.HAAR_KATEGORIE, 'Hair', 'head'
        else:
            kategorie, art, knochen = G9mbkategorien.fuer(rolle.get('ordner') or 'tops', anzeige), 'Clothing', None
        bilanz = G9eigenstueck.schreiben(roh, netz, kennung, anzeige, kategorie, material, heben=False,
                                         knochen=knochen, art_ordner=art)
        figur = dict(self.job.stellung() or {})
        ruhe, bericht = G9gcfigurbau.ruhelage(bilanz['stueck'], figur, roh, roh)
        bilanz = G9eigenstueck.schreiben(ruhe, netz, kennung, anzeige, kategorie, material, heben=False,
                                         knochen=knochen, art_ordner=art)
        bericht.update(stueck=bilanz['stueck'], name=anzeige, punkte=bilanz['punkte'], flaechen=bilanz['flaechen'],
                       haut_median_mm=bilanz['haut_median_mm'], kategorie=list(kategorie),
                       angezogen=G9gcfigurbau.pruefen(bilanz['stueck'], figur, roh))
        if haar:
            bericht['kopf'] = getattr(self.lage, 'kopf_befund', None)
        logger.info('Blender-Import %s: Stück %s → %s', self.ablage.kennung, rolle['name'], bilanz['stueck'])
        return bilanz['stueck'], bericht

    @classmethod
    def material(cls, kennung, quelle, ordner):
        """Material für `G9dsonschreiber`: Farbe, Normalen, Rauheit, Alpha aus der .blend (Bilder werden kopiert).
        Ein DDS (Detailnormale der Kleider) kann der Browser nicht lesen — es fällt weg, die Grundnormale bleibt."""
        def bild(kanal):
            pfad = quelle.get(kanal)
            return pfad if pfad and not str(pfad).lower().endswith('.dds') else None

        alpha = bild('alpha')
        if alpha:
            alpha = cls.alphabild(alpha, ordner / (kennung + '_alpha.png'))
        # Feste Farbe statt Bild (`Blendexport.festfarbe`: Haar mit Mix-Faktor 1,0): linear → sRGB, wie Daz' Diffusfarbe.
        fest = quelle.get('farbe_wert')
        farbe = tuple(round(cls.srgb(w), 4) for w in fest) if fest and not quelle.get('farbe') else (1.0, 1.0, 1.0)
        return {'name': kennung + '_Mat', 'farbe': farbe, 'bild': bild('farbe'),
                'normalen': bild('normalen'), 'rauheit_bild': bild('rauheit'), 'alpha_bild': alpha,
                'shininess': None, 'opacity': None}

    @staticmethod
    def srgb(linear):
        """Lineare Farbkomponente → sRGB (IEC 61966-2-1)."""
        linear = max(0.0, min(1.0, float(linear)))
        return 12.92 * linear if linear <= 0.0031308 else 1.055 * linear ** (1 / 2.4) - 0.055

    @staticmethod
    def alphabild(quelle, ziel):
        """Der Alpha-Kanal als Graubild: three.js liest eine `alphaMap` aus dem GRÜNkanal, Daz' Schnittmasken sind
        grau — das Farbbild mit Alpha (Haar der .blend: `hair_basecolor.png`, RGBA) gäbe dort die Haarfarbe als
        Deckkraft. Ohne Alpha-Kanal bleibt das Bild, wie es ist."""
        from PIL import Image

        with Image.open(quelle) as bild:
            if 'A' not in bild.getbands():
                return str(quelle)
            bild.getchannel('A').save(ziel)
        return str(ziel)

    @staticmethod
    def obj(ordner, punkte, dreiecke, uv_ecken, material):
        """`stueck.obj` (+ MTL ohne Bild: das Material geht getrennt an den Schreiber) — Punkte in Ruhe (m, Y oben),
        UV je Dreiecksecke."""
        (ordner / 'stueck.mtl').write_text('newmtl Stoff\nKd 1 1 1\n', encoding='utf-8')
        uv = np.asarray(uv_ecken, dtype=np.float64).reshape(-1, 2)
        zeilen = ['mtllib stueck.mtl', 'usemtl Stoff'] + ['v %.6f %.6f %.6f' % tuple(p) for p in punkte]
        zeilen += ['vt %.6f %.6f' % tuple(t) for t in uv]
        zeilen += ['f %d/%d %d/%d %d/%d' % (a + 1, 3 * i + 1, b + 1, 3 * i + 2, c + 1, 3 * i + 3)
                   for i, (a, b, c) in enumerate(np.asarray(dreiecke, dtype=np.int64))]
        pfad = ordner / 'stueck.obj'
        pfad.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
        return pfad
