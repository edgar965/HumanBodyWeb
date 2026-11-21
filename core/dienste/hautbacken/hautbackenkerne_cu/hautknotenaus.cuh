// hautknotenaus.cuh — die `extern "C"`-Eingänge der Knotenkerne (`hautknotenkern.cuh`); Argumente nach dem Strom wie die Kerne, Felder als Zeiger.
#pragma once
#include "hautknotenkern.cuh"

namespace hb {

#define HB_LAUF(KERN, ...)                                              \
    if (n > 0)                                                          \
        KERN<<<HB_GITTER(n)>>>(n, __VA_ARGS__);                         \
    HB_ENDE;

typedef const float* F;
typedef float* FA;

HB_EXPORT hb_farbattribut(void* s, int n, F val, F dx, F dy, int modus, float breite, FA farbe, FA alpha, FA fac) { HB_LAUF(k_farbattribut, val, dx, dy, modus, breite, farbe, alpha, fac) }
HB_EXPORT hb_bild_trennen(void* s, int n, F r, FA farbe, FA alpha) { HB_LAUF(k_bild_trennen, r, farbe, alpha) }
HB_EXPORT hb_uv_koordinate(void* s, int n, F val, F dx, F dy, int modus, float breite, FA aus) { HB_LAUF(k_uv_koordinate, val, dx, dy, modus, breite, aus) }
HB_EXPORT hb_bereich_zahl(void* s, int n, F w, F a, F b, F c, F d, F st, int art, int klemme, FA aus) { HB_LAUF(k_bereich_zahl, w, a, b, c, d, st, art, klemme, aus) }
HB_EXPORT hb_bereich_vektor(void* s, int n, F w, F a, F b, F c, F d, F st, int art, int klemme, FA aus) { HB_LAUF(k_bereich_vektor, w, a, b, c, d, st, art, klemme, aus) }
HB_EXPORT hb_klemmen(void* s, int n, F w, F lo, F hi, int bereich, FA aus) { HB_LAUF(k_klemmen, w, lo, hi, bereich, aus) }
HB_EXPORT hb_bump(void* s, int n, F hc, F hx, F hy, F nein, F dpx, F dpy, F staerke, F abstand, float breite, int umkehren, FA aus)
{
    HB_LAUF(k_bump, hc, hx, hy, nein, dpx, dpy, staerke, abstand, breite, umkehren, aus)
}
HB_EXPORT hb_hsv(void* s, int n, F farbe, F h, F sat, F v, F fac, FA aus) { HB_LAUF(k_hsv, farbe, h, sat, v, fac, aus) }
HB_EXPORT hb_helligkeit(void* s, int n, F farbe, F hell, F kontrast, FA aus) { HB_LAUF(k_helligkeit, farbe, hell, kontrast, aus) }
HB_EXPORT hb_gamma(void* s, int n, F farbe, F gamma, FA aus) { HB_LAUF(k_gamma, farbe, gamma, aus) }
HB_EXPORT hb_invertieren(void* s, int n, F farbe, F fac, FA aus) { HB_LAUF(k_invertieren, farbe, fac, aus) }
HB_EXPORT hb_abbilden(void* s, int n, F v, F o, F d, F sk, int art, FA aus) { HB_LAUF(k_abbilden, v, o, d, sk, art, aus) }
HB_EXPORT hb_mathe(void* s, int n, F a, F b, F c, int typ, int klemme, FA aus) { HB_LAUF(k_mathe, a, b, c, typ, klemme, aus) }
HB_EXPORT hb_vektor_mathe(void* s, int n, F a, F b, F c, F skala, int typ, FA v, FA w) { HB_LAUF(k_vektor_mathe, a, b, c, skala, typ, v, w) }
HB_EXPORT hb_mix_farbe(void* s, int n, F a, F b, F fac, int typ, int klemme, int klemme_e, FA aus) { HB_LAUF(k_mix_farbe, a, b, fac, typ, klemme, klemme_e, aus) }
HB_EXPORT hb_mix_alt(void* s, int n, F a, F b, F fac, int typ, int klemme, FA aus) { HB_LAUF(k_mix_alt, a, b, fac, typ, klemme, aus) }
HB_EXPORT hb_mix_zahl(void* s, int n, F a, F b, F fac, int klemme, FA aus) { HB_LAUF(k_mix_zahl, a, b, fac, klemme, aus) }
HB_EXPORT hb_mix_vektor(void* s, int n, F a, F b, F fac, int klemme, FA aus) { HB_LAUF(k_mix_vektor, a, b, fac, klemme, aus) }
HB_EXPORT hb_mix_vektor_ungleich(void* s, int n, F a, F b, F fac, int klemme, FA aus) { HB_LAUF(k_mix_vektor_ungleich, a, b, fac, klemme, aus) }
HB_EXPORT hb_normalkarte(void* s, int n, F farbe, F staerke, F tang, F vorz, F normale, F ng, const int* glatt, F n_shader, const int* rueck, int dx_umkehren,
                         FA aus)
{
    HB_LAUF(k_normalkarte, farbe, staerke, tang, vorz, normale, ng, glatt, n_shader, rueck, dx_umkehren, aus)
}
HB_EXPORT hb_normalkarte_fest(void* s, int n, F farbe, F staerke, F n_shader, const int* rueck, int blender, FA aus)
{
    HB_LAUF(k_normalkarte_fest, farbe, staerke, n_shader, rueck, blender, aus)
}
HB_EXPORT hb_rampe(void* s, int n, F fac, F tab, int interp, int groesse, FA farbe, FA alpha) { HB_LAUF(k_rampe, fac, tab, interp, groesse, farbe, alpha) }
HB_EXPORT hb_kurven(void* s, int n, F fac, F farbe, F tab, float min_x, float max_x, int extra, int groesse, FA aus)
{
    HB_LAUF(k_kurven, fac, farbe, tab, min_x, max_x, extra, groesse, aus)
}
HB_EXPORT hb_kurve(void* s, int n, F fac, F wert, F tab, float min_x, float max_x, int extra, int groesse, FA aus)
{
    HB_LAUF(k_kurve, fac, wert, tab, min_x, max_x, extra, groesse, aus)
}
HB_EXPORT hb_farbe_trennen(void* s, int n, F farbe, int modus, FA r, FA g, FA b) { HB_LAUF(k_farbe_trennen, farbe, modus, r, g, b) }
HB_EXPORT hb_farbe_zusammen(void* s, int n, F r, F g, F b, int modus, FA aus) { HB_LAUF(k_farbe_zusammen, r, g, b, modus, aus) }
HB_EXPORT hb_trennen_xyz(void* s, int n, F v, FA x, FA y, FA z) { HB_LAUF(k_trennen_xyz, v, x, y, z) }
HB_EXPORT hb_zusammen_xyz(void* s, int n, F x, F y, F z, FA aus) { HB_LAUF(k_zusammen_xyz, x, y, z, aus) }

}  // namespace hb
