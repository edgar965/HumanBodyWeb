# -*- coding: utf-8 -*-
u"""G9eigenhaarbau — die Generatoren „Eigen Haar“ und „Eigen Bart“: Haar und Bart aus der Haar-Engine auf der aktuellen Figur, Sorten von „Haar – Generisch“.

Edgar, 16.11.2026: „bei dem Genesis Objekt ‚Eigen Haar‘ möchte ich einstellungen haben, die du mit deiner Klasse zur verfügung stellst, das Haar soll dann auf das aktuelle Modell
gebaut werden im Character“ — erst ein eigener Eintrag; am selben Abend „Haar Eigen und Haar generisch versuche zu mergen, ich brauche nur einen“: seitdem Sorten im
Sammeleintrag (`G9haargenerisch`, `sorte.<kennung>` und `<kennung>.<regler>`), gemischt von `G9haarmischbau`; dann „mach weiter mit der Bart Klasse und Bart Generator im UI“:
der Bart als zweite Sorte, Kennung auf `_beard` — damit trägt die Mischung ihn ZUSÄTZLICH zur Frisur (`G9haargenerisch.ZUSATZ`), sein Anteil ist seine Dichte.
`sorten` liefert die Einträge (Regler aus `Eigenhaar.regler` bzw. `Eigenbart.regler`). Der Bau (`antwort`): Ruhelage der Figur (`G9formung.morphpunkte`, Käfig) → Strähnen der
Engine (`haar_Bart/eigenhaar.py`, `eigenbart.py`), Dichte mal Anteil der Sorte → ein Stranghaar-Teil (`G9eigenhaarstrang`) → derselbe Weg wie jedes Stück
(`G9garderobeapi._kleid` mit `teile`/`bilder`: Stellung, Lagen, Antwortform).

Karte: die Engine rechnet in torch auf der Grafikkarte, im Faden der Anfrage (wie die Eigenregler, `G9eigenkarte`; Edgar 16.11.2026: ohne Gpusperre „OK“). Ist auf der Karte
weniger als `FREI_GB` frei (Foto-Genesis rechnet), baut sie nicht und sagt es (Foto-Genesis hat Vorrang).
"""
import logging

from django.http import JsonResponse

from .meshgenesissuchpfad import Meshgenesissuchpfad

__all__ = ['G9eigenhaarbau']

logger = logging.getLogger('core')


class G9eigenhaarbau:
    #: Kennung → (Name, Klasse in `haar_Bart`)
    GENERATOREN = {'eigen_haar': (u'Eigen Haar', 'Eigenhaar'), 'eigen_beard': (u'Eigen Bart', 'Eigenbart')}
    #: Farbe der Linien (sRGB 0 … 1, Wurzel und Spitze), bis der Eintrag umgefärbt wird — Setzung
    FARBE, FARBE_SPITZE = [0.30, 0.19, 0.11], [0.45, 0.31, 0.19]
    FREI_GB = 3.0
    #: Quellen, deren Inhalt in den Schlüssel des Antwortvorrats geht (die Engine liegt außerhalb von `G9antworten.QUELLEN`)
    QUELLEN = ('meshgenesis/haar_Bart', 'HumanBodyWeb/core/dienste/g9eigenhaarbau.py', 'HumanBodyWeb/core/dienste/g9eigenhaarstrang.py',
               '3DObjects/meshgenesis/_katalog/haarkopfhaut_f1.pt',                # Kopfhaut der Genesis-Frisuren (`Haarkopfhaut`)
               '3DObjects/meshgenesis/_katalog/bartwuchs_f1.pt')                   # Bartwuchs der Genesis-Bärte (`Bartwuchs`)
    _quellen = None

    @staticmethod
    def _klasse(kennung):
        Meshgenesissuchpfad.einhaengen()
        from haar_Bart.eigenbart import Eigenbart
        from haar_Bart.eigenhaar import Eigenhaar
        return {'Eigenhaar': Eigenhaar, 'Eigenbart': Eigenbart}[G9eigenhaarbau.GENERATOREN[kennung][1]]

    @classmethod
    def kennzeichen(cls):
        u"""Für den Schlüssel des Antwortvorrats: ändert sich ein Byte der Engine (`QUELLEN`, einmal je Prozess gehasht), gilt keine alte Antwort."""
        Meshgenesissuchpfad.einhaengen()
        from django.conf import settings
        from haar_Bart.eigenwuchs import Eigenwuchs

        from .g9antwortquellen import G9antwortquellen
        if cls._quellen is None:
            cls._quellen = G9antwortquellen.fassung(settings.TOOLS_ROOT, cls.QUELLEN)
        return {'eigenwuchs': Eigenwuchs.FASSUNG, 'quellen': cls._quellen}

    @classmethod
    def ist(cls, kennung):
        return str(kennung or '') in cls.GENERATOREN

    @classmethod
    def sorten(cls):
        u"""Die erzeugten Sorten für `G9haargenerisch` (`erzeugt`): `[{id, name, regler}]`."""
        return [{'id': k, 'name': name, 'regler': cls._klasse(k).regler()} for k, (name, _klasse) in cls.GENERATOREN.items()]

    @classmethod
    def eintrag(cls, kennung):
        u"""Der Eintrag für `_kleid` — dieselbe Form wie ein `wearable` (`G9garderobeeintrag`), ohne Netz."""
        return {'id': kennung, 'name': cls.GENERATOREN[kennung][0], 'regler': cls._klasse(kennung).regler(), 'art': 'haar', 'datei': '', 'wurzel': '', 'zeigbar': True,
                'hinweis': '', 'vorschau': False, 'eigene_knochen': 0, 'varianten': [], 'stile': [], 'vorgaben': {}}

    @staticmethod
    def _kaefigdreiecke():
        import torch
        from Genesis9.basisnetz import G9basisnetz
        b = G9basisnetz.holen()
        return torch.as_tensor(b.ursprung, device='cuda').long()[torch.as_tensor(b.dreiecke, device='cuda').long()]

    @classmethod
    def antwort(cls, rumpf, kleid, formen, anteil=1.0, kennung='eigen_haar'):
        u"""Das Antwort-Dict — oder eine Fehlerantwort. `rumpf['regler_stueck']`: die Regler der Sorte ohne Präfix; `anteil`: Anteil der Sorte in der Mischung (Dichte mal
        Anteil). `kleid` = `G9garderobeapi._kleid`, `formen` = `G9figur.formung` (hereingereicht: dieser Dienst importiert die API nicht)."""
        import torch
        from Genesis9.rechenkarte import G9rechenkarte

        from .g9eigenhaarstrang import G9eigenhaarstrang
        name, klasse = cls.GENERATOREN[kennung][0], cls._klasse(kennung)
        frei = torch.cuda.mem_get_info()[0] / 2 ** 30
        if frei < cls.FREI_GB:
            return JsonResponse({'fehler': u'%s: auf der Grafikkarte sind nur %.1f GB frei (eine Rechnung läuft) — später noch einmal' % (name, frei)}, status=503)
        formung = formen(rumpf, {})
        ruhe = torch.as_tensor(formung.morphpunkte(), device='cuda').double()
        werte = klasse.werte(rumpf.get('regler_stueck'))
        werte['dichte'] *= float(anteil)
        try:
            with torch.no_grad():
                li = klasse(G9rechenkarte(torch)).bauen(ruhe, cls._kaefigdreiecke(), werte)
                folger = None if li is None else G9eigenhaarstrang(li, ruhe, name)
        except FileNotFoundError as fehler:                                    # Ablage der Kopfhaut / des Bartwuchses fehlt
            return JsonResponse({'fehler': u'%s: %s' % (name, fehler)}, status=404)
        if folger is None:
            return JsonResponse({'fehler': u'%s: keine Haut zum Wachsen bei diesen Reglern' % name}, status=404)
        logger.info('%s: %s', name, folger.steckbrief())
        bilder = {name: {'farbe': cls.FARBE, 'farbe_spitze': cls.FARBE_SPITZE}}
        return kleid(kennung, cls.eintrag(kennung), rumpf, teile=[(folger, None)], bilder=bilder)
