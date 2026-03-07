/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Xs={ROTATE:0,DOLLY:1,PAN:2},Hs={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},cM=0,Ap=1,uM=2,hg=1,hM=2,Qi=3,ir=0,Jn=1,Qn=2,Er=0,qs=1,Rp=2,Pp=3,Cp=4,dM=5,os=100,fM=101,pM=102,mM=103,gM=104,_M=200,vM=201,yM=202,xM=203,_h=204,vh=205,bM=206,SM=207,EM=208,MM=209,TM=210,wM=211,AM=212,RM=213,PM=214,yh=0,xh=1,bh=2,Qs=3,Sh=4,Eh=5,Mh=6,Th=7,dg=0,CM=1,DM=2,Mr=0,IM=1,LM=2,FM=3,fg=4,NM=5,OM=6,UM=7,Dp="attached",BM="detached",pg=300,Js=301,eo=302,wh=303,Ah=304,zl=306,to=1e3,br=1001,Fl=1002,Xn=1003,mg=1004,jo=1005,ci=1006,Tl=1007,er=1008,rr=1009,gg=1010,_g=1011,ea=1012,ud=1013,cs=1014,Ei=1015,ra=1016,hd=1017,dd=1018,no=1020,vg=35902,yg=1021,xg=1022,pi=1023,bg=1024,Sg=1025,Ys=1026,io=1027,fd=1028,pd=1029,Eg=1030,md=1031,gd=1033,wl=33776,Al=33777,Rl=33778,Pl=33779,Rh=35840,Ph=35841,Ch=35842,Dh=35843,Ih=36196,Lh=37492,Fh=37496,Nh=37808,Oh=37809,Uh=37810,Bh=37811,kh=37812,zh=37813,Hh=37814,Vh=37815,Gh=37816,Wh=37817,jh=37818,Xh=37819,qh=37820,Yh=37821,Cl=36492,Kh=36494,$h=36495,Mg=36283,Zh=36284,Qh=36285,Jh=36286,kM=2200,_d=2201,zM=2202,ta=2300,na=2301,Mu=2302,Vs=2400,Gs=2401,Nl=2402,vd=2500,HM=2501,VM=0,Tg=1,ed=2,GM=3200,WM=3201,wg=0,jM=1,xr="",Rn="srgb",qn="srgb-linear",Hl="linear",Qt="srgb",ws=7680,Ip=519,XM=512,qM=513,YM=514,Ag=515,KM=516,$M=517,ZM=518,QM=519,td=35044,Lp="300 es",tr=2e3,Ol=2001;class Rr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const s=i.indexOf(t);s!==-1&&i.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let s=0,a=i.length;s<a;s++)i[s].call(this,e);e.target=null}}}const kn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Fp=1234567;const Zo=Math.PI/180,ro=180/Math.PI;function Mi(){const r=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(kn[r&255]+kn[r>>8&255]+kn[r>>16&255]+kn[r>>24&255]+"-"+kn[e&255]+kn[e>>8&255]+"-"+kn[e>>16&15|64]+kn[e>>24&255]+"-"+kn[t&63|128]+kn[t>>8&255]+"-"+kn[t>>16&255]+kn[t>>24&255]+kn[n&255]+kn[n>>8&255]+kn[n>>16&255]+kn[n>>24&255]).toLowerCase()}function Fn(r,e,t){return Math.max(e,Math.min(t,r))}function yd(r,e){return(r%e+e)%e}function JM(r,e,t,n,i){return n+(r-e)*(i-n)/(t-e)}function eT(r,e,t){return r!==e?(t-r)/(e-r):0}function Qo(r,e,t){return(1-t)*r+t*e}function tT(r,e,t,n){return Qo(r,e,1-Math.exp(-t*n))}function nT(r,e=1){return e-Math.abs(yd(r,e*2)-e)}function iT(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*(3-2*r))}function rT(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*r*(r*(r*6-15)+10))}function sT(r,e){return r+Math.floor(Math.random()*(e-r+1))}function oT(r,e){return r+Math.random()*(e-r)}function aT(r){return r*(.5-Math.random())}function lT(r){r!==void 0&&(Fp=r);let e=Fp+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function cT(r){return r*Zo}function uT(r){return r*ro}function hT(r){return(r&r-1)===0&&r!==0}function dT(r){return Math.pow(2,Math.ceil(Math.log(r)/Math.LN2))}function fT(r){return Math.pow(2,Math.floor(Math.log(r)/Math.LN2))}function pT(r,e,t,n,i){const s=Math.cos,a=Math.sin,l=s(t/2),u=a(t/2),h=s((e+n)/2),f=a((e+n)/2),p=s((e-n)/2),m=a((e-n)/2),g=s((n-e)/2),x=a((n-e)/2);switch(i){case"XYX":r.set(l*f,u*p,u*m,l*h);break;case"YZY":r.set(u*m,l*f,u*p,l*h);break;case"ZXZ":r.set(u*p,u*m,l*f,l*h);break;case"XZX":r.set(l*f,u*x,u*g,l*h);break;case"YXY":r.set(u*g,l*f,u*x,l*h);break;case"ZYZ":r.set(u*x,u*g,l*f,l*h);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+i)}}function bi(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return r/4294967295;case Uint16Array:return r/65535;case Uint8Array:return r/255;case Int32Array:return Math.max(r/2147483647,-1);case Int16Array:return Math.max(r/32767,-1);case Int8Array:return Math.max(r/127,-1);default:throw new Error("Invalid component type.")}}function $t(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return Math.round(r*4294967295);case Uint16Array:return Math.round(r*65535);case Uint8Array:return Math.round(r*255);case Int32Array:return Math.round(r*2147483647);case Int16Array:return Math.round(r*32767);case Int8Array:return Math.round(r*127);default:throw new Error("Invalid component type.")}}const Rg={DEG2RAD:Zo,RAD2DEG:ro,generateUUID:Mi,clamp:Fn,euclideanModulo:yd,mapLinear:JM,inverseLerp:eT,lerp:Qo,damp:tT,pingpong:nT,smoothstep:iT,smootherstep:rT,randInt:sT,randFloat:oT,randFloatSpread:aT,seededRandom:lT,degToRad:cT,radToDeg:uT,isPowerOfTwo:hT,ceilPowerOfTwo:dT,floorPowerOfTwo:fT,setQuaternionFromProperEuler:pT,normalize:$t,denormalize:bi};class vt{constructor(e=0,t=0){vt.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Fn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),i=Math.sin(t),s=this.x-e.x,a=this.y-e.y;return this.x=s*n-a*i+e.x,this.y=s*i+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class Rt{constructor(e,t,n,i,s,a,l,u,h){Rt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,l,u,h)}set(e,t,n,i,s,a,l,u,h){const f=this.elements;return f[0]=e,f[1]=i,f[2]=l,f[3]=t,f[4]=s,f[5]=u,f[6]=n,f[7]=a,f[8]=h,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],l=n[3],u=n[6],h=n[1],f=n[4],p=n[7],m=n[2],g=n[5],x=n[8],E=i[0],v=i[3],_=i[6],R=i[1],w=i[4],S=i[7],k=i[2],N=i[5],O=i[8];return s[0]=a*E+l*R+u*k,s[3]=a*v+l*w+u*N,s[6]=a*_+l*S+u*O,s[1]=h*E+f*R+p*k,s[4]=h*v+f*w+p*N,s[7]=h*_+f*S+p*O,s[2]=m*E+g*R+x*k,s[5]=m*v+g*w+x*N,s[8]=m*_+g*S+x*O,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],l=e[5],u=e[6],h=e[7],f=e[8];return t*a*f-t*l*h-n*s*f+n*l*u+i*s*h-i*a*u}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],l=e[5],u=e[6],h=e[7],f=e[8],p=f*a-l*h,m=l*u-f*s,g=h*s-a*u,x=t*p+n*m+i*g;if(x===0)return this.set(0,0,0,0,0,0,0,0,0);const E=1/x;return e[0]=p*E,e[1]=(i*h-f*n)*E,e[2]=(l*n-i*a)*E,e[3]=m*E,e[4]=(f*t-i*u)*E,e[5]=(i*s-l*t)*E,e[6]=g*E,e[7]=(n*u-h*t)*E,e[8]=(a*t-n*s)*E,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,s,a,l){const u=Math.cos(s),h=Math.sin(s);return this.set(n*u,n*h,-n*(u*a+h*l)+a+e,-i*h,i*u,-i*(-h*a+u*l)+l+t,0,0,1),this}scale(e,t){return this.premultiply(Tu.makeScale(e,t)),this}rotate(e){return this.premultiply(Tu.makeRotation(-e)),this}translate(e,t){return this.premultiply(Tu.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Tu=new Rt;function Pg(r){for(let e=r.length-1;e>=0;--e)if(r[e]>=65535)return!0;return!1}function ia(r){return document.createElementNS("http://www.w3.org/1999/xhtml",r)}function mT(){const r=ia("canvas");return r.style.display="block",r}const Np={};function Xo(r){r in Np||(Np[r]=!0,console.warn(r))}function gT(r,e,t){return new Promise(function(n,i){function s(){switch(r.clientWaitSync(e,r.SYNC_FLUSH_COMMANDS_BIT,0)){case r.WAIT_FAILED:i();break;case r.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}function _T(r){const e=r.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function vT(r){const e=r.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const zt={enabled:!0,workingColorSpace:qn,spaces:{},convert:function(r,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===Qt&&(r.r=nr(r.r),r.g=nr(r.g),r.b=nr(r.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(r.applyMatrix3(this.spaces[e].toXYZ),r.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===Qt&&(r.r=Ks(r.r),r.g=Ks(r.g),r.b=Ks(r.b))),r},fromWorkingColorSpace:function(r,e){return this.convert(r,this.workingColorSpace,e)},toWorkingColorSpace:function(r,e){return this.convert(r,e,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===xr?Hl:this.spaces[r].transfer},getLuminanceCoefficients:function(r,e=this.workingColorSpace){return r.fromArray(this.spaces[e].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,e,t){return r.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace}};function nr(r){return r<.04045?r*.0773993808:Math.pow(r*.9478672986+.0521327014,2.4)}function Ks(r){return r<.0031308?r*12.92:1.055*Math.pow(r,.41666)-.055}const Op=[.64,.33,.3,.6,.15,.06],Up=[.2126,.7152,.0722],Bp=[.3127,.329],kp=new Rt().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),zp=new Rt().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);zt.define({[qn]:{primaries:Op,whitePoint:Bp,transfer:Hl,toXYZ:kp,fromXYZ:zp,luminanceCoefficients:Up,workingColorSpaceConfig:{unpackColorSpace:Rn},outputColorSpaceConfig:{drawingBufferColorSpace:Rn}},[Rn]:{primaries:Op,whitePoint:Bp,transfer:Qt,toXYZ:kp,fromXYZ:zp,luminanceCoefficients:Up,outputColorSpaceConfig:{drawingBufferColorSpace:Rn}}});let As;class yT{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{As===void 0&&(As=ia("canvas")),As.width=e.width,As.height=e.height;const n=As.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=As}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=ia("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const i=n.getImageData(0,0,e.width,e.height),s=i.data;for(let a=0;a<s.length;a++)s[a]=nr(s[a]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(nr(t[n]/255)*255):t[n]=nr(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let xT=0;class Cg{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:xT++}),this.uuid=Mi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let s;if(Array.isArray(i)){s=[];for(let a=0,l=i.length;a<l;a++)i[a].isDataTexture?s.push(wu(i[a].image)):s.push(wu(i[a]))}else s=wu(i);n.url=s}return t||(e.images[this.uuid]=n),n}}function wu(r){return typeof HTMLImageElement<"u"&&r instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&r instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&r instanceof ImageBitmap?yT.getDataURL(r):r.data?{data:Array.from(r.data),width:r.width,height:r.height,type:r.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let bT=0;class Pn extends Rr{constructor(e=Pn.DEFAULT_IMAGE,t=Pn.DEFAULT_MAPPING,n=br,i=br,s=ci,a=er,l=pi,u=rr,h=Pn.DEFAULT_ANISOTROPY,f=xr){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:bT++}),this.uuid=Mi(),this.name="",this.source=new Cg(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=i,this.magFilter=s,this.minFilter=a,this.anisotropy=h,this.format=l,this.internalFormat=null,this.type=u,this.offset=new vt(0,0),this.repeat=new vt(1,1),this.center=new vt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new Rt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=f,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==pg)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case to:e.x=e.x-Math.floor(e.x);break;case br:e.x=e.x<0?0:1;break;case Fl:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case to:e.y=e.y-Math.floor(e.y);break;case br:e.y=e.y<0?0:1;break;case Fl:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Pn.DEFAULT_IMAGE=null;Pn.DEFAULT_MAPPING=pg;Pn.DEFAULT_ANISOTROPY=1;class Gt{constructor(e=0,t=0,n=0,i=1){Gt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*i+a[12]*s,this.y=a[1]*t+a[5]*n+a[9]*i+a[13]*s,this.z=a[2]*t+a[6]*n+a[10]*i+a[14]*s,this.w=a[3]*t+a[7]*n+a[11]*i+a[15]*s,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,s;const u=e.elements,h=u[0],f=u[4],p=u[8],m=u[1],g=u[5],x=u[9],E=u[2],v=u[6],_=u[10];if(Math.abs(f-m)<.01&&Math.abs(p-E)<.01&&Math.abs(x-v)<.01){if(Math.abs(f+m)<.1&&Math.abs(p+E)<.1&&Math.abs(x+v)<.1&&Math.abs(h+g+_-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const w=(h+1)/2,S=(g+1)/2,k=(_+1)/2,N=(f+m)/4,O=(p+E)/4,H=(x+v)/4;return w>S&&w>k?w<.01?(n=0,i=.707106781,s=.707106781):(n=Math.sqrt(w),i=N/n,s=O/n):S>k?S<.01?(n=.707106781,i=0,s=.707106781):(i=Math.sqrt(S),n=N/i,s=H/i):k<.01?(n=.707106781,i=.707106781,s=0):(s=Math.sqrt(k),n=O/s,i=H/s),this.set(n,i,s,t),this}let R=Math.sqrt((v-x)*(v-x)+(p-E)*(p-E)+(m-f)*(m-f));return Math.abs(R)<.001&&(R=1),this.x=(v-x)/R,this.y=(p-E)/R,this.z=(m-f)/R,this.w=Math.acos((h+g+_-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class ST extends Rr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new Gt(0,0,e,t),this.scissorTest=!1,this.viewport=new Gt(0,0,e,t);const i={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ci,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new Pn(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let l=0;l<a;l++)this.textures[l]=s.clone(),this.textures[l].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let i=0,s=this.textures.length;i<s;i++)this.textures[i].image.width=e,this.textures[i].image.height=t,this.textures[i].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,i=e.textures.length;n<i;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Cg(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class us extends ST{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Dg extends Pn{constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Xn,this.minFilter=Xn,this.wrapR=br,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class ET extends Pn{constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Xn,this.minFilter=Xn,this.wrapR=br,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Dt{constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,s,a,l){let u=n[i+0],h=n[i+1],f=n[i+2],p=n[i+3];const m=s[a+0],g=s[a+1],x=s[a+2],E=s[a+3];if(l===0){e[t+0]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p;return}if(l===1){e[t+0]=m,e[t+1]=g,e[t+2]=x,e[t+3]=E;return}if(p!==E||u!==m||h!==g||f!==x){let v=1-l;const _=u*m+h*g+f*x+p*E,R=_>=0?1:-1,w=1-_*_;if(w>Number.EPSILON){const k=Math.sqrt(w),N=Math.atan2(k,_*R);v=Math.sin(v*N)/k,l=Math.sin(l*N)/k}const S=l*R;if(u=u*v+m*S,h=h*v+g*S,f=f*v+x*S,p=p*v+E*S,v===1-l){const k=1/Math.sqrt(u*u+h*h+f*f+p*p);u*=k,h*=k,f*=k,p*=k}}e[t]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p}static multiplyQuaternionsFlat(e,t,n,i,s,a){const l=n[i],u=n[i+1],h=n[i+2],f=n[i+3],p=s[a],m=s[a+1],g=s[a+2],x=s[a+3];return e[t]=l*x+f*p+u*g-h*m,e[t+1]=u*x+f*m+h*p-l*g,e[t+2]=h*x+f*g+l*m-u*p,e[t+3]=f*x-l*p-u*m-h*g,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,i=e._y,s=e._z,a=e._order,l=Math.cos,u=Math.sin,h=l(n/2),f=l(i/2),p=l(s/2),m=u(n/2),g=u(i/2),x=u(s/2);switch(a){case"XYZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"YXZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"ZXY":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"ZYX":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"YZX":this._x=m*f*p+h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p-m*g*x;break;case"XZY":this._x=m*f*p-h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p+m*g*x;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],i=t[4],s=t[8],a=t[1],l=t[5],u=t[9],h=t[2],f=t[6],p=t[10],m=n+l+p;if(m>0){const g=.5/Math.sqrt(m+1);this._w=.25/g,this._x=(f-u)*g,this._y=(s-h)*g,this._z=(a-i)*g}else if(n>l&&n>p){const g=2*Math.sqrt(1+n-l-p);this._w=(f-u)/g,this._x=.25*g,this._y=(i+a)/g,this._z=(s+h)/g}else if(l>p){const g=2*Math.sqrt(1+l-n-p);this._w=(s-h)/g,this._x=(i+a)/g,this._y=.25*g,this._z=(u+f)/g}else{const g=2*Math.sqrt(1+p-n-l);this._w=(a-i)/g,this._x=(s+h)/g,this._y=(u+f)/g,this._z=.25*g}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Fn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,i=e._y,s=e._z,a=e._w,l=t._x,u=t._y,h=t._z,f=t._w;return this._x=n*f+a*l+i*h-s*u,this._y=i*f+a*u+s*l-n*h,this._z=s*f+a*h+n*u-i*l,this._w=a*f-n*l-i*u-s*h,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,i=this._y,s=this._z,a=this._w;let l=a*e._w+n*e._x+i*e._y+s*e._z;if(l<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,l=-l):this.copy(e),l>=1)return this._w=a,this._x=n,this._y=i,this._z=s,this;const u=1-l*l;if(u<=Number.EPSILON){const g=1-t;return this._w=g*a+t*this._w,this._x=g*n+t*this._x,this._y=g*i+t*this._y,this._z=g*s+t*this._z,this.normalize(),this}const h=Math.sqrt(u),f=Math.atan2(h,l),p=Math.sin((1-t)*f)/h,m=Math.sin(t*f)/h;return this._w=a*p+this._w*m,this._x=n*p+this._x*m,this._y=i*p+this._y*m,this._z=s*p+this._z*m,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),i=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(i*Math.sin(e),i*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class F{constructor(e=0,t=0,n=0){F.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Hp.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Hp.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*i,this.y=s[1]*t+s[4]*n+s[7]*i,this.z=s[2]*t+s[5]*n+s[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=e.elements,a=1/(s[3]*t+s[7]*n+s[11]*i+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*i+s[12])*a,this.y=(s[1]*t+s[5]*n+s[9]*i+s[13])*a,this.z=(s[2]*t+s[6]*n+s[10]*i+s[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,i=this.z,s=e.x,a=e.y,l=e.z,u=e.w,h=2*(a*i-l*n),f=2*(l*t-s*i),p=2*(s*n-a*t);return this.x=t+u*h+a*p-l*f,this.y=n+u*f+l*h-s*p,this.z=i+u*p+s*f-a*h,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*i,this.y=s[1]*t+s[5]*n+s[9]*i,this.z=s[2]*t+s[6]*n+s[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,i=e.y,s=e.z,a=t.x,l=t.y,u=t.z;return this.x=i*u-s*l,this.y=s*a-n*u,this.z=n*l-i*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Au.copy(this).projectOnVector(e),this.sub(Au)}reflect(e){return this.sub(Au.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Fn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Au=new F,Hp=new Dt;class Ti{constructor(e=new F(1/0,1/0,1/0),t=new F(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(_i.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(_i.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=_i.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let a=0,l=s.count;a<l;a++)e.isMesh===!0?e.getVertexPosition(a,_i):_i.fromBufferAttribute(s,a),_i.applyMatrix4(e.matrixWorld),this.expandByPoint(_i);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),Xa.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),Xa.copy(n.boundingBox)),Xa.applyMatrix4(e.matrixWorld),this.union(Xa)}const i=e.children;for(let s=0,a=i.length;s<a;s++)this.expandByObject(i[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,_i),_i.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Fo),qa.subVectors(this.max,Fo),Rs.subVectors(e.a,Fo),Ps.subVectors(e.b,Fo),Cs.subVectors(e.c,Fo),ur.subVectors(Ps,Rs),hr.subVectors(Cs,Ps),$r.subVectors(Rs,Cs);let t=[0,-ur.z,ur.y,0,-hr.z,hr.y,0,-$r.z,$r.y,ur.z,0,-ur.x,hr.z,0,-hr.x,$r.z,0,-$r.x,-ur.y,ur.x,0,-hr.y,hr.x,0,-$r.y,$r.x,0];return!Ru(t,Rs,Ps,Cs,qa)||(t=[1,0,0,0,1,0,0,0,1],!Ru(t,Rs,Ps,Cs,qa))?!1:(Ya.crossVectors(ur,hr),t=[Ya.x,Ya.y,Ya.z],Ru(t,Rs,Ps,Cs,qa))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,_i).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(_i).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Xi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Xi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Xi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Xi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Xi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Xi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Xi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Xi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Xi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Xi=[new F,new F,new F,new F,new F,new F,new F,new F],_i=new F,Xa=new Ti,Rs=new F,Ps=new F,Cs=new F,ur=new F,hr=new F,$r=new F,Fo=new F,qa=new F,Ya=new F,Zr=new F;function Ru(r,e,t,n,i){for(let s=0,a=r.length-3;s<=a;s+=3){Zr.fromArray(r,s);const l=i.x*Math.abs(Zr.x)+i.y*Math.abs(Zr.y)+i.z*Math.abs(Zr.z),u=e.dot(Zr),h=t.dot(Zr),f=n.dot(Zr);if(Math.max(-Math.max(u,h,f),Math.min(u,h,f))>l)return!1}return!0}const MT=new Ti,No=new F,Pu=new F;class Fi{constructor(e=new F,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):MT.setFromPoints(e).getCenter(n);let i=0;for(let s=0,a=e.length;s<a;s++)i=Math.max(i,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;No.subVectors(e,this.center);const t=No.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(No,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Pu.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(No.copy(e.center).add(Pu)),this.expandByPoint(No.copy(e.center).sub(Pu))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const qi=new F,Cu=new F,Ka=new F,dr=new F,Du=new F,$a=new F,Iu=new F;class co{constructor(e=new F,t=new F(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,qi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=qi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(qi.copy(this.origin).addScaledVector(this.direction,t),qi.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){Cu.copy(e).add(t).multiplyScalar(.5),Ka.copy(t).sub(e).normalize(),dr.copy(this.origin).sub(Cu);const s=e.distanceTo(t)*.5,a=-this.direction.dot(Ka),l=dr.dot(this.direction),u=-dr.dot(Ka),h=dr.lengthSq(),f=Math.abs(1-a*a);let p,m,g,x;if(f>0)if(p=a*u-l,m=a*l-u,x=s*f,p>=0)if(m>=-x)if(m<=x){const E=1/f;p*=E,m*=E,g=p*(p+a*m+2*l)+m*(a*p+m+2*u)+h}else m=s,p=Math.max(0,-(a*m+l)),g=-p*p+m*(m+2*u)+h;else m=-s,p=Math.max(0,-(a*m+l)),g=-p*p+m*(m+2*u)+h;else m<=-x?(p=Math.max(0,-(-a*s+l)),m=p>0?-s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h):m<=x?(p=0,m=Math.min(Math.max(-s,-u),s),g=m*(m+2*u)+h):(p=Math.max(0,-(a*s+l)),m=p>0?s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h);else m=a>0?-s:s,p=Math.max(0,-(a*m+l)),g=-p*p+m*(m+2*u)+h;return n&&n.copy(this.origin).addScaledVector(this.direction,p),i&&i.copy(Cu).addScaledVector(Ka,m),g}intersectSphere(e,t){qi.subVectors(e.center,this.origin);const n=qi.dot(this.direction),i=qi.dot(qi)-n*n,s=e.radius*e.radius;if(i>s)return null;const a=Math.sqrt(s-i),l=n-a,u=n+a;return u<0?null:l<0?this.at(u,t):this.at(l,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,s,a,l,u;const h=1/this.direction.x,f=1/this.direction.y,p=1/this.direction.z,m=this.origin;return h>=0?(n=(e.min.x-m.x)*h,i=(e.max.x-m.x)*h):(n=(e.max.x-m.x)*h,i=(e.min.x-m.x)*h),f>=0?(s=(e.min.y-m.y)*f,a=(e.max.y-m.y)*f):(s=(e.max.y-m.y)*f,a=(e.min.y-m.y)*f),n>a||s>i||((s>n||isNaN(n))&&(n=s),(a<i||isNaN(i))&&(i=a),p>=0?(l=(e.min.z-m.z)*p,u=(e.max.z-m.z)*p):(l=(e.max.z-m.z)*p,u=(e.min.z-m.z)*p),n>u||l>i)||((l>n||n!==n)&&(n=l),(u<i||i!==i)&&(i=u),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,qi)!==null}intersectTriangle(e,t,n,i,s){Du.subVectors(t,e),$a.subVectors(n,e),Iu.crossVectors(Du,$a);let a=this.direction.dot(Iu),l;if(a>0){if(i)return null;l=1}else if(a<0)l=-1,a=-a;else return null;dr.subVectors(this.origin,e);const u=l*this.direction.dot($a.crossVectors(dr,$a));if(u<0)return null;const h=l*this.direction.dot(Du.cross(dr));if(h<0||u+h>a)return null;const f=-l*dr.dot(Iu);return f<0?null:this.at(f/a,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class St{constructor(e,t,n,i,s,a,l,u,h,f,p,m,g,x,E,v){St.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,l,u,h,f,p,m,g,x,E,v)}set(e,t,n,i,s,a,l,u,h,f,p,m,g,x,E,v){const _=this.elements;return _[0]=e,_[4]=t,_[8]=n,_[12]=i,_[1]=s,_[5]=a,_[9]=l,_[13]=u,_[2]=h,_[6]=f,_[10]=p,_[14]=m,_[3]=g,_[7]=x,_[11]=E,_[15]=v,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new St().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,i=1/Ds.setFromMatrixColumn(e,0).length(),s=1/Ds.setFromMatrixColumn(e,1).length(),a=1/Ds.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,i=e.y,s=e.z,a=Math.cos(n),l=Math.sin(n),u=Math.cos(i),h=Math.sin(i),f=Math.cos(s),p=Math.sin(s);if(e.order==="XYZ"){const m=a*f,g=a*p,x=l*f,E=l*p;t[0]=u*f,t[4]=-u*p,t[8]=h,t[1]=g+x*h,t[5]=m-E*h,t[9]=-l*u,t[2]=E-m*h,t[6]=x+g*h,t[10]=a*u}else if(e.order==="YXZ"){const m=u*f,g=u*p,x=h*f,E=h*p;t[0]=m+E*l,t[4]=x*l-g,t[8]=a*h,t[1]=a*p,t[5]=a*f,t[9]=-l,t[2]=g*l-x,t[6]=E+m*l,t[10]=a*u}else if(e.order==="ZXY"){const m=u*f,g=u*p,x=h*f,E=h*p;t[0]=m-E*l,t[4]=-a*p,t[8]=x+g*l,t[1]=g+x*l,t[5]=a*f,t[9]=E-m*l,t[2]=-a*h,t[6]=l,t[10]=a*u}else if(e.order==="ZYX"){const m=a*f,g=a*p,x=l*f,E=l*p;t[0]=u*f,t[4]=x*h-g,t[8]=m*h+E,t[1]=u*p,t[5]=E*h+m,t[9]=g*h-x,t[2]=-h,t[6]=l*u,t[10]=a*u}else if(e.order==="YZX"){const m=a*u,g=a*h,x=l*u,E=l*h;t[0]=u*f,t[4]=E-m*p,t[8]=x*p+g,t[1]=p,t[5]=a*f,t[9]=-l*f,t[2]=-h*f,t[6]=g*p+x,t[10]=m-E*p}else if(e.order==="XZY"){const m=a*u,g=a*h,x=l*u,E=l*h;t[0]=u*f,t[4]=-p,t[8]=h*f,t[1]=m*p+E,t[5]=a*f,t[9]=g*p-x,t[2]=x*p-g,t[6]=l*f,t[10]=E*p+m}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(TT,e,wT)}lookAt(e,t,n){const i=this.elements;return ai.subVectors(e,t),ai.lengthSq()===0&&(ai.z=1),ai.normalize(),fr.crossVectors(n,ai),fr.lengthSq()===0&&(Math.abs(n.z)===1?ai.x+=1e-4:ai.z+=1e-4,ai.normalize(),fr.crossVectors(n,ai)),fr.normalize(),Za.crossVectors(ai,fr),i[0]=fr.x,i[4]=Za.x,i[8]=ai.x,i[1]=fr.y,i[5]=Za.y,i[9]=ai.y,i[2]=fr.z,i[6]=Za.z,i[10]=ai.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],l=n[4],u=n[8],h=n[12],f=n[1],p=n[5],m=n[9],g=n[13],x=n[2],E=n[6],v=n[10],_=n[14],R=n[3],w=n[7],S=n[11],k=n[15],N=i[0],O=i[4],H=i[8],D=i[12],A=i[1],z=i[5],Z=i[9],$=i[13],ie=i[2],ae=i[6],X=i[10],he=i[14],te=i[3],ye=i[7],Ee=i[11],ke=i[15];return s[0]=a*N+l*A+u*ie+h*te,s[4]=a*O+l*z+u*ae+h*ye,s[8]=a*H+l*Z+u*X+h*Ee,s[12]=a*D+l*$+u*he+h*ke,s[1]=f*N+p*A+m*ie+g*te,s[5]=f*O+p*z+m*ae+g*ye,s[9]=f*H+p*Z+m*X+g*Ee,s[13]=f*D+p*$+m*he+g*ke,s[2]=x*N+E*A+v*ie+_*te,s[6]=x*O+E*z+v*ae+_*ye,s[10]=x*H+E*Z+v*X+_*Ee,s[14]=x*D+E*$+v*he+_*ke,s[3]=R*N+w*A+S*ie+k*te,s[7]=R*O+w*z+S*ae+k*ye,s[11]=R*H+w*Z+S*X+k*Ee,s[15]=R*D+w*$+S*he+k*ke,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],i=e[8],s=e[12],a=e[1],l=e[5],u=e[9],h=e[13],f=e[2],p=e[6],m=e[10],g=e[14],x=e[3],E=e[7],v=e[11],_=e[15];return x*(+s*u*p-i*h*p-s*l*m+n*h*m+i*l*g-n*u*g)+E*(+t*u*g-t*h*m+s*a*m-i*a*g+i*h*f-s*u*f)+v*(+t*h*p-t*l*g-s*a*p+n*a*g+s*l*f-n*h*f)+_*(-i*l*f-t*u*p+t*l*m+i*a*p-n*a*m+n*u*f)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],l=e[5],u=e[6],h=e[7],f=e[8],p=e[9],m=e[10],g=e[11],x=e[12],E=e[13],v=e[14],_=e[15],R=p*v*h-E*m*h+E*u*g-l*v*g-p*u*_+l*m*_,w=x*m*h-f*v*h-x*u*g+a*v*g+f*u*_-a*m*_,S=f*E*h-x*p*h+x*l*g-a*E*g-f*l*_+a*p*_,k=x*p*u-f*E*u-x*l*m+a*E*m+f*l*v-a*p*v,N=t*R+n*w+i*S+s*k;if(N===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const O=1/N;return e[0]=R*O,e[1]=(E*m*s-p*v*s-E*i*g+n*v*g+p*i*_-n*m*_)*O,e[2]=(l*v*s-E*u*s+E*i*h-n*v*h-l*i*_+n*u*_)*O,e[3]=(p*u*s-l*m*s-p*i*h+n*m*h+l*i*g-n*u*g)*O,e[4]=w*O,e[5]=(f*v*s-x*m*s+x*i*g-t*v*g-f*i*_+t*m*_)*O,e[6]=(x*u*s-a*v*s-x*i*h+t*v*h+a*i*_-t*u*_)*O,e[7]=(a*m*s-f*u*s+f*i*h-t*m*h-a*i*g+t*u*g)*O,e[8]=S*O,e[9]=(x*p*s-f*E*s-x*n*g+t*E*g+f*n*_-t*p*_)*O,e[10]=(a*E*s-x*l*s+x*n*h-t*E*h-a*n*_+t*l*_)*O,e[11]=(f*l*s-a*p*s-f*n*h+t*p*h+a*n*g-t*l*g)*O,e[12]=k*O,e[13]=(f*E*i-x*p*i+x*n*m-t*E*m-f*n*v+t*p*v)*O,e[14]=(x*l*i-a*E*i-x*n*u+t*E*u+a*n*v-t*l*v)*O,e[15]=(a*p*i-f*l*i+f*n*u-t*p*u-a*n*m+t*l*m)*O,this}scale(e){const t=this.elements,n=e.x,i=e.y,s=e.z;return t[0]*=n,t[4]*=i,t[8]*=s,t[1]*=n,t[5]*=i,t[9]*=s,t[2]*=n,t[6]*=i,t[10]*=s,t[3]*=n,t[7]*=i,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),i=Math.sin(t),s=1-n,a=e.x,l=e.y,u=e.z,h=s*a,f=s*l;return this.set(h*a+n,h*l-i*u,h*u+i*l,0,h*l+i*u,f*l+n,f*u-i*a,0,h*u-i*l,f*u+i*a,s*u*u+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,s,a){return this.set(1,n,s,0,e,1,a,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){const i=this.elements,s=t._x,a=t._y,l=t._z,u=t._w,h=s+s,f=a+a,p=l+l,m=s*h,g=s*f,x=s*p,E=a*f,v=a*p,_=l*p,R=u*h,w=u*f,S=u*p,k=n.x,N=n.y,O=n.z;return i[0]=(1-(E+_))*k,i[1]=(g+S)*k,i[2]=(x-w)*k,i[3]=0,i[4]=(g-S)*N,i[5]=(1-(m+_))*N,i[6]=(v+R)*N,i[7]=0,i[8]=(x+w)*O,i[9]=(v-R)*O,i[10]=(1-(m+E))*O,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){const i=this.elements;let s=Ds.set(i[0],i[1],i[2]).length();const a=Ds.set(i[4],i[5],i[6]).length(),l=Ds.set(i[8],i[9],i[10]).length();this.determinant()<0&&(s=-s),e.x=i[12],e.y=i[13],e.z=i[14],vi.copy(this);const h=1/s,f=1/a,p=1/l;return vi.elements[0]*=h,vi.elements[1]*=h,vi.elements[2]*=h,vi.elements[4]*=f,vi.elements[5]*=f,vi.elements[6]*=f,vi.elements[8]*=p,vi.elements[9]*=p,vi.elements[10]*=p,t.setFromRotationMatrix(vi),n.x=s,n.y=a,n.z=l,this}makePerspective(e,t,n,i,s,a,l=tr){const u=this.elements,h=2*s/(t-e),f=2*s/(n-i),p=(t+e)/(t-e),m=(n+i)/(n-i);let g,x;if(l===tr)g=-(a+s)/(a-s),x=-2*a*s/(a-s);else if(l===Ol)g=-a/(a-s),x=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+l);return u[0]=h,u[4]=0,u[8]=p,u[12]=0,u[1]=0,u[5]=f,u[9]=m,u[13]=0,u[2]=0,u[6]=0,u[10]=g,u[14]=x,u[3]=0,u[7]=0,u[11]=-1,u[15]=0,this}makeOrthographic(e,t,n,i,s,a,l=tr){const u=this.elements,h=1/(t-e),f=1/(n-i),p=1/(a-s),m=(t+e)*h,g=(n+i)*f;let x,E;if(l===tr)x=(a+s)*p,E=-2*p;else if(l===Ol)x=s*p,E=-1*p;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+l);return u[0]=2*h,u[4]=0,u[8]=0,u[12]=-m,u[1]=0,u[5]=2*f,u[9]=0,u[13]=-g,u[2]=0,u[6]=0,u[10]=E,u[14]=-x,u[3]=0,u[7]=0,u[11]=0,u[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Ds=new F,vi=new St,TT=new F(0,0,0),wT=new F(1,1,1),fr=new F,Za=new F,ai=new F,Vp=new St,Gp=new Dt;class wi{constructor(e=0,t=0,n=0,i=wi.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const i=e.elements,s=i[0],a=i[4],l=i[8],u=i[1],h=i[5],f=i[9],p=i[2],m=i[6],g=i[10];switch(t){case"XYZ":this._y=Math.asin(Fn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-f,g),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(m,h),this._z=0);break;case"YXZ":this._x=Math.asin(-Fn(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(l,g),this._z=Math.atan2(u,h)):(this._y=Math.atan2(-p,s),this._z=0);break;case"ZXY":this._x=Math.asin(Fn(m,-1,1)),Math.abs(m)<.9999999?(this._y=Math.atan2(-p,g),this._z=Math.atan2(-a,h)):(this._y=0,this._z=Math.atan2(u,s));break;case"ZYX":this._y=Math.asin(-Fn(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(m,g),this._z=Math.atan2(u,s)):(this._x=0,this._z=Math.atan2(-a,h));break;case"YZX":this._z=Math.asin(Fn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(-f,h),this._y=Math.atan2(-p,s)):(this._x=0,this._y=Math.atan2(l,g));break;case"XZY":this._z=Math.asin(-Fn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(m,h),this._y=Math.atan2(l,s)):(this._x=Math.atan2(-f,g),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Vp.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Vp,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Gp.setFromEuler(this),this.setFromQuaternion(Gp,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}wi.DEFAULT_ORDER="XYZ";class xd{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let AT=0;const Wp=new F,Is=new Dt,Yi=new St,Qa=new F,Oo=new F,RT=new F,PT=new Dt,jp=new F(1,0,0),Xp=new F(0,1,0),qp=new F(0,0,1),Yp={type:"added"},CT={type:"removed"},Ls={type:"childadded",child:null},Lu={type:"childremoved",child:null};class an extends Rr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:AT++}),this.uuid=Mi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=an.DEFAULT_UP.clone();const e=new F,t=new wi,n=new Dt,i=new F(1,1,1);function s(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new St},normalMatrix:{value:new Rt}}),this.matrix=new St,this.matrixWorld=new St,this.matrixAutoUpdate=an.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=an.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new xd,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.multiply(Is),this}rotateOnWorldAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.premultiply(Is),this}rotateX(e){return this.rotateOnAxis(jp,e)}rotateY(e){return this.rotateOnAxis(Xp,e)}rotateZ(e){return this.rotateOnAxis(qp,e)}translateOnAxis(e,t){return Wp.copy(e).applyQuaternion(this.quaternion),this.position.add(Wp.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(jp,e)}translateY(e){return this.translateOnAxis(Xp,e)}translateZ(e){return this.translateOnAxis(qp,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Yi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Qa.copy(e):Qa.set(e,t,n);const i=this.parent;this.updateWorldMatrix(!0,!1),Oo.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Yi.lookAt(Oo,Qa,this.up):Yi.lookAt(Qa,Oo,this.up),this.quaternion.setFromRotationMatrix(Yi),i&&(Yi.extractRotation(i.matrixWorld),Is.setFromRotationMatrix(Yi),this.quaternion.premultiply(Is.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(Yp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(CT),Lu.child=e,this.dispatchEvent(Lu),Lu.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Yi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Yi.multiply(e.parent.matrixWorld)),e.applyMatrix4(Yi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(Yp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Oo,e,RT),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Oo,PT,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),i.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(i.type="BatchedMesh",i.perObjectFrustumCulled=this.perObjectFrustumCulled,i.sortObjects=this.sortObjects,i.drawRanges=this._drawRanges,i.reservedRanges=this._reservedRanges,i.visibility=this._visibility,i.active=this._active,i.bounds=this._bounds.map(l=>({boxInitialized:l.boxInitialized,boxMin:l.box.min.toArray(),boxMax:l.box.max.toArray(),sphereInitialized:l.sphereInitialized,sphereRadius:l.sphere.radius,sphereCenter:l.sphere.center.toArray()})),i.maxInstanceCount=this._maxInstanceCount,i.maxVertexCount=this._maxVertexCount,i.maxIndexCount=this._maxIndexCount,i.geometryInitialized=this._geometryInitialized,i.geometryCount=this._geometryCount,i.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(i.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(i.boundingSphere={center:i.boundingSphere.center.toArray(),radius:i.boundingSphere.radius}),this.boundingBox!==null&&(i.boundingBox={min:i.boundingBox.min.toArray(),max:i.boundingBox.max.toArray()}));function s(l,u){return l[u.uuid]===void 0&&(l[u.uuid]=u.toJSON(e)),u.uuid}if(this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=s(e.geometries,this.geometry);const l=this.geometry.parameters;if(l!==void 0&&l.shapes!==void 0){const u=l.shapes;if(Array.isArray(u))for(let h=0,f=u.length;h<f;h++){const p=u[h];s(e.shapes,p)}else s(e.shapes,u)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const l=[];for(let u=0,h=this.material.length;u<h;u++)l.push(s(e.materials,this.material[u]));i.material=l}else i.material=s(e.materials,this.material);if(this.children.length>0){i.children=[];for(let l=0;l<this.children.length;l++)i.children.push(this.children[l].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let l=0;l<this.animations.length;l++){const u=this.animations[l];i.animations.push(s(e.animations,u))}}if(t){const l=a(e.geometries),u=a(e.materials),h=a(e.textures),f=a(e.images),p=a(e.shapes),m=a(e.skeletons),g=a(e.animations),x=a(e.nodes);l.length>0&&(n.geometries=l),u.length>0&&(n.materials=u),h.length>0&&(n.textures=h),f.length>0&&(n.images=f),p.length>0&&(n.shapes=p),m.length>0&&(n.skeletons=m),g.length>0&&(n.animations=g),x.length>0&&(n.nodes=x)}return n.object=i,n;function a(l){const u=[];for(const h in l){const f=l[h];delete f.metadata,u.push(f)}return u}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const i=e.children[n];this.add(i.clone())}return this}}an.DEFAULT_UP=new F(0,1,0);an.DEFAULT_MATRIX_AUTO_UPDATE=!0;an.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const yi=new F,Ki=new F,Fu=new F,$i=new F,Fs=new F,Ns=new F,Kp=new F,Nu=new F,Ou=new F,Uu=new F,Bu=new Gt,ku=new Gt,zu=new Gt;class Si{constructor(e=new F,t=new F,n=new F){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),yi.subVectors(e,t),i.cross(yi);const s=i.lengthSq();return s>0?i.multiplyScalar(1/Math.sqrt(s)):i.set(0,0,0)}static getBarycoord(e,t,n,i,s){yi.subVectors(i,t),Ki.subVectors(n,t),Fu.subVectors(e,t);const a=yi.dot(yi),l=yi.dot(Ki),u=yi.dot(Fu),h=Ki.dot(Ki),f=Ki.dot(Fu),p=a*h-l*l;if(p===0)return s.set(0,0,0),null;const m=1/p,g=(h*u-l*f)*m,x=(a*f-l*u)*m;return s.set(1-g-x,x,g)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,$i)===null?!1:$i.x>=0&&$i.y>=0&&$i.x+$i.y<=1}static getInterpolation(e,t,n,i,s,a,l,u){return this.getBarycoord(e,t,n,i,$i)===null?(u.x=0,u.y=0,"z"in u&&(u.z=0),"w"in u&&(u.w=0),null):(u.setScalar(0),u.addScaledVector(s,$i.x),u.addScaledVector(a,$i.y),u.addScaledVector(l,$i.z),u)}static getInterpolatedAttribute(e,t,n,i,s,a){return Bu.setScalar(0),ku.setScalar(0),zu.setScalar(0),Bu.fromBufferAttribute(e,t),ku.fromBufferAttribute(e,n),zu.fromBufferAttribute(e,i),a.setScalar(0),a.addScaledVector(Bu,s.x),a.addScaledVector(ku,s.y),a.addScaledVector(zu,s.z),a}static isFrontFacing(e,t,n,i){return yi.subVectors(n,t),Ki.subVectors(e,t),yi.cross(Ki).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return yi.subVectors(this.c,this.b),Ki.subVectors(this.a,this.b),yi.cross(Ki).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Si.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Si.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,i,s){return Si.getInterpolation(e,this.a,this.b,this.c,t,n,i,s)}containsPoint(e){return Si.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Si.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,i=this.b,s=this.c;let a,l;Fs.subVectors(i,n),Ns.subVectors(s,n),Nu.subVectors(e,n);const u=Fs.dot(Nu),h=Ns.dot(Nu);if(u<=0&&h<=0)return t.copy(n);Ou.subVectors(e,i);const f=Fs.dot(Ou),p=Ns.dot(Ou);if(f>=0&&p<=f)return t.copy(i);const m=u*p-f*h;if(m<=0&&u>=0&&f<=0)return a=u/(u-f),t.copy(n).addScaledVector(Fs,a);Uu.subVectors(e,s);const g=Fs.dot(Uu),x=Ns.dot(Uu);if(x>=0&&g<=x)return t.copy(s);const E=g*h-u*x;if(E<=0&&h>=0&&x<=0)return l=h/(h-x),t.copy(n).addScaledVector(Ns,l);const v=f*x-g*p;if(v<=0&&p-f>=0&&g-x>=0)return Kp.subVectors(s,i),l=(p-f)/(p-f+(g-x)),t.copy(i).addScaledVector(Kp,l);const _=1/(v+E+m);return a=E*_,l=m*_,t.copy(n).addScaledVector(Fs,a).addScaledVector(Ns,l)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Ig={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},pr={h:0,s:0,l:0},Ja={h:0,s:0,l:0};function Hu(r,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?r+(e-r)*6*t:t<1/2?e:t<2/3?r+(e-r)*6*(2/3-t):r}class pt{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const i=e;i&&i.isColor?this.copy(i):typeof i=="number"?this.setHex(i):typeof i=="string"&&this.setStyle(i)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Rn){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,zt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=zt.workingColorSpace){return this.r=e,this.g=t,this.b=n,zt.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=zt.workingColorSpace){if(e=yd(e,1),t=Fn(t,0,1),n=Fn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,a=2*n-s;this.r=Hu(a,s,e+1/3),this.g=Hu(a,s,e),this.b=Hu(a,s,e-1/3)}return zt.toWorkingColorSpace(this,i),this}setStyle(e,t=Rn){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let i;if(i=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const a=i[1],l=i[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(l))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(l))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(l))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=i[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Rn){const n=Ig[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=nr(e.r),this.g=nr(e.g),this.b=nr(e.b),this}copyLinearToSRGB(e){return this.r=Ks(e.r),this.g=Ks(e.g),this.b=Ks(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Rn){return zt.fromWorkingColorSpace(zn.copy(this),e),Math.round(Fn(zn.r*255,0,255))*65536+Math.round(Fn(zn.g*255,0,255))*256+Math.round(Fn(zn.b*255,0,255))}getHexString(e=Rn){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=zt.workingColorSpace){zt.fromWorkingColorSpace(zn.copy(this),t);const n=zn.r,i=zn.g,s=zn.b,a=Math.max(n,i,s),l=Math.min(n,i,s);let u,h;const f=(l+a)/2;if(l===a)u=0,h=0;else{const p=a-l;switch(h=f<=.5?p/(a+l):p/(2-a-l),a){case n:u=(i-s)/p+(i<s?6:0);break;case i:u=(s-n)/p+2;break;case s:u=(n-i)/p+4;break}u/=6}return e.h=u,e.s=h,e.l=f,e}getRGB(e,t=zt.workingColorSpace){return zt.fromWorkingColorSpace(zn.copy(this),t),e.r=zn.r,e.g=zn.g,e.b=zn.b,e}getStyle(e=Rn){zt.fromWorkingColorSpace(zn.copy(this),e);const t=zn.r,n=zn.g,i=zn.b;return e!==Rn?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${i.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(i*255)})`}offsetHSL(e,t,n){return this.getHSL(pr),this.setHSL(pr.h+e,pr.s+t,pr.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(pr),e.getHSL(Ja);const n=Qo(pr.h,Ja.h,t),i=Qo(pr.s,Ja.s,t),s=Qo(pr.l,Ja.l,t);return this.setHSL(n,i,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,i=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*i,this.g=s[1]*t+s[4]*n+s[7]*i,this.b=s[2]*t+s[5]*n+s[8]*i,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const zn=new pt;pt.NAMES=Ig;let DT=0;class Li extends Rr{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:DT++}),this.uuid=Mi(),this.name="",this.blending=qs,this.side=ir,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=_h,this.blendDst=vh,this.blendEquation=os,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new pt(0,0,0),this.blendAlpha=0,this.depthFunc=Qs,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Ip,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=ws,this.stencilZFail=ws,this.stencilZPass=ws,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const i=this[t];if(i===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==qs&&(n.blending=this.blending),this.side!==ir&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==_h&&(n.blendSrc=this.blendSrc),this.blendDst!==vh&&(n.blendDst=this.blendDst),this.blendEquation!==os&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Qs&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Ip&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==ws&&(n.stencilFail=this.stencilFail),this.stencilZFail!==ws&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==ws&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(s){const a=[];for(const l in s){const u=s[l];delete u.metadata,a.push(u)}return a}if(t){const s=i(e.textures),a=i(e.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const i=t.length;n=new Array(i);for(let s=0;s!==i;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class mi extends Li{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new pt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new wi,this.combine=dg,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const _n=new F,el=new vt;class pn{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=td,this.updateRanges=[],this.gpuType=Ei,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,s=this.itemSize;i<s;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)el.fromBufferAttribute(this,t),el.applyMatrix3(e),this.setXY(t,el.x,el.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)_n.fromBufferAttribute(this,t),_n.applyMatrix3(e),this.setXYZ(t,_n.x,_n.y,_n.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)_n.fromBufferAttribute(this,t),_n.applyMatrix4(e),this.setXYZ(t,_n.x,_n.y,_n.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)_n.fromBufferAttribute(this,t),_n.applyNormalMatrix(e),this.setXYZ(t,_n.x,_n.y,_n.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)_n.fromBufferAttribute(this,t),_n.transformDirection(e),this.setXYZ(t,_n.x,_n.y,_n.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=bi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=$t(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=bi(t,this.array)),t}setX(e,t){return this.normalized&&(t=$t(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=bi(t,this.array)),t}setY(e,t){return this.normalized&&(t=$t(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=bi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=$t(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=bi(t,this.array)),t}setW(e,t){return this.normalized&&(t=$t(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=$t(t,this.array),n=$t(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=$t(t,this.array),n=$t(n,this.array),i=$t(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e*=this.itemSize,this.normalized&&(t=$t(t,this.array),n=$t(n,this.array),i=$t(i,this.array),s=$t(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==td&&(e.usage=this.usage),e}}class Lg extends pn{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Fg extends pn{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class Wt extends pn{constructor(e,t,n){super(new Float32Array(e),t,n)}}let IT=0;const di=new St,Vu=new an,Os=new F,li=new Ti,Uo=new Ti,An=new F;class Sn extends Rr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:IT++}),this.uuid=Mi(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Pg(e)?Fg:Lg)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new Rt().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return di.makeRotationFromQuaternion(e),this.applyMatrix4(di),this}rotateX(e){return di.makeRotationX(e),this.applyMatrix4(di),this}rotateY(e){return di.makeRotationY(e),this.applyMatrix4(di),this}rotateZ(e){return di.makeRotationZ(e),this.applyMatrix4(di),this}translate(e,t,n){return di.makeTranslation(e,t,n),this.applyMatrix4(di),this}scale(e,t,n){return di.makeScale(e,t,n),this.applyMatrix4(di),this}lookAt(e){return Vu.lookAt(e),Vu.updateMatrix(),this.applyMatrix4(Vu.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Os).negate(),this.translate(Os.x,Os.y,Os.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let i=0,s=e.length;i<s;i++){const a=e[i];n.push(a.x,a.y,a.z||0)}this.setAttribute("position",new Wt(n,3))}else{for(let n=0,i=t.count;n<i;n++){const s=e[n];t.setXYZ(n,s.x,s.y,s.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Ti);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new F(-1/0,-1/0,-1/0),new F(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){const s=t[n];li.setFromBufferAttribute(s),this.morphTargetsRelative?(An.addVectors(this.boundingBox.min,li.min),this.boundingBox.expandByPoint(An),An.addVectors(this.boundingBox.max,li.max),this.boundingBox.expandByPoint(An)):(this.boundingBox.expandByPoint(li.min),this.boundingBox.expandByPoint(li.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Fi);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new F,1/0);return}if(e){const n=this.boundingSphere.center;if(li.setFromBufferAttribute(e),t)for(let s=0,a=t.length;s<a;s++){const l=t[s];Uo.setFromBufferAttribute(l),this.morphTargetsRelative?(An.addVectors(li.min,Uo.min),li.expandByPoint(An),An.addVectors(li.max,Uo.max),li.expandByPoint(An)):(li.expandByPoint(Uo.min),li.expandByPoint(Uo.max))}li.getCenter(n);let i=0;for(let s=0,a=e.count;s<a;s++)An.fromBufferAttribute(e,s),i=Math.max(i,n.distanceToSquared(An));if(t)for(let s=0,a=t.length;s<a;s++){const l=t[s],u=this.morphTargetsRelative;for(let h=0,f=l.count;h<f;h++)An.fromBufferAttribute(l,h),u&&(Os.fromBufferAttribute(e,h),An.add(Os)),i=Math.max(i,n.distanceToSquared(An))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,i=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new pn(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),l=[],u=[];for(let H=0;H<n.count;H++)l[H]=new F,u[H]=new F;const h=new F,f=new F,p=new F,m=new vt,g=new vt,x=new vt,E=new F,v=new F;function _(H,D,A){h.fromBufferAttribute(n,H),f.fromBufferAttribute(n,D),p.fromBufferAttribute(n,A),m.fromBufferAttribute(s,H),g.fromBufferAttribute(s,D),x.fromBufferAttribute(s,A),f.sub(h),p.sub(h),g.sub(m),x.sub(m);const z=1/(g.x*x.y-x.x*g.y);isFinite(z)&&(E.copy(f).multiplyScalar(x.y).addScaledVector(p,-g.y).multiplyScalar(z),v.copy(p).multiplyScalar(g.x).addScaledVector(f,-x.x).multiplyScalar(z),l[H].add(E),l[D].add(E),l[A].add(E),u[H].add(v),u[D].add(v),u[A].add(v))}let R=this.groups;R.length===0&&(R=[{start:0,count:e.count}]);for(let H=0,D=R.length;H<D;++H){const A=R[H],z=A.start,Z=A.count;for(let $=z,ie=z+Z;$<ie;$+=3)_(e.getX($+0),e.getX($+1),e.getX($+2))}const w=new F,S=new F,k=new F,N=new F;function O(H){k.fromBufferAttribute(i,H),N.copy(k);const D=l[H];w.copy(D),w.sub(k.multiplyScalar(k.dot(D))).normalize(),S.crossVectors(N,D);const z=S.dot(u[H])<0?-1:1;a.setXYZW(H,w.x,w.y,w.z,z)}for(let H=0,D=R.length;H<D;++H){const A=R[H],z=A.start,Z=A.count;for(let $=z,ie=z+Z;$<ie;$+=3)O(e.getX($+0)),O(e.getX($+1)),O(e.getX($+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new pn(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let m=0,g=n.count;m<g;m++)n.setXYZ(m,0,0,0);const i=new F,s=new F,a=new F,l=new F,u=new F,h=new F,f=new F,p=new F;if(e)for(let m=0,g=e.count;m<g;m+=3){const x=e.getX(m+0),E=e.getX(m+1),v=e.getX(m+2);i.fromBufferAttribute(t,x),s.fromBufferAttribute(t,E),a.fromBufferAttribute(t,v),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),l.fromBufferAttribute(n,x),u.fromBufferAttribute(n,E),h.fromBufferAttribute(n,v),l.add(f),u.add(f),h.add(f),n.setXYZ(x,l.x,l.y,l.z),n.setXYZ(E,u.x,u.y,u.z),n.setXYZ(v,h.x,h.y,h.z)}else for(let m=0,g=t.count;m<g;m+=3)i.fromBufferAttribute(t,m+0),s.fromBufferAttribute(t,m+1),a.fromBufferAttribute(t,m+2),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),n.setXYZ(m+0,f.x,f.y,f.z),n.setXYZ(m+1,f.x,f.y,f.z),n.setXYZ(m+2,f.x,f.y,f.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)An.fromBufferAttribute(e,t),An.normalize(),e.setXYZ(t,An.x,An.y,An.z)}toNonIndexed(){function e(l,u){const h=l.array,f=l.itemSize,p=l.normalized,m=new h.constructor(u.length*f);let g=0,x=0;for(let E=0,v=u.length;E<v;E++){l.isInterleavedBufferAttribute?g=u[E]*l.data.stride+l.offset:g=u[E]*f;for(let _=0;_<f;_++)m[x++]=h[g++]}return new pn(m,f,p)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Sn,n=this.index.array,i=this.attributes;for(const l in i){const u=i[l],h=e(u,n);t.setAttribute(l,h)}const s=this.morphAttributes;for(const l in s){const u=[],h=s[l];for(let f=0,p=h.length;f<p;f++){const m=h[f],g=e(m,n);u.push(g)}t.morphAttributes[l]=u}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let l=0,u=a.length;l<u;l++){const h=a[l];t.addGroup(h.start,h.count,h.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const u=this.parameters;for(const h in u)u[h]!==void 0&&(e[h]=u[h]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const u in n){const h=n[u];e.data.attributes[u]=h.toJSON(e.data)}const i={};let s=!1;for(const u in this.morphAttributes){const h=this.morphAttributes[u],f=[];for(let p=0,m=h.length;p<m;p++){const g=h[p];f.push(g.toJSON(e.data))}f.length>0&&(i[u]=f,s=!0)}s&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const l=this.boundingSphere;return l!==null&&(e.data.boundingSphere={center:l.center.toArray(),radius:l.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const i=e.attributes;for(const h in i){const f=i[h];this.setAttribute(h,f.clone(t))}const s=e.morphAttributes;for(const h in s){const f=[],p=s[h];for(let m=0,g=p.length;m<g;m++)f.push(p[m].clone(t));this.morphAttributes[h]=f}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let h=0,f=a.length;h<f;h++){const p=a[h];this.addGroup(p.start,p.count,p.materialIndex)}const l=e.boundingBox;l!==null&&(this.boundingBox=l.clone());const u=e.boundingSphere;return u!==null&&(this.boundingSphere=u.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const $p=new St,Qr=new co,tl=new Fi,Zp=new F,nl=new F,il=new F,rl=new F,Gu=new F,sl=new F,Qp=new F,ol=new F;class Pe extends an{constructor(e=new Sn,t=new mi){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const l=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[l]=s}}}}getVertexPosition(e,t){const n=this.geometry,i=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(i,e);const l=this.morphTargetInfluences;if(s&&l){sl.set(0,0,0);for(let u=0,h=s.length;u<h;u++){const f=l[u],p=s[u];f!==0&&(Gu.fromBufferAttribute(p,e),a?sl.addScaledVector(Gu,f):sl.addScaledVector(Gu.sub(t),f))}t.add(sl)}return t}raycast(e,t){const n=this.geometry,i=this.material,s=this.matrixWorld;i!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),tl.copy(n.boundingSphere),tl.applyMatrix4(s),Qr.copy(e.ray).recast(e.near),!(tl.containsPoint(Qr.origin)===!1&&(Qr.intersectSphere(tl,Zp)===null||Qr.origin.distanceToSquared(Zp)>(e.far-e.near)**2))&&($p.copy(s).invert(),Qr.copy(e.ray).applyMatrix4($p),!(n.boundingBox!==null&&Qr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Qr)))}_computeIntersections(e,t,n){let i;const s=this.geometry,a=this.material,l=s.index,u=s.attributes.position,h=s.attributes.uv,f=s.attributes.uv1,p=s.attributes.normal,m=s.groups,g=s.drawRange;if(l!==null)if(Array.isArray(a))for(let x=0,E=m.length;x<E;x++){const v=m[x],_=a[v.materialIndex],R=Math.max(v.start,g.start),w=Math.min(l.count,Math.min(v.start+v.count,g.start+g.count));for(let S=R,k=w;S<k;S+=3){const N=l.getX(S),O=l.getX(S+1),H=l.getX(S+2);i=al(this,_,e,n,h,f,p,N,O,H),i&&(i.faceIndex=Math.floor(S/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),E=Math.min(l.count,g.start+g.count);for(let v=x,_=E;v<_;v+=3){const R=l.getX(v),w=l.getX(v+1),S=l.getX(v+2);i=al(this,a,e,n,h,f,p,R,w,S),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}else if(u!==void 0)if(Array.isArray(a))for(let x=0,E=m.length;x<E;x++){const v=m[x],_=a[v.materialIndex],R=Math.max(v.start,g.start),w=Math.min(u.count,Math.min(v.start+v.count,g.start+g.count));for(let S=R,k=w;S<k;S+=3){const N=S,O=S+1,H=S+2;i=al(this,_,e,n,h,f,p,N,O,H),i&&(i.faceIndex=Math.floor(S/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),E=Math.min(u.count,g.start+g.count);for(let v=x,_=E;v<_;v+=3){const R=v,w=v+1,S=v+2;i=al(this,a,e,n,h,f,p,R,w,S),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}}}function LT(r,e,t,n,i,s,a,l){let u;if(e.side===Jn?u=n.intersectTriangle(a,s,i,!0,l):u=n.intersectTriangle(i,s,a,e.side===ir,l),u===null)return null;ol.copy(l),ol.applyMatrix4(r.matrixWorld);const h=t.ray.origin.distanceTo(ol);return h<t.near||h>t.far?null:{distance:h,point:ol.clone(),object:r}}function al(r,e,t,n,i,s,a,l,u,h){r.getVertexPosition(l,nl),r.getVertexPosition(u,il),r.getVertexPosition(h,rl);const f=LT(r,e,t,n,nl,il,rl,Qp);if(f){const p=new F;Si.getBarycoord(Qp,nl,il,rl,p),i&&(f.uv=Si.getInterpolatedAttribute(i,l,u,h,p,new vt)),s&&(f.uv1=Si.getInterpolatedAttribute(s,l,u,h,p,new vt)),a&&(f.normal=Si.getInterpolatedAttribute(a,l,u,h,p,new F),f.normal.dot(n.direction)>0&&f.normal.multiplyScalar(-1));const m={a:l,b:u,c:h,normal:new F,materialIndex:0};Si.getNormal(nl,il,rl,m.normal),f.face=m,f.barycoord=p}return f}class dn extends Sn{constructor(e=1,t=1,n=1,i=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:s,depthSegments:a};const l=this;i=Math.floor(i),s=Math.floor(s),a=Math.floor(a);const u=[],h=[],f=[],p=[];let m=0,g=0;x("z","y","x",-1,-1,n,t,e,a,s,0),x("z","y","x",1,-1,n,t,-e,a,s,1),x("x","z","y",1,1,e,n,t,i,a,2),x("x","z","y",1,-1,e,n,-t,i,a,3),x("x","y","z",1,-1,e,t,n,i,s,4),x("x","y","z",-1,-1,e,t,-n,i,s,5),this.setIndex(u),this.setAttribute("position",new Wt(h,3)),this.setAttribute("normal",new Wt(f,3)),this.setAttribute("uv",new Wt(p,2));function x(E,v,_,R,w,S,k,N,O,H,D){const A=S/O,z=k/H,Z=S/2,$=k/2,ie=N/2,ae=O+1,X=H+1;let he=0,te=0;const ye=new F;for(let Ee=0;Ee<X;Ee++){const ke=Ee*z-$;for(let Xe=0;Xe<ae;Xe++){const Tt=Xe*A-Z;ye[E]=Tt*R,ye[v]=ke*w,ye[_]=ie,h.push(ye.x,ye.y,ye.z),ye[E]=0,ye[v]=0,ye[_]=N>0?1:-1,f.push(ye.x,ye.y,ye.z),p.push(Xe/O),p.push(1-Ee/H),he+=1}}for(let Ee=0;Ee<H;Ee++)for(let ke=0;ke<O;ke++){const Xe=m+ke+ae*Ee,Tt=m+ke+ae*(Ee+1),ce=m+(ke+1)+ae*(Ee+1),ge=m+(ke+1)+ae*Ee;u.push(Xe,Tt,ge),u.push(Tt,ce,ge),te+=6}l.addGroup(g,te,D),g+=te,m+=he}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new dn(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function so(r){const e={};for(const t in r){e[t]={};for(const n in r[t]){const i=r[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?i.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}function Wn(r){const e={};for(let t=0;t<r.length;t++){const n=so(r[t]);for(const i in n)e[i]=n[i]}return e}function FT(r){const e=[];for(let t=0;t<r.length;t++)e.push(r[t].clone());return e}function Ng(r){const e=r.getRenderTarget();return e===null?r.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:zt.workingColorSpace}const NT={clone:so,merge:Wn};var OT=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,UT=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Tr extends Li{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=OT,this.fragmentShader=UT,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=so(e.uniforms),this.uniformsGroups=FT(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const i in this.uniforms){const a=this.uniforms[i].value;a&&a.isTexture?t.uniforms[i]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[i]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[i]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[i]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[i]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[i]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[i]={type:"m4",value:a.toArray()}:t.uniforms[i]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Og extends an{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new St,this.projectionMatrix=new St,this.projectionMatrixInverse=new St,this.coordinateSystem=tr}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const mr=new F,Jp=new vt,em=new vt;class jn extends Og{constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=ro*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Zo*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return ro*2*Math.atan(Math.tan(Zo*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){mr.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(mr.x,mr.y).multiplyScalar(-e/mr.z),mr.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(mr.x,mr.y).multiplyScalar(-e/mr.z)}getViewSize(e,t){return this.getViewBounds(e,Jp,em),t.subVectors(em,Jp)}setViewOffset(e,t,n,i,s,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Zo*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,s=-.5*i;const a=this.view;if(this.view!==null&&this.view.enabled){const u=a.fullWidth,h=a.fullHeight;s+=a.offsetX*i/u,t-=a.offsetY*n/h,i*=a.width/u,n*=a.height/h}const l=this.filmOffset;l!==0&&(s+=e*l/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+i,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Us=-90,Bs=1;class BT extends an{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const i=new jn(Us,Bs,e,t);i.layers=this.layers,this.add(i);const s=new jn(Us,Bs,e,t);s.layers=this.layers,this.add(s);const a=new jn(Us,Bs,e,t);a.layers=this.layers,this.add(a);const l=new jn(Us,Bs,e,t);l.layers=this.layers,this.add(l);const u=new jn(Us,Bs,e,t);u.layers=this.layers,this.add(u);const h=new jn(Us,Bs,e,t);h.layers=this.layers,this.add(h)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,i,s,a,l,u]=t;for(const h of t)this.remove(h);if(e===tr)n.up.set(0,1,0),n.lookAt(1,0,0),i.up.set(0,1,0),i.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),l.up.set(0,1,0),l.lookAt(0,0,1),u.up.set(0,1,0),u.lookAt(0,0,-1);else if(e===Ol)n.up.set(0,-1,0),n.lookAt(-1,0,0),i.up.set(0,-1,0),i.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),l.up.set(0,-1,0),l.lookAt(0,0,1),u.up.set(0,-1,0),u.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const h of t)this.add(h),h.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:i}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,a,l,u,h,f]=this.children,p=e.getRenderTarget(),m=e.getActiveCubeFace(),g=e.getActiveMipmapLevel(),x=e.xr.enabled;e.xr.enabled=!1;const E=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,i),e.render(t,s),e.setRenderTarget(n,1,i),e.render(t,a),e.setRenderTarget(n,2,i),e.render(t,l),e.setRenderTarget(n,3,i),e.render(t,u),e.setRenderTarget(n,4,i),e.render(t,h),n.texture.generateMipmaps=E,e.setRenderTarget(n,5,i),e.render(t,f),e.setRenderTarget(p,m,g),e.xr.enabled=x,n.texture.needsPMREMUpdate=!0}}class Ug extends Pn{constructor(e,t,n,i,s,a,l,u,h,f){e=e!==void 0?e:[],t=t!==void 0?t:Js,super(e,t,n,i,s,a,l,u,h,f),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class kT extends us{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new Ug(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ci}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},i=new dn(5,5,5),s=new Tr({name:"CubemapFromEquirect",uniforms:so(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Jn,blending:Er});s.uniforms.tEquirect.value=t;const a=new Pe(i,s),l=t.minFilter;return t.minFilter===er&&(t.minFilter=ci),new BT(1,10,this).update(e,a),t.minFilter=l,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,i){const s=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,i);e.setRenderTarget(s)}}const Wu=new F,zT=new F,HT=new Rt;class yr{constructor(e=new F(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const i=Wu.subVectors(n,t).cross(zT.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Wu),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/i;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||HT.getNormalMatrix(e),i=this.coplanarPoint(Wu).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Jr=new Fi,ll=new F;class bd{constructor(e=new yr,t=new yr,n=new yr,i=new yr,s=new yr,a=new yr){this.planes=[e,t,n,i,s,a]}set(e,t,n,i,s,a){const l=this.planes;return l[0].copy(e),l[1].copy(t),l[2].copy(n),l[3].copy(i),l[4].copy(s),l[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=tr){const n=this.planes,i=e.elements,s=i[0],a=i[1],l=i[2],u=i[3],h=i[4],f=i[5],p=i[6],m=i[7],g=i[8],x=i[9],E=i[10],v=i[11],_=i[12],R=i[13],w=i[14],S=i[15];if(n[0].setComponents(u-s,m-h,v-g,S-_).normalize(),n[1].setComponents(u+s,m+h,v+g,S+_).normalize(),n[2].setComponents(u+a,m+f,v+x,S+R).normalize(),n[3].setComponents(u-a,m-f,v-x,S-R).normalize(),n[4].setComponents(u-l,m-p,v-E,S-w).normalize(),t===tr)n[5].setComponents(u+l,m+p,v+E,S+w).normalize();else if(t===Ol)n[5].setComponents(l,p,E,w).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Jr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Jr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Jr)}intersectsSprite(e){return Jr.center.set(0,0,0),Jr.radius=.7071067811865476,Jr.applyMatrix4(e.matrixWorld),this.intersectsSphere(Jr)}intersectsSphere(e){const t=this.planes,n=e.center,i=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const i=t[n];if(ll.x=i.normal.x>0?e.max.x:e.min.x,ll.y=i.normal.y>0?e.max.y:e.min.y,ll.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(ll)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Bg(){let r=null,e=!1,t=null,n=null;function i(s,a){t(s,a),n=r.requestAnimationFrame(i)}return{start:function(){e!==!0&&t!==null&&(n=r.requestAnimationFrame(i),e=!0)},stop:function(){r.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){r=s}}}function VT(r){const e=new WeakMap;function t(l,u){const h=l.array,f=l.usage,p=h.byteLength,m=r.createBuffer();r.bindBuffer(u,m),r.bufferData(u,h,f),l.onUploadCallback();let g;if(h instanceof Float32Array)g=r.FLOAT;else if(h instanceof Uint16Array)l.isFloat16BufferAttribute?g=r.HALF_FLOAT:g=r.UNSIGNED_SHORT;else if(h instanceof Int16Array)g=r.SHORT;else if(h instanceof Uint32Array)g=r.UNSIGNED_INT;else if(h instanceof Int32Array)g=r.INT;else if(h instanceof Int8Array)g=r.BYTE;else if(h instanceof Uint8Array)g=r.UNSIGNED_BYTE;else if(h instanceof Uint8ClampedArray)g=r.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+h);return{buffer:m,type:g,bytesPerElement:h.BYTES_PER_ELEMENT,version:l.version,size:p}}function n(l,u,h){const f=u.array,p=u.updateRanges;if(r.bindBuffer(h,l),p.length===0)r.bufferSubData(h,0,f);else{p.sort((g,x)=>g.start-x.start);let m=0;for(let g=1;g<p.length;g++){const x=p[m],E=p[g];E.start<=x.start+x.count+1?x.count=Math.max(x.count,E.start+E.count-x.start):(++m,p[m]=E)}p.length=m+1;for(let g=0,x=p.length;g<x;g++){const E=p[g];r.bufferSubData(h,E.start*f.BYTES_PER_ELEMENT,f,E.start,E.count)}u.clearUpdateRanges()}u.onUploadCallback()}function i(l){return l.isInterleavedBufferAttribute&&(l=l.data),e.get(l)}function s(l){l.isInterleavedBufferAttribute&&(l=l.data);const u=e.get(l);u&&(r.deleteBuffer(u.buffer),e.delete(l))}function a(l,u){if(l.isInterleavedBufferAttribute&&(l=l.data),l.isGLBufferAttribute){const f=e.get(l);(!f||f.version<l.version)&&e.set(l,{buffer:l.buffer,type:l.type,bytesPerElement:l.elementSize,version:l.version});return}const h=e.get(l);if(h===void 0)e.set(l,t(l,u));else if(h.version<l.version){if(h.size!==l.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(h.buffer,l,u),h.version=l.version}}return{get:i,remove:s,update:a}}class uo extends Sn{constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};const s=e/2,a=t/2,l=Math.floor(n),u=Math.floor(i),h=l+1,f=u+1,p=e/l,m=t/u,g=[],x=[],E=[],v=[];for(let _=0;_<f;_++){const R=_*m-a;for(let w=0;w<h;w++){const S=w*p-s;x.push(S,-R,0),E.push(0,0,1),v.push(w/l),v.push(1-_/u)}}for(let _=0;_<u;_++)for(let R=0;R<l;R++){const w=R+h*_,S=R+h*(_+1),k=R+1+h*(_+1),N=R+1+h*_;g.push(w,S,N),g.push(S,k,N)}this.setIndex(g),this.setAttribute("position",new Wt(x,3)),this.setAttribute("normal",new Wt(E,3)),this.setAttribute("uv",new Wt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new uo(e.width,e.height,e.widthSegments,e.heightSegments)}}var GT=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,WT=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,jT=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,XT=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,qT=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,YT=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,KT=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,$T=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,ZT=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec3 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 ).rgb;
	}
#endif`,QT=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,JT=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,ew=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,tw=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,nw=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,iw=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,rw=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,sw=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,ow=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,aw=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,lw=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,cw=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,uw=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,hw=`#if defined( USE_COLOR_ALPHA )
	vColor = vec4( 1.0 );
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec3( 1.0 );
#endif
#ifdef USE_COLOR
	vColor *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.xyz *= instanceColor.xyz;
#endif
#ifdef USE_BATCHING_COLOR
	vec3 batchingColor = getBatchingColor( getIndirectIndex( gl_DrawID ) );
	vColor.xyz *= batchingColor.xyz;
#endif`,dw=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
mat3 transposeMat3( const in mat3 m ) {
	mat3 tmp;
	tmp[ 0 ] = vec3( m[ 0 ].x, m[ 1 ].x, m[ 2 ].x );
	tmp[ 1 ] = vec3( m[ 0 ].y, m[ 1 ].y, m[ 2 ].y );
	tmp[ 2 ] = vec3( m[ 0 ].z, m[ 1 ].z, m[ 2 ].z );
	return tmp;
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,fw=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,pw=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,mw=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,gw=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,_w=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,vw=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,yw="gl_FragColor = linearToOutputTexel( gl_FragColor );",xw=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,bw=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
	#else
		vec4 envColor = vec4( 0.0 );
	#endif
	#ifdef ENVMAP_BLENDING_MULTIPLY
		outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_MIX )
		outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_ADD )
		outgoingLight += envColor.xyz * specularStrength * reflectivity;
	#endif
#endif`,Sw=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,Ew=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,Mw=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,Tw=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,ww=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,Aw=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,Rw=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,Pw=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,Cw=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,Dw=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,Iw=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,Lw=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,Fw=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,Nw=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, roughness * roughness) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,Ow=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,Uw=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,Bw=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,kw=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,zw=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = mix( min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.07, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,Hw=`struct PhysicalMaterial {
	vec3 diffuseColor;
	float roughness;
	vec3 specularColor;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		float v = 0.5 / ( gv + gl );
		return saturate(v);
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColor;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transposeMat3( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float a = roughness < 0.25 ? -339.2 * r2 + 161.4 * roughness - 25.9 : -8.48 * r2 + 14.3 * roughness - 9.95;
	float b = roughness < 0.25 ? 44.0 * r2 - 23.7 * roughness + 3.26 : 1.97 * r2 - 3.27 * roughness + 0.72;
	float DG = exp( a * dotNV + b ) + ( roughness < 0.25 ? 0.0 : 0.1 * ( roughness - 0.25 ) );
	return saturate( DG * RECIPROCAL_PI );
}
vec2 DFGApprox( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	const vec4 c0 = vec4( - 1, - 0.0275, - 0.572, 0.022 );
	const vec4 c1 = vec4( 1, 0.0425, 1.04, - 0.04 );
	vec4 r = roughness * c0 + c1;
	float a004 = min( r.x * r.x, exp2( - 9.28 * dotNV ) ) * r.x + r.y;
	vec2 fab = vec2( - 1.04, 1.04 ) * a004 + r.zw;
	return fab;
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColor * t2.x + ( vec3( 1.0 ) - material.specularColor ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseColor * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
	#endif
	vec3 singleScattering = vec3( 0.0 );
	vec3 multiScattering = vec3( 0.0 );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness, singleScattering, multiScattering );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScattering, multiScattering );
	#endif
	vec3 totalScattering = singleScattering + multiScattering;
	vec3 diffuse = material.diffuseColor * ( 1.0 - max( max( totalScattering.r, totalScattering.g ), totalScattering.b ) );
	reflectedLight.indirectSpecular += radiance * singleScattering;
	reflectedLight.indirectSpecular += multiScattering * cosineWeightedIrradiance;
	reflectedLight.indirectDiffuse += diffuse * cosineWeightedIrradiance;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,Vw=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnel = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,Gw=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )
		iblIrradiance += getIBLIrradiance( geometryNormal );
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,Ww=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,jw=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,Xw=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,qw=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Yw=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,Kw=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,$w=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,Zw=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,Qw=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Jw=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,eA=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,tA=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,nA=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,iA=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,rA=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,sA=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,oA=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,aA=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,lA=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,cA=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,uA=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,hA=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,dA=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,fA=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,pA=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,mA=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,gA=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,_A=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return depth * ( near - far ) - near;
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return ( near * far ) / ( ( far - near ) * depth - far );
}`,vA=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,yA=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,xA=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,bA=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,SA=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,EA=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,MA=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform sampler2D pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	float texture2DCompare( sampler2D depths, vec2 uv, float compare ) {
		return step( compare, unpackRGBAToDepth( texture2D( depths, uv ) ) );
	}
	vec2 texture2DDistribution( sampler2D shadow, vec2 uv ) {
		return unpackRGBATo2Half( texture2D( shadow, uv ) );
	}
	float VSMShadow (sampler2D shadow, vec2 uv, float compare ){
		float occlusion = 1.0;
		vec2 distribution = texture2DDistribution( shadow, uv );
		float hard_shadow = step( compare , distribution.x );
		if (hard_shadow != 1.0 ) {
			float distance = compare - distribution.x ;
			float variance = max( 0.00000, distribution.y * distribution.y );
			float softness_probability = variance / (variance + distance * distance );			softness_probability = clamp( ( softness_probability - 0.3 ) / ( 0.95 - 0.3 ), 0.0, 1.0 );			occlusion = clamp( max( hard_shadow, softness_probability ), 0.0, 1.0 );
		}
		return occlusion;
	}
	float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
		float shadow = 1.0;
		shadowCoord.xyz /= shadowCoord.w;
		shadowCoord.z += shadowBias;
		bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
		bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
		if ( frustumTest ) {
		#if defined( SHADOWMAP_TYPE_PCF )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx0 = - texelSize.x * shadowRadius;
			float dy0 = - texelSize.y * shadowRadius;
			float dx1 = + texelSize.x * shadowRadius;
			float dy1 = + texelSize.y * shadowRadius;
			float dx2 = dx0 / 2.0;
			float dy2 = dy0 / 2.0;
			float dx3 = dx1 / 2.0;
			float dy3 = dy1 / 2.0;
			shadow = (
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy1 ), shadowCoord.z )
			) * ( 1.0 / 17.0 );
		#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx = texelSize.x;
			float dy = texelSize.y;
			vec2 uv = shadowCoord.xy;
			vec2 f = fract( uv * shadowMapSize + 0.5 );
			uv -= f * texelSize;
			shadow = (
				texture2DCompare( shadowMap, uv, shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( dx, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( 0.0, dy ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, 0.0 ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 0.0 ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, dy ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 0.0, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( texture2DCompare( shadowMap, uv + vec2( dx, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( dx, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( mix( texture2DCompare( shadowMap, uv + vec2( -dx, -dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, -dy ), shadowCoord.z ),
						  f.x ),
					 mix( texture2DCompare( shadowMap, uv + vec2( -dx, 2.0 * dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 2.0 * dy ), shadowCoord.z ),
						  f.x ),
					 f.y )
			) * ( 1.0 / 9.0 );
		#elif defined( SHADOWMAP_TYPE_VSM )
			shadow = VSMShadow( shadowMap, shadowCoord.xy, shadowCoord.z );
		#else
			shadow = texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z );
		#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	vec2 cubeToUV( vec3 v, float texelSizeY ) {
		vec3 absV = abs( v );
		float scaleToCube = 1.0 / max( absV.x, max( absV.y, absV.z ) );
		absV *= scaleToCube;
		v *= scaleToCube * ( 1.0 - 2.0 * texelSizeY );
		vec2 planar = v.xy;
		float almostATexel = 1.5 * texelSizeY;
		float almostOne = 1.0 - almostATexel;
		if ( absV.z >= almostOne ) {
			if ( v.z > 0.0 )
				planar.x = 4.0 - v.x;
		} else if ( absV.x >= almostOne ) {
			float signX = sign( v.x );
			planar.x = v.z * signX + 2.0 * signX;
		} else if ( absV.y >= almostOne ) {
			float signY = sign( v.y );
			planar.x = v.x + 2.0 * signY + 2.0;
			planar.y = v.z * signY - 2.0;
		}
		return vec2( 0.125, 0.25 ) * planar + vec2( 0.375, 0.75 );
	}
	float getPointShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		
		float lightToPositionLength = length( lightToPosition );
		if ( lightToPositionLength - shadowCameraFar <= 0.0 && lightToPositionLength - shadowCameraNear >= 0.0 ) {
			float dp = ( lightToPositionLength - shadowCameraNear ) / ( shadowCameraFar - shadowCameraNear );			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			vec2 texelSize = vec2( 1.0 ) / ( shadowMapSize * vec2( 4.0, 2.0 ) );
			#if defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_PCF_SOFT ) || defined( SHADOWMAP_TYPE_VSM )
				vec2 offset = vec2( - 1, 1 ) * shadowRadius * texelSize.y;
				shadow = (
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxx, texelSize.y ), dp )
				) * ( 1.0 / 9.0 );
			#else
				shadow = texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp );
			#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
#endif`,TA=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,wA=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,AA=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,RA=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,PA=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,CA=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,DA=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,IA=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,LA=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,FA=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,NA=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,OA=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseColor, material.specularColor, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,UA=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
		
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
		
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		
		#else
		
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,BA=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,kA=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,zA=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,HA=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const VA=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,GA=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,WA=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,jA=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,XA=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,qA=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,YA=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,KA=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	float fragCoordZ = 0.5 * vHighPrecisionZW[0] / vHighPrecisionZW[1] + 0.5;
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,$A=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,ZA=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = packDepthToRGBA( dist );
}`,QA=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,JA=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,e1=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,t1=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,n1=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,i1=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,r1=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,s1=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,o1=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,a1=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,l1=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,c1=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <packing>
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( packNormalToRGB( normal ), diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,u1=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,h1=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,d1=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,f1=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
		float sheenEnergyComp = 1.0 - 0.157 * max3( material.sheenColor );
		outgoingLight = outgoingLight * sheenEnergyComp + sheenSpecularDirect + sheenSpecularIndirect;
	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,p1=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,m1=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,g1=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,_1=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,v1=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,y1=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <packing>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,x1=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,b1=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,Ct={alphahash_fragment:GT,alphahash_pars_fragment:WT,alphamap_fragment:jT,alphamap_pars_fragment:XT,alphatest_fragment:qT,alphatest_pars_fragment:YT,aomap_fragment:KT,aomap_pars_fragment:$T,batching_pars_vertex:ZT,batching_vertex:QT,begin_vertex:JT,beginnormal_vertex:ew,bsdfs:tw,iridescence_fragment:nw,bumpmap_pars_fragment:iw,clipping_planes_fragment:rw,clipping_planes_pars_fragment:sw,clipping_planes_pars_vertex:ow,clipping_planes_vertex:aw,color_fragment:lw,color_pars_fragment:cw,color_pars_vertex:uw,color_vertex:hw,common:dw,cube_uv_reflection_fragment:fw,defaultnormal_vertex:pw,displacementmap_pars_vertex:mw,displacementmap_vertex:gw,emissivemap_fragment:_w,emissivemap_pars_fragment:vw,colorspace_fragment:yw,colorspace_pars_fragment:xw,envmap_fragment:bw,envmap_common_pars_fragment:Sw,envmap_pars_fragment:Ew,envmap_pars_vertex:Mw,envmap_physical_pars_fragment:Nw,envmap_vertex:Tw,fog_vertex:ww,fog_pars_vertex:Aw,fog_fragment:Rw,fog_pars_fragment:Pw,gradientmap_pars_fragment:Cw,lightmap_pars_fragment:Dw,lights_lambert_fragment:Iw,lights_lambert_pars_fragment:Lw,lights_pars_begin:Fw,lights_toon_fragment:Ow,lights_toon_pars_fragment:Uw,lights_phong_fragment:Bw,lights_phong_pars_fragment:kw,lights_physical_fragment:zw,lights_physical_pars_fragment:Hw,lights_fragment_begin:Vw,lights_fragment_maps:Gw,lights_fragment_end:Ww,logdepthbuf_fragment:jw,logdepthbuf_pars_fragment:Xw,logdepthbuf_pars_vertex:qw,logdepthbuf_vertex:Yw,map_fragment:Kw,map_pars_fragment:$w,map_particle_fragment:Zw,map_particle_pars_fragment:Qw,metalnessmap_fragment:Jw,metalnessmap_pars_fragment:eA,morphinstance_vertex:tA,morphcolor_vertex:nA,morphnormal_vertex:iA,morphtarget_pars_vertex:rA,morphtarget_vertex:sA,normal_fragment_begin:oA,normal_fragment_maps:aA,normal_pars_fragment:lA,normal_pars_vertex:cA,normal_vertex:uA,normalmap_pars_fragment:hA,clearcoat_normal_fragment_begin:dA,clearcoat_normal_fragment_maps:fA,clearcoat_pars_fragment:pA,iridescence_pars_fragment:mA,opaque_fragment:gA,packing:_A,premultiplied_alpha_fragment:vA,project_vertex:yA,dithering_fragment:xA,dithering_pars_fragment:bA,roughnessmap_fragment:SA,roughnessmap_pars_fragment:EA,shadowmap_pars_fragment:MA,shadowmap_pars_vertex:TA,shadowmap_vertex:wA,shadowmask_pars_fragment:AA,skinbase_vertex:RA,skinning_pars_vertex:PA,skinning_vertex:CA,skinnormal_vertex:DA,specularmap_fragment:IA,specularmap_pars_fragment:LA,tonemapping_fragment:FA,tonemapping_pars_fragment:NA,transmission_fragment:OA,transmission_pars_fragment:UA,uv_pars_fragment:BA,uv_pars_vertex:kA,uv_vertex:zA,worldpos_vertex:HA,background_vert:VA,background_frag:GA,backgroundCube_vert:WA,backgroundCube_frag:jA,cube_vert:XA,cube_frag:qA,depth_vert:YA,depth_frag:KA,distanceRGBA_vert:$A,distanceRGBA_frag:ZA,equirect_vert:QA,equirect_frag:JA,linedashed_vert:e1,linedashed_frag:t1,meshbasic_vert:n1,meshbasic_frag:i1,meshlambert_vert:r1,meshlambert_frag:s1,meshmatcap_vert:o1,meshmatcap_frag:a1,meshnormal_vert:l1,meshnormal_frag:c1,meshphong_vert:u1,meshphong_frag:h1,meshphysical_vert:d1,meshphysical_frag:f1,meshtoon_vert:p1,meshtoon_frag:m1,points_vert:g1,points_frag:_1,shadow_vert:v1,shadow_frag:y1,sprite_vert:x1,sprite_frag:b1},Ne={common:{diffuse:{value:new pt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new Rt},alphaMap:{value:null},alphaMapTransform:{value:new Rt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new Rt}},envmap:{envMap:{value:null},envMapRotation:{value:new Rt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new Rt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new Rt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new Rt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new Rt},normalScale:{value:new vt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new Rt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new Rt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new Rt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new Rt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new pt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new pt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new Rt},alphaTest:{value:0},uvTransform:{value:new Rt}},sprite:{diffuse:{value:new pt(16777215)},opacity:{value:1},center:{value:new vt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new Rt},alphaMap:{value:null},alphaMapTransform:{value:new Rt},alphaTest:{value:0}}},Ci={basic:{uniforms:Wn([Ne.common,Ne.specularmap,Ne.envmap,Ne.aomap,Ne.lightmap,Ne.fog]),vertexShader:Ct.meshbasic_vert,fragmentShader:Ct.meshbasic_frag},lambert:{uniforms:Wn([Ne.common,Ne.specularmap,Ne.envmap,Ne.aomap,Ne.lightmap,Ne.emissivemap,Ne.bumpmap,Ne.normalmap,Ne.displacementmap,Ne.fog,Ne.lights,{emissive:{value:new pt(0)}}]),vertexShader:Ct.meshlambert_vert,fragmentShader:Ct.meshlambert_frag},phong:{uniforms:Wn([Ne.common,Ne.specularmap,Ne.envmap,Ne.aomap,Ne.lightmap,Ne.emissivemap,Ne.bumpmap,Ne.normalmap,Ne.displacementmap,Ne.fog,Ne.lights,{emissive:{value:new pt(0)},specular:{value:new pt(1118481)},shininess:{value:30}}]),vertexShader:Ct.meshphong_vert,fragmentShader:Ct.meshphong_frag},standard:{uniforms:Wn([Ne.common,Ne.envmap,Ne.aomap,Ne.lightmap,Ne.emissivemap,Ne.bumpmap,Ne.normalmap,Ne.displacementmap,Ne.roughnessmap,Ne.metalnessmap,Ne.fog,Ne.lights,{emissive:{value:new pt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:Ct.meshphysical_vert,fragmentShader:Ct.meshphysical_frag},toon:{uniforms:Wn([Ne.common,Ne.aomap,Ne.lightmap,Ne.emissivemap,Ne.bumpmap,Ne.normalmap,Ne.displacementmap,Ne.gradientmap,Ne.fog,Ne.lights,{emissive:{value:new pt(0)}}]),vertexShader:Ct.meshtoon_vert,fragmentShader:Ct.meshtoon_frag},matcap:{uniforms:Wn([Ne.common,Ne.bumpmap,Ne.normalmap,Ne.displacementmap,Ne.fog,{matcap:{value:null}}]),vertexShader:Ct.meshmatcap_vert,fragmentShader:Ct.meshmatcap_frag},points:{uniforms:Wn([Ne.points,Ne.fog]),vertexShader:Ct.points_vert,fragmentShader:Ct.points_frag},dashed:{uniforms:Wn([Ne.common,Ne.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:Ct.linedashed_vert,fragmentShader:Ct.linedashed_frag},depth:{uniforms:Wn([Ne.common,Ne.displacementmap]),vertexShader:Ct.depth_vert,fragmentShader:Ct.depth_frag},normal:{uniforms:Wn([Ne.common,Ne.bumpmap,Ne.normalmap,Ne.displacementmap,{opacity:{value:1}}]),vertexShader:Ct.meshnormal_vert,fragmentShader:Ct.meshnormal_frag},sprite:{uniforms:Wn([Ne.sprite,Ne.fog]),vertexShader:Ct.sprite_vert,fragmentShader:Ct.sprite_frag},background:{uniforms:{uvTransform:{value:new Rt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:Ct.background_vert,fragmentShader:Ct.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new Rt}},vertexShader:Ct.backgroundCube_vert,fragmentShader:Ct.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:Ct.cube_vert,fragmentShader:Ct.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:Ct.equirect_vert,fragmentShader:Ct.equirect_frag},distanceRGBA:{uniforms:Wn([Ne.common,Ne.displacementmap,{referencePosition:{value:new F},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:Ct.distanceRGBA_vert,fragmentShader:Ct.distanceRGBA_frag},shadow:{uniforms:Wn([Ne.lights,Ne.fog,{color:{value:new pt(0)},opacity:{value:1}}]),vertexShader:Ct.shadow_vert,fragmentShader:Ct.shadow_frag}};Ci.physical={uniforms:Wn([Ci.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new Rt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new Rt},clearcoatNormalScale:{value:new vt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new Rt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new Rt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new Rt},sheen:{value:0},sheenColor:{value:new pt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new Rt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new Rt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new Rt},transmissionSamplerSize:{value:new vt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new Rt},attenuationDistance:{value:0},attenuationColor:{value:new pt(0)},specularColor:{value:new pt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new Rt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new Rt},anisotropyVector:{value:new vt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new Rt}}]),vertexShader:Ct.meshphysical_vert,fragmentShader:Ct.meshphysical_frag};const cl={r:0,b:0,g:0},es=new wi,S1=new St;function E1(r,e,t,n,i,s,a){const l=new pt(0);let u=s===!0?0:1,h,f,p=null,m=0,g=null;function x(R){let w=R.isScene===!0?R.background:null;return w&&w.isTexture&&(w=(R.backgroundBlurriness>0?t:e).get(w)),w}function E(R){let w=!1;const S=x(R);S===null?_(l,u):S&&S.isColor&&(_(S,1),w=!0);const k=r.xr.getEnvironmentBlendMode();k==="additive"?n.buffers.color.setClear(0,0,0,1,a):k==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(r.autoClear||w)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),r.clear(r.autoClearColor,r.autoClearDepth,r.autoClearStencil))}function v(R,w){const S=x(w);S&&(S.isCubeTexture||S.mapping===zl)?(f===void 0&&(f=new Pe(new dn(1,1,1),new Tr({name:"BackgroundCubeMaterial",uniforms:so(Ci.backgroundCube.uniforms),vertexShader:Ci.backgroundCube.vertexShader,fragmentShader:Ci.backgroundCube.fragmentShader,side:Jn,depthTest:!1,depthWrite:!1,fog:!1})),f.geometry.deleteAttribute("normal"),f.geometry.deleteAttribute("uv"),f.onBeforeRender=function(k,N,O){this.matrixWorld.copyPosition(O.matrixWorld)},Object.defineProperty(f.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(f)),es.copy(w.backgroundRotation),es.x*=-1,es.y*=-1,es.z*=-1,S.isCubeTexture&&S.isRenderTargetTexture===!1&&(es.y*=-1,es.z*=-1),f.material.uniforms.envMap.value=S,f.material.uniforms.flipEnvMap.value=S.isCubeTexture&&S.isRenderTargetTexture===!1?-1:1,f.material.uniforms.backgroundBlurriness.value=w.backgroundBlurriness,f.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,f.material.uniforms.backgroundRotation.value.setFromMatrix4(S1.makeRotationFromEuler(es)),f.material.toneMapped=zt.getTransfer(S.colorSpace)!==Qt,(p!==S||m!==S.version||g!==r.toneMapping)&&(f.material.needsUpdate=!0,p=S,m=S.version,g=r.toneMapping),f.layers.enableAll(),R.unshift(f,f.geometry,f.material,0,0,null)):S&&S.isTexture&&(h===void 0&&(h=new Pe(new uo(2,2),new Tr({name:"BackgroundMaterial",uniforms:so(Ci.background.uniforms),vertexShader:Ci.background.vertexShader,fragmentShader:Ci.background.fragmentShader,side:ir,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),Object.defineProperty(h.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(h)),h.material.uniforms.t2D.value=S,h.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,h.material.toneMapped=zt.getTransfer(S.colorSpace)!==Qt,S.matrixAutoUpdate===!0&&S.updateMatrix(),h.material.uniforms.uvTransform.value.copy(S.matrix),(p!==S||m!==S.version||g!==r.toneMapping)&&(h.material.needsUpdate=!0,p=S,m=S.version,g=r.toneMapping),h.layers.enableAll(),R.unshift(h,h.geometry,h.material,0,0,null))}function _(R,w){R.getRGB(cl,Ng(r)),n.buffers.color.setClear(cl.r,cl.g,cl.b,w,a)}return{getClearColor:function(){return l},setClearColor:function(R,w=1){l.set(R),u=w,_(l,u)},getClearAlpha:function(){return u},setClearAlpha:function(R){u=R,_(l,u)},render:E,addToRenderList:v}}function M1(r,e){const t=r.getParameter(r.MAX_VERTEX_ATTRIBS),n={},i=m(null);let s=i,a=!1;function l(A,z,Z,$,ie){let ae=!1;const X=p($,Z,z);s!==X&&(s=X,h(s.object)),ae=g(A,$,Z,ie),ae&&x(A,$,Z,ie),ie!==null&&e.update(ie,r.ELEMENT_ARRAY_BUFFER),(ae||a)&&(a=!1,S(A,z,Z,$),ie!==null&&r.bindBuffer(r.ELEMENT_ARRAY_BUFFER,e.get(ie).buffer))}function u(){return r.createVertexArray()}function h(A){return r.bindVertexArray(A)}function f(A){return r.deleteVertexArray(A)}function p(A,z,Z){const $=Z.wireframe===!0;let ie=n[A.id];ie===void 0&&(ie={},n[A.id]=ie);let ae=ie[z.id];ae===void 0&&(ae={},ie[z.id]=ae);let X=ae[$];return X===void 0&&(X=m(u()),ae[$]=X),X}function m(A){const z=[],Z=[],$=[];for(let ie=0;ie<t;ie++)z[ie]=0,Z[ie]=0,$[ie]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:z,enabledAttributes:Z,attributeDivisors:$,object:A,attributes:{},index:null}}function g(A,z,Z,$){const ie=s.attributes,ae=z.attributes;let X=0;const he=Z.getAttributes();for(const te in he)if(he[te].location>=0){const Ee=ie[te];let ke=ae[te];if(ke===void 0&&(te==="instanceMatrix"&&A.instanceMatrix&&(ke=A.instanceMatrix),te==="instanceColor"&&A.instanceColor&&(ke=A.instanceColor)),Ee===void 0||Ee.attribute!==ke||ke&&Ee.data!==ke.data)return!0;X++}return s.attributesNum!==X||s.index!==$}function x(A,z,Z,$){const ie={},ae=z.attributes;let X=0;const he=Z.getAttributes();for(const te in he)if(he[te].location>=0){let Ee=ae[te];Ee===void 0&&(te==="instanceMatrix"&&A.instanceMatrix&&(Ee=A.instanceMatrix),te==="instanceColor"&&A.instanceColor&&(Ee=A.instanceColor));const ke={};ke.attribute=Ee,Ee&&Ee.data&&(ke.data=Ee.data),ie[te]=ke,X++}s.attributes=ie,s.attributesNum=X,s.index=$}function E(){const A=s.newAttributes;for(let z=0,Z=A.length;z<Z;z++)A[z]=0}function v(A){_(A,0)}function _(A,z){const Z=s.newAttributes,$=s.enabledAttributes,ie=s.attributeDivisors;Z[A]=1,$[A]===0&&(r.enableVertexAttribArray(A),$[A]=1),ie[A]!==z&&(r.vertexAttribDivisor(A,z),ie[A]=z)}function R(){const A=s.newAttributes,z=s.enabledAttributes;for(let Z=0,$=z.length;Z<$;Z++)z[Z]!==A[Z]&&(r.disableVertexAttribArray(Z),z[Z]=0)}function w(A,z,Z,$,ie,ae,X){X===!0?r.vertexAttribIPointer(A,z,Z,ie,ae):r.vertexAttribPointer(A,z,Z,$,ie,ae)}function S(A,z,Z,$){E();const ie=$.attributes,ae=Z.getAttributes(),X=z.defaultAttributeValues;for(const he in ae){const te=ae[he];if(te.location>=0){let ye=ie[he];if(ye===void 0&&(he==="instanceMatrix"&&A.instanceMatrix&&(ye=A.instanceMatrix),he==="instanceColor"&&A.instanceColor&&(ye=A.instanceColor)),ye!==void 0){const Ee=ye.normalized,ke=ye.itemSize,Xe=e.get(ye);if(Xe===void 0)continue;const Tt=Xe.buffer,ce=Xe.type,ge=Xe.bytesPerElement,Be=ce===r.INT||ce===r.UNSIGNED_INT||ye.gpuType===ud;if(ye.isInterleavedBufferAttribute){const Me=ye.data,ot=Me.stride,ut=ye.offset;if(Me.isInstancedInterleavedBuffer){for(let Ke=0;Ke<te.locationSize;Ke++)_(te.location+Ke,Me.meshPerAttribute);A.isInstancedMesh!==!0&&$._maxInstanceCount===void 0&&($._maxInstanceCount=Me.meshPerAttribute*Me.count)}else for(let Ke=0;Ke<te.locationSize;Ke++)v(te.location+Ke);r.bindBuffer(r.ARRAY_BUFFER,Tt);for(let Ke=0;Ke<te.locationSize;Ke++)w(te.location+Ke,ke/te.locationSize,ce,Ee,ot*ge,(ut+ke/te.locationSize*Ke)*ge,Be)}else{if(ye.isInstancedBufferAttribute){for(let Me=0;Me<te.locationSize;Me++)_(te.location+Me,ye.meshPerAttribute);A.isInstancedMesh!==!0&&$._maxInstanceCount===void 0&&($._maxInstanceCount=ye.meshPerAttribute*ye.count)}else for(let Me=0;Me<te.locationSize;Me++)v(te.location+Me);r.bindBuffer(r.ARRAY_BUFFER,Tt);for(let Me=0;Me<te.locationSize;Me++)w(te.location+Me,ke/te.locationSize,ce,Ee,ke*ge,ke/te.locationSize*Me*ge,Be)}}else if(X!==void 0){const Ee=X[he];if(Ee!==void 0)switch(Ee.length){case 2:r.vertexAttrib2fv(te.location,Ee);break;case 3:r.vertexAttrib3fv(te.location,Ee);break;case 4:r.vertexAttrib4fv(te.location,Ee);break;default:r.vertexAttrib1fv(te.location,Ee)}}}}R()}function k(){H();for(const A in n){const z=n[A];for(const Z in z){const $=z[Z];for(const ie in $)f($[ie].object),delete $[ie];delete z[Z]}delete n[A]}}function N(A){if(n[A.id]===void 0)return;const z=n[A.id];for(const Z in z){const $=z[Z];for(const ie in $)f($[ie].object),delete $[ie];delete z[Z]}delete n[A.id]}function O(A){for(const z in n){const Z=n[z];if(Z[A.id]===void 0)continue;const $=Z[A.id];for(const ie in $)f($[ie].object),delete $[ie];delete Z[A.id]}}function H(){D(),a=!0,s!==i&&(s=i,h(s.object))}function D(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:l,reset:H,resetDefaultState:D,dispose:k,releaseStatesOfGeometry:N,releaseStatesOfProgram:O,initAttributes:E,enableAttribute:v,disableUnusedAttributes:R}}function T1(r,e,t){let n;function i(h){n=h}function s(h,f){r.drawArrays(n,h,f),t.update(f,n,1)}function a(h,f,p){p!==0&&(r.drawArraysInstanced(n,h,f,p),t.update(f,n,p))}function l(h,f,p){if(p===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,h,0,f,0,p);let g=0;for(let x=0;x<p;x++)g+=f[x];t.update(g,n,1)}function u(h,f,p,m){if(p===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let x=0;x<h.length;x++)a(h[x],f[x],m[x]);else{g.multiDrawArraysInstancedWEBGL(n,h,0,f,0,m,0,p);let x=0;for(let E=0;E<p;E++)x+=f[E]*m[E];t.update(x,n,1)}}this.setMode=i,this.render=s,this.renderInstances=a,this.renderMultiDraw=l,this.renderMultiDrawInstances=u}function w1(r,e,t,n){let i;function s(){if(i!==void 0)return i;if(e.has("EXT_texture_filter_anisotropic")===!0){const O=e.get("EXT_texture_filter_anisotropic");i=r.getParameter(O.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function a(O){return!(O!==pi&&n.convert(O)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_FORMAT))}function l(O){const H=O===ra&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(O!==rr&&n.convert(O)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_TYPE)&&O!==Ei&&!H)}function u(O){if(O==="highp"){if(r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.HIGH_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.HIGH_FLOAT).precision>0)return"highp";O="mediump"}return O==="mediump"&&r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.MEDIUM_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let h=t.precision!==void 0?t.precision:"highp";const f=u(h);f!==h&&(console.warn("THREE.WebGLRenderer:",h,"not supported, using",f,"instead."),h=f);const p=t.logarithmicDepthBuffer===!0,m=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),g=r.getParameter(r.MAX_TEXTURE_IMAGE_UNITS),x=r.getParameter(r.MAX_VERTEX_TEXTURE_IMAGE_UNITS),E=r.getParameter(r.MAX_TEXTURE_SIZE),v=r.getParameter(r.MAX_CUBE_MAP_TEXTURE_SIZE),_=r.getParameter(r.MAX_VERTEX_ATTRIBS),R=r.getParameter(r.MAX_VERTEX_UNIFORM_VECTORS),w=r.getParameter(r.MAX_VARYING_VECTORS),S=r.getParameter(r.MAX_FRAGMENT_UNIFORM_VECTORS),k=x>0,N=r.getParameter(r.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:u,textureFormatReadable:a,textureTypeReadable:l,precision:h,logarithmicDepthBuffer:p,reverseDepthBuffer:m,maxTextures:g,maxVertexTextures:x,maxTextureSize:E,maxCubemapSize:v,maxAttributes:_,maxVertexUniforms:R,maxVaryings:w,maxFragmentUniforms:S,vertexTextures:k,maxSamples:N}}function A1(r){const e=this;let t=null,n=0,i=!1,s=!1;const a=new yr,l=new Rt,u={value:null,needsUpdate:!1};this.uniform=u,this.numPlanes=0,this.numIntersection=0,this.init=function(p,m){const g=p.length!==0||m||n!==0||i;return i=m,n=p.length,g},this.beginShadows=function(){s=!0,f(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(p,m){t=f(p,m,0)},this.setState=function(p,m,g){const x=p.clippingPlanes,E=p.clipIntersection,v=p.clipShadows,_=r.get(p);if(!i||x===null||x.length===0||s&&!v)s?f(null):h();else{const R=s?0:n,w=R*4;let S=_.clippingState||null;u.value=S,S=f(x,m,w,g);for(let k=0;k!==w;++k)S[k]=t[k];_.clippingState=S,this.numIntersection=E?this.numPlanes:0,this.numPlanes+=R}};function h(){u.value!==t&&(u.value=t,u.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function f(p,m,g,x){const E=p!==null?p.length:0;let v=null;if(E!==0){if(v=u.value,x!==!0||v===null){const _=g+E*4,R=m.matrixWorldInverse;l.getNormalMatrix(R),(v===null||v.length<_)&&(v=new Float32Array(_));for(let w=0,S=g;w!==E;++w,S+=4)a.copy(p[w]).applyMatrix4(R,l),a.normal.toArray(v,S),v[S+3]=a.constant}u.value=v,u.needsUpdate=!0}return e.numPlanes=E,e.numIntersection=0,v}}function R1(r){let e=new WeakMap;function t(a,l){return l===wh?a.mapping=Js:l===Ah&&(a.mapping=eo),a}function n(a){if(a&&a.isTexture){const l=a.mapping;if(l===wh||l===Ah)if(e.has(a)){const u=e.get(a).texture;return t(u,a.mapping)}else{const u=a.image;if(u&&u.height>0){const h=new kT(u.height);return h.fromEquirectangularTexture(r,a),e.set(a,h),a.addEventListener("dispose",i),t(h.texture,a.mapping)}else return null}}return a}function i(a){const l=a.target;l.removeEventListener("dispose",i);const u=e.get(l);u!==void 0&&(e.delete(l),u.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class Sd extends Og{constructor(e=-1,t=1,n=1,i=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2;let s=n-e,a=n+e,l=i+t,u=i-t;if(this.view!==null&&this.view.enabled){const h=(this.right-this.left)/this.view.fullWidth/this.zoom,f=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=h*this.view.offsetX,a=s+h*this.view.width,l-=f*this.view.offsetY,u=l-f*this.view.height}this.projectionMatrix.makeOrthographic(s,a,l,u,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Ws=4,tm=[.125,.215,.35,.446,.526,.582],as=20,ju=new Sd,nm=new pt;let Xu=null,qu=0,Yu=0,Ku=!1;const rs=(1+Math.sqrt(5))/2,ks=1/rs,im=[new F(-rs,ks,0),new F(rs,ks,0),new F(-ks,0,rs),new F(ks,0,rs),new F(0,rs,-ks),new F(0,rs,ks),new F(-1,1,-1),new F(1,1,-1),new F(-1,1,1),new F(1,1,1)];class rm{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){Xu=this._renderer.getRenderTarget(),qu=this._renderer.getActiveCubeFace(),Yu=this._renderer.getActiveMipmapLevel(),Ku=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,i,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=am(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=om(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Xu,qu,Yu),this._renderer.xr.enabled=Ku,e.scissorTest=!1,ul(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Js||e.mapping===eo?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Xu=this._renderer.getRenderTarget(),qu=this._renderer.getActiveCubeFace(),Yu=this._renderer.getActiveMipmapLevel(),Ku=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ci,minFilter:ci,generateMipmaps:!1,type:ra,format:pi,colorSpace:qn,depthBuffer:!1},i=sm(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=sm(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=P1(s)),this._blurMaterial=C1(s,e,t)}return i}_compileMaterial(e){const t=new Pe(this._lodPlanes[0],e);this._renderer.compile(t,ju)}_sceneToCubeUV(e,t,n,i){const l=new jn(90,1,t,n),u=[1,-1,1,1,1,1],h=[1,1,1,-1,-1,-1],f=this._renderer,p=f.autoClear,m=f.toneMapping;f.getClearColor(nm),f.toneMapping=Mr,f.autoClear=!1;const g=new mi({name:"PMREM.Background",side:Jn,depthWrite:!1,depthTest:!1}),x=new Pe(new dn,g);let E=!1;const v=e.background;v?v.isColor&&(g.color.copy(v),e.background=null,E=!0):(g.color.copy(nm),E=!0);for(let _=0;_<6;_++){const R=_%3;R===0?(l.up.set(0,u[_],0),l.lookAt(h[_],0,0)):R===1?(l.up.set(0,0,u[_]),l.lookAt(0,h[_],0)):(l.up.set(0,u[_],0),l.lookAt(0,0,h[_]));const w=this._cubeSize;ul(i,R*w,_>2?w:0,w,w),f.setRenderTarget(i),E&&f.render(x,l),f.render(e,l)}x.geometry.dispose(),x.material.dispose(),f.toneMapping=m,f.autoClear=p,e.background=v}_textureToCubeUV(e,t){const n=this._renderer,i=e.mapping===Js||e.mapping===eo;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=am()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=om());const s=i?this._cubemapMaterial:this._equirectMaterial,a=new Pe(this._lodPlanes[0],s),l=s.uniforms;l.envMap.value=e;const u=this._cubeSize;ul(t,0,0,3*u,2*u),n.setRenderTarget(t),n.render(a,ju)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const i=this._lodPlanes.length;for(let s=1;s<i;s++){const a=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),l=im[(i-s-1)%im.length];this._blur(e,s-1,s,a,l)}t.autoClear=n}_blur(e,t,n,i,s){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,i,"latitudinal",s),this._halfBlur(a,e,n,n,i,"longitudinal",s)}_halfBlur(e,t,n,i,s,a,l){const u=this._renderer,h=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const f=3,p=new Pe(this._lodPlanes[i],h),m=h.uniforms,g=this._sizeLods[n]-1,x=isFinite(s)?Math.PI/(2*g):2*Math.PI/(2*as-1),E=s/x,v=isFinite(s)?1+Math.floor(f*E):as;v>as&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${v} samples when the maximum is set to ${as}`);const _=[];let R=0;for(let O=0;O<as;++O){const H=O/E,D=Math.exp(-H*H/2);_.push(D),O===0?R+=D:O<v&&(R+=2*D)}for(let O=0;O<_.length;O++)_[O]=_[O]/R;m.envMap.value=e.texture,m.samples.value=v,m.weights.value=_,m.latitudinal.value=a==="latitudinal",l&&(m.poleAxis.value=l);const{_lodMax:w}=this;m.dTheta.value=x,m.mipInt.value=w-n;const S=this._sizeLods[i],k=3*S*(i>w-Ws?i-w+Ws:0),N=4*(this._cubeSize-S);ul(t,k,N,3*S,2*S),u.setRenderTarget(t),u.render(p,ju)}}function P1(r){const e=[],t=[],n=[];let i=r;const s=r-Ws+1+tm.length;for(let a=0;a<s;a++){const l=Math.pow(2,i);t.push(l);let u=1/l;a>r-Ws?u=tm[a-r+Ws-1]:a===0&&(u=0),n.push(u);const h=1/(l-2),f=-h,p=1+h,m=[f,f,p,f,p,p,f,f,p,p,f,p],g=6,x=6,E=3,v=2,_=1,R=new Float32Array(E*x*g),w=new Float32Array(v*x*g),S=new Float32Array(_*x*g);for(let N=0;N<g;N++){const O=N%3*2/3-1,H=N>2?0:-1,D=[O,H,0,O+2/3,H,0,O+2/3,H+1,0,O,H,0,O+2/3,H+1,0,O,H+1,0];R.set(D,E*x*N),w.set(m,v*x*N);const A=[N,N,N,N,N,N];S.set(A,_*x*N)}const k=new Sn;k.setAttribute("position",new pn(R,E)),k.setAttribute("uv",new pn(w,v)),k.setAttribute("faceIndex",new pn(S,_)),e.push(k),i>Ws&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function sm(r,e,t){const n=new us(r,e,t);return n.texture.mapping=zl,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function ul(r,e,t,n,i){r.viewport.set(e,t,n,i),r.scissor.set(e,t,n,i)}function C1(r,e,t){const n=new Float32Array(as),i=new F(0,1,0);return new Tr({name:"SphericalGaussianBlur",defines:{n:as,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${r}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:Ed(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:Er,depthTest:!1,depthWrite:!1})}function om(){return new Tr({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Ed(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:Er,depthTest:!1,depthWrite:!1})}function am(){return new Tr({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Ed(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Er,depthTest:!1,depthWrite:!1})}function Ed(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}function D1(r){let e=new WeakMap,t=null;function n(l){if(l&&l.isTexture){const u=l.mapping,h=u===wh||u===Ah,f=u===Js||u===eo;if(h||f){let p=e.get(l);const m=p!==void 0?p.texture.pmremVersion:0;if(l.isRenderTargetTexture&&l.pmremVersion!==m)return t===null&&(t=new rm(r)),p=h?t.fromEquirectangular(l,p):t.fromCubemap(l,p),p.texture.pmremVersion=l.pmremVersion,e.set(l,p),p.texture;if(p!==void 0)return p.texture;{const g=l.image;return h&&g&&g.height>0||f&&g&&i(g)?(t===null&&(t=new rm(r)),p=h?t.fromEquirectangular(l):t.fromCubemap(l),p.texture.pmremVersion=l.pmremVersion,e.set(l,p),l.addEventListener("dispose",s),p.texture):null}}}return l}function i(l){let u=0;const h=6;for(let f=0;f<h;f++)l[f]!==void 0&&u++;return u===h}function s(l){const u=l.target;u.removeEventListener("dispose",s);const h=e.get(u);h!==void 0&&(e.delete(u),h.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function I1(r){const e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=r.getExtension("WEBGL_depth_texture")||r.getExtension("MOZ_WEBGL_depth_texture")||r.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=r.getExtension("EXT_texture_filter_anisotropic")||r.getExtension("MOZ_EXT_texture_filter_anisotropic")||r.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=r.getExtension("WEBGL_compressed_texture_s3tc")||r.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=r.getExtension("WEBGL_compressed_texture_pvrtc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=r.getExtension(n)}return e[n]=i,i}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const i=t(n);return i===null&&Xo("THREE.WebGLRenderer: "+n+" extension not supported."),i}}}function L1(r,e,t,n){const i={},s=new WeakMap;function a(p){const m=p.target;m.index!==null&&e.remove(m.index);for(const x in m.attributes)e.remove(m.attributes[x]);for(const x in m.morphAttributes){const E=m.morphAttributes[x];for(let v=0,_=E.length;v<_;v++)e.remove(E[v])}m.removeEventListener("dispose",a),delete i[m.id];const g=s.get(m);g&&(e.remove(g),s.delete(m)),n.releaseStatesOfGeometry(m),m.isInstancedBufferGeometry===!0&&delete m._maxInstanceCount,t.memory.geometries--}function l(p,m){return i[m.id]===!0||(m.addEventListener("dispose",a),i[m.id]=!0,t.memory.geometries++),m}function u(p){const m=p.attributes;for(const x in m)e.update(m[x],r.ARRAY_BUFFER);const g=p.morphAttributes;for(const x in g){const E=g[x];for(let v=0,_=E.length;v<_;v++)e.update(E[v],r.ARRAY_BUFFER)}}function h(p){const m=[],g=p.index,x=p.attributes.position;let E=0;if(g!==null){const R=g.array;E=g.version;for(let w=0,S=R.length;w<S;w+=3){const k=R[w+0],N=R[w+1],O=R[w+2];m.push(k,N,N,O,O,k)}}else if(x!==void 0){const R=x.array;E=x.version;for(let w=0,S=R.length/3-1;w<S;w+=3){const k=w+0,N=w+1,O=w+2;m.push(k,N,N,O,O,k)}}else return;const v=new(Pg(m)?Fg:Lg)(m,1);v.version=E;const _=s.get(p);_&&e.remove(_),s.set(p,v)}function f(p){const m=s.get(p);if(m){const g=p.index;g!==null&&m.version<g.version&&h(p)}else h(p);return s.get(p)}return{get:l,update:u,getWireframeAttribute:f}}function F1(r,e,t){let n;function i(m){n=m}let s,a;function l(m){s=m.type,a=m.bytesPerElement}function u(m,g){r.drawElements(n,g,s,m*a),t.update(g,n,1)}function h(m,g,x){x!==0&&(r.drawElementsInstanced(n,g,s,m*a,x),t.update(g,n,x))}function f(m,g,x){if(x===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,g,0,s,m,0,x);let v=0;for(let _=0;_<x;_++)v+=g[_];t.update(v,n,1)}function p(m,g,x,E){if(x===0)return;const v=e.get("WEBGL_multi_draw");if(v===null)for(let _=0;_<m.length;_++)h(m[_]/a,g[_],E[_]);else{v.multiDrawElementsInstancedWEBGL(n,g,0,s,m,0,E,0,x);let _=0;for(let R=0;R<x;R++)_+=g[R]*E[R];t.update(_,n,1)}}this.setMode=i,this.setIndex=l,this.render=u,this.renderInstances=h,this.renderMultiDraw=f,this.renderMultiDrawInstances=p}function N1(r){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,l){switch(t.calls++,a){case r.TRIANGLES:t.triangles+=l*(s/3);break;case r.LINES:t.lines+=l*(s/2);break;case r.LINE_STRIP:t.lines+=l*(s-1);break;case r.LINE_LOOP:t.lines+=l*s;break;case r.POINTS:t.points+=l*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function i(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}function O1(r,e,t){const n=new WeakMap,i=new Gt;function s(a,l,u){const h=a.morphTargetInfluences,f=l.morphAttributes.position||l.morphAttributes.normal||l.morphAttributes.color,p=f!==void 0?f.length:0;let m=n.get(l);if(m===void 0||m.count!==p){let A=function(){H.dispose(),n.delete(l),l.removeEventListener("dispose",A)};var g=A;m!==void 0&&m.texture.dispose();const x=l.morphAttributes.position!==void 0,E=l.morphAttributes.normal!==void 0,v=l.morphAttributes.color!==void 0,_=l.morphAttributes.position||[],R=l.morphAttributes.normal||[],w=l.morphAttributes.color||[];let S=0;x===!0&&(S=1),E===!0&&(S=2),v===!0&&(S=3);let k=l.attributes.position.count*S,N=1;k>e.maxTextureSize&&(N=Math.ceil(k/e.maxTextureSize),k=e.maxTextureSize);const O=new Float32Array(k*N*4*p),H=new Dg(O,k,N,p);H.type=Ei,H.needsUpdate=!0;const D=S*4;for(let z=0;z<p;z++){const Z=_[z],$=R[z],ie=w[z],ae=k*N*4*z;for(let X=0;X<Z.count;X++){const he=X*D;x===!0&&(i.fromBufferAttribute(Z,X),O[ae+he+0]=i.x,O[ae+he+1]=i.y,O[ae+he+2]=i.z,O[ae+he+3]=0),E===!0&&(i.fromBufferAttribute($,X),O[ae+he+4]=i.x,O[ae+he+5]=i.y,O[ae+he+6]=i.z,O[ae+he+7]=0),v===!0&&(i.fromBufferAttribute(ie,X),O[ae+he+8]=i.x,O[ae+he+9]=i.y,O[ae+he+10]=i.z,O[ae+he+11]=ie.itemSize===4?i.w:1)}}m={count:p,texture:H,size:new vt(k,N)},n.set(l,m),l.addEventListener("dispose",A)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)u.getUniforms().setValue(r,"morphTexture",a.morphTexture,t);else{let x=0;for(let v=0;v<h.length;v++)x+=h[v];const E=l.morphTargetsRelative?1:1-x;u.getUniforms().setValue(r,"morphTargetBaseInfluence",E),u.getUniforms().setValue(r,"morphTargetInfluences",h)}u.getUniforms().setValue(r,"morphTargetsTexture",m.texture,t),u.getUniforms().setValue(r,"morphTargetsTextureSize",m.size)}return{update:s}}function U1(r,e,t,n){let i=new WeakMap;function s(u){const h=n.render.frame,f=u.geometry,p=e.get(u,f);if(i.get(p)!==h&&(e.update(p),i.set(p,h)),u.isInstancedMesh&&(u.hasEventListener("dispose",l)===!1&&u.addEventListener("dispose",l),i.get(u)!==h&&(t.update(u.instanceMatrix,r.ARRAY_BUFFER),u.instanceColor!==null&&t.update(u.instanceColor,r.ARRAY_BUFFER),i.set(u,h))),u.isSkinnedMesh){const m=u.skeleton;i.get(m)!==h&&(m.update(),i.set(m,h))}return p}function a(){i=new WeakMap}function l(u){const h=u.target;h.removeEventListener("dispose",l),t.remove(h.instanceMatrix),h.instanceColor!==null&&t.remove(h.instanceColor)}return{update:s,dispose:a}}class kg extends Pn{constructor(e,t,n,i,s,a,l,u,h,f=Ys){if(f!==Ys&&f!==io)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&f===Ys&&(n=cs),n===void 0&&f===io&&(n=no),super(null,i,s,a,l,u,f,n,h),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=l!==void 0?l:Xn,this.minFilter=u!==void 0?u:Xn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const zg=new Pn,lm=new kg(1,1),Hg=new Dg,Vg=new ET,Gg=new Ug,cm=[],um=[],hm=new Float32Array(16),dm=new Float32Array(9),fm=new Float32Array(4);function ho(r,e,t){const n=r[0];if(n<=0||n>0)return r;const i=e*t;let s=cm[i];if(s===void 0&&(s=new Float32Array(i),cm[i]=s),e!==0){n.toArray(s,0);for(let a=1,l=0;a!==e;++a)l+=t,r[a].toArray(s,l)}return s}function En(r,e){if(r.length!==e.length)return!1;for(let t=0,n=r.length;t<n;t++)if(r[t]!==e[t])return!1;return!0}function Mn(r,e){for(let t=0,n=e.length;t<n;t++)r[t]=e[t]}function Vl(r,e){let t=um[e];t===void 0&&(t=new Int32Array(e),um[e]=t);for(let n=0;n!==e;++n)t[n]=r.allocateTextureUnit();return t}function B1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1f(this.addr,e),t[0]=e)}function k1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(En(t,e))return;r.uniform2fv(this.addr,e),Mn(t,e)}}function z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(r.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(En(t,e))return;r.uniform3fv(this.addr,e),Mn(t,e)}}function H1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(En(t,e))return;r.uniform4fv(this.addr,e),Mn(t,e)}}function V1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(En(t,e))return;r.uniformMatrix2fv(this.addr,!1,e),Mn(t,e)}else{if(En(t,n))return;fm.set(n),r.uniformMatrix2fv(this.addr,!1,fm),Mn(t,n)}}function G1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(En(t,e))return;r.uniformMatrix3fv(this.addr,!1,e),Mn(t,e)}else{if(En(t,n))return;dm.set(n),r.uniformMatrix3fv(this.addr,!1,dm),Mn(t,n)}}function W1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(En(t,e))return;r.uniformMatrix4fv(this.addr,!1,e),Mn(t,e)}else{if(En(t,n))return;hm.set(n),r.uniformMatrix4fv(this.addr,!1,hm),Mn(t,n)}}function j1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1i(this.addr,e),t[0]=e)}function X1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(En(t,e))return;r.uniform2iv(this.addr,e),Mn(t,e)}}function q1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(En(t,e))return;r.uniform3iv(this.addr,e),Mn(t,e)}}function Y1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(En(t,e))return;r.uniform4iv(this.addr,e),Mn(t,e)}}function K1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1ui(this.addr,e),t[0]=e)}function $1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(En(t,e))return;r.uniform2uiv(this.addr,e),Mn(t,e)}}function Z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(En(t,e))return;r.uniform3uiv(this.addr,e),Mn(t,e)}}function Q1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(En(t,e))return;r.uniform4uiv(this.addr,e),Mn(t,e)}}function J1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i);let s;this.type===r.SAMPLER_2D_SHADOW?(lm.compareFunction=Ag,s=lm):s=zg,t.setTexture2D(e||s,i)}function eR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||Vg,i)}function tR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||Gg,i)}function nR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||Hg,i)}function iR(r){switch(r){case 5126:return B1;case 35664:return k1;case 35665:return z1;case 35666:return H1;case 35674:return V1;case 35675:return G1;case 35676:return W1;case 5124:case 35670:return j1;case 35667:case 35671:return X1;case 35668:case 35672:return q1;case 35669:case 35673:return Y1;case 5125:return K1;case 36294:return $1;case 36295:return Z1;case 36296:return Q1;case 35678:case 36198:case 36298:case 36306:case 35682:return J1;case 35679:case 36299:case 36307:return eR;case 35680:case 36300:case 36308:case 36293:return tR;case 36289:case 36303:case 36311:case 36292:return nR}}function rR(r,e){r.uniform1fv(this.addr,e)}function sR(r,e){const t=ho(e,this.size,2);r.uniform2fv(this.addr,t)}function oR(r,e){const t=ho(e,this.size,3);r.uniform3fv(this.addr,t)}function aR(r,e){const t=ho(e,this.size,4);r.uniform4fv(this.addr,t)}function lR(r,e){const t=ho(e,this.size,4);r.uniformMatrix2fv(this.addr,!1,t)}function cR(r,e){const t=ho(e,this.size,9);r.uniformMatrix3fv(this.addr,!1,t)}function uR(r,e){const t=ho(e,this.size,16);r.uniformMatrix4fv(this.addr,!1,t)}function hR(r,e){r.uniform1iv(this.addr,e)}function dR(r,e){r.uniform2iv(this.addr,e)}function fR(r,e){r.uniform3iv(this.addr,e)}function pR(r,e){r.uniform4iv(this.addr,e)}function mR(r,e){r.uniform1uiv(this.addr,e)}function gR(r,e){r.uniform2uiv(this.addr,e)}function _R(r,e){r.uniform3uiv(this.addr,e)}function vR(r,e){r.uniform4uiv(this.addr,e)}function yR(r,e,t){const n=this.cache,i=e.length,s=Vl(t,i);En(n,s)||(r.uniform1iv(this.addr,s),Mn(n,s));for(let a=0;a!==i;++a)t.setTexture2D(e[a]||zg,s[a])}function xR(r,e,t){const n=this.cache,i=e.length,s=Vl(t,i);En(n,s)||(r.uniform1iv(this.addr,s),Mn(n,s));for(let a=0;a!==i;++a)t.setTexture3D(e[a]||Vg,s[a])}function bR(r,e,t){const n=this.cache,i=e.length,s=Vl(t,i);En(n,s)||(r.uniform1iv(this.addr,s),Mn(n,s));for(let a=0;a!==i;++a)t.setTextureCube(e[a]||Gg,s[a])}function SR(r,e,t){const n=this.cache,i=e.length,s=Vl(t,i);En(n,s)||(r.uniform1iv(this.addr,s),Mn(n,s));for(let a=0;a!==i;++a)t.setTexture2DArray(e[a]||Hg,s[a])}function ER(r){switch(r){case 5126:return rR;case 35664:return sR;case 35665:return oR;case 35666:return aR;case 35674:return lR;case 35675:return cR;case 35676:return uR;case 5124:case 35670:return hR;case 35667:case 35671:return dR;case 35668:case 35672:return fR;case 35669:case 35673:return pR;case 5125:return mR;case 36294:return gR;case 36295:return _R;case 36296:return vR;case 35678:case 36198:case 36298:case 36306:case 35682:return yR;case 35679:case 36299:case 36307:return xR;case 35680:case 36300:case 36308:case 36293:return bR;case 36289:case 36303:case 36311:case 36292:return SR}}class MR{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=iR(t.type)}}class TR{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=ER(t.type)}}class wR{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const i=this.seq;for(let s=0,a=i.length;s!==a;++s){const l=i[s];l.setValue(e,t[l.id],n)}}}const $u=/(\w+)(\])?(\[|\.)?/g;function pm(r,e){r.seq.push(e),r.map[e.id]=e}function AR(r,e,t){const n=r.name,i=n.length;for($u.lastIndex=0;;){const s=$u.exec(n),a=$u.lastIndex;let l=s[1];const u=s[2]==="]",h=s[3];if(u&&(l=l|0),h===void 0||h==="["&&a+2===i){pm(t,h===void 0?new MR(l,r,e):new TR(l,r,e));break}else{let p=t.map[l];p===void 0&&(p=new wR(l),pm(t,p)),t=p}}}class Dl{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let i=0;i<n;++i){const s=e.getActiveUniform(t,i),a=e.getUniformLocation(t,s.name);AR(s,a,this)}}setValue(e,t,n,i){const s=this.map[t];s!==void 0&&s.setValue(e,n,i)}setOptional(e,t,n){const i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let s=0,a=t.length;s!==a;++s){const l=t[s],u=n[l.id];u.needsUpdate!==!1&&l.setValue(e,u.value,i)}}static seqWithValue(e,t){const n=[];for(let i=0,s=e.length;i!==s;++i){const a=e[i];a.id in t&&n.push(a)}return n}}function mm(r,e,t){const n=r.createShader(e);return r.shaderSource(n,t),r.compileShader(n),n}const RR=37297;let PR=0;function CR(r,e){const t=r.split(`
`),n=[],i=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let a=i;a<s;a++){const l=a+1;n.push(`${l===e?">":" "} ${l}: ${t[a]}`)}return n.join(`
`)}const gm=new Rt;function DR(r){zt._getMatrix(gm,zt.workingColorSpace,r);const e=`mat3( ${gm.elements.map(t=>t.toFixed(4))} )`;switch(zt.getTransfer(r)){case Hl:return[e,"LinearTransferOETF"];case Qt:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",r),[e,"LinearTransferOETF"]}}function _m(r,e,t){const n=r.getShaderParameter(e,r.COMPILE_STATUS),i=r.getShaderInfoLog(e).trim();if(n&&i==="")return"";const s=/ERROR: 0:(\d+)/.exec(i);if(s){const a=parseInt(s[1]);return t.toUpperCase()+`

`+i+`

`+CR(r.getShaderSource(e),a)}else return i}function IR(r,e){const t=DR(e);return[`vec4 ${r}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function LR(r,e){let t;switch(e){case IM:t="Linear";break;case LM:t="Reinhard";break;case FM:t="Cineon";break;case fg:t="ACESFilmic";break;case OM:t="AgX";break;case UM:t="Neutral";break;case NM:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+r+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const hl=new F;function FR(){zt.getLuminanceCoefficients(hl);const r=hl.x.toFixed(4),e=hl.y.toFixed(4),t=hl.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${r}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function NR(r){return[r.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",r.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(qo).join(`
`)}function OR(r){const e=[];for(const t in r){const n=r[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function UR(r,e){const t={},n=r.getProgramParameter(e,r.ACTIVE_ATTRIBUTES);for(let i=0;i<n;i++){const s=r.getActiveAttrib(e,i),a=s.name;let l=1;s.type===r.FLOAT_MAT2&&(l=2),s.type===r.FLOAT_MAT3&&(l=3),s.type===r.FLOAT_MAT4&&(l=4),t[a]={type:s.type,location:r.getAttribLocation(e,a),locationSize:l}}return t}function qo(r){return r!==""}function vm(r,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return r.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function ym(r,e){return r.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const BR=/^[ \t]*#include +<([\w\d./]+)>/gm;function nd(r){return r.replace(BR,zR)}const kR=new Map;function zR(r,e){let t=Ct[e];if(t===void 0){const n=kR.get(e);if(n!==void 0)t=Ct[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return nd(t)}const HR=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function xm(r){return r.replace(HR,VR)}function VR(r,e,t,n){let i="";for(let s=parseInt(e);s<parseInt(t);s++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return i}function bm(r){let e=`precision ${r.precision} float;
	precision ${r.precision} int;
	precision ${r.precision} sampler2D;
	precision ${r.precision} samplerCube;
	precision ${r.precision} sampler3D;
	precision ${r.precision} sampler2DArray;
	precision ${r.precision} sampler2DShadow;
	precision ${r.precision} samplerCubeShadow;
	precision ${r.precision} sampler2DArrayShadow;
	precision ${r.precision} isampler2D;
	precision ${r.precision} isampler3D;
	precision ${r.precision} isamplerCube;
	precision ${r.precision} isampler2DArray;
	precision ${r.precision} usampler2D;
	precision ${r.precision} usampler3D;
	precision ${r.precision} usamplerCube;
	precision ${r.precision} usampler2DArray;
	`;return r.precision==="highp"?e+=`
#define HIGH_PRECISION`:r.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:r.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}function GR(r){let e="SHADOWMAP_TYPE_BASIC";return r.shadowMapType===hg?e="SHADOWMAP_TYPE_PCF":r.shadowMapType===hM?e="SHADOWMAP_TYPE_PCF_SOFT":r.shadowMapType===Qi&&(e="SHADOWMAP_TYPE_VSM"),e}function WR(r){let e="ENVMAP_TYPE_CUBE";if(r.envMap)switch(r.envMapMode){case Js:case eo:e="ENVMAP_TYPE_CUBE";break;case zl:e="ENVMAP_TYPE_CUBE_UV";break}return e}function jR(r){let e="ENVMAP_MODE_REFLECTION";if(r.envMap)switch(r.envMapMode){case eo:e="ENVMAP_MODE_REFRACTION";break}return e}function XR(r){let e="ENVMAP_BLENDING_NONE";if(r.envMap)switch(r.combine){case dg:e="ENVMAP_BLENDING_MULTIPLY";break;case CM:e="ENVMAP_BLENDING_MIX";break;case DM:e="ENVMAP_BLENDING_ADD";break}return e}function qR(r){const e=r.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function YR(r,e,t,n){const i=r.getContext(),s=t.defines;let a=t.vertexShader,l=t.fragmentShader;const u=GR(t),h=WR(t),f=jR(t),p=XR(t),m=qR(t),g=NR(t),x=OR(s),E=i.createProgram();let v,_,R=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(v=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(qo).join(`
`),v.length>0&&(v+=`
`),_=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(qo).join(`
`),_.length>0&&(_+=`
`)):(v=[bm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+f:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(qo).join(`
`),_=[bm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.envMap?"#define "+f:"",t.envMap?"#define "+p:"",m?"#define CUBEUV_TEXEL_WIDTH "+m.texelWidth:"",m?"#define CUBEUV_TEXEL_HEIGHT "+m.texelHeight:"",m?"#define CUBEUV_MAX_MIP "+m.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Mr?"#define TONE_MAPPING":"",t.toneMapping!==Mr?Ct.tonemapping_pars_fragment:"",t.toneMapping!==Mr?LR("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",Ct.colorspace_pars_fragment,IR("linearToOutputTexel",t.outputColorSpace),FR(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(qo).join(`
`)),a=nd(a),a=vm(a,t),a=ym(a,t),l=nd(l),l=vm(l,t),l=ym(l,t),a=xm(a),l=xm(l),t.isRawShaderMaterial!==!0&&(R=`#version 300 es
`,v=[g,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+v,_=["#define varying in",t.glslVersion===Lp?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Lp?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);const w=R+v+a,S=R+_+l,k=mm(i,i.VERTEX_SHADER,w),N=mm(i,i.FRAGMENT_SHADER,S);i.attachShader(E,k),i.attachShader(E,N),t.index0AttributeName!==void 0?i.bindAttribLocation(E,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(E,0,"position"),i.linkProgram(E);function O(z){if(r.debug.checkShaderErrors){const Z=i.getProgramInfoLog(E).trim(),$=i.getShaderInfoLog(k).trim(),ie=i.getShaderInfoLog(N).trim();let ae=!0,X=!0;if(i.getProgramParameter(E,i.LINK_STATUS)===!1)if(ae=!1,typeof r.debug.onShaderError=="function")r.debug.onShaderError(i,E,k,N);else{const he=_m(i,k,"vertex"),te=_m(i,N,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(E,i.VALIDATE_STATUS)+`

Material Name: `+z.name+`
Material Type: `+z.type+`

Program Info Log: `+Z+`
`+he+`
`+te)}else Z!==""?console.warn("THREE.WebGLProgram: Program Info Log:",Z):($===""||ie==="")&&(X=!1);X&&(z.diagnostics={runnable:ae,programLog:Z,vertexShader:{log:$,prefix:v},fragmentShader:{log:ie,prefix:_}})}i.deleteShader(k),i.deleteShader(N),H=new Dl(i,E),D=UR(i,E)}let H;this.getUniforms=function(){return H===void 0&&O(this),H};let D;this.getAttributes=function(){return D===void 0&&O(this),D};let A=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return A===!1&&(A=i.getProgramParameter(E,RR)),A},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(E),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=PR++,this.cacheKey=e,this.usedTimes=1,this.program=E,this.vertexShader=k,this.fragmentShader=N,this}let KR=0;class $R{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(i)===!1&&(a.add(i),i.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new ZR(e),t.set(e,n)),n}}class ZR{constructor(e){this.id=KR++,this.code=e,this.usedTimes=0}}function QR(r,e,t,n,i,s,a){const l=new xd,u=new $R,h=new Set,f=[],p=i.logarithmicDepthBuffer,m=i.vertexTextures;let g=i.precision;const x={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function E(D){return h.add(D),D===0?"uv":`uv${D}`}function v(D,A,z,Z,$){const ie=Z.fog,ae=$.geometry,X=D.isMeshStandardMaterial?Z.environment:null,he=(D.isMeshStandardMaterial?t:e).get(D.envMap||X),te=he&&he.mapping===zl?he.image.height:null,ye=x[D.type];D.precision!==null&&(g=i.getMaxPrecision(D.precision),g!==D.precision&&console.warn("THREE.WebGLProgram.getParameters:",D.precision,"not supported, using",g,"instead."));const Ee=ae.morphAttributes.position||ae.morphAttributes.normal||ae.morphAttributes.color,ke=Ee!==void 0?Ee.length:0;let Xe=0;ae.morphAttributes.position!==void 0&&(Xe=1),ae.morphAttributes.normal!==void 0&&(Xe=2),ae.morphAttributes.color!==void 0&&(Xe=3);let Tt,ce,ge,Be;if(ye){const U=Ci[ye];Tt=U.vertexShader,ce=U.fragmentShader}else Tt=D.vertexShader,ce=D.fragmentShader,u.update(D),ge=u.getVertexShaderID(D),Be=u.getFragmentShaderID(D);const Me=r.getRenderTarget(),ot=r.state.buffers.depth.getReversed(),ut=$.isInstancedMesh===!0,Ke=$.isBatchedMesh===!0,de=!!D.map,be=!!D.matcap,Oe=!!he,V=!!D.aoMap,ct=!!D.lightMap,it=!!D.bumpMap,tt=!!D.normalMap,ze=!!D.displacementMap,dt=!!D.emissiveMap,Ve=!!D.metalnessMap,L=!!D.roughnessMap,T=D.anisotropy>0,K=D.clearcoat>0,ue=D.dispersion>0,me=D.iridescence>0,le=D.sheen>0,Le=D.transmission>0,Ae=T&&!!D.anisotropyMap,He=K&&!!D.clearcoatMap,Pt=K&&!!D.clearcoatNormalMap,_e=K&&!!D.clearcoatRoughnessMap,Ce=me&&!!D.iridescenceMap,Ge=me&&!!D.iridescenceThicknessMap,ft=le&&!!D.sheenColorMap,We=le&&!!D.sheenRoughnessMap,At=!!D.specularMap,mt=!!D.specularColorMap,Ot=!!D.specularIntensityMap,W=Le&&!!D.transmissionMap,Re=Le&&!!D.thicknessMap,oe=!!D.gradientMap,pe=!!D.alphaMap,Fe=D.alphaTest>0,De=!!D.alphaHash,bt=!!D.extensions;let Zt=Mr;D.toneMapped&&(Me===null||Me.isXRRenderTarget===!0)&&(Zt=r.toneMapping);const un={shaderID:ye,shaderType:D.type,shaderName:D.name,vertexShader:Tt,fragmentShader:ce,defines:D.defines,customVertexShaderID:ge,customFragmentShaderID:Be,isRawShaderMaterial:D.isRawShaderMaterial===!0,glslVersion:D.glslVersion,precision:g,batching:Ke,batchingColor:Ke&&$._colorsTexture!==null,instancing:ut,instancingColor:ut&&$.instanceColor!==null,instancingMorph:ut&&$.morphTexture!==null,supportsVertexTextures:m,outputColorSpace:Me===null?r.outputColorSpace:Me.isXRRenderTarget===!0?Me.texture.colorSpace:qn,alphaToCoverage:!!D.alphaToCoverage,map:de,matcap:be,envMap:Oe,envMapMode:Oe&&he.mapping,envMapCubeUVHeight:te,aoMap:V,lightMap:ct,bumpMap:it,normalMap:tt,displacementMap:m&&ze,emissiveMap:dt,normalMapObjectSpace:tt&&D.normalMapType===jM,normalMapTangentSpace:tt&&D.normalMapType===wg,metalnessMap:Ve,roughnessMap:L,anisotropy:T,anisotropyMap:Ae,clearcoat:K,clearcoatMap:He,clearcoatNormalMap:Pt,clearcoatRoughnessMap:_e,dispersion:ue,iridescence:me,iridescenceMap:Ce,iridescenceThicknessMap:Ge,sheen:le,sheenColorMap:ft,sheenRoughnessMap:We,specularMap:At,specularColorMap:mt,specularIntensityMap:Ot,transmission:Le,transmissionMap:W,thicknessMap:Re,gradientMap:oe,opaque:D.transparent===!1&&D.blending===qs&&D.alphaToCoverage===!1,alphaMap:pe,alphaTest:Fe,alphaHash:De,combine:D.combine,mapUv:de&&E(D.map.channel),aoMapUv:V&&E(D.aoMap.channel),lightMapUv:ct&&E(D.lightMap.channel),bumpMapUv:it&&E(D.bumpMap.channel),normalMapUv:tt&&E(D.normalMap.channel),displacementMapUv:ze&&E(D.displacementMap.channel),emissiveMapUv:dt&&E(D.emissiveMap.channel),metalnessMapUv:Ve&&E(D.metalnessMap.channel),roughnessMapUv:L&&E(D.roughnessMap.channel),anisotropyMapUv:Ae&&E(D.anisotropyMap.channel),clearcoatMapUv:He&&E(D.clearcoatMap.channel),clearcoatNormalMapUv:Pt&&E(D.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:_e&&E(D.clearcoatRoughnessMap.channel),iridescenceMapUv:Ce&&E(D.iridescenceMap.channel),iridescenceThicknessMapUv:Ge&&E(D.iridescenceThicknessMap.channel),sheenColorMapUv:ft&&E(D.sheenColorMap.channel),sheenRoughnessMapUv:We&&E(D.sheenRoughnessMap.channel),specularMapUv:At&&E(D.specularMap.channel),specularColorMapUv:mt&&E(D.specularColorMap.channel),specularIntensityMapUv:Ot&&E(D.specularIntensityMap.channel),transmissionMapUv:W&&E(D.transmissionMap.channel),thicknessMapUv:Re&&E(D.thicknessMap.channel),alphaMapUv:pe&&E(D.alphaMap.channel),vertexTangents:!!ae.attributes.tangent&&(tt||T),vertexColors:D.vertexColors,vertexAlphas:D.vertexColors===!0&&!!ae.attributes.color&&ae.attributes.color.itemSize===4,pointsUvs:$.isPoints===!0&&!!ae.attributes.uv&&(de||pe),fog:!!ie,useFog:D.fog===!0,fogExp2:!!ie&&ie.isFogExp2,flatShading:D.flatShading===!0,sizeAttenuation:D.sizeAttenuation===!0,logarithmicDepthBuffer:p,reverseDepthBuffer:ot,skinning:$.isSkinnedMesh===!0,morphTargets:ae.morphAttributes.position!==void 0,morphNormals:ae.morphAttributes.normal!==void 0,morphColors:ae.morphAttributes.color!==void 0,morphTargetsCount:ke,morphTextureStride:Xe,numDirLights:A.directional.length,numPointLights:A.point.length,numSpotLights:A.spot.length,numSpotLightMaps:A.spotLightMap.length,numRectAreaLights:A.rectArea.length,numHemiLights:A.hemi.length,numDirLightShadows:A.directionalShadowMap.length,numPointLightShadows:A.pointShadowMap.length,numSpotLightShadows:A.spotShadowMap.length,numSpotLightShadowsWithMaps:A.numSpotLightShadowsWithMaps,numLightProbes:A.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:D.dithering,shadowMapEnabled:r.shadowMap.enabled&&z.length>0,shadowMapType:r.shadowMap.type,toneMapping:Zt,decodeVideoTexture:de&&D.map.isVideoTexture===!0&&zt.getTransfer(D.map.colorSpace)===Qt,decodeVideoTextureEmissive:dt&&D.emissiveMap.isVideoTexture===!0&&zt.getTransfer(D.emissiveMap.colorSpace)===Qt,premultipliedAlpha:D.premultipliedAlpha,doubleSided:D.side===Qn,flipSided:D.side===Jn,useDepthPacking:D.depthPacking>=0,depthPacking:D.depthPacking||0,index0AttributeName:D.index0AttributeName,extensionClipCullDistance:bt&&D.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(bt&&D.extensions.multiDraw===!0||Ke)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:D.customProgramCacheKey()};return un.vertexUv1s=h.has(1),un.vertexUv2s=h.has(2),un.vertexUv3s=h.has(3),h.clear(),un}function _(D){const A=[];if(D.shaderID?A.push(D.shaderID):(A.push(D.customVertexShaderID),A.push(D.customFragmentShaderID)),D.defines!==void 0)for(const z in D.defines)A.push(z),A.push(D.defines[z]);return D.isRawShaderMaterial===!1&&(R(A,D),w(A,D),A.push(r.outputColorSpace)),A.push(D.customProgramCacheKey),A.join()}function R(D,A){D.push(A.precision),D.push(A.outputColorSpace),D.push(A.envMapMode),D.push(A.envMapCubeUVHeight),D.push(A.mapUv),D.push(A.alphaMapUv),D.push(A.lightMapUv),D.push(A.aoMapUv),D.push(A.bumpMapUv),D.push(A.normalMapUv),D.push(A.displacementMapUv),D.push(A.emissiveMapUv),D.push(A.metalnessMapUv),D.push(A.roughnessMapUv),D.push(A.anisotropyMapUv),D.push(A.clearcoatMapUv),D.push(A.clearcoatNormalMapUv),D.push(A.clearcoatRoughnessMapUv),D.push(A.iridescenceMapUv),D.push(A.iridescenceThicknessMapUv),D.push(A.sheenColorMapUv),D.push(A.sheenRoughnessMapUv),D.push(A.specularMapUv),D.push(A.specularColorMapUv),D.push(A.specularIntensityMapUv),D.push(A.transmissionMapUv),D.push(A.thicknessMapUv),D.push(A.combine),D.push(A.fogExp2),D.push(A.sizeAttenuation),D.push(A.morphTargetsCount),D.push(A.morphAttributeCount),D.push(A.numDirLights),D.push(A.numPointLights),D.push(A.numSpotLights),D.push(A.numSpotLightMaps),D.push(A.numHemiLights),D.push(A.numRectAreaLights),D.push(A.numDirLightShadows),D.push(A.numPointLightShadows),D.push(A.numSpotLightShadows),D.push(A.numSpotLightShadowsWithMaps),D.push(A.numLightProbes),D.push(A.shadowMapType),D.push(A.toneMapping),D.push(A.numClippingPlanes),D.push(A.numClipIntersection),D.push(A.depthPacking)}function w(D,A){l.disableAll(),A.supportsVertexTextures&&l.enable(0),A.instancing&&l.enable(1),A.instancingColor&&l.enable(2),A.instancingMorph&&l.enable(3),A.matcap&&l.enable(4),A.envMap&&l.enable(5),A.normalMapObjectSpace&&l.enable(6),A.normalMapTangentSpace&&l.enable(7),A.clearcoat&&l.enable(8),A.iridescence&&l.enable(9),A.alphaTest&&l.enable(10),A.vertexColors&&l.enable(11),A.vertexAlphas&&l.enable(12),A.vertexUv1s&&l.enable(13),A.vertexUv2s&&l.enable(14),A.vertexUv3s&&l.enable(15),A.vertexTangents&&l.enable(16),A.anisotropy&&l.enable(17),A.alphaHash&&l.enable(18),A.batching&&l.enable(19),A.dispersion&&l.enable(20),A.batchingColor&&l.enable(21),D.push(l.mask),l.disableAll(),A.fog&&l.enable(0),A.useFog&&l.enable(1),A.flatShading&&l.enable(2),A.logarithmicDepthBuffer&&l.enable(3),A.reverseDepthBuffer&&l.enable(4),A.skinning&&l.enable(5),A.morphTargets&&l.enable(6),A.morphNormals&&l.enable(7),A.morphColors&&l.enable(8),A.premultipliedAlpha&&l.enable(9),A.shadowMapEnabled&&l.enable(10),A.doubleSided&&l.enable(11),A.flipSided&&l.enable(12),A.useDepthPacking&&l.enable(13),A.dithering&&l.enable(14),A.transmission&&l.enable(15),A.sheen&&l.enable(16),A.opaque&&l.enable(17),A.pointsUvs&&l.enable(18),A.decodeVideoTexture&&l.enable(19),A.decodeVideoTextureEmissive&&l.enable(20),A.alphaToCoverage&&l.enable(21),D.push(l.mask)}function S(D){const A=x[D.type];let z;if(A){const Z=Ci[A];z=NT.clone(Z.uniforms)}else z=D.uniforms;return z}function k(D,A){let z;for(let Z=0,$=f.length;Z<$;Z++){const ie=f[Z];if(ie.cacheKey===A){z=ie,++z.usedTimes;break}}return z===void 0&&(z=new YR(r,A,D,s),f.push(z)),z}function N(D){if(--D.usedTimes===0){const A=f.indexOf(D);f[A]=f[f.length-1],f.pop(),D.destroy()}}function O(D){u.remove(D)}function H(){u.dispose()}return{getParameters:v,getProgramCacheKey:_,getUniforms:S,acquireProgram:k,releaseProgram:N,releaseShaderCache:O,programs:f,dispose:H}}function JR(){let r=new WeakMap;function e(a){return r.has(a)}function t(a){let l=r.get(a);return l===void 0&&(l={},r.set(a,l)),l}function n(a){r.delete(a)}function i(a,l,u){r.get(a)[l]=u}function s(){r=new WeakMap}return{has:e,get:t,remove:n,update:i,dispose:s}}function eP(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.material.id!==e.material.id?r.material.id-e.material.id:r.z!==e.z?r.z-e.z:r.id-e.id}function Sm(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.z!==e.z?e.z-r.z:r.id-e.id}function Em(){const r=[];let e=0;const t=[],n=[],i=[];function s(){e=0,t.length=0,n.length=0,i.length=0}function a(p,m,g,x,E,v){let _=r[e];return _===void 0?(_={id:p.id,object:p,geometry:m,material:g,groupOrder:x,renderOrder:p.renderOrder,z:E,group:v},r[e]=_):(_.id=p.id,_.object=p,_.geometry=m,_.material=g,_.groupOrder=x,_.renderOrder=p.renderOrder,_.z=E,_.group=v),e++,_}function l(p,m,g,x,E,v){const _=a(p,m,g,x,E,v);g.transmission>0?n.push(_):g.transparent===!0?i.push(_):t.push(_)}function u(p,m,g,x,E,v){const _=a(p,m,g,x,E,v);g.transmission>0?n.unshift(_):g.transparent===!0?i.unshift(_):t.unshift(_)}function h(p,m){t.length>1&&t.sort(p||eP),n.length>1&&n.sort(m||Sm),i.length>1&&i.sort(m||Sm)}function f(){for(let p=e,m=r.length;p<m;p++){const g=r[p];if(g.id===null)break;g.id=null,g.object=null,g.geometry=null,g.material=null,g.group=null}}return{opaque:t,transmissive:n,transparent:i,init:s,push:l,unshift:u,finish:f,sort:h}}function tP(){let r=new WeakMap;function e(n,i){const s=r.get(n);let a;return s===void 0?(a=new Em,r.set(n,[a])):i>=s.length?(a=new Em,s.push(a)):a=s[i],a}function t(){r=new WeakMap}return{get:e,dispose:t}}function nP(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new F,color:new pt};break;case"SpotLight":t={position:new F,direction:new F,color:new pt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new F,color:new pt,distance:0,decay:0};break;case"HemisphereLight":t={direction:new F,skyColor:new pt,groundColor:new pt};break;case"RectAreaLight":t={color:new pt,position:new F,halfWidth:new F,halfHeight:new F};break}return r[e.id]=t,t}}}function iP(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new vt};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new vt};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new vt,shadowCameraNear:1,shadowCameraFar:1e3};break}return r[e.id]=t,t}}}let rP=0;function sP(r,e){return(e.castShadow?2:0)-(r.castShadow?2:0)+(e.map?1:0)-(r.map?1:0)}function oP(r){const e=new nP,t=iP(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let h=0;h<9;h++)n.probe.push(new F);const i=new F,s=new St,a=new St;function l(h){let f=0,p=0,m=0;for(let D=0;D<9;D++)n.probe[D].set(0,0,0);let g=0,x=0,E=0,v=0,_=0,R=0,w=0,S=0,k=0,N=0,O=0;h.sort(sP);for(let D=0,A=h.length;D<A;D++){const z=h[D],Z=z.color,$=z.intensity,ie=z.distance,ae=z.shadow&&z.shadow.map?z.shadow.map.texture:null;if(z.isAmbientLight)f+=Z.r*$,p+=Z.g*$,m+=Z.b*$;else if(z.isLightProbe){for(let X=0;X<9;X++)n.probe[X].addScaledVector(z.sh.coefficients[X],$);O++}else if(z.isDirectionalLight){const X=e.get(z);if(X.color.copy(z.color).multiplyScalar(z.intensity),z.castShadow){const he=z.shadow,te=t.get(z);te.shadowIntensity=he.intensity,te.shadowBias=he.bias,te.shadowNormalBias=he.normalBias,te.shadowRadius=he.radius,te.shadowMapSize=he.mapSize,n.directionalShadow[g]=te,n.directionalShadowMap[g]=ae,n.directionalShadowMatrix[g]=z.shadow.matrix,R++}n.directional[g]=X,g++}else if(z.isSpotLight){const X=e.get(z);X.position.setFromMatrixPosition(z.matrixWorld),X.color.copy(Z).multiplyScalar($),X.distance=ie,X.coneCos=Math.cos(z.angle),X.penumbraCos=Math.cos(z.angle*(1-z.penumbra)),X.decay=z.decay,n.spot[E]=X;const he=z.shadow;if(z.map&&(n.spotLightMap[k]=z.map,k++,he.updateMatrices(z),z.castShadow&&N++),n.spotLightMatrix[E]=he.matrix,z.castShadow){const te=t.get(z);te.shadowIntensity=he.intensity,te.shadowBias=he.bias,te.shadowNormalBias=he.normalBias,te.shadowRadius=he.radius,te.shadowMapSize=he.mapSize,n.spotShadow[E]=te,n.spotShadowMap[E]=ae,S++}E++}else if(z.isRectAreaLight){const X=e.get(z);X.color.copy(Z).multiplyScalar($),X.halfWidth.set(z.width*.5,0,0),X.halfHeight.set(0,z.height*.5,0),n.rectArea[v]=X,v++}else if(z.isPointLight){const X=e.get(z);if(X.color.copy(z.color).multiplyScalar(z.intensity),X.distance=z.distance,X.decay=z.decay,z.castShadow){const he=z.shadow,te=t.get(z);te.shadowIntensity=he.intensity,te.shadowBias=he.bias,te.shadowNormalBias=he.normalBias,te.shadowRadius=he.radius,te.shadowMapSize=he.mapSize,te.shadowCameraNear=he.camera.near,te.shadowCameraFar=he.camera.far,n.pointShadow[x]=te,n.pointShadowMap[x]=ae,n.pointShadowMatrix[x]=z.shadow.matrix,w++}n.point[x]=X,x++}else if(z.isHemisphereLight){const X=e.get(z);X.skyColor.copy(z.color).multiplyScalar($),X.groundColor.copy(z.groundColor).multiplyScalar($),n.hemi[_]=X,_++}}v>0&&(r.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Ne.LTC_FLOAT_1,n.rectAreaLTC2=Ne.LTC_FLOAT_2):(n.rectAreaLTC1=Ne.LTC_HALF_1,n.rectAreaLTC2=Ne.LTC_HALF_2)),n.ambient[0]=f,n.ambient[1]=p,n.ambient[2]=m;const H=n.hash;(H.directionalLength!==g||H.pointLength!==x||H.spotLength!==E||H.rectAreaLength!==v||H.hemiLength!==_||H.numDirectionalShadows!==R||H.numPointShadows!==w||H.numSpotShadows!==S||H.numSpotMaps!==k||H.numLightProbes!==O)&&(n.directional.length=g,n.spot.length=E,n.rectArea.length=v,n.point.length=x,n.hemi.length=_,n.directionalShadow.length=R,n.directionalShadowMap.length=R,n.pointShadow.length=w,n.pointShadowMap.length=w,n.spotShadow.length=S,n.spotShadowMap.length=S,n.directionalShadowMatrix.length=R,n.pointShadowMatrix.length=w,n.spotLightMatrix.length=S+k-N,n.spotLightMap.length=k,n.numSpotLightShadowsWithMaps=N,n.numLightProbes=O,H.directionalLength=g,H.pointLength=x,H.spotLength=E,H.rectAreaLength=v,H.hemiLength=_,H.numDirectionalShadows=R,H.numPointShadows=w,H.numSpotShadows=S,H.numSpotMaps=k,H.numLightProbes=O,n.version=rP++)}function u(h,f){let p=0,m=0,g=0,x=0,E=0;const v=f.matrixWorldInverse;for(let _=0,R=h.length;_<R;_++){const w=h[_];if(w.isDirectionalLight){const S=n.directional[p];S.direction.setFromMatrixPosition(w.matrixWorld),i.setFromMatrixPosition(w.target.matrixWorld),S.direction.sub(i),S.direction.transformDirection(v),p++}else if(w.isSpotLight){const S=n.spot[g];S.position.setFromMatrixPosition(w.matrixWorld),S.position.applyMatrix4(v),S.direction.setFromMatrixPosition(w.matrixWorld),i.setFromMatrixPosition(w.target.matrixWorld),S.direction.sub(i),S.direction.transformDirection(v),g++}else if(w.isRectAreaLight){const S=n.rectArea[x];S.position.setFromMatrixPosition(w.matrixWorld),S.position.applyMatrix4(v),a.identity(),s.copy(w.matrixWorld),s.premultiply(v),a.extractRotation(s),S.halfWidth.set(w.width*.5,0,0),S.halfHeight.set(0,w.height*.5,0),S.halfWidth.applyMatrix4(a),S.halfHeight.applyMatrix4(a),x++}else if(w.isPointLight){const S=n.point[m];S.position.setFromMatrixPosition(w.matrixWorld),S.position.applyMatrix4(v),m++}else if(w.isHemisphereLight){const S=n.hemi[E];S.direction.setFromMatrixPosition(w.matrixWorld),S.direction.transformDirection(v),E++}}}return{setup:l,setupView:u,state:n}}function Mm(r){const e=new oP(r),t=[],n=[];function i(f){h.camera=f,t.length=0,n.length=0}function s(f){t.push(f)}function a(f){n.push(f)}function l(){e.setup(t)}function u(f){e.setupView(t,f)}const h={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:i,state:h,setupLights:l,setupLightsView:u,pushLight:s,pushShadow:a}}function aP(r){let e=new WeakMap;function t(i,s=0){const a=e.get(i);let l;return a===void 0?(l=new Mm(r),e.set(i,[l])):s>=a.length?(l=new Mm(r),a.push(l)):l=a[s],l}function n(){e=new WeakMap}return{get:t,dispose:n}}class lP extends Li{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=GM,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class cP extends Li{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const uP=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,hP=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
#include <packing>
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = unpackRGBATo2Half( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ) );
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = unpackRGBAToDepth( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ) );
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( squared_mean - mean * mean );
	gl_FragColor = pack2HalfToRGBA( vec2( mean, std_dev ) );
}`;function dP(r,e,t){let n=new bd;const i=new vt,s=new vt,a=new Gt,l=new lP({depthPacking:WM}),u=new cP,h={},f=t.maxTextureSize,p={[ir]:Jn,[Jn]:ir,[Qn]:Qn},m=new Tr({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new vt},radius:{value:4}},vertexShader:uP,fragmentShader:hP}),g=m.clone();g.defines.HORIZONTAL_PASS=1;const x=new Sn;x.setAttribute("position",new pn(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const E=new Pe(x,m),v=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=hg;let _=this.type;this.render=function(N,O,H){if(v.enabled===!1||v.autoUpdate===!1&&v.needsUpdate===!1||N.length===0)return;const D=r.getRenderTarget(),A=r.getActiveCubeFace(),z=r.getActiveMipmapLevel(),Z=r.state;Z.setBlending(Er),Z.buffers.color.setClear(1,1,1,1),Z.buffers.depth.setTest(!0),Z.setScissorTest(!1);const $=_!==Qi&&this.type===Qi,ie=_===Qi&&this.type!==Qi;for(let ae=0,X=N.length;ae<X;ae++){const he=N[ae],te=he.shadow;if(te===void 0){console.warn("THREE.WebGLShadowMap:",he,"has no shadow.");continue}if(te.autoUpdate===!1&&te.needsUpdate===!1)continue;i.copy(te.mapSize);const ye=te.getFrameExtents();if(i.multiply(ye),s.copy(te.mapSize),(i.x>f||i.y>f)&&(i.x>f&&(s.x=Math.floor(f/ye.x),i.x=s.x*ye.x,te.mapSize.x=s.x),i.y>f&&(s.y=Math.floor(f/ye.y),i.y=s.y*ye.y,te.mapSize.y=s.y)),te.map===null||$===!0||ie===!0){const ke=this.type!==Qi?{minFilter:Xn,magFilter:Xn}:{};te.map!==null&&te.map.dispose(),te.map=new us(i.x,i.y,ke),te.map.texture.name=he.name+".shadowMap",te.camera.updateProjectionMatrix()}r.setRenderTarget(te.map),r.clear();const Ee=te.getViewportCount();for(let ke=0;ke<Ee;ke++){const Xe=te.getViewport(ke);a.set(s.x*Xe.x,s.y*Xe.y,s.x*Xe.z,s.y*Xe.w),Z.viewport(a),te.updateMatrices(he,ke),n=te.getFrustum(),S(O,H,te.camera,he,this.type)}te.isPointLightShadow!==!0&&this.type===Qi&&R(te,H),te.needsUpdate=!1}_=this.type,v.needsUpdate=!1,r.setRenderTarget(D,A,z)};function R(N,O){const H=e.update(E);m.defines.VSM_SAMPLES!==N.blurSamples&&(m.defines.VSM_SAMPLES=N.blurSamples,g.defines.VSM_SAMPLES=N.blurSamples,m.needsUpdate=!0,g.needsUpdate=!0),N.mapPass===null&&(N.mapPass=new us(i.x,i.y)),m.uniforms.shadow_pass.value=N.map.texture,m.uniforms.resolution.value=N.mapSize,m.uniforms.radius.value=N.radius,r.setRenderTarget(N.mapPass),r.clear(),r.renderBufferDirect(O,null,H,m,E,null),g.uniforms.shadow_pass.value=N.mapPass.texture,g.uniforms.resolution.value=N.mapSize,g.uniforms.radius.value=N.radius,r.setRenderTarget(N.map),r.clear(),r.renderBufferDirect(O,null,H,g,E,null)}function w(N,O,H,D){let A=null;const z=H.isPointLight===!0?N.customDistanceMaterial:N.customDepthMaterial;if(z!==void 0)A=z;else if(A=H.isPointLight===!0?u:l,r.localClippingEnabled&&O.clipShadows===!0&&Array.isArray(O.clippingPlanes)&&O.clippingPlanes.length!==0||O.displacementMap&&O.displacementScale!==0||O.alphaMap&&O.alphaTest>0||O.map&&O.alphaTest>0){const Z=A.uuid,$=O.uuid;let ie=h[Z];ie===void 0&&(ie={},h[Z]=ie);let ae=ie[$];ae===void 0&&(ae=A.clone(),ie[$]=ae,O.addEventListener("dispose",k)),A=ae}if(A.visible=O.visible,A.wireframe=O.wireframe,D===Qi?A.side=O.shadowSide!==null?O.shadowSide:O.side:A.side=O.shadowSide!==null?O.shadowSide:p[O.side],A.alphaMap=O.alphaMap,A.alphaTest=O.alphaTest,A.map=O.map,A.clipShadows=O.clipShadows,A.clippingPlanes=O.clippingPlanes,A.clipIntersection=O.clipIntersection,A.displacementMap=O.displacementMap,A.displacementScale=O.displacementScale,A.displacementBias=O.displacementBias,A.wireframeLinewidth=O.wireframeLinewidth,A.linewidth=O.linewidth,H.isPointLight===!0&&A.isMeshDistanceMaterial===!0){const Z=r.properties.get(A);Z.light=H}return A}function S(N,O,H,D,A){if(N.visible===!1)return;if(N.layers.test(O.layers)&&(N.isMesh||N.isLine||N.isPoints)&&(N.castShadow||N.receiveShadow&&A===Qi)&&(!N.frustumCulled||n.intersectsObject(N))){N.modelViewMatrix.multiplyMatrices(H.matrixWorldInverse,N.matrixWorld);const $=e.update(N),ie=N.material;if(Array.isArray(ie)){const ae=$.groups;for(let X=0,he=ae.length;X<he;X++){const te=ae[X],ye=ie[te.materialIndex];if(ye&&ye.visible){const Ee=w(N,ye,D,A);N.onBeforeShadow(r,N,O,H,$,Ee,te),r.renderBufferDirect(H,null,$,Ee,N,te),N.onAfterShadow(r,N,O,H,$,Ee,te)}}}else if(ie.visible){const ae=w(N,ie,D,A);N.onBeforeShadow(r,N,O,H,$,ae,null),r.renderBufferDirect(H,null,$,ae,N,null),N.onAfterShadow(r,N,O,H,$,ae,null)}}const Z=N.children;for(let $=0,ie=Z.length;$<ie;$++)S(Z[$],O,H,D,A)}function k(N){N.target.removeEventListener("dispose",k);for(const H in h){const D=h[H],A=N.target.uuid;A in D&&(D[A].dispose(),delete D[A])}}}const fP={[yh]:xh,[bh]:Mh,[Sh]:Th,[Qs]:Eh,[xh]:yh,[Mh]:bh,[Th]:Sh,[Eh]:Qs};function pP(r,e){function t(){let W=!1;const Re=new Gt;let oe=null;const pe=new Gt(0,0,0,0);return{setMask:function(Fe){oe!==Fe&&!W&&(r.colorMask(Fe,Fe,Fe,Fe),oe=Fe)},setLocked:function(Fe){W=Fe},setClear:function(Fe,De,bt,Zt,un){un===!0&&(Fe*=Zt,De*=Zt,bt*=Zt),Re.set(Fe,De,bt,Zt),pe.equals(Re)===!1&&(r.clearColor(Fe,De,bt,Zt),pe.copy(Re))},reset:function(){W=!1,oe=null,pe.set(-1,0,0,0)}}}function n(){let W=!1,Re=!1,oe=null,pe=null,Fe=null;return{setReversed:function(De){if(Re!==De){const bt=e.get("EXT_clip_control");Re?bt.clipControlEXT(bt.LOWER_LEFT_EXT,bt.ZERO_TO_ONE_EXT):bt.clipControlEXT(bt.LOWER_LEFT_EXT,bt.NEGATIVE_ONE_TO_ONE_EXT);const Zt=Fe;Fe=null,this.setClear(Zt)}Re=De},getReversed:function(){return Re},setTest:function(De){De?Me(r.DEPTH_TEST):ot(r.DEPTH_TEST)},setMask:function(De){oe!==De&&!W&&(r.depthMask(De),oe=De)},setFunc:function(De){if(Re&&(De=fP[De]),pe!==De){switch(De){case yh:r.depthFunc(r.NEVER);break;case xh:r.depthFunc(r.ALWAYS);break;case bh:r.depthFunc(r.LESS);break;case Qs:r.depthFunc(r.LEQUAL);break;case Sh:r.depthFunc(r.EQUAL);break;case Eh:r.depthFunc(r.GEQUAL);break;case Mh:r.depthFunc(r.GREATER);break;case Th:r.depthFunc(r.NOTEQUAL);break;default:r.depthFunc(r.LEQUAL)}pe=De}},setLocked:function(De){W=De},setClear:function(De){Fe!==De&&(Re&&(De=1-De),r.clearDepth(De),Fe=De)},reset:function(){W=!1,oe=null,pe=null,Fe=null,Re=!1}}}function i(){let W=!1,Re=null,oe=null,pe=null,Fe=null,De=null,bt=null,Zt=null,un=null;return{setTest:function(U){W||(U?Me(r.STENCIL_TEST):ot(r.STENCIL_TEST))},setMask:function(U){Re!==U&&!W&&(r.stencilMask(U),Re=U)},setFunc:function(U,ne,fe){(oe!==U||pe!==ne||Fe!==fe)&&(r.stencilFunc(U,ne,fe),oe=U,pe=ne,Fe=fe)},setOp:function(U,ne,fe){(De!==U||bt!==ne||Zt!==fe)&&(r.stencilOp(U,ne,fe),De=U,bt=ne,Zt=fe)},setLocked:function(U){W=U},setClear:function(U){un!==U&&(r.clearStencil(U),un=U)},reset:function(){W=!1,Re=null,oe=null,pe=null,Fe=null,De=null,bt=null,Zt=null,un=null}}}const s=new t,a=new n,l=new i,u=new WeakMap,h=new WeakMap;let f={},p={},m=new WeakMap,g=[],x=null,E=!1,v=null,_=null,R=null,w=null,S=null,k=null,N=null,O=new pt(0,0,0),H=0,D=!1,A=null,z=null,Z=null,$=null,ie=null;const ae=r.getParameter(r.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let X=!1,he=0;const te=r.getParameter(r.VERSION);te.indexOf("WebGL")!==-1?(he=parseFloat(/^WebGL (\d)/.exec(te)[1]),X=he>=1):te.indexOf("OpenGL ES")!==-1&&(he=parseFloat(/^OpenGL ES (\d)/.exec(te)[1]),X=he>=2);let ye=null,Ee={};const ke=r.getParameter(r.SCISSOR_BOX),Xe=r.getParameter(r.VIEWPORT),Tt=new Gt().fromArray(ke),ce=new Gt().fromArray(Xe);function ge(W,Re,oe,pe){const Fe=new Uint8Array(4),De=r.createTexture();r.bindTexture(W,De),r.texParameteri(W,r.TEXTURE_MIN_FILTER,r.NEAREST),r.texParameteri(W,r.TEXTURE_MAG_FILTER,r.NEAREST);for(let bt=0;bt<oe;bt++)W===r.TEXTURE_3D||W===r.TEXTURE_2D_ARRAY?r.texImage3D(Re,0,r.RGBA,1,1,pe,0,r.RGBA,r.UNSIGNED_BYTE,Fe):r.texImage2D(Re+bt,0,r.RGBA,1,1,0,r.RGBA,r.UNSIGNED_BYTE,Fe);return De}const Be={};Be[r.TEXTURE_2D]=ge(r.TEXTURE_2D,r.TEXTURE_2D,1),Be[r.TEXTURE_CUBE_MAP]=ge(r.TEXTURE_CUBE_MAP,r.TEXTURE_CUBE_MAP_POSITIVE_X,6),Be[r.TEXTURE_2D_ARRAY]=ge(r.TEXTURE_2D_ARRAY,r.TEXTURE_2D_ARRAY,1,1),Be[r.TEXTURE_3D]=ge(r.TEXTURE_3D,r.TEXTURE_3D,1,1),s.setClear(0,0,0,1),a.setClear(1),l.setClear(0),Me(r.DEPTH_TEST),a.setFunc(Qs),it(!1),tt(Ap),Me(r.CULL_FACE),V(Er);function Me(W){f[W]!==!0&&(r.enable(W),f[W]=!0)}function ot(W){f[W]!==!1&&(r.disable(W),f[W]=!1)}function ut(W,Re){return p[W]!==Re?(r.bindFramebuffer(W,Re),p[W]=Re,W===r.DRAW_FRAMEBUFFER&&(p[r.FRAMEBUFFER]=Re),W===r.FRAMEBUFFER&&(p[r.DRAW_FRAMEBUFFER]=Re),!0):!1}function Ke(W,Re){let oe=g,pe=!1;if(W){oe=m.get(Re),oe===void 0&&(oe=[],m.set(Re,oe));const Fe=W.textures;if(oe.length!==Fe.length||oe[0]!==r.COLOR_ATTACHMENT0){for(let De=0,bt=Fe.length;De<bt;De++)oe[De]=r.COLOR_ATTACHMENT0+De;oe.length=Fe.length,pe=!0}}else oe[0]!==r.BACK&&(oe[0]=r.BACK,pe=!0);pe&&r.drawBuffers(oe)}function de(W){return x!==W?(r.useProgram(W),x=W,!0):!1}const be={[os]:r.FUNC_ADD,[fM]:r.FUNC_SUBTRACT,[pM]:r.FUNC_REVERSE_SUBTRACT};be[mM]=r.MIN,be[gM]=r.MAX;const Oe={[_M]:r.ZERO,[vM]:r.ONE,[yM]:r.SRC_COLOR,[_h]:r.SRC_ALPHA,[TM]:r.SRC_ALPHA_SATURATE,[EM]:r.DST_COLOR,[bM]:r.DST_ALPHA,[xM]:r.ONE_MINUS_SRC_COLOR,[vh]:r.ONE_MINUS_SRC_ALPHA,[MM]:r.ONE_MINUS_DST_COLOR,[SM]:r.ONE_MINUS_DST_ALPHA,[wM]:r.CONSTANT_COLOR,[AM]:r.ONE_MINUS_CONSTANT_COLOR,[RM]:r.CONSTANT_ALPHA,[PM]:r.ONE_MINUS_CONSTANT_ALPHA};function V(W,Re,oe,pe,Fe,De,bt,Zt,un,U){if(W===Er){E===!0&&(ot(r.BLEND),E=!1);return}if(E===!1&&(Me(r.BLEND),E=!0),W!==dM){if(W!==v||U!==D){if((_!==os||S!==os)&&(r.blendEquation(r.FUNC_ADD),_=os,S=os),U)switch(W){case qs:r.blendFuncSeparate(r.ONE,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Rp:r.blendFunc(r.ONE,r.ONE);break;case Pp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Cp:r.blendFuncSeparate(r.ZERO,r.SRC_COLOR,r.ZERO,r.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",W);break}else switch(W){case qs:r.blendFuncSeparate(r.SRC_ALPHA,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Rp:r.blendFunc(r.SRC_ALPHA,r.ONE);break;case Pp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Cp:r.blendFunc(r.ZERO,r.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",W);break}R=null,w=null,k=null,N=null,O.set(0,0,0),H=0,v=W,D=U}return}Fe=Fe||Re,De=De||oe,bt=bt||pe,(Re!==_||Fe!==S)&&(r.blendEquationSeparate(be[Re],be[Fe]),_=Re,S=Fe),(oe!==R||pe!==w||De!==k||bt!==N)&&(r.blendFuncSeparate(Oe[oe],Oe[pe],Oe[De],Oe[bt]),R=oe,w=pe,k=De,N=bt),(Zt.equals(O)===!1||un!==H)&&(r.blendColor(Zt.r,Zt.g,Zt.b,un),O.copy(Zt),H=un),v=W,D=!1}function ct(W,Re){W.side===Qn?ot(r.CULL_FACE):Me(r.CULL_FACE);let oe=W.side===Jn;Re&&(oe=!oe),it(oe),W.blending===qs&&W.transparent===!1?V(Er):V(W.blending,W.blendEquation,W.blendSrc,W.blendDst,W.blendEquationAlpha,W.blendSrcAlpha,W.blendDstAlpha,W.blendColor,W.blendAlpha,W.premultipliedAlpha),a.setFunc(W.depthFunc),a.setTest(W.depthTest),a.setMask(W.depthWrite),s.setMask(W.colorWrite);const pe=W.stencilWrite;l.setTest(pe),pe&&(l.setMask(W.stencilWriteMask),l.setFunc(W.stencilFunc,W.stencilRef,W.stencilFuncMask),l.setOp(W.stencilFail,W.stencilZFail,W.stencilZPass)),dt(W.polygonOffset,W.polygonOffsetFactor,W.polygonOffsetUnits),W.alphaToCoverage===!0?Me(r.SAMPLE_ALPHA_TO_COVERAGE):ot(r.SAMPLE_ALPHA_TO_COVERAGE)}function it(W){A!==W&&(W?r.frontFace(r.CW):r.frontFace(r.CCW),A=W)}function tt(W){W!==cM?(Me(r.CULL_FACE),W!==z&&(W===Ap?r.cullFace(r.BACK):W===uM?r.cullFace(r.FRONT):r.cullFace(r.FRONT_AND_BACK))):ot(r.CULL_FACE),z=W}function ze(W){W!==Z&&(X&&r.lineWidth(W),Z=W)}function dt(W,Re,oe){W?(Me(r.POLYGON_OFFSET_FILL),($!==Re||ie!==oe)&&(r.polygonOffset(Re,oe),$=Re,ie=oe)):ot(r.POLYGON_OFFSET_FILL)}function Ve(W){W?Me(r.SCISSOR_TEST):ot(r.SCISSOR_TEST)}function L(W){W===void 0&&(W=r.TEXTURE0+ae-1),ye!==W&&(r.activeTexture(W),ye=W)}function T(W,Re,oe){oe===void 0&&(ye===null?oe=r.TEXTURE0+ae-1:oe=ye);let pe=Ee[oe];pe===void 0&&(pe={type:void 0,texture:void 0},Ee[oe]=pe),(pe.type!==W||pe.texture!==Re)&&(ye!==oe&&(r.activeTexture(oe),ye=oe),r.bindTexture(W,Re||Be[W]),pe.type=W,pe.texture=Re)}function K(){const W=Ee[ye];W!==void 0&&W.type!==void 0&&(r.bindTexture(W.type,null),W.type=void 0,W.texture=void 0)}function ue(){try{r.compressedTexImage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function me(){try{r.compressedTexImage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function le(){try{r.texSubImage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Le(){try{r.texSubImage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Ae(){try{r.compressedTexSubImage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function He(){try{r.compressedTexSubImage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Pt(){try{r.texStorage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function _e(){try{r.texStorage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Ce(){try{r.texImage2D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function Ge(){try{r.texImage3D.apply(r,arguments)}catch(W){console.error("THREE.WebGLState:",W)}}function ft(W){Tt.equals(W)===!1&&(r.scissor(W.x,W.y,W.z,W.w),Tt.copy(W))}function We(W){ce.equals(W)===!1&&(r.viewport(W.x,W.y,W.z,W.w),ce.copy(W))}function At(W,Re){let oe=h.get(Re);oe===void 0&&(oe=new WeakMap,h.set(Re,oe));let pe=oe.get(W);pe===void 0&&(pe=r.getUniformBlockIndex(Re,W.name),oe.set(W,pe))}function mt(W,Re){const pe=h.get(Re).get(W);u.get(Re)!==pe&&(r.uniformBlockBinding(Re,pe,W.__bindingPointIndex),u.set(Re,pe))}function Ot(){r.disable(r.BLEND),r.disable(r.CULL_FACE),r.disable(r.DEPTH_TEST),r.disable(r.POLYGON_OFFSET_FILL),r.disable(r.SCISSOR_TEST),r.disable(r.STENCIL_TEST),r.disable(r.SAMPLE_ALPHA_TO_COVERAGE),r.blendEquation(r.FUNC_ADD),r.blendFunc(r.ONE,r.ZERO),r.blendFuncSeparate(r.ONE,r.ZERO,r.ONE,r.ZERO),r.blendColor(0,0,0,0),r.colorMask(!0,!0,!0,!0),r.clearColor(0,0,0,0),r.depthMask(!0),r.depthFunc(r.LESS),a.setReversed(!1),r.clearDepth(1),r.stencilMask(4294967295),r.stencilFunc(r.ALWAYS,0,4294967295),r.stencilOp(r.KEEP,r.KEEP,r.KEEP),r.clearStencil(0),r.cullFace(r.BACK),r.frontFace(r.CCW),r.polygonOffset(0,0),r.activeTexture(r.TEXTURE0),r.bindFramebuffer(r.FRAMEBUFFER,null),r.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),r.bindFramebuffer(r.READ_FRAMEBUFFER,null),r.useProgram(null),r.lineWidth(1),r.scissor(0,0,r.canvas.width,r.canvas.height),r.viewport(0,0,r.canvas.width,r.canvas.height),f={},ye=null,Ee={},p={},m=new WeakMap,g=[],x=null,E=!1,v=null,_=null,R=null,w=null,S=null,k=null,N=null,O=new pt(0,0,0),H=0,D=!1,A=null,z=null,Z=null,$=null,ie=null,Tt.set(0,0,r.canvas.width,r.canvas.height),ce.set(0,0,r.canvas.width,r.canvas.height),s.reset(),a.reset(),l.reset()}return{buffers:{color:s,depth:a,stencil:l},enable:Me,disable:ot,bindFramebuffer:ut,drawBuffers:Ke,useProgram:de,setBlending:V,setMaterial:ct,setFlipSided:it,setCullFace:tt,setLineWidth:ze,setPolygonOffset:dt,setScissorTest:Ve,activeTexture:L,bindTexture:T,unbindTexture:K,compressedTexImage2D:ue,compressedTexImage3D:me,texImage2D:Ce,texImage3D:Ge,updateUBOMapping:At,uniformBlockBinding:mt,texStorage2D:Pt,texStorage3D:_e,texSubImage2D:le,texSubImage3D:Le,compressedTexSubImage2D:Ae,compressedTexSubImage3D:He,scissor:ft,viewport:We,reset:Ot}}function Tm(r,e,t,n){const i=mP(n);switch(t){case yg:return r*e;case bg:return r*e;case Sg:return r*e*2;case fd:return r*e/i.components*i.byteLength;case pd:return r*e/i.components*i.byteLength;case Eg:return r*e*2/i.components*i.byteLength;case md:return r*e*2/i.components*i.byteLength;case xg:return r*e*3/i.components*i.byteLength;case pi:return r*e*4/i.components*i.byteLength;case gd:return r*e*4/i.components*i.byteLength;case wl:case Al:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Rl:case Pl:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Ph:case Dh:return Math.max(r,16)*Math.max(e,8)/4;case Rh:case Ch:return Math.max(r,8)*Math.max(e,8)/2;case Ih:case Lh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Fh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Nh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Oh:return Math.floor((r+4)/5)*Math.floor((e+3)/4)*16;case Uh:return Math.floor((r+4)/5)*Math.floor((e+4)/5)*16;case Bh:return Math.floor((r+5)/6)*Math.floor((e+4)/5)*16;case kh:return Math.floor((r+5)/6)*Math.floor((e+5)/6)*16;case zh:return Math.floor((r+7)/8)*Math.floor((e+4)/5)*16;case Hh:return Math.floor((r+7)/8)*Math.floor((e+5)/6)*16;case Vh:return Math.floor((r+7)/8)*Math.floor((e+7)/8)*16;case Gh:return Math.floor((r+9)/10)*Math.floor((e+4)/5)*16;case Wh:return Math.floor((r+9)/10)*Math.floor((e+5)/6)*16;case jh:return Math.floor((r+9)/10)*Math.floor((e+7)/8)*16;case Xh:return Math.floor((r+9)/10)*Math.floor((e+9)/10)*16;case qh:return Math.floor((r+11)/12)*Math.floor((e+9)/10)*16;case Yh:return Math.floor((r+11)/12)*Math.floor((e+11)/12)*16;case Cl:case Kh:case $h:return Math.ceil(r/4)*Math.ceil(e/4)*16;case Mg:case Zh:return Math.ceil(r/4)*Math.ceil(e/4)*8;case Qh:case Jh:return Math.ceil(r/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function mP(r){switch(r){case rr:case gg:return{byteLength:1,components:1};case ea:case _g:case ra:return{byteLength:2,components:1};case hd:case dd:return{byteLength:2,components:4};case cs:case ud:case Ei:return{byteLength:4,components:1};case vg:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${r}.`)}function gP(r,e,t,n,i,s,a){const l=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,u=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),h=new vt,f=new WeakMap;let p;const m=new WeakMap;let g=!1;try{g=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function x(L,T){return g?new OffscreenCanvas(L,T):ia("canvas")}function E(L,T,K){let ue=1;const me=Ve(L);if((me.width>K||me.height>K)&&(ue=K/Math.max(me.width,me.height)),ue<1)if(typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&L instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&L instanceof ImageBitmap||typeof VideoFrame<"u"&&L instanceof VideoFrame){const le=Math.floor(ue*me.width),Le=Math.floor(ue*me.height);p===void 0&&(p=x(le,Le));const Ae=T?x(le,Le):p;return Ae.width=le,Ae.height=Le,Ae.getContext("2d").drawImage(L,0,0,le,Le),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+me.width+"x"+me.height+") to ("+le+"x"+Le+")."),Ae}else return"data"in L&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+me.width+"x"+me.height+")."),L;return L}function v(L){return L.generateMipmaps}function _(L){r.generateMipmap(L)}function R(L){return L.isWebGLCubeRenderTarget?r.TEXTURE_CUBE_MAP:L.isWebGL3DRenderTarget?r.TEXTURE_3D:L.isWebGLArrayRenderTarget||L.isCompressedArrayTexture?r.TEXTURE_2D_ARRAY:r.TEXTURE_2D}function w(L,T,K,ue,me=!1){if(L!==null){if(r[L]!==void 0)return r[L];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+L+"'")}let le=T;if(T===r.RED&&(K===r.FLOAT&&(le=r.R32F),K===r.HALF_FLOAT&&(le=r.R16F),K===r.UNSIGNED_BYTE&&(le=r.R8)),T===r.RED_INTEGER&&(K===r.UNSIGNED_BYTE&&(le=r.R8UI),K===r.UNSIGNED_SHORT&&(le=r.R16UI),K===r.UNSIGNED_INT&&(le=r.R32UI),K===r.BYTE&&(le=r.R8I),K===r.SHORT&&(le=r.R16I),K===r.INT&&(le=r.R32I)),T===r.RG&&(K===r.FLOAT&&(le=r.RG32F),K===r.HALF_FLOAT&&(le=r.RG16F),K===r.UNSIGNED_BYTE&&(le=r.RG8)),T===r.RG_INTEGER&&(K===r.UNSIGNED_BYTE&&(le=r.RG8UI),K===r.UNSIGNED_SHORT&&(le=r.RG16UI),K===r.UNSIGNED_INT&&(le=r.RG32UI),K===r.BYTE&&(le=r.RG8I),K===r.SHORT&&(le=r.RG16I),K===r.INT&&(le=r.RG32I)),T===r.RGB_INTEGER&&(K===r.UNSIGNED_BYTE&&(le=r.RGB8UI),K===r.UNSIGNED_SHORT&&(le=r.RGB16UI),K===r.UNSIGNED_INT&&(le=r.RGB32UI),K===r.BYTE&&(le=r.RGB8I),K===r.SHORT&&(le=r.RGB16I),K===r.INT&&(le=r.RGB32I)),T===r.RGBA_INTEGER&&(K===r.UNSIGNED_BYTE&&(le=r.RGBA8UI),K===r.UNSIGNED_SHORT&&(le=r.RGBA16UI),K===r.UNSIGNED_INT&&(le=r.RGBA32UI),K===r.BYTE&&(le=r.RGBA8I),K===r.SHORT&&(le=r.RGBA16I),K===r.INT&&(le=r.RGBA32I)),T===r.RGB&&K===r.UNSIGNED_INT_5_9_9_9_REV&&(le=r.RGB9_E5),T===r.RGBA){const Le=me?Hl:zt.getTransfer(ue);K===r.FLOAT&&(le=r.RGBA32F),K===r.HALF_FLOAT&&(le=r.RGBA16F),K===r.UNSIGNED_BYTE&&(le=Le===Qt?r.SRGB8_ALPHA8:r.RGBA8),K===r.UNSIGNED_SHORT_4_4_4_4&&(le=r.RGBA4),K===r.UNSIGNED_SHORT_5_5_5_1&&(le=r.RGB5_A1)}return(le===r.R16F||le===r.R32F||le===r.RG16F||le===r.RG32F||le===r.RGBA16F||le===r.RGBA32F)&&e.get("EXT_color_buffer_float"),le}function S(L,T){let K;return L?T===null||T===cs||T===no?K=r.DEPTH24_STENCIL8:T===Ei?K=r.DEPTH32F_STENCIL8:T===ea&&(K=r.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):T===null||T===cs||T===no?K=r.DEPTH_COMPONENT24:T===Ei?K=r.DEPTH_COMPONENT32F:T===ea&&(K=r.DEPTH_COMPONENT16),K}function k(L,T){return v(L)===!0||L.isFramebufferTexture&&L.minFilter!==Xn&&L.minFilter!==ci?Math.log2(Math.max(T.width,T.height))+1:L.mipmaps!==void 0&&L.mipmaps.length>0?L.mipmaps.length:L.isCompressedTexture&&Array.isArray(L.image)?T.mipmaps.length:1}function N(L){const T=L.target;T.removeEventListener("dispose",N),H(T),T.isVideoTexture&&f.delete(T)}function O(L){const T=L.target;T.removeEventListener("dispose",O),A(T)}function H(L){const T=n.get(L);if(T.__webglInit===void 0)return;const K=L.source,ue=m.get(K);if(ue){const me=ue[T.__cacheKey];me.usedTimes--,me.usedTimes===0&&D(L),Object.keys(ue).length===0&&m.delete(K)}n.remove(L)}function D(L){const T=n.get(L);r.deleteTexture(T.__webglTexture);const K=L.source,ue=m.get(K);delete ue[T.__cacheKey],a.memory.textures--}function A(L){const T=n.get(L);if(L.depthTexture&&(L.depthTexture.dispose(),n.remove(L.depthTexture)),L.isWebGLCubeRenderTarget)for(let ue=0;ue<6;ue++){if(Array.isArray(T.__webglFramebuffer[ue]))for(let me=0;me<T.__webglFramebuffer[ue].length;me++)r.deleteFramebuffer(T.__webglFramebuffer[ue][me]);else r.deleteFramebuffer(T.__webglFramebuffer[ue]);T.__webglDepthbuffer&&r.deleteRenderbuffer(T.__webglDepthbuffer[ue])}else{if(Array.isArray(T.__webglFramebuffer))for(let ue=0;ue<T.__webglFramebuffer.length;ue++)r.deleteFramebuffer(T.__webglFramebuffer[ue]);else r.deleteFramebuffer(T.__webglFramebuffer);if(T.__webglDepthbuffer&&r.deleteRenderbuffer(T.__webglDepthbuffer),T.__webglMultisampledFramebuffer&&r.deleteFramebuffer(T.__webglMultisampledFramebuffer),T.__webglColorRenderbuffer)for(let ue=0;ue<T.__webglColorRenderbuffer.length;ue++)T.__webglColorRenderbuffer[ue]&&r.deleteRenderbuffer(T.__webglColorRenderbuffer[ue]);T.__webglDepthRenderbuffer&&r.deleteRenderbuffer(T.__webglDepthRenderbuffer)}const K=L.textures;for(let ue=0,me=K.length;ue<me;ue++){const le=n.get(K[ue]);le.__webglTexture&&(r.deleteTexture(le.__webglTexture),a.memory.textures--),n.remove(K[ue])}n.remove(L)}let z=0;function Z(){z=0}function $(){const L=z;return L>=i.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+L+" texture units while this GPU supports only "+i.maxTextures),z+=1,L}function ie(L){const T=[];return T.push(L.wrapS),T.push(L.wrapT),T.push(L.wrapR||0),T.push(L.magFilter),T.push(L.minFilter),T.push(L.anisotropy),T.push(L.internalFormat),T.push(L.format),T.push(L.type),T.push(L.generateMipmaps),T.push(L.premultiplyAlpha),T.push(L.flipY),T.push(L.unpackAlignment),T.push(L.colorSpace),T.join()}function ae(L,T){const K=n.get(L);if(L.isVideoTexture&&ze(L),L.isRenderTargetTexture===!1&&L.version>0&&K.__version!==L.version){const ue=L.image;if(ue===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(ue.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{ce(K,L,T);return}}t.bindTexture(r.TEXTURE_2D,K.__webglTexture,r.TEXTURE0+T)}function X(L,T){const K=n.get(L);if(L.version>0&&K.__version!==L.version){ce(K,L,T);return}t.bindTexture(r.TEXTURE_2D_ARRAY,K.__webglTexture,r.TEXTURE0+T)}function he(L,T){const K=n.get(L);if(L.version>0&&K.__version!==L.version){ce(K,L,T);return}t.bindTexture(r.TEXTURE_3D,K.__webglTexture,r.TEXTURE0+T)}function te(L,T){const K=n.get(L);if(L.version>0&&K.__version!==L.version){ge(K,L,T);return}t.bindTexture(r.TEXTURE_CUBE_MAP,K.__webglTexture,r.TEXTURE0+T)}const ye={[to]:r.REPEAT,[br]:r.CLAMP_TO_EDGE,[Fl]:r.MIRRORED_REPEAT},Ee={[Xn]:r.NEAREST,[mg]:r.NEAREST_MIPMAP_NEAREST,[jo]:r.NEAREST_MIPMAP_LINEAR,[ci]:r.LINEAR,[Tl]:r.LINEAR_MIPMAP_NEAREST,[er]:r.LINEAR_MIPMAP_LINEAR},ke={[XM]:r.NEVER,[QM]:r.ALWAYS,[qM]:r.LESS,[Ag]:r.LEQUAL,[YM]:r.EQUAL,[ZM]:r.GEQUAL,[KM]:r.GREATER,[$M]:r.NOTEQUAL};function Xe(L,T){if(T.type===Ei&&e.has("OES_texture_float_linear")===!1&&(T.magFilter===ci||T.magFilter===Tl||T.magFilter===jo||T.magFilter===er||T.minFilter===ci||T.minFilter===Tl||T.minFilter===jo||T.minFilter===er)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),r.texParameteri(L,r.TEXTURE_WRAP_S,ye[T.wrapS]),r.texParameteri(L,r.TEXTURE_WRAP_T,ye[T.wrapT]),(L===r.TEXTURE_3D||L===r.TEXTURE_2D_ARRAY)&&r.texParameteri(L,r.TEXTURE_WRAP_R,ye[T.wrapR]),r.texParameteri(L,r.TEXTURE_MAG_FILTER,Ee[T.magFilter]),r.texParameteri(L,r.TEXTURE_MIN_FILTER,Ee[T.minFilter]),T.compareFunction&&(r.texParameteri(L,r.TEXTURE_COMPARE_MODE,r.COMPARE_REF_TO_TEXTURE),r.texParameteri(L,r.TEXTURE_COMPARE_FUNC,ke[T.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(T.magFilter===Xn||T.minFilter!==jo&&T.minFilter!==er||T.type===Ei&&e.has("OES_texture_float_linear")===!1)return;if(T.anisotropy>1||n.get(T).__currentAnisotropy){const K=e.get("EXT_texture_filter_anisotropic");r.texParameterf(L,K.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(T.anisotropy,i.getMaxAnisotropy())),n.get(T).__currentAnisotropy=T.anisotropy}}}function Tt(L,T){let K=!1;L.__webglInit===void 0&&(L.__webglInit=!0,T.addEventListener("dispose",N));const ue=T.source;let me=m.get(ue);me===void 0&&(me={},m.set(ue,me));const le=ie(T);if(le!==L.__cacheKey){me[le]===void 0&&(me[le]={texture:r.createTexture(),usedTimes:0},a.memory.textures++,K=!0),me[le].usedTimes++;const Le=me[L.__cacheKey];Le!==void 0&&(me[L.__cacheKey].usedTimes--,Le.usedTimes===0&&D(T)),L.__cacheKey=le,L.__webglTexture=me[le].texture}return K}function ce(L,T,K){let ue=r.TEXTURE_2D;(T.isDataArrayTexture||T.isCompressedArrayTexture)&&(ue=r.TEXTURE_2D_ARRAY),T.isData3DTexture&&(ue=r.TEXTURE_3D);const me=Tt(L,T),le=T.source;t.bindTexture(ue,L.__webglTexture,r.TEXTURE0+K);const Le=n.get(le);if(le.version!==Le.__version||me===!0){t.activeTexture(r.TEXTURE0+K);const Ae=zt.getPrimaries(zt.workingColorSpace),He=T.colorSpace===xr?null:zt.getPrimaries(T.colorSpace),Pt=T.colorSpace===xr||Ae===He?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,T.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,T.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,Pt);let _e=E(T.image,!1,i.maxTextureSize);_e=dt(T,_e);const Ce=s.convert(T.format,T.colorSpace),Ge=s.convert(T.type);let ft=w(T.internalFormat,Ce,Ge,T.colorSpace,T.isVideoTexture);Xe(ue,T);let We;const At=T.mipmaps,mt=T.isVideoTexture!==!0,Ot=Le.__version===void 0||me===!0,W=le.dataReady,Re=k(T,_e);if(T.isDepthTexture)ft=S(T.format===io,T.type),Ot&&(mt?t.texStorage2D(r.TEXTURE_2D,1,ft,_e.width,_e.height):t.texImage2D(r.TEXTURE_2D,0,ft,_e.width,_e.height,0,Ce,Ge,null));else if(T.isDataTexture)if(At.length>0){mt&&Ot&&t.texStorage2D(r.TEXTURE_2D,Re,ft,At[0].width,At[0].height);for(let oe=0,pe=At.length;oe<pe;oe++)We=At[oe],mt?W&&t.texSubImage2D(r.TEXTURE_2D,oe,0,0,We.width,We.height,Ce,Ge,We.data):t.texImage2D(r.TEXTURE_2D,oe,ft,We.width,We.height,0,Ce,Ge,We.data);T.generateMipmaps=!1}else mt?(Ot&&t.texStorage2D(r.TEXTURE_2D,Re,ft,_e.width,_e.height),W&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,_e.width,_e.height,Ce,Ge,_e.data)):t.texImage2D(r.TEXTURE_2D,0,ft,_e.width,_e.height,0,Ce,Ge,_e.data);else if(T.isCompressedTexture)if(T.isCompressedArrayTexture){mt&&Ot&&t.texStorage3D(r.TEXTURE_2D_ARRAY,Re,ft,At[0].width,At[0].height,_e.depth);for(let oe=0,pe=At.length;oe<pe;oe++)if(We=At[oe],T.format!==pi)if(Ce!==null)if(mt){if(W)if(T.layerUpdates.size>0){const Fe=Tm(We.width,We.height,T.format,T.type);for(const De of T.layerUpdates){const bt=We.data.subarray(De*Fe/We.data.BYTES_PER_ELEMENT,(De+1)*Fe/We.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,oe,0,0,De,We.width,We.height,1,Ce,bt)}T.clearLayerUpdates()}else t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,oe,0,0,0,We.width,We.height,_e.depth,Ce,We.data)}else t.compressedTexImage3D(r.TEXTURE_2D_ARRAY,oe,ft,We.width,We.height,_e.depth,0,We.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else mt?W&&t.texSubImage3D(r.TEXTURE_2D_ARRAY,oe,0,0,0,We.width,We.height,_e.depth,Ce,Ge,We.data):t.texImage3D(r.TEXTURE_2D_ARRAY,oe,ft,We.width,We.height,_e.depth,0,Ce,Ge,We.data)}else{mt&&Ot&&t.texStorage2D(r.TEXTURE_2D,Re,ft,At[0].width,At[0].height);for(let oe=0,pe=At.length;oe<pe;oe++)We=At[oe],T.format!==pi?Ce!==null?mt?W&&t.compressedTexSubImage2D(r.TEXTURE_2D,oe,0,0,We.width,We.height,Ce,We.data):t.compressedTexImage2D(r.TEXTURE_2D,oe,ft,We.width,We.height,0,We.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):mt?W&&t.texSubImage2D(r.TEXTURE_2D,oe,0,0,We.width,We.height,Ce,Ge,We.data):t.texImage2D(r.TEXTURE_2D,oe,ft,We.width,We.height,0,Ce,Ge,We.data)}else if(T.isDataArrayTexture)if(mt){if(Ot&&t.texStorage3D(r.TEXTURE_2D_ARRAY,Re,ft,_e.width,_e.height,_e.depth),W)if(T.layerUpdates.size>0){const oe=Tm(_e.width,_e.height,T.format,T.type);for(const pe of T.layerUpdates){const Fe=_e.data.subarray(pe*oe/_e.data.BYTES_PER_ELEMENT,(pe+1)*oe/_e.data.BYTES_PER_ELEMENT);t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,pe,_e.width,_e.height,1,Ce,Ge,Fe)}T.clearLayerUpdates()}else t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,0,_e.width,_e.height,_e.depth,Ce,Ge,_e.data)}else t.texImage3D(r.TEXTURE_2D_ARRAY,0,ft,_e.width,_e.height,_e.depth,0,Ce,Ge,_e.data);else if(T.isData3DTexture)mt?(Ot&&t.texStorage3D(r.TEXTURE_3D,Re,ft,_e.width,_e.height,_e.depth),W&&t.texSubImage3D(r.TEXTURE_3D,0,0,0,0,_e.width,_e.height,_e.depth,Ce,Ge,_e.data)):t.texImage3D(r.TEXTURE_3D,0,ft,_e.width,_e.height,_e.depth,0,Ce,Ge,_e.data);else if(T.isFramebufferTexture){if(Ot)if(mt)t.texStorage2D(r.TEXTURE_2D,Re,ft,_e.width,_e.height);else{let oe=_e.width,pe=_e.height;for(let Fe=0;Fe<Re;Fe++)t.texImage2D(r.TEXTURE_2D,Fe,ft,oe,pe,0,Ce,Ge,null),oe>>=1,pe>>=1}}else if(At.length>0){if(mt&&Ot){const oe=Ve(At[0]);t.texStorage2D(r.TEXTURE_2D,Re,ft,oe.width,oe.height)}for(let oe=0,pe=At.length;oe<pe;oe++)We=At[oe],mt?W&&t.texSubImage2D(r.TEXTURE_2D,oe,0,0,Ce,Ge,We):t.texImage2D(r.TEXTURE_2D,oe,ft,Ce,Ge,We);T.generateMipmaps=!1}else if(mt){if(Ot){const oe=Ve(_e);t.texStorage2D(r.TEXTURE_2D,Re,ft,oe.width,oe.height)}W&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,Ce,Ge,_e)}else t.texImage2D(r.TEXTURE_2D,0,ft,Ce,Ge,_e);v(T)&&_(ue),Le.__version=le.version,T.onUpdate&&T.onUpdate(T)}L.__version=T.version}function ge(L,T,K){if(T.image.length!==6)return;const ue=Tt(L,T),me=T.source;t.bindTexture(r.TEXTURE_CUBE_MAP,L.__webglTexture,r.TEXTURE0+K);const le=n.get(me);if(me.version!==le.__version||ue===!0){t.activeTexture(r.TEXTURE0+K);const Le=zt.getPrimaries(zt.workingColorSpace),Ae=T.colorSpace===xr?null:zt.getPrimaries(T.colorSpace),He=T.colorSpace===xr||Le===Ae?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,T.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,T.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,He);const Pt=T.isCompressedTexture||T.image[0].isCompressedTexture,_e=T.image[0]&&T.image[0].isDataTexture,Ce=[];for(let pe=0;pe<6;pe++)!Pt&&!_e?Ce[pe]=E(T.image[pe],!0,i.maxCubemapSize):Ce[pe]=_e?T.image[pe].image:T.image[pe],Ce[pe]=dt(T,Ce[pe]);const Ge=Ce[0],ft=s.convert(T.format,T.colorSpace),We=s.convert(T.type),At=w(T.internalFormat,ft,We,T.colorSpace),mt=T.isVideoTexture!==!0,Ot=le.__version===void 0||ue===!0,W=me.dataReady;let Re=k(T,Ge);Xe(r.TEXTURE_CUBE_MAP,T);let oe;if(Pt){mt&&Ot&&t.texStorage2D(r.TEXTURE_CUBE_MAP,Re,At,Ge.width,Ge.height);for(let pe=0;pe<6;pe++){oe=Ce[pe].mipmaps;for(let Fe=0;Fe<oe.length;Fe++){const De=oe[Fe];T.format!==pi?ft!==null?mt?W&&t.compressedTexSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,Fe,0,0,De.width,De.height,ft,De.data):t.compressedTexImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,Fe,At,De.width,De.height,0,De.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):mt?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,Fe,0,0,De.width,De.height,ft,We,De.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,Fe,At,De.width,De.height,0,ft,We,De.data)}}}else{if(oe=T.mipmaps,mt&&Ot){oe.length>0&&Re++;const pe=Ve(Ce[0]);t.texStorage2D(r.TEXTURE_CUBE_MAP,Re,At,pe.width,pe.height)}for(let pe=0;pe<6;pe++)if(_e){mt?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,0,0,0,Ce[pe].width,Ce[pe].height,ft,We,Ce[pe].data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,0,At,Ce[pe].width,Ce[pe].height,0,ft,We,Ce[pe].data);for(let Fe=0;Fe<oe.length;Fe++){const bt=oe[Fe].image[pe].image;mt?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,Fe+1,0,0,bt.width,bt.height,ft,We,bt.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,Fe+1,At,bt.width,bt.height,0,ft,We,bt.data)}}else{mt?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,0,0,0,ft,We,Ce[pe]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,0,At,ft,We,Ce[pe]);for(let Fe=0;Fe<oe.length;Fe++){const De=oe[Fe];mt?W&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,Fe+1,0,0,ft,We,De.image[pe]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,Fe+1,At,ft,We,De.image[pe])}}}v(T)&&_(r.TEXTURE_CUBE_MAP),le.__version=me.version,T.onUpdate&&T.onUpdate(T)}L.__version=T.version}function Be(L,T,K,ue,me,le){const Le=s.convert(K.format,K.colorSpace),Ae=s.convert(K.type),He=w(K.internalFormat,Le,Ae,K.colorSpace),Pt=n.get(T),_e=n.get(K);if(_e.__renderTarget=T,!Pt.__hasExternalTextures){const Ce=Math.max(1,T.width>>le),Ge=Math.max(1,T.height>>le);me===r.TEXTURE_3D||me===r.TEXTURE_2D_ARRAY?t.texImage3D(me,le,He,Ce,Ge,T.depth,0,Le,Ae,null):t.texImage2D(me,le,He,Ce,Ge,0,Le,Ae,null)}t.bindFramebuffer(r.FRAMEBUFFER,L),tt(T)?l.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,ue,me,_e.__webglTexture,0,it(T)):(me===r.TEXTURE_2D||me>=r.TEXTURE_CUBE_MAP_POSITIVE_X&&me<=r.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&r.framebufferTexture2D(r.FRAMEBUFFER,ue,me,_e.__webglTexture,le),t.bindFramebuffer(r.FRAMEBUFFER,null)}function Me(L,T,K){if(r.bindRenderbuffer(r.RENDERBUFFER,L),T.depthBuffer){const ue=T.depthTexture,me=ue&&ue.isDepthTexture?ue.type:null,le=S(T.stencilBuffer,me),Le=T.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Ae=it(T);tt(T)?l.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,Ae,le,T.width,T.height):K?r.renderbufferStorageMultisample(r.RENDERBUFFER,Ae,le,T.width,T.height):r.renderbufferStorage(r.RENDERBUFFER,le,T.width,T.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,Le,r.RENDERBUFFER,L)}else{const ue=T.textures;for(let me=0;me<ue.length;me++){const le=ue[me],Le=s.convert(le.format,le.colorSpace),Ae=s.convert(le.type),He=w(le.internalFormat,Le,Ae,le.colorSpace),Pt=it(T);K&&tt(T)===!1?r.renderbufferStorageMultisample(r.RENDERBUFFER,Pt,He,T.width,T.height):tt(T)?l.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,Pt,He,T.width,T.height):r.renderbufferStorage(r.RENDERBUFFER,He,T.width,T.height)}}r.bindRenderbuffer(r.RENDERBUFFER,null)}function ot(L,T){if(T&&T.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(r.FRAMEBUFFER,L),!(T.depthTexture&&T.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const ue=n.get(T.depthTexture);ue.__renderTarget=T,(!ue.__webglTexture||T.depthTexture.image.width!==T.width||T.depthTexture.image.height!==T.height)&&(T.depthTexture.image.width=T.width,T.depthTexture.image.height=T.height,T.depthTexture.needsUpdate=!0),ae(T.depthTexture,0);const me=ue.__webglTexture,le=it(T);if(T.depthTexture.format===Ys)tt(T)?l.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,me,0,le):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,me,0);else if(T.depthTexture.format===io)tt(T)?l.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,me,0,le):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,me,0);else throw new Error("Unknown depthTexture format")}function ut(L){const T=n.get(L),K=L.isWebGLCubeRenderTarget===!0;if(T.__boundDepthTexture!==L.depthTexture){const ue=L.depthTexture;if(T.__depthDisposeCallback&&T.__depthDisposeCallback(),ue){const me=()=>{delete T.__boundDepthTexture,delete T.__depthDisposeCallback,ue.removeEventListener("dispose",me)};ue.addEventListener("dispose",me),T.__depthDisposeCallback=me}T.__boundDepthTexture=ue}if(L.depthTexture&&!T.__autoAllocateDepthBuffer){if(K)throw new Error("target.depthTexture not supported in Cube render targets");ot(T.__webglFramebuffer,L)}else if(K){T.__webglDepthbuffer=[];for(let ue=0;ue<6;ue++)if(t.bindFramebuffer(r.FRAMEBUFFER,T.__webglFramebuffer[ue]),T.__webglDepthbuffer[ue]===void 0)T.__webglDepthbuffer[ue]=r.createRenderbuffer(),Me(T.__webglDepthbuffer[ue],L,!1);else{const me=L.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,le=T.__webglDepthbuffer[ue];r.bindRenderbuffer(r.RENDERBUFFER,le),r.framebufferRenderbuffer(r.FRAMEBUFFER,me,r.RENDERBUFFER,le)}}else if(t.bindFramebuffer(r.FRAMEBUFFER,T.__webglFramebuffer),T.__webglDepthbuffer===void 0)T.__webglDepthbuffer=r.createRenderbuffer(),Me(T.__webglDepthbuffer,L,!1);else{const ue=L.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,me=T.__webglDepthbuffer;r.bindRenderbuffer(r.RENDERBUFFER,me),r.framebufferRenderbuffer(r.FRAMEBUFFER,ue,r.RENDERBUFFER,me)}t.bindFramebuffer(r.FRAMEBUFFER,null)}function Ke(L,T,K){const ue=n.get(L);T!==void 0&&Be(ue.__webglFramebuffer,L,L.texture,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,0),K!==void 0&&ut(L)}function de(L){const T=L.texture,K=n.get(L),ue=n.get(T);L.addEventListener("dispose",O);const me=L.textures,le=L.isWebGLCubeRenderTarget===!0,Le=me.length>1;if(Le||(ue.__webglTexture===void 0&&(ue.__webglTexture=r.createTexture()),ue.__version=T.version,a.memory.textures++),le){K.__webglFramebuffer=[];for(let Ae=0;Ae<6;Ae++)if(T.mipmaps&&T.mipmaps.length>0){K.__webglFramebuffer[Ae]=[];for(let He=0;He<T.mipmaps.length;He++)K.__webglFramebuffer[Ae][He]=r.createFramebuffer()}else K.__webglFramebuffer[Ae]=r.createFramebuffer()}else{if(T.mipmaps&&T.mipmaps.length>0){K.__webglFramebuffer=[];for(let Ae=0;Ae<T.mipmaps.length;Ae++)K.__webglFramebuffer[Ae]=r.createFramebuffer()}else K.__webglFramebuffer=r.createFramebuffer();if(Le)for(let Ae=0,He=me.length;Ae<He;Ae++){const Pt=n.get(me[Ae]);Pt.__webglTexture===void 0&&(Pt.__webglTexture=r.createTexture(),a.memory.textures++)}if(L.samples>0&&tt(L)===!1){K.__webglMultisampledFramebuffer=r.createFramebuffer(),K.__webglColorRenderbuffer=[],t.bindFramebuffer(r.FRAMEBUFFER,K.__webglMultisampledFramebuffer);for(let Ae=0;Ae<me.length;Ae++){const He=me[Ae];K.__webglColorRenderbuffer[Ae]=r.createRenderbuffer(),r.bindRenderbuffer(r.RENDERBUFFER,K.__webglColorRenderbuffer[Ae]);const Pt=s.convert(He.format,He.colorSpace),_e=s.convert(He.type),Ce=w(He.internalFormat,Pt,_e,He.colorSpace,L.isXRRenderTarget===!0),Ge=it(L);r.renderbufferStorageMultisample(r.RENDERBUFFER,Ge,Ce,L.width,L.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Ae,r.RENDERBUFFER,K.__webglColorRenderbuffer[Ae])}r.bindRenderbuffer(r.RENDERBUFFER,null),L.depthBuffer&&(K.__webglDepthRenderbuffer=r.createRenderbuffer(),Me(K.__webglDepthRenderbuffer,L,!0)),t.bindFramebuffer(r.FRAMEBUFFER,null)}}if(le){t.bindTexture(r.TEXTURE_CUBE_MAP,ue.__webglTexture),Xe(r.TEXTURE_CUBE_MAP,T);for(let Ae=0;Ae<6;Ae++)if(T.mipmaps&&T.mipmaps.length>0)for(let He=0;He<T.mipmaps.length;He++)Be(K.__webglFramebuffer[Ae][He],L,T,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Ae,He);else Be(K.__webglFramebuffer[Ae],L,T,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Ae,0);v(T)&&_(r.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Le){for(let Ae=0,He=me.length;Ae<He;Ae++){const Pt=me[Ae],_e=n.get(Pt);t.bindTexture(r.TEXTURE_2D,_e.__webglTexture),Xe(r.TEXTURE_2D,Pt),Be(K.__webglFramebuffer,L,Pt,r.COLOR_ATTACHMENT0+Ae,r.TEXTURE_2D,0),v(Pt)&&_(r.TEXTURE_2D)}t.unbindTexture()}else{let Ae=r.TEXTURE_2D;if((L.isWebGL3DRenderTarget||L.isWebGLArrayRenderTarget)&&(Ae=L.isWebGL3DRenderTarget?r.TEXTURE_3D:r.TEXTURE_2D_ARRAY),t.bindTexture(Ae,ue.__webglTexture),Xe(Ae,T),T.mipmaps&&T.mipmaps.length>0)for(let He=0;He<T.mipmaps.length;He++)Be(K.__webglFramebuffer[He],L,T,r.COLOR_ATTACHMENT0,Ae,He);else Be(K.__webglFramebuffer,L,T,r.COLOR_ATTACHMENT0,Ae,0);v(T)&&_(Ae),t.unbindTexture()}L.depthBuffer&&ut(L)}function be(L){const T=L.textures;for(let K=0,ue=T.length;K<ue;K++){const me=T[K];if(v(me)){const le=R(L),Le=n.get(me).__webglTexture;t.bindTexture(le,Le),_(le),t.unbindTexture()}}}const Oe=[],V=[];function ct(L){if(L.samples>0){if(tt(L)===!1){const T=L.textures,K=L.width,ue=L.height;let me=r.COLOR_BUFFER_BIT;const le=L.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Le=n.get(L),Ae=T.length>1;if(Ae)for(let He=0;He<T.length;He++)t.bindFramebuffer(r.FRAMEBUFFER,Le.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+He,r.RENDERBUFFER,null),t.bindFramebuffer(r.FRAMEBUFFER,Le.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+He,r.TEXTURE_2D,null,0);t.bindFramebuffer(r.READ_FRAMEBUFFER,Le.__webglMultisampledFramebuffer),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Le.__webglFramebuffer);for(let He=0;He<T.length;He++){if(L.resolveDepthBuffer&&(L.depthBuffer&&(me|=r.DEPTH_BUFFER_BIT),L.stencilBuffer&&L.resolveStencilBuffer&&(me|=r.STENCIL_BUFFER_BIT)),Ae){r.framebufferRenderbuffer(r.READ_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.RENDERBUFFER,Le.__webglColorRenderbuffer[He]);const Pt=n.get(T[He]).__webglTexture;r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,Pt,0)}r.blitFramebuffer(0,0,K,ue,0,0,K,ue,me,r.NEAREST),u===!0&&(Oe.length=0,V.length=0,Oe.push(r.COLOR_ATTACHMENT0+He),L.depthBuffer&&L.resolveDepthBuffer===!1&&(Oe.push(le),V.push(le),r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,V)),r.invalidateFramebuffer(r.READ_FRAMEBUFFER,Oe))}if(t.bindFramebuffer(r.READ_FRAMEBUFFER,null),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),Ae)for(let He=0;He<T.length;He++){t.bindFramebuffer(r.FRAMEBUFFER,Le.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+He,r.RENDERBUFFER,Le.__webglColorRenderbuffer[He]);const Pt=n.get(T[He]).__webglTexture;t.bindFramebuffer(r.FRAMEBUFFER,Le.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+He,r.TEXTURE_2D,Pt,0)}t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Le.__webglMultisampledFramebuffer)}else if(L.depthBuffer&&L.resolveDepthBuffer===!1&&u){const T=L.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT;r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,[T])}}}function it(L){return Math.min(i.maxSamples,L.samples)}function tt(L){const T=n.get(L);return L.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&T.__useRenderToTexture!==!1}function ze(L){const T=a.render.frame;f.get(L)!==T&&(f.set(L,T),L.update())}function dt(L,T){const K=L.colorSpace,ue=L.format,me=L.type;return L.isCompressedTexture===!0||L.isVideoTexture===!0||K!==qn&&K!==xr&&(zt.getTransfer(K)===Qt?(ue!==pi||me!==rr)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",K)),T}function Ve(L){return typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement?(h.width=L.naturalWidth||L.width,h.height=L.naturalHeight||L.height):typeof VideoFrame<"u"&&L instanceof VideoFrame?(h.width=L.displayWidth,h.height=L.displayHeight):(h.width=L.width,h.height=L.height),h}this.allocateTextureUnit=$,this.resetTextureUnits=Z,this.setTexture2D=ae,this.setTexture2DArray=X,this.setTexture3D=he,this.setTextureCube=te,this.rebindTextures=Ke,this.setupRenderTarget=de,this.updateRenderTargetMipmap=be,this.updateMultisampleRenderTarget=ct,this.setupDepthRenderbuffer=ut,this.setupFrameBufferTexture=Be,this.useMultisampledRTT=tt}function _P(r,e){function t(n,i=xr){let s;const a=zt.getTransfer(i);if(n===rr)return r.UNSIGNED_BYTE;if(n===hd)return r.UNSIGNED_SHORT_4_4_4_4;if(n===dd)return r.UNSIGNED_SHORT_5_5_5_1;if(n===vg)return r.UNSIGNED_INT_5_9_9_9_REV;if(n===gg)return r.BYTE;if(n===_g)return r.SHORT;if(n===ea)return r.UNSIGNED_SHORT;if(n===ud)return r.INT;if(n===cs)return r.UNSIGNED_INT;if(n===Ei)return r.FLOAT;if(n===ra)return r.HALF_FLOAT;if(n===yg)return r.ALPHA;if(n===xg)return r.RGB;if(n===pi)return r.RGBA;if(n===bg)return r.LUMINANCE;if(n===Sg)return r.LUMINANCE_ALPHA;if(n===Ys)return r.DEPTH_COMPONENT;if(n===io)return r.DEPTH_STENCIL;if(n===fd)return r.RED;if(n===pd)return r.RED_INTEGER;if(n===Eg)return r.RG;if(n===md)return r.RG_INTEGER;if(n===gd)return r.RGBA_INTEGER;if(n===wl||n===Al||n===Rl||n===Pl)if(a===Qt)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===wl)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Al)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Rl)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Pl)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===wl)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Al)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Rl)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Pl)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Rh||n===Ph||n===Ch||n===Dh)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===Rh)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Ph)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Ch)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Dh)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Ih||n===Lh||n===Fh)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===Ih||n===Lh)return a===Qt?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===Fh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Nh||n===Oh||n===Uh||n===Bh||n===kh||n===zh||n===Hh||n===Vh||n===Gh||n===Wh||n===jh||n===Xh||n===qh||n===Yh)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===Nh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Oh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Uh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Bh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===kh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===zh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===Hh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Vh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Gh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Wh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===jh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Xh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===qh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===Yh)return a===Qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Cl||n===Kh||n===$h)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===Cl)return a===Qt?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Kh)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===$h)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Mg||n===Zh||n===Qh||n===Jh)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===Cl)return s.COMPRESSED_RED_RGTC1_EXT;if(n===Zh)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===Qh)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Jh)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===no?r.UNSIGNED_INT_24_8:r[n]!==void 0?r[n]:null}return{convert:t}}class vP extends jn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Ii extends an{constructor(){super(),this.isGroup=!0,this.type="Group"}}const yP={type:"move"};class Zu{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Ii,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Ii,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new F,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new F),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Ii,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new F,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new F),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,s=null,a=null;const l=this._targetRay,u=this._grip,h=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(h&&e.hand){a=!0;for(const E of e.hand.values()){const v=t.getJointPose(E,n),_=this._getHandJoint(h,E);v!==null&&(_.matrix.fromArray(v.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.matrixWorldNeedsUpdate=!0,_.jointRadius=v.radius),_.visible=v!==null}const f=h.joints["index-finger-tip"],p=h.joints["thumb-tip"],m=f.position.distanceTo(p.position),g=.02,x=.005;h.inputState.pinching&&m>g+x?(h.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!h.inputState.pinching&&m<=g-x&&(h.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else u!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(u.matrix.fromArray(s.transform.matrix),u.matrix.decompose(u.position,u.rotation,u.scale),u.matrixWorldNeedsUpdate=!0,s.linearVelocity?(u.hasLinearVelocity=!0,u.linearVelocity.copy(s.linearVelocity)):u.hasLinearVelocity=!1,s.angularVelocity?(u.hasAngularVelocity=!0,u.angularVelocity.copy(s.angularVelocity)):u.hasAngularVelocity=!1));l!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&s!==null&&(i=s),i!==null&&(l.matrix.fromArray(i.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,i.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(i.linearVelocity)):l.hasLinearVelocity=!1,i.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(i.angularVelocity)):l.hasAngularVelocity=!1,this.dispatchEvent(yP)))}return l!==null&&(l.visible=i!==null),u!==null&&(u.visible=s!==null),h!==null&&(h.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Ii;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const xP=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,bP=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class SP{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const i=new Pn,s=e.properties.get(i);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new Tr({vertexShader:xP,fragmentShader:bP,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Pe(new uo(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class EP extends Rr{constructor(e,t){super();const n=this;let i=null,s=1,a=null,l="local-floor",u=1,h=null,f=null,p=null,m=null,g=null,x=null;const E=new SP,v=t.getContextAttributes();let _=null,R=null;const w=[],S=[],k=new vt;let N=null;const O=new jn;O.viewport=new Gt;const H=new jn;H.viewport=new Gt;const D=[O,H],A=new vP;let z=null,Z=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ce){let ge=w[ce];return ge===void 0&&(ge=new Zu,w[ce]=ge),ge.getTargetRaySpace()},this.getControllerGrip=function(ce){let ge=w[ce];return ge===void 0&&(ge=new Zu,w[ce]=ge),ge.getGripSpace()},this.getHand=function(ce){let ge=w[ce];return ge===void 0&&(ge=new Zu,w[ce]=ge),ge.getHandSpace()};function $(ce){const ge=S.indexOf(ce.inputSource);if(ge===-1)return;const Be=w[ge];Be!==void 0&&(Be.update(ce.inputSource,ce.frame,h||a),Be.dispatchEvent({type:ce.type,data:ce.inputSource}))}function ie(){i.removeEventListener("select",$),i.removeEventListener("selectstart",$),i.removeEventListener("selectend",$),i.removeEventListener("squeeze",$),i.removeEventListener("squeezestart",$),i.removeEventListener("squeezeend",$),i.removeEventListener("end",ie),i.removeEventListener("inputsourceschange",ae);for(let ce=0;ce<w.length;ce++){const ge=S[ce];ge!==null&&(S[ce]=null,w[ce].disconnect(ge))}z=null,Z=null,E.reset(),e.setRenderTarget(_),g=null,m=null,p=null,i=null,R=null,Tt.stop(),n.isPresenting=!1,e.setPixelRatio(N),e.setSize(k.width,k.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ce){s=ce,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ce){l=ce,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return h||a},this.setReferenceSpace=function(ce){h=ce},this.getBaseLayer=function(){return m!==null?m:g},this.getBinding=function(){return p},this.getFrame=function(){return x},this.getSession=function(){return i},this.setSession=async function(ce){if(i=ce,i!==null){if(_=e.getRenderTarget(),i.addEventListener("select",$),i.addEventListener("selectstart",$),i.addEventListener("selectend",$),i.addEventListener("squeeze",$),i.addEventListener("squeezestart",$),i.addEventListener("squeezeend",$),i.addEventListener("end",ie),i.addEventListener("inputsourceschange",ae),v.xrCompatible!==!0&&await t.makeXRCompatible(),N=e.getPixelRatio(),e.getSize(k),i.renderState.layers===void 0){const ge={antialias:v.antialias,alpha:!0,depth:v.depth,stencil:v.stencil,framebufferScaleFactor:s};g=new XRWebGLLayer(i,t,ge),i.updateRenderState({baseLayer:g}),e.setPixelRatio(1),e.setSize(g.framebufferWidth,g.framebufferHeight,!1),R=new us(g.framebufferWidth,g.framebufferHeight,{format:pi,type:rr,colorSpace:e.outputColorSpace,stencilBuffer:v.stencil})}else{let ge=null,Be=null,Me=null;v.depth&&(Me=v.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,ge=v.stencil?io:Ys,Be=v.stencil?no:cs);const ot={colorFormat:t.RGBA8,depthFormat:Me,scaleFactor:s};p=new XRWebGLBinding(i,t),m=p.createProjectionLayer(ot),i.updateRenderState({layers:[m]}),e.setPixelRatio(1),e.setSize(m.textureWidth,m.textureHeight,!1),R=new us(m.textureWidth,m.textureHeight,{format:pi,type:rr,depthTexture:new kg(m.textureWidth,m.textureHeight,Be,void 0,void 0,void 0,void 0,void 0,void 0,ge),stencilBuffer:v.stencil,colorSpace:e.outputColorSpace,samples:v.antialias?4:0,resolveDepthBuffer:m.ignoreDepthValues===!1})}R.isXRRenderTarget=!0,this.setFoveation(u),h=null,a=await i.requestReferenceSpace(l),Tt.setContext(i),Tt.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(i!==null)return i.environmentBlendMode},this.getDepthTexture=function(){return E.getDepthTexture()};function ae(ce){for(let ge=0;ge<ce.removed.length;ge++){const Be=ce.removed[ge],Me=S.indexOf(Be);Me>=0&&(S[Me]=null,w[Me].disconnect(Be))}for(let ge=0;ge<ce.added.length;ge++){const Be=ce.added[ge];let Me=S.indexOf(Be);if(Me===-1){for(let ut=0;ut<w.length;ut++)if(ut>=S.length){S.push(Be),Me=ut;break}else if(S[ut]===null){S[ut]=Be,Me=ut;break}if(Me===-1)break}const ot=w[Me];ot&&ot.connect(Be)}}const X=new F,he=new F;function te(ce,ge,Be){X.setFromMatrixPosition(ge.matrixWorld),he.setFromMatrixPosition(Be.matrixWorld);const Me=X.distanceTo(he),ot=ge.projectionMatrix.elements,ut=Be.projectionMatrix.elements,Ke=ot[14]/(ot[10]-1),de=ot[14]/(ot[10]+1),be=(ot[9]+1)/ot[5],Oe=(ot[9]-1)/ot[5],V=(ot[8]-1)/ot[0],ct=(ut[8]+1)/ut[0],it=Ke*V,tt=Ke*ct,ze=Me/(-V+ct),dt=ze*-V;if(ge.matrixWorld.decompose(ce.position,ce.quaternion,ce.scale),ce.translateX(dt),ce.translateZ(ze),ce.matrixWorld.compose(ce.position,ce.quaternion,ce.scale),ce.matrixWorldInverse.copy(ce.matrixWorld).invert(),ot[10]===-1)ce.projectionMatrix.copy(ge.projectionMatrix),ce.projectionMatrixInverse.copy(ge.projectionMatrixInverse);else{const Ve=Ke+ze,L=de+ze,T=it-dt,K=tt+(Me-dt),ue=be*de/L*Ve,me=Oe*de/L*Ve;ce.projectionMatrix.makePerspective(T,K,ue,me,Ve,L),ce.projectionMatrixInverse.copy(ce.projectionMatrix).invert()}}function ye(ce,ge){ge===null?ce.matrixWorld.copy(ce.matrix):ce.matrixWorld.multiplyMatrices(ge.matrixWorld,ce.matrix),ce.matrixWorldInverse.copy(ce.matrixWorld).invert()}this.updateCamera=function(ce){if(i===null)return;let ge=ce.near,Be=ce.far;E.texture!==null&&(E.depthNear>0&&(ge=E.depthNear),E.depthFar>0&&(Be=E.depthFar)),A.near=H.near=O.near=ge,A.far=H.far=O.far=Be,(z!==A.near||Z!==A.far)&&(i.updateRenderState({depthNear:A.near,depthFar:A.far}),z=A.near,Z=A.far),O.layers.mask=ce.layers.mask|2,H.layers.mask=ce.layers.mask|4,A.layers.mask=O.layers.mask|H.layers.mask;const Me=ce.parent,ot=A.cameras;ye(A,Me);for(let ut=0;ut<ot.length;ut++)ye(ot[ut],Me);ot.length===2?te(A,O,H):A.projectionMatrix.copy(O.projectionMatrix),Ee(ce,A,Me)};function Ee(ce,ge,Be){Be===null?ce.matrix.copy(ge.matrixWorld):(ce.matrix.copy(Be.matrixWorld),ce.matrix.invert(),ce.matrix.multiply(ge.matrixWorld)),ce.matrix.decompose(ce.position,ce.quaternion,ce.scale),ce.updateMatrixWorld(!0),ce.projectionMatrix.copy(ge.projectionMatrix),ce.projectionMatrixInverse.copy(ge.projectionMatrixInverse),ce.isPerspectiveCamera&&(ce.fov=ro*2*Math.atan(1/ce.projectionMatrix.elements[5]),ce.zoom=1)}this.getCamera=function(){return A},this.getFoveation=function(){if(!(m===null&&g===null))return u},this.setFoveation=function(ce){u=ce,m!==null&&(m.fixedFoveation=ce),g!==null&&g.fixedFoveation!==void 0&&(g.fixedFoveation=ce)},this.hasDepthSensing=function(){return E.texture!==null},this.getDepthSensingMesh=function(){return E.getMesh(A)};let ke=null;function Xe(ce,ge){if(f=ge.getViewerPose(h||a),x=ge,f!==null){const Be=f.views;g!==null&&(e.setRenderTargetFramebuffer(R,g.framebuffer),e.setRenderTarget(R));let Me=!1;Be.length!==A.cameras.length&&(A.cameras.length=0,Me=!0);for(let ut=0;ut<Be.length;ut++){const Ke=Be[ut];let de=null;if(g!==null)de=g.getViewport(Ke);else{const Oe=p.getViewSubImage(m,Ke);de=Oe.viewport,ut===0&&(e.setRenderTargetTextures(R,Oe.colorTexture,m.ignoreDepthValues?void 0:Oe.depthStencilTexture),e.setRenderTarget(R))}let be=D[ut];be===void 0&&(be=new jn,be.layers.enable(ut),be.viewport=new Gt,D[ut]=be),be.matrix.fromArray(Ke.transform.matrix),be.matrix.decompose(be.position,be.quaternion,be.scale),be.projectionMatrix.fromArray(Ke.projectionMatrix),be.projectionMatrixInverse.copy(be.projectionMatrix).invert(),be.viewport.set(de.x,de.y,de.width,de.height),ut===0&&(A.matrix.copy(be.matrix),A.matrix.decompose(A.position,A.quaternion,A.scale)),Me===!0&&A.cameras.push(be)}const ot=i.enabledFeatures;if(ot&&ot.includes("depth-sensing")){const ut=p.getDepthInformation(Be[0]);ut&&ut.isValid&&ut.texture&&E.init(e,ut,i.renderState)}}for(let Be=0;Be<w.length;Be++){const Me=S[Be],ot=w[Be];Me!==null&&ot!==void 0&&ot.update(Me,ge,h||a)}ke&&ke(ce,ge),ge.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:ge}),x=null}const Tt=new Bg;Tt.setAnimationLoop(Xe),this.setAnimationLoop=function(ce){ke=ce},this.dispose=function(){}}}const ts=new wi,MP=new St;function TP(r,e){function t(v,_){v.matrixAutoUpdate===!0&&v.updateMatrix(),_.value.copy(v.matrix)}function n(v,_){_.color.getRGB(v.fogColor.value,Ng(r)),_.isFog?(v.fogNear.value=_.near,v.fogFar.value=_.far):_.isFogExp2&&(v.fogDensity.value=_.density)}function i(v,_,R,w,S){_.isMeshBasicMaterial||_.isMeshLambertMaterial?s(v,_):_.isMeshToonMaterial?(s(v,_),p(v,_)):_.isMeshPhongMaterial?(s(v,_),f(v,_)):_.isMeshStandardMaterial?(s(v,_),m(v,_),_.isMeshPhysicalMaterial&&g(v,_,S)):_.isMeshMatcapMaterial?(s(v,_),x(v,_)):_.isMeshDepthMaterial?s(v,_):_.isMeshDistanceMaterial?(s(v,_),E(v,_)):_.isMeshNormalMaterial?s(v,_):_.isLineBasicMaterial?(a(v,_),_.isLineDashedMaterial&&l(v,_)):_.isPointsMaterial?u(v,_,R,w):_.isSpriteMaterial?h(v,_):_.isShadowMaterial?(v.color.value.copy(_.color),v.opacity.value=_.opacity):_.isShaderMaterial&&(_.uniformsNeedUpdate=!1)}function s(v,_){v.opacity.value=_.opacity,_.color&&v.diffuse.value.copy(_.color),_.emissive&&v.emissive.value.copy(_.emissive).multiplyScalar(_.emissiveIntensity),_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.bumpMap&&(v.bumpMap.value=_.bumpMap,t(_.bumpMap,v.bumpMapTransform),v.bumpScale.value=_.bumpScale,_.side===Jn&&(v.bumpScale.value*=-1)),_.normalMap&&(v.normalMap.value=_.normalMap,t(_.normalMap,v.normalMapTransform),v.normalScale.value.copy(_.normalScale),_.side===Jn&&v.normalScale.value.negate()),_.displacementMap&&(v.displacementMap.value=_.displacementMap,t(_.displacementMap,v.displacementMapTransform),v.displacementScale.value=_.displacementScale,v.displacementBias.value=_.displacementBias),_.emissiveMap&&(v.emissiveMap.value=_.emissiveMap,t(_.emissiveMap,v.emissiveMapTransform)),_.specularMap&&(v.specularMap.value=_.specularMap,t(_.specularMap,v.specularMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest);const R=e.get(_),w=R.envMap,S=R.envMapRotation;w&&(v.envMap.value=w,ts.copy(S),ts.x*=-1,ts.y*=-1,ts.z*=-1,w.isCubeTexture&&w.isRenderTargetTexture===!1&&(ts.y*=-1,ts.z*=-1),v.envMapRotation.value.setFromMatrix4(MP.makeRotationFromEuler(ts)),v.flipEnvMap.value=w.isCubeTexture&&w.isRenderTargetTexture===!1?-1:1,v.reflectivity.value=_.reflectivity,v.ior.value=_.ior,v.refractionRatio.value=_.refractionRatio),_.lightMap&&(v.lightMap.value=_.lightMap,v.lightMapIntensity.value=_.lightMapIntensity,t(_.lightMap,v.lightMapTransform)),_.aoMap&&(v.aoMap.value=_.aoMap,v.aoMapIntensity.value=_.aoMapIntensity,t(_.aoMap,v.aoMapTransform))}function a(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform))}function l(v,_){v.dashSize.value=_.dashSize,v.totalSize.value=_.dashSize+_.gapSize,v.scale.value=_.scale}function u(v,_,R,w){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.size.value=_.size*R,v.scale.value=w*.5,_.map&&(v.map.value=_.map,t(_.map,v.uvTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function h(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.rotation.value=_.rotation,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function f(v,_){v.specular.value.copy(_.specular),v.shininess.value=Math.max(_.shininess,1e-4)}function p(v,_){_.gradientMap&&(v.gradientMap.value=_.gradientMap)}function m(v,_){v.metalness.value=_.metalness,_.metalnessMap&&(v.metalnessMap.value=_.metalnessMap,t(_.metalnessMap,v.metalnessMapTransform)),v.roughness.value=_.roughness,_.roughnessMap&&(v.roughnessMap.value=_.roughnessMap,t(_.roughnessMap,v.roughnessMapTransform)),_.envMap&&(v.envMapIntensity.value=_.envMapIntensity)}function g(v,_,R){v.ior.value=_.ior,_.sheen>0&&(v.sheenColor.value.copy(_.sheenColor).multiplyScalar(_.sheen),v.sheenRoughness.value=_.sheenRoughness,_.sheenColorMap&&(v.sheenColorMap.value=_.sheenColorMap,t(_.sheenColorMap,v.sheenColorMapTransform)),_.sheenRoughnessMap&&(v.sheenRoughnessMap.value=_.sheenRoughnessMap,t(_.sheenRoughnessMap,v.sheenRoughnessMapTransform))),_.clearcoat>0&&(v.clearcoat.value=_.clearcoat,v.clearcoatRoughness.value=_.clearcoatRoughness,_.clearcoatMap&&(v.clearcoatMap.value=_.clearcoatMap,t(_.clearcoatMap,v.clearcoatMapTransform)),_.clearcoatRoughnessMap&&(v.clearcoatRoughnessMap.value=_.clearcoatRoughnessMap,t(_.clearcoatRoughnessMap,v.clearcoatRoughnessMapTransform)),_.clearcoatNormalMap&&(v.clearcoatNormalMap.value=_.clearcoatNormalMap,t(_.clearcoatNormalMap,v.clearcoatNormalMapTransform),v.clearcoatNormalScale.value.copy(_.clearcoatNormalScale),_.side===Jn&&v.clearcoatNormalScale.value.negate())),_.dispersion>0&&(v.dispersion.value=_.dispersion),_.iridescence>0&&(v.iridescence.value=_.iridescence,v.iridescenceIOR.value=_.iridescenceIOR,v.iridescenceThicknessMinimum.value=_.iridescenceThicknessRange[0],v.iridescenceThicknessMaximum.value=_.iridescenceThicknessRange[1],_.iridescenceMap&&(v.iridescenceMap.value=_.iridescenceMap,t(_.iridescenceMap,v.iridescenceMapTransform)),_.iridescenceThicknessMap&&(v.iridescenceThicknessMap.value=_.iridescenceThicknessMap,t(_.iridescenceThicknessMap,v.iridescenceThicknessMapTransform))),_.transmission>0&&(v.transmission.value=_.transmission,v.transmissionSamplerMap.value=R.texture,v.transmissionSamplerSize.value.set(R.width,R.height),_.transmissionMap&&(v.transmissionMap.value=_.transmissionMap,t(_.transmissionMap,v.transmissionMapTransform)),v.thickness.value=_.thickness,_.thicknessMap&&(v.thicknessMap.value=_.thicknessMap,t(_.thicknessMap,v.thicknessMapTransform)),v.attenuationDistance.value=_.attenuationDistance,v.attenuationColor.value.copy(_.attenuationColor)),_.anisotropy>0&&(v.anisotropyVector.value.set(_.anisotropy*Math.cos(_.anisotropyRotation),_.anisotropy*Math.sin(_.anisotropyRotation)),_.anisotropyMap&&(v.anisotropyMap.value=_.anisotropyMap,t(_.anisotropyMap,v.anisotropyMapTransform))),v.specularIntensity.value=_.specularIntensity,v.specularColor.value.copy(_.specularColor),_.specularColorMap&&(v.specularColorMap.value=_.specularColorMap,t(_.specularColorMap,v.specularColorMapTransform)),_.specularIntensityMap&&(v.specularIntensityMap.value=_.specularIntensityMap,t(_.specularIntensityMap,v.specularIntensityMapTransform))}function x(v,_){_.matcap&&(v.matcap.value=_.matcap)}function E(v,_){const R=e.get(_).light;v.referencePosition.value.setFromMatrixPosition(R.matrixWorld),v.nearDistance.value=R.shadow.camera.near,v.farDistance.value=R.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:i}}function wP(r,e,t,n){let i={},s={},a=[];const l=r.getParameter(r.MAX_UNIFORM_BUFFER_BINDINGS);function u(R,w){const S=w.program;n.uniformBlockBinding(R,S)}function h(R,w){let S=i[R.id];S===void 0&&(x(R),S=f(R),i[R.id]=S,R.addEventListener("dispose",v));const k=w.program;n.updateUBOMapping(R,k);const N=e.render.frame;s[R.id]!==N&&(m(R),s[R.id]=N)}function f(R){const w=p();R.__bindingPointIndex=w;const S=r.createBuffer(),k=R.__size,N=R.usage;return r.bindBuffer(r.UNIFORM_BUFFER,S),r.bufferData(r.UNIFORM_BUFFER,k,N),r.bindBuffer(r.UNIFORM_BUFFER,null),r.bindBufferBase(r.UNIFORM_BUFFER,w,S),S}function p(){for(let R=0;R<l;R++)if(a.indexOf(R)===-1)return a.push(R),R;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function m(R){const w=i[R.id],S=R.uniforms,k=R.__cache;r.bindBuffer(r.UNIFORM_BUFFER,w);for(let N=0,O=S.length;N<O;N++){const H=Array.isArray(S[N])?S[N]:[S[N]];for(let D=0,A=H.length;D<A;D++){const z=H[D];if(g(z,N,D,k)===!0){const Z=z.__offset,$=Array.isArray(z.value)?z.value:[z.value];let ie=0;for(let ae=0;ae<$.length;ae++){const X=$[ae],he=E(X);typeof X=="number"||typeof X=="boolean"?(z.__data[0]=X,r.bufferSubData(r.UNIFORM_BUFFER,Z+ie,z.__data)):X.isMatrix3?(z.__data[0]=X.elements[0],z.__data[1]=X.elements[1],z.__data[2]=X.elements[2],z.__data[3]=0,z.__data[4]=X.elements[3],z.__data[5]=X.elements[4],z.__data[6]=X.elements[5],z.__data[7]=0,z.__data[8]=X.elements[6],z.__data[9]=X.elements[7],z.__data[10]=X.elements[8],z.__data[11]=0):(X.toArray(z.__data,ie),ie+=he.storage/Float32Array.BYTES_PER_ELEMENT)}r.bufferSubData(r.UNIFORM_BUFFER,Z,z.__data)}}}r.bindBuffer(r.UNIFORM_BUFFER,null)}function g(R,w,S,k){const N=R.value,O=w+"_"+S;if(k[O]===void 0)return typeof N=="number"||typeof N=="boolean"?k[O]=N:k[O]=N.clone(),!0;{const H=k[O];if(typeof N=="number"||typeof N=="boolean"){if(H!==N)return k[O]=N,!0}else if(H.equals(N)===!1)return H.copy(N),!0}return!1}function x(R){const w=R.uniforms;let S=0;const k=16;for(let O=0,H=w.length;O<H;O++){const D=Array.isArray(w[O])?w[O]:[w[O]];for(let A=0,z=D.length;A<z;A++){const Z=D[A],$=Array.isArray(Z.value)?Z.value:[Z.value];for(let ie=0,ae=$.length;ie<ae;ie++){const X=$[ie],he=E(X),te=S%k,ye=te%he.boundary,Ee=te+ye;S+=ye,Ee!==0&&k-Ee<he.storage&&(S+=k-Ee),Z.__data=new Float32Array(he.storage/Float32Array.BYTES_PER_ELEMENT),Z.__offset=S,S+=he.storage}}}const N=S%k;return N>0&&(S+=k-N),R.__size=S,R.__cache={},this}function E(R){const w={boundary:0,storage:0};return typeof R=="number"||typeof R=="boolean"?(w.boundary=4,w.storage=4):R.isVector2?(w.boundary=8,w.storage=8):R.isVector3||R.isColor?(w.boundary=16,w.storage=12):R.isVector4?(w.boundary=16,w.storage=16):R.isMatrix3?(w.boundary=48,w.storage=48):R.isMatrix4?(w.boundary=64,w.storage=64):R.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",R),w}function v(R){const w=R.target;w.removeEventListener("dispose",v);const S=a.indexOf(w.__bindingPointIndex);a.splice(S,1),r.deleteBuffer(i[w.id]),delete i[w.id],delete s[w.id]}function _(){for(const R in i)r.deleteBuffer(i[R]);a=[],i={},s={}}return{bind:u,update:h,dispose:_}}class AP{constructor(e={}){const{canvas:t=mT(),context:n=null,depth:i=!0,stencil:s=!1,alpha:a=!1,antialias:l=!1,premultipliedAlpha:u=!0,preserveDrawingBuffer:h=!1,powerPreference:f="default",failIfMajorPerformanceCaveat:p=!1,reverseDepthBuffer:m=!1}=e;this.isWebGLRenderer=!0;let g;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");g=n.getContextAttributes().alpha}else g=a;const x=new Uint32Array(4),E=new Int32Array(4);let v=null,_=null;const R=[],w=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Rn,this.toneMapping=Mr,this.toneMappingExposure=1;const S=this;let k=!1,N=0,O=0,H=null,D=-1,A=null;const z=new Gt,Z=new Gt;let $=null;const ie=new pt(0);let ae=0,X=t.width,he=t.height,te=1,ye=null,Ee=null;const ke=new Gt(0,0,X,he),Xe=new Gt(0,0,X,he);let Tt=!1;const ce=new bd;let ge=!1,Be=!1;const Me=new St,ot=new St,ut=new F,Ke=new Gt,de={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let be=!1;function Oe(){return H===null?te:1}let V=n;function ct(P,j){return t.getContext(P,j)}try{const P={alpha:!0,depth:i,stencil:s,antialias:l,premultipliedAlpha:u,preserveDrawingBuffer:h,powerPreference:f,failIfMajorPerformanceCaveat:p};if("setAttribute"in t&&t.setAttribute("data-engine","three.js r170"),t.addEventListener("webglcontextlost",pe,!1),t.addEventListener("webglcontextrestored",Fe,!1),t.addEventListener("webglcontextcreationerror",De,!1),V===null){const j="webgl2";if(V=ct(j,P),V===null)throw ct(j)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(P){throw console.error("THREE.WebGLRenderer: "+P.message),P}let it,tt,ze,dt,Ve,L,T,K,ue,me,le,Le,Ae,He,Pt,_e,Ce,Ge,ft,We,At,mt,Ot,W;function Re(){it=new I1(V),it.init(),mt=new _P(V,it),tt=new w1(V,it,e,mt),ze=new pP(V,it),tt.reverseDepthBuffer&&m&&ze.buffers.depth.setReversed(!0),dt=new N1(V),Ve=new JR,L=new gP(V,it,ze,Ve,tt,mt,dt),T=new R1(S),K=new D1(S),ue=new VT(V),Ot=new M1(V,ue),me=new L1(V,ue,dt,Ot),le=new U1(V,me,ue,dt),ft=new O1(V,tt,L),_e=new A1(Ve),Le=new QR(S,T,K,it,tt,Ot,_e),Ae=new TP(S,Ve),He=new tP,Pt=new aP(it),Ge=new E1(S,T,K,ze,le,g,u),Ce=new dP(S,le,tt),W=new wP(V,dt,tt,ze),We=new T1(V,it,dt),At=new F1(V,it,dt),dt.programs=Le.programs,S.capabilities=tt,S.extensions=it,S.properties=Ve,S.renderLists=He,S.shadowMap=Ce,S.state=ze,S.info=dt}Re();const oe=new EP(S,V);this.xr=oe,this.getContext=function(){return V},this.getContextAttributes=function(){return V.getContextAttributes()},this.forceContextLoss=function(){const P=it.get("WEBGL_lose_context");P&&P.loseContext()},this.forceContextRestore=function(){const P=it.get("WEBGL_lose_context");P&&P.restoreContext()},this.getPixelRatio=function(){return te},this.setPixelRatio=function(P){P!==void 0&&(te=P,this.setSize(X,he,!1))},this.getSize=function(P){return P.set(X,he)},this.setSize=function(P,j,J=!0){if(oe.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}X=P,he=j,t.width=Math.floor(P*te),t.height=Math.floor(j*te),J===!0&&(t.style.width=P+"px",t.style.height=j+"px"),this.setViewport(0,0,P,j)},this.getDrawingBufferSize=function(P){return P.set(X*te,he*te).floor()},this.setDrawingBufferSize=function(P,j,J){X=P,he=j,te=J,t.width=Math.floor(P*J),t.height=Math.floor(j*J),this.setViewport(0,0,P,j)},this.getCurrentViewport=function(P){return P.copy(z)},this.getViewport=function(P){return P.copy(ke)},this.setViewport=function(P,j,J,ee){P.isVector4?ke.set(P.x,P.y,P.z,P.w):ke.set(P,j,J,ee),ze.viewport(z.copy(ke).multiplyScalar(te).round())},this.getScissor=function(P){return P.copy(Xe)},this.setScissor=function(P,j,J,ee){P.isVector4?Xe.set(P.x,P.y,P.z,P.w):Xe.set(P,j,J,ee),ze.scissor(Z.copy(Xe).multiplyScalar(te).round())},this.getScissorTest=function(){return Tt},this.setScissorTest=function(P){ze.setScissorTest(Tt=P)},this.setOpaqueSort=function(P){ye=P},this.setTransparentSort=function(P){Ee=P},this.getClearColor=function(P){return P.copy(Ge.getClearColor())},this.setClearColor=function(){Ge.setClearColor.apply(Ge,arguments)},this.getClearAlpha=function(){return Ge.getClearAlpha()},this.setClearAlpha=function(){Ge.setClearAlpha.apply(Ge,arguments)},this.clear=function(P=!0,j=!0,J=!0){let ee=0;if(P){let q=!1;if(H!==null){const we=H.texture.format;q=we===gd||we===md||we===pd}if(q){const we=H.texture.type,Ue=we===rr||we===cs||we===ea||we===no||we===hd||we===dd,$e=Ge.getClearColor(),Ze=Ge.getClearAlpha(),xt=$e.r,gt=$e.g,Qe=$e.b;Ue?(x[0]=xt,x[1]=gt,x[2]=Qe,x[3]=Ze,V.clearBufferuiv(V.COLOR,0,x)):(E[0]=xt,E[1]=gt,E[2]=Qe,E[3]=Ze,V.clearBufferiv(V.COLOR,0,E))}else ee|=V.COLOR_BUFFER_BIT}j&&(ee|=V.DEPTH_BUFFER_BIT),J&&(ee|=V.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),V.clear(ee)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",pe,!1),t.removeEventListener("webglcontextrestored",Fe,!1),t.removeEventListener("webglcontextcreationerror",De,!1),He.dispose(),Pt.dispose(),Ve.dispose(),T.dispose(),K.dispose(),le.dispose(),Ot.dispose(),W.dispose(),Le.dispose(),oe.dispose(),oe.removeEventListener("sessionstart",ve),oe.removeEventListener("sessionend",Je),Te.stop()};function pe(P){P.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),k=!0}function Fe(){console.log("THREE.WebGLRenderer: Context Restored."),k=!1;const P=dt.autoReset,j=Ce.enabled,J=Ce.autoUpdate,ee=Ce.needsUpdate,q=Ce.type;Re(),dt.autoReset=P,Ce.enabled=j,Ce.autoUpdate=J,Ce.needsUpdate=ee,Ce.type=q}function De(P){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",P.statusMessage)}function bt(P){const j=P.target;j.removeEventListener("dispose",bt),Zt(j)}function Zt(P){un(P),Ve.remove(P)}function un(P){const j=Ve.get(P).programs;j!==void 0&&(j.forEach(function(J){Le.releaseProgram(J)}),P.isShaderMaterial&&Le.releaseShaderCache(P))}this.renderBufferDirect=function(P,j,J,ee,q,we){j===null&&(j=de);const Ue=q.isMesh&&q.matrixWorld.determinant()<0,$e=Ut(P,j,J,ee,q);ze.setMaterial(ee,Ue);let Ze=J.index,xt=1;if(ee.wireframe===!0){if(Ze=me.getWireframeAttribute(J),Ze===void 0)return;xt=2}const gt=J.drawRange,Qe=J.attributes.position;let Bt=gt.start*xt,jt=(gt.start+gt.count)*xt;we!==null&&(Bt=Math.max(Bt,we.start*xt),jt=Math.min(jt,(we.start+we.count)*xt)),Ze!==null?(Bt=Math.max(Bt,0),jt=Math.min(jt,Ze.count)):Qe!=null&&(Bt=Math.max(Bt,0),jt=Math.min(jt,Qe.count));const qt=jt-Bt;if(qt<0||qt===1/0)return;Ot.setup(q,ee,$e,J,Ze);let hn,kt=We;if(Ze!==null&&(hn=ue.get(Ze),kt=At,kt.setIndex(hn)),q.isMesh)ee.wireframe===!0?(ze.setLineWidth(ee.wireframeLinewidth*Oe()),kt.setMode(V.LINES)):kt.setMode(V.TRIANGLES);else if(q.isLine){let et=ee.linewidth;et===void 0&&(et=1),ze.setLineWidth(et*Oe()),q.isLineSegments?kt.setMode(V.LINES):q.isLineLoop?kt.setMode(V.LINE_LOOP):kt.setMode(V.LINE_STRIP)}else q.isPoints?kt.setMode(V.POINTS):q.isSprite&&kt.setMode(V.TRIANGLES);if(q.isBatchedMesh)if(q._multiDrawInstances!==null)kt.renderMultiDrawInstances(q._multiDrawStarts,q._multiDrawCounts,q._multiDrawCount,q._multiDrawInstances);else if(it.get("WEBGL_multi_draw"))kt.renderMultiDraw(q._multiDrawStarts,q._multiDrawCounts,q._multiDrawCount);else{const et=q._multiDrawStarts,ei=q._multiDrawCounts,Ft=q._multiDrawCount,Cn=Ze?ue.get(Ze).bytesPerElement:1,Ai=Ve.get(ee).currentProgram.getUniforms();for(let mn=0;mn<Ft;mn++)Ai.setValue(V,"_gl_DrawID",mn),kt.render(et[mn]/Cn,ei[mn])}else if(q.isInstancedMesh)kt.renderInstances(Bt,qt,q.count);else if(J.isInstancedBufferGeometry){const et=J._maxInstanceCount!==void 0?J._maxInstanceCount:1/0,ei=Math.min(J.instanceCount,et);kt.renderInstances(Bt,qt,ei)}else kt.render(Bt,qt)};function U(P,j,J){P.transparent===!0&&P.side===Qn&&P.forceSinglePass===!1?(P.side=Jn,P.needsUpdate=!0,je(P,j,J),P.side=ir,P.needsUpdate=!0,je(P,j,J),P.side=Qn):je(P,j,J)}this.compile=function(P,j,J=null){J===null&&(J=P),_=Pt.get(J),_.init(j),w.push(_),J.traverseVisible(function(q){q.isLight&&q.layers.test(j.layers)&&(_.pushLight(q),q.castShadow&&_.pushShadow(q))}),P!==J&&P.traverseVisible(function(q){q.isLight&&q.layers.test(j.layers)&&(_.pushLight(q),q.castShadow&&_.pushShadow(q))}),_.setupLights();const ee=new Set;return P.traverse(function(q){if(!(q.isMesh||q.isPoints||q.isLine||q.isSprite))return;const we=q.material;if(we)if(Array.isArray(we))for(let Ue=0;Ue<we.length;Ue++){const $e=we[Ue];U($e,J,q),ee.add($e)}else U(we,J,q),ee.add(we)}),w.pop(),_=null,ee},this.compileAsync=function(P,j,J=null){const ee=this.compile(P,j,J);return new Promise(q=>{function we(){if(ee.forEach(function(Ue){Ve.get(Ue).currentProgram.isReady()&&ee.delete(Ue)}),ee.size===0){q(P);return}setTimeout(we,10)}it.get("KHR_parallel_shader_compile")!==null?we():setTimeout(we,10)})};let ne=null;function fe(P){ne&&ne(P)}function ve(){Te.stop()}function Je(){Te.start()}const Te=new Bg;Te.setAnimationLoop(fe),typeof self<"u"&&Te.setContext(self),this.setAnimationLoop=function(P){ne=P,oe.setAnimationLoop(P),P===null?Te.stop():Te.start()},oe.addEventListener("sessionstart",ve),oe.addEventListener("sessionend",Je),this.render=function(P,j){if(j!==void 0&&j.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(k===!0)return;if(P.matrixWorldAutoUpdate===!0&&P.updateMatrixWorld(),j.parent===null&&j.matrixWorldAutoUpdate===!0&&j.updateMatrixWorld(),oe.enabled===!0&&oe.isPresenting===!0&&(oe.cameraAutoUpdate===!0&&oe.updateCamera(j),j=oe.getCamera()),P.isScene===!0&&P.onBeforeRender(S,P,j,H),_=Pt.get(P,w.length),_.init(j),w.push(_),ot.multiplyMatrices(j.projectionMatrix,j.matrixWorldInverse),ce.setFromProjectionMatrix(ot),Be=this.localClippingEnabled,ge=_e.init(this.clippingPlanes,Be),v=He.get(P,R.length),v.init(),R.push(v),oe.enabled===!0&&oe.isPresenting===!0){const we=S.xr.getDepthSensingMesh();we!==null&&qe(we,j,-1/0,S.sortObjects)}qe(P,j,0,S.sortObjects),v.finish(),S.sortObjects===!0&&v.sort(ye,Ee),be=oe.enabled===!1||oe.isPresenting===!1||oe.hasDepthSensing()===!1,be&&Ge.addToRenderList(v,P),this.info.render.frame++,ge===!0&&_e.beginShadows();const J=_.state.shadowsArray;Ce.render(J,P,j),ge===!0&&_e.endShadows(),this.info.autoReset===!0&&this.info.reset();const ee=v.opaque,q=v.transmissive;if(_.setupLights(),j.isArrayCamera){const we=j.cameras;if(q.length>0)for(let Ue=0,$e=we.length;Ue<$e;Ue++){const Ze=we[Ue];ht(ee,q,P,Ze)}be&&Ge.render(P);for(let Ue=0,$e=we.length;Ue<$e;Ue++){const Ze=we[Ue];at(v,P,Ze,Ze.viewport)}}else q.length>0&&ht(ee,q,P,j),be&&Ge.render(P),at(v,P,j);H!==null&&(L.updateMultisampleRenderTarget(H),L.updateRenderTargetMipmap(H)),P.isScene===!0&&P.onAfterRender(S,P,j),Ot.resetDefaultState(),D=-1,A=null,w.pop(),w.length>0?(_=w[w.length-1],ge===!0&&_e.setGlobalState(S.clippingPlanes,_.state.camera)):_=null,R.pop(),R.length>0?v=R[R.length-1]:v=null};function qe(P,j,J,ee){if(P.visible===!1)return;if(P.layers.test(j.layers)){if(P.isGroup)J=P.renderOrder;else if(P.isLOD)P.autoUpdate===!0&&P.update(j);else if(P.isLight)_.pushLight(P),P.castShadow&&_.pushShadow(P);else if(P.isSprite){if(!P.frustumCulled||ce.intersectsSprite(P)){ee&&Ke.setFromMatrixPosition(P.matrixWorld).applyMatrix4(ot);const Ue=le.update(P),$e=P.material;$e.visible&&v.push(P,Ue,$e,J,Ke.z,null)}}else if((P.isMesh||P.isLine||P.isPoints)&&(!P.frustumCulled||ce.intersectsObject(P))){const Ue=le.update(P),$e=P.material;if(ee&&(P.boundingSphere!==void 0?(P.boundingSphere===null&&P.computeBoundingSphere(),Ke.copy(P.boundingSphere.center)):(Ue.boundingSphere===null&&Ue.computeBoundingSphere(),Ke.copy(Ue.boundingSphere.center)),Ke.applyMatrix4(P.matrixWorld).applyMatrix4(ot)),Array.isArray($e)){const Ze=Ue.groups;for(let xt=0,gt=Ze.length;xt<gt;xt++){const Qe=Ze[xt],Bt=$e[Qe.materialIndex];Bt&&Bt.visible&&v.push(P,Ue,Bt,J,Ke.z,Qe)}}else $e.visible&&v.push(P,Ue,$e,J,Ke.z,null)}}const we=P.children;for(let Ue=0,$e=we.length;Ue<$e;Ue++)qe(we[Ue],j,J,ee)}function at(P,j,J,ee){const q=P.opaque,we=P.transmissive,Ue=P.transparent;_.setupLightsView(J),ge===!0&&_e.setGlobalState(S.clippingPlanes,J),ee&&ze.viewport(z.copy(ee)),q.length>0&&yt(q,j,J),we.length>0&&yt(we,j,J),Ue.length>0&&yt(Ue,j,J),ze.buffers.depth.setTest(!0),ze.buffers.depth.setMask(!0),ze.buffers.color.setMask(!0),ze.setPolygonOffset(!1)}function ht(P,j,J,ee){if((J.isScene===!0?J.overrideMaterial:null)!==null)return;_.state.transmissionRenderTarget[ee.id]===void 0&&(_.state.transmissionRenderTarget[ee.id]=new us(1,1,{generateMipmaps:!0,type:it.has("EXT_color_buffer_half_float")||it.has("EXT_color_buffer_float")?ra:rr,minFilter:er,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:zt.workingColorSpace}));const we=_.state.transmissionRenderTarget[ee.id],Ue=ee.viewport||z;we.setSize(Ue.z,Ue.w);const $e=S.getRenderTarget();S.setRenderTarget(we),S.getClearColor(ie),ae=S.getClearAlpha(),ae<1&&S.setClearColor(16777215,.5),S.clear(),be&&Ge.render(J);const Ze=S.toneMapping;S.toneMapping=Mr;const xt=ee.viewport;if(ee.viewport!==void 0&&(ee.viewport=void 0),_.setupLightsView(ee),ge===!0&&_e.setGlobalState(S.clippingPlanes,ee),yt(P,J,ee),L.updateMultisampleRenderTarget(we),L.updateRenderTargetMipmap(we),it.has("WEBGL_multisampled_render_to_texture")===!1){let gt=!1;for(let Qe=0,Bt=j.length;Qe<Bt;Qe++){const jt=j[Qe],qt=jt.object,hn=jt.geometry,kt=jt.material,et=jt.group;if(kt.side===Qn&&qt.layers.test(ee.layers)){const ei=kt.side;kt.side=Jn,kt.needsUpdate=!0,Et(qt,J,ee,hn,kt,et),kt.side=ei,kt.needsUpdate=!0,gt=!0}}gt===!0&&(L.updateMultisampleRenderTarget(we),L.updateRenderTargetMipmap(we))}S.setRenderTarget($e),S.setClearColor(ie,ae),xt!==void 0&&(ee.viewport=xt),S.toneMapping=Ze}function yt(P,j,J){const ee=j.isScene===!0?j.overrideMaterial:null;for(let q=0,we=P.length;q<we;q++){const Ue=P[q],$e=Ue.object,Ze=Ue.geometry,xt=ee===null?Ue.material:ee,gt=Ue.group;$e.layers.test(J.layers)&&Et($e,j,J,Ze,xt,gt)}}function Et(P,j,J,ee,q,we){P.onBeforeRender(S,j,J,ee,q,we),P.modelViewMatrix.multiplyMatrices(J.matrixWorldInverse,P.matrixWorld),P.normalMatrix.getNormalMatrix(P.modelViewMatrix),q.onBeforeRender(S,j,J,ee,P,we),q.transparent===!0&&q.side===Qn&&q.forceSinglePass===!1?(q.side=Jn,q.needsUpdate=!0,S.renderBufferDirect(J,j,ee,q,P,we),q.side=ir,q.needsUpdate=!0,S.renderBufferDirect(J,j,ee,q,P,we),q.side=Qn):S.renderBufferDirect(J,j,ee,q,P,we),P.onAfterRender(S,j,J,ee,q,we)}function je(P,j,J){j.isScene!==!0&&(j=de);const ee=Ve.get(P),q=_.state.lights,we=_.state.shadowsArray,Ue=q.state.version,$e=Le.getParameters(P,q.state,we,j,J),Ze=Le.getProgramCacheKey($e);let xt=ee.programs;ee.environment=P.isMeshStandardMaterial?j.environment:null,ee.fog=j.fog,ee.envMap=(P.isMeshStandardMaterial?K:T).get(P.envMap||ee.environment),ee.envMapRotation=ee.environment!==null&&P.envMap===null?j.environmentRotation:P.envMapRotation,xt===void 0&&(P.addEventListener("dispose",bt),xt=new Map,ee.programs=xt);let gt=xt.get(Ze);if(gt!==void 0){if(ee.currentProgram===gt&&ee.lightsStateVersion===Ue)return rt(P,$e),gt}else $e.uniforms=Le.getUniforms(P),P.onBeforeCompile($e,S),gt=Le.acquireProgram($e,Ze),xt.set(Ze,gt),ee.uniforms=$e.uniforms;const Qe=ee.uniforms;return(!P.isShaderMaterial&&!P.isRawShaderMaterial||P.clipping===!0)&&(Qe.clippingPlanes=_e.uniform),rt(P,$e),ee.needsLights=st(P),ee.lightsStateVersion=Ue,ee.needsLights&&(Qe.ambientLightColor.value=q.state.ambient,Qe.lightProbe.value=q.state.probe,Qe.directionalLights.value=q.state.directional,Qe.directionalLightShadows.value=q.state.directionalShadow,Qe.spotLights.value=q.state.spot,Qe.spotLightShadows.value=q.state.spotShadow,Qe.rectAreaLights.value=q.state.rectArea,Qe.ltc_1.value=q.state.rectAreaLTC1,Qe.ltc_2.value=q.state.rectAreaLTC2,Qe.pointLights.value=q.state.point,Qe.pointLightShadows.value=q.state.pointShadow,Qe.hemisphereLights.value=q.state.hemi,Qe.directionalShadowMap.value=q.state.directionalShadowMap,Qe.directionalShadowMatrix.value=q.state.directionalShadowMatrix,Qe.spotShadowMap.value=q.state.spotShadowMap,Qe.spotLightMatrix.value=q.state.spotLightMatrix,Qe.spotLightMap.value=q.state.spotLightMap,Qe.pointShadowMap.value=q.state.pointShadowMap,Qe.pointShadowMatrix.value=q.state.pointShadowMatrix),ee.currentProgram=gt,ee.uniformsList=null,gt}function nt(P){if(P.uniformsList===null){const j=P.currentProgram.getUniforms();P.uniformsList=Dl.seqWithValue(j.seq,P.uniforms)}return P.uniformsList}function rt(P,j){const J=Ve.get(P);J.outputColorSpace=j.outputColorSpace,J.batching=j.batching,J.batchingColor=j.batchingColor,J.instancing=j.instancing,J.instancingColor=j.instancingColor,J.instancingMorph=j.instancingMorph,J.skinning=j.skinning,J.morphTargets=j.morphTargets,J.morphNormals=j.morphNormals,J.morphColors=j.morphColors,J.morphTargetsCount=j.morphTargetsCount,J.numClippingPlanes=j.numClippingPlanes,J.numIntersection=j.numClipIntersection,J.vertexAlphas=j.vertexAlphas,J.vertexTangents=j.vertexTangents,J.toneMapping=j.toneMapping}function Ut(P,j,J,ee,q){j.isScene!==!0&&(j=de),L.resetTextureUnits();const we=j.fog,Ue=ee.isMeshStandardMaterial?j.environment:null,$e=H===null?S.outputColorSpace:H.isXRRenderTarget===!0?H.texture.colorSpace:qn,Ze=(ee.isMeshStandardMaterial?K:T).get(ee.envMap||Ue),xt=ee.vertexColors===!0&&!!J.attributes.color&&J.attributes.color.itemSize===4,gt=!!J.attributes.tangent&&(!!ee.normalMap||ee.anisotropy>0),Qe=!!J.morphAttributes.position,Bt=!!J.morphAttributes.normal,jt=!!J.morphAttributes.color;let qt=Mr;ee.toneMapped&&(H===null||H.isXRRenderTarget===!0)&&(qt=S.toneMapping);const hn=J.morphAttributes.position||J.morphAttributes.normal||J.morphAttributes.color,kt=hn!==void 0?hn.length:0,et=Ve.get(ee),ei=_.state.lights;if(ge===!0&&(Be===!0||P!==A)){const Nn=P===A&&ee.id===D;_e.setState(ee,P,Nn)}let Ft=!1;ee.version===et.__version?(et.needsLights&&et.lightsStateVersion!==ei.state.version||et.outputColorSpace!==$e||q.isBatchedMesh&&et.batching===!1||!q.isBatchedMesh&&et.batching===!0||q.isBatchedMesh&&et.batchingColor===!0&&q.colorTexture===null||q.isBatchedMesh&&et.batchingColor===!1&&q.colorTexture!==null||q.isInstancedMesh&&et.instancing===!1||!q.isInstancedMesh&&et.instancing===!0||q.isSkinnedMesh&&et.skinning===!1||!q.isSkinnedMesh&&et.skinning===!0||q.isInstancedMesh&&et.instancingColor===!0&&q.instanceColor===null||q.isInstancedMesh&&et.instancingColor===!1&&q.instanceColor!==null||q.isInstancedMesh&&et.instancingMorph===!0&&q.morphTexture===null||q.isInstancedMesh&&et.instancingMorph===!1&&q.morphTexture!==null||et.envMap!==Ze||ee.fog===!0&&et.fog!==we||et.numClippingPlanes!==void 0&&(et.numClippingPlanes!==_e.numPlanes||et.numIntersection!==_e.numIntersection)||et.vertexAlphas!==xt||et.vertexTangents!==gt||et.morphTargets!==Qe||et.morphNormals!==Bt||et.morphColors!==jt||et.toneMapping!==qt||et.morphTargetsCount!==kt)&&(Ft=!0):(Ft=!0,et.__version=ee.version);let Cn=et.currentProgram;Ft===!0&&(Cn=je(ee,j,q));let Ai=!1,mn=!1,Ui=!1;const Yt=Cn.getUniforms(),Yn=et.uniforms;if(ze.useProgram(Cn.program)&&(Ai=!0,mn=!0,Ui=!0),ee.id!==D&&(D=ee.id,mn=!0),Ai||A!==P){ze.buffers.depth.getReversed()?(Me.copy(P.projectionMatrix),_T(Me),vT(Me),Yt.setValue(V,"projectionMatrix",Me)):Yt.setValue(V,"projectionMatrix",P.projectionMatrix),Yt.setValue(V,"viewMatrix",P.matrixWorldInverse);const Dn=Yt.map.cameraPosition;Dn!==void 0&&Dn.setValue(V,ut.setFromMatrixPosition(P.matrixWorld)),tt.logarithmicDepthBuffer&&Yt.setValue(V,"logDepthBufFC",2/(Math.log(P.far+1)/Math.LN2)),(ee.isMeshPhongMaterial||ee.isMeshToonMaterial||ee.isMeshLambertMaterial||ee.isMeshBasicMaterial||ee.isMeshStandardMaterial||ee.isShaderMaterial)&&Yt.setValue(V,"isOrthographic",P.isOrthographicCamera===!0),A!==P&&(A=P,mn=!0,Ui=!0)}if(q.isSkinnedMesh){Yt.setOptional(V,q,"bindMatrix"),Yt.setOptional(V,q,"bindMatrixInverse");const Nn=q.skeleton;Nn&&(Nn.boneTexture===null&&Nn.computeBoneTexture(),Yt.setValue(V,"boneTexture",Nn.boneTexture,L))}q.isBatchedMesh&&(Yt.setOptional(V,q,"batchingTexture"),Yt.setValue(V,"batchingTexture",q._matricesTexture,L),Yt.setOptional(V,q,"batchingIdTexture"),Yt.setValue(V,"batchingIdTexture",q._indirectTexture,L),Yt.setOptional(V,q,"batchingColorTexture"),q._colorsTexture!==null&&Yt.setValue(V,"batchingColorTexture",q._colorsTexture,L));const Bi=J.morphAttributes;if((Bi.position!==void 0||Bi.normal!==void 0||Bi.color!==void 0)&&ft.update(q,J,Cn),(mn||et.receiveShadow!==q.receiveShadow)&&(et.receiveShadow=q.receiveShadow,Yt.setValue(V,"receiveShadow",q.receiveShadow)),ee.isMeshGouraudMaterial&&ee.envMap!==null&&(Yn.envMap.value=Ze,Yn.flipEnvMap.value=Ze.isCubeTexture&&Ze.isRenderTargetTexture===!1?-1:1),ee.isMeshStandardMaterial&&ee.envMap===null&&j.environment!==null&&(Yn.envMapIntensity.value=j.environmentIntensity),mn&&(Yt.setValue(V,"toneMappingExposure",S.toneMappingExposure),et.needsLights&&Lt(Yn,Ui),we&&ee.fog===!0&&Ae.refreshFogUniforms(Yn,we),Ae.refreshMaterialUniforms(Yn,ee,te,he,_.state.transmissionRenderTarget[P.id]),Dl.upload(V,nt(et),Yn,L)),ee.isShaderMaterial&&ee.uniformsNeedUpdate===!0&&(Dl.upload(V,nt(et),Yn,L),ee.uniformsNeedUpdate=!1),ee.isSpriteMaterial&&Yt.setValue(V,"center",q.center),Yt.setValue(V,"modelViewMatrix",q.modelViewMatrix),Yt.setValue(V,"normalMatrix",q.normalMatrix),Yt.setValue(V,"modelMatrix",q.matrixWorld),ee.isShaderMaterial||ee.isRawShaderMaterial){const Nn=ee.uniformsGroups;for(let Dn=0,ti=Nn.length;Dn<ti;Dn++){const fs=Nn[Dn];W.update(fs,Cn),W.bind(fs,Cn)}}return Cn}function Lt(P,j){P.ambientLightColor.needsUpdate=j,P.lightProbe.needsUpdate=j,P.directionalLights.needsUpdate=j,P.directionalLightShadows.needsUpdate=j,P.pointLights.needsUpdate=j,P.pointLightShadows.needsUpdate=j,P.spotLights.needsUpdate=j,P.spotLightShadows.needsUpdate=j,P.rectAreaLights.needsUpdate=j,P.hemisphereLights.needsUpdate=j}function st(P){return P.isMeshLambertMaterial||P.isMeshToonMaterial||P.isMeshPhongMaterial||P.isMeshStandardMaterial||P.isShadowMaterial||P.isShaderMaterial&&P.lights===!0}this.getActiveCubeFace=function(){return N},this.getActiveMipmapLevel=function(){return O},this.getRenderTarget=function(){return H},this.setRenderTargetTextures=function(P,j,J){Ve.get(P.texture).__webglTexture=j,Ve.get(P.depthTexture).__webglTexture=J;const ee=Ve.get(P);ee.__hasExternalTextures=!0,ee.__autoAllocateDepthBuffer=J===void 0,ee.__autoAllocateDepthBuffer||it.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),ee.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(P,j){const J=Ve.get(P);J.__webglFramebuffer=j,J.__useDefaultFramebuffer=j===void 0},this.setRenderTarget=function(P,j=0,J=0){H=P,N=j,O=J;let ee=!0,q=null,we=!1,Ue=!1;if(P){const Ze=Ve.get(P);if(Ze.__useDefaultFramebuffer!==void 0)ze.bindFramebuffer(V.FRAMEBUFFER,null),ee=!1;else if(Ze.__webglFramebuffer===void 0)L.setupRenderTarget(P);else if(Ze.__hasExternalTextures)L.rebindTextures(P,Ve.get(P.texture).__webglTexture,Ve.get(P.depthTexture).__webglTexture);else if(P.depthBuffer){const Qe=P.depthTexture;if(Ze.__boundDepthTexture!==Qe){if(Qe!==null&&Ve.has(Qe)&&(P.width!==Qe.image.width||P.height!==Qe.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");L.setupDepthRenderbuffer(P)}}const xt=P.texture;(xt.isData3DTexture||xt.isDataArrayTexture||xt.isCompressedArrayTexture)&&(Ue=!0);const gt=Ve.get(P).__webglFramebuffer;P.isWebGLCubeRenderTarget?(Array.isArray(gt[j])?q=gt[j][J]:q=gt[j],we=!0):P.samples>0&&L.useMultisampledRTT(P)===!1?q=Ve.get(P).__webglMultisampledFramebuffer:Array.isArray(gt)?q=gt[J]:q=gt,z.copy(P.viewport),Z.copy(P.scissor),$=P.scissorTest}else z.copy(ke).multiplyScalar(te).floor(),Z.copy(Xe).multiplyScalar(te).floor(),$=Tt;if(ze.bindFramebuffer(V.FRAMEBUFFER,q)&&ee&&ze.drawBuffers(P,q),ze.viewport(z),ze.scissor(Z),ze.setScissorTest($),we){const Ze=Ve.get(P.texture);V.framebufferTexture2D(V.FRAMEBUFFER,V.COLOR_ATTACHMENT0,V.TEXTURE_CUBE_MAP_POSITIVE_X+j,Ze.__webglTexture,J)}else if(Ue){const Ze=Ve.get(P.texture),xt=j||0;V.framebufferTextureLayer(V.FRAMEBUFFER,V.COLOR_ATTACHMENT0,Ze.__webglTexture,J||0,xt)}D=-1},this.readRenderTargetPixels=function(P,j,J,ee,q,we,Ue){if(!(P&&P.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let $e=Ve.get(P).__webglFramebuffer;if(P.isWebGLCubeRenderTarget&&Ue!==void 0&&($e=$e[Ue]),$e){ze.bindFramebuffer(V.FRAMEBUFFER,$e);try{const Ze=P.texture,xt=Ze.format,gt=Ze.type;if(!tt.textureFormatReadable(xt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!tt.textureTypeReadable(gt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}j>=0&&j<=P.width-ee&&J>=0&&J<=P.height-q&&V.readPixels(j,J,ee,q,mt.convert(xt),mt.convert(gt),we)}finally{const Ze=H!==null?Ve.get(H).__webglFramebuffer:null;ze.bindFramebuffer(V.FRAMEBUFFER,Ze)}}},this.readRenderTargetPixelsAsync=async function(P,j,J,ee,q,we,Ue){if(!(P&&P.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let $e=Ve.get(P).__webglFramebuffer;if(P.isWebGLCubeRenderTarget&&Ue!==void 0&&($e=$e[Ue]),$e){const Ze=P.texture,xt=Ze.format,gt=Ze.type;if(!tt.textureFormatReadable(xt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!tt.textureTypeReadable(gt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(j>=0&&j<=P.width-ee&&J>=0&&J<=P.height-q){ze.bindFramebuffer(V.FRAMEBUFFER,$e);const Qe=V.createBuffer();V.bindBuffer(V.PIXEL_PACK_BUFFER,Qe),V.bufferData(V.PIXEL_PACK_BUFFER,we.byteLength,V.STREAM_READ),V.readPixels(j,J,ee,q,mt.convert(xt),mt.convert(gt),0);const Bt=H!==null?Ve.get(H).__webglFramebuffer:null;ze.bindFramebuffer(V.FRAMEBUFFER,Bt);const jt=V.fenceSync(V.SYNC_GPU_COMMANDS_COMPLETE,0);return V.flush(),await gT(V,jt,4),V.bindBuffer(V.PIXEL_PACK_BUFFER,Qe),V.getBufferSubData(V.PIXEL_PACK_BUFFER,0,we),V.deleteBuffer(Qe),V.deleteSync(jt),we}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(P,j=null,J=0){P.isTexture!==!0&&(Xo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),j=arguments[0]||null,P=arguments[1]);const ee=Math.pow(2,-J),q=Math.floor(P.image.width*ee),we=Math.floor(P.image.height*ee),Ue=j!==null?j.x:0,$e=j!==null?j.y:0;L.setTexture2D(P,0),V.copyTexSubImage2D(V.TEXTURE_2D,J,0,0,Ue,$e,q,we),ze.unbindTexture()},this.copyTextureToTexture=function(P,j,J=null,ee=null,q=0){P.isTexture!==!0&&(Xo("WebGLRenderer: copyTextureToTexture function signature has changed."),ee=arguments[0]||null,P=arguments[1],j=arguments[2],q=arguments[3]||0,J=null);let we,Ue,$e,Ze,xt,gt,Qe,Bt,jt;const qt=P.isCompressedTexture?P.mipmaps[q]:P.image;J!==null?(we=J.max.x-J.min.x,Ue=J.max.y-J.min.y,$e=J.isBox3?J.max.z-J.min.z:1,Ze=J.min.x,xt=J.min.y,gt=J.isBox3?J.min.z:0):(we=qt.width,Ue=qt.height,$e=qt.depth||1,Ze=0,xt=0,gt=0),ee!==null?(Qe=ee.x,Bt=ee.y,jt=ee.z):(Qe=0,Bt=0,jt=0);const hn=mt.convert(j.format),kt=mt.convert(j.type);let et;j.isData3DTexture?(L.setTexture3D(j,0),et=V.TEXTURE_3D):j.isDataArrayTexture||j.isCompressedArrayTexture?(L.setTexture2DArray(j,0),et=V.TEXTURE_2D_ARRAY):(L.setTexture2D(j,0),et=V.TEXTURE_2D),V.pixelStorei(V.UNPACK_FLIP_Y_WEBGL,j.flipY),V.pixelStorei(V.UNPACK_PREMULTIPLY_ALPHA_WEBGL,j.premultiplyAlpha),V.pixelStorei(V.UNPACK_ALIGNMENT,j.unpackAlignment);const ei=V.getParameter(V.UNPACK_ROW_LENGTH),Ft=V.getParameter(V.UNPACK_IMAGE_HEIGHT),Cn=V.getParameter(V.UNPACK_SKIP_PIXELS),Ai=V.getParameter(V.UNPACK_SKIP_ROWS),mn=V.getParameter(V.UNPACK_SKIP_IMAGES);V.pixelStorei(V.UNPACK_ROW_LENGTH,qt.width),V.pixelStorei(V.UNPACK_IMAGE_HEIGHT,qt.height),V.pixelStorei(V.UNPACK_SKIP_PIXELS,Ze),V.pixelStorei(V.UNPACK_SKIP_ROWS,xt),V.pixelStorei(V.UNPACK_SKIP_IMAGES,gt);const Ui=P.isDataArrayTexture||P.isData3DTexture,Yt=j.isDataArrayTexture||j.isData3DTexture;if(P.isRenderTargetTexture||P.isDepthTexture){const Yn=Ve.get(P),Bi=Ve.get(j),Nn=Ve.get(Yn.__renderTarget),Dn=Ve.get(Bi.__renderTarget);ze.bindFramebuffer(V.READ_FRAMEBUFFER,Nn.__webglFramebuffer),ze.bindFramebuffer(V.DRAW_FRAMEBUFFER,Dn.__webglFramebuffer);for(let ti=0;ti<$e;ti++)Ui&&V.framebufferTextureLayer(V.READ_FRAMEBUFFER,V.COLOR_ATTACHMENT0,Ve.get(P).__webglTexture,q,gt+ti),P.isDepthTexture?(Yt&&V.framebufferTextureLayer(V.DRAW_FRAMEBUFFER,V.COLOR_ATTACHMENT0,Ve.get(j).__webglTexture,q,jt+ti),V.blitFramebuffer(Ze,xt,we,Ue,Qe,Bt,we,Ue,V.DEPTH_BUFFER_BIT,V.NEAREST)):Yt?V.copyTexSubImage3D(et,q,Qe,Bt,jt+ti,Ze,xt,we,Ue):V.copyTexSubImage2D(et,q,Qe,Bt,jt+ti,Ze,xt,we,Ue);ze.bindFramebuffer(V.READ_FRAMEBUFFER,null),ze.bindFramebuffer(V.DRAW_FRAMEBUFFER,null)}else Yt?P.isDataTexture||P.isData3DTexture?V.texSubImage3D(et,q,Qe,Bt,jt,we,Ue,$e,hn,kt,qt.data):j.isCompressedArrayTexture?V.compressedTexSubImage3D(et,q,Qe,Bt,jt,we,Ue,$e,hn,qt.data):V.texSubImage3D(et,q,Qe,Bt,jt,we,Ue,$e,hn,kt,qt):P.isDataTexture?V.texSubImage2D(V.TEXTURE_2D,q,Qe,Bt,we,Ue,hn,kt,qt.data):P.isCompressedTexture?V.compressedTexSubImage2D(V.TEXTURE_2D,q,Qe,Bt,qt.width,qt.height,hn,qt.data):V.texSubImage2D(V.TEXTURE_2D,q,Qe,Bt,we,Ue,hn,kt,qt);V.pixelStorei(V.UNPACK_ROW_LENGTH,ei),V.pixelStorei(V.UNPACK_IMAGE_HEIGHT,Ft),V.pixelStorei(V.UNPACK_SKIP_PIXELS,Cn),V.pixelStorei(V.UNPACK_SKIP_ROWS,Ai),V.pixelStorei(V.UNPACK_SKIP_IMAGES,mn),q===0&&j.generateMipmaps&&V.generateMipmap(et),ze.unbindTexture()},this.copyTextureToTexture3D=function(P,j,J=null,ee=null,q=0){return P.isTexture!==!0&&(Xo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),J=arguments[0]||null,ee=arguments[1]||null,P=arguments[2],j=arguments[3],q=arguments[4]||0),Xo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(P,j,J,ee,q)},this.initRenderTarget=function(P){Ve.get(P).__webglFramebuffer===void 0&&L.setupRenderTarget(P)},this.initTexture=function(P){P.isCubeTexture?L.setTextureCube(P,0):P.isData3DTexture?L.setTexture3D(P,0):P.isDataArrayTexture||P.isCompressedArrayTexture?L.setTexture2DArray(P,0):L.setTexture2D(P,0),ze.unbindTexture()},this.resetState=function(){N=0,O=0,H=null,ze.reset(),Ot.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return tr}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=zt._getDrawingBufferColorSpace(e),t.unpackColorSpace=zt._getUnpackColorSpace()}}class Md{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new pt(e),this.density=t}clone(){return new Md(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class RP extends an{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new wi,this.environmentIntensity=1,this.environmentRotation=new wi,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class PP{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=td,this.updateRanges=[],this.version=0,this.uuid=Mi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let i=0,s=this.stride;i<s;i++)this.array[e+i]=t.array[n+i];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Mi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Mi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Gn=new F;class Td{constructor(e,t,n,i=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=i}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Gn.fromBufferAttribute(this,t),Gn.applyMatrix4(e),this.setXYZ(t,Gn.x,Gn.y,Gn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Gn.fromBufferAttribute(this,t),Gn.applyNormalMatrix(e),this.setXYZ(t,Gn.x,Gn.y,Gn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Gn.fromBufferAttribute(this,t),Gn.transformDirection(e),this.setXYZ(t,Gn.x,Gn.y,Gn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=bi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=$t(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=$t(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=$t(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=$t(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=$t(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=bi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=bi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=bi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=bi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=$t(t,this.array),n=$t(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=$t(t,this.array),n=$t(n,this.array),i=$t(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=$t(t,this.array),n=$t(n,this.array),i=$t(i,this.array),s=$t(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return new pn(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Td(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const wm=new F,Am=new Gt,Rm=new Gt,CP=new F,Pm=new St,dl=new F,Qu=new Fi,Cm=new St,Ju=new co;class Ul extends Pe{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=Dp,this.bindMatrix=new St,this.bindMatrixInverse=new St,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new Ti),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,dl),this.boundingBox.expandByPoint(dl)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new Fi),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,dl),this.boundingSphere.expandByPoint(dl)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,i=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Qu.copy(this.boundingSphere),Qu.applyMatrix4(i),e.ray.intersectsSphere(Qu)!==!1&&(Cm.copy(i).invert(),Ju.copy(e.ray).applyMatrix4(Cm),!(this.boundingBox!==null&&Ju.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,Ju)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new Gt,t=this.geometry.attributes.skinWeight;for(let n=0,i=t.count;n<i;n++){e.fromBufferAttribute(t,n);const s=1/e.manhattanLength();s!==1/0?e.multiplyScalar(s):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===Dp?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===BM?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,i=this.geometry;Am.fromBufferAttribute(i.attributes.skinIndex,e),Rm.fromBufferAttribute(i.attributes.skinWeight,e),wm.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let s=0;s<4;s++){const a=Rm.getComponent(s);if(a!==0){const l=Am.getComponent(s);Pm.multiplyMatrices(n.bones[l].matrixWorld,n.boneInverses[l]),t.addScaledVector(CP.copy(wm).applyMatrix4(Pm),a)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Gl extends an{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Wg extends Pn{constructor(e=null,t=1,n=1,i,s,a,l,u,h=Xn,f=Xn,p,m){super(null,a,l,u,h,f,i,s,p,m),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Dm=new St,DP=new St;class sa{constructor(e=[],t=[]){this.uuid=Mi(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,i=this.bones.length;n<i;n++)this.boneInverses.push(new St)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new St;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,i=this.boneTexture;for(let s=0,a=e.length;s<a;s++){const l=e[s]?e[s].matrixWorld:DP;Dm.multiplyMatrices(l,t[s]),Dm.toArray(n,s*16)}i!==null&&(i.needsUpdate=!0)}clone(){return new sa(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Wg(t,e,e,pi,Ei);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const i=this.bones[t];if(i.name===e)return i}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,i=e.bones.length;n<i;n++){const s=e.bones[n];let a=t[s];a===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",s),a=new Gl),this.bones.push(a),this.boneInverses.push(new St().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let i=0,s=t.length;i<s;i++){const a=t[i];e.bones.push(a.uuid);const l=n[i];e.boneInverses.push(l.toArray())}return e}}class id extends pn{constructor(e,t,n,i=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=i}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const zs=new St,Im=new St,fl=[],Lm=new Ti,IP=new St,Bo=new Pe,ko=new Fi;class LP extends Pe{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new id(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let i=0;i<n;i++)this.setMatrixAt(i,IP)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new Ti),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,zs),Lm.copy(e.boundingBox).applyMatrix4(zs),this.boundingBox.union(Lm)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new Fi),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,zs),ko.copy(e.boundingSphere).applyMatrix4(zs),this.boundingSphere.union(ko)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,i=this.morphTexture.source.data.data,s=n.length+1,a=e*s+1;for(let l=0;l<n.length;l++)n[l]=i[a+l]}raycast(e,t){const n=this.matrixWorld,i=this.count;if(Bo.geometry=this.geometry,Bo.material=this.material,Bo.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),ko.copy(this.boundingSphere),ko.applyMatrix4(n),e.ray.intersectsSphere(ko)!==!1))for(let s=0;s<i;s++){this.getMatrixAt(s,zs),Im.multiplyMatrices(n,zs),Bo.matrixWorld=Im,Bo.raycast(e,fl);for(let a=0,l=fl.length;a<l;a++){const u=fl[a];u.instanceId=s,u.object=this,t.push(u)}fl.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new id(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,i=n.length+1;this.morphTexture===null&&(this.morphTexture=new Wg(new Float32Array(i*this.count),i,this.count,fd,Ei));const s=this.morphTexture.source.data.data;let a=0;for(let h=0;h<n.length;h++)a+=n[h];const l=this.geometry.morphTargetsRelative?1:1-a,u=i*e;s[u]=l,s.set(n,u+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class Wl extends Li{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new pt(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Bl=new F,kl=new F,Fm=new St,zo=new co,pl=new Fi,eh=new F,Nm=new F;class xi extends an{constructor(e=new Sn,t=new Wl){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let i=1,s=t.count;i<s;i++)Bl.fromBufferAttribute(t,i-1),kl.fromBufferAttribute(t,i),n[i]=n[i-1],n[i]+=Bl.distanceTo(kl);e.setAttribute("lineDistance",new Wt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),pl.copy(n.boundingSphere),pl.applyMatrix4(i),pl.radius+=s,e.ray.intersectsSphere(pl)===!1)return;Fm.copy(i).invert(),zo.copy(e.ray).applyMatrix4(Fm);const l=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=l*l,h=this.isLineSegments?2:1,f=n.index,m=n.attributes.position;if(f!==null){const g=Math.max(0,a.start),x=Math.min(f.count,a.start+a.count);for(let E=g,v=x-1;E<v;E+=h){const _=f.getX(E),R=f.getX(E+1),w=ml(this,e,zo,u,_,R);w&&t.push(w)}if(this.isLineLoop){const E=f.getX(x-1),v=f.getX(g),_=ml(this,e,zo,u,E,v);_&&t.push(_)}}else{const g=Math.max(0,a.start),x=Math.min(m.count,a.start+a.count);for(let E=g,v=x-1;E<v;E+=h){const _=ml(this,e,zo,u,E,E+1);_&&t.push(_)}if(this.isLineLoop){const E=ml(this,e,zo,u,x-1,g);E&&t.push(E)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const l=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[l]=s}}}}}function ml(r,e,t,n,i,s){const a=r.geometry.attributes.position;if(Bl.fromBufferAttribute(a,i),kl.fromBufferAttribute(a,s),t.distanceSqToSegment(Bl,kl,eh,Nm)>n)return;eh.applyMatrix4(r.matrixWorld);const u=e.ray.origin.distanceTo(eh);if(!(u<e.near||u>e.far))return{distance:u,point:Nm.clone().applyMatrix4(r.matrixWorld),index:i,face:null,faceIndex:null,barycoord:null,object:r}}const Om=new F,Um=new F;class jg extends xi{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let i=0,s=t.count;i<s;i+=2)Om.fromBufferAttribute(t,i),Um.fromBufferAttribute(t,i+1),n[i]=i===0?0:n[i-1],n[i+1]=n[i]+Om.distanceTo(Um);e.setAttribute("lineDistance",new Wt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class FP extends xi{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class Xg extends Li{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new pt(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Bm=new St,rd=new co,gl=new Fi,_l=new F;class NP extends an{constructor(e=new Sn,t=new Xg){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),gl.copy(n.boundingSphere),gl.applyMatrix4(i),gl.radius+=s,e.ray.intersectsSphere(gl)===!1)return;Bm.copy(i).invert(),rd.copy(e.ray).applyMatrix4(Bm);const l=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=l*l,h=n.index,p=n.attributes.position;if(h!==null){const m=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let x=m,E=g;x<E;x++){const v=h.getX(x);_l.fromBufferAttribute(p,v),km(_l,v,u,i,e,t,this)}}else{const m=Math.max(0,a.start),g=Math.min(p.count,a.start+a.count);for(let x=m,E=g;x<E;x++)_l.fromBufferAttribute(p,x),km(_l,x,u,i,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const l=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[l]=s}}}}}function km(r,e,t,n,i,s,a){const l=rd.distanceSqToPoint(r);if(l<t){const u=new F;rd.closestPointToPoint(r,u),u.applyMatrix4(n);const h=i.ray.origin.distanceTo(u);if(h<i.near||h>i.far)return;s.push({distance:h,distanceToRay:Math.sqrt(l),point:u,index:e,face:null,faceIndex:null,barycoord:null,object:a})}}class Ln extends Sn{constructor(e=1,t=1,n=1,i=32,s=1,a=!1,l=0,u=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:i,heightSegments:s,openEnded:a,thetaStart:l,thetaLength:u};const h=this;i=Math.floor(i),s=Math.floor(s);const f=[],p=[],m=[],g=[];let x=0;const E=[],v=n/2;let _=0;R(),a===!1&&(e>0&&w(!0),t>0&&w(!1)),this.setIndex(f),this.setAttribute("position",new Wt(p,3)),this.setAttribute("normal",new Wt(m,3)),this.setAttribute("uv",new Wt(g,2));function R(){const S=new F,k=new F;let N=0;const O=(t-e)/n;for(let H=0;H<=s;H++){const D=[],A=H/s,z=A*(t-e)+e;for(let Z=0;Z<=i;Z++){const $=Z/i,ie=$*u+l,ae=Math.sin(ie),X=Math.cos(ie);k.x=z*ae,k.y=-A*n+v,k.z=z*X,p.push(k.x,k.y,k.z),S.set(ae,O,X).normalize(),m.push(S.x,S.y,S.z),g.push($,1-A),D.push(x++)}E.push(D)}for(let H=0;H<i;H++)for(let D=0;D<s;D++){const A=E[D][H],z=E[D+1][H],Z=E[D+1][H+1],$=E[D][H+1];(e>0||D!==0)&&(f.push(A,z,$),N+=3),(t>0||D!==s-1)&&(f.push(z,Z,$),N+=3)}h.addGroup(_,N,0),_+=N}function w(S){const k=x,N=new vt,O=new F;let H=0;const D=S===!0?e:t,A=S===!0?1:-1;for(let Z=1;Z<=i;Z++)p.push(0,v*A,0),m.push(0,A,0),g.push(.5,.5),x++;const z=x;for(let Z=0;Z<=i;Z++){const ie=Z/i*u+l,ae=Math.cos(ie),X=Math.sin(ie);O.x=D*X,O.y=v*A,O.z=D*ae,p.push(O.x,O.y,O.z),m.push(0,A,0),N.x=ae*.5+.5,N.y=X*.5*A+.5,g.push(N.x,N.y),x++}for(let Z=0;Z<i;Z++){const $=k+Z,ie=z+Z;S===!0?f.push(ie,ie+1,$):f.push(ie+1,ie,$),H+=3}h.addGroup(_,H,S===!0?1:2),_+=H}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ln(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class wd extends Ln{constructor(e=1,t=1,n=32,i=1,s=!1,a=0,l=Math.PI*2){super(0,e,t,n,i,s,a,l),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:i,openEnded:s,thetaStart:a,thetaLength:l}}static fromJSON(e){return new wd(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Ad extends Sn{constructor(e=[],t=[],n=1,i=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:i};const s=[],a=[];l(i),h(n),f(),this.setAttribute("position",new Wt(s,3)),this.setAttribute("normal",new Wt(s.slice(),3)),this.setAttribute("uv",new Wt(a,2)),i===0?this.computeVertexNormals():this.normalizeNormals();function l(R){const w=new F,S=new F,k=new F;for(let N=0;N<t.length;N+=3)g(t[N+0],w),g(t[N+1],S),g(t[N+2],k),u(w,S,k,R)}function u(R,w,S,k){const N=k+1,O=[];for(let H=0;H<=N;H++){O[H]=[];const D=R.clone().lerp(S,H/N),A=w.clone().lerp(S,H/N),z=N-H;for(let Z=0;Z<=z;Z++)Z===0&&H===N?O[H][Z]=D:O[H][Z]=D.clone().lerp(A,Z/z)}for(let H=0;H<N;H++)for(let D=0;D<2*(N-H)-1;D++){const A=Math.floor(D/2);D%2===0?(m(O[H][A+1]),m(O[H+1][A]),m(O[H][A])):(m(O[H][A+1]),m(O[H+1][A+1]),m(O[H+1][A]))}}function h(R){const w=new F;for(let S=0;S<s.length;S+=3)w.x=s[S+0],w.y=s[S+1],w.z=s[S+2],w.normalize().multiplyScalar(R),s[S+0]=w.x,s[S+1]=w.y,s[S+2]=w.z}function f(){const R=new F;for(let w=0;w<s.length;w+=3){R.x=s[w+0],R.y=s[w+1],R.z=s[w+2];const S=v(R)/2/Math.PI+.5,k=_(R)/Math.PI+.5;a.push(S,1-k)}x(),p()}function p(){for(let R=0;R<a.length;R+=6){const w=a[R+0],S=a[R+2],k=a[R+4],N=Math.max(w,S,k),O=Math.min(w,S,k);N>.9&&O<.1&&(w<.2&&(a[R+0]+=1),S<.2&&(a[R+2]+=1),k<.2&&(a[R+4]+=1))}}function m(R){s.push(R.x,R.y,R.z)}function g(R,w){const S=R*3;w.x=e[S+0],w.y=e[S+1],w.z=e[S+2]}function x(){const R=new F,w=new F,S=new F,k=new F,N=new vt,O=new vt,H=new vt;for(let D=0,A=0;D<s.length;D+=9,A+=6){R.set(s[D+0],s[D+1],s[D+2]),w.set(s[D+3],s[D+4],s[D+5]),S.set(s[D+6],s[D+7],s[D+8]),N.set(a[A+0],a[A+1]),O.set(a[A+2],a[A+3]),H.set(a[A+4],a[A+5]),k.copy(R).add(w).add(S).divideScalar(3);const z=v(k);E(N,A+0,R,z),E(O,A+2,w,z),E(H,A+4,S,z)}}function E(R,w,S,k){k<0&&R.x===1&&(a[w]=R.x-1),S.x===0&&S.z===0&&(a[w]=k/2/Math.PI+.5)}function v(R){return Math.atan2(R.z,-R.x)}function _(R){return Math.atan2(-R.y,Math.sqrt(R.x*R.x+R.z*R.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ad(e.vertices,e.indices,e.radius,e.details)}}class js extends Ad{constructor(e=1,t=0){const n=[1,0,0,-1,0,0,0,1,0,0,-1,0,0,0,1,0,0,-1],i=[0,2,4,0,4,3,0,3,5,0,5,2,1,2,5,1,5,3,1,3,4,1,4,2];super(n,i,e,t),this.type="OctahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new js(e.radius,e.detail)}}class oa extends Sn{constructor(e=1,t=32,n=16,i=0,s=Math.PI*2,a=0,l=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:i,phiLength:s,thetaStart:a,thetaLength:l},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const u=Math.min(a+l,Math.PI);let h=0;const f=[],p=new F,m=new F,g=[],x=[],E=[],v=[];for(let _=0;_<=n;_++){const R=[],w=_/n;let S=0;_===0&&a===0?S=.5/t:_===n&&u===Math.PI&&(S=-.5/t);for(let k=0;k<=t;k++){const N=k/t;p.x=-e*Math.cos(i+N*s)*Math.sin(a+w*l),p.y=e*Math.cos(a+w*l),p.z=e*Math.sin(i+N*s)*Math.sin(a+w*l),x.push(p.x,p.y,p.z),m.copy(p).normalize(),E.push(m.x,m.y,m.z),v.push(N+S,1-w),R.push(h++)}f.push(R)}for(let _=0;_<n;_++)for(let R=0;R<t;R++){const w=f[_][R+1],S=f[_][R],k=f[_+1][R],N=f[_+1][R+1];(_!==0||a>0)&&g.push(w,S,N),(_!==n-1||u<Math.PI)&&g.push(S,k,N)}this.setIndex(g),this.setAttribute("position",new Wt(x,3)),this.setAttribute("normal",new Wt(E,3)),this.setAttribute("uv",new Wt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new oa(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class ls extends Sn{constructor(e=1,t=.4,n=12,i=48,s=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:i,arc:s},n=Math.floor(n),i=Math.floor(i);const a=[],l=[],u=[],h=[],f=new F,p=new F,m=new F;for(let g=0;g<=n;g++)for(let x=0;x<=i;x++){const E=x/i*s,v=g/n*Math.PI*2;p.x=(e+t*Math.cos(v))*Math.cos(E),p.y=(e+t*Math.cos(v))*Math.sin(E),p.z=t*Math.sin(v),l.push(p.x,p.y,p.z),f.x=e*Math.cos(E),f.y=e*Math.sin(E),m.subVectors(p,f).normalize(),u.push(m.x,m.y,m.z),h.push(x/i),h.push(g/n)}for(let g=1;g<=n;g++)for(let x=1;x<=i;x++){const E=(i+1)*g+x-1,v=(i+1)*(g-1)+x-1,_=(i+1)*(g-1)+x,R=(i+1)*g+x;a.push(E,v,R),a.push(v,_,R)}this.setIndex(a),this.setAttribute("position",new Wt(l,3)),this.setAttribute("normal",new Wt(u,3)),this.setAttribute("uv",new Wt(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ls(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class hs extends Li{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new pt(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new pt(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=wg,this.normalScale=new vt(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new wi,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Ni extends hs{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new vt(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return Fn(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new pt(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new pt(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new pt(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function vl(r,e,t){return!r||!t&&r.constructor===e?r:typeof e.BYTES_PER_ELEMENT=="number"?new e(r):Array.prototype.slice.call(r)}function OP(r){return ArrayBuffer.isView(r)&&!(r instanceof DataView)}function UP(r){function e(i,s){return r[i]-r[s]}const t=r.length,n=new Array(t);for(let i=0;i!==t;++i)n[i]=i;return n.sort(e),n}function zm(r,e,t){const n=r.length,i=new r.constructor(n);for(let s=0,a=0;a!==n;++s){const l=t[s]*e;for(let u=0;u!==e;++u)i[a++]=r[l+u]}return i}function qg(r,e,t,n){let i=1,s=r[0];for(;s!==void 0&&s[n]===void 0;)s=r[i++];if(s===void 0)return;let a=s[n];if(a!==void 0)if(Array.isArray(a))do a=s[n],a!==void 0&&(e.push(s.time),t.push.apply(t,a)),s=r[i++];while(s!==void 0);else if(a.toArray!==void 0)do a=s[n],a!==void 0&&(e.push(s.time),a.toArray(t,t.length)),s=r[i++];while(s!==void 0);else do a=s[n],a!==void 0&&(e.push(s.time),t.push(a)),s=r[i++];while(s!==void 0)}class aa{constructor(e,t,n,i){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=i!==void 0?i:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,i=t[n],s=t[n-1];e:{t:{let a;n:{i:if(!(e<i)){for(let l=n+2;;){if(i===void 0){if(e<s)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===l)break;if(s=i,i=t[++n],e<i)break t}a=t.length;break n}if(!(e>=s)){const l=t[1];e<l&&(n=2,s=l);for(let u=n-2;;){if(s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===u)break;if(i=s,s=t[--n-1],e>=s)break t}a=n,n=0;break n}break e}for(;n<a;){const l=n+a>>>1;e<t[l]?a=l:n=l+1}if(i=t[n],s=t[n-1],s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(i===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,s,i)}return this.interpolate_(n,s,e,i)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i;for(let a=0;a!==i;++a)t[a]=n[s+a];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class BP extends aa{constructor(e,t,n,i){super(e,t,n,i),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Vs,endingEnd:Vs}}intervalChanged_(e,t,n){const i=this.parameterPositions;let s=e-2,a=e+1,l=i[s],u=i[a];if(l===void 0)switch(this.getSettings_().endingStart){case Gs:s=e,l=2*t-n;break;case Nl:s=i.length-2,l=t+i[s]-i[s+1];break;default:s=e,l=n}if(u===void 0)switch(this.getSettings_().endingEnd){case Gs:a=e,u=2*n-t;break;case Nl:a=1,u=n+i[1]-i[0];break;default:a=e-1,u=t}const h=(n-t)*.5,f=this.valueSize;this._weightPrev=h/(t-l),this._weightNext=h/(u-n),this._offsetPrev=s*f,this._offsetNext=a*f}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,l=this.valueSize,u=e*l,h=u-l,f=this._offsetPrev,p=this._offsetNext,m=this._weightPrev,g=this._weightNext,x=(n-t)/(i-t),E=x*x,v=E*x,_=-m*v+2*m*E-m*x,R=(1+m)*v+(-1.5-2*m)*E+(-.5+m)*x+1,w=(-1-g)*v+(1.5+g)*E+.5*x,S=g*v-g*E;for(let k=0;k!==l;++k)s[k]=_*a[f+k]+R*a[h+k]+w*a[u+k]+S*a[p+k];return s}}class Yg extends aa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,l=this.valueSize,u=e*l,h=u-l,f=(n-t)/(i-t),p=1-f;for(let m=0;m!==l;++m)s[m]=a[h+m]*p+a[u+m]*f;return s}}class kP extends aa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e){return this.copySampleValue_(e-1)}}class Oi{constructor(e,t,n,i){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=vl(t,this.TimeBufferType),this.values=vl(n,this.ValueBufferType),this.setInterpolation(i||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:vl(e.times,Array),values:vl(e.values,Array)};const i=e.getInterpolation();i!==e.DefaultInterpolation&&(n.interpolation=i)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new kP(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new Yg(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new BP(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case ta:t=this.InterpolantFactoryMethodDiscrete;break;case na:t=this.InterpolantFactoryMethodLinear;break;case Mu:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return ta;case this.InterpolantFactoryMethodLinear:return na;case this.InterpolantFactoryMethodSmooth:return Mu}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]*=e}return this}trim(e,t){const n=this.times,i=n.length;let s=0,a=i-1;for(;s!==i&&n[s]<e;)++s;for(;a!==-1&&n[a]>t;)--a;if(++a,s!==0||a!==i){s>=a&&(a=Math.max(a,1),s=a-1);const l=this.getValueSize();this.times=n.slice(s,a),this.values=this.values.slice(s*l,a*l)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,i=this.values,s=n.length;s===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let a=null;for(let l=0;l!==s;l++){const u=n[l];if(typeof u=="number"&&isNaN(u)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,l,u),e=!1;break}if(a!==null&&a>u){console.error("THREE.KeyframeTrack: Out of order keys.",this,l,u,a),e=!1;break}a=u}if(i!==void 0&&OP(i))for(let l=0,u=i.length;l!==u;++l){const h=i[l];if(isNaN(h)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,l,h),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),i=this.getInterpolation()===Mu,s=e.length-1;let a=1;for(let l=1;l<s;++l){let u=!1;const h=e[l],f=e[l+1];if(h!==f&&(l!==1||h!==e[0]))if(i)u=!0;else{const p=l*n,m=p-n,g=p+n;for(let x=0;x!==n;++x){const E=t[p+x];if(E!==t[m+x]||E!==t[g+x]){u=!0;break}}}if(u){if(l!==a){e[a]=e[l];const p=l*n,m=a*n;for(let g=0;g!==n;++g)t[m+g]=t[p+g]}++a}}if(s>0){e[a]=e[s];for(let l=s*n,u=a*n,h=0;h!==n;++h)t[u+h]=t[l+h];++a}return a!==e.length?(this.times=e.slice(0,a),this.values=t.slice(0,a*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,i=new n(this.name,e,t);return i.createInterpolant=this.createInterpolant,i}}Oi.prototype.TimeBufferType=Float32Array;Oi.prototype.ValueBufferType=Float32Array;Oi.prototype.DefaultInterpolation=na;class fo extends Oi{constructor(e,t,n){super(e,t,n)}}fo.prototype.ValueTypeName="bool";fo.prototype.ValueBufferType=Array;fo.prototype.DefaultInterpolation=ta;fo.prototype.InterpolantFactoryMethodLinear=void 0;fo.prototype.InterpolantFactoryMethodSmooth=void 0;class Kg extends Oi{}Kg.prototype.ValueTypeName="color";class oo extends Oi{}oo.prototype.ValueTypeName="number";class zP extends aa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,l=this.valueSize,u=(n-t)/(i-t);let h=e*l;for(let f=h+l;h!==f;h+=4)Dt.slerpFlat(s,0,a,h-l,a,h,u);return s}}class wr extends Oi{InterpolantFactoryMethodLinear(e){return new zP(this.times,this.values,this.getValueSize(),e)}}wr.prototype.ValueTypeName="quaternion";wr.prototype.InterpolantFactoryMethodSmooth=void 0;class po extends Oi{constructor(e,t,n){super(e,t,n)}}po.prototype.ValueTypeName="string";po.prototype.ValueBufferType=Array;po.prototype.DefaultInterpolation=ta;po.prototype.InterpolantFactoryMethodLinear=void 0;po.prototype.InterpolantFactoryMethodSmooth=void 0;class Ar extends Oi{}Ar.prototype.ValueTypeName="vector";class ao{constructor(e="",t=-1,n=[],i=vd){this.name=e,this.tracks=n,this.duration=t,this.blendMode=i,this.uuid=Mi(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,i=1/(e.fps||1);for(let a=0,l=n.length;a!==l;++a)t.push(VP(n[a]).scale(i));const s=new this(e.name,e.duration,t,e.blendMode);return s.uuid=e.uuid,s}static toJSON(e){const t=[],n=e.tracks,i={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let s=0,a=n.length;s!==a;++s)t.push(Oi.toJSON(n[s]));return i}static CreateFromMorphTargetSequence(e,t,n,i){const s=t.length,a=[];for(let l=0;l<s;l++){let u=[],h=[];u.push((l+s-1)%s,l,(l+1)%s),h.push(0,1,0);const f=UP(u);u=zm(u,1,f),h=zm(h,1,f),!i&&u[0]===0&&(u.push(s),h.push(h[0])),a.push(new oo(".morphTargetInfluences["+t[l].name+"]",u,h).scale(1/n))}return new this(e,-1,a)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const i=e;n=i.geometry&&i.geometry.animations||i.animations}for(let i=0;i<n.length;i++)if(n[i].name===t)return n[i];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const i={},s=/^([\w-]*?)([\d]+)$/;for(let l=0,u=e.length;l<u;l++){const h=e[l],f=h.name.match(s);if(f&&f.length>1){const p=f[1];let m=i[p];m||(i[p]=m=[]),m.push(h)}}const a=[];for(const l in i)a.push(this.CreateFromMorphTargetSequence(l,i[l],t,n));return a}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(p,m,g,x,E){if(g.length!==0){const v=[],_=[];qg(g,v,_,x),v.length!==0&&E.push(new p(m,v,_))}},i=[],s=e.name||"default",a=e.fps||30,l=e.blendMode;let u=e.length||-1;const h=e.hierarchy||[];for(let p=0;p<h.length;p++){const m=h[p].keys;if(!(!m||m.length===0))if(m[0].morphTargets){const g={};let x;for(x=0;x<m.length;x++)if(m[x].morphTargets)for(let E=0;E<m[x].morphTargets.length;E++)g[m[x].morphTargets[E]]=-1;for(const E in g){const v=[],_=[];for(let R=0;R!==m[x].morphTargets.length;++R){const w=m[x];v.push(w.time),_.push(w.morphTarget===E?1:0)}i.push(new oo(".morphTargetInfluence["+E+"]",v,_))}u=g.length*a}else{const g=".bones["+t[p].name+"]";n(Ar,g+".position",m,"pos",i),n(wr,g+".quaternion",m,"rot",i),n(Ar,g+".scale",m,"scl",i)}}return i.length===0?null:new this(s,u,i,l)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,i=e.length;n!==i;++n){const s=this.tracks[n];t=Math.max(t,s.times[s.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function HP(r){switch(r.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return oo;case"vector":case"vector2":case"vector3":case"vector4":return Ar;case"color":return Kg;case"quaternion":return wr;case"bool":case"boolean":return fo;case"string":return po}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+r)}function VP(r){if(r.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=HP(r.type);if(r.times===void 0){const t=[],n=[];qg(r.keys,t,n,"value"),r.times=t,r.values=n}return e.parse!==void 0?e.parse(r):new e(r.name,r.times,r.values,r.interpolation)}const Sr={enabled:!1,files:{},add:function(r,e){this.enabled!==!1&&(this.files[r]=e)},get:function(r){if(this.enabled!==!1)return this.files[r]},remove:function(r){delete this.files[r]},clear:function(){this.files={}}};class GP{constructor(e,t,n){const i=this;let s=!1,a=0,l=0,u;const h=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(f){l++,s===!1&&i.onStart!==void 0&&i.onStart(f,a,l),s=!0},this.itemEnd=function(f){a++,i.onProgress!==void 0&&i.onProgress(f,a,l),a===l&&(s=!1,i.onLoad!==void 0&&i.onLoad())},this.itemError=function(f){i.onError!==void 0&&i.onError(f)},this.resolveURL=function(f){return u?u(f):f},this.setURLModifier=function(f){return u=f,this},this.addHandler=function(f,p){return h.push(f,p),this},this.removeHandler=function(f){const p=h.indexOf(f);return p!==-1&&h.splice(p,2),this},this.getHandler=function(f){for(let p=0,m=h.length;p<m;p+=2){const g=h[p],x=h[p+1];if(g.global&&(g.lastIndex=0),g.test(f))return x}return null}}}const WP=new GP;class ds{constructor(e){this.manager=e!==void 0?e:WP,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(i,s){n.load(e,i,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}ds.DEFAULT_MATERIAL_NAME="__DEFAULT";const Zi={};class jP extends Error{constructor(e,t){super(e),this.response=t}}class Rd extends ds{constructor(e){super(e)}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=Sr.get(e);if(s!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(s),this.manager.itemEnd(e)},0),s;if(Zi[e]!==void 0){Zi[e].push({onLoad:t,onProgress:n,onError:i});return}Zi[e]=[],Zi[e].push({onLoad:t,onProgress:n,onError:i});const a=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),l=this.mimeType,u=this.responseType;fetch(a).then(h=>{if(h.status===200||h.status===0){if(h.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||h.body===void 0||h.body.getReader===void 0)return h;const f=Zi[e],p=h.body.getReader(),m=h.headers.get("X-File-Size")||h.headers.get("Content-Length"),g=m?parseInt(m):0,x=g!==0;let E=0;const v=new ReadableStream({start(_){R();function R(){p.read().then(({done:w,value:S})=>{if(w)_.close();else{E+=S.byteLength;const k=new ProgressEvent("progress",{lengthComputable:x,loaded:E,total:g});for(let N=0,O=f.length;N<O;N++){const H=f[N];H.onProgress&&H.onProgress(k)}_.enqueue(S),R()}},w=>{_.error(w)})}}});return new Response(v)}else throw new jP(`fetch for "${h.url}" responded with ${h.status}: ${h.statusText}`,h)}).then(h=>{switch(u){case"arraybuffer":return h.arrayBuffer();case"blob":return h.blob();case"document":return h.text().then(f=>new DOMParser().parseFromString(f,l));case"json":return h.json();default:if(l===void 0)return h.text();{const p=/charset="?([^;"\s]*)"?/i.exec(l),m=p&&p[1]?p[1].toLowerCase():void 0,g=new TextDecoder(m);return h.arrayBuffer().then(x=>g.decode(x))}}}).then(h=>{Sr.add(e,h);const f=Zi[e];delete Zi[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onLoad&&g.onLoad(h)}}).catch(h=>{const f=Zi[e];if(f===void 0)throw this.manager.itemError(e),h;delete Zi[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onError&&g.onError(h)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class XP extends ds{constructor(e){super(e)}load(e,t,n,i){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=Sr.get(e);if(a!==void 0)return s.manager.itemStart(e),setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a;const l=ia("img");function u(){f(),Sr.add(e,this),t&&t(this),s.manager.itemEnd(e)}function h(p){f(),i&&i(p),s.manager.itemError(e),s.manager.itemEnd(e)}function f(){l.removeEventListener("load",u,!1),l.removeEventListener("error",h,!1)}return l.addEventListener("load",u,!1),l.addEventListener("error",h,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(l.crossOrigin=this.crossOrigin),s.manager.itemStart(e),l.src=e,l}}class qP extends ds{constructor(e){super(e)}load(e,t,n,i){const s=new Pn,a=new XP(this.manager);return a.setCrossOrigin(this.crossOrigin),a.setPath(this.path),a.load(e,function(l){s.image=l,s.needsUpdate=!0,t!==void 0&&t(s)},n,i),s}}class jl extends an{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new pt(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const th=new St,Hm=new F,Vm=new F;class Pd{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new vt(512,512),this.map=null,this.mapPass=null,this.matrix=new St,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new bd,this._frameExtents=new vt(1,1),this._viewportCount=1,this._viewports=[new Gt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;Hm.setFromMatrixPosition(e.matrixWorld),t.position.copy(Hm),Vm.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Vm),t.updateMatrixWorld(),th.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(th),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(th)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class YP extends Pd{constructor(){super(new jn(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=ro*2*e.angle*this.focus,i=this.mapSize.width/this.mapSize.height,s=e.distance||t.far;(n!==t.fov||i!==t.aspect||s!==t.far)&&(t.fov=n,t.aspect=i,t.far=s,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class KP extends jl{constructor(e,t,n=0,i=Math.PI/3,s=0,a=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(an.DEFAULT_UP),this.updateMatrix(),this.target=new an,this.distance=n,this.angle=i,this.penumbra=s,this.decay=a,this.map=null,this.shadow=new YP}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const Gm=new St,Ho=new F,nh=new F;class $P extends Pd{constructor(){super(new jn(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new vt(4,2),this._viewportCount=6,this._viewports=[new Gt(2,1,1,1),new Gt(0,1,1,1),new Gt(3,1,1,1),new Gt(1,1,1,1),new Gt(3,0,1,1),new Gt(1,0,1,1)],this._cubeDirections=[new F(1,0,0),new F(-1,0,0),new F(0,0,1),new F(0,0,-1),new F(0,1,0),new F(0,-1,0)],this._cubeUps=[new F(0,1,0),new F(0,1,0),new F(0,1,0),new F(0,1,0),new F(0,0,1),new F(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,i=this.matrix,s=e.distance||n.far;s!==n.far&&(n.far=s,n.updateProjectionMatrix()),Ho.setFromMatrixPosition(e.matrixWorld),n.position.copy(Ho),nh.copy(n.position),nh.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(nh),n.updateMatrixWorld(),i.makeTranslation(-Ho.x,-Ho.y,-Ho.z),Gm.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Gm)}}class $g extends jl{constructor(e,t,n=0,i=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=i,this.shadow=new $P}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class ZP extends Pd{constructor(){super(new Sd(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Il extends jl{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(an.DEFAULT_UP),this.updateMatrix(),this.target=new an,this.shadow=new ZP}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class QP extends jl{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}class Jo{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,i=e.length;n<i;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class JP extends ds{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=Sr.get(e);if(a!==void 0){if(s.manager.itemStart(e),a.then){a.then(h=>{t&&t(h),s.manager.itemEnd(e)}).catch(h=>{i&&i(h)});return}return setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a}const l={};l.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",l.headers=this.requestHeader;const u=fetch(e,l).then(function(h){return h.blob()}).then(function(h){return createImageBitmap(h,Object.assign(s.options,{colorSpaceConversion:"none"}))}).then(function(h){return Sr.add(e,h),t&&t(h),s.manager.itemEnd(e),h}).catch(function(h){i&&i(h),Sr.remove(e),s.manager.itemError(e),s.manager.itemEnd(e)});Sr.add(e,u),s.manager.itemStart(e)}}class eC{constructor(e=!0){this.autoStart=e,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=Wm(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let e=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const t=Wm();e=(t-this.oldTime)/1e3,this.oldTime=t,this.elapsedTime+=e}return e}}function Wm(){return performance.now()}class tC{constructor(e,t,n){this.binding=e,this.valueSize=n;let i,s,a;switch(t){case"quaternion":i=this._slerp,s=this._slerpAdditive,a=this._setAdditiveIdentityQuaternion,this.buffer=new Float64Array(n*6),this._workIndex=5;break;case"string":case"bool":i=this._select,s=this._select,a=this._setAdditiveIdentityOther,this.buffer=new Array(n*5);break;default:i=this._lerp,s=this._lerpAdditive,a=this._setAdditiveIdentityNumeric,this.buffer=new Float64Array(n*5)}this._mixBufferRegion=i,this._mixBufferRegionAdditive=s,this._setIdentity=a,this._origIndex=3,this._addIndex=4,this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,this.useCount=0,this.referenceCount=0}accumulate(e,t){const n=this.buffer,i=this.valueSize,s=e*i+i;let a=this.cumulativeWeight;if(a===0){for(let l=0;l!==i;++l)n[s+l]=n[l];a=t}else{a+=t;const l=t/a;this._mixBufferRegion(n,s,0,l,i)}this.cumulativeWeight=a}accumulateAdditive(e){const t=this.buffer,n=this.valueSize,i=n*this._addIndex;this.cumulativeWeightAdditive===0&&this._setIdentity(),this._mixBufferRegionAdditive(t,i,0,e,n),this.cumulativeWeightAdditive+=e}apply(e){const t=this.valueSize,n=this.buffer,i=e*t+t,s=this.cumulativeWeight,a=this.cumulativeWeightAdditive,l=this.binding;if(this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,s<1){const u=t*this._origIndex;this._mixBufferRegion(n,i,u,1-s,t)}a>0&&this._mixBufferRegionAdditive(n,i,this._addIndex*t,1,t);for(let u=t,h=t+t;u!==h;++u)if(n[u]!==n[u+t]){l.setValue(n,i);break}}saveOriginalState(){const e=this.binding,t=this.buffer,n=this.valueSize,i=n*this._origIndex;e.getValue(t,i);for(let s=n,a=i;s!==a;++s)t[s]=t[i+s%n];this._setIdentity(),this.cumulativeWeight=0,this.cumulativeWeightAdditive=0}restoreOriginalState(){const e=this.valueSize*3;this.binding.setValue(this.buffer,e)}_setAdditiveIdentityNumeric(){const e=this._addIndex*this.valueSize,t=e+this.valueSize;for(let n=e;n<t;n++)this.buffer[n]=0}_setAdditiveIdentityQuaternion(){this._setAdditiveIdentityNumeric(),this.buffer[this._addIndex*this.valueSize+3]=1}_setAdditiveIdentityOther(){const e=this._origIndex*this.valueSize,t=this._addIndex*this.valueSize;for(let n=0;n<this.valueSize;n++)this.buffer[t+n]=this.buffer[e+n]}_select(e,t,n,i,s){if(i>=.5)for(let a=0;a!==s;++a)e[t+a]=e[n+a]}_slerp(e,t,n,i){Dt.slerpFlat(e,t,e,t,e,n,i)}_slerpAdditive(e,t,n,i,s){const a=this._workIndex*s;Dt.multiplyQuaternionsFlat(e,a,e,t,e,n),Dt.slerpFlat(e,t,e,t,e,a,i)}_lerp(e,t,n,i,s){const a=1-i;for(let l=0;l!==s;++l){const u=t+l;e[u]=e[u]*a+e[n+l]*i}}_lerpAdditive(e,t,n,i,s){for(let a=0;a!==s;++a){const l=t+a;e[l]=e[l]+e[n+a]*i}}}const Cd="\\[\\]\\.:\\/",nC=new RegExp("["+Cd+"]","g"),Dd="[^"+Cd+"]",iC="[^"+Cd.replace("\\.","")+"]",rC=/((?:WC+[\/:])*)/.source.replace("WC",Dd),sC=/(WCOD+)?/.source.replace("WCOD",iC),oC=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Dd),aC=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Dd),lC=new RegExp("^"+rC+sC+oC+aC+"$"),cC=["material","materials","bones","map"];class uC{constructor(e,t,n){const i=n||Xt.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,i)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,i=this._bindings[n];i!==void 0&&i.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let i=this._targetGroup.nCachedObjects_,s=n.length;i!==s;++i)n[i].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class Xt{constructor(e,t,n){this.path=t,this.parsedPath=n||Xt.parseTrackName(t),this.node=Xt.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new Xt.Composite(e,t,n):new Xt(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(nC,"")}static parseTrackName(e){const t=lC.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},i=n.nodeName&&n.nodeName.lastIndexOf(".");if(i!==void 0&&i!==-1){const s=n.nodeName.substring(i+1);cC.indexOf(s)!==-1&&(n.nodeName=n.nodeName.substring(0,i),n.objectName=s)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(s){for(let a=0;a<s.length;a++){const l=s[a];if(l.name===t||l.uuid===t)return l;const u=n(l.children);if(u)return u}return null},i=n(e.children);if(i)return i}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)e[t++]=n[i]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,i=t.propertyName;let s=t.propertyIndex;if(e||(e=Xt.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let h=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let f=0;f<e.length;f++)if(e[f].name===h){h=f;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(h!==void 0){if(e[h]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[h]}}const a=e[i];if(a===void 0){const h=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+h+"."+i+" but it wasn't found.",e);return}let l=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?l=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(l=this.Versioning.MatrixWorldNeedsUpdate);let u=this.BindingType.Direct;if(s!==void 0){if(i==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[s]!==void 0&&(s=e.morphTargetDictionary[s])}u=this.BindingType.ArrayElement,this.resolvedProperty=a,this.propertyIndex=s}else a.fromArray!==void 0&&a.toArray!==void 0?(u=this.BindingType.HasFromToArray,this.resolvedProperty=a):Array.isArray(a)?(u=this.BindingType.EntireArray,this.resolvedProperty=a):this.propertyName=i;this.getValue=this.GetterByBindingType[u],this.setValue=this.SetterByBindingTypeAndVersioning[u][l]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}Xt.Composite=uC;Xt.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};Xt.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};Xt.prototype.GetterByBindingType=[Xt.prototype._getValue_direct,Xt.prototype._getValue_array,Xt.prototype._getValue_arrayElement,Xt.prototype._getValue_toArray];Xt.prototype.SetterByBindingTypeAndVersioning=[[Xt.prototype._setValue_direct,Xt.prototype._setValue_direct_setNeedsUpdate,Xt.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[Xt.prototype._setValue_array,Xt.prototype._setValue_array_setNeedsUpdate,Xt.prototype._setValue_array_setMatrixWorldNeedsUpdate],[Xt.prototype._setValue_arrayElement,Xt.prototype._setValue_arrayElement_setNeedsUpdate,Xt.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[Xt.prototype._setValue_fromArray,Xt.prototype._setValue_fromArray_setNeedsUpdate,Xt.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];class hC{constructor(e,t,n=null,i=t.blendMode){this._mixer=e,this._clip=t,this._localRoot=n,this.blendMode=i;const s=t.tracks,a=s.length,l=new Array(a),u={endingStart:Vs,endingEnd:Vs};for(let h=0;h!==a;++h){const f=s[h].createInterpolant(null);l[h]=f,f.settings=u}this._interpolantSettings=u,this._interpolants=l,this._propertyBindings=new Array(a),this._cacheIndex=null,this._byClipCacheIndex=null,this._timeScaleInterpolant=null,this._weightInterpolant=null,this.loop=_d,this._loopCount=-1,this._startTime=null,this.time=0,this.timeScale=1,this._effectiveTimeScale=1,this.weight=1,this._effectiveWeight=1,this.repetitions=1/0,this.paused=!1,this.enabled=!0,this.clampWhenFinished=!1,this.zeroSlopeAtStart=!0,this.zeroSlopeAtEnd=!0}play(){return this._mixer._activateAction(this),this}stop(){return this._mixer._deactivateAction(this),this.reset()}reset(){return this.paused=!1,this.enabled=!0,this.time=0,this._loopCount=-1,this._startTime=null,this.stopFading().stopWarping()}isRunning(){return this.enabled&&!this.paused&&this.timeScale!==0&&this._startTime===null&&this._mixer._isActiveAction(this)}isScheduled(){return this._mixer._isActiveAction(this)}startAt(e){return this._startTime=e,this}setLoop(e,t){return this.loop=e,this.repetitions=t,this}setEffectiveWeight(e){return this.weight=e,this._effectiveWeight=this.enabled?e:0,this.stopFading()}getEffectiveWeight(){return this._effectiveWeight}fadeIn(e){return this._scheduleFading(e,0,1)}fadeOut(e){return this._scheduleFading(e,1,0)}crossFadeFrom(e,t,n){if(e.fadeOut(t),this.fadeIn(t),n){const i=this._clip.duration,s=e._clip.duration,a=s/i,l=i/s;e.warp(1,a,t),this.warp(l,1,t)}return this}crossFadeTo(e,t,n){return e.crossFadeFrom(this,t,n)}stopFading(){const e=this._weightInterpolant;return e!==null&&(this._weightInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}setEffectiveTimeScale(e){return this.timeScale=e,this._effectiveTimeScale=this.paused?0:e,this.stopWarping()}getEffectiveTimeScale(){return this._effectiveTimeScale}setDuration(e){return this.timeScale=this._clip.duration/e,this.stopWarping()}syncWith(e){return this.time=e.time,this.timeScale=e.timeScale,this.stopWarping()}halt(e){return this.warp(this._effectiveTimeScale,0,e)}warp(e,t,n){const i=this._mixer,s=i.time,a=this.timeScale;let l=this._timeScaleInterpolant;l===null&&(l=i._lendControlInterpolant(),this._timeScaleInterpolant=l);const u=l.parameterPositions,h=l.sampleValues;return u[0]=s,u[1]=s+n,h[0]=e/a,h[1]=t/a,this}stopWarping(){const e=this._timeScaleInterpolant;return e!==null&&(this._timeScaleInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}getMixer(){return this._mixer}getClip(){return this._clip}getRoot(){return this._localRoot||this._mixer._root}_update(e,t,n,i){if(!this.enabled){this._updateWeight(e);return}const s=this._startTime;if(s!==null){const u=(e-s)*n;u<0||n===0?t=0:(this._startTime=null,t=n*u)}t*=this._updateTimeScale(e);const a=this._updateTime(t),l=this._updateWeight(e);if(l>0){const u=this._interpolants,h=this._propertyBindings;switch(this.blendMode){case HM:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulateAdditive(l);break;case vd:default:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulate(i,l)}}}_updateWeight(e){let t=0;if(this.enabled){t=this.weight;const n=this._weightInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopFading(),i===0&&(this.enabled=!1))}}return this._effectiveWeight=t,t}_updateTimeScale(e){let t=0;if(!this.paused){t=this.timeScale;const n=this._timeScaleInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopWarping(),t===0?this.paused=!0:this.timeScale=t)}}return this._effectiveTimeScale=t,t}_updateTime(e){const t=this._clip.duration,n=this.loop;let i=this.time+e,s=this._loopCount;const a=n===zM;if(e===0)return s===-1?i:a&&(s&1)===1?t-i:i;if(n===kM){s===-1&&(this._loopCount=0,this._setEndings(!0,!0,!1));e:{if(i>=t)i=t;else if(i<0)i=0;else{this.time=i;break e}this.clampWhenFinished?this.paused=!0:this.enabled=!1,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e<0?-1:1})}}else{if(s===-1&&(e>=0?(s=0,this._setEndings(!0,this.repetitions===0,a)):this._setEndings(this.repetitions===0,!0,a)),i>=t||i<0){const l=Math.floor(i/t);i-=t*l,s+=Math.abs(l);const u=this.repetitions-s;if(u<=0)this.clampWhenFinished?this.paused=!0:this.enabled=!1,i=e>0?t:0,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e>0?1:-1});else{if(u===1){const h=e<0;this._setEndings(h,!h,a)}else this._setEndings(!1,!1,a);this._loopCount=s,this.time=i,this._mixer.dispatchEvent({type:"loop",action:this,loopDelta:l})}}else this.time=i;if(a&&(s&1)===1)return t-i}return i}_setEndings(e,t,n){const i=this._interpolantSettings;n?(i.endingStart=Gs,i.endingEnd=Gs):(e?i.endingStart=this.zeroSlopeAtStart?Gs:Vs:i.endingStart=Nl,t?i.endingEnd=this.zeroSlopeAtEnd?Gs:Vs:i.endingEnd=Nl)}_scheduleFading(e,t,n){const i=this._mixer,s=i.time;let a=this._weightInterpolant;a===null&&(a=i._lendControlInterpolant(),this._weightInterpolant=a);const l=a.parameterPositions,u=a.sampleValues;return l[0]=s,u[0]=t,l[1]=s+e,u[1]=n,this}}const dC=new Float32Array(1);class Zg extends Rr{constructor(e){super(),this._root=e,this._initMemoryManager(),this._accuIndex=0,this.time=0,this.timeScale=1}_bindAction(e,t){const n=e._localRoot||this._root,i=e._clip.tracks,s=i.length,a=e._propertyBindings,l=e._interpolants,u=n.uuid,h=this._bindingsByRootAndName;let f=h[u];f===void 0&&(f={},h[u]=f);for(let p=0;p!==s;++p){const m=i[p],g=m.name;let x=f[g];if(x!==void 0)++x.referenceCount,a[p]=x;else{if(x=a[p],x!==void 0){x._cacheIndex===null&&(++x.referenceCount,this._addInactiveBinding(x,u,g));continue}const E=t&&t._propertyBindings[p].binding.parsedPath;x=new tC(Xt.create(n,g,E),m.ValueTypeName,m.getValueSize()),++x.referenceCount,this._addInactiveBinding(x,u,g),a[p]=x}l[p].resultBuffer=x.buffer}}_activateAction(e){if(!this._isActiveAction(e)){if(e._cacheIndex===null){const n=(e._localRoot||this._root).uuid,i=e._clip.uuid,s=this._actionsByClip[i];this._bindAction(e,s&&s.knownActions[0]),this._addInactiveAction(e,i,n)}const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];s.useCount++===0&&(this._lendBinding(s),s.saveOriginalState())}this._lendAction(e)}}_deactivateAction(e){if(this._isActiveAction(e)){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.useCount===0&&(s.restoreOriginalState(),this._takeBackBinding(s))}this._takeBackAction(e)}}_initMemoryManager(){this._actions=[],this._nActiveActions=0,this._actionsByClip={},this._bindings=[],this._nActiveBindings=0,this._bindingsByRootAndName={},this._controlInterpolants=[],this._nActiveControlInterpolants=0;const e=this;this.stats={actions:{get total(){return e._actions.length},get inUse(){return e._nActiveActions}},bindings:{get total(){return e._bindings.length},get inUse(){return e._nActiveBindings}},controlInterpolants:{get total(){return e._controlInterpolants.length},get inUse(){return e._nActiveControlInterpolants}}}}_isActiveAction(e){const t=e._cacheIndex;return t!==null&&t<this._nActiveActions}_addInactiveAction(e,t,n){const i=this._actions,s=this._actionsByClip;let a=s[t];if(a===void 0)a={knownActions:[e],actionByRoot:{}},e._byClipCacheIndex=0,s[t]=a;else{const l=a.knownActions;e._byClipCacheIndex=l.length,l.push(e)}e._cacheIndex=i.length,i.push(e),a.actionByRoot[n]=e}_removeInactiveAction(e){const t=this._actions,n=t[t.length-1],i=e._cacheIndex;n._cacheIndex=i,t[i]=n,t.pop(),e._cacheIndex=null;const s=e._clip.uuid,a=this._actionsByClip,l=a[s],u=l.knownActions,h=u[u.length-1],f=e._byClipCacheIndex;h._byClipCacheIndex=f,u[f]=h,u.pop(),e._byClipCacheIndex=null;const p=l.actionByRoot,m=(e._localRoot||this._root).uuid;delete p[m],u.length===0&&delete a[s],this._removeInactiveBindingsForAction(e)}_removeInactiveBindingsForAction(e){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.referenceCount===0&&this._removeInactiveBinding(s)}}_lendAction(e){const t=this._actions,n=e._cacheIndex,i=this._nActiveActions++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackAction(e){const t=this._actions,n=e._cacheIndex,i=--this._nActiveActions,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_addInactiveBinding(e,t,n){const i=this._bindingsByRootAndName,s=this._bindings;let a=i[t];a===void 0&&(a={},i[t]=a),a[n]=e,e._cacheIndex=s.length,s.push(e)}_removeInactiveBinding(e){const t=this._bindings,n=e.binding,i=n.rootNode.uuid,s=n.path,a=this._bindingsByRootAndName,l=a[i],u=t[t.length-1],h=e._cacheIndex;u._cacheIndex=h,t[h]=u,t.pop(),delete l[s],Object.keys(l).length===0&&delete a[i]}_lendBinding(e){const t=this._bindings,n=e._cacheIndex,i=this._nActiveBindings++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackBinding(e){const t=this._bindings,n=e._cacheIndex,i=--this._nActiveBindings,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_lendControlInterpolant(){const e=this._controlInterpolants,t=this._nActiveControlInterpolants++;let n=e[t];return n===void 0&&(n=new Yg(new Float32Array(2),new Float32Array(2),1,dC),n.__cacheIndex=t,e[t]=n),n}_takeBackControlInterpolant(e){const t=this._controlInterpolants,n=e.__cacheIndex,i=--this._nActiveControlInterpolants,s=t[i];e.__cacheIndex=i,t[i]=e,s.__cacheIndex=n,t[n]=s}clipAction(e,t,n){const i=t||this._root,s=i.uuid;let a=typeof e=="string"?ao.findByName(i,e):e;const l=a!==null?a.uuid:e,u=this._actionsByClip[l];let h=null;if(n===void 0&&(a!==null?n=a.blendMode:n=vd),u!==void 0){const p=u.actionByRoot[s];if(p!==void 0&&p.blendMode===n)return p;h=u.knownActions[0],a===null&&(a=h._clip)}if(a===null)return null;const f=new hC(this,a,t,n);return this._bindAction(f,h),this._addInactiveAction(f,l,s),f}existingAction(e,t){const n=t||this._root,i=n.uuid,s=typeof e=="string"?ao.findByName(n,e):e,a=s?s.uuid:e,l=this._actionsByClip[a];return l!==void 0&&l.actionByRoot[i]||null}stopAllAction(){const e=this._actions,t=this._nActiveActions;for(let n=t-1;n>=0;--n)e[n].stop();return this}update(e){e*=this.timeScale;const t=this._actions,n=this._nActiveActions,i=this.time+=e,s=Math.sign(e),a=this._accuIndex^=1;for(let h=0;h!==n;++h)t[h]._update(i,e,s,a);const l=this._bindings,u=this._nActiveBindings;for(let h=0;h!==u;++h)l[h].apply(a);return this}setTime(e){this.time=0;for(let t=0;t<this._actions.length;t++)this._actions[t].time=0;return this.update(e)}getRoot(){return this._root}uncacheClip(e){const t=this._actions,n=e.uuid,i=this._actionsByClip,s=i[n];if(s!==void 0){const a=s.knownActions;for(let l=0,u=a.length;l!==u;++l){const h=a[l];this._deactivateAction(h);const f=h._cacheIndex,p=t[t.length-1];h._cacheIndex=null,h._byClipCacheIndex=null,p._cacheIndex=f,t[f]=p,t.pop(),this._removeInactiveBindingsForAction(h)}delete i[n]}}uncacheRoot(e){const t=e.uuid,n=this._actionsByClip;for(const a in n){const l=n[a].actionByRoot,u=l[t];u!==void 0&&(this._deactivateAction(u),this._removeInactiveAction(u))}const i=this._bindingsByRootAndName,s=i[t];if(s!==void 0)for(const a in s){const l=s[a];l.restoreOriginalState(),this._removeInactiveBinding(l)}}uncacheAction(e,t){const n=this.existingAction(e,t);n!==null&&(this._deactivateAction(n),this._removeInactiveAction(n))}}const jm=new St;class Qg{constructor(e,t,n=0,i=1/0){this.ray=new co(e,t),this.near=n,this.far=i,this.camera=null,this.layers=new xd,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return jm.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(jm),this}intersectObject(e,t=!0,n=[]){return sd(e,this,n,t),n.sort(Xm),n}intersectObjects(e,t=!0,n=[]){for(let i=0,s=e.length;i<s;i++)sd(e[i],this,n,t);return n.sort(Xm),n}}function Xm(r,e){return r.distance-e.distance}function sd(r,e,t,n){let i=!0;if(r.layers.test(e.layers)&&r.raycast(e,t)===!1&&(i=!1),i===!0&&n===!0){const s=r.children;for(let a=0,l=s.length;a<l;a++)sd(s[a],e,t,!0)}}class qm{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Fn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}const gr=new F,yl=new St,ih=new St;class Jg extends jg{constructor(e){const t=e_(e),n=new Sn,i=[],s=[],a=new pt(0,0,1),l=new pt(0,1,0);for(let h=0;h<t.length;h++){const f=t[h];f.parent&&f.parent.isBone&&(i.push(0,0,0),i.push(0,0,0),s.push(a.r,a.g,a.b),s.push(l.r,l.g,l.b))}n.setAttribute("position",new Wt(i,3)),n.setAttribute("color",new Wt(s,3));const u=new Wl({vertexColors:!0,depthTest:!1,depthWrite:!1,toneMapped:!1,transparent:!0});super(n,u),this.isSkeletonHelper=!0,this.type="SkeletonHelper",this.root=e,this.bones=t,this.matrix=e.matrixWorld,this.matrixAutoUpdate=!1}updateMatrixWorld(e){const t=this.bones,n=this.geometry,i=n.getAttribute("position");ih.copy(this.root.matrixWorld).invert();for(let s=0,a=0;s<t.length;s++){const l=t[s];l.parent&&l.parent.isBone&&(yl.multiplyMatrices(ih,l.matrixWorld),gr.setFromMatrixPosition(yl),i.setXYZ(a,gr.x,gr.y,gr.z),yl.multiplyMatrices(ih,l.parent.matrixWorld),gr.setFromMatrixPosition(yl),i.setXYZ(a+1,gr.x,gr.y,gr.z),a+=2)}n.getAttribute("position").needsUpdate=!0,super.updateMatrixWorld(e)}dispose(){this.geometry.dispose(),this.material.dispose()}}function e_(r){const e=[];r.isBone===!0&&e.push(r);for(let t=0;t<r.children.length;t++)e.push.apply(e,e_(r.children[t]));return e}class t_ extends Rr{constructor(e,t=null){super(),this.object=e,this.domElement=t,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(){}disconnect(){}dispose(){}update(){}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:"170"}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__="170");class n_ extends ds{constructor(e){super(e),this.animateBonePositions=!0,this.animateBoneRotations=!0}load(e,t,n,i){const s=this,a=new Rd(s.manager);a.setPath(s.path),a.setRequestHeader(s.requestHeader),a.setWithCredentials(s.withCredentials),a.load(e,function(l){try{t(s.parse(l))}catch(u){i?i(u):console.error(u),s.manager.itemError(e)}},n,i)}parse(e){function t(g){l(g)!=="HIERARCHY"&&console.error("THREE.BVHLoader: HIERARCHY expected.");const x=[],E=i(g,l(g),x);l(g)!=="MOTION"&&console.error("THREE.BVHLoader: MOTION expected.");let v=l(g).split(/[\s]+/);const _=parseInt(v[1]);isNaN(_)&&console.error("THREE.BVHLoader: Failed to read number of frames."),v=l(g).split(/[\s]+/);const R=parseFloat(v[2]);isNaN(R)&&console.error("THREE.BVHLoader: Failed to read frame time.");for(let w=0;w<_;w++)v=l(g).split(/[\s]+/),n(v,w*R,E);return x}function n(g,x,E){if(E.type==="ENDSITE")return;const v={time:x,position:new F,rotation:new Dt};E.frames.push(v);const _=new Dt,R=new F(1,0,0),w=new F(0,1,0),S=new F(0,0,1);for(let k=0;k<E.channels.length;k++)switch(E.channels[k]){case"Xposition":v.position.x=parseFloat(g.shift().trim());break;case"Yposition":v.position.y=parseFloat(g.shift().trim());break;case"Zposition":v.position.z=parseFloat(g.shift().trim());break;case"Xrotation":_.setFromAxisAngle(R,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Yrotation":_.setFromAxisAngle(w,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Zrotation":_.setFromAxisAngle(S,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;default:console.warn("THREE.BVHLoader: Invalid channel type.")}for(let k=0;k<E.children.length;k++)n(g,x,E.children[k])}function i(g,x,E){const v={name:"",type:"",frames:[]};E.push(v);let _=x.split(/[\s]+/);_[0].toUpperCase()==="END"&&_[1].toUpperCase()==="SITE"?(v.type="ENDSITE",v.name="ENDSITE"):(v.name=_[1],v.type=_[0].toUpperCase()),l(g)!=="{"&&console.error("THREE.BVHLoader: Expected opening { after type & name"),_=l(g).split(/[\s]+/),_[0]!=="OFFSET"&&console.error("THREE.BVHLoader: Expected OFFSET but got: "+_[0]),_.length!==4&&console.error("THREE.BVHLoader: Invalid number of values for OFFSET.");const R=new F(parseFloat(_[1]),parseFloat(_[2]),parseFloat(_[3]));if((isNaN(R.x)||isNaN(R.y)||isNaN(R.z))&&console.error("THREE.BVHLoader: Invalid values of OFFSET."),v.offset=R,v.type!=="ENDSITE"){_=l(g).split(/[\s]+/),_[0]!=="CHANNELS"&&console.error("THREE.BVHLoader: Expected CHANNELS definition.");const w=parseInt(_[1]);v.channels=_.splice(2,w),v.children=[]}for(;;){const w=l(g);if(w==="}")return v;v.children.push(i(g,w,E))}}function s(g,x){const E=new Gl;if(x.push(E),E.position.add(g.offset),E.name=g.name,g.type!=="ENDSITE")for(let v=0;v<g.children.length;v++)E.add(s(g.children[v],x));return E}function a(g){const x=[];for(let E=0;E<g.length;E++){const v=g[E];if(v.type==="ENDSITE")continue;const _=[],R=[],w=[];for(let S=0;S<v.frames.length;S++){const k=v.frames[S];_.push(k.time),R.push(k.position.x+v.offset.x),R.push(k.position.y+v.offset.y),R.push(k.position.z+v.offset.z),w.push(k.rotation.x),w.push(k.rotation.y),w.push(k.rotation.z),w.push(k.rotation.w)}u.animateBonePositions&&x.push(new Ar(v.name+".position",_,R)),u.animateBoneRotations&&x.push(new wr(v.name+".quaternion",_,w))}return new ao("animation",-1,x)}function l(g){let x;for(;(x=g.shift().trim()).length===0;);return x}const u=this,h=e.split(/[\r\n]+/g),f=t(h),p=[];s(f[0],p);const m=a(f);return{skeleton:new sa(p),clip:m}}}var Di=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},rh={},Ym;function xn(){return Ym||(Ym=1,(function(r){var e=Object.defineProperty,t=Object.defineProperties,n=Object.getOwnPropertyDescriptors,i=Object.getOwnPropertySymbols,s=Object.prototype.hasOwnProperty,a=Object.prototype.propertyIsEnumerable,l=(b,I,G)=>I in b?e(b,I,{enumerable:!0,configurable:!0,writable:!0,value:G}):b[I]=G,u=(b,I)=>{for(var G in I||(I={}))s.call(I,G)&&l(b,G,I[G]);if(i)for(var G of i(I))a.call(I,G)&&l(b,G,I[G]);return b},h=(b,I)=>t(b,n(I)),f=b=>e(b,"__esModule",{value:!0}),p=(b,I)=>{f(b);for(var G in I)e(b,G,{get:I[G],enumerable:!0})};p(r,{Atom:()=>Ta,PointerProxy:()=>Lc,Ticker:()=>Aa,getPointerParts:()=>Ir,isPointer:()=>ki,isPrism:()=>vs,iterateAndCountTicks:()=>Cc,iterateOver:()=>Ic,pointer:()=>_o,pointerToPrism:()=>xs,prism:()=>Or,val:()=>Eo});var m=Array.isArray,g=m,x=typeof Di=="object"&&Di&&Di.Object===Object&&Di,E=x,v=typeof self=="object"&&self&&self.Object===Object&&self,_=E||v||Function("return this")(),R=_,w=R.Symbol,S=w,k=Object.prototype,N=k.hasOwnProperty,O=k.toString,H=S?S.toStringTag:void 0;function D(b){var I=N.call(b,H),G=b[H];try{b[H]=void 0;var re=!0}catch{}var _t=O.call(b);return re&&(I?b[H]=G:delete b[H]),_t}var A=D,z=Object.prototype,Z=z.toString;function $(b){return Z.call(b)}var ie=$,ae="[object Null]",X="[object Undefined]",he=S?S.toStringTag:void 0;function te(b){return b==null?b===void 0?X:ae:he&&he in Object(b)?A(b):ie(b)}var ye=te;function Ee(b){return b!=null&&typeof b=="object"}var ke=Ee,Xe="[object Symbol]";function Tt(b){return typeof b=="symbol"||ke(b)&&ye(b)==Xe}var ce=Tt,ge=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,Be=/^\w*$/;function Me(b,I){if(g(b))return!1;var G=typeof b;return G=="number"||G=="symbol"||G=="boolean"||b==null||ce(b)?!0:Be.test(b)||!ge.test(b)||I!=null&&b in Object(I)}var ot=Me;function ut(b){var I=typeof b;return b!=null&&(I=="object"||I=="function")}var Ke=ut,de="[object AsyncFunction]",be="[object Function]",Oe="[object GeneratorFunction]",V="[object Proxy]";function ct(b){if(!Ke(b))return!1;var I=ye(b);return I==be||I==Oe||I==de||I==V}var it=ct,tt=R["__core-js_shared__"],ze=tt,dt=(function(){var b=/[^.]+$/.exec(ze&&ze.keys&&ze.keys.IE_PROTO||"");return b?"Symbol(src)_1."+b:""})();function Ve(b){return!!dt&&dt in b}var L=Ve,T=Function.prototype,K=T.toString;function ue(b){if(b!=null){try{return K.call(b)}catch{}try{return b+""}catch{}}return""}var me=ue,le=/[\\^$.*+?()[\]{}|]/g,Le=/^\[object .+?Constructor\]$/,Ae=Function.prototype,He=Object.prototype,Pt=Ae.toString,_e=He.hasOwnProperty,Ce=RegExp("^"+Pt.call(_e).replace(le,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function Ge(b){if(!Ke(b)||L(b))return!1;var I=it(b)?Ce:Le;return I.test(me(b))}var ft=Ge;function We(b,I){return b==null?void 0:b[I]}var At=We;function mt(b,I){var G=At(b,I);return ft(G)?G:void 0}var Ot=mt,W=Ot(Object,"create"),Re=W;function oe(){this.__data__=Re?Re(null):{},this.size=0}var pe=oe;function Fe(b){var I=this.has(b)&&delete this.__data__[b];return this.size-=I?1:0,I}var De=Fe,bt="__lodash_hash_undefined__",Zt=Object.prototype,un=Zt.hasOwnProperty;function U(b){var I=this.__data__;if(Re){var G=I[b];return G===bt?void 0:G}return un.call(I,b)?I[b]:void 0}var ne=U,fe=Object.prototype,ve=fe.hasOwnProperty;function Je(b){var I=this.__data__;return Re?I[b]!==void 0:ve.call(I,b)}var Te=Je,qe="__lodash_hash_undefined__";function at(b,I){var G=this.__data__;return this.size+=this.has(b)?0:1,G[b]=Re&&I===void 0?qe:I,this}var ht=at;function yt(b){var I=-1,G=b==null?0:b.length;for(this.clear();++I<G;){var re=b[I];this.set(re[0],re[1])}}yt.prototype.clear=pe,yt.prototype.delete=De,yt.prototype.get=ne,yt.prototype.has=Te,yt.prototype.set=ht;var Et=yt;function je(){this.__data__=[],this.size=0}var nt=je;function rt(b,I){return b===I||b!==b&&I!==I}var Ut=rt;function Lt(b,I){for(var G=b.length;G--;)if(Ut(b[G][0],I))return G;return-1}var st=Lt,P=Array.prototype,j=P.splice;function J(b){var I=this.__data__,G=st(I,b);if(G<0)return!1;var re=I.length-1;return G==re?I.pop():j.call(I,G,1),--this.size,!0}var ee=J;function q(b){var I=this.__data__,G=st(I,b);return G<0?void 0:I[G][1]}var we=q;function Ue(b){return st(this.__data__,b)>-1}var $e=Ue;function Ze(b,I){var G=this.__data__,re=st(G,b);return re<0?(++this.size,G.push([b,I])):G[re][1]=I,this}var xt=Ze;function gt(b){var I=-1,G=b==null?0:b.length;for(this.clear();++I<G;){var re=b[I];this.set(re[0],re[1])}}gt.prototype.clear=nt,gt.prototype.delete=ee,gt.prototype.get=we,gt.prototype.has=$e,gt.prototype.set=xt;var Qe=gt,Bt=Ot(R,"Map"),jt=Bt;function qt(){this.size=0,this.__data__={hash:new Et,map:new(jt||Qe),string:new Et}}var hn=qt;function kt(b){var I=typeof b;return I=="string"||I=="number"||I=="symbol"||I=="boolean"?b!=="__proto__":b===null}var et=kt;function ei(b,I){var G=b.__data__;return et(I)?G[typeof I=="string"?"string":"hash"]:G.map}var Ft=ei;function Cn(b){var I=Ft(this,b).delete(b);return this.size-=I?1:0,I}var Ai=Cn;function mn(b){return Ft(this,b).get(b)}var Ui=mn;function Yt(b){return Ft(this,b).has(b)}var Yn=Yt;function Bi(b,I){var G=Ft(this,b),re=G.size;return G.set(b,I),this.size+=G.size==re?0:1,this}var Nn=Bi;function Dn(b){var I=-1,G=b==null?0:b.length;for(this.clear();++I<G;){var re=b[I];this.set(re[0],re[1])}}Dn.prototype.clear=hn,Dn.prototype.delete=Ai,Dn.prototype.get=Ui,Dn.prototype.has=Yn,Dn.prototype.set=Nn;var ti=Dn,fs="Expected a function";function mo(b,I){if(typeof b!="function"||I!=null&&typeof I!="function")throw new TypeError(fs);var G=function(){var re=arguments,_t=I?I.apply(this,re):re[0],Ht=G.cache;if(Ht.has(_t))return Ht.get(_t);var In=b.apply(this,re);return G.cache=Ht.set(_t,In)||Ht,In};return G.cache=new(mo.Cache||ti),G}mo.Cache=ti;var Xl=mo,sr=500;function ps(b){var I=Xl(b,function(re){return G.size===sr&&G.clear(),re}),G=I.cache;return I}var ql=ps,Pr=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,Yl=/\\(\\)?/g,Kl=ql(function(b){var I=[];return b.charCodeAt(0)===46&&I.push(""),b.replace(Pr,function(G,re,_t,Ht){I.push(_t?Ht.replace(Yl,"$1"):re||G)}),I}),$l=Kl;function Zl(b,I){for(var G=-1,re=b==null?0:b.length,_t=Array(re);++G<re;)_t[G]=I(b[G],G,b);return _t}var Ql=Zl,Cr=S?S.prototype:void 0,la=Cr?Cr.toString:void 0;function ca(b){if(typeof b=="string")return b;if(g(b))return Ql(b,ca)+"";if(ce(b))return la?la.call(b):"";var I=b+"";return I=="0"&&1/b==-1/0?"-0":I}var Jl=ca;function ec(b){return b==null?"":Jl(b)}var tc=ec;function nc(b,I){return g(b)?b:ot(b,I)?[b]:$l(tc(b))}var ic=nc;function rc(b){if(typeof b=="string"||ce(b))return b;var I=b+"";return I=="0"&&1/b==-1/0?"-0":I}var or=rc;function ms(b,I){I=ic(I,b);for(var G=0,re=I.length;b!=null&&G<re;)b=b[or(I[G++])];return G&&G==re?b:void 0}var sc=ms;function go(b,I,G){var re=b==null?void 0:sc(b,I);return re===void 0?G:re}var oc=go;function ac(b,I){return function(G){return b(I(G))}}var lc=ac,cc=lc(Object.getPrototypeOf,Object),uc=cc,hc="[object Object]",dc=Function.prototype,fc=Object.prototype,ua=dc.toString,pc=fc.hasOwnProperty,ha=ua.call(Object);function da(b){if(!ke(b)||ye(b)!=hc)return!1;var I=uc(b);if(I===null)return!0;var G=pc.call(I,"constructor")&&I.constructor;return typeof G=="function"&&G instanceof G&&ua.call(G)==ha}var fa=da;function pa(b){var I=b==null?0:b.length;return I?b[I-1]:void 0}var mc=pa,gs=new WeakMap,ma=new WeakMap,Dr=Symbol("pointerMeta"),gc={get(b,I){if(I===Dr)return gs.get(b);let G=ma.get(b);G||(G=new Map,ma.set(b,G));const re=G.get(I);if(re!==void 0)return re;const _t=gs.get(b),Ht=_s({root:_t.root,path:[..._t.path,I]});return G.set(I,Ht),Ht}},gi=b=>b[Dr],Ir=b=>{const{root:I,path:G}=gi(b);return{root:I,path:G}};function _s(b){var I;const G={root:b.root,path:(I=b.path)!=null?I:[]},re={};return gs.set(re,G),new Proxy(re,gc)}var _o=_s,ki=b=>b&&!!gi(b);function ga(b,I,G){return I.length===0?G(b):ar(b,I,G)}var ar=(b,I,G)=>{if(I.length===0)return G(b);if(Array.isArray(b)){let[re,..._t]=I;re=parseInt(String(re),10),isNaN(re)&&(re=0);const Ht=b[re],In=ar(Ht,_t,G);if(Ht===In)return b;const ui=[...b];return ui.splice(re,1,In),ui}else if(typeof b=="object"&&b!==null){const[re,..._t]=I,Ht=b[re],In=ar(Ht,_t,G);return Ht===In?b:h(u({},b),{[re]:In})}else{const[re,..._t]=I;return{[re]:ar(void 0,_t,G)}}},vn=class{constructor(){this._head=void 0}peek(){return this._head&&this._head.data}pop(){const b=this._head;if(b)return this._head=b.next,b.data}push(b){const I={next:this._head,data:b};this._head=I}};function vs(b){return!!(b&&b.isPrism&&b.isPrism===!0)}function vo(){const b=()=>{},I=new vn,G=b;return{type:"Dataverse_discoveryMechanism",startIgnoringDependencies:()=>{I.push(G)},stopIgnoringDependencies:()=>{I.peek()!==G||I.pop()},reportResolutionStart:lr=>{const Ur=I.peek();Ur&&Ur(lr),I.push(G)},reportResolutionEnd:lr=>{I.pop()},pushCollector:lr=>{I.push(lr)},popCollector:lr=>{if(I.peek()!==lr)throw new Error("Popped collector is not on top of the stack");I.pop()}}}function _c(){const b="__dataverse_discoveryMechanism_sharedStack",I=typeof window<"u"?window:typeof Di<"u"?Di:{};if(I){const G=I[b];if(G&&typeof G=="object"&&G.type==="Dataverse_discoveryMechanism")return G;{const re=vo();return I[b]=re,re}}else return vo()}var{startIgnoringDependencies:zi,stopIgnoringDependencies:Lr,reportResolutionEnd:vc,reportResolutionStart:yc,pushCollector:yo,popCollector:xc}=_c(),_a=()=>{},bc=class{constructor(b,I){this._fn=b,this._prismInstance=I,this._didMarkDependentsAsStale=!1,this._isFresh=!1,this._cacheOfDendencyValues=new Map,this._dependents=new Set,this._dependencies=new Set,this._possiblyStaleDeps=new Set,this._scope=new va(this),this._lastValue=void 0,this._forciblySetToStale=!1,this._reactToDependencyGoingStale=G=>{this._possiblyStaleDeps.add(G),this._markAsStale()};for(const G of this._dependencies)G._addDependent(this._reactToDependencyGoingStale);zi(),this.getValue(),Lr()}get hasDependents(){return this._dependents.size>0}removeDependent(b){this._dependents.delete(b)}addDependent(b){this._dependents.add(b)}destroy(){for(const b of this._dependencies)b._removeDependent(this._reactToDependencyGoingStale);ya(this._scope)}getValue(){if(!this._isFresh){const b=this._recalculate();this._lastValue=b,this._isFresh=!0,this._didMarkDependentsAsStale=!1,this._forciblySetToStale=!1}return this._lastValue}_recalculate(){let b;if(!this._forciblySetToStale&&this._possiblyStaleDeps.size>0){let re=!1;zi();for(const _t of this._possiblyStaleDeps)if(this._cacheOfDendencyValues.get(_t)!==_t.getValue()){re=!0;break}if(Lr(),this._possiblyStaleDeps.clear(),!re)return this._lastValue}const I=new Set;this._cacheOfDendencyValues.clear();const G=re=>{I.add(re),this._addDependency(re)};yo(G),Tn.push(this._scope);try{b=this._fn()}catch(re){console.error(re)}finally{Tn.pop()!==this._scope&&console.warn("The Prism hook stack has slipped. This is a bug.")}xc(G);for(const re of this._dependencies)I.has(re)||this._removeDependency(re);this._dependencies=I,zi();for(const re of I)this._cacheOfDendencyValues.set(re,re.getValue());return Lr(),b}forceStale(){this._forciblySetToStale=!0,this._markAsStale()}_markAsStale(){if(!this._didMarkDependentsAsStale){this._didMarkDependentsAsStale=!0,this._isFresh=!1;for(const b of this._dependents)b(this._prismInstance)}}_addDependency(b){this._dependencies.has(b)||(this._dependencies.add(b),b._addDependent(this._reactToDependencyGoingStale))}_removeDependency(b){this._dependencies.has(b)&&(this._dependencies.delete(b),b._removeDependent(this._reactToDependencyGoingStale))}},xo={},Sc=class{constructor(b){this._fn=b,this.isPrism=!0,this._state={hot:!1,handle:void 0}}get isHot(){return this._state.hot}onChange(b,I,G=!1){const re=()=>{b.onThisOrNextTick(Ht)};let _t=xo;const Ht=()=>{const ui=this.getValue();ui!==_t&&(_t=ui,I(ui))};return this._addDependent(re),G&&(_t=this.getValue(),I(_t)),()=>{this._removeDependent(re),b.offThisOrNextTick(Ht),b.offNextTick(Ht)}}onStale(b){const I=()=>{this._removeDependent(G)},G=()=>b();return this._addDependent(G),I}keepHot(){return this.onStale(()=>{})}_addDependent(b){this._state.hot||this._goHot(),this._state.handle.addDependent(b)}_goHot(){const b=new bc(this._fn,this);this._state={hot:!0,handle:b}}_removeDependent(b){const I=this._state;if(!I.hot)return;const G=I.handle;G.removeDependent(b),G.hasDependents||(this._state={hot:!1,handle:void 0},G.destroy())}getValue(){yc(this);const b=this._state;let I;return b.hot?I=b.handle.getValue():I=Nr(this._fn),vc(this),I}},va=class{constructor(b){this._hotHandle=b,this._refs=new Map,this.isPrismScope=!0,this.subs={},this.effects=new Map,this.memos=new Map}ref(b,I){let G=this._refs.get(b);if(G!==void 0)return G;{const re={current:I};return this._refs.set(b,re),re}}effect(b,I,G){let re=this.effects.get(b);re===void 0&&(re={cleanup:_a,deps:void 0},this.effects.set(b,re)),xa(re.deps,G)&&(re.cleanup(),zi(),re.cleanup=ys(I,_a).value,Lr(),re.deps=G)}memo(b,I,G){let re=this.memos.get(b);return re===void 0&&(re={cachedValue:null,deps:void 0},this.memos.set(b,re)),xa(re.deps,G)&&(zi(),re.cachedValue=ys(I,void 0).value,Lr(),re.deps=G),re.cachedValue}state(b,I){const{value:G,setValue:re}=this.memo("state/"+b,()=>{const _t={current:I};return{value:_t,setValue:In=>{_t.current=In,this._hotHandle.forceStale()}}},[]);return[G.current,re]}sub(b){return this.subs[b]||(this.subs[b]=new va(this._hotHandle)),this.subs[b]}cleanupEffects(){for(const b of this.effects.values())ys(b.cleanup,void 0);this.effects.clear()}source(b,I){return this.effect("$$source/blah",()=>b(()=>{this._hotHandle.forceStale()}),[b]),I()}};function ya(b){for(const I of Object.values(b.subs))ya(I);b.cleanupEffects()}function ys(b,I){try{return{value:b(),ok:!0}}catch(G){return setTimeout(function(){throw G}),{value:I,ok:!1}}}var Tn=new vn;function Ec(b,I){const G=Tn.peek();if(!G)throw new Error("prism.ref() is called outside of a prism() call.");return G.ref(b,I)}function bo(b,I,G){const re=Tn.peek();if(!re)throw new Error("prism.effect() is called outside of a prism() call.");return re.effect(b,I,G)}function xa(b,I){if(b===void 0||I===void 0)return!0;const G=b.length;if(G!==I.length)return!0;for(let re=0;re<G;re++)if(b[re]!==I[re])return!0;return!1}function ba(b,I,G){const re=Tn.peek();if(!re)throw new Error("prism.memo() is called outside of a prism() call.");return re.memo(b,I,G)}function Vn(b,I){const G=Tn.peek();if(!G)throw new Error("prism.state() is called outside of a prism() call.");return G.state(b,I)}function Mc(){if(!Tn.peek())throw new Error("The parent function is called outside of a prism() call.")}function Tc(b,I){const G=Tn.peek();if(!G)throw new Error("prism.scope() is called outside of a prism() call.");const re=G.sub(b);Tn.push(re);const _t=ys(I,void 0).value;return Tn.pop(),_t}function wc(b,I,G){return ba(b,()=>yn(I),G).getValue()}function Sa(){return!!Tn.peek()}function Ac(b,I){const G=Tn.peek();if(!G)throw new Error("prism.source() is called outside of a prism() call.");return G.source(b,I)}var yn=b=>new Sc(b),Fr=class{effect(b,I,G){console.warn("prism.effect() does not run in cold prisms")}memo(b,I,G){return I()}state(b,I){return[I,()=>{}]}ref(b,I){return{current:I}}sub(b){return new Fr}source(b,I){return I()}};function Nr(b){const I=new Fr;Tn.push(I);let G;try{G=b()}catch(re){console.error(re)}finally{Tn.pop()!==I&&console.warn("The Prism hook stack has slipped. This is a bug.")}return G}yn.ref=Ec,yn.effect=bo,yn.memo=ba,yn.ensurePrism=Mc,yn.state=Vn,yn.scope=Tc,yn.sub=wc,yn.inPrism=Sa,yn.source=Ac;var Or=yn,Ea;(function(b){b[b.Dict=0]="Dict",b[b.Array=1]="Array",b[b.Other=2]="Other"})(Ea||(Ea={}));var Kt=b=>Array.isArray(b)?1:fa(b)?0:2,So=(b,I,G=Kt(b))=>G===0&&typeof I=="string"||G===1&&Rc(I)?b[I]:void 0,Rc=b=>{const I=typeof b=="number"?b:parseInt(b,10);return!isNaN(I)&&I>=0&&I<1/0&&(I|0)===I},Ma=class{constructor(b,I){this._parent=b,this._path=I,this.children=new Map,this.identityChangeListeners=new Set}addIdentityChangeListener(b){this.identityChangeListeners.add(b)}removeIdentityChangeListener(b){this.identityChangeListeners.delete(b),this._checkForGC()}removeChild(b){this.children.delete(b),this._checkForGC()}getChild(b){return this.children.get(b)}getOrCreateChild(b){let I=this.children.get(b);return I||(I=I=new Ma(this,this._path.concat([b])),this.children.set(b,I)),I}_checkForGC(){this.identityChangeListeners.size>0||this.children.size>0||this._parent&&this._parent.removeChild(mc(this._path))}},Ta=class{constructor(b){this.$$isPointerToPrismProvider=!0,this.pointer=_o({root:this,path:[]}),this.prism=this.pointerToPrism(this.pointer),this._onPointerValueChange=(I,G)=>{const{path:re}=Ir(I),_t=this._getOrCreateScopeForPath(re);return _t.identityChangeListeners.add(G),()=>{_t.identityChangeListeners.delete(G)}},this._currentState=b,this._rootScope=new Ma(void 0,[])}set(b){const I=this._currentState;this._currentState=b,this._checkUpdates(this._rootScope,I,b)}get(){return this._currentState}getByPointer(b){const I=ki(b)?b:b(this.pointer),G=Ir(I).path;return this._getIn(G)}_getIn(b){return b.length===0?this.get():oc(this.get(),b)}reduce(b){this.set(b(this.get()))}reduceByPointer(b,I){const G=ki(b)?b:b(this.pointer),re=Ir(G).path,_t=ga(this.get(),re,I);this.set(_t)}setByPointer(b,I){this.reduceByPointer(b,()=>I)}_checkUpdates(b,I,G){if(I===G)return;for(const Ht of b.identityChangeListeners)Ht(G);if(b.children.size===0)return;const re=Kt(I),_t=Kt(G);if(!(re===2&&re===_t))for(const[Ht,In]of b.children){const ui=So(I,Ht,re),Ra=So(G,Ht,_t);this._checkUpdates(In,ui,Ra)}}_getOrCreateScopeForPath(b){let I=this._rootScope;for(const G of b)I=I.getOrCreateChild(G);return I}pointerToPrism(b){const{path:I}=Ir(b),G=_t=>this._onPointerValueChange(b,_t),re=()=>this._getIn(I);return Or(()=>Or.source(G,re))}},wa=new WeakMap;function Pc(b){return typeof b=="object"&&b!==null&&b.$$isPointerToPrismProvider===!0}var xs=b=>{const I=gi(b);let G=wa.get(I);if(!G){const re=I.root;if(!Pc(re))throw new Error("Cannot run pointerToPrism() on a pointer whose root is not an PointerToPrismProvider");G=re.pointerToPrism(b),wa.set(I,G)}return G},Eo=b=>ki(b)?xs(b).getValue():vs(b)?b.getValue():b;function*Cc(b){let I;if(ki(b))I=xs(b);else if(vs(b))I=b;else throw new Error("Only pointers and prisms are supported");let G=0;const re=I.onStale(()=>{G++});try{for(;;){const _t=G;G=0,yield{value:I.getValue(),ticks:_t}}}finally{re()}}var Dc=180,Aa=class{constructor(b){this._conf=b,this._ticking=!1,this._dormant=!0,this._numberOfDormantTicks=0,this.__ticks=0,this._scheduledForThisOrNextTick=new Set,this._scheduledForNextTick=new Set,this._timeAtCurrentTick=0}get dormant(){return this._dormant}onThisOrNextTick(b){this._scheduledForThisOrNextTick.add(b),this._dormant&&this._goActive()}onNextTick(b){this._scheduledForNextTick.add(b),this._dormant&&this._goActive()}offThisOrNextTick(b){this._scheduledForThisOrNextTick.delete(b)}offNextTick(b){this._scheduledForNextTick.delete(b)}get time(){return this._ticking?this._timeAtCurrentTick:performance.now()}_goActive(){var b,I;this._dormant&&(this._dormant=!1,(I=(b=this._conf)==null?void 0:b.onActive)==null||I.call(b))}_goDormant(){var b,I;this._dormant||(this._dormant=!0,this._numberOfDormantTicks=0,(I=(b=this._conf)==null?void 0:b.onDormant)==null||I.call(b))}tick(b=performance.now()){if(this.__ticks++,!this._dormant&&this._scheduledForNextTick.size===0&&this._scheduledForThisOrNextTick.size===0&&(this._numberOfDormantTicks++,this._numberOfDormantTicks>=Dc)){this._goDormant();return}this._ticking=!0,this._timeAtCurrentTick=b;for(const I of this._scheduledForNextTick)this._scheduledForThisOrNextTick.add(I);this._scheduledForNextTick.clear(),this._tick(0),this._ticking=!1}_tick(b){const I=this.time;if(b>10&&console.warn("_tick() recursing for 10 times"),b>100)throw new Error("Maximum recursion limit for _tick()");const G=this._scheduledForThisOrNextTick;this._scheduledForThisOrNextTick=new Set;for(const re of G)re(I);if(this._scheduledForThisOrNextTick.size>0)return this._tick(b+1)}};function*Ic(b){let I;if(ki(b))I=xs(b);else if(vs(b))I=b;else throw new Error("Only pointers and prisms are supported");const G=new Aa,re=I.onChange(G,_t=>{});try{for(;;)G.tick(),yield I.getValue()}finally{re()}}var Lc=class{constructor(b){this.$$isPointerToPrismProvider=!0,this._currentPointerBox=new Ta(b),this.pointer=_o({root:this,path:[]})}setPointer(b){this._currentPointerBox.set(b)}pointerToPrism(b){const{path:I}=gi(b);return Or(()=>{const G=this._currentPointerBox.prism.getValue(),re=I.reduce((_t,Ht)=>_t[Ht],G);return Eo(re)})}}})(rh)),rh}const Km={type:"change"},Id={type:"start"},i_={type:"end"},xl=new co,$m=new yr,fC=Math.cos(70*Rg.DEG2RAD),bn=new F,Zn=2*Math.PI,Jt={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},sh=1e-6;class pC extends t_{constructor(e,t=null){super(e,t),this.state=Jt.NONE,this.enabled=!0,this.target=new F,this.cursor=new F,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:Xs.ROTATE,MIDDLE:Xs.DOLLY,RIGHT:Xs.PAN},this.touches={ONE:Hs.ROTATE,TWO:Hs.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._domElementKeyEvents=null,this._lastPosition=new F,this._lastQuaternion=new Dt,this._lastTargetPosition=new F,this._quat=new Dt().setFromUnitVectors(e.up,new F(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new qm,this._sphericalDelta=new qm,this._scale=1,this._panOffset=new F,this._rotateStart=new vt,this._rotateEnd=new vt,this._rotateDelta=new vt,this._panStart=new vt,this._panEnd=new vt,this._panDelta=new vt,this._dollyStart=new vt,this._dollyEnd=new vt,this._dollyDelta=new vt,this._dollyDirection=new F,this._mouse=new vt,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=gC.bind(this),this._onPointerDown=mC.bind(this),this._onPointerUp=_C.bind(this),this._onContextMenu=MC.bind(this),this._onMouseWheel=xC.bind(this),this._onKeyDown=bC.bind(this),this._onTouchStart=SC.bind(this),this._onTouchMove=EC.bind(this),this._onMouseDown=vC.bind(this),this._onMouseMove=yC.bind(this),this._interceptControlDown=TC.bind(this),this._interceptControlUp=wC.bind(this),this.domElement!==null&&this.connect(),this.update()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointercancel",this._onPointerUp),this.domElement.addEventListener("contextmenu",this._onContextMenu),this.domElement.addEventListener("wheel",this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener("keydown",this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.removeEventListener("pointercancel",this._onPointerUp),this.domElement.removeEventListener("wheel",this._onMouseWheel),this.domElement.removeEventListener("contextmenu",this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener("keydown",this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction="auto"}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(e){e.addEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=e}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(Km),this.update(),this.state=Jt.NONE}update(e=null){const t=this.object.position;bn.copy(t).sub(this.target),bn.applyQuaternion(this._quat),this._spherical.setFromVector3(bn),this.autoRotate&&this.state===Jt.NONE&&this._rotateLeft(this._getAutoRotationAngle(e)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let n=this.minAzimuthAngle,i=this.maxAzimuthAngle;isFinite(n)&&isFinite(i)&&(n<-Math.PI?n+=Zn:n>Math.PI&&(n-=Zn),i<-Math.PI?i+=Zn:i>Math.PI&&(i-=Zn),n<=i?this._spherical.theta=Math.max(n,Math.min(i,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(n+i)/2?Math.max(n,this._spherical.theta):Math.min(i,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let s=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{const a=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),s=a!=this._spherical.radius}if(bn.setFromSpherical(this._spherical),bn.applyQuaternion(this._quatInverse),t.copy(this.target).add(bn),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let a=null;if(this.object.isPerspectiveCamera){const l=bn.length();a=this._clampDistance(l*this._scale);const u=l-a;this.object.position.addScaledVector(this._dollyDirection,u),this.object.updateMatrixWorld(),s=!!u}else if(this.object.isOrthographicCamera){const l=new F(this._mouse.x,this._mouse.y,0);l.unproject(this.object);const u=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),s=u!==this.object.zoom;const h=new F(this._mouse.x,this._mouse.y,0);h.unproject(this.object),this.object.position.sub(h).add(l),this.object.updateMatrixWorld(),a=bn.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),this.zoomToCursor=!1;a!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(a).add(this.object.position):(xl.origin.copy(this.object.position),xl.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(xl.direction))<fC?this.object.lookAt(this.target):($m.setFromNormalAndCoplanarPoint(this.object.up,this.target),xl.intersectPlane($m,this.target))))}else if(this.object.isOrthographicCamera){const a=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),a!==this.object.zoom&&(this.object.updateProjectionMatrix(),s=!0)}return this._scale=1,this._performCursorZoom=!1,s||this._lastPosition.distanceToSquared(this.object.position)>sh||8*(1-this._lastQuaternion.dot(this.object.quaternion))>sh||this._lastTargetPosition.distanceToSquared(this.target)>sh?(this.dispatchEvent(Km),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(e){return e!==null?Zn/60*this.autoRotateSpeed*e:Zn/60/60*this.autoRotateSpeed}_getZoomScale(e){const t=Math.abs(e*.01);return Math.pow(.95,this.zoomSpeed*t)}_rotateLeft(e){this._sphericalDelta.theta-=e}_rotateUp(e){this._sphericalDelta.phi-=e}_panLeft(e,t){bn.setFromMatrixColumn(t,0),bn.multiplyScalar(-e),this._panOffset.add(bn)}_panUp(e,t){this.screenSpacePanning===!0?bn.setFromMatrixColumn(t,1):(bn.setFromMatrixColumn(t,0),bn.crossVectors(this.object.up,bn)),bn.multiplyScalar(e),this._panOffset.add(bn)}_pan(e,t){const n=this.domElement;if(this.object.isPerspectiveCamera){const i=this.object.position;bn.copy(i).sub(this.target);let s=bn.length();s*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*e*s/n.clientHeight,this.object.matrix),this._panUp(2*t*s/n.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(e*(this.object.right-this.object.left)/this.object.zoom/n.clientWidth,this.object.matrix),this._panUp(t*(this.object.top-this.object.bottom)/this.object.zoom/n.clientHeight,this.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),this.enablePan=!1)}_dollyOut(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_dollyIn(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_updateZoomParameters(e,t){if(!this.zoomToCursor)return;this._performCursorZoom=!0;const n=this.domElement.getBoundingClientRect(),i=e-n.left,s=t-n.top,a=n.width,l=n.height;this._mouse.x=i/a*2-1,this._mouse.y=-(s/l)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(e){return Math.max(this.minDistance,Math.min(this.maxDistance,e))}_handleMouseDownRotate(e){this._rotateStart.set(e.clientX,e.clientY)}_handleMouseDownDolly(e){this._updateZoomParameters(e.clientX,e.clientX),this._dollyStart.set(e.clientX,e.clientY)}_handleMouseDownPan(e){this._panStart.set(e.clientX,e.clientY)}_handleMouseMoveRotate(e){this._rotateEnd.set(e.clientX,e.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Zn*this._rotateDelta.x/t.clientHeight),this._rotateUp(Zn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(e){this._dollyEnd.set(e.clientX,e.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(e){this._panEnd.set(e.clientX,e.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(e){this._updateZoomParameters(e.clientX,e.clientY),e.deltaY<0?this._dollyIn(this._getZoomScale(e.deltaY)):e.deltaY>0&&this._dollyOut(this._getZoomScale(e.deltaY)),this.update()}_handleKeyDown(e){let t=!1;switch(e.code){case this.keys.UP:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(Zn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,this.keyPanSpeed),t=!0;break;case this.keys.BOTTOM:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(-Zn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,-this.keyPanSpeed),t=!0;break;case this.keys.LEFT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(Zn*this.rotateSpeed/this.domElement.clientHeight):this._pan(this.keyPanSpeed,0),t=!0;break;case this.keys.RIGHT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(-Zn*this.rotateSpeed/this.domElement.clientHeight):this._pan(-this.keyPanSpeed,0),t=!0;break}t&&(e.preventDefault(),this.update())}_handleTouchStartRotate(e){if(this._pointers.length===1)this._rotateStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._rotateStart.set(n,i)}}_handleTouchStartPan(e){if(this._pointers.length===1)this._panStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panStart.set(n,i)}}_handleTouchStartDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyStart.set(0,s)}_handleTouchStartDollyPan(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enablePan&&this._handleTouchStartPan(e)}_handleTouchStartDollyRotate(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enableRotate&&this._handleTouchStartRotate(e)}_handleTouchMoveRotate(e){if(this._pointers.length==1)this._rotateEnd.set(e.pageX,e.pageY);else{const n=this._getSecondPointerPosition(e),i=.5*(e.pageX+n.x),s=.5*(e.pageY+n.y);this._rotateEnd.set(i,s)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Zn*this._rotateDelta.x/t.clientHeight),this._rotateUp(Zn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(e){if(this._pointers.length===1)this._panEnd.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panEnd.set(n,i)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyEnd.set(0,s),this._dollyDelta.set(0,Math.pow(this._dollyEnd.y/this._dollyStart.y,this.zoomSpeed)),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);const a=(e.pageX+t.x)*.5,l=(e.pageY+t.y)*.5;this._updateZoomParameters(a,l)}_handleTouchMoveDollyPan(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enablePan&&this._handleTouchMovePan(e)}_handleTouchMoveDollyRotate(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enableRotate&&this._handleTouchMoveRotate(e)}_addPointer(e){this._pointers.push(e.pointerId)}_removePointer(e){delete this._pointerPositions[e.pointerId];for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId){this._pointers.splice(t,1);return}}_isTrackingPointer(e){for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId)return!0;return!1}_trackPointer(e){let t=this._pointerPositions[e.pointerId];t===void 0&&(t=new vt,this._pointerPositions[e.pointerId]=t),t.set(e.pageX,e.pageY)}_getSecondPointerPosition(e){const t=e.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[t]}_customWheelEvent(e){const t=e.deltaMode,n={clientX:e.clientX,clientY:e.clientY,deltaY:e.deltaY};switch(t){case 1:n.deltaY*=16;break;case 2:n.deltaY*=100;break}return e.ctrlKey&&!this._controlActive&&(n.deltaY*=10),n}}function mC(r){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.domElement.addEventListener("pointerup",this._onPointerUp)),!this._isTrackingPointer(r)&&(this._addPointer(r),r.pointerType==="touch"?this._onTouchStart(r):this._onMouseDown(r)))}function gC(r){this.enabled!==!1&&(r.pointerType==="touch"?this._onTouchMove(r):this._onMouseMove(r))}function _C(r){switch(this._removePointer(r),this._pointers.length){case 0:this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.dispatchEvent(i_),this.state=Jt.NONE;break;case 1:const e=this._pointers[0],t=this._pointerPositions[e];this._onTouchStart({pointerId:e,pageX:t.x,pageY:t.y});break}}function vC(r){let e;switch(r.button){case 0:e=this.mouseButtons.LEFT;break;case 1:e=this.mouseButtons.MIDDLE;break;case 2:e=this.mouseButtons.RIGHT;break;default:e=-1}switch(e){case Xs.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(r),this.state=Jt.DOLLY;break;case Xs.ROTATE:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Jt.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Jt.ROTATE}break;case Xs.PAN:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Jt.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Jt.PAN}break;default:this.state=Jt.NONE}this.state!==Jt.NONE&&this.dispatchEvent(Id)}function yC(r){switch(this.state){case Jt.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(r);break;case Jt.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(r);break;case Jt.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(r);break}}function xC(r){this.enabled===!1||this.enableZoom===!1||this.state!==Jt.NONE||(r.preventDefault(),this.dispatchEvent(Id),this._handleMouseWheel(this._customWheelEvent(r)),this.dispatchEvent(i_))}function bC(r){this.enabled===!1||this.enablePan===!1||this._handleKeyDown(r)}function SC(r){switch(this._trackPointer(r),this._pointers.length){case 1:switch(this.touches.ONE){case Hs.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(r),this.state=Jt.TOUCH_ROTATE;break;case Hs.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(r),this.state=Jt.TOUCH_PAN;break;default:this.state=Jt.NONE}break;case 2:switch(this.touches.TWO){case Hs.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(r),this.state=Jt.TOUCH_DOLLY_PAN;break;case Hs.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(r),this.state=Jt.TOUCH_DOLLY_ROTATE;break;default:this.state=Jt.NONE}break;default:this.state=Jt.NONE}this.state!==Jt.NONE&&this.dispatchEvent(Id)}function EC(r){switch(this._trackPointer(r),this.state){case Jt.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(r),this.update();break;case Jt.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(r),this.update();break;case Jt.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(r),this.update();break;case Jt.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(r),this.update();break;default:this.state=Jt.NONE}}function MC(r){this.enabled!==!1&&r.preventDefault()}function TC(r){r.key==="Control"&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}function wC(r){r.key==="Control"&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}const ns=new Qg,Hn=new F,_r=new F,cn=new Dt,Zm={X:new F(1,0,0),Y:new F(0,1,0),Z:new F(0,0,1)},oh={type:"change"},Qm={type:"mouseDown",mode:null},Jm={type:"mouseUp",mode:null},eg={type:"objectChange"};class AC extends t_{constructor(e,t=null){super(void 0,t);const n=new LC(this);this._root=n;const i=new FC;this._gizmo=i,n.add(i);const s=new NC;this._plane=s,n.add(s);const a=this;function l(w,S){let k=S;Object.defineProperty(a,w,{get:function(){return k!==void 0?k:S},set:function(N){k!==N&&(k=N,s[w]=N,i[w]=N,a.dispatchEvent({type:w+"-changed",value:N}),a.dispatchEvent(oh))}}),a[w]=S,s[w]=S,i[w]=S}l("camera",e),l("object",void 0),l("enabled",!0),l("axis",null),l("mode","translate"),l("translationSnap",null),l("rotationSnap",null),l("scaleSnap",null),l("space","world"),l("size",1),l("dragging",!1),l("showX",!0),l("showY",!0),l("showZ",!0),l("minX",-1/0),l("maxX",1/0),l("minY",-1/0),l("maxY",1/0),l("minZ",-1/0),l("maxZ",1/0);const u=new F,h=new F,f=new Dt,p=new Dt,m=new F,g=new Dt,x=new F,E=new F,v=new F,_=0,R=new F;l("worldPosition",u),l("worldPositionStart",h),l("worldQuaternion",f),l("worldQuaternionStart",p),l("cameraPosition",m),l("cameraQuaternion",g),l("pointStart",x),l("pointEnd",E),l("rotationAxis",v),l("rotationAngle",_),l("eye",R),this._offset=new F,this._startNorm=new F,this._endNorm=new F,this._cameraScale=new F,this._parentPosition=new F,this._parentQuaternion=new Dt,this._parentQuaternionInv=new Dt,this._parentScale=new F,this._worldScaleStart=new F,this._worldQuaternionInv=new Dt,this._worldScale=new F,this._positionStart=new F,this._quaternionStart=new Dt,this._scaleStart=new F,this._getPointer=RC.bind(this),this._onPointerDown=CC.bind(this),this._onPointerHover=PC.bind(this),this._onPointerMove=DC.bind(this),this._onPointerUp=IC.bind(this),t!==null&&this.connect()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointermove",this._onPointerHover),this.domElement.addEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerHover),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="auto"}getHelper(){return this._root}pointerHover(e){if(this.object===void 0||this.dragging===!0)return;e!==null&&ns.setFromCamera(e,this.camera);const t=ah(this._gizmo.picker[this.mode],ns);t?this.axis=t.object.name:this.axis=null}pointerDown(e){if(!(this.object===void 0||this.dragging===!0||e!=null&&e.button!==0)&&this.axis!==null){e!==null&&ns.setFromCamera(e,this.camera);const t=ah(this._plane,ns,!0);t&&(this.object.updateMatrixWorld(),this.object.parent.updateMatrixWorld(),this._positionStart.copy(this.object.position),this._quaternionStart.copy(this.object.quaternion),this._scaleStart.copy(this.object.scale),this.object.matrixWorld.decompose(this.worldPositionStart,this.worldQuaternionStart,this._worldScaleStart),this.pointStart.copy(t.point).sub(this.worldPositionStart)),this.dragging=!0,Qm.mode=this.mode,this.dispatchEvent(Qm)}}pointerMove(e){const t=this.axis,n=this.mode,i=this.object;let s=this.space;if(n==="scale"?s="local":(t==="E"||t==="XYZE"||t==="XYZ")&&(s="world"),i===void 0||t===null||this.dragging===!1||e!==null&&e.button!==-1)return;e!==null&&ns.setFromCamera(e,this.camera);const a=ah(this._plane,ns,!0);if(a){if(this.pointEnd.copy(a.point).sub(this.worldPositionStart),n==="translate")this._offset.copy(this.pointEnd).sub(this.pointStart),s==="local"&&t!=="XYZ"&&this._offset.applyQuaternion(this._worldQuaternionInv),t.indexOf("X")===-1&&(this._offset.x=0),t.indexOf("Y")===-1&&(this._offset.y=0),t.indexOf("Z")===-1&&(this._offset.z=0),s==="local"&&t!=="XYZ"?this._offset.applyQuaternion(this._quaternionStart).divide(this._parentScale):this._offset.applyQuaternion(this._parentQuaternionInv).divide(this._parentScale),i.position.copy(this._offset).add(this._positionStart),this.translationSnap&&(s==="local"&&(i.position.applyQuaternion(cn.copy(this._quaternionStart).invert()),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.position.applyQuaternion(this._quaternionStart)),s==="world"&&(i.parent&&i.position.add(Hn.setFromMatrixPosition(i.parent.matrixWorld)),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.parent&&i.position.sub(Hn.setFromMatrixPosition(i.parent.matrixWorld)))),i.position.x=Math.max(this.minX,Math.min(this.maxX,i.position.x)),i.position.y=Math.max(this.minY,Math.min(this.maxY,i.position.y)),i.position.z=Math.max(this.minZ,Math.min(this.maxZ,i.position.z));else if(n==="scale"){if(t.search("XYZ")!==-1){let l=this.pointEnd.length()/this.pointStart.length();this.pointEnd.dot(this.pointStart)<0&&(l*=-1),_r.set(l,l,l)}else Hn.copy(this.pointStart),_r.copy(this.pointEnd),Hn.applyQuaternion(this._worldQuaternionInv),_r.applyQuaternion(this._worldQuaternionInv),_r.divide(Hn),t.search("X")===-1&&(_r.x=1),t.search("Y")===-1&&(_r.y=1),t.search("Z")===-1&&(_r.z=1);i.scale.copy(this._scaleStart).multiply(_r),this.scaleSnap&&(t.search("X")!==-1&&(i.scale.x=Math.round(i.scale.x/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Y")!==-1&&(i.scale.y=Math.round(i.scale.y/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Z")!==-1&&(i.scale.z=Math.round(i.scale.z/this.scaleSnap)*this.scaleSnap||this.scaleSnap))}else if(n==="rotate"){this._offset.copy(this.pointEnd).sub(this.pointStart);const l=20/this.worldPosition.distanceTo(Hn.setFromMatrixPosition(this.camera.matrixWorld));let u=!1;t==="XYZE"?(this.rotationAxis.copy(this._offset).cross(this.eye).normalize(),this.rotationAngle=this._offset.dot(Hn.copy(this.rotationAxis).cross(this.eye))*l):(t==="X"||t==="Y"||t==="Z")&&(this.rotationAxis.copy(Zm[t]),Hn.copy(Zm[t]),s==="local"&&Hn.applyQuaternion(this.worldQuaternion),Hn.cross(this.eye),Hn.length()===0?u=!0:this.rotationAngle=this._offset.dot(Hn.normalize())*l),(t==="E"||u)&&(this.rotationAxis.copy(this.eye),this.rotationAngle=this.pointEnd.angleTo(this.pointStart),this._startNorm.copy(this.pointStart).normalize(),this._endNorm.copy(this.pointEnd).normalize(),this.rotationAngle*=this._endNorm.cross(this._startNorm).dot(this.eye)<0?1:-1),this.rotationSnap&&(this.rotationAngle=Math.round(this.rotationAngle/this.rotationSnap)*this.rotationSnap),s==="local"&&t!=="E"&&t!=="XYZE"?(i.quaternion.copy(this._quaternionStart),i.quaternion.multiply(cn.setFromAxisAngle(this.rotationAxis,this.rotationAngle)).normalize()):(this.rotationAxis.applyQuaternion(this._parentQuaternionInv),i.quaternion.copy(cn.setFromAxisAngle(this.rotationAxis,this.rotationAngle)),i.quaternion.multiply(this._quaternionStart).normalize())}this.dispatchEvent(oh),this.dispatchEvent(eg)}}pointerUp(e){e!==null&&e.button!==0||(this.dragging&&this.axis!==null&&(Jm.mode=this.mode,this.dispatchEvent(Jm)),this.dragging=!1,this.axis=null)}dispose(){this.disconnect(),this._root.dispose()}attach(e){return this.object=e,this._root.visible=!0,this}detach(){return this.object=void 0,this.axis=null,this._root.visible=!1,this}reset(){this.enabled&&this.dragging&&(this.object.position.copy(this._positionStart),this.object.quaternion.copy(this._quaternionStart),this.object.scale.copy(this._scaleStart),this.dispatchEvent(oh),this.dispatchEvent(eg),this.pointStart.copy(this.pointEnd))}getRaycaster(){return ns}getMode(){return this.mode}setMode(e){this.mode=e}setTranslationSnap(e){this.translationSnap=e}setRotationSnap(e){this.rotationSnap=e}setScaleSnap(e){this.scaleSnap=e}setSize(e){this.size=e}setSpace(e){this.space=e}}function RC(r){if(this.domElement.ownerDocument.pointerLockElement)return{x:0,y:0,button:r.button};{const e=this.domElement.getBoundingClientRect();return{x:(r.clientX-e.left)/e.width*2-1,y:-(r.clientY-e.top)/e.height*2+1,button:r.button}}}function PC(r){if(this.enabled)switch(r.pointerType){case"mouse":case"pen":this.pointerHover(this._getPointer(r));break}}function CC(r){this.enabled&&(document.pointerLockElement||this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.pointerHover(this._getPointer(r)),this.pointerDown(this._getPointer(r)))}function DC(r){this.enabled&&this.pointerMove(this._getPointer(r))}function IC(r){this.enabled&&(this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.pointerUp(this._getPointer(r)))}function ah(r,e,t){const n=e.intersectObject(r,!0);for(let i=0;i<n.length;i++)if(n[i].object.visible||t)return n[i];return!1}const bl=new wi,tn=new F(0,1,0),tg=new F(0,0,0),ng=new St,Sl=new Dt,Ll=new Dt,Pi=new F,ig=new St,Yo=new F(1,0,0),ss=new F(0,1,0),Ko=new F(0,0,1),El=new F,Vo=new F,Go=new F;class LC extends an{constructor(e){super(),this.isTransformControlsRoot=!0,this.controls=e,this.visible=!1}updateMatrixWorld(e){const t=this.controls;t.object!==void 0&&(t.object.updateMatrixWorld(),t.object.parent===null?console.error("TransformControls: The attached 3D object must be a part of the scene graph."):t.object.parent.matrixWorld.decompose(t._parentPosition,t._parentQuaternion,t._parentScale),t.object.matrixWorld.decompose(t.worldPosition,t.worldQuaternion,t._worldScale),t._parentQuaternionInv.copy(t._parentQuaternion).invert(),t._worldQuaternionInv.copy(t.worldQuaternion).invert()),t.camera.updateMatrixWorld(),t.camera.matrixWorld.decompose(t.cameraPosition,t.cameraQuaternion,t._cameraScale),t.camera.isOrthographicCamera?t.camera.getWorldDirection(t.eye).negate():t.eye.copy(t.cameraPosition).sub(t.worldPosition).normalize(),super.updateMatrixWorld(e)}dispose(){this.traverse(function(e){e.geometry&&e.geometry.dispose(),e.material&&e.material.dispose()})}}class FC extends an{constructor(){super(),this.isTransformControlsGizmo=!0,this.type="TransformControlsGizmo";const e=new mi({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),t=new Wl({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),n=e.clone();n.opacity=.15;const i=t.clone();i.opacity=.5;const s=e.clone();s.color.setHex(16711680);const a=e.clone();a.color.setHex(65280);const l=e.clone();l.color.setHex(255);const u=e.clone();u.color.setHex(16711680),u.opacity=.5;const h=e.clone();h.color.setHex(65280),h.opacity=.5;const f=e.clone();f.color.setHex(255),f.opacity=.5;const p=e.clone();p.opacity=.25;const m=e.clone();m.color.setHex(16776960),m.opacity=.25,e.clone().color.setHex(16776960);const x=e.clone();x.color.setHex(7895160);const E=new Ln(0,.04,.1,12);E.translate(0,.05,0);const v=new dn(.08,.08,.08);v.translate(0,.04,0);const _=new Sn;_.setAttribute("position",new Wt([0,0,0,1,0,0],3));const R=new Ln(.0075,.0075,.5,3);R.translate(0,.25,0);function w(ae,X){const he=new ls(ae,.0075,3,64,X*Math.PI*2);return he.rotateY(Math.PI/2),he.rotateX(Math.PI/2),he}function S(){const ae=new Sn;return ae.setAttribute("position",new Wt([0,0,0,1,1,1],3)),ae}const k={X:[[new Pe(E,s),[.5,0,0],[0,0,-Math.PI/2]],[new Pe(E,s),[-.5,0,0],[0,0,Math.PI/2]],[new Pe(R,s),[0,0,0],[0,0,-Math.PI/2]]],Y:[[new Pe(E,a),[0,.5,0]],[new Pe(E,a),[0,-.5,0],[Math.PI,0,0]],[new Pe(R,a)]],Z:[[new Pe(E,l),[0,0,.5],[Math.PI/2,0,0]],[new Pe(E,l),[0,0,-.5],[-Math.PI/2,0,0]],[new Pe(R,l),null,[Math.PI/2,0,0]]],XYZ:[[new Pe(new js(.1,0),p.clone()),[0,0,0]]],XY:[[new Pe(new dn(.15,.15,.01),f.clone()),[.15,.15,0]]],YZ:[[new Pe(new dn(.15,.15,.01),u.clone()),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Pe(new dn(.15,.15,.01),h.clone()),[.15,0,.15],[-Math.PI/2,0,0]]]},N={X:[[new Pe(new Ln(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Pe(new Ln(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Pe(new Ln(.2,0,.6,4),n),[0,.3,0]],[new Pe(new Ln(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Pe(new Ln(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Pe(new Ln(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XYZ:[[new Pe(new js(.2,0),n)]],XY:[[new Pe(new dn(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Pe(new dn(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Pe(new dn(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]]},O={START:[[new Pe(new js(.01,2),i),null,null,null,"helper"]],END:[[new Pe(new js(.01,2),i),null,null,null,"helper"]],DELTA:[[new xi(S(),i),null,null,null,"helper"]],X:[[new xi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new xi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new xi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]},H={XYZE:[[new Pe(w(.5,1),x),null,[0,Math.PI/2,0]]],X:[[new Pe(w(.5,.5),s)]],Y:[[new Pe(w(.5,.5),a),null,[0,0,-Math.PI/2]]],Z:[[new Pe(w(.5,.5),l),null,[0,Math.PI/2,0]]],E:[[new Pe(w(.75,1),m),null,[0,Math.PI/2,0]]]},D={AXIS:[[new xi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]]},A={XYZE:[[new Pe(new oa(.25,10,8),n)]],X:[[new Pe(new ls(.5,.1,4,24),n),[0,0,0],[0,-Math.PI/2,-Math.PI/2]]],Y:[[new Pe(new ls(.5,.1,4,24),n),[0,0,0],[Math.PI/2,0,0]]],Z:[[new Pe(new ls(.5,.1,4,24),n),[0,0,0],[0,0,-Math.PI/2]]],E:[[new Pe(new ls(.75,.1,2,24),n)]]},z={X:[[new Pe(v,s),[.5,0,0],[0,0,-Math.PI/2]],[new Pe(R,s),[0,0,0],[0,0,-Math.PI/2]],[new Pe(v,s),[-.5,0,0],[0,0,Math.PI/2]]],Y:[[new Pe(v,a),[0,.5,0]],[new Pe(R,a)],[new Pe(v,a),[0,-.5,0],[0,0,Math.PI]]],Z:[[new Pe(v,l),[0,0,.5],[Math.PI/2,0,0]],[new Pe(R,l),[0,0,0],[Math.PI/2,0,0]],[new Pe(v,l),[0,0,-.5],[-Math.PI/2,0,0]]],XY:[[new Pe(new dn(.15,.15,.01),f),[.15,.15,0]]],YZ:[[new Pe(new dn(.15,.15,.01),u),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Pe(new dn(.15,.15,.01),h),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Pe(new dn(.1,.1,.1),p.clone())]]},Z={X:[[new Pe(new Ln(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Pe(new Ln(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Pe(new Ln(.2,0,.6,4),n),[0,.3,0]],[new Pe(new Ln(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Pe(new Ln(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Pe(new Ln(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XY:[[new Pe(new dn(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Pe(new dn(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Pe(new dn(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Pe(new dn(.2,.2,.2),n),[0,0,0]]]},$={X:[[new xi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new xi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new xi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]};function ie(ae){const X=new an;for(const he in ae)for(let te=ae[he].length;te--;){const ye=ae[he][te][0].clone(),Ee=ae[he][te][1],ke=ae[he][te][2],Xe=ae[he][te][3],Tt=ae[he][te][4];ye.name=he,ye.tag=Tt,Ee&&ye.position.set(Ee[0],Ee[1],Ee[2]),ke&&ye.rotation.set(ke[0],ke[1],ke[2]),Xe&&ye.scale.set(Xe[0],Xe[1],Xe[2]),ye.updateMatrix();const ce=ye.geometry.clone();ce.applyMatrix4(ye.matrix),ye.geometry=ce,ye.renderOrder=1/0,ye.position.set(0,0,0),ye.rotation.set(0,0,0),ye.scale.set(1,1,1),X.add(ye)}return X}this.gizmo={},this.picker={},this.helper={},this.add(this.gizmo.translate=ie(k)),this.add(this.gizmo.rotate=ie(H)),this.add(this.gizmo.scale=ie(z)),this.add(this.picker.translate=ie(N)),this.add(this.picker.rotate=ie(A)),this.add(this.picker.scale=ie(Z)),this.add(this.helper.translate=ie(O)),this.add(this.helper.rotate=ie(D)),this.add(this.helper.scale=ie($)),this.picker.translate.visible=!1,this.picker.rotate.visible=!1,this.picker.scale.visible=!1}updateMatrixWorld(e){const n=(this.mode==="scale"?"local":this.space)==="local"?this.worldQuaternion:Ll;this.gizmo.translate.visible=this.mode==="translate",this.gizmo.rotate.visible=this.mode==="rotate",this.gizmo.scale.visible=this.mode==="scale",this.helper.translate.visible=this.mode==="translate",this.helper.rotate.visible=this.mode==="rotate",this.helper.scale.visible=this.mode==="scale";let i=[];i=i.concat(this.picker[this.mode].children),i=i.concat(this.gizmo[this.mode].children),i=i.concat(this.helper[this.mode].children);for(let s=0;s<i.length;s++){const a=i[s];a.visible=!0,a.rotation.set(0,0,0),a.position.copy(this.worldPosition);let l;if(this.camera.isOrthographicCamera?l=(this.camera.top-this.camera.bottom)/this.camera.zoom:l=this.worldPosition.distanceTo(this.cameraPosition)*Math.min(1.9*Math.tan(Math.PI*this.camera.fov/360)/this.camera.zoom,7),a.scale.set(1,1,1).multiplyScalar(l*this.size/4),a.tag==="helper"){a.visible=!1,a.name==="AXIS"?(a.visible=!!this.axis,this.axis==="X"&&(cn.setFromEuler(bl.set(0,0,0)),a.quaternion.copy(n).multiply(cn),Math.abs(tn.copy(Yo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Y"&&(cn.setFromEuler(bl.set(0,0,Math.PI/2)),a.quaternion.copy(n).multiply(cn),Math.abs(tn.copy(ss).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Z"&&(cn.setFromEuler(bl.set(0,Math.PI/2,0)),a.quaternion.copy(n).multiply(cn),Math.abs(tn.copy(Ko).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="XYZE"&&(cn.setFromEuler(bl.set(0,Math.PI/2,0)),tn.copy(this.rotationAxis),a.quaternion.setFromRotationMatrix(ng.lookAt(tg,tn,ss)),a.quaternion.multiply(cn),a.visible=this.dragging),this.axis==="E"&&(a.visible=!1)):a.name==="START"?(a.position.copy(this.worldPositionStart),a.visible=this.dragging):a.name==="END"?(a.position.copy(this.worldPosition),a.visible=this.dragging):a.name==="DELTA"?(a.position.copy(this.worldPositionStart),a.quaternion.copy(this.worldQuaternionStart),Hn.set(1e-10,1e-10,1e-10).add(this.worldPositionStart).sub(this.worldPosition).multiplyScalar(-1),Hn.applyQuaternion(this.worldQuaternionStart.clone().invert()),a.scale.copy(Hn),a.visible=this.dragging):(a.quaternion.copy(n),this.dragging?a.position.copy(this.worldPositionStart):a.position.copy(this.worldPosition),this.axis&&(a.visible=this.axis.search(a.name)!==-1));continue}a.quaternion.copy(n),this.mode==="translate"||this.mode==="scale"?(a.name==="X"&&Math.abs(tn.copy(Yo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Y"&&Math.abs(tn.copy(ss).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Z"&&Math.abs(tn.copy(Ko).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XY"&&Math.abs(tn.copy(Ko).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="YZ"&&Math.abs(tn.copy(Yo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XZ"&&Math.abs(tn.copy(ss).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1)):this.mode==="rotate"&&(Sl.copy(n),tn.copy(this.eye).applyQuaternion(cn.copy(n).invert()),a.name.search("E")!==-1&&a.quaternion.setFromRotationMatrix(ng.lookAt(this.eye,tg,ss)),a.name==="X"&&(cn.setFromAxisAngle(Yo,Math.atan2(-tn.y,tn.z)),cn.multiplyQuaternions(Sl,cn),a.quaternion.copy(cn)),a.name==="Y"&&(cn.setFromAxisAngle(ss,Math.atan2(tn.x,tn.z)),cn.multiplyQuaternions(Sl,cn),a.quaternion.copy(cn)),a.name==="Z"&&(cn.setFromAxisAngle(Ko,Math.atan2(tn.y,tn.x)),cn.multiplyQuaternions(Sl,cn),a.quaternion.copy(cn))),a.visible=a.visible&&(a.name.indexOf("X")===-1||this.showX),a.visible=a.visible&&(a.name.indexOf("Y")===-1||this.showY),a.visible=a.visible&&(a.name.indexOf("Z")===-1||this.showZ),a.visible=a.visible&&(a.name.indexOf("E")===-1||this.showX&&this.showY&&this.showZ),a.material._color=a.material._color||a.material.color.clone(),a.material._opacity=a.material._opacity||a.material.opacity,a.material.color.copy(a.material._color),a.material.opacity=a.material._opacity,this.enabled&&this.axis&&(a.name===this.axis||this.axis.split("").some(function(u){return a.name===u}))&&(a.material.color.setHex(16776960),a.material.opacity=1)}super.updateMatrixWorld(e)}}class NC extends Pe{constructor(){super(new uo(1e5,1e5,2,2),new mi({visible:!1,wireframe:!0,side:Qn,transparent:!0,opacity:.1,toneMapped:!1})),this.isTransformControlsPlane=!0,this.type="TransformControlsPlane"}updateMatrixWorld(e){let t=this.space;switch(this.position.copy(this.worldPosition),this.mode==="scale"&&(t="local"),El.copy(Yo).applyQuaternion(t==="local"?this.worldQuaternion:Ll),Vo.copy(ss).applyQuaternion(t==="local"?this.worldQuaternion:Ll),Go.copy(Ko).applyQuaternion(t==="local"?this.worldQuaternion:Ll),tn.copy(Vo),this.mode){case"translate":case"scale":switch(this.axis){case"X":tn.copy(this.eye).cross(El),Pi.copy(El).cross(tn);break;case"Y":tn.copy(this.eye).cross(Vo),Pi.copy(Vo).cross(tn);break;case"Z":tn.copy(this.eye).cross(Go),Pi.copy(Go).cross(tn);break;case"XY":Pi.copy(Go);break;case"YZ":Pi.copy(El);break;case"XZ":tn.copy(Go),Pi.copy(Vo);break;case"XYZ":case"E":Pi.set(0,0,0);break}break;case"rotate":default:Pi.set(0,0,0)}Pi.length()===0?this.quaternion.copy(this.cameraQuaternion):(ig.lookAt(Hn.set(0,0,0),Pi,tn),this.quaternion.setFromRotationMatrix(ig)),super.updateMatrixWorld(e)}}function lh(r){const e=new Ii,t=new wd(.4,1,16),n=new mi({color:r,transparent:!0,opacity:1,side:Qn,depthTest:!1,depthWrite:!1}),i=new Pe(t,n);i.rotation.x=Math.PI,i.renderOrder=999;const s=new oa(.35,32,32),a=new mi({color:new pt(1,1,1),emissive:r,emissiveIntensity:2,transparent:!0,opacity:1,depthTest:!1,depthWrite:!1}),l=new Pe(s,a);return l.position.y=.5,l.renderOrder=999,e.add(i),e.add(l),e}function OC(r){const e=new AP({canvas:r,antialias:!0});e.setPixelRatio(window.devicePixelRatio),e.setSize(r.clientWidth,r.clientHeight),e.shadowMap.enabled=!1,e.toneMapping=fg,e.toneMappingExposure=1.6,e.outputColorSpace=Rn;const t=new RP;t.background=new pt(1381664),t.fog=new Md(1381664,.03);const n=new jn(50,r.clientWidth/r.clientHeight,.1,1e3);n.position.set(0,1.6,5);const i=new pC(n,r);i.target.set(0,.9,0),i.enableDamping=!0,i.dampingFactor=.08,i.update();const s=new uo(14,10),a=new hs({color:4864558,roughness:.35,metalness:.05}),l=new Pe(s,a);l.rotation.x=-Math.PI/2,l.position.y=-.01,l.receiveShadow=!0,t.add(l);const u=new dn(14.2,.06,10.2),h=new hs({color:3811866,roughness:.6}),f=new Pe(u,h);f.position.y=-.04,f.receiveShadow=!0,t.add(f);const p=new QP(16777215,.8);t.add(p);const m=new Il(16777215,3);m.position.set(2,4,-5),t.add(m);const g=lh(new pt(16777215));g.position.copy(m.position),g.lookAt(new F(0,0,0)),g.userData.light=m,t.add(g);const x=new Il(15658751,2);x.position.set(-3,3,-4),t.add(x);const E=lh(new pt(15658751));E.position.copy(x.position),E.lookAt(new F(0,0,0)),E.userData.light=x,t.add(E);const v=new Il(16772829,2.5);v.position.set(0,4,5),t.add(v);const _=lh(new pt(16772829));_.position.copy(v.position),_.lookAt(new F(0,0,0)),_.userData.light=v,t.add(_);const R={ambient:p,spotLeft:m,spotRight:x,backLight:v},w={spotLeftIcon:g,spotRightIcon:E,backLightIcon:_},S=new AC(n,r);S.setMode("translate"),S.setSize(.8),t.add(S),S.addEventListener("dragging-changed",N=>{i.enabled=!N.value});function k(){const N=r.clientWidth,O=r.clientHeight;e.setSize(N,O),n.aspect=N/O,n.updateProjectionMatrix()}return window.addEventListener("resize",k),{scene:t,camera:n,renderer:e,controls:i,lights:R,lightIcons:w,transformControls:S}}var $o={exports:{}};$o.exports;var rg;function UC(){return rg||(rg=1,(function(r,e){var t=Object.create,n=Object.defineProperty,i=Object.defineProperties,s=Object.getOwnPropertyDescriptor,a=Object.getOwnPropertyDescriptors,l=Object.getOwnPropertyNames,u=Object.getOwnPropertySymbols,h=Object.getPrototypeOf,f=Object.prototype.hasOwnProperty,p=Object.prototype.propertyIsEnumerable,m=(o,c,d)=>c in o?n(o,c,{enumerable:!0,configurable:!0,writable:!0,value:d}):o[c]=d,g=(o,c)=>{for(var d in c||(c={}))f.call(c,d)&&m(o,d,c[d]);if(u)for(var d of u(c))p.call(c,d)&&m(o,d,c[d]);return o},x=(o,c)=>i(o,a(c)),E=(o,c)=>function(){return c||(0,o[l(o)[0]])((c={exports:{}}).exports,c),c.exports},v=(o,c)=>{for(var d in c)n(o,d,{get:c[d],enumerable:!0})},_=(o,c,d,y)=>{if(c&&typeof c=="object"||typeof c=="function")for(let M of l(c))!f.call(o,M)&&M!==d&&n(o,M,{get:()=>c[M],enumerable:!(y=s(c,M))||y.enumerable});return o},R=(o,c,d)=>(d=o!=null?t(h(o)):{},_(!o||!o.__esModule?n(d,"default",{value:o,enumerable:!0}):d,o)),w=o=>_(n({},"__esModule",{value:!0}),o),S=(o,c,d)=>(m(o,typeof c!="symbol"?c+"":c,d),d),k=E({"../node_modules/timing-function/lib/UnitBezier.js"(o,c){c.exports=(function(){function d(y,M,C,B){this.set(y,M,C,B)}return d.prototype.set=function(y,M,C,B){this._cx=3*y,this._bx=3*(C-y)-this._cx,this._ax=1-this._cx-this._bx,this._cy=3*M,this._by=3*(B-M)-this._cy,this._ay=1-this._cy-this._by},d.epsilon=1e-6,d.prototype._sampleCurveX=function(y){return((this._ax*y+this._bx)*y+this._cx)*y},d.prototype._sampleCurveY=function(y){return((this._ay*y+this._by)*y+this._cy)*y},d.prototype._sampleCurveDerivativeX=function(y){return(3*this._ax*y+2*this._bx)*y+this._cx},d.prototype._solveCurveX=function(y,M){var C,B,Y,Q,se,xe;for(Y=void 0,Q=void 0,se=void 0,xe=void 0,C=void 0,B=void 0,se=y,B=0;B<8;){if(xe=this._sampleCurveX(se)-y,Math.abs(xe)<M)return se;if(C=this._sampleCurveDerivativeX(se),Math.abs(C)<M)break;se=se-xe/C,B++}if(Y=0,Q=1,se=y,se<Y)return Y;if(se>Q)return Q;for(;Y<Q;){if(xe=this._sampleCurveX(se),Math.abs(xe-y)<M)return se;y>xe?Y=se:Q=se,se=(Q-Y)*.5+Y}return se},d.prototype.solve=function(y,M){return this._sampleCurveY(this._solveCurveX(y,M))},d.prototype.solveSimple=function(y){return this._sampleCurveY(this._solveCurveX(y,1e-6))},d})()}}),N=E({"../node_modules/levenshtein-edit-distance/index.js"(o,c){var d,y;d=[],y=[];function M(C,B,Y){var Q,se,xe,Se,Ie,lt,Ye,wt;if(C===B)return 0;if(Q=C.length,se=B.length,Q===0)return se;if(se===0)return Q;for(Y&&(C=C.toLowerCase(),B=B.toLowerCase()),Ye=0;Ye<Q;)y[Ye]=C.charCodeAt(Ye),d[Ye]=++Ye;for(wt=0;wt<se;)for(xe=B.charCodeAt(wt),Se=Ie=wt++,Ye=-1;++Ye<Q;)lt=xe===y[Ye]?Ie:Ie+1,Ie=d[Ye],d[Ye]=Se=Ie>Se?lt>Se?Se+1:lt:lt>Ie?Ie+1:lt;return Se}c.exports=M}}),O=E({"../node_modules/propose/propose.js"(o,c){var d=N();function y(){var M,C,B,Y,Q,se=0,xe=arguments[0],Se=arguments[1],Ie=Se.length,lt=arguments[2];lt&&(Y=lt.threshold,Q=lt.ignoreCase),Y===void 0&&(Y=0);for(var Ye=0;Ye<Ie;++Ye)Q?C=d(xe,Se[Ye],!0):C=d(xe,Se[Ye]),C>xe.length?M=1-C/Se[Ye].length:M=1-C/xe.length,M>se&&(se=M,B=Se[Ye]);return se>=Y?B:null}c.exports=y}}),H=E({"../node_modules/fast-deep-equal/index.js"(o,c){c.exports=function d(y,M){if(y===M)return!0;if(y&&M&&typeof y=="object"&&typeof M=="object"){if(y.constructor!==M.constructor)return!1;var C,B,Y;if(Array.isArray(y)){if(C=y.length,C!=M.length)return!1;for(B=C;B--!==0;)if(!d(y[B],M[B]))return!1;return!0}if(y.constructor===RegExp)return y.source===M.source&&y.flags===M.flags;if(y.valueOf!==Object.prototype.valueOf)return y.valueOf()===M.valueOf();if(y.toString!==Object.prototype.toString)return y.toString()===M.toString();if(Y=Object.keys(y),C=Y.length,C!==Object.keys(M).length)return!1;for(B=C;B--!==0;)if(!Object.prototype.hasOwnProperty.call(M,Y[B]))return!1;for(B=C;B--!==0;){var Q=Y[B];if(!d(y[Q],M[Q]))return!1}return!0}return y!==y&&M!==M}}}),D={};v(D,{createRafDriver:()=>tu,getProject:()=>Tp,notify:()=>Es,onChange:()=>Eu,types:()=>nu,val:()=>wp}),r.exports=w(D);var A={};v(A,{createRafDriver:()=>tu,getProject:()=>Tp,notify:()=>Es,onChange:()=>Eu,types:()=>nu,val:()=>wp});var z=xn(),Z=class{constructor(){S(this,"atom",new z.Atom({projects:{}}))}add(o,c){this.atom.setByPointer(d=>d.projects[o],c)}get(o){return this.atom.get().projects[o]}has(o){return!!this.get(o)}},$=new Z,ie=$,ae=new WeakMap;function X(o){return ae.get(o)}function he(o,c){ae.set(o,c)}var te=[],ye=Array.isArray,Ee=ye,ke=typeof Di=="object"&&Di&&Di.Object===Object&&Di,Xe=ke,Tt=typeof self=="object"&&self&&self.Object===Object&&self,ce=Xe||Tt||Function("return this")(),ge=ce,Be=ge.Symbol,Me=Be,ot=Object.prototype,ut=ot.hasOwnProperty,Ke=ot.toString,de=Me?Me.toStringTag:void 0;function be(o){var c=ut.call(o,de),d=o[de];try{o[de]=void 0;var y=!0}catch{}var M=Ke.call(o);return y&&(c?o[de]=d:delete o[de]),M}var Oe=be,V=Object.prototype,ct=V.toString;function it(o){return ct.call(o)}var tt=it,ze="[object Null]",dt="[object Undefined]",Ve=Me?Me.toStringTag:void 0;function L(o){return o==null?o===void 0?dt:ze:Ve&&Ve in Object(o)?Oe(o):tt(o)}var T=L;function K(o){return o!=null&&typeof o=="object"}var ue=K,me="[object Symbol]";function le(o){return typeof o=="symbol"||ue(o)&&T(o)==me}var Le=le,Ae=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,He=/^\w*$/;function Pt(o,c){if(Ee(o))return!1;var d=typeof o;return d=="number"||d=="symbol"||d=="boolean"||o==null||Le(o)?!0:He.test(o)||!Ae.test(o)||c!=null&&o in Object(c)}var _e=Pt;function Ce(o){var c=typeof o;return o!=null&&(c=="object"||c=="function")}var Ge=Ce,ft="[object AsyncFunction]",We="[object Function]",At="[object GeneratorFunction]",mt="[object Proxy]";function Ot(o){if(!Ge(o))return!1;var c=T(o);return c==We||c==At||c==ft||c==mt}var W=Ot,Re=ge["__core-js_shared__"],oe=Re,pe=(function(){var o=/[^.]+$/.exec(oe&&oe.keys&&oe.keys.IE_PROTO||"");return o?"Symbol(src)_1."+o:""})();function Fe(o){return!!pe&&pe in o}var De=Fe,bt=Function.prototype,Zt=bt.toString;function un(o){if(o!=null){try{return Zt.call(o)}catch{}try{return o+""}catch{}}return""}var U=un,ne=/[\\^$.*+?()[\]{}|]/g,fe=/^\[object .+?Constructor\]$/,ve=Function.prototype,Je=Object.prototype,Te=ve.toString,qe=Je.hasOwnProperty,at=RegExp("^"+Te.call(qe).replace(ne,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function ht(o){if(!Ge(o)||De(o))return!1;var c=W(o)?at:fe;return c.test(U(o))}var yt=ht;function Et(o,c){return o==null?void 0:o[c]}var je=Et;function nt(o,c){var d=je(o,c);return yt(d)?d:void 0}var rt=nt,Ut=rt(Object,"create"),Lt=Ut;function st(){this.__data__=Lt?Lt(null):{},this.size=0}var P=st;function j(o){var c=this.has(o)&&delete this.__data__[o];return this.size-=c?1:0,c}var J=j,ee="__lodash_hash_undefined__",q=Object.prototype,we=q.hasOwnProperty;function Ue(o){var c=this.__data__;if(Lt){var d=c[o];return d===ee?void 0:d}return we.call(c,o)?c[o]:void 0}var $e=Ue,Ze=Object.prototype,xt=Ze.hasOwnProperty;function gt(o){var c=this.__data__;return Lt?c[o]!==void 0:xt.call(c,o)}var Qe=gt,Bt="__lodash_hash_undefined__";function jt(o,c){var d=this.__data__;return this.size+=this.has(o)?0:1,d[o]=Lt&&c===void 0?Bt:c,this}var qt=jt;function hn(o){var c=-1,d=o==null?0:o.length;for(this.clear();++c<d;){var y=o[c];this.set(y[0],y[1])}}hn.prototype.clear=P,hn.prototype.delete=J,hn.prototype.get=$e,hn.prototype.has=Qe,hn.prototype.set=qt;var kt=hn;function et(){this.__data__=[],this.size=0}var ei=et;function Ft(o,c){return o===c||o!==o&&c!==c}var Cn=Ft;function Ai(o,c){for(var d=o.length;d--;)if(Cn(o[d][0],c))return d;return-1}var mn=Ai,Ui=Array.prototype,Yt=Ui.splice;function Yn(o){var c=this.__data__,d=mn(c,o);if(d<0)return!1;var y=c.length-1;return d==y?c.pop():Yt.call(c,d,1),--this.size,!0}var Bi=Yn;function Nn(o){var c=this.__data__,d=mn(c,o);return d<0?void 0:c[d][1]}var Dn=Nn;function ti(o){return mn(this.__data__,o)>-1}var fs=ti;function mo(o,c){var d=this.__data__,y=mn(d,o);return y<0?(++this.size,d.push([o,c])):d[y][1]=c,this}var Xl=mo;function sr(o){var c=-1,d=o==null?0:o.length;for(this.clear();++c<d;){var y=o[c];this.set(y[0],y[1])}}sr.prototype.clear=ei,sr.prototype.delete=Bi,sr.prototype.get=Dn,sr.prototype.has=fs,sr.prototype.set=Xl;var ps=sr,ql=rt(ge,"Map"),Pr=ql;function Yl(){this.size=0,this.__data__={hash:new kt,map:new(Pr||ps),string:new kt}}var Kl=Yl;function $l(o){var c=typeof o;return c=="string"||c=="number"||c=="symbol"||c=="boolean"?o!=="__proto__":o===null}var Zl=$l;function Ql(o,c){var d=o.__data__;return Zl(c)?d[typeof c=="string"?"string":"hash"]:d.map}var Cr=Ql;function la(o){var c=Cr(this,o).delete(o);return this.size-=c?1:0,c}var ca=la;function Jl(o){return Cr(this,o).get(o)}var ec=Jl;function tc(o){return Cr(this,o).has(o)}var nc=tc;function ic(o,c){var d=Cr(this,o),y=d.size;return d.set(o,c),this.size+=d.size==y?0:1,this}var rc=ic;function or(o){var c=-1,d=o==null?0:o.length;for(this.clear();++c<d;){var y=o[c];this.set(y[0],y[1])}}or.prototype.clear=Kl,or.prototype.delete=ca,or.prototype.get=ec,or.prototype.has=nc,or.prototype.set=rc;var ms=or,sc="Expected a function";function go(o,c){if(typeof o!="function"||c!=null&&typeof c!="function")throw new TypeError(sc);var d=function(){var y=arguments,M=c?c.apply(this,y):y[0],C=d.cache;if(C.has(M))return C.get(M);var B=o.apply(this,y);return d.cache=C.set(M,B)||C,B};return d.cache=new(go.Cache||ms),d}go.Cache=ms;var oc=go,ac=500;function lc(o){var c=oc(o,function(y){return d.size===ac&&d.clear(),y}),d=c.cache;return c}var cc=lc,uc=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,hc=/\\(\\)?/g,dc=cc(function(o){var c=[];return o.charCodeAt(0)===46&&c.push(""),o.replace(uc,function(d,y,M,C){c.push(M?C.replace(hc,"$1"):y||d)}),c}),fc=dc;function ua(o,c){for(var d=-1,y=o==null?0:o.length,M=Array(y);++d<y;)M[d]=c(o[d],d,o);return M}var pc=ua,ha=Me?Me.prototype:void 0,da=ha?ha.toString:void 0;function fa(o){if(typeof o=="string")return o;if(Ee(o))return pc(o,fa)+"";if(Le(o))return da?da.call(o):"";var c=o+"";return c=="0"&&1/o==-1/0?"-0":c}var pa=fa;function mc(o){return o==null?"":pa(o)}var gs=mc;function ma(o,c){return Ee(o)?o:_e(o,c)?[o]:fc(gs(o))}var Dr=ma;function gc(o){if(typeof o=="string"||Le(o))return o;var c=o+"";return c=="0"&&1/o==-1/0?"-0":c}var gi=gc;function Ir(o,c){c=Dr(c,o);for(var d=0,y=c.length;o!=null&&d<y;)o=o[gi(c[d++])];return d&&d==y?o:void 0}var _s=Ir;function _o(o,c,d){var y=o==null?void 0:_s(o,c);return y===void 0?d:y}var ki=_o;function ga(o,c){return c.length===0?o:ki(o,c)}var ar=class{constructor(){S(this,"_values",{})}get(o,c){if(this.has(o))return this._values[o];{const d=c();return this._values[o]=d,d}}has(o){return this._values.hasOwnProperty(o)}},vn=xn(),vs=(function(){try{var o=rt(Object,"defineProperty");return o({},"",{}),o}catch{}})(),vo=vs;function _c(o,c,d){c=="__proto__"&&vo?vo(o,c,{configurable:!0,enumerable:!0,value:d,writable:!0}):o[c]=d}var zi=_c,Lr=Object.prototype,vc=Lr.hasOwnProperty;function yc(o,c,d){var y=o[c];(!(vc.call(o,c)&&Cn(y,d))||d===void 0&&!(c in o))&&zi(o,c,d)}var yo=yc,xc=9007199254740991,_a=/^(?:0|[1-9]\d*)$/;function bc(o,c){var d=typeof o;return c=c??xc,!!c&&(d=="number"||d!="symbol"&&_a.test(o))&&o>-1&&o%1==0&&o<c}var xo=bc;function Sc(o,c,d,y){if(!Ge(o))return o;c=Dr(c,o);for(var M=-1,C=c.length,B=C-1,Y=o;Y!=null&&++M<C;){var Q=gi(c[M]),se=d;if(Q==="__proto__"||Q==="constructor"||Q==="prototype")return o;if(M!=B){var xe=Y[Q];se=y?y(xe,Q,Y):void 0,se===void 0&&(se=Ge(xe)?xe:xo(c[M+1])?[]:{})}yo(Y,Q,se),Y=Y[Q]}return o}var va=Sc;function ya(o,c,d){return o==null?o:va(o,c,d)}var ys=ya,Tn=new WeakMap;function Ec(o){return bo(o)}function bo(o){if(Tn.has(o))return Tn.get(o);const c=o.type==="compound"?ba(o):o.type==="enum"?xa(o):o.default;return Tn.set(o,c),c}function xa(o){const c={$case:o.defaultCase};for(const[d,y]of Object.entries(o.cases))c[d]=bo(y);return c}function ba(o){const c={};for(const[d,y]of Object.entries(o.props))c[d]=bo(y);return c}var Vn=xn(),Mc=R(k());function Tc(o,c,d){return(0,Vn.prism)(()=>{const y=(0,Vn.val)(c);return Vn.prism.memo("driver",()=>y?y.type==="BasicKeyframedTrack"?wc(o,y,d):(o.logger.error("Track type not yet supported."),(0,Vn.prism)(()=>{})):(0,Vn.prism)(()=>{}),[y]).getValue()})}function wc(o,c,d){return(0,Vn.prism)(()=>{let y=Vn.prism.ref("state",{started:!1}),M=y.current;const C=d.getValue();return(!M.started||C<M.validFrom||M.validTo<=C)&&(y.current=M=Ac(o,d,c)),M.der.getValue()})}var Sa=(0,Vn.prism)(()=>{});function Ac(o,c,d){const y=c.getValue();if(d.keyframes.length===0)return{started:!0,validFrom:-1/0,validTo:1/0,der:Sa};let M=0;for(;;){const C=d.keyframes[M];if(!C)return yn.error;const B=M===d.keyframes.length-1;if(y<C.position)return M===0?yn.beforeFirstKeyframe(C):yn.error;if(C.position===y)return B?yn.lastKeyframe(C):yn.between(C,d.keyframes[M+1],c);if(M===d.keyframes.length-1)return yn.lastKeyframe(C);{const Y=M+1;if(d.keyframes[Y].position<=y){M=Y;continue}else return yn.between(C,d.keyframes[M+1],c)}}}var yn={beforeFirstKeyframe(o){return{started:!0,validFrom:-1/0,validTo:o.position,der:(0,Vn.prism)(()=>({left:o.value,progression:0}))}},lastKeyframe(o){return{started:!0,validFrom:o.position,validTo:1/0,der:(0,Vn.prism)(()=>({left:o.value,progression:0}))}},between(o,c,d){if(!o.connectedRight)return{started:!0,validFrom:o.position,validTo:c.position,der:(0,Vn.prism)(()=>({left:o.value,progression:0}))};const y=C=>(C-o.position)/(c.position-o.position);if(!o.type||o.type==="bezier"){const C=new Mc.default(o.handles[2],o.handles[3],c.handles[0],c.handles[1]),B=(0,Vn.prism)(()=>{const Y=y(d.getValue()),Q=C.solveSimple(Y);return{left:o.value,right:c.value,progression:Q}});return{started:!0,validFrom:o.position,validTo:c.position,der:B}}const M=(0,Vn.prism)(()=>{const C=y(d.getValue()),B=Math.floor(C);return{left:o.value,right:c.value,progression:B}});return{started:!0,validFrom:o.position,validTo:c.position,der:M}},error:{started:!0,validFrom:-1/0,validTo:1/0,der:Sa}};function Fr(o,c,d){const M=d.get(o);if(M&&M.override===c)return M.merged;const C=g({},o);for(const B of Object.keys(c)){const Y=c[B],Q=o[B];C[B]=typeof Y=="object"&&typeof Q=="object"?Fr(Q,Y,d):Y===void 0?Q:Y}return d.set(o,{override:c,merged:C}),C}function Nr(o,c){let d=o;for(const y of c)d=d[y];return d}var Or=xn(),Ea=(o,c)=>{const d=Or.prism.memo(o,()=>new Or.Atom(c),[]);return d.set(c),d},Kt=xn(),So=xn(),Rc=/\s/;function Ma(o){for(var c=o.length;c--&&Rc.test(o.charAt(c)););return c}var Ta=Ma,wa=/^\s+/;function Pc(o){return o&&o.slice(0,Ta(o)+1).replace(wa,"")}var xs=Pc,Eo=NaN,Cc=/^[-+]0x[0-9a-f]+$/i,Dc=/^0b[01]+$/i,Aa=/^0o[0-7]+$/i,Ic=parseInt;function Lc(o){if(typeof o=="number")return o;if(Le(o))return Eo;if(Ge(o)){var c=typeof o.valueOf=="function"?o.valueOf():o;o=Ge(c)?c+"":c}if(typeof o!="string")return o===0?o:+o;o=xs(o);var d=Dc.test(o);return d||Aa.test(o)?Ic(o.slice(2),d?2:8):Cc.test(o)?Eo:+o}var b=Lc,I=1/0,G=17976931348623157e292;function re(o){if(!o)return o===0?o:0;if(o=b(o),o===I||o===-I){var c=o<0?-1:1;return c*G}return o===o?o:0}var _t=re;function Ht(o){var c=_t(o),d=c%1;return c===c?d?c-d:c:0}var In=Ht;function ui(o){return o}var Ra=ui,lr=rt(ge,"WeakMap"),Ur=lr,Nd=Object.create,c_=(function(){function o(){}return function(c){if(!Ge(c))return{};if(Nd)return Nd(c);o.prototype=c;var d=new o;return o.prototype=void 0,d}})(),u_=c_;function h_(o,c){var d=-1,y=o.length;for(c||(c=Array(y));++d<y;)c[d]=o[d];return c}var d_=h_;function f_(o,c){for(var d=-1,y=o==null?0:o.length;++d<y&&c(o[d],d,o)!==!1;);return o}var p_=f_;function m_(o,c,d,y){var M=!d;d||(d={});for(var C=-1,B=c.length;++C<B;){var Y=c[C],Q=y?y(d[Y],o[Y],Y,d,o):void 0;Q===void 0&&(Q=o[Y]),M?zi(d,Y,Q):yo(d,Y,Q)}return d}var Pa=m_,g_=9007199254740991;function __(o){return typeof o=="number"&&o>-1&&o%1==0&&o<=g_}var Fc=__;function v_(o){return o!=null&&Fc(o.length)&&!W(o)}var Od=v_,y_=Object.prototype;function x_(o){var c=o&&o.constructor,d=typeof c=="function"&&c.prototype||y_;return o===d}var Nc=x_;function b_(o,c){for(var d=-1,y=Array(o);++d<o;)y[d]=c(d);return y}var S_=b_,E_="[object Arguments]";function M_(o){return ue(o)&&T(o)==E_}var Ud=M_,Bd=Object.prototype,T_=Bd.hasOwnProperty,w_=Bd.propertyIsEnumerable,A_=Ud((function(){return arguments})())?Ud:function(o){return ue(o)&&T_.call(o,"callee")&&!w_.call(o,"callee")},kd=A_;function R_(){return!1}var P_=R_,zd=e&&!e.nodeType&&e,Hd=zd&&!0&&r&&!r.nodeType&&r,C_=Hd&&Hd.exports===zd,Vd=C_?ge.Buffer:void 0,D_=Vd?Vd.isBuffer:void 0,I_=D_||P_,Ca=I_,L_="[object Arguments]",F_="[object Array]",N_="[object Boolean]",O_="[object Date]",U_="[object Error]",B_="[object Function]",k_="[object Map]",z_="[object Number]",H_="[object Object]",V_="[object RegExp]",G_="[object Set]",W_="[object String]",j_="[object WeakMap]",X_="[object ArrayBuffer]",q_="[object DataView]",Y_="[object Float32Array]",K_="[object Float64Array]",$_="[object Int8Array]",Z_="[object Int16Array]",Q_="[object Int32Array]",J_="[object Uint8Array]",e0="[object Uint8ClampedArray]",t0="[object Uint16Array]",n0="[object Uint32Array]",ln={};ln[Y_]=ln[K_]=ln[$_]=ln[Z_]=ln[Q_]=ln[J_]=ln[e0]=ln[t0]=ln[n0]=!0,ln[L_]=ln[F_]=ln[X_]=ln[N_]=ln[q_]=ln[O_]=ln[U_]=ln[B_]=ln[k_]=ln[z_]=ln[H_]=ln[V_]=ln[G_]=ln[W_]=ln[j_]=!1;function i0(o){return ue(o)&&Fc(o.length)&&!!ln[T(o)]}var r0=i0;function s0(o){return function(c){return o(c)}}var Oc=s0,Gd=e&&!e.nodeType&&e,Mo=Gd&&!0&&r&&!r.nodeType&&r,o0=Mo&&Mo.exports===Gd,Uc=o0&&Xe.process,a0=(function(){try{var o=Mo&&Mo.require&&Mo.require("util").types;return o||Uc&&Uc.binding&&Uc.binding("util")}catch{}})(),bs=a0,Wd=bs&&bs.isTypedArray,l0=Wd?Oc(Wd):r0,jd=l0,c0=Object.prototype,u0=c0.hasOwnProperty;function h0(o,c){var d=Ee(o),y=!d&&kd(o),M=!d&&!y&&Ca(o),C=!d&&!y&&!M&&jd(o),B=d||y||M||C,Y=B?S_(o.length,String):[],Q=Y.length;for(var se in o)(c||u0.call(o,se))&&!(B&&(se=="length"||M&&(se=="offset"||se=="parent")||C&&(se=="buffer"||se=="byteLength"||se=="byteOffset")||xo(se,Q)))&&Y.push(se);return Y}var Xd=h0;function d0(o,c){return function(d){return o(c(d))}}var qd=d0,f0=qd(Object.keys,Object),p0=f0,m0=Object.prototype,g0=m0.hasOwnProperty;function _0(o){if(!Nc(o))return p0(o);var c=[];for(var d in Object(o))g0.call(o,d)&&d!="constructor"&&c.push(d);return c}var v0=_0;function y0(o){return Od(o)?Xd(o):v0(o)}var To=y0;function x0(o){var c=[];if(o!=null)for(var d in Object(o))c.push(d);return c}var b0=x0,S0=Object.prototype,E0=S0.hasOwnProperty;function M0(o){if(!Ge(o))return b0(o);var c=Nc(o),d=[];for(var y in o)y=="constructor"&&(c||!E0.call(o,y))||d.push(y);return d}var T0=M0;function w0(o){return Od(o)?Xd(o,!0):T0(o)}var Bc=w0;function A0(o,c){for(var d=-1,y=c.length,M=o.length;++d<y;)o[M+d]=c[d];return o}var Yd=A0,R0=qd(Object.getPrototypeOf,Object),kc=R0,P0="[object Object]",C0=Function.prototype,D0=Object.prototype,Kd=C0.toString,I0=D0.hasOwnProperty,L0=Kd.call(Object);function F0(o){if(!ue(o)||T(o)!=P0)return!1;var c=kc(o);if(c===null)return!0;var d=I0.call(c,"constructor")&&c.constructor;return typeof d=="function"&&d instanceof d&&Kd.call(d)==L0}var N0=F0;function O0(o,c,d){var y=-1,M=o.length;c<0&&(c=-c>M?0:M+c),d=d>M?M:d,d<0&&(d+=M),M=c>d?0:d-c>>>0,c>>>=0;for(var C=Array(M);++y<M;)C[y]=o[y+c];return C}var $d=O0;function U0(o,c,d){var y=o.length;return d=d===void 0?y:d,!c&&d>=y?o:$d(o,c,d)}var B0=U0,k0="\\ud800-\\udfff",z0="\\u0300-\\u036f",H0="\\ufe20-\\ufe2f",V0="\\u20d0-\\u20ff",G0=z0+H0+V0,W0="\\ufe0e\\ufe0f",j0="\\u200d",X0=RegExp("["+j0+k0+G0+W0+"]");function q0(o){return X0.test(o)}var zc=q0;function Y0(o){return o.split("")}var K0=Y0,Zd="\\ud800-\\udfff",$0="\\u0300-\\u036f",Z0="\\ufe20-\\ufe2f",Q0="\\u20d0-\\u20ff",J0=$0+Z0+Q0,ev="\\ufe0e\\ufe0f",tv="["+Zd+"]",Hc="["+J0+"]",Vc="\\ud83c[\\udffb-\\udfff]",nv="(?:"+Hc+"|"+Vc+")",Qd="[^"+Zd+"]",Jd="(?:\\ud83c[\\udde6-\\uddff]){2}",ef="[\\ud800-\\udbff][\\udc00-\\udfff]",iv="\\u200d",tf=nv+"?",nf="["+ev+"]?",rv="(?:"+iv+"(?:"+[Qd,Jd,ef].join("|")+")"+nf+tf+")*",sv=nf+tf+rv,ov="(?:"+[Qd+Hc+"?",Hc,Jd,ef,tv].join("|")+")",av=RegExp(Vc+"(?="+Vc+")|"+ov+sv,"g");function lv(o){return o.match(av)||[]}var cv=lv;function uv(o){return zc(o)?cv(o):K0(o)}var hv=uv;function dv(o,c,d){return o===o&&(d!==void 0&&(o=o<=d?o:d),c!==void 0&&(o=o>=c?o:c)),o}var fv=dv;function pv(o,c,d){return d===void 0&&(d=c,c=void 0),d!==void 0&&(d=b(d),d=d===d?d:0),c!==void 0&&(c=b(c),c=c===c?c:0),fv(b(o),c,d)}var rf=pv;function mv(){this.__data__=new ps,this.size=0}var gv=mv;function _v(o){var c=this.__data__,d=c.delete(o);return this.size=c.size,d}var vv=_v;function yv(o){return this.__data__.get(o)}var xv=yv;function bv(o){return this.__data__.has(o)}var Sv=bv,Ev=200;function Mv(o,c){var d=this.__data__;if(d instanceof ps){var y=d.__data__;if(!Pr||y.length<Ev-1)return y.push([o,c]),this.size=++d.size,this;d=this.__data__=new ms(y)}return d.set(o,c),this.size=d.size,this}var Tv=Mv;function Ss(o){var c=this.__data__=new ps(o);this.size=c.size}Ss.prototype.clear=gv,Ss.prototype.delete=vv,Ss.prototype.get=xv,Ss.prototype.has=Sv,Ss.prototype.set=Tv;var wo=Ss;function wv(o,c){return o&&Pa(c,To(c),o)}var Av=wv;function Rv(o,c){return o&&Pa(c,Bc(c),o)}var Pv=Rv,sf=e&&!e.nodeType&&e,of=sf&&!0&&r&&!r.nodeType&&r,Cv=of&&of.exports===sf,af=Cv?ge.Buffer:void 0,lf=af?af.allocUnsafe:void 0;function Dv(o,c){if(c)return o.slice();var d=o.length,y=lf?lf(d):new o.constructor(d);return o.copy(y),y}var Iv=Dv;function Lv(o,c){for(var d=-1,y=o==null?0:o.length,M=0,C=[];++d<y;){var B=o[d];c(B,d,o)&&(C[M++]=B)}return C}var Fv=Lv;function Nv(){return[]}var cf=Nv,Ov=Object.prototype,Uv=Ov.propertyIsEnumerable,uf=Object.getOwnPropertySymbols,Bv=uf?function(o){return o==null?[]:(o=Object(o),Fv(uf(o),function(c){return Uv.call(o,c)}))}:cf,Gc=Bv;function kv(o,c){return Pa(o,Gc(o),c)}var zv=kv,Hv=Object.getOwnPropertySymbols,Vv=Hv?function(o){for(var c=[];o;)Yd(c,Gc(o)),o=kc(o);return c}:cf,hf=Vv;function Gv(o,c){return Pa(o,hf(o),c)}var Wv=Gv;function jv(o,c,d){var y=c(o);return Ee(o)?y:Yd(y,d(o))}var df=jv;function Xv(o){return df(o,To,Gc)}var Wc=Xv;function qv(o){return df(o,Bc,hf)}var Yv=qv,Kv=rt(ge,"DataView"),jc=Kv,$v=rt(ge,"Promise"),Xc=$v,Zv=rt(ge,"Set"),qc=Zv,ff="[object Map]",Qv="[object Object]",pf="[object Promise]",mf="[object Set]",gf="[object WeakMap]",_f="[object DataView]",Jv=U(jc),ey=U(Pr),ty=U(Xc),ny=U(qc),iy=U(Ur),Br=T;(jc&&Br(new jc(new ArrayBuffer(1)))!=_f||Pr&&Br(new Pr)!=ff||Xc&&Br(Xc.resolve())!=pf||qc&&Br(new qc)!=mf||Ur&&Br(new Ur)!=gf)&&(Br=function(o){var c=T(o),d=c==Qv?o.constructor:void 0,y=d?U(d):"";if(y)switch(y){case Jv:return _f;case ey:return ff;case ty:return pf;case ny:return mf;case iy:return gf}return c});var Ao=Br,ry=Object.prototype,sy=ry.hasOwnProperty;function oy(o){var c=o.length,d=new o.constructor(c);return c&&typeof o[0]=="string"&&sy.call(o,"index")&&(d.index=o.index,d.input=o.input),d}var ay=oy,ly=ge.Uint8Array,Da=ly;function cy(o){var c=new o.constructor(o.byteLength);return new Da(c).set(new Da(o)),c}var Yc=cy;function uy(o,c){var d=c?Yc(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.byteLength)}var hy=uy,dy=/\w*$/;function fy(o){var c=new o.constructor(o.source,dy.exec(o));return c.lastIndex=o.lastIndex,c}var py=fy,vf=Me?Me.prototype:void 0,yf=vf?vf.valueOf:void 0;function my(o){return yf?Object(yf.call(o)):{}}var gy=my;function _y(o,c){var d=c?Yc(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.length)}var vy=_y,yy="[object Boolean]",xy="[object Date]",by="[object Map]",Sy="[object Number]",Ey="[object RegExp]",My="[object Set]",Ty="[object String]",wy="[object Symbol]",Ay="[object ArrayBuffer]",Ry="[object DataView]",Py="[object Float32Array]",Cy="[object Float64Array]",Dy="[object Int8Array]",Iy="[object Int16Array]",Ly="[object Int32Array]",Fy="[object Uint8Array]",Ny="[object Uint8ClampedArray]",Oy="[object Uint16Array]",Uy="[object Uint32Array]";function By(o,c,d){var y=o.constructor;switch(c){case Ay:return Yc(o);case yy:case xy:return new y(+o);case Ry:return hy(o,d);case Py:case Cy:case Dy:case Iy:case Ly:case Fy:case Ny:case Oy:case Uy:return vy(o,d);case by:return new y;case Sy:case Ty:return new y(o);case Ey:return py(o);case My:return new y;case wy:return gy(o)}}var ky=By;function zy(o){return typeof o.constructor=="function"&&!Nc(o)?u_(kc(o)):{}}var Hy=zy,Vy="[object Map]";function Gy(o){return ue(o)&&Ao(o)==Vy}var Wy=Gy,xf=bs&&bs.isMap,jy=xf?Oc(xf):Wy,Xy=jy,qy="[object Set]";function Yy(o){return ue(o)&&Ao(o)==qy}var Ky=Yy,bf=bs&&bs.isSet,$y=bf?Oc(bf):Ky,Zy=$y,Qy=1,Jy=2,ex=4,Sf="[object Arguments]",tx="[object Array]",nx="[object Boolean]",ix="[object Date]",rx="[object Error]",Ef="[object Function]",sx="[object GeneratorFunction]",ox="[object Map]",ax="[object Number]",Mf="[object Object]",lx="[object RegExp]",cx="[object Set]",ux="[object String]",hx="[object Symbol]",dx="[object WeakMap]",fx="[object ArrayBuffer]",px="[object DataView]",mx="[object Float32Array]",gx="[object Float64Array]",_x="[object Int8Array]",vx="[object Int16Array]",yx="[object Int32Array]",xx="[object Uint8Array]",bx="[object Uint8ClampedArray]",Sx="[object Uint16Array]",Ex="[object Uint32Array]",nn={};nn[Sf]=nn[tx]=nn[fx]=nn[px]=nn[nx]=nn[ix]=nn[mx]=nn[gx]=nn[_x]=nn[vx]=nn[yx]=nn[ox]=nn[ax]=nn[Mf]=nn[lx]=nn[cx]=nn[ux]=nn[hx]=nn[xx]=nn[bx]=nn[Sx]=nn[Ex]=!0,nn[rx]=nn[Ef]=nn[dx]=!1;function Ia(o,c,d,y,M,C){var B,Y=c&Qy,Q=c&Jy,se=c&ex;if(d&&(B=M?d(o,y,M,C):d(o)),B!==void 0)return B;if(!Ge(o))return o;var xe=Ee(o);if(xe){if(B=ay(o),!Y)return d_(o,B)}else{var Se=Ao(o),Ie=Se==Ef||Se==sx;if(Ca(o))return Iv(o,Y);if(Se==Mf||Se==Sf||Ie&&!M){if(B=Q||Ie?{}:Hy(o),!Y)return Q?Wv(o,Pv(B,o)):zv(o,Av(B,o))}else{if(!nn[Se])return M?o:{};B=ky(o,Se,Y)}}C||(C=new wo);var lt=C.get(o);if(lt)return lt;C.set(o,B),Zy(o)?o.forEach(function(It){B.add(Ia(It,c,d,It,o,C))}):Xy(o)&&o.forEach(function(It,Mt){B.set(Mt,Ia(It,c,d,Mt,o,C))});var Ye=se?Q?Yv:Wc:Q?Bc:To,wt=xe?void 0:Ye(o);return p_(wt||o,function(It,Mt){wt&&(Mt=It,It=o[Mt]),yo(B,Mt,Ia(It,c,d,Mt,o,C))}),B}var Mx=Ia,Tx=1,wx=4;function Ax(o){return Mx(o,Tx|wx)}var Rx=Ax,Px="__lodash_hash_undefined__";function Cx(o){return this.__data__.set(o,Px),this}var Dx=Cx;function Ix(o){return this.__data__.has(o)}var Lx=Ix;function La(o){var c=-1,d=o==null?0:o.length;for(this.__data__=new ms;++c<d;)this.add(o[c])}La.prototype.add=La.prototype.push=Dx,La.prototype.has=Lx;var Fx=La;function Nx(o,c){for(var d=-1,y=o==null?0:o.length;++d<y;)if(c(o[d],d,o))return!0;return!1}var Ox=Nx;function Ux(o,c){return o.has(c)}var Bx=Ux,kx=1,zx=2;function Hx(o,c,d,y,M,C){var B=d&kx,Y=o.length,Q=c.length;if(Y!=Q&&!(B&&Q>Y))return!1;var se=C.get(o),xe=C.get(c);if(se&&xe)return se==c&&xe==o;var Se=-1,Ie=!0,lt=d&zx?new Fx:void 0;for(C.set(o,c),C.set(c,o);++Se<Y;){var Ye=o[Se],wt=c[Se];if(y)var It=B?y(wt,Ye,Se,c,o,C):y(Ye,wt,Se,o,c,C);if(It!==void 0){if(It)continue;Ie=!1;break}if(lt){if(!Ox(c,function(Mt,Vt){if(!Bx(lt,Vt)&&(Ye===Mt||M(Ye,Mt,d,y,C)))return lt.push(Vt)})){Ie=!1;break}}else if(!(Ye===wt||M(Ye,wt,d,y,C))){Ie=!1;break}}return C.delete(o),C.delete(c),Ie}var Tf=Hx;function Vx(o){var c=-1,d=Array(o.size);return o.forEach(function(y,M){d[++c]=[M,y]}),d}var Gx=Vx;function Wx(o){var c=-1,d=Array(o.size);return o.forEach(function(y){d[++c]=y}),d}var jx=Wx,Xx=1,qx=2,Yx="[object Boolean]",Kx="[object Date]",$x="[object Error]",Zx="[object Map]",Qx="[object Number]",Jx="[object RegExp]",eb="[object Set]",tb="[object String]",nb="[object Symbol]",ib="[object ArrayBuffer]",rb="[object DataView]",wf=Me?Me.prototype:void 0,Kc=wf?wf.valueOf:void 0;function sb(o,c,d,y,M,C,B){switch(d){case rb:if(o.byteLength!=c.byteLength||o.byteOffset!=c.byteOffset)return!1;o=o.buffer,c=c.buffer;case ib:return!(o.byteLength!=c.byteLength||!C(new Da(o),new Da(c)));case Yx:case Kx:case Qx:return Cn(+o,+c);case $x:return o.name==c.name&&o.message==c.message;case Jx:case tb:return o==c+"";case Zx:var Y=Gx;case eb:var Q=y&Xx;if(Y||(Y=jx),o.size!=c.size&&!Q)return!1;var se=B.get(o);if(se)return se==c;y|=qx,B.set(o,c);var xe=Tf(Y(o),Y(c),y,M,C,B);return B.delete(o),xe;case nb:if(Kc)return Kc.call(o)==Kc.call(c)}return!1}var ob=sb,ab=1,lb=Object.prototype,cb=lb.hasOwnProperty;function ub(o,c,d,y,M,C){var B=d&ab,Y=Wc(o),Q=Y.length,se=Wc(c),xe=se.length;if(Q!=xe&&!B)return!1;for(var Se=Q;Se--;){var Ie=Y[Se];if(!(B?Ie in c:cb.call(c,Ie)))return!1}var lt=C.get(o),Ye=C.get(c);if(lt&&Ye)return lt==c&&Ye==o;var wt=!0;C.set(o,c),C.set(c,o);for(var It=B;++Se<Q;){Ie=Y[Se];var Mt=o[Ie],Vt=c[Ie];if(y)var On=B?y(Vt,Mt,Ie,c,o,C):y(Mt,Vt,Ie,o,c,C);if(!(On===void 0?Mt===Vt||M(Mt,Vt,d,y,C):On)){wt=!1;break}It||(It=Ie=="constructor")}if(wt&&!It){var $n=o.constructor,Un=c.constructor;$n!=Un&&"constructor"in o&&"constructor"in c&&!(typeof $n=="function"&&$n instanceof $n&&typeof Un=="function"&&Un instanceof Un)&&(wt=!1)}return C.delete(o),C.delete(c),wt}var hb=ub,db=1,Af="[object Arguments]",Rf="[object Array]",Fa="[object Object]",fb=Object.prototype,Pf=fb.hasOwnProperty;function pb(o,c,d,y,M,C){var B=Ee(o),Y=Ee(c),Q=B?Rf:Ao(o),se=Y?Rf:Ao(c);Q=Q==Af?Fa:Q,se=se==Af?Fa:se;var xe=Q==Fa,Se=se==Fa,Ie=Q==se;if(Ie&&Ca(o)){if(!Ca(c))return!1;B=!0,xe=!1}if(Ie&&!xe)return C||(C=new wo),B||jd(o)?Tf(o,c,d,y,M,C):ob(o,c,Q,d,y,M,C);if(!(d&db)){var lt=xe&&Pf.call(o,"__wrapped__"),Ye=Se&&Pf.call(c,"__wrapped__");if(lt||Ye){var wt=lt?o.value():o,It=Ye?c.value():c;return C||(C=new wo),M(wt,It,d,y,C)}}return Ie?(C||(C=new wo),hb(o,c,d,y,M,C)):!1}var mb=pb;function Cf(o,c,d,y,M){return o===c?!0:o==null||c==null||!ue(o)&&!ue(c)?o!==o&&c!==c:mb(o,c,d,y,Cf,M)}var Df=Cf,gb=1,_b=2;function vb(o,c,d,y){var M=d.length,C=M,B=!y;if(o==null)return!C;for(o=Object(o);M--;){var Y=d[M];if(B&&Y[2]?Y[1]!==o[Y[0]]:!(Y[0]in o))return!1}for(;++M<C;){Y=d[M];var Q=Y[0],se=o[Q],xe=Y[1];if(B&&Y[2]){if(se===void 0&&!(Q in o))return!1}else{var Se=new wo;if(y)var Ie=y(se,xe,Q,o,c,Se);if(!(Ie===void 0?Df(xe,se,gb|_b,y,Se):Ie))return!1}}return!0}var yb=vb;function xb(o){return o===o&&!Ge(o)}var If=xb;function bb(o){for(var c=To(o),d=c.length;d--;){var y=c[d],M=o[y];c[d]=[y,M,If(M)]}return c}var Sb=bb;function Eb(o,c){return function(d){return d==null?!1:d[o]===c&&(c!==void 0||o in Object(d))}}var Lf=Eb;function Mb(o){var c=Sb(o);return c.length==1&&c[0][2]?Lf(c[0][0],c[0][1]):function(d){return d===o||yb(d,o,c)}}var Tb=Mb;function wb(o,c){return o!=null&&c in Object(o)}var Ab=wb;function Rb(o,c,d){c=Dr(c,o);for(var y=-1,M=c.length,C=!1;++y<M;){var B=gi(c[y]);if(!(C=o!=null&&d(o,B)))break;o=o[B]}return C||++y!=M?C:(M=o==null?0:o.length,!!M&&Fc(M)&&xo(B,M)&&(Ee(o)||kd(o)))}var Pb=Rb;function Cb(o,c){return o!=null&&Pb(o,c,Ab)}var Db=Cb,Ib=1,Lb=2;function Fb(o,c){return _e(o)&&If(c)?Lf(gi(o),c):function(d){var y=ki(d,o);return y===void 0&&y===c?Db(d,o):Df(c,y,Ib|Lb)}}var Nb=Fb;function Ob(o){return function(c){return c==null?void 0:c[o]}}var Ff=Ob;function Ub(o){return function(c){return _s(c,o)}}var Bb=Ub;function kb(o){return _e(o)?Ff(gi(o)):Bb(o)}var zb=kb;function Hb(o){return typeof o=="function"?o:o==null?Ra:typeof o=="object"?Ee(o)?Nb(o[0],o[1]):Tb(o):zb(o)}var Vb=Hb;function Gb(o){return function(c,d,y){for(var M=-1,C=Object(c),B=y(c),Y=B.length;Y--;){var Q=B[o?Y:++M];if(d(C[Q],Q,C)===!1)break}return c}}var Wb=Gb,jb=Wb(),Xb=jb;function qb(o,c){return o&&Xb(o,c,To)}var Yb=qb,Kb=function(){return ge.Date.now()},$c=Kb,$b="Expected a function",Zb=Math.max,Qb=Math.min;function Jb(o,c,d){var y,M,C,B,Y,Q,se=0,xe=!1,Se=!1,Ie=!0;if(typeof o!="function")throw new TypeError($b);c=b(c)||0,Ge(d)&&(xe=!!d.leading,Se="maxWait"in d,C=Se?Zb(b(d.maxWait)||0,c):C,Ie="trailing"in d?!!d.trailing:Ie);function lt(en){var Bn=y,si=M;return y=M=void 0,se=en,B=o.apply(si,Bn),B}function Ye(en){return se=en,Y=setTimeout(Mt,c),xe?lt(en):B}function wt(en){var Bn=en-Q,si=en-se,Ri=c-Bn;return Se?Qb(Ri,C-si):Ri}function It(en){var Bn=en-Q,si=en-se;return Q===void 0||Bn>=c||Bn<0||Se&&si>=C}function Mt(){var en=$c();if(It(en))return Vt(en);Y=setTimeout(Mt,wt(en))}function Vt(en){return Y=void 0,Ie&&y?lt(en):(y=M=void 0,B)}function On(){Y!==void 0&&clearTimeout(Y),se=0,y=Q=M=Y=void 0}function $n(){return Y===void 0?B:Vt($c())}function Un(){var en=$c(),Bn=It(en);if(y=arguments,M=this,Q=en,Bn){if(Y===void 0)return Ye(Q);if(Se)return clearTimeout(Y),Y=setTimeout(Mt,c),lt(Q)}return Y===void 0&&(Y=setTimeout(Mt,c)),B}return Un.cancel=On,Un.flush=$n,Un}var eS=Jb;function tS(o){var c=o==null?0:o.length;return c?o[c-1]:void 0}var nS=tS;function iS(o,c){return c.length<2?o:_s(o,$d(c,0,-1))}var rS=iS;function sS(o){return typeof o=="number"&&o==In(o)}var oS=sS;function aS(o,c){var d={};return c=Vb(c),Yb(o,function(y,M,C){zi(d,M,c(y,M,C))}),d}var lS=aS;function cS(o,c){return c=Dr(c,o),o=rS(o,c),o==null||delete o[gi(nS(c))]}var uS=cS,hS=9007199254740991,dS=Math.floor;function fS(o,c){var d="";if(!o||c<1||c>hS)return d;do c%2&&(d+=o),c=dS(c/2),c&&(o+=o);while(c);return d}var Nf=fS,pS=Ff("length"),mS=pS,Of="\\ud800-\\udfff",gS="\\u0300-\\u036f",_S="\\ufe20-\\ufe2f",vS="\\u20d0-\\u20ff",yS=gS+_S+vS,xS="\\ufe0e\\ufe0f",bS="["+Of+"]",Zc="["+yS+"]",Qc="\\ud83c[\\udffb-\\udfff]",SS="(?:"+Zc+"|"+Qc+")",Uf="[^"+Of+"]",Bf="(?:\\ud83c[\\udde6-\\uddff]){2}",kf="[\\ud800-\\udbff][\\udc00-\\udfff]",ES="\\u200d",zf=SS+"?",Hf="["+xS+"]?",MS="(?:"+ES+"(?:"+[Uf,Bf,kf].join("|")+")"+Hf+zf+")*",TS=Hf+zf+MS,wS="(?:"+[Uf+Zc+"?",Zc,Bf,kf,bS].join("|")+")",Vf=RegExp(Qc+"(?="+Qc+")|"+wS+TS,"g");function AS(o){for(var c=Vf.lastIndex=0;Vf.test(o);)++c;return c}var RS=AS;function PS(o){return zc(o)?RS(o):mS(o)}var Gf=PS,CS=Math.ceil;function DS(o,c){c=c===void 0?" ":pa(c);var d=c.length;if(d<2)return d?Nf(c,o):c;var y=Nf(c,CS(o/Gf(c)));return zc(c)?B0(hv(y),0,o).join(""):y.slice(0,o)}var IS=DS;function LS(o,c,d){o=gs(o),c=In(c);var y=c?Gf(o):0;return c&&y<c?IS(c-y,d)+o:o}var Ro=LS;function FS(o,c){return o==null?!0:uS(o,c)}var Wf=FS,NS=5*1e3,OS=class{constructor(o){S(this,"_cache",new ar),S(this,"_keepHotUntapDebounce"),he(this,o)}get type(){return"Theatre_SheetObject_PublicAPI"}get props(){return X(this).propsP}get sheet(){return X(this).sheet.publicApi}get project(){return X(this).sheet.project.publicApi}get address(){return g({},X(this).address)}_valuesPrism(){return this._cache.get("_valuesPrism",()=>{const o=X(this);return(0,So.prism)(()=>(0,So.val)(o.getValues().getValue()))})}onValuesChange(o,c){return Eu(this._valuesPrism(),o,c)}get value(){const o=this._valuesPrism();{if(!o.isHot){this._keepHotUntapDebounce!=null&&this._keepHotUntapDebounce.flush();const c=o.keepHot();this._keepHotUntapDebounce=eS(()=>{c(),this._keepHotUntapDebounce=void 0},NS)}this._keepHotUntapDebounce&&this._keepHotUntapDebounce()}return o.getValue()}set initialValue(o){X(this).setInitialValue(o)}};function US(o){const c=new WeakMap;return d=>(c.has(d)||c.set(d,o(d)),c.get(d))}function Na(o){return o.type==="compound"||o.type==="enum"}function Jc(o,c){if(!o)return;const[d,...y]=c;if(d===void 0)return o;if(!Na(o))return;const M=o.type==="enum"?o.cases[d]:o.props[d];return Jc(M,y)}function BS(o){return!Na(o)}var kS=class{constructor(o,c,d){this.sheet=o,this.template=c,this.nativeObject=d,S(this,"$$isPointerToPrismProvider",!0),S(this,"address"),S(this,"publicApi"),S(this,"_initialValue",new Kt.Atom({})),S(this,"_cache",new ar),S(this,"_logger"),S(this,"_internalUtilCtx"),this._logger=o._logger.named("SheetObject",c.address.objectKey),this._logger._trace("creating object"),this._internalUtilCtx={logger:this._logger.utilFor.internal()},this.address=x(g({},c.address),{sheetInstanceId:o.address.sheetInstanceId}),this.publicApi=new OS(this)}get type(){return"Theatre_SheetObject"}getValues(){return this._cache.get("getValues()",()=>(0,Kt.prism)(()=>{const o=(0,Kt.val)(this.template.getDefaultValues()),c=(0,Kt.val)(this._initialValue.pointer),d=Kt.prism.memo("withInitialCache",()=>new WeakMap,[]),y=Fr(o,c,d),M=(0,Kt.val)(this.template.getStaticValues()),C=Kt.prism.memo("withStatics",()=>new WeakMap,[]);let Y=Fr(y,M,C),Q;{const xe=Kt.prism.memo("seq",()=>this.getSequencedValues(),[]),Se=Kt.prism.memo("withSeqsCache",()=>new WeakMap,[]);Q=(0,Kt.val)((0,Kt.val)(xe)),Y=Fr(Y,Q,Se)}return Ea("finalAtom",Y).pointer}))}getValueByPointer(o){const c=(0,Kt.val)(this.getValues()),{path:d}=(0,Kt.getPointerParts)(o);return(0,Kt.val)(Nr(c,d))}pointerToPrism(o){const{path:c}=(0,Kt.getPointerParts)(o);return(0,Kt.prism)(()=>{const d=(0,Kt.val)(this.getValues());return(0,Kt.val)(Nr(d,c))})}getSequencedValues(){return(0,Kt.prism)(()=>{const o=Kt.prism.memo("tracksToProcess",()=>this.template.getArrayOfValidSequenceTracks(),[]),c=(0,Kt.val)(o),d=new Kt.Atom({}),y=(0,Kt.val)(this.template.configPointer);return Kt.prism.effect("processTracks",()=>{const M=[];for(const{trackId:C,pathToProp:B}of c){const Y=this._trackIdToPrism(C),Q=Jc(y,B),se=Q.deserializeAndSanitize,xe=Q.interpolate,Se=()=>{const lt=Y.getValue();if(!lt)return d.setByPointer(Vt=>Nr(Vt,B),void 0);const Ye=se(lt.left),wt=Ye===void 0?Q.default:Ye;if(lt.right===void 0)return d.setByPointer(Vt=>Nr(Vt,B),wt);const It=se(lt.right),Mt=It===void 0?Q.default:It;return d.setByPointer(Vt=>Nr(Vt,B),xe(wt,Mt,lt.progression))},Ie=Y.onStale(Se);Se(),M.push(Ie)}return()=>{for(const C of M)C()}},[y,...c]),d.pointer})}_trackIdToPrism(o){const c=this.template.project.pointers.historic.sheetsById[this.address.sheetId].sequence.tracksByObject[this.address.objectKey].trackData[o],d=this.sheet.getSequence().positionPrism;return Tc(this._internalUtilCtx,c,d)}get propsP(){return this._cache.get("propsP",()=>(0,Kt.pointer)({root:this,path:[]}))}validateValue(o,c){}setInitialValue(o){this.validateValue(this.propsP,o),this._initialValue.set(o)}};function rn(o){return function(d,y){return o(d,y())}}var ni={_hmm:ii(524),_todo:ii(522),_error:ii(521),errorDev:ii(529),errorPublic:ii(545),_kapow:ii(268),_warn:ii(265),warnDev:ii(273),warnPublic:ii(289),_debug:ii(137),debugDev:ii(145),_trace:ii(73),traceDev:ii(81)};function ii(o){return Object.freeze({audience:kr(o,8)?"internal":kr(o,16)?"dev":"public",category:kr(o,4)?"troubleshooting":kr(o,2)?"todo":"general",level:kr(o,512)?512:kr(o,256)?256:kr(o,128)?128:64})}function kr(o,c){return(o&c)===c}function sn(o,c){return((c&32)===32?!0:(c&16)===16?o.dev:(c&8)===8?o.internal:!1)&&o.min<=c}var Hi={loggingConsoleStyle:!0,loggerConsoleStyle:!0,includes:Object.freeze({internal:!1,dev:!1,min:256}),filtered:function(){},include:function(){return{}},create:null,creatExt:null,named(o,c,d){return this.create({names:[...o.names,{name:c,key:d}]})},style:{bold:void 0,italic:void 0,cssMemo:new Map([["",""]]),collapseOnRE:/[a-z- ]+/g,color:void 0,collapsed(o){if(o.length<5)return o;const c=o.replace(this.collapseOnRE,"");return this.cssMemo.has(c)||this.cssMemo.set(c,this.css(o)),c},css(o){var c,d,y,M;const C=this.cssMemo.get(o);if(C)return C;let B="color:".concat((d=(c=this.color)==null?void 0:c.call(this,o))!=null?d:"hsl(".concat((o.charCodeAt(0)+o.charCodeAt(o.length-1))%360,", 100%, 60%)"));return(y=this.bold)!=null&&y.test(o)&&(B+=";font-weight:600"),(M=this.italic)!=null&&M.test(o)&&(B+=";font-style:italic"),this.cssMemo.set(o,B),B}}};function jf(o=console,c={}){const d=x(g({},Hi),{includes:g({},Hi.includes)}),y={styled:VS.bind(d,o),noStyle:WS.bind(d,o)},M=HS.bind(d);function C(){return d.loggingConsoleStyle&&d.loggerConsoleStyle?y.styled:y.noStyle}return d.create=C(),{configureLogger(B){var Y;B==="console"?(d.loggerConsoleStyle=Hi.loggerConsoleStyle,d.create=C()):B.type==="console"?(d.loggerConsoleStyle=(Y=B.style)!=null?Y:Hi.loggerConsoleStyle,d.create=C()):B.type==="keyed"?(d.creatExt=Q=>B.keyed(Q.names),d.create=M):B.type==="named"&&(d.creatExt=zS.bind(null,B.named),d.create=M)},configureLogging(B){var Y,Q,se,xe,Se;d.includes.dev=(Y=B.dev)!=null?Y:Hi.includes.dev,d.includes.internal=(Q=B.internal)!=null?Q:Hi.includes.internal,d.includes.min=(se=B.min)!=null?se:Hi.includes.min,d.include=(xe=B.include)!=null?xe:Hi.include,d.loggingConsoleStyle=(Se=B.consoleStyle)!=null?Se:Hi.loggingConsoleStyle,d.create=C()},getLogger(){return d.create({names:[]})}}}function zS(o,c){const d=[];for(let{name:y,key:M}of c.names)d.push(M==null?y:"".concat(y," (").concat(M,")"));return o(d)}function HS(o){const c=g(g({},this.includes),this.include(o)),d=this.filtered,y=this.named.bind(this,o),M=this.creatExt(o),C=sn(c,524),B=sn(c,522),Y=sn(c,521),Q=sn(c,529),se=sn(c,545),xe=sn(c,265),Se=sn(c,268),Ie=sn(c,273),lt=sn(c,289),Ye=sn(c,137),wt=sn(c,145),It=sn(c,73),Mt=sn(c,81),Vt=C?M.error.bind(M,ni._hmm):d.bind(o,524),On=B?M.error.bind(M,ni._todo):d.bind(o,522),$n=Y?M.error.bind(M,ni._error):d.bind(o,521),Un=Q?M.error.bind(M,ni.errorDev):d.bind(o,529),en=se?M.error.bind(M,ni.errorPublic):d.bind(o,545),Bn=Se?M.warn.bind(M,ni._kapow):d.bind(o,268),si=xe?M.warn.bind(M,ni._warn):d.bind(o,265),Ri=Ie?M.warn.bind(M,ni.warnDev):d.bind(o,273),jr=lt?M.warn.bind(M,ni.warnPublic):d.bind(o,273),Xr=Ye?M.debug.bind(M,ni._debug):d.bind(o,137),qr=wt?M.debug.bind(M,ni.debugDev):d.bind(o,145),Yr=It?M.trace.bind(M,ni._trace):d.bind(o,73),Kr=Mt?M.trace.bind(M,ni.traceDev):d.bind(o,81),gn={_hmm:Vt,_todo:On,_error:$n,errorDev:Un,errorPublic:en,_kapow:Bn,_warn:si,warnDev:Ri,warnPublic:jr,_debug:Xr,debugDev:qr,_trace:Yr,traceDev:Kr,lazy:{_hmm:C?rn(Vt):Vt,_todo:B?rn(On):On,_error:Y?rn($n):$n,errorDev:Q?rn(Un):Un,errorPublic:se?rn(en):en,_kapow:Se?rn(Bn):Bn,_warn:xe?rn(si):si,warnDev:Ie?rn(Ri):Ri,warnPublic:lt?rn(jr):jr,_debug:Ye?rn(Xr):Xr,debugDev:wt?rn(qr):qr,_trace:It?rn(Yr):Yr,traceDev:Mt?rn(Kr):Kr},named:y,utilFor:{internal(){return{debug:gn._debug,error:gn._error,warn:gn._warn,trace:gn._trace,named(oi,on){return gn.named(oi,on).utilFor.internal()}}},dev(){return{debug:gn.debugDev,error:gn.errorDev,warn:gn.warnDev,trace:gn.traceDev,named(oi,on){return gn.named(oi,on).utilFor.dev()}}},public(){return{error:gn.errorPublic,warn:gn.warnPublic,debug(oi,on){gn._warn('(public "debug" filtered out) '.concat(oi),on)},trace(oi,on){gn._warn('(public "trace" filtered out) '.concat(oi),on)},named(oi,on){return gn.named(oi,on).utilFor.public()}}}}};return gn}function VS(o,c){const d=g(g({},this.includes),this.include(c)),y=[];let M="";for(let Q=0;Q<c.names.length;Q++){const{name:se,key:xe}=c.names[Q];if(M+=" %c".concat(se),y.push(this.style.css(se)),xe!=null){const Se="%c#".concat(xe);M+=Se,y.push(this.style.css(Se))}}const C=this.filtered,B=this.named.bind(this,c),Y=[M,...y];return Xf(C,c,d,o,Y,GS(Y),B)}function GS(o){const c=o.slice(0);for(let d=1;d<c.length;d++)c[d]+=";background-color:#e0005a;padding:2px;color:white";return c}function WS(o,c){const d=g(g({},this.includes),this.include(c));let y="";for(let Y=0;Y<c.names.length;Y++){const{name:Q,key:se}=c.names[Y];y+=" ".concat(Q),se!=null&&(y+="#".concat(se))}const M=this.filtered,C=this.named.bind(this,c),B=[y];return Xf(M,c,d,o,B,B,C)}function Xf(o,c,d,y,M,C,B){const Y=sn(d,524),Q=sn(d,522),se=sn(d,521),xe=sn(d,529),Se=sn(d,545),Ie=sn(d,265),lt=sn(d,268),Ye=sn(d,273),wt=sn(d,289),It=sn(d,137),Mt=sn(d,145),Vt=sn(d,73),On=sn(d,81),$n=Y?y.error.bind(y,...M):o.bind(c,524),Un=Q?y.error.bind(y,...M):o.bind(c,522),en=se?y.error.bind(y,...M):o.bind(c,521),Bn=xe?y.error.bind(y,...M):o.bind(c,529),si=Se?y.error.bind(y,...M):o.bind(c,545),Ri=lt?y.warn.bind(y,...C):o.bind(c,268),jr=Ie?y.warn.bind(y,...M):o.bind(c,265),Xr=Ye?y.warn.bind(y,...M):o.bind(c,273),qr=wt?y.warn.bind(y,...M):o.bind(c,273),Yr=It?y.info.bind(y,...M):o.bind(c,137),Kr=Mt?y.info.bind(y,...M):o.bind(c,145),gn=Vt?y.debug.bind(y,...M):o.bind(c,73),oi=On?y.debug.bind(y,...M):o.bind(c,81),on={_hmm:$n,_todo:Un,_error:en,errorDev:Bn,errorPublic:si,_kapow:Ri,_warn:jr,warnDev:Xr,warnPublic:qr,_debug:Yr,debugDev:Kr,_trace:gn,traceDev:oi,lazy:{_hmm:Y?rn($n):$n,_todo:Q?rn(Un):Un,_error:se?rn(en):en,errorDev:xe?rn(Bn):Bn,errorPublic:Se?rn(si):si,_kapow:lt?rn(Ri):Ri,_warn:Ie?rn(jr):jr,warnDev:Ye?rn(Xr):Xr,warnPublic:wt?rn(qr):qr,_debug:It?rn(Yr):Yr,debugDev:Mt?rn(Kr):Kr,_trace:Vt?rn(gn):gn,traceDev:On?rn(oi):oi},named:B,utilFor:{internal(){return{debug:on._debug,error:on._error,warn:on._warn,trace:on._trace,named(Wi,ji){return on.named(Wi,ji).utilFor.internal()}}},dev(){return{debug:on.debugDev,error:on.errorDev,warn:on.warnDev,trace:on.traceDev,named(Wi,ji){return on.named(Wi,ji).utilFor.dev()}}},public(){return{error:on.errorPublic,warn:on.warnPublic,debug(Wi,ji){on._warn('(public "debug" filtered out) '.concat(Wi),ji)},trace(Wi,ji){on._warn('(public "trace" filtered out) '.concat(Wi),ji)},named(Wi,ji){return on.named(Wi,ji).utilFor.public()}}}}};return on}var qf=jf(console,{});qf.configureLogging({dev:!0,min:64});var Oa=qf.getLogger().named("Theatre.js (default logger)").utilFor.dev(),Yf=new WeakMap;function jS(o){const c=Yf.get(o);if(c)return c;const d=new Map;return Yf.set(o,d),Kf([],o,d),d}function Kf(o,c,d){for(const[y,M]of Object.entries(c.props))if(!Na(M)){const C=[...o,y];d.set(JSON.stringify(C),d.size),$f(C,M,d)}for(const[y,M]of Object.entries(c.props))if(Na(M)){const C=[...o,y];d.set(JSON.stringify(C),d.size),$f(C,M,d)}}function $f(o,c,d){if(c.type==="compound")Kf(o,c,d);else{if(c.type==="enum")throw new Error("Enums aren't supported yet");d.set(JSON.stringify(o),d.size)}}function Zf(o){return typeof o=="object"&&o!==null&&Object.keys(o).length===0}var XS=class{constructor(o,c,d,y,M){this.sheetTemplate=o,S(this,"address"),S(this,"type","Theatre_SheetObjectTemplate"),S(this,"_config"),S(this,"_temp_actions_atom"),S(this,"_cache",new ar),S(this,"project"),S(this,"pointerToSheetState"),S(this,"pointerToStaticOverrides"),this.address=x(g({},o.address),{objectKey:c}),this._config=new vn.Atom(y),this._temp_actions_atom=new vn.Atom(M),this.project=o.project,this.pointerToSheetState=this.sheetTemplate.project.pointers.historic.sheetsById[this.address.sheetId],this.pointerToStaticOverrides=this.pointerToSheetState.staticOverrides.byObject[this.address.objectKey]}get staticConfig(){return this._config.get()}get configPointer(){return this._config.pointer}get _temp_actions(){return this._temp_actions_atom.get()}get _temp_actionsPointer(){return this._temp_actions_atom.pointer}createInstance(o,c,d){return this._config.set(d),new kS(o,this,c)}reconfigure(o){this._config.set(o)}_temp_setActions(o){this._temp_actions_atom.set(o)}getDefaultValues(){return this._cache.get("getDefaultValues()",()=>(0,vn.prism)(()=>{const o=(0,vn.val)(this.configPointer);return Ec(o)}))}getStaticValues(){return this._cache.get("getStaticValues",()=>(0,vn.prism)(()=>{var o;const c=(o=(0,vn.val)(this.pointerToStaticOverrides))!=null?o:{};return(0,vn.val)(this.configPointer).deserializeAndSanitize(c)||{}}))}getArrayOfValidSequenceTracks(){return this._cache.get("getArrayOfValidSequenceTracks",()=>(0,vn.prism)(()=>{const o=this.project.pointers.historic.sheetsById[this.address.sheetId],c=(0,vn.val)(o.sequence.tracksByObject[this.address.objectKey].trackIdByPropPath);if(!c)return te;const d=[];if(!c)return te;const y=(0,vn.val)(this.configPointer),M=Object.entries(c);for(const[B,Y]of M){const Q=qS(B);if(!Q)continue;const se=Jc(y,Q);se&&BS(se)&&d.push({pathToProp:Q,trackId:Y})}const C=jS(y);return d.sort((B,Y)=>{const Q=B.pathToProp,se=Y.pathToProp,xe=C.get(JSON.stringify(Q)),Se=C.get(JSON.stringify(se));return xe>Se?1:-1}),d.length===0?te:d}))}getMapOfValidSequenceTracks_forStudio(){return this._cache.get("getMapOfValidSequenceTracks_forStudio",()=>(0,vn.prism)(()=>{const o=(0,vn.val)(this.getArrayOfValidSequenceTracks());let c={};for(const{pathToProp:d,trackId:y}of o)ys(c,d,y);return c}))}getStaticButNotSequencedOverrides(){return this._cache.get("getStaticButNotSequencedOverrides",()=>(0,vn.prism)(()=>{const o=(0,vn.val)(this.getStaticValues()),c=(0,vn.val)(this.getArrayOfValidSequenceTracks()),d=Rx(o);for(const{pathToProp:y}of c){Wf(d,y);let M=y.slice(0,-1);for(;M.length>0;){const C=ga(d,M);if(!Zf(C))break;Wf(d,M),M=M.slice(0,-1)}}if(!Zf(d))return d}))}getDefaultsAtPointer(o){const{path:c}=(0,vn.getPointerParts)(o),d=this.getDefaultValues().getValue();return ga(d,c)}};function qS(o){try{return JSON.parse(o)}catch{Oa.warn("property ".concat(JSON.stringify(o)," cannot be parsed. Skipping."));return}}var Qf=xn(),YS=US(o=>JSON.stringify(o));R(O());var KS=class extends Error{},Po=class extends KS{},Jf=xn(),$S=xn(),ZS=xn(),wn=xn();function cr(){let o,c;const d=new Promise((M,C)=>{o=B=>{M(B),y.status="resolved"},c=B=>{C(B),y.status="rejected"}}),y={resolve:o,reject:c,promise:d,status:"pending"};return y}var QS=()=>{},Ua=QS,JS=xn(),eE=class{constructor(){S(this,"_stopPlayCallback",Ua),S(this,"_state",new JS.Atom({position:0,playing:!1})),S(this,"statePointer"),this.statePointer=this._state.pointer}destroy(){}pause(){this._stopPlayCallback(),this.playing=!1,this._stopPlayCallback=Ua}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.setByPointer(c=>c.position,o)}getCurrentPosition(){return this._state.get().position}get playing(){return this._state.get().playing}set playing(o){this._state.setByPointer(c=>c.playing,o)}play(o,c,d,y,M){this.playing&&this.pause(),this.playing=!0;const C=c[1]-c[0];{const Ie=this.getCurrentPosition();Ie<c[0]||Ie>c[1]?y==="normal"||y==="alternate"?this._updatePositionInState(c[0]):(y==="reverse"||y==="alternateReverse")&&this._updatePositionInState(c[1]):y==="normal"||y==="alternate"?Ie===c[1]&&this._updatePositionInState(c[0]):Ie===c[0]&&this._updatePositionInState(c[1])}const B=cr(),Y=M.time,Q=C*o;let se=this.getCurrentPosition()-c[0];(y==="reverse"||y==="alternateReverse")&&(se=c[1]-this.getCurrentPosition());const xe=Ie=>{const Ye=Math.max(Ie-Y,0)/1e3,wt=Math.min(Ye*d+se,Q);if(wt!==Q){const It=Math.floor(wt/C);let Mt=wt/C%1*C;if(y!=="normal")if(y==="reverse")Mt=C-Mt;else{const Vt=It%2===0;y==="alternate"?Vt||(Mt=C-Mt):Vt&&(Mt=C-Mt)}this._updatePositionInState(Mt+c[0]),Se()}else{if(y==="normal")this._updatePositionInState(c[1]);else if(y==="reverse")this._updatePositionInState(c[0]);else{const It=(o-1)%2===0;y==="alternate"?It?this._updatePositionInState(c[1]):this._updatePositionInState(c[0]):It?this._updatePositionInState(c[0]):this._updatePositionInState(c[1])}this.playing=!1,B.resolve(!0)}};this._stopPlayCallback=()=>{M.offThisOrNextTick(xe),M.offNextTick(xe),this.playing&&B.resolve(!1)};const Se=()=>M.onNextTick(xe);return M.onThisOrNextTick(xe),B.promise}playDynamicRange(o,c){this.playing&&this.pause(),this.playing=!0;const d=cr(),y=o.keepHot();d.promise.then(y,y);let M=c.time;const C=Y=>{const Q=Math.max(Y-M,0);M=Y;const se=Q/1e3,xe=this.getCurrentPosition(),Se=o.getValue();if(xe<Se[0]||xe>Se[1])this.gotoPosition(Se[0]);else{let Ie=xe+se;Ie>Se[1]&&(Ie=Se[0]+(Ie-Se[1])),this.gotoPosition(Ie)}B()};this._stopPlayCallback=()=>{c.offThisOrNextTick(C),c.offNextTick(C),d.resolve(!1)};const B=()=>c.onNextTick(C);return c.onThisOrNextTick(C),d.promise}},tE=xn(),nE="__TheatreJS_StudioBundle",eu="__TheatreJS_CoreBundle",iE="__TheatreJS_Notifications",Ba=o=>(...c)=>{var d;switch(o){case"success":{Oa.debug(c.slice(0,2).join(`
`));break}case"info":{Oa.debug(c.slice(0,2).join(`
`));break}case"warning":{Oa.warn(c.slice(0,2).join(`
`));break}}return typeof window<"u"?(d=window[iE])==null?void 0:d.notify[o](...c):void 0},Es={warning:Ba("warning"),success:Ba("success"),info:Ba("info"),error:Ba("error")};typeof window<"u"&&(window.addEventListener("error",o=>{Es.error("An error occurred","<pre>".concat(o.message,`</pre>

See **console** for details.`))}),window.addEventListener("unhandledrejection",o=>{Es.error("An error occurred","<pre>".concat(o.reason,`</pre>

See **console** for details.`))}));var rE=class{constructor(o,c,d){this._decodedBuffer=o,this._audioContext=c,this._nodeDestination=d,S(this,"_mainGain"),S(this,"_state",new tE.Atom({position:0,playing:!1})),S(this,"statePointer"),S(this,"_stopPlayCallback",Ua),this.statePointer=this._state.pointer,this._mainGain=this._audioContext.createGain(),this._mainGain.connect(this._nodeDestination)}playDynamicRange(o,c){const d=cr();this._playing&&this.pause(),this._playing=!0;let y;const M=()=>{y==null||y(),y=this._loopInRange(o.getValue(),c).stop},C=o.onStale(M);return M(),this._stopPlayCallback=()=>{y==null||y(),C(),d.resolve(!1)},d.promise}_loopInRange(o,c){let y=this.getCurrentPosition();const M=o[1]-o[0];y<o[0]||y>o[1]?this._updatePositionInState(o[0]):y===o[1]&&this._updatePositionInState(o[0]),y=this.getCurrentPosition();const C=this._audioContext.createBufferSource();C.buffer=this._decodedBuffer,C.connect(this._mainGain),C.playbackRate.value=1,C.loop=!0,C.loopStart=o[0],C.loopEnd=o[1];const B=c.time;let Y=y-o[0];C.start(0,y);const Q=Se=>{let wt=(Math.max(Se-B,0)/1e3*1+Y)/M%1*M;this._updatePositionInState(wt+o[0]),se()},se=()=>c.onNextTick(Q);return c.onThisOrNextTick(Q),{stop:()=>{C.stop(),C.disconnect(),c.offThisOrNextTick(Q),c.offNextTick(Q)}}}get _playing(){return this._state.get().playing}set _playing(o){this._state.setByPointer(c=>c.playing,o)}destroy(){}pause(){this._stopPlayCallback(),this._playing=!1,this._stopPlayCallback=Ua}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.reduce(c=>x(g({},c),{position:o}))}getCurrentPosition(){return this._state.get().position}play(o,c,d,y,M){this._playing&&this.pause(),this._playing=!0;let C=this.getCurrentPosition();const B=c[1]-c[0];if(y!=="normal")throw new Po('Audio-controlled sequences can only be played in the "normal" direction. '+"'".concat(y,"' given."));C<c[0]||C>c[1]?this._updatePositionInState(c[0]):C===c[1]&&this._updatePositionInState(c[0]),C=this.getCurrentPosition();const Y=cr(),Q=this._audioContext.createBufferSource();Q.buffer=this._decodedBuffer,Q.connect(this._mainGain),Q.playbackRate.value=d,o>1e3&&(Es.warning("Can't play sequences with audio more than 1000 times","The sequence will still play, but only 1000 times. The `iterationCount: ".concat(o,"` provided to `sequence.play()`\nis too high for a sequence with audio.\n\nTo fix this, either set `iterationCount` to a lower value, or remove the audio from the sequence."),[{url:"https://www.theatrejs.com/docs/latest/manual/audio",title:"Using Audio"},{url:"https://www.theatrejs.com/docs/latest/api/core#sequence.attachaudio",title:"Audio API"}]),o=1e3),o>1&&(Q.loop=!0,Q.loopStart=c[0],Q.loopEnd=c[1]);const se=M.time;let xe=C-c[0];const Se=B*o;Q.start(0,C,Se-xe);const Ie=wt=>{const Mt=Math.max(wt-se,0)/1e3,Vt=Math.min(Mt*d+xe,Se);if(Vt!==Se){let On=Vt/B%1*B;this._updatePositionInState(On+c[0]),Ye()}else this._updatePositionInState(c[1]),this._playing=!1,lt(),Y.resolve(!0)},lt=()=>{Q.stop(),Q.disconnect()};this._stopPlayCallback=()=>{lt(),M.offThisOrNextTick(Ie),M.offNextTick(Ie),this._playing&&Y.resolve(!1)};const Ye=()=>M.onNextTick(Ie);return M.onThisOrNextTick(Ie),Y.promise}},sE=xn(),ep=0;function tu(o){var c;const d=B=>{y.tick(B)},y=new sE.Ticker({onActive(){var B;(B=o==null?void 0:o.start)==null||B.call(o)},onDormant(){var B;(B=o==null?void 0:o.stop)==null||B.call(o)}}),M={tick:d,id:ep++,name:(c=o==null?void 0:o.name)!=null?c:"CustomRafDriver-".concat(ep),type:"Theatre_RafDriver_PublicAPI"},C={type:"Theatre_RafDriver_PrivateAPI",publicApi:M,ticker:y,start:o==null?void 0:o.start,stop:o==null?void 0:o.stop};return he(M,C),M}function oE(){let o=null;const y=tu({name:"DefaultCoreRafDriver",start:()=>{if(typeof window<"u"){const M=C=>{y.tick(C),o=window.requestAnimationFrame(M)};o=window.requestAnimationFrame(M)}else y.tick(0),setTimeout(()=>y.tick(1),0)},stop:()=>{typeof window<"u"&&o!==null&&window.cancelAnimationFrame(o)}});return y}var ka;function tp(){return ka||aE(oE()),ka}function np(){return tp().ticker}function aE(o){if(ka)throw new Error("`setCoreRafDriver()` is already called.");ka=X(o)}var lE=class{get type(){return"Theatre_Sequence_PublicAPI"}constructor(o){he(this,o)}play(o){const c=X(this);if(c._project.isReady()){const d=o!=null&&o.rafDriver?X(o.rafDriver).ticker:np();return c.play(o??{},d)}else{const d=cr();return d.resolve(!0),d.promise}}pause(){X(this).pause()}get position(){return X(this).position}set position(o){X(this).position=o}__experimental_getKeyframes(o){return X(this).getKeyframesOfSimpleProp(o)}async attachAudio(o){const{audioContext:c,destinationNode:d,decodedBuffer:y,gainNode:M}=await cE(o),C=new rE(y,c,M);return X(this).replacePlaybackController(C),{audioContext:c,destinationNode:d,decodedBuffer:y,gainNode:M}}get pointer(){return X(this).pointer}};async function cE(o){function c(){if(o.audioContext)return Promise.resolve(o.audioContext);const se=new AudioContext;return se.state==="running"||typeof window>"u"?Promise.resolve(se):new Promise(xe=>{const Se=()=>{se.resume().catch(Ye=>{console.error(Ye)})},Ie=["mousedown","keydown","touchstart"],lt={capture:!0,passive:!1};Ie.forEach(Ye=>{window.addEventListener(Ye,Se,lt)}),se.addEventListener("statechange",()=>{se.state==="running"&&(Ie.forEach(Ye=>{window.removeEventListener(Ye,Se,lt)}),xe(se))})})}async function d(){if(o.source instanceof AudioBuffer)return o.source;const se=cr();if(typeof o.source!="string")throw new Error("Error validating arguments to sequence.attachAudio(). args.source must either be a string or an instance of AudioBuffer.");let xe;try{xe=await fetch(o.source)}catch(Ye){throw console.error(Ye),new Error("Could not fetch '".concat(o.source,"'. Network error logged above."))}let Se;try{Se=await xe.arrayBuffer()}catch(Ye){throw console.error(Ye),new Error("Could not read '".concat(o.source,"' as an arrayBuffer."))}(await y).decodeAudioData(Se,se.resolve,se.reject);let lt;try{lt=await se.promise}catch(Ye){throw console.error(Ye),new Error("Could not decode ".concat(o.source," as an audio file."))}return lt}const y=c(),M=d(),[C,B]=await Promise.all([y,M]),Y=o.destinationNode||C.destination,Q=C.createGain();return Q.connect(Y),{audioContext:C,decodedBuffer:B,gainNode:Q,destinationNode:Y}}var uE=hE("Theatre_SheetObject");function hE(o){return c=>typeof c=="object"&&!!c&&c.type===o}var dE=class{constructor(o,c,d,y,M){this._project=o,this._sheet=c,this._lengthD=d,this._subUnitsPerUnitD=y,S(this,"address"),S(this,"publicApi"),S(this,"_playbackControllerBox"),S(this,"_prismOfStatePointer"),S(this,"_positionD"),S(this,"_positionFormatterD"),S(this,"_playableRangeD"),S(this,"pointer",(0,ZS.pointer)({root:this,path:[]})),S(this,"$$isPointerToPrismProvider",!0),S(this,"_logger"),S(this,"closestGridPosition",C=>{const Y=1/this.subUnitsPerUnit;return parseFloat((Math.round(C/Y)*Y).toFixed(3))}),this._logger=o._logger.named("Sheet",c.address.sheetId).named("Instance",c.address.sheetInstanceId),this.address=x(g({},this._sheet.address),{sequenceName:"default"}),this.publicApi=new lE(this),this._playbackControllerBox=new $S.Atom(M??new eE),this._prismOfStatePointer=(0,wn.prism)(()=>this._playbackControllerBox.prism.getValue().statePointer),this._positionD=(0,wn.prism)(()=>{const C=this._prismOfStatePointer.getValue();return(0,wn.val)(C.position)}),this._positionFormatterD=(0,wn.prism)(()=>{const C=(0,wn.val)(this._subUnitsPerUnitD);return new fE(C)})}get type(){return"Theatre_Sequence"}pointerToPrism(o){const{path:c}=(0,Jf.getPointerParts)(o);if(c.length===0)return(0,wn.prism)(()=>({length:(0,wn.val)(this.pointer.length),playing:(0,wn.val)(this.pointer.playing),position:(0,wn.val)(this.pointer.position),subUnitsPerUnit:(0,wn.val)(this.pointer.subUnitsPerUnit)}));if(c.length>1)return(0,wn.prism)(()=>{});const[d]=c;return d==="length"?this._lengthD:d==="subUnitsPerUnit"?this._subUnitsPerUnitD:d==="position"?this._positionD:d==="playing"?(0,wn.prism)(()=>(0,wn.val)(this._prismOfStatePointer.getValue().playing)):(0,wn.prism)(()=>{})}getKeyframesOfSimpleProp(o){const{path:c,root:d}=(0,Jf.getPointerParts)(o);if(!uE(d))throw new Po("Argument prop must be a pointer to a SheetObject property");const y=(0,wn.val)(this._project.pointers.historic.sheetsById[this._sheet.address.sheetId].sequence.tracksByObject[d.address.objectKey]);if(!y)return[];const{trackData:M,trackIdByPropPath:C}=y,B=YS(c),Y=C[B];if(!Y)return[];const Q=M[Y];return Q?Q.keyframes:[]}get positionFormatter(){return this._positionFormatterD.getValue()}get prismOfStatePointer(){return this._prismOfStatePointer}get length(){return this._lengthD.getValue()}get positionPrism(){return this._positionD}get position(){return this._playbackControllerBox.get().getCurrentPosition()}get subUnitsPerUnit(){return this._subUnitsPerUnitD.getValue()}get positionSnappedToGrid(){return this.closestGridPosition(this.position)}set position(o){let c=o;this.pause(),c>this.length&&(c=this.length);const d=this.length;this._playbackControllerBox.get().gotoPosition(c>d?d:c)}getDurationCold(){return this._lengthD.getValue()}get playing(){return(0,wn.val)(this._playbackControllerBox.get().statePointer.playing)}_makeRangeFromSequenceTemplate(){return(0,wn.prism)(()=>[0,(0,wn.val)(this._lengthD)])}playDynamicRange(o,c){return this._playbackControllerBox.get().playDynamicRange(o,c)}async play(o,c){const d=this.length,y=o&&o.range?o.range:[0,d],M=o&&typeof o.iterationCount=="number"?o.iterationCount:1,C=o&&typeof o.rate<"u"?o.rate:1,B=o&&o.direction?o.direction:"normal";return await this._play(M,[y[0],y[1]],C,B,c)}_play(o,c,d,y,M){return this._playbackControllerBox.get().play(o,c,d,y,M)}pause(){this._playbackControllerBox.get().pause()}replacePlaybackController(o){this.pause();const c=this._playbackControllerBox.get();this._playbackControllerBox.set(o);const d=c.getCurrentPosition();c.destroy(),o.gotoPosition(d)}},fE=class{constructor(o){this._fps=o}formatSubUnitForGrid(o){const c=o%1,d=1/this._fps;return Math.round(c/d)+"f"}formatFullUnitForGrid(o){let c=o,d="";if(c>=Ms){const M=Math.floor(c/Ms);d+=M+"h",c=c%Ms}if(c>=Hr){const M=Math.floor(c/Hr);d+=M+"m",c=c%Hr}if(c>=zr){const M=Math.floor(c/zr);d+=M+"s",c=c%zr}const y=1/this._fps;if(c>=y){const M=Math.floor(c/y);d+=M+"f",c=c%y}return d.length===0?"0s":d}formatForPlayhead(o){let c=o,d="";if(c>=Ms){const M=Math.floor(c/Ms);d+=Ro(M.toString(),2,"0")+"h",c=c%Ms}if(c>=Hr){const M=Math.floor(c/Hr);d+=Ro(M.toString(),2,"0")+"m",c=c%Hr}else d.length>0&&(d+="00m");if(c>=zr){const M=Math.floor(c/zr);d+=Ro(M.toString(),2,"0")+"s",c=c%zr}else d+="00s";const y=1/this._fps;if(c>=y){const M=Math.round(c/y);d+=Ro(M.toString(),2,"0")+"f",c=c%y}else c/y>.98?(d+=Ro("1",2,"0")+"f",c=c%y):d+="00f";return d.length===0?"00s00f":d}formatBasic(o){return o.toFixed(2)+"s"}},zr=1,Hr=zr*60,Ms=Hr*60,nu={};v(nu,{boolean:()=>cp,compound:()=>ru,file:()=>bE,image:()=>EE,number:()=>lp,rgba:()=>RE,string:()=>up,stringLiteral:()=>LE});function ip(o,c){return o.length<=c?o:o.substr(0,c-3)+"..."}var pE=o=>typeof o=="string"?'string("'.concat(ip(o,10),'")'):typeof o=="number"?"number(".concat(ip(String(o),10),")"):o===null?"null":o===void 0?"undefined":typeof o=="boolean"?String(o):Array.isArray(o)?"array":typeof o=="object"?"object":"unknown",rp=pE;function mE(o,{removeAlphaIfOpaque:c=!1}={}){const d=(o.a*255|256).toString(16).slice(1),y=(o.r*255|256).toString(16).slice(1)+(o.g*255|256).toString(16).slice(1)+(o.b*255|256).toString(16).slice(1)+(c&&d==="ff"?"":d);return"#".concat(y)}function iu(o){return x(g({},o),{toString(){return mE(this,{removeAlphaIfOpaque:!0})}})}function gE(o){return Object.fromEntries(Object.entries(o).map(([c,d])=>[c,rf(d,0,1)]))}function _E(o){function c(d){return d>=.0031308?1.055*d**(1/2.4)-.055:12.92*d}return gE({r:c(o.r),g:c(o.g),b:c(o.b),a:o.a})}function sp(o){function c(d){return d>=.04045?((d+.055)/(1+.055))**2.4:d/12.92}return{r:c(o.r),g:c(o.g),b:c(o.b),a:o.a}}function op(o){let c=.4122214708*o.r+.5363325363*o.g+.0514459929*o.b,d=.2119034982*o.r+.6806995451*o.g+.1073969566*o.b,y=.0883024619*o.r+.2817188376*o.g+.6299787005*o.b,M=Math.cbrt(c),C=Math.cbrt(d),B=Math.cbrt(y);return{L:.2104542553*M+.793617785*C-.0040720468*B,a:1.9779984951*M-2.428592205*C+.4505937099*B,b:.0259040371*M+.7827717662*C-.808675766*B,alpha:o.a}}function vE(o){let c=o.L+.3963377774*o.a+.2158037573*o.b,d=o.L-.1055613458*o.a-.0638541728*o.b,y=o.L-.0894841775*o.a-1.291485548*o.b,M=c*c*c,C=d*d*d,B=y*y*y;return{r:4.0767416621*M-3.3077115913*C+.2309699292*B,g:-1.2684380046*M+2.6097574011*C-.3413193965*B,b:-.0041960863*M-.7034186147*C+1.707614701*B,a:o.alpha}}var Vi=Symbol("TheatrePropType_Basic");function ap(o){return typeof o=="object"&&!!o&&o[Vi]==="TheatrePropType"}function yE(o){if(typeof o=="number")return lp(o);if(typeof o=="boolean")return cp(o);if(typeof o=="string")return up(o);if(typeof o=="object"&&o){if(ap(o))return o;if(N0(o))return ru(o);throw new Po("This value is not a valid prop type: ".concat(rp(o)))}else throw new Po("This value is not a valid prop type: ".concat(rp(o)))}function xE(o){const c={};for(const d of Object.keys(o)){const y=o[d];ap(y)?c[d]=y:c[d]=yE(y)}return c}var ru=(o,c={})=>{const d=xE(o),y=new WeakMap;return{type:"compound",props:d,valueType:null,[Vi]:"TheatrePropType",label:c.label,default:lS(d,C=>C.default),deserializeAndSanitize:C=>{if(typeof C!="object"||!C)return;if(y.has(C))return y.get(C);const B={};let Y=!1;for(const[Q,se]of Object.entries(d))if(Object.prototype.hasOwnProperty.call(C,Q)){const xe=se.deserializeAndSanitize(C[Q]);xe!=null&&(Y=!0,B[Q]=xe)}if(y.set(C,B),Y)return B}}},bE=(o,c={})=>{const d=(y,M,C)=>{var B;return{type:"file",id:((B=c.interpolate)!=null?B:Co)(y.id,M.id,C)}};return{type:"file",default:{type:"file",id:o},valueType:null,[Vi]:"TheatrePropType",label:c.label,interpolate:d,deserializeAndSanitize:SE}},SE=o=>{if(!o)return;let c=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(c=!1),o.type!=="file"&&(c=!1),!!c)return o},EE=(o,c={})=>{const d=(y,M,C)=>{var B;return{type:"image",id:((B=c.interpolate)!=null?B:Co)(y.id,M.id,C)}};return{type:"image",default:{type:"image",id:o},valueType:null,[Vi]:"TheatrePropType",label:c.label,interpolate:d,deserializeAndSanitize:ME}},ME=o=>{if(!o)return;let c=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(c=!1),o.type!=="image"&&(c=!1),!!c)return o},lp=(o,c={})=>{var d;return x(g({type:"number",valueType:0,default:o,[Vi]:"TheatrePropType"},c||{}),{label:c.label,nudgeFn:(d=c.nudgeFn)!=null?d:FE,nudgeMultiplier:typeof c.nudgeMultiplier=="number"?c.nudgeMultiplier:void 0,interpolate:AE,deserializeAndSanitize:TE(c.range)})},TE=o=>o?c=>{if(typeof c=="number"&&isFinite(c))return rf(c,o[0],o[1])}:wE,wE=o=>typeof o=="number"&&isFinite(o)?o:void 0,AE=(o,c,d)=>o+d*(c-o),RE=(o={r:0,g:0,b:0,a:1},c={})=>{const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return{type:"rgba",valueType:null,default:iu(d),[Vi]:"TheatrePropType",label:c.label,interpolate:CE,deserializeAndSanitize:PE}},PE=o=>{if(!o)return;let c=!0;for(const y of["r","g","b","a"])(!Object.prototype.hasOwnProperty.call(o,y)||typeof o[y]!="number")&&(c=!1);if(!c)return;const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return iu(d)},CE=(o,c,d)=>{const y=op(sp(o)),M=op(sp(c)),C={L:(1-d)*y.L+d*M.L,a:(1-d)*y.a+d*M.a,b:(1-d)*y.b+d*M.b,alpha:(1-d)*y.alpha+d*M.alpha},B=_E(vE(C));return iu(B)},cp=(o,c={})=>{var d;return{type:"boolean",default:o,valueType:null,[Vi]:"TheatrePropType",label:c.label,interpolate:(d=c.interpolate)!=null?d:Co,deserializeAndSanitize:DE}},DE=o=>typeof o=="boolean"?o:void 0;function Co(o){return o}var up=(o,c={})=>{var d;return{type:"string",default:o,valueType:null,[Vi]:"TheatrePropType",label:c.label,interpolate:(d=c.interpolate)!=null?d:Co,deserializeAndSanitize:IE}};function IE(o){return typeof o=="string"?o:void 0}function LE(o,c,d={}){var y,M;return{type:"stringLiteral",default:o,valuesAndLabels:g({},c),[Vi]:"TheatrePropType",valueType:null,as:(y=d.as)!=null?y:"menu",label:d.label,interpolate:(M=d.interpolate)!=null?M:Co,deserializeAndSanitize(C){if(typeof C=="string"&&Object.prototype.hasOwnProperty.call(c,C))return C}}}var FE=({config:o,deltaX:c,deltaFraction:d,magnitude:y})=>{var M;const{range:C}=o;return!o.nudgeMultiplier&&C&&!C.includes(1/0)&&!C.includes(-1/0)?d*(C[1]-C[0])*y:c*y*((M=o.nudgeMultiplier)!=null?M:1)},NE=o=>o.replace(/^[\s\/]*/,"").replace(/[\s\/]*$/,"").replace(/\s*\/\s*/g," / ");function za(o,c){return NE(o)}R(H());var OE=class{get type(){return"Theatre_Sheet_PublicAPI"}constructor(o){he(this,o)}object(o,c,d){const y=X(this),M=za(o),C=y.getObject(M),B=null,Y=d==null?void 0:d.__actions__THIS_API_IS_UNSTABLE_AND_WILL_CHANGE_IN_THE_NEXT_VERSION;if(C)return Y&&C.template._temp_setActions(Y),C.publicApi;{const Q=ru(c);return y.createObject(M,B,Q,Y).publicApi}}__experimental_getExistingObject(o){const c=X(this),d=za(o),y=c.getObject(d);return y==null?void 0:y.publicApi}get sequence(){return X(this).getSequence().publicApi}get project(){return X(this).project.publicApi}get address(){return g({},X(this).address)}detachObject(o){const c=X(this),d=za(o);if(!c.getObject(d)){Es.warning(`Couldn't delete object "`.concat(d,'"'),'There is no object with key "'.concat(d,`".

To fix this, make sure you are calling \`sheet.deleteObject("`).concat(d,'")` with the correct key.')),console.warn('Object key "'.concat(d,'" does not exist.'));return}c.deleteObject(d)}},Do=xn(),UE=class{constructor(o,c){this.template=o,this.instanceId=c,S(this,"_objects",new Do.Atom({})),S(this,"_sequence"),S(this,"address"),S(this,"publicApi"),S(this,"project"),S(this,"objectsP",this._objects.pointer),S(this,"type","Theatre_Sheet"),S(this,"_logger"),this._logger=o.project._logger.named("Sheet",c),this._logger._trace("creating sheet"),this.project=o.project,this.address=x(g({},o.address),{sheetInstanceId:this.instanceId}),this.publicApi=new OE(this)}createObject(o,c,d,y={}){const C=this.template.getObjectTemplate(o,c,d,y).createInstance(this,c,d);return this._objects.setByPointer(B=>B[o],C),C}getObject(o){return this._objects.get()[o]}deleteObject(o){this._objects.reduce(c=>{const d=g({},c);return delete d[o],d})}getSequence(){if(!this._sequence){const o=(0,Do.prism)(()=>{const d=(0,Do.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.length);return BE(d)}),c=(0,Do.prism)(()=>{const d=(0,Do.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.subUnitsPerUnit);return kE(d)});this._sequence=new dE(this.template.project,this,o,c)}return this._sequence}},BE=o=>typeof o=="number"&&isFinite(o)&&o>0?o:10,kE=o=>typeof o=="number"&&oS(o)&&o>=1&&o<=1e3?o:30,zE=class{constructor(o,c){this.project=o,S(this,"type","Theatre_SheetTemplate"),S(this,"address"),S(this,"_instances",new Qf.Atom({})),S(this,"instancesP",this._instances.pointer),S(this,"_objectTemplates",new Qf.Atom({})),S(this,"objectTemplatesP",this._objectTemplates.pointer),this.address=x(g({},o.address),{sheetId:c})}getInstance(o){let c=this._instances.get()[o];return c||(c=new UE(this,o),this._instances.setByPointer(d=>d[o],c)),c}getObjectTemplate(o,c,d,y){let M=this._objectTemplates.get()[o];return M||(M=new XS(this,o,c,d,y),this._objectTemplates.setByPointer(C=>C[o],M)),M}},su=xn(),hp=xn(),HE=o=>new Promise(c=>setTimeout(c,o)),VE=HE;function hi(o){for(var c=arguments.length,d=Array(c>1?c-1:0),y=1;y<c;y++)d[y-1]=arguments[y];throw Error("[Immer] minified error nr: "+o+(d.length?" "+d.map(function(M){return"'"+M+"'"}).join(","):"")+". Find the full error at: https://bit.ly/3cXEKWf")}function Vr(o){return!!o&&!!o[Kn]}function Gr(o){return!!o&&((function(c){if(!c||typeof c!="object")return!1;var d=Object.getPrototypeOf(c);if(d===null)return!0;var y=Object.hasOwnProperty.call(d,"constructor")&&d.constructor;return y===Object||typeof y=="function"&&Function.toString.call(y)===ZE})(o)||Array.isArray(o)||!!o[bp]||!!o.constructor[bp]||au(o)||lu(o))}function GE(o){return Vr(o)||hi(23,o),o[Kn].t}function Io(o,c,d){d===void 0&&(d=!1),Ts(o)===0?(d?Object.keys:xu)(o).forEach(function(y){d&&typeof y=="symbol"||c(y,o[y],o)}):o.forEach(function(y,M){return c(M,y,o)})}function Ts(o){var c=o[Kn];return c?c.i>3?c.i-4:c.i:Array.isArray(o)?1:au(o)?2:lu(o)?3:0}function ou(o,c){return Ts(o)===2?o.has(c):Object.prototype.hasOwnProperty.call(o,c)}function WE(o,c){return Ts(o)===2?o.get(c):o[c]}function dp(o,c,d){var y=Ts(o);y===2?o.set(c,d):y===3?(o.delete(c),o.add(d)):o[c]=d}function jE(o,c){return o===c?o!==0||1/o==1/c:o!=o&&c!=c}function au(o){return KE&&o instanceof Map}function lu(o){return $E&&o instanceof Set}function Wr(o){return o.o||o.t}function cu(o){if(Array.isArray(o))return Array.prototype.slice.call(o);var c=QE(o);delete c[Kn];for(var d=xu(c),y=0;y<d.length;y++){var M=d[y],C=c[M];C.writable===!1&&(C.writable=!0,C.configurable=!0),(C.get||C.set)&&(c[M]={configurable:!0,writable:!0,enumerable:C.enumerable,value:o[M]})}return Object.create(Object.getPrototypeOf(o),c)}function uu(o,c){return c===void 0&&(c=!1),hu(o)||Vr(o)||!Gr(o)||(Ts(o)>1&&(o.set=o.add=o.clear=o.delete=XE),Object.freeze(o),c&&Io(o,function(d,y){return uu(y,!0)},!0)),o}function XE(){hi(2)}function hu(o){return o==null||typeof o!="object"||Object.isFrozen(o)}function Gi(o){var c=JE[o];return c||hi(18,o),c}function fp(){return Lo}function du(o,c){c&&(Gi("Patches"),o.u=[],o.s=[],o.v=c)}function Ha(o){fu(o),o.p.forEach(qE),o.p=null}function fu(o){o===Lo&&(Lo=o.l)}function pp(o){return Lo={p:[],l:Lo,h:o,m:!0,_:0}}function qE(o){var c=o[Kn];c.i===0||c.i===1?c.j():c.O=!0}function pu(o,c){c._=c.p.length;var d=c.p[0],y=o!==void 0&&o!==d;return c.h.g||Gi("ES5").S(c,o,y),y?(d[Kn].P&&(Ha(c),hi(4)),Gr(o)&&(o=Va(c,o),c.l||Ga(c,o)),c.u&&Gi("Patches").M(d[Kn],o,c.u,c.s)):o=Va(c,d,[]),Ha(c),c.u&&c.v(c.u,c.s),o!==xp?o:void 0}function Va(o,c,d){if(hu(c))return c;var y=c[Kn];if(!y)return Io(c,function(C,B){return mp(o,y,c,C,B,d)},!0),c;if(y.A!==o)return c;if(!y.P)return Ga(o,y.t,!0),y.t;if(!y.I){y.I=!0,y.A._--;var M=y.i===4||y.i===5?y.o=cu(y.k):y.o;Io(y.i===3?new Set(M):M,function(C,B){return mp(o,y,M,C,B,d)}),Ga(o,M,!1),d&&o.u&&Gi("Patches").R(y,d,o.u,o.s)}return y.o}function mp(o,c,d,y,M,C){if(Vr(M)){var B=Va(o,M,C&&c&&c.i!==3&&!ou(c.D,y)?C.concat(y):void 0);if(dp(d,y,B),!Vr(B))return;o.m=!1}if(Gr(M)&&!hu(M)){if(!o.h.F&&o._<1)return;Va(o,M),c&&c.A.l||Ga(o,M)}}function Ga(o,c,d){d===void 0&&(d=!1),o.h.F&&o.m&&uu(c,d)}function mu(o,c){var d=o[Kn];return(d?Wr(d):o)[c]}function gp(o,c){if(c in o)for(var d=Object.getPrototypeOf(o);d;){var y=Object.getOwnPropertyDescriptor(d,c);if(y)return y;d=Object.getPrototypeOf(d)}}function gu(o){o.P||(o.P=!0,o.l&&gu(o.l))}function _u(o){o.o||(o.o=cu(o.t))}function vu(o,c,d){var y=au(c)?Gi("MapSet").N(c,d):lu(c)?Gi("MapSet").T(c,d):o.g?(function(M,C){var B=Array.isArray(M),Y={i:B?1:0,A:C?C.A:fp(),P:!1,I:!1,D:{},l:C,t:M,k:null,o:null,j:null,C:!1},Q=Y,se=Wa;B&&(Q=[Y],se=ja);var xe=Proxy.revocable(Q,se),Se=xe.revoke,Ie=xe.proxy;return Y.k=Ie,Y.j=Se,Ie})(c,d):Gi("ES5").J(c,d);return(d?d.A:fp()).p.push(y),y}function YE(o){return Vr(o)||hi(22,o),(function c(d){if(!Gr(d))return d;var y,M=d[Kn],C=Ts(d);if(M){if(!M.P&&(M.i<4||!Gi("ES5").K(M)))return M.t;M.I=!0,y=_p(d,C),M.I=!1}else y=_p(d,C);return Io(y,function(B,Y){M&&WE(M.t,B)===Y||dp(y,B,c(Y))}),C===3?new Set(y):y})(o)}function _p(o,c){switch(c){case 2:return new Map(o);case 3:return Array.from(o)}return cu(o)}var vp,Lo,yu=typeof Symbol<"u"&&typeof Symbol("x")=="symbol",KE=typeof Map<"u",$E=typeof Set<"u",yp=typeof Proxy<"u"&&Proxy.revocable!==void 0&&typeof Reflect<"u",xp=yu?Symbol.for("immer-nothing"):((vp={})["immer-nothing"]=!0,vp),bp=yu?Symbol.for("immer-draftable"):"__$immer_draftable",Kn=yu?Symbol.for("immer-state"):"__$immer_state",ZE=""+Object.prototype.constructor,xu=typeof Reflect<"u"&&Reflect.ownKeys?Reflect.ownKeys:Object.getOwnPropertySymbols!==void 0?function(o){return Object.getOwnPropertyNames(o).concat(Object.getOwnPropertySymbols(o))}:Object.getOwnPropertyNames,QE=Object.getOwnPropertyDescriptors||function(o){var c={};return xu(o).forEach(function(d){c[d]=Object.getOwnPropertyDescriptor(o,d)}),c},JE={},Wa={get:function(o,c){if(c===Kn)return o;var d=Wr(o);if(!ou(d,c))return(function(M,C,B){var Y,Q=gp(C,B);return Q?"value"in Q?Q.value:(Y=Q.get)===null||Y===void 0?void 0:Y.call(M.k):void 0})(o,d,c);var y=d[c];return o.I||!Gr(y)?y:y===mu(o.t,c)?(_u(o),o.o[c]=vu(o.A.h,y,o)):y},has:function(o,c){return c in Wr(o)},ownKeys:function(o){return Reflect.ownKeys(Wr(o))},set:function(o,c,d){var y=gp(Wr(o),c);if(y!=null&&y.set)return y.set.call(o.k,d),!0;if(!o.P){var M=mu(Wr(o),c),C=M==null?void 0:M[Kn];if(C&&C.t===d)return o.o[c]=d,o.D[c]=!1,!0;if(jE(d,M)&&(d!==void 0||ou(o.t,c)))return!0;_u(o),gu(o)}return o.o[c]===d&&typeof d!="number"&&(d!==void 0||c in o.o)||(o.o[c]=d,o.D[c]=!0,!0)},deleteProperty:function(o,c){return mu(o.t,c)!==void 0||c in o.t?(o.D[c]=!1,_u(o),gu(o)):delete o.D[c],o.o&&delete o.o[c],!0},getOwnPropertyDescriptor:function(o,c){var d=Wr(o),y=Reflect.getOwnPropertyDescriptor(d,c);return y&&{writable:!0,configurable:o.i!==1||c!=="length",enumerable:y.enumerable,value:d[c]}},defineProperty:function(){hi(11)},getPrototypeOf:function(o){return Object.getPrototypeOf(o.t)},setPrototypeOf:function(){hi(12)}},ja={};Io(Wa,function(o,c){ja[o]=function(){return arguments[0]=arguments[0][0],c.apply(this,arguments)}}),ja.deleteProperty=function(o,c){return Wa.deleteProperty.call(this,o[0],c)},ja.set=function(o,c,d){return Wa.set.call(this,o[0],c,d,o[0])};var eM=(function(){function o(d){var y=this;this.g=yp,this.F=!0,this.produce=function(M,C,B){if(typeof M=="function"&&typeof C!="function"){var Y=C;C=M;var Q=y;return function(lt){var Ye=this;lt===void 0&&(lt=Y);for(var wt=arguments.length,It=Array(wt>1?wt-1:0),Mt=1;Mt<wt;Mt++)It[Mt-1]=arguments[Mt];return Q.produce(lt,function(Vt){var On;return(On=C).call.apply(On,[Ye,Vt].concat(It))})}}var se;if(typeof C!="function"&&hi(6),B!==void 0&&typeof B!="function"&&hi(7),Gr(M)){var xe=pp(y),Se=vu(y,M,void 0),Ie=!0;try{se=C(Se),Ie=!1}finally{Ie?Ha(xe):fu(xe)}return typeof Promise<"u"&&se instanceof Promise?se.then(function(lt){return du(xe,B),pu(lt,xe)},function(lt){throw Ha(xe),lt}):(du(xe,B),pu(se,xe))}if(!M||typeof M!="object")return(se=C(M))===xp?void 0:(se===void 0&&(se=M),y.F&&uu(se,!0),se);hi(21,M)},this.produceWithPatches=function(M,C){return typeof M=="function"?function(Q){for(var se=arguments.length,xe=Array(se>1?se-1:0),Se=1;Se<se;Se++)xe[Se-1]=arguments[Se];return y.produceWithPatches(Q,function(Ie){return M.apply(void 0,[Ie].concat(xe))})}:[y.produce(M,C,function(Q,se){B=Q,Y=se}),B,Y];var B,Y},typeof(d==null?void 0:d.useProxies)=="boolean"&&this.setUseProxies(d.useProxies),typeof(d==null?void 0:d.autoFreeze)=="boolean"&&this.setAutoFreeze(d.autoFreeze)}var c=o.prototype;return c.createDraft=function(d){Gr(d)||hi(8),Vr(d)&&(d=YE(d));var y=pp(this),M=vu(this,d,void 0);return M[Kn].C=!0,fu(y),M},c.finishDraft=function(d,y){var M=d&&d[Kn],C=M.A;return du(C,y),pu(void 0,C)},c.setAutoFreeze=function(d){this.F=d},c.setUseProxies=function(d){d&&!yp&&hi(20),this.g=d},c.applyPatches=function(d,y){var M;for(M=y.length-1;M>=0;M--){var C=y[M];if(C.path.length===0&&C.op==="replace"){d=C.value;break}}var B=Gi("Patches").$;return Vr(d)?B(d,y):this.produce(d,function(Y){return B(Y,y.slice(M+1))})},o})(),ri=new eM;ri.produce,ri.produceWithPatches.bind(ri),ri.setAutoFreeze.bind(ri),ri.setUseProxies.bind(ri),ri.applyPatches.bind(ri),ri.createDraft.bind(ri),ri.finishDraft.bind(ri);var tM={currentProjectStateDefinitionVersion:"0.4.0"},bu=tM;async function nM(o,c,d){await VE(0),o.transaction(({drafts:y})=>{var M;const C=c.address.projectId;y.ephemeral.coreByProject[C]={lastExportedObject:null,loadingState:{type:"loading"}},y.ahistoric.coreByProject[C]={ahistoricStuff:""};function B(){y.ephemeral.coreByProject[C].loadingState={type:"loaded"},y.historic.coreByProject[C]={sheetsById:{},definitionVersion:bu.currentProjectStateDefinitionVersion,revisionHistory:[]}}function Y(Se){y.ephemeral.coreByProject[C].loadingState={type:"loaded"},y.historic.coreByProject[C]=Se}function Q(){y.ephemeral.coreByProject[C].loadingState={type:"loaded"}}function se(Se){y.ephemeral.coreByProject[C].loadingState={type:"browserStateIsNotBasedOnDiskState",onDiskState:Se}}const xe=(M=GE(y.historic))==null?void 0:M.coreByProject[c.address.projectId];xe?d&&xe.revisionHistory.indexOf(d.revisionHistory[0])==-1?se(d):Q():d?Y(d):B()})}function Sp(){}function Ep(o){var c,d;const y=(c=o==null?void 0:o.logging)!=null&&c.internal?(d=o.logging.min)!=null?d:256:1/0,M=y<=128,C=y<=512,B=jf(void 0,{_debug:M?console.debug.bind(console,"_coreLogger(TheatreInternalLogger) debug"):Sp,_error:C?console.error.bind(console,"_coreLogger(TheatreInternalLogger) error"):Sp});if(o){const{logger:Y,logging:Q}=o;Y&&B.configureLogger(Y),Q?B.configureLogging(Q):B.configureLogging({dev:!1})}return B.getLogger().named("Theatre")}var iM=class{constructor(o,c={},d){this.config=c,this.publicApi=d,S(this,"pointers"),S(this,"_pointerProxies"),S(this,"address"),S(this,"_studioReadyDeferred"),S(this,"_assetStorageReadyDeferred"),S(this,"_readyPromise"),S(this,"_sheetTemplates",new hp.Atom({})),S(this,"sheetTemplatesP",this._sheetTemplates.pointer),S(this,"_studio"),S(this,"assetStorage"),S(this,"type","Theatre_Project"),S(this,"_logger");var y;this._logger=Ep({logging:{dev:!0}}).named("Project",o),this._logger.traceDev("creating project"),this.address={projectId:o};const M=new hp.Atom({ahistoric:{ahistoricStuff:""},historic:(y=c.state)!=null?y:{sheetsById:{},definitionVersion:bu.currentProjectStateDefinitionVersion,revisionHistory:[]},ephemeral:{loadingState:{type:"loaded"},lastExportedObject:null}});this._assetStorageReadyDeferred=cr(),this.assetStorage={getAssetUrl:C=>{var B;return"".concat((B=c.assets)==null?void 0:B.baseUrl,"/").concat(C)},createAsset:()=>{throw new Error("Please wait for Project.ready to use assets.")}},this._pointerProxies={historic:new su.PointerProxy(M.pointer.historic),ahistoric:new su.PointerProxy(M.pointer.ahistoric),ephemeral:new su.PointerProxy(M.pointer.ephemeral)},this.pointers={historic:this._pointerProxies.historic.pointer,ahistoric:this._pointerProxies.ahistoric.pointer,ephemeral:this._pointerProxies.ephemeral.pointer},ie.add(o,this),this._studioReadyDeferred=cr(),this._readyPromise=Promise.all([this._studioReadyDeferred.promise,this._assetStorageReadyDeferred.promise]).then(()=>{}),c.state?setTimeout(()=>{this._studio||(this._studioReadyDeferred.resolve(void 0),this._assetStorageReadyDeferred.resolve(void 0),this._logger._trace("ready deferred resolved with no state"))},0):typeof window>"u"?console.error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. ')+"You can safely ignore this message if you're developing a Next.js/Remix project in development mode. But if you are shipping to your end-users, then you need to set config.state, otherwise your project's state will be empty and nothing will animate. Learn more at https://www.theatrejs.com/docs/latest/manual/projects#state"):setTimeout(()=>{if(!this._studio)throw new Error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. This is fine ')+"while you are using @theatre/core along with @theatre/studio. But since @theatre/studio "+'is not loaded, the state of project "'.concat(o,`" will be empty.

`)+`To fix this, you need to add @theatre/studio into the bundle and export the project's state. Learn how to do that at https://www.theatrejs.com/docs/latest/manual/projects#state
`)},1e3)}attachToStudio(o){if(this._studio){if(this._studio!==o)throw new Error("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));console.warn("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));return}this._studio=o,o.initialized.then(async()=>{var c;await nM(o,this,this.config.state),this._pointerProxies.historic.setPointer(o.atomP.historic.coreByProject[this.address.projectId]),this._pointerProxies.ahistoric.setPointer(o.atomP.ahistoric.coreByProject[this.address.projectId]),this._pointerProxies.ephemeral.setPointer(o.atomP.ephemeral.coreByProject[this.address.projectId]),await o.createAssetStorage(this,(c=this.config.assets)==null?void 0:c.baseUrl).then(d=>{this.assetStorage=d,this._assetStorageReadyDeferred.resolve(void 0)}),this._studioReadyDeferred.resolve(void 0)}).catch(c=>{throw console.error(c),c})}get isAttachedToStudio(){return!!this._studio}get ready(){return this._readyPromise}isReady(){return this._studioReadyDeferred.status==="resolved"&&this._assetStorageReadyDeferred.status==="resolved"}getOrCreateSheet(o,c="default"){let d=this._sheetTemplates.get()[o];return d||(d=new zE(this,o),this._sheetTemplates.reduce(y=>x(g({},y),{[o]:d}))),d.getInstance(c)}},rM=class{get type(){return"Theatre_Project_PublicAPI"}constructor(o,c={}){he(this,new iM(o,c,this))}get ready(){return X(this).ready}get isReady(){return X(this).isReady()}get address(){return g({},X(this).address)}getAssetUrl(o){if(!this.isReady){console.error("Calling `project.getAssetUrl()` before `project.ready` is resolved, will always return `undefined`. Either use `project.ready.then(() => project.getAssetUrl())` or `await project.ready` before calling `project.getAssetUrl()`.");return}return o.id?X(this).assetStorage.getAssetUrl(o.id):void 0}sheet(o,c="default"){const d=za(o);return X(this).getOrCreateSheet(d,c).publicApi}};R(H());var Mp=xn(),Su=xn();function Tp(o,c={}){const d=ie.get(o);if(d)return d.publicApi;const M=Ep().named("Project",o);return c.state?(oM(o,c.state),M._debug("deep validated config.state on disk")):M._debug("no config.state"),new rM(o,c)}var sM=(o,c)=>{if(Array.isArray(c)||c==null||c.definitionVersion!==bu.currentProjectStateDefinitionVersion)throw new Po("Error validating conf.state in Theatre.getProject(".concat(JSON.stringify(o),", conf). The state seems to be formatted in a way that is unreadable to Theatre.js. Read more at https://www.theatrejs.com/docs/latest/manual/projects#state"))},oM=(o,c)=>{sM(o,c)};function Eu(o,c,d){const y=d?X(d).ticker:np();if((0,Mp.isPointer)(o))return(0,Su.pointerToPrism)(o).onChange(y,c,!0);if((0,Su.isPrism)(o))return o.onChange(y,c,!0);throw new Error("Called onChange(p) where p is neither a pointer nor a prism.")}function wp(o){if((0,Mp.isPointer)(o))return(0,Su.pointerToPrism)(o).getValue();throw new Error("Called val(p) where p is not a pointer.")}var aM=class{constructor(){S(this,"_studio")}get type(){return"Theatre_CoreBundle"}get version(){return"0.7.2"}getBitsForStudio(o,c){if(this._studio)throw new Error("@theatre/core is already attached to @theatre/studio");this._studio=o;const d={projectsP:ie.atom.pointer.projects,privateAPI:X,coreExports:A,getCoreRafDriver:tp};c(d)}};lM();function lM(){if(typeof window>"u")return;const o=window[eu];if(typeof o<"u")throw typeof o=="object"&&o&&typeof o.version=="string"?new Error(`It seems that the module '@theatre/core' is loaded more than once. This could have two possible causes:
1. You might have two separate versions of Theatre.js in node_modules.
2. Or this might be a bundling misconfiguration, in case you're using a bundler like Webpack/ESBuild/Rollup.

Note that it **is okay** to import '@theatre/core' multiple times. But those imports should point to the same module.`):new Error("The variable window.".concat(eu," seems to be already set by a module other than @theatre/core."));const c=new aM;window[eu]=c;const d=window[nE];d&&d!==null&&d.type==="Theatre_StudioBundle"&&d.registerCoreBundle(c)}/*! Bundled license information:

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
		*/})($o,$o.exports)),$o.exports}var fn=UC();let ch=null,od=null;const r_=new Map;function BC(){return ch=fn.getProject("HumanBody Theatre"),od=ch.sheet("Main"),{project:ch,sheet:od}}function Ld(){return od}function kC(r,e){const t=r.object("Camera",{position:fn.types.compound({x:fn.types.number(e.position.x,{range:[-50,50]}),y:fn.types.number(e.position.y,{range:[-10,20]}),z:fn.types.number(e.position.z,{range:[-50,50]})}),fov:fn.types.number(e.fov,{range:[10,120]})});return t.onValuesChange(n=>{e.position.set(n.position.x,n.position.y,n.position.z),e.fov=n.fov,e.updateProjectionMatrix()}),r_.set("Camera",t),t}function Ml(r,e,t){const n={position:fn.types.compound({x:fn.types.number(t.position.x,{range:[-20,20]}),y:fn.types.number(t.position.y,{range:[0,20]}),z:fn.types.number(t.position.z,{range:[-20,20]})}),intensity:fn.types.number(t.intensity,{range:[0,100]}),color:fn.types.rgba({r:t.color.r,g:t.color.g,b:t.color.b,a:1})},i=r.object(e,n);return i.onValuesChange(s=>{t.position.set(s.position.x,s.position.y,s.position.z),t.intensity=s.intensity,t.color.setRGB(s.color.r,s.color.g,s.color.b)}),r_.set(e,i),i}function Fd(r,e,t){const n=r.object(e,{position:fn.types.compound({x:fn.types.number(t.position.x,{range:[-20,20]}),y:fn.types.number(t.position.y,{range:[-5,10]}),z:fn.types.number(t.position.z,{range:[-20,20]})}),rotation:fn.types.compound({x:fn.types.number(0,{range:[-180,180]}),y:fn.types.number(0,{range:[-180,180]}),z:fn.types.number(0,{range:[-180,180]})}),scale:fn.types.number(1,{range:[.01,10]})});return n.onValuesChange(i=>{t.position.set(i.position.x,i.position.y,i.position.z),t.rotation.set(i.rotation.x*Math.PI/180,i.rotation.y*Math.PI/180,i.rotation.z*Math.PI/180),t.scale.setScalar(i.scale)}),n}function sg(r,e){if(e===VM)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),r;if(e===ed||e===Tg){let t=r.getIndex();if(t===null){const a=[],l=r.getAttribute("position");if(l!==void 0){for(let u=0;u<l.count;u++)a.push(u);r.setIndex(a),t=r.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),r}const n=t.count-2,i=[];if(e===ed)for(let a=1;a<=n;a++)i.push(t.getX(0)),i.push(t.getX(a)),i.push(t.getX(a+1));else for(let a=0;a<n;a++)a%2===0?(i.push(t.getX(a)),i.push(t.getX(a+1)),i.push(t.getX(a+2))):(i.push(t.getX(a+2)),i.push(t.getX(a+1)),i.push(t.getX(a)));i.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const s=r.clone();return s.setIndex(i),s.clearGroups(),s}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),r}class zC extends ds{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new jC(t)}),this.register(function(t){return new XC(t)}),this.register(function(t){return new tD(t)}),this.register(function(t){return new nD(t)}),this.register(function(t){return new iD(t)}),this.register(function(t){return new YC(t)}),this.register(function(t){return new KC(t)}),this.register(function(t){return new $C(t)}),this.register(function(t){return new ZC(t)}),this.register(function(t){return new WC(t)}),this.register(function(t){return new QC(t)}),this.register(function(t){return new qC(t)}),this.register(function(t){return new eD(t)}),this.register(function(t){return new JC(t)}),this.register(function(t){return new VC(t)}),this.register(function(t){return new rD(t)}),this.register(function(t){return new sD(t)})}load(e,t,n,i){const s=this;let a;if(this.resourcePath!=="")a=this.resourcePath;else if(this.path!==""){const h=Jo.extractUrlBase(e);a=Jo.resolveURL(h,this.path)}else a=Jo.extractUrlBase(e);this.manager.itemStart(e);const l=function(h){i?i(h):console.error(h),s.manager.itemError(e),s.manager.itemEnd(e)},u=new Rd(this.manager);u.setPath(this.path),u.setResponseType("arraybuffer"),u.setRequestHeader(this.requestHeader),u.setWithCredentials(this.withCredentials),u.load(e,function(h){try{s.parse(h,a,function(f){t(f),s.manager.itemEnd(e)},l)}catch(f){l(f)}},n,l)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,i){let s;const a={},l={},u=new TextDecoder;if(typeof e=="string")s=JSON.parse(e);else if(e instanceof ArrayBuffer)if(u.decode(new Uint8Array(e,0,4))===s_){try{a[Nt.KHR_BINARY_GLTF]=new oD(e)}catch(p){i&&i(p);return}s=JSON.parse(a[Nt.KHR_BINARY_GLTF].content)}else s=JSON.parse(u.decode(e));else s=e;if(s.asset===void 0||s.asset.version[0]<2){i&&i(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const h=new yD(s,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});h.fileLoader.setRequestHeader(this.requestHeader);for(let f=0;f<this.pluginCallbacks.length;f++){const p=this.pluginCallbacks[f](h);p.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),l[p.name]=p,a[p.name]=!0}if(s.extensionsUsed)for(let f=0;f<s.extensionsUsed.length;++f){const p=s.extensionsUsed[f],m=s.extensionsRequired||[];switch(p){case Nt.KHR_MATERIALS_UNLIT:a[p]=new GC;break;case Nt.KHR_DRACO_MESH_COMPRESSION:a[p]=new aD(s,this.dracoLoader);break;case Nt.KHR_TEXTURE_TRANSFORM:a[p]=new lD;break;case Nt.KHR_MESH_QUANTIZATION:a[p]=new cD;break;default:m.indexOf(p)>=0&&l[p]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+p+'".')}}h.setExtensions(a),h.setPlugins(l),h.parse(n,i)}parseAsync(e,t){const n=this;return new Promise(function(i,s){n.parse(e,t,i,s)})}}function HC(){let r={};return{get:function(e){return r[e]},add:function(e,t){r[e]=t},remove:function(e){delete r[e]},removeAll:function(){r={}}}}const Nt={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class VC{constructor(e){this.parser=e,this.name=Nt.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,i=t.length;n<i;n++){const s=t[n];s.extensions&&s.extensions[this.name]&&s.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,s.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let i=t.cache.get(n);if(i)return i;const s=t.json,u=((s.extensions&&s.extensions[this.name]||{}).lights||[])[e];let h;const f=new pt(16777215);u.color!==void 0&&f.setRGB(u.color[0],u.color[1],u.color[2],qn);const p=u.range!==void 0?u.range:0;switch(u.type){case"directional":h=new Il(f),h.target.position.set(0,0,-1),h.add(h.target);break;case"point":h=new $g(f),h.distance=p;break;case"spot":h=new KP(f),h.distance=p,u.spot=u.spot||{},u.spot.innerConeAngle=u.spot.innerConeAngle!==void 0?u.spot.innerConeAngle:0,u.spot.outerConeAngle=u.spot.outerConeAngle!==void 0?u.spot.outerConeAngle:Math.PI/4,h.angle=u.spot.outerConeAngle,h.penumbra=1-u.spot.innerConeAngle/u.spot.outerConeAngle,h.target.position.set(0,0,-1),h.add(h.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+u.type)}return h.position.set(0,0,0),h.decay=2,Ji(h,u),u.intensity!==void 0&&(h.intensity=u.intensity),h.name=t.createUniqueName(u.name||"light_"+e),i=Promise.resolve(h),t.cache.add(n,i),i}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,s=n.json.nodes[e],l=(s.extensions&&s.extensions[this.name]||{}).light;return l===void 0?null:this._loadLight(l).then(function(u){return n._getNodeRef(t.cache,l,u)})}}class GC{constructor(){this.name=Nt.KHR_MATERIALS_UNLIT}getMaterialType(){return mi}extendParams(e,t,n){const i=[];e.color=new pt(1,1,1),e.opacity=1;const s=t.pbrMetallicRoughness;if(s){if(Array.isArray(s.baseColorFactor)){const a=s.baseColorFactor;e.color.setRGB(a[0],a[1],a[2],qn),e.opacity=a[3]}s.baseColorTexture!==void 0&&i.push(n.assignTexture(e,"map",s.baseColorTexture,Rn))}return Promise.all(i)}}class WC{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name].emissiveStrength;return s!==void 0&&(t.emissiveIntensity=s),Promise.resolve()}}class jC{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];if(a.clearcoatFactor!==void 0&&(t.clearcoat=a.clearcoatFactor),a.clearcoatTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatMap",a.clearcoatTexture)),a.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=a.clearcoatRoughnessFactor),a.clearcoatRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatRoughnessMap",a.clearcoatRoughnessTexture)),a.clearcoatNormalTexture!==void 0&&(s.push(n.assignTexture(t,"clearcoatNormalMap",a.clearcoatNormalTexture)),a.clearcoatNormalTexture.scale!==void 0)){const l=a.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new vt(l,l)}return Promise.all(s)}}class XC{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.dispersion=s.dispersion!==void 0?s.dispersion:0,Promise.resolve()}}class qC{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.iridescenceFactor!==void 0&&(t.iridescence=a.iridescenceFactor),a.iridescenceTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceMap",a.iridescenceTexture)),a.iridescenceIor!==void 0&&(t.iridescenceIOR=a.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),a.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=a.iridescenceThicknessMinimum),a.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=a.iridescenceThicknessMaximum),a.iridescenceThicknessTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceThicknessMap",a.iridescenceThicknessTexture)),Promise.all(s)}}class YC{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[];t.sheenColor=new pt(0,0,0),t.sheenRoughness=0,t.sheen=1;const a=i.extensions[this.name];if(a.sheenColorFactor!==void 0){const l=a.sheenColorFactor;t.sheenColor.setRGB(l[0],l[1],l[2],qn)}return a.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=a.sheenRoughnessFactor),a.sheenColorTexture!==void 0&&s.push(n.assignTexture(t,"sheenColorMap",a.sheenColorTexture,Rn)),a.sheenRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"sheenRoughnessMap",a.sheenRoughnessTexture)),Promise.all(s)}}class KC{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.transmissionFactor!==void 0&&(t.transmission=a.transmissionFactor),a.transmissionTexture!==void 0&&s.push(n.assignTexture(t,"transmissionMap",a.transmissionTexture)),Promise.all(s)}}class $C{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.thickness=a.thicknessFactor!==void 0?a.thicknessFactor:0,a.thicknessTexture!==void 0&&s.push(n.assignTexture(t,"thicknessMap",a.thicknessTexture)),t.attenuationDistance=a.attenuationDistance||1/0;const l=a.attenuationColor||[1,1,1];return t.attenuationColor=new pt().setRGB(l[0],l[1],l[2],qn),Promise.all(s)}}class ZC{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.ior=s.ior!==void 0?s.ior:1.5,Promise.resolve()}}class QC{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.specularIntensity=a.specularFactor!==void 0?a.specularFactor:1,a.specularTexture!==void 0&&s.push(n.assignTexture(t,"specularIntensityMap",a.specularTexture));const l=a.specularColorFactor||[1,1,1];return t.specularColor=new pt().setRGB(l[0],l[1],l[2],qn),a.specularColorTexture!==void 0&&s.push(n.assignTexture(t,"specularColorMap",a.specularColorTexture,Rn)),Promise.all(s)}}class JC{constructor(e){this.parser=e,this.name=Nt.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return t.bumpScale=a.bumpFactor!==void 0?a.bumpFactor:1,a.bumpTexture!==void 0&&s.push(n.assignTexture(t,"bumpMap",a.bumpTexture)),Promise.all(s)}}class eD{constructor(e){this.parser=e,this.name=Nt.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ni}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.anisotropyStrength!==void 0&&(t.anisotropy=a.anisotropyStrength),a.anisotropyRotation!==void 0&&(t.anisotropyRotation=a.anisotropyRotation),a.anisotropyTexture!==void 0&&s.push(n.assignTexture(t,"anisotropyMap",a.anisotropyTexture)),Promise.all(s)}}class tD{constructor(e){this.parser=e,this.name=Nt.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,i=n.textures[e];if(!i.extensions||!i.extensions[this.name])return null;const s=i.extensions[this.name],a=t.options.ktx2Loader;if(!a){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,s.source,a)}}class nD{constructor(e){this.parser=e,this.name=Nt.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],l=i.images[a.source];let u=n.textureLoader;if(l.uri){const h=n.options.manager.getHandler(l.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class iD{constructor(e){this.parser=e,this.name=Nt.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],l=i.images[a.source];let u=n.textureLoader;if(l.uri){const h=n.options.manager.getHandler(l.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class rD{constructor(e){this.name=Nt.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const i=n.extensions[this.name],s=this.parser.getDependency("buffer",i.buffer),a=this.parser.options.meshoptDecoder;if(!a||!a.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return s.then(function(l){const u=i.byteOffset||0,h=i.byteLength||0,f=i.count,p=i.byteStride,m=new Uint8Array(l,u,h);return a.decodeGltfBufferAsync?a.decodeGltfBufferAsync(f,p,m,i.mode,i.filter).then(function(g){return g.buffer}):a.ready.then(function(){const g=new ArrayBuffer(f*p);return a.decodeGltfBuffer(new Uint8Array(g),f,p,m,i.mode,i.filter),g})})}else return null}}class sD{constructor(e){this.name=Nt.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const i=t.meshes[n.mesh];for(const h of i.primitives)if(h.mode!==fi.TRIANGLES&&h.mode!==fi.TRIANGLE_STRIP&&h.mode!==fi.TRIANGLE_FAN&&h.mode!==void 0)return null;const a=n.extensions[this.name].attributes,l=[],u={};for(const h in a)l.push(this.parser.getDependency("accessor",a[h]).then(f=>(u[h]=f,u[h])));return l.length<1?null:(l.push(this.parser.createNodeMesh(e)),Promise.all(l).then(h=>{const f=h.pop(),p=f.isGroup?f.children:[f],m=h[0].count,g=[];for(const x of p){const E=new St,v=new F,_=new Dt,R=new F(1,1,1),w=new LP(x.geometry,x.material,m);for(let S=0;S<m;S++)u.TRANSLATION&&v.fromBufferAttribute(u.TRANSLATION,S),u.ROTATION&&_.fromBufferAttribute(u.ROTATION,S),u.SCALE&&R.fromBufferAttribute(u.SCALE,S),w.setMatrixAt(S,E.compose(v,_,R));for(const S in u)if(S==="_COLOR_0"){const k=u[S];w.instanceColor=new id(k.array,k.itemSize,k.normalized)}else S!=="TRANSLATION"&&S!=="ROTATION"&&S!=="SCALE"&&x.geometry.setAttribute(S,u[S]);an.prototype.copy.call(w,x),this.parser.assignFinalMaterial(w),g.push(w)}return f.isGroup?(f.clear(),f.add(...g),f):g[0]}))}}const s_="glTF",Wo=12,og={JSON:1313821514,BIN:5130562};class oD{constructor(e){this.name=Nt.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,Wo),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==s_)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const i=this.header.length-Wo,s=new DataView(e,Wo);let a=0;for(;a<i;){const l=s.getUint32(a,!0);a+=4;const u=s.getUint32(a,!0);if(a+=4,u===og.JSON){const h=new Uint8Array(e,Wo+a,l);this.content=n.decode(h)}else if(u===og.BIN){const h=Wo+a;this.body=e.slice(h,h+l)}a+=l}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class aD{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=Nt.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,i=this.dracoLoader,s=e.extensions[this.name].bufferView,a=e.extensions[this.name].attributes,l={},u={},h={};for(const f in a){const p=ad[f]||f.toLowerCase();l[p]=a[f]}for(const f in e.attributes){const p=ad[f]||f.toLowerCase();if(a[f]!==void 0){const m=n.accessors[e.attributes[f]],g=$s[m.componentType];h[p]=g.name,u[p]=m.normalized===!0}}return t.getDependency("bufferView",s).then(function(f){return new Promise(function(p,m){i.decodeDracoFile(f,function(g){for(const x in g.attributes){const E=g.attributes[x],v=u[x];v!==void 0&&(E.normalized=v)}p(g)},l,h,qn,m)})})}}class lD{constructor(){this.name=Nt.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class cD{constructor(){this.name=Nt.KHR_MESH_QUANTIZATION}}class o_ extends aa{constructor(e,t,n,i){super(e,t,n,i)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i*3+i;for(let a=0;a!==i;a++)t[a]=n[s+a];return t}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,l=this.valueSize,u=l*2,h=l*3,f=i-t,p=(n-t)/f,m=p*p,g=m*p,x=e*h,E=x-h,v=-2*g+3*m,_=g-m,R=1-v,w=_-m+p;for(let S=0;S!==l;S++){const k=a[E+S+l],N=a[E+S+u]*f,O=a[x+S+l],H=a[x+S]*f;s[S]=R*k+w*N+v*O+_*H}return s}}const uD=new Dt;class hD extends o_{interpolate_(e,t,n,i){const s=super.interpolate_(e,t,n,i);return uD.fromArray(s).normalize().toArray(s),s}}const fi={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},$s={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},ag={9728:Xn,9729:ci,9984:mg,9985:Tl,9986:jo,9987:er},lg={33071:br,33648:Fl,10497:to},uh={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},ad={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},vr={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},dD={CUBICSPLINE:void 0,LINEAR:na,STEP:ta},hh={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function fD(r){return r.DefaultMaterial===void 0&&(r.DefaultMaterial=new hs({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:ir})),r.DefaultMaterial}function is(r,e,t){for(const n in t.extensions)r[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function Ji(r,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(r.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function pD(r,e,t){let n=!1,i=!1,s=!1;for(let h=0,f=e.length;h<f;h++){const p=e[h];if(p.POSITION!==void 0&&(n=!0),p.NORMAL!==void 0&&(i=!0),p.COLOR_0!==void 0&&(s=!0),n&&i&&s)break}if(!n&&!i&&!s)return Promise.resolve(r);const a=[],l=[],u=[];for(let h=0,f=e.length;h<f;h++){const p=e[h];if(n){const m=p.POSITION!==void 0?t.getDependency("accessor",p.POSITION):r.attributes.position;a.push(m)}if(i){const m=p.NORMAL!==void 0?t.getDependency("accessor",p.NORMAL):r.attributes.normal;l.push(m)}if(s){const m=p.COLOR_0!==void 0?t.getDependency("accessor",p.COLOR_0):r.attributes.color;u.push(m)}}return Promise.all([Promise.all(a),Promise.all(l),Promise.all(u)]).then(function(h){const f=h[0],p=h[1],m=h[2];return n&&(r.morphAttributes.position=f),i&&(r.morphAttributes.normal=p),s&&(r.morphAttributes.color=m),r.morphTargetsRelative=!0,r})}function mD(r,e){if(r.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)r.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(r.morphTargetInfluences.length===t.length){r.morphTargetDictionary={};for(let n=0,i=t.length;n<i;n++)r.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function gD(r){let e;const t=r.extensions&&r.extensions[Nt.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+dh(t.attributes):e=r.indices+":"+dh(r.attributes)+":"+r.mode,r.targets!==void 0)for(let n=0,i=r.targets.length;n<i;n++)e+=":"+dh(r.targets[n]);return e}function dh(r){let e="";const t=Object.keys(r).sort();for(let n=0,i=t.length;n<i;n++)e+=t[n]+":"+r[t[n]]+";";return e}function ld(r){switch(r){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function _D(r){return r.search(/\.jpe?g($|\?)/i)>0||r.search(/^data\:image\/jpeg/)===0?"image/jpeg":r.search(/\.webp($|\?)/i)>0||r.search(/^data\:image\/webp/)===0?"image/webp":r.search(/\.ktx2($|\?)/i)>0||r.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const vD=new St;class yD{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new HC,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,i=-1,s=!1,a=-1;if(typeof navigator<"u"){const l=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(l)===!0;const u=l.match(/Version\/(\d+)/);i=n&&u?parseInt(u[1],10):-1,s=l.indexOf("Firefox")>-1,a=s?l.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&i<17||s&&a<98?this.textureLoader=new qP(this.options.manager):this.textureLoader=new JP(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new Rd(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,i=this.json,s=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(a){return a._markDefs&&a._markDefs()}),Promise.all(this._invokeAll(function(a){return a.beforeRoot&&a.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(a){const l={scene:a[0][i.scene||0],scenes:a[0],animations:a[1],cameras:a[2],asset:i.asset,parser:n,userData:{}};return is(s,l,i),Ji(l,i),Promise.all(n._invokeAll(function(u){return u.afterRoot&&u.afterRoot(l)})).then(function(){for(const u of l.scenes)u.updateMatrixWorld();e(l)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let i=0,s=t.length;i<s;i++){const a=t[i].joints;for(let l=0,u=a.length;l<u;l++)e[a[l]].isBone=!0}for(let i=0,s=e.length;i<s;i++){const a=e[i];a.mesh!==void 0&&(this._addNodeRef(this.meshCache,a.mesh),a.skin!==void 0&&(n[a.mesh].isSkinnedMesh=!0)),a.camera!==void 0&&this._addNodeRef(this.cameraCache,a.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const i=n.clone(),s=(a,l)=>{const u=this.associations.get(a);u!=null&&this.associations.set(l,u);for(const[h,f]of a.children.entries())s(f,l.children[h])};return s(n,i),i.name+="_instance_"+e.uses[t]++,i}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const i=e(t[n]);if(i)return i}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let i=0;i<t.length;i++){const s=e(t[i]);s&&n.push(s)}return n}getDependency(e,t){const n=e+":"+t;let i=this.cache.get(n);if(!i){switch(e){case"scene":i=this.loadScene(t);break;case"node":i=this._invokeOne(function(s){return s.loadNode&&s.loadNode(t)});break;case"mesh":i=this._invokeOne(function(s){return s.loadMesh&&s.loadMesh(t)});break;case"accessor":i=this.loadAccessor(t);break;case"bufferView":i=this._invokeOne(function(s){return s.loadBufferView&&s.loadBufferView(t)});break;case"buffer":i=this.loadBuffer(t);break;case"material":i=this._invokeOne(function(s){return s.loadMaterial&&s.loadMaterial(t)});break;case"texture":i=this._invokeOne(function(s){return s.loadTexture&&s.loadTexture(t)});break;case"skin":i=this.loadSkin(t);break;case"animation":i=this._invokeOne(function(s){return s.loadAnimation&&s.loadAnimation(t)});break;case"camera":i=this.loadCamera(t);break;default:if(i=this._invokeOne(function(s){return s!=this&&s.getDependency&&s.getDependency(e,t)}),!i)throw new Error("Unknown type: "+e);break}this.cache.add(n,i)}return i}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,i=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(i.map(function(s,a){return n.getDependency(e,a)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[Nt.KHR_BINARY_GLTF].body);const i=this.options;return new Promise(function(s,a){n.load(Jo.resolveURL(t.uri,i.path),s,void 0,function(){a(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const i=t.byteLength||0,s=t.byteOffset||0;return n.slice(s,s+i)})}loadAccessor(e){const t=this,n=this.json,i=this.json.accessors[e];if(i.bufferView===void 0&&i.sparse===void 0){const a=uh[i.type],l=$s[i.componentType],u=i.normalized===!0,h=new l(i.count*a);return Promise.resolve(new pn(h,a,u))}const s=[];return i.bufferView!==void 0?s.push(this.getDependency("bufferView",i.bufferView)):s.push(null),i.sparse!==void 0&&(s.push(this.getDependency("bufferView",i.sparse.indices.bufferView)),s.push(this.getDependency("bufferView",i.sparse.values.bufferView))),Promise.all(s).then(function(a){const l=a[0],u=uh[i.type],h=$s[i.componentType],f=h.BYTES_PER_ELEMENT,p=f*u,m=i.byteOffset||0,g=i.bufferView!==void 0?n.bufferViews[i.bufferView].byteStride:void 0,x=i.normalized===!0;let E,v;if(g&&g!==p){const _=Math.floor(m/g),R="InterleavedBuffer:"+i.bufferView+":"+i.componentType+":"+_+":"+i.count;let w=t.cache.get(R);w||(E=new h(l,_*g,i.count*g/f),w=new PP(E,g/f),t.cache.add(R,w)),v=new Td(w,u,m%g/f,x)}else l===null?E=new h(i.count*u):E=new h(l,m,i.count*u),v=new pn(E,u,x);if(i.sparse!==void 0){const _=uh.SCALAR,R=$s[i.sparse.indices.componentType],w=i.sparse.indices.byteOffset||0,S=i.sparse.values.byteOffset||0,k=new R(a[1],w,i.sparse.count*_),N=new h(a[2],S,i.sparse.count*u);l!==null&&(v=new pn(v.array.slice(),v.itemSize,v.normalized)),v.normalized=!1;for(let O=0,H=k.length;O<H;O++){const D=k[O];if(v.setX(D,N[O*u]),u>=2&&v.setY(D,N[O*u+1]),u>=3&&v.setZ(D,N[O*u+2]),u>=4&&v.setW(D,N[O*u+3]),u>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}v.normalized=x}return v})}loadTexture(e){const t=this.json,n=this.options,s=t.textures[e].source,a=t.images[s];let l=this.textureLoader;if(a.uri){const u=n.manager.getHandler(a.uri);u!==null&&(l=u)}return this.loadTextureImage(e,s,l)}loadTextureImage(e,t,n){const i=this,s=this.json,a=s.textures[e],l=s.images[t],u=(l.uri||l.bufferView)+":"+a.sampler;if(this.textureCache[u])return this.textureCache[u];const h=this.loadImageSource(t,n).then(function(f){f.flipY=!1,f.name=a.name||l.name||"",f.name===""&&typeof l.uri=="string"&&l.uri.startsWith("data:image/")===!1&&(f.name=l.uri);const m=(s.samplers||{})[a.sampler]||{};return f.magFilter=ag[m.magFilter]||ci,f.minFilter=ag[m.minFilter]||er,f.wrapS=lg[m.wrapS]||to,f.wrapT=lg[m.wrapT]||to,f.generateMipmaps=!f.isCompressedTexture&&f.minFilter!==Xn&&f.minFilter!==ci,i.associations.set(f,{textures:e}),f}).catch(function(){return null});return this.textureCache[u]=h,h}loadImageSource(e,t){const n=this,i=this.json,s=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(p=>p.clone());const a=i.images[e],l=self.URL||self.webkitURL;let u=a.uri||"",h=!1;if(a.bufferView!==void 0)u=n.getDependency("bufferView",a.bufferView).then(function(p){h=!0;const m=new Blob([p],{type:a.mimeType});return u=l.createObjectURL(m),u});else if(a.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const f=Promise.resolve(u).then(function(p){return new Promise(function(m,g){let x=m;t.isImageBitmapLoader===!0&&(x=function(E){const v=new Pn(E);v.needsUpdate=!0,m(v)}),t.load(Jo.resolveURL(p,s.path),x,void 0,g)})}).then(function(p){return h===!0&&l.revokeObjectURL(u),Ji(p,a),p.userData.mimeType=a.mimeType||_D(a.uri),p}).catch(function(p){throw console.error("THREE.GLTFLoader: Couldn't load texture",u),p});return this.sourceCache[e]=f,f}assignTexture(e,t,n,i){const s=this;return this.getDependency("texture",n.index).then(function(a){if(!a)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(a=a.clone(),a.channel=n.texCoord),s.extensions[Nt.KHR_TEXTURE_TRANSFORM]){const l=n.extensions!==void 0?n.extensions[Nt.KHR_TEXTURE_TRANSFORM]:void 0;if(l){const u=s.associations.get(a);a=s.extensions[Nt.KHR_TEXTURE_TRANSFORM].extendTexture(a,l),s.associations.set(a,u)}}return i!==void 0&&(a.colorSpace=i),e[t]=a,a})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const i=t.attributes.tangent===void 0,s=t.attributes.color!==void 0,a=t.attributes.normal===void 0;if(e.isPoints){const l="PointsMaterial:"+n.uuid;let u=this.cache.get(l);u||(u=new Xg,Li.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,u.sizeAttenuation=!1,this.cache.add(l,u)),n=u}else if(e.isLine){const l="LineBasicMaterial:"+n.uuid;let u=this.cache.get(l);u||(u=new Wl,Li.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,this.cache.add(l,u)),n=u}if(i||s||a){let l="ClonedMaterial:"+n.uuid+":";i&&(l+="derivative-tangents:"),s&&(l+="vertex-colors:"),a&&(l+="flat-shading:");let u=this.cache.get(l);u||(u=n.clone(),s&&(u.vertexColors=!0),a&&(u.flatShading=!0),i&&(u.normalScale&&(u.normalScale.y*=-1),u.clearcoatNormalScale&&(u.clearcoatNormalScale.y*=-1)),this.cache.add(l,u),this.associations.set(u,this.associations.get(n))),n=u}e.material=n}getMaterialType(){return hs}loadMaterial(e){const t=this,n=this.json,i=this.extensions,s=n.materials[e];let a;const l={},u=s.extensions||{},h=[];if(u[Nt.KHR_MATERIALS_UNLIT]){const p=i[Nt.KHR_MATERIALS_UNLIT];a=p.getMaterialType(),h.push(p.extendParams(l,s,t))}else{const p=s.pbrMetallicRoughness||{};if(l.color=new pt(1,1,1),l.opacity=1,Array.isArray(p.baseColorFactor)){const m=p.baseColorFactor;l.color.setRGB(m[0],m[1],m[2],qn),l.opacity=m[3]}p.baseColorTexture!==void 0&&h.push(t.assignTexture(l,"map",p.baseColorTexture,Rn)),l.metalness=p.metallicFactor!==void 0?p.metallicFactor:1,l.roughness=p.roughnessFactor!==void 0?p.roughnessFactor:1,p.metallicRoughnessTexture!==void 0&&(h.push(t.assignTexture(l,"metalnessMap",p.metallicRoughnessTexture)),h.push(t.assignTexture(l,"roughnessMap",p.metallicRoughnessTexture))),a=this._invokeOne(function(m){return m.getMaterialType&&m.getMaterialType(e)}),h.push(Promise.all(this._invokeAll(function(m){return m.extendMaterialParams&&m.extendMaterialParams(e,l)})))}s.doubleSided===!0&&(l.side=Qn);const f=s.alphaMode||hh.OPAQUE;if(f===hh.BLEND?(l.transparent=!0,l.depthWrite=!1):(l.transparent=!1,f===hh.MASK&&(l.alphaTest=s.alphaCutoff!==void 0?s.alphaCutoff:.5)),s.normalTexture!==void 0&&a!==mi&&(h.push(t.assignTexture(l,"normalMap",s.normalTexture)),l.normalScale=new vt(1,1),s.normalTexture.scale!==void 0)){const p=s.normalTexture.scale;l.normalScale.set(p,p)}if(s.occlusionTexture!==void 0&&a!==mi&&(h.push(t.assignTexture(l,"aoMap",s.occlusionTexture)),s.occlusionTexture.strength!==void 0&&(l.aoMapIntensity=s.occlusionTexture.strength)),s.emissiveFactor!==void 0&&a!==mi){const p=s.emissiveFactor;l.emissive=new pt().setRGB(p[0],p[1],p[2],qn)}return s.emissiveTexture!==void 0&&a!==mi&&h.push(t.assignTexture(l,"emissiveMap",s.emissiveTexture,Rn)),Promise.all(h).then(function(){const p=new a(l);return s.name&&(p.name=s.name),Ji(p,s),t.associations.set(p,{materials:e}),s.extensions&&is(i,p,s),p})}createUniqueName(e){const t=Xt.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,i=this.primitiveCache;function s(l){return n[Nt.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(l,t).then(function(u){return cg(u,l,t)})}const a=[];for(let l=0,u=e.length;l<u;l++){const h=e[l],f=gD(h),p=i[f];if(p)a.push(p.promise);else{let m;h.extensions&&h.extensions[Nt.KHR_DRACO_MESH_COMPRESSION]?m=s(h):m=cg(new Sn,h,t),i[f]={primitive:h,promise:m},a.push(m)}}return Promise.all(a)}loadMesh(e){const t=this,n=this.json,i=this.extensions,s=n.meshes[e],a=s.primitives,l=[];for(let u=0,h=a.length;u<h;u++){const f=a[u].material===void 0?fD(this.cache):this.getDependency("material",a[u].material);l.push(f)}return l.push(t.loadGeometries(a)),Promise.all(l).then(function(u){const h=u.slice(0,u.length-1),f=u[u.length-1],p=[];for(let g=0,x=f.length;g<x;g++){const E=f[g],v=a[g];let _;const R=h[g];if(v.mode===fi.TRIANGLES||v.mode===fi.TRIANGLE_STRIP||v.mode===fi.TRIANGLE_FAN||v.mode===void 0)_=s.isSkinnedMesh===!0?new Ul(E,R):new Pe(E,R),_.isSkinnedMesh===!0&&_.normalizeSkinWeights(),v.mode===fi.TRIANGLE_STRIP?_.geometry=sg(_.geometry,Tg):v.mode===fi.TRIANGLE_FAN&&(_.geometry=sg(_.geometry,ed));else if(v.mode===fi.LINES)_=new jg(E,R);else if(v.mode===fi.LINE_STRIP)_=new xi(E,R);else if(v.mode===fi.LINE_LOOP)_=new FP(E,R);else if(v.mode===fi.POINTS)_=new NP(E,R);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+v.mode);Object.keys(_.geometry.morphAttributes).length>0&&mD(_,s),_.name=t.createUniqueName(s.name||"mesh_"+e),Ji(_,s),v.extensions&&is(i,_,v),t.assignFinalMaterial(_),p.push(_)}for(let g=0,x=p.length;g<x;g++)t.associations.set(p[g],{meshes:e,primitives:g});if(p.length===1)return s.extensions&&is(i,p[0],s),p[0];const m=new Ii;s.extensions&&is(i,m,s),t.associations.set(m,{meshes:e});for(let g=0,x=p.length;g<x;g++)m.add(p[g]);return m})}loadCamera(e){let t;const n=this.json.cameras[e],i=n[n.type];if(!i){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new jn(Rg.radToDeg(i.yfov),i.aspectRatio||1,i.znear||1,i.zfar||2e6):n.type==="orthographic"&&(t=new Sd(-i.xmag,i.xmag,i.ymag,-i.ymag,i.znear,i.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),Ji(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let i=0,s=t.joints.length;i<s;i++)n.push(this._loadNodeShallow(t.joints[i]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(i){const s=i.pop(),a=i,l=[],u=[];for(let h=0,f=a.length;h<f;h++){const p=a[h];if(p){l.push(p);const m=new St;s!==null&&m.fromArray(s.array,h*16),u.push(m)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[h])}return new sa(l,u)})}loadAnimation(e){const t=this.json,n=this,i=t.animations[e],s=i.name?i.name:"animation_"+e,a=[],l=[],u=[],h=[],f=[];for(let p=0,m=i.channels.length;p<m;p++){const g=i.channels[p],x=i.samplers[g.sampler],E=g.target,v=E.node,_=i.parameters!==void 0?i.parameters[x.input]:x.input,R=i.parameters!==void 0?i.parameters[x.output]:x.output;E.node!==void 0&&(a.push(this.getDependency("node",v)),l.push(this.getDependency("accessor",_)),u.push(this.getDependency("accessor",R)),h.push(x),f.push(E))}return Promise.all([Promise.all(a),Promise.all(l),Promise.all(u),Promise.all(h),Promise.all(f)]).then(function(p){const m=p[0],g=p[1],x=p[2],E=p[3],v=p[4],_=[];for(let R=0,w=m.length;R<w;R++){const S=m[R],k=g[R],N=x[R],O=E[R],H=v[R];if(S===void 0)continue;S.updateMatrix&&S.updateMatrix();const D=n._createAnimationTracks(S,k,N,O,H);if(D)for(let A=0;A<D.length;A++)_.push(D[A])}return new ao(s,void 0,_)})}createNodeMesh(e){const t=this.json,n=this,i=t.nodes[e];return i.mesh===void 0?null:n.getDependency("mesh",i.mesh).then(function(s){const a=n._getNodeRef(n.meshCache,i.mesh,s);return i.weights!==void 0&&a.traverse(function(l){if(l.isMesh)for(let u=0,h=i.weights.length;u<h;u++)l.morphTargetInfluences[u]=i.weights[u]}),a})}loadNode(e){const t=this.json,n=this,i=t.nodes[e],s=n._loadNodeShallow(e),a=[],l=i.children||[];for(let h=0,f=l.length;h<f;h++)a.push(n.getDependency("node",l[h]));const u=i.skin===void 0?Promise.resolve(null):n.getDependency("skin",i.skin);return Promise.all([s,Promise.all(a),u]).then(function(h){const f=h[0],p=h[1],m=h[2];m!==null&&f.traverse(function(g){g.isSkinnedMesh&&g.bind(m,vD)});for(let g=0,x=p.length;g<x;g++)f.add(p[g]);return f})}_loadNodeShallow(e){const t=this.json,n=this.extensions,i=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const s=t.nodes[e],a=s.name?i.createUniqueName(s.name):"",l=[],u=i._invokeOne(function(h){return h.createNodeMesh&&h.createNodeMesh(e)});return u&&l.push(u),s.camera!==void 0&&l.push(i.getDependency("camera",s.camera).then(function(h){return i._getNodeRef(i.cameraCache,s.camera,h)})),i._invokeAll(function(h){return h.createNodeAttachment&&h.createNodeAttachment(e)}).forEach(function(h){l.push(h)}),this.nodeCache[e]=Promise.all(l).then(function(h){let f;if(s.isBone===!0?f=new Gl:h.length>1?f=new Ii:h.length===1?f=h[0]:f=new an,f!==h[0])for(let p=0,m=h.length;p<m;p++)f.add(h[p]);if(s.name&&(f.userData.name=s.name,f.name=a),Ji(f,s),s.extensions&&is(n,f,s),s.matrix!==void 0){const p=new St;p.fromArray(s.matrix),f.applyMatrix4(p)}else s.translation!==void 0&&f.position.fromArray(s.translation),s.rotation!==void 0&&f.quaternion.fromArray(s.rotation),s.scale!==void 0&&f.scale.fromArray(s.scale);return i.associations.has(f)||i.associations.set(f,{}),i.associations.get(f).nodes=e,f}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],i=this,s=new Ii;n.name&&(s.name=i.createUniqueName(n.name)),Ji(s,n),n.extensions&&is(t,s,n);const a=n.nodes||[],l=[];for(let u=0,h=a.length;u<h;u++)l.push(i.getDependency("node",a[u]));return Promise.all(l).then(function(u){for(let f=0,p=u.length;f<p;f++)s.add(u[f]);const h=f=>{const p=new Map;for(const[m,g]of i.associations)(m instanceof Li||m instanceof Pn)&&p.set(m,g);return f.traverse(m=>{const g=i.associations.get(m);g!=null&&p.set(m,g)}),p};return i.associations=h(s),s})}_createAnimationTracks(e,t,n,i,s){const a=[],l=e.name?e.name:e.uuid,u=[];vr[s.path]===vr.weights?e.traverse(function(m){m.morphTargetInfluences&&u.push(m.name?m.name:m.uuid)}):u.push(l);let h;switch(vr[s.path]){case vr.weights:h=oo;break;case vr.rotation:h=wr;break;case vr.position:case vr.scale:h=Ar;break;default:switch(n.itemSize){case 1:h=oo;break;case 2:case 3:default:h=Ar;break}break}const f=i.interpolation!==void 0?dD[i.interpolation]:na,p=this._getArrayFromAccessor(n);for(let m=0,g=u.length;m<g;m++){const x=new h(u[m]+"."+vr[s.path],t.array,p,f);i.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(x),a.push(x)}return a}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=ld(t.constructor),i=new Float32Array(t.length);for(let s=0,a=t.length;s<a;s++)i[s]=t[s]*n;t=i}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const i=this instanceof wr?hD:o_;return new i(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function xD(r,e,t){const n=e.attributes,i=new Ti;if(n.POSITION!==void 0){const l=t.json.accessors[n.POSITION],u=l.min,h=l.max;if(u!==void 0&&h!==void 0){if(i.set(new F(u[0],u[1],u[2]),new F(h[0],h[1],h[2])),l.normalized){const f=ld($s[l.componentType]);i.min.multiplyScalar(f),i.max.multiplyScalar(f)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const s=e.targets;if(s!==void 0){const l=new F,u=new F;for(let h=0,f=s.length;h<f;h++){const p=s[h];if(p.POSITION!==void 0){const m=t.json.accessors[p.POSITION],g=m.min,x=m.max;if(g!==void 0&&x!==void 0){if(u.setX(Math.max(Math.abs(g[0]),Math.abs(x[0]))),u.setY(Math.max(Math.abs(g[1]),Math.abs(x[1]))),u.setZ(Math.max(Math.abs(g[2]),Math.abs(x[2]))),m.normalized){const E=ld($s[m.componentType]);u.multiplyScalar(E)}l.max(u)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}i.expandByVector(l)}r.boundingBox=i;const a=new Fi;i.getCenter(a.center),a.radius=i.min.distanceTo(i.max)/2,r.boundingSphere=a}function cg(r,e,t){const n=e.attributes,i=[];function s(a,l){return t.getDependency("accessor",a).then(function(u){r.setAttribute(l,u)})}for(const a in n){const l=ad[a]||a.toLowerCase();l in r.attributes||i.push(s(n[a],l))}if(e.indices!==void 0&&!r.index){const a=t.getDependency("accessor",e.indices).then(function(l){r.setIndex(l)});i.push(a)}return zt.workingColorSpace!==qn&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${zt.workingColorSpace}" not supported.`),Ji(r,e),xD(r,e,t),Promise.all(i).then(function(){return e.targets!==void 0?pD(r,e.targets,t):r})}const a_=new zC,bD=new n_;let lo=0;async function SD(r,e){return new Promise((t,n)=>{a_.load(r,i=>{const s=i.scene;e.add(s),s.traverse(u=>{u.isMesh&&(u.castShadow=!0,u.receiveShadow=!0)}),lo++;const a=`Asset ${lo}`,l=Ld();l&&Fd(l,a,s),t(s)},void 0,i=>n(i))})}async function ED(r,e){const t=URL.createObjectURL(r);try{return await SD(t,e)}finally{URL.revokeObjectURL(t)}}const MD=[{color:13935988,roughness:.55,metalness:0},{color:13935988,roughness:.55,metalness:0},{color:1118481,roughness:.8,metalness:0},{color:657930,roughness:.1,metalness:0},{color:16052456,roughness:.2,metalness:0},{color:16052456,roughness:.05,metalness:0,opacity:.3,transparent:!0},{color:4881051,roughness:.15,metalness:0},{color:11885162,roughness:.7,metalness:0},{color:15789280,roughness:.3,metalness:0},{color:14723210,roughness:.4,metalness:0},{color:14723210,roughness:.4,metalness:0}];function Zs(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Float32Array(t.buffer)}function l_(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Uint32Array(t.buffer)}function cd(r){for(let e=0;e<r.length;e+=3){const t=r[e+1],n=r[e+2];r[e+1]=n,r[e+2]=-t}}function TD(r){const e=Zs(r.vertices),t=l_(r.faces);cd(e);const n=new Sn,i=new pn(e,3),s=new pn(t,1);if(n.setAttribute("position",i),n.setIndex(s),r.uvs){const f=Zs(r.uvs);n.setAttribute("uv",new pn(f,2))}if(r.normals){const f=Zs(r.normals);cd(f),n.setAttribute("normal",new pn(f,3))}else n.computeVertexNormals();const a=MD.map(f=>new hs({color:f.color,roughness:f.roughness,metalness:f.metalness,side:Qn,transparent:f.transparent||!1,opacity:f.opacity!==void 0?f.opacity:1})),l=r.groups||[];let u;if(s&&l.length>0){for(const f of l)n.addGroup(f.start,f.count,f.materialIndex);u=new Pe(n,a)}else u=new Pe(n,a[0]);u.castShadow=!0,u.receiveShadow=!0;const h=new Ii;return h.add(u),h}async function fh(r,e,t){const n=new URLSearchParams;if(e.body_type&&n.set("body_type",e.body_type),e.morphs&&typeof e.morphs=="object")for(const[m,g]of Object.entries(e.morphs))g!=null&&n.set(`morph_${m}`,String(g));if(e.user_morphs&&typeof e.user_morphs=="object")for(const[m,g]of Object.entries(e.user_morphs))g!=null&&n.set(`morph_${m}`,String(g));const i=["age","mass","tone","height"],s=e.meta||{};for(const m of i){const g=s[m]??e[`meta_${m}`];g!=null&&n.set(`meta_${m}`,String(g))}const a=`/api/character/mesh/?${n.toString()}`,l=await fetch(a);if(!l.ok)throw new Error(`Character mesh API error: ${l.status}`);const u=await l.json(),h=TD(u);if(r.add(h),h.userData.bodyType=e.body_type||"Female_Caucasian",h.userData.morphs={...e.morphs||{},...e.user_morphs||{}},h.userData.meta={...e.meta||{}},h.userData.presetName=t,e.hair_style&&e.hair_style.url)try{const m=await wD(e.hair_style.url);m.userData.isHair=!0,m.traverse(g=>{g.isMesh&&(g.userData.isHair=!0)}),h.add(m),console.log("✓ Hair loaded:",e.hair_style.name)}catch(m){console.error("Failed to load hair:",m)}if(e.garments&&Array.isArray(e.garments))for(const m of e.garments)try{const g=await AD(m,e.body_type);g.userData.isGarment=!0,h.add(g),console.log("✓ Garment loaded:",m.id)}catch(g){console.error("Failed to load garment:",m.id,g)}lo++;const f=t||`Character ${lo}`,p=Ld();return p&&Fd(p,f,h),h}async function wD(r){return new Promise((e,t)=>{a_.load(r,n=>{const i=n.scene;i.traverse(s=>{if(s.isMesh&&(s.castShadow=!0,s.receiveShadow=!0,s.material)){if(s.material.color){const a=s.material.color;a.r>.9&&a.g>.9&&a.b>.9&&s.material.color.setRGB(.1,.08,.06)}s.material.roughness===void 0&&(s.material.roughness=.8),s.material.metalness===void 0&&(s.material.metalness=0)}}),e(i)},void 0,n=>t(n))})}async function AD(r,e){const{id:t,offset:n=.006,stiffness:i=.8,color:s=[.3,.35,.5],roughness:a=.8,metalness:l=0}=r,u=s[0]??.3,h=s[1]??.35,f=s[2]??.5,p=`garment_id=${encodeURIComponent(t)}&body_type=${encodeURIComponent(e)}&offset=${n}&stiffness=${i}&color_r=${u.toFixed(3)}&color_g=${h.toFixed(3)}&color_b=${f.toFixed(3)}`,m=await fetch(`/api/character/garment/fit/?${p}`);if(!m.ok)throw new Error(`Garment fit API error: ${m.status}`);const g=await m.json();if(g.error)throw new Error(g.error);const x=Zs(g.vertices);cd(x);const E=l_(g.faces),v=new Sn;v.setAttribute("position",new pn(x,3)),v.setIndex(new pn(E,1)),v.computeVertexNormals();const _=new pt(g.color[0],g.color[1],g.color[2]),R=new hs({color:_,roughness:a,metalness:l,side:Qn,polygonOffset:!0,polygonOffsetFactor:-1,polygonOffsetUnit:-1});let w;if(g.skin_indices&&g.skin_weights){const S=Zs(g.skin_indices),k=Zs(g.skin_weights);v.setAttribute("skinIndex",new Wt(S,4)),v.setAttribute("skinWeight",new Wt(k,4)),w=new Ul(v,R),w.userData.needsBinding=!0}else w=new Pe(v,R);return w.castShadow=!0,w.receiveShadow=!0,w.userData.garmentId=t,w.userData.offset=n,w.userData.stiffness=i,w.userData.originalColor=[u,h,f],w.userData.roughness=a,w.userData.metalness=l,w.name=t,w}function RD(r,e,t){const n=bD.parse(r),i=new Jg(n.skeleton.bones[0]);i.skeleton=n.skeleton,i.visible=!0,i.userData.isRig=!0,i.renderOrder=999,i.material&&(i.material.depthTest=!1,i.material.depthWrite=!1);const s=n.skeleton.bones[0];s.userData.isRig=!0,e.add(s),e.add(i);const a=new Zg(s),l=a.clipAction(n.clip);l.setLoop(_d),l.play(),l.paused=!0,lo++;const u=Ld();u&&Fd(u,t||`BVH ${lo}`,s);const h=n.clip.duration||1;return{mixer:a,action:l,skeleton:i,clip:n.clip,rootBone:s,duration:h}}class PD{constructor(e){this._canvas=e,this._recorder=null,this._chunks=[]}start(e=30){const t=this._canvas.captureStream(e);this._chunks=[];const n=MediaRecorder.isTypeSupported("video/webm;codecs=vp9")?"video/webm;codecs=vp9":"video/webm;codecs=vp8";this._recorder=new MediaRecorder(t,{mimeType:n,videoBitsPerSecond:8e6}),this._recorder.ondataavailable=i=>{i.data.size>0&&this._chunks.push(i.data)},this._recorder.start()}stop(){return new Promise(e=>{this._recorder.onstop=()=>{const t=new Blob(this._chunks,{type:"video/webm"});this._chunks=[],e(t)},this._recorder.stop()})}get isRecording(){var e;return((e=this._recorder)==null?void 0:e.state)==="recording"}async stopAndDownload(e="theatre-export.webm"){const t=await this.stop(),n=URL.createObjectURL(t),i=document.createElement("a");i.href=n,i.download=e,i.click(),URL.revokeObjectURL(n)}}async function CD(){const r=await fetch("/api/character/scenes/");if(!r.ok)throw new Error(`Scene list error: ${r.status}`);return(await r.json()).scenes||[]}async function DD(r){const e=await fetch(`/api/character/scene/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Scene load error: ${e.status}`);return e.json()}async function ID(r,e){const t=await fetch("/api/character/scene/save/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:r,data:e})});if(!t.ok){const n=await t.json().catch(()=>({}));throw new Error(n.error||`Scene save error: ${t.status}`)}return t.json()}async function LD(){const r=await fetch("/api/character/models/");if(!r.ok)throw new Error(`Model list error: ${r.status}`);return(await r.json()).presets||[]}async function ug(r){const e=await fetch(`/api/character/model/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Model load error: ${e.status}`);return e.json()}async function FD(){const r=await fetch("/api/character/animations/");if(!r.ok)throw new Error(`Animation list error: ${r.status}`);return(await r.json()).categories||{}}async function ND(r,e){const t=`/api/character/bvh/${encodeURIComponent(r)}/${encodeURIComponent(e)}/`,n=await fetch(t);if(!n.ok)throw new Error(`BVH load error: ${n.status}`);return n.text()}const ph={ballet_stage:{name:"Ballet Stage",description:"Warme Spotlights, theatralisch dunkel",camera:{position:{x:0,y:1.6,z:5},fov:35},lights:{spotLeft:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:-3,y:6,z:3}},spotRight:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:3,y:6,z:3}},backLight:{intensity:25,color:{r:.4,g:.267,b:.667},position:{x:0,y:5,z:-4}}}},studio_bright:{name:"Studio Bright",description:"Helle, gleichmäßige Beleuchtung für Details",camera:{position:{x:0,y:1.6,z:4},fov:40},lights:{spotLeft:{intensity:80,color:{r:1,g:1,b:1},position:{x:-2,y:5,z:4}},spotRight:{intensity:80,color:{r:1,g:1,b:1},position:{x:2,y:5,z:4}},backLight:{intensity:30,color:{r:.9,g:.95,b:1},position:{x:0,y:4,z:-3}}}},cinematic_moody:{name:"Cinematic Moody",description:"Dramatisches Film-noir-Licht, starke Schatten",camera:{position:{x:2,y:1.4,z:4},fov:28},lights:{spotLeft:{intensity:15,color:{r:1,g:.8,b:.6},position:{x:-4,y:7,z:2}},spotRight:{intensity:2,color:{r:.6,g:.7,b:.9},position:{x:4,y:3,z:3}},backLight:{intensity:10,color:{r:.3,g:.5,b:1},position:{x:1,y:6,z:-5}}}},fashion_show:{name:"Fashion Show",description:"Laufsteg-Beleuchtung, kühles Weiß von oben",camera:{position:{x:0,y:1.2,z:6},fov:50},lights:{spotLeft:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:-2,y:8,z:2}},spotRight:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:2,y:8,z:2}},backLight:{intensity:5,color:{r:1,g:1,b:1},position:{x:0,y:3,z:-2}}}},sunset_warm:{name:"Sunset Warm",description:"Goldene Stunde, warmes Orange-Gold",camera:{position:{x:-1,y:1.5,z:4.5},fov:42},lights:{spotLeft:{intensity:14,color:{r:1,g:.7,b:.4},position:{x:-5,y:4,z:3}},spotRight:{intensity:6,color:{r:1,g:.85,b:.7},position:{x:3,y:5,z:2}},backLight:{intensity:8,color:{r:.8,g:.4,b:.6},position:{x:2,y:5,z:-4}}}}};function mh(r,e,t,n){console.log(`[Preset] Applying: ${r.name}`),e.position.set(r.camera.position.x,r.camera.position.y,r.camera.position.z),e.fov=r.camera.fov,e.updateProjectionMatrix(),n&&(n.target.set(0,.9,0),n.update()),gh(t.spotLeft,r.lights.spotLeft),gh(t.spotRight,r.lights.spotRight),gh(t.backLight,r.lights.backLight),console.log(`✓ Preset "${r.name}" applied (direct Three.js)`)}function gh(r,e){r&&(r.intensity=e.intensity,r.color.setRGB(e.color.r,e.color.g,e.color.b),r.position.set(e.position.x,e.position.y,e.position.z))}function OD(r){const e=new Set(r.map(t=>t.name));return e.has("Pelvis")&&e.has("Left_hip")?"AIST":e.has("Chest")&&e.has("UpperArm_L")?"BANDAI":e.has("Hips")&&e.has("LeftArm")?e.has("Spine2")?"MIXAMO":"CMU":e.has("hip")&&e.has("rShldr")?"OPENPOSE":e.has("hip")||e.has("rshoulder")?"MOCAPNET":"UNKNOWN"}const UD={Hips:"DEF-spine",Spine:"DEF-spine.001",Spine1:"DEF-spine.003",Neck:null,Neck1:"DEF-spine.004",Head:"DEF-spine.006",LeftShoulder:"DEF-shoulder.L",LeftArm:"DEF-upper_arm.L",LeftForeArm:"DEF-forearm.L",LeftHand:"DEF-hand.L",RightShoulder:"DEF-shoulder.R",RightArm:"DEF-upper_arm.R",RightForeArm:"DEF-forearm.R",RightHand:"DEF-hand.R",LeftUpLeg:"DEF-thigh.L",LeftLeg:"DEF-shin.L",LeftFoot:"DEF-foot.L",LeftToeBase:"DEF-toe.L",RightUpLeg:"DEF-thigh.R",RightLeg:"DEF-shin.R",RightFoot:"DEF-foot.R",RightToeBase:"DEF-toe.R",LHipJoint:null,RHipJoint:null,LowerBack:null,LeftFingerBase:null,RightFingerBase:null,LThumb:null,RThumb:null},BD={Hips:"DEF-spine",Spine:"DEF-spine.001",Spine1:"DEF-spine.002",Spine2:"DEF-spine.003",Neck:null,Neck1:"DEF-spine.004",Head:"DEF-spine.006",LeftShoulder:"DEF-shoulder.L",LeftArm:"DEF-upper_arm.L",LeftForeArm:"DEF-forearm.L",LeftHand:"DEF-hand.L",RightShoulder:"DEF-shoulder.R",RightArm:"DEF-upper_arm.R",RightForeArm:"DEF-forearm.R",RightHand:"DEF-hand.R",LeftUpLeg:"DEF-thigh.L",LeftLeg:"DEF-shin.L",LeftFoot:"DEF-foot.L",LeftToeBase:"DEF-toe.L",RightUpLeg:"DEF-thigh.R",RightLeg:"DEF-shin.R",RightFoot:"DEF-foot.R",RightToeBase:"DEF-toe.R",LeftHandThumb1:"DEF-thumb.01.L",LeftHandThumb2:"DEF-thumb.02.L",LeftHandThumb3:"DEF-thumb.03.L",LeftHandIndex1:"DEF-f_index.01.L",LeftHandIndex2:"DEF-f_index.02.L",LeftHandIndex3:"DEF-f_index.03.L",LeftHandMiddle1:"DEF-f_middle.01.L",LeftHandMiddle2:"DEF-f_middle.02.L",LeftHandMiddle3:"DEF-f_middle.03.L",LeftHandRing1:"DEF-f_ring.01.L",LeftHandRing2:"DEF-f_ring.02.L",LeftHandRing3:"DEF-f_ring.03.L",LeftHandPinky1:"DEF-f_pinky.01.L",LeftHandPinky2:"DEF-f_pinky.02.L",LeftHandPinky3:"DEF-f_pinky.03.L",RightHandThumb1:"DEF-thumb.01.R",RightHandThumb2:"DEF-thumb.02.R",RightHandThumb3:"DEF-thumb.03.R",RightHandIndex1:"DEF-f_index.01.R",RightHandIndex2:"DEF-f_index.02.R",RightHandIndex3:"DEF-f_index.03.R",RightHandMiddle1:"DEF-f_middle.01.R",RightHandMiddle2:"DEF-f_middle.02.R",RightHandMiddle3:"DEF-f_middle.03.R",RightHandRing1:"DEF-f_ring.01.R",RightHandRing2:"DEF-f_ring.02.R",RightHandRing3:"DEF-f_ring.03.R",RightHandPinky1:"DEF-f_pinky.01.R",RightHandPinky2:"DEF-f_pinky.02.R",RightHandPinky3:"DEF-f_pinky.03.R"},kD={hip:"DEF-spine",abdomen:"DEF-spine.001",chest:"DEF-spine.003",neck1:"DEF-spine.004",head:"DEF-spine.006",lcollar:"DEF-shoulder.L",rcollar:"DEF-shoulder.R",lshoulder:"DEF-upper_arm.L",rshoulder:"DEF-upper_arm.R",lelbow:"DEF-forearm.L",relbow:"DEF-forearm.R",lhand:"DEF-hand.L",rhand:"DEF-hand.R",lhip:"DEF-thigh.L",rhip:"DEF-thigh.R",lknee:"DEF-shin.L",rknee:"DEF-shin.R",lfoot:"DEF-foot.L",rfoot:"DEF-foot.R","toe1-1.l":"DEF-toe.L","toe1-1.r":"DEF-toe.R",lCollar:"DEF-shoulder.L",rCollar:"DEF-shoulder.R",lShldr:"DEF-upper_arm.L",rShldr:"DEF-upper_arm.R",lForeArm:"DEF-forearm.L",rForeArm:"DEF-forearm.R",lHand:"DEF-hand.L",rHand:"DEF-hand.R",lThigh:"DEF-thigh.L",rThigh:"DEF-thigh.R",lShin:"DEF-shin.L",rShin:"DEF-shin.R",lFoot:"DEF-foot.L",rFoot:"DEF-foot.R",lButtock:null,rButtock:null,"toe1-1.L":"DEF-toe.L","toe1-1.R":"DEF-toe.R",lthumb:"DEF-thumb.01.L","finger1-2.l":"DEF-thumb.02.L","finger1-3.l":"DEF-thumb.03.L","finger2-1.l":"DEF-f_index.01.L","finger2-2.l":"DEF-f_index.02.L","finger2-3.l":"DEF-f_index.03.L","finger3-1.l":"DEF-f_middle.01.L","finger3-2.l":"DEF-f_middle.02.L","finger3-3.l":"DEF-f_middle.03.L","finger4-1.l":"DEF-f_ring.01.L","finger4-2.l":"DEF-f_ring.02.L","finger4-3.l":"DEF-f_ring.03.L","finger5-1.l":"DEF-f_pinky.01.L","finger5-2.l":"DEF-f_pinky.02.L","finger5-3.l":"DEF-f_pinky.03.L",rthumb:"DEF-thumb.01.R","finger1-2.r":"DEF-thumb.02.R","finger1-3.r":"DEF-thumb.03.R","finger2-1.r":"DEF-f_index.01.R","finger2-2.r":"DEF-f_index.02.R","finger2-3.r":"DEF-f_index.03.R","finger3-1.r":"DEF-f_middle.01.R","finger3-2.r":"DEF-f_middle.02.R","finger3-3.r":"DEF-f_middle.03.R","finger4-1.r":"DEF-f_ring.01.R","finger4-2.r":"DEF-f_ring.02.R","finger4-3.r":"DEF-f_ring.03.R","finger5-1.r":"DEF-f_pinky.01.R","finger5-2.r":"DEF-f_pinky.02.R","finger5-3.r":"DEF-f_pinky.03.R","metacarpal1.l":"DEF-palm.01.L","metacarpal2.l":"DEF-palm.02.L","metacarpal3.l":"DEF-palm.03.L","metacarpal4.l":"DEF-palm.04.L","metacarpal1.r":"DEF-palm.01.R","metacarpal2.r":"DEF-palm.02.R","metacarpal3.r":"DEF-palm.03.R","metacarpal4.r":"DEF-palm.04.R",jaw:"DEF-jaw",tongue01:"DEF-tongue",tongue02:"DEF-tongue.001",tongue03:"DEF-tongue.002","eye.l":"MCH-eye.L","eye.r":"MCH-eye.R","oris04.l":"DEF-lip.T.L","oris04.r":"DEF-lip.T.R","oris03.l":"DEF-lip.T.L.001","oris03.r":"DEF-lip.T.R.001","oris06.l":"DEF-lip.B.L","oris06.r":"DEF-lip.B.R","oris07.l":"DEF-lip.B.L.001","oris07.r":"DEF-lip.B.R.001","orbicularis03.l":"DEF-lid.T.L","orbicularis03.r":"DEF-lid.T.R","orbicularis04.l":"DEF-lid.B.L","orbicularis04.r":"DEF-lid.B.R"},zD={Pelvis:"DEF-spine",Spine1:"DEF-spine.001",Spine2:"DEF-spine.002",Spine3:"DEF-spine.003",Neck:"DEF-spine.004",Head:"DEF-spine.006",Left_collar:"DEF-shoulder.L",Left_shoulder:"DEF-upper_arm.L",Left_elbow:"DEF-forearm.L",Left_wrist:"DEF-hand.L",Left_palm:null,Right_collar:"DEF-shoulder.R",Right_shoulder:"DEF-upper_arm.R",Right_elbow:"DEF-forearm.R",Right_wrist:"DEF-hand.R",Right_palm:null,Left_hip:"DEF-thigh.L",Left_knee:"DEF-shin.L",Left_ankle:"DEF-foot.L",Left_foot:"DEF-toe.L",Right_hip:"DEF-thigh.R",Right_knee:"DEF-shin.R",Right_ankle:"DEF-foot.R",Right_foot:"DEF-toe.R"},HD={hip:"DEF-spine",abdomen:"DEF-spine.001",chest:"DEF-spine.003",neck:null,neck1:"DEF-spine.004",head:"DEF-spine.006",lCollar:"DEF-shoulder.L",rCollar:"DEF-shoulder.R",lShldr:"DEF-upper_arm.L",rShldr:"DEF-upper_arm.R",lForeArm:"DEF-forearm.L",rForeArm:"DEF-forearm.R",lHand:"DEF-hand.L",rHand:"DEF-hand.R",lButtock:null,rButtock:null,lThigh:"DEF-thigh.L",rThigh:"DEF-thigh.R",lShin:"DEF-shin.L",rShin:"DEF-shin.R",lFoot:"DEF-foot.L",rFoot:"DEF-foot.R","toe1-1.L":"DEF-toe.L","toe1-1.R":"DEF-toe.R",lthumb:"DEF-thumb.01.L","finger1-2.l":"DEF-thumb.02.L","finger1-3.l":"DEF-thumb.03.L","finger2-1.l":"DEF-f_index.01.L","finger2-2.l":"DEF-f_index.02.L","finger2-3.l":"DEF-f_index.03.L","finger3-1.l":"DEF-f_middle.01.L","finger3-2.l":"DEF-f_middle.02.L","finger3-3.l":"DEF-f_middle.03.L","finger4-1.l":"DEF-f_ring.01.L","finger4-2.l":"DEF-f_ring.02.L","finger4-3.l":"DEF-f_ring.03.L","finger5-1.l":"DEF-f_pinky.01.L","finger5-2.l":"DEF-f_pinky.02.L","finger5-3.l":"DEF-f_pinky.03.L",rthumb:"DEF-thumb.01.R","finger1-2.r":"DEF-thumb.02.R","finger1-3.r":"DEF-thumb.03.R","finger2-1.r":"DEF-f_index.01.R","finger2-2.r":"DEF-f_index.02.R","finger2-3.r":"DEF-f_index.03.R","finger3-1.r":"DEF-f_middle.01.R","finger3-2.r":"DEF-f_middle.02.R","finger3-3.r":"DEF-f_middle.03.R","finger4-1.r":"DEF-f_ring.01.R","finger4-2.r":"DEF-f_ring.02.R","finger4-3.r":"DEF-f_ring.03.R","finger5-1.r":"DEF-f_pinky.01.R","finger5-2.r":"DEF-f_pinky.02.R","finger5-3.r":"DEF-f_pinky.03.R","metacarpal1.l":"DEF-palm.01.L","metacarpal2.l":"DEF-palm.02.L","metacarpal3.l":"DEF-palm.03.L","metacarpal4.l":"DEF-palm.04.L","metacarpal1.r":"DEF-palm.01.R","metacarpal2.r":"DEF-palm.02.R","metacarpal3.r":"DEF-palm.03.R","metacarpal4.r":"DEF-palm.04.R",jaw:"DEF-jaw",tongue01:"DEF-tongue",tongue02:"DEF-tongue.001",tongue03:"DEF-tongue.002","eye.l":"MCH-eye.L","eye.r":"MCH-eye.R","oris04.l":"DEF-lip.T.L","oris04.r":"DEF-lip.T.R","oris03.l":"DEF-lip.T.L.001","oris03.r":"DEF-lip.T.R.001","oris06.l":"DEF-lip.B.L","oris06.r":"DEF-lip.B.R","oris07.l":"DEF-lip.B.L.001","oris07.r":"DEF-lip.B.R.001","orbicularis03.l":"DEF-lid.T.L","orbicularis03.r":"DEF-lid.T.R","orbicularis04.l":"DEF-lid.B.L","orbicularis04.r":"DEF-lid.B.R"},VD={Hips:"DEF-spine",Spine:"DEF-spine.001",Chest:"DEF-spine.003",Neck:"DEF-spine.004",Head:"DEF-spine.006",Shoulder_L:"DEF-shoulder.L",UpperArm_L:"DEF-upper_arm.L",LowerArm_L:"DEF-forearm.L",Hand_L:"DEF-hand.L",Shoulder_R:"DEF-shoulder.R",UpperArm_R:"DEF-upper_arm.R",LowerArm_R:"DEF-forearm.R",Hand_R:"DEF-hand.R",UpperLeg_L:"DEF-thigh.L",LowerLeg_L:"DEF-shin.L",Foot_L:"DEF-foot.L",Toes_L:"DEF-toe.L",UpperLeg_R:"DEF-thigh.R",LowerLeg_R:"DEF-shin.R",Foot_R:"DEF-foot.R",Toes_R:"DEF-toe.R",joint_Root:null};function GD(r,e,t,n={}){const i=r.skeleton.bones,s=r.clip,a=t==="CMU"?UD:t==="MIXAMO"?BD:t==="BANDAI"?VD:t==="AIST"?zD:t==="OPENPOSE"?HD:kD;e.rootBone.updateWorldMatrix(!0,!0);const l={},u={},h=new Map;for(const[de,be]of Object.entries(e.boneByName))h.set(be,de);for(const[de,be]of Object.entries(e.boneByName)){l[de]=new Dt,be.getWorldQuaternion(l[de]);const Oe=h.get(be.parent);Oe&&l[Oe]?u[de]=l[Oe]:be.parent&&(u[de]=new Dt,be.parent.getWorldQuaternion(u[de]))}const f={};for(const de of i)f[de.name]=de;const p=i[0],m=[],g={};function x(de){m.push(de.name);for(const be of de.children)be.isBone&&(g[be.name]=de.name,x(be))}x(p);const E={};for(const[de,be]of Object.entries(a))be&&f[de]&&e.boneByName[be]&&(E[be]=de);const v=new Set(Object.keys(E));console.log(`[RETARGET] ${v.size} bones mapped`);const _={},R={};for(const de of s.tracks){const be=de.name.lastIndexOf(".");if(be<0)continue;const Oe=de.name.substring(0,be),V=de.name.substring(be+1);V==="quaternion"&&(_[Oe]=de),V==="position"&&(R[Oe]=de)}const w=new Ti,S=new Dt,k=new F;function N(de,be,Oe){k.copy(de.position).applyQuaternion(be);const V=Oe.clone().add(k);w.expandByPoint(V),S.copy(be).multiply(de.quaternion);for(const ct of de.children)ct.isBone&&N(ct,S.clone(),V)}N(p,new Dt,new F);const O=Math.max(w.max.y-w.min.y,.01);let H=1.68;if(n.bodyMesh){const de=new Ti().setFromObject(n.bodyMesh);de.isEmpty()||(H=de.max.y-de.min.y)}const D=H/O,A={};for(const[de,be]of Object.entries(e.boneByName))u[de]?A[de]=u[de].clone().invert().multiply(l[de]):A[de]=l[de].clone();const z={},Z=t==="BANDAI";if(Z){const de=new Dt;for(const be of m){const Oe=_[be];Oe?de.set(Oe.values[0],Oe.values[1],Oe.values[2],Oe.values[3]):de.set(0,0,0,1);const V=g[be];V&&z[V]?z[be]=z[V].clone().multiply(de):z[be]=de.clone()}}const $=new F(0,0,-1),ie={},ae=Object.values(a).find(de=>de&&e.boneByName[de]),X=new Set;t==="AIST"&&(X.add("DEF-foot.L"),X.add("DEF-foot.R"),X.add("DEF-toe.L"),X.add("DEF-toe.R"),X.add("DEF-spine.004"),X.add("DEF-spine.006")),t==="MOCAPNET"&&(X.add("DEF-foot.L"),X.add("DEF-foot.R"),X.add("DEF-toe.L"),X.add("DEF-toe.R"),X.add("DEF-jaw"),X.add("DEF-spine.004"),X.add("DEF-spine.006")),t==="OPENPOSE"&&(X.add("DEF-foot.L"),X.add("DEF-foot.R"),X.add("DEF-toe.L"),X.add("DEF-toe.R"),X.add("DEF-jaw"),X.add("DEF-spine.004"),X.add("DEF-spine.006"),X.add("DEF-shoulder.L"),X.add("DEF-shoulder.R"));for(const[de,be]of Object.entries(E)){if(de===ae||X.has(de)){ie[de]=l[de].clone();continue}const Oe=$.clone().applyQuaternion(l[de]).normalize(),V=f[be];let ct=null,it=-1/0;for(const tt of V.children)if(tt.isBone&&tt.position.lengthSq()>1e-10){let ze;Z&&z[be]?ze=tt.position.clone().applyQuaternion(z[be]).normalize():ze=tt.position.clone().normalize();const dt=ze.dot(Oe);dt>it&&(it=dt,ct=ze)}if(!ct&&V.position.lengthSq()>1e-10)if(Z){const tt=g[be];tt&&z[tt]?ct=V.position.clone().applyQuaternion(z[tt]).normalize():ct=V.position.clone().normalize()}else ct=V.position.clone().normalize();if(!ct||ct.lengthSq()<1e-10)ie[de]=l[de].clone();else{const tt=new Dt().setFromUnitVectors(Oe,ct);ie[de]=tt.multiply(l[de])}}const he=Object.keys(e.boneByName).sort((de,be)=>{let Oe=0,V=e.boneByName[de];for(;V.parent;)Oe++,V=V.parent;let ct=0,it=e.boneByName[be];for(;it.parent;)ct++,it=it.parent;return Oe-ct}),te=Object.values(_)[0];if(!te)return new ao("retargeted",0,[]);const ye=te.times,Ee=ye.length,ke={};for(const de of v)ke[de]=new Float32Array(Ee*4);const Xe=new Dt,Tt=new Dt,ce={},ge={};let Be=null;if(n.footCorrection){Be={};const de=new Dt,be=new F,Oe=180/Math.PI,V=15,ct=1.5;for(const it of["DEF-foot.L","DEF-foot.R"]){const tt=E[it];if(!tt)continue;const ze=[];let dt=tt;for(;dt;)ze.unshift(dt),dt=g[dt];const Ve=new Float32Array(Ee);let L=0,T=0;for(let K=0;K<Ee;K++){const ue=K*4;let me=new Dt;for(const Le of ze){const Ae=_[Le];Ae?de.set(Ae.values[ue],Ae.values[ue+1],Ae.values[ue+2],Ae.values[ue+3]):de.set(0,0,0,1),me.multiply(de)}be.set(0,0,-1).applyQuaternion(me);const le=Math.asin(Math.max(-1,Math.min(1,-be.y)))*Oe;if(le>T&&(T=le),le>V){const Le=Math.min(90,le+(le-V)*ct),Ae=90-le;Ve[K]=Ae>.1?Math.min((Le-le)/Ae,1):0}Ve[K]>L&&(L=Ve[K])}Be[it]=Ve,console.log(`[FOOT-CORRECTION] ${it}: maxAngle=${T.toFixed(1)}, thresh=${V}, boost=${ct}x, maxCorr=${L.toFixed(2)}`)}Object.keys(Be).length===0&&(Be=null)}for(let de=0;de<Ee;de++){const be=de*4;for(const Oe of m){const V=_[Oe];V?Xe.set(V.values[be],V.values[be+1],V.values[be+2],V.values[be+3]):Xe.set(0,0,0,1);const ct=g[Oe];ct&&ge[ct]?ge[Oe]=ge[ct].clone().multiply(Xe):ge[Oe]=Xe.clone()}for(const Oe of he){const V=e.boneByName[Oe],ct=h.get(V.parent),it=ct&&ce[ct]?ce[ct]:new Dt;if(v.has(Oe)){const tt=E[Oe];if(Z){const dt=ge[tt],Ve=z[tt];dt&&Ve?(Tt.copy(dt).multiply(Ve.clone().invert()).multiply(ie[Oe]).normalize(),Xe.copy(it).invert().multiply(Tt).normalize()):Xe.copy(A[Oe]||new Dt)}else{const dt=ge[tt];dt?(Tt.copy(dt).multiply(ie[Oe]).normalize(),Xe.copy(it).invert().multiply(Tt).normalize()):Xe.copy(A[Oe]||new Dt)}if(Be&&Be[Oe]){const dt=Be[Oe][de];if(dt>.01){const Ve=it.clone().multiply(Xe),L=new F(0,0,-1).applyQuaternion(Ve).normalize(),T=new F(0,-1,0),ue=new Dt().setFromUnitVectors(L,T).multiply(Ve),me=it.clone().invert().multiply(ue).normalize();Xe.slerp(me,dt)}}const ze=ke[Oe];ze[be]=Xe.x,ze[be+1]=Xe.y,ze[be+2]=Xe.z,ze[be+3]=Xe.w,ce[Oe]=it.clone().multiply(Xe)}else ce[Oe]=it.clone().multiply(A[Oe]||new Dt)}}const Me=[];for(const de of v){const be=e.boneByName[de];Me.push(new wr(`${be.name}.quaternion`,ye,ke[de]))}const ot=i[0].name;let ut=a[ot];const Ke=R[ot];if(!ut&&Ke){for(const de of i[0].children)if(de.isBone&&a[de.name]){ut=a[de.name];break}}if(ut&&Ke){const de=e.boneByName[ut];if(de){const be=new F(Ke.values[0],Ke.values[1],Ke.values[2]),Oe=de.position.clone(),V=new Float32Array(Ke.values.length);for(let ct=0;ct<Ke.values.length;ct+=3)V[ct]=Oe.x+(Ke.values[ct]-be.x)*D,V[ct+1]=Oe.y+(Ke.values[ct+1]-be.y)*D,V[ct+2]=Oe.z+(Ke.values[ct+2]-be.z)*D;Me.push(new Ar(`${de.name}.position`,Ke.times,V))}}return console.log(`[RETARGET] ${Me.length} tracks, ${Ee} frames`),new ao("retargeted",s.duration,Me)}window.addEventListener("DOMContentLoaded",()=>{const r=document.getElementById("theatre-canvas");if(!r){console.error("theatre-canvas not found");return}const{scene:e,camera:t,renderer:n,controls:i,lights:s,lightIcons:a,transformControls:l}=OC(r);window.scene=e,window.lights=s,window.lightIcons=a,window.transformControls=l,window.activeMixer=null,window.isPlaying=!1,window.currentTime=0,window.animDuration=1;const u=new Qg,h=new vt;let f=null,p=null;const m=[];let g=null,x=null,E=null,v=null,_=null,R=!1;function w(U,ne){const fe={};for(const at of U.bones)fe[at.name]=at;const ve=[],Je={};let Te=null;for(const at of ne.bone_names){const ht=new Gl;ht.name=at.replace(/\./g,"_"),ve.push(ht),Je[at]=ht}for(let at=0;at<ne.bone_names.length;at++){const ht=ne.bone_names[at],yt=ve[at],Et=fe[ht];if(!Et)continue;const je=Et.local_position;yt.position.set(je[0],je[2],-je[1]);const nt=Et.local_quaternion;yt.quaternion.set(nt[1],nt[3],-nt[2],nt[0]),Et.parent&&Je[Et.parent]?Je[Et.parent].add(yt):Te||(Te=yt)}for(let at=0;at<ve.length;at++){const ht=ne.bone_names[at],yt=fe[ht];yt&&!yt.parent&&ve[at]!==Te&&Te&&Te.add(ve[at])}return!Te&&ve.length>0&&(Te=ve[0]),Te.updateWorldMatrix(!0,!0),{skeleton:new sa(ve),rootBone:Te,bones:ve,boneByName:Je}}async function S(){return E||(E=(async()=>{var U;try{const[ne,fe]=await Promise.all([fetch("/api/character/def-skeleton/"),fetch("/api/character/skin-weights/")]);ne.ok&&(g=await ne.json()),fe.ok&&(x=await fe.json()),console.log("✓ Loaded skeleton and skin weights:",((U=g==null?void 0:g.bones)==null?void 0:U.length)||0,"bones"),g&&x&&(v=w(g,x),console.log("✓ Built defSkeleton:",v.bones.length,"bones"),window.defSkeletonData=g,window.defSkeleton=v);for(const ve of m)ve.userData.isSkinnedMesh||k(ve)}catch(ne){console.warn("Failed to load skeleton/weights:",ne)}})(),E)}S();function k(U){g&&x&&!U.userData.isSkinnedMesh&&setTimeout(()=>{try{O(U,e),console.log("✓ Auto-converted to SkinnedMesh:",U.userData.presetName)}catch(ne){console.warn("Auto-convert failed:",ne)}},100)}function N(U,ne,fe,ve){const Te=new n_().parse(U);if(!g)throw console.error("DEF skeleton data not loaded - cannot retarget animation"),new Error("Skeleton data not loaded");if(!ne||!ne.skeleton)throw console.error("SkinnedMesh has no skeleton"),new Error("SkinnedMesh not properly initialized");if(!ne.skeleton.bones||ne.skeleton.bones.length===0)throw console.error("SkinnedMesh skeleton has no bones"),new Error("Skeleton has no bones");if(!v||!v.boneByName)throw console.error("Global defSkeleton not loaded - cannot retarget"),new Error("Skeleton not ready");const qe=Te.skeleton.bones,at=OD(qe);console.log(`BVH format detected: ${at}, retargeting to DEF skeleton...`);const ht=GD(Te,v,at,{bodyMesh:ne});if(!ht||ht.tracks.length===0)throw console.error("Retargeting failed - no tracks generated"),new Error("Retargeting failed");console.log(`✓ Retargeted clip: ${ht.tracks.length} tracks, ${ht.duration.toFixed(2)}s`);const yt=new Zg(ne),Et=yt.clipAction(ht);Et.setLoop(_d),Et.play(),Et.paused=!0;const je=ht.duration||1;return console.log("✓ BVH animation loaded on SkinnedMesh:",ve,je+"s"),{mixer:yt,action:Et,duration:je}}function O(U,ne){if(!g||!x)return console.warn("Cannot convert to SkinnedMesh: skeleton/weights not loaded"),null;if(U.userData.isSkinnedMesh)return console.log("Already a SkinnedMesh"),U.userData.skinnedMesh;const fe=U.children.find(rt=>rt.isMesh&&!rt.userData.isHair&&!rt.userData.isGarment);if(!fe)return console.warn("No body mesh found in character group"),null;console.log("Converting to SkinnedMesh...");const ve=fe.geometry.clone(),Je=ve.attributes.position.count,Te=new Float32Array(Je*4),qe=new Float32Array(Je*4);for(let rt=0;rt<Je;rt++){const Lt=(x.weights[rt]||[]).slice().sort((P,j)=>j[1]-P[1]).slice(0,4);let st=Lt.reduce((P,j)=>P+j[1],0);st<1e-6&&(st=1);for(let P=0;P<4;P++)Te[rt*4+P]=P<Lt.length?Lt[P][0]:0,qe[rt*4+P]=P<Lt.length?Lt[P][1]/st:0}ve.setAttribute("skinIndex",new Wt(Te,4)),ve.setAttribute("skinWeight",new Wt(qe,4)),v||(v=w(g,x));const at=fe.material,ht=fe.position.clone(),yt=fe.rotation.clone(),Et=fe.scale.clone(),je=new Ul(ve,at);je.position.copy(ht),je.rotation.copy(yt),je.scale.copy(Et),je.castShadow=!0,je.receiveShadow=!0,je.add(v.rootBone),je.bind(v.skeleton),U.remove(fe),U.add(je),U.userData.isSkinnedMesh=!0,U.userData.skinnedMesh=je,U.userData.skeleton=v.skeleton,U.userData.rootBone=v.rootBone,console.log("✓ SkinnedMesh created:","bones:",v.skeleton.bones.length,"skinIndex:",!!ve.attributes.skinIndex,"skinWeight:",!!ve.attributes.skinWeight),window.loadedCharacters=window.loadedCharacters||[],window.loadedCharacters.includes(U)||window.loadedCharacters.push(U),U.traverse(rt=>{rt.isSkinnedMesh&&rt!==je&&rt.userData.needsBinding&&(rt.add(v.rootBone),rt.bind(v.skeleton,je.bindMatrix),delete rt.userData.needsBinding,console.log("✓ Garment bound to skeleton:",rt.name||rt.userData.garmentId))});const nt=[];U.traverse(rt=>{rt.userData.isHair&&rt.isGroup&&nt.push(rt)});for(const rt of nt){const Ut=H();if(Ut>=0){const Lt=D(rt,Ut,je),st=rt.parent;st&&(st.remove(rt),st.add(Lt),console.log("✓ Hair converted to SkinnedMesh"))}}return je}function H(){if(!x)return-1;const U=x.bone_names;for(const ne of["DEF-spine.006","DEF-spine.005","DEF-head"]){const fe=U.indexOf(ne);if(fe>=0)return fe}return-1}function D(U,ne,fe){const ve=[];U.traverse(Te=>{Te.isMesh&&ve.push(Te)});const Je=new Ii;Je.userData.isHair=!0;for(const Te of ve){const qe=Te.geometry.clone(),at=qe.attributes.position.count,ht=new Float32Array(at*4),yt=new Float32Array(at*4);for(let je=0;je<at;je++)ht[je*4]=ne,yt[je*4]=1;qe.setAttribute("skinIndex",new Wt(ht,4)),qe.setAttribute("skinWeight",new Wt(yt,4));const Et=new Ul(qe,Te.material);Te.updateWorldMatrix(!0,!1),Et.applyMatrix4(Te.matrixWorld),Et.bind(v.skeleton,fe.bindMatrix),Et.userData.isHair=!0,Je.add(Et)}return Je}r.addEventListener("click",U=>{const ne=r.getBoundingClientRect();h.x=(U.clientX-ne.left)/ne.width*2-1,h.y=-((U.clientY-ne.top)/ne.height)*2+1,u.setFromCamera(h,t);const fe=[a.spotLeftIcon,a.spotRightIcon,a.backLightIcon],ve=u.intersectObjects(fe,!0);if(ve.length>0){let Te=ve[0].object;for(;Te.parent&&!Te.userData.light;)Te=Te.parent;if(Te.userData.light){f=Te,p=null,l.attach(Te),console.log("✓ Licht ausgewählt:",Te.userData.light),Re(Te.userData.light);return}}const Je=u.intersectObjects(m,!0);if(Je.length>0){const Te=Je[0].object;if(Te.userData.isGarment){p=null,f=null,l.attach(Te),console.log("✓ Garment ausgewählt:",Te.name),oe(Te);return}let qe=Te;for(;qe.parent&&!qe.userData.isCharacter;)qe=qe.parent;if(qe.userData.isCharacter){p=qe,f=null,l.attach(qe),console.log("✓ Character ausgewählt:",qe.userData.presetName),pe(qe);return}}l.detach(),f=null,p=null,Zt()});const{sheet:A}=BC();kC(A,t),Ml(A,"Spot Left",s.spotLeft),Ml(A,"Spot Right",s.spotRight),Ml(A,"Back Light",s.backLight);const z=new PD(n.domElement);let Z=null,$=null;const ie=new eC;document.querySelectorAll(".menu-item").forEach(U=>{const ne=U.querySelector(".menu-dropdown");ne&&(U.addEventListener("click",fe=>{fe.stopPropagation(),document.querySelectorAll(".menu-item").forEach(ve=>ve.classList.remove("active")),U.classList.toggle("active")}),ne.addEventListener("click",fe=>{fe.stopPropagation()}))}),document.addEventListener("click",()=>{document.querySelectorAll(".menu-item").forEach(U=>U.classList.remove("active"))}),document.querySelectorAll("[data-preset]").forEach(U=>{U.addEventListener("click",()=>{const ne=U.getAttribute("data-preset"),fe=ph[ne];fe?(mh(fe,t,s,i),console.log("✓ Applied preset:",fe.name),document.querySelectorAll(".menu-item").forEach(ve=>ve.classList.remove("active"))):console.error("Preset not found:",ne)})}),document.querySelectorAll(".panel-tab").forEach(U=>{U.addEventListener("click",()=>{const ne=U.getAttribute("data-tab");document.querySelectorAll(".panel-tab").forEach(ve=>ve.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(ve=>ve.classList.remove("active")),U.classList.add("active");const fe=document.getElementById(ne);fe&&fe.classList.add("active")})});const ae=document.getElementById("btn-translate-mode"),X=document.getElementById("btn-rotate-mode"),he=document.getElementById("btn-toggle-lights");ae&&ae.addEventListener("click",()=>{l.setMode("translate"),ae.classList.add("active"),X.classList.remove("active")}),X&&X.addEventListener("click",()=>{l.setMode("rotate"),X.classList.add("active"),ae.classList.remove("active")});let te=!0;he&&he.addEventListener("click",()=>{te=!te,Object.values(a).forEach(U=>{U.visible=te}),te?he.classList.add("active"):he.classList.remove("active")});const ye=document.getElementById("btn-toggle-model");let Ee=!0;ye&&ye.addEventListener("click",()=>{Ee=!Ee,e.traverse(U=>{U.isMesh&&!U.userData.isGarment&&!U.userData.isHair&&!U.userData.isRig&&(U.visible=Ee)}),ye.classList.toggle("active",Ee)});const ke=document.getElementById("btn-toggle-clothes");let Xe=!0;ke&&ke.addEventListener("click",()=>{Xe=!Xe,e.traverse(U=>{U.isMesh&&(U.userData.isGarment||U.userData.isHair)&&(U.visible=Xe)}),ke.classList.toggle("active",Xe)});const Tt=document.getElementById("btn-toggle-rig");Tt&&Tt.addEventListener("click",()=>{R=!R,R?(!_&&v&&(_=new Jg(v.rootBone),_.material.depthTest=!1,_.material.depthWrite=!1,_.material.color.set(65450),_.material.linewidth=2,_.renderOrder=999,e.add(_),console.log("✓ SkeletonHelper created")),_&&(_.visible=!0)):_&&(_.visible=!1),Tt.classList.toggle("active",R)});const ce=document.getElementById("btn-play-animation");ce&&ce.addEventListener("click",()=>{const U=document.getElementById("btnPlayPause");U&&U.click()});function ge(U){const ne=document.getElementById(U);ne&&(ne.style.display="flex")}function Be(U){const ne=document.getElementById(U);ne&&(ne.style.display="none")}document.querySelectorAll("[data-close-modal]").forEach(U=>{U.addEventListener("click",()=>{var ne;(ne=U.closest(".theatre-modal-overlay"))==null||ne.style.removeProperty("display")})}),document.querySelectorAll(".theatre-modal-overlay").forEach(U=>{U.addEventListener("click",ne=>{ne.target===U&&U.style.removeProperty("display")})});const Me=document.getElementById("menu-scene-load");Me&&Me.addEventListener("click",async()=>{const U=document.getElementById("scene-list-body");U.innerHTML='<div class="loading-msg">Lade Scenes...</div>',ge("modal-scene-load");try{const ne=await CD();if(ne.length===0){U.innerHTML='<div class="loading-msg">Keine Scenes gefunden.</div>';return}U.innerHTML="";for(const fe of ne){const ve=document.createElement("div");ve.style.cssText="padding:10px 14px;border-radius:6px;cursor:pointer;color:#ccc;font-size:0.85rem;",ve.innerHTML=`<span>${fe.label||fe.name}</span>`,ve.addEventListener("click",()=>ot(fe.name)),ve.addEventListener("mouseenter",()=>ve.style.background="rgba(124, 92, 191, 0.2)"),ve.addEventListener("mouseleave",()=>ve.style.background=""),U.appendChild(ve)}}catch(ne){U.innerHTML=`<div class="loading-msg">Fehler: ${ne.message}</div>`}});async function ot(U){Be("modal-scene-load");try{const ne=await DD(U);if(console.log("Scene loaded:",U,ne),ne.characters&&Array.isArray(ne.characters))for(const fe of ne.characters){const ve=await fh(e,fe,fe.name||U);ve.userData.isCharacter=!0,ve.userData.presetName=fe.name||U,ve.userData.bodyType=fe.body_type||"Unknown",m.push(ve),p=ve,k(ve)}}catch(ne){console.error("Scene load error:",ne),alert("Scene laden fehlgeschlagen: "+ne.message)}}const ut=document.getElementById("menu-scene-save"),Ke=document.getElementById("scene-save-btn"),de=document.getElementById("scene-save-name");ut&&ut.addEventListener("click",()=>{ge("modal-scene-save"),de&&(de.value="",de.focus())}),Ke&&de&&(Ke.addEventListener("click",async()=>{const U=de.value.trim();if(U){Ke.disabled=!0,Ke.textContent="Speichere...";try{const ne={camera:{position:t.position.toArray(),fov:t.fov,target:i.target.toArray()},lights:{spotLeft:{position:s.spotLeft.position.toArray(),intensity:s.spotLeft.intensity,color:"#"+s.spotLeft.color.getHexString()},spotRight:{position:s.spotRight.position.toArray(),intensity:s.spotRight.intensity,color:"#"+s.spotRight.color.getHexString()},backLight:{position:s.backLight.position.toArray(),intensity:s.backLight.intensity,color:"#"+s.backLight.color.getHexString()}},characters:[]},fe=await ID(U,ne);console.log("Scene saved:",fe),Be("modal-scene-save")}catch(ne){console.error("Scene save error:",ne),alert("Scene speichern fehlgeschlagen: "+ne.message)}Ke.disabled=!1,Ke.textContent="Speichern"}}),de.addEventListener("keydown",U=>{U.key==="Enter"&&Ke.click()}));const be=document.getElementById("model-list"),Oe=document.getElementById("menu-model-load");async function V(){try{const U=await LD();if(U.length===0){be.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Modelle gefunden.</div>';return}be.innerHTML="";for(const ne of U){const fe=document.createElement("div");fe.className="anim-item",fe.textContent=ne.label||ne.name,fe.addEventListener("click",async()=>{try{const ve=await ug(ne.name),Je=await fh(e,ve,ne.name);Je.userData.isCharacter=!0,Je.userData.presetName=ne.name,Je.userData.bodyType=ve.body_type||"Unknown",m.push(Je),p=Je,k(Je),console.log("Model loaded:",ne.name),document.querySelectorAll("#model-list .anim-item").forEach(Te=>Te.classList.remove("active")),fe.classList.add("active")}catch(ve){console.error("Model load error:",ve),alert("Modell laden fehlgeschlagen: "+ve.message)}}),be.appendChild(fe)}}catch(U){be.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${U.message}</div>`}}V(),Oe&&Oe.addEventListener("click",()=>{document.querySelectorAll(".panel-tab").forEach(fe=>fe.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(fe=>fe.classList.remove("active"));const U=document.querySelector('[data-tab="tab-models"]'),ne=document.getElementById("tab-models");U&&U.classList.add("active"),ne&&ne.classList.add("active")});const ct=document.getElementById("anim-tree");async function it(){try{const U=await FD(),ne=Object.keys(U);if(ne.length===0){ct.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden.</div>';return}ct.innerHTML="";for(const fe of ne){const ve=U[fe],Je=document.createElement("div");Je.className="anim-cat";const Te=document.createElement("div");Te.className="anim-cat-header",Te.innerHTML=`<i class="fas fa-chevron-right"></i> ${fe} (${ve.length})`,Te.addEventListener("click",()=>{Je.classList.toggle("open")}),Je.appendChild(Te);const qe=document.createElement("div");qe.className="anim-cat-body";for(const at of ve){const ht=document.createElement("div");ht.className="anim-item",ht.textContent=at.name,ht.addEventListener("click",async()=>{await tt(at.category,at.name),document.querySelectorAll("#anim-tree .anim-item").forEach(yt=>yt.classList.remove("active")),ht.classList.add("active")}),qe.appendChild(ht)}Je.appendChild(qe),ct.appendChild(Je)}}catch(U){ct.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${U.message}</div>`}}async function tt(U,ne){try{const fe=await ND(U,ne);let ve=null;p?(console.log("Selected character found, converting to SkinnedMesh..."),ve=O(p,e),console.log("targetMesh:",!!ve,"isSkinnedMesh:",ve==null?void 0:ve.isSkinnedMesh)):console.log("No selected character - using BVH bones only");const{mixer:Je,action:Te,duration:qe}=ve?N(fe,ve,e,`${U}/${ne}`):RD(fe,e,`${U}/${ne}`);Z&&Z.stopAllAction(),Z=Je,$=Te,window.activeMixer=Z,We(qe),_e=!1,Ce=0,Ge=qe,window.isPlaying=!1,window.currentTime=0,window.animDuration=qe,mt(),console.log("Animation loaded:",U,ne,qe)}catch(fe){console.error("Animation load error:",fe),alert("Animation laden fehlgeschlagen: "+fe.message)}}it();const ze=document.getElementById("menu-add-glb"),dt=document.getElementById("glb-file-input");ze&&dt&&(ze.addEventListener("click",()=>dt.click()),dt.addEventListener("change",async()=>{const U=dt.files[0];if(U){try{await ED(U,e)}catch(ne){console.error("GLB load error:",ne),alert("Fehler beim Laden der GLB-Datei: "+ne.message)}dt.value=""}})),document.querySelectorAll("[data-preset]").forEach(U=>{U.addEventListener("click",()=>{const ne=U.getAttribute("data-preset"),fe=ph[ne];fe?(mh(fe,t,s,i),console.log("✓ Applied preset:",fe.name)):console.error("Preset not found:",ne)})});const Ve=document.getElementById("menu-add-light");let L=0;Ve&&Ve.addEventListener("click",()=>{L++;const U=new $g(16777215,1,15);U.position.set((Math.random()-.5)*6,2+Math.random()*3,(Math.random()-.5)*6),e.add(U);const ne=new Pe(new oa(.08,8,8),new mi({color:16776960}));U.add(ne),Ml(A,`Light ${L}`,U)});const T=document.getElementById("menu-export-video");T&&T.addEventListener("click",async()=>{z.isRecording?(T.innerHTML='<i class="fas fa-file-video"></i> Export Video',await z.stopAndDownload()):(z.start(30),T.innerHTML='<i class="fas fa-stop"></i> Stop Recording')});const K=document.getElementById("btnPlayPause"),ue=document.getElementById("btnStop"),me=document.getElementById("btnFrameBack"),le=document.getElementById("btnFrameFwd"),Le=document.getElementById("timelineSlider"),Ae=document.getElementById("timeCurrent"),He=document.getElementById("timeDuration"),Pt=document.getElementById("playIcon");let _e=!1,Ce=0,Ge=1,ft=1;function We(U){Ge=U||1,He.textContent=At(Ge),Le.max=Ge}function At(U){const ne=Math.floor(U/60),fe=Math.floor(U%60);return`${String(ne).padStart(2,"0")}:${String(fe).padStart(2,"0")}`}function mt(){Ae.textContent=At(Ce),Le.value=Ce,Pt&&(Pt.className=_e?"fas fa-pause":"fas fa-play")}function Ot(U){!Z||!$||(Ce=Math.max(0,Math.min(U,Ge)),$.time=Ce,Z.update(0),mt())}K&&K.addEventListener("click",()=>{Z&&(_e=!_e,window.isPlaying=_e,_e&&$?($.paused=!1,$.play()):$&&($.paused=!0),mt())}),ue&&ue.addEventListener("click",()=>{Z&&(_e=!1,Ce=0,Ot(0),$&&($.stop(),$.paused=!0),mt())}),me&&me.addEventListener("click",()=>{Ot(Ce-1/30)}),le&&le.addEventListener("click",()=>{Ot(Ce+1/30)}),Le&&(Le.addEventListener("mousedown",()=>{}),Le.addEventListener("mouseup",()=>{}),Le.addEventListener("input",()=>{const U=parseFloat(Le.value);Ot(U)})),document.querySelectorAll(".speed-btn").forEach(U=>{U.addEventListener("click",()=>{const ne=parseFloat(U.getAttribute("data-speed"));ft=ne,Z&&(Z.timeScale=ne),document.querySelectorAll(".speed-btn").forEach(fe=>fe.classList.remove("active")),U.classList.add("active")})}),document.addEventListener("keydown",U=>{U.target.tagName!=="INPUT"&&(U.code==="Space"?(U.preventDefault(),K&&K.click()):U.code==="ArrowLeft"?(U.preventDefault(),me&&me.click()):U.code==="ArrowRight"&&(U.preventDefault(),le&&le.click()))});async function W(){try{const U=await fetch("/api/settings/theatre/");if(!U.ok)return;const ne=await U.json();if(ne.preset){const fe=ph[ne.preset];fe&&(mh(fe,t,s,i),console.log("✓ Auto-applied preset:",fe.name))}if(ne.model)try{const fe=await ug(ne.model),ve=await fh(e,fe,ne.model);if(ve.userData.isCharacter=!0,ve.userData.presetName=ne.model,ve.userData.bodyType=fe.body_type||"Unknown",m.push(ve),p=ve,k(ve),console.log("✓ Auto-loaded model:",ne.model),ne.animation){const[Je,Te]=ne.animation.split("/");Je&&Te&&(await tt(Je,Te),console.log("✓ Auto-loaded animation:",ne.animation))}}catch(fe){console.warn("Auto-load model/animation failed:",fe)}}catch(U){console.warn("Failed to load Theatre defaults:",U)}}setTimeout(W,500);function Re(U){document.querySelectorAll(".panel-tab").forEach(Lt=>Lt.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Lt=>Lt.classList.remove("active"));const ne=document.querySelector('[data-tab="tab-properties"]'),fe=document.getElementById("tab-properties");ne&&ne.classList.add("active"),fe&&fe.classList.add("active");const ve=document.getElementById("properties-content");if(!ve)return;const Je=U===s.spotLeft?"Spot Left":U===s.spotRight?"Spot Right":U===s.backLight?"Back Light":"Light",Te="#"+U.color.getHexString();ve.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-lightbulb"></i> ${Je}
                </h3>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Intensität: <span id="light-intensity-value">${U.intensity.toFixed(1)}</span>
                    </label>
                    <input type="range" id="light-intensity" min="0" max="100" step="1" value="${U.intensity}"
                           style="width:100%;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Farbe
                    </label>
                    <input type="color" id="light-color" value="${Te}"
                           style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);background:var(--bg-primary);cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-pos-x" value="${U.position.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-pos-y" value="${U.position.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-pos-z" value="${U.position.z.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Rotation (Grad)
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-rot-x" value="${(U.rotation.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-rot-y" value="${(U.rotation.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-rot-z" value="${(U.rotation.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Ziehe das Licht-Icon in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const qe=document.getElementById("light-intensity"),at=document.getElementById("light-intensity-value"),ht=document.getElementById("light-color"),yt=document.getElementById("light-pos-x"),Et=document.getElementById("light-pos-y"),je=document.getElementById("light-pos-z");if(qe&&(qe.oninput=Lt=>{U.intensity=parseFloat(Lt.target.value),at.textContent=U.intensity.toFixed(1)}),ht&&(ht.oninput=Lt=>{U.color.setHex(parseInt(Lt.target.value.substring(1),16)),f&&f.children.forEach(st=>{st.material&&(st.material.color.copy(U.color),st.material.emissive&&st.material.emissive.copy(U.color))})}),yt&&Et&&je){const Lt=()=>{U.position.set(parseFloat(yt.value),parseFloat(Et.value),parseFloat(je.value)),f&&(f.position.copy(U.position),f.lookAt(U.target.position))};yt.oninput=Lt,Et.oninput=Lt,je.oninput=Lt}const nt=document.getElementById("light-rot-x"),rt=document.getElementById("light-rot-y"),Ut=document.getElementById("light-rot-z");if(nt&&rt&&Ut){const Lt=()=>{U.rotation.set(parseFloat(nt.value)*Math.PI/180,parseFloat(rt.value)*Math.PI/180,parseFloat(Ut.value)*Math.PI/180),f&&f.rotation.copy(U.rotation)};nt.oninput=Lt,rt.oninput=Lt,Ut.oninput=Lt}}function oe(U){document.querySelectorAll(".panel-tab").forEach(st=>st.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(st=>st.classList.remove("active"));const ne=document.querySelector('[data-tab="tab-properties"]'),fe=document.getElementById("tab-properties");ne&&ne.classList.add("active"),fe&&fe.classList.add("active");const ve=document.getElementById("properties-content");if(!ve)return;const Je=U.userData.garmentId||U.name||"Garment",Te=U.material,at="#"+Te.color.getHexString(),ht=Te.roughness??.8,yt=Te.metalness??0,Et=U.userData.offset||.006,je=U.userData.stiffness||.8;ve.innerHTML=`
            <div style="padding:16px;max-height:calc(100vh - 200px);overflow-y:auto;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-tshirt"></i> ${Je}
                </h3>

                <!-- Fit -->
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Fit</div>
                <div class="slider-row"><label>Offset</label>
                    <input type="range" id="garment-offset" min="0" max="30" value="${Math.round(Et*1e3)}" step="1">
                    <span class="slider-val" id="garment-offset-val">${Et.toFixed(3)}</span>
                </div>
                <div class="slider-row"><label>Stiffness</label>
                    <input type="range" id="garment-stiffness" min="0" max="100" value="${Math.round(je*100)}" step="1">
                    <span class="slider-val" id="garment-stiffness-val">${je.toFixed(2)}</span>
                </div>
                <div class="slider-row"><label>Min. Abstand</label>
                    <input type="range" id="garment-min-dist" min="0" max="15" value="3" step="1">
                    <span class="slider-val" id="garment-min-dist-val">3 mm</span>
                </div>
                <div class="slider-row"><label>Schritt-Boden</label>
                    <input type="range" id="garment-crotch-floor" min="-40" max="40" value="0" step="1">
                    <span class="slider-val" id="garment-crotch-floor-val">0 mm</span>
                </div>
                <div class="slider-row"><label>Anheben</label>
                    <input type="range" id="garment-lift" min="-20" max="40" value="0" step="1">
                    <span class="slider-val" id="garment-lift-val">0 mm</span>
                </div>
                <div class="slider-row"><label>Schritt-Tiefe</label>
                    <input type="range" id="garment-crotch-depth" min="0" max="40" value="0" step="1">
                    <span class="slider-val" id="garment-crotch-depth-val">0 mm</span>
                </div>

                <!-- Farbe / Material -->
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Farbe / Material</div>
                <div class="slider-row"><label>Color</label>
                    <input type="color" id="garment-color" value="${at}" style="width:40px;height:24px;border:none;cursor:pointer;">
                </div>
                <div class="slider-row"><label>Roughness</label>
                    <input type="range" id="garment-roughness" min="0" max="100" value="${Math.round(ht*100)}" step="1">
                    <span class="slider-val" id="garment-roughness-val">${ht.toFixed(2)}</span>
                </div>
                <div class="slider-row"><label>Metalness</label>
                    <input type="range" id="garment-metalness" min="0" max="100" value="${Math.round(yt*100)}" step="1">
                    <span class="slider-val" id="garment-metalness-val">${yt.toFixed(2)}</span>
                </div>

                <!-- Position -->
                <div id="garment-adjustments">
                    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Position</div>
                    <div class="slider-row"><label>Pos X</label>
                        <input type="range" id="garment-pos-x" min="-50" max="50" value="0" step="1">
                        <span class="slider-val" id="garment-pos-x-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Pos Y</label>
                        <input type="range" id="garment-pos-y" min="-50" max="50" value="0" step="1">
                        <span class="slider-val" id="garment-pos-y-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Pos Z</label>
                        <input type="range" id="garment-pos-z" min="-50" max="50" value="0" step="1">
                        <span class="slider-val" id="garment-pos-z-val">0.00 m</span>
                    </div>

                    <!-- Scale -->
                    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Scale</div>
                    <div class="slider-row"><label>Scale X</label>
                        <input type="range" id="garment-scale-x" min="50" max="200" value="100" step="1">
                        <span class="slider-val" id="garment-scale-x-val">1.00</span>
                    </div>
                    <div class="slider-row"><label>Scale Y</label>
                        <input type="range" id="garment-scale-y" min="50" max="200" value="100" step="1">
                        <span class="slider-val" id="garment-scale-y-val">1.00</span>
                    </div>
                    <div class="slider-row"><label>Scale Z</label>
                        <input type="range" id="garment-scale-z" min="50" max="200" value="100" step="1">
                        <span class="slider-val" id="garment-scale-z-val">1.00</span>
                    </div>

                    <!-- Region -->
                    <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.04em;color:var(--text-muted);margin:6px 0 4px;">Region</div>
                    <div class="slider-row"><label>Top</label>
                        <input type="range" id="garment-region-top" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-top-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Upper</label>
                        <input type="range" id="garment-region-upper" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-upper-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Mid</label>
                        <input type="range" id="garment-region-mid" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-mid-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Lower</label>
                        <input type="range" id="garment-region-lower" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-lower-val">0.00 m</span>
                    </div>
                    <div class="slider-row"><label>Bottom</label>
                        <input type="range" id="garment-region-bottom" min="-30" max="30" value="0" step="1">
                        <span class="slider-val" id="garment-region-bottom-val">0.00 m</span>
                    </div>
                </div>
            </div>
        `;const nt=(st,P,j)=>{const J=document.getElementById(st),ee=document.getElementById(P);J&&ee&&(J.oninput=()=>{ee.textContent=j?j(J.value):J.value})};nt("garment-offset","garment-offset-val",st=>(st/1e3).toFixed(3)),nt("garment-stiffness","garment-stiffness-val",st=>(st/100).toFixed(2)),nt("garment-min-dist","garment-min-dist-val",st=>st+" mm"),nt("garment-crotch-floor","garment-crotch-floor-val",st=>st+" mm"),nt("garment-lift","garment-lift-val",st=>st+" mm"),nt("garment-crotch-depth","garment-crotch-depth-val",st=>st+" mm"),nt("garment-roughness","garment-roughness-val",st=>(st/100).toFixed(2)),nt("garment-metalness","garment-metalness-val",st=>(st/100).toFixed(2)),nt("garment-pos-x","garment-pos-x-val",st=>(st/100).toFixed(2)+" m"),nt("garment-pos-y","garment-pos-y-val",st=>(st/100).toFixed(2)+" m"),nt("garment-pos-z","garment-pos-z-val",st=>(st/100).toFixed(2)+" m"),nt("garment-scale-x","garment-scale-x-val",st=>(st/100).toFixed(2)),nt("garment-scale-y","garment-scale-y-val",st=>(st/100).toFixed(2)),nt("garment-scale-z","garment-scale-z-val",st=>(st/100).toFixed(2));for(const st of["top","upper","mid","lower","bottom"])nt(`garment-region-${st}`,`garment-region-${st}-val`,P=>(P/100).toFixed(2)+" m");const rt=document.getElementById("garment-color");rt&&(rt.oninput=()=>{Te.color.setHex(parseInt(rt.value.substring(1),16))});const Ut=document.getElementById("garment-roughness");Ut&&(Ut.oninput=()=>{Te.roughness=parseInt(Ut.value)/100});const Lt=document.getElementById("garment-metalness");Lt&&(Lt.oninput=()=>{Te.metalness=parseInt(Lt.value)/100}),console.log("✓ Garment properties panel populated")}function pe(U){document.querySelectorAll(".panel-tab").forEach(Ut=>Ut.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Ut=>Ut.classList.remove("active"));const ne=document.querySelector('[data-tab="tab-properties"]'),fe=document.getElementById("tab-properties");ne&&ne.classList.add("active"),fe&&fe.classList.add("active");const ve=document.getElementById("properties-content");if(!ve)return;const Je=U.userData.presetName||"Character",Te=U.userData.bodyType||"Unknown",qe=U.position,at=U.rotation;ve.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-user"></i> ${Je}
                </h3>

                <div style="margin-bottom:16px;font-size:0.8rem;">
                    <span style="color:var(--text-muted);">Body Type:</span>
                    <span style="color:var(--text);margin-left:8px;">${Te}</span>
                </div>

                <!-- Meta Sliders (Age, Mass, Tone, Height) -->
                <div style="margin-bottom:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);">
                        <i class="fas fa-sliders-h"></i> Meta-Parameter
                    </h4>
                    <div id="meta-sliders-container"></div>
                </div>

                <!-- Morph Sliders -->
                <div style="margin-bottom:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);">
                        <i class="fas fa-palette"></i> Morphs
                    </h4>
                    <div id="morph-sliders-container"></div>
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="char-pos-x" value="${qe.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-pos-y" value="${qe.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-pos-z" value="${qe.z.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Rotation (Grad)
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="char-rot-x" value="${(at.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-rot-y" value="${(at.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-rot-z" value="${(at.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Nutze die Transform-Controls in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const ht=document.getElementById("char-pos-x"),yt=document.getElementById("char-pos-y"),Et=document.getElementById("char-pos-z");if(ht&&yt&&Et){const Ut=()=>{U.position.set(parseFloat(ht.value),parseFloat(yt.value),parseFloat(Et.value))};ht.oninput=Ut,yt.oninput=Ut,Et.oninput=Ut}const je=document.getElementById("char-rot-x"),nt=document.getElementById("char-rot-y"),rt=document.getElementById("char-rot-z");if(je&&nt&&rt){const Ut=()=>{U.rotation.set(parseFloat(je.value)*Math.PI/180,parseFloat(nt.value)*Math.PI/180,parseFloat(rt.value)*Math.PI/180)};je.oninput=Ut,nt.oninput=Ut,rt.oninput=Ut}Fe(U),bt(U)}function Fe(U){const ne=document.getElementById("meta-sliders-container");if(!ne)return;const fe={age:{min:-1,max:1,label:"Alter",step:.01},mass:{min:-1,max:1,label:"Gewicht",step:.01},tone:{min:-1,max:1,label:"Muskeltonus",step:.01},height:{min:-1,max:1,label:"Höhe",step:.01}},ve=U.userData.meta||{age:0,mass:0,tone:0,height:0};let Je="";for(const[Te,qe]of Object.entries(fe)){const at=ve[Te]||0,ht=qe.min,yt=qe.max;Je+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${qe.label}</span>
                        <span id="meta-${Te}-value" style="color:var(--text);">${at.toFixed(2)}</span>
                    </div>
                    <input type="range" id="meta-${Te}" min="${ht}" max="${yt}" step="${qe.step}" value="${at}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}ne.innerHTML=Je;for(const Te of Object.keys(fe)){const qe=document.getElementById(`meta-${Te}`),at=document.getElementById(`meta-${Te}-value`);qe&&at&&(qe.oninput=async()=>{const ht=parseFloat(qe.value);at.textContent=ht.toFixed(2),ve[Te]=ht,U.userData.meta=ve,await De(U)})}}async function De(U){try{let yt=function(je){const nt=atob(je),rt=new Uint8Array(nt.length);for(let Ut=0;Ut<nt.length;Ut++)rt[Ut]=nt.charCodeAt(Ut);return new Float32Array(rt.buffer)};var ne=yt;const fe=new URLSearchParams;fe.set("body_type",U.userData.bodyType||"Female_Caucasian");const ve=U.userData.morphs||{};for(const[je,nt]of Object.entries(ve))nt!=null&&fe.set(`morph_${je}`,String(nt));const Je=U.userData.meta||{};for(const[je,nt]of Object.entries(Je))nt!=null&&fe.set(`meta_${je}`,String(nt));const Te=`/api/character/mesh/?${fe.toString()}`,qe=await fetch(Te);if(!qe.ok)throw new Error(`Character mesh API error: ${qe.status}`);const at=await qe.json(),ht=U.children.find(je=>je.isMesh&&!je.userData.isHair&&!je.userData.isGarment);if(!ht){console.warn("Could not find body mesh to update");return}const Et=yt(at.vertices);for(let je=0;je<Et.length;je+=3){const nt=Et[je+1],rt=Et[je+2];Et[je+1]=rt,Et[je+2]=-nt}if(ht.geometry.attributes.position.array.set(Et),ht.geometry.attributes.position.needsUpdate=!0,at.normals){const je=yt(at.normals);for(let nt=0;nt<je.length;nt+=3){const rt=je[nt+1],Ut=je[nt+2];je[nt+1]=Ut,je[nt+2]=-rt}ht.geometry.attributes.normal.array.set(je),ht.geometry.attributes.normal.needsUpdate=!0}else ht.geometry.computeVertexNormals();console.log("✓ Character mesh reloaded")}catch(fe){console.error("Failed to reload character mesh:",fe)}}function bt(U){const ne=document.getElementById("morph-sliders-container");if(!ne)return;const fe=U.userData.morphs||{};if(Object.keys(fe).length===0){ne.innerHTML='<div style="font-size:0.75rem;color:var(--text-muted);text-align:center;padding:10px;">Keine Morphs</div>';return}let ve='<div style="max-height:300px;overflow-y:auto;padding-right:4px;">';for(const[Je,Te]of Object.entries(fe)){const qe=Te||0;ve+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${Je}</span>
                        <span id="morph-${Je}-value" style="color:var(--text);">${qe.toFixed(2)}</span>
                    </div>
                    <input type="range" id="morph-${Je}" min="0" max="1" step="0.01" value="${qe}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}ve+="</div>",ne.innerHTML=ve;for(const Je of Object.keys(fe)){const Te=document.getElementById(`morph-${Je}`),qe=document.getElementById(`morph-${Je}-value`);Te&&qe&&(Te.oninput=async()=>{const at=parseFloat(Te.value);qe.textContent=at.toFixed(2),fe[Je]=at,U.userData.morphs=fe,await De(U)})}}function Zt(){const U=document.getElementById("properties-content");U&&(U.innerHTML=`
            <div style="padding:20px;color:var(--text-muted);font-size:0.85rem;text-align:center;">
                <i class="fas fa-hand-pointer" style="font-size:2rem;margin-bottom:10px;opacity:0.3;"></i>
                <p>Klicke auf ein Licht-Icon oder Character in der Szene<br>um Eigenschaften zu bearbeiten.</p>
            </div>
        `)}function un(){requestAnimationFrame(un);const U=ie.getDelta();if(Z&&_e&&(Z.update(U*ft),Ce=$?$.time:0,Ce>=Ge&&(Ce=0,$&&($.time=0)),mt()),f&&f.userData.light){const ne=f.userData.light;ne.position.copy(f.position),f.lookAt(ne.target.position)}i.update(),n.render(e,t)}un()});
