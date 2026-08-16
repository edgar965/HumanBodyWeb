import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _bindSlider, _selectedInst } from './utils.js';
import { _applyGarmentRegionOffsets } from './kleidung_anpassen.js';
import { _doKleiderFit, _doKleiderStage1 } from './kleider_anpassen.js';
import { _kleiderSelectById, _renderKleiderList,
         _selectedKleiderMesh } from './kleider_liste.js';
import { Stueckbedienung } from './stueckbedienung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';

/**
 * Kleiderbedienung — der Reiter "Kleider" der Szene-Seite (Anpassen in Stufen).
 *
 * Aus scene/kleider.js herausgeloest (Umbau 16.08.2026): `loadKleiderUI()` hatte
 * 184 Zeilen. Vier Dinge daran waren mehr als lange Verdrahtung:
 *
 *  * Ein `setInterval(_updateKleiderVisibility, 1000)` als "Fallback für
 *    Randfälle" — ein Dauerläufer, der jede Sekunde das DOM anfasste, solange
 *    die Seite offen war. Jetzt wird die Sichtbarkeit dort nachgezogen, wo sie
 *    sich ändern kann: bei Reiterwechsel und über `fn.kleiderSichtbarkeit()`,
 *    das die Figurauswahl ruft.
 *  * Der Kleiderkatalog wurde per `setInterval(…, 200)` endlos gepollt →
 *    `Kleiderkatalog`.
 *  * Ein Debug-Protokoll (`_klog`/`_sendKlog`), das bei JEDEM Seitenaufbau
 *    seinen Verlauf per POST in die Einstellungen schrieb
 *    (`_kleider_debug_log`) — Fehlersuche von Hand, die in Betrieb blieb.
 *    Entfernt.
 *  * Die Wiederherstellung des zuletzt gewählten Stücks pollte die Liste
 *    zehnmal im Abstand von 300 ms. Die Liste wird direkt davor gebaut, also
 *    genügt ein Versuch danach.
 *
 * Alles, was dieser Reiter mit dem Assets-Reiter teilt — acht Regler, drei
 * Materialregler, Entprellung, fünf Regionsregler, Entfernen-Knöpfe, Katalog —
 * steckt in `Stueckbedienung`.
 */
export class Kleiderbedienung {

    /** Die drei Anpassschritte: Knopf-Kennung und Verfahren. */
    static SCHRITTE = [
        ['kleider-stage1', null],
        ['kleider-stage2', 'rig_hull'],
        ['kleider-stage3', 'body_refine'],
    ];

    async verdrahten() {
        this.teile = new Stueckbedienung({
            vorsilbe: 'kleider',
            schluessel: 'kld_',
            gewaehlt: _selectedKleiderMesh,
            anpassen: () => _doKleiderFit(),
            kennungMerken: kennung => { state._selectedKleiderId = kennung; },
            regionen: (figur, schluessel) =>
                _applyGarmentRegionOffsets(figur, schluessel),
            listeZeichnen: () => _renderKleiderList(),
        }).grundverdrahtung();

        // Nur dieser Reiter hat den Regler für die Dicke der Hülle.
        _bindSlider('kleider-bone-radius', 'kleider-bone-radius-val',
                    wert => parseFloat(wert).toFixed(1) + 'x');
        this._schritte();
        this._sichtbarkeit();
        if (await this.teile.katalogLaden()) await this.letzteAuswahl();
        return this;
    }

    /** Die drei Knöpfe: Hülle bauen, an die Hülle anpassen, am Körper feinen. */
    _schritte() {
        for (const [id, verfahren] of Kleiderbedienung.SCHRITTE) {
            document.getElementById(id)?.addEventListener('click', () => {
                if (verfahren === null) _doKleiderStage1();
                else _doKleiderFit(verfahren);
            });
        }
    }

    // -------------------------------------------------------------- Sichtbarkeit

    /**
     * Ohne gewählte Figur gibt es nichts anzukleiden — dann steht statt der
     * Bedienung ein Hinweis.
     */
    static sichtbarkeitNachziehen() {
        const hinweis = document.getElementById('kleider-empty');
        const inhalt = document.getElementById('kleider-content');
        if (!hinweis || !inhalt) return;
        const hatFigur = !!_selectedInst();
        hinweis.style.display = hatFigur ? 'none' : '';
        inhalt.style.display = hatFigur ? '' : 'none';
    }

    _sichtbarkeit() {
        Kleiderbedienung.sichtbarkeitNachziehen();
        // Die Figurauswahl ruft das hierüber (charakterliste.js) — statt des
        // früheren Sekundenintervalls.
        fn.kleiderSichtbarkeit = Kleiderbedienung.sichtbarkeitNachziehen;
        for (const reiter of document.querySelectorAll('.panel-tab')) {
            reiter.addEventListener('click', () => {
                Kleiderbedienung.sichtbarkeitNachziehen();
                if (reiter.dataset.tab === 'kleider') this._zurAuswahlRollen();
            });
        }
    }

    _zurAuswahlRollen() {
        if (!state._selectedKleiderId) return;
        document.getElementById('kleider-list')
            ?.querySelector('.anim-item.selected')
            ?.scrollIntoView({ block: 'center' });
    }

    // ----------------------------------------------------------- Letzte Auswahl

    /** Das zuletzt gewählte Stück wieder auswählen, wenn es in der Liste steht. */
    async letzteAuswahl() {
        let kennung = null;
        try {
            const daten = await Serverabruf.json('/api/settings/humanbody/');
            kennung = daten.ui_prefs?.last_kleider_id;
        } catch (fehler) {
            console.warn('Einstellungen nicht ladbar:', fehler);
            return;
        }
        if (!kennung) return;
        const vorhanden = [...(document.getElementById('kleider-list')
            ?.querySelectorAll('.anim-item') || [])]
            .some(eintrag => eintrag.dataset.kleiderId === kennung);
        if (vorhanden) _kleiderSelectById(kennung);
    }
}
