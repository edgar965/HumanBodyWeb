/**
 * BvhAnsicht — die kleine 3D-Ansicht auf der Auftragsseite: Gitter, Licht,
 * eine mit der Maus drehbare Kamera und die Bildzahl der BVH.
 *
 * Umbau 16.08.2026: `initBVHViewer()` hatte 171 Zeilen — Szene, Kamera, eigene
 * Maussteuerung, BVH-Lesen und das Zeichnen einer Ersatzfigur in einem Stück.
 * Die Ersatzfigur steckt jetzt in `Ersatzskelett` (bvh_ersatzskelett.js).
 *
 * Die Ansicht zeigt bewusst KEINE Animation: Sie liest der BVH nur die Bildzahl
 * ab und stellt eine T-Pose hin. Wer die Bewegung sehen will, nimmt die
 * Ergebnisseite.
 *
 * Klassisches Skript, kein ES-Modul: Die Seite lädt three.js r128 als globales
 * `THREE` vom CDN.
 */
class BvhAnsicht {

    static HINTERGRUND = 0x1a1a2e;
    static ERSATZHOEHE = 400;

    /** Kamera: Blickwinkel, Grenzen, Blickpunkt. */
    static SICHTFELD = 60;
    static NAH = 0.1;
    static FERN = 1000;
    static BLICKPUNKT = [0, 100, 0];

    /** Kugelkoordinaten der Kamera: Startwinkel und Abstand. */
    static START_PHI = Math.PI / 4;
    static START_ABSTAND = 300;
    static ABSTAND_MIN = 50;
    static ABSTAND_MAX = 800;
    /** Wie stark Mausbewegung und Rad wirken. */
    static DREH_SCHRITT = 0.01;
    static ZOOM_SCHRITT = 0.5;

    /** Gitter: Größe, Teilungen, Farben. */
    static GITTER = [400, 20, 0x2a2a4a, 0x1a1a2e];

    constructor(behaelterId) {
        this.behaelter = document.getElementById(behaelterId);
        this.kugel = { theta: 0, phi: BvhAnsicht.START_PHI,
                       abstand: BvhAnsicht.START_ABSTAND };
        this.zieht = false;
        this.letzteMaus = { x: 0, y: 0 };
    }

    /** Aufbauen und, wenn eine Adresse da ist, die BVH lesen. */
    starten(bvhAdresse) {
        if (!this.behaelter) return null;
        this._buehne();
        this._maussteuerung();
        this._anzeige();
        this.schleife();
        window.addEventListener('resize', () => this.groesseAnpassen());
        if (bvhAdresse) this.bvhLesen(bvhAdresse);
        return this;
    }

    masse() {
        return [this.behaelter.clientWidth,
                this.behaelter.clientHeight || BvhAnsicht.ERSATZHOEHE];
    }

    _buehne() {
        const [breite, hoehe] = this.masse();
        this.szene = new THREE.Scene();
        this.szene.background = new THREE.Color(BvhAnsicht.HINTERGRUND);
        this.szene.add(new THREE.GridHelper(...BvhAnsicht.GITTER));
        this.szene.add(new THREE.AmbientLight(0x404040, 2));
        const licht = new THREE.DirectionalLight(0xffffff, 1);
        licht.position.set(100, 200, 100);
        this.szene.add(licht);

        this.kamera = new THREE.PerspectiveCamera(
            BvhAnsicht.SICHTFELD, breite / hoehe, BvhAnsicht.NAH, BvhAnsicht.FERN);
        this.kameraSetzen();

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(breite, hoehe);
        this.behaelter.appendChild(this.renderer.domElement);

        this.figur = new THREE.Group();
        this.szene.add(this.figur);
    }

    /** Kamera aus den Kugelkoordinaten setzen. */
    kameraSetzen() {
        const { theta, phi, abstand } = this.kugel;
        this.kamera.position.set(
            abstand * Math.sin(phi) * Math.sin(theta),
            abstand * Math.cos(phi),
            abstand * Math.sin(phi) * Math.cos(theta));
        this.kamera.lookAt(...BvhAnsicht.BLICKPUNKT);
    }

    // ------------------------------------------------------------------- Maus

    _maussteuerung() {
        const flaeche = this.renderer.domElement;
        flaeche.addEventListener('mousedown', ereignis => {
            this.zieht = true;
            this.letzteMaus = { x: ereignis.clientX, y: ereignis.clientY };
        });
        flaeche.addEventListener('mousemove', ereignis => this.drehen(ereignis));
        // Loslassen und Verlassen beenden das Ziehen — sonst dreht die Kamera
        // weiter, wenn die Maus außerhalb losgelassen wird.
        flaeche.addEventListener('mouseup', () => { this.zieht = false; });
        flaeche.addEventListener('mouseleave', () => { this.zieht = false; });
        flaeche.addEventListener('wheel', ereignis => this.zoomen(ereignis));
    }

    drehen(ereignis) {
        if (!this.zieht) return;
        const dx = ereignis.clientX - this.letzteMaus.x;
        const dy = ereignis.clientY - this.letzteMaus.y;
        this.kugel.theta += dx * BvhAnsicht.DREH_SCHRITT;
        // Phi begrenzen, sonst klappt die Kamera über den Pol.
        this.kugel.phi = Math.max(0.1, Math.min(
            Math.PI - 0.1, this.kugel.phi + dy * BvhAnsicht.DREH_SCHRITT));
        this.letzteMaus = { x: ereignis.clientX, y: ereignis.clientY };
        this.kameraSetzen();
    }

    zoomen(ereignis) {
        ereignis.preventDefault();
        this.kugel.abstand = Math.max(BvhAnsicht.ABSTAND_MIN, Math.min(
            BvhAnsicht.ABSTAND_MAX,
            this.kugel.abstand + ereignis.deltaY * BvhAnsicht.ZOOM_SCHRITT));
        this.kameraSetzen();
    }

    // -------------------------------------------------------------------- BVH

    _anzeige() {
        this.behaelter.classList.add('bvh-ansicht');
        this.anzeige = document.createElement('div');
        this.anzeige.className = 'bvh-ansicht-info';
        this.anzeige.textContent = 'BVH wird geladen …';
        this.behaelter.appendChild(this.anzeige);
    }

    /**
     * Bildzahl aus dem Kopf der BVH lesen. Liegt die Datei nur auf der Platte
     * und nicht unter einer Adresse, wird das gemeldet — die Ersatzfigur kommt
     * in beiden Fällen.
     */
    async bvhLesen(adresse) {
        try {
            const antwort = await fetch(adresse);
            if (!antwort.ok) throw new Error('nicht abrufbar');
            this.anzeige.textContent = `BVH geladen: ${
                BvhAnsicht.bilder(await antwort.text())} Bilder`;
        } catch (fehler) {
            this.anzeige.textContent = 'BVH liegt auf der Platte '
                                       + '(nicht über HTTP abrufbar)';
        }
        Ersatzskelett.zeichnen(this.figur);
    }

    /** Bildzahl aus dem BVH-Text, oder 0. */
    static bilder(text) {
        const zeilen = text.split('\n');
        const start = zeilen.findIndex(zeile => zeile.trim() === 'MOTION');
        if (start < 0) return 0;
        const treffer = (zeilen[start + 1] || '').match(/Frames:\s*(\d+)/);
        return treffer ? parseInt(treffer[1], 10) : 0;
    }

    // ----------------------------------------------------------------- Bilder

    schleife() {
        const takt = () => {
            requestAnimationFrame(takt);
            this.renderer.render(this.szene, this.kamera);
        };
        requestAnimationFrame(takt);
    }

    groesseAnpassen() {
        const [breite, hoehe] = this.masse();
        this.kamera.aspect = breite / hoehe;
        this.kamera.updateProjectionMatrix();
        this.renderer.setSize(breite, hoehe);
    }
}

/** Name, den die Auftragsseite aufruft. */
function initBVHViewer(behaelterId, bvhAdresse) {
    return new BvhAnsicht(behaelterId).starten(bvhAdresse);
}
