# -*- coding: utf-8 -*-
"""Standmodellglb — die Figur des letzten Stands als EINE GLB mit Rig: Körper mit den gebackenen Kacheln, Augen,
Mund, Wimpern und Brauen, dazu Kleider und Haar (01.10.2026, Edgar: „Baue beim letzten stand ein 3d modell (Genesis
mit assets) und lades es gleich, das muss schnell gehen").

Bis dahin baute die Bühne von „2D3D Kleider" die Genesis-Figur bei jedem Öffnen im Browser (`Genesis9Modell`: 254
Regler, fünf 2048er-Kacheln, feine Stufe nach) — gemessen am Auftrag `.52` antwortete der Tab dabei zweimal über 45 s
lang nicht. Diese Datei lädt three.js in einem Zug.

Aufbau: ein Skelett (die Knochen der Stellung samt Zunge des Mundes, `G9koerpernetz` → `skelett.knochen`), EIN Skin
für alle Netze, je Kachel bzw. Materialgruppe ein Netz mit Bild (JPEG; mit Durchsicht PNG als Maske). Die
Knotennamen folgen der Runden-GLB (`koerper…`, `kleidung__<sorte>__<n>_g<k>__<slug>`, `haar__…`), damit „Haare" und
„Kleider" sie schalten (`Engine2d3dKleiderbuehnenmodell.art`) und der Pinsel die Gruppe kennt (`Engine2d3dKleidermalen`).

DIE BINDEMATRIZEN sind das Inverse der Weltlage jedes Knochens — Verschiebung UND Ruhedrehung. Bis 03.10.2026 schrieb
`G9rigglb.skelett` nur die Verschiebung und diese Klasse rechnete sie selbst nach; three.js nimmt die Matrizen wörtlich,
und gemessen stand `figur.glb` von `.51` dort in der Ruhelage verzerrt: die gehäuteten Punkte im Mittel 75 mm, höchstens
651 mm neben ihrer Lage im Netz. Seither kommen sie aus `G9rigglb.skelett` (für alle Schreiber, auch die Grundfigur
für Blender).

Weggelassen: Feuchtfilm und Träne der Augen (im Browser durchsichtig; deckend gezeichnet verdecken sie die Iris),
Normalen- und Rauheitsbilder (die Bühne soll schnell laden).
"""

import io
import json
import logging

import numpy as np
from Genesis9.rigglb import G9rigglb

logger = logging.getLogger('core')

__all__ = ['Standmodellglb']


class Standmodellglb(G9rigglb):
    """`koerper(netz, kacheln)`, `anhaenge(netz, augenbild)`, `teile(teile)`, dann `schreiben(pfad)`."""

    #: Längste Kante der Hautkacheln und Stoffbilder.
    KANTE = 1024
    #: Bilder mit Durchsicht (Wimpern, Brauen, Haarkarten): PNG, deshalb kleiner.
    KANTE_MASKE = 512
    JPEG_GUETE = 85
    #: Haarkarten der Kleidung/Frisur: harte Maske (viele Lagen übereinander — weiche Durchsicht bräuchte Sortierung).
    #: Wimpern und Brauen: weich (`BLEND`) — mit ihrer Deckkraft 0,7–0,9 fielen die Brauen an der harten Grenze weg.
    #: 0,35 → 0,15 am 03.10.2026 (Edgar: Modell ≠ Iteration): Der Bart (`mavick_beard`, Maske 130 × 216) hat bei 0,35 nur 28,2 % der Punkte
    #: (bei 0,15: 43,9 %, bei 0,05: 52,2 %; gemessen `_wegwerf/randy/bart_alpha.py` an stand_98597214b613.glb) — auf der Bühne stand ein
    #: Stoppelbart, der Mitsuba-Render der Iteration zeigt ihn dicht. Ob 0,15 dem Render genügt, sagt der Blick auf die Bühne.
    MASKE_GRENZE = 0.15
    DURCHSICHTIG = ('EyeMoisture', 'Cornea', 'Tear')
    #: Kleidungsstücke dieser Art (`sorte` beginnt so) bekommen Falten und weißen Stoff.
    HOSE = 'gc_hose'
    #: Wohin ein Punkt gebunden wird, dessen Knochen das Skelett nicht kennt (gezählt in `fehlend`).
    ERSATZ = 'hip'

    def __init__(self, knochen):
        super().__init__()
        self.gltf['asset']['generator'] = 'HumanBody 2D3D Kleider (Stand)'
        self.knochen = [k for k in knochen if not k.get('ende')]
        self.nummer = {k['name']: i for i, k in enumerate(self.knochen)}
        gelenke, wurzel, bind = self.skelett(self.knochen)
        self.gelenke = gelenke                       # Knotennummern in Knochenreihenfolge (`Standhaltung`)
        matrizen = self._zugriff(bind, self.FLOAT, 'MAT4', None)
        self.gltf['skins'] = [{'name': 'Genesis 9', 'inverseBindMatrices': matrizen, 'joints': list(gelenke),
                               'skeleton': wurzel}]
        self.gltf['samplers'] = [{'magFilter': 9729, 'minFilter': 9987, 'wrapS': 10497, 'wrapT': 10497}]
        self._bilder = {}
        self.fehlend = set()
        self.zahl = {'netze': 0, 'punkte': 0, 'dreiecke': 0, 'bilder': 0}

    # ---------------------------------------------------------------- Haut

    def _haut(self, haut, anzahl):
        """(index (N, 4), gewicht (N, 4)) in Knochenreihenfolge, Gewichte auf 1 normiert."""
        ersatz = self.nummer.get(self.ERSATZ, 0)
        if not haut or not haut.get('knochen'):
            gewicht = np.zeros((anzahl, 4))
            gewicht[:, 0] = 1.0
            return np.full((anzahl, 4), ersatz, dtype=np.int64), gewicht
        spalten = []
        for name in haut['knochen']:
            if name not in self.nummer:
                self.fehlend.add(str(name))
            spalten.append(self.nummer.get(name, ersatz))
        index = np.asarray(spalten, dtype=np.int64)[np.asarray(haut['index'], dtype=np.int64).reshape(-1, 4)]
        gewicht = np.asarray(haut['gewicht'], dtype=np.float64).reshape(-1, 4)
        summe = gewicht.sum(axis=1, keepdims=True)
        leer = summe[:, 0] <= 1e-9
        gewicht = gewicht / np.where(summe > 1e-9, summe, 1.0)
        gewicht[leer] = (1.0, 0.0, 0.0, 0.0)
        index[leer, 0] = ersatz
        return index, gewicht

    # ------------------------------------------------------------------ Bilder

    @staticmethod
    def _zahl(wert, vorgabe):
        if isinstance(wert, str):
            try:
                wert = json.loads(wert)
            except ValueError:
                return vorgabe
        return wert if wert is not None else vorgabe

    def _bild(self, albedo=None, alpha=None, alphawert=1.0, weissen=None):
        """Index der glTF-Textur — je (Bild, Maske, Deckkraft, Weißung) EINMAL in der Datei; None ohne beides. `weissen`: eine `Stoffweissung` (weißer Stoff der Hose: Flecken der
        Fotoprojektion auf Weiß, Innenseiten ohne Streifen); ihr `schluessel` gehört zum Bildspeicher."""
        if albedo is None and alpha is None:
            return None
        schluessel = (str(albedo), str(alpha), round(float(alphawert), 3), weissen.schluessel if weissen is not None else None)
        if schluessel in self._bilder:
            return self._bilder[schluessel]
        from PIL import Image
        kante = self.KANTE_MASKE if alpha else self.KANTE
        if albedo is not None:
            with Image.open(albedo) as roh:
                bild = roh.convert('RGB')
                bild.thumbnail((kante, kante))
                bild = bild.copy()
            if weissen is not None:
                bild = weissen(bild)
        if alpha is not None:
            with Image.open(alpha) as roh:
                maske = roh.convert('L')
                maske.thumbnail((kante, kante))
                maske = maske.copy()
            if albedo is None:
                bild = Image.new('RGB', maske.size, (255, 255, 255))
            elif bild.size[0] * bild.size[1] < maske.size[0] * maske.size[1]:
                bild = bild.resize(maske.size)      # Grauschicht ohne Daz-Bild ist 4 × 4 — die Maske (Strähnen) zählt
            maske = maske.resize(bild.size)
            if alphawert < 1.0:
                maske = maske.point(lambda v: int(v * float(alphawert)))
            bild.putalpha(maske)
        speicher = io.BytesIO()
        if alpha is not None:
            bild.save(speicher, format='PNG')
            art = 'image/png'
        else:
            bild.save(speicher, format='JPEG', quality=self.JPEG_GUETE)
            art = 'image/jpeg'
        self.gltf.setdefault('images', []).append({'bufferView': self._ablegen(speicher.getvalue()), 'mimeType': art})
        self.gltf.setdefault('textures', []).append({'source': len(self.gltf['images']) - 1, 'sampler': 0})
        self._bilder[schluessel] = len(self.gltf['textures']) - 1
        self.zahl['bilder'] += 1
        return self._bilder[schluessel]

    # -------------------------------------------------------------------- Netz

    def _netz(self, name, punkte, dreiecke, normalen, uv, haut, textur=None, faktor=(1.0, 1.0, 1.0), maske=False,
              zweiseitig=True, glanz=None):
        """Ein Netz am gemeinsamen Skin — nur die Punkte, die seine Dreiecke brauchen. `glanz`: `{metall, rauheit, opazitaet}` der Materialgruppe
        (Stiefel glänzen, die Brille ist durchsichtig — wie im Render der Runde, `Mitsubamaterial.metallglanz`/`durchsicht`)."""
        dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        if not len(dreiecke):
            return
        nummern, neu = np.unique(dreiecke.ravel(), return_inverse=True)
        punkte = np.asarray(punkte, dtype=np.float64)
        if normalen is None:
            from Genesis9.figurrigglb import G9figurrigglb
            normalen = G9figurrigglb._normalen(punkte, dreiecke)
        attribute = {
            'POSITION': self._zugriff(punkte[nummern], self.FLOAT, 'VEC3', self.ARRAY, grenzen=True),
            'NORMAL': self._zugriff(np.asarray(normalen, dtype=np.float64)[nummern], self.FLOAT, 'VEC3', self.ARRAY),
            'JOINTS_0': self._zugriff(haut[0][nummern], self.USHORT, 'VEC4', self.ARRAY),
            'WEIGHTS_0': self._zugriff(haut[1][nummern], self.FLOAT, 'VEC4', self.ARRAY),
        }
        if uv is not None:
            attribute['TEXCOORD_0'] = self._zugriff(np.asarray(uv, dtype=np.float64)[nummern], self.FLOAT, 'VEC2',
                                                    self.ARRAY)
        # Daz-Farben und Tönungen sind sRGB, glTF rechnet linear — wie `Genesis9netz.farbe` im Browser. Ohne die
        # Umrechnung standen die Brauen (#382a25) als helles Graubraun (#81716a) auf der Stirn.
        srgb = np.clip(np.asarray(list(faktor)[:3], dtype=np.float64), 0.0, 1.0)
        farbe = [float(v) for v in self.linear(srgb * 255.0)] + [1.0]
        material = {'name': name, 'doubleSided': bool(zweiseitig),
                    'pbrMetallicRoughness': {'baseColorFactor': farbe, 'metallicFactor': 0.0, 'roughnessFactor': 0.8}}
        self._glanz(material, glanz)
        if textur is not None and uv is not None:
            material['pbrMetallicRoughness']['baseColorTexture'] = {'index': textur}
        if maske == 'BLEND':
            material['alphaMode'] = 'BLEND'
        elif maske:
            material['alphaMode'] = 'MASK'
            material['alphaCutoff'] = self.MASKE_GRENZE
        self.gltf['materials'].append(material)
        indizes = self._zugriff(neu.reshape(-1), self.UINT32, 'SCALAR', self.ELEMENTE)
        self.gltf['meshes'].append({'name': name, 'primitives': [
            {'attributes': attribute, 'indices': indizes, 'material': len(self.gltf['materials']) - 1}]})
        self.gltf['nodes'].append({'name': name, 'mesh': len(self.gltf['meshes']) - 1, 'skin': 0})
        self.gltf['scenes'][0]['nodes'].append(len(self.gltf['nodes']) - 1)
        self.zahl['netze'] += 1
        self.zahl['punkte'] += int(len(nummern))
        self.zahl['dreiecke'] += int(len(dreiecke))

    #: Teilmetall höchstens so stark: Die Bühne hat kein Umgebungsbild, reines Metall stünde dort schwarz da (wie `Mitsubamaterial.metallglanz`
    #: nimmt der Klarlack den Glanz); Lack wie in three.js' `KHR_materials_clearcoat`.
    METALL_HOECHSTENS = 0.35

    def _glanz(self, material, glanz):
        """Metall/Lack (Stiefel) und Deckkraft (Brille) an das glTF-Material legen — nichts, wenn die Gruppe beides nicht trägt."""
        if not glanz:
            return
        pbr = material['pbrMetallicRoughness']
        if glanz.get('metall'):
            pbr['metallicFactor'] = min(self.METALL_HOECHSTENS, float(glanz['metall']))
            pbr['roughnessFactor'] = min(1.0, max(0.05, float(glanz.get('rauheit') if glanz.get('rauheit') is not None else 0.3)))
            material.setdefault('extensions', {})['KHR_materials_clearcoat'] = {'clearcoatFactor': 1.0, 'clearcoatRoughnessFactor': 0.08}
            if 'KHR_materials_clearcoat' not in self.gltf.setdefault('extensionsUsed', []):
                self.gltf['extensionsUsed'].append('KHR_materials_clearcoat')
        opazitaet = glanz.get('opazitaet')
        if opazitaet is not None and float(opazitaet) < 0.999:
            pbr['baseColorFactor'][3] = max(0.02, float(opazitaet))
            material['alphaMode'] = 'BLEND'

    @staticmethod
    def _uv(uv):
        """glTF zählt v von oben."""
        if uv is None:
            return None
        uv = np.asarray(uv, dtype=np.float64).reshape(-1, 2).copy()
        uv[:, 1] = 1.0 - uv[:, 1]
        return uv

    # ----------------------------------------------------------------- Teile

    def koerper(self, netz, kacheln):
        """Der Körper je UDIM-Kachel ein Netz: das gebackene Foto (`kacheln` {1001: Pfad}), sonst die Daz-Haut der
        ersten Gruppe der Kachel (mit ihrer Farbe)."""
        from Genesis9.material import G9material
        dreiecke = np.asarray(netz['dreiecke'], dtype=np.int64).reshape(-1, 3)
        uv = self._uv(netz['uv'])
        uv[:, 0] = np.clip(uv[:, 0], 0.0, 1.0)
        haut = self._haut(netz['haut'], len(netz['punkte']))
        je_kachel = {}
        for g in netz['gruppen']:
            von = int(g['index_ab']) // 3
            je_kachel.setdefault(int(g.get('kachel') or 1001), []).append((von, von + int(g['index_anzahl']) // 3, g))
        for kachel, stuecke in sorted(je_kachel.items()):
            bilder = stuecke[0][2].get('bilder') or {}
            foto = kacheln.get(kachel)
            albedo = foto or (G9material.datei(bilder['albedo']) if bilder.get('albedo') else None)
            faktor = (1.0, 1.0, 1.0) if foto else self._zahl(bilder.get('farbe'), (1.0, 1.0, 1.0))
            wahl = np.concatenate([dreiecke[a:b] for a, b, _ in stuecke])
            self._netz('koerper__koerper__0_k%d' % kachel, netz['punkte'], wahl, netz.get('normalen'), uv, haut,
                       self._bild(albedo), faktor, zweiseitig=False)

    def anhaenge(self, netz, augenbild=None):
        """Augen, Mund, Wimpern, Brauen (`G9koerpernetz` → `anhaenge`) — je Gruppe ein Netz; die Iris aus dem Bild
        des Auftrags (`fototextur.augen`), wenn es eins gibt."""
        from Genesis9.material import G9material
        for a in netz.get('anhaenge') or []:
            dreiecke = np.asarray(a['dreiecke'], dtype=np.int64).reshape(-1, 3)
            uv = self._uv(a.get('uv'))
            haut = self._haut(a.get('haut'), len(a['punkte']))
            for k, g in enumerate(a.get('gruppen') or []):
                if str(g.get('name', '')).startswith(self.DURCHSICHTIG):
                    continue
                b = g.get('bilder') or {}
                albedo = G9material.datei(b['albedo']) if b.get('albedo') else None
                if augenbild and a.get('schluessel') == 'augen' and albedo is not None:
                    albedo = augenbild
                alpha = G9material.datei(b['alpha']) if b.get('alpha') else None
                if albedo is None and alpha is None:
                    continue
                von = int(g['index_ab']) // 3
                textur = self._bild(albedo, alpha, self._zahl(b.get('alphawert'), 1.0))
                self._netz('koerper_%s__%s_g%d' % (a.get('schluessel'), a.get('name'), k), a['punkte'],
                           dreiecke[von:von + int(g['index_anzahl']) // 3], a.get('normalen'), uv, haut, textur,
                           self._zahl(b.get('farbe'), (1.0, 1.0, 1.0)), maske='BLEND' if alpha is not None else False)

    def teile(self, teile):
        """Kleider und Haar aus `Kleidermodellbau.teile` (ohne den Körper) — je Materialgruppe ein Netz mit dem Bild
        der Runde (Tönung als Farbfaktor), Gruppen ohne Bild und Stranghaar flach in der Farbe des Teils."""
        from Genesis9.kleidtexturen import G9kleidtexturen
        from Genesis9.material import G9material
        for i, t in enumerate(teile):
            if t.get('art') == 'koerper':
                continue
            name = '%s__%s__%d' % (t.get('art'), t.get('sorte') or t.get('art'), i)
            dreiecke = np.asarray(t['dreiecke'], dtype=np.int64).reshape(-1, 3)
            haut = self._haut(t.get('haut'), len(t['punkte']))
            weiss = str(t.get('sorte') or '').startswith(self.HOSE)       # weiße Hose: Stoffdrapierung (`Hosenfalten`) und fleckenfreies Weiß (`Stoffweissung`)
            innen = None
            if weiss:
                from .hosenfalten import Hosenfalten
                innen = Hosenfalten.innen(t['punkte'], dreiecke)
                t = dict(t, punkte=Hosenfalten.anwenden(t['punkte'], dreiecke), normalen=None)       # Normalen neu aus den verschobenen Punkten, sonst bleiben die Falten ungeschattet
            gruppen = [g for g in (t.get('gruppen') or []) if int(g.get('index_anzahl') or 0) >= 3]
            uv = self._uv(t.get('uv'))
            if uv is None or not gruppen:
                self._netz(name, t['punkte'], dreiecke, t.get('normalen'), None, haut, faktor=t['farbe'])
                continue
            je_ab = {int(x['ab']): x for x in (t.get('textur') or [])}
            belegt = np.zeros(len(dreiecke), dtype=bool)
            for k, g in enumerate(gruppen):
                ab, anzahl = int(g['index_ab']) // 3, int(g['index_anzahl']) // 3
                tx = je_ab.get(ab) or {}
                b = g.get('bilder') or {}
                alpha = G9material.datei(b['alpha']) if b.get('alpha') else None
                weissen = None
                if weiss:
                    from .stoffweissung import Stoffweissung
                    gewaehlt = dreiecke[ab:ab + anzahl][innen[ab:ab + anzahl]]
                    weissen = Stoffweissung(uv[gewaehlt] if len(gewaehlt) else None)
                textur = self._bild(tx.get('albedo'), alpha, self._zahl(b.get('alphawert'), 1.0), weissen=weissen)
                faktor = tx['faktor'] if tx.get('faktor') is not None else t['farbe']
                self._netz('%s_g%d__%s' % (name, k, G9kleidtexturen.slug(g['name'])), t['punkte'],
                           dreiecke[ab:ab + anzahl], t.get('normalen'), uv, haut, textur, faktor,
                           maske=alpha is not None,
                           glanz={'metall': tx.get('metall'), 'rauheit': tx.get('rauheit'), 'opazitaet': tx.get('opazitaet')})
                belegt[ab:ab + anzahl] = True
            if not belegt.all():
                self._netz(name + '_flach', t['punkte'], dreiecke[~belegt], t.get('normalen'), None, haut,
                           faktor=t['farbe'])
