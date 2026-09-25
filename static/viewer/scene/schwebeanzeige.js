import { state } from './state.js';
import { _clearBoneHover, _createBoneOverlay, _getBoneFromIntersection,
         _removeBoneOverlay } from './knochenmarkierung.js';
import { _findSubMeshForObject, _sameSubMesh, _setSubMeshEmissive,
         getAllSubMeshTargets } from './teilnetz_auswahl.js';
import { Trefferwahl } from './trefferwahl.js';

/**
 * Was unter dem Mauszeiger liegt: Kleidungsstück oder Knochen, mit Namensschild
 * und Aufleuchten.
 *
 * Die Prüfung läuft gedrosselt über `requestAnimationFrame` — bei jeder
 * Mausbewegung zu strahlen kostet auf großen Szenen spürbar Bildrate.
 *
 * Aus interaction.js herausgelöst (Umbau 27.08.2026, Befund `jsfunktionen`:
 * `initSubMeshInteraction()` hatte 91 Zeilen).
 */
export class Schwebeanzeige {
    /** Abstand des Namensschilds zum Zeiger in Pixeln. */
    static SCHILD_X = 14;
    static SCHILD_Y = -10;

    /** @param {HTMLCanvasElement} canvas */
    constructor(canvas) {
        this.canvas = canvas;
        this.schild = document.getElementById('mesh-tooltip');
        canvas.addEventListener('mousemove', (e) => this._gemerkt(e));
        canvas.addEventListener('mouseleave', () => this._verlassen());
    }

    /** Merkt das Ereignis und prüft frühestens zum nächsten Bild. */
    _gemerkt(e) {
        state._lastMouseEvent = e;
        if (state._hoverPending) return;
        state._hoverPending = true;
        requestAnimationFrame(() => {
            state._hoverPending = false;
            if (state._lastMouseEvent) this._pruefen(state._lastMouseEvent);
        });
    }

    _verlassen() {
        if (state._hoveredSubMesh
            && !_sameSubMesh(state._hoveredSubMesh, state._selectedSubMesh)) {
            _setSubMeshEmissive(state._hoveredSubMesh, state._ZERO_EMISSIVE);
        }
        state._hoveredSubMesh = null;
        state._hoveredCharId = null;
        _clearBoneHover();
        if (this.schild) this.schild.style.display = 'none';
        this.canvas.style.cursor = '';
    }

    _pruefen(e) {
        // Während des Nachziehens verändert sich die Geometrie — ein Treffer
        // darauf wäre schon beim Auswerten veraltet.
        if (state._refitting) return;
        const rahmen = this.canvas.getBoundingClientRect();
        state.mouse.x = ((e.clientX - rahmen.left) / rahmen.width) * 2 - 1;
        state.mouse.y = -((e.clientY - rahmen.top) / rahmen.height) * 2 + 1;
        state.raycaster.setFromCamera(state.mouse, state.camera);

        const ziele = Schwebeanzeige._ziele();
        const treffer = this._treffer(ziele);
        this._schild(e, rahmen, treffer);
        // Die Figur unter der Maus — für die helle Aura (`scene/auswahlziele.js`).
        state._hoveredCharId = treffer.teilnetz ? null : (treffer.figurId || null);
        this._teilnetzwechsel(treffer.teilnetz);
        this._knochenwechsel(treffer.knochen, treffer.koerpernetz);
    }

    /**
     * Alle anstrahlbaren Objekte: Kleidungsstücke und Körpernetze. Eine
     * Genesis-Figur hat keine Knochenbereiche — ihr Körper und ihre Anhänge
     * (Augen, Brauen, Zähne) zeigen den Namen des Modells (20.09.2026, Edgar:
     * „auch bei der genesis figur soll der name des Modells angezeigt werden").
     */
    static _ziele() {
        const teilnetze = getAllSubMeshTargets();
        const wurzeln = teilnetze.map(t => t.meshObj);
        const koerper = [];
        const figuren = new Map();
        state.characters.forEach((figur, id) => {
            if (figur.generatedConfig && figur.bodyMesh
                && figur.bodyMesh.userData.boneVertexRanges) {
                koerper.push({ bodyMesh: figur.bodyMesh, charId: id });
                wurzeln.push(figur.bodyMesh);
            } else if (figur.quelle === 'genesis9' && figur.bodyMesh) {
                const schild = `${figur.presetName || figur.name || id} (Genesis 9)`;
                for (const netz of [figur.bodyMesh, ...Object.values(figur.anhangNetze || {})]) {
                    if (!netz) continue;
                    figuren.set(netz, { schild, id });
                    wurzeln.push(netz);
                }
            }
        });
        return { teilnetze, wurzeln, koerper, figuren };
    }

    /**
     * @returns {{teilnetz: Object|null, knochen: string|null,
     *            koerpernetz: Object|null, figur: string|null}}
     */
    _treffer(ziele) {
        const leer = { teilnetz: null, knochen: null, koerpernetz: null, figur: null };
        const treffer = state.raycaster.intersectObjects(ziele.wurzeln, true);
        if (treffer.length === 0) return leer;
        // Wie der Klick (`Trefferwahl`): durch den Stoff stechende Haut zeigt den Stoff.
        const teilnetz = Trefferwahl.waehlen(treffer, ziele.teilnetze, _findSubMeshForObject).ziel;
        if (teilnetz) return { ...leer, teilnetz };
        // Die Genesis-Figur selbst: Netz oder eines seiner Elternteile (Anhänge sind Gruppen).
        for (let o = treffer[0].object; o; o = o.parent) {
            if (ziele.figuren?.has(o)) {
                const { schild, id } = ziele.figuren.get(o);
                return { ...leer, figur: schild, figurId: id };
            }
        }
        // Kein Kleidungsstück — dann vielleicht ein Knochen des Körpernetzes.
        for (const eintrag of ziele.koerper) {
            if (treffer[0].object !== eintrag.bodyMesh) continue;
            return { teilnetz: null, figurId: eintrag.charId,
                     knochen: _getBoneFromIntersection(treffer[0],
                                                       eintrag.bodyMesh),
                     koerpernetz: eintrag.bodyMesh };
        }
        return leer;
    }

    _schild(e, rahmen, treffer) {
        const text = treffer.teilnetz ? treffer.teilnetz.label
                                      : (treffer.figur || treffer.knochen);
        if (!text || !this.schild) {
            if (this.schild) this.schild.style.display = 'none';
            this.canvas.style.cursor = '';
            return;
        }
        this.schild.textContent = text;
        this.schild.style.left =
            (e.clientX - rahmen.left + Schwebeanzeige.SCHILD_X) + 'px';
        this.schild.style.top =
            (e.clientY - rahmen.top + Schwebeanzeige.SCHILD_Y) + 'px';
        this.schild.style.display = 'block';
        this.canvas.style.cursor = 'pointer';
    }

    /** Das Ausgewählte behält sein Leuchten — es darf nicht überschrieben werden. */
    _teilnetzwechsel(neu) {
        if (_sameSubMesh(state._hoveredSubMesh, neu)) return;
        if (state._hoveredSubMesh
            && !_sameSubMesh(state._hoveredSubMesh, state._selectedSubMesh)) {
            _setSubMeshEmissive(state._hoveredSubMesh, state._ZERO_EMISSIVE);
        }
        state._hoveredSubMesh = neu;
        if (neu && !_sameSubMesh(neu, state._selectedSubMesh)) {
            _setSubMeshEmissive(neu, state._HOVER_EMISSIVE);
        }
    }

    _knochenwechsel(name, koerpernetz) {
        if (state._hoveredBoneName === name) return;
        if (state._boneHoverOverlay) {
            _removeBoneOverlay(state._boneHoverOverlay);
            state._boneHoverOverlay = null;
        }
        state._hoveredBoneName = name;
        if (name && koerpernetz && name !== state._selectedBoneName) {
            state._boneHoverOverlay = _createBoneOverlay(
                koerpernetz, name, state._BONE_HOVER_MAT);
        }
    }
}
