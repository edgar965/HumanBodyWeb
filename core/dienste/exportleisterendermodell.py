# -*- coding: utf-8 -*-
"""Exportleisterendermodell — die GLB, die der Render der Exportleiste bekommt (31.10.2026, `Exportleisterender`).

Die Render-Kette (`Figurfilm`: Figurcache, Gelenkkorrektur, Mimik, Hautregler, `film_video.py`) erkennt Haut, Augen und Zähne am Knotennamen der Stand-GLB von „2D3D Kleider"
(`Standmodellglb`: `koerper__koerper__0_k1002` je UDIM-Kachel, `koerper_mund__Genesis9Mouth_g1`, …). Die GLB aus dem Browser (`Modellexport.glbBytes`) trägt andere Namen, den Körper als
EIN Netz mit sieben Materialgruppen ohne Kachelangabe (UV je Gruppe 0…1) und Hornhaut, Feuchtfilm und Wimpern als schwarze BLEND-Flächen — gemessen 31.10.2026 an Test edgar
(`ProjektTemp/_wegwerf/exportleiste/uv_probe.py`); der erste Render brach in `film_video.py` ab, weil `koerper__koerper__0_k1002` fehlte.
Darum entsteht die Figur hier wie der Stand von 2D3D Kleider aus denselben Reglern (`G9koerpernetz` → `Standmodellglb`: Körper je Kachel mit Normalen- und Dünnheitskarte, Augen, Mund,
Wimpern, Brauen; die Kacheln der Quelle, sonst die Daz-Haut der Grundfigur). Aus der Browser-GLB kommen nur die Stücke der Seite (KI-Kleider, Fotostücke, Anatomie-Stück) samt Bindung an
das Skelett, per Knochenname auf die Knochen des Stands umgehängt. Das trägt nur, wenn beide Skelette gleich stehen: Die größte Abweichung der Gelenke steht im Bericht, über
`ABWEICHUNG_M` bricht der Bau ab, statt Stücke neben die Figur zu legen. Die Haut unter den Stücken fällt aus dem Körper wie im Browser (`Exportleistehautmaske`).

Eine Figur mit eigenen Hautkacheln bekommt keine Daz-Brauen und -Wimpern (05.11.2026, Edgar zu Edgar_1: „die augenbrauen im render sind noch zu dunkel“): Die Kacheln tragen beide schon aus dem
Foto, die Seite zeichnet nur die Kacheln (im Chrome gelesen: 22 Netze, keins durchsichtig). Die Vorgaben des Stands legten `G9Eyebrows_CS06` (sRGB ~47/35/30, Deckkraft bis 0,9) und schwarze Wimpern darüber.
"""

import hashlib
import io
import re

import numpy as np

__all__ = ['Exportleisterendermodell']


class Exportleisterendermodell:
    #: Netze der Browser-GLB, die der Stand selbst baut (Körper und Anhänge von `G9koerpernetz`) — alles andere ist ein Stück der Seite.
    EIGEN = re.compile(r'^genesis9_(koerper|augen|mund|wimpern|brauen|traene)_')
    #: Anhänge von `G9koerpernetz`, die eine Figur mit eigenen Hautkacheln nicht bekommt: Beides trägt schon die Kachel.
    IN_DER_KACHEL = frozenset({'brauen', 'wimpern'})
    #: Größte erlaubte Abweichung eines Gelenks zwischen Browser und Server (m).
    ABWEICHUNG_M = 0.005
    TYPEN = {5126: '<f4', 5125: '<u4', 5123: '<u2', 5122: '<i2', 5121: 'u1', 5120: 'i1'}
    ANZAHL = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}

    def __init__(self, kacheln=None):
        #: `{1001: Pfad}` — die Hautkacheln der Quelle (Fotos); leer = Daz-Haut der Grundfigur.
        self.kacheln = dict(kacheln or {})

    def bauen(self, browser_glb, stellung, ziel):
        """Browser-GLB (Pfad) + Stellung (`{figur, regler}`) → `ziel` schreiben → Bericht `{netze, stuecke, abweichung_mm, knochen_ohne_gelenk, …}`."""
        from Genesis9.glbanimation import G9glbanimation

        from .exportleistehautmaske import Exportleistehautmaske
        from .exportleistekragen import Exportleistekragen
        from .standhaut import Standhaut
        from .standmodellglb import Standmodellglb
        figur = str(stellung.get('figur') or 'basis')
        netz = self._figur(figur, stellung.get('regler') or {}, Standhaut.SAETZE.get(figur))
        glb = Standmodellglb(netz['skelett']['knochen'])
        quelle = G9glbanimation(browser_glb)
        abweichung, gemeinsam = self._abweichung(quelle, glb)
        if abweichung > self.ABWEICHUNG_M:
            raise ValueError('Skelett der Seite und des Servers weichen um %.1f mm ab (über %d Gelenke) — die Stücke passten nicht auf die Figur' % (abweichung * 1000, gemeinsam))
        stuecke = self.stuecke(quelle, stellung.get('haut_deckt'))
        kragen = Exportleistekragen.anlegen(stuecke, netz)
        # Die Haut unter den Stücken fällt weg wie im Browser (`Hautverdeckung`) — sonst sticht sie in der Bewegung durch den Stoff
        koerper, verdeckung = Exportleistehautmaske.koerper(netz, [(s['punkte'], s['dreiecke']) for s in stuecke if s['deckt']])
        glb.koerper(koerper, self.kacheln)
        glb.anhaenge(self._anhaenge(netz))
        for s in stuecke:
            glb._netz(s['name'], s['punkte'], s['dreiecke'], s['normalen'], s['uv'], glb._haut(s['haut'], len(s['punkte'])), self._bild(quelle, glb, s['material']),
                      self._srgb(s['faktor']), maske=s['maske'])
            self._farben(glb, s)
        glb.schreiben(ziel)
        return dict(glb.zahl, stuecke=[s['name'] for s in stuecke], hautverdeckung=verdeckung, kragen=kragen, kacheln=sorted(self.kacheln), abweichung_mm=round(abweichung * 1000, 2),
                    gelenke_verglichen=gemeinsam, knochen_ohne_gelenk=sorted(glb.fehlend))

    def _anhaenge(self, netz):
        """`netz` für `Standmodellglb.anhaenge`: mit eigenen Kacheln ohne `IN_DER_KACHEL`, sonst unverändert."""
        if not self.kacheln:
            return netz
        return dict(netz, anhaenge=[a for a in netz.get('anhaenge') or [] if a.get('schluessel') not in self.IN_DER_KACHEL])

    @staticmethod
    def _figur(figur, regler, hautpreset):
        from Genesis9.charaktere import G9charaktere
        from Genesis9.formung import G9formung
        from Genesis9.koerpernetz import G9koerpernetz
        eintrag = G9charaktere.eintrag(figur) or G9charaktere.eintrag('basis')
        # Dieselbe Formung wie Bewegung, Mimik und Gelenkkorrektur (`G9formung.aus_abfrage(regler)`), A-Pose, Grundstufe (die Hautunterteilung macht der Figurcache)
        return G9koerpernetz(G9formung.aus_abfrage(regler, {}), eintrag, hautpreset=hautpreset, anhaenge=True, stufen=0).bauen()

    # ------------------------------------------------------------- Browser-GLB

    @classmethod
    def _feld(cls, quelle, i):
        a = quelle.j['accessors'][i]
        bv = quelle.j['bufferViews'][a['bufferView']]
        art = np.dtype(cls.TYPEN[a['componentType']])
        k = cls.ANZAHL[a['type']]
        schritt = bv.get('byteStride') or art.itemsize * k
        w = np.ndarray((a['count'], k), dtype=art, buffer=quelle.bin, offset=bv.get('byteOffset', 0) + a.get('byteOffset', 0), strides=(schritt, art.itemsize)).copy()
        return w.astype(np.float64) / np.iinfo(art).max if a.get('normalized') and art.kind in 'ui' else w

    def _abweichung(self, quelle, glb):
        """Größte Entfernung (m) gleichnamiger Gelenke: Browser aus den inversen Bindmatrizen des ersten Skins, Server aus `kopf` der Stand-Knochen → (Abweichung, Zahl)."""
        skins = quelle.j.get('skins') or []
        if not skins:
            return 0.0, 0
        matrizen = self._feld(quelle, skins[0]['inverseBindMatrices'])
        server = {k['name']: np.asarray(k['kopf'], dtype=np.float64) for k in glb.knochen}
        weit, zahl = 0.0, 0
        for knoten, m in zip(skins[0]['joints'], matrizen, strict=True):
            name = quelle.j['nodes'][knoten].get('name')
            if name in server:
                lage = np.linalg.inv(m.reshape(4, 4).T)[:3, 3]
                weit, zahl = max(weit, float(np.linalg.norm(lage - server[name]))), zahl + 1
        return weit, zahl

    def _bild(self, quelle, glb, material):
        """Die Farbtextur eines Browser-Materials als Textur der Stand-GLB oder None. Je Bildinhalt einmal: Die Stücke der KI tragen dasselbe Bild als eigenes glTF-Bild
        (Test edgar: drei Stücke, dreimal dieselben 6,5 MB)."""
        from PIL import Image
        tex = (material.get('pbrMetallicRoughness') or {}).get('baseColorTexture')
        if tex is None:
            return None
        quelle_nr = quelle.j['textures'][tex['index']]['source']
        bv = quelle.j['bufferViews'][quelle.j['images'][quelle_nr]['bufferView']]
        roh = bytes(quelle.bin[bv.get('byteOffset', 0):bv.get('byteOffset', 0) + bv['byteLength']])
        with Image.open(io.BytesIO(roh)) as b:
            return glb._bild_aus(b.copy(), ('stueck', hashlib.md5(roh).hexdigest()))

    @staticmethod
    def _farben(glb, s):
        """Die Punktfarben des Stücks (linear, wie glTF `COLOR_0`) an das Netz, das `Standmodellglb._netz` eben angelegt hat — mit denselben Punkten wie dort (nur die genutzten)."""
        dreiecke = np.asarray(s['dreiecke'], dtype=np.int64).reshape(-1)
        if s.get('farben') is None or not len(dreiecke):
            return
        primitiv = glb.gltf['meshes'][-1]['primitives'][0]
        primitiv['attributes']['COLOR_0'] = glb._zugriff(s['farben'][np.unique(dreiecke)], glb.FLOAT, 'VEC3', glb.ARRAY)

    @staticmethod
    def _srgb(linear):
        """glTF-Farbfaktor (linear) → sRGB 0…1 (`Standmodellglb._netz` rechnet wieder linear)."""
        c = np.clip(np.asarray(linear, dtype=np.float64)[:3], 0.0, 1.0)
        return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055)

    def stuecke(self, quelle, deckend=None):
        """Alle Netze der Browser-GLB außer Körper und Anhängen, je Primitive ein Stück `kleidung__eigen_foto_<name>__<n>_g<k>` (ohne Bild `eigen_farbe_`) → `[{name, punkte, dreiecke, normalen, uv,
        haut, material, faktor, maske, deckt}]`; `deckt`: verdeckt die Haut darunter (`Exportleistehautmaske`) — deckendes Material und, wenn die Seite sie nennt
        (`deckend`: Knotennamen, `Exportleistefigur.hautDeckt`), eines ihrer Stücke.

        `eigen_foto_` wie die Fotostücke von 2D3D Kleider: Nur so gibt das Werkstoffprofil des Renders (`profil_generisch.json`, Regel `^kleidung__(gc_|eigen_foto_)`) ihnen
        die Textur, und die Stoffsimulation lässt sie starr (gehäutet wie im Browser). Mit `kleidung__stueck__…` kamen sie einfarbig grau (Regel `^kleidung__` → `farbe`),
        gesehen im Render vom 31.10.2026 an Test edgar. Ein Stück OHNE Bild heißt `kleidung__eigen_farbe_…` (nur Regel `^kleidung__`: `farbe` mit seiner eigenen Farbe) — als
        `eigen_foto_` verlangte das Profil ein Bild, und Mitsuba brach ab (`Material.woerterbuch`: KeyError 'bild', 2d-3d-AI EdgarTrip, 31.10.2026). Trägt es Punktfarben
        (`COLOR_0`; EdgarTrip: alle fünf Stücke, UV überall 0, `_wegwerf/exportleiste/stueck_attribute_probe.py`), gehen sie als `farben` mit in die Render-GLB (`_farben`), und der
        Render rechnet Faktor × Punktfarbe wie glTF (`Figurcache`: `punktfarben`, `Mitsubafilm`); bis zum Abend des 31.10.2026 bekam das Stück nur ihr Mittel, Verläufe fehlten.
        """
        j, aus = quelle.j, []
        for nr, knoten in enumerate(j.get('nodes', [])):
            name = knoten.get('name') or ''
            if knoten.get('mesh') is None or self.EIGEN.match(name):
                continue
            skin = j['skins'][knoten['skin']] if knoten.get('skin') is not None else None
            knochen = [j['nodes'][g].get('name') for g in skin['joints']] if skin else []
            slug = re.sub(r'[^A-Za-z0-9]+', '_', name.replace('genesis9_kleid_', '')).strip('_') or 'stueck'
            for k, p in enumerate(j['meshes'][knoten['mesh']]['primitives']):
                a = p['attributes']
                if p.get('mode', 4) != 4 or 'POSITION' not in a:
                    continue
                punkte = self._feld(quelle, a['POSITION']).astype(np.float64)
                dreiecke = self._feld(quelle, p['indices']).reshape(-1, 3) if 'indices' in p else np.arange(len(punkte)).reshape(-1, 3)
                haut = {'knochen': knochen, 'index': self._feld(quelle, a['JOINTS_0']), 'gewicht': self._feld(quelle, a['WEIGHTS_0'])} if skin and 'JOINTS_0' in a else None
                material = j['materials'][p['material']] if p.get('material') is not None else {}
                pbr = material.get('pbrMetallicRoughness') or {}
                faktor = pbr.get('baseColorFactor') or [1.0, 1.0, 1.0]
                maske = {'BLEND': 'BLEND', 'MASK': True}.get(material.get('alphaMode'), False)
                art = 'foto' if pbr.get('baseColorTexture') is not None else 'farbe'
                farben = self._feld(quelle, a['COLOR_0'])[:, :3].astype(np.float64) if art == 'farbe' and 'COLOR_0' in a else None
                aus.append({'name': 'kleidung__eigen_%s_%s__%d_g%d' % (art, slug, nr, k), 'punkte': punkte, 'dreiecke': dreiecke,
                            'normalen': self._feld(quelle, a['NORMAL']) if 'NORMAL' in a else None, 'uv': self._feld(quelle, a['TEXCOORD_0']) if 'TEXCOORD_0' in a else None,
                            'haut': haut, 'material': material, 'faktor': faktor, 'farben': farben, 'maske': maske,
                            'deckt': not maske and (deckend is None or name in deckend)})
        return aus
