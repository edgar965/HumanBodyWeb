# -*- coding: utf-8 -*-
"""Fremdimporteinstellungen — die Einstellungen des Modell-Imports für OBJ und FBX (10.10.2026).

Kein zweiter Katalog: Er wird aus dem der .blend (`Blendimporteinstellungen.KATALOG`) abgeleitet — dieselben Fragen, dieselben
Vorgaben, dieselbe Prüfung und dasselbe Merken (die Klassenmethoden der Basis gelten über `cls.KATALOG` und `cls.DATEI`). Je Format
weicht nur ab: der Pfad (Titel, Hinweis), die Datei der gemerkten Werte und was gar nicht gefragt wird (`OHNE`).

Gemerkt wird je Format getrennt (`einstellungen_obj.json`, `einstellungen_fbx.json`), damit der Pfad der einen nicht den der anderen
überschreibt. **Erstes Mal:** Gibt es die Datei noch nicht, gelten die gemerkten Werte der .blend (ohne Pfad) — wer dort 4096 px
gewählt hat, bekommt es hier ebenso, ohne alles noch einmal einzustellen.
"""

import copy

from .blendimporteinstellungen import Blendimporteinstellungen

__all__ = ['Fremdimporteinstellungen', 'Objimporteinstellungen', 'Fbximporteinstellungen']


def _ableiten(endung, hinweis, ohne=(), aenderungen=None):
    """Der Katalog der .blend mit eigenem Pfad-Feld, ohne die Fragen aus `ohne`, Felder nach `aenderungen` {schlüssel: {feld: wert}}."""
    katalog = []
    for eintrag in copy.deepcopy(Blendimporteinstellungen.KATALOG):
        if eintrag['schluessel'] in ohne:
            continue
        if eintrag['schluessel'] == 'pfad':
            eintrag.update(titel='Ordner oder %s' % endung, platzhalter='A:\\…\\Ordner oder Datei%s' % endung, hinweis=hinweis)
        eintrag.update((aenderungen or {}).get(eintrag['schluessel'], {}))
        katalog.append(eintrag)
    return katalog


class Fremdimporteinstellungen(Blendimporteinstellungen):
    """Basis für OBJ und FBX; die Unterklassen setzen `FORMAT`, `DATEI` und `KATALOG`."""

    #: Was das erste Mal NICHT von der .blend kommt: Pfad und Name (der „Eigene Name" der letzten .blend — im Dialog stand für „cute girl" die
    #: Figur „seori", gesehen 10.10.2026) und alles, was das Format anders vorgibt (FBX: die Haltung).
    EIGEN = ('pfad', 'name', 'eigener_name')

    @classmethod
    def laden(cls):
        """Die gemerkten Werte dieses Formats; ohne Datei die der .blend (ohne `EIGEN`)."""
        if not cls.pfad().exists():
            return cls.pruefen({k: v for k, v in Blendimporteinstellungen.laden().items() if k not in cls.EIGEN})
        return super().laden()

    @classmethod
    def fuer(cls, format):
        return {'obj': Objimporteinstellungen, 'fbx': Fbximporteinstellungen}[format]


class Objimporteinstellungen(Fremdimporteinstellungen):
    FORMAT = 'obj'
    DATEI = 'einstellungen_obj.json'
    #: Eine OBJ kennt kein Skelett: Haltung per Rig gibt es nicht.
    KATALOG = _ableiten(
        '.obj',
        'Ein Ordner: die .obj mit der höchsten Fassungsnummer im Namen. Die .mtl und die Texturen liegen neben der Datei '
        '(Farbe, Rauheit, Deckkraft stehen in der .mtl; Normalenkarten nur, wenn sie dort als map_Bump stehen). Eine OBJ hat '
        'kein Skelett — „Mesh to 3D" schätzt die Haltung.',
        ohne=('umposen',))


class Fbximporteinstellungen(Fremdimporteinstellungen):
    FORMAT = 'fbx'
    DATEI = 'einstellungen_fbx.json'
    EIGEN = Fremdimporteinstellungen.EIGEN + ('umposen',)
    KATALOG = _ableiten(
        '.fbx',
        'Ein Ordner: die .fbx mit der höchsten Fassungsnummer im Namen. Skelett und Hautgewichte kommen aus der Datei; die '
        'Texturen werden neben der Datei und einen Ordner darüber gesucht (Unity-Muster: FBX in „Character", Bilder in „Textures").',
        aenderungen={'umposen': {
            'vorgabe': 'aus',
            'hinweis': 'Die Knochenkarte gilt nur für Auto-Rig Pro (FBX-Export eines ARP-Rigs). Jedes andere Rig (Mixamo, Character '
                       'Creator, Unity) bleibt, wie es ist: die Haltung der Datei gilt, „Mesh to 3D" schätzt sie.'}})
