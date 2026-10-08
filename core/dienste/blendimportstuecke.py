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

Die Scham (Einstellung `scham` = `objekt`): der Teil des Körpers, den die Figur nicht trägt, als Stück „<Name> Scham" unter Zubehör
(`scham_stueck`, `Blendimportscham`) — ohne Abstimmung der Flächenrichtung gegen die Haut und mit `haut_tiefe_mm` neben der `.duf`.
"""

import logging

import numpy as np

from .blendimportlage import Blendimportlage

logger = logging.getLogger('core')

__all__ = ['Blendimportstuecke']


class Blendimportstuecke:
    HAAR_KATEGORIE = ('Follower/Hair', '/Default/Hair')
    #: Die Originalaugen stehen unter „Zubehör"; was sie ersetzen, sagt die Datei neben der `.duf` (`G9stueckersatz`).
    AUGEN_KATEGORIE = ('Follower/Accessory', '/Default/Accessories')
    #: Name des Stücks je Rolle/Art: „<Figur> <Zusatz>".
    HAAR_ZUSATZ = 'Haar'
    AUGEN_ZUSATZ = 'Augen'
    SCHAM_ZUSATZ = 'Scham'
    #: Blenders Augen haben Rauheit 0 (Hornhaut): als `shininess` an den Schreiber, der daraus Rauheit 0,05 macht.
    AUGEN_GLANZ = 0.95
    #: Bildformate, die der Browser liest; alles andere (TGA, BMP …) geht als PNG ins Stück.
    BROWSER_FORMATE = ('.png', '.jpg', '.jpeg')

    def __init__(self, ablage, job, inventar, rollen, figurname, melden=None, augen='original', zusatz=None, scham='aus'):
        self.ablage = ablage
        self.job = job
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen
        self.figurname = figurname
        self.melden = melden or (lambda anteil, text: None)
        self.lage = Blendimportlage(job, zusatz)
        #: `objekt`: die Originalaugen werden ein eigenes Stück (Einstellung „Augen" des Dialogs).
        self.augen_objekt = augen == 'objekt'
        #: `objekt`: der Teil des Körpers, den die Figur nicht trägt, wird das Stück „<Name> Scham" (`Blendimportscham`).
        self.scham_objekt = scham == 'objekt'

    def _netz(self, rolle):
        """Das Netz einer Rolle; eine Rolle mit mehreren Netzen (`namen`: beide Augen) wird zu EINEM zusammengelegt."""
        teile = []
        for name in rolle.get('namen') or [rolle['name']]:
            with np.load(self.ablage.export(self.inventar[name]['datei'])) as d:
                teile.append({k: d[k] for k in d.files})
        if len(teile) == 1:
            return teile[0]
        anfang = np.cumsum([0] + [len(t['punkte']) for t in teile[:-1]])
        return {'punkte': np.concatenate([t['punkte'] for t in teile]),
                'dreiecke': np.concatenate([t['dreiecke'] + int(a) for t, a in zip(teile, anfang, strict=True)]),
                'uv_ecken': np.concatenate([t['uv_ecken'] for t in teile])}

    def bauen(self):
        """`({rolle_name: garderobenkennung}, bericht)` für alle Kleider, das Haar und (Einstellung) die Augen."""
        wahl = [r for r in self.rollen if r['rolle'] in ('kleid', 'haar')]
        augen = [r for r in self.rollen if r['rolle'] == 'auge']
        if self.augen_objekt and augen:
            wahl.append({'name': augen[0]['name'], 'namen': [a['name'] for a in augen], 'rolle': 'auge'})
        koerper = next((r for r in self.rollen if r['rolle'] == 'koerper'), None)
        if self.scham_objekt and koerper:
            # Schlüssel `scham`, nicht der Name des Körpers: der Körper selbst ist kein Stück.
            wahl.append({'name': koerper['name'], 'rolle': 'scham', 'schluessel': 'scham'})
        stuecke, bericht = {}, {}
        for i, rolle in enumerate(wahl):
            schluessel = rolle.get('schluessel') or rolle['name']
            self.melden(i / max(len(wahl), 1), 'Stück %s' % schluessel)
            try:
                kennung, b = self.stueck(rolle)
            except Exception as fehler:  # noqa: BLE001 — ein Stück darf scheitern, die Figur bleibt
                logger.exception('Blender-Import %s: Stück %s gescheitert', self.ablage.kennung, schluessel)
                bericht[schluessel] = {'fehler': str(fehler)[:300]}
                continue
            if kennung is None:                       # das Stück entfällt mit Grund (Scham: die Figur trifft das Original)
                bericht[schluessel] = b
                continue
            stuecke[schluessel] = kennung
            bericht[schluessel] = b
        return stuecke, bericht

    def anzeige(self, rolle):
        zusatz = ({'haar': self.HAAR_ZUSATZ, 'auge': self.AUGEN_ZUSATZ, 'scham': self.SCHAM_ZUSATZ}.get(rolle['rolle'])
                  or rolle.get('art') or rolle['name'])
        return '%s %s' % (self.figurname, zusatz)

    def scham_stueck(self, rolle):
        """Das Stück „<Name> Scham": Fläche und Haut des Originalkörpers dort, wo die Figur ihn nicht trägt
        (`Blendimportscham`). `(None, {'aus': Grund})`, wenn die Figur das Original schon trifft."""
        import trimesh
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.objleser import G9objleser
        from Genesis9.stueckersatz import G9stueckersatz

        from .blendimportscham import Blendimportscham

        kennung, anzeige = G9eigenstueck.kennung_und_name(self.anzeige(rolle))
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        figur = self.lage.genesis()
        flaeche = trimesh.Trimesh(figur['punkte'], figur['dreiecke'], process=False)
        material_quelle = (self.inventar[rolle['name']]['materialien'] or [{}])[0] or {}
        d = Blendimportscham(self.lage, self._netz(rolle), material_quelle).bauen(ordner, kennung, flaeche)
        if 'aus' in d:
            return None, d
        material = self.material(kennung, d['quelle'], ordner)
        netz = G9objleser.lesen(str(self.obj(ordner, d['punkte'], d['dreiecke'], d['uv_ecken'], material)))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        kategorie = self.AUGEN_KATEGORIE
        # `wicklung=False`: die Fläche liegt teils HINTER der Haut — die Abstimmung gegen die Haut drehte sie um.
        # Gewichte: die der drei nächsten Hautpunkte, also bewegt sich das Stück beim Beugen wie die Haut dort (ganz am Becken
        # stünden die Seitenteile bei gespreizten Beinen ab, gesehen 08.10.2026). Die LAGE folgt dem Körper nicht
        # (`G9stueckteile.netze`, Hauttiefe), darum keine Rückrechnung auf die Grundfigur (`G9gcfigurbau`): die gespeicherte Lage IST
        # die Ruhelage der Figur dieses Imports.
        bilanz = G9eigenstueck.schreiben(roh, netz, kennung, anzeige, kategorie, material, heben=False, wicklung=False)
        G9stueckersatz.schreiben(bilanz['duf'], [], haut_tiefe_mm=Blendimportscham.HAUT_TIEFE_MM, anatomie='scham')
        bericht = dict(d['bericht'], stueck=bilanz['stueck'], name=anzeige, flaechen=bilanz['flaechen'], kategorie=list(kategorie),
                       punkte=bilanz['punkte'], knochen=bilanz['knochen'])
        logger.info('Blender-Import %s: Scham-Stück → %s (%s)', self.ablage.kennung, bilanz['stueck'], d['bericht'])
        return bilanz['stueck'], bericht

    def stueck(self, rolle):
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.gcfigurbau import G9gcfigurbau
        from Genesis9.mbkategorien import G9mbkategorien
        from Genesis9.objleser import G9objleser
        from Genesis9.stueckersatz import G9stueckersatz

        if rolle['rolle'] == 'scham':
            return self.scham_stueck(rolle)
        haar = rolle['rolle'] == 'haar'
        auge = rolle['rolle'] == 'auge'
        d = self._netz(rolle)
        # Haar und Augen hängen im Original starr am Kopf: sie gehen mit dem Kopf in die Ruhelage.
        punkte = self.lage.kopf_starr(d['punkte']) if haar or auge else self.lage.ruhelage(d['punkte'])
        kennung, anzeige = G9eigenstueck.kennung_und_name(self.anzeige(rolle))
        ordner = G9eigenstueck.arbeitsordner(kennung)
        ordner.mkdir(parents=True, exist_ok=True)
        material = self.material(kennung, (self.inventar[rolle['name']]['materialien'] or [{}])[0] or {}, ordner, haar)
        if auge:
            material['shininess'] = self.AUGEN_GLANZ
        obj = self.obj(ordner, punkte, d['dreiecke'], d['uv_ecken'], material)
        netz = G9objleser.lesen(str(obj))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        if haar:
            kategorie, art, knochen = self.HAAR_KATEGORIE, 'Hair', 'head'
        elif auge:
            kategorie, art, knochen = self.AUGEN_KATEGORIE, 'Clothing', 'head'
        else:
            kategorie, art, knochen = G9mbkategorien.fuer(rolle.get('ordner') or 'tops', anzeige), 'Clothing', None
        bilanz = G9eigenstueck.schreiben(roh, netz, kennung, anzeige, kategorie, material, heben=False,
                                         knochen=knochen, art_ordner=art)
        figur = self.lage.stellung()
        ruhe, bericht = G9gcfigurbau.ruhelage(bilanz['stueck'], figur, roh, roh)
        bilanz = G9eigenstueck.schreiben(ruhe, netz, kennung, anzeige, kategorie, material, heben=False,
                                         knochen=knochen, art_ordner=art)
        bericht.update(stueck=bilanz['stueck'], name=anzeige, punkte=bilanz['punkte'], flaechen=bilanz['flaechen'],
                       haut_median_mm=bilanz['haut_median_mm'], kategorie=list(kategorie),
                       angezogen=G9gcfigurbau.pruefen(bilanz['stueck'], figur, roh))
        if haar:
            bericht['kopf'] = getattr(self.lage, 'kopf_befund', None)
        if auge:
            # Die Datei NACH der `.duf` (Stückstand im Antwortvorrat): der Browser blendet die Genesis-Augen aus, solange es sitzt.
            G9stueckersatz.schreiben(bilanz['duf'], ['augen'])
            bericht['ersetzt'] = ['augen']
        logger.info('Blender-Import %s: Stück %s → %s', self.ablage.kennung, rolle['name'], bilanz['stueck'])
        return bilanz['stueck'], bericht

    #: Schnitt der Deckkraftkarte beim Haar (Anteil 0…1): Haarkarten der .blend tragen einzelne Strähnen von 1–3 Texeln Breite.
    #: Mit Alpha-to-Coverage und Schnitt 0,02 verwischt der Browser sie zu flachen Bahnen; Blender rechnet „Hashed" mit
    #: vielen Abtastungen. Setzung am Vergleich mit Blender (cute girl, 08.10.2026): 0,18 zeigt einzelne Strähnen und
    #: bleibt dicht, 0,35 lichtet die Frisur aus — kein Messwert.
    HAAR_ALPHA_SCHWELLE = 0.18

    @classmethod
    def material(cls, kennung, quelle, ordner, haar=False):
        """Material für `G9dsonschreiber`: Farbe, Normalen, Rauheit, Alpha aus der .blend (Bilder werden kopiert).
        Die zweite, gekachelte Normalenkarte (`detailnormalen`, Gewebe der Kleider) kommt als PNG aus dem Export und trägt
        ihre Wiederholungen (`detail_kachel`). Ein DDS an der Grundnormale kann der Browser nicht lesen — es fällt weg."""
        def bild(kanal):
            pfad = quelle.get(kanal)
            if not pfad or str(pfad).lower().endswith('.dds'):
                return None
            return cls.browserbild(pfad, ordner / ('%s_%s.png' % (kennung, kanal)))

        alpha = bild('alpha')
        if alpha:
            alpha = cls.alphabild(alpha, ordner / (kennung + '_alpha.png'))
        # Feste Farbe statt Bild (`Blendexport.festfarbe`: Haar mit Mix-Faktor 1,0): linear → sRGB, wie Daz' Diffusfarbe.
        fest = quelle.get('farbe_wert')
        farbe = tuple(round(cls.srgb(w), 4) for w in fest) if fest and not quelle.get('farbe') else (1.0, 1.0, 1.0)
        return {'name': kennung + '_Mat', 'farbe': farbe, 'bild': bild('farbe'),
                'normalen': bild('normalen'), 'rauheit_bild': bild('rauheit'), 'alpha_bild': alpha,
                'detailnormalen': bild('detailnormalen'), 'detail_kachel': quelle.get('detail_kachel'),
                'alpha_schwelle': cls.HAAR_ALPHA_SCHWELLE if haar and alpha else None,
                'shininess': None, 'opacity': None}

    @classmethod
    def browserbild(cls, pfad, ziel):
        """Das Bild in einem Format, das der Browser liest: PNG und JPG gehen unverändert durch; TGA (das Augenbild der
        .blend, `Eye_BaseColor.tga`), BMP und Ähnliches werden als PNG neben das Stück gelegt (`ziel`)."""
        if str(pfad).lower().endswith(cls.BROWSER_FORMATE):
            return pfad
        from PIL import Image

        with Image.open(pfad) as bild:
            bild.convert('RGBA' if 'A' in bild.getbands() else 'RGB').save(ziel)
        return str(ziel)

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
