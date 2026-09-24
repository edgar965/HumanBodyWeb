var g = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {};
function Dn(u) {
  return u && u.__esModule && Object.prototype.hasOwnProperty.call(u, "default") ? u.default : u;
}
var $ = {}, Pe;
function jn() {
  return Pe || (Pe = 1, (function(u) {
    var M = Object.defineProperty, we = Object.defineProperties, Te = Object.getOwnPropertyDescriptors, L = Object.getOwnPropertySymbols, Ce = Object.prototype.hasOwnProperty, Oe = Object.prototype.propertyIsEnumerable, K = (e, t, r) => t in e ? M(e, t, { enumerable: !0, configurable: !0, writable: !0, value: r }) : e[t] = r, ke = (e, t) => {
      for (var r in t || (t = {}))
        Ce.call(t, r) && K(e, r, t[r]);
      if (L)
        for (var r of L(t))
          Oe.call(t, r) && K(e, r, t[r]);
      return e;
    }, De = (e, t) => we(e, Te(t)), je = (e) => M(e, "__esModule", { value: !0 }), xe = (e, t) => {
      je(e);
      for (var r in t)
        M(e, r, { get: t[r], enumerable: !0 });
    };
    xe(u, {
      Atom: () => ge,
      PointerProxy: () => kn,
      Ticker: () => be,
      getPointerParts: () => b,
      isPointer: () => _,
      isPrism: () => k,
      iterateAndCountTicks: () => Tn,
      iterateOver: () => On,
      pointer: () => z,
      pointerToPrism: () => x,
      prism: () => j,
      val: () => ye
    });
    var Me = Array.isArray, V = Me, Ve = typeof g == "object" && g && g.Object === Object && g, Ae = Ve, Ie = typeof self == "object" && self && self.Object === Object && self, Ee = Ae || Ie || Function("return this")(), A = Ee, Ne = A.Symbol, h = Ne, B = Object.prototype, Fe = B.hasOwnProperty, He = B.toString, m = h ? h.toStringTag : void 0;
    function ze(e) {
      var t = Fe.call(e, m), r = e[m];
      try {
        e[m] = void 0;
        var n = !0;
      } catch {
      }
      var s = He.call(e);
      return n && (t ? e[m] = r : delete e[m]), s;
    }
    var Ge = ze, Re = Object.prototype, $e = Re.toString;
    function Le(e) {
      return $e.call(e);
    }
    var Ke = Le, Be = "[object Null]", Ue = "[object Undefined]", U = h ? h.toStringTag : void 0;
    function We(e) {
      return e == null ? e === void 0 ? Ue : Be : U && U in Object(e) ? Ge(e) : Ke(e);
    }
    var I = We;
    function qe(e) {
      return e != null && typeof e == "object";
    }
    var W = qe, Je = "[object Symbol]";
    function Xe(e) {
      return typeof e == "symbol" || W(e) && I(e) == Je;
    }
    var E = Xe, Ye = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, Ze = /^\w*$/;
    function Qe(e, t) {
      if (V(e))
        return !1;
      var r = typeof e;
      return r == "number" || r == "symbol" || r == "boolean" || e == null || E(e) ? !0 : Ze.test(e) || !Ye.test(e) || t != null && e in Object(t);
    }
    var et = Qe;
    function tt(e) {
      var t = typeof e;
      return e != null && (t == "object" || t == "function");
    }
    var q = tt, rt = "[object AsyncFunction]", nt = "[object Function]", st = "[object GeneratorFunction]", ot = "[object Proxy]";
    function it(e) {
      if (!q(e))
        return !1;
      var t = I(e);
      return t == nt || t == st || t == rt || t == ot;
    }
    var at = it, ct = A["__core-js_shared__"], N = ct, J = (function() {
      var e = /[^.]+$/.exec(N && N.keys && N.keys.IE_PROTO || "");
      return e ? "Symbol(src)_1." + e : "";
    })();
    function lt(e) {
      return !!J && J in e;
    }
    var ut = lt, ht = Function.prototype, dt = ht.toString;
    function ft(e) {
      if (e != null) {
        try {
          return dt.call(e);
        } catch {
        }
        try {
          return e + "";
        } catch {
        }
      }
      return "";
    }
    var pt = ft, _t = /[\\^$.*+?()[\]{}|]/g, vt = /^\[object .+?Constructor\]$/, gt = Function.prototype, mt = Object.prototype, yt = gt.toString, bt = mt.hasOwnProperty, St = RegExp("^" + yt.call(bt).replace(_t, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$");
    function Pt(e) {
      if (!q(e) || ut(e))
        return !1;
      var t = at(e) ? St : vt;
      return t.test(pt(e));
    }
    var wt = Pt;
    function Tt(e, t) {
      return e == null ? void 0 : e[t];
    }
    var Ct = Tt;
    function Ot(e, t) {
      var r = Ct(e, t);
      return wt(r) ? r : void 0;
    }
    var X = Ot, kt = X(Object, "create"), y = kt;
    function Dt() {
      this.__data__ = y ? y(null) : {}, this.size = 0;
    }
    var jt = Dt;
    function xt(e) {
      var t = this.has(e) && delete this.__data__[e];
      return this.size -= t ? 1 : 0, t;
    }
    var Mt = xt, Vt = "__lodash_hash_undefined__", At = Object.prototype, It = At.hasOwnProperty;
    function Et(e) {
      var t = this.__data__;
      if (y) {
        var r = t[e];
        return r === Vt ? void 0 : r;
      }
      return It.call(t, e) ? t[e] : void 0;
    }
    var Nt = Et, Ft = Object.prototype, Ht = Ft.hasOwnProperty;
    function zt(e) {
      var t = this.__data__;
      return y ? t[e] !== void 0 : Ht.call(t, e);
    }
    var Gt = zt, Rt = "__lodash_hash_undefined__";
    function $t(e, t) {
      var r = this.__data__;
      return this.size += this.has(e) ? 0 : 1, r[e] = y && t === void 0 ? Rt : t, this;
    }
    var Lt = $t;
    function d(e) {
      var t = -1, r = e == null ? 0 : e.length;
      for (this.clear(); ++t < r; ) {
        var n = e[t];
        this.set(n[0], n[1]);
      }
    }
    d.prototype.clear = jt, d.prototype.delete = Mt, d.prototype.get = Nt, d.prototype.has = Gt, d.prototype.set = Lt;
    var Y = d;
    function Kt() {
      this.__data__ = [], this.size = 0;
    }
    var Bt = Kt;
    function Ut(e, t) {
      return e === t || e !== e && t !== t;
    }
    var Wt = Ut;
    function qt(e, t) {
      for (var r = e.length; r--; )
        if (Wt(e[r][0], t))
          return r;
      return -1;
    }
    var w = qt, Jt = Array.prototype, Xt = Jt.splice;
    function Yt(e) {
      var t = this.__data__, r = w(t, e);
      if (r < 0)
        return !1;
      var n = t.length - 1;
      return r == n ? t.pop() : Xt.call(t, r, 1), --this.size, !0;
    }
    var Zt = Yt;
    function Qt(e) {
      var t = this.__data__, r = w(t, e);
      return r < 0 ? void 0 : t[r][1];
    }
    var er = Qt;
    function tr(e) {
      return w(this.__data__, e) > -1;
    }
    var rr = tr;
    function nr(e, t) {
      var r = this.__data__, n = w(r, e);
      return n < 0 ? (++this.size, r.push([e, t])) : r[n][1] = t, this;
    }
    var sr = nr;
    function f(e) {
      var t = -1, r = e == null ? 0 : e.length;
      for (this.clear(); ++t < r; ) {
        var n = e[t];
        this.set(n[0], n[1]);
      }
    }
    f.prototype.clear = Bt, f.prototype.delete = Zt, f.prototype.get = er, f.prototype.has = rr, f.prototype.set = sr;
    var or = f, ir = X(A, "Map"), ar = ir;
    function cr() {
      this.size = 0, this.__data__ = {
        hash: new Y(),
        map: new (ar || or)(),
        string: new Y()
      };
    }
    var lr = cr;
    function ur(e) {
      var t = typeof e;
      return t == "string" || t == "number" || t == "symbol" || t == "boolean" ? e !== "__proto__" : e === null;
    }
    var hr = ur;
    function dr(e, t) {
      var r = e.__data__;
      return hr(t) ? r[typeof t == "string" ? "string" : "hash"] : r.map;
    }
    var T = dr;
    function fr(e) {
      var t = T(this, e).delete(e);
      return this.size -= t ? 1 : 0, t;
    }
    var pr = fr;
    function _r(e) {
      return T(this, e).get(e);
    }
    var vr = _r;
    function gr(e) {
      return T(this, e).has(e);
    }
    var mr = gr;
    function yr(e, t) {
      var r = T(this, e), n = r.size;
      return r.set(e, t), this.size += r.size == n ? 0 : 1, this;
    }
    var br = yr;
    function p(e) {
      var t = -1, r = e == null ? 0 : e.length;
      for (this.clear(); ++t < r; ) {
        var n = e[t];
        this.set(n[0], n[1]);
      }
    }
    p.prototype.clear = lr, p.prototype.delete = pr, p.prototype.get = vr, p.prototype.has = mr, p.prototype.set = br;
    var Z = p, Sr = "Expected a function";
    function F(e, t) {
      if (typeof e != "function" || t != null && typeof t != "function")
        throw new TypeError(Sr);
      var r = function() {
        var n = arguments, s = t ? t.apply(this, n) : n[0], o = r.cache;
        if (o.has(s))
          return o.get(s);
        var a = e.apply(this, n);
        return r.cache = o.set(s, a) || o, a;
      };
      return r.cache = new (F.Cache || Z)(), r;
    }
    F.Cache = Z;
    var Pr = F, wr = 500;
    function Tr(e) {
      var t = Pr(e, function(n) {
        return r.size === wr && r.clear(), n;
      }), r = t.cache;
      return t;
    }
    var Cr = Tr, Or = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, kr = /\\(\\)?/g, Dr = Cr(function(e) {
      var t = [];
      return e.charCodeAt(0) === 46 && t.push(""), e.replace(Or, function(r, n, s, o) {
        t.push(s ? o.replace(kr, "$1") : n || r);
      }), t;
    }), jr = Dr;
    function xr(e, t) {
      for (var r = -1, n = e == null ? 0 : e.length, s = Array(n); ++r < n; )
        s[r] = t(e[r], r, e);
      return s;
    }
    var Mr = xr, Q = h ? h.prototype : void 0, ee = Q ? Q.toString : void 0;
    function te(e) {
      if (typeof e == "string")
        return e;
      if (V(e))
        return Mr(e, te) + "";
      if (E(e))
        return ee ? ee.call(e) : "";
      var t = e + "";
      return t == "0" && 1 / e == -1 / 0 ? "-0" : t;
    }
    var Vr = te;
    function Ar(e) {
      return e == null ? "" : Vr(e);
    }
    var Ir = Ar;
    function Er(e, t) {
      return V(e) ? e : et(e, t) ? [e] : jr(Ir(e));
    }
    var Nr = Er;
    function Fr(e) {
      if (typeof e == "string" || E(e))
        return e;
      var t = e + "";
      return t == "0" && 1 / e == -1 / 0 ? "-0" : t;
    }
    var Hr = Fr;
    function zr(e, t) {
      t = Nr(t, e);
      for (var r = 0, n = t.length; e != null && r < n; )
        e = e[Hr(t[r++])];
      return r && r == n ? e : void 0;
    }
    var Gr = zr;
    function Rr(e, t, r) {
      var n = e == null ? void 0 : Gr(e, t);
      return n === void 0 ? r : n;
    }
    var $r = Rr;
    function Lr(e, t) {
      return function(r) {
        return e(t(r));
      };
    }
    var Kr = Lr, Br = Kr(Object.getPrototypeOf, Object), Ur = Br, Wr = "[object Object]", qr = Function.prototype, Jr = Object.prototype, re = qr.toString, Xr = Jr.hasOwnProperty, Yr = re.call(Object);
    function Zr(e) {
      if (!W(e) || I(e) != Wr)
        return !1;
      var t = Ur(e);
      if (t === null)
        return !0;
      var r = Xr.call(t, "constructor") && t.constructor;
      return typeof r == "function" && r instanceof r && re.call(r) == Yr;
    }
    var Qr = Zr;
    function en(e) {
      var t = e == null ? 0 : e.length;
      return t ? e[t - 1] : void 0;
    }
    var tn = en, H = /* @__PURE__ */ new WeakMap(), ne = /* @__PURE__ */ new WeakMap(), se = Symbol("pointerMeta"), rn = {
      get(e, t) {
        if (t === se)
          return H.get(e);
        let r = ne.get(e);
        r || (r = /* @__PURE__ */ new Map(), ne.set(e, r));
        const n = r.get(t);
        if (n !== void 0)
          return n;
        const s = H.get(e), o = oe({ root: s.root, path: [...s.path, t] });
        return r.set(t, o), o;
      }
    }, C = (e) => e[se], b = (e) => {
      const { root: t, path: r } = C(e);
      return { root: t, path: r };
    };
    function oe(e) {
      var t;
      const r = {
        root: e.root,
        path: (t = e.path) != null ? t : []
      }, n = {};
      return H.set(n, r), new Proxy(n, rn);
    }
    var z = oe, _ = (e) => e && !!C(e);
    function nn(e, t, r) {
      return t.length === 0 ? r(e) : O(e, t, r);
    }
    var O = (e, t, r) => {
      if (t.length === 0)
        return r(e);
      if (Array.isArray(e)) {
        let [n, ...s] = t;
        n = parseInt(String(n), 10), isNaN(n) && (n = 0);
        const o = e[n], a = O(o, s, r);
        if (o === a)
          return e;
        const l = [...e];
        return l.splice(n, 1, a), l;
      } else if (typeof e == "object" && e !== null) {
        const [n, ...s] = t, o = e[n], a = O(o, s, r);
        return o === a ? e : De(ke({}, e), { [n]: a });
      } else {
        const [n, ...s] = t;
        return { [n]: O(void 0, s, r) };
      }
    }, ie = class {
      constructor() {
        this._head = void 0;
      }
      peek() {
        return this._head && this._head.data;
      }
      pop() {
        const e = this._head;
        if (e)
          return this._head = e.next, e.data;
      }
      push(e) {
        const t = { next: this._head, data: e };
        this._head = t;
      }
    };
    function k(e) {
      return !!(e && e.isPrism && e.isPrism === !0);
    }
    function ae() {
      const e = () => {
      }, t = new ie(), r = e;
      return {
        type: "Dataverse_discoveryMechanism",
        startIgnoringDependencies: () => {
          t.push(r);
        },
        stopIgnoringDependencies: () => {
          t.peek() !== r || t.pop();
        },
        reportResolutionStart: (v) => {
          const R = t.peek();
          R && R(v), t.push(r);
        },
        reportResolutionEnd: (v) => {
          t.pop();
        },
        pushCollector: (v) => {
          t.push(v);
        },
        popCollector: (v) => {
          if (t.peek() !== v)
            throw new Error("Popped collector is not on top of the stack");
          t.pop();
        }
      };
    }
    function sn() {
      const e = "__dataverse_discoveryMechanism_sharedStack", t = typeof window < "u" ? window : typeof g < "u" ? g : {};
      if (t) {
        const r = t[e];
        if (r && typeof r == "object" && r.type === "Dataverse_discoveryMechanism")
          return r;
        {
          const n = ae();
          return t[e] = n, n;
        }
      } else
        return ae();
    }
    var {
      startIgnoringDependencies: S,
      stopIgnoringDependencies: P,
      reportResolutionEnd: on,
      reportResolutionStart: an,
      pushCollector: cn,
      popCollector: ln
    } = sn(), ce = () => {
    }, un = class {
      constructor(e, t) {
        this._fn = e, this._prismInstance = t, this._didMarkDependentsAsStale = !1, this._isFresh = !1, this._cacheOfDendencyValues = /* @__PURE__ */ new Map(), this._dependents = /* @__PURE__ */ new Set(), this._dependencies = /* @__PURE__ */ new Set(), this._possiblyStaleDeps = /* @__PURE__ */ new Set(), this._scope = new le(this), this._lastValue = void 0, this._forciblySetToStale = !1, this._reactToDependencyGoingStale = (r) => {
          this._possiblyStaleDeps.add(r), this._markAsStale();
        };
        for (const r of this._dependencies)
          r._addDependent(this._reactToDependencyGoingStale);
        S(), this.getValue(), P();
      }
      get hasDependents() {
        return this._dependents.size > 0;
      }
      removeDependent(e) {
        this._dependents.delete(e);
      }
      addDependent(e) {
        this._dependents.add(e);
      }
      destroy() {
        for (const e of this._dependencies)
          e._removeDependent(this._reactToDependencyGoingStale);
        ue(this._scope);
      }
      getValue() {
        if (!this._isFresh) {
          const e = this._recalculate();
          this._lastValue = e, this._isFresh = !0, this._didMarkDependentsAsStale = !1, this._forciblySetToStale = !1;
        }
        return this._lastValue;
      }
      _recalculate() {
        let e;
        if (!this._forciblySetToStale && this._possiblyStaleDeps.size > 0) {
          let n = !1;
          S();
          for (const s of this._possiblyStaleDeps)
            if (this._cacheOfDendencyValues.get(s) !== s.getValue()) {
              n = !0;
              break;
            }
          if (P(), this._possiblyStaleDeps.clear(), !n)
            return this._lastValue;
        }
        const t = /* @__PURE__ */ new Set();
        this._cacheOfDendencyValues.clear();
        const r = (n) => {
          t.add(n), this._addDependency(n);
        };
        cn(r), i.push(this._scope);
        try {
          e = this._fn();
        } catch (n) {
          console.error(n);
        } finally {
          i.pop() !== this._scope && console.warn("The Prism hook stack has slipped. This is a bug.");
        }
        ln(r);
        for (const n of this._dependencies)
          t.has(n) || this._removeDependency(n);
        this._dependencies = t, S();
        for (const n of t)
          this._cacheOfDendencyValues.set(n, n.getValue());
        return P(), e;
      }
      forceStale() {
        this._forciblySetToStale = !0, this._markAsStale();
      }
      _markAsStale() {
        if (!this._didMarkDependentsAsStale) {
          this._didMarkDependentsAsStale = !0, this._isFresh = !1;
          for (const e of this._dependents)
            e(this._prismInstance);
        }
      }
      _addDependency(e) {
        this._dependencies.has(e) || (this._dependencies.add(e), e._addDependent(this._reactToDependencyGoingStale));
      }
      _removeDependency(e) {
        this._dependencies.has(e) && (this._dependencies.delete(e), e._removeDependent(this._reactToDependencyGoingStale));
      }
    }, hn = {}, dn = class {
      constructor(e) {
        this._fn = e, this.isPrism = !0, this._state = {
          hot: !1,
          handle: void 0
        };
      }
      get isHot() {
        return this._state.hot;
      }
      onChange(e, t, r = !1) {
        const n = () => {
          e.onThisOrNextTick(o);
        };
        let s = hn;
        const o = () => {
          const l = this.getValue();
          l !== s && (s = l, t(l));
        };
        return this._addDependent(n), r && (s = this.getValue(), t(s)), () => {
          this._removeDependent(n), e.offThisOrNextTick(o), e.offNextTick(o);
        };
      }
      onStale(e) {
        const t = () => {
          this._removeDependent(r);
        }, r = () => e();
        return this._addDependent(r), t;
      }
      keepHot() {
        return this.onStale(() => {
        });
      }
      _addDependent(e) {
        this._state.hot || this._goHot(), this._state.handle.addDependent(e);
      }
      _goHot() {
        const e = new un(this._fn, this);
        this._state = {
          hot: !0,
          handle: e
        };
      }
      _removeDependent(e) {
        const t = this._state;
        if (!t.hot)
          return;
        const r = t.handle;
        r.removeDependent(e), r.hasDependents || (this._state = { hot: !1, handle: void 0 }, r.destroy());
      }
      getValue() {
        an(this);
        const e = this._state;
        let t;
        return e.hot ? t = e.handle.getValue() : t = Sn(this._fn), on(this), t;
      }
    }, le = class {
      constructor(e) {
        this._hotHandle = e, this._refs = /* @__PURE__ */ new Map(), this.isPrismScope = !0, this.subs = {}, this.effects = /* @__PURE__ */ new Map(), this.memos = /* @__PURE__ */ new Map();
      }
      ref(e, t) {
        let r = this._refs.get(e);
        if (r !== void 0)
          return r;
        {
          const n = {
            current: t
          };
          return this._refs.set(e, n), n;
        }
      }
      effect(e, t, r) {
        let n = this.effects.get(e);
        n === void 0 && (n = {
          cleanup: ce,
          deps: void 0
        }, this.effects.set(e, n)), he(n.deps, r) && (n.cleanup(), S(), n.cleanup = D(t, ce).value, P(), n.deps = r);
      }
      memo(e, t, r) {
        let n = this.memos.get(e);
        return n === void 0 && (n = {
          cachedValue: null,
          deps: void 0
        }, this.memos.set(e, n)), he(n.deps, r) && (S(), n.cachedValue = D(t, void 0).value, P(), n.deps = r), n.cachedValue;
      }
      state(e, t) {
        const { value: r, setValue: n } = this.memo("state/" + e, () => {
          const s = { current: t };
          return { value: s, setValue: (a) => {
            s.current = a, this._hotHandle.forceStale();
          } };
        }, []);
        return [r.current, n];
      }
      sub(e) {
        return this.subs[e] || (this.subs[e] = new le(this._hotHandle)), this.subs[e];
      }
      cleanupEffects() {
        for (const e of this.effects.values())
          D(e.cleanup, void 0);
        this.effects.clear();
      }
      source(e, t) {
        return this.effect("$$source/blah", () => e(() => {
          this._hotHandle.forceStale();
        }), [e]), t();
      }
    };
    function ue(e) {
      for (const t of Object.values(e.subs))
        ue(t);
      e.cleanupEffects();
    }
    function D(e, t) {
      try {
        return { value: e(), ok: !0 };
      } catch (r) {
        return setTimeout(function() {
          throw r;
        }), { value: t, ok: !1 };
      }
    }
    var i = new ie();
    function fn(e, t) {
      const r = i.peek();
      if (!r)
        throw new Error("prism.ref() is called outside of a prism() call.");
      return r.ref(e, t);
    }
    function pn(e, t, r) {
      const n = i.peek();
      if (!n)
        throw new Error("prism.effect() is called outside of a prism() call.");
      return n.effect(e, t, r);
    }
    function he(e, t) {
      if (e === void 0 || t === void 0)
        return !0;
      const r = e.length;
      if (r !== t.length)
        return !0;
      for (let n = 0; n < r; n++)
        if (e[n] !== t[n])
          return !0;
      return !1;
    }
    function de(e, t, r) {
      const n = i.peek();
      if (!n)
        throw new Error("prism.memo() is called outside of a prism() call.");
      return n.memo(e, t, r);
    }
    function _n(e, t) {
      const r = i.peek();
      if (!r)
        throw new Error("prism.state() is called outside of a prism() call.");
      return r.state(e, t);
    }
    function vn() {
      if (!i.peek())
        throw new Error("The parent function is called outside of a prism() call.");
    }
    function gn(e, t) {
      const r = i.peek();
      if (!r)
        throw new Error("prism.scope() is called outside of a prism() call.");
      const n = r.sub(e);
      i.push(n);
      const s = D(t, void 0).value;
      return i.pop(), s;
    }
    function mn(e, t, r) {
      return de(e, () => c(t), r).getValue();
    }
    function yn() {
      return !!i.peek();
    }
    function bn(e, t) {
      const r = i.peek();
      if (!r)
        throw new Error("prism.source() is called outside of a prism() call.");
      return r.source(e, t);
    }
    var c = (e) => new dn(e), fe = class {
      effect(e, t, r) {
        console.warn("prism.effect() does not run in cold prisms");
      }
      memo(e, t, r) {
        return t();
      }
      state(e, t) {
        return [t, () => {
        }];
      }
      ref(e, t) {
        return { current: t };
      }
      sub(e) {
        return new fe();
      }
      source(e, t) {
        return t();
      }
    };
    function Sn(e) {
      const t = new fe();
      i.push(t);
      let r;
      try {
        r = e();
      } catch (n) {
        console.error(n);
      } finally {
        i.pop() !== t && console.warn("The Prism hook stack has slipped. This is a bug.");
      }
      return r;
    }
    c.ref = fn, c.effect = pn, c.memo = de, c.ensurePrism = vn, c.state = _n, c.scope = gn, c.sub = mn, c.inPrism = yn, c.source = bn;
    var j = c, pe;
    (function(e) {
      e[e.Dict = 0] = "Dict", e[e.Array = 1] = "Array", e[e.Other = 2] = "Other";
    })(pe || (pe = {}));
    var G = (e) => Array.isArray(e) ? 1 : Qr(e) ? 0 : 2, _e = (e, t, r = G(e)) => r === 0 && typeof t == "string" || r === 1 && Pn(t) ? e[t] : void 0, Pn = (e) => {
      const t = typeof e == "number" ? e : parseInt(e, 10);
      return !isNaN(t) && t >= 0 && t < 1 / 0 && (t | 0) === t;
    }, ve = class {
      constructor(e, t) {
        this._parent = e, this._path = t, this.children = /* @__PURE__ */ new Map(), this.identityChangeListeners = /* @__PURE__ */ new Set();
      }
      addIdentityChangeListener(e) {
        this.identityChangeListeners.add(e);
      }
      removeIdentityChangeListener(e) {
        this.identityChangeListeners.delete(e), this._checkForGC();
      }
      removeChild(e) {
        this.children.delete(e), this._checkForGC();
      }
      getChild(e) {
        return this.children.get(e);
      }
      getOrCreateChild(e) {
        let t = this.children.get(e);
        return t || (t = t = new ve(this, this._path.concat([e])), this.children.set(e, t)), t;
      }
      _checkForGC() {
        this.identityChangeListeners.size > 0 || this.children.size > 0 || this._parent && this._parent.removeChild(tn(this._path));
      }
    }, ge = class {
      constructor(e) {
        this.$$isPointerToPrismProvider = !0, this.pointer = z({ root: this, path: [] }), this.prism = this.pointerToPrism(this.pointer), this._onPointerValueChange = (t, r) => {
          const { path: n } = b(t), s = this._getOrCreateScopeForPath(n);
          return s.identityChangeListeners.add(r), () => {
            s.identityChangeListeners.delete(r);
          };
        }, this._currentState = e, this._rootScope = new ve(void 0, []);
      }
      set(e) {
        const t = this._currentState;
        this._currentState = e, this._checkUpdates(this._rootScope, t, e);
      }
      get() {
        return this._currentState;
      }
      getByPointer(e) {
        const t = _(e) ? e : e(this.pointer), r = b(t).path;
        return this._getIn(r);
      }
      _getIn(e) {
        return e.length === 0 ? this.get() : $r(this.get(), e);
      }
      reduce(e) {
        this.set(e(this.get()));
      }
      reduceByPointer(e, t) {
        const r = _(e) ? e : e(this.pointer), n = b(r).path, s = nn(this.get(), n, t);
        this.set(s);
      }
      setByPointer(e, t) {
        this.reduceByPointer(e, () => t);
      }
      _checkUpdates(e, t, r) {
        if (t === r)
          return;
        for (const o of e.identityChangeListeners)
          o(r);
        if (e.children.size === 0)
          return;
        const n = G(t), s = G(r);
        if (!(n === 2 && n === s))
          for (const [o, a] of e.children) {
            const l = _e(t, o, n), Se = _e(r, o, s);
            this._checkUpdates(a, l, Se);
          }
      }
      _getOrCreateScopeForPath(e) {
        let t = this._rootScope;
        for (const r of e)
          t = t.getOrCreateChild(r);
        return t;
      }
      pointerToPrism(e) {
        const { path: t } = b(e), r = (s) => this._onPointerValueChange(e, s), n = () => this._getIn(t);
        return j(() => j.source(r, n));
      }
    }, me = /* @__PURE__ */ new WeakMap();
    function wn(e) {
      return typeof e == "object" && e !== null && e.$$isPointerToPrismProvider === !0;
    }
    var x = (e) => {
      const t = C(e);
      let r = me.get(t);
      if (!r) {
        const n = t.root;
        if (!wn(n))
          throw new Error("Cannot run pointerToPrism() on a pointer whose root is not an PointerToPrismProvider");
        r = n.pointerToPrism(e), me.set(t, r);
      }
      return r;
    }, ye = (e) => _(e) ? x(e).getValue() : k(e) ? e.getValue() : e;
    function* Tn(e) {
      let t;
      if (_(e))
        t = x(e);
      else if (k(e))
        t = e;
      else
        throw new Error("Only pointers and prisms are supported");
      let r = 0;
      const n = t.onStale(() => {
        r++;
      });
      try {
        for (; ; ) {
          const s = r;
          r = 0, yield { value: t.getValue(), ticks: s };
        }
      } finally {
        n();
      }
    }
    var Cn = 180, be = class {
      constructor(e) {
        this._conf = e, this._ticking = !1, this._dormant = !0, this._numberOfDormantTicks = 0, this.__ticks = 0, this._scheduledForThisOrNextTick = /* @__PURE__ */ new Set(), this._scheduledForNextTick = /* @__PURE__ */ new Set(), this._timeAtCurrentTick = 0;
      }
      get dormant() {
        return this._dormant;
      }
      onThisOrNextTick(e) {
        this._scheduledForThisOrNextTick.add(e), this._dormant && this._goActive();
      }
      onNextTick(e) {
        this._scheduledForNextTick.add(e), this._dormant && this._goActive();
      }
      offThisOrNextTick(e) {
        this._scheduledForThisOrNextTick.delete(e);
      }
      offNextTick(e) {
        this._scheduledForNextTick.delete(e);
      }
      get time() {
        return this._ticking ? this._timeAtCurrentTick : performance.now();
      }
      _goActive() {
        var e, t;
        this._dormant && (this._dormant = !1, (t = (e = this._conf) == null ? void 0 : e.onActive) == null || t.call(e));
      }
      _goDormant() {
        var e, t;
        this._dormant || (this._dormant = !0, this._numberOfDormantTicks = 0, (t = (e = this._conf) == null ? void 0 : e.onDormant) == null || t.call(e));
      }
      tick(e = performance.now()) {
        if (this.__ticks++, !this._dormant && this._scheduledForNextTick.size === 0 && this._scheduledForThisOrNextTick.size === 0 && (this._numberOfDormantTicks++, this._numberOfDormantTicks >= Cn)) {
          this._goDormant();
          return;
        }
        this._ticking = !0, this._timeAtCurrentTick = e;
        for (const t of this._scheduledForNextTick)
          this._scheduledForThisOrNextTick.add(t);
        this._scheduledForNextTick.clear(), this._tick(0), this._ticking = !1;
      }
      _tick(e) {
        const t = this.time;
        if (e > 10 && console.warn("_tick() recursing for 10 times"), e > 100)
          throw new Error("Maximum recursion limit for _tick()");
        const r = this._scheduledForThisOrNextTick;
        this._scheduledForThisOrNextTick = /* @__PURE__ */ new Set();
        for (const n of r)
          n(t);
        if (this._scheduledForThisOrNextTick.size > 0)
          return this._tick(e + 1);
      }
    };
    function* On(e) {
      let t;
      if (_(e))
        t = x(e);
      else if (k(e))
        t = e;
      else
        throw new Error("Only pointers and prisms are supported");
      const r = new be(), n = t.onChange(r, (s) => {
      });
      try {
        for (; ; )
          r.tick(), yield t.getValue();
      } finally {
        n();
      }
    }
    var kn = class {
      constructor(e) {
        this.$$isPointerToPrismProvider = !0, this._currentPointerBox = new ge(e), this.pointer = z({ root: this, path: [] });
      }
      setPointer(e) {
        this._currentPointerBox.set(e);
      }
      pointerToPrism(e) {
        const { path: t } = C(e);
        return j(() => {
          const r = this._currentPointerBox.prism.getValue(), n = t.reduce((s, o) => s[o], r);
          return ye(n);
        });
      }
    };
  })($)), $;
}
export {
  g as c,
  Dn as g,
  jn as r
};
