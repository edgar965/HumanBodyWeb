# -*- coding: utf-8 -*-
"""Mesh3daitesteigenstueck — ein Stück „aus dem Netz“ (Weg b eines Tests von Mesh3D-AI) als eigenes Genesis-Stück in die Garderobe (17.10.2026 nachts).

Ein gespeichertes Genesis-Modell trägt nur Stücke der Garderobe (`figur.kleidung`); ein Objekt aus dem Netz muss also erst eines werden. Derselbe Weg wie der Blend-Import (`Blendimportstuecke.stueck`):
OBJ mit Textur in der Ruhelage der vorhergesagten Figur → `G9eigenstueck.schreiben` (Gewichte der 3 nächsten Hautpunkte; Haar und starre Bestandteile ganz an EINEM Knochen) → die Ruhelage auf die
GRUNDFIGUR zurückrechnen (`G9gcfigurbau.ruhelage`, Regler der vorhergesagten Figur) → neu schreiben. So folgt das Stück jeder Genesis-Figur und allen Körpermorphs (`G9folger`).

Das Stück liegt danach in `3DObjects/models/Genesis9/bibliothek` (eigene Stücke, Hersteller EIGEN) und in der Garderobe unter seiner Kategorie; der Arbeitsordner (`eigene_stuecke/<Kennung>`) trägt OBJ und Bilanz.
Ein zweites Übernehmen desselben Stücks (gleiches Anzeigenetz, gleiche Regler) nimmt das schon geschriebene (`eigenstueck.json` neben dem Anzeigenetz) — `G9gcfigurbau` kostet Minuten.
"""

import hashlib
import json
import logging
import shutil

import numpy as np

logger = logging.getLogger(__name__)

__all__ = ['Mesh3daitesteigenstueck']


class Mesh3daitesteigenstueck:
    FASSUNG = 1
    #: Region des Stücks → Ordner für `G9mbkategorien.fuer` (Kopfbedeckung und Haar haben eigene Kategorien).
    ORDNER = {'oberteil': 'tops', 'hose': 'pants', 'schuhe': 'shoes', 'zubehoer': 'accessories', 'teil': 'accessories'}
    KOPF_KATEGORIE = ('Follower/Wardrobe/Headwear', '/Default/Wardrobe/Headwear')
    HAAR_KATEGORIE = ('Follower/Hair', '/Default/Hair')
    #: Folgt das geschriebene Stück dem Ziel schlechter als so (p99, mm), rechnet ein zweiter Durchgang gegen die gelesene Datei nach (wie `Blendimportstuecke.NACHRECHNEN_MM`).
    NACHRECHNEN_MM = 3.0

    def __init__(self, stueck_ordner, stueck, regler, praefix, rig_namen):
        """`stueck_ordner`: `kleider_<g>/b/<id>` (mit `anzeige/`); `stueck`: Eintrag aus `stuecke.json`; `regler`: Stellung der vorhergesagten Figur; `praefix`: Anfang des Stücknamens
        („<Modell>“); `rig_namen`: die 138 Knochennamen in der Reihenfolge des Anzeigenetzes (für starre Stücke)."""
        self.ordner = stueck_ordner
        self.stueck = stueck
        self.regler = dict(regler)
        self.praefix = praefix
        self.rig_namen = list(rig_namen)

    def _marke(self):
        h = hashlib.sha1()
        for datei in ('netz.npz', 'materialien.json'):
            h.update((self.ordner / 'anzeige' / datei).read_bytes())
        h.update(json.dumps(self.regler, sort_keys=True).encode('utf-8'))
        h.update(self.praefix.encode('utf-8'))
        return '%d:%s' % (self.FASSUNG, h.hexdigest()[:16])

    def holen(self):
        """`{stueck, name, …}` — das geschriebene Stück (gemerkt) oder neu gebaut."""
        from Genesis9.garderobe import G9garderobe
        marke = self._marke()
        merk = self.ordner / 'eigenstueck.json'
        try:
            alt = json.loads(merk.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            alt = {}
        if alt.get('marke') == marke and G9garderobe.eintrag(alt.get('stueck')) is not None:
            return dict(alt, gemerkt=True)
        bilanz = self.bauen()
        bilanz['marke'] = marke
        merk.write_text(json.dumps(bilanz, ensure_ascii=False, indent=1), encoding='utf-8')
        return bilanz

    def _art(self):
        """(Kategorie, Ordnerart, Knochen) — Haar und starre Bestandteile an EINEM Knochen."""
        from Genesis9.mbkategorien import G9mbkategorien
        st = self.stueck
        if st.get('art') == 'haar':
            return self.HAAR_KATEGORIE, 'Hair', 'head'
        uebertrag = (st.get('b') or {}).get('uebertrag') or {}
        knochen = self.rig_namen[int(uebertrag['knochen'])] if uebertrag.get('art') == 'starr' and uebertrag.get('knochen') is not None else None
        if st.get('region') == 'kopf':
            return self.KOPF_KATEGORIE, 'Clothing', knochen or 'head'
        name = '%s %s' % (self.praefix, st.get('name'))
        return G9mbkategorien.fuer(self.ORDNER.get(st.get('region'), 'tops'), name), 'Clothing', knochen

    def bauen(self):
        from Genesis9.eigenstueck import G9eigenstueck
        from Genesis9.gcfigurbau import G9gcfigurbau
        from Genesis9.objleser import G9objleser

        from .blendimportbilder import Blendimportbilder

        anzeige = self.ordner / 'anzeige'
        with np.load(anzeige / 'netz.npz') as z:
            punkte = np.asarray(z['ruhe'], dtype=np.float64)
            dreiecke = np.asarray(z['dreiecke'], dtype=np.int64)
            uv = np.asarray(z['uv'], dtype=np.float64)
        mat = json.loads((anzeige / 'materialien.json').read_text(encoding='utf-8'))[0]
        kennung, anzeige_name = G9eigenstueck.kennung_und_name('%s %s' % (self.praefix, self.stueck.get('name')))
        arbeit = G9eigenstueck.arbeitsordner(kennung)
        arbeit.mkdir(parents=True, exist_ok=True)
        bild = None
        if mat.get('bild'):
            bild = arbeit / ('%s_farbe.jpg' % kennung)
            shutil.copyfile(anzeige / 'bilder' / mat['bild'], bild)
        lin = np.asarray(mat.get('farbe') or [1.0, 1.0, 1.0], dtype=np.float64)
        farbe = tuple(round(float(Blendimportbilder.srgb(w)), 4) for w in lin) if bild is None else (1.0, 1.0, 1.0)
        material = {'name': kennung + '_Mat', 'farbe': farbe, 'bild': str(bild) if bild else None, 'normalen': None, 'rauheit_bild': None, 'alpha_bild': None,
                    'detailnormalen': None, 'detail_kachel': None, 'alpha_schwelle': None, 'shininess': None, 'opacity': None}
        obj = Blendimportbilder.obj(arbeit, punkte, dreiecke, uv[dreiecke].reshape(-1, 2), material)
        netz = G9objleser.lesen(str(obj))
        roh = np.asarray(netz['punkte'], dtype=np.float64)
        kategorie, art, knochen = self._art()

        def schreiben(lage):
            return G9eigenstueck.schreiben(lage, netz, kennung, anzeige_name, kategorie, material, heben=False, knochen=knochen, art_ordner=art)

        bilanz = schreiben(roh)
        ruhe, bericht = G9gcfigurbau.ruhelage(bilanz['stueck'], self.regler, roh, roh)
        bilanz = schreiben(ruhe)
        angezogen = G9gcfigurbau.pruefen(bilanz['stueck'], self.regler, roh)
        if angezogen['p99_mm'] > self.NACHRECHNEN_MM and art != 'Hair':
            ruhe2, bericht2 = G9gcfigurbau.ruhelage(bilanz['stueck'], self.regler, roh, ruhe)
            bilanz2 = schreiben(ruhe2)
            angezogen2 = G9gcfigurbau.pruefen(bilanz2['stueck'], self.regler, roh)
            if (angezogen2['p99_mm'], angezogen2['max_mm']) < (angezogen['p99_mm'], angezogen['max_mm']):
                bilanz, bericht, angezogen = bilanz2, dict(bericht2, zweiter_durchgang=True), angezogen2
            else:
                bilanz = schreiben(ruhe)
                bericht['zweiter_durchgang'] = 'verworfen'
        logger.info('Mesh3D-AI Test: eigenes Stück %s (%s) — angezogen %s', bilanz['stueck'], anzeige_name, angezogen)
        return {'stueck': bilanz['stueck'], 'name': anzeige_name, 'kennung': kennung, 'punkte': bilanz['punkte'], 'flaechen': bilanz['flaechen'],
                'kategorie': list(kategorie), 'knochen': bilanz.get('knochen'), 'angezogen': angezogen, 'ruhelage': {k: v for k, v in bericht.items() if not isinstance(v, (list, dict))}}
