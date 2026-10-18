# -*- coding: utf-8 -*-
"""Mesh3daiformlaufendpunkte — Seite EINES Trainingslaufs der gemeinsamen Netze (18.10.2026, Reiter „Formtraining“ auf /mesh-3D-AI/).

Edgar: „Ich möchte die Jobs auch öffnen können und Resultate sehen, mach Vorschlag“ → „mach deinen Vorschlag“.

GET /mesh-3D-AI/formtraining/<lauf>/   Stand, Verlauf (Kurve), Ergebnis je Gruppe, Vergleich mit dem vorigen Lauf derselben Art, Kopfmessung, Ergebnis je Figur, Einstellungen, Ausgelassenes, Log.
Alles von der Platte (`Mesh3daiformlauf`); ein Lauf, der noch rechnet, zeigt Kopfzeile, Verlauf und Log — Ergebnis-Tabellen erst nach `lauf_ergebnis.json`.
"""

import time

from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

from ..dienste.mesh3daiformlauf import Mesh3daiformlauf
from ..dienste.mesh3daiformlauffiguren import Mesh3daiformlauffiguren
from ..dienste.mesh3daiformlaufgruppen import Mesh3daiformlaufgruppen
from ..dienste.mesh3daiformlaufkurve import Mesh3daiformlaufkurve
from ..dienste.mesh3daiformtraining import Mesh3daiformtraining
from ..dienste.mesh3daiformtrainingtabelle import Mesh3daiformtrainingtabelle
from ..dienste.mesh3daiformvariante import Mesh3daiformvariante
from ..dienste.mesh3daiformzellen import Mesh3daiformzellen as Z

__all__ = ['Mesh3daiformlaufendpunkte']


class Mesh3daiformlaufendpunkte:
    @staticmethod
    @require_GET
    def seite(request, lauf):
        jetzt = time.time()
        daten = Mesh3daiformlauf.lesen(lauf, jetzt)
        if daten is None:
            raise Http404('Kein Trainingslauf %s' % lauf)
        lf, e, vor = daten['lauf'], daten['ergebnis'], daten['vorgaenger']
        laeuft = lf['zustand'] == 'läuft'
        rest = lf['dauer_s'] / lf['epoche'] * (lf['epochen'] - lf['epoche']) if laeuft and lf['epoche'] and lf['epochen'] and lf['dauer_s'] else None
        return render(request, 'mesh3dai_formlauf.html', {
            'lf': lf, 'status': Mesh3daiformtrainingtabelle.status(lf, jetzt), 'laeuft': laeuft,
            'anteil': round(100.0 * lf['epoche'] / lf['epochen'], 1) if lf['epochen'] and lf['epoche'] else 0,
            'rest': Z.spanne(rest) if rest is not None else '',
            'zeiten': {'start': Z.datum(lf['start']), 'ende': Z.datum(lf['ende']), 'letzte': Z.datum(lf['letzte']),
                       'dauer': Z.spanne(lf['dauer_s']) if lf['dauer_s'] else '—', 'still': Z.spanne(jetzt - lf['letzte']) if lf['letzte'] else ''},
            'kopfzeile': daten['kopfzeile'], 'messung': Mesh3daiformtrainingtabelle.messung(lf['messung']),
            'kurve': Mesh3daiformlaufkurve.zeichnen(daten['verlauf']),
            'verlauftabelle': Mesh3daiformlauffiguren.verlauf(daten['verlauf']),
            'gruppen': Mesh3daiformlaufgruppen.gruppen(e),
            'vorgaenger': vor['lauf'] if vor else None,
            'vergleich': Mesh3daiformlaufgruppen.vergleich(e, vor['ergebnis']) if vor else None,
            'unterschiede': Mesh3daiformlaufgruppen.unterschiede(e, vor['ergebnis']) if vor and e else [],
            'kopf': Mesh3daiformlauffiguren.kopf(daten['kopf'], vor['kopf'] if vor else None),
            # Figuren mit Formvorhersage öffnen ihre Seite mit diesem Lauf (`/mesh-3D-AI/formvariante/<Figur>/?lauf=…`).
            'figuren': Mesh3daiformlauffiguren.figuren(e, daten['echt'], lf['name'], Mesh3daiformvariante.mit_seite(Mesh3daiformtraining.ordner() / lf['name'])),
            'echt': (daten['echt'] or {}).get('messgroesse') if daten['echt'] else '',
            'einstellungen': Mesh3daiformlaufgruppen.einstellungen(e),
            'ausgelassen': sorted((e.get('ausgelassen') or {}).items()) if isinstance(e.get('ausgelassen'), dict) else [],
            'log': daten['log'], 'log_weg': daten['log_weg'],
        })
