/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Xs={ROTATE:0,DOLLY:1,PAN:2},Hs={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},lM=0,wp=1,uM=2,ug=1,hM=2,Zi=3,ir=0,Zn=1,$n=2,Er=0,qs=1,Ap=2,Rp=3,Pp=4,dM=5,os=100,fM=101,pM=102,mM=103,gM=104,_M=200,vM=201,yM=202,xM=203,gh=204,_h=205,bM=206,SM=207,EM=208,MM=209,TM=210,wM=211,AM=212,RM=213,PM=214,vh=0,yh=1,xh=2,Zs=3,bh=4,Sh=5,Eh=6,Mh=7,hg=0,CM=1,DM=2,Mr=0,IM=1,LM=2,FM=3,dg=4,NM=5,OM=6,UM=7,Cp="attached",BM="detached",fg=300,Qs=301,Js=302,Th=303,wh=304,kc=306,eo=1e3,br=1001,Fc=1002,Wn=1003,pg=1004,Wo=1005,ai=1006,Mc=1007,Ji=1008,rr=1009,mg=1010,gg=1011,Jo=1012,ld=1013,ls=1014,Ei=1015,ia=1016,ud=1017,hd=1018,to=1020,_g=35902,vg=1021,yg=1022,fi=1023,xg=1024,bg=1025,Ys=1026,no=1027,dd=1028,fd=1029,Sg=1030,pd=1031,md=1033,Tc=33776,wc=33777,Ac=33778,Rc=33779,Ah=35840,Rh=35841,Ph=35842,Ch=35843,Dh=36196,Ih=37492,Lh=37496,Fh=37808,Nh=37809,Oh=37810,Uh=37811,Bh=37812,kh=37813,zh=37814,Hh=37815,Vh=37816,Gh=37817,Wh=37818,jh=37819,Xh=37820,qh=37821,Pc=36492,Yh=36494,Kh=36495,Eg=36283,$h=36284,Zh=36285,Qh=36286,kM=2200,gd=2201,zM=2202,ea=2300,ta=2301,Eu=2302,Vs=2400,Gs=2401,Nc=2402,_d=2500,HM=2501,VM=0,Mg=1,Jh=2,GM=3200,WM=3201,Tg=0,jM=1,xr="",Tn="srgb",jn="srgb-linear",zc="linear",qt="srgb",ws=7680,Dp=519,XM=512,qM=513,YM=514,wg=515,KM=516,$M=517,ZM=518,QM=519,ed=35044,Ip="300 es",er=2e3,Oc=2001;class Rr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const s=i.indexOf(t);s!==-1&&i.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let s=0,a=i.length;s<a;s++)i[s].call(this,e);e.target=null}}}const Un=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Lp=1234567;const $o=Math.PI/180,io=180/Math.PI;function Mi(){const r=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Un[r&255]+Un[r>>8&255]+Un[r>>16&255]+Un[r>>24&255]+"-"+Un[e&255]+Un[e>>8&255]+"-"+Un[e>>16&15|64]+Un[e>>24&255]+"-"+Un[t&63|128]+Un[t>>8&255]+"-"+Un[t>>16&255]+Un[t>>24&255]+Un[n&255]+Un[n>>8&255]+Un[n>>16&255]+Un[n>>24&255]).toLowerCase()}function Dn(r,e,t){return Math.max(e,Math.min(t,r))}function vd(r,e){return(r%e+e)%e}function JM(r,e,t,n,i){return n+(r-e)*(i-n)/(t-e)}function eT(r,e,t){return r!==e?(t-r)/(e-r):0}function Zo(r,e,t){return(1-t)*r+t*e}function tT(r,e,t,n){return Zo(r,e,1-Math.exp(-t*n))}function nT(r,e=1){return e-Math.abs(vd(r,e*2)-e)}function iT(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*(3-2*r))}function rT(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*r*(r*(r*6-15)+10))}function sT(r,e){return r+Math.floor(Math.random()*(e-r+1))}function oT(r,e){return r+Math.random()*(e-r)}function aT(r){return r*(.5-Math.random())}function cT(r){r!==void 0&&(Lp=r);let e=Lp+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function lT(r){return r*$o}function uT(r){return r*io}function hT(r){return(r&r-1)===0&&r!==0}function dT(r){return Math.pow(2,Math.ceil(Math.log(r)/Math.LN2))}function fT(r){return Math.pow(2,Math.floor(Math.log(r)/Math.LN2))}function pT(r,e,t,n,i){const s=Math.cos,a=Math.sin,c=s(t/2),u=a(t/2),h=s((e+n)/2),f=a((e+n)/2),p=s((e-n)/2),m=a((e-n)/2),g=s((n-e)/2),x=a((n-e)/2);switch(i){case"XYX":r.set(c*f,u*p,u*m,c*h);break;case"YZY":r.set(u*m,c*f,u*p,c*h);break;case"ZXZ":r.set(u*p,u*m,c*f,c*h);break;case"XZX":r.set(c*f,u*x,u*g,c*h);break;case"YXY":r.set(u*g,c*f,u*x,c*h);break;case"ZYZ":r.set(u*x,u*g,c*f,c*h);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+i)}}function bi(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return r/4294967295;case Uint16Array:return r/65535;case Uint8Array:return r/255;case Int32Array:return Math.max(r/2147483647,-1);case Int16Array:return Math.max(r/32767,-1);case Int8Array:return Math.max(r/127,-1);default:throw new Error("Invalid component type.")}}function jt(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return Math.round(r*4294967295);case Uint16Array:return Math.round(r*65535);case Uint8Array:return Math.round(r*255);case Int32Array:return Math.round(r*2147483647);case Int16Array:return Math.round(r*32767);case Int8Array:return Math.round(r*127);default:throw new Error("Invalid component type.")}}const Ag={DEG2RAD:$o,RAD2DEG:io,generateUUID:Mi,clamp:Dn,euclideanModulo:vd,mapLinear:JM,inverseLerp:eT,lerp:Zo,damp:tT,pingpong:nT,smoothstep:iT,smootherstep:rT,randInt:sT,randFloat:oT,randFloatSpread:aT,seededRandom:cT,degToRad:lT,radToDeg:uT,isPowerOfTwo:hT,ceilPowerOfTwo:dT,floorPowerOfTwo:fT,setQuaternionFromProperEuler:pT,normalize:jt,denormalize:bi};class ht{constructor(e=0,t=0){ht.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Dn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),i=Math.sin(t),s=this.x-e.x,a=this.y-e.y;return this.x=s*n-a*i+e.x,this.y=s*i+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class yt{constructor(e,t,n,i,s,a,c,u,h){yt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h)}set(e,t,n,i,s,a,c,u,h){const f=this.elements;return f[0]=e,f[1]=i,f[2]=c,f[3]=t,f[4]=s,f[5]=u,f[6]=n,f[7]=a,f[8]=h,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[3],u=n[6],h=n[1],f=n[4],p=n[7],m=n[2],g=n[5],x=n[8],E=i[0],v=i[3],_=i[6],R=i[1],w=i[4],S=i[7],z=i[2],O=i[5],N=i[8];return s[0]=a*E+c*R+u*z,s[3]=a*v+c*w+u*O,s[6]=a*_+c*S+u*N,s[1]=h*E+f*R+p*z,s[4]=h*v+f*w+p*O,s[7]=h*_+f*S+p*N,s[2]=m*E+g*R+x*z,s[5]=m*v+g*w+x*O,s[8]=m*_+g*S+x*N,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8];return t*a*f-t*c*h-n*s*f+n*c*u+i*s*h-i*a*u}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=f*a-c*h,m=c*u-f*s,g=h*s-a*u,x=t*p+n*m+i*g;if(x===0)return this.set(0,0,0,0,0,0,0,0,0);const E=1/x;return e[0]=p*E,e[1]=(i*h-f*n)*E,e[2]=(c*n-i*a)*E,e[3]=m*E,e[4]=(f*t-i*u)*E,e[5]=(i*s-c*t)*E,e[6]=g*E,e[7]=(n*u-h*t)*E,e[8]=(a*t-n*s)*E,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,s,a,c){const u=Math.cos(s),h=Math.sin(s);return this.set(n*u,n*h,-n*(u*a+h*c)+a+e,-i*h,i*u,-i*(-h*a+u*c)+c+t,0,0,1),this}scale(e,t){return this.premultiply(Mu.makeScale(e,t)),this}rotate(e){return this.premultiply(Mu.makeRotation(-e)),this}translate(e,t){return this.premultiply(Mu.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Mu=new yt;function Rg(r){for(let e=r.length-1;e>=0;--e)if(r[e]>=65535)return!0;return!1}function na(r){return document.createElementNS("http://www.w3.org/1999/xhtml",r)}function mT(){const r=na("canvas");return r.style.display="block",r}const Fp={};function jo(r){r in Fp||(Fp[r]=!0,console.warn(r))}function gT(r,e,t){return new Promise(function(n,i){function s(){switch(r.clientWaitSync(e,r.SYNC_FLUSH_COMMANDS_BIT,0)){case r.WAIT_FAILED:i();break;case r.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}function _T(r){const e=r.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function vT(r){const e=r.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const Lt={enabled:!0,workingColorSpace:jn,spaces:{},convert:function(r,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===qt&&(r.r=nr(r.r),r.g=nr(r.g),r.b=nr(r.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(r.applyMatrix3(this.spaces[e].toXYZ),r.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===qt&&(r.r=Ks(r.r),r.g=Ks(r.g),r.b=Ks(r.b))),r},fromWorkingColorSpace:function(r,e){return this.convert(r,this.workingColorSpace,e)},toWorkingColorSpace:function(r,e){return this.convert(r,e,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===xr?zc:this.spaces[r].transfer},getLuminanceCoefficients:function(r,e=this.workingColorSpace){return r.fromArray(this.spaces[e].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,e,t){return r.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace}};function nr(r){return r<.04045?r*.0773993808:Math.pow(r*.9478672986+.0521327014,2.4)}function Ks(r){return r<.0031308?r*12.92:1.055*Math.pow(r,.41666)-.055}const Np=[.64,.33,.3,.6,.15,.06],Op=[.2126,.7152,.0722],Up=[.3127,.329],Bp=new yt().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),kp=new yt().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);Lt.define({[jn]:{primaries:Np,whitePoint:Up,transfer:zc,toXYZ:Bp,fromXYZ:kp,luminanceCoefficients:Op,workingColorSpaceConfig:{unpackColorSpace:Tn},outputColorSpaceConfig:{drawingBufferColorSpace:Tn}},[Tn]:{primaries:Np,whitePoint:Up,transfer:qt,toXYZ:Bp,fromXYZ:kp,luminanceCoefficients:Op,outputColorSpaceConfig:{drawingBufferColorSpace:Tn}}});let As;class yT{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{As===void 0&&(As=na("canvas")),As.width=e.width,As.height=e.height;const n=As.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=As}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=na("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const i=n.getImageData(0,0,e.width,e.height),s=i.data;for(let a=0;a<s.length;a++)s[a]=nr(s[a]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(nr(t[n]/255)*255):t[n]=nr(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let xT=0;class Pg{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:xT++}),this.uuid=Mi(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let s;if(Array.isArray(i)){s=[];for(let a=0,c=i.length;a<c;a++)i[a].isDataTexture?s.push(Tu(i[a].image)):s.push(Tu(i[a]))}else s=Tu(i);n.url=s}return t||(e.images[this.uuid]=n),n}}function Tu(r){return typeof HTMLImageElement<"u"&&r instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&r instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&r instanceof ImageBitmap?yT.getDataURL(r):r.data?{data:Array.from(r.data),width:r.width,height:r.height,type:r.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let bT=0;class wn extends Rr{constructor(e=wn.DEFAULT_IMAGE,t=wn.DEFAULT_MAPPING,n=br,i=br,s=ai,a=Ji,c=fi,u=rr,h=wn.DEFAULT_ANISOTROPY,f=xr){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:bT++}),this.uuid=Mi(),this.name="",this.source=new Pg(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=i,this.magFilter=s,this.minFilter=a,this.anisotropy=h,this.format=c,this.internalFormat=null,this.type=u,this.offset=new ht(0,0),this.repeat=new ht(1,1),this.center=new ht(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new yt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=f,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==fg)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case eo:e.x=e.x-Math.floor(e.x);break;case br:e.x=e.x<0?0:1;break;case Fc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case eo:e.y=e.y-Math.floor(e.y);break;case br:e.y=e.y<0?0:1;break;case Fc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}wn.DEFAULT_IMAGE=null;wn.DEFAULT_MAPPING=fg;wn.DEFAULT_ANISOTROPY=1;class Bt{constructor(e=0,t=0,n=0,i=1){Bt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*i+a[12]*s,this.y=a[1]*t+a[5]*n+a[9]*i+a[13]*s,this.z=a[2]*t+a[6]*n+a[10]*i+a[14]*s,this.w=a[3]*t+a[7]*n+a[11]*i+a[15]*s,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,s;const u=e.elements,h=u[0],f=u[4],p=u[8],m=u[1],g=u[5],x=u[9],E=u[2],v=u[6],_=u[10];if(Math.abs(f-m)<.01&&Math.abs(p-E)<.01&&Math.abs(x-v)<.01){if(Math.abs(f+m)<.1&&Math.abs(p+E)<.1&&Math.abs(x+v)<.1&&Math.abs(h+g+_-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const w=(h+1)/2,S=(g+1)/2,z=(_+1)/2,O=(f+m)/4,N=(p+E)/4,V=(x+v)/4;return w>S&&w>z?w<.01?(n=0,i=.707106781,s=.707106781):(n=Math.sqrt(w),i=O/n,s=N/n):S>z?S<.01?(n=.707106781,i=0,s=.707106781):(i=Math.sqrt(S),n=O/i,s=V/i):z<.01?(n=.707106781,i=.707106781,s=0):(s=Math.sqrt(z),n=N/s,i=V/s),this.set(n,i,s,t),this}let R=Math.sqrt((v-x)*(v-x)+(p-E)*(p-E)+(m-f)*(m-f));return Math.abs(R)<.001&&(R=1),this.x=(v-x)/R,this.y=(p-E)/R,this.z=(m-f)/R,this.w=Math.acos((h+g+_-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class ST extends Rr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new Bt(0,0,e,t),this.scissorTest=!1,this.viewport=new Bt(0,0,e,t);const i={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ai,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new wn(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let c=0;c<a;c++)this.textures[c]=s.clone(),this.textures[c].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let i=0,s=this.textures.length;i<s;i++)this.textures[i].image.width=e,this.textures[i].image.height=t,this.textures[i].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,i=e.textures.length;n<i;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Pg(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class us extends ST{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Cg extends wn{constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Wn,this.minFilter=Wn,this.wrapR=br,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class ET extends wn{constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Wn,this.minFilter=Wn,this.wrapR=br,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Mt{constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,s,a,c){let u=n[i+0],h=n[i+1],f=n[i+2],p=n[i+3];const m=s[a+0],g=s[a+1],x=s[a+2],E=s[a+3];if(c===0){e[t+0]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p;return}if(c===1){e[t+0]=m,e[t+1]=g,e[t+2]=x,e[t+3]=E;return}if(p!==E||u!==m||h!==g||f!==x){let v=1-c;const _=u*m+h*g+f*x+p*E,R=_>=0?1:-1,w=1-_*_;if(w>Number.EPSILON){const z=Math.sqrt(w),O=Math.atan2(z,_*R);v=Math.sin(v*O)/z,c=Math.sin(c*O)/z}const S=c*R;if(u=u*v+m*S,h=h*v+g*S,f=f*v+x*S,p=p*v+E*S,v===1-c){const z=1/Math.sqrt(u*u+h*h+f*f+p*p);u*=z,h*=z,f*=z,p*=z}}e[t]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p}static multiplyQuaternionsFlat(e,t,n,i,s,a){const c=n[i],u=n[i+1],h=n[i+2],f=n[i+3],p=s[a],m=s[a+1],g=s[a+2],x=s[a+3];return e[t]=c*x+f*p+u*g-h*m,e[t+1]=u*x+f*m+h*p-c*g,e[t+2]=h*x+f*g+c*m-u*p,e[t+3]=f*x-c*p-u*m-h*g,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,i=e._y,s=e._z,a=e._order,c=Math.cos,u=Math.sin,h=c(n/2),f=c(i/2),p=c(s/2),m=u(n/2),g=u(i/2),x=u(s/2);switch(a){case"XYZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"YXZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"ZXY":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"ZYX":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"YZX":this._x=m*f*p+h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p-m*g*x;break;case"XZY":this._x=m*f*p-h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p+m*g*x;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],i=t[4],s=t[8],a=t[1],c=t[5],u=t[9],h=t[2],f=t[6],p=t[10],m=n+c+p;if(m>0){const g=.5/Math.sqrt(m+1);this._w=.25/g,this._x=(f-u)*g,this._y=(s-h)*g,this._z=(a-i)*g}else if(n>c&&n>p){const g=2*Math.sqrt(1+n-c-p);this._w=(f-u)/g,this._x=.25*g,this._y=(i+a)/g,this._z=(s+h)/g}else if(c>p){const g=2*Math.sqrt(1+c-n-p);this._w=(s-h)/g,this._x=(i+a)/g,this._y=.25*g,this._z=(u+f)/g}else{const g=2*Math.sqrt(1+p-n-c);this._w=(a-i)/g,this._x=(s+h)/g,this._y=(u+f)/g,this._z=.25*g}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Dn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,i=e._y,s=e._z,a=e._w,c=t._x,u=t._y,h=t._z,f=t._w;return this._x=n*f+a*c+i*h-s*u,this._y=i*f+a*u+s*c-n*h,this._z=s*f+a*h+n*u-i*c,this._w=a*f-n*c-i*u-s*h,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,i=this._y,s=this._z,a=this._w;let c=a*e._w+n*e._x+i*e._y+s*e._z;if(c<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,c=-c):this.copy(e),c>=1)return this._w=a,this._x=n,this._y=i,this._z=s,this;const u=1-c*c;if(u<=Number.EPSILON){const g=1-t;return this._w=g*a+t*this._w,this._x=g*n+t*this._x,this._y=g*i+t*this._y,this._z=g*s+t*this._z,this.normalize(),this}const h=Math.sqrt(u),f=Math.atan2(h,c),p=Math.sin((1-t)*f)/h,m=Math.sin(t*f)/h;return this._w=a*p+this._w*m,this._x=n*p+this._x*m,this._y=i*p+this._y*m,this._z=s*p+this._z*m,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),i=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(i*Math.sin(e),i*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class U{constructor(e=0,t=0,n=0){U.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(zp.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(zp.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*i,this.y=s[1]*t+s[4]*n+s[7]*i,this.z=s[2]*t+s[5]*n+s[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=e.elements,a=1/(s[3]*t+s[7]*n+s[11]*i+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*i+s[12])*a,this.y=(s[1]*t+s[5]*n+s[9]*i+s[13])*a,this.z=(s[2]*t+s[6]*n+s[10]*i+s[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,i=this.z,s=e.x,a=e.y,c=e.z,u=e.w,h=2*(a*i-c*n),f=2*(c*t-s*i),p=2*(s*n-a*t);return this.x=t+u*h+a*p-c*f,this.y=n+u*f+c*h-s*p,this.z=i+u*p+s*f-a*h,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*i,this.y=s[1]*t+s[5]*n+s[9]*i,this.z=s[2]*t+s[6]*n+s[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,i=e.y,s=e.z,a=t.x,c=t.y,u=t.z;return this.x=i*u-s*c,this.y=s*a-n*u,this.z=n*c-i*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return wu.copy(this).projectOnVector(e),this.sub(wu)}reflect(e){return this.sub(wu.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Dn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const wu=new U,zp=new Mt;class Ti{constructor(e=new U(1/0,1/0,1/0),t=new U(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(_i.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(_i.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=_i.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let a=0,c=s.count;a<c;a++)e.isMesh===!0?e.getVertexPosition(a,_i):_i.fromBufferAttribute(s,a),_i.applyMatrix4(e.matrixWorld),this.expandByPoint(_i);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),ja.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),ja.copy(n.boundingBox)),ja.applyMatrix4(e.matrixWorld),this.union(ja)}const i=e.children;for(let s=0,a=i.length;s<a;s++)this.expandByObject(i[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,_i),_i.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Lo),Xa.subVectors(this.max,Lo),Rs.subVectors(e.a,Lo),Ps.subVectors(e.b,Lo),Cs.subVectors(e.c,Lo),ur.subVectors(Ps,Rs),hr.subVectors(Cs,Ps),$r.subVectors(Rs,Cs);let t=[0,-ur.z,ur.y,0,-hr.z,hr.y,0,-$r.z,$r.y,ur.z,0,-ur.x,hr.z,0,-hr.x,$r.z,0,-$r.x,-ur.y,ur.x,0,-hr.y,hr.x,0,-$r.y,$r.x,0];return!Au(t,Rs,Ps,Cs,Xa)||(t=[1,0,0,0,1,0,0,0,1],!Au(t,Rs,Ps,Cs,Xa))?!1:(qa.crossVectors(ur,hr),t=[qa.x,qa.y,qa.z],Au(t,Rs,Ps,Cs,Xa))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,_i).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(_i).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(ji[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),ji[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),ji[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),ji[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),ji[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),ji[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),ji[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),ji[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(ji),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const ji=[new U,new U,new U,new U,new U,new U,new U,new U],_i=new U,ja=new Ti,Rs=new U,Ps=new U,Cs=new U,ur=new U,hr=new U,$r=new U,Lo=new U,Xa=new U,qa=new U,Zr=new U;function Au(r,e,t,n,i){for(let s=0,a=r.length-3;s<=a;s+=3){Zr.fromArray(r,s);const c=i.x*Math.abs(Zr.x)+i.y*Math.abs(Zr.y)+i.z*Math.abs(Zr.z),u=e.dot(Zr),h=t.dot(Zr),f=n.dot(Zr);if(Math.max(-Math.max(u,h,f),Math.min(u,h,f))>c)return!1}return!0}const MT=new Ti,Fo=new U,Ru=new U;class Li{constructor(e=new U,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):MT.setFromPoints(e).getCenter(n);let i=0;for(let s=0,a=e.length;s<a;s++)i=Math.max(i,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Fo.subVectors(e,this.center);const t=Fo.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(Fo,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Ru.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Fo.copy(e.center).add(Ru)),this.expandByPoint(Fo.copy(e.center).sub(Ru))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Xi=new U,Pu=new U,Ya=new U,dr=new U,Cu=new U,Ka=new U,Du=new U;class co{constructor(e=new U,t=new U(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Xi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Xi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Xi.copy(this.origin).addScaledVector(this.direction,t),Xi.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){Pu.copy(e).add(t).multiplyScalar(.5),Ya.copy(t).sub(e).normalize(),dr.copy(this.origin).sub(Pu);const s=e.distanceTo(t)*.5,a=-this.direction.dot(Ya),c=dr.dot(this.direction),u=-dr.dot(Ya),h=dr.lengthSq(),f=Math.abs(1-a*a);let p,m,g,x;if(f>0)if(p=a*u-c,m=a*c-u,x=s*f,p>=0)if(m>=-x)if(m<=x){const E=1/f;p*=E,m*=E,g=p*(p+a*m+2*c)+m*(a*p+m+2*u)+h}else m=s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m=-s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m<=-x?(p=Math.max(0,-(-a*s+c)),m=p>0?-s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h):m<=x?(p=0,m=Math.min(Math.max(-s,-u),s),g=m*(m+2*u)+h):(p=Math.max(0,-(a*s+c)),m=p>0?s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h);else m=a>0?-s:s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;return n&&n.copy(this.origin).addScaledVector(this.direction,p),i&&i.copy(Pu).addScaledVector(Ya,m),g}intersectSphere(e,t){Xi.subVectors(e.center,this.origin);const n=Xi.dot(this.direction),i=Xi.dot(Xi)-n*n,s=e.radius*e.radius;if(i>s)return null;const a=Math.sqrt(s-i),c=n-a,u=n+a;return u<0?null:c<0?this.at(u,t):this.at(c,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,s,a,c,u;const h=1/this.direction.x,f=1/this.direction.y,p=1/this.direction.z,m=this.origin;return h>=0?(n=(e.min.x-m.x)*h,i=(e.max.x-m.x)*h):(n=(e.max.x-m.x)*h,i=(e.min.x-m.x)*h),f>=0?(s=(e.min.y-m.y)*f,a=(e.max.y-m.y)*f):(s=(e.max.y-m.y)*f,a=(e.min.y-m.y)*f),n>a||s>i||((s>n||isNaN(n))&&(n=s),(a<i||isNaN(i))&&(i=a),p>=0?(c=(e.min.z-m.z)*p,u=(e.max.z-m.z)*p):(c=(e.max.z-m.z)*p,u=(e.min.z-m.z)*p),n>u||c>i)||((c>n||n!==n)&&(n=c),(u<i||i!==i)&&(i=u),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,Xi)!==null}intersectTriangle(e,t,n,i,s){Cu.subVectors(t,e),Ka.subVectors(n,e),Du.crossVectors(Cu,Ka);let a=this.direction.dot(Du),c;if(a>0){if(i)return null;c=1}else if(a<0)c=-1,a=-a;else return null;dr.subVectors(this.origin,e);const u=c*this.direction.dot(Ka.crossVectors(dr,Ka));if(u<0)return null;const h=c*this.direction.dot(Cu.cross(dr));if(h<0||u+h>a)return null;const f=-c*dr.dot(Du);return f<0?null:this.at(f/a,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class pt{constructor(e,t,n,i,s,a,c,u,h,f,p,m,g,x,E,v){pt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,E,v)}set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,E,v){const _=this.elements;return _[0]=e,_[4]=t,_[8]=n,_[12]=i,_[1]=s,_[5]=a,_[9]=c,_[13]=u,_[2]=h,_[6]=f,_[10]=p,_[14]=m,_[3]=g,_[7]=x,_[11]=E,_[15]=v,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new pt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,i=1/Ds.setFromMatrixColumn(e,0).length(),s=1/Ds.setFromMatrixColumn(e,1).length(),a=1/Ds.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,i=e.y,s=e.z,a=Math.cos(n),c=Math.sin(n),u=Math.cos(i),h=Math.sin(i),f=Math.cos(s),p=Math.sin(s);if(e.order==="XYZ"){const m=a*f,g=a*p,x=c*f,E=c*p;t[0]=u*f,t[4]=-u*p,t[8]=h,t[1]=g+x*h,t[5]=m-E*h,t[9]=-c*u,t[2]=E-m*h,t[6]=x+g*h,t[10]=a*u}else if(e.order==="YXZ"){const m=u*f,g=u*p,x=h*f,E=h*p;t[0]=m+E*c,t[4]=x*c-g,t[8]=a*h,t[1]=a*p,t[5]=a*f,t[9]=-c,t[2]=g*c-x,t[6]=E+m*c,t[10]=a*u}else if(e.order==="ZXY"){const m=u*f,g=u*p,x=h*f,E=h*p;t[0]=m-E*c,t[4]=-a*p,t[8]=x+g*c,t[1]=g+x*c,t[5]=a*f,t[9]=E-m*c,t[2]=-a*h,t[6]=c,t[10]=a*u}else if(e.order==="ZYX"){const m=a*f,g=a*p,x=c*f,E=c*p;t[0]=u*f,t[4]=x*h-g,t[8]=m*h+E,t[1]=u*p,t[5]=E*h+m,t[9]=g*h-x,t[2]=-h,t[6]=c*u,t[10]=a*u}else if(e.order==="YZX"){const m=a*u,g=a*h,x=c*u,E=c*h;t[0]=u*f,t[4]=E-m*p,t[8]=x*p+g,t[1]=p,t[5]=a*f,t[9]=-c*f,t[2]=-h*f,t[6]=g*p+x,t[10]=m-E*p}else if(e.order==="XZY"){const m=a*u,g=a*h,x=c*u,E=c*h;t[0]=u*f,t[4]=-p,t[8]=h*f,t[1]=m*p+E,t[5]=a*f,t[9]=g*p-x,t[2]=x*p-g,t[6]=c*f,t[10]=E*p+m}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(TT,e,wT)}lookAt(e,t,n){const i=this.elements;return si.subVectors(e,t),si.lengthSq()===0&&(si.z=1),si.normalize(),fr.crossVectors(n,si),fr.lengthSq()===0&&(Math.abs(n.z)===1?si.x+=1e-4:si.z+=1e-4,si.normalize(),fr.crossVectors(n,si)),fr.normalize(),$a.crossVectors(si,fr),i[0]=fr.x,i[4]=$a.x,i[8]=si.x,i[1]=fr.y,i[5]=$a.y,i[9]=si.y,i[2]=fr.z,i[6]=$a.z,i[10]=si.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[4],u=n[8],h=n[12],f=n[1],p=n[5],m=n[9],g=n[13],x=n[2],E=n[6],v=n[10],_=n[14],R=n[3],w=n[7],S=n[11],z=n[15],O=i[0],N=i[4],V=i[8],D=i[12],A=i[1],k=i[5],J=i[9],ee=i[13],re=i[2],le=i[6],Y=i[10],de=i[14],ne=i[3],ye=i[7],Te=i[11],ze=i[15];return s[0]=a*O+c*A+u*re+h*ne,s[4]=a*N+c*k+u*le+h*ye,s[8]=a*V+c*J+u*Y+h*Te,s[12]=a*D+c*ee+u*de+h*ze,s[1]=f*O+p*A+m*re+g*ne,s[5]=f*N+p*k+m*le+g*ye,s[9]=f*V+p*J+m*Y+g*Te,s[13]=f*D+p*ee+m*de+g*ze,s[2]=x*O+E*A+v*re+_*ne,s[6]=x*N+E*k+v*le+_*ye,s[10]=x*V+E*J+v*Y+_*Te,s[14]=x*D+E*ee+v*de+_*ze,s[3]=R*O+w*A+S*re+z*ne,s[7]=R*N+w*k+S*le+z*ye,s[11]=R*V+w*J+S*Y+z*Te,s[15]=R*D+w*ee+S*de+z*ze,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],i=e[8],s=e[12],a=e[1],c=e[5],u=e[9],h=e[13],f=e[2],p=e[6],m=e[10],g=e[14],x=e[3],E=e[7],v=e[11],_=e[15];return x*(+s*u*p-i*h*p-s*c*m+n*h*m+i*c*g-n*u*g)+E*(+t*u*g-t*h*m+s*a*m-i*a*g+i*h*f-s*u*f)+v*(+t*h*p-t*c*g-s*a*p+n*a*g+s*c*f-n*h*f)+_*(-i*c*f-t*u*p+t*c*m+i*a*p-n*a*m+n*u*f)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=e[9],m=e[10],g=e[11],x=e[12],E=e[13],v=e[14],_=e[15],R=p*v*h-E*m*h+E*u*g-c*v*g-p*u*_+c*m*_,w=x*m*h-f*v*h-x*u*g+a*v*g+f*u*_-a*m*_,S=f*E*h-x*p*h+x*c*g-a*E*g-f*c*_+a*p*_,z=x*p*u-f*E*u-x*c*m+a*E*m+f*c*v-a*p*v,O=t*R+n*w+i*S+s*z;if(O===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const N=1/O;return e[0]=R*N,e[1]=(E*m*s-p*v*s-E*i*g+n*v*g+p*i*_-n*m*_)*N,e[2]=(c*v*s-E*u*s+E*i*h-n*v*h-c*i*_+n*u*_)*N,e[3]=(p*u*s-c*m*s-p*i*h+n*m*h+c*i*g-n*u*g)*N,e[4]=w*N,e[5]=(f*v*s-x*m*s+x*i*g-t*v*g-f*i*_+t*m*_)*N,e[6]=(x*u*s-a*v*s-x*i*h+t*v*h+a*i*_-t*u*_)*N,e[7]=(a*m*s-f*u*s+f*i*h-t*m*h-a*i*g+t*u*g)*N,e[8]=S*N,e[9]=(x*p*s-f*E*s-x*n*g+t*E*g+f*n*_-t*p*_)*N,e[10]=(a*E*s-x*c*s+x*n*h-t*E*h-a*n*_+t*c*_)*N,e[11]=(f*c*s-a*p*s-f*n*h+t*p*h+a*n*g-t*c*g)*N,e[12]=z*N,e[13]=(f*E*i-x*p*i+x*n*m-t*E*m-f*n*v+t*p*v)*N,e[14]=(x*c*i-a*E*i-x*n*u+t*E*u+a*n*v-t*c*v)*N,e[15]=(a*p*i-f*c*i+f*n*u-t*p*u-a*n*m+t*c*m)*N,this}scale(e){const t=this.elements,n=e.x,i=e.y,s=e.z;return t[0]*=n,t[4]*=i,t[8]*=s,t[1]*=n,t[5]*=i,t[9]*=s,t[2]*=n,t[6]*=i,t[10]*=s,t[3]*=n,t[7]*=i,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),i=Math.sin(t),s=1-n,a=e.x,c=e.y,u=e.z,h=s*a,f=s*c;return this.set(h*a+n,h*c-i*u,h*u+i*c,0,h*c+i*u,f*c+n,f*u-i*a,0,h*u-i*c,f*u+i*a,s*u*u+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,s,a){return this.set(1,n,s,0,e,1,a,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){const i=this.elements,s=t._x,a=t._y,c=t._z,u=t._w,h=s+s,f=a+a,p=c+c,m=s*h,g=s*f,x=s*p,E=a*f,v=a*p,_=c*p,R=u*h,w=u*f,S=u*p,z=n.x,O=n.y,N=n.z;return i[0]=(1-(E+_))*z,i[1]=(g+S)*z,i[2]=(x-w)*z,i[3]=0,i[4]=(g-S)*O,i[5]=(1-(m+_))*O,i[6]=(v+R)*O,i[7]=0,i[8]=(x+w)*N,i[9]=(v-R)*N,i[10]=(1-(m+E))*N,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){const i=this.elements;let s=Ds.set(i[0],i[1],i[2]).length();const a=Ds.set(i[4],i[5],i[6]).length(),c=Ds.set(i[8],i[9],i[10]).length();this.determinant()<0&&(s=-s),e.x=i[12],e.y=i[13],e.z=i[14],vi.copy(this);const h=1/s,f=1/a,p=1/c;return vi.elements[0]*=h,vi.elements[1]*=h,vi.elements[2]*=h,vi.elements[4]*=f,vi.elements[5]*=f,vi.elements[6]*=f,vi.elements[8]*=p,vi.elements[9]*=p,vi.elements[10]*=p,t.setFromRotationMatrix(vi),n.x=s,n.y=a,n.z=c,this}makePerspective(e,t,n,i,s,a,c=er){const u=this.elements,h=2*s/(t-e),f=2*s/(n-i),p=(t+e)/(t-e),m=(n+i)/(n-i);let g,x;if(c===er)g=-(a+s)/(a-s),x=-2*a*s/(a-s);else if(c===Oc)g=-a/(a-s),x=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+c);return u[0]=h,u[4]=0,u[8]=p,u[12]=0,u[1]=0,u[5]=f,u[9]=m,u[13]=0,u[2]=0,u[6]=0,u[10]=g,u[14]=x,u[3]=0,u[7]=0,u[11]=-1,u[15]=0,this}makeOrthographic(e,t,n,i,s,a,c=er){const u=this.elements,h=1/(t-e),f=1/(n-i),p=1/(a-s),m=(t+e)*h,g=(n+i)*f;let x,E;if(c===er)x=(a+s)*p,E=-2*p;else if(c===Oc)x=s*p,E=-1*p;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+c);return u[0]=2*h,u[4]=0,u[8]=0,u[12]=-m,u[1]=0,u[5]=2*f,u[9]=0,u[13]=-g,u[2]=0,u[6]=0,u[10]=E,u[14]=-x,u[3]=0,u[7]=0,u[11]=0,u[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Ds=new U,vi=new pt,TT=new U(0,0,0),wT=new U(1,1,1),fr=new U,$a=new U,si=new U,Hp=new pt,Vp=new Mt;class wi{constructor(e=0,t=0,n=0,i=wi.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const i=e.elements,s=i[0],a=i[4],c=i[8],u=i[1],h=i[5],f=i[9],p=i[2],m=i[6],g=i[10];switch(t){case"XYZ":this._y=Math.asin(Dn(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-f,g),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(m,h),this._z=0);break;case"YXZ":this._x=Math.asin(-Dn(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(c,g),this._z=Math.atan2(u,h)):(this._y=Math.atan2(-p,s),this._z=0);break;case"ZXY":this._x=Math.asin(Dn(m,-1,1)),Math.abs(m)<.9999999?(this._y=Math.atan2(-p,g),this._z=Math.atan2(-a,h)):(this._y=0,this._z=Math.atan2(u,s));break;case"ZYX":this._y=Math.asin(-Dn(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(m,g),this._z=Math.atan2(u,s)):(this._x=0,this._z=Math.atan2(-a,h));break;case"YZX":this._z=Math.asin(Dn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(-f,h),this._y=Math.atan2(-p,s)):(this._x=0,this._y=Math.atan2(c,g));break;case"XZY":this._z=Math.asin(-Dn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(m,h),this._y=Math.atan2(c,s)):(this._x=Math.atan2(-f,g),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Hp.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Hp,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Vp.setFromEuler(this),this.setFromQuaternion(Vp,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}wi.DEFAULT_ORDER="XYZ";class yd{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let AT=0;const Gp=new U,Is=new Mt,qi=new pt,Za=new U,No=new U,RT=new U,PT=new Mt,Wp=new U(1,0,0),jp=new U(0,1,0),Xp=new U(0,0,1),qp={type:"added"},CT={type:"removed"},Ls={type:"childadded",child:null},Iu={type:"childremoved",child:null};class rn extends Rr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:AT++}),this.uuid=Mi(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=rn.DEFAULT_UP.clone();const e=new U,t=new wi,n=new Mt,i=new U(1,1,1);function s(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new pt},normalMatrix:{value:new yt}}),this.matrix=new pt,this.matrixWorld=new pt,this.matrixAutoUpdate=rn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=rn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new yd,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.multiply(Is),this}rotateOnWorldAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.premultiply(Is),this}rotateX(e){return this.rotateOnAxis(Wp,e)}rotateY(e){return this.rotateOnAxis(jp,e)}rotateZ(e){return this.rotateOnAxis(Xp,e)}translateOnAxis(e,t){return Gp.copy(e).applyQuaternion(this.quaternion),this.position.add(Gp.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Wp,e)}translateY(e){return this.translateOnAxis(jp,e)}translateZ(e){return this.translateOnAxis(Xp,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(qi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Za.copy(e):Za.set(e,t,n);const i=this.parent;this.updateWorldMatrix(!0,!1),No.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?qi.lookAt(No,Za,this.up):qi.lookAt(Za,No,this.up),this.quaternion.setFromRotationMatrix(qi),i&&(qi.extractRotation(i.matrixWorld),Is.setFromRotationMatrix(qi),this.quaternion.premultiply(Is.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(qp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(CT),Iu.child=e,this.dispatchEvent(Iu),Iu.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),qi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),qi.multiply(e.parent.matrixWorld)),e.applyMatrix4(qi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(qp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,e,RT),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,PT,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),i.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(i.type="BatchedMesh",i.perObjectFrustumCulled=this.perObjectFrustumCulled,i.sortObjects=this.sortObjects,i.drawRanges=this._drawRanges,i.reservedRanges=this._reservedRanges,i.visibility=this._visibility,i.active=this._active,i.bounds=this._bounds.map(c=>({boxInitialized:c.boxInitialized,boxMin:c.box.min.toArray(),boxMax:c.box.max.toArray(),sphereInitialized:c.sphereInitialized,sphereRadius:c.sphere.radius,sphereCenter:c.sphere.center.toArray()})),i.maxInstanceCount=this._maxInstanceCount,i.maxVertexCount=this._maxVertexCount,i.maxIndexCount=this._maxIndexCount,i.geometryInitialized=this._geometryInitialized,i.geometryCount=this._geometryCount,i.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(i.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(i.boundingSphere={center:i.boundingSphere.center.toArray(),radius:i.boundingSphere.radius}),this.boundingBox!==null&&(i.boundingBox={min:i.boundingBox.min.toArray(),max:i.boundingBox.max.toArray()}));function s(c,u){return c[u.uuid]===void 0&&(c[u.uuid]=u.toJSON(e)),u.uuid}if(this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=s(e.geometries,this.geometry);const c=this.geometry.parameters;if(c!==void 0&&c.shapes!==void 0){const u=c.shapes;if(Array.isArray(u))for(let h=0,f=u.length;h<f;h++){const p=u[h];s(e.shapes,p)}else s(e.shapes,u)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const c=[];for(let u=0,h=this.material.length;u<h;u++)c.push(s(e.materials,this.material[u]));i.material=c}else i.material=s(e.materials,this.material);if(this.children.length>0){i.children=[];for(let c=0;c<this.children.length;c++)i.children.push(this.children[c].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let c=0;c<this.animations.length;c++){const u=this.animations[c];i.animations.push(s(e.animations,u))}}if(t){const c=a(e.geometries),u=a(e.materials),h=a(e.textures),f=a(e.images),p=a(e.shapes),m=a(e.skeletons),g=a(e.animations),x=a(e.nodes);c.length>0&&(n.geometries=c),u.length>0&&(n.materials=u),h.length>0&&(n.textures=h),f.length>0&&(n.images=f),p.length>0&&(n.shapes=p),m.length>0&&(n.skeletons=m),g.length>0&&(n.animations=g),x.length>0&&(n.nodes=x)}return n.object=i,n;function a(c){const u=[];for(const h in c){const f=c[h];delete f.metadata,u.push(f)}return u}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const i=e.children[n];this.add(i.clone())}return this}}rn.DEFAULT_UP=new U(0,1,0);rn.DEFAULT_MATRIX_AUTO_UPDATE=!0;rn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const yi=new U,Yi=new U,Lu=new U,Ki=new U,Fs=new U,Ns=new U,Yp=new U,Fu=new U,Nu=new U,Ou=new U,Uu=new Bt,Bu=new Bt,ku=new Bt;class Si{constructor(e=new U,t=new U,n=new U){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),yi.subVectors(e,t),i.cross(yi);const s=i.lengthSq();return s>0?i.multiplyScalar(1/Math.sqrt(s)):i.set(0,0,0)}static getBarycoord(e,t,n,i,s){yi.subVectors(i,t),Yi.subVectors(n,t),Lu.subVectors(e,t);const a=yi.dot(yi),c=yi.dot(Yi),u=yi.dot(Lu),h=Yi.dot(Yi),f=Yi.dot(Lu),p=a*h-c*c;if(p===0)return s.set(0,0,0),null;const m=1/p,g=(h*u-c*f)*m,x=(a*f-c*u)*m;return s.set(1-g-x,x,g)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,Ki)===null?!1:Ki.x>=0&&Ki.y>=0&&Ki.x+Ki.y<=1}static getInterpolation(e,t,n,i,s,a,c,u){return this.getBarycoord(e,t,n,i,Ki)===null?(u.x=0,u.y=0,"z"in u&&(u.z=0),"w"in u&&(u.w=0),null):(u.setScalar(0),u.addScaledVector(s,Ki.x),u.addScaledVector(a,Ki.y),u.addScaledVector(c,Ki.z),u)}static getInterpolatedAttribute(e,t,n,i,s,a){return Uu.setScalar(0),Bu.setScalar(0),ku.setScalar(0),Uu.fromBufferAttribute(e,t),Bu.fromBufferAttribute(e,n),ku.fromBufferAttribute(e,i),a.setScalar(0),a.addScaledVector(Uu,s.x),a.addScaledVector(Bu,s.y),a.addScaledVector(ku,s.z),a}static isFrontFacing(e,t,n,i){return yi.subVectors(n,t),Yi.subVectors(e,t),yi.cross(Yi).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return yi.subVectors(this.c,this.b),Yi.subVectors(this.a,this.b),yi.cross(Yi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Si.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Si.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,i,s){return Si.getInterpolation(e,this.a,this.b,this.c,t,n,i,s)}containsPoint(e){return Si.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Si.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,i=this.b,s=this.c;let a,c;Fs.subVectors(i,n),Ns.subVectors(s,n),Fu.subVectors(e,n);const u=Fs.dot(Fu),h=Ns.dot(Fu);if(u<=0&&h<=0)return t.copy(n);Nu.subVectors(e,i);const f=Fs.dot(Nu),p=Ns.dot(Nu);if(f>=0&&p<=f)return t.copy(i);const m=u*p-f*h;if(m<=0&&u>=0&&f<=0)return a=u/(u-f),t.copy(n).addScaledVector(Fs,a);Ou.subVectors(e,s);const g=Fs.dot(Ou),x=Ns.dot(Ou);if(x>=0&&g<=x)return t.copy(s);const E=g*h-u*x;if(E<=0&&h>=0&&x<=0)return c=h/(h-x),t.copy(n).addScaledVector(Ns,c);const v=f*x-g*p;if(v<=0&&p-f>=0&&g-x>=0)return Yp.subVectors(s,i),c=(p-f)/(p-f+(g-x)),t.copy(i).addScaledVector(Yp,c);const _=1/(v+E+m);return a=E*_,c=m*_,t.copy(n).addScaledVector(Fs,a).addScaledVector(Ns,c)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Dg={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},pr={h:0,s:0,l:0},Qa={h:0,s:0,l:0};function zu(r,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?r+(e-r)*6*t:t<1/2?e:t<2/3?r+(e-r)*6*(2/3-t):r}class rt{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const i=e;i&&i.isColor?this.copy(i):typeof i=="number"?this.setHex(i):typeof i=="string"&&this.setStyle(i)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Tn){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,Lt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=Lt.workingColorSpace){return this.r=e,this.g=t,this.b=n,Lt.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=Lt.workingColorSpace){if(e=vd(e,1),t=Dn(t,0,1),n=Dn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,a=2*n-s;this.r=zu(a,s,e+1/3),this.g=zu(a,s,e),this.b=zu(a,s,e-1/3)}return Lt.toWorkingColorSpace(this,i),this}setStyle(e,t=Tn){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let i;if(i=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const a=i[1],c=i[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=i[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Tn){const n=Dg[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=nr(e.r),this.g=nr(e.g),this.b=nr(e.b),this}copyLinearToSRGB(e){return this.r=Ks(e.r),this.g=Ks(e.g),this.b=Ks(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Tn){return Lt.fromWorkingColorSpace(Bn.copy(this),e),Math.round(Dn(Bn.r*255,0,255))*65536+Math.round(Dn(Bn.g*255,0,255))*256+Math.round(Dn(Bn.b*255,0,255))}getHexString(e=Tn){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=Lt.workingColorSpace){Lt.fromWorkingColorSpace(Bn.copy(this),t);const n=Bn.r,i=Bn.g,s=Bn.b,a=Math.max(n,i,s),c=Math.min(n,i,s);let u,h;const f=(c+a)/2;if(c===a)u=0,h=0;else{const p=a-c;switch(h=f<=.5?p/(a+c):p/(2-a-c),a){case n:u=(i-s)/p+(i<s?6:0);break;case i:u=(s-n)/p+2;break;case s:u=(n-i)/p+4;break}u/=6}return e.h=u,e.s=h,e.l=f,e}getRGB(e,t=Lt.workingColorSpace){return Lt.fromWorkingColorSpace(Bn.copy(this),t),e.r=Bn.r,e.g=Bn.g,e.b=Bn.b,e}getStyle(e=Tn){Lt.fromWorkingColorSpace(Bn.copy(this),e);const t=Bn.r,n=Bn.g,i=Bn.b;return e!==Tn?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${i.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(i*255)})`}offsetHSL(e,t,n){return this.getHSL(pr),this.setHSL(pr.h+e,pr.s+t,pr.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(pr),e.getHSL(Qa);const n=Zo(pr.h,Qa.h,t),i=Zo(pr.s,Qa.s,t),s=Zo(pr.l,Qa.l,t);return this.setHSL(n,i,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,i=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*i,this.g=s[1]*t+s[4]*n+s[7]*i,this.b=s[2]*t+s[5]*n+s[8]*i,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Bn=new rt;rt.NAMES=Dg;let DT=0;class Ii extends Rr{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:DT++}),this.uuid=Mi(),this.name="",this.blending=qs,this.side=ir,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=gh,this.blendDst=_h,this.blendEquation=os,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new rt(0,0,0),this.blendAlpha=0,this.depthFunc=Zs,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Dp,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=ws,this.stencilZFail=ws,this.stencilZPass=ws,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const i=this[t];if(i===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==qs&&(n.blending=this.blending),this.side!==ir&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==gh&&(n.blendSrc=this.blendSrc),this.blendDst!==_h&&(n.blendDst=this.blendDst),this.blendEquation!==os&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Zs&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Dp&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==ws&&(n.stencilFail=this.stencilFail),this.stencilZFail!==ws&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==ws&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(s){const a=[];for(const c in s){const u=s[c];delete u.metadata,a.push(u)}return a}if(t){const s=i(e.textures),a=i(e.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const i=t.length;n=new Array(i);for(let s=0;s!==i;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class pi extends Ii{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new rt(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new wi,this.combine=hg,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const pn=new U,Ja=new ht;class hn{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=ed,this.updateRanges=[],this.gpuType=Ei,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,s=this.itemSize;i<s;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Ja.fromBufferAttribute(this,t),Ja.applyMatrix3(e),this.setXY(t,Ja.x,Ja.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)pn.fromBufferAttribute(this,t),pn.applyMatrix3(e),this.setXYZ(t,pn.x,pn.y,pn.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)pn.fromBufferAttribute(this,t),pn.applyMatrix4(e),this.setXYZ(t,pn.x,pn.y,pn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)pn.fromBufferAttribute(this,t),pn.applyNormalMatrix(e),this.setXYZ(t,pn.x,pn.y,pn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)pn.fromBufferAttribute(this,t),pn.transformDirection(e),this.setXYZ(t,pn.x,pn.y,pn.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=bi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=jt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=bi(t,this.array)),t}setX(e,t){return this.normalized&&(t=jt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=bi(t,this.array)),t}setY(e,t){return this.normalized&&(t=jt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=bi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=jt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=bi(t,this.array)),t}setW(e,t){return this.normalized&&(t=jt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=jt(t,this.array),n=jt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=jt(t,this.array),n=jt(n,this.array),i=jt(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e*=this.itemSize,this.normalized&&(t=jt(t,this.array),n=jt(n,this.array),i=jt(i,this.array),s=jt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==ed&&(e.usage=this.usage),e}}class Ig extends hn{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Lg extends hn{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class Zt extends hn{constructor(e,t,n){super(new Float32Array(e),t,n)}}let IT=0;const hi=new pt,Hu=new rn,Os=new U,oi=new Ti,Oo=new Ti,Mn=new U;class yn extends Rr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:IT++}),this.uuid=Mi(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Rg(e)?Lg:Ig)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new yt().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return hi.makeRotationFromQuaternion(e),this.applyMatrix4(hi),this}rotateX(e){return hi.makeRotationX(e),this.applyMatrix4(hi),this}rotateY(e){return hi.makeRotationY(e),this.applyMatrix4(hi),this}rotateZ(e){return hi.makeRotationZ(e),this.applyMatrix4(hi),this}translate(e,t,n){return hi.makeTranslation(e,t,n),this.applyMatrix4(hi),this}scale(e,t,n){return hi.makeScale(e,t,n),this.applyMatrix4(hi),this}lookAt(e){return Hu.lookAt(e),Hu.updateMatrix(),this.applyMatrix4(Hu.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Os).negate(),this.translate(Os.x,Os.y,Os.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let i=0,s=e.length;i<s;i++){const a=e[i];n.push(a.x,a.y,a.z||0)}this.setAttribute("position",new Zt(n,3))}else{for(let n=0,i=t.count;n<i;n++){const s=e[n];t.setXYZ(n,s.x,s.y,s.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Ti);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new U(-1/0,-1/0,-1/0),new U(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){const s=t[n];oi.setFromBufferAttribute(s),this.morphTargetsRelative?(Mn.addVectors(this.boundingBox.min,oi.min),this.boundingBox.expandByPoint(Mn),Mn.addVectors(this.boundingBox.max,oi.max),this.boundingBox.expandByPoint(Mn)):(this.boundingBox.expandByPoint(oi.min),this.boundingBox.expandByPoint(oi.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Li);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new U,1/0);return}if(e){const n=this.boundingSphere.center;if(oi.setFromBufferAttribute(e),t)for(let s=0,a=t.length;s<a;s++){const c=t[s];Oo.setFromBufferAttribute(c),this.morphTargetsRelative?(Mn.addVectors(oi.min,Oo.min),oi.expandByPoint(Mn),Mn.addVectors(oi.max,Oo.max),oi.expandByPoint(Mn)):(oi.expandByPoint(Oo.min),oi.expandByPoint(Oo.max))}oi.getCenter(n);let i=0;for(let s=0,a=e.count;s<a;s++)Mn.fromBufferAttribute(e,s),i=Math.max(i,n.distanceToSquared(Mn));if(t)for(let s=0,a=t.length;s<a;s++){const c=t[s],u=this.morphTargetsRelative;for(let h=0,f=c.count;h<f;h++)Mn.fromBufferAttribute(c,h),u&&(Os.fromBufferAttribute(e,h),Mn.add(Os)),i=Math.max(i,n.distanceToSquared(Mn))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,i=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new hn(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),c=[],u=[];for(let V=0;V<n.count;V++)c[V]=new U,u[V]=new U;const h=new U,f=new U,p=new U,m=new ht,g=new ht,x=new ht,E=new U,v=new U;function _(V,D,A){h.fromBufferAttribute(n,V),f.fromBufferAttribute(n,D),p.fromBufferAttribute(n,A),m.fromBufferAttribute(s,V),g.fromBufferAttribute(s,D),x.fromBufferAttribute(s,A),f.sub(h),p.sub(h),g.sub(m),x.sub(m);const k=1/(g.x*x.y-x.x*g.y);isFinite(k)&&(E.copy(f).multiplyScalar(x.y).addScaledVector(p,-g.y).multiplyScalar(k),v.copy(p).multiplyScalar(g.x).addScaledVector(f,-x.x).multiplyScalar(k),c[V].add(E),c[D].add(E),c[A].add(E),u[V].add(v),u[D].add(v),u[A].add(v))}let R=this.groups;R.length===0&&(R=[{start:0,count:e.count}]);for(let V=0,D=R.length;V<D;++V){const A=R[V],k=A.start,J=A.count;for(let ee=k,re=k+J;ee<re;ee+=3)_(e.getX(ee+0),e.getX(ee+1),e.getX(ee+2))}const w=new U,S=new U,z=new U,O=new U;function N(V){z.fromBufferAttribute(i,V),O.copy(z);const D=c[V];w.copy(D),w.sub(z.multiplyScalar(z.dot(D))).normalize(),S.crossVectors(O,D);const k=S.dot(u[V])<0?-1:1;a.setXYZW(V,w.x,w.y,w.z,k)}for(let V=0,D=R.length;V<D;++V){const A=R[V],k=A.start,J=A.count;for(let ee=k,re=k+J;ee<re;ee+=3)N(e.getX(ee+0)),N(e.getX(ee+1)),N(e.getX(ee+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new hn(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let m=0,g=n.count;m<g;m++)n.setXYZ(m,0,0,0);const i=new U,s=new U,a=new U,c=new U,u=new U,h=new U,f=new U,p=new U;if(e)for(let m=0,g=e.count;m<g;m+=3){const x=e.getX(m+0),E=e.getX(m+1),v=e.getX(m+2);i.fromBufferAttribute(t,x),s.fromBufferAttribute(t,E),a.fromBufferAttribute(t,v),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),c.fromBufferAttribute(n,x),u.fromBufferAttribute(n,E),h.fromBufferAttribute(n,v),c.add(f),u.add(f),h.add(f),n.setXYZ(x,c.x,c.y,c.z),n.setXYZ(E,u.x,u.y,u.z),n.setXYZ(v,h.x,h.y,h.z)}else for(let m=0,g=t.count;m<g;m+=3)i.fromBufferAttribute(t,m+0),s.fromBufferAttribute(t,m+1),a.fromBufferAttribute(t,m+2),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),n.setXYZ(m+0,f.x,f.y,f.z),n.setXYZ(m+1,f.x,f.y,f.z),n.setXYZ(m+2,f.x,f.y,f.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)Mn.fromBufferAttribute(e,t),Mn.normalize(),e.setXYZ(t,Mn.x,Mn.y,Mn.z)}toNonIndexed(){function e(c,u){const h=c.array,f=c.itemSize,p=c.normalized,m=new h.constructor(u.length*f);let g=0,x=0;for(let E=0,v=u.length;E<v;E++){c.isInterleavedBufferAttribute?g=u[E]*c.data.stride+c.offset:g=u[E]*f;for(let _=0;_<f;_++)m[x++]=h[g++]}return new hn(m,f,p)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new yn,n=this.index.array,i=this.attributes;for(const c in i){const u=i[c],h=e(u,n);t.setAttribute(c,h)}const s=this.morphAttributes;for(const c in s){const u=[],h=s[c];for(let f=0,p=h.length;f<p;f++){const m=h[f],g=e(m,n);u.push(g)}t.morphAttributes[c]=u}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];t.addGroup(h.start,h.count,h.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const u=this.parameters;for(const h in u)u[h]!==void 0&&(e[h]=u[h]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const u in n){const h=n[u];e.data.attributes[u]=h.toJSON(e.data)}const i={};let s=!1;for(const u in this.morphAttributes){const h=this.morphAttributes[u],f=[];for(let p=0,m=h.length;p<m;p++){const g=h[p];f.push(g.toJSON(e.data))}f.length>0&&(i[u]=f,s=!0)}s&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const c=this.boundingSphere;return c!==null&&(e.data.boundingSphere={center:c.center.toArray(),radius:c.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const i=e.attributes;for(const h in i){const f=i[h];this.setAttribute(h,f.clone(t))}const s=e.morphAttributes;for(const h in s){const f=[],p=s[h];for(let m=0,g=p.length;m<g;m++)f.push(p[m].clone(t));this.morphAttributes[h]=f}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let h=0,f=a.length;h<f;h++){const p=a[h];this.addGroup(p.start,p.count,p.materialIndex)}const c=e.boundingBox;c!==null&&(this.boundingBox=c.clone());const u=e.boundingSphere;return u!==null&&(this.boundingSphere=u.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Kp=new pt,Qr=new co,ec=new Li,$p=new U,tc=new U,nc=new U,ic=new U,Vu=new U,rc=new U,Zp=new U,sc=new U;class Pe extends rn{constructor(e=new yn,t=new pi){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}getVertexPosition(e,t){const n=this.geometry,i=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(i,e);const c=this.morphTargetInfluences;if(s&&c){rc.set(0,0,0);for(let u=0,h=s.length;u<h;u++){const f=c[u],p=s[u];f!==0&&(Vu.fromBufferAttribute(p,e),a?rc.addScaledVector(Vu,f):rc.addScaledVector(Vu.sub(t),f))}t.add(rc)}return t}raycast(e,t){const n=this.geometry,i=this.material,s=this.matrixWorld;i!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),ec.copy(n.boundingSphere),ec.applyMatrix4(s),Qr.copy(e.ray).recast(e.near),!(ec.containsPoint(Qr.origin)===!1&&(Qr.intersectSphere(ec,$p)===null||Qr.origin.distanceToSquared($p)>(e.far-e.near)**2))&&(Kp.copy(s).invert(),Qr.copy(e.ray).applyMatrix4(Kp),!(n.boundingBox!==null&&Qr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Qr)))}_computeIntersections(e,t,n){let i;const s=this.geometry,a=this.material,c=s.index,u=s.attributes.position,h=s.attributes.uv,f=s.attributes.uv1,p=s.attributes.normal,m=s.groups,g=s.drawRange;if(c!==null)if(Array.isArray(a))for(let x=0,E=m.length;x<E;x++){const v=m[x],_=a[v.materialIndex],R=Math.max(v.start,g.start),w=Math.min(c.count,Math.min(v.start+v.count,g.start+g.count));for(let S=R,z=w;S<z;S+=3){const O=c.getX(S),N=c.getX(S+1),V=c.getX(S+2);i=oc(this,_,e,n,h,f,p,O,N,V),i&&(i.faceIndex=Math.floor(S/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),E=Math.min(c.count,g.start+g.count);for(let v=x,_=E;v<_;v+=3){const R=c.getX(v),w=c.getX(v+1),S=c.getX(v+2);i=oc(this,a,e,n,h,f,p,R,w,S),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}else if(u!==void 0)if(Array.isArray(a))for(let x=0,E=m.length;x<E;x++){const v=m[x],_=a[v.materialIndex],R=Math.max(v.start,g.start),w=Math.min(u.count,Math.min(v.start+v.count,g.start+g.count));for(let S=R,z=w;S<z;S+=3){const O=S,N=S+1,V=S+2;i=oc(this,_,e,n,h,f,p,O,N,V),i&&(i.faceIndex=Math.floor(S/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),E=Math.min(u.count,g.start+g.count);for(let v=x,_=E;v<_;v+=3){const R=v,w=v+1,S=v+2;i=oc(this,a,e,n,h,f,p,R,w,S),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}}}function LT(r,e,t,n,i,s,a,c){let u;if(e.side===Zn?u=n.intersectTriangle(a,s,i,!0,c):u=n.intersectTriangle(i,s,a,e.side===ir,c),u===null)return null;sc.copy(c),sc.applyMatrix4(r.matrixWorld);const h=t.ray.origin.distanceTo(sc);return h<t.near||h>t.far?null:{distance:h,point:sc.clone(),object:r}}function oc(r,e,t,n,i,s,a,c,u,h){r.getVertexPosition(c,tc),r.getVertexPosition(u,nc),r.getVertexPosition(h,ic);const f=LT(r,e,t,n,tc,nc,ic,Zp);if(f){const p=new U;Si.getBarycoord(Zp,tc,nc,ic,p),i&&(f.uv=Si.getInterpolatedAttribute(i,c,u,h,p,new ht)),s&&(f.uv1=Si.getInterpolatedAttribute(s,c,u,h,p,new ht)),a&&(f.normal=Si.getInterpolatedAttribute(a,c,u,h,p,new U),f.normal.dot(n.direction)>0&&f.normal.multiplyScalar(-1));const m={a:c,b:u,c:h,normal:new U,materialIndex:0};Si.getNormal(tc,nc,ic,m.normal),f.face=m,f.barycoord=p}return f}class ln extends yn{constructor(e=1,t=1,n=1,i=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:s,depthSegments:a};const c=this;i=Math.floor(i),s=Math.floor(s),a=Math.floor(a);const u=[],h=[],f=[],p=[];let m=0,g=0;x("z","y","x",-1,-1,n,t,e,a,s,0),x("z","y","x",1,-1,n,t,-e,a,s,1),x("x","z","y",1,1,e,n,t,i,a,2),x("x","z","y",1,-1,e,n,-t,i,a,3),x("x","y","z",1,-1,e,t,n,i,s,4),x("x","y","z",-1,-1,e,t,-n,i,s,5),this.setIndex(u),this.setAttribute("position",new Zt(h,3)),this.setAttribute("normal",new Zt(f,3)),this.setAttribute("uv",new Zt(p,2));function x(E,v,_,R,w,S,z,O,N,V,D){const A=S/N,k=z/V,J=S/2,ee=z/2,re=O/2,le=N+1,Y=V+1;let de=0,ne=0;const ye=new U;for(let Te=0;Te<Y;Te++){const ze=Te*k-ee;for(let We=0;We<le;We++){const xt=We*A-J;ye[E]=xt*R,ye[v]=ze*w,ye[_]=re,h.push(ye.x,ye.y,ye.z),ye[E]=0,ye[v]=0,ye[_]=O>0?1:-1,f.push(ye.x,ye.y,ye.z),p.push(We/N),p.push(1-Te/V),de+=1}}for(let Te=0;Te<V;Te++)for(let ze=0;ze<N;ze++){const We=m+ze+le*Te,xt=m+ze+le*(Te+1),ue=m+(ze+1)+le*(Te+1),me=m+(ze+1)+le*Te;u.push(We,xt,me),u.push(xt,ue,me),ne+=6}c.addGroup(g,ne,D),g+=ne,m+=de}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ln(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function ro(r){const e={};for(const t in r){e[t]={};for(const n in r[t]){const i=r[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?i.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}function Vn(r){const e={};for(let t=0;t<r.length;t++){const n=ro(r[t]);for(const i in n)e[i]=n[i]}return e}function FT(r){const e=[];for(let t=0;t<r.length;t++)e.push(r[t].clone());return e}function Fg(r){const e=r.getRenderTarget();return e===null?r.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:Lt.workingColorSpace}const NT={clone:ro,merge:Vn};var OT=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,UT=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Tr extends Ii{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=OT,this.fragmentShader=UT,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=ro(e.uniforms),this.uniformsGroups=FT(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const i in this.uniforms){const a=this.uniforms[i].value;a&&a.isTexture?t.uniforms[i]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[i]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[i]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[i]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[i]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[i]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[i]={type:"m4",value:a.toArray()}:t.uniforms[i]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Ng extends rn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new pt,this.projectionMatrix=new pt,this.projectionMatrixInverse=new pt,this.coordinateSystem=er}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const mr=new U,Qp=new ht,Jp=new ht;class Gn extends Ng{constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=io*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan($o*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return io*2*Math.atan(Math.tan($o*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){mr.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(mr.x,mr.y).multiplyScalar(-e/mr.z),mr.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(mr.x,mr.y).multiplyScalar(-e/mr.z)}getViewSize(e,t){return this.getViewBounds(e,Qp,Jp),t.subVectors(Jp,Qp)}setViewOffset(e,t,n,i,s,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan($o*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,s=-.5*i;const a=this.view;if(this.view!==null&&this.view.enabled){const u=a.fullWidth,h=a.fullHeight;s+=a.offsetX*i/u,t-=a.offsetY*n/h,i*=a.width/u,n*=a.height/h}const c=this.filmOffset;c!==0&&(s+=e*c/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+i,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Us=-90,Bs=1;class BT extends rn{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const i=new Gn(Us,Bs,e,t);i.layers=this.layers,this.add(i);const s=new Gn(Us,Bs,e,t);s.layers=this.layers,this.add(s);const a=new Gn(Us,Bs,e,t);a.layers=this.layers,this.add(a);const c=new Gn(Us,Bs,e,t);c.layers=this.layers,this.add(c);const u=new Gn(Us,Bs,e,t);u.layers=this.layers,this.add(u);const h=new Gn(Us,Bs,e,t);h.layers=this.layers,this.add(h)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,i,s,a,c,u]=t;for(const h of t)this.remove(h);if(e===er)n.up.set(0,1,0),n.lookAt(1,0,0),i.up.set(0,1,0),i.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),c.up.set(0,1,0),c.lookAt(0,0,1),u.up.set(0,1,0),u.lookAt(0,0,-1);else if(e===Oc)n.up.set(0,-1,0),n.lookAt(-1,0,0),i.up.set(0,-1,0),i.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),c.up.set(0,-1,0),c.lookAt(0,0,1),u.up.set(0,-1,0),u.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const h of t)this.add(h),h.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:i}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,a,c,u,h,f]=this.children,p=e.getRenderTarget(),m=e.getActiveCubeFace(),g=e.getActiveMipmapLevel(),x=e.xr.enabled;e.xr.enabled=!1;const E=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,i),e.render(t,s),e.setRenderTarget(n,1,i),e.render(t,a),e.setRenderTarget(n,2,i),e.render(t,c),e.setRenderTarget(n,3,i),e.render(t,u),e.setRenderTarget(n,4,i),e.render(t,h),n.texture.generateMipmaps=E,e.setRenderTarget(n,5,i),e.render(t,f),e.setRenderTarget(p,m,g),e.xr.enabled=x,n.texture.needsPMREMUpdate=!0}}class Og extends wn{constructor(e,t,n,i,s,a,c,u,h,f){e=e!==void 0?e:[],t=t!==void 0?t:Qs,super(e,t,n,i,s,a,c,u,h,f),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class kT extends us{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new Og(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ai}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},i=new ln(5,5,5),s=new Tr({name:"CubemapFromEquirect",uniforms:ro(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Zn,blending:Er});s.uniforms.tEquirect.value=t;const a=new Pe(i,s),c=t.minFilter;return t.minFilter===Ji&&(t.minFilter=ai),new BT(1,10,this).update(e,a),t.minFilter=c,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,i){const s=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,i);e.setRenderTarget(s)}}const Gu=new U,zT=new U,HT=new yt;class yr{constructor(e=new U(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const i=Gu.subVectors(n,t).cross(zT.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Gu),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/i;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||HT.getNormalMatrix(e),i=this.coplanarPoint(Gu).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Jr=new Li,ac=new U;class xd{constructor(e=new yr,t=new yr,n=new yr,i=new yr,s=new yr,a=new yr){this.planes=[e,t,n,i,s,a]}set(e,t,n,i,s,a){const c=this.planes;return c[0].copy(e),c[1].copy(t),c[2].copy(n),c[3].copy(i),c[4].copy(s),c[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=er){const n=this.planes,i=e.elements,s=i[0],a=i[1],c=i[2],u=i[3],h=i[4],f=i[5],p=i[6],m=i[7],g=i[8],x=i[9],E=i[10],v=i[11],_=i[12],R=i[13],w=i[14],S=i[15];if(n[0].setComponents(u-s,m-h,v-g,S-_).normalize(),n[1].setComponents(u+s,m+h,v+g,S+_).normalize(),n[2].setComponents(u+a,m+f,v+x,S+R).normalize(),n[3].setComponents(u-a,m-f,v-x,S-R).normalize(),n[4].setComponents(u-c,m-p,v-E,S-w).normalize(),t===er)n[5].setComponents(u+c,m+p,v+E,S+w).normalize();else if(t===Oc)n[5].setComponents(c,p,E,w).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Jr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Jr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Jr)}intersectsSprite(e){return Jr.center.set(0,0,0),Jr.radius=.7071067811865476,Jr.applyMatrix4(e.matrixWorld),this.intersectsSphere(Jr)}intersectsSphere(e){const t=this.planes,n=e.center,i=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const i=t[n];if(ac.x=i.normal.x>0?e.max.x:e.min.x,ac.y=i.normal.y>0?e.max.y:e.min.y,ac.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(ac)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Ug(){let r=null,e=!1,t=null,n=null;function i(s,a){t(s,a),n=r.requestAnimationFrame(i)}return{start:function(){e!==!0&&t!==null&&(n=r.requestAnimationFrame(i),e=!0)},stop:function(){r.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){r=s}}}function VT(r){const e=new WeakMap;function t(c,u){const h=c.array,f=c.usage,p=h.byteLength,m=r.createBuffer();r.bindBuffer(u,m),r.bufferData(u,h,f),c.onUploadCallback();let g;if(h instanceof Float32Array)g=r.FLOAT;else if(h instanceof Uint16Array)c.isFloat16BufferAttribute?g=r.HALF_FLOAT:g=r.UNSIGNED_SHORT;else if(h instanceof Int16Array)g=r.SHORT;else if(h instanceof Uint32Array)g=r.UNSIGNED_INT;else if(h instanceof Int32Array)g=r.INT;else if(h instanceof Int8Array)g=r.BYTE;else if(h instanceof Uint8Array)g=r.UNSIGNED_BYTE;else if(h instanceof Uint8ClampedArray)g=r.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+h);return{buffer:m,type:g,bytesPerElement:h.BYTES_PER_ELEMENT,version:c.version,size:p}}function n(c,u,h){const f=u.array,p=u.updateRanges;if(r.bindBuffer(h,c),p.length===0)r.bufferSubData(h,0,f);else{p.sort((g,x)=>g.start-x.start);let m=0;for(let g=1;g<p.length;g++){const x=p[m],E=p[g];E.start<=x.start+x.count+1?x.count=Math.max(x.count,E.start+E.count-x.start):(++m,p[m]=E)}p.length=m+1;for(let g=0,x=p.length;g<x;g++){const E=p[g];r.bufferSubData(h,E.start*f.BYTES_PER_ELEMENT,f,E.start,E.count)}u.clearUpdateRanges()}u.onUploadCallback()}function i(c){return c.isInterleavedBufferAttribute&&(c=c.data),e.get(c)}function s(c){c.isInterleavedBufferAttribute&&(c=c.data);const u=e.get(c);u&&(r.deleteBuffer(u.buffer),e.delete(c))}function a(c,u){if(c.isInterleavedBufferAttribute&&(c=c.data),c.isGLBufferAttribute){const f=e.get(c);(!f||f.version<c.version)&&e.set(c,{buffer:c.buffer,type:c.type,bytesPerElement:c.elementSize,version:c.version});return}const h=e.get(c);if(h===void 0)e.set(c,t(c,u));else if(h.version<c.version){if(h.size!==c.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(h.buffer,c,u),h.version=c.version}}return{get:i,remove:s,update:a}}class lo extends yn{constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};const s=e/2,a=t/2,c=Math.floor(n),u=Math.floor(i),h=c+1,f=u+1,p=e/c,m=t/u,g=[],x=[],E=[],v=[];for(let _=0;_<f;_++){const R=_*m-a;for(let w=0;w<h;w++){const S=w*p-s;x.push(S,-R,0),E.push(0,0,1),v.push(w/c),v.push(1-_/u)}}for(let _=0;_<u;_++)for(let R=0;R<c;R++){const w=R+h*_,S=R+h*(_+1),z=R+1+h*(_+1),O=R+1+h*_;g.push(w,S,O),g.push(S,z,O)}this.setIndex(g),this.setAttribute("position",new Zt(x,3)),this.setAttribute("normal",new Zt(E,3)),this.setAttribute("uv",new Zt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new lo(e.width,e.height,e.widthSegments,e.heightSegments)}}var GT=`#ifdef USE_ALPHAHASH
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
#endif`,cw=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,lw=`#if defined( USE_COLOR_ALPHA )
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
#endif`,cA=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,lA=`#ifndef FLAT_SHADED
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
}`,c1=`#define NORMAL
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
}`,l1=`#define NORMAL
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
}`,Et={alphahash_fragment:GT,alphahash_pars_fragment:WT,alphamap_fragment:jT,alphamap_pars_fragment:XT,alphatest_fragment:qT,alphatest_pars_fragment:YT,aomap_fragment:KT,aomap_pars_fragment:$T,batching_pars_vertex:ZT,batching_vertex:QT,begin_vertex:JT,beginnormal_vertex:ew,bsdfs:tw,iridescence_fragment:nw,bumpmap_pars_fragment:iw,clipping_planes_fragment:rw,clipping_planes_pars_fragment:sw,clipping_planes_pars_vertex:ow,clipping_planes_vertex:aw,color_fragment:cw,color_pars_fragment:lw,color_pars_vertex:uw,color_vertex:hw,common:dw,cube_uv_reflection_fragment:fw,defaultnormal_vertex:pw,displacementmap_pars_vertex:mw,displacementmap_vertex:gw,emissivemap_fragment:_w,emissivemap_pars_fragment:vw,colorspace_fragment:yw,colorspace_pars_fragment:xw,envmap_fragment:bw,envmap_common_pars_fragment:Sw,envmap_pars_fragment:Ew,envmap_pars_vertex:Mw,envmap_physical_pars_fragment:Nw,envmap_vertex:Tw,fog_vertex:ww,fog_pars_vertex:Aw,fog_fragment:Rw,fog_pars_fragment:Pw,gradientmap_pars_fragment:Cw,lightmap_pars_fragment:Dw,lights_lambert_fragment:Iw,lights_lambert_pars_fragment:Lw,lights_pars_begin:Fw,lights_toon_fragment:Ow,lights_toon_pars_fragment:Uw,lights_phong_fragment:Bw,lights_phong_pars_fragment:kw,lights_physical_fragment:zw,lights_physical_pars_fragment:Hw,lights_fragment_begin:Vw,lights_fragment_maps:Gw,lights_fragment_end:Ww,logdepthbuf_fragment:jw,logdepthbuf_pars_fragment:Xw,logdepthbuf_pars_vertex:qw,logdepthbuf_vertex:Yw,map_fragment:Kw,map_pars_fragment:$w,map_particle_fragment:Zw,map_particle_pars_fragment:Qw,metalnessmap_fragment:Jw,metalnessmap_pars_fragment:eA,morphinstance_vertex:tA,morphcolor_vertex:nA,morphnormal_vertex:iA,morphtarget_pars_vertex:rA,morphtarget_vertex:sA,normal_fragment_begin:oA,normal_fragment_maps:aA,normal_pars_fragment:cA,normal_pars_vertex:lA,normal_vertex:uA,normalmap_pars_fragment:hA,clearcoat_normal_fragment_begin:dA,clearcoat_normal_fragment_maps:fA,clearcoat_pars_fragment:pA,iridescence_pars_fragment:mA,opaque_fragment:gA,packing:_A,premultiplied_alpha_fragment:vA,project_vertex:yA,dithering_fragment:xA,dithering_pars_fragment:bA,roughnessmap_fragment:SA,roughnessmap_pars_fragment:EA,shadowmap_pars_fragment:MA,shadowmap_pars_vertex:TA,shadowmap_vertex:wA,shadowmask_pars_fragment:AA,skinbase_vertex:RA,skinning_pars_vertex:PA,skinning_vertex:CA,skinnormal_vertex:DA,specularmap_fragment:IA,specularmap_pars_fragment:LA,tonemapping_fragment:FA,tonemapping_pars_fragment:NA,transmission_fragment:OA,transmission_pars_fragment:UA,uv_pars_fragment:BA,uv_pars_vertex:kA,uv_vertex:zA,worldpos_vertex:HA,background_vert:VA,background_frag:GA,backgroundCube_vert:WA,backgroundCube_frag:jA,cube_vert:XA,cube_frag:qA,depth_vert:YA,depth_frag:KA,distanceRGBA_vert:$A,distanceRGBA_frag:ZA,equirect_vert:QA,equirect_frag:JA,linedashed_vert:e1,linedashed_frag:t1,meshbasic_vert:n1,meshbasic_frag:i1,meshlambert_vert:r1,meshlambert_frag:s1,meshmatcap_vert:o1,meshmatcap_frag:a1,meshnormal_vert:c1,meshnormal_frag:l1,meshphong_vert:u1,meshphong_frag:h1,meshphysical_vert:d1,meshphysical_frag:f1,meshtoon_vert:p1,meshtoon_frag:m1,points_vert:g1,points_frag:_1,shadow_vert:v1,shadow_frag:y1,sprite_vert:x1,sprite_frag:b1},Le={common:{diffuse:{value:new rt(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new yt},alphaMap:{value:null},alphaMapTransform:{value:new yt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new yt}},envmap:{envMap:{value:null},envMapRotation:{value:new yt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new yt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new yt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new yt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new yt},normalScale:{value:new ht(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new yt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new yt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new yt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new yt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new rt(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new rt(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new yt},alphaTest:{value:0},uvTransform:{value:new yt}},sprite:{diffuse:{value:new rt(16777215)},opacity:{value:1},center:{value:new ht(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new yt},alphaMap:{value:null},alphaMapTransform:{value:new yt},alphaTest:{value:0}}},Ci={basic:{uniforms:Vn([Le.common,Le.specularmap,Le.envmap,Le.aomap,Le.lightmap,Le.fog]),vertexShader:Et.meshbasic_vert,fragmentShader:Et.meshbasic_frag},lambert:{uniforms:Vn([Le.common,Le.specularmap,Le.envmap,Le.aomap,Le.lightmap,Le.emissivemap,Le.bumpmap,Le.normalmap,Le.displacementmap,Le.fog,Le.lights,{emissive:{value:new rt(0)}}]),vertexShader:Et.meshlambert_vert,fragmentShader:Et.meshlambert_frag},phong:{uniforms:Vn([Le.common,Le.specularmap,Le.envmap,Le.aomap,Le.lightmap,Le.emissivemap,Le.bumpmap,Le.normalmap,Le.displacementmap,Le.fog,Le.lights,{emissive:{value:new rt(0)},specular:{value:new rt(1118481)},shininess:{value:30}}]),vertexShader:Et.meshphong_vert,fragmentShader:Et.meshphong_frag},standard:{uniforms:Vn([Le.common,Le.envmap,Le.aomap,Le.lightmap,Le.emissivemap,Le.bumpmap,Le.normalmap,Le.displacementmap,Le.roughnessmap,Le.metalnessmap,Le.fog,Le.lights,{emissive:{value:new rt(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:Et.meshphysical_vert,fragmentShader:Et.meshphysical_frag},toon:{uniforms:Vn([Le.common,Le.aomap,Le.lightmap,Le.emissivemap,Le.bumpmap,Le.normalmap,Le.displacementmap,Le.gradientmap,Le.fog,Le.lights,{emissive:{value:new rt(0)}}]),vertexShader:Et.meshtoon_vert,fragmentShader:Et.meshtoon_frag},matcap:{uniforms:Vn([Le.common,Le.bumpmap,Le.normalmap,Le.displacementmap,Le.fog,{matcap:{value:null}}]),vertexShader:Et.meshmatcap_vert,fragmentShader:Et.meshmatcap_frag},points:{uniforms:Vn([Le.points,Le.fog]),vertexShader:Et.points_vert,fragmentShader:Et.points_frag},dashed:{uniforms:Vn([Le.common,Le.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:Et.linedashed_vert,fragmentShader:Et.linedashed_frag},depth:{uniforms:Vn([Le.common,Le.displacementmap]),vertexShader:Et.depth_vert,fragmentShader:Et.depth_frag},normal:{uniforms:Vn([Le.common,Le.bumpmap,Le.normalmap,Le.displacementmap,{opacity:{value:1}}]),vertexShader:Et.meshnormal_vert,fragmentShader:Et.meshnormal_frag},sprite:{uniforms:Vn([Le.sprite,Le.fog]),vertexShader:Et.sprite_vert,fragmentShader:Et.sprite_frag},background:{uniforms:{uvTransform:{value:new yt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:Et.background_vert,fragmentShader:Et.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new yt}},vertexShader:Et.backgroundCube_vert,fragmentShader:Et.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:Et.cube_vert,fragmentShader:Et.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:Et.equirect_vert,fragmentShader:Et.equirect_frag},distanceRGBA:{uniforms:Vn([Le.common,Le.displacementmap,{referencePosition:{value:new U},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:Et.distanceRGBA_vert,fragmentShader:Et.distanceRGBA_frag},shadow:{uniforms:Vn([Le.lights,Le.fog,{color:{value:new rt(0)},opacity:{value:1}}]),vertexShader:Et.shadow_vert,fragmentShader:Et.shadow_frag}};Ci.physical={uniforms:Vn([Ci.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new yt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new yt},clearcoatNormalScale:{value:new ht(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new yt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new yt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new yt},sheen:{value:0},sheenColor:{value:new rt(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new yt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new yt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new yt},transmissionSamplerSize:{value:new ht},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new yt},attenuationDistance:{value:0},attenuationColor:{value:new rt(0)},specularColor:{value:new rt(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new yt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new yt},anisotropyVector:{value:new ht},anisotropyMap:{value:null},anisotropyMapTransform:{value:new yt}}]),vertexShader:Et.meshphysical_vert,fragmentShader:Et.meshphysical_frag};const cc={r:0,b:0,g:0},es=new wi,S1=new pt;function E1(r,e,t,n,i,s,a){const c=new rt(0);let u=s===!0?0:1,h,f,p=null,m=0,g=null;function x(R){let w=R.isScene===!0?R.background:null;return w&&w.isTexture&&(w=(R.backgroundBlurriness>0?t:e).get(w)),w}function E(R){let w=!1;const S=x(R);S===null?_(c,u):S&&S.isColor&&(_(S,1),w=!0);const z=r.xr.getEnvironmentBlendMode();z==="additive"?n.buffers.color.setClear(0,0,0,1,a):z==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(r.autoClear||w)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),r.clear(r.autoClearColor,r.autoClearDepth,r.autoClearStencil))}function v(R,w){const S=x(w);S&&(S.isCubeTexture||S.mapping===kc)?(f===void 0&&(f=new Pe(new ln(1,1,1),new Tr({name:"BackgroundCubeMaterial",uniforms:ro(Ci.backgroundCube.uniforms),vertexShader:Ci.backgroundCube.vertexShader,fragmentShader:Ci.backgroundCube.fragmentShader,side:Zn,depthTest:!1,depthWrite:!1,fog:!1})),f.geometry.deleteAttribute("normal"),f.geometry.deleteAttribute("uv"),f.onBeforeRender=function(z,O,N){this.matrixWorld.copyPosition(N.matrixWorld)},Object.defineProperty(f.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(f)),es.copy(w.backgroundRotation),es.x*=-1,es.y*=-1,es.z*=-1,S.isCubeTexture&&S.isRenderTargetTexture===!1&&(es.y*=-1,es.z*=-1),f.material.uniforms.envMap.value=S,f.material.uniforms.flipEnvMap.value=S.isCubeTexture&&S.isRenderTargetTexture===!1?-1:1,f.material.uniforms.backgroundBlurriness.value=w.backgroundBlurriness,f.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,f.material.uniforms.backgroundRotation.value.setFromMatrix4(S1.makeRotationFromEuler(es)),f.material.toneMapped=Lt.getTransfer(S.colorSpace)!==qt,(p!==S||m!==S.version||g!==r.toneMapping)&&(f.material.needsUpdate=!0,p=S,m=S.version,g=r.toneMapping),f.layers.enableAll(),R.unshift(f,f.geometry,f.material,0,0,null)):S&&S.isTexture&&(h===void 0&&(h=new Pe(new lo(2,2),new Tr({name:"BackgroundMaterial",uniforms:ro(Ci.background.uniforms),vertexShader:Ci.background.vertexShader,fragmentShader:Ci.background.fragmentShader,side:ir,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),Object.defineProperty(h.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(h)),h.material.uniforms.t2D.value=S,h.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,h.material.toneMapped=Lt.getTransfer(S.colorSpace)!==qt,S.matrixAutoUpdate===!0&&S.updateMatrix(),h.material.uniforms.uvTransform.value.copy(S.matrix),(p!==S||m!==S.version||g!==r.toneMapping)&&(h.material.needsUpdate=!0,p=S,m=S.version,g=r.toneMapping),h.layers.enableAll(),R.unshift(h,h.geometry,h.material,0,0,null))}function _(R,w){R.getRGB(cc,Fg(r)),n.buffers.color.setClear(cc.r,cc.g,cc.b,w,a)}return{getClearColor:function(){return c},setClearColor:function(R,w=1){c.set(R),u=w,_(c,u)},getClearAlpha:function(){return u},setClearAlpha:function(R){u=R,_(c,u)},render:E,addToRenderList:v}}function M1(r,e){const t=r.getParameter(r.MAX_VERTEX_ATTRIBS),n={},i=m(null);let s=i,a=!1;function c(A,k,J,ee,re){let le=!1;const Y=p(ee,J,k);s!==Y&&(s=Y,h(s.object)),le=g(A,ee,J,re),le&&x(A,ee,J,re),re!==null&&e.update(re,r.ELEMENT_ARRAY_BUFFER),(le||a)&&(a=!1,S(A,k,J,ee),re!==null&&r.bindBuffer(r.ELEMENT_ARRAY_BUFFER,e.get(re).buffer))}function u(){return r.createVertexArray()}function h(A){return r.bindVertexArray(A)}function f(A){return r.deleteVertexArray(A)}function p(A,k,J){const ee=J.wireframe===!0;let re=n[A.id];re===void 0&&(re={},n[A.id]=re);let le=re[k.id];le===void 0&&(le={},re[k.id]=le);let Y=le[ee];return Y===void 0&&(Y=m(u()),le[ee]=Y),Y}function m(A){const k=[],J=[],ee=[];for(let re=0;re<t;re++)k[re]=0,J[re]=0,ee[re]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:k,enabledAttributes:J,attributeDivisors:ee,object:A,attributes:{},index:null}}function g(A,k,J,ee){const re=s.attributes,le=k.attributes;let Y=0;const de=J.getAttributes();for(const ne in de)if(de[ne].location>=0){const Te=re[ne];let ze=le[ne];if(ze===void 0&&(ne==="instanceMatrix"&&A.instanceMatrix&&(ze=A.instanceMatrix),ne==="instanceColor"&&A.instanceColor&&(ze=A.instanceColor)),Te===void 0||Te.attribute!==ze||ze&&Te.data!==ze.data)return!0;Y++}return s.attributesNum!==Y||s.index!==ee}function x(A,k,J,ee){const re={},le=k.attributes;let Y=0;const de=J.getAttributes();for(const ne in de)if(de[ne].location>=0){let Te=le[ne];Te===void 0&&(ne==="instanceMatrix"&&A.instanceMatrix&&(Te=A.instanceMatrix),ne==="instanceColor"&&A.instanceColor&&(Te=A.instanceColor));const ze={};ze.attribute=Te,Te&&Te.data&&(ze.data=Te.data),re[ne]=ze,Y++}s.attributes=re,s.attributesNum=Y,s.index=ee}function E(){const A=s.newAttributes;for(let k=0,J=A.length;k<J;k++)A[k]=0}function v(A){_(A,0)}function _(A,k){const J=s.newAttributes,ee=s.enabledAttributes,re=s.attributeDivisors;J[A]=1,ee[A]===0&&(r.enableVertexAttribArray(A),ee[A]=1),re[A]!==k&&(r.vertexAttribDivisor(A,k),re[A]=k)}function R(){const A=s.newAttributes,k=s.enabledAttributes;for(let J=0,ee=k.length;J<ee;J++)k[J]!==A[J]&&(r.disableVertexAttribArray(J),k[J]=0)}function w(A,k,J,ee,re,le,Y){Y===!0?r.vertexAttribIPointer(A,k,J,re,le):r.vertexAttribPointer(A,k,J,ee,re,le)}function S(A,k,J,ee){E();const re=ee.attributes,le=J.getAttributes(),Y=k.defaultAttributeValues;for(const de in le){const ne=le[de];if(ne.location>=0){let ye=re[de];if(ye===void 0&&(de==="instanceMatrix"&&A.instanceMatrix&&(ye=A.instanceMatrix),de==="instanceColor"&&A.instanceColor&&(ye=A.instanceColor)),ye!==void 0){const Te=ye.normalized,ze=ye.itemSize,We=e.get(ye);if(We===void 0)continue;const xt=We.buffer,ue=We.type,me=We.bytesPerElement,De=ue===r.INT||ue===r.UNSIGNED_INT||ye.gpuType===ld;if(ye.isInterleavedBufferAttribute){const Se=ye.data,et=Se.stride,it=ye.offset;if(Se.isInstancedInterleavedBuffer){for(let Qe=0;Qe<ne.locationSize;Qe++)_(ne.location+Qe,Se.meshPerAttribute);A.isInstancedMesh!==!0&&ee._maxInstanceCount===void 0&&(ee._maxInstanceCount=Se.meshPerAttribute*Se.count)}else for(let Qe=0;Qe<ne.locationSize;Qe++)v(ne.location+Qe);r.bindBuffer(r.ARRAY_BUFFER,xt);for(let Qe=0;Qe<ne.locationSize;Qe++)w(ne.location+Qe,ze/ne.locationSize,ue,Te,et*me,(it+ze/ne.locationSize*Qe)*me,De)}else{if(ye.isInstancedBufferAttribute){for(let Se=0;Se<ne.locationSize;Se++)_(ne.location+Se,ye.meshPerAttribute);A.isInstancedMesh!==!0&&ee._maxInstanceCount===void 0&&(ee._maxInstanceCount=ye.meshPerAttribute*ye.count)}else for(let Se=0;Se<ne.locationSize;Se++)v(ne.location+Se);r.bindBuffer(r.ARRAY_BUFFER,xt);for(let Se=0;Se<ne.locationSize;Se++)w(ne.location+Se,ze/ne.locationSize,ue,Te,ze*me,ze/ne.locationSize*Se*me,De)}}else if(Y!==void 0){const Te=Y[de];if(Te!==void 0)switch(Te.length){case 2:r.vertexAttrib2fv(ne.location,Te);break;case 3:r.vertexAttrib3fv(ne.location,Te);break;case 4:r.vertexAttrib4fv(ne.location,Te);break;default:r.vertexAttrib1fv(ne.location,Te)}}}}R()}function z(){V();for(const A in n){const k=n[A];for(const J in k){const ee=k[J];for(const re in ee)f(ee[re].object),delete ee[re];delete k[J]}delete n[A]}}function O(A){if(n[A.id]===void 0)return;const k=n[A.id];for(const J in k){const ee=k[J];for(const re in ee)f(ee[re].object),delete ee[re];delete k[J]}delete n[A.id]}function N(A){for(const k in n){const J=n[k];if(J[A.id]===void 0)continue;const ee=J[A.id];for(const re in ee)f(ee[re].object),delete ee[re];delete J[A.id]}}function V(){D(),a=!0,s!==i&&(s=i,h(s.object))}function D(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:c,reset:V,resetDefaultState:D,dispose:z,releaseStatesOfGeometry:O,releaseStatesOfProgram:N,initAttributes:E,enableAttribute:v,disableUnusedAttributes:R}}function T1(r,e,t){let n;function i(h){n=h}function s(h,f){r.drawArrays(n,h,f),t.update(f,n,1)}function a(h,f,p){p!==0&&(r.drawArraysInstanced(n,h,f,p),t.update(f,n,p))}function c(h,f,p){if(p===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,h,0,f,0,p);let g=0;for(let x=0;x<p;x++)g+=f[x];t.update(g,n,1)}function u(h,f,p,m){if(p===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let x=0;x<h.length;x++)a(h[x],f[x],m[x]);else{g.multiDrawArraysInstancedWEBGL(n,h,0,f,0,m,0,p);let x=0;for(let E=0;E<p;E++)x+=f[E]*m[E];t.update(x,n,1)}}this.setMode=i,this.render=s,this.renderInstances=a,this.renderMultiDraw=c,this.renderMultiDrawInstances=u}function w1(r,e,t,n){let i;function s(){if(i!==void 0)return i;if(e.has("EXT_texture_filter_anisotropic")===!0){const N=e.get("EXT_texture_filter_anisotropic");i=r.getParameter(N.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function a(N){return!(N!==fi&&n.convert(N)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_FORMAT))}function c(N){const V=N===ia&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(N!==rr&&n.convert(N)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_TYPE)&&N!==Ei&&!V)}function u(N){if(N==="highp"){if(r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.HIGH_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.HIGH_FLOAT).precision>0)return"highp";N="mediump"}return N==="mediump"&&r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.MEDIUM_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let h=t.precision!==void 0?t.precision:"highp";const f=u(h);f!==h&&(console.warn("THREE.WebGLRenderer:",h,"not supported, using",f,"instead."),h=f);const p=t.logarithmicDepthBuffer===!0,m=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),g=r.getParameter(r.MAX_TEXTURE_IMAGE_UNITS),x=r.getParameter(r.MAX_VERTEX_TEXTURE_IMAGE_UNITS),E=r.getParameter(r.MAX_TEXTURE_SIZE),v=r.getParameter(r.MAX_CUBE_MAP_TEXTURE_SIZE),_=r.getParameter(r.MAX_VERTEX_ATTRIBS),R=r.getParameter(r.MAX_VERTEX_UNIFORM_VECTORS),w=r.getParameter(r.MAX_VARYING_VECTORS),S=r.getParameter(r.MAX_FRAGMENT_UNIFORM_VECTORS),z=x>0,O=r.getParameter(r.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:u,textureFormatReadable:a,textureTypeReadable:c,precision:h,logarithmicDepthBuffer:p,reverseDepthBuffer:m,maxTextures:g,maxVertexTextures:x,maxTextureSize:E,maxCubemapSize:v,maxAttributes:_,maxVertexUniforms:R,maxVaryings:w,maxFragmentUniforms:S,vertexTextures:z,maxSamples:O}}function A1(r){const e=this;let t=null,n=0,i=!1,s=!1;const a=new yr,c=new yt,u={value:null,needsUpdate:!1};this.uniform=u,this.numPlanes=0,this.numIntersection=0,this.init=function(p,m){const g=p.length!==0||m||n!==0||i;return i=m,n=p.length,g},this.beginShadows=function(){s=!0,f(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(p,m){t=f(p,m,0)},this.setState=function(p,m,g){const x=p.clippingPlanes,E=p.clipIntersection,v=p.clipShadows,_=r.get(p);if(!i||x===null||x.length===0||s&&!v)s?f(null):h();else{const R=s?0:n,w=R*4;let S=_.clippingState||null;u.value=S,S=f(x,m,w,g);for(let z=0;z!==w;++z)S[z]=t[z];_.clippingState=S,this.numIntersection=E?this.numPlanes:0,this.numPlanes+=R}};function h(){u.value!==t&&(u.value=t,u.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function f(p,m,g,x){const E=p!==null?p.length:0;let v=null;if(E!==0){if(v=u.value,x!==!0||v===null){const _=g+E*4,R=m.matrixWorldInverse;c.getNormalMatrix(R),(v===null||v.length<_)&&(v=new Float32Array(_));for(let w=0,S=g;w!==E;++w,S+=4)a.copy(p[w]).applyMatrix4(R,c),a.normal.toArray(v,S),v[S+3]=a.constant}u.value=v,u.needsUpdate=!0}return e.numPlanes=E,e.numIntersection=0,v}}function R1(r){let e=new WeakMap;function t(a,c){return c===Th?a.mapping=Qs:c===wh&&(a.mapping=Js),a}function n(a){if(a&&a.isTexture){const c=a.mapping;if(c===Th||c===wh)if(e.has(a)){const u=e.get(a).texture;return t(u,a.mapping)}else{const u=a.image;if(u&&u.height>0){const h=new kT(u.height);return h.fromEquirectangularTexture(r,a),e.set(a,h),a.addEventListener("dispose",i),t(h.texture,a.mapping)}else return null}}return a}function i(a){const c=a.target;c.removeEventListener("dispose",i);const u=e.get(c);u!==void 0&&(e.delete(c),u.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class bd extends Ng{constructor(e=-1,t=1,n=1,i=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2;let s=n-e,a=n+e,c=i+t,u=i-t;if(this.view!==null&&this.view.enabled){const h=(this.right-this.left)/this.view.fullWidth/this.zoom,f=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=h*this.view.offsetX,a=s+h*this.view.width,c-=f*this.view.offsetY,u=c-f*this.view.height}this.projectionMatrix.makeOrthographic(s,a,c,u,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Ws=4,em=[.125,.215,.35,.446,.526,.582],as=20,Wu=new bd,tm=new rt;let ju=null,Xu=0,qu=0,Yu=!1;const rs=(1+Math.sqrt(5))/2,ks=1/rs,nm=[new U(-rs,ks,0),new U(rs,ks,0),new U(-ks,0,rs),new U(ks,0,rs),new U(0,rs,-ks),new U(0,rs,ks),new U(-1,1,-1),new U(1,1,-1),new U(-1,1,1),new U(1,1,1)];class im{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){ju=this._renderer.getRenderTarget(),Xu=this._renderer.getActiveCubeFace(),qu=this._renderer.getActiveMipmapLevel(),Yu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,i,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=om(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=sm(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(ju,Xu,qu),this._renderer.xr.enabled=Yu,e.scissorTest=!1,lc(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Qs||e.mapping===Js?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),ju=this._renderer.getRenderTarget(),Xu=this._renderer.getActiveCubeFace(),qu=this._renderer.getActiveMipmapLevel(),Yu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ai,minFilter:ai,generateMipmaps:!1,type:ia,format:fi,colorSpace:jn,depthBuffer:!1},i=rm(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=rm(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=P1(s)),this._blurMaterial=C1(s,e,t)}return i}_compileMaterial(e){const t=new Pe(this._lodPlanes[0],e);this._renderer.compile(t,Wu)}_sceneToCubeUV(e,t,n,i){const c=new Gn(90,1,t,n),u=[1,-1,1,1,1,1],h=[1,1,1,-1,-1,-1],f=this._renderer,p=f.autoClear,m=f.toneMapping;f.getClearColor(tm),f.toneMapping=Mr,f.autoClear=!1;const g=new pi({name:"PMREM.Background",side:Zn,depthWrite:!1,depthTest:!1}),x=new Pe(new ln,g);let E=!1;const v=e.background;v?v.isColor&&(g.color.copy(v),e.background=null,E=!0):(g.color.copy(tm),E=!0);for(let _=0;_<6;_++){const R=_%3;R===0?(c.up.set(0,u[_],0),c.lookAt(h[_],0,0)):R===1?(c.up.set(0,0,u[_]),c.lookAt(0,h[_],0)):(c.up.set(0,u[_],0),c.lookAt(0,0,h[_]));const w=this._cubeSize;lc(i,R*w,_>2?w:0,w,w),f.setRenderTarget(i),E&&f.render(x,c),f.render(e,c)}x.geometry.dispose(),x.material.dispose(),f.toneMapping=m,f.autoClear=p,e.background=v}_textureToCubeUV(e,t){const n=this._renderer,i=e.mapping===Qs||e.mapping===Js;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=om()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=sm());const s=i?this._cubemapMaterial:this._equirectMaterial,a=new Pe(this._lodPlanes[0],s),c=s.uniforms;c.envMap.value=e;const u=this._cubeSize;lc(t,0,0,3*u,2*u),n.setRenderTarget(t),n.render(a,Wu)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const i=this._lodPlanes.length;for(let s=1;s<i;s++){const a=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),c=nm[(i-s-1)%nm.length];this._blur(e,s-1,s,a,c)}t.autoClear=n}_blur(e,t,n,i,s){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,i,"latitudinal",s),this._halfBlur(a,e,n,n,i,"longitudinal",s)}_halfBlur(e,t,n,i,s,a,c){const u=this._renderer,h=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const f=3,p=new Pe(this._lodPlanes[i],h),m=h.uniforms,g=this._sizeLods[n]-1,x=isFinite(s)?Math.PI/(2*g):2*Math.PI/(2*as-1),E=s/x,v=isFinite(s)?1+Math.floor(f*E):as;v>as&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${v} samples when the maximum is set to ${as}`);const _=[];let R=0;for(let N=0;N<as;++N){const V=N/E,D=Math.exp(-V*V/2);_.push(D),N===0?R+=D:N<v&&(R+=2*D)}for(let N=0;N<_.length;N++)_[N]=_[N]/R;m.envMap.value=e.texture,m.samples.value=v,m.weights.value=_,m.latitudinal.value=a==="latitudinal",c&&(m.poleAxis.value=c);const{_lodMax:w}=this;m.dTheta.value=x,m.mipInt.value=w-n;const S=this._sizeLods[i],z=3*S*(i>w-Ws?i-w+Ws:0),O=4*(this._cubeSize-S);lc(t,z,O,3*S,2*S),u.setRenderTarget(t),u.render(p,Wu)}}function P1(r){const e=[],t=[],n=[];let i=r;const s=r-Ws+1+em.length;for(let a=0;a<s;a++){const c=Math.pow(2,i);t.push(c);let u=1/c;a>r-Ws?u=em[a-r+Ws-1]:a===0&&(u=0),n.push(u);const h=1/(c-2),f=-h,p=1+h,m=[f,f,p,f,p,p,f,f,p,p,f,p],g=6,x=6,E=3,v=2,_=1,R=new Float32Array(E*x*g),w=new Float32Array(v*x*g),S=new Float32Array(_*x*g);for(let O=0;O<g;O++){const N=O%3*2/3-1,V=O>2?0:-1,D=[N,V,0,N+2/3,V,0,N+2/3,V+1,0,N,V,0,N+2/3,V+1,0,N,V+1,0];R.set(D,E*x*O),w.set(m,v*x*O);const A=[O,O,O,O,O,O];S.set(A,_*x*O)}const z=new yn;z.setAttribute("position",new hn(R,E)),z.setAttribute("uv",new hn(w,v)),z.setAttribute("faceIndex",new hn(S,_)),e.push(z),i>Ws&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function rm(r,e,t){const n=new us(r,e,t);return n.texture.mapping=kc,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function lc(r,e,t,n,i){r.viewport.set(e,t,n,i),r.scissor.set(e,t,n,i)}function C1(r,e,t){const n=new Float32Array(as),i=new U(0,1,0);return new Tr({name:"SphericalGaussianBlur",defines:{n:as,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${r}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:Sd(),fragmentShader:`

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
		`,blending:Er,depthTest:!1,depthWrite:!1})}function sm(){return new Tr({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Sd(),fragmentShader:`

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
		`,blending:Er,depthTest:!1,depthWrite:!1})}function om(){return new Tr({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Sd(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Er,depthTest:!1,depthWrite:!1})}function Sd(){return`

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
	`}function D1(r){let e=new WeakMap,t=null;function n(c){if(c&&c.isTexture){const u=c.mapping,h=u===Th||u===wh,f=u===Qs||u===Js;if(h||f){let p=e.get(c);const m=p!==void 0?p.texture.pmremVersion:0;if(c.isRenderTargetTexture&&c.pmremVersion!==m)return t===null&&(t=new im(r)),p=h?t.fromEquirectangular(c,p):t.fromCubemap(c,p),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),p.texture;if(p!==void 0)return p.texture;{const g=c.image;return h&&g&&g.height>0||f&&g&&i(g)?(t===null&&(t=new im(r)),p=h?t.fromEquirectangular(c):t.fromCubemap(c),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),c.addEventListener("dispose",s),p.texture):null}}}return c}function i(c){let u=0;const h=6;for(let f=0;f<h;f++)c[f]!==void 0&&u++;return u===h}function s(c){const u=c.target;u.removeEventListener("dispose",s);const h=e.get(u);h!==void 0&&(e.delete(u),h.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function I1(r){const e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=r.getExtension("WEBGL_depth_texture")||r.getExtension("MOZ_WEBGL_depth_texture")||r.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=r.getExtension("EXT_texture_filter_anisotropic")||r.getExtension("MOZ_EXT_texture_filter_anisotropic")||r.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=r.getExtension("WEBGL_compressed_texture_s3tc")||r.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=r.getExtension("WEBGL_compressed_texture_pvrtc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=r.getExtension(n)}return e[n]=i,i}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const i=t(n);return i===null&&jo("THREE.WebGLRenderer: "+n+" extension not supported."),i}}}function L1(r,e,t,n){const i={},s=new WeakMap;function a(p){const m=p.target;m.index!==null&&e.remove(m.index);for(const x in m.attributes)e.remove(m.attributes[x]);for(const x in m.morphAttributes){const E=m.morphAttributes[x];for(let v=0,_=E.length;v<_;v++)e.remove(E[v])}m.removeEventListener("dispose",a),delete i[m.id];const g=s.get(m);g&&(e.remove(g),s.delete(m)),n.releaseStatesOfGeometry(m),m.isInstancedBufferGeometry===!0&&delete m._maxInstanceCount,t.memory.geometries--}function c(p,m){return i[m.id]===!0||(m.addEventListener("dispose",a),i[m.id]=!0,t.memory.geometries++),m}function u(p){const m=p.attributes;for(const x in m)e.update(m[x],r.ARRAY_BUFFER);const g=p.morphAttributes;for(const x in g){const E=g[x];for(let v=0,_=E.length;v<_;v++)e.update(E[v],r.ARRAY_BUFFER)}}function h(p){const m=[],g=p.index,x=p.attributes.position;let E=0;if(g!==null){const R=g.array;E=g.version;for(let w=0,S=R.length;w<S;w+=3){const z=R[w+0],O=R[w+1],N=R[w+2];m.push(z,O,O,N,N,z)}}else if(x!==void 0){const R=x.array;E=x.version;for(let w=0,S=R.length/3-1;w<S;w+=3){const z=w+0,O=w+1,N=w+2;m.push(z,O,O,N,N,z)}}else return;const v=new(Rg(m)?Lg:Ig)(m,1);v.version=E;const _=s.get(p);_&&e.remove(_),s.set(p,v)}function f(p){const m=s.get(p);if(m){const g=p.index;g!==null&&m.version<g.version&&h(p)}else h(p);return s.get(p)}return{get:c,update:u,getWireframeAttribute:f}}function F1(r,e,t){let n;function i(m){n=m}let s,a;function c(m){s=m.type,a=m.bytesPerElement}function u(m,g){r.drawElements(n,g,s,m*a),t.update(g,n,1)}function h(m,g,x){x!==0&&(r.drawElementsInstanced(n,g,s,m*a,x),t.update(g,n,x))}function f(m,g,x){if(x===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,g,0,s,m,0,x);let v=0;for(let _=0;_<x;_++)v+=g[_];t.update(v,n,1)}function p(m,g,x,E){if(x===0)return;const v=e.get("WEBGL_multi_draw");if(v===null)for(let _=0;_<m.length;_++)h(m[_]/a,g[_],E[_]);else{v.multiDrawElementsInstancedWEBGL(n,g,0,s,m,0,E,0,x);let _=0;for(let R=0;R<x;R++)_+=g[R]*E[R];t.update(_,n,1)}}this.setMode=i,this.setIndex=c,this.render=u,this.renderInstances=h,this.renderMultiDraw=f,this.renderMultiDrawInstances=p}function N1(r){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,c){switch(t.calls++,a){case r.TRIANGLES:t.triangles+=c*(s/3);break;case r.LINES:t.lines+=c*(s/2);break;case r.LINE_STRIP:t.lines+=c*(s-1);break;case r.LINE_LOOP:t.lines+=c*s;break;case r.POINTS:t.points+=c*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function i(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}function O1(r,e,t){const n=new WeakMap,i=new Bt;function s(a,c,u){const h=a.morphTargetInfluences,f=c.morphAttributes.position||c.morphAttributes.normal||c.morphAttributes.color,p=f!==void 0?f.length:0;let m=n.get(c);if(m===void 0||m.count!==p){let A=function(){V.dispose(),n.delete(c),c.removeEventListener("dispose",A)};var g=A;m!==void 0&&m.texture.dispose();const x=c.morphAttributes.position!==void 0,E=c.morphAttributes.normal!==void 0,v=c.morphAttributes.color!==void 0,_=c.morphAttributes.position||[],R=c.morphAttributes.normal||[],w=c.morphAttributes.color||[];let S=0;x===!0&&(S=1),E===!0&&(S=2),v===!0&&(S=3);let z=c.attributes.position.count*S,O=1;z>e.maxTextureSize&&(O=Math.ceil(z/e.maxTextureSize),z=e.maxTextureSize);const N=new Float32Array(z*O*4*p),V=new Cg(N,z,O,p);V.type=Ei,V.needsUpdate=!0;const D=S*4;for(let k=0;k<p;k++){const J=_[k],ee=R[k],re=w[k],le=z*O*4*k;for(let Y=0;Y<J.count;Y++){const de=Y*D;x===!0&&(i.fromBufferAttribute(J,Y),N[le+de+0]=i.x,N[le+de+1]=i.y,N[le+de+2]=i.z,N[le+de+3]=0),E===!0&&(i.fromBufferAttribute(ee,Y),N[le+de+4]=i.x,N[le+de+5]=i.y,N[le+de+6]=i.z,N[le+de+7]=0),v===!0&&(i.fromBufferAttribute(re,Y),N[le+de+8]=i.x,N[le+de+9]=i.y,N[le+de+10]=i.z,N[le+de+11]=re.itemSize===4?i.w:1)}}m={count:p,texture:V,size:new ht(z,O)},n.set(c,m),c.addEventListener("dispose",A)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)u.getUniforms().setValue(r,"morphTexture",a.morphTexture,t);else{let x=0;for(let v=0;v<h.length;v++)x+=h[v];const E=c.morphTargetsRelative?1:1-x;u.getUniforms().setValue(r,"morphTargetBaseInfluence",E),u.getUniforms().setValue(r,"morphTargetInfluences",h)}u.getUniforms().setValue(r,"morphTargetsTexture",m.texture,t),u.getUniforms().setValue(r,"morphTargetsTextureSize",m.size)}return{update:s}}function U1(r,e,t,n){let i=new WeakMap;function s(u){const h=n.render.frame,f=u.geometry,p=e.get(u,f);if(i.get(p)!==h&&(e.update(p),i.set(p,h)),u.isInstancedMesh&&(u.hasEventListener("dispose",c)===!1&&u.addEventListener("dispose",c),i.get(u)!==h&&(t.update(u.instanceMatrix,r.ARRAY_BUFFER),u.instanceColor!==null&&t.update(u.instanceColor,r.ARRAY_BUFFER),i.set(u,h))),u.isSkinnedMesh){const m=u.skeleton;i.get(m)!==h&&(m.update(),i.set(m,h))}return p}function a(){i=new WeakMap}function c(u){const h=u.target;h.removeEventListener("dispose",c),t.remove(h.instanceMatrix),h.instanceColor!==null&&t.remove(h.instanceColor)}return{update:s,dispose:a}}class Bg extends wn{constructor(e,t,n,i,s,a,c,u,h,f=Ys){if(f!==Ys&&f!==no)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&f===Ys&&(n=ls),n===void 0&&f===no&&(n=to),super(null,i,s,a,c,u,f,n,h),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=c!==void 0?c:Wn,this.minFilter=u!==void 0?u:Wn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const kg=new wn,am=new Bg(1,1),zg=new Cg,Hg=new ET,Vg=new Og,cm=[],lm=[],um=new Float32Array(16),hm=new Float32Array(9),dm=new Float32Array(4);function uo(r,e,t){const n=r[0];if(n<=0||n>0)return r;const i=e*t;let s=cm[i];if(s===void 0&&(s=new Float32Array(i),cm[i]=s),e!==0){n.toArray(s,0);for(let a=1,c=0;a!==e;++a)c+=t,r[a].toArray(s,c)}return s}function xn(r,e){if(r.length!==e.length)return!1;for(let t=0,n=r.length;t<n;t++)if(r[t]!==e[t])return!1;return!0}function bn(r,e){for(let t=0,n=e.length;t<n;t++)r[t]=e[t]}function Hc(r,e){let t=lm[e];t===void 0&&(t=new Int32Array(e),lm[e]=t);for(let n=0;n!==e;++n)t[n]=r.allocateTextureUnit();return t}function B1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1f(this.addr,e),t[0]=e)}function k1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(xn(t,e))return;r.uniform2fv(this.addr,e),bn(t,e)}}function z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(r.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(xn(t,e))return;r.uniform3fv(this.addr,e),bn(t,e)}}function H1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(xn(t,e))return;r.uniform4fv(this.addr,e),bn(t,e)}}function V1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(xn(t,e))return;r.uniformMatrix2fv(this.addr,!1,e),bn(t,e)}else{if(xn(t,n))return;dm.set(n),r.uniformMatrix2fv(this.addr,!1,dm),bn(t,n)}}function G1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(xn(t,e))return;r.uniformMatrix3fv(this.addr,!1,e),bn(t,e)}else{if(xn(t,n))return;hm.set(n),r.uniformMatrix3fv(this.addr,!1,hm),bn(t,n)}}function W1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(xn(t,e))return;r.uniformMatrix4fv(this.addr,!1,e),bn(t,e)}else{if(xn(t,n))return;um.set(n),r.uniformMatrix4fv(this.addr,!1,um),bn(t,n)}}function j1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1i(this.addr,e),t[0]=e)}function X1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(xn(t,e))return;r.uniform2iv(this.addr,e),bn(t,e)}}function q1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(xn(t,e))return;r.uniform3iv(this.addr,e),bn(t,e)}}function Y1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(xn(t,e))return;r.uniform4iv(this.addr,e),bn(t,e)}}function K1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1ui(this.addr,e),t[0]=e)}function $1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(xn(t,e))return;r.uniform2uiv(this.addr,e),bn(t,e)}}function Z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(xn(t,e))return;r.uniform3uiv(this.addr,e),bn(t,e)}}function Q1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(xn(t,e))return;r.uniform4uiv(this.addr,e),bn(t,e)}}function J1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i);let s;this.type===r.SAMPLER_2D_SHADOW?(am.compareFunction=wg,s=am):s=kg,t.setTexture2D(e||s,i)}function eR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||Hg,i)}function tR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||Vg,i)}function nR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||zg,i)}function iR(r){switch(r){case 5126:return B1;case 35664:return k1;case 35665:return z1;case 35666:return H1;case 35674:return V1;case 35675:return G1;case 35676:return W1;case 5124:case 35670:return j1;case 35667:case 35671:return X1;case 35668:case 35672:return q1;case 35669:case 35673:return Y1;case 5125:return K1;case 36294:return $1;case 36295:return Z1;case 36296:return Q1;case 35678:case 36198:case 36298:case 36306:case 35682:return J1;case 35679:case 36299:case 36307:return eR;case 35680:case 36300:case 36308:case 36293:return tR;case 36289:case 36303:case 36311:case 36292:return nR}}function rR(r,e){r.uniform1fv(this.addr,e)}function sR(r,e){const t=uo(e,this.size,2);r.uniform2fv(this.addr,t)}function oR(r,e){const t=uo(e,this.size,3);r.uniform3fv(this.addr,t)}function aR(r,e){const t=uo(e,this.size,4);r.uniform4fv(this.addr,t)}function cR(r,e){const t=uo(e,this.size,4);r.uniformMatrix2fv(this.addr,!1,t)}function lR(r,e){const t=uo(e,this.size,9);r.uniformMatrix3fv(this.addr,!1,t)}function uR(r,e){const t=uo(e,this.size,16);r.uniformMatrix4fv(this.addr,!1,t)}function hR(r,e){r.uniform1iv(this.addr,e)}function dR(r,e){r.uniform2iv(this.addr,e)}function fR(r,e){r.uniform3iv(this.addr,e)}function pR(r,e){r.uniform4iv(this.addr,e)}function mR(r,e){r.uniform1uiv(this.addr,e)}function gR(r,e){r.uniform2uiv(this.addr,e)}function _R(r,e){r.uniform3uiv(this.addr,e)}function vR(r,e){r.uniform4uiv(this.addr,e)}function yR(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);xn(n,s)||(r.uniform1iv(this.addr,s),bn(n,s));for(let a=0;a!==i;++a)t.setTexture2D(e[a]||kg,s[a])}function xR(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);xn(n,s)||(r.uniform1iv(this.addr,s),bn(n,s));for(let a=0;a!==i;++a)t.setTexture3D(e[a]||Hg,s[a])}function bR(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);xn(n,s)||(r.uniform1iv(this.addr,s),bn(n,s));for(let a=0;a!==i;++a)t.setTextureCube(e[a]||Vg,s[a])}function SR(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);xn(n,s)||(r.uniform1iv(this.addr,s),bn(n,s));for(let a=0;a!==i;++a)t.setTexture2DArray(e[a]||zg,s[a])}function ER(r){switch(r){case 5126:return rR;case 35664:return sR;case 35665:return oR;case 35666:return aR;case 35674:return cR;case 35675:return lR;case 35676:return uR;case 5124:case 35670:return hR;case 35667:case 35671:return dR;case 35668:case 35672:return fR;case 35669:case 35673:return pR;case 5125:return mR;case 36294:return gR;case 36295:return _R;case 36296:return vR;case 35678:case 36198:case 36298:case 36306:case 35682:return yR;case 35679:case 36299:case 36307:return xR;case 35680:case 36300:case 36308:case 36293:return bR;case 36289:case 36303:case 36311:case 36292:return SR}}class MR{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=iR(t.type)}}class TR{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=ER(t.type)}}class wR{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const i=this.seq;for(let s=0,a=i.length;s!==a;++s){const c=i[s];c.setValue(e,t[c.id],n)}}}const Ku=/(\w+)(\])?(\[|\.)?/g;function fm(r,e){r.seq.push(e),r.map[e.id]=e}function AR(r,e,t){const n=r.name,i=n.length;for(Ku.lastIndex=0;;){const s=Ku.exec(n),a=Ku.lastIndex;let c=s[1];const u=s[2]==="]",h=s[3];if(u&&(c=c|0),h===void 0||h==="["&&a+2===i){fm(t,h===void 0?new MR(c,r,e):new TR(c,r,e));break}else{let p=t.map[c];p===void 0&&(p=new wR(c),fm(t,p)),t=p}}}class Cc{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let i=0;i<n;++i){const s=e.getActiveUniform(t,i),a=e.getUniformLocation(t,s.name);AR(s,a,this)}}setValue(e,t,n,i){const s=this.map[t];s!==void 0&&s.setValue(e,n,i)}setOptional(e,t,n){const i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let s=0,a=t.length;s!==a;++s){const c=t[s],u=n[c.id];u.needsUpdate!==!1&&c.setValue(e,u.value,i)}}static seqWithValue(e,t){const n=[];for(let i=0,s=e.length;i!==s;++i){const a=e[i];a.id in t&&n.push(a)}return n}}function pm(r,e,t){const n=r.createShader(e);return r.shaderSource(n,t),r.compileShader(n),n}const RR=37297;let PR=0;function CR(r,e){const t=r.split(`
`),n=[],i=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let a=i;a<s;a++){const c=a+1;n.push(`${c===e?">":" "} ${c}: ${t[a]}`)}return n.join(`
`)}const mm=new yt;function DR(r){Lt._getMatrix(mm,Lt.workingColorSpace,r);const e=`mat3( ${mm.elements.map(t=>t.toFixed(4))} )`;switch(Lt.getTransfer(r)){case zc:return[e,"LinearTransferOETF"];case qt:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",r),[e,"LinearTransferOETF"]}}function gm(r,e,t){const n=r.getShaderParameter(e,r.COMPILE_STATUS),i=r.getShaderInfoLog(e).trim();if(n&&i==="")return"";const s=/ERROR: 0:(\d+)/.exec(i);if(s){const a=parseInt(s[1]);return t.toUpperCase()+`

`+i+`

`+CR(r.getShaderSource(e),a)}else return i}function IR(r,e){const t=DR(e);return[`vec4 ${r}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function LR(r,e){let t;switch(e){case IM:t="Linear";break;case LM:t="Reinhard";break;case FM:t="Cineon";break;case dg:t="ACESFilmic";break;case OM:t="AgX";break;case UM:t="Neutral";break;case NM:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+r+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const uc=new U;function FR(){Lt.getLuminanceCoefficients(uc);const r=uc.x.toFixed(4),e=uc.y.toFixed(4),t=uc.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${r}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function NR(r){return[r.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",r.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Xo).join(`
`)}function OR(r){const e=[];for(const t in r){const n=r[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function UR(r,e){const t={},n=r.getProgramParameter(e,r.ACTIVE_ATTRIBUTES);for(let i=0;i<n;i++){const s=r.getActiveAttrib(e,i),a=s.name;let c=1;s.type===r.FLOAT_MAT2&&(c=2),s.type===r.FLOAT_MAT3&&(c=3),s.type===r.FLOAT_MAT4&&(c=4),t[a]={type:s.type,location:r.getAttribLocation(e,a),locationSize:c}}return t}function Xo(r){return r!==""}function _m(r,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return r.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function vm(r,e){return r.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const BR=/^[ \t]*#include +<([\w\d./]+)>/gm;function td(r){return r.replace(BR,zR)}const kR=new Map;function zR(r,e){let t=Et[e];if(t===void 0){const n=kR.get(e);if(n!==void 0)t=Et[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return td(t)}const HR=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function ym(r){return r.replace(HR,VR)}function VR(r,e,t,n){let i="";for(let s=parseInt(e);s<parseInt(t);s++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return i}function xm(r){let e=`precision ${r.precision} float;
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
#define LOW_PRECISION`),e}function GR(r){let e="SHADOWMAP_TYPE_BASIC";return r.shadowMapType===ug?e="SHADOWMAP_TYPE_PCF":r.shadowMapType===hM?e="SHADOWMAP_TYPE_PCF_SOFT":r.shadowMapType===Zi&&(e="SHADOWMAP_TYPE_VSM"),e}function WR(r){let e="ENVMAP_TYPE_CUBE";if(r.envMap)switch(r.envMapMode){case Qs:case Js:e="ENVMAP_TYPE_CUBE";break;case kc:e="ENVMAP_TYPE_CUBE_UV";break}return e}function jR(r){let e="ENVMAP_MODE_REFLECTION";if(r.envMap)switch(r.envMapMode){case Js:e="ENVMAP_MODE_REFRACTION";break}return e}function XR(r){let e="ENVMAP_BLENDING_NONE";if(r.envMap)switch(r.combine){case hg:e="ENVMAP_BLENDING_MULTIPLY";break;case CM:e="ENVMAP_BLENDING_MIX";break;case DM:e="ENVMAP_BLENDING_ADD";break}return e}function qR(r){const e=r.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function YR(r,e,t,n){const i=r.getContext(),s=t.defines;let a=t.vertexShader,c=t.fragmentShader;const u=GR(t),h=WR(t),f=jR(t),p=XR(t),m=qR(t),g=NR(t),x=OR(s),E=i.createProgram();let v,_,R=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(v=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(Xo).join(`
`),v.length>0&&(v+=`
`),_=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(Xo).join(`
`),_.length>0&&(_+=`
`)):(v=[xm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+f:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Xo).join(`
`),_=[xm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.envMap?"#define "+f:"",t.envMap?"#define "+p:"",m?"#define CUBEUV_TEXEL_WIDTH "+m.texelWidth:"",m?"#define CUBEUV_TEXEL_HEIGHT "+m.texelHeight:"",m?"#define CUBEUV_MAX_MIP "+m.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Mr?"#define TONE_MAPPING":"",t.toneMapping!==Mr?Et.tonemapping_pars_fragment:"",t.toneMapping!==Mr?LR("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",Et.colorspace_pars_fragment,IR("linearToOutputTexel",t.outputColorSpace),FR(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Xo).join(`
`)),a=td(a),a=_m(a,t),a=vm(a,t),c=td(c),c=_m(c,t),c=vm(c,t),a=ym(a),c=ym(c),t.isRawShaderMaterial!==!0&&(R=`#version 300 es
`,v=[g,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+v,_=["#define varying in",t.glslVersion===Ip?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Ip?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);const w=R+v+a,S=R+_+c,z=pm(i,i.VERTEX_SHADER,w),O=pm(i,i.FRAGMENT_SHADER,S);i.attachShader(E,z),i.attachShader(E,O),t.index0AttributeName!==void 0?i.bindAttribLocation(E,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(E,0,"position"),i.linkProgram(E);function N(k){if(r.debug.checkShaderErrors){const J=i.getProgramInfoLog(E).trim(),ee=i.getShaderInfoLog(z).trim(),re=i.getShaderInfoLog(O).trim();let le=!0,Y=!0;if(i.getProgramParameter(E,i.LINK_STATUS)===!1)if(le=!1,typeof r.debug.onShaderError=="function")r.debug.onShaderError(i,E,z,O);else{const de=gm(i,z,"vertex"),ne=gm(i,O,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(E,i.VALIDATE_STATUS)+`

Material Name: `+k.name+`
Material Type: `+k.type+`

Program Info Log: `+J+`
`+de+`
`+ne)}else J!==""?console.warn("THREE.WebGLProgram: Program Info Log:",J):(ee===""||re==="")&&(Y=!1);Y&&(k.diagnostics={runnable:le,programLog:J,vertexShader:{log:ee,prefix:v},fragmentShader:{log:re,prefix:_}})}i.deleteShader(z),i.deleteShader(O),V=new Cc(i,E),D=UR(i,E)}let V;this.getUniforms=function(){return V===void 0&&N(this),V};let D;this.getAttributes=function(){return D===void 0&&N(this),D};let A=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return A===!1&&(A=i.getProgramParameter(E,RR)),A},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(E),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=PR++,this.cacheKey=e,this.usedTimes=1,this.program=E,this.vertexShader=z,this.fragmentShader=O,this}let KR=0;class $R{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(i)===!1&&(a.add(i),i.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new ZR(e),t.set(e,n)),n}}class ZR{constructor(e){this.id=KR++,this.code=e,this.usedTimes=0}}function QR(r,e,t,n,i,s,a){const c=new yd,u=new $R,h=new Set,f=[],p=i.logarithmicDepthBuffer,m=i.vertexTextures;let g=i.precision;const x={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function E(D){return h.add(D),D===0?"uv":`uv${D}`}function v(D,A,k,J,ee){const re=J.fog,le=ee.geometry,Y=D.isMeshStandardMaterial?J.environment:null,de=(D.isMeshStandardMaterial?t:e).get(D.envMap||Y),ne=de&&de.mapping===kc?de.image.height:null,ye=x[D.type];D.precision!==null&&(g=i.getMaxPrecision(D.precision),g!==D.precision&&console.warn("THREE.WebGLProgram.getParameters:",D.precision,"not supported, using",g,"instead."));const Te=le.morphAttributes.position||le.morphAttributes.normal||le.morphAttributes.color,ze=Te!==void 0?Te.length:0;let We=0;le.morphAttributes.position!==void 0&&(We=1),le.morphAttributes.normal!==void 0&&(We=2),le.morphAttributes.color!==void 0&&(We=3);let xt,ue,me,De;if(ye){const _e=Ci[ye];xt=_e.vertexShader,ue=_e.fragmentShader}else xt=D.vertexShader,ue=D.fragmentShader,u.update(D),me=u.getVertexShaderID(D),De=u.getFragmentShaderID(D);const Se=r.getRenderTarget(),et=r.state.buffers.depth.getReversed(),it=ee.isInstancedMesh===!0,Qe=ee.isBatchedMesh===!0,fe=!!D.map,Me=!!D.matcap,Fe=!!de,H=!!D.aoMap,nt=!!D.lightMap,Je=!!D.bumpMap,$e=!!D.normalMap,Oe=!!D.displacementMap,at=!!D.emissiveMap,Be=!!D.metalnessMap,L=!!D.roughnessMap,T=D.anisotropy>0,$=D.clearcoat>0,he=D.dispersion>0,ge=D.iridescence>0,ce=D.sheen>0,Ce=D.transmission>0,we=T&&!!D.anisotropyMap,ke=$&&!!D.clearcoatMap,Tt=$&&!!D.clearcoatNormalMap,be=$&&!!D.clearcoatRoughnessMap,Ue=ge&&!!D.iridescenceMap,Ge=ge&&!!D.iridescenceThicknessMap,st=ce&&!!D.sheenColorMap,Ve=ce&&!!D.sheenRoughnessMap,bt=!!D.specularMap,mt=!!D.specularColorMap,Ft=!!D.specularIntensityMap,X=Ce&&!!D.transmissionMap,Re=Ce&&!!D.thicknessMap,ae=!!D.gradientMap,pe=!!D.alphaMap,F=D.alphaTest>0,W=!!D.alphaHash,ie=!!D.extensions;let ve=Mr;D.toneMapped&&(Se===null||Se.isXRRenderTarget===!0)&&(ve=r.toneMapping);const je={shaderID:ye,shaderType:D.type,shaderName:D.name,vertexShader:xt,fragmentShader:ue,defines:D.defines,customVertexShaderID:me,customFragmentShaderID:De,isRawShaderMaterial:D.isRawShaderMaterial===!0,glslVersion:D.glslVersion,precision:g,batching:Qe,batchingColor:Qe&&ee._colorsTexture!==null,instancing:it,instancingColor:it&&ee.instanceColor!==null,instancingMorph:it&&ee.morphTexture!==null,supportsVertexTextures:m,outputColorSpace:Se===null?r.outputColorSpace:Se.isXRRenderTarget===!0?Se.texture.colorSpace:jn,alphaToCoverage:!!D.alphaToCoverage,map:fe,matcap:Me,envMap:Fe,envMapMode:Fe&&de.mapping,envMapCubeUVHeight:ne,aoMap:H,lightMap:nt,bumpMap:Je,normalMap:$e,displacementMap:m&&Oe,emissiveMap:at,normalMapObjectSpace:$e&&D.normalMapType===jM,normalMapTangentSpace:$e&&D.normalMapType===Tg,metalnessMap:Be,roughnessMap:L,anisotropy:T,anisotropyMap:we,clearcoat:$,clearcoatMap:ke,clearcoatNormalMap:Tt,clearcoatRoughnessMap:be,dispersion:he,iridescence:ge,iridescenceMap:Ue,iridescenceThicknessMap:Ge,sheen:ce,sheenColorMap:st,sheenRoughnessMap:Ve,specularMap:bt,specularColorMap:mt,specularIntensityMap:Ft,transmission:Ce,transmissionMap:X,thicknessMap:Re,gradientMap:ae,opaque:D.transparent===!1&&D.blending===qs&&D.alphaToCoverage===!1,alphaMap:pe,alphaTest:F,alphaHash:W,combine:D.combine,mapUv:fe&&E(D.map.channel),aoMapUv:H&&E(D.aoMap.channel),lightMapUv:nt&&E(D.lightMap.channel),bumpMapUv:Je&&E(D.bumpMap.channel),normalMapUv:$e&&E(D.normalMap.channel),displacementMapUv:Oe&&E(D.displacementMap.channel),emissiveMapUv:at&&E(D.emissiveMap.channel),metalnessMapUv:Be&&E(D.metalnessMap.channel),roughnessMapUv:L&&E(D.roughnessMap.channel),anisotropyMapUv:we&&E(D.anisotropyMap.channel),clearcoatMapUv:ke&&E(D.clearcoatMap.channel),clearcoatNormalMapUv:Tt&&E(D.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:be&&E(D.clearcoatRoughnessMap.channel),iridescenceMapUv:Ue&&E(D.iridescenceMap.channel),iridescenceThicknessMapUv:Ge&&E(D.iridescenceThicknessMap.channel),sheenColorMapUv:st&&E(D.sheenColorMap.channel),sheenRoughnessMapUv:Ve&&E(D.sheenRoughnessMap.channel),specularMapUv:bt&&E(D.specularMap.channel),specularColorMapUv:mt&&E(D.specularColorMap.channel),specularIntensityMapUv:Ft&&E(D.specularIntensityMap.channel),transmissionMapUv:X&&E(D.transmissionMap.channel),thicknessMapUv:Re&&E(D.thicknessMap.channel),alphaMapUv:pe&&E(D.alphaMap.channel),vertexTangents:!!le.attributes.tangent&&($e||T),vertexColors:D.vertexColors,vertexAlphas:D.vertexColors===!0&&!!le.attributes.color&&le.attributes.color.itemSize===4,pointsUvs:ee.isPoints===!0&&!!le.attributes.uv&&(fe||pe),fog:!!re,useFog:D.fog===!0,fogExp2:!!re&&re.isFogExp2,flatShading:D.flatShading===!0,sizeAttenuation:D.sizeAttenuation===!0,logarithmicDepthBuffer:p,reverseDepthBuffer:et,skinning:ee.isSkinnedMesh===!0,morphTargets:le.morphAttributes.position!==void 0,morphNormals:le.morphAttributes.normal!==void 0,morphColors:le.morphAttributes.color!==void 0,morphTargetsCount:ze,morphTextureStride:We,numDirLights:A.directional.length,numPointLights:A.point.length,numSpotLights:A.spot.length,numSpotLightMaps:A.spotLightMap.length,numRectAreaLights:A.rectArea.length,numHemiLights:A.hemi.length,numDirLightShadows:A.directionalShadowMap.length,numPointLightShadows:A.pointShadowMap.length,numSpotLightShadows:A.spotShadowMap.length,numSpotLightShadowsWithMaps:A.numSpotLightShadowsWithMaps,numLightProbes:A.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:D.dithering,shadowMapEnabled:r.shadowMap.enabled&&k.length>0,shadowMapType:r.shadowMap.type,toneMapping:ve,decodeVideoTexture:fe&&D.map.isVideoTexture===!0&&Lt.getTransfer(D.map.colorSpace)===qt,decodeVideoTextureEmissive:at&&D.emissiveMap.isVideoTexture===!0&&Lt.getTransfer(D.emissiveMap.colorSpace)===qt,premultipliedAlpha:D.premultipliedAlpha,doubleSided:D.side===$n,flipSided:D.side===Zn,useDepthPacking:D.depthPacking>=0,depthPacking:D.depthPacking||0,index0AttributeName:D.index0AttributeName,extensionClipCullDistance:ie&&D.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(ie&&D.extensions.multiDraw===!0||Qe)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:D.customProgramCacheKey()};return je.vertexUv1s=h.has(1),je.vertexUv2s=h.has(2),je.vertexUv3s=h.has(3),h.clear(),je}function _(D){const A=[];if(D.shaderID?A.push(D.shaderID):(A.push(D.customVertexShaderID),A.push(D.customFragmentShaderID)),D.defines!==void 0)for(const k in D.defines)A.push(k),A.push(D.defines[k]);return D.isRawShaderMaterial===!1&&(R(A,D),w(A,D),A.push(r.outputColorSpace)),A.push(D.customProgramCacheKey),A.join()}function R(D,A){D.push(A.precision),D.push(A.outputColorSpace),D.push(A.envMapMode),D.push(A.envMapCubeUVHeight),D.push(A.mapUv),D.push(A.alphaMapUv),D.push(A.lightMapUv),D.push(A.aoMapUv),D.push(A.bumpMapUv),D.push(A.normalMapUv),D.push(A.displacementMapUv),D.push(A.emissiveMapUv),D.push(A.metalnessMapUv),D.push(A.roughnessMapUv),D.push(A.anisotropyMapUv),D.push(A.clearcoatMapUv),D.push(A.clearcoatNormalMapUv),D.push(A.clearcoatRoughnessMapUv),D.push(A.iridescenceMapUv),D.push(A.iridescenceThicknessMapUv),D.push(A.sheenColorMapUv),D.push(A.sheenRoughnessMapUv),D.push(A.specularMapUv),D.push(A.specularColorMapUv),D.push(A.specularIntensityMapUv),D.push(A.transmissionMapUv),D.push(A.thicknessMapUv),D.push(A.combine),D.push(A.fogExp2),D.push(A.sizeAttenuation),D.push(A.morphTargetsCount),D.push(A.morphAttributeCount),D.push(A.numDirLights),D.push(A.numPointLights),D.push(A.numSpotLights),D.push(A.numSpotLightMaps),D.push(A.numHemiLights),D.push(A.numRectAreaLights),D.push(A.numDirLightShadows),D.push(A.numPointLightShadows),D.push(A.numSpotLightShadows),D.push(A.numSpotLightShadowsWithMaps),D.push(A.numLightProbes),D.push(A.shadowMapType),D.push(A.toneMapping),D.push(A.numClippingPlanes),D.push(A.numClipIntersection),D.push(A.depthPacking)}function w(D,A){c.disableAll(),A.supportsVertexTextures&&c.enable(0),A.instancing&&c.enable(1),A.instancingColor&&c.enable(2),A.instancingMorph&&c.enable(3),A.matcap&&c.enable(4),A.envMap&&c.enable(5),A.normalMapObjectSpace&&c.enable(6),A.normalMapTangentSpace&&c.enable(7),A.clearcoat&&c.enable(8),A.iridescence&&c.enable(9),A.alphaTest&&c.enable(10),A.vertexColors&&c.enable(11),A.vertexAlphas&&c.enable(12),A.vertexUv1s&&c.enable(13),A.vertexUv2s&&c.enable(14),A.vertexUv3s&&c.enable(15),A.vertexTangents&&c.enable(16),A.anisotropy&&c.enable(17),A.alphaHash&&c.enable(18),A.batching&&c.enable(19),A.dispersion&&c.enable(20),A.batchingColor&&c.enable(21),D.push(c.mask),c.disableAll(),A.fog&&c.enable(0),A.useFog&&c.enable(1),A.flatShading&&c.enable(2),A.logarithmicDepthBuffer&&c.enable(3),A.reverseDepthBuffer&&c.enable(4),A.skinning&&c.enable(5),A.morphTargets&&c.enable(6),A.morphNormals&&c.enable(7),A.morphColors&&c.enable(8),A.premultipliedAlpha&&c.enable(9),A.shadowMapEnabled&&c.enable(10),A.doubleSided&&c.enable(11),A.flipSided&&c.enable(12),A.useDepthPacking&&c.enable(13),A.dithering&&c.enable(14),A.transmission&&c.enable(15),A.sheen&&c.enable(16),A.opaque&&c.enable(17),A.pointsUvs&&c.enable(18),A.decodeVideoTexture&&c.enable(19),A.decodeVideoTextureEmissive&&c.enable(20),A.alphaToCoverage&&c.enable(21),D.push(c.mask)}function S(D){const A=x[D.type];let k;if(A){const J=Ci[A];k=NT.clone(J.uniforms)}else k=D.uniforms;return k}function z(D,A){let k;for(let J=0,ee=f.length;J<ee;J++){const re=f[J];if(re.cacheKey===A){k=re,++k.usedTimes;break}}return k===void 0&&(k=new YR(r,A,D,s),f.push(k)),k}function O(D){if(--D.usedTimes===0){const A=f.indexOf(D);f[A]=f[f.length-1],f.pop(),D.destroy()}}function N(D){u.remove(D)}function V(){u.dispose()}return{getParameters:v,getProgramCacheKey:_,getUniforms:S,acquireProgram:z,releaseProgram:O,releaseShaderCache:N,programs:f,dispose:V}}function JR(){let r=new WeakMap;function e(a){return r.has(a)}function t(a){let c=r.get(a);return c===void 0&&(c={},r.set(a,c)),c}function n(a){r.delete(a)}function i(a,c,u){r.get(a)[c]=u}function s(){r=new WeakMap}return{has:e,get:t,remove:n,update:i,dispose:s}}function eP(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.material.id!==e.material.id?r.material.id-e.material.id:r.z!==e.z?r.z-e.z:r.id-e.id}function bm(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.z!==e.z?e.z-r.z:r.id-e.id}function Sm(){const r=[];let e=0;const t=[],n=[],i=[];function s(){e=0,t.length=0,n.length=0,i.length=0}function a(p,m,g,x,E,v){let _=r[e];return _===void 0?(_={id:p.id,object:p,geometry:m,material:g,groupOrder:x,renderOrder:p.renderOrder,z:E,group:v},r[e]=_):(_.id=p.id,_.object=p,_.geometry=m,_.material=g,_.groupOrder=x,_.renderOrder=p.renderOrder,_.z=E,_.group=v),e++,_}function c(p,m,g,x,E,v){const _=a(p,m,g,x,E,v);g.transmission>0?n.push(_):g.transparent===!0?i.push(_):t.push(_)}function u(p,m,g,x,E,v){const _=a(p,m,g,x,E,v);g.transmission>0?n.unshift(_):g.transparent===!0?i.unshift(_):t.unshift(_)}function h(p,m){t.length>1&&t.sort(p||eP),n.length>1&&n.sort(m||bm),i.length>1&&i.sort(m||bm)}function f(){for(let p=e,m=r.length;p<m;p++){const g=r[p];if(g.id===null)break;g.id=null,g.object=null,g.geometry=null,g.material=null,g.group=null}}return{opaque:t,transmissive:n,transparent:i,init:s,push:c,unshift:u,finish:f,sort:h}}function tP(){let r=new WeakMap;function e(n,i){const s=r.get(n);let a;return s===void 0?(a=new Sm,r.set(n,[a])):i>=s.length?(a=new Sm,s.push(a)):a=s[i],a}function t(){r=new WeakMap}return{get:e,dispose:t}}function nP(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new U,color:new rt};break;case"SpotLight":t={position:new U,direction:new U,color:new rt,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new U,color:new rt,distance:0,decay:0};break;case"HemisphereLight":t={direction:new U,skyColor:new rt,groundColor:new rt};break;case"RectAreaLight":t={color:new rt,position:new U,halfWidth:new U,halfHeight:new U};break}return r[e.id]=t,t}}}function iP(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ht};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ht};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ht,shadowCameraNear:1,shadowCameraFar:1e3};break}return r[e.id]=t,t}}}let rP=0;function sP(r,e){return(e.castShadow?2:0)-(r.castShadow?2:0)+(e.map?1:0)-(r.map?1:0)}function oP(r){const e=new nP,t=iP(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let h=0;h<9;h++)n.probe.push(new U);const i=new U,s=new pt,a=new pt;function c(h){let f=0,p=0,m=0;for(let D=0;D<9;D++)n.probe[D].set(0,0,0);let g=0,x=0,E=0,v=0,_=0,R=0,w=0,S=0,z=0,O=0,N=0;h.sort(sP);for(let D=0,A=h.length;D<A;D++){const k=h[D],J=k.color,ee=k.intensity,re=k.distance,le=k.shadow&&k.shadow.map?k.shadow.map.texture:null;if(k.isAmbientLight)f+=J.r*ee,p+=J.g*ee,m+=J.b*ee;else if(k.isLightProbe){for(let Y=0;Y<9;Y++)n.probe[Y].addScaledVector(k.sh.coefficients[Y],ee);N++}else if(k.isDirectionalLight){const Y=e.get(k);if(Y.color.copy(k.color).multiplyScalar(k.intensity),k.castShadow){const de=k.shadow,ne=t.get(k);ne.shadowIntensity=de.intensity,ne.shadowBias=de.bias,ne.shadowNormalBias=de.normalBias,ne.shadowRadius=de.radius,ne.shadowMapSize=de.mapSize,n.directionalShadow[g]=ne,n.directionalShadowMap[g]=le,n.directionalShadowMatrix[g]=k.shadow.matrix,R++}n.directional[g]=Y,g++}else if(k.isSpotLight){const Y=e.get(k);Y.position.setFromMatrixPosition(k.matrixWorld),Y.color.copy(J).multiplyScalar(ee),Y.distance=re,Y.coneCos=Math.cos(k.angle),Y.penumbraCos=Math.cos(k.angle*(1-k.penumbra)),Y.decay=k.decay,n.spot[E]=Y;const de=k.shadow;if(k.map&&(n.spotLightMap[z]=k.map,z++,de.updateMatrices(k),k.castShadow&&O++),n.spotLightMatrix[E]=de.matrix,k.castShadow){const ne=t.get(k);ne.shadowIntensity=de.intensity,ne.shadowBias=de.bias,ne.shadowNormalBias=de.normalBias,ne.shadowRadius=de.radius,ne.shadowMapSize=de.mapSize,n.spotShadow[E]=ne,n.spotShadowMap[E]=le,S++}E++}else if(k.isRectAreaLight){const Y=e.get(k);Y.color.copy(J).multiplyScalar(ee),Y.halfWidth.set(k.width*.5,0,0),Y.halfHeight.set(0,k.height*.5,0),n.rectArea[v]=Y,v++}else if(k.isPointLight){const Y=e.get(k);if(Y.color.copy(k.color).multiplyScalar(k.intensity),Y.distance=k.distance,Y.decay=k.decay,k.castShadow){const de=k.shadow,ne=t.get(k);ne.shadowIntensity=de.intensity,ne.shadowBias=de.bias,ne.shadowNormalBias=de.normalBias,ne.shadowRadius=de.radius,ne.shadowMapSize=de.mapSize,ne.shadowCameraNear=de.camera.near,ne.shadowCameraFar=de.camera.far,n.pointShadow[x]=ne,n.pointShadowMap[x]=le,n.pointShadowMatrix[x]=k.shadow.matrix,w++}n.point[x]=Y,x++}else if(k.isHemisphereLight){const Y=e.get(k);Y.skyColor.copy(k.color).multiplyScalar(ee),Y.groundColor.copy(k.groundColor).multiplyScalar(ee),n.hemi[_]=Y,_++}}v>0&&(r.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Le.LTC_FLOAT_1,n.rectAreaLTC2=Le.LTC_FLOAT_2):(n.rectAreaLTC1=Le.LTC_HALF_1,n.rectAreaLTC2=Le.LTC_HALF_2)),n.ambient[0]=f,n.ambient[1]=p,n.ambient[2]=m;const V=n.hash;(V.directionalLength!==g||V.pointLength!==x||V.spotLength!==E||V.rectAreaLength!==v||V.hemiLength!==_||V.numDirectionalShadows!==R||V.numPointShadows!==w||V.numSpotShadows!==S||V.numSpotMaps!==z||V.numLightProbes!==N)&&(n.directional.length=g,n.spot.length=E,n.rectArea.length=v,n.point.length=x,n.hemi.length=_,n.directionalShadow.length=R,n.directionalShadowMap.length=R,n.pointShadow.length=w,n.pointShadowMap.length=w,n.spotShadow.length=S,n.spotShadowMap.length=S,n.directionalShadowMatrix.length=R,n.pointShadowMatrix.length=w,n.spotLightMatrix.length=S+z-O,n.spotLightMap.length=z,n.numSpotLightShadowsWithMaps=O,n.numLightProbes=N,V.directionalLength=g,V.pointLength=x,V.spotLength=E,V.rectAreaLength=v,V.hemiLength=_,V.numDirectionalShadows=R,V.numPointShadows=w,V.numSpotShadows=S,V.numSpotMaps=z,V.numLightProbes=N,n.version=rP++)}function u(h,f){let p=0,m=0,g=0,x=0,E=0;const v=f.matrixWorldInverse;for(let _=0,R=h.length;_<R;_++){const w=h[_];if(w.isDirectionalLight){const S=n.directional[p];S.direction.setFromMatrixPosition(w.matrixWorld),i.setFromMatrixPosition(w.target.matrixWorld),S.direction.sub(i),S.direction.transformDirection(v),p++}else if(w.isSpotLight){const S=n.spot[g];S.position.setFromMatrixPosition(w.matrixWorld),S.position.applyMatrix4(v),S.direction.setFromMatrixPosition(w.matrixWorld),i.setFromMatrixPosition(w.target.matrixWorld),S.direction.sub(i),S.direction.transformDirection(v),g++}else if(w.isRectAreaLight){const S=n.rectArea[x];S.position.setFromMatrixPosition(w.matrixWorld),S.position.applyMatrix4(v),a.identity(),s.copy(w.matrixWorld),s.premultiply(v),a.extractRotation(s),S.halfWidth.set(w.width*.5,0,0),S.halfHeight.set(0,w.height*.5,0),S.halfWidth.applyMatrix4(a),S.halfHeight.applyMatrix4(a),x++}else if(w.isPointLight){const S=n.point[m];S.position.setFromMatrixPosition(w.matrixWorld),S.position.applyMatrix4(v),m++}else if(w.isHemisphereLight){const S=n.hemi[E];S.direction.setFromMatrixPosition(w.matrixWorld),S.direction.transformDirection(v),E++}}}return{setup:c,setupView:u,state:n}}function Em(r){const e=new oP(r),t=[],n=[];function i(f){h.camera=f,t.length=0,n.length=0}function s(f){t.push(f)}function a(f){n.push(f)}function c(){e.setup(t)}function u(f){e.setupView(t,f)}const h={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:i,state:h,setupLights:c,setupLightsView:u,pushLight:s,pushShadow:a}}function aP(r){let e=new WeakMap;function t(i,s=0){const a=e.get(i);let c;return a===void 0?(c=new Em(r),e.set(i,[c])):s>=a.length?(c=new Em(r),a.push(c)):c=a[s],c}function n(){e=new WeakMap}return{get:t,dispose:n}}class cP extends Ii{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=GM,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class lP extends Ii{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const uP=`void main() {
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
}`;function dP(r,e,t){let n=new xd;const i=new ht,s=new ht,a=new Bt,c=new cP({depthPacking:WM}),u=new lP,h={},f=t.maxTextureSize,p={[ir]:Zn,[Zn]:ir,[$n]:$n},m=new Tr({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new ht},radius:{value:4}},vertexShader:uP,fragmentShader:hP}),g=m.clone();g.defines.HORIZONTAL_PASS=1;const x=new yn;x.setAttribute("position",new hn(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const E=new Pe(x,m),v=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=ug;let _=this.type;this.render=function(O,N,V){if(v.enabled===!1||v.autoUpdate===!1&&v.needsUpdate===!1||O.length===0)return;const D=r.getRenderTarget(),A=r.getActiveCubeFace(),k=r.getActiveMipmapLevel(),J=r.state;J.setBlending(Er),J.buffers.color.setClear(1,1,1,1),J.buffers.depth.setTest(!0),J.setScissorTest(!1);const ee=_!==Zi&&this.type===Zi,re=_===Zi&&this.type!==Zi;for(let le=0,Y=O.length;le<Y;le++){const de=O[le],ne=de.shadow;if(ne===void 0){console.warn("THREE.WebGLShadowMap:",de,"has no shadow.");continue}if(ne.autoUpdate===!1&&ne.needsUpdate===!1)continue;i.copy(ne.mapSize);const ye=ne.getFrameExtents();if(i.multiply(ye),s.copy(ne.mapSize),(i.x>f||i.y>f)&&(i.x>f&&(s.x=Math.floor(f/ye.x),i.x=s.x*ye.x,ne.mapSize.x=s.x),i.y>f&&(s.y=Math.floor(f/ye.y),i.y=s.y*ye.y,ne.mapSize.y=s.y)),ne.map===null||ee===!0||re===!0){const ze=this.type!==Zi?{minFilter:Wn,magFilter:Wn}:{};ne.map!==null&&ne.map.dispose(),ne.map=new us(i.x,i.y,ze),ne.map.texture.name=de.name+".shadowMap",ne.camera.updateProjectionMatrix()}r.setRenderTarget(ne.map),r.clear();const Te=ne.getViewportCount();for(let ze=0;ze<Te;ze++){const We=ne.getViewport(ze);a.set(s.x*We.x,s.y*We.y,s.x*We.z,s.y*We.w),J.viewport(a),ne.updateMatrices(de,ze),n=ne.getFrustum(),S(N,V,ne.camera,de,this.type)}ne.isPointLightShadow!==!0&&this.type===Zi&&R(ne,V),ne.needsUpdate=!1}_=this.type,v.needsUpdate=!1,r.setRenderTarget(D,A,k)};function R(O,N){const V=e.update(E);m.defines.VSM_SAMPLES!==O.blurSamples&&(m.defines.VSM_SAMPLES=O.blurSamples,g.defines.VSM_SAMPLES=O.blurSamples,m.needsUpdate=!0,g.needsUpdate=!0),O.mapPass===null&&(O.mapPass=new us(i.x,i.y)),m.uniforms.shadow_pass.value=O.map.texture,m.uniforms.resolution.value=O.mapSize,m.uniforms.radius.value=O.radius,r.setRenderTarget(O.mapPass),r.clear(),r.renderBufferDirect(N,null,V,m,E,null),g.uniforms.shadow_pass.value=O.mapPass.texture,g.uniforms.resolution.value=O.mapSize,g.uniforms.radius.value=O.radius,r.setRenderTarget(O.map),r.clear(),r.renderBufferDirect(N,null,V,g,E,null)}function w(O,N,V,D){let A=null;const k=V.isPointLight===!0?O.customDistanceMaterial:O.customDepthMaterial;if(k!==void 0)A=k;else if(A=V.isPointLight===!0?u:c,r.localClippingEnabled&&N.clipShadows===!0&&Array.isArray(N.clippingPlanes)&&N.clippingPlanes.length!==0||N.displacementMap&&N.displacementScale!==0||N.alphaMap&&N.alphaTest>0||N.map&&N.alphaTest>0){const J=A.uuid,ee=N.uuid;let re=h[J];re===void 0&&(re={},h[J]=re);let le=re[ee];le===void 0&&(le=A.clone(),re[ee]=le,N.addEventListener("dispose",z)),A=le}if(A.visible=N.visible,A.wireframe=N.wireframe,D===Zi?A.side=N.shadowSide!==null?N.shadowSide:N.side:A.side=N.shadowSide!==null?N.shadowSide:p[N.side],A.alphaMap=N.alphaMap,A.alphaTest=N.alphaTest,A.map=N.map,A.clipShadows=N.clipShadows,A.clippingPlanes=N.clippingPlanes,A.clipIntersection=N.clipIntersection,A.displacementMap=N.displacementMap,A.displacementScale=N.displacementScale,A.displacementBias=N.displacementBias,A.wireframeLinewidth=N.wireframeLinewidth,A.linewidth=N.linewidth,V.isPointLight===!0&&A.isMeshDistanceMaterial===!0){const J=r.properties.get(A);J.light=V}return A}function S(O,N,V,D,A){if(O.visible===!1)return;if(O.layers.test(N.layers)&&(O.isMesh||O.isLine||O.isPoints)&&(O.castShadow||O.receiveShadow&&A===Zi)&&(!O.frustumCulled||n.intersectsObject(O))){O.modelViewMatrix.multiplyMatrices(V.matrixWorldInverse,O.matrixWorld);const ee=e.update(O),re=O.material;if(Array.isArray(re)){const le=ee.groups;for(let Y=0,de=le.length;Y<de;Y++){const ne=le[Y],ye=re[ne.materialIndex];if(ye&&ye.visible){const Te=w(O,ye,D,A);O.onBeforeShadow(r,O,N,V,ee,Te,ne),r.renderBufferDirect(V,null,ee,Te,O,ne),O.onAfterShadow(r,O,N,V,ee,Te,ne)}}}else if(re.visible){const le=w(O,re,D,A);O.onBeforeShadow(r,O,N,V,ee,le,null),r.renderBufferDirect(V,null,ee,le,O,null),O.onAfterShadow(r,O,N,V,ee,le,null)}}const J=O.children;for(let ee=0,re=J.length;ee<re;ee++)S(J[ee],N,V,D,A)}function z(O){O.target.removeEventListener("dispose",z);for(const V in h){const D=h[V],A=O.target.uuid;A in D&&(D[A].dispose(),delete D[A])}}}const fP={[vh]:yh,[xh]:Eh,[bh]:Mh,[Zs]:Sh,[yh]:vh,[Eh]:xh,[Mh]:bh,[Sh]:Zs};function pP(r,e){function t(){let X=!1;const Re=new Bt;let ae=null;const pe=new Bt(0,0,0,0);return{setMask:function(F){ae!==F&&!X&&(r.colorMask(F,F,F,F),ae=F)},setLocked:function(F){X=F},setClear:function(F,W,ie,ve,je){je===!0&&(F*=ve,W*=ve,ie*=ve),Re.set(F,W,ie,ve),pe.equals(Re)===!1&&(r.clearColor(F,W,ie,ve),pe.copy(Re))},reset:function(){X=!1,ae=null,pe.set(-1,0,0,0)}}}function n(){let X=!1,Re=!1,ae=null,pe=null,F=null;return{setReversed:function(W){if(Re!==W){const ie=e.get("EXT_clip_control");Re?ie.clipControlEXT(ie.LOWER_LEFT_EXT,ie.ZERO_TO_ONE_EXT):ie.clipControlEXT(ie.LOWER_LEFT_EXT,ie.NEGATIVE_ONE_TO_ONE_EXT);const ve=F;F=null,this.setClear(ve)}Re=W},getReversed:function(){return Re},setTest:function(W){W?Se(r.DEPTH_TEST):et(r.DEPTH_TEST)},setMask:function(W){ae!==W&&!X&&(r.depthMask(W),ae=W)},setFunc:function(W){if(Re&&(W=fP[W]),pe!==W){switch(W){case vh:r.depthFunc(r.NEVER);break;case yh:r.depthFunc(r.ALWAYS);break;case xh:r.depthFunc(r.LESS);break;case Zs:r.depthFunc(r.LEQUAL);break;case bh:r.depthFunc(r.EQUAL);break;case Sh:r.depthFunc(r.GEQUAL);break;case Eh:r.depthFunc(r.GREATER);break;case Mh:r.depthFunc(r.NOTEQUAL);break;default:r.depthFunc(r.LEQUAL)}pe=W}},setLocked:function(W){X=W},setClear:function(W){F!==W&&(Re&&(W=1-W),r.clearDepth(W),F=W)},reset:function(){X=!1,ae=null,pe=null,F=null,Re=!1}}}function i(){let X=!1,Re=null,ae=null,pe=null,F=null,W=null,ie=null,ve=null,je=null;return{setTest:function(_e){X||(_e?Se(r.STENCIL_TEST):et(r.STENCIL_TEST))},setMask:function(_e){Re!==_e&&!X&&(r.stencilMask(_e),Re=_e)},setFunc:function(_e,He,ot){(ae!==_e||pe!==He||F!==ot)&&(r.stencilFunc(_e,He,ot),ae=_e,pe=He,F=ot)},setOp:function(_e,He,ot){(W!==_e||ie!==He||ve!==ot)&&(r.stencilOp(_e,He,ot),W=_e,ie=He,ve=ot)},setLocked:function(_e){X=_e},setClear:function(_e){je!==_e&&(r.clearStencil(_e),je=_e)},reset:function(){X=!1,Re=null,ae=null,pe=null,F=null,W=null,ie=null,ve=null,je=null}}}const s=new t,a=new n,c=new i,u=new WeakMap,h=new WeakMap;let f={},p={},m=new WeakMap,g=[],x=null,E=!1,v=null,_=null,R=null,w=null,S=null,z=null,O=null,N=new rt(0,0,0),V=0,D=!1,A=null,k=null,J=null,ee=null,re=null;const le=r.getParameter(r.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let Y=!1,de=0;const ne=r.getParameter(r.VERSION);ne.indexOf("WebGL")!==-1?(de=parseFloat(/^WebGL (\d)/.exec(ne)[1]),Y=de>=1):ne.indexOf("OpenGL ES")!==-1&&(de=parseFloat(/^OpenGL ES (\d)/.exec(ne)[1]),Y=de>=2);let ye=null,Te={};const ze=r.getParameter(r.SCISSOR_BOX),We=r.getParameter(r.VIEWPORT),xt=new Bt().fromArray(ze),ue=new Bt().fromArray(We);function me(X,Re,ae,pe){const F=new Uint8Array(4),W=r.createTexture();r.bindTexture(X,W),r.texParameteri(X,r.TEXTURE_MIN_FILTER,r.NEAREST),r.texParameteri(X,r.TEXTURE_MAG_FILTER,r.NEAREST);for(let ie=0;ie<ae;ie++)X===r.TEXTURE_3D||X===r.TEXTURE_2D_ARRAY?r.texImage3D(Re,0,r.RGBA,1,1,pe,0,r.RGBA,r.UNSIGNED_BYTE,F):r.texImage2D(Re+ie,0,r.RGBA,1,1,0,r.RGBA,r.UNSIGNED_BYTE,F);return W}const De={};De[r.TEXTURE_2D]=me(r.TEXTURE_2D,r.TEXTURE_2D,1),De[r.TEXTURE_CUBE_MAP]=me(r.TEXTURE_CUBE_MAP,r.TEXTURE_CUBE_MAP_POSITIVE_X,6),De[r.TEXTURE_2D_ARRAY]=me(r.TEXTURE_2D_ARRAY,r.TEXTURE_2D_ARRAY,1,1),De[r.TEXTURE_3D]=me(r.TEXTURE_3D,r.TEXTURE_3D,1,1),s.setClear(0,0,0,1),a.setClear(1),c.setClear(0),Se(r.DEPTH_TEST),a.setFunc(Zs),Je(!1),$e(wp),Se(r.CULL_FACE),H(Er);function Se(X){f[X]!==!0&&(r.enable(X),f[X]=!0)}function et(X){f[X]!==!1&&(r.disable(X),f[X]=!1)}function it(X,Re){return p[X]!==Re?(r.bindFramebuffer(X,Re),p[X]=Re,X===r.DRAW_FRAMEBUFFER&&(p[r.FRAMEBUFFER]=Re),X===r.FRAMEBUFFER&&(p[r.DRAW_FRAMEBUFFER]=Re),!0):!1}function Qe(X,Re){let ae=g,pe=!1;if(X){ae=m.get(Re),ae===void 0&&(ae=[],m.set(Re,ae));const F=X.textures;if(ae.length!==F.length||ae[0]!==r.COLOR_ATTACHMENT0){for(let W=0,ie=F.length;W<ie;W++)ae[W]=r.COLOR_ATTACHMENT0+W;ae.length=F.length,pe=!0}}else ae[0]!==r.BACK&&(ae[0]=r.BACK,pe=!0);pe&&r.drawBuffers(ae)}function fe(X){return x!==X?(r.useProgram(X),x=X,!0):!1}const Me={[os]:r.FUNC_ADD,[fM]:r.FUNC_SUBTRACT,[pM]:r.FUNC_REVERSE_SUBTRACT};Me[mM]=r.MIN,Me[gM]=r.MAX;const Fe={[_M]:r.ZERO,[vM]:r.ONE,[yM]:r.SRC_COLOR,[gh]:r.SRC_ALPHA,[TM]:r.SRC_ALPHA_SATURATE,[EM]:r.DST_COLOR,[bM]:r.DST_ALPHA,[xM]:r.ONE_MINUS_SRC_COLOR,[_h]:r.ONE_MINUS_SRC_ALPHA,[MM]:r.ONE_MINUS_DST_COLOR,[SM]:r.ONE_MINUS_DST_ALPHA,[wM]:r.CONSTANT_COLOR,[AM]:r.ONE_MINUS_CONSTANT_COLOR,[RM]:r.CONSTANT_ALPHA,[PM]:r.ONE_MINUS_CONSTANT_ALPHA};function H(X,Re,ae,pe,F,W,ie,ve,je,_e){if(X===Er){E===!0&&(et(r.BLEND),E=!1);return}if(E===!1&&(Se(r.BLEND),E=!0),X!==dM){if(X!==v||_e!==D){if((_!==os||S!==os)&&(r.blendEquation(r.FUNC_ADD),_=os,S=os),_e)switch(X){case qs:r.blendFuncSeparate(r.ONE,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Ap:r.blendFunc(r.ONE,r.ONE);break;case Rp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Pp:r.blendFuncSeparate(r.ZERO,r.SRC_COLOR,r.ZERO,r.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",X);break}else switch(X){case qs:r.blendFuncSeparate(r.SRC_ALPHA,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Ap:r.blendFunc(r.SRC_ALPHA,r.ONE);break;case Rp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Pp:r.blendFunc(r.ZERO,r.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",X);break}R=null,w=null,z=null,O=null,N.set(0,0,0),V=0,v=X,D=_e}return}F=F||Re,W=W||ae,ie=ie||pe,(Re!==_||F!==S)&&(r.blendEquationSeparate(Me[Re],Me[F]),_=Re,S=F),(ae!==R||pe!==w||W!==z||ie!==O)&&(r.blendFuncSeparate(Fe[ae],Fe[pe],Fe[W],Fe[ie]),R=ae,w=pe,z=W,O=ie),(ve.equals(N)===!1||je!==V)&&(r.blendColor(ve.r,ve.g,ve.b,je),N.copy(ve),V=je),v=X,D=!1}function nt(X,Re){X.side===$n?et(r.CULL_FACE):Se(r.CULL_FACE);let ae=X.side===Zn;Re&&(ae=!ae),Je(ae),X.blending===qs&&X.transparent===!1?H(Er):H(X.blending,X.blendEquation,X.blendSrc,X.blendDst,X.blendEquationAlpha,X.blendSrcAlpha,X.blendDstAlpha,X.blendColor,X.blendAlpha,X.premultipliedAlpha),a.setFunc(X.depthFunc),a.setTest(X.depthTest),a.setMask(X.depthWrite),s.setMask(X.colorWrite);const pe=X.stencilWrite;c.setTest(pe),pe&&(c.setMask(X.stencilWriteMask),c.setFunc(X.stencilFunc,X.stencilRef,X.stencilFuncMask),c.setOp(X.stencilFail,X.stencilZFail,X.stencilZPass)),at(X.polygonOffset,X.polygonOffsetFactor,X.polygonOffsetUnits),X.alphaToCoverage===!0?Se(r.SAMPLE_ALPHA_TO_COVERAGE):et(r.SAMPLE_ALPHA_TO_COVERAGE)}function Je(X){A!==X&&(X?r.frontFace(r.CW):r.frontFace(r.CCW),A=X)}function $e(X){X!==lM?(Se(r.CULL_FACE),X!==k&&(X===wp?r.cullFace(r.BACK):X===uM?r.cullFace(r.FRONT):r.cullFace(r.FRONT_AND_BACK))):et(r.CULL_FACE),k=X}function Oe(X){X!==J&&(Y&&r.lineWidth(X),J=X)}function at(X,Re,ae){X?(Se(r.POLYGON_OFFSET_FILL),(ee!==Re||re!==ae)&&(r.polygonOffset(Re,ae),ee=Re,re=ae)):et(r.POLYGON_OFFSET_FILL)}function Be(X){X?Se(r.SCISSOR_TEST):et(r.SCISSOR_TEST)}function L(X){X===void 0&&(X=r.TEXTURE0+le-1),ye!==X&&(r.activeTexture(X),ye=X)}function T(X,Re,ae){ae===void 0&&(ye===null?ae=r.TEXTURE0+le-1:ae=ye);let pe=Te[ae];pe===void 0&&(pe={type:void 0,texture:void 0},Te[ae]=pe),(pe.type!==X||pe.texture!==Re)&&(ye!==ae&&(r.activeTexture(ae),ye=ae),r.bindTexture(X,Re||De[X]),pe.type=X,pe.texture=Re)}function $(){const X=Te[ye];X!==void 0&&X.type!==void 0&&(r.bindTexture(X.type,null),X.type=void 0,X.texture=void 0)}function he(){try{r.compressedTexImage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function ge(){try{r.compressedTexImage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function ce(){try{r.texSubImage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function Ce(){try{r.texSubImage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function we(){try{r.compressedTexSubImage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function ke(){try{r.compressedTexSubImage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function Tt(){try{r.texStorage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function be(){try{r.texStorage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function Ue(){try{r.texImage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function Ge(){try{r.texImage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function st(X){xt.equals(X)===!1&&(r.scissor(X.x,X.y,X.z,X.w),xt.copy(X))}function Ve(X){ue.equals(X)===!1&&(r.viewport(X.x,X.y,X.z,X.w),ue.copy(X))}function bt(X,Re){let ae=h.get(Re);ae===void 0&&(ae=new WeakMap,h.set(Re,ae));let pe=ae.get(X);pe===void 0&&(pe=r.getUniformBlockIndex(Re,X.name),ae.set(X,pe))}function mt(X,Re){const pe=h.get(Re).get(X);u.get(Re)!==pe&&(r.uniformBlockBinding(Re,pe,X.__bindingPointIndex),u.set(Re,pe))}function Ft(){r.disable(r.BLEND),r.disable(r.CULL_FACE),r.disable(r.DEPTH_TEST),r.disable(r.POLYGON_OFFSET_FILL),r.disable(r.SCISSOR_TEST),r.disable(r.STENCIL_TEST),r.disable(r.SAMPLE_ALPHA_TO_COVERAGE),r.blendEquation(r.FUNC_ADD),r.blendFunc(r.ONE,r.ZERO),r.blendFuncSeparate(r.ONE,r.ZERO,r.ONE,r.ZERO),r.blendColor(0,0,0,0),r.colorMask(!0,!0,!0,!0),r.clearColor(0,0,0,0),r.depthMask(!0),r.depthFunc(r.LESS),a.setReversed(!1),r.clearDepth(1),r.stencilMask(4294967295),r.stencilFunc(r.ALWAYS,0,4294967295),r.stencilOp(r.KEEP,r.KEEP,r.KEEP),r.clearStencil(0),r.cullFace(r.BACK),r.frontFace(r.CCW),r.polygonOffset(0,0),r.activeTexture(r.TEXTURE0),r.bindFramebuffer(r.FRAMEBUFFER,null),r.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),r.bindFramebuffer(r.READ_FRAMEBUFFER,null),r.useProgram(null),r.lineWidth(1),r.scissor(0,0,r.canvas.width,r.canvas.height),r.viewport(0,0,r.canvas.width,r.canvas.height),f={},ye=null,Te={},p={},m=new WeakMap,g=[],x=null,E=!1,v=null,_=null,R=null,w=null,S=null,z=null,O=null,N=new rt(0,0,0),V=0,D=!1,A=null,k=null,J=null,ee=null,re=null,xt.set(0,0,r.canvas.width,r.canvas.height),ue.set(0,0,r.canvas.width,r.canvas.height),s.reset(),a.reset(),c.reset()}return{buffers:{color:s,depth:a,stencil:c},enable:Se,disable:et,bindFramebuffer:it,drawBuffers:Qe,useProgram:fe,setBlending:H,setMaterial:nt,setFlipSided:Je,setCullFace:$e,setLineWidth:Oe,setPolygonOffset:at,setScissorTest:Be,activeTexture:L,bindTexture:T,unbindTexture:$,compressedTexImage2D:he,compressedTexImage3D:ge,texImage2D:Ue,texImage3D:Ge,updateUBOMapping:bt,uniformBlockBinding:mt,texStorage2D:Tt,texStorage3D:be,texSubImage2D:ce,texSubImage3D:Ce,compressedTexSubImage2D:we,compressedTexSubImage3D:ke,scissor:st,viewport:Ve,reset:Ft}}function Mm(r,e,t,n){const i=mP(n);switch(t){case vg:return r*e;case xg:return r*e;case bg:return r*e*2;case dd:return r*e/i.components*i.byteLength;case fd:return r*e/i.components*i.byteLength;case Sg:return r*e*2/i.components*i.byteLength;case pd:return r*e*2/i.components*i.byteLength;case yg:return r*e*3/i.components*i.byteLength;case fi:return r*e*4/i.components*i.byteLength;case md:return r*e*4/i.components*i.byteLength;case Tc:case wc:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Ac:case Rc:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Rh:case Ch:return Math.max(r,16)*Math.max(e,8)/4;case Ah:case Ph:return Math.max(r,8)*Math.max(e,8)/2;case Dh:case Ih:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Lh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Fh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Nh:return Math.floor((r+4)/5)*Math.floor((e+3)/4)*16;case Oh:return Math.floor((r+4)/5)*Math.floor((e+4)/5)*16;case Uh:return Math.floor((r+5)/6)*Math.floor((e+4)/5)*16;case Bh:return Math.floor((r+5)/6)*Math.floor((e+5)/6)*16;case kh:return Math.floor((r+7)/8)*Math.floor((e+4)/5)*16;case zh:return Math.floor((r+7)/8)*Math.floor((e+5)/6)*16;case Hh:return Math.floor((r+7)/8)*Math.floor((e+7)/8)*16;case Vh:return Math.floor((r+9)/10)*Math.floor((e+4)/5)*16;case Gh:return Math.floor((r+9)/10)*Math.floor((e+5)/6)*16;case Wh:return Math.floor((r+9)/10)*Math.floor((e+7)/8)*16;case jh:return Math.floor((r+9)/10)*Math.floor((e+9)/10)*16;case Xh:return Math.floor((r+11)/12)*Math.floor((e+9)/10)*16;case qh:return Math.floor((r+11)/12)*Math.floor((e+11)/12)*16;case Pc:case Yh:case Kh:return Math.ceil(r/4)*Math.ceil(e/4)*16;case Eg:case $h:return Math.ceil(r/4)*Math.ceil(e/4)*8;case Zh:case Qh:return Math.ceil(r/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function mP(r){switch(r){case rr:case mg:return{byteLength:1,components:1};case Jo:case gg:case ia:return{byteLength:2,components:1};case ud:case hd:return{byteLength:2,components:4};case ls:case ld:case Ei:return{byteLength:4,components:1};case _g:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${r}.`)}function gP(r,e,t,n,i,s,a){const c=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,u=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),h=new ht,f=new WeakMap;let p;const m=new WeakMap;let g=!1;try{g=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function x(L,T){return g?new OffscreenCanvas(L,T):na("canvas")}function E(L,T,$){let he=1;const ge=Be(L);if((ge.width>$||ge.height>$)&&(he=$/Math.max(ge.width,ge.height)),he<1)if(typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&L instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&L instanceof ImageBitmap||typeof VideoFrame<"u"&&L instanceof VideoFrame){const ce=Math.floor(he*ge.width),Ce=Math.floor(he*ge.height);p===void 0&&(p=x(ce,Ce));const we=T?x(ce,Ce):p;return we.width=ce,we.height=Ce,we.getContext("2d").drawImage(L,0,0,ce,Ce),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+ge.width+"x"+ge.height+") to ("+ce+"x"+Ce+")."),we}else return"data"in L&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+ge.width+"x"+ge.height+")."),L;return L}function v(L){return L.generateMipmaps}function _(L){r.generateMipmap(L)}function R(L){return L.isWebGLCubeRenderTarget?r.TEXTURE_CUBE_MAP:L.isWebGL3DRenderTarget?r.TEXTURE_3D:L.isWebGLArrayRenderTarget||L.isCompressedArrayTexture?r.TEXTURE_2D_ARRAY:r.TEXTURE_2D}function w(L,T,$,he,ge=!1){if(L!==null){if(r[L]!==void 0)return r[L];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+L+"'")}let ce=T;if(T===r.RED&&($===r.FLOAT&&(ce=r.R32F),$===r.HALF_FLOAT&&(ce=r.R16F),$===r.UNSIGNED_BYTE&&(ce=r.R8)),T===r.RED_INTEGER&&($===r.UNSIGNED_BYTE&&(ce=r.R8UI),$===r.UNSIGNED_SHORT&&(ce=r.R16UI),$===r.UNSIGNED_INT&&(ce=r.R32UI),$===r.BYTE&&(ce=r.R8I),$===r.SHORT&&(ce=r.R16I),$===r.INT&&(ce=r.R32I)),T===r.RG&&($===r.FLOAT&&(ce=r.RG32F),$===r.HALF_FLOAT&&(ce=r.RG16F),$===r.UNSIGNED_BYTE&&(ce=r.RG8)),T===r.RG_INTEGER&&($===r.UNSIGNED_BYTE&&(ce=r.RG8UI),$===r.UNSIGNED_SHORT&&(ce=r.RG16UI),$===r.UNSIGNED_INT&&(ce=r.RG32UI),$===r.BYTE&&(ce=r.RG8I),$===r.SHORT&&(ce=r.RG16I),$===r.INT&&(ce=r.RG32I)),T===r.RGB_INTEGER&&($===r.UNSIGNED_BYTE&&(ce=r.RGB8UI),$===r.UNSIGNED_SHORT&&(ce=r.RGB16UI),$===r.UNSIGNED_INT&&(ce=r.RGB32UI),$===r.BYTE&&(ce=r.RGB8I),$===r.SHORT&&(ce=r.RGB16I),$===r.INT&&(ce=r.RGB32I)),T===r.RGBA_INTEGER&&($===r.UNSIGNED_BYTE&&(ce=r.RGBA8UI),$===r.UNSIGNED_SHORT&&(ce=r.RGBA16UI),$===r.UNSIGNED_INT&&(ce=r.RGBA32UI),$===r.BYTE&&(ce=r.RGBA8I),$===r.SHORT&&(ce=r.RGBA16I),$===r.INT&&(ce=r.RGBA32I)),T===r.RGB&&$===r.UNSIGNED_INT_5_9_9_9_REV&&(ce=r.RGB9_E5),T===r.RGBA){const Ce=ge?zc:Lt.getTransfer(he);$===r.FLOAT&&(ce=r.RGBA32F),$===r.HALF_FLOAT&&(ce=r.RGBA16F),$===r.UNSIGNED_BYTE&&(ce=Ce===qt?r.SRGB8_ALPHA8:r.RGBA8),$===r.UNSIGNED_SHORT_4_4_4_4&&(ce=r.RGBA4),$===r.UNSIGNED_SHORT_5_5_5_1&&(ce=r.RGB5_A1)}return(ce===r.R16F||ce===r.R32F||ce===r.RG16F||ce===r.RG32F||ce===r.RGBA16F||ce===r.RGBA32F)&&e.get("EXT_color_buffer_float"),ce}function S(L,T){let $;return L?T===null||T===ls||T===to?$=r.DEPTH24_STENCIL8:T===Ei?$=r.DEPTH32F_STENCIL8:T===Jo&&($=r.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):T===null||T===ls||T===to?$=r.DEPTH_COMPONENT24:T===Ei?$=r.DEPTH_COMPONENT32F:T===Jo&&($=r.DEPTH_COMPONENT16),$}function z(L,T){return v(L)===!0||L.isFramebufferTexture&&L.minFilter!==Wn&&L.minFilter!==ai?Math.log2(Math.max(T.width,T.height))+1:L.mipmaps!==void 0&&L.mipmaps.length>0?L.mipmaps.length:L.isCompressedTexture&&Array.isArray(L.image)?T.mipmaps.length:1}function O(L){const T=L.target;T.removeEventListener("dispose",O),V(T),T.isVideoTexture&&f.delete(T)}function N(L){const T=L.target;T.removeEventListener("dispose",N),A(T)}function V(L){const T=n.get(L);if(T.__webglInit===void 0)return;const $=L.source,he=m.get($);if(he){const ge=he[T.__cacheKey];ge.usedTimes--,ge.usedTimes===0&&D(L),Object.keys(he).length===0&&m.delete($)}n.remove(L)}function D(L){const T=n.get(L);r.deleteTexture(T.__webglTexture);const $=L.source,he=m.get($);delete he[T.__cacheKey],a.memory.textures--}function A(L){const T=n.get(L);if(L.depthTexture&&(L.depthTexture.dispose(),n.remove(L.depthTexture)),L.isWebGLCubeRenderTarget)for(let he=0;he<6;he++){if(Array.isArray(T.__webglFramebuffer[he]))for(let ge=0;ge<T.__webglFramebuffer[he].length;ge++)r.deleteFramebuffer(T.__webglFramebuffer[he][ge]);else r.deleteFramebuffer(T.__webglFramebuffer[he]);T.__webglDepthbuffer&&r.deleteRenderbuffer(T.__webglDepthbuffer[he])}else{if(Array.isArray(T.__webglFramebuffer))for(let he=0;he<T.__webglFramebuffer.length;he++)r.deleteFramebuffer(T.__webglFramebuffer[he]);else r.deleteFramebuffer(T.__webglFramebuffer);if(T.__webglDepthbuffer&&r.deleteRenderbuffer(T.__webglDepthbuffer),T.__webglMultisampledFramebuffer&&r.deleteFramebuffer(T.__webglMultisampledFramebuffer),T.__webglColorRenderbuffer)for(let he=0;he<T.__webglColorRenderbuffer.length;he++)T.__webglColorRenderbuffer[he]&&r.deleteRenderbuffer(T.__webglColorRenderbuffer[he]);T.__webglDepthRenderbuffer&&r.deleteRenderbuffer(T.__webglDepthRenderbuffer)}const $=L.textures;for(let he=0,ge=$.length;he<ge;he++){const ce=n.get($[he]);ce.__webglTexture&&(r.deleteTexture(ce.__webglTexture),a.memory.textures--),n.remove($[he])}n.remove(L)}let k=0;function J(){k=0}function ee(){const L=k;return L>=i.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+L+" texture units while this GPU supports only "+i.maxTextures),k+=1,L}function re(L){const T=[];return T.push(L.wrapS),T.push(L.wrapT),T.push(L.wrapR||0),T.push(L.magFilter),T.push(L.minFilter),T.push(L.anisotropy),T.push(L.internalFormat),T.push(L.format),T.push(L.type),T.push(L.generateMipmaps),T.push(L.premultiplyAlpha),T.push(L.flipY),T.push(L.unpackAlignment),T.push(L.colorSpace),T.join()}function le(L,T){const $=n.get(L);if(L.isVideoTexture&&Oe(L),L.isRenderTargetTexture===!1&&L.version>0&&$.__version!==L.version){const he=L.image;if(he===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(he.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{ue($,L,T);return}}t.bindTexture(r.TEXTURE_2D,$.__webglTexture,r.TEXTURE0+T)}function Y(L,T){const $=n.get(L);if(L.version>0&&$.__version!==L.version){ue($,L,T);return}t.bindTexture(r.TEXTURE_2D_ARRAY,$.__webglTexture,r.TEXTURE0+T)}function de(L,T){const $=n.get(L);if(L.version>0&&$.__version!==L.version){ue($,L,T);return}t.bindTexture(r.TEXTURE_3D,$.__webglTexture,r.TEXTURE0+T)}function ne(L,T){const $=n.get(L);if(L.version>0&&$.__version!==L.version){me($,L,T);return}t.bindTexture(r.TEXTURE_CUBE_MAP,$.__webglTexture,r.TEXTURE0+T)}const ye={[eo]:r.REPEAT,[br]:r.CLAMP_TO_EDGE,[Fc]:r.MIRRORED_REPEAT},Te={[Wn]:r.NEAREST,[pg]:r.NEAREST_MIPMAP_NEAREST,[Wo]:r.NEAREST_MIPMAP_LINEAR,[ai]:r.LINEAR,[Mc]:r.LINEAR_MIPMAP_NEAREST,[Ji]:r.LINEAR_MIPMAP_LINEAR},ze={[XM]:r.NEVER,[QM]:r.ALWAYS,[qM]:r.LESS,[wg]:r.LEQUAL,[YM]:r.EQUAL,[ZM]:r.GEQUAL,[KM]:r.GREATER,[$M]:r.NOTEQUAL};function We(L,T){if(T.type===Ei&&e.has("OES_texture_float_linear")===!1&&(T.magFilter===ai||T.magFilter===Mc||T.magFilter===Wo||T.magFilter===Ji||T.minFilter===ai||T.minFilter===Mc||T.minFilter===Wo||T.minFilter===Ji)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),r.texParameteri(L,r.TEXTURE_WRAP_S,ye[T.wrapS]),r.texParameteri(L,r.TEXTURE_WRAP_T,ye[T.wrapT]),(L===r.TEXTURE_3D||L===r.TEXTURE_2D_ARRAY)&&r.texParameteri(L,r.TEXTURE_WRAP_R,ye[T.wrapR]),r.texParameteri(L,r.TEXTURE_MAG_FILTER,Te[T.magFilter]),r.texParameteri(L,r.TEXTURE_MIN_FILTER,Te[T.minFilter]),T.compareFunction&&(r.texParameteri(L,r.TEXTURE_COMPARE_MODE,r.COMPARE_REF_TO_TEXTURE),r.texParameteri(L,r.TEXTURE_COMPARE_FUNC,ze[T.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(T.magFilter===Wn||T.minFilter!==Wo&&T.minFilter!==Ji||T.type===Ei&&e.has("OES_texture_float_linear")===!1)return;if(T.anisotropy>1||n.get(T).__currentAnisotropy){const $=e.get("EXT_texture_filter_anisotropic");r.texParameterf(L,$.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(T.anisotropy,i.getMaxAnisotropy())),n.get(T).__currentAnisotropy=T.anisotropy}}}function xt(L,T){let $=!1;L.__webglInit===void 0&&(L.__webglInit=!0,T.addEventListener("dispose",O));const he=T.source;let ge=m.get(he);ge===void 0&&(ge={},m.set(he,ge));const ce=re(T);if(ce!==L.__cacheKey){ge[ce]===void 0&&(ge[ce]={texture:r.createTexture(),usedTimes:0},a.memory.textures++,$=!0),ge[ce].usedTimes++;const Ce=ge[L.__cacheKey];Ce!==void 0&&(ge[L.__cacheKey].usedTimes--,Ce.usedTimes===0&&D(T)),L.__cacheKey=ce,L.__webglTexture=ge[ce].texture}return $}function ue(L,T,$){let he=r.TEXTURE_2D;(T.isDataArrayTexture||T.isCompressedArrayTexture)&&(he=r.TEXTURE_2D_ARRAY),T.isData3DTexture&&(he=r.TEXTURE_3D);const ge=xt(L,T),ce=T.source;t.bindTexture(he,L.__webglTexture,r.TEXTURE0+$);const Ce=n.get(ce);if(ce.version!==Ce.__version||ge===!0){t.activeTexture(r.TEXTURE0+$);const we=Lt.getPrimaries(Lt.workingColorSpace),ke=T.colorSpace===xr?null:Lt.getPrimaries(T.colorSpace),Tt=T.colorSpace===xr||we===ke?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,T.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,T.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,Tt);let be=E(T.image,!1,i.maxTextureSize);be=at(T,be);const Ue=s.convert(T.format,T.colorSpace),Ge=s.convert(T.type);let st=w(T.internalFormat,Ue,Ge,T.colorSpace,T.isVideoTexture);We(he,T);let Ve;const bt=T.mipmaps,mt=T.isVideoTexture!==!0,Ft=Ce.__version===void 0||ge===!0,X=ce.dataReady,Re=z(T,be);if(T.isDepthTexture)st=S(T.format===no,T.type),Ft&&(mt?t.texStorage2D(r.TEXTURE_2D,1,st,be.width,be.height):t.texImage2D(r.TEXTURE_2D,0,st,be.width,be.height,0,Ue,Ge,null));else if(T.isDataTexture)if(bt.length>0){mt&&Ft&&t.texStorage2D(r.TEXTURE_2D,Re,st,bt[0].width,bt[0].height);for(let ae=0,pe=bt.length;ae<pe;ae++)Ve=bt[ae],mt?X&&t.texSubImage2D(r.TEXTURE_2D,ae,0,0,Ve.width,Ve.height,Ue,Ge,Ve.data):t.texImage2D(r.TEXTURE_2D,ae,st,Ve.width,Ve.height,0,Ue,Ge,Ve.data);T.generateMipmaps=!1}else mt?(Ft&&t.texStorage2D(r.TEXTURE_2D,Re,st,be.width,be.height),X&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,be.width,be.height,Ue,Ge,be.data)):t.texImage2D(r.TEXTURE_2D,0,st,be.width,be.height,0,Ue,Ge,be.data);else if(T.isCompressedTexture)if(T.isCompressedArrayTexture){mt&&Ft&&t.texStorage3D(r.TEXTURE_2D_ARRAY,Re,st,bt[0].width,bt[0].height,be.depth);for(let ae=0,pe=bt.length;ae<pe;ae++)if(Ve=bt[ae],T.format!==fi)if(Ue!==null)if(mt){if(X)if(T.layerUpdates.size>0){const F=Mm(Ve.width,Ve.height,T.format,T.type);for(const W of T.layerUpdates){const ie=Ve.data.subarray(W*F/Ve.data.BYTES_PER_ELEMENT,(W+1)*F/Ve.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,ae,0,0,W,Ve.width,Ve.height,1,Ue,ie)}T.clearLayerUpdates()}else t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,ae,0,0,0,Ve.width,Ve.height,be.depth,Ue,Ve.data)}else t.compressedTexImage3D(r.TEXTURE_2D_ARRAY,ae,st,Ve.width,Ve.height,be.depth,0,Ve.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else mt?X&&t.texSubImage3D(r.TEXTURE_2D_ARRAY,ae,0,0,0,Ve.width,Ve.height,be.depth,Ue,Ge,Ve.data):t.texImage3D(r.TEXTURE_2D_ARRAY,ae,st,Ve.width,Ve.height,be.depth,0,Ue,Ge,Ve.data)}else{mt&&Ft&&t.texStorage2D(r.TEXTURE_2D,Re,st,bt[0].width,bt[0].height);for(let ae=0,pe=bt.length;ae<pe;ae++)Ve=bt[ae],T.format!==fi?Ue!==null?mt?X&&t.compressedTexSubImage2D(r.TEXTURE_2D,ae,0,0,Ve.width,Ve.height,Ue,Ve.data):t.compressedTexImage2D(r.TEXTURE_2D,ae,st,Ve.width,Ve.height,0,Ve.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):mt?X&&t.texSubImage2D(r.TEXTURE_2D,ae,0,0,Ve.width,Ve.height,Ue,Ge,Ve.data):t.texImage2D(r.TEXTURE_2D,ae,st,Ve.width,Ve.height,0,Ue,Ge,Ve.data)}else if(T.isDataArrayTexture)if(mt){if(Ft&&t.texStorage3D(r.TEXTURE_2D_ARRAY,Re,st,be.width,be.height,be.depth),X)if(T.layerUpdates.size>0){const ae=Mm(be.width,be.height,T.format,T.type);for(const pe of T.layerUpdates){const F=be.data.subarray(pe*ae/be.data.BYTES_PER_ELEMENT,(pe+1)*ae/be.data.BYTES_PER_ELEMENT);t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,pe,be.width,be.height,1,Ue,Ge,F)}T.clearLayerUpdates()}else t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,0,be.width,be.height,be.depth,Ue,Ge,be.data)}else t.texImage3D(r.TEXTURE_2D_ARRAY,0,st,be.width,be.height,be.depth,0,Ue,Ge,be.data);else if(T.isData3DTexture)mt?(Ft&&t.texStorage3D(r.TEXTURE_3D,Re,st,be.width,be.height,be.depth),X&&t.texSubImage3D(r.TEXTURE_3D,0,0,0,0,be.width,be.height,be.depth,Ue,Ge,be.data)):t.texImage3D(r.TEXTURE_3D,0,st,be.width,be.height,be.depth,0,Ue,Ge,be.data);else if(T.isFramebufferTexture){if(Ft)if(mt)t.texStorage2D(r.TEXTURE_2D,Re,st,be.width,be.height);else{let ae=be.width,pe=be.height;for(let F=0;F<Re;F++)t.texImage2D(r.TEXTURE_2D,F,st,ae,pe,0,Ue,Ge,null),ae>>=1,pe>>=1}}else if(bt.length>0){if(mt&&Ft){const ae=Be(bt[0]);t.texStorage2D(r.TEXTURE_2D,Re,st,ae.width,ae.height)}for(let ae=0,pe=bt.length;ae<pe;ae++)Ve=bt[ae],mt?X&&t.texSubImage2D(r.TEXTURE_2D,ae,0,0,Ue,Ge,Ve):t.texImage2D(r.TEXTURE_2D,ae,st,Ue,Ge,Ve);T.generateMipmaps=!1}else if(mt){if(Ft){const ae=Be(be);t.texStorage2D(r.TEXTURE_2D,Re,st,ae.width,ae.height)}X&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,Ue,Ge,be)}else t.texImage2D(r.TEXTURE_2D,0,st,Ue,Ge,be);v(T)&&_(he),Ce.__version=ce.version,T.onUpdate&&T.onUpdate(T)}L.__version=T.version}function me(L,T,$){if(T.image.length!==6)return;const he=xt(L,T),ge=T.source;t.bindTexture(r.TEXTURE_CUBE_MAP,L.__webglTexture,r.TEXTURE0+$);const ce=n.get(ge);if(ge.version!==ce.__version||he===!0){t.activeTexture(r.TEXTURE0+$);const Ce=Lt.getPrimaries(Lt.workingColorSpace),we=T.colorSpace===xr?null:Lt.getPrimaries(T.colorSpace),ke=T.colorSpace===xr||Ce===we?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,T.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,T.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,ke);const Tt=T.isCompressedTexture||T.image[0].isCompressedTexture,be=T.image[0]&&T.image[0].isDataTexture,Ue=[];for(let pe=0;pe<6;pe++)!Tt&&!be?Ue[pe]=E(T.image[pe],!0,i.maxCubemapSize):Ue[pe]=be?T.image[pe].image:T.image[pe],Ue[pe]=at(T,Ue[pe]);const Ge=Ue[0],st=s.convert(T.format,T.colorSpace),Ve=s.convert(T.type),bt=w(T.internalFormat,st,Ve,T.colorSpace),mt=T.isVideoTexture!==!0,Ft=ce.__version===void 0||he===!0,X=ge.dataReady;let Re=z(T,Ge);We(r.TEXTURE_CUBE_MAP,T);let ae;if(Tt){mt&&Ft&&t.texStorage2D(r.TEXTURE_CUBE_MAP,Re,bt,Ge.width,Ge.height);for(let pe=0;pe<6;pe++){ae=Ue[pe].mipmaps;for(let F=0;F<ae.length;F++){const W=ae[F];T.format!==fi?st!==null?mt?X&&t.compressedTexSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,F,0,0,W.width,W.height,st,W.data):t.compressedTexImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,F,bt,W.width,W.height,0,W.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):mt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,F,0,0,W.width,W.height,st,Ve,W.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,F,bt,W.width,W.height,0,st,Ve,W.data)}}}else{if(ae=T.mipmaps,mt&&Ft){ae.length>0&&Re++;const pe=Be(Ue[0]);t.texStorage2D(r.TEXTURE_CUBE_MAP,Re,bt,pe.width,pe.height)}for(let pe=0;pe<6;pe++)if(be){mt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,0,0,0,Ue[pe].width,Ue[pe].height,st,Ve,Ue[pe].data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,0,bt,Ue[pe].width,Ue[pe].height,0,st,Ve,Ue[pe].data);for(let F=0;F<ae.length;F++){const ie=ae[F].image[pe].image;mt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,F+1,0,0,ie.width,ie.height,st,Ve,ie.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,F+1,bt,ie.width,ie.height,0,st,Ve,ie.data)}}else{mt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,0,0,0,st,Ve,Ue[pe]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,0,bt,st,Ve,Ue[pe]);for(let F=0;F<ae.length;F++){const W=ae[F];mt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,F+1,0,0,st,Ve,W.image[pe]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+pe,F+1,bt,st,Ve,W.image[pe])}}}v(T)&&_(r.TEXTURE_CUBE_MAP),ce.__version=ge.version,T.onUpdate&&T.onUpdate(T)}L.__version=T.version}function De(L,T,$,he,ge,ce){const Ce=s.convert($.format,$.colorSpace),we=s.convert($.type),ke=w($.internalFormat,Ce,we,$.colorSpace),Tt=n.get(T),be=n.get($);if(be.__renderTarget=T,!Tt.__hasExternalTextures){const Ue=Math.max(1,T.width>>ce),Ge=Math.max(1,T.height>>ce);ge===r.TEXTURE_3D||ge===r.TEXTURE_2D_ARRAY?t.texImage3D(ge,ce,ke,Ue,Ge,T.depth,0,Ce,we,null):t.texImage2D(ge,ce,ke,Ue,Ge,0,Ce,we,null)}t.bindFramebuffer(r.FRAMEBUFFER,L),$e(T)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,he,ge,be.__webglTexture,0,Je(T)):(ge===r.TEXTURE_2D||ge>=r.TEXTURE_CUBE_MAP_POSITIVE_X&&ge<=r.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&r.framebufferTexture2D(r.FRAMEBUFFER,he,ge,be.__webglTexture,ce),t.bindFramebuffer(r.FRAMEBUFFER,null)}function Se(L,T,$){if(r.bindRenderbuffer(r.RENDERBUFFER,L),T.depthBuffer){const he=T.depthTexture,ge=he&&he.isDepthTexture?he.type:null,ce=S(T.stencilBuffer,ge),Ce=T.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,we=Je(T);$e(T)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,we,ce,T.width,T.height):$?r.renderbufferStorageMultisample(r.RENDERBUFFER,we,ce,T.width,T.height):r.renderbufferStorage(r.RENDERBUFFER,ce,T.width,T.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,Ce,r.RENDERBUFFER,L)}else{const he=T.textures;for(let ge=0;ge<he.length;ge++){const ce=he[ge],Ce=s.convert(ce.format,ce.colorSpace),we=s.convert(ce.type),ke=w(ce.internalFormat,Ce,we,ce.colorSpace),Tt=Je(T);$&&$e(T)===!1?r.renderbufferStorageMultisample(r.RENDERBUFFER,Tt,ke,T.width,T.height):$e(T)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,Tt,ke,T.width,T.height):r.renderbufferStorage(r.RENDERBUFFER,ke,T.width,T.height)}}r.bindRenderbuffer(r.RENDERBUFFER,null)}function et(L,T){if(T&&T.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(r.FRAMEBUFFER,L),!(T.depthTexture&&T.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const he=n.get(T.depthTexture);he.__renderTarget=T,(!he.__webglTexture||T.depthTexture.image.width!==T.width||T.depthTexture.image.height!==T.height)&&(T.depthTexture.image.width=T.width,T.depthTexture.image.height=T.height,T.depthTexture.needsUpdate=!0),le(T.depthTexture,0);const ge=he.__webglTexture,ce=Je(T);if(T.depthTexture.format===Ys)$e(T)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,ge,0,ce):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,ge,0);else if(T.depthTexture.format===no)$e(T)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,ge,0,ce):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,ge,0);else throw new Error("Unknown depthTexture format")}function it(L){const T=n.get(L),$=L.isWebGLCubeRenderTarget===!0;if(T.__boundDepthTexture!==L.depthTexture){const he=L.depthTexture;if(T.__depthDisposeCallback&&T.__depthDisposeCallback(),he){const ge=()=>{delete T.__boundDepthTexture,delete T.__depthDisposeCallback,he.removeEventListener("dispose",ge)};he.addEventListener("dispose",ge),T.__depthDisposeCallback=ge}T.__boundDepthTexture=he}if(L.depthTexture&&!T.__autoAllocateDepthBuffer){if($)throw new Error("target.depthTexture not supported in Cube render targets");et(T.__webglFramebuffer,L)}else if($){T.__webglDepthbuffer=[];for(let he=0;he<6;he++)if(t.bindFramebuffer(r.FRAMEBUFFER,T.__webglFramebuffer[he]),T.__webglDepthbuffer[he]===void 0)T.__webglDepthbuffer[he]=r.createRenderbuffer(),Se(T.__webglDepthbuffer[he],L,!1);else{const ge=L.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,ce=T.__webglDepthbuffer[he];r.bindRenderbuffer(r.RENDERBUFFER,ce),r.framebufferRenderbuffer(r.FRAMEBUFFER,ge,r.RENDERBUFFER,ce)}}else if(t.bindFramebuffer(r.FRAMEBUFFER,T.__webglFramebuffer),T.__webglDepthbuffer===void 0)T.__webglDepthbuffer=r.createRenderbuffer(),Se(T.__webglDepthbuffer,L,!1);else{const he=L.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,ge=T.__webglDepthbuffer;r.bindRenderbuffer(r.RENDERBUFFER,ge),r.framebufferRenderbuffer(r.FRAMEBUFFER,he,r.RENDERBUFFER,ge)}t.bindFramebuffer(r.FRAMEBUFFER,null)}function Qe(L,T,$){const he=n.get(L);T!==void 0&&De(he.__webglFramebuffer,L,L.texture,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,0),$!==void 0&&it(L)}function fe(L){const T=L.texture,$=n.get(L),he=n.get(T);L.addEventListener("dispose",N);const ge=L.textures,ce=L.isWebGLCubeRenderTarget===!0,Ce=ge.length>1;if(Ce||(he.__webglTexture===void 0&&(he.__webglTexture=r.createTexture()),he.__version=T.version,a.memory.textures++),ce){$.__webglFramebuffer=[];for(let we=0;we<6;we++)if(T.mipmaps&&T.mipmaps.length>0){$.__webglFramebuffer[we]=[];for(let ke=0;ke<T.mipmaps.length;ke++)$.__webglFramebuffer[we][ke]=r.createFramebuffer()}else $.__webglFramebuffer[we]=r.createFramebuffer()}else{if(T.mipmaps&&T.mipmaps.length>0){$.__webglFramebuffer=[];for(let we=0;we<T.mipmaps.length;we++)$.__webglFramebuffer[we]=r.createFramebuffer()}else $.__webglFramebuffer=r.createFramebuffer();if(Ce)for(let we=0,ke=ge.length;we<ke;we++){const Tt=n.get(ge[we]);Tt.__webglTexture===void 0&&(Tt.__webglTexture=r.createTexture(),a.memory.textures++)}if(L.samples>0&&$e(L)===!1){$.__webglMultisampledFramebuffer=r.createFramebuffer(),$.__webglColorRenderbuffer=[],t.bindFramebuffer(r.FRAMEBUFFER,$.__webglMultisampledFramebuffer);for(let we=0;we<ge.length;we++){const ke=ge[we];$.__webglColorRenderbuffer[we]=r.createRenderbuffer(),r.bindRenderbuffer(r.RENDERBUFFER,$.__webglColorRenderbuffer[we]);const Tt=s.convert(ke.format,ke.colorSpace),be=s.convert(ke.type),Ue=w(ke.internalFormat,Tt,be,ke.colorSpace,L.isXRRenderTarget===!0),Ge=Je(L);r.renderbufferStorageMultisample(r.RENDERBUFFER,Ge,Ue,L.width,L.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+we,r.RENDERBUFFER,$.__webglColorRenderbuffer[we])}r.bindRenderbuffer(r.RENDERBUFFER,null),L.depthBuffer&&($.__webglDepthRenderbuffer=r.createRenderbuffer(),Se($.__webglDepthRenderbuffer,L,!0)),t.bindFramebuffer(r.FRAMEBUFFER,null)}}if(ce){t.bindTexture(r.TEXTURE_CUBE_MAP,he.__webglTexture),We(r.TEXTURE_CUBE_MAP,T);for(let we=0;we<6;we++)if(T.mipmaps&&T.mipmaps.length>0)for(let ke=0;ke<T.mipmaps.length;ke++)De($.__webglFramebuffer[we][ke],L,T,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+we,ke);else De($.__webglFramebuffer[we],L,T,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+we,0);v(T)&&_(r.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ce){for(let we=0,ke=ge.length;we<ke;we++){const Tt=ge[we],be=n.get(Tt);t.bindTexture(r.TEXTURE_2D,be.__webglTexture),We(r.TEXTURE_2D,Tt),De($.__webglFramebuffer,L,Tt,r.COLOR_ATTACHMENT0+we,r.TEXTURE_2D,0),v(Tt)&&_(r.TEXTURE_2D)}t.unbindTexture()}else{let we=r.TEXTURE_2D;if((L.isWebGL3DRenderTarget||L.isWebGLArrayRenderTarget)&&(we=L.isWebGL3DRenderTarget?r.TEXTURE_3D:r.TEXTURE_2D_ARRAY),t.bindTexture(we,he.__webglTexture),We(we,T),T.mipmaps&&T.mipmaps.length>0)for(let ke=0;ke<T.mipmaps.length;ke++)De($.__webglFramebuffer[ke],L,T,r.COLOR_ATTACHMENT0,we,ke);else De($.__webglFramebuffer,L,T,r.COLOR_ATTACHMENT0,we,0);v(T)&&_(we),t.unbindTexture()}L.depthBuffer&&it(L)}function Me(L){const T=L.textures;for(let $=0,he=T.length;$<he;$++){const ge=T[$];if(v(ge)){const ce=R(L),Ce=n.get(ge).__webglTexture;t.bindTexture(ce,Ce),_(ce),t.unbindTexture()}}}const Fe=[],H=[];function nt(L){if(L.samples>0){if($e(L)===!1){const T=L.textures,$=L.width,he=L.height;let ge=r.COLOR_BUFFER_BIT;const ce=L.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Ce=n.get(L),we=T.length>1;if(we)for(let ke=0;ke<T.length;ke++)t.bindFramebuffer(r.FRAMEBUFFER,Ce.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+ke,r.RENDERBUFFER,null),t.bindFramebuffer(r.FRAMEBUFFER,Ce.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+ke,r.TEXTURE_2D,null,0);t.bindFramebuffer(r.READ_FRAMEBUFFER,Ce.__webglMultisampledFramebuffer),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Ce.__webglFramebuffer);for(let ke=0;ke<T.length;ke++){if(L.resolveDepthBuffer&&(L.depthBuffer&&(ge|=r.DEPTH_BUFFER_BIT),L.stencilBuffer&&L.resolveStencilBuffer&&(ge|=r.STENCIL_BUFFER_BIT)),we){r.framebufferRenderbuffer(r.READ_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.RENDERBUFFER,Ce.__webglColorRenderbuffer[ke]);const Tt=n.get(T[ke]).__webglTexture;r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,Tt,0)}r.blitFramebuffer(0,0,$,he,0,0,$,he,ge,r.NEAREST),u===!0&&(Fe.length=0,H.length=0,Fe.push(r.COLOR_ATTACHMENT0+ke),L.depthBuffer&&L.resolveDepthBuffer===!1&&(Fe.push(ce),H.push(ce),r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,H)),r.invalidateFramebuffer(r.READ_FRAMEBUFFER,Fe))}if(t.bindFramebuffer(r.READ_FRAMEBUFFER,null),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),we)for(let ke=0;ke<T.length;ke++){t.bindFramebuffer(r.FRAMEBUFFER,Ce.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+ke,r.RENDERBUFFER,Ce.__webglColorRenderbuffer[ke]);const Tt=n.get(T[ke]).__webglTexture;t.bindFramebuffer(r.FRAMEBUFFER,Ce.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+ke,r.TEXTURE_2D,Tt,0)}t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Ce.__webglMultisampledFramebuffer)}else if(L.depthBuffer&&L.resolveDepthBuffer===!1&&u){const T=L.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT;r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,[T])}}}function Je(L){return Math.min(i.maxSamples,L.samples)}function $e(L){const T=n.get(L);return L.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&T.__useRenderToTexture!==!1}function Oe(L){const T=a.render.frame;f.get(L)!==T&&(f.set(L,T),L.update())}function at(L,T){const $=L.colorSpace,he=L.format,ge=L.type;return L.isCompressedTexture===!0||L.isVideoTexture===!0||$!==jn&&$!==xr&&(Lt.getTransfer($)===qt?(he!==fi||ge!==rr)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",$)),T}function Be(L){return typeof HTMLImageElement<"u"&&L instanceof HTMLImageElement?(h.width=L.naturalWidth||L.width,h.height=L.naturalHeight||L.height):typeof VideoFrame<"u"&&L instanceof VideoFrame?(h.width=L.displayWidth,h.height=L.displayHeight):(h.width=L.width,h.height=L.height),h}this.allocateTextureUnit=ee,this.resetTextureUnits=J,this.setTexture2D=le,this.setTexture2DArray=Y,this.setTexture3D=de,this.setTextureCube=ne,this.rebindTextures=Qe,this.setupRenderTarget=fe,this.updateRenderTargetMipmap=Me,this.updateMultisampleRenderTarget=nt,this.setupDepthRenderbuffer=it,this.setupFrameBufferTexture=De,this.useMultisampledRTT=$e}function _P(r,e){function t(n,i=xr){let s;const a=Lt.getTransfer(i);if(n===rr)return r.UNSIGNED_BYTE;if(n===ud)return r.UNSIGNED_SHORT_4_4_4_4;if(n===hd)return r.UNSIGNED_SHORT_5_5_5_1;if(n===_g)return r.UNSIGNED_INT_5_9_9_9_REV;if(n===mg)return r.BYTE;if(n===gg)return r.SHORT;if(n===Jo)return r.UNSIGNED_SHORT;if(n===ld)return r.INT;if(n===ls)return r.UNSIGNED_INT;if(n===Ei)return r.FLOAT;if(n===ia)return r.HALF_FLOAT;if(n===vg)return r.ALPHA;if(n===yg)return r.RGB;if(n===fi)return r.RGBA;if(n===xg)return r.LUMINANCE;if(n===bg)return r.LUMINANCE_ALPHA;if(n===Ys)return r.DEPTH_COMPONENT;if(n===no)return r.DEPTH_STENCIL;if(n===dd)return r.RED;if(n===fd)return r.RED_INTEGER;if(n===Sg)return r.RG;if(n===pd)return r.RG_INTEGER;if(n===md)return r.RGBA_INTEGER;if(n===Tc||n===wc||n===Ac||n===Rc)if(a===qt)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===Tc)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===wc)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Ac)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Rc)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===Tc)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===wc)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Ac)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Rc)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Ah||n===Rh||n===Ph||n===Ch)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===Ah)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Rh)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Ph)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Ch)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Dh||n===Ih||n===Lh)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===Dh||n===Ih)return a===qt?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===Lh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Fh||n===Nh||n===Oh||n===Uh||n===Bh||n===kh||n===zh||n===Hh||n===Vh||n===Gh||n===Wh||n===jh||n===Xh||n===qh)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===Fh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Nh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Oh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Uh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Bh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===kh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===zh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Hh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Vh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Gh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Wh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===jh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Xh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===qh)return a===qt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Pc||n===Yh||n===Kh)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===Pc)return a===qt?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Yh)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Kh)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Eg||n===$h||n===Zh||n===Qh)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===Pc)return s.COMPRESSED_RED_RGTC1_EXT;if(n===$h)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===Zh)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Qh)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===to?r.UNSIGNED_INT_24_8:r[n]!==void 0?r[n]:null}return{convert:t}}class vP extends Gn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class tr extends rn{constructor(){super(),this.isGroup=!0,this.type="Group"}}const yP={type:"move"};class $u{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new tr,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new tr,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new U,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new U),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new tr,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new U,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new U),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,s=null,a=null;const c=this._targetRay,u=this._grip,h=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(h&&e.hand){a=!0;for(const E of e.hand.values()){const v=t.getJointPose(E,n),_=this._getHandJoint(h,E);v!==null&&(_.matrix.fromArray(v.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.matrixWorldNeedsUpdate=!0,_.jointRadius=v.radius),_.visible=v!==null}const f=h.joints["index-finger-tip"],p=h.joints["thumb-tip"],m=f.position.distanceTo(p.position),g=.02,x=.005;h.inputState.pinching&&m>g+x?(h.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!h.inputState.pinching&&m<=g-x&&(h.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else u!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(u.matrix.fromArray(s.transform.matrix),u.matrix.decompose(u.position,u.rotation,u.scale),u.matrixWorldNeedsUpdate=!0,s.linearVelocity?(u.hasLinearVelocity=!0,u.linearVelocity.copy(s.linearVelocity)):u.hasLinearVelocity=!1,s.angularVelocity?(u.hasAngularVelocity=!0,u.angularVelocity.copy(s.angularVelocity)):u.hasAngularVelocity=!1));c!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&s!==null&&(i=s),i!==null&&(c.matrix.fromArray(i.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,i.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(i.linearVelocity)):c.hasLinearVelocity=!1,i.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(i.angularVelocity)):c.hasAngularVelocity=!1,this.dispatchEvent(yP)))}return c!==null&&(c.visible=i!==null),u!==null&&(u.visible=s!==null),h!==null&&(h.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new tr;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const xP=`
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

}`;class SP{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const i=new wn,s=e.properties.get(i);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new Tr({vertexShader:xP,fragmentShader:bP,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Pe(new lo(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class EP extends Rr{constructor(e,t){super();const n=this;let i=null,s=1,a=null,c="local-floor",u=1,h=null,f=null,p=null,m=null,g=null,x=null;const E=new SP,v=t.getContextAttributes();let _=null,R=null;const w=[],S=[],z=new ht;let O=null;const N=new Gn;N.viewport=new Bt;const V=new Gn;V.viewport=new Bt;const D=[N,V],A=new vP;let k=null,J=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(ue){let me=w[ue];return me===void 0&&(me=new $u,w[ue]=me),me.getTargetRaySpace()},this.getControllerGrip=function(ue){let me=w[ue];return me===void 0&&(me=new $u,w[ue]=me),me.getGripSpace()},this.getHand=function(ue){let me=w[ue];return me===void 0&&(me=new $u,w[ue]=me),me.getHandSpace()};function ee(ue){const me=S.indexOf(ue.inputSource);if(me===-1)return;const De=w[me];De!==void 0&&(De.update(ue.inputSource,ue.frame,h||a),De.dispatchEvent({type:ue.type,data:ue.inputSource}))}function re(){i.removeEventListener("select",ee),i.removeEventListener("selectstart",ee),i.removeEventListener("selectend",ee),i.removeEventListener("squeeze",ee),i.removeEventListener("squeezestart",ee),i.removeEventListener("squeezeend",ee),i.removeEventListener("end",re),i.removeEventListener("inputsourceschange",le);for(let ue=0;ue<w.length;ue++){const me=S[ue];me!==null&&(S[ue]=null,w[ue].disconnect(me))}k=null,J=null,E.reset(),e.setRenderTarget(_),g=null,m=null,p=null,i=null,R=null,xt.stop(),n.isPresenting=!1,e.setPixelRatio(O),e.setSize(z.width,z.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(ue){s=ue,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(ue){c=ue,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return h||a},this.setReferenceSpace=function(ue){h=ue},this.getBaseLayer=function(){return m!==null?m:g},this.getBinding=function(){return p},this.getFrame=function(){return x},this.getSession=function(){return i},this.setSession=async function(ue){if(i=ue,i!==null){if(_=e.getRenderTarget(),i.addEventListener("select",ee),i.addEventListener("selectstart",ee),i.addEventListener("selectend",ee),i.addEventListener("squeeze",ee),i.addEventListener("squeezestart",ee),i.addEventListener("squeezeend",ee),i.addEventListener("end",re),i.addEventListener("inputsourceschange",le),v.xrCompatible!==!0&&await t.makeXRCompatible(),O=e.getPixelRatio(),e.getSize(z),i.renderState.layers===void 0){const me={antialias:v.antialias,alpha:!0,depth:v.depth,stencil:v.stencil,framebufferScaleFactor:s};g=new XRWebGLLayer(i,t,me),i.updateRenderState({baseLayer:g}),e.setPixelRatio(1),e.setSize(g.framebufferWidth,g.framebufferHeight,!1),R=new us(g.framebufferWidth,g.framebufferHeight,{format:fi,type:rr,colorSpace:e.outputColorSpace,stencilBuffer:v.stencil})}else{let me=null,De=null,Se=null;v.depth&&(Se=v.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,me=v.stencil?no:Ys,De=v.stencil?to:ls);const et={colorFormat:t.RGBA8,depthFormat:Se,scaleFactor:s};p=new XRWebGLBinding(i,t),m=p.createProjectionLayer(et),i.updateRenderState({layers:[m]}),e.setPixelRatio(1),e.setSize(m.textureWidth,m.textureHeight,!1),R=new us(m.textureWidth,m.textureHeight,{format:fi,type:rr,depthTexture:new Bg(m.textureWidth,m.textureHeight,De,void 0,void 0,void 0,void 0,void 0,void 0,me),stencilBuffer:v.stencil,colorSpace:e.outputColorSpace,samples:v.antialias?4:0,resolveDepthBuffer:m.ignoreDepthValues===!1})}R.isXRRenderTarget=!0,this.setFoveation(u),h=null,a=await i.requestReferenceSpace(c),xt.setContext(i),xt.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(i!==null)return i.environmentBlendMode},this.getDepthTexture=function(){return E.getDepthTexture()};function le(ue){for(let me=0;me<ue.removed.length;me++){const De=ue.removed[me],Se=S.indexOf(De);Se>=0&&(S[Se]=null,w[Se].disconnect(De))}for(let me=0;me<ue.added.length;me++){const De=ue.added[me];let Se=S.indexOf(De);if(Se===-1){for(let it=0;it<w.length;it++)if(it>=S.length){S.push(De),Se=it;break}else if(S[it]===null){S[it]=De,Se=it;break}if(Se===-1)break}const et=w[Se];et&&et.connect(De)}}const Y=new U,de=new U;function ne(ue,me,De){Y.setFromMatrixPosition(me.matrixWorld),de.setFromMatrixPosition(De.matrixWorld);const Se=Y.distanceTo(de),et=me.projectionMatrix.elements,it=De.projectionMatrix.elements,Qe=et[14]/(et[10]-1),fe=et[14]/(et[10]+1),Me=(et[9]+1)/et[5],Fe=(et[9]-1)/et[5],H=(et[8]-1)/et[0],nt=(it[8]+1)/it[0],Je=Qe*H,$e=Qe*nt,Oe=Se/(-H+nt),at=Oe*-H;if(me.matrixWorld.decompose(ue.position,ue.quaternion,ue.scale),ue.translateX(at),ue.translateZ(Oe),ue.matrixWorld.compose(ue.position,ue.quaternion,ue.scale),ue.matrixWorldInverse.copy(ue.matrixWorld).invert(),et[10]===-1)ue.projectionMatrix.copy(me.projectionMatrix),ue.projectionMatrixInverse.copy(me.projectionMatrixInverse);else{const Be=Qe+Oe,L=fe+Oe,T=Je-at,$=$e+(Se-at),he=Me*fe/L*Be,ge=Fe*fe/L*Be;ue.projectionMatrix.makePerspective(T,$,he,ge,Be,L),ue.projectionMatrixInverse.copy(ue.projectionMatrix).invert()}}function ye(ue,me){me===null?ue.matrixWorld.copy(ue.matrix):ue.matrixWorld.multiplyMatrices(me.matrixWorld,ue.matrix),ue.matrixWorldInverse.copy(ue.matrixWorld).invert()}this.updateCamera=function(ue){if(i===null)return;let me=ue.near,De=ue.far;E.texture!==null&&(E.depthNear>0&&(me=E.depthNear),E.depthFar>0&&(De=E.depthFar)),A.near=V.near=N.near=me,A.far=V.far=N.far=De,(k!==A.near||J!==A.far)&&(i.updateRenderState({depthNear:A.near,depthFar:A.far}),k=A.near,J=A.far),N.layers.mask=ue.layers.mask|2,V.layers.mask=ue.layers.mask|4,A.layers.mask=N.layers.mask|V.layers.mask;const Se=ue.parent,et=A.cameras;ye(A,Se);for(let it=0;it<et.length;it++)ye(et[it],Se);et.length===2?ne(A,N,V):A.projectionMatrix.copy(N.projectionMatrix),Te(ue,A,Se)};function Te(ue,me,De){De===null?ue.matrix.copy(me.matrixWorld):(ue.matrix.copy(De.matrixWorld),ue.matrix.invert(),ue.matrix.multiply(me.matrixWorld)),ue.matrix.decompose(ue.position,ue.quaternion,ue.scale),ue.updateMatrixWorld(!0),ue.projectionMatrix.copy(me.projectionMatrix),ue.projectionMatrixInverse.copy(me.projectionMatrixInverse),ue.isPerspectiveCamera&&(ue.fov=io*2*Math.atan(1/ue.projectionMatrix.elements[5]),ue.zoom=1)}this.getCamera=function(){return A},this.getFoveation=function(){if(!(m===null&&g===null))return u},this.setFoveation=function(ue){u=ue,m!==null&&(m.fixedFoveation=ue),g!==null&&g.fixedFoveation!==void 0&&(g.fixedFoveation=ue)},this.hasDepthSensing=function(){return E.texture!==null},this.getDepthSensingMesh=function(){return E.getMesh(A)};let ze=null;function We(ue,me){if(f=me.getViewerPose(h||a),x=me,f!==null){const De=f.views;g!==null&&(e.setRenderTargetFramebuffer(R,g.framebuffer),e.setRenderTarget(R));let Se=!1;De.length!==A.cameras.length&&(A.cameras.length=0,Se=!0);for(let it=0;it<De.length;it++){const Qe=De[it];let fe=null;if(g!==null)fe=g.getViewport(Qe);else{const Fe=p.getViewSubImage(m,Qe);fe=Fe.viewport,it===0&&(e.setRenderTargetTextures(R,Fe.colorTexture,m.ignoreDepthValues?void 0:Fe.depthStencilTexture),e.setRenderTarget(R))}let Me=D[it];Me===void 0&&(Me=new Gn,Me.layers.enable(it),Me.viewport=new Bt,D[it]=Me),Me.matrix.fromArray(Qe.transform.matrix),Me.matrix.decompose(Me.position,Me.quaternion,Me.scale),Me.projectionMatrix.fromArray(Qe.projectionMatrix),Me.projectionMatrixInverse.copy(Me.projectionMatrix).invert(),Me.viewport.set(fe.x,fe.y,fe.width,fe.height),it===0&&(A.matrix.copy(Me.matrix),A.matrix.decompose(A.position,A.quaternion,A.scale)),Se===!0&&A.cameras.push(Me)}const et=i.enabledFeatures;if(et&&et.includes("depth-sensing")){const it=p.getDepthInformation(De[0]);it&&it.isValid&&it.texture&&E.init(e,it,i.renderState)}}for(let De=0;De<w.length;De++){const Se=S[De],et=w[De];Se!==null&&et!==void 0&&et.update(Se,me,h||a)}ze&&ze(ue,me),me.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:me}),x=null}const xt=new Ug;xt.setAnimationLoop(We),this.setAnimationLoop=function(ue){ze=ue},this.dispose=function(){}}}const ts=new wi,MP=new pt;function TP(r,e){function t(v,_){v.matrixAutoUpdate===!0&&v.updateMatrix(),_.value.copy(v.matrix)}function n(v,_){_.color.getRGB(v.fogColor.value,Fg(r)),_.isFog?(v.fogNear.value=_.near,v.fogFar.value=_.far):_.isFogExp2&&(v.fogDensity.value=_.density)}function i(v,_,R,w,S){_.isMeshBasicMaterial||_.isMeshLambertMaterial?s(v,_):_.isMeshToonMaterial?(s(v,_),p(v,_)):_.isMeshPhongMaterial?(s(v,_),f(v,_)):_.isMeshStandardMaterial?(s(v,_),m(v,_),_.isMeshPhysicalMaterial&&g(v,_,S)):_.isMeshMatcapMaterial?(s(v,_),x(v,_)):_.isMeshDepthMaterial?s(v,_):_.isMeshDistanceMaterial?(s(v,_),E(v,_)):_.isMeshNormalMaterial?s(v,_):_.isLineBasicMaterial?(a(v,_),_.isLineDashedMaterial&&c(v,_)):_.isPointsMaterial?u(v,_,R,w):_.isSpriteMaterial?h(v,_):_.isShadowMaterial?(v.color.value.copy(_.color),v.opacity.value=_.opacity):_.isShaderMaterial&&(_.uniformsNeedUpdate=!1)}function s(v,_){v.opacity.value=_.opacity,_.color&&v.diffuse.value.copy(_.color),_.emissive&&v.emissive.value.copy(_.emissive).multiplyScalar(_.emissiveIntensity),_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.bumpMap&&(v.bumpMap.value=_.bumpMap,t(_.bumpMap,v.bumpMapTransform),v.bumpScale.value=_.bumpScale,_.side===Zn&&(v.bumpScale.value*=-1)),_.normalMap&&(v.normalMap.value=_.normalMap,t(_.normalMap,v.normalMapTransform),v.normalScale.value.copy(_.normalScale),_.side===Zn&&v.normalScale.value.negate()),_.displacementMap&&(v.displacementMap.value=_.displacementMap,t(_.displacementMap,v.displacementMapTransform),v.displacementScale.value=_.displacementScale,v.displacementBias.value=_.displacementBias),_.emissiveMap&&(v.emissiveMap.value=_.emissiveMap,t(_.emissiveMap,v.emissiveMapTransform)),_.specularMap&&(v.specularMap.value=_.specularMap,t(_.specularMap,v.specularMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest);const R=e.get(_),w=R.envMap,S=R.envMapRotation;w&&(v.envMap.value=w,ts.copy(S),ts.x*=-1,ts.y*=-1,ts.z*=-1,w.isCubeTexture&&w.isRenderTargetTexture===!1&&(ts.y*=-1,ts.z*=-1),v.envMapRotation.value.setFromMatrix4(MP.makeRotationFromEuler(ts)),v.flipEnvMap.value=w.isCubeTexture&&w.isRenderTargetTexture===!1?-1:1,v.reflectivity.value=_.reflectivity,v.ior.value=_.ior,v.refractionRatio.value=_.refractionRatio),_.lightMap&&(v.lightMap.value=_.lightMap,v.lightMapIntensity.value=_.lightMapIntensity,t(_.lightMap,v.lightMapTransform)),_.aoMap&&(v.aoMap.value=_.aoMap,v.aoMapIntensity.value=_.aoMapIntensity,t(_.aoMap,v.aoMapTransform))}function a(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform))}function c(v,_){v.dashSize.value=_.dashSize,v.totalSize.value=_.dashSize+_.gapSize,v.scale.value=_.scale}function u(v,_,R,w){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.size.value=_.size*R,v.scale.value=w*.5,_.map&&(v.map.value=_.map,t(_.map,v.uvTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function h(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.rotation.value=_.rotation,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function f(v,_){v.specular.value.copy(_.specular),v.shininess.value=Math.max(_.shininess,1e-4)}function p(v,_){_.gradientMap&&(v.gradientMap.value=_.gradientMap)}function m(v,_){v.metalness.value=_.metalness,_.metalnessMap&&(v.metalnessMap.value=_.metalnessMap,t(_.metalnessMap,v.metalnessMapTransform)),v.roughness.value=_.roughness,_.roughnessMap&&(v.roughnessMap.value=_.roughnessMap,t(_.roughnessMap,v.roughnessMapTransform)),_.envMap&&(v.envMapIntensity.value=_.envMapIntensity)}function g(v,_,R){v.ior.value=_.ior,_.sheen>0&&(v.sheenColor.value.copy(_.sheenColor).multiplyScalar(_.sheen),v.sheenRoughness.value=_.sheenRoughness,_.sheenColorMap&&(v.sheenColorMap.value=_.sheenColorMap,t(_.sheenColorMap,v.sheenColorMapTransform)),_.sheenRoughnessMap&&(v.sheenRoughnessMap.value=_.sheenRoughnessMap,t(_.sheenRoughnessMap,v.sheenRoughnessMapTransform))),_.clearcoat>0&&(v.clearcoat.value=_.clearcoat,v.clearcoatRoughness.value=_.clearcoatRoughness,_.clearcoatMap&&(v.clearcoatMap.value=_.clearcoatMap,t(_.clearcoatMap,v.clearcoatMapTransform)),_.clearcoatRoughnessMap&&(v.clearcoatRoughnessMap.value=_.clearcoatRoughnessMap,t(_.clearcoatRoughnessMap,v.clearcoatRoughnessMapTransform)),_.clearcoatNormalMap&&(v.clearcoatNormalMap.value=_.clearcoatNormalMap,t(_.clearcoatNormalMap,v.clearcoatNormalMapTransform),v.clearcoatNormalScale.value.copy(_.clearcoatNormalScale),_.side===Zn&&v.clearcoatNormalScale.value.negate())),_.dispersion>0&&(v.dispersion.value=_.dispersion),_.iridescence>0&&(v.iridescence.value=_.iridescence,v.iridescenceIOR.value=_.iridescenceIOR,v.iridescenceThicknessMinimum.value=_.iridescenceThicknessRange[0],v.iridescenceThicknessMaximum.value=_.iridescenceThicknessRange[1],_.iridescenceMap&&(v.iridescenceMap.value=_.iridescenceMap,t(_.iridescenceMap,v.iridescenceMapTransform)),_.iridescenceThicknessMap&&(v.iridescenceThicknessMap.value=_.iridescenceThicknessMap,t(_.iridescenceThicknessMap,v.iridescenceThicknessMapTransform))),_.transmission>0&&(v.transmission.value=_.transmission,v.transmissionSamplerMap.value=R.texture,v.transmissionSamplerSize.value.set(R.width,R.height),_.transmissionMap&&(v.transmissionMap.value=_.transmissionMap,t(_.transmissionMap,v.transmissionMapTransform)),v.thickness.value=_.thickness,_.thicknessMap&&(v.thicknessMap.value=_.thicknessMap,t(_.thicknessMap,v.thicknessMapTransform)),v.attenuationDistance.value=_.attenuationDistance,v.attenuationColor.value.copy(_.attenuationColor)),_.anisotropy>0&&(v.anisotropyVector.value.set(_.anisotropy*Math.cos(_.anisotropyRotation),_.anisotropy*Math.sin(_.anisotropyRotation)),_.anisotropyMap&&(v.anisotropyMap.value=_.anisotropyMap,t(_.anisotropyMap,v.anisotropyMapTransform))),v.specularIntensity.value=_.specularIntensity,v.specularColor.value.copy(_.specularColor),_.specularColorMap&&(v.specularColorMap.value=_.specularColorMap,t(_.specularColorMap,v.specularColorMapTransform)),_.specularIntensityMap&&(v.specularIntensityMap.value=_.specularIntensityMap,t(_.specularIntensityMap,v.specularIntensityMapTransform))}function x(v,_){_.matcap&&(v.matcap.value=_.matcap)}function E(v,_){const R=e.get(_).light;v.referencePosition.value.setFromMatrixPosition(R.matrixWorld),v.nearDistance.value=R.shadow.camera.near,v.farDistance.value=R.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:i}}function wP(r,e,t,n){let i={},s={},a=[];const c=r.getParameter(r.MAX_UNIFORM_BUFFER_BINDINGS);function u(R,w){const S=w.program;n.uniformBlockBinding(R,S)}function h(R,w){let S=i[R.id];S===void 0&&(x(R),S=f(R),i[R.id]=S,R.addEventListener("dispose",v));const z=w.program;n.updateUBOMapping(R,z);const O=e.render.frame;s[R.id]!==O&&(m(R),s[R.id]=O)}function f(R){const w=p();R.__bindingPointIndex=w;const S=r.createBuffer(),z=R.__size,O=R.usage;return r.bindBuffer(r.UNIFORM_BUFFER,S),r.bufferData(r.UNIFORM_BUFFER,z,O),r.bindBuffer(r.UNIFORM_BUFFER,null),r.bindBufferBase(r.UNIFORM_BUFFER,w,S),S}function p(){for(let R=0;R<c;R++)if(a.indexOf(R)===-1)return a.push(R),R;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function m(R){const w=i[R.id],S=R.uniforms,z=R.__cache;r.bindBuffer(r.UNIFORM_BUFFER,w);for(let O=0,N=S.length;O<N;O++){const V=Array.isArray(S[O])?S[O]:[S[O]];for(let D=0,A=V.length;D<A;D++){const k=V[D];if(g(k,O,D,z)===!0){const J=k.__offset,ee=Array.isArray(k.value)?k.value:[k.value];let re=0;for(let le=0;le<ee.length;le++){const Y=ee[le],de=E(Y);typeof Y=="number"||typeof Y=="boolean"?(k.__data[0]=Y,r.bufferSubData(r.UNIFORM_BUFFER,J+re,k.__data)):Y.isMatrix3?(k.__data[0]=Y.elements[0],k.__data[1]=Y.elements[1],k.__data[2]=Y.elements[2],k.__data[3]=0,k.__data[4]=Y.elements[3],k.__data[5]=Y.elements[4],k.__data[6]=Y.elements[5],k.__data[7]=0,k.__data[8]=Y.elements[6],k.__data[9]=Y.elements[7],k.__data[10]=Y.elements[8],k.__data[11]=0):(Y.toArray(k.__data,re),re+=de.storage/Float32Array.BYTES_PER_ELEMENT)}r.bufferSubData(r.UNIFORM_BUFFER,J,k.__data)}}}r.bindBuffer(r.UNIFORM_BUFFER,null)}function g(R,w,S,z){const O=R.value,N=w+"_"+S;if(z[N]===void 0)return typeof O=="number"||typeof O=="boolean"?z[N]=O:z[N]=O.clone(),!0;{const V=z[N];if(typeof O=="number"||typeof O=="boolean"){if(V!==O)return z[N]=O,!0}else if(V.equals(O)===!1)return V.copy(O),!0}return!1}function x(R){const w=R.uniforms;let S=0;const z=16;for(let N=0,V=w.length;N<V;N++){const D=Array.isArray(w[N])?w[N]:[w[N]];for(let A=0,k=D.length;A<k;A++){const J=D[A],ee=Array.isArray(J.value)?J.value:[J.value];for(let re=0,le=ee.length;re<le;re++){const Y=ee[re],de=E(Y),ne=S%z,ye=ne%de.boundary,Te=ne+ye;S+=ye,Te!==0&&z-Te<de.storage&&(S+=z-Te),J.__data=new Float32Array(de.storage/Float32Array.BYTES_PER_ELEMENT),J.__offset=S,S+=de.storage}}}const O=S%z;return O>0&&(S+=z-O),R.__size=S,R.__cache={},this}function E(R){const w={boundary:0,storage:0};return typeof R=="number"||typeof R=="boolean"?(w.boundary=4,w.storage=4):R.isVector2?(w.boundary=8,w.storage=8):R.isVector3||R.isColor?(w.boundary=16,w.storage=12):R.isVector4?(w.boundary=16,w.storage=16):R.isMatrix3?(w.boundary=48,w.storage=48):R.isMatrix4?(w.boundary=64,w.storage=64):R.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",R),w}function v(R){const w=R.target;w.removeEventListener("dispose",v);const S=a.indexOf(w.__bindingPointIndex);a.splice(S,1),r.deleteBuffer(i[w.id]),delete i[w.id],delete s[w.id]}function _(){for(const R in i)r.deleteBuffer(i[R]);a=[],i={},s={}}return{bind:u,update:h,dispose:_}}class AP{constructor(e={}){const{canvas:t=mT(),context:n=null,depth:i=!0,stencil:s=!1,alpha:a=!1,antialias:c=!1,premultipliedAlpha:u=!0,preserveDrawingBuffer:h=!1,powerPreference:f="default",failIfMajorPerformanceCaveat:p=!1,reverseDepthBuffer:m=!1}=e;this.isWebGLRenderer=!0;let g;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");g=n.getContextAttributes().alpha}else g=a;const x=new Uint32Array(4),E=new Int32Array(4);let v=null,_=null;const R=[],w=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Tn,this.toneMapping=Mr,this.toneMappingExposure=1;const S=this;let z=!1,O=0,N=0,V=null,D=-1,A=null;const k=new Bt,J=new Bt;let ee=null;const re=new rt(0);let le=0,Y=t.width,de=t.height,ne=1,ye=null,Te=null;const ze=new Bt(0,0,Y,de),We=new Bt(0,0,Y,de);let xt=!1;const ue=new xd;let me=!1,De=!1;const Se=new pt,et=new pt,it=new U,Qe=new Bt,fe={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Me=!1;function Fe(){return V===null?ne:1}let H=n;function nt(P,q){return t.getContext(P,q)}try{const P={alpha:!0,depth:i,stencil:s,antialias:c,premultipliedAlpha:u,preserveDrawingBuffer:h,powerPreference:f,failIfMajorPerformanceCaveat:p};if("setAttribute"in t&&t.setAttribute("data-engine","three.js r170"),t.addEventListener("webglcontextlost",pe,!1),t.addEventListener("webglcontextrestored",F,!1),t.addEventListener("webglcontextcreationerror",W,!1),H===null){const q="webgl2";if(H=nt(q,P),H===null)throw nt(q)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(P){throw console.error("THREE.WebGLRenderer: "+P.message),P}let Je,$e,Oe,at,Be,L,T,$,he,ge,ce,Ce,we,ke,Tt,be,Ue,Ge,st,Ve,bt,mt,Ft,X;function Re(){Je=new I1(H),Je.init(),mt=new _P(H,Je),$e=new w1(H,Je,e,mt),Oe=new pP(H,Je),$e.reverseDepthBuffer&&m&&Oe.buffers.depth.setReversed(!0),at=new N1(H),Be=new JR,L=new gP(H,Je,Oe,Be,$e,mt,at),T=new R1(S),$=new D1(S),he=new VT(H),Ft=new M1(H,he),ge=new L1(H,he,at,Ft),ce=new U1(H,ge,he,at),st=new O1(H,$e,L),be=new A1(Be),Ce=new QR(S,T,$,Je,$e,Ft,be),we=new TP(S,Be),ke=new tP,Tt=new aP(Je),Ge=new E1(S,T,$,Oe,ce,g,u),Ue=new dP(S,ce,$e),X=new wP(H,at,$e,Oe),Ve=new T1(H,Je,at),bt=new F1(H,Je,at),at.programs=Ce.programs,S.capabilities=$e,S.extensions=Je,S.properties=Be,S.renderLists=ke,S.shadowMap=Ue,S.state=Oe,S.info=at}Re();const ae=new EP(S,H);this.xr=ae,this.getContext=function(){return H},this.getContextAttributes=function(){return H.getContextAttributes()},this.forceContextLoss=function(){const P=Je.get("WEBGL_lose_context");P&&P.loseContext()},this.forceContextRestore=function(){const P=Je.get("WEBGL_lose_context");P&&P.restoreContext()},this.getPixelRatio=function(){return ne},this.setPixelRatio=function(P){P!==void 0&&(ne=P,this.setSize(Y,de,!1))},this.getSize=function(P){return P.set(Y,de)},this.setSize=function(P,q,te=!0){if(ae.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}Y=P,de=q,t.width=Math.floor(P*ne),t.height=Math.floor(q*ne),te===!0&&(t.style.width=P+"px",t.style.height=q+"px"),this.setViewport(0,0,P,q)},this.getDrawingBufferSize=function(P){return P.set(Y*ne,de*ne).floor()},this.setDrawingBufferSize=function(P,q,te){Y=P,de=q,ne=te,t.width=Math.floor(P*te),t.height=Math.floor(q*te),this.setViewport(0,0,P,q)},this.getCurrentViewport=function(P){return P.copy(k)},this.getViewport=function(P){return P.copy(ze)},this.setViewport=function(P,q,te,Z){P.isVector4?ze.set(P.x,P.y,P.z,P.w):ze.set(P,q,te,Z),Oe.viewport(k.copy(ze).multiplyScalar(ne).round())},this.getScissor=function(P){return P.copy(We)},this.setScissor=function(P,q,te,Z){P.isVector4?We.set(P.x,P.y,P.z,P.w):We.set(P,q,te,Z),Oe.scissor(J.copy(We).multiplyScalar(ne).round())},this.getScissorTest=function(){return xt},this.setScissorTest=function(P){Oe.setScissorTest(xt=P)},this.setOpaqueSort=function(P){ye=P},this.setTransparentSort=function(P){Te=P},this.getClearColor=function(P){return P.copy(Ge.getClearColor())},this.setClearColor=function(){Ge.setClearColor.apply(Ge,arguments)},this.getClearAlpha=function(){return Ge.getClearAlpha()},this.setClearAlpha=function(){Ge.setClearAlpha.apply(Ge,arguments)},this.clear=function(P=!0,q=!0,te=!0){let Z=0;if(P){let j=!1;if(V!==null){const Ae=V.texture.format;j=Ae===md||Ae===pd||Ae===fd}if(j){const Ae=V.texture.type,Ne=Ae===rr||Ae===ls||Ae===Jo||Ae===to||Ae===ud||Ae===hd,qe=Ge.getClearColor(),Ye=Ge.getClearAlpha(),dt=qe.r,lt=qe.g,Ke=qe.b;Ne?(x[0]=dt,x[1]=lt,x[2]=Ke,x[3]=Ye,H.clearBufferuiv(H.COLOR,0,x)):(E[0]=dt,E[1]=lt,E[2]=Ke,E[3]=Ye,H.clearBufferiv(H.COLOR,0,E))}else Z|=H.COLOR_BUFFER_BIT}q&&(Z|=H.DEPTH_BUFFER_BIT),te&&(Z|=H.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),H.clear(Z)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",pe,!1),t.removeEventListener("webglcontextrestored",F,!1),t.removeEventListener("webglcontextcreationerror",W,!1),ke.dispose(),Tt.dispose(),Be.dispose(),T.dispose(),$.dispose(),ce.dispose(),Ft.dispose(),X.dispose(),Ce.dispose(),ae.dispose(),ae.removeEventListener("sessionstart",St),ae.removeEventListener("sessionend",Nt),Pt.stop()};function pe(P){P.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),z=!0}function F(){console.log("THREE.WebGLRenderer: Context Restored."),z=!1;const P=at.autoReset,q=Ue.enabled,te=Ue.autoUpdate,Z=Ue.needsUpdate,j=Ue.type;Re(),at.autoReset=P,Ue.enabled=q,Ue.autoUpdate=te,Ue.needsUpdate=Z,Ue.type=j}function W(P){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",P.statusMessage)}function ie(P){const q=P.target;q.removeEventListener("dispose",ie),ve(q)}function ve(P){je(P),Be.remove(P)}function je(P){const q=Be.get(P).programs;q!==void 0&&(q.forEach(function(te){Ce.releaseProgram(te)}),P.isShaderMaterial&&Ce.releaseShaderCache(P))}this.renderBufferDirect=function(P,q,te,Z,j,Ae){q===null&&(q=fe);const Ne=j.isMesh&&j.matrixWorld.determinant()<0,qe=In(P,q,te,Z,j);Oe.setMaterial(Z,Ne);let Ye=te.index,dt=1;if(Z.wireframe===!0){if(Ye=ge.getWireframeAttribute(te),Ye===void 0)return;dt=2}const lt=te.drawRange,Ke=te.attributes.position;let Dt=lt.start*dt,kt=(lt.start+lt.count)*dt;Ae!==null&&(Dt=Math.max(Dt,Ae.start*dt),kt=Math.min(kt,(Ae.start+Ae.count)*dt)),Ye!==null?(Dt=Math.max(Dt,0),kt=Math.min(kt,Ye.count)):Ke!=null&&(Dt=Math.max(Dt,0),kt=Math.min(kt,Ke.count));const Vt=kt-Dt;if(Vt<0||Vt===1/0)return;Ft.setup(j,Z,qe,te,Ye);let an,It=Ve;if(Ye!==null&&(an=he.get(Ye),It=bt,It.setIndex(an)),j.isMesh)Z.wireframe===!0?(Oe.setLineWidth(Z.wireframeLinewidth*Fe()),It.setMode(H.LINES)):It.setMode(H.TRIANGLES);else if(j.isLine){let Ze=Z.linewidth;Ze===void 0&&(Ze=1),Oe.setLineWidth(Ze*Fe()),j.isLineSegments?It.setMode(H.LINES):j.isLineLoop?It.setMode(H.LINE_LOOP):It.setMode(H.LINE_STRIP)}else j.isPoints?It.setMode(H.POINTS):j.isSprite&&It.setMode(H.TRIANGLES);if(j.isBatchedMesh)if(j._multiDrawInstances!==null)It.renderMultiDrawInstances(j._multiDrawStarts,j._multiDrawCounts,j._multiDrawCount,j._multiDrawInstances);else if(Je.get("WEBGL_multi_draw"))It.renderMultiDraw(j._multiDrawStarts,j._multiDrawCounts,j._multiDrawCount);else{const Ze=j._multiDrawStarts,Qn=j._multiDrawCounts,At=j._multiDrawCount,An=Ye?he.get(Ye).bytesPerElement:1,Ai=Be.get(Z).currentProgram.getUniforms();for(let dn=0;dn<At;dn++)Ai.setValue(H,"_gl_DrawID",dn),It.render(Ze[dn]/An,Qn[dn])}else if(j.isInstancedMesh)It.renderInstances(Dt,Vt,j.count);else if(te.isInstancedBufferGeometry){const Ze=te._maxInstanceCount!==void 0?te._maxInstanceCount:1/0,Qn=Math.min(te.instanceCount,Ze);It.renderInstances(Dt,Vt,Qn)}else It.render(Dt,Vt)};function _e(P,q,te){P.transparent===!0&&P.side===$n&&P.forceSinglePass===!1?(P.side=Zn,P.needsUpdate=!0,cn(P,q,te),P.side=ir,P.needsUpdate=!0,cn(P,q,te),P.side=$n):cn(P,q,te)}this.compile=function(P,q,te=null){te===null&&(te=P),_=Tt.get(te),_.init(q),w.push(_),te.traverseVisible(function(j){j.isLight&&j.layers.test(q.layers)&&(_.pushLight(j),j.castShadow&&_.pushShadow(j))}),P!==te&&P.traverseVisible(function(j){j.isLight&&j.layers.test(q.layers)&&(_.pushLight(j),j.castShadow&&_.pushShadow(j))}),_.setupLights();const Z=new Set;return P.traverse(function(j){if(!(j.isMesh||j.isPoints||j.isLine||j.isSprite))return;const Ae=j.material;if(Ae)if(Array.isArray(Ae))for(let Ne=0;Ne<Ae.length;Ne++){const qe=Ae[Ne];_e(qe,te,j),Z.add(qe)}else _e(Ae,te,j),Z.add(Ae)}),w.pop(),_=null,Z},this.compileAsync=function(P,q,te=null){const Z=this.compile(P,q,te);return new Promise(j=>{function Ae(){if(Z.forEach(function(Ne){Be.get(Ne).currentProgram.isReady()&&Z.delete(Ne)}),Z.size===0){j(P);return}setTimeout(Ae,10)}Je.get("KHR_parallel_shader_compile")!==null?Ae():setTimeout(Ae,10)})};let He=null;function ot(P){He&&He(P)}function St(){Pt.stop()}function Nt(){Pt.start()}const Pt=new Ug;Pt.setAnimationLoop(ot),typeof self<"u"&&Pt.setContext(self),this.setAnimationLoop=function(P){He=P,ae.setAnimationLoop(P),P===null?Pt.stop():Pt.start()},ae.addEventListener("sessionstart",St),ae.addEventListener("sessionend",Nt),this.render=function(P,q){if(q!==void 0&&q.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(z===!0)return;if(P.matrixWorldAutoUpdate===!0&&P.updateMatrixWorld(),q.parent===null&&q.matrixWorldAutoUpdate===!0&&q.updateMatrixWorld(),ae.enabled===!0&&ae.isPresenting===!0&&(ae.cameraAutoUpdate===!0&&ae.updateCamera(q),q=ae.getCamera()),P.isScene===!0&&P.onBeforeRender(S,P,q,V),_=Tt.get(P,w.length),_.init(q),w.push(_),et.multiplyMatrices(q.projectionMatrix,q.matrixWorldInverse),ue.setFromProjectionMatrix(et),De=this.localClippingEnabled,me=be.init(this.clippingPlanes,De),v=ke.get(P,R.length),v.init(),R.push(v),ae.enabled===!0&&ae.isPresenting===!0){const Ae=S.xr.getDepthSensingMesh();Ae!==null&&ft(Ae,q,-1/0,S.sortObjects)}ft(P,q,0,S.sortObjects),v.finish(),S.sortObjects===!0&&v.sort(ye,Te),Me=ae.enabled===!1||ae.isPresenting===!1||ae.hasDepthSensing()===!1,Me&&Ge.addToRenderList(v,P),this.info.render.frame++,me===!0&&be.beginShadows();const te=_.state.shadowsArray;Ue.render(te,P,q),me===!0&&be.endShadows(),this.info.autoReset===!0&&this.info.reset();const Z=v.opaque,j=v.transmissive;if(_.setupLights(),q.isArrayCamera){const Ae=q.cameras;if(j.length>0)for(let Ne=0,qe=Ae.length;Ne<qe;Ne++){const Ye=Ae[Ne];Qt(Z,j,P,Ye)}Me&&Ge.render(P);for(let Ne=0,qe=Ae.length;Ne<qe;Ne++){const Ye=Ae[Ne];ct(v,P,Ye,Ye.viewport)}}else j.length>0&&Qt(Z,j,P,q),Me&&Ge.render(P),ct(v,P,q);V!==null&&(L.updateMultisampleRenderTarget(V),L.updateRenderTargetMipmap(V)),P.isScene===!0&&P.onAfterRender(S,P,q),Ft.resetDefaultState(),D=-1,A=null,w.pop(),w.length>0?(_=w[w.length-1],me===!0&&be.setGlobalState(S.clippingPlanes,_.state.camera)):_=null,R.pop(),R.length>0?v=R[R.length-1]:v=null};function ft(P,q,te,Z){if(P.visible===!1)return;if(P.layers.test(q.layers)){if(P.isGroup)te=P.renderOrder;else if(P.isLOD)P.autoUpdate===!0&&P.update(q);else if(P.isLight)_.pushLight(P),P.castShadow&&_.pushShadow(P);else if(P.isSprite){if(!P.frustumCulled||ue.intersectsSprite(P)){Z&&Qe.setFromMatrixPosition(P.matrixWorld).applyMatrix4(et);const Ne=ce.update(P),qe=P.material;qe.visible&&v.push(P,Ne,qe,te,Qe.z,null)}}else if((P.isMesh||P.isLine||P.isPoints)&&(!P.frustumCulled||ue.intersectsObject(P))){const Ne=ce.update(P),qe=P.material;if(Z&&(P.boundingSphere!==void 0?(P.boundingSphere===null&&P.computeBoundingSphere(),Qe.copy(P.boundingSphere.center)):(Ne.boundingSphere===null&&Ne.computeBoundingSphere(),Qe.copy(Ne.boundingSphere.center)),Qe.applyMatrix4(P.matrixWorld).applyMatrix4(et)),Array.isArray(qe)){const Ye=Ne.groups;for(let dt=0,lt=Ye.length;dt<lt;dt++){const Ke=Ye[dt],Dt=qe[Ke.materialIndex];Dt&&Dt.visible&&v.push(P,Ne,Dt,te,Qe.z,Ke)}}else qe.visible&&v.push(P,Ne,qe,te,Qe.z,null)}}const Ae=P.children;for(let Ne=0,qe=Ae.length;Ne<qe;Ne++)ft(Ae[Ne],q,te,Z)}function ct(P,q,te,Z){const j=P.opaque,Ae=P.transmissive,Ne=P.transparent;_.setupLightsView(te),me===!0&&be.setGlobalState(S.clippingPlanes,te),Z&&Oe.viewport(k.copy(Z)),j.length>0&&vt(j,q,te),Ae.length>0&&vt(Ae,q,te),Ne.length>0&&vt(Ne,q,te),Oe.buffers.depth.setTest(!0),Oe.buffers.depth.setMask(!0),Oe.buffers.color.setMask(!0),Oe.setPolygonOffset(!1)}function Qt(P,q,te,Z){if((te.isScene===!0?te.overrideMaterial:null)!==null)return;_.state.transmissionRenderTarget[Z.id]===void 0&&(_.state.transmissionRenderTarget[Z.id]=new us(1,1,{generateMipmaps:!0,type:Je.has("EXT_color_buffer_half_float")||Je.has("EXT_color_buffer_float")?ia:rr,minFilter:Ji,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Lt.workingColorSpace}));const Ae=_.state.transmissionRenderTarget[Z.id],Ne=Z.viewport||k;Ae.setSize(Ne.z,Ne.w);const qe=S.getRenderTarget();S.setRenderTarget(Ae),S.getClearColor(re),le=S.getClearAlpha(),le<1&&S.setClearColor(16777215,.5),S.clear(),Me&&Ge.render(te);const Ye=S.toneMapping;S.toneMapping=Mr;const dt=Z.viewport;if(Z.viewport!==void 0&&(Z.viewport=void 0),_.setupLightsView(Z),me===!0&&be.setGlobalState(S.clippingPlanes,Z),vt(P,te,Z),L.updateMultisampleRenderTarget(Ae),L.updateRenderTargetMipmap(Ae),Je.has("WEBGL_multisampled_render_to_texture")===!1){let lt=!1;for(let Ke=0,Dt=q.length;Ke<Dt;Ke++){const kt=q[Ke],Vt=kt.object,an=kt.geometry,It=kt.material,Ze=kt.group;if(It.side===$n&&Vt.layers.test(Z.layers)){const Qn=It.side;It.side=Zn,It.needsUpdate=!0,Xt(Vt,te,Z,an,It,Ze),It.side=Qn,It.needsUpdate=!0,lt=!0}}lt===!0&&(L.updateMultisampleRenderTarget(Ae),L.updateRenderTargetMipmap(Ae))}S.setRenderTarget(qe),S.setClearColor(re,le),dt!==void 0&&(Z.viewport=dt),S.toneMapping=Ye}function vt(P,q,te){const Z=q.isScene===!0?q.overrideMaterial:null;for(let j=0,Ae=P.length;j<Ae;j++){const Ne=P[j],qe=Ne.object,Ye=Ne.geometry,dt=Z===null?Ne.material:Z,lt=Ne.group;qe.layers.test(te.layers)&&Xt(qe,q,te,Ye,dt,lt)}}function Xt(P,q,te,Z,j,Ae){P.onBeforeRender(S,q,te,Z,j,Ae),P.modelViewMatrix.multiplyMatrices(te.matrixWorldInverse,P.matrixWorld),P.normalMatrix.getNormalMatrix(P.modelViewMatrix),j.onBeforeRender(S,q,te,Z,P,Ae),j.transparent===!0&&j.side===$n&&j.forceSinglePass===!1?(j.side=Zn,j.needsUpdate=!0,S.renderBufferDirect(te,q,Z,j,P,Ae),j.side=ir,j.needsUpdate=!0,S.renderBufferDirect(te,q,Z,j,P,Ae),j.side=$n):S.renderBufferDirect(te,q,Z,j,P,Ae),P.onAfterRender(S,q,te,Z,j,Ae)}function cn(P,q,te){q.isScene!==!0&&(q=fe);const Z=Be.get(P),j=_.state.lights,Ae=_.state.shadowsArray,Ne=j.state.version,qe=Ce.getParameters(P,j.state,Ae,q,te),Ye=Ce.getProgramCacheKey(qe);let dt=Z.programs;Z.environment=P.isMeshStandardMaterial?q.environment:null,Z.fog=q.fog,Z.envMap=(P.isMeshStandardMaterial?$:T).get(P.envMap||Z.environment),Z.envMapRotation=Z.environment!==null&&P.envMap===null?q.environmentRotation:P.envMapRotation,dt===void 0&&(P.addEventListener("dispose",ie),dt=new Map,Z.programs=dt);let lt=dt.get(Ye);if(lt!==void 0){if(Z.currentProgram===lt&&Z.lightsStateVersion===Ne)return Ht(P,qe),lt}else qe.uniforms=Ce.getUniforms(P),P.onBeforeCompile(qe,S),lt=Ce.acquireProgram(qe,Ye),dt.set(Ye,lt),Z.uniforms=qe.uniforms;const Ke=Z.uniforms;return(!P.isShaderMaterial&&!P.isRawShaderMaterial||P.clipping===!0)&&(Ke.clippingPlanes=be.uniform),Ht(P,qe),Z.needsLights=mi(P),Z.lightsStateVersion=Ne,Z.needsLights&&(Ke.ambientLightColor.value=j.state.ambient,Ke.lightProbe.value=j.state.probe,Ke.directionalLights.value=j.state.directional,Ke.directionalLightShadows.value=j.state.directionalShadow,Ke.spotLights.value=j.state.spot,Ke.spotLightShadows.value=j.state.spotShadow,Ke.rectAreaLights.value=j.state.rectArea,Ke.ltc_1.value=j.state.rectAreaLTC1,Ke.ltc_2.value=j.state.rectAreaLTC2,Ke.pointLights.value=j.state.point,Ke.pointLightShadows.value=j.state.pointShadow,Ke.hemisphereLights.value=j.state.hemi,Ke.directionalShadowMap.value=j.state.directionalShadowMap,Ke.directionalShadowMatrix.value=j.state.directionalShadowMatrix,Ke.spotShadowMap.value=j.state.spotShadowMap,Ke.spotLightMatrix.value=j.state.spotLightMatrix,Ke.spotLightMap.value=j.state.spotLightMap,Ke.pointShadowMap.value=j.state.pointShadowMap,Ke.pointShadowMatrix.value=j.state.pointShadowMatrix),Z.currentProgram=lt,Z.uniformsList=null,lt}function Ct(P){if(P.uniformsList===null){const q=P.currentProgram.getUniforms();P.uniformsList=Cc.seqWithValue(q.seq,P.uniforms)}return P.uniformsList}function Ht(P,q){const te=Be.get(P);te.outputColorSpace=q.outputColorSpace,te.batching=q.batching,te.batchingColor=q.batchingColor,te.instancing=q.instancing,te.instancingColor=q.instancingColor,te.instancingMorph=q.instancingMorph,te.skinning=q.skinning,te.morphTargets=q.morphTargets,te.morphNormals=q.morphNormals,te.morphColors=q.morphColors,te.morphTargetsCount=q.morphTargetsCount,te.numClippingPlanes=q.numClippingPlanes,te.numIntersection=q.numClipIntersection,te.vertexAlphas=q.vertexAlphas,te.vertexTangents=q.vertexTangents,te.toneMapping=q.toneMapping}function In(P,q,te,Z,j){q.isScene!==!0&&(q=fe),L.resetTextureUnits();const Ae=q.fog,Ne=Z.isMeshStandardMaterial?q.environment:null,qe=V===null?S.outputColorSpace:V.isXRRenderTarget===!0?V.texture.colorSpace:jn,Ye=(Z.isMeshStandardMaterial?$:T).get(Z.envMap||Ne),dt=Z.vertexColors===!0&&!!te.attributes.color&&te.attributes.color.itemSize===4,lt=!!te.attributes.tangent&&(!!Z.normalMap||Z.anisotropy>0),Ke=!!te.morphAttributes.position,Dt=!!te.morphAttributes.normal,kt=!!te.morphAttributes.color;let Vt=Mr;Z.toneMapped&&(V===null||V.isXRRenderTarget===!0)&&(Vt=S.toneMapping);const an=te.morphAttributes.position||te.morphAttributes.normal||te.morphAttributes.color,It=an!==void 0?an.length:0,Ze=Be.get(Z),Qn=_.state.lights;if(me===!0&&(De===!0||P!==A)){const Ln=P===A&&Z.id===D;be.setState(Z,P,Ln)}let At=!1;Z.version===Ze.__version?(Ze.needsLights&&Ze.lightsStateVersion!==Qn.state.version||Ze.outputColorSpace!==qe||j.isBatchedMesh&&Ze.batching===!1||!j.isBatchedMesh&&Ze.batching===!0||j.isBatchedMesh&&Ze.batchingColor===!0&&j.colorTexture===null||j.isBatchedMesh&&Ze.batchingColor===!1&&j.colorTexture!==null||j.isInstancedMesh&&Ze.instancing===!1||!j.isInstancedMesh&&Ze.instancing===!0||j.isSkinnedMesh&&Ze.skinning===!1||!j.isSkinnedMesh&&Ze.skinning===!0||j.isInstancedMesh&&Ze.instancingColor===!0&&j.instanceColor===null||j.isInstancedMesh&&Ze.instancingColor===!1&&j.instanceColor!==null||j.isInstancedMesh&&Ze.instancingMorph===!0&&j.morphTexture===null||j.isInstancedMesh&&Ze.instancingMorph===!1&&j.morphTexture!==null||Ze.envMap!==Ye||Z.fog===!0&&Ze.fog!==Ae||Ze.numClippingPlanes!==void 0&&(Ze.numClippingPlanes!==be.numPlanes||Ze.numIntersection!==be.numIntersection)||Ze.vertexAlphas!==dt||Ze.vertexTangents!==lt||Ze.morphTargets!==Ke||Ze.morphNormals!==Dt||Ze.morphColors!==kt||Ze.toneMapping!==Vt||Ze.morphTargetsCount!==It)&&(At=!0):(At=!0,Ze.__version=Z.version);let An=Ze.currentProgram;At===!0&&(An=cn(Z,q,j));let Ai=!1,dn=!1,Oi=!1;const Gt=An.getUniforms(),Xn=Ze.uniforms;if(Oe.useProgram(An.program)&&(Ai=!0,dn=!0,Oi=!0),Z.id!==D&&(D=Z.id,dn=!0),Ai||A!==P){Oe.buffers.depth.getReversed()?(Se.copy(P.projectionMatrix),_T(Se),vT(Se),Gt.setValue(H,"projectionMatrix",Se)):Gt.setValue(H,"projectionMatrix",P.projectionMatrix),Gt.setValue(H,"viewMatrix",P.matrixWorldInverse);const Rn=Gt.map.cameraPosition;Rn!==void 0&&Rn.setValue(H,it.setFromMatrixPosition(P.matrixWorld)),$e.logarithmicDepthBuffer&&Gt.setValue(H,"logDepthBufFC",2/(Math.log(P.far+1)/Math.LN2)),(Z.isMeshPhongMaterial||Z.isMeshToonMaterial||Z.isMeshLambertMaterial||Z.isMeshBasicMaterial||Z.isMeshStandardMaterial||Z.isShaderMaterial)&&Gt.setValue(H,"isOrthographic",P.isOrthographicCamera===!0),A!==P&&(A=P,dn=!0,Oi=!0)}if(j.isSkinnedMesh){Gt.setOptional(H,j,"bindMatrix"),Gt.setOptional(H,j,"bindMatrixInverse");const Ln=j.skeleton;Ln&&(Ln.boneTexture===null&&Ln.computeBoneTexture(),Gt.setValue(H,"boneTexture",Ln.boneTexture,L))}j.isBatchedMesh&&(Gt.setOptional(H,j,"batchingTexture"),Gt.setValue(H,"batchingTexture",j._matricesTexture,L),Gt.setOptional(H,j,"batchingIdTexture"),Gt.setValue(H,"batchingIdTexture",j._indirectTexture,L),Gt.setOptional(H,j,"batchingColorTexture"),j._colorsTexture!==null&&Gt.setValue(H,"batchingColorTexture",j._colorsTexture,L));const Ui=te.morphAttributes;if((Ui.position!==void 0||Ui.normal!==void 0||Ui.color!==void 0)&&st.update(j,te,An),(dn||Ze.receiveShadow!==j.receiveShadow)&&(Ze.receiveShadow=j.receiveShadow,Gt.setValue(H,"receiveShadow",j.receiveShadow)),Z.isMeshGouraudMaterial&&Z.envMap!==null&&(Xn.envMap.value=Ye,Xn.flipEnvMap.value=Ye.isCubeTexture&&Ye.isRenderTargetTexture===!1?-1:1),Z.isMeshStandardMaterial&&Z.envMap===null&&q.environment!==null&&(Xn.envMapIntensity.value=q.environmentIntensity),dn&&(Gt.setValue(H,"toneMappingExposure",S.toneMappingExposure),Ze.needsLights&&ci(Xn,Oi),Ae&&Z.fog===!0&&we.refreshFogUniforms(Xn,Ae),we.refreshMaterialUniforms(Xn,Z,ne,de,_.state.transmissionRenderTarget[P.id]),Cc.upload(H,Ct(Ze),Xn,L)),Z.isShaderMaterial&&Z.uniformsNeedUpdate===!0&&(Cc.upload(H,Ct(Ze),Xn,L),Z.uniformsNeedUpdate=!1),Z.isSpriteMaterial&&Gt.setValue(H,"center",j.center),Gt.setValue(H,"modelViewMatrix",j.modelViewMatrix),Gt.setValue(H,"normalMatrix",j.normalMatrix),Gt.setValue(H,"modelMatrix",j.matrixWorld),Z.isShaderMaterial||Z.isRawShaderMaterial){const Ln=Z.uniformsGroups;for(let Rn=0,Jn=Ln.length;Rn<Jn;Rn++){const fs=Ln[Rn];X.update(fs,An),X.bind(fs,An)}}return An}function ci(P,q){P.ambientLightColor.needsUpdate=q,P.lightProbe.needsUpdate=q,P.directionalLights.needsUpdate=q,P.directionalLightShadows.needsUpdate=q,P.pointLights.needsUpdate=q,P.pointLightShadows.needsUpdate=q,P.spotLights.needsUpdate=q,P.spotLightShadows.needsUpdate=q,P.rectAreaLights.needsUpdate=q,P.hemisphereLights.needsUpdate=q}function mi(P){return P.isMeshLambertMaterial||P.isMeshToonMaterial||P.isMeshPhongMaterial||P.isMeshStandardMaterial||P.isShadowMaterial||P.isShaderMaterial&&P.lights===!0}this.getActiveCubeFace=function(){return O},this.getActiveMipmapLevel=function(){return N},this.getRenderTarget=function(){return V},this.setRenderTargetTextures=function(P,q,te){Be.get(P.texture).__webglTexture=q,Be.get(P.depthTexture).__webglTexture=te;const Z=Be.get(P);Z.__hasExternalTextures=!0,Z.__autoAllocateDepthBuffer=te===void 0,Z.__autoAllocateDepthBuffer||Je.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),Z.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(P,q){const te=Be.get(P);te.__webglFramebuffer=q,te.__useDefaultFramebuffer=q===void 0},this.setRenderTarget=function(P,q=0,te=0){V=P,O=q,N=te;let Z=!0,j=null,Ae=!1,Ne=!1;if(P){const Ye=Be.get(P);if(Ye.__useDefaultFramebuffer!==void 0)Oe.bindFramebuffer(H.FRAMEBUFFER,null),Z=!1;else if(Ye.__webglFramebuffer===void 0)L.setupRenderTarget(P);else if(Ye.__hasExternalTextures)L.rebindTextures(P,Be.get(P.texture).__webglTexture,Be.get(P.depthTexture).__webglTexture);else if(P.depthBuffer){const Ke=P.depthTexture;if(Ye.__boundDepthTexture!==Ke){if(Ke!==null&&Be.has(Ke)&&(P.width!==Ke.image.width||P.height!==Ke.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");L.setupDepthRenderbuffer(P)}}const dt=P.texture;(dt.isData3DTexture||dt.isDataArrayTexture||dt.isCompressedArrayTexture)&&(Ne=!0);const lt=Be.get(P).__webglFramebuffer;P.isWebGLCubeRenderTarget?(Array.isArray(lt[q])?j=lt[q][te]:j=lt[q],Ae=!0):P.samples>0&&L.useMultisampledRTT(P)===!1?j=Be.get(P).__webglMultisampledFramebuffer:Array.isArray(lt)?j=lt[te]:j=lt,k.copy(P.viewport),J.copy(P.scissor),ee=P.scissorTest}else k.copy(ze).multiplyScalar(ne).floor(),J.copy(We).multiplyScalar(ne).floor(),ee=xt;if(Oe.bindFramebuffer(H.FRAMEBUFFER,j)&&Z&&Oe.drawBuffers(P,j),Oe.viewport(k),Oe.scissor(J),Oe.setScissorTest(ee),Ae){const Ye=Be.get(P.texture);H.framebufferTexture2D(H.FRAMEBUFFER,H.COLOR_ATTACHMENT0,H.TEXTURE_CUBE_MAP_POSITIVE_X+q,Ye.__webglTexture,te)}else if(Ne){const Ye=Be.get(P.texture),dt=q||0;H.framebufferTextureLayer(H.FRAMEBUFFER,H.COLOR_ATTACHMENT0,Ye.__webglTexture,te||0,dt)}D=-1},this.readRenderTargetPixels=function(P,q,te,Z,j,Ae,Ne){if(!(P&&P.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let qe=Be.get(P).__webglFramebuffer;if(P.isWebGLCubeRenderTarget&&Ne!==void 0&&(qe=qe[Ne]),qe){Oe.bindFramebuffer(H.FRAMEBUFFER,qe);try{const Ye=P.texture,dt=Ye.format,lt=Ye.type;if(!$e.textureFormatReadable(dt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!$e.textureTypeReadable(lt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}q>=0&&q<=P.width-Z&&te>=0&&te<=P.height-j&&H.readPixels(q,te,Z,j,mt.convert(dt),mt.convert(lt),Ae)}finally{const Ye=V!==null?Be.get(V).__webglFramebuffer:null;Oe.bindFramebuffer(H.FRAMEBUFFER,Ye)}}},this.readRenderTargetPixelsAsync=async function(P,q,te,Z,j,Ae,Ne){if(!(P&&P.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let qe=Be.get(P).__webglFramebuffer;if(P.isWebGLCubeRenderTarget&&Ne!==void 0&&(qe=qe[Ne]),qe){const Ye=P.texture,dt=Ye.format,lt=Ye.type;if(!$e.textureFormatReadable(dt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!$e.textureTypeReadable(lt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(q>=0&&q<=P.width-Z&&te>=0&&te<=P.height-j){Oe.bindFramebuffer(H.FRAMEBUFFER,qe);const Ke=H.createBuffer();H.bindBuffer(H.PIXEL_PACK_BUFFER,Ke),H.bufferData(H.PIXEL_PACK_BUFFER,Ae.byteLength,H.STREAM_READ),H.readPixels(q,te,Z,j,mt.convert(dt),mt.convert(lt),0);const Dt=V!==null?Be.get(V).__webglFramebuffer:null;Oe.bindFramebuffer(H.FRAMEBUFFER,Dt);const kt=H.fenceSync(H.SYNC_GPU_COMMANDS_COMPLETE,0);return H.flush(),await gT(H,kt,4),H.bindBuffer(H.PIXEL_PACK_BUFFER,Ke),H.getBufferSubData(H.PIXEL_PACK_BUFFER,0,Ae),H.deleteBuffer(Ke),H.deleteSync(kt),Ae}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(P,q=null,te=0){P.isTexture!==!0&&(jo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),q=arguments[0]||null,P=arguments[1]);const Z=Math.pow(2,-te),j=Math.floor(P.image.width*Z),Ae=Math.floor(P.image.height*Z),Ne=q!==null?q.x:0,qe=q!==null?q.y:0;L.setTexture2D(P,0),H.copyTexSubImage2D(H.TEXTURE_2D,te,0,0,Ne,qe,j,Ae),Oe.unbindTexture()},this.copyTextureToTexture=function(P,q,te=null,Z=null,j=0){P.isTexture!==!0&&(jo("WebGLRenderer: copyTextureToTexture function signature has changed."),Z=arguments[0]||null,P=arguments[1],q=arguments[2],j=arguments[3]||0,te=null);let Ae,Ne,qe,Ye,dt,lt,Ke,Dt,kt;const Vt=P.isCompressedTexture?P.mipmaps[j]:P.image;te!==null?(Ae=te.max.x-te.min.x,Ne=te.max.y-te.min.y,qe=te.isBox3?te.max.z-te.min.z:1,Ye=te.min.x,dt=te.min.y,lt=te.isBox3?te.min.z:0):(Ae=Vt.width,Ne=Vt.height,qe=Vt.depth||1,Ye=0,dt=0,lt=0),Z!==null?(Ke=Z.x,Dt=Z.y,kt=Z.z):(Ke=0,Dt=0,kt=0);const an=mt.convert(q.format),It=mt.convert(q.type);let Ze;q.isData3DTexture?(L.setTexture3D(q,0),Ze=H.TEXTURE_3D):q.isDataArrayTexture||q.isCompressedArrayTexture?(L.setTexture2DArray(q,0),Ze=H.TEXTURE_2D_ARRAY):(L.setTexture2D(q,0),Ze=H.TEXTURE_2D),H.pixelStorei(H.UNPACK_FLIP_Y_WEBGL,q.flipY),H.pixelStorei(H.UNPACK_PREMULTIPLY_ALPHA_WEBGL,q.premultiplyAlpha),H.pixelStorei(H.UNPACK_ALIGNMENT,q.unpackAlignment);const Qn=H.getParameter(H.UNPACK_ROW_LENGTH),At=H.getParameter(H.UNPACK_IMAGE_HEIGHT),An=H.getParameter(H.UNPACK_SKIP_PIXELS),Ai=H.getParameter(H.UNPACK_SKIP_ROWS),dn=H.getParameter(H.UNPACK_SKIP_IMAGES);H.pixelStorei(H.UNPACK_ROW_LENGTH,Vt.width),H.pixelStorei(H.UNPACK_IMAGE_HEIGHT,Vt.height),H.pixelStorei(H.UNPACK_SKIP_PIXELS,Ye),H.pixelStorei(H.UNPACK_SKIP_ROWS,dt),H.pixelStorei(H.UNPACK_SKIP_IMAGES,lt);const Oi=P.isDataArrayTexture||P.isData3DTexture,Gt=q.isDataArrayTexture||q.isData3DTexture;if(P.isRenderTargetTexture||P.isDepthTexture){const Xn=Be.get(P),Ui=Be.get(q),Ln=Be.get(Xn.__renderTarget),Rn=Be.get(Ui.__renderTarget);Oe.bindFramebuffer(H.READ_FRAMEBUFFER,Ln.__webglFramebuffer),Oe.bindFramebuffer(H.DRAW_FRAMEBUFFER,Rn.__webglFramebuffer);for(let Jn=0;Jn<qe;Jn++)Oi&&H.framebufferTextureLayer(H.READ_FRAMEBUFFER,H.COLOR_ATTACHMENT0,Be.get(P).__webglTexture,j,lt+Jn),P.isDepthTexture?(Gt&&H.framebufferTextureLayer(H.DRAW_FRAMEBUFFER,H.COLOR_ATTACHMENT0,Be.get(q).__webglTexture,j,kt+Jn),H.blitFramebuffer(Ye,dt,Ae,Ne,Ke,Dt,Ae,Ne,H.DEPTH_BUFFER_BIT,H.NEAREST)):Gt?H.copyTexSubImage3D(Ze,j,Ke,Dt,kt+Jn,Ye,dt,Ae,Ne):H.copyTexSubImage2D(Ze,j,Ke,Dt,kt+Jn,Ye,dt,Ae,Ne);Oe.bindFramebuffer(H.READ_FRAMEBUFFER,null),Oe.bindFramebuffer(H.DRAW_FRAMEBUFFER,null)}else Gt?P.isDataTexture||P.isData3DTexture?H.texSubImage3D(Ze,j,Ke,Dt,kt,Ae,Ne,qe,an,It,Vt.data):q.isCompressedArrayTexture?H.compressedTexSubImage3D(Ze,j,Ke,Dt,kt,Ae,Ne,qe,an,Vt.data):H.texSubImage3D(Ze,j,Ke,Dt,kt,Ae,Ne,qe,an,It,Vt):P.isDataTexture?H.texSubImage2D(H.TEXTURE_2D,j,Ke,Dt,Ae,Ne,an,It,Vt.data):P.isCompressedTexture?H.compressedTexSubImage2D(H.TEXTURE_2D,j,Ke,Dt,Vt.width,Vt.height,an,Vt.data):H.texSubImage2D(H.TEXTURE_2D,j,Ke,Dt,Ae,Ne,an,It,Vt);H.pixelStorei(H.UNPACK_ROW_LENGTH,Qn),H.pixelStorei(H.UNPACK_IMAGE_HEIGHT,At),H.pixelStorei(H.UNPACK_SKIP_PIXELS,An),H.pixelStorei(H.UNPACK_SKIP_ROWS,Ai),H.pixelStorei(H.UNPACK_SKIP_IMAGES,dn),j===0&&q.generateMipmaps&&H.generateMipmap(Ze),Oe.unbindTexture()},this.copyTextureToTexture3D=function(P,q,te=null,Z=null,j=0){return P.isTexture!==!0&&(jo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),te=arguments[0]||null,Z=arguments[1]||null,P=arguments[2],q=arguments[3],j=arguments[4]||0),jo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(P,q,te,Z,j)},this.initRenderTarget=function(P){Be.get(P).__webglFramebuffer===void 0&&L.setupRenderTarget(P)},this.initTexture=function(P){P.isCubeTexture?L.setTextureCube(P,0):P.isData3DTexture?L.setTexture3D(P,0):P.isDataArrayTexture||P.isCompressedArrayTexture?L.setTexture2DArray(P,0):L.setTexture2D(P,0),Oe.unbindTexture()},this.resetState=function(){O=0,N=0,V=null,Oe.reset(),Ft.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return er}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=Lt._getDrawingBufferColorSpace(e),t.unpackColorSpace=Lt._getUnpackColorSpace()}}class Ed{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new rt(e),this.density=t}clone(){return new Ed(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class RP extends rn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new wi,this.environmentIntensity=1,this.environmentRotation=new wi,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class PP{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=ed,this.updateRanges=[],this.version=0,this.uuid=Mi()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let i=0,s=this.stride;i<s;i++)this.array[e+i]=t.array[n+i];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Mi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Mi()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Hn=new U;class Md{constructor(e,t,n,i=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=i}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Hn.fromBufferAttribute(this,t),Hn.applyMatrix4(e),this.setXYZ(t,Hn.x,Hn.y,Hn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Hn.fromBufferAttribute(this,t),Hn.applyNormalMatrix(e),this.setXYZ(t,Hn.x,Hn.y,Hn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Hn.fromBufferAttribute(this,t),Hn.transformDirection(e),this.setXYZ(t,Hn.x,Hn.y,Hn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=bi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=jt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=jt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=jt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=jt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=jt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=bi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=bi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=bi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=bi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=jt(t,this.array),n=jt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=jt(t,this.array),n=jt(n,this.array),i=jt(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=jt(t,this.array),n=jt(n,this.array),i=jt(i,this.array),s=jt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return new hn(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Md(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const Tm=new U,wm=new Bt,Am=new Bt,CP=new U,Rm=new pt,hc=new U,Zu=new Li,Pm=new pt,Qu=new co;class Gg extends Pe{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=Cp,this.bindMatrix=new pt,this.bindMatrixInverse=new pt,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new Ti),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,hc),this.boundingBox.expandByPoint(hc)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new Li),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,hc),this.boundingSphere.expandByPoint(hc)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,i=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Zu.copy(this.boundingSphere),Zu.applyMatrix4(i),e.ray.intersectsSphere(Zu)!==!1&&(Pm.copy(i).invert(),Qu.copy(e.ray).applyMatrix4(Pm),!(this.boundingBox!==null&&Qu.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,Qu)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new Bt,t=this.geometry.attributes.skinWeight;for(let n=0,i=t.count;n<i;n++){e.fromBufferAttribute(t,n);const s=1/e.manhattanLength();s!==1/0?e.multiplyScalar(s):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===Cp?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===BM?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,i=this.geometry;wm.fromBufferAttribute(i.attributes.skinIndex,e),Am.fromBufferAttribute(i.attributes.skinWeight,e),Tm.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let s=0;s<4;s++){const a=Am.getComponent(s);if(a!==0){const c=wm.getComponent(s);Rm.multiplyMatrices(n.bones[c].matrixWorld,n.boneInverses[c]),t.addScaledVector(CP.copy(Tm).applyMatrix4(Rm),a)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Vc extends rn{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Wg extends wn{constructor(e=null,t=1,n=1,i,s,a,c,u,h=Wn,f=Wn,p,m){super(null,a,c,u,h,f,i,s,p,m),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Cm=new pt,DP=new pt;class ra{constructor(e=[],t=[]){this.uuid=Mi(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,i=this.bones.length;n<i;n++)this.boneInverses.push(new pt)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new pt;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,i=this.boneTexture;for(let s=0,a=e.length;s<a;s++){const c=e[s]?e[s].matrixWorld:DP;Cm.multiplyMatrices(c,t[s]),Cm.toArray(n,s*16)}i!==null&&(i.needsUpdate=!0)}clone(){return new ra(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Wg(t,e,e,fi,Ei);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const i=this.bones[t];if(i.name===e)return i}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,i=e.bones.length;n<i;n++){const s=e.bones[n];let a=t[s];a===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",s),a=new Vc),this.bones.push(a),this.boneInverses.push(new pt().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let i=0,s=t.length;i<s;i++){const a=t[i];e.bones.push(a.uuid);const c=n[i];e.boneInverses.push(c.toArray())}return e}}class nd extends hn{constructor(e,t,n,i=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=i}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const zs=new pt,Dm=new pt,dc=[],Im=new Ti,IP=new pt,Uo=new Pe,Bo=new Li;class LP extends Pe{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new nd(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let i=0;i<n;i++)this.setMatrixAt(i,IP)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new Ti),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,zs),Im.copy(e.boundingBox).applyMatrix4(zs),this.boundingBox.union(Im)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new Li),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,zs),Bo.copy(e.boundingSphere).applyMatrix4(zs),this.boundingSphere.union(Bo)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,i=this.morphTexture.source.data.data,s=n.length+1,a=e*s+1;for(let c=0;c<n.length;c++)n[c]=i[a+c]}raycast(e,t){const n=this.matrixWorld,i=this.count;if(Uo.geometry=this.geometry,Uo.material=this.material,Uo.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Bo.copy(this.boundingSphere),Bo.applyMatrix4(n),e.ray.intersectsSphere(Bo)!==!1))for(let s=0;s<i;s++){this.getMatrixAt(s,zs),Dm.multiplyMatrices(n,zs),Uo.matrixWorld=Dm,Uo.raycast(e,dc);for(let a=0,c=dc.length;a<c;a++){const u=dc[a];u.instanceId=s,u.object=this,t.push(u)}dc.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new nd(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,i=n.length+1;this.morphTexture===null&&(this.morphTexture=new Wg(new Float32Array(i*this.count),i,this.count,dd,Ei));const s=this.morphTexture.source.data.data;let a=0;for(let h=0;h<n.length;h++)a+=n[h];const c=this.geometry.morphTargetsRelative?1:1-a,u=i*e;s[u]=c,s.set(n,u+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class Gc extends Ii{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new rt(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Uc=new U,Bc=new U,Lm=new pt,ko=new co,fc=new Li,Ju=new U,Fm=new U;class xi extends rn{constructor(e=new yn,t=new Gc){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let i=1,s=t.count;i<s;i++)Uc.fromBufferAttribute(t,i-1),Bc.fromBufferAttribute(t,i),n[i]=n[i-1],n[i]+=Uc.distanceTo(Bc);e.setAttribute("lineDistance",new Zt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),fc.copy(n.boundingSphere),fc.applyMatrix4(i),fc.radius+=s,e.ray.intersectsSphere(fc)===!1)return;Lm.copy(i).invert(),ko.copy(e.ray).applyMatrix4(Lm);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=this.isLineSegments?2:1,f=n.index,m=n.attributes.position;if(f!==null){const g=Math.max(0,a.start),x=Math.min(f.count,a.start+a.count);for(let E=g,v=x-1;E<v;E+=h){const _=f.getX(E),R=f.getX(E+1),w=pc(this,e,ko,u,_,R);w&&t.push(w)}if(this.isLineLoop){const E=f.getX(x-1),v=f.getX(g),_=pc(this,e,ko,u,E,v);_&&t.push(_)}}else{const g=Math.max(0,a.start),x=Math.min(m.count,a.start+a.count);for(let E=g,v=x-1;E<v;E+=h){const _=pc(this,e,ko,u,E,E+1);_&&t.push(_)}if(this.isLineLoop){const E=pc(this,e,ko,u,x-1,g);E&&t.push(E)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function pc(r,e,t,n,i,s){const a=r.geometry.attributes.position;if(Uc.fromBufferAttribute(a,i),Bc.fromBufferAttribute(a,s),t.distanceSqToSegment(Uc,Bc,Ju,Fm)>n)return;Ju.applyMatrix4(r.matrixWorld);const u=e.ray.origin.distanceTo(Ju);if(!(u<e.near||u>e.far))return{distance:u,point:Fm.clone().applyMatrix4(r.matrixWorld),index:i,face:null,faceIndex:null,barycoord:null,object:r}}const Nm=new U,Om=new U;class jg extends xi{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let i=0,s=t.count;i<s;i+=2)Nm.fromBufferAttribute(t,i),Om.fromBufferAttribute(t,i+1),n[i]=i===0?0:n[i-1],n[i+1]=n[i]+Nm.distanceTo(Om);e.setAttribute("lineDistance",new Zt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class FP extends xi{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class Xg extends Ii{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new rt(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Um=new pt,id=new co,mc=new Li,gc=new U;class NP extends rn{constructor(e=new yn,t=new Xg){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),mc.copy(n.boundingSphere),mc.applyMatrix4(i),mc.radius+=s,e.ray.intersectsSphere(mc)===!1)return;Um.copy(i).invert(),id.copy(e.ray).applyMatrix4(Um);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=n.index,p=n.attributes.position;if(h!==null){const m=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let x=m,E=g;x<E;x++){const v=h.getX(x);gc.fromBufferAttribute(p,v),Bm(gc,v,u,i,e,t,this)}}else{const m=Math.max(0,a.start),g=Math.min(p.count,a.start+a.count);for(let x=m,E=g;x<E;x++)gc.fromBufferAttribute(p,x),Bm(gc,x,u,i,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function Bm(r,e,t,n,i,s,a){const c=id.distanceSqToPoint(r);if(c<t){const u=new U;id.closestPointToPoint(r,u),u.applyMatrix4(n);const h=i.ray.origin.distanceTo(u);if(h<i.near||h>i.far)return;s.push({distance:h,distanceToRay:Math.sqrt(c),point:u,index:e,face:null,faceIndex:null,barycoord:null,object:a})}}class Cn extends yn{constructor(e=1,t=1,n=1,i=32,s=1,a=!1,c=0,u=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:i,heightSegments:s,openEnded:a,thetaStart:c,thetaLength:u};const h=this;i=Math.floor(i),s=Math.floor(s);const f=[],p=[],m=[],g=[];let x=0;const E=[],v=n/2;let _=0;R(),a===!1&&(e>0&&w(!0),t>0&&w(!1)),this.setIndex(f),this.setAttribute("position",new Zt(p,3)),this.setAttribute("normal",new Zt(m,3)),this.setAttribute("uv",new Zt(g,2));function R(){const S=new U,z=new U;let O=0;const N=(t-e)/n;for(let V=0;V<=s;V++){const D=[],A=V/s,k=A*(t-e)+e;for(let J=0;J<=i;J++){const ee=J/i,re=ee*u+c,le=Math.sin(re),Y=Math.cos(re);z.x=k*le,z.y=-A*n+v,z.z=k*Y,p.push(z.x,z.y,z.z),S.set(le,N,Y).normalize(),m.push(S.x,S.y,S.z),g.push(ee,1-A),D.push(x++)}E.push(D)}for(let V=0;V<i;V++)for(let D=0;D<s;D++){const A=E[D][V],k=E[D+1][V],J=E[D+1][V+1],ee=E[D][V+1];(e>0||D!==0)&&(f.push(A,k,ee),O+=3),(t>0||D!==s-1)&&(f.push(k,J,ee),O+=3)}h.addGroup(_,O,0),_+=O}function w(S){const z=x,O=new ht,N=new U;let V=0;const D=S===!0?e:t,A=S===!0?1:-1;for(let J=1;J<=i;J++)p.push(0,v*A,0),m.push(0,A,0),g.push(.5,.5),x++;const k=x;for(let J=0;J<=i;J++){const re=J/i*u+c,le=Math.cos(re),Y=Math.sin(re);N.x=D*Y,N.y=v*A,N.z=D*le,p.push(N.x,N.y,N.z),m.push(0,A,0),O.x=le*.5+.5,O.y=Y*.5*A+.5,g.push(O.x,O.y),x++}for(let J=0;J<i;J++){const ee=z+J,re=k+J;S===!0?f.push(re,re+1,ee):f.push(re+1,re,ee),V+=3}h.addGroup(_,V,S===!0?1:2),_+=V}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Cn(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Td extends Cn{constructor(e=1,t=1,n=32,i=1,s=!1,a=0,c=Math.PI*2){super(0,e,t,n,i,s,a,c),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:i,openEnded:s,thetaStart:a,thetaLength:c}}static fromJSON(e){return new Td(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class wd extends yn{constructor(e=[],t=[],n=1,i=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:i};const s=[],a=[];c(i),h(n),f(),this.setAttribute("position",new Zt(s,3)),this.setAttribute("normal",new Zt(s.slice(),3)),this.setAttribute("uv",new Zt(a,2)),i===0?this.computeVertexNormals():this.normalizeNormals();function c(R){const w=new U,S=new U,z=new U;for(let O=0;O<t.length;O+=3)g(t[O+0],w),g(t[O+1],S),g(t[O+2],z),u(w,S,z,R)}function u(R,w,S,z){const O=z+1,N=[];for(let V=0;V<=O;V++){N[V]=[];const D=R.clone().lerp(S,V/O),A=w.clone().lerp(S,V/O),k=O-V;for(let J=0;J<=k;J++)J===0&&V===O?N[V][J]=D:N[V][J]=D.clone().lerp(A,J/k)}for(let V=0;V<O;V++)for(let D=0;D<2*(O-V)-1;D++){const A=Math.floor(D/2);D%2===0?(m(N[V][A+1]),m(N[V+1][A]),m(N[V][A])):(m(N[V][A+1]),m(N[V+1][A+1]),m(N[V+1][A]))}}function h(R){const w=new U;for(let S=0;S<s.length;S+=3)w.x=s[S+0],w.y=s[S+1],w.z=s[S+2],w.normalize().multiplyScalar(R),s[S+0]=w.x,s[S+1]=w.y,s[S+2]=w.z}function f(){const R=new U;for(let w=0;w<s.length;w+=3){R.x=s[w+0],R.y=s[w+1],R.z=s[w+2];const S=v(R)/2/Math.PI+.5,z=_(R)/Math.PI+.5;a.push(S,1-z)}x(),p()}function p(){for(let R=0;R<a.length;R+=6){const w=a[R+0],S=a[R+2],z=a[R+4],O=Math.max(w,S,z),N=Math.min(w,S,z);O>.9&&N<.1&&(w<.2&&(a[R+0]+=1),S<.2&&(a[R+2]+=1),z<.2&&(a[R+4]+=1))}}function m(R){s.push(R.x,R.y,R.z)}function g(R,w){const S=R*3;w.x=e[S+0],w.y=e[S+1],w.z=e[S+2]}function x(){const R=new U,w=new U,S=new U,z=new U,O=new ht,N=new ht,V=new ht;for(let D=0,A=0;D<s.length;D+=9,A+=6){R.set(s[D+0],s[D+1],s[D+2]),w.set(s[D+3],s[D+4],s[D+5]),S.set(s[D+6],s[D+7],s[D+8]),O.set(a[A+0],a[A+1]),N.set(a[A+2],a[A+3]),V.set(a[A+4],a[A+5]),z.copy(R).add(w).add(S).divideScalar(3);const k=v(z);E(O,A+0,R,k),E(N,A+2,w,k),E(V,A+4,S,k)}}function E(R,w,S,z){z<0&&R.x===1&&(a[w]=R.x-1),S.x===0&&S.z===0&&(a[w]=z/2/Math.PI+.5)}function v(R){return Math.atan2(R.z,-R.x)}function _(R){return Math.atan2(-R.y,Math.sqrt(R.x*R.x+R.z*R.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new wd(e.vertices,e.indices,e.radius,e.details)}}class js extends wd{constructor(e=1,t=0){const n=[1,0,0,-1,0,0,0,1,0,0,-1,0,0,0,1,0,0,-1],i=[0,2,4,0,4,3,0,3,5,0,5,2,1,2,5,1,5,3,1,3,4,1,4,2];super(n,i,e,t),this.type="OctahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new js(e.radius,e.detail)}}class sa extends yn{constructor(e=1,t=32,n=16,i=0,s=Math.PI*2,a=0,c=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:i,phiLength:s,thetaStart:a,thetaLength:c},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const u=Math.min(a+c,Math.PI);let h=0;const f=[],p=new U,m=new U,g=[],x=[],E=[],v=[];for(let _=0;_<=n;_++){const R=[],w=_/n;let S=0;_===0&&a===0?S=.5/t:_===n&&u===Math.PI&&(S=-.5/t);for(let z=0;z<=t;z++){const O=z/t;p.x=-e*Math.cos(i+O*s)*Math.sin(a+w*c),p.y=e*Math.cos(a+w*c),p.z=e*Math.sin(i+O*s)*Math.sin(a+w*c),x.push(p.x,p.y,p.z),m.copy(p).normalize(),E.push(m.x,m.y,m.z),v.push(O+S,1-w),R.push(h++)}f.push(R)}for(let _=0;_<n;_++)for(let R=0;R<t;R++){const w=f[_][R+1],S=f[_][R],z=f[_+1][R],O=f[_+1][R+1];(_!==0||a>0)&&g.push(w,S,O),(_!==n-1||u<Math.PI)&&g.push(S,z,O)}this.setIndex(g),this.setAttribute("position",new Zt(x,3)),this.setAttribute("normal",new Zt(E,3)),this.setAttribute("uv",new Zt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new sa(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class cs extends yn{constructor(e=1,t=.4,n=12,i=48,s=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:i,arc:s},n=Math.floor(n),i=Math.floor(i);const a=[],c=[],u=[],h=[],f=new U,p=new U,m=new U;for(let g=0;g<=n;g++)for(let x=0;x<=i;x++){const E=x/i*s,v=g/n*Math.PI*2;p.x=(e+t*Math.cos(v))*Math.cos(E),p.y=(e+t*Math.cos(v))*Math.sin(E),p.z=t*Math.sin(v),c.push(p.x,p.y,p.z),f.x=e*Math.cos(E),f.y=e*Math.sin(E),m.subVectors(p,f).normalize(),u.push(m.x,m.y,m.z),h.push(x/i),h.push(g/n)}for(let g=1;g<=n;g++)for(let x=1;x<=i;x++){const E=(i+1)*g+x-1,v=(i+1)*(g-1)+x-1,_=(i+1)*(g-1)+x,R=(i+1)*g+x;a.push(E,v,R),a.push(v,_,R)}this.setIndex(a),this.setAttribute("position",new Zt(c,3)),this.setAttribute("normal",new Zt(u,3)),this.setAttribute("uv",new Zt(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new cs(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class hs extends Ii{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new rt(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new rt(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Tg,this.normalScale=new ht(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new wi,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Fi extends hs{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new ht(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return Dn(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new rt(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new rt(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new rt(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function _c(r,e,t){return!r||!t&&r.constructor===e?r:typeof e.BYTES_PER_ELEMENT=="number"?new e(r):Array.prototype.slice.call(r)}function OP(r){return ArrayBuffer.isView(r)&&!(r instanceof DataView)}function UP(r){function e(i,s){return r[i]-r[s]}const t=r.length,n=new Array(t);for(let i=0;i!==t;++i)n[i]=i;return n.sort(e),n}function km(r,e,t){const n=r.length,i=new r.constructor(n);for(let s=0,a=0;a!==n;++s){const c=t[s]*e;for(let u=0;u!==e;++u)i[a++]=r[c+u]}return i}function qg(r,e,t,n){let i=1,s=r[0];for(;s!==void 0&&s[n]===void 0;)s=r[i++];if(s===void 0)return;let a=s[n];if(a!==void 0)if(Array.isArray(a))do a=s[n],a!==void 0&&(e.push(s.time),t.push.apply(t,a)),s=r[i++];while(s!==void 0);else if(a.toArray!==void 0)do a=s[n],a!==void 0&&(e.push(s.time),a.toArray(t,t.length)),s=r[i++];while(s!==void 0);else do a=s[n],a!==void 0&&(e.push(s.time),t.push(a)),s=r[i++];while(s!==void 0)}class oa{constructor(e,t,n,i){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=i!==void 0?i:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,i=t[n],s=t[n-1];e:{t:{let a;n:{i:if(!(e<i)){for(let c=n+2;;){if(i===void 0){if(e<s)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===c)break;if(s=i,i=t[++n],e<i)break t}a=t.length;break n}if(!(e>=s)){const c=t[1];e<c&&(n=2,s=c);for(let u=n-2;;){if(s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===u)break;if(i=s,s=t[--n-1],e>=s)break t}a=n,n=0;break n}break e}for(;n<a;){const c=n+a>>>1;e<t[c]?a=c:n=c+1}if(i=t[n],s=t[n-1],s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(i===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,s,i)}return this.interpolate_(n,s,e,i)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i;for(let a=0;a!==i;++a)t[a]=n[s+a];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class BP extends oa{constructor(e,t,n,i){super(e,t,n,i),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Vs,endingEnd:Vs}}intervalChanged_(e,t,n){const i=this.parameterPositions;let s=e-2,a=e+1,c=i[s],u=i[a];if(c===void 0)switch(this.getSettings_().endingStart){case Gs:s=e,c=2*t-n;break;case Nc:s=i.length-2,c=t+i[s]-i[s+1];break;default:s=e,c=n}if(u===void 0)switch(this.getSettings_().endingEnd){case Gs:a=e,u=2*n-t;break;case Nc:a=1,u=n+i[1]-i[0];break;default:a=e-1,u=t}const h=(n-t)*.5,f=this.valueSize;this._weightPrev=h/(t-c),this._weightNext=h/(u-n),this._offsetPrev=s*f,this._offsetNext=a*f}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=this._offsetPrev,p=this._offsetNext,m=this._weightPrev,g=this._weightNext,x=(n-t)/(i-t),E=x*x,v=E*x,_=-m*v+2*m*E-m*x,R=(1+m)*v+(-1.5-2*m)*E+(-.5+m)*x+1,w=(-1-g)*v+(1.5+g)*E+.5*x,S=g*v-g*E;for(let z=0;z!==c;++z)s[z]=_*a[f+z]+R*a[h+z]+w*a[u+z]+S*a[p+z];return s}}class Yg extends oa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=(n-t)/(i-t),p=1-f;for(let m=0;m!==c;++m)s[m]=a[h+m]*p+a[u+m]*f;return s}}class kP extends oa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e){return this.copySampleValue_(e-1)}}class Ni{constructor(e,t,n,i){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=_c(t,this.TimeBufferType),this.values=_c(n,this.ValueBufferType),this.setInterpolation(i||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:_c(e.times,Array),values:_c(e.values,Array)};const i=e.getInterpolation();i!==e.DefaultInterpolation&&(n.interpolation=i)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new kP(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new Yg(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new BP(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case ea:t=this.InterpolantFactoryMethodDiscrete;break;case ta:t=this.InterpolantFactoryMethodLinear;break;case Eu:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return ea;case this.InterpolantFactoryMethodLinear:return ta;case this.InterpolantFactoryMethodSmooth:return Eu}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]*=e}return this}trim(e,t){const n=this.times,i=n.length;let s=0,a=i-1;for(;s!==i&&n[s]<e;)++s;for(;a!==-1&&n[a]>t;)--a;if(++a,s!==0||a!==i){s>=a&&(a=Math.max(a,1),s=a-1);const c=this.getValueSize();this.times=n.slice(s,a),this.values=this.values.slice(s*c,a*c)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,i=this.values,s=n.length;s===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let a=null;for(let c=0;c!==s;c++){const u=n[c];if(typeof u=="number"&&isNaN(u)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,c,u),e=!1;break}if(a!==null&&a>u){console.error("THREE.KeyframeTrack: Out of order keys.",this,c,u,a),e=!1;break}a=u}if(i!==void 0&&OP(i))for(let c=0,u=i.length;c!==u;++c){const h=i[c];if(isNaN(h)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,c,h),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),i=this.getInterpolation()===Eu,s=e.length-1;let a=1;for(let c=1;c<s;++c){let u=!1;const h=e[c],f=e[c+1];if(h!==f&&(c!==1||h!==e[0]))if(i)u=!0;else{const p=c*n,m=p-n,g=p+n;for(let x=0;x!==n;++x){const E=t[p+x];if(E!==t[m+x]||E!==t[g+x]){u=!0;break}}}if(u){if(c!==a){e[a]=e[c];const p=c*n,m=a*n;for(let g=0;g!==n;++g)t[m+g]=t[p+g]}++a}}if(s>0){e[a]=e[s];for(let c=s*n,u=a*n,h=0;h!==n;++h)t[u+h]=t[c+h];++a}return a!==e.length?(this.times=e.slice(0,a),this.values=t.slice(0,a*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,i=new n(this.name,e,t);return i.createInterpolant=this.createInterpolant,i}}Ni.prototype.TimeBufferType=Float32Array;Ni.prototype.ValueBufferType=Float32Array;Ni.prototype.DefaultInterpolation=ta;class ho extends Ni{constructor(e,t,n){super(e,t,n)}}ho.prototype.ValueTypeName="bool";ho.prototype.ValueBufferType=Array;ho.prototype.DefaultInterpolation=ea;ho.prototype.InterpolantFactoryMethodLinear=void 0;ho.prototype.InterpolantFactoryMethodSmooth=void 0;class Kg extends Ni{}Kg.prototype.ValueTypeName="color";class so extends Ni{}so.prototype.ValueTypeName="number";class zP extends oa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=(n-t)/(i-t);let h=e*c;for(let f=h+c;h!==f;h+=4)Mt.slerpFlat(s,0,a,h-c,a,h,u);return s}}class wr extends Ni{InterpolantFactoryMethodLinear(e){return new zP(this.times,this.values,this.getValueSize(),e)}}wr.prototype.ValueTypeName="quaternion";wr.prototype.InterpolantFactoryMethodSmooth=void 0;class fo extends Ni{constructor(e,t,n){super(e,t,n)}}fo.prototype.ValueTypeName="string";fo.prototype.ValueBufferType=Array;fo.prototype.DefaultInterpolation=ea;fo.prototype.InterpolantFactoryMethodLinear=void 0;fo.prototype.InterpolantFactoryMethodSmooth=void 0;class Ar extends Ni{}Ar.prototype.ValueTypeName="vector";class oo{constructor(e="",t=-1,n=[],i=_d){this.name=e,this.tracks=n,this.duration=t,this.blendMode=i,this.uuid=Mi(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,i=1/(e.fps||1);for(let a=0,c=n.length;a!==c;++a)t.push(VP(n[a]).scale(i));const s=new this(e.name,e.duration,t,e.blendMode);return s.uuid=e.uuid,s}static toJSON(e){const t=[],n=e.tracks,i={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let s=0,a=n.length;s!==a;++s)t.push(Ni.toJSON(n[s]));return i}static CreateFromMorphTargetSequence(e,t,n,i){const s=t.length,a=[];for(let c=0;c<s;c++){let u=[],h=[];u.push((c+s-1)%s,c,(c+1)%s),h.push(0,1,0);const f=UP(u);u=km(u,1,f),h=km(h,1,f),!i&&u[0]===0&&(u.push(s),h.push(h[0])),a.push(new so(".morphTargetInfluences["+t[c].name+"]",u,h).scale(1/n))}return new this(e,-1,a)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const i=e;n=i.geometry&&i.geometry.animations||i.animations}for(let i=0;i<n.length;i++)if(n[i].name===t)return n[i];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const i={},s=/^([\w-]*?)([\d]+)$/;for(let c=0,u=e.length;c<u;c++){const h=e[c],f=h.name.match(s);if(f&&f.length>1){const p=f[1];let m=i[p];m||(i[p]=m=[]),m.push(h)}}const a=[];for(const c in i)a.push(this.CreateFromMorphTargetSequence(c,i[c],t,n));return a}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(p,m,g,x,E){if(g.length!==0){const v=[],_=[];qg(g,v,_,x),v.length!==0&&E.push(new p(m,v,_))}},i=[],s=e.name||"default",a=e.fps||30,c=e.blendMode;let u=e.length||-1;const h=e.hierarchy||[];for(let p=0;p<h.length;p++){const m=h[p].keys;if(!(!m||m.length===0))if(m[0].morphTargets){const g={};let x;for(x=0;x<m.length;x++)if(m[x].morphTargets)for(let E=0;E<m[x].morphTargets.length;E++)g[m[x].morphTargets[E]]=-1;for(const E in g){const v=[],_=[];for(let R=0;R!==m[x].morphTargets.length;++R){const w=m[x];v.push(w.time),_.push(w.morphTarget===E?1:0)}i.push(new so(".morphTargetInfluence["+E+"]",v,_))}u=g.length*a}else{const g=".bones["+t[p].name+"]";n(Ar,g+".position",m,"pos",i),n(wr,g+".quaternion",m,"rot",i),n(Ar,g+".scale",m,"scl",i)}}return i.length===0?null:new this(s,u,i,c)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,i=e.length;n!==i;++n){const s=this.tracks[n];t=Math.max(t,s.times[s.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function HP(r){switch(r.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return so;case"vector":case"vector2":case"vector3":case"vector4":return Ar;case"color":return Kg;case"quaternion":return wr;case"bool":case"boolean":return ho;case"string":return fo}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+r)}function VP(r){if(r.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=HP(r.type);if(r.times===void 0){const t=[],n=[];qg(r.keys,t,n,"value"),r.times=t,r.values=n}return e.parse!==void 0?e.parse(r):new e(r.name,r.times,r.values,r.interpolation)}const Sr={enabled:!1,files:{},add:function(r,e){this.enabled!==!1&&(this.files[r]=e)},get:function(r){if(this.enabled!==!1)return this.files[r]},remove:function(r){delete this.files[r]},clear:function(){this.files={}}};class GP{constructor(e,t,n){const i=this;let s=!1,a=0,c=0,u;const h=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(f){c++,s===!1&&i.onStart!==void 0&&i.onStart(f,a,c),s=!0},this.itemEnd=function(f){a++,i.onProgress!==void 0&&i.onProgress(f,a,c),a===c&&(s=!1,i.onLoad!==void 0&&i.onLoad())},this.itemError=function(f){i.onError!==void 0&&i.onError(f)},this.resolveURL=function(f){return u?u(f):f},this.setURLModifier=function(f){return u=f,this},this.addHandler=function(f,p){return h.push(f,p),this},this.removeHandler=function(f){const p=h.indexOf(f);return p!==-1&&h.splice(p,2),this},this.getHandler=function(f){for(let p=0,m=h.length;p<m;p+=2){const g=h[p],x=h[p+1];if(g.global&&(g.lastIndex=0),g.test(f))return x}return null}}}const WP=new GP;class ds{constructor(e){this.manager=e!==void 0?e:WP,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(i,s){n.load(e,i,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}ds.DEFAULT_MATERIAL_NAME="__DEFAULT";const $i={};class jP extends Error{constructor(e,t){super(e),this.response=t}}class Ad extends ds{constructor(e){super(e)}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=Sr.get(e);if(s!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(s),this.manager.itemEnd(e)},0),s;if($i[e]!==void 0){$i[e].push({onLoad:t,onProgress:n,onError:i});return}$i[e]=[],$i[e].push({onLoad:t,onProgress:n,onError:i});const a=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),c=this.mimeType,u=this.responseType;fetch(a).then(h=>{if(h.status===200||h.status===0){if(h.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||h.body===void 0||h.body.getReader===void 0)return h;const f=$i[e],p=h.body.getReader(),m=h.headers.get("X-File-Size")||h.headers.get("Content-Length"),g=m?parseInt(m):0,x=g!==0;let E=0;const v=new ReadableStream({start(_){R();function R(){p.read().then(({done:w,value:S})=>{if(w)_.close();else{E+=S.byteLength;const z=new ProgressEvent("progress",{lengthComputable:x,loaded:E,total:g});for(let O=0,N=f.length;O<N;O++){const V=f[O];V.onProgress&&V.onProgress(z)}_.enqueue(S),R()}},w=>{_.error(w)})}}});return new Response(v)}else throw new jP(`fetch for "${h.url}" responded with ${h.status}: ${h.statusText}`,h)}).then(h=>{switch(u){case"arraybuffer":return h.arrayBuffer();case"blob":return h.blob();case"document":return h.text().then(f=>new DOMParser().parseFromString(f,c));case"json":return h.json();default:if(c===void 0)return h.text();{const p=/charset="?([^;"\s]*)"?/i.exec(c),m=p&&p[1]?p[1].toLowerCase():void 0,g=new TextDecoder(m);return h.arrayBuffer().then(x=>g.decode(x))}}}).then(h=>{Sr.add(e,h);const f=$i[e];delete $i[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onLoad&&g.onLoad(h)}}).catch(h=>{const f=$i[e];if(f===void 0)throw this.manager.itemError(e),h;delete $i[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onError&&g.onError(h)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class XP extends ds{constructor(e){super(e)}load(e,t,n,i){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=Sr.get(e);if(a!==void 0)return s.manager.itemStart(e),setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a;const c=na("img");function u(){f(),Sr.add(e,this),t&&t(this),s.manager.itemEnd(e)}function h(p){f(),i&&i(p),s.manager.itemError(e),s.manager.itemEnd(e)}function f(){c.removeEventListener("load",u,!1),c.removeEventListener("error",h,!1)}return c.addEventListener("load",u,!1),c.addEventListener("error",h,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(c.crossOrigin=this.crossOrigin),s.manager.itemStart(e),c.src=e,c}}class qP extends ds{constructor(e){super(e)}load(e,t,n,i){const s=new wn,a=new XP(this.manager);return a.setCrossOrigin(this.crossOrigin),a.setPath(this.path),a.load(e,function(c){s.image=c,s.needsUpdate=!0,t!==void 0&&t(s)},n,i),s}}class Wc extends rn{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new rt(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const eh=new pt,zm=new U,Hm=new U;class Rd{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new ht(512,512),this.map=null,this.mapPass=null,this.matrix=new pt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new xd,this._frameExtents=new ht(1,1),this._viewportCount=1,this._viewports=[new Bt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;zm.setFromMatrixPosition(e.matrixWorld),t.position.copy(zm),Hm.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Hm),t.updateMatrixWorld(),eh.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(eh),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(eh)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class YP extends Rd{constructor(){super(new Gn(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=io*2*e.angle*this.focus,i=this.mapSize.width/this.mapSize.height,s=e.distance||t.far;(n!==t.fov||i!==t.aspect||s!==t.far)&&(t.fov=n,t.aspect=i,t.far=s,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class KP extends Wc{constructor(e,t,n=0,i=Math.PI/3,s=0,a=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(rn.DEFAULT_UP),this.updateMatrix(),this.target=new rn,this.distance=n,this.angle=i,this.penumbra=s,this.decay=a,this.map=null,this.shadow=new YP}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const Vm=new pt,zo=new U,th=new U;class $P extends Rd{constructor(){super(new Gn(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new ht(4,2),this._viewportCount=6,this._viewports=[new Bt(2,1,1,1),new Bt(0,1,1,1),new Bt(3,1,1,1),new Bt(1,1,1,1),new Bt(3,0,1,1),new Bt(1,0,1,1)],this._cubeDirections=[new U(1,0,0),new U(-1,0,0),new U(0,0,1),new U(0,0,-1),new U(0,1,0),new U(0,-1,0)],this._cubeUps=[new U(0,1,0),new U(0,1,0),new U(0,1,0),new U(0,1,0),new U(0,0,1),new U(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,i=this.matrix,s=e.distance||n.far;s!==n.far&&(n.far=s,n.updateProjectionMatrix()),zo.setFromMatrixPosition(e.matrixWorld),n.position.copy(zo),th.copy(n.position),th.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(th),n.updateMatrixWorld(),i.makeTranslation(-zo.x,-zo.y,-zo.z),Vm.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Vm)}}class $g extends Wc{constructor(e,t,n=0,i=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=i,this.shadow=new $P}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class ZP extends Rd{constructor(){super(new bd(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Dc extends Wc{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(rn.DEFAULT_UP),this.updateMatrix(),this.target=new rn,this.shadow=new ZP}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class QP extends Wc{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}class Qo{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,i=e.length;n<i;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class JP extends ds{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=Sr.get(e);if(a!==void 0){if(s.manager.itemStart(e),a.then){a.then(h=>{t&&t(h),s.manager.itemEnd(e)}).catch(h=>{i&&i(h)});return}return setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a}const c={};c.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",c.headers=this.requestHeader;const u=fetch(e,c).then(function(h){return h.blob()}).then(function(h){return createImageBitmap(h,Object.assign(s.options,{colorSpaceConversion:"none"}))}).then(function(h){return Sr.add(e,h),t&&t(h),s.manager.itemEnd(e),h}).catch(function(h){i&&i(h),Sr.remove(e),s.manager.itemError(e),s.manager.itemEnd(e)});Sr.add(e,u),s.manager.itemStart(e)}}class eC{constructor(e=!0){this.autoStart=e,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=Gm(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let e=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const t=Gm();e=(t-this.oldTime)/1e3,this.oldTime=t,this.elapsedTime+=e}return e}}function Gm(){return performance.now()}class tC{constructor(e,t,n){this.binding=e,this.valueSize=n;let i,s,a;switch(t){case"quaternion":i=this._slerp,s=this._slerpAdditive,a=this._setAdditiveIdentityQuaternion,this.buffer=new Float64Array(n*6),this._workIndex=5;break;case"string":case"bool":i=this._select,s=this._select,a=this._setAdditiveIdentityOther,this.buffer=new Array(n*5);break;default:i=this._lerp,s=this._lerpAdditive,a=this._setAdditiveIdentityNumeric,this.buffer=new Float64Array(n*5)}this._mixBufferRegion=i,this._mixBufferRegionAdditive=s,this._setIdentity=a,this._origIndex=3,this._addIndex=4,this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,this.useCount=0,this.referenceCount=0}accumulate(e,t){const n=this.buffer,i=this.valueSize,s=e*i+i;let a=this.cumulativeWeight;if(a===0){for(let c=0;c!==i;++c)n[s+c]=n[c];a=t}else{a+=t;const c=t/a;this._mixBufferRegion(n,s,0,c,i)}this.cumulativeWeight=a}accumulateAdditive(e){const t=this.buffer,n=this.valueSize,i=n*this._addIndex;this.cumulativeWeightAdditive===0&&this._setIdentity(),this._mixBufferRegionAdditive(t,i,0,e,n),this.cumulativeWeightAdditive+=e}apply(e){const t=this.valueSize,n=this.buffer,i=e*t+t,s=this.cumulativeWeight,a=this.cumulativeWeightAdditive,c=this.binding;if(this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,s<1){const u=t*this._origIndex;this._mixBufferRegion(n,i,u,1-s,t)}a>0&&this._mixBufferRegionAdditive(n,i,this._addIndex*t,1,t);for(let u=t,h=t+t;u!==h;++u)if(n[u]!==n[u+t]){c.setValue(n,i);break}}saveOriginalState(){const e=this.binding,t=this.buffer,n=this.valueSize,i=n*this._origIndex;e.getValue(t,i);for(let s=n,a=i;s!==a;++s)t[s]=t[i+s%n];this._setIdentity(),this.cumulativeWeight=0,this.cumulativeWeightAdditive=0}restoreOriginalState(){const e=this.valueSize*3;this.binding.setValue(this.buffer,e)}_setAdditiveIdentityNumeric(){const e=this._addIndex*this.valueSize,t=e+this.valueSize;for(let n=e;n<t;n++)this.buffer[n]=0}_setAdditiveIdentityQuaternion(){this._setAdditiveIdentityNumeric(),this.buffer[this._addIndex*this.valueSize+3]=1}_setAdditiveIdentityOther(){const e=this._origIndex*this.valueSize,t=this._addIndex*this.valueSize;for(let n=0;n<this.valueSize;n++)this.buffer[t+n]=this.buffer[e+n]}_select(e,t,n,i,s){if(i>=.5)for(let a=0;a!==s;++a)e[t+a]=e[n+a]}_slerp(e,t,n,i){Mt.slerpFlat(e,t,e,t,e,n,i)}_slerpAdditive(e,t,n,i,s){const a=this._workIndex*s;Mt.multiplyQuaternionsFlat(e,a,e,t,e,n),Mt.slerpFlat(e,t,e,t,e,a,i)}_lerp(e,t,n,i,s){const a=1-i;for(let c=0;c!==s;++c){const u=t+c;e[u]=e[u]*a+e[n+c]*i}}_lerpAdditive(e,t,n,i,s){for(let a=0;a!==s;++a){const c=t+a;e[c]=e[c]+e[n+a]*i}}}const Pd="\\[\\]\\.:\\/",nC=new RegExp("["+Pd+"]","g"),Cd="[^"+Pd+"]",iC="[^"+Pd.replace("\\.","")+"]",rC=/((?:WC+[\/:])*)/.source.replace("WC",Cd),sC=/(WCOD+)?/.source.replace("WCOD",iC),oC=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Cd),aC=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Cd),cC=new RegExp("^"+rC+sC+oC+aC+"$"),lC=["material","materials","bones","map"];class uC{constructor(e,t,n){const i=n||zt.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,i)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,i=this._bindings[n];i!==void 0&&i.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let i=this._targetGroup.nCachedObjects_,s=n.length;i!==s;++i)n[i].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class zt{constructor(e,t,n){this.path=t,this.parsedPath=n||zt.parseTrackName(t),this.node=zt.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new zt.Composite(e,t,n):new zt(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(nC,"")}static parseTrackName(e){const t=cC.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},i=n.nodeName&&n.nodeName.lastIndexOf(".");if(i!==void 0&&i!==-1){const s=n.nodeName.substring(i+1);lC.indexOf(s)!==-1&&(n.nodeName=n.nodeName.substring(0,i),n.objectName=s)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(s){for(let a=0;a<s.length;a++){const c=s[a];if(c.name===t||c.uuid===t)return c;const u=n(c.children);if(u)return u}return null},i=n(e.children);if(i)return i}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)e[t++]=n[i]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,i=t.propertyName;let s=t.propertyIndex;if(e||(e=zt.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let h=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let f=0;f<e.length;f++)if(e[f].name===h){h=f;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(h!==void 0){if(e[h]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[h]}}const a=e[i];if(a===void 0){const h=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+h+"."+i+" but it wasn't found.",e);return}let c=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?c=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(c=this.Versioning.MatrixWorldNeedsUpdate);let u=this.BindingType.Direct;if(s!==void 0){if(i==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[s]!==void 0&&(s=e.morphTargetDictionary[s])}u=this.BindingType.ArrayElement,this.resolvedProperty=a,this.propertyIndex=s}else a.fromArray!==void 0&&a.toArray!==void 0?(u=this.BindingType.HasFromToArray,this.resolvedProperty=a):Array.isArray(a)?(u=this.BindingType.EntireArray,this.resolvedProperty=a):this.propertyName=i;this.getValue=this.GetterByBindingType[u],this.setValue=this.SetterByBindingTypeAndVersioning[u][c]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}zt.Composite=uC;zt.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};zt.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};zt.prototype.GetterByBindingType=[zt.prototype._getValue_direct,zt.prototype._getValue_array,zt.prototype._getValue_arrayElement,zt.prototype._getValue_toArray];zt.prototype.SetterByBindingTypeAndVersioning=[[zt.prototype._setValue_direct,zt.prototype._setValue_direct_setNeedsUpdate,zt.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[zt.prototype._setValue_array,zt.prototype._setValue_array_setNeedsUpdate,zt.prototype._setValue_array_setMatrixWorldNeedsUpdate],[zt.prototype._setValue_arrayElement,zt.prototype._setValue_arrayElement_setNeedsUpdate,zt.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[zt.prototype._setValue_fromArray,zt.prototype._setValue_fromArray_setNeedsUpdate,zt.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];class hC{constructor(e,t,n=null,i=t.blendMode){this._mixer=e,this._clip=t,this._localRoot=n,this.blendMode=i;const s=t.tracks,a=s.length,c=new Array(a),u={endingStart:Vs,endingEnd:Vs};for(let h=0;h!==a;++h){const f=s[h].createInterpolant(null);c[h]=f,f.settings=u}this._interpolantSettings=u,this._interpolants=c,this._propertyBindings=new Array(a),this._cacheIndex=null,this._byClipCacheIndex=null,this._timeScaleInterpolant=null,this._weightInterpolant=null,this.loop=gd,this._loopCount=-1,this._startTime=null,this.time=0,this.timeScale=1,this._effectiveTimeScale=1,this.weight=1,this._effectiveWeight=1,this.repetitions=1/0,this.paused=!1,this.enabled=!0,this.clampWhenFinished=!1,this.zeroSlopeAtStart=!0,this.zeroSlopeAtEnd=!0}play(){return this._mixer._activateAction(this),this}stop(){return this._mixer._deactivateAction(this),this.reset()}reset(){return this.paused=!1,this.enabled=!0,this.time=0,this._loopCount=-1,this._startTime=null,this.stopFading().stopWarping()}isRunning(){return this.enabled&&!this.paused&&this.timeScale!==0&&this._startTime===null&&this._mixer._isActiveAction(this)}isScheduled(){return this._mixer._isActiveAction(this)}startAt(e){return this._startTime=e,this}setLoop(e,t){return this.loop=e,this.repetitions=t,this}setEffectiveWeight(e){return this.weight=e,this._effectiveWeight=this.enabled?e:0,this.stopFading()}getEffectiveWeight(){return this._effectiveWeight}fadeIn(e){return this._scheduleFading(e,0,1)}fadeOut(e){return this._scheduleFading(e,1,0)}crossFadeFrom(e,t,n){if(e.fadeOut(t),this.fadeIn(t),n){const i=this._clip.duration,s=e._clip.duration,a=s/i,c=i/s;e.warp(1,a,t),this.warp(c,1,t)}return this}crossFadeTo(e,t,n){return e.crossFadeFrom(this,t,n)}stopFading(){const e=this._weightInterpolant;return e!==null&&(this._weightInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}setEffectiveTimeScale(e){return this.timeScale=e,this._effectiveTimeScale=this.paused?0:e,this.stopWarping()}getEffectiveTimeScale(){return this._effectiveTimeScale}setDuration(e){return this.timeScale=this._clip.duration/e,this.stopWarping()}syncWith(e){return this.time=e.time,this.timeScale=e.timeScale,this.stopWarping()}halt(e){return this.warp(this._effectiveTimeScale,0,e)}warp(e,t,n){const i=this._mixer,s=i.time,a=this.timeScale;let c=this._timeScaleInterpolant;c===null&&(c=i._lendControlInterpolant(),this._timeScaleInterpolant=c);const u=c.parameterPositions,h=c.sampleValues;return u[0]=s,u[1]=s+n,h[0]=e/a,h[1]=t/a,this}stopWarping(){const e=this._timeScaleInterpolant;return e!==null&&(this._timeScaleInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}getMixer(){return this._mixer}getClip(){return this._clip}getRoot(){return this._localRoot||this._mixer._root}_update(e,t,n,i){if(!this.enabled){this._updateWeight(e);return}const s=this._startTime;if(s!==null){const u=(e-s)*n;u<0||n===0?t=0:(this._startTime=null,t=n*u)}t*=this._updateTimeScale(e);const a=this._updateTime(t),c=this._updateWeight(e);if(c>0){const u=this._interpolants,h=this._propertyBindings;switch(this.blendMode){case HM:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulateAdditive(c);break;case _d:default:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulate(i,c)}}}_updateWeight(e){let t=0;if(this.enabled){t=this.weight;const n=this._weightInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopFading(),i===0&&(this.enabled=!1))}}return this._effectiveWeight=t,t}_updateTimeScale(e){let t=0;if(!this.paused){t=this.timeScale;const n=this._timeScaleInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopWarping(),t===0?this.paused=!0:this.timeScale=t)}}return this._effectiveTimeScale=t,t}_updateTime(e){const t=this._clip.duration,n=this.loop;let i=this.time+e,s=this._loopCount;const a=n===zM;if(e===0)return s===-1?i:a&&(s&1)===1?t-i:i;if(n===kM){s===-1&&(this._loopCount=0,this._setEndings(!0,!0,!1));e:{if(i>=t)i=t;else if(i<0)i=0;else{this.time=i;break e}this.clampWhenFinished?this.paused=!0:this.enabled=!1,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e<0?-1:1})}}else{if(s===-1&&(e>=0?(s=0,this._setEndings(!0,this.repetitions===0,a)):this._setEndings(this.repetitions===0,!0,a)),i>=t||i<0){const c=Math.floor(i/t);i-=t*c,s+=Math.abs(c);const u=this.repetitions-s;if(u<=0)this.clampWhenFinished?this.paused=!0:this.enabled=!1,i=e>0?t:0,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e>0?1:-1});else{if(u===1){const h=e<0;this._setEndings(h,!h,a)}else this._setEndings(!1,!1,a);this._loopCount=s,this.time=i,this._mixer.dispatchEvent({type:"loop",action:this,loopDelta:c})}}else this.time=i;if(a&&(s&1)===1)return t-i}return i}_setEndings(e,t,n){const i=this._interpolantSettings;n?(i.endingStart=Gs,i.endingEnd=Gs):(e?i.endingStart=this.zeroSlopeAtStart?Gs:Vs:i.endingStart=Nc,t?i.endingEnd=this.zeroSlopeAtEnd?Gs:Vs:i.endingEnd=Nc)}_scheduleFading(e,t,n){const i=this._mixer,s=i.time;let a=this._weightInterpolant;a===null&&(a=i._lendControlInterpolant(),this._weightInterpolant=a);const c=a.parameterPositions,u=a.sampleValues;return c[0]=s,u[0]=t,c[1]=s+e,u[1]=n,this}}const dC=new Float32Array(1);class Zg extends Rr{constructor(e){super(),this._root=e,this._initMemoryManager(),this._accuIndex=0,this.time=0,this.timeScale=1}_bindAction(e,t){const n=e._localRoot||this._root,i=e._clip.tracks,s=i.length,a=e._propertyBindings,c=e._interpolants,u=n.uuid,h=this._bindingsByRootAndName;let f=h[u];f===void 0&&(f={},h[u]=f);for(let p=0;p!==s;++p){const m=i[p],g=m.name;let x=f[g];if(x!==void 0)++x.referenceCount,a[p]=x;else{if(x=a[p],x!==void 0){x._cacheIndex===null&&(++x.referenceCount,this._addInactiveBinding(x,u,g));continue}const E=t&&t._propertyBindings[p].binding.parsedPath;x=new tC(zt.create(n,g,E),m.ValueTypeName,m.getValueSize()),++x.referenceCount,this._addInactiveBinding(x,u,g),a[p]=x}c[p].resultBuffer=x.buffer}}_activateAction(e){if(!this._isActiveAction(e)){if(e._cacheIndex===null){const n=(e._localRoot||this._root).uuid,i=e._clip.uuid,s=this._actionsByClip[i];this._bindAction(e,s&&s.knownActions[0]),this._addInactiveAction(e,i,n)}const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];s.useCount++===0&&(this._lendBinding(s),s.saveOriginalState())}this._lendAction(e)}}_deactivateAction(e){if(this._isActiveAction(e)){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.useCount===0&&(s.restoreOriginalState(),this._takeBackBinding(s))}this._takeBackAction(e)}}_initMemoryManager(){this._actions=[],this._nActiveActions=0,this._actionsByClip={},this._bindings=[],this._nActiveBindings=0,this._bindingsByRootAndName={},this._controlInterpolants=[],this._nActiveControlInterpolants=0;const e=this;this.stats={actions:{get total(){return e._actions.length},get inUse(){return e._nActiveActions}},bindings:{get total(){return e._bindings.length},get inUse(){return e._nActiveBindings}},controlInterpolants:{get total(){return e._controlInterpolants.length},get inUse(){return e._nActiveControlInterpolants}}}}_isActiveAction(e){const t=e._cacheIndex;return t!==null&&t<this._nActiveActions}_addInactiveAction(e,t,n){const i=this._actions,s=this._actionsByClip;let a=s[t];if(a===void 0)a={knownActions:[e],actionByRoot:{}},e._byClipCacheIndex=0,s[t]=a;else{const c=a.knownActions;e._byClipCacheIndex=c.length,c.push(e)}e._cacheIndex=i.length,i.push(e),a.actionByRoot[n]=e}_removeInactiveAction(e){const t=this._actions,n=t[t.length-1],i=e._cacheIndex;n._cacheIndex=i,t[i]=n,t.pop(),e._cacheIndex=null;const s=e._clip.uuid,a=this._actionsByClip,c=a[s],u=c.knownActions,h=u[u.length-1],f=e._byClipCacheIndex;h._byClipCacheIndex=f,u[f]=h,u.pop(),e._byClipCacheIndex=null;const p=c.actionByRoot,m=(e._localRoot||this._root).uuid;delete p[m],u.length===0&&delete a[s],this._removeInactiveBindingsForAction(e)}_removeInactiveBindingsForAction(e){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.referenceCount===0&&this._removeInactiveBinding(s)}}_lendAction(e){const t=this._actions,n=e._cacheIndex,i=this._nActiveActions++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackAction(e){const t=this._actions,n=e._cacheIndex,i=--this._nActiveActions,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_addInactiveBinding(e,t,n){const i=this._bindingsByRootAndName,s=this._bindings;let a=i[t];a===void 0&&(a={},i[t]=a),a[n]=e,e._cacheIndex=s.length,s.push(e)}_removeInactiveBinding(e){const t=this._bindings,n=e.binding,i=n.rootNode.uuid,s=n.path,a=this._bindingsByRootAndName,c=a[i],u=t[t.length-1],h=e._cacheIndex;u._cacheIndex=h,t[h]=u,t.pop(),delete c[s],Object.keys(c).length===0&&delete a[i]}_lendBinding(e){const t=this._bindings,n=e._cacheIndex,i=this._nActiveBindings++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackBinding(e){const t=this._bindings,n=e._cacheIndex,i=--this._nActiveBindings,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_lendControlInterpolant(){const e=this._controlInterpolants,t=this._nActiveControlInterpolants++;let n=e[t];return n===void 0&&(n=new Yg(new Float32Array(2),new Float32Array(2),1,dC),n.__cacheIndex=t,e[t]=n),n}_takeBackControlInterpolant(e){const t=this._controlInterpolants,n=e.__cacheIndex,i=--this._nActiveControlInterpolants,s=t[i];e.__cacheIndex=i,t[i]=e,s.__cacheIndex=n,t[n]=s}clipAction(e,t,n){const i=t||this._root,s=i.uuid;let a=typeof e=="string"?oo.findByName(i,e):e;const c=a!==null?a.uuid:e,u=this._actionsByClip[c];let h=null;if(n===void 0&&(a!==null?n=a.blendMode:n=_d),u!==void 0){const p=u.actionByRoot[s];if(p!==void 0&&p.blendMode===n)return p;h=u.knownActions[0],a===null&&(a=h._clip)}if(a===null)return null;const f=new hC(this,a,t,n);return this._bindAction(f,h),this._addInactiveAction(f,c,s),f}existingAction(e,t){const n=t||this._root,i=n.uuid,s=typeof e=="string"?oo.findByName(n,e):e,a=s?s.uuid:e,c=this._actionsByClip[a];return c!==void 0&&c.actionByRoot[i]||null}stopAllAction(){const e=this._actions,t=this._nActiveActions;for(let n=t-1;n>=0;--n)e[n].stop();return this}update(e){e*=this.timeScale;const t=this._actions,n=this._nActiveActions,i=this.time+=e,s=Math.sign(e),a=this._accuIndex^=1;for(let h=0;h!==n;++h)t[h]._update(i,e,s,a);const c=this._bindings,u=this._nActiveBindings;for(let h=0;h!==u;++h)c[h].apply(a);return this}setTime(e){this.time=0;for(let t=0;t<this._actions.length;t++)this._actions[t].time=0;return this.update(e)}getRoot(){return this._root}uncacheClip(e){const t=this._actions,n=e.uuid,i=this._actionsByClip,s=i[n];if(s!==void 0){const a=s.knownActions;for(let c=0,u=a.length;c!==u;++c){const h=a[c];this._deactivateAction(h);const f=h._cacheIndex,p=t[t.length-1];h._cacheIndex=null,h._byClipCacheIndex=null,p._cacheIndex=f,t[f]=p,t.pop(),this._removeInactiveBindingsForAction(h)}delete i[n]}}uncacheRoot(e){const t=e.uuid,n=this._actionsByClip;for(const a in n){const c=n[a].actionByRoot,u=c[t];u!==void 0&&(this._deactivateAction(u),this._removeInactiveAction(u))}const i=this._bindingsByRootAndName,s=i[t];if(s!==void 0)for(const a in s){const c=s[a];c.restoreOriginalState(),this._removeInactiveBinding(c)}}uncacheAction(e,t){const n=this.existingAction(e,t);n!==null&&(this._deactivateAction(n),this._removeInactiveAction(n))}}const Wm=new pt;class Qg{constructor(e,t,n=0,i=1/0){this.ray=new co(e,t),this.near=n,this.far=i,this.camera=null,this.layers=new yd,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Wm.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Wm),this}intersectObject(e,t=!0,n=[]){return rd(e,this,n,t),n.sort(jm),n}intersectObjects(e,t=!0,n=[]){for(let i=0,s=e.length;i<s;i++)rd(e[i],this,n,t);return n.sort(jm),n}}function jm(r,e){return r.distance-e.distance}function rd(r,e,t,n){let i=!0;if(r.layers.test(e.layers)&&r.raycast(e,t)===!1&&(i=!1),i===!0&&n===!0){const s=r.children;for(let a=0,c=s.length;a<c;a++)rd(s[a],e,t,!0)}}class Xm{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Dn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}const gr=new U,vc=new pt,nh=new pt;class Jg extends jg{constructor(e){const t=e_(e),n=new yn,i=[],s=[],a=new rt(0,0,1),c=new rt(0,1,0);for(let h=0;h<t.length;h++){const f=t[h];f.parent&&f.parent.isBone&&(i.push(0,0,0),i.push(0,0,0),s.push(a.r,a.g,a.b),s.push(c.r,c.g,c.b))}n.setAttribute("position",new Zt(i,3)),n.setAttribute("color",new Zt(s,3));const u=new Gc({vertexColors:!0,depthTest:!1,depthWrite:!1,toneMapped:!1,transparent:!0});super(n,u),this.isSkeletonHelper=!0,this.type="SkeletonHelper",this.root=e,this.bones=t,this.matrix=e.matrixWorld,this.matrixAutoUpdate=!1}updateMatrixWorld(e){const t=this.bones,n=this.geometry,i=n.getAttribute("position");nh.copy(this.root.matrixWorld).invert();for(let s=0,a=0;s<t.length;s++){const c=t[s];c.parent&&c.parent.isBone&&(vc.multiplyMatrices(nh,c.matrixWorld),gr.setFromMatrixPosition(vc),i.setXYZ(a,gr.x,gr.y,gr.z),vc.multiplyMatrices(nh,c.parent.matrixWorld),gr.setFromMatrixPosition(vc),i.setXYZ(a+1,gr.x,gr.y,gr.z),a+=2)}n.getAttribute("position").needsUpdate=!0,super.updateMatrixWorld(e)}dispose(){this.geometry.dispose(),this.material.dispose()}}function e_(r){const e=[];r.isBone===!0&&e.push(r);for(let t=0;t<r.children.length;t++)e.push.apply(e,e_(r.children[t]));return e}class t_ extends Rr{constructor(e,t=null){super(),this.object=e,this.domElement=t,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(){}disconnect(){}dispose(){}update(){}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:"170"}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__="170");class n_ extends ds{constructor(e){super(e),this.animateBonePositions=!0,this.animateBoneRotations=!0}load(e,t,n,i){const s=this,a=new Ad(s.manager);a.setPath(s.path),a.setRequestHeader(s.requestHeader),a.setWithCredentials(s.withCredentials),a.load(e,function(c){try{t(s.parse(c))}catch(u){i?i(u):console.error(u),s.manager.itemError(e)}},n,i)}parse(e){function t(g){c(g)!=="HIERARCHY"&&console.error("THREE.BVHLoader: HIERARCHY expected.");const x=[],E=i(g,c(g),x);c(g)!=="MOTION"&&console.error("THREE.BVHLoader: MOTION expected.");let v=c(g).split(/[\s]+/);const _=parseInt(v[1]);isNaN(_)&&console.error("THREE.BVHLoader: Failed to read number of frames."),v=c(g).split(/[\s]+/);const R=parseFloat(v[2]);isNaN(R)&&console.error("THREE.BVHLoader: Failed to read frame time.");for(let w=0;w<_;w++)v=c(g).split(/[\s]+/),n(v,w*R,E);return x}function n(g,x,E){if(E.type==="ENDSITE")return;const v={time:x,position:new U,rotation:new Mt};E.frames.push(v);const _=new Mt,R=new U(1,0,0),w=new U(0,1,0),S=new U(0,0,1);for(let z=0;z<E.channels.length;z++)switch(E.channels[z]){case"Xposition":v.position.x=parseFloat(g.shift().trim());break;case"Yposition":v.position.y=parseFloat(g.shift().trim());break;case"Zposition":v.position.z=parseFloat(g.shift().trim());break;case"Xrotation":_.setFromAxisAngle(R,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Yrotation":_.setFromAxisAngle(w,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Zrotation":_.setFromAxisAngle(S,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;default:console.warn("THREE.BVHLoader: Invalid channel type.")}for(let z=0;z<E.children.length;z++)n(g,x,E.children[z])}function i(g,x,E){const v={name:"",type:"",frames:[]};E.push(v);let _=x.split(/[\s]+/);_[0].toUpperCase()==="END"&&_[1].toUpperCase()==="SITE"?(v.type="ENDSITE",v.name="ENDSITE"):(v.name=_[1],v.type=_[0].toUpperCase()),c(g)!=="{"&&console.error("THREE.BVHLoader: Expected opening { after type & name"),_=c(g).split(/[\s]+/),_[0]!=="OFFSET"&&console.error("THREE.BVHLoader: Expected OFFSET but got: "+_[0]),_.length!==4&&console.error("THREE.BVHLoader: Invalid number of values for OFFSET.");const R=new U(parseFloat(_[1]),parseFloat(_[2]),parseFloat(_[3]));if((isNaN(R.x)||isNaN(R.y)||isNaN(R.z))&&console.error("THREE.BVHLoader: Invalid values of OFFSET."),v.offset=R,v.type!=="ENDSITE"){_=c(g).split(/[\s]+/),_[0]!=="CHANNELS"&&console.error("THREE.BVHLoader: Expected CHANNELS definition.");const w=parseInt(_[1]);v.channels=_.splice(2,w),v.children=[]}for(;;){const w=c(g);if(w==="}")return v;v.children.push(i(g,w,E))}}function s(g,x){const E=new Vc;if(x.push(E),E.position.add(g.offset),E.name=g.name,g.type!=="ENDSITE")for(let v=0;v<g.children.length;v++)E.add(s(g.children[v],x));return E}function a(g){const x=[];for(let E=0;E<g.length;E++){const v=g[E];if(v.type==="ENDSITE")continue;const _=[],R=[],w=[];for(let S=0;S<v.frames.length;S++){const z=v.frames[S];_.push(z.time),R.push(z.position.x+v.offset.x),R.push(z.position.y+v.offset.y),R.push(z.position.z+v.offset.z),w.push(z.rotation.x),w.push(z.rotation.y),w.push(z.rotation.z),w.push(z.rotation.w)}u.animateBonePositions&&x.push(new Ar(v.name+".position",_,R)),u.animateBoneRotations&&x.push(new wr(v.name+".quaternion",_,w))}return new oo("animation",-1,x)}function c(g){let x;for(;(x=g.shift().trim()).length===0;);return x}const u=this,h=e.split(/[\r\n]+/g),f=t(h),p=[];s(f[0],p);const m=a(f);return{skeleton:new ra(p),clip:m}}}var Di=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},ih={},qm;function _n(){return qm||(qm=1,(function(r){var e=Object.defineProperty,t=Object.defineProperties,n=Object.getOwnPropertyDescriptors,i=Object.getOwnPropertySymbols,s=Object.prototype.hasOwnProperty,a=Object.prototype.propertyIsEnumerable,c=(b,I,G)=>I in b?e(b,I,{enumerable:!0,configurable:!0,writable:!0,value:G}):b[I]=G,u=(b,I)=>{for(var G in I||(I={}))s.call(I,G)&&c(b,G,I[G]);if(i)for(var G of i(I))a.call(I,G)&&c(b,G,I[G]);return b},h=(b,I)=>t(b,n(I)),f=b=>e(b,"__esModule",{value:!0}),p=(b,I)=>{f(b);for(var G in I)e(b,G,{get:I[G],enumerable:!0})};p(r,{Atom:()=>Ma,PointerProxy:()=>Il,Ticker:()=>wa,getPointerParts:()=>Ir,isPointer:()=>Bi,isPrism:()=>vs,iterateAndCountTicks:()=>Pl,iterateOver:()=>Dl,pointer:()=>go,pointerToPrism:()=>xs,prism:()=>Or,val:()=>So});var m=Array.isArray,g=m,x=typeof Di=="object"&&Di&&Di.Object===Object&&Di,E=x,v=typeof self=="object"&&self&&self.Object===Object&&self,_=E||v||Function("return this")(),R=_,w=R.Symbol,S=w,z=Object.prototype,O=z.hasOwnProperty,N=z.toString,V=S?S.toStringTag:void 0;function D(b){var I=O.call(b,V),G=b[V];try{b[V]=void 0;var se=!0}catch{}var ut=N.call(b);return se&&(I?b[V]=G:delete b[V]),ut}var A=D,k=Object.prototype,J=k.toString;function ee(b){return J.call(b)}var re=ee,le="[object Null]",Y="[object Undefined]",de=S?S.toStringTag:void 0;function ne(b){return b==null?b===void 0?Y:le:de&&de in Object(b)?A(b):re(b)}var ye=ne;function Te(b){return b!=null&&typeof b=="object"}var ze=Te,We="[object Symbol]";function xt(b){return typeof b=="symbol"||ze(b)&&ye(b)==We}var ue=xt,me=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,De=/^\w*$/;function Se(b,I){if(g(b))return!1;var G=typeof b;return G=="number"||G=="symbol"||G=="boolean"||b==null||ue(b)?!0:De.test(b)||!me.test(b)||I!=null&&b in Object(I)}var et=Se;function it(b){var I=typeof b;return b!=null&&(I=="object"||I=="function")}var Qe=it,fe="[object AsyncFunction]",Me="[object Function]",Fe="[object GeneratorFunction]",H="[object Proxy]";function nt(b){if(!Qe(b))return!1;var I=ye(b);return I==Me||I==Fe||I==fe||I==H}var Je=nt,$e=R["__core-js_shared__"],Oe=$e,at=(function(){var b=/[^.]+$/.exec(Oe&&Oe.keys&&Oe.keys.IE_PROTO||"");return b?"Symbol(src)_1."+b:""})();function Be(b){return!!at&&at in b}var L=Be,T=Function.prototype,$=T.toString;function he(b){if(b!=null){try{return $.call(b)}catch{}try{return b+""}catch{}}return""}var ge=he,ce=/[\\^$.*+?()[\]{}|]/g,Ce=/^\[object .+?Constructor\]$/,we=Function.prototype,ke=Object.prototype,Tt=we.toString,be=ke.hasOwnProperty,Ue=RegExp("^"+Tt.call(be).replace(ce,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function Ge(b){if(!Qe(b)||L(b))return!1;var I=Je(b)?Ue:Ce;return I.test(ge(b))}var st=Ge;function Ve(b,I){return b==null?void 0:b[I]}var bt=Ve;function mt(b,I){var G=bt(b,I);return st(G)?G:void 0}var Ft=mt,X=Ft(Object,"create"),Re=X;function ae(){this.__data__=Re?Re(null):{},this.size=0}var pe=ae;function F(b){var I=this.has(b)&&delete this.__data__[b];return this.size-=I?1:0,I}var W=F,ie="__lodash_hash_undefined__",ve=Object.prototype,je=ve.hasOwnProperty;function _e(b){var I=this.__data__;if(Re){var G=I[b];return G===ie?void 0:G}return je.call(I,b)?I[b]:void 0}var He=_e,ot=Object.prototype,St=ot.hasOwnProperty;function Nt(b){var I=this.__data__;return Re?I[b]!==void 0:St.call(I,b)}var Pt=Nt,ft="__lodash_hash_undefined__";function ct(b,I){var G=this.__data__;return this.size+=this.has(b)?0:1,G[b]=Re&&I===void 0?ft:I,this}var Qt=ct;function vt(b){var I=-1,G=b==null?0:b.length;for(this.clear();++I<G;){var se=b[I];this.set(se[0],se[1])}}vt.prototype.clear=pe,vt.prototype.delete=W,vt.prototype.get=He,vt.prototype.has=Pt,vt.prototype.set=Qt;var Xt=vt;function cn(){this.__data__=[],this.size=0}var Ct=cn;function Ht(b,I){return b===I||b!==b&&I!==I}var In=Ht;function ci(b,I){for(var G=b.length;G--;)if(In(b[G][0],I))return G;return-1}var mi=ci,P=Array.prototype,q=P.splice;function te(b){var I=this.__data__,G=mi(I,b);if(G<0)return!1;var se=I.length-1;return G==se?I.pop():q.call(I,G,1),--this.size,!0}var Z=te;function j(b){var I=this.__data__,G=mi(I,b);return G<0?void 0:I[G][1]}var Ae=j;function Ne(b){return mi(this.__data__,b)>-1}var qe=Ne;function Ye(b,I){var G=this.__data__,se=mi(G,b);return se<0?(++this.size,G.push([b,I])):G[se][1]=I,this}var dt=Ye;function lt(b){var I=-1,G=b==null?0:b.length;for(this.clear();++I<G;){var se=b[I];this.set(se[0],se[1])}}lt.prototype.clear=Ct,lt.prototype.delete=Z,lt.prototype.get=Ae,lt.prototype.has=qe,lt.prototype.set=dt;var Ke=lt,Dt=Ft(R,"Map"),kt=Dt;function Vt(){this.size=0,this.__data__={hash:new Xt,map:new(kt||Ke),string:new Xt}}var an=Vt;function It(b){var I=typeof b;return I=="string"||I=="number"||I=="symbol"||I=="boolean"?b!=="__proto__":b===null}var Ze=It;function Qn(b,I){var G=b.__data__;return Ze(I)?G[typeof I=="string"?"string":"hash"]:G.map}var At=Qn;function An(b){var I=At(this,b).delete(b);return this.size-=I?1:0,I}var Ai=An;function dn(b){return At(this,b).get(b)}var Oi=dn;function Gt(b){return At(this,b).has(b)}var Xn=Gt;function Ui(b,I){var G=At(this,b),se=G.size;return G.set(b,I),this.size+=G.size==se?0:1,this}var Ln=Ui;function Rn(b){var I=-1,G=b==null?0:b.length;for(this.clear();++I<G;){var se=b[I];this.set(se[0],se[1])}}Rn.prototype.clear=an,Rn.prototype.delete=Ai,Rn.prototype.get=Oi,Rn.prototype.has=Xn,Rn.prototype.set=Ln;var Jn=Rn,fs="Expected a function";function po(b,I){if(typeof b!="function"||I!=null&&typeof I!="function")throw new TypeError(fs);var G=function(){var se=arguments,ut=I?I.apply(this,se):se[0],Ot=G.cache;if(Ot.has(ut))return Ot.get(ut);var Pn=b.apply(this,se);return G.cache=Ot.set(ut,Pn)||Ot,Pn};return G.cache=new(po.Cache||Jn),G}po.Cache=Jn;var jc=po,sr=500;function ps(b){var I=jc(b,function(se){return G.size===sr&&G.clear(),se}),G=I.cache;return I}var Xc=ps,Pr=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,qc=/\\(\\)?/g,Yc=Xc(function(b){var I=[];return b.charCodeAt(0)===46&&I.push(""),b.replace(Pr,function(G,se,ut,Ot){I.push(ut?Ot.replace(qc,"$1"):se||G)}),I}),Kc=Yc;function $c(b,I){for(var G=-1,se=b==null?0:b.length,ut=Array(se);++G<se;)ut[G]=I(b[G],G,b);return ut}var Zc=$c,Cr=S?S.prototype:void 0,aa=Cr?Cr.toString:void 0;function ca(b){if(typeof b=="string")return b;if(g(b))return Zc(b,ca)+"";if(ue(b))return aa?aa.call(b):"";var I=b+"";return I=="0"&&1/b==-1/0?"-0":I}var Qc=ca;function Jc(b){return b==null?"":Qc(b)}var el=Jc;function tl(b,I){return g(b)?b:et(b,I)?[b]:Kc(el(b))}var nl=tl;function il(b){if(typeof b=="string"||ue(b))return b;var I=b+"";return I=="0"&&1/b==-1/0?"-0":I}var or=il;function ms(b,I){I=nl(I,b);for(var G=0,se=I.length;b!=null&&G<se;)b=b[or(I[G++])];return G&&G==se?b:void 0}var rl=ms;function mo(b,I,G){var se=b==null?void 0:rl(b,I);return se===void 0?G:se}var sl=mo;function ol(b,I){return function(G){return b(I(G))}}var al=ol,cl=al(Object.getPrototypeOf,Object),ll=cl,ul="[object Object]",hl=Function.prototype,dl=Object.prototype,la=hl.toString,fl=dl.hasOwnProperty,ua=la.call(Object);function ha(b){if(!ze(b)||ye(b)!=ul)return!1;var I=ll(b);if(I===null)return!0;var G=fl.call(I,"constructor")&&I.constructor;return typeof G=="function"&&G instanceof G&&la.call(G)==ua}var da=ha;function fa(b){var I=b==null?0:b.length;return I?b[I-1]:void 0}var pl=fa,gs=new WeakMap,pa=new WeakMap,Dr=Symbol("pointerMeta"),ml={get(b,I){if(I===Dr)return gs.get(b);let G=pa.get(b);G||(G=new Map,pa.set(b,G));const se=G.get(I);if(se!==void 0)return se;const ut=gs.get(b),Ot=_s({root:ut.root,path:[...ut.path,I]});return G.set(I,Ot),Ot}},gi=b=>b[Dr],Ir=b=>{const{root:I,path:G}=gi(b);return{root:I,path:G}};function _s(b){var I;const G={root:b.root,path:(I=b.path)!=null?I:[]},se={};return gs.set(se,G),new Proxy(se,ml)}var go=_s,Bi=b=>b&&!!gi(b);function ma(b,I,G){return I.length===0?G(b):ar(b,I,G)}var ar=(b,I,G)=>{if(I.length===0)return G(b);if(Array.isArray(b)){let[se,...ut]=I;se=parseInt(String(se),10),isNaN(se)&&(se=0);const Ot=b[se],Pn=ar(Ot,ut,G);if(Ot===Pn)return b;const li=[...b];return li.splice(se,1,Pn),li}else if(typeof b=="object"&&b!==null){const[se,...ut]=I,Ot=b[se],Pn=ar(Ot,ut,G);return Ot===Pn?b:h(u({},b),{[se]:Pn})}else{const[se,...ut]=I;return{[se]:ar(void 0,ut,G)}}},mn=class{constructor(){this._head=void 0}peek(){return this._head&&this._head.data}pop(){const b=this._head;if(b)return this._head=b.next,b.data}push(b){const I={next:this._head,data:b};this._head=I}};function vs(b){return!!(b&&b.isPrism&&b.isPrism===!0)}function _o(){const b=()=>{},I=new mn,G=b;return{type:"Dataverse_discoveryMechanism",startIgnoringDependencies:()=>{I.push(G)},stopIgnoringDependencies:()=>{I.peek()!==G||I.pop()},reportResolutionStart:cr=>{const Ur=I.peek();Ur&&Ur(cr),I.push(G)},reportResolutionEnd:cr=>{I.pop()},pushCollector:cr=>{I.push(cr)},popCollector:cr=>{if(I.peek()!==cr)throw new Error("Popped collector is not on top of the stack");I.pop()}}}function gl(){const b="__dataverse_discoveryMechanism_sharedStack",I=typeof window<"u"?window:typeof Di<"u"?Di:{};if(I){const G=I[b];if(G&&typeof G=="object"&&G.type==="Dataverse_discoveryMechanism")return G;{const se=_o();return I[b]=se,se}}else return _o()}var{startIgnoringDependencies:ki,stopIgnoringDependencies:Lr,reportResolutionEnd:_l,reportResolutionStart:vl,pushCollector:vo,popCollector:yl}=gl(),ga=()=>{},xl=class{constructor(b,I){this._fn=b,this._prismInstance=I,this._didMarkDependentsAsStale=!1,this._isFresh=!1,this._cacheOfDendencyValues=new Map,this._dependents=new Set,this._dependencies=new Set,this._possiblyStaleDeps=new Set,this._scope=new _a(this),this._lastValue=void 0,this._forciblySetToStale=!1,this._reactToDependencyGoingStale=G=>{this._possiblyStaleDeps.add(G),this._markAsStale()};for(const G of this._dependencies)G._addDependent(this._reactToDependencyGoingStale);ki(),this.getValue(),Lr()}get hasDependents(){return this._dependents.size>0}removeDependent(b){this._dependents.delete(b)}addDependent(b){this._dependents.add(b)}destroy(){for(const b of this._dependencies)b._removeDependent(this._reactToDependencyGoingStale);va(this._scope)}getValue(){if(!this._isFresh){const b=this._recalculate();this._lastValue=b,this._isFresh=!0,this._didMarkDependentsAsStale=!1,this._forciblySetToStale=!1}return this._lastValue}_recalculate(){let b;if(!this._forciblySetToStale&&this._possiblyStaleDeps.size>0){let se=!1;ki();for(const ut of this._possiblyStaleDeps)if(this._cacheOfDendencyValues.get(ut)!==ut.getValue()){se=!0;break}if(Lr(),this._possiblyStaleDeps.clear(),!se)return this._lastValue}const I=new Set;this._cacheOfDendencyValues.clear();const G=se=>{I.add(se),this._addDependency(se)};vo(G),Sn.push(this._scope);try{b=this._fn()}catch(se){console.error(se)}finally{Sn.pop()!==this._scope&&console.warn("The Prism hook stack has slipped. This is a bug.")}yl(G);for(const se of this._dependencies)I.has(se)||this._removeDependency(se);this._dependencies=I,ki();for(const se of I)this._cacheOfDendencyValues.set(se,se.getValue());return Lr(),b}forceStale(){this._forciblySetToStale=!0,this._markAsStale()}_markAsStale(){if(!this._didMarkDependentsAsStale){this._didMarkDependentsAsStale=!0,this._isFresh=!1;for(const b of this._dependents)b(this._prismInstance)}}_addDependency(b){this._dependencies.has(b)||(this._dependencies.add(b),b._addDependent(this._reactToDependencyGoingStale))}_removeDependency(b){this._dependencies.has(b)&&(this._dependencies.delete(b),b._removeDependent(this._reactToDependencyGoingStale))}},yo={},bl=class{constructor(b){this._fn=b,this.isPrism=!0,this._state={hot:!1,handle:void 0}}get isHot(){return this._state.hot}onChange(b,I,G=!1){const se=()=>{b.onThisOrNextTick(Ot)};let ut=yo;const Ot=()=>{const li=this.getValue();li!==ut&&(ut=li,I(li))};return this._addDependent(se),G&&(ut=this.getValue(),I(ut)),()=>{this._removeDependent(se),b.offThisOrNextTick(Ot),b.offNextTick(Ot)}}onStale(b){const I=()=>{this._removeDependent(G)},G=()=>b();return this._addDependent(G),I}keepHot(){return this.onStale(()=>{})}_addDependent(b){this._state.hot||this._goHot(),this._state.handle.addDependent(b)}_goHot(){const b=new xl(this._fn,this);this._state={hot:!0,handle:b}}_removeDependent(b){const I=this._state;if(!I.hot)return;const G=I.handle;G.removeDependent(b),G.hasDependents||(this._state={hot:!1,handle:void 0},G.destroy())}getValue(){vl(this);const b=this._state;let I;return b.hot?I=b.handle.getValue():I=Nr(this._fn),_l(this),I}},_a=class{constructor(b){this._hotHandle=b,this._refs=new Map,this.isPrismScope=!0,this.subs={},this.effects=new Map,this.memos=new Map}ref(b,I){let G=this._refs.get(b);if(G!==void 0)return G;{const se={current:I};return this._refs.set(b,se),se}}effect(b,I,G){let se=this.effects.get(b);se===void 0&&(se={cleanup:ga,deps:void 0},this.effects.set(b,se)),ya(se.deps,G)&&(se.cleanup(),ki(),se.cleanup=ys(I,ga).value,Lr(),se.deps=G)}memo(b,I,G){let se=this.memos.get(b);return se===void 0&&(se={cachedValue:null,deps:void 0},this.memos.set(b,se)),ya(se.deps,G)&&(ki(),se.cachedValue=ys(I,void 0).value,Lr(),se.deps=G),se.cachedValue}state(b,I){const{value:G,setValue:se}=this.memo("state/"+b,()=>{const ut={current:I};return{value:ut,setValue:Pn=>{ut.current=Pn,this._hotHandle.forceStale()}}},[]);return[G.current,se]}sub(b){return this.subs[b]||(this.subs[b]=new _a(this._hotHandle)),this.subs[b]}cleanupEffects(){for(const b of this.effects.values())ys(b.cleanup,void 0);this.effects.clear()}source(b,I){return this.effect("$$source/blah",()=>b(()=>{this._hotHandle.forceStale()}),[b]),I()}};function va(b){for(const I of Object.values(b.subs))va(I);b.cleanupEffects()}function ys(b,I){try{return{value:b(),ok:!0}}catch(G){return setTimeout(function(){throw G}),{value:I,ok:!1}}}var Sn=new mn;function Sl(b,I){const G=Sn.peek();if(!G)throw new Error("prism.ref() is called outside of a prism() call.");return G.ref(b,I)}function xo(b,I,G){const se=Sn.peek();if(!se)throw new Error("prism.effect() is called outside of a prism() call.");return se.effect(b,I,G)}function ya(b,I){if(b===void 0||I===void 0)return!0;const G=b.length;if(G!==I.length)return!0;for(let se=0;se<G;se++)if(b[se]!==I[se])return!0;return!1}function xa(b,I,G){const se=Sn.peek();if(!se)throw new Error("prism.memo() is called outside of a prism() call.");return se.memo(b,I,G)}function zn(b,I){const G=Sn.peek();if(!G)throw new Error("prism.state() is called outside of a prism() call.");return G.state(b,I)}function El(){if(!Sn.peek())throw new Error("The parent function is called outside of a prism() call.")}function Ml(b,I){const G=Sn.peek();if(!G)throw new Error("prism.scope() is called outside of a prism() call.");const se=G.sub(b);Sn.push(se);const ut=ys(I,void 0).value;return Sn.pop(),ut}function Tl(b,I,G){return xa(b,()=>gn(I),G).getValue()}function ba(){return!!Sn.peek()}function wl(b,I){const G=Sn.peek();if(!G)throw new Error("prism.source() is called outside of a prism() call.");return G.source(b,I)}var gn=b=>new bl(b),Fr=class{effect(b,I,G){console.warn("prism.effect() does not run in cold prisms")}memo(b,I,G){return I()}state(b,I){return[I,()=>{}]}ref(b,I){return{current:I}}sub(b){return new Fr}source(b,I){return I()}};function Nr(b){const I=new Fr;Sn.push(I);let G;try{G=b()}catch(se){console.error(se)}finally{Sn.pop()!==I&&console.warn("The Prism hook stack has slipped. This is a bug.")}return G}gn.ref=Sl,gn.effect=xo,gn.memo=xa,gn.ensurePrism=El,gn.state=zn,gn.scope=Ml,gn.sub=Tl,gn.inPrism=ba,gn.source=wl;var Or=gn,Sa;(function(b){b[b.Dict=0]="Dict",b[b.Array=1]="Array",b[b.Other=2]="Other"})(Sa||(Sa={}));var Wt=b=>Array.isArray(b)?1:da(b)?0:2,bo=(b,I,G=Wt(b))=>G===0&&typeof I=="string"||G===1&&Al(I)?b[I]:void 0,Al=b=>{const I=typeof b=="number"?b:parseInt(b,10);return!isNaN(I)&&I>=0&&I<1/0&&(I|0)===I},Ea=class{constructor(b,I){this._parent=b,this._path=I,this.children=new Map,this.identityChangeListeners=new Set}addIdentityChangeListener(b){this.identityChangeListeners.add(b)}removeIdentityChangeListener(b){this.identityChangeListeners.delete(b),this._checkForGC()}removeChild(b){this.children.delete(b),this._checkForGC()}getChild(b){return this.children.get(b)}getOrCreateChild(b){let I=this.children.get(b);return I||(I=I=new Ea(this,this._path.concat([b])),this.children.set(b,I)),I}_checkForGC(){this.identityChangeListeners.size>0||this.children.size>0||this._parent&&this._parent.removeChild(pl(this._path))}},Ma=class{constructor(b){this.$$isPointerToPrismProvider=!0,this.pointer=go({root:this,path:[]}),this.prism=this.pointerToPrism(this.pointer),this._onPointerValueChange=(I,G)=>{const{path:se}=Ir(I),ut=this._getOrCreateScopeForPath(se);return ut.identityChangeListeners.add(G),()=>{ut.identityChangeListeners.delete(G)}},this._currentState=b,this._rootScope=new Ea(void 0,[])}set(b){const I=this._currentState;this._currentState=b,this._checkUpdates(this._rootScope,I,b)}get(){return this._currentState}getByPointer(b){const I=Bi(b)?b:b(this.pointer),G=Ir(I).path;return this._getIn(G)}_getIn(b){return b.length===0?this.get():sl(this.get(),b)}reduce(b){this.set(b(this.get()))}reduceByPointer(b,I){const G=Bi(b)?b:b(this.pointer),se=Ir(G).path,ut=ma(this.get(),se,I);this.set(ut)}setByPointer(b,I){this.reduceByPointer(b,()=>I)}_checkUpdates(b,I,G){if(I===G)return;for(const Ot of b.identityChangeListeners)Ot(G);if(b.children.size===0)return;const se=Wt(I),ut=Wt(G);if(!(se===2&&se===ut))for(const[Ot,Pn]of b.children){const li=bo(I,Ot,se),Aa=bo(G,Ot,ut);this._checkUpdates(Pn,li,Aa)}}_getOrCreateScopeForPath(b){let I=this._rootScope;for(const G of b)I=I.getOrCreateChild(G);return I}pointerToPrism(b){const{path:I}=Ir(b),G=ut=>this._onPointerValueChange(b,ut),se=()=>this._getIn(I);return Or(()=>Or.source(G,se))}},Ta=new WeakMap;function Rl(b){return typeof b=="object"&&b!==null&&b.$$isPointerToPrismProvider===!0}var xs=b=>{const I=gi(b);let G=Ta.get(I);if(!G){const se=I.root;if(!Rl(se))throw new Error("Cannot run pointerToPrism() on a pointer whose root is not an PointerToPrismProvider");G=se.pointerToPrism(b),Ta.set(I,G)}return G},So=b=>Bi(b)?xs(b).getValue():vs(b)?b.getValue():b;function*Pl(b){let I;if(Bi(b))I=xs(b);else if(vs(b))I=b;else throw new Error("Only pointers and prisms are supported");let G=0;const se=I.onStale(()=>{G++});try{for(;;){const ut=G;G=0,yield{value:I.getValue(),ticks:ut}}}finally{se()}}var Cl=180,wa=class{constructor(b){this._conf=b,this._ticking=!1,this._dormant=!0,this._numberOfDormantTicks=0,this.__ticks=0,this._scheduledForThisOrNextTick=new Set,this._scheduledForNextTick=new Set,this._timeAtCurrentTick=0}get dormant(){return this._dormant}onThisOrNextTick(b){this._scheduledForThisOrNextTick.add(b),this._dormant&&this._goActive()}onNextTick(b){this._scheduledForNextTick.add(b),this._dormant&&this._goActive()}offThisOrNextTick(b){this._scheduledForThisOrNextTick.delete(b)}offNextTick(b){this._scheduledForNextTick.delete(b)}get time(){return this._ticking?this._timeAtCurrentTick:performance.now()}_goActive(){var b,I;this._dormant&&(this._dormant=!1,(I=(b=this._conf)==null?void 0:b.onActive)==null||I.call(b))}_goDormant(){var b,I;this._dormant||(this._dormant=!0,this._numberOfDormantTicks=0,(I=(b=this._conf)==null?void 0:b.onDormant)==null||I.call(b))}tick(b=performance.now()){if(this.__ticks++,!this._dormant&&this._scheduledForNextTick.size===0&&this._scheduledForThisOrNextTick.size===0&&(this._numberOfDormantTicks++,this._numberOfDormantTicks>=Cl)){this._goDormant();return}this._ticking=!0,this._timeAtCurrentTick=b;for(const I of this._scheduledForNextTick)this._scheduledForThisOrNextTick.add(I);this._scheduledForNextTick.clear(),this._tick(0),this._ticking=!1}_tick(b){const I=this.time;if(b>10&&console.warn("_tick() recursing for 10 times"),b>100)throw new Error("Maximum recursion limit for _tick()");const G=this._scheduledForThisOrNextTick;this._scheduledForThisOrNextTick=new Set;for(const se of G)se(I);if(this._scheduledForThisOrNextTick.size>0)return this._tick(b+1)}};function*Dl(b){let I;if(Bi(b))I=xs(b);else if(vs(b))I=b;else throw new Error("Only pointers and prisms are supported");const G=new wa,se=I.onChange(G,ut=>{});try{for(;;)G.tick(),yield I.getValue()}finally{se()}}var Il=class{constructor(b){this.$$isPointerToPrismProvider=!0,this._currentPointerBox=new Ma(b),this.pointer=go({root:this,path:[]})}setPointer(b){this._currentPointerBox.set(b)}pointerToPrism(b){const{path:I}=gi(b);return Or(()=>{const G=this._currentPointerBox.prism.getValue(),se=I.reduce((ut,Ot)=>ut[Ot],G);return So(se)})}}})(ih)),ih}const Ym={type:"change"},Dd={type:"start"},i_={type:"end"},yc=new co,Km=new yr,fC=Math.cos(70*Ag.DEG2RAD),vn=new U,Kn=2*Math.PI,Yt={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},rh=1e-6;class pC extends t_{constructor(e,t=null){super(e,t),this.state=Yt.NONE,this.enabled=!0,this.target=new U,this.cursor=new U,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:Xs.ROTATE,MIDDLE:Xs.DOLLY,RIGHT:Xs.PAN},this.touches={ONE:Hs.ROTATE,TWO:Hs.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._domElementKeyEvents=null,this._lastPosition=new U,this._lastQuaternion=new Mt,this._lastTargetPosition=new U,this._quat=new Mt().setFromUnitVectors(e.up,new U(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new Xm,this._sphericalDelta=new Xm,this._scale=1,this._panOffset=new U,this._rotateStart=new ht,this._rotateEnd=new ht,this._rotateDelta=new ht,this._panStart=new ht,this._panEnd=new ht,this._panDelta=new ht,this._dollyStart=new ht,this._dollyEnd=new ht,this._dollyDelta=new ht,this._dollyDirection=new U,this._mouse=new ht,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=gC.bind(this),this._onPointerDown=mC.bind(this),this._onPointerUp=_C.bind(this),this._onContextMenu=MC.bind(this),this._onMouseWheel=xC.bind(this),this._onKeyDown=bC.bind(this),this._onTouchStart=SC.bind(this),this._onTouchMove=EC.bind(this),this._onMouseDown=vC.bind(this),this._onMouseMove=yC.bind(this),this._interceptControlDown=TC.bind(this),this._interceptControlUp=wC.bind(this),this.domElement!==null&&this.connect(),this.update()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointercancel",this._onPointerUp),this.domElement.addEventListener("contextmenu",this._onContextMenu),this.domElement.addEventListener("wheel",this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener("keydown",this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.removeEventListener("pointercancel",this._onPointerUp),this.domElement.removeEventListener("wheel",this._onMouseWheel),this.domElement.removeEventListener("contextmenu",this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener("keydown",this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction="auto"}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(e){e.addEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=e}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(Ym),this.update(),this.state=Yt.NONE}update(e=null){const t=this.object.position;vn.copy(t).sub(this.target),vn.applyQuaternion(this._quat),this._spherical.setFromVector3(vn),this.autoRotate&&this.state===Yt.NONE&&this._rotateLeft(this._getAutoRotationAngle(e)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let n=this.minAzimuthAngle,i=this.maxAzimuthAngle;isFinite(n)&&isFinite(i)&&(n<-Math.PI?n+=Kn:n>Math.PI&&(n-=Kn),i<-Math.PI?i+=Kn:i>Math.PI&&(i-=Kn),n<=i?this._spherical.theta=Math.max(n,Math.min(i,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(n+i)/2?Math.max(n,this._spherical.theta):Math.min(i,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let s=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{const a=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),s=a!=this._spherical.radius}if(vn.setFromSpherical(this._spherical),vn.applyQuaternion(this._quatInverse),t.copy(this.target).add(vn),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let a=null;if(this.object.isPerspectiveCamera){const c=vn.length();a=this._clampDistance(c*this._scale);const u=c-a;this.object.position.addScaledVector(this._dollyDirection,u),this.object.updateMatrixWorld(),s=!!u}else if(this.object.isOrthographicCamera){const c=new U(this._mouse.x,this._mouse.y,0);c.unproject(this.object);const u=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),s=u!==this.object.zoom;const h=new U(this._mouse.x,this._mouse.y,0);h.unproject(this.object),this.object.position.sub(h).add(c),this.object.updateMatrixWorld(),a=vn.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),this.zoomToCursor=!1;a!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(a).add(this.object.position):(yc.origin.copy(this.object.position),yc.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(yc.direction))<fC?this.object.lookAt(this.target):(Km.setFromNormalAndCoplanarPoint(this.object.up,this.target),yc.intersectPlane(Km,this.target))))}else if(this.object.isOrthographicCamera){const a=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),a!==this.object.zoom&&(this.object.updateProjectionMatrix(),s=!0)}return this._scale=1,this._performCursorZoom=!1,s||this._lastPosition.distanceToSquared(this.object.position)>rh||8*(1-this._lastQuaternion.dot(this.object.quaternion))>rh||this._lastTargetPosition.distanceToSquared(this.target)>rh?(this.dispatchEvent(Ym),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(e){return e!==null?Kn/60*this.autoRotateSpeed*e:Kn/60/60*this.autoRotateSpeed}_getZoomScale(e){const t=Math.abs(e*.01);return Math.pow(.95,this.zoomSpeed*t)}_rotateLeft(e){this._sphericalDelta.theta-=e}_rotateUp(e){this._sphericalDelta.phi-=e}_panLeft(e,t){vn.setFromMatrixColumn(t,0),vn.multiplyScalar(-e),this._panOffset.add(vn)}_panUp(e,t){this.screenSpacePanning===!0?vn.setFromMatrixColumn(t,1):(vn.setFromMatrixColumn(t,0),vn.crossVectors(this.object.up,vn)),vn.multiplyScalar(e),this._panOffset.add(vn)}_pan(e,t){const n=this.domElement;if(this.object.isPerspectiveCamera){const i=this.object.position;vn.copy(i).sub(this.target);let s=vn.length();s*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*e*s/n.clientHeight,this.object.matrix),this._panUp(2*t*s/n.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(e*(this.object.right-this.object.left)/this.object.zoom/n.clientWidth,this.object.matrix),this._panUp(t*(this.object.top-this.object.bottom)/this.object.zoom/n.clientHeight,this.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),this.enablePan=!1)}_dollyOut(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_dollyIn(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_updateZoomParameters(e,t){if(!this.zoomToCursor)return;this._performCursorZoom=!0;const n=this.domElement.getBoundingClientRect(),i=e-n.left,s=t-n.top,a=n.width,c=n.height;this._mouse.x=i/a*2-1,this._mouse.y=-(s/c)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(e){return Math.max(this.minDistance,Math.min(this.maxDistance,e))}_handleMouseDownRotate(e){this._rotateStart.set(e.clientX,e.clientY)}_handleMouseDownDolly(e){this._updateZoomParameters(e.clientX,e.clientX),this._dollyStart.set(e.clientX,e.clientY)}_handleMouseDownPan(e){this._panStart.set(e.clientX,e.clientY)}_handleMouseMoveRotate(e){this._rotateEnd.set(e.clientX,e.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Kn*this._rotateDelta.x/t.clientHeight),this._rotateUp(Kn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(e){this._dollyEnd.set(e.clientX,e.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(e){this._panEnd.set(e.clientX,e.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(e){this._updateZoomParameters(e.clientX,e.clientY),e.deltaY<0?this._dollyIn(this._getZoomScale(e.deltaY)):e.deltaY>0&&this._dollyOut(this._getZoomScale(e.deltaY)),this.update()}_handleKeyDown(e){let t=!1;switch(e.code){case this.keys.UP:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(Kn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,this.keyPanSpeed),t=!0;break;case this.keys.BOTTOM:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(-Kn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,-this.keyPanSpeed),t=!0;break;case this.keys.LEFT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(Kn*this.rotateSpeed/this.domElement.clientHeight):this._pan(this.keyPanSpeed,0),t=!0;break;case this.keys.RIGHT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(-Kn*this.rotateSpeed/this.domElement.clientHeight):this._pan(-this.keyPanSpeed,0),t=!0;break}t&&(e.preventDefault(),this.update())}_handleTouchStartRotate(e){if(this._pointers.length===1)this._rotateStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._rotateStart.set(n,i)}}_handleTouchStartPan(e){if(this._pointers.length===1)this._panStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panStart.set(n,i)}}_handleTouchStartDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyStart.set(0,s)}_handleTouchStartDollyPan(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enablePan&&this._handleTouchStartPan(e)}_handleTouchStartDollyRotate(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enableRotate&&this._handleTouchStartRotate(e)}_handleTouchMoveRotate(e){if(this._pointers.length==1)this._rotateEnd.set(e.pageX,e.pageY);else{const n=this._getSecondPointerPosition(e),i=.5*(e.pageX+n.x),s=.5*(e.pageY+n.y);this._rotateEnd.set(i,s)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Kn*this._rotateDelta.x/t.clientHeight),this._rotateUp(Kn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(e){if(this._pointers.length===1)this._panEnd.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panEnd.set(n,i)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyEnd.set(0,s),this._dollyDelta.set(0,Math.pow(this._dollyEnd.y/this._dollyStart.y,this.zoomSpeed)),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);const a=(e.pageX+t.x)*.5,c=(e.pageY+t.y)*.5;this._updateZoomParameters(a,c)}_handleTouchMoveDollyPan(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enablePan&&this._handleTouchMovePan(e)}_handleTouchMoveDollyRotate(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enableRotate&&this._handleTouchMoveRotate(e)}_addPointer(e){this._pointers.push(e.pointerId)}_removePointer(e){delete this._pointerPositions[e.pointerId];for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId){this._pointers.splice(t,1);return}}_isTrackingPointer(e){for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId)return!0;return!1}_trackPointer(e){let t=this._pointerPositions[e.pointerId];t===void 0&&(t=new ht,this._pointerPositions[e.pointerId]=t),t.set(e.pageX,e.pageY)}_getSecondPointerPosition(e){const t=e.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[t]}_customWheelEvent(e){const t=e.deltaMode,n={clientX:e.clientX,clientY:e.clientY,deltaY:e.deltaY};switch(t){case 1:n.deltaY*=16;break;case 2:n.deltaY*=100;break}return e.ctrlKey&&!this._controlActive&&(n.deltaY*=10),n}}function mC(r){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.domElement.addEventListener("pointerup",this._onPointerUp)),!this._isTrackingPointer(r)&&(this._addPointer(r),r.pointerType==="touch"?this._onTouchStart(r):this._onMouseDown(r)))}function gC(r){this.enabled!==!1&&(r.pointerType==="touch"?this._onTouchMove(r):this._onMouseMove(r))}function _C(r){switch(this._removePointer(r),this._pointers.length){case 0:this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.dispatchEvent(i_),this.state=Yt.NONE;break;case 1:const e=this._pointers[0],t=this._pointerPositions[e];this._onTouchStart({pointerId:e,pageX:t.x,pageY:t.y});break}}function vC(r){let e;switch(r.button){case 0:e=this.mouseButtons.LEFT;break;case 1:e=this.mouseButtons.MIDDLE;break;case 2:e=this.mouseButtons.RIGHT;break;default:e=-1}switch(e){case Xs.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(r),this.state=Yt.DOLLY;break;case Xs.ROTATE:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Yt.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Yt.ROTATE}break;case Xs.PAN:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Yt.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Yt.PAN}break;default:this.state=Yt.NONE}this.state!==Yt.NONE&&this.dispatchEvent(Dd)}function yC(r){switch(this.state){case Yt.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(r);break;case Yt.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(r);break;case Yt.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(r);break}}function xC(r){this.enabled===!1||this.enableZoom===!1||this.state!==Yt.NONE||(r.preventDefault(),this.dispatchEvent(Dd),this._handleMouseWheel(this._customWheelEvent(r)),this.dispatchEvent(i_))}function bC(r){this.enabled===!1||this.enablePan===!1||this._handleKeyDown(r)}function SC(r){switch(this._trackPointer(r),this._pointers.length){case 1:switch(this.touches.ONE){case Hs.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(r),this.state=Yt.TOUCH_ROTATE;break;case Hs.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(r),this.state=Yt.TOUCH_PAN;break;default:this.state=Yt.NONE}break;case 2:switch(this.touches.TWO){case Hs.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(r),this.state=Yt.TOUCH_DOLLY_PAN;break;case Hs.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(r),this.state=Yt.TOUCH_DOLLY_ROTATE;break;default:this.state=Yt.NONE}break;default:this.state=Yt.NONE}this.state!==Yt.NONE&&this.dispatchEvent(Dd)}function EC(r){switch(this._trackPointer(r),this.state){case Yt.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(r),this.update();break;case Yt.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(r),this.update();break;case Yt.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(r),this.update();break;case Yt.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(r),this.update();break;default:this.state=Yt.NONE}}function MC(r){this.enabled!==!1&&r.preventDefault()}function TC(r){r.key==="Control"&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}function wC(r){r.key==="Control"&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}const ns=new Qg,kn=new U,_r=new U,on=new Mt,$m={X:new U(1,0,0),Y:new U(0,1,0),Z:new U(0,0,1)},sh={type:"change"},Zm={type:"mouseDown",mode:null},Qm={type:"mouseUp",mode:null},Jm={type:"objectChange"};class AC extends t_{constructor(e,t=null){super(void 0,t);const n=new LC(this);this._root=n;const i=new FC;this._gizmo=i,n.add(i);const s=new NC;this._plane=s,n.add(s);const a=this;function c(w,S){let z=S;Object.defineProperty(a,w,{get:function(){return z!==void 0?z:S},set:function(O){z!==O&&(z=O,s[w]=O,i[w]=O,a.dispatchEvent({type:w+"-changed",value:O}),a.dispatchEvent(sh))}}),a[w]=S,s[w]=S,i[w]=S}c("camera",e),c("object",void 0),c("enabled",!0),c("axis",null),c("mode","translate"),c("translationSnap",null),c("rotationSnap",null),c("scaleSnap",null),c("space","world"),c("size",1),c("dragging",!1),c("showX",!0),c("showY",!0),c("showZ",!0),c("minX",-1/0),c("maxX",1/0),c("minY",-1/0),c("maxY",1/0),c("minZ",-1/0),c("maxZ",1/0);const u=new U,h=new U,f=new Mt,p=new Mt,m=new U,g=new Mt,x=new U,E=new U,v=new U,_=0,R=new U;c("worldPosition",u),c("worldPositionStart",h),c("worldQuaternion",f),c("worldQuaternionStart",p),c("cameraPosition",m),c("cameraQuaternion",g),c("pointStart",x),c("pointEnd",E),c("rotationAxis",v),c("rotationAngle",_),c("eye",R),this._offset=new U,this._startNorm=new U,this._endNorm=new U,this._cameraScale=new U,this._parentPosition=new U,this._parentQuaternion=new Mt,this._parentQuaternionInv=new Mt,this._parentScale=new U,this._worldScaleStart=new U,this._worldQuaternionInv=new Mt,this._worldScale=new U,this._positionStart=new U,this._quaternionStart=new Mt,this._scaleStart=new U,this._getPointer=RC.bind(this),this._onPointerDown=CC.bind(this),this._onPointerHover=PC.bind(this),this._onPointerMove=DC.bind(this),this._onPointerUp=IC.bind(this),t!==null&&this.connect()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointermove",this._onPointerHover),this.domElement.addEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerHover),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="auto"}getHelper(){return this._root}pointerHover(e){if(this.object===void 0||this.dragging===!0)return;e!==null&&ns.setFromCamera(e,this.camera);const t=oh(this._gizmo.picker[this.mode],ns);t?this.axis=t.object.name:this.axis=null}pointerDown(e){if(!(this.object===void 0||this.dragging===!0||e!=null&&e.button!==0)&&this.axis!==null){e!==null&&ns.setFromCamera(e,this.camera);const t=oh(this._plane,ns,!0);t&&(this.object.updateMatrixWorld(),this.object.parent.updateMatrixWorld(),this._positionStart.copy(this.object.position),this._quaternionStart.copy(this.object.quaternion),this._scaleStart.copy(this.object.scale),this.object.matrixWorld.decompose(this.worldPositionStart,this.worldQuaternionStart,this._worldScaleStart),this.pointStart.copy(t.point).sub(this.worldPositionStart)),this.dragging=!0,Zm.mode=this.mode,this.dispatchEvent(Zm)}}pointerMove(e){const t=this.axis,n=this.mode,i=this.object;let s=this.space;if(n==="scale"?s="local":(t==="E"||t==="XYZE"||t==="XYZ")&&(s="world"),i===void 0||t===null||this.dragging===!1||e!==null&&e.button!==-1)return;e!==null&&ns.setFromCamera(e,this.camera);const a=oh(this._plane,ns,!0);if(a){if(this.pointEnd.copy(a.point).sub(this.worldPositionStart),n==="translate")this._offset.copy(this.pointEnd).sub(this.pointStart),s==="local"&&t!=="XYZ"&&this._offset.applyQuaternion(this._worldQuaternionInv),t.indexOf("X")===-1&&(this._offset.x=0),t.indexOf("Y")===-1&&(this._offset.y=0),t.indexOf("Z")===-1&&(this._offset.z=0),s==="local"&&t!=="XYZ"?this._offset.applyQuaternion(this._quaternionStart).divide(this._parentScale):this._offset.applyQuaternion(this._parentQuaternionInv).divide(this._parentScale),i.position.copy(this._offset).add(this._positionStart),this.translationSnap&&(s==="local"&&(i.position.applyQuaternion(on.copy(this._quaternionStart).invert()),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.position.applyQuaternion(this._quaternionStart)),s==="world"&&(i.parent&&i.position.add(kn.setFromMatrixPosition(i.parent.matrixWorld)),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.parent&&i.position.sub(kn.setFromMatrixPosition(i.parent.matrixWorld)))),i.position.x=Math.max(this.minX,Math.min(this.maxX,i.position.x)),i.position.y=Math.max(this.minY,Math.min(this.maxY,i.position.y)),i.position.z=Math.max(this.minZ,Math.min(this.maxZ,i.position.z));else if(n==="scale"){if(t.search("XYZ")!==-1){let c=this.pointEnd.length()/this.pointStart.length();this.pointEnd.dot(this.pointStart)<0&&(c*=-1),_r.set(c,c,c)}else kn.copy(this.pointStart),_r.copy(this.pointEnd),kn.applyQuaternion(this._worldQuaternionInv),_r.applyQuaternion(this._worldQuaternionInv),_r.divide(kn),t.search("X")===-1&&(_r.x=1),t.search("Y")===-1&&(_r.y=1),t.search("Z")===-1&&(_r.z=1);i.scale.copy(this._scaleStart).multiply(_r),this.scaleSnap&&(t.search("X")!==-1&&(i.scale.x=Math.round(i.scale.x/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Y")!==-1&&(i.scale.y=Math.round(i.scale.y/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Z")!==-1&&(i.scale.z=Math.round(i.scale.z/this.scaleSnap)*this.scaleSnap||this.scaleSnap))}else if(n==="rotate"){this._offset.copy(this.pointEnd).sub(this.pointStart);const c=20/this.worldPosition.distanceTo(kn.setFromMatrixPosition(this.camera.matrixWorld));let u=!1;t==="XYZE"?(this.rotationAxis.copy(this._offset).cross(this.eye).normalize(),this.rotationAngle=this._offset.dot(kn.copy(this.rotationAxis).cross(this.eye))*c):(t==="X"||t==="Y"||t==="Z")&&(this.rotationAxis.copy($m[t]),kn.copy($m[t]),s==="local"&&kn.applyQuaternion(this.worldQuaternion),kn.cross(this.eye),kn.length()===0?u=!0:this.rotationAngle=this._offset.dot(kn.normalize())*c),(t==="E"||u)&&(this.rotationAxis.copy(this.eye),this.rotationAngle=this.pointEnd.angleTo(this.pointStart),this._startNorm.copy(this.pointStart).normalize(),this._endNorm.copy(this.pointEnd).normalize(),this.rotationAngle*=this._endNorm.cross(this._startNorm).dot(this.eye)<0?1:-1),this.rotationSnap&&(this.rotationAngle=Math.round(this.rotationAngle/this.rotationSnap)*this.rotationSnap),s==="local"&&t!=="E"&&t!=="XYZE"?(i.quaternion.copy(this._quaternionStart),i.quaternion.multiply(on.setFromAxisAngle(this.rotationAxis,this.rotationAngle)).normalize()):(this.rotationAxis.applyQuaternion(this._parentQuaternionInv),i.quaternion.copy(on.setFromAxisAngle(this.rotationAxis,this.rotationAngle)),i.quaternion.multiply(this._quaternionStart).normalize())}this.dispatchEvent(sh),this.dispatchEvent(Jm)}}pointerUp(e){e!==null&&e.button!==0||(this.dragging&&this.axis!==null&&(Qm.mode=this.mode,this.dispatchEvent(Qm)),this.dragging=!1,this.axis=null)}dispose(){this.disconnect(),this._root.dispose()}attach(e){return this.object=e,this._root.visible=!0,this}detach(){return this.object=void 0,this.axis=null,this._root.visible=!1,this}reset(){this.enabled&&this.dragging&&(this.object.position.copy(this._positionStart),this.object.quaternion.copy(this._quaternionStart),this.object.scale.copy(this._scaleStart),this.dispatchEvent(sh),this.dispatchEvent(Jm),this.pointStart.copy(this.pointEnd))}getRaycaster(){return ns}getMode(){return this.mode}setMode(e){this.mode=e}setTranslationSnap(e){this.translationSnap=e}setRotationSnap(e){this.rotationSnap=e}setScaleSnap(e){this.scaleSnap=e}setSize(e){this.size=e}setSpace(e){this.space=e}}function RC(r){if(this.domElement.ownerDocument.pointerLockElement)return{x:0,y:0,button:r.button};{const e=this.domElement.getBoundingClientRect();return{x:(r.clientX-e.left)/e.width*2-1,y:-(r.clientY-e.top)/e.height*2+1,button:r.button}}}function PC(r){if(this.enabled)switch(r.pointerType){case"mouse":case"pen":this.pointerHover(this._getPointer(r));break}}function CC(r){this.enabled&&(document.pointerLockElement||this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.pointerHover(this._getPointer(r)),this.pointerDown(this._getPointer(r)))}function DC(r){this.enabled&&this.pointerMove(this._getPointer(r))}function IC(r){this.enabled&&(this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.pointerUp(this._getPointer(r)))}function oh(r,e,t){const n=e.intersectObject(r,!0);for(let i=0;i<n.length;i++)if(n[i].object.visible||t)return n[i];return!1}const xc=new wi,$t=new U(0,1,0),eg=new U(0,0,0),tg=new pt,bc=new Mt,Ic=new Mt,Pi=new U,ng=new pt,qo=new U(1,0,0),ss=new U(0,1,0),Yo=new U(0,0,1),Sc=new U,Ho=new U,Vo=new U;class LC extends rn{constructor(e){super(),this.isTransformControlsRoot=!0,this.controls=e,this.visible=!1}updateMatrixWorld(e){const t=this.controls;t.object!==void 0&&(t.object.updateMatrixWorld(),t.object.parent===null?console.error("TransformControls: The attached 3D object must be a part of the scene graph."):t.object.parent.matrixWorld.decompose(t._parentPosition,t._parentQuaternion,t._parentScale),t.object.matrixWorld.decompose(t.worldPosition,t.worldQuaternion,t._worldScale),t._parentQuaternionInv.copy(t._parentQuaternion).invert(),t._worldQuaternionInv.copy(t.worldQuaternion).invert()),t.camera.updateMatrixWorld(),t.camera.matrixWorld.decompose(t.cameraPosition,t.cameraQuaternion,t._cameraScale),t.camera.isOrthographicCamera?t.camera.getWorldDirection(t.eye).negate():t.eye.copy(t.cameraPosition).sub(t.worldPosition).normalize(),super.updateMatrixWorld(e)}dispose(){this.traverse(function(e){e.geometry&&e.geometry.dispose(),e.material&&e.material.dispose()})}}class FC extends rn{constructor(){super(),this.isTransformControlsGizmo=!0,this.type="TransformControlsGizmo";const e=new pi({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),t=new Gc({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),n=e.clone();n.opacity=.15;const i=t.clone();i.opacity=.5;const s=e.clone();s.color.setHex(16711680);const a=e.clone();a.color.setHex(65280);const c=e.clone();c.color.setHex(255);const u=e.clone();u.color.setHex(16711680),u.opacity=.5;const h=e.clone();h.color.setHex(65280),h.opacity=.5;const f=e.clone();f.color.setHex(255),f.opacity=.5;const p=e.clone();p.opacity=.25;const m=e.clone();m.color.setHex(16776960),m.opacity=.25,e.clone().color.setHex(16776960);const x=e.clone();x.color.setHex(7895160);const E=new Cn(0,.04,.1,12);E.translate(0,.05,0);const v=new ln(.08,.08,.08);v.translate(0,.04,0);const _=new yn;_.setAttribute("position",new Zt([0,0,0,1,0,0],3));const R=new Cn(.0075,.0075,.5,3);R.translate(0,.25,0);function w(le,Y){const de=new cs(le,.0075,3,64,Y*Math.PI*2);return de.rotateY(Math.PI/2),de.rotateX(Math.PI/2),de}function S(){const le=new yn;return le.setAttribute("position",new Zt([0,0,0,1,1,1],3)),le}const z={X:[[new Pe(E,s),[.5,0,0],[0,0,-Math.PI/2]],[new Pe(E,s),[-.5,0,0],[0,0,Math.PI/2]],[new Pe(R,s),[0,0,0],[0,0,-Math.PI/2]]],Y:[[new Pe(E,a),[0,.5,0]],[new Pe(E,a),[0,-.5,0],[Math.PI,0,0]],[new Pe(R,a)]],Z:[[new Pe(E,c),[0,0,.5],[Math.PI/2,0,0]],[new Pe(E,c),[0,0,-.5],[-Math.PI/2,0,0]],[new Pe(R,c),null,[Math.PI/2,0,0]]],XYZ:[[new Pe(new js(.1,0),p.clone()),[0,0,0]]],XY:[[new Pe(new ln(.15,.15,.01),f.clone()),[.15,.15,0]]],YZ:[[new Pe(new ln(.15,.15,.01),u.clone()),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Pe(new ln(.15,.15,.01),h.clone()),[.15,0,.15],[-Math.PI/2,0,0]]]},O={X:[[new Pe(new Cn(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Pe(new Cn(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Pe(new Cn(.2,0,.6,4),n),[0,.3,0]],[new Pe(new Cn(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Pe(new Cn(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Pe(new Cn(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XYZ:[[new Pe(new js(.2,0),n)]],XY:[[new Pe(new ln(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Pe(new ln(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Pe(new ln(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]]},N={START:[[new Pe(new js(.01,2),i),null,null,null,"helper"]],END:[[new Pe(new js(.01,2),i),null,null,null,"helper"]],DELTA:[[new xi(S(),i),null,null,null,"helper"]],X:[[new xi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new xi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new xi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]},V={XYZE:[[new Pe(w(.5,1),x),null,[0,Math.PI/2,0]]],X:[[new Pe(w(.5,.5),s)]],Y:[[new Pe(w(.5,.5),a),null,[0,0,-Math.PI/2]]],Z:[[new Pe(w(.5,.5),c),null,[0,Math.PI/2,0]]],E:[[new Pe(w(.75,1),m),null,[0,Math.PI/2,0]]]},D={AXIS:[[new xi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]]},A={XYZE:[[new Pe(new sa(.25,10,8),n)]],X:[[new Pe(new cs(.5,.1,4,24),n),[0,0,0],[0,-Math.PI/2,-Math.PI/2]]],Y:[[new Pe(new cs(.5,.1,4,24),n),[0,0,0],[Math.PI/2,0,0]]],Z:[[new Pe(new cs(.5,.1,4,24),n),[0,0,0],[0,0,-Math.PI/2]]],E:[[new Pe(new cs(.75,.1,2,24),n)]]},k={X:[[new Pe(v,s),[.5,0,0],[0,0,-Math.PI/2]],[new Pe(R,s),[0,0,0],[0,0,-Math.PI/2]],[new Pe(v,s),[-.5,0,0],[0,0,Math.PI/2]]],Y:[[new Pe(v,a),[0,.5,0]],[new Pe(R,a)],[new Pe(v,a),[0,-.5,0],[0,0,Math.PI]]],Z:[[new Pe(v,c),[0,0,.5],[Math.PI/2,0,0]],[new Pe(R,c),[0,0,0],[Math.PI/2,0,0]],[new Pe(v,c),[0,0,-.5],[-Math.PI/2,0,0]]],XY:[[new Pe(new ln(.15,.15,.01),f),[.15,.15,0]]],YZ:[[new Pe(new ln(.15,.15,.01),u),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Pe(new ln(.15,.15,.01),h),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Pe(new ln(.1,.1,.1),p.clone())]]},J={X:[[new Pe(new Cn(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Pe(new Cn(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Pe(new Cn(.2,0,.6,4),n),[0,.3,0]],[new Pe(new Cn(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Pe(new Cn(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Pe(new Cn(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XY:[[new Pe(new ln(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Pe(new ln(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Pe(new ln(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Pe(new ln(.2,.2,.2),n),[0,0,0]]]},ee={X:[[new xi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new xi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new xi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]};function re(le){const Y=new rn;for(const de in le)for(let ne=le[de].length;ne--;){const ye=le[de][ne][0].clone(),Te=le[de][ne][1],ze=le[de][ne][2],We=le[de][ne][3],xt=le[de][ne][4];ye.name=de,ye.tag=xt,Te&&ye.position.set(Te[0],Te[1],Te[2]),ze&&ye.rotation.set(ze[0],ze[1],ze[2]),We&&ye.scale.set(We[0],We[1],We[2]),ye.updateMatrix();const ue=ye.geometry.clone();ue.applyMatrix4(ye.matrix),ye.geometry=ue,ye.renderOrder=1/0,ye.position.set(0,0,0),ye.rotation.set(0,0,0),ye.scale.set(1,1,1),Y.add(ye)}return Y}this.gizmo={},this.picker={},this.helper={},this.add(this.gizmo.translate=re(z)),this.add(this.gizmo.rotate=re(V)),this.add(this.gizmo.scale=re(k)),this.add(this.picker.translate=re(O)),this.add(this.picker.rotate=re(A)),this.add(this.picker.scale=re(J)),this.add(this.helper.translate=re(N)),this.add(this.helper.rotate=re(D)),this.add(this.helper.scale=re(ee)),this.picker.translate.visible=!1,this.picker.rotate.visible=!1,this.picker.scale.visible=!1}updateMatrixWorld(e){const n=(this.mode==="scale"?"local":this.space)==="local"?this.worldQuaternion:Ic;this.gizmo.translate.visible=this.mode==="translate",this.gizmo.rotate.visible=this.mode==="rotate",this.gizmo.scale.visible=this.mode==="scale",this.helper.translate.visible=this.mode==="translate",this.helper.rotate.visible=this.mode==="rotate",this.helper.scale.visible=this.mode==="scale";let i=[];i=i.concat(this.picker[this.mode].children),i=i.concat(this.gizmo[this.mode].children),i=i.concat(this.helper[this.mode].children);for(let s=0;s<i.length;s++){const a=i[s];a.visible=!0,a.rotation.set(0,0,0),a.position.copy(this.worldPosition);let c;if(this.camera.isOrthographicCamera?c=(this.camera.top-this.camera.bottom)/this.camera.zoom:c=this.worldPosition.distanceTo(this.cameraPosition)*Math.min(1.9*Math.tan(Math.PI*this.camera.fov/360)/this.camera.zoom,7),a.scale.set(1,1,1).multiplyScalar(c*this.size/4),a.tag==="helper"){a.visible=!1,a.name==="AXIS"?(a.visible=!!this.axis,this.axis==="X"&&(on.setFromEuler(xc.set(0,0,0)),a.quaternion.copy(n).multiply(on),Math.abs($t.copy(qo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Y"&&(on.setFromEuler(xc.set(0,0,Math.PI/2)),a.quaternion.copy(n).multiply(on),Math.abs($t.copy(ss).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Z"&&(on.setFromEuler(xc.set(0,Math.PI/2,0)),a.quaternion.copy(n).multiply(on),Math.abs($t.copy(Yo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="XYZE"&&(on.setFromEuler(xc.set(0,Math.PI/2,0)),$t.copy(this.rotationAxis),a.quaternion.setFromRotationMatrix(tg.lookAt(eg,$t,ss)),a.quaternion.multiply(on),a.visible=this.dragging),this.axis==="E"&&(a.visible=!1)):a.name==="START"?(a.position.copy(this.worldPositionStart),a.visible=this.dragging):a.name==="END"?(a.position.copy(this.worldPosition),a.visible=this.dragging):a.name==="DELTA"?(a.position.copy(this.worldPositionStart),a.quaternion.copy(this.worldQuaternionStart),kn.set(1e-10,1e-10,1e-10).add(this.worldPositionStart).sub(this.worldPosition).multiplyScalar(-1),kn.applyQuaternion(this.worldQuaternionStart.clone().invert()),a.scale.copy(kn),a.visible=this.dragging):(a.quaternion.copy(n),this.dragging?a.position.copy(this.worldPositionStart):a.position.copy(this.worldPosition),this.axis&&(a.visible=this.axis.search(a.name)!==-1));continue}a.quaternion.copy(n),this.mode==="translate"||this.mode==="scale"?(a.name==="X"&&Math.abs($t.copy(qo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Y"&&Math.abs($t.copy(ss).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Z"&&Math.abs($t.copy(Yo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XY"&&Math.abs($t.copy(Yo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="YZ"&&Math.abs($t.copy(qo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XZ"&&Math.abs($t.copy(ss).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1)):this.mode==="rotate"&&(bc.copy(n),$t.copy(this.eye).applyQuaternion(on.copy(n).invert()),a.name.search("E")!==-1&&a.quaternion.setFromRotationMatrix(tg.lookAt(this.eye,eg,ss)),a.name==="X"&&(on.setFromAxisAngle(qo,Math.atan2(-$t.y,$t.z)),on.multiplyQuaternions(bc,on),a.quaternion.copy(on)),a.name==="Y"&&(on.setFromAxisAngle(ss,Math.atan2($t.x,$t.z)),on.multiplyQuaternions(bc,on),a.quaternion.copy(on)),a.name==="Z"&&(on.setFromAxisAngle(Yo,Math.atan2($t.y,$t.x)),on.multiplyQuaternions(bc,on),a.quaternion.copy(on))),a.visible=a.visible&&(a.name.indexOf("X")===-1||this.showX),a.visible=a.visible&&(a.name.indexOf("Y")===-1||this.showY),a.visible=a.visible&&(a.name.indexOf("Z")===-1||this.showZ),a.visible=a.visible&&(a.name.indexOf("E")===-1||this.showX&&this.showY&&this.showZ),a.material._color=a.material._color||a.material.color.clone(),a.material._opacity=a.material._opacity||a.material.opacity,a.material.color.copy(a.material._color),a.material.opacity=a.material._opacity,this.enabled&&this.axis&&(a.name===this.axis||this.axis.split("").some(function(u){return a.name===u}))&&(a.material.color.setHex(16776960),a.material.opacity=1)}super.updateMatrixWorld(e)}}class NC extends Pe{constructor(){super(new lo(1e5,1e5,2,2),new pi({visible:!1,wireframe:!0,side:$n,transparent:!0,opacity:.1,toneMapped:!1})),this.isTransformControlsPlane=!0,this.type="TransformControlsPlane"}updateMatrixWorld(e){let t=this.space;switch(this.position.copy(this.worldPosition),this.mode==="scale"&&(t="local"),Sc.copy(qo).applyQuaternion(t==="local"?this.worldQuaternion:Ic),Ho.copy(ss).applyQuaternion(t==="local"?this.worldQuaternion:Ic),Vo.copy(Yo).applyQuaternion(t==="local"?this.worldQuaternion:Ic),$t.copy(Ho),this.mode){case"translate":case"scale":switch(this.axis){case"X":$t.copy(this.eye).cross(Sc),Pi.copy(Sc).cross($t);break;case"Y":$t.copy(this.eye).cross(Ho),Pi.copy(Ho).cross($t);break;case"Z":$t.copy(this.eye).cross(Vo),Pi.copy(Vo).cross($t);break;case"XY":Pi.copy(Vo);break;case"YZ":Pi.copy(Sc);break;case"XZ":$t.copy(Vo),Pi.copy(Ho);break;case"XYZ":case"E":Pi.set(0,0,0);break}break;case"rotate":default:Pi.set(0,0,0)}Pi.length()===0?this.quaternion.copy(this.cameraQuaternion):(ng.lookAt(kn.set(0,0,0),Pi,$t),this.quaternion.setFromRotationMatrix(ng)),super.updateMatrixWorld(e)}}function ah(r){const e=new tr,t=new Td(.4,1,16),n=new pi({color:r,transparent:!0,opacity:1,side:$n,depthTest:!1,depthWrite:!1}),i=new Pe(t,n);i.rotation.x=Math.PI,i.renderOrder=999;const s=new sa(.35,32,32),a=new pi({color:new rt(1,1,1),emissive:r,emissiveIntensity:2,transparent:!0,opacity:1,depthTest:!1,depthWrite:!1}),c=new Pe(s,a);return c.position.y=.5,c.renderOrder=999,e.add(i),e.add(c),e}function OC(r){const e=new AP({canvas:r,antialias:!0});e.setPixelRatio(window.devicePixelRatio),e.setSize(r.clientWidth,r.clientHeight),e.shadowMap.enabled=!1,e.toneMapping=dg,e.toneMappingExposure=1.6,e.outputColorSpace=Tn;const t=new RP;t.background=new rt(1381664),t.fog=new Ed(1381664,.03);const n=new Gn(50,r.clientWidth/r.clientHeight,.1,1e3);n.position.set(0,1.6,5);const i=new pC(n,r);i.target.set(0,.9,0),i.enableDamping=!0,i.dampingFactor=.08,i.update();const s=new lo(14,10),a=new hs({color:4864558,roughness:.35,metalness:.05}),c=new Pe(s,a);c.rotation.x=-Math.PI/2,c.position.y=-.01,c.receiveShadow=!0,t.add(c);const u=new ln(14.2,.06,10.2),h=new hs({color:3811866,roughness:.6}),f=new Pe(u,h);f.position.y=-.04,f.receiveShadow=!0,t.add(f);const p=new QP(16777215,.8);t.add(p);const m=new Dc(16777215,3);m.position.set(2,4,-5),t.add(m);const g=ah(new rt(16777215));g.position.copy(m.position),g.lookAt(new U(0,0,0)),g.userData.light=m,t.add(g);const x=new Dc(15658751,2);x.position.set(-3,3,-4),t.add(x);const E=ah(new rt(15658751));E.position.copy(x.position),E.lookAt(new U(0,0,0)),E.userData.light=x,t.add(E);const v=new Dc(16772829,2.5);v.position.set(0,4,5),t.add(v);const _=ah(new rt(16772829));_.position.copy(v.position),_.lookAt(new U(0,0,0)),_.userData.light=v,t.add(_);const R={ambient:p,spotLeft:m,spotRight:x,backLight:v},w={spotLeftIcon:g,spotRightIcon:E,backLightIcon:_},S=new AC(n,r);S.setMode("translate"),S.setSize(.8),t.add(S),S.addEventListener("dragging-changed",O=>{i.enabled=!O.value});function z(){const O=r.clientWidth,N=r.clientHeight;e.setSize(O,N),n.aspect=O/N,n.updateProjectionMatrix()}return window.addEventListener("resize",z),{scene:t,camera:n,renderer:e,controls:i,lights:R,lightIcons:w,transformControls:S}}var Ko={exports:{}};Ko.exports;var ig;function UC(){return ig||(ig=1,(function(r,e){var t=Object.create,n=Object.defineProperty,i=Object.defineProperties,s=Object.getOwnPropertyDescriptor,a=Object.getOwnPropertyDescriptors,c=Object.getOwnPropertyNames,u=Object.getOwnPropertySymbols,h=Object.getPrototypeOf,f=Object.prototype.hasOwnProperty,p=Object.prototype.propertyIsEnumerable,m=(o,l,d)=>l in o?n(o,l,{enumerable:!0,configurable:!0,writable:!0,value:d}):o[l]=d,g=(o,l)=>{for(var d in l||(l={}))f.call(l,d)&&m(o,d,l[d]);if(u)for(var d of u(l))p.call(l,d)&&m(o,d,l[d]);return o},x=(o,l)=>i(o,a(l)),E=(o,l)=>function(){return l||(0,o[c(o)[0]])((l={exports:{}}).exports,l),l.exports},v=(o,l)=>{for(var d in l)n(o,d,{get:l[d],enumerable:!0})},_=(o,l,d,y)=>{if(l&&typeof l=="object"||typeof l=="function")for(let M of c(l))!f.call(o,M)&&M!==d&&n(o,M,{get:()=>l[M],enumerable:!(y=s(l,M))||y.enumerable});return o},R=(o,l,d)=>(d=o!=null?t(h(o)):{},_(!o||!o.__esModule?n(d,"default",{value:o,enumerable:!0}):d,o)),w=o=>_(n({},"__esModule",{value:!0}),o),S=(o,l,d)=>(m(o,typeof l!="symbol"?l+"":l,d),d),z=E({"../node_modules/timing-function/lib/UnitBezier.js"(o,l){l.exports=(function(){function d(y,M,C,B){this.set(y,M,C,B)}return d.prototype.set=function(y,M,C,B){this._cx=3*y,this._bx=3*(C-y)-this._cx,this._ax=1-this._cx-this._bx,this._cy=3*M,this._by=3*(B-M)-this._cy,this._ay=1-this._cy-this._by},d.epsilon=1e-6,d.prototype._sampleCurveX=function(y){return((this._ax*y+this._bx)*y+this._cx)*y},d.prototype._sampleCurveY=function(y){return((this._ay*y+this._by)*y+this._cy)*y},d.prototype._sampleCurveDerivativeX=function(y){return(3*this._ax*y+2*this._bx)*y+this._cx},d.prototype._solveCurveX=function(y,M){var C,B,K,Q,oe,xe;for(K=void 0,Q=void 0,oe=void 0,xe=void 0,C=void 0,B=void 0,oe=y,B=0;B<8;){if(xe=this._sampleCurveX(oe)-y,Math.abs(xe)<M)return oe;if(C=this._sampleCurveDerivativeX(oe),Math.abs(C)<M)break;oe=oe-xe/C,B++}if(K=0,Q=1,oe=y,oe<K)return K;if(oe>Q)return Q;for(;K<Q;){if(xe=this._sampleCurveX(oe),Math.abs(xe-y)<M)return oe;y>xe?K=oe:Q=oe,oe=(Q-K)*.5+K}return oe},d.prototype.solve=function(y,M){return this._sampleCurveY(this._solveCurveX(y,M))},d.prototype.solveSimple=function(y){return this._sampleCurveY(this._solveCurveX(y,1e-6))},d})()}}),O=E({"../node_modules/levenshtein-edit-distance/index.js"(o,l){var d,y;d=[],y=[];function M(C,B,K){var Q,oe,xe,Ee,Ie,tt,Xe,_t;if(C===B)return 0;if(Q=C.length,oe=B.length,Q===0)return oe;if(oe===0)return Q;for(K&&(C=C.toLowerCase(),B=B.toLowerCase()),Xe=0;Xe<Q;)y[Xe]=C.charCodeAt(Xe),d[Xe]=++Xe;for(_t=0;_t<oe;)for(xe=B.charCodeAt(_t),Ee=Ie=_t++,Xe=-1;++Xe<Q;)tt=xe===y[Xe]?Ie:Ie+1,Ie=d[Xe],d[Xe]=Ee=Ie>Ee?tt>Ee?Ee+1:tt:tt>Ie?Ie+1:tt;return Ee}l.exports=M}}),N=E({"../node_modules/propose/propose.js"(o,l){var d=O();function y(){var M,C,B,K,Q,oe=0,xe=arguments[0],Ee=arguments[1],Ie=Ee.length,tt=arguments[2];tt&&(K=tt.threshold,Q=tt.ignoreCase),K===void 0&&(K=0);for(var Xe=0;Xe<Ie;++Xe)Q?C=d(xe,Ee[Xe],!0):C=d(xe,Ee[Xe]),C>xe.length?M=1-C/Ee[Xe].length:M=1-C/xe.length,M>oe&&(oe=M,B=Ee[Xe]);return oe>=K?B:null}l.exports=y}}),V=E({"../node_modules/fast-deep-equal/index.js"(o,l){l.exports=function d(y,M){if(y===M)return!0;if(y&&M&&typeof y=="object"&&typeof M=="object"){if(y.constructor!==M.constructor)return!1;var C,B,K;if(Array.isArray(y)){if(C=y.length,C!=M.length)return!1;for(B=C;B--!==0;)if(!d(y[B],M[B]))return!1;return!0}if(y.constructor===RegExp)return y.source===M.source&&y.flags===M.flags;if(y.valueOf!==Object.prototype.valueOf)return y.valueOf()===M.valueOf();if(y.toString!==Object.prototype.toString)return y.toString()===M.toString();if(K=Object.keys(y),C=K.length,C!==Object.keys(M).length)return!1;for(B=C;B--!==0;)if(!Object.prototype.hasOwnProperty.call(M,K[B]))return!1;for(B=C;B--!==0;){var Q=K[B];if(!d(y[Q],M[Q]))return!1}return!0}return y!==y&&M!==M}}}),D={};v(D,{createRafDriver:()=>eu,getProject:()=>Mp,notify:()=>Es,onChange:()=>Su,types:()=>tu,val:()=>Tp}),r.exports=w(D);var A={};v(A,{createRafDriver:()=>eu,getProject:()=>Mp,notify:()=>Es,onChange:()=>Su,types:()=>tu,val:()=>Tp});var k=_n(),J=class{constructor(){S(this,"atom",new k.Atom({projects:{}}))}add(o,l){this.atom.setByPointer(d=>d.projects[o],l)}get(o){return this.atom.get().projects[o]}has(o){return!!this.get(o)}},ee=new J,re=ee,le=new WeakMap;function Y(o){return le.get(o)}function de(o,l){le.set(o,l)}var ne=[],ye=Array.isArray,Te=ye,ze=typeof Di=="object"&&Di&&Di.Object===Object&&Di,We=ze,xt=typeof self=="object"&&self&&self.Object===Object&&self,ue=We||xt||Function("return this")(),me=ue,De=me.Symbol,Se=De,et=Object.prototype,it=et.hasOwnProperty,Qe=et.toString,fe=Se?Se.toStringTag:void 0;function Me(o){var l=it.call(o,fe),d=o[fe];try{o[fe]=void 0;var y=!0}catch{}var M=Qe.call(o);return y&&(l?o[fe]=d:delete o[fe]),M}var Fe=Me,H=Object.prototype,nt=H.toString;function Je(o){return nt.call(o)}var $e=Je,Oe="[object Null]",at="[object Undefined]",Be=Se?Se.toStringTag:void 0;function L(o){return o==null?o===void 0?at:Oe:Be&&Be in Object(o)?Fe(o):$e(o)}var T=L;function $(o){return o!=null&&typeof o=="object"}var he=$,ge="[object Symbol]";function ce(o){return typeof o=="symbol"||he(o)&&T(o)==ge}var Ce=ce,we=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,ke=/^\w*$/;function Tt(o,l){if(Te(o))return!1;var d=typeof o;return d=="number"||d=="symbol"||d=="boolean"||o==null||Ce(o)?!0:ke.test(o)||!we.test(o)||l!=null&&o in Object(l)}var be=Tt;function Ue(o){var l=typeof o;return o!=null&&(l=="object"||l=="function")}var Ge=Ue,st="[object AsyncFunction]",Ve="[object Function]",bt="[object GeneratorFunction]",mt="[object Proxy]";function Ft(o){if(!Ge(o))return!1;var l=T(o);return l==Ve||l==bt||l==st||l==mt}var X=Ft,Re=me["__core-js_shared__"],ae=Re,pe=(function(){var o=/[^.]+$/.exec(ae&&ae.keys&&ae.keys.IE_PROTO||"");return o?"Symbol(src)_1."+o:""})();function F(o){return!!pe&&pe in o}var W=F,ie=Function.prototype,ve=ie.toString;function je(o){if(o!=null){try{return ve.call(o)}catch{}try{return o+""}catch{}}return""}var _e=je,He=/[\\^$.*+?()[\]{}|]/g,ot=/^\[object .+?Constructor\]$/,St=Function.prototype,Nt=Object.prototype,Pt=St.toString,ft=Nt.hasOwnProperty,ct=RegExp("^"+Pt.call(ft).replace(He,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function Qt(o){if(!Ge(o)||W(o))return!1;var l=X(o)?ct:ot;return l.test(_e(o))}var vt=Qt;function Xt(o,l){return o==null?void 0:o[l]}var cn=Xt;function Ct(o,l){var d=cn(o,l);return vt(d)?d:void 0}var Ht=Ct,In=Ht(Object,"create"),ci=In;function mi(){this.__data__=ci?ci(null):{},this.size=0}var P=mi;function q(o){var l=this.has(o)&&delete this.__data__[o];return this.size-=l?1:0,l}var te=q,Z="__lodash_hash_undefined__",j=Object.prototype,Ae=j.hasOwnProperty;function Ne(o){var l=this.__data__;if(ci){var d=l[o];return d===Z?void 0:d}return Ae.call(l,o)?l[o]:void 0}var qe=Ne,Ye=Object.prototype,dt=Ye.hasOwnProperty;function lt(o){var l=this.__data__;return ci?l[o]!==void 0:dt.call(l,o)}var Ke=lt,Dt="__lodash_hash_undefined__";function kt(o,l){var d=this.__data__;return this.size+=this.has(o)?0:1,d[o]=ci&&l===void 0?Dt:l,this}var Vt=kt;function an(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}an.prototype.clear=P,an.prototype.delete=te,an.prototype.get=qe,an.prototype.has=Ke,an.prototype.set=Vt;var It=an;function Ze(){this.__data__=[],this.size=0}var Qn=Ze;function At(o,l){return o===l||o!==o&&l!==l}var An=At;function Ai(o,l){for(var d=o.length;d--;)if(An(o[d][0],l))return d;return-1}var dn=Ai,Oi=Array.prototype,Gt=Oi.splice;function Xn(o){var l=this.__data__,d=dn(l,o);if(d<0)return!1;var y=l.length-1;return d==y?l.pop():Gt.call(l,d,1),--this.size,!0}var Ui=Xn;function Ln(o){var l=this.__data__,d=dn(l,o);return d<0?void 0:l[d][1]}var Rn=Ln;function Jn(o){return dn(this.__data__,o)>-1}var fs=Jn;function po(o,l){var d=this.__data__,y=dn(d,o);return y<0?(++this.size,d.push([o,l])):d[y][1]=l,this}var jc=po;function sr(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}sr.prototype.clear=Qn,sr.prototype.delete=Ui,sr.prototype.get=Rn,sr.prototype.has=fs,sr.prototype.set=jc;var ps=sr,Xc=Ht(me,"Map"),Pr=Xc;function qc(){this.size=0,this.__data__={hash:new It,map:new(Pr||ps),string:new It}}var Yc=qc;function Kc(o){var l=typeof o;return l=="string"||l=="number"||l=="symbol"||l=="boolean"?o!=="__proto__":o===null}var $c=Kc;function Zc(o,l){var d=o.__data__;return $c(l)?d[typeof l=="string"?"string":"hash"]:d.map}var Cr=Zc;function aa(o){var l=Cr(this,o).delete(o);return this.size-=l?1:0,l}var ca=aa;function Qc(o){return Cr(this,o).get(o)}var Jc=Qc;function el(o){return Cr(this,o).has(o)}var tl=el;function nl(o,l){var d=Cr(this,o),y=d.size;return d.set(o,l),this.size+=d.size==y?0:1,this}var il=nl;function or(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}or.prototype.clear=Yc,or.prototype.delete=ca,or.prototype.get=Jc,or.prototype.has=tl,or.prototype.set=il;var ms=or,rl="Expected a function";function mo(o,l){if(typeof o!="function"||l!=null&&typeof l!="function")throw new TypeError(rl);var d=function(){var y=arguments,M=l?l.apply(this,y):y[0],C=d.cache;if(C.has(M))return C.get(M);var B=o.apply(this,y);return d.cache=C.set(M,B)||C,B};return d.cache=new(mo.Cache||ms),d}mo.Cache=ms;var sl=mo,ol=500;function al(o){var l=sl(o,function(y){return d.size===ol&&d.clear(),y}),d=l.cache;return l}var cl=al,ll=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,ul=/\\(\\)?/g,hl=cl(function(o){var l=[];return o.charCodeAt(0)===46&&l.push(""),o.replace(ll,function(d,y,M,C){l.push(M?C.replace(ul,"$1"):y||d)}),l}),dl=hl;function la(o,l){for(var d=-1,y=o==null?0:o.length,M=Array(y);++d<y;)M[d]=l(o[d],d,o);return M}var fl=la,ua=Se?Se.prototype:void 0,ha=ua?ua.toString:void 0;function da(o){if(typeof o=="string")return o;if(Te(o))return fl(o,da)+"";if(Ce(o))return ha?ha.call(o):"";var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var fa=da;function pl(o){return o==null?"":fa(o)}var gs=pl;function pa(o,l){return Te(o)?o:be(o,l)?[o]:dl(gs(o))}var Dr=pa;function ml(o){if(typeof o=="string"||Ce(o))return o;var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var gi=ml;function Ir(o,l){l=Dr(l,o);for(var d=0,y=l.length;o!=null&&d<y;)o=o[gi(l[d++])];return d&&d==y?o:void 0}var _s=Ir;function go(o,l,d){var y=o==null?void 0:_s(o,l);return y===void 0?d:y}var Bi=go;function ma(o,l){return l.length===0?o:Bi(o,l)}var ar=class{constructor(){S(this,"_values",{})}get(o,l){if(this.has(o))return this._values[o];{const d=l();return this._values[o]=d,d}}has(o){return this._values.hasOwnProperty(o)}},mn=_n(),vs=(function(){try{var o=Ht(Object,"defineProperty");return o({},"",{}),o}catch{}})(),_o=vs;function gl(o,l,d){l=="__proto__"&&_o?_o(o,l,{configurable:!0,enumerable:!0,value:d,writable:!0}):o[l]=d}var ki=gl,Lr=Object.prototype,_l=Lr.hasOwnProperty;function vl(o,l,d){var y=o[l];(!(_l.call(o,l)&&An(y,d))||d===void 0&&!(l in o))&&ki(o,l,d)}var vo=vl,yl=9007199254740991,ga=/^(?:0|[1-9]\d*)$/;function xl(o,l){var d=typeof o;return l=l??yl,!!l&&(d=="number"||d!="symbol"&&ga.test(o))&&o>-1&&o%1==0&&o<l}var yo=xl;function bl(o,l,d,y){if(!Ge(o))return o;l=Dr(l,o);for(var M=-1,C=l.length,B=C-1,K=o;K!=null&&++M<C;){var Q=gi(l[M]),oe=d;if(Q==="__proto__"||Q==="constructor"||Q==="prototype")return o;if(M!=B){var xe=K[Q];oe=y?y(xe,Q,K):void 0,oe===void 0&&(oe=Ge(xe)?xe:yo(l[M+1])?[]:{})}vo(K,Q,oe),K=K[Q]}return o}var _a=bl;function va(o,l,d){return o==null?o:_a(o,l,d)}var ys=va,Sn=new WeakMap;function Sl(o){return xo(o)}function xo(o){if(Sn.has(o))return Sn.get(o);const l=o.type==="compound"?xa(o):o.type==="enum"?ya(o):o.default;return Sn.set(o,l),l}function ya(o){const l={$case:o.defaultCase};for(const[d,y]of Object.entries(o.cases))l[d]=xo(y);return l}function xa(o){const l={};for(const[d,y]of Object.entries(o.props))l[d]=xo(y);return l}var zn=_n(),El=R(z());function Ml(o,l,d){return(0,zn.prism)(()=>{const y=(0,zn.val)(l);return zn.prism.memo("driver",()=>y?y.type==="BasicKeyframedTrack"?Tl(o,y,d):(o.logger.error("Track type not yet supported."),(0,zn.prism)(()=>{})):(0,zn.prism)(()=>{}),[y]).getValue()})}function Tl(o,l,d){return(0,zn.prism)(()=>{let y=zn.prism.ref("state",{started:!1}),M=y.current;const C=d.getValue();return(!M.started||C<M.validFrom||M.validTo<=C)&&(y.current=M=wl(o,d,l)),M.der.getValue()})}var ba=(0,zn.prism)(()=>{});function wl(o,l,d){const y=l.getValue();if(d.keyframes.length===0)return{started:!0,validFrom:-1/0,validTo:1/0,der:ba};let M=0;for(;;){const C=d.keyframes[M];if(!C)return gn.error;const B=M===d.keyframes.length-1;if(y<C.position)return M===0?gn.beforeFirstKeyframe(C):gn.error;if(C.position===y)return B?gn.lastKeyframe(C):gn.between(C,d.keyframes[M+1],l);if(M===d.keyframes.length-1)return gn.lastKeyframe(C);{const K=M+1;if(d.keyframes[K].position<=y){M=K;continue}else return gn.between(C,d.keyframes[M+1],l)}}}var gn={beforeFirstKeyframe(o){return{started:!0,validFrom:-1/0,validTo:o.position,der:(0,zn.prism)(()=>({left:o.value,progression:0}))}},lastKeyframe(o){return{started:!0,validFrom:o.position,validTo:1/0,der:(0,zn.prism)(()=>({left:o.value,progression:0}))}},between(o,l,d){if(!o.connectedRight)return{started:!0,validFrom:o.position,validTo:l.position,der:(0,zn.prism)(()=>({left:o.value,progression:0}))};const y=C=>(C-o.position)/(l.position-o.position);if(!o.type||o.type==="bezier"){const C=new El.default(o.handles[2],o.handles[3],l.handles[0],l.handles[1]),B=(0,zn.prism)(()=>{const K=y(d.getValue()),Q=C.solveSimple(K);return{left:o.value,right:l.value,progression:Q}});return{started:!0,validFrom:o.position,validTo:l.position,der:B}}const M=(0,zn.prism)(()=>{const C=y(d.getValue()),B=Math.floor(C);return{left:o.value,right:l.value,progression:B}});return{started:!0,validFrom:o.position,validTo:l.position,der:M}},error:{started:!0,validFrom:-1/0,validTo:1/0,der:ba}};function Fr(o,l,d){const M=d.get(o);if(M&&M.override===l)return M.merged;const C=g({},o);for(const B of Object.keys(l)){const K=l[B],Q=o[B];C[B]=typeof K=="object"&&typeof Q=="object"?Fr(Q,K,d):K===void 0?Q:K}return d.set(o,{override:l,merged:C}),C}function Nr(o,l){let d=o;for(const y of l)d=d[y];return d}var Or=_n(),Sa=(o,l)=>{const d=Or.prism.memo(o,()=>new Or.Atom(l),[]);return d.set(l),d},Wt=_n(),bo=_n(),Al=/\s/;function Ea(o){for(var l=o.length;l--&&Al.test(o.charAt(l)););return l}var Ma=Ea,Ta=/^\s+/;function Rl(o){return o&&o.slice(0,Ma(o)+1).replace(Ta,"")}var xs=Rl,So=NaN,Pl=/^[-+]0x[0-9a-f]+$/i,Cl=/^0b[01]+$/i,wa=/^0o[0-7]+$/i,Dl=parseInt;function Il(o){if(typeof o=="number")return o;if(Ce(o))return So;if(Ge(o)){var l=typeof o.valueOf=="function"?o.valueOf():o;o=Ge(l)?l+"":l}if(typeof o!="string")return o===0?o:+o;o=xs(o);var d=Cl.test(o);return d||wa.test(o)?Dl(o.slice(2),d?2:8):Pl.test(o)?So:+o}var b=Il,I=1/0,G=17976931348623157e292;function se(o){if(!o)return o===0?o:0;if(o=b(o),o===I||o===-I){var l=o<0?-1:1;return l*G}return o===o?o:0}var ut=se;function Ot(o){var l=ut(o),d=l%1;return l===l?d?l-d:l:0}var Pn=Ot;function li(o){return o}var Aa=li,cr=Ht(me,"WeakMap"),Ur=cr,Fd=Object.create,l_=(function(){function o(){}return function(l){if(!Ge(l))return{};if(Fd)return Fd(l);o.prototype=l;var d=new o;return o.prototype=void 0,d}})(),u_=l_;function h_(o,l){var d=-1,y=o.length;for(l||(l=Array(y));++d<y;)l[d]=o[d];return l}var d_=h_;function f_(o,l){for(var d=-1,y=o==null?0:o.length;++d<y&&l(o[d],d,o)!==!1;);return o}var p_=f_;function m_(o,l,d,y){var M=!d;d||(d={});for(var C=-1,B=l.length;++C<B;){var K=l[C],Q=y?y(d[K],o[K],K,d,o):void 0;Q===void 0&&(Q=o[K]),M?ki(d,K,Q):vo(d,K,Q)}return d}var Ra=m_,g_=9007199254740991;function __(o){return typeof o=="number"&&o>-1&&o%1==0&&o<=g_}var Ll=__;function v_(o){return o!=null&&Ll(o.length)&&!X(o)}var Nd=v_,y_=Object.prototype;function x_(o){var l=o&&o.constructor,d=typeof l=="function"&&l.prototype||y_;return o===d}var Fl=x_;function b_(o,l){for(var d=-1,y=Array(o);++d<o;)y[d]=l(d);return y}var S_=b_,E_="[object Arguments]";function M_(o){return he(o)&&T(o)==E_}var Od=M_,Ud=Object.prototype,T_=Ud.hasOwnProperty,w_=Ud.propertyIsEnumerable,A_=Od((function(){return arguments})())?Od:function(o){return he(o)&&T_.call(o,"callee")&&!w_.call(o,"callee")},Bd=A_;function R_(){return!1}var P_=R_,kd=e&&!e.nodeType&&e,zd=kd&&!0&&r&&!r.nodeType&&r,C_=zd&&zd.exports===kd,Hd=C_?me.Buffer:void 0,D_=Hd?Hd.isBuffer:void 0,I_=D_||P_,Pa=I_,L_="[object Arguments]",F_="[object Array]",N_="[object Boolean]",O_="[object Date]",U_="[object Error]",B_="[object Function]",k_="[object Map]",z_="[object Number]",H_="[object Object]",V_="[object RegExp]",G_="[object Set]",W_="[object String]",j_="[object WeakMap]",X_="[object ArrayBuffer]",q_="[object DataView]",Y_="[object Float32Array]",K_="[object Float64Array]",$_="[object Int8Array]",Z_="[object Int16Array]",Q_="[object Int32Array]",J_="[object Uint8Array]",ev="[object Uint8ClampedArray]",tv="[object Uint16Array]",nv="[object Uint32Array]",sn={};sn[Y_]=sn[K_]=sn[$_]=sn[Z_]=sn[Q_]=sn[J_]=sn[ev]=sn[tv]=sn[nv]=!0,sn[L_]=sn[F_]=sn[X_]=sn[N_]=sn[q_]=sn[O_]=sn[U_]=sn[B_]=sn[k_]=sn[z_]=sn[H_]=sn[V_]=sn[G_]=sn[W_]=sn[j_]=!1;function iv(o){return he(o)&&Ll(o.length)&&!!sn[T(o)]}var rv=iv;function sv(o){return function(l){return o(l)}}var Nl=sv,Vd=e&&!e.nodeType&&e,Eo=Vd&&!0&&r&&!r.nodeType&&r,ov=Eo&&Eo.exports===Vd,Ol=ov&&We.process,av=(function(){try{var o=Eo&&Eo.require&&Eo.require("util").types;return o||Ol&&Ol.binding&&Ol.binding("util")}catch{}})(),bs=av,Gd=bs&&bs.isTypedArray,cv=Gd?Nl(Gd):rv,Wd=cv,lv=Object.prototype,uv=lv.hasOwnProperty;function hv(o,l){var d=Te(o),y=!d&&Bd(o),M=!d&&!y&&Pa(o),C=!d&&!y&&!M&&Wd(o),B=d||y||M||C,K=B?S_(o.length,String):[],Q=K.length;for(var oe in o)(l||uv.call(o,oe))&&!(B&&(oe=="length"||M&&(oe=="offset"||oe=="parent")||C&&(oe=="buffer"||oe=="byteLength"||oe=="byteOffset")||yo(oe,Q)))&&K.push(oe);return K}var jd=hv;function dv(o,l){return function(d){return o(l(d))}}var Xd=dv,fv=Xd(Object.keys,Object),pv=fv,mv=Object.prototype,gv=mv.hasOwnProperty;function _v(o){if(!Fl(o))return pv(o);var l=[];for(var d in Object(o))gv.call(o,d)&&d!="constructor"&&l.push(d);return l}var vv=_v;function yv(o){return Nd(o)?jd(o):vv(o)}var Mo=yv;function xv(o){var l=[];if(o!=null)for(var d in Object(o))l.push(d);return l}var bv=xv,Sv=Object.prototype,Ev=Sv.hasOwnProperty;function Mv(o){if(!Ge(o))return bv(o);var l=Fl(o),d=[];for(var y in o)y=="constructor"&&(l||!Ev.call(o,y))||d.push(y);return d}var Tv=Mv;function wv(o){return Nd(o)?jd(o,!0):Tv(o)}var Ul=wv;function Av(o,l){for(var d=-1,y=l.length,M=o.length;++d<y;)o[M+d]=l[d];return o}var qd=Av,Rv=Xd(Object.getPrototypeOf,Object),Bl=Rv,Pv="[object Object]",Cv=Function.prototype,Dv=Object.prototype,Yd=Cv.toString,Iv=Dv.hasOwnProperty,Lv=Yd.call(Object);function Fv(o){if(!he(o)||T(o)!=Pv)return!1;var l=Bl(o);if(l===null)return!0;var d=Iv.call(l,"constructor")&&l.constructor;return typeof d=="function"&&d instanceof d&&Yd.call(d)==Lv}var Nv=Fv;function Ov(o,l,d){var y=-1,M=o.length;l<0&&(l=-l>M?0:M+l),d=d>M?M:d,d<0&&(d+=M),M=l>d?0:d-l>>>0,l>>>=0;for(var C=Array(M);++y<M;)C[y]=o[y+l];return C}var Kd=Ov;function Uv(o,l,d){var y=o.length;return d=d===void 0?y:d,!l&&d>=y?o:Kd(o,l,d)}var Bv=Uv,kv="\\ud800-\\udfff",zv="\\u0300-\\u036f",Hv="\\ufe20-\\ufe2f",Vv="\\u20d0-\\u20ff",Gv=zv+Hv+Vv,Wv="\\ufe0e\\ufe0f",jv="\\u200d",Xv=RegExp("["+jv+kv+Gv+Wv+"]");function qv(o){return Xv.test(o)}var kl=qv;function Yv(o){return o.split("")}var Kv=Yv,$d="\\ud800-\\udfff",$v="\\u0300-\\u036f",Zv="\\ufe20-\\ufe2f",Qv="\\u20d0-\\u20ff",Jv=$v+Zv+Qv,e0="\\ufe0e\\ufe0f",t0="["+$d+"]",zl="["+Jv+"]",Hl="\\ud83c[\\udffb-\\udfff]",n0="(?:"+zl+"|"+Hl+")",Zd="[^"+$d+"]",Qd="(?:\\ud83c[\\udde6-\\uddff]){2}",Jd="[\\ud800-\\udbff][\\udc00-\\udfff]",i0="\\u200d",ef=n0+"?",tf="["+e0+"]?",r0="(?:"+i0+"(?:"+[Zd,Qd,Jd].join("|")+")"+tf+ef+")*",s0=tf+ef+r0,o0="(?:"+[Zd+zl+"?",zl,Qd,Jd,t0].join("|")+")",a0=RegExp(Hl+"(?="+Hl+")|"+o0+s0,"g");function c0(o){return o.match(a0)||[]}var l0=c0;function u0(o){return kl(o)?l0(o):Kv(o)}var h0=u0;function d0(o,l,d){return o===o&&(d!==void 0&&(o=o<=d?o:d),l!==void 0&&(o=o>=l?o:l)),o}var f0=d0;function p0(o,l,d){return d===void 0&&(d=l,l=void 0),d!==void 0&&(d=b(d),d=d===d?d:0),l!==void 0&&(l=b(l),l=l===l?l:0),f0(b(o),l,d)}var nf=p0;function m0(){this.__data__=new ps,this.size=0}var g0=m0;function _0(o){var l=this.__data__,d=l.delete(o);return this.size=l.size,d}var v0=_0;function y0(o){return this.__data__.get(o)}var x0=y0;function b0(o){return this.__data__.has(o)}var S0=b0,E0=200;function M0(o,l){var d=this.__data__;if(d instanceof ps){var y=d.__data__;if(!Pr||y.length<E0-1)return y.push([o,l]),this.size=++d.size,this;d=this.__data__=new ms(y)}return d.set(o,l),this.size=d.size,this}var T0=M0;function Ss(o){var l=this.__data__=new ps(o);this.size=l.size}Ss.prototype.clear=g0,Ss.prototype.delete=v0,Ss.prototype.get=x0,Ss.prototype.has=S0,Ss.prototype.set=T0;var To=Ss;function w0(o,l){return o&&Ra(l,Mo(l),o)}var A0=w0;function R0(o,l){return o&&Ra(l,Ul(l),o)}var P0=R0,rf=e&&!e.nodeType&&e,sf=rf&&!0&&r&&!r.nodeType&&r,C0=sf&&sf.exports===rf,of=C0?me.Buffer:void 0,af=of?of.allocUnsafe:void 0;function D0(o,l){if(l)return o.slice();var d=o.length,y=af?af(d):new o.constructor(d);return o.copy(y),y}var I0=D0;function L0(o,l){for(var d=-1,y=o==null?0:o.length,M=0,C=[];++d<y;){var B=o[d];l(B,d,o)&&(C[M++]=B)}return C}var F0=L0;function N0(){return[]}var cf=N0,O0=Object.prototype,U0=O0.propertyIsEnumerable,lf=Object.getOwnPropertySymbols,B0=lf?function(o){return o==null?[]:(o=Object(o),F0(lf(o),function(l){return U0.call(o,l)}))}:cf,Vl=B0;function k0(o,l){return Ra(o,Vl(o),l)}var z0=k0,H0=Object.getOwnPropertySymbols,V0=H0?function(o){for(var l=[];o;)qd(l,Vl(o)),o=Bl(o);return l}:cf,uf=V0;function G0(o,l){return Ra(o,uf(o),l)}var W0=G0;function j0(o,l,d){var y=l(o);return Te(o)?y:qd(y,d(o))}var hf=j0;function X0(o){return hf(o,Mo,Vl)}var Gl=X0;function q0(o){return hf(o,Ul,uf)}var Y0=q0,K0=Ht(me,"DataView"),Wl=K0,$0=Ht(me,"Promise"),jl=$0,Z0=Ht(me,"Set"),Xl=Z0,df="[object Map]",Q0="[object Object]",ff="[object Promise]",pf="[object Set]",mf="[object WeakMap]",gf="[object DataView]",J0=_e(Wl),ey=_e(Pr),ty=_e(jl),ny=_e(Xl),iy=_e(Ur),Br=T;(Wl&&Br(new Wl(new ArrayBuffer(1)))!=gf||Pr&&Br(new Pr)!=df||jl&&Br(jl.resolve())!=ff||Xl&&Br(new Xl)!=pf||Ur&&Br(new Ur)!=mf)&&(Br=function(o){var l=T(o),d=l==Q0?o.constructor:void 0,y=d?_e(d):"";if(y)switch(y){case J0:return gf;case ey:return df;case ty:return ff;case ny:return pf;case iy:return mf}return l});var wo=Br,ry=Object.prototype,sy=ry.hasOwnProperty;function oy(o){var l=o.length,d=new o.constructor(l);return l&&typeof o[0]=="string"&&sy.call(o,"index")&&(d.index=o.index,d.input=o.input),d}var ay=oy,cy=me.Uint8Array,Ca=cy;function ly(o){var l=new o.constructor(o.byteLength);return new Ca(l).set(new Ca(o)),l}var ql=ly;function uy(o,l){var d=l?ql(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.byteLength)}var hy=uy,dy=/\w*$/;function fy(o){var l=new o.constructor(o.source,dy.exec(o));return l.lastIndex=o.lastIndex,l}var py=fy,_f=Se?Se.prototype:void 0,vf=_f?_f.valueOf:void 0;function my(o){return vf?Object(vf.call(o)):{}}var gy=my;function _y(o,l){var d=l?ql(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.length)}var vy=_y,yy="[object Boolean]",xy="[object Date]",by="[object Map]",Sy="[object Number]",Ey="[object RegExp]",My="[object Set]",Ty="[object String]",wy="[object Symbol]",Ay="[object ArrayBuffer]",Ry="[object DataView]",Py="[object Float32Array]",Cy="[object Float64Array]",Dy="[object Int8Array]",Iy="[object Int16Array]",Ly="[object Int32Array]",Fy="[object Uint8Array]",Ny="[object Uint8ClampedArray]",Oy="[object Uint16Array]",Uy="[object Uint32Array]";function By(o,l,d){var y=o.constructor;switch(l){case Ay:return ql(o);case yy:case xy:return new y(+o);case Ry:return hy(o,d);case Py:case Cy:case Dy:case Iy:case Ly:case Fy:case Ny:case Oy:case Uy:return vy(o,d);case by:return new y;case Sy:case Ty:return new y(o);case Ey:return py(o);case My:return new y;case wy:return gy(o)}}var ky=By;function zy(o){return typeof o.constructor=="function"&&!Fl(o)?u_(Bl(o)):{}}var Hy=zy,Vy="[object Map]";function Gy(o){return he(o)&&wo(o)==Vy}var Wy=Gy,yf=bs&&bs.isMap,jy=yf?Nl(yf):Wy,Xy=jy,qy="[object Set]";function Yy(o){return he(o)&&wo(o)==qy}var Ky=Yy,xf=bs&&bs.isSet,$y=xf?Nl(xf):Ky,Zy=$y,Qy=1,Jy=2,ex=4,bf="[object Arguments]",tx="[object Array]",nx="[object Boolean]",ix="[object Date]",rx="[object Error]",Sf="[object Function]",sx="[object GeneratorFunction]",ox="[object Map]",ax="[object Number]",Ef="[object Object]",cx="[object RegExp]",lx="[object Set]",ux="[object String]",hx="[object Symbol]",dx="[object WeakMap]",fx="[object ArrayBuffer]",px="[object DataView]",mx="[object Float32Array]",gx="[object Float64Array]",_x="[object Int8Array]",vx="[object Int16Array]",yx="[object Int32Array]",xx="[object Uint8Array]",bx="[object Uint8ClampedArray]",Sx="[object Uint16Array]",Ex="[object Uint32Array]",Jt={};Jt[bf]=Jt[tx]=Jt[fx]=Jt[px]=Jt[nx]=Jt[ix]=Jt[mx]=Jt[gx]=Jt[_x]=Jt[vx]=Jt[yx]=Jt[ox]=Jt[ax]=Jt[Ef]=Jt[cx]=Jt[lx]=Jt[ux]=Jt[hx]=Jt[xx]=Jt[bx]=Jt[Sx]=Jt[Ex]=!0,Jt[rx]=Jt[Sf]=Jt[dx]=!1;function Da(o,l,d,y,M,C){var B,K=l&Qy,Q=l&Jy,oe=l&ex;if(d&&(B=M?d(o,y,M,C):d(o)),B!==void 0)return B;if(!Ge(o))return o;var xe=Te(o);if(xe){if(B=ay(o),!K)return d_(o,B)}else{var Ee=wo(o),Ie=Ee==Sf||Ee==sx;if(Pa(o))return I0(o,K);if(Ee==Ef||Ee==bf||Ie&&!M){if(B=Q||Ie?{}:Hy(o),!K)return Q?W0(o,P0(B,o)):z0(o,A0(B,o))}else{if(!Jt[Ee])return M?o:{};B=ky(o,Ee,K)}}C||(C=new To);var tt=C.get(o);if(tt)return tt;C.set(o,B),Zy(o)?o.forEach(function(wt){B.add(Da(wt,l,d,wt,o,C))}):Xy(o)&&o.forEach(function(wt,gt){B.set(gt,Da(wt,l,d,gt,o,C))});var Xe=oe?Q?Y0:Gl:Q?Ul:Mo,_t=xe?void 0:Xe(o);return p_(_t||o,function(wt,gt){_t&&(gt=wt,wt=o[gt]),vo(B,gt,Da(wt,l,d,gt,o,C))}),B}var Mx=Da,Tx=1,wx=4;function Ax(o){return Mx(o,Tx|wx)}var Rx=Ax,Px="__lodash_hash_undefined__";function Cx(o){return this.__data__.set(o,Px),this}var Dx=Cx;function Ix(o){return this.__data__.has(o)}var Lx=Ix;function Ia(o){var l=-1,d=o==null?0:o.length;for(this.__data__=new ms;++l<d;)this.add(o[l])}Ia.prototype.add=Ia.prototype.push=Dx,Ia.prototype.has=Lx;var Fx=Ia;function Nx(o,l){for(var d=-1,y=o==null?0:o.length;++d<y;)if(l(o[d],d,o))return!0;return!1}var Ox=Nx;function Ux(o,l){return o.has(l)}var Bx=Ux,kx=1,zx=2;function Hx(o,l,d,y,M,C){var B=d&kx,K=o.length,Q=l.length;if(K!=Q&&!(B&&Q>K))return!1;var oe=C.get(o),xe=C.get(l);if(oe&&xe)return oe==l&&xe==o;var Ee=-1,Ie=!0,tt=d&zx?new Fx:void 0;for(C.set(o,l),C.set(l,o);++Ee<K;){var Xe=o[Ee],_t=l[Ee];if(y)var wt=B?y(_t,Xe,Ee,l,o,C):y(Xe,_t,Ee,o,l,C);if(wt!==void 0){if(wt)continue;Ie=!1;break}if(tt){if(!Ox(l,function(gt,Ut){if(!Bx(tt,Ut)&&(Xe===gt||M(Xe,gt,d,y,C)))return tt.push(Ut)})){Ie=!1;break}}else if(!(Xe===_t||M(Xe,_t,d,y,C))){Ie=!1;break}}return C.delete(o),C.delete(l),Ie}var Mf=Hx;function Vx(o){var l=-1,d=Array(o.size);return o.forEach(function(y,M){d[++l]=[M,y]}),d}var Gx=Vx;function Wx(o){var l=-1,d=Array(o.size);return o.forEach(function(y){d[++l]=y}),d}var jx=Wx,Xx=1,qx=2,Yx="[object Boolean]",Kx="[object Date]",$x="[object Error]",Zx="[object Map]",Qx="[object Number]",Jx="[object RegExp]",eb="[object Set]",tb="[object String]",nb="[object Symbol]",ib="[object ArrayBuffer]",rb="[object DataView]",Tf=Se?Se.prototype:void 0,Yl=Tf?Tf.valueOf:void 0;function sb(o,l,d,y,M,C,B){switch(d){case rb:if(o.byteLength!=l.byteLength||o.byteOffset!=l.byteOffset)return!1;o=o.buffer,l=l.buffer;case ib:return!(o.byteLength!=l.byteLength||!C(new Ca(o),new Ca(l)));case Yx:case Kx:case Qx:return An(+o,+l);case $x:return o.name==l.name&&o.message==l.message;case Jx:case tb:return o==l+"";case Zx:var K=Gx;case eb:var Q=y&Xx;if(K||(K=jx),o.size!=l.size&&!Q)return!1;var oe=B.get(o);if(oe)return oe==l;y|=qx,B.set(o,l);var xe=Mf(K(o),K(l),y,M,C,B);return B.delete(o),xe;case nb:if(Yl)return Yl.call(o)==Yl.call(l)}return!1}var ob=sb,ab=1,cb=Object.prototype,lb=cb.hasOwnProperty;function ub(o,l,d,y,M,C){var B=d&ab,K=Gl(o),Q=K.length,oe=Gl(l),xe=oe.length;if(Q!=xe&&!B)return!1;for(var Ee=Q;Ee--;){var Ie=K[Ee];if(!(B?Ie in l:lb.call(l,Ie)))return!1}var tt=C.get(o),Xe=C.get(l);if(tt&&Xe)return tt==l&&Xe==o;var _t=!0;C.set(o,l),C.set(l,o);for(var wt=B;++Ee<Q;){Ie=K[Ee];var gt=o[Ie],Ut=l[Ie];if(y)var Fn=B?y(Ut,gt,Ie,l,o,C):y(gt,Ut,Ie,o,l,C);if(!(Fn===void 0?gt===Ut||M(gt,Ut,d,y,C):Fn)){_t=!1;break}wt||(wt=Ie=="constructor")}if(_t&&!wt){var Yn=o.constructor,Nn=l.constructor;Yn!=Nn&&"constructor"in o&&"constructor"in l&&!(typeof Yn=="function"&&Yn instanceof Yn&&typeof Nn=="function"&&Nn instanceof Nn)&&(_t=!1)}return C.delete(o),C.delete(l),_t}var hb=ub,db=1,wf="[object Arguments]",Af="[object Array]",La="[object Object]",fb=Object.prototype,Rf=fb.hasOwnProperty;function pb(o,l,d,y,M,C){var B=Te(o),K=Te(l),Q=B?Af:wo(o),oe=K?Af:wo(l);Q=Q==wf?La:Q,oe=oe==wf?La:oe;var xe=Q==La,Ee=oe==La,Ie=Q==oe;if(Ie&&Pa(o)){if(!Pa(l))return!1;B=!0,xe=!1}if(Ie&&!xe)return C||(C=new To),B||Wd(o)?Mf(o,l,d,y,M,C):ob(o,l,Q,d,y,M,C);if(!(d&db)){var tt=xe&&Rf.call(o,"__wrapped__"),Xe=Ee&&Rf.call(l,"__wrapped__");if(tt||Xe){var _t=tt?o.value():o,wt=Xe?l.value():l;return C||(C=new To),M(_t,wt,d,y,C)}}return Ie?(C||(C=new To),hb(o,l,d,y,M,C)):!1}var mb=pb;function Pf(o,l,d,y,M){return o===l?!0:o==null||l==null||!he(o)&&!he(l)?o!==o&&l!==l:mb(o,l,d,y,Pf,M)}var Cf=Pf,gb=1,_b=2;function vb(o,l,d,y){var M=d.length,C=M,B=!y;if(o==null)return!C;for(o=Object(o);M--;){var K=d[M];if(B&&K[2]?K[1]!==o[K[0]]:!(K[0]in o))return!1}for(;++M<C;){K=d[M];var Q=K[0],oe=o[Q],xe=K[1];if(B&&K[2]){if(oe===void 0&&!(Q in o))return!1}else{var Ee=new To;if(y)var Ie=y(oe,xe,Q,o,l,Ee);if(!(Ie===void 0?Cf(xe,oe,gb|_b,y,Ee):Ie))return!1}}return!0}var yb=vb;function xb(o){return o===o&&!Ge(o)}var Df=xb;function bb(o){for(var l=Mo(o),d=l.length;d--;){var y=l[d],M=o[y];l[d]=[y,M,Df(M)]}return l}var Sb=bb;function Eb(o,l){return function(d){return d==null?!1:d[o]===l&&(l!==void 0||o in Object(d))}}var If=Eb;function Mb(o){var l=Sb(o);return l.length==1&&l[0][2]?If(l[0][0],l[0][1]):function(d){return d===o||yb(d,o,l)}}var Tb=Mb;function wb(o,l){return o!=null&&l in Object(o)}var Ab=wb;function Rb(o,l,d){l=Dr(l,o);for(var y=-1,M=l.length,C=!1;++y<M;){var B=gi(l[y]);if(!(C=o!=null&&d(o,B)))break;o=o[B]}return C||++y!=M?C:(M=o==null?0:o.length,!!M&&Ll(M)&&yo(B,M)&&(Te(o)||Bd(o)))}var Pb=Rb;function Cb(o,l){return o!=null&&Pb(o,l,Ab)}var Db=Cb,Ib=1,Lb=2;function Fb(o,l){return be(o)&&Df(l)?If(gi(o),l):function(d){var y=Bi(d,o);return y===void 0&&y===l?Db(d,o):Cf(l,y,Ib|Lb)}}var Nb=Fb;function Ob(o){return function(l){return l==null?void 0:l[o]}}var Lf=Ob;function Ub(o){return function(l){return _s(l,o)}}var Bb=Ub;function kb(o){return be(o)?Lf(gi(o)):Bb(o)}var zb=kb;function Hb(o){return typeof o=="function"?o:o==null?Aa:typeof o=="object"?Te(o)?Nb(o[0],o[1]):Tb(o):zb(o)}var Vb=Hb;function Gb(o){return function(l,d,y){for(var M=-1,C=Object(l),B=y(l),K=B.length;K--;){var Q=B[o?K:++M];if(d(C[Q],Q,C)===!1)break}return l}}var Wb=Gb,jb=Wb(),Xb=jb;function qb(o,l){return o&&Xb(o,l,Mo)}var Yb=qb,Kb=function(){return me.Date.now()},Kl=Kb,$b="Expected a function",Zb=Math.max,Qb=Math.min;function Jb(o,l,d){var y,M,C,B,K,Q,oe=0,xe=!1,Ee=!1,Ie=!0;if(typeof o!="function")throw new TypeError($b);l=b(l)||0,Ge(d)&&(xe=!!d.leading,Ee="maxWait"in d,C=Ee?Zb(b(d.maxWait)||0,l):C,Ie="trailing"in d?!!d.trailing:Ie);function tt(Kt){var On=y,ii=M;return y=M=void 0,oe=Kt,B=o.apply(ii,On),B}function Xe(Kt){return oe=Kt,K=setTimeout(gt,l),xe?tt(Kt):B}function _t(Kt){var On=Kt-Q,ii=Kt-oe,Ri=l-On;return Ee?Qb(Ri,C-ii):Ri}function wt(Kt){var On=Kt-Q,ii=Kt-oe;return Q===void 0||On>=l||On<0||Ee&&ii>=C}function gt(){var Kt=Kl();if(wt(Kt))return Ut(Kt);K=setTimeout(gt,_t(Kt))}function Ut(Kt){return K=void 0,Ie&&y?tt(Kt):(y=M=void 0,B)}function Fn(){K!==void 0&&clearTimeout(K),oe=0,y=Q=M=K=void 0}function Yn(){return K===void 0?B:Ut(Kl())}function Nn(){var Kt=Kl(),On=wt(Kt);if(y=arguments,M=this,Q=Kt,On){if(K===void 0)return Xe(Q);if(Ee)return clearTimeout(K),K=setTimeout(gt,l),tt(Q)}return K===void 0&&(K=setTimeout(gt,l)),B}return Nn.cancel=Fn,Nn.flush=Yn,Nn}var eS=Jb;function tS(o){var l=o==null?0:o.length;return l?o[l-1]:void 0}var nS=tS;function iS(o,l){return l.length<2?o:_s(o,Kd(l,0,-1))}var rS=iS;function sS(o){return typeof o=="number"&&o==Pn(o)}var oS=sS;function aS(o,l){var d={};return l=Vb(l),Yb(o,function(y,M,C){ki(d,M,l(y,M,C))}),d}var cS=aS;function lS(o,l){return l=Dr(l,o),o=rS(o,l),o==null||delete o[gi(nS(l))]}var uS=lS,hS=9007199254740991,dS=Math.floor;function fS(o,l){var d="";if(!o||l<1||l>hS)return d;do l%2&&(d+=o),l=dS(l/2),l&&(o+=o);while(l);return d}var Ff=fS,pS=Lf("length"),mS=pS,Nf="\\ud800-\\udfff",gS="\\u0300-\\u036f",_S="\\ufe20-\\ufe2f",vS="\\u20d0-\\u20ff",yS=gS+_S+vS,xS="\\ufe0e\\ufe0f",bS="["+Nf+"]",$l="["+yS+"]",Zl="\\ud83c[\\udffb-\\udfff]",SS="(?:"+$l+"|"+Zl+")",Of="[^"+Nf+"]",Uf="(?:\\ud83c[\\udde6-\\uddff]){2}",Bf="[\\ud800-\\udbff][\\udc00-\\udfff]",ES="\\u200d",kf=SS+"?",zf="["+xS+"]?",MS="(?:"+ES+"(?:"+[Of,Uf,Bf].join("|")+")"+zf+kf+")*",TS=zf+kf+MS,wS="(?:"+[Of+$l+"?",$l,Uf,Bf,bS].join("|")+")",Hf=RegExp(Zl+"(?="+Zl+")|"+wS+TS,"g");function AS(o){for(var l=Hf.lastIndex=0;Hf.test(o);)++l;return l}var RS=AS;function PS(o){return kl(o)?RS(o):mS(o)}var Vf=PS,CS=Math.ceil;function DS(o,l){l=l===void 0?" ":fa(l);var d=l.length;if(d<2)return d?Ff(l,o):l;var y=Ff(l,CS(o/Vf(l)));return kl(l)?Bv(h0(y),0,o).join(""):y.slice(0,o)}var IS=DS;function LS(o,l,d){o=gs(o),l=Pn(l);var y=l?Vf(o):0;return l&&y<l?IS(l-y,d)+o:o}var Ao=LS;function FS(o,l){return o==null?!0:uS(o,l)}var Gf=FS,NS=5*1e3,OS=class{constructor(o){S(this,"_cache",new ar),S(this,"_keepHotUntapDebounce"),de(this,o)}get type(){return"Theatre_SheetObject_PublicAPI"}get props(){return Y(this).propsP}get sheet(){return Y(this).sheet.publicApi}get project(){return Y(this).sheet.project.publicApi}get address(){return g({},Y(this).address)}_valuesPrism(){return this._cache.get("_valuesPrism",()=>{const o=Y(this);return(0,bo.prism)(()=>(0,bo.val)(o.getValues().getValue()))})}onValuesChange(o,l){return Su(this._valuesPrism(),o,l)}get value(){const o=this._valuesPrism();{if(!o.isHot){this._keepHotUntapDebounce!=null&&this._keepHotUntapDebounce.flush();const l=o.keepHot();this._keepHotUntapDebounce=eS(()=>{l(),this._keepHotUntapDebounce=void 0},NS)}this._keepHotUntapDebounce&&this._keepHotUntapDebounce()}return o.getValue()}set initialValue(o){Y(this).setInitialValue(o)}};function US(o){const l=new WeakMap;return d=>(l.has(d)||l.set(d,o(d)),l.get(d))}function Fa(o){return o.type==="compound"||o.type==="enum"}function Ql(o,l){if(!o)return;const[d,...y]=l;if(d===void 0)return o;if(!Fa(o))return;const M=o.type==="enum"?o.cases[d]:o.props[d];return Ql(M,y)}function BS(o){return!Fa(o)}var kS=class{constructor(o,l,d){this.sheet=o,this.template=l,this.nativeObject=d,S(this,"$$isPointerToPrismProvider",!0),S(this,"address"),S(this,"publicApi"),S(this,"_initialValue",new Wt.Atom({})),S(this,"_cache",new ar),S(this,"_logger"),S(this,"_internalUtilCtx"),this._logger=o._logger.named("SheetObject",l.address.objectKey),this._logger._trace("creating object"),this._internalUtilCtx={logger:this._logger.utilFor.internal()},this.address=x(g({},l.address),{sheetInstanceId:o.address.sheetInstanceId}),this.publicApi=new OS(this)}get type(){return"Theatre_SheetObject"}getValues(){return this._cache.get("getValues()",()=>(0,Wt.prism)(()=>{const o=(0,Wt.val)(this.template.getDefaultValues()),l=(0,Wt.val)(this._initialValue.pointer),d=Wt.prism.memo("withInitialCache",()=>new WeakMap,[]),y=Fr(o,l,d),M=(0,Wt.val)(this.template.getStaticValues()),C=Wt.prism.memo("withStatics",()=>new WeakMap,[]);let K=Fr(y,M,C),Q;{const xe=Wt.prism.memo("seq",()=>this.getSequencedValues(),[]),Ee=Wt.prism.memo("withSeqsCache",()=>new WeakMap,[]);Q=(0,Wt.val)((0,Wt.val)(xe)),K=Fr(K,Q,Ee)}return Sa("finalAtom",K).pointer}))}getValueByPointer(o){const l=(0,Wt.val)(this.getValues()),{path:d}=(0,Wt.getPointerParts)(o);return(0,Wt.val)(Nr(l,d))}pointerToPrism(o){const{path:l}=(0,Wt.getPointerParts)(o);return(0,Wt.prism)(()=>{const d=(0,Wt.val)(this.getValues());return(0,Wt.val)(Nr(d,l))})}getSequencedValues(){return(0,Wt.prism)(()=>{const o=Wt.prism.memo("tracksToProcess",()=>this.template.getArrayOfValidSequenceTracks(),[]),l=(0,Wt.val)(o),d=new Wt.Atom({}),y=(0,Wt.val)(this.template.configPointer);return Wt.prism.effect("processTracks",()=>{const M=[];for(const{trackId:C,pathToProp:B}of l){const K=this._trackIdToPrism(C),Q=Ql(y,B),oe=Q.deserializeAndSanitize,xe=Q.interpolate,Ee=()=>{const tt=K.getValue();if(!tt)return d.setByPointer(Ut=>Nr(Ut,B),void 0);const Xe=oe(tt.left),_t=Xe===void 0?Q.default:Xe;if(tt.right===void 0)return d.setByPointer(Ut=>Nr(Ut,B),_t);const wt=oe(tt.right),gt=wt===void 0?Q.default:wt;return d.setByPointer(Ut=>Nr(Ut,B),xe(_t,gt,tt.progression))},Ie=K.onStale(Ee);Ee(),M.push(Ie)}return()=>{for(const C of M)C()}},[y,...l]),d.pointer})}_trackIdToPrism(o){const l=this.template.project.pointers.historic.sheetsById[this.address.sheetId].sequence.tracksByObject[this.address.objectKey].trackData[o],d=this.sheet.getSequence().positionPrism;return Ml(this._internalUtilCtx,l,d)}get propsP(){return this._cache.get("propsP",()=>(0,Wt.pointer)({root:this,path:[]}))}validateValue(o,l){}setInitialValue(o){this.validateValue(this.propsP,o),this._initialValue.set(o)}};function en(o){return function(d,y){return o(d,y())}}var ei={_hmm:ti(524),_todo:ti(522),_error:ti(521),errorDev:ti(529),errorPublic:ti(545),_kapow:ti(268),_warn:ti(265),warnDev:ti(273),warnPublic:ti(289),_debug:ti(137),debugDev:ti(145),_trace:ti(73),traceDev:ti(81)};function ti(o){return Object.freeze({audience:kr(o,8)?"internal":kr(o,16)?"dev":"public",category:kr(o,4)?"troubleshooting":kr(o,2)?"todo":"general",level:kr(o,512)?512:kr(o,256)?256:kr(o,128)?128:64})}function kr(o,l){return(o&l)===l}function tn(o,l){return((l&32)===32?!0:(l&16)===16?o.dev:(l&8)===8?o.internal:!1)&&o.min<=l}var zi={loggingConsoleStyle:!0,loggerConsoleStyle:!0,includes:Object.freeze({internal:!1,dev:!1,min:256}),filtered:function(){},include:function(){return{}},create:null,creatExt:null,named(o,l,d){return this.create({names:[...o.names,{name:l,key:d}]})},style:{bold:void 0,italic:void 0,cssMemo:new Map([["",""]]),collapseOnRE:/[a-z- ]+/g,color:void 0,collapsed(o){if(o.length<5)return o;const l=o.replace(this.collapseOnRE,"");return this.cssMemo.has(l)||this.cssMemo.set(l,this.css(o)),l},css(o){var l,d,y,M;const C=this.cssMemo.get(o);if(C)return C;let B="color:".concat((d=(l=this.color)==null?void 0:l.call(this,o))!=null?d:"hsl(".concat((o.charCodeAt(0)+o.charCodeAt(o.length-1))%360,", 100%, 60%)"));return(y=this.bold)!=null&&y.test(o)&&(B+=";font-weight:600"),(M=this.italic)!=null&&M.test(o)&&(B+=";font-style:italic"),this.cssMemo.set(o,B),B}}};function Wf(o=console,l={}){const d=x(g({},zi),{includes:g({},zi.includes)}),y={styled:VS.bind(d,o),noStyle:WS.bind(d,o)},M=HS.bind(d);function C(){return d.loggingConsoleStyle&&d.loggerConsoleStyle?y.styled:y.noStyle}return d.create=C(),{configureLogger(B){var K;B==="console"?(d.loggerConsoleStyle=zi.loggerConsoleStyle,d.create=C()):B.type==="console"?(d.loggerConsoleStyle=(K=B.style)!=null?K:zi.loggerConsoleStyle,d.create=C()):B.type==="keyed"?(d.creatExt=Q=>B.keyed(Q.names),d.create=M):B.type==="named"&&(d.creatExt=zS.bind(null,B.named),d.create=M)},configureLogging(B){var K,Q,oe,xe,Ee;d.includes.dev=(K=B.dev)!=null?K:zi.includes.dev,d.includes.internal=(Q=B.internal)!=null?Q:zi.includes.internal,d.includes.min=(oe=B.min)!=null?oe:zi.includes.min,d.include=(xe=B.include)!=null?xe:zi.include,d.loggingConsoleStyle=(Ee=B.consoleStyle)!=null?Ee:zi.loggingConsoleStyle,d.create=C()},getLogger(){return d.create({names:[]})}}}function zS(o,l){const d=[];for(let{name:y,key:M}of l.names)d.push(M==null?y:"".concat(y," (").concat(M,")"));return o(d)}function HS(o){const l=g(g({},this.includes),this.include(o)),d=this.filtered,y=this.named.bind(this,o),M=this.creatExt(o),C=tn(l,524),B=tn(l,522),K=tn(l,521),Q=tn(l,529),oe=tn(l,545),xe=tn(l,265),Ee=tn(l,268),Ie=tn(l,273),tt=tn(l,289),Xe=tn(l,137),_t=tn(l,145),wt=tn(l,73),gt=tn(l,81),Ut=C?M.error.bind(M,ei._hmm):d.bind(o,524),Fn=B?M.error.bind(M,ei._todo):d.bind(o,522),Yn=K?M.error.bind(M,ei._error):d.bind(o,521),Nn=Q?M.error.bind(M,ei.errorDev):d.bind(o,529),Kt=oe?M.error.bind(M,ei.errorPublic):d.bind(o,545),On=Ee?M.warn.bind(M,ei._kapow):d.bind(o,268),ii=xe?M.warn.bind(M,ei._warn):d.bind(o,265),Ri=Ie?M.warn.bind(M,ei.warnDev):d.bind(o,273),jr=tt?M.warn.bind(M,ei.warnPublic):d.bind(o,273),Xr=Xe?M.debug.bind(M,ei._debug):d.bind(o,137),qr=_t?M.debug.bind(M,ei.debugDev):d.bind(o,145),Yr=wt?M.trace.bind(M,ei._trace):d.bind(o,73),Kr=gt?M.trace.bind(M,ei.traceDev):d.bind(o,81),fn={_hmm:Ut,_todo:Fn,_error:Yn,errorDev:Nn,errorPublic:Kt,_kapow:On,_warn:ii,warnDev:Ri,warnPublic:jr,_debug:Xr,debugDev:qr,_trace:Yr,traceDev:Kr,lazy:{_hmm:C?en(Ut):Ut,_todo:B?en(Fn):Fn,_error:K?en(Yn):Yn,errorDev:Q?en(Nn):Nn,errorPublic:oe?en(Kt):Kt,_kapow:Ee?en(On):On,_warn:xe?en(ii):ii,warnDev:Ie?en(Ri):Ri,warnPublic:tt?en(jr):jr,_debug:Xe?en(Xr):Xr,debugDev:_t?en(qr):qr,_trace:wt?en(Yr):Yr,traceDev:gt?en(Kr):Kr},named:y,utilFor:{internal(){return{debug:fn._debug,error:fn._error,warn:fn._warn,trace:fn._trace,named(ri,nn){return fn.named(ri,nn).utilFor.internal()}}},dev(){return{debug:fn.debugDev,error:fn.errorDev,warn:fn.warnDev,trace:fn.traceDev,named(ri,nn){return fn.named(ri,nn).utilFor.dev()}}},public(){return{error:fn.errorPublic,warn:fn.warnPublic,debug(ri,nn){fn._warn('(public "debug" filtered out) '.concat(ri),nn)},trace(ri,nn){fn._warn('(public "trace" filtered out) '.concat(ri),nn)},named(ri,nn){return fn.named(ri,nn).utilFor.public()}}}}};return fn}function VS(o,l){const d=g(g({},this.includes),this.include(l)),y=[];let M="";for(let Q=0;Q<l.names.length;Q++){const{name:oe,key:xe}=l.names[Q];if(M+=" %c".concat(oe),y.push(this.style.css(oe)),xe!=null){const Ee="%c#".concat(xe);M+=Ee,y.push(this.style.css(Ee))}}const C=this.filtered,B=this.named.bind(this,l),K=[M,...y];return jf(C,l,d,o,K,GS(K),B)}function GS(o){const l=o.slice(0);for(let d=1;d<l.length;d++)l[d]+=";background-color:#e0005a;padding:2px;color:white";return l}function WS(o,l){const d=g(g({},this.includes),this.include(l));let y="";for(let K=0;K<l.names.length;K++){const{name:Q,key:oe}=l.names[K];y+=" ".concat(Q),oe!=null&&(y+="#".concat(oe))}const M=this.filtered,C=this.named.bind(this,l),B=[y];return jf(M,l,d,o,B,B,C)}function jf(o,l,d,y,M,C,B){const K=tn(d,524),Q=tn(d,522),oe=tn(d,521),xe=tn(d,529),Ee=tn(d,545),Ie=tn(d,265),tt=tn(d,268),Xe=tn(d,273),_t=tn(d,289),wt=tn(d,137),gt=tn(d,145),Ut=tn(d,73),Fn=tn(d,81),Yn=K?y.error.bind(y,...M):o.bind(l,524),Nn=Q?y.error.bind(y,...M):o.bind(l,522),Kt=oe?y.error.bind(y,...M):o.bind(l,521),On=xe?y.error.bind(y,...M):o.bind(l,529),ii=Ee?y.error.bind(y,...M):o.bind(l,545),Ri=tt?y.warn.bind(y,...C):o.bind(l,268),jr=Ie?y.warn.bind(y,...M):o.bind(l,265),Xr=Xe?y.warn.bind(y,...M):o.bind(l,273),qr=_t?y.warn.bind(y,...M):o.bind(l,273),Yr=wt?y.info.bind(y,...M):o.bind(l,137),Kr=gt?y.info.bind(y,...M):o.bind(l,145),fn=Ut?y.debug.bind(y,...M):o.bind(l,73),ri=Fn?y.debug.bind(y,...M):o.bind(l,81),nn={_hmm:Yn,_todo:Nn,_error:Kt,errorDev:On,errorPublic:ii,_kapow:Ri,_warn:jr,warnDev:Xr,warnPublic:qr,_debug:Yr,debugDev:Kr,_trace:fn,traceDev:ri,lazy:{_hmm:K?en(Yn):Yn,_todo:Q?en(Nn):Nn,_error:oe?en(Kt):Kt,errorDev:xe?en(On):On,errorPublic:Ee?en(ii):ii,_kapow:tt?en(Ri):Ri,_warn:Ie?en(jr):jr,warnDev:Xe?en(Xr):Xr,warnPublic:_t?en(qr):qr,_debug:wt?en(Yr):Yr,debugDev:gt?en(Kr):Kr,_trace:Ut?en(fn):fn,traceDev:Fn?en(ri):ri},named:B,utilFor:{internal(){return{debug:nn._debug,error:nn._error,warn:nn._warn,trace:nn._trace,named(Gi,Wi){return nn.named(Gi,Wi).utilFor.internal()}}},dev(){return{debug:nn.debugDev,error:nn.errorDev,warn:nn.warnDev,trace:nn.traceDev,named(Gi,Wi){return nn.named(Gi,Wi).utilFor.dev()}}},public(){return{error:nn.errorPublic,warn:nn.warnPublic,debug(Gi,Wi){nn._warn('(public "debug" filtered out) '.concat(Gi),Wi)},trace(Gi,Wi){nn._warn('(public "trace" filtered out) '.concat(Gi),Wi)},named(Gi,Wi){return nn.named(Gi,Wi).utilFor.public()}}}}};return nn}var Xf=Wf(console,{});Xf.configureLogging({dev:!0,min:64});var Na=Xf.getLogger().named("Theatre.js (default logger)").utilFor.dev(),qf=new WeakMap;function jS(o){const l=qf.get(o);if(l)return l;const d=new Map;return qf.set(o,d),Yf([],o,d),d}function Yf(o,l,d){for(const[y,M]of Object.entries(l.props))if(!Fa(M)){const C=[...o,y];d.set(JSON.stringify(C),d.size),Kf(C,M,d)}for(const[y,M]of Object.entries(l.props))if(Fa(M)){const C=[...o,y];d.set(JSON.stringify(C),d.size),Kf(C,M,d)}}function Kf(o,l,d){if(l.type==="compound")Yf(o,l,d);else{if(l.type==="enum")throw new Error("Enums aren't supported yet");d.set(JSON.stringify(o),d.size)}}function $f(o){return typeof o=="object"&&o!==null&&Object.keys(o).length===0}var XS=class{constructor(o,l,d,y,M){this.sheetTemplate=o,S(this,"address"),S(this,"type","Theatre_SheetObjectTemplate"),S(this,"_config"),S(this,"_temp_actions_atom"),S(this,"_cache",new ar),S(this,"project"),S(this,"pointerToSheetState"),S(this,"pointerToStaticOverrides"),this.address=x(g({},o.address),{objectKey:l}),this._config=new mn.Atom(y),this._temp_actions_atom=new mn.Atom(M),this.project=o.project,this.pointerToSheetState=this.sheetTemplate.project.pointers.historic.sheetsById[this.address.sheetId],this.pointerToStaticOverrides=this.pointerToSheetState.staticOverrides.byObject[this.address.objectKey]}get staticConfig(){return this._config.get()}get configPointer(){return this._config.pointer}get _temp_actions(){return this._temp_actions_atom.get()}get _temp_actionsPointer(){return this._temp_actions_atom.pointer}createInstance(o,l,d){return this._config.set(d),new kS(o,this,l)}reconfigure(o){this._config.set(o)}_temp_setActions(o){this._temp_actions_atom.set(o)}getDefaultValues(){return this._cache.get("getDefaultValues()",()=>(0,mn.prism)(()=>{const o=(0,mn.val)(this.configPointer);return Sl(o)}))}getStaticValues(){return this._cache.get("getStaticValues",()=>(0,mn.prism)(()=>{var o;const l=(o=(0,mn.val)(this.pointerToStaticOverrides))!=null?o:{};return(0,mn.val)(this.configPointer).deserializeAndSanitize(l)||{}}))}getArrayOfValidSequenceTracks(){return this._cache.get("getArrayOfValidSequenceTracks",()=>(0,mn.prism)(()=>{const o=this.project.pointers.historic.sheetsById[this.address.sheetId],l=(0,mn.val)(o.sequence.tracksByObject[this.address.objectKey].trackIdByPropPath);if(!l)return ne;const d=[];if(!l)return ne;const y=(0,mn.val)(this.configPointer),M=Object.entries(l);for(const[B,K]of M){const Q=qS(B);if(!Q)continue;const oe=Ql(y,Q);oe&&BS(oe)&&d.push({pathToProp:Q,trackId:K})}const C=jS(y);return d.sort((B,K)=>{const Q=B.pathToProp,oe=K.pathToProp,xe=C.get(JSON.stringify(Q)),Ee=C.get(JSON.stringify(oe));return xe>Ee?1:-1}),d.length===0?ne:d}))}getMapOfValidSequenceTracks_forStudio(){return this._cache.get("getMapOfValidSequenceTracks_forStudio",()=>(0,mn.prism)(()=>{const o=(0,mn.val)(this.getArrayOfValidSequenceTracks());let l={};for(const{pathToProp:d,trackId:y}of o)ys(l,d,y);return l}))}getStaticButNotSequencedOverrides(){return this._cache.get("getStaticButNotSequencedOverrides",()=>(0,mn.prism)(()=>{const o=(0,mn.val)(this.getStaticValues()),l=(0,mn.val)(this.getArrayOfValidSequenceTracks()),d=Rx(o);for(const{pathToProp:y}of l){Gf(d,y);let M=y.slice(0,-1);for(;M.length>0;){const C=ma(d,M);if(!$f(C))break;Gf(d,M),M=M.slice(0,-1)}}if(!$f(d))return d}))}getDefaultsAtPointer(o){const{path:l}=(0,mn.getPointerParts)(o),d=this.getDefaultValues().getValue();return ma(d,l)}};function qS(o){try{return JSON.parse(o)}catch{Na.warn("property ".concat(JSON.stringify(o)," cannot be parsed. Skipping."));return}}var Zf=_n(),YS=US(o=>JSON.stringify(o));R(N());var KS=class extends Error{},Ro=class extends KS{},Qf=_n(),$S=_n(),ZS=_n(),En=_n();function lr(){let o,l;const d=new Promise((M,C)=>{o=B=>{M(B),y.status="resolved"},l=B=>{C(B),y.status="rejected"}}),y={resolve:o,reject:l,promise:d,status:"pending"};return y}var QS=()=>{},Oa=QS,JS=_n(),eE=class{constructor(){S(this,"_stopPlayCallback",Oa),S(this,"_state",new JS.Atom({position:0,playing:!1})),S(this,"statePointer"),this.statePointer=this._state.pointer}destroy(){}pause(){this._stopPlayCallback(),this.playing=!1,this._stopPlayCallback=Oa}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.setByPointer(l=>l.position,o)}getCurrentPosition(){return this._state.get().position}get playing(){return this._state.get().playing}set playing(o){this._state.setByPointer(l=>l.playing,o)}play(o,l,d,y,M){this.playing&&this.pause(),this.playing=!0;const C=l[1]-l[0];{const Ie=this.getCurrentPosition();Ie<l[0]||Ie>l[1]?y==="normal"||y==="alternate"?this._updatePositionInState(l[0]):(y==="reverse"||y==="alternateReverse")&&this._updatePositionInState(l[1]):y==="normal"||y==="alternate"?Ie===l[1]&&this._updatePositionInState(l[0]):Ie===l[0]&&this._updatePositionInState(l[1])}const B=lr(),K=M.time,Q=C*o;let oe=this.getCurrentPosition()-l[0];(y==="reverse"||y==="alternateReverse")&&(oe=l[1]-this.getCurrentPosition());const xe=Ie=>{const Xe=Math.max(Ie-K,0)/1e3,_t=Math.min(Xe*d+oe,Q);if(_t!==Q){const wt=Math.floor(_t/C);let gt=_t/C%1*C;if(y!=="normal")if(y==="reverse")gt=C-gt;else{const Ut=wt%2===0;y==="alternate"?Ut||(gt=C-gt):Ut&&(gt=C-gt)}this._updatePositionInState(gt+l[0]),Ee()}else{if(y==="normal")this._updatePositionInState(l[1]);else if(y==="reverse")this._updatePositionInState(l[0]);else{const wt=(o-1)%2===0;y==="alternate"?wt?this._updatePositionInState(l[1]):this._updatePositionInState(l[0]):wt?this._updatePositionInState(l[0]):this._updatePositionInState(l[1])}this.playing=!1,B.resolve(!0)}};this._stopPlayCallback=()=>{M.offThisOrNextTick(xe),M.offNextTick(xe),this.playing&&B.resolve(!1)};const Ee=()=>M.onNextTick(xe);return M.onThisOrNextTick(xe),B.promise}playDynamicRange(o,l){this.playing&&this.pause(),this.playing=!0;const d=lr(),y=o.keepHot();d.promise.then(y,y);let M=l.time;const C=K=>{const Q=Math.max(K-M,0);M=K;const oe=Q/1e3,xe=this.getCurrentPosition(),Ee=o.getValue();if(xe<Ee[0]||xe>Ee[1])this.gotoPosition(Ee[0]);else{let Ie=xe+oe;Ie>Ee[1]&&(Ie=Ee[0]+(Ie-Ee[1])),this.gotoPosition(Ie)}B()};this._stopPlayCallback=()=>{l.offThisOrNextTick(C),l.offNextTick(C),d.resolve(!1)};const B=()=>l.onNextTick(C);return l.onThisOrNextTick(C),d.promise}},tE=_n(),nE="__TheatreJS_StudioBundle",Jl="__TheatreJS_CoreBundle",iE="__TheatreJS_Notifications",Ua=o=>(...l)=>{var d;switch(o){case"success":{Na.debug(l.slice(0,2).join(`
`));break}case"info":{Na.debug(l.slice(0,2).join(`
`));break}case"warning":{Na.warn(l.slice(0,2).join(`
`));break}}return typeof window<"u"?(d=window[iE])==null?void 0:d.notify[o](...l):void 0},Es={warning:Ua("warning"),success:Ua("success"),info:Ua("info"),error:Ua("error")};typeof window<"u"&&(window.addEventListener("error",o=>{Es.error("An error occurred","<pre>".concat(o.message,`</pre>

See **console** for details.`))}),window.addEventListener("unhandledrejection",o=>{Es.error("An error occurred","<pre>".concat(o.reason,`</pre>

See **console** for details.`))}));var rE=class{constructor(o,l,d){this._decodedBuffer=o,this._audioContext=l,this._nodeDestination=d,S(this,"_mainGain"),S(this,"_state",new tE.Atom({position:0,playing:!1})),S(this,"statePointer"),S(this,"_stopPlayCallback",Oa),this.statePointer=this._state.pointer,this._mainGain=this._audioContext.createGain(),this._mainGain.connect(this._nodeDestination)}playDynamicRange(o,l){const d=lr();this._playing&&this.pause(),this._playing=!0;let y;const M=()=>{y==null||y(),y=this._loopInRange(o.getValue(),l).stop},C=o.onStale(M);return M(),this._stopPlayCallback=()=>{y==null||y(),C(),d.resolve(!1)},d.promise}_loopInRange(o,l){let y=this.getCurrentPosition();const M=o[1]-o[0];y<o[0]||y>o[1]?this._updatePositionInState(o[0]):y===o[1]&&this._updatePositionInState(o[0]),y=this.getCurrentPosition();const C=this._audioContext.createBufferSource();C.buffer=this._decodedBuffer,C.connect(this._mainGain),C.playbackRate.value=1,C.loop=!0,C.loopStart=o[0],C.loopEnd=o[1];const B=l.time;let K=y-o[0];C.start(0,y);const Q=Ee=>{let _t=(Math.max(Ee-B,0)/1e3*1+K)/M%1*M;this._updatePositionInState(_t+o[0]),oe()},oe=()=>l.onNextTick(Q);return l.onThisOrNextTick(Q),{stop:()=>{C.stop(),C.disconnect(),l.offThisOrNextTick(Q),l.offNextTick(Q)}}}get _playing(){return this._state.get().playing}set _playing(o){this._state.setByPointer(l=>l.playing,o)}destroy(){}pause(){this._stopPlayCallback(),this._playing=!1,this._stopPlayCallback=Oa}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.reduce(l=>x(g({},l),{position:o}))}getCurrentPosition(){return this._state.get().position}play(o,l,d,y,M){this._playing&&this.pause(),this._playing=!0;let C=this.getCurrentPosition();const B=l[1]-l[0];if(y!=="normal")throw new Ro('Audio-controlled sequences can only be played in the "normal" direction. '+"'".concat(y,"' given."));C<l[0]||C>l[1]?this._updatePositionInState(l[0]):C===l[1]&&this._updatePositionInState(l[0]),C=this.getCurrentPosition();const K=lr(),Q=this._audioContext.createBufferSource();Q.buffer=this._decodedBuffer,Q.connect(this._mainGain),Q.playbackRate.value=d,o>1e3&&(Es.warning("Can't play sequences with audio more than 1000 times","The sequence will still play, but only 1000 times. The `iterationCount: ".concat(o,"` provided to `sequence.play()`\nis too high for a sequence with audio.\n\nTo fix this, either set `iterationCount` to a lower value, or remove the audio from the sequence."),[{url:"https://www.theatrejs.com/docs/latest/manual/audio",title:"Using Audio"},{url:"https://www.theatrejs.com/docs/latest/api/core#sequence.attachaudio",title:"Audio API"}]),o=1e3),o>1&&(Q.loop=!0,Q.loopStart=l[0],Q.loopEnd=l[1]);const oe=M.time;let xe=C-l[0];const Ee=B*o;Q.start(0,C,Ee-xe);const Ie=_t=>{const gt=Math.max(_t-oe,0)/1e3,Ut=Math.min(gt*d+xe,Ee);if(Ut!==Ee){let Fn=Ut/B%1*B;this._updatePositionInState(Fn+l[0]),Xe()}else this._updatePositionInState(l[1]),this._playing=!1,tt(),K.resolve(!0)},tt=()=>{Q.stop(),Q.disconnect()};this._stopPlayCallback=()=>{tt(),M.offThisOrNextTick(Ie),M.offNextTick(Ie),this._playing&&K.resolve(!1)};const Xe=()=>M.onNextTick(Ie);return M.onThisOrNextTick(Ie),K.promise}},sE=_n(),Jf=0;function eu(o){var l;const d=B=>{y.tick(B)},y=new sE.Ticker({onActive(){var B;(B=o==null?void 0:o.start)==null||B.call(o)},onDormant(){var B;(B=o==null?void 0:o.stop)==null||B.call(o)}}),M={tick:d,id:Jf++,name:(l=o==null?void 0:o.name)!=null?l:"CustomRafDriver-".concat(Jf),type:"Theatre_RafDriver_PublicAPI"},C={type:"Theatre_RafDriver_PrivateAPI",publicApi:M,ticker:y,start:o==null?void 0:o.start,stop:o==null?void 0:o.stop};return de(M,C),M}function oE(){let o=null;const y=eu({name:"DefaultCoreRafDriver",start:()=>{if(typeof window<"u"){const M=C=>{y.tick(C),o=window.requestAnimationFrame(M)};o=window.requestAnimationFrame(M)}else y.tick(0),setTimeout(()=>y.tick(1),0)},stop:()=>{typeof window<"u"&&o!==null&&window.cancelAnimationFrame(o)}});return y}var Ba;function ep(){return Ba||aE(oE()),Ba}function tp(){return ep().ticker}function aE(o){if(Ba)throw new Error("`setCoreRafDriver()` is already called.");Ba=Y(o)}var cE=class{get type(){return"Theatre_Sequence_PublicAPI"}constructor(o){de(this,o)}play(o){const l=Y(this);if(l._project.isReady()){const d=o!=null&&o.rafDriver?Y(o.rafDriver).ticker:tp();return l.play(o??{},d)}else{const d=lr();return d.resolve(!0),d.promise}}pause(){Y(this).pause()}get position(){return Y(this).position}set position(o){Y(this).position=o}__experimental_getKeyframes(o){return Y(this).getKeyframesOfSimpleProp(o)}async attachAudio(o){const{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:M}=await lE(o),C=new rE(y,l,M);return Y(this).replacePlaybackController(C),{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:M}}get pointer(){return Y(this).pointer}};async function lE(o){function l(){if(o.audioContext)return Promise.resolve(o.audioContext);const oe=new AudioContext;return oe.state==="running"||typeof window>"u"?Promise.resolve(oe):new Promise(xe=>{const Ee=()=>{oe.resume().catch(Xe=>{console.error(Xe)})},Ie=["mousedown","keydown","touchstart"],tt={capture:!0,passive:!1};Ie.forEach(Xe=>{window.addEventListener(Xe,Ee,tt)}),oe.addEventListener("statechange",()=>{oe.state==="running"&&(Ie.forEach(Xe=>{window.removeEventListener(Xe,Ee,tt)}),xe(oe))})})}async function d(){if(o.source instanceof AudioBuffer)return o.source;const oe=lr();if(typeof o.source!="string")throw new Error("Error validating arguments to sequence.attachAudio(). args.source must either be a string or an instance of AudioBuffer.");let xe;try{xe=await fetch(o.source)}catch(Xe){throw console.error(Xe),new Error("Could not fetch '".concat(o.source,"'. Network error logged above."))}let Ee;try{Ee=await xe.arrayBuffer()}catch(Xe){throw console.error(Xe),new Error("Could not read '".concat(o.source,"' as an arrayBuffer."))}(await y).decodeAudioData(Ee,oe.resolve,oe.reject);let tt;try{tt=await oe.promise}catch(Xe){throw console.error(Xe),new Error("Could not decode ".concat(o.source," as an audio file."))}return tt}const y=l(),M=d(),[C,B]=await Promise.all([y,M]),K=o.destinationNode||C.destination,Q=C.createGain();return Q.connect(K),{audioContext:C,decodedBuffer:B,gainNode:Q,destinationNode:K}}var uE=hE("Theatre_SheetObject");function hE(o){return l=>typeof l=="object"&&!!l&&l.type===o}var dE=class{constructor(o,l,d,y,M){this._project=o,this._sheet=l,this._lengthD=d,this._subUnitsPerUnitD=y,S(this,"address"),S(this,"publicApi"),S(this,"_playbackControllerBox"),S(this,"_prismOfStatePointer"),S(this,"_positionD"),S(this,"_positionFormatterD"),S(this,"_playableRangeD"),S(this,"pointer",(0,ZS.pointer)({root:this,path:[]})),S(this,"$$isPointerToPrismProvider",!0),S(this,"_logger"),S(this,"closestGridPosition",C=>{const K=1/this.subUnitsPerUnit;return parseFloat((Math.round(C/K)*K).toFixed(3))}),this._logger=o._logger.named("Sheet",l.address.sheetId).named("Instance",l.address.sheetInstanceId),this.address=x(g({},this._sheet.address),{sequenceName:"default"}),this.publicApi=new cE(this),this._playbackControllerBox=new $S.Atom(M??new eE),this._prismOfStatePointer=(0,En.prism)(()=>this._playbackControllerBox.prism.getValue().statePointer),this._positionD=(0,En.prism)(()=>{const C=this._prismOfStatePointer.getValue();return(0,En.val)(C.position)}),this._positionFormatterD=(0,En.prism)(()=>{const C=(0,En.val)(this._subUnitsPerUnitD);return new fE(C)})}get type(){return"Theatre_Sequence"}pointerToPrism(o){const{path:l}=(0,Qf.getPointerParts)(o);if(l.length===0)return(0,En.prism)(()=>({length:(0,En.val)(this.pointer.length),playing:(0,En.val)(this.pointer.playing),position:(0,En.val)(this.pointer.position),subUnitsPerUnit:(0,En.val)(this.pointer.subUnitsPerUnit)}));if(l.length>1)return(0,En.prism)(()=>{});const[d]=l;return d==="length"?this._lengthD:d==="subUnitsPerUnit"?this._subUnitsPerUnitD:d==="position"?this._positionD:d==="playing"?(0,En.prism)(()=>(0,En.val)(this._prismOfStatePointer.getValue().playing)):(0,En.prism)(()=>{})}getKeyframesOfSimpleProp(o){const{path:l,root:d}=(0,Qf.getPointerParts)(o);if(!uE(d))throw new Ro("Argument prop must be a pointer to a SheetObject property");const y=(0,En.val)(this._project.pointers.historic.sheetsById[this._sheet.address.sheetId].sequence.tracksByObject[d.address.objectKey]);if(!y)return[];const{trackData:M,trackIdByPropPath:C}=y,B=YS(l),K=C[B];if(!K)return[];const Q=M[K];return Q?Q.keyframes:[]}get positionFormatter(){return this._positionFormatterD.getValue()}get prismOfStatePointer(){return this._prismOfStatePointer}get length(){return this._lengthD.getValue()}get positionPrism(){return this._positionD}get position(){return this._playbackControllerBox.get().getCurrentPosition()}get subUnitsPerUnit(){return this._subUnitsPerUnitD.getValue()}get positionSnappedToGrid(){return this.closestGridPosition(this.position)}set position(o){let l=o;this.pause(),l>this.length&&(l=this.length);const d=this.length;this._playbackControllerBox.get().gotoPosition(l>d?d:l)}getDurationCold(){return this._lengthD.getValue()}get playing(){return(0,En.val)(this._playbackControllerBox.get().statePointer.playing)}_makeRangeFromSequenceTemplate(){return(0,En.prism)(()=>[0,(0,En.val)(this._lengthD)])}playDynamicRange(o,l){return this._playbackControllerBox.get().playDynamicRange(o,l)}async play(o,l){const d=this.length,y=o&&o.range?o.range:[0,d],M=o&&typeof o.iterationCount=="number"?o.iterationCount:1,C=o&&typeof o.rate<"u"?o.rate:1,B=o&&o.direction?o.direction:"normal";return await this._play(M,[y[0],y[1]],C,B,l)}_play(o,l,d,y,M){return this._playbackControllerBox.get().play(o,l,d,y,M)}pause(){this._playbackControllerBox.get().pause()}replacePlaybackController(o){this.pause();const l=this._playbackControllerBox.get();this._playbackControllerBox.set(o);const d=l.getCurrentPosition();l.destroy(),o.gotoPosition(d)}},fE=class{constructor(o){this._fps=o}formatSubUnitForGrid(o){const l=o%1,d=1/this._fps;return Math.round(l/d)+"f"}formatFullUnitForGrid(o){let l=o,d="";if(l>=Ms){const M=Math.floor(l/Ms);d+=M+"h",l=l%Ms}if(l>=Hr){const M=Math.floor(l/Hr);d+=M+"m",l=l%Hr}if(l>=zr){const M=Math.floor(l/zr);d+=M+"s",l=l%zr}const y=1/this._fps;if(l>=y){const M=Math.floor(l/y);d+=M+"f",l=l%y}return d.length===0?"0s":d}formatForPlayhead(o){let l=o,d="";if(l>=Ms){const M=Math.floor(l/Ms);d+=Ao(M.toString(),2,"0")+"h",l=l%Ms}if(l>=Hr){const M=Math.floor(l/Hr);d+=Ao(M.toString(),2,"0")+"m",l=l%Hr}else d.length>0&&(d+="00m");if(l>=zr){const M=Math.floor(l/zr);d+=Ao(M.toString(),2,"0")+"s",l=l%zr}else d+="00s";const y=1/this._fps;if(l>=y){const M=Math.round(l/y);d+=Ao(M.toString(),2,"0")+"f",l=l%y}else l/y>.98?(d+=Ao("1",2,"0")+"f",l=l%y):d+="00f";return d.length===0?"00s00f":d}formatBasic(o){return o.toFixed(2)+"s"}},zr=1,Hr=zr*60,Ms=Hr*60,tu={};v(tu,{boolean:()=>cp,compound:()=>iu,file:()=>bE,image:()=>EE,number:()=>ap,rgba:()=>RE,string:()=>lp,stringLiteral:()=>LE});function np(o,l){return o.length<=l?o:o.substr(0,l-3)+"..."}var pE=o=>typeof o=="string"?'string("'.concat(np(o,10),'")'):typeof o=="number"?"number(".concat(np(String(o),10),")"):o===null?"null":o===void 0?"undefined":typeof o=="boolean"?String(o):Array.isArray(o)?"array":typeof o=="object"?"object":"unknown",ip=pE;function mE(o,{removeAlphaIfOpaque:l=!1}={}){const d=(o.a*255|256).toString(16).slice(1),y=(o.r*255|256).toString(16).slice(1)+(o.g*255|256).toString(16).slice(1)+(o.b*255|256).toString(16).slice(1)+(l&&d==="ff"?"":d);return"#".concat(y)}function nu(o){return x(g({},o),{toString(){return mE(this,{removeAlphaIfOpaque:!0})}})}function gE(o){return Object.fromEntries(Object.entries(o).map(([l,d])=>[l,nf(d,0,1)]))}function _E(o){function l(d){return d>=.0031308?1.055*d**(1/2.4)-.055:12.92*d}return gE({r:l(o.r),g:l(o.g),b:l(o.b),a:o.a})}function rp(o){function l(d){return d>=.04045?((d+.055)/(1+.055))**2.4:d/12.92}return{r:l(o.r),g:l(o.g),b:l(o.b),a:o.a}}function sp(o){let l=.4122214708*o.r+.5363325363*o.g+.0514459929*o.b,d=.2119034982*o.r+.6806995451*o.g+.1073969566*o.b,y=.0883024619*o.r+.2817188376*o.g+.6299787005*o.b,M=Math.cbrt(l),C=Math.cbrt(d),B=Math.cbrt(y);return{L:.2104542553*M+.793617785*C-.0040720468*B,a:1.9779984951*M-2.428592205*C+.4505937099*B,b:.0259040371*M+.7827717662*C-.808675766*B,alpha:o.a}}function vE(o){let l=o.L+.3963377774*o.a+.2158037573*o.b,d=o.L-.1055613458*o.a-.0638541728*o.b,y=o.L-.0894841775*o.a-1.291485548*o.b,M=l*l*l,C=d*d*d,B=y*y*y;return{r:4.0767416621*M-3.3077115913*C+.2309699292*B,g:-1.2684380046*M+2.6097574011*C-.3413193965*B,b:-.0041960863*M-.7034186147*C+1.707614701*B,a:o.alpha}}var Hi=Symbol("TheatrePropType_Basic");function op(o){return typeof o=="object"&&!!o&&o[Hi]==="TheatrePropType"}function yE(o){if(typeof o=="number")return ap(o);if(typeof o=="boolean")return cp(o);if(typeof o=="string")return lp(o);if(typeof o=="object"&&o){if(op(o))return o;if(Nv(o))return iu(o);throw new Ro("This value is not a valid prop type: ".concat(ip(o)))}else throw new Ro("This value is not a valid prop type: ".concat(ip(o)))}function xE(o){const l={};for(const d of Object.keys(o)){const y=o[d];op(y)?l[d]=y:l[d]=yE(y)}return l}var iu=(o,l={})=>{const d=xE(o),y=new WeakMap;return{type:"compound",props:d,valueType:null,[Hi]:"TheatrePropType",label:l.label,default:cS(d,C=>C.default),deserializeAndSanitize:C=>{if(typeof C!="object"||!C)return;if(y.has(C))return y.get(C);const B={};let K=!1;for(const[Q,oe]of Object.entries(d))if(Object.prototype.hasOwnProperty.call(C,Q)){const xe=oe.deserializeAndSanitize(C[Q]);xe!=null&&(K=!0,B[Q]=xe)}if(y.set(C,B),K)return B}}},bE=(o,l={})=>{const d=(y,M,C)=>{var B;return{type:"file",id:((B=l.interpolate)!=null?B:Po)(y.id,M.id,C)}};return{type:"file",default:{type:"file",id:o},valueType:null,[Hi]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:SE}},SE=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="file"&&(l=!1),!!l)return o},EE=(o,l={})=>{const d=(y,M,C)=>{var B;return{type:"image",id:((B=l.interpolate)!=null?B:Po)(y.id,M.id,C)}};return{type:"image",default:{type:"image",id:o},valueType:null,[Hi]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:ME}},ME=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="image"&&(l=!1),!!l)return o},ap=(o,l={})=>{var d;return x(g({type:"number",valueType:0,default:o,[Hi]:"TheatrePropType"},l||{}),{label:l.label,nudgeFn:(d=l.nudgeFn)!=null?d:FE,nudgeMultiplier:typeof l.nudgeMultiplier=="number"?l.nudgeMultiplier:void 0,interpolate:AE,deserializeAndSanitize:TE(l.range)})},TE=o=>o?l=>{if(typeof l=="number"&&isFinite(l))return nf(l,o[0],o[1])}:wE,wE=o=>typeof o=="number"&&isFinite(o)?o:void 0,AE=(o,l,d)=>o+d*(l-o),RE=(o={r:0,g:0,b:0,a:1},l={})=>{const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return{type:"rgba",valueType:null,default:nu(d),[Hi]:"TheatrePropType",label:l.label,interpolate:CE,deserializeAndSanitize:PE}},PE=o=>{if(!o)return;let l=!0;for(const y of["r","g","b","a"])(!Object.prototype.hasOwnProperty.call(o,y)||typeof o[y]!="number")&&(l=!1);if(!l)return;const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return nu(d)},CE=(o,l,d)=>{const y=sp(rp(o)),M=sp(rp(l)),C={L:(1-d)*y.L+d*M.L,a:(1-d)*y.a+d*M.a,b:(1-d)*y.b+d*M.b,alpha:(1-d)*y.alpha+d*M.alpha},B=_E(vE(C));return nu(B)},cp=(o,l={})=>{var d;return{type:"boolean",default:o,valueType:null,[Hi]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:DE}},DE=o=>typeof o=="boolean"?o:void 0;function Po(o){return o}var lp=(o,l={})=>{var d;return{type:"string",default:o,valueType:null,[Hi]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:IE}};function IE(o){return typeof o=="string"?o:void 0}function LE(o,l,d={}){var y,M;return{type:"stringLiteral",default:o,valuesAndLabels:g({},l),[Hi]:"TheatrePropType",valueType:null,as:(y=d.as)!=null?y:"menu",label:d.label,interpolate:(M=d.interpolate)!=null?M:Po,deserializeAndSanitize(C){if(typeof C=="string"&&Object.prototype.hasOwnProperty.call(l,C))return C}}}var FE=({config:o,deltaX:l,deltaFraction:d,magnitude:y})=>{var M;const{range:C}=o;return!o.nudgeMultiplier&&C&&!C.includes(1/0)&&!C.includes(-1/0)?d*(C[1]-C[0])*y:l*y*((M=o.nudgeMultiplier)!=null?M:1)},NE=o=>o.replace(/^[\s\/]*/,"").replace(/[\s\/]*$/,"").replace(/\s*\/\s*/g," / ");function ka(o,l){return NE(o)}R(V());var OE=class{get type(){return"Theatre_Sheet_PublicAPI"}constructor(o){de(this,o)}object(o,l,d){const y=Y(this),M=ka(o),C=y.getObject(M),B=null,K=d==null?void 0:d.__actions__THIS_API_IS_UNSTABLE_AND_WILL_CHANGE_IN_THE_NEXT_VERSION;if(C)return K&&C.template._temp_setActions(K),C.publicApi;{const Q=iu(l);return y.createObject(M,B,Q,K).publicApi}}__experimental_getExistingObject(o){const l=Y(this),d=ka(o),y=l.getObject(d);return y==null?void 0:y.publicApi}get sequence(){return Y(this).getSequence().publicApi}get project(){return Y(this).project.publicApi}get address(){return g({},Y(this).address)}detachObject(o){const l=Y(this),d=ka(o);if(!l.getObject(d)){Es.warning(`Couldn't delete object "`.concat(d,'"'),'There is no object with key "'.concat(d,`".

To fix this, make sure you are calling \`sheet.deleteObject("`).concat(d,'")` with the correct key.')),console.warn('Object key "'.concat(d,'" does not exist.'));return}l.deleteObject(d)}},Co=_n(),UE=class{constructor(o,l){this.template=o,this.instanceId=l,S(this,"_objects",new Co.Atom({})),S(this,"_sequence"),S(this,"address"),S(this,"publicApi"),S(this,"project"),S(this,"objectsP",this._objects.pointer),S(this,"type","Theatre_Sheet"),S(this,"_logger"),this._logger=o.project._logger.named("Sheet",l),this._logger._trace("creating sheet"),this.project=o.project,this.address=x(g({},o.address),{sheetInstanceId:this.instanceId}),this.publicApi=new OE(this)}createObject(o,l,d,y={}){const C=this.template.getObjectTemplate(o,l,d,y).createInstance(this,l,d);return this._objects.setByPointer(B=>B[o],C),C}getObject(o){return this._objects.get()[o]}deleteObject(o){this._objects.reduce(l=>{const d=g({},l);return delete d[o],d})}getSequence(){if(!this._sequence){const o=(0,Co.prism)(()=>{const d=(0,Co.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.length);return BE(d)}),l=(0,Co.prism)(()=>{const d=(0,Co.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.subUnitsPerUnit);return kE(d)});this._sequence=new dE(this.template.project,this,o,l)}return this._sequence}},BE=o=>typeof o=="number"&&isFinite(o)&&o>0?o:10,kE=o=>typeof o=="number"&&oS(o)&&o>=1&&o<=1e3?o:30,zE=class{constructor(o,l){this.project=o,S(this,"type","Theatre_SheetTemplate"),S(this,"address"),S(this,"_instances",new Zf.Atom({})),S(this,"instancesP",this._instances.pointer),S(this,"_objectTemplates",new Zf.Atom({})),S(this,"objectTemplatesP",this._objectTemplates.pointer),this.address=x(g({},o.address),{sheetId:l})}getInstance(o){let l=this._instances.get()[o];return l||(l=new UE(this,o),this._instances.setByPointer(d=>d[o],l)),l}getObjectTemplate(o,l,d,y){let M=this._objectTemplates.get()[o];return M||(M=new XS(this,o,l,d,y),this._objectTemplates.setByPointer(C=>C[o],M)),M}},ru=_n(),up=_n(),HE=o=>new Promise(l=>setTimeout(l,o)),VE=HE;function ui(o){for(var l=arguments.length,d=Array(l>1?l-1:0),y=1;y<l;y++)d[y-1]=arguments[y];throw Error("[Immer] minified error nr: "+o+(d.length?" "+d.map(function(M){return"'"+M+"'"}).join(","):"")+". Find the full error at: https://bit.ly/3cXEKWf")}function Vr(o){return!!o&&!!o[qn]}function Gr(o){return!!o&&((function(l){if(!l||typeof l!="object")return!1;var d=Object.getPrototypeOf(l);if(d===null)return!0;var y=Object.hasOwnProperty.call(d,"constructor")&&d.constructor;return y===Object||typeof y=="function"&&Function.toString.call(y)===ZE})(o)||Array.isArray(o)||!!o[xp]||!!o.constructor[xp]||ou(o)||au(o))}function GE(o){return Vr(o)||ui(23,o),o[qn].t}function Do(o,l,d){d===void 0&&(d=!1),Ts(o)===0?(d?Object.keys:yu)(o).forEach(function(y){d&&typeof y=="symbol"||l(y,o[y],o)}):o.forEach(function(y,M){return l(M,y,o)})}function Ts(o){var l=o[qn];return l?l.i>3?l.i-4:l.i:Array.isArray(o)?1:ou(o)?2:au(o)?3:0}function su(o,l){return Ts(o)===2?o.has(l):Object.prototype.hasOwnProperty.call(o,l)}function WE(o,l){return Ts(o)===2?o.get(l):o[l]}function hp(o,l,d){var y=Ts(o);y===2?o.set(l,d):y===3?(o.delete(l),o.add(d)):o[l]=d}function jE(o,l){return o===l?o!==0||1/o==1/l:o!=o&&l!=l}function ou(o){return KE&&o instanceof Map}function au(o){return $E&&o instanceof Set}function Wr(o){return o.o||o.t}function cu(o){if(Array.isArray(o))return Array.prototype.slice.call(o);var l=QE(o);delete l[qn];for(var d=yu(l),y=0;y<d.length;y++){var M=d[y],C=l[M];C.writable===!1&&(C.writable=!0,C.configurable=!0),(C.get||C.set)&&(l[M]={configurable:!0,writable:!0,enumerable:C.enumerable,value:o[M]})}return Object.create(Object.getPrototypeOf(o),l)}function lu(o,l){return l===void 0&&(l=!1),uu(o)||Vr(o)||!Gr(o)||(Ts(o)>1&&(o.set=o.add=o.clear=o.delete=XE),Object.freeze(o),l&&Do(o,function(d,y){return lu(y,!0)},!0)),o}function XE(){ui(2)}function uu(o){return o==null||typeof o!="object"||Object.isFrozen(o)}function Vi(o){var l=JE[o];return l||ui(18,o),l}function dp(){return Io}function hu(o,l){l&&(Vi("Patches"),o.u=[],o.s=[],o.v=l)}function za(o){du(o),o.p.forEach(qE),o.p=null}function du(o){o===Io&&(Io=o.l)}function fp(o){return Io={p:[],l:Io,h:o,m:!0,_:0}}function qE(o){var l=o[qn];l.i===0||l.i===1?l.j():l.O=!0}function fu(o,l){l._=l.p.length;var d=l.p[0],y=o!==void 0&&o!==d;return l.h.g||Vi("ES5").S(l,o,y),y?(d[qn].P&&(za(l),ui(4)),Gr(o)&&(o=Ha(l,o),l.l||Va(l,o)),l.u&&Vi("Patches").M(d[qn],o,l.u,l.s)):o=Ha(l,d,[]),za(l),l.u&&l.v(l.u,l.s),o!==yp?o:void 0}function Ha(o,l,d){if(uu(l))return l;var y=l[qn];if(!y)return Do(l,function(C,B){return pp(o,y,l,C,B,d)},!0),l;if(y.A!==o)return l;if(!y.P)return Va(o,y.t,!0),y.t;if(!y.I){y.I=!0,y.A._--;var M=y.i===4||y.i===5?y.o=cu(y.k):y.o;Do(y.i===3?new Set(M):M,function(C,B){return pp(o,y,M,C,B,d)}),Va(o,M,!1),d&&o.u&&Vi("Patches").R(y,d,o.u,o.s)}return y.o}function pp(o,l,d,y,M,C){if(Vr(M)){var B=Ha(o,M,C&&l&&l.i!==3&&!su(l.D,y)?C.concat(y):void 0);if(hp(d,y,B),!Vr(B))return;o.m=!1}if(Gr(M)&&!uu(M)){if(!o.h.F&&o._<1)return;Ha(o,M),l&&l.A.l||Va(o,M)}}function Va(o,l,d){d===void 0&&(d=!1),o.h.F&&o.m&&lu(l,d)}function pu(o,l){var d=o[qn];return(d?Wr(d):o)[l]}function mp(o,l){if(l in o)for(var d=Object.getPrototypeOf(o);d;){var y=Object.getOwnPropertyDescriptor(d,l);if(y)return y;d=Object.getPrototypeOf(d)}}function mu(o){o.P||(o.P=!0,o.l&&mu(o.l))}function gu(o){o.o||(o.o=cu(o.t))}function _u(o,l,d){var y=ou(l)?Vi("MapSet").N(l,d):au(l)?Vi("MapSet").T(l,d):o.g?(function(M,C){var B=Array.isArray(M),K={i:B?1:0,A:C?C.A:dp(),P:!1,I:!1,D:{},l:C,t:M,k:null,o:null,j:null,C:!1},Q=K,oe=Ga;B&&(Q=[K],oe=Wa);var xe=Proxy.revocable(Q,oe),Ee=xe.revoke,Ie=xe.proxy;return K.k=Ie,K.j=Ee,Ie})(l,d):Vi("ES5").J(l,d);return(d?d.A:dp()).p.push(y),y}function YE(o){return Vr(o)||ui(22,o),(function l(d){if(!Gr(d))return d;var y,M=d[qn],C=Ts(d);if(M){if(!M.P&&(M.i<4||!Vi("ES5").K(M)))return M.t;M.I=!0,y=gp(d,C),M.I=!1}else y=gp(d,C);return Do(y,function(B,K){M&&WE(M.t,B)===K||hp(y,B,l(K))}),C===3?new Set(y):y})(o)}function gp(o,l){switch(l){case 2:return new Map(o);case 3:return Array.from(o)}return cu(o)}var _p,Io,vu=typeof Symbol<"u"&&typeof Symbol("x")=="symbol",KE=typeof Map<"u",$E=typeof Set<"u",vp=typeof Proxy<"u"&&Proxy.revocable!==void 0&&typeof Reflect<"u",yp=vu?Symbol.for("immer-nothing"):((_p={})["immer-nothing"]=!0,_p),xp=vu?Symbol.for("immer-draftable"):"__$immer_draftable",qn=vu?Symbol.for("immer-state"):"__$immer_state",ZE=""+Object.prototype.constructor,yu=typeof Reflect<"u"&&Reflect.ownKeys?Reflect.ownKeys:Object.getOwnPropertySymbols!==void 0?function(o){return Object.getOwnPropertyNames(o).concat(Object.getOwnPropertySymbols(o))}:Object.getOwnPropertyNames,QE=Object.getOwnPropertyDescriptors||function(o){var l={};return yu(o).forEach(function(d){l[d]=Object.getOwnPropertyDescriptor(o,d)}),l},JE={},Ga={get:function(o,l){if(l===qn)return o;var d=Wr(o);if(!su(d,l))return(function(M,C,B){var K,Q=mp(C,B);return Q?"value"in Q?Q.value:(K=Q.get)===null||K===void 0?void 0:K.call(M.k):void 0})(o,d,l);var y=d[l];return o.I||!Gr(y)?y:y===pu(o.t,l)?(gu(o),o.o[l]=_u(o.A.h,y,o)):y},has:function(o,l){return l in Wr(o)},ownKeys:function(o){return Reflect.ownKeys(Wr(o))},set:function(o,l,d){var y=mp(Wr(o),l);if(y!=null&&y.set)return y.set.call(o.k,d),!0;if(!o.P){var M=pu(Wr(o),l),C=M==null?void 0:M[qn];if(C&&C.t===d)return o.o[l]=d,o.D[l]=!1,!0;if(jE(d,M)&&(d!==void 0||su(o.t,l)))return!0;gu(o),mu(o)}return o.o[l]===d&&typeof d!="number"&&(d!==void 0||l in o.o)||(o.o[l]=d,o.D[l]=!0,!0)},deleteProperty:function(o,l){return pu(o.t,l)!==void 0||l in o.t?(o.D[l]=!1,gu(o),mu(o)):delete o.D[l],o.o&&delete o.o[l],!0},getOwnPropertyDescriptor:function(o,l){var d=Wr(o),y=Reflect.getOwnPropertyDescriptor(d,l);return y&&{writable:!0,configurable:o.i!==1||l!=="length",enumerable:y.enumerable,value:d[l]}},defineProperty:function(){ui(11)},getPrototypeOf:function(o){return Object.getPrototypeOf(o.t)},setPrototypeOf:function(){ui(12)}},Wa={};Do(Ga,function(o,l){Wa[o]=function(){return arguments[0]=arguments[0][0],l.apply(this,arguments)}}),Wa.deleteProperty=function(o,l){return Ga.deleteProperty.call(this,o[0],l)},Wa.set=function(o,l,d){return Ga.set.call(this,o[0],l,d,o[0])};var eM=(function(){function o(d){var y=this;this.g=vp,this.F=!0,this.produce=function(M,C,B){if(typeof M=="function"&&typeof C!="function"){var K=C;C=M;var Q=y;return function(tt){var Xe=this;tt===void 0&&(tt=K);for(var _t=arguments.length,wt=Array(_t>1?_t-1:0),gt=1;gt<_t;gt++)wt[gt-1]=arguments[gt];return Q.produce(tt,function(Ut){var Fn;return(Fn=C).call.apply(Fn,[Xe,Ut].concat(wt))})}}var oe;if(typeof C!="function"&&ui(6),B!==void 0&&typeof B!="function"&&ui(7),Gr(M)){var xe=fp(y),Ee=_u(y,M,void 0),Ie=!0;try{oe=C(Ee),Ie=!1}finally{Ie?za(xe):du(xe)}return typeof Promise<"u"&&oe instanceof Promise?oe.then(function(tt){return hu(xe,B),fu(tt,xe)},function(tt){throw za(xe),tt}):(hu(xe,B),fu(oe,xe))}if(!M||typeof M!="object")return(oe=C(M))===yp?void 0:(oe===void 0&&(oe=M),y.F&&lu(oe,!0),oe);ui(21,M)},this.produceWithPatches=function(M,C){return typeof M=="function"?function(Q){for(var oe=arguments.length,xe=Array(oe>1?oe-1:0),Ee=1;Ee<oe;Ee++)xe[Ee-1]=arguments[Ee];return y.produceWithPatches(Q,function(Ie){return M.apply(void 0,[Ie].concat(xe))})}:[y.produce(M,C,function(Q,oe){B=Q,K=oe}),B,K];var B,K},typeof(d==null?void 0:d.useProxies)=="boolean"&&this.setUseProxies(d.useProxies),typeof(d==null?void 0:d.autoFreeze)=="boolean"&&this.setAutoFreeze(d.autoFreeze)}var l=o.prototype;return l.createDraft=function(d){Gr(d)||ui(8),Vr(d)&&(d=YE(d));var y=fp(this),M=_u(this,d,void 0);return M[qn].C=!0,du(y),M},l.finishDraft=function(d,y){var M=d&&d[qn],C=M.A;return hu(C,y),fu(void 0,C)},l.setAutoFreeze=function(d){this.F=d},l.setUseProxies=function(d){d&&!vp&&ui(20),this.g=d},l.applyPatches=function(d,y){var M;for(M=y.length-1;M>=0;M--){var C=y[M];if(C.path.length===0&&C.op==="replace"){d=C.value;break}}var B=Vi("Patches").$;return Vr(d)?B(d,y):this.produce(d,function(K){return B(K,y.slice(M+1))})},o})(),ni=new eM;ni.produce,ni.produceWithPatches.bind(ni),ni.setAutoFreeze.bind(ni),ni.setUseProxies.bind(ni),ni.applyPatches.bind(ni),ni.createDraft.bind(ni),ni.finishDraft.bind(ni);var tM={currentProjectStateDefinitionVersion:"0.4.0"},xu=tM;async function nM(o,l,d){await VE(0),o.transaction(({drafts:y})=>{var M;const C=l.address.projectId;y.ephemeral.coreByProject[C]={lastExportedObject:null,loadingState:{type:"loading"}},y.ahistoric.coreByProject[C]={ahistoricStuff:""};function B(){y.ephemeral.coreByProject[C].loadingState={type:"loaded"},y.historic.coreByProject[C]={sheetsById:{},definitionVersion:xu.currentProjectStateDefinitionVersion,revisionHistory:[]}}function K(Ee){y.ephemeral.coreByProject[C].loadingState={type:"loaded"},y.historic.coreByProject[C]=Ee}function Q(){y.ephemeral.coreByProject[C].loadingState={type:"loaded"}}function oe(Ee){y.ephemeral.coreByProject[C].loadingState={type:"browserStateIsNotBasedOnDiskState",onDiskState:Ee}}const xe=(M=GE(y.historic))==null?void 0:M.coreByProject[l.address.projectId];xe?d&&xe.revisionHistory.indexOf(d.revisionHistory[0])==-1?oe(d):Q():d?K(d):B()})}function bp(){}function Sp(o){var l,d;const y=(l=o==null?void 0:o.logging)!=null&&l.internal?(d=o.logging.min)!=null?d:256:1/0,M=y<=128,C=y<=512,B=Wf(void 0,{_debug:M?console.debug.bind(console,"_coreLogger(TheatreInternalLogger) debug"):bp,_error:C?console.error.bind(console,"_coreLogger(TheatreInternalLogger) error"):bp});if(o){const{logger:K,logging:Q}=o;K&&B.configureLogger(K),Q?B.configureLogging(Q):B.configureLogging({dev:!1})}return B.getLogger().named("Theatre")}var iM=class{constructor(o,l={},d){this.config=l,this.publicApi=d,S(this,"pointers"),S(this,"_pointerProxies"),S(this,"address"),S(this,"_studioReadyDeferred"),S(this,"_assetStorageReadyDeferred"),S(this,"_readyPromise"),S(this,"_sheetTemplates",new up.Atom({})),S(this,"sheetTemplatesP",this._sheetTemplates.pointer),S(this,"_studio"),S(this,"assetStorage"),S(this,"type","Theatre_Project"),S(this,"_logger");var y;this._logger=Sp({logging:{dev:!0}}).named("Project",o),this._logger.traceDev("creating project"),this.address={projectId:o};const M=new up.Atom({ahistoric:{ahistoricStuff:""},historic:(y=l.state)!=null?y:{sheetsById:{},definitionVersion:xu.currentProjectStateDefinitionVersion,revisionHistory:[]},ephemeral:{loadingState:{type:"loaded"},lastExportedObject:null}});this._assetStorageReadyDeferred=lr(),this.assetStorage={getAssetUrl:C=>{var B;return"".concat((B=l.assets)==null?void 0:B.baseUrl,"/").concat(C)},createAsset:()=>{throw new Error("Please wait for Project.ready to use assets.")}},this._pointerProxies={historic:new ru.PointerProxy(M.pointer.historic),ahistoric:new ru.PointerProxy(M.pointer.ahistoric),ephemeral:new ru.PointerProxy(M.pointer.ephemeral)},this.pointers={historic:this._pointerProxies.historic.pointer,ahistoric:this._pointerProxies.ahistoric.pointer,ephemeral:this._pointerProxies.ephemeral.pointer},re.add(o,this),this._studioReadyDeferred=lr(),this._readyPromise=Promise.all([this._studioReadyDeferred.promise,this._assetStorageReadyDeferred.promise]).then(()=>{}),l.state?setTimeout(()=>{this._studio||(this._studioReadyDeferred.resolve(void 0),this._assetStorageReadyDeferred.resolve(void 0),this._logger._trace("ready deferred resolved with no state"))},0):typeof window>"u"?console.error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. ')+"You can safely ignore this message if you're developing a Next.js/Remix project in development mode. But if you are shipping to your end-users, then you need to set config.state, otherwise your project's state will be empty and nothing will animate. Learn more at https://www.theatrejs.com/docs/latest/manual/projects#state"):setTimeout(()=>{if(!this._studio)throw new Error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. This is fine ')+"while you are using @theatre/core along with @theatre/studio. But since @theatre/studio "+'is not loaded, the state of project "'.concat(o,`" will be empty.

`)+`To fix this, you need to add @theatre/studio into the bundle and export the project's state. Learn how to do that at https://www.theatrejs.com/docs/latest/manual/projects#state
`)},1e3)}attachToStudio(o){if(this._studio){if(this._studio!==o)throw new Error("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));console.warn("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));return}this._studio=o,o.initialized.then(async()=>{var l;await nM(o,this,this.config.state),this._pointerProxies.historic.setPointer(o.atomP.historic.coreByProject[this.address.projectId]),this._pointerProxies.ahistoric.setPointer(o.atomP.ahistoric.coreByProject[this.address.projectId]),this._pointerProxies.ephemeral.setPointer(o.atomP.ephemeral.coreByProject[this.address.projectId]),await o.createAssetStorage(this,(l=this.config.assets)==null?void 0:l.baseUrl).then(d=>{this.assetStorage=d,this._assetStorageReadyDeferred.resolve(void 0)}),this._studioReadyDeferred.resolve(void 0)}).catch(l=>{throw console.error(l),l})}get isAttachedToStudio(){return!!this._studio}get ready(){return this._readyPromise}isReady(){return this._studioReadyDeferred.status==="resolved"&&this._assetStorageReadyDeferred.status==="resolved"}getOrCreateSheet(o,l="default"){let d=this._sheetTemplates.get()[o];return d||(d=new zE(this,o),this._sheetTemplates.reduce(y=>x(g({},y),{[o]:d}))),d.getInstance(l)}},rM=class{get type(){return"Theatre_Project_PublicAPI"}constructor(o,l={}){de(this,new iM(o,l,this))}get ready(){return Y(this).ready}get isReady(){return Y(this).isReady()}get address(){return g({},Y(this).address)}getAssetUrl(o){if(!this.isReady){console.error("Calling `project.getAssetUrl()` before `project.ready` is resolved, will always return `undefined`. Either use `project.ready.then(() => project.getAssetUrl())` or `await project.ready` before calling `project.getAssetUrl()`.");return}return o.id?Y(this).assetStorage.getAssetUrl(o.id):void 0}sheet(o,l="default"){const d=ka(o);return Y(this).getOrCreateSheet(d,l).publicApi}};R(V());var Ep=_n(),bu=_n();function Mp(o,l={}){const d=re.get(o);if(d)return d.publicApi;const M=Sp().named("Project",o);return l.state?(oM(o,l.state),M._debug("deep validated config.state on disk")):M._debug("no config.state"),new rM(o,l)}var sM=(o,l)=>{if(Array.isArray(l)||l==null||l.definitionVersion!==xu.currentProjectStateDefinitionVersion)throw new Ro("Error validating conf.state in Theatre.getProject(".concat(JSON.stringify(o),", conf). The state seems to be formatted in a way that is unreadable to Theatre.js. Read more at https://www.theatrejs.com/docs/latest/manual/projects#state"))},oM=(o,l)=>{sM(o,l)};function Su(o,l,d){const y=d?Y(d).ticker:tp();if((0,Ep.isPointer)(o))return(0,bu.pointerToPrism)(o).onChange(y,l,!0);if((0,bu.isPrism)(o))return o.onChange(y,l,!0);throw new Error("Called onChange(p) where p is neither a pointer nor a prism.")}function Tp(o){if((0,Ep.isPointer)(o))return(0,bu.pointerToPrism)(o).getValue();throw new Error("Called val(p) where p is not a pointer.")}var aM=class{constructor(){S(this,"_studio")}get type(){return"Theatre_CoreBundle"}get version(){return"0.7.2"}getBitsForStudio(o,l){if(this._studio)throw new Error("@theatre/core is already attached to @theatre/studio");this._studio=o;const d={projectsP:re.atom.pointer.projects,privateAPI:Y,coreExports:A,getCoreRafDriver:ep};l(d)}};cM();function cM(){if(typeof window>"u")return;const o=window[Jl];if(typeof o<"u")throw typeof o=="object"&&o&&typeof o.version=="string"?new Error(`It seems that the module '@theatre/core' is loaded more than once. This could have two possible causes:
1. You might have two separate versions of Theatre.js in node_modules.
2. Or this might be a bundling misconfiguration, in case you're using a bundler like Webpack/ESBuild/Rollup.

Note that it **is okay** to import '@theatre/core' multiple times. But those imports should point to the same module.`):new Error("The variable window.".concat(Jl," seems to be already set by a module other than @theatre/core."));const l=new aM;window[Jl]=l;const d=window[nE];d&&d!==null&&d.type==="Theatre_StudioBundle"&&d.registerCoreBundle(l)}/*! Bundled license information:

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
		*/})(Ko,Ko.exports)),Ko.exports}var un=UC();let ch=null,sd=null;const r_=new Map;function BC(){return ch=un.getProject("HumanBody Theatre"),sd=ch.sheet("Main"),{project:ch,sheet:sd}}function Id(){return sd}function kC(r,e){const t=r.object("Camera",{position:un.types.compound({x:un.types.number(e.position.x,{range:[-50,50]}),y:un.types.number(e.position.y,{range:[-10,20]}),z:un.types.number(e.position.z,{range:[-50,50]})}),fov:un.types.number(e.fov,{range:[10,120]})});return t.onValuesChange(n=>{e.position.set(n.position.x,n.position.y,n.position.z),e.fov=n.fov,e.updateProjectionMatrix()}),r_.set("Camera",t),t}function Ec(r,e,t){const n={position:un.types.compound({x:un.types.number(t.position.x,{range:[-20,20]}),y:un.types.number(t.position.y,{range:[0,20]}),z:un.types.number(t.position.z,{range:[-20,20]})}),intensity:un.types.number(t.intensity,{range:[0,100]}),color:un.types.rgba({r:t.color.r,g:t.color.g,b:t.color.b,a:1})},i=r.object(e,n);return i.onValuesChange(s=>{t.position.set(s.position.x,s.position.y,s.position.z),t.intensity=s.intensity,t.color.setRGB(s.color.r,s.color.g,s.color.b)}),r_.set(e,i),i}function Ld(r,e,t){const n=r.object(e,{position:un.types.compound({x:un.types.number(t.position.x,{range:[-20,20]}),y:un.types.number(t.position.y,{range:[-5,10]}),z:un.types.number(t.position.z,{range:[-20,20]})}),rotation:un.types.compound({x:un.types.number(0,{range:[-180,180]}),y:un.types.number(0,{range:[-180,180]}),z:un.types.number(0,{range:[-180,180]})}),scale:un.types.number(1,{range:[.01,10]})});return n.onValuesChange(i=>{t.position.set(i.position.x,i.position.y,i.position.z),t.rotation.set(i.rotation.x*Math.PI/180,i.rotation.y*Math.PI/180,i.rotation.z*Math.PI/180),t.scale.setScalar(i.scale)}),n}function rg(r,e){if(e===VM)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),r;if(e===Jh||e===Mg){let t=r.getIndex();if(t===null){const a=[],c=r.getAttribute("position");if(c!==void 0){for(let u=0;u<c.count;u++)a.push(u);r.setIndex(a),t=r.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),r}const n=t.count-2,i=[];if(e===Jh)for(let a=1;a<=n;a++)i.push(t.getX(0)),i.push(t.getX(a)),i.push(t.getX(a+1));else for(let a=0;a<n;a++)a%2===0?(i.push(t.getX(a)),i.push(t.getX(a+1)),i.push(t.getX(a+2))):(i.push(t.getX(a+2)),i.push(t.getX(a+1)),i.push(t.getX(a)));i.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const s=r.clone();return s.setIndex(i),s.clearGroups(),s}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),r}class zC extends ds{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new jC(t)}),this.register(function(t){return new XC(t)}),this.register(function(t){return new tD(t)}),this.register(function(t){return new nD(t)}),this.register(function(t){return new iD(t)}),this.register(function(t){return new YC(t)}),this.register(function(t){return new KC(t)}),this.register(function(t){return new $C(t)}),this.register(function(t){return new ZC(t)}),this.register(function(t){return new WC(t)}),this.register(function(t){return new QC(t)}),this.register(function(t){return new qC(t)}),this.register(function(t){return new eD(t)}),this.register(function(t){return new JC(t)}),this.register(function(t){return new VC(t)}),this.register(function(t){return new rD(t)}),this.register(function(t){return new sD(t)})}load(e,t,n,i){const s=this;let a;if(this.resourcePath!=="")a=this.resourcePath;else if(this.path!==""){const h=Qo.extractUrlBase(e);a=Qo.resolveURL(h,this.path)}else a=Qo.extractUrlBase(e);this.manager.itemStart(e);const c=function(h){i?i(h):console.error(h),s.manager.itemError(e),s.manager.itemEnd(e)},u=new Ad(this.manager);u.setPath(this.path),u.setResponseType("arraybuffer"),u.setRequestHeader(this.requestHeader),u.setWithCredentials(this.withCredentials),u.load(e,function(h){try{s.parse(h,a,function(f){t(f),s.manager.itemEnd(e)},c)}catch(f){c(f)}},n,c)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,i){let s;const a={},c={},u=new TextDecoder;if(typeof e=="string")s=JSON.parse(e);else if(e instanceof ArrayBuffer)if(u.decode(new Uint8Array(e,0,4))===s_){try{a[Rt.KHR_BINARY_GLTF]=new oD(e)}catch(p){i&&i(p);return}s=JSON.parse(a[Rt.KHR_BINARY_GLTF].content)}else s=JSON.parse(u.decode(e));else s=e;if(s.asset===void 0||s.asset.version[0]<2){i&&i(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const h=new yD(s,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});h.fileLoader.setRequestHeader(this.requestHeader);for(let f=0;f<this.pluginCallbacks.length;f++){const p=this.pluginCallbacks[f](h);p.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),c[p.name]=p,a[p.name]=!0}if(s.extensionsUsed)for(let f=0;f<s.extensionsUsed.length;++f){const p=s.extensionsUsed[f],m=s.extensionsRequired||[];switch(p){case Rt.KHR_MATERIALS_UNLIT:a[p]=new GC;break;case Rt.KHR_DRACO_MESH_COMPRESSION:a[p]=new aD(s,this.dracoLoader);break;case Rt.KHR_TEXTURE_TRANSFORM:a[p]=new cD;break;case Rt.KHR_MESH_QUANTIZATION:a[p]=new lD;break;default:m.indexOf(p)>=0&&c[p]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+p+'".')}}h.setExtensions(a),h.setPlugins(c),h.parse(n,i)}parseAsync(e,t){const n=this;return new Promise(function(i,s){n.parse(e,t,i,s)})}}function HC(){let r={};return{get:function(e){return r[e]},add:function(e,t){r[e]=t},remove:function(e){delete r[e]},removeAll:function(){r={}}}}const Rt={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class VC{constructor(e){this.parser=e,this.name=Rt.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,i=t.length;n<i;n++){const s=t[n];s.extensions&&s.extensions[this.name]&&s.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,s.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let i=t.cache.get(n);if(i)return i;const s=t.json,u=((s.extensions&&s.extensions[this.name]||{}).lights||[])[e];let h;const f=new rt(16777215);u.color!==void 0&&f.setRGB(u.color[0],u.color[1],u.color[2],jn);const p=u.range!==void 0?u.range:0;switch(u.type){case"directional":h=new Dc(f),h.target.position.set(0,0,-1),h.add(h.target);break;case"point":h=new $g(f),h.distance=p;break;case"spot":h=new KP(f),h.distance=p,u.spot=u.spot||{},u.spot.innerConeAngle=u.spot.innerConeAngle!==void 0?u.spot.innerConeAngle:0,u.spot.outerConeAngle=u.spot.outerConeAngle!==void 0?u.spot.outerConeAngle:Math.PI/4,h.angle=u.spot.outerConeAngle,h.penumbra=1-u.spot.innerConeAngle/u.spot.outerConeAngle,h.target.position.set(0,0,-1),h.add(h.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+u.type)}return h.position.set(0,0,0),h.decay=2,Qi(h,u),u.intensity!==void 0&&(h.intensity=u.intensity),h.name=t.createUniqueName(u.name||"light_"+e),i=Promise.resolve(h),t.cache.add(n,i),i}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,s=n.json.nodes[e],c=(s.extensions&&s.extensions[this.name]||{}).light;return c===void 0?null:this._loadLight(c).then(function(u){return n._getNodeRef(t.cache,c,u)})}}class GC{constructor(){this.name=Rt.KHR_MATERIALS_UNLIT}getMaterialType(){return pi}extendParams(e,t,n){const i=[];e.color=new rt(1,1,1),e.opacity=1;const s=t.pbrMetallicRoughness;if(s){if(Array.isArray(s.baseColorFactor)){const a=s.baseColorFactor;e.color.setRGB(a[0],a[1],a[2],jn),e.opacity=a[3]}s.baseColorTexture!==void 0&&i.push(n.assignTexture(e,"map",s.baseColorTexture,Tn))}return Promise.all(i)}}class WC{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name].emissiveStrength;return s!==void 0&&(t.emissiveIntensity=s),Promise.resolve()}}class jC{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];if(a.clearcoatFactor!==void 0&&(t.clearcoat=a.clearcoatFactor),a.clearcoatTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatMap",a.clearcoatTexture)),a.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=a.clearcoatRoughnessFactor),a.clearcoatRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatRoughnessMap",a.clearcoatRoughnessTexture)),a.clearcoatNormalTexture!==void 0&&(s.push(n.assignTexture(t,"clearcoatNormalMap",a.clearcoatNormalTexture)),a.clearcoatNormalTexture.scale!==void 0)){const c=a.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new ht(c,c)}return Promise.all(s)}}class XC{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.dispersion=s.dispersion!==void 0?s.dispersion:0,Promise.resolve()}}class qC{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.iridescenceFactor!==void 0&&(t.iridescence=a.iridescenceFactor),a.iridescenceTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceMap",a.iridescenceTexture)),a.iridescenceIor!==void 0&&(t.iridescenceIOR=a.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),a.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=a.iridescenceThicknessMinimum),a.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=a.iridescenceThicknessMaximum),a.iridescenceThicknessTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceThicknessMap",a.iridescenceThicknessTexture)),Promise.all(s)}}class YC{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[];t.sheenColor=new rt(0,0,0),t.sheenRoughness=0,t.sheen=1;const a=i.extensions[this.name];if(a.sheenColorFactor!==void 0){const c=a.sheenColorFactor;t.sheenColor.setRGB(c[0],c[1],c[2],jn)}return a.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=a.sheenRoughnessFactor),a.sheenColorTexture!==void 0&&s.push(n.assignTexture(t,"sheenColorMap",a.sheenColorTexture,Tn)),a.sheenRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"sheenRoughnessMap",a.sheenRoughnessTexture)),Promise.all(s)}}class KC{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.transmissionFactor!==void 0&&(t.transmission=a.transmissionFactor),a.transmissionTexture!==void 0&&s.push(n.assignTexture(t,"transmissionMap",a.transmissionTexture)),Promise.all(s)}}class $C{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.thickness=a.thicknessFactor!==void 0?a.thicknessFactor:0,a.thicknessTexture!==void 0&&s.push(n.assignTexture(t,"thicknessMap",a.thicknessTexture)),t.attenuationDistance=a.attenuationDistance||1/0;const c=a.attenuationColor||[1,1,1];return t.attenuationColor=new rt().setRGB(c[0],c[1],c[2],jn),Promise.all(s)}}class ZC{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.ior=s.ior!==void 0?s.ior:1.5,Promise.resolve()}}class QC{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.specularIntensity=a.specularFactor!==void 0?a.specularFactor:1,a.specularTexture!==void 0&&s.push(n.assignTexture(t,"specularIntensityMap",a.specularTexture));const c=a.specularColorFactor||[1,1,1];return t.specularColor=new rt().setRGB(c[0],c[1],c[2],jn),a.specularColorTexture!==void 0&&s.push(n.assignTexture(t,"specularColorMap",a.specularColorTexture,Tn)),Promise.all(s)}}class JC{constructor(e){this.parser=e,this.name=Rt.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return t.bumpScale=a.bumpFactor!==void 0?a.bumpFactor:1,a.bumpTexture!==void 0&&s.push(n.assignTexture(t,"bumpMap",a.bumpTexture)),Promise.all(s)}}class eD{constructor(e){this.parser=e,this.name=Rt.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Fi}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.anisotropyStrength!==void 0&&(t.anisotropy=a.anisotropyStrength),a.anisotropyRotation!==void 0&&(t.anisotropyRotation=a.anisotropyRotation),a.anisotropyTexture!==void 0&&s.push(n.assignTexture(t,"anisotropyMap",a.anisotropyTexture)),Promise.all(s)}}class tD{constructor(e){this.parser=e,this.name=Rt.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,i=n.textures[e];if(!i.extensions||!i.extensions[this.name])return null;const s=i.extensions[this.name],a=t.options.ktx2Loader;if(!a){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,s.source,a)}}class nD{constructor(e){this.parser=e,this.name=Rt.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class iD{constructor(e){this.parser=e,this.name=Rt.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class rD{constructor(e){this.name=Rt.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const i=n.extensions[this.name],s=this.parser.getDependency("buffer",i.buffer),a=this.parser.options.meshoptDecoder;if(!a||!a.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return s.then(function(c){const u=i.byteOffset||0,h=i.byteLength||0,f=i.count,p=i.byteStride,m=new Uint8Array(c,u,h);return a.decodeGltfBufferAsync?a.decodeGltfBufferAsync(f,p,m,i.mode,i.filter).then(function(g){return g.buffer}):a.ready.then(function(){const g=new ArrayBuffer(f*p);return a.decodeGltfBuffer(new Uint8Array(g),f,p,m,i.mode,i.filter),g})})}else return null}}class sD{constructor(e){this.name=Rt.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const i=t.meshes[n.mesh];for(const h of i.primitives)if(h.mode!==di.TRIANGLES&&h.mode!==di.TRIANGLE_STRIP&&h.mode!==di.TRIANGLE_FAN&&h.mode!==void 0)return null;const a=n.extensions[this.name].attributes,c=[],u={};for(const h in a)c.push(this.parser.getDependency("accessor",a[h]).then(f=>(u[h]=f,u[h])));return c.length<1?null:(c.push(this.parser.createNodeMesh(e)),Promise.all(c).then(h=>{const f=h.pop(),p=f.isGroup?f.children:[f],m=h[0].count,g=[];for(const x of p){const E=new pt,v=new U,_=new Mt,R=new U(1,1,1),w=new LP(x.geometry,x.material,m);for(let S=0;S<m;S++)u.TRANSLATION&&v.fromBufferAttribute(u.TRANSLATION,S),u.ROTATION&&_.fromBufferAttribute(u.ROTATION,S),u.SCALE&&R.fromBufferAttribute(u.SCALE,S),w.setMatrixAt(S,E.compose(v,_,R));for(const S in u)if(S==="_COLOR_0"){const z=u[S];w.instanceColor=new nd(z.array,z.itemSize,z.normalized)}else S!=="TRANSLATION"&&S!=="ROTATION"&&S!=="SCALE"&&x.geometry.setAttribute(S,u[S]);rn.prototype.copy.call(w,x),this.parser.assignFinalMaterial(w),g.push(w)}return f.isGroup?(f.clear(),f.add(...g),f):g[0]}))}}const s_="glTF",Go=12,sg={JSON:1313821514,BIN:5130562};class oD{constructor(e){this.name=Rt.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,Go),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==s_)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const i=this.header.length-Go,s=new DataView(e,Go);let a=0;for(;a<i;){const c=s.getUint32(a,!0);a+=4;const u=s.getUint32(a,!0);if(a+=4,u===sg.JSON){const h=new Uint8Array(e,Go+a,c);this.content=n.decode(h)}else if(u===sg.BIN){const h=Go+a;this.body=e.slice(h,h+c)}a+=c}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class aD{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=Rt.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,i=this.dracoLoader,s=e.extensions[this.name].bufferView,a=e.extensions[this.name].attributes,c={},u={},h={};for(const f in a){const p=od[f]||f.toLowerCase();c[p]=a[f]}for(const f in e.attributes){const p=od[f]||f.toLowerCase();if(a[f]!==void 0){const m=n.accessors[e.attributes[f]],g=$s[m.componentType];h[p]=g.name,u[p]=m.normalized===!0}}return t.getDependency("bufferView",s).then(function(f){return new Promise(function(p,m){i.decodeDracoFile(f,function(g){for(const x in g.attributes){const E=g.attributes[x],v=u[x];v!==void 0&&(E.normalized=v)}p(g)},c,h,jn,m)})})}}class cD{constructor(){this.name=Rt.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class lD{constructor(){this.name=Rt.KHR_MESH_QUANTIZATION}}class o_ extends oa{constructor(e,t,n,i){super(e,t,n,i)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i*3+i;for(let a=0;a!==i;a++)t[a]=n[s+a];return t}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=c*2,h=c*3,f=i-t,p=(n-t)/f,m=p*p,g=m*p,x=e*h,E=x-h,v=-2*g+3*m,_=g-m,R=1-v,w=_-m+p;for(let S=0;S!==c;S++){const z=a[E+S+c],O=a[E+S+u]*f,N=a[x+S+c],V=a[x+S]*f;s[S]=R*z+w*O+v*N+_*V}return s}}const uD=new Mt;class hD extends o_{interpolate_(e,t,n,i){const s=super.interpolate_(e,t,n,i);return uD.fromArray(s).normalize().toArray(s),s}}const di={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},$s={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},og={9728:Wn,9729:ai,9984:pg,9985:Mc,9986:Wo,9987:Ji},ag={33071:br,33648:Fc,10497:eo},lh={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},od={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},vr={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},dD={CUBICSPLINE:void 0,LINEAR:ta,STEP:ea},uh={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function fD(r){return r.DefaultMaterial===void 0&&(r.DefaultMaterial=new hs({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:ir})),r.DefaultMaterial}function is(r,e,t){for(const n in t.extensions)r[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function Qi(r,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(r.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function pD(r,e,t){let n=!1,i=!1,s=!1;for(let h=0,f=e.length;h<f;h++){const p=e[h];if(p.POSITION!==void 0&&(n=!0),p.NORMAL!==void 0&&(i=!0),p.COLOR_0!==void 0&&(s=!0),n&&i&&s)break}if(!n&&!i&&!s)return Promise.resolve(r);const a=[],c=[],u=[];for(let h=0,f=e.length;h<f;h++){const p=e[h];if(n){const m=p.POSITION!==void 0?t.getDependency("accessor",p.POSITION):r.attributes.position;a.push(m)}if(i){const m=p.NORMAL!==void 0?t.getDependency("accessor",p.NORMAL):r.attributes.normal;c.push(m)}if(s){const m=p.COLOR_0!==void 0?t.getDependency("accessor",p.COLOR_0):r.attributes.color;u.push(m)}}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u)]).then(function(h){const f=h[0],p=h[1],m=h[2];return n&&(r.morphAttributes.position=f),i&&(r.morphAttributes.normal=p),s&&(r.morphAttributes.color=m),r.morphTargetsRelative=!0,r})}function mD(r,e){if(r.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)r.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(r.morphTargetInfluences.length===t.length){r.morphTargetDictionary={};for(let n=0,i=t.length;n<i;n++)r.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function gD(r){let e;const t=r.extensions&&r.extensions[Rt.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+hh(t.attributes):e=r.indices+":"+hh(r.attributes)+":"+r.mode,r.targets!==void 0)for(let n=0,i=r.targets.length;n<i;n++)e+=":"+hh(r.targets[n]);return e}function hh(r){let e="";const t=Object.keys(r).sort();for(let n=0,i=t.length;n<i;n++)e+=t[n]+":"+r[t[n]]+";";return e}function ad(r){switch(r){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function _D(r){return r.search(/\.jpe?g($|\?)/i)>0||r.search(/^data\:image\/jpeg/)===0?"image/jpeg":r.search(/\.webp($|\?)/i)>0||r.search(/^data\:image\/webp/)===0?"image/webp":r.search(/\.ktx2($|\?)/i)>0||r.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const vD=new pt;class yD{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new HC,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,i=-1,s=!1,a=-1;if(typeof navigator<"u"){const c=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(c)===!0;const u=c.match(/Version\/(\d+)/);i=n&&u?parseInt(u[1],10):-1,s=c.indexOf("Firefox")>-1,a=s?c.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&i<17||s&&a<98?this.textureLoader=new qP(this.options.manager):this.textureLoader=new JP(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new Ad(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,i=this.json,s=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(a){return a._markDefs&&a._markDefs()}),Promise.all(this._invokeAll(function(a){return a.beforeRoot&&a.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(a){const c={scene:a[0][i.scene||0],scenes:a[0],animations:a[1],cameras:a[2],asset:i.asset,parser:n,userData:{}};return is(s,c,i),Qi(c,i),Promise.all(n._invokeAll(function(u){return u.afterRoot&&u.afterRoot(c)})).then(function(){for(const u of c.scenes)u.updateMatrixWorld();e(c)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let i=0,s=t.length;i<s;i++){const a=t[i].joints;for(let c=0,u=a.length;c<u;c++)e[a[c]].isBone=!0}for(let i=0,s=e.length;i<s;i++){const a=e[i];a.mesh!==void 0&&(this._addNodeRef(this.meshCache,a.mesh),a.skin!==void 0&&(n[a.mesh].isSkinnedMesh=!0)),a.camera!==void 0&&this._addNodeRef(this.cameraCache,a.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const i=n.clone(),s=(a,c)=>{const u=this.associations.get(a);u!=null&&this.associations.set(c,u);for(const[h,f]of a.children.entries())s(f,c.children[h])};return s(n,i),i.name+="_instance_"+e.uses[t]++,i}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const i=e(t[n]);if(i)return i}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let i=0;i<t.length;i++){const s=e(t[i]);s&&n.push(s)}return n}getDependency(e,t){const n=e+":"+t;let i=this.cache.get(n);if(!i){switch(e){case"scene":i=this.loadScene(t);break;case"node":i=this._invokeOne(function(s){return s.loadNode&&s.loadNode(t)});break;case"mesh":i=this._invokeOne(function(s){return s.loadMesh&&s.loadMesh(t)});break;case"accessor":i=this.loadAccessor(t);break;case"bufferView":i=this._invokeOne(function(s){return s.loadBufferView&&s.loadBufferView(t)});break;case"buffer":i=this.loadBuffer(t);break;case"material":i=this._invokeOne(function(s){return s.loadMaterial&&s.loadMaterial(t)});break;case"texture":i=this._invokeOne(function(s){return s.loadTexture&&s.loadTexture(t)});break;case"skin":i=this.loadSkin(t);break;case"animation":i=this._invokeOne(function(s){return s.loadAnimation&&s.loadAnimation(t)});break;case"camera":i=this.loadCamera(t);break;default:if(i=this._invokeOne(function(s){return s!=this&&s.getDependency&&s.getDependency(e,t)}),!i)throw new Error("Unknown type: "+e);break}this.cache.add(n,i)}return i}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,i=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(i.map(function(s,a){return n.getDependency(e,a)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[Rt.KHR_BINARY_GLTF].body);const i=this.options;return new Promise(function(s,a){n.load(Qo.resolveURL(t.uri,i.path),s,void 0,function(){a(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const i=t.byteLength||0,s=t.byteOffset||0;return n.slice(s,s+i)})}loadAccessor(e){const t=this,n=this.json,i=this.json.accessors[e];if(i.bufferView===void 0&&i.sparse===void 0){const a=lh[i.type],c=$s[i.componentType],u=i.normalized===!0,h=new c(i.count*a);return Promise.resolve(new hn(h,a,u))}const s=[];return i.bufferView!==void 0?s.push(this.getDependency("bufferView",i.bufferView)):s.push(null),i.sparse!==void 0&&(s.push(this.getDependency("bufferView",i.sparse.indices.bufferView)),s.push(this.getDependency("bufferView",i.sparse.values.bufferView))),Promise.all(s).then(function(a){const c=a[0],u=lh[i.type],h=$s[i.componentType],f=h.BYTES_PER_ELEMENT,p=f*u,m=i.byteOffset||0,g=i.bufferView!==void 0?n.bufferViews[i.bufferView].byteStride:void 0,x=i.normalized===!0;let E,v;if(g&&g!==p){const _=Math.floor(m/g),R="InterleavedBuffer:"+i.bufferView+":"+i.componentType+":"+_+":"+i.count;let w=t.cache.get(R);w||(E=new h(c,_*g,i.count*g/f),w=new PP(E,g/f),t.cache.add(R,w)),v=new Md(w,u,m%g/f,x)}else c===null?E=new h(i.count*u):E=new h(c,m,i.count*u),v=new hn(E,u,x);if(i.sparse!==void 0){const _=lh.SCALAR,R=$s[i.sparse.indices.componentType],w=i.sparse.indices.byteOffset||0,S=i.sparse.values.byteOffset||0,z=new R(a[1],w,i.sparse.count*_),O=new h(a[2],S,i.sparse.count*u);c!==null&&(v=new hn(v.array.slice(),v.itemSize,v.normalized)),v.normalized=!1;for(let N=0,V=z.length;N<V;N++){const D=z[N];if(v.setX(D,O[N*u]),u>=2&&v.setY(D,O[N*u+1]),u>=3&&v.setZ(D,O[N*u+2]),u>=4&&v.setW(D,O[N*u+3]),u>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}v.normalized=x}return v})}loadTexture(e){const t=this.json,n=this.options,s=t.textures[e].source,a=t.images[s];let c=this.textureLoader;if(a.uri){const u=n.manager.getHandler(a.uri);u!==null&&(c=u)}return this.loadTextureImage(e,s,c)}loadTextureImage(e,t,n){const i=this,s=this.json,a=s.textures[e],c=s.images[t],u=(c.uri||c.bufferView)+":"+a.sampler;if(this.textureCache[u])return this.textureCache[u];const h=this.loadImageSource(t,n).then(function(f){f.flipY=!1,f.name=a.name||c.name||"",f.name===""&&typeof c.uri=="string"&&c.uri.startsWith("data:image/")===!1&&(f.name=c.uri);const m=(s.samplers||{})[a.sampler]||{};return f.magFilter=og[m.magFilter]||ai,f.minFilter=og[m.minFilter]||Ji,f.wrapS=ag[m.wrapS]||eo,f.wrapT=ag[m.wrapT]||eo,f.generateMipmaps=!f.isCompressedTexture&&f.minFilter!==Wn&&f.minFilter!==ai,i.associations.set(f,{textures:e}),f}).catch(function(){return null});return this.textureCache[u]=h,h}loadImageSource(e,t){const n=this,i=this.json,s=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(p=>p.clone());const a=i.images[e],c=self.URL||self.webkitURL;let u=a.uri||"",h=!1;if(a.bufferView!==void 0)u=n.getDependency("bufferView",a.bufferView).then(function(p){h=!0;const m=new Blob([p],{type:a.mimeType});return u=c.createObjectURL(m),u});else if(a.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const f=Promise.resolve(u).then(function(p){return new Promise(function(m,g){let x=m;t.isImageBitmapLoader===!0&&(x=function(E){const v=new wn(E);v.needsUpdate=!0,m(v)}),t.load(Qo.resolveURL(p,s.path),x,void 0,g)})}).then(function(p){return h===!0&&c.revokeObjectURL(u),Qi(p,a),p.userData.mimeType=a.mimeType||_D(a.uri),p}).catch(function(p){throw console.error("THREE.GLTFLoader: Couldn't load texture",u),p});return this.sourceCache[e]=f,f}assignTexture(e,t,n,i){const s=this;return this.getDependency("texture",n.index).then(function(a){if(!a)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(a=a.clone(),a.channel=n.texCoord),s.extensions[Rt.KHR_TEXTURE_TRANSFORM]){const c=n.extensions!==void 0?n.extensions[Rt.KHR_TEXTURE_TRANSFORM]:void 0;if(c){const u=s.associations.get(a);a=s.extensions[Rt.KHR_TEXTURE_TRANSFORM].extendTexture(a,c),s.associations.set(a,u)}}return i!==void 0&&(a.colorSpace=i),e[t]=a,a})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const i=t.attributes.tangent===void 0,s=t.attributes.color!==void 0,a=t.attributes.normal===void 0;if(e.isPoints){const c="PointsMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Xg,Ii.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,u.sizeAttenuation=!1,this.cache.add(c,u)),n=u}else if(e.isLine){const c="LineBasicMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Gc,Ii.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,this.cache.add(c,u)),n=u}if(i||s||a){let c="ClonedMaterial:"+n.uuid+":";i&&(c+="derivative-tangents:"),s&&(c+="vertex-colors:"),a&&(c+="flat-shading:");let u=this.cache.get(c);u||(u=n.clone(),s&&(u.vertexColors=!0),a&&(u.flatShading=!0),i&&(u.normalScale&&(u.normalScale.y*=-1),u.clearcoatNormalScale&&(u.clearcoatNormalScale.y*=-1)),this.cache.add(c,u),this.associations.set(u,this.associations.get(n))),n=u}e.material=n}getMaterialType(){return hs}loadMaterial(e){const t=this,n=this.json,i=this.extensions,s=n.materials[e];let a;const c={},u=s.extensions||{},h=[];if(u[Rt.KHR_MATERIALS_UNLIT]){const p=i[Rt.KHR_MATERIALS_UNLIT];a=p.getMaterialType(),h.push(p.extendParams(c,s,t))}else{const p=s.pbrMetallicRoughness||{};if(c.color=new rt(1,1,1),c.opacity=1,Array.isArray(p.baseColorFactor)){const m=p.baseColorFactor;c.color.setRGB(m[0],m[1],m[2],jn),c.opacity=m[3]}p.baseColorTexture!==void 0&&h.push(t.assignTexture(c,"map",p.baseColorTexture,Tn)),c.metalness=p.metallicFactor!==void 0?p.metallicFactor:1,c.roughness=p.roughnessFactor!==void 0?p.roughnessFactor:1,p.metallicRoughnessTexture!==void 0&&(h.push(t.assignTexture(c,"metalnessMap",p.metallicRoughnessTexture)),h.push(t.assignTexture(c,"roughnessMap",p.metallicRoughnessTexture))),a=this._invokeOne(function(m){return m.getMaterialType&&m.getMaterialType(e)}),h.push(Promise.all(this._invokeAll(function(m){return m.extendMaterialParams&&m.extendMaterialParams(e,c)})))}s.doubleSided===!0&&(c.side=$n);const f=s.alphaMode||uh.OPAQUE;if(f===uh.BLEND?(c.transparent=!0,c.depthWrite=!1):(c.transparent=!1,f===uh.MASK&&(c.alphaTest=s.alphaCutoff!==void 0?s.alphaCutoff:.5)),s.normalTexture!==void 0&&a!==pi&&(h.push(t.assignTexture(c,"normalMap",s.normalTexture)),c.normalScale=new ht(1,1),s.normalTexture.scale!==void 0)){const p=s.normalTexture.scale;c.normalScale.set(p,p)}if(s.occlusionTexture!==void 0&&a!==pi&&(h.push(t.assignTexture(c,"aoMap",s.occlusionTexture)),s.occlusionTexture.strength!==void 0&&(c.aoMapIntensity=s.occlusionTexture.strength)),s.emissiveFactor!==void 0&&a!==pi){const p=s.emissiveFactor;c.emissive=new rt().setRGB(p[0],p[1],p[2],jn)}return s.emissiveTexture!==void 0&&a!==pi&&h.push(t.assignTexture(c,"emissiveMap",s.emissiveTexture,Tn)),Promise.all(h).then(function(){const p=new a(c);return s.name&&(p.name=s.name),Qi(p,s),t.associations.set(p,{materials:e}),s.extensions&&is(i,p,s),p})}createUniqueName(e){const t=zt.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,i=this.primitiveCache;function s(c){return n[Rt.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(c,t).then(function(u){return cg(u,c,t)})}const a=[];for(let c=0,u=e.length;c<u;c++){const h=e[c],f=gD(h),p=i[f];if(p)a.push(p.promise);else{let m;h.extensions&&h.extensions[Rt.KHR_DRACO_MESH_COMPRESSION]?m=s(h):m=cg(new yn,h,t),i[f]={primitive:h,promise:m},a.push(m)}}return Promise.all(a)}loadMesh(e){const t=this,n=this.json,i=this.extensions,s=n.meshes[e],a=s.primitives,c=[];for(let u=0,h=a.length;u<h;u++){const f=a[u].material===void 0?fD(this.cache):this.getDependency("material",a[u].material);c.push(f)}return c.push(t.loadGeometries(a)),Promise.all(c).then(function(u){const h=u.slice(0,u.length-1),f=u[u.length-1],p=[];for(let g=0,x=f.length;g<x;g++){const E=f[g],v=a[g];let _;const R=h[g];if(v.mode===di.TRIANGLES||v.mode===di.TRIANGLE_STRIP||v.mode===di.TRIANGLE_FAN||v.mode===void 0)_=s.isSkinnedMesh===!0?new Gg(E,R):new Pe(E,R),_.isSkinnedMesh===!0&&_.normalizeSkinWeights(),v.mode===di.TRIANGLE_STRIP?_.geometry=rg(_.geometry,Mg):v.mode===di.TRIANGLE_FAN&&(_.geometry=rg(_.geometry,Jh));else if(v.mode===di.LINES)_=new jg(E,R);else if(v.mode===di.LINE_STRIP)_=new xi(E,R);else if(v.mode===di.LINE_LOOP)_=new FP(E,R);else if(v.mode===di.POINTS)_=new NP(E,R);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+v.mode);Object.keys(_.geometry.morphAttributes).length>0&&mD(_,s),_.name=t.createUniqueName(s.name||"mesh_"+e),Qi(_,s),v.extensions&&is(i,_,v),t.assignFinalMaterial(_),p.push(_)}for(let g=0,x=p.length;g<x;g++)t.associations.set(p[g],{meshes:e,primitives:g});if(p.length===1)return s.extensions&&is(i,p[0],s),p[0];const m=new tr;s.extensions&&is(i,m,s),t.associations.set(m,{meshes:e});for(let g=0,x=p.length;g<x;g++)m.add(p[g]);return m})}loadCamera(e){let t;const n=this.json.cameras[e],i=n[n.type];if(!i){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new Gn(Ag.radToDeg(i.yfov),i.aspectRatio||1,i.znear||1,i.zfar||2e6):n.type==="orthographic"&&(t=new bd(-i.xmag,i.xmag,i.ymag,-i.ymag,i.znear,i.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),Qi(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let i=0,s=t.joints.length;i<s;i++)n.push(this._loadNodeShallow(t.joints[i]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(i){const s=i.pop(),a=i,c=[],u=[];for(let h=0,f=a.length;h<f;h++){const p=a[h];if(p){c.push(p);const m=new pt;s!==null&&m.fromArray(s.array,h*16),u.push(m)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[h])}return new ra(c,u)})}loadAnimation(e){const t=this.json,n=this,i=t.animations[e],s=i.name?i.name:"animation_"+e,a=[],c=[],u=[],h=[],f=[];for(let p=0,m=i.channels.length;p<m;p++){const g=i.channels[p],x=i.samplers[g.sampler],E=g.target,v=E.node,_=i.parameters!==void 0?i.parameters[x.input]:x.input,R=i.parameters!==void 0?i.parameters[x.output]:x.output;E.node!==void 0&&(a.push(this.getDependency("node",v)),c.push(this.getDependency("accessor",_)),u.push(this.getDependency("accessor",R)),h.push(x),f.push(E))}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u),Promise.all(h),Promise.all(f)]).then(function(p){const m=p[0],g=p[1],x=p[2],E=p[3],v=p[4],_=[];for(let R=0,w=m.length;R<w;R++){const S=m[R],z=g[R],O=x[R],N=E[R],V=v[R];if(S===void 0)continue;S.updateMatrix&&S.updateMatrix();const D=n._createAnimationTracks(S,z,O,N,V);if(D)for(let A=0;A<D.length;A++)_.push(D[A])}return new oo(s,void 0,_)})}createNodeMesh(e){const t=this.json,n=this,i=t.nodes[e];return i.mesh===void 0?null:n.getDependency("mesh",i.mesh).then(function(s){const a=n._getNodeRef(n.meshCache,i.mesh,s);return i.weights!==void 0&&a.traverse(function(c){if(c.isMesh)for(let u=0,h=i.weights.length;u<h;u++)c.morphTargetInfluences[u]=i.weights[u]}),a})}loadNode(e){const t=this.json,n=this,i=t.nodes[e],s=n._loadNodeShallow(e),a=[],c=i.children||[];for(let h=0,f=c.length;h<f;h++)a.push(n.getDependency("node",c[h]));const u=i.skin===void 0?Promise.resolve(null):n.getDependency("skin",i.skin);return Promise.all([s,Promise.all(a),u]).then(function(h){const f=h[0],p=h[1],m=h[2];m!==null&&f.traverse(function(g){g.isSkinnedMesh&&g.bind(m,vD)});for(let g=0,x=p.length;g<x;g++)f.add(p[g]);return f})}_loadNodeShallow(e){const t=this.json,n=this.extensions,i=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const s=t.nodes[e],a=s.name?i.createUniqueName(s.name):"",c=[],u=i._invokeOne(function(h){return h.createNodeMesh&&h.createNodeMesh(e)});return u&&c.push(u),s.camera!==void 0&&c.push(i.getDependency("camera",s.camera).then(function(h){return i._getNodeRef(i.cameraCache,s.camera,h)})),i._invokeAll(function(h){return h.createNodeAttachment&&h.createNodeAttachment(e)}).forEach(function(h){c.push(h)}),this.nodeCache[e]=Promise.all(c).then(function(h){let f;if(s.isBone===!0?f=new Vc:h.length>1?f=new tr:h.length===1?f=h[0]:f=new rn,f!==h[0])for(let p=0,m=h.length;p<m;p++)f.add(h[p]);if(s.name&&(f.userData.name=s.name,f.name=a),Qi(f,s),s.extensions&&is(n,f,s),s.matrix!==void 0){const p=new pt;p.fromArray(s.matrix),f.applyMatrix4(p)}else s.translation!==void 0&&f.position.fromArray(s.translation),s.rotation!==void 0&&f.quaternion.fromArray(s.rotation),s.scale!==void 0&&f.scale.fromArray(s.scale);return i.associations.has(f)||i.associations.set(f,{}),i.associations.get(f).nodes=e,f}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],i=this,s=new tr;n.name&&(s.name=i.createUniqueName(n.name)),Qi(s,n),n.extensions&&is(t,s,n);const a=n.nodes||[],c=[];for(let u=0,h=a.length;u<h;u++)c.push(i.getDependency("node",a[u]));return Promise.all(c).then(function(u){for(let f=0,p=u.length;f<p;f++)s.add(u[f]);const h=f=>{const p=new Map;for(const[m,g]of i.associations)(m instanceof Ii||m instanceof wn)&&p.set(m,g);return f.traverse(m=>{const g=i.associations.get(m);g!=null&&p.set(m,g)}),p};return i.associations=h(s),s})}_createAnimationTracks(e,t,n,i,s){const a=[],c=e.name?e.name:e.uuid,u=[];vr[s.path]===vr.weights?e.traverse(function(m){m.morphTargetInfluences&&u.push(m.name?m.name:m.uuid)}):u.push(c);let h;switch(vr[s.path]){case vr.weights:h=so;break;case vr.rotation:h=wr;break;case vr.position:case vr.scale:h=Ar;break;default:switch(n.itemSize){case 1:h=so;break;case 2:case 3:default:h=Ar;break}break}const f=i.interpolation!==void 0?dD[i.interpolation]:ta,p=this._getArrayFromAccessor(n);for(let m=0,g=u.length;m<g;m++){const x=new h(u[m]+"."+vr[s.path],t.array,p,f);i.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(x),a.push(x)}return a}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=ad(t.constructor),i=new Float32Array(t.length);for(let s=0,a=t.length;s<a;s++)i[s]=t[s]*n;t=i}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const i=this instanceof wr?hD:o_;return new i(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function xD(r,e,t){const n=e.attributes,i=new Ti;if(n.POSITION!==void 0){const c=t.json.accessors[n.POSITION],u=c.min,h=c.max;if(u!==void 0&&h!==void 0){if(i.set(new U(u[0],u[1],u[2]),new U(h[0],h[1],h[2])),c.normalized){const f=ad($s[c.componentType]);i.min.multiplyScalar(f),i.max.multiplyScalar(f)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const s=e.targets;if(s!==void 0){const c=new U,u=new U;for(let h=0,f=s.length;h<f;h++){const p=s[h];if(p.POSITION!==void 0){const m=t.json.accessors[p.POSITION],g=m.min,x=m.max;if(g!==void 0&&x!==void 0){if(u.setX(Math.max(Math.abs(g[0]),Math.abs(x[0]))),u.setY(Math.max(Math.abs(g[1]),Math.abs(x[1]))),u.setZ(Math.max(Math.abs(g[2]),Math.abs(x[2]))),m.normalized){const E=ad($s[m.componentType]);u.multiplyScalar(E)}c.max(u)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}i.expandByVector(c)}r.boundingBox=i;const a=new Li;i.getCenter(a.center),a.radius=i.min.distanceTo(i.max)/2,r.boundingSphere=a}function cg(r,e,t){const n=e.attributes,i=[];function s(a,c){return t.getDependency("accessor",a).then(function(u){r.setAttribute(c,u)})}for(const a in n){const c=od[a]||a.toLowerCase();c in r.attributes||i.push(s(n[a],c))}if(e.indices!==void 0&&!r.index){const a=t.getDependency("accessor",e.indices).then(function(c){r.setIndex(c)});i.push(a)}return Lt.workingColorSpace!==jn&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${Lt.workingColorSpace}" not supported.`),Qi(r,e),xD(r,e,t),Promise.all(i).then(function(){return e.targets!==void 0?pD(r,e.targets,t):r})}const a_=new zC,bD=new n_;let ao=0;async function SD(r,e){return new Promise((t,n)=>{a_.load(r,i=>{const s=i.scene;e.add(s),s.traverse(u=>{u.isMesh&&(u.castShadow=!0,u.receiveShadow=!0)}),ao++;const a=`Asset ${ao}`,c=Id();c&&Ld(c,a,s),t(s)},void 0,i=>n(i))})}async function ED(r,e){const t=URL.createObjectURL(r);try{return await SD(t,e)}finally{URL.revokeObjectURL(t)}}const MD=[{color:13935988,roughness:.55,metalness:0},{color:13935988,roughness:.55,metalness:0},{color:1118481,roughness:.8,metalness:0},{color:657930,roughness:.1,metalness:0},{color:16052456,roughness:.2,metalness:0},{color:16052456,roughness:.05,metalness:0,opacity:.3,transparent:!0},{color:4881051,roughness:.15,metalness:0},{color:11885162,roughness:.7,metalness:0},{color:15789280,roughness:.3,metalness:0},{color:14723210,roughness:.4,metalness:0},{color:14723210,roughness:.4,metalness:0}];function Lc(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Float32Array(t.buffer)}function c_(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Uint32Array(t.buffer)}function cd(r){for(let e=0;e<r.length;e+=3){const t=r[e+1],n=r[e+2];r[e+1]=n,r[e+2]=-t}}function TD(r){const e=Lc(r.vertices),t=c_(r.faces);cd(e);const n=new yn,i=new hn(e,3),s=new hn(t,1);if(n.setAttribute("position",i),n.setIndex(s),r.uvs){const f=Lc(r.uvs);n.setAttribute("uv",new hn(f,2))}if(r.normals){const f=Lc(r.normals);cd(f),n.setAttribute("normal",new hn(f,3))}else n.computeVertexNormals();const a=MD.map(f=>new hs({color:f.color,roughness:f.roughness,metalness:f.metalness,side:$n,transparent:f.transparent||!1,opacity:f.opacity!==void 0?f.opacity:1})),c=r.groups||[];let u;if(s&&c.length>0){for(const f of c)n.addGroup(f.start,f.count,f.materialIndex);u=new Pe(n,a)}else u=new Pe(n,a[0]);u.castShadow=!0,u.receiveShadow=!0;const h=new tr;return h.add(u),h}async function dh(r,e,t){const n=new URLSearchParams;if(e.body_type&&n.set("body_type",e.body_type),e.morphs&&typeof e.morphs=="object")for(const[m,g]of Object.entries(e.morphs))g!=null&&n.set(`morph_${m}`,String(g));if(e.user_morphs&&typeof e.user_morphs=="object")for(const[m,g]of Object.entries(e.user_morphs))g!=null&&n.set(`morph_${m}`,String(g));const i=["age","mass","tone","height"],s=e.meta||{};for(const m of i){const g=s[m]??e[`meta_${m}`];g!=null&&n.set(`meta_${m}`,String(g))}const a=`/api/character/mesh/?${n.toString()}`,c=await fetch(a);if(!c.ok)throw new Error(`Character mesh API error: ${c.status}`);const u=await c.json(),h=TD(u);if(r.add(h),h.userData.bodyType=e.body_type||"Female_Caucasian",h.userData.morphs={...e.morphs||{},...e.user_morphs||{}},h.userData.meta={...e.meta||{}},h.userData.presetName=t,e.hair_style&&e.hair_style.url)try{const m=await wD(e.hair_style.url);m.userData.isHair=!0,m.traverse(g=>{g.isMesh&&(g.userData.isHair=!0)}),h.add(m),console.log("✓ Hair loaded:",e.hair_style.name)}catch(m){console.error("Failed to load hair:",m)}if(e.garments&&Array.isArray(e.garments))for(const m of e.garments)try{const g=await AD(m,e.body_type);g.userData.isGarment=!0,h.add(g),console.log("✓ Garment loaded:",m.id)}catch(g){console.error("Failed to load garment:",m.id,g)}ao++;const f=t||`Character ${ao}`,p=Id();return p&&Ld(p,f,h),h}async function wD(r){return new Promise((e,t)=>{a_.load(r,n=>{const i=n.scene;i.traverse(s=>{if(s.isMesh&&(s.castShadow=!0,s.receiveShadow=!0,s.material)){if(s.material.color){const a=s.material.color;a.r>.9&&a.g>.9&&a.b>.9&&s.material.color.setRGB(.1,.08,.06)}s.material.roughness===void 0&&(s.material.roughness=.8),s.material.metalness===void 0&&(s.material.metalness=0)}}),e(i)},void 0,n=>t(n))})}async function AD(r,e){const{id:t,offset:n=.006,stiffness:i=.8,color:s=[.3,.35,.5],roughness:a=.8,metalness:c=0}=r,u=s[0]??.3,h=s[1]??.35,f=s[2]??.5,p=`garment_id=${encodeURIComponent(t)}&body_type=${encodeURIComponent(e)}&offset=${n}&stiffness=${i}&color_r=${u.toFixed(3)}&color_g=${h.toFixed(3)}&color_b=${f.toFixed(3)}`,m=await fetch(`/api/character/garment/fit/?${p}`);if(!m.ok)throw new Error(`Garment fit API error: ${m.status}`);const g=await m.json();if(g.error)throw new Error(g.error);const x=Lc(g.vertices);cd(x);const E=c_(g.faces),v=new yn;v.setAttribute("position",new hn(x,3)),v.setIndex(new hn(E,1)),v.computeVertexNormals();const _=new rt(g.color[0],g.color[1],g.color[2]),R=new hs({color:_,roughness:a,metalness:c,side:$n,polygonOffset:!0,polygonOffsetFactor:-1,polygonOffsetUnit:-1}),w=new Pe(v,R);return w.castShadow=!0,w.receiveShadow=!0,w.userData.garmentId=t,w.userData.offset=n,w.userData.stiffness=i,w.userData.originalColor=[u,h,f],w.userData.roughness=a,w.userData.metalness=c,w.name=t,w}function RD(r,e,t){const n=bD.parse(r),i=new Jg(n.skeleton.bones[0]);i.skeleton=n.skeleton,i.visible=!0,i.userData.isRig=!0,i.renderOrder=999,i.material&&(i.material.depthTest=!1,i.material.depthWrite=!1);const s=n.skeleton.bones[0];s.userData.isRig=!0,e.add(s),e.add(i);const a=new Zg(s),c=a.clipAction(n.clip);c.setLoop(gd),c.play(),c.paused=!0,ao++;const u=Id();u&&Ld(u,t||`BVH ${ao}`,s);const h=n.clip.duration||1;return{mixer:a,action:c,skeleton:i,clip:n.clip,rootBone:s,duration:h}}class PD{constructor(e){this._canvas=e,this._recorder=null,this._chunks=[]}start(e=30){const t=this._canvas.captureStream(e);this._chunks=[];const n=MediaRecorder.isTypeSupported("video/webm;codecs=vp9")?"video/webm;codecs=vp9":"video/webm;codecs=vp8";this._recorder=new MediaRecorder(t,{mimeType:n,videoBitsPerSecond:8e6}),this._recorder.ondataavailable=i=>{i.data.size>0&&this._chunks.push(i.data)},this._recorder.start()}stop(){return new Promise(e=>{this._recorder.onstop=()=>{const t=new Blob(this._chunks,{type:"video/webm"});this._chunks=[],e(t)},this._recorder.stop()})}get isRecording(){var e;return((e=this._recorder)==null?void 0:e.state)==="recording"}async stopAndDownload(e="theatre-export.webm"){const t=await this.stop(),n=URL.createObjectURL(t),i=document.createElement("a");i.href=n,i.download=e,i.click(),URL.revokeObjectURL(n)}}async function CD(){const r=await fetch("/api/character/scenes/");if(!r.ok)throw new Error(`Scene list error: ${r.status}`);return(await r.json()).scenes||[]}async function DD(r){const e=await fetch(`/api/character/scene/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Scene load error: ${e.status}`);return e.json()}async function ID(r,e){const t=await fetch("/api/character/scene/save/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:r,data:e})});if(!t.ok){const n=await t.json().catch(()=>({}));throw new Error(n.error||`Scene save error: ${t.status}`)}return t.json()}async function LD(){const r=await fetch("/api/character/models/");if(!r.ok)throw new Error(`Model list error: ${r.status}`);return(await r.json()).presets||[]}async function lg(r){const e=await fetch(`/api/character/model/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Model load error: ${e.status}`);return e.json()}async function FD(){const r=await fetch("/api/character/animations/");if(!r.ok)throw new Error(`Animation list error: ${r.status}`);return(await r.json()).categories||{}}async function ND(r,e){const t=`/api/character/bvh/${encodeURIComponent(r)}/${encodeURIComponent(e)}/`,n=await fetch(t);if(!n.ok)throw new Error(`BVH load error: ${n.status}`);return n.text()}const fh={ballet_stage:{name:"Ballet Stage",description:"Warme Spotlights, theatralisch dunkel",camera:{position:{x:0,y:1.6,z:5},fov:35},lights:{spotLeft:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:-3,y:6,z:3}},spotRight:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:3,y:6,z:3}},backLight:{intensity:25,color:{r:.4,g:.267,b:.667},position:{x:0,y:5,z:-4}}}},studio_bright:{name:"Studio Bright",description:"Helle, gleichmäßige Beleuchtung für Details",camera:{position:{x:0,y:1.6,z:4},fov:40},lights:{spotLeft:{intensity:80,color:{r:1,g:1,b:1},position:{x:-2,y:5,z:4}},spotRight:{intensity:80,color:{r:1,g:1,b:1},position:{x:2,y:5,z:4}},backLight:{intensity:30,color:{r:.9,g:.95,b:1},position:{x:0,y:4,z:-3}}}},cinematic_moody:{name:"Cinematic Moody",description:"Dramatisches Film-noir-Licht, starke Schatten",camera:{position:{x:2,y:1.4,z:4},fov:28},lights:{spotLeft:{intensity:15,color:{r:1,g:.8,b:.6},position:{x:-4,y:7,z:2}},spotRight:{intensity:2,color:{r:.6,g:.7,b:.9},position:{x:4,y:3,z:3}},backLight:{intensity:10,color:{r:.3,g:.5,b:1},position:{x:1,y:6,z:-5}}}},fashion_show:{name:"Fashion Show",description:"Laufsteg-Beleuchtung, kühles Weiß von oben",camera:{position:{x:0,y:1.2,z:6},fov:50},lights:{spotLeft:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:-2,y:8,z:2}},spotRight:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:2,y:8,z:2}},backLight:{intensity:5,color:{r:1,g:1,b:1},position:{x:0,y:3,z:-2}}}},sunset_warm:{name:"Sunset Warm",description:"Goldene Stunde, warmes Orange-Gold",camera:{position:{x:-1,y:1.5,z:4.5},fov:42},lights:{spotLeft:{intensity:14,color:{r:1,g:.7,b:.4},position:{x:-5,y:4,z:3}},spotRight:{intensity:6,color:{r:1,g:.85,b:.7},position:{x:3,y:5,z:2}},backLight:{intensity:8,color:{r:.8,g:.4,b:.6},position:{x:2,y:5,z:-4}}}}};function ph(r,e,t,n){console.log(`[Preset] Applying: ${r.name}`),e.position.set(r.camera.position.x,r.camera.position.y,r.camera.position.z),e.fov=r.camera.fov,e.updateProjectionMatrix(),n&&(n.target.set(0,.9,0),n.update()),mh(t.spotLeft,r.lights.spotLeft),mh(t.spotRight,r.lights.spotRight),mh(t.backLight,r.lights.backLight),console.log(`✓ Preset "${r.name}" applied (direct Three.js)`)}function mh(r,e){r&&(r.intensity=e.intensity,r.color.setRGB(e.color.r,e.color.g,e.color.b),r.position.set(e.position.x,e.position.y,e.position.z))}const OD={Hips:"DEF-spine",Spine:"DEF-spine.001",Spine1:"DEF-spine.003",Neck:null,Neck1:"DEF-spine.004",Head:"DEF-spine.006",LeftShoulder:"DEF-shoulder.L",LeftArm:"DEF-upper_arm.L",LeftForeArm:"DEF-forearm.L",LeftHand:"DEF-hand.L",RightShoulder:"DEF-shoulder.R",RightArm:"DEF-upper_arm.R",RightForeArm:"DEF-forearm.R",RightHand:"DEF-hand.R",LeftUpLeg:"DEF-thigh.L",LeftLeg:"DEF-shin.L",LeftFoot:"DEF-foot.L",LeftToeBase:"DEF-toe.L",RightUpLeg:"DEF-thigh.R",RightLeg:"DEF-shin.R",RightFoot:"DEF-foot.R",RightToeBase:"DEF-toe.R",LHipJoint:null,RHipJoint:null,LowerBack:null,LeftFingerBase:null,RightFingerBase:null,LThumb:null,RThumb:null},UD={Hips:"DEF-spine",Spine:"DEF-spine.001",Spine1:"DEF-spine.002",Spine2:"DEF-spine.003",Neck:null,Neck1:"DEF-spine.004",Head:"DEF-spine.006",LeftShoulder:"DEF-shoulder.L",LeftArm:"DEF-upper_arm.L",LeftForeArm:"DEF-forearm.L",LeftHand:"DEF-hand.L",RightShoulder:"DEF-shoulder.R",RightArm:"DEF-upper_arm.R",RightForeArm:"DEF-forearm.R",RightHand:"DEF-hand.R",LeftUpLeg:"DEF-thigh.L",LeftLeg:"DEF-shin.L",LeftFoot:"DEF-foot.L",LeftToeBase:"DEF-toe.L",RightUpLeg:"DEF-thigh.R",RightLeg:"DEF-shin.R",RightFoot:"DEF-foot.R",RightToeBase:"DEF-toe.R",LeftHandThumb1:"DEF-thumb.01.L",LeftHandThumb2:"DEF-thumb.02.L",LeftHandThumb3:"DEF-thumb.03.L",LeftHandIndex1:"DEF-f_index.01.L",LeftHandIndex2:"DEF-f_index.02.L",LeftHandIndex3:"DEF-f_index.03.L",LeftHandMiddle1:"DEF-f_middle.01.L",LeftHandMiddle2:"DEF-f_middle.02.L",LeftHandMiddle3:"DEF-f_middle.03.L",LeftHandRing1:"DEF-f_ring.01.L",LeftHandRing2:"DEF-f_ring.02.L",LeftHandRing3:"DEF-f_ring.03.L",LeftHandPinky1:"DEF-f_pinky.01.L",LeftHandPinky2:"DEF-f_pinky.02.L",LeftHandPinky3:"DEF-f_pinky.03.L",RightHandThumb1:"DEF-thumb.01.R",RightHandThumb2:"DEF-thumb.02.R",RightHandThumb3:"DEF-thumb.03.R",RightHandIndex1:"DEF-f_index.01.R",RightHandIndex2:"DEF-f_index.02.R",RightHandIndex3:"DEF-f_index.03.R",RightHandMiddle1:"DEF-f_middle.01.R",RightHandMiddle2:"DEF-f_middle.02.R",RightHandMiddle3:"DEF-f_middle.03.R",RightHandRing1:"DEF-f_ring.01.R",RightHandRing2:"DEF-f_ring.02.R",RightHandRing3:"DEF-f_ring.03.R",RightHandPinky1:"DEF-f_pinky.01.R",RightHandPinky2:"DEF-f_pinky.02.R",RightHandPinky3:"DEF-f_pinky.03.R"},BD={hip:"DEF-spine",abdomen:"DEF-spine.001",chest:"DEF-spine.003",neck1:"DEF-spine.004",head:"DEF-spine.006",lcollar:"DEF-shoulder.L",rcollar:"DEF-shoulder.R",lshoulder:"DEF-upper_arm.L",rshoulder:"DEF-upper_arm.R",lelbow:"DEF-forearm.L",relbow:"DEF-forearm.R",lhand:"DEF-hand.L",rhand:"DEF-hand.R",lhip:"DEF-thigh.L",rhip:"DEF-thigh.R",lknee:"DEF-shin.L",rknee:"DEF-shin.R",lfoot:"DEF-foot.L",rfoot:"DEF-foot.R","toe1-1.l":"DEF-toe.L","toe1-1.r":"DEF-toe.R",lCollar:"DEF-shoulder.L",rCollar:"DEF-shoulder.R",lShldr:"DEF-upper_arm.L",rShldr:"DEF-upper_arm.R",lForeArm:"DEF-forearm.L",rForeArm:"DEF-forearm.R",lHand:"DEF-hand.L",rHand:"DEF-hand.R",lThigh:"DEF-thigh.L",rThigh:"DEF-thigh.R",lShin:"DEF-shin.L",rShin:"DEF-shin.R",lFoot:"DEF-foot.L",rFoot:"DEF-foot.R",lButtock:null,rButtock:null,"toe1-1.L":"DEF-toe.L","toe1-1.R":"DEF-toe.R",lthumb:"DEF-thumb.01.L","finger1-2.l":"DEF-thumb.02.L","finger1-3.l":"DEF-thumb.03.L","finger2-1.l":"DEF-f_index.01.L","finger2-2.l":"DEF-f_index.02.L","finger2-3.l":"DEF-f_index.03.L","finger3-1.l":"DEF-f_middle.01.L","finger3-2.l":"DEF-f_middle.02.L","finger3-3.l":"DEF-f_middle.03.L","finger4-1.l":"DEF-f_ring.01.L","finger4-2.l":"DEF-f_ring.02.L","finger4-3.l":"DEF-f_ring.03.L","finger5-1.l":"DEF-f_pinky.01.L","finger5-2.l":"DEF-f_pinky.02.L","finger5-3.l":"DEF-f_pinky.03.L",rthumb:"DEF-thumb.01.R","finger1-2.r":"DEF-thumb.02.R","finger1-3.r":"DEF-thumb.03.R","finger2-1.r":"DEF-f_index.01.R","finger2-2.r":"DEF-f_index.02.R","finger2-3.r":"DEF-f_index.03.R","finger3-1.r":"DEF-f_middle.01.R","finger3-2.r":"DEF-f_middle.02.R","finger3-3.r":"DEF-f_middle.03.R","finger4-1.r":"DEF-f_ring.01.R","finger4-2.r":"DEF-f_ring.02.R","finger4-3.r":"DEF-f_ring.03.R","finger5-1.r":"DEF-f_pinky.01.R","finger5-2.r":"DEF-f_pinky.02.R","finger5-3.r":"DEF-f_pinky.03.R","metacarpal1.l":"DEF-palm.01.L","metacarpal2.l":"DEF-palm.02.L","metacarpal3.l":"DEF-palm.03.L","metacarpal4.l":"DEF-palm.04.L","metacarpal1.r":"DEF-palm.01.R","metacarpal2.r":"DEF-palm.02.R","metacarpal3.r":"DEF-palm.03.R","metacarpal4.r":"DEF-palm.04.R",jaw:"DEF-jaw",tongue01:"DEF-tongue",tongue02:"DEF-tongue.001",tongue03:"DEF-tongue.002","eye.l":"MCH-eye.L","eye.r":"MCH-eye.R","oris04.l":"DEF-lip.T.L","oris04.r":"DEF-lip.T.R","oris03.l":"DEF-lip.T.L.001","oris03.r":"DEF-lip.T.R.001","oris06.l":"DEF-lip.B.L","oris06.r":"DEF-lip.B.R","oris07.l":"DEF-lip.B.L.001","oris07.r":"DEF-lip.B.R.001","orbicularis03.l":"DEF-lid.T.L","orbicularis03.r":"DEF-lid.T.R","orbicularis04.l":"DEF-lid.B.L","orbicularis04.r":"DEF-lid.B.R"},kD={Pelvis:"DEF-spine",Spine1:"DEF-spine.001",Spine2:"DEF-spine.002",Spine3:"DEF-spine.003",Neck:"DEF-spine.004",Head:"DEF-spine.006",Left_collar:"DEF-shoulder.L",Left_shoulder:"DEF-upper_arm.L",Left_elbow:"DEF-forearm.L",Left_wrist:"DEF-hand.L",Left_palm:null,Right_collar:"DEF-shoulder.R",Right_shoulder:"DEF-upper_arm.R",Right_elbow:"DEF-forearm.R",Right_wrist:"DEF-hand.R",Right_palm:null,Left_hip:"DEF-thigh.L",Left_knee:"DEF-shin.L",Left_ankle:"DEF-foot.L",Left_foot:"DEF-toe.L",Right_hip:"DEF-thigh.R",Right_knee:"DEF-shin.R",Right_ankle:"DEF-foot.R",Right_foot:"DEF-toe.R"},zD={hip:"DEF-spine",abdomen:"DEF-spine.001",chest:"DEF-spine.003",neck:null,neck1:"DEF-spine.004",head:"DEF-spine.006",lCollar:"DEF-shoulder.L",rCollar:"DEF-shoulder.R",lShldr:"DEF-upper_arm.L",rShldr:"DEF-upper_arm.R",lForeArm:"DEF-forearm.L",rForeArm:"DEF-forearm.R",lHand:"DEF-hand.L",rHand:"DEF-hand.R",lButtock:null,rButtock:null,lThigh:"DEF-thigh.L",rThigh:"DEF-thigh.R",lShin:"DEF-shin.L",rShin:"DEF-shin.R",lFoot:"DEF-foot.L",rFoot:"DEF-foot.R","toe1-1.L":"DEF-toe.L","toe1-1.R":"DEF-toe.R",lthumb:"DEF-thumb.01.L","finger1-2.l":"DEF-thumb.02.L","finger1-3.l":"DEF-thumb.03.L","finger2-1.l":"DEF-f_index.01.L","finger2-2.l":"DEF-f_index.02.L","finger2-3.l":"DEF-f_index.03.L","finger3-1.l":"DEF-f_middle.01.L","finger3-2.l":"DEF-f_middle.02.L","finger3-3.l":"DEF-f_middle.03.L","finger4-1.l":"DEF-f_ring.01.L","finger4-2.l":"DEF-f_ring.02.L","finger4-3.l":"DEF-f_ring.03.L","finger5-1.l":"DEF-f_pinky.01.L","finger5-2.l":"DEF-f_pinky.02.L","finger5-3.l":"DEF-f_pinky.03.L",rthumb:"DEF-thumb.01.R","finger1-2.r":"DEF-thumb.02.R","finger1-3.r":"DEF-thumb.03.R","finger2-1.r":"DEF-f_index.01.R","finger2-2.r":"DEF-f_index.02.R","finger2-3.r":"DEF-f_index.03.R","finger3-1.r":"DEF-f_middle.01.R","finger3-2.r":"DEF-f_middle.02.R","finger3-3.r":"DEF-f_middle.03.R","finger4-1.r":"DEF-f_ring.01.R","finger4-2.r":"DEF-f_ring.02.R","finger4-3.r":"DEF-f_ring.03.R","finger5-1.r":"DEF-f_pinky.01.R","finger5-2.r":"DEF-f_pinky.02.R","finger5-3.r":"DEF-f_pinky.03.R","metacarpal1.l":"DEF-palm.01.L","metacarpal2.l":"DEF-palm.02.L","metacarpal3.l":"DEF-palm.03.L","metacarpal4.l":"DEF-palm.04.L","metacarpal1.r":"DEF-palm.01.R","metacarpal2.r":"DEF-palm.02.R","metacarpal3.r":"DEF-palm.03.R","metacarpal4.r":"DEF-palm.04.R",jaw:"DEF-jaw",tongue01:"DEF-tongue",tongue02:"DEF-tongue.001",tongue03:"DEF-tongue.002","eye.l":"MCH-eye.L","eye.r":"MCH-eye.R","oris04.l":"DEF-lip.T.L","oris04.r":"DEF-lip.T.R","oris03.l":"DEF-lip.T.L.001","oris03.r":"DEF-lip.T.R.001","oris06.l":"DEF-lip.B.L","oris06.r":"DEF-lip.B.R","oris07.l":"DEF-lip.B.L.001","oris07.r":"DEF-lip.B.R.001","orbicularis03.l":"DEF-lid.T.L","orbicularis03.r":"DEF-lid.T.R","orbicularis04.l":"DEF-lid.B.L","orbicularis04.r":"DEF-lid.B.R"},HD={Hips:"DEF-spine",Spine:"DEF-spine.001",Chest:"DEF-spine.003",Neck:"DEF-spine.004",Head:"DEF-spine.006",Shoulder_L:"DEF-shoulder.L",UpperArm_L:"DEF-upper_arm.L",LowerArm_L:"DEF-forearm.L",Hand_L:"DEF-hand.L",Shoulder_R:"DEF-shoulder.R",UpperArm_R:"DEF-upper_arm.R",LowerArm_R:"DEF-forearm.R",Hand_R:"DEF-hand.R",UpperLeg_L:"DEF-thigh.L",LowerLeg_L:"DEF-shin.L",Foot_L:"DEF-foot.L",Toes_L:"DEF-toe.L",UpperLeg_R:"DEF-thigh.R",LowerLeg_R:"DEF-shin.R",Foot_R:"DEF-foot.R",Toes_R:"DEF-toe.R",joint_Root:null};function VD(r,e,t,n={}){const i=r.skeleton.bones,s=r.clip,a=t==="CMU"?OD:t==="MIXAMO"?UD:t==="BANDAI"?HD:t==="AIST"?kD:t==="OPENPOSE"?zD:BD;e.rootBone.updateWorldMatrix(!0,!0);const c={},u={},h=new Map;for(const[fe,Me]of Object.entries(e.boneByName))h.set(Me,fe);for(const[fe,Me]of Object.entries(e.boneByName)){c[fe]=new Mt,Me.getWorldQuaternion(c[fe]);const Fe=h.get(Me.parent);Fe&&c[Fe]?u[fe]=c[Fe]:Me.parent&&(u[fe]=new Mt,Me.parent.getWorldQuaternion(u[fe]))}const f={};for(const fe of i)f[fe.name]=fe;const p=i[0],m=[],g={};function x(fe){m.push(fe.name);for(const Me of fe.children)Me.isBone&&(g[Me.name]=fe.name,x(Me))}x(p);const E={};for(const[fe,Me]of Object.entries(a))Me&&f[fe]&&e.boneByName[Me]&&(E[Me]=fe);const v=new Set(Object.keys(E));console.log(`[RETARGET] ${v.size} bones mapped`);const _={},R={};for(const fe of s.tracks){const Me=fe.name.lastIndexOf(".");if(Me<0)continue;const Fe=fe.name.substring(0,Me),H=fe.name.substring(Me+1);H==="quaternion"&&(_[Fe]=fe),H==="position"&&(R[Fe]=fe)}const w=new Ti,S=new Mt,z=new U;function O(fe,Me,Fe){z.copy(fe.position).applyQuaternion(Me);const H=Fe.clone().add(z);w.expandByPoint(H),S.copy(Me).multiply(fe.quaternion);for(const nt of fe.children)nt.isBone&&O(nt,S.clone(),H)}O(p,new Mt,new U);const N=Math.max(w.max.y-w.min.y,.01);let V=1.68;if(n.bodyMesh){const fe=new Ti().setFromObject(n.bodyMesh);fe.isEmpty()||(V=fe.max.y-fe.min.y)}const D=V/N,A={};for(const[fe,Me]of Object.entries(e.boneByName))u[fe]?A[fe]=u[fe].clone().invert().multiply(c[fe]):A[fe]=c[fe].clone();const k={},J=t==="BANDAI";if(J){const fe=new Mt;for(const Me of m){const Fe=_[Me];Fe?fe.set(Fe.values[0],Fe.values[1],Fe.values[2],Fe.values[3]):fe.set(0,0,0,1);const H=g[Me];H&&k[H]?k[Me]=k[H].clone().multiply(fe):k[Me]=fe.clone()}}const ee=new U(0,0,-1),re={},le=Object.values(a).find(fe=>fe&&e.boneByName[fe]),Y=new Set;t==="AIST"&&(Y.add("DEF-foot.L"),Y.add("DEF-foot.R"),Y.add("DEF-toe.L"),Y.add("DEF-toe.R"),Y.add("DEF-spine.004"),Y.add("DEF-spine.006")),t==="MOCAPNET"&&(Y.add("DEF-foot.L"),Y.add("DEF-foot.R"),Y.add("DEF-toe.L"),Y.add("DEF-toe.R"),Y.add("DEF-jaw"),Y.add("DEF-spine.004"),Y.add("DEF-spine.006")),t==="OPENPOSE"&&(Y.add("DEF-foot.L"),Y.add("DEF-foot.R"),Y.add("DEF-toe.L"),Y.add("DEF-toe.R"),Y.add("DEF-jaw"),Y.add("DEF-spine.004"),Y.add("DEF-spine.006"),Y.add("DEF-shoulder.L"),Y.add("DEF-shoulder.R"));for(const[fe,Me]of Object.entries(E)){if(fe===le||Y.has(fe)){re[fe]=c[fe].clone();continue}const Fe=ee.clone().applyQuaternion(c[fe]).normalize(),H=f[Me];let nt=null,Je=-1/0;for(const $e of H.children)if($e.isBone&&$e.position.lengthSq()>1e-10){let Oe;J&&k[Me]?Oe=$e.position.clone().applyQuaternion(k[Me]).normalize():Oe=$e.position.clone().normalize();const at=Oe.dot(Fe);at>Je&&(Je=at,nt=Oe)}if(!nt&&H.position.lengthSq()>1e-10)if(J){const $e=g[Me];$e&&k[$e]?nt=H.position.clone().applyQuaternion(k[$e]).normalize():nt=H.position.clone().normalize()}else nt=H.position.clone().normalize();if(!nt||nt.lengthSq()<1e-10)re[fe]=c[fe].clone();else{const $e=new Mt().setFromUnitVectors(Fe,nt);re[fe]=$e.multiply(c[fe])}}const de=Object.keys(e.boneByName).sort((fe,Me)=>{let Fe=0,H=e.boneByName[fe];for(;H.parent;)Fe++,H=H.parent;let nt=0,Je=e.boneByName[Me];for(;Je.parent;)nt++,Je=Je.parent;return Fe-nt}),ne=Object.values(_)[0];if(!ne)return new oo("retargeted",0,[]);const ye=ne.times,Te=ye.length,ze={};for(const fe of v)ze[fe]=new Float32Array(Te*4);const We=new Mt,xt=new Mt,ue={},me={};let De=null;if(n.footCorrection){De={};const fe=new Mt,Me=new U,Fe=180/Math.PI,H=15,nt=1.5;for(const Je of["DEF-foot.L","DEF-foot.R"]){const $e=E[Je];if(!$e)continue;const Oe=[];let at=$e;for(;at;)Oe.unshift(at),at=g[at];const Be=new Float32Array(Te);let L=0,T=0;for(let $=0;$<Te;$++){const he=$*4;let ge=new Mt;for(const Ce of Oe){const we=_[Ce];we?fe.set(we.values[he],we.values[he+1],we.values[he+2],we.values[he+3]):fe.set(0,0,0,1),ge.multiply(fe)}Me.set(0,0,-1).applyQuaternion(ge);const ce=Math.asin(Math.max(-1,Math.min(1,-Me.y)))*Fe;if(ce>T&&(T=ce),ce>H){const Ce=Math.min(90,ce+(ce-H)*nt),we=90-ce;Be[$]=we>.1?Math.min((Ce-ce)/we,1):0}Be[$]>L&&(L=Be[$])}De[Je]=Be,console.log(`[FOOT-CORRECTION] ${Je}: maxAngle=${T.toFixed(1)}, thresh=${H}, boost=${nt}x, maxCorr=${L.toFixed(2)}`)}Object.keys(De).length===0&&(De=null)}for(let fe=0;fe<Te;fe++){const Me=fe*4;for(const Fe of m){const H=_[Fe];H?We.set(H.values[Me],H.values[Me+1],H.values[Me+2],H.values[Me+3]):We.set(0,0,0,1);const nt=g[Fe];nt&&me[nt]?me[Fe]=me[nt].clone().multiply(We):me[Fe]=We.clone()}for(const Fe of de){const H=e.boneByName[Fe],nt=h.get(H.parent),Je=nt&&ue[nt]?ue[nt]:new Mt;if(v.has(Fe)){const $e=E[Fe];if(J){const at=me[$e],Be=k[$e];at&&Be?(xt.copy(at).multiply(Be.clone().invert()).multiply(re[Fe]).normalize(),We.copy(Je).invert().multiply(xt).normalize()):We.copy(A[Fe]||new Mt)}else{const at=me[$e];at?(xt.copy(at).multiply(re[Fe]).normalize(),We.copy(Je).invert().multiply(xt).normalize()):We.copy(A[Fe]||new Mt)}if(De&&De[Fe]){const at=De[Fe][fe];if(at>.01){const Be=Je.clone().multiply(We),L=new U(0,0,-1).applyQuaternion(Be).normalize(),T=new U(0,-1,0),he=new Mt().setFromUnitVectors(L,T).multiply(Be),ge=Je.clone().invert().multiply(he).normalize();We.slerp(ge,at)}}const Oe=ze[Fe];Oe[Me]=We.x,Oe[Me+1]=We.y,Oe[Me+2]=We.z,Oe[Me+3]=We.w,ue[Fe]=Je.clone().multiply(We)}else ue[Fe]=Je.clone().multiply(A[Fe]||new Mt)}}const Se=[];for(const fe of v){const Me=e.boneByName[fe];Se.push(new wr(`${Me.name}.quaternion`,ye,ze[fe]))}const et=i[0].name;let it=a[et];const Qe=R[et];if(!it&&Qe){for(const fe of i[0].children)if(fe.isBone&&a[fe.name]){it=a[fe.name];break}}if(it&&Qe){const fe=e.boneByName[it];if(fe){const Me=new U(Qe.values[0],Qe.values[1],Qe.values[2]),Fe=fe.position.clone(),H=new Float32Array(Qe.values.length);for(let nt=0;nt<Qe.values.length;nt+=3)H[nt]=Fe.x+(Qe.values[nt]-Me.x)*D,H[nt+1]=Fe.y+(Qe.values[nt+1]-Me.y)*D,H[nt+2]=Fe.z+(Qe.values[nt+2]-Me.z)*D;Se.push(new Ar(`${fe.name}.position`,Qe.times,H))}}return console.log(`[RETARGET] ${Se.length} tracks, ${Te} frames`),new oo("retargeted",s.duration,Se)}window.addEventListener("DOMContentLoaded",()=>{const r=document.getElementById("theatre-canvas");if(!r){console.error("theatre-canvas not found");return}const{scene:e,camera:t,renderer:n,controls:i,lights:s,lightIcons:a,transformControls:c}=OC(r);window.scene=e,window.lights=s,window.lightIcons=a,window.transformControls=c,window.activeMixer=null,window.isPlaying=!1,window.currentTime=0,window.animDuration=1;const u=new Qg,h=new ht;let f=null,p=null;const m=[];let g=null,x=null,E=null;async function v(){return E||(E=(async()=>{var F;try{const[W,ie]=await Promise.all([fetch("/api/character/def-skeleton/"),fetch("/api/character/skin-weights/")]);W.ok&&(g=await W.json()),ie.ok&&(x=await ie.json()),console.log("✓ Loaded skeleton and skin weights:",((F=g==null?void 0:g.bones)==null?void 0:F.length)||0,"bones");for(const ve of m)ve.userData.isSkinnedMesh||_(ve)}catch(W){console.warn("Failed to load skeleton/weights:",W)}})(),E)}v();function _(F){g&&x&&!F.userData.isSkinnedMesh&&setTimeout(()=>{try{w(F,e),console.log("✓ Auto-converted to SkinnedMesh:",F.userData.presetName)}catch(W){console.warn("Auto-convert failed:",W)}},100)}function R(F,W,ie,ve){const _e=new n_().parse(F);if(!g)throw console.error("DEF skeleton data not loaded - cannot retarget animation"),new Error("Skeleton data not loaded");if(!W||!W.skeleton)throw console.error("SkinnedMesh has no skeleton"),new Error("SkinnedMesh not properly initialized");if(!W.skeleton.bones||W.skeleton.bones.length===0)throw console.error("SkinnedMesh skeleton has no bones"),new Error("Skeleton has no bones");const He={skeleton:W.skeleton,rootBone:W.skeleton.bones[0],bones:W.skeleton.bones,boneByName:{}};for(const ft of W.skeleton.bones)He.boneByName[ft.name]=ft;const ot=VD(_e,He,ve||_e.clip.name);if(!ot||ot.tracks.length===0)throw console.error("Retargeting failed - no tracks generated"),new Error("Retargeting failed");const St=new Zg(W),Nt=St.clipAction(ot);Nt.setLoop(gd),Nt.play(),Nt.paused=!0;const Pt=ot.duration||1;return console.log("✓ BVH animation retargeted and loaded on SkinnedMesh:",ve,Pt+"s",ot.tracks.length,"tracks"),{mixer:St,action:Nt,duration:Pt}}function w(F,W){if(!g||!x)return console.warn("Cannot convert to SkinnedMesh: skeleton/weights not loaded"),null;if(F.userData.isSkinnedMesh)return console.log("Already a SkinnedMesh"),F.userData.skinnedMesh;const ie=F.children.find(Ct=>Ct.isMesh);if(!ie)return console.warn("No mesh found in character group"),null;console.log("Converting to SkinnedMesh...");const ve=ie.geometry.clone(),je=ve.attributes.position.count,_e=new Float32Array(je*4),He=new Float32Array(je*4);for(let Ct=0;Ct<je;Ct++){const Ht=x.indices[Ct]||[0,0,0,0],In=x.weights[Ct]||[1,0,0,0];_e[Ct*4+0]=Ht[0],_e[Ct*4+1]=Ht[1],_e[Ct*4+2]=Ht[2],_e[Ct*4+3]=Ht[3],He[Ct*4+0]=In[0],He[Ct*4+1]=In[1],He[Ct*4+2]=In[2],He[Ct*4+3]=In[3]}ve.setAttribute("skinIndex",new Zt(_e,4)),ve.setAttribute("skinWeight",new Zt(He,4));const ot=[],St=[];for(const Ct of g.bones){const Ht=new Vc;Ht.name=Ct.name,Ht.position.fromArray(Ct.position),Ht.quaternion.fromArray(Ct.quaternion),Ht.scale.fromArray(Ct.scale),ot.push(Ht);const In=new pt;Ct.inverse&&In.fromArray(Ct.inverse),St.push(In)}for(let Ct=0;Ct<g.bones.length;Ct++){const Ht=g.bones[Ct].parent;Ht>=0&&ot[Ht].add(ot[Ct])}const Nt=new ra(ot,St),Pt=ot[0],ft=ie.material,ct=new Gg(ve,ft);ct.castShadow=!0,ct.receiveShadow=!0,ct.add(Pt),ct.bind(Nt);const Qt=ie.position.clone(),vt=ie.rotation.clone(),Xt=ie.scale.clone();F.remove(ie),ct.position.copy(Qt),ct.rotation.copy(vt),ct.scale.copy(Xt),F.add(ct);const cn=new Jg(Pt);return cn.visible=!1,cn.material.linewidth=2,cn.userData.isRig=!0,W.add(cn),F.userData.isSkinnedMesh=!0,F.userData.skinnedMesh=ct,F.userData.skeleton=Nt,F.userData.rootBone=Pt,F.userData.skeletonHelper=cn,console.log("✓ Converted to SkinnedMesh with",ot.length,"bones"),ct}r.addEventListener("click",F=>{const W=r.getBoundingClientRect();h.x=(F.clientX-W.left)/W.width*2-1,h.y=-((F.clientY-W.top)/W.height)*2+1,u.setFromCamera(h,t);const ie=[a.spotLeftIcon,a.spotRightIcon,a.backLightIcon],ve=u.intersectObjects(ie,!0);if(ve.length>0){let _e=ve[0].object;for(;_e.parent&&!_e.userData.light;)_e=_e.parent;if(_e.userData.light){f=_e,p=null,c.attach(_e),console.log("✓ Licht ausgewählt:",_e.userData.light),Ve(_e.userData.light);return}}const je=u.intersectObjects(m,!0);if(je.length>0){const _e=je[0].object;if(_e.userData.isGarment){p=null,f=null,c.attach(_e),console.log("✓ Garment ausgewählt:",_e.name),bt(_e);return}let He=_e;for(;He.parent&&!He.userData.isCharacter;)He=He.parent;if(He.userData.isCharacter){p=He,f=null,c.attach(He),console.log("✓ Character ausgewählt:",He.userData.presetName),mt(He);return}}c.detach(),f=null,p=null,ae()});const{sheet:S}=BC();kC(S,t),Ec(S,"Spot Left",s.spotLeft),Ec(S,"Spot Right",s.spotRight),Ec(S,"Back Light",s.backLight);const z=new PD(n.domElement);let O=null,N=null;const V=new eC;document.querySelectorAll(".menu-item").forEach(F=>{const W=F.querySelector(".menu-dropdown");W&&(F.addEventListener("click",ie=>{ie.stopPropagation(),document.querySelectorAll(".menu-item").forEach(ve=>ve.classList.remove("active")),F.classList.toggle("active")}),W.addEventListener("click",ie=>{ie.stopPropagation()}))}),document.addEventListener("click",()=>{document.querySelectorAll(".menu-item").forEach(F=>F.classList.remove("active"))}),document.querySelectorAll("[data-preset]").forEach(F=>{F.addEventListener("click",()=>{const W=F.getAttribute("data-preset"),ie=fh[W];ie?(ph(ie,t,s,i),console.log("✓ Applied preset:",ie.name),document.querySelectorAll(".menu-item").forEach(ve=>ve.classList.remove("active"))):console.error("Preset not found:",W)})}),document.querySelectorAll(".panel-tab").forEach(F=>{F.addEventListener("click",()=>{const W=F.getAttribute("data-tab");document.querySelectorAll(".panel-tab").forEach(ve=>ve.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(ve=>ve.classList.remove("active")),F.classList.add("active");const ie=document.getElementById(W);ie&&ie.classList.add("active")})});const D=document.getElementById("btn-translate-mode"),A=document.getElementById("btn-rotate-mode"),k=document.getElementById("btn-toggle-lights");D&&D.addEventListener("click",()=>{c.setMode("translate"),D.classList.add("active"),A.classList.remove("active")}),A&&A.addEventListener("click",()=>{c.setMode("rotate"),A.classList.add("active"),D.classList.remove("active")});let J=!0;k&&k.addEventListener("click",()=>{J=!J,Object.values(a).forEach(F=>{F.visible=J}),J?k.classList.add("active"):k.classList.remove("active")});const ee=document.getElementById("btn-toggle-model");let re=!0;ee&&ee.addEventListener("click",()=>{re=!re,e.traverse(F=>{F.isMesh&&!F.userData.isGarment&&!F.userData.isHair&&!F.userData.isRig&&(F.visible=re)}),ee.classList.toggle("active",re)});const le=document.getElementById("btn-toggle-clothes");let Y=!0;le&&le.addEventListener("click",()=>{Y=!Y,e.traverse(F=>{F.isMesh&&(F.userData.isGarment||F.userData.isHair)&&(F.visible=Y)}),le.classList.toggle("active",Y)});const de=document.getElementById("btn-toggle-rig");let ne=!1;de&&de.addEventListener("click",()=>{ne=!ne,e.traverse(F=>{(F.isSkeletonHelper||F.userData.isRig)&&(F.visible=ne)}),de.classList.toggle("active",ne)});const ye=document.getElementById("btn-play-animation");ye&&ye.addEventListener("click",()=>{const F=document.getElementById("btnPlayPause");F&&F.click()});function Te(F){const W=document.getElementById(F);W&&(W.style.display="flex")}function ze(F){const W=document.getElementById(F);W&&(W.style.display="none")}document.querySelectorAll("[data-close-modal]").forEach(F=>{F.addEventListener("click",()=>{var W;(W=F.closest(".theatre-modal-overlay"))==null||W.style.removeProperty("display")})}),document.querySelectorAll(".theatre-modal-overlay").forEach(F=>{F.addEventListener("click",W=>{W.target===F&&F.style.removeProperty("display")})});const We=document.getElementById("menu-scene-load");We&&We.addEventListener("click",async()=>{const F=document.getElementById("scene-list-body");F.innerHTML='<div class="loading-msg">Lade Scenes...</div>',Te("modal-scene-load");try{const W=await CD();if(W.length===0){F.innerHTML='<div class="loading-msg">Keine Scenes gefunden.</div>';return}F.innerHTML="";for(const ie of W){const ve=document.createElement("div");ve.style.cssText="padding:10px 14px;border-radius:6px;cursor:pointer;color:#ccc;font-size:0.85rem;",ve.innerHTML=`<span>${ie.label||ie.name}</span>`,ve.addEventListener("click",()=>xt(ie.name)),ve.addEventListener("mouseenter",()=>ve.style.background="rgba(124, 92, 191, 0.2)"),ve.addEventListener("mouseleave",()=>ve.style.background=""),F.appendChild(ve)}}catch(W){F.innerHTML=`<div class="loading-msg">Fehler: ${W.message}</div>`}});async function xt(F){ze("modal-scene-load");try{const W=await DD(F);if(console.log("Scene loaded:",F,W),W.characters&&Array.isArray(W.characters))for(const ie of W.characters){const ve=await dh(e,ie,ie.name||F);ve.userData.isCharacter=!0,ve.userData.presetName=ie.name||F,ve.userData.bodyType=ie.body_type||"Unknown",m.push(ve),_(ve)}}catch(W){console.error("Scene load error:",W),alert("Scene laden fehlgeschlagen: "+W.message)}}const ue=document.getElementById("menu-scene-save"),me=document.getElementById("scene-save-btn"),De=document.getElementById("scene-save-name");ue&&ue.addEventListener("click",()=>{Te("modal-scene-save"),De&&(De.value="",De.focus())}),me&&De&&(me.addEventListener("click",async()=>{const F=De.value.trim();if(F){me.disabled=!0,me.textContent="Speichere...";try{const W={camera:{position:t.position.toArray(),fov:t.fov,target:i.target.toArray()},lights:{spotLeft:{position:s.spotLeft.position.toArray(),intensity:s.spotLeft.intensity,color:"#"+s.spotLeft.color.getHexString()},spotRight:{position:s.spotRight.position.toArray(),intensity:s.spotRight.intensity,color:"#"+s.spotRight.color.getHexString()},backLight:{position:s.backLight.position.toArray(),intensity:s.backLight.intensity,color:"#"+s.backLight.color.getHexString()}},characters:[]},ie=await ID(F,W);console.log("Scene saved:",ie),ze("modal-scene-save")}catch(W){console.error("Scene save error:",W),alert("Scene speichern fehlgeschlagen: "+W.message)}me.disabled=!1,me.textContent="Speichern"}}),De.addEventListener("keydown",F=>{F.key==="Enter"&&me.click()}));const Se=document.getElementById("model-list"),et=document.getElementById("menu-model-load");async function it(){try{const F=await LD();if(F.length===0){Se.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Modelle gefunden.</div>';return}Se.innerHTML="";for(const W of F){const ie=document.createElement("div");ie.className="anim-item",ie.textContent=W.label||W.name,ie.addEventListener("click",async()=>{try{const ve=await lg(W.name),je=await dh(e,ve,W.name);je.userData.isCharacter=!0,je.userData.presetName=W.name,je.userData.bodyType=ve.body_type||"Unknown",m.push(je),_(je),console.log("Model loaded:",W.name),document.querySelectorAll("#model-list .anim-item").forEach(_e=>_e.classList.remove("active")),ie.classList.add("active")}catch(ve){console.error("Model load error:",ve),alert("Modell laden fehlgeschlagen: "+ve.message)}}),Se.appendChild(ie)}}catch(F){Se.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${F.message}</div>`}}it(),et&&et.addEventListener("click",()=>{document.querySelectorAll(".panel-tab").forEach(ie=>ie.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(ie=>ie.classList.remove("active"));const F=document.querySelector('[data-tab="tab-models"]'),W=document.getElementById("tab-models");F&&F.classList.add("active"),W&&W.classList.add("active")});const Qe=document.getElementById("anim-tree");async function fe(){try{const F=await FD(),W=Object.keys(F);if(W.length===0){Qe.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden.</div>';return}Qe.innerHTML="";for(const ie of W){const ve=F[ie],je=document.createElement("div");je.className="anim-cat";const _e=document.createElement("div");_e.className="anim-cat-header",_e.innerHTML=`<i class="fas fa-chevron-right"></i> ${ie} (${ve.length})`,_e.addEventListener("click",()=>{je.classList.toggle("open")}),je.appendChild(_e);const He=document.createElement("div");He.className="anim-cat-body";for(const ot of ve){const St=document.createElement("div");St.className="anim-item",St.textContent=ot.name,St.addEventListener("click",async()=>{await Me(ot.category,ot.name),document.querySelectorAll("#anim-tree .anim-item").forEach(Nt=>Nt.classList.remove("active")),St.classList.add("active")}),He.appendChild(St)}je.appendChild(He),Qe.appendChild(je)}}catch(F){Qe.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${F.message}</div>`}}async function Me(F,W){try{const ie=await ND(F,W);let ve=null;p&&(ve=w(p,e));const{mixer:je,action:_e,duration:He}=ve?R(ie,ve,e,`${F}/${W}`):RD(ie,e,`${F}/${W}`);O&&O.stopAllAction(),O=je,N=_e,window.activeMixer=O,Tt(He),ce=!1,Ce=0,we=He,window.isPlaying=!1,window.currentTime=0,window.animDuration=He,Ue(),console.log("Animation loaded:",F,W,He)}catch(ie){console.error("Animation load error:",ie),alert("Animation laden fehlgeschlagen: "+ie.message)}}fe();const Fe=document.getElementById("menu-add-glb"),H=document.getElementById("glb-file-input");Fe&&H&&(Fe.addEventListener("click",()=>H.click()),H.addEventListener("change",async()=>{const F=H.files[0];if(F){try{await ED(F,e)}catch(W){console.error("GLB load error:",W),alert("Fehler beim Laden der GLB-Datei: "+W.message)}H.value=""}})),document.querySelectorAll("[data-preset]").forEach(F=>{F.addEventListener("click",()=>{const W=F.getAttribute("data-preset"),ie=fh[W];ie?(ph(ie,t,s,i),console.log("✓ Applied preset:",ie.name)):console.error("Preset not found:",W)})});const nt=document.getElementById("menu-add-light");let Je=0;nt&&nt.addEventListener("click",()=>{Je++;const F=new $g(16777215,1,15);F.position.set((Math.random()-.5)*6,2+Math.random()*3,(Math.random()-.5)*6),e.add(F);const W=new Pe(new sa(.08,8,8),new pi({color:16776960}));F.add(W),Ec(S,`Light ${Je}`,F)});const $e=document.getElementById("menu-export-video");$e&&$e.addEventListener("click",async()=>{z.isRecording?($e.innerHTML='<i class="fas fa-file-video"></i> Export Video',await z.stopAndDownload()):(z.start(30),$e.innerHTML='<i class="fas fa-stop"></i> Stop Recording')});const Oe=document.getElementById("btnPlayPause"),at=document.getElementById("btnStop"),Be=document.getElementById("btnFrameBack"),L=document.getElementById("btnFrameFwd"),T=document.getElementById("timelineSlider"),$=document.getElementById("timeCurrent"),he=document.getElementById("timeDuration"),ge=document.getElementById("playIcon");let ce=!1,Ce=0,we=1,ke=1;function Tt(F){we=F||1,he.textContent=be(we),T.max=we}function be(F){const W=Math.floor(F/60),ie=Math.floor(F%60);return`${String(W).padStart(2,"0")}:${String(ie).padStart(2,"0")}`}function Ue(){$.textContent=be(Ce),T.value=Ce,ge&&(ge.className=ce?"fas fa-pause":"fas fa-play")}function Ge(F){!O||!N||(Ce=Math.max(0,Math.min(F,we)),N.time=Ce,O.update(0),Ue())}Oe&&Oe.addEventListener("click",()=>{O&&(ce=!ce,window.isPlaying=ce,ce&&N?(N.paused=!1,N.play()):N&&(N.paused=!0),Ue())}),at&&at.addEventListener("click",()=>{O&&(ce=!1,Ce=0,Ge(0),N&&(N.stop(),N.paused=!0),Ue())}),Be&&Be.addEventListener("click",()=>{Ge(Ce-1/30)}),L&&L.addEventListener("click",()=>{Ge(Ce+1/30)}),T&&(T.addEventListener("mousedown",()=>{}),T.addEventListener("mouseup",()=>{}),T.addEventListener("input",()=>{const F=parseFloat(T.value);Ge(F)})),document.querySelectorAll(".speed-btn").forEach(F=>{F.addEventListener("click",()=>{const W=parseFloat(F.getAttribute("data-speed"));ke=W,O&&(O.timeScale=W),document.querySelectorAll(".speed-btn").forEach(ie=>ie.classList.remove("active")),F.classList.add("active")})}),document.addEventListener("keydown",F=>{F.target.tagName!=="INPUT"&&(F.code==="Space"?(F.preventDefault(),Oe&&Oe.click()):F.code==="ArrowLeft"?(F.preventDefault(),Be&&Be.click()):F.code==="ArrowRight"&&(F.preventDefault(),L&&L.click()))});async function st(){try{const F=await fetch("/api/settings/theatre/");if(!F.ok)return;const W=await F.json();if(W.preset){const ie=fh[W.preset];ie&&(ph(ie,t,s,i),console.log("✓ Auto-applied preset:",ie.name))}if(W.model)try{const ie=await lg(W.model),ve=await dh(e,ie,W.model);if(ve.userData.isCharacter=!0,ve.userData.presetName=W.model,ve.userData.bodyType=ie.body_type||"Unknown",m.push(ve),_(ve),console.log("✓ Auto-loaded model:",W.model),W.animation){const[je,_e]=W.animation.split("/");je&&_e&&(await Me(je,_e),console.log("✓ Auto-loaded animation:",W.animation))}}catch(ie){console.warn("Auto-load model/animation failed:",ie)}}catch(F){console.warn("Failed to load Theatre defaults:",F)}}setTimeout(st,500);function Ve(F){document.querySelectorAll(".panel-tab").forEach(Xt=>Xt.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Xt=>Xt.classList.remove("active"));const W=document.querySelector('[data-tab="tab-properties"]'),ie=document.getElementById("tab-properties");W&&W.classList.add("active"),ie&&ie.classList.add("active");const ve=document.getElementById("properties-content");if(!ve)return;const je=F===s.spotLeft?"Spot Left":F===s.spotRight?"Spot Right":F===s.backLight?"Back Light":"Light",_e="#"+F.color.getHexString();ve.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-lightbulb"></i> ${je}
                </h3>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Intensität: <span id="light-intensity-value">${F.intensity.toFixed(1)}</span>
                    </label>
                    <input type="range" id="light-intensity" min="0" max="100" step="1" value="${F.intensity}"
                           style="width:100%;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Farbe
                    </label>
                    <input type="color" id="light-color" value="${_e}"
                           style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);background:var(--bg-primary);cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-pos-x" value="${F.position.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-pos-y" value="${F.position.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-pos-z" value="${F.position.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="light-rot-x" value="${(F.rotation.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-rot-y" value="${(F.rotation.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-rot-z" value="${(F.rotation.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Ziehe das Licht-Icon in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const He=document.getElementById("light-intensity"),ot=document.getElementById("light-intensity-value"),St=document.getElementById("light-color"),Nt=document.getElementById("light-pos-x"),Pt=document.getElementById("light-pos-y"),ft=document.getElementById("light-pos-z");if(He&&(He.oninput=Xt=>{F.intensity=parseFloat(Xt.target.value),ot.textContent=F.intensity.toFixed(1)}),St&&(St.oninput=Xt=>{F.color.setHex(parseInt(Xt.target.value.substring(1),16)),f&&f.children.forEach(cn=>{cn.material&&(cn.material.color.copy(F.color),cn.material.emissive&&cn.material.emissive.copy(F.color))})}),Nt&&Pt&&ft){const Xt=()=>{F.position.set(parseFloat(Nt.value),parseFloat(Pt.value),parseFloat(ft.value)),f&&(f.position.copy(F.position),f.lookAt(F.target.position))};Nt.oninput=Xt,Pt.oninput=Xt,ft.oninput=Xt}const ct=document.getElementById("light-rot-x"),Qt=document.getElementById("light-rot-y"),vt=document.getElementById("light-rot-z");if(ct&&Qt&&vt){const Xt=()=>{F.rotation.set(parseFloat(ct.value)*Math.PI/180,parseFloat(Qt.value)*Math.PI/180,parseFloat(vt.value)*Math.PI/180),f&&f.rotation.copy(F.rotation)};ct.oninput=Xt,Qt.oninput=Xt,vt.oninput=Xt}}function bt(F){document.querySelectorAll(".panel-tab").forEach(Z=>Z.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Z=>Z.classList.remove("active"));const W=document.querySelector('[data-tab="tab-properties"]'),ie=document.getElementById("tab-properties");W&&W.classList.add("active"),ie&&ie.classList.add("active");const ve=document.getElementById("properties-content");if(!ve)return;const je=F.userData.garmentId||F.name||"Garment",_e=F.material,ot="#"+_e.color.getHexString(),St=_e.roughness??.8,Nt=_e.metalness??0,Pt=F.userData.offset||.006,ft=F.userData.stiffness||.8,ct=F.position;ve.innerHTML=`
            <div style="padding:16px;max-height:calc(100vh - 200px);overflow-y:auto;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-tshirt"></i> ${je}
                </h3>

                <!-- Material Properties -->
                <div style="margin-bottom:20px;">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-palette"></i> Material</h4>

                    <div style="margin-bottom:12px;">
                        <label style="display:block;font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">Farbe</label>
                        <input type="color" id="garment-color" value="${ot}"
                               style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Roughness</span>
                            <span id="garment-roughness-value">${St.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-roughness" min="0" max="1" step="0.01" value="${St}" style="width:100%;cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Metalness</span>
                            <span id="garment-metalness-value">${Nt.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-metalness" min="0" max="1" step="0.01" value="${Nt}" style="width:100%;cursor:pointer;" />
                    </div>
                </div>

                <!-- Fit Properties -->
                <div style="margin-bottom:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-compress-arrows-alt"></i> Fit</h4>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Offset (Abstand)</span>
                            <span id="garment-offset-value">${Pt.toFixed(3)}</span>
                        </div>
                        <input type="range" id="garment-offset" min="0" max="50" step="0.1" value="${Pt*1e3}" style="width:100%;cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Stiffness (Steifigkeit)</span>
                            <span id="garment-stiffness-value">${ft.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-stiffness" min="0" max="100" step="1" value="${ft*100}" style="width:100%;cursor:pointer;" />
                    </div>
                </div>

                <!-- Transform -->
                <div style="margin-bottom:16px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-arrows-alt"></i> Transform</h4>

                    <label style="display:block;font-size:0.75rem;color:var(--text-muted);margin-bottom:6px;">Position</label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;margin-bottom:12px;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="garment-pos-x" value="${ct.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="garment-pos-y" value="${ct.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="garment-pos-z" value="${ct.z.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Material-Änderungen wirken sofort<br>
                    <i class="fas fa-info-circle"></i> Fit-Änderungen erfordern Garment-Reload (TODO)
                </div>
            </div>
        `;const Qt=document.getElementById("garment-color"),vt=document.getElementById("garment-roughness"),Xt=document.getElementById("garment-roughness-value"),cn=document.getElementById("garment-metalness"),Ct=document.getElementById("garment-metalness-value"),Ht=document.getElementById("garment-offset"),In=document.getElementById("garment-offset-value"),ci=document.getElementById("garment-stiffness"),mi=document.getElementById("garment-stiffness-value"),P=document.getElementById("garment-pos-x"),q=document.getElementById("garment-pos-y"),te=document.getElementById("garment-pos-z");if(Qt&&(Qt.oninput=Z=>{_e.color.setHex(parseInt(Z.target.value.substring(1),16))}),vt&&Xt&&(vt.oninput=Z=>{const j=parseFloat(Z.target.value);_e.roughness=j,Xt.textContent=j.toFixed(2)}),cn&&Ct&&(cn.oninput=Z=>{const j=parseFloat(Z.target.value);_e.metalness=j,Ct.textContent=j.toFixed(2)}),Ht&&In&&(Ht.oninput=Z=>{const j=parseFloat(Z.target.value)/1e3;In.textContent=j.toFixed(3),F.userData.offset=j}),ci&&mi&&(ci.oninput=Z=>{const j=parseFloat(Z.target.value)/100;mi.textContent=j.toFixed(2),F.userData.stiffness=j}),P&&q&&te){const Z=()=>{F.position.set(parseFloat(P.value),parseFloat(q.value),parseFloat(te.value))};P.oninput=Z,q.oninput=Z,te.oninput=Z}}function mt(F){document.querySelectorAll(".panel-tab").forEach(vt=>vt.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(vt=>vt.classList.remove("active"));const W=document.querySelector('[data-tab="tab-properties"]'),ie=document.getElementById("tab-properties");W&&W.classList.add("active"),ie&&ie.classList.add("active");const ve=document.getElementById("properties-content");if(!ve)return;const je=F.userData.presetName||"Character",_e=F.userData.bodyType||"Unknown",He=F.position,ot=F.rotation;ve.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-user"></i> ${je}
                </h3>

                <div style="margin-bottom:16px;font-size:0.8rem;">
                    <span style="color:var(--text-muted);">Body Type:</span>
                    <span style="color:var(--text);margin-left:8px;">${_e}</span>
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
                            <input type="number" id="char-pos-x" value="${He.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-pos-y" value="${He.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-pos-z" value="${He.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="char-rot-x" value="${(ot.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-rot-y" value="${(ot.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-rot-z" value="${(ot.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Nutze die Transform-Controls in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const St=document.getElementById("char-pos-x"),Nt=document.getElementById("char-pos-y"),Pt=document.getElementById("char-pos-z");if(St&&Nt&&Pt){const vt=()=>{F.position.set(parseFloat(St.value),parseFloat(Nt.value),parseFloat(Pt.value))};St.oninput=vt,Nt.oninput=vt,Pt.oninput=vt}const ft=document.getElementById("char-rot-x"),ct=document.getElementById("char-rot-y"),Qt=document.getElementById("char-rot-z");if(ft&&ct&&Qt){const vt=()=>{F.rotation.set(parseFloat(ft.value)*Math.PI/180,parseFloat(ct.value)*Math.PI/180,parseFloat(Qt.value)*Math.PI/180)};ft.oninput=vt,ct.oninput=vt,Qt.oninput=vt}Ft(F),Re(F)}function Ft(F){const W=document.getElementById("meta-sliders-container");if(!W)return;const ie={age:{min:-1,max:1,label:"Alter",step:.01},mass:{min:-1,max:1,label:"Gewicht",step:.01},tone:{min:-1,max:1,label:"Muskeltonus",step:.01},height:{min:-1,max:1,label:"Höhe",step:.01}},ve=F.userData.meta||{age:0,mass:0,tone:0,height:0};let je="";for(const[_e,He]of Object.entries(ie)){const ot=ve[_e]||0,St=He.min,Nt=He.max;je+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${He.label}</span>
                        <span id="meta-${_e}-value" style="color:var(--text);">${ot.toFixed(2)}</span>
                    </div>
                    <input type="range" id="meta-${_e}" min="${St}" max="${Nt}" step="${He.step}" value="${ot}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}W.innerHTML=je;for(const _e of Object.keys(ie)){const He=document.getElementById(`meta-${_e}`),ot=document.getElementById(`meta-${_e}-value`);He&&ot&&(He.oninput=async()=>{const St=parseFloat(He.value);ot.textContent=St.toFixed(2),ve[_e]=St,F.userData.meta=ve,await X(F)})}}async function X(F){try{let Nt=function(ft){const ct=atob(ft),Qt=new Uint8Array(ct.length);for(let vt=0;vt<ct.length;vt++)Qt[vt]=ct.charCodeAt(vt);return new Float32Array(Qt.buffer)};var W=Nt;const ie=new URLSearchParams;ie.set("body_type",F.userData.bodyType||"Female_Caucasian");const ve=F.userData.morphs||{};for(const[ft,ct]of Object.entries(ve))ct!=null&&ie.set(`morph_${ft}`,String(ct));const je=F.userData.meta||{};for(const[ft,ct]of Object.entries(je))ct!=null&&ie.set(`meta_${ft}`,String(ct));const _e=`/api/character/mesh/?${ie.toString()}`,He=await fetch(_e);if(!He.ok)throw new Error(`Character mesh API error: ${He.status}`);const ot=await He.json(),St=F.children.find(ft=>ft.isMesh&&!ft.userData.isHair&&!ft.userData.isGarment);if(!St){console.warn("Could not find body mesh to update");return}const Pt=Nt(ot.vertices);for(let ft=0;ft<Pt.length;ft+=3){const ct=Pt[ft+1],Qt=Pt[ft+2];Pt[ft+1]=Qt,Pt[ft+2]=-ct}if(St.geometry.attributes.position.array.set(Pt),St.geometry.attributes.position.needsUpdate=!0,ot.normals){const ft=Nt(ot.normals);for(let ct=0;ct<ft.length;ct+=3){const Qt=ft[ct+1],vt=ft[ct+2];ft[ct+1]=vt,ft[ct+2]=-Qt}St.geometry.attributes.normal.array.set(ft),St.geometry.attributes.normal.needsUpdate=!0}else St.geometry.computeVertexNormals();console.log("✓ Character mesh reloaded")}catch(ie){console.error("Failed to reload character mesh:",ie)}}function Re(F){const W=document.getElementById("morph-sliders-container");if(!W)return;const ie=F.userData.morphs||{};if(Object.keys(ie).length===0){W.innerHTML='<div style="font-size:0.75rem;color:var(--text-muted);text-align:center;padding:10px;">Keine Morphs</div>';return}let ve='<div style="max-height:300px;overflow-y:auto;padding-right:4px;">';for(const[je,_e]of Object.entries(ie)){const He=_e||0;ve+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${je}</span>
                        <span id="morph-${je}-value" style="color:var(--text);">${He.toFixed(2)}</span>
                    </div>
                    <input type="range" id="morph-${je}" min="0" max="1" step="0.01" value="${He}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}ve+="</div>",W.innerHTML=ve;for(const je of Object.keys(ie)){const _e=document.getElementById(`morph-${je}`),He=document.getElementById(`morph-${je}-value`);_e&&He&&(_e.oninput=async()=>{const ot=parseFloat(_e.value);He.textContent=ot.toFixed(2),ie[je]=ot,F.userData.morphs=ie,await X(F)})}}function ae(){const F=document.getElementById("properties-content");F&&(F.innerHTML=`
            <div style="padding:20px;color:var(--text-muted);font-size:0.85rem;text-align:center;">
                <i class="fas fa-hand-pointer" style="font-size:2rem;margin-bottom:10px;opacity:0.3;"></i>
                <p>Klicke auf ein Licht-Icon oder Character in der Szene<br>um Eigenschaften zu bearbeiten.</p>
            </div>
        `)}function pe(){requestAnimationFrame(pe);const F=V.getDelta();if(O&&ce&&(O.update(F*ke),Ce=N?N.time:0,Ce>=we&&(Ce=0,N&&(N.time=0)),Ue()),f&&f.userData.light){const W=f.userData.light;W.position.copy(f.position),f.lookAt(W.target.position)}i.update(),n.render(e,t)}pe()});
