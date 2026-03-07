/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Xs={ROTATE:0,DOLLY:1,PAN:2},Hs={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},lM=0,wp=1,uM=2,ug=1,hM=2,$i=3,nr=0,$n=1,Kn=2,Er=0,qs=1,Ap=2,Rp=3,Pp=4,dM=5,os=100,fM=101,pM=102,mM=103,gM=104,_M=200,vM=201,yM=202,xM=203,gh=204,_h=205,bM=206,SM=207,EM=208,MM=209,TM=210,wM=211,AM=212,RM=213,PM=214,vh=0,yh=1,xh=2,Zs=3,bh=4,Sh=5,Eh=6,Mh=7,hg=0,CM=1,DM=2,Mr=0,IM=1,LM=2,FM=3,dg=4,NM=5,OM=6,UM=7,Cp="attached",BM="detached",fg=300,Qs=301,Js=302,Th=303,wh=304,kc=306,eo=1e3,br=1001,Fc=1002,Gn=1003,pg=1004,Wo=1005,ai=1006,Mc=1007,Qi=1008,ir=1009,mg=1010,gg=1011,Jo=1012,ld=1013,ls=1014,Si=1015,ia=1016,ud=1017,hd=1018,to=1020,_g=35902,vg=1021,yg=1022,fi=1023,xg=1024,bg=1025,Ys=1026,no=1027,dd=1028,fd=1029,Sg=1030,pd=1031,md=1033,Tc=33776,wc=33777,Ac=33778,Rc=33779,Ah=35840,Rh=35841,Ph=35842,Ch=35843,Dh=36196,Ih=37492,Lh=37496,Fh=37808,Nh=37809,Oh=37810,Uh=37811,Bh=37812,kh=37813,zh=37814,Hh=37815,Vh=37816,Gh=37817,Wh=37818,jh=37819,Xh=37820,qh=37821,Pc=36492,Yh=36494,Kh=36495,Eg=36283,$h=36284,Zh=36285,Qh=36286,kM=2200,gd=2201,zM=2202,ea=2300,ta=2301,Eu=2302,Vs=2400,Gs=2401,Nc=2402,_d=2500,HM=2501,VM=0,Mg=1,Jh=2,GM=3200,WM=3201,Tg=0,jM=1,xr="",En="srgb",Wn="srgb-linear",zc="linear",Gt="srgb",ws=7680,Dp=519,XM=512,qM=513,YM=514,wg=515,KM=516,$M=517,ZM=518,QM=519,ed=35044,Ip="300 es",Ji=2e3,Oc=2001;class Rr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const s=i.indexOf(t);s!==-1&&i.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let s=0,a=i.length;s<a;s++)i[s].call(this,e);e.target=null}}}const Nn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Lp=1234567;const $o=Math.PI/180,io=180/Math.PI;function Ei(){const r=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Nn[r&255]+Nn[r>>8&255]+Nn[r>>16&255]+Nn[r>>24&255]+"-"+Nn[e&255]+Nn[e>>8&255]+"-"+Nn[e>>16&15|64]+Nn[e>>24&255]+"-"+Nn[t&63|128]+Nn[t>>8&255]+"-"+Nn[t>>16&255]+Nn[t>>24&255]+Nn[n&255]+Nn[n>>8&255]+Nn[n>>16&255]+Nn[n>>24&255]).toLowerCase()}function Cn(r,e,t){return Math.max(e,Math.min(t,r))}function vd(r,e){return(r%e+e)%e}function JM(r,e,t,n,i){return n+(r-e)*(i-n)/(t-e)}function eT(r,e,t){return r!==e?(t-r)/(e-r):0}function Zo(r,e,t){return(1-t)*r+t*e}function tT(r,e,t,n){return Zo(r,e,1-Math.exp(-t*n))}function nT(r,e=1){return e-Math.abs(vd(r,e*2)-e)}function iT(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*(3-2*r))}function rT(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*r*(r*(r*6-15)+10))}function sT(r,e){return r+Math.floor(Math.random()*(e-r+1))}function oT(r,e){return r+Math.random()*(e-r)}function aT(r){return r*(.5-Math.random())}function cT(r){r!==void 0&&(Lp=r);let e=Lp+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function lT(r){return r*$o}function uT(r){return r*io}function hT(r){return(r&r-1)===0&&r!==0}function dT(r){return Math.pow(2,Math.ceil(Math.log(r)/Math.LN2))}function fT(r){return Math.pow(2,Math.floor(Math.log(r)/Math.LN2))}function pT(r,e,t,n,i){const s=Math.cos,a=Math.sin,c=s(t/2),u=a(t/2),h=s((e+n)/2),f=a((e+n)/2),p=s((e-n)/2),m=a((e-n)/2),g=s((n-e)/2),x=a((n-e)/2);switch(i){case"XYX":r.set(c*f,u*p,u*m,c*h);break;case"YZY":r.set(u*m,c*f,u*p,c*h);break;case"ZXZ":r.set(u*p,u*m,c*f,c*h);break;case"XZX":r.set(c*f,u*x,u*g,c*h);break;case"YXY":r.set(u*g,c*f,u*x,c*h);break;case"ZYZ":r.set(u*x,u*g,c*f,c*h);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+i)}}function xi(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return r/4294967295;case Uint16Array:return r/65535;case Uint8Array:return r/255;case Int32Array:return Math.max(r/2147483647,-1);case Int16Array:return Math.max(r/32767,-1);case Int8Array:return Math.max(r/127,-1);default:throw new Error("Invalid component type.")}}function Vt(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return Math.round(r*4294967295);case Uint16Array:return Math.round(r*65535);case Uint8Array:return Math.round(r*255);case Int32Array:return Math.round(r*2147483647);case Int16Array:return Math.round(r*32767);case Int8Array:return Math.round(r*127);default:throw new Error("Invalid component type.")}}const Ag={DEG2RAD:$o,RAD2DEG:io,generateUUID:Ei,clamp:Cn,euclideanModulo:vd,mapLinear:JM,inverseLerp:eT,lerp:Zo,damp:tT,pingpong:nT,smoothstep:iT,smootherstep:rT,randInt:sT,randFloat:oT,randFloatSpread:aT,seededRandom:cT,degToRad:lT,radToDeg:uT,isPowerOfTwo:hT,ceilPowerOfTwo:dT,floorPowerOfTwo:fT,setQuaternionFromProperEuler:pT,normalize:Vt,denormalize:xi};class lt{constructor(e=0,t=0){lt.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Cn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),i=Math.sin(t),s=this.x-e.x,a=this.y-e.y;return this.x=s*n-a*i+e.x,this.y=s*i+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class yt{constructor(e,t,n,i,s,a,c,u,h){yt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h)}set(e,t,n,i,s,a,c,u,h){const f=this.elements;return f[0]=e,f[1]=i,f[2]=c,f[3]=t,f[4]=s,f[5]=u,f[6]=n,f[7]=a,f[8]=h,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[3],u=n[6],h=n[1],f=n[4],p=n[7],m=n[2],g=n[5],x=n[8],E=i[0],v=i[3],_=i[6],A=i[1],w=i[4],b=i[7],B=i[2],U=i[5],O=i[8];return s[0]=a*E+c*A+u*B,s[3]=a*v+c*w+u*U,s[6]=a*_+c*b+u*O,s[1]=h*E+f*A+p*B,s[4]=h*v+f*w+p*U,s[7]=h*_+f*b+p*O,s[2]=m*E+g*A+x*B,s[5]=m*v+g*w+x*U,s[8]=m*_+g*b+x*O,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8];return t*a*f-t*c*h-n*s*f+n*c*u+i*s*h-i*a*u}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=f*a-c*h,m=c*u-f*s,g=h*s-a*u,x=t*p+n*m+i*g;if(x===0)return this.set(0,0,0,0,0,0,0,0,0);const E=1/x;return e[0]=p*E,e[1]=(i*h-f*n)*E,e[2]=(c*n-i*a)*E,e[3]=m*E,e[4]=(f*t-i*u)*E,e[5]=(i*s-c*t)*E,e[6]=g*E,e[7]=(n*u-h*t)*E,e[8]=(a*t-n*s)*E,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,s,a,c){const u=Math.cos(s),h=Math.sin(s);return this.set(n*u,n*h,-n*(u*a+h*c)+a+e,-i*h,i*u,-i*(-h*a+u*c)+c+t,0,0,1),this}scale(e,t){return this.premultiply(Mu.makeScale(e,t)),this}rotate(e){return this.premultiply(Mu.makeRotation(-e)),this}translate(e,t){return this.premultiply(Mu.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Mu=new yt;function Rg(r){for(let e=r.length-1;e>=0;--e)if(r[e]>=65535)return!0;return!1}function na(r){return document.createElementNS("http://www.w3.org/1999/xhtml",r)}function mT(){const r=na("canvas");return r.style.display="block",r}const Fp={};function jo(r){r in Fp||(Fp[r]=!0,console.warn(r))}function gT(r,e,t){return new Promise(function(n,i){function s(){switch(r.clientWaitSync(e,r.SYNC_FLUSH_COMMANDS_BIT,0)){case r.WAIT_FAILED:i();break;case r.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}function _T(r){const e=r.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function vT(r){const e=r.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const Ct={enabled:!0,workingColorSpace:Wn,spaces:{},convert:function(r,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===Gt&&(r.r=tr(r.r),r.g=tr(r.g),r.b=tr(r.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(r.applyMatrix3(this.spaces[e].toXYZ),r.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===Gt&&(r.r=Ks(r.r),r.g=Ks(r.g),r.b=Ks(r.b))),r},fromWorkingColorSpace:function(r,e){return this.convert(r,this.workingColorSpace,e)},toWorkingColorSpace:function(r,e){return this.convert(r,e,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===xr?zc:this.spaces[r].transfer},getLuminanceCoefficients:function(r,e=this.workingColorSpace){return r.fromArray(this.spaces[e].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,e,t){return r.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace}};function tr(r){return r<.04045?r*.0773993808:Math.pow(r*.9478672986+.0521327014,2.4)}function Ks(r){return r<.0031308?r*12.92:1.055*Math.pow(r,.41666)-.055}const Np=[.64,.33,.3,.6,.15,.06],Op=[.2126,.7152,.0722],Up=[.3127,.329],Bp=new yt().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),kp=new yt().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);Ct.define({[Wn]:{primaries:Np,whitePoint:Up,transfer:zc,toXYZ:Bp,fromXYZ:kp,luminanceCoefficients:Op,workingColorSpaceConfig:{unpackColorSpace:En},outputColorSpaceConfig:{drawingBufferColorSpace:En}},[En]:{primaries:Np,whitePoint:Up,transfer:Gt,toXYZ:Bp,fromXYZ:kp,luminanceCoefficients:Op,outputColorSpaceConfig:{drawingBufferColorSpace:En}}});let As;class yT{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{As===void 0&&(As=na("canvas")),As.width=e.width,As.height=e.height;const n=As.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=As}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=na("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const i=n.getImageData(0,0,e.width,e.height),s=i.data;for(let a=0;a<s.length;a++)s[a]=tr(s[a]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(tr(t[n]/255)*255):t[n]=tr(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let xT=0;class Pg{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:xT++}),this.uuid=Ei(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let s;if(Array.isArray(i)){s=[];for(let a=0,c=i.length;a<c;a++)i[a].isDataTexture?s.push(Tu(i[a].image)):s.push(Tu(i[a]))}else s=Tu(i);n.url=s}return t||(e.images[this.uuid]=n),n}}function Tu(r){return typeof HTMLImageElement<"u"&&r instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&r instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&r instanceof ImageBitmap?yT.getDataURL(r):r.data?{data:Array.from(r.data),width:r.width,height:r.height,type:r.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let bT=0;class Mn extends Rr{constructor(e=Mn.DEFAULT_IMAGE,t=Mn.DEFAULT_MAPPING,n=br,i=br,s=ai,a=Qi,c=fi,u=ir,h=Mn.DEFAULT_ANISOTROPY,f=xr){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:bT++}),this.uuid=Ei(),this.name="",this.source=new Pg(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=i,this.magFilter=s,this.minFilter=a,this.anisotropy=h,this.format=c,this.internalFormat=null,this.type=u,this.offset=new lt(0,0),this.repeat=new lt(1,1),this.center=new lt(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new yt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=f,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==fg)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case eo:e.x=e.x-Math.floor(e.x);break;case br:e.x=e.x<0?0:1;break;case Fc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case eo:e.y=e.y-Math.floor(e.y);break;case br:e.y=e.y<0?0:1;break;case Fc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Mn.DEFAULT_IMAGE=null;Mn.DEFAULT_MAPPING=fg;Mn.DEFAULT_ANISOTROPY=1;class Ot{constructor(e=0,t=0,n=0,i=1){Ot.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*i+a[12]*s,this.y=a[1]*t+a[5]*n+a[9]*i+a[13]*s,this.z=a[2]*t+a[6]*n+a[10]*i+a[14]*s,this.w=a[3]*t+a[7]*n+a[11]*i+a[15]*s,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,s;const u=e.elements,h=u[0],f=u[4],p=u[8],m=u[1],g=u[5],x=u[9],E=u[2],v=u[6],_=u[10];if(Math.abs(f-m)<.01&&Math.abs(p-E)<.01&&Math.abs(x-v)<.01){if(Math.abs(f+m)<.1&&Math.abs(p+E)<.1&&Math.abs(x+v)<.1&&Math.abs(h+g+_-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const w=(h+1)/2,b=(g+1)/2,B=(_+1)/2,U=(f+m)/4,O=(p+E)/4,V=(x+v)/4;return w>b&&w>B?w<.01?(n=0,i=.707106781,s=.707106781):(n=Math.sqrt(w),i=U/n,s=O/n):b>B?b<.01?(n=.707106781,i=0,s=.707106781):(i=Math.sqrt(b),n=U/i,s=V/i):B<.01?(n=.707106781,i=.707106781,s=0):(s=Math.sqrt(B),n=O/s,i=V/s),this.set(n,i,s,t),this}let A=Math.sqrt((v-x)*(v-x)+(p-E)*(p-E)+(m-f)*(m-f));return Math.abs(A)<.001&&(A=1),this.x=(v-x)/A,this.y=(p-E)/A,this.z=(m-f)/A,this.w=Math.acos((h+g+_-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class ST extends Rr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new Ot(0,0,e,t),this.scissorTest=!1,this.viewport=new Ot(0,0,e,t);const i={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ai,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new Mn(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let c=0;c<a;c++)this.textures[c]=s.clone(),this.textures[c].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let i=0,s=this.textures.length;i<s;i++)this.textures[i].image.width=e,this.textures[i].image.height=t,this.textures[i].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,i=e.textures.length;n<i;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Pg(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class us extends ST{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Cg extends Mn{constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Gn,this.minFilter=Gn,this.wrapR=br,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class ET extends Mn{constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Gn,this.minFilter=Gn,this.wrapR=br,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Et{constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,s,a,c){let u=n[i+0],h=n[i+1],f=n[i+2],p=n[i+3];const m=s[a+0],g=s[a+1],x=s[a+2],E=s[a+3];if(c===0){e[t+0]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p;return}if(c===1){e[t+0]=m,e[t+1]=g,e[t+2]=x,e[t+3]=E;return}if(p!==E||u!==m||h!==g||f!==x){let v=1-c;const _=u*m+h*g+f*x+p*E,A=_>=0?1:-1,w=1-_*_;if(w>Number.EPSILON){const B=Math.sqrt(w),U=Math.atan2(B,_*A);v=Math.sin(v*U)/B,c=Math.sin(c*U)/B}const b=c*A;if(u=u*v+m*b,h=h*v+g*b,f=f*v+x*b,p=p*v+E*b,v===1-c){const B=1/Math.sqrt(u*u+h*h+f*f+p*p);u*=B,h*=B,f*=B,p*=B}}e[t]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p}static multiplyQuaternionsFlat(e,t,n,i,s,a){const c=n[i],u=n[i+1],h=n[i+2],f=n[i+3],p=s[a],m=s[a+1],g=s[a+2],x=s[a+3];return e[t]=c*x+f*p+u*g-h*m,e[t+1]=u*x+f*m+h*p-c*g,e[t+2]=h*x+f*g+c*m-u*p,e[t+3]=f*x-c*p-u*m-h*g,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,i=e._y,s=e._z,a=e._order,c=Math.cos,u=Math.sin,h=c(n/2),f=c(i/2),p=c(s/2),m=u(n/2),g=u(i/2),x=u(s/2);switch(a){case"XYZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"YXZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"ZXY":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"ZYX":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"YZX":this._x=m*f*p+h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p-m*g*x;break;case"XZY":this._x=m*f*p-h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p+m*g*x;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],i=t[4],s=t[8],a=t[1],c=t[5],u=t[9],h=t[2],f=t[6],p=t[10],m=n+c+p;if(m>0){const g=.5/Math.sqrt(m+1);this._w=.25/g,this._x=(f-u)*g,this._y=(s-h)*g,this._z=(a-i)*g}else if(n>c&&n>p){const g=2*Math.sqrt(1+n-c-p);this._w=(f-u)/g,this._x=.25*g,this._y=(i+a)/g,this._z=(s+h)/g}else if(c>p){const g=2*Math.sqrt(1+c-n-p);this._w=(s-h)/g,this._x=(i+a)/g,this._y=.25*g,this._z=(u+f)/g}else{const g=2*Math.sqrt(1+p-n-c);this._w=(a-i)/g,this._x=(s+h)/g,this._y=(u+f)/g,this._z=.25*g}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Cn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,i=e._y,s=e._z,a=e._w,c=t._x,u=t._y,h=t._z,f=t._w;return this._x=n*f+a*c+i*h-s*u,this._y=i*f+a*u+s*c-n*h,this._z=s*f+a*h+n*u-i*c,this._w=a*f-n*c-i*u-s*h,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,i=this._y,s=this._z,a=this._w;let c=a*e._w+n*e._x+i*e._y+s*e._z;if(c<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,c=-c):this.copy(e),c>=1)return this._w=a,this._x=n,this._y=i,this._z=s,this;const u=1-c*c;if(u<=Number.EPSILON){const g=1-t;return this._w=g*a+t*this._w,this._x=g*n+t*this._x,this._y=g*i+t*this._y,this._z=g*s+t*this._z,this.normalize(),this}const h=Math.sqrt(u),f=Math.atan2(h,c),p=Math.sin((1-t)*f)/h,m=Math.sin(t*f)/h;return this._w=a*p+this._w*m,this._x=n*p+this._x*m,this._y=i*p+this._y*m,this._z=s*p+this._z*m,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),i=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(i*Math.sin(e),i*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class N{constructor(e=0,t=0,n=0){N.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(zp.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(zp.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*i,this.y=s[1]*t+s[4]*n+s[7]*i,this.z=s[2]*t+s[5]*n+s[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=e.elements,a=1/(s[3]*t+s[7]*n+s[11]*i+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*i+s[12])*a,this.y=(s[1]*t+s[5]*n+s[9]*i+s[13])*a,this.z=(s[2]*t+s[6]*n+s[10]*i+s[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,i=this.z,s=e.x,a=e.y,c=e.z,u=e.w,h=2*(a*i-c*n),f=2*(c*t-s*i),p=2*(s*n-a*t);return this.x=t+u*h+a*p-c*f,this.y=n+u*f+c*h-s*p,this.z=i+u*p+s*f-a*h,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*i,this.y=s[1]*t+s[5]*n+s[9]*i,this.z=s[2]*t+s[6]*n+s[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,i=e.y,s=e.z,a=t.x,c=t.y,u=t.z;return this.x=i*u-s*c,this.y=s*a-n*u,this.z=n*c-i*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return wu.copy(this).projectOnVector(e),this.sub(wu)}reflect(e){return this.sub(wu.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Cn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const wu=new N,zp=new Et;class Mi{constructor(e=new N(1/0,1/0,1/0),t=new N(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(gi.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(gi.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=gi.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let a=0,c=s.count;a<c;a++)e.isMesh===!0?e.getVertexPosition(a,gi):gi.fromBufferAttribute(s,a),gi.applyMatrix4(e.matrixWorld),this.expandByPoint(gi);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),ja.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),ja.copy(n.boundingBox)),ja.applyMatrix4(e.matrixWorld),this.union(ja)}const i=e.children;for(let s=0,a=i.length;s<a;s++)this.expandByObject(i[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,gi),gi.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Lo),Xa.subVectors(this.max,Lo),Rs.subVectors(e.a,Lo),Ps.subVectors(e.b,Lo),Cs.subVectors(e.c,Lo),ur.subVectors(Ps,Rs),hr.subVectors(Cs,Ps),$r.subVectors(Rs,Cs);let t=[0,-ur.z,ur.y,0,-hr.z,hr.y,0,-$r.z,$r.y,ur.z,0,-ur.x,hr.z,0,-hr.x,$r.z,0,-$r.x,-ur.y,ur.x,0,-hr.y,hr.x,0,-$r.y,$r.x,0];return!Au(t,Rs,Ps,Cs,Xa)||(t=[1,0,0,0,1,0,0,0,1],!Au(t,Rs,Ps,Cs,Xa))?!1:(qa.crossVectors(ur,hr),t=[qa.x,qa.y,qa.z],Au(t,Rs,Ps,Cs,Xa))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,gi).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(gi).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Wi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Wi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Wi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Wi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Wi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Wi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Wi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Wi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Wi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Wi=[new N,new N,new N,new N,new N,new N,new N,new N],gi=new N,ja=new Mi,Rs=new N,Ps=new N,Cs=new N,ur=new N,hr=new N,$r=new N,Lo=new N,Xa=new N,qa=new N,Zr=new N;function Au(r,e,t,n,i){for(let s=0,a=r.length-3;s<=a;s+=3){Zr.fromArray(r,s);const c=i.x*Math.abs(Zr.x)+i.y*Math.abs(Zr.y)+i.z*Math.abs(Zr.z),u=e.dot(Zr),h=t.dot(Zr),f=n.dot(Zr);if(Math.max(-Math.max(u,h,f),Math.min(u,h,f))>c)return!1}return!0}const MT=new Mi,Fo=new N,Ru=new N;class Ii{constructor(e=new N,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):MT.setFromPoints(e).getCenter(n);let i=0;for(let s=0,a=e.length;s<a;s++)i=Math.max(i,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Fo.subVectors(e,this.center);const t=Fo.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(Fo,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Ru.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Fo.copy(e.center).add(Ru)),this.expandByPoint(Fo.copy(e.center).sub(Ru))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const ji=new N,Pu=new N,Ya=new N,dr=new N,Cu=new N,Ka=new N,Du=new N;class co{constructor(e=new N,t=new N(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,ji)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=ji.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(ji.copy(this.origin).addScaledVector(this.direction,t),ji.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){Pu.copy(e).add(t).multiplyScalar(.5),Ya.copy(t).sub(e).normalize(),dr.copy(this.origin).sub(Pu);const s=e.distanceTo(t)*.5,a=-this.direction.dot(Ya),c=dr.dot(this.direction),u=-dr.dot(Ya),h=dr.lengthSq(),f=Math.abs(1-a*a);let p,m,g,x;if(f>0)if(p=a*u-c,m=a*c-u,x=s*f,p>=0)if(m>=-x)if(m<=x){const E=1/f;p*=E,m*=E,g=p*(p+a*m+2*c)+m*(a*p+m+2*u)+h}else m=s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m=-s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m<=-x?(p=Math.max(0,-(-a*s+c)),m=p>0?-s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h):m<=x?(p=0,m=Math.min(Math.max(-s,-u),s),g=m*(m+2*u)+h):(p=Math.max(0,-(a*s+c)),m=p>0?s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h);else m=a>0?-s:s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;return n&&n.copy(this.origin).addScaledVector(this.direction,p),i&&i.copy(Pu).addScaledVector(Ya,m),g}intersectSphere(e,t){ji.subVectors(e.center,this.origin);const n=ji.dot(this.direction),i=ji.dot(ji)-n*n,s=e.radius*e.radius;if(i>s)return null;const a=Math.sqrt(s-i),c=n-a,u=n+a;return u<0?null:c<0?this.at(u,t):this.at(c,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,s,a,c,u;const h=1/this.direction.x,f=1/this.direction.y,p=1/this.direction.z,m=this.origin;return h>=0?(n=(e.min.x-m.x)*h,i=(e.max.x-m.x)*h):(n=(e.max.x-m.x)*h,i=(e.min.x-m.x)*h),f>=0?(s=(e.min.y-m.y)*f,a=(e.max.y-m.y)*f):(s=(e.max.y-m.y)*f,a=(e.min.y-m.y)*f),n>a||s>i||((s>n||isNaN(n))&&(n=s),(a<i||isNaN(i))&&(i=a),p>=0?(c=(e.min.z-m.z)*p,u=(e.max.z-m.z)*p):(c=(e.max.z-m.z)*p,u=(e.min.z-m.z)*p),n>u||c>i)||((c>n||n!==n)&&(n=c),(u<i||i!==i)&&(i=u),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,ji)!==null}intersectTriangle(e,t,n,i,s){Cu.subVectors(t,e),Ka.subVectors(n,e),Du.crossVectors(Cu,Ka);let a=this.direction.dot(Du),c;if(a>0){if(i)return null;c=1}else if(a<0)c=-1,a=-a;else return null;dr.subVectors(this.origin,e);const u=c*this.direction.dot(Ka.crossVectors(dr,Ka));if(u<0)return null;const h=c*this.direction.dot(Cu.cross(dr));if(h<0||u+h>a)return null;const f=-c*dr.dot(Du);return f<0?null:this.at(f/a,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class ft{constructor(e,t,n,i,s,a,c,u,h,f,p,m,g,x,E,v){ft.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,E,v)}set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,E,v){const _=this.elements;return _[0]=e,_[4]=t,_[8]=n,_[12]=i,_[1]=s,_[5]=a,_[9]=c,_[13]=u,_[2]=h,_[6]=f,_[10]=p,_[14]=m,_[3]=g,_[7]=x,_[11]=E,_[15]=v,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new ft().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,i=1/Ds.setFromMatrixColumn(e,0).length(),s=1/Ds.setFromMatrixColumn(e,1).length(),a=1/Ds.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,i=e.y,s=e.z,a=Math.cos(n),c=Math.sin(n),u=Math.cos(i),h=Math.sin(i),f=Math.cos(s),p=Math.sin(s);if(e.order==="XYZ"){const m=a*f,g=a*p,x=c*f,E=c*p;t[0]=u*f,t[4]=-u*p,t[8]=h,t[1]=g+x*h,t[5]=m-E*h,t[9]=-c*u,t[2]=E-m*h,t[6]=x+g*h,t[10]=a*u}else if(e.order==="YXZ"){const m=u*f,g=u*p,x=h*f,E=h*p;t[0]=m+E*c,t[4]=x*c-g,t[8]=a*h,t[1]=a*p,t[5]=a*f,t[9]=-c,t[2]=g*c-x,t[6]=E+m*c,t[10]=a*u}else if(e.order==="ZXY"){const m=u*f,g=u*p,x=h*f,E=h*p;t[0]=m-E*c,t[4]=-a*p,t[8]=x+g*c,t[1]=g+x*c,t[5]=a*f,t[9]=E-m*c,t[2]=-a*h,t[6]=c,t[10]=a*u}else if(e.order==="ZYX"){const m=a*f,g=a*p,x=c*f,E=c*p;t[0]=u*f,t[4]=x*h-g,t[8]=m*h+E,t[1]=u*p,t[5]=E*h+m,t[9]=g*h-x,t[2]=-h,t[6]=c*u,t[10]=a*u}else if(e.order==="YZX"){const m=a*u,g=a*h,x=c*u,E=c*h;t[0]=u*f,t[4]=E-m*p,t[8]=x*p+g,t[1]=p,t[5]=a*f,t[9]=-c*f,t[2]=-h*f,t[6]=g*p+x,t[10]=m-E*p}else if(e.order==="XZY"){const m=a*u,g=a*h,x=c*u,E=c*h;t[0]=u*f,t[4]=-p,t[8]=h*f,t[1]=m*p+E,t[5]=a*f,t[9]=g*p-x,t[2]=x*p-g,t[6]=c*f,t[10]=E*p+m}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(TT,e,wT)}lookAt(e,t,n){const i=this.elements;return si.subVectors(e,t),si.lengthSq()===0&&(si.z=1),si.normalize(),fr.crossVectors(n,si),fr.lengthSq()===0&&(Math.abs(n.z)===1?si.x+=1e-4:si.z+=1e-4,si.normalize(),fr.crossVectors(n,si)),fr.normalize(),$a.crossVectors(si,fr),i[0]=fr.x,i[4]=$a.x,i[8]=si.x,i[1]=fr.y,i[5]=$a.y,i[9]=si.y,i[2]=fr.z,i[6]=$a.z,i[10]=si.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[4],u=n[8],h=n[12],f=n[1],p=n[5],m=n[9],g=n[13],x=n[2],E=n[6],v=n[10],_=n[14],A=n[3],w=n[7],b=n[11],B=n[15],U=i[0],O=i[4],V=i[8],I=i[12],R=i[1],H=i[5],ee=i[9],te=i[13],se=i[2],he=i[6],q=i[10],de=i[14],re=i[3],ge=i[7],be=i[11],ze=i[15];return s[0]=a*U+c*R+u*se+h*re,s[4]=a*O+c*H+u*he+h*ge,s[8]=a*V+c*ee+u*q+h*be,s[12]=a*I+c*te+u*de+h*ze,s[1]=f*U+p*R+m*se+g*re,s[5]=f*O+p*H+m*he+g*ge,s[9]=f*V+p*ee+m*q+g*be,s[13]=f*I+p*te+m*de+g*ze,s[2]=x*U+E*R+v*se+_*re,s[6]=x*O+E*H+v*he+_*ge,s[10]=x*V+E*ee+v*q+_*be,s[14]=x*I+E*te+v*de+_*ze,s[3]=A*U+w*R+b*se+B*re,s[7]=A*O+w*H+b*he+B*ge,s[11]=A*V+w*ee+b*q+B*be,s[15]=A*I+w*te+b*de+B*ze,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],i=e[8],s=e[12],a=e[1],c=e[5],u=e[9],h=e[13],f=e[2],p=e[6],m=e[10],g=e[14],x=e[3],E=e[7],v=e[11],_=e[15];return x*(+s*u*p-i*h*p-s*c*m+n*h*m+i*c*g-n*u*g)+E*(+t*u*g-t*h*m+s*a*m-i*a*g+i*h*f-s*u*f)+v*(+t*h*p-t*c*g-s*a*p+n*a*g+s*c*f-n*h*f)+_*(-i*c*f-t*u*p+t*c*m+i*a*p-n*a*m+n*u*f)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=e[9],m=e[10],g=e[11],x=e[12],E=e[13],v=e[14],_=e[15],A=p*v*h-E*m*h+E*u*g-c*v*g-p*u*_+c*m*_,w=x*m*h-f*v*h-x*u*g+a*v*g+f*u*_-a*m*_,b=f*E*h-x*p*h+x*c*g-a*E*g-f*c*_+a*p*_,B=x*p*u-f*E*u-x*c*m+a*E*m+f*c*v-a*p*v,U=t*A+n*w+i*b+s*B;if(U===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const O=1/U;return e[0]=A*O,e[1]=(E*m*s-p*v*s-E*i*g+n*v*g+p*i*_-n*m*_)*O,e[2]=(c*v*s-E*u*s+E*i*h-n*v*h-c*i*_+n*u*_)*O,e[3]=(p*u*s-c*m*s-p*i*h+n*m*h+c*i*g-n*u*g)*O,e[4]=w*O,e[5]=(f*v*s-x*m*s+x*i*g-t*v*g-f*i*_+t*m*_)*O,e[6]=(x*u*s-a*v*s-x*i*h+t*v*h+a*i*_-t*u*_)*O,e[7]=(a*m*s-f*u*s+f*i*h-t*m*h-a*i*g+t*u*g)*O,e[8]=b*O,e[9]=(x*p*s-f*E*s-x*n*g+t*E*g+f*n*_-t*p*_)*O,e[10]=(a*E*s-x*c*s+x*n*h-t*E*h-a*n*_+t*c*_)*O,e[11]=(f*c*s-a*p*s-f*n*h+t*p*h+a*n*g-t*c*g)*O,e[12]=B*O,e[13]=(f*E*i-x*p*i+x*n*m-t*E*m-f*n*v+t*p*v)*O,e[14]=(x*c*i-a*E*i-x*n*u+t*E*u+a*n*v-t*c*v)*O,e[15]=(a*p*i-f*c*i+f*n*u-t*p*u-a*n*m+t*c*m)*O,this}scale(e){const t=this.elements,n=e.x,i=e.y,s=e.z;return t[0]*=n,t[4]*=i,t[8]*=s,t[1]*=n,t[5]*=i,t[9]*=s,t[2]*=n,t[6]*=i,t[10]*=s,t[3]*=n,t[7]*=i,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),i=Math.sin(t),s=1-n,a=e.x,c=e.y,u=e.z,h=s*a,f=s*c;return this.set(h*a+n,h*c-i*u,h*u+i*c,0,h*c+i*u,f*c+n,f*u-i*a,0,h*u-i*c,f*u+i*a,s*u*u+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,s,a){return this.set(1,n,s,0,e,1,a,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){const i=this.elements,s=t._x,a=t._y,c=t._z,u=t._w,h=s+s,f=a+a,p=c+c,m=s*h,g=s*f,x=s*p,E=a*f,v=a*p,_=c*p,A=u*h,w=u*f,b=u*p,B=n.x,U=n.y,O=n.z;return i[0]=(1-(E+_))*B,i[1]=(g+b)*B,i[2]=(x-w)*B,i[3]=0,i[4]=(g-b)*U,i[5]=(1-(m+_))*U,i[6]=(v+A)*U,i[7]=0,i[8]=(x+w)*O,i[9]=(v-A)*O,i[10]=(1-(m+E))*O,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){const i=this.elements;let s=Ds.set(i[0],i[1],i[2]).length();const a=Ds.set(i[4],i[5],i[6]).length(),c=Ds.set(i[8],i[9],i[10]).length();this.determinant()<0&&(s=-s),e.x=i[12],e.y=i[13],e.z=i[14],_i.copy(this);const h=1/s,f=1/a,p=1/c;return _i.elements[0]*=h,_i.elements[1]*=h,_i.elements[2]*=h,_i.elements[4]*=f,_i.elements[5]*=f,_i.elements[6]*=f,_i.elements[8]*=p,_i.elements[9]*=p,_i.elements[10]*=p,t.setFromRotationMatrix(_i),n.x=s,n.y=a,n.z=c,this}makePerspective(e,t,n,i,s,a,c=Ji){const u=this.elements,h=2*s/(t-e),f=2*s/(n-i),p=(t+e)/(t-e),m=(n+i)/(n-i);let g,x;if(c===Ji)g=-(a+s)/(a-s),x=-2*a*s/(a-s);else if(c===Oc)g=-a/(a-s),x=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+c);return u[0]=h,u[4]=0,u[8]=p,u[12]=0,u[1]=0,u[5]=f,u[9]=m,u[13]=0,u[2]=0,u[6]=0,u[10]=g,u[14]=x,u[3]=0,u[7]=0,u[11]=-1,u[15]=0,this}makeOrthographic(e,t,n,i,s,a,c=Ji){const u=this.elements,h=1/(t-e),f=1/(n-i),p=1/(a-s),m=(t+e)*h,g=(n+i)*f;let x,E;if(c===Ji)x=(a+s)*p,E=-2*p;else if(c===Oc)x=s*p,E=-1*p;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+c);return u[0]=2*h,u[4]=0,u[8]=0,u[12]=-m,u[1]=0,u[5]=2*f,u[9]=0,u[13]=-g,u[2]=0,u[6]=0,u[10]=E,u[14]=-x,u[3]=0,u[7]=0,u[11]=0,u[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Ds=new N,_i=new ft,TT=new N(0,0,0),wT=new N(1,1,1),fr=new N,$a=new N,si=new N,Hp=new ft,Vp=new Et;class Ti{constructor(e=0,t=0,n=0,i=Ti.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const i=e.elements,s=i[0],a=i[4],c=i[8],u=i[1],h=i[5],f=i[9],p=i[2],m=i[6],g=i[10];switch(t){case"XYZ":this._y=Math.asin(Cn(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-f,g),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(m,h),this._z=0);break;case"YXZ":this._x=Math.asin(-Cn(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(c,g),this._z=Math.atan2(u,h)):(this._y=Math.atan2(-p,s),this._z=0);break;case"ZXY":this._x=Math.asin(Cn(m,-1,1)),Math.abs(m)<.9999999?(this._y=Math.atan2(-p,g),this._z=Math.atan2(-a,h)):(this._y=0,this._z=Math.atan2(u,s));break;case"ZYX":this._y=Math.asin(-Cn(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(m,g),this._z=Math.atan2(u,s)):(this._x=0,this._z=Math.atan2(-a,h));break;case"YZX":this._z=Math.asin(Cn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(-f,h),this._y=Math.atan2(-p,s)):(this._x=0,this._y=Math.atan2(c,g));break;case"XZY":this._z=Math.asin(-Cn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(m,h),this._y=Math.atan2(c,s)):(this._x=Math.atan2(-f,g),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Hp.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Hp,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Vp.setFromEuler(this),this.setFromQuaternion(Vp,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Ti.DEFAULT_ORDER="XYZ";class yd{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let AT=0;const Gp=new N,Is=new Et,Xi=new ft,Za=new N,No=new N,RT=new N,PT=new Et,Wp=new N(1,0,0),jp=new N(0,1,0),Xp=new N(0,0,1),qp={type:"added"},CT={type:"removed"},Ls={type:"childadded",child:null},Iu={type:"childremoved",child:null};class tn extends Rr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:AT++}),this.uuid=Ei(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=tn.DEFAULT_UP.clone();const e=new N,t=new Ti,n=new Et,i=new N(1,1,1);function s(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new ft},normalMatrix:{value:new yt}}),this.matrix=new ft,this.matrixWorld=new ft,this.matrixAutoUpdate=tn.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new yd,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.multiply(Is),this}rotateOnWorldAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.premultiply(Is),this}rotateX(e){return this.rotateOnAxis(Wp,e)}rotateY(e){return this.rotateOnAxis(jp,e)}rotateZ(e){return this.rotateOnAxis(Xp,e)}translateOnAxis(e,t){return Gp.copy(e).applyQuaternion(this.quaternion),this.position.add(Gp.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Wp,e)}translateY(e){return this.translateOnAxis(jp,e)}translateZ(e){return this.translateOnAxis(Xp,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Xi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Za.copy(e):Za.set(e,t,n);const i=this.parent;this.updateWorldMatrix(!0,!1),No.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Xi.lookAt(No,Za,this.up):Xi.lookAt(Za,No,this.up),this.quaternion.setFromRotationMatrix(Xi),i&&(Xi.extractRotation(i.matrixWorld),Is.setFromRotationMatrix(Xi),this.quaternion.premultiply(Is.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(qp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(CT),Iu.child=e,this.dispatchEvent(Iu),Iu.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Xi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Xi.multiply(e.parent.matrixWorld)),e.applyMatrix4(Xi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(qp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,e,RT),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,PT,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),i.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(i.type="BatchedMesh",i.perObjectFrustumCulled=this.perObjectFrustumCulled,i.sortObjects=this.sortObjects,i.drawRanges=this._drawRanges,i.reservedRanges=this._reservedRanges,i.visibility=this._visibility,i.active=this._active,i.bounds=this._bounds.map(c=>({boxInitialized:c.boxInitialized,boxMin:c.box.min.toArray(),boxMax:c.box.max.toArray(),sphereInitialized:c.sphereInitialized,sphereRadius:c.sphere.radius,sphereCenter:c.sphere.center.toArray()})),i.maxInstanceCount=this._maxInstanceCount,i.maxVertexCount=this._maxVertexCount,i.maxIndexCount=this._maxIndexCount,i.geometryInitialized=this._geometryInitialized,i.geometryCount=this._geometryCount,i.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(i.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(i.boundingSphere={center:i.boundingSphere.center.toArray(),radius:i.boundingSphere.radius}),this.boundingBox!==null&&(i.boundingBox={min:i.boundingBox.min.toArray(),max:i.boundingBox.max.toArray()}));function s(c,u){return c[u.uuid]===void 0&&(c[u.uuid]=u.toJSON(e)),u.uuid}if(this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=s(e.geometries,this.geometry);const c=this.geometry.parameters;if(c!==void 0&&c.shapes!==void 0){const u=c.shapes;if(Array.isArray(u))for(let h=0,f=u.length;h<f;h++){const p=u[h];s(e.shapes,p)}else s(e.shapes,u)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const c=[];for(let u=0,h=this.material.length;u<h;u++)c.push(s(e.materials,this.material[u]));i.material=c}else i.material=s(e.materials,this.material);if(this.children.length>0){i.children=[];for(let c=0;c<this.children.length;c++)i.children.push(this.children[c].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let c=0;c<this.animations.length;c++){const u=this.animations[c];i.animations.push(s(e.animations,u))}}if(t){const c=a(e.geometries),u=a(e.materials),h=a(e.textures),f=a(e.images),p=a(e.shapes),m=a(e.skeletons),g=a(e.animations),x=a(e.nodes);c.length>0&&(n.geometries=c),u.length>0&&(n.materials=u),h.length>0&&(n.textures=h),f.length>0&&(n.images=f),p.length>0&&(n.shapes=p),m.length>0&&(n.skeletons=m),g.length>0&&(n.animations=g),x.length>0&&(n.nodes=x)}return n.object=i,n;function a(c){const u=[];for(const h in c){const f=c[h];delete f.metadata,u.push(f)}return u}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const i=e.children[n];this.add(i.clone())}return this}}tn.DEFAULT_UP=new N(0,1,0);tn.DEFAULT_MATRIX_AUTO_UPDATE=!0;tn.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const vi=new N,qi=new N,Lu=new N,Yi=new N,Fs=new N,Ns=new N,Yp=new N,Fu=new N,Nu=new N,Ou=new N,Uu=new Ot,Bu=new Ot,ku=new Ot;class bi{constructor(e=new N,t=new N,n=new N){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),vi.subVectors(e,t),i.cross(vi);const s=i.lengthSq();return s>0?i.multiplyScalar(1/Math.sqrt(s)):i.set(0,0,0)}static getBarycoord(e,t,n,i,s){vi.subVectors(i,t),qi.subVectors(n,t),Lu.subVectors(e,t);const a=vi.dot(vi),c=vi.dot(qi),u=vi.dot(Lu),h=qi.dot(qi),f=qi.dot(Lu),p=a*h-c*c;if(p===0)return s.set(0,0,0),null;const m=1/p,g=(h*u-c*f)*m,x=(a*f-c*u)*m;return s.set(1-g-x,x,g)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,Yi)===null?!1:Yi.x>=0&&Yi.y>=0&&Yi.x+Yi.y<=1}static getInterpolation(e,t,n,i,s,a,c,u){return this.getBarycoord(e,t,n,i,Yi)===null?(u.x=0,u.y=0,"z"in u&&(u.z=0),"w"in u&&(u.w=0),null):(u.setScalar(0),u.addScaledVector(s,Yi.x),u.addScaledVector(a,Yi.y),u.addScaledVector(c,Yi.z),u)}static getInterpolatedAttribute(e,t,n,i,s,a){return Uu.setScalar(0),Bu.setScalar(0),ku.setScalar(0),Uu.fromBufferAttribute(e,t),Bu.fromBufferAttribute(e,n),ku.fromBufferAttribute(e,i),a.setScalar(0),a.addScaledVector(Uu,s.x),a.addScaledVector(Bu,s.y),a.addScaledVector(ku,s.z),a}static isFrontFacing(e,t,n,i){return vi.subVectors(n,t),qi.subVectors(e,t),vi.cross(qi).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return vi.subVectors(this.c,this.b),qi.subVectors(this.a,this.b),vi.cross(qi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return bi.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return bi.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,i,s){return bi.getInterpolation(e,this.a,this.b,this.c,t,n,i,s)}containsPoint(e){return bi.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return bi.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,i=this.b,s=this.c;let a,c;Fs.subVectors(i,n),Ns.subVectors(s,n),Fu.subVectors(e,n);const u=Fs.dot(Fu),h=Ns.dot(Fu);if(u<=0&&h<=0)return t.copy(n);Nu.subVectors(e,i);const f=Fs.dot(Nu),p=Ns.dot(Nu);if(f>=0&&p<=f)return t.copy(i);const m=u*p-f*h;if(m<=0&&u>=0&&f<=0)return a=u/(u-f),t.copy(n).addScaledVector(Fs,a);Ou.subVectors(e,s);const g=Fs.dot(Ou),x=Ns.dot(Ou);if(x>=0&&g<=x)return t.copy(s);const E=g*h-u*x;if(E<=0&&h>=0&&x<=0)return c=h/(h-x),t.copy(n).addScaledVector(Ns,c);const v=f*x-g*p;if(v<=0&&p-f>=0&&g-x>=0)return Yp.subVectors(s,i),c=(p-f)/(p-f+(g-x)),t.copy(i).addScaledVector(Yp,c);const _=1/(v+E+m);return a=E*_,c=m*_,t.copy(n).addScaledVector(Fs,a).addScaledVector(Ns,c)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Dg={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},pr={h:0,s:0,l:0},Qa={h:0,s:0,l:0};function zu(r,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?r+(e-r)*6*t:t<1/2?e:t<2/3?r+(e-r)*6*(2/3-t):r}class st{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const i=e;i&&i.isColor?this.copy(i):typeof i=="number"?this.setHex(i):typeof i=="string"&&this.setStyle(i)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=En){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,Ct.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=Ct.workingColorSpace){return this.r=e,this.g=t,this.b=n,Ct.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=Ct.workingColorSpace){if(e=vd(e,1),t=Cn(t,0,1),n=Cn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,a=2*n-s;this.r=zu(a,s,e+1/3),this.g=zu(a,s,e),this.b=zu(a,s,e-1/3)}return Ct.toWorkingColorSpace(this,i),this}setStyle(e,t=En){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let i;if(i=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const a=i[1],c=i[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=i[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=En){const n=Dg[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=tr(e.r),this.g=tr(e.g),this.b=tr(e.b),this}copyLinearToSRGB(e){return this.r=Ks(e.r),this.g=Ks(e.g),this.b=Ks(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=En){return Ct.fromWorkingColorSpace(On.copy(this),e),Math.round(Cn(On.r*255,0,255))*65536+Math.round(Cn(On.g*255,0,255))*256+Math.round(Cn(On.b*255,0,255))}getHexString(e=En){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=Ct.workingColorSpace){Ct.fromWorkingColorSpace(On.copy(this),t);const n=On.r,i=On.g,s=On.b,a=Math.max(n,i,s),c=Math.min(n,i,s);let u,h;const f=(c+a)/2;if(c===a)u=0,h=0;else{const p=a-c;switch(h=f<=.5?p/(a+c):p/(2-a-c),a){case n:u=(i-s)/p+(i<s?6:0);break;case i:u=(s-n)/p+2;break;case s:u=(n-i)/p+4;break}u/=6}return e.h=u,e.s=h,e.l=f,e}getRGB(e,t=Ct.workingColorSpace){return Ct.fromWorkingColorSpace(On.copy(this),t),e.r=On.r,e.g=On.g,e.b=On.b,e}getStyle(e=En){Ct.fromWorkingColorSpace(On.copy(this),e);const t=On.r,n=On.g,i=On.b;return e!==En?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${i.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(i*255)})`}offsetHSL(e,t,n){return this.getHSL(pr),this.setHSL(pr.h+e,pr.s+t,pr.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(pr),e.getHSL(Qa);const n=Zo(pr.h,Qa.h,t),i=Zo(pr.s,Qa.s,t),s=Zo(pr.l,Qa.l,t);return this.setHSL(n,i,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,i=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*i,this.g=s[1]*t+s[4]*n+s[7]*i,this.b=s[2]*t+s[5]*n+s[8]*i,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const On=new st;st.NAMES=Dg;let DT=0;class Di extends Rr{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:DT++}),this.uuid=Ei(),this.name="",this.blending=qs,this.side=nr,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=gh,this.blendDst=_h,this.blendEquation=os,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new st(0,0,0),this.blendAlpha=0,this.depthFunc=Zs,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Dp,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=ws,this.stencilZFail=ws,this.stencilZPass=ws,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const i=this[t];if(i===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==qs&&(n.blending=this.blending),this.side!==nr&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==gh&&(n.blendSrc=this.blendSrc),this.blendDst!==_h&&(n.blendDst=this.blendDst),this.blendEquation!==os&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Zs&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Dp&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==ws&&(n.stencilFail=this.stencilFail),this.stencilZFail!==ws&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==ws&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(s){const a=[];for(const c in s){const u=s[c];delete u.metadata,a.push(u)}return a}if(t){const s=i(e.textures),a=i(e.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const i=t.length;n=new Array(i);for(let s=0;s!==i;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class pi extends Di{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new st(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ti,this.combine=hg,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const dn=new N,Ja=new lt;class ln{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=ed,this.updateRanges=[],this.gpuType=Si,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,s=this.itemSize;i<s;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Ja.fromBufferAttribute(this,t),Ja.applyMatrix3(e),this.setXY(t,Ja.x,Ja.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)dn.fromBufferAttribute(this,t),dn.applyMatrix3(e),this.setXYZ(t,dn.x,dn.y,dn.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)dn.fromBufferAttribute(this,t),dn.applyMatrix4(e),this.setXYZ(t,dn.x,dn.y,dn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)dn.fromBufferAttribute(this,t),dn.applyNormalMatrix(e),this.setXYZ(t,dn.x,dn.y,dn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)dn.fromBufferAttribute(this,t),dn.transformDirection(e),this.setXYZ(t,dn.x,dn.y,dn.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=xi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Vt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=xi(t,this.array)),t}setX(e,t){return this.normalized&&(t=Vt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=xi(t,this.array)),t}setY(e,t){return this.normalized&&(t=Vt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=xi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Vt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=xi(t,this.array)),t}setW(e,t){return this.normalized&&(t=Vt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=Vt(t,this.array),n=Vt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=Vt(t,this.array),n=Vt(n,this.array),i=Vt(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e*=this.itemSize,this.normalized&&(t=Vt(t,this.array),n=Vt(n,this.array),i=Vt(i,this.array),s=Vt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==ed&&(e.usage=this.usage),e}}class Ig extends ln{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Lg extends ln{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class $t extends ln{constructor(e,t,n){super(new Float32Array(e),t,n)}}let IT=0;const hi=new ft,Hu=new tn,Os=new N,oi=new Mi,Oo=new Mi,Sn=new N;class _n extends Rr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:IT++}),this.uuid=Ei(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Rg(e)?Lg:Ig)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new yt().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return hi.makeRotationFromQuaternion(e),this.applyMatrix4(hi),this}rotateX(e){return hi.makeRotationX(e),this.applyMatrix4(hi),this}rotateY(e){return hi.makeRotationY(e),this.applyMatrix4(hi),this}rotateZ(e){return hi.makeRotationZ(e),this.applyMatrix4(hi),this}translate(e,t,n){return hi.makeTranslation(e,t,n),this.applyMatrix4(hi),this}scale(e,t,n){return hi.makeScale(e,t,n),this.applyMatrix4(hi),this}lookAt(e){return Hu.lookAt(e),Hu.updateMatrix(),this.applyMatrix4(Hu.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Os).negate(),this.translate(Os.x,Os.y,Os.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let i=0,s=e.length;i<s;i++){const a=e[i];n.push(a.x,a.y,a.z||0)}this.setAttribute("position",new $t(n,3))}else{for(let n=0,i=t.count;n<i;n++){const s=e[n];t.setXYZ(n,s.x,s.y,s.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Mi);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new N(-1/0,-1/0,-1/0),new N(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){const s=t[n];oi.setFromBufferAttribute(s),this.morphTargetsRelative?(Sn.addVectors(this.boundingBox.min,oi.min),this.boundingBox.expandByPoint(Sn),Sn.addVectors(this.boundingBox.max,oi.max),this.boundingBox.expandByPoint(Sn)):(this.boundingBox.expandByPoint(oi.min),this.boundingBox.expandByPoint(oi.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Ii);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new N,1/0);return}if(e){const n=this.boundingSphere.center;if(oi.setFromBufferAttribute(e),t)for(let s=0,a=t.length;s<a;s++){const c=t[s];Oo.setFromBufferAttribute(c),this.morphTargetsRelative?(Sn.addVectors(oi.min,Oo.min),oi.expandByPoint(Sn),Sn.addVectors(oi.max,Oo.max),oi.expandByPoint(Sn)):(oi.expandByPoint(Oo.min),oi.expandByPoint(Oo.max))}oi.getCenter(n);let i=0;for(let s=0,a=e.count;s<a;s++)Sn.fromBufferAttribute(e,s),i=Math.max(i,n.distanceToSquared(Sn));if(t)for(let s=0,a=t.length;s<a;s++){const c=t[s],u=this.morphTargetsRelative;for(let h=0,f=c.count;h<f;h++)Sn.fromBufferAttribute(c,h),u&&(Os.fromBufferAttribute(e,h),Sn.add(Os)),i=Math.max(i,n.distanceToSquared(Sn))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,i=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new ln(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),c=[],u=[];for(let V=0;V<n.count;V++)c[V]=new N,u[V]=new N;const h=new N,f=new N,p=new N,m=new lt,g=new lt,x=new lt,E=new N,v=new N;function _(V,I,R){h.fromBufferAttribute(n,V),f.fromBufferAttribute(n,I),p.fromBufferAttribute(n,R),m.fromBufferAttribute(s,V),g.fromBufferAttribute(s,I),x.fromBufferAttribute(s,R),f.sub(h),p.sub(h),g.sub(m),x.sub(m);const H=1/(g.x*x.y-x.x*g.y);isFinite(H)&&(E.copy(f).multiplyScalar(x.y).addScaledVector(p,-g.y).multiplyScalar(H),v.copy(p).multiplyScalar(g.x).addScaledVector(f,-x.x).multiplyScalar(H),c[V].add(E),c[I].add(E),c[R].add(E),u[V].add(v),u[I].add(v),u[R].add(v))}let A=this.groups;A.length===0&&(A=[{start:0,count:e.count}]);for(let V=0,I=A.length;V<I;++V){const R=A[V],H=R.start,ee=R.count;for(let te=H,se=H+ee;te<se;te+=3)_(e.getX(te+0),e.getX(te+1),e.getX(te+2))}const w=new N,b=new N,B=new N,U=new N;function O(V){B.fromBufferAttribute(i,V),U.copy(B);const I=c[V];w.copy(I),w.sub(B.multiplyScalar(B.dot(I))).normalize(),b.crossVectors(U,I);const H=b.dot(u[V])<0?-1:1;a.setXYZW(V,w.x,w.y,w.z,H)}for(let V=0,I=A.length;V<I;++V){const R=A[V],H=R.start,ee=R.count;for(let te=H,se=H+ee;te<se;te+=3)O(e.getX(te+0)),O(e.getX(te+1)),O(e.getX(te+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new ln(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let m=0,g=n.count;m<g;m++)n.setXYZ(m,0,0,0);const i=new N,s=new N,a=new N,c=new N,u=new N,h=new N,f=new N,p=new N;if(e)for(let m=0,g=e.count;m<g;m+=3){const x=e.getX(m+0),E=e.getX(m+1),v=e.getX(m+2);i.fromBufferAttribute(t,x),s.fromBufferAttribute(t,E),a.fromBufferAttribute(t,v),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),c.fromBufferAttribute(n,x),u.fromBufferAttribute(n,E),h.fromBufferAttribute(n,v),c.add(f),u.add(f),h.add(f),n.setXYZ(x,c.x,c.y,c.z),n.setXYZ(E,u.x,u.y,u.z),n.setXYZ(v,h.x,h.y,h.z)}else for(let m=0,g=t.count;m<g;m+=3)i.fromBufferAttribute(t,m+0),s.fromBufferAttribute(t,m+1),a.fromBufferAttribute(t,m+2),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),n.setXYZ(m+0,f.x,f.y,f.z),n.setXYZ(m+1,f.x,f.y,f.z),n.setXYZ(m+2,f.x,f.y,f.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)Sn.fromBufferAttribute(e,t),Sn.normalize(),e.setXYZ(t,Sn.x,Sn.y,Sn.z)}toNonIndexed(){function e(c,u){const h=c.array,f=c.itemSize,p=c.normalized,m=new h.constructor(u.length*f);let g=0,x=0;for(let E=0,v=u.length;E<v;E++){c.isInterleavedBufferAttribute?g=u[E]*c.data.stride+c.offset:g=u[E]*f;for(let _=0;_<f;_++)m[x++]=h[g++]}return new ln(m,f,p)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new _n,n=this.index.array,i=this.attributes;for(const c in i){const u=i[c],h=e(u,n);t.setAttribute(c,h)}const s=this.morphAttributes;for(const c in s){const u=[],h=s[c];for(let f=0,p=h.length;f<p;f++){const m=h[f],g=e(m,n);u.push(g)}t.morphAttributes[c]=u}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];t.addGroup(h.start,h.count,h.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const u=this.parameters;for(const h in u)u[h]!==void 0&&(e[h]=u[h]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const u in n){const h=n[u];e.data.attributes[u]=h.toJSON(e.data)}const i={};let s=!1;for(const u in this.morphAttributes){const h=this.morphAttributes[u],f=[];for(let p=0,m=h.length;p<m;p++){const g=h[p];f.push(g.toJSON(e.data))}f.length>0&&(i[u]=f,s=!0)}s&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const c=this.boundingSphere;return c!==null&&(e.data.boundingSphere={center:c.center.toArray(),radius:c.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const i=e.attributes;for(const h in i){const f=i[h];this.setAttribute(h,f.clone(t))}const s=e.morphAttributes;for(const h in s){const f=[],p=s[h];for(let m=0,g=p.length;m<g;m++)f.push(p[m].clone(t));this.morphAttributes[h]=f}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let h=0,f=a.length;h<f;h++){const p=a[h];this.addGroup(p.start,p.count,p.materialIndex)}const c=e.boundingBox;c!==null&&(this.boundingBox=c.clone());const u=e.boundingSphere;return u!==null&&(this.boundingSphere=u.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Kp=new ft,Qr=new co,ec=new Ii,$p=new N,tc=new N,nc=new N,ic=new N,Vu=new N,rc=new N,Zp=new N,sc=new N;class Re extends tn{constructor(e=new _n,t=new pi){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}getVertexPosition(e,t){const n=this.geometry,i=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(i,e);const c=this.morphTargetInfluences;if(s&&c){rc.set(0,0,0);for(let u=0,h=s.length;u<h;u++){const f=c[u],p=s[u];f!==0&&(Vu.fromBufferAttribute(p,e),a?rc.addScaledVector(Vu,f):rc.addScaledVector(Vu.sub(t),f))}t.add(rc)}return t}raycast(e,t){const n=this.geometry,i=this.material,s=this.matrixWorld;i!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),ec.copy(n.boundingSphere),ec.applyMatrix4(s),Qr.copy(e.ray).recast(e.near),!(ec.containsPoint(Qr.origin)===!1&&(Qr.intersectSphere(ec,$p)===null||Qr.origin.distanceToSquared($p)>(e.far-e.near)**2))&&(Kp.copy(s).invert(),Qr.copy(e.ray).applyMatrix4(Kp),!(n.boundingBox!==null&&Qr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Qr)))}_computeIntersections(e,t,n){let i;const s=this.geometry,a=this.material,c=s.index,u=s.attributes.position,h=s.attributes.uv,f=s.attributes.uv1,p=s.attributes.normal,m=s.groups,g=s.drawRange;if(c!==null)if(Array.isArray(a))for(let x=0,E=m.length;x<E;x++){const v=m[x],_=a[v.materialIndex],A=Math.max(v.start,g.start),w=Math.min(c.count,Math.min(v.start+v.count,g.start+g.count));for(let b=A,B=w;b<B;b+=3){const U=c.getX(b),O=c.getX(b+1),V=c.getX(b+2);i=oc(this,_,e,n,h,f,p,U,O,V),i&&(i.faceIndex=Math.floor(b/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),E=Math.min(c.count,g.start+g.count);for(let v=x,_=E;v<_;v+=3){const A=c.getX(v),w=c.getX(v+1),b=c.getX(v+2);i=oc(this,a,e,n,h,f,p,A,w,b),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}else if(u!==void 0)if(Array.isArray(a))for(let x=0,E=m.length;x<E;x++){const v=m[x],_=a[v.materialIndex],A=Math.max(v.start,g.start),w=Math.min(u.count,Math.min(v.start+v.count,g.start+g.count));for(let b=A,B=w;b<B;b+=3){const U=b,O=b+1,V=b+2;i=oc(this,_,e,n,h,f,p,U,O,V),i&&(i.faceIndex=Math.floor(b/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),E=Math.min(u.count,g.start+g.count);for(let v=x,_=E;v<_;v+=3){const A=v,w=v+1,b=v+2;i=oc(this,a,e,n,h,f,p,A,w,b),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}}}function LT(r,e,t,n,i,s,a,c){let u;if(e.side===$n?u=n.intersectTriangle(a,s,i,!0,c):u=n.intersectTriangle(i,s,a,e.side===nr,c),u===null)return null;sc.copy(c),sc.applyMatrix4(r.matrixWorld);const h=t.ray.origin.distanceTo(sc);return h<t.near||h>t.far?null:{distance:h,point:sc.clone(),object:r}}function oc(r,e,t,n,i,s,a,c,u,h){r.getVertexPosition(c,tc),r.getVertexPosition(u,nc),r.getVertexPosition(h,ic);const f=LT(r,e,t,n,tc,nc,ic,Zp);if(f){const p=new N;bi.getBarycoord(Zp,tc,nc,ic,p),i&&(f.uv=bi.getInterpolatedAttribute(i,c,u,h,p,new lt)),s&&(f.uv1=bi.getInterpolatedAttribute(s,c,u,h,p,new lt)),a&&(f.normal=bi.getInterpolatedAttribute(a,c,u,h,p,new N),f.normal.dot(n.direction)>0&&f.normal.multiplyScalar(-1));const m={a:c,b:u,c:h,normal:new N,materialIndex:0};bi.getNormal(tc,nc,ic,m.normal),f.face=m,f.barycoord=p}return f}class an extends _n{constructor(e=1,t=1,n=1,i=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:s,depthSegments:a};const c=this;i=Math.floor(i),s=Math.floor(s),a=Math.floor(a);const u=[],h=[],f=[],p=[];let m=0,g=0;x("z","y","x",-1,-1,n,t,e,a,s,0),x("z","y","x",1,-1,n,t,-e,a,s,1),x("x","z","y",1,1,e,n,t,i,a,2),x("x","z","y",1,-1,e,n,-t,i,a,3),x("x","y","z",1,-1,e,t,n,i,s,4),x("x","y","z",-1,-1,e,t,-n,i,s,5),this.setIndex(u),this.setAttribute("position",new $t(h,3)),this.setAttribute("normal",new $t(f,3)),this.setAttribute("uv",new $t(p,2));function x(E,v,_,A,w,b,B,U,O,V,I){const R=b/O,H=B/V,ee=b/2,te=B/2,se=U/2,he=O+1,q=V+1;let de=0,re=0;const ge=new N;for(let be=0;be<q;be++){const ze=be*H-te;for(let Ge=0;Ge<he;Ge++){const pt=Ge*R-ee;ge[E]=pt*A,ge[v]=ze*w,ge[_]=se,h.push(ge.x,ge.y,ge.z),ge[E]=0,ge[v]=0,ge[_]=U>0?1:-1,f.push(ge.x,ge.y,ge.z),p.push(Ge/O),p.push(1-be/V),de+=1}}for(let be=0;be<V;be++)for(let ze=0;ze<O;ze++){const Ge=m+ze+he*be,pt=m+ze+he*(be+1),le=m+(ze+1)+he*(be+1),me=m+(ze+1)+he*be;u.push(Ge,pt,me),u.push(pt,le,me),re+=6}c.addGroup(g,re,I),g+=re,m+=de}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new an(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function ro(r){const e={};for(const t in r){e[t]={};for(const n in r[t]){const i=r[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?i.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}function Hn(r){const e={};for(let t=0;t<r.length;t++){const n=ro(r[t]);for(const i in n)e[i]=n[i]}return e}function FT(r){const e=[];for(let t=0;t<r.length;t++)e.push(r[t].clone());return e}function Fg(r){const e=r.getRenderTarget();return e===null?r.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:Ct.workingColorSpace}const NT={clone:ro,merge:Hn};var OT=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,UT=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Tr extends Di{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=OT,this.fragmentShader=UT,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=ro(e.uniforms),this.uniformsGroups=FT(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const i in this.uniforms){const a=this.uniforms[i].value;a&&a.isTexture?t.uniforms[i]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[i]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[i]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[i]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[i]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[i]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[i]={type:"m4",value:a.toArray()}:t.uniforms[i]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Ng extends tn{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new ft,this.projectionMatrix=new ft,this.projectionMatrixInverse=new ft,this.coordinateSystem=Ji}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const mr=new N,Qp=new lt,Jp=new lt;class Vn extends Ng{constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=io*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan($o*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return io*2*Math.atan(Math.tan($o*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){mr.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(mr.x,mr.y).multiplyScalar(-e/mr.z),mr.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(mr.x,mr.y).multiplyScalar(-e/mr.z)}getViewSize(e,t){return this.getViewBounds(e,Qp,Jp),t.subVectors(Jp,Qp)}setViewOffset(e,t,n,i,s,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan($o*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,s=-.5*i;const a=this.view;if(this.view!==null&&this.view.enabled){const u=a.fullWidth,h=a.fullHeight;s+=a.offsetX*i/u,t-=a.offsetY*n/h,i*=a.width/u,n*=a.height/h}const c=this.filmOffset;c!==0&&(s+=e*c/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+i,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Us=-90,Bs=1;class BT extends tn{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const i=new Vn(Us,Bs,e,t);i.layers=this.layers,this.add(i);const s=new Vn(Us,Bs,e,t);s.layers=this.layers,this.add(s);const a=new Vn(Us,Bs,e,t);a.layers=this.layers,this.add(a);const c=new Vn(Us,Bs,e,t);c.layers=this.layers,this.add(c);const u=new Vn(Us,Bs,e,t);u.layers=this.layers,this.add(u);const h=new Vn(Us,Bs,e,t);h.layers=this.layers,this.add(h)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,i,s,a,c,u]=t;for(const h of t)this.remove(h);if(e===Ji)n.up.set(0,1,0),n.lookAt(1,0,0),i.up.set(0,1,0),i.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),c.up.set(0,1,0),c.lookAt(0,0,1),u.up.set(0,1,0),u.lookAt(0,0,-1);else if(e===Oc)n.up.set(0,-1,0),n.lookAt(-1,0,0),i.up.set(0,-1,0),i.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),c.up.set(0,-1,0),c.lookAt(0,0,1),u.up.set(0,-1,0),u.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const h of t)this.add(h),h.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:i}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,a,c,u,h,f]=this.children,p=e.getRenderTarget(),m=e.getActiveCubeFace(),g=e.getActiveMipmapLevel(),x=e.xr.enabled;e.xr.enabled=!1;const E=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,i),e.render(t,s),e.setRenderTarget(n,1,i),e.render(t,a),e.setRenderTarget(n,2,i),e.render(t,c),e.setRenderTarget(n,3,i),e.render(t,u),e.setRenderTarget(n,4,i),e.render(t,h),n.texture.generateMipmaps=E,e.setRenderTarget(n,5,i),e.render(t,f),e.setRenderTarget(p,m,g),e.xr.enabled=x,n.texture.needsPMREMUpdate=!0}}class Og extends Mn{constructor(e,t,n,i,s,a,c,u,h,f){e=e!==void 0?e:[],t=t!==void 0?t:Qs,super(e,t,n,i,s,a,c,u,h,f),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class kT extends us{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new Og(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ai}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},i=new an(5,5,5),s=new Tr({name:"CubemapFromEquirect",uniforms:ro(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:$n,blending:Er});s.uniforms.tEquirect.value=t;const a=new Re(i,s),c=t.minFilter;return t.minFilter===Qi&&(t.minFilter=ai),new BT(1,10,this).update(e,a),t.minFilter=c,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,i){const s=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,i);e.setRenderTarget(s)}}const Gu=new N,zT=new N,HT=new yt;class yr{constructor(e=new N(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const i=Gu.subVectors(n,t).cross(zT.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Gu),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/i;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||HT.getNormalMatrix(e),i=this.coplanarPoint(Gu).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Jr=new Ii,ac=new N;class xd{constructor(e=new yr,t=new yr,n=new yr,i=new yr,s=new yr,a=new yr){this.planes=[e,t,n,i,s,a]}set(e,t,n,i,s,a){const c=this.planes;return c[0].copy(e),c[1].copy(t),c[2].copy(n),c[3].copy(i),c[4].copy(s),c[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Ji){const n=this.planes,i=e.elements,s=i[0],a=i[1],c=i[2],u=i[3],h=i[4],f=i[5],p=i[6],m=i[7],g=i[8],x=i[9],E=i[10],v=i[11],_=i[12],A=i[13],w=i[14],b=i[15];if(n[0].setComponents(u-s,m-h,v-g,b-_).normalize(),n[1].setComponents(u+s,m+h,v+g,b+_).normalize(),n[2].setComponents(u+a,m+f,v+x,b+A).normalize(),n[3].setComponents(u-a,m-f,v-x,b-A).normalize(),n[4].setComponents(u-c,m-p,v-E,b-w).normalize(),t===Ji)n[5].setComponents(u+c,m+p,v+E,b+w).normalize();else if(t===Oc)n[5].setComponents(c,p,E,w).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Jr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Jr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Jr)}intersectsSprite(e){return Jr.center.set(0,0,0),Jr.radius=.7071067811865476,Jr.applyMatrix4(e.matrixWorld),this.intersectsSphere(Jr)}intersectsSphere(e){const t=this.planes,n=e.center,i=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const i=t[n];if(ac.x=i.normal.x>0?e.max.x:e.min.x,ac.y=i.normal.y>0?e.max.y:e.min.y,ac.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(ac)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Ug(){let r=null,e=!1,t=null,n=null;function i(s,a){t(s,a),n=r.requestAnimationFrame(i)}return{start:function(){e!==!0&&t!==null&&(n=r.requestAnimationFrame(i),e=!0)},stop:function(){r.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){r=s}}}function VT(r){const e=new WeakMap;function t(c,u){const h=c.array,f=c.usage,p=h.byteLength,m=r.createBuffer();r.bindBuffer(u,m),r.bufferData(u,h,f),c.onUploadCallback();let g;if(h instanceof Float32Array)g=r.FLOAT;else if(h instanceof Uint16Array)c.isFloat16BufferAttribute?g=r.HALF_FLOAT:g=r.UNSIGNED_SHORT;else if(h instanceof Int16Array)g=r.SHORT;else if(h instanceof Uint32Array)g=r.UNSIGNED_INT;else if(h instanceof Int32Array)g=r.INT;else if(h instanceof Int8Array)g=r.BYTE;else if(h instanceof Uint8Array)g=r.UNSIGNED_BYTE;else if(h instanceof Uint8ClampedArray)g=r.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+h);return{buffer:m,type:g,bytesPerElement:h.BYTES_PER_ELEMENT,version:c.version,size:p}}function n(c,u,h){const f=u.array,p=u.updateRanges;if(r.bindBuffer(h,c),p.length===0)r.bufferSubData(h,0,f);else{p.sort((g,x)=>g.start-x.start);let m=0;for(let g=1;g<p.length;g++){const x=p[m],E=p[g];E.start<=x.start+x.count+1?x.count=Math.max(x.count,E.start+E.count-x.start):(++m,p[m]=E)}p.length=m+1;for(let g=0,x=p.length;g<x;g++){const E=p[g];r.bufferSubData(h,E.start*f.BYTES_PER_ELEMENT,f,E.start,E.count)}u.clearUpdateRanges()}u.onUploadCallback()}function i(c){return c.isInterleavedBufferAttribute&&(c=c.data),e.get(c)}function s(c){c.isInterleavedBufferAttribute&&(c=c.data);const u=e.get(c);u&&(r.deleteBuffer(u.buffer),e.delete(c))}function a(c,u){if(c.isInterleavedBufferAttribute&&(c=c.data),c.isGLBufferAttribute){const f=e.get(c);(!f||f.version<c.version)&&e.set(c,{buffer:c.buffer,type:c.type,bytesPerElement:c.elementSize,version:c.version});return}const h=e.get(c);if(h===void 0)e.set(c,t(c,u));else if(h.version<c.version){if(h.size!==c.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(h.buffer,c,u),h.version=c.version}}return{get:i,remove:s,update:a}}class lo extends _n{constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};const s=e/2,a=t/2,c=Math.floor(n),u=Math.floor(i),h=c+1,f=u+1,p=e/c,m=t/u,g=[],x=[],E=[],v=[];for(let _=0;_<f;_++){const A=_*m-a;for(let w=0;w<h;w++){const b=w*p-s;x.push(b,-A,0),E.push(0,0,1),v.push(w/c),v.push(1-_/u)}}for(let _=0;_<u;_++)for(let A=0;A<c;A++){const w=A+h*_,b=A+h*(_+1),B=A+1+h*(_+1),U=A+1+h*_;g.push(w,b,U),g.push(b,B,U)}this.setIndex(g),this.setAttribute("position",new $t(x,3)),this.setAttribute("normal",new $t(E,3)),this.setAttribute("uv",new $t(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new lo(e.width,e.height,e.widthSegments,e.heightSegments)}}var GT=`#ifdef USE_ALPHAHASH
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
}`,St={alphahash_fragment:GT,alphahash_pars_fragment:WT,alphamap_fragment:jT,alphamap_pars_fragment:XT,alphatest_fragment:qT,alphatest_pars_fragment:YT,aomap_fragment:KT,aomap_pars_fragment:$T,batching_pars_vertex:ZT,batching_vertex:QT,begin_vertex:JT,beginnormal_vertex:ew,bsdfs:tw,iridescence_fragment:nw,bumpmap_pars_fragment:iw,clipping_planes_fragment:rw,clipping_planes_pars_fragment:sw,clipping_planes_pars_vertex:ow,clipping_planes_vertex:aw,color_fragment:cw,color_pars_fragment:lw,color_pars_vertex:uw,color_vertex:hw,common:dw,cube_uv_reflection_fragment:fw,defaultnormal_vertex:pw,displacementmap_pars_vertex:mw,displacementmap_vertex:gw,emissivemap_fragment:_w,emissivemap_pars_fragment:vw,colorspace_fragment:yw,colorspace_pars_fragment:xw,envmap_fragment:bw,envmap_common_pars_fragment:Sw,envmap_pars_fragment:Ew,envmap_pars_vertex:Mw,envmap_physical_pars_fragment:Nw,envmap_vertex:Tw,fog_vertex:ww,fog_pars_vertex:Aw,fog_fragment:Rw,fog_pars_fragment:Pw,gradientmap_pars_fragment:Cw,lightmap_pars_fragment:Dw,lights_lambert_fragment:Iw,lights_lambert_pars_fragment:Lw,lights_pars_begin:Fw,lights_toon_fragment:Ow,lights_toon_pars_fragment:Uw,lights_phong_fragment:Bw,lights_phong_pars_fragment:kw,lights_physical_fragment:zw,lights_physical_pars_fragment:Hw,lights_fragment_begin:Vw,lights_fragment_maps:Gw,lights_fragment_end:Ww,logdepthbuf_fragment:jw,logdepthbuf_pars_fragment:Xw,logdepthbuf_pars_vertex:qw,logdepthbuf_vertex:Yw,map_fragment:Kw,map_pars_fragment:$w,map_particle_fragment:Zw,map_particle_pars_fragment:Qw,metalnessmap_fragment:Jw,metalnessmap_pars_fragment:eA,morphinstance_vertex:tA,morphcolor_vertex:nA,morphnormal_vertex:iA,morphtarget_pars_vertex:rA,morphtarget_vertex:sA,normal_fragment_begin:oA,normal_fragment_maps:aA,normal_pars_fragment:cA,normal_pars_vertex:lA,normal_vertex:uA,normalmap_pars_fragment:hA,clearcoat_normal_fragment_begin:dA,clearcoat_normal_fragment_maps:fA,clearcoat_pars_fragment:pA,iridescence_pars_fragment:mA,opaque_fragment:gA,packing:_A,premultiplied_alpha_fragment:vA,project_vertex:yA,dithering_fragment:xA,dithering_pars_fragment:bA,roughnessmap_fragment:SA,roughnessmap_pars_fragment:EA,shadowmap_pars_fragment:MA,shadowmap_pars_vertex:TA,shadowmap_vertex:wA,shadowmask_pars_fragment:AA,skinbase_vertex:RA,skinning_pars_vertex:PA,skinning_vertex:CA,skinnormal_vertex:DA,specularmap_fragment:IA,specularmap_pars_fragment:LA,tonemapping_fragment:FA,tonemapping_pars_fragment:NA,transmission_fragment:OA,transmission_pars_fragment:UA,uv_pars_fragment:BA,uv_pars_vertex:kA,uv_vertex:zA,worldpos_vertex:HA,background_vert:VA,background_frag:GA,backgroundCube_vert:WA,backgroundCube_frag:jA,cube_vert:XA,cube_frag:qA,depth_vert:YA,depth_frag:KA,distanceRGBA_vert:$A,distanceRGBA_frag:ZA,equirect_vert:QA,equirect_frag:JA,linedashed_vert:e1,linedashed_frag:t1,meshbasic_vert:n1,meshbasic_frag:i1,meshlambert_vert:r1,meshlambert_frag:s1,meshmatcap_vert:o1,meshmatcap_frag:a1,meshnormal_vert:c1,meshnormal_frag:l1,meshphong_vert:u1,meshphong_frag:h1,meshphysical_vert:d1,meshphysical_frag:f1,meshtoon_vert:p1,meshtoon_frag:m1,points_vert:g1,points_frag:_1,shadow_vert:v1,shadow_frag:y1,sprite_vert:x1,sprite_frag:b1},Ie={common:{diffuse:{value:new st(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new yt},alphaMap:{value:null},alphaMapTransform:{value:new yt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new yt}},envmap:{envMap:{value:null},envMapRotation:{value:new yt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new yt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new yt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new yt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new yt},normalScale:{value:new lt(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new yt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new yt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new yt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new yt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new st(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new st(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new yt},alphaTest:{value:0},uvTransform:{value:new yt}},sprite:{diffuse:{value:new st(16777215)},opacity:{value:1},center:{value:new lt(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new yt},alphaMap:{value:null},alphaMapTransform:{value:new yt},alphaTest:{value:0}}},Pi={basic:{uniforms:Hn([Ie.common,Ie.specularmap,Ie.envmap,Ie.aomap,Ie.lightmap,Ie.fog]),vertexShader:St.meshbasic_vert,fragmentShader:St.meshbasic_frag},lambert:{uniforms:Hn([Ie.common,Ie.specularmap,Ie.envmap,Ie.aomap,Ie.lightmap,Ie.emissivemap,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.fog,Ie.lights,{emissive:{value:new st(0)}}]),vertexShader:St.meshlambert_vert,fragmentShader:St.meshlambert_frag},phong:{uniforms:Hn([Ie.common,Ie.specularmap,Ie.envmap,Ie.aomap,Ie.lightmap,Ie.emissivemap,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.fog,Ie.lights,{emissive:{value:new st(0)},specular:{value:new st(1118481)},shininess:{value:30}}]),vertexShader:St.meshphong_vert,fragmentShader:St.meshphong_frag},standard:{uniforms:Hn([Ie.common,Ie.envmap,Ie.aomap,Ie.lightmap,Ie.emissivemap,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.roughnessmap,Ie.metalnessmap,Ie.fog,Ie.lights,{emissive:{value:new st(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:St.meshphysical_vert,fragmentShader:St.meshphysical_frag},toon:{uniforms:Hn([Ie.common,Ie.aomap,Ie.lightmap,Ie.emissivemap,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.gradientmap,Ie.fog,Ie.lights,{emissive:{value:new st(0)}}]),vertexShader:St.meshtoon_vert,fragmentShader:St.meshtoon_frag},matcap:{uniforms:Hn([Ie.common,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,Ie.fog,{matcap:{value:null}}]),vertexShader:St.meshmatcap_vert,fragmentShader:St.meshmatcap_frag},points:{uniforms:Hn([Ie.points,Ie.fog]),vertexShader:St.points_vert,fragmentShader:St.points_frag},dashed:{uniforms:Hn([Ie.common,Ie.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:St.linedashed_vert,fragmentShader:St.linedashed_frag},depth:{uniforms:Hn([Ie.common,Ie.displacementmap]),vertexShader:St.depth_vert,fragmentShader:St.depth_frag},normal:{uniforms:Hn([Ie.common,Ie.bumpmap,Ie.normalmap,Ie.displacementmap,{opacity:{value:1}}]),vertexShader:St.meshnormal_vert,fragmentShader:St.meshnormal_frag},sprite:{uniforms:Hn([Ie.sprite,Ie.fog]),vertexShader:St.sprite_vert,fragmentShader:St.sprite_frag},background:{uniforms:{uvTransform:{value:new yt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:St.background_vert,fragmentShader:St.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new yt}},vertexShader:St.backgroundCube_vert,fragmentShader:St.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:St.cube_vert,fragmentShader:St.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:St.equirect_vert,fragmentShader:St.equirect_frag},distanceRGBA:{uniforms:Hn([Ie.common,Ie.displacementmap,{referencePosition:{value:new N},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:St.distanceRGBA_vert,fragmentShader:St.distanceRGBA_frag},shadow:{uniforms:Hn([Ie.lights,Ie.fog,{color:{value:new st(0)},opacity:{value:1}}]),vertexShader:St.shadow_vert,fragmentShader:St.shadow_frag}};Pi.physical={uniforms:Hn([Pi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new yt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new yt},clearcoatNormalScale:{value:new lt(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new yt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new yt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new yt},sheen:{value:0},sheenColor:{value:new st(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new yt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new yt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new yt},transmissionSamplerSize:{value:new lt},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new yt},attenuationDistance:{value:0},attenuationColor:{value:new st(0)},specularColor:{value:new st(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new yt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new yt},anisotropyVector:{value:new lt},anisotropyMap:{value:null},anisotropyMapTransform:{value:new yt}}]),vertexShader:St.meshphysical_vert,fragmentShader:St.meshphysical_frag};const cc={r:0,b:0,g:0},es=new Ti,S1=new ft;function E1(r,e,t,n,i,s,a){const c=new st(0);let u=s===!0?0:1,h,f,p=null,m=0,g=null;function x(A){let w=A.isScene===!0?A.background:null;return w&&w.isTexture&&(w=(A.backgroundBlurriness>0?t:e).get(w)),w}function E(A){let w=!1;const b=x(A);b===null?_(c,u):b&&b.isColor&&(_(b,1),w=!0);const B=r.xr.getEnvironmentBlendMode();B==="additive"?n.buffers.color.setClear(0,0,0,1,a):B==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(r.autoClear||w)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),r.clear(r.autoClearColor,r.autoClearDepth,r.autoClearStencil))}function v(A,w){const b=x(w);b&&(b.isCubeTexture||b.mapping===kc)?(f===void 0&&(f=new Re(new an(1,1,1),new Tr({name:"BackgroundCubeMaterial",uniforms:ro(Pi.backgroundCube.uniforms),vertexShader:Pi.backgroundCube.vertexShader,fragmentShader:Pi.backgroundCube.fragmentShader,side:$n,depthTest:!1,depthWrite:!1,fog:!1})),f.geometry.deleteAttribute("normal"),f.geometry.deleteAttribute("uv"),f.onBeforeRender=function(B,U,O){this.matrixWorld.copyPosition(O.matrixWorld)},Object.defineProperty(f.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(f)),es.copy(w.backgroundRotation),es.x*=-1,es.y*=-1,es.z*=-1,b.isCubeTexture&&b.isRenderTargetTexture===!1&&(es.y*=-1,es.z*=-1),f.material.uniforms.envMap.value=b,f.material.uniforms.flipEnvMap.value=b.isCubeTexture&&b.isRenderTargetTexture===!1?-1:1,f.material.uniforms.backgroundBlurriness.value=w.backgroundBlurriness,f.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,f.material.uniforms.backgroundRotation.value.setFromMatrix4(S1.makeRotationFromEuler(es)),f.material.toneMapped=Ct.getTransfer(b.colorSpace)!==Gt,(p!==b||m!==b.version||g!==r.toneMapping)&&(f.material.needsUpdate=!0,p=b,m=b.version,g=r.toneMapping),f.layers.enableAll(),A.unshift(f,f.geometry,f.material,0,0,null)):b&&b.isTexture&&(h===void 0&&(h=new Re(new lo(2,2),new Tr({name:"BackgroundMaterial",uniforms:ro(Pi.background.uniforms),vertexShader:Pi.background.vertexShader,fragmentShader:Pi.background.fragmentShader,side:nr,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),Object.defineProperty(h.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(h)),h.material.uniforms.t2D.value=b,h.material.uniforms.backgroundIntensity.value=w.backgroundIntensity,h.material.toneMapped=Ct.getTransfer(b.colorSpace)!==Gt,b.matrixAutoUpdate===!0&&b.updateMatrix(),h.material.uniforms.uvTransform.value.copy(b.matrix),(p!==b||m!==b.version||g!==r.toneMapping)&&(h.material.needsUpdate=!0,p=b,m=b.version,g=r.toneMapping),h.layers.enableAll(),A.unshift(h,h.geometry,h.material,0,0,null))}function _(A,w){A.getRGB(cc,Fg(r)),n.buffers.color.setClear(cc.r,cc.g,cc.b,w,a)}return{getClearColor:function(){return c},setClearColor:function(A,w=1){c.set(A),u=w,_(c,u)},getClearAlpha:function(){return u},setClearAlpha:function(A){u=A,_(c,u)},render:E,addToRenderList:v}}function M1(r,e){const t=r.getParameter(r.MAX_VERTEX_ATTRIBS),n={},i=m(null);let s=i,a=!1;function c(R,H,ee,te,se){let he=!1;const q=p(te,ee,H);s!==q&&(s=q,h(s.object)),he=g(R,te,ee,se),he&&x(R,te,ee,se),se!==null&&e.update(se,r.ELEMENT_ARRAY_BUFFER),(he||a)&&(a=!1,b(R,H,ee,te),se!==null&&r.bindBuffer(r.ELEMENT_ARRAY_BUFFER,e.get(se).buffer))}function u(){return r.createVertexArray()}function h(R){return r.bindVertexArray(R)}function f(R){return r.deleteVertexArray(R)}function p(R,H,ee){const te=ee.wireframe===!0;let se=n[R.id];se===void 0&&(se={},n[R.id]=se);let he=se[H.id];he===void 0&&(he={},se[H.id]=he);let q=he[te];return q===void 0&&(q=m(u()),he[te]=q),q}function m(R){const H=[],ee=[],te=[];for(let se=0;se<t;se++)H[se]=0,ee[se]=0,te[se]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:H,enabledAttributes:ee,attributeDivisors:te,object:R,attributes:{},index:null}}function g(R,H,ee,te){const se=s.attributes,he=H.attributes;let q=0;const de=ee.getAttributes();for(const re in de)if(de[re].location>=0){const be=se[re];let ze=he[re];if(ze===void 0&&(re==="instanceMatrix"&&R.instanceMatrix&&(ze=R.instanceMatrix),re==="instanceColor"&&R.instanceColor&&(ze=R.instanceColor)),be===void 0||be.attribute!==ze||ze&&be.data!==ze.data)return!0;q++}return s.attributesNum!==q||s.index!==te}function x(R,H,ee,te){const se={},he=H.attributes;let q=0;const de=ee.getAttributes();for(const re in de)if(de[re].location>=0){let be=he[re];be===void 0&&(re==="instanceMatrix"&&R.instanceMatrix&&(be=R.instanceMatrix),re==="instanceColor"&&R.instanceColor&&(be=R.instanceColor));const ze={};ze.attribute=be,be&&be.data&&(ze.data=be.data),se[re]=ze,q++}s.attributes=se,s.attributesNum=q,s.index=te}function E(){const R=s.newAttributes;for(let H=0,ee=R.length;H<ee;H++)R[H]=0}function v(R){_(R,0)}function _(R,H){const ee=s.newAttributes,te=s.enabledAttributes,se=s.attributeDivisors;ee[R]=1,te[R]===0&&(r.enableVertexAttribArray(R),te[R]=1),se[R]!==H&&(r.vertexAttribDivisor(R,H),se[R]=H)}function A(){const R=s.newAttributes,H=s.enabledAttributes;for(let ee=0,te=H.length;ee<te;ee++)H[ee]!==R[ee]&&(r.disableVertexAttribArray(ee),H[ee]=0)}function w(R,H,ee,te,se,he,q){q===!0?r.vertexAttribIPointer(R,H,ee,se,he):r.vertexAttribPointer(R,H,ee,te,se,he)}function b(R,H,ee,te){E();const se=te.attributes,he=ee.getAttributes(),q=H.defaultAttributeValues;for(const de in he){const re=he[de];if(re.location>=0){let ge=se[de];if(ge===void 0&&(de==="instanceMatrix"&&R.instanceMatrix&&(ge=R.instanceMatrix),de==="instanceColor"&&R.instanceColor&&(ge=R.instanceColor)),ge!==void 0){const be=ge.normalized,ze=ge.itemSize,Ge=e.get(ge);if(Ge===void 0)continue;const pt=Ge.buffer,le=Ge.type,me=Ge.bytesPerElement,Ue=le===r.INT||le===r.UNSIGNED_INT||ge.gpuType===ld;if(ge.isInterleavedBufferAttribute){const Se=ge.data,$e=Se.stride,it=ge.offset;if(Se.isInstancedInterleavedBuffer){for(let Je=0;Je<re.locationSize;Je++)_(re.location+Je,Se.meshPerAttribute);R.isInstancedMesh!==!0&&te._maxInstanceCount===void 0&&(te._maxInstanceCount=Se.meshPerAttribute*Se.count)}else for(let Je=0;Je<re.locationSize;Je++)v(re.location+Je);r.bindBuffer(r.ARRAY_BUFFER,pt);for(let Je=0;Je<re.locationSize;Je++)w(re.location+Je,ze/re.locationSize,le,be,$e*me,(it+ze/re.locationSize*Je)*me,Ue)}else{if(ge.isInstancedBufferAttribute){for(let Se=0;Se<re.locationSize;Se++)_(re.location+Se,ge.meshPerAttribute);R.isInstancedMesh!==!0&&te._maxInstanceCount===void 0&&(te._maxInstanceCount=ge.meshPerAttribute*ge.count)}else for(let Se=0;Se<re.locationSize;Se++)v(re.location+Se);r.bindBuffer(r.ARRAY_BUFFER,pt);for(let Se=0;Se<re.locationSize;Se++)w(re.location+Se,ze/re.locationSize,le,be,ze*me,ze/re.locationSize*Se*me,Ue)}}else if(q!==void 0){const be=q[de];if(be!==void 0)switch(be.length){case 2:r.vertexAttrib2fv(re.location,be);break;case 3:r.vertexAttrib3fv(re.location,be);break;case 4:r.vertexAttrib4fv(re.location,be);break;default:r.vertexAttrib1fv(re.location,be)}}}}A()}function B(){V();for(const R in n){const H=n[R];for(const ee in H){const te=H[ee];for(const se in te)f(te[se].object),delete te[se];delete H[ee]}delete n[R]}}function U(R){if(n[R.id]===void 0)return;const H=n[R.id];for(const ee in H){const te=H[ee];for(const se in te)f(te[se].object),delete te[se];delete H[ee]}delete n[R.id]}function O(R){for(const H in n){const ee=n[H];if(ee[R.id]===void 0)continue;const te=ee[R.id];for(const se in te)f(te[se].object),delete te[se];delete ee[R.id]}}function V(){I(),a=!0,s!==i&&(s=i,h(s.object))}function I(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:c,reset:V,resetDefaultState:I,dispose:B,releaseStatesOfGeometry:U,releaseStatesOfProgram:O,initAttributes:E,enableAttribute:v,disableUnusedAttributes:A}}function T1(r,e,t){let n;function i(h){n=h}function s(h,f){r.drawArrays(n,h,f),t.update(f,n,1)}function a(h,f,p){p!==0&&(r.drawArraysInstanced(n,h,f,p),t.update(f,n,p))}function c(h,f,p){if(p===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,h,0,f,0,p);let g=0;for(let x=0;x<p;x++)g+=f[x];t.update(g,n,1)}function u(h,f,p,m){if(p===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let x=0;x<h.length;x++)a(h[x],f[x],m[x]);else{g.multiDrawArraysInstancedWEBGL(n,h,0,f,0,m,0,p);let x=0;for(let E=0;E<p;E++)x+=f[E]*m[E];t.update(x,n,1)}}this.setMode=i,this.render=s,this.renderInstances=a,this.renderMultiDraw=c,this.renderMultiDrawInstances=u}function w1(r,e,t,n){let i;function s(){if(i!==void 0)return i;if(e.has("EXT_texture_filter_anisotropic")===!0){const O=e.get("EXT_texture_filter_anisotropic");i=r.getParameter(O.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function a(O){return!(O!==fi&&n.convert(O)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_FORMAT))}function c(O){const V=O===ia&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(O!==ir&&n.convert(O)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_TYPE)&&O!==Si&&!V)}function u(O){if(O==="highp"){if(r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.HIGH_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.HIGH_FLOAT).precision>0)return"highp";O="mediump"}return O==="mediump"&&r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.MEDIUM_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let h=t.precision!==void 0?t.precision:"highp";const f=u(h);f!==h&&(console.warn("THREE.WebGLRenderer:",h,"not supported, using",f,"instead."),h=f);const p=t.logarithmicDepthBuffer===!0,m=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),g=r.getParameter(r.MAX_TEXTURE_IMAGE_UNITS),x=r.getParameter(r.MAX_VERTEX_TEXTURE_IMAGE_UNITS),E=r.getParameter(r.MAX_TEXTURE_SIZE),v=r.getParameter(r.MAX_CUBE_MAP_TEXTURE_SIZE),_=r.getParameter(r.MAX_VERTEX_ATTRIBS),A=r.getParameter(r.MAX_VERTEX_UNIFORM_VECTORS),w=r.getParameter(r.MAX_VARYING_VECTORS),b=r.getParameter(r.MAX_FRAGMENT_UNIFORM_VECTORS),B=x>0,U=r.getParameter(r.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:u,textureFormatReadable:a,textureTypeReadable:c,precision:h,logarithmicDepthBuffer:p,reverseDepthBuffer:m,maxTextures:g,maxVertexTextures:x,maxTextureSize:E,maxCubemapSize:v,maxAttributes:_,maxVertexUniforms:A,maxVaryings:w,maxFragmentUniforms:b,vertexTextures:B,maxSamples:U}}function A1(r){const e=this;let t=null,n=0,i=!1,s=!1;const a=new yr,c=new yt,u={value:null,needsUpdate:!1};this.uniform=u,this.numPlanes=0,this.numIntersection=0,this.init=function(p,m){const g=p.length!==0||m||n!==0||i;return i=m,n=p.length,g},this.beginShadows=function(){s=!0,f(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(p,m){t=f(p,m,0)},this.setState=function(p,m,g){const x=p.clippingPlanes,E=p.clipIntersection,v=p.clipShadows,_=r.get(p);if(!i||x===null||x.length===0||s&&!v)s?f(null):h();else{const A=s?0:n,w=A*4;let b=_.clippingState||null;u.value=b,b=f(x,m,w,g);for(let B=0;B!==w;++B)b[B]=t[B];_.clippingState=b,this.numIntersection=E?this.numPlanes:0,this.numPlanes+=A}};function h(){u.value!==t&&(u.value=t,u.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function f(p,m,g,x){const E=p!==null?p.length:0;let v=null;if(E!==0){if(v=u.value,x!==!0||v===null){const _=g+E*4,A=m.matrixWorldInverse;c.getNormalMatrix(A),(v===null||v.length<_)&&(v=new Float32Array(_));for(let w=0,b=g;w!==E;++w,b+=4)a.copy(p[w]).applyMatrix4(A,c),a.normal.toArray(v,b),v[b+3]=a.constant}u.value=v,u.needsUpdate=!0}return e.numPlanes=E,e.numIntersection=0,v}}function R1(r){let e=new WeakMap;function t(a,c){return c===Th?a.mapping=Qs:c===wh&&(a.mapping=Js),a}function n(a){if(a&&a.isTexture){const c=a.mapping;if(c===Th||c===wh)if(e.has(a)){const u=e.get(a).texture;return t(u,a.mapping)}else{const u=a.image;if(u&&u.height>0){const h=new kT(u.height);return h.fromEquirectangularTexture(r,a),e.set(a,h),a.addEventListener("dispose",i),t(h.texture,a.mapping)}else return null}}return a}function i(a){const c=a.target;c.removeEventListener("dispose",i);const u=e.get(c);u!==void 0&&(e.delete(c),u.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class bd extends Ng{constructor(e=-1,t=1,n=1,i=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2;let s=n-e,a=n+e,c=i+t,u=i-t;if(this.view!==null&&this.view.enabled){const h=(this.right-this.left)/this.view.fullWidth/this.zoom,f=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=h*this.view.offsetX,a=s+h*this.view.width,c-=f*this.view.offsetY,u=c-f*this.view.height}this.projectionMatrix.makeOrthographic(s,a,c,u,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Ws=4,em=[.125,.215,.35,.446,.526,.582],as=20,Wu=new bd,tm=new st;let ju=null,Xu=0,qu=0,Yu=!1;const rs=(1+Math.sqrt(5))/2,ks=1/rs,nm=[new N(-rs,ks,0),new N(rs,ks,0),new N(-ks,0,rs),new N(ks,0,rs),new N(0,rs,-ks),new N(0,rs,ks),new N(-1,1,-1),new N(1,1,-1),new N(-1,1,1),new N(1,1,1)];class im{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){ju=this._renderer.getRenderTarget(),Xu=this._renderer.getActiveCubeFace(),qu=this._renderer.getActiveMipmapLevel(),Yu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,i,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=om(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=sm(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(ju,Xu,qu),this._renderer.xr.enabled=Yu,e.scissorTest=!1,lc(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Qs||e.mapping===Js?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),ju=this._renderer.getRenderTarget(),Xu=this._renderer.getActiveCubeFace(),qu=this._renderer.getActiveMipmapLevel(),Yu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ai,minFilter:ai,generateMipmaps:!1,type:ia,format:fi,colorSpace:Wn,depthBuffer:!1},i=rm(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=rm(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=P1(s)),this._blurMaterial=C1(s,e,t)}return i}_compileMaterial(e){const t=new Re(this._lodPlanes[0],e);this._renderer.compile(t,Wu)}_sceneToCubeUV(e,t,n,i){const c=new Vn(90,1,t,n),u=[1,-1,1,1,1,1],h=[1,1,1,-1,-1,-1],f=this._renderer,p=f.autoClear,m=f.toneMapping;f.getClearColor(tm),f.toneMapping=Mr,f.autoClear=!1;const g=new pi({name:"PMREM.Background",side:$n,depthWrite:!1,depthTest:!1}),x=new Re(new an,g);let E=!1;const v=e.background;v?v.isColor&&(g.color.copy(v),e.background=null,E=!0):(g.color.copy(tm),E=!0);for(let _=0;_<6;_++){const A=_%3;A===0?(c.up.set(0,u[_],0),c.lookAt(h[_],0,0)):A===1?(c.up.set(0,0,u[_]),c.lookAt(0,h[_],0)):(c.up.set(0,u[_],0),c.lookAt(0,0,h[_]));const w=this._cubeSize;lc(i,A*w,_>2?w:0,w,w),f.setRenderTarget(i),E&&f.render(x,c),f.render(e,c)}x.geometry.dispose(),x.material.dispose(),f.toneMapping=m,f.autoClear=p,e.background=v}_textureToCubeUV(e,t){const n=this._renderer,i=e.mapping===Qs||e.mapping===Js;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=om()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=sm());const s=i?this._cubemapMaterial:this._equirectMaterial,a=new Re(this._lodPlanes[0],s),c=s.uniforms;c.envMap.value=e;const u=this._cubeSize;lc(t,0,0,3*u,2*u),n.setRenderTarget(t),n.render(a,Wu)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const i=this._lodPlanes.length;for(let s=1;s<i;s++){const a=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),c=nm[(i-s-1)%nm.length];this._blur(e,s-1,s,a,c)}t.autoClear=n}_blur(e,t,n,i,s){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,i,"latitudinal",s),this._halfBlur(a,e,n,n,i,"longitudinal",s)}_halfBlur(e,t,n,i,s,a,c){const u=this._renderer,h=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const f=3,p=new Re(this._lodPlanes[i],h),m=h.uniforms,g=this._sizeLods[n]-1,x=isFinite(s)?Math.PI/(2*g):2*Math.PI/(2*as-1),E=s/x,v=isFinite(s)?1+Math.floor(f*E):as;v>as&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${v} samples when the maximum is set to ${as}`);const _=[];let A=0;for(let O=0;O<as;++O){const V=O/E,I=Math.exp(-V*V/2);_.push(I),O===0?A+=I:O<v&&(A+=2*I)}for(let O=0;O<_.length;O++)_[O]=_[O]/A;m.envMap.value=e.texture,m.samples.value=v,m.weights.value=_,m.latitudinal.value=a==="latitudinal",c&&(m.poleAxis.value=c);const{_lodMax:w}=this;m.dTheta.value=x,m.mipInt.value=w-n;const b=this._sizeLods[i],B=3*b*(i>w-Ws?i-w+Ws:0),U=4*(this._cubeSize-b);lc(t,B,U,3*b,2*b),u.setRenderTarget(t),u.render(p,Wu)}}function P1(r){const e=[],t=[],n=[];let i=r;const s=r-Ws+1+em.length;for(let a=0;a<s;a++){const c=Math.pow(2,i);t.push(c);let u=1/c;a>r-Ws?u=em[a-r+Ws-1]:a===0&&(u=0),n.push(u);const h=1/(c-2),f=-h,p=1+h,m=[f,f,p,f,p,p,f,f,p,p,f,p],g=6,x=6,E=3,v=2,_=1,A=new Float32Array(E*x*g),w=new Float32Array(v*x*g),b=new Float32Array(_*x*g);for(let U=0;U<g;U++){const O=U%3*2/3-1,V=U>2?0:-1,I=[O,V,0,O+2/3,V,0,O+2/3,V+1,0,O,V,0,O+2/3,V+1,0,O,V+1,0];A.set(I,E*x*U),w.set(m,v*x*U);const R=[U,U,U,U,U,U];b.set(R,_*x*U)}const B=new _n;B.setAttribute("position",new ln(A,E)),B.setAttribute("uv",new ln(w,v)),B.setAttribute("faceIndex",new ln(b,_)),e.push(B),i>Ws&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function rm(r,e,t){const n=new us(r,e,t);return n.texture.mapping=kc,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function lc(r,e,t,n,i){r.viewport.set(e,t,n,i),r.scissor.set(e,t,n,i)}function C1(r,e,t){const n=new Float32Array(as),i=new N(0,1,0);return new Tr({name:"SphericalGaussianBlur",defines:{n:as,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${r}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:Sd(),fragmentShader:`

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
	`}function D1(r){let e=new WeakMap,t=null;function n(c){if(c&&c.isTexture){const u=c.mapping,h=u===Th||u===wh,f=u===Qs||u===Js;if(h||f){let p=e.get(c);const m=p!==void 0?p.texture.pmremVersion:0;if(c.isRenderTargetTexture&&c.pmremVersion!==m)return t===null&&(t=new im(r)),p=h?t.fromEquirectangular(c,p):t.fromCubemap(c,p),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),p.texture;if(p!==void 0)return p.texture;{const g=c.image;return h&&g&&g.height>0||f&&g&&i(g)?(t===null&&(t=new im(r)),p=h?t.fromEquirectangular(c):t.fromCubemap(c),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),c.addEventListener("dispose",s),p.texture):null}}}return c}function i(c){let u=0;const h=6;for(let f=0;f<h;f++)c[f]!==void 0&&u++;return u===h}function s(c){const u=c.target;u.removeEventListener("dispose",s);const h=e.get(u);h!==void 0&&(e.delete(u),h.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function I1(r){const e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=r.getExtension("WEBGL_depth_texture")||r.getExtension("MOZ_WEBGL_depth_texture")||r.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=r.getExtension("EXT_texture_filter_anisotropic")||r.getExtension("MOZ_EXT_texture_filter_anisotropic")||r.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=r.getExtension("WEBGL_compressed_texture_s3tc")||r.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=r.getExtension("WEBGL_compressed_texture_pvrtc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=r.getExtension(n)}return e[n]=i,i}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const i=t(n);return i===null&&jo("THREE.WebGLRenderer: "+n+" extension not supported."),i}}}function L1(r,e,t,n){const i={},s=new WeakMap;function a(p){const m=p.target;m.index!==null&&e.remove(m.index);for(const x in m.attributes)e.remove(m.attributes[x]);for(const x in m.morphAttributes){const E=m.morphAttributes[x];for(let v=0,_=E.length;v<_;v++)e.remove(E[v])}m.removeEventListener("dispose",a),delete i[m.id];const g=s.get(m);g&&(e.remove(g),s.delete(m)),n.releaseStatesOfGeometry(m),m.isInstancedBufferGeometry===!0&&delete m._maxInstanceCount,t.memory.geometries--}function c(p,m){return i[m.id]===!0||(m.addEventListener("dispose",a),i[m.id]=!0,t.memory.geometries++),m}function u(p){const m=p.attributes;for(const x in m)e.update(m[x],r.ARRAY_BUFFER);const g=p.morphAttributes;for(const x in g){const E=g[x];for(let v=0,_=E.length;v<_;v++)e.update(E[v],r.ARRAY_BUFFER)}}function h(p){const m=[],g=p.index,x=p.attributes.position;let E=0;if(g!==null){const A=g.array;E=g.version;for(let w=0,b=A.length;w<b;w+=3){const B=A[w+0],U=A[w+1],O=A[w+2];m.push(B,U,U,O,O,B)}}else if(x!==void 0){const A=x.array;E=x.version;for(let w=0,b=A.length/3-1;w<b;w+=3){const B=w+0,U=w+1,O=w+2;m.push(B,U,U,O,O,B)}}else return;const v=new(Rg(m)?Lg:Ig)(m,1);v.version=E;const _=s.get(p);_&&e.remove(_),s.set(p,v)}function f(p){const m=s.get(p);if(m){const g=p.index;g!==null&&m.version<g.version&&h(p)}else h(p);return s.get(p)}return{get:c,update:u,getWireframeAttribute:f}}function F1(r,e,t){let n;function i(m){n=m}let s,a;function c(m){s=m.type,a=m.bytesPerElement}function u(m,g){r.drawElements(n,g,s,m*a),t.update(g,n,1)}function h(m,g,x){x!==0&&(r.drawElementsInstanced(n,g,s,m*a,x),t.update(g,n,x))}function f(m,g,x){if(x===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,g,0,s,m,0,x);let v=0;for(let _=0;_<x;_++)v+=g[_];t.update(v,n,1)}function p(m,g,x,E){if(x===0)return;const v=e.get("WEBGL_multi_draw");if(v===null)for(let _=0;_<m.length;_++)h(m[_]/a,g[_],E[_]);else{v.multiDrawElementsInstancedWEBGL(n,g,0,s,m,0,E,0,x);let _=0;for(let A=0;A<x;A++)_+=g[A]*E[A];t.update(_,n,1)}}this.setMode=i,this.setIndex=c,this.render=u,this.renderInstances=h,this.renderMultiDraw=f,this.renderMultiDrawInstances=p}function N1(r){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,c){switch(t.calls++,a){case r.TRIANGLES:t.triangles+=c*(s/3);break;case r.LINES:t.lines+=c*(s/2);break;case r.LINE_STRIP:t.lines+=c*(s-1);break;case r.LINE_LOOP:t.lines+=c*s;break;case r.POINTS:t.points+=c*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function i(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}function O1(r,e,t){const n=new WeakMap,i=new Ot;function s(a,c,u){const h=a.morphTargetInfluences,f=c.morphAttributes.position||c.morphAttributes.normal||c.morphAttributes.color,p=f!==void 0?f.length:0;let m=n.get(c);if(m===void 0||m.count!==p){let R=function(){V.dispose(),n.delete(c),c.removeEventListener("dispose",R)};var g=R;m!==void 0&&m.texture.dispose();const x=c.morphAttributes.position!==void 0,E=c.morphAttributes.normal!==void 0,v=c.morphAttributes.color!==void 0,_=c.morphAttributes.position||[],A=c.morphAttributes.normal||[],w=c.morphAttributes.color||[];let b=0;x===!0&&(b=1),E===!0&&(b=2),v===!0&&(b=3);let B=c.attributes.position.count*b,U=1;B>e.maxTextureSize&&(U=Math.ceil(B/e.maxTextureSize),B=e.maxTextureSize);const O=new Float32Array(B*U*4*p),V=new Cg(O,B,U,p);V.type=Si,V.needsUpdate=!0;const I=b*4;for(let H=0;H<p;H++){const ee=_[H],te=A[H],se=w[H],he=B*U*4*H;for(let q=0;q<ee.count;q++){const de=q*I;x===!0&&(i.fromBufferAttribute(ee,q),O[he+de+0]=i.x,O[he+de+1]=i.y,O[he+de+2]=i.z,O[he+de+3]=0),E===!0&&(i.fromBufferAttribute(te,q),O[he+de+4]=i.x,O[he+de+5]=i.y,O[he+de+6]=i.z,O[he+de+7]=0),v===!0&&(i.fromBufferAttribute(se,q),O[he+de+8]=i.x,O[he+de+9]=i.y,O[he+de+10]=i.z,O[he+de+11]=se.itemSize===4?i.w:1)}}m={count:p,texture:V,size:new lt(B,U)},n.set(c,m),c.addEventListener("dispose",R)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)u.getUniforms().setValue(r,"morphTexture",a.morphTexture,t);else{let x=0;for(let v=0;v<h.length;v++)x+=h[v];const E=c.morphTargetsRelative?1:1-x;u.getUniforms().setValue(r,"morphTargetBaseInfluence",E),u.getUniforms().setValue(r,"morphTargetInfluences",h)}u.getUniforms().setValue(r,"morphTargetsTexture",m.texture,t),u.getUniforms().setValue(r,"morphTargetsTextureSize",m.size)}return{update:s}}function U1(r,e,t,n){let i=new WeakMap;function s(u){const h=n.render.frame,f=u.geometry,p=e.get(u,f);if(i.get(p)!==h&&(e.update(p),i.set(p,h)),u.isInstancedMesh&&(u.hasEventListener("dispose",c)===!1&&u.addEventListener("dispose",c),i.get(u)!==h&&(t.update(u.instanceMatrix,r.ARRAY_BUFFER),u.instanceColor!==null&&t.update(u.instanceColor,r.ARRAY_BUFFER),i.set(u,h))),u.isSkinnedMesh){const m=u.skeleton;i.get(m)!==h&&(m.update(),i.set(m,h))}return p}function a(){i=new WeakMap}function c(u){const h=u.target;h.removeEventListener("dispose",c),t.remove(h.instanceMatrix),h.instanceColor!==null&&t.remove(h.instanceColor)}return{update:s,dispose:a}}class Bg extends Mn{constructor(e,t,n,i,s,a,c,u,h,f=Ys){if(f!==Ys&&f!==no)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&f===Ys&&(n=ls),n===void 0&&f===no&&(n=to),super(null,i,s,a,c,u,f,n,h),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=c!==void 0?c:Gn,this.minFilter=u!==void 0?u:Gn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const kg=new Mn,am=new Bg(1,1),zg=new Cg,Hg=new ET,Vg=new Og,cm=[],lm=[],um=new Float32Array(16),hm=new Float32Array(9),dm=new Float32Array(4);function uo(r,e,t){const n=r[0];if(n<=0||n>0)return r;const i=e*t;let s=cm[i];if(s===void 0&&(s=new Float32Array(i),cm[i]=s),e!==0){n.toArray(s,0);for(let a=1,c=0;a!==e;++a)c+=t,r[a].toArray(s,c)}return s}function vn(r,e){if(r.length!==e.length)return!1;for(let t=0,n=r.length;t<n;t++)if(r[t]!==e[t])return!1;return!0}function yn(r,e){for(let t=0,n=e.length;t<n;t++)r[t]=e[t]}function Hc(r,e){let t=lm[e];t===void 0&&(t=new Int32Array(e),lm[e]=t);for(let n=0;n!==e;++n)t[n]=r.allocateTextureUnit();return t}function B1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1f(this.addr,e),t[0]=e)}function k1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(vn(t,e))return;r.uniform2fv(this.addr,e),yn(t,e)}}function z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(r.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(vn(t,e))return;r.uniform3fv(this.addr,e),yn(t,e)}}function H1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(vn(t,e))return;r.uniform4fv(this.addr,e),yn(t,e)}}function V1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(vn(t,e))return;r.uniformMatrix2fv(this.addr,!1,e),yn(t,e)}else{if(vn(t,n))return;dm.set(n),r.uniformMatrix2fv(this.addr,!1,dm),yn(t,n)}}function G1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(vn(t,e))return;r.uniformMatrix3fv(this.addr,!1,e),yn(t,e)}else{if(vn(t,n))return;hm.set(n),r.uniformMatrix3fv(this.addr,!1,hm),yn(t,n)}}function W1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(vn(t,e))return;r.uniformMatrix4fv(this.addr,!1,e),yn(t,e)}else{if(vn(t,n))return;um.set(n),r.uniformMatrix4fv(this.addr,!1,um),yn(t,n)}}function j1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1i(this.addr,e),t[0]=e)}function X1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(vn(t,e))return;r.uniform2iv(this.addr,e),yn(t,e)}}function q1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(vn(t,e))return;r.uniform3iv(this.addr,e),yn(t,e)}}function Y1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(vn(t,e))return;r.uniform4iv(this.addr,e),yn(t,e)}}function K1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1ui(this.addr,e),t[0]=e)}function $1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(vn(t,e))return;r.uniform2uiv(this.addr,e),yn(t,e)}}function Z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(vn(t,e))return;r.uniform3uiv(this.addr,e),yn(t,e)}}function Q1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(vn(t,e))return;r.uniform4uiv(this.addr,e),yn(t,e)}}function J1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i);let s;this.type===r.SAMPLER_2D_SHADOW?(am.compareFunction=wg,s=am):s=kg,t.setTexture2D(e||s,i)}function eR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||Hg,i)}function tR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||Vg,i)}function nR(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||zg,i)}function iR(r){switch(r){case 5126:return B1;case 35664:return k1;case 35665:return z1;case 35666:return H1;case 35674:return V1;case 35675:return G1;case 35676:return W1;case 5124:case 35670:return j1;case 35667:case 35671:return X1;case 35668:case 35672:return q1;case 35669:case 35673:return Y1;case 5125:return K1;case 36294:return $1;case 36295:return Z1;case 36296:return Q1;case 35678:case 36198:case 36298:case 36306:case 35682:return J1;case 35679:case 36299:case 36307:return eR;case 35680:case 36300:case 36308:case 36293:return tR;case 36289:case 36303:case 36311:case 36292:return nR}}function rR(r,e){r.uniform1fv(this.addr,e)}function sR(r,e){const t=uo(e,this.size,2);r.uniform2fv(this.addr,t)}function oR(r,e){const t=uo(e,this.size,3);r.uniform3fv(this.addr,t)}function aR(r,e){const t=uo(e,this.size,4);r.uniform4fv(this.addr,t)}function cR(r,e){const t=uo(e,this.size,4);r.uniformMatrix2fv(this.addr,!1,t)}function lR(r,e){const t=uo(e,this.size,9);r.uniformMatrix3fv(this.addr,!1,t)}function uR(r,e){const t=uo(e,this.size,16);r.uniformMatrix4fv(this.addr,!1,t)}function hR(r,e){r.uniform1iv(this.addr,e)}function dR(r,e){r.uniform2iv(this.addr,e)}function fR(r,e){r.uniform3iv(this.addr,e)}function pR(r,e){r.uniform4iv(this.addr,e)}function mR(r,e){r.uniform1uiv(this.addr,e)}function gR(r,e){r.uniform2uiv(this.addr,e)}function _R(r,e){r.uniform3uiv(this.addr,e)}function vR(r,e){r.uniform4uiv(this.addr,e)}function yR(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);vn(n,s)||(r.uniform1iv(this.addr,s),yn(n,s));for(let a=0;a!==i;++a)t.setTexture2D(e[a]||kg,s[a])}function xR(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);vn(n,s)||(r.uniform1iv(this.addr,s),yn(n,s));for(let a=0;a!==i;++a)t.setTexture3D(e[a]||Hg,s[a])}function bR(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);vn(n,s)||(r.uniform1iv(this.addr,s),yn(n,s));for(let a=0;a!==i;++a)t.setTextureCube(e[a]||Vg,s[a])}function SR(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);vn(n,s)||(r.uniform1iv(this.addr,s),yn(n,s));for(let a=0;a!==i;++a)t.setTexture2DArray(e[a]||zg,s[a])}function ER(r){switch(r){case 5126:return rR;case 35664:return sR;case 35665:return oR;case 35666:return aR;case 35674:return cR;case 35675:return lR;case 35676:return uR;case 5124:case 35670:return hR;case 35667:case 35671:return dR;case 35668:case 35672:return fR;case 35669:case 35673:return pR;case 5125:return mR;case 36294:return gR;case 36295:return _R;case 36296:return vR;case 35678:case 36198:case 36298:case 36306:case 35682:return yR;case 35679:case 36299:case 36307:return xR;case 35680:case 36300:case 36308:case 36293:return bR;case 36289:case 36303:case 36311:case 36292:return SR}}class MR{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=iR(t.type)}}class TR{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=ER(t.type)}}class wR{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const i=this.seq;for(let s=0,a=i.length;s!==a;++s){const c=i[s];c.setValue(e,t[c.id],n)}}}const Ku=/(\w+)(\])?(\[|\.)?/g;function fm(r,e){r.seq.push(e),r.map[e.id]=e}function AR(r,e,t){const n=r.name,i=n.length;for(Ku.lastIndex=0;;){const s=Ku.exec(n),a=Ku.lastIndex;let c=s[1];const u=s[2]==="]",h=s[3];if(u&&(c=c|0),h===void 0||h==="["&&a+2===i){fm(t,h===void 0?new MR(c,r,e):new TR(c,r,e));break}else{let p=t.map[c];p===void 0&&(p=new wR(c),fm(t,p)),t=p}}}class Cc{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let i=0;i<n;++i){const s=e.getActiveUniform(t,i),a=e.getUniformLocation(t,s.name);AR(s,a,this)}}setValue(e,t,n,i){const s=this.map[t];s!==void 0&&s.setValue(e,n,i)}setOptional(e,t,n){const i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let s=0,a=t.length;s!==a;++s){const c=t[s],u=n[c.id];u.needsUpdate!==!1&&c.setValue(e,u.value,i)}}static seqWithValue(e,t){const n=[];for(let i=0,s=e.length;i!==s;++i){const a=e[i];a.id in t&&n.push(a)}return n}}function pm(r,e,t){const n=r.createShader(e);return r.shaderSource(n,t),r.compileShader(n),n}const RR=37297;let PR=0;function CR(r,e){const t=r.split(`
`),n=[],i=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let a=i;a<s;a++){const c=a+1;n.push(`${c===e?">":" "} ${c}: ${t[a]}`)}return n.join(`
`)}const mm=new yt;function DR(r){Ct._getMatrix(mm,Ct.workingColorSpace,r);const e=`mat3( ${mm.elements.map(t=>t.toFixed(4))} )`;switch(Ct.getTransfer(r)){case zc:return[e,"LinearTransferOETF"];case Gt:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",r),[e,"LinearTransferOETF"]}}function gm(r,e,t){const n=r.getShaderParameter(e,r.COMPILE_STATUS),i=r.getShaderInfoLog(e).trim();if(n&&i==="")return"";const s=/ERROR: 0:(\d+)/.exec(i);if(s){const a=parseInt(s[1]);return t.toUpperCase()+`

`+i+`

`+CR(r.getShaderSource(e),a)}else return i}function IR(r,e){const t=DR(e);return[`vec4 ${r}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function LR(r,e){let t;switch(e){case IM:t="Linear";break;case LM:t="Reinhard";break;case FM:t="Cineon";break;case dg:t="ACESFilmic";break;case OM:t="AgX";break;case UM:t="Neutral";break;case NM:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+r+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const uc=new N;function FR(){Ct.getLuminanceCoefficients(uc);const r=uc.x.toFixed(4),e=uc.y.toFixed(4),t=uc.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${r}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function NR(r){return[r.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",r.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Xo).join(`
`)}function OR(r){const e=[];for(const t in r){const n=r[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function UR(r,e){const t={},n=r.getProgramParameter(e,r.ACTIVE_ATTRIBUTES);for(let i=0;i<n;i++){const s=r.getActiveAttrib(e,i),a=s.name;let c=1;s.type===r.FLOAT_MAT2&&(c=2),s.type===r.FLOAT_MAT3&&(c=3),s.type===r.FLOAT_MAT4&&(c=4),t[a]={type:s.type,location:r.getAttribLocation(e,a),locationSize:c}}return t}function Xo(r){return r!==""}function _m(r,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return r.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function vm(r,e){return r.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const BR=/^[ \t]*#include +<([\w\d./]+)>/gm;function td(r){return r.replace(BR,zR)}const kR=new Map;function zR(r,e){let t=St[e];if(t===void 0){const n=kR.get(e);if(n!==void 0)t=St[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return td(t)}const HR=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function ym(r){return r.replace(HR,VR)}function VR(r,e,t,n){let i="";for(let s=parseInt(e);s<parseInt(t);s++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return i}function xm(r){let e=`precision ${r.precision} float;
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
#define LOW_PRECISION`),e}function GR(r){let e="SHADOWMAP_TYPE_BASIC";return r.shadowMapType===ug?e="SHADOWMAP_TYPE_PCF":r.shadowMapType===hM?e="SHADOWMAP_TYPE_PCF_SOFT":r.shadowMapType===$i&&(e="SHADOWMAP_TYPE_VSM"),e}function WR(r){let e="ENVMAP_TYPE_CUBE";if(r.envMap)switch(r.envMapMode){case Qs:case Js:e="ENVMAP_TYPE_CUBE";break;case kc:e="ENVMAP_TYPE_CUBE_UV";break}return e}function jR(r){let e="ENVMAP_MODE_REFLECTION";if(r.envMap)switch(r.envMapMode){case Js:e="ENVMAP_MODE_REFRACTION";break}return e}function XR(r){let e="ENVMAP_BLENDING_NONE";if(r.envMap)switch(r.combine){case hg:e="ENVMAP_BLENDING_MULTIPLY";break;case CM:e="ENVMAP_BLENDING_MIX";break;case DM:e="ENVMAP_BLENDING_ADD";break}return e}function qR(r){const e=r.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function YR(r,e,t,n){const i=r.getContext(),s=t.defines;let a=t.vertexShader,c=t.fragmentShader;const u=GR(t),h=WR(t),f=jR(t),p=XR(t),m=qR(t),g=NR(t),x=OR(s),E=i.createProgram();let v,_,A=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(v=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(Xo).join(`
`),v.length>0&&(v+=`
`),_=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(Xo).join(`
`),_.length>0&&(_+=`
`)):(v=[xm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+f:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Xo).join(`
`),_=[xm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.envMap?"#define "+f:"",t.envMap?"#define "+p:"",m?"#define CUBEUV_TEXEL_WIDTH "+m.texelWidth:"",m?"#define CUBEUV_TEXEL_HEIGHT "+m.texelHeight:"",m?"#define CUBEUV_MAX_MIP "+m.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Mr?"#define TONE_MAPPING":"",t.toneMapping!==Mr?St.tonemapping_pars_fragment:"",t.toneMapping!==Mr?LR("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",St.colorspace_pars_fragment,IR("linearToOutputTexel",t.outputColorSpace),FR(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Xo).join(`
`)),a=td(a),a=_m(a,t),a=vm(a,t),c=td(c),c=_m(c,t),c=vm(c,t),a=ym(a),c=ym(c),t.isRawShaderMaterial!==!0&&(A=`#version 300 es
`,v=[g,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+v,_=["#define varying in",t.glslVersion===Ip?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Ip?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);const w=A+v+a,b=A+_+c,B=pm(i,i.VERTEX_SHADER,w),U=pm(i,i.FRAGMENT_SHADER,b);i.attachShader(E,B),i.attachShader(E,U),t.index0AttributeName!==void 0?i.bindAttribLocation(E,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(E,0,"position"),i.linkProgram(E);function O(H){if(r.debug.checkShaderErrors){const ee=i.getProgramInfoLog(E).trim(),te=i.getShaderInfoLog(B).trim(),se=i.getShaderInfoLog(U).trim();let he=!0,q=!0;if(i.getProgramParameter(E,i.LINK_STATUS)===!1)if(he=!1,typeof r.debug.onShaderError=="function")r.debug.onShaderError(i,E,B,U);else{const de=gm(i,B,"vertex"),re=gm(i,U,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(E,i.VALIDATE_STATUS)+`

Material Name: `+H.name+`
Material Type: `+H.type+`

Program Info Log: `+ee+`
`+de+`
`+re)}else ee!==""?console.warn("THREE.WebGLProgram: Program Info Log:",ee):(te===""||se==="")&&(q=!1);q&&(H.diagnostics={runnable:he,programLog:ee,vertexShader:{log:te,prefix:v},fragmentShader:{log:se,prefix:_}})}i.deleteShader(B),i.deleteShader(U),V=new Cc(i,E),I=UR(i,E)}let V;this.getUniforms=function(){return V===void 0&&O(this),V};let I;this.getAttributes=function(){return I===void 0&&O(this),I};let R=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return R===!1&&(R=i.getProgramParameter(E,RR)),R},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(E),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=PR++,this.cacheKey=e,this.usedTimes=1,this.program=E,this.vertexShader=B,this.fragmentShader=U,this}let KR=0;class $R{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(i)===!1&&(a.add(i),i.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new ZR(e),t.set(e,n)),n}}class ZR{constructor(e){this.id=KR++,this.code=e,this.usedTimes=0}}function QR(r,e,t,n,i,s,a){const c=new yd,u=new $R,h=new Set,f=[],p=i.logarithmicDepthBuffer,m=i.vertexTextures;let g=i.precision;const x={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function E(I){return h.add(I),I===0?"uv":`uv${I}`}function v(I,R,H,ee,te){const se=ee.fog,he=te.geometry,q=I.isMeshStandardMaterial?ee.environment:null,de=(I.isMeshStandardMaterial?t:e).get(I.envMap||q),re=de&&de.mapping===kc?de.image.height:null,ge=x[I.type];I.precision!==null&&(g=i.getMaxPrecision(I.precision),g!==I.precision&&console.warn("THREE.WebGLProgram.getParameters:",I.precision,"not supported, using",g,"instead."));const be=he.morphAttributes.position||he.morphAttributes.normal||he.morphAttributes.color,ze=be!==void 0?be.length:0;let Ge=0;he.morphAttributes.position!==void 0&&(Ge=1),he.morphAttributes.normal!==void 0&&(Ge=2),he.morphAttributes.color!==void 0&&(Ge=3);let pt,le,me,Ue;if(ge){const Pe=Pi[ge];pt=Pe.vertexShader,le=Pe.fragmentShader}else pt=I.vertexShader,le=I.fragmentShader,u.update(I),me=u.getVertexShaderID(I),Ue=u.getFragmentShaderID(I);const Se=r.getRenderTarget(),$e=r.state.buffers.depth.getReversed(),it=te.isInstancedMesh===!0,Je=te.isBatchedMesh===!0,pe=!!I.map,ve=!!I.matcap,Le=!!de,G=!!I.aoMap,tt=!!I.lightMap,Ke=!!I.bumpMap,Qe=!!I.normalMap,Oe=!!I.displacementMap,rt=!!I.emissiveMap,Fe=!!I.metalnessMap,F=!!I.roughnessMap,T=I.anisotropy>0,Z=I.clearcoat>0,ce=I.dispersion>0,fe=I.iridescence>0,ue=I.sheen>0,ke=I.transmission>0,we=T&&!!I.anisotropyMap,Be=Z&&!!I.clearcoatMap,gt=Z&&!!I.clearcoatNormalMap,_e=Z&&!!I.clearcoatRoughnessMap,He=fe&&!!I.iridescenceMap,We=fe&&!!I.iridescenceThicknessMap,ot=ue&&!!I.sheenColorMap,Ve=ue&&!!I.sheenRoughnessMap,xt=!!I.specularMap,dt=!!I.specularColorMap,It=!!I.specularIntensityMap,X=ke&&!!I.transmissionMap,Ae=ke&&!!I.thicknessMap,P=!!I.gradientMap,k=!!I.alphaMap,$=I.alphaTest>0,ie=!!I.alphaHash,Te=!!I.extensions;let Ee=Mr;I.toneMapped&&(Se===null||Se.isXRRenderTarget===!0)&&(Ee=r.toneMapping);const De={shaderID:ge,shaderType:I.type,shaderName:I.name,vertexShader:pt,fragmentShader:le,defines:I.defines,customVertexShaderID:me,customFragmentShaderID:Ue,isRawShaderMaterial:I.isRawShaderMaterial===!0,glslVersion:I.glslVersion,precision:g,batching:Je,batchingColor:Je&&te._colorsTexture!==null,instancing:it,instancingColor:it&&te.instanceColor!==null,instancingMorph:it&&te.morphTexture!==null,supportsVertexTextures:m,outputColorSpace:Se===null?r.outputColorSpace:Se.isXRRenderTarget===!0?Se.texture.colorSpace:Wn,alphaToCoverage:!!I.alphaToCoverage,map:pe,matcap:ve,envMap:Le,envMapMode:Le&&de.mapping,envMapCubeUVHeight:re,aoMap:G,lightMap:tt,bumpMap:Ke,normalMap:Qe,displacementMap:m&&Oe,emissiveMap:rt,normalMapObjectSpace:Qe&&I.normalMapType===jM,normalMapTangentSpace:Qe&&I.normalMapType===Tg,metalnessMap:Fe,roughnessMap:F,anisotropy:T,anisotropyMap:we,clearcoat:Z,clearcoatMap:Be,clearcoatNormalMap:gt,clearcoatRoughnessMap:_e,dispersion:ce,iridescence:fe,iridescenceMap:He,iridescenceThicknessMap:We,sheen:ue,sheenColorMap:ot,sheenRoughnessMap:Ve,specularMap:xt,specularColorMap:dt,specularIntensityMap:It,transmission:ke,transmissionMap:X,thicknessMap:Ae,gradientMap:P,opaque:I.transparent===!1&&I.blending===qs&&I.alphaToCoverage===!1,alphaMap:k,alphaTest:$,alphaHash:ie,combine:I.combine,mapUv:pe&&E(I.map.channel),aoMapUv:G&&E(I.aoMap.channel),lightMapUv:tt&&E(I.lightMap.channel),bumpMapUv:Ke&&E(I.bumpMap.channel),normalMapUv:Qe&&E(I.normalMap.channel),displacementMapUv:Oe&&E(I.displacementMap.channel),emissiveMapUv:rt&&E(I.emissiveMap.channel),metalnessMapUv:Fe&&E(I.metalnessMap.channel),roughnessMapUv:F&&E(I.roughnessMap.channel),anisotropyMapUv:we&&E(I.anisotropyMap.channel),clearcoatMapUv:Be&&E(I.clearcoatMap.channel),clearcoatNormalMapUv:gt&&E(I.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:_e&&E(I.clearcoatRoughnessMap.channel),iridescenceMapUv:He&&E(I.iridescenceMap.channel),iridescenceThicknessMapUv:We&&E(I.iridescenceThicknessMap.channel),sheenColorMapUv:ot&&E(I.sheenColorMap.channel),sheenRoughnessMapUv:Ve&&E(I.sheenRoughnessMap.channel),specularMapUv:xt&&E(I.specularMap.channel),specularColorMapUv:dt&&E(I.specularColorMap.channel),specularIntensityMapUv:It&&E(I.specularIntensityMap.channel),transmissionMapUv:X&&E(I.transmissionMap.channel),thicknessMapUv:Ae&&E(I.thicknessMap.channel),alphaMapUv:k&&E(I.alphaMap.channel),vertexTangents:!!he.attributes.tangent&&(Qe||T),vertexColors:I.vertexColors,vertexAlphas:I.vertexColors===!0&&!!he.attributes.color&&he.attributes.color.itemSize===4,pointsUvs:te.isPoints===!0&&!!he.attributes.uv&&(pe||k),fog:!!se,useFog:I.fog===!0,fogExp2:!!se&&se.isFogExp2,flatShading:I.flatShading===!0,sizeAttenuation:I.sizeAttenuation===!0,logarithmicDepthBuffer:p,reverseDepthBuffer:$e,skinning:te.isSkinnedMesh===!0,morphTargets:he.morphAttributes.position!==void 0,morphNormals:he.morphAttributes.normal!==void 0,morphColors:he.morphAttributes.color!==void 0,morphTargetsCount:ze,morphTextureStride:Ge,numDirLights:R.directional.length,numPointLights:R.point.length,numSpotLights:R.spot.length,numSpotLightMaps:R.spotLightMap.length,numRectAreaLights:R.rectArea.length,numHemiLights:R.hemi.length,numDirLightShadows:R.directionalShadowMap.length,numPointLightShadows:R.pointShadowMap.length,numSpotLightShadows:R.spotShadowMap.length,numSpotLightShadowsWithMaps:R.numSpotLightShadowsWithMaps,numLightProbes:R.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:I.dithering,shadowMapEnabled:r.shadowMap.enabled&&H.length>0,shadowMapType:r.shadowMap.type,toneMapping:Ee,decodeVideoTexture:pe&&I.map.isVideoTexture===!0&&Ct.getTransfer(I.map.colorSpace)===Gt,decodeVideoTextureEmissive:rt&&I.emissiveMap.isVideoTexture===!0&&Ct.getTransfer(I.emissiveMap.colorSpace)===Gt,premultipliedAlpha:I.premultipliedAlpha,doubleSided:I.side===Kn,flipSided:I.side===$n,useDepthPacking:I.depthPacking>=0,depthPacking:I.depthPacking||0,index0AttributeName:I.index0AttributeName,extensionClipCullDistance:Te&&I.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(Te&&I.extensions.multiDraw===!0||Je)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:I.customProgramCacheKey()};return De.vertexUv1s=h.has(1),De.vertexUv2s=h.has(2),De.vertexUv3s=h.has(3),h.clear(),De}function _(I){const R=[];if(I.shaderID?R.push(I.shaderID):(R.push(I.customVertexShaderID),R.push(I.customFragmentShaderID)),I.defines!==void 0)for(const H in I.defines)R.push(H),R.push(I.defines[H]);return I.isRawShaderMaterial===!1&&(A(R,I),w(R,I),R.push(r.outputColorSpace)),R.push(I.customProgramCacheKey),R.join()}function A(I,R){I.push(R.precision),I.push(R.outputColorSpace),I.push(R.envMapMode),I.push(R.envMapCubeUVHeight),I.push(R.mapUv),I.push(R.alphaMapUv),I.push(R.lightMapUv),I.push(R.aoMapUv),I.push(R.bumpMapUv),I.push(R.normalMapUv),I.push(R.displacementMapUv),I.push(R.emissiveMapUv),I.push(R.metalnessMapUv),I.push(R.roughnessMapUv),I.push(R.anisotropyMapUv),I.push(R.clearcoatMapUv),I.push(R.clearcoatNormalMapUv),I.push(R.clearcoatRoughnessMapUv),I.push(R.iridescenceMapUv),I.push(R.iridescenceThicknessMapUv),I.push(R.sheenColorMapUv),I.push(R.sheenRoughnessMapUv),I.push(R.specularMapUv),I.push(R.specularColorMapUv),I.push(R.specularIntensityMapUv),I.push(R.transmissionMapUv),I.push(R.thicknessMapUv),I.push(R.combine),I.push(R.fogExp2),I.push(R.sizeAttenuation),I.push(R.morphTargetsCount),I.push(R.morphAttributeCount),I.push(R.numDirLights),I.push(R.numPointLights),I.push(R.numSpotLights),I.push(R.numSpotLightMaps),I.push(R.numHemiLights),I.push(R.numRectAreaLights),I.push(R.numDirLightShadows),I.push(R.numPointLightShadows),I.push(R.numSpotLightShadows),I.push(R.numSpotLightShadowsWithMaps),I.push(R.numLightProbes),I.push(R.shadowMapType),I.push(R.toneMapping),I.push(R.numClippingPlanes),I.push(R.numClipIntersection),I.push(R.depthPacking)}function w(I,R){c.disableAll(),R.supportsVertexTextures&&c.enable(0),R.instancing&&c.enable(1),R.instancingColor&&c.enable(2),R.instancingMorph&&c.enable(3),R.matcap&&c.enable(4),R.envMap&&c.enable(5),R.normalMapObjectSpace&&c.enable(6),R.normalMapTangentSpace&&c.enable(7),R.clearcoat&&c.enable(8),R.iridescence&&c.enable(9),R.alphaTest&&c.enable(10),R.vertexColors&&c.enable(11),R.vertexAlphas&&c.enable(12),R.vertexUv1s&&c.enable(13),R.vertexUv2s&&c.enable(14),R.vertexUv3s&&c.enable(15),R.vertexTangents&&c.enable(16),R.anisotropy&&c.enable(17),R.alphaHash&&c.enable(18),R.batching&&c.enable(19),R.dispersion&&c.enable(20),R.batchingColor&&c.enable(21),I.push(c.mask),c.disableAll(),R.fog&&c.enable(0),R.useFog&&c.enable(1),R.flatShading&&c.enable(2),R.logarithmicDepthBuffer&&c.enable(3),R.reverseDepthBuffer&&c.enable(4),R.skinning&&c.enable(5),R.morphTargets&&c.enable(6),R.morphNormals&&c.enable(7),R.morphColors&&c.enable(8),R.premultipliedAlpha&&c.enable(9),R.shadowMapEnabled&&c.enable(10),R.doubleSided&&c.enable(11),R.flipSided&&c.enable(12),R.useDepthPacking&&c.enable(13),R.dithering&&c.enable(14),R.transmission&&c.enable(15),R.sheen&&c.enable(16),R.opaque&&c.enable(17),R.pointsUvs&&c.enable(18),R.decodeVideoTexture&&c.enable(19),R.decodeVideoTextureEmissive&&c.enable(20),R.alphaToCoverage&&c.enable(21),I.push(c.mask)}function b(I){const R=x[I.type];let H;if(R){const ee=Pi[R];H=NT.clone(ee.uniforms)}else H=I.uniforms;return H}function B(I,R){let H;for(let ee=0,te=f.length;ee<te;ee++){const se=f[ee];if(se.cacheKey===R){H=se,++H.usedTimes;break}}return H===void 0&&(H=new YR(r,R,I,s),f.push(H)),H}function U(I){if(--I.usedTimes===0){const R=f.indexOf(I);f[R]=f[f.length-1],f.pop(),I.destroy()}}function O(I){u.remove(I)}function V(){u.dispose()}return{getParameters:v,getProgramCacheKey:_,getUniforms:b,acquireProgram:B,releaseProgram:U,releaseShaderCache:O,programs:f,dispose:V}}function JR(){let r=new WeakMap;function e(a){return r.has(a)}function t(a){let c=r.get(a);return c===void 0&&(c={},r.set(a,c)),c}function n(a){r.delete(a)}function i(a,c,u){r.get(a)[c]=u}function s(){r=new WeakMap}return{has:e,get:t,remove:n,update:i,dispose:s}}function eP(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.material.id!==e.material.id?r.material.id-e.material.id:r.z!==e.z?r.z-e.z:r.id-e.id}function bm(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.z!==e.z?e.z-r.z:r.id-e.id}function Sm(){const r=[];let e=0;const t=[],n=[],i=[];function s(){e=0,t.length=0,n.length=0,i.length=0}function a(p,m,g,x,E,v){let _=r[e];return _===void 0?(_={id:p.id,object:p,geometry:m,material:g,groupOrder:x,renderOrder:p.renderOrder,z:E,group:v},r[e]=_):(_.id=p.id,_.object=p,_.geometry=m,_.material=g,_.groupOrder=x,_.renderOrder=p.renderOrder,_.z=E,_.group=v),e++,_}function c(p,m,g,x,E,v){const _=a(p,m,g,x,E,v);g.transmission>0?n.push(_):g.transparent===!0?i.push(_):t.push(_)}function u(p,m,g,x,E,v){const _=a(p,m,g,x,E,v);g.transmission>0?n.unshift(_):g.transparent===!0?i.unshift(_):t.unshift(_)}function h(p,m){t.length>1&&t.sort(p||eP),n.length>1&&n.sort(m||bm),i.length>1&&i.sort(m||bm)}function f(){for(let p=e,m=r.length;p<m;p++){const g=r[p];if(g.id===null)break;g.id=null,g.object=null,g.geometry=null,g.material=null,g.group=null}}return{opaque:t,transmissive:n,transparent:i,init:s,push:c,unshift:u,finish:f,sort:h}}function tP(){let r=new WeakMap;function e(n,i){const s=r.get(n);let a;return s===void 0?(a=new Sm,r.set(n,[a])):i>=s.length?(a=new Sm,s.push(a)):a=s[i],a}function t(){r=new WeakMap}return{get:e,dispose:t}}function nP(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new N,color:new st};break;case"SpotLight":t={position:new N,direction:new N,color:new st,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new N,color:new st,distance:0,decay:0};break;case"HemisphereLight":t={direction:new N,skyColor:new st,groundColor:new st};break;case"RectAreaLight":t={color:new st,position:new N,halfWidth:new N,halfHeight:new N};break}return r[e.id]=t,t}}}function iP(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new lt};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new lt};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new lt,shadowCameraNear:1,shadowCameraFar:1e3};break}return r[e.id]=t,t}}}let rP=0;function sP(r,e){return(e.castShadow?2:0)-(r.castShadow?2:0)+(e.map?1:0)-(r.map?1:0)}function oP(r){const e=new nP,t=iP(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let h=0;h<9;h++)n.probe.push(new N);const i=new N,s=new ft,a=new ft;function c(h){let f=0,p=0,m=0;for(let I=0;I<9;I++)n.probe[I].set(0,0,0);let g=0,x=0,E=0,v=0,_=0,A=0,w=0,b=0,B=0,U=0,O=0;h.sort(sP);for(let I=0,R=h.length;I<R;I++){const H=h[I],ee=H.color,te=H.intensity,se=H.distance,he=H.shadow&&H.shadow.map?H.shadow.map.texture:null;if(H.isAmbientLight)f+=ee.r*te,p+=ee.g*te,m+=ee.b*te;else if(H.isLightProbe){for(let q=0;q<9;q++)n.probe[q].addScaledVector(H.sh.coefficients[q],te);O++}else if(H.isDirectionalLight){const q=e.get(H);if(q.color.copy(H.color).multiplyScalar(H.intensity),H.castShadow){const de=H.shadow,re=t.get(H);re.shadowIntensity=de.intensity,re.shadowBias=de.bias,re.shadowNormalBias=de.normalBias,re.shadowRadius=de.radius,re.shadowMapSize=de.mapSize,n.directionalShadow[g]=re,n.directionalShadowMap[g]=he,n.directionalShadowMatrix[g]=H.shadow.matrix,A++}n.directional[g]=q,g++}else if(H.isSpotLight){const q=e.get(H);q.position.setFromMatrixPosition(H.matrixWorld),q.color.copy(ee).multiplyScalar(te),q.distance=se,q.coneCos=Math.cos(H.angle),q.penumbraCos=Math.cos(H.angle*(1-H.penumbra)),q.decay=H.decay,n.spot[E]=q;const de=H.shadow;if(H.map&&(n.spotLightMap[B]=H.map,B++,de.updateMatrices(H),H.castShadow&&U++),n.spotLightMatrix[E]=de.matrix,H.castShadow){const re=t.get(H);re.shadowIntensity=de.intensity,re.shadowBias=de.bias,re.shadowNormalBias=de.normalBias,re.shadowRadius=de.radius,re.shadowMapSize=de.mapSize,n.spotShadow[E]=re,n.spotShadowMap[E]=he,b++}E++}else if(H.isRectAreaLight){const q=e.get(H);q.color.copy(ee).multiplyScalar(te),q.halfWidth.set(H.width*.5,0,0),q.halfHeight.set(0,H.height*.5,0),n.rectArea[v]=q,v++}else if(H.isPointLight){const q=e.get(H);if(q.color.copy(H.color).multiplyScalar(H.intensity),q.distance=H.distance,q.decay=H.decay,H.castShadow){const de=H.shadow,re=t.get(H);re.shadowIntensity=de.intensity,re.shadowBias=de.bias,re.shadowNormalBias=de.normalBias,re.shadowRadius=de.radius,re.shadowMapSize=de.mapSize,re.shadowCameraNear=de.camera.near,re.shadowCameraFar=de.camera.far,n.pointShadow[x]=re,n.pointShadowMap[x]=he,n.pointShadowMatrix[x]=H.shadow.matrix,w++}n.point[x]=q,x++}else if(H.isHemisphereLight){const q=e.get(H);q.skyColor.copy(H.color).multiplyScalar(te),q.groundColor.copy(H.groundColor).multiplyScalar(te),n.hemi[_]=q,_++}}v>0&&(r.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=Ie.LTC_FLOAT_1,n.rectAreaLTC2=Ie.LTC_FLOAT_2):(n.rectAreaLTC1=Ie.LTC_HALF_1,n.rectAreaLTC2=Ie.LTC_HALF_2)),n.ambient[0]=f,n.ambient[1]=p,n.ambient[2]=m;const V=n.hash;(V.directionalLength!==g||V.pointLength!==x||V.spotLength!==E||V.rectAreaLength!==v||V.hemiLength!==_||V.numDirectionalShadows!==A||V.numPointShadows!==w||V.numSpotShadows!==b||V.numSpotMaps!==B||V.numLightProbes!==O)&&(n.directional.length=g,n.spot.length=E,n.rectArea.length=v,n.point.length=x,n.hemi.length=_,n.directionalShadow.length=A,n.directionalShadowMap.length=A,n.pointShadow.length=w,n.pointShadowMap.length=w,n.spotShadow.length=b,n.spotShadowMap.length=b,n.directionalShadowMatrix.length=A,n.pointShadowMatrix.length=w,n.spotLightMatrix.length=b+B-U,n.spotLightMap.length=B,n.numSpotLightShadowsWithMaps=U,n.numLightProbes=O,V.directionalLength=g,V.pointLength=x,V.spotLength=E,V.rectAreaLength=v,V.hemiLength=_,V.numDirectionalShadows=A,V.numPointShadows=w,V.numSpotShadows=b,V.numSpotMaps=B,V.numLightProbes=O,n.version=rP++)}function u(h,f){let p=0,m=0,g=0,x=0,E=0;const v=f.matrixWorldInverse;for(let _=0,A=h.length;_<A;_++){const w=h[_];if(w.isDirectionalLight){const b=n.directional[p];b.direction.setFromMatrixPosition(w.matrixWorld),i.setFromMatrixPosition(w.target.matrixWorld),b.direction.sub(i),b.direction.transformDirection(v),p++}else if(w.isSpotLight){const b=n.spot[g];b.position.setFromMatrixPosition(w.matrixWorld),b.position.applyMatrix4(v),b.direction.setFromMatrixPosition(w.matrixWorld),i.setFromMatrixPosition(w.target.matrixWorld),b.direction.sub(i),b.direction.transformDirection(v),g++}else if(w.isRectAreaLight){const b=n.rectArea[x];b.position.setFromMatrixPosition(w.matrixWorld),b.position.applyMatrix4(v),a.identity(),s.copy(w.matrixWorld),s.premultiply(v),a.extractRotation(s),b.halfWidth.set(w.width*.5,0,0),b.halfHeight.set(0,w.height*.5,0),b.halfWidth.applyMatrix4(a),b.halfHeight.applyMatrix4(a),x++}else if(w.isPointLight){const b=n.point[m];b.position.setFromMatrixPosition(w.matrixWorld),b.position.applyMatrix4(v),m++}else if(w.isHemisphereLight){const b=n.hemi[E];b.direction.setFromMatrixPosition(w.matrixWorld),b.direction.transformDirection(v),E++}}}return{setup:c,setupView:u,state:n}}function Em(r){const e=new oP(r),t=[],n=[];function i(f){h.camera=f,t.length=0,n.length=0}function s(f){t.push(f)}function a(f){n.push(f)}function c(){e.setup(t)}function u(f){e.setupView(t,f)}const h={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:i,state:h,setupLights:c,setupLightsView:u,pushLight:s,pushShadow:a}}function aP(r){let e=new WeakMap;function t(i,s=0){const a=e.get(i);let c;return a===void 0?(c=new Em(r),e.set(i,[c])):s>=a.length?(c=new Em(r),a.push(c)):c=a[s],c}function n(){e=new WeakMap}return{get:t,dispose:n}}class cP extends Di{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=GM,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class lP extends Di{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const uP=`void main() {
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
}`;function dP(r,e,t){let n=new xd;const i=new lt,s=new lt,a=new Ot,c=new cP({depthPacking:WM}),u=new lP,h={},f=t.maxTextureSize,p={[nr]:$n,[$n]:nr,[Kn]:Kn},m=new Tr({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new lt},radius:{value:4}},vertexShader:uP,fragmentShader:hP}),g=m.clone();g.defines.HORIZONTAL_PASS=1;const x=new _n;x.setAttribute("position",new ln(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const E=new Re(x,m),v=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=ug;let _=this.type;this.render=function(U,O,V){if(v.enabled===!1||v.autoUpdate===!1&&v.needsUpdate===!1||U.length===0)return;const I=r.getRenderTarget(),R=r.getActiveCubeFace(),H=r.getActiveMipmapLevel(),ee=r.state;ee.setBlending(Er),ee.buffers.color.setClear(1,1,1,1),ee.buffers.depth.setTest(!0),ee.setScissorTest(!1);const te=_!==$i&&this.type===$i,se=_===$i&&this.type!==$i;for(let he=0,q=U.length;he<q;he++){const de=U[he],re=de.shadow;if(re===void 0){console.warn("THREE.WebGLShadowMap:",de,"has no shadow.");continue}if(re.autoUpdate===!1&&re.needsUpdate===!1)continue;i.copy(re.mapSize);const ge=re.getFrameExtents();if(i.multiply(ge),s.copy(re.mapSize),(i.x>f||i.y>f)&&(i.x>f&&(s.x=Math.floor(f/ge.x),i.x=s.x*ge.x,re.mapSize.x=s.x),i.y>f&&(s.y=Math.floor(f/ge.y),i.y=s.y*ge.y,re.mapSize.y=s.y)),re.map===null||te===!0||se===!0){const ze=this.type!==$i?{minFilter:Gn,magFilter:Gn}:{};re.map!==null&&re.map.dispose(),re.map=new us(i.x,i.y,ze),re.map.texture.name=de.name+".shadowMap",re.camera.updateProjectionMatrix()}r.setRenderTarget(re.map),r.clear();const be=re.getViewportCount();for(let ze=0;ze<be;ze++){const Ge=re.getViewport(ze);a.set(s.x*Ge.x,s.y*Ge.y,s.x*Ge.z,s.y*Ge.w),ee.viewport(a),re.updateMatrices(de,ze),n=re.getFrustum(),b(O,V,re.camera,de,this.type)}re.isPointLightShadow!==!0&&this.type===$i&&A(re,V),re.needsUpdate=!1}_=this.type,v.needsUpdate=!1,r.setRenderTarget(I,R,H)};function A(U,O){const V=e.update(E);m.defines.VSM_SAMPLES!==U.blurSamples&&(m.defines.VSM_SAMPLES=U.blurSamples,g.defines.VSM_SAMPLES=U.blurSamples,m.needsUpdate=!0,g.needsUpdate=!0),U.mapPass===null&&(U.mapPass=new us(i.x,i.y)),m.uniforms.shadow_pass.value=U.map.texture,m.uniforms.resolution.value=U.mapSize,m.uniforms.radius.value=U.radius,r.setRenderTarget(U.mapPass),r.clear(),r.renderBufferDirect(O,null,V,m,E,null),g.uniforms.shadow_pass.value=U.mapPass.texture,g.uniforms.resolution.value=U.mapSize,g.uniforms.radius.value=U.radius,r.setRenderTarget(U.map),r.clear(),r.renderBufferDirect(O,null,V,g,E,null)}function w(U,O,V,I){let R=null;const H=V.isPointLight===!0?U.customDistanceMaterial:U.customDepthMaterial;if(H!==void 0)R=H;else if(R=V.isPointLight===!0?u:c,r.localClippingEnabled&&O.clipShadows===!0&&Array.isArray(O.clippingPlanes)&&O.clippingPlanes.length!==0||O.displacementMap&&O.displacementScale!==0||O.alphaMap&&O.alphaTest>0||O.map&&O.alphaTest>0){const ee=R.uuid,te=O.uuid;let se=h[ee];se===void 0&&(se={},h[ee]=se);let he=se[te];he===void 0&&(he=R.clone(),se[te]=he,O.addEventListener("dispose",B)),R=he}if(R.visible=O.visible,R.wireframe=O.wireframe,I===$i?R.side=O.shadowSide!==null?O.shadowSide:O.side:R.side=O.shadowSide!==null?O.shadowSide:p[O.side],R.alphaMap=O.alphaMap,R.alphaTest=O.alphaTest,R.map=O.map,R.clipShadows=O.clipShadows,R.clippingPlanes=O.clippingPlanes,R.clipIntersection=O.clipIntersection,R.displacementMap=O.displacementMap,R.displacementScale=O.displacementScale,R.displacementBias=O.displacementBias,R.wireframeLinewidth=O.wireframeLinewidth,R.linewidth=O.linewidth,V.isPointLight===!0&&R.isMeshDistanceMaterial===!0){const ee=r.properties.get(R);ee.light=V}return R}function b(U,O,V,I,R){if(U.visible===!1)return;if(U.layers.test(O.layers)&&(U.isMesh||U.isLine||U.isPoints)&&(U.castShadow||U.receiveShadow&&R===$i)&&(!U.frustumCulled||n.intersectsObject(U))){U.modelViewMatrix.multiplyMatrices(V.matrixWorldInverse,U.matrixWorld);const te=e.update(U),se=U.material;if(Array.isArray(se)){const he=te.groups;for(let q=0,de=he.length;q<de;q++){const re=he[q],ge=se[re.materialIndex];if(ge&&ge.visible){const be=w(U,ge,I,R);U.onBeforeShadow(r,U,O,V,te,be,re),r.renderBufferDirect(V,null,te,be,U,re),U.onAfterShadow(r,U,O,V,te,be,re)}}}else if(se.visible){const he=w(U,se,I,R);U.onBeforeShadow(r,U,O,V,te,he,null),r.renderBufferDirect(V,null,te,he,U,null),U.onAfterShadow(r,U,O,V,te,he,null)}}const ee=U.children;for(let te=0,se=ee.length;te<se;te++)b(ee[te],O,V,I,R)}function B(U){U.target.removeEventListener("dispose",B);for(const V in h){const I=h[V],R=U.target.uuid;R in I&&(I[R].dispose(),delete I[R])}}}const fP={[vh]:yh,[xh]:Eh,[bh]:Mh,[Zs]:Sh,[yh]:vh,[Eh]:xh,[Mh]:bh,[Sh]:Zs};function pP(r,e){function t(){let X=!1;const Ae=new Ot;let P=null;const k=new Ot(0,0,0,0);return{setMask:function($){P!==$&&!X&&(r.colorMask($,$,$,$),P=$)},setLocked:function($){X=$},setClear:function($,ie,Te,Ee,De){De===!0&&($*=Ee,ie*=Ee,Te*=Ee),Ae.set($,ie,Te,Ee),k.equals(Ae)===!1&&(r.clearColor($,ie,Te,Ee),k.copy(Ae))},reset:function(){X=!1,P=null,k.set(-1,0,0,0)}}}function n(){let X=!1,Ae=!1,P=null,k=null,$=null;return{setReversed:function(ie){if(Ae!==ie){const Te=e.get("EXT_clip_control");Ae?Te.clipControlEXT(Te.LOWER_LEFT_EXT,Te.ZERO_TO_ONE_EXT):Te.clipControlEXT(Te.LOWER_LEFT_EXT,Te.NEGATIVE_ONE_TO_ONE_EXT);const Ee=$;$=null,this.setClear(Ee)}Ae=ie},getReversed:function(){return Ae},setTest:function(ie){ie?Se(r.DEPTH_TEST):$e(r.DEPTH_TEST)},setMask:function(ie){P!==ie&&!X&&(r.depthMask(ie),P=ie)},setFunc:function(ie){if(Ae&&(ie=fP[ie]),k!==ie){switch(ie){case vh:r.depthFunc(r.NEVER);break;case yh:r.depthFunc(r.ALWAYS);break;case xh:r.depthFunc(r.LESS);break;case Zs:r.depthFunc(r.LEQUAL);break;case bh:r.depthFunc(r.EQUAL);break;case Sh:r.depthFunc(r.GEQUAL);break;case Eh:r.depthFunc(r.GREATER);break;case Mh:r.depthFunc(r.NOTEQUAL);break;default:r.depthFunc(r.LEQUAL)}k=ie}},setLocked:function(ie){X=ie},setClear:function(ie){$!==ie&&(Ae&&(ie=1-ie),r.clearDepth(ie),$=ie)},reset:function(){X=!1,P=null,k=null,$=null,Ae=!1}}}function i(){let X=!1,Ae=null,P=null,k=null,$=null,ie=null,Te=null,Ee=null,De=null;return{setTest:function(Pe){X||(Pe?Se(r.STENCIL_TEST):$e(r.STENCIL_TEST))},setMask:function(Pe){Ae!==Pe&&!X&&(r.stencilMask(Pe),Ae=Pe)},setFunc:function(Pe,ut,bt){(P!==Pe||k!==ut||$!==bt)&&(r.stencilFunc(Pe,ut,bt),P=Pe,k=ut,$=bt)},setOp:function(Pe,ut,bt){(ie!==Pe||Te!==ut||Ee!==bt)&&(r.stencilOp(Pe,ut,bt),ie=Pe,Te=ut,Ee=bt)},setLocked:function(Pe){X=Pe},setClear:function(Pe){De!==Pe&&(r.clearStencil(Pe),De=Pe)},reset:function(){X=!1,Ae=null,P=null,k=null,$=null,ie=null,Te=null,Ee=null,De=null}}}const s=new t,a=new n,c=new i,u=new WeakMap,h=new WeakMap;let f={},p={},m=new WeakMap,g=[],x=null,E=!1,v=null,_=null,A=null,w=null,b=null,B=null,U=null,O=new st(0,0,0),V=0,I=!1,R=null,H=null,ee=null,te=null,se=null;const he=r.getParameter(r.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let q=!1,de=0;const re=r.getParameter(r.VERSION);re.indexOf("WebGL")!==-1?(de=parseFloat(/^WebGL (\d)/.exec(re)[1]),q=de>=1):re.indexOf("OpenGL ES")!==-1&&(de=parseFloat(/^OpenGL ES (\d)/.exec(re)[1]),q=de>=2);let ge=null,be={};const ze=r.getParameter(r.SCISSOR_BOX),Ge=r.getParameter(r.VIEWPORT),pt=new Ot().fromArray(ze),le=new Ot().fromArray(Ge);function me(X,Ae,P,k){const $=new Uint8Array(4),ie=r.createTexture();r.bindTexture(X,ie),r.texParameteri(X,r.TEXTURE_MIN_FILTER,r.NEAREST),r.texParameteri(X,r.TEXTURE_MAG_FILTER,r.NEAREST);for(let Te=0;Te<P;Te++)X===r.TEXTURE_3D||X===r.TEXTURE_2D_ARRAY?r.texImage3D(Ae,0,r.RGBA,1,1,k,0,r.RGBA,r.UNSIGNED_BYTE,$):r.texImage2D(Ae+Te,0,r.RGBA,1,1,0,r.RGBA,r.UNSIGNED_BYTE,$);return ie}const Ue={};Ue[r.TEXTURE_2D]=me(r.TEXTURE_2D,r.TEXTURE_2D,1),Ue[r.TEXTURE_CUBE_MAP]=me(r.TEXTURE_CUBE_MAP,r.TEXTURE_CUBE_MAP_POSITIVE_X,6),Ue[r.TEXTURE_2D_ARRAY]=me(r.TEXTURE_2D_ARRAY,r.TEXTURE_2D_ARRAY,1,1),Ue[r.TEXTURE_3D]=me(r.TEXTURE_3D,r.TEXTURE_3D,1,1),s.setClear(0,0,0,1),a.setClear(1),c.setClear(0),Se(r.DEPTH_TEST),a.setFunc(Zs),Ke(!1),Qe(wp),Se(r.CULL_FACE),G(Er);function Se(X){f[X]!==!0&&(r.enable(X),f[X]=!0)}function $e(X){f[X]!==!1&&(r.disable(X),f[X]=!1)}function it(X,Ae){return p[X]!==Ae?(r.bindFramebuffer(X,Ae),p[X]=Ae,X===r.DRAW_FRAMEBUFFER&&(p[r.FRAMEBUFFER]=Ae),X===r.FRAMEBUFFER&&(p[r.DRAW_FRAMEBUFFER]=Ae),!0):!1}function Je(X,Ae){let P=g,k=!1;if(X){P=m.get(Ae),P===void 0&&(P=[],m.set(Ae,P));const $=X.textures;if(P.length!==$.length||P[0]!==r.COLOR_ATTACHMENT0){for(let ie=0,Te=$.length;ie<Te;ie++)P[ie]=r.COLOR_ATTACHMENT0+ie;P.length=$.length,k=!0}}else P[0]!==r.BACK&&(P[0]=r.BACK,k=!0);k&&r.drawBuffers(P)}function pe(X){return x!==X?(r.useProgram(X),x=X,!0):!1}const ve={[os]:r.FUNC_ADD,[fM]:r.FUNC_SUBTRACT,[pM]:r.FUNC_REVERSE_SUBTRACT};ve[mM]=r.MIN,ve[gM]=r.MAX;const Le={[_M]:r.ZERO,[vM]:r.ONE,[yM]:r.SRC_COLOR,[gh]:r.SRC_ALPHA,[TM]:r.SRC_ALPHA_SATURATE,[EM]:r.DST_COLOR,[bM]:r.DST_ALPHA,[xM]:r.ONE_MINUS_SRC_COLOR,[_h]:r.ONE_MINUS_SRC_ALPHA,[MM]:r.ONE_MINUS_DST_COLOR,[SM]:r.ONE_MINUS_DST_ALPHA,[wM]:r.CONSTANT_COLOR,[AM]:r.ONE_MINUS_CONSTANT_COLOR,[RM]:r.CONSTANT_ALPHA,[PM]:r.ONE_MINUS_CONSTANT_ALPHA};function G(X,Ae,P,k,$,ie,Te,Ee,De,Pe){if(X===Er){E===!0&&($e(r.BLEND),E=!1);return}if(E===!1&&(Se(r.BLEND),E=!0),X!==dM){if(X!==v||Pe!==I){if((_!==os||b!==os)&&(r.blendEquation(r.FUNC_ADD),_=os,b=os),Pe)switch(X){case qs:r.blendFuncSeparate(r.ONE,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Ap:r.blendFunc(r.ONE,r.ONE);break;case Rp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Pp:r.blendFuncSeparate(r.ZERO,r.SRC_COLOR,r.ZERO,r.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",X);break}else switch(X){case qs:r.blendFuncSeparate(r.SRC_ALPHA,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Ap:r.blendFunc(r.SRC_ALPHA,r.ONE);break;case Rp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Pp:r.blendFunc(r.ZERO,r.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",X);break}A=null,w=null,B=null,U=null,O.set(0,0,0),V=0,v=X,I=Pe}return}$=$||Ae,ie=ie||P,Te=Te||k,(Ae!==_||$!==b)&&(r.blendEquationSeparate(ve[Ae],ve[$]),_=Ae,b=$),(P!==A||k!==w||ie!==B||Te!==U)&&(r.blendFuncSeparate(Le[P],Le[k],Le[ie],Le[Te]),A=P,w=k,B=ie,U=Te),(Ee.equals(O)===!1||De!==V)&&(r.blendColor(Ee.r,Ee.g,Ee.b,De),O.copy(Ee),V=De),v=X,I=!1}function tt(X,Ae){X.side===Kn?$e(r.CULL_FACE):Se(r.CULL_FACE);let P=X.side===$n;Ae&&(P=!P),Ke(P),X.blending===qs&&X.transparent===!1?G(Er):G(X.blending,X.blendEquation,X.blendSrc,X.blendDst,X.blendEquationAlpha,X.blendSrcAlpha,X.blendDstAlpha,X.blendColor,X.blendAlpha,X.premultipliedAlpha),a.setFunc(X.depthFunc),a.setTest(X.depthTest),a.setMask(X.depthWrite),s.setMask(X.colorWrite);const k=X.stencilWrite;c.setTest(k),k&&(c.setMask(X.stencilWriteMask),c.setFunc(X.stencilFunc,X.stencilRef,X.stencilFuncMask),c.setOp(X.stencilFail,X.stencilZFail,X.stencilZPass)),rt(X.polygonOffset,X.polygonOffsetFactor,X.polygonOffsetUnits),X.alphaToCoverage===!0?Se(r.SAMPLE_ALPHA_TO_COVERAGE):$e(r.SAMPLE_ALPHA_TO_COVERAGE)}function Ke(X){R!==X&&(X?r.frontFace(r.CW):r.frontFace(r.CCW),R=X)}function Qe(X){X!==lM?(Se(r.CULL_FACE),X!==H&&(X===wp?r.cullFace(r.BACK):X===uM?r.cullFace(r.FRONT):r.cullFace(r.FRONT_AND_BACK))):$e(r.CULL_FACE),H=X}function Oe(X){X!==ee&&(q&&r.lineWidth(X),ee=X)}function rt(X,Ae,P){X?(Se(r.POLYGON_OFFSET_FILL),(te!==Ae||se!==P)&&(r.polygonOffset(Ae,P),te=Ae,se=P)):$e(r.POLYGON_OFFSET_FILL)}function Fe(X){X?Se(r.SCISSOR_TEST):$e(r.SCISSOR_TEST)}function F(X){X===void 0&&(X=r.TEXTURE0+he-1),ge!==X&&(r.activeTexture(X),ge=X)}function T(X,Ae,P){P===void 0&&(ge===null?P=r.TEXTURE0+he-1:P=ge);let k=be[P];k===void 0&&(k={type:void 0,texture:void 0},be[P]=k),(k.type!==X||k.texture!==Ae)&&(ge!==P&&(r.activeTexture(P),ge=P),r.bindTexture(X,Ae||Ue[X]),k.type=X,k.texture=Ae)}function Z(){const X=be[ge];X!==void 0&&X.type!==void 0&&(r.bindTexture(X.type,null),X.type=void 0,X.texture=void 0)}function ce(){try{r.compressedTexImage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function fe(){try{r.compressedTexImage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function ue(){try{r.texSubImage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function ke(){try{r.texSubImage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function we(){try{r.compressedTexSubImage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function Be(){try{r.compressedTexSubImage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function gt(){try{r.texStorage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function _e(){try{r.texStorage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function He(){try{r.texImage2D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function We(){try{r.texImage3D.apply(r,arguments)}catch(X){console.error("THREE.WebGLState:",X)}}function ot(X){pt.equals(X)===!1&&(r.scissor(X.x,X.y,X.z,X.w),pt.copy(X))}function Ve(X){le.equals(X)===!1&&(r.viewport(X.x,X.y,X.z,X.w),le.copy(X))}function xt(X,Ae){let P=h.get(Ae);P===void 0&&(P=new WeakMap,h.set(Ae,P));let k=P.get(X);k===void 0&&(k=r.getUniformBlockIndex(Ae,X.name),P.set(X,k))}function dt(X,Ae){const k=h.get(Ae).get(X);u.get(Ae)!==k&&(r.uniformBlockBinding(Ae,k,X.__bindingPointIndex),u.set(Ae,k))}function It(){r.disable(r.BLEND),r.disable(r.CULL_FACE),r.disable(r.DEPTH_TEST),r.disable(r.POLYGON_OFFSET_FILL),r.disable(r.SCISSOR_TEST),r.disable(r.STENCIL_TEST),r.disable(r.SAMPLE_ALPHA_TO_COVERAGE),r.blendEquation(r.FUNC_ADD),r.blendFunc(r.ONE,r.ZERO),r.blendFuncSeparate(r.ONE,r.ZERO,r.ONE,r.ZERO),r.blendColor(0,0,0,0),r.colorMask(!0,!0,!0,!0),r.clearColor(0,0,0,0),r.depthMask(!0),r.depthFunc(r.LESS),a.setReversed(!1),r.clearDepth(1),r.stencilMask(4294967295),r.stencilFunc(r.ALWAYS,0,4294967295),r.stencilOp(r.KEEP,r.KEEP,r.KEEP),r.clearStencil(0),r.cullFace(r.BACK),r.frontFace(r.CCW),r.polygonOffset(0,0),r.activeTexture(r.TEXTURE0),r.bindFramebuffer(r.FRAMEBUFFER,null),r.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),r.bindFramebuffer(r.READ_FRAMEBUFFER,null),r.useProgram(null),r.lineWidth(1),r.scissor(0,0,r.canvas.width,r.canvas.height),r.viewport(0,0,r.canvas.width,r.canvas.height),f={},ge=null,be={},p={},m=new WeakMap,g=[],x=null,E=!1,v=null,_=null,A=null,w=null,b=null,B=null,U=null,O=new st(0,0,0),V=0,I=!1,R=null,H=null,ee=null,te=null,se=null,pt.set(0,0,r.canvas.width,r.canvas.height),le.set(0,0,r.canvas.width,r.canvas.height),s.reset(),a.reset(),c.reset()}return{buffers:{color:s,depth:a,stencil:c},enable:Se,disable:$e,bindFramebuffer:it,drawBuffers:Je,useProgram:pe,setBlending:G,setMaterial:tt,setFlipSided:Ke,setCullFace:Qe,setLineWidth:Oe,setPolygonOffset:rt,setScissorTest:Fe,activeTexture:F,bindTexture:T,unbindTexture:Z,compressedTexImage2D:ce,compressedTexImage3D:fe,texImage2D:He,texImage3D:We,updateUBOMapping:xt,uniformBlockBinding:dt,texStorage2D:gt,texStorage3D:_e,texSubImage2D:ue,texSubImage3D:ke,compressedTexSubImage2D:we,compressedTexSubImage3D:Be,scissor:ot,viewport:Ve,reset:It}}function Mm(r,e,t,n){const i=mP(n);switch(t){case vg:return r*e;case xg:return r*e;case bg:return r*e*2;case dd:return r*e/i.components*i.byteLength;case fd:return r*e/i.components*i.byteLength;case Sg:return r*e*2/i.components*i.byteLength;case pd:return r*e*2/i.components*i.byteLength;case yg:return r*e*3/i.components*i.byteLength;case fi:return r*e*4/i.components*i.byteLength;case md:return r*e*4/i.components*i.byteLength;case Tc:case wc:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Ac:case Rc:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Rh:case Ch:return Math.max(r,16)*Math.max(e,8)/4;case Ah:case Ph:return Math.max(r,8)*Math.max(e,8)/2;case Dh:case Ih:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Lh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Fh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Nh:return Math.floor((r+4)/5)*Math.floor((e+3)/4)*16;case Oh:return Math.floor((r+4)/5)*Math.floor((e+4)/5)*16;case Uh:return Math.floor((r+5)/6)*Math.floor((e+4)/5)*16;case Bh:return Math.floor((r+5)/6)*Math.floor((e+5)/6)*16;case kh:return Math.floor((r+7)/8)*Math.floor((e+4)/5)*16;case zh:return Math.floor((r+7)/8)*Math.floor((e+5)/6)*16;case Hh:return Math.floor((r+7)/8)*Math.floor((e+7)/8)*16;case Vh:return Math.floor((r+9)/10)*Math.floor((e+4)/5)*16;case Gh:return Math.floor((r+9)/10)*Math.floor((e+5)/6)*16;case Wh:return Math.floor((r+9)/10)*Math.floor((e+7)/8)*16;case jh:return Math.floor((r+9)/10)*Math.floor((e+9)/10)*16;case Xh:return Math.floor((r+11)/12)*Math.floor((e+9)/10)*16;case qh:return Math.floor((r+11)/12)*Math.floor((e+11)/12)*16;case Pc:case Yh:case Kh:return Math.ceil(r/4)*Math.ceil(e/4)*16;case Eg:case $h:return Math.ceil(r/4)*Math.ceil(e/4)*8;case Zh:case Qh:return Math.ceil(r/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function mP(r){switch(r){case ir:case mg:return{byteLength:1,components:1};case Jo:case gg:case ia:return{byteLength:2,components:1};case ud:case hd:return{byteLength:2,components:4};case ls:case ld:case Si:return{byteLength:4,components:1};case _g:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${r}.`)}function gP(r,e,t,n,i,s,a){const c=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,u=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),h=new lt,f=new WeakMap;let p;const m=new WeakMap;let g=!1;try{g=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function x(F,T){return g?new OffscreenCanvas(F,T):na("canvas")}function E(F,T,Z){let ce=1;const fe=Fe(F);if((fe.width>Z||fe.height>Z)&&(ce=Z/Math.max(fe.width,fe.height)),ce<1)if(typeof HTMLImageElement<"u"&&F instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&F instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&F instanceof ImageBitmap||typeof VideoFrame<"u"&&F instanceof VideoFrame){const ue=Math.floor(ce*fe.width),ke=Math.floor(ce*fe.height);p===void 0&&(p=x(ue,ke));const we=T?x(ue,ke):p;return we.width=ue,we.height=ke,we.getContext("2d").drawImage(F,0,0,ue,ke),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+fe.width+"x"+fe.height+") to ("+ue+"x"+ke+")."),we}else return"data"in F&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+fe.width+"x"+fe.height+")."),F;return F}function v(F){return F.generateMipmaps}function _(F){r.generateMipmap(F)}function A(F){return F.isWebGLCubeRenderTarget?r.TEXTURE_CUBE_MAP:F.isWebGL3DRenderTarget?r.TEXTURE_3D:F.isWebGLArrayRenderTarget||F.isCompressedArrayTexture?r.TEXTURE_2D_ARRAY:r.TEXTURE_2D}function w(F,T,Z,ce,fe=!1){if(F!==null){if(r[F]!==void 0)return r[F];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+F+"'")}let ue=T;if(T===r.RED&&(Z===r.FLOAT&&(ue=r.R32F),Z===r.HALF_FLOAT&&(ue=r.R16F),Z===r.UNSIGNED_BYTE&&(ue=r.R8)),T===r.RED_INTEGER&&(Z===r.UNSIGNED_BYTE&&(ue=r.R8UI),Z===r.UNSIGNED_SHORT&&(ue=r.R16UI),Z===r.UNSIGNED_INT&&(ue=r.R32UI),Z===r.BYTE&&(ue=r.R8I),Z===r.SHORT&&(ue=r.R16I),Z===r.INT&&(ue=r.R32I)),T===r.RG&&(Z===r.FLOAT&&(ue=r.RG32F),Z===r.HALF_FLOAT&&(ue=r.RG16F),Z===r.UNSIGNED_BYTE&&(ue=r.RG8)),T===r.RG_INTEGER&&(Z===r.UNSIGNED_BYTE&&(ue=r.RG8UI),Z===r.UNSIGNED_SHORT&&(ue=r.RG16UI),Z===r.UNSIGNED_INT&&(ue=r.RG32UI),Z===r.BYTE&&(ue=r.RG8I),Z===r.SHORT&&(ue=r.RG16I),Z===r.INT&&(ue=r.RG32I)),T===r.RGB_INTEGER&&(Z===r.UNSIGNED_BYTE&&(ue=r.RGB8UI),Z===r.UNSIGNED_SHORT&&(ue=r.RGB16UI),Z===r.UNSIGNED_INT&&(ue=r.RGB32UI),Z===r.BYTE&&(ue=r.RGB8I),Z===r.SHORT&&(ue=r.RGB16I),Z===r.INT&&(ue=r.RGB32I)),T===r.RGBA_INTEGER&&(Z===r.UNSIGNED_BYTE&&(ue=r.RGBA8UI),Z===r.UNSIGNED_SHORT&&(ue=r.RGBA16UI),Z===r.UNSIGNED_INT&&(ue=r.RGBA32UI),Z===r.BYTE&&(ue=r.RGBA8I),Z===r.SHORT&&(ue=r.RGBA16I),Z===r.INT&&(ue=r.RGBA32I)),T===r.RGB&&Z===r.UNSIGNED_INT_5_9_9_9_REV&&(ue=r.RGB9_E5),T===r.RGBA){const ke=fe?zc:Ct.getTransfer(ce);Z===r.FLOAT&&(ue=r.RGBA32F),Z===r.HALF_FLOAT&&(ue=r.RGBA16F),Z===r.UNSIGNED_BYTE&&(ue=ke===Gt?r.SRGB8_ALPHA8:r.RGBA8),Z===r.UNSIGNED_SHORT_4_4_4_4&&(ue=r.RGBA4),Z===r.UNSIGNED_SHORT_5_5_5_1&&(ue=r.RGB5_A1)}return(ue===r.R16F||ue===r.R32F||ue===r.RG16F||ue===r.RG32F||ue===r.RGBA16F||ue===r.RGBA32F)&&e.get("EXT_color_buffer_float"),ue}function b(F,T){let Z;return F?T===null||T===ls||T===to?Z=r.DEPTH24_STENCIL8:T===Si?Z=r.DEPTH32F_STENCIL8:T===Jo&&(Z=r.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):T===null||T===ls||T===to?Z=r.DEPTH_COMPONENT24:T===Si?Z=r.DEPTH_COMPONENT32F:T===Jo&&(Z=r.DEPTH_COMPONENT16),Z}function B(F,T){return v(F)===!0||F.isFramebufferTexture&&F.minFilter!==Gn&&F.minFilter!==ai?Math.log2(Math.max(T.width,T.height))+1:F.mipmaps!==void 0&&F.mipmaps.length>0?F.mipmaps.length:F.isCompressedTexture&&Array.isArray(F.image)?T.mipmaps.length:1}function U(F){const T=F.target;T.removeEventListener("dispose",U),V(T),T.isVideoTexture&&f.delete(T)}function O(F){const T=F.target;T.removeEventListener("dispose",O),R(T)}function V(F){const T=n.get(F);if(T.__webglInit===void 0)return;const Z=F.source,ce=m.get(Z);if(ce){const fe=ce[T.__cacheKey];fe.usedTimes--,fe.usedTimes===0&&I(F),Object.keys(ce).length===0&&m.delete(Z)}n.remove(F)}function I(F){const T=n.get(F);r.deleteTexture(T.__webglTexture);const Z=F.source,ce=m.get(Z);delete ce[T.__cacheKey],a.memory.textures--}function R(F){const T=n.get(F);if(F.depthTexture&&(F.depthTexture.dispose(),n.remove(F.depthTexture)),F.isWebGLCubeRenderTarget)for(let ce=0;ce<6;ce++){if(Array.isArray(T.__webglFramebuffer[ce]))for(let fe=0;fe<T.__webglFramebuffer[ce].length;fe++)r.deleteFramebuffer(T.__webglFramebuffer[ce][fe]);else r.deleteFramebuffer(T.__webglFramebuffer[ce]);T.__webglDepthbuffer&&r.deleteRenderbuffer(T.__webglDepthbuffer[ce])}else{if(Array.isArray(T.__webglFramebuffer))for(let ce=0;ce<T.__webglFramebuffer.length;ce++)r.deleteFramebuffer(T.__webglFramebuffer[ce]);else r.deleteFramebuffer(T.__webglFramebuffer);if(T.__webglDepthbuffer&&r.deleteRenderbuffer(T.__webglDepthbuffer),T.__webglMultisampledFramebuffer&&r.deleteFramebuffer(T.__webglMultisampledFramebuffer),T.__webglColorRenderbuffer)for(let ce=0;ce<T.__webglColorRenderbuffer.length;ce++)T.__webglColorRenderbuffer[ce]&&r.deleteRenderbuffer(T.__webglColorRenderbuffer[ce]);T.__webglDepthRenderbuffer&&r.deleteRenderbuffer(T.__webglDepthRenderbuffer)}const Z=F.textures;for(let ce=0,fe=Z.length;ce<fe;ce++){const ue=n.get(Z[ce]);ue.__webglTexture&&(r.deleteTexture(ue.__webglTexture),a.memory.textures--),n.remove(Z[ce])}n.remove(F)}let H=0;function ee(){H=0}function te(){const F=H;return F>=i.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+F+" texture units while this GPU supports only "+i.maxTextures),H+=1,F}function se(F){const T=[];return T.push(F.wrapS),T.push(F.wrapT),T.push(F.wrapR||0),T.push(F.magFilter),T.push(F.minFilter),T.push(F.anisotropy),T.push(F.internalFormat),T.push(F.format),T.push(F.type),T.push(F.generateMipmaps),T.push(F.premultiplyAlpha),T.push(F.flipY),T.push(F.unpackAlignment),T.push(F.colorSpace),T.join()}function he(F,T){const Z=n.get(F);if(F.isVideoTexture&&Oe(F),F.isRenderTargetTexture===!1&&F.version>0&&Z.__version!==F.version){const ce=F.image;if(ce===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(ce.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{le(Z,F,T);return}}t.bindTexture(r.TEXTURE_2D,Z.__webglTexture,r.TEXTURE0+T)}function q(F,T){const Z=n.get(F);if(F.version>0&&Z.__version!==F.version){le(Z,F,T);return}t.bindTexture(r.TEXTURE_2D_ARRAY,Z.__webglTexture,r.TEXTURE0+T)}function de(F,T){const Z=n.get(F);if(F.version>0&&Z.__version!==F.version){le(Z,F,T);return}t.bindTexture(r.TEXTURE_3D,Z.__webglTexture,r.TEXTURE0+T)}function re(F,T){const Z=n.get(F);if(F.version>0&&Z.__version!==F.version){me(Z,F,T);return}t.bindTexture(r.TEXTURE_CUBE_MAP,Z.__webglTexture,r.TEXTURE0+T)}const ge={[eo]:r.REPEAT,[br]:r.CLAMP_TO_EDGE,[Fc]:r.MIRRORED_REPEAT},be={[Gn]:r.NEAREST,[pg]:r.NEAREST_MIPMAP_NEAREST,[Wo]:r.NEAREST_MIPMAP_LINEAR,[ai]:r.LINEAR,[Mc]:r.LINEAR_MIPMAP_NEAREST,[Qi]:r.LINEAR_MIPMAP_LINEAR},ze={[XM]:r.NEVER,[QM]:r.ALWAYS,[qM]:r.LESS,[wg]:r.LEQUAL,[YM]:r.EQUAL,[ZM]:r.GEQUAL,[KM]:r.GREATER,[$M]:r.NOTEQUAL};function Ge(F,T){if(T.type===Si&&e.has("OES_texture_float_linear")===!1&&(T.magFilter===ai||T.magFilter===Mc||T.magFilter===Wo||T.magFilter===Qi||T.minFilter===ai||T.minFilter===Mc||T.minFilter===Wo||T.minFilter===Qi)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),r.texParameteri(F,r.TEXTURE_WRAP_S,ge[T.wrapS]),r.texParameteri(F,r.TEXTURE_WRAP_T,ge[T.wrapT]),(F===r.TEXTURE_3D||F===r.TEXTURE_2D_ARRAY)&&r.texParameteri(F,r.TEXTURE_WRAP_R,ge[T.wrapR]),r.texParameteri(F,r.TEXTURE_MAG_FILTER,be[T.magFilter]),r.texParameteri(F,r.TEXTURE_MIN_FILTER,be[T.minFilter]),T.compareFunction&&(r.texParameteri(F,r.TEXTURE_COMPARE_MODE,r.COMPARE_REF_TO_TEXTURE),r.texParameteri(F,r.TEXTURE_COMPARE_FUNC,ze[T.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(T.magFilter===Gn||T.minFilter!==Wo&&T.minFilter!==Qi||T.type===Si&&e.has("OES_texture_float_linear")===!1)return;if(T.anisotropy>1||n.get(T).__currentAnisotropy){const Z=e.get("EXT_texture_filter_anisotropic");r.texParameterf(F,Z.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(T.anisotropy,i.getMaxAnisotropy())),n.get(T).__currentAnisotropy=T.anisotropy}}}function pt(F,T){let Z=!1;F.__webglInit===void 0&&(F.__webglInit=!0,T.addEventListener("dispose",U));const ce=T.source;let fe=m.get(ce);fe===void 0&&(fe={},m.set(ce,fe));const ue=se(T);if(ue!==F.__cacheKey){fe[ue]===void 0&&(fe[ue]={texture:r.createTexture(),usedTimes:0},a.memory.textures++,Z=!0),fe[ue].usedTimes++;const ke=fe[F.__cacheKey];ke!==void 0&&(fe[F.__cacheKey].usedTimes--,ke.usedTimes===0&&I(T)),F.__cacheKey=ue,F.__webglTexture=fe[ue].texture}return Z}function le(F,T,Z){let ce=r.TEXTURE_2D;(T.isDataArrayTexture||T.isCompressedArrayTexture)&&(ce=r.TEXTURE_2D_ARRAY),T.isData3DTexture&&(ce=r.TEXTURE_3D);const fe=pt(F,T),ue=T.source;t.bindTexture(ce,F.__webglTexture,r.TEXTURE0+Z);const ke=n.get(ue);if(ue.version!==ke.__version||fe===!0){t.activeTexture(r.TEXTURE0+Z);const we=Ct.getPrimaries(Ct.workingColorSpace),Be=T.colorSpace===xr?null:Ct.getPrimaries(T.colorSpace),gt=T.colorSpace===xr||we===Be?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,T.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,T.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,gt);let _e=E(T.image,!1,i.maxTextureSize);_e=rt(T,_e);const He=s.convert(T.format,T.colorSpace),We=s.convert(T.type);let ot=w(T.internalFormat,He,We,T.colorSpace,T.isVideoTexture);Ge(ce,T);let Ve;const xt=T.mipmaps,dt=T.isVideoTexture!==!0,It=ke.__version===void 0||fe===!0,X=ue.dataReady,Ae=B(T,_e);if(T.isDepthTexture)ot=b(T.format===no,T.type),It&&(dt?t.texStorage2D(r.TEXTURE_2D,1,ot,_e.width,_e.height):t.texImage2D(r.TEXTURE_2D,0,ot,_e.width,_e.height,0,He,We,null));else if(T.isDataTexture)if(xt.length>0){dt&&It&&t.texStorage2D(r.TEXTURE_2D,Ae,ot,xt[0].width,xt[0].height);for(let P=0,k=xt.length;P<k;P++)Ve=xt[P],dt?X&&t.texSubImage2D(r.TEXTURE_2D,P,0,0,Ve.width,Ve.height,He,We,Ve.data):t.texImage2D(r.TEXTURE_2D,P,ot,Ve.width,Ve.height,0,He,We,Ve.data);T.generateMipmaps=!1}else dt?(It&&t.texStorage2D(r.TEXTURE_2D,Ae,ot,_e.width,_e.height),X&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,_e.width,_e.height,He,We,_e.data)):t.texImage2D(r.TEXTURE_2D,0,ot,_e.width,_e.height,0,He,We,_e.data);else if(T.isCompressedTexture)if(T.isCompressedArrayTexture){dt&&It&&t.texStorage3D(r.TEXTURE_2D_ARRAY,Ae,ot,xt[0].width,xt[0].height,_e.depth);for(let P=0,k=xt.length;P<k;P++)if(Ve=xt[P],T.format!==fi)if(He!==null)if(dt){if(X)if(T.layerUpdates.size>0){const $=Mm(Ve.width,Ve.height,T.format,T.type);for(const ie of T.layerUpdates){const Te=Ve.data.subarray(ie*$/Ve.data.BYTES_PER_ELEMENT,(ie+1)*$/Ve.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,P,0,0,ie,Ve.width,Ve.height,1,He,Te)}T.clearLayerUpdates()}else t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,P,0,0,0,Ve.width,Ve.height,_e.depth,He,Ve.data)}else t.compressedTexImage3D(r.TEXTURE_2D_ARRAY,P,ot,Ve.width,Ve.height,_e.depth,0,Ve.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else dt?X&&t.texSubImage3D(r.TEXTURE_2D_ARRAY,P,0,0,0,Ve.width,Ve.height,_e.depth,He,We,Ve.data):t.texImage3D(r.TEXTURE_2D_ARRAY,P,ot,Ve.width,Ve.height,_e.depth,0,He,We,Ve.data)}else{dt&&It&&t.texStorage2D(r.TEXTURE_2D,Ae,ot,xt[0].width,xt[0].height);for(let P=0,k=xt.length;P<k;P++)Ve=xt[P],T.format!==fi?He!==null?dt?X&&t.compressedTexSubImage2D(r.TEXTURE_2D,P,0,0,Ve.width,Ve.height,He,Ve.data):t.compressedTexImage2D(r.TEXTURE_2D,P,ot,Ve.width,Ve.height,0,Ve.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):dt?X&&t.texSubImage2D(r.TEXTURE_2D,P,0,0,Ve.width,Ve.height,He,We,Ve.data):t.texImage2D(r.TEXTURE_2D,P,ot,Ve.width,Ve.height,0,He,We,Ve.data)}else if(T.isDataArrayTexture)if(dt){if(It&&t.texStorage3D(r.TEXTURE_2D_ARRAY,Ae,ot,_e.width,_e.height,_e.depth),X)if(T.layerUpdates.size>0){const P=Mm(_e.width,_e.height,T.format,T.type);for(const k of T.layerUpdates){const $=_e.data.subarray(k*P/_e.data.BYTES_PER_ELEMENT,(k+1)*P/_e.data.BYTES_PER_ELEMENT);t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,k,_e.width,_e.height,1,He,We,$)}T.clearLayerUpdates()}else t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,0,_e.width,_e.height,_e.depth,He,We,_e.data)}else t.texImage3D(r.TEXTURE_2D_ARRAY,0,ot,_e.width,_e.height,_e.depth,0,He,We,_e.data);else if(T.isData3DTexture)dt?(It&&t.texStorage3D(r.TEXTURE_3D,Ae,ot,_e.width,_e.height,_e.depth),X&&t.texSubImage3D(r.TEXTURE_3D,0,0,0,0,_e.width,_e.height,_e.depth,He,We,_e.data)):t.texImage3D(r.TEXTURE_3D,0,ot,_e.width,_e.height,_e.depth,0,He,We,_e.data);else if(T.isFramebufferTexture){if(It)if(dt)t.texStorage2D(r.TEXTURE_2D,Ae,ot,_e.width,_e.height);else{let P=_e.width,k=_e.height;for(let $=0;$<Ae;$++)t.texImage2D(r.TEXTURE_2D,$,ot,P,k,0,He,We,null),P>>=1,k>>=1}}else if(xt.length>0){if(dt&&It){const P=Fe(xt[0]);t.texStorage2D(r.TEXTURE_2D,Ae,ot,P.width,P.height)}for(let P=0,k=xt.length;P<k;P++)Ve=xt[P],dt?X&&t.texSubImage2D(r.TEXTURE_2D,P,0,0,He,We,Ve):t.texImage2D(r.TEXTURE_2D,P,ot,He,We,Ve);T.generateMipmaps=!1}else if(dt){if(It){const P=Fe(_e);t.texStorage2D(r.TEXTURE_2D,Ae,ot,P.width,P.height)}X&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,He,We,_e)}else t.texImage2D(r.TEXTURE_2D,0,ot,He,We,_e);v(T)&&_(ce),ke.__version=ue.version,T.onUpdate&&T.onUpdate(T)}F.__version=T.version}function me(F,T,Z){if(T.image.length!==6)return;const ce=pt(F,T),fe=T.source;t.bindTexture(r.TEXTURE_CUBE_MAP,F.__webglTexture,r.TEXTURE0+Z);const ue=n.get(fe);if(fe.version!==ue.__version||ce===!0){t.activeTexture(r.TEXTURE0+Z);const ke=Ct.getPrimaries(Ct.workingColorSpace),we=T.colorSpace===xr?null:Ct.getPrimaries(T.colorSpace),Be=T.colorSpace===xr||ke===we?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,T.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,T.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,T.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,Be);const gt=T.isCompressedTexture||T.image[0].isCompressedTexture,_e=T.image[0]&&T.image[0].isDataTexture,He=[];for(let k=0;k<6;k++)!gt&&!_e?He[k]=E(T.image[k],!0,i.maxCubemapSize):He[k]=_e?T.image[k].image:T.image[k],He[k]=rt(T,He[k]);const We=He[0],ot=s.convert(T.format,T.colorSpace),Ve=s.convert(T.type),xt=w(T.internalFormat,ot,Ve,T.colorSpace),dt=T.isVideoTexture!==!0,It=ue.__version===void 0||ce===!0,X=fe.dataReady;let Ae=B(T,We);Ge(r.TEXTURE_CUBE_MAP,T);let P;if(gt){dt&&It&&t.texStorage2D(r.TEXTURE_CUBE_MAP,Ae,xt,We.width,We.height);for(let k=0;k<6;k++){P=He[k].mipmaps;for(let $=0;$<P.length;$++){const ie=P[$];T.format!==fi?ot!==null?dt?X&&t.compressedTexSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,$,0,0,ie.width,ie.height,ot,ie.data):t.compressedTexImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,$,xt,ie.width,ie.height,0,ie.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):dt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,$,0,0,ie.width,ie.height,ot,Ve,ie.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,$,xt,ie.width,ie.height,0,ot,Ve,ie.data)}}}else{if(P=T.mipmaps,dt&&It){P.length>0&&Ae++;const k=Fe(He[0]);t.texStorage2D(r.TEXTURE_CUBE_MAP,Ae,xt,k.width,k.height)}for(let k=0;k<6;k++)if(_e){dt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,0,0,0,He[k].width,He[k].height,ot,Ve,He[k].data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,0,xt,He[k].width,He[k].height,0,ot,Ve,He[k].data);for(let $=0;$<P.length;$++){const Te=P[$].image[k].image;dt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,$+1,0,0,Te.width,Te.height,ot,Ve,Te.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,$+1,xt,Te.width,Te.height,0,ot,Ve,Te.data)}}else{dt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,0,0,0,ot,Ve,He[k]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,0,xt,ot,Ve,He[k]);for(let $=0;$<P.length;$++){const ie=P[$];dt?X&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,$+1,0,0,ot,Ve,ie.image[k]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+k,$+1,xt,ot,Ve,ie.image[k])}}}v(T)&&_(r.TEXTURE_CUBE_MAP),ue.__version=fe.version,T.onUpdate&&T.onUpdate(T)}F.__version=T.version}function Ue(F,T,Z,ce,fe,ue){const ke=s.convert(Z.format,Z.colorSpace),we=s.convert(Z.type),Be=w(Z.internalFormat,ke,we,Z.colorSpace),gt=n.get(T),_e=n.get(Z);if(_e.__renderTarget=T,!gt.__hasExternalTextures){const He=Math.max(1,T.width>>ue),We=Math.max(1,T.height>>ue);fe===r.TEXTURE_3D||fe===r.TEXTURE_2D_ARRAY?t.texImage3D(fe,ue,Be,He,We,T.depth,0,ke,we,null):t.texImage2D(fe,ue,Be,He,We,0,ke,we,null)}t.bindFramebuffer(r.FRAMEBUFFER,F),Qe(T)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,ce,fe,_e.__webglTexture,0,Ke(T)):(fe===r.TEXTURE_2D||fe>=r.TEXTURE_CUBE_MAP_POSITIVE_X&&fe<=r.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&r.framebufferTexture2D(r.FRAMEBUFFER,ce,fe,_e.__webglTexture,ue),t.bindFramebuffer(r.FRAMEBUFFER,null)}function Se(F,T,Z){if(r.bindRenderbuffer(r.RENDERBUFFER,F),T.depthBuffer){const ce=T.depthTexture,fe=ce&&ce.isDepthTexture?ce.type:null,ue=b(T.stencilBuffer,fe),ke=T.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,we=Ke(T);Qe(T)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,we,ue,T.width,T.height):Z?r.renderbufferStorageMultisample(r.RENDERBUFFER,we,ue,T.width,T.height):r.renderbufferStorage(r.RENDERBUFFER,ue,T.width,T.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,ke,r.RENDERBUFFER,F)}else{const ce=T.textures;for(let fe=0;fe<ce.length;fe++){const ue=ce[fe],ke=s.convert(ue.format,ue.colorSpace),we=s.convert(ue.type),Be=w(ue.internalFormat,ke,we,ue.colorSpace),gt=Ke(T);Z&&Qe(T)===!1?r.renderbufferStorageMultisample(r.RENDERBUFFER,gt,Be,T.width,T.height):Qe(T)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,gt,Be,T.width,T.height):r.renderbufferStorage(r.RENDERBUFFER,Be,T.width,T.height)}}r.bindRenderbuffer(r.RENDERBUFFER,null)}function $e(F,T){if(T&&T.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(r.FRAMEBUFFER,F),!(T.depthTexture&&T.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const ce=n.get(T.depthTexture);ce.__renderTarget=T,(!ce.__webglTexture||T.depthTexture.image.width!==T.width||T.depthTexture.image.height!==T.height)&&(T.depthTexture.image.width=T.width,T.depthTexture.image.height=T.height,T.depthTexture.needsUpdate=!0),he(T.depthTexture,0);const fe=ce.__webglTexture,ue=Ke(T);if(T.depthTexture.format===Ys)Qe(T)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,fe,0,ue):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,fe,0);else if(T.depthTexture.format===no)Qe(T)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,fe,0,ue):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,fe,0);else throw new Error("Unknown depthTexture format")}function it(F){const T=n.get(F),Z=F.isWebGLCubeRenderTarget===!0;if(T.__boundDepthTexture!==F.depthTexture){const ce=F.depthTexture;if(T.__depthDisposeCallback&&T.__depthDisposeCallback(),ce){const fe=()=>{delete T.__boundDepthTexture,delete T.__depthDisposeCallback,ce.removeEventListener("dispose",fe)};ce.addEventListener("dispose",fe),T.__depthDisposeCallback=fe}T.__boundDepthTexture=ce}if(F.depthTexture&&!T.__autoAllocateDepthBuffer){if(Z)throw new Error("target.depthTexture not supported in Cube render targets");$e(T.__webglFramebuffer,F)}else if(Z){T.__webglDepthbuffer=[];for(let ce=0;ce<6;ce++)if(t.bindFramebuffer(r.FRAMEBUFFER,T.__webglFramebuffer[ce]),T.__webglDepthbuffer[ce]===void 0)T.__webglDepthbuffer[ce]=r.createRenderbuffer(),Se(T.__webglDepthbuffer[ce],F,!1);else{const fe=F.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,ue=T.__webglDepthbuffer[ce];r.bindRenderbuffer(r.RENDERBUFFER,ue),r.framebufferRenderbuffer(r.FRAMEBUFFER,fe,r.RENDERBUFFER,ue)}}else if(t.bindFramebuffer(r.FRAMEBUFFER,T.__webglFramebuffer),T.__webglDepthbuffer===void 0)T.__webglDepthbuffer=r.createRenderbuffer(),Se(T.__webglDepthbuffer,F,!1);else{const ce=F.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,fe=T.__webglDepthbuffer;r.bindRenderbuffer(r.RENDERBUFFER,fe),r.framebufferRenderbuffer(r.FRAMEBUFFER,ce,r.RENDERBUFFER,fe)}t.bindFramebuffer(r.FRAMEBUFFER,null)}function Je(F,T,Z){const ce=n.get(F);T!==void 0&&Ue(ce.__webglFramebuffer,F,F.texture,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,0),Z!==void 0&&it(F)}function pe(F){const T=F.texture,Z=n.get(F),ce=n.get(T);F.addEventListener("dispose",O);const fe=F.textures,ue=F.isWebGLCubeRenderTarget===!0,ke=fe.length>1;if(ke||(ce.__webglTexture===void 0&&(ce.__webglTexture=r.createTexture()),ce.__version=T.version,a.memory.textures++),ue){Z.__webglFramebuffer=[];for(let we=0;we<6;we++)if(T.mipmaps&&T.mipmaps.length>0){Z.__webglFramebuffer[we]=[];for(let Be=0;Be<T.mipmaps.length;Be++)Z.__webglFramebuffer[we][Be]=r.createFramebuffer()}else Z.__webglFramebuffer[we]=r.createFramebuffer()}else{if(T.mipmaps&&T.mipmaps.length>0){Z.__webglFramebuffer=[];for(let we=0;we<T.mipmaps.length;we++)Z.__webglFramebuffer[we]=r.createFramebuffer()}else Z.__webglFramebuffer=r.createFramebuffer();if(ke)for(let we=0,Be=fe.length;we<Be;we++){const gt=n.get(fe[we]);gt.__webglTexture===void 0&&(gt.__webglTexture=r.createTexture(),a.memory.textures++)}if(F.samples>0&&Qe(F)===!1){Z.__webglMultisampledFramebuffer=r.createFramebuffer(),Z.__webglColorRenderbuffer=[],t.bindFramebuffer(r.FRAMEBUFFER,Z.__webglMultisampledFramebuffer);for(let we=0;we<fe.length;we++){const Be=fe[we];Z.__webglColorRenderbuffer[we]=r.createRenderbuffer(),r.bindRenderbuffer(r.RENDERBUFFER,Z.__webglColorRenderbuffer[we]);const gt=s.convert(Be.format,Be.colorSpace),_e=s.convert(Be.type),He=w(Be.internalFormat,gt,_e,Be.colorSpace,F.isXRRenderTarget===!0),We=Ke(F);r.renderbufferStorageMultisample(r.RENDERBUFFER,We,He,F.width,F.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+we,r.RENDERBUFFER,Z.__webglColorRenderbuffer[we])}r.bindRenderbuffer(r.RENDERBUFFER,null),F.depthBuffer&&(Z.__webglDepthRenderbuffer=r.createRenderbuffer(),Se(Z.__webglDepthRenderbuffer,F,!0)),t.bindFramebuffer(r.FRAMEBUFFER,null)}}if(ue){t.bindTexture(r.TEXTURE_CUBE_MAP,ce.__webglTexture),Ge(r.TEXTURE_CUBE_MAP,T);for(let we=0;we<6;we++)if(T.mipmaps&&T.mipmaps.length>0)for(let Be=0;Be<T.mipmaps.length;Be++)Ue(Z.__webglFramebuffer[we][Be],F,T,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+we,Be);else Ue(Z.__webglFramebuffer[we],F,T,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+we,0);v(T)&&_(r.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(ke){for(let we=0,Be=fe.length;we<Be;we++){const gt=fe[we],_e=n.get(gt);t.bindTexture(r.TEXTURE_2D,_e.__webglTexture),Ge(r.TEXTURE_2D,gt),Ue(Z.__webglFramebuffer,F,gt,r.COLOR_ATTACHMENT0+we,r.TEXTURE_2D,0),v(gt)&&_(r.TEXTURE_2D)}t.unbindTexture()}else{let we=r.TEXTURE_2D;if((F.isWebGL3DRenderTarget||F.isWebGLArrayRenderTarget)&&(we=F.isWebGL3DRenderTarget?r.TEXTURE_3D:r.TEXTURE_2D_ARRAY),t.bindTexture(we,ce.__webglTexture),Ge(we,T),T.mipmaps&&T.mipmaps.length>0)for(let Be=0;Be<T.mipmaps.length;Be++)Ue(Z.__webglFramebuffer[Be],F,T,r.COLOR_ATTACHMENT0,we,Be);else Ue(Z.__webglFramebuffer,F,T,r.COLOR_ATTACHMENT0,we,0);v(T)&&_(we),t.unbindTexture()}F.depthBuffer&&it(F)}function ve(F){const T=F.textures;for(let Z=0,ce=T.length;Z<ce;Z++){const fe=T[Z];if(v(fe)){const ue=A(F),ke=n.get(fe).__webglTexture;t.bindTexture(ue,ke),_(ue),t.unbindTexture()}}}const Le=[],G=[];function tt(F){if(F.samples>0){if(Qe(F)===!1){const T=F.textures,Z=F.width,ce=F.height;let fe=r.COLOR_BUFFER_BIT;const ue=F.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,ke=n.get(F),we=T.length>1;if(we)for(let Be=0;Be<T.length;Be++)t.bindFramebuffer(r.FRAMEBUFFER,ke.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Be,r.RENDERBUFFER,null),t.bindFramebuffer(r.FRAMEBUFFER,ke.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+Be,r.TEXTURE_2D,null,0);t.bindFramebuffer(r.READ_FRAMEBUFFER,ke.__webglMultisampledFramebuffer),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,ke.__webglFramebuffer);for(let Be=0;Be<T.length;Be++){if(F.resolveDepthBuffer&&(F.depthBuffer&&(fe|=r.DEPTH_BUFFER_BIT),F.stencilBuffer&&F.resolveStencilBuffer&&(fe|=r.STENCIL_BUFFER_BIT)),we){r.framebufferRenderbuffer(r.READ_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.RENDERBUFFER,ke.__webglColorRenderbuffer[Be]);const gt=n.get(T[Be]).__webglTexture;r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,gt,0)}r.blitFramebuffer(0,0,Z,ce,0,0,Z,ce,fe,r.NEAREST),u===!0&&(Le.length=0,G.length=0,Le.push(r.COLOR_ATTACHMENT0+Be),F.depthBuffer&&F.resolveDepthBuffer===!1&&(Le.push(ue),G.push(ue),r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,G)),r.invalidateFramebuffer(r.READ_FRAMEBUFFER,Le))}if(t.bindFramebuffer(r.READ_FRAMEBUFFER,null),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),we)for(let Be=0;Be<T.length;Be++){t.bindFramebuffer(r.FRAMEBUFFER,ke.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Be,r.RENDERBUFFER,ke.__webglColorRenderbuffer[Be]);const gt=n.get(T[Be]).__webglTexture;t.bindFramebuffer(r.FRAMEBUFFER,ke.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+Be,r.TEXTURE_2D,gt,0)}t.bindFramebuffer(r.DRAW_FRAMEBUFFER,ke.__webglMultisampledFramebuffer)}else if(F.depthBuffer&&F.resolveDepthBuffer===!1&&u){const T=F.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT;r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,[T])}}}function Ke(F){return Math.min(i.maxSamples,F.samples)}function Qe(F){const T=n.get(F);return F.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&T.__useRenderToTexture!==!1}function Oe(F){const T=a.render.frame;f.get(F)!==T&&(f.set(F,T),F.update())}function rt(F,T){const Z=F.colorSpace,ce=F.format,fe=F.type;return F.isCompressedTexture===!0||F.isVideoTexture===!0||Z!==Wn&&Z!==xr&&(Ct.getTransfer(Z)===Gt?(ce!==fi||fe!==ir)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Z)),T}function Fe(F){return typeof HTMLImageElement<"u"&&F instanceof HTMLImageElement?(h.width=F.naturalWidth||F.width,h.height=F.naturalHeight||F.height):typeof VideoFrame<"u"&&F instanceof VideoFrame?(h.width=F.displayWidth,h.height=F.displayHeight):(h.width=F.width,h.height=F.height),h}this.allocateTextureUnit=te,this.resetTextureUnits=ee,this.setTexture2D=he,this.setTexture2DArray=q,this.setTexture3D=de,this.setTextureCube=re,this.rebindTextures=Je,this.setupRenderTarget=pe,this.updateRenderTargetMipmap=ve,this.updateMultisampleRenderTarget=tt,this.setupDepthRenderbuffer=it,this.setupFrameBufferTexture=Ue,this.useMultisampledRTT=Qe}function _P(r,e){function t(n,i=xr){let s;const a=Ct.getTransfer(i);if(n===ir)return r.UNSIGNED_BYTE;if(n===ud)return r.UNSIGNED_SHORT_4_4_4_4;if(n===hd)return r.UNSIGNED_SHORT_5_5_5_1;if(n===_g)return r.UNSIGNED_INT_5_9_9_9_REV;if(n===mg)return r.BYTE;if(n===gg)return r.SHORT;if(n===Jo)return r.UNSIGNED_SHORT;if(n===ld)return r.INT;if(n===ls)return r.UNSIGNED_INT;if(n===Si)return r.FLOAT;if(n===ia)return r.HALF_FLOAT;if(n===vg)return r.ALPHA;if(n===yg)return r.RGB;if(n===fi)return r.RGBA;if(n===xg)return r.LUMINANCE;if(n===bg)return r.LUMINANCE_ALPHA;if(n===Ys)return r.DEPTH_COMPONENT;if(n===no)return r.DEPTH_STENCIL;if(n===dd)return r.RED;if(n===fd)return r.RED_INTEGER;if(n===Sg)return r.RG;if(n===pd)return r.RG_INTEGER;if(n===md)return r.RGBA_INTEGER;if(n===Tc||n===wc||n===Ac||n===Rc)if(a===Gt)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===Tc)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===wc)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Ac)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Rc)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===Tc)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===wc)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Ac)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Rc)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Ah||n===Rh||n===Ph||n===Ch)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===Ah)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Rh)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Ph)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Ch)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Dh||n===Ih||n===Lh)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===Dh||n===Ih)return a===Gt?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===Lh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Fh||n===Nh||n===Oh||n===Uh||n===Bh||n===kh||n===zh||n===Hh||n===Vh||n===Gh||n===Wh||n===jh||n===Xh||n===qh)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===Fh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Nh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Oh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Uh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Bh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===kh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===zh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Hh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Vh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Gh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Wh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===jh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Xh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===qh)return a===Gt?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Pc||n===Yh||n===Kh)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===Pc)return a===Gt?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Yh)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Kh)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Eg||n===$h||n===Zh||n===Qh)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===Pc)return s.COMPRESSED_RED_RGTC1_EXT;if(n===$h)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===Zh)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Qh)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===to?r.UNSIGNED_INT_24_8:r[n]!==void 0?r[n]:null}return{convert:t}}class vP extends Vn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class er extends tn{constructor(){super(),this.isGroup=!0,this.type="Group"}}const yP={type:"move"};class $u{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new er,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new er,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new N,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new N),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new er,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new N,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new N),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,s=null,a=null;const c=this._targetRay,u=this._grip,h=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(h&&e.hand){a=!0;for(const E of e.hand.values()){const v=t.getJointPose(E,n),_=this._getHandJoint(h,E);v!==null&&(_.matrix.fromArray(v.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.matrixWorldNeedsUpdate=!0,_.jointRadius=v.radius),_.visible=v!==null}const f=h.joints["index-finger-tip"],p=h.joints["thumb-tip"],m=f.position.distanceTo(p.position),g=.02,x=.005;h.inputState.pinching&&m>g+x?(h.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!h.inputState.pinching&&m<=g-x&&(h.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else u!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(u.matrix.fromArray(s.transform.matrix),u.matrix.decompose(u.position,u.rotation,u.scale),u.matrixWorldNeedsUpdate=!0,s.linearVelocity?(u.hasLinearVelocity=!0,u.linearVelocity.copy(s.linearVelocity)):u.hasLinearVelocity=!1,s.angularVelocity?(u.hasAngularVelocity=!0,u.angularVelocity.copy(s.angularVelocity)):u.hasAngularVelocity=!1));c!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&s!==null&&(i=s),i!==null&&(c.matrix.fromArray(i.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,i.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(i.linearVelocity)):c.hasLinearVelocity=!1,i.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(i.angularVelocity)):c.hasAngularVelocity=!1,this.dispatchEvent(yP)))}return c!==null&&(c.visible=i!==null),u!==null&&(u.visible=s!==null),h!==null&&(h.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new er;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const xP=`
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

}`;class SP{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const i=new Mn,s=e.properties.get(i);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new Tr({vertexShader:xP,fragmentShader:bP,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Re(new lo(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class EP extends Rr{constructor(e,t){super();const n=this;let i=null,s=1,a=null,c="local-floor",u=1,h=null,f=null,p=null,m=null,g=null,x=null;const E=new SP,v=t.getContextAttributes();let _=null,A=null;const w=[],b=[],B=new lt;let U=null;const O=new Vn;O.viewport=new Ot;const V=new Vn;V.viewport=new Ot;const I=[O,V],R=new vP;let H=null,ee=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(le){let me=w[le];return me===void 0&&(me=new $u,w[le]=me),me.getTargetRaySpace()},this.getControllerGrip=function(le){let me=w[le];return me===void 0&&(me=new $u,w[le]=me),me.getGripSpace()},this.getHand=function(le){let me=w[le];return me===void 0&&(me=new $u,w[le]=me),me.getHandSpace()};function te(le){const me=b.indexOf(le.inputSource);if(me===-1)return;const Ue=w[me];Ue!==void 0&&(Ue.update(le.inputSource,le.frame,h||a),Ue.dispatchEvent({type:le.type,data:le.inputSource}))}function se(){i.removeEventListener("select",te),i.removeEventListener("selectstart",te),i.removeEventListener("selectend",te),i.removeEventListener("squeeze",te),i.removeEventListener("squeezestart",te),i.removeEventListener("squeezeend",te),i.removeEventListener("end",se),i.removeEventListener("inputsourceschange",he);for(let le=0;le<w.length;le++){const me=b[le];me!==null&&(b[le]=null,w[le].disconnect(me))}H=null,ee=null,E.reset(),e.setRenderTarget(_),g=null,m=null,p=null,i=null,A=null,pt.stop(),n.isPresenting=!1,e.setPixelRatio(U),e.setSize(B.width,B.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(le){s=le,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(le){c=le,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return h||a},this.setReferenceSpace=function(le){h=le},this.getBaseLayer=function(){return m!==null?m:g},this.getBinding=function(){return p},this.getFrame=function(){return x},this.getSession=function(){return i},this.setSession=async function(le){if(i=le,i!==null){if(_=e.getRenderTarget(),i.addEventListener("select",te),i.addEventListener("selectstart",te),i.addEventListener("selectend",te),i.addEventListener("squeeze",te),i.addEventListener("squeezestart",te),i.addEventListener("squeezeend",te),i.addEventListener("end",se),i.addEventListener("inputsourceschange",he),v.xrCompatible!==!0&&await t.makeXRCompatible(),U=e.getPixelRatio(),e.getSize(B),i.renderState.layers===void 0){const me={antialias:v.antialias,alpha:!0,depth:v.depth,stencil:v.stencil,framebufferScaleFactor:s};g=new XRWebGLLayer(i,t,me),i.updateRenderState({baseLayer:g}),e.setPixelRatio(1),e.setSize(g.framebufferWidth,g.framebufferHeight,!1),A=new us(g.framebufferWidth,g.framebufferHeight,{format:fi,type:ir,colorSpace:e.outputColorSpace,stencilBuffer:v.stencil})}else{let me=null,Ue=null,Se=null;v.depth&&(Se=v.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,me=v.stencil?no:Ys,Ue=v.stencil?to:ls);const $e={colorFormat:t.RGBA8,depthFormat:Se,scaleFactor:s};p=new XRWebGLBinding(i,t),m=p.createProjectionLayer($e),i.updateRenderState({layers:[m]}),e.setPixelRatio(1),e.setSize(m.textureWidth,m.textureHeight,!1),A=new us(m.textureWidth,m.textureHeight,{format:fi,type:ir,depthTexture:new Bg(m.textureWidth,m.textureHeight,Ue,void 0,void 0,void 0,void 0,void 0,void 0,me),stencilBuffer:v.stencil,colorSpace:e.outputColorSpace,samples:v.antialias?4:0,resolveDepthBuffer:m.ignoreDepthValues===!1})}A.isXRRenderTarget=!0,this.setFoveation(u),h=null,a=await i.requestReferenceSpace(c),pt.setContext(i),pt.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(i!==null)return i.environmentBlendMode},this.getDepthTexture=function(){return E.getDepthTexture()};function he(le){for(let me=0;me<le.removed.length;me++){const Ue=le.removed[me],Se=b.indexOf(Ue);Se>=0&&(b[Se]=null,w[Se].disconnect(Ue))}for(let me=0;me<le.added.length;me++){const Ue=le.added[me];let Se=b.indexOf(Ue);if(Se===-1){for(let it=0;it<w.length;it++)if(it>=b.length){b.push(Ue),Se=it;break}else if(b[it]===null){b[it]=Ue,Se=it;break}if(Se===-1)break}const $e=w[Se];$e&&$e.connect(Ue)}}const q=new N,de=new N;function re(le,me,Ue){q.setFromMatrixPosition(me.matrixWorld),de.setFromMatrixPosition(Ue.matrixWorld);const Se=q.distanceTo(de),$e=me.projectionMatrix.elements,it=Ue.projectionMatrix.elements,Je=$e[14]/($e[10]-1),pe=$e[14]/($e[10]+1),ve=($e[9]+1)/$e[5],Le=($e[9]-1)/$e[5],G=($e[8]-1)/$e[0],tt=(it[8]+1)/it[0],Ke=Je*G,Qe=Je*tt,Oe=Se/(-G+tt),rt=Oe*-G;if(me.matrixWorld.decompose(le.position,le.quaternion,le.scale),le.translateX(rt),le.translateZ(Oe),le.matrixWorld.compose(le.position,le.quaternion,le.scale),le.matrixWorldInverse.copy(le.matrixWorld).invert(),$e[10]===-1)le.projectionMatrix.copy(me.projectionMatrix),le.projectionMatrixInverse.copy(me.projectionMatrixInverse);else{const Fe=Je+Oe,F=pe+Oe,T=Ke-rt,Z=Qe+(Se-rt),ce=ve*pe/F*Fe,fe=Le*pe/F*Fe;le.projectionMatrix.makePerspective(T,Z,ce,fe,Fe,F),le.projectionMatrixInverse.copy(le.projectionMatrix).invert()}}function ge(le,me){me===null?le.matrixWorld.copy(le.matrix):le.matrixWorld.multiplyMatrices(me.matrixWorld,le.matrix),le.matrixWorldInverse.copy(le.matrixWorld).invert()}this.updateCamera=function(le){if(i===null)return;let me=le.near,Ue=le.far;E.texture!==null&&(E.depthNear>0&&(me=E.depthNear),E.depthFar>0&&(Ue=E.depthFar)),R.near=V.near=O.near=me,R.far=V.far=O.far=Ue,(H!==R.near||ee!==R.far)&&(i.updateRenderState({depthNear:R.near,depthFar:R.far}),H=R.near,ee=R.far),O.layers.mask=le.layers.mask|2,V.layers.mask=le.layers.mask|4,R.layers.mask=O.layers.mask|V.layers.mask;const Se=le.parent,$e=R.cameras;ge(R,Se);for(let it=0;it<$e.length;it++)ge($e[it],Se);$e.length===2?re(R,O,V):R.projectionMatrix.copy(O.projectionMatrix),be(le,R,Se)};function be(le,me,Ue){Ue===null?le.matrix.copy(me.matrixWorld):(le.matrix.copy(Ue.matrixWorld),le.matrix.invert(),le.matrix.multiply(me.matrixWorld)),le.matrix.decompose(le.position,le.quaternion,le.scale),le.updateMatrixWorld(!0),le.projectionMatrix.copy(me.projectionMatrix),le.projectionMatrixInverse.copy(me.projectionMatrixInverse),le.isPerspectiveCamera&&(le.fov=io*2*Math.atan(1/le.projectionMatrix.elements[5]),le.zoom=1)}this.getCamera=function(){return R},this.getFoveation=function(){if(!(m===null&&g===null))return u},this.setFoveation=function(le){u=le,m!==null&&(m.fixedFoveation=le),g!==null&&g.fixedFoveation!==void 0&&(g.fixedFoveation=le)},this.hasDepthSensing=function(){return E.texture!==null},this.getDepthSensingMesh=function(){return E.getMesh(R)};let ze=null;function Ge(le,me){if(f=me.getViewerPose(h||a),x=me,f!==null){const Ue=f.views;g!==null&&(e.setRenderTargetFramebuffer(A,g.framebuffer),e.setRenderTarget(A));let Se=!1;Ue.length!==R.cameras.length&&(R.cameras.length=0,Se=!0);for(let it=0;it<Ue.length;it++){const Je=Ue[it];let pe=null;if(g!==null)pe=g.getViewport(Je);else{const Le=p.getViewSubImage(m,Je);pe=Le.viewport,it===0&&(e.setRenderTargetTextures(A,Le.colorTexture,m.ignoreDepthValues?void 0:Le.depthStencilTexture),e.setRenderTarget(A))}let ve=I[it];ve===void 0&&(ve=new Vn,ve.layers.enable(it),ve.viewport=new Ot,I[it]=ve),ve.matrix.fromArray(Je.transform.matrix),ve.matrix.decompose(ve.position,ve.quaternion,ve.scale),ve.projectionMatrix.fromArray(Je.projectionMatrix),ve.projectionMatrixInverse.copy(ve.projectionMatrix).invert(),ve.viewport.set(pe.x,pe.y,pe.width,pe.height),it===0&&(R.matrix.copy(ve.matrix),R.matrix.decompose(R.position,R.quaternion,R.scale)),Se===!0&&R.cameras.push(ve)}const $e=i.enabledFeatures;if($e&&$e.includes("depth-sensing")){const it=p.getDepthInformation(Ue[0]);it&&it.isValid&&it.texture&&E.init(e,it,i.renderState)}}for(let Ue=0;Ue<w.length;Ue++){const Se=b[Ue],$e=w[Ue];Se!==null&&$e!==void 0&&$e.update(Se,me,h||a)}ze&&ze(le,me),me.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:me}),x=null}const pt=new Ug;pt.setAnimationLoop(Ge),this.setAnimationLoop=function(le){ze=le},this.dispose=function(){}}}const ts=new Ti,MP=new ft;function TP(r,e){function t(v,_){v.matrixAutoUpdate===!0&&v.updateMatrix(),_.value.copy(v.matrix)}function n(v,_){_.color.getRGB(v.fogColor.value,Fg(r)),_.isFog?(v.fogNear.value=_.near,v.fogFar.value=_.far):_.isFogExp2&&(v.fogDensity.value=_.density)}function i(v,_,A,w,b){_.isMeshBasicMaterial||_.isMeshLambertMaterial?s(v,_):_.isMeshToonMaterial?(s(v,_),p(v,_)):_.isMeshPhongMaterial?(s(v,_),f(v,_)):_.isMeshStandardMaterial?(s(v,_),m(v,_),_.isMeshPhysicalMaterial&&g(v,_,b)):_.isMeshMatcapMaterial?(s(v,_),x(v,_)):_.isMeshDepthMaterial?s(v,_):_.isMeshDistanceMaterial?(s(v,_),E(v,_)):_.isMeshNormalMaterial?s(v,_):_.isLineBasicMaterial?(a(v,_),_.isLineDashedMaterial&&c(v,_)):_.isPointsMaterial?u(v,_,A,w):_.isSpriteMaterial?h(v,_):_.isShadowMaterial?(v.color.value.copy(_.color),v.opacity.value=_.opacity):_.isShaderMaterial&&(_.uniformsNeedUpdate=!1)}function s(v,_){v.opacity.value=_.opacity,_.color&&v.diffuse.value.copy(_.color),_.emissive&&v.emissive.value.copy(_.emissive).multiplyScalar(_.emissiveIntensity),_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.bumpMap&&(v.bumpMap.value=_.bumpMap,t(_.bumpMap,v.bumpMapTransform),v.bumpScale.value=_.bumpScale,_.side===$n&&(v.bumpScale.value*=-1)),_.normalMap&&(v.normalMap.value=_.normalMap,t(_.normalMap,v.normalMapTransform),v.normalScale.value.copy(_.normalScale),_.side===$n&&v.normalScale.value.negate()),_.displacementMap&&(v.displacementMap.value=_.displacementMap,t(_.displacementMap,v.displacementMapTransform),v.displacementScale.value=_.displacementScale,v.displacementBias.value=_.displacementBias),_.emissiveMap&&(v.emissiveMap.value=_.emissiveMap,t(_.emissiveMap,v.emissiveMapTransform)),_.specularMap&&(v.specularMap.value=_.specularMap,t(_.specularMap,v.specularMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest);const A=e.get(_),w=A.envMap,b=A.envMapRotation;w&&(v.envMap.value=w,ts.copy(b),ts.x*=-1,ts.y*=-1,ts.z*=-1,w.isCubeTexture&&w.isRenderTargetTexture===!1&&(ts.y*=-1,ts.z*=-1),v.envMapRotation.value.setFromMatrix4(MP.makeRotationFromEuler(ts)),v.flipEnvMap.value=w.isCubeTexture&&w.isRenderTargetTexture===!1?-1:1,v.reflectivity.value=_.reflectivity,v.ior.value=_.ior,v.refractionRatio.value=_.refractionRatio),_.lightMap&&(v.lightMap.value=_.lightMap,v.lightMapIntensity.value=_.lightMapIntensity,t(_.lightMap,v.lightMapTransform)),_.aoMap&&(v.aoMap.value=_.aoMap,v.aoMapIntensity.value=_.aoMapIntensity,t(_.aoMap,v.aoMapTransform))}function a(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform))}function c(v,_){v.dashSize.value=_.dashSize,v.totalSize.value=_.dashSize+_.gapSize,v.scale.value=_.scale}function u(v,_,A,w){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.size.value=_.size*A,v.scale.value=w*.5,_.map&&(v.map.value=_.map,t(_.map,v.uvTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function h(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.rotation.value=_.rotation,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function f(v,_){v.specular.value.copy(_.specular),v.shininess.value=Math.max(_.shininess,1e-4)}function p(v,_){_.gradientMap&&(v.gradientMap.value=_.gradientMap)}function m(v,_){v.metalness.value=_.metalness,_.metalnessMap&&(v.metalnessMap.value=_.metalnessMap,t(_.metalnessMap,v.metalnessMapTransform)),v.roughness.value=_.roughness,_.roughnessMap&&(v.roughnessMap.value=_.roughnessMap,t(_.roughnessMap,v.roughnessMapTransform)),_.envMap&&(v.envMapIntensity.value=_.envMapIntensity)}function g(v,_,A){v.ior.value=_.ior,_.sheen>0&&(v.sheenColor.value.copy(_.sheenColor).multiplyScalar(_.sheen),v.sheenRoughness.value=_.sheenRoughness,_.sheenColorMap&&(v.sheenColorMap.value=_.sheenColorMap,t(_.sheenColorMap,v.sheenColorMapTransform)),_.sheenRoughnessMap&&(v.sheenRoughnessMap.value=_.sheenRoughnessMap,t(_.sheenRoughnessMap,v.sheenRoughnessMapTransform))),_.clearcoat>0&&(v.clearcoat.value=_.clearcoat,v.clearcoatRoughness.value=_.clearcoatRoughness,_.clearcoatMap&&(v.clearcoatMap.value=_.clearcoatMap,t(_.clearcoatMap,v.clearcoatMapTransform)),_.clearcoatRoughnessMap&&(v.clearcoatRoughnessMap.value=_.clearcoatRoughnessMap,t(_.clearcoatRoughnessMap,v.clearcoatRoughnessMapTransform)),_.clearcoatNormalMap&&(v.clearcoatNormalMap.value=_.clearcoatNormalMap,t(_.clearcoatNormalMap,v.clearcoatNormalMapTransform),v.clearcoatNormalScale.value.copy(_.clearcoatNormalScale),_.side===$n&&v.clearcoatNormalScale.value.negate())),_.dispersion>0&&(v.dispersion.value=_.dispersion),_.iridescence>0&&(v.iridescence.value=_.iridescence,v.iridescenceIOR.value=_.iridescenceIOR,v.iridescenceThicknessMinimum.value=_.iridescenceThicknessRange[0],v.iridescenceThicknessMaximum.value=_.iridescenceThicknessRange[1],_.iridescenceMap&&(v.iridescenceMap.value=_.iridescenceMap,t(_.iridescenceMap,v.iridescenceMapTransform)),_.iridescenceThicknessMap&&(v.iridescenceThicknessMap.value=_.iridescenceThicknessMap,t(_.iridescenceThicknessMap,v.iridescenceThicknessMapTransform))),_.transmission>0&&(v.transmission.value=_.transmission,v.transmissionSamplerMap.value=A.texture,v.transmissionSamplerSize.value.set(A.width,A.height),_.transmissionMap&&(v.transmissionMap.value=_.transmissionMap,t(_.transmissionMap,v.transmissionMapTransform)),v.thickness.value=_.thickness,_.thicknessMap&&(v.thicknessMap.value=_.thicknessMap,t(_.thicknessMap,v.thicknessMapTransform)),v.attenuationDistance.value=_.attenuationDistance,v.attenuationColor.value.copy(_.attenuationColor)),_.anisotropy>0&&(v.anisotropyVector.value.set(_.anisotropy*Math.cos(_.anisotropyRotation),_.anisotropy*Math.sin(_.anisotropyRotation)),_.anisotropyMap&&(v.anisotropyMap.value=_.anisotropyMap,t(_.anisotropyMap,v.anisotropyMapTransform))),v.specularIntensity.value=_.specularIntensity,v.specularColor.value.copy(_.specularColor),_.specularColorMap&&(v.specularColorMap.value=_.specularColorMap,t(_.specularColorMap,v.specularColorMapTransform)),_.specularIntensityMap&&(v.specularIntensityMap.value=_.specularIntensityMap,t(_.specularIntensityMap,v.specularIntensityMapTransform))}function x(v,_){_.matcap&&(v.matcap.value=_.matcap)}function E(v,_){const A=e.get(_).light;v.referencePosition.value.setFromMatrixPosition(A.matrixWorld),v.nearDistance.value=A.shadow.camera.near,v.farDistance.value=A.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:i}}function wP(r,e,t,n){let i={},s={},a=[];const c=r.getParameter(r.MAX_UNIFORM_BUFFER_BINDINGS);function u(A,w){const b=w.program;n.uniformBlockBinding(A,b)}function h(A,w){let b=i[A.id];b===void 0&&(x(A),b=f(A),i[A.id]=b,A.addEventListener("dispose",v));const B=w.program;n.updateUBOMapping(A,B);const U=e.render.frame;s[A.id]!==U&&(m(A),s[A.id]=U)}function f(A){const w=p();A.__bindingPointIndex=w;const b=r.createBuffer(),B=A.__size,U=A.usage;return r.bindBuffer(r.UNIFORM_BUFFER,b),r.bufferData(r.UNIFORM_BUFFER,B,U),r.bindBuffer(r.UNIFORM_BUFFER,null),r.bindBufferBase(r.UNIFORM_BUFFER,w,b),b}function p(){for(let A=0;A<c;A++)if(a.indexOf(A)===-1)return a.push(A),A;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function m(A){const w=i[A.id],b=A.uniforms,B=A.__cache;r.bindBuffer(r.UNIFORM_BUFFER,w);for(let U=0,O=b.length;U<O;U++){const V=Array.isArray(b[U])?b[U]:[b[U]];for(let I=0,R=V.length;I<R;I++){const H=V[I];if(g(H,U,I,B)===!0){const ee=H.__offset,te=Array.isArray(H.value)?H.value:[H.value];let se=0;for(let he=0;he<te.length;he++){const q=te[he],de=E(q);typeof q=="number"||typeof q=="boolean"?(H.__data[0]=q,r.bufferSubData(r.UNIFORM_BUFFER,ee+se,H.__data)):q.isMatrix3?(H.__data[0]=q.elements[0],H.__data[1]=q.elements[1],H.__data[2]=q.elements[2],H.__data[3]=0,H.__data[4]=q.elements[3],H.__data[5]=q.elements[4],H.__data[6]=q.elements[5],H.__data[7]=0,H.__data[8]=q.elements[6],H.__data[9]=q.elements[7],H.__data[10]=q.elements[8],H.__data[11]=0):(q.toArray(H.__data,se),se+=de.storage/Float32Array.BYTES_PER_ELEMENT)}r.bufferSubData(r.UNIFORM_BUFFER,ee,H.__data)}}}r.bindBuffer(r.UNIFORM_BUFFER,null)}function g(A,w,b,B){const U=A.value,O=w+"_"+b;if(B[O]===void 0)return typeof U=="number"||typeof U=="boolean"?B[O]=U:B[O]=U.clone(),!0;{const V=B[O];if(typeof U=="number"||typeof U=="boolean"){if(V!==U)return B[O]=U,!0}else if(V.equals(U)===!1)return V.copy(U),!0}return!1}function x(A){const w=A.uniforms;let b=0;const B=16;for(let O=0,V=w.length;O<V;O++){const I=Array.isArray(w[O])?w[O]:[w[O]];for(let R=0,H=I.length;R<H;R++){const ee=I[R],te=Array.isArray(ee.value)?ee.value:[ee.value];for(let se=0,he=te.length;se<he;se++){const q=te[se],de=E(q),re=b%B,ge=re%de.boundary,be=re+ge;b+=ge,be!==0&&B-be<de.storage&&(b+=B-be),ee.__data=new Float32Array(de.storage/Float32Array.BYTES_PER_ELEMENT),ee.__offset=b,b+=de.storage}}}const U=b%B;return U>0&&(b+=B-U),A.__size=b,A.__cache={},this}function E(A){const w={boundary:0,storage:0};return typeof A=="number"||typeof A=="boolean"?(w.boundary=4,w.storage=4):A.isVector2?(w.boundary=8,w.storage=8):A.isVector3||A.isColor?(w.boundary=16,w.storage=12):A.isVector4?(w.boundary=16,w.storage=16):A.isMatrix3?(w.boundary=48,w.storage=48):A.isMatrix4?(w.boundary=64,w.storage=64):A.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",A),w}function v(A){const w=A.target;w.removeEventListener("dispose",v);const b=a.indexOf(w.__bindingPointIndex);a.splice(b,1),r.deleteBuffer(i[w.id]),delete i[w.id],delete s[w.id]}function _(){for(const A in i)r.deleteBuffer(i[A]);a=[],i={},s={}}return{bind:u,update:h,dispose:_}}class AP{constructor(e={}){const{canvas:t=mT(),context:n=null,depth:i=!0,stencil:s=!1,alpha:a=!1,antialias:c=!1,premultipliedAlpha:u=!0,preserveDrawingBuffer:h=!1,powerPreference:f="default",failIfMajorPerformanceCaveat:p=!1,reverseDepthBuffer:m=!1}=e;this.isWebGLRenderer=!0;let g;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");g=n.getContextAttributes().alpha}else g=a;const x=new Uint32Array(4),E=new Int32Array(4);let v=null,_=null;const A=[],w=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=En,this.toneMapping=Mr,this.toneMappingExposure=1;const b=this;let B=!1,U=0,O=0,V=null,I=-1,R=null;const H=new Ot,ee=new Ot;let te=null;const se=new st(0);let he=0,q=t.width,de=t.height,re=1,ge=null,be=null;const ze=new Ot(0,0,q,de),Ge=new Ot(0,0,q,de);let pt=!1;const le=new xd;let me=!1,Ue=!1;const Se=new ft,$e=new ft,it=new N,Je=new Ot,pe={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let ve=!1;function Le(){return V===null?re:1}let G=n;function tt(C,j){return t.getContext(C,j)}try{const C={alpha:!0,depth:i,stencil:s,antialias:c,premultipliedAlpha:u,preserveDrawingBuffer:h,powerPreference:f,failIfMajorPerformanceCaveat:p};if("setAttribute"in t&&t.setAttribute("data-engine","three.js r170"),t.addEventListener("webglcontextlost",k,!1),t.addEventListener("webglcontextrestored",$,!1),t.addEventListener("webglcontextcreationerror",ie,!1),G===null){const j="webgl2";if(G=tt(j,C),G===null)throw tt(j)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(C){throw console.error("THREE.WebGLRenderer: "+C.message),C}let Ke,Qe,Oe,rt,Fe,F,T,Z,ce,fe,ue,ke,we,Be,gt,_e,He,We,ot,Ve,xt,dt,It,X;function Ae(){Ke=new I1(G),Ke.init(),dt=new _P(G,Ke),Qe=new w1(G,Ke,e,dt),Oe=new pP(G,Ke),Qe.reverseDepthBuffer&&m&&Oe.buffers.depth.setReversed(!0),rt=new N1(G),Fe=new JR,F=new gP(G,Ke,Oe,Fe,Qe,dt,rt),T=new R1(b),Z=new D1(b),ce=new VT(G),It=new M1(G,ce),fe=new L1(G,ce,rt,It),ue=new U1(G,fe,ce,rt),ot=new O1(G,Qe,F),_e=new A1(Fe),ke=new QR(b,T,Z,Ke,Qe,It,_e),we=new TP(b,Fe),Be=new tP,gt=new aP(Ke),We=new E1(b,T,Z,Oe,ue,g,u),He=new dP(b,ue,Qe),X=new wP(G,rt,Qe,Oe),Ve=new T1(G,Ke,rt),xt=new F1(G,Ke,rt),rt.programs=ke.programs,b.capabilities=Qe,b.extensions=Ke,b.properties=Fe,b.renderLists=Be,b.shadowMap=He,b.state=Oe,b.info=rt}Ae();const P=new EP(b,G);this.xr=P,this.getContext=function(){return G},this.getContextAttributes=function(){return G.getContextAttributes()},this.forceContextLoss=function(){const C=Ke.get("WEBGL_lose_context");C&&C.loseContext()},this.forceContextRestore=function(){const C=Ke.get("WEBGL_lose_context");C&&C.restoreContext()},this.getPixelRatio=function(){return re},this.setPixelRatio=function(C){C!==void 0&&(re=C,this.setSize(q,de,!1))},this.getSize=function(C){return C.set(q,de)},this.setSize=function(C,j,J=!0){if(P.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}q=C,de=j,t.width=Math.floor(C*re),t.height=Math.floor(j*re),J===!0&&(t.style.width=C+"px",t.style.height=j+"px"),this.setViewport(0,0,C,j)},this.getDrawingBufferSize=function(C){return C.set(q*re,de*re).floor()},this.setDrawingBufferSize=function(C,j,J){q=C,de=j,re=J,t.width=Math.floor(C*J),t.height=Math.floor(j*J),this.setViewport(0,0,C,j)},this.getCurrentViewport=function(C){return C.copy(H)},this.getViewport=function(C){return C.copy(ze)},this.setViewport=function(C,j,J,ne){C.isVector4?ze.set(C.x,C.y,C.z,C.w):ze.set(C,j,J,ne),Oe.viewport(H.copy(ze).multiplyScalar(re).round())},this.getScissor=function(C){return C.copy(Ge)},this.setScissor=function(C,j,J,ne){C.isVector4?Ge.set(C.x,C.y,C.z,C.w):Ge.set(C,j,J,ne),Oe.scissor(ee.copy(Ge).multiplyScalar(re).round())},this.getScissorTest=function(){return pt},this.setScissorTest=function(C){Oe.setScissorTest(pt=C)},this.setOpaqueSort=function(C){ge=C},this.setTransparentSort=function(C){be=C},this.getClearColor=function(C){return C.copy(We.getClearColor())},this.setClearColor=function(){We.setClearColor.apply(We,arguments)},this.getClearAlpha=function(){return We.getClearAlpha()},this.setClearAlpha=function(){We.setClearAlpha.apply(We,arguments)},this.clear=function(C=!0,j=!0,J=!0){let ne=0;if(C){let Y=!1;if(V!==null){const Me=V.texture.format;Y=Me===md||Me===pd||Me===fd}if(Y){const Me=V.texture.type,Ne=Me===ir||Me===ls||Me===Jo||Me===to||Me===ud||Me===hd,Xe=We.getClearColor(),qe=We.getClearAlpha(),ht=Xe.r,at=Xe.g,Ye=Xe.b;Ne?(x[0]=ht,x[1]=at,x[2]=Ye,x[3]=qe,G.clearBufferuiv(G.COLOR,0,x)):(E[0]=ht,E[1]=at,E[2]=Ye,E[3]=qe,G.clearBufferiv(G.COLOR,0,E))}else ne|=G.COLOR_BUFFER_BIT}j&&(ne|=G.DEPTH_BUFFER_BIT),J&&(ne|=G.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),G.clear(ne)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",k,!1),t.removeEventListener("webglcontextrestored",$,!1),t.removeEventListener("webglcontextcreationerror",ie,!1),Be.dispose(),gt.dispose(),Fe.dispose(),T.dispose(),Z.dispose(),ue.dispose(),It.dispose(),X.dispose(),ke.dispose(),P.dispose(),P.removeEventListener("sessionstart",Ft),P.removeEventListener("sessionend",mt),nt.stop()};function k(C){C.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),B=!0}function $(){console.log("THREE.WebGLRenderer: Context Restored."),B=!1;const C=rt.autoReset,j=He.enabled,J=He.autoUpdate,ne=He.needsUpdate,Y=He.type;Ae(),rt.autoReset=C,He.enabled=j,He.autoUpdate=J,He.needsUpdate=ne,He.type=Y}function ie(C){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",C.statusMessage)}function Te(C){const j=C.target;j.removeEventListener("dispose",Te),Ee(j)}function Ee(C){De(C),Fe.remove(C)}function De(C){const j=Fe.get(C).programs;j!==void 0&&(j.forEach(function(J){ke.releaseProgram(J)}),C.isShaderMaterial&&ke.releaseShaderCache(C))}this.renderBufferDirect=function(C,j,J,ne,Y,Me){j===null&&(j=pe);const Ne=Y.isMesh&&Y.matrixWorld.determinant()<0,Xe=rr(C,j,J,ne,Y);Oe.setMaterial(ne,Ne);let qe=J.index,ht=1;if(ne.wireframe===!0){if(qe=fe.getWireframeAttribute(J),qe===void 0)return;ht=2}const at=J.drawRange,Ye=J.attributes.position;let Rt=at.start*ht,Ut=(at.start+at.count)*ht;Me!==null&&(Rt=Math.max(Rt,Me.start*ht),Ut=Math.min(Ut,(Me.start+Me.count)*ht)),qe!==null?(Rt=Math.max(Rt,0),Ut=Math.min(Ut,qe.count)):Ye!=null&&(Rt=Math.max(Rt,0),Ut=Math.min(Ut,Ye.count));const kt=Ut-Rt;if(kt<0||kt===1/0)return;It.setup(Y,ne,Xe,J,qe);let on,Pt=Ve;if(qe!==null&&(on=ce.get(qe),Pt=xt,Pt.setIndex(on)),Y.isMesh)ne.wireframe===!0?(Oe.setLineWidth(ne.wireframeLinewidth*Le()),Pt.setMode(G.LINES)):Pt.setMode(G.TRIANGLES);else if(Y.isLine){let Ze=ne.linewidth;Ze===void 0&&(Ze=1),Oe.setLineWidth(Ze*Le()),Y.isLineSegments?Pt.setMode(G.LINES):Y.isLineLoop?Pt.setMode(G.LINE_LOOP):Pt.setMode(G.LINE_STRIP)}else Y.isPoints?Pt.setMode(G.POINTS):Y.isSprite&&Pt.setMode(G.TRIANGLES);if(Y.isBatchedMesh)if(Y._multiDrawInstances!==null)Pt.renderMultiDrawInstances(Y._multiDrawStarts,Y._multiDrawCounts,Y._multiDrawCount,Y._multiDrawInstances);else if(Ke.get("WEBGL_multi_draw"))Pt.renderMultiDraw(Y._multiDrawStarts,Y._multiDrawCounts,Y._multiDrawCount);else{const Ze=Y._multiDrawStarts,Qn=Y._multiDrawCounts,wt=Y._multiDrawCount,wn=qe?ce.get(qe).bytesPerElement:1,wi=Fe.get(ne).currentProgram.getUniforms();for(let un=0;un<wt;un++)wi.setValue(G,"_gl_DrawID",un),Pt.render(Ze[un]/wn,Qn[un])}else if(Y.isInstancedMesh)Pt.renderInstances(Rt,kt,Y.count);else if(J.isInstancedBufferGeometry){const Ze=J._maxInstanceCount!==void 0?J._maxInstanceCount:1/0,Qn=Math.min(J.instanceCount,Ze);Pt.renderInstances(Rt,kt,Qn)}else Pt.render(Rt,kt)};function Pe(C,j,J){C.transparent===!0&&C.side===Kn&&C.forceSinglePass===!1?(C.side=$n,C.needsUpdate=!0,nn(C,j,J),C.side=nr,C.needsUpdate=!0,nn(C,j,J),C.side=Kn):nn(C,j,J)}this.compile=function(C,j,J=null){J===null&&(J=C),_=gt.get(J),_.init(j),w.push(_),J.traverseVisible(function(Y){Y.isLight&&Y.layers.test(j.layers)&&(_.pushLight(Y),Y.castShadow&&_.pushShadow(Y))}),C!==J&&C.traverseVisible(function(Y){Y.isLight&&Y.layers.test(j.layers)&&(_.pushLight(Y),Y.castShadow&&_.pushShadow(Y))}),_.setupLights();const ne=new Set;return C.traverse(function(Y){if(!(Y.isMesh||Y.isPoints||Y.isLine||Y.isSprite))return;const Me=Y.material;if(Me)if(Array.isArray(Me))for(let Ne=0;Ne<Me.length;Ne++){const Xe=Me[Ne];Pe(Xe,J,Y),ne.add(Xe)}else Pe(Me,J,Y),ne.add(Me)}),w.pop(),_=null,ne},this.compileAsync=function(C,j,J=null){const ne=this.compile(C,j,J);return new Promise(Y=>{function Me(){if(ne.forEach(function(Ne){Fe.get(Ne).currentProgram.isReady()&&ne.delete(Ne)}),ne.size===0){Y(C);return}setTimeout(Me,10)}Ke.get("KHR_parallel_shader_compile")!==null?Me():setTimeout(Me,10)})};let ut=null;function bt(C){ut&&ut(C)}function Ft(){nt.stop()}function mt(){nt.start()}const nt=new Ug;nt.setAnimationLoop(bt),typeof self<"u"&&nt.setContext(self),this.setAnimationLoop=function(C){ut=C,P.setAnimationLoop(C),C===null?nt.stop():nt.start()},P.addEventListener("sessionstart",Ft),P.addEventListener("sessionend",mt),this.render=function(C,j){if(j!==void 0&&j.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(B===!0)return;if(C.matrixWorldAutoUpdate===!0&&C.updateMatrixWorld(),j.parent===null&&j.matrixWorldAutoUpdate===!0&&j.updateMatrixWorld(),P.enabled===!0&&P.isPresenting===!0&&(P.cameraAutoUpdate===!0&&P.updateCamera(j),j=P.getCamera()),C.isScene===!0&&C.onBeforeRender(b,C,j,V),_=gt.get(C,w.length),_.init(j),w.push(_),$e.multiplyMatrices(j.projectionMatrix,j.matrixWorldInverse),le.setFromProjectionMatrix($e),Ue=this.localClippingEnabled,me=_e.init(this.clippingPlanes,Ue),v=Be.get(C,A.length),v.init(),A.push(v),P.enabled===!0&&P.isPresenting===!0){const Me=b.xr.getDepthSensingMesh();Me!==null&&jt(Me,j,-1/0,b.sortObjects)}jt(C,j,0,b.sortObjects),v.finish(),b.sortObjects===!0&&v.sort(ge,be),ve=P.enabled===!1||P.isPresenting===!1||P.hasDepthSensing()===!1,ve&&We.addToRenderList(v,C),this.info.render.frame++,me===!0&&_e.beginShadows();const J=_.state.shadowsArray;He.render(J,C,j),me===!0&&_e.endShadows(),this.info.autoReset===!0&&this.info.reset();const ne=v.opaque,Y=v.transmissive;if(_.setupLights(),j.isArrayCamera){const Me=j.cameras;if(Y.length>0)for(let Ne=0,Xe=Me.length;Ne<Xe;Ne++){const qe=Me[Ne];Xt(ne,Y,C,qe)}ve&&We.render(C);for(let Ne=0,Xe=Me.length;Ne<Xe;Ne++){const qe=Me[Ne];Dt(v,C,qe,qe.viewport)}}else Y.length>0&&Xt(ne,Y,C,j),ve&&We.render(C),Dt(v,C,j);V!==null&&(F.updateMultisampleRenderTarget(V),F.updateRenderTargetMipmap(V)),C.isScene===!0&&C.onAfterRender(b,C,j),It.resetDefaultState(),I=-1,R=null,w.pop(),w.length>0?(_=w[w.length-1],me===!0&&_e.setGlobalState(b.clippingPlanes,_.state.camera)):_=null,A.pop(),A.length>0?v=A[A.length-1]:v=null};function jt(C,j,J,ne){if(C.visible===!1)return;if(C.layers.test(j.layers)){if(C.isGroup)J=C.renderOrder;else if(C.isLOD)C.autoUpdate===!0&&C.update(j);else if(C.isLight)_.pushLight(C),C.castShadow&&_.pushShadow(C);else if(C.isSprite){if(!C.frustumCulled||le.intersectsSprite(C)){ne&&Je.setFromMatrixPosition(C.matrixWorld).applyMatrix4($e);const Ne=ue.update(C),Xe=C.material;Xe.visible&&v.push(C,Ne,Xe,J,Je.z,null)}}else if((C.isMesh||C.isLine||C.isPoints)&&(!C.frustumCulled||le.intersectsObject(C))){const Ne=ue.update(C),Xe=C.material;if(ne&&(C.boundingSphere!==void 0?(C.boundingSphere===null&&C.computeBoundingSphere(),Je.copy(C.boundingSphere.center)):(Ne.boundingSphere===null&&Ne.computeBoundingSphere(),Je.copy(Ne.boundingSphere.center)),Je.applyMatrix4(C.matrixWorld).applyMatrix4($e)),Array.isArray(Xe)){const qe=Ne.groups;for(let ht=0,at=qe.length;ht<at;ht++){const Ye=qe[ht],Rt=Xe[Ye.materialIndex];Rt&&Rt.visible&&v.push(C,Ne,Rt,J,Je.z,Ye)}}else Xe.visible&&v.push(C,Ne,Xe,J,Je.z,null)}}const Me=C.children;for(let Ne=0,Xe=Me.length;Ne<Xe;Ne++)jt(Me[Ne],j,J,ne)}function Dt(C,j,J,ne){const Y=C.opaque,Me=C.transmissive,Ne=C.transparent;_.setupLightsView(J),me===!0&&_e.setGlobalState(b.clippingPlanes,J),ne&&Oe.viewport(H.copy(ne)),Y.length>0&&qt(Y,j,J),Me.length>0&&qt(Me,j,J),Ne.length>0&&qt(Ne,j,J),Oe.buffers.depth.setTest(!0),Oe.buffers.depth.setMask(!0),Oe.buffers.color.setMask(!0),Oe.setPolygonOffset(!1)}function Xt(C,j,J,ne){if((J.isScene===!0?J.overrideMaterial:null)!==null)return;_.state.transmissionRenderTarget[ne.id]===void 0&&(_.state.transmissionRenderTarget[ne.id]=new us(1,1,{generateMipmaps:!0,type:Ke.has("EXT_color_buffer_half_float")||Ke.has("EXT_color_buffer_float")?ia:ir,minFilter:Qi,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Ct.workingColorSpace}));const Me=_.state.transmissionRenderTarget[ne.id],Ne=ne.viewport||H;Me.setSize(Ne.z,Ne.w);const Xe=b.getRenderTarget();b.setRenderTarget(Me),b.getClearColor(se),he=b.getClearAlpha(),he<1&&b.setClearColor(16777215,.5),b.clear(),ve&&We.render(J);const qe=b.toneMapping;b.toneMapping=Mr;const ht=ne.viewport;if(ne.viewport!==void 0&&(ne.viewport=void 0),_.setupLightsView(ne),me===!0&&_e.setGlobalState(b.clippingPlanes,ne),qt(C,J,ne),F.updateMultisampleRenderTarget(Me),F.updateRenderTargetMipmap(Me),Ke.has("WEBGL_multisampled_render_to_texture")===!1){let at=!1;for(let Ye=0,Rt=j.length;Ye<Rt;Ye++){const Ut=j[Ye],kt=Ut.object,on=Ut.geometry,Pt=Ut.material,Ze=Ut.group;if(Pt.side===Kn&&kt.layers.test(ne.layers)){const Qn=Pt.side;Pt.side=$n,Pt.needsUpdate=!0,Tt(kt,J,ne,on,Pt,Ze),Pt.side=Qn,Pt.needsUpdate=!0,at=!0}}at===!0&&(F.updateMultisampleRenderTarget(Me),F.updateRenderTargetMipmap(Me))}b.setRenderTarget(Xe),b.setClearColor(se,he),ht!==void 0&&(ne.viewport=ht),b.toneMapping=qe}function qt(C,j,J){const ne=j.isScene===!0?j.overrideMaterial:null;for(let Y=0,Me=C.length;Y<Me;Y++){const Ne=C[Y],Xe=Ne.object,qe=Ne.geometry,ht=ne===null?Ne.material:ne,at=Ne.group;Xe.layers.test(J.layers)&&Tt(Xe,j,J,qe,ht,at)}}function Tt(C,j,J,ne,Y,Me){C.onBeforeRender(b,j,J,ne,Y,Me),C.modelViewMatrix.multiplyMatrices(J.matrixWorldInverse,C.matrixWorld),C.normalMatrix.getNormalMatrix(C.modelViewMatrix),Y.onBeforeRender(b,j,J,ne,C,Me),Y.transparent===!0&&Y.side===Kn&&Y.forceSinglePass===!1?(Y.side=$n,Y.needsUpdate=!0,b.renderBufferDirect(J,j,ne,Y,C,Me),Y.side=nr,Y.needsUpdate=!0,b.renderBufferDirect(J,j,ne,Y,C,Me),Y.side=Kn):b.renderBufferDirect(J,j,ne,Y,C,Me),C.onAfterRender(b,j,J,ne,Y,Me)}function nn(C,j,J){j.isScene!==!0&&(j=pe);const ne=Fe.get(C),Y=_.state.lights,Me=_.state.shadowsArray,Ne=Y.state.version,Xe=ke.getParameters(C,Y.state,Me,j,J),qe=ke.getProgramCacheKey(Xe);let ht=ne.programs;ne.environment=C.isMeshStandardMaterial?j.environment:null,ne.fog=j.fog,ne.envMap=(C.isMeshStandardMaterial?Z:T).get(C.envMap||ne.environment),ne.envMapRotation=ne.environment!==null&&C.envMap===null?j.environmentRotation:C.envMapRotation,ht===void 0&&(C.addEventListener("dispose",Te),ht=new Map,ne.programs=ht);let at=ht.get(qe);if(at!==void 0){if(ne.currentProgram===at&&ne.lightsStateVersion===Ne)return Bn(C,Xe),at}else Xe.uniforms=ke.getUniforms(C),C.onBeforeCompile(Xe,b),at=ke.acquireProgram(Xe,qe),ht.set(qe,at),ne.uniforms=Xe.uniforms;const Ye=ne.uniforms;return(!C.isShaderMaterial&&!C.isRawShaderMaterial||C.clipping===!0)&&(Ye.clippingPlanes=_e.uniform),Bn(C,Xe),ne.needsLights=ci(C),ne.lightsStateVersion=Ne,ne.needsLights&&(Ye.ambientLightColor.value=Y.state.ambient,Ye.lightProbe.value=Y.state.probe,Ye.directionalLights.value=Y.state.directional,Ye.directionalLightShadows.value=Y.state.directionalShadow,Ye.spotLights.value=Y.state.spot,Ye.spotLightShadows.value=Y.state.spotShadow,Ye.rectAreaLights.value=Y.state.rectArea,Ye.ltc_1.value=Y.state.rectAreaLTC1,Ye.ltc_2.value=Y.state.rectAreaLTC2,Ye.pointLights.value=Y.state.point,Ye.pointLightShadows.value=Y.state.pointShadow,Ye.hemisphereLights.value=Y.state.hemi,Ye.directionalShadowMap.value=Y.state.directionalShadowMap,Ye.directionalShadowMatrix.value=Y.state.directionalShadowMatrix,Ye.spotShadowMap.value=Y.state.spotShadowMap,Ye.spotLightMatrix.value=Y.state.spotLightMatrix,Ye.spotLightMap.value=Y.state.spotLightMap,Ye.pointShadowMap.value=Y.state.pointShadowMap,Ye.pointShadowMatrix.value=Y.state.pointShadowMatrix),ne.currentProgram=at,ne.uniformsList=null,at}function Tn(C){if(C.uniformsList===null){const j=C.currentProgram.getUniforms();C.uniformsList=Cc.seqWithValue(j.seq,C.uniforms)}return C.uniformsList}function Bn(C,j){const J=Fe.get(C);J.outputColorSpace=j.outputColorSpace,J.batching=j.batching,J.batchingColor=j.batchingColor,J.instancing=j.instancing,J.instancingColor=j.instancingColor,J.instancingMorph=j.instancingMorph,J.skinning=j.skinning,J.morphTargets=j.morphTargets,J.morphNormals=j.morphNormals,J.morphColors=j.morphColors,J.morphTargetsCount=j.morphTargetsCount,J.numClippingPlanes=j.numClippingPlanes,J.numIntersection=j.numClipIntersection,J.vertexAlphas=j.vertexAlphas,J.vertexTangents=j.vertexTangents,J.toneMapping=j.toneMapping}function rr(C,j,J,ne,Y){j.isScene!==!0&&(j=pe),F.resetTextureUnits();const Me=j.fog,Ne=ne.isMeshStandardMaterial?j.environment:null,Xe=V===null?b.outputColorSpace:V.isXRRenderTarget===!0?V.texture.colorSpace:Wn,qe=(ne.isMeshStandardMaterial?Z:T).get(ne.envMap||Ne),ht=ne.vertexColors===!0&&!!J.attributes.color&&J.attributes.color.itemSize===4,at=!!J.attributes.tangent&&(!!ne.normalMap||ne.anisotropy>0),Ye=!!J.morphAttributes.position,Rt=!!J.morphAttributes.normal,Ut=!!J.morphAttributes.color;let kt=Mr;ne.toneMapped&&(V===null||V.isXRRenderTarget===!0)&&(kt=b.toneMapping);const on=J.morphAttributes.position||J.morphAttributes.normal||J.morphAttributes.color,Pt=on!==void 0?on.length:0,Ze=Fe.get(ne),Qn=_.state.lights;if(me===!0&&(Ue===!0||C!==R)){const Dn=C===R&&ne.id===I;_e.setState(ne,C,Dn)}let wt=!1;ne.version===Ze.__version?(Ze.needsLights&&Ze.lightsStateVersion!==Qn.state.version||Ze.outputColorSpace!==Xe||Y.isBatchedMesh&&Ze.batching===!1||!Y.isBatchedMesh&&Ze.batching===!0||Y.isBatchedMesh&&Ze.batchingColor===!0&&Y.colorTexture===null||Y.isBatchedMesh&&Ze.batchingColor===!1&&Y.colorTexture!==null||Y.isInstancedMesh&&Ze.instancing===!1||!Y.isInstancedMesh&&Ze.instancing===!0||Y.isSkinnedMesh&&Ze.skinning===!1||!Y.isSkinnedMesh&&Ze.skinning===!0||Y.isInstancedMesh&&Ze.instancingColor===!0&&Y.instanceColor===null||Y.isInstancedMesh&&Ze.instancingColor===!1&&Y.instanceColor!==null||Y.isInstancedMesh&&Ze.instancingMorph===!0&&Y.morphTexture===null||Y.isInstancedMesh&&Ze.instancingMorph===!1&&Y.morphTexture!==null||Ze.envMap!==qe||ne.fog===!0&&Ze.fog!==Me||Ze.numClippingPlanes!==void 0&&(Ze.numClippingPlanes!==_e.numPlanes||Ze.numIntersection!==_e.numIntersection)||Ze.vertexAlphas!==ht||Ze.vertexTangents!==at||Ze.morphTargets!==Ye||Ze.morphNormals!==Rt||Ze.morphColors!==Ut||Ze.toneMapping!==kt||Ze.morphTargetsCount!==Pt)&&(wt=!0):(wt=!0,Ze.__version=ne.version);let wn=Ze.currentProgram;wt===!0&&(wn=nn(ne,j,Y));let wi=!1,un=!1,Ni=!1;const zt=wn.getUniforms(),jn=Ze.uniforms;if(Oe.useProgram(wn.program)&&(wi=!0,un=!0,Ni=!0),ne.id!==I&&(I=ne.id,un=!0),wi||R!==C){Oe.buffers.depth.getReversed()?(Se.copy(C.projectionMatrix),_T(Se),vT(Se),zt.setValue(G,"projectionMatrix",Se)):zt.setValue(G,"projectionMatrix",C.projectionMatrix),zt.setValue(G,"viewMatrix",C.matrixWorldInverse);const An=zt.map.cameraPosition;An!==void 0&&An.setValue(G,it.setFromMatrixPosition(C.matrixWorld)),Qe.logarithmicDepthBuffer&&zt.setValue(G,"logDepthBufFC",2/(Math.log(C.far+1)/Math.LN2)),(ne.isMeshPhongMaterial||ne.isMeshToonMaterial||ne.isMeshLambertMaterial||ne.isMeshBasicMaterial||ne.isMeshStandardMaterial||ne.isShaderMaterial)&&zt.setValue(G,"isOrthographic",C.isOrthographicCamera===!0),R!==C&&(R=C,un=!0,Ni=!0)}if(Y.isSkinnedMesh){zt.setOptional(G,Y,"bindMatrix"),zt.setOptional(G,Y,"bindMatrixInverse");const Dn=Y.skeleton;Dn&&(Dn.boneTexture===null&&Dn.computeBoneTexture(),zt.setValue(G,"boneTexture",Dn.boneTexture,F))}Y.isBatchedMesh&&(zt.setOptional(G,Y,"batchingTexture"),zt.setValue(G,"batchingTexture",Y._matricesTexture,F),zt.setOptional(G,Y,"batchingIdTexture"),zt.setValue(G,"batchingIdTexture",Y._indirectTexture,F),zt.setOptional(G,Y,"batchingColorTexture"),Y._colorsTexture!==null&&zt.setValue(G,"batchingColorTexture",Y._colorsTexture,F));const Oi=J.morphAttributes;if((Oi.position!==void 0||Oi.normal!==void 0||Oi.color!==void 0)&&ot.update(Y,J,wn),(un||Ze.receiveShadow!==Y.receiveShadow)&&(Ze.receiveShadow=Y.receiveShadow,zt.setValue(G,"receiveShadow",Y.receiveShadow)),ne.isMeshGouraudMaterial&&ne.envMap!==null&&(jn.envMap.value=qe,jn.flipEnvMap.value=qe.isCubeTexture&&qe.isRenderTargetTexture===!1?-1:1),ne.isMeshStandardMaterial&&ne.envMap===null&&j.environment!==null&&(jn.envMapIntensity.value=j.environmentIntensity),un&&(zt.setValue(G,"toneMappingExposure",b.toneMappingExposure),Ze.needsLights&&Zn(jn,Ni),Me&&ne.fog===!0&&we.refreshFogUniforms(jn,Me),we.refreshMaterialUniforms(jn,ne,re,de,_.state.transmissionRenderTarget[C.id]),Cc.upload(G,Tn(Ze),jn,F)),ne.isShaderMaterial&&ne.uniformsNeedUpdate===!0&&(Cc.upload(G,Tn(Ze),jn,F),ne.uniformsNeedUpdate=!1),ne.isSpriteMaterial&&zt.setValue(G,"center",Y.center),zt.setValue(G,"modelViewMatrix",Y.modelViewMatrix),zt.setValue(G,"normalMatrix",Y.normalMatrix),zt.setValue(G,"modelMatrix",Y.matrixWorld),ne.isShaderMaterial||ne.isRawShaderMaterial){const Dn=ne.uniformsGroups;for(let An=0,Jn=Dn.length;An<Jn;An++){const fs=Dn[An];X.update(fs,wn),X.bind(fs,wn)}}return wn}function Zn(C,j){C.ambientLightColor.needsUpdate=j,C.lightProbe.needsUpdate=j,C.directionalLights.needsUpdate=j,C.directionalLightShadows.needsUpdate=j,C.pointLights.needsUpdate=j,C.pointLightShadows.needsUpdate=j,C.spotLights.needsUpdate=j,C.spotLightShadows.needsUpdate=j,C.rectAreaLights.needsUpdate=j,C.hemisphereLights.needsUpdate=j}function ci(C){return C.isMeshLambertMaterial||C.isMeshToonMaterial||C.isMeshPhongMaterial||C.isMeshStandardMaterial||C.isShadowMaterial||C.isShaderMaterial&&C.lights===!0}this.getActiveCubeFace=function(){return U},this.getActiveMipmapLevel=function(){return O},this.getRenderTarget=function(){return V},this.setRenderTargetTextures=function(C,j,J){Fe.get(C.texture).__webglTexture=j,Fe.get(C.depthTexture).__webglTexture=J;const ne=Fe.get(C);ne.__hasExternalTextures=!0,ne.__autoAllocateDepthBuffer=J===void 0,ne.__autoAllocateDepthBuffer||Ke.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),ne.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(C,j){const J=Fe.get(C);J.__webglFramebuffer=j,J.__useDefaultFramebuffer=j===void 0},this.setRenderTarget=function(C,j=0,J=0){V=C,U=j,O=J;let ne=!0,Y=null,Me=!1,Ne=!1;if(C){const qe=Fe.get(C);if(qe.__useDefaultFramebuffer!==void 0)Oe.bindFramebuffer(G.FRAMEBUFFER,null),ne=!1;else if(qe.__webglFramebuffer===void 0)F.setupRenderTarget(C);else if(qe.__hasExternalTextures)F.rebindTextures(C,Fe.get(C.texture).__webglTexture,Fe.get(C.depthTexture).__webglTexture);else if(C.depthBuffer){const Ye=C.depthTexture;if(qe.__boundDepthTexture!==Ye){if(Ye!==null&&Fe.has(Ye)&&(C.width!==Ye.image.width||C.height!==Ye.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");F.setupDepthRenderbuffer(C)}}const ht=C.texture;(ht.isData3DTexture||ht.isDataArrayTexture||ht.isCompressedArrayTexture)&&(Ne=!0);const at=Fe.get(C).__webglFramebuffer;C.isWebGLCubeRenderTarget?(Array.isArray(at[j])?Y=at[j][J]:Y=at[j],Me=!0):C.samples>0&&F.useMultisampledRTT(C)===!1?Y=Fe.get(C).__webglMultisampledFramebuffer:Array.isArray(at)?Y=at[J]:Y=at,H.copy(C.viewport),ee.copy(C.scissor),te=C.scissorTest}else H.copy(ze).multiplyScalar(re).floor(),ee.copy(Ge).multiplyScalar(re).floor(),te=pt;if(Oe.bindFramebuffer(G.FRAMEBUFFER,Y)&&ne&&Oe.drawBuffers(C,Y),Oe.viewport(H),Oe.scissor(ee),Oe.setScissorTest(te),Me){const qe=Fe.get(C.texture);G.framebufferTexture2D(G.FRAMEBUFFER,G.COLOR_ATTACHMENT0,G.TEXTURE_CUBE_MAP_POSITIVE_X+j,qe.__webglTexture,J)}else if(Ne){const qe=Fe.get(C.texture),ht=j||0;G.framebufferTextureLayer(G.FRAMEBUFFER,G.COLOR_ATTACHMENT0,qe.__webglTexture,J||0,ht)}I=-1},this.readRenderTargetPixels=function(C,j,J,ne,Y,Me,Ne){if(!(C&&C.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Xe=Fe.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&Ne!==void 0&&(Xe=Xe[Ne]),Xe){Oe.bindFramebuffer(G.FRAMEBUFFER,Xe);try{const qe=C.texture,ht=qe.format,at=qe.type;if(!Qe.textureFormatReadable(ht)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Qe.textureTypeReadable(at)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}j>=0&&j<=C.width-ne&&J>=0&&J<=C.height-Y&&G.readPixels(j,J,ne,Y,dt.convert(ht),dt.convert(at),Me)}finally{const qe=V!==null?Fe.get(V).__webglFramebuffer:null;Oe.bindFramebuffer(G.FRAMEBUFFER,qe)}}},this.readRenderTargetPixelsAsync=async function(C,j,J,ne,Y,Me,Ne){if(!(C&&C.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Xe=Fe.get(C).__webglFramebuffer;if(C.isWebGLCubeRenderTarget&&Ne!==void 0&&(Xe=Xe[Ne]),Xe){const qe=C.texture,ht=qe.format,at=qe.type;if(!Qe.textureFormatReadable(ht))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Qe.textureTypeReadable(at))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(j>=0&&j<=C.width-ne&&J>=0&&J<=C.height-Y){Oe.bindFramebuffer(G.FRAMEBUFFER,Xe);const Ye=G.createBuffer();G.bindBuffer(G.PIXEL_PACK_BUFFER,Ye),G.bufferData(G.PIXEL_PACK_BUFFER,Me.byteLength,G.STREAM_READ),G.readPixels(j,J,ne,Y,dt.convert(ht),dt.convert(at),0);const Rt=V!==null?Fe.get(V).__webglFramebuffer:null;Oe.bindFramebuffer(G.FRAMEBUFFER,Rt);const Ut=G.fenceSync(G.SYNC_GPU_COMMANDS_COMPLETE,0);return G.flush(),await gT(G,Ut,4),G.bindBuffer(G.PIXEL_PACK_BUFFER,Ye),G.getBufferSubData(G.PIXEL_PACK_BUFFER,0,Me),G.deleteBuffer(Ye),G.deleteSync(Ut),Me}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(C,j=null,J=0){C.isTexture!==!0&&(jo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),j=arguments[0]||null,C=arguments[1]);const ne=Math.pow(2,-J),Y=Math.floor(C.image.width*ne),Me=Math.floor(C.image.height*ne),Ne=j!==null?j.x:0,Xe=j!==null?j.y:0;F.setTexture2D(C,0),G.copyTexSubImage2D(G.TEXTURE_2D,J,0,0,Ne,Xe,Y,Me),Oe.unbindTexture()},this.copyTextureToTexture=function(C,j,J=null,ne=null,Y=0){C.isTexture!==!0&&(jo("WebGLRenderer: copyTextureToTexture function signature has changed."),ne=arguments[0]||null,C=arguments[1],j=arguments[2],Y=arguments[3]||0,J=null);let Me,Ne,Xe,qe,ht,at,Ye,Rt,Ut;const kt=C.isCompressedTexture?C.mipmaps[Y]:C.image;J!==null?(Me=J.max.x-J.min.x,Ne=J.max.y-J.min.y,Xe=J.isBox3?J.max.z-J.min.z:1,qe=J.min.x,ht=J.min.y,at=J.isBox3?J.min.z:0):(Me=kt.width,Ne=kt.height,Xe=kt.depth||1,qe=0,ht=0,at=0),ne!==null?(Ye=ne.x,Rt=ne.y,Ut=ne.z):(Ye=0,Rt=0,Ut=0);const on=dt.convert(j.format),Pt=dt.convert(j.type);let Ze;j.isData3DTexture?(F.setTexture3D(j,0),Ze=G.TEXTURE_3D):j.isDataArrayTexture||j.isCompressedArrayTexture?(F.setTexture2DArray(j,0),Ze=G.TEXTURE_2D_ARRAY):(F.setTexture2D(j,0),Ze=G.TEXTURE_2D),G.pixelStorei(G.UNPACK_FLIP_Y_WEBGL,j.flipY),G.pixelStorei(G.UNPACK_PREMULTIPLY_ALPHA_WEBGL,j.premultiplyAlpha),G.pixelStorei(G.UNPACK_ALIGNMENT,j.unpackAlignment);const Qn=G.getParameter(G.UNPACK_ROW_LENGTH),wt=G.getParameter(G.UNPACK_IMAGE_HEIGHT),wn=G.getParameter(G.UNPACK_SKIP_PIXELS),wi=G.getParameter(G.UNPACK_SKIP_ROWS),un=G.getParameter(G.UNPACK_SKIP_IMAGES);G.pixelStorei(G.UNPACK_ROW_LENGTH,kt.width),G.pixelStorei(G.UNPACK_IMAGE_HEIGHT,kt.height),G.pixelStorei(G.UNPACK_SKIP_PIXELS,qe),G.pixelStorei(G.UNPACK_SKIP_ROWS,ht),G.pixelStorei(G.UNPACK_SKIP_IMAGES,at);const Ni=C.isDataArrayTexture||C.isData3DTexture,zt=j.isDataArrayTexture||j.isData3DTexture;if(C.isRenderTargetTexture||C.isDepthTexture){const jn=Fe.get(C),Oi=Fe.get(j),Dn=Fe.get(jn.__renderTarget),An=Fe.get(Oi.__renderTarget);Oe.bindFramebuffer(G.READ_FRAMEBUFFER,Dn.__webglFramebuffer),Oe.bindFramebuffer(G.DRAW_FRAMEBUFFER,An.__webglFramebuffer);for(let Jn=0;Jn<Xe;Jn++)Ni&&G.framebufferTextureLayer(G.READ_FRAMEBUFFER,G.COLOR_ATTACHMENT0,Fe.get(C).__webglTexture,Y,at+Jn),C.isDepthTexture?(zt&&G.framebufferTextureLayer(G.DRAW_FRAMEBUFFER,G.COLOR_ATTACHMENT0,Fe.get(j).__webglTexture,Y,Ut+Jn),G.blitFramebuffer(qe,ht,Me,Ne,Ye,Rt,Me,Ne,G.DEPTH_BUFFER_BIT,G.NEAREST)):zt?G.copyTexSubImage3D(Ze,Y,Ye,Rt,Ut+Jn,qe,ht,Me,Ne):G.copyTexSubImage2D(Ze,Y,Ye,Rt,Ut+Jn,qe,ht,Me,Ne);Oe.bindFramebuffer(G.READ_FRAMEBUFFER,null),Oe.bindFramebuffer(G.DRAW_FRAMEBUFFER,null)}else zt?C.isDataTexture||C.isData3DTexture?G.texSubImage3D(Ze,Y,Ye,Rt,Ut,Me,Ne,Xe,on,Pt,kt.data):j.isCompressedArrayTexture?G.compressedTexSubImage3D(Ze,Y,Ye,Rt,Ut,Me,Ne,Xe,on,kt.data):G.texSubImage3D(Ze,Y,Ye,Rt,Ut,Me,Ne,Xe,on,Pt,kt):C.isDataTexture?G.texSubImage2D(G.TEXTURE_2D,Y,Ye,Rt,Me,Ne,on,Pt,kt.data):C.isCompressedTexture?G.compressedTexSubImage2D(G.TEXTURE_2D,Y,Ye,Rt,kt.width,kt.height,on,kt.data):G.texSubImage2D(G.TEXTURE_2D,Y,Ye,Rt,Me,Ne,on,Pt,kt);G.pixelStorei(G.UNPACK_ROW_LENGTH,Qn),G.pixelStorei(G.UNPACK_IMAGE_HEIGHT,wt),G.pixelStorei(G.UNPACK_SKIP_PIXELS,wn),G.pixelStorei(G.UNPACK_SKIP_ROWS,wi),G.pixelStorei(G.UNPACK_SKIP_IMAGES,un),Y===0&&j.generateMipmaps&&G.generateMipmap(Ze),Oe.unbindTexture()},this.copyTextureToTexture3D=function(C,j,J=null,ne=null,Y=0){return C.isTexture!==!0&&(jo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),J=arguments[0]||null,ne=arguments[1]||null,C=arguments[2],j=arguments[3],Y=arguments[4]||0),jo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(C,j,J,ne,Y)},this.initRenderTarget=function(C){Fe.get(C).__webglFramebuffer===void 0&&F.setupRenderTarget(C)},this.initTexture=function(C){C.isCubeTexture?F.setTextureCube(C,0):C.isData3DTexture?F.setTexture3D(C,0):C.isDataArrayTexture||C.isCompressedArrayTexture?F.setTexture2DArray(C,0):F.setTexture2D(C,0),Oe.unbindTexture()},this.resetState=function(){U=0,O=0,V=null,Oe.reset(),It.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ji}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=Ct._getDrawingBufferColorSpace(e),t.unpackColorSpace=Ct._getUnpackColorSpace()}}class Ed{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new st(e),this.density=t}clone(){return new Ed(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class RP extends tn{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Ti,this.environmentIntensity=1,this.environmentRotation=new Ti,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class PP{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=ed,this.updateRanges=[],this.version=0,this.uuid=Ei()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let i=0,s=this.stride;i<s;i++)this.array[e+i]=t.array[n+i];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Ei()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Ei()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const zn=new N;class Md{constructor(e,t,n,i=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=i}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)zn.fromBufferAttribute(this,t),zn.applyMatrix4(e),this.setXYZ(t,zn.x,zn.y,zn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)zn.fromBufferAttribute(this,t),zn.applyNormalMatrix(e),this.setXYZ(t,zn.x,zn.y,zn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)zn.fromBufferAttribute(this,t),zn.transformDirection(e),this.setXYZ(t,zn.x,zn.y,zn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=xi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Vt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=Vt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=Vt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=Vt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=Vt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=xi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=xi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=xi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=xi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=Vt(t,this.array),n=Vt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=Vt(t,this.array),n=Vt(n,this.array),i=Vt(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=Vt(t,this.array),n=Vt(n,this.array),i=Vt(i,this.array),s=Vt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return new ln(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Md(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const Tm=new N,wm=new Ot,Am=new Ot,CP=new N,Rm=new ft,hc=new N,Zu=new Ii,Pm=new ft,Qu=new co;class Gg extends Re{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=Cp,this.bindMatrix=new ft,this.bindMatrixInverse=new ft,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new Mi),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,hc),this.boundingBox.expandByPoint(hc)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new Ii),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,hc),this.boundingSphere.expandByPoint(hc)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,i=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Zu.copy(this.boundingSphere),Zu.applyMatrix4(i),e.ray.intersectsSphere(Zu)!==!1&&(Pm.copy(i).invert(),Qu.copy(e.ray).applyMatrix4(Pm),!(this.boundingBox!==null&&Qu.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,Qu)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new Ot,t=this.geometry.attributes.skinWeight;for(let n=0,i=t.count;n<i;n++){e.fromBufferAttribute(t,n);const s=1/e.manhattanLength();s!==1/0?e.multiplyScalar(s):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===Cp?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===BM?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,i=this.geometry;wm.fromBufferAttribute(i.attributes.skinIndex,e),Am.fromBufferAttribute(i.attributes.skinWeight,e),Tm.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let s=0;s<4;s++){const a=Am.getComponent(s);if(a!==0){const c=wm.getComponent(s);Rm.multiplyMatrices(n.bones[c].matrixWorld,n.boneInverses[c]),t.addScaledVector(CP.copy(Tm).applyMatrix4(Rm),a)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Vc extends tn{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Wg extends Mn{constructor(e=null,t=1,n=1,i,s,a,c,u,h=Gn,f=Gn,p,m){super(null,a,c,u,h,f,i,s,p,m),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Cm=new ft,DP=new ft;class ra{constructor(e=[],t=[]){this.uuid=Ei(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,i=this.bones.length;n<i;n++)this.boneInverses.push(new ft)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new ft;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,i=this.boneTexture;for(let s=0,a=e.length;s<a;s++){const c=e[s]?e[s].matrixWorld:DP;Cm.multiplyMatrices(c,t[s]),Cm.toArray(n,s*16)}i!==null&&(i.needsUpdate=!0)}clone(){return new ra(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Wg(t,e,e,fi,Si);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const i=this.bones[t];if(i.name===e)return i}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,i=e.bones.length;n<i;n++){const s=e.bones[n];let a=t[s];a===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",s),a=new Vc),this.bones.push(a),this.boneInverses.push(new ft().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let i=0,s=t.length;i<s;i++){const a=t[i];e.bones.push(a.uuid);const c=n[i];e.boneInverses.push(c.toArray())}return e}}class nd extends ln{constructor(e,t,n,i=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=i}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const zs=new ft,Dm=new ft,dc=[],Im=new Mi,IP=new ft,Uo=new Re,Bo=new Ii;class LP extends Re{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new nd(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let i=0;i<n;i++)this.setMatrixAt(i,IP)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new Mi),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,zs),Im.copy(e.boundingBox).applyMatrix4(zs),this.boundingBox.union(Im)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new Ii),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,zs),Bo.copy(e.boundingSphere).applyMatrix4(zs),this.boundingSphere.union(Bo)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,i=this.morphTexture.source.data.data,s=n.length+1,a=e*s+1;for(let c=0;c<n.length;c++)n[c]=i[a+c]}raycast(e,t){const n=this.matrixWorld,i=this.count;if(Uo.geometry=this.geometry,Uo.material=this.material,Uo.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Bo.copy(this.boundingSphere),Bo.applyMatrix4(n),e.ray.intersectsSphere(Bo)!==!1))for(let s=0;s<i;s++){this.getMatrixAt(s,zs),Dm.multiplyMatrices(n,zs),Uo.matrixWorld=Dm,Uo.raycast(e,dc);for(let a=0,c=dc.length;a<c;a++){const u=dc[a];u.instanceId=s,u.object=this,t.push(u)}dc.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new nd(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,i=n.length+1;this.morphTexture===null&&(this.morphTexture=new Wg(new Float32Array(i*this.count),i,this.count,dd,Si));const s=this.morphTexture.source.data.data;let a=0;for(let h=0;h<n.length;h++)a+=n[h];const c=this.geometry.morphTargetsRelative?1:1-a,u=i*e;s[u]=c,s.set(n,u+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class Gc extends Di{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new st(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Uc=new N,Bc=new N,Lm=new ft,ko=new co,fc=new Ii,Ju=new N,Fm=new N;class yi extends tn{constructor(e=new _n,t=new Gc){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let i=1,s=t.count;i<s;i++)Uc.fromBufferAttribute(t,i-1),Bc.fromBufferAttribute(t,i),n[i]=n[i-1],n[i]+=Uc.distanceTo(Bc);e.setAttribute("lineDistance",new $t(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),fc.copy(n.boundingSphere),fc.applyMatrix4(i),fc.radius+=s,e.ray.intersectsSphere(fc)===!1)return;Lm.copy(i).invert(),ko.copy(e.ray).applyMatrix4(Lm);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=this.isLineSegments?2:1,f=n.index,m=n.attributes.position;if(f!==null){const g=Math.max(0,a.start),x=Math.min(f.count,a.start+a.count);for(let E=g,v=x-1;E<v;E+=h){const _=f.getX(E),A=f.getX(E+1),w=pc(this,e,ko,u,_,A);w&&t.push(w)}if(this.isLineLoop){const E=f.getX(x-1),v=f.getX(g),_=pc(this,e,ko,u,E,v);_&&t.push(_)}}else{const g=Math.max(0,a.start),x=Math.min(m.count,a.start+a.count);for(let E=g,v=x-1;E<v;E+=h){const _=pc(this,e,ko,u,E,E+1);_&&t.push(_)}if(this.isLineLoop){const E=pc(this,e,ko,u,x-1,g);E&&t.push(E)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function pc(r,e,t,n,i,s){const a=r.geometry.attributes.position;if(Uc.fromBufferAttribute(a,i),Bc.fromBufferAttribute(a,s),t.distanceSqToSegment(Uc,Bc,Ju,Fm)>n)return;Ju.applyMatrix4(r.matrixWorld);const u=e.ray.origin.distanceTo(Ju);if(!(u<e.near||u>e.far))return{distance:u,point:Fm.clone().applyMatrix4(r.matrixWorld),index:i,face:null,faceIndex:null,barycoord:null,object:r}}const Nm=new N,Om=new N;class jg extends yi{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let i=0,s=t.count;i<s;i+=2)Nm.fromBufferAttribute(t,i),Om.fromBufferAttribute(t,i+1),n[i]=i===0?0:n[i-1],n[i+1]=n[i]+Nm.distanceTo(Om);e.setAttribute("lineDistance",new $t(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class FP extends yi{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class Xg extends Di{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new st(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Um=new ft,id=new co,mc=new Ii,gc=new N;class NP extends tn{constructor(e=new _n,t=new Xg){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),mc.copy(n.boundingSphere),mc.applyMatrix4(i),mc.radius+=s,e.ray.intersectsSphere(mc)===!1)return;Um.copy(i).invert(),id.copy(e.ray).applyMatrix4(Um);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=n.index,p=n.attributes.position;if(h!==null){const m=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let x=m,E=g;x<E;x++){const v=h.getX(x);gc.fromBufferAttribute(p,v),Bm(gc,v,u,i,e,t,this)}}else{const m=Math.max(0,a.start),g=Math.min(p.count,a.start+a.count);for(let x=m,E=g;x<E;x++)gc.fromBufferAttribute(p,x),Bm(gc,x,u,i,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function Bm(r,e,t,n,i,s,a){const c=id.distanceSqToPoint(r);if(c<t){const u=new N;id.closestPointToPoint(r,u),u.applyMatrix4(n);const h=i.ray.origin.distanceTo(u);if(h<i.near||h>i.far)return;s.push({distance:h,distanceToRay:Math.sqrt(c),point:u,index:e,face:null,faceIndex:null,barycoord:null,object:a})}}class Pn extends _n{constructor(e=1,t=1,n=1,i=32,s=1,a=!1,c=0,u=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:i,heightSegments:s,openEnded:a,thetaStart:c,thetaLength:u};const h=this;i=Math.floor(i),s=Math.floor(s);const f=[],p=[],m=[],g=[];let x=0;const E=[],v=n/2;let _=0;A(),a===!1&&(e>0&&w(!0),t>0&&w(!1)),this.setIndex(f),this.setAttribute("position",new $t(p,3)),this.setAttribute("normal",new $t(m,3)),this.setAttribute("uv",new $t(g,2));function A(){const b=new N,B=new N;let U=0;const O=(t-e)/n;for(let V=0;V<=s;V++){const I=[],R=V/s,H=R*(t-e)+e;for(let ee=0;ee<=i;ee++){const te=ee/i,se=te*u+c,he=Math.sin(se),q=Math.cos(se);B.x=H*he,B.y=-R*n+v,B.z=H*q,p.push(B.x,B.y,B.z),b.set(he,O,q).normalize(),m.push(b.x,b.y,b.z),g.push(te,1-R),I.push(x++)}E.push(I)}for(let V=0;V<i;V++)for(let I=0;I<s;I++){const R=E[I][V],H=E[I+1][V],ee=E[I+1][V+1],te=E[I][V+1];(e>0||I!==0)&&(f.push(R,H,te),U+=3),(t>0||I!==s-1)&&(f.push(H,ee,te),U+=3)}h.addGroup(_,U,0),_+=U}function w(b){const B=x,U=new lt,O=new N;let V=0;const I=b===!0?e:t,R=b===!0?1:-1;for(let ee=1;ee<=i;ee++)p.push(0,v*R,0),m.push(0,R,0),g.push(.5,.5),x++;const H=x;for(let ee=0;ee<=i;ee++){const se=ee/i*u+c,he=Math.cos(se),q=Math.sin(se);O.x=I*q,O.y=v*R,O.z=I*he,p.push(O.x,O.y,O.z),m.push(0,R,0),U.x=he*.5+.5,U.y=q*.5*R+.5,g.push(U.x,U.y),x++}for(let ee=0;ee<i;ee++){const te=B+ee,se=H+ee;b===!0?f.push(se,se+1,te):f.push(se+1,se,te),V+=3}h.addGroup(_,V,b===!0?1:2),_+=V}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Pn(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Td extends Pn{constructor(e=1,t=1,n=32,i=1,s=!1,a=0,c=Math.PI*2){super(0,e,t,n,i,s,a,c),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:i,openEnded:s,thetaStart:a,thetaLength:c}}static fromJSON(e){return new Td(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class wd extends _n{constructor(e=[],t=[],n=1,i=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:i};const s=[],a=[];c(i),h(n),f(),this.setAttribute("position",new $t(s,3)),this.setAttribute("normal",new $t(s.slice(),3)),this.setAttribute("uv",new $t(a,2)),i===0?this.computeVertexNormals():this.normalizeNormals();function c(A){const w=new N,b=new N,B=new N;for(let U=0;U<t.length;U+=3)g(t[U+0],w),g(t[U+1],b),g(t[U+2],B),u(w,b,B,A)}function u(A,w,b,B){const U=B+1,O=[];for(let V=0;V<=U;V++){O[V]=[];const I=A.clone().lerp(b,V/U),R=w.clone().lerp(b,V/U),H=U-V;for(let ee=0;ee<=H;ee++)ee===0&&V===U?O[V][ee]=I:O[V][ee]=I.clone().lerp(R,ee/H)}for(let V=0;V<U;V++)for(let I=0;I<2*(U-V)-1;I++){const R=Math.floor(I/2);I%2===0?(m(O[V][R+1]),m(O[V+1][R]),m(O[V][R])):(m(O[V][R+1]),m(O[V+1][R+1]),m(O[V+1][R]))}}function h(A){const w=new N;for(let b=0;b<s.length;b+=3)w.x=s[b+0],w.y=s[b+1],w.z=s[b+2],w.normalize().multiplyScalar(A),s[b+0]=w.x,s[b+1]=w.y,s[b+2]=w.z}function f(){const A=new N;for(let w=0;w<s.length;w+=3){A.x=s[w+0],A.y=s[w+1],A.z=s[w+2];const b=v(A)/2/Math.PI+.5,B=_(A)/Math.PI+.5;a.push(b,1-B)}x(),p()}function p(){for(let A=0;A<a.length;A+=6){const w=a[A+0],b=a[A+2],B=a[A+4],U=Math.max(w,b,B),O=Math.min(w,b,B);U>.9&&O<.1&&(w<.2&&(a[A+0]+=1),b<.2&&(a[A+2]+=1),B<.2&&(a[A+4]+=1))}}function m(A){s.push(A.x,A.y,A.z)}function g(A,w){const b=A*3;w.x=e[b+0],w.y=e[b+1],w.z=e[b+2]}function x(){const A=new N,w=new N,b=new N,B=new N,U=new lt,O=new lt,V=new lt;for(let I=0,R=0;I<s.length;I+=9,R+=6){A.set(s[I+0],s[I+1],s[I+2]),w.set(s[I+3],s[I+4],s[I+5]),b.set(s[I+6],s[I+7],s[I+8]),U.set(a[R+0],a[R+1]),O.set(a[R+2],a[R+3]),V.set(a[R+4],a[R+5]),B.copy(A).add(w).add(b).divideScalar(3);const H=v(B);E(U,R+0,A,H),E(O,R+2,w,H),E(V,R+4,b,H)}}function E(A,w,b,B){B<0&&A.x===1&&(a[w]=A.x-1),b.x===0&&b.z===0&&(a[w]=B/2/Math.PI+.5)}function v(A){return Math.atan2(A.z,-A.x)}function _(A){return Math.atan2(-A.y,Math.sqrt(A.x*A.x+A.z*A.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new wd(e.vertices,e.indices,e.radius,e.details)}}class js extends wd{constructor(e=1,t=0){const n=[1,0,0,-1,0,0,0,1,0,0,-1,0,0,0,1,0,0,-1],i=[0,2,4,0,4,3,0,3,5,0,5,2,1,2,5,1,5,3,1,3,4,1,4,2];super(n,i,e,t),this.type="OctahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new js(e.radius,e.detail)}}class sa extends _n{constructor(e=1,t=32,n=16,i=0,s=Math.PI*2,a=0,c=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:i,phiLength:s,thetaStart:a,thetaLength:c},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const u=Math.min(a+c,Math.PI);let h=0;const f=[],p=new N,m=new N,g=[],x=[],E=[],v=[];for(let _=0;_<=n;_++){const A=[],w=_/n;let b=0;_===0&&a===0?b=.5/t:_===n&&u===Math.PI&&(b=-.5/t);for(let B=0;B<=t;B++){const U=B/t;p.x=-e*Math.cos(i+U*s)*Math.sin(a+w*c),p.y=e*Math.cos(a+w*c),p.z=e*Math.sin(i+U*s)*Math.sin(a+w*c),x.push(p.x,p.y,p.z),m.copy(p).normalize(),E.push(m.x,m.y,m.z),v.push(U+b,1-w),A.push(h++)}f.push(A)}for(let _=0;_<n;_++)for(let A=0;A<t;A++){const w=f[_][A+1],b=f[_][A],B=f[_+1][A],U=f[_+1][A+1];(_!==0||a>0)&&g.push(w,b,U),(_!==n-1||u<Math.PI)&&g.push(b,B,U)}this.setIndex(g),this.setAttribute("position",new $t(x,3)),this.setAttribute("normal",new $t(E,3)),this.setAttribute("uv",new $t(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new sa(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class cs extends _n{constructor(e=1,t=.4,n=12,i=48,s=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:i,arc:s},n=Math.floor(n),i=Math.floor(i);const a=[],c=[],u=[],h=[],f=new N,p=new N,m=new N;for(let g=0;g<=n;g++)for(let x=0;x<=i;x++){const E=x/i*s,v=g/n*Math.PI*2;p.x=(e+t*Math.cos(v))*Math.cos(E),p.y=(e+t*Math.cos(v))*Math.sin(E),p.z=t*Math.sin(v),c.push(p.x,p.y,p.z),f.x=e*Math.cos(E),f.y=e*Math.sin(E),m.subVectors(p,f).normalize(),u.push(m.x,m.y,m.z),h.push(x/i),h.push(g/n)}for(let g=1;g<=n;g++)for(let x=1;x<=i;x++){const E=(i+1)*g+x-1,v=(i+1)*(g-1)+x-1,_=(i+1)*(g-1)+x,A=(i+1)*g+x;a.push(E,v,A),a.push(v,_,A)}this.setIndex(a),this.setAttribute("position",new $t(c,3)),this.setAttribute("normal",new $t(u,3)),this.setAttribute("uv",new $t(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new cs(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class hs extends Di{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new st(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new st(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Tg,this.normalScale=new lt(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Ti,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Li extends hs{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new lt(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return Cn(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new st(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new st(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new st(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function _c(r,e,t){return!r||!t&&r.constructor===e?r:typeof e.BYTES_PER_ELEMENT=="number"?new e(r):Array.prototype.slice.call(r)}function OP(r){return ArrayBuffer.isView(r)&&!(r instanceof DataView)}function UP(r){function e(i,s){return r[i]-r[s]}const t=r.length,n=new Array(t);for(let i=0;i!==t;++i)n[i]=i;return n.sort(e),n}function km(r,e,t){const n=r.length,i=new r.constructor(n);for(let s=0,a=0;a!==n;++s){const c=t[s]*e;for(let u=0;u!==e;++u)i[a++]=r[c+u]}return i}function qg(r,e,t,n){let i=1,s=r[0];for(;s!==void 0&&s[n]===void 0;)s=r[i++];if(s===void 0)return;let a=s[n];if(a!==void 0)if(Array.isArray(a))do a=s[n],a!==void 0&&(e.push(s.time),t.push.apply(t,a)),s=r[i++];while(s!==void 0);else if(a.toArray!==void 0)do a=s[n],a!==void 0&&(e.push(s.time),a.toArray(t,t.length)),s=r[i++];while(s!==void 0);else do a=s[n],a!==void 0&&(e.push(s.time),t.push(a)),s=r[i++];while(s!==void 0)}class oa{constructor(e,t,n,i){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=i!==void 0?i:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,i=t[n],s=t[n-1];e:{t:{let a;n:{i:if(!(e<i)){for(let c=n+2;;){if(i===void 0){if(e<s)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===c)break;if(s=i,i=t[++n],e<i)break t}a=t.length;break n}if(!(e>=s)){const c=t[1];e<c&&(n=2,s=c);for(let u=n-2;;){if(s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===u)break;if(i=s,s=t[--n-1],e>=s)break t}a=n,n=0;break n}break e}for(;n<a;){const c=n+a>>>1;e<t[c]?a=c:n=c+1}if(i=t[n],s=t[n-1],s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(i===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,s,i)}return this.interpolate_(n,s,e,i)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i;for(let a=0;a!==i;++a)t[a]=n[s+a];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class BP extends oa{constructor(e,t,n,i){super(e,t,n,i),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Vs,endingEnd:Vs}}intervalChanged_(e,t,n){const i=this.parameterPositions;let s=e-2,a=e+1,c=i[s],u=i[a];if(c===void 0)switch(this.getSettings_().endingStart){case Gs:s=e,c=2*t-n;break;case Nc:s=i.length-2,c=t+i[s]-i[s+1];break;default:s=e,c=n}if(u===void 0)switch(this.getSettings_().endingEnd){case Gs:a=e,u=2*n-t;break;case Nc:a=1,u=n+i[1]-i[0];break;default:a=e-1,u=t}const h=(n-t)*.5,f=this.valueSize;this._weightPrev=h/(t-c),this._weightNext=h/(u-n),this._offsetPrev=s*f,this._offsetNext=a*f}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=this._offsetPrev,p=this._offsetNext,m=this._weightPrev,g=this._weightNext,x=(n-t)/(i-t),E=x*x,v=E*x,_=-m*v+2*m*E-m*x,A=(1+m)*v+(-1.5-2*m)*E+(-.5+m)*x+1,w=(-1-g)*v+(1.5+g)*E+.5*x,b=g*v-g*E;for(let B=0;B!==c;++B)s[B]=_*a[f+B]+A*a[h+B]+w*a[u+B]+b*a[p+B];return s}}class Yg extends oa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=(n-t)/(i-t),p=1-f;for(let m=0;m!==c;++m)s[m]=a[h+m]*p+a[u+m]*f;return s}}class kP extends oa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e){return this.copySampleValue_(e-1)}}class Fi{constructor(e,t,n,i){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=_c(t,this.TimeBufferType),this.values=_c(n,this.ValueBufferType),this.setInterpolation(i||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:_c(e.times,Array),values:_c(e.values,Array)};const i=e.getInterpolation();i!==e.DefaultInterpolation&&(n.interpolation=i)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new kP(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new Yg(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new BP(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case ea:t=this.InterpolantFactoryMethodDiscrete;break;case ta:t=this.InterpolantFactoryMethodLinear;break;case Eu:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return ea;case this.InterpolantFactoryMethodLinear:return ta;case this.InterpolantFactoryMethodSmooth:return Eu}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]*=e}return this}trim(e,t){const n=this.times,i=n.length;let s=0,a=i-1;for(;s!==i&&n[s]<e;)++s;for(;a!==-1&&n[a]>t;)--a;if(++a,s!==0||a!==i){s>=a&&(a=Math.max(a,1),s=a-1);const c=this.getValueSize();this.times=n.slice(s,a),this.values=this.values.slice(s*c,a*c)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,i=this.values,s=n.length;s===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let a=null;for(let c=0;c!==s;c++){const u=n[c];if(typeof u=="number"&&isNaN(u)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,c,u),e=!1;break}if(a!==null&&a>u){console.error("THREE.KeyframeTrack: Out of order keys.",this,c,u,a),e=!1;break}a=u}if(i!==void 0&&OP(i))for(let c=0,u=i.length;c!==u;++c){const h=i[c];if(isNaN(h)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,c,h),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),i=this.getInterpolation()===Eu,s=e.length-1;let a=1;for(let c=1;c<s;++c){let u=!1;const h=e[c],f=e[c+1];if(h!==f&&(c!==1||h!==e[0]))if(i)u=!0;else{const p=c*n,m=p-n,g=p+n;for(let x=0;x!==n;++x){const E=t[p+x];if(E!==t[m+x]||E!==t[g+x]){u=!0;break}}}if(u){if(c!==a){e[a]=e[c];const p=c*n,m=a*n;for(let g=0;g!==n;++g)t[m+g]=t[p+g]}++a}}if(s>0){e[a]=e[s];for(let c=s*n,u=a*n,h=0;h!==n;++h)t[u+h]=t[c+h];++a}return a!==e.length?(this.times=e.slice(0,a),this.values=t.slice(0,a*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,i=new n(this.name,e,t);return i.createInterpolant=this.createInterpolant,i}}Fi.prototype.TimeBufferType=Float32Array;Fi.prototype.ValueBufferType=Float32Array;Fi.prototype.DefaultInterpolation=ta;class ho extends Fi{constructor(e,t,n){super(e,t,n)}}ho.prototype.ValueTypeName="bool";ho.prototype.ValueBufferType=Array;ho.prototype.DefaultInterpolation=ea;ho.prototype.InterpolantFactoryMethodLinear=void 0;ho.prototype.InterpolantFactoryMethodSmooth=void 0;class Kg extends Fi{}Kg.prototype.ValueTypeName="color";class so extends Fi{}so.prototype.ValueTypeName="number";class zP extends oa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=(n-t)/(i-t);let h=e*c;for(let f=h+c;h!==f;h+=4)Et.slerpFlat(s,0,a,h-c,a,h,u);return s}}class wr extends Fi{InterpolantFactoryMethodLinear(e){return new zP(this.times,this.values,this.getValueSize(),e)}}wr.prototype.ValueTypeName="quaternion";wr.prototype.InterpolantFactoryMethodSmooth=void 0;class fo extends Fi{constructor(e,t,n){super(e,t,n)}}fo.prototype.ValueTypeName="string";fo.prototype.ValueBufferType=Array;fo.prototype.DefaultInterpolation=ea;fo.prototype.InterpolantFactoryMethodLinear=void 0;fo.prototype.InterpolantFactoryMethodSmooth=void 0;class Ar extends Fi{}Ar.prototype.ValueTypeName="vector";class oo{constructor(e="",t=-1,n=[],i=_d){this.name=e,this.tracks=n,this.duration=t,this.blendMode=i,this.uuid=Ei(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,i=1/(e.fps||1);for(let a=0,c=n.length;a!==c;++a)t.push(VP(n[a]).scale(i));const s=new this(e.name,e.duration,t,e.blendMode);return s.uuid=e.uuid,s}static toJSON(e){const t=[],n=e.tracks,i={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let s=0,a=n.length;s!==a;++s)t.push(Fi.toJSON(n[s]));return i}static CreateFromMorphTargetSequence(e,t,n,i){const s=t.length,a=[];for(let c=0;c<s;c++){let u=[],h=[];u.push((c+s-1)%s,c,(c+1)%s),h.push(0,1,0);const f=UP(u);u=km(u,1,f),h=km(h,1,f),!i&&u[0]===0&&(u.push(s),h.push(h[0])),a.push(new so(".morphTargetInfluences["+t[c].name+"]",u,h).scale(1/n))}return new this(e,-1,a)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const i=e;n=i.geometry&&i.geometry.animations||i.animations}for(let i=0;i<n.length;i++)if(n[i].name===t)return n[i];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const i={},s=/^([\w-]*?)([\d]+)$/;for(let c=0,u=e.length;c<u;c++){const h=e[c],f=h.name.match(s);if(f&&f.length>1){const p=f[1];let m=i[p];m||(i[p]=m=[]),m.push(h)}}const a=[];for(const c in i)a.push(this.CreateFromMorphTargetSequence(c,i[c],t,n));return a}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(p,m,g,x,E){if(g.length!==0){const v=[],_=[];qg(g,v,_,x),v.length!==0&&E.push(new p(m,v,_))}},i=[],s=e.name||"default",a=e.fps||30,c=e.blendMode;let u=e.length||-1;const h=e.hierarchy||[];for(let p=0;p<h.length;p++){const m=h[p].keys;if(!(!m||m.length===0))if(m[0].morphTargets){const g={};let x;for(x=0;x<m.length;x++)if(m[x].morphTargets)for(let E=0;E<m[x].morphTargets.length;E++)g[m[x].morphTargets[E]]=-1;for(const E in g){const v=[],_=[];for(let A=0;A!==m[x].morphTargets.length;++A){const w=m[x];v.push(w.time),_.push(w.morphTarget===E?1:0)}i.push(new so(".morphTargetInfluence["+E+"]",v,_))}u=g.length*a}else{const g=".bones["+t[p].name+"]";n(Ar,g+".position",m,"pos",i),n(wr,g+".quaternion",m,"rot",i),n(Ar,g+".scale",m,"scl",i)}}return i.length===0?null:new this(s,u,i,c)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,i=e.length;n!==i;++n){const s=this.tracks[n];t=Math.max(t,s.times[s.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function HP(r){switch(r.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return so;case"vector":case"vector2":case"vector3":case"vector4":return Ar;case"color":return Kg;case"quaternion":return wr;case"bool":case"boolean":return ho;case"string":return fo}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+r)}function VP(r){if(r.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=HP(r.type);if(r.times===void 0){const t=[],n=[];qg(r.keys,t,n,"value"),r.times=t,r.values=n}return e.parse!==void 0?e.parse(r):new e(r.name,r.times,r.values,r.interpolation)}const Sr={enabled:!1,files:{},add:function(r,e){this.enabled!==!1&&(this.files[r]=e)},get:function(r){if(this.enabled!==!1)return this.files[r]},remove:function(r){delete this.files[r]},clear:function(){this.files={}}};class GP{constructor(e,t,n){const i=this;let s=!1,a=0,c=0,u;const h=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(f){c++,s===!1&&i.onStart!==void 0&&i.onStart(f,a,c),s=!0},this.itemEnd=function(f){a++,i.onProgress!==void 0&&i.onProgress(f,a,c),a===c&&(s=!1,i.onLoad!==void 0&&i.onLoad())},this.itemError=function(f){i.onError!==void 0&&i.onError(f)},this.resolveURL=function(f){return u?u(f):f},this.setURLModifier=function(f){return u=f,this},this.addHandler=function(f,p){return h.push(f,p),this},this.removeHandler=function(f){const p=h.indexOf(f);return p!==-1&&h.splice(p,2),this},this.getHandler=function(f){for(let p=0,m=h.length;p<m;p+=2){const g=h[p],x=h[p+1];if(g.global&&(g.lastIndex=0),g.test(f))return x}return null}}}const WP=new GP;class ds{constructor(e){this.manager=e!==void 0?e:WP,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(i,s){n.load(e,i,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}ds.DEFAULT_MATERIAL_NAME="__DEFAULT";const Ki={};class jP extends Error{constructor(e,t){super(e),this.response=t}}class Ad extends ds{constructor(e){super(e)}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=Sr.get(e);if(s!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(s),this.manager.itemEnd(e)},0),s;if(Ki[e]!==void 0){Ki[e].push({onLoad:t,onProgress:n,onError:i});return}Ki[e]=[],Ki[e].push({onLoad:t,onProgress:n,onError:i});const a=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),c=this.mimeType,u=this.responseType;fetch(a).then(h=>{if(h.status===200||h.status===0){if(h.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||h.body===void 0||h.body.getReader===void 0)return h;const f=Ki[e],p=h.body.getReader(),m=h.headers.get("X-File-Size")||h.headers.get("Content-Length"),g=m?parseInt(m):0,x=g!==0;let E=0;const v=new ReadableStream({start(_){A();function A(){p.read().then(({done:w,value:b})=>{if(w)_.close();else{E+=b.byteLength;const B=new ProgressEvent("progress",{lengthComputable:x,loaded:E,total:g});for(let U=0,O=f.length;U<O;U++){const V=f[U];V.onProgress&&V.onProgress(B)}_.enqueue(b),A()}},w=>{_.error(w)})}}});return new Response(v)}else throw new jP(`fetch for "${h.url}" responded with ${h.status}: ${h.statusText}`,h)}).then(h=>{switch(u){case"arraybuffer":return h.arrayBuffer();case"blob":return h.blob();case"document":return h.text().then(f=>new DOMParser().parseFromString(f,c));case"json":return h.json();default:if(c===void 0)return h.text();{const p=/charset="?([^;"\s]*)"?/i.exec(c),m=p&&p[1]?p[1].toLowerCase():void 0,g=new TextDecoder(m);return h.arrayBuffer().then(x=>g.decode(x))}}}).then(h=>{Sr.add(e,h);const f=Ki[e];delete Ki[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onLoad&&g.onLoad(h)}}).catch(h=>{const f=Ki[e];if(f===void 0)throw this.manager.itemError(e),h;delete Ki[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onError&&g.onError(h)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class XP extends ds{constructor(e){super(e)}load(e,t,n,i){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=Sr.get(e);if(a!==void 0)return s.manager.itemStart(e),setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a;const c=na("img");function u(){f(),Sr.add(e,this),t&&t(this),s.manager.itemEnd(e)}function h(p){f(),i&&i(p),s.manager.itemError(e),s.manager.itemEnd(e)}function f(){c.removeEventListener("load",u,!1),c.removeEventListener("error",h,!1)}return c.addEventListener("load",u,!1),c.addEventListener("error",h,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(c.crossOrigin=this.crossOrigin),s.manager.itemStart(e),c.src=e,c}}class qP extends ds{constructor(e){super(e)}load(e,t,n,i){const s=new Mn,a=new XP(this.manager);return a.setCrossOrigin(this.crossOrigin),a.setPath(this.path),a.load(e,function(c){s.image=c,s.needsUpdate=!0,t!==void 0&&t(s)},n,i),s}}class Wc extends tn{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new st(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const eh=new ft,zm=new N,Hm=new N;class Rd{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new lt(512,512),this.map=null,this.mapPass=null,this.matrix=new ft,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new xd,this._frameExtents=new lt(1,1),this._viewportCount=1,this._viewports=[new Ot(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;zm.setFromMatrixPosition(e.matrixWorld),t.position.copy(zm),Hm.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Hm),t.updateMatrixWorld(),eh.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(eh),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(eh)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class YP extends Rd{constructor(){super(new Vn(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=io*2*e.angle*this.focus,i=this.mapSize.width/this.mapSize.height,s=e.distance||t.far;(n!==t.fov||i!==t.aspect||s!==t.far)&&(t.fov=n,t.aspect=i,t.far=s,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class KP extends Wc{constructor(e,t,n=0,i=Math.PI/3,s=0,a=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(tn.DEFAULT_UP),this.updateMatrix(),this.target=new tn,this.distance=n,this.angle=i,this.penumbra=s,this.decay=a,this.map=null,this.shadow=new YP}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const Vm=new ft,zo=new N,th=new N;class $P extends Rd{constructor(){super(new Vn(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new lt(4,2),this._viewportCount=6,this._viewports=[new Ot(2,1,1,1),new Ot(0,1,1,1),new Ot(3,1,1,1),new Ot(1,1,1,1),new Ot(3,0,1,1),new Ot(1,0,1,1)],this._cubeDirections=[new N(1,0,0),new N(-1,0,0),new N(0,0,1),new N(0,0,-1),new N(0,1,0),new N(0,-1,0)],this._cubeUps=[new N(0,1,0),new N(0,1,0),new N(0,1,0),new N(0,1,0),new N(0,0,1),new N(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,i=this.matrix,s=e.distance||n.far;s!==n.far&&(n.far=s,n.updateProjectionMatrix()),zo.setFromMatrixPosition(e.matrixWorld),n.position.copy(zo),th.copy(n.position),th.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(th),n.updateMatrixWorld(),i.makeTranslation(-zo.x,-zo.y,-zo.z),Vm.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Vm)}}class $g extends Wc{constructor(e,t,n=0,i=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=i,this.shadow=new $P}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class ZP extends Rd{constructor(){super(new bd(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Dc extends Wc{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(tn.DEFAULT_UP),this.updateMatrix(),this.target=new tn,this.shadow=new ZP}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class QP extends Wc{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}class Qo{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,i=e.length;n<i;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class JP extends ds{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=Sr.get(e);if(a!==void 0){if(s.manager.itemStart(e),a.then){a.then(h=>{t&&t(h),s.manager.itemEnd(e)}).catch(h=>{i&&i(h)});return}return setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a}const c={};c.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",c.headers=this.requestHeader;const u=fetch(e,c).then(function(h){return h.blob()}).then(function(h){return createImageBitmap(h,Object.assign(s.options,{colorSpaceConversion:"none"}))}).then(function(h){return Sr.add(e,h),t&&t(h),s.manager.itemEnd(e),h}).catch(function(h){i&&i(h),Sr.remove(e),s.manager.itemError(e),s.manager.itemEnd(e)});Sr.add(e,u),s.manager.itemStart(e)}}class eC{constructor(e=!0){this.autoStart=e,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=Gm(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let e=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const t=Gm();e=(t-this.oldTime)/1e3,this.oldTime=t,this.elapsedTime+=e}return e}}function Gm(){return performance.now()}class tC{constructor(e,t,n){this.binding=e,this.valueSize=n;let i,s,a;switch(t){case"quaternion":i=this._slerp,s=this._slerpAdditive,a=this._setAdditiveIdentityQuaternion,this.buffer=new Float64Array(n*6),this._workIndex=5;break;case"string":case"bool":i=this._select,s=this._select,a=this._setAdditiveIdentityOther,this.buffer=new Array(n*5);break;default:i=this._lerp,s=this._lerpAdditive,a=this._setAdditiveIdentityNumeric,this.buffer=new Float64Array(n*5)}this._mixBufferRegion=i,this._mixBufferRegionAdditive=s,this._setIdentity=a,this._origIndex=3,this._addIndex=4,this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,this.useCount=0,this.referenceCount=0}accumulate(e,t){const n=this.buffer,i=this.valueSize,s=e*i+i;let a=this.cumulativeWeight;if(a===0){for(let c=0;c!==i;++c)n[s+c]=n[c];a=t}else{a+=t;const c=t/a;this._mixBufferRegion(n,s,0,c,i)}this.cumulativeWeight=a}accumulateAdditive(e){const t=this.buffer,n=this.valueSize,i=n*this._addIndex;this.cumulativeWeightAdditive===0&&this._setIdentity(),this._mixBufferRegionAdditive(t,i,0,e,n),this.cumulativeWeightAdditive+=e}apply(e){const t=this.valueSize,n=this.buffer,i=e*t+t,s=this.cumulativeWeight,a=this.cumulativeWeightAdditive,c=this.binding;if(this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,s<1){const u=t*this._origIndex;this._mixBufferRegion(n,i,u,1-s,t)}a>0&&this._mixBufferRegionAdditive(n,i,this._addIndex*t,1,t);for(let u=t,h=t+t;u!==h;++u)if(n[u]!==n[u+t]){c.setValue(n,i);break}}saveOriginalState(){const e=this.binding,t=this.buffer,n=this.valueSize,i=n*this._origIndex;e.getValue(t,i);for(let s=n,a=i;s!==a;++s)t[s]=t[i+s%n];this._setIdentity(),this.cumulativeWeight=0,this.cumulativeWeightAdditive=0}restoreOriginalState(){const e=this.valueSize*3;this.binding.setValue(this.buffer,e)}_setAdditiveIdentityNumeric(){const e=this._addIndex*this.valueSize,t=e+this.valueSize;for(let n=e;n<t;n++)this.buffer[n]=0}_setAdditiveIdentityQuaternion(){this._setAdditiveIdentityNumeric(),this.buffer[this._addIndex*this.valueSize+3]=1}_setAdditiveIdentityOther(){const e=this._origIndex*this.valueSize,t=this._addIndex*this.valueSize;for(let n=0;n<this.valueSize;n++)this.buffer[t+n]=this.buffer[e+n]}_select(e,t,n,i,s){if(i>=.5)for(let a=0;a!==s;++a)e[t+a]=e[n+a]}_slerp(e,t,n,i){Et.slerpFlat(e,t,e,t,e,n,i)}_slerpAdditive(e,t,n,i,s){const a=this._workIndex*s;Et.multiplyQuaternionsFlat(e,a,e,t,e,n),Et.slerpFlat(e,t,e,t,e,a,i)}_lerp(e,t,n,i,s){const a=1-i;for(let c=0;c!==s;++c){const u=t+c;e[u]=e[u]*a+e[n+c]*i}}_lerpAdditive(e,t,n,i,s){for(let a=0;a!==s;++a){const c=t+a;e[c]=e[c]+e[n+a]*i}}}const Pd="\\[\\]\\.:\\/",nC=new RegExp("["+Pd+"]","g"),Cd="[^"+Pd+"]",iC="[^"+Pd.replace("\\.","")+"]",rC=/((?:WC+[\/:])*)/.source.replace("WC",Cd),sC=/(WCOD+)?/.source.replace("WCOD",iC),oC=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Cd),aC=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Cd),cC=new RegExp("^"+rC+sC+oC+aC+"$"),lC=["material","materials","bones","map"];class uC{constructor(e,t,n){const i=n||Bt.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,i)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,i=this._bindings[n];i!==void 0&&i.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let i=this._targetGroup.nCachedObjects_,s=n.length;i!==s;++i)n[i].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class Bt{constructor(e,t,n){this.path=t,this.parsedPath=n||Bt.parseTrackName(t),this.node=Bt.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new Bt.Composite(e,t,n):new Bt(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(nC,"")}static parseTrackName(e){const t=cC.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},i=n.nodeName&&n.nodeName.lastIndexOf(".");if(i!==void 0&&i!==-1){const s=n.nodeName.substring(i+1);lC.indexOf(s)!==-1&&(n.nodeName=n.nodeName.substring(0,i),n.objectName=s)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(s){for(let a=0;a<s.length;a++){const c=s[a];if(c.name===t||c.uuid===t)return c;const u=n(c.children);if(u)return u}return null},i=n(e.children);if(i)return i}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)e[t++]=n[i]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,i=t.propertyName;let s=t.propertyIndex;if(e||(e=Bt.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let h=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let f=0;f<e.length;f++)if(e[f].name===h){h=f;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(h!==void 0){if(e[h]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[h]}}const a=e[i];if(a===void 0){const h=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+h+"."+i+" but it wasn't found.",e);return}let c=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?c=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(c=this.Versioning.MatrixWorldNeedsUpdate);let u=this.BindingType.Direct;if(s!==void 0){if(i==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[s]!==void 0&&(s=e.morphTargetDictionary[s])}u=this.BindingType.ArrayElement,this.resolvedProperty=a,this.propertyIndex=s}else a.fromArray!==void 0&&a.toArray!==void 0?(u=this.BindingType.HasFromToArray,this.resolvedProperty=a):Array.isArray(a)?(u=this.BindingType.EntireArray,this.resolvedProperty=a):this.propertyName=i;this.getValue=this.GetterByBindingType[u],this.setValue=this.SetterByBindingTypeAndVersioning[u][c]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}Bt.Composite=uC;Bt.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};Bt.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};Bt.prototype.GetterByBindingType=[Bt.prototype._getValue_direct,Bt.prototype._getValue_array,Bt.prototype._getValue_arrayElement,Bt.prototype._getValue_toArray];Bt.prototype.SetterByBindingTypeAndVersioning=[[Bt.prototype._setValue_direct,Bt.prototype._setValue_direct_setNeedsUpdate,Bt.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[Bt.prototype._setValue_array,Bt.prototype._setValue_array_setNeedsUpdate,Bt.prototype._setValue_array_setMatrixWorldNeedsUpdate],[Bt.prototype._setValue_arrayElement,Bt.prototype._setValue_arrayElement_setNeedsUpdate,Bt.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[Bt.prototype._setValue_fromArray,Bt.prototype._setValue_fromArray_setNeedsUpdate,Bt.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];class hC{constructor(e,t,n=null,i=t.blendMode){this._mixer=e,this._clip=t,this._localRoot=n,this.blendMode=i;const s=t.tracks,a=s.length,c=new Array(a),u={endingStart:Vs,endingEnd:Vs};for(let h=0;h!==a;++h){const f=s[h].createInterpolant(null);c[h]=f,f.settings=u}this._interpolantSettings=u,this._interpolants=c,this._propertyBindings=new Array(a),this._cacheIndex=null,this._byClipCacheIndex=null,this._timeScaleInterpolant=null,this._weightInterpolant=null,this.loop=gd,this._loopCount=-1,this._startTime=null,this.time=0,this.timeScale=1,this._effectiveTimeScale=1,this.weight=1,this._effectiveWeight=1,this.repetitions=1/0,this.paused=!1,this.enabled=!0,this.clampWhenFinished=!1,this.zeroSlopeAtStart=!0,this.zeroSlopeAtEnd=!0}play(){return this._mixer._activateAction(this),this}stop(){return this._mixer._deactivateAction(this),this.reset()}reset(){return this.paused=!1,this.enabled=!0,this.time=0,this._loopCount=-1,this._startTime=null,this.stopFading().stopWarping()}isRunning(){return this.enabled&&!this.paused&&this.timeScale!==0&&this._startTime===null&&this._mixer._isActiveAction(this)}isScheduled(){return this._mixer._isActiveAction(this)}startAt(e){return this._startTime=e,this}setLoop(e,t){return this.loop=e,this.repetitions=t,this}setEffectiveWeight(e){return this.weight=e,this._effectiveWeight=this.enabled?e:0,this.stopFading()}getEffectiveWeight(){return this._effectiveWeight}fadeIn(e){return this._scheduleFading(e,0,1)}fadeOut(e){return this._scheduleFading(e,1,0)}crossFadeFrom(e,t,n){if(e.fadeOut(t),this.fadeIn(t),n){const i=this._clip.duration,s=e._clip.duration,a=s/i,c=i/s;e.warp(1,a,t),this.warp(c,1,t)}return this}crossFadeTo(e,t,n){return e.crossFadeFrom(this,t,n)}stopFading(){const e=this._weightInterpolant;return e!==null&&(this._weightInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}setEffectiveTimeScale(e){return this.timeScale=e,this._effectiveTimeScale=this.paused?0:e,this.stopWarping()}getEffectiveTimeScale(){return this._effectiveTimeScale}setDuration(e){return this.timeScale=this._clip.duration/e,this.stopWarping()}syncWith(e){return this.time=e.time,this.timeScale=e.timeScale,this.stopWarping()}halt(e){return this.warp(this._effectiveTimeScale,0,e)}warp(e,t,n){const i=this._mixer,s=i.time,a=this.timeScale;let c=this._timeScaleInterpolant;c===null&&(c=i._lendControlInterpolant(),this._timeScaleInterpolant=c);const u=c.parameterPositions,h=c.sampleValues;return u[0]=s,u[1]=s+n,h[0]=e/a,h[1]=t/a,this}stopWarping(){const e=this._timeScaleInterpolant;return e!==null&&(this._timeScaleInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}getMixer(){return this._mixer}getClip(){return this._clip}getRoot(){return this._localRoot||this._mixer._root}_update(e,t,n,i){if(!this.enabled){this._updateWeight(e);return}const s=this._startTime;if(s!==null){const u=(e-s)*n;u<0||n===0?t=0:(this._startTime=null,t=n*u)}t*=this._updateTimeScale(e);const a=this._updateTime(t),c=this._updateWeight(e);if(c>0){const u=this._interpolants,h=this._propertyBindings;switch(this.blendMode){case HM:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulateAdditive(c);break;case _d:default:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulate(i,c)}}}_updateWeight(e){let t=0;if(this.enabled){t=this.weight;const n=this._weightInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopFading(),i===0&&(this.enabled=!1))}}return this._effectiveWeight=t,t}_updateTimeScale(e){let t=0;if(!this.paused){t=this.timeScale;const n=this._timeScaleInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopWarping(),t===0?this.paused=!0:this.timeScale=t)}}return this._effectiveTimeScale=t,t}_updateTime(e){const t=this._clip.duration,n=this.loop;let i=this.time+e,s=this._loopCount;const a=n===zM;if(e===0)return s===-1?i:a&&(s&1)===1?t-i:i;if(n===kM){s===-1&&(this._loopCount=0,this._setEndings(!0,!0,!1));e:{if(i>=t)i=t;else if(i<0)i=0;else{this.time=i;break e}this.clampWhenFinished?this.paused=!0:this.enabled=!1,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e<0?-1:1})}}else{if(s===-1&&(e>=0?(s=0,this._setEndings(!0,this.repetitions===0,a)):this._setEndings(this.repetitions===0,!0,a)),i>=t||i<0){const c=Math.floor(i/t);i-=t*c,s+=Math.abs(c);const u=this.repetitions-s;if(u<=0)this.clampWhenFinished?this.paused=!0:this.enabled=!1,i=e>0?t:0,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e>0?1:-1});else{if(u===1){const h=e<0;this._setEndings(h,!h,a)}else this._setEndings(!1,!1,a);this._loopCount=s,this.time=i,this._mixer.dispatchEvent({type:"loop",action:this,loopDelta:c})}}else this.time=i;if(a&&(s&1)===1)return t-i}return i}_setEndings(e,t,n){const i=this._interpolantSettings;n?(i.endingStart=Gs,i.endingEnd=Gs):(e?i.endingStart=this.zeroSlopeAtStart?Gs:Vs:i.endingStart=Nc,t?i.endingEnd=this.zeroSlopeAtEnd?Gs:Vs:i.endingEnd=Nc)}_scheduleFading(e,t,n){const i=this._mixer,s=i.time;let a=this._weightInterpolant;a===null&&(a=i._lendControlInterpolant(),this._weightInterpolant=a);const c=a.parameterPositions,u=a.sampleValues;return c[0]=s,u[0]=t,c[1]=s+e,u[1]=n,this}}const dC=new Float32Array(1);class Zg extends Rr{constructor(e){super(),this._root=e,this._initMemoryManager(),this._accuIndex=0,this.time=0,this.timeScale=1}_bindAction(e,t){const n=e._localRoot||this._root,i=e._clip.tracks,s=i.length,a=e._propertyBindings,c=e._interpolants,u=n.uuid,h=this._bindingsByRootAndName;let f=h[u];f===void 0&&(f={},h[u]=f);for(let p=0;p!==s;++p){const m=i[p],g=m.name;let x=f[g];if(x!==void 0)++x.referenceCount,a[p]=x;else{if(x=a[p],x!==void 0){x._cacheIndex===null&&(++x.referenceCount,this._addInactiveBinding(x,u,g));continue}const E=t&&t._propertyBindings[p].binding.parsedPath;x=new tC(Bt.create(n,g,E),m.ValueTypeName,m.getValueSize()),++x.referenceCount,this._addInactiveBinding(x,u,g),a[p]=x}c[p].resultBuffer=x.buffer}}_activateAction(e){if(!this._isActiveAction(e)){if(e._cacheIndex===null){const n=(e._localRoot||this._root).uuid,i=e._clip.uuid,s=this._actionsByClip[i];this._bindAction(e,s&&s.knownActions[0]),this._addInactiveAction(e,i,n)}const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];s.useCount++===0&&(this._lendBinding(s),s.saveOriginalState())}this._lendAction(e)}}_deactivateAction(e){if(this._isActiveAction(e)){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.useCount===0&&(s.restoreOriginalState(),this._takeBackBinding(s))}this._takeBackAction(e)}}_initMemoryManager(){this._actions=[],this._nActiveActions=0,this._actionsByClip={},this._bindings=[],this._nActiveBindings=0,this._bindingsByRootAndName={},this._controlInterpolants=[],this._nActiveControlInterpolants=0;const e=this;this.stats={actions:{get total(){return e._actions.length},get inUse(){return e._nActiveActions}},bindings:{get total(){return e._bindings.length},get inUse(){return e._nActiveBindings}},controlInterpolants:{get total(){return e._controlInterpolants.length},get inUse(){return e._nActiveControlInterpolants}}}}_isActiveAction(e){const t=e._cacheIndex;return t!==null&&t<this._nActiveActions}_addInactiveAction(e,t,n){const i=this._actions,s=this._actionsByClip;let a=s[t];if(a===void 0)a={knownActions:[e],actionByRoot:{}},e._byClipCacheIndex=0,s[t]=a;else{const c=a.knownActions;e._byClipCacheIndex=c.length,c.push(e)}e._cacheIndex=i.length,i.push(e),a.actionByRoot[n]=e}_removeInactiveAction(e){const t=this._actions,n=t[t.length-1],i=e._cacheIndex;n._cacheIndex=i,t[i]=n,t.pop(),e._cacheIndex=null;const s=e._clip.uuid,a=this._actionsByClip,c=a[s],u=c.knownActions,h=u[u.length-1],f=e._byClipCacheIndex;h._byClipCacheIndex=f,u[f]=h,u.pop(),e._byClipCacheIndex=null;const p=c.actionByRoot,m=(e._localRoot||this._root).uuid;delete p[m],u.length===0&&delete a[s],this._removeInactiveBindingsForAction(e)}_removeInactiveBindingsForAction(e){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.referenceCount===0&&this._removeInactiveBinding(s)}}_lendAction(e){const t=this._actions,n=e._cacheIndex,i=this._nActiveActions++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackAction(e){const t=this._actions,n=e._cacheIndex,i=--this._nActiveActions,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_addInactiveBinding(e,t,n){const i=this._bindingsByRootAndName,s=this._bindings;let a=i[t];a===void 0&&(a={},i[t]=a),a[n]=e,e._cacheIndex=s.length,s.push(e)}_removeInactiveBinding(e){const t=this._bindings,n=e.binding,i=n.rootNode.uuid,s=n.path,a=this._bindingsByRootAndName,c=a[i],u=t[t.length-1],h=e._cacheIndex;u._cacheIndex=h,t[h]=u,t.pop(),delete c[s],Object.keys(c).length===0&&delete a[i]}_lendBinding(e){const t=this._bindings,n=e._cacheIndex,i=this._nActiveBindings++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackBinding(e){const t=this._bindings,n=e._cacheIndex,i=--this._nActiveBindings,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_lendControlInterpolant(){const e=this._controlInterpolants,t=this._nActiveControlInterpolants++;let n=e[t];return n===void 0&&(n=new Yg(new Float32Array(2),new Float32Array(2),1,dC),n.__cacheIndex=t,e[t]=n),n}_takeBackControlInterpolant(e){const t=this._controlInterpolants,n=e.__cacheIndex,i=--this._nActiveControlInterpolants,s=t[i];e.__cacheIndex=i,t[i]=e,s.__cacheIndex=n,t[n]=s}clipAction(e,t,n){const i=t||this._root,s=i.uuid;let a=typeof e=="string"?oo.findByName(i,e):e;const c=a!==null?a.uuid:e,u=this._actionsByClip[c];let h=null;if(n===void 0&&(a!==null?n=a.blendMode:n=_d),u!==void 0){const p=u.actionByRoot[s];if(p!==void 0&&p.blendMode===n)return p;h=u.knownActions[0],a===null&&(a=h._clip)}if(a===null)return null;const f=new hC(this,a,t,n);return this._bindAction(f,h),this._addInactiveAction(f,c,s),f}existingAction(e,t){const n=t||this._root,i=n.uuid,s=typeof e=="string"?oo.findByName(n,e):e,a=s?s.uuid:e,c=this._actionsByClip[a];return c!==void 0&&c.actionByRoot[i]||null}stopAllAction(){const e=this._actions,t=this._nActiveActions;for(let n=t-1;n>=0;--n)e[n].stop();return this}update(e){e*=this.timeScale;const t=this._actions,n=this._nActiveActions,i=this.time+=e,s=Math.sign(e),a=this._accuIndex^=1;for(let h=0;h!==n;++h)t[h]._update(i,e,s,a);const c=this._bindings,u=this._nActiveBindings;for(let h=0;h!==u;++h)c[h].apply(a);return this}setTime(e){this.time=0;for(let t=0;t<this._actions.length;t++)this._actions[t].time=0;return this.update(e)}getRoot(){return this._root}uncacheClip(e){const t=this._actions,n=e.uuid,i=this._actionsByClip,s=i[n];if(s!==void 0){const a=s.knownActions;for(let c=0,u=a.length;c!==u;++c){const h=a[c];this._deactivateAction(h);const f=h._cacheIndex,p=t[t.length-1];h._cacheIndex=null,h._byClipCacheIndex=null,p._cacheIndex=f,t[f]=p,t.pop(),this._removeInactiveBindingsForAction(h)}delete i[n]}}uncacheRoot(e){const t=e.uuid,n=this._actionsByClip;for(const a in n){const c=n[a].actionByRoot,u=c[t];u!==void 0&&(this._deactivateAction(u),this._removeInactiveAction(u))}const i=this._bindingsByRootAndName,s=i[t];if(s!==void 0)for(const a in s){const c=s[a];c.restoreOriginalState(),this._removeInactiveBinding(c)}}uncacheAction(e,t){const n=this.existingAction(e,t);n!==null&&(this._deactivateAction(n),this._removeInactiveAction(n))}}const Wm=new ft;class Qg{constructor(e,t,n=0,i=1/0){this.ray=new co(e,t),this.near=n,this.far=i,this.camera=null,this.layers=new yd,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Wm.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Wm),this}intersectObject(e,t=!0,n=[]){return rd(e,this,n,t),n.sort(jm),n}intersectObjects(e,t=!0,n=[]){for(let i=0,s=e.length;i<s;i++)rd(e[i],this,n,t);return n.sort(jm),n}}function jm(r,e){return r.distance-e.distance}function rd(r,e,t,n){let i=!0;if(r.layers.test(e.layers)&&r.raycast(e,t)===!1&&(i=!1),i===!0&&n===!0){const s=r.children;for(let a=0,c=s.length;a<c;a++)rd(s[a],e,t,!0)}}class Xm{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Cn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}const gr=new N,vc=new ft,nh=new ft;class Jg extends jg{constructor(e){const t=e_(e),n=new _n,i=[],s=[],a=new st(0,0,1),c=new st(0,1,0);for(let h=0;h<t.length;h++){const f=t[h];f.parent&&f.parent.isBone&&(i.push(0,0,0),i.push(0,0,0),s.push(a.r,a.g,a.b),s.push(c.r,c.g,c.b))}n.setAttribute("position",new $t(i,3)),n.setAttribute("color",new $t(s,3));const u=new Gc({vertexColors:!0,depthTest:!1,depthWrite:!1,toneMapped:!1,transparent:!0});super(n,u),this.isSkeletonHelper=!0,this.type="SkeletonHelper",this.root=e,this.bones=t,this.matrix=e.matrixWorld,this.matrixAutoUpdate=!1}updateMatrixWorld(e){const t=this.bones,n=this.geometry,i=n.getAttribute("position");nh.copy(this.root.matrixWorld).invert();for(let s=0,a=0;s<t.length;s++){const c=t[s];c.parent&&c.parent.isBone&&(vc.multiplyMatrices(nh,c.matrixWorld),gr.setFromMatrixPosition(vc),i.setXYZ(a,gr.x,gr.y,gr.z),vc.multiplyMatrices(nh,c.parent.matrixWorld),gr.setFromMatrixPosition(vc),i.setXYZ(a+1,gr.x,gr.y,gr.z),a+=2)}n.getAttribute("position").needsUpdate=!0,super.updateMatrixWorld(e)}dispose(){this.geometry.dispose(),this.material.dispose()}}function e_(r){const e=[];r.isBone===!0&&e.push(r);for(let t=0;t<r.children.length;t++)e.push.apply(e,e_(r.children[t]));return e}class t_ extends Rr{constructor(e,t=null){super(),this.object=e,this.domElement=t,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(){}disconnect(){}dispose(){}update(){}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:"170"}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__="170");class n_ extends ds{constructor(e){super(e),this.animateBonePositions=!0,this.animateBoneRotations=!0}load(e,t,n,i){const s=this,a=new Ad(s.manager);a.setPath(s.path),a.setRequestHeader(s.requestHeader),a.setWithCredentials(s.withCredentials),a.load(e,function(c){try{t(s.parse(c))}catch(u){i?i(u):console.error(u),s.manager.itemError(e)}},n,i)}parse(e){function t(g){c(g)!=="HIERARCHY"&&console.error("THREE.BVHLoader: HIERARCHY expected.");const x=[],E=i(g,c(g),x);c(g)!=="MOTION"&&console.error("THREE.BVHLoader: MOTION expected.");let v=c(g).split(/[\s]+/);const _=parseInt(v[1]);isNaN(_)&&console.error("THREE.BVHLoader: Failed to read number of frames."),v=c(g).split(/[\s]+/);const A=parseFloat(v[2]);isNaN(A)&&console.error("THREE.BVHLoader: Failed to read frame time.");for(let w=0;w<_;w++)v=c(g).split(/[\s]+/),n(v,w*A,E);return x}function n(g,x,E){if(E.type==="ENDSITE")return;const v={time:x,position:new N,rotation:new Et};E.frames.push(v);const _=new Et,A=new N(1,0,0),w=new N(0,1,0),b=new N(0,0,1);for(let B=0;B<E.channels.length;B++)switch(E.channels[B]){case"Xposition":v.position.x=parseFloat(g.shift().trim());break;case"Yposition":v.position.y=parseFloat(g.shift().trim());break;case"Zposition":v.position.z=parseFloat(g.shift().trim());break;case"Xrotation":_.setFromAxisAngle(A,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Yrotation":_.setFromAxisAngle(w,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Zrotation":_.setFromAxisAngle(b,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;default:console.warn("THREE.BVHLoader: Invalid channel type.")}for(let B=0;B<E.children.length;B++)n(g,x,E.children[B])}function i(g,x,E){const v={name:"",type:"",frames:[]};E.push(v);let _=x.split(/[\s]+/);_[0].toUpperCase()==="END"&&_[1].toUpperCase()==="SITE"?(v.type="ENDSITE",v.name="ENDSITE"):(v.name=_[1],v.type=_[0].toUpperCase()),c(g)!=="{"&&console.error("THREE.BVHLoader: Expected opening { after type & name"),_=c(g).split(/[\s]+/),_[0]!=="OFFSET"&&console.error("THREE.BVHLoader: Expected OFFSET but got: "+_[0]),_.length!==4&&console.error("THREE.BVHLoader: Invalid number of values for OFFSET.");const A=new N(parseFloat(_[1]),parseFloat(_[2]),parseFloat(_[3]));if((isNaN(A.x)||isNaN(A.y)||isNaN(A.z))&&console.error("THREE.BVHLoader: Invalid values of OFFSET."),v.offset=A,v.type!=="ENDSITE"){_=c(g).split(/[\s]+/),_[0]!=="CHANNELS"&&console.error("THREE.BVHLoader: Expected CHANNELS definition.");const w=parseInt(_[1]);v.channels=_.splice(2,w),v.children=[]}for(;;){const w=c(g);if(w==="}")return v;v.children.push(i(g,w,E))}}function s(g,x){const E=new Vc;if(x.push(E),E.position.add(g.offset),E.name=g.name,g.type!=="ENDSITE")for(let v=0;v<g.children.length;v++)E.add(s(g.children[v],x));return E}function a(g){const x=[];for(let E=0;E<g.length;E++){const v=g[E];if(v.type==="ENDSITE")continue;const _=[],A=[],w=[];for(let b=0;b<v.frames.length;b++){const B=v.frames[b];_.push(B.time),A.push(B.position.x+v.offset.x),A.push(B.position.y+v.offset.y),A.push(B.position.z+v.offset.z),w.push(B.rotation.x),w.push(B.rotation.y),w.push(B.rotation.z),w.push(B.rotation.w)}u.animateBonePositions&&x.push(new Ar(v.name+".position",_,A)),u.animateBoneRotations&&x.push(new wr(v.name+".quaternion",_,w))}return new oo("animation",-1,x)}function c(g){let x;for(;(x=g.shift().trim()).length===0;);return x}const u=this,h=e.split(/[\r\n]+/g),f=t(h),p=[];s(f[0],p);const m=a(f);return{skeleton:new ra(p),clip:m}}}var Ci=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},ih={},qm;function mn(){return qm||(qm=1,(function(r){var e=Object.defineProperty,t=Object.defineProperties,n=Object.getOwnPropertyDescriptors,i=Object.getOwnPropertySymbols,s=Object.prototype.hasOwnProperty,a=Object.prototype.propertyIsEnumerable,c=(S,L,W)=>L in S?e(S,L,{enumerable:!0,configurable:!0,writable:!0,value:W}):S[L]=W,u=(S,L)=>{for(var W in L||(L={}))s.call(L,W)&&c(S,W,L[W]);if(i)for(var W of i(L))a.call(L,W)&&c(S,W,L[W]);return S},h=(S,L)=>t(S,n(L)),f=S=>e(S,"__esModule",{value:!0}),p=(S,L)=>{f(S);for(var W in L)e(S,W,{get:L[W],enumerable:!0})};p(r,{Atom:()=>Ma,PointerProxy:()=>Il,Ticker:()=>wa,getPointerParts:()=>Ir,isPointer:()=>Ui,isPrism:()=>vs,iterateAndCountTicks:()=>Pl,iterateOver:()=>Dl,pointer:()=>go,pointerToPrism:()=>xs,prism:()=>Or,val:()=>So});var m=Array.isArray,g=m,x=typeof Ci=="object"&&Ci&&Ci.Object===Object&&Ci,E=x,v=typeof self=="object"&&self&&self.Object===Object&&self,_=E||v||Function("return this")(),A=_,w=A.Symbol,b=w,B=Object.prototype,U=B.hasOwnProperty,O=B.toString,V=b?b.toStringTag:void 0;function I(S){var L=U.call(S,V),W=S[V];try{S[V]=void 0;var oe=!0}catch{}var ct=O.call(S);return oe&&(L?S[V]=W:delete S[V]),ct}var R=I,H=Object.prototype,ee=H.toString;function te(S){return ee.call(S)}var se=te,he="[object Null]",q="[object Undefined]",de=b?b.toStringTag:void 0;function re(S){return S==null?S===void 0?q:he:de&&de in Object(S)?R(S):se(S)}var ge=re;function be(S){return S!=null&&typeof S=="object"}var ze=be,Ge="[object Symbol]";function pt(S){return typeof S=="symbol"||ze(S)&&ge(S)==Ge}var le=pt,me=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,Ue=/^\w*$/;function Se(S,L){if(g(S))return!1;var W=typeof S;return W=="number"||W=="symbol"||W=="boolean"||S==null||le(S)?!0:Ue.test(S)||!me.test(S)||L!=null&&S in Object(L)}var $e=Se;function it(S){var L=typeof S;return S!=null&&(L=="object"||L=="function")}var Je=it,pe="[object AsyncFunction]",ve="[object Function]",Le="[object GeneratorFunction]",G="[object Proxy]";function tt(S){if(!Je(S))return!1;var L=ge(S);return L==ve||L==Le||L==pe||L==G}var Ke=tt,Qe=A["__core-js_shared__"],Oe=Qe,rt=(function(){var S=/[^.]+$/.exec(Oe&&Oe.keys&&Oe.keys.IE_PROTO||"");return S?"Symbol(src)_1."+S:""})();function Fe(S){return!!rt&&rt in S}var F=Fe,T=Function.prototype,Z=T.toString;function ce(S){if(S!=null){try{return Z.call(S)}catch{}try{return S+""}catch{}}return""}var fe=ce,ue=/[\\^$.*+?()[\]{}|]/g,ke=/^\[object .+?Constructor\]$/,we=Function.prototype,Be=Object.prototype,gt=we.toString,_e=Be.hasOwnProperty,He=RegExp("^"+gt.call(_e).replace(ue,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function We(S){if(!Je(S)||F(S))return!1;var L=Ke(S)?He:ke;return L.test(fe(S))}var ot=We;function Ve(S,L){return S==null?void 0:S[L]}var xt=Ve;function dt(S,L){var W=xt(S,L);return ot(W)?W:void 0}var It=dt,X=It(Object,"create"),Ae=X;function P(){this.__data__=Ae?Ae(null):{},this.size=0}var k=P;function $(S){var L=this.has(S)&&delete this.__data__[S];return this.size-=L?1:0,L}var ie=$,Te="__lodash_hash_undefined__",Ee=Object.prototype,De=Ee.hasOwnProperty;function Pe(S){var L=this.__data__;if(Ae){var W=L[S];return W===Te?void 0:W}return De.call(L,S)?L[S]:void 0}var ut=Pe,bt=Object.prototype,Ft=bt.hasOwnProperty;function mt(S){var L=this.__data__;return Ae?L[S]!==void 0:Ft.call(L,S)}var nt=mt,jt="__lodash_hash_undefined__";function Dt(S,L){var W=this.__data__;return this.size+=this.has(S)?0:1,W[S]=Ae&&L===void 0?jt:L,this}var Xt=Dt;function qt(S){var L=-1,W=S==null?0:S.length;for(this.clear();++L<W;){var oe=S[L];this.set(oe[0],oe[1])}}qt.prototype.clear=k,qt.prototype.delete=ie,qt.prototype.get=ut,qt.prototype.has=nt,qt.prototype.set=Xt;var Tt=qt;function nn(){this.__data__=[],this.size=0}var Tn=nn;function Bn(S,L){return S===L||S!==S&&L!==L}var rr=Bn;function Zn(S,L){for(var W=S.length;W--;)if(rr(S[W][0],L))return W;return-1}var ci=Zn,C=Array.prototype,j=C.splice;function J(S){var L=this.__data__,W=ci(L,S);if(W<0)return!1;var oe=L.length-1;return W==oe?L.pop():j.call(L,W,1),--this.size,!0}var ne=J;function Y(S){var L=this.__data__,W=ci(L,S);return W<0?void 0:L[W][1]}var Me=Y;function Ne(S){return ci(this.__data__,S)>-1}var Xe=Ne;function qe(S,L){var W=this.__data__,oe=ci(W,S);return oe<0?(++this.size,W.push([S,L])):W[oe][1]=L,this}var ht=qe;function at(S){var L=-1,W=S==null?0:S.length;for(this.clear();++L<W;){var oe=S[L];this.set(oe[0],oe[1])}}at.prototype.clear=Tn,at.prototype.delete=ne,at.prototype.get=Me,at.prototype.has=Xe,at.prototype.set=ht;var Ye=at,Rt=It(A,"Map"),Ut=Rt;function kt(){this.size=0,this.__data__={hash:new Tt,map:new(Ut||Ye),string:new Tt}}var on=kt;function Pt(S){var L=typeof S;return L=="string"||L=="number"||L=="symbol"||L=="boolean"?S!=="__proto__":S===null}var Ze=Pt;function Qn(S,L){var W=S.__data__;return Ze(L)?W[typeof L=="string"?"string":"hash"]:W.map}var wt=Qn;function wn(S){var L=wt(this,S).delete(S);return this.size-=L?1:0,L}var wi=wn;function un(S){return wt(this,S).get(S)}var Ni=un;function zt(S){return wt(this,S).has(S)}var jn=zt;function Oi(S,L){var W=wt(this,S),oe=W.size;return W.set(S,L),this.size+=W.size==oe?0:1,this}var Dn=Oi;function An(S){var L=-1,W=S==null?0:S.length;for(this.clear();++L<W;){var oe=S[L];this.set(oe[0],oe[1])}}An.prototype.clear=on,An.prototype.delete=wi,An.prototype.get=Ni,An.prototype.has=jn,An.prototype.set=Dn;var Jn=An,fs="Expected a function";function po(S,L){if(typeof S!="function"||L!=null&&typeof L!="function")throw new TypeError(fs);var W=function(){var oe=arguments,ct=L?L.apply(this,oe):oe[0],Lt=W.cache;if(Lt.has(ct))return Lt.get(ct);var Rn=S.apply(this,oe);return W.cache=Lt.set(ct,Rn)||Lt,Rn};return W.cache=new(po.Cache||Jn),W}po.Cache=Jn;var jc=po,sr=500;function ps(S){var L=jc(S,function(oe){return W.size===sr&&W.clear(),oe}),W=L.cache;return L}var Xc=ps,Pr=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,qc=/\\(\\)?/g,Yc=Xc(function(S){var L=[];return S.charCodeAt(0)===46&&L.push(""),S.replace(Pr,function(W,oe,ct,Lt){L.push(ct?Lt.replace(qc,"$1"):oe||W)}),L}),Kc=Yc;function $c(S,L){for(var W=-1,oe=S==null?0:S.length,ct=Array(oe);++W<oe;)ct[W]=L(S[W],W,S);return ct}var Zc=$c,Cr=b?b.prototype:void 0,aa=Cr?Cr.toString:void 0;function ca(S){if(typeof S=="string")return S;if(g(S))return Zc(S,ca)+"";if(le(S))return aa?aa.call(S):"";var L=S+"";return L=="0"&&1/S==-1/0?"-0":L}var Qc=ca;function Jc(S){return S==null?"":Qc(S)}var el=Jc;function tl(S,L){return g(S)?S:$e(S,L)?[S]:Kc(el(S))}var nl=tl;function il(S){if(typeof S=="string"||le(S))return S;var L=S+"";return L=="0"&&1/S==-1/0?"-0":L}var or=il;function ms(S,L){L=nl(L,S);for(var W=0,oe=L.length;S!=null&&W<oe;)S=S[or(L[W++])];return W&&W==oe?S:void 0}var rl=ms;function mo(S,L,W){var oe=S==null?void 0:rl(S,L);return oe===void 0?W:oe}var sl=mo;function ol(S,L){return function(W){return S(L(W))}}var al=ol,cl=al(Object.getPrototypeOf,Object),ll=cl,ul="[object Object]",hl=Function.prototype,dl=Object.prototype,la=hl.toString,fl=dl.hasOwnProperty,ua=la.call(Object);function ha(S){if(!ze(S)||ge(S)!=ul)return!1;var L=ll(S);if(L===null)return!0;var W=fl.call(L,"constructor")&&L.constructor;return typeof W=="function"&&W instanceof W&&la.call(W)==ua}var da=ha;function fa(S){var L=S==null?0:S.length;return L?S[L-1]:void 0}var pl=fa,gs=new WeakMap,pa=new WeakMap,Dr=Symbol("pointerMeta"),ml={get(S,L){if(L===Dr)return gs.get(S);let W=pa.get(S);W||(W=new Map,pa.set(S,W));const oe=W.get(L);if(oe!==void 0)return oe;const ct=gs.get(S),Lt=_s({root:ct.root,path:[...ct.path,L]});return W.set(L,Lt),Lt}},mi=S=>S[Dr],Ir=S=>{const{root:L,path:W}=mi(S);return{root:L,path:W}};function _s(S){var L;const W={root:S.root,path:(L=S.path)!=null?L:[]},oe={};return gs.set(oe,W),new Proxy(oe,ml)}var go=_s,Ui=S=>S&&!!mi(S);function ma(S,L,W){return L.length===0?W(S):ar(S,L,W)}var ar=(S,L,W)=>{if(L.length===0)return W(S);if(Array.isArray(S)){let[oe,...ct]=L;oe=parseInt(String(oe),10),isNaN(oe)&&(oe=0);const Lt=S[oe],Rn=ar(Lt,ct,W);if(Lt===Rn)return S;const li=[...S];return li.splice(oe,1,Rn),li}else if(typeof S=="object"&&S!==null){const[oe,...ct]=L,Lt=S[oe],Rn=ar(Lt,ct,W);return Lt===Rn?S:h(u({},S),{[oe]:Rn})}else{const[oe,...ct]=L;return{[oe]:ar(void 0,ct,W)}}},fn=class{constructor(){this._head=void 0}peek(){return this._head&&this._head.data}pop(){const S=this._head;if(S)return this._head=S.next,S.data}push(S){const L={next:this._head,data:S};this._head=L}};function vs(S){return!!(S&&S.isPrism&&S.isPrism===!0)}function _o(){const S=()=>{},L=new fn,W=S;return{type:"Dataverse_discoveryMechanism",startIgnoringDependencies:()=>{L.push(W)},stopIgnoringDependencies:()=>{L.peek()!==W||L.pop()},reportResolutionStart:cr=>{const Ur=L.peek();Ur&&Ur(cr),L.push(W)},reportResolutionEnd:cr=>{L.pop()},pushCollector:cr=>{L.push(cr)},popCollector:cr=>{if(L.peek()!==cr)throw new Error("Popped collector is not on top of the stack");L.pop()}}}function gl(){const S="__dataverse_discoveryMechanism_sharedStack",L=typeof window<"u"?window:typeof Ci<"u"?Ci:{};if(L){const W=L[S];if(W&&typeof W=="object"&&W.type==="Dataverse_discoveryMechanism")return W;{const oe=_o();return L[S]=oe,oe}}else return _o()}var{startIgnoringDependencies:Bi,stopIgnoringDependencies:Lr,reportResolutionEnd:_l,reportResolutionStart:vl,pushCollector:vo,popCollector:yl}=gl(),ga=()=>{},xl=class{constructor(S,L){this._fn=S,this._prismInstance=L,this._didMarkDependentsAsStale=!1,this._isFresh=!1,this._cacheOfDendencyValues=new Map,this._dependents=new Set,this._dependencies=new Set,this._possiblyStaleDeps=new Set,this._scope=new _a(this),this._lastValue=void 0,this._forciblySetToStale=!1,this._reactToDependencyGoingStale=W=>{this._possiblyStaleDeps.add(W),this._markAsStale()};for(const W of this._dependencies)W._addDependent(this._reactToDependencyGoingStale);Bi(),this.getValue(),Lr()}get hasDependents(){return this._dependents.size>0}removeDependent(S){this._dependents.delete(S)}addDependent(S){this._dependents.add(S)}destroy(){for(const S of this._dependencies)S._removeDependent(this._reactToDependencyGoingStale);va(this._scope)}getValue(){if(!this._isFresh){const S=this._recalculate();this._lastValue=S,this._isFresh=!0,this._didMarkDependentsAsStale=!1,this._forciblySetToStale=!1}return this._lastValue}_recalculate(){let S;if(!this._forciblySetToStale&&this._possiblyStaleDeps.size>0){let oe=!1;Bi();for(const ct of this._possiblyStaleDeps)if(this._cacheOfDendencyValues.get(ct)!==ct.getValue()){oe=!0;break}if(Lr(),this._possiblyStaleDeps.clear(),!oe)return this._lastValue}const L=new Set;this._cacheOfDendencyValues.clear();const W=oe=>{L.add(oe),this._addDependency(oe)};vo(W),xn.push(this._scope);try{S=this._fn()}catch(oe){console.error(oe)}finally{xn.pop()!==this._scope&&console.warn("The Prism hook stack has slipped. This is a bug.")}yl(W);for(const oe of this._dependencies)L.has(oe)||this._removeDependency(oe);this._dependencies=L,Bi();for(const oe of L)this._cacheOfDendencyValues.set(oe,oe.getValue());return Lr(),S}forceStale(){this._forciblySetToStale=!0,this._markAsStale()}_markAsStale(){if(!this._didMarkDependentsAsStale){this._didMarkDependentsAsStale=!0,this._isFresh=!1;for(const S of this._dependents)S(this._prismInstance)}}_addDependency(S){this._dependencies.has(S)||(this._dependencies.add(S),S._addDependent(this._reactToDependencyGoingStale))}_removeDependency(S){this._dependencies.has(S)&&(this._dependencies.delete(S),S._removeDependent(this._reactToDependencyGoingStale))}},yo={},bl=class{constructor(S){this._fn=S,this.isPrism=!0,this._state={hot:!1,handle:void 0}}get isHot(){return this._state.hot}onChange(S,L,W=!1){const oe=()=>{S.onThisOrNextTick(Lt)};let ct=yo;const Lt=()=>{const li=this.getValue();li!==ct&&(ct=li,L(li))};return this._addDependent(oe),W&&(ct=this.getValue(),L(ct)),()=>{this._removeDependent(oe),S.offThisOrNextTick(Lt),S.offNextTick(Lt)}}onStale(S){const L=()=>{this._removeDependent(W)},W=()=>S();return this._addDependent(W),L}keepHot(){return this.onStale(()=>{})}_addDependent(S){this._state.hot||this._goHot(),this._state.handle.addDependent(S)}_goHot(){const S=new xl(this._fn,this);this._state={hot:!0,handle:S}}_removeDependent(S){const L=this._state;if(!L.hot)return;const W=L.handle;W.removeDependent(S),W.hasDependents||(this._state={hot:!1,handle:void 0},W.destroy())}getValue(){vl(this);const S=this._state;let L;return S.hot?L=S.handle.getValue():L=Nr(this._fn),_l(this),L}},_a=class{constructor(S){this._hotHandle=S,this._refs=new Map,this.isPrismScope=!0,this.subs={},this.effects=new Map,this.memos=new Map}ref(S,L){let W=this._refs.get(S);if(W!==void 0)return W;{const oe={current:L};return this._refs.set(S,oe),oe}}effect(S,L,W){let oe=this.effects.get(S);oe===void 0&&(oe={cleanup:ga,deps:void 0},this.effects.set(S,oe)),ya(oe.deps,W)&&(oe.cleanup(),Bi(),oe.cleanup=ys(L,ga).value,Lr(),oe.deps=W)}memo(S,L,W){let oe=this.memos.get(S);return oe===void 0&&(oe={cachedValue:null,deps:void 0},this.memos.set(S,oe)),ya(oe.deps,W)&&(Bi(),oe.cachedValue=ys(L,void 0).value,Lr(),oe.deps=W),oe.cachedValue}state(S,L){const{value:W,setValue:oe}=this.memo("state/"+S,()=>{const ct={current:L};return{value:ct,setValue:Rn=>{ct.current=Rn,this._hotHandle.forceStale()}}},[]);return[W.current,oe]}sub(S){return this.subs[S]||(this.subs[S]=new _a(this._hotHandle)),this.subs[S]}cleanupEffects(){for(const S of this.effects.values())ys(S.cleanup,void 0);this.effects.clear()}source(S,L){return this.effect("$$source/blah",()=>S(()=>{this._hotHandle.forceStale()}),[S]),L()}};function va(S){for(const L of Object.values(S.subs))va(L);S.cleanupEffects()}function ys(S,L){try{return{value:S(),ok:!0}}catch(W){return setTimeout(function(){throw W}),{value:L,ok:!1}}}var xn=new fn;function Sl(S,L){const W=xn.peek();if(!W)throw new Error("prism.ref() is called outside of a prism() call.");return W.ref(S,L)}function xo(S,L,W){const oe=xn.peek();if(!oe)throw new Error("prism.effect() is called outside of a prism() call.");return oe.effect(S,L,W)}function ya(S,L){if(S===void 0||L===void 0)return!0;const W=S.length;if(W!==L.length)return!0;for(let oe=0;oe<W;oe++)if(S[oe]!==L[oe])return!0;return!1}function xa(S,L,W){const oe=xn.peek();if(!oe)throw new Error("prism.memo() is called outside of a prism() call.");return oe.memo(S,L,W)}function kn(S,L){const W=xn.peek();if(!W)throw new Error("prism.state() is called outside of a prism() call.");return W.state(S,L)}function El(){if(!xn.peek())throw new Error("The parent function is called outside of a prism() call.")}function Ml(S,L){const W=xn.peek();if(!W)throw new Error("prism.scope() is called outside of a prism() call.");const oe=W.sub(S);xn.push(oe);const ct=ys(L,void 0).value;return xn.pop(),ct}function Tl(S,L,W){return xa(S,()=>pn(L),W).getValue()}function ba(){return!!xn.peek()}function wl(S,L){const W=xn.peek();if(!W)throw new Error("prism.source() is called outside of a prism() call.");return W.source(S,L)}var pn=S=>new bl(S),Fr=class{effect(S,L,W){console.warn("prism.effect() does not run in cold prisms")}memo(S,L,W){return L()}state(S,L){return[L,()=>{}]}ref(S,L){return{current:L}}sub(S){return new Fr}source(S,L){return L()}};function Nr(S){const L=new Fr;xn.push(L);let W;try{W=S()}catch(oe){console.error(oe)}finally{xn.pop()!==L&&console.warn("The Prism hook stack has slipped. This is a bug.")}return W}pn.ref=Sl,pn.effect=xo,pn.memo=xa,pn.ensurePrism=El,pn.state=kn,pn.scope=Ml,pn.sub=Tl,pn.inPrism=ba,pn.source=wl;var Or=pn,Sa;(function(S){S[S.Dict=0]="Dict",S[S.Array=1]="Array",S[S.Other=2]="Other"})(Sa||(Sa={}));var Ht=S=>Array.isArray(S)?1:da(S)?0:2,bo=(S,L,W=Ht(S))=>W===0&&typeof L=="string"||W===1&&Al(L)?S[L]:void 0,Al=S=>{const L=typeof S=="number"?S:parseInt(S,10);return!isNaN(L)&&L>=0&&L<1/0&&(L|0)===L},Ea=class{constructor(S,L){this._parent=S,this._path=L,this.children=new Map,this.identityChangeListeners=new Set}addIdentityChangeListener(S){this.identityChangeListeners.add(S)}removeIdentityChangeListener(S){this.identityChangeListeners.delete(S),this._checkForGC()}removeChild(S){this.children.delete(S),this._checkForGC()}getChild(S){return this.children.get(S)}getOrCreateChild(S){let L=this.children.get(S);return L||(L=L=new Ea(this,this._path.concat([S])),this.children.set(S,L)),L}_checkForGC(){this.identityChangeListeners.size>0||this.children.size>0||this._parent&&this._parent.removeChild(pl(this._path))}},Ma=class{constructor(S){this.$$isPointerToPrismProvider=!0,this.pointer=go({root:this,path:[]}),this.prism=this.pointerToPrism(this.pointer),this._onPointerValueChange=(L,W)=>{const{path:oe}=Ir(L),ct=this._getOrCreateScopeForPath(oe);return ct.identityChangeListeners.add(W),()=>{ct.identityChangeListeners.delete(W)}},this._currentState=S,this._rootScope=new Ea(void 0,[])}set(S){const L=this._currentState;this._currentState=S,this._checkUpdates(this._rootScope,L,S)}get(){return this._currentState}getByPointer(S){const L=Ui(S)?S:S(this.pointer),W=Ir(L).path;return this._getIn(W)}_getIn(S){return S.length===0?this.get():sl(this.get(),S)}reduce(S){this.set(S(this.get()))}reduceByPointer(S,L){const W=Ui(S)?S:S(this.pointer),oe=Ir(W).path,ct=ma(this.get(),oe,L);this.set(ct)}setByPointer(S,L){this.reduceByPointer(S,()=>L)}_checkUpdates(S,L,W){if(L===W)return;for(const Lt of S.identityChangeListeners)Lt(W);if(S.children.size===0)return;const oe=Ht(L),ct=Ht(W);if(!(oe===2&&oe===ct))for(const[Lt,Rn]of S.children){const li=bo(L,Lt,oe),Aa=bo(W,Lt,ct);this._checkUpdates(Rn,li,Aa)}}_getOrCreateScopeForPath(S){let L=this._rootScope;for(const W of S)L=L.getOrCreateChild(W);return L}pointerToPrism(S){const{path:L}=Ir(S),W=ct=>this._onPointerValueChange(S,ct),oe=()=>this._getIn(L);return Or(()=>Or.source(W,oe))}},Ta=new WeakMap;function Rl(S){return typeof S=="object"&&S!==null&&S.$$isPointerToPrismProvider===!0}var xs=S=>{const L=mi(S);let W=Ta.get(L);if(!W){const oe=L.root;if(!Rl(oe))throw new Error("Cannot run pointerToPrism() on a pointer whose root is not an PointerToPrismProvider");W=oe.pointerToPrism(S),Ta.set(L,W)}return W},So=S=>Ui(S)?xs(S).getValue():vs(S)?S.getValue():S;function*Pl(S){let L;if(Ui(S))L=xs(S);else if(vs(S))L=S;else throw new Error("Only pointers and prisms are supported");let W=0;const oe=L.onStale(()=>{W++});try{for(;;){const ct=W;W=0,yield{value:L.getValue(),ticks:ct}}}finally{oe()}}var Cl=180,wa=class{constructor(S){this._conf=S,this._ticking=!1,this._dormant=!0,this._numberOfDormantTicks=0,this.__ticks=0,this._scheduledForThisOrNextTick=new Set,this._scheduledForNextTick=new Set,this._timeAtCurrentTick=0}get dormant(){return this._dormant}onThisOrNextTick(S){this._scheduledForThisOrNextTick.add(S),this._dormant&&this._goActive()}onNextTick(S){this._scheduledForNextTick.add(S),this._dormant&&this._goActive()}offThisOrNextTick(S){this._scheduledForThisOrNextTick.delete(S)}offNextTick(S){this._scheduledForNextTick.delete(S)}get time(){return this._ticking?this._timeAtCurrentTick:performance.now()}_goActive(){var S,L;this._dormant&&(this._dormant=!1,(L=(S=this._conf)==null?void 0:S.onActive)==null||L.call(S))}_goDormant(){var S,L;this._dormant||(this._dormant=!0,this._numberOfDormantTicks=0,(L=(S=this._conf)==null?void 0:S.onDormant)==null||L.call(S))}tick(S=performance.now()){if(this.__ticks++,!this._dormant&&this._scheduledForNextTick.size===0&&this._scheduledForThisOrNextTick.size===0&&(this._numberOfDormantTicks++,this._numberOfDormantTicks>=Cl)){this._goDormant();return}this._ticking=!0,this._timeAtCurrentTick=S;for(const L of this._scheduledForNextTick)this._scheduledForThisOrNextTick.add(L);this._scheduledForNextTick.clear(),this._tick(0),this._ticking=!1}_tick(S){const L=this.time;if(S>10&&console.warn("_tick() recursing for 10 times"),S>100)throw new Error("Maximum recursion limit for _tick()");const W=this._scheduledForThisOrNextTick;this._scheduledForThisOrNextTick=new Set;for(const oe of W)oe(L);if(this._scheduledForThisOrNextTick.size>0)return this._tick(S+1)}};function*Dl(S){let L;if(Ui(S))L=xs(S);else if(vs(S))L=S;else throw new Error("Only pointers and prisms are supported");const W=new wa,oe=L.onChange(W,ct=>{});try{for(;;)W.tick(),yield L.getValue()}finally{oe()}}var Il=class{constructor(S){this.$$isPointerToPrismProvider=!0,this._currentPointerBox=new Ma(S),this.pointer=go({root:this,path:[]})}setPointer(S){this._currentPointerBox.set(S)}pointerToPrism(S){const{path:L}=mi(S);return Or(()=>{const W=this._currentPointerBox.prism.getValue(),oe=L.reduce((ct,Lt)=>ct[Lt],W);return So(oe)})}}})(ih)),ih}const Ym={type:"change"},Dd={type:"start"},i_={type:"end"},yc=new co,Km=new yr,fC=Math.cos(70*Ag.DEG2RAD),gn=new N,Yn=2*Math.PI,Wt={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},rh=1e-6;class pC extends t_{constructor(e,t=null){super(e,t),this.state=Wt.NONE,this.enabled=!0,this.target=new N,this.cursor=new N,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:Xs.ROTATE,MIDDLE:Xs.DOLLY,RIGHT:Xs.PAN},this.touches={ONE:Hs.ROTATE,TWO:Hs.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._domElementKeyEvents=null,this._lastPosition=new N,this._lastQuaternion=new Et,this._lastTargetPosition=new N,this._quat=new Et().setFromUnitVectors(e.up,new N(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new Xm,this._sphericalDelta=new Xm,this._scale=1,this._panOffset=new N,this._rotateStart=new lt,this._rotateEnd=new lt,this._rotateDelta=new lt,this._panStart=new lt,this._panEnd=new lt,this._panDelta=new lt,this._dollyStart=new lt,this._dollyEnd=new lt,this._dollyDelta=new lt,this._dollyDirection=new N,this._mouse=new lt,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=gC.bind(this),this._onPointerDown=mC.bind(this),this._onPointerUp=_C.bind(this),this._onContextMenu=MC.bind(this),this._onMouseWheel=xC.bind(this),this._onKeyDown=bC.bind(this),this._onTouchStart=SC.bind(this),this._onTouchMove=EC.bind(this),this._onMouseDown=vC.bind(this),this._onMouseMove=yC.bind(this),this._interceptControlDown=TC.bind(this),this._interceptControlUp=wC.bind(this),this.domElement!==null&&this.connect(),this.update()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointercancel",this._onPointerUp),this.domElement.addEventListener("contextmenu",this._onContextMenu),this.domElement.addEventListener("wheel",this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener("keydown",this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.removeEventListener("pointercancel",this._onPointerUp),this.domElement.removeEventListener("wheel",this._onMouseWheel),this.domElement.removeEventListener("contextmenu",this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener("keydown",this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction="auto"}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(e){e.addEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=e}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(Ym),this.update(),this.state=Wt.NONE}update(e=null){const t=this.object.position;gn.copy(t).sub(this.target),gn.applyQuaternion(this._quat),this._spherical.setFromVector3(gn),this.autoRotate&&this.state===Wt.NONE&&this._rotateLeft(this._getAutoRotationAngle(e)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let n=this.minAzimuthAngle,i=this.maxAzimuthAngle;isFinite(n)&&isFinite(i)&&(n<-Math.PI?n+=Yn:n>Math.PI&&(n-=Yn),i<-Math.PI?i+=Yn:i>Math.PI&&(i-=Yn),n<=i?this._spherical.theta=Math.max(n,Math.min(i,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(n+i)/2?Math.max(n,this._spherical.theta):Math.min(i,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let s=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{const a=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),s=a!=this._spherical.radius}if(gn.setFromSpherical(this._spherical),gn.applyQuaternion(this._quatInverse),t.copy(this.target).add(gn),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let a=null;if(this.object.isPerspectiveCamera){const c=gn.length();a=this._clampDistance(c*this._scale);const u=c-a;this.object.position.addScaledVector(this._dollyDirection,u),this.object.updateMatrixWorld(),s=!!u}else if(this.object.isOrthographicCamera){const c=new N(this._mouse.x,this._mouse.y,0);c.unproject(this.object);const u=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),s=u!==this.object.zoom;const h=new N(this._mouse.x,this._mouse.y,0);h.unproject(this.object),this.object.position.sub(h).add(c),this.object.updateMatrixWorld(),a=gn.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),this.zoomToCursor=!1;a!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(a).add(this.object.position):(yc.origin.copy(this.object.position),yc.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(yc.direction))<fC?this.object.lookAt(this.target):(Km.setFromNormalAndCoplanarPoint(this.object.up,this.target),yc.intersectPlane(Km,this.target))))}else if(this.object.isOrthographicCamera){const a=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),a!==this.object.zoom&&(this.object.updateProjectionMatrix(),s=!0)}return this._scale=1,this._performCursorZoom=!1,s||this._lastPosition.distanceToSquared(this.object.position)>rh||8*(1-this._lastQuaternion.dot(this.object.quaternion))>rh||this._lastTargetPosition.distanceToSquared(this.target)>rh?(this.dispatchEvent(Ym),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(e){return e!==null?Yn/60*this.autoRotateSpeed*e:Yn/60/60*this.autoRotateSpeed}_getZoomScale(e){const t=Math.abs(e*.01);return Math.pow(.95,this.zoomSpeed*t)}_rotateLeft(e){this._sphericalDelta.theta-=e}_rotateUp(e){this._sphericalDelta.phi-=e}_panLeft(e,t){gn.setFromMatrixColumn(t,0),gn.multiplyScalar(-e),this._panOffset.add(gn)}_panUp(e,t){this.screenSpacePanning===!0?gn.setFromMatrixColumn(t,1):(gn.setFromMatrixColumn(t,0),gn.crossVectors(this.object.up,gn)),gn.multiplyScalar(e),this._panOffset.add(gn)}_pan(e,t){const n=this.domElement;if(this.object.isPerspectiveCamera){const i=this.object.position;gn.copy(i).sub(this.target);let s=gn.length();s*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*e*s/n.clientHeight,this.object.matrix),this._panUp(2*t*s/n.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(e*(this.object.right-this.object.left)/this.object.zoom/n.clientWidth,this.object.matrix),this._panUp(t*(this.object.top-this.object.bottom)/this.object.zoom/n.clientHeight,this.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),this.enablePan=!1)}_dollyOut(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_dollyIn(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_updateZoomParameters(e,t){if(!this.zoomToCursor)return;this._performCursorZoom=!0;const n=this.domElement.getBoundingClientRect(),i=e-n.left,s=t-n.top,a=n.width,c=n.height;this._mouse.x=i/a*2-1,this._mouse.y=-(s/c)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(e){return Math.max(this.minDistance,Math.min(this.maxDistance,e))}_handleMouseDownRotate(e){this._rotateStart.set(e.clientX,e.clientY)}_handleMouseDownDolly(e){this._updateZoomParameters(e.clientX,e.clientX),this._dollyStart.set(e.clientX,e.clientY)}_handleMouseDownPan(e){this._panStart.set(e.clientX,e.clientY)}_handleMouseMoveRotate(e){this._rotateEnd.set(e.clientX,e.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Yn*this._rotateDelta.x/t.clientHeight),this._rotateUp(Yn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(e){this._dollyEnd.set(e.clientX,e.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(e){this._panEnd.set(e.clientX,e.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(e){this._updateZoomParameters(e.clientX,e.clientY),e.deltaY<0?this._dollyIn(this._getZoomScale(e.deltaY)):e.deltaY>0&&this._dollyOut(this._getZoomScale(e.deltaY)),this.update()}_handleKeyDown(e){let t=!1;switch(e.code){case this.keys.UP:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(Yn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,this.keyPanSpeed),t=!0;break;case this.keys.BOTTOM:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(-Yn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,-this.keyPanSpeed),t=!0;break;case this.keys.LEFT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(Yn*this.rotateSpeed/this.domElement.clientHeight):this._pan(this.keyPanSpeed,0),t=!0;break;case this.keys.RIGHT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(-Yn*this.rotateSpeed/this.domElement.clientHeight):this._pan(-this.keyPanSpeed,0),t=!0;break}t&&(e.preventDefault(),this.update())}_handleTouchStartRotate(e){if(this._pointers.length===1)this._rotateStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._rotateStart.set(n,i)}}_handleTouchStartPan(e){if(this._pointers.length===1)this._panStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panStart.set(n,i)}}_handleTouchStartDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyStart.set(0,s)}_handleTouchStartDollyPan(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enablePan&&this._handleTouchStartPan(e)}_handleTouchStartDollyRotate(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enableRotate&&this._handleTouchStartRotate(e)}_handleTouchMoveRotate(e){if(this._pointers.length==1)this._rotateEnd.set(e.pageX,e.pageY);else{const n=this._getSecondPointerPosition(e),i=.5*(e.pageX+n.x),s=.5*(e.pageY+n.y);this._rotateEnd.set(i,s)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Yn*this._rotateDelta.x/t.clientHeight),this._rotateUp(Yn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(e){if(this._pointers.length===1)this._panEnd.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panEnd.set(n,i)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyEnd.set(0,s),this._dollyDelta.set(0,Math.pow(this._dollyEnd.y/this._dollyStart.y,this.zoomSpeed)),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);const a=(e.pageX+t.x)*.5,c=(e.pageY+t.y)*.5;this._updateZoomParameters(a,c)}_handleTouchMoveDollyPan(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enablePan&&this._handleTouchMovePan(e)}_handleTouchMoveDollyRotate(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enableRotate&&this._handleTouchMoveRotate(e)}_addPointer(e){this._pointers.push(e.pointerId)}_removePointer(e){delete this._pointerPositions[e.pointerId];for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId){this._pointers.splice(t,1);return}}_isTrackingPointer(e){for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId)return!0;return!1}_trackPointer(e){let t=this._pointerPositions[e.pointerId];t===void 0&&(t=new lt,this._pointerPositions[e.pointerId]=t),t.set(e.pageX,e.pageY)}_getSecondPointerPosition(e){const t=e.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[t]}_customWheelEvent(e){const t=e.deltaMode,n={clientX:e.clientX,clientY:e.clientY,deltaY:e.deltaY};switch(t){case 1:n.deltaY*=16;break;case 2:n.deltaY*=100;break}return e.ctrlKey&&!this._controlActive&&(n.deltaY*=10),n}}function mC(r){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.domElement.addEventListener("pointerup",this._onPointerUp)),!this._isTrackingPointer(r)&&(this._addPointer(r),r.pointerType==="touch"?this._onTouchStart(r):this._onMouseDown(r)))}function gC(r){this.enabled!==!1&&(r.pointerType==="touch"?this._onTouchMove(r):this._onMouseMove(r))}function _C(r){switch(this._removePointer(r),this._pointers.length){case 0:this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.dispatchEvent(i_),this.state=Wt.NONE;break;case 1:const e=this._pointers[0],t=this._pointerPositions[e];this._onTouchStart({pointerId:e,pageX:t.x,pageY:t.y});break}}function vC(r){let e;switch(r.button){case 0:e=this.mouseButtons.LEFT;break;case 1:e=this.mouseButtons.MIDDLE;break;case 2:e=this.mouseButtons.RIGHT;break;default:e=-1}switch(e){case Xs.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(r),this.state=Wt.DOLLY;break;case Xs.ROTATE:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Wt.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Wt.ROTATE}break;case Xs.PAN:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Wt.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Wt.PAN}break;default:this.state=Wt.NONE}this.state!==Wt.NONE&&this.dispatchEvent(Dd)}function yC(r){switch(this.state){case Wt.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(r);break;case Wt.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(r);break;case Wt.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(r);break}}function xC(r){this.enabled===!1||this.enableZoom===!1||this.state!==Wt.NONE||(r.preventDefault(),this.dispatchEvent(Dd),this._handleMouseWheel(this._customWheelEvent(r)),this.dispatchEvent(i_))}function bC(r){this.enabled===!1||this.enablePan===!1||this._handleKeyDown(r)}function SC(r){switch(this._trackPointer(r),this._pointers.length){case 1:switch(this.touches.ONE){case Hs.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(r),this.state=Wt.TOUCH_ROTATE;break;case Hs.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(r),this.state=Wt.TOUCH_PAN;break;default:this.state=Wt.NONE}break;case 2:switch(this.touches.TWO){case Hs.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(r),this.state=Wt.TOUCH_DOLLY_PAN;break;case Hs.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(r),this.state=Wt.TOUCH_DOLLY_ROTATE;break;default:this.state=Wt.NONE}break;default:this.state=Wt.NONE}this.state!==Wt.NONE&&this.dispatchEvent(Dd)}function EC(r){switch(this._trackPointer(r),this.state){case Wt.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(r),this.update();break;case Wt.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(r),this.update();break;case Wt.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(r),this.update();break;case Wt.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(r),this.update();break;default:this.state=Wt.NONE}}function MC(r){this.enabled!==!1&&r.preventDefault()}function TC(r){r.key==="Control"&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}function wC(r){r.key==="Control"&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}const ns=new Qg,Un=new N,_r=new N,sn=new Et,$m={X:new N(1,0,0),Y:new N(0,1,0),Z:new N(0,0,1)},sh={type:"change"},Zm={type:"mouseDown",mode:null},Qm={type:"mouseUp",mode:null},Jm={type:"objectChange"};class AC extends t_{constructor(e,t=null){super(void 0,t);const n=new LC(this);this._root=n;const i=new FC;this._gizmo=i,n.add(i);const s=new NC;this._plane=s,n.add(s);const a=this;function c(w,b){let B=b;Object.defineProperty(a,w,{get:function(){return B!==void 0?B:b},set:function(U){B!==U&&(B=U,s[w]=U,i[w]=U,a.dispatchEvent({type:w+"-changed",value:U}),a.dispatchEvent(sh))}}),a[w]=b,s[w]=b,i[w]=b}c("camera",e),c("object",void 0),c("enabled",!0),c("axis",null),c("mode","translate"),c("translationSnap",null),c("rotationSnap",null),c("scaleSnap",null),c("space","world"),c("size",1),c("dragging",!1),c("showX",!0),c("showY",!0),c("showZ",!0),c("minX",-1/0),c("maxX",1/0),c("minY",-1/0),c("maxY",1/0),c("minZ",-1/0),c("maxZ",1/0);const u=new N,h=new N,f=new Et,p=new Et,m=new N,g=new Et,x=new N,E=new N,v=new N,_=0,A=new N;c("worldPosition",u),c("worldPositionStart",h),c("worldQuaternion",f),c("worldQuaternionStart",p),c("cameraPosition",m),c("cameraQuaternion",g),c("pointStart",x),c("pointEnd",E),c("rotationAxis",v),c("rotationAngle",_),c("eye",A),this._offset=new N,this._startNorm=new N,this._endNorm=new N,this._cameraScale=new N,this._parentPosition=new N,this._parentQuaternion=new Et,this._parentQuaternionInv=new Et,this._parentScale=new N,this._worldScaleStart=new N,this._worldQuaternionInv=new Et,this._worldScale=new N,this._positionStart=new N,this._quaternionStart=new Et,this._scaleStart=new N,this._getPointer=RC.bind(this),this._onPointerDown=CC.bind(this),this._onPointerHover=PC.bind(this),this._onPointerMove=DC.bind(this),this._onPointerUp=IC.bind(this),t!==null&&this.connect()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointermove",this._onPointerHover),this.domElement.addEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerHover),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="auto"}getHelper(){return this._root}pointerHover(e){if(this.object===void 0||this.dragging===!0)return;e!==null&&ns.setFromCamera(e,this.camera);const t=oh(this._gizmo.picker[this.mode],ns);t?this.axis=t.object.name:this.axis=null}pointerDown(e){if(!(this.object===void 0||this.dragging===!0||e!=null&&e.button!==0)&&this.axis!==null){e!==null&&ns.setFromCamera(e,this.camera);const t=oh(this._plane,ns,!0);t&&(this.object.updateMatrixWorld(),this.object.parent.updateMatrixWorld(),this._positionStart.copy(this.object.position),this._quaternionStart.copy(this.object.quaternion),this._scaleStart.copy(this.object.scale),this.object.matrixWorld.decompose(this.worldPositionStart,this.worldQuaternionStart,this._worldScaleStart),this.pointStart.copy(t.point).sub(this.worldPositionStart)),this.dragging=!0,Zm.mode=this.mode,this.dispatchEvent(Zm)}}pointerMove(e){const t=this.axis,n=this.mode,i=this.object;let s=this.space;if(n==="scale"?s="local":(t==="E"||t==="XYZE"||t==="XYZ")&&(s="world"),i===void 0||t===null||this.dragging===!1||e!==null&&e.button!==-1)return;e!==null&&ns.setFromCamera(e,this.camera);const a=oh(this._plane,ns,!0);if(a){if(this.pointEnd.copy(a.point).sub(this.worldPositionStart),n==="translate")this._offset.copy(this.pointEnd).sub(this.pointStart),s==="local"&&t!=="XYZ"&&this._offset.applyQuaternion(this._worldQuaternionInv),t.indexOf("X")===-1&&(this._offset.x=0),t.indexOf("Y")===-1&&(this._offset.y=0),t.indexOf("Z")===-1&&(this._offset.z=0),s==="local"&&t!=="XYZ"?this._offset.applyQuaternion(this._quaternionStart).divide(this._parentScale):this._offset.applyQuaternion(this._parentQuaternionInv).divide(this._parentScale),i.position.copy(this._offset).add(this._positionStart),this.translationSnap&&(s==="local"&&(i.position.applyQuaternion(sn.copy(this._quaternionStart).invert()),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.position.applyQuaternion(this._quaternionStart)),s==="world"&&(i.parent&&i.position.add(Un.setFromMatrixPosition(i.parent.matrixWorld)),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.parent&&i.position.sub(Un.setFromMatrixPosition(i.parent.matrixWorld)))),i.position.x=Math.max(this.minX,Math.min(this.maxX,i.position.x)),i.position.y=Math.max(this.minY,Math.min(this.maxY,i.position.y)),i.position.z=Math.max(this.minZ,Math.min(this.maxZ,i.position.z));else if(n==="scale"){if(t.search("XYZ")!==-1){let c=this.pointEnd.length()/this.pointStart.length();this.pointEnd.dot(this.pointStart)<0&&(c*=-1),_r.set(c,c,c)}else Un.copy(this.pointStart),_r.copy(this.pointEnd),Un.applyQuaternion(this._worldQuaternionInv),_r.applyQuaternion(this._worldQuaternionInv),_r.divide(Un),t.search("X")===-1&&(_r.x=1),t.search("Y")===-1&&(_r.y=1),t.search("Z")===-1&&(_r.z=1);i.scale.copy(this._scaleStart).multiply(_r),this.scaleSnap&&(t.search("X")!==-1&&(i.scale.x=Math.round(i.scale.x/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Y")!==-1&&(i.scale.y=Math.round(i.scale.y/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Z")!==-1&&(i.scale.z=Math.round(i.scale.z/this.scaleSnap)*this.scaleSnap||this.scaleSnap))}else if(n==="rotate"){this._offset.copy(this.pointEnd).sub(this.pointStart);const c=20/this.worldPosition.distanceTo(Un.setFromMatrixPosition(this.camera.matrixWorld));let u=!1;t==="XYZE"?(this.rotationAxis.copy(this._offset).cross(this.eye).normalize(),this.rotationAngle=this._offset.dot(Un.copy(this.rotationAxis).cross(this.eye))*c):(t==="X"||t==="Y"||t==="Z")&&(this.rotationAxis.copy($m[t]),Un.copy($m[t]),s==="local"&&Un.applyQuaternion(this.worldQuaternion),Un.cross(this.eye),Un.length()===0?u=!0:this.rotationAngle=this._offset.dot(Un.normalize())*c),(t==="E"||u)&&(this.rotationAxis.copy(this.eye),this.rotationAngle=this.pointEnd.angleTo(this.pointStart),this._startNorm.copy(this.pointStart).normalize(),this._endNorm.copy(this.pointEnd).normalize(),this.rotationAngle*=this._endNorm.cross(this._startNorm).dot(this.eye)<0?1:-1),this.rotationSnap&&(this.rotationAngle=Math.round(this.rotationAngle/this.rotationSnap)*this.rotationSnap),s==="local"&&t!=="E"&&t!=="XYZE"?(i.quaternion.copy(this._quaternionStart),i.quaternion.multiply(sn.setFromAxisAngle(this.rotationAxis,this.rotationAngle)).normalize()):(this.rotationAxis.applyQuaternion(this._parentQuaternionInv),i.quaternion.copy(sn.setFromAxisAngle(this.rotationAxis,this.rotationAngle)),i.quaternion.multiply(this._quaternionStart).normalize())}this.dispatchEvent(sh),this.dispatchEvent(Jm)}}pointerUp(e){e!==null&&e.button!==0||(this.dragging&&this.axis!==null&&(Qm.mode=this.mode,this.dispatchEvent(Qm)),this.dragging=!1,this.axis=null)}dispose(){this.disconnect(),this._root.dispose()}attach(e){return this.object=e,this._root.visible=!0,this}detach(){return this.object=void 0,this.axis=null,this._root.visible=!1,this}reset(){this.enabled&&this.dragging&&(this.object.position.copy(this._positionStart),this.object.quaternion.copy(this._quaternionStart),this.object.scale.copy(this._scaleStart),this.dispatchEvent(sh),this.dispatchEvent(Jm),this.pointStart.copy(this.pointEnd))}getRaycaster(){return ns}getMode(){return this.mode}setMode(e){this.mode=e}setTranslationSnap(e){this.translationSnap=e}setRotationSnap(e){this.rotationSnap=e}setScaleSnap(e){this.scaleSnap=e}setSize(e){this.size=e}setSpace(e){this.space=e}}function RC(r){if(this.domElement.ownerDocument.pointerLockElement)return{x:0,y:0,button:r.button};{const e=this.domElement.getBoundingClientRect();return{x:(r.clientX-e.left)/e.width*2-1,y:-(r.clientY-e.top)/e.height*2+1,button:r.button}}}function PC(r){if(this.enabled)switch(r.pointerType){case"mouse":case"pen":this.pointerHover(this._getPointer(r));break}}function CC(r){this.enabled&&(document.pointerLockElement||this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.pointerHover(this._getPointer(r)),this.pointerDown(this._getPointer(r)))}function DC(r){this.enabled&&this.pointerMove(this._getPointer(r))}function IC(r){this.enabled&&(this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.pointerUp(this._getPointer(r)))}function oh(r,e,t){const n=e.intersectObject(r,!0);for(let i=0;i<n.length;i++)if(n[i].object.visible||t)return n[i];return!1}const xc=new Ti,Kt=new N(0,1,0),eg=new N(0,0,0),tg=new ft,bc=new Et,Ic=new Et,Ri=new N,ng=new ft,qo=new N(1,0,0),ss=new N(0,1,0),Yo=new N(0,0,1),Sc=new N,Ho=new N,Vo=new N;class LC extends tn{constructor(e){super(),this.isTransformControlsRoot=!0,this.controls=e,this.visible=!1}updateMatrixWorld(e){const t=this.controls;t.object!==void 0&&(t.object.updateMatrixWorld(),t.object.parent===null?console.error("TransformControls: The attached 3D object must be a part of the scene graph."):t.object.parent.matrixWorld.decompose(t._parentPosition,t._parentQuaternion,t._parentScale),t.object.matrixWorld.decompose(t.worldPosition,t.worldQuaternion,t._worldScale),t._parentQuaternionInv.copy(t._parentQuaternion).invert(),t._worldQuaternionInv.copy(t.worldQuaternion).invert()),t.camera.updateMatrixWorld(),t.camera.matrixWorld.decompose(t.cameraPosition,t.cameraQuaternion,t._cameraScale),t.camera.isOrthographicCamera?t.camera.getWorldDirection(t.eye).negate():t.eye.copy(t.cameraPosition).sub(t.worldPosition).normalize(),super.updateMatrixWorld(e)}dispose(){this.traverse(function(e){e.geometry&&e.geometry.dispose(),e.material&&e.material.dispose()})}}class FC extends tn{constructor(){super(),this.isTransformControlsGizmo=!0,this.type="TransformControlsGizmo";const e=new pi({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),t=new Gc({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),n=e.clone();n.opacity=.15;const i=t.clone();i.opacity=.5;const s=e.clone();s.color.setHex(16711680);const a=e.clone();a.color.setHex(65280);const c=e.clone();c.color.setHex(255);const u=e.clone();u.color.setHex(16711680),u.opacity=.5;const h=e.clone();h.color.setHex(65280),h.opacity=.5;const f=e.clone();f.color.setHex(255),f.opacity=.5;const p=e.clone();p.opacity=.25;const m=e.clone();m.color.setHex(16776960),m.opacity=.25,e.clone().color.setHex(16776960);const x=e.clone();x.color.setHex(7895160);const E=new Pn(0,.04,.1,12);E.translate(0,.05,0);const v=new an(.08,.08,.08);v.translate(0,.04,0);const _=new _n;_.setAttribute("position",new $t([0,0,0,1,0,0],3));const A=new Pn(.0075,.0075,.5,3);A.translate(0,.25,0);function w(he,q){const de=new cs(he,.0075,3,64,q*Math.PI*2);return de.rotateY(Math.PI/2),de.rotateX(Math.PI/2),de}function b(){const he=new _n;return he.setAttribute("position",new $t([0,0,0,1,1,1],3)),he}const B={X:[[new Re(E,s),[.5,0,0],[0,0,-Math.PI/2]],[new Re(E,s),[-.5,0,0],[0,0,Math.PI/2]],[new Re(A,s),[0,0,0],[0,0,-Math.PI/2]]],Y:[[new Re(E,a),[0,.5,0]],[new Re(E,a),[0,-.5,0],[Math.PI,0,0]],[new Re(A,a)]],Z:[[new Re(E,c),[0,0,.5],[Math.PI/2,0,0]],[new Re(E,c),[0,0,-.5],[-Math.PI/2,0,0]],[new Re(A,c),null,[Math.PI/2,0,0]]],XYZ:[[new Re(new js(.1,0),p.clone()),[0,0,0]]],XY:[[new Re(new an(.15,.15,.01),f.clone()),[.15,.15,0]]],YZ:[[new Re(new an(.15,.15,.01),u.clone()),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Re(new an(.15,.15,.01),h.clone()),[.15,0,.15],[-Math.PI/2,0,0]]]},U={X:[[new Re(new Pn(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Re(new Pn(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Re(new Pn(.2,0,.6,4),n),[0,.3,0]],[new Re(new Pn(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Re(new Pn(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Re(new Pn(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XYZ:[[new Re(new js(.2,0),n)]],XY:[[new Re(new an(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Re(new an(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Re(new an(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]]},O={START:[[new Re(new js(.01,2),i),null,null,null,"helper"]],END:[[new Re(new js(.01,2),i),null,null,null,"helper"]],DELTA:[[new yi(b(),i),null,null,null,"helper"]],X:[[new yi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new yi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new yi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]},V={XYZE:[[new Re(w(.5,1),x),null,[0,Math.PI/2,0]]],X:[[new Re(w(.5,.5),s)]],Y:[[new Re(w(.5,.5),a),null,[0,0,-Math.PI/2]]],Z:[[new Re(w(.5,.5),c),null,[0,Math.PI/2,0]]],E:[[new Re(w(.75,1),m),null,[0,Math.PI/2,0]]]},I={AXIS:[[new yi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]]},R={XYZE:[[new Re(new sa(.25,10,8),n)]],X:[[new Re(new cs(.5,.1,4,24),n),[0,0,0],[0,-Math.PI/2,-Math.PI/2]]],Y:[[new Re(new cs(.5,.1,4,24),n),[0,0,0],[Math.PI/2,0,0]]],Z:[[new Re(new cs(.5,.1,4,24),n),[0,0,0],[0,0,-Math.PI/2]]],E:[[new Re(new cs(.75,.1,2,24),n)]]},H={X:[[new Re(v,s),[.5,0,0],[0,0,-Math.PI/2]],[new Re(A,s),[0,0,0],[0,0,-Math.PI/2]],[new Re(v,s),[-.5,0,0],[0,0,Math.PI/2]]],Y:[[new Re(v,a),[0,.5,0]],[new Re(A,a)],[new Re(v,a),[0,-.5,0],[0,0,Math.PI]]],Z:[[new Re(v,c),[0,0,.5],[Math.PI/2,0,0]],[new Re(A,c),[0,0,0],[Math.PI/2,0,0]],[new Re(v,c),[0,0,-.5],[-Math.PI/2,0,0]]],XY:[[new Re(new an(.15,.15,.01),f),[.15,.15,0]]],YZ:[[new Re(new an(.15,.15,.01),u),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Re(new an(.15,.15,.01),h),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Re(new an(.1,.1,.1),p.clone())]]},ee={X:[[new Re(new Pn(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Re(new Pn(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Re(new Pn(.2,0,.6,4),n),[0,.3,0]],[new Re(new Pn(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Re(new Pn(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Re(new Pn(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XY:[[new Re(new an(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Re(new an(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Re(new an(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Re(new an(.2,.2,.2),n),[0,0,0]]]},te={X:[[new yi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new yi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new yi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]};function se(he){const q=new tn;for(const de in he)for(let re=he[de].length;re--;){const ge=he[de][re][0].clone(),be=he[de][re][1],ze=he[de][re][2],Ge=he[de][re][3],pt=he[de][re][4];ge.name=de,ge.tag=pt,be&&ge.position.set(be[0],be[1],be[2]),ze&&ge.rotation.set(ze[0],ze[1],ze[2]),Ge&&ge.scale.set(Ge[0],Ge[1],Ge[2]),ge.updateMatrix();const le=ge.geometry.clone();le.applyMatrix4(ge.matrix),ge.geometry=le,ge.renderOrder=1/0,ge.position.set(0,0,0),ge.rotation.set(0,0,0),ge.scale.set(1,1,1),q.add(ge)}return q}this.gizmo={},this.picker={},this.helper={},this.add(this.gizmo.translate=se(B)),this.add(this.gizmo.rotate=se(V)),this.add(this.gizmo.scale=se(H)),this.add(this.picker.translate=se(U)),this.add(this.picker.rotate=se(R)),this.add(this.picker.scale=se(ee)),this.add(this.helper.translate=se(O)),this.add(this.helper.rotate=se(I)),this.add(this.helper.scale=se(te)),this.picker.translate.visible=!1,this.picker.rotate.visible=!1,this.picker.scale.visible=!1}updateMatrixWorld(e){const n=(this.mode==="scale"?"local":this.space)==="local"?this.worldQuaternion:Ic;this.gizmo.translate.visible=this.mode==="translate",this.gizmo.rotate.visible=this.mode==="rotate",this.gizmo.scale.visible=this.mode==="scale",this.helper.translate.visible=this.mode==="translate",this.helper.rotate.visible=this.mode==="rotate",this.helper.scale.visible=this.mode==="scale";let i=[];i=i.concat(this.picker[this.mode].children),i=i.concat(this.gizmo[this.mode].children),i=i.concat(this.helper[this.mode].children);for(let s=0;s<i.length;s++){const a=i[s];a.visible=!0,a.rotation.set(0,0,0),a.position.copy(this.worldPosition);let c;if(this.camera.isOrthographicCamera?c=(this.camera.top-this.camera.bottom)/this.camera.zoom:c=this.worldPosition.distanceTo(this.cameraPosition)*Math.min(1.9*Math.tan(Math.PI*this.camera.fov/360)/this.camera.zoom,7),a.scale.set(1,1,1).multiplyScalar(c*this.size/4),a.tag==="helper"){a.visible=!1,a.name==="AXIS"?(a.visible=!!this.axis,this.axis==="X"&&(sn.setFromEuler(xc.set(0,0,0)),a.quaternion.copy(n).multiply(sn),Math.abs(Kt.copy(qo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Y"&&(sn.setFromEuler(xc.set(0,0,Math.PI/2)),a.quaternion.copy(n).multiply(sn),Math.abs(Kt.copy(ss).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Z"&&(sn.setFromEuler(xc.set(0,Math.PI/2,0)),a.quaternion.copy(n).multiply(sn),Math.abs(Kt.copy(Yo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="XYZE"&&(sn.setFromEuler(xc.set(0,Math.PI/2,0)),Kt.copy(this.rotationAxis),a.quaternion.setFromRotationMatrix(tg.lookAt(eg,Kt,ss)),a.quaternion.multiply(sn),a.visible=this.dragging),this.axis==="E"&&(a.visible=!1)):a.name==="START"?(a.position.copy(this.worldPositionStart),a.visible=this.dragging):a.name==="END"?(a.position.copy(this.worldPosition),a.visible=this.dragging):a.name==="DELTA"?(a.position.copy(this.worldPositionStart),a.quaternion.copy(this.worldQuaternionStart),Un.set(1e-10,1e-10,1e-10).add(this.worldPositionStart).sub(this.worldPosition).multiplyScalar(-1),Un.applyQuaternion(this.worldQuaternionStart.clone().invert()),a.scale.copy(Un),a.visible=this.dragging):(a.quaternion.copy(n),this.dragging?a.position.copy(this.worldPositionStart):a.position.copy(this.worldPosition),this.axis&&(a.visible=this.axis.search(a.name)!==-1));continue}a.quaternion.copy(n),this.mode==="translate"||this.mode==="scale"?(a.name==="X"&&Math.abs(Kt.copy(qo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Y"&&Math.abs(Kt.copy(ss).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Z"&&Math.abs(Kt.copy(Yo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XY"&&Math.abs(Kt.copy(Yo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="YZ"&&Math.abs(Kt.copy(qo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XZ"&&Math.abs(Kt.copy(ss).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1)):this.mode==="rotate"&&(bc.copy(n),Kt.copy(this.eye).applyQuaternion(sn.copy(n).invert()),a.name.search("E")!==-1&&a.quaternion.setFromRotationMatrix(tg.lookAt(this.eye,eg,ss)),a.name==="X"&&(sn.setFromAxisAngle(qo,Math.atan2(-Kt.y,Kt.z)),sn.multiplyQuaternions(bc,sn),a.quaternion.copy(sn)),a.name==="Y"&&(sn.setFromAxisAngle(ss,Math.atan2(Kt.x,Kt.z)),sn.multiplyQuaternions(bc,sn),a.quaternion.copy(sn)),a.name==="Z"&&(sn.setFromAxisAngle(Yo,Math.atan2(Kt.y,Kt.x)),sn.multiplyQuaternions(bc,sn),a.quaternion.copy(sn))),a.visible=a.visible&&(a.name.indexOf("X")===-1||this.showX),a.visible=a.visible&&(a.name.indexOf("Y")===-1||this.showY),a.visible=a.visible&&(a.name.indexOf("Z")===-1||this.showZ),a.visible=a.visible&&(a.name.indexOf("E")===-1||this.showX&&this.showY&&this.showZ),a.material._color=a.material._color||a.material.color.clone(),a.material._opacity=a.material._opacity||a.material.opacity,a.material.color.copy(a.material._color),a.material.opacity=a.material._opacity,this.enabled&&this.axis&&(a.name===this.axis||this.axis.split("").some(function(u){return a.name===u}))&&(a.material.color.setHex(16776960),a.material.opacity=1)}super.updateMatrixWorld(e)}}class NC extends Re{constructor(){super(new lo(1e5,1e5,2,2),new pi({visible:!1,wireframe:!0,side:Kn,transparent:!0,opacity:.1,toneMapped:!1})),this.isTransformControlsPlane=!0,this.type="TransformControlsPlane"}updateMatrixWorld(e){let t=this.space;switch(this.position.copy(this.worldPosition),this.mode==="scale"&&(t="local"),Sc.copy(qo).applyQuaternion(t==="local"?this.worldQuaternion:Ic),Ho.copy(ss).applyQuaternion(t==="local"?this.worldQuaternion:Ic),Vo.copy(Yo).applyQuaternion(t==="local"?this.worldQuaternion:Ic),Kt.copy(Ho),this.mode){case"translate":case"scale":switch(this.axis){case"X":Kt.copy(this.eye).cross(Sc),Ri.copy(Sc).cross(Kt);break;case"Y":Kt.copy(this.eye).cross(Ho),Ri.copy(Ho).cross(Kt);break;case"Z":Kt.copy(this.eye).cross(Vo),Ri.copy(Vo).cross(Kt);break;case"XY":Ri.copy(Vo);break;case"YZ":Ri.copy(Sc);break;case"XZ":Kt.copy(Vo),Ri.copy(Ho);break;case"XYZ":case"E":Ri.set(0,0,0);break}break;case"rotate":default:Ri.set(0,0,0)}Ri.length()===0?this.quaternion.copy(this.cameraQuaternion):(ng.lookAt(Un.set(0,0,0),Ri,Kt),this.quaternion.setFromRotationMatrix(ng)),super.updateMatrixWorld(e)}}function ah(r){const e=new er,t=new Td(.4,1,16),n=new pi({color:r,transparent:!0,opacity:1,side:Kn,depthTest:!1,depthWrite:!1}),i=new Re(t,n);i.rotation.x=Math.PI,i.renderOrder=999;const s=new sa(.35,32,32),a=new pi({color:new st(1,1,1),emissive:r,emissiveIntensity:2,transparent:!0,opacity:1,depthTest:!1,depthWrite:!1}),c=new Re(s,a);return c.position.y=.5,c.renderOrder=999,e.add(i),e.add(c),e}function OC(r){const e=new AP({canvas:r,antialias:!0});e.setPixelRatio(window.devicePixelRatio),e.setSize(r.clientWidth,r.clientHeight),e.shadowMap.enabled=!1,e.toneMapping=dg,e.toneMappingExposure=1.6,e.outputColorSpace=En;const t=new RP;t.background=new st(1381664),t.fog=new Ed(1381664,.03);const n=new Vn(50,r.clientWidth/r.clientHeight,.1,1e3);n.position.set(0,1.6,5);const i=new pC(n,r);i.target.set(0,.9,0),i.enableDamping=!0,i.dampingFactor=.08,i.update();const s=new lo(14,10),a=new hs({color:4864558,roughness:.35,metalness:.05}),c=new Re(s,a);c.rotation.x=-Math.PI/2,c.position.y=-.01,c.receiveShadow=!0,t.add(c);const u=new an(14.2,.06,10.2),h=new hs({color:3811866,roughness:.6}),f=new Re(u,h);f.position.y=-.04,f.receiveShadow=!0,t.add(f);const p=new QP(16777215,.8);t.add(p);const m=new Dc(16777215,3);m.position.set(2,4,-5),t.add(m);const g=ah(new st(16777215));g.position.copy(m.position),g.lookAt(new N(0,0,0)),g.userData.light=m,t.add(g);const x=new Dc(15658751,2);x.position.set(-3,3,-4),t.add(x);const E=ah(new st(15658751));E.position.copy(x.position),E.lookAt(new N(0,0,0)),E.userData.light=x,t.add(E);const v=new Dc(16772829,2.5);v.position.set(0,4,5),t.add(v);const _=ah(new st(16772829));_.position.copy(v.position),_.lookAt(new N(0,0,0)),_.userData.light=v,t.add(_);const A={ambient:p,spotLeft:m,spotRight:x,backLight:v},w={spotLeftIcon:g,spotRightIcon:E,backLightIcon:_},b=new AC(n,r);b.setMode("translate"),b.setSize(.8),t.add(b),b.addEventListener("dragging-changed",U=>{i.enabled=!U.value});function B(){const U=r.clientWidth,O=r.clientHeight;e.setSize(U,O),n.aspect=U/O,n.updateProjectionMatrix()}return window.addEventListener("resize",B),{scene:t,camera:n,renderer:e,controls:i,lights:A,lightIcons:w,transformControls:b}}var Ko={exports:{}};Ko.exports;var ig;function UC(){return ig||(ig=1,(function(r,e){var t=Object.create,n=Object.defineProperty,i=Object.defineProperties,s=Object.getOwnPropertyDescriptor,a=Object.getOwnPropertyDescriptors,c=Object.getOwnPropertyNames,u=Object.getOwnPropertySymbols,h=Object.getPrototypeOf,f=Object.prototype.hasOwnProperty,p=Object.prototype.propertyIsEnumerable,m=(o,l,d)=>l in o?n(o,l,{enumerable:!0,configurable:!0,writable:!0,value:d}):o[l]=d,g=(o,l)=>{for(var d in l||(l={}))f.call(l,d)&&m(o,d,l[d]);if(u)for(var d of u(l))p.call(l,d)&&m(o,d,l[d]);return o},x=(o,l)=>i(o,a(l)),E=(o,l)=>function(){return l||(0,o[c(o)[0]])((l={exports:{}}).exports,l),l.exports},v=(o,l)=>{for(var d in l)n(o,d,{get:l[d],enumerable:!0})},_=(o,l,d,y)=>{if(l&&typeof l=="object"||typeof l=="function")for(let M of c(l))!f.call(o,M)&&M!==d&&n(o,M,{get:()=>l[M],enumerable:!(y=s(l,M))||y.enumerable});return o},A=(o,l,d)=>(d=o!=null?t(h(o)):{},_(!o||!o.__esModule?n(d,"default",{value:o,enumerable:!0}):d,o)),w=o=>_(n({},"__esModule",{value:!0}),o),b=(o,l,d)=>(m(o,typeof l!="symbol"?l+"":l,d),d),B=E({"../node_modules/timing-function/lib/UnitBezier.js"(o,l){l.exports=(function(){function d(y,M,D,z){this.set(y,M,D,z)}return d.prototype.set=function(y,M,D,z){this._cx=3*y,this._bx=3*(D-y)-this._cx,this._ax=1-this._cx-this._bx,this._cy=3*M,this._by=3*(z-M)-this._cy,this._ay=1-this._cy-this._by},d.epsilon=1e-6,d.prototype._sampleCurveX=function(y){return((this._ax*y+this._bx)*y+this._cx)*y},d.prototype._sampleCurveY=function(y){return((this._ay*y+this._by)*y+this._cy)*y},d.prototype._sampleCurveDerivativeX=function(y){return(3*this._ax*y+2*this._bx)*y+this._cx},d.prototype._solveCurveX=function(y,M){var D,z,K,Q,ae,ye;for(K=void 0,Q=void 0,ae=void 0,ye=void 0,D=void 0,z=void 0,ae=y,z=0;z<8;){if(ye=this._sampleCurveX(ae)-y,Math.abs(ye)<M)return ae;if(D=this._sampleCurveDerivativeX(ae),Math.abs(D)<M)break;ae=ae-ye/D,z++}if(K=0,Q=1,ae=y,ae<K)return K;if(ae>Q)return Q;for(;K<Q;){if(ye=this._sampleCurveX(ae),Math.abs(ye-y)<M)return ae;y>ye?K=ae:Q=ae,ae=(Q-K)*.5+K}return ae},d.prototype.solve=function(y,M){return this._sampleCurveY(this._solveCurveX(y,M))},d.prototype.solveSimple=function(y){return this._sampleCurveY(this._solveCurveX(y,1e-6))},d})()}}),U=E({"../node_modules/levenshtein-edit-distance/index.js"(o,l){var d,y;d=[],y=[];function M(D,z,K){var Q,ae,ye,xe,Ce,et,je,vt;if(D===z)return 0;if(Q=D.length,ae=z.length,Q===0)return ae;if(ae===0)return Q;for(K&&(D=D.toLowerCase(),z=z.toLowerCase()),je=0;je<Q;)y[je]=D.charCodeAt(je),d[je]=++je;for(vt=0;vt<ae;)for(ye=z.charCodeAt(vt),xe=Ce=vt++,je=-1;++je<Q;)et=ye===y[je]?Ce:Ce+1,Ce=d[je],d[je]=xe=Ce>xe?et>xe?xe+1:et:et>Ce?Ce+1:et;return xe}l.exports=M}}),O=E({"../node_modules/propose/propose.js"(o,l){var d=U();function y(){var M,D,z,K,Q,ae=0,ye=arguments[0],xe=arguments[1],Ce=xe.length,et=arguments[2];et&&(K=et.threshold,Q=et.ignoreCase),K===void 0&&(K=0);for(var je=0;je<Ce;++je)Q?D=d(ye,xe[je],!0):D=d(ye,xe[je]),D>ye.length?M=1-D/xe[je].length:M=1-D/ye.length,M>ae&&(ae=M,z=xe[je]);return ae>=K?z:null}l.exports=y}}),V=E({"../node_modules/fast-deep-equal/index.js"(o,l){l.exports=function d(y,M){if(y===M)return!0;if(y&&M&&typeof y=="object"&&typeof M=="object"){if(y.constructor!==M.constructor)return!1;var D,z,K;if(Array.isArray(y)){if(D=y.length,D!=M.length)return!1;for(z=D;z--!==0;)if(!d(y[z],M[z]))return!1;return!0}if(y.constructor===RegExp)return y.source===M.source&&y.flags===M.flags;if(y.valueOf!==Object.prototype.valueOf)return y.valueOf()===M.valueOf();if(y.toString!==Object.prototype.toString)return y.toString()===M.toString();if(K=Object.keys(y),D=K.length,D!==Object.keys(M).length)return!1;for(z=D;z--!==0;)if(!Object.prototype.hasOwnProperty.call(M,K[z]))return!1;for(z=D;z--!==0;){var Q=K[z];if(!d(y[Q],M[Q]))return!1}return!0}return y!==y&&M!==M}}}),I={};v(I,{createRafDriver:()=>eu,getProject:()=>Mp,notify:()=>Es,onChange:()=>Su,types:()=>tu,val:()=>Tp}),r.exports=w(I);var R={};v(R,{createRafDriver:()=>eu,getProject:()=>Mp,notify:()=>Es,onChange:()=>Su,types:()=>tu,val:()=>Tp});var H=mn(),ee=class{constructor(){b(this,"atom",new H.Atom({projects:{}}))}add(o,l){this.atom.setByPointer(d=>d.projects[o],l)}get(o){return this.atom.get().projects[o]}has(o){return!!this.get(o)}},te=new ee,se=te,he=new WeakMap;function q(o){return he.get(o)}function de(o,l){he.set(o,l)}var re=[],ge=Array.isArray,be=ge,ze=typeof Ci=="object"&&Ci&&Ci.Object===Object&&Ci,Ge=ze,pt=typeof self=="object"&&self&&self.Object===Object&&self,le=Ge||pt||Function("return this")(),me=le,Ue=me.Symbol,Se=Ue,$e=Object.prototype,it=$e.hasOwnProperty,Je=$e.toString,pe=Se?Se.toStringTag:void 0;function ve(o){var l=it.call(o,pe),d=o[pe];try{o[pe]=void 0;var y=!0}catch{}var M=Je.call(o);return y&&(l?o[pe]=d:delete o[pe]),M}var Le=ve,G=Object.prototype,tt=G.toString;function Ke(o){return tt.call(o)}var Qe=Ke,Oe="[object Null]",rt="[object Undefined]",Fe=Se?Se.toStringTag:void 0;function F(o){return o==null?o===void 0?rt:Oe:Fe&&Fe in Object(o)?Le(o):Qe(o)}var T=F;function Z(o){return o!=null&&typeof o=="object"}var ce=Z,fe="[object Symbol]";function ue(o){return typeof o=="symbol"||ce(o)&&T(o)==fe}var ke=ue,we=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,Be=/^\w*$/;function gt(o,l){if(be(o))return!1;var d=typeof o;return d=="number"||d=="symbol"||d=="boolean"||o==null||ke(o)?!0:Be.test(o)||!we.test(o)||l!=null&&o in Object(l)}var _e=gt;function He(o){var l=typeof o;return o!=null&&(l=="object"||l=="function")}var We=He,ot="[object AsyncFunction]",Ve="[object Function]",xt="[object GeneratorFunction]",dt="[object Proxy]";function It(o){if(!We(o))return!1;var l=T(o);return l==Ve||l==xt||l==ot||l==dt}var X=It,Ae=me["__core-js_shared__"],P=Ae,k=(function(){var o=/[^.]+$/.exec(P&&P.keys&&P.keys.IE_PROTO||"");return o?"Symbol(src)_1."+o:""})();function $(o){return!!k&&k in o}var ie=$,Te=Function.prototype,Ee=Te.toString;function De(o){if(o!=null){try{return Ee.call(o)}catch{}try{return o+""}catch{}}return""}var Pe=De,ut=/[\\^$.*+?()[\]{}|]/g,bt=/^\[object .+?Constructor\]$/,Ft=Function.prototype,mt=Object.prototype,nt=Ft.toString,jt=mt.hasOwnProperty,Dt=RegExp("^"+nt.call(jt).replace(ut,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function Xt(o){if(!We(o)||ie(o))return!1;var l=X(o)?Dt:bt;return l.test(Pe(o))}var qt=Xt;function Tt(o,l){return o==null?void 0:o[l]}var nn=Tt;function Tn(o,l){var d=nn(o,l);return qt(d)?d:void 0}var Bn=Tn,rr=Bn(Object,"create"),Zn=rr;function ci(){this.__data__=Zn?Zn(null):{},this.size=0}var C=ci;function j(o){var l=this.has(o)&&delete this.__data__[o];return this.size-=l?1:0,l}var J=j,ne="__lodash_hash_undefined__",Y=Object.prototype,Me=Y.hasOwnProperty;function Ne(o){var l=this.__data__;if(Zn){var d=l[o];return d===ne?void 0:d}return Me.call(l,o)?l[o]:void 0}var Xe=Ne,qe=Object.prototype,ht=qe.hasOwnProperty;function at(o){var l=this.__data__;return Zn?l[o]!==void 0:ht.call(l,o)}var Ye=at,Rt="__lodash_hash_undefined__";function Ut(o,l){var d=this.__data__;return this.size+=this.has(o)?0:1,d[o]=Zn&&l===void 0?Rt:l,this}var kt=Ut;function on(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}on.prototype.clear=C,on.prototype.delete=J,on.prototype.get=Xe,on.prototype.has=Ye,on.prototype.set=kt;var Pt=on;function Ze(){this.__data__=[],this.size=0}var Qn=Ze;function wt(o,l){return o===l||o!==o&&l!==l}var wn=wt;function wi(o,l){for(var d=o.length;d--;)if(wn(o[d][0],l))return d;return-1}var un=wi,Ni=Array.prototype,zt=Ni.splice;function jn(o){var l=this.__data__,d=un(l,o);if(d<0)return!1;var y=l.length-1;return d==y?l.pop():zt.call(l,d,1),--this.size,!0}var Oi=jn;function Dn(o){var l=this.__data__,d=un(l,o);return d<0?void 0:l[d][1]}var An=Dn;function Jn(o){return un(this.__data__,o)>-1}var fs=Jn;function po(o,l){var d=this.__data__,y=un(d,o);return y<0?(++this.size,d.push([o,l])):d[y][1]=l,this}var jc=po;function sr(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}sr.prototype.clear=Qn,sr.prototype.delete=Oi,sr.prototype.get=An,sr.prototype.has=fs,sr.prototype.set=jc;var ps=sr,Xc=Bn(me,"Map"),Pr=Xc;function qc(){this.size=0,this.__data__={hash:new Pt,map:new(Pr||ps),string:new Pt}}var Yc=qc;function Kc(o){var l=typeof o;return l=="string"||l=="number"||l=="symbol"||l=="boolean"?o!=="__proto__":o===null}var $c=Kc;function Zc(o,l){var d=o.__data__;return $c(l)?d[typeof l=="string"?"string":"hash"]:d.map}var Cr=Zc;function aa(o){var l=Cr(this,o).delete(o);return this.size-=l?1:0,l}var ca=aa;function Qc(o){return Cr(this,o).get(o)}var Jc=Qc;function el(o){return Cr(this,o).has(o)}var tl=el;function nl(o,l){var d=Cr(this,o),y=d.size;return d.set(o,l),this.size+=d.size==y?0:1,this}var il=nl;function or(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}or.prototype.clear=Yc,or.prototype.delete=ca,or.prototype.get=Jc,or.prototype.has=tl,or.prototype.set=il;var ms=or,rl="Expected a function";function mo(o,l){if(typeof o!="function"||l!=null&&typeof l!="function")throw new TypeError(rl);var d=function(){var y=arguments,M=l?l.apply(this,y):y[0],D=d.cache;if(D.has(M))return D.get(M);var z=o.apply(this,y);return d.cache=D.set(M,z)||D,z};return d.cache=new(mo.Cache||ms),d}mo.Cache=ms;var sl=mo,ol=500;function al(o){var l=sl(o,function(y){return d.size===ol&&d.clear(),y}),d=l.cache;return l}var cl=al,ll=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,ul=/\\(\\)?/g,hl=cl(function(o){var l=[];return o.charCodeAt(0)===46&&l.push(""),o.replace(ll,function(d,y,M,D){l.push(M?D.replace(ul,"$1"):y||d)}),l}),dl=hl;function la(o,l){for(var d=-1,y=o==null?0:o.length,M=Array(y);++d<y;)M[d]=l(o[d],d,o);return M}var fl=la,ua=Se?Se.prototype:void 0,ha=ua?ua.toString:void 0;function da(o){if(typeof o=="string")return o;if(be(o))return fl(o,da)+"";if(ke(o))return ha?ha.call(o):"";var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var fa=da;function pl(o){return o==null?"":fa(o)}var gs=pl;function pa(o,l){return be(o)?o:_e(o,l)?[o]:dl(gs(o))}var Dr=pa;function ml(o){if(typeof o=="string"||ke(o))return o;var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var mi=ml;function Ir(o,l){l=Dr(l,o);for(var d=0,y=l.length;o!=null&&d<y;)o=o[mi(l[d++])];return d&&d==y?o:void 0}var _s=Ir;function go(o,l,d){var y=o==null?void 0:_s(o,l);return y===void 0?d:y}var Ui=go;function ma(o,l){return l.length===0?o:Ui(o,l)}var ar=class{constructor(){b(this,"_values",{})}get(o,l){if(this.has(o))return this._values[o];{const d=l();return this._values[o]=d,d}}has(o){return this._values.hasOwnProperty(o)}},fn=mn(),vs=(function(){try{var o=Bn(Object,"defineProperty");return o({},"",{}),o}catch{}})(),_o=vs;function gl(o,l,d){l=="__proto__"&&_o?_o(o,l,{configurable:!0,enumerable:!0,value:d,writable:!0}):o[l]=d}var Bi=gl,Lr=Object.prototype,_l=Lr.hasOwnProperty;function vl(o,l,d){var y=o[l];(!(_l.call(o,l)&&wn(y,d))||d===void 0&&!(l in o))&&Bi(o,l,d)}var vo=vl,yl=9007199254740991,ga=/^(?:0|[1-9]\d*)$/;function xl(o,l){var d=typeof o;return l=l??yl,!!l&&(d=="number"||d!="symbol"&&ga.test(o))&&o>-1&&o%1==0&&o<l}var yo=xl;function bl(o,l,d,y){if(!We(o))return o;l=Dr(l,o);for(var M=-1,D=l.length,z=D-1,K=o;K!=null&&++M<D;){var Q=mi(l[M]),ae=d;if(Q==="__proto__"||Q==="constructor"||Q==="prototype")return o;if(M!=z){var ye=K[Q];ae=y?y(ye,Q,K):void 0,ae===void 0&&(ae=We(ye)?ye:yo(l[M+1])?[]:{})}vo(K,Q,ae),K=K[Q]}return o}var _a=bl;function va(o,l,d){return o==null?o:_a(o,l,d)}var ys=va,xn=new WeakMap;function Sl(o){return xo(o)}function xo(o){if(xn.has(o))return xn.get(o);const l=o.type==="compound"?xa(o):o.type==="enum"?ya(o):o.default;return xn.set(o,l),l}function ya(o){const l={$case:o.defaultCase};for(const[d,y]of Object.entries(o.cases))l[d]=xo(y);return l}function xa(o){const l={};for(const[d,y]of Object.entries(o.props))l[d]=xo(y);return l}var kn=mn(),El=A(B());function Ml(o,l,d){return(0,kn.prism)(()=>{const y=(0,kn.val)(l);return kn.prism.memo("driver",()=>y?y.type==="BasicKeyframedTrack"?Tl(o,y,d):(o.logger.error("Track type not yet supported."),(0,kn.prism)(()=>{})):(0,kn.prism)(()=>{}),[y]).getValue()})}function Tl(o,l,d){return(0,kn.prism)(()=>{let y=kn.prism.ref("state",{started:!1}),M=y.current;const D=d.getValue();return(!M.started||D<M.validFrom||M.validTo<=D)&&(y.current=M=wl(o,d,l)),M.der.getValue()})}var ba=(0,kn.prism)(()=>{});function wl(o,l,d){const y=l.getValue();if(d.keyframes.length===0)return{started:!0,validFrom:-1/0,validTo:1/0,der:ba};let M=0;for(;;){const D=d.keyframes[M];if(!D)return pn.error;const z=M===d.keyframes.length-1;if(y<D.position)return M===0?pn.beforeFirstKeyframe(D):pn.error;if(D.position===y)return z?pn.lastKeyframe(D):pn.between(D,d.keyframes[M+1],l);if(M===d.keyframes.length-1)return pn.lastKeyframe(D);{const K=M+1;if(d.keyframes[K].position<=y){M=K;continue}else return pn.between(D,d.keyframes[M+1],l)}}}var pn={beforeFirstKeyframe(o){return{started:!0,validFrom:-1/0,validTo:o.position,der:(0,kn.prism)(()=>({left:o.value,progression:0}))}},lastKeyframe(o){return{started:!0,validFrom:o.position,validTo:1/0,der:(0,kn.prism)(()=>({left:o.value,progression:0}))}},between(o,l,d){if(!o.connectedRight)return{started:!0,validFrom:o.position,validTo:l.position,der:(0,kn.prism)(()=>({left:o.value,progression:0}))};const y=D=>(D-o.position)/(l.position-o.position);if(!o.type||o.type==="bezier"){const D=new El.default(o.handles[2],o.handles[3],l.handles[0],l.handles[1]),z=(0,kn.prism)(()=>{const K=y(d.getValue()),Q=D.solveSimple(K);return{left:o.value,right:l.value,progression:Q}});return{started:!0,validFrom:o.position,validTo:l.position,der:z}}const M=(0,kn.prism)(()=>{const D=y(d.getValue()),z=Math.floor(D);return{left:o.value,right:l.value,progression:z}});return{started:!0,validFrom:o.position,validTo:l.position,der:M}},error:{started:!0,validFrom:-1/0,validTo:1/0,der:ba}};function Fr(o,l,d){const M=d.get(o);if(M&&M.override===l)return M.merged;const D=g({},o);for(const z of Object.keys(l)){const K=l[z],Q=o[z];D[z]=typeof K=="object"&&typeof Q=="object"?Fr(Q,K,d):K===void 0?Q:K}return d.set(o,{override:l,merged:D}),D}function Nr(o,l){let d=o;for(const y of l)d=d[y];return d}var Or=mn(),Sa=(o,l)=>{const d=Or.prism.memo(o,()=>new Or.Atom(l),[]);return d.set(l),d},Ht=mn(),bo=mn(),Al=/\s/;function Ea(o){for(var l=o.length;l--&&Al.test(o.charAt(l)););return l}var Ma=Ea,Ta=/^\s+/;function Rl(o){return o&&o.slice(0,Ma(o)+1).replace(Ta,"")}var xs=Rl,So=NaN,Pl=/^[-+]0x[0-9a-f]+$/i,Cl=/^0b[01]+$/i,wa=/^0o[0-7]+$/i,Dl=parseInt;function Il(o){if(typeof o=="number")return o;if(ke(o))return So;if(We(o)){var l=typeof o.valueOf=="function"?o.valueOf():o;o=We(l)?l+"":l}if(typeof o!="string")return o===0?o:+o;o=xs(o);var d=Cl.test(o);return d||wa.test(o)?Dl(o.slice(2),d?2:8):Pl.test(o)?So:+o}var S=Il,L=1/0,W=17976931348623157e292;function oe(o){if(!o)return o===0?o:0;if(o=S(o),o===L||o===-L){var l=o<0?-1:1;return l*W}return o===o?o:0}var ct=oe;function Lt(o){var l=ct(o),d=l%1;return l===l?d?l-d:l:0}var Rn=Lt;function li(o){return o}var Aa=li,cr=Bn(me,"WeakMap"),Ur=cr,Fd=Object.create,l_=(function(){function o(){}return function(l){if(!We(l))return{};if(Fd)return Fd(l);o.prototype=l;var d=new o;return o.prototype=void 0,d}})(),u_=l_;function h_(o,l){var d=-1,y=o.length;for(l||(l=Array(y));++d<y;)l[d]=o[d];return l}var d_=h_;function f_(o,l){for(var d=-1,y=o==null?0:o.length;++d<y&&l(o[d],d,o)!==!1;);return o}var p_=f_;function m_(o,l,d,y){var M=!d;d||(d={});for(var D=-1,z=l.length;++D<z;){var K=l[D],Q=y?y(d[K],o[K],K,d,o):void 0;Q===void 0&&(Q=o[K]),M?Bi(d,K,Q):vo(d,K,Q)}return d}var Ra=m_,g_=9007199254740991;function __(o){return typeof o=="number"&&o>-1&&o%1==0&&o<=g_}var Ll=__;function v_(o){return o!=null&&Ll(o.length)&&!X(o)}var Nd=v_,y_=Object.prototype;function x_(o){var l=o&&o.constructor,d=typeof l=="function"&&l.prototype||y_;return o===d}var Fl=x_;function b_(o,l){for(var d=-1,y=Array(o);++d<o;)y[d]=l(d);return y}var S_=b_,E_="[object Arguments]";function M_(o){return ce(o)&&T(o)==E_}var Od=M_,Ud=Object.prototype,T_=Ud.hasOwnProperty,w_=Ud.propertyIsEnumerable,A_=Od((function(){return arguments})())?Od:function(o){return ce(o)&&T_.call(o,"callee")&&!w_.call(o,"callee")},Bd=A_;function R_(){return!1}var P_=R_,kd=e&&!e.nodeType&&e,zd=kd&&!0&&r&&!r.nodeType&&r,C_=zd&&zd.exports===kd,Hd=C_?me.Buffer:void 0,D_=Hd?Hd.isBuffer:void 0,I_=D_||P_,Pa=I_,L_="[object Arguments]",F_="[object Array]",N_="[object Boolean]",O_="[object Date]",U_="[object Error]",B_="[object Function]",k_="[object Map]",z_="[object Number]",H_="[object Object]",V_="[object RegExp]",G_="[object Set]",W_="[object String]",j_="[object WeakMap]",X_="[object ArrayBuffer]",q_="[object DataView]",Y_="[object Float32Array]",K_="[object Float64Array]",$_="[object Int8Array]",Z_="[object Int16Array]",Q_="[object Int32Array]",J_="[object Uint8Array]",ev="[object Uint8ClampedArray]",tv="[object Uint16Array]",nv="[object Uint32Array]",rn={};rn[Y_]=rn[K_]=rn[$_]=rn[Z_]=rn[Q_]=rn[J_]=rn[ev]=rn[tv]=rn[nv]=!0,rn[L_]=rn[F_]=rn[X_]=rn[N_]=rn[q_]=rn[O_]=rn[U_]=rn[B_]=rn[k_]=rn[z_]=rn[H_]=rn[V_]=rn[G_]=rn[W_]=rn[j_]=!1;function iv(o){return ce(o)&&Ll(o.length)&&!!rn[T(o)]}var rv=iv;function sv(o){return function(l){return o(l)}}var Nl=sv,Vd=e&&!e.nodeType&&e,Eo=Vd&&!0&&r&&!r.nodeType&&r,ov=Eo&&Eo.exports===Vd,Ol=ov&&Ge.process,av=(function(){try{var o=Eo&&Eo.require&&Eo.require("util").types;return o||Ol&&Ol.binding&&Ol.binding("util")}catch{}})(),bs=av,Gd=bs&&bs.isTypedArray,cv=Gd?Nl(Gd):rv,Wd=cv,lv=Object.prototype,uv=lv.hasOwnProperty;function hv(o,l){var d=be(o),y=!d&&Bd(o),M=!d&&!y&&Pa(o),D=!d&&!y&&!M&&Wd(o),z=d||y||M||D,K=z?S_(o.length,String):[],Q=K.length;for(var ae in o)(l||uv.call(o,ae))&&!(z&&(ae=="length"||M&&(ae=="offset"||ae=="parent")||D&&(ae=="buffer"||ae=="byteLength"||ae=="byteOffset")||yo(ae,Q)))&&K.push(ae);return K}var jd=hv;function dv(o,l){return function(d){return o(l(d))}}var Xd=dv,fv=Xd(Object.keys,Object),pv=fv,mv=Object.prototype,gv=mv.hasOwnProperty;function _v(o){if(!Fl(o))return pv(o);var l=[];for(var d in Object(o))gv.call(o,d)&&d!="constructor"&&l.push(d);return l}var vv=_v;function yv(o){return Nd(o)?jd(o):vv(o)}var Mo=yv;function xv(o){var l=[];if(o!=null)for(var d in Object(o))l.push(d);return l}var bv=xv,Sv=Object.prototype,Ev=Sv.hasOwnProperty;function Mv(o){if(!We(o))return bv(o);var l=Fl(o),d=[];for(var y in o)y=="constructor"&&(l||!Ev.call(o,y))||d.push(y);return d}var Tv=Mv;function wv(o){return Nd(o)?jd(o,!0):Tv(o)}var Ul=wv;function Av(o,l){for(var d=-1,y=l.length,M=o.length;++d<y;)o[M+d]=l[d];return o}var qd=Av,Rv=Xd(Object.getPrototypeOf,Object),Bl=Rv,Pv="[object Object]",Cv=Function.prototype,Dv=Object.prototype,Yd=Cv.toString,Iv=Dv.hasOwnProperty,Lv=Yd.call(Object);function Fv(o){if(!ce(o)||T(o)!=Pv)return!1;var l=Bl(o);if(l===null)return!0;var d=Iv.call(l,"constructor")&&l.constructor;return typeof d=="function"&&d instanceof d&&Yd.call(d)==Lv}var Nv=Fv;function Ov(o,l,d){var y=-1,M=o.length;l<0&&(l=-l>M?0:M+l),d=d>M?M:d,d<0&&(d+=M),M=l>d?0:d-l>>>0,l>>>=0;for(var D=Array(M);++y<M;)D[y]=o[y+l];return D}var Kd=Ov;function Uv(o,l,d){var y=o.length;return d=d===void 0?y:d,!l&&d>=y?o:Kd(o,l,d)}var Bv=Uv,kv="\\ud800-\\udfff",zv="\\u0300-\\u036f",Hv="\\ufe20-\\ufe2f",Vv="\\u20d0-\\u20ff",Gv=zv+Hv+Vv,Wv="\\ufe0e\\ufe0f",jv="\\u200d",Xv=RegExp("["+jv+kv+Gv+Wv+"]");function qv(o){return Xv.test(o)}var kl=qv;function Yv(o){return o.split("")}var Kv=Yv,$d="\\ud800-\\udfff",$v="\\u0300-\\u036f",Zv="\\ufe20-\\ufe2f",Qv="\\u20d0-\\u20ff",Jv=$v+Zv+Qv,e0="\\ufe0e\\ufe0f",t0="["+$d+"]",zl="["+Jv+"]",Hl="\\ud83c[\\udffb-\\udfff]",n0="(?:"+zl+"|"+Hl+")",Zd="[^"+$d+"]",Qd="(?:\\ud83c[\\udde6-\\uddff]){2}",Jd="[\\ud800-\\udbff][\\udc00-\\udfff]",i0="\\u200d",ef=n0+"?",tf="["+e0+"]?",r0="(?:"+i0+"(?:"+[Zd,Qd,Jd].join("|")+")"+tf+ef+")*",s0=tf+ef+r0,o0="(?:"+[Zd+zl+"?",zl,Qd,Jd,t0].join("|")+")",a0=RegExp(Hl+"(?="+Hl+")|"+o0+s0,"g");function c0(o){return o.match(a0)||[]}var l0=c0;function u0(o){return kl(o)?l0(o):Kv(o)}var h0=u0;function d0(o,l,d){return o===o&&(d!==void 0&&(o=o<=d?o:d),l!==void 0&&(o=o>=l?o:l)),o}var f0=d0;function p0(o,l,d){return d===void 0&&(d=l,l=void 0),d!==void 0&&(d=S(d),d=d===d?d:0),l!==void 0&&(l=S(l),l=l===l?l:0),f0(S(o),l,d)}var nf=p0;function m0(){this.__data__=new ps,this.size=0}var g0=m0;function _0(o){var l=this.__data__,d=l.delete(o);return this.size=l.size,d}var v0=_0;function y0(o){return this.__data__.get(o)}var x0=y0;function b0(o){return this.__data__.has(o)}var S0=b0,E0=200;function M0(o,l){var d=this.__data__;if(d instanceof ps){var y=d.__data__;if(!Pr||y.length<E0-1)return y.push([o,l]),this.size=++d.size,this;d=this.__data__=new ms(y)}return d.set(o,l),this.size=d.size,this}var T0=M0;function Ss(o){var l=this.__data__=new ps(o);this.size=l.size}Ss.prototype.clear=g0,Ss.prototype.delete=v0,Ss.prototype.get=x0,Ss.prototype.has=S0,Ss.prototype.set=T0;var To=Ss;function w0(o,l){return o&&Ra(l,Mo(l),o)}var A0=w0;function R0(o,l){return o&&Ra(l,Ul(l),o)}var P0=R0,rf=e&&!e.nodeType&&e,sf=rf&&!0&&r&&!r.nodeType&&r,C0=sf&&sf.exports===rf,of=C0?me.Buffer:void 0,af=of?of.allocUnsafe:void 0;function D0(o,l){if(l)return o.slice();var d=o.length,y=af?af(d):new o.constructor(d);return o.copy(y),y}var I0=D0;function L0(o,l){for(var d=-1,y=o==null?0:o.length,M=0,D=[];++d<y;){var z=o[d];l(z,d,o)&&(D[M++]=z)}return D}var F0=L0;function N0(){return[]}var cf=N0,O0=Object.prototype,U0=O0.propertyIsEnumerable,lf=Object.getOwnPropertySymbols,B0=lf?function(o){return o==null?[]:(o=Object(o),F0(lf(o),function(l){return U0.call(o,l)}))}:cf,Vl=B0;function k0(o,l){return Ra(o,Vl(o),l)}var z0=k0,H0=Object.getOwnPropertySymbols,V0=H0?function(o){for(var l=[];o;)qd(l,Vl(o)),o=Bl(o);return l}:cf,uf=V0;function G0(o,l){return Ra(o,uf(o),l)}var W0=G0;function j0(o,l,d){var y=l(o);return be(o)?y:qd(y,d(o))}var hf=j0;function X0(o){return hf(o,Mo,Vl)}var Gl=X0;function q0(o){return hf(o,Ul,uf)}var Y0=q0,K0=Bn(me,"DataView"),Wl=K0,$0=Bn(me,"Promise"),jl=$0,Z0=Bn(me,"Set"),Xl=Z0,df="[object Map]",Q0="[object Object]",ff="[object Promise]",pf="[object Set]",mf="[object WeakMap]",gf="[object DataView]",J0=Pe(Wl),ey=Pe(Pr),ty=Pe(jl),ny=Pe(Xl),iy=Pe(Ur),Br=T;(Wl&&Br(new Wl(new ArrayBuffer(1)))!=gf||Pr&&Br(new Pr)!=df||jl&&Br(jl.resolve())!=ff||Xl&&Br(new Xl)!=pf||Ur&&Br(new Ur)!=mf)&&(Br=function(o){var l=T(o),d=l==Q0?o.constructor:void 0,y=d?Pe(d):"";if(y)switch(y){case J0:return gf;case ey:return df;case ty:return ff;case ny:return pf;case iy:return mf}return l});var wo=Br,ry=Object.prototype,sy=ry.hasOwnProperty;function oy(o){var l=o.length,d=new o.constructor(l);return l&&typeof o[0]=="string"&&sy.call(o,"index")&&(d.index=o.index,d.input=o.input),d}var ay=oy,cy=me.Uint8Array,Ca=cy;function ly(o){var l=new o.constructor(o.byteLength);return new Ca(l).set(new Ca(o)),l}var ql=ly;function uy(o,l){var d=l?ql(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.byteLength)}var hy=uy,dy=/\w*$/;function fy(o){var l=new o.constructor(o.source,dy.exec(o));return l.lastIndex=o.lastIndex,l}var py=fy,_f=Se?Se.prototype:void 0,vf=_f?_f.valueOf:void 0;function my(o){return vf?Object(vf.call(o)):{}}var gy=my;function _y(o,l){var d=l?ql(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.length)}var vy=_y,yy="[object Boolean]",xy="[object Date]",by="[object Map]",Sy="[object Number]",Ey="[object RegExp]",My="[object Set]",Ty="[object String]",wy="[object Symbol]",Ay="[object ArrayBuffer]",Ry="[object DataView]",Py="[object Float32Array]",Cy="[object Float64Array]",Dy="[object Int8Array]",Iy="[object Int16Array]",Ly="[object Int32Array]",Fy="[object Uint8Array]",Ny="[object Uint8ClampedArray]",Oy="[object Uint16Array]",Uy="[object Uint32Array]";function By(o,l,d){var y=o.constructor;switch(l){case Ay:return ql(o);case yy:case xy:return new y(+o);case Ry:return hy(o,d);case Py:case Cy:case Dy:case Iy:case Ly:case Fy:case Ny:case Oy:case Uy:return vy(o,d);case by:return new y;case Sy:case Ty:return new y(o);case Ey:return py(o);case My:return new y;case wy:return gy(o)}}var ky=By;function zy(o){return typeof o.constructor=="function"&&!Fl(o)?u_(Bl(o)):{}}var Hy=zy,Vy="[object Map]";function Gy(o){return ce(o)&&wo(o)==Vy}var Wy=Gy,yf=bs&&bs.isMap,jy=yf?Nl(yf):Wy,Xy=jy,qy="[object Set]";function Yy(o){return ce(o)&&wo(o)==qy}var Ky=Yy,xf=bs&&bs.isSet,$y=xf?Nl(xf):Ky,Zy=$y,Qy=1,Jy=2,ex=4,bf="[object Arguments]",tx="[object Array]",nx="[object Boolean]",ix="[object Date]",rx="[object Error]",Sf="[object Function]",sx="[object GeneratorFunction]",ox="[object Map]",ax="[object Number]",Ef="[object Object]",cx="[object RegExp]",lx="[object Set]",ux="[object String]",hx="[object Symbol]",dx="[object WeakMap]",fx="[object ArrayBuffer]",px="[object DataView]",mx="[object Float32Array]",gx="[object Float64Array]",_x="[object Int8Array]",vx="[object Int16Array]",yx="[object Int32Array]",xx="[object Uint8Array]",bx="[object Uint8ClampedArray]",Sx="[object Uint16Array]",Ex="[object Uint32Array]",Zt={};Zt[bf]=Zt[tx]=Zt[fx]=Zt[px]=Zt[nx]=Zt[ix]=Zt[mx]=Zt[gx]=Zt[_x]=Zt[vx]=Zt[yx]=Zt[ox]=Zt[ax]=Zt[Ef]=Zt[cx]=Zt[lx]=Zt[ux]=Zt[hx]=Zt[xx]=Zt[bx]=Zt[Sx]=Zt[Ex]=!0,Zt[rx]=Zt[Sf]=Zt[dx]=!1;function Da(o,l,d,y,M,D){var z,K=l&Qy,Q=l&Jy,ae=l&ex;if(d&&(z=M?d(o,y,M,D):d(o)),z!==void 0)return z;if(!We(o))return o;var ye=be(o);if(ye){if(z=ay(o),!K)return d_(o,z)}else{var xe=wo(o),Ce=xe==Sf||xe==sx;if(Pa(o))return I0(o,K);if(xe==Ef||xe==bf||Ce&&!M){if(z=Q||Ce?{}:Hy(o),!K)return Q?W0(o,P0(z,o)):z0(o,A0(z,o))}else{if(!Zt[xe])return M?o:{};z=ky(o,xe,K)}}D||(D=new To);var et=D.get(o);if(et)return et;D.set(o,z),Zy(o)?o.forEach(function(Mt){z.add(Da(Mt,l,d,Mt,o,D))}):Xy(o)&&o.forEach(function(Mt,_t){z.set(_t,Da(Mt,l,d,_t,o,D))});var je=ae?Q?Y0:Gl:Q?Ul:Mo,vt=ye?void 0:je(o);return p_(vt||o,function(Mt,_t){vt&&(_t=Mt,Mt=o[_t]),vo(z,_t,Da(Mt,l,d,_t,o,D))}),z}var Mx=Da,Tx=1,wx=4;function Ax(o){return Mx(o,Tx|wx)}var Rx=Ax,Px="__lodash_hash_undefined__";function Cx(o){return this.__data__.set(o,Px),this}var Dx=Cx;function Ix(o){return this.__data__.has(o)}var Lx=Ix;function Ia(o){var l=-1,d=o==null?0:o.length;for(this.__data__=new ms;++l<d;)this.add(o[l])}Ia.prototype.add=Ia.prototype.push=Dx,Ia.prototype.has=Lx;var Fx=Ia;function Nx(o,l){for(var d=-1,y=o==null?0:o.length;++d<y;)if(l(o[d],d,o))return!0;return!1}var Ox=Nx;function Ux(o,l){return o.has(l)}var Bx=Ux,kx=1,zx=2;function Hx(o,l,d,y,M,D){var z=d&kx,K=o.length,Q=l.length;if(K!=Q&&!(z&&Q>K))return!1;var ae=D.get(o),ye=D.get(l);if(ae&&ye)return ae==l&&ye==o;var xe=-1,Ce=!0,et=d&zx?new Fx:void 0;for(D.set(o,l),D.set(l,o);++xe<K;){var je=o[xe],vt=l[xe];if(y)var Mt=z?y(vt,je,xe,l,o,D):y(je,vt,xe,o,l,D);if(Mt!==void 0){if(Mt)continue;Ce=!1;break}if(et){if(!Ox(l,function(_t,Nt){if(!Bx(et,Nt)&&(je===_t||M(je,_t,d,y,D)))return et.push(Nt)})){Ce=!1;break}}else if(!(je===vt||M(je,vt,d,y,D))){Ce=!1;break}}return D.delete(o),D.delete(l),Ce}var Mf=Hx;function Vx(o){var l=-1,d=Array(o.size);return o.forEach(function(y,M){d[++l]=[M,y]}),d}var Gx=Vx;function Wx(o){var l=-1,d=Array(o.size);return o.forEach(function(y){d[++l]=y}),d}var jx=Wx,Xx=1,qx=2,Yx="[object Boolean]",Kx="[object Date]",$x="[object Error]",Zx="[object Map]",Qx="[object Number]",Jx="[object RegExp]",eb="[object Set]",tb="[object String]",nb="[object Symbol]",ib="[object ArrayBuffer]",rb="[object DataView]",Tf=Se?Se.prototype:void 0,Yl=Tf?Tf.valueOf:void 0;function sb(o,l,d,y,M,D,z){switch(d){case rb:if(o.byteLength!=l.byteLength||o.byteOffset!=l.byteOffset)return!1;o=o.buffer,l=l.buffer;case ib:return!(o.byteLength!=l.byteLength||!D(new Ca(o),new Ca(l)));case Yx:case Kx:case Qx:return wn(+o,+l);case $x:return o.name==l.name&&o.message==l.message;case Jx:case tb:return o==l+"";case Zx:var K=Gx;case eb:var Q=y&Xx;if(K||(K=jx),o.size!=l.size&&!Q)return!1;var ae=z.get(o);if(ae)return ae==l;y|=qx,z.set(o,l);var ye=Mf(K(o),K(l),y,M,D,z);return z.delete(o),ye;case nb:if(Yl)return Yl.call(o)==Yl.call(l)}return!1}var ob=sb,ab=1,cb=Object.prototype,lb=cb.hasOwnProperty;function ub(o,l,d,y,M,D){var z=d&ab,K=Gl(o),Q=K.length,ae=Gl(l),ye=ae.length;if(Q!=ye&&!z)return!1;for(var xe=Q;xe--;){var Ce=K[xe];if(!(z?Ce in l:lb.call(l,Ce)))return!1}var et=D.get(o),je=D.get(l);if(et&&je)return et==l&&je==o;var vt=!0;D.set(o,l),D.set(l,o);for(var Mt=z;++xe<Q;){Ce=K[xe];var _t=o[Ce],Nt=l[Ce];if(y)var In=z?y(Nt,_t,Ce,l,o,D):y(_t,Nt,Ce,o,l,D);if(!(In===void 0?_t===Nt||M(_t,Nt,d,y,D):In)){vt=!1;break}Mt||(Mt=Ce=="constructor")}if(vt&&!Mt){var qn=o.constructor,Ln=l.constructor;qn!=Ln&&"constructor"in o&&"constructor"in l&&!(typeof qn=="function"&&qn instanceof qn&&typeof Ln=="function"&&Ln instanceof Ln)&&(vt=!1)}return D.delete(o),D.delete(l),vt}var hb=ub,db=1,wf="[object Arguments]",Af="[object Array]",La="[object Object]",fb=Object.prototype,Rf=fb.hasOwnProperty;function pb(o,l,d,y,M,D){var z=be(o),K=be(l),Q=z?Af:wo(o),ae=K?Af:wo(l);Q=Q==wf?La:Q,ae=ae==wf?La:ae;var ye=Q==La,xe=ae==La,Ce=Q==ae;if(Ce&&Pa(o)){if(!Pa(l))return!1;z=!0,ye=!1}if(Ce&&!ye)return D||(D=new To),z||Wd(o)?Mf(o,l,d,y,M,D):ob(o,l,Q,d,y,M,D);if(!(d&db)){var et=ye&&Rf.call(o,"__wrapped__"),je=xe&&Rf.call(l,"__wrapped__");if(et||je){var vt=et?o.value():o,Mt=je?l.value():l;return D||(D=new To),M(vt,Mt,d,y,D)}}return Ce?(D||(D=new To),hb(o,l,d,y,M,D)):!1}var mb=pb;function Pf(o,l,d,y,M){return o===l?!0:o==null||l==null||!ce(o)&&!ce(l)?o!==o&&l!==l:mb(o,l,d,y,Pf,M)}var Cf=Pf,gb=1,_b=2;function vb(o,l,d,y){var M=d.length,D=M,z=!y;if(o==null)return!D;for(o=Object(o);M--;){var K=d[M];if(z&&K[2]?K[1]!==o[K[0]]:!(K[0]in o))return!1}for(;++M<D;){K=d[M];var Q=K[0],ae=o[Q],ye=K[1];if(z&&K[2]){if(ae===void 0&&!(Q in o))return!1}else{var xe=new To;if(y)var Ce=y(ae,ye,Q,o,l,xe);if(!(Ce===void 0?Cf(ye,ae,gb|_b,y,xe):Ce))return!1}}return!0}var yb=vb;function xb(o){return o===o&&!We(o)}var Df=xb;function bb(o){for(var l=Mo(o),d=l.length;d--;){var y=l[d],M=o[y];l[d]=[y,M,Df(M)]}return l}var Sb=bb;function Eb(o,l){return function(d){return d==null?!1:d[o]===l&&(l!==void 0||o in Object(d))}}var If=Eb;function Mb(o){var l=Sb(o);return l.length==1&&l[0][2]?If(l[0][0],l[0][1]):function(d){return d===o||yb(d,o,l)}}var Tb=Mb;function wb(o,l){return o!=null&&l in Object(o)}var Ab=wb;function Rb(o,l,d){l=Dr(l,o);for(var y=-1,M=l.length,D=!1;++y<M;){var z=mi(l[y]);if(!(D=o!=null&&d(o,z)))break;o=o[z]}return D||++y!=M?D:(M=o==null?0:o.length,!!M&&Ll(M)&&yo(z,M)&&(be(o)||Bd(o)))}var Pb=Rb;function Cb(o,l){return o!=null&&Pb(o,l,Ab)}var Db=Cb,Ib=1,Lb=2;function Fb(o,l){return _e(o)&&Df(l)?If(mi(o),l):function(d){var y=Ui(d,o);return y===void 0&&y===l?Db(d,o):Cf(l,y,Ib|Lb)}}var Nb=Fb;function Ob(o){return function(l){return l==null?void 0:l[o]}}var Lf=Ob;function Ub(o){return function(l){return _s(l,o)}}var Bb=Ub;function kb(o){return _e(o)?Lf(mi(o)):Bb(o)}var zb=kb;function Hb(o){return typeof o=="function"?o:o==null?Aa:typeof o=="object"?be(o)?Nb(o[0],o[1]):Tb(o):zb(o)}var Vb=Hb;function Gb(o){return function(l,d,y){for(var M=-1,D=Object(l),z=y(l),K=z.length;K--;){var Q=z[o?K:++M];if(d(D[Q],Q,D)===!1)break}return l}}var Wb=Gb,jb=Wb(),Xb=jb;function qb(o,l){return o&&Xb(o,l,Mo)}var Yb=qb,Kb=function(){return me.Date.now()},Kl=Kb,$b="Expected a function",Zb=Math.max,Qb=Math.min;function Jb(o,l,d){var y,M,D,z,K,Q,ae=0,ye=!1,xe=!1,Ce=!0;if(typeof o!="function")throw new TypeError($b);l=S(l)||0,We(d)&&(ye=!!d.leading,xe="maxWait"in d,D=xe?Zb(S(d.maxWait)||0,l):D,Ce="trailing"in d?!!d.trailing:Ce);function et(Yt){var Fn=y,ii=M;return y=M=void 0,ae=Yt,z=o.apply(ii,Fn),z}function je(Yt){return ae=Yt,K=setTimeout(_t,l),ye?et(Yt):z}function vt(Yt){var Fn=Yt-Q,ii=Yt-ae,Ai=l-Fn;return xe?Qb(Ai,D-ii):Ai}function Mt(Yt){var Fn=Yt-Q,ii=Yt-ae;return Q===void 0||Fn>=l||Fn<0||xe&&ii>=D}function _t(){var Yt=Kl();if(Mt(Yt))return Nt(Yt);K=setTimeout(_t,vt(Yt))}function Nt(Yt){return K=void 0,Ce&&y?et(Yt):(y=M=void 0,z)}function In(){K!==void 0&&clearTimeout(K),ae=0,y=Q=M=K=void 0}function qn(){return K===void 0?z:Nt(Kl())}function Ln(){var Yt=Kl(),Fn=Mt(Yt);if(y=arguments,M=this,Q=Yt,Fn){if(K===void 0)return je(Q);if(xe)return clearTimeout(K),K=setTimeout(_t,l),et(Q)}return K===void 0&&(K=setTimeout(_t,l)),z}return Ln.cancel=In,Ln.flush=qn,Ln}var eS=Jb;function tS(o){var l=o==null?0:o.length;return l?o[l-1]:void 0}var nS=tS;function iS(o,l){return l.length<2?o:_s(o,Kd(l,0,-1))}var rS=iS;function sS(o){return typeof o=="number"&&o==Rn(o)}var oS=sS;function aS(o,l){var d={};return l=Vb(l),Yb(o,function(y,M,D){Bi(d,M,l(y,M,D))}),d}var cS=aS;function lS(o,l){return l=Dr(l,o),o=rS(o,l),o==null||delete o[mi(nS(l))]}var uS=lS,hS=9007199254740991,dS=Math.floor;function fS(o,l){var d="";if(!o||l<1||l>hS)return d;do l%2&&(d+=o),l=dS(l/2),l&&(o+=o);while(l);return d}var Ff=fS,pS=Lf("length"),mS=pS,Nf="\\ud800-\\udfff",gS="\\u0300-\\u036f",_S="\\ufe20-\\ufe2f",vS="\\u20d0-\\u20ff",yS=gS+_S+vS,xS="\\ufe0e\\ufe0f",bS="["+Nf+"]",$l="["+yS+"]",Zl="\\ud83c[\\udffb-\\udfff]",SS="(?:"+$l+"|"+Zl+")",Of="[^"+Nf+"]",Uf="(?:\\ud83c[\\udde6-\\uddff]){2}",Bf="[\\ud800-\\udbff][\\udc00-\\udfff]",ES="\\u200d",kf=SS+"?",zf="["+xS+"]?",MS="(?:"+ES+"(?:"+[Of,Uf,Bf].join("|")+")"+zf+kf+")*",TS=zf+kf+MS,wS="(?:"+[Of+$l+"?",$l,Uf,Bf,bS].join("|")+")",Hf=RegExp(Zl+"(?="+Zl+")|"+wS+TS,"g");function AS(o){for(var l=Hf.lastIndex=0;Hf.test(o);)++l;return l}var RS=AS;function PS(o){return kl(o)?RS(o):mS(o)}var Vf=PS,CS=Math.ceil;function DS(o,l){l=l===void 0?" ":fa(l);var d=l.length;if(d<2)return d?Ff(l,o):l;var y=Ff(l,CS(o/Vf(l)));return kl(l)?Bv(h0(y),0,o).join(""):y.slice(0,o)}var IS=DS;function LS(o,l,d){o=gs(o),l=Rn(l);var y=l?Vf(o):0;return l&&y<l?IS(l-y,d)+o:o}var Ao=LS;function FS(o,l){return o==null?!0:uS(o,l)}var Gf=FS,NS=5*1e3,OS=class{constructor(o){b(this,"_cache",new ar),b(this,"_keepHotUntapDebounce"),de(this,o)}get type(){return"Theatre_SheetObject_PublicAPI"}get props(){return q(this).propsP}get sheet(){return q(this).sheet.publicApi}get project(){return q(this).sheet.project.publicApi}get address(){return g({},q(this).address)}_valuesPrism(){return this._cache.get("_valuesPrism",()=>{const o=q(this);return(0,bo.prism)(()=>(0,bo.val)(o.getValues().getValue()))})}onValuesChange(o,l){return Su(this._valuesPrism(),o,l)}get value(){const o=this._valuesPrism();{if(!o.isHot){this._keepHotUntapDebounce!=null&&this._keepHotUntapDebounce.flush();const l=o.keepHot();this._keepHotUntapDebounce=eS(()=>{l(),this._keepHotUntapDebounce=void 0},NS)}this._keepHotUntapDebounce&&this._keepHotUntapDebounce()}return o.getValue()}set initialValue(o){q(this).setInitialValue(o)}};function US(o){const l=new WeakMap;return d=>(l.has(d)||l.set(d,o(d)),l.get(d))}function Fa(o){return o.type==="compound"||o.type==="enum"}function Ql(o,l){if(!o)return;const[d,...y]=l;if(d===void 0)return o;if(!Fa(o))return;const M=o.type==="enum"?o.cases[d]:o.props[d];return Ql(M,y)}function BS(o){return!Fa(o)}var kS=class{constructor(o,l,d){this.sheet=o,this.template=l,this.nativeObject=d,b(this,"$$isPointerToPrismProvider",!0),b(this,"address"),b(this,"publicApi"),b(this,"_initialValue",new Ht.Atom({})),b(this,"_cache",new ar),b(this,"_logger"),b(this,"_internalUtilCtx"),this._logger=o._logger.named("SheetObject",l.address.objectKey),this._logger._trace("creating object"),this._internalUtilCtx={logger:this._logger.utilFor.internal()},this.address=x(g({},l.address),{sheetInstanceId:o.address.sheetInstanceId}),this.publicApi=new OS(this)}get type(){return"Theatre_SheetObject"}getValues(){return this._cache.get("getValues()",()=>(0,Ht.prism)(()=>{const o=(0,Ht.val)(this.template.getDefaultValues()),l=(0,Ht.val)(this._initialValue.pointer),d=Ht.prism.memo("withInitialCache",()=>new WeakMap,[]),y=Fr(o,l,d),M=(0,Ht.val)(this.template.getStaticValues()),D=Ht.prism.memo("withStatics",()=>new WeakMap,[]);let K=Fr(y,M,D),Q;{const ye=Ht.prism.memo("seq",()=>this.getSequencedValues(),[]),xe=Ht.prism.memo("withSeqsCache",()=>new WeakMap,[]);Q=(0,Ht.val)((0,Ht.val)(ye)),K=Fr(K,Q,xe)}return Sa("finalAtom",K).pointer}))}getValueByPointer(o){const l=(0,Ht.val)(this.getValues()),{path:d}=(0,Ht.getPointerParts)(o);return(0,Ht.val)(Nr(l,d))}pointerToPrism(o){const{path:l}=(0,Ht.getPointerParts)(o);return(0,Ht.prism)(()=>{const d=(0,Ht.val)(this.getValues());return(0,Ht.val)(Nr(d,l))})}getSequencedValues(){return(0,Ht.prism)(()=>{const o=Ht.prism.memo("tracksToProcess",()=>this.template.getArrayOfValidSequenceTracks(),[]),l=(0,Ht.val)(o),d=new Ht.Atom({}),y=(0,Ht.val)(this.template.configPointer);return Ht.prism.effect("processTracks",()=>{const M=[];for(const{trackId:D,pathToProp:z}of l){const K=this._trackIdToPrism(D),Q=Ql(y,z),ae=Q.deserializeAndSanitize,ye=Q.interpolate,xe=()=>{const et=K.getValue();if(!et)return d.setByPointer(Nt=>Nr(Nt,z),void 0);const je=ae(et.left),vt=je===void 0?Q.default:je;if(et.right===void 0)return d.setByPointer(Nt=>Nr(Nt,z),vt);const Mt=ae(et.right),_t=Mt===void 0?Q.default:Mt;return d.setByPointer(Nt=>Nr(Nt,z),ye(vt,_t,et.progression))},Ce=K.onStale(xe);xe(),M.push(Ce)}return()=>{for(const D of M)D()}},[y,...l]),d.pointer})}_trackIdToPrism(o){const l=this.template.project.pointers.historic.sheetsById[this.address.sheetId].sequence.tracksByObject[this.address.objectKey].trackData[o],d=this.sheet.getSequence().positionPrism;return Ml(this._internalUtilCtx,l,d)}get propsP(){return this._cache.get("propsP",()=>(0,Ht.pointer)({root:this,path:[]}))}validateValue(o,l){}setInitialValue(o){this.validateValue(this.propsP,o),this._initialValue.set(o)}};function Qt(o){return function(d,y){return o(d,y())}}var ei={_hmm:ti(524),_todo:ti(522),_error:ti(521),errorDev:ti(529),errorPublic:ti(545),_kapow:ti(268),_warn:ti(265),warnDev:ti(273),warnPublic:ti(289),_debug:ti(137),debugDev:ti(145),_trace:ti(73),traceDev:ti(81)};function ti(o){return Object.freeze({audience:kr(o,8)?"internal":kr(o,16)?"dev":"public",category:kr(o,4)?"troubleshooting":kr(o,2)?"todo":"general",level:kr(o,512)?512:kr(o,256)?256:kr(o,128)?128:64})}function kr(o,l){return(o&l)===l}function Jt(o,l){return((l&32)===32?!0:(l&16)===16?o.dev:(l&8)===8?o.internal:!1)&&o.min<=l}var ki={loggingConsoleStyle:!0,loggerConsoleStyle:!0,includes:Object.freeze({internal:!1,dev:!1,min:256}),filtered:function(){},include:function(){return{}},create:null,creatExt:null,named(o,l,d){return this.create({names:[...o.names,{name:l,key:d}]})},style:{bold:void 0,italic:void 0,cssMemo:new Map([["",""]]),collapseOnRE:/[a-z- ]+/g,color:void 0,collapsed(o){if(o.length<5)return o;const l=o.replace(this.collapseOnRE,"");return this.cssMemo.has(l)||this.cssMemo.set(l,this.css(o)),l},css(o){var l,d,y,M;const D=this.cssMemo.get(o);if(D)return D;let z="color:".concat((d=(l=this.color)==null?void 0:l.call(this,o))!=null?d:"hsl(".concat((o.charCodeAt(0)+o.charCodeAt(o.length-1))%360,", 100%, 60%)"));return(y=this.bold)!=null&&y.test(o)&&(z+=";font-weight:600"),(M=this.italic)!=null&&M.test(o)&&(z+=";font-style:italic"),this.cssMemo.set(o,z),z}}};function Wf(o=console,l={}){const d=x(g({},ki),{includes:g({},ki.includes)}),y={styled:VS.bind(d,o),noStyle:WS.bind(d,o)},M=HS.bind(d);function D(){return d.loggingConsoleStyle&&d.loggerConsoleStyle?y.styled:y.noStyle}return d.create=D(),{configureLogger(z){var K;z==="console"?(d.loggerConsoleStyle=ki.loggerConsoleStyle,d.create=D()):z.type==="console"?(d.loggerConsoleStyle=(K=z.style)!=null?K:ki.loggerConsoleStyle,d.create=D()):z.type==="keyed"?(d.creatExt=Q=>z.keyed(Q.names),d.create=M):z.type==="named"&&(d.creatExt=zS.bind(null,z.named),d.create=M)},configureLogging(z){var K,Q,ae,ye,xe;d.includes.dev=(K=z.dev)!=null?K:ki.includes.dev,d.includes.internal=(Q=z.internal)!=null?Q:ki.includes.internal,d.includes.min=(ae=z.min)!=null?ae:ki.includes.min,d.include=(ye=z.include)!=null?ye:ki.include,d.loggingConsoleStyle=(xe=z.consoleStyle)!=null?xe:ki.loggingConsoleStyle,d.create=D()},getLogger(){return d.create({names:[]})}}}function zS(o,l){const d=[];for(let{name:y,key:M}of l.names)d.push(M==null?y:"".concat(y," (").concat(M,")"));return o(d)}function HS(o){const l=g(g({},this.includes),this.include(o)),d=this.filtered,y=this.named.bind(this,o),M=this.creatExt(o),D=Jt(l,524),z=Jt(l,522),K=Jt(l,521),Q=Jt(l,529),ae=Jt(l,545),ye=Jt(l,265),xe=Jt(l,268),Ce=Jt(l,273),et=Jt(l,289),je=Jt(l,137),vt=Jt(l,145),Mt=Jt(l,73),_t=Jt(l,81),Nt=D?M.error.bind(M,ei._hmm):d.bind(o,524),In=z?M.error.bind(M,ei._todo):d.bind(o,522),qn=K?M.error.bind(M,ei._error):d.bind(o,521),Ln=Q?M.error.bind(M,ei.errorDev):d.bind(o,529),Yt=ae?M.error.bind(M,ei.errorPublic):d.bind(o,545),Fn=xe?M.warn.bind(M,ei._kapow):d.bind(o,268),ii=ye?M.warn.bind(M,ei._warn):d.bind(o,265),Ai=Ce?M.warn.bind(M,ei.warnDev):d.bind(o,273),jr=et?M.warn.bind(M,ei.warnPublic):d.bind(o,273),Xr=je?M.debug.bind(M,ei._debug):d.bind(o,137),qr=vt?M.debug.bind(M,ei.debugDev):d.bind(o,145),Yr=Mt?M.trace.bind(M,ei._trace):d.bind(o,73),Kr=_t?M.trace.bind(M,ei.traceDev):d.bind(o,81),hn={_hmm:Nt,_todo:In,_error:qn,errorDev:Ln,errorPublic:Yt,_kapow:Fn,_warn:ii,warnDev:Ai,warnPublic:jr,_debug:Xr,debugDev:qr,_trace:Yr,traceDev:Kr,lazy:{_hmm:D?Qt(Nt):Nt,_todo:z?Qt(In):In,_error:K?Qt(qn):qn,errorDev:Q?Qt(Ln):Ln,errorPublic:ae?Qt(Yt):Yt,_kapow:xe?Qt(Fn):Fn,_warn:ye?Qt(ii):ii,warnDev:Ce?Qt(Ai):Ai,warnPublic:et?Qt(jr):jr,_debug:je?Qt(Xr):Xr,debugDev:vt?Qt(qr):qr,_trace:Mt?Qt(Yr):Yr,traceDev:_t?Qt(Kr):Kr},named:y,utilFor:{internal(){return{debug:hn._debug,error:hn._error,warn:hn._warn,trace:hn._trace,named(ri,en){return hn.named(ri,en).utilFor.internal()}}},dev(){return{debug:hn.debugDev,error:hn.errorDev,warn:hn.warnDev,trace:hn.traceDev,named(ri,en){return hn.named(ri,en).utilFor.dev()}}},public(){return{error:hn.errorPublic,warn:hn.warnPublic,debug(ri,en){hn._warn('(public "debug" filtered out) '.concat(ri),en)},trace(ri,en){hn._warn('(public "trace" filtered out) '.concat(ri),en)},named(ri,en){return hn.named(ri,en).utilFor.public()}}}}};return hn}function VS(o,l){const d=g(g({},this.includes),this.include(l)),y=[];let M="";for(let Q=0;Q<l.names.length;Q++){const{name:ae,key:ye}=l.names[Q];if(M+=" %c".concat(ae),y.push(this.style.css(ae)),ye!=null){const xe="%c#".concat(ye);M+=xe,y.push(this.style.css(xe))}}const D=this.filtered,z=this.named.bind(this,l),K=[M,...y];return jf(D,l,d,o,K,GS(K),z)}function GS(o){const l=o.slice(0);for(let d=1;d<l.length;d++)l[d]+=";background-color:#e0005a;padding:2px;color:white";return l}function WS(o,l){const d=g(g({},this.includes),this.include(l));let y="";for(let K=0;K<l.names.length;K++){const{name:Q,key:ae}=l.names[K];y+=" ".concat(Q),ae!=null&&(y+="#".concat(ae))}const M=this.filtered,D=this.named.bind(this,l),z=[y];return jf(M,l,d,o,z,z,D)}function jf(o,l,d,y,M,D,z){const K=Jt(d,524),Q=Jt(d,522),ae=Jt(d,521),ye=Jt(d,529),xe=Jt(d,545),Ce=Jt(d,265),et=Jt(d,268),je=Jt(d,273),vt=Jt(d,289),Mt=Jt(d,137),_t=Jt(d,145),Nt=Jt(d,73),In=Jt(d,81),qn=K?y.error.bind(y,...M):o.bind(l,524),Ln=Q?y.error.bind(y,...M):o.bind(l,522),Yt=ae?y.error.bind(y,...M):o.bind(l,521),Fn=ye?y.error.bind(y,...M):o.bind(l,529),ii=xe?y.error.bind(y,...M):o.bind(l,545),Ai=et?y.warn.bind(y,...D):o.bind(l,268),jr=Ce?y.warn.bind(y,...M):o.bind(l,265),Xr=je?y.warn.bind(y,...M):o.bind(l,273),qr=vt?y.warn.bind(y,...M):o.bind(l,273),Yr=Mt?y.info.bind(y,...M):o.bind(l,137),Kr=_t?y.info.bind(y,...M):o.bind(l,145),hn=Nt?y.debug.bind(y,...M):o.bind(l,73),ri=In?y.debug.bind(y,...M):o.bind(l,81),en={_hmm:qn,_todo:Ln,_error:Yt,errorDev:Fn,errorPublic:ii,_kapow:Ai,_warn:jr,warnDev:Xr,warnPublic:qr,_debug:Yr,debugDev:Kr,_trace:hn,traceDev:ri,lazy:{_hmm:K?Qt(qn):qn,_todo:Q?Qt(Ln):Ln,_error:ae?Qt(Yt):Yt,errorDev:ye?Qt(Fn):Fn,errorPublic:xe?Qt(ii):ii,_kapow:et?Qt(Ai):Ai,_warn:Ce?Qt(jr):jr,warnDev:je?Qt(Xr):Xr,warnPublic:vt?Qt(qr):qr,_debug:Mt?Qt(Yr):Yr,debugDev:_t?Qt(Kr):Kr,_trace:Nt?Qt(hn):hn,traceDev:In?Qt(ri):ri},named:z,utilFor:{internal(){return{debug:en._debug,error:en._error,warn:en._warn,trace:en._trace,named(Vi,Gi){return en.named(Vi,Gi).utilFor.internal()}}},dev(){return{debug:en.debugDev,error:en.errorDev,warn:en.warnDev,trace:en.traceDev,named(Vi,Gi){return en.named(Vi,Gi).utilFor.dev()}}},public(){return{error:en.errorPublic,warn:en.warnPublic,debug(Vi,Gi){en._warn('(public "debug" filtered out) '.concat(Vi),Gi)},trace(Vi,Gi){en._warn('(public "trace" filtered out) '.concat(Vi),Gi)},named(Vi,Gi){return en.named(Vi,Gi).utilFor.public()}}}}};return en}var Xf=Wf(console,{});Xf.configureLogging({dev:!0,min:64});var Na=Xf.getLogger().named("Theatre.js (default logger)").utilFor.dev(),qf=new WeakMap;function jS(o){const l=qf.get(o);if(l)return l;const d=new Map;return qf.set(o,d),Yf([],o,d),d}function Yf(o,l,d){for(const[y,M]of Object.entries(l.props))if(!Fa(M)){const D=[...o,y];d.set(JSON.stringify(D),d.size),Kf(D,M,d)}for(const[y,M]of Object.entries(l.props))if(Fa(M)){const D=[...o,y];d.set(JSON.stringify(D),d.size),Kf(D,M,d)}}function Kf(o,l,d){if(l.type==="compound")Yf(o,l,d);else{if(l.type==="enum")throw new Error("Enums aren't supported yet");d.set(JSON.stringify(o),d.size)}}function $f(o){return typeof o=="object"&&o!==null&&Object.keys(o).length===0}var XS=class{constructor(o,l,d,y,M){this.sheetTemplate=o,b(this,"address"),b(this,"type","Theatre_SheetObjectTemplate"),b(this,"_config"),b(this,"_temp_actions_atom"),b(this,"_cache",new ar),b(this,"project"),b(this,"pointerToSheetState"),b(this,"pointerToStaticOverrides"),this.address=x(g({},o.address),{objectKey:l}),this._config=new fn.Atom(y),this._temp_actions_atom=new fn.Atom(M),this.project=o.project,this.pointerToSheetState=this.sheetTemplate.project.pointers.historic.sheetsById[this.address.sheetId],this.pointerToStaticOverrides=this.pointerToSheetState.staticOverrides.byObject[this.address.objectKey]}get staticConfig(){return this._config.get()}get configPointer(){return this._config.pointer}get _temp_actions(){return this._temp_actions_atom.get()}get _temp_actionsPointer(){return this._temp_actions_atom.pointer}createInstance(o,l,d){return this._config.set(d),new kS(o,this,l)}reconfigure(o){this._config.set(o)}_temp_setActions(o){this._temp_actions_atom.set(o)}getDefaultValues(){return this._cache.get("getDefaultValues()",()=>(0,fn.prism)(()=>{const o=(0,fn.val)(this.configPointer);return Sl(o)}))}getStaticValues(){return this._cache.get("getStaticValues",()=>(0,fn.prism)(()=>{var o;const l=(o=(0,fn.val)(this.pointerToStaticOverrides))!=null?o:{};return(0,fn.val)(this.configPointer).deserializeAndSanitize(l)||{}}))}getArrayOfValidSequenceTracks(){return this._cache.get("getArrayOfValidSequenceTracks",()=>(0,fn.prism)(()=>{const o=this.project.pointers.historic.sheetsById[this.address.sheetId],l=(0,fn.val)(o.sequence.tracksByObject[this.address.objectKey].trackIdByPropPath);if(!l)return re;const d=[];if(!l)return re;const y=(0,fn.val)(this.configPointer),M=Object.entries(l);for(const[z,K]of M){const Q=qS(z);if(!Q)continue;const ae=Ql(y,Q);ae&&BS(ae)&&d.push({pathToProp:Q,trackId:K})}const D=jS(y);return d.sort((z,K)=>{const Q=z.pathToProp,ae=K.pathToProp,ye=D.get(JSON.stringify(Q)),xe=D.get(JSON.stringify(ae));return ye>xe?1:-1}),d.length===0?re:d}))}getMapOfValidSequenceTracks_forStudio(){return this._cache.get("getMapOfValidSequenceTracks_forStudio",()=>(0,fn.prism)(()=>{const o=(0,fn.val)(this.getArrayOfValidSequenceTracks());let l={};for(const{pathToProp:d,trackId:y}of o)ys(l,d,y);return l}))}getStaticButNotSequencedOverrides(){return this._cache.get("getStaticButNotSequencedOverrides",()=>(0,fn.prism)(()=>{const o=(0,fn.val)(this.getStaticValues()),l=(0,fn.val)(this.getArrayOfValidSequenceTracks()),d=Rx(o);for(const{pathToProp:y}of l){Gf(d,y);let M=y.slice(0,-1);for(;M.length>0;){const D=ma(d,M);if(!$f(D))break;Gf(d,M),M=M.slice(0,-1)}}if(!$f(d))return d}))}getDefaultsAtPointer(o){const{path:l}=(0,fn.getPointerParts)(o),d=this.getDefaultValues().getValue();return ma(d,l)}};function qS(o){try{return JSON.parse(o)}catch{Na.warn("property ".concat(JSON.stringify(o)," cannot be parsed. Skipping."));return}}var Zf=mn(),YS=US(o=>JSON.stringify(o));A(O());var KS=class extends Error{},Ro=class extends KS{},Qf=mn(),$S=mn(),ZS=mn(),bn=mn();function lr(){let o,l;const d=new Promise((M,D)=>{o=z=>{M(z),y.status="resolved"},l=z=>{D(z),y.status="rejected"}}),y={resolve:o,reject:l,promise:d,status:"pending"};return y}var QS=()=>{},Oa=QS,JS=mn(),eE=class{constructor(){b(this,"_stopPlayCallback",Oa),b(this,"_state",new JS.Atom({position:0,playing:!1})),b(this,"statePointer"),this.statePointer=this._state.pointer}destroy(){}pause(){this._stopPlayCallback(),this.playing=!1,this._stopPlayCallback=Oa}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.setByPointer(l=>l.position,o)}getCurrentPosition(){return this._state.get().position}get playing(){return this._state.get().playing}set playing(o){this._state.setByPointer(l=>l.playing,o)}play(o,l,d,y,M){this.playing&&this.pause(),this.playing=!0;const D=l[1]-l[0];{const Ce=this.getCurrentPosition();Ce<l[0]||Ce>l[1]?y==="normal"||y==="alternate"?this._updatePositionInState(l[0]):(y==="reverse"||y==="alternateReverse")&&this._updatePositionInState(l[1]):y==="normal"||y==="alternate"?Ce===l[1]&&this._updatePositionInState(l[0]):Ce===l[0]&&this._updatePositionInState(l[1])}const z=lr(),K=M.time,Q=D*o;let ae=this.getCurrentPosition()-l[0];(y==="reverse"||y==="alternateReverse")&&(ae=l[1]-this.getCurrentPosition());const ye=Ce=>{const je=Math.max(Ce-K,0)/1e3,vt=Math.min(je*d+ae,Q);if(vt!==Q){const Mt=Math.floor(vt/D);let _t=vt/D%1*D;if(y!=="normal")if(y==="reverse")_t=D-_t;else{const Nt=Mt%2===0;y==="alternate"?Nt||(_t=D-_t):Nt&&(_t=D-_t)}this._updatePositionInState(_t+l[0]),xe()}else{if(y==="normal")this._updatePositionInState(l[1]);else if(y==="reverse")this._updatePositionInState(l[0]);else{const Mt=(o-1)%2===0;y==="alternate"?Mt?this._updatePositionInState(l[1]):this._updatePositionInState(l[0]):Mt?this._updatePositionInState(l[0]):this._updatePositionInState(l[1])}this.playing=!1,z.resolve(!0)}};this._stopPlayCallback=()=>{M.offThisOrNextTick(ye),M.offNextTick(ye),this.playing&&z.resolve(!1)};const xe=()=>M.onNextTick(ye);return M.onThisOrNextTick(ye),z.promise}playDynamicRange(o,l){this.playing&&this.pause(),this.playing=!0;const d=lr(),y=o.keepHot();d.promise.then(y,y);let M=l.time;const D=K=>{const Q=Math.max(K-M,0);M=K;const ae=Q/1e3,ye=this.getCurrentPosition(),xe=o.getValue();if(ye<xe[0]||ye>xe[1])this.gotoPosition(xe[0]);else{let Ce=ye+ae;Ce>xe[1]&&(Ce=xe[0]+(Ce-xe[1])),this.gotoPosition(Ce)}z()};this._stopPlayCallback=()=>{l.offThisOrNextTick(D),l.offNextTick(D),d.resolve(!1)};const z=()=>l.onNextTick(D);return l.onThisOrNextTick(D),d.promise}},tE=mn(),nE="__TheatreJS_StudioBundle",Jl="__TheatreJS_CoreBundle",iE="__TheatreJS_Notifications",Ua=o=>(...l)=>{var d;switch(o){case"success":{Na.debug(l.slice(0,2).join(`
`));break}case"info":{Na.debug(l.slice(0,2).join(`
`));break}case"warning":{Na.warn(l.slice(0,2).join(`
`));break}}return typeof window<"u"?(d=window[iE])==null?void 0:d.notify[o](...l):void 0},Es={warning:Ua("warning"),success:Ua("success"),info:Ua("info"),error:Ua("error")};typeof window<"u"&&(window.addEventListener("error",o=>{Es.error("An error occurred","<pre>".concat(o.message,`</pre>

See **console** for details.`))}),window.addEventListener("unhandledrejection",o=>{Es.error("An error occurred","<pre>".concat(o.reason,`</pre>

See **console** for details.`))}));var rE=class{constructor(o,l,d){this._decodedBuffer=o,this._audioContext=l,this._nodeDestination=d,b(this,"_mainGain"),b(this,"_state",new tE.Atom({position:0,playing:!1})),b(this,"statePointer"),b(this,"_stopPlayCallback",Oa),this.statePointer=this._state.pointer,this._mainGain=this._audioContext.createGain(),this._mainGain.connect(this._nodeDestination)}playDynamicRange(o,l){const d=lr();this._playing&&this.pause(),this._playing=!0;let y;const M=()=>{y==null||y(),y=this._loopInRange(o.getValue(),l).stop},D=o.onStale(M);return M(),this._stopPlayCallback=()=>{y==null||y(),D(),d.resolve(!1)},d.promise}_loopInRange(o,l){let y=this.getCurrentPosition();const M=o[1]-o[0];y<o[0]||y>o[1]?this._updatePositionInState(o[0]):y===o[1]&&this._updatePositionInState(o[0]),y=this.getCurrentPosition();const D=this._audioContext.createBufferSource();D.buffer=this._decodedBuffer,D.connect(this._mainGain),D.playbackRate.value=1,D.loop=!0,D.loopStart=o[0],D.loopEnd=o[1];const z=l.time;let K=y-o[0];D.start(0,y);const Q=xe=>{let vt=(Math.max(xe-z,0)/1e3*1+K)/M%1*M;this._updatePositionInState(vt+o[0]),ae()},ae=()=>l.onNextTick(Q);return l.onThisOrNextTick(Q),{stop:()=>{D.stop(),D.disconnect(),l.offThisOrNextTick(Q),l.offNextTick(Q)}}}get _playing(){return this._state.get().playing}set _playing(o){this._state.setByPointer(l=>l.playing,o)}destroy(){}pause(){this._stopPlayCallback(),this._playing=!1,this._stopPlayCallback=Oa}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.reduce(l=>x(g({},l),{position:o}))}getCurrentPosition(){return this._state.get().position}play(o,l,d,y,M){this._playing&&this.pause(),this._playing=!0;let D=this.getCurrentPosition();const z=l[1]-l[0];if(y!=="normal")throw new Ro('Audio-controlled sequences can only be played in the "normal" direction. '+"'".concat(y,"' given."));D<l[0]||D>l[1]?this._updatePositionInState(l[0]):D===l[1]&&this._updatePositionInState(l[0]),D=this.getCurrentPosition();const K=lr(),Q=this._audioContext.createBufferSource();Q.buffer=this._decodedBuffer,Q.connect(this._mainGain),Q.playbackRate.value=d,o>1e3&&(Es.warning("Can't play sequences with audio more than 1000 times","The sequence will still play, but only 1000 times. The `iterationCount: ".concat(o,"` provided to `sequence.play()`\nis too high for a sequence with audio.\n\nTo fix this, either set `iterationCount` to a lower value, or remove the audio from the sequence."),[{url:"https://www.theatrejs.com/docs/latest/manual/audio",title:"Using Audio"},{url:"https://www.theatrejs.com/docs/latest/api/core#sequence.attachaudio",title:"Audio API"}]),o=1e3),o>1&&(Q.loop=!0,Q.loopStart=l[0],Q.loopEnd=l[1]);const ae=M.time;let ye=D-l[0];const xe=z*o;Q.start(0,D,xe-ye);const Ce=vt=>{const _t=Math.max(vt-ae,0)/1e3,Nt=Math.min(_t*d+ye,xe);if(Nt!==xe){let In=Nt/z%1*z;this._updatePositionInState(In+l[0]),je()}else this._updatePositionInState(l[1]),this._playing=!1,et(),K.resolve(!0)},et=()=>{Q.stop(),Q.disconnect()};this._stopPlayCallback=()=>{et(),M.offThisOrNextTick(Ce),M.offNextTick(Ce),this._playing&&K.resolve(!1)};const je=()=>M.onNextTick(Ce);return M.onThisOrNextTick(Ce),K.promise}},sE=mn(),Jf=0;function eu(o){var l;const d=z=>{y.tick(z)},y=new sE.Ticker({onActive(){var z;(z=o==null?void 0:o.start)==null||z.call(o)},onDormant(){var z;(z=o==null?void 0:o.stop)==null||z.call(o)}}),M={tick:d,id:Jf++,name:(l=o==null?void 0:o.name)!=null?l:"CustomRafDriver-".concat(Jf),type:"Theatre_RafDriver_PublicAPI"},D={type:"Theatre_RafDriver_PrivateAPI",publicApi:M,ticker:y,start:o==null?void 0:o.start,stop:o==null?void 0:o.stop};return de(M,D),M}function oE(){let o=null;const y=eu({name:"DefaultCoreRafDriver",start:()=>{if(typeof window<"u"){const M=D=>{y.tick(D),o=window.requestAnimationFrame(M)};o=window.requestAnimationFrame(M)}else y.tick(0),setTimeout(()=>y.tick(1),0)},stop:()=>{typeof window<"u"&&o!==null&&window.cancelAnimationFrame(o)}});return y}var Ba;function ep(){return Ba||aE(oE()),Ba}function tp(){return ep().ticker}function aE(o){if(Ba)throw new Error("`setCoreRafDriver()` is already called.");Ba=q(o)}var cE=class{get type(){return"Theatre_Sequence_PublicAPI"}constructor(o){de(this,o)}play(o){const l=q(this);if(l._project.isReady()){const d=o!=null&&o.rafDriver?q(o.rafDriver).ticker:tp();return l.play(o??{},d)}else{const d=lr();return d.resolve(!0),d.promise}}pause(){q(this).pause()}get position(){return q(this).position}set position(o){q(this).position=o}__experimental_getKeyframes(o){return q(this).getKeyframesOfSimpleProp(o)}async attachAudio(o){const{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:M}=await lE(o),D=new rE(y,l,M);return q(this).replacePlaybackController(D),{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:M}}get pointer(){return q(this).pointer}};async function lE(o){function l(){if(o.audioContext)return Promise.resolve(o.audioContext);const ae=new AudioContext;return ae.state==="running"||typeof window>"u"?Promise.resolve(ae):new Promise(ye=>{const xe=()=>{ae.resume().catch(je=>{console.error(je)})},Ce=["mousedown","keydown","touchstart"],et={capture:!0,passive:!1};Ce.forEach(je=>{window.addEventListener(je,xe,et)}),ae.addEventListener("statechange",()=>{ae.state==="running"&&(Ce.forEach(je=>{window.removeEventListener(je,xe,et)}),ye(ae))})})}async function d(){if(o.source instanceof AudioBuffer)return o.source;const ae=lr();if(typeof o.source!="string")throw new Error("Error validating arguments to sequence.attachAudio(). args.source must either be a string or an instance of AudioBuffer.");let ye;try{ye=await fetch(o.source)}catch(je){throw console.error(je),new Error("Could not fetch '".concat(o.source,"'. Network error logged above."))}let xe;try{xe=await ye.arrayBuffer()}catch(je){throw console.error(je),new Error("Could not read '".concat(o.source,"' as an arrayBuffer."))}(await y).decodeAudioData(xe,ae.resolve,ae.reject);let et;try{et=await ae.promise}catch(je){throw console.error(je),new Error("Could not decode ".concat(o.source," as an audio file."))}return et}const y=l(),M=d(),[D,z]=await Promise.all([y,M]),K=o.destinationNode||D.destination,Q=D.createGain();return Q.connect(K),{audioContext:D,decodedBuffer:z,gainNode:Q,destinationNode:K}}var uE=hE("Theatre_SheetObject");function hE(o){return l=>typeof l=="object"&&!!l&&l.type===o}var dE=class{constructor(o,l,d,y,M){this._project=o,this._sheet=l,this._lengthD=d,this._subUnitsPerUnitD=y,b(this,"address"),b(this,"publicApi"),b(this,"_playbackControllerBox"),b(this,"_prismOfStatePointer"),b(this,"_positionD"),b(this,"_positionFormatterD"),b(this,"_playableRangeD"),b(this,"pointer",(0,ZS.pointer)({root:this,path:[]})),b(this,"$$isPointerToPrismProvider",!0),b(this,"_logger"),b(this,"closestGridPosition",D=>{const K=1/this.subUnitsPerUnit;return parseFloat((Math.round(D/K)*K).toFixed(3))}),this._logger=o._logger.named("Sheet",l.address.sheetId).named("Instance",l.address.sheetInstanceId),this.address=x(g({},this._sheet.address),{sequenceName:"default"}),this.publicApi=new cE(this),this._playbackControllerBox=new $S.Atom(M??new eE),this._prismOfStatePointer=(0,bn.prism)(()=>this._playbackControllerBox.prism.getValue().statePointer),this._positionD=(0,bn.prism)(()=>{const D=this._prismOfStatePointer.getValue();return(0,bn.val)(D.position)}),this._positionFormatterD=(0,bn.prism)(()=>{const D=(0,bn.val)(this._subUnitsPerUnitD);return new fE(D)})}get type(){return"Theatre_Sequence"}pointerToPrism(o){const{path:l}=(0,Qf.getPointerParts)(o);if(l.length===0)return(0,bn.prism)(()=>({length:(0,bn.val)(this.pointer.length),playing:(0,bn.val)(this.pointer.playing),position:(0,bn.val)(this.pointer.position),subUnitsPerUnit:(0,bn.val)(this.pointer.subUnitsPerUnit)}));if(l.length>1)return(0,bn.prism)(()=>{});const[d]=l;return d==="length"?this._lengthD:d==="subUnitsPerUnit"?this._subUnitsPerUnitD:d==="position"?this._positionD:d==="playing"?(0,bn.prism)(()=>(0,bn.val)(this._prismOfStatePointer.getValue().playing)):(0,bn.prism)(()=>{})}getKeyframesOfSimpleProp(o){const{path:l,root:d}=(0,Qf.getPointerParts)(o);if(!uE(d))throw new Ro("Argument prop must be a pointer to a SheetObject property");const y=(0,bn.val)(this._project.pointers.historic.sheetsById[this._sheet.address.sheetId].sequence.tracksByObject[d.address.objectKey]);if(!y)return[];const{trackData:M,trackIdByPropPath:D}=y,z=YS(l),K=D[z];if(!K)return[];const Q=M[K];return Q?Q.keyframes:[]}get positionFormatter(){return this._positionFormatterD.getValue()}get prismOfStatePointer(){return this._prismOfStatePointer}get length(){return this._lengthD.getValue()}get positionPrism(){return this._positionD}get position(){return this._playbackControllerBox.get().getCurrentPosition()}get subUnitsPerUnit(){return this._subUnitsPerUnitD.getValue()}get positionSnappedToGrid(){return this.closestGridPosition(this.position)}set position(o){let l=o;this.pause(),l>this.length&&(l=this.length);const d=this.length;this._playbackControllerBox.get().gotoPosition(l>d?d:l)}getDurationCold(){return this._lengthD.getValue()}get playing(){return(0,bn.val)(this._playbackControllerBox.get().statePointer.playing)}_makeRangeFromSequenceTemplate(){return(0,bn.prism)(()=>[0,(0,bn.val)(this._lengthD)])}playDynamicRange(o,l){return this._playbackControllerBox.get().playDynamicRange(o,l)}async play(o,l){const d=this.length,y=o&&o.range?o.range:[0,d],M=o&&typeof o.iterationCount=="number"?o.iterationCount:1,D=o&&typeof o.rate<"u"?o.rate:1,z=o&&o.direction?o.direction:"normal";return await this._play(M,[y[0],y[1]],D,z,l)}_play(o,l,d,y,M){return this._playbackControllerBox.get().play(o,l,d,y,M)}pause(){this._playbackControllerBox.get().pause()}replacePlaybackController(o){this.pause();const l=this._playbackControllerBox.get();this._playbackControllerBox.set(o);const d=l.getCurrentPosition();l.destroy(),o.gotoPosition(d)}},fE=class{constructor(o){this._fps=o}formatSubUnitForGrid(o){const l=o%1,d=1/this._fps;return Math.round(l/d)+"f"}formatFullUnitForGrid(o){let l=o,d="";if(l>=Ms){const M=Math.floor(l/Ms);d+=M+"h",l=l%Ms}if(l>=Hr){const M=Math.floor(l/Hr);d+=M+"m",l=l%Hr}if(l>=zr){const M=Math.floor(l/zr);d+=M+"s",l=l%zr}const y=1/this._fps;if(l>=y){const M=Math.floor(l/y);d+=M+"f",l=l%y}return d.length===0?"0s":d}formatForPlayhead(o){let l=o,d="";if(l>=Ms){const M=Math.floor(l/Ms);d+=Ao(M.toString(),2,"0")+"h",l=l%Ms}if(l>=Hr){const M=Math.floor(l/Hr);d+=Ao(M.toString(),2,"0")+"m",l=l%Hr}else d.length>0&&(d+="00m");if(l>=zr){const M=Math.floor(l/zr);d+=Ao(M.toString(),2,"0")+"s",l=l%zr}else d+="00s";const y=1/this._fps;if(l>=y){const M=Math.round(l/y);d+=Ao(M.toString(),2,"0")+"f",l=l%y}else l/y>.98?(d+=Ao("1",2,"0")+"f",l=l%y):d+="00f";return d.length===0?"00s00f":d}formatBasic(o){return o.toFixed(2)+"s"}},zr=1,Hr=zr*60,Ms=Hr*60,tu={};v(tu,{boolean:()=>cp,compound:()=>iu,file:()=>bE,image:()=>EE,number:()=>ap,rgba:()=>RE,string:()=>lp,stringLiteral:()=>LE});function np(o,l){return o.length<=l?o:o.substr(0,l-3)+"..."}var pE=o=>typeof o=="string"?'string("'.concat(np(o,10),'")'):typeof o=="number"?"number(".concat(np(String(o),10),")"):o===null?"null":o===void 0?"undefined":typeof o=="boolean"?String(o):Array.isArray(o)?"array":typeof o=="object"?"object":"unknown",ip=pE;function mE(o,{removeAlphaIfOpaque:l=!1}={}){const d=(o.a*255|256).toString(16).slice(1),y=(o.r*255|256).toString(16).slice(1)+(o.g*255|256).toString(16).slice(1)+(o.b*255|256).toString(16).slice(1)+(l&&d==="ff"?"":d);return"#".concat(y)}function nu(o){return x(g({},o),{toString(){return mE(this,{removeAlphaIfOpaque:!0})}})}function gE(o){return Object.fromEntries(Object.entries(o).map(([l,d])=>[l,nf(d,0,1)]))}function _E(o){function l(d){return d>=.0031308?1.055*d**(1/2.4)-.055:12.92*d}return gE({r:l(o.r),g:l(o.g),b:l(o.b),a:o.a})}function rp(o){function l(d){return d>=.04045?((d+.055)/(1+.055))**2.4:d/12.92}return{r:l(o.r),g:l(o.g),b:l(o.b),a:o.a}}function sp(o){let l=.4122214708*o.r+.5363325363*o.g+.0514459929*o.b,d=.2119034982*o.r+.6806995451*o.g+.1073969566*o.b,y=.0883024619*o.r+.2817188376*o.g+.6299787005*o.b,M=Math.cbrt(l),D=Math.cbrt(d),z=Math.cbrt(y);return{L:.2104542553*M+.793617785*D-.0040720468*z,a:1.9779984951*M-2.428592205*D+.4505937099*z,b:.0259040371*M+.7827717662*D-.808675766*z,alpha:o.a}}function vE(o){let l=o.L+.3963377774*o.a+.2158037573*o.b,d=o.L-.1055613458*o.a-.0638541728*o.b,y=o.L-.0894841775*o.a-1.291485548*o.b,M=l*l*l,D=d*d*d,z=y*y*y;return{r:4.0767416621*M-3.3077115913*D+.2309699292*z,g:-1.2684380046*M+2.6097574011*D-.3413193965*z,b:-.0041960863*M-.7034186147*D+1.707614701*z,a:o.alpha}}var zi=Symbol("TheatrePropType_Basic");function op(o){return typeof o=="object"&&!!o&&o[zi]==="TheatrePropType"}function yE(o){if(typeof o=="number")return ap(o);if(typeof o=="boolean")return cp(o);if(typeof o=="string")return lp(o);if(typeof o=="object"&&o){if(op(o))return o;if(Nv(o))return iu(o);throw new Ro("This value is not a valid prop type: ".concat(ip(o)))}else throw new Ro("This value is not a valid prop type: ".concat(ip(o)))}function xE(o){const l={};for(const d of Object.keys(o)){const y=o[d];op(y)?l[d]=y:l[d]=yE(y)}return l}var iu=(o,l={})=>{const d=xE(o),y=new WeakMap;return{type:"compound",props:d,valueType:null,[zi]:"TheatrePropType",label:l.label,default:cS(d,D=>D.default),deserializeAndSanitize:D=>{if(typeof D!="object"||!D)return;if(y.has(D))return y.get(D);const z={};let K=!1;for(const[Q,ae]of Object.entries(d))if(Object.prototype.hasOwnProperty.call(D,Q)){const ye=ae.deserializeAndSanitize(D[Q]);ye!=null&&(K=!0,z[Q]=ye)}if(y.set(D,z),K)return z}}},bE=(o,l={})=>{const d=(y,M,D)=>{var z;return{type:"file",id:((z=l.interpolate)!=null?z:Po)(y.id,M.id,D)}};return{type:"file",default:{type:"file",id:o},valueType:null,[zi]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:SE}},SE=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="file"&&(l=!1),!!l)return o},EE=(o,l={})=>{const d=(y,M,D)=>{var z;return{type:"image",id:((z=l.interpolate)!=null?z:Po)(y.id,M.id,D)}};return{type:"image",default:{type:"image",id:o},valueType:null,[zi]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:ME}},ME=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="image"&&(l=!1),!!l)return o},ap=(o,l={})=>{var d;return x(g({type:"number",valueType:0,default:o,[zi]:"TheatrePropType"},l||{}),{label:l.label,nudgeFn:(d=l.nudgeFn)!=null?d:FE,nudgeMultiplier:typeof l.nudgeMultiplier=="number"?l.nudgeMultiplier:void 0,interpolate:AE,deserializeAndSanitize:TE(l.range)})},TE=o=>o?l=>{if(typeof l=="number"&&isFinite(l))return nf(l,o[0],o[1])}:wE,wE=o=>typeof o=="number"&&isFinite(o)?o:void 0,AE=(o,l,d)=>o+d*(l-o),RE=(o={r:0,g:0,b:0,a:1},l={})=>{const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return{type:"rgba",valueType:null,default:nu(d),[zi]:"TheatrePropType",label:l.label,interpolate:CE,deserializeAndSanitize:PE}},PE=o=>{if(!o)return;let l=!0;for(const y of["r","g","b","a"])(!Object.prototype.hasOwnProperty.call(o,y)||typeof o[y]!="number")&&(l=!1);if(!l)return;const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return nu(d)},CE=(o,l,d)=>{const y=sp(rp(o)),M=sp(rp(l)),D={L:(1-d)*y.L+d*M.L,a:(1-d)*y.a+d*M.a,b:(1-d)*y.b+d*M.b,alpha:(1-d)*y.alpha+d*M.alpha},z=_E(vE(D));return nu(z)},cp=(o,l={})=>{var d;return{type:"boolean",default:o,valueType:null,[zi]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:DE}},DE=o=>typeof o=="boolean"?o:void 0;function Po(o){return o}var lp=(o,l={})=>{var d;return{type:"string",default:o,valueType:null,[zi]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:IE}};function IE(o){return typeof o=="string"?o:void 0}function LE(o,l,d={}){var y,M;return{type:"stringLiteral",default:o,valuesAndLabels:g({},l),[zi]:"TheatrePropType",valueType:null,as:(y=d.as)!=null?y:"menu",label:d.label,interpolate:(M=d.interpolate)!=null?M:Po,deserializeAndSanitize(D){if(typeof D=="string"&&Object.prototype.hasOwnProperty.call(l,D))return D}}}var FE=({config:o,deltaX:l,deltaFraction:d,magnitude:y})=>{var M;const{range:D}=o;return!o.nudgeMultiplier&&D&&!D.includes(1/0)&&!D.includes(-1/0)?d*(D[1]-D[0])*y:l*y*((M=o.nudgeMultiplier)!=null?M:1)},NE=o=>o.replace(/^[\s\/]*/,"").replace(/[\s\/]*$/,"").replace(/\s*\/\s*/g," / ");function ka(o,l){return NE(o)}A(V());var OE=class{get type(){return"Theatre_Sheet_PublicAPI"}constructor(o){de(this,o)}object(o,l,d){const y=q(this),M=ka(o),D=y.getObject(M),z=null,K=d==null?void 0:d.__actions__THIS_API_IS_UNSTABLE_AND_WILL_CHANGE_IN_THE_NEXT_VERSION;if(D)return K&&D.template._temp_setActions(K),D.publicApi;{const Q=iu(l);return y.createObject(M,z,Q,K).publicApi}}__experimental_getExistingObject(o){const l=q(this),d=ka(o),y=l.getObject(d);return y==null?void 0:y.publicApi}get sequence(){return q(this).getSequence().publicApi}get project(){return q(this).project.publicApi}get address(){return g({},q(this).address)}detachObject(o){const l=q(this),d=ka(o);if(!l.getObject(d)){Es.warning(`Couldn't delete object "`.concat(d,'"'),'There is no object with key "'.concat(d,`".

To fix this, make sure you are calling \`sheet.deleteObject("`).concat(d,'")` with the correct key.')),console.warn('Object key "'.concat(d,'" does not exist.'));return}l.deleteObject(d)}},Co=mn(),UE=class{constructor(o,l){this.template=o,this.instanceId=l,b(this,"_objects",new Co.Atom({})),b(this,"_sequence"),b(this,"address"),b(this,"publicApi"),b(this,"project"),b(this,"objectsP",this._objects.pointer),b(this,"type","Theatre_Sheet"),b(this,"_logger"),this._logger=o.project._logger.named("Sheet",l),this._logger._trace("creating sheet"),this.project=o.project,this.address=x(g({},o.address),{sheetInstanceId:this.instanceId}),this.publicApi=new OE(this)}createObject(o,l,d,y={}){const D=this.template.getObjectTemplate(o,l,d,y).createInstance(this,l,d);return this._objects.setByPointer(z=>z[o],D),D}getObject(o){return this._objects.get()[o]}deleteObject(o){this._objects.reduce(l=>{const d=g({},l);return delete d[o],d})}getSequence(){if(!this._sequence){const o=(0,Co.prism)(()=>{const d=(0,Co.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.length);return BE(d)}),l=(0,Co.prism)(()=>{const d=(0,Co.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.subUnitsPerUnit);return kE(d)});this._sequence=new dE(this.template.project,this,o,l)}return this._sequence}},BE=o=>typeof o=="number"&&isFinite(o)&&o>0?o:10,kE=o=>typeof o=="number"&&oS(o)&&o>=1&&o<=1e3?o:30,zE=class{constructor(o,l){this.project=o,b(this,"type","Theatre_SheetTemplate"),b(this,"address"),b(this,"_instances",new Zf.Atom({})),b(this,"instancesP",this._instances.pointer),b(this,"_objectTemplates",new Zf.Atom({})),b(this,"objectTemplatesP",this._objectTemplates.pointer),this.address=x(g({},o.address),{sheetId:l})}getInstance(o){let l=this._instances.get()[o];return l||(l=new UE(this,o),this._instances.setByPointer(d=>d[o],l)),l}getObjectTemplate(o,l,d,y){let M=this._objectTemplates.get()[o];return M||(M=new XS(this,o,l,d,y),this._objectTemplates.setByPointer(D=>D[o],M)),M}},ru=mn(),up=mn(),HE=o=>new Promise(l=>setTimeout(l,o)),VE=HE;function ui(o){for(var l=arguments.length,d=Array(l>1?l-1:0),y=1;y<l;y++)d[y-1]=arguments[y];throw Error("[Immer] minified error nr: "+o+(d.length?" "+d.map(function(M){return"'"+M+"'"}).join(","):"")+". Find the full error at: https://bit.ly/3cXEKWf")}function Vr(o){return!!o&&!!o[Xn]}function Gr(o){return!!o&&((function(l){if(!l||typeof l!="object")return!1;var d=Object.getPrototypeOf(l);if(d===null)return!0;var y=Object.hasOwnProperty.call(d,"constructor")&&d.constructor;return y===Object||typeof y=="function"&&Function.toString.call(y)===ZE})(o)||Array.isArray(o)||!!o[xp]||!!o.constructor[xp]||ou(o)||au(o))}function GE(o){return Vr(o)||ui(23,o),o[Xn].t}function Do(o,l,d){d===void 0&&(d=!1),Ts(o)===0?(d?Object.keys:yu)(o).forEach(function(y){d&&typeof y=="symbol"||l(y,o[y],o)}):o.forEach(function(y,M){return l(M,y,o)})}function Ts(o){var l=o[Xn];return l?l.i>3?l.i-4:l.i:Array.isArray(o)?1:ou(o)?2:au(o)?3:0}function su(o,l){return Ts(o)===2?o.has(l):Object.prototype.hasOwnProperty.call(o,l)}function WE(o,l){return Ts(o)===2?o.get(l):o[l]}function hp(o,l,d){var y=Ts(o);y===2?o.set(l,d):y===3?(o.delete(l),o.add(d)):o[l]=d}function jE(o,l){return o===l?o!==0||1/o==1/l:o!=o&&l!=l}function ou(o){return KE&&o instanceof Map}function au(o){return $E&&o instanceof Set}function Wr(o){return o.o||o.t}function cu(o){if(Array.isArray(o))return Array.prototype.slice.call(o);var l=QE(o);delete l[Xn];for(var d=yu(l),y=0;y<d.length;y++){var M=d[y],D=l[M];D.writable===!1&&(D.writable=!0,D.configurable=!0),(D.get||D.set)&&(l[M]={configurable:!0,writable:!0,enumerable:D.enumerable,value:o[M]})}return Object.create(Object.getPrototypeOf(o),l)}function lu(o,l){return l===void 0&&(l=!1),uu(o)||Vr(o)||!Gr(o)||(Ts(o)>1&&(o.set=o.add=o.clear=o.delete=XE),Object.freeze(o),l&&Do(o,function(d,y){return lu(y,!0)},!0)),o}function XE(){ui(2)}function uu(o){return o==null||typeof o!="object"||Object.isFrozen(o)}function Hi(o){var l=JE[o];return l||ui(18,o),l}function dp(){return Io}function hu(o,l){l&&(Hi("Patches"),o.u=[],o.s=[],o.v=l)}function za(o){du(o),o.p.forEach(qE),o.p=null}function du(o){o===Io&&(Io=o.l)}function fp(o){return Io={p:[],l:Io,h:o,m:!0,_:0}}function qE(o){var l=o[Xn];l.i===0||l.i===1?l.j():l.O=!0}function fu(o,l){l._=l.p.length;var d=l.p[0],y=o!==void 0&&o!==d;return l.h.g||Hi("ES5").S(l,o,y),y?(d[Xn].P&&(za(l),ui(4)),Gr(o)&&(o=Ha(l,o),l.l||Va(l,o)),l.u&&Hi("Patches").M(d[Xn],o,l.u,l.s)):o=Ha(l,d,[]),za(l),l.u&&l.v(l.u,l.s),o!==yp?o:void 0}function Ha(o,l,d){if(uu(l))return l;var y=l[Xn];if(!y)return Do(l,function(D,z){return pp(o,y,l,D,z,d)},!0),l;if(y.A!==o)return l;if(!y.P)return Va(o,y.t,!0),y.t;if(!y.I){y.I=!0,y.A._--;var M=y.i===4||y.i===5?y.o=cu(y.k):y.o;Do(y.i===3?new Set(M):M,function(D,z){return pp(o,y,M,D,z,d)}),Va(o,M,!1),d&&o.u&&Hi("Patches").R(y,d,o.u,o.s)}return y.o}function pp(o,l,d,y,M,D){if(Vr(M)){var z=Ha(o,M,D&&l&&l.i!==3&&!su(l.D,y)?D.concat(y):void 0);if(hp(d,y,z),!Vr(z))return;o.m=!1}if(Gr(M)&&!uu(M)){if(!o.h.F&&o._<1)return;Ha(o,M),l&&l.A.l||Va(o,M)}}function Va(o,l,d){d===void 0&&(d=!1),o.h.F&&o.m&&lu(l,d)}function pu(o,l){var d=o[Xn];return(d?Wr(d):o)[l]}function mp(o,l){if(l in o)for(var d=Object.getPrototypeOf(o);d;){var y=Object.getOwnPropertyDescriptor(d,l);if(y)return y;d=Object.getPrototypeOf(d)}}function mu(o){o.P||(o.P=!0,o.l&&mu(o.l))}function gu(o){o.o||(o.o=cu(o.t))}function _u(o,l,d){var y=ou(l)?Hi("MapSet").N(l,d):au(l)?Hi("MapSet").T(l,d):o.g?(function(M,D){var z=Array.isArray(M),K={i:z?1:0,A:D?D.A:dp(),P:!1,I:!1,D:{},l:D,t:M,k:null,o:null,j:null,C:!1},Q=K,ae=Ga;z&&(Q=[K],ae=Wa);var ye=Proxy.revocable(Q,ae),xe=ye.revoke,Ce=ye.proxy;return K.k=Ce,K.j=xe,Ce})(l,d):Hi("ES5").J(l,d);return(d?d.A:dp()).p.push(y),y}function YE(o){return Vr(o)||ui(22,o),(function l(d){if(!Gr(d))return d;var y,M=d[Xn],D=Ts(d);if(M){if(!M.P&&(M.i<4||!Hi("ES5").K(M)))return M.t;M.I=!0,y=gp(d,D),M.I=!1}else y=gp(d,D);return Do(y,function(z,K){M&&WE(M.t,z)===K||hp(y,z,l(K))}),D===3?new Set(y):y})(o)}function gp(o,l){switch(l){case 2:return new Map(o);case 3:return Array.from(o)}return cu(o)}var _p,Io,vu=typeof Symbol<"u"&&typeof Symbol("x")=="symbol",KE=typeof Map<"u",$E=typeof Set<"u",vp=typeof Proxy<"u"&&Proxy.revocable!==void 0&&typeof Reflect<"u",yp=vu?Symbol.for("immer-nothing"):((_p={})["immer-nothing"]=!0,_p),xp=vu?Symbol.for("immer-draftable"):"__$immer_draftable",Xn=vu?Symbol.for("immer-state"):"__$immer_state",ZE=""+Object.prototype.constructor,yu=typeof Reflect<"u"&&Reflect.ownKeys?Reflect.ownKeys:Object.getOwnPropertySymbols!==void 0?function(o){return Object.getOwnPropertyNames(o).concat(Object.getOwnPropertySymbols(o))}:Object.getOwnPropertyNames,QE=Object.getOwnPropertyDescriptors||function(o){var l={};return yu(o).forEach(function(d){l[d]=Object.getOwnPropertyDescriptor(o,d)}),l},JE={},Ga={get:function(o,l){if(l===Xn)return o;var d=Wr(o);if(!su(d,l))return(function(M,D,z){var K,Q=mp(D,z);return Q?"value"in Q?Q.value:(K=Q.get)===null||K===void 0?void 0:K.call(M.k):void 0})(o,d,l);var y=d[l];return o.I||!Gr(y)?y:y===pu(o.t,l)?(gu(o),o.o[l]=_u(o.A.h,y,o)):y},has:function(o,l){return l in Wr(o)},ownKeys:function(o){return Reflect.ownKeys(Wr(o))},set:function(o,l,d){var y=mp(Wr(o),l);if(y!=null&&y.set)return y.set.call(o.k,d),!0;if(!o.P){var M=pu(Wr(o),l),D=M==null?void 0:M[Xn];if(D&&D.t===d)return o.o[l]=d,o.D[l]=!1,!0;if(jE(d,M)&&(d!==void 0||su(o.t,l)))return!0;gu(o),mu(o)}return o.o[l]===d&&typeof d!="number"&&(d!==void 0||l in o.o)||(o.o[l]=d,o.D[l]=!0,!0)},deleteProperty:function(o,l){return pu(o.t,l)!==void 0||l in o.t?(o.D[l]=!1,gu(o),mu(o)):delete o.D[l],o.o&&delete o.o[l],!0},getOwnPropertyDescriptor:function(o,l){var d=Wr(o),y=Reflect.getOwnPropertyDescriptor(d,l);return y&&{writable:!0,configurable:o.i!==1||l!=="length",enumerable:y.enumerable,value:d[l]}},defineProperty:function(){ui(11)},getPrototypeOf:function(o){return Object.getPrototypeOf(o.t)},setPrototypeOf:function(){ui(12)}},Wa={};Do(Ga,function(o,l){Wa[o]=function(){return arguments[0]=arguments[0][0],l.apply(this,arguments)}}),Wa.deleteProperty=function(o,l){return Ga.deleteProperty.call(this,o[0],l)},Wa.set=function(o,l,d){return Ga.set.call(this,o[0],l,d,o[0])};var eM=(function(){function o(d){var y=this;this.g=vp,this.F=!0,this.produce=function(M,D,z){if(typeof M=="function"&&typeof D!="function"){var K=D;D=M;var Q=y;return function(et){var je=this;et===void 0&&(et=K);for(var vt=arguments.length,Mt=Array(vt>1?vt-1:0),_t=1;_t<vt;_t++)Mt[_t-1]=arguments[_t];return Q.produce(et,function(Nt){var In;return(In=D).call.apply(In,[je,Nt].concat(Mt))})}}var ae;if(typeof D!="function"&&ui(6),z!==void 0&&typeof z!="function"&&ui(7),Gr(M)){var ye=fp(y),xe=_u(y,M,void 0),Ce=!0;try{ae=D(xe),Ce=!1}finally{Ce?za(ye):du(ye)}return typeof Promise<"u"&&ae instanceof Promise?ae.then(function(et){return hu(ye,z),fu(et,ye)},function(et){throw za(ye),et}):(hu(ye,z),fu(ae,ye))}if(!M||typeof M!="object")return(ae=D(M))===yp?void 0:(ae===void 0&&(ae=M),y.F&&lu(ae,!0),ae);ui(21,M)},this.produceWithPatches=function(M,D){return typeof M=="function"?function(Q){for(var ae=arguments.length,ye=Array(ae>1?ae-1:0),xe=1;xe<ae;xe++)ye[xe-1]=arguments[xe];return y.produceWithPatches(Q,function(Ce){return M.apply(void 0,[Ce].concat(ye))})}:[y.produce(M,D,function(Q,ae){z=Q,K=ae}),z,K];var z,K},typeof(d==null?void 0:d.useProxies)=="boolean"&&this.setUseProxies(d.useProxies),typeof(d==null?void 0:d.autoFreeze)=="boolean"&&this.setAutoFreeze(d.autoFreeze)}var l=o.prototype;return l.createDraft=function(d){Gr(d)||ui(8),Vr(d)&&(d=YE(d));var y=fp(this),M=_u(this,d,void 0);return M[Xn].C=!0,du(y),M},l.finishDraft=function(d,y){var M=d&&d[Xn],D=M.A;return hu(D,y),fu(void 0,D)},l.setAutoFreeze=function(d){this.F=d},l.setUseProxies=function(d){d&&!vp&&ui(20),this.g=d},l.applyPatches=function(d,y){var M;for(M=y.length-1;M>=0;M--){var D=y[M];if(D.path.length===0&&D.op==="replace"){d=D.value;break}}var z=Hi("Patches").$;return Vr(d)?z(d,y):this.produce(d,function(K){return z(K,y.slice(M+1))})},o})(),ni=new eM;ni.produce,ni.produceWithPatches.bind(ni),ni.setAutoFreeze.bind(ni),ni.setUseProxies.bind(ni),ni.applyPatches.bind(ni),ni.createDraft.bind(ni),ni.finishDraft.bind(ni);var tM={currentProjectStateDefinitionVersion:"0.4.0"},xu=tM;async function nM(o,l,d){await VE(0),o.transaction(({drafts:y})=>{var M;const D=l.address.projectId;y.ephemeral.coreByProject[D]={lastExportedObject:null,loadingState:{type:"loading"}},y.ahistoric.coreByProject[D]={ahistoricStuff:""};function z(){y.ephemeral.coreByProject[D].loadingState={type:"loaded"},y.historic.coreByProject[D]={sheetsById:{},definitionVersion:xu.currentProjectStateDefinitionVersion,revisionHistory:[]}}function K(xe){y.ephemeral.coreByProject[D].loadingState={type:"loaded"},y.historic.coreByProject[D]=xe}function Q(){y.ephemeral.coreByProject[D].loadingState={type:"loaded"}}function ae(xe){y.ephemeral.coreByProject[D].loadingState={type:"browserStateIsNotBasedOnDiskState",onDiskState:xe}}const ye=(M=GE(y.historic))==null?void 0:M.coreByProject[l.address.projectId];ye?d&&ye.revisionHistory.indexOf(d.revisionHistory[0])==-1?ae(d):Q():d?K(d):z()})}function bp(){}function Sp(o){var l,d;const y=(l=o==null?void 0:o.logging)!=null&&l.internal?(d=o.logging.min)!=null?d:256:1/0,M=y<=128,D=y<=512,z=Wf(void 0,{_debug:M?console.debug.bind(console,"_coreLogger(TheatreInternalLogger) debug"):bp,_error:D?console.error.bind(console,"_coreLogger(TheatreInternalLogger) error"):bp});if(o){const{logger:K,logging:Q}=o;K&&z.configureLogger(K),Q?z.configureLogging(Q):z.configureLogging({dev:!1})}return z.getLogger().named("Theatre")}var iM=class{constructor(o,l={},d){this.config=l,this.publicApi=d,b(this,"pointers"),b(this,"_pointerProxies"),b(this,"address"),b(this,"_studioReadyDeferred"),b(this,"_assetStorageReadyDeferred"),b(this,"_readyPromise"),b(this,"_sheetTemplates",new up.Atom({})),b(this,"sheetTemplatesP",this._sheetTemplates.pointer),b(this,"_studio"),b(this,"assetStorage"),b(this,"type","Theatre_Project"),b(this,"_logger");var y;this._logger=Sp({logging:{dev:!0}}).named("Project",o),this._logger.traceDev("creating project"),this.address={projectId:o};const M=new up.Atom({ahistoric:{ahistoricStuff:""},historic:(y=l.state)!=null?y:{sheetsById:{},definitionVersion:xu.currentProjectStateDefinitionVersion,revisionHistory:[]},ephemeral:{loadingState:{type:"loaded"},lastExportedObject:null}});this._assetStorageReadyDeferred=lr(),this.assetStorage={getAssetUrl:D=>{var z;return"".concat((z=l.assets)==null?void 0:z.baseUrl,"/").concat(D)},createAsset:()=>{throw new Error("Please wait for Project.ready to use assets.")}},this._pointerProxies={historic:new ru.PointerProxy(M.pointer.historic),ahistoric:new ru.PointerProxy(M.pointer.ahistoric),ephemeral:new ru.PointerProxy(M.pointer.ephemeral)},this.pointers={historic:this._pointerProxies.historic.pointer,ahistoric:this._pointerProxies.ahistoric.pointer,ephemeral:this._pointerProxies.ephemeral.pointer},se.add(o,this),this._studioReadyDeferred=lr(),this._readyPromise=Promise.all([this._studioReadyDeferred.promise,this._assetStorageReadyDeferred.promise]).then(()=>{}),l.state?setTimeout(()=>{this._studio||(this._studioReadyDeferred.resolve(void 0),this._assetStorageReadyDeferred.resolve(void 0),this._logger._trace("ready deferred resolved with no state"))},0):typeof window>"u"?console.error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. ')+"You can safely ignore this message if you're developing a Next.js/Remix project in development mode. But if you are shipping to your end-users, then you need to set config.state, otherwise your project's state will be empty and nothing will animate. Learn more at https://www.theatrejs.com/docs/latest/manual/projects#state"):setTimeout(()=>{if(!this._studio)throw new Error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. This is fine ')+"while you are using @theatre/core along with @theatre/studio. But since @theatre/studio "+'is not loaded, the state of project "'.concat(o,`" will be empty.

`)+`To fix this, you need to add @theatre/studio into the bundle and export the project's state. Learn how to do that at https://www.theatrejs.com/docs/latest/manual/projects#state
`)},1e3)}attachToStudio(o){if(this._studio){if(this._studio!==o)throw new Error("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));console.warn("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));return}this._studio=o,o.initialized.then(async()=>{var l;await nM(o,this,this.config.state),this._pointerProxies.historic.setPointer(o.atomP.historic.coreByProject[this.address.projectId]),this._pointerProxies.ahistoric.setPointer(o.atomP.ahistoric.coreByProject[this.address.projectId]),this._pointerProxies.ephemeral.setPointer(o.atomP.ephemeral.coreByProject[this.address.projectId]),await o.createAssetStorage(this,(l=this.config.assets)==null?void 0:l.baseUrl).then(d=>{this.assetStorage=d,this._assetStorageReadyDeferred.resolve(void 0)}),this._studioReadyDeferred.resolve(void 0)}).catch(l=>{throw console.error(l),l})}get isAttachedToStudio(){return!!this._studio}get ready(){return this._readyPromise}isReady(){return this._studioReadyDeferred.status==="resolved"&&this._assetStorageReadyDeferred.status==="resolved"}getOrCreateSheet(o,l="default"){let d=this._sheetTemplates.get()[o];return d||(d=new zE(this,o),this._sheetTemplates.reduce(y=>x(g({},y),{[o]:d}))),d.getInstance(l)}},rM=class{get type(){return"Theatre_Project_PublicAPI"}constructor(o,l={}){de(this,new iM(o,l,this))}get ready(){return q(this).ready}get isReady(){return q(this).isReady()}get address(){return g({},q(this).address)}getAssetUrl(o){if(!this.isReady){console.error("Calling `project.getAssetUrl()` before `project.ready` is resolved, will always return `undefined`. Either use `project.ready.then(() => project.getAssetUrl())` or `await project.ready` before calling `project.getAssetUrl()`.");return}return o.id?q(this).assetStorage.getAssetUrl(o.id):void 0}sheet(o,l="default"){const d=ka(o);return q(this).getOrCreateSheet(d,l).publicApi}};A(V());var Ep=mn(),bu=mn();function Mp(o,l={}){const d=se.get(o);if(d)return d.publicApi;const M=Sp().named("Project",o);return l.state?(oM(o,l.state),M._debug("deep validated config.state on disk")):M._debug("no config.state"),new rM(o,l)}var sM=(o,l)=>{if(Array.isArray(l)||l==null||l.definitionVersion!==xu.currentProjectStateDefinitionVersion)throw new Ro("Error validating conf.state in Theatre.getProject(".concat(JSON.stringify(o),", conf). The state seems to be formatted in a way that is unreadable to Theatre.js. Read more at https://www.theatrejs.com/docs/latest/manual/projects#state"))},oM=(o,l)=>{sM(o,l)};function Su(o,l,d){const y=d?q(d).ticker:tp();if((0,Ep.isPointer)(o))return(0,bu.pointerToPrism)(o).onChange(y,l,!0);if((0,bu.isPrism)(o))return o.onChange(y,l,!0);throw new Error("Called onChange(p) where p is neither a pointer nor a prism.")}function Tp(o){if((0,Ep.isPointer)(o))return(0,bu.pointerToPrism)(o).getValue();throw new Error("Called val(p) where p is not a pointer.")}var aM=class{constructor(){b(this,"_studio")}get type(){return"Theatre_CoreBundle"}get version(){return"0.7.2"}getBitsForStudio(o,l){if(this._studio)throw new Error("@theatre/core is already attached to @theatre/studio");this._studio=o;const d={projectsP:se.atom.pointer.projects,privateAPI:q,coreExports:R,getCoreRafDriver:ep};l(d)}};cM();function cM(){if(typeof window>"u")return;const o=window[Jl];if(typeof o<"u")throw typeof o=="object"&&o&&typeof o.version=="string"?new Error(`It seems that the module '@theatre/core' is loaded more than once. This could have two possible causes:
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
		*/})(Ko,Ko.exports)),Ko.exports}var cn=UC();let ch=null,sd=null;const r_=new Map;function BC(){return ch=cn.getProject("HumanBody Theatre"),sd=ch.sheet("Main"),{project:ch,sheet:sd}}function Id(){return sd}function kC(r,e){const t=r.object("Camera",{position:cn.types.compound({x:cn.types.number(e.position.x,{range:[-50,50]}),y:cn.types.number(e.position.y,{range:[-10,20]}),z:cn.types.number(e.position.z,{range:[-50,50]})}),fov:cn.types.number(e.fov,{range:[10,120]})});return t.onValuesChange(n=>{e.position.set(n.position.x,n.position.y,n.position.z),e.fov=n.fov,e.updateProjectionMatrix()}),r_.set("Camera",t),t}function Ec(r,e,t){const n={position:cn.types.compound({x:cn.types.number(t.position.x,{range:[-20,20]}),y:cn.types.number(t.position.y,{range:[0,20]}),z:cn.types.number(t.position.z,{range:[-20,20]})}),intensity:cn.types.number(t.intensity,{range:[0,100]}),color:cn.types.rgba({r:t.color.r,g:t.color.g,b:t.color.b,a:1})},i=r.object(e,n);return i.onValuesChange(s=>{t.position.set(s.position.x,s.position.y,s.position.z),t.intensity=s.intensity,t.color.setRGB(s.color.r,s.color.g,s.color.b)}),r_.set(e,i),i}function Ld(r,e,t){const n=r.object(e,{position:cn.types.compound({x:cn.types.number(t.position.x,{range:[-20,20]}),y:cn.types.number(t.position.y,{range:[-5,10]}),z:cn.types.number(t.position.z,{range:[-20,20]})}),rotation:cn.types.compound({x:cn.types.number(0,{range:[-180,180]}),y:cn.types.number(0,{range:[-180,180]}),z:cn.types.number(0,{range:[-180,180]})}),scale:cn.types.number(1,{range:[.01,10]})});return n.onValuesChange(i=>{t.position.set(i.position.x,i.position.y,i.position.z),t.rotation.set(i.rotation.x*Math.PI/180,i.rotation.y*Math.PI/180,i.rotation.z*Math.PI/180),t.scale.setScalar(i.scale)}),n}function rg(r,e){if(e===VM)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),r;if(e===Jh||e===Mg){let t=r.getIndex();if(t===null){const a=[],c=r.getAttribute("position");if(c!==void 0){for(let u=0;u<c.count;u++)a.push(u);r.setIndex(a),t=r.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),r}const n=t.count-2,i=[];if(e===Jh)for(let a=1;a<=n;a++)i.push(t.getX(0)),i.push(t.getX(a)),i.push(t.getX(a+1));else for(let a=0;a<n;a++)a%2===0?(i.push(t.getX(a)),i.push(t.getX(a+1)),i.push(t.getX(a+2))):(i.push(t.getX(a+2)),i.push(t.getX(a+1)),i.push(t.getX(a)));i.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const s=r.clone();return s.setIndex(i),s.clearGroups(),s}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),r}class zC extends ds{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new jC(t)}),this.register(function(t){return new XC(t)}),this.register(function(t){return new tD(t)}),this.register(function(t){return new nD(t)}),this.register(function(t){return new iD(t)}),this.register(function(t){return new YC(t)}),this.register(function(t){return new KC(t)}),this.register(function(t){return new $C(t)}),this.register(function(t){return new ZC(t)}),this.register(function(t){return new WC(t)}),this.register(function(t){return new QC(t)}),this.register(function(t){return new qC(t)}),this.register(function(t){return new eD(t)}),this.register(function(t){return new JC(t)}),this.register(function(t){return new VC(t)}),this.register(function(t){return new rD(t)}),this.register(function(t){return new sD(t)})}load(e,t,n,i){const s=this;let a;if(this.resourcePath!=="")a=this.resourcePath;else if(this.path!==""){const h=Qo.extractUrlBase(e);a=Qo.resolveURL(h,this.path)}else a=Qo.extractUrlBase(e);this.manager.itemStart(e);const c=function(h){i?i(h):console.error(h),s.manager.itemError(e),s.manager.itemEnd(e)},u=new Ad(this.manager);u.setPath(this.path),u.setResponseType("arraybuffer"),u.setRequestHeader(this.requestHeader),u.setWithCredentials(this.withCredentials),u.load(e,function(h){try{s.parse(h,a,function(f){t(f),s.manager.itemEnd(e)},c)}catch(f){c(f)}},n,c)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,i){let s;const a={},c={},u=new TextDecoder;if(typeof e=="string")s=JSON.parse(e);else if(e instanceof ArrayBuffer)if(u.decode(new Uint8Array(e,0,4))===s_){try{a[At.KHR_BINARY_GLTF]=new oD(e)}catch(p){i&&i(p);return}s=JSON.parse(a[At.KHR_BINARY_GLTF].content)}else s=JSON.parse(u.decode(e));else s=e;if(s.asset===void 0||s.asset.version[0]<2){i&&i(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const h=new yD(s,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});h.fileLoader.setRequestHeader(this.requestHeader);for(let f=0;f<this.pluginCallbacks.length;f++){const p=this.pluginCallbacks[f](h);p.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),c[p.name]=p,a[p.name]=!0}if(s.extensionsUsed)for(let f=0;f<s.extensionsUsed.length;++f){const p=s.extensionsUsed[f],m=s.extensionsRequired||[];switch(p){case At.KHR_MATERIALS_UNLIT:a[p]=new GC;break;case At.KHR_DRACO_MESH_COMPRESSION:a[p]=new aD(s,this.dracoLoader);break;case At.KHR_TEXTURE_TRANSFORM:a[p]=new cD;break;case At.KHR_MESH_QUANTIZATION:a[p]=new lD;break;default:m.indexOf(p)>=0&&c[p]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+p+'".')}}h.setExtensions(a),h.setPlugins(c),h.parse(n,i)}parseAsync(e,t){const n=this;return new Promise(function(i,s){n.parse(e,t,i,s)})}}function HC(){let r={};return{get:function(e){return r[e]},add:function(e,t){r[e]=t},remove:function(e){delete r[e]},removeAll:function(){r={}}}}const At={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class VC{constructor(e){this.parser=e,this.name=At.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,i=t.length;n<i;n++){const s=t[n];s.extensions&&s.extensions[this.name]&&s.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,s.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let i=t.cache.get(n);if(i)return i;const s=t.json,u=((s.extensions&&s.extensions[this.name]||{}).lights||[])[e];let h;const f=new st(16777215);u.color!==void 0&&f.setRGB(u.color[0],u.color[1],u.color[2],Wn);const p=u.range!==void 0?u.range:0;switch(u.type){case"directional":h=new Dc(f),h.target.position.set(0,0,-1),h.add(h.target);break;case"point":h=new $g(f),h.distance=p;break;case"spot":h=new KP(f),h.distance=p,u.spot=u.spot||{},u.spot.innerConeAngle=u.spot.innerConeAngle!==void 0?u.spot.innerConeAngle:0,u.spot.outerConeAngle=u.spot.outerConeAngle!==void 0?u.spot.outerConeAngle:Math.PI/4,h.angle=u.spot.outerConeAngle,h.penumbra=1-u.spot.innerConeAngle/u.spot.outerConeAngle,h.target.position.set(0,0,-1),h.add(h.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+u.type)}return h.position.set(0,0,0),h.decay=2,Zi(h,u),u.intensity!==void 0&&(h.intensity=u.intensity),h.name=t.createUniqueName(u.name||"light_"+e),i=Promise.resolve(h),t.cache.add(n,i),i}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,s=n.json.nodes[e],c=(s.extensions&&s.extensions[this.name]||{}).light;return c===void 0?null:this._loadLight(c).then(function(u){return n._getNodeRef(t.cache,c,u)})}}class GC{constructor(){this.name=At.KHR_MATERIALS_UNLIT}getMaterialType(){return pi}extendParams(e,t,n){const i=[];e.color=new st(1,1,1),e.opacity=1;const s=t.pbrMetallicRoughness;if(s){if(Array.isArray(s.baseColorFactor)){const a=s.baseColorFactor;e.color.setRGB(a[0],a[1],a[2],Wn),e.opacity=a[3]}s.baseColorTexture!==void 0&&i.push(n.assignTexture(e,"map",s.baseColorTexture,En))}return Promise.all(i)}}class WC{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name].emissiveStrength;return s!==void 0&&(t.emissiveIntensity=s),Promise.resolve()}}class jC{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];if(a.clearcoatFactor!==void 0&&(t.clearcoat=a.clearcoatFactor),a.clearcoatTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatMap",a.clearcoatTexture)),a.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=a.clearcoatRoughnessFactor),a.clearcoatRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatRoughnessMap",a.clearcoatRoughnessTexture)),a.clearcoatNormalTexture!==void 0&&(s.push(n.assignTexture(t,"clearcoatNormalMap",a.clearcoatNormalTexture)),a.clearcoatNormalTexture.scale!==void 0)){const c=a.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new lt(c,c)}return Promise.all(s)}}class XC{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.dispersion=s.dispersion!==void 0?s.dispersion:0,Promise.resolve()}}class qC{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.iridescenceFactor!==void 0&&(t.iridescence=a.iridescenceFactor),a.iridescenceTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceMap",a.iridescenceTexture)),a.iridescenceIor!==void 0&&(t.iridescenceIOR=a.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),a.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=a.iridescenceThicknessMinimum),a.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=a.iridescenceThicknessMaximum),a.iridescenceThicknessTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceThicknessMap",a.iridescenceThicknessTexture)),Promise.all(s)}}class YC{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[];t.sheenColor=new st(0,0,0),t.sheenRoughness=0,t.sheen=1;const a=i.extensions[this.name];if(a.sheenColorFactor!==void 0){const c=a.sheenColorFactor;t.sheenColor.setRGB(c[0],c[1],c[2],Wn)}return a.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=a.sheenRoughnessFactor),a.sheenColorTexture!==void 0&&s.push(n.assignTexture(t,"sheenColorMap",a.sheenColorTexture,En)),a.sheenRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"sheenRoughnessMap",a.sheenRoughnessTexture)),Promise.all(s)}}class KC{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.transmissionFactor!==void 0&&(t.transmission=a.transmissionFactor),a.transmissionTexture!==void 0&&s.push(n.assignTexture(t,"transmissionMap",a.transmissionTexture)),Promise.all(s)}}class $C{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.thickness=a.thicknessFactor!==void 0?a.thicknessFactor:0,a.thicknessTexture!==void 0&&s.push(n.assignTexture(t,"thicknessMap",a.thicknessTexture)),t.attenuationDistance=a.attenuationDistance||1/0;const c=a.attenuationColor||[1,1,1];return t.attenuationColor=new st().setRGB(c[0],c[1],c[2],Wn),Promise.all(s)}}class ZC{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.ior=s.ior!==void 0?s.ior:1.5,Promise.resolve()}}class QC{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.specularIntensity=a.specularFactor!==void 0?a.specularFactor:1,a.specularTexture!==void 0&&s.push(n.assignTexture(t,"specularIntensityMap",a.specularTexture));const c=a.specularColorFactor||[1,1,1];return t.specularColor=new st().setRGB(c[0],c[1],c[2],Wn),a.specularColorTexture!==void 0&&s.push(n.assignTexture(t,"specularColorMap",a.specularColorTexture,En)),Promise.all(s)}}class JC{constructor(e){this.parser=e,this.name=At.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return t.bumpScale=a.bumpFactor!==void 0?a.bumpFactor:1,a.bumpTexture!==void 0&&s.push(n.assignTexture(t,"bumpMap",a.bumpTexture)),Promise.all(s)}}class eD{constructor(e){this.parser=e,this.name=At.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Li}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.anisotropyStrength!==void 0&&(t.anisotropy=a.anisotropyStrength),a.anisotropyRotation!==void 0&&(t.anisotropyRotation=a.anisotropyRotation),a.anisotropyTexture!==void 0&&s.push(n.assignTexture(t,"anisotropyMap",a.anisotropyTexture)),Promise.all(s)}}class tD{constructor(e){this.parser=e,this.name=At.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,i=n.textures[e];if(!i.extensions||!i.extensions[this.name])return null;const s=i.extensions[this.name],a=t.options.ktx2Loader;if(!a){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,s.source,a)}}class nD{constructor(e){this.parser=e,this.name=At.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class iD{constructor(e){this.parser=e,this.name=At.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class rD{constructor(e){this.name=At.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const i=n.extensions[this.name],s=this.parser.getDependency("buffer",i.buffer),a=this.parser.options.meshoptDecoder;if(!a||!a.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return s.then(function(c){const u=i.byteOffset||0,h=i.byteLength||0,f=i.count,p=i.byteStride,m=new Uint8Array(c,u,h);return a.decodeGltfBufferAsync?a.decodeGltfBufferAsync(f,p,m,i.mode,i.filter).then(function(g){return g.buffer}):a.ready.then(function(){const g=new ArrayBuffer(f*p);return a.decodeGltfBuffer(new Uint8Array(g),f,p,m,i.mode,i.filter),g})})}else return null}}class sD{constructor(e){this.name=At.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const i=t.meshes[n.mesh];for(const h of i.primitives)if(h.mode!==di.TRIANGLES&&h.mode!==di.TRIANGLE_STRIP&&h.mode!==di.TRIANGLE_FAN&&h.mode!==void 0)return null;const a=n.extensions[this.name].attributes,c=[],u={};for(const h in a)c.push(this.parser.getDependency("accessor",a[h]).then(f=>(u[h]=f,u[h])));return c.length<1?null:(c.push(this.parser.createNodeMesh(e)),Promise.all(c).then(h=>{const f=h.pop(),p=f.isGroup?f.children:[f],m=h[0].count,g=[];for(const x of p){const E=new ft,v=new N,_=new Et,A=new N(1,1,1),w=new LP(x.geometry,x.material,m);for(let b=0;b<m;b++)u.TRANSLATION&&v.fromBufferAttribute(u.TRANSLATION,b),u.ROTATION&&_.fromBufferAttribute(u.ROTATION,b),u.SCALE&&A.fromBufferAttribute(u.SCALE,b),w.setMatrixAt(b,E.compose(v,_,A));for(const b in u)if(b==="_COLOR_0"){const B=u[b];w.instanceColor=new nd(B.array,B.itemSize,B.normalized)}else b!=="TRANSLATION"&&b!=="ROTATION"&&b!=="SCALE"&&x.geometry.setAttribute(b,u[b]);tn.prototype.copy.call(w,x),this.parser.assignFinalMaterial(w),g.push(w)}return f.isGroup?(f.clear(),f.add(...g),f):g[0]}))}}const s_="glTF",Go=12,sg={JSON:1313821514,BIN:5130562};class oD{constructor(e){this.name=At.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,Go),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==s_)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const i=this.header.length-Go,s=new DataView(e,Go);let a=0;for(;a<i;){const c=s.getUint32(a,!0);a+=4;const u=s.getUint32(a,!0);if(a+=4,u===sg.JSON){const h=new Uint8Array(e,Go+a,c);this.content=n.decode(h)}else if(u===sg.BIN){const h=Go+a;this.body=e.slice(h,h+c)}a+=c}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class aD{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=At.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,i=this.dracoLoader,s=e.extensions[this.name].bufferView,a=e.extensions[this.name].attributes,c={},u={},h={};for(const f in a){const p=od[f]||f.toLowerCase();c[p]=a[f]}for(const f in e.attributes){const p=od[f]||f.toLowerCase();if(a[f]!==void 0){const m=n.accessors[e.attributes[f]],g=$s[m.componentType];h[p]=g.name,u[p]=m.normalized===!0}}return t.getDependency("bufferView",s).then(function(f){return new Promise(function(p,m){i.decodeDracoFile(f,function(g){for(const x in g.attributes){const E=g.attributes[x],v=u[x];v!==void 0&&(E.normalized=v)}p(g)},c,h,Wn,m)})})}}class cD{constructor(){this.name=At.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class lD{constructor(){this.name=At.KHR_MESH_QUANTIZATION}}class o_ extends oa{constructor(e,t,n,i){super(e,t,n,i)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i*3+i;for(let a=0;a!==i;a++)t[a]=n[s+a];return t}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=c*2,h=c*3,f=i-t,p=(n-t)/f,m=p*p,g=m*p,x=e*h,E=x-h,v=-2*g+3*m,_=g-m,A=1-v,w=_-m+p;for(let b=0;b!==c;b++){const B=a[E+b+c],U=a[E+b+u]*f,O=a[x+b+c],V=a[x+b]*f;s[b]=A*B+w*U+v*O+_*V}return s}}const uD=new Et;class hD extends o_{interpolate_(e,t,n,i){const s=super.interpolate_(e,t,n,i);return uD.fromArray(s).normalize().toArray(s),s}}const di={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},$s={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},og={9728:Gn,9729:ai,9984:pg,9985:Mc,9986:Wo,9987:Qi},ag={33071:br,33648:Fc,10497:eo},lh={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},od={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},vr={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},dD={CUBICSPLINE:void 0,LINEAR:ta,STEP:ea},uh={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function fD(r){return r.DefaultMaterial===void 0&&(r.DefaultMaterial=new hs({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:nr})),r.DefaultMaterial}function is(r,e,t){for(const n in t.extensions)r[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function Zi(r,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(r.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function pD(r,e,t){let n=!1,i=!1,s=!1;for(let h=0,f=e.length;h<f;h++){const p=e[h];if(p.POSITION!==void 0&&(n=!0),p.NORMAL!==void 0&&(i=!0),p.COLOR_0!==void 0&&(s=!0),n&&i&&s)break}if(!n&&!i&&!s)return Promise.resolve(r);const a=[],c=[],u=[];for(let h=0,f=e.length;h<f;h++){const p=e[h];if(n){const m=p.POSITION!==void 0?t.getDependency("accessor",p.POSITION):r.attributes.position;a.push(m)}if(i){const m=p.NORMAL!==void 0?t.getDependency("accessor",p.NORMAL):r.attributes.normal;c.push(m)}if(s){const m=p.COLOR_0!==void 0?t.getDependency("accessor",p.COLOR_0):r.attributes.color;u.push(m)}}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u)]).then(function(h){const f=h[0],p=h[1],m=h[2];return n&&(r.morphAttributes.position=f),i&&(r.morphAttributes.normal=p),s&&(r.morphAttributes.color=m),r.morphTargetsRelative=!0,r})}function mD(r,e){if(r.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)r.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(r.morphTargetInfluences.length===t.length){r.morphTargetDictionary={};for(let n=0,i=t.length;n<i;n++)r.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function gD(r){let e;const t=r.extensions&&r.extensions[At.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+hh(t.attributes):e=r.indices+":"+hh(r.attributes)+":"+r.mode,r.targets!==void 0)for(let n=0,i=r.targets.length;n<i;n++)e+=":"+hh(r.targets[n]);return e}function hh(r){let e="";const t=Object.keys(r).sort();for(let n=0,i=t.length;n<i;n++)e+=t[n]+":"+r[t[n]]+";";return e}function ad(r){switch(r){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function _D(r){return r.search(/\.jpe?g($|\?)/i)>0||r.search(/^data\:image\/jpeg/)===0?"image/jpeg":r.search(/\.webp($|\?)/i)>0||r.search(/^data\:image\/webp/)===0?"image/webp":r.search(/\.ktx2($|\?)/i)>0||r.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const vD=new ft;class yD{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new HC,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,i=-1,s=!1,a=-1;if(typeof navigator<"u"){const c=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(c)===!0;const u=c.match(/Version\/(\d+)/);i=n&&u?parseInt(u[1],10):-1,s=c.indexOf("Firefox")>-1,a=s?c.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&i<17||s&&a<98?this.textureLoader=new qP(this.options.manager):this.textureLoader=new JP(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new Ad(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,i=this.json,s=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(a){return a._markDefs&&a._markDefs()}),Promise.all(this._invokeAll(function(a){return a.beforeRoot&&a.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(a){const c={scene:a[0][i.scene||0],scenes:a[0],animations:a[1],cameras:a[2],asset:i.asset,parser:n,userData:{}};return is(s,c,i),Zi(c,i),Promise.all(n._invokeAll(function(u){return u.afterRoot&&u.afterRoot(c)})).then(function(){for(const u of c.scenes)u.updateMatrixWorld();e(c)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let i=0,s=t.length;i<s;i++){const a=t[i].joints;for(let c=0,u=a.length;c<u;c++)e[a[c]].isBone=!0}for(let i=0,s=e.length;i<s;i++){const a=e[i];a.mesh!==void 0&&(this._addNodeRef(this.meshCache,a.mesh),a.skin!==void 0&&(n[a.mesh].isSkinnedMesh=!0)),a.camera!==void 0&&this._addNodeRef(this.cameraCache,a.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const i=n.clone(),s=(a,c)=>{const u=this.associations.get(a);u!=null&&this.associations.set(c,u);for(const[h,f]of a.children.entries())s(f,c.children[h])};return s(n,i),i.name+="_instance_"+e.uses[t]++,i}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const i=e(t[n]);if(i)return i}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let i=0;i<t.length;i++){const s=e(t[i]);s&&n.push(s)}return n}getDependency(e,t){const n=e+":"+t;let i=this.cache.get(n);if(!i){switch(e){case"scene":i=this.loadScene(t);break;case"node":i=this._invokeOne(function(s){return s.loadNode&&s.loadNode(t)});break;case"mesh":i=this._invokeOne(function(s){return s.loadMesh&&s.loadMesh(t)});break;case"accessor":i=this.loadAccessor(t);break;case"bufferView":i=this._invokeOne(function(s){return s.loadBufferView&&s.loadBufferView(t)});break;case"buffer":i=this.loadBuffer(t);break;case"material":i=this._invokeOne(function(s){return s.loadMaterial&&s.loadMaterial(t)});break;case"texture":i=this._invokeOne(function(s){return s.loadTexture&&s.loadTexture(t)});break;case"skin":i=this.loadSkin(t);break;case"animation":i=this._invokeOne(function(s){return s.loadAnimation&&s.loadAnimation(t)});break;case"camera":i=this.loadCamera(t);break;default:if(i=this._invokeOne(function(s){return s!=this&&s.getDependency&&s.getDependency(e,t)}),!i)throw new Error("Unknown type: "+e);break}this.cache.add(n,i)}return i}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,i=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(i.map(function(s,a){return n.getDependency(e,a)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[At.KHR_BINARY_GLTF].body);const i=this.options;return new Promise(function(s,a){n.load(Qo.resolveURL(t.uri,i.path),s,void 0,function(){a(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const i=t.byteLength||0,s=t.byteOffset||0;return n.slice(s,s+i)})}loadAccessor(e){const t=this,n=this.json,i=this.json.accessors[e];if(i.bufferView===void 0&&i.sparse===void 0){const a=lh[i.type],c=$s[i.componentType],u=i.normalized===!0,h=new c(i.count*a);return Promise.resolve(new ln(h,a,u))}const s=[];return i.bufferView!==void 0?s.push(this.getDependency("bufferView",i.bufferView)):s.push(null),i.sparse!==void 0&&(s.push(this.getDependency("bufferView",i.sparse.indices.bufferView)),s.push(this.getDependency("bufferView",i.sparse.values.bufferView))),Promise.all(s).then(function(a){const c=a[0],u=lh[i.type],h=$s[i.componentType],f=h.BYTES_PER_ELEMENT,p=f*u,m=i.byteOffset||0,g=i.bufferView!==void 0?n.bufferViews[i.bufferView].byteStride:void 0,x=i.normalized===!0;let E,v;if(g&&g!==p){const _=Math.floor(m/g),A="InterleavedBuffer:"+i.bufferView+":"+i.componentType+":"+_+":"+i.count;let w=t.cache.get(A);w||(E=new h(c,_*g,i.count*g/f),w=new PP(E,g/f),t.cache.add(A,w)),v=new Md(w,u,m%g/f,x)}else c===null?E=new h(i.count*u):E=new h(c,m,i.count*u),v=new ln(E,u,x);if(i.sparse!==void 0){const _=lh.SCALAR,A=$s[i.sparse.indices.componentType],w=i.sparse.indices.byteOffset||0,b=i.sparse.values.byteOffset||0,B=new A(a[1],w,i.sparse.count*_),U=new h(a[2],b,i.sparse.count*u);c!==null&&(v=new ln(v.array.slice(),v.itemSize,v.normalized)),v.normalized=!1;for(let O=0,V=B.length;O<V;O++){const I=B[O];if(v.setX(I,U[O*u]),u>=2&&v.setY(I,U[O*u+1]),u>=3&&v.setZ(I,U[O*u+2]),u>=4&&v.setW(I,U[O*u+3]),u>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}v.normalized=x}return v})}loadTexture(e){const t=this.json,n=this.options,s=t.textures[e].source,a=t.images[s];let c=this.textureLoader;if(a.uri){const u=n.manager.getHandler(a.uri);u!==null&&(c=u)}return this.loadTextureImage(e,s,c)}loadTextureImage(e,t,n){const i=this,s=this.json,a=s.textures[e],c=s.images[t],u=(c.uri||c.bufferView)+":"+a.sampler;if(this.textureCache[u])return this.textureCache[u];const h=this.loadImageSource(t,n).then(function(f){f.flipY=!1,f.name=a.name||c.name||"",f.name===""&&typeof c.uri=="string"&&c.uri.startsWith("data:image/")===!1&&(f.name=c.uri);const m=(s.samplers||{})[a.sampler]||{};return f.magFilter=og[m.magFilter]||ai,f.minFilter=og[m.minFilter]||Qi,f.wrapS=ag[m.wrapS]||eo,f.wrapT=ag[m.wrapT]||eo,f.generateMipmaps=!f.isCompressedTexture&&f.minFilter!==Gn&&f.minFilter!==ai,i.associations.set(f,{textures:e}),f}).catch(function(){return null});return this.textureCache[u]=h,h}loadImageSource(e,t){const n=this,i=this.json,s=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(p=>p.clone());const a=i.images[e],c=self.URL||self.webkitURL;let u=a.uri||"",h=!1;if(a.bufferView!==void 0)u=n.getDependency("bufferView",a.bufferView).then(function(p){h=!0;const m=new Blob([p],{type:a.mimeType});return u=c.createObjectURL(m),u});else if(a.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const f=Promise.resolve(u).then(function(p){return new Promise(function(m,g){let x=m;t.isImageBitmapLoader===!0&&(x=function(E){const v=new Mn(E);v.needsUpdate=!0,m(v)}),t.load(Qo.resolveURL(p,s.path),x,void 0,g)})}).then(function(p){return h===!0&&c.revokeObjectURL(u),Zi(p,a),p.userData.mimeType=a.mimeType||_D(a.uri),p}).catch(function(p){throw console.error("THREE.GLTFLoader: Couldn't load texture",u),p});return this.sourceCache[e]=f,f}assignTexture(e,t,n,i){const s=this;return this.getDependency("texture",n.index).then(function(a){if(!a)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(a=a.clone(),a.channel=n.texCoord),s.extensions[At.KHR_TEXTURE_TRANSFORM]){const c=n.extensions!==void 0?n.extensions[At.KHR_TEXTURE_TRANSFORM]:void 0;if(c){const u=s.associations.get(a);a=s.extensions[At.KHR_TEXTURE_TRANSFORM].extendTexture(a,c),s.associations.set(a,u)}}return i!==void 0&&(a.colorSpace=i),e[t]=a,a})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const i=t.attributes.tangent===void 0,s=t.attributes.color!==void 0,a=t.attributes.normal===void 0;if(e.isPoints){const c="PointsMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Xg,Di.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,u.sizeAttenuation=!1,this.cache.add(c,u)),n=u}else if(e.isLine){const c="LineBasicMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Gc,Di.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,this.cache.add(c,u)),n=u}if(i||s||a){let c="ClonedMaterial:"+n.uuid+":";i&&(c+="derivative-tangents:"),s&&(c+="vertex-colors:"),a&&(c+="flat-shading:");let u=this.cache.get(c);u||(u=n.clone(),s&&(u.vertexColors=!0),a&&(u.flatShading=!0),i&&(u.normalScale&&(u.normalScale.y*=-1),u.clearcoatNormalScale&&(u.clearcoatNormalScale.y*=-1)),this.cache.add(c,u),this.associations.set(u,this.associations.get(n))),n=u}e.material=n}getMaterialType(){return hs}loadMaterial(e){const t=this,n=this.json,i=this.extensions,s=n.materials[e];let a;const c={},u=s.extensions||{},h=[];if(u[At.KHR_MATERIALS_UNLIT]){const p=i[At.KHR_MATERIALS_UNLIT];a=p.getMaterialType(),h.push(p.extendParams(c,s,t))}else{const p=s.pbrMetallicRoughness||{};if(c.color=new st(1,1,1),c.opacity=1,Array.isArray(p.baseColorFactor)){const m=p.baseColorFactor;c.color.setRGB(m[0],m[1],m[2],Wn),c.opacity=m[3]}p.baseColorTexture!==void 0&&h.push(t.assignTexture(c,"map",p.baseColorTexture,En)),c.metalness=p.metallicFactor!==void 0?p.metallicFactor:1,c.roughness=p.roughnessFactor!==void 0?p.roughnessFactor:1,p.metallicRoughnessTexture!==void 0&&(h.push(t.assignTexture(c,"metalnessMap",p.metallicRoughnessTexture)),h.push(t.assignTexture(c,"roughnessMap",p.metallicRoughnessTexture))),a=this._invokeOne(function(m){return m.getMaterialType&&m.getMaterialType(e)}),h.push(Promise.all(this._invokeAll(function(m){return m.extendMaterialParams&&m.extendMaterialParams(e,c)})))}s.doubleSided===!0&&(c.side=Kn);const f=s.alphaMode||uh.OPAQUE;if(f===uh.BLEND?(c.transparent=!0,c.depthWrite=!1):(c.transparent=!1,f===uh.MASK&&(c.alphaTest=s.alphaCutoff!==void 0?s.alphaCutoff:.5)),s.normalTexture!==void 0&&a!==pi&&(h.push(t.assignTexture(c,"normalMap",s.normalTexture)),c.normalScale=new lt(1,1),s.normalTexture.scale!==void 0)){const p=s.normalTexture.scale;c.normalScale.set(p,p)}if(s.occlusionTexture!==void 0&&a!==pi&&(h.push(t.assignTexture(c,"aoMap",s.occlusionTexture)),s.occlusionTexture.strength!==void 0&&(c.aoMapIntensity=s.occlusionTexture.strength)),s.emissiveFactor!==void 0&&a!==pi){const p=s.emissiveFactor;c.emissive=new st().setRGB(p[0],p[1],p[2],Wn)}return s.emissiveTexture!==void 0&&a!==pi&&h.push(t.assignTexture(c,"emissiveMap",s.emissiveTexture,En)),Promise.all(h).then(function(){const p=new a(c);return s.name&&(p.name=s.name),Zi(p,s),t.associations.set(p,{materials:e}),s.extensions&&is(i,p,s),p})}createUniqueName(e){const t=Bt.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,i=this.primitiveCache;function s(c){return n[At.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(c,t).then(function(u){return cg(u,c,t)})}const a=[];for(let c=0,u=e.length;c<u;c++){const h=e[c],f=gD(h),p=i[f];if(p)a.push(p.promise);else{let m;h.extensions&&h.extensions[At.KHR_DRACO_MESH_COMPRESSION]?m=s(h):m=cg(new _n,h,t),i[f]={primitive:h,promise:m},a.push(m)}}return Promise.all(a)}loadMesh(e){const t=this,n=this.json,i=this.extensions,s=n.meshes[e],a=s.primitives,c=[];for(let u=0,h=a.length;u<h;u++){const f=a[u].material===void 0?fD(this.cache):this.getDependency("material",a[u].material);c.push(f)}return c.push(t.loadGeometries(a)),Promise.all(c).then(function(u){const h=u.slice(0,u.length-1),f=u[u.length-1],p=[];for(let g=0,x=f.length;g<x;g++){const E=f[g],v=a[g];let _;const A=h[g];if(v.mode===di.TRIANGLES||v.mode===di.TRIANGLE_STRIP||v.mode===di.TRIANGLE_FAN||v.mode===void 0)_=s.isSkinnedMesh===!0?new Gg(E,A):new Re(E,A),_.isSkinnedMesh===!0&&_.normalizeSkinWeights(),v.mode===di.TRIANGLE_STRIP?_.geometry=rg(_.geometry,Mg):v.mode===di.TRIANGLE_FAN&&(_.geometry=rg(_.geometry,Jh));else if(v.mode===di.LINES)_=new jg(E,A);else if(v.mode===di.LINE_STRIP)_=new yi(E,A);else if(v.mode===di.LINE_LOOP)_=new FP(E,A);else if(v.mode===di.POINTS)_=new NP(E,A);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+v.mode);Object.keys(_.geometry.morphAttributes).length>0&&mD(_,s),_.name=t.createUniqueName(s.name||"mesh_"+e),Zi(_,s),v.extensions&&is(i,_,v),t.assignFinalMaterial(_),p.push(_)}for(let g=0,x=p.length;g<x;g++)t.associations.set(p[g],{meshes:e,primitives:g});if(p.length===1)return s.extensions&&is(i,p[0],s),p[0];const m=new er;s.extensions&&is(i,m,s),t.associations.set(m,{meshes:e});for(let g=0,x=p.length;g<x;g++)m.add(p[g]);return m})}loadCamera(e){let t;const n=this.json.cameras[e],i=n[n.type];if(!i){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new Vn(Ag.radToDeg(i.yfov),i.aspectRatio||1,i.znear||1,i.zfar||2e6):n.type==="orthographic"&&(t=new bd(-i.xmag,i.xmag,i.ymag,-i.ymag,i.znear,i.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),Zi(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let i=0,s=t.joints.length;i<s;i++)n.push(this._loadNodeShallow(t.joints[i]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(i){const s=i.pop(),a=i,c=[],u=[];for(let h=0,f=a.length;h<f;h++){const p=a[h];if(p){c.push(p);const m=new ft;s!==null&&m.fromArray(s.array,h*16),u.push(m)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[h])}return new ra(c,u)})}loadAnimation(e){const t=this.json,n=this,i=t.animations[e],s=i.name?i.name:"animation_"+e,a=[],c=[],u=[],h=[],f=[];for(let p=0,m=i.channels.length;p<m;p++){const g=i.channels[p],x=i.samplers[g.sampler],E=g.target,v=E.node,_=i.parameters!==void 0?i.parameters[x.input]:x.input,A=i.parameters!==void 0?i.parameters[x.output]:x.output;E.node!==void 0&&(a.push(this.getDependency("node",v)),c.push(this.getDependency("accessor",_)),u.push(this.getDependency("accessor",A)),h.push(x),f.push(E))}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u),Promise.all(h),Promise.all(f)]).then(function(p){const m=p[0],g=p[1],x=p[2],E=p[3],v=p[4],_=[];for(let A=0,w=m.length;A<w;A++){const b=m[A],B=g[A],U=x[A],O=E[A],V=v[A];if(b===void 0)continue;b.updateMatrix&&b.updateMatrix();const I=n._createAnimationTracks(b,B,U,O,V);if(I)for(let R=0;R<I.length;R++)_.push(I[R])}return new oo(s,void 0,_)})}createNodeMesh(e){const t=this.json,n=this,i=t.nodes[e];return i.mesh===void 0?null:n.getDependency("mesh",i.mesh).then(function(s){const a=n._getNodeRef(n.meshCache,i.mesh,s);return i.weights!==void 0&&a.traverse(function(c){if(c.isMesh)for(let u=0,h=i.weights.length;u<h;u++)c.morphTargetInfluences[u]=i.weights[u]}),a})}loadNode(e){const t=this.json,n=this,i=t.nodes[e],s=n._loadNodeShallow(e),a=[],c=i.children||[];for(let h=0,f=c.length;h<f;h++)a.push(n.getDependency("node",c[h]));const u=i.skin===void 0?Promise.resolve(null):n.getDependency("skin",i.skin);return Promise.all([s,Promise.all(a),u]).then(function(h){const f=h[0],p=h[1],m=h[2];m!==null&&f.traverse(function(g){g.isSkinnedMesh&&g.bind(m,vD)});for(let g=0,x=p.length;g<x;g++)f.add(p[g]);return f})}_loadNodeShallow(e){const t=this.json,n=this.extensions,i=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const s=t.nodes[e],a=s.name?i.createUniqueName(s.name):"",c=[],u=i._invokeOne(function(h){return h.createNodeMesh&&h.createNodeMesh(e)});return u&&c.push(u),s.camera!==void 0&&c.push(i.getDependency("camera",s.camera).then(function(h){return i._getNodeRef(i.cameraCache,s.camera,h)})),i._invokeAll(function(h){return h.createNodeAttachment&&h.createNodeAttachment(e)}).forEach(function(h){c.push(h)}),this.nodeCache[e]=Promise.all(c).then(function(h){let f;if(s.isBone===!0?f=new Vc:h.length>1?f=new er:h.length===1?f=h[0]:f=new tn,f!==h[0])for(let p=0,m=h.length;p<m;p++)f.add(h[p]);if(s.name&&(f.userData.name=s.name,f.name=a),Zi(f,s),s.extensions&&is(n,f,s),s.matrix!==void 0){const p=new ft;p.fromArray(s.matrix),f.applyMatrix4(p)}else s.translation!==void 0&&f.position.fromArray(s.translation),s.rotation!==void 0&&f.quaternion.fromArray(s.rotation),s.scale!==void 0&&f.scale.fromArray(s.scale);return i.associations.has(f)||i.associations.set(f,{}),i.associations.get(f).nodes=e,f}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],i=this,s=new er;n.name&&(s.name=i.createUniqueName(n.name)),Zi(s,n),n.extensions&&is(t,s,n);const a=n.nodes||[],c=[];for(let u=0,h=a.length;u<h;u++)c.push(i.getDependency("node",a[u]));return Promise.all(c).then(function(u){for(let f=0,p=u.length;f<p;f++)s.add(u[f]);const h=f=>{const p=new Map;for(const[m,g]of i.associations)(m instanceof Di||m instanceof Mn)&&p.set(m,g);return f.traverse(m=>{const g=i.associations.get(m);g!=null&&p.set(m,g)}),p};return i.associations=h(s),s})}_createAnimationTracks(e,t,n,i,s){const a=[],c=e.name?e.name:e.uuid,u=[];vr[s.path]===vr.weights?e.traverse(function(m){m.morphTargetInfluences&&u.push(m.name?m.name:m.uuid)}):u.push(c);let h;switch(vr[s.path]){case vr.weights:h=so;break;case vr.rotation:h=wr;break;case vr.position:case vr.scale:h=Ar;break;default:switch(n.itemSize){case 1:h=so;break;case 2:case 3:default:h=Ar;break}break}const f=i.interpolation!==void 0?dD[i.interpolation]:ta,p=this._getArrayFromAccessor(n);for(let m=0,g=u.length;m<g;m++){const x=new h(u[m]+"."+vr[s.path],t.array,p,f);i.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(x),a.push(x)}return a}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=ad(t.constructor),i=new Float32Array(t.length);for(let s=0,a=t.length;s<a;s++)i[s]=t[s]*n;t=i}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const i=this instanceof wr?hD:o_;return new i(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function xD(r,e,t){const n=e.attributes,i=new Mi;if(n.POSITION!==void 0){const c=t.json.accessors[n.POSITION],u=c.min,h=c.max;if(u!==void 0&&h!==void 0){if(i.set(new N(u[0],u[1],u[2]),new N(h[0],h[1],h[2])),c.normalized){const f=ad($s[c.componentType]);i.min.multiplyScalar(f),i.max.multiplyScalar(f)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const s=e.targets;if(s!==void 0){const c=new N,u=new N;for(let h=0,f=s.length;h<f;h++){const p=s[h];if(p.POSITION!==void 0){const m=t.json.accessors[p.POSITION],g=m.min,x=m.max;if(g!==void 0&&x!==void 0){if(u.setX(Math.max(Math.abs(g[0]),Math.abs(x[0]))),u.setY(Math.max(Math.abs(g[1]),Math.abs(x[1]))),u.setZ(Math.max(Math.abs(g[2]),Math.abs(x[2]))),m.normalized){const E=ad($s[m.componentType]);u.multiplyScalar(E)}c.max(u)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}i.expandByVector(c)}r.boundingBox=i;const a=new Ii;i.getCenter(a.center),a.radius=i.min.distanceTo(i.max)/2,r.boundingSphere=a}function cg(r,e,t){const n=e.attributes,i=[];function s(a,c){return t.getDependency("accessor",a).then(function(u){r.setAttribute(c,u)})}for(const a in n){const c=od[a]||a.toLowerCase();c in r.attributes||i.push(s(n[a],c))}if(e.indices!==void 0&&!r.index){const a=t.getDependency("accessor",e.indices).then(function(c){r.setIndex(c)});i.push(a)}return Ct.workingColorSpace!==Wn&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${Ct.workingColorSpace}" not supported.`),Zi(r,e),xD(r,e,t),Promise.all(i).then(function(){return e.targets!==void 0?pD(r,e.targets,t):r})}const a_=new zC,bD=new n_;let ao=0;async function SD(r,e){return new Promise((t,n)=>{a_.load(r,i=>{const s=i.scene;e.add(s),s.traverse(u=>{u.isMesh&&(u.castShadow=!0,u.receiveShadow=!0)}),ao++;const a=`Asset ${ao}`,c=Id();c&&Ld(c,a,s),t(s)},void 0,i=>n(i))})}async function ED(r,e){const t=URL.createObjectURL(r);try{return await SD(t,e)}finally{URL.revokeObjectURL(t)}}const MD=[{color:13935988,roughness:.55,metalness:0},{color:13935988,roughness:.55,metalness:0},{color:1118481,roughness:.8,metalness:0},{color:657930,roughness:.1,metalness:0},{color:16052456,roughness:.2,metalness:0},{color:16052456,roughness:.05,metalness:0,opacity:.3,transparent:!0},{color:4881051,roughness:.15,metalness:0},{color:11885162,roughness:.7,metalness:0},{color:15789280,roughness:.3,metalness:0},{color:14723210,roughness:.4,metalness:0},{color:14723210,roughness:.4,metalness:0}];function Lc(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Float32Array(t.buffer)}function c_(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Uint32Array(t.buffer)}function cd(r){for(let e=0;e<r.length;e+=3){const t=r[e+1],n=r[e+2];r[e+1]=n,r[e+2]=-t}}function TD(r){const e=Lc(r.vertices),t=c_(r.faces);cd(e);const n=new _n,i=new ln(e,3),s=new ln(t,1);if(n.setAttribute("position",i),n.setIndex(s),r.uvs){const f=Lc(r.uvs);n.setAttribute("uv",new ln(f,2))}if(r.normals){const f=Lc(r.normals);cd(f),n.setAttribute("normal",new ln(f,3))}else n.computeVertexNormals();const a=MD.map(f=>new hs({color:f.color,roughness:f.roughness,metalness:f.metalness,side:Kn,transparent:f.transparent||!1,opacity:f.opacity!==void 0?f.opacity:1})),c=r.groups||[];let u;if(s&&c.length>0){for(const f of c)n.addGroup(f.start,f.count,f.materialIndex);u=new Re(n,a)}else u=new Re(n,a[0]);u.castShadow=!0,u.receiveShadow=!0;const h=new er;return h.add(u),h}async function dh(r,e,t){const n=new URLSearchParams;if(e.body_type&&n.set("body_type",e.body_type),e.morphs&&typeof e.morphs=="object")for(const[m,g]of Object.entries(e.morphs))g!=null&&n.set(`morph_${m}`,String(g));if(e.user_morphs&&typeof e.user_morphs=="object")for(const[m,g]of Object.entries(e.user_morphs))g!=null&&n.set(`morph_${m}`,String(g));const i=["age","mass","tone","height"],s=e.meta||{};for(const m of i){const g=s[m]??e[`meta_${m}`];g!=null&&n.set(`meta_${m}`,String(g))}const a=`/api/character/mesh/?${n.toString()}`,c=await fetch(a);if(!c.ok)throw new Error(`Character mesh API error: ${c.status}`);const u=await c.json(),h=TD(u);if(r.add(h),h.userData.bodyType=e.body_type||"Female_Caucasian",h.userData.morphs={...e.morphs||{},...e.user_morphs||{}},h.userData.meta={...e.meta||{}},h.userData.presetName=t,e.hair_style&&e.hair_style.url)try{const m=await wD(e.hair_style.url);m.userData.isHair=!0,m.traverse(g=>{g.isMesh&&(g.userData.isHair=!0)}),h.add(m),console.log("✓ Hair loaded:",e.hair_style.name)}catch(m){console.error("Failed to load hair:",m)}if(e.garments&&Array.isArray(e.garments))for(const m of e.garments)try{const g=await AD(m,e.body_type);g.userData.isGarment=!0,h.add(g),console.log("✓ Garment loaded:",m.id)}catch(g){console.error("Failed to load garment:",m.id,g)}ao++;const f=t||`Character ${ao}`,p=Id();return p&&Ld(p,f,h),h}async function wD(r){return new Promise((e,t)=>{a_.load(r,n=>{const i=n.scene;i.traverse(s=>{if(s.isMesh&&(s.castShadow=!0,s.receiveShadow=!0,s.material)){if(s.material.color){const a=s.material.color;a.r>.9&&a.g>.9&&a.b>.9&&s.material.color.setRGB(.1,.08,.06)}s.material.roughness===void 0&&(s.material.roughness=.8),s.material.metalness===void 0&&(s.material.metalness=0)}}),e(i)},void 0,n=>t(n))})}async function AD(r,e){const{id:t,offset:n=.006,stiffness:i=.8,color:s=[.3,.35,.5],roughness:a=.8,metalness:c=0}=r,u=s[0]??.3,h=s[1]??.35,f=s[2]??.5,p=`garment_id=${encodeURIComponent(t)}&body_type=${encodeURIComponent(e)}&offset=${n}&stiffness=${i}&color_r=${u.toFixed(3)}&color_g=${h.toFixed(3)}&color_b=${f.toFixed(3)}`,m=await fetch(`/api/character/garment/fit/?${p}`);if(!m.ok)throw new Error(`Garment fit API error: ${m.status}`);const g=await m.json();if(g.error)throw new Error(g.error);const x=Lc(g.vertices);cd(x);const E=c_(g.faces),v=new _n;v.setAttribute("position",new ln(x,3)),v.setIndex(new ln(E,1)),v.computeVertexNormals();const _=new st(g.color[0],g.color[1],g.color[2]),A=new hs({color:_,roughness:a,metalness:c,side:Kn,polygonOffset:!0,polygonOffsetFactor:-1,polygonOffsetUnit:-1}),w=new Re(v,A);return w.castShadow=!0,w.receiveShadow=!0,w.userData.garmentId=t,w.userData.offset=n,w.userData.stiffness=i,w.userData.originalColor=[u,h,f],w.userData.roughness=a,w.userData.metalness=c,w.name=t,w}function RD(r,e,t){const n=bD.parse(r),i=new Jg(n.skeleton.bones[0]);i.skeleton=n.skeleton,i.visible=!0,i.userData.isRig=!0,i.renderOrder=999,i.material&&(i.material.depthTest=!1,i.material.depthWrite=!1);const s=n.skeleton.bones[0];s.userData.isRig=!0,e.add(s),e.add(i);const a=new Zg(s),c=a.clipAction(n.clip);c.setLoop(gd),c.play(),c.paused=!0,ao++;const u=Id();u&&Ld(u,t||`BVH ${ao}`,s);const h=n.clip.duration||1;return{mixer:a,action:c,skeleton:i,clip:n.clip,rootBone:s,duration:h}}class PD{constructor(e){this._canvas=e,this._recorder=null,this._chunks=[]}start(e=30){const t=this._canvas.captureStream(e);this._chunks=[];const n=MediaRecorder.isTypeSupported("video/webm;codecs=vp9")?"video/webm;codecs=vp9":"video/webm;codecs=vp8";this._recorder=new MediaRecorder(t,{mimeType:n,videoBitsPerSecond:8e6}),this._recorder.ondataavailable=i=>{i.data.size>0&&this._chunks.push(i.data)},this._recorder.start()}stop(){return new Promise(e=>{this._recorder.onstop=()=>{const t=new Blob(this._chunks,{type:"video/webm"});this._chunks=[],e(t)},this._recorder.stop()})}get isRecording(){var e;return((e=this._recorder)==null?void 0:e.state)==="recording"}async stopAndDownload(e="theatre-export.webm"){const t=await this.stop(),n=URL.createObjectURL(t),i=document.createElement("a");i.href=n,i.download=e,i.click(),URL.revokeObjectURL(n)}}async function CD(){const r=await fetch("/api/character/scenes/");if(!r.ok)throw new Error(`Scene list error: ${r.status}`);return(await r.json()).scenes||[]}async function DD(r){const e=await fetch(`/api/character/scene/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Scene load error: ${e.status}`);return e.json()}async function ID(r,e){const t=await fetch("/api/character/scene/save/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:r,data:e})});if(!t.ok){const n=await t.json().catch(()=>({}));throw new Error(n.error||`Scene save error: ${t.status}`)}return t.json()}async function LD(){const r=await fetch("/api/character/models/");if(!r.ok)throw new Error(`Model list error: ${r.status}`);return(await r.json()).presets||[]}async function lg(r){const e=await fetch(`/api/character/model/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Model load error: ${e.status}`);return e.json()}async function FD(){const r=await fetch("/api/character/animations/");if(!r.ok)throw new Error(`Animation list error: ${r.status}`);return(await r.json()).categories||{}}async function ND(r,e){const t=`/api/character/bvh/${encodeURIComponent(r)}/${encodeURIComponent(e)}/`,n=await fetch(t);if(!n.ok)throw new Error(`BVH load error: ${n.status}`);return n.text()}const fh={ballet_stage:{name:"Ballet Stage",description:"Warme Spotlights, theatralisch dunkel",camera:{position:{x:0,y:1.6,z:5},fov:35},lights:{spotLeft:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:-3,y:6,z:3}},spotRight:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:3,y:6,z:3}},backLight:{intensity:25,color:{r:.4,g:.267,b:.667},position:{x:0,y:5,z:-4}}}},studio_bright:{name:"Studio Bright",description:"Helle, gleichmäßige Beleuchtung für Details",camera:{position:{x:0,y:1.6,z:4},fov:40},lights:{spotLeft:{intensity:80,color:{r:1,g:1,b:1},position:{x:-2,y:5,z:4}},spotRight:{intensity:80,color:{r:1,g:1,b:1},position:{x:2,y:5,z:4}},backLight:{intensity:30,color:{r:.9,g:.95,b:1},position:{x:0,y:4,z:-3}}}},cinematic_moody:{name:"Cinematic Moody",description:"Dramatisches Film-noir-Licht, starke Schatten",camera:{position:{x:2,y:1.4,z:4},fov:28},lights:{spotLeft:{intensity:15,color:{r:1,g:.8,b:.6},position:{x:-4,y:7,z:2}},spotRight:{intensity:2,color:{r:.6,g:.7,b:.9},position:{x:4,y:3,z:3}},backLight:{intensity:10,color:{r:.3,g:.5,b:1},position:{x:1,y:6,z:-5}}}},fashion_show:{name:"Fashion Show",description:"Laufsteg-Beleuchtung, kühles Weiß von oben",camera:{position:{x:0,y:1.2,z:6},fov:50},lights:{spotLeft:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:-2,y:8,z:2}},spotRight:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:2,y:8,z:2}},backLight:{intensity:5,color:{r:1,g:1,b:1},position:{x:0,y:3,z:-2}}}},sunset_warm:{name:"Sunset Warm",description:"Goldene Stunde, warmes Orange-Gold",camera:{position:{x:-1,y:1.5,z:4.5},fov:42},lights:{spotLeft:{intensity:14,color:{r:1,g:.7,b:.4},position:{x:-5,y:4,z:3}},spotRight:{intensity:6,color:{r:1,g:.85,b:.7},position:{x:3,y:5,z:2}},backLight:{intensity:8,color:{r:.8,g:.4,b:.6},position:{x:2,y:5,z:-4}}}}};function ph(r,e,t,n){console.log(`[Preset] Applying: ${r.name}`),e.position.set(r.camera.position.x,r.camera.position.y,r.camera.position.z),e.fov=r.camera.fov,e.updateProjectionMatrix(),n&&(n.target.set(0,.9,0),n.update()),mh(t.spotLeft,r.lights.spotLeft),mh(t.spotRight,r.lights.spotRight),mh(t.backLight,r.lights.backLight),console.log(`✓ Preset "${r.name}" applied (direct Three.js)`)}function mh(r,e){r&&(r.intensity=e.intensity,r.color.setRGB(e.color.r,e.color.g,e.color.b),r.position.set(e.position.x,e.position.y,e.position.z))}const OD={Hips:"DEF-spine",Spine:"DEF-spine.001",Spine1:"DEF-spine.003",Neck:null,Neck1:"DEF-spine.004",Head:"DEF-spine.006",LeftShoulder:"DEF-shoulder.L",LeftArm:"DEF-upper_arm.L",LeftForeArm:"DEF-forearm.L",LeftHand:"DEF-hand.L",RightShoulder:"DEF-shoulder.R",RightArm:"DEF-upper_arm.R",RightForeArm:"DEF-forearm.R",RightHand:"DEF-hand.R",LeftUpLeg:"DEF-thigh.L",LeftLeg:"DEF-shin.L",LeftFoot:"DEF-foot.L",LeftToeBase:"DEF-toe.L",RightUpLeg:"DEF-thigh.R",RightLeg:"DEF-shin.R",RightFoot:"DEF-foot.R",RightToeBase:"DEF-toe.R",LHipJoint:null,RHipJoint:null,LowerBack:null,LeftFingerBase:null,RightFingerBase:null,LThumb:null,RThumb:null},UD={Hips:"DEF-spine",Spine:"DEF-spine.001",Spine1:"DEF-spine.002",Spine2:"DEF-spine.003",Neck:null,Neck1:"DEF-spine.004",Head:"DEF-spine.006",LeftShoulder:"DEF-shoulder.L",LeftArm:"DEF-upper_arm.L",LeftForeArm:"DEF-forearm.L",LeftHand:"DEF-hand.L",RightShoulder:"DEF-shoulder.R",RightArm:"DEF-upper_arm.R",RightForeArm:"DEF-forearm.R",RightHand:"DEF-hand.R",LeftUpLeg:"DEF-thigh.L",LeftLeg:"DEF-shin.L",LeftFoot:"DEF-foot.L",LeftToeBase:"DEF-toe.L",RightUpLeg:"DEF-thigh.R",RightLeg:"DEF-shin.R",RightFoot:"DEF-foot.R",RightToeBase:"DEF-toe.R",LeftHandThumb1:"DEF-thumb.01.L",LeftHandThumb2:"DEF-thumb.02.L",LeftHandThumb3:"DEF-thumb.03.L",LeftHandIndex1:"DEF-f_index.01.L",LeftHandIndex2:"DEF-f_index.02.L",LeftHandIndex3:"DEF-f_index.03.L",LeftHandMiddle1:"DEF-f_middle.01.L",LeftHandMiddle2:"DEF-f_middle.02.L",LeftHandMiddle3:"DEF-f_middle.03.L",LeftHandRing1:"DEF-f_ring.01.L",LeftHandRing2:"DEF-f_ring.02.L",LeftHandRing3:"DEF-f_ring.03.L",LeftHandPinky1:"DEF-f_pinky.01.L",LeftHandPinky2:"DEF-f_pinky.02.L",LeftHandPinky3:"DEF-f_pinky.03.L",RightHandThumb1:"DEF-thumb.01.R",RightHandThumb2:"DEF-thumb.02.R",RightHandThumb3:"DEF-thumb.03.R",RightHandIndex1:"DEF-f_index.01.R",RightHandIndex2:"DEF-f_index.02.R",RightHandIndex3:"DEF-f_index.03.R",RightHandMiddle1:"DEF-f_middle.01.R",RightHandMiddle2:"DEF-f_middle.02.R",RightHandMiddle3:"DEF-f_middle.03.R",RightHandRing1:"DEF-f_ring.01.R",RightHandRing2:"DEF-f_ring.02.R",RightHandRing3:"DEF-f_ring.03.R",RightHandPinky1:"DEF-f_pinky.01.R",RightHandPinky2:"DEF-f_pinky.02.R",RightHandPinky3:"DEF-f_pinky.03.R"},BD={hip:"DEF-spine",abdomen:"DEF-spine.001",chest:"DEF-spine.003",neck1:"DEF-spine.004",head:"DEF-spine.006",lcollar:"DEF-shoulder.L",rcollar:"DEF-shoulder.R",lshoulder:"DEF-upper_arm.L",rshoulder:"DEF-upper_arm.R",lelbow:"DEF-forearm.L",relbow:"DEF-forearm.R",lhand:"DEF-hand.L",rhand:"DEF-hand.R",lhip:"DEF-thigh.L",rhip:"DEF-thigh.R",lknee:"DEF-shin.L",rknee:"DEF-shin.R",lfoot:"DEF-foot.L",rfoot:"DEF-foot.R","toe1-1.l":"DEF-toe.L","toe1-1.r":"DEF-toe.R",lCollar:"DEF-shoulder.L",rCollar:"DEF-shoulder.R",lShldr:"DEF-upper_arm.L",rShldr:"DEF-upper_arm.R",lForeArm:"DEF-forearm.L",rForeArm:"DEF-forearm.R",lHand:"DEF-hand.L",rHand:"DEF-hand.R",lThigh:"DEF-thigh.L",rThigh:"DEF-thigh.R",lShin:"DEF-shin.L",rShin:"DEF-shin.R",lFoot:"DEF-foot.L",rFoot:"DEF-foot.R",lButtock:null,rButtock:null,"toe1-1.L":"DEF-toe.L","toe1-1.R":"DEF-toe.R",lthumb:"DEF-thumb.01.L","finger1-2.l":"DEF-thumb.02.L","finger1-3.l":"DEF-thumb.03.L","finger2-1.l":"DEF-f_index.01.L","finger2-2.l":"DEF-f_index.02.L","finger2-3.l":"DEF-f_index.03.L","finger3-1.l":"DEF-f_middle.01.L","finger3-2.l":"DEF-f_middle.02.L","finger3-3.l":"DEF-f_middle.03.L","finger4-1.l":"DEF-f_ring.01.L","finger4-2.l":"DEF-f_ring.02.L","finger4-3.l":"DEF-f_ring.03.L","finger5-1.l":"DEF-f_pinky.01.L","finger5-2.l":"DEF-f_pinky.02.L","finger5-3.l":"DEF-f_pinky.03.L",rthumb:"DEF-thumb.01.R","finger1-2.r":"DEF-thumb.02.R","finger1-3.r":"DEF-thumb.03.R","finger2-1.r":"DEF-f_index.01.R","finger2-2.r":"DEF-f_index.02.R","finger2-3.r":"DEF-f_index.03.R","finger3-1.r":"DEF-f_middle.01.R","finger3-2.r":"DEF-f_middle.02.R","finger3-3.r":"DEF-f_middle.03.R","finger4-1.r":"DEF-f_ring.01.R","finger4-2.r":"DEF-f_ring.02.R","finger4-3.r":"DEF-f_ring.03.R","finger5-1.r":"DEF-f_pinky.01.R","finger5-2.r":"DEF-f_pinky.02.R","finger5-3.r":"DEF-f_pinky.03.R","metacarpal1.l":"DEF-palm.01.L","metacarpal2.l":"DEF-palm.02.L","metacarpal3.l":"DEF-palm.03.L","metacarpal4.l":"DEF-palm.04.L","metacarpal1.r":"DEF-palm.01.R","metacarpal2.r":"DEF-palm.02.R","metacarpal3.r":"DEF-palm.03.R","metacarpal4.r":"DEF-palm.04.R",jaw:"DEF-jaw",tongue01:"DEF-tongue",tongue02:"DEF-tongue.001",tongue03:"DEF-tongue.002","eye.l":"MCH-eye.L","eye.r":"MCH-eye.R","oris04.l":"DEF-lip.T.L","oris04.r":"DEF-lip.T.R","oris03.l":"DEF-lip.T.L.001","oris03.r":"DEF-lip.T.R.001","oris06.l":"DEF-lip.B.L","oris06.r":"DEF-lip.B.R","oris07.l":"DEF-lip.B.L.001","oris07.r":"DEF-lip.B.R.001","orbicularis03.l":"DEF-lid.T.L","orbicularis03.r":"DEF-lid.T.R","orbicularis04.l":"DEF-lid.B.L","orbicularis04.r":"DEF-lid.B.R"},kD={Pelvis:"DEF-spine",Spine1:"DEF-spine.001",Spine2:"DEF-spine.002",Spine3:"DEF-spine.003",Neck:"DEF-spine.004",Head:"DEF-spine.006",Left_collar:"DEF-shoulder.L",Left_shoulder:"DEF-upper_arm.L",Left_elbow:"DEF-forearm.L",Left_wrist:"DEF-hand.L",Left_palm:null,Right_collar:"DEF-shoulder.R",Right_shoulder:"DEF-upper_arm.R",Right_elbow:"DEF-forearm.R",Right_wrist:"DEF-hand.R",Right_palm:null,Left_hip:"DEF-thigh.L",Left_knee:"DEF-shin.L",Left_ankle:"DEF-foot.L",Left_foot:"DEF-toe.L",Right_hip:"DEF-thigh.R",Right_knee:"DEF-shin.R",Right_ankle:"DEF-foot.R",Right_foot:"DEF-toe.R"},zD={hip:"DEF-spine",abdomen:"DEF-spine.001",chest:"DEF-spine.003",neck:null,neck1:"DEF-spine.004",head:"DEF-spine.006",lCollar:"DEF-shoulder.L",rCollar:"DEF-shoulder.R",lShldr:"DEF-upper_arm.L",rShldr:"DEF-upper_arm.R",lForeArm:"DEF-forearm.L",rForeArm:"DEF-forearm.R",lHand:"DEF-hand.L",rHand:"DEF-hand.R",lButtock:null,rButtock:null,lThigh:"DEF-thigh.L",rThigh:"DEF-thigh.R",lShin:"DEF-shin.L",rShin:"DEF-shin.R",lFoot:"DEF-foot.L",rFoot:"DEF-foot.R","toe1-1.L":"DEF-toe.L","toe1-1.R":"DEF-toe.R",lthumb:"DEF-thumb.01.L","finger1-2.l":"DEF-thumb.02.L","finger1-3.l":"DEF-thumb.03.L","finger2-1.l":"DEF-f_index.01.L","finger2-2.l":"DEF-f_index.02.L","finger2-3.l":"DEF-f_index.03.L","finger3-1.l":"DEF-f_middle.01.L","finger3-2.l":"DEF-f_middle.02.L","finger3-3.l":"DEF-f_middle.03.L","finger4-1.l":"DEF-f_ring.01.L","finger4-2.l":"DEF-f_ring.02.L","finger4-3.l":"DEF-f_ring.03.L","finger5-1.l":"DEF-f_pinky.01.L","finger5-2.l":"DEF-f_pinky.02.L","finger5-3.l":"DEF-f_pinky.03.L",rthumb:"DEF-thumb.01.R","finger1-2.r":"DEF-thumb.02.R","finger1-3.r":"DEF-thumb.03.R","finger2-1.r":"DEF-f_index.01.R","finger2-2.r":"DEF-f_index.02.R","finger2-3.r":"DEF-f_index.03.R","finger3-1.r":"DEF-f_middle.01.R","finger3-2.r":"DEF-f_middle.02.R","finger3-3.r":"DEF-f_middle.03.R","finger4-1.r":"DEF-f_ring.01.R","finger4-2.r":"DEF-f_ring.02.R","finger4-3.r":"DEF-f_ring.03.R","finger5-1.r":"DEF-f_pinky.01.R","finger5-2.r":"DEF-f_pinky.02.R","finger5-3.r":"DEF-f_pinky.03.R","metacarpal1.l":"DEF-palm.01.L","metacarpal2.l":"DEF-palm.02.L","metacarpal3.l":"DEF-palm.03.L","metacarpal4.l":"DEF-palm.04.L","metacarpal1.r":"DEF-palm.01.R","metacarpal2.r":"DEF-palm.02.R","metacarpal3.r":"DEF-palm.03.R","metacarpal4.r":"DEF-palm.04.R",jaw:"DEF-jaw",tongue01:"DEF-tongue",tongue02:"DEF-tongue.001",tongue03:"DEF-tongue.002","eye.l":"MCH-eye.L","eye.r":"MCH-eye.R","oris04.l":"DEF-lip.T.L","oris04.r":"DEF-lip.T.R","oris03.l":"DEF-lip.T.L.001","oris03.r":"DEF-lip.T.R.001","oris06.l":"DEF-lip.B.L","oris06.r":"DEF-lip.B.R","oris07.l":"DEF-lip.B.L.001","oris07.r":"DEF-lip.B.R.001","orbicularis03.l":"DEF-lid.T.L","orbicularis03.r":"DEF-lid.T.R","orbicularis04.l":"DEF-lid.B.L","orbicularis04.r":"DEF-lid.B.R"},HD={Hips:"DEF-spine",Spine:"DEF-spine.001",Chest:"DEF-spine.003",Neck:"DEF-spine.004",Head:"DEF-spine.006",Shoulder_L:"DEF-shoulder.L",UpperArm_L:"DEF-upper_arm.L",LowerArm_L:"DEF-forearm.L",Hand_L:"DEF-hand.L",Shoulder_R:"DEF-shoulder.R",UpperArm_R:"DEF-upper_arm.R",LowerArm_R:"DEF-forearm.R",Hand_R:"DEF-hand.R",UpperLeg_L:"DEF-thigh.L",LowerLeg_L:"DEF-shin.L",Foot_L:"DEF-foot.L",Toes_L:"DEF-toe.L",UpperLeg_R:"DEF-thigh.R",LowerLeg_R:"DEF-shin.R",Foot_R:"DEF-foot.R",Toes_R:"DEF-toe.R",joint_Root:null};function VD(r,e,t,n={}){const i=r.skeleton.bones,s=r.clip,a=t==="CMU"?OD:t==="MIXAMO"?UD:t==="BANDAI"?HD:t==="AIST"?kD:t==="OPENPOSE"?zD:BD;e.rootBone.updateWorldMatrix(!0,!0);const c={},u={},h=new Map;for(const[pe,ve]of Object.entries(e.boneByName))h.set(ve,pe);for(const[pe,ve]of Object.entries(e.boneByName)){c[pe]=new Et,ve.getWorldQuaternion(c[pe]);const Le=h.get(ve.parent);Le&&c[Le]?u[pe]=c[Le]:ve.parent&&(u[pe]=new Et,ve.parent.getWorldQuaternion(u[pe]))}const f={};for(const pe of i)f[pe.name]=pe;const p=i[0],m=[],g={};function x(pe){m.push(pe.name);for(const ve of pe.children)ve.isBone&&(g[ve.name]=pe.name,x(ve))}x(p);const E={};for(const[pe,ve]of Object.entries(a))ve&&f[pe]&&e.boneByName[ve]&&(E[ve]=pe);const v=new Set(Object.keys(E));console.log(`[RETARGET] ${v.size} bones mapped`);const _={},A={};for(const pe of s.tracks){const ve=pe.name.lastIndexOf(".");if(ve<0)continue;const Le=pe.name.substring(0,ve),G=pe.name.substring(ve+1);G==="quaternion"&&(_[Le]=pe),G==="position"&&(A[Le]=pe)}const w=new Mi,b=new Et,B=new N;function U(pe,ve,Le){B.copy(pe.position).applyQuaternion(ve);const G=Le.clone().add(B);w.expandByPoint(G),b.copy(ve).multiply(pe.quaternion);for(const tt of pe.children)tt.isBone&&U(tt,b.clone(),G)}U(p,new Et,new N);const O=Math.max(w.max.y-w.min.y,.01);let V=1.68;if(n.bodyMesh){const pe=new Mi().setFromObject(n.bodyMesh);pe.isEmpty()||(V=pe.max.y-pe.min.y)}const I=V/O,R={};for(const[pe,ve]of Object.entries(e.boneByName))u[pe]?R[pe]=u[pe].clone().invert().multiply(c[pe]):R[pe]=c[pe].clone();const H={},ee=t==="BANDAI";if(ee){const pe=new Et;for(const ve of m){const Le=_[ve];Le?pe.set(Le.values[0],Le.values[1],Le.values[2],Le.values[3]):pe.set(0,0,0,1);const G=g[ve];G&&H[G]?H[ve]=H[G].clone().multiply(pe):H[ve]=pe.clone()}}const te=new N(0,0,-1),se={},he=Object.values(a).find(pe=>pe&&e.boneByName[pe]),q=new Set;t==="AIST"&&(q.add("DEF-foot.L"),q.add("DEF-foot.R"),q.add("DEF-toe.L"),q.add("DEF-toe.R"),q.add("DEF-spine.004"),q.add("DEF-spine.006")),t==="MOCAPNET"&&(q.add("DEF-foot.L"),q.add("DEF-foot.R"),q.add("DEF-toe.L"),q.add("DEF-toe.R"),q.add("DEF-jaw"),q.add("DEF-spine.004"),q.add("DEF-spine.006")),t==="OPENPOSE"&&(q.add("DEF-foot.L"),q.add("DEF-foot.R"),q.add("DEF-toe.L"),q.add("DEF-toe.R"),q.add("DEF-jaw"),q.add("DEF-spine.004"),q.add("DEF-spine.006"),q.add("DEF-shoulder.L"),q.add("DEF-shoulder.R"));for(const[pe,ve]of Object.entries(E)){if(pe===he||q.has(pe)){se[pe]=c[pe].clone();continue}const Le=te.clone().applyQuaternion(c[pe]).normalize(),G=f[ve];let tt=null,Ke=-1/0;for(const Qe of G.children)if(Qe.isBone&&Qe.position.lengthSq()>1e-10){let Oe;ee&&H[ve]?Oe=Qe.position.clone().applyQuaternion(H[ve]).normalize():Oe=Qe.position.clone().normalize();const rt=Oe.dot(Le);rt>Ke&&(Ke=rt,tt=Oe)}if(!tt&&G.position.lengthSq()>1e-10)if(ee){const Qe=g[ve];Qe&&H[Qe]?tt=G.position.clone().applyQuaternion(H[Qe]).normalize():tt=G.position.clone().normalize()}else tt=G.position.clone().normalize();if(!tt||tt.lengthSq()<1e-10)se[pe]=c[pe].clone();else{const Qe=new Et().setFromUnitVectors(Le,tt);se[pe]=Qe.multiply(c[pe])}}const de=Object.keys(e.boneByName).sort((pe,ve)=>{let Le=0,G=e.boneByName[pe];for(;G.parent;)Le++,G=G.parent;let tt=0,Ke=e.boneByName[ve];for(;Ke.parent;)tt++,Ke=Ke.parent;return Le-tt}),re=Object.values(_)[0];if(!re)return new oo("retargeted",0,[]);const ge=re.times,be=ge.length,ze={};for(const pe of v)ze[pe]=new Float32Array(be*4);const Ge=new Et,pt=new Et,le={},me={};let Ue=null;if(n.footCorrection){Ue={};const pe=new Et,ve=new N,Le=180/Math.PI,G=15,tt=1.5;for(const Ke of["DEF-foot.L","DEF-foot.R"]){const Qe=E[Ke];if(!Qe)continue;const Oe=[];let rt=Qe;for(;rt;)Oe.unshift(rt),rt=g[rt];const Fe=new Float32Array(be);let F=0,T=0;for(let Z=0;Z<be;Z++){const ce=Z*4;let fe=new Et;for(const ke of Oe){const we=_[ke];we?pe.set(we.values[ce],we.values[ce+1],we.values[ce+2],we.values[ce+3]):pe.set(0,0,0,1),fe.multiply(pe)}ve.set(0,0,-1).applyQuaternion(fe);const ue=Math.asin(Math.max(-1,Math.min(1,-ve.y)))*Le;if(ue>T&&(T=ue),ue>G){const ke=Math.min(90,ue+(ue-G)*tt),we=90-ue;Fe[Z]=we>.1?Math.min((ke-ue)/we,1):0}Fe[Z]>F&&(F=Fe[Z])}Ue[Ke]=Fe,console.log(`[FOOT-CORRECTION] ${Ke}: maxAngle=${T.toFixed(1)}, thresh=${G}, boost=${tt}x, maxCorr=${F.toFixed(2)}`)}Object.keys(Ue).length===0&&(Ue=null)}for(let pe=0;pe<be;pe++){const ve=pe*4;for(const Le of m){const G=_[Le];G?Ge.set(G.values[ve],G.values[ve+1],G.values[ve+2],G.values[ve+3]):Ge.set(0,0,0,1);const tt=g[Le];tt&&me[tt]?me[Le]=me[tt].clone().multiply(Ge):me[Le]=Ge.clone()}for(const Le of de){const G=e.boneByName[Le],tt=h.get(G.parent),Ke=tt&&le[tt]?le[tt]:new Et;if(v.has(Le)){const Qe=E[Le];if(ee){const rt=me[Qe],Fe=H[Qe];rt&&Fe?(pt.copy(rt).multiply(Fe.clone().invert()).multiply(se[Le]).normalize(),Ge.copy(Ke).invert().multiply(pt).normalize()):Ge.copy(R[Le]||new Et)}else{const rt=me[Qe];rt?(pt.copy(rt).multiply(se[Le]).normalize(),Ge.copy(Ke).invert().multiply(pt).normalize()):Ge.copy(R[Le]||new Et)}if(Ue&&Ue[Le]){const rt=Ue[Le][pe];if(rt>.01){const Fe=Ke.clone().multiply(Ge),F=new N(0,0,-1).applyQuaternion(Fe).normalize(),T=new N(0,-1,0),ce=new Et().setFromUnitVectors(F,T).multiply(Fe),fe=Ke.clone().invert().multiply(ce).normalize();Ge.slerp(fe,rt)}}const Oe=ze[Le];Oe[ve]=Ge.x,Oe[ve+1]=Ge.y,Oe[ve+2]=Ge.z,Oe[ve+3]=Ge.w,le[Le]=Ke.clone().multiply(Ge)}else le[Le]=Ke.clone().multiply(R[Le]||new Et)}}const Se=[];for(const pe of v){const ve=e.boneByName[pe];Se.push(new wr(`${ve.name}.quaternion`,ge,ze[pe]))}const $e=i[0].name;let it=a[$e];const Je=A[$e];if(!it&&Je){for(const pe of i[0].children)if(pe.isBone&&a[pe.name]){it=a[pe.name];break}}if(it&&Je){const pe=e.boneByName[it];if(pe){const ve=new N(Je.values[0],Je.values[1],Je.values[2]),Le=pe.position.clone(),G=new Float32Array(Je.values.length);for(let tt=0;tt<Je.values.length;tt+=3)G[tt]=Le.x+(Je.values[tt]-ve.x)*I,G[tt+1]=Le.y+(Je.values[tt+1]-ve.y)*I,G[tt+2]=Le.z+(Je.values[tt+2]-ve.z)*I;Se.push(new Ar(`${pe.name}.position`,Je.times,G))}}return console.log(`[RETARGET] ${Se.length} tracks, ${be} frames`),new oo("retargeted",s.duration,Se)}window.addEventListener("DOMContentLoaded",()=>{const r=document.getElementById("theatre-canvas");if(!r){console.error("theatre-canvas not found");return}const{scene:e,camera:t,renderer:n,controls:i,lights:s,lightIcons:a,transformControls:c}=OC(r);window.scene=e,window.lights=s,window.lightIcons=a,window.transformControls=c,window.activeMixer=null,window.isPlaying=!1,window.currentTime=0,window.animDuration=1;const u=new Qg,h=new lt;let f=null,p=null;const m=[];let g=null,x=null;async function E(){try{const[P,k]=await Promise.all([fetch("/api/character/def-skeleton/"),fetch("/api/character/skin-weights/")]);P.ok&&(g=await P.json()),k.ok&&(x=await k.json()),console.log("✓ Loaded skeleton and skin weights")}catch(P){console.warn("Failed to load skeleton/weights:",P)}}E();function v(P,k,$,ie){const Ee=new n_().parse(P);if(!g)throw console.error("DEF skeleton data not loaded - cannot retarget animation"),new Error("Skeleton data not loaded");if(!k||!k.skeleton)throw console.error("SkinnedMesh has no skeleton"),new Error("SkinnedMesh not properly initialized");if(!k.skeleton.bones||k.skeleton.bones.length===0)throw console.error("SkinnedMesh skeleton has no bones"),new Error("Skeleton has no bones");const De={skeleton:k.skeleton,rootBone:k.skeleton.bones[0],bones:k.skeleton.bones,boneByName:{}};for(const mt of k.skeleton.bones)De.boneByName[mt.name]=mt;const Pe=VD(Ee,De,ie||Ee.clip.name);if(!Pe||Pe.tracks.length===0)throw console.error("Retargeting failed - no tracks generated"),new Error("Retargeting failed");const ut=new Zg(k),bt=ut.clipAction(Pe);bt.setLoop(gd),bt.play(),bt.paused=!0;const Ft=Pe.duration||1;return console.log("✓ BVH animation retargeted and loaded on SkinnedMesh:",ie,Ft+"s",Pe.tracks.length,"tracks"),{mixer:ut,action:bt,duration:Ft}}function _(P,k){if(!g||!x)return console.warn("Cannot convert to SkinnedMesh: skeleton/weights not loaded"),null;if(P.userData.isSkinnedMesh)return console.log("Already a SkinnedMesh"),P.userData.skinnedMesh;const $=P.children.find(Tt=>Tt.isMesh);if(!$)return console.warn("No mesh found in character group"),null;console.log("Converting to SkinnedMesh...");const ie=$.geometry.clone(),Te=ie.attributes.position.count,Ee=new Float32Array(Te*4),De=new Float32Array(Te*4);for(let Tt=0;Tt<Te;Tt++){const nn=x.indices[Tt]||[0,0,0,0],Tn=x.weights[Tt]||[1,0,0,0];Ee[Tt*4+0]=nn[0],Ee[Tt*4+1]=nn[1],Ee[Tt*4+2]=nn[2],Ee[Tt*4+3]=nn[3],De[Tt*4+0]=Tn[0],De[Tt*4+1]=Tn[1],De[Tt*4+2]=Tn[2],De[Tt*4+3]=Tn[3]}ie.setAttribute("skinIndex",new $t(Ee,4)),ie.setAttribute("skinWeight",new $t(De,4));const Pe=[],ut=[];for(const Tt of g.bones){const nn=new Vc;nn.name=Tt.name,nn.position.fromArray(Tt.position),nn.quaternion.fromArray(Tt.quaternion),nn.scale.fromArray(Tt.scale),Pe.push(nn);const Tn=new ft;Tt.inverse&&Tn.fromArray(Tt.inverse),ut.push(Tn)}for(let Tt=0;Tt<g.bones.length;Tt++){const nn=g.bones[Tt].parent;nn>=0&&Pe[nn].add(Pe[Tt])}const bt=new ra(Pe,ut),Ft=Pe[0],mt=$.material,nt=new Gg(ie,mt);nt.castShadow=!0,nt.receiveShadow=!0,nt.add(Ft),nt.bind(bt);const jt=$.position.clone(),Dt=$.rotation.clone(),Xt=$.scale.clone();P.remove($),nt.position.copy(jt),nt.rotation.copy(Dt),nt.scale.copy(Xt),P.add(nt);const qt=new Jg(Ft);return qt.visible=!1,qt.material.linewidth=2,qt.userData.isRig=!0,k.add(qt),P.userData.isSkinnedMesh=!0,P.userData.skinnedMesh=nt,P.userData.skeleton=bt,P.userData.rootBone=Ft,P.userData.skeletonHelper=qt,console.log("✓ Converted to SkinnedMesh with",Pe.length,"bones"),nt}r.addEventListener("click",P=>{const k=r.getBoundingClientRect();h.x=(P.clientX-k.left)/k.width*2-1,h.y=-((P.clientY-k.top)/k.height)*2+1,u.setFromCamera(h,t);const $=[a.spotLeftIcon,a.spotRightIcon,a.backLightIcon],ie=u.intersectObjects($,!0);if(ie.length>0){let Ee=ie[0].object;for(;Ee.parent&&!Ee.userData.light;)Ee=Ee.parent;if(Ee.userData.light){f=Ee,p=null,c.attach(Ee),console.log("✓ Licht ausgewählt:",Ee.userData.light),We(Ee.userData.light);return}}const Te=u.intersectObjects(m,!0);if(Te.length>0){const Ee=Te[0].object;if(Ee.userData.isGarment){p=null,f=null,c.attach(Ee),console.log("✓ Garment ausgewählt:",Ee.name),ot(Ee);return}let De=Ee;for(;De.parent&&!De.userData.isCharacter;)De=De.parent;if(De.userData.isCharacter){p=De,f=null,c.attach(De),console.log("✓ Character ausgewählt:",De.userData.presetName),Ve(De);return}}c.detach(),f=null,p=null,X()});const{sheet:A}=BC();kC(A,t),Ec(A,"Spot Left",s.spotLeft),Ec(A,"Spot Right",s.spotRight),Ec(A,"Back Light",s.backLight);const w=new PD(n.domElement);let b=null,B=null;const U=new eC;document.querySelectorAll(".menu-item").forEach(P=>{const k=P.querySelector(".menu-dropdown");k&&(P.addEventListener("click",$=>{$.stopPropagation(),document.querySelectorAll(".menu-item").forEach(ie=>ie.classList.remove("active")),P.classList.toggle("active")}),k.addEventListener("click",$=>{$.stopPropagation()}))}),document.addEventListener("click",()=>{document.querySelectorAll(".menu-item").forEach(P=>P.classList.remove("active"))}),document.querySelectorAll("[data-preset]").forEach(P=>{P.addEventListener("click",()=>{const k=P.getAttribute("data-preset"),$=fh[k];$?(ph($,t,s,i),console.log("✓ Applied preset:",$.name),document.querySelectorAll(".menu-item").forEach(ie=>ie.classList.remove("active"))):console.error("Preset not found:",k)})}),document.querySelectorAll(".panel-tab").forEach(P=>{P.addEventListener("click",()=>{const k=P.getAttribute("data-tab");document.querySelectorAll(".panel-tab").forEach(ie=>ie.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(ie=>ie.classList.remove("active")),P.classList.add("active");const $=document.getElementById(k);$&&$.classList.add("active")})});const O=document.getElementById("btn-translate-mode"),V=document.getElementById("btn-rotate-mode"),I=document.getElementById("btn-toggle-lights");O&&O.addEventListener("click",()=>{c.setMode("translate"),O.classList.add("active"),V.classList.remove("active")}),V&&V.addEventListener("click",()=>{c.setMode("rotate"),V.classList.add("active"),O.classList.remove("active")});let R=!0;I&&I.addEventListener("click",()=>{R=!R,Object.values(a).forEach(P=>{P.visible=R}),R?I.classList.add("active"):I.classList.remove("active")});const H=document.getElementById("btn-toggle-model");let ee=!0;H&&H.addEventListener("click",()=>{ee=!ee,e.traverse(P=>{P.isMesh&&!P.userData.isGarment&&!P.userData.isHair&&!P.userData.isRig&&(P.visible=ee)}),H.classList.toggle("active",ee)});const te=document.getElementById("btn-toggle-clothes");let se=!0;te&&te.addEventListener("click",()=>{se=!se,e.traverse(P=>{P.isMesh&&(P.userData.isGarment||P.userData.isHair)&&(P.visible=se)}),te.classList.toggle("active",se)});const he=document.getElementById("btn-toggle-rig");let q=!1;he&&he.addEventListener("click",()=>{q=!q,e.traverse(P=>{(P.isSkeletonHelper||P.userData.isRig)&&(P.visible=q)}),he.classList.toggle("active",q)});const de=document.getElementById("btn-play-animation");de&&de.addEventListener("click",()=>{const P=document.getElementById("btnPlayPause");P&&P.click()});function re(P){const k=document.getElementById(P);k&&(k.style.display="flex")}function ge(P){const k=document.getElementById(P);k&&(k.style.display="none")}document.querySelectorAll("[data-close-modal]").forEach(P=>{P.addEventListener("click",()=>{var k;(k=P.closest(".theatre-modal-overlay"))==null||k.style.removeProperty("display")})}),document.querySelectorAll(".theatre-modal-overlay").forEach(P=>{P.addEventListener("click",k=>{k.target===P&&P.style.removeProperty("display")})});const be=document.getElementById("menu-scene-load");be&&be.addEventListener("click",async()=>{const P=document.getElementById("scene-list-body");P.innerHTML='<div class="loading-msg">Lade Scenes...</div>',re("modal-scene-load");try{const k=await CD();if(k.length===0){P.innerHTML='<div class="loading-msg">Keine Scenes gefunden.</div>';return}P.innerHTML="";for(const $ of k){const ie=document.createElement("div");ie.style.cssText="padding:10px 14px;border-radius:6px;cursor:pointer;color:#ccc;font-size:0.85rem;",ie.innerHTML=`<span>${$.label||$.name}</span>`,ie.addEventListener("click",()=>ze($.name)),ie.addEventListener("mouseenter",()=>ie.style.background="rgba(124, 92, 191, 0.2)"),ie.addEventListener("mouseleave",()=>ie.style.background=""),P.appendChild(ie)}}catch(k){P.innerHTML=`<div class="loading-msg">Fehler: ${k.message}</div>`}});async function ze(P){ge("modal-scene-load");try{const k=await DD(P);if(console.log("Scene loaded:",P,k),k.characters&&Array.isArray(k.characters))for(const $ of k.characters){const ie=await dh(e,$,$.name||P);ie.userData.isCharacter=!0,ie.userData.presetName=$.name||P,ie.userData.bodyType=$.body_type||"Unknown",m.push(ie)}}catch(k){console.error("Scene load error:",k),alert("Scene laden fehlgeschlagen: "+k.message)}}const Ge=document.getElementById("menu-scene-save"),pt=document.getElementById("scene-save-btn"),le=document.getElementById("scene-save-name");Ge&&Ge.addEventListener("click",()=>{re("modal-scene-save"),le&&(le.value="",le.focus())}),pt&&le&&(pt.addEventListener("click",async()=>{const P=le.value.trim();if(P){pt.disabled=!0,pt.textContent="Speichere...";try{const k={camera:{position:t.position.toArray(),fov:t.fov,target:i.target.toArray()},lights:{spotLeft:{position:s.spotLeft.position.toArray(),intensity:s.spotLeft.intensity,color:"#"+s.spotLeft.color.getHexString()},spotRight:{position:s.spotRight.position.toArray(),intensity:s.spotRight.intensity,color:"#"+s.spotRight.color.getHexString()},backLight:{position:s.backLight.position.toArray(),intensity:s.backLight.intensity,color:"#"+s.backLight.color.getHexString()}},characters:[]},$=await ID(P,k);console.log("Scene saved:",$),ge("modal-scene-save")}catch(k){console.error("Scene save error:",k),alert("Scene speichern fehlgeschlagen: "+k.message)}pt.disabled=!1,pt.textContent="Speichern"}}),le.addEventListener("keydown",P=>{P.key==="Enter"&&pt.click()}));const me=document.getElementById("model-list"),Ue=document.getElementById("menu-model-load");async function Se(){try{const P=await LD();if(P.length===0){me.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Modelle gefunden.</div>';return}me.innerHTML="";for(const k of P){const $=document.createElement("div");$.className="anim-item",$.textContent=k.label||k.name,$.addEventListener("click",async()=>{try{const ie=await lg(k.name),Te=await dh(e,ie,k.name);Te.userData.isCharacter=!0,Te.userData.presetName=k.name,Te.userData.bodyType=ie.body_type||"Unknown",m.push(Te),console.log("Model loaded:",k.name),document.querySelectorAll("#model-list .anim-item").forEach(Ee=>Ee.classList.remove("active")),$.classList.add("active")}catch(ie){console.error("Model load error:",ie),alert("Modell laden fehlgeschlagen: "+ie.message)}}),me.appendChild($)}}catch(P){me.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${P.message}</div>`}}Se(),Ue&&Ue.addEventListener("click",()=>{document.querySelectorAll(".panel-tab").forEach($=>$.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach($=>$.classList.remove("active"));const P=document.querySelector('[data-tab="tab-models"]'),k=document.getElementById("tab-models");P&&P.classList.add("active"),k&&k.classList.add("active")});const $e=document.getElementById("anim-tree");async function it(){try{const P=await FD(),k=Object.keys(P);if(k.length===0){$e.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden.</div>';return}$e.innerHTML="";for(const $ of k){const ie=P[$],Te=document.createElement("div");Te.className="anim-cat";const Ee=document.createElement("div");Ee.className="anim-cat-header",Ee.innerHTML=`<i class="fas fa-chevron-right"></i> ${$} (${ie.length})`,Ee.addEventListener("click",()=>{Te.classList.toggle("open")}),Te.appendChild(Ee);const De=document.createElement("div");De.className="anim-cat-body";for(const Pe of ie){const ut=document.createElement("div");ut.className="anim-item",ut.textContent=Pe.name,ut.addEventListener("click",async()=>{await Je(Pe.category,Pe.name),document.querySelectorAll("#anim-tree .anim-item").forEach(bt=>bt.classList.remove("active")),ut.classList.add("active")}),De.appendChild(ut)}Te.appendChild(De),$e.appendChild(Te)}}catch(P){$e.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${P.message}</div>`}}async function Je(P,k){try{const $=await ND(P,k);let ie=null;p&&(ie=_(p,e));const{mixer:Te,action:Ee,duration:De}=ie?v($,ie,e,`${P}/${k}`):RD($,e,`${P}/${k}`);b&&b.stopAllAction(),b=Te,B=Ee,window.activeMixer=b,we(De),ce=!1,fe=0,ue=De,window.isPlaying=!1,window.currentTime=0,window.animDuration=De,gt(),console.log("Animation loaded:",P,k,De)}catch($){console.error("Animation load error:",$),alert("Animation laden fehlgeschlagen: "+$.message)}}it();const pe=document.getElementById("menu-add-glb"),ve=document.getElementById("glb-file-input");pe&&ve&&(pe.addEventListener("click",()=>ve.click()),ve.addEventListener("change",async()=>{const P=ve.files[0];if(P){try{await ED(P,e)}catch(k){console.error("GLB load error:",k),alert("Fehler beim Laden der GLB-Datei: "+k.message)}ve.value=""}})),document.querySelectorAll("[data-preset]").forEach(P=>{P.addEventListener("click",()=>{const k=P.getAttribute("data-preset"),$=fh[k];$?(ph($,t,s,i),console.log("✓ Applied preset:",$.name)):console.error("Preset not found:",k)})});const Le=document.getElementById("menu-add-light");let G=0;Le&&Le.addEventListener("click",()=>{G++;const P=new $g(16777215,1,15);P.position.set((Math.random()-.5)*6,2+Math.random()*3,(Math.random()-.5)*6),e.add(P);const k=new Re(new sa(.08,8,8),new pi({color:16776960}));P.add(k),Ec(A,`Light ${G}`,P)});const tt=document.getElementById("menu-export-video");tt&&tt.addEventListener("click",async()=>{w.isRecording?(tt.innerHTML='<i class="fas fa-file-video"></i> Export Video',await w.stopAndDownload()):(w.start(30),tt.innerHTML='<i class="fas fa-stop"></i> Stop Recording')});const Ke=document.getElementById("btnPlayPause"),Qe=document.getElementById("btnStop"),Oe=document.getElementById("btnFrameBack"),rt=document.getElementById("btnFrameFwd"),Fe=document.getElementById("timelineSlider"),F=document.getElementById("timeCurrent"),T=document.getElementById("timeDuration"),Z=document.getElementById("playIcon");let ce=!1,fe=0,ue=1,ke=1;function we(P){ue=P||1,T.textContent=Be(ue),Fe.max=ue}function Be(P){const k=Math.floor(P/60),$=Math.floor(P%60);return`${String(k).padStart(2,"0")}:${String($).padStart(2,"0")}`}function gt(){F.textContent=Be(fe),Fe.value=fe,Z&&(Z.className=ce?"fas fa-pause":"fas fa-play")}function _e(P){!b||!B||(fe=Math.max(0,Math.min(P,ue)),B.time=fe,b.update(0),gt())}Ke&&Ke.addEventListener("click",()=>{b&&(ce=!ce,window.isPlaying=ce,ce&&B?(B.paused=!1,B.play()):B&&(B.paused=!0),gt())}),Qe&&Qe.addEventListener("click",()=>{b&&(ce=!1,fe=0,_e(0),B&&(B.stop(),B.paused=!0),gt())}),Oe&&Oe.addEventListener("click",()=>{_e(fe-1/30)}),rt&&rt.addEventListener("click",()=>{_e(fe+1/30)}),Fe&&(Fe.addEventListener("mousedown",()=>{}),Fe.addEventListener("mouseup",()=>{}),Fe.addEventListener("input",()=>{const P=parseFloat(Fe.value);_e(P)})),document.querySelectorAll(".speed-btn").forEach(P=>{P.addEventListener("click",()=>{const k=parseFloat(P.getAttribute("data-speed"));ke=k,b&&(b.timeScale=k),document.querySelectorAll(".speed-btn").forEach($=>$.classList.remove("active")),P.classList.add("active")})}),document.addEventListener("keydown",P=>{P.target.tagName!=="INPUT"&&(P.code==="Space"?(P.preventDefault(),Ke&&Ke.click()):P.code==="ArrowLeft"?(P.preventDefault(),Oe&&Oe.click()):P.code==="ArrowRight"&&(P.preventDefault(),rt&&rt.click()))});async function He(){try{const P=await fetch("/api/settings/theatre/");if(!P.ok)return;const k=await P.json();if(k.preset){const $=fh[k.preset];$&&(ph($,t,s,i),console.log("✓ Auto-applied preset:",$.name))}if(k.model)try{const $=await lg(k.model),ie=await dh(e,$,k.model);if(ie.userData.isCharacter=!0,ie.userData.presetName=k.model,ie.userData.bodyType=$.body_type||"Unknown",m.push(ie),console.log("✓ Auto-loaded model:",k.model),k.animation){const[Te,Ee]=k.animation.split("/");Te&&Ee&&(await Je(Te,Ee),console.log("✓ Auto-loaded animation:",k.animation))}}catch($){console.warn("Auto-load model/animation failed:",$)}}catch(P){console.warn("Failed to load Theatre defaults:",P)}}setTimeout(He,500);function We(P){document.querySelectorAll(".panel-tab").forEach(Xt=>Xt.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Xt=>Xt.classList.remove("active"));const k=document.querySelector('[data-tab="tab-properties"]'),$=document.getElementById("tab-properties");k&&k.classList.add("active"),$&&$.classList.add("active");const ie=document.getElementById("properties-content");if(!ie)return;const Te=P===s.spotLeft?"Spot Left":P===s.spotRight?"Spot Right":P===s.backLight?"Back Light":"Light",Ee="#"+P.color.getHexString();ie.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-lightbulb"></i> ${Te}
                </h3>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Intensität: <span id="light-intensity-value">${P.intensity.toFixed(1)}</span>
                    </label>
                    <input type="range" id="light-intensity" min="0" max="100" step="1" value="${P.intensity}"
                           style="width:100%;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Farbe
                    </label>
                    <input type="color" id="light-color" value="${Ee}"
                           style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);background:var(--bg-primary);cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-pos-x" value="${P.position.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-pos-y" value="${P.position.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-pos-z" value="${P.position.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="light-rot-x" value="${(P.rotation.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-rot-y" value="${(P.rotation.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-rot-z" value="${(P.rotation.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Ziehe das Licht-Icon in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const De=document.getElementById("light-intensity"),Pe=document.getElementById("light-intensity-value"),ut=document.getElementById("light-color"),bt=document.getElementById("light-pos-x"),Ft=document.getElementById("light-pos-y"),mt=document.getElementById("light-pos-z");if(De&&(De.oninput=Xt=>{P.intensity=parseFloat(Xt.target.value),Pe.textContent=P.intensity.toFixed(1)}),ut&&(ut.oninput=Xt=>{P.color.setHex(parseInt(Xt.target.value.substring(1),16)),f&&f.children.forEach(qt=>{qt.material&&(qt.material.color.copy(P.color),qt.material.emissive&&qt.material.emissive.copy(P.color))})}),bt&&Ft&&mt){const Xt=()=>{P.position.set(parseFloat(bt.value),parseFloat(Ft.value),parseFloat(mt.value)),f&&(f.position.copy(P.position),f.lookAt(P.target.position))};bt.oninput=Xt,Ft.oninput=Xt,mt.oninput=Xt}const nt=document.getElementById("light-rot-x"),jt=document.getElementById("light-rot-y"),Dt=document.getElementById("light-rot-z");if(nt&&jt&&Dt){const Xt=()=>{P.rotation.set(parseFloat(nt.value)*Math.PI/180,parseFloat(jt.value)*Math.PI/180,parseFloat(Dt.value)*Math.PI/180),f&&f.rotation.copy(P.rotation)};nt.oninput=Xt,jt.oninput=Xt,Dt.oninput=Xt}}function ot(P){document.querySelectorAll(".panel-tab").forEach(j=>j.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(j=>j.classList.remove("active"));const k=document.querySelector('[data-tab="tab-properties"]'),$=document.getElementById("tab-properties");k&&k.classList.add("active"),$&&$.classList.add("active");const ie=document.getElementById("properties-content");if(!ie)return;const Te=P.userData.garmentId||P.name||"Garment",Ee=P.material,Pe="#"+Ee.color.getHexString(),ut=Ee.roughness??.8,bt=Ee.metalness??0,Ft=P.userData.offset||.006,mt=P.userData.stiffness||.8,nt=P.position;ie.innerHTML=`
            <div style="padding:16px;max-height:calc(100vh - 200px);overflow-y:auto;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-tshirt"></i> ${Te}
                </h3>

                <!-- Material Properties -->
                <div style="margin-bottom:20px;">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-palette"></i> Material</h4>

                    <div style="margin-bottom:12px;">
                        <label style="display:block;font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;">Farbe</label>
                        <input type="color" id="garment-color" value="${Pe}"
                               style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Roughness</span>
                            <span id="garment-roughness-value">${ut.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-roughness" min="0" max="1" step="0.01" value="${ut}" style="width:100%;cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Metalness</span>
                            <span id="garment-metalness-value">${bt.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-metalness" min="0" max="1" step="0.01" value="${bt}" style="width:100%;cursor:pointer;" />
                    </div>
                </div>

                <!-- Fit Properties -->
                <div style="margin-bottom:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-compress-arrows-alt"></i> Fit</h4>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Offset (Abstand)</span>
                            <span id="garment-offset-value">${Ft.toFixed(3)}</span>
                        </div>
                        <input type="range" id="garment-offset" min="0" max="50" step="0.1" value="${Ft*1e3}" style="width:100%;cursor:pointer;" />
                    </div>

                    <div style="margin-bottom:12px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                            <span style="color:var(--text-muted);">Stiffness (Steifigkeit)</span>
                            <span id="garment-stiffness-value">${mt.toFixed(2)}</span>
                        </div>
                        <input type="range" id="garment-stiffness" min="0" max="100" step="1" value="${mt*100}" style="width:100%;cursor:pointer;" />
                    </div>
                </div>

                <!-- Transform -->
                <div style="margin-bottom:16px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);"><i class="fas fa-arrows-alt"></i> Transform</h4>

                    <label style="display:block;font-size:0.75rem;color:var(--text-muted);margin-bottom:6px;">Position</label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;margin-bottom:12px;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="garment-pos-x" value="${nt.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="garment-pos-y" value="${nt.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="garment-pos-z" value="${nt.z.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Material-Änderungen wirken sofort<br>
                    <i class="fas fa-info-circle"></i> Fit-Änderungen erfordern Garment-Reload (TODO)
                </div>
            </div>
        `;const jt=document.getElementById("garment-color"),Dt=document.getElementById("garment-roughness"),Xt=document.getElementById("garment-roughness-value"),qt=document.getElementById("garment-metalness"),Tt=document.getElementById("garment-metalness-value"),nn=document.getElementById("garment-offset"),Tn=document.getElementById("garment-offset-value"),Bn=document.getElementById("garment-stiffness"),rr=document.getElementById("garment-stiffness-value"),Zn=document.getElementById("garment-pos-x"),ci=document.getElementById("garment-pos-y"),C=document.getElementById("garment-pos-z");if(jt&&(jt.oninput=j=>{Ee.color.setHex(parseInt(j.target.value.substring(1),16))}),Dt&&Xt&&(Dt.oninput=j=>{const J=parseFloat(j.target.value);Ee.roughness=J,Xt.textContent=J.toFixed(2)}),qt&&Tt&&(qt.oninput=j=>{const J=parseFloat(j.target.value);Ee.metalness=J,Tt.textContent=J.toFixed(2)}),nn&&Tn&&(nn.oninput=j=>{const J=parseFloat(j.target.value)/1e3;Tn.textContent=J.toFixed(3),P.userData.offset=J}),Bn&&rr&&(Bn.oninput=j=>{const J=parseFloat(j.target.value)/100;rr.textContent=J.toFixed(2),P.userData.stiffness=J}),Zn&&ci&&C){const j=()=>{P.position.set(parseFloat(Zn.value),parseFloat(ci.value),parseFloat(C.value))};Zn.oninput=j,ci.oninput=j,C.oninput=j}}function Ve(P){document.querySelectorAll(".panel-tab").forEach(Dt=>Dt.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Dt=>Dt.classList.remove("active"));const k=document.querySelector('[data-tab="tab-properties"]'),$=document.getElementById("tab-properties");k&&k.classList.add("active"),$&&$.classList.add("active");const ie=document.getElementById("properties-content");if(!ie)return;const Te=P.userData.presetName||"Character",Ee=P.userData.bodyType||"Unknown",De=P.position,Pe=P.rotation;ie.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-user"></i> ${Te}
                </h3>

                <div style="margin-bottom:16px;font-size:0.8rem;">
                    <span style="color:var(--text-muted);">Body Type:</span>
                    <span style="color:var(--text);margin-left:8px;">${Ee}</span>
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
                            <input type="number" id="char-pos-x" value="${De.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-pos-y" value="${De.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-pos-z" value="${De.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="char-rot-x" value="${(Pe.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-rot-y" value="${(Pe.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-rot-z" value="${(Pe.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Nutze die Transform-Controls in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const ut=document.getElementById("char-pos-x"),bt=document.getElementById("char-pos-y"),Ft=document.getElementById("char-pos-z");if(ut&&bt&&Ft){const Dt=()=>{P.position.set(parseFloat(ut.value),parseFloat(bt.value),parseFloat(Ft.value))};ut.oninput=Dt,bt.oninput=Dt,Ft.oninput=Dt}const mt=document.getElementById("char-rot-x"),nt=document.getElementById("char-rot-y"),jt=document.getElementById("char-rot-z");if(mt&&nt&&jt){const Dt=()=>{P.rotation.set(parseFloat(mt.value)*Math.PI/180,parseFloat(nt.value)*Math.PI/180,parseFloat(jt.value)*Math.PI/180)};mt.oninput=Dt,nt.oninput=Dt,jt.oninput=Dt}xt(P),It(P)}function xt(P){const k=document.getElementById("meta-sliders-container");if(!k)return;const $={age:{min:-1,max:1,label:"Alter",step:.01},mass:{min:-1,max:1,label:"Gewicht",step:.01},tone:{min:-1,max:1,label:"Muskeltonus",step:.01},height:{min:-1,max:1,label:"Höhe",step:.01}},ie=P.userData.meta||{age:0,mass:0,tone:0,height:0};let Te="";for(const[Ee,De]of Object.entries($)){const Pe=ie[Ee]||0,ut=De.min,bt=De.max;Te+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${De.label}</span>
                        <span id="meta-${Ee}-value" style="color:var(--text);">${Pe.toFixed(2)}</span>
                    </div>
                    <input type="range" id="meta-${Ee}" min="${ut}" max="${bt}" step="${De.step}" value="${Pe}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}k.innerHTML=Te;for(const Ee of Object.keys($)){const De=document.getElementById(`meta-${Ee}`),Pe=document.getElementById(`meta-${Ee}-value`);De&&Pe&&(De.oninput=async()=>{const ut=parseFloat(De.value);Pe.textContent=ut.toFixed(2),ie[Ee]=ut,P.userData.meta=ie,await dt(P)})}}async function dt(P){try{let bt=function(mt){const nt=atob(mt),jt=new Uint8Array(nt.length);for(let Dt=0;Dt<nt.length;Dt++)jt[Dt]=nt.charCodeAt(Dt);return new Float32Array(jt.buffer)};var k=bt;const $=new URLSearchParams;$.set("body_type",P.userData.bodyType||"Female_Caucasian");const ie=P.userData.morphs||{};for(const[mt,nt]of Object.entries(ie))nt!=null&&$.set(`morph_${mt}`,String(nt));const Te=P.userData.meta||{};for(const[mt,nt]of Object.entries(Te))nt!=null&&$.set(`meta_${mt}`,String(nt));const Ee=`/api/character/mesh/?${$.toString()}`,De=await fetch(Ee);if(!De.ok)throw new Error(`Character mesh API error: ${De.status}`);const Pe=await De.json(),ut=P.children.find(mt=>mt.isMesh&&!mt.userData.isHair&&!mt.userData.isGarment);if(!ut){console.warn("Could not find body mesh to update");return}const Ft=bt(Pe.vertices);for(let mt=0;mt<Ft.length;mt+=3){const nt=Ft[mt+1],jt=Ft[mt+2];Ft[mt+1]=jt,Ft[mt+2]=-nt}if(ut.geometry.attributes.position.array.set(Ft),ut.geometry.attributes.position.needsUpdate=!0,Pe.normals){const mt=bt(Pe.normals);for(let nt=0;nt<mt.length;nt+=3){const jt=mt[nt+1],Dt=mt[nt+2];mt[nt+1]=Dt,mt[nt+2]=-jt}ut.geometry.attributes.normal.array.set(mt),ut.geometry.attributes.normal.needsUpdate=!0}else ut.geometry.computeVertexNormals();console.log("✓ Character mesh reloaded")}catch($){console.error("Failed to reload character mesh:",$)}}function It(P){const k=document.getElementById("morph-sliders-container");if(!k)return;const $=P.userData.morphs||{};if(Object.keys($).length===0){k.innerHTML='<div style="font-size:0.75rem;color:var(--text-muted);text-align:center;padding:10px;">Keine Morphs</div>';return}let ie='<div style="max-height:300px;overflow-y:auto;padding-right:4px;">';for(const[Te,Ee]of Object.entries($)){const De=Ee||0;ie+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${Te}</span>
                        <span id="morph-${Te}-value" style="color:var(--text);">${De.toFixed(2)}</span>
                    </div>
                    <input type="range" id="morph-${Te}" min="0" max="1" step="0.01" value="${De}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}ie+="</div>",k.innerHTML=ie;for(const Te of Object.keys($)){const Ee=document.getElementById(`morph-${Te}`),De=document.getElementById(`morph-${Te}-value`);Ee&&De&&(Ee.oninput=async()=>{const Pe=parseFloat(Ee.value);De.textContent=Pe.toFixed(2),$[Te]=Pe,P.userData.morphs=$,await dt(P)})}}function X(){const P=document.getElementById("properties-content");P&&(P.innerHTML=`
            <div style="padding:20px;color:var(--text-muted);font-size:0.85rem;text-align:center;">
                <i class="fas fa-hand-pointer" style="font-size:2rem;margin-bottom:10px;opacity:0.3;"></i>
                <p>Klicke auf ein Licht-Icon oder Character in der Szene<br>um Eigenschaften zu bearbeiten.</p>
            </div>
        `)}function Ae(){requestAnimationFrame(Ae);const P=U.getDelta();if(b&&ce&&(b.update(P*ke),fe=B?B.time:0,fe>=ue&&(fe=0,B&&(B.time=0)),gt()),f&&f.userData.light){const k=f.userData.light;k.position.copy(f.position),f.lookAt(k.target.position)}i.update(),n.render(e,t)}Ae()});
