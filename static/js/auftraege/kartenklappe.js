/**
 * Kartenklappe — die Einstellungen einer Pipeline-Karte ein- und ausklappen.
 *
 * Bis zum 12.09.2026 klappte die WAHL einer Pipeline ihren Einstellungsblock
 * auf und die anderen zu; beim Laden stand damit die zuletzt gewaehlte Karte
 * offen, meist GVHMR. Edgar: „alle sollen per default eingeklappt sein".
 * Seither ist Waehlen (Radio, `Pipelinewahl`) vom Aufklappen getrennt: Beim
 * Laden ist alles zu, der Pfeil rechts im Kopf oeffnet und schliesst genau
 * seine Karte (`aria-controls` nennt den Block), und mehrere duerfen offen
 * sein. Der Knopf steht NEBEN dem <label> der Wahl, nicht darin — sonst
 * waehlte jeder Klick auf den Pfeil auch die Pipeline.
 */
export class Kartenklappe {

    static KNOPF = '.pipeline-card-klappe';
    static OFFEN = 'visible';

    static aufbauen() {
        return new Kartenklappe().aufbauen();
    }

    aufbauen() {
        document.querySelectorAll(Kartenklappe.KNOPF).forEach(knopf => {
            knopf.addEventListener('click', () => this.umschalten(knopf));
        });
        return this;
    }

    /** Der Einstellungsblock, den dieser Knopf steuert. */
    block(knopf) {
        return document.getElementById(knopf.getAttribute('aria-controls'));
    }

    /** Offen oder zu? Gelesen am Block, nicht am Knopf — der Block ist die Wahrheit. */
    offen(knopf) {
        return this.block(knopf)?.classList.contains(Kartenklappe.OFFEN) === true;
    }

    umschalten(knopf) {
        this.setzen(knopf, !this.offen(knopf));
    }

    setzen(knopf, offen) {
        const block = this.block(knopf);
        if (!block) {
            console.warn('Kartenklappe: kein Block', knopf.getAttribute('aria-controls'));
            return;
        }
        block.classList.toggle(Kartenklappe.OFFEN, offen);
        knopf.setAttribute('aria-expanded', offen ? 'true' : 'false');
    }
}
