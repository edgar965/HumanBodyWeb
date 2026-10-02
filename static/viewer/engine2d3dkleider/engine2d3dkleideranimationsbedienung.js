/**
 * Engine2d3dKleideranimationsbedienung — Knöpfe und Tasten der Animationsleiste (aus `Engine2d3dKleideranimation` herausgelöst,
 * 01.10.2026).
 *
 * Edgar (01.10.2026): „es fehlt die Stopptaste bei der Animation, das komplette rewind nach hinten, vorne, die
 * Pfeiltasten sollen um einen Frame verschieben" — dazu Play/Pause per Leertaste.
 *
 *     ⏮ Anfang   ◀ ein Bild zurück   ▶/⏸ Play/Pause   ⏹ Stopp (Ruhehaltung)   ▶ ein Bild vor   ⏭ Ende
 *     Tasten: Leertaste Play/Pause · ← → ein Bild · Pos1/Ende an Anfang/Ende — nicht, solange ein Eingabefeld den
 *     Fokus hat.
 */
export class Engine2d3dKleideranimationsbedienung {
    static TASTEN = {
        Space: a => a.umschalten(),
        ArrowLeft: a => a.bild(-1),
        ArrowRight: a => a.bild(1),
        Home: a => a.springen(false),
        End: a => a.springen(true),
    };

    constructor(animation) {
        this.a = animation;
        const knopf = (id, tun) => document.getElementById(id)?.addEventListener('click', tun);
        knopf('anim-anfang', () => this.a.springen(false));
        knopf('anim-zurueck', () => this.a.bild(-1));
        knopf('anim-play', () => this.a.umschalten());
        knopf('anim-stopp', () => this.a.stoppen());
        knopf('anim-vor', () => this.a.bild(1));
        knopf('anim-ende', () => this.a.springen(true));
        const schieber = this.a.scrubber;
        schieber.addEventListener('input', () => this.a.gezogen());
        schieber.addEventListener('mousedown', () => { this.a._ziehen = true; });
        schieber.addEventListener('touchstart', () => { this.a._ziehen = true; }, { passive: true });
        const loslassen = () => { this.a._ziehen = false; };
        schieber.addEventListener('mouseup', loslassen);
        schieber.addEventListener('touchend', loslassen);
        document.addEventListener('keydown', ereignis => this.taste(ereignis));
    }

    taste(ereignis) {
        const tun = Engine2d3dKleideranimationsbedienung.TASTEN[ereignis.code];
        if (!tun || !this.a.action || this.a.karte.hidden) return;
        const ziel = ereignis.target;
        if (ziel && (ziel.isContentEditable || /^(INPUT|TEXTAREA|SELECT|BUTTON)$/.test(ziel.tagName))) return;
        ereignis.preventDefault();
        tun(this.a);
    }
}
