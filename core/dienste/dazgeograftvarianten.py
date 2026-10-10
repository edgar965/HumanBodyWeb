# -*- coding: utf-8 -*-
"""Dazgeograftvarianten — die Genital-Texturen der Charaktere als Varianten des Geografts-Stücks (10.10.2026).

Edgar, 10.10.2026: „hat Damira Modell und die anderen nun auch eine eigene Scham, die mit dem Modell mitkam? Kannst du das überprüfen und portieren?"
GEMESSEN (Install-Manager-Manifeste und alle Materialpresets unter `People/Genesis 9/Characters`, 10.10.2026): Vier Charaktere bringen Texturen für das WEIBLICHE
Geograft (`#Genesis9FemaleGenitalia-1`, Gruppe `Genitalia`) mit — MB Allyne und MB Olesia (`… Gens MAT`: Farbe, SSS, Glanz, Bump, Normalen), NW Damira
(`Anatomical Elements`: `Damira_genital*.jpg`) und P3D Ursula (`Complete Texture …`, dazu `Genitalia Wet Skin Apply/REM`). Kein Charakter bringt Formmorphe für die Genitalien mit,
und KEIN Charakter bringt Texturen für das männliche Geograft (Hirai & Co. sind nicht installiert); die Basishaut `G9 Feminine|Masculine Skin 01` hat keine Gruppe `Genitalia`.

Ein Materialpreset, das eine Gruppe des Stücks belegt, gilt als Variante des Stücks (`G9garderobeeintrag.varianten`, zweite Schleife) — aber nur, wenn es im Ordner des
Stücks liegt. Hier wird je Charakter eine Kopie des Presets neben das Stück geschrieben (`Daz Anatomie Frau <Charakter>.duf`), die Gruppe `Genitalia` darin umbenannt in die des
Stücks (`Dazgeograft.GRUPPEN`: „Genitalia Frau" | „Genitalia Mann" — mit demselben Namen zählte die Suche die Texturen der Frau auch beim Mann). Die Bilder bleiben in
der Daz-Bibliothek (Adressen `/Runtime/Textures/…`), nichts davon wird kopiert.
"""
import gzip
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

__all__ = ['Dazgeograftvarianten']


class Dazgeograftvarianten:
    GEOMETRIE = {'mann': '#Genesis9MaleGenitalia-1', 'frau': '#Genesis9FemaleGenitalia-1'}
    GRUPPE = 'Genitalia'
    PRESETS = ('preset_material', 'preset_hierarchical_material')
    #: Presets, die nichts belegen (Entfernen) oder dasselbe nochmals (`!All` trägt die Gruppen aller Teile der Figur).
    AUSLASSEN = re.compile(r'!All| REM$', re.I)

    @classmethod
    def finden(cls, geschlecht):
        """`[(Anzeigename, Pfad)]`: Materialpresets der Charaktere, die die Gruppe `Genitalia` des Geografts belegen — je Bildsatz eines (die Zweige mit/ohne Brauen
        sind für das Geograft gleich)."""
        from Genesis9.pfade import G9pfade

        wurzel = G9pfade.people() / 'Characters'
        gesehen, aus = set(), []
        if not wurzel.is_dir():
            return aus
        for datei in sorted(wurzel.rglob('*.duf')):
            if cls.AUSLASSEN.search(datei.stem):
                continue
            doc = cls._lesen(datei)
            if not doc or (doc.get('asset_info') or {}).get('type') not in cls.PRESETS:
                continue
            bilder = cls._bilder(datei, doc, geschlecht)
            if not bilder or tuple(bilder) in gesehen:
                continue
            gesehen.add(tuple(bilder))
            aus.append((cls.anzeige(datei, wurzel), datei))
        return aus

    @classmethod
    def schreiben(cls, stueck_duf, geschlecht, gruppe):
        """Je gefundenem Preset eine Kopie neben `stueck_duf` — `<Stück> <Charakter>.duf`, die Gruppe `Genitalia` umbenannt in `gruppe` (die des Stücks). Gibt die Namen
        zurück; alte Kopien derselben Namen werden ersetzt."""
        stueck_duf = Path(stueck_duf)
        namen = []
        for anzeige, quelle in cls.finden(geschlecht):
            doc = cls._umbenennen(cls._lesen(quelle), gruppe)
            cls._ablegen(stueck_duf, anzeige, doc)
            namen.append(anzeige)
            nass = cls._nass(quelle)
            if nass is not None:
                cls._ablegen(stueck_duf, anzeige + ' nass', cls._ueberlagern(doc, cls._umbenennen(nass, gruppe)))
                namen.append(anzeige + ' nass')
        cls._melden(stueck_duf)
        return namen

    @classmethod
    def _umbenennen(cls, doc, gruppe):
        """Die Gruppe `Genitalia` des Presets in `gruppe` umbenannt (die des Stücks)."""
        # Die Gruppe steht dreifach im Preset: `groups` des Szenenmaterials, `url` darauf und `id` des Bibliothekseintrags — `G9material` liest sie von dort.
        for m in (doc.get('scene') or {}).get('materials') or []:
            m['groups'] = [gruppe if g == cls.GRUPPE else g for g in m.get('groups') or []]
            if m.get('url') == '#' + cls.GRUPPE:
                m['url'] = '#' + gruppe
        for m in doc.get('material_library') or []:
            if m.get('id') == cls.GRUPPE:
                m['id'] = gruppe
        # Die Bilder legen die Charakter-Presets über `scene.animations` fest: `#materials/Genitalia:?extra/…/image_file` — die Gruppe steht in der Adresse.
        for a in (doc.get('scene') or {}).get('animations') or []:
            if isinstance(a.get('url'), str):
                a['url'] = a['url'].replace('#materials/%s:' % cls.GRUPPE, '#materials/%s:' % quote(gruppe))
        return doc

    @classmethod
    def _nass(cls, textur_preset):
        """Das Preset `… Genitalia Wet Skin Apply` im Ordner des Texturpresets (Ursula, P3D) — oder None. Es setzt keine Bilder, nur Glanzwerte der Gruppe `Genitalia`:
        `Specular Lobe 1 Roughness` 0,3 statt 0,8 (gemessen 10.10.2026: dasselbe Rauheitsbild `P3DUrsula_Genitalia_R.jpg`, Glanzgewicht 1)."""
        for datei in sorted(Path(textur_preset).parent.glob('*Genitalia Wet Skin Apply.duf')):
            doc = cls._lesen(datei)
            if doc and (doc.get('asset_info') or {}).get('type') in cls.PRESETS:
                return doc
        return None

    @staticmethod
    def _ueberlagern(basis, nass):
        """Die Zeilen von `nass` (`scene.animations`) über die von `basis`: gleicher Kanal ersetzt, neuer hängt an — `G9material` nimmt je Kanal die ERSTE Zeile, anhängen allein
        änderte nichts. Der Kanal ist die Adresse ab `#materials/` (davor steht beim Texturpreset der Knoten `…Genesis9FemaleGenitalia`, beim Wet-Skin-Preset `name://@selection`)."""
        def kanal(a):
            return str(a.get('url')).split('#materials/', 1)[-1]

        zeilen = list((basis.get('scene') or {}).get('animations') or [])
        stelle = {kanal(a): i for i, a in enumerate(zeilen)}
        for a in (nass.get('scene') or {}).get('animations') or []:
            if kanal(a) in stelle:
                zeilen[stelle[kanal(a)]] = a
            else:
                zeilen.append(a)
        basis.setdefault('scene', {})['animations'] = zeilen
        return basis

    @staticmethod
    def _ablegen(stueck_duf, anzeige, doc):
        """`<Stück> <anzeige>.duf` neben das Stück schreiben (über eine `.neu`-Datei, nie halb)."""
        ziel = stueck_duf.with_name('%s %s.duf' % (stueck_duf.stem, anzeige))
        neben = ziel.with_name(ziel.name + '.neu')
        neben.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        neben.replace(ziel)

    @classmethod
    def hautton(cls, stueck_duf, geschlecht, gruppe, name, rgb):
        """Eine Variante OHNE Bilder neben `stueck_duf`: nur die Diffusfarbe (sRGB 0 … 255) der Gruppe `gruppe` — für ein Modell, dessen Haut eine Fototextur trägt (cute girl:
        Median der Beine-Kachel 1003 = 214/168/155, gemessen 10.10.2026) und das Stück sonst in der Mittelfarbe der Basishaut stünde. Gibt den Namen der Variante zurück.
        Die Farbe liegt im Material, nicht in der Umfärbung des Browsers: deren Shader-Patch ließ am oberen Rand des Stücks eine dunkle Linie stehen (gesehen 10.10.2026)."""
        stueck_duf = Path(stueck_duf)
        farbe = [round(float(w) / 255.0, 4) for w in rgb]
        ziel = stueck_duf.with_name('%s %s.duf' % (stueck_duf.stem, name))
        doc = {'file_version': '0.6.0.0',
               'asset_info': {'id': '/' + ziel.relative_to(cls._bibliothek(ziel)).as_posix(), 'type': 'preset_material',
                              'contributor': {'author': 'HumanBody', 'email': '', 'website': ''}, 'revision': '1.0'},
               'scene': {'materials': [{'id': gruppe + '-1', 'url': '#' + gruppe, 'geometry': cls.GEOMETRIE[geschlecht], 'groups': [gruppe],
                                        'diffuse': {'channel': {'type': 'color', 'name': 'Diffuse Color', 'value': farbe, 'current_value': farbe}}}]}}
        neben = ziel.with_name(ziel.name + '.neu')
        neben.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
        neben.replace(ziel)
        cls._melden(stueck_duf)
        return name

    @classmethod
    def _melden(cls, stueck_duf):
        """Den Marker des Stücks (`Runtime/Support/EIGEN_EIGEN_<Stück>.dsx`) berühren — an seinem Stand merkt ein laufender Server (`G9eigenstand`), dass die eigene
        Wurzel sich geändert hat und die Garderobenliste neu zu lesen ist; eine neue Variante allein verändert ihn nicht."""
        marker = cls._bibliothek(stueck_duf) / 'Runtime' / 'Support' / ('EIGEN_EIGEN_%s.dsx' % Path(stueck_duf).stem.replace(' ', '_'))
        if marker.is_file():
            os.utime(marker)

    @staticmethod
    def _bibliothek(datei):
        """Die Wurzel (`…/bibliothek`), unter der `datei` liegt — für die Adresse `/People/…` im Preset."""
        for eltern in Path(datei).parents:
            if eltern.name == 'People':
                return eltern.parent
        raise ValueError('%s liegt nicht unter People/' % datei)

    @staticmethod
    def anzeige(datei, wurzel):
        """Name des Charakters aus dem Ordner (`Characters/<Hersteller>/<Charakter>/Materials/…`), „nass" bei Ursulas Wet Skin."""
        teile = datei.relative_to(wurzel).parts
        name = teile[1] if len(teile) > 2 else datei.stem
        return name + (' nass' if re.search(r'wet', datei.stem, re.I) else '')

    @classmethod
    def _bilder(cls, datei, doc, geschlecht):
        """Was das Preset der Gruppe `Genitalia` des Geografts `geschlecht` gibt (`['kanal=bild', …]`, sortiert) — leer, wenn es die Gruppe nicht oder für das andere
        Geschlecht belegt oder kein Farbbild hat. Die Bilder liest `G9material.bilder_aus` (dasselbe wie die Garderobe für jede Variante).
        Ein Preset ohne Geometrieangabe (Ursulas Wet Skin) gilt nur für das weibliche Geograft: kein Charakter des Mannes bringt Genitaltexturen."""
        from Genesis9.material import G9material

        gesucht = cls.GEOMETRIE[geschlecht]
        passt = any(cls.GRUPPE in (m.get('groups') or []) and (m.get('geometry') == gesucht or (m.get('geometry') is None and geschlecht == 'frau'))
                    for m in (doc.get('scene') or {}).get('materials') or [])
        gruppe = G9material.bilder_aus(datei).get(cls.GRUPPE) if passt else None
        if not gruppe or not gruppe.get('albedo'):
            return []
        return sorted('%s=%s' % (kanal, wert) for kanal, wert in gruppe.items() if kanal in ('albedo', 'normalen', 'rauheit', 'glanz', 'durchlicht'))

    @staticmethod
    def _lesen(pfad):
        try:
            roh = Path(pfad).read_bytes()
            return json.loads((gzip.decompress(roh) if roh[:2] == b'\x1f\x8b' else roh).decode('utf-8'))
        except (OSError, ValueError):
            return None
