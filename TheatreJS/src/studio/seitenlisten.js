import { fetchAnimationList } from '../scene-manager.js';

/**
 * Seitenlisten — die Listen im rechten Bereich: Modelle, Animationen, Szenen.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026). Die drei Listen wurden dort
 * jeweils von Hand aufgebaut, mit denselben drei Schritten: Ladehinweis
 * schreiben, holen, Eintraege anhaengen — und im Fehlerfall dieselbe
 * Fehlerzeile, dreimal mit eigenem Inline-Stil ausgeschrieben.
 *
 * Der Modalfenster-Umgang (`openModal`/`closeModal` und zwei
 * Klick-Zuhoerer zum Schliessen) steckt ebenfalls hier: Er gehoert zur
 * Bedienung dieser Listen und stand sonst frei in der Datei.
 */
export class Seitenlisten {

    /**
     * @param {Figurenlader} lader
     * @param {Function} animationLaden  (kategorie, name) => Promise
     */
    constructor(lader, animationLaden) {
        this.lader = lader;
        this.animationLaden = animationLaden;
    }

    // ------------------------------------------------------------ Modalfenster

    static oeffnen(id) {
        const feld = document.getElementById(id);
        if (feld) feld.style.display = 'flex';
    }

    static schliessen(id) {
        const feld = document.getElementById(id);
        if (feld) feld.style.display = 'none';
    }

    /** Schliess-Knöpfe und Klick auf den Hintergrund verdrahten. */
    static modalfensterVerdrahten() {
        document.querySelectorAll('[data-close-modal]').forEach(knopf => {
            knopf.addEventListener('click', () => {
                knopf.closest('.theatre-modal-overlay')?.style.removeProperty('display');
            });
        });
        document.querySelectorAll('.theatre-modal-overlay').forEach(flaeche => {
            flaeche.addEventListener('click', ereignis => {
                if (ereignis.target === flaeche) {
                    flaeche.style.removeProperty('display');
                }
            });
        });
    }

    // ------------------------------------------------------------------ Listen

    /** Modell-Liste im rechten Bereich. */
    async modelle(zielId = 'model-list') {
        const ziel = document.getElementById(zielId);
        if (!ziel) return;
        await this._fuellen(ziel, () => this.lader.modellliste(),
                            'Keine Modelle gefunden.', (modelle) => {
            for (const modell of modelle) {
                ziel.appendChild(this._eintrag(modell.label || modell.name,
                    async (element) => {
                        await this.lader.modell(modell.name);
                        this._hervorheben(zielId, element);
                    }));
            }
        });
    }

    /** Animationsbaum: Kategorien zum Aufklappen. */
    async animationen(zielId = 'anim-tree') {
        const ziel = document.getElementById(zielId);
        if (!ziel) return;
        await this._fuellen(ziel, fetchAnimationList,
                            'Keine Animationen gefunden.', (kategorien) => {
            for (const [name, eintraege] of Object.entries(kategorien)) {
                ziel.appendChild(this._kategorie(name, eintraege, zielId));
            }
        });
    }

    /** Szenen-Liste im Lade-Fenster. */
    async szenen(zielId = 'scene-list-body') {
        const ziel = document.getElementById(zielId);
        if (!ziel) return;
        Seitenlisten.oeffnen('modal-scene-load');
        await this._fuellen(ziel, () => this.lader.szenenliste(),
                            'Keine Szenen gefunden.', (szenen) => {
            for (const szene of szenen) {
                const eintrag = this._eintrag(szene.label || szene.name, async () => {
                    Seitenlisten.schliessen('modal-scene-load');
                    await this.lader.szene(szene.name);
                });
                eintrag.classList.add('scene-item');
                ziel.appendChild(eintrag);
            }
        });
    }

    // ------------------------------------------------------------------ intern

    /**
     * Ladehinweis, Holen, Fuellen, Fehlerbehandlung — der gemeinsame Ablauf
     * aller drei Listen.
     */
    async _fuellen(ziel, holen, leertext, aufbauen) {
        ziel.innerHTML = '<div class="loading-msg">lädt …</div>';
        try {
            const daten = await holen();
            const leer = Array.isArray(daten)
                ? daten.length === 0 : Object.keys(daten || {}).length === 0;
            if (leer) {
                ziel.innerHTML = `<div class="loading-msg">${leertext}</div>`;
                return;
            }
            ziel.innerHTML = '';
            aufbauen(daten);
        } catch (fehler) {
            ziel.innerHTML = `<div class="loading-msg fehler">Fehler: ${fehler.message}</div>`;
            console.error('Liste nicht ladbar:', fehler);
        }
    }

    _eintrag(text, beiKlick) {
        const element = document.createElement('div');
        element.className = 'anim-item';
        element.textContent = text;
        element.addEventListener('click', async () => {
            try {
                await beiKlick(element);
            } catch (fehler) {
                console.error('Laden fehlgeschlagen:', fehler);
                alert('Laden fehlgeschlagen: ' + fehler.message);
            }
        });
        return element;
    }

    _kategorie(name, eintraege, zielId) {
        const gruppe = document.createElement('div');
        gruppe.className = 'anim-cat';
        const kopf = document.createElement('div');
        kopf.className = 'anim-cat-header';
        kopf.innerHTML = `<i class="fas fa-chevron-right"></i> ${name} (${eintraege.length})`;
        kopf.addEventListener('click', () => gruppe.classList.toggle('open'));
        gruppe.appendChild(kopf);

        const koerper = document.createElement('div');
        koerper.className = 'anim-cat-body';
        for (const anim of eintraege) {
            koerper.appendChild(this._eintrag(anim.name, async (element) => {
                await this.animationLaden(anim.category, anim.name);
                this._hervorheben(zielId, element);
            }));
        }
        gruppe.appendChild(koerper);
        return gruppe;
    }

    _hervorheben(zielId, element) {
        document.querySelectorAll(`#${zielId} .anim-item`)
            .forEach(e => e.classList.remove('active'));
        element.classList.add('active');
    }
}
