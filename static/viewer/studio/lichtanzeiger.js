import * as THREE from 'three';

/**
 * Lichtanzeiger — die sichtbare Form eines Lichts in der Szene.
 *
 * Herausgelöst aus `spur_lichter.js` (321 Zeilen). Zwei Dinge werden gezeigt:
 *
 *     Helferlinien   Three.js-Drahtgitter (SpotLightHelper & Co.) — Vorgabe AUS
 *     Lichtform      eine halbdurchsichtige Form am Lichtort — Vorgabe AN
 *
 * FORM JE LICHTART (Spitze immer am Licht, Form zeigt IN die Szene)
 * ================================================================
 *     Spot         Kegel, Radius aus `light.angle` (breiter Winkel = breiter Kegel)
 *     Directional  Zylinder (parallele Strahlen)
 *     Point        Kugel (strahlt in alle Richtungen)
 *     Ambient      flaches Rechteck (ungerichtet)
 *
 * WARUM DER KEGEL NEU GEBAUT WIRD
 * ===============================
 * Der Öffnungswinkel steckt in der GEOMETRIE, nicht in einer Transformation.
 * Ändert der Nutzer ihn am Regler, muss die Geometrie neu entstehen — und die
 * alte weg (`dispose`), sonst wächst der Grafikspeicher mit jedem Reglerzug.
 */
export class Lichtanzeiger {

    /** Höhe der Form in Metern — Kegel und Zylinder. */
    static HOEHE = 0.6;
    /** Farbe der Helferlinien. */
    static HELFERFARBE = 0xffc107;
    static KEGELSEGMENTE = 24;
    static MINDESTRADIUS = 0.05;
    static HOECHSTRADIUS = 1.0;
    static VORGABEWINKEL = Math.PI / 6;

    /** `spot` | `directional` | `point` | `ambient` — nie leer. */
    static art(licht) {
        if (!licht) return 'spot';
        if (licht.isSpotLight) return 'spot';
        if (licht.isDirectionalLight) return 'directional';
        if (licht.isPointLight) return 'point';
        if (licht.isAmbientLight) return 'ambient';
        return 'spot';
    }

    /** Die halbdurchsichtige Form — `null` bei unbekannter Lichtart. */
    static form(licht) {
        const geometrie = Lichtanzeiger._geometrie(licht);
        if (!geometrie) return null;
        const netz = new THREE.Mesh(geometrie, new THREE.MeshBasicMaterial({
            color: licht.color.clone(), transparent: true, opacity: 0.45,
            side: THREE.DoubleSide, depthWrite: false,
        }));
        netz._lightShapeKind = Lichtanzeiger.art(licht);
        netz._lastAngle = licht.angle ?? null;
        return netz;
    }

    static _geometrie(licht) {
        const hoehe = Lichtanzeiger.HOEHE;
        if (licht.isSpotLight) return Lichtanzeiger._kegel(licht.angle);
        if (licht.isDirectionalLight) {
            const geometrie = new THREE.CylinderGeometry(0.08, 0.08, hoehe, 16, 1, true);
            geometrie.translate(0, -hoehe / 2, 0);
            return geometrie;
        }
        if (licht.isPointLight) return new THREE.SphereGeometry(0.12, 20, 14);
        if (licht.isAmbientLight) {
            const geometrie = new THREE.PlaneGeometry(0.5, 0.3);
            geometrie.rotateX(-Math.PI / 2);            // waagerecht
            return geometrie;
        }
        return null;
    }

    static _kegel(winkel) {
        const hoehe = Lichtanzeiger.HOEHE;
        const radius = Math.min(Math.max(
            hoehe * Math.tan(winkel ?? Lichtanzeiger.VORGABEWINKEL),
            Lichtanzeiger.MINDESTRADIUS), Lichtanzeiger.HOECHSTRADIUS);
        const geometrie = new THREE.ConeGeometry(radius, hoehe,
                                                Lichtanzeiger.KEGELSEGMENTE, 1, true);
        geometrie.translate(0, -hoehe / 2, 0);          // Spitze zum Ursprung
        return geometrie;
    }

    // --------------------------------------------------------------- Helferbund

    /**
     * Gruppe mit Helferlinien und Form — mit `update()`.
     *
     * Die Feldnamen `spotHelper` und `originCone` bleiben, weil mehrere Module
     * sie lesen (`tracks.js`, `eigenschaften/licht.js`, `theatre_lichtspuren.js`).
     */
    static helfer(licht) {
        if (!licht) return null;
        const gruppe = new THREE.Group();
        const linien = Lichtanzeiger._linien(licht);
        if (linien) {
            linien.visible = false;                     // Vorgabe: Linien aus
            gruppe.add(linien);
        }
        const form = Lichtanzeiger.form(licht);
        if (form) {
            form.visible = true;                        // Vorgabe: Form an
            gruppe.add(form);
        }
        gruppe.spotHelper = linien;
        gruppe.originCone = form;
        gruppe.update = () => Lichtanzeiger.nachziehen(licht, linien, form);
        gruppe.update();
        return gruppe;
    }

    static _linien(licht) {
        if (licht.isSpotLight) {
            return new THREE.SpotLightHelper(licht, Lichtanzeiger.HELFERFARBE);
        }
        if (licht.isDirectionalLight) {
            return new THREE.DirectionalLightHelper(licht, 0.6,
                                                    Lichtanzeiger.HELFERFARBE);
        }
        if (licht.isPointLight) {
            return new THREE.PointLightHelper(licht, 0.12,
                                              Lichtanzeiger.HELFERFARBE);
        }
        return null;    // Ambient hat keinen Drahtgitter-Helfer
    }

    /** Form an Ort, Richtung, Winkel und Farbe des Lichts anpassen. */
    static nachziehen(licht, linien, form) {
        linien?.update?.();
        if (!form) return;
        form.position.copy(licht.position);
        Lichtanzeiger._ausrichten(licht, form);
        if (licht.isSpotLight && form._lastAngle !== licht.angle) {
            form._lastAngle = licht.angle;
            form.geometry.dispose();                    // sonst waechst der VRAM
            form.geometry = Lichtanzeiger._kegel(licht.angle);
        }
        form.material.color.copy(licht.color);
    }

    static _ausrichten(licht, form) {
        const gerichtet = licht.isSpotLight || licht.isDirectionalLight;
        if (licht.target && gerichtet) {
            const richtung = new THREE.Vector3()
                .subVectors(licht.target.position, licht.position);
            if (richtung.lengthSq() > 1e-6) {
                richtung.normalize();
                // Die lokale -Y-Achse der Form zeigt zum Ziel.
                form.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0),
                                                   richtung);
            }
            return;
        }
        if (licht.isAmbientLight) {
            // Etwas anheben, damit das Rechteck nicht im Boden liegt.
            form.position.set(licht.position.x, (licht.position.y || 0) + 0.05,
                              licht.position.z);
        }
        form.quaternion.identity();
    }
}
