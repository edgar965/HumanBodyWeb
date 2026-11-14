/**
 * Dqhaut — Genesis-Figuren häuten wie Daz: halb linear, halb Dual Quaternion (12.11.2026).
 *
 * ANLASS: An Olesia1 im Spagat (Bild 51, hoher Kick) lag ein verschmierter Streifen im Schritt der Jeans, mit und ohne Hautbindung; Edgar:
 * „das problem ist wohl dass die Animation die Knochen verstellt“. Gelesen in `Genesis9.dsf` (Daz-Bibliothek, `ProjektTemp/_wegwerf/genesis_zuerst/
 * skinart_probe.py`): `binding_mode: General`, `general_map_mode: DualQuat`, `blend_mode: BlendLinearDualQuat`, `blend_weights` an allen 25.182
 * Käfigpunkten 0,5. Three.js häutet nur linear (`skinning_vertex`): Bei starker Beugung fällt das Volumen am Gelenk ein, und die Fläche zwischen
 * zwei Knochen wird zusammengeschoben oder gezerrt. Daz mischt je Punkt halb die lineare, halb die Dual-Quaternion-Lage.
 *
 * WIE: Die Chunks `skinbase_vertex`, `skinnormal_vertex`, `skinning_vertex` bekommen einen Zweig unter `#ifdef DQ_MISCH`; ohne das Define rechnet jeder
 * Shader wie vorher (andere Figurarten bleiben linear). `einschalten(netz)` setzt das Define an den Materialien eines Netzes und ersetzt
 * `applyBoneTransform` des Netzes, damit jede Messung auf der CPU (Kleidungsprobe, Modell-Check, Bindungsprobe, Treffer) die gezeichnete Lage sieht.
 * Die Körperlage der Hautbindung (`koerperlage.js`) setzt das Define an ihrem Material, wenn der Körper es trägt — Stoff und Körper bleiben im
 * selben Raum.
 *
 * Die Formeln sind Blenders (`source/blender/blenlib/intern/math_rotation.c`, v3.6.0: `mat4_to_dquat` Dualteil, `add_weighted_dq_dq` mit Vorzeichen
 * gegen die Summe, `mul_v3m3_dq` mit Division durch |q|²), gelesen am 12.11.2026 (`ProjektTemp/_wegwerf/dqs/math_rotation.c`). Den Anteil Skalierung
 * (`dq->scale`) rechnet das hier nicht: die Knochenmatrizen einer Animation sind starr (Drehung und Verschiebung). Die Quaternion aus der Matrix wie
 * three `Quaternion.setFromRotationMatrix`. Gemischt werden die LAGEN (0,5 · linear + 0,5 · DQ), wie Daz es mit `BlendLinearDualQuat` mischt, ist
 * nicht nachgelesen (Daz Studio ist nicht offen).
 *
 * Nicht hier: der Stoff-Worker (`stoffarbeiter.js`) häutet die festgehaltenen Käfigpunkte weiter linear; der GLB-Export kennt nur lineare Häutung.
 */
import * as THREE from 'three';

export class Dqhaut {

    /** Anteil der Dual-Quaternion-Lage: Daz' `blend_weights` von Genesis 9, an allen 25.182 Käfigpunkten 0,5 (`skinart_probe.py`, 12.11.2026). */
    static MISCH = 0.5;

    static PARS = `
#if defined( USE_SKINNING ) && defined( DQ_MISCH )
vec4 dqDrehung( mat4 m ) {
	float m11 = m[0][0], m12 = m[1][0], m13 = m[2][0];
	float m21 = m[0][1], m22 = m[1][1], m23 = m[2][1];
	float m31 = m[0][2], m32 = m[1][2], m33 = m[2][2];
	float spur = m11 + m22 + m33;
	if ( spur > 0.0 ) {
		float s = 0.5 / sqrt( spur + 1.0 );
		return vec4( 0.25 / s, ( m32 - m23 ) * s, ( m13 - m31 ) * s, ( m21 - m12 ) * s );
	} else if ( m11 > m22 && m11 > m33 ) {
		float s = 2.0 * sqrt( 1.0 + m11 - m22 - m33 );
		return vec4( ( m32 - m23 ) / s, 0.25 * s, ( m12 + m21 ) / s, ( m13 + m31 ) / s );
	} else if ( m22 > m33 ) {
		float s = 2.0 * sqrt( 1.0 + m22 - m11 - m33 );
		return vec4( ( m13 - m31 ) / s, ( m12 + m21 ) / s, 0.25 * s, ( m23 + m32 ) / s );
	}
	float s = 2.0 * sqrt( 1.0 + m33 - m11 - m22 );
	return vec4( ( m21 - m12 ) / s, ( m13 + m31 ) / s, ( m23 + m32 ) / s, 0.25 * s );
}
void dqDazu( inout vec4 sq, inout vec4 sd, mat4 m, float w ) {
	if ( w == 0.0 ) return;
	vec4 q = dqDrehung( m );
	vec3 t = m[ 3 ].xyz;
	vec4 d = vec4( -0.5 * ( t.x * q.y + t.y * q.z + t.z * q.w ),
	                0.5 * ( t.x * q.x + t.y * q.w - t.z * q.z ),
	                0.5 * ( -t.x * q.w + t.y * q.x + t.z * q.y ),
	                0.5 * ( t.x * q.z - t.y * q.y + t.z * q.x ) );
	if ( dot( q, sq ) < 0.0 ) w = -w;
	sq += w * q;
	sd += w * d;
}
mat3 dqMatrix( vec4 sq ) {
	float w = sq.x, x = sq.y, y = sq.z, z = sq.w;
	float l = dot( sq, sq );
	l = l > 0.0 ? 1.0 / l : 0.0;
	return l * mat3( w * w + x * x - y * y - z * z, 2.0 * ( x * y + w * z ), 2.0 * ( x * z - w * y ),
	                 2.0 * ( x * y - w * z ), w * w + y * y - x * x - z * z, 2.0 * ( y * z + w * x ),
	                 2.0 * ( x * z + w * y ), 2.0 * ( y * z - w * x ), w * w + z * z - x * x - y * y );
}
vec3 dqPunkt( vec4 sq, vec4 sd, vec3 r ) {
	float w = sq.x, x = sq.y, y = sq.z, z = sq.w;
	float l = dot( sq, sq );
	l = l > 0.0 ? 1.0 / l : 0.0;
	vec3 t = 2.0 * vec3( -sd.x * x + w * sd.y - sd.z * z + y * sd.w,
	                     -sd.x * y + sd.y * z - x * sd.w + w * sd.z,
	                     -sd.x * z + x * sd.z + w * sd.w - sd.y * y );
	return dqMatrix( sq ) * r + t * l;
}
#endif
`;

    static BASIS = `
#if defined( USE_SKINNING ) && defined( DQ_MISCH )
	vec4 dqQ = vec4( 0.0 ), dqD = vec4( 0.0 );
	dqDazu( dqQ, dqD, boneMatX, skinWeight.x );
	dqDazu( dqQ, dqD, boneMatY, skinWeight.y );
	dqDazu( dqQ, dqD, boneMatZ, skinWeight.z );
	dqDazu( dqQ, dqD, boneMatW, skinWeight.w );
#endif
`;

    static NORMALE_VOR = `
#if defined( USE_SKINNING ) && defined( DQ_MISCH )
	vec3 dqNormaleVorher = objectNormal;
#endif
`;

    static NORMALE_NACH = `
#if defined( USE_SKINNING ) && defined( DQ_MISCH )
	objectNormal = mix( objectNormal, mat3( bindMatrixInverse ) * ( dqMatrix( dqQ ) * ( mat3( bindMatrix ) * dqNormaleVorher ) ), float( DQ_MISCH ) );
#endif
`;

    static LAGE_NACH = `
#if defined( USE_SKINNING ) && defined( DQ_MISCH )
	transformed = mix( transformed, ( bindMatrixInverse * vec4( dqPunkt( dqQ, dqD, skinVertex.xyz ), 1.0 ) ).xyz, float( DQ_MISCH ) );
#endif
`;

    static _eingehaengt = false;

    /** Die Chunks einmal je Seite erweitern (vor dem ersten Übersetzen eines Shaders mit Häutung — beim Laden des Moduls). */
    static chunksErweitern() {
        if (Dqhaut._eingehaengt) return;
        const C = THREE.ShaderChunk;
        if (!C.skinning_pars_vertex.includes('dqDrehung')) C.skinning_pars_vertex += Dqhaut.PARS;
        if (!C.skinbase_vertex.includes('dqDazu')) C.skinbase_vertex += Dqhaut.BASIS;
        if (!C.skinnormal_vertex.includes('dqNormaleVorher')) C.skinnormal_vertex = Dqhaut.NORMALE_VOR + C.skinnormal_vertex + Dqhaut.NORMALE_NACH;
        if (!C.skinning_vertex.includes('dqPunkt')) {
            // `skinVertex` gibt es nur im Zweig von `skinning_vertex` — die Mischung gehört an sein Ende, vor das schließende `#endif`.
            const ende = C.skinning_vertex.lastIndexOf('#endif');
            C.skinning_vertex = C.skinning_vertex.slice(0, ende) + Dqhaut.LAGE_NACH + C.skinning_vertex.slice(ende);
        }
        Dqhaut._eingehaengt = true;
    }

    /** Ein Netz (gehäutet) wie Daz häuten: Define an jedem Material, CPU-Lage über `knochenlage`. */
    static einschalten(netz, misch = Dqhaut.MISCH) {
        if (!netz?.isSkinnedMesh || !(misch >= 0)) return false;          // 0 = rein linear (Gegenprobe: `__dqhaut.figur(inst, 0)`)
        Dqhaut.chunksErweitern();
        const wert = String(misch);
        for (const mat of Array.isArray(netz.material) ? netz.material : [netz.material]) {
            if (!mat || mat.defines?.DQ_MISCH === wert) continue;
            mat.defines = { ...(mat.defines || {}), DQ_MISCH: wert };
            mat.needsUpdate = true;
        }
        netz.userData.dqMisch = misch;
        netz.applyBoneTransform = function (index, vector) { return Dqhaut.knochenlage(this, index, vector); };
        return true;
    }

    /**
     * Alle gehäuteten Netze einer Genesis-Figur am Skelett des Körpers (Körper, Anhänge, Stücke, später gebundene GarmentCode-Stücke): sonst
     * hinge der Stoff linear und die Haut gemischt, und an jedem gebeugten Gelenk stäche die Haut durch. Billig genug für jedes Bild: gerechnet
     * wird nur, wenn die Gruppe neue Kinder hat (`Genesis9gelenke.takt`) oder ein Netz eingehängt wird (`Genesis9Modell._einhaengen`).
     */
    static figur(inst, misch = Dqhaut.MISCH) {
        const skelett = inst?.bodyMesh?.skeleton;
        if (!skelett || !inst.group) return 0;
        let n = 0;
        inst.group.traverse((o) => {
            if (o.isSkinnedMesh && o.skeleton === skelett && o.userData?.dqMisch !== misch && Dqhaut.einschalten(o, misch)) n++;
        });
        inst._dqKinder = inst.group.children.length;
        return n;
    }

    /** Das Define für ein eigenes Material (Körperlage der Hautbindung), wenn der Körper so gehäutet wird. */
    static material(mat, koerper) {
        const misch = koerper?.userData?.dqMisch;
        if (!mat || misch == null || mat.defines?.DQ_MISCH === String(misch)) return;
        Dqhaut.chunksErweitern();
        mat.defines = { ...(mat.defines || {}), DQ_MISCH: String(misch) };
        mat.needsUpdate = true;
    }

    static _i = new THREE.Vector4();
    static _w = new THREE.Vector4();
    static _m = new THREE.Matrix4();
    static _basis = new THREE.Vector3();
    static _lin = new THREE.Vector3();
    static _t = new THREE.Vector3();

    /** Wie `SkinnedMesh.applyBoneTransform` (three 0.170), dazu die Dual-Quaternion-Lage nach Blender, gemischt mit `userData.dqMisch`. */
    static knochenlage(netz, index, vector) {
        const D = Dqhaut, skelett = netz.skeleton, geo = netz.geometry;
        D._i.fromBufferAttribute(geo.attributes.skinIndex, index);
        D._w.fromBufferAttribute(geo.attributes.skinWeight, index);
        D._basis.copy(vector).applyMatrix4(netz.bindMatrix);
        D._lin.set(0, 0, 0);
        const sq = [0, 0, 0, 0], sd = [0, 0, 0, 0];
        for (let k = 0; k < 4; k++) {
            let w = D._w.getComponent(k);
            if (w === 0) continue;
            const b = D._i.getComponent(k);
            D._m.multiplyMatrices(skelett.bones[b].matrixWorld, skelett.boneInverses[b]);
            D._lin.addScaledVector(D._t.copy(D._basis).applyMatrix4(D._m), w);
            const q = D.drehung(D._m.elements), t = [D._m.elements[12], D._m.elements[13], D._m.elements[14]];
            const d = [-0.5 * (t[0] * q[1] + t[1] * q[2] + t[2] * q[3]), 0.5 * (t[0] * q[0] + t[1] * q[3] - t[2] * q[2]),
                       0.5 * (-t[0] * q[3] + t[1] * q[0] + t[2] * q[1]), 0.5 * (t[0] * q[2] - t[1] * q[1] + t[2] * q[0])];
            if (q[0] * sq[0] + q[1] * sq[1] + q[2] * sq[2] + q[3] * sq[3] < 0) w = -w;
            for (let j = 0; j < 4; j++) { sq[j] += w * q[j]; sd[j] += w * d[j]; }
        }
        const [w, x, y, z] = sq, l2 = w * w + x * x + y * y + z * z, l = l2 > 0 ? 1 / l2 : 0;
        const r = D._basis;
        const px = (w * w + x * x - y * y - z * z) * r.x + 2 * (x * y - w * z) * r.y + 2 * (x * z + w * y) * r.z;
        const py = 2 * (x * y + w * z) * r.x + (w * w + y * y - x * x - z * z) * r.y + 2 * (y * z - w * x) * r.z;
        const pz = 2 * (x * z - w * y) * r.x + 2 * (y * z + w * x) * r.y + (w * w + z * z - x * x - y * y) * r.z;
        const tx = 2 * (-sd[0] * x + w * sd[1] - sd[2] * z + y * sd[3]);
        const ty = 2 * (-sd[0] * y + sd[1] * z - x * sd[3] + w * sd[2]);
        const tz = 2 * (-sd[0] * z + x * sd[2] + w * sd[3] - sd[1] * y);
        const a = netz.userData.dqMisch || 0;
        vector.set((1 - a) * D._lin.x + a * (px + tx) * l, (1 - a) * D._lin.y + a * (py + ty) * l, (1 - a) * D._lin.z + a * (pz + tz) * l);
        return vector.applyMatrix4(netz.bindMatrixInverse);
    }

    /** Je Knochen die Dual Quaternion (q: w, x, y, z; d: Dualteil nach Blender) aus 16er-Blöcken (`Stoffhaut.matrizen`) → Float64Array (8 je Knochen). */
    static tafel(M, anzahl) {
        const aus = new Float64Array(8 * anzahl);
        for (let b = 0; b < anzahl; b++) {
            const e = M.subarray(16 * b, 16 * b + 16), q = Dqhaut.drehung(e), t0 = e[12], t1 = e[13], t2 = e[14];
            aus.set([q[0], q[1], q[2], q[3],
                -0.5 * (t0 * q[1] + t1 * q[2] + t2 * q[3]), 0.5 * (t0 * q[0] + t1 * q[3] - t2 * q[2]),
                0.5 * (-t0 * q[3] + t1 * q[0] + t2 * q[1]), 0.5 * (t0 * q[2] - t1 * q[1] + t2 * q[0])], 8 * b);
        }
        return aus;
    }

    /** Punkt (x, y, z) mit den Einflüssen `index`/`gewicht` ab Stelle 4·i über die Tafel → `aus` [x, y, z] (Dual-Quaternion-Lage, ohne Mischung). */
    static punkt(Q, index, gewicht, i, x, y, z, aus) {
        let w = 0, qx = 0, qy = 0, qz = 0, d0 = 0, d1 = 0, d2 = 0, d3 = 0;
        for (let k = 0; k < 4; k++) {
            let g = gewicht[4 * i + k];
            if (g === 0) continue;
            const o = 8 * index[4 * i + k];
            if (Q[o] * w + Q[o + 1] * qx + Q[o + 2] * qy + Q[o + 3] * qz < 0) g = -g;
            w += g * Q[o]; qx += g * Q[o + 1]; qy += g * Q[o + 2]; qz += g * Q[o + 3];
            d0 += g * Q[o + 4]; d1 += g * Q[o + 5]; d2 += g * Q[o + 6]; d3 += g * Q[o + 7];
        }
        const l2 = w * w + qx * qx + qy * qy + qz * qz, l = l2 > 0 ? 1 / l2 : 0;
        aus[0] = ((w * w + qx * qx - qy * qy - qz * qz) * x + 2 * (qx * qy - w * qz) * y + 2 * (qx * qz + w * qy) * z
                  + 2 * (-d0 * qx + w * d1 - d2 * qz + qy * d3)) * l;
        aus[1] = (2 * (qx * qy + w * qz) * x + (w * w + qy * qy - qx * qx - qz * qz) * y + 2 * (qy * qz - w * qx) * z
                  + 2 * (-d0 * qy + d1 * qz - qx * d3 + w * d2)) * l;
        aus[2] = (2 * (qx * qz - w * qy) * x + 2 * (qy * qz + w * qx) * y + (w * w + qz * qz - qx * qx - qy * qy) * z
                  + 2 * (-d0 * qz + qx * d2 + w * d3 - d1 * qy)) * l;
        return aus;
    }

    /** Quaternion [w, x, y, z] aus den Elementen einer Matrix4 (spaltenweise), wie three `Quaternion.setFromRotationMatrix`. */
    static drehung(e) {
        const m11 = e[0], m12 = e[4], m13 = e[8], m21 = e[1], m22 = e[5], m23 = e[9], m31 = e[2], m32 = e[6], m33 = e[10];
        const spur = m11 + m22 + m33;
        if (spur > 0) {
            const s = 0.5 / Math.sqrt(spur + 1);
            return [0.25 / s, (m32 - m23) * s, (m13 - m31) * s, (m21 - m12) * s];
        }
        if (m11 > m22 && m11 > m33) {
            const s = 2 * Math.sqrt(1 + m11 - m22 - m33);
            return [(m32 - m23) / s, 0.25 * s, (m12 + m21) / s, (m13 + m31) / s];
        }
        if (m22 > m33) {
            const s = 2 * Math.sqrt(1 + m22 - m11 - m33);
            return [(m13 - m31) / s, (m12 + m21) / s, 0.25 * s, (m23 + m32) / s];
        }
        const s = 2 * Math.sqrt(1 + m33 - m11 - m22);
        return [(m21 - m12) / s, (m13 + m31) / s, (m23 + m32) / s, 0.25 * s];
    }
}

Dqhaut.chunksErweitern();
if (typeof window !== 'undefined') window.__dqhaut = Dqhaut;      // für Proben im Tab (Gegenprobe linear: `__dqhaut.figur(inst, 0)`)
