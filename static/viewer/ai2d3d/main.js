/**
 * Einstieg der Jobseite „2d-3d-AI“ (08.11.2026) — vorher stand dieser Code als Inline-Skript in `templates/ai2d3d.html` und lud rund 240 ES-Module einzeln.
 *
 * Edgar: „optimiere das laden der seiten, alle modelle sollen innerhalb von max. 5 s angezeigt werden, auch genesis“. Gemessen im Chrome am 08.11.2026 (Zauberer Alle Textur):
 * 250 Einträge im Resource-Timing, davon 235 Module, jedes über den Server — Chrome stellt höchstens 6 Anfragen je Host gleichzeitig, die Daten der Felder warteten hinter den
 * Modulen. Jetzt EIN Bündel wie Szene, BVH Studio und Mesh-3D (`core/dienste/modulbuendel.py`, `EINSTIEGE['ai2d3d']`, Vorlagenmarke `{% ai2d3dskript %}`); ohne esbuild oder mit
 * Schalter aus lädt die Seite diesen Einstieg mit den Einzelmodulen, gleiches Verhalten.
 *
 * Was die Vorlage vorher über `{% if %}` entschied, steht in `#ai2d3d-start` (`data-test`, `data-jobname`) und in den Seitendaten (`genesiszeile.ergebnis`, `test.eigen`).
 * Importe in der Reihenfolge des alten Inline-Skripts (Auswertungsreihenfolge der Module bleibt).
 */
import { Ai2d3dseite } from './ai2d3dseite.js';
import { Ai2d3dkoerpergroesse } from './ai2d3dkoerpergroesse.js';
import { Auftragname } from '../gemeinsam/auftragname.js';
import { Ai2d3dnormalen } from './ai2d3dnormalen.js';
import { Ai2d3dtextur } from './ai2d3dtextur.js';
import { Ai2d3dform } from './ai2d3dform.js';
import { Ai2d3dpshuman } from './ai2d3dpshuman.js';
import { Ai2d3dpshumaneingabe } from './ai2d3dpshumaneingabe.js';
import { Ai2d3djobwahl } from './ai2d3djobwahl.js';
import { Ai2d3dhautangleich } from './ai2d3dhautangleich.js';
import { Ai2d3dweitverdeckung } from './ai2d3dweitverdeckung.js';
import { Exportleiste } from '../exportleiste/exportleiste.js';
import { Ai2d3dbewegung } from './ai2d3dbewegung.js';
import { Ai2d3dexportfigur } from './ai2d3dexportfigur.js';
import { Ai2d3dmodellspeichern } from './ai2d3dmodellspeichern.js';

const start = document.getElementById('ai2d3d-start')?.dataset ?? {};
const daten = JSON.parse(document.getElementById('ai2d3d-daten')?.textContent || '{}');
const element = id => document.getElementById(id);

if (start.test === '1') {
    Ai2d3dkoerpergroesse.binden(element('ai2d3d-groesse'));
    Ai2d3dnormalen.binden(element('ai2d3d-normalen'));
    Ai2d3dtextur.binden(element('ai2d3d-textur'));
    Ai2d3dform.binden(element('ai2d3d-form'));
    Ai2d3dpshuman.binden(element('ai2d3d-pshuman'));
    Ai2d3dpshumaneingabe.binden(element('ai2d3d-pshumaneingabe'), element('ai2d3d-jobwahl'));
    Ai2d3djobwahl.binden(element('ai2d3d-jobwahl'));
    Auftragname.binden();
}
const seite = Ai2d3dseite.aufbauen();
if (daten.genesiszeile?.ergebnis) Ai2d3dhautangleich.binden(element('ai2d3d-hautangleich'), () => seite.genesiszeile?.hautort);
if (daten.genesiszeile?.ergebnis) Ai2d3dweitverdeckung.binden(element('ai2d3d-weitverdeckung'));         // Haut unter weiten Stücken (08.11.2026)
if (daten.test?.eigen) {
    const figur = new Ai2d3dexportfigur(daten.test.adresse, seite.genesisfeld);
    const genesiskarte = document.querySelector('[data-feld="genesis"]').closest('section');          // in der dritten Zeile tragen auch Feld 1 und 3 eine Exportleiste (04.11.2026)
    Exportleiste.starten(genesiskarte.querySelector('.exportleiste'), figur);
    Ai2d3dbewegung.leisten(seite, figur);
    Ai2d3dmodellspeichern.binden(daten.test.adresse, `${start.jobname ?? ''} 2d-3d-AI`, genesiskarte);
}
