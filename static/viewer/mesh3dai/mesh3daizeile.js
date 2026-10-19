/**
 * Mesh3daizeile — EINE Zeile der Seite „Mesh3D-AI“ (14.10.2026): drei gekoppelte Felder (Eingabe · gewünschte Ausgabe · Ausgabe des Netzes), die Reihe der Ansichtsarten und die Texte darunter.
 * Das Element der Zeile trägt `data-bereich` (Schlüssel in `Mesh3daibereiche`), die Felder `.mesh3dai-leinwand[data-art]`, die Texte `[data-info]` und die Reihe `.mesh3dai-ansicht` (Schaltknöpfe)
 * (Arten aus `Mesh3daimaterial.MODI` — Oberfläche, Drahtnetz, Textur, Matcap …). Seit 15.10.2026 gelten Ansichtsart und Rig-Knopf für ALLE Zeilen gemeinsam (`Mesh3daizeile.alle`).
 */
import { Mesh3daianimationsleiste } from './mesh3daianimationsleiste.js';
import { Mesh3daiansicht } from './mesh3daiansicht.js';
import { Mesh3daiansichtgedaechtnis } from './mesh3daiansichtgedaechtnis.js';
import { Mesh3daiapose } from './mesh3daiapose.js';
import { Mesh3daibereiche } from './mesh3daibereiche.js';
import { Mesh3daiechtteile } from './mesh3daiechtteile.js';
import { Mesh3daiguete } from './mesh3daiguete.js';
import { Mesh3daimaterial } from './mesh3daimaterial.js';

export class Mesh3daizeile {
    /** Alle Zeilen der Seite — Ansichtsart und Rig-Knopf gelten für alle gemeinsam. */
    static alle = [];

    constructor(element) {
        Mesh3daizeile.alle.push(this);
        this.element = element;
        this.schluessel = element.dataset.bereich;
        this.bereich = Mesh3daibereiche.fuer(this.schluessel);
        this.ansichten = [...element.querySelectorAll('.mesh3dai-leinwand')]
            .map(feld => new Mesh3daiansicht(feld, feld.dataset.art, this.bereich.zeichner, this.bereich.kamera));
        Mesh3daiansicht.koppeln(this.ansichten);
        this.info = Object.fromEntries([...element.querySelectorAll('[data-info]')].map(el => [el.dataset.info, el]));
        this.guete = element.querySelector('[data-guete]');
        this.modus = Mesh3daimaterial.VORGABE;
        this.rig = true;
        this._letzte = null;
        this._antwort = null;
        this._geist = false;   // wie das Kästchen „Soll als Geist“ (Vorgabe aus)
        this._ansichtwahl(element.querySelector('.mesh3dai-ansicht'));
        this._rigknopf(element.querySelector('.mesh3dai-rigleiste'));
        const leiste = element.querySelector('.mesh3dai-animation');
        this.animation = leiste ? new Mesh3daianimationsleiste(leiste, this) : null;
    }

    /**
     * Ansichtsart und Rig wie beim letzten Mal (16.10.2026, `Mesh3daiansichtgedaechtnis`) — für alle Zeilen, ohne zu zeichnen (die Seite ruft das vor der ersten Probe).
     * Eine Art, die es nicht mehr gibt, bleibt bei der Vorgabe.
     */
    static gemerktSetzen(stand) {
        const modus = Mesh3daimaterial.MODI.some(m => m.schluessel === stand?.modus) ? stand.modus : null;
        for (const zeile of Mesh3daizeile.alle) {
            if (modus) zeile.modusSetzen(modus, false);
            if (typeof stand?.rig === 'boolean') zeile.rigSetzen(stand.rig, false);
        }
    }

    /** Die Antwort des Servers für den Job (Beschreibungen von Gerüst, Rig und Zeilen) — die Animationsleiste braucht sie, um ein Bild der Bewegung zu zeichnen und den Job zu kennen. */
    get antwort() {
        return this._antwort;
    }

    /**
     * Neuer Job: die Antwort merken, eine laufende Animation anhalten und vergessen. Ansichtsarten und Rig-Knopf bleiben auch bei echten Daten stehen — sie wirken dort auf die gehäutete Figur
     * (`Mesh3daiechtzeichner`). Am 15.10.2026 hatte ich sie bei echten Daten ausgeblendet („warum hast du das denn wieder ausgebaut??“); das war falsch.
     */
    jobSetzen(antwort) {
        this._antwort = antwort;
        this.animation?.zuruecksetzen(true);
    }

    /**
     * Der Schaltknopf „Rig“: legt das Genesis-9-Rig über jede Ansichtsart (Vorgabe an — Edgar will das volle Skelett sehen). Er schaltet ALLE Zeilen
     * (Edgar, 15.10.2026: „die Ansicht-Umschalt-Buttons und Rig button sollen für alle Views gelten, also auch für ‚Nur Körper‘ usw“).
     */
    _rigknopf(leiste) {
        if (!leiste) return;
        const knopf = document.createElement('button');
        knopf.type = 'button';
        knopf.className = 'schaltknopf';
        knopf.dataset.rig = '';
        knopf.title = 'Das Genesis-9-Skelett ein- und ausblenden — in allen Zeilen: Soll in den Farben der Gruppen, Ausgabe nach dem Fehler je Knochen (grün bis rot). Gilt für jede Ansichtsart.';
        knopf.innerHTML = '<i class="fas fa-bone"></i> ';
        knopf.append('Rig');
        knopf.addEventListener('click', () => {
            const an = !this.rig;
            Mesh3daiansichtgedaechtnis.merken({ rig: an });
            for (const zeile of Mesh3daizeile.alle) zeile.rigSetzen(an);
        });
        this._rigKnopf = knopf;
        leiste.replaceChildren(knopf);
        this.rigSetzen(this.rig, false);
    }

    rigSetzen(an, zeichnen = true) {
        this.rig = an;
        this._rigKnopf?.classList.toggle('active', an);
        this._rigKnopf?.setAttribute('aria-pressed', String(an));
        if (zeichnen && this._letzte) this.zeigen(...this._letzte);
    }

    /** Die Reihe der Ansichtsarten aus `Mesh3daimaterial.MODI` bauen (ein Schaltknopf je Art, genau einer aktiv); ein Klick stellt ALLE Zeilen auf diese Art. */
    _ansichtwahl(reihe) {
        if (!reihe) return;
        this._modusKnoepfe = Mesh3daimaterial.MODI.map(m => {
            const knopf = document.createElement('button');
            knopf.type = 'button';
            knopf.className = 'schaltknopf';
            knopf.dataset.modus = m.schluessel;
            knopf.title = `${m.hinweis} Gilt für alle Zeilen.`;
            knopf.innerHTML = `<i class="fas ${m.icon}"></i> `;
            knopf.append(m.name);
            knopf.addEventListener('click', () => {
                Mesh3daiansichtgedaechtnis.merken({ modus: m.schluessel });
                for (const zeile of Mesh3daizeile.alle) zeile.modusSetzen(m.schluessel);
            });
            return knopf;
        });
        reihe.replaceChildren(...this._modusKnoepfe);
        this.modusSetzen(this.modus, false);
    }

    modusSetzen(modus, zeichnen = true) {
        this.modus = modus;
        for (const k of this._modusKnoepfe ?? []) k.classList.toggle('active', k.dataset.modus === modus);
        if (zeichnen && this._letzte) this.zeigen(...this._letzte);
    }

    /** Eine Probe aus der Probenwahl zeigen: eine laufende Animation hält an (die Felder zeigen dann die Probe, nicht ein Bild der Bewegung). */
    probe(antwort, probe, geist) {
        this.animation?.zuruecksetzen();
        this.zeigen(antwort, probe, geist);
    }

    /** Das Soll als Geist ein- oder ausschalten, ohne die Probe oder das Bild der Animation zu wechseln. */
    geistSetzen(geist) {
        this._geist = geist;
        if (this._letzte) this.zeigen(this._letzte[0], this._letzte[1], geist);
    }

    /** Ein Bild der Bewegung (hat die Form einer Probe) zeichnen. */
    zeigenBild(bild) {
        this.zeigen(this._antwort, bild, this._geist);
    }

    /** @param {object} antwort die Antwort von `/api/mesh3dai/<job>/proben/`; @param {object|null} probe; @param {boolean} geist das Soll als Drahtgitter über der Ausgabe */
    zeigen(antwort, probe, geist) {
        this._letzte = [antwort, probe, geist];
        this._antwort = antwort;
        this._geist = geist;
        const echt = antwort?.attrappe === false;
        // Echte Daten: der ganze Körper liegt in der Probe selbst, die Zeilen darunter sind Ausschnitte desselben Rigs und derselben Figur (`Mesh3daiechtteile`).
        const grund = !probe ? null : echt && this.schluessel !== 'koerper' ? Mesh3daiechtteile.daten(antwort, probe, this.schluessel) : this.bereich.daten(antwort, probe);
        // Die Punktwolke der Eingabe hängt an `id`; die Bilder der Bewegung tragen einen festen `punktsamen`, damit die Punkte nicht von Bild zu Bild flimmern.
        const d = grund ? {
            ...grund, probe, id: probe.punktsamen ?? probe.id, geist, modus: this.modus, echt, job: antwort.job, zeile: this.schluessel,
            rig: this.rig, rigBeschreibung: antwort.rig, rigIndizes: antwort.rig?.zeilen?.[this.schluessel], rigMassstab: this.bereich.rigMassstab, haltung: antwort.haltung ?? null,
        } : null;
        for (const a of this.ansichten) a.zeigen(d);
        let texte = !d ? {} : echt ? Mesh3daiechtteile.texte(this.schluessel, probe, grund.teil, this.modus, antwort.modell) : this.bereich.texte({ probe, ...grund });
        if (probe && !grund) texte = { ausgabe: 'Der Server liefert für diese Zeile keine Daten.' };
        this._aposeFeld(!!(echt && probe?.apose));
        if (this.info.apose) texte.apose = Mesh3daiapose.text(probe);
        for (const [art, el] of Object.entries(this.info)) el.textContent = texte[art] ?? '';
        // Unter dem Ergebnis: Tabelle „Wie gut?“ mit 14 Zahlen über die Rig-Punkte der Zeile (16.10.2026) — nur bei echten Daten.
        this.guete?.replaceChildren(echt && d ? Mesh3daiguete.tabelle(Mesh3daiguete.werte(grund.teil, d.rigIndizes, antwort.rig?.knochen ?? [])) : '');
    }

    /**
     * Das vierte Feld „Rig → A-Pose“ (17.10.2026, nur in der Zeile „Ganzer Körper“): sichtbar, wenn die Probe durch die Vorstufe lief; dann vier Spalten und die Felder heißen 1 Start · 2 Rig → A-Pose ·
     * 3 Ziel · 4 Ergebnis, sonst drei wie bisher.
     */
    _aposeFeld(sichtbar) {
        const feld = this.element.querySelector('[data-feld="apose"]');
        if (!feld) return;
        feld.hidden = !sichtbar;
        feld.parentElement.classList.toggle('mesh3dai-bereiche-vier', sichtbar);
        const folge = sichtbar ? ['eingabe', 'apose', 'soll', 'ausgabe'] : ['eingabe', 'soll', 'ausgabe'];
        for (const nummer of this.element.querySelectorAll('[data-nummer]')) {
            const platz = folge.indexOf(nummer.dataset.nummer);
            if (platz >= 0) nummer.textContent = String(platz + 1);
        }
    }
}
