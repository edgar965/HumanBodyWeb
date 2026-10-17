# -*- coding: utf-8 -*-
"""Architekturmesh3dairegler — die Genesis-9-Regler neben dem Netz auf Hilfe → Architektur → Mesh3DAI (16.10.2026).

Edgar: „… dann rechts die Genesis regler" und vorher „Ich habe ja ganz viele Custom Regler bei genesis 9 für gesicht usw, hast du die alle berücksichtigt?".
Gelesen beim Aufruf: der Reglerkatalog des Bedienfelds (`G9reglerplan.bereiche()` — dieselbe Liste wie `/api/character/genesis9-figur/regler/`, am 16.10.2026 1.138 Regler) und die
Regler von Ursula1 (`HumanBody/data/models/Ursula1.json`, `figur.regler`). Von Hand steht nur `PLAN`: welcher Bereich zu welcher Art Kopf gehört, mit Grund (Tooltip).
Seit 16.10.2026 abends sagt der Formkopf alle Form-Regler voraus (`formkopf` je Bereich aus der Formregler-Liste des Bezugslaufs); fehlt ein Form-Regler des Katalogs, steht es auf der Seite.
"""

import json
from pathlib import Path

__all__ = ['Architekturmesh3dairegler']


class Architekturmesh3dairegler:
    #: Bereich → (Kopf im Plan, Grund). Kopf None = keine Ausgabe des Netzes. Regler der Art „pose" ausserhalb der Mimik deckt der Kopf „Haltung" über Knochendrehungen ab.
    PLAN = {
        'figur': ('Körperform', 'Charakter-Mischregler (Amala, Base Feminine …) — wirken auf Körper UND Kopf; im Plan bei der Körperform.'),
        'koerper': ('Körperform', 'Body Shapes: Größe, Masse, Muskeln, Proportionen.'),
        'kopf': ('Gesicht', 'Daz-Kopfregler (Augen, Nase, Mund, Kiefer, Schädel).'),
        'mimik': ('Mimik', 'Ausdruck (Pose Controls Head). Im Datensatz heute NIE verändert — erst mit Ausdrücken im Datensatz sinnvoll.'),
        'hals': ('Körperform', ''), 'brust': ('Körperform', ''), 'ruecken': ('Körperform', ''), 'taille': ('Körperform', ''), 'huefte': ('Körperform', ''),
        'arme': ('Körperform', ''), 'haende': ('Körperform', ''), 'beine': ('Körperform', ''), 'fuesse': ('Körperform', ''),
        'hb_koerper': ('Körperform', 'HumanBody-Morphs, auf Genesis übertragen.'),
        'hb_gesicht': ('Gesicht', 'HumanBody-Morphs des Gesichts, auf Genesis übertragen.'),
        'hb_fantasie': (None, 'Fantasieformen (Elfenohren …) — erst, wenn der Datensatz sie enthält.'),
        'kopf_eigen': (None, 'Eigenform eines Kopfnetzes — gehört zu EINEM Modell, nicht zu Genesis.'),
        'ort': (None, 'Nachformung eines Imports — gehört zu einem Modell.'),
        'region': (None, 'Regionen-Regler des Projekts; in „Mesh to 3D“ ohne messbaren Gewinn (Option `regionen`, Vorgabe aus).'),
        'modell_eigen': (None, 'Eigenform eines importierten Modells — gehört zu einem Modell.'),
        # 17.10.2026: die Regler der anderen Sitzung (`genesis9-alter.md`, `genesis9-reglerabdeckung.md`), im Formkopf seit Formregler-Fassung 2.
        'alter': ('Körperform', 'Sammelregler „Alter“ (`G9alter`): stellt Daz- und HB-Regler zugleich; in den Formvarianten ab Form041 gewürfelt.'),
        'zaehne': ('Gesicht', 'Zähne (Mund-Anhang, `G9anhangregler`): im Formkopf, aber die Außenfläche des Datensatzes zeigt keine Zähne — gemessen 0 mm an den Körperpunkten, nie gewürfelt.'),
        'augen_eigen': ('Gesicht', 'Iris und Pupille (Augen-Anhang): im Formkopf, aber der Datensatz hat keine Augäpfel — gemessen 0 mm an den Körperpunkten, nie gewürfelt.'),
        'verborgen_200_plus': ('Gesicht', 'Verborgene 200+-Formhelfer (Daz zeigt sie nicht): im Formkopf, in den Formvarianten ab Form041 gewürfelt.'),
        'verborgen_clones': ('Körperform', 'Klone Genesis 1–8 (verborgen): ganze Körperformen, im Formkopf, ab Form041 gewürfelt.'),
    }
    #: Die übrigen verborgenen Abschnitte (`G9verborgeneregler`): Gelenkkorrekturen, Mimik/FACS, Posensteuerungen, Muskelspiel — sie folgen Haltung oder Ausdruck, keine Form.
    VERBORGEN = (None, 'Verborgen (Daz-intern): Gelenkkorrekturen, Mimik/FACS, Posensteuerungen — folgen der Haltung oder dem Ausdruck, nicht im Formkopf.')
    MODELL = Path('Ursula1.json')
    JOBS = ('Ursula1', 'Damira0', 'Mann1', 'Matt0')

    @classmethod
    def jobs(cls, stammdaten=()):
        """Die vier Trainingsjobs: gestellte Regler, Kleidung, Geschlecht (`stammdaten` = `Mesh3daiattrappe.stammdaten()`) — gelesen aus `HumanBody/data/models/<Name>.json`."""
        from django.conf import settings
        geschlecht = {s.get('ordner') or s.get('name'): s.get('geschlecht') for s in stammdaten}
        aus = []
        for name in cls.JOBS:
            try:
                figur = json.loads((Path(settings.HUMANBODY_MODELS_DIR) / ('%s.json' % name)).read_text(encoding='utf-8'))['figur']
            except (OSError, ValueError, KeyError):
                continue
            g = geschlecht.get(name) or '—'
            aus.append({'name': name, 'geschlecht': 'männlich' if g == 'maennlich' else g, 'regler': len(figur.get('regler') or {}), 'kleidung': list(figur.get('kleidung') or {})})
        return aus

    @classmethod
    def _bereiche(cls):
        from Genesis9.pfade import G9pfade
        if not G9pfade.vorhanden():
            raise RuntimeError('Die Daz-Bibliothek fehlt auf diesem Rechner — der Reglerkatalog ist nicht lesbar.')
        from Genesis9.reglerplan import G9reglerplan
        return G9reglerplan.bereiche()

    @classmethod
    def _ursula(cls):
        from django.conf import settings
        datei = Path(settings.HUMANBODY_MODELS_DIR) / cls.MODELL
        return json.loads(datei.read_text(encoding='utf-8'))['figur'].get('regler') or {}

    @classmethod
    def kontext(cls, formnamen=None):
        """`formnamen` = die Regler im Formkopf des Bezugslaufs (`Architekturmesh3daiform.regler(lauf)['namen']`, seine Formregler-Liste). Gezählt wird je Bereich nach NAMEN:
        seit 17.10.2026 stehen im Formkopf auch verborgene Formabschnitte (Art `pose` im Bedienfeld), eine Zählung nach Art ginge dort nicht auf."""
        bereiche = cls._bereiche()
        ursula = cls._ursula()
        wo = {r['name']: b['name'] for b in bereiche for r in b['regler']}
        im_kopf = set(formnamen) if formnamen is not None else None
        zeilen = []
        koepfe = {}
        for b in bereiche:
            pose = [r for r in b['regler'] if r.get('art') == 'pose']
            form = len(b['regler']) - len(pose)
            standard = cls.VERBORGEN if b['schluessel'].startswith('verborgen_') else (None, 'nicht eingeplant (neuer Bereich, im Plan nicht bewertet)')
            kopf, grund = cls.PLAN.get(b['schluessel'], standard)
            formkopf = sum(1 for r in b['regler'] if r['name'] in im_kopf) if im_kopf is not None else None
            ins_netz = len(b['regler']) if kopf == 'Mimik' else max(form, formkopf or 0) if kopf else 0
            if kopf:
                koepfe[kopf] = koepfe.get(kopf, 0) + ins_netz
            zeilen.append({'name': b['name'], 'zahl': len(b['regler']), 'form': form, 'pose': len(pose), 'kopf': kopf or '—', 'ins_netz': ins_netz, 'im_formkopf': formkopf,
                           'grund': grund or ('Form-Regler; die %d Posen-Regler deckt der Kopf „Haltung“ über Knochen ab.' % len(pose) if pose else 'Form-Regler.'),
                           'ursula': sum(1 for n in ursula if wo.get(n) == b['name'])})
        ursula_liste = [{'name': n, 'wert': w, 'bereich': wo.get(n, 'nicht im Bedienfeld')} for n, w in sorted(ursula.items())]
        im_formkopf = sum(z['im_formkopf'] or 0 for z in zeilen) if im_kopf is not None else None
        # Jeder Form-Regler des heutigen Katalogs muss im Formkopf stehen — sonst misst die Liste des Laufs einen älteren Katalog (17.10.2026: 74 neue Regler der anderen Sitzung).
        fehlen = sorted(r['name'] for b in bereiche for r in b['regler'] if r.get('art') != 'pose' and r['name'] not in im_kopf) if im_kopf is not None else []
        return {'zeilen': zeilen, 'gesamt': sum(z['zahl'] for z in zeilen), 'form': sum(z['form'] for z in zeilen), 'pose': sum(z['pose'] for z in zeilen),
                'koepfe': koepfe, 'ursula': ursula_liste, 'ursula_zahl': len(ursula_liste), 'im_formkopf': im_formkopf, 'fehlen': fehlen,
                'abweichung': None if not fehlen else 'Der Formkopf des Bezugslaufs kennt %d Form-Regler des heutigen Katalogs nicht (z. B. %s) — neu messen und trainieren '
                                                      '(ProjektTemp/_wegwerf/mesh3dai_formregler.py, mesh3dai_form_alle.py).' % (len(fehlen), ', '.join(fehlen[:3]))}
