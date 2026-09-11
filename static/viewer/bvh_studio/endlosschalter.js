import { state } from './state.js';
import { Protokoll } from '../gemeinsam/protokoll.js';

/**
 * Endlosschalter — der Knopf „Endlos" in der Abspielleiste.
 *
 * Schaltet `state.endlos`; die Schleife (`Studioschleife.abspielen`) fragt
 * ihn über `Abspielende` ab. Der Stand bleibt im `localStorage` dieses
 * Browsers (jeder Zugriff umschlossen — im privaten Fenster wirft schon das
 * Lesen, dann gilt die Vorgabe „aus").
 */
export class Endlosschalter {

    static SCHLUESSEL = 'bvhStudio_endlos';

    static binden() {
        const knopf = document.getElementById('pb-loop');
        if (!knopf) return null;
        state.endlos = Endlosschalter.gemerkt();
        Endlosschalter.zeigen(knopf);
        knopf.addEventListener('click', () => {
            state.endlos = !state.endlos;
            Endlosschalter.merken(state.endlos);
            Endlosschalter.zeigen(knopf);
            Protokoll.debug('BVH Studio', `Endlos ${state.endlos ? 'an' : 'aus'}`);
        });
        return knopf;
    }

    static zeigen(knopf) {
        knopf.classList.toggle('an', Boolean(state.endlos));
        knopf.setAttribute('aria-pressed', state.endlos ? 'true' : 'false');
    }

    static gemerkt() {
        try { return localStorage.getItem(Endlosschalter.SCHLUESSEL) === '1'; }
        catch (fehler) { return false; }
    }

    static merken(an) {
        try { localStorage.setItem(Endlosschalter.SCHLUESSEL, an ? '1' : '0'); }
        catch (fehler) { /* privates Fenster: nur für diese Sitzung */ }
    }
}
