/**
 * Importpflege — einen Blender-Import abbrechen, löschen und die verwaisten aufräumen (10.10.2026).
 *
 * Edgar (10.10.2026): „mach einen Button zum Löschen eines Imports oder verwaisten Imports" (im Dialog „Charakter hinzufügen") und
 * „mach einen Button daneben zum Abbrechen des Jobs — der Abbrechen löscht auch alle Importdaten" (neben der Fortschrittsleiste oben).
 * Beides sind Löschungen auf der Platte: davor steht eine Rückfrage, die sagt, WAS verschwindet (Plan vom Server,
 * `core/dienste/blendimportloeschen.py`) — Importordner mit Größe, Auftrag „Mesh to 3D", Stücke der Garderobe, Modell.
 * Stücke, die noch ein Modell oder ein anderer Import braucht, bleiben stehen; die Rückfrage nennt sie.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Importpflege {

    static ADRESSE = '/api/character/blendimport';

    /**
     * Rückfragen und löschen. `abbrechen`: der Import rechnet noch — er wird angehalten (Leiste oben).
     * `vorSenden()` läuft nach der Zusage und vor dem Löschen: die Leiste hört dort auf, den Stand zu erfragen.
     *
     * @returns true, wenn gelöscht wurde; false bei „Abbrechen" in der Rückfrage
     */
    static async loeschen(kennung, { abbrechen = false, vorSenden = null } = {}) {
        const plan = await Serverabruf.json(`${Importpflege.ADRESSE}/${encodeURIComponent(kennung)}/loeschplan/`);
        if (!window.confirm(Importpflege.text(plan, abbrechen))) return false;
        // Stücke, die noch ein Modell oder ein anderer Import braucht, bleiben von selbst — „möglichst alles weg" (Edgar): eine zweite, ausdrückliche Frage.
        const trotzdem = (plan.behalten || []).length > 0 && window.confirm(Importpflege.textTrotzdem(plan));
        vorSenden?.();
        await Serverabruf.senden(`${Importpflege.ADRESSE}/${encodeURIComponent(kennung)}/loeschen/`,
                                 { mit_modell: true, anhalten: Boolean(plan.laeuft), stuecke_trotzdem: trotzdem });
        // Leiste oben und Dialog „Modell importieren" hören zu und räumen ihre Anzeige dieses Imports weg.
        document.dispatchEvent(new CustomEvent(Importpflege.EREIGNIS, { detail: { kennung } }));
        return true;
    }

    static EREIGNIS = 'blendimport-geloescht';

    /** Text in die Zwischenablage — ohne Clipboard-Schnittstelle (unsichere Adresse) über ein verstecktes Feld; `knopf` meldet das Ergebnis. */
    static async kopieren(text, knopf) {
        const vorher = knopf.textContent;
        try {
            if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(text);
            } else {
                const feld = Object.assign(document.createElement('textarea'), { value: text });
                feld.style.cssText = 'position:fixed;opacity:0;top:0;left:0';
                document.body.appendChild(feld);
                feld.select();
                const ok = document.execCommand('copy');
                feld.remove();
                if (!ok) throw new Error('Kopieren nicht möglich');
            }
            knopf.textContent = 'Kopiert ✓';
        } catch (fehler) {
            knopf.textContent = 'Nicht kopiert';
            knopf.title = fehler.message;
        }
        setTimeout(() => { knopf.textContent = vorher; }, 1800);
    }

    /** Alle verwaisten Importe auf einmal: die Liste steht in der Rückfrage. @returns true, wenn gelöscht wurde */
    static async verwaisteLoeschen() {
        const antwort = await Serverabruf.json(`${Importpflege.ADRESSE}/verwaist/`);
        const plaene = antwort.importe || [];
        if (!plaene.length) {
            window.alert('Es gibt keine verwaisten Importe.');
            return false;
        }
        const zeilen = plaene.map(p => `• ${p.name} (${p.kennung}, ${p.mb} MB): ${p.verwaist}`);
        if (!window.confirm(`${plaene.length} verwaiste Importe löschen?\n\n${zeilen.join('\n')}\n\n`
                            + 'Gelöscht werden ihre Ordner und Aufträge „Mesh to 3D". Stücke und Modelle, die ein anderer Import '
                            + 'oder ein Modell noch braucht, bleiben.')) return false;
        const ergebnis = await Serverabruf.senden(`${Importpflege.ADRESSE}/verwaist/loeschen/`,
                                                  { kennungen: plaene.map(p => p.kennung) });
        const fehler = Object.entries(ergebnis.fehler || {});
        if (fehler.length) window.alert(`Nicht gelöscht:\n${fehler.map(([k, t]) => `${k}: ${t}`).join('\n')}`);
        const geblieben = Importpflege.gruppiert(Object.values(ergebnis.behalten || {}).flat());
        if (geblieben.length) {
            window.alert('Diese Stücke sind geblieben, weil sie noch gebraucht werden:\n\n' + geblieben.join('\n')
                         + '\n\nZum Löschen: den Import des Modells einzeln löschen (dort kommt die Frage, ob sie auch weg sollen).');
        }
        return true;
    }

    /** Die behaltenen Stücke, nach Grund zusammengefasst: „• Name, Name: Grund" (dieselbe Kennung steht nur einmal, auch wenn mehrere Importe sie nennen). */
    static gruppiert(stuecke) {
        const gruppen = new Map();
        const gesehen = new Set();
        for (const s of stuecke) {
            if (gesehen.has(s.kennung)) continue;
            gesehen.add(s.kennung);
            gruppen.set(s.grund, [...(gruppen.get(s.grund) || []), s.name || s.kennung]);
        }
        return [...gruppen].map(([grund, namen]) => `• ${namen.join(', ')}: ${grund}`);
    }

    /** Zweite Rückfrage: die Stücke, die geblieben wären, doch löschen? OK = ja (Papierkorb, zurückholbar), Abbrechen = sie bleiben. */
    static textTrotzdem(plan) {
        const verlierer = [...new Set(plan.behalten.flatMap(s => s.benutzer))];
        return ['Diese Stücke auch löschen?', '', ...Importpflege.gruppiert(plan.behalten), '',
                `OK: auch diese ${plan.behalten.length} Stücke löschen. Sie gehen in den Papierkorb der Garderobe (zurückholbar); `
                + `${verlierer.join(' und ')} verliert sie.`,
                'Abbrechen: die Stücke bleiben — der Import selbst wird trotzdem gelöscht.'].join('\n');
    }

    /** Der Text der Rückfrage aus dem Plan des Servers. */
    static text(plan, abbrechen) {
        const zeilen = [abbrechen && plan.laeuft
            ? `Import „${plan.name}" abbrechen?` : `Import „${plan.name}" löschen?`, ''];
        if (plan.laeuft) {
            zeilen.push(`Er rechnet noch (Schritt „${plan.schritt || '?'}") — der Lauf wird angehalten.`, '');
        }
        zeilen.push('Gelöscht wird:');
        zeilen.push(`• der Importordner (${plan.mb} MB: Rohdaten, Netze, gebackene Kacheln)`);
        if (plan.auftrag) zeilen.push(`• der Auftrag „Mesh to 3D" (${plan.auftrag.kennung})`);
        if (plan.stuecke.length) {
            zeilen.push(`• ${plan.stuecke.length} Stücke der Garderobe (im Papierkorb, zurückholbar): `
                        + plan.stuecke.map(s => s.name).join(', '));
        }
        if (plan.modelle.length) zeilen.push(`• das Modell „${plan.modelle.join('", „')}"`);
        if ((plan.behalten || []).length) {
            zeilen.push('', `Bleibt stehen: ${plan.behalten.length} Stücke, weil sie noch gebraucht werden:`,
                        ...Importpflege.gruppiert(plan.behalten),
                        'Nach „OK" fragt ein zweites Fenster, ob sie auch gelöscht werden sollen.');
        }
        return zeilen.join('\n');
    }
}
