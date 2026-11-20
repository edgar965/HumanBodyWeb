# -*- coding: utf-8 -*-
"""Exportleistekettenlauf — Stoff und Haar der Kleiderbibliothek für die BVH des Renders nachrechnen, wo die Kette noch keine Ablage hat (20.11.2026, Edgar „ja, Weg 2“: der Render nimmt
die Ergebnisse der Kette; bewegt er sich anders, rechnet er mit demselben Code).

Dieselben Kettenschritte wie im Job (`meshgenesis_kleiderstoff_lauf.py`, `meshgenesis_kleiderhaar_lauf.py`, mit `--bvh` und `--stueck`) über den Skriptdienst von python14 bzw. einen eigenen
Prozess (`Meshgenesisrechenschritt`, gleiche Umgebung wie der Rechenlauf: reproduzierbar). Die Ablage liegt danach beim Stück wie jede andere — auch die Seite spielt sie ab, wenn dort
diese BVH gewählt ist. Ausgabe nach `arbeit/render/kette.log`. Gerechnet wird vor der Gpusperre des Renders (die Läufe holen sie selbst).

    stellung = Exportleistekettenlauf.rechnen(stellung, bvh_pfad, log_datei)    # danach `Exportleistekette.aufloesen` erneut
    stellung = Exportleistekettenlauf.vorbereiten(render, optionen, regler_json, stellung, bvh_pfad, glb)      # alles vor dem Render (`exportleiste_render`)

Regler des Renders (20.11.2026, Edgar: „die sollen wirken, wenn der Render eingestellt ist“): weicht ein Wind-, Stoff- oder Haar-Regler von der Vorgabe ab, rechnet der Lauf mit
`--regler <regler.json>` (`Kettenregler`) in eine eigene Ablage mit Zeichen; die Seite sieht sie nicht.
"""

import json
import logging
import os
import sys
import time
from collections import defaultdict

from django.conf import settings

from .exportleistekette import Exportleistekette
from .meshgenesisrechenschritt import Meshgenesisrechenschritt

logger = logging.getLogger('core')

__all__ = ['Exportleistekettenlauf']


class Exportleistekettenlauf:
    SKRIPTE = {'stoff': 'meshgenesis_kleiderstoff_lauf.py', 'haar': 'meshgenesis_kleiderhaar_lauf.py'}

    class _Messung:
        """Was `Meshgenesisrechenschritt` von einer Messung braucht — hier zählt nur das Log."""
        prozess_holen = None

        def zeile(self, _text):
            pass

        def dienst(self, _stand):
            pass

    @staticmethod
    def kettenregler(regler_json):
        """`Kettenregler` der Regler-Datei des Renders (`meshgenesis/meshgenesis_kettenregler.py`)."""
        kette = os.path.join(str(settings.TOOLS_ROOT), 'meshgenesis')
        if kette not in sys.path:
            sys.path.append(kette)
        from meshgenesis_kettenregler import Kettenregler
        return Kettenregler.laden(regler_json)

    @classmethod
    def vorbereiten(cls, render, optionen, regler_json, stellung, bvh_pfad, glb):
        """Vor dem Render: fehlt Ablage für diese BVH und diese Regler, rechnen; dann auflösen und `<glb>.stellung.json` schreiben (liest `Figurfilm.Kettenfilm`). Mit
        `kettenfilm.an` aus (auch „ohne Physik“) nichts. → Stellung."""
        if (optionen.get('renderphysik') or {}).get('kettenfilm.an', 'an') in ('aus', False):
            return stellung
        regler = cls.kettenregler(regler_json)
        if Exportleistekette.fehlend(stellung, bvh_pfad, regler):
            mit = ' und die Regler' if any(regler.zeichen(s) for s in cls.SKRIPTE) else ''
            render.melden(schritt='Stoff und Haar der Kleiderbibliothek für diese Bewegung%s (Kette, GPU)' % mit, fortschritt=0.05)
            cls.rechnen(stellung, bvh_pfad, render._datei('kette.log'), regler_json, regler)
        stellung = Exportleistekette.aufloesen(stellung, bvh_pfad, regler)
        glb.with_suffix('.stellung.json').write_text(json.dumps(stellung, ensure_ascii=False), encoding='utf-8')
        return stellung

    @classmethod
    def rechnen(cls, stellung, bvh_pfad, log_datei, regler_json=None, regler=None):
        """Die fehlenden Ablagen rechnen (je Test, Geschlecht und Schritt ein Lauf mit allen Stücken) und die Stellung neu auflösen. → neue Stellung."""
        gruppen = defaultdict(list)
        for kennung, g, schritt, stueck in Exportleistekette.fehlend(stellung, bvh_pfad, regler):
            gruppen[(kennung, g, schritt)].append(stueck)
        env = dict(os.environ, PYTHONIOENCODING='utf-8', MESHGENESIS_DETERMINISTISCH='1', CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONHASHSEED='0')
        kette = os.path.join(str(settings.TOOLS_ROOT), 'meshgenesis')
        with open(log_datei, 'a', encoding='utf-8') as aus:
            for (kennung, g, schritt), stuecke in gruppen.items():
                befehl = [sys.executable, '-u', cls.SKRIPTE[schritt], '--nur', kennung, '--geschlecht', g, '--bvh', str(bvh_pfad)]
                if regler is not None and regler.zeichen(schritt):
                    befehl += ['--regler', str(regler_json)]
                for s in stuecke:
                    befehl += ['--stueck', s]
                t = time.time()
                aus.write('\n=== %s: %s\n' % (time.strftime('%H:%M:%S'), ' '.join(befehl[2:])))
                _zeilen, code = Meshgenesisrechenschritt.rechnen(befehl, aus, cls._Messung(), kette, env, 'Exportleiste Kette %s %s' % (kennung, schritt))
                logger.info('Exportleistekettenlauf %s (%s) %s %s: Rückgabe %s, %.0f s', kennung, g, schritt, stuecke, code, time.time() - t)
        return Exportleistekette.aufloesen(stellung, bvh_pfad, regler)
