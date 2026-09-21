# -*- coding: utf-8 -*-
u"""Genesis-9-Figur (Daz) fuer Szene und Studio: Katalog, Netz, Regler, Garderobe.

    GET  /api/character/genesis9-figur/
         {figuren: [{name, anzeige, geschlecht, regler, haut}], vorhanden, punkte}
         — dahinter die gespeicherten Modelle (`gespeichert: true`, mit
         augen, brauen, kleidung), Netz und Katalog kennen ihre Namen.
    GET  /api/character/genesis9-figur/<name>/netz/            Vorgabestellung
    POST dieselbe Adresse, JSON {regler, haut, augen, brauen, brauenstil,
         praesets, pose, ausdruck, griffe, anhaenge}
         {name, vertices, faces, normals, uvs, gruppen[{name, index_ab,
          index_anzahl, bilder}], hautgewichte, skelett, hoehe, boden,
          vertex_count, punktzahl (Kaefig), browserpunkte, stufen,
          anhaenge: [{schluessel, name, vertices, …}]}
         Die Stufe ist die Daz-Ansichtsstufe 1, mit dem Keks `netzstufen`
         (Strg+Alt+H) die Renderstufe 2 (`G9netzstufe.browser`).
    GET  /api/character/genesis9-figur/regler/
         {bereiche: [{schluessel, name, regler}], haut: [...], augen: [...],
          praesets: [...], brauen, brauenstile, brauenfarben}
    Garderobe, Texturen und Posenliste: `g9garderobe.py` (seit 18.09.2026).

POSE UND AUSDRUCK (18.09.2026, `G9posen`): `pose` ist die Kennung eines
Daz-Posenpresets — seine Regler (Posensteuerungen, Korrekturmorphe) liegen
ueber denen des Nutzers, seine Knochendrehungen gehen an die Formung;
`ausdruck` stellt nur Regler (FACS). Beides ein Standbild. `griffe` sind
die Kennungen getragener Props (`G9garderobe.griff`): ihre Griffposen
schliessen die Finger um Dolch und Speer — ueber der Pose.

WARUM POST FUER DAS NETZ: Die Reglerstellung sind bis zu 108 Kanaele mit
Werten — dieselbe Entscheidung wie bei `Mhfigur.netz` (269 Regler passen
in keine Adresse). GET liefert die Vorgabestellung des Katalogeintrags
(fuer Tests und den ersten Blick).

Die Daten kommen aus der Daz-Bibliothek (`Genesis9/HERKUNFT.md`): gelesen
in Python, nichts davon im Repo. Fehlt sie, antwortet der Katalog leer mit
`vorhanden: false` — kein 500.
"""
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from ..daten.anfragerumpf import Anfragerumpf
from ..dienste.g9antworten import G9antworten
from .g9netzantwort import G9netzantwort
from ..dienste.modellkatalog import Modellkatalog
from Genesis9.brauen import G9brauen
from Genesis9.charaktere import G9charaktere
from Genesis9.formung import G9formung
from Genesis9.garderobe import G9garderobe
from Genesis9.hautpresets import G9hautpresets
from Genesis9.hautwahl import G9hautwahl
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.posen import G9posen
from Genesis9.schminke import G9schminke
from Genesis9.pfade import G9pfade
from Genesis9.reglerplan import G9reglerplan

logger = logging.getLogger('core')

__all__ = ['G9figur']

FEHLT = u'Daz-Bibliothek mit Genesis 9 fehlt — siehe Genesis9/HERKUNFT.md'


class G9figur:
    u"""Lesende Endpunkte auf Genesis 9."""

    # --------------------------------------------------------------- Katalog

    @staticmethod
    @require_GET
    def liste(request):
        if not G9pfade.vorhanden():
            return JsonResponse({'figuren': [], 'vorhanden': False,
                                 'fehler': FEHLT})
        try:
            figuren = [{'name': e['name'], 'anzeige': e['anzeige'],
                        'geschlecht': e['geschlecht'],
                        'regler': dict(e['regler']),
                        'haut': e.get('haut') or ''}
                       for e in G9charaktere.liste()]
        except (OSError, ValueError) as fehler:
            logger.warning('Genesis 9: Katalog nicht lesbar: %s', fehler)
            return JsonResponse({'figuren': [], 'vorhanden': True,
                                 'fehler': str(fehler)})
        # Dahinter die GESPEICHERTEN Genesis-9-Modelle (`data/models/*.json`
        # mit `quelle: genesis9`, 17.09.2026) — mit `gespeichert: true`, der
        # Dialog stellt sie in den zweiten Bereich.
        figuren += G9figur._gespeicherte()
        from Genesis9.basisnetz import G9basisnetz
        return JsonResponse({'figuren': figuren, 'vorhanden': True,
                             'punkte': G9basisnetz.holen().steckbrief()})

    @staticmethod
    def _gespeicherte():
        aus = []
        for e in Modellkatalog.gespeicherte():
            if e['quelle'] != 'genesis9':
                continue
            eintrag = G9figur._eintrag(e['name'])
            if eintrag is not None:
                aus.append({'name': e['name'], 'anzeige': e['name'],
                            'geschlecht': eintrag['geschlecht'],
                            'regler': dict(eintrag['regler']),
                            'haut': eintrag.get('haut') or '',
                            'augen': eintrag.get('augen') or '',
                            'brauen': eintrag.get('brauen') or '',
                            'kleidung': dict(eintrag.get('kleidung') or {}),
                            'praesets': dict(eintrag.get('praesets') or {}),
                            'hautmischung': dict(eintrag.get('hautmischung') or {}),
                            'brauenstil': eintrag.get('brauenstil') or '',
                            'pose': eintrag.get('pose') or '',
                            'ausdruck': eintrag.get('ausdruck') or '',
                            'gespeichert': True})
        return aus

    @staticmethod
    def _eintrag(name):
        u"""Katalogeintrag der Bibliothek — oder ein gespeichertes Modell
        (`Modellkatalog.gespeichert`, `figur` aus `Genesis9Figur.toJSON`)."""
        eintrag = G9charaktere.eintrag(name)
        if eintrag is not None:
            return eintrag
        figur = Modellkatalog.gespeichert(name, 'genesis9')
        if figur is None:
            return None
        grund = G9charaktere.eintrag(str(figur.get('figur') or 'basis')) or {}
        regler = figur.get('regler') if isinstance(figur.get('regler'), dict) \
            else grund.get('regler') or {}
        return {'name': name, 'anzeige': name,
                'geschlecht': grund.get('geschlecht') or 'neutral',
                'regler': dict(regler),
                'haut': figur.get('haut') or grund.get('haut') or '',
                'augen': figur.get('augen') or '',
                'brauen': figur.get('brauen') or '',
                'kleidung': figur.get('kleidung') or {},
                'praesets': figur.get('praesets') or {},
                # Texturmischung (21.09.2026): {hautsatz: prozent}, gemischt im Browser.
                'hautmischung': figur.get('hautmischung') or {},
                'brauenstil': figur.get('brauenstil') or '',
                'pose': figur.get('pose') or '',
                'ausdruck': figur.get('ausdruck') or '',
                'bilder': grund.get('bilder') or {},
                'gespeichert': True}

    # ------------------------------------------------------------------ Netz

    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET', 'POST'])
    def netz(request, name):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        eintrag = G9figur._eintrag(name)
        if eintrag is None:
            return JsonResponse({'fehler': u'Unbekannte Genesis-9-Figur'},
                                status=404)
        rumpf = G9figur._rumpf(request)
        # Fertige Antworten je Stellung, Strg+Alt+H-Stufe vorausgerechnet
        # (`G9antworten`, 18.09.2026 nachts).
        return G9antworten.liefern(
            'koerper', name, rumpf, lambda: G9figur._koerper(name, eintrag, rumpf),
            eintrag=eintrag)

    @staticmethod
    def _koerper(name, eintrag, rumpf):
        u"""Das Antwort-Dict des Koerpers — oder eine Fehlerantwort."""
        # Ohne Angabe im Rumpf gelten Haut, Augen und Brauen des Eintrags —
        # bei einem gespeicherten Modell die gespeicherten.
        haut = G9figur._name(rumpf.get('haut')) or G9figur._name(
            eintrag.get('haut') if eintrag.get('gespeichert') else None)
        augen = (G9figur._name(rumpf.get('augen'))
                 or G9figur._name(eintrag.get('augen')) or '01')
        brauen = (G9figur._name(rumpf.get('brauen'))
                  or G9figur._name(eintrag.get('brauen')))
        praesets = (rumpf['praesets'] if isinstance(rumpf.get('praesets'), dict)
                    else eintrag.get('praesets') or {})
        brauenstil = (G9figur._name(rumpf.get('brauenstil'))
                      or G9figur._name(eintrag.get('brauenstil')))
        try:
            netz = G9koerpernetz(
                G9figur.formung(rumpf, eintrag), eintrag,
                hautpreset=haut, augen=augen,
                anhaenge=rumpf.get('anhaenge', True) is not False,
                brauen=brauen, praesets=praesets,
                brauenstil=brauenstil,
                kleidung=G9figur._kleidung(rumpf.get('kleidung'))).bauen()
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Genesis 9: Netz nicht baubar: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        antwort = G9figur._netzantwort(netz)
        antwort.update({
            'name': name, 'skelett': netz['skelett'], 'hoehe': netz['hoehe'],
            'boden': netz['boden'], 'punktzahl': netz['punktzahl'],
            'browserpunkte': netz['browserpunkte'], 'stufen': netz['stufen'],
            'morphwerte': netz['morphwerte'],
            'hdkanaele': netz.get('hdkanaele') or [],
            'gelenkregler': netz.get('gelenkregler') or {},
            'anhaenge': [dict(G9figur._netzantwort(a), schluessel=a['schluessel'],
                              name=a['name']) for a in netz['anhaenge']],
        })
        return antwort

    #: Netz -> Antwort-Dict (`G9netzantwort`, ausgelagert 18.09.2026 nachts).
    _netzantwort = staticmethod(G9netzantwort.aus)

    @staticmethod
    def formung(rumpf, eintrag, ohne_griff=None):
        u"""`G9formung` aus Reglern, Pose und Ausdruck des Rumpfs (sonst des
        Eintrags): Preset-Regler ueber Nutzerreglern, Drehung aus der Pose.
        `ohne_griff`: die Griffpose DIESES Stuecks weglassen — ein Genesis-8-
        Schuh ist in seiner Ruhelage schon so modelliert, wie er am posierten
        Fuss sitzt (`G9autofit`); die Figur stellt den Fuss, der Schuh bleibt."""
        regler = dict(rumpf['regler'] if isinstance(rumpf.get('regler'), dict)
                      else eintrag.get('regler') or {})
        drehung = {}
        for feld in ('ausdruck', 'pose'):
            kennung = G9figur._name(rumpf.get(feld)) or G9figur._name(
                eintrag.get(feld) if eintrag.get('gespeichert') else None)
            if not kennung:
                continue
            knochen, werte = G9posen.werte(kennung)
            regler.update(werte)
            if feld == 'pose':
                drehung = dict(knochen)
        for kennung in G9figur._namen(rumpf.get('griffe')):
            if kennung == ohne_griff:
                continue
            for name, kanaele in G9garderobe.griff(kennung).items():
                drehung.setdefault(name, {}).update(kanaele)
            # Dark Fantasy Weapons (Genesis 8) greifen ueber Posensteuerungen.
            regler.update(G9garderobe.griffregler(kennung))
        return G9formung.aus_abfrage(regler, drehung)

    @staticmethod
    def _kleidung(wert):
        u"""`[{kennung, stil: [Namen]}]` aus dem Rumpf — die getragenen Stuecke
        (`Genesis9Modell.kleidungsliste`), fuer die eigenen Knochen im Skelett."""
        aus = []
        for stueck in wert if isinstance(wert, list) else []:
            if isinstance(stueck, dict) and stueck.get('kennung'):
                aus.append({'kennung': G9figur._name(stueck['kennung']),
                            'stil': G9figur._namen(stueck.get('stil'))})
            elif isinstance(stueck, str):
                aus.append({'kennung': G9figur._name(stueck), 'stil': []})
        return aus

    @staticmethod
    def _rumpf(request):
        if request.method != 'POST':
            return {}
        rumpf, fehler = Anfragerumpf.lesen(request)
        return rumpf if fehler is None and isinstance(rumpf, dict) else {}

    @staticmethod
    def _namen(wert):
        u"""Eine Kennung oder eine Liste davon aus dem Rumpf — bereinigt."""
        roh = wert if isinstance(wert, (list, tuple)) else [wert]
        return [n for n in (G9figur._name(w) for w in roh) if n]

    @staticmethod
    def _name(wert):
        u"""Ein Presetname aus dem Rumpf — ohne Pfadzeichen, sonst None."""
        text = str(wert or '').strip()
        if not text or '/' in text or '\\' in text or '..' in text:
            return None
        return text[:80]

    # --------------------------------------------------------------- Regler

    @staticmethod
    @require_GET
    def regler(request):
        if not G9pfade.vorhanden():
            return JsonResponse({'bereiche': [], 'haut': [], 'augen': [],
                                 'brauen': [], 'fehler': FEHLT})
        from Genesis9.anhang import G9anhang
        return JsonResponse({
            'bereiche': G9reglerplan.bereiche(),
            'haut': G9hautpresets.hautpresets(),
            'augen': G9hautpresets.augen(),
            'praesets': G9hautwahl.kategorien() + G9schminke.katalog(),
            'brauen': G9anhang.brauenfarben(),
            'brauenstile': G9brauen.stile(),
            'brauenfarben': G9brauen.farben_je_art(),
        })
