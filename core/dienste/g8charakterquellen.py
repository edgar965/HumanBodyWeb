# -*- coding: utf-8 -*-
u"""G8charakterquellen — welche Genesis-8-Charaktere es gibt, welche Morphs sie setzen und woher ihre Haut kommt (16.11.2026).

Für `G8charakteraufgenesis`. Drei Bauarten in der Bibliothek (gesichtet 16.11.2026):

1. CHARAKTERPRESET (`"type": "character"`, Katyee KT Margie/Poppy/Quail, Pekmez JamesF, RAJ 3D Sakshi, Paspu Barbossa unter `Charakter/`):
   die gesetzten Morphs stehen als `modifiers` mit `url` und `current_value`.
2. APPLY-SATZ ohne Charakterpreset (Lintang07 Jodie Foster, Luwiana): `<Name> Body Apply.duf` und `<Name> Head Apply.duf` (`preset_shape`)
   setzen je einen Morph über seinen Namen (`name://@selection#Jodie%20Foster%20Body:?value/value` = 1). Die Morphdatei heißt wie der Morph
   und liegt im Morph-Ordner der Figur (`data/DAZ 3D/Genesis 8/Female/Morphs/**/<Name>.dsf`).
3. HAUT: im Preset selbst (Katyee) oder als Material-Preset im Charakterordner (JamesF `JamesF  Skin.duf`, Lintang07): das erste Preset, das
   den Gruppen Face UND Torso ein Bild gibt — Namen mit „skin“/„full body“ zuerst.
4. MORPHPAKET ohne Preset (18.11.2026, InTheFlesh Dante DMC5): ein Zip mit nur Formmorphs für Genesis 8 (`_aus_paketen`), ohne Haut.
Die Apply-Sätze liest `G9charakterapply` (gemeinsam mit Genesis 9).
"""
import re
from pathlib import Path
from urllib.parse import unquote

from Genesis9.charakterapply import G9charakterapply
from Genesis9.charakterpresets import G9charakterpresets
from Genesis9.dazpaket import G9dazpaket
from Genesis9.dson import G9dson
from Genesis9.g8morphe import G9g8morphe
from Genesis9.material import G9material
from Genesis9.pfade import G9pfade

__all__ = ['G8charakterquellen']


class G8charakterquellen:
    u"""Aufträge, Morphverweise, Hautquelle."""

    #: Figurordner -> (Klon, Figurdatei, Geschlecht, Morph-Ordner unter `data/DAZ 3D/Genesis 8/`).
    FIGUREN = {'Genesis 8 Female': ('CloneGenesis8Female', 'Genesis8Female', u'weiblich', 'Female'),
               'Genesis 8 Male': ('CloneGenesis8Male', 'Genesis8Male', u'männlich', 'Male')}
    ORDNER = ('Characters', 'Charakter')

    @classmethod
    def auftraege(cls, nur=None):
        u"""`[{kennung, datei, apply, klon, figur, geschlecht, morphordner, anzeige, reihe}]` — `nur`: Namen (Dateiname ohne Endung, beim Apply-Satz der Charaktername)."""
        aus = []
        for wurzel in G9pfade.bibliotheken():
            for figurordner, (klon, figur, geschlecht, morphordner) in cls.FIGUREN.items():
                for ordner in cls.ORDNER:
                    basis = wurzel / 'People' / figurordner / ordner
                    if basis.is_dir():
                        aus += cls._aus_ordner(basis, nur, aus, {'klon': klon, 'figur': figur, 'geschlecht': geschlecht, 'morphordner': morphordner})
        aus += cls._aus_paketen(nur, aus)
        for nr, a in enumerate(aus):
            a['reihe'] = nr
        return aus

    #: Höchstens so viele Formmorphs darf ein Paket ohne Preset tragen, um als EIN Charakter zu gelten — Setzung (18.11.2026): Dante hat
    #: einen („Combined head and body morph“), üblich sind Body + Head; ein Reglerpaket mit vielen Formen auf einmal gezogen wäre kein Charakter.
    PAKET_MORPHE = 2
    _PAKETMORPH = re.compile(r'^data/daz 3d/genesis 8/(female|male)/morphs/.+\.dsf$')

    @classmethod
    def _aus_paketen(cls, nur, bekannt):
        u"""4. MORPHPAKET (18.11.2026, InTheFlesh „Dante DmC Remake G8M“: eine Datei `data/DAZ 3D/Genesis 8/Male/Morphs/InTheFlesh/Dante DMC5/
        Dante DMC5.dsf`, README „Combined head and body morph. No textures or hair, no JCM“): ein Zip aus `G9dazpaket` (seine Dateiliste),
        das für Genesis 8 nur Formmorphs bringt und kein Preset unter `People/Genesis 8 …`. Die Morphs auf 1 sind der Charakter; die Haut
        bleibt die von Genesis 9 (`hautquelle`: None)."""
        aus = []
        vergeben = {a['kennung'] for a in bekannt}
        figur_von = {f[3].casefold(): dict(zip(('klon', 'figur', 'geschlecht', 'morphordner'), f)) for f in cls.FIGUREN.values()}
        for liste in sorted((G9pfade.eigene_daten() / G9dazpaket.ORDNER).glob('*.json')):
            stand = G9dazpaket.lesen_manifest(liste.name)
            pfade = [d['pfad'] for d in stand.get('dateien') or []]
            morphe = [p for p in pfade if cls._PAKETMORPH.match(p.casefold())]
            if not morphe or len(morphe) > cls.PAKET_MORPHE:
                continue
            if any(p.casefold().startswith('people/genesis 8') and p.casefold().endswith('.duf') for p in pfade):
                continue                                                    # mit Preset: Bauart 1 oder 2
            wurzel = Path(stand.get('bibliothek') or G9pfade.bibliothek())
            dateien = [wurzel / p for p in morphe if (wurzel / p).is_file()]
            if not dateien:
                continue
            figur = figur_von[cls._PAKETMORPH.match(morphe[0].casefold()).group(1)]
            name = dateien[0].stem
            kennung = G9g8morphe.kennung(name)
            if kennung in vergeben or (nur and name not in nur):
                continue
            vergeben.add(kennung)
            aus.append(dict(figur, kennung=kennung, datei=dateien[0], apply=[], morphe=[(d, 1.0, d.stem) for d in dateien],
                            anzeige=u'%s  (Genesis 8)' % name))
        return aus

    @classmethod
    def _aus_ordner(cls, basis, nur, bekannt, figur):
        aus = []
        vergeben = {a['kennung'] for a in bekannt}
        apply = {}
        for datei in sorted(basis.rglob('*.duf')):
            treffer = G9charakterapply.APPLY.match(datei.stem)
            if treffer:
                apply.setdefault((datei.parent, treffer.group(1)), []).append(datei)
                continue
            if nur and datei.stem not in nur or not G9charakterpresets.ist_preset(datei):
                continue
            kennung = G9g8morphe.kennung(datei.stem)
            if kennung in vergeben:
                continue                                                    # Katyee legt das Preset zweimal ab (Wurzel und Unterordner)
            vergeben.add(kennung)
            name = re.sub(r'\s+G8(\.1)?$', '', datei.stem).strip()
            aus.append(dict(figur, kennung=kennung, datei=datei, apply=[], anzeige=u'%s  (Genesis 8)' % name))
        presets = [a['datei'].stem.casefold() for a in bekannt + aus if not a['apply']]
        for (_ordner, name), dateien in sorted(apply.items()):
            kennung = G9g8morphe.kennung(name)
            if kennung in vergeben or (nur and name not in nur):
                continue
            if any(name.casefold().startswith(p) for p in presets):
                continue                                                    # „Barbossa Full Body Apply“ neben dem Preset „Barbossa“: derselbe Charakter
            vergeben.add(kennung)
            aus.append(dict(figur, kennung=kennung, datei=dateien[0], apply=dateien, anzeige=u'%s  (Genesis 8)' % name))
        return aus

    # -------------------------------------------------------------- Morphs

    @classmethod
    def verweise(cls, auftrag):
        u"""`[(Pfad der Morphdatei oder None, Wert, Bezeichnung)]` der gesetzten Morphs."""
        if auftrag.get('morphe'):
            return list(auftrag['morphe'])
        if not auftrag.get('apply'):
            aus = []
            for m in G9dson.lesen(auftrag['datei']).szene().get('modifiers') or []:
                wert = (m.get('channel') or {}).get('current_value')
                if isinstance(wert, (int, float)) and wert:
                    pfad, _kennung = G9pfade.aufloesen(m.get('url') or '')
                    aus.append((pfad if pfad is not None and pfad.is_file() else None, float(wert), unquote(str(m.get('url')))))
            return aus
        aus = []
        for datei in auftrag['apply']:
            for morph, wert in G9charakterapply.werte(datei):
                aus.append((cls._morphdatei(morph, auftrag['morphordner']), wert, morph))
        return aus

    @staticmethod
    def _morphdatei(name, morphordner):
        for wurzel in G9pfade.bibliotheken():
            ordner = wurzel / 'data' / 'DAZ 3D' / 'Genesis 8' / morphordner / 'Morphs'
            for pfad in ordner.rglob(name + '.dsf') if ordner.is_dir() else []:
                return pfad
        return None

    # ---------------------------------------------------------------- Haut

    @classmethod
    def hautquelle(cls, auftrag):
        u"""Die `.duf`, deren Materialien die Haut tragen (Face und Torso mit Bild) — oder None (dann bleibt Genesis' eigene Haut)."""
        if auftrag.get('morphe'):
            return None                                                     # Morphpaket: keine Haut im Zip
        datei = auftrag['datei']
        kandidaten = [] if auftrag.get('apply') else [datei]
        if datei.parent.name in cls.ORDNER:
            # Preset direkt unter `Characters/` (JamesF, KT Margie): nur die Ordner seiner gleichnamigen Kopien (`PekmezJamesF/JamesF.duf`) —
            # der ganze Charakterordner gäbe womöglich die Haut eines anderen Charakters.
            ordnerliste = [p.parent for p in sorted(datei.parent.rglob(datei.name)) if p != datei]
        else:
            ordnerliste = [datei.parent]
        unterordner = datei.parent / datei.stem
        for ordner in ([unterordner] if unterordner.is_dir() else []) + ordnerliste:
            kandidaten += sorted(ordner.rglob('*.duf'), key=lambda d: (not re.search(r'skin|full ?body', d.stem, re.I), str(d).lower()))
        for kandidat in kandidaten:
            bilder = G9material.bilder_aus(kandidat)
            if (bilder.get('Face') or {}).get('albedo') and (bilder.get('Torso') or {}).get('albedo'):
                return kandidat
        return None
