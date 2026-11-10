# -*- coding: utf-8 -*-
"""Meshgenesisformlaufendpunkte — Seite EINES Trainingslaufs der gemeinsamen Netze (18.10.2026, Reiter „Formtraining“ auf /mesh-genesis/).

Edgar: „Ich möchte die Jobs auch öffnen können und Resultate sehen, mach Vorschlag“ → „mach deinen Vorschlag“.

GET /mesh-genesis/formtraining/<lauf>/   Stand, Verlauf (Kurve), Ergebnis je Gruppe, Vergleich mit dem vorigen Lauf derselben Art, Kopfmessung, Ergebnis je Figur, Einstellungen, Ausgelassenes, Log.
Alles von der Platte (`Meshgenesisformlauf`); ein Lauf, der noch rechnet, zeigt Kopfzeile, Verlauf und Log — Ergebnis-Tabellen erst nach `lauf_ergebnis.json`.
"""

import time

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

from ..dienste.meshgenesisformlauf import Meshgenesisformlauf
from ..dienste.meshgenesisformlauffiguren import Meshgenesisformlauffiguren
from ..dienste.meshgenesisformlaufgruppen import Meshgenesisformlaufgruppen
from ..dienste.meshgenesisformlaufkurve import Meshgenesisformlaufkurve
from ..dienste.meshgenesisformtraining import Meshgenesisformtraining
from ..dienste.meshgenesisformtrainingtabelle import Meshgenesisformtrainingtabelle
from ..dienste.meshgenesisformvariante import Meshgenesisformvariante
from ..dienste.meshgenesisformzellen import Meshgenesisformzellen as Z

__all__ = ['Meshgenesisformlaufendpunkte']


class Meshgenesisformlaufendpunkte:
    @staticmethod
    @require_GET
    def seite(request, lauf):
        jetzt = time.time()
        daten = Meshgenesisformlauf.lesen(lauf, jetzt)
        if daten is None:
            raise Http404('Kein Trainingslauf %s' % lauf)
        lf, e, vor = daten['lauf'], daten['ergebnis'], daten['vorgaenger']
        laeuft = lf['zustand'] == 'läuft'
        rest = lf['dauer_s'] / lf['epoche'] * (lf['epochen'] - lf['epoche']) if laeuft and lf['epoche'] and lf['epochen'] and lf['dauer_s'] else None
        return render(request, 'meshgenesis_formlauf.html', {
            'lf': lf, 'status': Meshgenesisformtrainingtabelle.status(lf, jetzt), 'laeuft': laeuft,
            'anteil': round(100.0 * lf['epoche'] / lf['epochen'], 1) if lf['epochen'] and lf['epoche'] else 0,
            'rest': Z.spanne(rest) if rest is not None else '',
            'zeiten': {'start': Z.datum(lf['start']), 'ende': Z.datum(lf['ende']), 'letzte': Z.datum(lf['letzte']),
                       'dauer': Z.spanne(lf['dauer_s']) if lf['dauer_s'] else '—', 'still': Z.spanne(jetzt - lf['letzte']) if lf['letzte'] else ''},
            'kopfzeile': daten['kopfzeile'], 'messung': Meshgenesisformtrainingtabelle.messung(lf['messung']),
            'kurve': Meshgenesisformlaufkurve.zeichnen(daten['verlauf']),
            'verlauftabelle': Meshgenesisformlauffiguren.verlauf(daten['verlauf']),
            'gruppen': Meshgenesisformlaufgruppen.gruppen(e),
            'vorgaenger': vor['lauf'] if vor else None,
            'vergleich': Meshgenesisformlaufgruppen.vergleich(e, vor['ergebnis']) if vor else None,
            'unterschiede': Meshgenesisformlaufgruppen.unterschiede(e, vor['ergebnis']) if vor and e else [],
            'kopf': Meshgenesisformlauffiguren.kopf(daten['kopf'], vor['kopf'] if vor else None),
            # Figuren mit Formvorhersage öffnen ihre Seite mit diesem Lauf (`/mesh-genesis/formvariante/<Figur>/?lauf=…`).
            'figuren': Meshgenesisformlauffiguren.figuren(e, daten['echt'], lf['name'], Meshgenesisformvariante.mit_seite(Meshgenesisformtraining.ordner() / lf['name'])),
            'echt': (daten['echt'] or {}).get('messgroesse') if daten['echt'] else '',
            'einstellungen': Meshgenesisformlaufgruppen.einstellungen(e),
            'ausgelassen': sorted((e.get('ausgelassen') or {}).items()) if isinstance(e.get('ausgelassen'), dict) else [],
            'log': daten['log'], 'log_weg': daten['log_weg'],
        })
