/**
 * Einstieg der Testseite „Mesh3D-AI“ (08.11.2026) — vorher das Inline-Skript in `templates/mesh3dai_test.html`, das jedes Modul einzeln lud.
 *
 * Edgar: „optimiere das laden der seiten, alle modelle sollen innerhalb von max. 5 s angezeigt werden, auch genesis“. Jetzt EIN Bündel wie die Jobseite „2d-3d-AI“
 * (`core/dienste/modulbuendel.py`, `EINSTIEGE['mesh3dai']`, Vorlagenmarke `{% mesh3daiskript %}`); ohne esbuild lädt die Seite diesen Einstieg mit den Einzelmodulen.
 */
// Importe in der Reihenfolge des alten Inline-Skripts (Auswertungsreihenfolge der Module bleibt)
import { Mesh3daitestseite } from './mesh3daitestseite.js';
import { Auftragname } from '../gemeinsam/auftragname.js';
import { Mesh3dairechnen } from './mesh3dairechnen.js';
import { Mesh3daitestmesspunkte } from './mesh3daitestmesspunkte.js';
import { Mesh3dailinien } from './mesh3dailinien.js';
import { Mesh3daimeshanpassung } from './mesh3daimeshanpassung.js';
import { Exportleiste } from '../exportleiste/exportleiste.js';
import { Mesh3daiexportquelle } from './mesh3daiexportquelle.js';
import { Ai2d3dhautangleich } from '../ai2d3d/ai2d3dhautangleich.js';
import { Mesh3daitestwahl } from './mesh3daitestwahl.js';

const element = id => document.getElementById(id);
Mesh3daimeshanpassung.starten(element('mesh3dai-meshanpassung'));
Mesh3daitestseite.starten(element('mesh3dai-test'));
Mesh3daitestwahl.binden(element('mesh3dai-test'));
Ai2d3dhautangleich.binden(element('ai2d3d-hautangleich'), () => window.__mesh3daitest?.hautort);
// `starten` legt die Seite (und ihre bewegte Figur) gleich an, bevor es lädt — `window.__mesh3daitest`
Exportleiste.starten(element('exportleiste'), new Mesh3daiexportquelle(() => window.__mesh3daitest?.bewegung));
Mesh3dailinien.testStarten(element('mesh3dai-linien'));
Mesh3daitestmesspunkte.starten(element('mesh3dai-messpunkte'));
Mesh3daitestmesspunkte.gesichtStarten(element('mesh3dai-gesichtspunkte'));
Auftragname.binden();
new Mesh3dairechnen(element('mesh3dai-rechnen'));
