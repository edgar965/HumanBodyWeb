/**
 * Einstieg der Testseite „Mesh-Genesis“ (08.11.2026) — vorher das Inline-Skript in `templates/meshgenesis_test.html`, das jedes Modul einzeln lud.
 *
 * Edgar: „optimiere das laden der seiten, alle modelle sollen innerhalb von max. 5 s angezeigt werden, auch genesis“. Jetzt EIN Bündel wie die Jobseite „Foto-Genesis“
 * (`core/dienste/modulbuendel.py`, `EINSTIEGE['meshgenesis']`, Vorlagenmarke `{% meshgenesisskript %}`); ohne esbuild lädt die Seite diesen Einstieg mit den Einzelmodulen.
 */
// Importe in der Reihenfolge des alten Inline-Skripts (Auswertungsreihenfolge der Module bleibt)
import { Meshgenesistestseite } from './meshgenesistestseite.js';
import { Auftragname } from '../gemeinsam/auftragname.js';
import { Meshgenesisrechnen } from './meshgenesisrechnen.js';
import { Meshgenesistestmesspunkte } from './meshgenesistestmesspunkte.js';
import { Meshgenesislinien } from './meshgenesislinien.js';
import { Meshgenesismeshanpassung } from './meshgenesismeshanpassung.js';
import { Exportleiste } from '../exportleiste/exportleiste.js';
import { Meshgenesisexportquelle } from './meshgenesisexportquelle.js';
import { Fotogenesishautangleich } from '../fotogenesis/fotogenesishautangleich.js';
import { Meshgenesistestwahl } from './meshgenesistestwahl.js';

const element = id => document.getElementById(id);
Meshgenesismeshanpassung.starten(element('meshgenesis-meshanpassung'));
Meshgenesistestseite.starten(element('meshgenesis-test'));
Meshgenesistestwahl.binden(element('meshgenesis-test'));
Fotogenesishautangleich.binden(element('fotogenesis-hautangleich'), () => window.__meshgenesistest?.hautort);
// `starten` legt die Seite (und ihre bewegte Figur) gleich an, bevor es lädt — `window.__meshgenesistest`
Exportleiste.starten(element('exportleiste'), new Meshgenesisexportquelle(() => window.__meshgenesistest?.bewegung));
Meshgenesislinien.testStarten(element('meshgenesis-linien'));
Meshgenesistestmesspunkte.starten(element('meshgenesis-messpunkte'));
Meshgenesistestmesspunkte.gesichtStarten(element('meshgenesis-gesichtspunkte'));
Auftragname.binden();
new Meshgenesisrechnen(element('meshgenesis-rechnen'));
