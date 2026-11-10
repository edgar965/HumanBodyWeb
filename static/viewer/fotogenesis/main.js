/**
 * Einstieg der Jobseite „Foto-Genesis“ (08.11.2026) — vorher stand dieser Code als Inline-Skript in `templates/fotogenesis.html` und lud rund 240 ES-Module einzeln.
 *
 * Edgar: „optimiere das laden der seiten, alle modelle sollen innerhalb von max. 5 s angezeigt werden, auch genesis“. Gemessen im Chrome am 08.11.2026 (Zauberer Alle Textur):
 * 250 Einträge im Resource-Timing, davon 235 Module, jedes über den Server — Chrome stellt höchstens 6 Anfragen je Host gleichzeitig, die Daten der Felder warteten hinter den
 * Modulen. Jetzt EIN Bündel wie Szene, BVH Studio und Mesh-3D (`core/dienste/modulbuendel.py`, `EINSTIEGE['fotogenesis']`, Vorlagenmarke `{% fotogenesisskript %}`); ohne esbuild oder mit
 * Schalter aus lädt die Seite diesen Einstieg mit den Einzelmodulen, gleiches Verhalten.
 *
 * Was die Vorlage vorher über `{% if %}` entschied, steht in `#fotogenesis-start` (`data-test`, `data-jobname`) und in den Seitendaten (`genesiszeile.ergebnis`, `test.eigen`).
 * Importe in der Reihenfolge des alten Inline-Skripts (Auswertungsreihenfolge der Module bleibt).
 */
import { Fotogenesisseite } from './fotogenesisseite.js';
import { Fotogenesiskoerpergroesse } from './fotogenesiskoerpergroesse.js';
import { Auftragname } from '../gemeinsam/auftragname.js';
import { Fotogenesisnormalen } from './fotogenesisnormalen.js';
import { Fotogenesistextur } from './fotogenesistextur.js';
import { Fotogenesisform } from './fotogenesisform.js';
import { Fotogenesispshuman } from './fotogenesispshuman.js';
import { Fotogenesispshumaneingabe } from './fotogenesispshumaneingabe.js';
import { Fotogenesisjobwahl } from './fotogenesisjobwahl.js';
import { Fotogenesishautangleich } from './fotogenesishautangleich.js';
import { Fotogenesisweitverdeckung } from './fotogenesisweitverdeckung.js';
import { Exportleiste } from '../exportleiste/exportleiste.js';
import { Fotogenesisbewegung } from './fotogenesisbewegung.js';
import { Fotogenesisexportfigur } from './fotogenesisexportfigur.js';
import { Fotogenesismodellspeichern } from './fotogenesismodellspeichern.js';

const start = document.getElementById('fotogenesis-start')?.dataset ?? {};
const daten = JSON.parse(document.getElementById('fotogenesis-daten')?.textContent || '{}');
const element = id => document.getElementById(id);

if (start.test === '1') {
    Fotogenesiskoerpergroesse.binden(element('fotogenesis-groesse'));
    Fotogenesisnormalen.binden(element('fotogenesis-normalen'));
    Fotogenesistextur.binden(element('fotogenesis-textur'));
    Fotogenesisform.binden(element('fotogenesis-form'));
    Fotogenesispshuman.binden(element('fotogenesis-pshuman'));
    Fotogenesispshumaneingabe.binden(element('fotogenesis-pshumaneingabe'), element('fotogenesis-jobwahl'));
    Fotogenesisjobwahl.binden(element('fotogenesis-jobwahl'));
    Auftragname.binden();
}
const seite = Fotogenesisseite.aufbauen();
if (daten.genesiszeile?.ergebnis) Fotogenesishautangleich.binden(element('fotogenesis-hautangleich'), () => seite.genesiszeile?.hautort);
if (daten.genesiszeile?.ergebnis) Fotogenesisweitverdeckung.binden(element('fotogenesis-weitverdeckung'));         // Haut unter weiten Stücken (08.11.2026)
if (daten.test?.eigen) {
    const figur = new Fotogenesisexportfigur(daten.test.adresse, seite.genesisfeld);
    const genesiskarte = document.querySelector('[data-feld="genesis"]').closest('section');          // in der dritten Zeile tragen auch Feld 1 und 3 eine Exportleiste (04.11.2026)
    Exportleiste.starten(genesiskarte.querySelector('.exportleiste'), figur);
    Fotogenesisbewegung.leisten(seite, figur);
    Fotogenesismodellspeichern.binden(daten.test.adresse, `${start.jobname ?? ''} Foto-Genesis`, genesiskarte);
}
