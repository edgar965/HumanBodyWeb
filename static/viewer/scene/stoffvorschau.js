import { Netznachricht } from '../gemeinsam/netznachricht.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Stoffvorschau — drapierte Kleidung folgt den Reglern, ohne neue Simulation.
 *
 * WARUM (Edgar, 08.09.2026: „mach mir auch einen 3D Vorschau der schnell ist
 * und synchron mit Regler geht", davor „vielleicht zweistufig — erst der
 * schnelle MakeHuman nachbau, dann das «echte» genaue Bauen?")
 * =====================================================================
 * Eine echte Drapierung kostet gemessen 24,5 s, davon 15,7 s Simulation.
 * Nach EINER Simulation steht aber fest, wo jeder Stoffpunkt relativ zum
 * Körper liegt. Diese Lage hält der Server fest (`Stoffnachfuehrung`), und
 * bei jedem Reglerzug wandert der Stoff mit — gemessen 8,4 ms bei 11.387
 * Punkten. Die zweite Stufe ist „Finalize": eine echte Simulation.
 *
 * WARUM ÜBER EINEN WEBSOCKET (Edgars Vorschlag): Die Bindung kostet
 * einmalig rund einer halben Sekunde und muss über die Reglerzüge hinweg
 * stehen bleiben. HTTP ist zustandslos — dort müsste sie bei jeder Anfrage
 * neu entstehen, und dann wäre nichts gewonnen.
 *
 * DIE VORSCHAU IST EINE VORSCHAU. Sie verschiebt den Stoff mit der Haut,
 * sie rechnet keine neue Physik: Wird die Figur dicker, dehnt sich der
 * Stoff mit, statt zu spannen. Deshalb meldet der Server die Abweichung von
 * der simulierten Form mit, und deshalb gibt es „Finalize".
 */
export class Stoffvorschau {

    static ADRESSE = '/ws/stoff/';

    /** Der eine Kanal dieser Seite. */
    static _kanal = null;
    static _zustand = { stoffErwartet: null };
    /** {stueck: THREE.Mesh} — wohin die Punkte gehören. */
    static _netze = {};
    /** Woher die aktuelle Stellung kommt, wenn der Server fragt. */
    static _stellung = null;

    // -- Verbindung -----------------------------------------------------------

    static verbinden() {
        if (Stoffvorschau._kanal
            && Stoffvorschau._kanal.readyState <= WebSocket.OPEN) {
            return Stoffvorschau._kanal;
        }
        const schema = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const kanal = new WebSocket(
            `${schema}://${window.location.host}${Stoffvorschau.ADRESSE}`);
        kanal.binaryType = 'arraybuffer';
        kanal.onmessage = (ereignis) => Netznachricht.verteilen(ereignis, {
            stoff: (puffer, stueck) => Stoffvorschau._setzen(puffer, stueck),
            stoffStand: (nachricht) => Stoffvorschau._stand(nachricht),
            stoffBindung: (nachricht) => Stoffvorschau._bindung(nachricht),
        }, Stoffvorschau._zustand);
        kanal.onclose = () => { Stoffvorschau._kanal = null; };
        kanal.onerror = () => Protokoll.debug('Stoffvorschau',
                                              'Kanal nicht erreichbar');
        Stoffvorschau._kanal = kanal;
        return kanal;
    }

    static _senden(nachricht) {
        const kanal = Stoffvorschau.verbinden();
        if (kanal.readyState === WebSocket.OPEN) {
            kanal.send(JSON.stringify(nachricht));
            return true;
        }
        if (kanal.readyState === WebSocket.CONNECTING) {
            // Der erste Aufruf kommt oft vor dem Verbindungsaufbau. Ihn
            // wegzuwerfen hieße: die Bindung entsteht nie, und die Vorschau
            // bleibt still stehen.
            kanal.addEventListener('open',
                () => kanal.send(JSON.stringify(nachricht)), { once: true });
            return true;
        }
        return false;
    }

    // -- Binden ---------------------------------------------------------------

    /**
     * Ein frisch drapiertes Stück an den Körper binden.
     *
     * @param stueck   Name des Kleidungsstücks
     * @param ordner   Ergebnisordner der Drapierung (der Server prüft ihn)
     * @param netz     das THREE-Netz, dessen Punkte nachgezogen werden
     * @param stellung {bauart, morphs, meta} der Figur
     */
    static binden(stueck, ordner, netz, stellung) {
        if (!stueck || !ordner || !netz) return false;
        Stoffvorschau._netze[stueck] = netz;
        Stoffvorschau._stellung = stellung || null;
        return Stoffvorschau._senden({
            type: 'stoff_binden', stueck, ordner, ...(stellung || {}),
        });
    }

    static loesen(stueck = null) {
        if (stueck) delete Stoffvorschau._netze[stueck];
        else Stoffvorschau._netze = {};
        Stoffvorschau._senden({ type: 'stoff_loesen', stueck });
    }

    /** Gibt es überhaupt etwas nachzuziehen? */
    static get aktiv() {
        return Object.keys(Stoffvorschau._netze).length > 0;
    }

    // -- Nachziehen -----------------------------------------------------------

    /** Die Figur hat sich geändert — den Stoff nachziehen lassen. */
    static nachziehen(stellung) {
        if (!Stoffvorschau.aktiv) return false;
        Stoffvorschau._stellung = stellung || Stoffvorschau._stellung;
        return Stoffvorschau._senden({
            type: 'stellung', ...(Stoffvorschau._stellung || {}),
        });
    }

    static _setzen(puffer, stueck) {
        const netz = Stoffvorschau._netze[stueck];
        if (!netz || !netz.geometry) return;
        const lage = netz.geometry.attributes.position;
        const neu = new Float32Array(puffer);
        if (neu.length !== lage.array.length) {
            // Punktzahl passt nicht: lieber gar nichts setzen als das Netz
            // zerreißen. Kommt vor, wenn die Bauart gewechselt wurde.
            Protokoll.debug('Stoffvorschau',
                `${stueck}: ${neu.length / 3} Punkte statt ${lage.count}`);
            return;
        }
        lage.array.set(neu);
        lage.needsUpdate = true;
        netz.geometry.computeVertexNormals();
        netz.geometry.computeBoundingSphere();
    }

    /**
     * Die Zeile unter den Knöpfen: Was gerade zu sehen ist.
     *
     * Ohne sie hält man die Vorschau für das Ergebnis. Der Abstand ist
     * gemessen — er sagt, wie weit die Figur von dem Körper entfernt ist,
     * auf dem wirklich simuliert wurde.
     */
    static _stand(nachricht) {
        const zeile = document.getElementById('gc-vorschau-hinweis');
        const text = document.getElementById('gc-vorschau-text');
        if (!zeile || !text) return;
        zeile.classList.remove('hb-versteckt');
        const mm = Number(nachricht.abstand_mm);
        text.textContent = isFinite(mm) && mm > 0
            ? `Vorschau: Der Stoff folgt den Reglern (${mm.toFixed(0)} mm von `
              + 'der simulierten Form entfernt).'
            : 'Vorschau: Der Stoff folgt den Reglern, ohne neu zu rechnen.';
    }

    /** Die Zeile wieder verstecken — nach einer echten Simulation. */
    static hinweisAus() {
        document.getElementById('gc-vorschau-hinweis')
            ?.classList.add('hb-versteckt');
    }

    static _bindung(nachricht) {
        if (nachricht.fehler) {
            Protokoll.warnung('Stoffvorschau', nachricht.fehler);
            delete Stoffvorschau._netze[nachricht.stueck];
            return;
        }
        Protokoll.debug('Stoffvorschau',
            `${nachricht.stueck}: ${nachricht.punkte} Punkte gebunden, `
            + `${nachricht.median_mm} mm zur Haut`);
    }
}
