# -*- coding: utf-8 -*-
"""Mesh3dvarianten — mehrere Ausgaben EINES Imports: dieselbe Einstellung mit anderem Wert gerechnet und nebeneinander gestellt (13.10.2026).

Edgar: „mach im Job Optionen für die unterschiedlichen Einstellungen, mit Vorschlag, was ich machen soll — ggf. mit Option, die Jobs mit beiden Optionen (z. B. nah und ignorieren für `kleidung_zug`)
auszurechnen und zu vergleichen", dann „berechnen von mehreren Ausgaben in einem Job". Konzept: `Docu/konzepte/2026-10-13_mesh-3d-ohne-nacharbeit-konzept.md`, Baustein C.

Eine Variante ist ein weiterer Auftrag „Mesh to 3D" (`Meshfigurauftrag`) auf demselben Körpernetz, derselben Segmentierung und derselben Pose wie die Hauptausgabe — nur ein Feld (`kleidung_zug`, `basis`, `pose`)
hat einen anderen Wert. Er speichert KEIN Modell (`modell = aus`); erst „Übernehmen" legt es an. Die Liste steht in `varianten.json` im Ordner des Imports (nicht in `stand.json`: den schreibt der Arbeitsprozess aus
seinem Speicher neu, `Mesh3dreiter` hat dieselbe Lehre). Gerechnet wird nacheinander in EINEM Prozess (`Mesh3dvariantenlauf`) — eine GPU, ein Lauf zugleich. Die Hauptausgabe zählt nicht mit: nur Werte, die sie
nicht schon hat.

Nur der Weg „netz": beim Weg „teile" folgen auf „figur" Stücke, Haut und Modell; eine zweite Figur daneben hätte nichts, womit sie sich vergleichen ließe.
"""

import json
import logging

from django.utils import timezone

from ..atomic_write import AtomarSchreiber
from ..daten.blendimportablage import Blendimportablage
from .blendimportarbeiter import Blendimportarbeiter

logger = logging.getLogger('core')

__all__ = ['Mesh3dvarianten']


class Mesh3dvarianten:
    DATEI = 'varianten.json'
    #: Minuten je Variante — Schritt „figur" des Wegs „netz" (Spiralballerina, Dateizeiten 13.10.2026: 13:41:16 → 13:45:35 = 4 min 19 s; Zauberer warm 244–250 s); eine Schätzung für die Anzeige.
    MINUTEN = 5
    #: So viele Varianten höchstens je Import (Platte und Zeit).
    HOECHSTENS = 8
    #: Die Felder, die sich als Variante rechnen lassen, mit den Werten, die der Katalog des Imports kennt. `weg`: nur dieser Weg.
    FELDER = (
        {'schluessel': 'kleidung_zug', 'titel': 'Stoff beim Anpassen', 'weg': 'netz',
         'werte': (('nah', 'nah — nur Stoff bis 7 cm Abstand zieht'), ('ignorieren', 'ignorieren — der Stoff zieht nicht'), ('weich', 'weich — der Stoff zieht schwach'))},
        {'schluessel': 'basis', 'titel': 'Grundfigur', 'weg': 'netz',
         'werte': (('feminine', 'Genesis 9 Feminine'), ('masculine', 'Genesis 9 Masculine'), ('neutral', 'Genesis 9 (neutral)'))},
        {'schluessel': 'pose', 'titel': 'Pose bestimmen', 'weg': 'netz',
         'werte': (('sam', 'SAM 3D Body'), ('aus', 'Aus — MediaPipe auf Renderings'))},
    )

    # ------------------------------------------------------------------ Datei

    @classmethod
    def pfad(cls, kennung):
        return Blendimportablage(kennung).ordner() / cls.DATEI

    @classmethod
    def lesen(cls, kennung):
        """`{eintraege: [...], haupt: id oder None}` — fehlt die Datei oder ist sie unlesbar, gibt es keine Varianten."""
        try:
            daten = json.loads(cls.pfad(kennung).read_text(encoding='utf-8'))
        except FileNotFoundError:
            daten = {}
        except (OSError, ValueError):
            logger.warning('Mesh-3D %s: %s nicht lesbar — keine Varianten', kennung, cls.DATEI)
            daten = {}
        eintraege = [e for e in daten.get('eintraege') or [] if isinstance(e, dict) and e.get('id') and e.get('feld')]
        vorher = daten.get('vorher') if isinstance(daten.get('vorher'), dict) else {}
        return {'eintraege': eintraege, 'haupt': daten.get('haupt') if daten.get('haupt') in {e['id'] for e in eintraege} else None, 'vorher': vorher}

    @classmethod
    def schreiben(cls, kennung, daten):
        cls.pfad(kennung).parent.mkdir(parents=True, exist_ok=True)
        AtomarSchreiber.json_schreiben(cls.pfad(kennung), {'eintraege': daten['eintraege'], 'haupt': daten.get('haupt'), 'vorher': daten.get('vorher') or {}})

    @classmethod
    def feld(cls, schluessel):
        for f in cls.FELDER:
            if f['schluessel'] == schluessel:
                return f
        raise ValueError('Dieses Feld lässt sich nicht als Variante rechnen: %s' % schluessel)

    @staticmethod
    def aktuell(stand, schluessel):
        """Der Wert des Felds im Import (Vorgabe wie die Hauptausgabe: `kleidung_zug` fehlt → `weich`, `pose` fehlt → `aus`)."""
        vorgabe = {'kleidung_zug': 'weich', 'pose': 'aus', 'basis': 'feminine'}
        return str((stand.get('einstellungen') or {}).get(schluessel) or vorgabe[schluessel])

    # --------------------------------------------------------------- Anlegen

    @classmethod
    def anlegen(cls, kennung, feld, werte=None):
        """Varianten anlegen und starten → `{angelegt: [...], uebersprungen: [...], minuten}`. `werte` leer: alle Werte des Felds, die weder die Hauptausgabe hat noch schon als Variante da sind.
        `ValueError` mit dem Grund, wenn es nicht geht (Weg, laufender Import, Hauptausgabe fehlt, Pose nicht gerechnet)."""
        from .mesh3dvariantenlauf import Mesh3dvariantenlauf

        ablage = Blendimportablage(kennung)
        stand = ablage.stand()
        f = cls.feld(feld)
        if not stand:
            raise ValueError('Kein Auftrag %s' % kennung)
        if (stand.get('weg') or 'teile') != f['weg']:
            raise ValueError('Varianten gibt es nur beim Weg „%s“ (ein verschmolzenes Netz)' % f['weg'])
        cls._frei(ablage, kennung)
        cls._hauptauftrag(stand)
        daten = cls.lesen(kennung)
        gueltig = [w for w, _ in f['werte']]
        gewuenscht = [str(w) for w in (werte or gueltig)]
        unbekannt = [w for w in gewuenscht if w not in gueltig]
        if unbekannt:
            raise ValueError('Unbekannter Wert für %s: %s' % (feld, ', '.join(unbekannt)))
        vorhanden = {e['wert'] for e in daten['eintraege'] if e['feld'] == feld} | {daten['vorher'].get(feld)}      # der Wert des ersten Laufs nach „Übernehmen“ steht schon in der Hauptausgabe
        eigen = cls.aktuell(stand, feld)
        zu_rechnen = [w for w in gewuenscht if w != eigen and w not in vorhanden]
        uebersprungen = [w for w in gewuenscht if w not in zu_rechnen]
        if not zu_rechnen:
            raise ValueError('Nichts zu rechnen: %s steht schon in der Hauptausgabe oder als Variante' % ', '.join(gewuenscht))
        if len(daten['eintraege']) + len(zu_rechnen) > cls.HOECHSTENS:
            raise ValueError('Höchstens %d Varianten je Auftrag — erst löschen' % cls.HOECHSTENS)
        for wert in zu_rechnen:
            cls._pose_pruefen(ablage, stand, f, wert)                               # vor dem ersten Auftrag: scheitert es, bleibt nichts liegen
        angelegt = [cls._eintrag(ablage, stand, f, wert) for wert in zu_rechnen]
        daten['eintraege'].extend(angelegt)
        cls.schreiben(kennung, daten)
        Mesh3dvariantenlauf.starten(kennung)
        logger.info('Mesh-3D %s: %d Variante(n) zu %s angelegt (%s)', kennung, len(angelegt), feld, ', '.join(e['wert'] for e in angelegt))
        return {'angelegt': angelegt, 'uebersprungen': uebersprungen, 'minuten': cls.MINUTEN * len(angelegt)}

    @classmethod
    def _frei(cls, ablage, kennung):
        from .mesh3dvariantenlauf import Mesh3dvariantenlauf

        if Blendimportarbeiter.lebt(ablage):
            raise ValueError('Der Auftrag rechnet — Varianten gehen danach')
        if Mesh3dvariantenlauf.lebt(kennung):
            raise ValueError('Varianten dieses Auftrags rechnen noch')
        andere = Blendimportarbeiter.laufender()
        if andere:
            raise ValueError('Der Import %s rechnet — GPU und Kerne gehören ihm' % andere)

    @staticmethod
    def _hauptauftrag(stand):
        from ..models import Meshfigurauftrag

        figur = (stand.get('ergebnis') or {}).get('figur') or {}
        try:
            job = Meshfigurauftrag.objects.filter(pk=figur.get('id')).first() if figur.get('id') else None
        except (ValueError, TypeError):
            job = None
        if job is None or job.status != 'fertig':
            raise ValueError('Die Hauptausgabe ist noch nicht gerechnet — Varianten vergleichen sich mit ihr')
        return job

    @staticmethod
    def _pose_pruefen(ablage, stand, f, wert):
        """Eine Variante mit `pose = sam` braucht die Pose des Imports (Schritt „pose“) — sonst scheitert sie erst beim Rechnen."""
        if f['schluessel'] != 'pose' or wert != 'sam':
            return
        from .blendimportkoerper import Blendimportkoerper
        from .blendimportpose import Blendimportpose

        try:
            Blendimportpose.zusatz(ablage, {**stand, 'einstellungen': {**(stand.get('einstellungen') or {}), 'pose': 'sam'}}, ablage.arbeit(Blendimportkoerper.DATEI))
        except RuntimeError as grund:
            raise ValueError(str(grund)) from grund

    @classmethod
    def _eintrag(cls, ablage, stand, f, wert):
        """Den Auftrag „Mesh to 3D“ der Variante anlegen (wie der Schritt „figur“ des Imports, nur mit einem anderen Wert) → ihr Eintrag in `varianten.json`."""
        from .blendimportfigur import Blendimportfigur
        from .blendimportkoerper import Blendimportkoerper

        titel = '%s: %s' % (f['titel'], wert)
        basis = wert if f['schluessel'] == 'basis' else cls.aktuell(stand, 'basis')
        zug = wert if f['schluessel'] == 'kleidung_zug' else cls.aktuell(stand, 'kleidung_zug')
        name = (stand.get('quelle') or {}).get('name') or ablage.kennung
        figur = Blendimportfigur(ablage, '%s · %s' % (name, titel), basis, netz=True, kleidung_zug=zug,
                                 animationspruefung=(stand.get('einstellungen') or {}).get('animationspruefung'))
        job = figur.anlegen(ablage.arbeit(Blendimportkoerper.DATEI))
        job.optionen = {**(job.optionen or {}), 'modell': 'aus'}                 # erst „Übernehmen“ legt ein Modell an
        job.save(update_fields=['optionen', 'updated_at'])
        return {'id': str(job.id), 'kennung': job.kennung, 'feld': f['schluessel'], 'wert': wert, 'titel': titel, 'basisname': name,
                'angelegt': timezone.now().isoformat()}

    # ------------------------------------------------------------- Übernehmen

    @classmethod
    def uebernehmen(cls, kennung, eintrag_id):
        """Eine Variante zur Ausgabe des Auftrags machen: der Wert gilt ab jetzt im Import (`stand.einstellungen`), die Seite zeigt ihre Figur als Hauptausgabe, und ihr Modell wird gespeichert
        (`ab speichern`, Name wie der Auftrag, bei Gleichheit nummeriert — das Modell der ersten Ausgabe bleibt). → `{wert, feld, modell_wird_gespeichert}`."""
        from .meshfigurarbeiter import Meshfigurarbeiter

        ablage = Blendimportablage(kennung)
        stand = ablage.stand()
        daten = cls.lesen(kennung)
        eintrag = next((e for e in daten['eintraege'] if e['id'] == eintrag_id), None)
        if not stand or eintrag is None:
            raise ValueError('Diese Variante gibt es nicht')
        cls._frei(ablage, kennung)
        job = cls._job(eintrag)
        if job is None or job.status != 'fertig':
            raise ValueError('Die Variante ist noch nicht fertig gerechnet')
        stand = ablage.stand()
        daten['vorher'].setdefault(eintrag['feld'], cls.aktuell(stand, eintrag['feld']))        # womit der erste Lauf gerechnet wurde (nur beim ersten Übernehmen je Feld)
        stand['einstellungen'] = {**(stand.get('einstellungen') or {}), eintrag['feld']: eintrag['wert']}
        ablage.stand_schreiben(stand)
        daten['haupt'] = eintrag['id']
        cls.schreiben(kennung, daten)
        speichern = not job.modell
        if speichern:
            job.name = eintrag.get('basisname') or job.name
            job.optionen = {**(job.optionen or {}), 'modell': 'an'}
            job.save(update_fields=['name', 'optionen', 'updated_at'])
            Meshfigurarbeiter.starten(job, ab='speichern')
        logger.info('Mesh-3D %s: Variante %s=%s übernommen (Modell wird gespeichert: %s)', kennung, eintrag['feld'], eintrag['wert'], speichern)
        return {'feld': eintrag['feld'], 'wert': eintrag['wert'], 'modell_wird_gespeichert': speichern}

    # --------------------------------------------------------------- Löschen

    @classmethod
    def loeschen(cls, kennung, eintrag_id=None):
        """Eine Variante (oder alle) entfernen: Auftrag „Mesh to 3D“ samt Ordner; gespeicherte Modelle bleiben (sie gehören dem Nutzer). → Anzahl."""
        from .mesh3dvariantenlauf import Mesh3dvariantenlauf

        daten = cls.lesen(kennung)
        if eintrag_id is None:
            Mesh3dvariantenlauf.anhalten(kennung)
        elif Mesh3dvariantenlauf.lebt(kennung):
            raise ValueError('Die Varianten rechnen — erst anhalten oder abwarten')
        weg = [e for e in daten['eintraege'] if eintrag_id in (None, e['id'])]
        for e in weg:
            cls._entfernen(e)
        daten['eintraege'] = [e for e in daten['eintraege'] if e not in weg]
        if daten['haupt'] in {e['id'] for e in weg}:
            cls._zuruecksetzen(kennung, daten, next(e for e in weg if e['id'] == daten['haupt']))
            daten['haupt'] = None
        if daten['eintraege']:
            cls.schreiben(kennung, daten)
        else:
            cls._datei_entfernen(kennung)
        return len(weg)

    @staticmethod
    def _zuruecksetzen(kennung, daten, eintrag):
        """Die übernommene Variante ist weg: der Import trägt wieder den Wert, mit dem sein erster Lauf gerechnet wurde (`vorher`)."""
        wert = daten['vorher'].pop(eintrag['feld'], None)
        ablage = Blendimportablage(kennung)
        if wert is None or Blendimportarbeiter.lebt(ablage):
            return
        stand = ablage.stand()
        if stand:
            stand['einstellungen'] = {**(stand.get('einstellungen') or {}), eintrag['feld']: wert}
            ablage.stand_schreiben(stand)

    @classmethod
    def alle_entfernen(cls, kennung):
        """Beim Löschen des Imports: alle Varianten mit (`Blendimportloeschen`)."""
        try:
            return cls.loeschen(kennung)
        except (OSError, ValueError):
            logger.exception('Mesh-3D %s: Varianten nicht entfernt', kennung)
            return 0

    @classmethod
    def _datei_entfernen(cls, kennung):
        try:
            cls.pfad(kennung).unlink()
        except OSError:
            logger.debug('Mesh-3D %s: %s war nicht da', kennung, cls.DATEI)

    @staticmethod
    def _job(eintrag):
        from ..models import Meshfigurauftrag

        try:
            return Meshfigurauftrag.objects.filter(pk=eintrag['id']).first()
        except (ValueError, TypeError):
            return None

    @classmethod
    def _entfernen(cls, eintrag):
        from ..daten.meshfigurablage import Meshfigurablage
        from .meshfigurarbeiter import Meshfigurarbeiter

        job = cls._job(eintrag)
        if job is None:
            return
        if job.laeuft:
            Meshfigurarbeiter.anhalten(job)
        Meshfigurablage(job.kennung).loeschen()
        job.delete()

    @classmethod
    def haupt_job(cls, kennung):
        """Der Auftrag „Mesh to 3D“ der übernommenen Variante oder `None`."""
        daten = cls.lesen(kennung)
        eintrag = next((e for e in daten['eintraege'] if e['id'] == daten['haupt']), None)
        return cls._job(eintrag) if eintrag else None

    @classmethod
    def haupt_loesen(cls, kennung):
        """Ein neuer Lauf des Imports rechnet die Hauptausgabe mit den jetzigen Einstellungen neu: die übernommene Variante ist dann keine Ausnahme mehr (`Blendimportarbeiter.starten`)."""
        daten = cls.lesen(kennung)
        if daten['haupt'] is None and not daten['vorher']:
            return
        daten['haupt'], daten['vorher'] = None, {}
        cls.schreiben(kennung, daten)

    @staticmethod
    def figur_von(job):
        """Was `stand.ergebnis.figur` für die Hauptausgabe trägt (wie `Blendimportlauf._figur`) — für die Seite, wenn eine Variante übernommen ist."""
        e = job.ergebnis or {}
        return {'id': str(job.id), 'kennung': job.kennung, 'regler': len(job.stellung() or {}), 'rest': (e.get('rest') or {}).get('regler'), 'schammessung': e.get('schammessung'),
                'hautmodell': (e.get('koerper') or {}).get('haut'), 'kleidung': {k: (e.get('kleidung') or {}).get(k) for k in ('fehler', 'sapiens', 'hautmodell')}}
