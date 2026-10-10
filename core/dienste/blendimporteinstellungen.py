# -*- coding: utf-8 -*-
"""Blendimporteinstellungen — was der Dialog „Modell importieren" für eine .blend fragt, mit Edgars Vorgaben.

Edgar (08.10.2026), die Entscheidungen zum Import von „cute girl", die beim nächsten Mal als Vorgabe dastehen sollen:

    datei       „die letzte blender Datei (mit der aktuellsten Version)" → aus dem Ordner die .blend mit der höchsten
                Fassungsnummer im Namen (`Blendimportquelle`)
    name        „name wie der Ordner"; später dazu „eine neue Option, wo man den Namen in der Textbox setzen kann"
                → `ordner` | `datei` | `eigen` (dann gilt `eigener_name`)
    augen       „Die Originalaugen auf Genesis übertragen, aber einstellbar / ersetzbar" → `original` | `genesis`
    textur      „geringe Auflösung im Browser, mit Strg+Alt+H umschaltbar auf die höchste" → gebacken mit
                `kachel_px` je Kachel; der Browser bekommt `browser_px`, Strg+Alt+H die volle Kachel.
                Später, am selben Tag: „default für Import: Höchste Auflösung" → beide Vorgaben 8192 (keine
                verkleinerte Kopie; kleinere Browser-Stufen bleiben wählbar)

Gemerkt werden die zuletzt benutzten Werte (samt Pfad) in `<OBJECTS_ROOT>/blendimport/einstellungen.json`; jeder Wert
wird gegen den Katalog geprüft, Unbekanntes fällt auf die Vorgabe (wie `Meshfiguroptionen.pruefen`).
"""

import json
import logging
import os

from ..daten.blendimportablage import Blendimportablage

logger = logging.getLogger('core')

__all__ = ['Blendimporteinstellungen']


class Blendimporteinstellungen:
    #: OBJ und FBX (`Fremdimporteinstellungen`) erben die Methoden und ersetzen nur diese drei.
    FORMAT = 'blend'
    DATEI = 'einstellungen.json'

    KATALOG = [
        {'schluessel': 'pfad', 'titel': 'Ordner oder .blend', 'art': 'text', 'vorgabe': '',
         'hinweis': 'Ein Ordner: die .blend mit der höchsten Fassungsnummer im Namen. Die Texturen dürfen neben der '
                    'Datei liegen (nicht gepackt) — deshalb ein Pfad und kein Hochladen.'},
        {'schluessel': 'name', 'titel': 'Name', 'art': 'wahl', 'vorgabe': 'ordner',
         'werte': [('ordner', 'Wie der Ordner'), ('datei', 'Wie die Datei (ohne Fassung)'),
                   ('eigen', 'Eigener Name (Textfeld darunter)')]},
        {'schluessel': 'eigener_name', 'titel': 'Eigener Name', 'art': 'text', 'vorgabe': '', 'platzhalter': 'z. B. Mila',
         'nur_wenn': {'name': 'eigen'},
         'hinweis': 'Gilt nur bei „Eigener Name". Buchstaben, Ziffern, Leerzeichen und Bindestrich; bis zu 60 Zeichen. '
                    'Ein Modell mit demselben Namen wird beim Import ersetzt.'},
        {'schluessel': 'umposen', 'titel': 'Haltung', 'art': 'wahl', 'vorgabe': 'rig',
         'werte': [('rig', 'Mit dem Rig in die Genesis-Haltung bringen (Knochenkarte)'),
                   ('aus', 'Haltung der Datei lassen')],
         'hinweis': 'Körper, Kleider und Haar stehen dann wie Genesis in A-Haltung; „Mesh to 3D" muss die Haltung nicht '
                    'mehr schätzen. Nur für Auto-Rig Pro; ein anderes Rig wird übersprungen. Eine .blend ganz ohne Skelett '
                    'bleibt in ihrer Haltung — „Mesh to 3D" schätzt sie.'},
        {'schluessel': 'augen', 'titel': 'Augen', 'art': 'wahl', 'vorgabe': 'objekt',
         'werte': [('objekt', 'Originalaugen als eigenes Objekt (Genesis-Augen ausgeblendet)'),
                   ('original', 'Originaliris auf die Genesis-Augen übertragen'),
                   ('genesis', 'Genesis-Augen (Irisfarbe aus dem Modell)')],
         'hinweis': 'Eigenes Objekt: die Augäpfel der .blend (eigene Form, Hornhaut, Glanz) kommen als Stück „<Name> Augen" '
                    'unter Zubehör, solange es getragen wird, weichen die Genesis-Augen; zieht man es aus, gilt die '
                    'Originaliris auf den Genesis-Augen. Das Augenbild liegt als eigene Datei beim Modell.'},
        {'schluessel': 'scham', 'titel': 'Scham', 'art': 'wahl', 'vorgabe': 'objekt',
         'werte': [('objekt', 'Fläche und Haut des Originals als eigenes Stück (Zubehör)'),
                   ('mann', 'Männliche Anatomie (Penis, Hoden) als eigenes Stück — ohne Scham-Regler'),
                   ('figur', 'Nur die Genesis-Fläche (weiche Mulde)')],
         'hinweis': 'Die Genesis-Figur trägt die inneren Schamlippen nicht: ihr Käfig hat dort ~8 mm Punktabstand, die Furche '
                    'wird überbrückt, und das Backen trifft verschmiert. Eigenes Stück: der Teil des Körpers, der von der Figur '
                    'abweicht, kommt als „<Name> Scham" unter Zubehör — mit der Fläche und der Haut (Farbe, Normalen, Rauheit) '
                    'des Originals; die Genesis-Haut darunter entfällt, solange es getragen wird. Ausziehen zeigt wieder die '
                    'Genesis-Fläche. „Männliche Anatomie" baut dasselbe Stück („<Name> Genitalien"), trägt aber nicht die '
                    'weiblichen Scham-Regler (Hügel, Lippen, Haube, Eingang, Damm) — Regler für Länge, Umfang und Hoden gibt es '
                    'noch nicht.'},
        {'schluessel': 'kachel_px', 'titel': 'Haut: gespeicherte Auflösung', 'art': 'wahl', 'vorgabe': '8192',
         'werte': [('2048', '2048 px (klein)'), ('4096', '4096 px (mittel)'), ('8192', '8192 px (volle Auflösung)')],
         'hinweis': 'In dieser Größe wird jede der vier Haut-Kacheln (Kopf, Rumpf, Beine, Arme) aus dem Original '
                    'gebacken und gespeichert. 8192 px sind so groß wie das Original — dann geht nichts verloren. '
                    'Zu sehen ist sie, wenn du in der Szene Strg+Alt+H drückst. Die Nägel bleiben Genesis, damit der '
                    'Nagellack wirkt.'},
        {'schluessel': 'browser_px', 'titel': 'Haut: Anzeige im Browser', 'art': 'wahl', 'vorgabe': '8192',
         'werte': [('1024', '1024 px (sehr schnell)'), ('2048', '2048 px (schnell)'), ('4096', '4096 px (schärfer)'),
                   ('8192', '8192 px (höchste — keine Verkleinerung)')],
         'hinweis': 'Was der Browser normal lädt. Kleinere Werte sind eine verkleinerte KOPIE: lädt schneller und braucht '
                    'weniger Grafikspeicher; die volle Größe oben bleibt gespeichert und kommt mit Strg+Alt+H. Bei der '
                    'höchsten Stufe gibt es keine Kopie — der Browser lädt immer die volle Größe (am schärfsten, aber '
                    'langsam: gemessen 92 MB je Normalenkarte). Größer als gespeichert wird es nie.'},
        {'schluessel': 'normalen_grenze', 'titel': 'Normalen säubern ab', 'art': 'wahl', 'vorgabe': '50',
         'werte': [('35', '35° (streng)'), ('50', '50° (Vorgabe)'), ('70', '70° (nur grobe Fehltreffer)'),
                   ('aus', 'Nicht säubern')],
         'hinweis': 'Gebackene Normalen, die stärker von der Figur abweichen, gelten als falscher Strahltreffer (so '
                    'entstand ein weißer Fleck im Dekolleté) und werden flach. An cute girl gemessen bei 50°: 0,8–2,8 % '
                    'der Texel je Kachel; ab 8 % warnt der Import.'},
        {'schluessel': 'normalen_form', 'titel': 'Normalen: Form', 'art': 'wahl', 'vorgabe': 'weg',
         'werte': [('weg', 'Nur Feindetail (die Form kommt aus der Figur)'), ('bleibt', 'Ganze Karte übernehmen')],
         'hinweis': 'Wo die Figur vom Original abweicht (Scham, Brustwarzen, Lippen), kippt die gebackene Karte die Normalen '
                    'großflächig — im Licht stünde eine Form, die die Fläche nicht hat. „Nur Feindetail" lässt Poren und '
                    'Haarstoppeln, nimmt das Großflächige weg.'},
        {'schluessel': 'basis', 'titel': 'Grundfigur', 'art': 'wahl', 'vorgabe': 'feminine',
         'werte': [('feminine', 'Genesis 9 Feminine'), ('masculine', 'Genesis 9 Masculine'),
                   ('neutral', 'Genesis 9 (neutral)')]},
        {'schluessel': 'stuecke', 'titel': 'Kleider und Haar', 'art': 'wahl', 'vorgabe': 'an',
         'werte': [('an', 'Als eigene Stücke in die Genesis-Bibliothek'), ('aus', 'Nur die Figur')]},
        {'schluessel': 'koerper_ergaenzen', 'titel': 'Körper unter Kleidung ergänzen', 'art': 'haken', 'vorgabe': 'an',
         'werte': [('an', 'Ja'), ('aus', 'Nein')],
         'hinweis': 'Reicht der Körper nicht bis zu den Füßen (Rosemary Winters: Strumpf-Netz über den Beinen), nimmt „Mesh to 3D" die '
                    'Form des Kleidungsstücks darunter (3 mm nach innen) als Körper. Die Haut kommt aus der Genesis-9-Standardhaut, '
                    'nie aus dem Stoff; die Haut der .blend bleibt unverändert.'},
        {'schluessel': 'unvollstaendig', 'titel': 'Unvollständiger Körper', 'art': 'wahl', 'vorgabe': 'anhalten',
         'werte': [('anhalten', 'Import nach dem Lesen anhalten und melden'), ('weiter', 'Trotzdem importieren')],
         'hinweis': 'Reicht das Körper-Netz nur über weniger als 70 % der Figurhöhe (Rosemary Winters: Kopf bis Mitte Oberschenkel, 48 %; '
                    'sonst 93–100 %), hält der Import nach 5 Sekunden an und sagt, was fehlt — „Mesh to 3D" passt eine ganze Figur an, '
                    'und ein Torso ergäbe nach Stunden eine Figur, die nicht zum Körper passt. „Trotzdem importieren" nur für eine '
                    'Büste oder einen Teilkörper, den du so willst.'},
    ]

    @classmethod
    def pfad(cls):
        return Blendimportablage.wurzel() / cls.DATEI

    @classmethod
    def eintrag(cls, schluessel):
        for e in cls.KATALOG:
            if e['schluessel'] == schluessel:
                return e
        raise KeyError(schluessel)

    @classmethod
    def pruefen(cls, roh):
        roh = roh if isinstance(roh, dict) else {}
        aus = {}
        for e in cls.KATALOG:
            wert = roh.get(e['schluessel'], e['vorgabe'])
            if e['art'] == 'text':
                wert = str(wert or '').strip().strip('"').strip("'").strip()[:1000]
            elif str(wert) not in [w for w, _ in e['werte']]:
                wert = e['vorgabe']
            aus[e['schluessel']] = str(wert)
        return aus

    @classmethod
    def laden(cls):
        """Die gemerkten Werte (geprüft) — ohne Datei die Vorgaben."""
        try:
            roh = json.loads(cls.pfad().read_text(encoding='utf-8'))
        except FileNotFoundError:
            roh = {}
        except (OSError, ValueError):
            logger.warning('Blender-Import: %s nicht lesbar — Vorgaben', cls.pfad(), exc_info=True)
            roh = {}
        return cls.pruefen(roh)

    @classmethod
    def speichern(cls, werte):
        """Geprüft ablegen und zurückgeben (bei jedem Start eines Imports)."""
        werte = cls.pruefen({**cls.laden(), **(werte if isinstance(werte, dict) else {})})
        cls.pfad().parent.mkdir(parents=True, exist_ok=True)
        neben = cls.pfad().with_suffix('.json.neu')
        neben.write_text(json.dumps(werte, ensure_ascii=False, indent=1), encoding='utf-8')
        os.replace(neben, cls.pfad())
        return werte

    @classmethod
    def katalog(cls):
        """`{optionen: [...], werte: {...}}` für den Dialog — Werte der Auswahl als `{wert, text}`."""
        optionen = []
        for e in cls.KATALOG:
            feld = {k: v for k, v in e.items() if k != 'werte'}
            if e['art'] in ('wahl', 'haken'):
                feld['werte'] = [{'wert': w, 'text': t} for w, t in e['werte']]
            optionen.append(feld)
        return {'format': cls.FORMAT, 'optionen': optionen, 'werte': cls.laden()}
