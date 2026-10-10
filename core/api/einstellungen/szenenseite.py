# -*- coding: utf-8 -*-
"""Einstellungen der Szenenseite (Vorgaben, Auswahl-Deckkraft, MakeHuman)."""

import json

from ...dienste.blendimportbackenwahl import Blendimportbackenwahl
from .basis import Einstellungsseite
from .formularwert import Formularwert as F


class SzeneEinstellungen(Einstellungsseite):
    VORLAGE = 'settings_scene.html'
    ROUTE = 'settings_scene'

    #: Wie viele MakeHuman-Vorgabeteile die Seite anbietet.
    MH_PLAETZE = 4

    #: Diese Werte liegen in `ui_prefs` statt in einer eigenen Spalte. Sie
    #: werden nur GESETZT, wenn das Formular etwas schickt — ein leeres Feld
    #: soll die vorhandene Vorgabe nicht löschen.
    #:
    #: OHNE STANDARD-MODELL seit dem 30.09.2026 (Edgar: „entferne das Standardmodell
    #: und die Standard Animation. Auf der Seite /Charakter/ soll immer nur der letzte
    #: geladene Modell und die letzte Animation geladen werden"). Die Szene merkt sich
    #: beides selbst (`viewer/charakter/letztewahl.js`); die Felder `default_model_scene`,
    #: `…_quelle`, `…_bereich` und `default_anim_scene` bleiben in der Datenbank stehen
    #: — eine Migration, die Spalten wirft, nimmt anderen Seiten ihre Vorgaben
    #: (`settings_model`, `settings_result`, Theatre und Effekte haben eigene).
    VORLIEBEN = ('default_pose', 'kleider_bone_model')

    def uebernehmen(self, s, post):
        s.show_rig_scene = F.schalter(post, 'show_rig_scene')
        s.expanded_panels_scene = json.dumps(F.aufgeklappt(post, 'panel_scene_'))
        s.selection_opacity = F.zahl(post, 'selection_opacity', 0.3, mini=0.0, maxi=1.0)
        s.ui_prefs = self._vorlieben(s.ui_prefs or {}, post)

    def _vorlieben(self, prefs, post):
        for name in self.VORLIEBEN:
            wert = F.text(post, name)
            if wert:
                prefs[name] = wert
        for i in range(1, self.MH_PLAETZE + 1):
            name = 'mh_default_%d' % i
            prefs[name] = F.text(post, name)
        prefs['mh_tpose_displacement'] = '1' if post.get('mh_tpose_displacement') else '0'
        # Vorgabe AN: Wer nichts einstellt, bekommt die schnelle Seite
        # (`core/dienste/modulbuendel.py`). Ausgeschaltet liegt jedes der
        # 230 Module wieder einzeln im Browser — das braucht man beim
        # Suchen eines JavaScript-Fehlers.
        prefs['module_buendeln'] = '1' if post.get('module_buendeln') else '0'
        # Vorgabe AUS: Die Normalen der Gelenkkorrekturen rechnet dann der Hauptfaden wie bisher;
        # an rechnet sie ein Worker (`viewer/gemeinsam/normalenarbeit.js`), die Animation ruckelt weniger.
        prefs['normalen_worker'] = '1' if post.get('normalen_worker') else '0'
        # Womit der Blender-Import die Haut bäckt (`Blendimportbackenwahl`): nur ein bekannter Wert wird gespeichert, sonst bleibt die alte Wahl.
        wahl = F.text(post, Blendimportbackenwahl.SCHLUESSEL)
        if wahl in Blendimportbackenwahl.WAHLEN:
            prefs[Blendimportbackenwahl.SCHLUESSEL] = wahl
        return prefs

    def kontext(self, s):
        prefs = s.ui_prefs or {}
        return {
            'selection_opacity_pct': int(round(s.selection_opacity * 100)),
            'module_buendeln': str(prefs.get('module_buendeln', '1')) != '0',
            'normalen_worker': str(prefs.get('normalen_worker', '0')) == '1',
            'backen': Blendimportbackenwahl.aus(prefs),
            'backen_wahlen': list(Blendimportbackenwahl.WAHLEN.items()),
        }
