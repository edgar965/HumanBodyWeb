# -*- coding: utf-8 -*-
"""Blendimportweg — welchen Weg ein Auftrag der Jobseite „Mesh-3D“ geht (11.10.2026).

Edgar (11.10.2026): „nimm das als Modell“ — `wizard character 3d model_Best.glb`, eine GLB aus Tripo: EIN Netz (1.013.572 Punkte, 1.935.797 Dreiecke), kein Skelett, ein Material, 0,98 m hoch (ein Bild-zu-3D-Netz hat keinen
Maßstab). Die Kette des Modell-Imports (`Blendimportlauf`) setzt getrennte Objekte mit Rollen voraus: einen Körper, daneben Kleider und Haar. Ein verschmolzenes Netz hat nur den „Körper“ — in Kleidung, Hut und Bart
eingewickelt, kein nackter Körper darunter. Darum zwei Wege (Konzept `Docu/konzepte/2026-10-11_mesh-3d-konzept.md`, Abschnitt 2):

    teile   getrennte Objekte (.blend, FBX, OBJ, GLB mit mehreren Netzen): Blender liest, Rollen, Körper nackt, Kleider und Haar als Genesis-Stücke, Haut backen — die ganze Kette
    netz    ein verschmolzenes Netz (GLB mit EINEM Netz ohne Skelett): `koerper` (das Netz auf Menschenhöhe bringen, `Blendimportnetz`), `pose` (SAM 3D Body, wenn gewählt), `figur` („Mesh to 3D“ auf dem GANZEN Netz
            wie auf dem Reiter „Mesh to 3D“: Regler, Gesicht, Eigenmorph, Frisur, Haut aus dem Netz, Modell `<Name> Mesh`) — kein Blender, keine Stücke aus dem Netz, keine gebackene Originalhaut

Die Wahl trifft `erkennen` beim Anlegen (an der Datei, ohne Blender) und schreibt sie in den Stand (`stand.weg`); ein Stand ohne `weg` ist „teile“. Der Weg „netz“ liest nur GLB — OBJ und FBX bleiben bei Blender.
**Nicht gebaut:** Kleidung und Haar als Genesis-Stücke aus einem verschmolzenen Netz (das kann „2D3D Kleider“, Schritt „Kleiderstücke“); der Weg „netz“ trägt am Ende die Frisur, die „Mesh to 3D“ wählt.
"""

import json
import struct

__all__ = ['Blendimportweg']


class Blendimportweg:
    TEILE = 'teile'
    NETZ = 'netz'
    #: Die Schritte des Wegs „netz“ (Namen aus `Blendimportlauf.SCHRITTE`, dieselben Karten wie beim Weg „teile“).
    NETZ_SCHRITTE = ('koerper', 'segmentierung', 'pose', 'figur')
    #: Die Bänder des Fortschrittsbalkens (Prozent) für diesen Weg: er endet nach „figur" (das Modell speichert „Mesh to 3D“ selbst), also füllt „figur" den Rest bis 100.
    #: Nach den Zeiten am Zauberer (11.10.2026): Körper 12 s, Segmentierung 200,7 s, Pose 97,3 s, Figur rund 1.750 s von rund 2.060 s.
    NETZ_BAENDER = {'koerper': (0, 1), 'segmentierung': (1, 11), 'pose': (11, 16), 'figur': (16, 100)}
    #: Vorgaben des Wegs „netz“ (13.10.2026, Konzept „Mesh-3D ohne Nacharbeit“): Aus dem Katalog kommen sie nicht — der gilt für alle Wege (Weg „teile“: Pose `aus`, Stoffzug ohne Wirkung).
    #: `pose = sam`: alle 12 Aufträge dieses Wegs liefen so (SAM 3D Body findet die Gelenke am Rendering; ~12 s warm, 75 s kalt, `meshfigur-tempo.md`).
    #: `kleidung_zug = ignorieren` (seit 13.10.2026 abends; vorher `nah`, davor `weich`), gemessen an drei Modellen (Tagebuch 13.10.2026, Abschnitt 8): anliegende Kleidung (Edgar, `nah` → `ignorieren`) Figur→Netz 2,41 → 2,48 mm, Netz→Figur 2,58 → 2,52 mm, Höhe
    #: 199,7 → 199,8 cm — kein Unterschied; lockere Kleidung: Robe Oberschenkel 51,8 (`ignorieren`) gegen 68,9 cm (`nah`) und 103,5 (`weich`), Reifenrock Taille 58,6 gegen 73,3 cm, Hüfte 86,2 gegen 98,3 cm. Preis von `ignorieren`: der Stoff steht öfter im Körper
    #: (Reifenrock 9,7 gegen 3,5 %). Die automatische Vergleichsvariante (`Mesh3dvariantenauto`) rechnet `nah` mit. Nicht gemessen: Polstertänzer (`nah`), Damira ist nackt (der Zug wirkt dort nicht).
    VORGABEN_NETZ = {'pose': 'sam', 'kleidung_zug': 'ignorieren'}
    #: Einstellungen, die am Modell hängen und darum nie vom zuletzt angelegten Auftrag geerbt werden: das Formular „Neuer Auftrag“ schickt sie nicht mit (`Mesh3dneu`), der Server nimmt die Vorgabe des Wegs.
    MODELLABHAENGIG = ('pose', 'pose_drehung', 'kleidung_zug')

    @classmethod
    def pruefen(cls, wert):
        return wert if wert in (cls.TEILE, cls.NETZ) else cls.TEILE

    @staticmethod
    def glb_json(datei):
        """Der JSON-Block einer GLB (liest nur den Anfang der Datei, nicht die 67 MB)."""
        with open(str(datei), 'rb') as f:
            kopf = f.read(20)
            if len(kopf) < 20 or kopf[:4] != b'glTF':
                raise ValueError('Keine GLB-Datei: %s' % datei)
            laenge, art = struct.unpack('<I4s', kopf[12:20])
            if art != b'JSON':
                raise ValueError('GLB ohne JSON-Block am Anfang: %s' % datei)
            return json.loads(f.read(laenge).decode('utf-8'))

    @classmethod
    def erkennen(cls, format, datei):
        """`(weg, grund)` — „netz“ nur für eine GLB mit höchstens einem Netzknoten und ohne Skin; alles andere liest Blender."""
        if format != 'glb':
            return cls.TEILE, 'Blender liest die Datei (%s)' % format
        daten = cls.glb_json(datei)
        netze = [n for n in daten.get('nodes') or [] if 'mesh' in n]
        if daten.get('skins'):
            return cls.TEILE, 'die GLB hat ein Skelett (%d Skins)' % len(daten['skins'])
        if len(netze) > 1:
            return cls.TEILE, 'die GLB hat %d Netze — getrennte Teile' % len(netze)
        return cls.NETZ, 'ein einziges Netz ohne Skelett — verschmolzen'
