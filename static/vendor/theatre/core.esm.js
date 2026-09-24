import { r as D, c as Pt } from "./index-BiE5ULEf.js";
var Je = { exports: {} };
Je.exports;
var Ja;
function Jv() {
  return Ja || (Ja = 1, (function(W, Z) {
    var $a = Object.create, Ee = Object.defineProperty, Ya = Object.defineProperties, Za = Object.getOwnPropertyDescriptor, Qa = Object.getOwnPropertyDescriptors, Cr = Object.getOwnPropertyNames, Ir = Object.getOwnPropertySymbols, ei = Object.getPrototypeOf, Dr = Object.prototype.hasOwnProperty, ti = Object.prototype.propertyIsEnumerable, Tt = (e, t, r) => t in e ? Ee(e, t, { enumerable: !0, configurable: !0, writable: !0, value: r }) : e[t] = r, C = (e, t) => {
      for (var r in t || (t = {}))
        Dr.call(t, r) && Tt(e, r, t[r]);
      if (Ir)
        for (var r of Ir(t))
          ti.call(t, r) && Tt(e, r, t[r]);
      return e;
    }, J = (e, t) => Ya(e, Qa(t)), Xe = (e, t) => function() {
      return t || (0, e[Cr(e)[0]])((t = { exports: {} }).exports, t), t.exports;
    }, wt = (e, t) => {
      for (var r in t)
        Ee(e, r, { get: t[r], enumerable: !0 });
    }, xr = (e, t, r, n) => {
      if (t && typeof t == "object" || typeof t == "function")
        for (let a of Cr(t))
          !Dr.call(e, a) && a !== r && Ee(e, a, { get: () => t[a], enumerable: !(n = Za(t, a)) || n.enumerable });
      return e;
    }, $e = (e, t, r) => (r = e != null ? $a(ei(e)) : {}, xr(
      // If the importer is in node compatibility mode or this is not an ESM
      // file that has been converted to a CommonJS file using a Babel-
      // compatible transform (i.e. "__esModule" has not been set), then set
      // "default" to the CommonJS "module.exports" for node compatibility.
      !e || !e.__esModule ? Ee(r, "default", { value: e, enumerable: !0 }) : r,
      e
    )), ri = (e) => xr(Ee({}, "__esModule", { value: !0 }), e), p = (e, t, r) => (Tt(e, typeof t != "symbol" ? t + "" : t, r), r), ni = Xe({
      "../node_modules/timing-function/lib/UnitBezier.js"(e, t) {
        t.exports = (function() {
          function r(n, a, i, o) {
            this.set(n, a, i, o);
          }
          return r.prototype.set = function(n, a, i, o) {
            this._cx = 3 * n, this._bx = 3 * (i - n) - this._cx, this._ax = 1 - this._cx - this._bx, this._cy = 3 * a, this._by = 3 * (o - a) - this._cy, this._ay = 1 - this._cy - this._by;
          }, r.epsilon = 1e-6, r.prototype._sampleCurveX = function(n) {
            return ((this._ax * n + this._bx) * n + this._cx) * n;
          }, r.prototype._sampleCurveY = function(n) {
            return ((this._ay * n + this._by) * n + this._cy) * n;
          }, r.prototype._sampleCurveDerivativeX = function(n) {
            return (3 * this._ax * n + 2 * this._bx) * n + this._cx;
          }, r.prototype._solveCurveX = function(n, a) {
            var i, o, s, u, l, c;
            for (s = void 0, u = void 0, l = void 0, c = void 0, i = void 0, o = void 0, l = n, o = 0; o < 8; ) {
              if (c = this._sampleCurveX(l) - n, Math.abs(c) < a)
                return l;
              if (i = this._sampleCurveDerivativeX(l), Math.abs(i) < a)
                break;
              l = l - c / i, o++;
            }
            if (s = 0, u = 1, l = n, l < s)
              return s;
            if (l > u)
              return u;
            for (; s < u; ) {
              if (c = this._sampleCurveX(l), Math.abs(c - n) < a)
                return l;
              n > c ? s = l : u = l, l = (u - s) * 0.5 + s;
            }
            return l;
          }, r.prototype.solve = function(n, a) {
            return this._sampleCurveY(this._solveCurveX(n, a));
          }, r.prototype.solveSimple = function(n) {
            return this._sampleCurveY(this._solveCurveX(n, 1e-6));
          }, r;
        })();
      }
    }), ai = Xe({
      "../node_modules/levenshtein-edit-distance/index.js"(e, t) {
        var r, n;
        r = [], n = [];
        function a(i, o, s) {
          var u, l, c, f, d, v, h, _;
          if (i === o)
            return 0;
          if (u = i.length, l = o.length, u === 0)
            return l;
          if (l === 0)
            return u;
          for (s && (i = i.toLowerCase(), o = o.toLowerCase()), h = 0; h < u; )
            n[h] = i.charCodeAt(h), r[h] = ++h;
          for (_ = 0; _ < l; )
            for (c = o.charCodeAt(_), f = d = _++, h = -1; ++h < u; )
              v = c === n[h] ? d : d + 1, d = r[h], r[h] = f = d > f ? v > f ? f + 1 : v : v > d ? d + 1 : v;
          return f;
        }
        t.exports = a;
      }
    }), ii = Xe({
      "../node_modules/propose/propose.js"(e, t) {
        var r = ai();
        function n() {
          var a, i, o, s, u, l = 0, c = arguments[0], f = arguments[1], d = f.length, v = arguments[2];
          v && (s = v.threshold, u = v.ignoreCase), s === void 0 && (s = 0);
          for (var h = 0; h < d; ++h)
            u ? i = r(c, f[h], !0) : i = r(c, f[h]), i > c.length ? a = 1 - i / f[h].length : a = 1 - i / c.length, a > l && (l = a, o = f[h]);
          return l >= s ? o : null;
        }
        t.exports = n;
      }
    }), Er = Xe({
      "../node_modules/fast-deep-equal/index.js"(e, t) {
        t.exports = function r(n, a) {
          if (n === a)
            return !0;
          if (n && a && typeof n == "object" && typeof a == "object") {
            if (n.constructor !== a.constructor)
              return !1;
            var i, o, s;
            if (Array.isArray(n)) {
              if (i = n.length, i != a.length)
                return !1;
              for (o = i; o-- !== 0; )
                if (!r(n[o], a[o]))
                  return !1;
              return !0;
            }
            if (n.constructor === RegExp)
              return n.source === a.source && n.flags === a.flags;
            if (n.valueOf !== Object.prototype.valueOf)
              return n.valueOf() === a.valueOf();
            if (n.toString !== Object.prototype.toString)
              return n.toString() === a.toString();
            if (s = Object.keys(n), i = s.length, i !== Object.keys(a).length)
              return !1;
            for (o = i; o-- !== 0; )
              if (!Object.prototype.hasOwnProperty.call(a, s[o]))
                return !1;
            for (o = i; o-- !== 0; ) {
              var u = s[o];
              if (!r(n[u], a[u]))
                return !1;
            }
            return !0;
          }
          return n !== n && a !== a;
        };
      }
    }), Rr = {};
    wt(Rr, {
      createRafDriver: () => ir,
      getProject: () => Ka,
      notify: () => Ie,
      onChange: () => jr,
      types: () => or,
      val: () => Wa
    }), W.exports = ri(Rr);
    var Mr = {};
    wt(Mr, {
      createRafDriver: () => ir,
      getProject: () => Ka,
      notify: () => Ie,
      onChange: () => jr,
      types: () => or,
      val: () => Wa
    });
    var oi = D(), si = class {
      constructor() {
        p(this, "atom", new oi.Atom({ projects: {} }));
      }
      /**
       * We're trusting here that each project id is unique
       */
      add(e, t) {
        this.atom.setByPointer((r) => r.projects[e], t);
      }
      get(e) {
        return this.atom.get().projects[e];
      }
      has(e) {
        return !!this.get(e);
      }
    }, ui = new si(), St = ui, Br = /* @__PURE__ */ new WeakMap();
    function m(e) {
      return Br.get(e);
    }
    function Re(e, t) {
      Br.set(e, t);
    }
    var Ot = [], li = Array.isArray, X = li, ci = typeof Pt == "object" && Pt && Pt.Object === Object && Pt, Lr = ci, fi = typeof self == "object" && self && self.Object === Object && self, di = Lr || fi || Function("return this")(), H = di, pi = H.Symbol, $ = pi, Fr = Object.prototype, hi = Fr.hasOwnProperty, vi = Fr.toString, Me = $ ? $.toStringTag : void 0;
    function gi(e) {
      var t = hi.call(e, Me), r = e[Me];
      try {
        e[Me] = void 0;
        var n = !0;
      } catch {
      }
      var a = vi.call(e);
      return n && (t ? e[Me] = r : delete e[Me]), a;
    }
    var _i = gi, yi = Object.prototype, bi = yi.toString;
    function mi(e) {
      return bi.call(e);
    }
    var Pi = mi, Ti = "[object Null]", wi = "[object Undefined]", kr = $ ? $.toStringTag : void 0;
    function Si(e) {
      return e == null ? e === void 0 ? wi : Ti : kr && kr in Object(e) ? _i(e) : Pi(e);
    }
    var oe = Si;
    function Oi(e) {
      return e != null && typeof e == "object";
    }
    var Q = Oi, Ai = "[object Symbol]";
    function ji(e) {
      return typeof e == "symbol" || Q(e) && oe(e) == Ai;
    }
    var Ye = ji, Ci = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, Ii = /^\w*$/;
    function Di(e, t) {
      if (X(e))
        return !1;
      var r = typeof e;
      return r == "number" || r == "symbol" || r == "boolean" || e == null || Ye(e) ? !0 : Ii.test(e) || !Ci.test(e) || t != null && e in Object(t);
    }
    var At = Di;
    function xi(e) {
      var t = typeof e;
      return e != null && (t == "object" || t == "function");
    }
    var K = xi, Ei = "[object AsyncFunction]", Ri = "[object Function]", Mi = "[object GeneratorFunction]", Bi = "[object Proxy]";
    function Li(e) {
      if (!K(e))
        return !1;
      var t = oe(e);
      return t == Ri || t == Mi || t == Ei || t == Bi;
    }
    var Nr = Li, Fi = H["__core-js_shared__"], jt = Fi, Ur = (function() {
      var e = /[^.]+$/.exec(jt && jt.keys && jt.keys.IE_PROTO || "");
      return e ? "Symbol(src)_1." + e : "";
    })();
    function ki(e) {
      return !!Ur && Ur in e;
    }
    var Ni = ki, Ui = Function.prototype, zi = Ui.toString;
    function qi(e) {
      if (e != null) {
        try {
          return zi.call(e);
        } catch {
        }
        try {
          return e + "";
        } catch {
        }
      }
      return "";
    }
    var se = qi, Vi = /[\\^$.*+?()[\]{}|]/g, Gi = /^\[object .+?Constructor\]$/, Hi = Function.prototype, Ki = Object.prototype, Wi = Hi.toString, Ji = Ki.hasOwnProperty, Xi = RegExp(
      "^" + Wi.call(Ji).replace(Vi, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
    );
    function $i(e) {
      if (!K(e) || Ni(e))
        return !1;
      var t = Nr(e) ? Xi : Gi;
      return t.test(se(e));
    }
    var Yi = $i;
    function Zi(e, t) {
      return e == null ? void 0 : e[t];
    }
    var Qi = Zi;
    function eo(e, t) {
      var r = Qi(e, t);
      return Yi(r) ? r : void 0;
    }
    var ue = eo, to = ue(Object, "create"), Be = to;
    function ro() {
      this.__data__ = Be ? Be(null) : {}, this.size = 0;
    }
    var no = ro;
    function ao(e) {
      var t = this.has(e) && delete this.__data__[e];
      return this.size -= t ? 1 : 0, t;
    }
    var io = ao, oo = "__lodash_hash_undefined__", so = Object.prototype, uo = so.hasOwnProperty;
    function lo(e) {
      var t = this.__data__;
      if (Be) {
        var r = t[e];
        return r === oo ? void 0 : r;
      }
      return uo.call(t, e) ? t[e] : void 0;
    }
    var co = lo, fo = Object.prototype, po = fo.hasOwnProperty;
    function ho(e) {
      var t = this.__data__;
      return Be ? t[e] !== void 0 : po.call(t, e);
    }
    var vo = ho, go = "__lodash_hash_undefined__";
    function _o(e, t) {
      var r = this.__data__;
      return this.size += this.has(e) ? 0 : 1, r[e] = Be && t === void 0 ? go : t, this;
    }
    var yo = _o;
    function Te(e) {
      var t = -1, r = e == null ? 0 : e.length;
      for (this.clear(); ++t < r; ) {
        var n = e[t];
        this.set(n[0], n[1]);
      }
    }
    Te.prototype.clear = no, Te.prototype.delete = io, Te.prototype.get = co, Te.prototype.has = vo, Te.prototype.set = yo;
    var zr = Te;
    function bo() {
      this.__data__ = [], this.size = 0;
    }
    var mo = bo;
    function Po(e, t) {
      return e === t || e !== e && t !== t;
    }
    var Ct = Po;
    function To(e, t) {
      for (var r = e.length; r--; )
        if (Ct(e[r][0], t))
          return r;
      return -1;
    }
    var Ze = To, wo = Array.prototype, So = wo.splice;
    function Oo(e) {
      var t = this.__data__, r = Ze(t, e);
      if (r < 0)
        return !1;
      var n = t.length - 1;
      return r == n ? t.pop() : So.call(t, r, 1), --this.size, !0;
    }
    var Ao = Oo;
    function jo(e) {
      var t = this.__data__, r = Ze(t, e);
      return r < 0 ? void 0 : t[r][1];
    }
    var Co = jo;
    function Io(e) {
      return Ze(this.__data__, e) > -1;
    }
    var Do = Io;
    function xo(e, t) {
      var r = this.__data__, n = Ze(r, e);
      return n < 0 ? (++this.size, r.push([e, t])) : r[n][1] = t, this;
    }
    var Eo = xo;
    function we(e) {
      var t = -1, r = e == null ? 0 : e.length;
      for (this.clear(); ++t < r; ) {
        var n = e[t];
        this.set(n[0], n[1]);
      }
    }
    we.prototype.clear = mo, we.prototype.delete = Ao, we.prototype.get = Co, we.prototype.has = Do, we.prototype.set = Eo;
    var Qe = we, Ro = ue(H, "Map"), Le = Ro;
    function Mo() {
      this.size = 0, this.__data__ = {
        hash: new zr(),
        map: new (Le || Qe)(),
        string: new zr()
      };
    }
    var Bo = Mo;
    function Lo(e) {
      var t = typeof e;
      return t == "string" || t == "number" || t == "symbol" || t == "boolean" ? e !== "__proto__" : e === null;
    }
    var Fo = Lo;
    function ko(e, t) {
      var r = e.__data__;
      return Fo(t) ? r[typeof t == "string" ? "string" : "hash"] : r.map;
    }
    var et = ko;
    function No(e) {
      var t = et(this, e).delete(e);
      return this.size -= t ? 1 : 0, t;
    }
    var Uo = No;
    function zo(e) {
      return et(this, e).get(e);
    }
    var qo = zo;
    function Vo(e) {
      return et(this, e).has(e);
    }
    var Go = Vo;
    function Ho(e, t) {
      var r = et(this, e), n = r.size;
      return r.set(e, t), this.size += r.size == n ? 0 : 1, this;
    }
    var Ko = Ho;
    function Se(e) {
      var t = -1, r = e == null ? 0 : e.length;
      for (this.clear(); ++t < r; ) {
        var n = e[t];
        this.set(n[0], n[1]);
      }
    }
    Se.prototype.clear = Bo, Se.prototype.delete = Uo, Se.prototype.get = qo, Se.prototype.has = Go, Se.prototype.set = Ko;
    var tt = Se, Wo = "Expected a function";
    function It(e, t) {
      if (typeof e != "function" || t != null && typeof t != "function")
        throw new TypeError(Wo);
      var r = function() {
        var n = arguments, a = t ? t.apply(this, n) : n[0], i = r.cache;
        if (i.has(a))
          return i.get(a);
        var o = e.apply(this, n);
        return r.cache = i.set(a, o) || i, o;
      };
      return r.cache = new (It.Cache || tt)(), r;
    }
    It.Cache = tt;
    var Jo = It, Xo = 500;
    function $o(e) {
      var t = Jo(e, function(n) {
        return r.size === Xo && r.clear(), n;
      }), r = t.cache;
      return t;
    }
    var Yo = $o, Zo = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, Qo = /\\(\\)?/g, es = Yo(function(e) {
      var t = [];
      return e.charCodeAt(0) === 46 && t.push(""), e.replace(Zo, function(r, n, a, i) {
        t.push(a ? i.replace(Qo, "$1") : n || r);
      }), t;
    }), ts = es;
    function rs(e, t) {
      for (var r = -1, n = e == null ? 0 : e.length, a = Array(n); ++r < n; )
        a[r] = t(e[r], r, e);
      return a;
    }
    var ns = rs, qr = $ ? $.prototype : void 0, Vr = qr ? qr.toString : void 0;
    function Gr(e) {
      if (typeof e == "string")
        return e;
      if (X(e))
        return ns(e, Gr) + "";
      if (Ye(e))
        return Vr ? Vr.call(e) : "";
      var t = e + "";
      return t == "0" && 1 / e == -1 / 0 ? "-0" : t;
    }
    var Hr = Gr;
    function as(e) {
      return e == null ? "" : Hr(e);
    }
    var Kr = as;
    function is(e, t) {
      return X(e) ? e : At(e, t) ? [e] : ts(Kr(e));
    }
    var rt = is;
    function os(e) {
      if (typeof e == "string" || Ye(e))
        return e;
      var t = e + "";
      return t == "0" && 1 / e == -1 / 0 ? "-0" : t;
    }
    var Oe = os;
    function ss(e, t) {
      t = rt(t, e);
      for (var r = 0, n = t.length; e != null && r < n; )
        e = e[Oe(t[r++])];
      return r && r == n ? e : void 0;
    }
    var Dt = ss;
    function us(e, t, r) {
      var n = e == null ? void 0 : Dt(e, t);
      return n === void 0 ? r : n;
    }
    var Wr = us;
    function Jr(e, t) {
      return t.length === 0 ? e : Wr(e, t);
    }
    var xt = class {
      constructor() {
        p(this, "_values", {});
      }
      /**
       * get the cache item at `key` or produce it using `producer` and cache _that_.
       *
       * Note that this won't work if you change the producer, like `get(key, producer1); get(key, producer2)`.
       */
      get(e, t) {
        if (this.has(e))
          return this._values[e];
        {
          const r = t();
          return this._values[e] = r, r;
        }
      }
      /**
       * Returns true if the cache has an item at `key`.
       */
      has(e) {
        return this._values.hasOwnProperty(e);
      }
    }, E = D(), ls = (function() {
      try {
        var e = ue(Object, "defineProperty");
        return e({}, "", {}), e;
      } catch {
      }
    })(), Xr = ls;
    function cs(e, t, r) {
      t == "__proto__" && Xr ? Xr(e, t, {
        configurable: !0,
        enumerable: !0,
        value: r,
        writable: !0
      }) : e[t] = r;
    }
    var Et = cs, fs = Object.prototype, ds = fs.hasOwnProperty;
    function ps(e, t, r) {
      var n = e[t];
      (!(ds.call(e, t) && Ct(n, r)) || r === void 0 && !(t in e)) && Et(e, t, r);
    }
    var Rt = ps, hs = 9007199254740991, vs = /^(?:0|[1-9]\d*)$/;
    function gs(e, t) {
      var r = typeof e;
      return t = t ?? hs, !!t && (r == "number" || r != "symbol" && vs.test(e)) && e > -1 && e % 1 == 0 && e < t;
    }
    var Mt = gs;
    function _s(e, t, r, n) {
      if (!K(e))
        return e;
      t = rt(t, e);
      for (var a = -1, i = t.length, o = i - 1, s = e; s != null && ++a < i; ) {
        var u = Oe(t[a]), l = r;
        if (u === "__proto__" || u === "constructor" || u === "prototype")
          return e;
        if (a != o) {
          var c = s[u];
          l = n ? n(c, u, s) : void 0, l === void 0 && (l = K(c) ? c : Mt(t[a + 1]) ? [] : {});
        }
        Rt(s, u, l), s = s[u];
      }
      return e;
    }
    var ys = _s;
    function bs(e, t, r) {
      return e == null ? e : ys(e, t, r);
    }
    var ms = bs, Bt = /* @__PURE__ */ new WeakMap();
    function Ps(e) {
      return Lt(e);
    }
    function Lt(e) {
      if (Bt.has(e))
        return Bt.get(e);
      const t = e.type === "compound" ? ws(e) : e.type === "enum" ? Ts(e) : e.default;
      return Bt.set(e, t), t;
    }
    function Ts(e) {
      const t = {
        $case: e.defaultCase
      };
      for (const [r, n] of Object.entries(e.cases))
        t[r] = Lt(n);
      return t;
    }
    function ws(e) {
      const t = {};
      for (const [r, n] of Object.entries(e.props))
        t[r] = Lt(n);
      return t;
    }
    var k = D(), Ss = $e(ni());
    function Os(e, t, r) {
      return (0, k.prism)(() => {
        const n = (0, k.val)(t);
        return k.prism.memo(
          "driver",
          () => n ? n.type === "BasicKeyframedTrack" ? As(e, n, r) : (e.logger.error("Track type not yet supported."), (0, k.prism)(() => {
          })) : (0, k.prism)(() => {
          }),
          [n]
        ).getValue();
      });
    }
    function As(e, t, r) {
      return (0, k.prism)(() => {
        let n = k.prism.ref("state", { started: !1 }), a = n.current;
        const i = r.getValue();
        return (!a.started || i < a.validFrom || a.validTo <= i) && (n.current = a = js(e, r, t)), a.der.getValue();
      });
    }
    var $r = (0, k.prism)(() => {
    });
    function js(e, t, r) {
      const n = t.getValue();
      if (r.keyframes.length === 0)
        return {
          started: !0,
          validFrom: -1 / 0,
          validTo: 1 / 0,
          der: $r
        };
      let a = 0;
      for (; ; ) {
        const i = r.keyframes[a];
        if (!i)
          return le.error;
        const o = a === r.keyframes.length - 1;
        if (n < i.position)
          return a === 0 ? le.beforeFirstKeyframe(i) : le.error;
        if (i.position === n)
          return o ? le.lastKeyframe(i) : le.between(
            i,
            r.keyframes[a + 1],
            t
          );
        if (a === r.keyframes.length - 1)
          return le.lastKeyframe(i);
        {
          const s = a + 1;
          if (r.keyframes[s].position <= n) {
            a = s;
            continue;
          } else
            return le.between(
              i,
              r.keyframes[a + 1],
              t
            );
        }
      }
    }
    var le = {
      beforeFirstKeyframe(e) {
        return {
          started: !0,
          validFrom: -1 / 0,
          validTo: e.position,
          der: (0, k.prism)(() => ({ left: e.value, progression: 0 }))
        };
      },
      lastKeyframe(e) {
        return {
          started: !0,
          validFrom: e.position,
          validTo: 1 / 0,
          der: (0, k.prism)(() => ({ left: e.value, progression: 0 }))
        };
      },
      between(e, t, r) {
        if (!e.connectedRight)
          return {
            started: !0,
            validFrom: e.position,
            validTo: t.position,
            der: (0, k.prism)(() => ({ left: e.value, progression: 0 }))
          };
        const n = (i) => (i - e.position) / (t.position - e.position);
        if (!e.type || e.type === "bezier") {
          const i = new Ss.default(
            e.handles[2],
            e.handles[3],
            t.handles[0],
            t.handles[1]
          ), o = (0, k.prism)(() => {
            const s = n(
              r.getValue()
            ), u = i.solveSimple(s);
            return {
              left: e.value,
              right: t.value,
              progression: u
            };
          });
          return {
            started: !0,
            validFrom: e.position,
            validTo: t.position,
            der: o
          };
        }
        const a = (0, k.prism)(() => {
          const i = n(
            r.getValue()
          ), o = Math.floor(i);
          return {
            left: e.value,
            right: t.value,
            progression: o
          };
        });
        return {
          started: !0,
          validFrom: e.position,
          validTo: t.position,
          der: a
        };
      },
      error: {
        started: !0,
        validFrom: -1 / 0,
        validTo: 1 / 0,
        der: $r
      }
    };
    function nt(e, t, r) {
      const a = r.get(e);
      if (a && a.override === t)
        return a.merged;
      const i = C({}, e);
      for (const o of Object.keys(t)) {
        const s = t[o], u = e[o];
        i[o] = typeof s == "object" && typeof u == "object" ? nt(
          u,
          s,
          r
        ) : s === void 0 ? u : s;
      }
      return r.set(e, { override: t, merged: i }), i;
    }
    function Fe(e, t) {
      let r = e;
      for (const n of t)
        r = r[n];
      return r;
    }
    var Yr = D(), Cs = (e, t) => {
      const r = Yr.prism.memo(e, () => new Yr.Atom(t), []);
      return r.set(t), r;
    }, A = D(), Zr = D(), Is = /\s/;
    function Ds(e) {
      for (var t = e.length; t-- && Is.test(e.charAt(t)); )
        ;
      return t;
    }
    var xs = Ds, Es = /^\s+/;
    function Rs(e) {
      return e && e.slice(0, xs(e) + 1).replace(Es, "");
    }
    var Ms = Rs, Qr = NaN, Bs = /^[-+]0x[0-9a-f]+$/i, Ls = /^0b[01]+$/i, Fs = /^0o[0-7]+$/i, ks = parseInt;
    function Ns(e) {
      if (typeof e == "number")
        return e;
      if (Ye(e))
        return Qr;
      if (K(e)) {
        var t = typeof e.valueOf == "function" ? e.valueOf() : e;
        e = K(t) ? t + "" : t;
      }
      if (typeof e != "string")
        return e === 0 ? e : +e;
      e = Ms(e);
      var r = Ls.test(e);
      return r || Fs.test(e) ? ks(e.slice(2), r ? 2 : 8) : Bs.test(e) ? Qr : +e;
    }
    var Ae = Ns, en = 1 / 0, Us = 17976931348623157e292;
    function zs(e) {
      if (!e)
        return e === 0 ? e : 0;
      if (e = Ae(e), e === en || e === -en) {
        var t = e < 0 ? -1 : 1;
        return t * Us;
      }
      return e === e ? e : 0;
    }
    var qs = zs;
    function Vs(e) {
      var t = qs(e), r = t % 1;
      return t === t ? r ? t - r : t : 0;
    }
    var tn = Vs;
    function Gs(e) {
      return e;
    }
    var Hs = Gs, Ks = ue(H, "WeakMap"), Ft = Ks, rn = Object.create, Ws = /* @__PURE__ */ (function() {
      function e() {
      }
      return function(t) {
        if (!K(t))
          return {};
        if (rn)
          return rn(t);
        e.prototype = t;
        var r = new e();
        return e.prototype = void 0, r;
      };
    })(), Js = Ws;
    function Xs(e, t) {
      var r = -1, n = e.length;
      for (t || (t = Array(n)); ++r < n; )
        t[r] = e[r];
      return t;
    }
    var $s = Xs;
    function Ys(e, t) {
      for (var r = -1, n = e == null ? 0 : e.length; ++r < n && t(e[r], r, e) !== !1; )
        ;
      return e;
    }
    var Zs = Ys;
    function Qs(e, t, r, n) {
      var a = !r;
      r || (r = {});
      for (var i = -1, o = t.length; ++i < o; ) {
        var s = t[i], u = n ? n(r[s], e[s], s, r, e) : void 0;
        u === void 0 && (u = e[s]), a ? Et(r, s, u) : Rt(r, s, u);
      }
      return r;
    }
    var at = Qs, eu = 9007199254740991;
    function tu(e) {
      return typeof e == "number" && e > -1 && e % 1 == 0 && e <= eu;
    }
    var kt = tu;
    function ru(e) {
      return e != null && kt(e.length) && !Nr(e);
    }
    var nn = ru, nu = Object.prototype;
    function au(e) {
      var t = e && e.constructor, r = typeof t == "function" && t.prototype || nu;
      return e === r;
    }
    var Nt = au;
    function iu(e, t) {
      for (var r = -1, n = Array(e); ++r < e; )
        n[r] = t(r);
      return n;
    }
    var ou = iu, su = "[object Arguments]";
    function uu(e) {
      return Q(e) && oe(e) == su;
    }
    var an = uu, on = Object.prototype, lu = on.hasOwnProperty, cu = on.propertyIsEnumerable, fu = an(/* @__PURE__ */ (function() {
      return arguments;
    })()) ? an : function(e) {
      return Q(e) && lu.call(e, "callee") && !cu.call(e, "callee");
    }, sn = fu;
    function du() {
      return !1;
    }
    var pu = du, un = Z && !Z.nodeType && Z, ln = un && !0 && W && !W.nodeType && W, hu = ln && ln.exports === un, cn = hu ? H.Buffer : void 0, vu = cn ? cn.isBuffer : void 0, gu = vu || pu, it = gu, _u = "[object Arguments]", yu = "[object Array]", bu = "[object Boolean]", mu = "[object Date]", Pu = "[object Error]", Tu = "[object Function]", wu = "[object Map]", Su = "[object Number]", Ou = "[object Object]", Au = "[object RegExp]", ju = "[object Set]", Cu = "[object String]", Iu = "[object WeakMap]", Du = "[object ArrayBuffer]", xu = "[object DataView]", Eu = "[object Float32Array]", Ru = "[object Float64Array]", Mu = "[object Int8Array]", Bu = "[object Int16Array]", Lu = "[object Int32Array]", Fu = "[object Uint8Array]", ku = "[object Uint8ClampedArray]", Nu = "[object Uint16Array]", Uu = "[object Uint32Array]", j = {};
    j[Eu] = j[Ru] = j[Mu] = j[Bu] = j[Lu] = j[Fu] = j[ku] = j[Nu] = j[Uu] = !0, j[_u] = j[yu] = j[Du] = j[bu] = j[xu] = j[mu] = j[Pu] = j[Tu] = j[wu] = j[Su] = j[Ou] = j[Au] = j[ju] = j[Cu] = j[Iu] = !1;
    function zu(e) {
      return Q(e) && kt(e.length) && !!j[oe(e)];
    }
    var qu = zu;
    function Vu(e) {
      return function(t) {
        return e(t);
      };
    }
    var Ut = Vu, fn = Z && !Z.nodeType && Z, ke = fn && !0 && W && !W.nodeType && W, Gu = ke && ke.exports === fn, zt = Gu && Lr.process, Hu = (function() {
      try {
        var e = ke && ke.require && ke.require("util").types;
        return e || zt && zt.binding && zt.binding("util");
      } catch {
      }
    })(), je = Hu, dn = je && je.isTypedArray, Ku = dn ? Ut(dn) : qu, pn = Ku, Wu = Object.prototype, Ju = Wu.hasOwnProperty;
    function Xu(e, t) {
      var r = X(e), n = !r && sn(e), a = !r && !n && it(e), i = !r && !n && !a && pn(e), o = r || n || a || i, s = o ? ou(e.length, String) : [], u = s.length;
      for (var l in e)
        (t || Ju.call(e, l)) && !(o && // Safari 9 has enumerable `arguments.length` in strict mode.
        (l == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
        a && (l == "offset" || l == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
        i && (l == "buffer" || l == "byteLength" || l == "byteOffset") || // Skip index properties.
        Mt(l, u))) && s.push(l);
      return s;
    }
    var hn = Xu;
    function $u(e, t) {
      return function(r) {
        return e(t(r));
      };
    }
    var vn = $u, Yu = vn(Object.keys, Object), Zu = Yu, Qu = Object.prototype, el = Qu.hasOwnProperty;
    function tl(e) {
      if (!Nt(e))
        return Zu(e);
      var t = [];
      for (var r in Object(e))
        el.call(e, r) && r != "constructor" && t.push(r);
      return t;
    }
    var rl = tl;
    function nl(e) {
      return nn(e) ? hn(e) : rl(e);
    }
    var Ne = nl;
    function al(e) {
      var t = [];
      if (e != null)
        for (var r in Object(e))
          t.push(r);
      return t;
    }
    var il = al, ol = Object.prototype, sl = ol.hasOwnProperty;
    function ul(e) {
      if (!K(e))
        return il(e);
      var t = Nt(e), r = [];
      for (var n in e)
        n == "constructor" && (t || !sl.call(e, n)) || r.push(n);
      return r;
    }
    var ll = ul;
    function cl(e) {
      return nn(e) ? hn(e, !0) : ll(e);
    }
    var qt = cl;
    function fl(e, t) {
      for (var r = -1, n = t.length, a = e.length; ++r < n; )
        e[a + r] = t[r];
      return e;
    }
    var gn = fl, dl = vn(Object.getPrototypeOf, Object), Vt = dl, pl = "[object Object]", hl = Function.prototype, vl = Object.prototype, _n = hl.toString, gl = vl.hasOwnProperty, _l = _n.call(Object);
    function yl(e) {
      if (!Q(e) || oe(e) != pl)
        return !1;
      var t = Vt(e);
      if (t === null)
        return !0;
      var r = gl.call(t, "constructor") && t.constructor;
      return typeof r == "function" && r instanceof r && _n.call(r) == _l;
    }
    var bl = yl;
    function ml(e, t, r) {
      var n = -1, a = e.length;
      t < 0 && (t = -t > a ? 0 : a + t), r = r > a ? a : r, r < 0 && (r += a), a = t > r ? 0 : r - t >>> 0, t >>>= 0;
      for (var i = Array(a); ++n < a; )
        i[n] = e[n + t];
      return i;
    }
    var yn = ml;
    function Pl(e, t, r) {
      var n = e.length;
      return r = r === void 0 ? n : r, !t && r >= n ? e : yn(e, t, r);
    }
    var Tl = Pl, wl = "\\ud800-\\udfff", Sl = "\\u0300-\\u036f", Ol = "\\ufe20-\\ufe2f", Al = "\\u20d0-\\u20ff", jl = Sl + Ol + Al, Cl = "\\ufe0e\\ufe0f", Il = "\\u200d", Dl = RegExp("[" + Il + wl + jl + Cl + "]");
    function xl(e) {
      return Dl.test(e);
    }
    var Gt = xl;
    function El(e) {
      return e.split("");
    }
    var Rl = El, bn = "\\ud800-\\udfff", Ml = "\\u0300-\\u036f", Bl = "\\ufe20-\\ufe2f", Ll = "\\u20d0-\\u20ff", Fl = Ml + Bl + Ll, kl = "\\ufe0e\\ufe0f", Nl = "[" + bn + "]", Ht = "[" + Fl + "]", Kt = "\\ud83c[\\udffb-\\udfff]", Ul = "(?:" + Ht + "|" + Kt + ")", mn = "[^" + bn + "]", Pn = "(?:\\ud83c[\\udde6-\\uddff]){2}", Tn = "[\\ud800-\\udbff][\\udc00-\\udfff]", zl = "\\u200d", wn = Ul + "?", Sn = "[" + kl + "]?", ql = "(?:" + zl + "(?:" + [mn, Pn, Tn].join("|") + ")" + Sn + wn + ")*", Vl = Sn + wn + ql, Gl = "(?:" + [mn + Ht + "?", Ht, Pn, Tn, Nl].join("|") + ")", Hl = RegExp(Kt + "(?=" + Kt + ")|" + Gl + Vl, "g");
    function Kl(e) {
      return e.match(Hl) || [];
    }
    var Wl = Kl;
    function Jl(e) {
      return Gt(e) ? Wl(e) : Rl(e);
    }
    var Xl = Jl;
    function $l(e, t, r) {
      return e === e && (r !== void 0 && (e = e <= r ? e : r), t !== void 0 && (e = e >= t ? e : t)), e;
    }
    var Yl = $l;
    function Zl(e, t, r) {
      return r === void 0 && (r = t, t = void 0), r !== void 0 && (r = Ae(r), r = r === r ? r : 0), t !== void 0 && (t = Ae(t), t = t === t ? t : 0), Yl(Ae(e), t, r);
    }
    var On = Zl;
    function Ql() {
      this.__data__ = new Qe(), this.size = 0;
    }
    var ec = Ql;
    function tc(e) {
      var t = this.__data__, r = t.delete(e);
      return this.size = t.size, r;
    }
    var rc = tc;
    function nc(e) {
      return this.__data__.get(e);
    }
    var ac = nc;
    function ic(e) {
      return this.__data__.has(e);
    }
    var oc = ic, sc = 200;
    function uc(e, t) {
      var r = this.__data__;
      if (r instanceof Qe) {
        var n = r.__data__;
        if (!Le || n.length < sc - 1)
          return n.push([e, t]), this.size = ++r.size, this;
        r = this.__data__ = new tt(n);
      }
      return r.set(e, t), this.size = r.size, this;
    }
    var lc = uc;
    function Ce(e) {
      var t = this.__data__ = new Qe(e);
      this.size = t.size;
    }
    Ce.prototype.clear = ec, Ce.prototype.delete = rc, Ce.prototype.get = ac, Ce.prototype.has = oc, Ce.prototype.set = lc;
    var Ue = Ce;
    function cc(e, t) {
      return e && at(t, Ne(t), e);
    }
    var fc = cc;
    function dc(e, t) {
      return e && at(t, qt(t), e);
    }
    var pc = dc, An = Z && !Z.nodeType && Z, jn = An && !0 && W && !W.nodeType && W, hc = jn && jn.exports === An, Cn = hc ? H.Buffer : void 0, In = Cn ? Cn.allocUnsafe : void 0;
    function vc(e, t) {
      if (t)
        return e.slice();
      var r = e.length, n = In ? In(r) : new e.constructor(r);
      return e.copy(n), n;
    }
    var gc = vc;
    function _c(e, t) {
      for (var r = -1, n = e == null ? 0 : e.length, a = 0, i = []; ++r < n; ) {
        var o = e[r];
        t(o, r, e) && (i[a++] = o);
      }
      return i;
    }
    var yc = _c;
    function bc() {
      return [];
    }
    var Dn = bc, mc = Object.prototype, Pc = mc.propertyIsEnumerable, xn = Object.getOwnPropertySymbols, Tc = xn ? function(e) {
      return e == null ? [] : (e = Object(e), yc(xn(e), function(t) {
        return Pc.call(e, t);
      }));
    } : Dn, Wt = Tc;
    function wc(e, t) {
      return at(e, Wt(e), t);
    }
    var Sc = wc, Oc = Object.getOwnPropertySymbols, Ac = Oc ? function(e) {
      for (var t = []; e; )
        gn(t, Wt(e)), e = Vt(e);
      return t;
    } : Dn, En = Ac;
    function jc(e, t) {
      return at(e, En(e), t);
    }
    var Cc = jc;
    function Ic(e, t, r) {
      var n = t(e);
      return X(e) ? n : gn(n, r(e));
    }
    var Rn = Ic;
    function Dc(e) {
      return Rn(e, Ne, Wt);
    }
    var Jt = Dc;
    function xc(e) {
      return Rn(e, qt, En);
    }
    var Ec = xc, Rc = ue(H, "DataView"), Xt = Rc, Mc = ue(H, "Promise"), $t = Mc, Bc = ue(H, "Set"), Yt = Bc, Mn = "[object Map]", Lc = "[object Object]", Bn = "[object Promise]", Ln = "[object Set]", Fn = "[object WeakMap]", kn = "[object DataView]", Fc = se(Xt), kc = se(Le), Nc = se($t), Uc = se(Yt), zc = se(Ft), ce = oe;
    (Xt && ce(new Xt(new ArrayBuffer(1))) != kn || Le && ce(new Le()) != Mn || $t && ce($t.resolve()) != Bn || Yt && ce(new Yt()) != Ln || Ft && ce(new Ft()) != Fn) && (ce = function(e) {
      var t = oe(e), r = t == Lc ? e.constructor : void 0, n = r ? se(r) : "";
      if (n)
        switch (n) {
          case Fc:
            return kn;
          case kc:
            return Mn;
          case Nc:
            return Bn;
          case Uc:
            return Ln;
          case zc:
            return Fn;
        }
      return t;
    });
    var ze = ce, qc = Object.prototype, Vc = qc.hasOwnProperty;
    function Gc(e) {
      var t = e.length, r = new e.constructor(t);
      return t && typeof e[0] == "string" && Vc.call(e, "index") && (r.index = e.index, r.input = e.input), r;
    }
    var Hc = Gc, Kc = H.Uint8Array, ot = Kc;
    function Wc(e) {
      var t = new e.constructor(e.byteLength);
      return new ot(t).set(new ot(e)), t;
    }
    var Zt = Wc;
    function Jc(e, t) {
      var r = t ? Zt(e.buffer) : e.buffer;
      return new e.constructor(r, e.byteOffset, e.byteLength);
    }
    var Xc = Jc, $c = /\w*$/;
    function Yc(e) {
      var t = new e.constructor(e.source, $c.exec(e));
      return t.lastIndex = e.lastIndex, t;
    }
    var Zc = Yc, Nn = $ ? $.prototype : void 0, Un = Nn ? Nn.valueOf : void 0;
    function Qc(e) {
      return Un ? Object(Un.call(e)) : {};
    }
    var ef = Qc;
    function tf(e, t) {
      var r = t ? Zt(e.buffer) : e.buffer;
      return new e.constructor(r, e.byteOffset, e.length);
    }
    var rf = tf, nf = "[object Boolean]", af = "[object Date]", of = "[object Map]", sf = "[object Number]", uf = "[object RegExp]", lf = "[object Set]", cf = "[object String]", ff = "[object Symbol]", df = "[object ArrayBuffer]", pf = "[object DataView]", hf = "[object Float32Array]", vf = "[object Float64Array]", gf = "[object Int8Array]", _f = "[object Int16Array]", yf = "[object Int32Array]", bf = "[object Uint8Array]", mf = "[object Uint8ClampedArray]", Pf = "[object Uint16Array]", Tf = "[object Uint32Array]";
    function wf(e, t, r) {
      var n = e.constructor;
      switch (t) {
        case df:
          return Zt(e);
        case nf:
        case af:
          return new n(+e);
        case pf:
          return Xc(e, r);
        case hf:
        case vf:
        case gf:
        case _f:
        case yf:
        case bf:
        case mf:
        case Pf:
        case Tf:
          return rf(e, r);
        case of:
          return new n();
        case sf:
        case cf:
          return new n(e);
        case uf:
          return Zc(e);
        case lf:
          return new n();
        case ff:
          return ef(e);
      }
    }
    var Sf = wf;
    function Of(e) {
      return typeof e.constructor == "function" && !Nt(e) ? Js(Vt(e)) : {};
    }
    var Af = Of, jf = "[object Map]";
    function Cf(e) {
      return Q(e) && ze(e) == jf;
    }
    var If = Cf, zn = je && je.isMap, Df = zn ? Ut(zn) : If, xf = Df, Ef = "[object Set]";
    function Rf(e) {
      return Q(e) && ze(e) == Ef;
    }
    var Mf = Rf, qn = je && je.isSet, Bf = qn ? Ut(qn) : Mf, Lf = Bf, Ff = 1, kf = 2, Nf = 4, Vn = "[object Arguments]", Uf = "[object Array]", zf = "[object Boolean]", qf = "[object Date]", Vf = "[object Error]", Gn = "[object Function]", Gf = "[object GeneratorFunction]", Hf = "[object Map]", Kf = "[object Number]", Hn = "[object Object]", Wf = "[object RegExp]", Jf = "[object Set]", Xf = "[object String]", $f = "[object Symbol]", Yf = "[object WeakMap]", Zf = "[object ArrayBuffer]", Qf = "[object DataView]", ed = "[object Float32Array]", td = "[object Float64Array]", rd = "[object Int8Array]", nd = "[object Int16Array]", ad = "[object Int32Array]", id = "[object Uint8Array]", od = "[object Uint8ClampedArray]", sd = "[object Uint16Array]", ud = "[object Uint32Array]", T = {};
    T[Vn] = T[Uf] = T[Zf] = T[Qf] = T[zf] = T[qf] = T[ed] = T[td] = T[rd] = T[nd] = T[ad] = T[Hf] = T[Kf] = T[Hn] = T[Wf] = T[Jf] = T[Xf] = T[$f] = T[id] = T[od] = T[sd] = T[ud] = !0, T[Vf] = T[Gn] = T[Yf] = !1;
    function st(e, t, r, n, a, i) {
      var o, s = t & Ff, u = t & kf, l = t & Nf;
      if (r && (o = a ? r(e, n, a, i) : r(e)), o !== void 0)
        return o;
      if (!K(e))
        return e;
      var c = X(e);
      if (c) {
        if (o = Hc(e), !s)
          return $s(e, o);
      } else {
        var f = ze(e), d = f == Gn || f == Gf;
        if (it(e))
          return gc(e, s);
        if (f == Hn || f == Vn || d && !a) {
          if (o = u || d ? {} : Af(e), !s)
            return u ? Cc(e, pc(o, e)) : Sc(e, fc(o, e));
        } else {
          if (!T[f])
            return a ? e : {};
          o = Sf(e, f, s);
        }
      }
      i || (i = new Ue());
      var v = i.get(e);
      if (v)
        return v;
      i.set(e, o), Lf(e) ? e.forEach(function(y) {
        o.add(st(y, t, r, y, e, i));
      }) : xf(e) && e.forEach(function(y, g) {
        o.set(g, st(y, t, r, g, e, i));
      });
      var h = l ? u ? Ec : Jt : u ? qt : Ne, _ = c ? void 0 : h(e);
      return Zs(_ || e, function(y, g) {
        _ && (g = y, y = e[g]), Rt(o, g, st(y, t, r, g, e, i));
      }), o;
    }
    var ld = st, cd = 1, fd = 4;
    function dd(e) {
      return ld(e, cd | fd);
    }
    var pd = dd, hd = "__lodash_hash_undefined__";
    function vd(e) {
      return this.__data__.set(e, hd), this;
    }
    var gd = vd;
    function _d(e) {
      return this.__data__.has(e);
    }
    var yd = _d;
    function ut(e) {
      var t = -1, r = e == null ? 0 : e.length;
      for (this.__data__ = new tt(); ++t < r; )
        this.add(e[t]);
    }
    ut.prototype.add = ut.prototype.push = gd, ut.prototype.has = yd;
    var bd = ut;
    function md(e, t) {
      for (var r = -1, n = e == null ? 0 : e.length; ++r < n; )
        if (t(e[r], r, e))
          return !0;
      return !1;
    }
    var Pd = md;
    function Td(e, t) {
      return e.has(t);
    }
    var wd = Td, Sd = 1, Od = 2;
    function Ad(e, t, r, n, a, i) {
      var o = r & Sd, s = e.length, u = t.length;
      if (s != u && !(o && u > s))
        return !1;
      var l = i.get(e), c = i.get(t);
      if (l && c)
        return l == t && c == e;
      var f = -1, d = !0, v = r & Od ? new bd() : void 0;
      for (i.set(e, t), i.set(t, e); ++f < s; ) {
        var h = e[f], _ = t[f];
        if (n)
          var y = o ? n(_, h, f, t, e, i) : n(h, _, f, e, t, i);
        if (y !== void 0) {
          if (y)
            continue;
          d = !1;
          break;
        }
        if (v) {
          if (!Pd(t, function(g, b) {
            if (!wd(v, b) && (h === g || a(h, g, r, n, i)))
              return v.push(b);
          })) {
            d = !1;
            break;
          }
        } else if (!(h === _ || a(h, _, r, n, i))) {
          d = !1;
          break;
        }
      }
      return i.delete(e), i.delete(t), d;
    }
    var Kn = Ad;
    function jd(e) {
      var t = -1, r = Array(e.size);
      return e.forEach(function(n, a) {
        r[++t] = [a, n];
      }), r;
    }
    var Cd = jd;
    function Id(e) {
      var t = -1, r = Array(e.size);
      return e.forEach(function(n) {
        r[++t] = n;
      }), r;
    }
    var Dd = Id, xd = 1, Ed = 2, Rd = "[object Boolean]", Md = "[object Date]", Bd = "[object Error]", Ld = "[object Map]", Fd = "[object Number]", kd = "[object RegExp]", Nd = "[object Set]", Ud = "[object String]", zd = "[object Symbol]", qd = "[object ArrayBuffer]", Vd = "[object DataView]", Wn = $ ? $.prototype : void 0, Qt = Wn ? Wn.valueOf : void 0;
    function Gd(e, t, r, n, a, i, o) {
      switch (r) {
        case Vd:
          if (e.byteLength != t.byteLength || e.byteOffset != t.byteOffset)
            return !1;
          e = e.buffer, t = t.buffer;
        case qd:
          return !(e.byteLength != t.byteLength || !i(new ot(e), new ot(t)));
        case Rd:
        case Md:
        case Fd:
          return Ct(+e, +t);
        case Bd:
          return e.name == t.name && e.message == t.message;
        case kd:
        case Ud:
          return e == t + "";
        case Ld:
          var s = Cd;
        case Nd:
          var u = n & xd;
          if (s || (s = Dd), e.size != t.size && !u)
            return !1;
          var l = o.get(e);
          if (l)
            return l == t;
          n |= Ed, o.set(e, t);
          var c = Kn(s(e), s(t), n, a, i, o);
          return o.delete(e), c;
        case zd:
          if (Qt)
            return Qt.call(e) == Qt.call(t);
      }
      return !1;
    }
    var Hd = Gd, Kd = 1, Wd = Object.prototype, Jd = Wd.hasOwnProperty;
    function Xd(e, t, r, n, a, i) {
      var o = r & Kd, s = Jt(e), u = s.length, l = Jt(t), c = l.length;
      if (u != c && !o)
        return !1;
      for (var f = u; f--; ) {
        var d = s[f];
        if (!(o ? d in t : Jd.call(t, d)))
          return !1;
      }
      var v = i.get(e), h = i.get(t);
      if (v && h)
        return v == t && h == e;
      var _ = !0;
      i.set(e, t), i.set(t, e);
      for (var y = o; ++f < u; ) {
        d = s[f];
        var g = e[d], b = t[d];
        if (n)
          var R = o ? n(b, g, d, t, e, i) : n(g, b, d, e, t, i);
        if (!(R === void 0 ? g === b || a(g, b, r, n, i) : R)) {
          _ = !1;
          break;
        }
        y || (y = d == "constructor");
      }
      if (_ && !y) {
        var F = e.constructor, M = t.constructor;
        F != M && "constructor" in e && "constructor" in t && !(typeof F == "function" && F instanceof F && typeof M == "function" && M instanceof M) && (_ = !1);
      }
      return i.delete(e), i.delete(t), _;
    }
    var $d = Xd, Yd = 1, Jn = "[object Arguments]", Xn = "[object Array]", lt = "[object Object]", Zd = Object.prototype, $n = Zd.hasOwnProperty;
    function Qd(e, t, r, n, a, i) {
      var o = X(e), s = X(t), u = o ? Xn : ze(e), l = s ? Xn : ze(t);
      u = u == Jn ? lt : u, l = l == Jn ? lt : l;
      var c = u == lt, f = l == lt, d = u == l;
      if (d && it(e)) {
        if (!it(t))
          return !1;
        o = !0, c = !1;
      }
      if (d && !c)
        return i || (i = new Ue()), o || pn(e) ? Kn(e, t, r, n, a, i) : Hd(e, t, u, r, n, a, i);
      if (!(r & Yd)) {
        var v = c && $n.call(e, "__wrapped__"), h = f && $n.call(t, "__wrapped__");
        if (v || h) {
          var _ = v ? e.value() : e, y = h ? t.value() : t;
          return i || (i = new Ue()), a(_, y, r, n, i);
        }
      }
      return d ? (i || (i = new Ue()), $d(e, t, r, n, a, i)) : !1;
    }
    var ep = Qd;
    function Yn(e, t, r, n, a) {
      return e === t ? !0 : e == null || t == null || !Q(e) && !Q(t) ? e !== e && t !== t : ep(e, t, r, n, Yn, a);
    }
    var Zn = Yn, tp = 1, rp = 2;
    function np(e, t, r, n) {
      var a = r.length, i = a, o = !n;
      if (e == null)
        return !i;
      for (e = Object(e); a--; ) {
        var s = r[a];
        if (o && s[2] ? s[1] !== e[s[0]] : !(s[0] in e))
          return !1;
      }
      for (; ++a < i; ) {
        s = r[a];
        var u = s[0], l = e[u], c = s[1];
        if (o && s[2]) {
          if (l === void 0 && !(u in e))
            return !1;
        } else {
          var f = new Ue();
          if (n)
            var d = n(l, c, u, e, t, f);
          if (!(d === void 0 ? Zn(c, l, tp | rp, n, f) : d))
            return !1;
        }
      }
      return !0;
    }
    var ap = np;
    function ip(e) {
      return e === e && !K(e);
    }
    var Qn = ip;
    function op(e) {
      for (var t = Ne(e), r = t.length; r--; ) {
        var n = t[r], a = e[n];
        t[r] = [n, a, Qn(a)];
      }
      return t;
    }
    var sp = op;
    function up(e, t) {
      return function(r) {
        return r == null ? !1 : r[e] === t && (t !== void 0 || e in Object(r));
      };
    }
    var ea = up;
    function lp(e) {
      var t = sp(e);
      return t.length == 1 && t[0][2] ? ea(t[0][0], t[0][1]) : function(r) {
        return r === e || ap(r, e, t);
      };
    }
    var cp = lp;
    function fp(e, t) {
      return e != null && t in Object(e);
    }
    var dp = fp;
    function pp(e, t, r) {
      t = rt(t, e);
      for (var n = -1, a = t.length, i = !1; ++n < a; ) {
        var o = Oe(t[n]);
        if (!(i = e != null && r(e, o)))
          break;
        e = e[o];
      }
      return i || ++n != a ? i : (a = e == null ? 0 : e.length, !!a && kt(a) && Mt(o, a) && (X(e) || sn(e)));
    }
    var hp = pp;
    function vp(e, t) {
      return e != null && hp(e, t, dp);
    }
    var gp = vp, _p = 1, yp = 2;
    function bp(e, t) {
      return At(e) && Qn(t) ? ea(Oe(e), t) : function(r) {
        var n = Wr(r, e);
        return n === void 0 && n === t ? gp(r, e) : Zn(t, n, _p | yp);
      };
    }
    var mp = bp;
    function Pp(e) {
      return function(t) {
        return t == null ? void 0 : t[e];
      };
    }
    var ta = Pp;
    function Tp(e) {
      return function(t) {
        return Dt(t, e);
      };
    }
    var wp = Tp;
    function Sp(e) {
      return At(e) ? ta(Oe(e)) : wp(e);
    }
    var Op = Sp;
    function Ap(e) {
      return typeof e == "function" ? e : e == null ? Hs : typeof e == "object" ? X(e) ? mp(e[0], e[1]) : cp(e) : Op(e);
    }
    var jp = Ap;
    function Cp(e) {
      return function(t, r, n) {
        for (var a = -1, i = Object(t), o = n(t), s = o.length; s--; ) {
          var u = o[e ? s : ++a];
          if (r(i[u], u, i) === !1)
            break;
        }
        return t;
      };
    }
    var Ip = Cp, Dp = Ip(), xp = Dp;
    function Ep(e, t) {
      return e && xp(e, t, Ne);
    }
    var Rp = Ep, Mp = function() {
      return H.Date.now();
    }, er = Mp, Bp = "Expected a function", Lp = Math.max, Fp = Math.min;
    function kp(e, t, r) {
      var n, a, i, o, s, u, l = 0, c = !1, f = !1, d = !0;
      if (typeof e != "function")
        throw new TypeError(Bp);
      t = Ae(t) || 0, K(r) && (c = !!r.leading, f = "maxWait" in r, i = f ? Lp(Ae(r.maxWait) || 0, t) : i, d = "trailing" in r ? !!r.trailing : d);
      function v(P) {
        var B = n, q = a;
        return n = a = void 0, l = P, o = e.apply(q, B), o;
      }
      function h(P) {
        return l = P, s = setTimeout(g, t), c ? v(P) : o;
      }
      function _(P) {
        var B = P - u, q = P - l, Y = t - B;
        return f ? Fp(Y, i - q) : Y;
      }
      function y(P) {
        var B = P - u, q = P - l;
        return u === void 0 || B >= t || B < 0 || f && q >= i;
      }
      function g() {
        var P = er();
        if (y(P))
          return b(P);
        s = setTimeout(g, _(P));
      }
      function b(P) {
        return s = void 0, d && n ? v(P) : (n = a = void 0, o);
      }
      function R() {
        s !== void 0 && clearTimeout(s), l = 0, n = u = a = s = void 0;
      }
      function F() {
        return s === void 0 ? o : b(er());
      }
      function M() {
        var P = er(), B = y(P);
        if (n = arguments, a = this, u = P, B) {
          if (s === void 0)
            return h(u);
          if (f)
            return clearTimeout(s), s = setTimeout(g, t), v(u);
        }
        return s === void 0 && (s = setTimeout(g, t)), o;
      }
      return M.cancel = R, M.flush = F, M;
    }
    var Np = kp;
    function Up(e) {
      var t = e == null ? 0 : e.length;
      return t ? e[t - 1] : void 0;
    }
    var zp = Up;
    function qp(e, t) {
      return t.length < 2 ? e : Dt(e, yn(t, 0, -1));
    }
    var Vp = qp;
    function Gp(e) {
      return typeof e == "number" && e == tn(e);
    }
    var Hp = Gp;
    function Kp(e, t) {
      var r = {};
      return t = jp(t), Rp(e, function(n, a, i) {
        Et(r, a, t(n, a, i));
      }), r;
    }
    var Wp = Kp;
    function Jp(e, t) {
      return t = rt(t, e), e = Vp(e, t), e == null || delete e[Oe(zp(t))];
    }
    var Xp = Jp, $p = 9007199254740991, Yp = Math.floor;
    function Zp(e, t) {
      var r = "";
      if (!e || t < 1 || t > $p)
        return r;
      do
        t % 2 && (r += e), t = Yp(t / 2), t && (e += e);
      while (t);
      return r;
    }
    var ra = Zp, Qp = ta("length"), eh = Qp, na = "\\ud800-\\udfff", th = "\\u0300-\\u036f", rh = "\\ufe20-\\ufe2f", nh = "\\u20d0-\\u20ff", ah = th + rh + nh, ih = "\\ufe0e\\ufe0f", oh = "[" + na + "]", tr = "[" + ah + "]", rr = "\\ud83c[\\udffb-\\udfff]", sh = "(?:" + tr + "|" + rr + ")", aa = "[^" + na + "]", ia = "(?:\\ud83c[\\udde6-\\uddff]){2}", oa = "[\\ud800-\\udbff][\\udc00-\\udfff]", uh = "\\u200d", sa = sh + "?", ua = "[" + ih + "]?", lh = "(?:" + uh + "(?:" + [aa, ia, oa].join("|") + ")" + ua + sa + ")*", ch = ua + sa + lh, fh = "(?:" + [aa + tr + "?", tr, ia, oa, oh].join("|") + ")", la = RegExp(rr + "(?=" + rr + ")|" + fh + ch, "g");
    function dh(e) {
      for (var t = la.lastIndex = 0; la.test(e); )
        ++t;
      return t;
    }
    var ph = dh;
    function hh(e) {
      return Gt(e) ? ph(e) : eh(e);
    }
    var ca = hh, vh = Math.ceil;
    function gh(e, t) {
      t = t === void 0 ? " " : Hr(t);
      var r = t.length;
      if (r < 2)
        return r ? ra(t, e) : t;
      var n = ra(t, vh(e / ca(t)));
      return Gt(t) ? Tl(Xl(n), 0, e).join("") : n.slice(0, e);
    }
    var _h = gh;
    function yh(e, t, r) {
      e = Kr(e), t = tn(t);
      var n = t ? ca(e) : 0;
      return t && n < t ? _h(t - n, r) + e : e;
    }
    var qe = yh;
    function bh(e, t) {
      return e == null ? !0 : Xp(e, t);
    }
    var fa = bh, mh = 5 * 1e3, Ph = class {
      /**
       * @internal
       */
      constructor(e) {
        p(this, "_cache", new xt()), p(this, "_keepHotUntapDebounce"), Re(this, e);
      }
      get type() {
        return "Theatre_SheetObject_PublicAPI";
      }
      get props() {
        return m(this).propsP;
      }
      get sheet() {
        return m(this).sheet.publicApi;
      }
      get project() {
        return m(this).sheet.project.publicApi;
      }
      get address() {
        return C({}, m(this).address);
      }
      _valuesPrism() {
        return this._cache.get("_valuesPrism", () => {
          const e = m(this);
          return (0, Zr.prism)(() => (0, Zr.val)(e.getValues().getValue()));
        });
      }
      onValuesChange(e, t) {
        return jr(this._valuesPrism(), e, t);
      }
      // internal: Make the deviration keepHot if directly read
      get value() {
        const e = this._valuesPrism();
        {
          if (!e.isHot) {
            this._keepHotUntapDebounce != null && this._keepHotUntapDebounce.flush();
            const t = e.keepHot();
            this._keepHotUntapDebounce = Np(() => {
              t(), this._keepHotUntapDebounce = void 0;
            }, mh);
          }
          this._keepHotUntapDebounce && this._keepHotUntapDebounce();
        }
        return e.getValue();
      }
      set initialValue(e) {
        m(this).setInitialValue(e);
      }
    };
    function Th(e) {
      const t = /* @__PURE__ */ new WeakMap();
      return (r) => (t.has(r) || t.set(r, e(r)), t.get(r));
    }
    function ct(e) {
      return e.type === "compound" || e.type === "enum";
    }
    function nr(e, t) {
      if (!e)
        return;
      const [r, ...n] = t;
      if (r === void 0)
        return e;
      if (!ct(e))
        return;
      const a = e.type === "enum" ? e.cases[r] : e.props[r];
      return nr(a, n);
    }
    function wh(e) {
      return !ct(e);
    }
    var Sh = class {
      constructor(e, t, r) {
        this.sheet = e, this.template = t, this.nativeObject = r, p(this, "$$isPointerToPrismProvider", !0), p(this, "address"), p(this, "publicApi"), p(this, "_initialValue", new A.Atom({})), p(this, "_cache", new xt()), p(this, "_logger"), p(this, "_internalUtilCtx"), this._logger = e._logger.named(
          "SheetObject",
          t.address.objectKey
        ), this._logger._trace("creating object"), this._internalUtilCtx = { logger: this._logger.utilFor.internal() }, this.address = J(C({}, t.address), {
          sheetInstanceId: e.address.sheetInstanceId
        }), this.publicApi = new Ph(this);
      }
      get type() {
        return "Theatre_SheetObject";
      }
      getValues() {
        return this._cache.get(
          "getValues()",
          () => (0, A.prism)(() => {
            const e = (0, A.val)(this.template.getDefaultValues()), t = (0, A.val)(this._initialValue.pointer), r = A.prism.memo(
              "withInitialCache",
              () => /* @__PURE__ */ new WeakMap(),
              []
            ), n = nt(
              e,
              t,
              r
            ), a = (0, A.val)(this.template.getStaticValues()), i = A.prism.memo(
              "withStatics",
              () => /* @__PURE__ */ new WeakMap(),
              []
            );
            let s = nt(
              n,
              a,
              i
            ), u;
            {
              const c = A.prism.memo(
                "seq",
                () => this.getSequencedValues(),
                []
              ), f = A.prism.memo(
                "withSeqsCache",
                () => /* @__PURE__ */ new WeakMap(),
                []
              );
              u = (0, A.val)((0, A.val)(c)), s = nt(s, u, f);
            }
            return Cs("finalAtom", s).pointer;
          })
        );
      }
      getValueByPointer(e) {
        const t = (0, A.val)(this.getValues()), { path: r } = (0, A.getPointerParts)(e);
        return (0, A.val)(
          Fe(t, r)
        );
      }
      pointerToPrism(e) {
        const { path: t } = (0, A.getPointerParts)(e);
        return (0, A.prism)(() => {
          const r = (0, A.val)(this.getValues());
          return (0, A.val)(Fe(r, t));
        });
      }
      /**
       * Returns values of props that are sequenced.
       */
      getSequencedValues() {
        return (0, A.prism)(() => {
          const e = A.prism.memo(
            "tracksToProcess",
            () => this.template.getArrayOfValidSequenceTracks(),
            []
          ), t = (0, A.val)(e), r = new A.Atom({}), n = (0, A.val)(this.template.configPointer);
          return A.prism.effect(
            "processTracks",
            () => {
              const a = [];
              for (const { trackId: i, pathToProp: o } of t) {
                const s = this._trackIdToPrism(i), u = nr(
                  n,
                  o
                ), l = u.deserializeAndSanitize, c = u.interpolate, f = () => {
                  const v = s.getValue();
                  if (!v)
                    return r.setByPointer(
                      (b) => Fe(b, o),
                      void 0
                    );
                  const h = l(v.left), _ = h === void 0 ? u.default : h;
                  if (v.right === void 0)
                    return r.setByPointer(
                      (b) => Fe(b, o),
                      _
                    );
                  const y = l(v.right), g = y === void 0 ? u.default : y;
                  return r.setByPointer(
                    (b) => Fe(b, o),
                    c(_, g, v.progression)
                  );
                }, d = s.onStale(f);
                f(), a.push(d);
              }
              return () => {
                for (const i of a)
                  i();
              };
            },
            [n, ...t]
          ), r.pointer;
        });
      }
      _trackIdToPrism(e) {
        const t = this.template.project.pointers.historic.sheetsById[this.address.sheetId].sequence.tracksByObject[this.address.objectKey].trackData[e], r = this.sheet.getSequence().positionPrism;
        return Os(this._internalUtilCtx, t, r);
      }
      get propsP() {
        return this._cache.get(
          "propsP",
          () => (0, A.pointer)({ root: this, path: [] })
        );
      }
      validateValue(e, t) {
      }
      setInitialValue(e) {
        this.validateValue(this.propsP, e), this._initialValue.set(e);
      }
    };
    function w(e) {
      return function(r, n) {
        return e(r, n());
      };
    }
    var N = {
      _hmm: U(
        524
        /* _HMM */
      ),
      _todo: U(
        522
        /* _TODO */
      ),
      _error: U(
        521
        /* _ERROR */
      ),
      errorDev: U(
        529
        /* ERROR_DEV */
      ),
      errorPublic: U(
        545
        /* ERROR_PUBLIC */
      ),
      _kapow: U(
        268
        /* _KAPOW */
      ),
      _warn: U(
        265
        /* _WARN */
      ),
      warnDev: U(
        273
        /* WARN_DEV */
      ),
      warnPublic: U(
        289
        /* WARN_PUBLIC */
      ),
      _debug: U(
        137
        /* _DEBUG */
      ),
      debugDev: U(
        145
        /* DEBUG_DEV */
      ),
      _trace: U(
        73
        /* _TRACE */
      ),
      traceDev: U(
        81
        /* TRACE_DEV */
      )
    };
    function U(e) {
      return Object.freeze({
        audience: fe(
          e,
          8
          /* INTERNAL */
        ) ? "internal" : fe(
          e,
          16
          /* DEV */
        ) ? "dev" : "public",
        category: fe(
          e,
          4
          /* TROUBLESHOOTING */
        ) ? "troubleshooting" : fe(
          e,
          2
          /* TODO */
        ) ? "todo" : "general",
        level: (
          // I think this is equivalent... but I'm not using it until we have tests.
          // this code won't really impact performance much anyway, since it's just computed once
          // up front.
          // level &
          // (TheatreLoggerLevel.TRACE |
          //   TheatreLoggerLevel.DEBUG |
          //   TheatreLoggerLevel.WARN |
          //   TheatreLoggerLevel.ERROR),
          fe(
            e,
            512
            /* ERROR */
          ) ? 512 : fe(
            e,
            256
            /* WARN */
          ) ? 256 : fe(
            e,
            128
            /* DEBUG */
          ) ? 128 : (
            // no other option
            64
          )
        )
      });
    }
    function fe(e, t) {
      return (e & t) === t;
    }
    function S(e, t) {
      return ((t & 32) === 32 ? !0 : (t & 16) === 16 ? e.dev : (t & 8) === 8 ? e.internal : !1) && e.min <= t;
    }
    var ee = {
      loggingConsoleStyle: !0,
      loggerConsoleStyle: !0,
      includes: Object.freeze({
        internal: !1,
        dev: !1,
        min: 256
        /* WARN */
      }),
      filtered: function() {
      },
      include: function() {
        return {};
      },
      create: null,
      creatExt: null,
      named(e, t, r) {
        return this.create({
          names: [...e.names, { name: t, key: r }]
        });
      },
      style: {
        bold: void 0,
        // /Service$/
        italic: void 0,
        // /Model$/
        cssMemo: /* @__PURE__ */ new Map([
          // handle empty names so we don't have to check for
          // name.length > 0 during this.css('')
          ["", ""]
          // bring a specific override
          // ["Marker", "color:#aea9ff;font-size:0.75em;text-transform:uppercase"]
        ]),
        collapseOnRE: /[a-z- ]+/g,
        color: void 0,
        // create collapsed name
        // insert collapsed name into cssMemo with original's style
        collapsed(e) {
          if (e.length < 5)
            return e;
          const t = e.replace(this.collapseOnRE, "");
          return this.cssMemo.has(t) || this.cssMemo.set(t, this.css(e)), t;
        },
        css(e) {
          var t, r, n, a;
          const i = this.cssMemo.get(e);
          if (i)
            return i;
          let o = "color:".concat((r = (t = this.color) == null ? void 0 : t.call(this, e)) != null ? r : "hsl(".concat((e.charCodeAt(0) + e.charCodeAt(e.length - 1)) % 360, ", 100%, 60%)"));
          return (n = this.bold) != null && n.test(e) && (o += ";font-weight:600"), (a = this.italic) != null && a.test(e) && (o += ";font-style:italic"), this.cssMemo.set(e, o), o;
        }
      }
    };
    function da(e = console, t = {}) {
      const r = J(C({}, ee), { includes: C({}, ee.includes) }), n = {
        styled: jh.bind(r, e),
        noStyle: Ih.bind(r, e)
      }, a = Ah.bind(r);
      function i() {
        return r.loggingConsoleStyle && r.loggerConsoleStyle ? n.styled : n.noStyle;
      }
      return r.create = i(), {
        configureLogger(o) {
          var s;
          o === "console" ? (r.loggerConsoleStyle = ee.loggerConsoleStyle, r.create = i()) : o.type === "console" ? (r.loggerConsoleStyle = (s = o.style) != null ? s : ee.loggerConsoleStyle, r.create = i()) : o.type === "keyed" ? (r.creatExt = (u) => o.keyed(u.names), r.create = a) : o.type === "named" && (r.creatExt = Oh.bind(null, o.named), r.create = a);
        },
        configureLogging(o) {
          var s, u, l, c, f;
          r.includes.dev = (s = o.dev) != null ? s : ee.includes.dev, r.includes.internal = (u = o.internal) != null ? u : ee.includes.internal, r.includes.min = (l = o.min) != null ? l : ee.includes.min, r.include = (c = o.include) != null ? c : ee.include, r.loggingConsoleStyle = (f = o.consoleStyle) != null ? f : ee.loggingConsoleStyle, r.create = i();
        },
        getLogger() {
          return r.create({ names: [] });
        }
      };
    }
    function Oh(e, t) {
      const r = [];
      for (let { name: n, key: a } of t.names)
        r.push(a == null ? n : "".concat(n, " (").concat(a, ")"));
      return e(r);
    }
    function Ah(e) {
      const t = C(C({}, this.includes), this.include(e)), r = this.filtered, n = this.named.bind(this, e), a = this.creatExt(e), i = S(
        t,
        524
        /* _HMM */
      ), o = S(
        t,
        522
        /* _TODO */
      ), s = S(
        t,
        521
        /* _ERROR */
      ), u = S(
        t,
        529
        /* ERROR_DEV */
      ), l = S(
        t,
        545
        /* ERROR_PUBLIC */
      ), c = S(
        t,
        265
        /* _WARN */
      ), f = S(
        t,
        268
        /* _KAPOW */
      ), d = S(
        t,
        273
        /* WARN_DEV */
      ), v = S(
        t,
        289
        /* WARN_PUBLIC */
      ), h = S(
        t,
        137
        /* _DEBUG */
      ), _ = S(
        t,
        145
        /* DEBUG_DEV */
      ), y = S(
        t,
        73
        /* _TRACE */
      ), g = S(
        t,
        81
        /* TRACE_DEV */
      ), b = i ? a.error.bind(a, N._hmm) : r.bind(
        e,
        524
        /* _HMM */
      ), R = o ? a.error.bind(a, N._todo) : r.bind(
        e,
        522
        /* _TODO */
      ), F = s ? a.error.bind(a, N._error) : r.bind(
        e,
        521
        /* _ERROR */
      ), M = u ? a.error.bind(a, N.errorDev) : r.bind(
        e,
        529
        /* ERROR_DEV */
      ), P = l ? a.error.bind(a, N.errorPublic) : r.bind(
        e,
        545
        /* ERROR_PUBLIC */
      ), B = f ? a.warn.bind(a, N._kapow) : r.bind(
        e,
        268
        /* _KAPOW */
      ), q = c ? a.warn.bind(a, N._warn) : r.bind(
        e,
        265
        /* _WARN */
      ), Y = d ? a.warn.bind(a, N.warnDev) : r.bind(
        e,
        273
        /* WARN_DEV */
      ), _e = v ? a.warn.bind(a, N.warnPublic) : r.bind(
        e,
        273
        /* WARN_DEV */
      ), ye = h ? a.debug.bind(a, N._debug) : r.bind(
        e,
        137
        /* _DEBUG */
      ), be = _ ? a.debug.bind(a, N.debugDev) : r.bind(
        e,
        145
        /* DEBUG_DEV */
      ), me = y ? a.trace.bind(a, N._trace) : r.bind(
        e,
        73
        /* _TRACE */
      ), Pe = g ? a.trace.bind(a, N.traceDev) : r.bind(
        e,
        81
        /* TRACE_DEV */
      ), I = {
        _hmm: b,
        _todo: R,
        _error: F,
        errorDev: M,
        errorPublic: P,
        _kapow: B,
        _warn: q,
        warnDev: Y,
        warnPublic: _e,
        _debug: ye,
        debugDev: be,
        _trace: me,
        traceDev: Pe,
        lazy: {
          _hmm: i ? w(b) : b,
          _todo: o ? w(R) : R,
          _error: s ? w(F) : F,
          errorDev: u ? w(M) : M,
          errorPublic: l ? w(P) : P,
          _kapow: f ? w(B) : B,
          _warn: c ? w(q) : q,
          warnDev: d ? w(Y) : Y,
          warnPublic: v ? w(_e) : _e,
          _debug: h ? w(ye) : ye,
          debugDev: _ ? w(be) : be,
          _trace: y ? w(me) : me,
          traceDev: g ? w(Pe) : Pe
        },
        //
        named: n,
        utilFor: {
          internal() {
            return {
              debug: I._debug,
              error: I._error,
              warn: I._warn,
              trace: I._trace,
              named(V, O) {
                return I.named(V, O).utilFor.internal();
              }
            };
          },
          dev() {
            return {
              debug: I.debugDev,
              error: I.errorDev,
              warn: I.warnDev,
              trace: I.traceDev,
              named(V, O) {
                return I.named(V, O).utilFor.dev();
              }
            };
          },
          public() {
            return {
              error: I.errorPublic,
              warn: I.warnPublic,
              debug(V, O) {
                I._warn('(public "debug" filtered out) '.concat(V), O);
              },
              trace(V, O) {
                I._warn('(public "trace" filtered out) '.concat(V), O);
              },
              named(V, O) {
                return I.named(V, O).utilFor.public();
              }
            };
          }
        }
      };
      return I;
    }
    function jh(e, t) {
      const r = C(C({}, this.includes), this.include(t)), n = [];
      let a = "";
      for (let u = 0; u < t.names.length; u++) {
        const { name: l, key: c } = t.names[u];
        if (a += " %c".concat(l), n.push(this.style.css(l)), c != null) {
          const f = "%c#".concat(c);
          a += f, n.push(this.style.css(f));
        }
      }
      const i = this.filtered, o = this.named.bind(this, t), s = [a, ...n];
      return pa(
        i,
        t,
        r,
        e,
        s,
        Ch(s),
        o
      );
    }
    function Ch(e) {
      const t = e.slice(0);
      for (let r = 1; r < t.length; r++)
        t[r] += ";background-color:#e0005a;padding:2px;color:white";
      return t;
    }
    function Ih(e, t) {
      const r = C(C({}, this.includes), this.include(t));
      let n = "";
      for (let s = 0; s < t.names.length; s++) {
        const { name: u, key: l } = t.names[s];
        n += " ".concat(u), l != null && (n += "#".concat(l));
      }
      const a = this.filtered, i = this.named.bind(this, t), o = [n];
      return pa(
        a,
        t,
        r,
        e,
        o,
        o,
        i
      );
    }
    function pa(e, t, r, n, a, i, o) {
      const s = S(
        r,
        524
        /* _HMM */
      ), u = S(
        r,
        522
        /* _TODO */
      ), l = S(
        r,
        521
        /* _ERROR */
      ), c = S(
        r,
        529
        /* ERROR_DEV */
      ), f = S(
        r,
        545
        /* ERROR_PUBLIC */
      ), d = S(
        r,
        265
        /* _WARN */
      ), v = S(
        r,
        268
        /* _KAPOW */
      ), h = S(
        r,
        273
        /* WARN_DEV */
      ), _ = S(
        r,
        289
        /* WARN_PUBLIC */
      ), y = S(
        r,
        137
        /* _DEBUG */
      ), g = S(
        r,
        145
        /* DEBUG_DEV */
      ), b = S(
        r,
        73
        /* _TRACE */
      ), R = S(
        r,
        81
        /* TRACE_DEV */
      ), F = s ? n.error.bind(n, ...a) : e.bind(
        t,
        524
        /* _HMM */
      ), M = u ? n.error.bind(n, ...a) : e.bind(
        t,
        522
        /* _TODO */
      ), P = l ? n.error.bind(n, ...a) : e.bind(
        t,
        521
        /* _ERROR */
      ), B = c ? n.error.bind(n, ...a) : e.bind(
        t,
        529
        /* ERROR_DEV */
      ), q = f ? n.error.bind(n, ...a) : e.bind(
        t,
        545
        /* ERROR_PUBLIC */
      ), Y = v ? n.warn.bind(n, ...i) : e.bind(
        t,
        268
        /* _KAPOW */
      ), _e = d ? n.warn.bind(n, ...a) : e.bind(
        t,
        265
        /* _WARN */
      ), ye = h ? n.warn.bind(n, ...a) : e.bind(
        t,
        273
        /* WARN_DEV */
      ), be = _ ? n.warn.bind(n, ...a) : e.bind(
        t,
        273
        /* WARN_DEV */
      ), me = y ? n.info.bind(n, ...a) : e.bind(
        t,
        137
        /* _DEBUG */
      ), Pe = g ? n.info.bind(n, ...a) : e.bind(
        t,
        145
        /* DEBUG_DEV */
      ), I = b ? n.debug.bind(n, ...a) : e.bind(
        t,
        73
        /* _TRACE */
      ), V = R ? n.debug.bind(n, ...a) : e.bind(
        t,
        81
        /* TRACE_DEV */
      ), O = {
        _hmm: F,
        _todo: M,
        _error: P,
        errorDev: B,
        errorPublic: q,
        _kapow: Y,
        _warn: _e,
        warnDev: ye,
        warnPublic: be,
        _debug: me,
        debugDev: Pe,
        _trace: I,
        traceDev: V,
        lazy: {
          _hmm: s ? w(F) : F,
          _todo: u ? w(M) : M,
          _error: l ? w(P) : P,
          errorDev: c ? w(B) : B,
          errorPublic: f ? w(q) : q,
          _kapow: v ? w(Y) : Y,
          _warn: d ? w(_e) : _e,
          warnDev: h ? w(ye) : ye,
          warnPublic: _ ? w(be) : be,
          _debug: y ? w(me) : me,
          debugDev: g ? w(Pe) : Pe,
          _trace: b ? w(I) : I,
          traceDev: R ? w(V) : V
        },
        //
        named: o,
        utilFor: {
          internal() {
            return {
              debug: O._debug,
              error: O._error,
              warn: O._warn,
              trace: O._trace,
              named(ne, ae) {
                return O.named(ne, ae).utilFor.internal();
              }
            };
          },
          dev() {
            return {
              debug: O.debugDev,
              error: O.errorDev,
              warn: O.warnDev,
              trace: O.traceDev,
              named(ne, ae) {
                return O.named(ne, ae).utilFor.dev();
              }
            };
          },
          public() {
            return {
              error: O.errorPublic,
              warn: O.warnPublic,
              debug(ne, ae) {
                O._warn('(public "debug" filtered out) '.concat(ne), ae);
              },
              trace(ne, ae) {
                O._warn('(public "trace" filtered out) '.concat(ne), ae);
              },
              named(ne, ae) {
                return O.named(ne, ae).utilFor.public();
              }
            };
          }
        }
      };
      return O;
    }
    var ha = da(console, {});
    ha.configureLogging({
      dev: !0,
      min: 64
      /* TRACE */
    });
    var ft = ha.getLogger().named("Theatre.js (default logger)").utilFor.dev(), va = /* @__PURE__ */ new WeakMap();
    function Dh(e) {
      const t = va.get(e);
      if (t)
        return t;
      const r = /* @__PURE__ */ new Map();
      return va.set(e, r), ga([], e, r), r;
    }
    function ga(e, t, r) {
      for (const [n, a] of Object.entries(t.props))
        if (!ct(a)) {
          const i = [...e, n];
          r.set(JSON.stringify(i), r.size), _a(i, a, r);
        }
      for (const [n, a] of Object.entries(t.props))
        if (ct(a)) {
          const i = [...e, n];
          r.set(JSON.stringify(i), r.size), _a(i, a, r);
        }
    }
    function _a(e, t, r) {
      if (t.type === "compound")
        ga(e, t, r);
      else {
        if (t.type === "enum")
          throw new Error("Enums aren't supported yet");
        r.set(JSON.stringify(e), r.size);
      }
    }
    function ya(e) {
      return typeof e == "object" && e !== null && Object.keys(e).length === 0;
    }
    var xh = class {
      constructor(e, t, r, n, a) {
        this.sheetTemplate = e, p(this, "address"), p(this, "type", "Theatre_SheetObjectTemplate"), p(this, "_config"), p(this, "_temp_actions_atom"), p(this, "_cache", new xt()), p(this, "project"), p(this, "pointerToSheetState"), p(this, "pointerToStaticOverrides"), this.address = J(C({}, e.address), { objectKey: t }), this._config = new E.Atom(n), this._temp_actions_atom = new E.Atom(a), this.project = e.project, this.pointerToSheetState = this.sheetTemplate.project.pointers.historic.sheetsById[this.address.sheetId], this.pointerToStaticOverrides = this.pointerToSheetState.staticOverrides.byObject[this.address.objectKey];
      }
      get staticConfig() {
        return this._config.get();
      }
      get configPointer() {
        return this._config.pointer;
      }
      get _temp_actions() {
        return this._temp_actions_atom.get();
      }
      get _temp_actionsPointer() {
        return this._temp_actions_atom.pointer;
      }
      createInstance(e, t, r) {
        return this._config.set(r), new Sh(e, this, t);
      }
      reconfigure(e) {
        this._config.set(e);
      }
      /**
       * The `actions` api is temporary until we implement events.
       */
      _temp_setActions(e) {
        this._temp_actions_atom.set(e);
      }
      /**
       * Returns the default values (all defaults are read from the config)
       */
      getDefaultValues() {
        return this._cache.get(
          "getDefaultValues()",
          () => (0, E.prism)(() => {
            const e = (0, E.val)(this.configPointer);
            return Ps(e);
          })
        );
      }
      /**
       * Returns values that are set statically (ie, not sequenced, and not defaults)
       */
      getStaticValues() {
        return this._cache.get(
          "getStaticValues",
          () => (0, E.prism)(() => {
            var e;
            const t = (e = (0, E.val)(this.pointerToStaticOverrides)) != null ? e : {};
            return (0, E.val)(this.configPointer).deserializeAndSanitize(t) || {};
          })
        );
      }
      /**
       * Filters through the sequenced tracks and returns those tracks who are valid
       * according to the object's prop types, then sorted in the same order as the config
       *
       * Returns an array.
       */
      getArrayOfValidSequenceTracks() {
        return this._cache.get(
          "getArrayOfValidSequenceTracks",
          () => (0, E.prism)(() => {
            const e = this.project.pointers.historic.sheetsById[this.address.sheetId], t = (0, E.val)(
              e.sequence.tracksByObject[this.address.objectKey].trackIdByPropPath
            );
            if (!t)
              return Ot;
            const r = [];
            if (!t)
              return Ot;
            const n = (0, E.val)(this.configPointer), a = Object.entries(t);
            for (const [o, s] of a) {
              const u = Eh(o);
              if (!u)
                continue;
              const l = nr(n, u);
              l && wh(l) && r.push({ pathToProp: u, trackId: s });
            }
            const i = Dh(n);
            return r.sort((o, s) => {
              const u = o.pathToProp, l = s.pathToProp, c = i.get(JSON.stringify(u)), f = i.get(JSON.stringify(l));
              return c > f ? 1 : -1;
            }), r.length === 0 ? Ot : r;
          })
        );
      }
      /**
       * Filters through the sequenced tracks those tracks that are valid
       * according to the object's prop types.
       *
       * Returns a map.
       *
       * Not available in core.
       */
      getMapOfValidSequenceTracks_forStudio() {
        return this._cache.get(
          "getMapOfValidSequenceTracks_forStudio",
          () => (0, E.prism)(() => {
            const e = (0, E.val)(this.getArrayOfValidSequenceTracks());
            let t = {};
            for (const { pathToProp: r, trackId: n } of e)
              ms(t, r, n);
            return t;
          })
        );
      }
      /**
       * @returns The static overrides that are not sequenced. Returns undefined if there are no static overrides,
       * or if all those static overrides are sequenced.
       */
      getStaticButNotSequencedOverrides() {
        return this._cache.get(
          "getStaticButNotSequencedOverrides",
          () => (0, E.prism)(() => {
            const e = (0, E.val)(this.getStaticValues()), t = (0, E.val)(
              this.getArrayOfValidSequenceTracks()
            ), r = pd(e);
            for (const { pathToProp: n } of t) {
              fa(r, n);
              let a = n.slice(0, -1);
              for (; a.length > 0; ) {
                const i = Jr(
                  r,
                  a
                );
                if (!ya(i))
                  break;
                fa(r, a), a = a.slice(0, -1);
              }
            }
            if (!ya(r))
              return r;
          })
        );
      }
      getDefaultsAtPointer(e) {
        const { path: t } = (0, E.getPointerParts)(e), r = this.getDefaultValues().getValue();
        return Jr(r, t);
      }
    };
    function Eh(e) {
      try {
        return JSON.parse(e);
      } catch {
        ft.warn(
          "property ".concat(JSON.stringify(
            e
          ), " cannot be parsed. Skipping.")
        );
        return;
      }
    }
    var ba = D(), Rh = Th(
      (e) => (
        // we're using JSON.stringify here, but we could use a faster alternative.
        // If you happen to do that, first make sure no `PathToProp_Encoded` is ever
        // used in the store, otherwise you'll have to write a migration.
        JSON.stringify(e)
      )
    );
    $e(ii());
    var Mh = class extends Error {
    }, Ve = class extends Mh {
    }, ma = D(), Bh = D(), Lh = D(), x = D();
    function ie() {
      let e, t;
      const r = new Promise((a, i) => {
        e = (o) => {
          a(o), n.status = "resolved";
        }, t = (o) => {
          i(o), n.status = "rejected";
        };
      }), n = {
        resolve: e,
        reject: t,
        promise: r,
        status: "pending"
      };
      return n;
    }
    var Fh = () => {
    }, dt = Fh, kh = D(), Nh = class {
      constructor() {
        p(this, "_stopPlayCallback", dt), p(this, "_state", new kh.Atom({
          position: 0,
          playing: !1
        })), p(this, "statePointer"), this.statePointer = this._state.pointer;
      }
      destroy() {
      }
      pause() {
        this._stopPlayCallback(), this.playing = !1, this._stopPlayCallback = dt;
      }
      gotoPosition(e) {
        this._updatePositionInState(e);
      }
      _updatePositionInState(e) {
        this._state.setByPointer((t) => t.position, e);
      }
      getCurrentPosition() {
        return this._state.get().position;
      }
      get playing() {
        return this._state.get().playing;
      }
      set playing(e) {
        this._state.setByPointer((t) => t.playing, e);
      }
      play(e, t, r, n, a) {
        this.playing && this.pause(), this.playing = !0;
        const i = t[1] - t[0];
        {
          const d = this.getCurrentPosition();
          d < t[0] || d > t[1] ? n === "normal" || n === "alternate" ? this._updatePositionInState(t[0]) : (n === "reverse" || n === "alternateReverse") && this._updatePositionInState(t[1]) : n === "normal" || n === "alternate" ? d === t[1] && this._updatePositionInState(t[0]) : d === t[0] && this._updatePositionInState(t[1]);
        }
        const o = ie(), s = a.time, u = i * e;
        let l = this.getCurrentPosition() - t[0];
        (n === "reverse" || n === "alternateReverse") && (l = t[1] - this.getCurrentPosition());
        const c = (d) => {
          const h = Math.max(
            d - s,
            0
          ) / 1e3, _ = Math.min(
            h * r + l,
            u
          );
          if (_ !== u) {
            const y = Math.floor(_ / i);
            let g = _ / i % 1 * i;
            if (n !== "normal")
              if (n === "reverse")
                g = i - g;
              else {
                const b = y % 2 === 0;
                n === "alternate" ? b || (g = i - g) : b && (g = i - g);
              }
            this._updatePositionInState(g + t[0]), f();
          } else {
            if (n === "normal")
              this._updatePositionInState(t[1]);
            else if (n === "reverse")
              this._updatePositionInState(t[0]);
            else {
              const y = (e - 1) % 2 === 0;
              n === "alternate" ? y ? this._updatePositionInState(t[1]) : this._updatePositionInState(t[0]) : y ? this._updatePositionInState(t[0]) : this._updatePositionInState(t[1]);
            }
            this.playing = !1, o.resolve(!0);
          }
        };
        this._stopPlayCallback = () => {
          a.offThisOrNextTick(c), a.offNextTick(c), this.playing && o.resolve(!1);
        };
        const f = () => a.onNextTick(c);
        return a.onThisOrNextTick(c), o.promise;
      }
      playDynamicRange(e, t) {
        this.playing && this.pause(), this.playing = !0;
        const r = ie(), n = e.keepHot();
        r.promise.then(n, n);
        let a = t.time;
        const i = (s) => {
          const u = Math.max(
            s - a,
            0
          );
          a = s;
          const l = u / 1e3, c = this.getCurrentPosition(), f = e.getValue();
          if (c < f[0] || c > f[1])
            this.gotoPosition(f[0]);
          else {
            let d = c + l;
            d > f[1] && (d = f[0] + (d - f[1])), this.gotoPosition(d);
          }
          o();
        };
        this._stopPlayCallback = () => {
          t.offThisOrNextTick(i), t.offNextTick(i), r.resolve(!1);
        };
        const o = () => t.onNextTick(i);
        return t.onThisOrNextTick(i), r.promise;
      }
    }, Uh = D(), zh = "__TheatreJS_StudioBundle", ar = "__TheatreJS_CoreBundle", qh = "__TheatreJS_Notifications", pt = (e) => (...t) => {
      var r;
      switch (e) {
        case "success": {
          ft.debug(t.slice(0, 2).join(`
`));
          break;
        }
        case "info": {
          ft.debug(t.slice(0, 2).join(`
`));
          break;
        }
        case "warning": {
          ft.warn(t.slice(0, 2).join(`
`));
          break;
        }
      }
      return typeof window < "u" ? (
        // @ts-ignore
        (r = window[qh]) == null ? void 0 : r.notify[e](...t)
      ) : void 0;
    }, Ie = {
      warning: pt("warning"),
      success: pt("success"),
      info: pt("info"),
      error: pt("error")
    };
    typeof window < "u" && (window.addEventListener("error", (e) => {
      Ie.error(
        "An error occurred",
        "<pre>".concat(e.message, `</pre>

See **console** for details.`)
      );
    }), window.addEventListener("unhandledrejection", (e) => {
      Ie.error(
        "An error occurred",
        "<pre>".concat(e.reason, `</pre>

See **console** for details.`)
      );
    }));
    var Vh = class {
      constructor(e, t, r) {
        this._decodedBuffer = e, this._audioContext = t, this._nodeDestination = r, p(this, "_mainGain"), p(this, "_state", new Uh.Atom({
          position: 0,
          playing: !1
        })), p(this, "statePointer"), p(this, "_stopPlayCallback", dt), this.statePointer = this._state.pointer, this._mainGain = this._audioContext.createGain(), this._mainGain.connect(this._nodeDestination);
      }
      playDynamicRange(e, t) {
        const r = ie();
        this._playing && this.pause(), this._playing = !0;
        let n;
        const a = () => {
          n == null || n(), n = this._loopInRange(e.getValue(), t).stop;
        }, i = e.onStale(a);
        return a(), this._stopPlayCallback = () => {
          n == null || n(), i(), r.resolve(!1);
        }, r.promise;
      }
      _loopInRange(e, t) {
        let n = this.getCurrentPosition();
        const a = e[1] - e[0];
        n < e[0] || n > e[1] ? this._updatePositionInState(e[0]) : n === e[1] && this._updatePositionInState(e[0]), n = this.getCurrentPosition();
        const i = this._audioContext.createBufferSource();
        i.buffer = this._decodedBuffer, i.connect(this._mainGain), i.playbackRate.value = 1, i.loop = !0, i.loopStart = e[0], i.loopEnd = e[1];
        const o = t.time;
        let s = n - e[0];
        i.start(0, n);
        const u = (f) => {
          let _ = (Math.max(
            f - o,
            0
          ) / 1e3 * 1 + s) / a % 1 * a;
          this._updatePositionInState(_ + e[0]), l();
        }, l = () => t.onNextTick(u);
        return t.onThisOrNextTick(u), { stop: () => {
          i.stop(), i.disconnect(), t.offThisOrNextTick(u), t.offNextTick(u);
        } };
      }
      get _playing() {
        return this._state.get().playing;
      }
      set _playing(e) {
        this._state.setByPointer((t) => t.playing, e);
      }
      destroy() {
      }
      pause() {
        this._stopPlayCallback(), this._playing = !1, this._stopPlayCallback = dt;
      }
      gotoPosition(e) {
        this._updatePositionInState(e);
      }
      _updatePositionInState(e) {
        this._state.reduce((t) => J(C({}, t), { position: e }));
      }
      getCurrentPosition() {
        return this._state.get().position;
      }
      play(e, t, r, n, a) {
        this._playing && this.pause(), this._playing = !0;
        let i = this.getCurrentPosition();
        const o = t[1] - t[0];
        if (n !== "normal")
          throw new Ve(
            'Audio-controlled sequences can only be played in the "normal" direction. ' + "'".concat(n, "' given.")
          );
        i < t[0] || i > t[1] ? this._updatePositionInState(t[0]) : i === t[1] && this._updatePositionInState(t[0]), i = this.getCurrentPosition();
        const s = ie(), u = this._audioContext.createBufferSource();
        u.buffer = this._decodedBuffer, u.connect(this._mainGain), u.playbackRate.value = r, e > 1e3 && (Ie.warning(
          "Can't play sequences with audio more than 1000 times",
          "The sequence will still play, but only 1000 times. The `iterationCount: ".concat(e, "` provided to `sequence.play()`\nis too high for a sequence with audio.\n\nTo fix this, either set `iterationCount` to a lower value, or remove the audio from the sequence."),
          [
            {
              url: "https://www.theatrejs.com/docs/latest/manual/audio",
              title: "Using Audio"
            },
            {
              url: "https://www.theatrejs.com/docs/latest/api/core#sequence.attachaudio",
              title: "Audio API"
            }
          ]
        ), e = 1e3), e > 1 && (u.loop = !0, u.loopStart = t[0], u.loopEnd = t[1]);
        const l = a.time;
        let c = i - t[0];
        const f = o * e;
        u.start(0, i, f - c);
        const d = (_) => {
          const g = Math.max(
            _ - l,
            0
          ) / 1e3, b = Math.min(
            g * r + c,
            f
          );
          if (b !== f) {
            let R = b / o % 1 * o;
            this._updatePositionInState(R + t[0]), h();
          } else
            this._updatePositionInState(t[1]), this._playing = !1, v(), s.resolve(!0);
        }, v = () => {
          u.stop(), u.disconnect();
        };
        this._stopPlayCallback = () => {
          v(), a.offThisOrNextTick(d), a.offNextTick(d), this._playing && s.resolve(!1);
        };
        const h = () => a.onNextTick(d);
        return a.onThisOrNextTick(d), s.promise;
      }
    }, Gh = D(), Pa = 0;
    function ir(e) {
      var t;
      const r = (o) => {
        n.tick(o);
      }, n = new Gh.Ticker({
        onActive() {
          var o;
          (o = e == null ? void 0 : e.start) == null || o.call(e);
        },
        onDormant() {
          var o;
          (o = e == null ? void 0 : e.stop) == null || o.call(e);
        }
      }), a = {
        tick: r,
        id: Pa++,
        name: (t = e == null ? void 0 : e.name) != null ? t : "CustomRafDriver-".concat(Pa),
        type: "Theatre_RafDriver_PublicAPI"
      }, i = {
        type: "Theatre_RafDriver_PrivateAPI",
        publicApi: a,
        ticker: n,
        start: e == null ? void 0 : e.start,
        stop: e == null ? void 0 : e.stop
      };
      return Re(a, i), a;
    }
    function Hh() {
      let e = null;
      const n = ir({ name: "DefaultCoreRafDriver", start: () => {
        if (typeof window < "u") {
          const a = (i) => {
            n.tick(i), e = window.requestAnimationFrame(a);
          };
          e = window.requestAnimationFrame(a);
        } else
          n.tick(0), setTimeout(() => n.tick(1), 0);
      }, stop: () => {
        typeof window < "u" && e !== null && window.cancelAnimationFrame(e);
      } });
      return n;
    }
    var ht;
    function Ta() {
      return ht || Kh(Hh()), ht;
    }
    function wa() {
      return Ta().ticker;
    }
    function Kh(e) {
      if (ht)
        throw new Error("`setCoreRafDriver()` is already called.");
      ht = m(e);
    }
    var Wh = class {
      get type() {
        return "Theatre_Sequence_PublicAPI";
      }
      /**
       * @internal
       */
      constructor(e) {
        Re(this, e);
      }
      play(e) {
        const t = m(this);
        if (t._project.isReady()) {
          const r = e != null && e.rafDriver ? m(e.rafDriver).ticker : wa();
          return t.play(e ?? {}, r);
        } else {
          const r = ie();
          return r.resolve(!0), r.promise;
        }
      }
      pause() {
        m(this).pause();
      }
      get position() {
        return m(this).position;
      }
      set position(e) {
        m(this).position = e;
      }
      __experimental_getKeyframes(e) {
        return m(this).getKeyframesOfSimpleProp(e);
      }
      async attachAudio(e) {
        const { audioContext: t, destinationNode: r, decodedBuffer: n, gainNode: a } = await Jh(e), i = new Vh(
          n,
          t,
          a
        );
        return m(this).replacePlaybackController(i), { audioContext: t, destinationNode: r, decodedBuffer: n, gainNode: a };
      }
      get pointer() {
        return m(this).pointer;
      }
    };
    async function Jh(e) {
      function t() {
        if (e.audioContext)
          return Promise.resolve(e.audioContext);
        const l = new AudioContext();
        return l.state === "running" || typeof window > "u" ? Promise.resolve(l) : new Promise((c) => {
          const f = () => {
            l.resume().catch((h) => {
              console.error(h);
            });
          }, d = [
            "mousedown",
            "keydown",
            "touchstart"
          ], v = { capture: !0, passive: !1 };
          d.forEach((h) => {
            window.addEventListener(h, f, v);
          }), l.addEventListener("statechange", () => {
            l.state === "running" && (d.forEach((h) => {
              window.removeEventListener(h, f, v);
            }), c(l));
          });
        });
      }
      async function r() {
        if (e.source instanceof AudioBuffer)
          return e.source;
        const l = ie();
        if (typeof e.source != "string")
          throw new Error(
            "Error validating arguments to sequence.attachAudio(). args.source must either be a string or an instance of AudioBuffer."
          );
        let c;
        try {
          c = await fetch(e.source);
        } catch (h) {
          throw console.error(h), new Error(
            "Could not fetch '".concat(e.source, "'. Network error logged above.")
          );
        }
        let f;
        try {
          f = await c.arrayBuffer();
        } catch (h) {
          throw console.error(h), new Error("Could not read '".concat(e.source, "' as an arrayBuffer."));
        }
        (await n).decodeAudioData(
          f,
          l.resolve,
          l.reject
        );
        let v;
        try {
          v = await l.promise;
        } catch (h) {
          throw console.error(h), new Error("Could not decode ".concat(e.source, " as an audio file."));
        }
        return v;
      }
      const n = t(), a = r(), [i, o] = await Promise.all([
        n,
        a
      ]), s = e.destinationNode || i.destination, u = i.createGain();
      return u.connect(s), {
        audioContext: i,
        decodedBuffer: o,
        gainNode: u,
        destinationNode: s
      };
    }
    var Xh = $h("Theatre_SheetObject");
    function $h(e) {
      return (t) => typeof t == "object" && !!t && t.type === e;
    }
    var Yh = class {
      constructor(e, t, r, n, a) {
        this._project = e, this._sheet = t, this._lengthD = r, this._subUnitsPerUnitD = n, p(this, "address"), p(this, "publicApi"), p(this, "_playbackControllerBox"), p(this, "_prismOfStatePointer"), p(this, "_positionD"), p(this, "_positionFormatterD"), p(this, "_playableRangeD"), p(this, "pointer", (0, Lh.pointer)({ root: this, path: [] })), p(this, "$$isPointerToPrismProvider", !0), p(this, "_logger"), p(this, "closestGridPosition", (i) => {
          const s = 1 / this.subUnitsPerUnit;
          return parseFloat(
            (Math.round(i / s) * s).toFixed(3)
          );
        }), this._logger = e._logger.named("Sheet", t.address.sheetId).named("Instance", t.address.sheetInstanceId), this.address = J(C({}, this._sheet.address), { sequenceName: "default" }), this.publicApi = new Wh(this), this._playbackControllerBox = new Bh.Atom(
          a ?? new Nh()
        ), this._prismOfStatePointer = (0, x.prism)(
          () => this._playbackControllerBox.prism.getValue().statePointer
        ), this._positionD = (0, x.prism)(() => {
          const i = this._prismOfStatePointer.getValue();
          return (0, x.val)(i.position);
        }), this._positionFormatterD = (0, x.prism)(() => {
          const i = (0, x.val)(this._subUnitsPerUnitD);
          return new Zh(i);
        });
      }
      get type() {
        return "Theatre_Sequence";
      }
      pointerToPrism(e) {
        const { path: t } = (0, ma.getPointerParts)(e);
        if (t.length === 0)
          return (0, x.prism)(() => ({
            length: (0, x.val)(this.pointer.length),
            playing: (0, x.val)(this.pointer.playing),
            position: (0, x.val)(this.pointer.position),
            subUnitsPerUnit: (0, x.val)(this.pointer.subUnitsPerUnit)
          }));
        if (t.length > 1)
          return (0, x.prism)(() => {
          });
        const [r] = t;
        return r === "length" ? this._lengthD : r === "subUnitsPerUnit" ? this._subUnitsPerUnitD : r === "position" ? this._positionD : r === "playing" ? (0, x.prism)(() => (0, x.val)(this._prismOfStatePointer.getValue().playing)) : (0, x.prism)(() => {
        });
      }
      /**
       * Takes a pointer to a property of a SheetObject and returns the keyframes of that property.
       *
       * Theoretically, this method can be called from inside a prism so it can be reactive.
       */
      getKeyframesOfSimpleProp(e) {
        const { path: t, root: r } = (0, ma.getPointerParts)(e);
        if (!Xh(r))
          throw new Ve(
            "Argument prop must be a pointer to a SheetObject property"
          );
        const n = (0, x.val)(
          this._project.pointers.historic.sheetsById[this._sheet.address.sheetId].sequence.tracksByObject[r.address.objectKey]
        );
        if (!n)
          return [];
        const { trackData: a, trackIdByPropPath: i } = n, o = Rh(t), s = i[o];
        if (!s)
          return [];
        const u = a[s];
        return u ? u.keyframes : [];
      }
      get positionFormatter() {
        return this._positionFormatterD.getValue();
      }
      get prismOfStatePointer() {
        return this._prismOfStatePointer;
      }
      get length() {
        return this._lengthD.getValue();
      }
      get positionPrism() {
        return this._positionD;
      }
      get position() {
        return this._playbackControllerBox.get().getCurrentPosition();
      }
      get subUnitsPerUnit() {
        return this._subUnitsPerUnitD.getValue();
      }
      get positionSnappedToGrid() {
        return this.closestGridPosition(this.position);
      }
      set position(e) {
        let t = e;
        this.pause(), t > this.length && (t = this.length);
        const r = this.length;
        this._playbackControllerBox.get().gotoPosition(t > r ? r : t);
      }
      getDurationCold() {
        return this._lengthD.getValue();
      }
      get playing() {
        return (0, x.val)(this._playbackControllerBox.get().statePointer.playing);
      }
      _makeRangeFromSequenceTemplate() {
        return (0, x.prism)(() => [0, (0, x.val)(this._lengthD)]);
      }
      /**
       * Controls the playback within a range. Repeats infinitely unless stopped.
       *
       * @remarks
       *   One use case for this is to play the playback within the focus range.
       *
       * @param rangeD - The prism that contains the range that will be used for the playback
       *
       * @returns  a promise that gets rejected if the playback stopped for whatever reason
       *
       */
      playDynamicRange(e, t) {
        return this._playbackControllerBox.get().playDynamicRange(e, t);
      }
      async play(e, t) {
        const r = this.length, n = e && e.range ? e.range : [0, r], a = e && typeof e.iterationCount == "number" ? e.iterationCount : 1, i = e && typeof e.rate < "u" ? e.rate : 1, o = e && e.direction ? e.direction : "normal";
        return await this._play(
          a,
          [n[0], n[1]],
          i,
          o,
          t
        );
      }
      _play(e, t, r, n, a) {
        return this._playbackControllerBox.get().play(e, t, r, n, a);
      }
      pause() {
        this._playbackControllerBox.get().pause();
      }
      replacePlaybackController(e) {
        this.pause();
        const t = this._playbackControllerBox.get();
        this._playbackControllerBox.set(e);
        const r = t.getCurrentPosition();
        t.destroy(), e.gotoPosition(r);
      }
    }, Zh = class {
      constructor(e) {
        this._fps = e;
      }
      formatSubUnitForGrid(e) {
        const t = e % 1, r = 1 / this._fps;
        return Math.round(t / r) + "f";
      }
      formatFullUnitForGrid(e) {
        let t = e, r = "";
        if (t >= De) {
          const a = Math.floor(t / De);
          r += a + "h", t = t % De;
        }
        if (t >= pe) {
          const a = Math.floor(t / pe);
          r += a + "m", t = t % pe;
        }
        if (t >= de) {
          const a = Math.floor(t / de);
          r += a + "s", t = t % de;
        }
        const n = 1 / this._fps;
        if (t >= n) {
          const a = Math.floor(t / n);
          r += a + "f", t = t % n;
        }
        return r.length === 0 ? "0s" : r;
      }
      formatForPlayhead(e) {
        let t = e, r = "";
        if (t >= De) {
          const a = Math.floor(t / De);
          r += qe(a.toString(), 2, "0") + "h", t = t % De;
        }
        if (t >= pe) {
          const a = Math.floor(t / pe);
          r += qe(a.toString(), 2, "0") + "m", t = t % pe;
        } else r.length > 0 && (r += "00m");
        if (t >= de) {
          const a = Math.floor(t / de);
          r += qe(a.toString(), 2, "0") + "s", t = t % de;
        } else
          r += "00s";
        const n = 1 / this._fps;
        if (t >= n) {
          const a = Math.round(t / n);
          r += qe(a.toString(), 2, "0") + "f", t = t % n;
        } else t / n > 0.98 ? (r += qe("1", 2, "0") + "f", t = t % n) : r += "00f";
        return r.length === 0 ? "00s00f" : r;
      }
      formatBasic(e) {
        return e.toFixed(2) + "s";
      }
    }, de = 1, pe = de * 60, De = pe * 60, or = {};
    wt(or, {
      boolean: () => Da,
      compound: () => ur,
      file: () => ov,
      image: () => uv,
      number: () => Ia,
      rgba: () => pv,
      string: () => xa,
      stringLiteral: () => yv
    });
    function Sa(e, t) {
      return e.length <= t ? e : e.substr(0, t - 3) + "...";
    }
    var Qh = (e) => typeof e == "string" ? 'string("'.concat(Sa(e, 10), '")') : typeof e == "number" ? "number(".concat(Sa(String(e), 10), ")") : e === null ? "null" : e === void 0 ? "undefined" : typeof e == "boolean" ? String(e) : Array.isArray(e) ? "array" : typeof e == "object" ? "object" : "unknown", Oa = Qh;
    function ev(e, {
      /** Alpha is usually an optional value for most hex inputs, so if it's opaque, we can omit its value. */
      removeAlphaIfOpaque: t = !1
    } = {}) {
      const r = (e.a * 255 | 256).toString(16).slice(1), n = (e.r * 255 | 256).toString(16).slice(1) + (e.g * 255 | 256).toString(16).slice(1) + (e.b * 255 | 256).toString(16).slice(1) + (t && r === "ff" ? "" : r);
      return "#".concat(n);
    }
    function sr(e) {
      return J(C({}, e), {
        toString() {
          return ev(this, { removeAlphaIfOpaque: !0 });
        }
      });
    }
    function tv(e) {
      return Object.fromEntries(
        Object.entries(e).map(([t, r]) => [t, On(r, 0, 1)])
      );
    }
    function rv(e) {
      function t(r) {
        return r >= 31308e-7 ? 1.055 * r ** (1 / 2.4) - 0.055 : 12.92 * r;
      }
      return tv({
        r: t(e.r),
        g: t(e.g),
        b: t(e.b),
        a: e.a
      });
    }
    function Aa(e) {
      function t(r) {
        return r >= 0.04045 ? ((r + 0.055) / (1 + 0.055)) ** 2.4 : r / 12.92;
      }
      return {
        r: t(e.r),
        g: t(e.g),
        b: t(e.b),
        a: e.a
      };
    }
    function ja(e) {
      let t = 0.4122214708 * e.r + 0.5363325363 * e.g + 0.0514459929 * e.b, r = 0.2119034982 * e.r + 0.6806995451 * e.g + 0.1073969566 * e.b, n = 0.0883024619 * e.r + 0.2817188376 * e.g + 0.6299787005 * e.b, a = Math.cbrt(t), i = Math.cbrt(r), o = Math.cbrt(n);
      return {
        L: 0.2104542553 * a + 0.793617785 * i - 0.0040720468 * o,
        a: 1.9779984951 * a - 2.428592205 * i + 0.4505937099 * o,
        b: 0.0259040371 * a + 0.7827717662 * i - 0.808675766 * o,
        alpha: e.a
      };
    }
    function nv(e) {
      let t = e.L + 0.3963377774 * e.a + 0.2158037573 * e.b, r = e.L - 0.1055613458 * e.a - 0.0638541728 * e.b, n = e.L - 0.0894841775 * e.a - 1.291485548 * e.b, a = t * t * t, i = r * r * r, o = n * n * n;
      return {
        r: 4.0767416621 * a - 3.3077115913 * i + 0.2309699292 * o,
        g: -1.2684380046 * a + 2.6097574011 * i - 0.3413193965 * o,
        b: -0.0041960863 * a - 0.7034186147 * i + 1.707614701 * o,
        a: e.alpha
      };
    }
    var te = Symbol("TheatrePropType_Basic");
    function Ca(e) {
      return typeof e == "object" && !!e && e[te] === "TheatrePropType";
    }
    function av(e) {
      if (typeof e == "number")
        return Ia(e);
      if (typeof e == "boolean")
        return Da(e);
      if (typeof e == "string")
        return xa(e);
      if (typeof e == "object" && e) {
        if (Ca(e))
          return e;
        if (bl(e))
          return ur(e);
        throw new Ve(
          "This value is not a valid prop type: ".concat(Oa(e))
        );
      } else
        throw new Ve(
          "This value is not a valid prop type: ".concat(Oa(e))
        );
    }
    function iv(e) {
      const t = {};
      for (const r of Object.keys(e)) {
        const n = e[r];
        Ca(n) ? t[r] = n : t[r] = av(n);
      }
      return t;
    }
    var ur = (e, t = {}) => {
      const r = iv(e), n = /* @__PURE__ */ new WeakMap();
      return {
        type: "compound",
        props: r,
        valueType: null,
        [te]: "TheatrePropType",
        label: t.label,
        default: Wp(r, (i) => i.default),
        deserializeAndSanitize: (i) => {
          if (typeof i != "object" || !i)
            return;
          if (n.has(i))
            return n.get(i);
          const o = {};
          let s = !1;
          for (const [u, l] of Object.entries(r))
            if (Object.prototype.hasOwnProperty.call(i, u)) {
              const c = l.deserializeAndSanitize(
                i[u]
              );
              c != null && (s = !0, o[u] = c);
            }
          if (n.set(i, o), s)
            return o;
        }
      };
    }, ov = (e, t = {}) => {
      const r = (n, a, i) => {
        var o;
        return {
          type: "file",
          id: ((o = t.interpolate) != null ? o : Ge)(n.id, a.id, i)
        };
      };
      return {
        type: "file",
        default: { type: "file", id: e },
        valueType: null,
        [te]: "TheatrePropType",
        label: t.label,
        interpolate: r,
        deserializeAndSanitize: sv
      };
    }, sv = (e) => {
      if (!e)
        return;
      let t = !0;
      if (typeof e.id != "string" && ![null, void 0].includes(e.id) && (t = !1), e.type !== "file" && (t = !1), !!t)
        return e;
    }, uv = (e, t = {}) => {
      const r = (n, a, i) => {
        var o;
        return {
          type: "image",
          id: ((o = t.interpolate) != null ? o : Ge)(n.id, a.id, i)
        };
      };
      return {
        type: "image",
        default: { type: "image", id: e },
        valueType: null,
        [te]: "TheatrePropType",
        label: t.label,
        interpolate: r,
        deserializeAndSanitize: lv
      };
    }, lv = (e) => {
      if (!e)
        return;
      let t = !0;
      if (typeof e.id != "string" && ![null, void 0].includes(e.id) && (t = !1), e.type !== "image" && (t = !1), !!t)
        return e;
    }, Ia = (e, t = {}) => {
      var r;
      return J(C({
        type: "number",
        valueType: 0,
        default: e,
        [te]: "TheatrePropType"
      }, t || {}), {
        label: t.label,
        nudgeFn: (r = t.nudgeFn) != null ? r : bv,
        nudgeMultiplier: typeof t.nudgeMultiplier == "number" ? t.nudgeMultiplier : void 0,
        interpolate: dv,
        deserializeAndSanitize: cv(t.range)
      });
    }, cv = (e) => e ? (t) => {
      if (typeof t == "number" && isFinite(t))
        return On(t, e[0], e[1]);
    } : fv, fv = (e) => typeof e == "number" && isFinite(e) ? e : void 0, dv = (e, t, r) => e + r * (t - e), pv = (e = { r: 0, g: 0, b: 0, a: 1 }, t = {}) => {
      const r = {};
      for (const n of ["r", "g", "b", "a"])
        r[n] = Math.min(
          Math.max(e[n], 0),
          1
        );
      return {
        type: "rgba",
        valueType: null,
        default: sr(r),
        [te]: "TheatrePropType",
        label: t.label,
        interpolate: vv,
        deserializeAndSanitize: hv
      };
    }, hv = (e) => {
      if (!e)
        return;
      let t = !0;
      for (const n of ["r", "g", "b", "a"])
        (!Object.prototype.hasOwnProperty.call(e, n) || typeof e[n] != "number") && (t = !1);
      if (!t)
        return;
      const r = {};
      for (const n of ["r", "g", "b", "a"])
        r[n] = Math.min(
          Math.max(e[n], 0),
          1
        );
      return sr(r);
    }, vv = (e, t, r) => {
      const n = ja(Aa(e)), a = ja(Aa(t)), i = {
        L: (1 - r) * n.L + r * a.L,
        a: (1 - r) * n.a + r * a.a,
        b: (1 - r) * n.b + r * a.b,
        alpha: (1 - r) * n.alpha + r * a.alpha
      }, o = rv(nv(i));
      return sr(o);
    }, Da = (e, t = {}) => {
      var r;
      return {
        type: "boolean",
        default: e,
        valueType: null,
        [te]: "TheatrePropType",
        label: t.label,
        interpolate: (r = t.interpolate) != null ? r : Ge,
        deserializeAndSanitize: gv
      };
    }, gv = (e) => typeof e == "boolean" ? e : void 0;
    function Ge(e) {
      return e;
    }
    var xa = (e, t = {}) => {
      var r;
      return {
        type: "string",
        default: e,
        valueType: null,
        [te]: "TheatrePropType",
        label: t.label,
        interpolate: (r = t.interpolate) != null ? r : Ge,
        deserializeAndSanitize: _v
      };
    };
    function _v(e) {
      return typeof e == "string" ? e : void 0;
    }
    function yv(e, t, r = {}) {
      var n, a;
      return {
        type: "stringLiteral",
        default: e,
        valuesAndLabels: C({}, t),
        [te]: "TheatrePropType",
        valueType: null,
        as: (n = r.as) != null ? n : "menu",
        label: r.label,
        interpolate: (a = r.interpolate) != null ? a : Ge,
        deserializeAndSanitize(i) {
          if (typeof i == "string" && Object.prototype.hasOwnProperty.call(t, i))
            return i;
        }
      };
    }
    var bv = ({
      config: e,
      deltaX: t,
      deltaFraction: r,
      magnitude: n
    }) => {
      var a;
      const { range: i } = e;
      return !e.nudgeMultiplier && i && !i.includes(1 / 0) && !i.includes(-1 / 0) ? r * (i[1] - i[0]) * n : t * n * ((a = e.nudgeMultiplier) != null ? a : 1);
    }, mv = (e) => e.replace(/^[\s\/]*/, "").replace(/[\s\/]*$/, "").replace(/\s*\/\s*/g, " / ");
    function vt(e, t) {
      return mv(e);
    }
    $e(Er());
    var Pv = class {
      get type() {
        return "Theatre_Sheet_PublicAPI";
      }
      /**
       * @internal
       */
      constructor(e) {
        Re(this, e);
      }
      object(e, t, r) {
        const n = m(this), a = vt(
          e
        ), i = n.getObject(a), o = null, s = r == null ? void 0 : r.__actions__THIS_API_IS_UNSTABLE_AND_WILL_CHANGE_IN_THE_NEXT_VERSION;
        if (i)
          return s && i.template._temp_setActions(s), i.publicApi;
        {
          const u = ur(t);
          return n.createObject(
            a,
            o,
            u,
            s
          ).publicApi;
        }
      }
      __experimental_getExistingObject(e) {
        const t = m(this), r = vt(
          e
        ), n = t.getObject(r);
        return n == null ? void 0 : n.publicApi;
      }
      get sequence() {
        return m(this).getSequence().publicApi;
      }
      get project() {
        return m(this).project.publicApi;
      }
      get address() {
        return C({}, m(this).address);
      }
      detachObject(e) {
        const t = m(this), r = vt(
          e
        );
        if (!t.getObject(r)) {
          Ie.warning(
            `Couldn't delete object "`.concat(r, '"'),
            'There is no object with key "'.concat(r, `".

To fix this, make sure you are calling \`sheet.deleteObject("`).concat(r, '")` with the correct key.')
          ), console.warn('Object key "'.concat(r, '" does not exist.'));
          return;
        }
        t.deleteObject(r);
      }
    }, He = D(), Tv = class {
      constructor(e, t) {
        this.template = e, this.instanceId = t, p(this, "_objects", new He.Atom({})), p(this, "_sequence"), p(this, "address"), p(this, "publicApi"), p(this, "project"), p(this, "objectsP", this._objects.pointer), p(this, "type", "Theatre_Sheet"), p(this, "_logger"), this._logger = e.project._logger.named("Sheet", t), this._logger._trace("creating sheet"), this.project = e.project, this.address = J(C({}, e.address), {
          sheetInstanceId: this.instanceId
        }), this.publicApi = new Pv(this);
      }
      /**
       * @remarks At some point, we have to reconcile the concept of "an object"
       * with that of "an element."
       */
      createObject(e, t, r, n = {}) {
        const i = this.template.getObjectTemplate(
          e,
          t,
          r,
          n
        ).createInstance(this, t, r);
        return this._objects.setByPointer((o) => o[e], i), i;
      }
      getObject(e) {
        return this._objects.get()[e];
      }
      deleteObject(e) {
        this._objects.reduce((t) => {
          const r = C({}, t);
          return delete r[e], r;
        });
      }
      getSequence() {
        if (!this._sequence) {
          const e = (0, He.prism)(() => {
            const r = (0, He.val)(
              this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.length
            );
            return wv(r);
          }), t = (0, He.prism)(() => {
            const r = (0, He.val)(
              this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.subUnitsPerUnit
            );
            return Sv(r);
          });
          this._sequence = new Yh(
            this.template.project,
            this,
            e,
            t
          );
        }
        return this._sequence;
      }
    }, wv = (e) => typeof e == "number" && isFinite(e) && e > 0 ? e : 10, Sv = (e) => typeof e == "number" && Hp(e) && e >= 1 && e <= 1e3 ? e : 30, Ov = class {
      constructor(e, t) {
        this.project = e, p(this, "type", "Theatre_SheetTemplate"), p(this, "address"), p(this, "_instances", new ba.Atom({})), p(this, "instancesP", this._instances.pointer), p(this, "_objectTemplates", new ba.Atom({})), p(this, "objectTemplatesP", this._objectTemplates.pointer), this.address = J(C({}, e.address), { sheetId: t });
      }
      getInstance(e) {
        let t = this._instances.get()[e];
        return t || (t = new Tv(this, e), this._instances.setByPointer((r) => r[e], t)), t;
      }
      getObjectTemplate(e, t, r, n) {
        let a = this._objectTemplates.get()[e];
        return a || (a = new xh(
          this,
          e,
          t,
          r,
          n
        ), this._objectTemplates.setByPointer((i) => i[e], a)), a;
      }
    }, lr = D(), Ea = D(), Av = (e) => new Promise((t) => setTimeout(t, e)), jv = Av;
    function G(e) {
      for (var t = arguments.length, r = Array(t > 1 ? t - 1 : 0), n = 1; n < t; n++)
        r[n - 1] = arguments[n];
      throw Error("[Immer] minified error nr: " + e + (r.length ? " " + r.map(function(a) {
        return "'" + a + "'";
      }).join(",") : "") + ". Find the full error at: https://bit.ly/3cXEKWf");
    }
    function he(e) {
      return !!e && !!e[L];
    }
    function ve(e) {
      return !!e && ((function(t) {
        if (!t || typeof t != "object")
          return !1;
        var r = Object.getPrototypeOf(t);
        if (r === null)
          return !0;
        var n = Object.hasOwnProperty.call(r, "constructor") && r.constructor;
        return n === Object || typeof n == "function" && Function.toString.call(n) === Lv;
      })(e) || Array.isArray(e) || !!e[qa] || !!e.constructor[qa] || fr(e) || dr(e));
    }
    function Cv(e) {
      return he(e) || G(23, e), e[L].t;
    }
    function Ke(e, t, r) {
      r === void 0 && (r = !1), xe(e) === 0 ? (r ? Object.keys : Sr)(e).forEach(function(n) {
        r && typeof n == "symbol" || t(n, e[n], e);
      }) : e.forEach(function(n, a) {
        return t(a, n, e);
      });
    }
    function xe(e) {
      var t = e[L];
      return t ? t.i > 3 ? t.i - 4 : t.i : Array.isArray(e) ? 1 : fr(e) ? 2 : dr(e) ? 3 : 0;
    }
    function cr(e, t) {
      return xe(e) === 2 ? e.has(t) : Object.prototype.hasOwnProperty.call(e, t);
    }
    function Iv(e, t) {
      return xe(e) === 2 ? e.get(t) : e[t];
    }
    function Ra(e, t, r) {
      var n = xe(e);
      n === 2 ? e.set(t, r) : n === 3 ? (e.delete(t), e.add(r)) : e[t] = r;
    }
    function Dv(e, t) {
      return e === t ? e !== 0 || 1 / e == 1 / t : e != e && t != t;
    }
    function fr(e) {
      return Mv && e instanceof Map;
    }
    function dr(e) {
      return Bv && e instanceof Set;
    }
    function ge(e) {
      return e.o || e.t;
    }
    function pr(e) {
      if (Array.isArray(e))
        return Array.prototype.slice.call(e);
      var t = Fv(e);
      delete t[L];
      for (var r = Sr(t), n = 0; n < r.length; n++) {
        var a = r[n], i = t[a];
        i.writable === !1 && (i.writable = !0, i.configurable = !0), (i.get || i.set) && (t[a] = { configurable: !0, writable: !0, enumerable: i.enumerable, value: e[a] });
      }
      return Object.create(Object.getPrototypeOf(e), t);
    }
    function hr(e, t) {
      return t === void 0 && (t = !1), vr(e) || he(e) || !ve(e) || (xe(e) > 1 && (e.set = e.add = e.clear = e.delete = xv), Object.freeze(e), t && Ke(e, function(r, n) {
        return hr(n, !0);
      }, !0)), e;
    }
    function xv() {
      G(2);
    }
    function vr(e) {
      return e == null || typeof e != "object" || Object.isFrozen(e);
    }
    function re(e) {
      var t = kv[e];
      return t || G(18, e), t;
    }
    function Ma() {
      return We;
    }
    function gr(e, t) {
      t && (re("Patches"), e.u = [], e.s = [], e.v = t);
    }
    function gt(e) {
      _r(e), e.p.forEach(Ev), e.p = null;
    }
    function _r(e) {
      e === We && (We = e.l);
    }
    function Ba(e) {
      return We = { p: [], l: We, h: e, m: !0, _: 0 };
    }
    function Ev(e) {
      var t = e[L];
      t.i === 0 || t.i === 1 ? t.j() : t.O = !0;
    }
    function yr(e, t) {
      t._ = t.p.length;
      var r = t.p[0], n = e !== void 0 && e !== r;
      return t.h.g || re("ES5").S(t, e, n), n ? (r[L].P && (gt(t), G(4)), ve(e) && (e = _t(t, e), t.l || yt(t, e)), t.u && re("Patches").M(r[L], e, t.u, t.s)) : e = _t(t, r, []), gt(t), t.u && t.v(t.u, t.s), e !== za ? e : void 0;
    }
    function _t(e, t, r) {
      if (vr(t))
        return t;
      var n = t[L];
      if (!n)
        return Ke(t, function(i, o) {
          return La(e, n, t, i, o, r);
        }, !0), t;
      if (n.A !== e)
        return t;
      if (!n.P)
        return yt(e, n.t, !0), n.t;
      if (!n.I) {
        n.I = !0, n.A._--;
        var a = n.i === 4 || n.i === 5 ? n.o = pr(n.k) : n.o;
        Ke(n.i === 3 ? new Set(a) : a, function(i, o) {
          return La(e, n, a, i, o, r);
        }), yt(e, a, !1), r && e.u && re("Patches").R(n, r, e.u, e.s);
      }
      return n.o;
    }
    function La(e, t, r, n, a, i) {
      if (he(a)) {
        var o = _t(e, a, i && t && t.i !== 3 && !cr(t.D, n) ? i.concat(n) : void 0);
        if (Ra(r, n, o), !he(o))
          return;
        e.m = !1;
      }
      if (ve(a) && !vr(a)) {
        if (!e.h.F && e._ < 1)
          return;
        _t(e, a), t && t.A.l || yt(e, a);
      }
    }
    function yt(e, t, r) {
      r === void 0 && (r = !1), e.h.F && e.m && hr(t, r);
    }
    function br(e, t) {
      var r = e[L];
      return (r ? ge(r) : e)[t];
    }
    function Fa(e, t) {
      if (t in e)
        for (var r = Object.getPrototypeOf(e); r; ) {
          var n = Object.getOwnPropertyDescriptor(r, t);
          if (n)
            return n;
          r = Object.getPrototypeOf(r);
        }
    }
    function mr(e) {
      e.P || (e.P = !0, e.l && mr(e.l));
    }
    function Pr(e) {
      e.o || (e.o = pr(e.t));
    }
    function Tr(e, t, r) {
      var n = fr(t) ? re("MapSet").N(t, r) : dr(t) ? re("MapSet").T(t, r) : e.g ? (function(a, i) {
        var o = Array.isArray(a), s = { i: o ? 1 : 0, A: i ? i.A : Ma(), P: !1, I: !1, D: {}, l: i, t: a, k: null, o: null, j: null, C: !1 }, u = s, l = bt;
        o && (u = [s], l = mt);
        var c = Proxy.revocable(u, l), f = c.revoke, d = c.proxy;
        return s.k = d, s.j = f, d;
      })(t, r) : re("ES5").J(t, r);
      return (r ? r.A : Ma()).p.push(n), n;
    }
    function Rv(e) {
      return he(e) || G(22, e), (function t(r) {
        if (!ve(r))
          return r;
        var n, a = r[L], i = xe(r);
        if (a) {
          if (!a.P && (a.i < 4 || !re("ES5").K(a)))
            return a.t;
          a.I = !0, n = ka(r, i), a.I = !1;
        } else
          n = ka(r, i);
        return Ke(n, function(o, s) {
          a && Iv(a.t, o) === s || Ra(n, o, t(s));
        }), i === 3 ? new Set(n) : n;
      })(e);
    }
    function ka(e, t) {
      switch (t) {
        case 2:
          return new Map(e);
        case 3:
          return Array.from(e);
      }
      return pr(e);
    }
    var Na, We, wr = typeof Symbol < "u" && typeof Symbol("x") == "symbol", Mv = typeof Map < "u", Bv = typeof Set < "u", Ua = typeof Proxy < "u" && Proxy.revocable !== void 0 && typeof Reflect < "u", za = wr ? Symbol.for("immer-nothing") : ((Na = {})["immer-nothing"] = !0, Na), qa = wr ? Symbol.for("immer-draftable") : "__$immer_draftable", L = wr ? Symbol.for("immer-state") : "__$immer_state", Lv = "" + Object.prototype.constructor, Sr = typeof Reflect < "u" && Reflect.ownKeys ? Reflect.ownKeys : Object.getOwnPropertySymbols !== void 0 ? function(e) {
      return Object.getOwnPropertyNames(e).concat(Object.getOwnPropertySymbols(e));
    } : Object.getOwnPropertyNames, Fv = Object.getOwnPropertyDescriptors || function(e) {
      var t = {};
      return Sr(e).forEach(function(r) {
        t[r] = Object.getOwnPropertyDescriptor(e, r);
      }), t;
    }, kv = {}, bt = { get: function(e, t) {
      if (t === L)
        return e;
      var r = ge(e);
      if (!cr(r, t))
        return (function(a, i, o) {
          var s, u = Fa(i, o);
          return u ? "value" in u ? u.value : (s = u.get) === null || s === void 0 ? void 0 : s.call(a.k) : void 0;
        })(e, r, t);
      var n = r[t];
      return e.I || !ve(n) ? n : n === br(e.t, t) ? (Pr(e), e.o[t] = Tr(e.A.h, n, e)) : n;
    }, has: function(e, t) {
      return t in ge(e);
    }, ownKeys: function(e) {
      return Reflect.ownKeys(ge(e));
    }, set: function(e, t, r) {
      var n = Fa(ge(e), t);
      if (n != null && n.set)
        return n.set.call(e.k, r), !0;
      if (!e.P) {
        var a = br(ge(e), t), i = a == null ? void 0 : a[L];
        if (i && i.t === r)
          return e.o[t] = r, e.D[t] = !1, !0;
        if (Dv(r, a) && (r !== void 0 || cr(e.t, t)))
          return !0;
        Pr(e), mr(e);
      }
      return e.o[t] === r && typeof r != "number" && (r !== void 0 || t in e.o) || (e.o[t] = r, e.D[t] = !0, !0);
    }, deleteProperty: function(e, t) {
      return br(e.t, t) !== void 0 || t in e.t ? (e.D[t] = !1, Pr(e), mr(e)) : delete e.D[t], e.o && delete e.o[t], !0;
    }, getOwnPropertyDescriptor: function(e, t) {
      var r = ge(e), n = Reflect.getOwnPropertyDescriptor(r, t);
      return n && { writable: !0, configurable: e.i !== 1 || t !== "length", enumerable: n.enumerable, value: r[t] };
    }, defineProperty: function() {
      G(11);
    }, getPrototypeOf: function(e) {
      return Object.getPrototypeOf(e.t);
    }, setPrototypeOf: function() {
      G(12);
    } }, mt = {};
    Ke(bt, function(e, t) {
      mt[e] = function() {
        return arguments[0] = arguments[0][0], t.apply(this, arguments);
      };
    }), mt.deleteProperty = function(e, t) {
      return bt.deleteProperty.call(this, e[0], t);
    }, mt.set = function(e, t, r) {
      return bt.set.call(this, e[0], t, r, e[0]);
    };
    var Nv = (function() {
      function e(r) {
        var n = this;
        this.g = Ua, this.F = !0, this.produce = function(a, i, o) {
          if (typeof a == "function" && typeof i != "function") {
            var s = i;
            i = a;
            var u = n;
            return function(v) {
              var h = this;
              v === void 0 && (v = s);
              for (var _ = arguments.length, y = Array(_ > 1 ? _ - 1 : 0), g = 1; g < _; g++)
                y[g - 1] = arguments[g];
              return u.produce(v, function(b) {
                var R;
                return (R = i).call.apply(R, [h, b].concat(y));
              });
            };
          }
          var l;
          if (typeof i != "function" && G(6), o !== void 0 && typeof o != "function" && G(7), ve(a)) {
            var c = Ba(n), f = Tr(n, a, void 0), d = !0;
            try {
              l = i(f), d = !1;
            } finally {
              d ? gt(c) : _r(c);
            }
            return typeof Promise < "u" && l instanceof Promise ? l.then(function(v) {
              return gr(c, o), yr(v, c);
            }, function(v) {
              throw gt(c), v;
            }) : (gr(c, o), yr(l, c));
          }
          if (!a || typeof a != "object")
            return (l = i(a)) === za ? void 0 : (l === void 0 && (l = a), n.F && hr(l, !0), l);
          G(21, a);
        }, this.produceWithPatches = function(a, i) {
          return typeof a == "function" ? function(u) {
            for (var l = arguments.length, c = Array(l > 1 ? l - 1 : 0), f = 1; f < l; f++)
              c[f - 1] = arguments[f];
            return n.produceWithPatches(u, function(d) {
              return a.apply(void 0, [d].concat(c));
            });
          } : [n.produce(a, i, function(u, l) {
            o = u, s = l;
          }), o, s];
          var o, s;
        }, typeof (r == null ? void 0 : r.useProxies) == "boolean" && this.setUseProxies(r.useProxies), typeof (r == null ? void 0 : r.autoFreeze) == "boolean" && this.setAutoFreeze(r.autoFreeze);
      }
      var t = e.prototype;
      return t.createDraft = function(r) {
        ve(r) || G(8), he(r) && (r = Rv(r));
        var n = Ba(this), a = Tr(this, r, void 0);
        return a[L].C = !0, _r(n), a;
      }, t.finishDraft = function(r, n) {
        var a = r && r[L], i = a.A;
        return gr(i, n), yr(void 0, i);
      }, t.setAutoFreeze = function(r) {
        this.F = r;
      }, t.setUseProxies = function(r) {
        r && !Ua && G(20), this.g = r;
      }, t.applyPatches = function(r, n) {
        var a;
        for (a = n.length - 1; a >= 0; a--) {
          var i = n[a];
          if (i.path.length === 0 && i.op === "replace") {
            r = i.value;
            break;
          }
        }
        var o = re("Patches").$;
        return he(r) ? o(r, n) : this.produce(r, function(s) {
          return o(s, n.slice(a + 1));
        });
      }, e;
    })(), z = new Nv();
    z.produce, z.produceWithPatches.bind(z), z.setAutoFreeze.bind(z), z.setUseProxies.bind(z), z.applyPatches.bind(z), z.createDraft.bind(z), z.finishDraft.bind(z);
    var Uv = {
      /**
       * If the schema of the redux store changes in a backwards-incompatible way, then this version number should be incremented.
       *
       * While this looks like semver, it is not. There are no patch numbers, so any change in this number is a breaking change.
       *
       * However, as long as the schema of the redux store is backwards-compatible, then we don't have to change this number.
       *
       * Since the 0.4.0 release, this number has not had to change.
       */
      currentProjectStateDefinitionVersion: "0.4.0"
    }, Or = Uv;
    async function zv(e, t, r) {
      await jv(0), e.transaction(({ drafts: n }) => {
        var a;
        const i = t.address.projectId;
        n.ephemeral.coreByProject[i] = {
          lastExportedObject: null,
          loadingState: { type: "loading" }
        }, n.ahistoric.coreByProject[i] = {
          ahistoricStuff: ""
        };
        function o() {
          n.ephemeral.coreByProject[i].loadingState = {
            type: "loaded"
          }, n.historic.coreByProject[i] = {
            sheetsById: {},
            definitionVersion: Or.currentProjectStateDefinitionVersion,
            revisionHistory: []
          };
        }
        function s(f) {
          n.ephemeral.coreByProject[i].loadingState = {
            type: "loaded"
          }, n.historic.coreByProject[i] = f;
        }
        function u() {
          n.ephemeral.coreByProject[i].loadingState = {
            type: "loaded"
          };
        }
        function l(f) {
          n.ephemeral.coreByProject[i].loadingState = {
            type: "browserStateIsNotBasedOnDiskState",
            onDiskState: f
          };
        }
        const c = (a = Cv(n.historic)) == null ? void 0 : a.coreByProject[t.address.projectId];
        c ? r && c.revisionHistory.indexOf(
          r.revisionHistory[0]
        ) == -1 ? l(r) : u() : r ? s(r) : o();
      });
    }
    function Va() {
    }
    function Ga(e) {
      var t, r;
      const n = (t = e == null ? void 0 : e.logging) != null && t.internal ? (r = e.logging.min) != null ? r : 256 : 1 / 0, a = n <= 128, i = n <= 512, o = da(void 0, {
        _debug: a ? console.debug.bind(console, "_coreLogger(TheatreInternalLogger) debug") : Va,
        _error: i ? console.error.bind(console, "_coreLogger(TheatreInternalLogger) error") : Va
      });
      if (e) {
        const { logger: s, logging: u } = e;
        s && o.configureLogger(s), u ? o.configureLogging(u) : o.configureLogging({
          dev: !1
        });
      }
      return o.getLogger().named("Theatre");
    }
    var qv = class {
      constructor(e, t = {}, r) {
        this.config = t, this.publicApi = r, p(this, "pointers"), p(this, "_pointerProxies"), p(this, "address"), p(this, "_studioReadyDeferred"), p(this, "_assetStorageReadyDeferred"), p(this, "_readyPromise"), p(this, "_sheetTemplates", new Ea.Atom({})), p(this, "sheetTemplatesP", this._sheetTemplates.pointer), p(this, "_studio"), p(this, "assetStorage"), p(this, "type", "Theatre_Project"), p(this, "_logger");
        var n;
        this._logger = Ga({ logging: { dev: !0 } }).named("Project", e), this._logger.traceDev("creating project"), this.address = { projectId: e };
        const a = new Ea.Atom({
          ahistoric: {
            ahistoricStuff: ""
          },
          historic: (n = t.state) != null ? n : {
            sheetsById: {},
            definitionVersion: Or.currentProjectStateDefinitionVersion,
            revisionHistory: []
          },
          ephemeral: {
            loadingState: {
              type: "loaded"
            },
            lastExportedObject: null
          }
        });
        this._assetStorageReadyDeferred = ie(), this.assetStorage = {
          getAssetUrl: (i) => {
            var o;
            return "".concat((o = t.assets) == null ? void 0 : o.baseUrl, "/").concat(i);
          },
          // Until the asset storage is ready, we'll throw an error when the user tries to use it
          createAsset: () => {
            throw new Error("Please wait for Project.ready to use assets.");
          }
        }, this._pointerProxies = {
          historic: new lr.PointerProxy(a.pointer.historic),
          ahistoric: new lr.PointerProxy(a.pointer.ahistoric),
          ephemeral: new lr.PointerProxy(a.pointer.ephemeral)
        }, this.pointers = {
          historic: this._pointerProxies.historic.pointer,
          ahistoric: this._pointerProxies.ahistoric.pointer,
          ephemeral: this._pointerProxies.ephemeral.pointer
        }, St.add(e, this), this._studioReadyDeferred = ie(), this._readyPromise = Promise.all([
          this._studioReadyDeferred.promise,
          this._assetStorageReadyDeferred.promise
          // hide the array from the user, i.e. make it Promise<void> instead of Promise<[undefined, undefined]>
        ]).then(() => {
        }), t.state ? setTimeout(() => {
          this._studio || (this._studioReadyDeferred.resolve(void 0), this._assetStorageReadyDeferred.resolve(void 0), this._logger._trace("ready deferred resolved with no state"));
        }, 0) : typeof window > "u" ? console.error(
          'Argument config.state in Theatre.getProject("'.concat(e, '", config) is empty. ') + "You can safely ignore this message if you're developing a Next.js/Remix project in development mode. But if you are shipping to your end-users, then you need to set config.state, otherwise your project's state will be empty and nothing will animate. Learn more at https://www.theatrejs.com/docs/latest/manual/projects#state"
        ) : setTimeout(() => {
          if (!this._studio)
            throw new Error(
              'Argument config.state in Theatre.getProject("'.concat(e, '", config) is empty. This is fine ') + "while you are using @theatre/core along with @theatre/studio. But since @theatre/studio " + 'is not loaded, the state of project "'.concat(e, `" will be empty.

`) + `To fix this, you need to add @theatre/studio into the bundle and export the project's state. Learn how to do that at https://www.theatrejs.com/docs/latest/manual/projects#state
`
            );
        }, 1e3);
      }
      attachToStudio(e) {
        if (this._studio) {
          if (this._studio !== e)
            throw new Error(
              "Project ".concat(this.address.projectId, " is already attached to studio ").concat(this._studio.address.studioId)
            );
          console.warn(
            "Project ".concat(this.address.projectId, " is already attached to studio ").concat(this._studio.address.studioId)
          );
          return;
        }
        this._studio = e, e.initialized.then(async () => {
          var t;
          await zv(e, this, this.config.state), this._pointerProxies.historic.setPointer(
            e.atomP.historic.coreByProject[this.address.projectId]
          ), this._pointerProxies.ahistoric.setPointer(
            e.atomP.ahistoric.coreByProject[this.address.projectId]
          ), this._pointerProxies.ephemeral.setPointer(
            e.atomP.ephemeral.coreByProject[this.address.projectId]
          ), await e.createAssetStorage(this, (t = this.config.assets) == null ? void 0 : t.baseUrl).then((r) => {
            this.assetStorage = r, this._assetStorageReadyDeferred.resolve(void 0);
          }), this._studioReadyDeferred.resolve(void 0);
        }).catch((t) => {
          throw console.error(t), t;
        });
      }
      get isAttachedToStudio() {
        return !!this._studio;
      }
      get ready() {
        return this._readyPromise;
      }
      isReady() {
        return this._studioReadyDeferred.status === "resolved" && this._assetStorageReadyDeferred.status === "resolved";
      }
      getOrCreateSheet(e, t = "default") {
        let r = this._sheetTemplates.get()[e];
        return r || (r = new Ov(this, e), this._sheetTemplates.reduce((n) => J(C({}, n), { [e]: r }))), r.getInstance(t);
      }
    }, Vv = class {
      get type() {
        return "Theatre_Project_PublicAPI";
      }
      /**
       * @internal
       */
      constructor(e, t = {}) {
        Re(this, new qv(e, t, this));
      }
      get ready() {
        return m(this).ready;
      }
      get isReady() {
        return m(this).isReady();
      }
      get address() {
        return C({}, m(this).address);
      }
      getAssetUrl(e) {
        if (!this.isReady) {
          console.error(
            "Calling `project.getAssetUrl()` before `project.ready` is resolved, will always return `undefined`. Either use `project.ready.then(() => project.getAssetUrl())` or `await project.ready` before calling `project.getAssetUrl()`."
          );
          return;
        }
        return e.id ? m(this).assetStorage.getAssetUrl(e.id) : void 0;
      }
      sheet(e, t = "default") {
        const r = vt(
          e
        );
        return m(this).getOrCreateSheet(
          r,
          t
        ).publicApi;
      }
    };
    $e(Er());
    var Ha = D(), Ar = D();
    function Ka(e, t = {}) {
      const r = St.get(e);
      if (r)
        return r.publicApi;
      const a = Ga().named("Project", e);
      return t.state ? (Hv(e, t.state), a._debug("deep validated config.state on disk")) : a._debug("no config.state"), new Vv(e, t);
    }
    var Gv = (e, t) => {
      if (Array.isArray(t) || t == null || t.definitionVersion !== Or.currentProjectStateDefinitionVersion)
        throw new Ve(
          "Error validating conf.state in Theatre.getProject(".concat(JSON.stringify(
            e
          ), ", conf). The state seems to be formatted in a way that is unreadable to Theatre.js. Read more at https://www.theatrejs.com/docs/latest/manual/projects#state")
        );
    }, Hv = (e, t) => {
      Gv(e, t);
    };
    function jr(e, t, r) {
      const n = r ? m(r).ticker : wa();
      if ((0, Ha.isPointer)(e))
        return (0, Ar.pointerToPrism)(e).onChange(n, t, !0);
      if ((0, Ar.isPrism)(e))
        return e.onChange(n, t, !0);
      throw new Error(
        "Called onChange(p) where p is neither a pointer nor a prism."
      );
    }
    function Wa(e) {
      if ((0, Ha.isPointer)(e))
        return (0, Ar.pointerToPrism)(e).getValue();
      throw new Error("Called val(p) where p is not a pointer.");
    }
    var Kv = class {
      constructor() {
        p(this, "_studio");
      }
      get type() {
        return "Theatre_CoreBundle";
      }
      get version() {
        return "0.7.2";
      }
      getBitsForStudio(e, t) {
        if (this._studio)
          throw new Error("@theatre/core is already attached to @theatre/studio");
        this._studio = e;
        const r = {
          projectsP: St.atom.pointer.projects,
          privateAPI: m,
          coreExports: Mr,
          getCoreRafDriver: Ta
        };
        t(r);
      }
    };
    Wv();
    function Wv() {
      if (typeof window > "u")
        return;
      const e = (
        // @ts-ignore ignore
        window[ar]
      );
      if (typeof e < "u")
        throw typeof e == "object" && e && typeof e.version == "string" ? new Error(
          `It seems that the module '@theatre/core' is loaded more than once. This could have two possible causes:
1. You might have two separate versions of Theatre.js in node_modules.
2. Or this might be a bundling misconfiguration, in case you're using a bundler like Webpack/ESBuild/Rollup.

Note that it **is okay** to import '@theatre/core' multiple times. But those imports should point to the same module.`
        ) : new Error(
          "The variable window.".concat(ar, " seems to be already set by a module other than @theatre/core.")
        );
      const t = new Kv();
      window[ar] = t;
      const r = (
        // @ts-ignore ignore
        window[zh]
      );
      r && r !== null && r.type === "Theatre_StudioBundle" && r.registerCoreBundle(t);
    }
    /*! Bundled license information:
    
    		lodash-es/lodash.js:
    		  (**
    		   * @license
    		   * Lodash (Custom Build) <https://lodash.com/>
    		   * Build: `lodash modularize exports="es" -o ./`
    		   * Copyright OpenJS Foundation and other contributors <https://openjsf.org/>
    		   * Released under MIT license <https://lodash.com/license>
    		   * Based on Underscore.js 1.8.3 <http://underscorejs.org/LICENSE>
    		   * Copyright Jeremy Ashkenas, DocumentCloud and Investigative Reporters & Editors
    		   *)
    		*/
  })(Je, Je.exports)), Je.exports;
}
var Xa = Jv();
const $v = Xa.getProject, Yv = Xa.types;
export {
  $v as getProject,
  Yv as types
};
