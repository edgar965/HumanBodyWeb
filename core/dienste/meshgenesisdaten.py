# -*- coding: utf-8 -*-
"""Meshgenesisdaten — die ECHTEN Daten eines Jobs von Mesh-Genesis für die Jobseite: Datensatz auf der Platte und die Vorhersagen des jüngsten fertigen Trainingslaufs (15.10.2026).

Edgar zur Jobseite nach dem ersten Lauf: „das ist doch noch nichts?" — sie zeigte weiter die Attrappe. Diese Klasse liefert dieselbe Form wie `Meshgenesisattrappe` (`jobs`, `proben`, `animation`), die Seite zeigt sie mit
demselben Code; `attrappe: False` sagt ihr, dass es echt ist. Gibt es keinen fertigen Lauf, liefert jede Methode `None` und die Endpunkte fallen auf die Attrappe zurück.

    Meshgenesisdaten.lauf(modell)        -> Ordner des jüngsten Laufs mit `lauf_ergebnis.json` UND `vorhersagen.npz`, sonst None
    Meshgenesisdaten.jobs()              -> wie `Meshgenesisattrappe.jobs()`, für Jobs mit Lauf die echten Zahlen
    Meshgenesisdaten.proben(job)         -> {job, attrappe: False, hinweis, lauf, gelenke: [], rig, teile: {}, proben: [...], zusammenfassung} | None
    Meshgenesisdaten.eingabe(job, nr)    -> {nr, punkte: [[x, y, z]…], farbe: [[r, g, b]…], etikett: [Teil…]} — 4.096 von 16.384 Punkten der Außenfläche (fest je Probe) | None
    Meshgenesisdaten.animation(job)      -> die Bilder der Bewegung (Spagat) aus den Proben, nach Bild geordnet | None

ECHT ist: die Posen (Retarget BVH → Genesis 9 auf Ursula1), das Rig mit 138 Knochen als Soll (`proben/NNNN/soll.npz`), die Außenfläche als Punktwolke mit den Teilfarben (`eingabe.npz`) und die Rig-Punkte, die das Netz
vorhersagt (`vorhersagen.npz` des Laufs). Die Flächen der gehäuteten Figur (für die Ansichtsarten) holt die Seite je Probe (`Meshgenesisflaeche`); die Zeilen unter dem ganzen Körper sind Ausschnitte desselben Rigs
und derselben Figur (`Meshgenesisdatenteile`). Das Netz sagt NUR die Rig-Punkte voraus — eine Fläche als Ausgabe des Netzes gibt es nicht.
Jede Probe ist einzeln ausgerichtet (Blick +Z, Hüfte in der Mitte, Füße auf dem Boden — wie im Datensatz); die Bilder der Bewegung also auch (anders als die Attrappe, die die Bewegung gemeinsam ausrichtet).
Zwischengespeichert je Lauf und Stand von `proben.json` (die Seite fragt `proben` und `animation` getrennt).
"""

import json
import logging
from pathlib import Path

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch
from KoerperKI_alle.zufallsstrom import Zufallsstrom

from .meshgenesisapose import Meshgenesisapose
from .meshgenesisaposewahl import Meshgenesisaposewahl
from .meshgenesisattrappe import Meshgenesisattrappe
from .meshgenesisautorig import Meshgenesisautorig
from .meshgenesisbild import Meshgenesisbild
from .meshgenesisdatensatz import Meshgenesisdatensatz
from .meshgenesisdatenteile import Meshgenesisdatenteile
from .meshgenesisrig import Meshgenesisrig
from .meshgenesisvergleich import Meshgenesisvergleich
from .meshgenesiswege import Meshgenesiswege

logger = logging.getLogger('core')

__all__ = ['Meshgenesisdaten']


class Meshgenesisdaten:
    GRUPPEN = ('training', 'pruefung', 'spagat')
    EINGABE_ANZEIGE = 4096
    SCHWELLE_MM = 10.0
    #: Die Figur heißt wie der Datensatz des Laufs (`daten` in `lauf_ergebnis.json`; bis 16.10.2026 abends stand hier fest „Ursula1“ — auch auf der Seite von Mann1).
    #: Kurz seit 20.10.2026 abends (Edgar: „ich brauche keine Romane, kurz und bündig“) — bis dahin stand hier ein Absatz über Datensatz, Netz und Anpassung.
    HINWEIS = 'Lauf %(lauf)s · das Netz sagt nur die Rig-Punkte voraus.'
    #: Lauf mit Daz-Winkeln als Ausgabe (16.10.2026, `--ausgabe kanaele`): die Seite häutet das Ergebnis genau wie das Ziel, aus der Ruhelage mit den vorhergesagten Knochendrehungen.
    HINWEIS_KANAELE = 'Lauf %(lauf)s · Figur im Ergebnis von der KI, nicht %(modell)s.'
    #: Lauf mit Stimmen je Punkt (16.10.2026, `meshgenesis_stimmen_netz.py`, `kopf = stimmen` in `lauf_ergebnis.json`): das Netz sagt Punkte voraus, die Winkel kommen aus einer Anpassung danach.
    HINWEIS_STIMMEN = 'Lauf %(lauf)s%(training)s · Figur im Ergebnis von der KI, nicht %(modell)s.'
    #: Tripo-Jobs (18.10.2026 abends, `Meshgenesispaare`; bis 19.10.2026 „Trainingspaar“ genannt — Edgar: „hör auch mit Tripo Paar, das sind ganz einfache Tripo jobs“): Start = Tripo-Netz, Ziel = Genesis-Export,
    #: Ergebnis = was die KI aus dem Tripo-Netz macht (`meshgenesis_paar_lauf.py` schreibt den Lauf). Bis 19.10.2026 spätabends war die Figur im Ergebnis das ZIEL in der vorhergesagten Pose, ihr Rig auf das Ziel
    #: gelegt, die Pose aus Make-It-Animatable — Edgar: „Hast du geschummelt …?“. Seitdem: Figur und Pose nur aus der KI (`Meshgenesisergebnisfigur`), Lage nach fester Regel.
    #: Kleider und Haar im Ergebnis (20.10.2026, `Meshgenesisergebniskleider`, `Meshgenesisprobenkleider`) — bis dahin stand hier „gibt die KI nicht aus“.
    #: 20.10.2026 mittags: Haar nicht mehr als Frisur der Garderobe (Edgar an DamiraAlt: „die sollen doch nicht aus der Bibliothek kommen“) — die Vorgabe nimmt nur k und s (`Meshgenesistestkikleider.AUS_DER_BIBLIOTHEK`).
    KLEIDER_TEXT = 'Kleider und Haar: aus der KI, wo gerechnet.'
    HINWEIS_PAAR = 'Tripo-Job: Start = Tripo-Netz, Ziel = dein Genesis-Export. %(ergebnis)s'
    ERGEBNIS_PAAR = 'Ergebnis nur aus der KI (Formnetz %(lauf)s).'
    OHNE_ERGEBNIS_PAAR = 'Noch kein Ergebnis.'
    #: Unter dem Ergebnis (19.10.2026 spätabends, Edgar: „alle jobs, alle test jobs, alle trainings sollen der WAHRHEIT entsprechen“): was aus der KI kommt — seit 20.10.2026 abends in einer Zeile.
    ERGEBNIS_TEXT = 'Nur aus der KI: Pose, Figur, Kleider und Haar (wo gerechnet). Haut: aus dem Hautkopf, wo gerechnet, sonst Vorgabe des Geschlechts.'
    #: Punkte der Eingabewolke auf der Seite: ein Paar zeigt im Start die Wolke selbst (nicht die Außenfläche des Ziels) — alle 16.384, sonst bleibt die Figur zu dünn.
    EINGABE_ANZEIGE_PAAR = 16384
    _ablage = {}

    @staticmethod
    def lauf(modell):
        ordner = Meshgenesisdatensatz.ordner(modell) / '_laeufe'
        if not ordner.is_dir():
            return None
        fertig = [p for p in sorted(ordner.iterdir()) if Npztorch.da(p / 'lauf_ergebnis.json') and Npztorch.da(p / 'vorhersagen.npz')]
        return fertig[-1] if fertig else None

    @classmethod
    def jobs(cls):
        """Die Jobs wie `Meshgenesisattrappe.jobs()`; wo ein fertiger Lauf liegt, mit den Zahlen des Datensatzes (Prüfposen = alle nie trainierten Proben)."""
        aus = []
        for job in Meshgenesisattrappe.jobs():
            lauf = cls.lauf(job['ordner'])
            plan = cls._plan(job['ordner']) if lauf else None
            if plan:
                training = sum(1 for e in plan.values() if e['gruppe'] == 'training')
                job = dict(job, proben=len(plan), training=training, pruefung=len(plan) - training, status='Echt (Lauf %s)' % lauf.name, hinweis=cls.hinweis(lauf, modell=job.get('modell')))
            elif job.get('paar'):
                plan = cls._plan(job['ordner']) or {}
                training = sum(1 for e in plan.values() if e['gruppe'] == 'training')
                job = dict(job, proben=len(plan), training=training, pruefung=len(plan) - training, status='Tripo-Job: Start und Ziel bereit, noch kein Ergebnis',
                           hinweis=cls.HINWEIS_PAAR % {'ergebnis': cls.OHNE_ERGEBNIS_PAAR})
            aus.append(job)
        return aus

    @classmethod
    def hinweis(cls, lauf, ergebnis=None, modell=None):
        """Der Hinweis über der Jobseite — je nach Ausgabe des Laufs (`ausgabe` in `lauf_ergebnis.json`: freie Punkte oder Daz-Winkel)."""
        if ergebnis is None:
            try:
                ergebnis = json.loads((lauf / 'lauf_ergebnis.json').read_text(encoding='utf-8'))
            except (OSError, ValueError):
                ergebnis = {}
        if ergebnis.get('kopf') == 'paar':
            return cls.HINWEIS_PAAR % {'ergebnis': cls.ERGEBNIS_PAAR % {'lauf': ergebnis.get('formkopf') or lauf.name}}
        alle = ergebnis.get('training_daten') or []
        werte = {'lauf': lauf.name, 'modell': modell or ergebnis.get('daten') or 'Ursula1',
                 'training': ' · trainiert an %s' % ', '.join(alle) if len(alle) > 1 else ''}
        if ergebnis.get('kopf') == 'stimmen':
            return cls.HINWEIS_STIMMEN % werte
        return (cls.HINWEIS_KANAELE if ergebnis.get('ausgabe') == 'kanaele' else cls.HINWEIS) % werte

    @staticmethod
    def _quaternionen(m):
        """(N, 3, 3) Drehmatrizen → (N, 4) Quaternionen (x, y, z, w), wie three.js `Quaternion.setFromRotationMatrix` (Fallunterscheidung nach der Spur)."""
        aus = torch.zeros((len(m), 4), dtype=torch.float64, device='cuda')
        for i, r in enumerate(m):
            spur = r[0, 0] + r[1, 1] + r[2, 2]
            if spur > 0:
                s = 0.5 / Torchfeld.sqrt(spur + 1.0)
                aus[i] = Torchfeld.feld(((r[2, 1] - r[1, 2]) * s, (r[0, 2] - r[2, 0]) * s, (r[1, 0] - r[0, 1]) * s, 0.25 / s))
            elif r[0, 0] > r[1, 1] and r[0, 0] > r[2, 2]:
                s = 2.0 * Torchfeld.sqrt(1.0 + r[0, 0] - r[1, 1] - r[2, 2])
                aus[i] = Torchfeld.feld((0.25 * s, (r[0, 1] + r[1, 0]) / s, (r[0, 2] + r[2, 0]) / s, (r[2, 1] - r[1, 2]) / s))
            elif r[1, 1] > r[2, 2]:
                s = 2.0 * Torchfeld.sqrt(1.0 + r[1, 1] - r[0, 0] - r[2, 2])
                aus[i] = Torchfeld.feld(((r[0, 1] + r[1, 0]) / s, 0.25 * s, (r[1, 2] + r[2, 1]) / s, (r[0, 2] - r[2, 0]) / s))
            else:
                s = 2.0 * Torchfeld.sqrt(1.0 + r[2, 2] - r[0, 0] - r[1, 1])
                aus[i] = Torchfeld.feld(((r[0, 2] + r[2, 0]) / s, (r[1, 2] + r[2, 1]) / s, 0.25 * s, (r[1, 0] - r[0, 1]) / s))
        return aus

    @staticmethod
    def _plan(ordner):
        datei = Meshgenesisdatensatz.ordner(ordner) / 'proben.json'
        if not Npztorch.da(datei):
            return None
        return {e['nr']: e for e in json.loads(datei.read_text(encoding='utf-8'))}

    @classmethod
    def proben(cls, job):
        lauf = cls.lauf(job['ordner'])
        if lauf is None:
            return None
        ordner = Meshgenesisdatensatz.ordner(job['ordner'])
        try:
            stand = (str(lauf), Npztorch.stat(lauf / 'vorhersagen.npz').st_mtime_ns, Npztorch.stat(ordner / 'proben.json').st_mtime_ns, Meshgenesisautorig.stand(ordner), Meshgenesiswege.stand(lauf),
                     str(Meshgenesisapose.datei(lauf)))
            # Je Job gemerkt (seit Ursula_Pose1 gibt es zwei; ein gemeinsamer Platz würde bei jedem Wechsel neu bauen).
            gemerkt = cls._ablage.get(job['id'])
            if gemerkt is None or gemerkt['stand'] != stand:
                cls._ablage[job['id']] = gemerkt = {'stand': stand, 'proben': cls._bauen(job, lauf, ordner)}
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Meshgenesisdaten: Lauf %s nicht lesbar (%s) — die Seite zeigt die Attrappe', lauf, fehler)
            return None
        return gemerkt['proben']

    @classmethod
    def _bauen(cls, job, lauf, ordner):
        plan = cls._plan(job['ordner'])
        beschr = Meshgenesisrig.beschreibung()
        namen = [k['name'] for k in beschr['knochen']]
        gruppen = [k['gruppe'] for k in beschr['knochen']]
        ergebnis = json.loads((lauf / 'lauf_ergebnis.json').read_text(encoding='utf-8'))
        vor = Npztorch.lesen(lauf / 'vorhersagen.npz')
        soll = {int(nr): Torchfeld.astype(Npztorch.lesen(ordner / 'proben' / ('%04d' % int(nr)) / 'soll.npz')['rig'], torch.float64)
                for gruppe in cls.GRUPPEN if gruppe + '_nr' in vor.files for nr in vor[gruppe + '_nr']}
        # Maßstäbe der Tabelle unter dem Ergebnis (16.10.2026): mittlere und nächste Trainingspose, je Zeile.
        vergleich = Meshgenesisvergleich({nr: soll[nr] for nr in vor['training_nr'].tolist()} if 'training_nr' in vor.files else {})
        # Lauf mit Daz-Winkeln: je Probe die Drehung jedes Knochens gegen die Ruhelage (ausgerichtet) und einmal die Ruhezentren — damit häutet die Seite das Ergebnis genau (`Meshgenesisflaechen.ausgabe`).
        haltung = None
        gruppen_da = [g for g in cls.GRUPPEN if g + '_nr' in vor.files]
        if ergebnis.get('ausgabe') == 'kanaele' and all(g + '_dreh' in vor.files for g in gruppen_da) and 'ruhezentren' in vor.files:
            # Tripo-Job (19.10.2026 abends, `meshgenesis_paar_lauf.py`): Drehungen und Ruhezentren der VORHERGESAGTEN Figur (seit 19.10.2026 spätabends) — gezeichnet wird das Ergebnis als Genesis-Figur.
            haltung = {'art': 'kanaele', 'ruhezentren': Torchfeld.round(Torchfeld.astype(vor['ruhezentren'], torch.float64), 6).tolist()}
        elif ergebnis.get('ausgabe') == 'kanaele' and all(g + '_dreh' in vor.files for g in gruppen_da) and Npztorch.da(ordner / 'kinematik.json'):
            kin = json.loads((ordner / 'kinematik.json').read_text(encoding='utf-8'))['knochen']
            if [k['name'] for k in kin] == namen:
                haltung = {'art': 'kanaele', 'ruhezentren': Torchfeld.round(Torchfeld.feld([k['zentrum'] for k in kin], copy=True), 6).tolist()}
            else:
                logger.warning('Meshgenesisdaten: kinematik.json von %s passt nicht zum Rig — das Ergebnis wird mit der Näherung gehäutet', ordner)
        proben = []
        wege = Meshgenesiswege.lesen(lauf, len(namen))
        # Zwischenbild „Rig → A-Pose" (17.10.2026, `Meshgenesisapose`): die Probe, auf der die Kette der Vorstufe lief, bekommt das vierte Feld.
        apose = Meshgenesisapose.vorhanden(lauf)
        for gruppe in gruppen_da:
            dreh = vor[gruppe + '_dreh'] if haltung else [None] * len(vor[gruppe + '_nr'])
            for nr, ausgabe, d in zip(vor[gruppe + '_nr'], vor[gruppe + '_rig'], dreh, strict=True):
                p = cls._probe(plan[int(nr)], gruppe, soll[int(nr)], Torchfeld.astype(ausgabe, torch.float64), namen, gruppen, vergleich, d)
                if wege and int(nr) in wege['proben']:
                    cls._wege(p, wege, plan[int(nr)], gruppe, soll[int(nr)], namen, gruppen, vergleich, haltung is not None)
                    p['apose'] = apose and int(nr) == Meshgenesisapose.PROBE
                # Zwischenschritt „nur Rig“ (16.10.2026): das Skelett von „Mesh to 3D“ in der Außenfläche, falls für diese Probe gerechnet (`Meshgenesisautorig`).
                p['rig']['autorig'] = Meshgenesisautorig.lesen(ordner, nr, soll[int(nr)], namen)
                proben.append(p)
        proben.sort(key=lambda p: p['id'])
        masse = ergebnis.get('maße') or {}
        # `modell`: der Name der Figur in den Texten der Zeilen (16.10.2026, Edgar auf der Seite von Mann1: „warum ist Kopf von Ursula1 in der Pose …? korrigiere“).
        return {'job': job['id'], 'modell': job.get('modell') or job['name'], 'attrappe': False, 'hinweis': cls.hinweis(lauf, ergebnis, job.get('modell')),
                'lauf': {'name': lauf.name, 'epochen': ergebnis.get('epochen'), 'dauer_s': ergebnis.get('dauer_s'), 'ausgabe': ergebnis.get('ausgabe', 'punkte')},
                'gelenke': [], 'rig': beschr, 'haltung': haltung, 'teile': Meshgenesisdatenteile.beschreibungen(), 'proben': proben,
                'ergebnis_flaeche': False, 'ergebnis_text': cls.ERGEBNIS_TEXT,
                'zusammenfassung': {'%s_mittel_mm' % g: masse.get(g, {}).get('netz_mm') for g in cls.GRUPPEN}}

    @classmethod
    def _wege(cls, p, wege, e, gruppe, soll, namen, gruppen, vergleich, mit_dreh):
        """Mehrere Wege zum Rig dieser Probe (`Meshgenesiswege`, 16.10.2026): je Weg Rig, Kennzahlen und Zeilen wie eine eigene Ausgabe; oben steht der Vorgabeweg, die Seite schaltet um."""
        alternativen = {}
        for w in wege['wege']:
            rig, dreh = wege['proben'][int(e['nr'])][w['schluessel']]
            q = cls._probe(e, gruppe, soll, rig, namen, gruppen, vergleich, dreh if mit_dreh else None)
            alternativen[w['schluessel']] = {'name': w['name'], 'text': w['text'], 'rig': q['rig'], 'kennzahlen': q['kennzahlen'], 'teile': q['teile']}
        vorgabe = alternativen[wege['standard']]
        p.update(rig=vorgabe['rig'], kennzahlen=vorgabe['kennzahlen'], teile=vorgabe['teile'], wege=alternativen, weg=wege['standard'], wege_reihe=[w['schluessel'] for w in wege['wege']])
        # Welche Methode die A-Pose rechnete (18.10.2026 abends, Einstellungen → Mesh-Genesis): `fehlt` — der Job hat keinen Lauf der eingestellten Methode, gezeigt ist der jüngste.
        p['zwischenschritt'] = {'methode': wege['methode'], 'fehlt': wege['fehlt'], 'datei': wege['datei'], 'eingestellt': Meshgenesisaposewahl.NAMEN[Meshgenesisaposewahl.gewaehlt()]}

    @classmethod
    def _probe(cls, e, gruppe, soll, ausgabe, namen, gruppen, vergleich, dreh=None):
        # Dieselbe Kennzahlrechnung wie die Attrappe (Fehler je Punkt in mm, Mittel, größter, Anteil unter der Schwelle, je Gruppe) — hier über die 138 Rig-Punkte.
        k = Meshgenesisbild._kennzahlen(soll, ausgabe, namen, gruppen, cls.SCHWELLE_MM)
        k.update(vergleich.werte(int(e['nr']), soll, list(range(len(namen)))))
        # `datei`: die OBJ-Datei, aus der der Datensatz diese Probe liest (Ursula_Pose1, Probe 1) — sonst None (die Probe entsteht im Datenskript aus Pose und Modell).
        rig = {'soll': Torchfeld.round(soll, 4).tolist(), 'ausgabe': Torchfeld.round(ausgabe, 4).tolist(), 'je_mm': k['je_gelenk_mm'],
               'kennzahlen': {'mittel_mm': k['mittel_mm'], 'groesster_mm': k['groesster_mm'], 'groesster_knochen': k['groesster_gelenk'], 'knochen': len(namen)}}
        if dreh is not None:
            rig['dreh'] = Torchfeld.round(cls._quaternionen(Torchfeld.feld(dreh, dtype=torch.float64)), 5).tolist()
        # `start`: bei einem Trainingspaar ist der Start ein ANDERES Netz als das Ziel (Tripo) — das Feld zeigt die Wolke, nicht die Außenfläche des Ziels (`Meshgenesisechtzeichner`).
        return {'id': int(e['nr']), 'name': e['name'], 'quelle': e['quelle'], 'gruppe': gruppe, 'aufteilung': 'training' if gruppe == 'training' else 'pruefung',
                'start': 'wolke' if e.get('paar') else None,
                'bewegung': Path(e['bvh']).stem if e.get('bvh') else None, 'bild': e.get('bild'), 'datei': e.get('obj'),
                'soll': [], 'ausgabe': [], 'kennzahlen': k, 'eingabe': {'punkte': cls.EINGABE_ANZEIGE, 'echt': True}, 'rig': rig,
                'teile': Meshgenesisdatenteile.teile(soll, ausgabe, vergleich, int(e['nr']))}

    @classmethod
    def eingabe(cls, job, nr):
        """4.096 Punkte der Außenfläche dieser Probe mit ihren Farben (0–255) — eine feste Auswahl je Probe, damit die Wolke beim Wiederkommen gleich aussieht."""
        datei = Meshgenesisdatensatz.ordner(job['ordner']) / 'proben' / ('%04d' % int(nr)) / 'eingabe.npz'
        if not Npztorch.da(datei):
            return None
        e = Npztorch.lesen(datei)
        anzahl = cls.EINGABE_ANZEIGE_PAAR if job.get('paar') else cls.EINGABE_ANZEIGE
        wahl = torch.sort(Zufallsstrom.default_rng(int(nr)).choice(len(e['punkte']), min(anzahl, len(e['punkte'])), replace=False), stable=True).values
        # float64 vor dem Runden: float32 gerundet ergibt in JSON `-0.0020000000949949026` statt `-0.002` (gemessen: 326 KB je Wolke).
        # `etikett` = Teil je Punkt (`Meshgenesisflaeche.TEILE`) — die Zeilen „Nur Körper" und „Kleider" zeigen nur ihre Teile der Wolke.
        return {'nr': int(nr), 'von': int(len(e['punkte'])), 'punkte': Torchfeld.round(Torchfeld.astype(e['punkte'][wahl], torch.float64), 3).tolist(),
                'farbe': Torchfeld.astype(Torchfeld.clip(Torchfeld.round(e['farbe'][wahl] * 255), 0, 255), torch.int64).tolist(), 'etikett': Torchfeld.astype(e['etikett'][wahl], torch.int64).tolist()}

    @classmethod
    def animation(cls, job):
        """Die Bewegung der Standardanimation (Spagat) aus den Proben: jedes Bild der BVH-Datei ist genau eine Probe (Training oder zurückgehalten) — ohne Lücke, sonst `None`."""
        from .meshgenesisanimation import Meshgenesisanimation

        daten = cls.proben(job)
        if daten is None:
            return None
        bilder = sorted((p for p in daten['proben'] if p['bewegung'] == Meshgenesisanimation.NAME), key=lambda p: p['bild'])
        if not bilder or [p['bild'] for p in bilder] != list(range(len(bilder))):
            logger.warning('Meshgenesisdaten: die Bilder von %s sind nicht vollständig im Datensatz — die Animation bleibt die Attrappe', Meshgenesisanimation.NAME)
            return None
        bildzeit = Meshgenesisanimation.bildzeit(Meshgenesisattrappe.bvh(*Meshgenesisanimation.BVH))
        return {'attrappe': False, 'name': Meshgenesisanimation.NAME, 'quelle': 'A_Results/%s.bvh' % Meshgenesisanimation.NAME, 'bildzeit': round(bildzeit, 5), 'fps': round(1.0 / bildzeit, 2),
                'bilder': [dict(p, animation=True) for p in bilder]}
