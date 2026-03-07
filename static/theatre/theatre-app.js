/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const js={ROTATE:0,DOLLY:1,PAN:2},zs={ROTATE:0,PAN:1,DOLLY_PAN:2,DOLLY_ROTATE:3},aT=0,Ap=1,cT=2,ug=1,lT=2,Wi=3,Zi=0,Wn=1,Gn=2,yr=0,Xs=1,wp=2,Pp=3,Rp=4,uT=5,ts=100,hT=101,dT=102,fT=103,pT=104,mT=200,gT=201,_T=202,vT=203,gh=204,_h=205,yT=206,xT=207,bT=208,ST=209,MT=210,TT=211,ET=212,AT=213,wT=214,vh=0,yh=1,xh=2,Zs=3,bh=4,Sh=5,Mh=6,Th=7,hg=0,PT=1,RT=2,xr=0,CT=1,IT=2,LT=3,dg=4,DT=5,NT=6,OT=7,Cp="attached",UT="detached",fg=300,$s=301,Js=302,Eh=303,Ah=304,kc=306,Qs=1e3,_r=1001,Dc=1002,Un=1003,pg=1004,Go=1005,ti=1006,Mc=1007,Xi=1008,$i=1009,mg=1010,gg=1011,Jo=1012,ld=1013,rs=1014,gi=1015,na=1016,ud=1017,hd=1018,eo=1020,_g=35902,vg=1021,yg=1022,ai=1023,xg=1024,bg=1025,qs=1026,to=1027,dd=1028,fd=1029,Sg=1030,pd=1031,md=1033,Tc=33776,Ec=33777,Ac=33778,wc=33779,wh=35840,Ph=35841,Rh=35842,Ch=35843,Ih=36196,Lh=37492,Dh=37496,Nh=37808,Oh=37809,Uh=37810,Fh=37811,Bh=37812,kh=37813,zh=37814,Hh=37815,Vh=37816,Gh=37817,Wh=37818,jh=37819,Xh=37820,qh=37821,Pc=36492,Yh=36494,Kh=36495,Mg=36283,Zh=36284,$h=36285,Jh=36286,FT=2200,gd=2201,BT=2202,Qo=2300,ea=2301,Mu=2302,Hs=2400,Vs=2401,Nc=2402,_d=2500,kT=2501,zT=0,Tg=1,Qh=2,HT=3200,VT=3201,Eg=0,GT=1,gr="",_n="srgb",Fn="srgb-linear",zc="linear",Ut="srgb",Es=7680,Ip=519,WT=512,jT=513,XT=514,Ag=515,qT=516,YT=517,KT=518,ZT=519,ed=35044,Lp="300 es",qi=2e3,Oc=2001;class Sr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const s=i.indexOf(t);s!==-1&&i.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let s=0,a=i.length;s<a;s++)i[s].call(this,e);e.target=null}}}const Rn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Dp=1234567;const Ko=Math.PI/180,no=180/Math.PI;function _i(){const r=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Rn[r&255]+Rn[r>>8&255]+Rn[r>>16&255]+Rn[r>>24&255]+"-"+Rn[e&255]+Rn[e>>8&255]+"-"+Rn[e>>16&15|64]+Rn[e>>24&255]+"-"+Rn[t&63|128]+Rn[t>>8&255]+"-"+Rn[t>>16&255]+Rn[t>>24&255]+Rn[n&255]+Rn[n>>8&255]+Rn[n>>16&255]+Rn[n>>24&255]).toLowerCase()}function Mn(r,e,t){return Math.max(e,Math.min(t,r))}function vd(r,e){return(r%e+e)%e}function $T(r,e,t,n,i){return n+(r-e)*(i-n)/(t-e)}function JT(r,e,t){return r!==e?(t-r)/(e-r):0}function Zo(r,e,t){return(1-t)*r+t*e}function QT(r,e,t,n){return Zo(r,e,1-Math.exp(-t*n))}function eE(r,e=1){return e-Math.abs(vd(r,e*2)-e)}function tE(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*(3-2*r))}function nE(r,e,t){return r<=e?0:r>=t?1:(r=(r-e)/(t-e),r*r*r*(r*(r*6-15)+10))}function iE(r,e){return r+Math.floor(Math.random()*(e-r+1))}function rE(r,e){return r+Math.random()*(e-r)}function sE(r){return r*(.5-Math.random())}function oE(r){r!==void 0&&(Dp=r);let e=Dp+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function aE(r){return r*Ko}function cE(r){return r*no}function lE(r){return(r&r-1)===0&&r!==0}function uE(r){return Math.pow(2,Math.ceil(Math.log(r)/Math.LN2))}function hE(r){return Math.pow(2,Math.floor(Math.log(r)/Math.LN2))}function dE(r,e,t,n,i){const s=Math.cos,a=Math.sin,c=s(t/2),u=a(t/2),h=s((e+n)/2),f=a((e+n)/2),p=s((e-n)/2),m=a((e-n)/2),g=s((n-e)/2),x=a((n-e)/2);switch(i){case"XYX":r.set(c*f,u*p,u*m,c*h);break;case"YZY":r.set(u*m,c*f,u*p,c*h);break;case"ZXZ":r.set(u*p,u*m,c*f,c*h);break;case"XZX":r.set(c*f,u*x,u*g,c*h);break;case"YXY":r.set(u*g,c*f,u*x,c*h);break;case"ZYZ":r.set(u*x,u*g,c*f,c*h);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+i)}}function pi(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return r/4294967295;case Uint16Array:return r/65535;case Uint8Array:return r/255;case Int32Array:return Math.max(r/2147483647,-1);case Int16Array:return Math.max(r/32767,-1);case Int8Array:return Math.max(r/127,-1);default:throw new Error("Invalid component type.")}}function Nt(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return Math.round(r*4294967295);case Uint16Array:return Math.round(r*65535);case Uint8Array:return Math.round(r*255);case Int32Array:return Math.round(r*2147483647);case Int16Array:return Math.round(r*32767);case Int8Array:return Math.round(r*127);default:throw new Error("Invalid component type.")}}const wg={DEG2RAD:Ko,RAD2DEG:no,generateUUID:_i,clamp:Mn,euclideanModulo:vd,mapLinear:$T,inverseLerp:JT,lerp:Zo,damp:QT,pingpong:eE,smoothstep:tE,smootherstep:nE,randInt:iE,randFloat:rE,randFloatSpread:sE,seededRandom:oE,degToRad:aE,radToDeg:cE,isPowerOfTwo:lE,ceilPowerOfTwo:uE,floorPowerOfTwo:hE,setQuaternionFromProperEuler:dE,normalize:Nt,denormalize:pi};class Qe{constructor(e=0,t=0){Qe.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Mn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),i=Math.sin(t),s=this.x-e.x,a=this.y-e.y;return this.x=s*n-a*i+e.x,this.y=s*i+a*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class ft{constructor(e,t,n,i,s,a,c,u,h){ft.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h)}set(e,t,n,i,s,a,c,u,h){const f=this.elements;return f[0]=e,f[1]=i,f[2]=c,f[3]=t,f[4]=s,f[5]=u,f[6]=n,f[7]=a,f[8]=h,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[3],u=n[6],h=n[1],f=n[4],p=n[7],m=n[2],g=n[5],x=n[8],M=i[0],v=i[3],_=i[6],A=i[1],P=i[4],b=i[7],B=i[2],U=i[5],O=i[8];return s[0]=a*M+c*A+u*B,s[3]=a*v+c*P+u*U,s[6]=a*_+c*b+u*O,s[1]=h*M+f*A+p*B,s[4]=h*v+f*P+p*U,s[7]=h*_+f*b+p*O,s[2]=m*M+g*A+x*B,s[5]=m*v+g*P+x*U,s[8]=m*_+g*b+x*O,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8];return t*a*f-t*c*h-n*s*f+n*c*u+i*s*h-i*a*u}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=f*a-c*h,m=c*u-f*s,g=h*s-a*u,x=t*p+n*m+i*g;if(x===0)return this.set(0,0,0,0,0,0,0,0,0);const M=1/x;return e[0]=p*M,e[1]=(i*h-f*n)*M,e[2]=(c*n-i*a)*M,e[3]=m*M,e[4]=(f*t-i*u)*M,e[5]=(i*s-c*t)*M,e[6]=g*M,e[7]=(n*u-h*t)*M,e[8]=(a*t-n*s)*M,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,s,a,c){const u=Math.cos(s),h=Math.sin(s);return this.set(n*u,n*h,-n*(u*a+h*c)+a+e,-i*h,i*u,-i*(-h*a+u*c)+c+t,0,0,1),this}scale(e,t){return this.premultiply(Tu.makeScale(e,t)),this}rotate(e){return this.premultiply(Tu.makeRotation(-e)),this}translate(e,t){return this.premultiply(Tu.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Tu=new ft;function Pg(r){for(let e=r.length-1;e>=0;--e)if(r[e]>=65535)return!0;return!1}function ta(r){return document.createElementNS("http://www.w3.org/1999/xhtml",r)}function fE(){const r=ta("canvas");return r.style.display="block",r}const Np={};function Wo(r){r in Np||(Np[r]=!0,console.warn(r))}function pE(r,e,t){return new Promise(function(n,i){function s(){switch(r.clientWaitSync(e,r.SYNC_FLUSH_COMMANDS_BIT,0)){case r.WAIT_FAILED:i();break;case r.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}function mE(r){const e=r.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function gE(r){const e=r.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const Mt={enabled:!0,workingColorSpace:Fn,spaces:{},convert:function(r,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===Ut&&(r.r=Ki(r.r),r.g=Ki(r.g),r.b=Ki(r.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(r.applyMatrix3(this.spaces[e].toXYZ),r.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===Ut&&(r.r=Ys(r.r),r.g=Ys(r.g),r.b=Ys(r.b))),r},fromWorkingColorSpace:function(r,e){return this.convert(r,this.workingColorSpace,e)},toWorkingColorSpace:function(r,e){return this.convert(r,e,this.workingColorSpace)},getPrimaries:function(r){return this.spaces[r].primaries},getTransfer:function(r){return r===gr?zc:this.spaces[r].transfer},getLuminanceCoefficients:function(r,e=this.workingColorSpace){return r.fromArray(this.spaces[e].luminanceCoefficients)},define:function(r){Object.assign(this.spaces,r)},_getMatrix:function(r,e,t){return r.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(r){return this.spaces[r].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(r=this.workingColorSpace){return this.spaces[r].workingColorSpaceConfig.unpackColorSpace}};function Ki(r){return r<.04045?r*.0773993808:Math.pow(r*.9478672986+.0521327014,2.4)}function Ys(r){return r<.0031308?r*12.92:1.055*Math.pow(r,.41666)-.055}const Op=[.64,.33,.3,.6,.15,.06],Up=[.2126,.7152,.0722],Fp=[.3127,.329],Bp=new ft().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),kp=new ft().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);Mt.define({[Fn]:{primaries:Op,whitePoint:Fp,transfer:zc,toXYZ:Bp,fromXYZ:kp,luminanceCoefficients:Up,workingColorSpaceConfig:{unpackColorSpace:_n},outputColorSpaceConfig:{drawingBufferColorSpace:_n}},[_n]:{primaries:Op,whitePoint:Fp,transfer:Ut,toXYZ:Bp,fromXYZ:kp,luminanceCoefficients:Up,outputColorSpaceConfig:{drawingBufferColorSpace:_n}}});let As;class _E{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{As===void 0&&(As=ta("canvas")),As.width=e.width,As.height=e.height;const n=As.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=As}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=ta("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const i=n.getImageData(0,0,e.width,e.height),s=i.data;for(let a=0;a<s.length;a++)s[a]=Ki(s[a]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Ki(t[n]/255)*255):t[n]=Ki(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let vE=0;class Rg{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:vE++}),this.uuid=_i(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let s;if(Array.isArray(i)){s=[];for(let a=0,c=i.length;a<c;a++)i[a].isDataTexture?s.push(Eu(i[a].image)):s.push(Eu(i[a]))}else s=Eu(i);n.url=s}return t||(e.images[this.uuid]=n),n}}function Eu(r){return typeof HTMLImageElement<"u"&&r instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&r instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&r instanceof ImageBitmap?_E.getDataURL(r):r.data?{data:Array.from(r.data),width:r.width,height:r.height,type:r.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let yE=0;class vn extends Sr{constructor(e=vn.DEFAULT_IMAGE,t=vn.DEFAULT_MAPPING,n=_r,i=_r,s=ti,a=Xi,c=ai,u=$i,h=vn.DEFAULT_ANISOTROPY,f=gr){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:yE++}),this.uuid=_i(),this.name="",this.source=new Rg(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=i,this.magFilter=s,this.minFilter=a,this.anisotropy=h,this.format=c,this.internalFormat=null,this.type=u,this.offset=new Qe(0,0),this.repeat=new Qe(1,1),this.center=new Qe(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new ft,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=f,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==fg)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Qs:e.x=e.x-Math.floor(e.x);break;case _r:e.x=e.x<0?0:1;break;case Dc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Qs:e.y=e.y-Math.floor(e.y);break;case _r:e.y=e.y<0?0:1;break;case Dc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}vn.DEFAULT_IMAGE=null;vn.DEFAULT_MAPPING=fg;vn.DEFAULT_ANISOTROPY=1;class Pt{constructor(e=0,t=0,n=0,i=1){Pt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=this.w,a=e.elements;return this.x=a[0]*t+a[4]*n+a[8]*i+a[12]*s,this.y=a[1]*t+a[5]*n+a[9]*i+a[13]*s,this.z=a[2]*t+a[6]*n+a[10]*i+a[14]*s,this.w=a[3]*t+a[7]*n+a[11]*i+a[15]*s,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,s;const u=e.elements,h=u[0],f=u[4],p=u[8],m=u[1],g=u[5],x=u[9],M=u[2],v=u[6],_=u[10];if(Math.abs(f-m)<.01&&Math.abs(p-M)<.01&&Math.abs(x-v)<.01){if(Math.abs(f+m)<.1&&Math.abs(p+M)<.1&&Math.abs(x+v)<.1&&Math.abs(h+g+_-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const P=(h+1)/2,b=(g+1)/2,B=(_+1)/2,U=(f+m)/4,O=(p+M)/4,z=(x+v)/4;return P>b&&P>B?P<.01?(n=0,i=.707106781,s=.707106781):(n=Math.sqrt(P),i=U/n,s=O/n):b>B?b<.01?(n=.707106781,i=0,s=.707106781):(i=Math.sqrt(b),n=U/i,s=z/i):B<.01?(n=.707106781,i=.707106781,s=0):(s=Math.sqrt(B),n=O/s,i=z/s),this.set(n,i,s,t),this}let A=Math.sqrt((v-x)*(v-x)+(p-M)*(p-M)+(m-f)*(m-f));return Math.abs(A)<.001&&(A=1),this.x=(v-x)/A,this.y=(p-M)/A,this.z=(m-f)/A,this.w=Math.acos((h+g+_-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class xE extends Sr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new Pt(0,0,e,t),this.scissorTest=!1,this.viewport=new Pt(0,0,e,t);const i={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:ti,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new vn(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const a=n.count;for(let c=0;c<a;c++)this.textures[c]=s.clone(),this.textures[c].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let i=0,s=this.textures.length;i<s;i++)this.textures[i].image.width=e,this.textures[i].image.height=t,this.textures[i].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,i=e.textures.length;n<i;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Rg(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class ss extends xE{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Cg extends vn{constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Un,this.minFilter=Un,this.wrapR=_r,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class bE extends vn{constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Un,this.minFilter=Un,this.wrapR=_r,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Yt{constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,s,a,c){let u=n[i+0],h=n[i+1],f=n[i+2],p=n[i+3];const m=s[a+0],g=s[a+1],x=s[a+2],M=s[a+3];if(c===0){e[t+0]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p;return}if(c===1){e[t+0]=m,e[t+1]=g,e[t+2]=x,e[t+3]=M;return}if(p!==M||u!==m||h!==g||f!==x){let v=1-c;const _=u*m+h*g+f*x+p*M,A=_>=0?1:-1,P=1-_*_;if(P>Number.EPSILON){const B=Math.sqrt(P),U=Math.atan2(B,_*A);v=Math.sin(v*U)/B,c=Math.sin(c*U)/B}const b=c*A;if(u=u*v+m*b,h=h*v+g*b,f=f*v+x*b,p=p*v+M*b,v===1-c){const B=1/Math.sqrt(u*u+h*h+f*f+p*p);u*=B,h*=B,f*=B,p*=B}}e[t]=u,e[t+1]=h,e[t+2]=f,e[t+3]=p}static multiplyQuaternionsFlat(e,t,n,i,s,a){const c=n[i],u=n[i+1],h=n[i+2],f=n[i+3],p=s[a],m=s[a+1],g=s[a+2],x=s[a+3];return e[t]=c*x+f*p+u*g-h*m,e[t+1]=u*x+f*m+h*p-c*g,e[t+2]=h*x+f*g+c*m-u*p,e[t+3]=f*x-c*p-u*m-h*g,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,i=e._y,s=e._z,a=e._order,c=Math.cos,u=Math.sin,h=c(n/2),f=c(i/2),p=c(s/2),m=u(n/2),g=u(i/2),x=u(s/2);switch(a){case"XYZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"YXZ":this._x=m*f*p+h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"ZXY":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p-m*g*x;break;case"ZYX":this._x=m*f*p-h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p+m*g*x;break;case"YZX":this._x=m*f*p+h*g*x,this._y=h*g*p+m*f*x,this._z=h*f*x-m*g*p,this._w=h*f*p-m*g*x;break;case"XZY":this._x=m*f*p-h*g*x,this._y=h*g*p-m*f*x,this._z=h*f*x+m*g*p,this._w=h*f*p+m*g*x;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+a)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],i=t[4],s=t[8],a=t[1],c=t[5],u=t[9],h=t[2],f=t[6],p=t[10],m=n+c+p;if(m>0){const g=.5/Math.sqrt(m+1);this._w=.25/g,this._x=(f-u)*g,this._y=(s-h)*g,this._z=(a-i)*g}else if(n>c&&n>p){const g=2*Math.sqrt(1+n-c-p);this._w=(f-u)/g,this._x=.25*g,this._y=(i+a)/g,this._z=(s+h)/g}else if(c>p){const g=2*Math.sqrt(1+c-n-p);this._w=(s-h)/g,this._x=(i+a)/g,this._y=.25*g,this._z=(u+f)/g}else{const g=2*Math.sqrt(1+p-n-c);this._w=(a-i)/g,this._x=(s+h)/g,this._y=(u+f)/g,this._z=.25*g}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Mn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,i=e._y,s=e._z,a=e._w,c=t._x,u=t._y,h=t._z,f=t._w;return this._x=n*f+a*c+i*h-s*u,this._y=i*f+a*u+s*c-n*h,this._z=s*f+a*h+n*u-i*c,this._w=a*f-n*c-i*u-s*h,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,i=this._y,s=this._z,a=this._w;let c=a*e._w+n*e._x+i*e._y+s*e._z;if(c<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,c=-c):this.copy(e),c>=1)return this._w=a,this._x=n,this._y=i,this._z=s,this;const u=1-c*c;if(u<=Number.EPSILON){const g=1-t;return this._w=g*a+t*this._w,this._x=g*n+t*this._x,this._y=g*i+t*this._y,this._z=g*s+t*this._z,this.normalize(),this}const h=Math.sqrt(u),f=Math.atan2(h,c),p=Math.sin((1-t)*f)/h,m=Math.sin(t*f)/h;return this._w=a*p+this._w*m,this._x=n*p+this._x*m,this._y=i*p+this._y*m,this._z=s*p+this._z*m,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),i=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(i*Math.sin(e),i*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class F{constructor(e=0,t=0,n=0){F.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(zp.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(zp.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*i,this.y=s[1]*t+s[4]*n+s[7]*i,this.z=s[2]*t+s[5]*n+s[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=e.elements,a=1/(s[3]*t+s[7]*n+s[11]*i+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*i+s[12])*a,this.y=(s[1]*t+s[5]*n+s[9]*i+s[13])*a,this.z=(s[2]*t+s[6]*n+s[10]*i+s[14])*a,this}applyQuaternion(e){const t=this.x,n=this.y,i=this.z,s=e.x,a=e.y,c=e.z,u=e.w,h=2*(a*i-c*n),f=2*(c*t-s*i),p=2*(s*n-a*t);return this.x=t+u*h+a*p-c*f,this.y=n+u*f+c*h-s*p,this.z=i+u*p+s*f-a*h,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*i,this.y=s[1]*t+s[5]*n+s[9]*i,this.z=s[2]*t+s[6]*n+s[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,i=e.y,s=e.z,a=t.x,c=t.y,u=t.z;return this.x=i*u-s*c,this.y=s*a-n*u,this.z=n*c-i*a,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Au.copy(this).projectOnVector(e),this.sub(Au)}reflect(e){return this.sub(Au.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Mn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Au=new F,zp=new Yt;class Ji{constructor(e=new F(1/0,1/0,1/0),t=new F(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(ui.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(ui.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=ui.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let a=0,c=s.count;a<c;a++)e.isMesh===!0?e.getVertexPosition(a,ui):ui.fromBufferAttribute(s,a),ui.applyMatrix4(e.matrixWorld),this.expandByPoint(ui);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),Wa.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),Wa.copy(n.boundingBox)),Wa.applyMatrix4(e.matrixWorld),this.union(Wa)}const i=e.children;for(let s=0,a=i.length;s<a;s++)this.expandByObject(i[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,ui),ui.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Lo),ja.subVectors(this.max,Lo),ws.subVectors(e.a,Lo),Ps.subVectors(e.b,Lo),Rs.subVectors(e.c,Lo),or.subVectors(Ps,ws),ar.subVectors(Rs,Ps),jr.subVectors(ws,Rs);let t=[0,-or.z,or.y,0,-ar.z,ar.y,0,-jr.z,jr.y,or.z,0,-or.x,ar.z,0,-ar.x,jr.z,0,-jr.x,-or.y,or.x,0,-ar.y,ar.x,0,-jr.y,jr.x,0];return!wu(t,ws,Ps,Rs,ja)||(t=[1,0,0,0,1,0,0,0,1],!wu(t,ws,Ps,Rs,ja))?!1:(Xa.crossVectors(or,ar),t=[Xa.x,Xa.y,Xa.z],wu(t,ws,Ps,Rs,ja))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,ui).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(ui).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(Bi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),Bi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),Bi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),Bi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),Bi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),Bi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),Bi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),Bi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(Bi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const Bi=[new F,new F,new F,new F,new F,new F,new F,new F],ui=new F,Wa=new Ji,ws=new F,Ps=new F,Rs=new F,or=new F,ar=new F,jr=new F,Lo=new F,ja=new F,Xa=new F,Xr=new F;function wu(r,e,t,n,i){for(let s=0,a=r.length-3;s<=a;s+=3){Xr.fromArray(r,s);const c=i.x*Math.abs(Xr.x)+i.y*Math.abs(Xr.y)+i.z*Math.abs(Xr.z),u=e.dot(Xr),h=t.dot(Xr),f=n.dot(Xr);if(Math.max(-Math.max(u,h,f),Math.min(u,h,f))>c)return!1}return!0}const SE=new Ji,Do=new F,Pu=new F;class Ei{constructor(e=new F,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):SE.setFromPoints(e).getCenter(n);let i=0;for(let s=0,a=e.length;s<a;s++)i=Math.max(i,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Do.subVectors(e,this.center);const t=Do.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(Do,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Pu.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Do.copy(e.center).add(Pu)),this.expandByPoint(Do.copy(e.center).sub(Pu))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const ki=new F,Ru=new F,qa=new F,cr=new F,Cu=new F,Ya=new F,Iu=new F;class oo{constructor(e=new F,t=new F(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,ki)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=ki.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(ki.copy(this.origin).addScaledVector(this.direction,t),ki.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){Ru.copy(e).add(t).multiplyScalar(.5),qa.copy(t).sub(e).normalize(),cr.copy(this.origin).sub(Ru);const s=e.distanceTo(t)*.5,a=-this.direction.dot(qa),c=cr.dot(this.direction),u=-cr.dot(qa),h=cr.lengthSq(),f=Math.abs(1-a*a);let p,m,g,x;if(f>0)if(p=a*u-c,m=a*c-u,x=s*f,p>=0)if(m>=-x)if(m<=x){const M=1/f;p*=M,m*=M,g=p*(p+a*m+2*c)+m*(a*p+m+2*u)+h}else m=s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m=-s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;else m<=-x?(p=Math.max(0,-(-a*s+c)),m=p>0?-s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h):m<=x?(p=0,m=Math.min(Math.max(-s,-u),s),g=m*(m+2*u)+h):(p=Math.max(0,-(a*s+c)),m=p>0?s:Math.min(Math.max(-s,-u),s),g=-p*p+m*(m+2*u)+h);else m=a>0?-s:s,p=Math.max(0,-(a*m+c)),g=-p*p+m*(m+2*u)+h;return n&&n.copy(this.origin).addScaledVector(this.direction,p),i&&i.copy(Ru).addScaledVector(qa,m),g}intersectSphere(e,t){ki.subVectors(e.center,this.origin);const n=ki.dot(this.direction),i=ki.dot(ki)-n*n,s=e.radius*e.radius;if(i>s)return null;const a=Math.sqrt(s-i),c=n-a,u=n+a;return u<0?null:c<0?this.at(u,t):this.at(c,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,s,a,c,u;const h=1/this.direction.x,f=1/this.direction.y,p=1/this.direction.z,m=this.origin;return h>=0?(n=(e.min.x-m.x)*h,i=(e.max.x-m.x)*h):(n=(e.max.x-m.x)*h,i=(e.min.x-m.x)*h),f>=0?(s=(e.min.y-m.y)*f,a=(e.max.y-m.y)*f):(s=(e.max.y-m.y)*f,a=(e.min.y-m.y)*f),n>a||s>i||((s>n||isNaN(n))&&(n=s),(a<i||isNaN(i))&&(i=a),p>=0?(c=(e.min.z-m.z)*p,u=(e.max.z-m.z)*p):(c=(e.max.z-m.z)*p,u=(e.min.z-m.z)*p),n>u||c>i)||((c>n||n!==n)&&(n=c),(u<i||i!==i)&&(i=u),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,ki)!==null}intersectTriangle(e,t,n,i,s){Cu.subVectors(t,e),Ya.subVectors(n,e),Iu.crossVectors(Cu,Ya);let a=this.direction.dot(Iu),c;if(a>0){if(i)return null;c=1}else if(a<0)c=-1,a=-a;else return null;cr.subVectors(this.origin,e);const u=c*this.direction.dot(Ya.crossVectors(cr,Ya));if(u<0)return null;const h=c*this.direction.dot(Cu.cross(cr));if(h<0||u+h>a)return null;const f=-c*cr.dot(Iu);return f<0?null:this.at(f/a,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class rt{constructor(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v){rt.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v)}set(e,t,n,i,s,a,c,u,h,f,p,m,g,x,M,v){const _=this.elements;return _[0]=e,_[4]=t,_[8]=n,_[12]=i,_[1]=s,_[5]=a,_[9]=c,_[13]=u,_[2]=h,_[6]=f,_[10]=p,_[14]=m,_[3]=g,_[7]=x,_[11]=M,_[15]=v,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new rt().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,i=1/Cs.setFromMatrixColumn(e,0).length(),s=1/Cs.setFromMatrixColumn(e,1).length(),a=1/Cs.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*a,t[9]=n[9]*a,t[10]=n[10]*a,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,i=e.y,s=e.z,a=Math.cos(n),c=Math.sin(n),u=Math.cos(i),h=Math.sin(i),f=Math.cos(s),p=Math.sin(s);if(e.order==="XYZ"){const m=a*f,g=a*p,x=c*f,M=c*p;t[0]=u*f,t[4]=-u*p,t[8]=h,t[1]=g+x*h,t[5]=m-M*h,t[9]=-c*u,t[2]=M-m*h,t[6]=x+g*h,t[10]=a*u}else if(e.order==="YXZ"){const m=u*f,g=u*p,x=h*f,M=h*p;t[0]=m+M*c,t[4]=x*c-g,t[8]=a*h,t[1]=a*p,t[5]=a*f,t[9]=-c,t[2]=g*c-x,t[6]=M+m*c,t[10]=a*u}else if(e.order==="ZXY"){const m=u*f,g=u*p,x=h*f,M=h*p;t[0]=m-M*c,t[4]=-a*p,t[8]=x+g*c,t[1]=g+x*c,t[5]=a*f,t[9]=M-m*c,t[2]=-a*h,t[6]=c,t[10]=a*u}else if(e.order==="ZYX"){const m=a*f,g=a*p,x=c*f,M=c*p;t[0]=u*f,t[4]=x*h-g,t[8]=m*h+M,t[1]=u*p,t[5]=M*h+m,t[9]=g*h-x,t[2]=-h,t[6]=c*u,t[10]=a*u}else if(e.order==="YZX"){const m=a*u,g=a*h,x=c*u,M=c*h;t[0]=u*f,t[4]=M-m*p,t[8]=x*p+g,t[1]=p,t[5]=a*f,t[9]=-c*f,t[2]=-h*f,t[6]=g*p+x,t[10]=m-M*p}else if(e.order==="XZY"){const m=a*u,g=a*h,x=c*u,M=c*h;t[0]=u*f,t[4]=-p,t[8]=h*f,t[1]=m*p+M,t[5]=a*f,t[9]=g*p-x,t[2]=x*p-g,t[6]=c*f,t[10]=M*p+m}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(ME,e,TE)}lookAt(e,t,n){const i=this.elements;return Qn.subVectors(e,t),Qn.lengthSq()===0&&(Qn.z=1),Qn.normalize(),lr.crossVectors(n,Qn),lr.lengthSq()===0&&(Math.abs(n.z)===1?Qn.x+=1e-4:Qn.z+=1e-4,Qn.normalize(),lr.crossVectors(n,Qn)),lr.normalize(),Ka.crossVectors(Qn,lr),i[0]=lr.x,i[4]=Ka.x,i[8]=Qn.x,i[1]=lr.y,i[5]=Ka.y,i[9]=Qn.y,i[2]=lr.z,i[6]=Ka.z,i[10]=Qn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,a=n[0],c=n[4],u=n[8],h=n[12],f=n[1],p=n[5],m=n[9],g=n[13],x=n[2],M=n[6],v=n[10],_=n[14],A=n[3],P=n[7],b=n[11],B=n[15],U=i[0],O=i[4],z=i[8],I=i[12],w=i[1],H=i[5],ee=i[9],Q=i[13],ae=i[2],ce=i[6],$=i[10],fe=i[14],re=i[3],ye=i[7],Me=i[11],Ne=i[15];return s[0]=a*U+c*w+u*ae+h*re,s[4]=a*O+c*H+u*ce+h*ye,s[8]=a*z+c*ee+u*$+h*Me,s[12]=a*I+c*Q+u*fe+h*Ne,s[1]=f*U+p*w+m*ae+g*re,s[5]=f*O+p*H+m*ce+g*ye,s[9]=f*z+p*ee+m*$+g*Me,s[13]=f*I+p*Q+m*fe+g*Ne,s[2]=x*U+M*w+v*ae+_*re,s[6]=x*O+M*H+v*ce+_*ye,s[10]=x*z+M*ee+v*$+_*Me,s[14]=x*I+M*Q+v*fe+_*Ne,s[3]=A*U+P*w+b*ae+B*re,s[7]=A*O+P*H+b*ce+B*ye,s[11]=A*z+P*ee+b*$+B*Me,s[15]=A*I+P*Q+b*fe+B*Ne,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],i=e[8],s=e[12],a=e[1],c=e[5],u=e[9],h=e[13],f=e[2],p=e[6],m=e[10],g=e[14],x=e[3],M=e[7],v=e[11],_=e[15];return x*(+s*u*p-i*h*p-s*c*m+n*h*m+i*c*g-n*u*g)+M*(+t*u*g-t*h*m+s*a*m-i*a*g+i*h*f-s*u*f)+v*(+t*h*p-t*c*g-s*a*p+n*a*g+s*c*f-n*h*f)+_*(-i*c*f-t*u*p+t*c*m+i*a*p-n*a*m+n*u*f)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],a=e[4],c=e[5],u=e[6],h=e[7],f=e[8],p=e[9],m=e[10],g=e[11],x=e[12],M=e[13],v=e[14],_=e[15],A=p*v*h-M*m*h+M*u*g-c*v*g-p*u*_+c*m*_,P=x*m*h-f*v*h-x*u*g+a*v*g+f*u*_-a*m*_,b=f*M*h-x*p*h+x*c*g-a*M*g-f*c*_+a*p*_,B=x*p*u-f*M*u-x*c*m+a*M*m+f*c*v-a*p*v,U=t*A+n*P+i*b+s*B;if(U===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const O=1/U;return e[0]=A*O,e[1]=(M*m*s-p*v*s-M*i*g+n*v*g+p*i*_-n*m*_)*O,e[2]=(c*v*s-M*u*s+M*i*h-n*v*h-c*i*_+n*u*_)*O,e[3]=(p*u*s-c*m*s-p*i*h+n*m*h+c*i*g-n*u*g)*O,e[4]=P*O,e[5]=(f*v*s-x*m*s+x*i*g-t*v*g-f*i*_+t*m*_)*O,e[6]=(x*u*s-a*v*s-x*i*h+t*v*h+a*i*_-t*u*_)*O,e[7]=(a*m*s-f*u*s+f*i*h-t*m*h-a*i*g+t*u*g)*O,e[8]=b*O,e[9]=(x*p*s-f*M*s-x*n*g+t*M*g+f*n*_-t*p*_)*O,e[10]=(a*M*s-x*c*s+x*n*h-t*M*h-a*n*_+t*c*_)*O,e[11]=(f*c*s-a*p*s-f*n*h+t*p*h+a*n*g-t*c*g)*O,e[12]=B*O,e[13]=(f*M*i-x*p*i+x*n*m-t*M*m-f*n*v+t*p*v)*O,e[14]=(x*c*i-a*M*i-x*n*u+t*M*u+a*n*v-t*c*v)*O,e[15]=(a*p*i-f*c*i+f*n*u-t*p*u-a*n*m+t*c*m)*O,this}scale(e){const t=this.elements,n=e.x,i=e.y,s=e.z;return t[0]*=n,t[4]*=i,t[8]*=s,t[1]*=n,t[5]*=i,t[9]*=s,t[2]*=n,t[6]*=i,t[10]*=s,t[3]*=n,t[7]*=i,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),i=Math.sin(t),s=1-n,a=e.x,c=e.y,u=e.z,h=s*a,f=s*c;return this.set(h*a+n,h*c-i*u,h*u+i*c,0,h*c+i*u,f*c+n,f*u-i*a,0,h*u-i*c,f*u+i*a,s*u*u+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,s,a){return this.set(1,n,s,0,e,1,a,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){const i=this.elements,s=t._x,a=t._y,c=t._z,u=t._w,h=s+s,f=a+a,p=c+c,m=s*h,g=s*f,x=s*p,M=a*f,v=a*p,_=c*p,A=u*h,P=u*f,b=u*p,B=n.x,U=n.y,O=n.z;return i[0]=(1-(M+_))*B,i[1]=(g+b)*B,i[2]=(x-P)*B,i[3]=0,i[4]=(g-b)*U,i[5]=(1-(m+_))*U,i[6]=(v+A)*U,i[7]=0,i[8]=(x+P)*O,i[9]=(v-A)*O,i[10]=(1-(m+M))*O,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){const i=this.elements;let s=Cs.set(i[0],i[1],i[2]).length();const a=Cs.set(i[4],i[5],i[6]).length(),c=Cs.set(i[8],i[9],i[10]).length();this.determinant()<0&&(s=-s),e.x=i[12],e.y=i[13],e.z=i[14],hi.copy(this);const h=1/s,f=1/a,p=1/c;return hi.elements[0]*=h,hi.elements[1]*=h,hi.elements[2]*=h,hi.elements[4]*=f,hi.elements[5]*=f,hi.elements[6]*=f,hi.elements[8]*=p,hi.elements[9]*=p,hi.elements[10]*=p,t.setFromRotationMatrix(hi),n.x=s,n.y=a,n.z=c,this}makePerspective(e,t,n,i,s,a,c=qi){const u=this.elements,h=2*s/(t-e),f=2*s/(n-i),p=(t+e)/(t-e),m=(n+i)/(n-i);let g,x;if(c===qi)g=-(a+s)/(a-s),x=-2*a*s/(a-s);else if(c===Oc)g=-a/(a-s),x=-a*s/(a-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+c);return u[0]=h,u[4]=0,u[8]=p,u[12]=0,u[1]=0,u[5]=f,u[9]=m,u[13]=0,u[2]=0,u[6]=0,u[10]=g,u[14]=x,u[3]=0,u[7]=0,u[11]=-1,u[15]=0,this}makeOrthographic(e,t,n,i,s,a,c=qi){const u=this.elements,h=1/(t-e),f=1/(n-i),p=1/(a-s),m=(t+e)*h,g=(n+i)*f;let x,M;if(c===qi)x=(a+s)*p,M=-2*p;else if(c===Oc)x=s*p,M=-1*p;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+c);return u[0]=2*h,u[4]=0,u[8]=0,u[12]=-m,u[1]=0,u[5]=2*f,u[9]=0,u[13]=-g,u[2]=0,u[6]=0,u[10]=M,u[14]=-x,u[3]=0,u[7]=0,u[11]=0,u[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Cs=new F,hi=new rt,ME=new F(0,0,0),TE=new F(1,1,1),lr=new F,Ka=new F,Qn=new F,Hp=new rt,Vp=new Yt;class vi{constructor(e=0,t=0,n=0,i=vi.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const i=e.elements,s=i[0],a=i[4],c=i[8],u=i[1],h=i[5],f=i[9],p=i[2],m=i[6],g=i[10];switch(t){case"XYZ":this._y=Math.asin(Mn(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-f,g),this._z=Math.atan2(-a,s)):(this._x=Math.atan2(m,h),this._z=0);break;case"YXZ":this._x=Math.asin(-Mn(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(c,g),this._z=Math.atan2(u,h)):(this._y=Math.atan2(-p,s),this._z=0);break;case"ZXY":this._x=Math.asin(Mn(m,-1,1)),Math.abs(m)<.9999999?(this._y=Math.atan2(-p,g),this._z=Math.atan2(-a,h)):(this._y=0,this._z=Math.atan2(u,s));break;case"ZYX":this._y=Math.asin(-Mn(p,-1,1)),Math.abs(p)<.9999999?(this._x=Math.atan2(m,g),this._z=Math.atan2(u,s)):(this._x=0,this._z=Math.atan2(-a,h));break;case"YZX":this._z=Math.asin(Mn(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(-f,h),this._y=Math.atan2(-p,s)):(this._x=0,this._y=Math.atan2(c,g));break;case"XZY":this._z=Math.asin(-Mn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(m,h),this._y=Math.atan2(c,s)):(this._x=Math.atan2(-f,g),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Hp.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Hp,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Vp.setFromEuler(this),this.setFromQuaternion(Vp,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}vi.DEFAULT_ORDER="XYZ";class yd{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let EE=0;const Gp=new F,Is=new Yt,zi=new rt,Za=new F,No=new F,AE=new F,wE=new Yt,Wp=new F(1,0,0),jp=new F(0,1,0),Xp=new F(0,0,1),qp={type:"added"},PE={type:"removed"},Ls={type:"childadded",child:null},Lu={type:"childremoved",child:null};class Xt extends Sr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:EE++}),this.uuid=_i(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Xt.DEFAULT_UP.clone();const e=new F,t=new vi,n=new Yt,i=new F(1,1,1);function s(){n.setFromEuler(t,!1)}function a(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(a),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new rt},normalMatrix:{value:new ft}}),this.matrix=new rt,this.matrixWorld=new rt,this.matrixAutoUpdate=Xt.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Xt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new yd,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.multiply(Is),this}rotateOnWorldAxis(e,t){return Is.setFromAxisAngle(e,t),this.quaternion.premultiply(Is),this}rotateX(e){return this.rotateOnAxis(Wp,e)}rotateY(e){return this.rotateOnAxis(jp,e)}rotateZ(e){return this.rotateOnAxis(Xp,e)}translateOnAxis(e,t){return Gp.copy(e).applyQuaternion(this.quaternion),this.position.add(Gp.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Wp,e)}translateY(e){return this.translateOnAxis(jp,e)}translateZ(e){return this.translateOnAxis(Xp,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(zi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Za.copy(e):Za.set(e,t,n);const i=this.parent;this.updateWorldMatrix(!0,!1),No.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?zi.lookAt(No,Za,this.up):zi.lookAt(Za,No,this.up),this.quaternion.setFromRotationMatrix(zi),i&&(zi.extractRotation(i.matrixWorld),Is.setFromRotationMatrix(zi),this.quaternion.premultiply(Is.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(qp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(PE),Lu.child=e,this.dispatchEvent(Lu),Lu.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),zi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),zi.multiply(e.parent.matrixWorld)),e.applyMatrix4(zi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(qp),Ls.child=e,this.dispatchEvent(Ls),Ls.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){const a=this.children[n].getObjectByProperty(e,t);if(a!==void 0)return a}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,e,AE),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(No,wE,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const i=this.children;for(let s=0,a=i.length;s<a;s++)i[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),i.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(i.type="BatchedMesh",i.perObjectFrustumCulled=this.perObjectFrustumCulled,i.sortObjects=this.sortObjects,i.drawRanges=this._drawRanges,i.reservedRanges=this._reservedRanges,i.visibility=this._visibility,i.active=this._active,i.bounds=this._bounds.map(c=>({boxInitialized:c.boxInitialized,boxMin:c.box.min.toArray(),boxMax:c.box.max.toArray(),sphereInitialized:c.sphereInitialized,sphereRadius:c.sphere.radius,sphereCenter:c.sphere.center.toArray()})),i.maxInstanceCount=this._maxInstanceCount,i.maxVertexCount=this._maxVertexCount,i.maxIndexCount=this._maxIndexCount,i.geometryInitialized=this._geometryInitialized,i.geometryCount=this._geometryCount,i.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(i.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(i.boundingSphere={center:i.boundingSphere.center.toArray(),radius:i.boundingSphere.radius}),this.boundingBox!==null&&(i.boundingBox={min:i.boundingBox.min.toArray(),max:i.boundingBox.max.toArray()}));function s(c,u){return c[u.uuid]===void 0&&(c[u.uuid]=u.toJSON(e)),u.uuid}if(this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=s(e.geometries,this.geometry);const c=this.geometry.parameters;if(c!==void 0&&c.shapes!==void 0){const u=c.shapes;if(Array.isArray(u))for(let h=0,f=u.length;h<f;h++){const p=u[h];s(e.shapes,p)}else s(e.shapes,u)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const c=[];for(let u=0,h=this.material.length;u<h;u++)c.push(s(e.materials,this.material[u]));i.material=c}else i.material=s(e.materials,this.material);if(this.children.length>0){i.children=[];for(let c=0;c<this.children.length;c++)i.children.push(this.children[c].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let c=0;c<this.animations.length;c++){const u=this.animations[c];i.animations.push(s(e.animations,u))}}if(t){const c=a(e.geometries),u=a(e.materials),h=a(e.textures),f=a(e.images),p=a(e.shapes),m=a(e.skeletons),g=a(e.animations),x=a(e.nodes);c.length>0&&(n.geometries=c),u.length>0&&(n.materials=u),h.length>0&&(n.textures=h),f.length>0&&(n.images=f),p.length>0&&(n.shapes=p),m.length>0&&(n.skeletons=m),g.length>0&&(n.animations=g),x.length>0&&(n.nodes=x)}return n.object=i,n;function a(c){const u=[];for(const h in c){const f=c[h];delete f.metadata,u.push(f)}return u}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const i=e.children[n];this.add(i.clone())}return this}}Xt.DEFAULT_UP=new F(0,1,0);Xt.DEFAULT_MATRIX_AUTO_UPDATE=!0;Xt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const di=new F,Hi=new F,Du=new F,Vi=new F,Ds=new F,Ns=new F,Yp=new F,Nu=new F,Ou=new F,Uu=new F,Fu=new Pt,Bu=new Pt,ku=new Pt;class mi{constructor(e=new F,t=new F,n=new F){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),di.subVectors(e,t),i.cross(di);const s=i.lengthSq();return s>0?i.multiplyScalar(1/Math.sqrt(s)):i.set(0,0,0)}static getBarycoord(e,t,n,i,s){di.subVectors(i,t),Hi.subVectors(n,t),Du.subVectors(e,t);const a=di.dot(di),c=di.dot(Hi),u=di.dot(Du),h=Hi.dot(Hi),f=Hi.dot(Du),p=a*h-c*c;if(p===0)return s.set(0,0,0),null;const m=1/p,g=(h*u-c*f)*m,x=(a*f-c*u)*m;return s.set(1-g-x,x,g)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,Vi)===null?!1:Vi.x>=0&&Vi.y>=0&&Vi.x+Vi.y<=1}static getInterpolation(e,t,n,i,s,a,c,u){return this.getBarycoord(e,t,n,i,Vi)===null?(u.x=0,u.y=0,"z"in u&&(u.z=0),"w"in u&&(u.w=0),null):(u.setScalar(0),u.addScaledVector(s,Vi.x),u.addScaledVector(a,Vi.y),u.addScaledVector(c,Vi.z),u)}static getInterpolatedAttribute(e,t,n,i,s,a){return Fu.setScalar(0),Bu.setScalar(0),ku.setScalar(0),Fu.fromBufferAttribute(e,t),Bu.fromBufferAttribute(e,n),ku.fromBufferAttribute(e,i),a.setScalar(0),a.addScaledVector(Fu,s.x),a.addScaledVector(Bu,s.y),a.addScaledVector(ku,s.z),a}static isFrontFacing(e,t,n,i){return di.subVectors(n,t),Hi.subVectors(e,t),di.cross(Hi).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return di.subVectors(this.c,this.b),Hi.subVectors(this.a,this.b),di.cross(Hi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return mi.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return mi.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,i,s){return mi.getInterpolation(e,this.a,this.b,this.c,t,n,i,s)}containsPoint(e){return mi.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return mi.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,i=this.b,s=this.c;let a,c;Ds.subVectors(i,n),Ns.subVectors(s,n),Nu.subVectors(e,n);const u=Ds.dot(Nu),h=Ns.dot(Nu);if(u<=0&&h<=0)return t.copy(n);Ou.subVectors(e,i);const f=Ds.dot(Ou),p=Ns.dot(Ou);if(f>=0&&p<=f)return t.copy(i);const m=u*p-f*h;if(m<=0&&u>=0&&f<=0)return a=u/(u-f),t.copy(n).addScaledVector(Ds,a);Uu.subVectors(e,s);const g=Ds.dot(Uu),x=Ns.dot(Uu);if(x>=0&&g<=x)return t.copy(s);const M=g*h-u*x;if(M<=0&&h>=0&&x<=0)return c=h/(h-x),t.copy(n).addScaledVector(Ns,c);const v=f*x-g*p;if(v<=0&&p-f>=0&&g-x>=0)return Yp.subVectors(s,i),c=(p-f)/(p-f+(g-x)),t.copy(i).addScaledVector(Yp,c);const _=1/(v+M+m);return a=M*_,c=m*_,t.copy(n).addScaledVector(Ds,a).addScaledVector(Ns,c)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Ig={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ur={h:0,s:0,l:0},$a={h:0,s:0,l:0};function zu(r,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?r+(e-r)*6*t:t<1/2?e:t<2/3?r+(e-r)*6*(2/3-t):r}class qe{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const i=e;i&&i.isColor?this.copy(i):typeof i=="number"?this.setHex(i):typeof i=="string"&&this.setStyle(i)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=_n){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,Mt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=Mt.workingColorSpace){return this.r=e,this.g=t,this.b=n,Mt.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=Mt.workingColorSpace){if(e=vd(e,1),t=Mn(t,0,1),n=Mn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,a=2*n-s;this.r=zu(a,s,e+1/3),this.g=zu(a,s,e),this.b=zu(a,s,e-1/3)}return Mt.toWorkingColorSpace(this,i),this}setStyle(e,t=_n){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let i;if(i=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const a=i[1],c=i[2];switch(a){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(c))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=i[1],a=s.length;if(a===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(a===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=_n){const n=Ig[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Ki(e.r),this.g=Ki(e.g),this.b=Ki(e.b),this}copyLinearToSRGB(e){return this.r=Ys(e.r),this.g=Ys(e.g),this.b=Ys(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=_n){return Mt.fromWorkingColorSpace(Cn.copy(this),e),Math.round(Mn(Cn.r*255,0,255))*65536+Math.round(Mn(Cn.g*255,0,255))*256+Math.round(Mn(Cn.b*255,0,255))}getHexString(e=_n){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=Mt.workingColorSpace){Mt.fromWorkingColorSpace(Cn.copy(this),t);const n=Cn.r,i=Cn.g,s=Cn.b,a=Math.max(n,i,s),c=Math.min(n,i,s);let u,h;const f=(c+a)/2;if(c===a)u=0,h=0;else{const p=a-c;switch(h=f<=.5?p/(a+c):p/(2-a-c),a){case n:u=(i-s)/p+(i<s?6:0);break;case i:u=(s-n)/p+2;break;case s:u=(n-i)/p+4;break}u/=6}return e.h=u,e.s=h,e.l=f,e}getRGB(e,t=Mt.workingColorSpace){return Mt.fromWorkingColorSpace(Cn.copy(this),t),e.r=Cn.r,e.g=Cn.g,e.b=Cn.b,e}getStyle(e=_n){Mt.fromWorkingColorSpace(Cn.copy(this),e);const t=Cn.r,n=Cn.g,i=Cn.b;return e!==_n?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${i.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(i*255)})`}offsetHSL(e,t,n){return this.getHSL(ur),this.setHSL(ur.h+e,ur.s+t,ur.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(ur),e.getHSL($a);const n=Zo(ur.h,$a.h,t),i=Zo(ur.s,$a.s,t),s=Zo(ur.l,$a.l,t);return this.setHSL(n,i,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,i=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*i,this.g=s[1]*t+s[4]*n+s[7]*i,this.b=s[2]*t+s[5]*n+s[8]*i,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Cn=new qe;qe.NAMES=Ig;let RE=0;class Ti extends Sr{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:RE++}),this.uuid=_i(),this.name="",this.blending=Xs,this.side=Zi,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=gh,this.blendDst=_h,this.blendEquation=ts,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new qe(0,0,0),this.blendAlpha=0,this.depthFunc=Zs,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Ip,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Es,this.stencilZFail=Es,this.stencilZPass=Es,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const i=this[t];if(i===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Xs&&(n.blending=this.blending),this.side!==Zi&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==gh&&(n.blendSrc=this.blendSrc),this.blendDst!==_h&&(n.blendDst=this.blendDst),this.blendEquation!==ts&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Zs&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Ip&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Es&&(n.stencilFail=this.stencilFail),this.stencilZFail!==Es&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==Es&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(s){const a=[];for(const c in s){const u=s[c];delete u.metadata,a.push(u)}return a}if(t){const s=i(e.textures),a=i(e.images);s.length>0&&(n.textures=s),a.length>0&&(n.images=a)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const i=t.length;n=new Array(i);for(let s=0;s!==i;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class ci extends Ti{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new qe(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new vi,this.combine=hg,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const on=new F,Ja=new Qe;class nn{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=ed,this.updateRanges=[],this.gpuType=gi,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,s=this.itemSize;i<s;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Ja.fromBufferAttribute(this,t),Ja.applyMatrix3(e),this.setXY(t,Ja.x,Ja.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)on.fromBufferAttribute(this,t),on.applyMatrix3(e),this.setXYZ(t,on.x,on.y,on.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)on.fromBufferAttribute(this,t),on.applyMatrix4(e),this.setXYZ(t,on.x,on.y,on.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)on.fromBufferAttribute(this,t),on.applyNormalMatrix(e),this.setXYZ(t,on.x,on.y,on.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)on.fromBufferAttribute(this,t),on.transformDirection(e),this.setXYZ(t,on.x,on.y,on.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=pi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Nt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=pi(t,this.array)),t}setX(e,t){return this.normalized&&(t=Nt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=pi(t,this.array)),t}setY(e,t){return this.normalized&&(t=Nt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=pi(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Nt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=pi(t,this.array)),t}setW(e,t){return this.normalized&&(t=Nt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=Nt(t,this.array),n=Nt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=Nt(t,this.array),n=Nt(n,this.array),i=Nt(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e*=this.itemSize,this.normalized&&(t=Nt(t,this.array),n=Nt(n,this.array),i=Nt(i,this.array),s=Nt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==ed&&(e.usage=this.usage),e}}class Lg extends nn{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Dg extends nn{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class zt extends nn{constructor(e,t,n){super(new Float32Array(e),t,n)}}let CE=0;const si=new rt,Hu=new Xt,Os=new F,ei=new Ji,Oo=new Ji,gn=new F;class hn extends Sr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:CE++}),this.uuid=_i(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Pg(e)?Dg:Lg)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new ft().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return si.makeRotationFromQuaternion(e),this.applyMatrix4(si),this}rotateX(e){return si.makeRotationX(e),this.applyMatrix4(si),this}rotateY(e){return si.makeRotationY(e),this.applyMatrix4(si),this}rotateZ(e){return si.makeRotationZ(e),this.applyMatrix4(si),this}translate(e,t,n){return si.makeTranslation(e,t,n),this.applyMatrix4(si),this}scale(e,t,n){return si.makeScale(e,t,n),this.applyMatrix4(si),this}lookAt(e){return Hu.lookAt(e),Hu.updateMatrix(),this.applyMatrix4(Hu.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Os).negate(),this.translate(Os.x,Os.y,Os.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let i=0,s=e.length;i<s;i++){const a=e[i];n.push(a.x,a.y,a.z||0)}this.setAttribute("position",new zt(n,3))}else{for(let n=0,i=t.count;n<i;n++){const s=e[n];t.setXYZ(n,s.x,s.y,s.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new Ji);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new F(-1/0,-1/0,-1/0),new F(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){const s=t[n];ei.setFromBufferAttribute(s),this.morphTargetsRelative?(gn.addVectors(this.boundingBox.min,ei.min),this.boundingBox.expandByPoint(gn),gn.addVectors(this.boundingBox.max,ei.max),this.boundingBox.expandByPoint(gn)):(this.boundingBox.expandByPoint(ei.min),this.boundingBox.expandByPoint(ei.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Ei);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new F,1/0);return}if(e){const n=this.boundingSphere.center;if(ei.setFromBufferAttribute(e),t)for(let s=0,a=t.length;s<a;s++){const c=t[s];Oo.setFromBufferAttribute(c),this.morphTargetsRelative?(gn.addVectors(ei.min,Oo.min),ei.expandByPoint(gn),gn.addVectors(ei.max,Oo.max),ei.expandByPoint(gn)):(ei.expandByPoint(Oo.min),ei.expandByPoint(Oo.max))}ei.getCenter(n);let i=0;for(let s=0,a=e.count;s<a;s++)gn.fromBufferAttribute(e,s),i=Math.max(i,n.distanceToSquared(gn));if(t)for(let s=0,a=t.length;s<a;s++){const c=t[s],u=this.morphTargetsRelative;for(let h=0,f=c.count;h<f;h++)gn.fromBufferAttribute(c,h),u&&(Os.fromBufferAttribute(e,h),gn.add(Os)),i=Math.max(i,n.distanceToSquared(gn))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,i=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new nn(new Float32Array(4*n.count),4));const a=this.getAttribute("tangent"),c=[],u=[];for(let z=0;z<n.count;z++)c[z]=new F,u[z]=new F;const h=new F,f=new F,p=new F,m=new Qe,g=new Qe,x=new Qe,M=new F,v=new F;function _(z,I,w){h.fromBufferAttribute(n,z),f.fromBufferAttribute(n,I),p.fromBufferAttribute(n,w),m.fromBufferAttribute(s,z),g.fromBufferAttribute(s,I),x.fromBufferAttribute(s,w),f.sub(h),p.sub(h),g.sub(m),x.sub(m);const H=1/(g.x*x.y-x.x*g.y);isFinite(H)&&(M.copy(f).multiplyScalar(x.y).addScaledVector(p,-g.y).multiplyScalar(H),v.copy(p).multiplyScalar(g.x).addScaledVector(f,-x.x).multiplyScalar(H),c[z].add(M),c[I].add(M),c[w].add(M),u[z].add(v),u[I].add(v),u[w].add(v))}let A=this.groups;A.length===0&&(A=[{start:0,count:e.count}]);for(let z=0,I=A.length;z<I;++z){const w=A[z],H=w.start,ee=w.count;for(let Q=H,ae=H+ee;Q<ae;Q+=3)_(e.getX(Q+0),e.getX(Q+1),e.getX(Q+2))}const P=new F,b=new F,B=new F,U=new F;function O(z){B.fromBufferAttribute(i,z),U.copy(B);const I=c[z];P.copy(I),P.sub(B.multiplyScalar(B.dot(I))).normalize(),b.crossVectors(U,I);const H=b.dot(u[z])<0?-1:1;a.setXYZW(z,P.x,P.y,P.z,H)}for(let z=0,I=A.length;z<I;++z){const w=A[z],H=w.start,ee=w.count;for(let Q=H,ae=H+ee;Q<ae;Q+=3)O(e.getX(Q+0)),O(e.getX(Q+1)),O(e.getX(Q+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new nn(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let m=0,g=n.count;m<g;m++)n.setXYZ(m,0,0,0);const i=new F,s=new F,a=new F,c=new F,u=new F,h=new F,f=new F,p=new F;if(e)for(let m=0,g=e.count;m<g;m+=3){const x=e.getX(m+0),M=e.getX(m+1),v=e.getX(m+2);i.fromBufferAttribute(t,x),s.fromBufferAttribute(t,M),a.fromBufferAttribute(t,v),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),c.fromBufferAttribute(n,x),u.fromBufferAttribute(n,M),h.fromBufferAttribute(n,v),c.add(f),u.add(f),h.add(f),n.setXYZ(x,c.x,c.y,c.z),n.setXYZ(M,u.x,u.y,u.z),n.setXYZ(v,h.x,h.y,h.z)}else for(let m=0,g=t.count;m<g;m+=3)i.fromBufferAttribute(t,m+0),s.fromBufferAttribute(t,m+1),a.fromBufferAttribute(t,m+2),f.subVectors(a,s),p.subVectors(i,s),f.cross(p),n.setXYZ(m+0,f.x,f.y,f.z),n.setXYZ(m+1,f.x,f.y,f.z),n.setXYZ(m+2,f.x,f.y,f.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)gn.fromBufferAttribute(e,t),gn.normalize(),e.setXYZ(t,gn.x,gn.y,gn.z)}toNonIndexed(){function e(c,u){const h=c.array,f=c.itemSize,p=c.normalized,m=new h.constructor(u.length*f);let g=0,x=0;for(let M=0,v=u.length;M<v;M++){c.isInterleavedBufferAttribute?g=u[M]*c.data.stride+c.offset:g=u[M]*f;for(let _=0;_<f;_++)m[x++]=h[g++]}return new nn(m,f,p)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new hn,n=this.index.array,i=this.attributes;for(const c in i){const u=i[c],h=e(u,n);t.setAttribute(c,h)}const s=this.morphAttributes;for(const c in s){const u=[],h=s[c];for(let f=0,p=h.length;f<p;f++){const m=h[f],g=e(m,n);u.push(g)}t.morphAttributes[c]=u}t.morphTargetsRelative=this.morphTargetsRelative;const a=this.groups;for(let c=0,u=a.length;c<u;c++){const h=a[c];t.addGroup(h.start,h.count,h.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const u=this.parameters;for(const h in u)u[h]!==void 0&&(e[h]=u[h]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const u in n){const h=n[u];e.data.attributes[u]=h.toJSON(e.data)}const i={};let s=!1;for(const u in this.morphAttributes){const h=this.morphAttributes[u],f=[];for(let p=0,m=h.length;p<m;p++){const g=h[p];f.push(g.toJSON(e.data))}f.length>0&&(i[u]=f,s=!0)}s&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);const a=this.groups;a.length>0&&(e.data.groups=JSON.parse(JSON.stringify(a)));const c=this.boundingSphere;return c!==null&&(e.data.boundingSphere={center:c.center.toArray(),radius:c.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const i=e.attributes;for(const h in i){const f=i[h];this.setAttribute(h,f.clone(t))}const s=e.morphAttributes;for(const h in s){const f=[],p=s[h];for(let m=0,g=p.length;m<g;m++)f.push(p[m].clone(t));this.morphAttributes[h]=f}this.morphTargetsRelative=e.morphTargetsRelative;const a=e.groups;for(let h=0,f=a.length;h<f;h++){const p=a[h];this.addGroup(p.start,p.count,p.materialIndex)}const c=e.boundingBox;c!==null&&(this.boundingBox=c.clone());const u=e.boundingSphere;return u!==null&&(this.boundingSphere=u.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Kp=new rt,qr=new oo,Qa=new Ei,Zp=new F,ec=new F,tc=new F,nc=new F,Vu=new F,ic=new F,$p=new F,rc=new F;class Te extends Xt{constructor(e=new hn,t=new ci){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}getVertexPosition(e,t){const n=this.geometry,i=n.attributes.position,s=n.morphAttributes.position,a=n.morphTargetsRelative;t.fromBufferAttribute(i,e);const c=this.morphTargetInfluences;if(s&&c){ic.set(0,0,0);for(let u=0,h=s.length;u<h;u++){const f=c[u],p=s[u];f!==0&&(Vu.fromBufferAttribute(p,e),a?ic.addScaledVector(Vu,f):ic.addScaledVector(Vu.sub(t),f))}t.add(ic)}return t}raycast(e,t){const n=this.geometry,i=this.material,s=this.matrixWorld;i!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Qa.copy(n.boundingSphere),Qa.applyMatrix4(s),qr.copy(e.ray).recast(e.near),!(Qa.containsPoint(qr.origin)===!1&&(qr.intersectSphere(Qa,Zp)===null||qr.origin.distanceToSquared(Zp)>(e.far-e.near)**2))&&(Kp.copy(s).invert(),qr.copy(e.ray).applyMatrix4(Kp),!(n.boundingBox!==null&&qr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,qr)))}_computeIntersections(e,t,n){let i;const s=this.geometry,a=this.material,c=s.index,u=s.attributes.position,h=s.attributes.uv,f=s.attributes.uv1,p=s.attributes.normal,m=s.groups,g=s.drawRange;if(c!==null)if(Array.isArray(a))for(let x=0,M=m.length;x<M;x++){const v=m[x],_=a[v.materialIndex],A=Math.max(v.start,g.start),P=Math.min(c.count,Math.min(v.start+v.count,g.start+g.count));for(let b=A,B=P;b<B;b+=3){const U=c.getX(b),O=c.getX(b+1),z=c.getX(b+2);i=sc(this,_,e,n,h,f,p,U,O,z),i&&(i.faceIndex=Math.floor(b/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),M=Math.min(c.count,g.start+g.count);for(let v=x,_=M;v<_;v+=3){const A=c.getX(v),P=c.getX(v+1),b=c.getX(v+2);i=sc(this,a,e,n,h,f,p,A,P,b),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}else if(u!==void 0)if(Array.isArray(a))for(let x=0,M=m.length;x<M;x++){const v=m[x],_=a[v.materialIndex],A=Math.max(v.start,g.start),P=Math.min(u.count,Math.min(v.start+v.count,g.start+g.count));for(let b=A,B=P;b<B;b+=3){const U=b,O=b+1,z=b+2;i=sc(this,_,e,n,h,f,p,U,O,z),i&&(i.faceIndex=Math.floor(b/3),i.face.materialIndex=v.materialIndex,t.push(i))}}else{const x=Math.max(0,g.start),M=Math.min(u.count,g.start+g.count);for(let v=x,_=M;v<_;v+=3){const A=v,P=v+1,b=v+2;i=sc(this,a,e,n,h,f,p,A,P,b),i&&(i.faceIndex=Math.floor(v/3),t.push(i))}}}}function IE(r,e,t,n,i,s,a,c){let u;if(e.side===Wn?u=n.intersectTriangle(a,s,i,!0,c):u=n.intersectTriangle(i,s,a,e.side===Zi,c),u===null)return null;rc.copy(c),rc.applyMatrix4(r.matrixWorld);const h=t.ray.origin.distanceTo(rc);return h<t.near||h>t.far?null:{distance:h,point:rc.clone(),object:r}}function sc(r,e,t,n,i,s,a,c,u,h){r.getVertexPosition(c,ec),r.getVertexPosition(u,tc),r.getVertexPosition(h,nc);const f=IE(r,e,t,n,ec,tc,nc,$p);if(f){const p=new F;mi.getBarycoord($p,ec,tc,nc,p),i&&(f.uv=mi.getInterpolatedAttribute(i,c,u,h,p,new Qe)),s&&(f.uv1=mi.getInterpolatedAttribute(s,c,u,h,p,new Qe)),a&&(f.normal=mi.getInterpolatedAttribute(a,c,u,h,p,new F),f.normal.dot(n.direction)>0&&f.normal.multiplyScalar(-1));const m={a:c,b:u,c:h,normal:new F,materialIndex:0};mi.getNormal(ec,tc,nc,m.normal),f.face=m,f.barycoord=p}return f}class en extends hn{constructor(e=1,t=1,n=1,i=1,s=1,a=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:s,depthSegments:a};const c=this;i=Math.floor(i),s=Math.floor(s),a=Math.floor(a);const u=[],h=[],f=[],p=[];let m=0,g=0;x("z","y","x",-1,-1,n,t,e,a,s,0),x("z","y","x",1,-1,n,t,-e,a,s,1),x("x","z","y",1,1,e,n,t,i,a,2),x("x","z","y",1,-1,e,n,-t,i,a,3),x("x","y","z",1,-1,e,t,n,i,s,4),x("x","y","z",-1,-1,e,t,-n,i,s,5),this.setIndex(u),this.setAttribute("position",new zt(h,3)),this.setAttribute("normal",new zt(f,3)),this.setAttribute("uv",new zt(p,2));function x(M,v,_,A,P,b,B,U,O,z,I){const w=b/O,H=B/z,ee=b/2,Q=B/2,ae=U/2,ce=O+1,$=z+1;let fe=0,re=0;const ye=new F;for(let Me=0;Me<$;Me++){const Ne=Me*H-Q;for(let Ze=0;Ze<ce;Ze++){const ht=Ze*w-ee;ye[M]=ht*A,ye[v]=Ne*P,ye[_]=ae,h.push(ye.x,ye.y,ye.z),ye[M]=0,ye[v]=0,ye[_]=U>0?1:-1,f.push(ye.x,ye.y,ye.z),p.push(Ze/O),p.push(1-Me/z),fe+=1}}for(let Me=0;Me<z;Me++)for(let Ne=0;Ne<O;Ne++){const Ze=m+Ne+ce*Me,ht=m+Ne+ce*(Me+1),le=m+(Ne+1)+ce*(Me+1),ge=m+(Ne+1)+ce*Me;u.push(Ze,ht,ge),u.push(ht,le,ge),re+=6}c.addGroup(g,re,I),g+=re,m+=fe}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new en(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function io(r){const e={};for(const t in r){e[t]={};for(const n in r[t]){const i=r[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?i.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}function Nn(r){const e={};for(let t=0;t<r.length;t++){const n=io(r[t]);for(const i in n)e[i]=n[i]}return e}function LE(r){const e=[];for(let t=0;t<r.length;t++)e.push(r[t].clone());return e}function Ng(r){const e=r.getRenderTarget();return e===null?r.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:Mt.workingColorSpace}const DE={clone:io,merge:Nn};var NE=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,OE=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class br extends Ti{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=NE,this.fragmentShader=OE,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=io(e.uniforms),this.uniformsGroups=LE(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const i in this.uniforms){const a=this.uniforms[i].value;a&&a.isTexture?t.uniforms[i]={type:"t",value:a.toJSON(e).uuid}:a&&a.isColor?t.uniforms[i]={type:"c",value:a.getHex()}:a&&a.isVector2?t.uniforms[i]={type:"v2",value:a.toArray()}:a&&a.isVector3?t.uniforms[i]={type:"v3",value:a.toArray()}:a&&a.isVector4?t.uniforms[i]={type:"v4",value:a.toArray()}:a&&a.isMatrix3?t.uniforms[i]={type:"m3",value:a.toArray()}:a&&a.isMatrix4?t.uniforms[i]={type:"m4",value:a.toArray()}:t.uniforms[i]={value:a}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Og extends Xt{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new rt,this.projectionMatrix=new rt,this.projectionMatrixInverse=new rt,this.coordinateSystem=qi}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const hr=new F,Jp=new Qe,Qp=new Qe;class On extends Og{constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=no*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Ko*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return no*2*Math.atan(Math.tan(Ko*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){hr.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(hr.x,hr.y).multiplyScalar(-e/hr.z),hr.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(hr.x,hr.y).multiplyScalar(-e/hr.z)}getViewSize(e,t){return this.getViewBounds(e,Jp,Qp),t.subVectors(Qp,Jp)}setViewOffset(e,t,n,i,s,a){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Ko*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,s=-.5*i;const a=this.view;if(this.view!==null&&this.view.enabled){const u=a.fullWidth,h=a.fullHeight;s+=a.offsetX*i/u,t-=a.offsetY*n/h,i*=a.width/u,n*=a.height/h}const c=this.filmOffset;c!==0&&(s+=e*c/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+i,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Us=-90,Fs=1;class UE extends Xt{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const i=new On(Us,Fs,e,t);i.layers=this.layers,this.add(i);const s=new On(Us,Fs,e,t);s.layers=this.layers,this.add(s);const a=new On(Us,Fs,e,t);a.layers=this.layers,this.add(a);const c=new On(Us,Fs,e,t);c.layers=this.layers,this.add(c);const u=new On(Us,Fs,e,t);u.layers=this.layers,this.add(u);const h=new On(Us,Fs,e,t);h.layers=this.layers,this.add(h)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,i,s,a,c,u]=t;for(const h of t)this.remove(h);if(e===qi)n.up.set(0,1,0),n.lookAt(1,0,0),i.up.set(0,1,0),i.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),a.up.set(0,0,1),a.lookAt(0,-1,0),c.up.set(0,1,0),c.lookAt(0,0,1),u.up.set(0,1,0),u.lookAt(0,0,-1);else if(e===Oc)n.up.set(0,-1,0),n.lookAt(-1,0,0),i.up.set(0,-1,0),i.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),a.up.set(0,0,-1),a.lookAt(0,-1,0),c.up.set(0,-1,0),c.lookAt(0,0,1),u.up.set(0,-1,0),u.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const h of t)this.add(h),h.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:i}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,a,c,u,h,f]=this.children,p=e.getRenderTarget(),m=e.getActiveCubeFace(),g=e.getActiveMipmapLevel(),x=e.xr.enabled;e.xr.enabled=!1;const M=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,i),e.render(t,s),e.setRenderTarget(n,1,i),e.render(t,a),e.setRenderTarget(n,2,i),e.render(t,c),e.setRenderTarget(n,3,i),e.render(t,u),e.setRenderTarget(n,4,i),e.render(t,h),n.texture.generateMipmaps=M,e.setRenderTarget(n,5,i),e.render(t,f),e.setRenderTarget(p,m,g),e.xr.enabled=x,n.texture.needsPMREMUpdate=!0}}class Ug extends vn{constructor(e,t,n,i,s,a,c,u,h,f){e=e!==void 0?e:[],t=t!==void 0?t:$s,super(e,t,n,i,s,a,c,u,h,f),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class FE extends ss{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new Ug(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:ti}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},i=new en(5,5,5),s=new br({name:"CubemapFromEquirect",uniforms:io(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Wn,blending:yr});s.uniforms.tEquirect.value=t;const a=new Te(i,s),c=t.minFilter;return t.minFilter===Xi&&(t.minFilter=ti),new UE(1,10,this).update(e,a),t.minFilter=c,a.geometry.dispose(),a.material.dispose(),this}clear(e,t,n,i){const s=e.getRenderTarget();for(let a=0;a<6;a++)e.setRenderTarget(this,a),e.clear(t,n,i);e.setRenderTarget(s)}}const Gu=new F,BE=new F,kE=new ft;class mr{constructor(e=new F(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const i=Gu.subVectors(n,t).cross(BE.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Gu),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/i;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||kE.getNormalMatrix(e),i=this.coplanarPoint(Gu).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Yr=new Ei,oc=new F;class xd{constructor(e=new mr,t=new mr,n=new mr,i=new mr,s=new mr,a=new mr){this.planes=[e,t,n,i,s,a]}set(e,t,n,i,s,a){const c=this.planes;return c[0].copy(e),c[1].copy(t),c[2].copy(n),c[3].copy(i),c[4].copy(s),c[5].copy(a),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=qi){const n=this.planes,i=e.elements,s=i[0],a=i[1],c=i[2],u=i[3],h=i[4],f=i[5],p=i[6],m=i[7],g=i[8],x=i[9],M=i[10],v=i[11],_=i[12],A=i[13],P=i[14],b=i[15];if(n[0].setComponents(u-s,m-h,v-g,b-_).normalize(),n[1].setComponents(u+s,m+h,v+g,b+_).normalize(),n[2].setComponents(u+a,m+f,v+x,b+A).normalize(),n[3].setComponents(u-a,m-f,v-x,b-A).normalize(),n[4].setComponents(u-c,m-p,v-M,b-P).normalize(),t===qi)n[5].setComponents(u+c,m+p,v+M,b+P).normalize();else if(t===Oc)n[5].setComponents(c,p,M,P).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Yr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Yr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Yr)}intersectsSprite(e){return Yr.center.set(0,0,0),Yr.radius=.7071067811865476,Yr.applyMatrix4(e.matrixWorld),this.intersectsSphere(Yr)}intersectsSphere(e){const t=this.planes,n=e.center,i=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const i=t[n];if(oc.x=i.normal.x>0?e.max.x:e.min.x,oc.y=i.normal.y>0?e.max.y:e.min.y,oc.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(oc)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Fg(){let r=null,e=!1,t=null,n=null;function i(s,a){t(s,a),n=r.requestAnimationFrame(i)}return{start:function(){e!==!0&&t!==null&&(n=r.requestAnimationFrame(i),e=!0)},stop:function(){r.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){r=s}}}function zE(r){const e=new WeakMap;function t(c,u){const h=c.array,f=c.usage,p=h.byteLength,m=r.createBuffer();r.bindBuffer(u,m),r.bufferData(u,h,f),c.onUploadCallback();let g;if(h instanceof Float32Array)g=r.FLOAT;else if(h instanceof Uint16Array)c.isFloat16BufferAttribute?g=r.HALF_FLOAT:g=r.UNSIGNED_SHORT;else if(h instanceof Int16Array)g=r.SHORT;else if(h instanceof Uint32Array)g=r.UNSIGNED_INT;else if(h instanceof Int32Array)g=r.INT;else if(h instanceof Int8Array)g=r.BYTE;else if(h instanceof Uint8Array)g=r.UNSIGNED_BYTE;else if(h instanceof Uint8ClampedArray)g=r.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+h);return{buffer:m,type:g,bytesPerElement:h.BYTES_PER_ELEMENT,version:c.version,size:p}}function n(c,u,h){const f=u.array,p=u.updateRanges;if(r.bindBuffer(h,c),p.length===0)r.bufferSubData(h,0,f);else{p.sort((g,x)=>g.start-x.start);let m=0;for(let g=1;g<p.length;g++){const x=p[m],M=p[g];M.start<=x.start+x.count+1?x.count=Math.max(x.count,M.start+M.count-x.start):(++m,p[m]=M)}p.length=m+1;for(let g=0,x=p.length;g<x;g++){const M=p[g];r.bufferSubData(h,M.start*f.BYTES_PER_ELEMENT,f,M.start,M.count)}u.clearUpdateRanges()}u.onUploadCallback()}function i(c){return c.isInterleavedBufferAttribute&&(c=c.data),e.get(c)}function s(c){c.isInterleavedBufferAttribute&&(c=c.data);const u=e.get(c);u&&(r.deleteBuffer(u.buffer),e.delete(c))}function a(c,u){if(c.isInterleavedBufferAttribute&&(c=c.data),c.isGLBufferAttribute){const f=e.get(c);(!f||f.version<c.version)&&e.set(c,{buffer:c.buffer,type:c.type,bytesPerElement:c.elementSize,version:c.version});return}const h=e.get(c);if(h===void 0)e.set(c,t(c,u));else if(h.version<c.version){if(h.size!==c.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(h.buffer,c,u),h.version=c.version}}return{get:i,remove:s,update:a}}class ao extends hn{constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};const s=e/2,a=t/2,c=Math.floor(n),u=Math.floor(i),h=c+1,f=u+1,p=e/c,m=t/u,g=[],x=[],M=[],v=[];for(let _=0;_<f;_++){const A=_*m-a;for(let P=0;P<h;P++){const b=P*p-s;x.push(b,-A,0),M.push(0,0,1),v.push(P/c),v.push(1-_/u)}}for(let _=0;_<u;_++)for(let A=0;A<c;A++){const P=A+h*_,b=A+h*(_+1),B=A+1+h*(_+1),U=A+1+h*_;g.push(P,b,U),g.push(b,B,U)}this.setIndex(g),this.setAttribute("position",new zt(x,3)),this.setAttribute("normal",new zt(M,3)),this.setAttribute("uv",new zt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ao(e.width,e.height,e.widthSegments,e.heightSegments)}}var HE=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,VE=`#ifdef USE_ALPHAHASH
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
#endif`,GE=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,WE=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,jE=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,XE=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,qE=`#ifdef USE_AOMAP
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
#endif`,YE=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,KE=`#ifdef USE_BATCHING
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
#endif`,ZE=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,$E=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,JE=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,QE=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,eA=`#ifdef USE_IRIDESCENCE
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
#endif`,tA=`#ifdef USE_BUMPMAP
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
#endif`,nA=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,iA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,rA=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,sA=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,oA=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,aA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,cA=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,lA=`#if defined( USE_COLOR_ALPHA )
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
#endif`,uA=`#define PI 3.141592653589793
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
} // validated`,hA=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,dA=`vec3 transformedNormal = objectNormal;
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
#endif`,fA=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,pA=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,mA=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,gA=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,_A="gl_FragColor = linearToOutputTexel( gl_FragColor );",vA=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,yA=`#ifdef USE_ENVMAP
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
#endif`,xA=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,bA=`#ifdef USE_ENVMAP
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
#endif`,SA=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,MA=`#ifdef USE_ENVMAP
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
#endif`,TA=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,EA=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,AA=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,wA=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,PA=`#ifdef USE_GRADIENTMAP
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
}`,RA=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,CA=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,IA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,LA=`uniform bool receiveShadow;
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
#endif`,DA=`#ifdef USE_ENVMAP
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
#endif`,NA=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,OA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,UA=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,FA=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,BA=`PhysicalMaterial material;
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
#endif`,kA=`struct PhysicalMaterial {
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
}`,zA=`
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
#endif`,HA=`#if defined( RE_IndirectDiffuse )
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
#endif`,VA=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,GA=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,WA=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,jA=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,XA=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,qA=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,YA=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,KA=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,ZA=`#if defined( USE_POINTS_UV )
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
#endif`,$A=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,JA=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,QA=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,ew=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,tw=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,nw=`#ifdef USE_MORPHTARGETS
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
#endif`,iw=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,rw=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,sw=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,ow=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,aw=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,cw=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,lw=`#ifdef USE_NORMALMAP
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
#endif`,uw=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,hw=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,dw=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,fw=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,pw=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,mw=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,gw=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,_w=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,vw=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,yw=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,xw=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,bw=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,Sw=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,Mw=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,Tw=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,Ew=`float getShadowMask() {
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
}`,Aw=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,ww=`#ifdef USE_SKINNING
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
#endif`,Pw=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,Rw=`#ifdef USE_SKINNING
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
#endif`,Cw=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,Iw=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,Lw=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,Dw=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,Nw=`#ifdef USE_TRANSMISSION
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
#endif`,Ow=`#ifdef USE_TRANSMISSION
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
#endif`,Uw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Fw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Bw=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,kw=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const zw=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,Hw=`uniform sampler2D t2D;
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
}`,Vw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Gw=`#ifdef ENVMAP_TYPE_CUBE
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
}`,Ww=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,jw=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Xw=`#include <common>
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
}`,qw=`#if DEPTH_PACKING == 3200
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
}`,Yw=`#define DISTANCE
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
}`,Kw=`#define DISTANCE
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
}`,Zw=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,$w=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Jw=`uniform float scale;
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
}`,Qw=`uniform vec3 diffuse;
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
}`,e1=`#include <common>
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
}`,t1=`uniform vec3 diffuse;
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
}`,n1=`#define LAMBERT
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
}`,i1=`#define LAMBERT
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
}`,r1=`#define MATCAP
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
}`,s1=`#define MATCAP
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
}`,o1=`#define NORMAL
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
}`,a1=`#define NORMAL
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
}`,c1=`#define PHONG
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
}`,l1=`#define PHONG
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
}`,u1=`#define STANDARD
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
}`,h1=`#define STANDARD
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
}`,d1=`#define TOON
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
}`,f1=`#define TOON
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
}`,p1=`uniform float size;
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
}`,m1=`uniform vec3 diffuse;
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
}`,g1=`#include <common>
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
}`,_1=`uniform vec3 color;
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
}`,v1=`uniform float rotation;
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
}`,y1=`uniform vec3 diffuse;
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
}`,mt={alphahash_fragment:HE,alphahash_pars_fragment:VE,alphamap_fragment:GE,alphamap_pars_fragment:WE,alphatest_fragment:jE,alphatest_pars_fragment:XE,aomap_fragment:qE,aomap_pars_fragment:YE,batching_pars_vertex:KE,batching_vertex:ZE,begin_vertex:$E,beginnormal_vertex:JE,bsdfs:QE,iridescence_fragment:eA,bumpmap_pars_fragment:tA,clipping_planes_fragment:nA,clipping_planes_pars_fragment:iA,clipping_planes_pars_vertex:rA,clipping_planes_vertex:sA,color_fragment:oA,color_pars_fragment:aA,color_pars_vertex:cA,color_vertex:lA,common:uA,cube_uv_reflection_fragment:hA,defaultnormal_vertex:dA,displacementmap_pars_vertex:fA,displacementmap_vertex:pA,emissivemap_fragment:mA,emissivemap_pars_fragment:gA,colorspace_fragment:_A,colorspace_pars_fragment:vA,envmap_fragment:yA,envmap_common_pars_fragment:xA,envmap_pars_fragment:bA,envmap_pars_vertex:SA,envmap_physical_pars_fragment:DA,envmap_vertex:MA,fog_vertex:TA,fog_pars_vertex:EA,fog_fragment:AA,fog_pars_fragment:wA,gradientmap_pars_fragment:PA,lightmap_pars_fragment:RA,lights_lambert_fragment:CA,lights_lambert_pars_fragment:IA,lights_pars_begin:LA,lights_toon_fragment:NA,lights_toon_pars_fragment:OA,lights_phong_fragment:UA,lights_phong_pars_fragment:FA,lights_physical_fragment:BA,lights_physical_pars_fragment:kA,lights_fragment_begin:zA,lights_fragment_maps:HA,lights_fragment_end:VA,logdepthbuf_fragment:GA,logdepthbuf_pars_fragment:WA,logdepthbuf_pars_vertex:jA,logdepthbuf_vertex:XA,map_fragment:qA,map_pars_fragment:YA,map_particle_fragment:KA,map_particle_pars_fragment:ZA,metalnessmap_fragment:$A,metalnessmap_pars_fragment:JA,morphinstance_vertex:QA,morphcolor_vertex:ew,morphnormal_vertex:tw,morphtarget_pars_vertex:nw,morphtarget_vertex:iw,normal_fragment_begin:rw,normal_fragment_maps:sw,normal_pars_fragment:ow,normal_pars_vertex:aw,normal_vertex:cw,normalmap_pars_fragment:lw,clearcoat_normal_fragment_begin:uw,clearcoat_normal_fragment_maps:hw,clearcoat_pars_fragment:dw,iridescence_pars_fragment:fw,opaque_fragment:pw,packing:mw,premultiplied_alpha_fragment:gw,project_vertex:_w,dithering_fragment:vw,dithering_pars_fragment:yw,roughnessmap_fragment:xw,roughnessmap_pars_fragment:bw,shadowmap_pars_fragment:Sw,shadowmap_pars_vertex:Mw,shadowmap_vertex:Tw,shadowmask_pars_fragment:Ew,skinbase_vertex:Aw,skinning_pars_vertex:ww,skinning_vertex:Pw,skinnormal_vertex:Rw,specularmap_fragment:Cw,specularmap_pars_fragment:Iw,tonemapping_fragment:Lw,tonemapping_pars_fragment:Dw,transmission_fragment:Nw,transmission_pars_fragment:Ow,uv_pars_fragment:Uw,uv_pars_vertex:Fw,uv_vertex:Bw,worldpos_vertex:kw,background_vert:zw,background_frag:Hw,backgroundCube_vert:Vw,backgroundCube_frag:Gw,cube_vert:Ww,cube_frag:jw,depth_vert:Xw,depth_frag:qw,distanceRGBA_vert:Yw,distanceRGBA_frag:Kw,equirect_vert:Zw,equirect_frag:$w,linedashed_vert:Jw,linedashed_frag:Qw,meshbasic_vert:e1,meshbasic_frag:t1,meshlambert_vert:n1,meshlambert_frag:i1,meshmatcap_vert:r1,meshmatcap_frag:s1,meshnormal_vert:o1,meshnormal_frag:a1,meshphong_vert:c1,meshphong_frag:l1,meshphysical_vert:u1,meshphysical_frag:h1,meshtoon_vert:d1,meshtoon_frag:f1,points_vert:p1,points_frag:m1,shadow_vert:g1,shadow_frag:_1,sprite_vert:v1,sprite_frag:y1},we={common:{diffuse:{value:new qe(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new ft},alphaMap:{value:null},alphaMapTransform:{value:new ft},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new ft}},envmap:{envMap:{value:null},envMapRotation:{value:new ft},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new ft}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new ft}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new ft},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new ft},normalScale:{value:new Qe(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new ft},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new ft}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new ft}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new ft}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new qe(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new qe(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new ft},alphaTest:{value:0},uvTransform:{value:new ft}},sprite:{diffuse:{value:new qe(16777215)},opacity:{value:1},center:{value:new Qe(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new ft},alphaMap:{value:null},alphaMapTransform:{value:new ft},alphaTest:{value:0}}},Si={basic:{uniforms:Nn([we.common,we.specularmap,we.envmap,we.aomap,we.lightmap,we.fog]),vertexShader:mt.meshbasic_vert,fragmentShader:mt.meshbasic_frag},lambert:{uniforms:Nn([we.common,we.specularmap,we.envmap,we.aomap,we.lightmap,we.emissivemap,we.bumpmap,we.normalmap,we.displacementmap,we.fog,we.lights,{emissive:{value:new qe(0)}}]),vertexShader:mt.meshlambert_vert,fragmentShader:mt.meshlambert_frag},phong:{uniforms:Nn([we.common,we.specularmap,we.envmap,we.aomap,we.lightmap,we.emissivemap,we.bumpmap,we.normalmap,we.displacementmap,we.fog,we.lights,{emissive:{value:new qe(0)},specular:{value:new qe(1118481)},shininess:{value:30}}]),vertexShader:mt.meshphong_vert,fragmentShader:mt.meshphong_frag},standard:{uniforms:Nn([we.common,we.envmap,we.aomap,we.lightmap,we.emissivemap,we.bumpmap,we.normalmap,we.displacementmap,we.roughnessmap,we.metalnessmap,we.fog,we.lights,{emissive:{value:new qe(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:mt.meshphysical_vert,fragmentShader:mt.meshphysical_frag},toon:{uniforms:Nn([we.common,we.aomap,we.lightmap,we.emissivemap,we.bumpmap,we.normalmap,we.displacementmap,we.gradientmap,we.fog,we.lights,{emissive:{value:new qe(0)}}]),vertexShader:mt.meshtoon_vert,fragmentShader:mt.meshtoon_frag},matcap:{uniforms:Nn([we.common,we.bumpmap,we.normalmap,we.displacementmap,we.fog,{matcap:{value:null}}]),vertexShader:mt.meshmatcap_vert,fragmentShader:mt.meshmatcap_frag},points:{uniforms:Nn([we.points,we.fog]),vertexShader:mt.points_vert,fragmentShader:mt.points_frag},dashed:{uniforms:Nn([we.common,we.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:mt.linedashed_vert,fragmentShader:mt.linedashed_frag},depth:{uniforms:Nn([we.common,we.displacementmap]),vertexShader:mt.depth_vert,fragmentShader:mt.depth_frag},normal:{uniforms:Nn([we.common,we.bumpmap,we.normalmap,we.displacementmap,{opacity:{value:1}}]),vertexShader:mt.meshnormal_vert,fragmentShader:mt.meshnormal_frag},sprite:{uniforms:Nn([we.sprite,we.fog]),vertexShader:mt.sprite_vert,fragmentShader:mt.sprite_frag},background:{uniforms:{uvTransform:{value:new ft},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:mt.background_vert,fragmentShader:mt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new ft}},vertexShader:mt.backgroundCube_vert,fragmentShader:mt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:mt.cube_vert,fragmentShader:mt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:mt.equirect_vert,fragmentShader:mt.equirect_frag},distanceRGBA:{uniforms:Nn([we.common,we.displacementmap,{referencePosition:{value:new F},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:mt.distanceRGBA_vert,fragmentShader:mt.distanceRGBA_frag},shadow:{uniforms:Nn([we.lights,we.fog,{color:{value:new qe(0)},opacity:{value:1}}]),vertexShader:mt.shadow_vert,fragmentShader:mt.shadow_frag}};Si.physical={uniforms:Nn([Si.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new ft},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new ft},clearcoatNormalScale:{value:new Qe(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new ft},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new ft},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new ft},sheen:{value:0},sheenColor:{value:new qe(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new ft},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new ft},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new ft},transmissionSamplerSize:{value:new Qe},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new ft},attenuationDistance:{value:0},attenuationColor:{value:new qe(0)},specularColor:{value:new qe(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new ft},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new ft},anisotropyVector:{value:new Qe},anisotropyMap:{value:null},anisotropyMapTransform:{value:new ft}}]),vertexShader:mt.meshphysical_vert,fragmentShader:mt.meshphysical_frag};const ac={r:0,b:0,g:0},Kr=new vi,x1=new rt;function b1(r,e,t,n,i,s,a){const c=new qe(0);let u=s===!0?0:1,h,f,p=null,m=0,g=null;function x(A){let P=A.isScene===!0?A.background:null;return P&&P.isTexture&&(P=(A.backgroundBlurriness>0?t:e).get(P)),P}function M(A){let P=!1;const b=x(A);b===null?_(c,u):b&&b.isColor&&(_(b,1),P=!0);const B=r.xr.getEnvironmentBlendMode();B==="additive"?n.buffers.color.setClear(0,0,0,1,a):B==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,a),(r.autoClear||P)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),r.clear(r.autoClearColor,r.autoClearDepth,r.autoClearStencil))}function v(A,P){const b=x(P);b&&(b.isCubeTexture||b.mapping===kc)?(f===void 0&&(f=new Te(new en(1,1,1),new br({name:"BackgroundCubeMaterial",uniforms:io(Si.backgroundCube.uniforms),vertexShader:Si.backgroundCube.vertexShader,fragmentShader:Si.backgroundCube.fragmentShader,side:Wn,depthTest:!1,depthWrite:!1,fog:!1})),f.geometry.deleteAttribute("normal"),f.geometry.deleteAttribute("uv"),f.onBeforeRender=function(B,U,O){this.matrixWorld.copyPosition(O.matrixWorld)},Object.defineProperty(f.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(f)),Kr.copy(P.backgroundRotation),Kr.x*=-1,Kr.y*=-1,Kr.z*=-1,b.isCubeTexture&&b.isRenderTargetTexture===!1&&(Kr.y*=-1,Kr.z*=-1),f.material.uniforms.envMap.value=b,f.material.uniforms.flipEnvMap.value=b.isCubeTexture&&b.isRenderTargetTexture===!1?-1:1,f.material.uniforms.backgroundBlurriness.value=P.backgroundBlurriness,f.material.uniforms.backgroundIntensity.value=P.backgroundIntensity,f.material.uniforms.backgroundRotation.value.setFromMatrix4(x1.makeRotationFromEuler(Kr)),f.material.toneMapped=Mt.getTransfer(b.colorSpace)!==Ut,(p!==b||m!==b.version||g!==r.toneMapping)&&(f.material.needsUpdate=!0,p=b,m=b.version,g=r.toneMapping),f.layers.enableAll(),A.unshift(f,f.geometry,f.material,0,0,null)):b&&b.isTexture&&(h===void 0&&(h=new Te(new ao(2,2),new br({name:"BackgroundMaterial",uniforms:io(Si.background.uniforms),vertexShader:Si.background.vertexShader,fragmentShader:Si.background.fragmentShader,side:Zi,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),Object.defineProperty(h.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(h)),h.material.uniforms.t2D.value=b,h.material.uniforms.backgroundIntensity.value=P.backgroundIntensity,h.material.toneMapped=Mt.getTransfer(b.colorSpace)!==Ut,b.matrixAutoUpdate===!0&&b.updateMatrix(),h.material.uniforms.uvTransform.value.copy(b.matrix),(p!==b||m!==b.version||g!==r.toneMapping)&&(h.material.needsUpdate=!0,p=b,m=b.version,g=r.toneMapping),h.layers.enableAll(),A.unshift(h,h.geometry,h.material,0,0,null))}function _(A,P){A.getRGB(ac,Ng(r)),n.buffers.color.setClear(ac.r,ac.g,ac.b,P,a)}return{getClearColor:function(){return c},setClearColor:function(A,P=1){c.set(A),u=P,_(c,u)},getClearAlpha:function(){return u},setClearAlpha:function(A){u=A,_(c,u)},render:M,addToRenderList:v}}function S1(r,e){const t=r.getParameter(r.MAX_VERTEX_ATTRIBS),n={},i=m(null);let s=i,a=!1;function c(w,H,ee,Q,ae){let ce=!1;const $=p(Q,ee,H);s!==$&&(s=$,h(s.object)),ce=g(w,Q,ee,ae),ce&&x(w,Q,ee,ae),ae!==null&&e.update(ae,r.ELEMENT_ARRAY_BUFFER),(ce||a)&&(a=!1,b(w,H,ee,Q),ae!==null&&r.bindBuffer(r.ELEMENT_ARRAY_BUFFER,e.get(ae).buffer))}function u(){return r.createVertexArray()}function h(w){return r.bindVertexArray(w)}function f(w){return r.deleteVertexArray(w)}function p(w,H,ee){const Q=ee.wireframe===!0;let ae=n[w.id];ae===void 0&&(ae={},n[w.id]=ae);let ce=ae[H.id];ce===void 0&&(ce={},ae[H.id]=ce);let $=ce[Q];return $===void 0&&($=m(u()),ce[Q]=$),$}function m(w){const H=[],ee=[],Q=[];for(let ae=0;ae<t;ae++)H[ae]=0,ee[ae]=0,Q[ae]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:H,enabledAttributes:ee,attributeDivisors:Q,object:w,attributes:{},index:null}}function g(w,H,ee,Q){const ae=s.attributes,ce=H.attributes;let $=0;const fe=ee.getAttributes();for(const re in fe)if(fe[re].location>=0){const Me=ae[re];let Ne=ce[re];if(Ne===void 0&&(re==="instanceMatrix"&&w.instanceMatrix&&(Ne=w.instanceMatrix),re==="instanceColor"&&w.instanceColor&&(Ne=w.instanceColor)),Me===void 0||Me.attribute!==Ne||Ne&&Me.data!==Ne.data)return!0;$++}return s.attributesNum!==$||s.index!==Q}function x(w,H,ee,Q){const ae={},ce=H.attributes;let $=0;const fe=ee.getAttributes();for(const re in fe)if(fe[re].location>=0){let Me=ce[re];Me===void 0&&(re==="instanceMatrix"&&w.instanceMatrix&&(Me=w.instanceMatrix),re==="instanceColor"&&w.instanceColor&&(Me=w.instanceColor));const Ne={};Ne.attribute=Me,Me&&Me.data&&(Ne.data=Me.data),ae[re]=Ne,$++}s.attributes=ae,s.attributesNum=$,s.index=Q}function M(){const w=s.newAttributes;for(let H=0,ee=w.length;H<ee;H++)w[H]=0}function v(w){_(w,0)}function _(w,H){const ee=s.newAttributes,Q=s.enabledAttributes,ae=s.attributeDivisors;ee[w]=1,Q[w]===0&&(r.enableVertexAttribArray(w),Q[w]=1),ae[w]!==H&&(r.vertexAttribDivisor(w,H),ae[w]=H)}function A(){const w=s.newAttributes,H=s.enabledAttributes;for(let ee=0,Q=H.length;ee<Q;ee++)H[ee]!==w[ee]&&(r.disableVertexAttribArray(ee),H[ee]=0)}function P(w,H,ee,Q,ae,ce,$){$===!0?r.vertexAttribIPointer(w,H,ee,ae,ce):r.vertexAttribPointer(w,H,ee,Q,ae,ce)}function b(w,H,ee,Q){M();const ae=Q.attributes,ce=ee.getAttributes(),$=H.defaultAttributeValues;for(const fe in ce){const re=ce[fe];if(re.location>=0){let ye=ae[fe];if(ye===void 0&&(fe==="instanceMatrix"&&w.instanceMatrix&&(ye=w.instanceMatrix),fe==="instanceColor"&&w.instanceColor&&(ye=w.instanceColor)),ye!==void 0){const Me=ye.normalized,Ne=ye.itemSize,Ze=e.get(ye);if(Ze===void 0)continue;const ht=Ze.buffer,le=Ze.type,ge=Ze.bytesPerElement,Oe=le===r.INT||le===r.UNSIGNED_INT||ye.gpuType===ld;if(ye.isInterleavedBufferAttribute){const Se=ye.data,We=Se.stride,tt=ye.offset;if(Se.isInstancedInterleavedBuffer){for(let st=0;st<re.locationSize;st++)_(re.location+st,Se.meshPerAttribute);w.isInstancedMesh!==!0&&Q._maxInstanceCount===void 0&&(Q._maxInstanceCount=Se.meshPerAttribute*Se.count)}else for(let st=0;st<re.locationSize;st++)v(re.location+st);r.bindBuffer(r.ARRAY_BUFFER,ht);for(let st=0;st<re.locationSize;st++)P(re.location+st,Ne/re.locationSize,le,Me,We*ge,(tt+Ne/re.locationSize*st)*ge,Oe)}else{if(ye.isInstancedBufferAttribute){for(let Se=0;Se<re.locationSize;Se++)_(re.location+Se,ye.meshPerAttribute);w.isInstancedMesh!==!0&&Q._maxInstanceCount===void 0&&(Q._maxInstanceCount=ye.meshPerAttribute*ye.count)}else for(let Se=0;Se<re.locationSize;Se++)v(re.location+Se);r.bindBuffer(r.ARRAY_BUFFER,ht);for(let Se=0;Se<re.locationSize;Se++)P(re.location+Se,Ne/re.locationSize,le,Me,Ne*ge,Ne/re.locationSize*Se*ge,Oe)}}else if($!==void 0){const Me=$[fe];if(Me!==void 0)switch(Me.length){case 2:r.vertexAttrib2fv(re.location,Me);break;case 3:r.vertexAttrib3fv(re.location,Me);break;case 4:r.vertexAttrib4fv(re.location,Me);break;default:r.vertexAttrib1fv(re.location,Me)}}}}A()}function B(){z();for(const w in n){const H=n[w];for(const ee in H){const Q=H[ee];for(const ae in Q)f(Q[ae].object),delete Q[ae];delete H[ee]}delete n[w]}}function U(w){if(n[w.id]===void 0)return;const H=n[w.id];for(const ee in H){const Q=H[ee];for(const ae in Q)f(Q[ae].object),delete Q[ae];delete H[ee]}delete n[w.id]}function O(w){for(const H in n){const ee=n[H];if(ee[w.id]===void 0)continue;const Q=ee[w.id];for(const ae in Q)f(Q[ae].object),delete Q[ae];delete ee[w.id]}}function z(){I(),a=!0,s!==i&&(s=i,h(s.object))}function I(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:c,reset:z,resetDefaultState:I,dispose:B,releaseStatesOfGeometry:U,releaseStatesOfProgram:O,initAttributes:M,enableAttribute:v,disableUnusedAttributes:A}}function M1(r,e,t){let n;function i(h){n=h}function s(h,f){r.drawArrays(n,h,f),t.update(f,n,1)}function a(h,f,p){p!==0&&(r.drawArraysInstanced(n,h,f,p),t.update(f,n,p))}function c(h,f,p){if(p===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,h,0,f,0,p);let g=0;for(let x=0;x<p;x++)g+=f[x];t.update(g,n,1)}function u(h,f,p,m){if(p===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let x=0;x<h.length;x++)a(h[x],f[x],m[x]);else{g.multiDrawArraysInstancedWEBGL(n,h,0,f,0,m,0,p);let x=0;for(let M=0;M<p;M++)x+=f[M]*m[M];t.update(x,n,1)}}this.setMode=i,this.render=s,this.renderInstances=a,this.renderMultiDraw=c,this.renderMultiDrawInstances=u}function T1(r,e,t,n){let i;function s(){if(i!==void 0)return i;if(e.has("EXT_texture_filter_anisotropic")===!0){const O=e.get("EXT_texture_filter_anisotropic");i=r.getParameter(O.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function a(O){return!(O!==ai&&n.convert(O)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_FORMAT))}function c(O){const z=O===na&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(O!==$i&&n.convert(O)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_TYPE)&&O!==gi&&!z)}function u(O){if(O==="highp"){if(r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.HIGH_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.HIGH_FLOAT).precision>0)return"highp";O="mediump"}return O==="mediump"&&r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.MEDIUM_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let h=t.precision!==void 0?t.precision:"highp";const f=u(h);f!==h&&(console.warn("THREE.WebGLRenderer:",h,"not supported, using",f,"instead."),h=f);const p=t.logarithmicDepthBuffer===!0,m=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),g=r.getParameter(r.MAX_TEXTURE_IMAGE_UNITS),x=r.getParameter(r.MAX_VERTEX_TEXTURE_IMAGE_UNITS),M=r.getParameter(r.MAX_TEXTURE_SIZE),v=r.getParameter(r.MAX_CUBE_MAP_TEXTURE_SIZE),_=r.getParameter(r.MAX_VERTEX_ATTRIBS),A=r.getParameter(r.MAX_VERTEX_UNIFORM_VECTORS),P=r.getParameter(r.MAX_VARYING_VECTORS),b=r.getParameter(r.MAX_FRAGMENT_UNIFORM_VECTORS),B=x>0,U=r.getParameter(r.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:u,textureFormatReadable:a,textureTypeReadable:c,precision:h,logarithmicDepthBuffer:p,reverseDepthBuffer:m,maxTextures:g,maxVertexTextures:x,maxTextureSize:M,maxCubemapSize:v,maxAttributes:_,maxVertexUniforms:A,maxVaryings:P,maxFragmentUniforms:b,vertexTextures:B,maxSamples:U}}function E1(r){const e=this;let t=null,n=0,i=!1,s=!1;const a=new mr,c=new ft,u={value:null,needsUpdate:!1};this.uniform=u,this.numPlanes=0,this.numIntersection=0,this.init=function(p,m){const g=p.length!==0||m||n!==0||i;return i=m,n=p.length,g},this.beginShadows=function(){s=!0,f(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(p,m){t=f(p,m,0)},this.setState=function(p,m,g){const x=p.clippingPlanes,M=p.clipIntersection,v=p.clipShadows,_=r.get(p);if(!i||x===null||x.length===0||s&&!v)s?f(null):h();else{const A=s?0:n,P=A*4;let b=_.clippingState||null;u.value=b,b=f(x,m,P,g);for(let B=0;B!==P;++B)b[B]=t[B];_.clippingState=b,this.numIntersection=M?this.numPlanes:0,this.numPlanes+=A}};function h(){u.value!==t&&(u.value=t,u.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function f(p,m,g,x){const M=p!==null?p.length:0;let v=null;if(M!==0){if(v=u.value,x!==!0||v===null){const _=g+M*4,A=m.matrixWorldInverse;c.getNormalMatrix(A),(v===null||v.length<_)&&(v=new Float32Array(_));for(let P=0,b=g;P!==M;++P,b+=4)a.copy(p[P]).applyMatrix4(A,c),a.normal.toArray(v,b),v[b+3]=a.constant}u.value=v,u.needsUpdate=!0}return e.numPlanes=M,e.numIntersection=0,v}}function A1(r){let e=new WeakMap;function t(a,c){return c===Eh?a.mapping=$s:c===Ah&&(a.mapping=Js),a}function n(a){if(a&&a.isTexture){const c=a.mapping;if(c===Eh||c===Ah)if(e.has(a)){const u=e.get(a).texture;return t(u,a.mapping)}else{const u=a.image;if(u&&u.height>0){const h=new FE(u.height);return h.fromEquirectangularTexture(r,a),e.set(a,h),a.addEventListener("dispose",i),t(h.texture,a.mapping)}else return null}}return a}function i(a){const c=a.target;c.removeEventListener("dispose",i);const u=e.get(c);u!==void 0&&(e.delete(c),u.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class bd extends Og{constructor(e=-1,t=1,n=1,i=-1,s=.1,a=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=s,this.far=a,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,s,a){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=a,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2;let s=n-e,a=n+e,c=i+t,u=i-t;if(this.view!==null&&this.view.enabled){const h=(this.right-this.left)/this.view.fullWidth/this.zoom,f=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=h*this.view.offsetX,a=s+h*this.view.width,c-=f*this.view.offsetY,u=c-f*this.view.height}this.projectionMatrix.makeOrthographic(s,a,c,u,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Gs=4,em=[.125,.215,.35,.446,.526,.582],ns=20,Wu=new bd,tm=new qe;let ju=null,Xu=0,qu=0,Yu=!1;const Qr=(1+Math.sqrt(5))/2,Bs=1/Qr,nm=[new F(-Qr,Bs,0),new F(Qr,Bs,0),new F(-Bs,0,Qr),new F(Bs,0,Qr),new F(0,Qr,-Bs),new F(0,Qr,Bs),new F(-1,1,-1),new F(1,1,-1),new F(-1,1,1),new F(1,1,1)];class im{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){ju=this._renderer.getRenderTarget(),Xu=this._renderer.getActiveCubeFace(),qu=this._renderer.getActiveMipmapLevel(),Yu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,i,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=om(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=sm(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(ju,Xu,qu),this._renderer.xr.enabled=Yu,e.scissorTest=!1,cc(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===$s||e.mapping===Js?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),ju=this._renderer.getRenderTarget(),Xu=this._renderer.getActiveCubeFace(),qu=this._renderer.getActiveMipmapLevel(),Yu=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:ti,minFilter:ti,generateMipmaps:!1,type:na,format:ai,colorSpace:Fn,depthBuffer:!1},i=rm(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=rm(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=w1(s)),this._blurMaterial=P1(s,e,t)}return i}_compileMaterial(e){const t=new Te(this._lodPlanes[0],e);this._renderer.compile(t,Wu)}_sceneToCubeUV(e,t,n,i){const c=new On(90,1,t,n),u=[1,-1,1,1,1,1],h=[1,1,1,-1,-1,-1],f=this._renderer,p=f.autoClear,m=f.toneMapping;f.getClearColor(tm),f.toneMapping=xr,f.autoClear=!1;const g=new ci({name:"PMREM.Background",side:Wn,depthWrite:!1,depthTest:!1}),x=new Te(new en,g);let M=!1;const v=e.background;v?v.isColor&&(g.color.copy(v),e.background=null,M=!0):(g.color.copy(tm),M=!0);for(let _=0;_<6;_++){const A=_%3;A===0?(c.up.set(0,u[_],0),c.lookAt(h[_],0,0)):A===1?(c.up.set(0,0,u[_]),c.lookAt(0,h[_],0)):(c.up.set(0,u[_],0),c.lookAt(0,0,h[_]));const P=this._cubeSize;cc(i,A*P,_>2?P:0,P,P),f.setRenderTarget(i),M&&f.render(x,c),f.render(e,c)}x.geometry.dispose(),x.material.dispose(),f.toneMapping=m,f.autoClear=p,e.background=v}_textureToCubeUV(e,t){const n=this._renderer,i=e.mapping===$s||e.mapping===Js;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=om()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=sm());const s=i?this._cubemapMaterial:this._equirectMaterial,a=new Te(this._lodPlanes[0],s),c=s.uniforms;c.envMap.value=e;const u=this._cubeSize;cc(t,0,0,3*u,2*u),n.setRenderTarget(t),n.render(a,Wu)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const i=this._lodPlanes.length;for(let s=1;s<i;s++){const a=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),c=nm[(i-s-1)%nm.length];this._blur(e,s-1,s,a,c)}t.autoClear=n}_blur(e,t,n,i,s){const a=this._pingPongRenderTarget;this._halfBlur(e,a,t,n,i,"latitudinal",s),this._halfBlur(a,e,n,n,i,"longitudinal",s)}_halfBlur(e,t,n,i,s,a,c){const u=this._renderer,h=this._blurMaterial;a!=="latitudinal"&&a!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const f=3,p=new Te(this._lodPlanes[i],h),m=h.uniforms,g=this._sizeLods[n]-1,x=isFinite(s)?Math.PI/(2*g):2*Math.PI/(2*ns-1),M=s/x,v=isFinite(s)?1+Math.floor(f*M):ns;v>ns&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${v} samples when the maximum is set to ${ns}`);const _=[];let A=0;for(let O=0;O<ns;++O){const z=O/M,I=Math.exp(-z*z/2);_.push(I),O===0?A+=I:O<v&&(A+=2*I)}for(let O=0;O<_.length;O++)_[O]=_[O]/A;m.envMap.value=e.texture,m.samples.value=v,m.weights.value=_,m.latitudinal.value=a==="latitudinal",c&&(m.poleAxis.value=c);const{_lodMax:P}=this;m.dTheta.value=x,m.mipInt.value=P-n;const b=this._sizeLods[i],B=3*b*(i>P-Gs?i-P+Gs:0),U=4*(this._cubeSize-b);cc(t,B,U,3*b,2*b),u.setRenderTarget(t),u.render(p,Wu)}}function w1(r){const e=[],t=[],n=[];let i=r;const s=r-Gs+1+em.length;for(let a=0;a<s;a++){const c=Math.pow(2,i);t.push(c);let u=1/c;a>r-Gs?u=em[a-r+Gs-1]:a===0&&(u=0),n.push(u);const h=1/(c-2),f=-h,p=1+h,m=[f,f,p,f,p,p,f,f,p,p,f,p],g=6,x=6,M=3,v=2,_=1,A=new Float32Array(M*x*g),P=new Float32Array(v*x*g),b=new Float32Array(_*x*g);for(let U=0;U<g;U++){const O=U%3*2/3-1,z=U>2?0:-1,I=[O,z,0,O+2/3,z,0,O+2/3,z+1,0,O,z,0,O+2/3,z+1,0,O,z+1,0];A.set(I,M*x*U),P.set(m,v*x*U);const w=[U,U,U,U,U,U];b.set(w,_*x*U)}const B=new hn;B.setAttribute("position",new nn(A,M)),B.setAttribute("uv",new nn(P,v)),B.setAttribute("faceIndex",new nn(b,_)),e.push(B),i>Gs&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function rm(r,e,t){const n=new ss(r,e,t);return n.texture.mapping=kc,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function cc(r,e,t,n,i){r.viewport.set(e,t,n,i),r.scissor.set(e,t,n,i)}function P1(r,e,t){const n=new Float32Array(ns),i=new F(0,1,0);return new br({name:"SphericalGaussianBlur",defines:{n:ns,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${r}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:Sd(),fragmentShader:`

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
		`,blending:yr,depthTest:!1,depthWrite:!1})}function sm(){return new br({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Sd(),fragmentShader:`

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
		`,blending:yr,depthTest:!1,depthWrite:!1})}function om(){return new br({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Sd(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:yr,depthTest:!1,depthWrite:!1})}function Sd(){return`

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
	`}function R1(r){let e=new WeakMap,t=null;function n(c){if(c&&c.isTexture){const u=c.mapping,h=u===Eh||u===Ah,f=u===$s||u===Js;if(h||f){let p=e.get(c);const m=p!==void 0?p.texture.pmremVersion:0;if(c.isRenderTargetTexture&&c.pmremVersion!==m)return t===null&&(t=new im(r)),p=h?t.fromEquirectangular(c,p):t.fromCubemap(c,p),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),p.texture;if(p!==void 0)return p.texture;{const g=c.image;return h&&g&&g.height>0||f&&g&&i(g)?(t===null&&(t=new im(r)),p=h?t.fromEquirectangular(c):t.fromCubemap(c),p.texture.pmremVersion=c.pmremVersion,e.set(c,p),c.addEventListener("dispose",s),p.texture):null}}}return c}function i(c){let u=0;const h=6;for(let f=0;f<h;f++)c[f]!==void 0&&u++;return u===h}function s(c){const u=c.target;u.removeEventListener("dispose",s);const h=e.get(u);h!==void 0&&(e.delete(u),h.dispose())}function a(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:a}}function C1(r){const e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=r.getExtension("WEBGL_depth_texture")||r.getExtension("MOZ_WEBGL_depth_texture")||r.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=r.getExtension("EXT_texture_filter_anisotropic")||r.getExtension("MOZ_EXT_texture_filter_anisotropic")||r.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=r.getExtension("WEBGL_compressed_texture_s3tc")||r.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=r.getExtension("WEBGL_compressed_texture_pvrtc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=r.getExtension(n)}return e[n]=i,i}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const i=t(n);return i===null&&Wo("THREE.WebGLRenderer: "+n+" extension not supported."),i}}}function I1(r,e,t,n){const i={},s=new WeakMap;function a(p){const m=p.target;m.index!==null&&e.remove(m.index);for(const x in m.attributes)e.remove(m.attributes[x]);for(const x in m.morphAttributes){const M=m.morphAttributes[x];for(let v=0,_=M.length;v<_;v++)e.remove(M[v])}m.removeEventListener("dispose",a),delete i[m.id];const g=s.get(m);g&&(e.remove(g),s.delete(m)),n.releaseStatesOfGeometry(m),m.isInstancedBufferGeometry===!0&&delete m._maxInstanceCount,t.memory.geometries--}function c(p,m){return i[m.id]===!0||(m.addEventListener("dispose",a),i[m.id]=!0,t.memory.geometries++),m}function u(p){const m=p.attributes;for(const x in m)e.update(m[x],r.ARRAY_BUFFER);const g=p.morphAttributes;for(const x in g){const M=g[x];for(let v=0,_=M.length;v<_;v++)e.update(M[v],r.ARRAY_BUFFER)}}function h(p){const m=[],g=p.index,x=p.attributes.position;let M=0;if(g!==null){const A=g.array;M=g.version;for(let P=0,b=A.length;P<b;P+=3){const B=A[P+0],U=A[P+1],O=A[P+2];m.push(B,U,U,O,O,B)}}else if(x!==void 0){const A=x.array;M=x.version;for(let P=0,b=A.length/3-1;P<b;P+=3){const B=P+0,U=P+1,O=P+2;m.push(B,U,U,O,O,B)}}else return;const v=new(Pg(m)?Dg:Lg)(m,1);v.version=M;const _=s.get(p);_&&e.remove(_),s.set(p,v)}function f(p){const m=s.get(p);if(m){const g=p.index;g!==null&&m.version<g.version&&h(p)}else h(p);return s.get(p)}return{get:c,update:u,getWireframeAttribute:f}}function L1(r,e,t){let n;function i(m){n=m}let s,a;function c(m){s=m.type,a=m.bytesPerElement}function u(m,g){r.drawElements(n,g,s,m*a),t.update(g,n,1)}function h(m,g,x){x!==0&&(r.drawElementsInstanced(n,g,s,m*a,x),t.update(g,n,x))}function f(m,g,x){if(x===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,g,0,s,m,0,x);let v=0;for(let _=0;_<x;_++)v+=g[_];t.update(v,n,1)}function p(m,g,x,M){if(x===0)return;const v=e.get("WEBGL_multi_draw");if(v===null)for(let _=0;_<m.length;_++)h(m[_]/a,g[_],M[_]);else{v.multiDrawElementsInstancedWEBGL(n,g,0,s,m,0,M,0,x);let _=0;for(let A=0;A<x;A++)_+=g[A]*M[A];t.update(_,n,1)}}this.setMode=i,this.setIndex=c,this.render=u,this.renderInstances=h,this.renderMultiDraw=f,this.renderMultiDrawInstances=p}function D1(r){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,a,c){switch(t.calls++,a){case r.TRIANGLES:t.triangles+=c*(s/3);break;case r.LINES:t.lines+=c*(s/2);break;case r.LINE_STRIP:t.lines+=c*(s-1);break;case r.LINE_LOOP:t.lines+=c*s;break;case r.POINTS:t.points+=c*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",a);break}}function i(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}function N1(r,e,t){const n=new WeakMap,i=new Pt;function s(a,c,u){const h=a.morphTargetInfluences,f=c.morphAttributes.position||c.morphAttributes.normal||c.morphAttributes.color,p=f!==void 0?f.length:0;let m=n.get(c);if(m===void 0||m.count!==p){let w=function(){z.dispose(),n.delete(c),c.removeEventListener("dispose",w)};var g=w;m!==void 0&&m.texture.dispose();const x=c.morphAttributes.position!==void 0,M=c.morphAttributes.normal!==void 0,v=c.morphAttributes.color!==void 0,_=c.morphAttributes.position||[],A=c.morphAttributes.normal||[],P=c.morphAttributes.color||[];let b=0;x===!0&&(b=1),M===!0&&(b=2),v===!0&&(b=3);let B=c.attributes.position.count*b,U=1;B>e.maxTextureSize&&(U=Math.ceil(B/e.maxTextureSize),B=e.maxTextureSize);const O=new Float32Array(B*U*4*p),z=new Cg(O,B,U,p);z.type=gi,z.needsUpdate=!0;const I=b*4;for(let H=0;H<p;H++){const ee=_[H],Q=A[H],ae=P[H],ce=B*U*4*H;for(let $=0;$<ee.count;$++){const fe=$*I;x===!0&&(i.fromBufferAttribute(ee,$),O[ce+fe+0]=i.x,O[ce+fe+1]=i.y,O[ce+fe+2]=i.z,O[ce+fe+3]=0),M===!0&&(i.fromBufferAttribute(Q,$),O[ce+fe+4]=i.x,O[ce+fe+5]=i.y,O[ce+fe+6]=i.z,O[ce+fe+7]=0),v===!0&&(i.fromBufferAttribute(ae,$),O[ce+fe+8]=i.x,O[ce+fe+9]=i.y,O[ce+fe+10]=i.z,O[ce+fe+11]=ae.itemSize===4?i.w:1)}}m={count:p,texture:z,size:new Qe(B,U)},n.set(c,m),c.addEventListener("dispose",w)}if(a.isInstancedMesh===!0&&a.morphTexture!==null)u.getUniforms().setValue(r,"morphTexture",a.morphTexture,t);else{let x=0;for(let v=0;v<h.length;v++)x+=h[v];const M=c.morphTargetsRelative?1:1-x;u.getUniforms().setValue(r,"morphTargetBaseInfluence",M),u.getUniforms().setValue(r,"morphTargetInfluences",h)}u.getUniforms().setValue(r,"morphTargetsTexture",m.texture,t),u.getUniforms().setValue(r,"morphTargetsTextureSize",m.size)}return{update:s}}function O1(r,e,t,n){let i=new WeakMap;function s(u){const h=n.render.frame,f=u.geometry,p=e.get(u,f);if(i.get(p)!==h&&(e.update(p),i.set(p,h)),u.isInstancedMesh&&(u.hasEventListener("dispose",c)===!1&&u.addEventListener("dispose",c),i.get(u)!==h&&(t.update(u.instanceMatrix,r.ARRAY_BUFFER),u.instanceColor!==null&&t.update(u.instanceColor,r.ARRAY_BUFFER),i.set(u,h))),u.isSkinnedMesh){const m=u.skeleton;i.get(m)!==h&&(m.update(),i.set(m,h))}return p}function a(){i=new WeakMap}function c(u){const h=u.target;h.removeEventListener("dispose",c),t.remove(h.instanceMatrix),h.instanceColor!==null&&t.remove(h.instanceColor)}return{update:s,dispose:a}}class Bg extends vn{constructor(e,t,n,i,s,a,c,u,h,f=qs){if(f!==qs&&f!==to)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&f===qs&&(n=rs),n===void 0&&f===to&&(n=eo),super(null,i,s,a,c,u,f,n,h),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=c!==void 0?c:Un,this.minFilter=u!==void 0?u:Un,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const kg=new vn,am=new Bg(1,1),zg=new Cg,Hg=new bE,Vg=new Ug,cm=[],lm=[],um=new Float32Array(16),hm=new Float32Array(9),dm=new Float32Array(4);function co(r,e,t){const n=r[0];if(n<=0||n>0)return r;const i=e*t;let s=cm[i];if(s===void 0&&(s=new Float32Array(i),cm[i]=s),e!==0){n.toArray(s,0);for(let a=1,c=0;a!==e;++a)c+=t,r[a].toArray(s,c)}return s}function dn(r,e){if(r.length!==e.length)return!1;for(let t=0,n=r.length;t<n;t++)if(r[t]!==e[t])return!1;return!0}function fn(r,e){for(let t=0,n=e.length;t<n;t++)r[t]=e[t]}function Hc(r,e){let t=lm[e];t===void 0&&(t=new Int32Array(e),lm[e]=t);for(let n=0;n!==e;++n)t[n]=r.allocateTextureUnit();return t}function U1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1f(this.addr,e),t[0]=e)}function F1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(dn(t,e))return;r.uniform2fv(this.addr,e),fn(t,e)}}function B1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(r.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(dn(t,e))return;r.uniform3fv(this.addr,e),fn(t,e)}}function k1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(dn(t,e))return;r.uniform4fv(this.addr,e),fn(t,e)}}function z1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(dn(t,e))return;r.uniformMatrix2fv(this.addr,!1,e),fn(t,e)}else{if(dn(t,n))return;dm.set(n),r.uniformMatrix2fv(this.addr,!1,dm),fn(t,n)}}function H1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(dn(t,e))return;r.uniformMatrix3fv(this.addr,!1,e),fn(t,e)}else{if(dn(t,n))return;hm.set(n),r.uniformMatrix3fv(this.addr,!1,hm),fn(t,n)}}function V1(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(dn(t,e))return;r.uniformMatrix4fv(this.addr,!1,e),fn(t,e)}else{if(dn(t,n))return;um.set(n),r.uniformMatrix4fv(this.addr,!1,um),fn(t,n)}}function G1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1i(this.addr,e),t[0]=e)}function W1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(dn(t,e))return;r.uniform2iv(this.addr,e),fn(t,e)}}function j1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(dn(t,e))return;r.uniform3iv(this.addr,e),fn(t,e)}}function X1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(dn(t,e))return;r.uniform4iv(this.addr,e),fn(t,e)}}function q1(r,e){const t=this.cache;t[0]!==e&&(r.uniform1ui(this.addr,e),t[0]=e)}function Y1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(dn(t,e))return;r.uniform2uiv(this.addr,e),fn(t,e)}}function K1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(dn(t,e))return;r.uniform3uiv(this.addr,e),fn(t,e)}}function Z1(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(dn(t,e))return;r.uniform4uiv(this.addr,e),fn(t,e)}}function $1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i);let s;this.type===r.SAMPLER_2D_SHADOW?(am.compareFunction=Ag,s=am):s=kg,t.setTexture2D(e||s,i)}function J1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||Hg,i)}function Q1(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||Vg,i)}function eP(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||zg,i)}function tP(r){switch(r){case 5126:return U1;case 35664:return F1;case 35665:return B1;case 35666:return k1;case 35674:return z1;case 35675:return H1;case 35676:return V1;case 5124:case 35670:return G1;case 35667:case 35671:return W1;case 35668:case 35672:return j1;case 35669:case 35673:return X1;case 5125:return q1;case 36294:return Y1;case 36295:return K1;case 36296:return Z1;case 35678:case 36198:case 36298:case 36306:case 35682:return $1;case 35679:case 36299:case 36307:return J1;case 35680:case 36300:case 36308:case 36293:return Q1;case 36289:case 36303:case 36311:case 36292:return eP}}function nP(r,e){r.uniform1fv(this.addr,e)}function iP(r,e){const t=co(e,this.size,2);r.uniform2fv(this.addr,t)}function rP(r,e){const t=co(e,this.size,3);r.uniform3fv(this.addr,t)}function sP(r,e){const t=co(e,this.size,4);r.uniform4fv(this.addr,t)}function oP(r,e){const t=co(e,this.size,4);r.uniformMatrix2fv(this.addr,!1,t)}function aP(r,e){const t=co(e,this.size,9);r.uniformMatrix3fv(this.addr,!1,t)}function cP(r,e){const t=co(e,this.size,16);r.uniformMatrix4fv(this.addr,!1,t)}function lP(r,e){r.uniform1iv(this.addr,e)}function uP(r,e){r.uniform2iv(this.addr,e)}function hP(r,e){r.uniform3iv(this.addr,e)}function dP(r,e){r.uniform4iv(this.addr,e)}function fP(r,e){r.uniform1uiv(this.addr,e)}function pP(r,e){r.uniform2uiv(this.addr,e)}function mP(r,e){r.uniform3uiv(this.addr,e)}function gP(r,e){r.uniform4uiv(this.addr,e)}function _P(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);dn(n,s)||(r.uniform1iv(this.addr,s),fn(n,s));for(let a=0;a!==i;++a)t.setTexture2D(e[a]||kg,s[a])}function vP(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);dn(n,s)||(r.uniform1iv(this.addr,s),fn(n,s));for(let a=0;a!==i;++a)t.setTexture3D(e[a]||Hg,s[a])}function yP(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);dn(n,s)||(r.uniform1iv(this.addr,s),fn(n,s));for(let a=0;a!==i;++a)t.setTextureCube(e[a]||Vg,s[a])}function xP(r,e,t){const n=this.cache,i=e.length,s=Hc(t,i);dn(n,s)||(r.uniform1iv(this.addr,s),fn(n,s));for(let a=0;a!==i;++a)t.setTexture2DArray(e[a]||zg,s[a])}function bP(r){switch(r){case 5126:return nP;case 35664:return iP;case 35665:return rP;case 35666:return sP;case 35674:return oP;case 35675:return aP;case 35676:return cP;case 5124:case 35670:return lP;case 35667:case 35671:return uP;case 35668:case 35672:return hP;case 35669:case 35673:return dP;case 5125:return fP;case 36294:return pP;case 36295:return mP;case 36296:return gP;case 35678:case 36198:case 36298:case 36306:case 35682:return _P;case 35679:case 36299:case 36307:return vP;case 35680:case 36300:case 36308:case 36293:return yP;case 36289:case 36303:case 36311:case 36292:return xP}}class SP{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=tP(t.type)}}class MP{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=bP(t.type)}}class TP{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const i=this.seq;for(let s=0,a=i.length;s!==a;++s){const c=i[s];c.setValue(e,t[c.id],n)}}}const Ku=/(\w+)(\])?(\[|\.)?/g;function fm(r,e){r.seq.push(e),r.map[e.id]=e}function EP(r,e,t){const n=r.name,i=n.length;for(Ku.lastIndex=0;;){const s=Ku.exec(n),a=Ku.lastIndex;let c=s[1];const u=s[2]==="]",h=s[3];if(u&&(c=c|0),h===void 0||h==="["&&a+2===i){fm(t,h===void 0?new SP(c,r,e):new MP(c,r,e));break}else{let p=t.map[c];p===void 0&&(p=new TP(c),fm(t,p)),t=p}}}class Rc{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let i=0;i<n;++i){const s=e.getActiveUniform(t,i),a=e.getUniformLocation(t,s.name);EP(s,a,this)}}setValue(e,t,n,i){const s=this.map[t];s!==void 0&&s.setValue(e,n,i)}setOptional(e,t,n){const i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let s=0,a=t.length;s!==a;++s){const c=t[s],u=n[c.id];u.needsUpdate!==!1&&c.setValue(e,u.value,i)}}static seqWithValue(e,t){const n=[];for(let i=0,s=e.length;i!==s;++i){const a=e[i];a.id in t&&n.push(a)}return n}}function pm(r,e,t){const n=r.createShader(e);return r.shaderSource(n,t),r.compileShader(n),n}const AP=37297;let wP=0;function PP(r,e){const t=r.split(`
`),n=[],i=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let a=i;a<s;a++){const c=a+1;n.push(`${c===e?">":" "} ${c}: ${t[a]}`)}return n.join(`
`)}const mm=new ft;function RP(r){Mt._getMatrix(mm,Mt.workingColorSpace,r);const e=`mat3( ${mm.elements.map(t=>t.toFixed(4))} )`;switch(Mt.getTransfer(r)){case zc:return[e,"LinearTransferOETF"];case Ut:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",r),[e,"LinearTransferOETF"]}}function gm(r,e,t){const n=r.getShaderParameter(e,r.COMPILE_STATUS),i=r.getShaderInfoLog(e).trim();if(n&&i==="")return"";const s=/ERROR: 0:(\d+)/.exec(i);if(s){const a=parseInt(s[1]);return t.toUpperCase()+`

`+i+`

`+PP(r.getShaderSource(e),a)}else return i}function CP(r,e){const t=RP(e);return[`vec4 ${r}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function IP(r,e){let t;switch(e){case CT:t="Linear";break;case IT:t="Reinhard";break;case LT:t="Cineon";break;case dg:t="ACESFilmic";break;case NT:t="AgX";break;case OT:t="Neutral";break;case DT:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+r+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const lc=new F;function LP(){Mt.getLuminanceCoefficients(lc);const r=lc.x.toFixed(4),e=lc.y.toFixed(4),t=lc.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${r}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function DP(r){return[r.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",r.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(jo).join(`
`)}function NP(r){const e=[];for(const t in r){const n=r[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function OP(r,e){const t={},n=r.getProgramParameter(e,r.ACTIVE_ATTRIBUTES);for(let i=0;i<n;i++){const s=r.getActiveAttrib(e,i),a=s.name;let c=1;s.type===r.FLOAT_MAT2&&(c=2),s.type===r.FLOAT_MAT3&&(c=3),s.type===r.FLOAT_MAT4&&(c=4),t[a]={type:s.type,location:r.getAttribLocation(e,a),locationSize:c}}return t}function jo(r){return r!==""}function _m(r,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return r.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function vm(r,e){return r.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const UP=/^[ \t]*#include +<([\w\d./]+)>/gm;function td(r){return r.replace(UP,BP)}const FP=new Map;function BP(r,e){let t=mt[e];if(t===void 0){const n=FP.get(e);if(n!==void 0)t=mt[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return td(t)}const kP=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function ym(r){return r.replace(kP,zP)}function zP(r,e,t,n){let i="";for(let s=parseInt(e);s<parseInt(t);s++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return i}function xm(r){let e=`precision ${r.precision} float;
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
#define LOW_PRECISION`),e}function HP(r){let e="SHADOWMAP_TYPE_BASIC";return r.shadowMapType===ug?e="SHADOWMAP_TYPE_PCF":r.shadowMapType===lT?e="SHADOWMAP_TYPE_PCF_SOFT":r.shadowMapType===Wi&&(e="SHADOWMAP_TYPE_VSM"),e}function VP(r){let e="ENVMAP_TYPE_CUBE";if(r.envMap)switch(r.envMapMode){case $s:case Js:e="ENVMAP_TYPE_CUBE";break;case kc:e="ENVMAP_TYPE_CUBE_UV";break}return e}function GP(r){let e="ENVMAP_MODE_REFLECTION";if(r.envMap)switch(r.envMapMode){case Js:e="ENVMAP_MODE_REFRACTION";break}return e}function WP(r){let e="ENVMAP_BLENDING_NONE";if(r.envMap)switch(r.combine){case hg:e="ENVMAP_BLENDING_MULTIPLY";break;case PT:e="ENVMAP_BLENDING_MIX";break;case RT:e="ENVMAP_BLENDING_ADD";break}return e}function jP(r){const e=r.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function XP(r,e,t,n){const i=r.getContext(),s=t.defines;let a=t.vertexShader,c=t.fragmentShader;const u=HP(t),h=VP(t),f=GP(t),p=WP(t),m=jP(t),g=DP(t),x=NP(s),M=i.createProgram();let v,_,A=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(v=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(jo).join(`
`),v.length>0&&(v+=`
`),_=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x].filter(jo).join(`
`),_.length>0&&(_+=`
`)):(v=[xm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+f:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(jo).join(`
`),_=[xm(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,x,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.envMap?"#define "+f:"",t.envMap?"#define "+p:"",m?"#define CUBEUV_TEXEL_WIDTH "+m.texelWidth:"",m?"#define CUBEUV_TEXEL_HEIGHT "+m.texelHeight:"",m?"#define CUBEUV_MAX_MIP "+m.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+u:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==xr?"#define TONE_MAPPING":"",t.toneMapping!==xr?mt.tonemapping_pars_fragment:"",t.toneMapping!==xr?IP("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",mt.colorspace_pars_fragment,CP("linearToOutputTexel",t.outputColorSpace),LP(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(jo).join(`
`)),a=td(a),a=_m(a,t),a=vm(a,t),c=td(c),c=_m(c,t),c=vm(c,t),a=ym(a),c=ym(c),t.isRawShaderMaterial!==!0&&(A=`#version 300 es
`,v=[g,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+v,_=["#define varying in",t.glslVersion===Lp?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Lp?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+_);const P=A+v+a,b=A+_+c,B=pm(i,i.VERTEX_SHADER,P),U=pm(i,i.FRAGMENT_SHADER,b);i.attachShader(M,B),i.attachShader(M,U),t.index0AttributeName!==void 0?i.bindAttribLocation(M,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(M,0,"position"),i.linkProgram(M);function O(H){if(r.debug.checkShaderErrors){const ee=i.getProgramInfoLog(M).trim(),Q=i.getShaderInfoLog(B).trim(),ae=i.getShaderInfoLog(U).trim();let ce=!0,$=!0;if(i.getProgramParameter(M,i.LINK_STATUS)===!1)if(ce=!1,typeof r.debug.onShaderError=="function")r.debug.onShaderError(i,M,B,U);else{const fe=gm(i,B,"vertex"),re=gm(i,U,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(M,i.VALIDATE_STATUS)+`

Material Name: `+H.name+`
Material Type: `+H.type+`

Program Info Log: `+ee+`
`+fe+`
`+re)}else ee!==""?console.warn("THREE.WebGLProgram: Program Info Log:",ee):(Q===""||ae==="")&&($=!1);$&&(H.diagnostics={runnable:ce,programLog:ee,vertexShader:{log:Q,prefix:v},fragmentShader:{log:ae,prefix:_}})}i.deleteShader(B),i.deleteShader(U),z=new Rc(i,M),I=OP(i,M)}let z;this.getUniforms=function(){return z===void 0&&O(this),z};let I;this.getAttributes=function(){return I===void 0&&O(this),I};let w=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return w===!1&&(w=i.getProgramParameter(M,AP)),w},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(M),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=wP++,this.cacheKey=e,this.usedTimes=1,this.program=M,this.vertexShader=B,this.fragmentShader=U,this}let qP=0;class YP{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),s=this._getShaderStage(n),a=this._getShaderCacheForMaterial(e);return a.has(i)===!1&&(a.add(i),i.usedTimes++),a.has(s)===!1&&(a.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new KP(e),t.set(e,n)),n}}class KP{constructor(e){this.id=qP++,this.code=e,this.usedTimes=0}}function ZP(r,e,t,n,i,s,a){const c=new yd,u=new YP,h=new Set,f=[],p=i.logarithmicDepthBuffer,m=i.vertexTextures;let g=i.precision;const x={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function M(I){return h.add(I),I===0?"uv":`uv${I}`}function v(I,w,H,ee,Q){const ae=ee.fog,ce=Q.geometry,$=I.isMeshStandardMaterial?ee.environment:null,fe=(I.isMeshStandardMaterial?t:e).get(I.envMap||$),re=fe&&fe.mapping===kc?fe.image.height:null,ye=x[I.type];I.precision!==null&&(g=i.getMaxPrecision(I.precision),g!==I.precision&&console.warn("THREE.WebGLProgram.getParameters:",I.precision,"not supported, using",g,"instead."));const Me=ce.morphAttributes.position||ce.morphAttributes.normal||ce.morphAttributes.color,Ne=Me!==void 0?Me.length:0;let Ze=0;ce.morphAttributes.position!==void 0&&(Ze=1),ce.morphAttributes.normal!==void 0&&(Ze=2),ce.morphAttributes.color!==void 0&&(Ze=3);let ht,le,ge,Oe;if(ye){const et=Si[ye];ht=et.vertexShader,le=et.fragmentShader}else ht=I.vertexShader,le=I.fragmentShader,u.update(I),ge=u.getVertexShaderID(I),Oe=u.getFragmentShaderID(I);const Se=r.getRenderTarget(),We=r.state.buffers.depth.getReversed(),tt=Q.isInstancedMesh===!0,st=Q.isBatchedMesh===!0,Tt=!!I.map,ot=!!I.matcap,Ot=!!fe,X=!!I.aoMap,Qt=!!I.lightMap,at=!!I.bumpMap,dt=!!I.normalMap,Ve=!!I.displacementMap,xt=!!I.emissiveMap,Fe=!!I.metalnessMap,N=!!I.roughnessMap,E=I.anisotropy>0,Z=I.clearcoat>0,ue=I.dispersion>0,pe=I.iridescence>0,de=I.sheen>0,De=I.transmission>0,Ee=E&&!!I.anisotropyMap,Re=Z&&!!I.clearcoatMap,ct=Z&&!!I.clearcoatNormalMap,_e=Z&&!!I.clearcoatRoughnessMap,Ce=pe&&!!I.iridescenceMap,Ue=pe&&!!I.iridescenceThicknessMap,Ye=de&&!!I.sheenColorMap,Ie=de&&!!I.sheenRoughnessMap,pt=!!I.specularMap,it=!!I.specularColorMap,V=!!I.specularIntensityMap,L=De&&!!I.transmissionMap,J=De&&!!I.thicknessMap,W=!!I.gradientMap,ie=!!I.alphaMap,he=I.alphaTest>0,me=!!I.alphaHash,Le=!!I.extensions;let Ke=xr;I.toneMapped&&(Se===null||Se.isXRRenderTarget===!0)&&(Ke=r.toneMapping);const bt={shaderID:ye,shaderType:I.type,shaderName:I.name,vertexShader:ht,fragmentShader:le,defines:I.defines,customVertexShaderID:ge,customFragmentShaderID:Oe,isRawShaderMaterial:I.isRawShaderMaterial===!0,glslVersion:I.glslVersion,precision:g,batching:st,batchingColor:st&&Q._colorsTexture!==null,instancing:tt,instancingColor:tt&&Q.instanceColor!==null,instancingMorph:tt&&Q.morphTexture!==null,supportsVertexTextures:m,outputColorSpace:Se===null?r.outputColorSpace:Se.isXRRenderTarget===!0?Se.texture.colorSpace:Fn,alphaToCoverage:!!I.alphaToCoverage,map:Tt,matcap:ot,envMap:Ot,envMapMode:Ot&&fe.mapping,envMapCubeUVHeight:re,aoMap:X,lightMap:Qt,bumpMap:at,normalMap:dt,displacementMap:m&&Ve,emissiveMap:xt,normalMapObjectSpace:dt&&I.normalMapType===GT,normalMapTangentSpace:dt&&I.normalMapType===Eg,metalnessMap:Fe,roughnessMap:N,anisotropy:E,anisotropyMap:Ee,clearcoat:Z,clearcoatMap:Re,clearcoatNormalMap:ct,clearcoatRoughnessMap:_e,dispersion:ue,iridescence:pe,iridescenceMap:Ce,iridescenceThicknessMap:Ue,sheen:de,sheenColorMap:Ye,sheenRoughnessMap:Ie,specularMap:pt,specularColorMap:it,specularIntensityMap:V,transmission:De,transmissionMap:L,thicknessMap:J,gradientMap:W,opaque:I.transparent===!1&&I.blending===Xs&&I.alphaToCoverage===!1,alphaMap:ie,alphaTest:he,alphaHash:me,combine:I.combine,mapUv:Tt&&M(I.map.channel),aoMapUv:X&&M(I.aoMap.channel),lightMapUv:Qt&&M(I.lightMap.channel),bumpMapUv:at&&M(I.bumpMap.channel),normalMapUv:dt&&M(I.normalMap.channel),displacementMapUv:Ve&&M(I.displacementMap.channel),emissiveMapUv:xt&&M(I.emissiveMap.channel),metalnessMapUv:Fe&&M(I.metalnessMap.channel),roughnessMapUv:N&&M(I.roughnessMap.channel),anisotropyMapUv:Ee&&M(I.anisotropyMap.channel),clearcoatMapUv:Re&&M(I.clearcoatMap.channel),clearcoatNormalMapUv:ct&&M(I.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:_e&&M(I.clearcoatRoughnessMap.channel),iridescenceMapUv:Ce&&M(I.iridescenceMap.channel),iridescenceThicknessMapUv:Ue&&M(I.iridescenceThicknessMap.channel),sheenColorMapUv:Ye&&M(I.sheenColorMap.channel),sheenRoughnessMapUv:Ie&&M(I.sheenRoughnessMap.channel),specularMapUv:pt&&M(I.specularMap.channel),specularColorMapUv:it&&M(I.specularColorMap.channel),specularIntensityMapUv:V&&M(I.specularIntensityMap.channel),transmissionMapUv:L&&M(I.transmissionMap.channel),thicknessMapUv:J&&M(I.thicknessMap.channel),alphaMapUv:ie&&M(I.alphaMap.channel),vertexTangents:!!ce.attributes.tangent&&(dt||E),vertexColors:I.vertexColors,vertexAlphas:I.vertexColors===!0&&!!ce.attributes.color&&ce.attributes.color.itemSize===4,pointsUvs:Q.isPoints===!0&&!!ce.attributes.uv&&(Tt||ie),fog:!!ae,useFog:I.fog===!0,fogExp2:!!ae&&ae.isFogExp2,flatShading:I.flatShading===!0,sizeAttenuation:I.sizeAttenuation===!0,logarithmicDepthBuffer:p,reverseDepthBuffer:We,skinning:Q.isSkinnedMesh===!0,morphTargets:ce.morphAttributes.position!==void 0,morphNormals:ce.morphAttributes.normal!==void 0,morphColors:ce.morphAttributes.color!==void 0,morphTargetsCount:Ne,morphTextureStride:Ze,numDirLights:w.directional.length,numPointLights:w.point.length,numSpotLights:w.spot.length,numSpotLightMaps:w.spotLightMap.length,numRectAreaLights:w.rectArea.length,numHemiLights:w.hemi.length,numDirLightShadows:w.directionalShadowMap.length,numPointLightShadows:w.pointShadowMap.length,numSpotLightShadows:w.spotShadowMap.length,numSpotLightShadowsWithMaps:w.numSpotLightShadowsWithMaps,numLightProbes:w.numLightProbes,numClippingPlanes:a.numPlanes,numClipIntersection:a.numIntersection,dithering:I.dithering,shadowMapEnabled:r.shadowMap.enabled&&H.length>0,shadowMapType:r.shadowMap.type,toneMapping:Ke,decodeVideoTexture:Tt&&I.map.isVideoTexture===!0&&Mt.getTransfer(I.map.colorSpace)===Ut,decodeVideoTextureEmissive:xt&&I.emissiveMap.isVideoTexture===!0&&Mt.getTransfer(I.emissiveMap.colorSpace)===Ut,premultipliedAlpha:I.premultipliedAlpha,doubleSided:I.side===Gn,flipSided:I.side===Wn,useDepthPacking:I.depthPacking>=0,depthPacking:I.depthPacking||0,index0AttributeName:I.index0AttributeName,extensionClipCullDistance:Le&&I.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(Le&&I.extensions.multiDraw===!0||st)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:I.customProgramCacheKey()};return bt.vertexUv1s=h.has(1),bt.vertexUv2s=h.has(2),bt.vertexUv3s=h.has(3),h.clear(),bt}function _(I){const w=[];if(I.shaderID?w.push(I.shaderID):(w.push(I.customVertexShaderID),w.push(I.customFragmentShaderID)),I.defines!==void 0)for(const H in I.defines)w.push(H),w.push(I.defines[H]);return I.isRawShaderMaterial===!1&&(A(w,I),P(w,I),w.push(r.outputColorSpace)),w.push(I.customProgramCacheKey),w.join()}function A(I,w){I.push(w.precision),I.push(w.outputColorSpace),I.push(w.envMapMode),I.push(w.envMapCubeUVHeight),I.push(w.mapUv),I.push(w.alphaMapUv),I.push(w.lightMapUv),I.push(w.aoMapUv),I.push(w.bumpMapUv),I.push(w.normalMapUv),I.push(w.displacementMapUv),I.push(w.emissiveMapUv),I.push(w.metalnessMapUv),I.push(w.roughnessMapUv),I.push(w.anisotropyMapUv),I.push(w.clearcoatMapUv),I.push(w.clearcoatNormalMapUv),I.push(w.clearcoatRoughnessMapUv),I.push(w.iridescenceMapUv),I.push(w.iridescenceThicknessMapUv),I.push(w.sheenColorMapUv),I.push(w.sheenRoughnessMapUv),I.push(w.specularMapUv),I.push(w.specularColorMapUv),I.push(w.specularIntensityMapUv),I.push(w.transmissionMapUv),I.push(w.thicknessMapUv),I.push(w.combine),I.push(w.fogExp2),I.push(w.sizeAttenuation),I.push(w.morphTargetsCount),I.push(w.morphAttributeCount),I.push(w.numDirLights),I.push(w.numPointLights),I.push(w.numSpotLights),I.push(w.numSpotLightMaps),I.push(w.numHemiLights),I.push(w.numRectAreaLights),I.push(w.numDirLightShadows),I.push(w.numPointLightShadows),I.push(w.numSpotLightShadows),I.push(w.numSpotLightShadowsWithMaps),I.push(w.numLightProbes),I.push(w.shadowMapType),I.push(w.toneMapping),I.push(w.numClippingPlanes),I.push(w.numClipIntersection),I.push(w.depthPacking)}function P(I,w){c.disableAll(),w.supportsVertexTextures&&c.enable(0),w.instancing&&c.enable(1),w.instancingColor&&c.enable(2),w.instancingMorph&&c.enable(3),w.matcap&&c.enable(4),w.envMap&&c.enable(5),w.normalMapObjectSpace&&c.enable(6),w.normalMapTangentSpace&&c.enable(7),w.clearcoat&&c.enable(8),w.iridescence&&c.enable(9),w.alphaTest&&c.enable(10),w.vertexColors&&c.enable(11),w.vertexAlphas&&c.enable(12),w.vertexUv1s&&c.enable(13),w.vertexUv2s&&c.enable(14),w.vertexUv3s&&c.enable(15),w.vertexTangents&&c.enable(16),w.anisotropy&&c.enable(17),w.alphaHash&&c.enable(18),w.batching&&c.enable(19),w.dispersion&&c.enable(20),w.batchingColor&&c.enable(21),I.push(c.mask),c.disableAll(),w.fog&&c.enable(0),w.useFog&&c.enable(1),w.flatShading&&c.enable(2),w.logarithmicDepthBuffer&&c.enable(3),w.reverseDepthBuffer&&c.enable(4),w.skinning&&c.enable(5),w.morphTargets&&c.enable(6),w.morphNormals&&c.enable(7),w.morphColors&&c.enable(8),w.premultipliedAlpha&&c.enable(9),w.shadowMapEnabled&&c.enable(10),w.doubleSided&&c.enable(11),w.flipSided&&c.enable(12),w.useDepthPacking&&c.enable(13),w.dithering&&c.enable(14),w.transmission&&c.enable(15),w.sheen&&c.enable(16),w.opaque&&c.enable(17),w.pointsUvs&&c.enable(18),w.decodeVideoTexture&&c.enable(19),w.decodeVideoTextureEmissive&&c.enable(20),w.alphaToCoverage&&c.enable(21),I.push(c.mask)}function b(I){const w=x[I.type];let H;if(w){const ee=Si[w];H=DE.clone(ee.uniforms)}else H=I.uniforms;return H}function B(I,w){let H;for(let ee=0,Q=f.length;ee<Q;ee++){const ae=f[ee];if(ae.cacheKey===w){H=ae,++H.usedTimes;break}}return H===void 0&&(H=new XP(r,w,I,s),f.push(H)),H}function U(I){if(--I.usedTimes===0){const w=f.indexOf(I);f[w]=f[f.length-1],f.pop(),I.destroy()}}function O(I){u.remove(I)}function z(){u.dispose()}return{getParameters:v,getProgramCacheKey:_,getUniforms:b,acquireProgram:B,releaseProgram:U,releaseShaderCache:O,programs:f,dispose:z}}function $P(){let r=new WeakMap;function e(a){return r.has(a)}function t(a){let c=r.get(a);return c===void 0&&(c={},r.set(a,c)),c}function n(a){r.delete(a)}function i(a,c,u){r.get(a)[c]=u}function s(){r=new WeakMap}return{has:e,get:t,remove:n,update:i,dispose:s}}function JP(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.material.id!==e.material.id?r.material.id-e.material.id:r.z!==e.z?r.z-e.z:r.id-e.id}function bm(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.z!==e.z?e.z-r.z:r.id-e.id}function Sm(){const r=[];let e=0;const t=[],n=[],i=[];function s(){e=0,t.length=0,n.length=0,i.length=0}function a(p,m,g,x,M,v){let _=r[e];return _===void 0?(_={id:p.id,object:p,geometry:m,material:g,groupOrder:x,renderOrder:p.renderOrder,z:M,group:v},r[e]=_):(_.id=p.id,_.object=p,_.geometry=m,_.material=g,_.groupOrder=x,_.renderOrder=p.renderOrder,_.z=M,_.group=v),e++,_}function c(p,m,g,x,M,v){const _=a(p,m,g,x,M,v);g.transmission>0?n.push(_):g.transparent===!0?i.push(_):t.push(_)}function u(p,m,g,x,M,v){const _=a(p,m,g,x,M,v);g.transmission>0?n.unshift(_):g.transparent===!0?i.unshift(_):t.unshift(_)}function h(p,m){t.length>1&&t.sort(p||JP),n.length>1&&n.sort(m||bm),i.length>1&&i.sort(m||bm)}function f(){for(let p=e,m=r.length;p<m;p++){const g=r[p];if(g.id===null)break;g.id=null,g.object=null,g.geometry=null,g.material=null,g.group=null}}return{opaque:t,transmissive:n,transparent:i,init:s,push:c,unshift:u,finish:f,sort:h}}function QP(){let r=new WeakMap;function e(n,i){const s=r.get(n);let a;return s===void 0?(a=new Sm,r.set(n,[a])):i>=s.length?(a=new Sm,s.push(a)):a=s[i],a}function t(){r=new WeakMap}return{get:e,dispose:t}}function eR(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new F,color:new qe};break;case"SpotLight":t={position:new F,direction:new F,color:new qe,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new F,color:new qe,distance:0,decay:0};break;case"HemisphereLight":t={direction:new F,skyColor:new qe,groundColor:new qe};break;case"RectAreaLight":t={color:new qe,position:new F,halfWidth:new F,halfHeight:new F};break}return r[e.id]=t,t}}}function tR(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qe};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qe};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new Qe,shadowCameraNear:1,shadowCameraFar:1e3};break}return r[e.id]=t,t}}}let nR=0;function iR(r,e){return(e.castShadow?2:0)-(r.castShadow?2:0)+(e.map?1:0)-(r.map?1:0)}function rR(r){const e=new eR,t=tR(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let h=0;h<9;h++)n.probe.push(new F);const i=new F,s=new rt,a=new rt;function c(h){let f=0,p=0,m=0;for(let I=0;I<9;I++)n.probe[I].set(0,0,0);let g=0,x=0,M=0,v=0,_=0,A=0,P=0,b=0,B=0,U=0,O=0;h.sort(iR);for(let I=0,w=h.length;I<w;I++){const H=h[I],ee=H.color,Q=H.intensity,ae=H.distance,ce=H.shadow&&H.shadow.map?H.shadow.map.texture:null;if(H.isAmbientLight)f+=ee.r*Q,p+=ee.g*Q,m+=ee.b*Q;else if(H.isLightProbe){for(let $=0;$<9;$++)n.probe[$].addScaledVector(H.sh.coefficients[$],Q);O++}else if(H.isDirectionalLight){const $=e.get(H);if($.color.copy(H.color).multiplyScalar(H.intensity),H.castShadow){const fe=H.shadow,re=t.get(H);re.shadowIntensity=fe.intensity,re.shadowBias=fe.bias,re.shadowNormalBias=fe.normalBias,re.shadowRadius=fe.radius,re.shadowMapSize=fe.mapSize,n.directionalShadow[g]=re,n.directionalShadowMap[g]=ce,n.directionalShadowMatrix[g]=H.shadow.matrix,A++}n.directional[g]=$,g++}else if(H.isSpotLight){const $=e.get(H);$.position.setFromMatrixPosition(H.matrixWorld),$.color.copy(ee).multiplyScalar(Q),$.distance=ae,$.coneCos=Math.cos(H.angle),$.penumbraCos=Math.cos(H.angle*(1-H.penumbra)),$.decay=H.decay,n.spot[M]=$;const fe=H.shadow;if(H.map&&(n.spotLightMap[B]=H.map,B++,fe.updateMatrices(H),H.castShadow&&U++),n.spotLightMatrix[M]=fe.matrix,H.castShadow){const re=t.get(H);re.shadowIntensity=fe.intensity,re.shadowBias=fe.bias,re.shadowNormalBias=fe.normalBias,re.shadowRadius=fe.radius,re.shadowMapSize=fe.mapSize,n.spotShadow[M]=re,n.spotShadowMap[M]=ce,b++}M++}else if(H.isRectAreaLight){const $=e.get(H);$.color.copy(ee).multiplyScalar(Q),$.halfWidth.set(H.width*.5,0,0),$.halfHeight.set(0,H.height*.5,0),n.rectArea[v]=$,v++}else if(H.isPointLight){const $=e.get(H);if($.color.copy(H.color).multiplyScalar(H.intensity),$.distance=H.distance,$.decay=H.decay,H.castShadow){const fe=H.shadow,re=t.get(H);re.shadowIntensity=fe.intensity,re.shadowBias=fe.bias,re.shadowNormalBias=fe.normalBias,re.shadowRadius=fe.radius,re.shadowMapSize=fe.mapSize,re.shadowCameraNear=fe.camera.near,re.shadowCameraFar=fe.camera.far,n.pointShadow[x]=re,n.pointShadowMap[x]=ce,n.pointShadowMatrix[x]=H.shadow.matrix,P++}n.point[x]=$,x++}else if(H.isHemisphereLight){const $=e.get(H);$.skyColor.copy(H.color).multiplyScalar(Q),$.groundColor.copy(H.groundColor).multiplyScalar(Q),n.hemi[_]=$,_++}}v>0&&(r.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=we.LTC_FLOAT_1,n.rectAreaLTC2=we.LTC_FLOAT_2):(n.rectAreaLTC1=we.LTC_HALF_1,n.rectAreaLTC2=we.LTC_HALF_2)),n.ambient[0]=f,n.ambient[1]=p,n.ambient[2]=m;const z=n.hash;(z.directionalLength!==g||z.pointLength!==x||z.spotLength!==M||z.rectAreaLength!==v||z.hemiLength!==_||z.numDirectionalShadows!==A||z.numPointShadows!==P||z.numSpotShadows!==b||z.numSpotMaps!==B||z.numLightProbes!==O)&&(n.directional.length=g,n.spot.length=M,n.rectArea.length=v,n.point.length=x,n.hemi.length=_,n.directionalShadow.length=A,n.directionalShadowMap.length=A,n.pointShadow.length=P,n.pointShadowMap.length=P,n.spotShadow.length=b,n.spotShadowMap.length=b,n.directionalShadowMatrix.length=A,n.pointShadowMatrix.length=P,n.spotLightMatrix.length=b+B-U,n.spotLightMap.length=B,n.numSpotLightShadowsWithMaps=U,n.numLightProbes=O,z.directionalLength=g,z.pointLength=x,z.spotLength=M,z.rectAreaLength=v,z.hemiLength=_,z.numDirectionalShadows=A,z.numPointShadows=P,z.numSpotShadows=b,z.numSpotMaps=B,z.numLightProbes=O,n.version=nR++)}function u(h,f){let p=0,m=0,g=0,x=0,M=0;const v=f.matrixWorldInverse;for(let _=0,A=h.length;_<A;_++){const P=h[_];if(P.isDirectionalLight){const b=n.directional[p];b.direction.setFromMatrixPosition(P.matrixWorld),i.setFromMatrixPosition(P.target.matrixWorld),b.direction.sub(i),b.direction.transformDirection(v),p++}else if(P.isSpotLight){const b=n.spot[g];b.position.setFromMatrixPosition(P.matrixWorld),b.position.applyMatrix4(v),b.direction.setFromMatrixPosition(P.matrixWorld),i.setFromMatrixPosition(P.target.matrixWorld),b.direction.sub(i),b.direction.transformDirection(v),g++}else if(P.isRectAreaLight){const b=n.rectArea[x];b.position.setFromMatrixPosition(P.matrixWorld),b.position.applyMatrix4(v),a.identity(),s.copy(P.matrixWorld),s.premultiply(v),a.extractRotation(s),b.halfWidth.set(P.width*.5,0,0),b.halfHeight.set(0,P.height*.5,0),b.halfWidth.applyMatrix4(a),b.halfHeight.applyMatrix4(a),x++}else if(P.isPointLight){const b=n.point[m];b.position.setFromMatrixPosition(P.matrixWorld),b.position.applyMatrix4(v),m++}else if(P.isHemisphereLight){const b=n.hemi[M];b.direction.setFromMatrixPosition(P.matrixWorld),b.direction.transformDirection(v),M++}}}return{setup:c,setupView:u,state:n}}function Mm(r){const e=new rR(r),t=[],n=[];function i(f){h.camera=f,t.length=0,n.length=0}function s(f){t.push(f)}function a(f){n.push(f)}function c(){e.setup(t)}function u(f){e.setupView(t,f)}const h={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:i,state:h,setupLights:c,setupLightsView:u,pushLight:s,pushShadow:a}}function sR(r){let e=new WeakMap;function t(i,s=0){const a=e.get(i);let c;return a===void 0?(c=new Mm(r),e.set(i,[c])):s>=a.length?(c=new Mm(r),a.push(c)):c=a[s],c}function n(){e=new WeakMap}return{get:t,dispose:n}}class oR extends Ti{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=HT,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class aR extends Ti{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const cR=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,lR=`uniform sampler2D shadow_pass;
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
}`;function uR(r,e,t){let n=new xd;const i=new Qe,s=new Qe,a=new Pt,c=new oR({depthPacking:VT}),u=new aR,h={},f=t.maxTextureSize,p={[Zi]:Wn,[Wn]:Zi,[Gn]:Gn},m=new br({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new Qe},radius:{value:4}},vertexShader:cR,fragmentShader:lR}),g=m.clone();g.defines.HORIZONTAL_PASS=1;const x=new hn;x.setAttribute("position",new nn(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const M=new Te(x,m),v=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=ug;let _=this.type;this.render=function(U,O,z){if(v.enabled===!1||v.autoUpdate===!1&&v.needsUpdate===!1||U.length===0)return;const I=r.getRenderTarget(),w=r.getActiveCubeFace(),H=r.getActiveMipmapLevel(),ee=r.state;ee.setBlending(yr),ee.buffers.color.setClear(1,1,1,1),ee.buffers.depth.setTest(!0),ee.setScissorTest(!1);const Q=_!==Wi&&this.type===Wi,ae=_===Wi&&this.type!==Wi;for(let ce=0,$=U.length;ce<$;ce++){const fe=U[ce],re=fe.shadow;if(re===void 0){console.warn("THREE.WebGLShadowMap:",fe,"has no shadow.");continue}if(re.autoUpdate===!1&&re.needsUpdate===!1)continue;i.copy(re.mapSize);const ye=re.getFrameExtents();if(i.multiply(ye),s.copy(re.mapSize),(i.x>f||i.y>f)&&(i.x>f&&(s.x=Math.floor(f/ye.x),i.x=s.x*ye.x,re.mapSize.x=s.x),i.y>f&&(s.y=Math.floor(f/ye.y),i.y=s.y*ye.y,re.mapSize.y=s.y)),re.map===null||Q===!0||ae===!0){const Ne=this.type!==Wi?{minFilter:Un,magFilter:Un}:{};re.map!==null&&re.map.dispose(),re.map=new ss(i.x,i.y,Ne),re.map.texture.name=fe.name+".shadowMap",re.camera.updateProjectionMatrix()}r.setRenderTarget(re.map),r.clear();const Me=re.getViewportCount();for(let Ne=0;Ne<Me;Ne++){const Ze=re.getViewport(Ne);a.set(s.x*Ze.x,s.y*Ze.y,s.x*Ze.z,s.y*Ze.w),ee.viewport(a),re.updateMatrices(fe,Ne),n=re.getFrustum(),b(O,z,re.camera,fe,this.type)}re.isPointLightShadow!==!0&&this.type===Wi&&A(re,z),re.needsUpdate=!1}_=this.type,v.needsUpdate=!1,r.setRenderTarget(I,w,H)};function A(U,O){const z=e.update(M);m.defines.VSM_SAMPLES!==U.blurSamples&&(m.defines.VSM_SAMPLES=U.blurSamples,g.defines.VSM_SAMPLES=U.blurSamples,m.needsUpdate=!0,g.needsUpdate=!0),U.mapPass===null&&(U.mapPass=new ss(i.x,i.y)),m.uniforms.shadow_pass.value=U.map.texture,m.uniforms.resolution.value=U.mapSize,m.uniforms.radius.value=U.radius,r.setRenderTarget(U.mapPass),r.clear(),r.renderBufferDirect(O,null,z,m,M,null),g.uniforms.shadow_pass.value=U.mapPass.texture,g.uniforms.resolution.value=U.mapSize,g.uniforms.radius.value=U.radius,r.setRenderTarget(U.map),r.clear(),r.renderBufferDirect(O,null,z,g,M,null)}function P(U,O,z,I){let w=null;const H=z.isPointLight===!0?U.customDistanceMaterial:U.customDepthMaterial;if(H!==void 0)w=H;else if(w=z.isPointLight===!0?u:c,r.localClippingEnabled&&O.clipShadows===!0&&Array.isArray(O.clippingPlanes)&&O.clippingPlanes.length!==0||O.displacementMap&&O.displacementScale!==0||O.alphaMap&&O.alphaTest>0||O.map&&O.alphaTest>0){const ee=w.uuid,Q=O.uuid;let ae=h[ee];ae===void 0&&(ae={},h[ee]=ae);let ce=ae[Q];ce===void 0&&(ce=w.clone(),ae[Q]=ce,O.addEventListener("dispose",B)),w=ce}if(w.visible=O.visible,w.wireframe=O.wireframe,I===Wi?w.side=O.shadowSide!==null?O.shadowSide:O.side:w.side=O.shadowSide!==null?O.shadowSide:p[O.side],w.alphaMap=O.alphaMap,w.alphaTest=O.alphaTest,w.map=O.map,w.clipShadows=O.clipShadows,w.clippingPlanes=O.clippingPlanes,w.clipIntersection=O.clipIntersection,w.displacementMap=O.displacementMap,w.displacementScale=O.displacementScale,w.displacementBias=O.displacementBias,w.wireframeLinewidth=O.wireframeLinewidth,w.linewidth=O.linewidth,z.isPointLight===!0&&w.isMeshDistanceMaterial===!0){const ee=r.properties.get(w);ee.light=z}return w}function b(U,O,z,I,w){if(U.visible===!1)return;if(U.layers.test(O.layers)&&(U.isMesh||U.isLine||U.isPoints)&&(U.castShadow||U.receiveShadow&&w===Wi)&&(!U.frustumCulled||n.intersectsObject(U))){U.modelViewMatrix.multiplyMatrices(z.matrixWorldInverse,U.matrixWorld);const Q=e.update(U),ae=U.material;if(Array.isArray(ae)){const ce=Q.groups;for(let $=0,fe=ce.length;$<fe;$++){const re=ce[$],ye=ae[re.materialIndex];if(ye&&ye.visible){const Me=P(U,ye,I,w);U.onBeforeShadow(r,U,O,z,Q,Me,re),r.renderBufferDirect(z,null,Q,Me,U,re),U.onAfterShadow(r,U,O,z,Q,Me,re)}}}else if(ae.visible){const ce=P(U,ae,I,w);U.onBeforeShadow(r,U,O,z,Q,ce,null),r.renderBufferDirect(z,null,Q,ce,U,null),U.onAfterShadow(r,U,O,z,Q,ce,null)}}const ee=U.children;for(let Q=0,ae=ee.length;Q<ae;Q++)b(ee[Q],O,z,I,w)}function B(U){U.target.removeEventListener("dispose",B);for(const z in h){const I=h[z],w=U.target.uuid;w in I&&(I[w].dispose(),delete I[w])}}}const hR={[vh]:yh,[xh]:Mh,[bh]:Th,[Zs]:Sh,[yh]:vh,[Mh]:xh,[Th]:bh,[Sh]:Zs};function dR(r,e){function t(){let L=!1;const J=new Pt;let W=null;const ie=new Pt(0,0,0,0);return{setMask:function(he){W!==he&&!L&&(r.colorMask(he,he,he,he),W=he)},setLocked:function(he){L=he},setClear:function(he,me,Le,Ke,bt){bt===!0&&(he*=Ke,me*=Ke,Le*=Ke),J.set(he,me,Le,Ke),ie.equals(J)===!1&&(r.clearColor(he,me,Le,Ke),ie.copy(J))},reset:function(){L=!1,W=null,ie.set(-1,0,0,0)}}}function n(){let L=!1,J=!1,W=null,ie=null,he=null;return{setReversed:function(me){if(J!==me){const Le=e.get("EXT_clip_control");J?Le.clipControlEXT(Le.LOWER_LEFT_EXT,Le.ZERO_TO_ONE_EXT):Le.clipControlEXT(Le.LOWER_LEFT_EXT,Le.NEGATIVE_ONE_TO_ONE_EXT);const Ke=he;he=null,this.setClear(Ke)}J=me},getReversed:function(){return J},setTest:function(me){me?Se(r.DEPTH_TEST):We(r.DEPTH_TEST)},setMask:function(me){W!==me&&!L&&(r.depthMask(me),W=me)},setFunc:function(me){if(J&&(me=hR[me]),ie!==me){switch(me){case vh:r.depthFunc(r.NEVER);break;case yh:r.depthFunc(r.ALWAYS);break;case xh:r.depthFunc(r.LESS);break;case Zs:r.depthFunc(r.LEQUAL);break;case bh:r.depthFunc(r.EQUAL);break;case Sh:r.depthFunc(r.GEQUAL);break;case Mh:r.depthFunc(r.GREATER);break;case Th:r.depthFunc(r.NOTEQUAL);break;default:r.depthFunc(r.LEQUAL)}ie=me}},setLocked:function(me){L=me},setClear:function(me){he!==me&&(J&&(me=1-me),r.clearDepth(me),he=me)},reset:function(){L=!1,W=null,ie=null,he=null,J=!1}}}function i(){let L=!1,J=null,W=null,ie=null,he=null,me=null,Le=null,Ke=null,bt=null;return{setTest:function(et){L||(et?Se(r.STENCIL_TEST):We(r.STENCIL_TEST))},setMask:function(et){J!==et&&!L&&(r.stencilMask(et),J=et)},setFunc:function(et,Et,$t){(W!==et||ie!==Et||he!==$t)&&(r.stencilFunc(et,Et,$t),W=et,ie=Et,he=$t)},setOp:function(et,Et,$t){(me!==et||Le!==Et||Ke!==$t)&&(r.stencilOp(et,Et,$t),me=et,Le=Et,Ke=$t)},setLocked:function(et){L=et},setClear:function(et){bt!==et&&(r.clearStencil(et),bt=et)},reset:function(){L=!1,J=null,W=null,ie=null,he=null,me=null,Le=null,Ke=null,bt=null}}}const s=new t,a=new n,c=new i,u=new WeakMap,h=new WeakMap;let f={},p={},m=new WeakMap,g=[],x=null,M=!1,v=null,_=null,A=null,P=null,b=null,B=null,U=null,O=new qe(0,0,0),z=0,I=!1,w=null,H=null,ee=null,Q=null,ae=null;const ce=r.getParameter(r.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let $=!1,fe=0;const re=r.getParameter(r.VERSION);re.indexOf("WebGL")!==-1?(fe=parseFloat(/^WebGL (\d)/.exec(re)[1]),$=fe>=1):re.indexOf("OpenGL ES")!==-1&&(fe=parseFloat(/^OpenGL ES (\d)/.exec(re)[1]),$=fe>=2);let ye=null,Me={};const Ne=r.getParameter(r.SCISSOR_BOX),Ze=r.getParameter(r.VIEWPORT),ht=new Pt().fromArray(Ne),le=new Pt().fromArray(Ze);function ge(L,J,W,ie){const he=new Uint8Array(4),me=r.createTexture();r.bindTexture(L,me),r.texParameteri(L,r.TEXTURE_MIN_FILTER,r.NEAREST),r.texParameteri(L,r.TEXTURE_MAG_FILTER,r.NEAREST);for(let Le=0;Le<W;Le++)L===r.TEXTURE_3D||L===r.TEXTURE_2D_ARRAY?r.texImage3D(J,0,r.RGBA,1,1,ie,0,r.RGBA,r.UNSIGNED_BYTE,he):r.texImage2D(J+Le,0,r.RGBA,1,1,0,r.RGBA,r.UNSIGNED_BYTE,he);return me}const Oe={};Oe[r.TEXTURE_2D]=ge(r.TEXTURE_2D,r.TEXTURE_2D,1),Oe[r.TEXTURE_CUBE_MAP]=ge(r.TEXTURE_CUBE_MAP,r.TEXTURE_CUBE_MAP_POSITIVE_X,6),Oe[r.TEXTURE_2D_ARRAY]=ge(r.TEXTURE_2D_ARRAY,r.TEXTURE_2D_ARRAY,1,1),Oe[r.TEXTURE_3D]=ge(r.TEXTURE_3D,r.TEXTURE_3D,1,1),s.setClear(0,0,0,1),a.setClear(1),c.setClear(0),Se(r.DEPTH_TEST),a.setFunc(Zs),at(!1),dt(Ap),Se(r.CULL_FACE),X(yr);function Se(L){f[L]!==!0&&(r.enable(L),f[L]=!0)}function We(L){f[L]!==!1&&(r.disable(L),f[L]=!1)}function tt(L,J){return p[L]!==J?(r.bindFramebuffer(L,J),p[L]=J,L===r.DRAW_FRAMEBUFFER&&(p[r.FRAMEBUFFER]=J),L===r.FRAMEBUFFER&&(p[r.DRAW_FRAMEBUFFER]=J),!0):!1}function st(L,J){let W=g,ie=!1;if(L){W=m.get(J),W===void 0&&(W=[],m.set(J,W));const he=L.textures;if(W.length!==he.length||W[0]!==r.COLOR_ATTACHMENT0){for(let me=0,Le=he.length;me<Le;me++)W[me]=r.COLOR_ATTACHMENT0+me;W.length=he.length,ie=!0}}else W[0]!==r.BACK&&(W[0]=r.BACK,ie=!0);ie&&r.drawBuffers(W)}function Tt(L){return x!==L?(r.useProgram(L),x=L,!0):!1}const ot={[ts]:r.FUNC_ADD,[hT]:r.FUNC_SUBTRACT,[dT]:r.FUNC_REVERSE_SUBTRACT};ot[fT]=r.MIN,ot[pT]=r.MAX;const Ot={[mT]:r.ZERO,[gT]:r.ONE,[_T]:r.SRC_COLOR,[gh]:r.SRC_ALPHA,[MT]:r.SRC_ALPHA_SATURATE,[bT]:r.DST_COLOR,[yT]:r.DST_ALPHA,[vT]:r.ONE_MINUS_SRC_COLOR,[_h]:r.ONE_MINUS_SRC_ALPHA,[ST]:r.ONE_MINUS_DST_COLOR,[xT]:r.ONE_MINUS_DST_ALPHA,[TT]:r.CONSTANT_COLOR,[ET]:r.ONE_MINUS_CONSTANT_COLOR,[AT]:r.CONSTANT_ALPHA,[wT]:r.ONE_MINUS_CONSTANT_ALPHA};function X(L,J,W,ie,he,me,Le,Ke,bt,et){if(L===yr){M===!0&&(We(r.BLEND),M=!1);return}if(M===!1&&(Se(r.BLEND),M=!0),L!==uT){if(L!==v||et!==I){if((_!==ts||b!==ts)&&(r.blendEquation(r.FUNC_ADD),_=ts,b=ts),et)switch(L){case Xs:r.blendFuncSeparate(r.ONE,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case wp:r.blendFunc(r.ONE,r.ONE);break;case Pp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Rp:r.blendFuncSeparate(r.ZERO,r.SRC_COLOR,r.ZERO,r.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",L);break}else switch(L){case Xs:r.blendFuncSeparate(r.SRC_ALPHA,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case wp:r.blendFunc(r.SRC_ALPHA,r.ONE);break;case Pp:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Rp:r.blendFunc(r.ZERO,r.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",L);break}A=null,P=null,B=null,U=null,O.set(0,0,0),z=0,v=L,I=et}return}he=he||J,me=me||W,Le=Le||ie,(J!==_||he!==b)&&(r.blendEquationSeparate(ot[J],ot[he]),_=J,b=he),(W!==A||ie!==P||me!==B||Le!==U)&&(r.blendFuncSeparate(Ot[W],Ot[ie],Ot[me],Ot[Le]),A=W,P=ie,B=me,U=Le),(Ke.equals(O)===!1||bt!==z)&&(r.blendColor(Ke.r,Ke.g,Ke.b,bt),O.copy(Ke),z=bt),v=L,I=!1}function Qt(L,J){L.side===Gn?We(r.CULL_FACE):Se(r.CULL_FACE);let W=L.side===Wn;J&&(W=!W),at(W),L.blending===Xs&&L.transparent===!1?X(yr):X(L.blending,L.blendEquation,L.blendSrc,L.blendDst,L.blendEquationAlpha,L.blendSrcAlpha,L.blendDstAlpha,L.blendColor,L.blendAlpha,L.premultipliedAlpha),a.setFunc(L.depthFunc),a.setTest(L.depthTest),a.setMask(L.depthWrite),s.setMask(L.colorWrite);const ie=L.stencilWrite;c.setTest(ie),ie&&(c.setMask(L.stencilWriteMask),c.setFunc(L.stencilFunc,L.stencilRef,L.stencilFuncMask),c.setOp(L.stencilFail,L.stencilZFail,L.stencilZPass)),xt(L.polygonOffset,L.polygonOffsetFactor,L.polygonOffsetUnits),L.alphaToCoverage===!0?Se(r.SAMPLE_ALPHA_TO_COVERAGE):We(r.SAMPLE_ALPHA_TO_COVERAGE)}function at(L){w!==L&&(L?r.frontFace(r.CW):r.frontFace(r.CCW),w=L)}function dt(L){L!==aT?(Se(r.CULL_FACE),L!==H&&(L===Ap?r.cullFace(r.BACK):L===cT?r.cullFace(r.FRONT):r.cullFace(r.FRONT_AND_BACK))):We(r.CULL_FACE),H=L}function Ve(L){L!==ee&&($&&r.lineWidth(L),ee=L)}function xt(L,J,W){L?(Se(r.POLYGON_OFFSET_FILL),(Q!==J||ae!==W)&&(r.polygonOffset(J,W),Q=J,ae=W)):We(r.POLYGON_OFFSET_FILL)}function Fe(L){L?Se(r.SCISSOR_TEST):We(r.SCISSOR_TEST)}function N(L){L===void 0&&(L=r.TEXTURE0+ce-1),ye!==L&&(r.activeTexture(L),ye=L)}function E(L,J,W){W===void 0&&(ye===null?W=r.TEXTURE0+ce-1:W=ye);let ie=Me[W];ie===void 0&&(ie={type:void 0,texture:void 0},Me[W]=ie),(ie.type!==L||ie.texture!==J)&&(ye!==W&&(r.activeTexture(W),ye=W),r.bindTexture(L,J||Oe[L]),ie.type=L,ie.texture=J)}function Z(){const L=Me[ye];L!==void 0&&L.type!==void 0&&(r.bindTexture(L.type,null),L.type=void 0,L.texture=void 0)}function ue(){try{r.compressedTexImage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function pe(){try{r.compressedTexImage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function de(){try{r.texSubImage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function De(){try{r.texSubImage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function Ee(){try{r.compressedTexSubImage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function Re(){try{r.compressedTexSubImage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function ct(){try{r.texStorage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function _e(){try{r.texStorage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function Ce(){try{r.texImage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function Ue(){try{r.texImage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function Ye(L){ht.equals(L)===!1&&(r.scissor(L.x,L.y,L.z,L.w),ht.copy(L))}function Ie(L){le.equals(L)===!1&&(r.viewport(L.x,L.y,L.z,L.w),le.copy(L))}function pt(L,J){let W=h.get(J);W===void 0&&(W=new WeakMap,h.set(J,W));let ie=W.get(L);ie===void 0&&(ie=r.getUniformBlockIndex(J,L.name),W.set(L,ie))}function it(L,J){const ie=h.get(J).get(L);u.get(J)!==ie&&(r.uniformBlockBinding(J,ie,L.__bindingPointIndex),u.set(J,ie))}function V(){r.disable(r.BLEND),r.disable(r.CULL_FACE),r.disable(r.DEPTH_TEST),r.disable(r.POLYGON_OFFSET_FILL),r.disable(r.SCISSOR_TEST),r.disable(r.STENCIL_TEST),r.disable(r.SAMPLE_ALPHA_TO_COVERAGE),r.blendEquation(r.FUNC_ADD),r.blendFunc(r.ONE,r.ZERO),r.blendFuncSeparate(r.ONE,r.ZERO,r.ONE,r.ZERO),r.blendColor(0,0,0,0),r.colorMask(!0,!0,!0,!0),r.clearColor(0,0,0,0),r.depthMask(!0),r.depthFunc(r.LESS),a.setReversed(!1),r.clearDepth(1),r.stencilMask(4294967295),r.stencilFunc(r.ALWAYS,0,4294967295),r.stencilOp(r.KEEP,r.KEEP,r.KEEP),r.clearStencil(0),r.cullFace(r.BACK),r.frontFace(r.CCW),r.polygonOffset(0,0),r.activeTexture(r.TEXTURE0),r.bindFramebuffer(r.FRAMEBUFFER,null),r.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),r.bindFramebuffer(r.READ_FRAMEBUFFER,null),r.useProgram(null),r.lineWidth(1),r.scissor(0,0,r.canvas.width,r.canvas.height),r.viewport(0,0,r.canvas.width,r.canvas.height),f={},ye=null,Me={},p={},m=new WeakMap,g=[],x=null,M=!1,v=null,_=null,A=null,P=null,b=null,B=null,U=null,O=new qe(0,0,0),z=0,I=!1,w=null,H=null,ee=null,Q=null,ae=null,ht.set(0,0,r.canvas.width,r.canvas.height),le.set(0,0,r.canvas.width,r.canvas.height),s.reset(),a.reset(),c.reset()}return{buffers:{color:s,depth:a,stencil:c},enable:Se,disable:We,bindFramebuffer:tt,drawBuffers:st,useProgram:Tt,setBlending:X,setMaterial:Qt,setFlipSided:at,setCullFace:dt,setLineWidth:Ve,setPolygonOffset:xt,setScissorTest:Fe,activeTexture:N,bindTexture:E,unbindTexture:Z,compressedTexImage2D:ue,compressedTexImage3D:pe,texImage2D:Ce,texImage3D:Ue,updateUBOMapping:pt,uniformBlockBinding:it,texStorage2D:ct,texStorage3D:_e,texSubImage2D:de,texSubImage3D:De,compressedTexSubImage2D:Ee,compressedTexSubImage3D:Re,scissor:Ye,viewport:Ie,reset:V}}function Tm(r,e,t,n){const i=fR(n);switch(t){case vg:return r*e;case xg:return r*e;case bg:return r*e*2;case dd:return r*e/i.components*i.byteLength;case fd:return r*e/i.components*i.byteLength;case Sg:return r*e*2/i.components*i.byteLength;case pd:return r*e*2/i.components*i.byteLength;case yg:return r*e*3/i.components*i.byteLength;case ai:return r*e*4/i.components*i.byteLength;case md:return r*e*4/i.components*i.byteLength;case Tc:case Ec:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Ac:case wc:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Ph:case Ch:return Math.max(r,16)*Math.max(e,8)/4;case wh:case Rh:return Math.max(r,8)*Math.max(e,8)/2;case Ih:case Lh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Dh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Nh:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Oh:return Math.floor((r+4)/5)*Math.floor((e+3)/4)*16;case Uh:return Math.floor((r+4)/5)*Math.floor((e+4)/5)*16;case Fh:return Math.floor((r+5)/6)*Math.floor((e+4)/5)*16;case Bh:return Math.floor((r+5)/6)*Math.floor((e+5)/6)*16;case kh:return Math.floor((r+7)/8)*Math.floor((e+4)/5)*16;case zh:return Math.floor((r+7)/8)*Math.floor((e+5)/6)*16;case Hh:return Math.floor((r+7)/8)*Math.floor((e+7)/8)*16;case Vh:return Math.floor((r+9)/10)*Math.floor((e+4)/5)*16;case Gh:return Math.floor((r+9)/10)*Math.floor((e+5)/6)*16;case Wh:return Math.floor((r+9)/10)*Math.floor((e+7)/8)*16;case jh:return Math.floor((r+9)/10)*Math.floor((e+9)/10)*16;case Xh:return Math.floor((r+11)/12)*Math.floor((e+9)/10)*16;case qh:return Math.floor((r+11)/12)*Math.floor((e+11)/12)*16;case Pc:case Yh:case Kh:return Math.ceil(r/4)*Math.ceil(e/4)*16;case Mg:case Zh:return Math.ceil(r/4)*Math.ceil(e/4)*8;case $h:case Jh:return Math.ceil(r/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function fR(r){switch(r){case $i:case mg:return{byteLength:1,components:1};case Jo:case gg:case na:return{byteLength:2,components:1};case ud:case hd:return{byteLength:2,components:4};case rs:case ld:case gi:return{byteLength:4,components:1};case _g:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${r}.`)}function pR(r,e,t,n,i,s,a){const c=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,u=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),h=new Qe,f=new WeakMap;let p;const m=new WeakMap;let g=!1;try{g=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function x(N,E){return g?new OffscreenCanvas(N,E):ta("canvas")}function M(N,E,Z){let ue=1;const pe=Fe(N);if((pe.width>Z||pe.height>Z)&&(ue=Z/Math.max(pe.width,pe.height)),ue<1)if(typeof HTMLImageElement<"u"&&N instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&N instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&N instanceof ImageBitmap||typeof VideoFrame<"u"&&N instanceof VideoFrame){const de=Math.floor(ue*pe.width),De=Math.floor(ue*pe.height);p===void 0&&(p=x(de,De));const Ee=E?x(de,De):p;return Ee.width=de,Ee.height=De,Ee.getContext("2d").drawImage(N,0,0,de,De),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+pe.width+"x"+pe.height+") to ("+de+"x"+De+")."),Ee}else return"data"in N&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+pe.width+"x"+pe.height+")."),N;return N}function v(N){return N.generateMipmaps}function _(N){r.generateMipmap(N)}function A(N){return N.isWebGLCubeRenderTarget?r.TEXTURE_CUBE_MAP:N.isWebGL3DRenderTarget?r.TEXTURE_3D:N.isWebGLArrayRenderTarget||N.isCompressedArrayTexture?r.TEXTURE_2D_ARRAY:r.TEXTURE_2D}function P(N,E,Z,ue,pe=!1){if(N!==null){if(r[N]!==void 0)return r[N];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+N+"'")}let de=E;if(E===r.RED&&(Z===r.FLOAT&&(de=r.R32F),Z===r.HALF_FLOAT&&(de=r.R16F),Z===r.UNSIGNED_BYTE&&(de=r.R8)),E===r.RED_INTEGER&&(Z===r.UNSIGNED_BYTE&&(de=r.R8UI),Z===r.UNSIGNED_SHORT&&(de=r.R16UI),Z===r.UNSIGNED_INT&&(de=r.R32UI),Z===r.BYTE&&(de=r.R8I),Z===r.SHORT&&(de=r.R16I),Z===r.INT&&(de=r.R32I)),E===r.RG&&(Z===r.FLOAT&&(de=r.RG32F),Z===r.HALF_FLOAT&&(de=r.RG16F),Z===r.UNSIGNED_BYTE&&(de=r.RG8)),E===r.RG_INTEGER&&(Z===r.UNSIGNED_BYTE&&(de=r.RG8UI),Z===r.UNSIGNED_SHORT&&(de=r.RG16UI),Z===r.UNSIGNED_INT&&(de=r.RG32UI),Z===r.BYTE&&(de=r.RG8I),Z===r.SHORT&&(de=r.RG16I),Z===r.INT&&(de=r.RG32I)),E===r.RGB_INTEGER&&(Z===r.UNSIGNED_BYTE&&(de=r.RGB8UI),Z===r.UNSIGNED_SHORT&&(de=r.RGB16UI),Z===r.UNSIGNED_INT&&(de=r.RGB32UI),Z===r.BYTE&&(de=r.RGB8I),Z===r.SHORT&&(de=r.RGB16I),Z===r.INT&&(de=r.RGB32I)),E===r.RGBA_INTEGER&&(Z===r.UNSIGNED_BYTE&&(de=r.RGBA8UI),Z===r.UNSIGNED_SHORT&&(de=r.RGBA16UI),Z===r.UNSIGNED_INT&&(de=r.RGBA32UI),Z===r.BYTE&&(de=r.RGBA8I),Z===r.SHORT&&(de=r.RGBA16I),Z===r.INT&&(de=r.RGBA32I)),E===r.RGB&&Z===r.UNSIGNED_INT_5_9_9_9_REV&&(de=r.RGB9_E5),E===r.RGBA){const De=pe?zc:Mt.getTransfer(ue);Z===r.FLOAT&&(de=r.RGBA32F),Z===r.HALF_FLOAT&&(de=r.RGBA16F),Z===r.UNSIGNED_BYTE&&(de=De===Ut?r.SRGB8_ALPHA8:r.RGBA8),Z===r.UNSIGNED_SHORT_4_4_4_4&&(de=r.RGBA4),Z===r.UNSIGNED_SHORT_5_5_5_1&&(de=r.RGB5_A1)}return(de===r.R16F||de===r.R32F||de===r.RG16F||de===r.RG32F||de===r.RGBA16F||de===r.RGBA32F)&&e.get("EXT_color_buffer_float"),de}function b(N,E){let Z;return N?E===null||E===rs||E===eo?Z=r.DEPTH24_STENCIL8:E===gi?Z=r.DEPTH32F_STENCIL8:E===Jo&&(Z=r.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):E===null||E===rs||E===eo?Z=r.DEPTH_COMPONENT24:E===gi?Z=r.DEPTH_COMPONENT32F:E===Jo&&(Z=r.DEPTH_COMPONENT16),Z}function B(N,E){return v(N)===!0||N.isFramebufferTexture&&N.minFilter!==Un&&N.minFilter!==ti?Math.log2(Math.max(E.width,E.height))+1:N.mipmaps!==void 0&&N.mipmaps.length>0?N.mipmaps.length:N.isCompressedTexture&&Array.isArray(N.image)?E.mipmaps.length:1}function U(N){const E=N.target;E.removeEventListener("dispose",U),z(E),E.isVideoTexture&&f.delete(E)}function O(N){const E=N.target;E.removeEventListener("dispose",O),w(E)}function z(N){const E=n.get(N);if(E.__webglInit===void 0)return;const Z=N.source,ue=m.get(Z);if(ue){const pe=ue[E.__cacheKey];pe.usedTimes--,pe.usedTimes===0&&I(N),Object.keys(ue).length===0&&m.delete(Z)}n.remove(N)}function I(N){const E=n.get(N);r.deleteTexture(E.__webglTexture);const Z=N.source,ue=m.get(Z);delete ue[E.__cacheKey],a.memory.textures--}function w(N){const E=n.get(N);if(N.depthTexture&&(N.depthTexture.dispose(),n.remove(N.depthTexture)),N.isWebGLCubeRenderTarget)for(let ue=0;ue<6;ue++){if(Array.isArray(E.__webglFramebuffer[ue]))for(let pe=0;pe<E.__webglFramebuffer[ue].length;pe++)r.deleteFramebuffer(E.__webglFramebuffer[ue][pe]);else r.deleteFramebuffer(E.__webglFramebuffer[ue]);E.__webglDepthbuffer&&r.deleteRenderbuffer(E.__webglDepthbuffer[ue])}else{if(Array.isArray(E.__webglFramebuffer))for(let ue=0;ue<E.__webglFramebuffer.length;ue++)r.deleteFramebuffer(E.__webglFramebuffer[ue]);else r.deleteFramebuffer(E.__webglFramebuffer);if(E.__webglDepthbuffer&&r.deleteRenderbuffer(E.__webglDepthbuffer),E.__webglMultisampledFramebuffer&&r.deleteFramebuffer(E.__webglMultisampledFramebuffer),E.__webglColorRenderbuffer)for(let ue=0;ue<E.__webglColorRenderbuffer.length;ue++)E.__webglColorRenderbuffer[ue]&&r.deleteRenderbuffer(E.__webglColorRenderbuffer[ue]);E.__webglDepthRenderbuffer&&r.deleteRenderbuffer(E.__webglDepthRenderbuffer)}const Z=N.textures;for(let ue=0,pe=Z.length;ue<pe;ue++){const de=n.get(Z[ue]);de.__webglTexture&&(r.deleteTexture(de.__webglTexture),a.memory.textures--),n.remove(Z[ue])}n.remove(N)}let H=0;function ee(){H=0}function Q(){const N=H;return N>=i.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+N+" texture units while this GPU supports only "+i.maxTextures),H+=1,N}function ae(N){const E=[];return E.push(N.wrapS),E.push(N.wrapT),E.push(N.wrapR||0),E.push(N.magFilter),E.push(N.minFilter),E.push(N.anisotropy),E.push(N.internalFormat),E.push(N.format),E.push(N.type),E.push(N.generateMipmaps),E.push(N.premultiplyAlpha),E.push(N.flipY),E.push(N.unpackAlignment),E.push(N.colorSpace),E.join()}function ce(N,E){const Z=n.get(N);if(N.isVideoTexture&&Ve(N),N.isRenderTargetTexture===!1&&N.version>0&&Z.__version!==N.version){const ue=N.image;if(ue===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(ue.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{le(Z,N,E);return}}t.bindTexture(r.TEXTURE_2D,Z.__webglTexture,r.TEXTURE0+E)}function $(N,E){const Z=n.get(N);if(N.version>0&&Z.__version!==N.version){le(Z,N,E);return}t.bindTexture(r.TEXTURE_2D_ARRAY,Z.__webglTexture,r.TEXTURE0+E)}function fe(N,E){const Z=n.get(N);if(N.version>0&&Z.__version!==N.version){le(Z,N,E);return}t.bindTexture(r.TEXTURE_3D,Z.__webglTexture,r.TEXTURE0+E)}function re(N,E){const Z=n.get(N);if(N.version>0&&Z.__version!==N.version){ge(Z,N,E);return}t.bindTexture(r.TEXTURE_CUBE_MAP,Z.__webglTexture,r.TEXTURE0+E)}const ye={[Qs]:r.REPEAT,[_r]:r.CLAMP_TO_EDGE,[Dc]:r.MIRRORED_REPEAT},Me={[Un]:r.NEAREST,[pg]:r.NEAREST_MIPMAP_NEAREST,[Go]:r.NEAREST_MIPMAP_LINEAR,[ti]:r.LINEAR,[Mc]:r.LINEAR_MIPMAP_NEAREST,[Xi]:r.LINEAR_MIPMAP_LINEAR},Ne={[WT]:r.NEVER,[ZT]:r.ALWAYS,[jT]:r.LESS,[Ag]:r.LEQUAL,[XT]:r.EQUAL,[KT]:r.GEQUAL,[qT]:r.GREATER,[YT]:r.NOTEQUAL};function Ze(N,E){if(E.type===gi&&e.has("OES_texture_float_linear")===!1&&(E.magFilter===ti||E.magFilter===Mc||E.magFilter===Go||E.magFilter===Xi||E.minFilter===ti||E.minFilter===Mc||E.minFilter===Go||E.minFilter===Xi)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),r.texParameteri(N,r.TEXTURE_WRAP_S,ye[E.wrapS]),r.texParameteri(N,r.TEXTURE_WRAP_T,ye[E.wrapT]),(N===r.TEXTURE_3D||N===r.TEXTURE_2D_ARRAY)&&r.texParameteri(N,r.TEXTURE_WRAP_R,ye[E.wrapR]),r.texParameteri(N,r.TEXTURE_MAG_FILTER,Me[E.magFilter]),r.texParameteri(N,r.TEXTURE_MIN_FILTER,Me[E.minFilter]),E.compareFunction&&(r.texParameteri(N,r.TEXTURE_COMPARE_MODE,r.COMPARE_REF_TO_TEXTURE),r.texParameteri(N,r.TEXTURE_COMPARE_FUNC,Ne[E.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(E.magFilter===Un||E.minFilter!==Go&&E.minFilter!==Xi||E.type===gi&&e.has("OES_texture_float_linear")===!1)return;if(E.anisotropy>1||n.get(E).__currentAnisotropy){const Z=e.get("EXT_texture_filter_anisotropic");r.texParameterf(N,Z.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(E.anisotropy,i.getMaxAnisotropy())),n.get(E).__currentAnisotropy=E.anisotropy}}}function ht(N,E){let Z=!1;N.__webglInit===void 0&&(N.__webglInit=!0,E.addEventListener("dispose",U));const ue=E.source;let pe=m.get(ue);pe===void 0&&(pe={},m.set(ue,pe));const de=ae(E);if(de!==N.__cacheKey){pe[de]===void 0&&(pe[de]={texture:r.createTexture(),usedTimes:0},a.memory.textures++,Z=!0),pe[de].usedTimes++;const De=pe[N.__cacheKey];De!==void 0&&(pe[N.__cacheKey].usedTimes--,De.usedTimes===0&&I(E)),N.__cacheKey=de,N.__webglTexture=pe[de].texture}return Z}function le(N,E,Z){let ue=r.TEXTURE_2D;(E.isDataArrayTexture||E.isCompressedArrayTexture)&&(ue=r.TEXTURE_2D_ARRAY),E.isData3DTexture&&(ue=r.TEXTURE_3D);const pe=ht(N,E),de=E.source;t.bindTexture(ue,N.__webglTexture,r.TEXTURE0+Z);const De=n.get(de);if(de.version!==De.__version||pe===!0){t.activeTexture(r.TEXTURE0+Z);const Ee=Mt.getPrimaries(Mt.workingColorSpace),Re=E.colorSpace===gr?null:Mt.getPrimaries(E.colorSpace),ct=E.colorSpace===gr||Ee===Re?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,E.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,E.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,ct);let _e=M(E.image,!1,i.maxTextureSize);_e=xt(E,_e);const Ce=s.convert(E.format,E.colorSpace),Ue=s.convert(E.type);let Ye=P(E.internalFormat,Ce,Ue,E.colorSpace,E.isVideoTexture);Ze(ue,E);let Ie;const pt=E.mipmaps,it=E.isVideoTexture!==!0,V=De.__version===void 0||pe===!0,L=de.dataReady,J=B(E,_e);if(E.isDepthTexture)Ye=b(E.format===to,E.type),V&&(it?t.texStorage2D(r.TEXTURE_2D,1,Ye,_e.width,_e.height):t.texImage2D(r.TEXTURE_2D,0,Ye,_e.width,_e.height,0,Ce,Ue,null));else if(E.isDataTexture)if(pt.length>0){it&&V&&t.texStorage2D(r.TEXTURE_2D,J,Ye,pt[0].width,pt[0].height);for(let W=0,ie=pt.length;W<ie;W++)Ie=pt[W],it?L&&t.texSubImage2D(r.TEXTURE_2D,W,0,0,Ie.width,Ie.height,Ce,Ue,Ie.data):t.texImage2D(r.TEXTURE_2D,W,Ye,Ie.width,Ie.height,0,Ce,Ue,Ie.data);E.generateMipmaps=!1}else it?(V&&t.texStorage2D(r.TEXTURE_2D,J,Ye,_e.width,_e.height),L&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,_e.width,_e.height,Ce,Ue,_e.data)):t.texImage2D(r.TEXTURE_2D,0,Ye,_e.width,_e.height,0,Ce,Ue,_e.data);else if(E.isCompressedTexture)if(E.isCompressedArrayTexture){it&&V&&t.texStorage3D(r.TEXTURE_2D_ARRAY,J,Ye,pt[0].width,pt[0].height,_e.depth);for(let W=0,ie=pt.length;W<ie;W++)if(Ie=pt[W],E.format!==ai)if(Ce!==null)if(it){if(L)if(E.layerUpdates.size>0){const he=Tm(Ie.width,Ie.height,E.format,E.type);for(const me of E.layerUpdates){const Le=Ie.data.subarray(me*he/Ie.data.BYTES_PER_ELEMENT,(me+1)*he/Ie.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,W,0,0,me,Ie.width,Ie.height,1,Ce,Le)}E.clearLayerUpdates()}else t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,W,0,0,0,Ie.width,Ie.height,_e.depth,Ce,Ie.data)}else t.compressedTexImage3D(r.TEXTURE_2D_ARRAY,W,Ye,Ie.width,Ie.height,_e.depth,0,Ie.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else it?L&&t.texSubImage3D(r.TEXTURE_2D_ARRAY,W,0,0,0,Ie.width,Ie.height,_e.depth,Ce,Ue,Ie.data):t.texImage3D(r.TEXTURE_2D_ARRAY,W,Ye,Ie.width,Ie.height,_e.depth,0,Ce,Ue,Ie.data)}else{it&&V&&t.texStorage2D(r.TEXTURE_2D,J,Ye,pt[0].width,pt[0].height);for(let W=0,ie=pt.length;W<ie;W++)Ie=pt[W],E.format!==ai?Ce!==null?it?L&&t.compressedTexSubImage2D(r.TEXTURE_2D,W,0,0,Ie.width,Ie.height,Ce,Ie.data):t.compressedTexImage2D(r.TEXTURE_2D,W,Ye,Ie.width,Ie.height,0,Ie.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):it?L&&t.texSubImage2D(r.TEXTURE_2D,W,0,0,Ie.width,Ie.height,Ce,Ue,Ie.data):t.texImage2D(r.TEXTURE_2D,W,Ye,Ie.width,Ie.height,0,Ce,Ue,Ie.data)}else if(E.isDataArrayTexture)if(it){if(V&&t.texStorage3D(r.TEXTURE_2D_ARRAY,J,Ye,_e.width,_e.height,_e.depth),L)if(E.layerUpdates.size>0){const W=Tm(_e.width,_e.height,E.format,E.type);for(const ie of E.layerUpdates){const he=_e.data.subarray(ie*W/_e.data.BYTES_PER_ELEMENT,(ie+1)*W/_e.data.BYTES_PER_ELEMENT);t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,ie,_e.width,_e.height,1,Ce,Ue,he)}E.clearLayerUpdates()}else t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,0,_e.width,_e.height,_e.depth,Ce,Ue,_e.data)}else t.texImage3D(r.TEXTURE_2D_ARRAY,0,Ye,_e.width,_e.height,_e.depth,0,Ce,Ue,_e.data);else if(E.isData3DTexture)it?(V&&t.texStorage3D(r.TEXTURE_3D,J,Ye,_e.width,_e.height,_e.depth),L&&t.texSubImage3D(r.TEXTURE_3D,0,0,0,0,_e.width,_e.height,_e.depth,Ce,Ue,_e.data)):t.texImage3D(r.TEXTURE_3D,0,Ye,_e.width,_e.height,_e.depth,0,Ce,Ue,_e.data);else if(E.isFramebufferTexture){if(V)if(it)t.texStorage2D(r.TEXTURE_2D,J,Ye,_e.width,_e.height);else{let W=_e.width,ie=_e.height;for(let he=0;he<J;he++)t.texImage2D(r.TEXTURE_2D,he,Ye,W,ie,0,Ce,Ue,null),W>>=1,ie>>=1}}else if(pt.length>0){if(it&&V){const W=Fe(pt[0]);t.texStorage2D(r.TEXTURE_2D,J,Ye,W.width,W.height)}for(let W=0,ie=pt.length;W<ie;W++)Ie=pt[W],it?L&&t.texSubImage2D(r.TEXTURE_2D,W,0,0,Ce,Ue,Ie):t.texImage2D(r.TEXTURE_2D,W,Ye,Ce,Ue,Ie);E.generateMipmaps=!1}else if(it){if(V){const W=Fe(_e);t.texStorage2D(r.TEXTURE_2D,J,Ye,W.width,W.height)}L&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,Ce,Ue,_e)}else t.texImage2D(r.TEXTURE_2D,0,Ye,Ce,Ue,_e);v(E)&&_(ue),De.__version=de.version,E.onUpdate&&E.onUpdate(E)}N.__version=E.version}function ge(N,E,Z){if(E.image.length!==6)return;const ue=ht(N,E),pe=E.source;t.bindTexture(r.TEXTURE_CUBE_MAP,N.__webglTexture,r.TEXTURE0+Z);const de=n.get(pe);if(pe.version!==de.__version||ue===!0){t.activeTexture(r.TEXTURE0+Z);const De=Mt.getPrimaries(Mt.workingColorSpace),Ee=E.colorSpace===gr?null:Mt.getPrimaries(E.colorSpace),Re=E.colorSpace===gr||De===Ee?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,E.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,E.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,E.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,Re);const ct=E.isCompressedTexture||E.image[0].isCompressedTexture,_e=E.image[0]&&E.image[0].isDataTexture,Ce=[];for(let ie=0;ie<6;ie++)!ct&&!_e?Ce[ie]=M(E.image[ie],!0,i.maxCubemapSize):Ce[ie]=_e?E.image[ie].image:E.image[ie],Ce[ie]=xt(E,Ce[ie]);const Ue=Ce[0],Ye=s.convert(E.format,E.colorSpace),Ie=s.convert(E.type),pt=P(E.internalFormat,Ye,Ie,E.colorSpace),it=E.isVideoTexture!==!0,V=de.__version===void 0||ue===!0,L=pe.dataReady;let J=B(E,Ue);Ze(r.TEXTURE_CUBE_MAP,E);let W;if(ct){it&&V&&t.texStorage2D(r.TEXTURE_CUBE_MAP,J,pt,Ue.width,Ue.height);for(let ie=0;ie<6;ie++){W=Ce[ie].mipmaps;for(let he=0;he<W.length;he++){const me=W[he];E.format!==ai?Ye!==null?it?L&&t.compressedTexSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,he,0,0,me.width,me.height,Ye,me.data):t.compressedTexImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,he,pt,me.width,me.height,0,me.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):it?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,he,0,0,me.width,me.height,Ye,Ie,me.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,he,pt,me.width,me.height,0,Ye,Ie,me.data)}}}else{if(W=E.mipmaps,it&&V){W.length>0&&J++;const ie=Fe(Ce[0]);t.texStorage2D(r.TEXTURE_CUBE_MAP,J,pt,ie.width,ie.height)}for(let ie=0;ie<6;ie++)if(_e){it?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,0,0,Ce[ie].width,Ce[ie].height,Ye,Ie,Ce[ie].data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,pt,Ce[ie].width,Ce[ie].height,0,Ye,Ie,Ce[ie].data);for(let he=0;he<W.length;he++){const Le=W[he].image[ie].image;it?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,he+1,0,0,Le.width,Le.height,Ye,Ie,Le.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,he+1,pt,Le.width,Le.height,0,Ye,Ie,Le.data)}}else{it?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,0,0,Ye,Ie,Ce[ie]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0,pt,Ye,Ie,Ce[ie]);for(let he=0;he<W.length;he++){const me=W[he];it?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,he+1,0,0,Ye,Ie,me.image[ie]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,he+1,pt,Ye,Ie,me.image[ie])}}}v(E)&&_(r.TEXTURE_CUBE_MAP),de.__version=pe.version,E.onUpdate&&E.onUpdate(E)}N.__version=E.version}function Oe(N,E,Z,ue,pe,de){const De=s.convert(Z.format,Z.colorSpace),Ee=s.convert(Z.type),Re=P(Z.internalFormat,De,Ee,Z.colorSpace),ct=n.get(E),_e=n.get(Z);if(_e.__renderTarget=E,!ct.__hasExternalTextures){const Ce=Math.max(1,E.width>>de),Ue=Math.max(1,E.height>>de);pe===r.TEXTURE_3D||pe===r.TEXTURE_2D_ARRAY?t.texImage3D(pe,de,Re,Ce,Ue,E.depth,0,De,Ee,null):t.texImage2D(pe,de,Re,Ce,Ue,0,De,Ee,null)}t.bindFramebuffer(r.FRAMEBUFFER,N),dt(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,ue,pe,_e.__webglTexture,0,at(E)):(pe===r.TEXTURE_2D||pe>=r.TEXTURE_CUBE_MAP_POSITIVE_X&&pe<=r.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&r.framebufferTexture2D(r.FRAMEBUFFER,ue,pe,_e.__webglTexture,de),t.bindFramebuffer(r.FRAMEBUFFER,null)}function Se(N,E,Z){if(r.bindRenderbuffer(r.RENDERBUFFER,N),E.depthBuffer){const ue=E.depthTexture,pe=ue&&ue.isDepthTexture?ue.type:null,de=b(E.stencilBuffer,pe),De=E.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Ee=at(E);dt(E)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,Ee,de,E.width,E.height):Z?r.renderbufferStorageMultisample(r.RENDERBUFFER,Ee,de,E.width,E.height):r.renderbufferStorage(r.RENDERBUFFER,de,E.width,E.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,De,r.RENDERBUFFER,N)}else{const ue=E.textures;for(let pe=0;pe<ue.length;pe++){const de=ue[pe],De=s.convert(de.format,de.colorSpace),Ee=s.convert(de.type),Re=P(de.internalFormat,De,Ee,de.colorSpace),ct=at(E);Z&&dt(E)===!1?r.renderbufferStorageMultisample(r.RENDERBUFFER,ct,Re,E.width,E.height):dt(E)?c.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,ct,Re,E.width,E.height):r.renderbufferStorage(r.RENDERBUFFER,Re,E.width,E.height)}}r.bindRenderbuffer(r.RENDERBUFFER,null)}function We(N,E){if(E&&E.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(r.FRAMEBUFFER,N),!(E.depthTexture&&E.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const ue=n.get(E.depthTexture);ue.__renderTarget=E,(!ue.__webglTexture||E.depthTexture.image.width!==E.width||E.depthTexture.image.height!==E.height)&&(E.depthTexture.image.width=E.width,E.depthTexture.image.height=E.height,E.depthTexture.needsUpdate=!0),ce(E.depthTexture,0);const pe=ue.__webglTexture,de=at(E);if(E.depthTexture.format===qs)dt(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,pe,0,de):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,pe,0);else if(E.depthTexture.format===to)dt(E)?c.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,pe,0,de):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,pe,0);else throw new Error("Unknown depthTexture format")}function tt(N){const E=n.get(N),Z=N.isWebGLCubeRenderTarget===!0;if(E.__boundDepthTexture!==N.depthTexture){const ue=N.depthTexture;if(E.__depthDisposeCallback&&E.__depthDisposeCallback(),ue){const pe=()=>{delete E.__boundDepthTexture,delete E.__depthDisposeCallback,ue.removeEventListener("dispose",pe)};ue.addEventListener("dispose",pe),E.__depthDisposeCallback=pe}E.__boundDepthTexture=ue}if(N.depthTexture&&!E.__autoAllocateDepthBuffer){if(Z)throw new Error("target.depthTexture not supported in Cube render targets");We(E.__webglFramebuffer,N)}else if(Z){E.__webglDepthbuffer=[];for(let ue=0;ue<6;ue++)if(t.bindFramebuffer(r.FRAMEBUFFER,E.__webglFramebuffer[ue]),E.__webglDepthbuffer[ue]===void 0)E.__webglDepthbuffer[ue]=r.createRenderbuffer(),Se(E.__webglDepthbuffer[ue],N,!1);else{const pe=N.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,de=E.__webglDepthbuffer[ue];r.bindRenderbuffer(r.RENDERBUFFER,de),r.framebufferRenderbuffer(r.FRAMEBUFFER,pe,r.RENDERBUFFER,de)}}else if(t.bindFramebuffer(r.FRAMEBUFFER,E.__webglFramebuffer),E.__webglDepthbuffer===void 0)E.__webglDepthbuffer=r.createRenderbuffer(),Se(E.__webglDepthbuffer,N,!1);else{const ue=N.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,pe=E.__webglDepthbuffer;r.bindRenderbuffer(r.RENDERBUFFER,pe),r.framebufferRenderbuffer(r.FRAMEBUFFER,ue,r.RENDERBUFFER,pe)}t.bindFramebuffer(r.FRAMEBUFFER,null)}function st(N,E,Z){const ue=n.get(N);E!==void 0&&Oe(ue.__webglFramebuffer,N,N.texture,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,0),Z!==void 0&&tt(N)}function Tt(N){const E=N.texture,Z=n.get(N),ue=n.get(E);N.addEventListener("dispose",O);const pe=N.textures,de=N.isWebGLCubeRenderTarget===!0,De=pe.length>1;if(De||(ue.__webglTexture===void 0&&(ue.__webglTexture=r.createTexture()),ue.__version=E.version,a.memory.textures++),de){Z.__webglFramebuffer=[];for(let Ee=0;Ee<6;Ee++)if(E.mipmaps&&E.mipmaps.length>0){Z.__webglFramebuffer[Ee]=[];for(let Re=0;Re<E.mipmaps.length;Re++)Z.__webglFramebuffer[Ee][Re]=r.createFramebuffer()}else Z.__webglFramebuffer[Ee]=r.createFramebuffer()}else{if(E.mipmaps&&E.mipmaps.length>0){Z.__webglFramebuffer=[];for(let Ee=0;Ee<E.mipmaps.length;Ee++)Z.__webglFramebuffer[Ee]=r.createFramebuffer()}else Z.__webglFramebuffer=r.createFramebuffer();if(De)for(let Ee=0,Re=pe.length;Ee<Re;Ee++){const ct=n.get(pe[Ee]);ct.__webglTexture===void 0&&(ct.__webglTexture=r.createTexture(),a.memory.textures++)}if(N.samples>0&&dt(N)===!1){Z.__webglMultisampledFramebuffer=r.createFramebuffer(),Z.__webglColorRenderbuffer=[],t.bindFramebuffer(r.FRAMEBUFFER,Z.__webglMultisampledFramebuffer);for(let Ee=0;Ee<pe.length;Ee++){const Re=pe[Ee];Z.__webglColorRenderbuffer[Ee]=r.createRenderbuffer(),r.bindRenderbuffer(r.RENDERBUFFER,Z.__webglColorRenderbuffer[Ee]);const ct=s.convert(Re.format,Re.colorSpace),_e=s.convert(Re.type),Ce=P(Re.internalFormat,ct,_e,Re.colorSpace,N.isXRRenderTarget===!0),Ue=at(N);r.renderbufferStorageMultisample(r.RENDERBUFFER,Ue,Ce,N.width,N.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Ee,r.RENDERBUFFER,Z.__webglColorRenderbuffer[Ee])}r.bindRenderbuffer(r.RENDERBUFFER,null),N.depthBuffer&&(Z.__webglDepthRenderbuffer=r.createRenderbuffer(),Se(Z.__webglDepthRenderbuffer,N,!0)),t.bindFramebuffer(r.FRAMEBUFFER,null)}}if(de){t.bindTexture(r.TEXTURE_CUBE_MAP,ue.__webglTexture),Ze(r.TEXTURE_CUBE_MAP,E);for(let Ee=0;Ee<6;Ee++)if(E.mipmaps&&E.mipmaps.length>0)for(let Re=0;Re<E.mipmaps.length;Re++)Oe(Z.__webglFramebuffer[Ee][Re],N,E,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Ee,Re);else Oe(Z.__webglFramebuffer[Ee],N,E,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+Ee,0);v(E)&&_(r.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(De){for(let Ee=0,Re=pe.length;Ee<Re;Ee++){const ct=pe[Ee],_e=n.get(ct);t.bindTexture(r.TEXTURE_2D,_e.__webglTexture),Ze(r.TEXTURE_2D,ct),Oe(Z.__webglFramebuffer,N,ct,r.COLOR_ATTACHMENT0+Ee,r.TEXTURE_2D,0),v(ct)&&_(r.TEXTURE_2D)}t.unbindTexture()}else{let Ee=r.TEXTURE_2D;if((N.isWebGL3DRenderTarget||N.isWebGLArrayRenderTarget)&&(Ee=N.isWebGL3DRenderTarget?r.TEXTURE_3D:r.TEXTURE_2D_ARRAY),t.bindTexture(Ee,ue.__webglTexture),Ze(Ee,E),E.mipmaps&&E.mipmaps.length>0)for(let Re=0;Re<E.mipmaps.length;Re++)Oe(Z.__webglFramebuffer[Re],N,E,r.COLOR_ATTACHMENT0,Ee,Re);else Oe(Z.__webglFramebuffer,N,E,r.COLOR_ATTACHMENT0,Ee,0);v(E)&&_(Ee),t.unbindTexture()}N.depthBuffer&&tt(N)}function ot(N){const E=N.textures;for(let Z=0,ue=E.length;Z<ue;Z++){const pe=E[Z];if(v(pe)){const de=A(N),De=n.get(pe).__webglTexture;t.bindTexture(de,De),_(de),t.unbindTexture()}}}const Ot=[],X=[];function Qt(N){if(N.samples>0){if(dt(N)===!1){const E=N.textures,Z=N.width,ue=N.height;let pe=r.COLOR_BUFFER_BIT;const de=N.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,De=n.get(N),Ee=E.length>1;if(Ee)for(let Re=0;Re<E.length;Re++)t.bindFramebuffer(r.FRAMEBUFFER,De.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Re,r.RENDERBUFFER,null),t.bindFramebuffer(r.FRAMEBUFFER,De.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+Re,r.TEXTURE_2D,null,0);t.bindFramebuffer(r.READ_FRAMEBUFFER,De.__webglMultisampledFramebuffer),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,De.__webglFramebuffer);for(let Re=0;Re<E.length;Re++){if(N.resolveDepthBuffer&&(N.depthBuffer&&(pe|=r.DEPTH_BUFFER_BIT),N.stencilBuffer&&N.resolveStencilBuffer&&(pe|=r.STENCIL_BUFFER_BIT)),Ee){r.framebufferRenderbuffer(r.READ_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.RENDERBUFFER,De.__webglColorRenderbuffer[Re]);const ct=n.get(E[Re]).__webglTexture;r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,ct,0)}r.blitFramebuffer(0,0,Z,ue,0,0,Z,ue,pe,r.NEAREST),u===!0&&(Ot.length=0,X.length=0,Ot.push(r.COLOR_ATTACHMENT0+Re),N.depthBuffer&&N.resolveDepthBuffer===!1&&(Ot.push(de),X.push(de),r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,X)),r.invalidateFramebuffer(r.READ_FRAMEBUFFER,Ot))}if(t.bindFramebuffer(r.READ_FRAMEBUFFER,null),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),Ee)for(let Re=0;Re<E.length;Re++){t.bindFramebuffer(r.FRAMEBUFFER,De.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+Re,r.RENDERBUFFER,De.__webglColorRenderbuffer[Re]);const ct=n.get(E[Re]).__webglTexture;t.bindFramebuffer(r.FRAMEBUFFER,De.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+Re,r.TEXTURE_2D,ct,0)}t.bindFramebuffer(r.DRAW_FRAMEBUFFER,De.__webglMultisampledFramebuffer)}else if(N.depthBuffer&&N.resolveDepthBuffer===!1&&u){const E=N.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT;r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,[E])}}}function at(N){return Math.min(i.maxSamples,N.samples)}function dt(N){const E=n.get(N);return N.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&E.__useRenderToTexture!==!1}function Ve(N){const E=a.render.frame;f.get(N)!==E&&(f.set(N,E),N.update())}function xt(N,E){const Z=N.colorSpace,ue=N.format,pe=N.type;return N.isCompressedTexture===!0||N.isVideoTexture===!0||Z!==Fn&&Z!==gr&&(Mt.getTransfer(Z)===Ut?(ue!==ai||pe!==$i)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",Z)),E}function Fe(N){return typeof HTMLImageElement<"u"&&N instanceof HTMLImageElement?(h.width=N.naturalWidth||N.width,h.height=N.naturalHeight||N.height):typeof VideoFrame<"u"&&N instanceof VideoFrame?(h.width=N.displayWidth,h.height=N.displayHeight):(h.width=N.width,h.height=N.height),h}this.allocateTextureUnit=Q,this.resetTextureUnits=ee,this.setTexture2D=ce,this.setTexture2DArray=$,this.setTexture3D=fe,this.setTextureCube=re,this.rebindTextures=st,this.setupRenderTarget=Tt,this.updateRenderTargetMipmap=ot,this.updateMultisampleRenderTarget=Qt,this.setupDepthRenderbuffer=tt,this.setupFrameBufferTexture=Oe,this.useMultisampledRTT=dt}function mR(r,e){function t(n,i=gr){let s;const a=Mt.getTransfer(i);if(n===$i)return r.UNSIGNED_BYTE;if(n===ud)return r.UNSIGNED_SHORT_4_4_4_4;if(n===hd)return r.UNSIGNED_SHORT_5_5_5_1;if(n===_g)return r.UNSIGNED_INT_5_9_9_9_REV;if(n===mg)return r.BYTE;if(n===gg)return r.SHORT;if(n===Jo)return r.UNSIGNED_SHORT;if(n===ld)return r.INT;if(n===rs)return r.UNSIGNED_INT;if(n===gi)return r.FLOAT;if(n===na)return r.HALF_FLOAT;if(n===vg)return r.ALPHA;if(n===yg)return r.RGB;if(n===ai)return r.RGBA;if(n===xg)return r.LUMINANCE;if(n===bg)return r.LUMINANCE_ALPHA;if(n===qs)return r.DEPTH_COMPONENT;if(n===to)return r.DEPTH_STENCIL;if(n===dd)return r.RED;if(n===fd)return r.RED_INTEGER;if(n===Sg)return r.RG;if(n===pd)return r.RG_INTEGER;if(n===md)return r.RGBA_INTEGER;if(n===Tc||n===Ec||n===Ac||n===wc)if(a===Ut)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===Tc)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Ec)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Ac)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===wc)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===Tc)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Ec)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Ac)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===wc)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===wh||n===Ph||n===Rh||n===Ch)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===wh)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Ph)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Rh)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Ch)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Ih||n===Lh||n===Dh)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===Ih||n===Lh)return a===Ut?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===Dh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Nh||n===Oh||n===Uh||n===Fh||n===Bh||n===kh||n===zh||n===Hh||n===Vh||n===Gh||n===Wh||n===jh||n===Xh||n===qh)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===Nh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Oh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Uh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Fh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Bh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===kh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===zh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Hh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Vh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Gh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Wh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===jh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Xh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===qh)return a===Ut?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Pc||n===Yh||n===Kh)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===Pc)return a===Ut?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Yh)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Kh)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Mg||n===Zh||n===$h||n===Jh)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===Pc)return s.COMPRESSED_RED_RGTC1_EXT;if(n===Zh)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===$h)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Jh)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===eo?r.UNSIGNED_INT_24_8:r[n]!==void 0?r[n]:null}return{convert:t}}class gR extends On{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Yi extends Xt{constructor(){super(),this.isGroup=!0,this.type="Group"}}const _R={type:"move"};class Zu{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Yi,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Yi,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new F,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new F),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Yi,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new F,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new F),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,s=null,a=null;const c=this._targetRay,u=this._grip,h=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(h&&e.hand){a=!0;for(const M of e.hand.values()){const v=t.getJointPose(M,n),_=this._getHandJoint(h,M);v!==null&&(_.matrix.fromArray(v.transform.matrix),_.matrix.decompose(_.position,_.rotation,_.scale),_.matrixWorldNeedsUpdate=!0,_.jointRadius=v.radius),_.visible=v!==null}const f=h.joints["index-finger-tip"],p=h.joints["thumb-tip"],m=f.position.distanceTo(p.position),g=.02,x=.005;h.inputState.pinching&&m>g+x?(h.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!h.inputState.pinching&&m<=g-x&&(h.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else u!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(u.matrix.fromArray(s.transform.matrix),u.matrix.decompose(u.position,u.rotation,u.scale),u.matrixWorldNeedsUpdate=!0,s.linearVelocity?(u.hasLinearVelocity=!0,u.linearVelocity.copy(s.linearVelocity)):u.hasLinearVelocity=!1,s.angularVelocity?(u.hasAngularVelocity=!0,u.angularVelocity.copy(s.angularVelocity)):u.hasAngularVelocity=!1));c!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&s!==null&&(i=s),i!==null&&(c.matrix.fromArray(i.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,i.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(i.linearVelocity)):c.hasLinearVelocity=!1,i.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(i.angularVelocity)):c.hasAngularVelocity=!1,this.dispatchEvent(_R)))}return c!==null&&(c.visible=i!==null),u!==null&&(u.visible=s!==null),h!==null&&(h.visible=a!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Yi;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const vR=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,yR=`
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

}`;class xR{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const i=new vn,s=e.properties.get(i);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new br({vertexShader:vR,fragmentShader:yR,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Te(new ao(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class bR extends Sr{constructor(e,t){super();const n=this;let i=null,s=1,a=null,c="local-floor",u=1,h=null,f=null,p=null,m=null,g=null,x=null;const M=new xR,v=t.getContextAttributes();let _=null,A=null;const P=[],b=[],B=new Qe;let U=null;const O=new On;O.viewport=new Pt;const z=new On;z.viewport=new Pt;const I=[O,z],w=new gR;let H=null,ee=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(le){let ge=P[le];return ge===void 0&&(ge=new Zu,P[le]=ge),ge.getTargetRaySpace()},this.getControllerGrip=function(le){let ge=P[le];return ge===void 0&&(ge=new Zu,P[le]=ge),ge.getGripSpace()},this.getHand=function(le){let ge=P[le];return ge===void 0&&(ge=new Zu,P[le]=ge),ge.getHandSpace()};function Q(le){const ge=b.indexOf(le.inputSource);if(ge===-1)return;const Oe=P[ge];Oe!==void 0&&(Oe.update(le.inputSource,le.frame,h||a),Oe.dispatchEvent({type:le.type,data:le.inputSource}))}function ae(){i.removeEventListener("select",Q),i.removeEventListener("selectstart",Q),i.removeEventListener("selectend",Q),i.removeEventListener("squeeze",Q),i.removeEventListener("squeezestart",Q),i.removeEventListener("squeezeend",Q),i.removeEventListener("end",ae),i.removeEventListener("inputsourceschange",ce);for(let le=0;le<P.length;le++){const ge=b[le];ge!==null&&(b[le]=null,P[le].disconnect(ge))}H=null,ee=null,M.reset(),e.setRenderTarget(_),g=null,m=null,p=null,i=null,A=null,ht.stop(),n.isPresenting=!1,e.setPixelRatio(U),e.setSize(B.width,B.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(le){s=le,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(le){c=le,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return h||a},this.setReferenceSpace=function(le){h=le},this.getBaseLayer=function(){return m!==null?m:g},this.getBinding=function(){return p},this.getFrame=function(){return x},this.getSession=function(){return i},this.setSession=async function(le){if(i=le,i!==null){if(_=e.getRenderTarget(),i.addEventListener("select",Q),i.addEventListener("selectstart",Q),i.addEventListener("selectend",Q),i.addEventListener("squeeze",Q),i.addEventListener("squeezestart",Q),i.addEventListener("squeezeend",Q),i.addEventListener("end",ae),i.addEventListener("inputsourceschange",ce),v.xrCompatible!==!0&&await t.makeXRCompatible(),U=e.getPixelRatio(),e.getSize(B),i.renderState.layers===void 0){const ge={antialias:v.antialias,alpha:!0,depth:v.depth,stencil:v.stencil,framebufferScaleFactor:s};g=new XRWebGLLayer(i,t,ge),i.updateRenderState({baseLayer:g}),e.setPixelRatio(1),e.setSize(g.framebufferWidth,g.framebufferHeight,!1),A=new ss(g.framebufferWidth,g.framebufferHeight,{format:ai,type:$i,colorSpace:e.outputColorSpace,stencilBuffer:v.stencil})}else{let ge=null,Oe=null,Se=null;v.depth&&(Se=v.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,ge=v.stencil?to:qs,Oe=v.stencil?eo:rs);const We={colorFormat:t.RGBA8,depthFormat:Se,scaleFactor:s};p=new XRWebGLBinding(i,t),m=p.createProjectionLayer(We),i.updateRenderState({layers:[m]}),e.setPixelRatio(1),e.setSize(m.textureWidth,m.textureHeight,!1),A=new ss(m.textureWidth,m.textureHeight,{format:ai,type:$i,depthTexture:new Bg(m.textureWidth,m.textureHeight,Oe,void 0,void 0,void 0,void 0,void 0,void 0,ge),stencilBuffer:v.stencil,colorSpace:e.outputColorSpace,samples:v.antialias?4:0,resolveDepthBuffer:m.ignoreDepthValues===!1})}A.isXRRenderTarget=!0,this.setFoveation(u),h=null,a=await i.requestReferenceSpace(c),ht.setContext(i),ht.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(i!==null)return i.environmentBlendMode},this.getDepthTexture=function(){return M.getDepthTexture()};function ce(le){for(let ge=0;ge<le.removed.length;ge++){const Oe=le.removed[ge],Se=b.indexOf(Oe);Se>=0&&(b[Se]=null,P[Se].disconnect(Oe))}for(let ge=0;ge<le.added.length;ge++){const Oe=le.added[ge];let Se=b.indexOf(Oe);if(Se===-1){for(let tt=0;tt<P.length;tt++)if(tt>=b.length){b.push(Oe),Se=tt;break}else if(b[tt]===null){b[tt]=Oe,Se=tt;break}if(Se===-1)break}const We=P[Se];We&&We.connect(Oe)}}const $=new F,fe=new F;function re(le,ge,Oe){$.setFromMatrixPosition(ge.matrixWorld),fe.setFromMatrixPosition(Oe.matrixWorld);const Se=$.distanceTo(fe),We=ge.projectionMatrix.elements,tt=Oe.projectionMatrix.elements,st=We[14]/(We[10]-1),Tt=We[14]/(We[10]+1),ot=(We[9]+1)/We[5],Ot=(We[9]-1)/We[5],X=(We[8]-1)/We[0],Qt=(tt[8]+1)/tt[0],at=st*X,dt=st*Qt,Ve=Se/(-X+Qt),xt=Ve*-X;if(ge.matrixWorld.decompose(le.position,le.quaternion,le.scale),le.translateX(xt),le.translateZ(Ve),le.matrixWorld.compose(le.position,le.quaternion,le.scale),le.matrixWorldInverse.copy(le.matrixWorld).invert(),We[10]===-1)le.projectionMatrix.copy(ge.projectionMatrix),le.projectionMatrixInverse.copy(ge.projectionMatrixInverse);else{const Fe=st+Ve,N=Tt+Ve,E=at-xt,Z=dt+(Se-xt),ue=ot*Tt/N*Fe,pe=Ot*Tt/N*Fe;le.projectionMatrix.makePerspective(E,Z,ue,pe,Fe,N),le.projectionMatrixInverse.copy(le.projectionMatrix).invert()}}function ye(le,ge){ge===null?le.matrixWorld.copy(le.matrix):le.matrixWorld.multiplyMatrices(ge.matrixWorld,le.matrix),le.matrixWorldInverse.copy(le.matrixWorld).invert()}this.updateCamera=function(le){if(i===null)return;let ge=le.near,Oe=le.far;M.texture!==null&&(M.depthNear>0&&(ge=M.depthNear),M.depthFar>0&&(Oe=M.depthFar)),w.near=z.near=O.near=ge,w.far=z.far=O.far=Oe,(H!==w.near||ee!==w.far)&&(i.updateRenderState({depthNear:w.near,depthFar:w.far}),H=w.near,ee=w.far),O.layers.mask=le.layers.mask|2,z.layers.mask=le.layers.mask|4,w.layers.mask=O.layers.mask|z.layers.mask;const Se=le.parent,We=w.cameras;ye(w,Se);for(let tt=0;tt<We.length;tt++)ye(We[tt],Se);We.length===2?re(w,O,z):w.projectionMatrix.copy(O.projectionMatrix),Me(le,w,Se)};function Me(le,ge,Oe){Oe===null?le.matrix.copy(ge.matrixWorld):(le.matrix.copy(Oe.matrixWorld),le.matrix.invert(),le.matrix.multiply(ge.matrixWorld)),le.matrix.decompose(le.position,le.quaternion,le.scale),le.updateMatrixWorld(!0),le.projectionMatrix.copy(ge.projectionMatrix),le.projectionMatrixInverse.copy(ge.projectionMatrixInverse),le.isPerspectiveCamera&&(le.fov=no*2*Math.atan(1/le.projectionMatrix.elements[5]),le.zoom=1)}this.getCamera=function(){return w},this.getFoveation=function(){if(!(m===null&&g===null))return u},this.setFoveation=function(le){u=le,m!==null&&(m.fixedFoveation=le),g!==null&&g.fixedFoveation!==void 0&&(g.fixedFoveation=le)},this.hasDepthSensing=function(){return M.texture!==null},this.getDepthSensingMesh=function(){return M.getMesh(w)};let Ne=null;function Ze(le,ge){if(f=ge.getViewerPose(h||a),x=ge,f!==null){const Oe=f.views;g!==null&&(e.setRenderTargetFramebuffer(A,g.framebuffer),e.setRenderTarget(A));let Se=!1;Oe.length!==w.cameras.length&&(w.cameras.length=0,Se=!0);for(let tt=0;tt<Oe.length;tt++){const st=Oe[tt];let Tt=null;if(g!==null)Tt=g.getViewport(st);else{const Ot=p.getViewSubImage(m,st);Tt=Ot.viewport,tt===0&&(e.setRenderTargetTextures(A,Ot.colorTexture,m.ignoreDepthValues?void 0:Ot.depthStencilTexture),e.setRenderTarget(A))}let ot=I[tt];ot===void 0&&(ot=new On,ot.layers.enable(tt),ot.viewport=new Pt,I[tt]=ot),ot.matrix.fromArray(st.transform.matrix),ot.matrix.decompose(ot.position,ot.quaternion,ot.scale),ot.projectionMatrix.fromArray(st.projectionMatrix),ot.projectionMatrixInverse.copy(ot.projectionMatrix).invert(),ot.viewport.set(Tt.x,Tt.y,Tt.width,Tt.height),tt===0&&(w.matrix.copy(ot.matrix),w.matrix.decompose(w.position,w.quaternion,w.scale)),Se===!0&&w.cameras.push(ot)}const We=i.enabledFeatures;if(We&&We.includes("depth-sensing")){const tt=p.getDepthInformation(Oe[0]);tt&&tt.isValid&&tt.texture&&M.init(e,tt,i.renderState)}}for(let Oe=0;Oe<P.length;Oe++){const Se=b[Oe],We=P[Oe];Se!==null&&We!==void 0&&We.update(Se,ge,h||a)}Ne&&Ne(le,ge),ge.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:ge}),x=null}const ht=new Fg;ht.setAnimationLoop(Ze),this.setAnimationLoop=function(le){Ne=le},this.dispose=function(){}}}const Zr=new vi,SR=new rt;function MR(r,e){function t(v,_){v.matrixAutoUpdate===!0&&v.updateMatrix(),_.value.copy(v.matrix)}function n(v,_){_.color.getRGB(v.fogColor.value,Ng(r)),_.isFog?(v.fogNear.value=_.near,v.fogFar.value=_.far):_.isFogExp2&&(v.fogDensity.value=_.density)}function i(v,_,A,P,b){_.isMeshBasicMaterial||_.isMeshLambertMaterial?s(v,_):_.isMeshToonMaterial?(s(v,_),p(v,_)):_.isMeshPhongMaterial?(s(v,_),f(v,_)):_.isMeshStandardMaterial?(s(v,_),m(v,_),_.isMeshPhysicalMaterial&&g(v,_,b)):_.isMeshMatcapMaterial?(s(v,_),x(v,_)):_.isMeshDepthMaterial?s(v,_):_.isMeshDistanceMaterial?(s(v,_),M(v,_)):_.isMeshNormalMaterial?s(v,_):_.isLineBasicMaterial?(a(v,_),_.isLineDashedMaterial&&c(v,_)):_.isPointsMaterial?u(v,_,A,P):_.isSpriteMaterial?h(v,_):_.isShadowMaterial?(v.color.value.copy(_.color),v.opacity.value=_.opacity):_.isShaderMaterial&&(_.uniformsNeedUpdate=!1)}function s(v,_){v.opacity.value=_.opacity,_.color&&v.diffuse.value.copy(_.color),_.emissive&&v.emissive.value.copy(_.emissive).multiplyScalar(_.emissiveIntensity),_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.bumpMap&&(v.bumpMap.value=_.bumpMap,t(_.bumpMap,v.bumpMapTransform),v.bumpScale.value=_.bumpScale,_.side===Wn&&(v.bumpScale.value*=-1)),_.normalMap&&(v.normalMap.value=_.normalMap,t(_.normalMap,v.normalMapTransform),v.normalScale.value.copy(_.normalScale),_.side===Wn&&v.normalScale.value.negate()),_.displacementMap&&(v.displacementMap.value=_.displacementMap,t(_.displacementMap,v.displacementMapTransform),v.displacementScale.value=_.displacementScale,v.displacementBias.value=_.displacementBias),_.emissiveMap&&(v.emissiveMap.value=_.emissiveMap,t(_.emissiveMap,v.emissiveMapTransform)),_.specularMap&&(v.specularMap.value=_.specularMap,t(_.specularMap,v.specularMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest);const A=e.get(_),P=A.envMap,b=A.envMapRotation;P&&(v.envMap.value=P,Zr.copy(b),Zr.x*=-1,Zr.y*=-1,Zr.z*=-1,P.isCubeTexture&&P.isRenderTargetTexture===!1&&(Zr.y*=-1,Zr.z*=-1),v.envMapRotation.value.setFromMatrix4(SR.makeRotationFromEuler(Zr)),v.flipEnvMap.value=P.isCubeTexture&&P.isRenderTargetTexture===!1?-1:1,v.reflectivity.value=_.reflectivity,v.ior.value=_.ior,v.refractionRatio.value=_.refractionRatio),_.lightMap&&(v.lightMap.value=_.lightMap,v.lightMapIntensity.value=_.lightMapIntensity,t(_.lightMap,v.lightMapTransform)),_.aoMap&&(v.aoMap.value=_.aoMap,v.aoMapIntensity.value=_.aoMapIntensity,t(_.aoMap,v.aoMapTransform))}function a(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform))}function c(v,_){v.dashSize.value=_.dashSize,v.totalSize.value=_.dashSize+_.gapSize,v.scale.value=_.scale}function u(v,_,A,P){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.size.value=_.size*A,v.scale.value=P*.5,_.map&&(v.map.value=_.map,t(_.map,v.uvTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function h(v,_){v.diffuse.value.copy(_.color),v.opacity.value=_.opacity,v.rotation.value=_.rotation,_.map&&(v.map.value=_.map,t(_.map,v.mapTransform)),_.alphaMap&&(v.alphaMap.value=_.alphaMap,t(_.alphaMap,v.alphaMapTransform)),_.alphaTest>0&&(v.alphaTest.value=_.alphaTest)}function f(v,_){v.specular.value.copy(_.specular),v.shininess.value=Math.max(_.shininess,1e-4)}function p(v,_){_.gradientMap&&(v.gradientMap.value=_.gradientMap)}function m(v,_){v.metalness.value=_.metalness,_.metalnessMap&&(v.metalnessMap.value=_.metalnessMap,t(_.metalnessMap,v.metalnessMapTransform)),v.roughness.value=_.roughness,_.roughnessMap&&(v.roughnessMap.value=_.roughnessMap,t(_.roughnessMap,v.roughnessMapTransform)),_.envMap&&(v.envMapIntensity.value=_.envMapIntensity)}function g(v,_,A){v.ior.value=_.ior,_.sheen>0&&(v.sheenColor.value.copy(_.sheenColor).multiplyScalar(_.sheen),v.sheenRoughness.value=_.sheenRoughness,_.sheenColorMap&&(v.sheenColorMap.value=_.sheenColorMap,t(_.sheenColorMap,v.sheenColorMapTransform)),_.sheenRoughnessMap&&(v.sheenRoughnessMap.value=_.sheenRoughnessMap,t(_.sheenRoughnessMap,v.sheenRoughnessMapTransform))),_.clearcoat>0&&(v.clearcoat.value=_.clearcoat,v.clearcoatRoughness.value=_.clearcoatRoughness,_.clearcoatMap&&(v.clearcoatMap.value=_.clearcoatMap,t(_.clearcoatMap,v.clearcoatMapTransform)),_.clearcoatRoughnessMap&&(v.clearcoatRoughnessMap.value=_.clearcoatRoughnessMap,t(_.clearcoatRoughnessMap,v.clearcoatRoughnessMapTransform)),_.clearcoatNormalMap&&(v.clearcoatNormalMap.value=_.clearcoatNormalMap,t(_.clearcoatNormalMap,v.clearcoatNormalMapTransform),v.clearcoatNormalScale.value.copy(_.clearcoatNormalScale),_.side===Wn&&v.clearcoatNormalScale.value.negate())),_.dispersion>0&&(v.dispersion.value=_.dispersion),_.iridescence>0&&(v.iridescence.value=_.iridescence,v.iridescenceIOR.value=_.iridescenceIOR,v.iridescenceThicknessMinimum.value=_.iridescenceThicknessRange[0],v.iridescenceThicknessMaximum.value=_.iridescenceThicknessRange[1],_.iridescenceMap&&(v.iridescenceMap.value=_.iridescenceMap,t(_.iridescenceMap,v.iridescenceMapTransform)),_.iridescenceThicknessMap&&(v.iridescenceThicknessMap.value=_.iridescenceThicknessMap,t(_.iridescenceThicknessMap,v.iridescenceThicknessMapTransform))),_.transmission>0&&(v.transmission.value=_.transmission,v.transmissionSamplerMap.value=A.texture,v.transmissionSamplerSize.value.set(A.width,A.height),_.transmissionMap&&(v.transmissionMap.value=_.transmissionMap,t(_.transmissionMap,v.transmissionMapTransform)),v.thickness.value=_.thickness,_.thicknessMap&&(v.thicknessMap.value=_.thicknessMap,t(_.thicknessMap,v.thicknessMapTransform)),v.attenuationDistance.value=_.attenuationDistance,v.attenuationColor.value.copy(_.attenuationColor)),_.anisotropy>0&&(v.anisotropyVector.value.set(_.anisotropy*Math.cos(_.anisotropyRotation),_.anisotropy*Math.sin(_.anisotropyRotation)),_.anisotropyMap&&(v.anisotropyMap.value=_.anisotropyMap,t(_.anisotropyMap,v.anisotropyMapTransform))),v.specularIntensity.value=_.specularIntensity,v.specularColor.value.copy(_.specularColor),_.specularColorMap&&(v.specularColorMap.value=_.specularColorMap,t(_.specularColorMap,v.specularColorMapTransform)),_.specularIntensityMap&&(v.specularIntensityMap.value=_.specularIntensityMap,t(_.specularIntensityMap,v.specularIntensityMapTransform))}function x(v,_){_.matcap&&(v.matcap.value=_.matcap)}function M(v,_){const A=e.get(_).light;v.referencePosition.value.setFromMatrixPosition(A.matrixWorld),v.nearDistance.value=A.shadow.camera.near,v.farDistance.value=A.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:i}}function TR(r,e,t,n){let i={},s={},a=[];const c=r.getParameter(r.MAX_UNIFORM_BUFFER_BINDINGS);function u(A,P){const b=P.program;n.uniformBlockBinding(A,b)}function h(A,P){let b=i[A.id];b===void 0&&(x(A),b=f(A),i[A.id]=b,A.addEventListener("dispose",v));const B=P.program;n.updateUBOMapping(A,B);const U=e.render.frame;s[A.id]!==U&&(m(A),s[A.id]=U)}function f(A){const P=p();A.__bindingPointIndex=P;const b=r.createBuffer(),B=A.__size,U=A.usage;return r.bindBuffer(r.UNIFORM_BUFFER,b),r.bufferData(r.UNIFORM_BUFFER,B,U),r.bindBuffer(r.UNIFORM_BUFFER,null),r.bindBufferBase(r.UNIFORM_BUFFER,P,b),b}function p(){for(let A=0;A<c;A++)if(a.indexOf(A)===-1)return a.push(A),A;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function m(A){const P=i[A.id],b=A.uniforms,B=A.__cache;r.bindBuffer(r.UNIFORM_BUFFER,P);for(let U=0,O=b.length;U<O;U++){const z=Array.isArray(b[U])?b[U]:[b[U]];for(let I=0,w=z.length;I<w;I++){const H=z[I];if(g(H,U,I,B)===!0){const ee=H.__offset,Q=Array.isArray(H.value)?H.value:[H.value];let ae=0;for(let ce=0;ce<Q.length;ce++){const $=Q[ce],fe=M($);typeof $=="number"||typeof $=="boolean"?(H.__data[0]=$,r.bufferSubData(r.UNIFORM_BUFFER,ee+ae,H.__data)):$.isMatrix3?(H.__data[0]=$.elements[0],H.__data[1]=$.elements[1],H.__data[2]=$.elements[2],H.__data[3]=0,H.__data[4]=$.elements[3],H.__data[5]=$.elements[4],H.__data[6]=$.elements[5],H.__data[7]=0,H.__data[8]=$.elements[6],H.__data[9]=$.elements[7],H.__data[10]=$.elements[8],H.__data[11]=0):($.toArray(H.__data,ae),ae+=fe.storage/Float32Array.BYTES_PER_ELEMENT)}r.bufferSubData(r.UNIFORM_BUFFER,ee,H.__data)}}}r.bindBuffer(r.UNIFORM_BUFFER,null)}function g(A,P,b,B){const U=A.value,O=P+"_"+b;if(B[O]===void 0)return typeof U=="number"||typeof U=="boolean"?B[O]=U:B[O]=U.clone(),!0;{const z=B[O];if(typeof U=="number"||typeof U=="boolean"){if(z!==U)return B[O]=U,!0}else if(z.equals(U)===!1)return z.copy(U),!0}return!1}function x(A){const P=A.uniforms;let b=0;const B=16;for(let O=0,z=P.length;O<z;O++){const I=Array.isArray(P[O])?P[O]:[P[O]];for(let w=0,H=I.length;w<H;w++){const ee=I[w],Q=Array.isArray(ee.value)?ee.value:[ee.value];for(let ae=0,ce=Q.length;ae<ce;ae++){const $=Q[ae],fe=M($),re=b%B,ye=re%fe.boundary,Me=re+ye;b+=ye,Me!==0&&B-Me<fe.storage&&(b+=B-Me),ee.__data=new Float32Array(fe.storage/Float32Array.BYTES_PER_ELEMENT),ee.__offset=b,b+=fe.storage}}}const U=b%B;return U>0&&(b+=B-U),A.__size=b,A.__cache={},this}function M(A){const P={boundary:0,storage:0};return typeof A=="number"||typeof A=="boolean"?(P.boundary=4,P.storage=4):A.isVector2?(P.boundary=8,P.storage=8):A.isVector3||A.isColor?(P.boundary=16,P.storage=12):A.isVector4?(P.boundary=16,P.storage=16):A.isMatrix3?(P.boundary=48,P.storage=48):A.isMatrix4?(P.boundary=64,P.storage=64):A.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",A),P}function v(A){const P=A.target;P.removeEventListener("dispose",v);const b=a.indexOf(P.__bindingPointIndex);a.splice(b,1),r.deleteBuffer(i[P.id]),delete i[P.id],delete s[P.id]}function _(){for(const A in i)r.deleteBuffer(i[A]);a=[],i={},s={}}return{bind:u,update:h,dispose:_}}class ER{constructor(e={}){const{canvas:t=fE(),context:n=null,depth:i=!0,stencil:s=!1,alpha:a=!1,antialias:c=!1,premultipliedAlpha:u=!0,preserveDrawingBuffer:h=!1,powerPreference:f="default",failIfMajorPerformanceCaveat:p=!1,reverseDepthBuffer:m=!1}=e;this.isWebGLRenderer=!0;let g;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");g=n.getContextAttributes().alpha}else g=a;const x=new Uint32Array(4),M=new Int32Array(4);let v=null,_=null;const A=[],P=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=_n,this.toneMapping=xr,this.toneMappingExposure=1;const b=this;let B=!1,U=0,O=0,z=null,I=-1,w=null;const H=new Pt,ee=new Pt;let Q=null;const ae=new qe(0);let ce=0,$=t.width,fe=t.height,re=1,ye=null,Me=null;const Ne=new Pt(0,0,$,fe),Ze=new Pt(0,0,$,fe);let ht=!1;const le=new xd;let ge=!1,Oe=!1;const Se=new rt,We=new rt,tt=new F,st=new Pt,Tt={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let ot=!1;function Ot(){return z===null?re:1}let X=n;function Qt(R,j){return t.getContext(R,j)}try{const R={alpha:!0,depth:i,stencil:s,antialias:c,premultipliedAlpha:u,preserveDrawingBuffer:h,powerPreference:f,failIfMajorPerformanceCaveat:p};if("setAttribute"in t&&t.setAttribute("data-engine","three.js r170"),t.addEventListener("webglcontextlost",ie,!1),t.addEventListener("webglcontextrestored",he,!1),t.addEventListener("webglcontextcreationerror",me,!1),X===null){const j="webgl2";if(X=Qt(j,R),X===null)throw Qt(j)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(R){throw console.error("THREE.WebGLRenderer: "+R.message),R}let at,dt,Ve,xt,Fe,N,E,Z,ue,pe,de,De,Ee,Re,ct,_e,Ce,Ue,Ye,Ie,pt,it,V,L;function J(){at=new C1(X),at.init(),it=new mR(X,at),dt=new T1(X,at,e,it),Ve=new dR(X,at),dt.reverseDepthBuffer&&m&&Ve.buffers.depth.setReversed(!0),xt=new D1(X),Fe=new $P,N=new pR(X,at,Ve,Fe,dt,it,xt),E=new A1(b),Z=new R1(b),ue=new zE(X),V=new S1(X,ue),pe=new I1(X,ue,xt,V),de=new O1(X,pe,ue,xt),Ye=new N1(X,dt,N),_e=new E1(Fe),De=new ZP(b,E,Z,at,dt,V,_e),Ee=new MR(b,Fe),Re=new QP,ct=new sR(at),Ue=new b1(b,E,Z,Ve,de,g,u),Ce=new uR(b,de,dt),L=new TR(X,xt,dt,Ve),Ie=new M1(X,at,xt),pt=new L1(X,at,xt),xt.programs=De.programs,b.capabilities=dt,b.extensions=at,b.properties=Fe,b.renderLists=Re,b.shadowMap=Ce,b.state=Ve,b.info=xt}J();const W=new bR(b,X);this.xr=W,this.getContext=function(){return X},this.getContextAttributes=function(){return X.getContextAttributes()},this.forceContextLoss=function(){const R=at.get("WEBGL_lose_context");R&&R.loseContext()},this.forceContextRestore=function(){const R=at.get("WEBGL_lose_context");R&&R.restoreContext()},this.getPixelRatio=function(){return re},this.setPixelRatio=function(R){R!==void 0&&(re=R,this.setSize($,fe,!1))},this.getSize=function(R){return R.set($,fe)},this.setSize=function(R,j,te=!0){if(W.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}$=R,fe=j,t.width=Math.floor(R*re),t.height=Math.floor(j*re),te===!0&&(t.style.width=R+"px",t.style.height=j+"px"),this.setViewport(0,0,R,j)},this.getDrawingBufferSize=function(R){return R.set($*re,fe*re).floor()},this.setDrawingBufferSize=function(R,j,te){$=R,fe=j,re=te,t.width=Math.floor(R*te),t.height=Math.floor(j*te),this.setViewport(0,0,R,j)},this.getCurrentViewport=function(R){return R.copy(H)},this.getViewport=function(R){return R.copy(Ne)},this.setViewport=function(R,j,te,ne){R.isVector4?Ne.set(R.x,R.y,R.z,R.w):Ne.set(R,j,te,ne),Ve.viewport(H.copy(Ne).multiplyScalar(re).round())},this.getScissor=function(R){return R.copy(Ze)},this.setScissor=function(R,j,te,ne){R.isVector4?Ze.set(R.x,R.y,R.z,R.w):Ze.set(R,j,te,ne),Ve.scissor(ee.copy(Ze).multiplyScalar(re).round())},this.getScissorTest=function(){return ht},this.setScissorTest=function(R){Ve.setScissorTest(ht=R)},this.setOpaqueSort=function(R){ye=R},this.setTransparentSort=function(R){Me=R},this.getClearColor=function(R){return R.copy(Ue.getClearColor())},this.setClearColor=function(){Ue.setClearColor.apply(Ue,arguments)},this.getClearAlpha=function(){return Ue.getClearAlpha()},this.setClearAlpha=function(){Ue.setClearAlpha.apply(Ue,arguments)},this.clear=function(R=!0,j=!0,te=!0){let ne=0;if(R){let q=!1;if(z!==null){const be=z.texture.format;q=be===md||be===pd||be===fd}if(q){const be=z.texture.type,Pe=be===$i||be===rs||be===Jo||be===eo||be===ud||be===hd,ke=Ue.getClearColor(),ze=Ue.getClearAlpha(),nt=ke.r,$e=ke.g,He=ke.b;Pe?(x[0]=nt,x[1]=$e,x[2]=He,x[3]=ze,X.clearBufferuiv(X.COLOR,0,x)):(M[0]=nt,M[1]=$e,M[2]=He,M[3]=ze,X.clearBufferiv(X.COLOR,0,M))}else ne|=X.COLOR_BUFFER_BIT}j&&(ne|=X.DEPTH_BUFFER_BIT),te&&(ne|=X.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),X.clear(ne)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",ie,!1),t.removeEventListener("webglcontextrestored",he,!1),t.removeEventListener("webglcontextcreationerror",me,!1),Re.dispose(),ct.dispose(),Fe.dispose(),E.dispose(),Z.dispose(),de.dispose(),V.dispose(),L.dispose(),De.dispose(),W.dispose(),W.removeEventListener("sessionstart",Tn),W.removeEventListener("sessionend",Kt),Xe.stop()};function ie(R){R.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),B=!0}function he(){console.log("THREE.WebGLRenderer: Context Restored."),B=!1;const R=xt.autoReset,j=Ce.enabled,te=Ce.autoUpdate,ne=Ce.needsUpdate,q=Ce.type;J(),xt.autoReset=R,Ce.enabled=j,Ce.autoUpdate=te,Ce.needsUpdate=ne,Ce.type=q}function me(R){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",R.statusMessage)}function Le(R){const j=R.target;j.removeEventListener("dispose",Le),Ke(j)}function Ke(R){bt(R),Fe.remove(R)}function bt(R){const j=Fe.get(R).programs;j!==void 0&&(j.forEach(function(te){De.releaseProgram(te)}),R.isShaderMaterial&&De.releaseShaderCache(R))}this.renderBufferDirect=function(R,j,te,ne,q,be){j===null&&(j=Tt);const Pe=q.isMesh&&q.matrixWorld.determinant()<0,ke=ho(R,j,te,ne,q);Ve.setMaterial(ne,Pe);let ze=te.index,nt=1;if(ne.wireframe===!0){if(ze=pe.getWireframeAttribute(te),ze===void 0)return;nt=2}const $e=te.drawRange,He=te.attributes.position;let yt=$e.start*nt,Rt=($e.start+$e.count)*nt;be!==null&&(yt=Math.max(yt,be.start*nt),Rt=Math.min(Rt,(be.start+be.count)*nt)),ze!==null?(yt=Math.max(yt,0),Rt=Math.min(Rt,ze.count)):He!=null&&(yt=Math.max(yt,0),Rt=Math.min(Rt,He.count));const It=Rt-yt;if(It<0||It===1/0)return;V.setup(q,ne,ke,te,ze);let Jt,St=Ie;if(ze!==null&&(Jt=ue.get(ze),St=pt,St.setIndex(Jt)),q.isMesh)ne.wireframe===!0?(Ve.setLineWidth(ne.wireframeLinewidth*Ot()),St.setMode(X.LINES)):St.setMode(X.TRIANGLES);else if(q.isLine){let Ge=ne.linewidth;Ge===void 0&&(Ge=1),Ve.setLineWidth(Ge*Ot()),q.isLineSegments?St.setMode(X.LINES):q.isLineLoop?St.setMode(X.LINE_LOOP):St.setMode(X.LINE_STRIP)}else q.isPoints?St.setMode(X.POINTS):q.isSprite&&St.setMode(X.TRIANGLES);if(q.isBatchedMesh)if(q._multiDrawInstances!==null)St.renderMultiDrawInstances(q._multiDrawStarts,q._multiDrawCounts,q._multiDrawCount,q._multiDrawInstances);else if(at.get("WEBGL_multi_draw"))St.renderMultiDraw(q._multiDrawStarts,q._multiDrawCounts,q._multiDrawCount);else{const Ge=q._multiDrawStarts,Xn=q._multiDrawCounts,_t=q._multiDrawCount,yn=ze?ue.get(ze).bytesPerElement:1,yi=Fe.get(ne).currentProgram.getUniforms();for(let rn=0;rn<_t;rn++)yi.setValue(X,"_gl_DrawID",rn),St.render(Ge[rn]/yn,Xn[rn])}else if(q.isInstancedMesh)St.renderInstances(yt,It,q.count);else if(te.isInstancedBufferGeometry){const Ge=te._maxInstanceCount!==void 0?te._maxInstanceCount:1/0,Xn=Math.min(te.instanceCount,Ge);St.renderInstances(yt,It,Xn)}else St.render(yt,It)};function et(R,j,te){R.transparent===!0&&R.side===Gn&&R.forceSinglePass===!1?(R.side=Wn,R.needsUpdate=!0,Qi(R,j,te),R.side=Zi,R.needsUpdate=!0,Qi(R,j,te),R.side=Gn):Qi(R,j,te)}this.compile=function(R,j,te=null){te===null&&(te=R),_=ct.get(te),_.init(j),P.push(_),te.traverseVisible(function(q){q.isLight&&q.layers.test(j.layers)&&(_.pushLight(q),q.castShadow&&_.pushShadow(q))}),R!==te&&R.traverseVisible(function(q){q.isLight&&q.layers.test(j.layers)&&(_.pushLight(q),q.castShadow&&_.pushShadow(q))}),_.setupLights();const ne=new Set;return R.traverse(function(q){if(!(q.isMesh||q.isPoints||q.isLine||q.isSprite))return;const be=q.material;if(be)if(Array.isArray(be))for(let Pe=0;Pe<be.length;Pe++){const ke=be[Pe];et(ke,te,q),ne.add(ke)}else et(be,te,q),ne.add(be)}),P.pop(),_=null,ne},this.compileAsync=function(R,j,te=null){const ne=this.compile(R,j,te);return new Promise(q=>{function be(){if(ne.forEach(function(Pe){Fe.get(Pe).currentProgram.isReady()&&ne.delete(Pe)}),ne.size===0){q(R);return}setTimeout(be,10)}at.get("KHR_parallel_shader_compile")!==null?be():setTimeout(be,10)})};let Et=null;function $t(R){Et&&Et(R)}function Tn(){Xe.stop()}function Kt(){Xe.start()}const Xe=new Fg;Xe.setAnimationLoop($t),typeof self<"u"&&Xe.setContext(self),this.setAnimationLoop=function(R){Et=R,W.setAnimationLoop(R),R===null?Xe.stop():Xe.start()},W.addEventListener("sessionstart",Tn),W.addEventListener("sessionend",Kt),this.render=function(R,j){if(j!==void 0&&j.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(B===!0)return;if(R.matrixWorldAutoUpdate===!0&&R.updateMatrixWorld(),j.parent===null&&j.matrixWorldAutoUpdate===!0&&j.updateMatrixWorld(),W.enabled===!0&&W.isPresenting===!0&&(W.cameraAutoUpdate===!0&&W.updateCamera(j),j=W.getCamera()),R.isScene===!0&&R.onBeforeRender(b,R,j,z),_=ct.get(R,P.length),_.init(j),P.push(_),We.multiplyMatrices(j.projectionMatrix,j.matrixWorldInverse),le.setFromProjectionMatrix(We),Oe=this.localClippingEnabled,ge=_e.init(this.clippingPlanes,Oe),v=Re.get(R,A.length),v.init(),A.push(v),W.enabled===!0&&W.isPresenting===!0){const be=b.xr.getDepthSensingMesh();be!==null&&Ht(be,j,-1/0,b.sortObjects)}Ht(R,j,0,b.sortObjects),v.finish(),b.sortObjects===!0&&v.sort(ye,Me),ot=W.enabled===!1||W.isPresenting===!1||W.hasDepthSensing()===!1,ot&&Ue.addToRenderList(v,R),this.info.render.frame++,ge===!0&&_e.beginShadows();const te=_.state.shadowsArray;Ce.render(te,R,j),ge===!0&&_e.endShadows(),this.info.autoReset===!0&&this.info.reset();const ne=v.opaque,q=v.transmissive;if(_.setupLights(),j.isArrayCamera){const be=j.cameras;if(q.length>0)for(let Pe=0,ke=be.length;Pe<ke;Pe++){const ze=be[Pe];us(ne,q,R,ze)}ot&&Ue.render(R);for(let Pe=0,ke=be.length;Pe<ke;Pe++){const ze=be[Pe];Bn(v,R,ze,ze.viewport)}}else q.length>0&&us(ne,q,R,j),ot&&Ue.render(R),Bn(v,R,j);z!==null&&(N.updateMultisampleRenderTarget(z),N.updateRenderTargetMipmap(z)),R.isScene===!0&&R.onAfterRender(b,R,j),V.resetDefaultState(),I=-1,w=null,P.pop(),P.length>0?(_=P[P.length-1],ge===!0&&_e.setGlobalState(b.clippingPlanes,_.state.camera)):_=null,A.pop(),A.length>0?v=A[A.length-1]:v=null};function Ht(R,j,te,ne){if(R.visible===!1)return;if(R.layers.test(j.layers)){if(R.isGroup)te=R.renderOrder;else if(R.isLOD)R.autoUpdate===!0&&R.update(j);else if(R.isLight)_.pushLight(R),R.castShadow&&_.pushShadow(R);else if(R.isSprite){if(!R.frustumCulled||le.intersectsSprite(R)){ne&&st.setFromMatrixPosition(R.matrixWorld).applyMatrix4(We);const Pe=de.update(R),ke=R.material;ke.visible&&v.push(R,Pe,ke,te,st.z,null)}}else if((R.isMesh||R.isLine||R.isPoints)&&(!R.frustumCulled||le.intersectsObject(R))){const Pe=de.update(R),ke=R.material;if(ne&&(R.boundingSphere!==void 0?(R.boundingSphere===null&&R.computeBoundingSphere(),st.copy(R.boundingSphere.center)):(Pe.boundingSphere===null&&Pe.computeBoundingSphere(),st.copy(Pe.boundingSphere.center)),st.applyMatrix4(R.matrixWorld).applyMatrix4(We)),Array.isArray(ke)){const ze=Pe.groups;for(let nt=0,$e=ze.length;nt<$e;nt++){const He=ze[nt],yt=ke[He.materialIndex];yt&&yt.visible&&v.push(R,Pe,yt,te,st.z,He)}}else ke.visible&&v.push(R,Pe,ke,te,st.z,null)}}const be=R.children;for(let Pe=0,ke=be.length;Pe<ke;Pe++)Ht(be[Pe],j,te,ne)}function Bn(R,j,te,ne){const q=R.opaque,be=R.transmissive,Pe=R.transparent;_.setupLightsView(te),ge===!0&&_e.setGlobalState(b.clippingPlanes,te),ne&&Ve.viewport(H.copy(ne)),q.length>0&&jn(q,j,te),be.length>0&&jn(be,j,te),Pe.length>0&&jn(Pe,j,te),Ve.buffers.depth.setTest(!0),Ve.buffers.depth.setMask(!0),Ve.buffers.color.setMask(!0),Ve.setPolygonOffset(!1)}function us(R,j,te,ne){if((te.isScene===!0?te.overrideMaterial:null)!==null)return;_.state.transmissionRenderTarget[ne.id]===void 0&&(_.state.transmissionRenderTarget[ne.id]=new ss(1,1,{generateMipmaps:!0,type:at.has("EXT_color_buffer_half_float")||at.has("EXT_color_buffer_float")?na:$i,minFilter:Xi,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:Mt.workingColorSpace}));const be=_.state.transmissionRenderTarget[ne.id],Pe=ne.viewport||H;be.setSize(Pe.z,Pe.w);const ke=b.getRenderTarget();b.setRenderTarget(be),b.getClearColor(ae),ce=b.getClearAlpha(),ce<1&&b.setClearColor(16777215,.5),b.clear(),ot&&Ue.render(te);const ze=b.toneMapping;b.toneMapping=xr;const nt=ne.viewport;if(ne.viewport!==void 0&&(ne.viewport=void 0),_.setupLightsView(ne),ge===!0&&_e.setGlobalState(b.clippingPlanes,ne),jn(R,te,ne),N.updateMultisampleRenderTarget(be),N.updateRenderTargetMipmap(be),at.has("WEBGL_multisampled_render_to_texture")===!1){let $e=!1;for(let He=0,yt=j.length;He<yt;He++){const Rt=j[He],It=Rt.object,Jt=Rt.geometry,St=Rt.material,Ge=Rt.group;if(St.side===Gn&&It.layers.test(ne.layers)){const Xn=St.side;St.side=Wn,St.needsUpdate=!0,Mr(It,te,ne,Jt,St,Ge),St.side=Xn,St.needsUpdate=!0,$e=!0}}$e===!0&&(N.updateMultisampleRenderTarget(be),N.updateRenderTargetMipmap(be))}b.setRenderTarget(ke),b.setClearColor(ae,ce),nt!==void 0&&(ne.viewport=nt),b.toneMapping=ze}function jn(R,j,te){const ne=j.isScene===!0?j.overrideMaterial:null;for(let q=0,be=R.length;q<be;q++){const Pe=R[q],ke=Pe.object,ze=Pe.geometry,nt=ne===null?Pe.material:ne,$e=Pe.group;ke.layers.test(te.layers)&&Mr(ke,j,te,ze,nt,$e)}}function Mr(R,j,te,ne,q,be){R.onBeforeRender(b,j,te,ne,q,be),R.modelViewMatrix.multiplyMatrices(te.matrixWorldInverse,R.matrixWorld),R.normalMatrix.getNormalMatrix(R.modelViewMatrix),q.onBeforeRender(b,j,te,ne,R,be),q.transparent===!0&&q.side===Gn&&q.forceSinglePass===!1?(q.side=Wn,q.needsUpdate=!0,b.renderBufferDirect(te,j,ne,q,R,be),q.side=Zi,q.needsUpdate=!0,b.renderBufferDirect(te,j,ne,q,R,be),q.side=Gn):b.renderBufferDirect(te,j,ne,q,R,be),R.onAfterRender(b,j,te,ne,q,be)}function Qi(R,j,te){j.isScene!==!0&&(j=Tt);const ne=Fe.get(R),q=_.state.lights,be=_.state.shadowsArray,Pe=q.state.version,ke=De.getParameters(R,q.state,be,j,te),ze=De.getProgramCacheKey(ke);let nt=ne.programs;ne.environment=R.isMeshStandardMaterial?j.environment:null,ne.fog=j.fog,ne.envMap=(R.isMeshStandardMaterial?Z:E).get(R.envMap||ne.environment),ne.envMapRotation=ne.environment!==null&&R.envMap===null?j.environmentRotation:R.envMapRotation,nt===void 0&&(R.addEventListener("dispose",Le),nt=new Map,ne.programs=nt);let $e=nt.get(ze);if($e!==void 0){if(ne.currentProgram===$e&&ne.lightsStateVersion===Pe)return ni(R,ke),$e}else ke.uniforms=De.getUniforms(R),R.onBeforeCompile(ke,b),$e=De.acquireProgram(ke,ze),nt.set(ze,$e),ne.uniforms=ke.uniforms;const He=ne.uniforms;return(!R.isShaderMaterial&&!R.isRawShaderMaterial||R.clipping===!0)&&(He.clippingPlanes=_e.uniform),ni(R,ke),ne.needsLights=er(R),ne.lightsStateVersion=Pe,ne.needsLights&&(He.ambientLightColor.value=q.state.ambient,He.lightProbe.value=q.state.probe,He.directionalLights.value=q.state.directional,He.directionalLightShadows.value=q.state.directionalShadow,He.spotLights.value=q.state.spot,He.spotLightShadows.value=q.state.spotShadow,He.rectAreaLights.value=q.state.rectArea,He.ltc_1.value=q.state.rectAreaLTC1,He.ltc_2.value=q.state.rectAreaLTC2,He.pointLights.value=q.state.point,He.pointLightShadows.value=q.state.pointShadow,He.hemisphereLights.value=q.state.hemi,He.directionalShadowMap.value=q.state.directionalShadowMap,He.directionalShadowMatrix.value=q.state.directionalShadowMatrix,He.spotShadowMap.value=q.state.spotShadowMap,He.spotLightMatrix.value=q.state.spotLightMatrix,He.spotLightMap.value=q.state.spotLightMap,He.pointShadowMap.value=q.state.pointShadowMap,He.pointShadowMatrix.value=q.state.pointShadowMatrix),ne.currentProgram=$e,ne.uniformsList=null,$e}function hs(R){if(R.uniformsList===null){const j=R.currentProgram.getUniforms();R.uniformsList=Rc.seqWithValue(j.seq,R.uniforms)}return R.uniformsList}function ni(R,j){const te=Fe.get(R);te.outputColorSpace=j.outputColorSpace,te.batching=j.batching,te.batchingColor=j.batchingColor,te.instancing=j.instancing,te.instancingColor=j.instancingColor,te.instancingMorph=j.instancingMorph,te.skinning=j.skinning,te.morphTargets=j.morphTargets,te.morphNormals=j.morphNormals,te.morphColors=j.morphColors,te.morphTargetsCount=j.morphTargetsCount,te.numClippingPlanes=j.numClippingPlanes,te.numIntersection=j.numClipIntersection,te.vertexAlphas=j.vertexAlphas,te.vertexTangents=j.vertexTangents,te.toneMapping=j.toneMapping}function ho(R,j,te,ne,q){j.isScene!==!0&&(j=Tt),N.resetTextureUnits();const be=j.fog,Pe=ne.isMeshStandardMaterial?j.environment:null,ke=z===null?b.outputColorSpace:z.isXRRenderTarget===!0?z.texture.colorSpace:Fn,ze=(ne.isMeshStandardMaterial?Z:E).get(ne.envMap||Pe),nt=ne.vertexColors===!0&&!!te.attributes.color&&te.attributes.color.itemSize===4,$e=!!te.attributes.tangent&&(!!ne.normalMap||ne.anisotropy>0),He=!!te.morphAttributes.position,yt=!!te.morphAttributes.normal,Rt=!!te.morphAttributes.color;let It=xr;ne.toneMapped&&(z===null||z.isXRRenderTarget===!0)&&(It=b.toneMapping);const Jt=te.morphAttributes.position||te.morphAttributes.normal||te.morphAttributes.color,St=Jt!==void 0?Jt.length:0,Ge=Fe.get(ne),Xn=_.state.lights;if(ge===!0&&(Oe===!0||R!==w)){const En=R===w&&ne.id===I;_e.setState(ne,R,En)}let _t=!1;ne.version===Ge.__version?(Ge.needsLights&&Ge.lightsStateVersion!==Xn.state.version||Ge.outputColorSpace!==ke||q.isBatchedMesh&&Ge.batching===!1||!q.isBatchedMesh&&Ge.batching===!0||q.isBatchedMesh&&Ge.batchingColor===!0&&q.colorTexture===null||q.isBatchedMesh&&Ge.batchingColor===!1&&q.colorTexture!==null||q.isInstancedMesh&&Ge.instancing===!1||!q.isInstancedMesh&&Ge.instancing===!0||q.isSkinnedMesh&&Ge.skinning===!1||!q.isSkinnedMesh&&Ge.skinning===!0||q.isInstancedMesh&&Ge.instancingColor===!0&&q.instanceColor===null||q.isInstancedMesh&&Ge.instancingColor===!1&&q.instanceColor!==null||q.isInstancedMesh&&Ge.instancingMorph===!0&&q.morphTexture===null||q.isInstancedMesh&&Ge.instancingMorph===!1&&q.morphTexture!==null||Ge.envMap!==ze||ne.fog===!0&&Ge.fog!==be||Ge.numClippingPlanes!==void 0&&(Ge.numClippingPlanes!==_e.numPlanes||Ge.numIntersection!==_e.numIntersection)||Ge.vertexAlphas!==nt||Ge.vertexTangents!==$e||Ge.morphTargets!==He||Ge.morphNormals!==yt||Ge.morphColors!==Rt||Ge.toneMapping!==It||Ge.morphTargetsCount!==St)&&(_t=!0):(_t=!0,Ge.__version=ne.version);let yn=Ge.currentProgram;_t===!0&&(yn=Qi(ne,j,q));let yi=!1,rn=!1,Ri=!1;const Lt=yn.getUniforms(),kn=Ge.uniforms;if(Ve.useProgram(yn.program)&&(yi=!0,rn=!0,Ri=!0),ne.id!==I&&(I=ne.id,rn=!0),yi||w!==R){Ve.buffers.depth.getReversed()?(Se.copy(R.projectionMatrix),mE(Se),gE(Se),Lt.setValue(X,"projectionMatrix",Se)):Lt.setValue(X,"projectionMatrix",R.projectionMatrix),Lt.setValue(X,"viewMatrix",R.matrixWorldInverse);const xn=Lt.map.cameraPosition;xn!==void 0&&xn.setValue(X,tt.setFromMatrixPosition(R.matrixWorld)),dt.logarithmicDepthBuffer&&Lt.setValue(X,"logDepthBufFC",2/(Math.log(R.far+1)/Math.LN2)),(ne.isMeshPhongMaterial||ne.isMeshToonMaterial||ne.isMeshLambertMaterial||ne.isMeshBasicMaterial||ne.isMeshStandardMaterial||ne.isShaderMaterial)&&Lt.setValue(X,"isOrthographic",R.isOrthographicCamera===!0),w!==R&&(w=R,rn=!0,Ri=!0)}if(q.isSkinnedMesh){Lt.setOptional(X,q,"bindMatrix"),Lt.setOptional(X,q,"bindMatrixInverse");const En=q.skeleton;En&&(En.boneTexture===null&&En.computeBoneTexture(),Lt.setValue(X,"boneTexture",En.boneTexture,N))}q.isBatchedMesh&&(Lt.setOptional(X,q,"batchingTexture"),Lt.setValue(X,"batchingTexture",q._matricesTexture,N),Lt.setOptional(X,q,"batchingIdTexture"),Lt.setValue(X,"batchingIdTexture",q._indirectTexture,N),Lt.setOptional(X,q,"batchingColorTexture"),q._colorsTexture!==null&&Lt.setValue(X,"batchingColorTexture",q._colorsTexture,N));const Ci=te.morphAttributes;if((Ci.position!==void 0||Ci.normal!==void 0||Ci.color!==void 0)&&Ye.update(q,te,yn),(rn||Ge.receiveShadow!==q.receiveShadow)&&(Ge.receiveShadow=q.receiveShadow,Lt.setValue(X,"receiveShadow",q.receiveShadow)),ne.isMeshGouraudMaterial&&ne.envMap!==null&&(kn.envMap.value=ze,kn.flipEnvMap.value=ze.isCubeTexture&&ze.isRenderTargetTexture===!1?-1:1),ne.isMeshStandardMaterial&&ne.envMap===null&&j.environment!==null&&(kn.envMapIntensity.value=j.environmentIntensity),rn&&(Lt.setValue(X,"toneMappingExposure",b.toneMappingExposure),Ge.needsLights&&Pi(kn,Ri),be&&ne.fog===!0&&Ee.refreshFogUniforms(kn,be),Ee.refreshMaterialUniforms(kn,ne,re,fe,_.state.transmissionRenderTarget[R.id]),Rc.upload(X,hs(Ge),kn,N)),ne.isShaderMaterial&&ne.uniformsNeedUpdate===!0&&(Rc.upload(X,hs(Ge),kn,N),ne.uniformsNeedUpdate=!1),ne.isSpriteMaterial&&Lt.setValue(X,"center",q.center),Lt.setValue(X,"modelViewMatrix",q.modelViewMatrix),Lt.setValue(X,"normalMatrix",q.normalMatrix),Lt.setValue(X,"modelMatrix",q.matrixWorld),ne.isShaderMaterial||ne.isRawShaderMaterial){const En=ne.uniformsGroups;for(let xn=0,qn=En.length;xn<qn;xn++){const ds=En[xn];L.update(ds,yn),L.bind(ds,yn)}}return yn}function Pi(R,j){R.ambientLightColor.needsUpdate=j,R.lightProbe.needsUpdate=j,R.directionalLights.needsUpdate=j,R.directionalLightShadows.needsUpdate=j,R.pointLights.needsUpdate=j,R.pointLightShadows.needsUpdate=j,R.spotLights.needsUpdate=j,R.spotLightShadows.needsUpdate=j,R.rectAreaLights.needsUpdate=j,R.hemisphereLights.needsUpdate=j}function er(R){return R.isMeshLambertMaterial||R.isMeshToonMaterial||R.isMeshPhongMaterial||R.isMeshStandardMaterial||R.isShadowMaterial||R.isShaderMaterial&&R.lights===!0}this.getActiveCubeFace=function(){return U},this.getActiveMipmapLevel=function(){return O},this.getRenderTarget=function(){return z},this.setRenderTargetTextures=function(R,j,te){Fe.get(R.texture).__webglTexture=j,Fe.get(R.depthTexture).__webglTexture=te;const ne=Fe.get(R);ne.__hasExternalTextures=!0,ne.__autoAllocateDepthBuffer=te===void 0,ne.__autoAllocateDepthBuffer||at.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),ne.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(R,j){const te=Fe.get(R);te.__webglFramebuffer=j,te.__useDefaultFramebuffer=j===void 0},this.setRenderTarget=function(R,j=0,te=0){z=R,U=j,O=te;let ne=!0,q=null,be=!1,Pe=!1;if(R){const ze=Fe.get(R);if(ze.__useDefaultFramebuffer!==void 0)Ve.bindFramebuffer(X.FRAMEBUFFER,null),ne=!1;else if(ze.__webglFramebuffer===void 0)N.setupRenderTarget(R);else if(ze.__hasExternalTextures)N.rebindTextures(R,Fe.get(R.texture).__webglTexture,Fe.get(R.depthTexture).__webglTexture);else if(R.depthBuffer){const He=R.depthTexture;if(ze.__boundDepthTexture!==He){if(He!==null&&Fe.has(He)&&(R.width!==He.image.width||R.height!==He.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");N.setupDepthRenderbuffer(R)}}const nt=R.texture;(nt.isData3DTexture||nt.isDataArrayTexture||nt.isCompressedArrayTexture)&&(Pe=!0);const $e=Fe.get(R).__webglFramebuffer;R.isWebGLCubeRenderTarget?(Array.isArray($e[j])?q=$e[j][te]:q=$e[j],be=!0):R.samples>0&&N.useMultisampledRTT(R)===!1?q=Fe.get(R).__webglMultisampledFramebuffer:Array.isArray($e)?q=$e[te]:q=$e,H.copy(R.viewport),ee.copy(R.scissor),Q=R.scissorTest}else H.copy(Ne).multiplyScalar(re).floor(),ee.copy(Ze).multiplyScalar(re).floor(),Q=ht;if(Ve.bindFramebuffer(X.FRAMEBUFFER,q)&&ne&&Ve.drawBuffers(R,q),Ve.viewport(H),Ve.scissor(ee),Ve.setScissorTest(Q),be){const ze=Fe.get(R.texture);X.framebufferTexture2D(X.FRAMEBUFFER,X.COLOR_ATTACHMENT0,X.TEXTURE_CUBE_MAP_POSITIVE_X+j,ze.__webglTexture,te)}else if(Pe){const ze=Fe.get(R.texture),nt=j||0;X.framebufferTextureLayer(X.FRAMEBUFFER,X.COLOR_ATTACHMENT0,ze.__webglTexture,te||0,nt)}I=-1},this.readRenderTargetPixels=function(R,j,te,ne,q,be,Pe){if(!(R&&R.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let ke=Fe.get(R).__webglFramebuffer;if(R.isWebGLCubeRenderTarget&&Pe!==void 0&&(ke=ke[Pe]),ke){Ve.bindFramebuffer(X.FRAMEBUFFER,ke);try{const ze=R.texture,nt=ze.format,$e=ze.type;if(!dt.textureFormatReadable(nt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!dt.textureTypeReadable($e)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}j>=0&&j<=R.width-ne&&te>=0&&te<=R.height-q&&X.readPixels(j,te,ne,q,it.convert(nt),it.convert($e),be)}finally{const ze=z!==null?Fe.get(z).__webglFramebuffer:null;Ve.bindFramebuffer(X.FRAMEBUFFER,ze)}}},this.readRenderTargetPixelsAsync=async function(R,j,te,ne,q,be,Pe){if(!(R&&R.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let ke=Fe.get(R).__webglFramebuffer;if(R.isWebGLCubeRenderTarget&&Pe!==void 0&&(ke=ke[Pe]),ke){const ze=R.texture,nt=ze.format,$e=ze.type;if(!dt.textureFormatReadable(nt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!dt.textureTypeReadable($e))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(j>=0&&j<=R.width-ne&&te>=0&&te<=R.height-q){Ve.bindFramebuffer(X.FRAMEBUFFER,ke);const He=X.createBuffer();X.bindBuffer(X.PIXEL_PACK_BUFFER,He),X.bufferData(X.PIXEL_PACK_BUFFER,be.byteLength,X.STREAM_READ),X.readPixels(j,te,ne,q,it.convert(nt),it.convert($e),0);const yt=z!==null?Fe.get(z).__webglFramebuffer:null;Ve.bindFramebuffer(X.FRAMEBUFFER,yt);const Rt=X.fenceSync(X.SYNC_GPU_COMMANDS_COMPLETE,0);return X.flush(),await pE(X,Rt,4),X.bindBuffer(X.PIXEL_PACK_BUFFER,He),X.getBufferSubData(X.PIXEL_PACK_BUFFER,0,be),X.deleteBuffer(He),X.deleteSync(Rt),be}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(R,j=null,te=0){R.isTexture!==!0&&(Wo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),j=arguments[0]||null,R=arguments[1]);const ne=Math.pow(2,-te),q=Math.floor(R.image.width*ne),be=Math.floor(R.image.height*ne),Pe=j!==null?j.x:0,ke=j!==null?j.y:0;N.setTexture2D(R,0),X.copyTexSubImage2D(X.TEXTURE_2D,te,0,0,Pe,ke,q,be),Ve.unbindTexture()},this.copyTextureToTexture=function(R,j,te=null,ne=null,q=0){R.isTexture!==!0&&(Wo("WebGLRenderer: copyTextureToTexture function signature has changed."),ne=arguments[0]||null,R=arguments[1],j=arguments[2],q=arguments[3]||0,te=null);let be,Pe,ke,ze,nt,$e,He,yt,Rt;const It=R.isCompressedTexture?R.mipmaps[q]:R.image;te!==null?(be=te.max.x-te.min.x,Pe=te.max.y-te.min.y,ke=te.isBox3?te.max.z-te.min.z:1,ze=te.min.x,nt=te.min.y,$e=te.isBox3?te.min.z:0):(be=It.width,Pe=It.height,ke=It.depth||1,ze=0,nt=0,$e=0),ne!==null?(He=ne.x,yt=ne.y,Rt=ne.z):(He=0,yt=0,Rt=0);const Jt=it.convert(j.format),St=it.convert(j.type);let Ge;j.isData3DTexture?(N.setTexture3D(j,0),Ge=X.TEXTURE_3D):j.isDataArrayTexture||j.isCompressedArrayTexture?(N.setTexture2DArray(j,0),Ge=X.TEXTURE_2D_ARRAY):(N.setTexture2D(j,0),Ge=X.TEXTURE_2D),X.pixelStorei(X.UNPACK_FLIP_Y_WEBGL,j.flipY),X.pixelStorei(X.UNPACK_PREMULTIPLY_ALPHA_WEBGL,j.premultiplyAlpha),X.pixelStorei(X.UNPACK_ALIGNMENT,j.unpackAlignment);const Xn=X.getParameter(X.UNPACK_ROW_LENGTH),_t=X.getParameter(X.UNPACK_IMAGE_HEIGHT),yn=X.getParameter(X.UNPACK_SKIP_PIXELS),yi=X.getParameter(X.UNPACK_SKIP_ROWS),rn=X.getParameter(X.UNPACK_SKIP_IMAGES);X.pixelStorei(X.UNPACK_ROW_LENGTH,It.width),X.pixelStorei(X.UNPACK_IMAGE_HEIGHT,It.height),X.pixelStorei(X.UNPACK_SKIP_PIXELS,ze),X.pixelStorei(X.UNPACK_SKIP_ROWS,nt),X.pixelStorei(X.UNPACK_SKIP_IMAGES,$e);const Ri=R.isDataArrayTexture||R.isData3DTexture,Lt=j.isDataArrayTexture||j.isData3DTexture;if(R.isRenderTargetTexture||R.isDepthTexture){const kn=Fe.get(R),Ci=Fe.get(j),En=Fe.get(kn.__renderTarget),xn=Fe.get(Ci.__renderTarget);Ve.bindFramebuffer(X.READ_FRAMEBUFFER,En.__webglFramebuffer),Ve.bindFramebuffer(X.DRAW_FRAMEBUFFER,xn.__webglFramebuffer);for(let qn=0;qn<ke;qn++)Ri&&X.framebufferTextureLayer(X.READ_FRAMEBUFFER,X.COLOR_ATTACHMENT0,Fe.get(R).__webglTexture,q,$e+qn),R.isDepthTexture?(Lt&&X.framebufferTextureLayer(X.DRAW_FRAMEBUFFER,X.COLOR_ATTACHMENT0,Fe.get(j).__webglTexture,q,Rt+qn),X.blitFramebuffer(ze,nt,be,Pe,He,yt,be,Pe,X.DEPTH_BUFFER_BIT,X.NEAREST)):Lt?X.copyTexSubImage3D(Ge,q,He,yt,Rt+qn,ze,nt,be,Pe):X.copyTexSubImage2D(Ge,q,He,yt,Rt+qn,ze,nt,be,Pe);Ve.bindFramebuffer(X.READ_FRAMEBUFFER,null),Ve.bindFramebuffer(X.DRAW_FRAMEBUFFER,null)}else Lt?R.isDataTexture||R.isData3DTexture?X.texSubImage3D(Ge,q,He,yt,Rt,be,Pe,ke,Jt,St,It.data):j.isCompressedArrayTexture?X.compressedTexSubImage3D(Ge,q,He,yt,Rt,be,Pe,ke,Jt,It.data):X.texSubImage3D(Ge,q,He,yt,Rt,be,Pe,ke,Jt,St,It):R.isDataTexture?X.texSubImage2D(X.TEXTURE_2D,q,He,yt,be,Pe,Jt,St,It.data):R.isCompressedTexture?X.compressedTexSubImage2D(X.TEXTURE_2D,q,He,yt,It.width,It.height,Jt,It.data):X.texSubImage2D(X.TEXTURE_2D,q,He,yt,be,Pe,Jt,St,It);X.pixelStorei(X.UNPACK_ROW_LENGTH,Xn),X.pixelStorei(X.UNPACK_IMAGE_HEIGHT,_t),X.pixelStorei(X.UNPACK_SKIP_PIXELS,yn),X.pixelStorei(X.UNPACK_SKIP_ROWS,yi),X.pixelStorei(X.UNPACK_SKIP_IMAGES,rn),q===0&&j.generateMipmaps&&X.generateMipmap(Ge),Ve.unbindTexture()},this.copyTextureToTexture3D=function(R,j,te=null,ne=null,q=0){return R.isTexture!==!0&&(Wo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),te=arguments[0]||null,ne=arguments[1]||null,R=arguments[2],j=arguments[3],q=arguments[4]||0),Wo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(R,j,te,ne,q)},this.initRenderTarget=function(R){Fe.get(R).__webglFramebuffer===void 0&&N.setupRenderTarget(R)},this.initTexture=function(R){R.isCubeTexture?N.setTextureCube(R,0):R.isData3DTexture?N.setTexture3D(R,0):R.isDataArrayTexture||R.isCompressedArrayTexture?N.setTexture2DArray(R,0):N.setTexture2D(R,0),Ve.unbindTexture()},this.resetState=function(){U=0,O=0,z=null,Ve.reset(),V.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return qi}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=Mt._getDrawingBufferColorSpace(e),t.unpackColorSpace=Mt._getUnpackColorSpace()}}class Md{constructor(e,t=25e-5){this.isFogExp2=!0,this.name="",this.color=new qe(e),this.density=t}clone(){return new Md(this.color,this.density)}toJSON(){return{type:"FogExp2",name:this.name,color:this.color.getHex(),density:this.density}}}class AR extends Xt{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new vi,this.environmentIntensity=1,this.environmentRotation=new vi,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class wR{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=ed,this.updateRanges=[],this.version=0,this.uuid=_i()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let i=0,s=this.stride;i<s;i++)this.array[e+i]=t.array[n+i];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=_i()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=_i()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const Dn=new F;class Td{constructor(e,t,n,i=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=i}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)Dn.fromBufferAttribute(this,t),Dn.applyMatrix4(e),this.setXYZ(t,Dn.x,Dn.y,Dn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Dn.fromBufferAttribute(this,t),Dn.applyNormalMatrix(e),this.setXYZ(t,Dn.x,Dn.y,Dn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Dn.fromBufferAttribute(this,t),Dn.transformDirection(e),this.setXYZ(t,Dn.x,Dn.y,Dn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=pi(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Nt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=Nt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=Nt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=Nt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=Nt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=pi(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=pi(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=pi(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=pi(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=Nt(t,this.array),n=Nt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,i){return e=e*this.data.stride+this.offset,this.normalized&&(t=Nt(t,this.array),n=Nt(n,this.array),i=Nt(i,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=Nt(t,this.array),n=Nt(n,this.array),i=Nt(i,this.array),s=Nt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=i,this.data.array[e+3]=s,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return new nn(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Td(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const i=n*this.data.stride+this.offset;for(let s=0;s<this.itemSize;s++)t.push(this.data.array[i+s])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const Em=new F,Am=new Pt,wm=new Pt,PR=new F,Pm=new rt,uc=new F,$u=new Ei,Rm=new rt,Ju=new oo;class Gg extends Te{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=Cp,this.bindMatrix=new rt,this.bindMatrixInverse=new rt,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new Ji),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,uc),this.boundingBox.expandByPoint(uc)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new Ei),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,uc),this.boundingSphere.expandByPoint(uc)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,i=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),$u.copy(this.boundingSphere),$u.applyMatrix4(i),e.ray.intersectsSphere($u)!==!1&&(Rm.copy(i).invert(),Ju.copy(e.ray).applyMatrix4(Rm),!(this.boundingBox!==null&&Ju.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,Ju)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new Pt,t=this.geometry.attributes.skinWeight;for(let n=0,i=t.count;n<i;n++){e.fromBufferAttribute(t,n);const s=1/e.manhattanLength();s!==1/0?e.multiplyScalar(s):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===Cp?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===UT?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,i=this.geometry;Am.fromBufferAttribute(i.attributes.skinIndex,e),wm.fromBufferAttribute(i.attributes.skinWeight,e),Em.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let s=0;s<4;s++){const a=wm.getComponent(s);if(a!==0){const c=Am.getComponent(s);Pm.multiplyMatrices(n.bones[c].matrixWorld,n.boneInverses[c]),t.addScaledVector(PR.copy(Em).applyMatrix4(Pm),a)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Vc extends Xt{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Wg extends vn{constructor(e=null,t=1,n=1,i,s,a,c,u,h=Un,f=Un,p,m){super(null,a,c,u,h,f,i,s,p,m),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Cm=new rt,RR=new rt;class ia{constructor(e=[],t=[]){this.uuid=_i(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,i=this.bones.length;n<i;n++)this.boneInverses.push(new rt)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new rt;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,i=this.boneTexture;for(let s=0,a=e.length;s<a;s++){const c=e[s]?e[s].matrixWorld:RR;Cm.multiplyMatrices(c,t[s]),Cm.toArray(n,s*16)}i!==null&&(i.needsUpdate=!0)}clone(){return new ia(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Wg(t,e,e,ai,gi);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const i=this.bones[t];if(i.name===e)return i}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,i=e.bones.length;n<i;n++){const s=e.bones[n];let a=t[s];a===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",s),a=new Vc),this.bones.push(a),this.boneInverses.push(new rt().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let i=0,s=t.length;i<s;i++){const a=t[i];e.bones.push(a.uuid);const c=n[i];e.boneInverses.push(c.toArray())}return e}}class nd extends nn{constructor(e,t,n,i=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=i}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const ks=new rt,Im=new rt,hc=[],Lm=new Ji,CR=new rt,Uo=new Te,Fo=new Ei;class IR extends Te{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new nd(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let i=0;i<n;i++)this.setMatrixAt(i,CR)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new Ji),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,ks),Lm.copy(e.boundingBox).applyMatrix4(ks),this.boundingBox.union(Lm)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new Ei),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,ks),Fo.copy(e.boundingSphere).applyMatrix4(ks),this.boundingSphere.union(Fo)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,i=this.morphTexture.source.data.data,s=n.length+1,a=e*s+1;for(let c=0;c<n.length;c++)n[c]=i[a+c]}raycast(e,t){const n=this.matrixWorld,i=this.count;if(Uo.geometry=this.geometry,Uo.material=this.material,Uo.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Fo.copy(this.boundingSphere),Fo.applyMatrix4(n),e.ray.intersectsSphere(Fo)!==!1))for(let s=0;s<i;s++){this.getMatrixAt(s,ks),Im.multiplyMatrices(n,ks),Uo.matrixWorld=Im,Uo.raycast(e,hc);for(let a=0,c=hc.length;a<c;a++){const u=hc[a];u.instanceId=s,u.object=this,t.push(u)}hc.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new nd(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,i=n.length+1;this.morphTexture===null&&(this.morphTexture=new Wg(new Float32Array(i*this.count),i,this.count,dd,gi));const s=this.morphTexture.source.data.data;let a=0;for(let h=0;h<n.length;h++)a+=n[h];const c=this.geometry.morphTargetsRelative?1:1-a,u=i*e;s[u]=c,s.set(n,u+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class Gc extends Ti{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new qe(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const Uc=new F,Fc=new F,Dm=new rt,Bo=new oo,dc=new Ei,Qu=new F,Nm=new F;class fi extends Xt{constructor(e=new hn,t=new Gc){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let i=1,s=t.count;i<s;i++)Uc.fromBufferAttribute(t,i-1),Fc.fromBufferAttribute(t,i),n[i]=n[i-1],n[i]+=Uc.distanceTo(Fc);e.setAttribute("lineDistance",new zt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Line.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),dc.copy(n.boundingSphere),dc.applyMatrix4(i),dc.radius+=s,e.ray.intersectsSphere(dc)===!1)return;Dm.copy(i).invert(),Bo.copy(e.ray).applyMatrix4(Dm);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=this.isLineSegments?2:1,f=n.index,m=n.attributes.position;if(f!==null){const g=Math.max(0,a.start),x=Math.min(f.count,a.start+a.count);for(let M=g,v=x-1;M<v;M+=h){const _=f.getX(M),A=f.getX(M+1),P=fc(this,e,Bo,u,_,A);P&&t.push(P)}if(this.isLineLoop){const M=f.getX(x-1),v=f.getX(g),_=fc(this,e,Bo,u,M,v);_&&t.push(_)}}else{const g=Math.max(0,a.start),x=Math.min(m.count,a.start+a.count);for(let M=g,v=x-1;M<v;M+=h){const _=fc(this,e,Bo,u,M,M+1);_&&t.push(_)}if(this.isLineLoop){const M=fc(this,e,Bo,u,x-1,g);M&&t.push(M)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function fc(r,e,t,n,i,s){const a=r.geometry.attributes.position;if(Uc.fromBufferAttribute(a,i),Fc.fromBufferAttribute(a,s),t.distanceSqToSegment(Uc,Fc,Qu,Nm)>n)return;Qu.applyMatrix4(r.matrixWorld);const u=e.ray.origin.distanceTo(Qu);if(!(u<e.near||u>e.far))return{distance:u,point:Nm.clone().applyMatrix4(r.matrixWorld),index:i,face:null,faceIndex:null,barycoord:null,object:r}}const Om=new F,Um=new F;class jg extends fi{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let i=0,s=t.count;i<s;i+=2)Om.fromBufferAttribute(t,i),Um.fromBufferAttribute(t,i+1),n[i]=i===0?0:n[i-1],n[i+1]=n[i]+Om.distanceTo(Um);e.setAttribute("lineDistance",new zt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class LR extends fi{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class Xg extends Ti{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new qe(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Fm=new rt,id=new oo,pc=new Ei,mc=new F;class DR extends Xt{constructor(e=new hn,t=new Xg){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Points.threshold,a=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),pc.copy(n.boundingSphere),pc.applyMatrix4(i),pc.radius+=s,e.ray.intersectsSphere(pc)===!1)return;Fm.copy(i).invert(),id.copy(e.ray).applyMatrix4(Fm);const c=s/((this.scale.x+this.scale.y+this.scale.z)/3),u=c*c,h=n.index,p=n.attributes.position;if(h!==null){const m=Math.max(0,a.start),g=Math.min(h.count,a.start+a.count);for(let x=m,M=g;x<M;x++){const v=h.getX(x);mc.fromBufferAttribute(p,v),Bm(mc,v,u,i,e,t,this)}}else{const m=Math.max(0,a.start),g=Math.min(p.count,a.start+a.count);for(let x=m,M=g;x<M;x++)mc.fromBufferAttribute(p,x),Bm(mc,x,u,i,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,a=i.length;s<a;s++){const c=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[c]=s}}}}}function Bm(r,e,t,n,i,s,a){const c=id.distanceSqToPoint(r);if(c<t){const u=new F;id.closestPointToPoint(r,u),u.applyMatrix4(n);const h=i.ray.origin.distanceTo(u);if(h<i.near||h>i.far)return;s.push({distance:h,distanceToRay:Math.sqrt(c),point:u,index:e,face:null,faceIndex:null,barycoord:null,object:a})}}class Sn extends hn{constructor(e=1,t=1,n=1,i=32,s=1,a=!1,c=0,u=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:i,heightSegments:s,openEnded:a,thetaStart:c,thetaLength:u};const h=this;i=Math.floor(i),s=Math.floor(s);const f=[],p=[],m=[],g=[];let x=0;const M=[],v=n/2;let _=0;A(),a===!1&&(e>0&&P(!0),t>0&&P(!1)),this.setIndex(f),this.setAttribute("position",new zt(p,3)),this.setAttribute("normal",new zt(m,3)),this.setAttribute("uv",new zt(g,2));function A(){const b=new F,B=new F;let U=0;const O=(t-e)/n;for(let z=0;z<=s;z++){const I=[],w=z/s,H=w*(t-e)+e;for(let ee=0;ee<=i;ee++){const Q=ee/i,ae=Q*u+c,ce=Math.sin(ae),$=Math.cos(ae);B.x=H*ce,B.y=-w*n+v,B.z=H*$,p.push(B.x,B.y,B.z),b.set(ce,O,$).normalize(),m.push(b.x,b.y,b.z),g.push(Q,1-w),I.push(x++)}M.push(I)}for(let z=0;z<i;z++)for(let I=0;I<s;I++){const w=M[I][z],H=M[I+1][z],ee=M[I+1][z+1],Q=M[I][z+1];(e>0||I!==0)&&(f.push(w,H,Q),U+=3),(t>0||I!==s-1)&&(f.push(H,ee,Q),U+=3)}h.addGroup(_,U,0),_+=U}function P(b){const B=x,U=new Qe,O=new F;let z=0;const I=b===!0?e:t,w=b===!0?1:-1;for(let ee=1;ee<=i;ee++)p.push(0,v*w,0),m.push(0,w,0),g.push(.5,.5),x++;const H=x;for(let ee=0;ee<=i;ee++){const ae=ee/i*u+c,ce=Math.cos(ae),$=Math.sin(ae);O.x=I*$,O.y=v*w,O.z=I*ce,p.push(O.x,O.y,O.z),m.push(0,w,0),U.x=ce*.5+.5,U.y=$*.5*w+.5,g.push(U.x,U.y),x++}for(let ee=0;ee<i;ee++){const Q=B+ee,ae=H+ee;b===!0?f.push(ae,ae+1,Q):f.push(ae+1,ae,Q),z+=3}h.addGroup(_,z,b===!0?1:2),_+=z}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Sn(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Ed extends Sn{constructor(e=1,t=1,n=32,i=1,s=!1,a=0,c=Math.PI*2){super(0,e,t,n,i,s,a,c),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:i,openEnded:s,thetaStart:a,thetaLength:c}}static fromJSON(e){return new Ed(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Ad extends hn{constructor(e=[],t=[],n=1,i=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:i};const s=[],a=[];c(i),h(n),f(),this.setAttribute("position",new zt(s,3)),this.setAttribute("normal",new zt(s.slice(),3)),this.setAttribute("uv",new zt(a,2)),i===0?this.computeVertexNormals():this.normalizeNormals();function c(A){const P=new F,b=new F,B=new F;for(let U=0;U<t.length;U+=3)g(t[U+0],P),g(t[U+1],b),g(t[U+2],B),u(P,b,B,A)}function u(A,P,b,B){const U=B+1,O=[];for(let z=0;z<=U;z++){O[z]=[];const I=A.clone().lerp(b,z/U),w=P.clone().lerp(b,z/U),H=U-z;for(let ee=0;ee<=H;ee++)ee===0&&z===U?O[z][ee]=I:O[z][ee]=I.clone().lerp(w,ee/H)}for(let z=0;z<U;z++)for(let I=0;I<2*(U-z)-1;I++){const w=Math.floor(I/2);I%2===0?(m(O[z][w+1]),m(O[z+1][w]),m(O[z][w])):(m(O[z][w+1]),m(O[z+1][w+1]),m(O[z+1][w]))}}function h(A){const P=new F;for(let b=0;b<s.length;b+=3)P.x=s[b+0],P.y=s[b+1],P.z=s[b+2],P.normalize().multiplyScalar(A),s[b+0]=P.x,s[b+1]=P.y,s[b+2]=P.z}function f(){const A=new F;for(let P=0;P<s.length;P+=3){A.x=s[P+0],A.y=s[P+1],A.z=s[P+2];const b=v(A)/2/Math.PI+.5,B=_(A)/Math.PI+.5;a.push(b,1-B)}x(),p()}function p(){for(let A=0;A<a.length;A+=6){const P=a[A+0],b=a[A+2],B=a[A+4],U=Math.max(P,b,B),O=Math.min(P,b,B);U>.9&&O<.1&&(P<.2&&(a[A+0]+=1),b<.2&&(a[A+2]+=1),B<.2&&(a[A+4]+=1))}}function m(A){s.push(A.x,A.y,A.z)}function g(A,P){const b=A*3;P.x=e[b+0],P.y=e[b+1],P.z=e[b+2]}function x(){const A=new F,P=new F,b=new F,B=new F,U=new Qe,O=new Qe,z=new Qe;for(let I=0,w=0;I<s.length;I+=9,w+=6){A.set(s[I+0],s[I+1],s[I+2]),P.set(s[I+3],s[I+4],s[I+5]),b.set(s[I+6],s[I+7],s[I+8]),U.set(a[w+0],a[w+1]),O.set(a[w+2],a[w+3]),z.set(a[w+4],a[w+5]),B.copy(A).add(P).add(b).divideScalar(3);const H=v(B);M(U,w+0,A,H),M(O,w+2,P,H),M(z,w+4,b,H)}}function M(A,P,b,B){B<0&&A.x===1&&(a[P]=A.x-1),b.x===0&&b.z===0&&(a[P]=B/2/Math.PI+.5)}function v(A){return Math.atan2(A.z,-A.x)}function _(A){return Math.atan2(-A.y,Math.sqrt(A.x*A.x+A.z*A.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ad(e.vertices,e.indices,e.radius,e.details)}}class Ws extends Ad{constructor(e=1,t=0){const n=[1,0,0,-1,0,0,0,1,0,0,-1,0,0,0,1,0,0,-1],i=[0,2,4,0,4,3,0,3,5,0,5,2,1,2,5,1,5,3,1,3,4,1,4,2];super(n,i,e,t),this.type="OctahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new Ws(e.radius,e.detail)}}class ra extends hn{constructor(e=1,t=32,n=16,i=0,s=Math.PI*2,a=0,c=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:i,phiLength:s,thetaStart:a,thetaLength:c},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const u=Math.min(a+c,Math.PI);let h=0;const f=[],p=new F,m=new F,g=[],x=[],M=[],v=[];for(let _=0;_<=n;_++){const A=[],P=_/n;let b=0;_===0&&a===0?b=.5/t:_===n&&u===Math.PI&&(b=-.5/t);for(let B=0;B<=t;B++){const U=B/t;p.x=-e*Math.cos(i+U*s)*Math.sin(a+P*c),p.y=e*Math.cos(a+P*c),p.z=e*Math.sin(i+U*s)*Math.sin(a+P*c),x.push(p.x,p.y,p.z),m.copy(p).normalize(),M.push(m.x,m.y,m.z),v.push(U+b,1-P),A.push(h++)}f.push(A)}for(let _=0;_<n;_++)for(let A=0;A<t;A++){const P=f[_][A+1],b=f[_][A],B=f[_+1][A],U=f[_+1][A+1];(_!==0||a>0)&&g.push(P,b,U),(_!==n-1||u<Math.PI)&&g.push(b,B,U)}this.setIndex(g),this.setAttribute("position",new zt(x,3)),this.setAttribute("normal",new zt(M,3)),this.setAttribute("uv",new zt(v,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ra(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class is extends hn{constructor(e=1,t=.4,n=12,i=48,s=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:i,arc:s},n=Math.floor(n),i=Math.floor(i);const a=[],c=[],u=[],h=[],f=new F,p=new F,m=new F;for(let g=0;g<=n;g++)for(let x=0;x<=i;x++){const M=x/i*s,v=g/n*Math.PI*2;p.x=(e+t*Math.cos(v))*Math.cos(M),p.y=(e+t*Math.cos(v))*Math.sin(M),p.z=t*Math.sin(v),c.push(p.x,p.y,p.z),f.x=e*Math.cos(M),f.y=e*Math.sin(M),m.subVectors(p,f).normalize(),u.push(m.x,m.y,m.z),h.push(x/i),h.push(g/n)}for(let g=1;g<=n;g++)for(let x=1;x<=i;x++){const M=(i+1)*g+x-1,v=(i+1)*(g-1)+x-1,_=(i+1)*(g-1)+x,A=(i+1)*g+x;a.push(M,v,A),a.push(v,_,A)}this.setIndex(a),this.setAttribute("position",new zt(c,3)),this.setAttribute("normal",new zt(u,3)),this.setAttribute("uv",new zt(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new is(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class os extends Ti{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new qe(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new qe(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Eg,this.normalScale=new Qe(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new vi,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Ai extends os{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new Qe(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return Mn(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new qe(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new qe(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new qe(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function gc(r,e,t){return!r||!t&&r.constructor===e?r:typeof e.BYTES_PER_ELEMENT=="number"?new e(r):Array.prototype.slice.call(r)}function NR(r){return ArrayBuffer.isView(r)&&!(r instanceof DataView)}function OR(r){function e(i,s){return r[i]-r[s]}const t=r.length,n=new Array(t);for(let i=0;i!==t;++i)n[i]=i;return n.sort(e),n}function km(r,e,t){const n=r.length,i=new r.constructor(n);for(let s=0,a=0;a!==n;++s){const c=t[s]*e;for(let u=0;u!==e;++u)i[a++]=r[c+u]}return i}function qg(r,e,t,n){let i=1,s=r[0];for(;s!==void 0&&s[n]===void 0;)s=r[i++];if(s===void 0)return;let a=s[n];if(a!==void 0)if(Array.isArray(a))do a=s[n],a!==void 0&&(e.push(s.time),t.push.apply(t,a)),s=r[i++];while(s!==void 0);else if(a.toArray!==void 0)do a=s[n],a!==void 0&&(e.push(s.time),a.toArray(t,t.length)),s=r[i++];while(s!==void 0);else do a=s[n],a!==void 0&&(e.push(s.time),t.push(a)),s=r[i++];while(s!==void 0)}class sa{constructor(e,t,n,i){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=i!==void 0?i:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,i=t[n],s=t[n-1];e:{t:{let a;n:{i:if(!(e<i)){for(let c=n+2;;){if(i===void 0){if(e<s)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===c)break;if(s=i,i=t[++n],e<i)break t}a=t.length;break n}if(!(e>=s)){const c=t[1];e<c&&(n=2,s=c);for(let u=n-2;;){if(s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===u)break;if(i=s,s=t[--n-1],e>=s)break t}a=n,n=0;break n}break e}for(;n<a;){const c=n+a>>>1;e<t[c]?a=c:n=c+1}if(i=t[n],s=t[n-1],s===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(i===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,s,i)}return this.interpolate_(n,s,e,i)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i;for(let a=0;a!==i;++a)t[a]=n[s+a];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class UR extends sa{constructor(e,t,n,i){super(e,t,n,i),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Hs,endingEnd:Hs}}intervalChanged_(e,t,n){const i=this.parameterPositions;let s=e-2,a=e+1,c=i[s],u=i[a];if(c===void 0)switch(this.getSettings_().endingStart){case Vs:s=e,c=2*t-n;break;case Nc:s=i.length-2,c=t+i[s]-i[s+1];break;default:s=e,c=n}if(u===void 0)switch(this.getSettings_().endingEnd){case Vs:a=e,u=2*n-t;break;case Nc:a=1,u=n+i[1]-i[0];break;default:a=e-1,u=t}const h=(n-t)*.5,f=this.valueSize;this._weightPrev=h/(t-c),this._weightNext=h/(u-n),this._offsetPrev=s*f,this._offsetNext=a*f}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=this._offsetPrev,p=this._offsetNext,m=this._weightPrev,g=this._weightNext,x=(n-t)/(i-t),M=x*x,v=M*x,_=-m*v+2*m*M-m*x,A=(1+m)*v+(-1.5-2*m)*M+(-.5+m)*x+1,P=(-1-g)*v+(1.5+g)*M+.5*x,b=g*v-g*M;for(let B=0;B!==c;++B)s[B]=_*a[f+B]+A*a[h+B]+P*a[u+B]+b*a[p+B];return s}}class Yg extends sa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=e*c,h=u-c,f=(n-t)/(i-t),p=1-f;for(let m=0;m!==c;++m)s[m]=a[h+m]*p+a[u+m]*f;return s}}class FR extends sa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e){return this.copySampleValue_(e-1)}}class wi{constructor(e,t,n,i){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=gc(t,this.TimeBufferType),this.values=gc(n,this.ValueBufferType),this.setInterpolation(i||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:gc(e.times,Array),values:gc(e.values,Array)};const i=e.getInterpolation();i!==e.DefaultInterpolation&&(n.interpolation=i)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new FR(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new Yg(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new UR(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case Qo:t=this.InterpolantFactoryMethodDiscrete;break;case ea:t=this.InterpolantFactoryMethodLinear;break;case Mu:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return Qo;case this.InterpolantFactoryMethodLinear:return ea;case this.InterpolantFactoryMethodSmooth:return Mu}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,i=t.length;n!==i;++n)t[n]*=e}return this}trim(e,t){const n=this.times,i=n.length;let s=0,a=i-1;for(;s!==i&&n[s]<e;)++s;for(;a!==-1&&n[a]>t;)--a;if(++a,s!==0||a!==i){s>=a&&(a=Math.max(a,1),s=a-1);const c=this.getValueSize();this.times=n.slice(s,a),this.values=this.values.slice(s*c,a*c)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,i=this.values,s=n.length;s===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let a=null;for(let c=0;c!==s;c++){const u=n[c];if(typeof u=="number"&&isNaN(u)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,c,u),e=!1;break}if(a!==null&&a>u){console.error("THREE.KeyframeTrack: Out of order keys.",this,c,u,a),e=!1;break}a=u}if(i!==void 0&&NR(i))for(let c=0,u=i.length;c!==u;++c){const h=i[c];if(isNaN(h)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,c,h),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),i=this.getInterpolation()===Mu,s=e.length-1;let a=1;for(let c=1;c<s;++c){let u=!1;const h=e[c],f=e[c+1];if(h!==f&&(c!==1||h!==e[0]))if(i)u=!0;else{const p=c*n,m=p-n,g=p+n;for(let x=0;x!==n;++x){const M=t[p+x];if(M!==t[m+x]||M!==t[g+x]){u=!0;break}}}if(u){if(c!==a){e[a]=e[c];const p=c*n,m=a*n;for(let g=0;g!==n;++g)t[m+g]=t[p+g]}++a}}if(s>0){e[a]=e[s];for(let c=s*n,u=a*n,h=0;h!==n;++h)t[u+h]=t[c+h];++a}return a!==e.length?(this.times=e.slice(0,a),this.values=t.slice(0,a*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,i=new n(this.name,e,t);return i.createInterpolant=this.createInterpolant,i}}wi.prototype.TimeBufferType=Float32Array;wi.prototype.ValueBufferType=Float32Array;wi.prototype.DefaultInterpolation=ea;class lo extends wi{constructor(e,t,n){super(e,t,n)}}lo.prototype.ValueTypeName="bool";lo.prototype.ValueBufferType=Array;lo.prototype.DefaultInterpolation=Qo;lo.prototype.InterpolantFactoryMethodLinear=void 0;lo.prototype.InterpolantFactoryMethodSmooth=void 0;class Kg extends wi{}Kg.prototype.ValueTypeName="color";class ro extends wi{}ro.prototype.ValueTypeName="number";class BR extends sa{constructor(e,t,n,i){super(e,t,n,i)}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=(n-t)/(i-t);let h=e*c;for(let f=h+c;h!==f;h+=4)Yt.slerpFlat(s,0,a,h-c,a,h,u);return s}}class as extends wi{InterpolantFactoryMethodLinear(e){return new BR(this.times,this.values,this.getValueSize(),e)}}as.prototype.ValueTypeName="quaternion";as.prototype.InterpolantFactoryMethodSmooth=void 0;class uo extends wi{constructor(e,t,n){super(e,t,n)}}uo.prototype.ValueTypeName="string";uo.prototype.ValueBufferType=Array;uo.prototype.DefaultInterpolation=Qo;uo.prototype.InterpolantFactoryMethodLinear=void 0;uo.prototype.InterpolantFactoryMethodSmooth=void 0;class cs extends wi{}cs.prototype.ValueTypeName="vector";class Bc{constructor(e="",t=-1,n=[],i=_d){this.name=e,this.tracks=n,this.duration=t,this.blendMode=i,this.uuid=_i(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,i=1/(e.fps||1);for(let a=0,c=n.length;a!==c;++a)t.push(zR(n[a]).scale(i));const s=new this(e.name,e.duration,t,e.blendMode);return s.uuid=e.uuid,s}static toJSON(e){const t=[],n=e.tracks,i={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let s=0,a=n.length;s!==a;++s)t.push(wi.toJSON(n[s]));return i}static CreateFromMorphTargetSequence(e,t,n,i){const s=t.length,a=[];for(let c=0;c<s;c++){let u=[],h=[];u.push((c+s-1)%s,c,(c+1)%s),h.push(0,1,0);const f=OR(u);u=km(u,1,f),h=km(h,1,f),!i&&u[0]===0&&(u.push(s),h.push(h[0])),a.push(new ro(".morphTargetInfluences["+t[c].name+"]",u,h).scale(1/n))}return new this(e,-1,a)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const i=e;n=i.geometry&&i.geometry.animations||i.animations}for(let i=0;i<n.length;i++)if(n[i].name===t)return n[i];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const i={},s=/^([\w-]*?)([\d]+)$/;for(let c=0,u=e.length;c<u;c++){const h=e[c],f=h.name.match(s);if(f&&f.length>1){const p=f[1];let m=i[p];m||(i[p]=m=[]),m.push(h)}}const a=[];for(const c in i)a.push(this.CreateFromMorphTargetSequence(c,i[c],t,n));return a}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(p,m,g,x,M){if(g.length!==0){const v=[],_=[];qg(g,v,_,x),v.length!==0&&M.push(new p(m,v,_))}},i=[],s=e.name||"default",a=e.fps||30,c=e.blendMode;let u=e.length||-1;const h=e.hierarchy||[];for(let p=0;p<h.length;p++){const m=h[p].keys;if(!(!m||m.length===0))if(m[0].morphTargets){const g={};let x;for(x=0;x<m.length;x++)if(m[x].morphTargets)for(let M=0;M<m[x].morphTargets.length;M++)g[m[x].morphTargets[M]]=-1;for(const M in g){const v=[],_=[];for(let A=0;A!==m[x].morphTargets.length;++A){const P=m[x];v.push(P.time),_.push(P.morphTarget===M?1:0)}i.push(new ro(".morphTargetInfluence["+M+"]",v,_))}u=g.length*a}else{const g=".bones["+t[p].name+"]";n(cs,g+".position",m,"pos",i),n(as,g+".quaternion",m,"rot",i),n(cs,g+".scale",m,"scl",i)}}return i.length===0?null:new this(s,u,i,c)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,i=e.length;n!==i;++n){const s=this.tracks[n];t=Math.max(t,s.times[s.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function kR(r){switch(r.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return ro;case"vector":case"vector2":case"vector3":case"vector4":return cs;case"color":return Kg;case"quaternion":return as;case"bool":case"boolean":return lo;case"string":return uo}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+r)}function zR(r){if(r.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=kR(r.type);if(r.times===void 0){const t=[],n=[];qg(r.keys,t,n,"value"),r.times=t,r.values=n}return e.parse!==void 0?e.parse(r):new e(r.name,r.times,r.values,r.interpolation)}const vr={enabled:!1,files:{},add:function(r,e){this.enabled!==!1&&(this.files[r]=e)},get:function(r){if(this.enabled!==!1)return this.files[r]},remove:function(r){delete this.files[r]},clear:function(){this.files={}}};class HR{constructor(e,t,n){const i=this;let s=!1,a=0,c=0,u;const h=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(f){c++,s===!1&&i.onStart!==void 0&&i.onStart(f,a,c),s=!0},this.itemEnd=function(f){a++,i.onProgress!==void 0&&i.onProgress(f,a,c),a===c&&(s=!1,i.onLoad!==void 0&&i.onLoad())},this.itemError=function(f){i.onError!==void 0&&i.onError(f)},this.resolveURL=function(f){return u?u(f):f},this.setURLModifier=function(f){return u=f,this},this.addHandler=function(f,p){return h.push(f,p),this},this.removeHandler=function(f){const p=h.indexOf(f);return p!==-1&&h.splice(p,2),this},this.getHandler=function(f){for(let p=0,m=h.length;p<m;p+=2){const g=h[p],x=h[p+1];if(g.global&&(g.lastIndex=0),g.test(f))return x}return null}}}const VR=new HR;class ls{constructor(e){this.manager=e!==void 0?e:VR,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(i,s){n.load(e,i,t,s)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}ls.DEFAULT_MATERIAL_NAME="__DEFAULT";const Gi={};class GR extends Error{constructor(e,t){super(e),this.response=t}}class wd extends ls{constructor(e){super(e)}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=vr.get(e);if(s!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(s),this.manager.itemEnd(e)},0),s;if(Gi[e]!==void 0){Gi[e].push({onLoad:t,onProgress:n,onError:i});return}Gi[e]=[],Gi[e].push({onLoad:t,onProgress:n,onError:i});const a=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),c=this.mimeType,u=this.responseType;fetch(a).then(h=>{if(h.status===200||h.status===0){if(h.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||h.body===void 0||h.body.getReader===void 0)return h;const f=Gi[e],p=h.body.getReader(),m=h.headers.get("X-File-Size")||h.headers.get("Content-Length"),g=m?parseInt(m):0,x=g!==0;let M=0;const v=new ReadableStream({start(_){A();function A(){p.read().then(({done:P,value:b})=>{if(P)_.close();else{M+=b.byteLength;const B=new ProgressEvent("progress",{lengthComputable:x,loaded:M,total:g});for(let U=0,O=f.length;U<O;U++){const z=f[U];z.onProgress&&z.onProgress(B)}_.enqueue(b),A()}},P=>{_.error(P)})}}});return new Response(v)}else throw new GR(`fetch for "${h.url}" responded with ${h.status}: ${h.statusText}`,h)}).then(h=>{switch(u){case"arraybuffer":return h.arrayBuffer();case"blob":return h.blob();case"document":return h.text().then(f=>new DOMParser().parseFromString(f,c));case"json":return h.json();default:if(c===void 0)return h.text();{const p=/charset="?([^;"\s]*)"?/i.exec(c),m=p&&p[1]?p[1].toLowerCase():void 0,g=new TextDecoder(m);return h.arrayBuffer().then(x=>g.decode(x))}}}).then(h=>{vr.add(e,h);const f=Gi[e];delete Gi[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onLoad&&g.onLoad(h)}}).catch(h=>{const f=Gi[e];if(f===void 0)throw this.manager.itemError(e),h;delete Gi[e];for(let p=0,m=f.length;p<m;p++){const g=f[p];g.onError&&g.onError(h)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class WR extends ls{constructor(e){super(e)}load(e,t,n,i){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=vr.get(e);if(a!==void 0)return s.manager.itemStart(e),setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a;const c=ta("img");function u(){f(),vr.add(e,this),t&&t(this),s.manager.itemEnd(e)}function h(p){f(),i&&i(p),s.manager.itemError(e),s.manager.itemEnd(e)}function f(){c.removeEventListener("load",u,!1),c.removeEventListener("error",h,!1)}return c.addEventListener("load",u,!1),c.addEventListener("error",h,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(c.crossOrigin=this.crossOrigin),s.manager.itemStart(e),c.src=e,c}}class jR extends ls{constructor(e){super(e)}load(e,t,n,i){const s=new vn,a=new WR(this.manager);return a.setCrossOrigin(this.crossOrigin),a.setPath(this.path),a.load(e,function(c){s.image=c,s.needsUpdate=!0,t!==void 0&&t(s)},n,i),s}}class Wc extends Xt{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new qe(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const eh=new rt,zm=new F,Hm=new F;class Pd{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new Qe(512,512),this.map=null,this.mapPass=null,this.matrix=new rt,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new xd,this._frameExtents=new Qe(1,1),this._viewportCount=1,this._viewports=[new Pt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;zm.setFromMatrixPosition(e.matrixWorld),t.position.copy(zm),Hm.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Hm),t.updateMatrixWorld(),eh.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(eh),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(eh)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class XR extends Pd{constructor(){super(new On(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=no*2*e.angle*this.focus,i=this.mapSize.width/this.mapSize.height,s=e.distance||t.far;(n!==t.fov||i!==t.aspect||s!==t.far)&&(t.fov=n,t.aspect=i,t.far=s,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class qR extends Wc{constructor(e,t,n=0,i=Math.PI/3,s=0,a=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(Xt.DEFAULT_UP),this.updateMatrix(),this.target=new Xt,this.distance=n,this.angle=i,this.penumbra=s,this.decay=a,this.map=null,this.shadow=new XR}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const Vm=new rt,ko=new F,th=new F;class YR extends Pd{constructor(){super(new On(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new Qe(4,2),this._viewportCount=6,this._viewports=[new Pt(2,1,1,1),new Pt(0,1,1,1),new Pt(3,1,1,1),new Pt(1,1,1,1),new Pt(3,0,1,1),new Pt(1,0,1,1)],this._cubeDirections=[new F(1,0,0),new F(-1,0,0),new F(0,0,1),new F(0,0,-1),new F(0,1,0),new F(0,-1,0)],this._cubeUps=[new F(0,1,0),new F(0,1,0),new F(0,1,0),new F(0,1,0),new F(0,0,1),new F(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,i=this.matrix,s=e.distance||n.far;s!==n.far&&(n.far=s,n.updateProjectionMatrix()),ko.setFromMatrixPosition(e.matrixWorld),n.position.copy(ko),th.copy(n.position),th.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(th),n.updateMatrixWorld(),i.makeTranslation(-ko.x,-ko.y,-ko.z),Vm.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Vm)}}class Zg extends Wc{constructor(e,t,n=0,i=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=i,this.shadow=new YR}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class KR extends Pd{constructor(){super(new bd(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Cc extends Wc{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Xt.DEFAULT_UP),this.updateMatrix(),this.target=new Xt,this.shadow=new KR}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class ZR extends Wc{constructor(e,t){super(e,t),this.isAmbientLight=!0,this.type="AmbientLight"}}class $o{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,i=e.length;n<i;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class $R extends ls{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,i){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const s=this,a=vr.get(e);if(a!==void 0){if(s.manager.itemStart(e),a.then){a.then(h=>{t&&t(h),s.manager.itemEnd(e)}).catch(h=>{i&&i(h)});return}return setTimeout(function(){t&&t(a),s.manager.itemEnd(e)},0),a}const c={};c.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",c.headers=this.requestHeader;const u=fetch(e,c).then(function(h){return h.blob()}).then(function(h){return createImageBitmap(h,Object.assign(s.options,{colorSpaceConversion:"none"}))}).then(function(h){return vr.add(e,h),t&&t(h),s.manager.itemEnd(e),h}).catch(function(h){i&&i(h),vr.remove(e),s.manager.itemError(e),s.manager.itemEnd(e)});vr.add(e,u),s.manager.itemStart(e)}}class JR{constructor(e=!0){this.autoStart=e,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=Gm(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let e=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const t=Gm();e=(t-this.oldTime)/1e3,this.oldTime=t,this.elapsedTime+=e}return e}}function Gm(){return performance.now()}class QR{constructor(e,t,n){this.binding=e,this.valueSize=n;let i,s,a;switch(t){case"quaternion":i=this._slerp,s=this._slerpAdditive,a=this._setAdditiveIdentityQuaternion,this.buffer=new Float64Array(n*6),this._workIndex=5;break;case"string":case"bool":i=this._select,s=this._select,a=this._setAdditiveIdentityOther,this.buffer=new Array(n*5);break;default:i=this._lerp,s=this._lerpAdditive,a=this._setAdditiveIdentityNumeric,this.buffer=new Float64Array(n*5)}this._mixBufferRegion=i,this._mixBufferRegionAdditive=s,this._setIdentity=a,this._origIndex=3,this._addIndex=4,this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,this.useCount=0,this.referenceCount=0}accumulate(e,t){const n=this.buffer,i=this.valueSize,s=e*i+i;let a=this.cumulativeWeight;if(a===0){for(let c=0;c!==i;++c)n[s+c]=n[c];a=t}else{a+=t;const c=t/a;this._mixBufferRegion(n,s,0,c,i)}this.cumulativeWeight=a}accumulateAdditive(e){const t=this.buffer,n=this.valueSize,i=n*this._addIndex;this.cumulativeWeightAdditive===0&&this._setIdentity(),this._mixBufferRegionAdditive(t,i,0,e,n),this.cumulativeWeightAdditive+=e}apply(e){const t=this.valueSize,n=this.buffer,i=e*t+t,s=this.cumulativeWeight,a=this.cumulativeWeightAdditive,c=this.binding;if(this.cumulativeWeight=0,this.cumulativeWeightAdditive=0,s<1){const u=t*this._origIndex;this._mixBufferRegion(n,i,u,1-s,t)}a>0&&this._mixBufferRegionAdditive(n,i,this._addIndex*t,1,t);for(let u=t,h=t+t;u!==h;++u)if(n[u]!==n[u+t]){c.setValue(n,i);break}}saveOriginalState(){const e=this.binding,t=this.buffer,n=this.valueSize,i=n*this._origIndex;e.getValue(t,i);for(let s=n,a=i;s!==a;++s)t[s]=t[i+s%n];this._setIdentity(),this.cumulativeWeight=0,this.cumulativeWeightAdditive=0}restoreOriginalState(){const e=this.valueSize*3;this.binding.setValue(this.buffer,e)}_setAdditiveIdentityNumeric(){const e=this._addIndex*this.valueSize,t=e+this.valueSize;for(let n=e;n<t;n++)this.buffer[n]=0}_setAdditiveIdentityQuaternion(){this._setAdditiveIdentityNumeric(),this.buffer[this._addIndex*this.valueSize+3]=1}_setAdditiveIdentityOther(){const e=this._origIndex*this.valueSize,t=this._addIndex*this.valueSize;for(let n=0;n<this.valueSize;n++)this.buffer[t+n]=this.buffer[e+n]}_select(e,t,n,i,s){if(i>=.5)for(let a=0;a!==s;++a)e[t+a]=e[n+a]}_slerp(e,t,n,i){Yt.slerpFlat(e,t,e,t,e,n,i)}_slerpAdditive(e,t,n,i,s){const a=this._workIndex*s;Yt.multiplyQuaternionsFlat(e,a,e,t,e,n),Yt.slerpFlat(e,t,e,t,e,a,i)}_lerp(e,t,n,i,s){const a=1-i;for(let c=0;c!==s;++c){const u=t+c;e[u]=e[u]*a+e[n+c]*i}}_lerpAdditive(e,t,n,i,s){for(let a=0;a!==s;++a){const c=t+a;e[c]=e[c]+e[n+a]*i}}}const Rd="\\[\\]\\.:\\/",eC=new RegExp("["+Rd+"]","g"),Cd="[^"+Rd+"]",tC="[^"+Rd.replace("\\.","")+"]",nC=/((?:WC+[\/:])*)/.source.replace("WC",Cd),iC=/(WCOD+)?/.source.replace("WCOD",tC),rC=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Cd),sC=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Cd),oC=new RegExp("^"+nC+iC+rC+sC+"$"),aC=["material","materials","bones","map"];class cC{constructor(e,t,n){const i=n||Ct.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,i)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,i=this._bindings[n];i!==void 0&&i.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let i=this._targetGroup.nCachedObjects_,s=n.length;i!==s;++i)n[i].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class Ct{constructor(e,t,n){this.path=t,this.parsedPath=n||Ct.parseTrackName(t),this.node=Ct.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new Ct.Composite(e,t,n):new Ct(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(eC,"")}static parseTrackName(e){const t=oC.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},i=n.nodeName&&n.nodeName.lastIndexOf(".");if(i!==void 0&&i!==-1){const s=n.nodeName.substring(i+1);aC.indexOf(s)!==-1&&(n.nodeName=n.nodeName.substring(0,i),n.objectName=s)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(s){for(let a=0;a<s.length;a++){const c=s[a];if(c.name===t||c.uuid===t)return c;const u=n(c.children);if(u)return u}return null},i=n(e.children);if(i)return i}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)e[t++]=n[i]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let i=0,s=n.length;i!==s;++i)n[i]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,i=t.propertyName;let s=t.propertyIndex;if(e||(e=Ct.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let h=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let f=0;f<e.length;f++)if(e[f].name===h){h=f;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(h!==void 0){if(e[h]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[h]}}const a=e[i];if(a===void 0){const h=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+h+"."+i+" but it wasn't found.",e);return}let c=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?c=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(c=this.Versioning.MatrixWorldNeedsUpdate);let u=this.BindingType.Direct;if(s!==void 0){if(i==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[s]!==void 0&&(s=e.morphTargetDictionary[s])}u=this.BindingType.ArrayElement,this.resolvedProperty=a,this.propertyIndex=s}else a.fromArray!==void 0&&a.toArray!==void 0?(u=this.BindingType.HasFromToArray,this.resolvedProperty=a):Array.isArray(a)?(u=this.BindingType.EntireArray,this.resolvedProperty=a):this.propertyName=i;this.getValue=this.GetterByBindingType[u],this.setValue=this.SetterByBindingTypeAndVersioning[u][c]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}Ct.Composite=cC;Ct.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};Ct.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};Ct.prototype.GetterByBindingType=[Ct.prototype._getValue_direct,Ct.prototype._getValue_array,Ct.prototype._getValue_arrayElement,Ct.prototype._getValue_toArray];Ct.prototype.SetterByBindingTypeAndVersioning=[[Ct.prototype._setValue_direct,Ct.prototype._setValue_direct_setNeedsUpdate,Ct.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[Ct.prototype._setValue_array,Ct.prototype._setValue_array_setNeedsUpdate,Ct.prototype._setValue_array_setMatrixWorldNeedsUpdate],[Ct.prototype._setValue_arrayElement,Ct.prototype._setValue_arrayElement_setNeedsUpdate,Ct.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[Ct.prototype._setValue_fromArray,Ct.prototype._setValue_fromArray_setNeedsUpdate,Ct.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];class lC{constructor(e,t,n=null,i=t.blendMode){this._mixer=e,this._clip=t,this._localRoot=n,this.blendMode=i;const s=t.tracks,a=s.length,c=new Array(a),u={endingStart:Hs,endingEnd:Hs};for(let h=0;h!==a;++h){const f=s[h].createInterpolant(null);c[h]=f,f.settings=u}this._interpolantSettings=u,this._interpolants=c,this._propertyBindings=new Array(a),this._cacheIndex=null,this._byClipCacheIndex=null,this._timeScaleInterpolant=null,this._weightInterpolant=null,this.loop=gd,this._loopCount=-1,this._startTime=null,this.time=0,this.timeScale=1,this._effectiveTimeScale=1,this.weight=1,this._effectiveWeight=1,this.repetitions=1/0,this.paused=!1,this.enabled=!0,this.clampWhenFinished=!1,this.zeroSlopeAtStart=!0,this.zeroSlopeAtEnd=!0}play(){return this._mixer._activateAction(this),this}stop(){return this._mixer._deactivateAction(this),this.reset()}reset(){return this.paused=!1,this.enabled=!0,this.time=0,this._loopCount=-1,this._startTime=null,this.stopFading().stopWarping()}isRunning(){return this.enabled&&!this.paused&&this.timeScale!==0&&this._startTime===null&&this._mixer._isActiveAction(this)}isScheduled(){return this._mixer._isActiveAction(this)}startAt(e){return this._startTime=e,this}setLoop(e,t){return this.loop=e,this.repetitions=t,this}setEffectiveWeight(e){return this.weight=e,this._effectiveWeight=this.enabled?e:0,this.stopFading()}getEffectiveWeight(){return this._effectiveWeight}fadeIn(e){return this._scheduleFading(e,0,1)}fadeOut(e){return this._scheduleFading(e,1,0)}crossFadeFrom(e,t,n){if(e.fadeOut(t),this.fadeIn(t),n){const i=this._clip.duration,s=e._clip.duration,a=s/i,c=i/s;e.warp(1,a,t),this.warp(c,1,t)}return this}crossFadeTo(e,t,n){return e.crossFadeFrom(this,t,n)}stopFading(){const e=this._weightInterpolant;return e!==null&&(this._weightInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}setEffectiveTimeScale(e){return this.timeScale=e,this._effectiveTimeScale=this.paused?0:e,this.stopWarping()}getEffectiveTimeScale(){return this._effectiveTimeScale}setDuration(e){return this.timeScale=this._clip.duration/e,this.stopWarping()}syncWith(e){return this.time=e.time,this.timeScale=e.timeScale,this.stopWarping()}halt(e){return this.warp(this._effectiveTimeScale,0,e)}warp(e,t,n){const i=this._mixer,s=i.time,a=this.timeScale;let c=this._timeScaleInterpolant;c===null&&(c=i._lendControlInterpolant(),this._timeScaleInterpolant=c);const u=c.parameterPositions,h=c.sampleValues;return u[0]=s,u[1]=s+n,h[0]=e/a,h[1]=t/a,this}stopWarping(){const e=this._timeScaleInterpolant;return e!==null&&(this._timeScaleInterpolant=null,this._mixer._takeBackControlInterpolant(e)),this}getMixer(){return this._mixer}getClip(){return this._clip}getRoot(){return this._localRoot||this._mixer._root}_update(e,t,n,i){if(!this.enabled){this._updateWeight(e);return}const s=this._startTime;if(s!==null){const u=(e-s)*n;u<0||n===0?t=0:(this._startTime=null,t=n*u)}t*=this._updateTimeScale(e);const a=this._updateTime(t),c=this._updateWeight(e);if(c>0){const u=this._interpolants,h=this._propertyBindings;switch(this.blendMode){case kT:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulateAdditive(c);break;case _d:default:for(let f=0,p=u.length;f!==p;++f)u[f].evaluate(a),h[f].accumulate(i,c)}}}_updateWeight(e){let t=0;if(this.enabled){t=this.weight;const n=this._weightInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopFading(),i===0&&(this.enabled=!1))}}return this._effectiveWeight=t,t}_updateTimeScale(e){let t=0;if(!this.paused){t=this.timeScale;const n=this._timeScaleInterpolant;if(n!==null){const i=n.evaluate(e)[0];t*=i,e>n.parameterPositions[1]&&(this.stopWarping(),t===0?this.paused=!0:this.timeScale=t)}}return this._effectiveTimeScale=t,t}_updateTime(e){const t=this._clip.duration,n=this.loop;let i=this.time+e,s=this._loopCount;const a=n===BT;if(e===0)return s===-1?i:a&&(s&1)===1?t-i:i;if(n===FT){s===-1&&(this._loopCount=0,this._setEndings(!0,!0,!1));e:{if(i>=t)i=t;else if(i<0)i=0;else{this.time=i;break e}this.clampWhenFinished?this.paused=!0:this.enabled=!1,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e<0?-1:1})}}else{if(s===-1&&(e>=0?(s=0,this._setEndings(!0,this.repetitions===0,a)):this._setEndings(this.repetitions===0,!0,a)),i>=t||i<0){const c=Math.floor(i/t);i-=t*c,s+=Math.abs(c);const u=this.repetitions-s;if(u<=0)this.clampWhenFinished?this.paused=!0:this.enabled=!1,i=e>0?t:0,this.time=i,this._mixer.dispatchEvent({type:"finished",action:this,direction:e>0?1:-1});else{if(u===1){const h=e<0;this._setEndings(h,!h,a)}else this._setEndings(!1,!1,a);this._loopCount=s,this.time=i,this._mixer.dispatchEvent({type:"loop",action:this,loopDelta:c})}}else this.time=i;if(a&&(s&1)===1)return t-i}return i}_setEndings(e,t,n){const i=this._interpolantSettings;n?(i.endingStart=Vs,i.endingEnd=Vs):(e?i.endingStart=this.zeroSlopeAtStart?Vs:Hs:i.endingStart=Nc,t?i.endingEnd=this.zeroSlopeAtEnd?Vs:Hs:i.endingEnd=Nc)}_scheduleFading(e,t,n){const i=this._mixer,s=i.time;let a=this._weightInterpolant;a===null&&(a=i._lendControlInterpolant(),this._weightInterpolant=a);const c=a.parameterPositions,u=a.sampleValues;return c[0]=s,u[0]=t,c[1]=s+e,u[1]=n,this}}const uC=new Float32Array(1);class $g extends Sr{constructor(e){super(),this._root=e,this._initMemoryManager(),this._accuIndex=0,this.time=0,this.timeScale=1}_bindAction(e,t){const n=e._localRoot||this._root,i=e._clip.tracks,s=i.length,a=e._propertyBindings,c=e._interpolants,u=n.uuid,h=this._bindingsByRootAndName;let f=h[u];f===void 0&&(f={},h[u]=f);for(let p=0;p!==s;++p){const m=i[p],g=m.name;let x=f[g];if(x!==void 0)++x.referenceCount,a[p]=x;else{if(x=a[p],x!==void 0){x._cacheIndex===null&&(++x.referenceCount,this._addInactiveBinding(x,u,g));continue}const M=t&&t._propertyBindings[p].binding.parsedPath;x=new QR(Ct.create(n,g,M),m.ValueTypeName,m.getValueSize()),++x.referenceCount,this._addInactiveBinding(x,u,g),a[p]=x}c[p].resultBuffer=x.buffer}}_activateAction(e){if(!this._isActiveAction(e)){if(e._cacheIndex===null){const n=(e._localRoot||this._root).uuid,i=e._clip.uuid,s=this._actionsByClip[i];this._bindAction(e,s&&s.knownActions[0]),this._addInactiveAction(e,i,n)}const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];s.useCount++===0&&(this._lendBinding(s),s.saveOriginalState())}this._lendAction(e)}}_deactivateAction(e){if(this._isActiveAction(e)){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.useCount===0&&(s.restoreOriginalState(),this._takeBackBinding(s))}this._takeBackAction(e)}}_initMemoryManager(){this._actions=[],this._nActiveActions=0,this._actionsByClip={},this._bindings=[],this._nActiveBindings=0,this._bindingsByRootAndName={},this._controlInterpolants=[],this._nActiveControlInterpolants=0;const e=this;this.stats={actions:{get total(){return e._actions.length},get inUse(){return e._nActiveActions}},bindings:{get total(){return e._bindings.length},get inUse(){return e._nActiveBindings}},controlInterpolants:{get total(){return e._controlInterpolants.length},get inUse(){return e._nActiveControlInterpolants}}}}_isActiveAction(e){const t=e._cacheIndex;return t!==null&&t<this._nActiveActions}_addInactiveAction(e,t,n){const i=this._actions,s=this._actionsByClip;let a=s[t];if(a===void 0)a={knownActions:[e],actionByRoot:{}},e._byClipCacheIndex=0,s[t]=a;else{const c=a.knownActions;e._byClipCacheIndex=c.length,c.push(e)}e._cacheIndex=i.length,i.push(e),a.actionByRoot[n]=e}_removeInactiveAction(e){const t=this._actions,n=t[t.length-1],i=e._cacheIndex;n._cacheIndex=i,t[i]=n,t.pop(),e._cacheIndex=null;const s=e._clip.uuid,a=this._actionsByClip,c=a[s],u=c.knownActions,h=u[u.length-1],f=e._byClipCacheIndex;h._byClipCacheIndex=f,u[f]=h,u.pop(),e._byClipCacheIndex=null;const p=c.actionByRoot,m=(e._localRoot||this._root).uuid;delete p[m],u.length===0&&delete a[s],this._removeInactiveBindingsForAction(e)}_removeInactiveBindingsForAction(e){const t=e._propertyBindings;for(let n=0,i=t.length;n!==i;++n){const s=t[n];--s.referenceCount===0&&this._removeInactiveBinding(s)}}_lendAction(e){const t=this._actions,n=e._cacheIndex,i=this._nActiveActions++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackAction(e){const t=this._actions,n=e._cacheIndex,i=--this._nActiveActions,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_addInactiveBinding(e,t,n){const i=this._bindingsByRootAndName,s=this._bindings;let a=i[t];a===void 0&&(a={},i[t]=a),a[n]=e,e._cacheIndex=s.length,s.push(e)}_removeInactiveBinding(e){const t=this._bindings,n=e.binding,i=n.rootNode.uuid,s=n.path,a=this._bindingsByRootAndName,c=a[i],u=t[t.length-1],h=e._cacheIndex;u._cacheIndex=h,t[h]=u,t.pop(),delete c[s],Object.keys(c).length===0&&delete a[i]}_lendBinding(e){const t=this._bindings,n=e._cacheIndex,i=this._nActiveBindings++,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_takeBackBinding(e){const t=this._bindings,n=e._cacheIndex,i=--this._nActiveBindings,s=t[i];e._cacheIndex=i,t[i]=e,s._cacheIndex=n,t[n]=s}_lendControlInterpolant(){const e=this._controlInterpolants,t=this._nActiveControlInterpolants++;let n=e[t];return n===void 0&&(n=new Yg(new Float32Array(2),new Float32Array(2),1,uC),n.__cacheIndex=t,e[t]=n),n}_takeBackControlInterpolant(e){const t=this._controlInterpolants,n=e.__cacheIndex,i=--this._nActiveControlInterpolants,s=t[i];e.__cacheIndex=i,t[i]=e,s.__cacheIndex=n,t[n]=s}clipAction(e,t,n){const i=t||this._root,s=i.uuid;let a=typeof e=="string"?Bc.findByName(i,e):e;const c=a!==null?a.uuid:e,u=this._actionsByClip[c];let h=null;if(n===void 0&&(a!==null?n=a.blendMode:n=_d),u!==void 0){const p=u.actionByRoot[s];if(p!==void 0&&p.blendMode===n)return p;h=u.knownActions[0],a===null&&(a=h._clip)}if(a===null)return null;const f=new lC(this,a,t,n);return this._bindAction(f,h),this._addInactiveAction(f,c,s),f}existingAction(e,t){const n=t||this._root,i=n.uuid,s=typeof e=="string"?Bc.findByName(n,e):e,a=s?s.uuid:e,c=this._actionsByClip[a];return c!==void 0&&c.actionByRoot[i]||null}stopAllAction(){const e=this._actions,t=this._nActiveActions;for(let n=t-1;n>=0;--n)e[n].stop();return this}update(e){e*=this.timeScale;const t=this._actions,n=this._nActiveActions,i=this.time+=e,s=Math.sign(e),a=this._accuIndex^=1;for(let h=0;h!==n;++h)t[h]._update(i,e,s,a);const c=this._bindings,u=this._nActiveBindings;for(let h=0;h!==u;++h)c[h].apply(a);return this}setTime(e){this.time=0;for(let t=0;t<this._actions.length;t++)this._actions[t].time=0;return this.update(e)}getRoot(){return this._root}uncacheClip(e){const t=this._actions,n=e.uuid,i=this._actionsByClip,s=i[n];if(s!==void 0){const a=s.knownActions;for(let c=0,u=a.length;c!==u;++c){const h=a[c];this._deactivateAction(h);const f=h._cacheIndex,p=t[t.length-1];h._cacheIndex=null,h._byClipCacheIndex=null,p._cacheIndex=f,t[f]=p,t.pop(),this._removeInactiveBindingsForAction(h)}delete i[n]}}uncacheRoot(e){const t=e.uuid,n=this._actionsByClip;for(const a in n){const c=n[a].actionByRoot,u=c[t];u!==void 0&&(this._deactivateAction(u),this._removeInactiveAction(u))}const i=this._bindingsByRootAndName,s=i[t];if(s!==void 0)for(const a in s){const c=s[a];c.restoreOriginalState(),this._removeInactiveBinding(c)}}uncacheAction(e,t){const n=this.existingAction(e,t);n!==null&&(this._deactivateAction(n),this._removeInactiveAction(n))}}const Wm=new rt;class Jg{constructor(e,t,n=0,i=1/0){this.ray=new oo(e,t),this.near=n,this.far=i,this.camera=null,this.layers=new yd,this.params={Mesh:{},Line:{threshold:1},LOD:{},Points:{threshold:1},Sprite:{}}}set(e,t){this.ray.set(e,t)}setFromCamera(e,t){t.isPerspectiveCamera?(this.ray.origin.setFromMatrixPosition(t.matrixWorld),this.ray.direction.set(e.x,e.y,.5).unproject(t).sub(this.ray.origin).normalize(),this.camera=t):t.isOrthographicCamera?(this.ray.origin.set(e.x,e.y,(t.near+t.far)/(t.near-t.far)).unproject(t),this.ray.direction.set(0,0,-1).transformDirection(t.matrixWorld),this.camera=t):console.error("THREE.Raycaster: Unsupported camera type: "+t.type)}setFromXRController(e){return Wm.identity().extractRotation(e.matrixWorld),this.ray.origin.setFromMatrixPosition(e.matrixWorld),this.ray.direction.set(0,0,-1).applyMatrix4(Wm),this}intersectObject(e,t=!0,n=[]){return rd(e,this,n,t),n.sort(jm),n}intersectObjects(e,t=!0,n=[]){for(let i=0,s=e.length;i<s;i++)rd(e[i],this,n,t);return n.sort(jm),n}}function jm(r,e){return r.distance-e.distance}function rd(r,e,t,n){let i=!0;if(r.layers.test(e.layers)&&r.raycast(e,t)===!1&&(i=!1),i===!0&&n===!0){const s=r.children;for(let a=0,c=s.length;a<c;a++)rd(s[a],e,t,!0)}}class Xm{constructor(e=1,t=0,n=0){return this.radius=e,this.phi=t,this.theta=n,this}set(e,t,n){return this.radius=e,this.phi=t,this.theta=n,this}copy(e){return this.radius=e.radius,this.phi=e.phi,this.theta=e.theta,this}makeSafe(){return this.phi=Math.max(1e-6,Math.min(Math.PI-1e-6,this.phi)),this}setFromVector3(e){return this.setFromCartesianCoords(e.x,e.y,e.z)}setFromCartesianCoords(e,t,n){return this.radius=Math.sqrt(e*e+t*t+n*n),this.radius===0?(this.theta=0,this.phi=0):(this.theta=Math.atan2(e,n),this.phi=Math.acos(Mn(t/this.radius,-1,1))),this}clone(){return new this.constructor().copy(this)}}const dr=new F,_c=new rt,nh=new rt;class hC extends jg{constructor(e){const t=Qg(e),n=new hn,i=[],s=[],a=new qe(0,0,1),c=new qe(0,1,0);for(let h=0;h<t.length;h++){const f=t[h];f.parent&&f.parent.isBone&&(i.push(0,0,0),i.push(0,0,0),s.push(a.r,a.g,a.b),s.push(c.r,c.g,c.b))}n.setAttribute("position",new zt(i,3)),n.setAttribute("color",new zt(s,3));const u=new Gc({vertexColors:!0,depthTest:!1,depthWrite:!1,toneMapped:!1,transparent:!0});super(n,u),this.isSkeletonHelper=!0,this.type="SkeletonHelper",this.root=e,this.bones=t,this.matrix=e.matrixWorld,this.matrixAutoUpdate=!1}updateMatrixWorld(e){const t=this.bones,n=this.geometry,i=n.getAttribute("position");nh.copy(this.root.matrixWorld).invert();for(let s=0,a=0;s<t.length;s++){const c=t[s];c.parent&&c.parent.isBone&&(_c.multiplyMatrices(nh,c.matrixWorld),dr.setFromMatrixPosition(_c),i.setXYZ(a,dr.x,dr.y,dr.z),_c.multiplyMatrices(nh,c.parent.matrixWorld),dr.setFromMatrixPosition(_c),i.setXYZ(a+1,dr.x,dr.y,dr.z),a+=2)}n.getAttribute("position").needsUpdate=!0,super.updateMatrixWorld(e)}dispose(){this.geometry.dispose(),this.material.dispose()}}function Qg(r){const e=[];r.isBone===!0&&e.push(r);for(let t=0;t<r.children.length;t++)e.push.apply(e,Qg(r.children[t]));return e}class e_ extends Sr{constructor(e,t=null){super(),this.object=e,this.domElement=t,this.enabled=!0,this.state=-1,this.keys={},this.mouseButtons={LEFT:null,MIDDLE:null,RIGHT:null},this.touches={ONE:null,TWO:null}}connect(){}disconnect(){}dispose(){}update(){}}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:"170"}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__="170");var Mi=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},ih={},qm;function ln(){return qm||(qm=1,(function(r){var e=Object.defineProperty,t=Object.defineProperties,n=Object.getOwnPropertyDescriptors,i=Object.getOwnPropertySymbols,s=Object.prototype.hasOwnProperty,a=Object.prototype.propertyIsEnumerable,c=(S,D,G)=>D in S?e(S,D,{enumerable:!0,configurable:!0,writable:!0,value:G}):S[D]=G,u=(S,D)=>{for(var G in D||(D={}))s.call(D,G)&&c(S,G,D[G]);if(i)for(var G of i(D))a.call(D,G)&&c(S,G,D[G]);return S},h=(S,D)=>t(S,n(D)),f=S=>e(S,"__esModule",{value:!0}),p=(S,D)=>{f(S);for(var G in D)e(S,G,{get:D[G],enumerable:!0})};p(r,{Atom:()=>Ma,PointerProxy:()=>Ll,Ticker:()=>Ea,getPointerParts:()=>wr,isPointer:()=>Ii,isPrism:()=>_s,iterateAndCountTicks:()=>Rl,iterateOver:()=>Il,pointer:()=>mo,pointerToPrism:()=>ys,prism:()=>Ir,val:()=>bo});var m=Array.isArray,g=m,x=typeof Mi=="object"&&Mi&&Mi.Object===Object&&Mi,M=x,v=typeof self=="object"&&self&&self.Object===Object&&self,_=M||v||Function("return this")(),A=_,P=A.Symbol,b=P,B=Object.prototype,U=B.hasOwnProperty,O=B.toString,z=b?b.toStringTag:void 0;function I(S){var D=U.call(S,z),G=S[z];try{S[z]=void 0;var se=!0}catch{}var Je=O.call(S);return se&&(D?S[z]=G:delete S[z]),Je}var w=I,H=Object.prototype,ee=H.toString;function Q(S){return ee.call(S)}var ae=Q,ce="[object Null]",$="[object Undefined]",fe=b?b.toStringTag:void 0;function re(S){return S==null?S===void 0?$:ce:fe&&fe in Object(S)?w(S):ae(S)}var ye=re;function Me(S){return S!=null&&typeof S=="object"}var Ne=Me,Ze="[object Symbol]";function ht(S){return typeof S=="symbol"||Ne(S)&&ye(S)==Ze}var le=ht,ge=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,Oe=/^\w*$/;function Se(S,D){if(g(S))return!1;var G=typeof S;return G=="number"||G=="symbol"||G=="boolean"||S==null||le(S)?!0:Oe.test(S)||!ge.test(S)||D!=null&&S in Object(D)}var We=Se;function tt(S){var D=typeof S;return S!=null&&(D=="object"||D=="function")}var st=tt,Tt="[object AsyncFunction]",ot="[object Function]",Ot="[object GeneratorFunction]",X="[object Proxy]";function Qt(S){if(!st(S))return!1;var D=ye(S);return D==ot||D==Ot||D==Tt||D==X}var at=Qt,dt=A["__core-js_shared__"],Ve=dt,xt=(function(){var S=/[^.]+$/.exec(Ve&&Ve.keys&&Ve.keys.IE_PROTO||"");return S?"Symbol(src)_1."+S:""})();function Fe(S){return!!xt&&xt in S}var N=Fe,E=Function.prototype,Z=E.toString;function ue(S){if(S!=null){try{return Z.call(S)}catch{}try{return S+""}catch{}}return""}var pe=ue,de=/[\\^$.*+?()[\]{}|]/g,De=/^\[object .+?Constructor\]$/,Ee=Function.prototype,Re=Object.prototype,ct=Ee.toString,_e=Re.hasOwnProperty,Ce=RegExp("^"+ct.call(_e).replace(de,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function Ue(S){if(!st(S)||N(S))return!1;var D=at(S)?Ce:De;return D.test(pe(S))}var Ye=Ue;function Ie(S,D){return S==null?void 0:S[D]}var pt=Ie;function it(S,D){var G=pt(S,D);return Ye(G)?G:void 0}var V=it,L=V(Object,"create"),J=L;function W(){this.__data__=J?J(null):{},this.size=0}var ie=W;function he(S){var D=this.has(S)&&delete this.__data__[S];return this.size-=D?1:0,D}var me=he,Le="__lodash_hash_undefined__",Ke=Object.prototype,bt=Ke.hasOwnProperty;function et(S){var D=this.__data__;if(J){var G=D[S];return G===Le?void 0:G}return bt.call(D,S)?D[S]:void 0}var Et=et,$t=Object.prototype,Tn=$t.hasOwnProperty;function Kt(S){var D=this.__data__;return J?D[S]!==void 0:Tn.call(D,S)}var Xe=Kt,Ht="__lodash_hash_undefined__";function Bn(S,D){var G=this.__data__;return this.size+=this.has(S)?0:1,G[S]=J&&D===void 0?Ht:D,this}var us=Bn;function jn(S){var D=-1,G=S==null?0:S.length;for(this.clear();++D<G;){var se=S[D];this.set(se[0],se[1])}}jn.prototype.clear=ie,jn.prototype.delete=me,jn.prototype.get=Et,jn.prototype.has=Xe,jn.prototype.set=us;var Mr=jn;function Qi(){this.__data__=[],this.size=0}var hs=Qi;function ni(S,D){return S===D||S!==S&&D!==D}var ho=ni;function Pi(S,D){for(var G=S.length;G--;)if(ho(S[G][0],D))return G;return-1}var er=Pi,R=Array.prototype,j=R.splice;function te(S){var D=this.__data__,G=er(D,S);if(G<0)return!1;var se=D.length-1;return G==se?D.pop():j.call(D,G,1),--this.size,!0}var ne=te;function q(S){var D=this.__data__,G=er(D,S);return G<0?void 0:D[G][1]}var be=q;function Pe(S){return er(this.__data__,S)>-1}var ke=Pe;function ze(S,D){var G=this.__data__,se=er(G,S);return se<0?(++this.size,G.push([S,D])):G[se][1]=D,this}var nt=ze;function $e(S){var D=-1,G=S==null?0:S.length;for(this.clear();++D<G;){var se=S[D];this.set(se[0],se[1])}}$e.prototype.clear=hs,$e.prototype.delete=ne,$e.prototype.get=be,$e.prototype.has=ke,$e.prototype.set=nt;var He=$e,yt=V(A,"Map"),Rt=yt;function It(){this.size=0,this.__data__={hash:new Mr,map:new(Rt||He),string:new Mr}}var Jt=It;function St(S){var D=typeof S;return D=="string"||D=="number"||D=="symbol"||D=="boolean"?S!=="__proto__":S===null}var Ge=St;function Xn(S,D){var G=S.__data__;return Ge(D)?G[typeof D=="string"?"string":"hash"]:G.map}var _t=Xn;function yn(S){var D=_t(this,S).delete(S);return this.size-=D?1:0,D}var yi=yn;function rn(S){return _t(this,S).get(S)}var Ri=rn;function Lt(S){return _t(this,S).has(S)}var kn=Lt;function Ci(S,D){var G=_t(this,S),se=G.size;return G.set(S,D),this.size+=G.size==se?0:1,this}var En=Ci;function xn(S){var D=-1,G=S==null?0:S.length;for(this.clear();++D<G;){var se=S[D];this.set(se[0],se[1])}}xn.prototype.clear=Jt,xn.prototype.delete=yi,xn.prototype.get=Ri,xn.prototype.has=kn,xn.prototype.set=En;var qn=xn,ds="Expected a function";function fo(S,D){if(typeof S!="function"||D!=null&&typeof D!="function")throw new TypeError(ds);var G=function(){var se=arguments,Je=D?D.apply(this,se):se[0],At=G.cache;if(At.has(Je))return At.get(Je);var bn=S.apply(this,se);return G.cache=At.set(Je,bn)||At,bn};return G.cache=new(fo.Cache||qn),G}fo.Cache=qn;var jc=fo,tr=500;function fs(S){var D=jc(S,function(se){return G.size===tr&&G.clear(),se}),G=D.cache;return D}var Xc=fs,Tr=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,qc=/\\(\\)?/g,Yc=Xc(function(S){var D=[];return S.charCodeAt(0)===46&&D.push(""),S.replace(Tr,function(G,se,Je,At){D.push(Je?At.replace(qc,"$1"):se||G)}),D}),Kc=Yc;function Zc(S,D){for(var G=-1,se=S==null?0:S.length,Je=Array(se);++G<se;)Je[G]=D(S[G],G,S);return Je}var $c=Zc,Er=b?b.prototype:void 0,oa=Er?Er.toString:void 0;function aa(S){if(typeof S=="string")return S;if(g(S))return $c(S,aa)+"";if(le(S))return oa?oa.call(S):"";var D=S+"";return D=="0"&&1/S==-1/0?"-0":D}var Jc=aa;function Qc(S){return S==null?"":Jc(S)}var el=Qc;function tl(S,D){return g(S)?S:We(S,D)?[S]:Kc(el(S))}var nl=tl;function il(S){if(typeof S=="string"||le(S))return S;var D=S+"";return D=="0"&&1/S==-1/0?"-0":D}var nr=il;function ps(S,D){D=nl(D,S);for(var G=0,se=D.length;S!=null&&G<se;)S=S[nr(D[G++])];return G&&G==se?S:void 0}var rl=ps;function po(S,D,G){var se=S==null?void 0:rl(S,D);return se===void 0?G:se}var sl=po;function ol(S,D){return function(G){return S(D(G))}}var al=ol,cl=al(Object.getPrototypeOf,Object),ll=cl,ul="[object Object]",hl=Function.prototype,dl=Object.prototype,ca=hl.toString,fl=dl.hasOwnProperty,la=ca.call(Object);function ua(S){if(!Ne(S)||ye(S)!=ul)return!1;var D=ll(S);if(D===null)return!0;var G=fl.call(D,"constructor")&&D.constructor;return typeof G=="function"&&G instanceof G&&ca.call(G)==la}var ha=ua;function da(S){var D=S==null?0:S.length;return D?S[D-1]:void 0}var pl=da,ms=new WeakMap,fa=new WeakMap,Ar=Symbol("pointerMeta"),ml={get(S,D){if(D===Ar)return ms.get(S);let G=fa.get(S);G||(G=new Map,fa.set(S,G));const se=G.get(D);if(se!==void 0)return se;const Je=ms.get(S),At=gs({root:Je.root,path:[...Je.path,D]});return G.set(D,At),At}},li=S=>S[Ar],wr=S=>{const{root:D,path:G}=li(S);return{root:D,path:G}};function gs(S){var D;const G={root:S.root,path:(D=S.path)!=null?D:[]},se={};return ms.set(se,G),new Proxy(se,ml)}var mo=gs,Ii=S=>S&&!!li(S);function pa(S,D,G){return D.length===0?G(S):ir(S,D,G)}var ir=(S,D,G)=>{if(D.length===0)return G(S);if(Array.isArray(S)){let[se,...Je]=D;se=parseInt(String(se),10),isNaN(se)&&(se=0);const At=S[se],bn=ir(At,Je,G);if(At===bn)return S;const ii=[...S];return ii.splice(se,1,bn),ii}else if(typeof S=="object"&&S!==null){const[se,...Je]=D,At=S[se],bn=ir(At,Je,G);return At===bn?S:h(u({},S),{[se]:bn})}else{const[se,...Je]=D;return{[se]:ir(void 0,Je,G)}}},an=class{constructor(){this._head=void 0}peek(){return this._head&&this._head.data}pop(){const S=this._head;if(S)return this._head=S.next,S.data}push(S){const D={next:this._head,data:S};this._head=D}};function _s(S){return!!(S&&S.isPrism&&S.isPrism===!0)}function go(){const S=()=>{},D=new an,G=S;return{type:"Dataverse_discoveryMechanism",startIgnoringDependencies:()=>{D.push(G)},stopIgnoringDependencies:()=>{D.peek()!==G||D.pop()},reportResolutionStart:rr=>{const Lr=D.peek();Lr&&Lr(rr),D.push(G)},reportResolutionEnd:rr=>{D.pop()},pushCollector:rr=>{D.push(rr)},popCollector:rr=>{if(D.peek()!==rr)throw new Error("Popped collector is not on top of the stack");D.pop()}}}function gl(){const S="__dataverse_discoveryMechanism_sharedStack",D=typeof window<"u"?window:typeof Mi<"u"?Mi:{};if(D){const G=D[S];if(G&&typeof G=="object"&&G.type==="Dataverse_discoveryMechanism")return G;{const se=go();return D[S]=se,se}}else return go()}var{startIgnoringDependencies:Li,stopIgnoringDependencies:Pr,reportResolutionEnd:_l,reportResolutionStart:vl,pushCollector:_o,popCollector:yl}=gl(),ma=()=>{},xl=class{constructor(S,D){this._fn=S,this._prismInstance=D,this._didMarkDependentsAsStale=!1,this._isFresh=!1,this._cacheOfDendencyValues=new Map,this._dependents=new Set,this._dependencies=new Set,this._possiblyStaleDeps=new Set,this._scope=new ga(this),this._lastValue=void 0,this._forciblySetToStale=!1,this._reactToDependencyGoingStale=G=>{this._possiblyStaleDeps.add(G),this._markAsStale()};for(const G of this._dependencies)G._addDependent(this._reactToDependencyGoingStale);Li(),this.getValue(),Pr()}get hasDependents(){return this._dependents.size>0}removeDependent(S){this._dependents.delete(S)}addDependent(S){this._dependents.add(S)}destroy(){for(const S of this._dependencies)S._removeDependent(this._reactToDependencyGoingStale);_a(this._scope)}getValue(){if(!this._isFresh){const S=this._recalculate();this._lastValue=S,this._isFresh=!0,this._didMarkDependentsAsStale=!1,this._forciblySetToStale=!1}return this._lastValue}_recalculate(){let S;if(!this._forciblySetToStale&&this._possiblyStaleDeps.size>0){let se=!1;Li();for(const Je of this._possiblyStaleDeps)if(this._cacheOfDendencyValues.get(Je)!==Je.getValue()){se=!0;break}if(Pr(),this._possiblyStaleDeps.clear(),!se)return this._lastValue}const D=new Set;this._cacheOfDendencyValues.clear();const G=se=>{D.add(se),this._addDependency(se)};_o(G),pn.push(this._scope);try{S=this._fn()}catch(se){console.error(se)}finally{pn.pop()!==this._scope&&console.warn("The Prism hook stack has slipped. This is a bug.")}yl(G);for(const se of this._dependencies)D.has(se)||this._removeDependency(se);this._dependencies=D,Li();for(const se of D)this._cacheOfDendencyValues.set(se,se.getValue());return Pr(),S}forceStale(){this._forciblySetToStale=!0,this._markAsStale()}_markAsStale(){if(!this._didMarkDependentsAsStale){this._didMarkDependentsAsStale=!0,this._isFresh=!1;for(const S of this._dependents)S(this._prismInstance)}}_addDependency(S){this._dependencies.has(S)||(this._dependencies.add(S),S._addDependent(this._reactToDependencyGoingStale))}_removeDependency(S){this._dependencies.has(S)&&(this._dependencies.delete(S),S._removeDependent(this._reactToDependencyGoingStale))}},vo={},bl=class{constructor(S){this._fn=S,this.isPrism=!0,this._state={hot:!1,handle:void 0}}get isHot(){return this._state.hot}onChange(S,D,G=!1){const se=()=>{S.onThisOrNextTick(At)};let Je=vo;const At=()=>{const ii=this.getValue();ii!==Je&&(Je=ii,D(ii))};return this._addDependent(se),G&&(Je=this.getValue(),D(Je)),()=>{this._removeDependent(se),S.offThisOrNextTick(At),S.offNextTick(At)}}onStale(S){const D=()=>{this._removeDependent(G)},G=()=>S();return this._addDependent(G),D}keepHot(){return this.onStale(()=>{})}_addDependent(S){this._state.hot||this._goHot(),this._state.handle.addDependent(S)}_goHot(){const S=new xl(this._fn,this);this._state={hot:!0,handle:S}}_removeDependent(S){const D=this._state;if(!D.hot)return;const G=D.handle;G.removeDependent(S),G.hasDependents||(this._state={hot:!1,handle:void 0},G.destroy())}getValue(){vl(this);const S=this._state;let D;return S.hot?D=S.handle.getValue():D=Cr(this._fn),_l(this),D}},ga=class{constructor(S){this._hotHandle=S,this._refs=new Map,this.isPrismScope=!0,this.subs={},this.effects=new Map,this.memos=new Map}ref(S,D){let G=this._refs.get(S);if(G!==void 0)return G;{const se={current:D};return this._refs.set(S,se),se}}effect(S,D,G){let se=this.effects.get(S);se===void 0&&(se={cleanup:ma,deps:void 0},this.effects.set(S,se)),va(se.deps,G)&&(se.cleanup(),Li(),se.cleanup=vs(D,ma).value,Pr(),se.deps=G)}memo(S,D,G){let se=this.memos.get(S);return se===void 0&&(se={cachedValue:null,deps:void 0},this.memos.set(S,se)),va(se.deps,G)&&(Li(),se.cachedValue=vs(D,void 0).value,Pr(),se.deps=G),se.cachedValue}state(S,D){const{value:G,setValue:se}=this.memo("state/"+S,()=>{const Je={current:D};return{value:Je,setValue:bn=>{Je.current=bn,this._hotHandle.forceStale()}}},[]);return[G.current,se]}sub(S){return this.subs[S]||(this.subs[S]=new ga(this._hotHandle)),this.subs[S]}cleanupEffects(){for(const S of this.effects.values())vs(S.cleanup,void 0);this.effects.clear()}source(S,D){return this.effect("$$source/blah",()=>S(()=>{this._hotHandle.forceStale()}),[S]),D()}};function _a(S){for(const D of Object.values(S.subs))_a(D);S.cleanupEffects()}function vs(S,D){try{return{value:S(),ok:!0}}catch(G){return setTimeout(function(){throw G}),{value:D,ok:!1}}}var pn=new an;function Sl(S,D){const G=pn.peek();if(!G)throw new Error("prism.ref() is called outside of a prism() call.");return G.ref(S,D)}function yo(S,D,G){const se=pn.peek();if(!se)throw new Error("prism.effect() is called outside of a prism() call.");return se.effect(S,D,G)}function va(S,D){if(S===void 0||D===void 0)return!0;const G=S.length;if(G!==D.length)return!0;for(let se=0;se<G;se++)if(S[se]!==D[se])return!0;return!1}function ya(S,D,G){const se=pn.peek();if(!se)throw new Error("prism.memo() is called outside of a prism() call.");return se.memo(S,D,G)}function Ln(S,D){const G=pn.peek();if(!G)throw new Error("prism.state() is called outside of a prism() call.");return G.state(S,D)}function Ml(){if(!pn.peek())throw new Error("The parent function is called outside of a prism() call.")}function Tl(S,D){const G=pn.peek();if(!G)throw new Error("prism.scope() is called outside of a prism() call.");const se=G.sub(S);pn.push(se);const Je=vs(D,void 0).value;return pn.pop(),Je}function El(S,D,G){return ya(S,()=>cn(D),G).getValue()}function xa(){return!!pn.peek()}function Al(S,D){const G=pn.peek();if(!G)throw new Error("prism.source() is called outside of a prism() call.");return G.source(S,D)}var cn=S=>new bl(S),Rr=class{effect(S,D,G){console.warn("prism.effect() does not run in cold prisms")}memo(S,D,G){return D()}state(S,D){return[D,()=>{}]}ref(S,D){return{current:D}}sub(S){return new Rr}source(S,D){return D()}};function Cr(S){const D=new Rr;pn.push(D);let G;try{G=S()}catch(se){console.error(se)}finally{pn.pop()!==D&&console.warn("The Prism hook stack has slipped. This is a bug.")}return G}cn.ref=Sl,cn.effect=yo,cn.memo=ya,cn.ensurePrism=Ml,cn.state=Ln,cn.scope=Tl,cn.sub=El,cn.inPrism=xa,cn.source=Al;var Ir=cn,ba;(function(S){S[S.Dict=0]="Dict",S[S.Array=1]="Array",S[S.Other=2]="Other"})(ba||(ba={}));var Dt=S=>Array.isArray(S)?1:ha(S)?0:2,xo=(S,D,G=Dt(S))=>G===0&&typeof D=="string"||G===1&&wl(D)?S[D]:void 0,wl=S=>{const D=typeof S=="number"?S:parseInt(S,10);return!isNaN(D)&&D>=0&&D<1/0&&(D|0)===D},Sa=class{constructor(S,D){this._parent=S,this._path=D,this.children=new Map,this.identityChangeListeners=new Set}addIdentityChangeListener(S){this.identityChangeListeners.add(S)}removeIdentityChangeListener(S){this.identityChangeListeners.delete(S),this._checkForGC()}removeChild(S){this.children.delete(S),this._checkForGC()}getChild(S){return this.children.get(S)}getOrCreateChild(S){let D=this.children.get(S);return D||(D=D=new Sa(this,this._path.concat([S])),this.children.set(S,D)),D}_checkForGC(){this.identityChangeListeners.size>0||this.children.size>0||this._parent&&this._parent.removeChild(pl(this._path))}},Ma=class{constructor(S){this.$$isPointerToPrismProvider=!0,this.pointer=mo({root:this,path:[]}),this.prism=this.pointerToPrism(this.pointer),this._onPointerValueChange=(D,G)=>{const{path:se}=wr(D),Je=this._getOrCreateScopeForPath(se);return Je.identityChangeListeners.add(G),()=>{Je.identityChangeListeners.delete(G)}},this._currentState=S,this._rootScope=new Sa(void 0,[])}set(S){const D=this._currentState;this._currentState=S,this._checkUpdates(this._rootScope,D,S)}get(){return this._currentState}getByPointer(S){const D=Ii(S)?S:S(this.pointer),G=wr(D).path;return this._getIn(G)}_getIn(S){return S.length===0?this.get():sl(this.get(),S)}reduce(S){this.set(S(this.get()))}reduceByPointer(S,D){const G=Ii(S)?S:S(this.pointer),se=wr(G).path,Je=pa(this.get(),se,D);this.set(Je)}setByPointer(S,D){this.reduceByPointer(S,()=>D)}_checkUpdates(S,D,G){if(D===G)return;for(const At of S.identityChangeListeners)At(G);if(S.children.size===0)return;const se=Dt(D),Je=Dt(G);if(!(se===2&&se===Je))for(const[At,bn]of S.children){const ii=xo(D,At,se),Aa=xo(G,At,Je);this._checkUpdates(bn,ii,Aa)}}_getOrCreateScopeForPath(S){let D=this._rootScope;for(const G of S)D=D.getOrCreateChild(G);return D}pointerToPrism(S){const{path:D}=wr(S),G=Je=>this._onPointerValueChange(S,Je),se=()=>this._getIn(D);return Ir(()=>Ir.source(G,se))}},Ta=new WeakMap;function Pl(S){return typeof S=="object"&&S!==null&&S.$$isPointerToPrismProvider===!0}var ys=S=>{const D=li(S);let G=Ta.get(D);if(!G){const se=D.root;if(!Pl(se))throw new Error("Cannot run pointerToPrism() on a pointer whose root is not an PointerToPrismProvider");G=se.pointerToPrism(S),Ta.set(D,G)}return G},bo=S=>Ii(S)?ys(S).getValue():_s(S)?S.getValue():S;function*Rl(S){let D;if(Ii(S))D=ys(S);else if(_s(S))D=S;else throw new Error("Only pointers and prisms are supported");let G=0;const se=D.onStale(()=>{G++});try{for(;;){const Je=G;G=0,yield{value:D.getValue(),ticks:Je}}}finally{se()}}var Cl=180,Ea=class{constructor(S){this._conf=S,this._ticking=!1,this._dormant=!0,this._numberOfDormantTicks=0,this.__ticks=0,this._scheduledForThisOrNextTick=new Set,this._scheduledForNextTick=new Set,this._timeAtCurrentTick=0}get dormant(){return this._dormant}onThisOrNextTick(S){this._scheduledForThisOrNextTick.add(S),this._dormant&&this._goActive()}onNextTick(S){this._scheduledForNextTick.add(S),this._dormant&&this._goActive()}offThisOrNextTick(S){this._scheduledForThisOrNextTick.delete(S)}offNextTick(S){this._scheduledForNextTick.delete(S)}get time(){return this._ticking?this._timeAtCurrentTick:performance.now()}_goActive(){var S,D;this._dormant&&(this._dormant=!1,(D=(S=this._conf)==null?void 0:S.onActive)==null||D.call(S))}_goDormant(){var S,D;this._dormant||(this._dormant=!0,this._numberOfDormantTicks=0,(D=(S=this._conf)==null?void 0:S.onDormant)==null||D.call(S))}tick(S=performance.now()){if(this.__ticks++,!this._dormant&&this._scheduledForNextTick.size===0&&this._scheduledForThisOrNextTick.size===0&&(this._numberOfDormantTicks++,this._numberOfDormantTicks>=Cl)){this._goDormant();return}this._ticking=!0,this._timeAtCurrentTick=S;for(const D of this._scheduledForNextTick)this._scheduledForThisOrNextTick.add(D);this._scheduledForNextTick.clear(),this._tick(0),this._ticking=!1}_tick(S){const D=this.time;if(S>10&&console.warn("_tick() recursing for 10 times"),S>100)throw new Error("Maximum recursion limit for _tick()");const G=this._scheduledForThisOrNextTick;this._scheduledForThisOrNextTick=new Set;for(const se of G)se(D);if(this._scheduledForThisOrNextTick.size>0)return this._tick(S+1)}};function*Il(S){let D;if(Ii(S))D=ys(S);else if(_s(S))D=S;else throw new Error("Only pointers and prisms are supported");const G=new Ea,se=D.onChange(G,Je=>{});try{for(;;)G.tick(),yield D.getValue()}finally{se()}}var Ll=class{constructor(S){this.$$isPointerToPrismProvider=!0,this._currentPointerBox=new Ma(S),this.pointer=mo({root:this,path:[]})}setPointer(S){this._currentPointerBox.set(S)}pointerToPrism(S){const{path:D}=li(S);return Ir(()=>{const G=this._currentPointerBox.prism.getValue(),se=D.reduce((Je,At)=>Je[At],G);return bo(se)})}}})(ih)),ih}const Ym={type:"change"},Id={type:"start"},t_={type:"end"},vc=new oo,Km=new mr,dC=Math.cos(70*wg.DEG2RAD),un=new F,Vn=2*Math.PI,Ft={NONE:-1,ROTATE:0,DOLLY:1,PAN:2,TOUCH_ROTATE:3,TOUCH_PAN:4,TOUCH_DOLLY_PAN:5,TOUCH_DOLLY_ROTATE:6},rh=1e-6;class fC extends e_{constructor(e,t=null){super(e,t),this.state=Ft.NONE,this.enabled=!0,this.target=new F,this.cursor=new F,this.minDistance=0,this.maxDistance=1/0,this.minZoom=0,this.maxZoom=1/0,this.minTargetRadius=0,this.maxTargetRadius=1/0,this.minPolarAngle=0,this.maxPolarAngle=Math.PI,this.minAzimuthAngle=-1/0,this.maxAzimuthAngle=1/0,this.enableDamping=!1,this.dampingFactor=.05,this.enableZoom=!0,this.zoomSpeed=1,this.enableRotate=!0,this.rotateSpeed=1,this.enablePan=!0,this.panSpeed=1,this.screenSpacePanning=!0,this.keyPanSpeed=7,this.zoomToCursor=!1,this.autoRotate=!1,this.autoRotateSpeed=2,this.keys={LEFT:"ArrowLeft",UP:"ArrowUp",RIGHT:"ArrowRight",BOTTOM:"ArrowDown"},this.mouseButtons={LEFT:js.ROTATE,MIDDLE:js.DOLLY,RIGHT:js.PAN},this.touches={ONE:zs.ROTATE,TWO:zs.DOLLY_PAN},this.target0=this.target.clone(),this.position0=this.object.position.clone(),this.zoom0=this.object.zoom,this._domElementKeyEvents=null,this._lastPosition=new F,this._lastQuaternion=new Yt,this._lastTargetPosition=new F,this._quat=new Yt().setFromUnitVectors(e.up,new F(0,1,0)),this._quatInverse=this._quat.clone().invert(),this._spherical=new Xm,this._sphericalDelta=new Xm,this._scale=1,this._panOffset=new F,this._rotateStart=new Qe,this._rotateEnd=new Qe,this._rotateDelta=new Qe,this._panStart=new Qe,this._panEnd=new Qe,this._panDelta=new Qe,this._dollyStart=new Qe,this._dollyEnd=new Qe,this._dollyDelta=new Qe,this._dollyDirection=new F,this._mouse=new Qe,this._performCursorZoom=!1,this._pointers=[],this._pointerPositions={},this._controlActive=!1,this._onPointerMove=mC.bind(this),this._onPointerDown=pC.bind(this),this._onPointerUp=gC.bind(this),this._onContextMenu=MC.bind(this),this._onMouseWheel=yC.bind(this),this._onKeyDown=xC.bind(this),this._onTouchStart=bC.bind(this),this._onTouchMove=SC.bind(this),this._onMouseDown=_C.bind(this),this._onMouseMove=vC.bind(this),this._interceptControlDown=TC.bind(this),this._interceptControlUp=EC.bind(this),this.domElement!==null&&this.connect(),this.update()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointercancel",this._onPointerUp),this.domElement.addEventListener("contextmenu",this._onContextMenu),this.domElement.addEventListener("wheel",this._onMouseWheel,{passive:!1}),this.domElement.getRootNode().addEventListener("keydown",this._interceptControlDown,{passive:!0,capture:!0}),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.removeEventListener("pointercancel",this._onPointerUp),this.domElement.removeEventListener("wheel",this._onMouseWheel),this.domElement.removeEventListener("contextmenu",this._onContextMenu),this.stopListenToKeyEvents(),this.domElement.getRootNode().removeEventListener("keydown",this._interceptControlDown,{capture:!0}),this.domElement.style.touchAction="auto"}dispose(){this.disconnect()}getPolarAngle(){return this._spherical.phi}getAzimuthalAngle(){return this._spherical.theta}getDistance(){return this.object.position.distanceTo(this.target)}listenToKeyEvents(e){e.addEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=e}stopListenToKeyEvents(){this._domElementKeyEvents!==null&&(this._domElementKeyEvents.removeEventListener("keydown",this._onKeyDown),this._domElementKeyEvents=null)}saveState(){this.target0.copy(this.target),this.position0.copy(this.object.position),this.zoom0=this.object.zoom}reset(){this.target.copy(this.target0),this.object.position.copy(this.position0),this.object.zoom=this.zoom0,this.object.updateProjectionMatrix(),this.dispatchEvent(Ym),this.update(),this.state=Ft.NONE}update(e=null){const t=this.object.position;un.copy(t).sub(this.target),un.applyQuaternion(this._quat),this._spherical.setFromVector3(un),this.autoRotate&&this.state===Ft.NONE&&this._rotateLeft(this._getAutoRotationAngle(e)),this.enableDamping?(this._spherical.theta+=this._sphericalDelta.theta*this.dampingFactor,this._spherical.phi+=this._sphericalDelta.phi*this.dampingFactor):(this._spherical.theta+=this._sphericalDelta.theta,this._spherical.phi+=this._sphericalDelta.phi);let n=this.minAzimuthAngle,i=this.maxAzimuthAngle;isFinite(n)&&isFinite(i)&&(n<-Math.PI?n+=Vn:n>Math.PI&&(n-=Vn),i<-Math.PI?i+=Vn:i>Math.PI&&(i-=Vn),n<=i?this._spherical.theta=Math.max(n,Math.min(i,this._spherical.theta)):this._spherical.theta=this._spherical.theta>(n+i)/2?Math.max(n,this._spherical.theta):Math.min(i,this._spherical.theta)),this._spherical.phi=Math.max(this.minPolarAngle,Math.min(this.maxPolarAngle,this._spherical.phi)),this._spherical.makeSafe(),this.enableDamping===!0?this.target.addScaledVector(this._panOffset,this.dampingFactor):this.target.add(this._panOffset),this.target.sub(this.cursor),this.target.clampLength(this.minTargetRadius,this.maxTargetRadius),this.target.add(this.cursor);let s=!1;if(this.zoomToCursor&&this._performCursorZoom||this.object.isOrthographicCamera)this._spherical.radius=this._clampDistance(this._spherical.radius);else{const a=this._spherical.radius;this._spherical.radius=this._clampDistance(this._spherical.radius*this._scale),s=a!=this._spherical.radius}if(un.setFromSpherical(this._spherical),un.applyQuaternion(this._quatInverse),t.copy(this.target).add(un),this.object.lookAt(this.target),this.enableDamping===!0?(this._sphericalDelta.theta*=1-this.dampingFactor,this._sphericalDelta.phi*=1-this.dampingFactor,this._panOffset.multiplyScalar(1-this.dampingFactor)):(this._sphericalDelta.set(0,0,0),this._panOffset.set(0,0,0)),this.zoomToCursor&&this._performCursorZoom){let a=null;if(this.object.isPerspectiveCamera){const c=un.length();a=this._clampDistance(c*this._scale);const u=c-a;this.object.position.addScaledVector(this._dollyDirection,u),this.object.updateMatrixWorld(),s=!!u}else if(this.object.isOrthographicCamera){const c=new F(this._mouse.x,this._mouse.y,0);c.unproject(this.object);const u=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),this.object.updateProjectionMatrix(),s=u!==this.object.zoom;const h=new F(this._mouse.x,this._mouse.y,0);h.unproject(this.object),this.object.position.sub(h).add(c),this.object.updateMatrixWorld(),a=un.length()}else console.warn("WARNING: OrbitControls.js encountered an unknown camera type - zoom to cursor disabled."),this.zoomToCursor=!1;a!==null&&(this.screenSpacePanning?this.target.set(0,0,-1).transformDirection(this.object.matrix).multiplyScalar(a).add(this.object.position):(vc.origin.copy(this.object.position),vc.direction.set(0,0,-1).transformDirection(this.object.matrix),Math.abs(this.object.up.dot(vc.direction))<dC?this.object.lookAt(this.target):(Km.setFromNormalAndCoplanarPoint(this.object.up,this.target),vc.intersectPlane(Km,this.target))))}else if(this.object.isOrthographicCamera){const a=this.object.zoom;this.object.zoom=Math.max(this.minZoom,Math.min(this.maxZoom,this.object.zoom/this._scale)),a!==this.object.zoom&&(this.object.updateProjectionMatrix(),s=!0)}return this._scale=1,this._performCursorZoom=!1,s||this._lastPosition.distanceToSquared(this.object.position)>rh||8*(1-this._lastQuaternion.dot(this.object.quaternion))>rh||this._lastTargetPosition.distanceToSquared(this.target)>rh?(this.dispatchEvent(Ym),this._lastPosition.copy(this.object.position),this._lastQuaternion.copy(this.object.quaternion),this._lastTargetPosition.copy(this.target),!0):!1}_getAutoRotationAngle(e){return e!==null?Vn/60*this.autoRotateSpeed*e:Vn/60/60*this.autoRotateSpeed}_getZoomScale(e){const t=Math.abs(e*.01);return Math.pow(.95,this.zoomSpeed*t)}_rotateLeft(e){this._sphericalDelta.theta-=e}_rotateUp(e){this._sphericalDelta.phi-=e}_panLeft(e,t){un.setFromMatrixColumn(t,0),un.multiplyScalar(-e),this._panOffset.add(un)}_panUp(e,t){this.screenSpacePanning===!0?un.setFromMatrixColumn(t,1):(un.setFromMatrixColumn(t,0),un.crossVectors(this.object.up,un)),un.multiplyScalar(e),this._panOffset.add(un)}_pan(e,t){const n=this.domElement;if(this.object.isPerspectiveCamera){const i=this.object.position;un.copy(i).sub(this.target);let s=un.length();s*=Math.tan(this.object.fov/2*Math.PI/180),this._panLeft(2*e*s/n.clientHeight,this.object.matrix),this._panUp(2*t*s/n.clientHeight,this.object.matrix)}else this.object.isOrthographicCamera?(this._panLeft(e*(this.object.right-this.object.left)/this.object.zoom/n.clientWidth,this.object.matrix),this._panUp(t*(this.object.top-this.object.bottom)/this.object.zoom/n.clientHeight,this.object.matrix)):(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - pan disabled."),this.enablePan=!1)}_dollyOut(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale/=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_dollyIn(e){this.object.isPerspectiveCamera||this.object.isOrthographicCamera?this._scale*=e:(console.warn("WARNING: OrbitControls.js encountered an unknown camera type - dolly/zoom disabled."),this.enableZoom=!1)}_updateZoomParameters(e,t){if(!this.zoomToCursor)return;this._performCursorZoom=!0;const n=this.domElement.getBoundingClientRect(),i=e-n.left,s=t-n.top,a=n.width,c=n.height;this._mouse.x=i/a*2-1,this._mouse.y=-(s/c)*2+1,this._dollyDirection.set(this._mouse.x,this._mouse.y,1).unproject(this.object).sub(this.object.position).normalize()}_clampDistance(e){return Math.max(this.minDistance,Math.min(this.maxDistance,e))}_handleMouseDownRotate(e){this._rotateStart.set(e.clientX,e.clientY)}_handleMouseDownDolly(e){this._updateZoomParameters(e.clientX,e.clientX),this._dollyStart.set(e.clientX,e.clientY)}_handleMouseDownPan(e){this._panStart.set(e.clientX,e.clientY)}_handleMouseMoveRotate(e){this._rotateEnd.set(e.clientX,e.clientY),this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Vn*this._rotateDelta.x/t.clientHeight),this._rotateUp(Vn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd),this.update()}_handleMouseMoveDolly(e){this._dollyEnd.set(e.clientX,e.clientY),this._dollyDelta.subVectors(this._dollyEnd,this._dollyStart),this._dollyDelta.y>0?this._dollyOut(this._getZoomScale(this._dollyDelta.y)):this._dollyDelta.y<0&&this._dollyIn(this._getZoomScale(this._dollyDelta.y)),this._dollyStart.copy(this._dollyEnd),this.update()}_handleMouseMovePan(e){this._panEnd.set(e.clientX,e.clientY),this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd),this.update()}_handleMouseWheel(e){this._updateZoomParameters(e.clientX,e.clientY),e.deltaY<0?this._dollyIn(this._getZoomScale(e.deltaY)):e.deltaY>0&&this._dollyOut(this._getZoomScale(e.deltaY)),this.update()}_handleKeyDown(e){let t=!1;switch(e.code){case this.keys.UP:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(Vn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,this.keyPanSpeed),t=!0;break;case this.keys.BOTTOM:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateUp(-Vn*this.rotateSpeed/this.domElement.clientHeight):this._pan(0,-this.keyPanSpeed),t=!0;break;case this.keys.LEFT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(Vn*this.rotateSpeed/this.domElement.clientHeight):this._pan(this.keyPanSpeed,0),t=!0;break;case this.keys.RIGHT:e.ctrlKey||e.metaKey||e.shiftKey?this._rotateLeft(-Vn*this.rotateSpeed/this.domElement.clientHeight):this._pan(-this.keyPanSpeed,0),t=!0;break}t&&(e.preventDefault(),this.update())}_handleTouchStartRotate(e){if(this._pointers.length===1)this._rotateStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._rotateStart.set(n,i)}}_handleTouchStartPan(e){if(this._pointers.length===1)this._panStart.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panStart.set(n,i)}}_handleTouchStartDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyStart.set(0,s)}_handleTouchStartDollyPan(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enablePan&&this._handleTouchStartPan(e)}_handleTouchStartDollyRotate(e){this.enableZoom&&this._handleTouchStartDolly(e),this.enableRotate&&this._handleTouchStartRotate(e)}_handleTouchMoveRotate(e){if(this._pointers.length==1)this._rotateEnd.set(e.pageX,e.pageY);else{const n=this._getSecondPointerPosition(e),i=.5*(e.pageX+n.x),s=.5*(e.pageY+n.y);this._rotateEnd.set(i,s)}this._rotateDelta.subVectors(this._rotateEnd,this._rotateStart).multiplyScalar(this.rotateSpeed);const t=this.domElement;this._rotateLeft(Vn*this._rotateDelta.x/t.clientHeight),this._rotateUp(Vn*this._rotateDelta.y/t.clientHeight),this._rotateStart.copy(this._rotateEnd)}_handleTouchMovePan(e){if(this._pointers.length===1)this._panEnd.set(e.pageX,e.pageY);else{const t=this._getSecondPointerPosition(e),n=.5*(e.pageX+t.x),i=.5*(e.pageY+t.y);this._panEnd.set(n,i)}this._panDelta.subVectors(this._panEnd,this._panStart).multiplyScalar(this.panSpeed),this._pan(this._panDelta.x,this._panDelta.y),this._panStart.copy(this._panEnd)}_handleTouchMoveDolly(e){const t=this._getSecondPointerPosition(e),n=e.pageX-t.x,i=e.pageY-t.y,s=Math.sqrt(n*n+i*i);this._dollyEnd.set(0,s),this._dollyDelta.set(0,Math.pow(this._dollyEnd.y/this._dollyStart.y,this.zoomSpeed)),this._dollyOut(this._dollyDelta.y),this._dollyStart.copy(this._dollyEnd);const a=(e.pageX+t.x)*.5,c=(e.pageY+t.y)*.5;this._updateZoomParameters(a,c)}_handleTouchMoveDollyPan(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enablePan&&this._handleTouchMovePan(e)}_handleTouchMoveDollyRotate(e){this.enableZoom&&this._handleTouchMoveDolly(e),this.enableRotate&&this._handleTouchMoveRotate(e)}_addPointer(e){this._pointers.push(e.pointerId)}_removePointer(e){delete this._pointerPositions[e.pointerId];for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId){this._pointers.splice(t,1);return}}_isTrackingPointer(e){for(let t=0;t<this._pointers.length;t++)if(this._pointers[t]==e.pointerId)return!0;return!1}_trackPointer(e){let t=this._pointerPositions[e.pointerId];t===void 0&&(t=new Qe,this._pointerPositions[e.pointerId]=t),t.set(e.pageX,e.pageY)}_getSecondPointerPosition(e){const t=e.pointerId===this._pointers[0]?this._pointers[1]:this._pointers[0];return this._pointerPositions[t]}_customWheelEvent(e){const t=e.deltaMode,n={clientX:e.clientX,clientY:e.clientY,deltaY:e.deltaY};switch(t){case 1:n.deltaY*=16;break;case 2:n.deltaY*=100;break}return e.ctrlKey&&!this._controlActive&&(n.deltaY*=10),n}}function pC(r){this.enabled!==!1&&(this._pointers.length===0&&(this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.domElement.addEventListener("pointerup",this._onPointerUp)),!this._isTrackingPointer(r)&&(this._addPointer(r),r.pointerType==="touch"?this._onTouchStart(r):this._onMouseDown(r)))}function mC(r){this.enabled!==!1&&(r.pointerType==="touch"?this._onTouchMove(r):this._onMouseMove(r))}function gC(r){switch(this._removePointer(r),this._pointers.length){case 0:this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.dispatchEvent(t_),this.state=Ft.NONE;break;case 1:const e=this._pointers[0],t=this._pointerPositions[e];this._onTouchStart({pointerId:e,pageX:t.x,pageY:t.y});break}}function _C(r){let e;switch(r.button){case 0:e=this.mouseButtons.LEFT;break;case 1:e=this.mouseButtons.MIDDLE;break;case 2:e=this.mouseButtons.RIGHT;break;default:e=-1}switch(e){case js.DOLLY:if(this.enableZoom===!1)return;this._handleMouseDownDolly(r),this.state=Ft.DOLLY;break;case js.ROTATE:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Ft.PAN}else{if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Ft.ROTATE}break;case js.PAN:if(r.ctrlKey||r.metaKey||r.shiftKey){if(this.enableRotate===!1)return;this._handleMouseDownRotate(r),this.state=Ft.ROTATE}else{if(this.enablePan===!1)return;this._handleMouseDownPan(r),this.state=Ft.PAN}break;default:this.state=Ft.NONE}this.state!==Ft.NONE&&this.dispatchEvent(Id)}function vC(r){switch(this.state){case Ft.ROTATE:if(this.enableRotate===!1)return;this._handleMouseMoveRotate(r);break;case Ft.DOLLY:if(this.enableZoom===!1)return;this._handleMouseMoveDolly(r);break;case Ft.PAN:if(this.enablePan===!1)return;this._handleMouseMovePan(r);break}}function yC(r){this.enabled===!1||this.enableZoom===!1||this.state!==Ft.NONE||(r.preventDefault(),this.dispatchEvent(Id),this._handleMouseWheel(this._customWheelEvent(r)),this.dispatchEvent(t_))}function xC(r){this.enabled===!1||this.enablePan===!1||this._handleKeyDown(r)}function bC(r){switch(this._trackPointer(r),this._pointers.length){case 1:switch(this.touches.ONE){case zs.ROTATE:if(this.enableRotate===!1)return;this._handleTouchStartRotate(r),this.state=Ft.TOUCH_ROTATE;break;case zs.PAN:if(this.enablePan===!1)return;this._handleTouchStartPan(r),this.state=Ft.TOUCH_PAN;break;default:this.state=Ft.NONE}break;case 2:switch(this.touches.TWO){case zs.DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchStartDollyPan(r),this.state=Ft.TOUCH_DOLLY_PAN;break;case zs.DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchStartDollyRotate(r),this.state=Ft.TOUCH_DOLLY_ROTATE;break;default:this.state=Ft.NONE}break;default:this.state=Ft.NONE}this.state!==Ft.NONE&&this.dispatchEvent(Id)}function SC(r){switch(this._trackPointer(r),this.state){case Ft.TOUCH_ROTATE:if(this.enableRotate===!1)return;this._handleTouchMoveRotate(r),this.update();break;case Ft.TOUCH_PAN:if(this.enablePan===!1)return;this._handleTouchMovePan(r),this.update();break;case Ft.TOUCH_DOLLY_PAN:if(this.enableZoom===!1&&this.enablePan===!1)return;this._handleTouchMoveDollyPan(r),this.update();break;case Ft.TOUCH_DOLLY_ROTATE:if(this.enableZoom===!1&&this.enableRotate===!1)return;this._handleTouchMoveDollyRotate(r),this.update();break;default:this.state=Ft.NONE}}function MC(r){this.enabled!==!1&&r.preventDefault()}function TC(r){r.key==="Control"&&(this._controlActive=!0,this.domElement.getRootNode().addEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}function EC(r){r.key==="Control"&&(this._controlActive=!1,this.domElement.getRootNode().removeEventListener("keyup",this._interceptControlUp,{passive:!0,capture:!0}))}const $r=new Jg,In=new F,fr=new F,Zt=new Yt,Zm={X:new F(1,0,0),Y:new F(0,1,0),Z:new F(0,0,1)},sh={type:"change"},$m={type:"mouseDown",mode:null},Jm={type:"mouseUp",mode:null},Qm={type:"objectChange"};class AC extends e_{constructor(e,t=null){super(void 0,t);const n=new LC(this);this._root=n;const i=new DC;this._gizmo=i,n.add(i);const s=new NC;this._plane=s,n.add(s);const a=this;function c(P,b){let B=b;Object.defineProperty(a,P,{get:function(){return B!==void 0?B:b},set:function(U){B!==U&&(B=U,s[P]=U,i[P]=U,a.dispatchEvent({type:P+"-changed",value:U}),a.dispatchEvent(sh))}}),a[P]=b,s[P]=b,i[P]=b}c("camera",e),c("object",void 0),c("enabled",!0),c("axis",null),c("mode","translate"),c("translationSnap",null),c("rotationSnap",null),c("scaleSnap",null),c("space","world"),c("size",1),c("dragging",!1),c("showX",!0),c("showY",!0),c("showZ",!0),c("minX",-1/0),c("maxX",1/0),c("minY",-1/0),c("maxY",1/0),c("minZ",-1/0),c("maxZ",1/0);const u=new F,h=new F,f=new Yt,p=new Yt,m=new F,g=new Yt,x=new F,M=new F,v=new F,_=0,A=new F;c("worldPosition",u),c("worldPositionStart",h),c("worldQuaternion",f),c("worldQuaternionStart",p),c("cameraPosition",m),c("cameraQuaternion",g),c("pointStart",x),c("pointEnd",M),c("rotationAxis",v),c("rotationAngle",_),c("eye",A),this._offset=new F,this._startNorm=new F,this._endNorm=new F,this._cameraScale=new F,this._parentPosition=new F,this._parentQuaternion=new Yt,this._parentQuaternionInv=new Yt,this._parentScale=new F,this._worldScaleStart=new F,this._worldQuaternionInv=new Yt,this._worldScale=new F,this._positionStart=new F,this._quaternionStart=new Yt,this._scaleStart=new F,this._getPointer=wC.bind(this),this._onPointerDown=RC.bind(this),this._onPointerHover=PC.bind(this),this._onPointerMove=CC.bind(this),this._onPointerUp=IC.bind(this),t!==null&&this.connect()}connect(){this.domElement.addEventListener("pointerdown",this._onPointerDown),this.domElement.addEventListener("pointermove",this._onPointerHover),this.domElement.addEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="none"}disconnect(){this.domElement.removeEventListener("pointerdown",this._onPointerDown),this.domElement.removeEventListener("pointermove",this._onPointerHover),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.domElement.removeEventListener("pointerup",this._onPointerUp),this.domElement.style.touchAction="auto"}getHelper(){return this._root}pointerHover(e){if(this.object===void 0||this.dragging===!0)return;e!==null&&$r.setFromCamera(e,this.camera);const t=oh(this._gizmo.picker[this.mode],$r);t?this.axis=t.object.name:this.axis=null}pointerDown(e){if(!(this.object===void 0||this.dragging===!0||e!=null&&e.button!==0)&&this.axis!==null){e!==null&&$r.setFromCamera(e,this.camera);const t=oh(this._plane,$r,!0);t&&(this.object.updateMatrixWorld(),this.object.parent.updateMatrixWorld(),this._positionStart.copy(this.object.position),this._quaternionStart.copy(this.object.quaternion),this._scaleStart.copy(this.object.scale),this.object.matrixWorld.decompose(this.worldPositionStart,this.worldQuaternionStart,this._worldScaleStart),this.pointStart.copy(t.point).sub(this.worldPositionStart)),this.dragging=!0,$m.mode=this.mode,this.dispatchEvent($m)}}pointerMove(e){const t=this.axis,n=this.mode,i=this.object;let s=this.space;if(n==="scale"?s="local":(t==="E"||t==="XYZE"||t==="XYZ")&&(s="world"),i===void 0||t===null||this.dragging===!1||e!==null&&e.button!==-1)return;e!==null&&$r.setFromCamera(e,this.camera);const a=oh(this._plane,$r,!0);if(a){if(this.pointEnd.copy(a.point).sub(this.worldPositionStart),n==="translate")this._offset.copy(this.pointEnd).sub(this.pointStart),s==="local"&&t!=="XYZ"&&this._offset.applyQuaternion(this._worldQuaternionInv),t.indexOf("X")===-1&&(this._offset.x=0),t.indexOf("Y")===-1&&(this._offset.y=0),t.indexOf("Z")===-1&&(this._offset.z=0),s==="local"&&t!=="XYZ"?this._offset.applyQuaternion(this._quaternionStart).divide(this._parentScale):this._offset.applyQuaternion(this._parentQuaternionInv).divide(this._parentScale),i.position.copy(this._offset).add(this._positionStart),this.translationSnap&&(s==="local"&&(i.position.applyQuaternion(Zt.copy(this._quaternionStart).invert()),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.position.applyQuaternion(this._quaternionStart)),s==="world"&&(i.parent&&i.position.add(In.setFromMatrixPosition(i.parent.matrixWorld)),t.search("X")!==-1&&(i.position.x=Math.round(i.position.x/this.translationSnap)*this.translationSnap),t.search("Y")!==-1&&(i.position.y=Math.round(i.position.y/this.translationSnap)*this.translationSnap),t.search("Z")!==-1&&(i.position.z=Math.round(i.position.z/this.translationSnap)*this.translationSnap),i.parent&&i.position.sub(In.setFromMatrixPosition(i.parent.matrixWorld)))),i.position.x=Math.max(this.minX,Math.min(this.maxX,i.position.x)),i.position.y=Math.max(this.minY,Math.min(this.maxY,i.position.y)),i.position.z=Math.max(this.minZ,Math.min(this.maxZ,i.position.z));else if(n==="scale"){if(t.search("XYZ")!==-1){let c=this.pointEnd.length()/this.pointStart.length();this.pointEnd.dot(this.pointStart)<0&&(c*=-1),fr.set(c,c,c)}else In.copy(this.pointStart),fr.copy(this.pointEnd),In.applyQuaternion(this._worldQuaternionInv),fr.applyQuaternion(this._worldQuaternionInv),fr.divide(In),t.search("X")===-1&&(fr.x=1),t.search("Y")===-1&&(fr.y=1),t.search("Z")===-1&&(fr.z=1);i.scale.copy(this._scaleStart).multiply(fr),this.scaleSnap&&(t.search("X")!==-1&&(i.scale.x=Math.round(i.scale.x/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Y")!==-1&&(i.scale.y=Math.round(i.scale.y/this.scaleSnap)*this.scaleSnap||this.scaleSnap),t.search("Z")!==-1&&(i.scale.z=Math.round(i.scale.z/this.scaleSnap)*this.scaleSnap||this.scaleSnap))}else if(n==="rotate"){this._offset.copy(this.pointEnd).sub(this.pointStart);const c=20/this.worldPosition.distanceTo(In.setFromMatrixPosition(this.camera.matrixWorld));let u=!1;t==="XYZE"?(this.rotationAxis.copy(this._offset).cross(this.eye).normalize(),this.rotationAngle=this._offset.dot(In.copy(this.rotationAxis).cross(this.eye))*c):(t==="X"||t==="Y"||t==="Z")&&(this.rotationAxis.copy(Zm[t]),In.copy(Zm[t]),s==="local"&&In.applyQuaternion(this.worldQuaternion),In.cross(this.eye),In.length()===0?u=!0:this.rotationAngle=this._offset.dot(In.normalize())*c),(t==="E"||u)&&(this.rotationAxis.copy(this.eye),this.rotationAngle=this.pointEnd.angleTo(this.pointStart),this._startNorm.copy(this.pointStart).normalize(),this._endNorm.copy(this.pointEnd).normalize(),this.rotationAngle*=this._endNorm.cross(this._startNorm).dot(this.eye)<0?1:-1),this.rotationSnap&&(this.rotationAngle=Math.round(this.rotationAngle/this.rotationSnap)*this.rotationSnap),s==="local"&&t!=="E"&&t!=="XYZE"?(i.quaternion.copy(this._quaternionStart),i.quaternion.multiply(Zt.setFromAxisAngle(this.rotationAxis,this.rotationAngle)).normalize()):(this.rotationAxis.applyQuaternion(this._parentQuaternionInv),i.quaternion.copy(Zt.setFromAxisAngle(this.rotationAxis,this.rotationAngle)),i.quaternion.multiply(this._quaternionStart).normalize())}this.dispatchEvent(sh),this.dispatchEvent(Qm)}}pointerUp(e){e!==null&&e.button!==0||(this.dragging&&this.axis!==null&&(Jm.mode=this.mode,this.dispatchEvent(Jm)),this.dragging=!1,this.axis=null)}dispose(){this.disconnect(),this._root.dispose()}attach(e){return this.object=e,this._root.visible=!0,this}detach(){return this.object=void 0,this.axis=null,this._root.visible=!1,this}reset(){this.enabled&&this.dragging&&(this.object.position.copy(this._positionStart),this.object.quaternion.copy(this._quaternionStart),this.object.scale.copy(this._scaleStart),this.dispatchEvent(sh),this.dispatchEvent(Qm),this.pointStart.copy(this.pointEnd))}getRaycaster(){return $r}getMode(){return this.mode}setMode(e){this.mode=e}setTranslationSnap(e){this.translationSnap=e}setRotationSnap(e){this.rotationSnap=e}setScaleSnap(e){this.scaleSnap=e}setSize(e){this.size=e}setSpace(e){this.space=e}}function wC(r){if(this.domElement.ownerDocument.pointerLockElement)return{x:0,y:0,button:r.button};{const e=this.domElement.getBoundingClientRect();return{x:(r.clientX-e.left)/e.width*2-1,y:-(r.clientY-e.top)/e.height*2+1,button:r.button}}}function PC(r){if(this.enabled)switch(r.pointerType){case"mouse":case"pen":this.pointerHover(this._getPointer(r));break}}function RC(r){this.enabled&&(document.pointerLockElement||this.domElement.setPointerCapture(r.pointerId),this.domElement.addEventListener("pointermove",this._onPointerMove),this.pointerHover(this._getPointer(r)),this.pointerDown(this._getPointer(r)))}function CC(r){this.enabled&&this.pointerMove(this._getPointer(r))}function IC(r){this.enabled&&(this.domElement.releasePointerCapture(r.pointerId),this.domElement.removeEventListener("pointermove",this._onPointerMove),this.pointerUp(this._getPointer(r)))}function oh(r,e,t){const n=e.intersectObject(r,!0);for(let i=0;i<n.length;i++)if(n[i].object.visible||t)return n[i];return!1}const yc=new vi,kt=new F(0,1,0),eg=new F(0,0,0),tg=new rt,xc=new Yt,Ic=new Yt,bi=new F,ng=new rt,Xo=new F(1,0,0),es=new F(0,1,0),qo=new F(0,0,1),bc=new F,zo=new F,Ho=new F;class LC extends Xt{constructor(e){super(),this.isTransformControlsRoot=!0,this.controls=e,this.visible=!1}updateMatrixWorld(e){const t=this.controls;t.object!==void 0&&(t.object.updateMatrixWorld(),t.object.parent===null?console.error("TransformControls: The attached 3D object must be a part of the scene graph."):t.object.parent.matrixWorld.decompose(t._parentPosition,t._parentQuaternion,t._parentScale),t.object.matrixWorld.decompose(t.worldPosition,t.worldQuaternion,t._worldScale),t._parentQuaternionInv.copy(t._parentQuaternion).invert(),t._worldQuaternionInv.copy(t.worldQuaternion).invert()),t.camera.updateMatrixWorld(),t.camera.matrixWorld.decompose(t.cameraPosition,t.cameraQuaternion,t._cameraScale),t.camera.isOrthographicCamera?t.camera.getWorldDirection(t.eye).negate():t.eye.copy(t.cameraPosition).sub(t.worldPosition).normalize(),super.updateMatrixWorld(e)}dispose(){this.traverse(function(e){e.geometry&&e.geometry.dispose(),e.material&&e.material.dispose()})}}class DC extends Xt{constructor(){super(),this.isTransformControlsGizmo=!0,this.type="TransformControlsGizmo";const e=new ci({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),t=new Gc({depthTest:!1,depthWrite:!1,fog:!1,toneMapped:!1,transparent:!0}),n=e.clone();n.opacity=.15;const i=t.clone();i.opacity=.5;const s=e.clone();s.color.setHex(16711680);const a=e.clone();a.color.setHex(65280);const c=e.clone();c.color.setHex(255);const u=e.clone();u.color.setHex(16711680),u.opacity=.5;const h=e.clone();h.color.setHex(65280),h.opacity=.5;const f=e.clone();f.color.setHex(255),f.opacity=.5;const p=e.clone();p.opacity=.25;const m=e.clone();m.color.setHex(16776960),m.opacity=.25,e.clone().color.setHex(16776960);const x=e.clone();x.color.setHex(7895160);const M=new Sn(0,.04,.1,12);M.translate(0,.05,0);const v=new en(.08,.08,.08);v.translate(0,.04,0);const _=new hn;_.setAttribute("position",new zt([0,0,0,1,0,0],3));const A=new Sn(.0075,.0075,.5,3);A.translate(0,.25,0);function P(ce,$){const fe=new is(ce,.0075,3,64,$*Math.PI*2);return fe.rotateY(Math.PI/2),fe.rotateX(Math.PI/2),fe}function b(){const ce=new hn;return ce.setAttribute("position",new zt([0,0,0,1,1,1],3)),ce}const B={X:[[new Te(M,s),[.5,0,0],[0,0,-Math.PI/2]],[new Te(M,s),[-.5,0,0],[0,0,Math.PI/2]],[new Te(A,s),[0,0,0],[0,0,-Math.PI/2]]],Y:[[new Te(M,a),[0,.5,0]],[new Te(M,a),[0,-.5,0],[Math.PI,0,0]],[new Te(A,a)]],Z:[[new Te(M,c),[0,0,.5],[Math.PI/2,0,0]],[new Te(M,c),[0,0,-.5],[-Math.PI/2,0,0]],[new Te(A,c),null,[Math.PI/2,0,0]]],XYZ:[[new Te(new Ws(.1,0),p.clone()),[0,0,0]]],XY:[[new Te(new en(.15,.15,.01),f.clone()),[.15,.15,0]]],YZ:[[new Te(new en(.15,.15,.01),u.clone()),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Te(new en(.15,.15,.01),h.clone()),[.15,0,.15],[-Math.PI/2,0,0]]]},U={X:[[new Te(new Sn(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Te(new Sn(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Te(new Sn(.2,0,.6,4),n),[0,.3,0]],[new Te(new Sn(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Te(new Sn(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Te(new Sn(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XYZ:[[new Te(new Ws(.2,0),n)]],XY:[[new Te(new en(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Te(new en(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Te(new en(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]]},O={START:[[new Te(new Ws(.01,2),i),null,null,null,"helper"]],END:[[new Te(new Ws(.01,2),i),null,null,null,"helper"]],DELTA:[[new fi(b(),i),null,null,null,"helper"]],X:[[new fi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new fi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new fi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]},z={XYZE:[[new Te(P(.5,1),x),null,[0,Math.PI/2,0]]],X:[[new Te(P(.5,.5),s)]],Y:[[new Te(P(.5,.5),a),null,[0,0,-Math.PI/2]]],Z:[[new Te(P(.5,.5),c),null,[0,Math.PI/2,0]]],E:[[new Te(P(.75,1),m),null,[0,Math.PI/2,0]]]},I={AXIS:[[new fi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]]},w={XYZE:[[new Te(new ra(.25,10,8),n)]],X:[[new Te(new is(.5,.1,4,24),n),[0,0,0],[0,-Math.PI/2,-Math.PI/2]]],Y:[[new Te(new is(.5,.1,4,24),n),[0,0,0],[Math.PI/2,0,0]]],Z:[[new Te(new is(.5,.1,4,24),n),[0,0,0],[0,0,-Math.PI/2]]],E:[[new Te(new is(.75,.1,2,24),n)]]},H={X:[[new Te(v,s),[.5,0,0],[0,0,-Math.PI/2]],[new Te(A,s),[0,0,0],[0,0,-Math.PI/2]],[new Te(v,s),[-.5,0,0],[0,0,Math.PI/2]]],Y:[[new Te(v,a),[0,.5,0]],[new Te(A,a)],[new Te(v,a),[0,-.5,0],[0,0,Math.PI]]],Z:[[new Te(v,c),[0,0,.5],[Math.PI/2,0,0]],[new Te(A,c),[0,0,0],[Math.PI/2,0,0]],[new Te(v,c),[0,0,-.5],[-Math.PI/2,0,0]]],XY:[[new Te(new en(.15,.15,.01),f),[.15,.15,0]]],YZ:[[new Te(new en(.15,.15,.01),u),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Te(new en(.15,.15,.01),h),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Te(new en(.1,.1,.1),p.clone())]]},ee={X:[[new Te(new Sn(.2,0,.6,4),n),[.3,0,0],[0,0,-Math.PI/2]],[new Te(new Sn(.2,0,.6,4),n),[-.3,0,0],[0,0,Math.PI/2]]],Y:[[new Te(new Sn(.2,0,.6,4),n),[0,.3,0]],[new Te(new Sn(.2,0,.6,4),n),[0,-.3,0],[0,0,Math.PI]]],Z:[[new Te(new Sn(.2,0,.6,4),n),[0,0,.3],[Math.PI/2,0,0]],[new Te(new Sn(.2,0,.6,4),n),[0,0,-.3],[-Math.PI/2,0,0]]],XY:[[new Te(new en(.2,.2,.01),n),[.15,.15,0]]],YZ:[[new Te(new en(.2,.2,.01),n),[0,.15,.15],[0,Math.PI/2,0]]],XZ:[[new Te(new en(.2,.2,.01),n),[.15,0,.15],[-Math.PI/2,0,0]]],XYZ:[[new Te(new en(.2,.2,.2),n),[0,0,0]]]},Q={X:[[new fi(_,i.clone()),[-1e3,0,0],null,[1e6,1,1],"helper"]],Y:[[new fi(_,i.clone()),[0,-1e3,0],[0,0,Math.PI/2],[1e6,1,1],"helper"]],Z:[[new fi(_,i.clone()),[0,0,-1e3],[0,-Math.PI/2,0],[1e6,1,1],"helper"]]};function ae(ce){const $=new Xt;for(const fe in ce)for(let re=ce[fe].length;re--;){const ye=ce[fe][re][0].clone(),Me=ce[fe][re][1],Ne=ce[fe][re][2],Ze=ce[fe][re][3],ht=ce[fe][re][4];ye.name=fe,ye.tag=ht,Me&&ye.position.set(Me[0],Me[1],Me[2]),Ne&&ye.rotation.set(Ne[0],Ne[1],Ne[2]),Ze&&ye.scale.set(Ze[0],Ze[1],Ze[2]),ye.updateMatrix();const le=ye.geometry.clone();le.applyMatrix4(ye.matrix),ye.geometry=le,ye.renderOrder=1/0,ye.position.set(0,0,0),ye.rotation.set(0,0,0),ye.scale.set(1,1,1),$.add(ye)}return $}this.gizmo={},this.picker={},this.helper={},this.add(this.gizmo.translate=ae(B)),this.add(this.gizmo.rotate=ae(z)),this.add(this.gizmo.scale=ae(H)),this.add(this.picker.translate=ae(U)),this.add(this.picker.rotate=ae(w)),this.add(this.picker.scale=ae(ee)),this.add(this.helper.translate=ae(O)),this.add(this.helper.rotate=ae(I)),this.add(this.helper.scale=ae(Q)),this.picker.translate.visible=!1,this.picker.rotate.visible=!1,this.picker.scale.visible=!1}updateMatrixWorld(e){const n=(this.mode==="scale"?"local":this.space)==="local"?this.worldQuaternion:Ic;this.gizmo.translate.visible=this.mode==="translate",this.gizmo.rotate.visible=this.mode==="rotate",this.gizmo.scale.visible=this.mode==="scale",this.helper.translate.visible=this.mode==="translate",this.helper.rotate.visible=this.mode==="rotate",this.helper.scale.visible=this.mode==="scale";let i=[];i=i.concat(this.picker[this.mode].children),i=i.concat(this.gizmo[this.mode].children),i=i.concat(this.helper[this.mode].children);for(let s=0;s<i.length;s++){const a=i[s];a.visible=!0,a.rotation.set(0,0,0),a.position.copy(this.worldPosition);let c;if(this.camera.isOrthographicCamera?c=(this.camera.top-this.camera.bottom)/this.camera.zoom:c=this.worldPosition.distanceTo(this.cameraPosition)*Math.min(1.9*Math.tan(Math.PI*this.camera.fov/360)/this.camera.zoom,7),a.scale.set(1,1,1).multiplyScalar(c*this.size/4),a.tag==="helper"){a.visible=!1,a.name==="AXIS"?(a.visible=!!this.axis,this.axis==="X"&&(Zt.setFromEuler(yc.set(0,0,0)),a.quaternion.copy(n).multiply(Zt),Math.abs(kt.copy(Xo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Y"&&(Zt.setFromEuler(yc.set(0,0,Math.PI/2)),a.quaternion.copy(n).multiply(Zt),Math.abs(kt.copy(es).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="Z"&&(Zt.setFromEuler(yc.set(0,Math.PI/2,0)),a.quaternion.copy(n).multiply(Zt),Math.abs(kt.copy(qo).applyQuaternion(n).dot(this.eye))>.9&&(a.visible=!1)),this.axis==="XYZE"&&(Zt.setFromEuler(yc.set(0,Math.PI/2,0)),kt.copy(this.rotationAxis),a.quaternion.setFromRotationMatrix(tg.lookAt(eg,kt,es)),a.quaternion.multiply(Zt),a.visible=this.dragging),this.axis==="E"&&(a.visible=!1)):a.name==="START"?(a.position.copy(this.worldPositionStart),a.visible=this.dragging):a.name==="END"?(a.position.copy(this.worldPosition),a.visible=this.dragging):a.name==="DELTA"?(a.position.copy(this.worldPositionStart),a.quaternion.copy(this.worldQuaternionStart),In.set(1e-10,1e-10,1e-10).add(this.worldPositionStart).sub(this.worldPosition).multiplyScalar(-1),In.applyQuaternion(this.worldQuaternionStart.clone().invert()),a.scale.copy(In),a.visible=this.dragging):(a.quaternion.copy(n),this.dragging?a.position.copy(this.worldPositionStart):a.position.copy(this.worldPosition),this.axis&&(a.visible=this.axis.search(a.name)!==-1));continue}a.quaternion.copy(n),this.mode==="translate"||this.mode==="scale"?(a.name==="X"&&Math.abs(kt.copy(Xo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Y"&&Math.abs(kt.copy(es).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="Z"&&Math.abs(kt.copy(qo).applyQuaternion(n).dot(this.eye))>.99&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XY"&&Math.abs(kt.copy(qo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="YZ"&&Math.abs(kt.copy(Xo).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1),a.name==="XZ"&&Math.abs(kt.copy(es).applyQuaternion(n).dot(this.eye))<.2&&(a.scale.set(1e-10,1e-10,1e-10),a.visible=!1)):this.mode==="rotate"&&(xc.copy(n),kt.copy(this.eye).applyQuaternion(Zt.copy(n).invert()),a.name.search("E")!==-1&&a.quaternion.setFromRotationMatrix(tg.lookAt(this.eye,eg,es)),a.name==="X"&&(Zt.setFromAxisAngle(Xo,Math.atan2(-kt.y,kt.z)),Zt.multiplyQuaternions(xc,Zt),a.quaternion.copy(Zt)),a.name==="Y"&&(Zt.setFromAxisAngle(es,Math.atan2(kt.x,kt.z)),Zt.multiplyQuaternions(xc,Zt),a.quaternion.copy(Zt)),a.name==="Z"&&(Zt.setFromAxisAngle(qo,Math.atan2(kt.y,kt.x)),Zt.multiplyQuaternions(xc,Zt),a.quaternion.copy(Zt))),a.visible=a.visible&&(a.name.indexOf("X")===-1||this.showX),a.visible=a.visible&&(a.name.indexOf("Y")===-1||this.showY),a.visible=a.visible&&(a.name.indexOf("Z")===-1||this.showZ),a.visible=a.visible&&(a.name.indexOf("E")===-1||this.showX&&this.showY&&this.showZ),a.material._color=a.material._color||a.material.color.clone(),a.material._opacity=a.material._opacity||a.material.opacity,a.material.color.copy(a.material._color),a.material.opacity=a.material._opacity,this.enabled&&this.axis&&(a.name===this.axis||this.axis.split("").some(function(u){return a.name===u}))&&(a.material.color.setHex(16776960),a.material.opacity=1)}super.updateMatrixWorld(e)}}class NC extends Te{constructor(){super(new ao(1e5,1e5,2,2),new ci({visible:!1,wireframe:!0,side:Gn,transparent:!0,opacity:.1,toneMapped:!1})),this.isTransformControlsPlane=!0,this.type="TransformControlsPlane"}updateMatrixWorld(e){let t=this.space;switch(this.position.copy(this.worldPosition),this.mode==="scale"&&(t="local"),bc.copy(Xo).applyQuaternion(t==="local"?this.worldQuaternion:Ic),zo.copy(es).applyQuaternion(t==="local"?this.worldQuaternion:Ic),Ho.copy(qo).applyQuaternion(t==="local"?this.worldQuaternion:Ic),kt.copy(zo),this.mode){case"translate":case"scale":switch(this.axis){case"X":kt.copy(this.eye).cross(bc),bi.copy(bc).cross(kt);break;case"Y":kt.copy(this.eye).cross(zo),bi.copy(zo).cross(kt);break;case"Z":kt.copy(this.eye).cross(Ho),bi.copy(Ho).cross(kt);break;case"XY":bi.copy(Ho);break;case"YZ":bi.copy(bc);break;case"XZ":kt.copy(Ho),bi.copy(zo);break;case"XYZ":case"E":bi.set(0,0,0);break}break;case"rotate":default:bi.set(0,0,0)}bi.length()===0?this.quaternion.copy(this.cameraQuaternion):(ng.lookAt(In.set(0,0,0),bi,kt),this.quaternion.setFromRotationMatrix(ng)),super.updateMatrixWorld(e)}}function ah(r){const e=new Yi,t=new Ed(.4,1,16),n=new ci({color:r,transparent:!0,opacity:1,side:Gn,depthTest:!1,depthWrite:!1}),i=new Te(t,n);i.rotation.x=Math.PI,i.renderOrder=999;const s=new ra(.35,32,32),a=new ci({color:new qe(1,1,1),emissive:r,emissiveIntensity:2,transparent:!0,opacity:1,depthTest:!1,depthWrite:!1}),c=new Te(s,a);return c.position.y=.5,c.renderOrder=999,e.add(i),e.add(c),e}function OC(r){const e=new ER({canvas:r,antialias:!0});e.setPixelRatio(window.devicePixelRatio),e.setSize(r.clientWidth,r.clientHeight),e.shadowMap.enabled=!1,e.toneMapping=dg,e.toneMappingExposure=1.6,e.outputColorSpace=_n;const t=new AR;t.background=new qe(1381664),t.fog=new Md(1381664,.03);const n=new On(50,r.clientWidth/r.clientHeight,.1,1e3);n.position.set(0,1.6,5);const i=new fC(n,r);i.target.set(0,.9,0),i.enableDamping=!0,i.dampingFactor=.08,i.update();const s=new ao(14,10),a=new os({color:4864558,roughness:.35,metalness:.05}),c=new Te(s,a);c.rotation.x=-Math.PI/2,c.position.y=-.01,c.receiveShadow=!0,t.add(c);const u=new en(14.2,.06,10.2),h=new os({color:3811866,roughness:.6}),f=new Te(u,h);f.position.y=-.04,f.receiveShadow=!0,t.add(f);const p=new ZR(16777215,.8);t.add(p);const m=new Cc(16777215,3);m.position.set(2,4,-5),t.add(m);const g=ah(new qe(16777215));g.position.copy(m.position),g.lookAt(new F(0,0,0)),g.userData.light=m,t.add(g);const x=new Cc(15658751,2);x.position.set(-3,3,-4),t.add(x);const M=ah(new qe(15658751));M.position.copy(x.position),M.lookAt(new F(0,0,0)),M.userData.light=x,t.add(M);const v=new Cc(16772829,2.5);v.position.set(0,4,5),t.add(v);const _=ah(new qe(16772829));_.position.copy(v.position),_.lookAt(new F(0,0,0)),_.userData.light=v,t.add(_);const A={ambient:p,spotLeft:m,spotRight:x,backLight:v},P={spotLeftIcon:g,spotRightIcon:M,backLightIcon:_},b=new AC(n,r);b.setMode("translate"),b.setSize(.8),t.add(b),b.addEventListener("dragging-changed",U=>{i.enabled=!U.value});function B(){const U=r.clientWidth,O=r.clientHeight;e.setSize(U,O),n.aspect=U/O,n.updateProjectionMatrix()}return window.addEventListener("resize",B),{scene:t,camera:n,renderer:e,controls:i,lights:A,lightIcons:P,transformControls:b}}var Yo={exports:{}};Yo.exports;var ig;function UC(){return ig||(ig=1,(function(r,e){var t=Object.create,n=Object.defineProperty,i=Object.defineProperties,s=Object.getOwnPropertyDescriptor,a=Object.getOwnPropertyDescriptors,c=Object.getOwnPropertyNames,u=Object.getOwnPropertySymbols,h=Object.getPrototypeOf,f=Object.prototype.hasOwnProperty,p=Object.prototype.propertyIsEnumerable,m=(o,l,d)=>l in o?n(o,l,{enumerable:!0,configurable:!0,writable:!0,value:d}):o[l]=d,g=(o,l)=>{for(var d in l||(l={}))f.call(l,d)&&m(o,d,l[d]);if(u)for(var d of u(l))p.call(l,d)&&m(o,d,l[d]);return o},x=(o,l)=>i(o,a(l)),M=(o,l)=>function(){return l||(0,o[c(o)[0]])((l={exports:{}}).exports,l),l.exports},v=(o,l)=>{for(var d in l)n(o,d,{get:l[d],enumerable:!0})},_=(o,l,d,y)=>{if(l&&typeof l=="object"||typeof l=="function")for(let T of c(l))!f.call(o,T)&&T!==d&&n(o,T,{get:()=>l[T],enumerable:!(y=s(l,T))||y.enumerable});return o},A=(o,l,d)=>(d=o!=null?t(h(o)):{},_(!o||!o.__esModule?n(d,"default",{value:o,enumerable:!0}):d,o)),P=o=>_(n({},"__esModule",{value:!0}),o),b=(o,l,d)=>(m(o,typeof l!="symbol"?l+"":l,d),d),B=M({"../node_modules/timing-function/lib/UnitBezier.js"(o,l){l.exports=(function(){function d(y,T,C,k){this.set(y,T,C,k)}return d.prototype.set=function(y,T,C,k){this._cx=3*y,this._bx=3*(C-y)-this._cx,this._ax=1-this._cx-this._bx,this._cy=3*T,this._by=3*(k-T)-this._cy,this._ay=1-this._cy-this._by},d.epsilon=1e-6,d.prototype._sampleCurveX=function(y){return((this._ax*y+this._bx)*y+this._cx)*y},d.prototype._sampleCurveY=function(y){return((this._ay*y+this._by)*y+this._cy)*y},d.prototype._sampleCurveDerivativeX=function(y){return(3*this._ax*y+2*this._bx)*y+this._cx},d.prototype._solveCurveX=function(y,T){var C,k,Y,K,oe,ve;for(Y=void 0,K=void 0,oe=void 0,ve=void 0,C=void 0,k=void 0,oe=y,k=0;k<8;){if(ve=this._sampleCurveX(oe)-y,Math.abs(ve)<T)return oe;if(C=this._sampleCurveDerivativeX(oe),Math.abs(C)<T)break;oe=oe-ve/C,k++}if(Y=0,K=1,oe=y,oe<Y)return Y;if(oe>K)return K;for(;Y<K;){if(ve=this._sampleCurveX(oe),Math.abs(ve-y)<T)return oe;y>ve?Y=oe:K=oe,oe=(K-Y)*.5+Y}return oe},d.prototype.solve=function(y,T){return this._sampleCurveY(this._solveCurveX(y,T))},d.prototype.solveSimple=function(y){return this._sampleCurveY(this._solveCurveX(y,1e-6))},d})()}}),U=M({"../node_modules/levenshtein-edit-distance/index.js"(o,l){var d,y;d=[],y=[];function T(C,k,Y){var K,oe,ve,xe,Ae,je,Be,ut;if(C===k)return 0;if(K=C.length,oe=k.length,K===0)return oe;if(oe===0)return K;for(Y&&(C=C.toLowerCase(),k=k.toLowerCase()),Be=0;Be<K;)y[Be]=C.charCodeAt(Be),d[Be]=++Be;for(ut=0;ut<oe;)for(ve=k.charCodeAt(ut),xe=Ae=ut++,Be=-1;++Be<K;)je=ve===y[Be]?Ae:Ae+1,Ae=d[Be],d[Be]=xe=Ae>xe?je>xe?xe+1:je:je>Ae?Ae+1:je;return xe}l.exports=T}}),O=M({"../node_modules/propose/propose.js"(o,l){var d=U();function y(){var T,C,k,Y,K,oe=0,ve=arguments[0],xe=arguments[1],Ae=xe.length,je=arguments[2];je&&(Y=je.threshold,K=je.ignoreCase),Y===void 0&&(Y=0);for(var Be=0;Be<Ae;++Be)K?C=d(ve,xe[Be],!0):C=d(ve,xe[Be]),C>ve.length?T=1-C/xe[Be].length:T=1-C/ve.length,T>oe&&(oe=T,k=xe[Be]);return oe>=Y?k:null}l.exports=y}}),z=M({"../node_modules/fast-deep-equal/index.js"(o,l){l.exports=function d(y,T){if(y===T)return!0;if(y&&T&&typeof y=="object"&&typeof T=="object"){if(y.constructor!==T.constructor)return!1;var C,k,Y;if(Array.isArray(y)){if(C=y.length,C!=T.length)return!1;for(k=C;k--!==0;)if(!d(y[k],T[k]))return!1;return!0}if(y.constructor===RegExp)return y.source===T.source&&y.flags===T.flags;if(y.valueOf!==Object.prototype.valueOf)return y.valueOf()===T.valueOf();if(y.toString!==Object.prototype.toString)return y.toString()===T.toString();if(Y=Object.keys(y),C=Y.length,C!==Object.keys(T).length)return!1;for(k=C;k--!==0;)if(!Object.prototype.hasOwnProperty.call(T,Y[k]))return!1;for(k=C;k--!==0;){var K=Y[k];if(!d(y[K],T[K]))return!1}return!0}return y!==y&&T!==T}}}),I={};v(I,{createRafDriver:()=>eu,getProject:()=>Tp,notify:()=>Ss,onChange:()=>Su,types:()=>tu,val:()=>Ep}),r.exports=P(I);var w={};v(w,{createRafDriver:()=>eu,getProject:()=>Tp,notify:()=>Ss,onChange:()=>Su,types:()=>tu,val:()=>Ep});var H=ln(),ee=class{constructor(){b(this,"atom",new H.Atom({projects:{}}))}add(o,l){this.atom.setByPointer(d=>d.projects[o],l)}get(o){return this.atom.get().projects[o]}has(o){return!!this.get(o)}},Q=new ee,ae=Q,ce=new WeakMap;function $(o){return ce.get(o)}function fe(o,l){ce.set(o,l)}var re=[],ye=Array.isArray,Me=ye,Ne=typeof Mi=="object"&&Mi&&Mi.Object===Object&&Mi,Ze=Ne,ht=typeof self=="object"&&self&&self.Object===Object&&self,le=Ze||ht||Function("return this")(),ge=le,Oe=ge.Symbol,Se=Oe,We=Object.prototype,tt=We.hasOwnProperty,st=We.toString,Tt=Se?Se.toStringTag:void 0;function ot(o){var l=tt.call(o,Tt),d=o[Tt];try{o[Tt]=void 0;var y=!0}catch{}var T=st.call(o);return y&&(l?o[Tt]=d:delete o[Tt]),T}var Ot=ot,X=Object.prototype,Qt=X.toString;function at(o){return Qt.call(o)}var dt=at,Ve="[object Null]",xt="[object Undefined]",Fe=Se?Se.toStringTag:void 0;function N(o){return o==null?o===void 0?xt:Ve:Fe&&Fe in Object(o)?Ot(o):dt(o)}var E=N;function Z(o){return o!=null&&typeof o=="object"}var ue=Z,pe="[object Symbol]";function de(o){return typeof o=="symbol"||ue(o)&&E(o)==pe}var De=de,Ee=/\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/,Re=/^\w*$/;function ct(o,l){if(Me(o))return!1;var d=typeof o;return d=="number"||d=="symbol"||d=="boolean"||o==null||De(o)?!0:Re.test(o)||!Ee.test(o)||l!=null&&o in Object(l)}var _e=ct;function Ce(o){var l=typeof o;return o!=null&&(l=="object"||l=="function")}var Ue=Ce,Ye="[object AsyncFunction]",Ie="[object Function]",pt="[object GeneratorFunction]",it="[object Proxy]";function V(o){if(!Ue(o))return!1;var l=E(o);return l==Ie||l==pt||l==Ye||l==it}var L=V,J=ge["__core-js_shared__"],W=J,ie=(function(){var o=/[^.]+$/.exec(W&&W.keys&&W.keys.IE_PROTO||"");return o?"Symbol(src)_1."+o:""})();function he(o){return!!ie&&ie in o}var me=he,Le=Function.prototype,Ke=Le.toString;function bt(o){if(o!=null){try{return Ke.call(o)}catch{}try{return o+""}catch{}}return""}var et=bt,Et=/[\\^$.*+?()[\]{}|]/g,$t=/^\[object .+?Constructor\]$/,Tn=Function.prototype,Kt=Object.prototype,Xe=Tn.toString,Ht=Kt.hasOwnProperty,Bn=RegExp("^"+Xe.call(Ht).replace(Et,"\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g,"$1.*?")+"$");function us(o){if(!Ue(o)||me(o))return!1;var l=L(o)?Bn:$t;return l.test(et(o))}var jn=us;function Mr(o,l){return o==null?void 0:o[l]}var Qi=Mr;function hs(o,l){var d=Qi(o,l);return jn(d)?d:void 0}var ni=hs,ho=ni(Object,"create"),Pi=ho;function er(){this.__data__=Pi?Pi(null):{},this.size=0}var R=er;function j(o){var l=this.has(o)&&delete this.__data__[o];return this.size-=l?1:0,l}var te=j,ne="__lodash_hash_undefined__",q=Object.prototype,be=q.hasOwnProperty;function Pe(o){var l=this.__data__;if(Pi){var d=l[o];return d===ne?void 0:d}return be.call(l,o)?l[o]:void 0}var ke=Pe,ze=Object.prototype,nt=ze.hasOwnProperty;function $e(o){var l=this.__data__;return Pi?l[o]!==void 0:nt.call(l,o)}var He=$e,yt="__lodash_hash_undefined__";function Rt(o,l){var d=this.__data__;return this.size+=this.has(o)?0:1,d[o]=Pi&&l===void 0?yt:l,this}var It=Rt;function Jt(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}Jt.prototype.clear=R,Jt.prototype.delete=te,Jt.prototype.get=ke,Jt.prototype.has=He,Jt.prototype.set=It;var St=Jt;function Ge(){this.__data__=[],this.size=0}var Xn=Ge;function _t(o,l){return o===l||o!==o&&l!==l}var yn=_t;function yi(o,l){for(var d=o.length;d--;)if(yn(o[d][0],l))return d;return-1}var rn=yi,Ri=Array.prototype,Lt=Ri.splice;function kn(o){var l=this.__data__,d=rn(l,o);if(d<0)return!1;var y=l.length-1;return d==y?l.pop():Lt.call(l,d,1),--this.size,!0}var Ci=kn;function En(o){var l=this.__data__,d=rn(l,o);return d<0?void 0:l[d][1]}var xn=En;function qn(o){return rn(this.__data__,o)>-1}var ds=qn;function fo(o,l){var d=this.__data__,y=rn(d,o);return y<0?(++this.size,d.push([o,l])):d[y][1]=l,this}var jc=fo;function tr(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}tr.prototype.clear=Xn,tr.prototype.delete=Ci,tr.prototype.get=xn,tr.prototype.has=ds,tr.prototype.set=jc;var fs=tr,Xc=ni(ge,"Map"),Tr=Xc;function qc(){this.size=0,this.__data__={hash:new St,map:new(Tr||fs),string:new St}}var Yc=qc;function Kc(o){var l=typeof o;return l=="string"||l=="number"||l=="symbol"||l=="boolean"?o!=="__proto__":o===null}var Zc=Kc;function $c(o,l){var d=o.__data__;return Zc(l)?d[typeof l=="string"?"string":"hash"]:d.map}var Er=$c;function oa(o){var l=Er(this,o).delete(o);return this.size-=l?1:0,l}var aa=oa;function Jc(o){return Er(this,o).get(o)}var Qc=Jc;function el(o){return Er(this,o).has(o)}var tl=el;function nl(o,l){var d=Er(this,o),y=d.size;return d.set(o,l),this.size+=d.size==y?0:1,this}var il=nl;function nr(o){var l=-1,d=o==null?0:o.length;for(this.clear();++l<d;){var y=o[l];this.set(y[0],y[1])}}nr.prototype.clear=Yc,nr.prototype.delete=aa,nr.prototype.get=Qc,nr.prototype.has=tl,nr.prototype.set=il;var ps=nr,rl="Expected a function";function po(o,l){if(typeof o!="function"||l!=null&&typeof l!="function")throw new TypeError(rl);var d=function(){var y=arguments,T=l?l.apply(this,y):y[0],C=d.cache;if(C.has(T))return C.get(T);var k=o.apply(this,y);return d.cache=C.set(T,k)||C,k};return d.cache=new(po.Cache||ps),d}po.Cache=ps;var sl=po,ol=500;function al(o){var l=sl(o,function(y){return d.size===ol&&d.clear(),y}),d=l.cache;return l}var cl=al,ll=/[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g,ul=/\\(\\)?/g,hl=cl(function(o){var l=[];return o.charCodeAt(0)===46&&l.push(""),o.replace(ll,function(d,y,T,C){l.push(T?C.replace(ul,"$1"):y||d)}),l}),dl=hl;function ca(o,l){for(var d=-1,y=o==null?0:o.length,T=Array(y);++d<y;)T[d]=l(o[d],d,o);return T}var fl=ca,la=Se?Se.prototype:void 0,ua=la?la.toString:void 0;function ha(o){if(typeof o=="string")return o;if(Me(o))return fl(o,ha)+"";if(De(o))return ua?ua.call(o):"";var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var da=ha;function pl(o){return o==null?"":da(o)}var ms=pl;function fa(o,l){return Me(o)?o:_e(o,l)?[o]:dl(ms(o))}var Ar=fa;function ml(o){if(typeof o=="string"||De(o))return o;var l=o+"";return l=="0"&&1/o==-1/0?"-0":l}var li=ml;function wr(o,l){l=Ar(l,o);for(var d=0,y=l.length;o!=null&&d<y;)o=o[li(l[d++])];return d&&d==y?o:void 0}var gs=wr;function mo(o,l,d){var y=o==null?void 0:gs(o,l);return y===void 0?d:y}var Ii=mo;function pa(o,l){return l.length===0?o:Ii(o,l)}var ir=class{constructor(){b(this,"_values",{})}get(o,l){if(this.has(o))return this._values[o];{const d=l();return this._values[o]=d,d}}has(o){return this._values.hasOwnProperty(o)}},an=ln(),_s=(function(){try{var o=ni(Object,"defineProperty");return o({},"",{}),o}catch{}})(),go=_s;function gl(o,l,d){l=="__proto__"&&go?go(o,l,{configurable:!0,enumerable:!0,value:d,writable:!0}):o[l]=d}var Li=gl,Pr=Object.prototype,_l=Pr.hasOwnProperty;function vl(o,l,d){var y=o[l];(!(_l.call(o,l)&&yn(y,d))||d===void 0&&!(l in o))&&Li(o,l,d)}var _o=vl,yl=9007199254740991,ma=/^(?:0|[1-9]\d*)$/;function xl(o,l){var d=typeof o;return l=l??yl,!!l&&(d=="number"||d!="symbol"&&ma.test(o))&&o>-1&&o%1==0&&o<l}var vo=xl;function bl(o,l,d,y){if(!Ue(o))return o;l=Ar(l,o);for(var T=-1,C=l.length,k=C-1,Y=o;Y!=null&&++T<C;){var K=li(l[T]),oe=d;if(K==="__proto__"||K==="constructor"||K==="prototype")return o;if(T!=k){var ve=Y[K];oe=y?y(ve,K,Y):void 0,oe===void 0&&(oe=Ue(ve)?ve:vo(l[T+1])?[]:{})}_o(Y,K,oe),Y=Y[K]}return o}var ga=bl;function _a(o,l,d){return o==null?o:ga(o,l,d)}var vs=_a,pn=new WeakMap;function Sl(o){return yo(o)}function yo(o){if(pn.has(o))return pn.get(o);const l=o.type==="compound"?ya(o):o.type==="enum"?va(o):o.default;return pn.set(o,l),l}function va(o){const l={$case:o.defaultCase};for(const[d,y]of Object.entries(o.cases))l[d]=yo(y);return l}function ya(o){const l={};for(const[d,y]of Object.entries(o.props))l[d]=yo(y);return l}var Ln=ln(),Ml=A(B());function Tl(o,l,d){return(0,Ln.prism)(()=>{const y=(0,Ln.val)(l);return Ln.prism.memo("driver",()=>y?y.type==="BasicKeyframedTrack"?El(o,y,d):(o.logger.error("Track type not yet supported."),(0,Ln.prism)(()=>{})):(0,Ln.prism)(()=>{}),[y]).getValue()})}function El(o,l,d){return(0,Ln.prism)(()=>{let y=Ln.prism.ref("state",{started:!1}),T=y.current;const C=d.getValue();return(!T.started||C<T.validFrom||T.validTo<=C)&&(y.current=T=Al(o,d,l)),T.der.getValue()})}var xa=(0,Ln.prism)(()=>{});function Al(o,l,d){const y=l.getValue();if(d.keyframes.length===0)return{started:!0,validFrom:-1/0,validTo:1/0,der:xa};let T=0;for(;;){const C=d.keyframes[T];if(!C)return cn.error;const k=T===d.keyframes.length-1;if(y<C.position)return T===0?cn.beforeFirstKeyframe(C):cn.error;if(C.position===y)return k?cn.lastKeyframe(C):cn.between(C,d.keyframes[T+1],l);if(T===d.keyframes.length-1)return cn.lastKeyframe(C);{const Y=T+1;if(d.keyframes[Y].position<=y){T=Y;continue}else return cn.between(C,d.keyframes[T+1],l)}}}var cn={beforeFirstKeyframe(o){return{started:!0,validFrom:-1/0,validTo:o.position,der:(0,Ln.prism)(()=>({left:o.value,progression:0}))}},lastKeyframe(o){return{started:!0,validFrom:o.position,validTo:1/0,der:(0,Ln.prism)(()=>({left:o.value,progression:0}))}},between(o,l,d){if(!o.connectedRight)return{started:!0,validFrom:o.position,validTo:l.position,der:(0,Ln.prism)(()=>({left:o.value,progression:0}))};const y=C=>(C-o.position)/(l.position-o.position);if(!o.type||o.type==="bezier"){const C=new Ml.default(o.handles[2],o.handles[3],l.handles[0],l.handles[1]),k=(0,Ln.prism)(()=>{const Y=y(d.getValue()),K=C.solveSimple(Y);return{left:o.value,right:l.value,progression:K}});return{started:!0,validFrom:o.position,validTo:l.position,der:k}}const T=(0,Ln.prism)(()=>{const C=y(d.getValue()),k=Math.floor(C);return{left:o.value,right:l.value,progression:k}});return{started:!0,validFrom:o.position,validTo:l.position,der:T}},error:{started:!0,validFrom:-1/0,validTo:1/0,der:xa}};function Rr(o,l,d){const T=d.get(o);if(T&&T.override===l)return T.merged;const C=g({},o);for(const k of Object.keys(l)){const Y=l[k],K=o[k];C[k]=typeof Y=="object"&&typeof K=="object"?Rr(K,Y,d):Y===void 0?K:Y}return d.set(o,{override:l,merged:C}),C}function Cr(o,l){let d=o;for(const y of l)d=d[y];return d}var Ir=ln(),ba=(o,l)=>{const d=Ir.prism.memo(o,()=>new Ir.Atom(l),[]);return d.set(l),d},Dt=ln(),xo=ln(),wl=/\s/;function Sa(o){for(var l=o.length;l--&&wl.test(o.charAt(l)););return l}var Ma=Sa,Ta=/^\s+/;function Pl(o){return o&&o.slice(0,Ma(o)+1).replace(Ta,"")}var ys=Pl,bo=NaN,Rl=/^[-+]0x[0-9a-f]+$/i,Cl=/^0b[01]+$/i,Ea=/^0o[0-7]+$/i,Il=parseInt;function Ll(o){if(typeof o=="number")return o;if(De(o))return bo;if(Ue(o)){var l=typeof o.valueOf=="function"?o.valueOf():o;o=Ue(l)?l+"":l}if(typeof o!="string")return o===0?o:+o;o=ys(o);var d=Cl.test(o);return d||Ea.test(o)?Il(o.slice(2),d?2:8):Rl.test(o)?bo:+o}var S=Ll,D=1/0,G=17976931348623157e292;function se(o){if(!o)return o===0?o:0;if(o=S(o),o===D||o===-D){var l=o<0?-1:1;return l*G}return o===o?o:0}var Je=se;function At(o){var l=Je(o),d=l%1;return l===l?d?l-d:l:0}var bn=At;function ii(o){return o}var Aa=ii,rr=ni(ge,"WeakMap"),Lr=rr,Nd=Object.create,a_=(function(){function o(){}return function(l){if(!Ue(l))return{};if(Nd)return Nd(l);o.prototype=l;var d=new o;return o.prototype=void 0,d}})(),c_=a_;function l_(o,l){var d=-1,y=o.length;for(l||(l=Array(y));++d<y;)l[d]=o[d];return l}var u_=l_;function h_(o,l){for(var d=-1,y=o==null?0:o.length;++d<y&&l(o[d],d,o)!==!1;);return o}var d_=h_;function f_(o,l,d,y){var T=!d;d||(d={});for(var C=-1,k=l.length;++C<k;){var Y=l[C],K=y?y(d[Y],o[Y],Y,d,o):void 0;K===void 0&&(K=o[Y]),T?Li(d,Y,K):_o(d,Y,K)}return d}var wa=f_,p_=9007199254740991;function m_(o){return typeof o=="number"&&o>-1&&o%1==0&&o<=p_}var Dl=m_;function g_(o){return o!=null&&Dl(o.length)&&!L(o)}var Od=g_,__=Object.prototype;function v_(o){var l=o&&o.constructor,d=typeof l=="function"&&l.prototype||__;return o===d}var Nl=v_;function y_(o,l){for(var d=-1,y=Array(o);++d<o;)y[d]=l(d);return y}var x_=y_,b_="[object Arguments]";function S_(o){return ue(o)&&E(o)==b_}var Ud=S_,Fd=Object.prototype,M_=Fd.hasOwnProperty,T_=Fd.propertyIsEnumerable,E_=Ud((function(){return arguments})())?Ud:function(o){return ue(o)&&M_.call(o,"callee")&&!T_.call(o,"callee")},Bd=E_;function A_(){return!1}var w_=A_,kd=e&&!e.nodeType&&e,zd=kd&&!0&&r&&!r.nodeType&&r,P_=zd&&zd.exports===kd,Hd=P_?ge.Buffer:void 0,R_=Hd?Hd.isBuffer:void 0,C_=R_||w_,Pa=C_,I_="[object Arguments]",L_="[object Array]",D_="[object Boolean]",N_="[object Date]",O_="[object Error]",U_="[object Function]",F_="[object Map]",B_="[object Number]",k_="[object Object]",z_="[object RegExp]",H_="[object Set]",V_="[object String]",G_="[object WeakMap]",W_="[object ArrayBuffer]",j_="[object DataView]",X_="[object Float32Array]",q_="[object Float64Array]",Y_="[object Int8Array]",K_="[object Int16Array]",Z_="[object Int32Array]",$_="[object Uint8Array]",J_="[object Uint8ClampedArray]",Q_="[object Uint16Array]",ev="[object Uint32Array]",qt={};qt[X_]=qt[q_]=qt[Y_]=qt[K_]=qt[Z_]=qt[$_]=qt[J_]=qt[Q_]=qt[ev]=!0,qt[I_]=qt[L_]=qt[W_]=qt[D_]=qt[j_]=qt[N_]=qt[O_]=qt[U_]=qt[F_]=qt[B_]=qt[k_]=qt[z_]=qt[H_]=qt[V_]=qt[G_]=!1;function tv(o){return ue(o)&&Dl(o.length)&&!!qt[E(o)]}var nv=tv;function iv(o){return function(l){return o(l)}}var Ol=iv,Vd=e&&!e.nodeType&&e,So=Vd&&!0&&r&&!r.nodeType&&r,rv=So&&So.exports===Vd,Ul=rv&&Ze.process,sv=(function(){try{var o=So&&So.require&&So.require("util").types;return o||Ul&&Ul.binding&&Ul.binding("util")}catch{}})(),xs=sv,Gd=xs&&xs.isTypedArray,ov=Gd?Ol(Gd):nv,Wd=ov,av=Object.prototype,cv=av.hasOwnProperty;function lv(o,l){var d=Me(o),y=!d&&Bd(o),T=!d&&!y&&Pa(o),C=!d&&!y&&!T&&Wd(o),k=d||y||T||C,Y=k?x_(o.length,String):[],K=Y.length;for(var oe in o)(l||cv.call(o,oe))&&!(k&&(oe=="length"||T&&(oe=="offset"||oe=="parent")||C&&(oe=="buffer"||oe=="byteLength"||oe=="byteOffset")||vo(oe,K)))&&Y.push(oe);return Y}var jd=lv;function uv(o,l){return function(d){return o(l(d))}}var Xd=uv,hv=Xd(Object.keys,Object),dv=hv,fv=Object.prototype,pv=fv.hasOwnProperty;function mv(o){if(!Nl(o))return dv(o);var l=[];for(var d in Object(o))pv.call(o,d)&&d!="constructor"&&l.push(d);return l}var gv=mv;function _v(o){return Od(o)?jd(o):gv(o)}var Mo=_v;function vv(o){var l=[];if(o!=null)for(var d in Object(o))l.push(d);return l}var yv=vv,xv=Object.prototype,bv=xv.hasOwnProperty;function Sv(o){if(!Ue(o))return yv(o);var l=Nl(o),d=[];for(var y in o)y=="constructor"&&(l||!bv.call(o,y))||d.push(y);return d}var Mv=Sv;function Tv(o){return Od(o)?jd(o,!0):Mv(o)}var Fl=Tv;function Ev(o,l){for(var d=-1,y=l.length,T=o.length;++d<y;)o[T+d]=l[d];return o}var qd=Ev,Av=Xd(Object.getPrototypeOf,Object),Bl=Av,wv="[object Object]",Pv=Function.prototype,Rv=Object.prototype,Yd=Pv.toString,Cv=Rv.hasOwnProperty,Iv=Yd.call(Object);function Lv(o){if(!ue(o)||E(o)!=wv)return!1;var l=Bl(o);if(l===null)return!0;var d=Cv.call(l,"constructor")&&l.constructor;return typeof d=="function"&&d instanceof d&&Yd.call(d)==Iv}var Dv=Lv;function Nv(o,l,d){var y=-1,T=o.length;l<0&&(l=-l>T?0:T+l),d=d>T?T:d,d<0&&(d+=T),T=l>d?0:d-l>>>0,l>>>=0;for(var C=Array(T);++y<T;)C[y]=o[y+l];return C}var Kd=Nv;function Ov(o,l,d){var y=o.length;return d=d===void 0?y:d,!l&&d>=y?o:Kd(o,l,d)}var Uv=Ov,Fv="\\ud800-\\udfff",Bv="\\u0300-\\u036f",kv="\\ufe20-\\ufe2f",zv="\\u20d0-\\u20ff",Hv=Bv+kv+zv,Vv="\\ufe0e\\ufe0f",Gv="\\u200d",Wv=RegExp("["+Gv+Fv+Hv+Vv+"]");function jv(o){return Wv.test(o)}var kl=jv;function Xv(o){return o.split("")}var qv=Xv,Zd="\\ud800-\\udfff",Yv="\\u0300-\\u036f",Kv="\\ufe20-\\ufe2f",Zv="\\u20d0-\\u20ff",$v=Yv+Kv+Zv,Jv="\\ufe0e\\ufe0f",Qv="["+Zd+"]",zl="["+$v+"]",Hl="\\ud83c[\\udffb-\\udfff]",e0="(?:"+zl+"|"+Hl+")",$d="[^"+Zd+"]",Jd="(?:\\ud83c[\\udde6-\\uddff]){2}",Qd="[\\ud800-\\udbff][\\udc00-\\udfff]",t0="\\u200d",ef=e0+"?",tf="["+Jv+"]?",n0="(?:"+t0+"(?:"+[$d,Jd,Qd].join("|")+")"+tf+ef+")*",i0=tf+ef+n0,r0="(?:"+[$d+zl+"?",zl,Jd,Qd,Qv].join("|")+")",s0=RegExp(Hl+"(?="+Hl+")|"+r0+i0,"g");function o0(o){return o.match(s0)||[]}var a0=o0;function c0(o){return kl(o)?a0(o):qv(o)}var l0=c0;function u0(o,l,d){return o===o&&(d!==void 0&&(o=o<=d?o:d),l!==void 0&&(o=o>=l?o:l)),o}var h0=u0;function d0(o,l,d){return d===void 0&&(d=l,l=void 0),d!==void 0&&(d=S(d),d=d===d?d:0),l!==void 0&&(l=S(l),l=l===l?l:0),h0(S(o),l,d)}var nf=d0;function f0(){this.__data__=new fs,this.size=0}var p0=f0;function m0(o){var l=this.__data__,d=l.delete(o);return this.size=l.size,d}var g0=m0;function _0(o){return this.__data__.get(o)}var v0=_0;function y0(o){return this.__data__.has(o)}var x0=y0,b0=200;function S0(o,l){var d=this.__data__;if(d instanceof fs){var y=d.__data__;if(!Tr||y.length<b0-1)return y.push([o,l]),this.size=++d.size,this;d=this.__data__=new ps(y)}return d.set(o,l),this.size=d.size,this}var M0=S0;function bs(o){var l=this.__data__=new fs(o);this.size=l.size}bs.prototype.clear=p0,bs.prototype.delete=g0,bs.prototype.get=v0,bs.prototype.has=x0,bs.prototype.set=M0;var To=bs;function T0(o,l){return o&&wa(l,Mo(l),o)}var E0=T0;function A0(o,l){return o&&wa(l,Fl(l),o)}var w0=A0,rf=e&&!e.nodeType&&e,sf=rf&&!0&&r&&!r.nodeType&&r,P0=sf&&sf.exports===rf,of=P0?ge.Buffer:void 0,af=of?of.allocUnsafe:void 0;function R0(o,l){if(l)return o.slice();var d=o.length,y=af?af(d):new o.constructor(d);return o.copy(y),y}var C0=R0;function I0(o,l){for(var d=-1,y=o==null?0:o.length,T=0,C=[];++d<y;){var k=o[d];l(k,d,o)&&(C[T++]=k)}return C}var L0=I0;function D0(){return[]}var cf=D0,N0=Object.prototype,O0=N0.propertyIsEnumerable,lf=Object.getOwnPropertySymbols,U0=lf?function(o){return o==null?[]:(o=Object(o),L0(lf(o),function(l){return O0.call(o,l)}))}:cf,Vl=U0;function F0(o,l){return wa(o,Vl(o),l)}var B0=F0,k0=Object.getOwnPropertySymbols,z0=k0?function(o){for(var l=[];o;)qd(l,Vl(o)),o=Bl(o);return l}:cf,uf=z0;function H0(o,l){return wa(o,uf(o),l)}var V0=H0;function G0(o,l,d){var y=l(o);return Me(o)?y:qd(y,d(o))}var hf=G0;function W0(o){return hf(o,Mo,Vl)}var Gl=W0;function j0(o){return hf(o,Fl,uf)}var X0=j0,q0=ni(ge,"DataView"),Wl=q0,Y0=ni(ge,"Promise"),jl=Y0,K0=ni(ge,"Set"),Xl=K0,df="[object Map]",Z0="[object Object]",ff="[object Promise]",pf="[object Set]",mf="[object WeakMap]",gf="[object DataView]",$0=et(Wl),J0=et(Tr),Q0=et(jl),ey=et(Xl),ty=et(Lr),Dr=E;(Wl&&Dr(new Wl(new ArrayBuffer(1)))!=gf||Tr&&Dr(new Tr)!=df||jl&&Dr(jl.resolve())!=ff||Xl&&Dr(new Xl)!=pf||Lr&&Dr(new Lr)!=mf)&&(Dr=function(o){var l=E(o),d=l==Z0?o.constructor:void 0,y=d?et(d):"";if(y)switch(y){case $0:return gf;case J0:return df;case Q0:return ff;case ey:return pf;case ty:return mf}return l});var Eo=Dr,ny=Object.prototype,iy=ny.hasOwnProperty;function ry(o){var l=o.length,d=new o.constructor(l);return l&&typeof o[0]=="string"&&iy.call(o,"index")&&(d.index=o.index,d.input=o.input),d}var sy=ry,oy=ge.Uint8Array,Ra=oy;function ay(o){var l=new o.constructor(o.byteLength);return new Ra(l).set(new Ra(o)),l}var ql=ay;function cy(o,l){var d=l?ql(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.byteLength)}var ly=cy,uy=/\w*$/;function hy(o){var l=new o.constructor(o.source,uy.exec(o));return l.lastIndex=o.lastIndex,l}var dy=hy,_f=Se?Se.prototype:void 0,vf=_f?_f.valueOf:void 0;function fy(o){return vf?Object(vf.call(o)):{}}var py=fy;function my(o,l){var d=l?ql(o.buffer):o.buffer;return new o.constructor(d,o.byteOffset,o.length)}var gy=my,_y="[object Boolean]",vy="[object Date]",yy="[object Map]",xy="[object Number]",by="[object RegExp]",Sy="[object Set]",My="[object String]",Ty="[object Symbol]",Ey="[object ArrayBuffer]",Ay="[object DataView]",wy="[object Float32Array]",Py="[object Float64Array]",Ry="[object Int8Array]",Cy="[object Int16Array]",Iy="[object Int32Array]",Ly="[object Uint8Array]",Dy="[object Uint8ClampedArray]",Ny="[object Uint16Array]",Oy="[object Uint32Array]";function Uy(o,l,d){var y=o.constructor;switch(l){case Ey:return ql(o);case _y:case vy:return new y(+o);case Ay:return ly(o,d);case wy:case Py:case Ry:case Cy:case Iy:case Ly:case Dy:case Ny:case Oy:return gy(o,d);case yy:return new y;case xy:case My:return new y(o);case by:return dy(o);case Sy:return new y;case Ty:return py(o)}}var Fy=Uy;function By(o){return typeof o.constructor=="function"&&!Nl(o)?c_(Bl(o)):{}}var ky=By,zy="[object Map]";function Hy(o){return ue(o)&&Eo(o)==zy}var Vy=Hy,yf=xs&&xs.isMap,Gy=yf?Ol(yf):Vy,Wy=Gy,jy="[object Set]";function Xy(o){return ue(o)&&Eo(o)==jy}var qy=Xy,xf=xs&&xs.isSet,Yy=xf?Ol(xf):qy,Ky=Yy,Zy=1,$y=2,Jy=4,bf="[object Arguments]",Qy="[object Array]",ex="[object Boolean]",tx="[object Date]",nx="[object Error]",Sf="[object Function]",ix="[object GeneratorFunction]",rx="[object Map]",sx="[object Number]",Mf="[object Object]",ox="[object RegExp]",ax="[object Set]",cx="[object String]",lx="[object Symbol]",ux="[object WeakMap]",hx="[object ArrayBuffer]",dx="[object DataView]",fx="[object Float32Array]",px="[object Float64Array]",mx="[object Int8Array]",gx="[object Int16Array]",_x="[object Int32Array]",vx="[object Uint8Array]",yx="[object Uint8ClampedArray]",xx="[object Uint16Array]",bx="[object Uint32Array]",Vt={};Vt[bf]=Vt[Qy]=Vt[hx]=Vt[dx]=Vt[ex]=Vt[tx]=Vt[fx]=Vt[px]=Vt[mx]=Vt[gx]=Vt[_x]=Vt[rx]=Vt[sx]=Vt[Mf]=Vt[ox]=Vt[ax]=Vt[cx]=Vt[lx]=Vt[vx]=Vt[yx]=Vt[xx]=Vt[bx]=!0,Vt[nx]=Vt[Sf]=Vt[ux]=!1;function Ca(o,l,d,y,T,C){var k,Y=l&Zy,K=l&$y,oe=l&Jy;if(d&&(k=T?d(o,y,T,C):d(o)),k!==void 0)return k;if(!Ue(o))return o;var ve=Me(o);if(ve){if(k=sy(o),!Y)return u_(o,k)}else{var xe=Eo(o),Ae=xe==Sf||xe==ix;if(Pa(o))return C0(o,Y);if(xe==Mf||xe==bf||Ae&&!T){if(k=K||Ae?{}:ky(o),!Y)return K?V0(o,w0(k,o)):B0(o,E0(k,o))}else{if(!Vt[xe])return T?o:{};k=Fy(o,xe,Y)}}C||(C=new To);var je=C.get(o);if(je)return je;C.set(o,k),Ky(o)?o.forEach(function(gt){k.add(Ca(gt,l,d,gt,o,C))}):Wy(o)&&o.forEach(function(gt,lt){k.set(lt,Ca(gt,l,d,lt,o,C))});var Be=oe?K?X0:Gl:K?Fl:Mo,ut=ve?void 0:Be(o);return d_(ut||o,function(gt,lt){ut&&(lt=gt,gt=o[lt]),_o(k,lt,Ca(gt,l,d,lt,o,C))}),k}var Sx=Ca,Mx=1,Tx=4;function Ex(o){return Sx(o,Mx|Tx)}var Ax=Ex,wx="__lodash_hash_undefined__";function Px(o){return this.__data__.set(o,wx),this}var Rx=Px;function Cx(o){return this.__data__.has(o)}var Ix=Cx;function Ia(o){var l=-1,d=o==null?0:o.length;for(this.__data__=new ps;++l<d;)this.add(o[l])}Ia.prototype.add=Ia.prototype.push=Rx,Ia.prototype.has=Ix;var Lx=Ia;function Dx(o,l){for(var d=-1,y=o==null?0:o.length;++d<y;)if(l(o[d],d,o))return!0;return!1}var Nx=Dx;function Ox(o,l){return o.has(l)}var Ux=Ox,Fx=1,Bx=2;function kx(o,l,d,y,T,C){var k=d&Fx,Y=o.length,K=l.length;if(Y!=K&&!(k&&K>Y))return!1;var oe=C.get(o),ve=C.get(l);if(oe&&ve)return oe==l&&ve==o;var xe=-1,Ae=!0,je=d&Bx?new Lx:void 0;for(C.set(o,l),C.set(l,o);++xe<Y;){var Be=o[xe],ut=l[xe];if(y)var gt=k?y(ut,Be,xe,l,o,C):y(Be,ut,xe,o,l,C);if(gt!==void 0){if(gt)continue;Ae=!1;break}if(je){if(!Nx(l,function(lt,wt){if(!Ux(je,wt)&&(Be===lt||T(Be,lt,d,y,C)))return je.push(wt)})){Ae=!1;break}}else if(!(Be===ut||T(Be,ut,d,y,C))){Ae=!1;break}}return C.delete(o),C.delete(l),Ae}var Tf=kx;function zx(o){var l=-1,d=Array(o.size);return o.forEach(function(y,T){d[++l]=[T,y]}),d}var Hx=zx;function Vx(o){var l=-1,d=Array(o.size);return o.forEach(function(y){d[++l]=y}),d}var Gx=Vx,Wx=1,jx=2,Xx="[object Boolean]",qx="[object Date]",Yx="[object Error]",Kx="[object Map]",Zx="[object Number]",$x="[object RegExp]",Jx="[object Set]",Qx="[object String]",eb="[object Symbol]",tb="[object ArrayBuffer]",nb="[object DataView]",Ef=Se?Se.prototype:void 0,Yl=Ef?Ef.valueOf:void 0;function ib(o,l,d,y,T,C,k){switch(d){case nb:if(o.byteLength!=l.byteLength||o.byteOffset!=l.byteOffset)return!1;o=o.buffer,l=l.buffer;case tb:return!(o.byteLength!=l.byteLength||!C(new Ra(o),new Ra(l)));case Xx:case qx:case Zx:return yn(+o,+l);case Yx:return o.name==l.name&&o.message==l.message;case $x:case Qx:return o==l+"";case Kx:var Y=Hx;case Jx:var K=y&Wx;if(Y||(Y=Gx),o.size!=l.size&&!K)return!1;var oe=k.get(o);if(oe)return oe==l;y|=jx,k.set(o,l);var ve=Tf(Y(o),Y(l),y,T,C,k);return k.delete(o),ve;case eb:if(Yl)return Yl.call(o)==Yl.call(l)}return!1}var rb=ib,sb=1,ob=Object.prototype,ab=ob.hasOwnProperty;function cb(o,l,d,y,T,C){var k=d&sb,Y=Gl(o),K=Y.length,oe=Gl(l),ve=oe.length;if(K!=ve&&!k)return!1;for(var xe=K;xe--;){var Ae=Y[xe];if(!(k?Ae in l:ab.call(l,Ae)))return!1}var je=C.get(o),Be=C.get(l);if(je&&Be)return je==l&&Be==o;var ut=!0;C.set(o,l),C.set(l,o);for(var gt=k;++xe<K;){Ae=Y[xe];var lt=o[Ae],wt=l[Ae];if(y)var An=k?y(wt,lt,Ae,l,o,C):y(lt,wt,Ae,o,l,C);if(!(An===void 0?lt===wt||T(lt,wt,d,y,C):An)){ut=!1;break}gt||(gt=Ae=="constructor")}if(ut&&!gt){var Hn=o.constructor,wn=l.constructor;Hn!=wn&&"constructor"in o&&"constructor"in l&&!(typeof Hn=="function"&&Hn instanceof Hn&&typeof wn=="function"&&wn instanceof wn)&&(ut=!1)}return C.delete(o),C.delete(l),ut}var lb=cb,ub=1,Af="[object Arguments]",wf="[object Array]",La="[object Object]",hb=Object.prototype,Pf=hb.hasOwnProperty;function db(o,l,d,y,T,C){var k=Me(o),Y=Me(l),K=k?wf:Eo(o),oe=Y?wf:Eo(l);K=K==Af?La:K,oe=oe==Af?La:oe;var ve=K==La,xe=oe==La,Ae=K==oe;if(Ae&&Pa(o)){if(!Pa(l))return!1;k=!0,ve=!1}if(Ae&&!ve)return C||(C=new To),k||Wd(o)?Tf(o,l,d,y,T,C):rb(o,l,K,d,y,T,C);if(!(d&ub)){var je=ve&&Pf.call(o,"__wrapped__"),Be=xe&&Pf.call(l,"__wrapped__");if(je||Be){var ut=je?o.value():o,gt=Be?l.value():l;return C||(C=new To),T(ut,gt,d,y,C)}}return Ae?(C||(C=new To),lb(o,l,d,y,T,C)):!1}var fb=db;function Rf(o,l,d,y,T){return o===l?!0:o==null||l==null||!ue(o)&&!ue(l)?o!==o&&l!==l:fb(o,l,d,y,Rf,T)}var Cf=Rf,pb=1,mb=2;function gb(o,l,d,y){var T=d.length,C=T,k=!y;if(o==null)return!C;for(o=Object(o);T--;){var Y=d[T];if(k&&Y[2]?Y[1]!==o[Y[0]]:!(Y[0]in o))return!1}for(;++T<C;){Y=d[T];var K=Y[0],oe=o[K],ve=Y[1];if(k&&Y[2]){if(oe===void 0&&!(K in o))return!1}else{var xe=new To;if(y)var Ae=y(oe,ve,K,o,l,xe);if(!(Ae===void 0?Cf(ve,oe,pb|mb,y,xe):Ae))return!1}}return!0}var _b=gb;function vb(o){return o===o&&!Ue(o)}var If=vb;function yb(o){for(var l=Mo(o),d=l.length;d--;){var y=l[d],T=o[y];l[d]=[y,T,If(T)]}return l}var xb=yb;function bb(o,l){return function(d){return d==null?!1:d[o]===l&&(l!==void 0||o in Object(d))}}var Lf=bb;function Sb(o){var l=xb(o);return l.length==1&&l[0][2]?Lf(l[0][0],l[0][1]):function(d){return d===o||_b(d,o,l)}}var Mb=Sb;function Tb(o,l){return o!=null&&l in Object(o)}var Eb=Tb;function Ab(o,l,d){l=Ar(l,o);for(var y=-1,T=l.length,C=!1;++y<T;){var k=li(l[y]);if(!(C=o!=null&&d(o,k)))break;o=o[k]}return C||++y!=T?C:(T=o==null?0:o.length,!!T&&Dl(T)&&vo(k,T)&&(Me(o)||Bd(o)))}var wb=Ab;function Pb(o,l){return o!=null&&wb(o,l,Eb)}var Rb=Pb,Cb=1,Ib=2;function Lb(o,l){return _e(o)&&If(l)?Lf(li(o),l):function(d){var y=Ii(d,o);return y===void 0&&y===l?Rb(d,o):Cf(l,y,Cb|Ib)}}var Db=Lb;function Nb(o){return function(l){return l==null?void 0:l[o]}}var Df=Nb;function Ob(o){return function(l){return gs(l,o)}}var Ub=Ob;function Fb(o){return _e(o)?Df(li(o)):Ub(o)}var Bb=Fb;function kb(o){return typeof o=="function"?o:o==null?Aa:typeof o=="object"?Me(o)?Db(o[0],o[1]):Mb(o):Bb(o)}var zb=kb;function Hb(o){return function(l,d,y){for(var T=-1,C=Object(l),k=y(l),Y=k.length;Y--;){var K=k[o?Y:++T];if(d(C[K],K,C)===!1)break}return l}}var Vb=Hb,Gb=Vb(),Wb=Gb;function jb(o,l){return o&&Wb(o,l,Mo)}var Xb=jb,qb=function(){return ge.Date.now()},Kl=qb,Yb="Expected a function",Kb=Math.max,Zb=Math.min;function $b(o,l,d){var y,T,C,k,Y,K,oe=0,ve=!1,xe=!1,Ae=!0;if(typeof o!="function")throw new TypeError(Yb);l=S(l)||0,Ue(d)&&(ve=!!d.leading,xe="maxWait"in d,C=xe?Kb(S(d.maxWait)||0,l):C,Ae="trailing"in d?!!d.trailing:Ae);function je(Bt){var Pn=y,$n=T;return y=T=void 0,oe=Bt,k=o.apply($n,Pn),k}function Be(Bt){return oe=Bt,Y=setTimeout(lt,l),ve?je(Bt):k}function ut(Bt){var Pn=Bt-K,$n=Bt-oe,xi=l-Pn;return xe?Zb(xi,C-$n):xi}function gt(Bt){var Pn=Bt-K,$n=Bt-oe;return K===void 0||Pn>=l||Pn<0||xe&&$n>=C}function lt(){var Bt=Kl();if(gt(Bt))return wt(Bt);Y=setTimeout(lt,ut(Bt))}function wt(Bt){return Y=void 0,Ae&&y?je(Bt):(y=T=void 0,k)}function An(){Y!==void 0&&clearTimeout(Y),oe=0,y=K=T=Y=void 0}function Hn(){return Y===void 0?k:wt(Kl())}function wn(){var Bt=Kl(),Pn=gt(Bt);if(y=arguments,T=this,K=Bt,Pn){if(Y===void 0)return Be(K);if(xe)return clearTimeout(Y),Y=setTimeout(lt,l),je(K)}return Y===void 0&&(Y=setTimeout(lt,l)),k}return wn.cancel=An,wn.flush=Hn,wn}var Jb=$b;function Qb(o){var l=o==null?0:o.length;return l?o[l-1]:void 0}var eS=Qb;function tS(o,l){return l.length<2?o:gs(o,Kd(l,0,-1))}var nS=tS;function iS(o){return typeof o=="number"&&o==bn(o)}var rS=iS;function sS(o,l){var d={};return l=zb(l),Xb(o,function(y,T,C){Li(d,T,l(y,T,C))}),d}var oS=sS;function aS(o,l){return l=Ar(l,o),o=nS(o,l),o==null||delete o[li(eS(l))]}var cS=aS,lS=9007199254740991,uS=Math.floor;function hS(o,l){var d="";if(!o||l<1||l>lS)return d;do l%2&&(d+=o),l=uS(l/2),l&&(o+=o);while(l);return d}var Nf=hS,dS=Df("length"),fS=dS,Of="\\ud800-\\udfff",pS="\\u0300-\\u036f",mS="\\ufe20-\\ufe2f",gS="\\u20d0-\\u20ff",_S=pS+mS+gS,vS="\\ufe0e\\ufe0f",yS="["+Of+"]",Zl="["+_S+"]",$l="\\ud83c[\\udffb-\\udfff]",xS="(?:"+Zl+"|"+$l+")",Uf="[^"+Of+"]",Ff="(?:\\ud83c[\\udde6-\\uddff]){2}",Bf="[\\ud800-\\udbff][\\udc00-\\udfff]",bS="\\u200d",kf=xS+"?",zf="["+vS+"]?",SS="(?:"+bS+"(?:"+[Uf,Ff,Bf].join("|")+")"+zf+kf+")*",MS=zf+kf+SS,TS="(?:"+[Uf+Zl+"?",Zl,Ff,Bf,yS].join("|")+")",Hf=RegExp($l+"(?="+$l+")|"+TS+MS,"g");function ES(o){for(var l=Hf.lastIndex=0;Hf.test(o);)++l;return l}var AS=ES;function wS(o){return kl(o)?AS(o):fS(o)}var Vf=wS,PS=Math.ceil;function RS(o,l){l=l===void 0?" ":da(l);var d=l.length;if(d<2)return d?Nf(l,o):l;var y=Nf(l,PS(o/Vf(l)));return kl(l)?Uv(l0(y),0,o).join(""):y.slice(0,o)}var CS=RS;function IS(o,l,d){o=ms(o),l=bn(l);var y=l?Vf(o):0;return l&&y<l?CS(l-y,d)+o:o}var Ao=IS;function LS(o,l){return o==null?!0:cS(o,l)}var Gf=LS,DS=5*1e3,NS=class{constructor(o){b(this,"_cache",new ir),b(this,"_keepHotUntapDebounce"),fe(this,o)}get type(){return"Theatre_SheetObject_PublicAPI"}get props(){return $(this).propsP}get sheet(){return $(this).sheet.publicApi}get project(){return $(this).sheet.project.publicApi}get address(){return g({},$(this).address)}_valuesPrism(){return this._cache.get("_valuesPrism",()=>{const o=$(this);return(0,xo.prism)(()=>(0,xo.val)(o.getValues().getValue()))})}onValuesChange(o,l){return Su(this._valuesPrism(),o,l)}get value(){const o=this._valuesPrism();{if(!o.isHot){this._keepHotUntapDebounce!=null&&this._keepHotUntapDebounce.flush();const l=o.keepHot();this._keepHotUntapDebounce=Jb(()=>{l(),this._keepHotUntapDebounce=void 0},DS)}this._keepHotUntapDebounce&&this._keepHotUntapDebounce()}return o.getValue()}set initialValue(o){$(this).setInitialValue(o)}};function OS(o){const l=new WeakMap;return d=>(l.has(d)||l.set(d,o(d)),l.get(d))}function Da(o){return o.type==="compound"||o.type==="enum"}function Jl(o,l){if(!o)return;const[d,...y]=l;if(d===void 0)return o;if(!Da(o))return;const T=o.type==="enum"?o.cases[d]:o.props[d];return Jl(T,y)}function US(o){return!Da(o)}var FS=class{constructor(o,l,d){this.sheet=o,this.template=l,this.nativeObject=d,b(this,"$$isPointerToPrismProvider",!0),b(this,"address"),b(this,"publicApi"),b(this,"_initialValue",new Dt.Atom({})),b(this,"_cache",new ir),b(this,"_logger"),b(this,"_internalUtilCtx"),this._logger=o._logger.named("SheetObject",l.address.objectKey),this._logger._trace("creating object"),this._internalUtilCtx={logger:this._logger.utilFor.internal()},this.address=x(g({},l.address),{sheetInstanceId:o.address.sheetInstanceId}),this.publicApi=new NS(this)}get type(){return"Theatre_SheetObject"}getValues(){return this._cache.get("getValues()",()=>(0,Dt.prism)(()=>{const o=(0,Dt.val)(this.template.getDefaultValues()),l=(0,Dt.val)(this._initialValue.pointer),d=Dt.prism.memo("withInitialCache",()=>new WeakMap,[]),y=Rr(o,l,d),T=(0,Dt.val)(this.template.getStaticValues()),C=Dt.prism.memo("withStatics",()=>new WeakMap,[]);let Y=Rr(y,T,C),K;{const ve=Dt.prism.memo("seq",()=>this.getSequencedValues(),[]),xe=Dt.prism.memo("withSeqsCache",()=>new WeakMap,[]);K=(0,Dt.val)((0,Dt.val)(ve)),Y=Rr(Y,K,xe)}return ba("finalAtom",Y).pointer}))}getValueByPointer(o){const l=(0,Dt.val)(this.getValues()),{path:d}=(0,Dt.getPointerParts)(o);return(0,Dt.val)(Cr(l,d))}pointerToPrism(o){const{path:l}=(0,Dt.getPointerParts)(o);return(0,Dt.prism)(()=>{const d=(0,Dt.val)(this.getValues());return(0,Dt.val)(Cr(d,l))})}getSequencedValues(){return(0,Dt.prism)(()=>{const o=Dt.prism.memo("tracksToProcess",()=>this.template.getArrayOfValidSequenceTracks(),[]),l=(0,Dt.val)(o),d=new Dt.Atom({}),y=(0,Dt.val)(this.template.configPointer);return Dt.prism.effect("processTracks",()=>{const T=[];for(const{trackId:C,pathToProp:k}of l){const Y=this._trackIdToPrism(C),K=Jl(y,k),oe=K.deserializeAndSanitize,ve=K.interpolate,xe=()=>{const je=Y.getValue();if(!je)return d.setByPointer(wt=>Cr(wt,k),void 0);const Be=oe(je.left),ut=Be===void 0?K.default:Be;if(je.right===void 0)return d.setByPointer(wt=>Cr(wt,k),ut);const gt=oe(je.right),lt=gt===void 0?K.default:gt;return d.setByPointer(wt=>Cr(wt,k),ve(ut,lt,je.progression))},Ae=Y.onStale(xe);xe(),T.push(Ae)}return()=>{for(const C of T)C()}},[y,...l]),d.pointer})}_trackIdToPrism(o){const l=this.template.project.pointers.historic.sheetsById[this.address.sheetId].sequence.tracksByObject[this.address.objectKey].trackData[o],d=this.sheet.getSequence().positionPrism;return Tl(this._internalUtilCtx,l,d)}get propsP(){return this._cache.get("propsP",()=>(0,Dt.pointer)({root:this,path:[]}))}validateValue(o,l){}setInitialValue(o){this.validateValue(this.propsP,o),this._initialValue.set(o)}};function Gt(o){return function(d,y){return o(d,y())}}var Yn={_hmm:Kn(524),_todo:Kn(522),_error:Kn(521),errorDev:Kn(529),errorPublic:Kn(545),_kapow:Kn(268),_warn:Kn(265),warnDev:Kn(273),warnPublic:Kn(289),_debug:Kn(137),debugDev:Kn(145),_trace:Kn(73),traceDev:Kn(81)};function Kn(o){return Object.freeze({audience:Nr(o,8)?"internal":Nr(o,16)?"dev":"public",category:Nr(o,4)?"troubleshooting":Nr(o,2)?"todo":"general",level:Nr(o,512)?512:Nr(o,256)?256:Nr(o,128)?128:64})}function Nr(o,l){return(o&l)===l}function Wt(o,l){return((l&32)===32?!0:(l&16)===16?o.dev:(l&8)===8?o.internal:!1)&&o.min<=l}var Di={loggingConsoleStyle:!0,loggerConsoleStyle:!0,includes:Object.freeze({internal:!1,dev:!1,min:256}),filtered:function(){},include:function(){return{}},create:null,creatExt:null,named(o,l,d){return this.create({names:[...o.names,{name:l,key:d}]})},style:{bold:void 0,italic:void 0,cssMemo:new Map([["",""]]),collapseOnRE:/[a-z- ]+/g,color:void 0,collapsed(o){if(o.length<5)return o;const l=o.replace(this.collapseOnRE,"");return this.cssMemo.has(l)||this.cssMemo.set(l,this.css(o)),l},css(o){var l,d,y,T;const C=this.cssMemo.get(o);if(C)return C;let k="color:".concat((d=(l=this.color)==null?void 0:l.call(this,o))!=null?d:"hsl(".concat((o.charCodeAt(0)+o.charCodeAt(o.length-1))%360,", 100%, 60%)"));return(y=this.bold)!=null&&y.test(o)&&(k+=";font-weight:600"),(T=this.italic)!=null&&T.test(o)&&(k+=";font-style:italic"),this.cssMemo.set(o,k),k}}};function Wf(o=console,l={}){const d=x(g({},Di),{includes:g({},Di.includes)}),y={styled:zS.bind(d,o),noStyle:VS.bind(d,o)},T=kS.bind(d);function C(){return d.loggingConsoleStyle&&d.loggerConsoleStyle?y.styled:y.noStyle}return d.create=C(),{configureLogger(k){var Y;k==="console"?(d.loggerConsoleStyle=Di.loggerConsoleStyle,d.create=C()):k.type==="console"?(d.loggerConsoleStyle=(Y=k.style)!=null?Y:Di.loggerConsoleStyle,d.create=C()):k.type==="keyed"?(d.creatExt=K=>k.keyed(K.names),d.create=T):k.type==="named"&&(d.creatExt=BS.bind(null,k.named),d.create=T)},configureLogging(k){var Y,K,oe,ve,xe;d.includes.dev=(Y=k.dev)!=null?Y:Di.includes.dev,d.includes.internal=(K=k.internal)!=null?K:Di.includes.internal,d.includes.min=(oe=k.min)!=null?oe:Di.includes.min,d.include=(ve=k.include)!=null?ve:Di.include,d.loggingConsoleStyle=(xe=k.consoleStyle)!=null?xe:Di.loggingConsoleStyle,d.create=C()},getLogger(){return d.create({names:[]})}}}function BS(o,l){const d=[];for(let{name:y,key:T}of l.names)d.push(T==null?y:"".concat(y," (").concat(T,")"));return o(d)}function kS(o){const l=g(g({},this.includes),this.include(o)),d=this.filtered,y=this.named.bind(this,o),T=this.creatExt(o),C=Wt(l,524),k=Wt(l,522),Y=Wt(l,521),K=Wt(l,529),oe=Wt(l,545),ve=Wt(l,265),xe=Wt(l,268),Ae=Wt(l,273),je=Wt(l,289),Be=Wt(l,137),ut=Wt(l,145),gt=Wt(l,73),lt=Wt(l,81),wt=C?T.error.bind(T,Yn._hmm):d.bind(o,524),An=k?T.error.bind(T,Yn._todo):d.bind(o,522),Hn=Y?T.error.bind(T,Yn._error):d.bind(o,521),wn=K?T.error.bind(T,Yn.errorDev):d.bind(o,529),Bt=oe?T.error.bind(T,Yn.errorPublic):d.bind(o,545),Pn=xe?T.warn.bind(T,Yn._kapow):d.bind(o,268),$n=ve?T.warn.bind(T,Yn._warn):d.bind(o,265),xi=Ae?T.warn.bind(T,Yn.warnDev):d.bind(o,273),zr=je?T.warn.bind(T,Yn.warnPublic):d.bind(o,273),Hr=Be?T.debug.bind(T,Yn._debug):d.bind(o,137),Vr=ut?T.debug.bind(T,Yn.debugDev):d.bind(o,145),Gr=gt?T.trace.bind(T,Yn._trace):d.bind(o,73),Wr=lt?T.trace.bind(T,Yn.traceDev):d.bind(o,81),sn={_hmm:wt,_todo:An,_error:Hn,errorDev:wn,errorPublic:Bt,_kapow:Pn,_warn:$n,warnDev:xi,warnPublic:zr,_debug:Hr,debugDev:Vr,_trace:Gr,traceDev:Wr,lazy:{_hmm:C?Gt(wt):wt,_todo:k?Gt(An):An,_error:Y?Gt(Hn):Hn,errorDev:K?Gt(wn):wn,errorPublic:oe?Gt(Bt):Bt,_kapow:xe?Gt(Pn):Pn,_warn:ve?Gt($n):$n,warnDev:Ae?Gt(xi):xi,warnPublic:je?Gt(zr):zr,_debug:Be?Gt(Hr):Hr,debugDev:ut?Gt(Vr):Vr,_trace:gt?Gt(Gr):Gr,traceDev:lt?Gt(Wr):Wr},named:y,utilFor:{internal(){return{debug:sn._debug,error:sn._error,warn:sn._warn,trace:sn._trace,named(Jn,jt){return sn.named(Jn,jt).utilFor.internal()}}},dev(){return{debug:sn.debugDev,error:sn.errorDev,warn:sn.warnDev,trace:sn.traceDev,named(Jn,jt){return sn.named(Jn,jt).utilFor.dev()}}},public(){return{error:sn.errorPublic,warn:sn.warnPublic,debug(Jn,jt){sn._warn('(public "debug" filtered out) '.concat(Jn),jt)},trace(Jn,jt){sn._warn('(public "trace" filtered out) '.concat(Jn),jt)},named(Jn,jt){return sn.named(Jn,jt).utilFor.public()}}}}};return sn}function zS(o,l){const d=g(g({},this.includes),this.include(l)),y=[];let T="";for(let K=0;K<l.names.length;K++){const{name:oe,key:ve}=l.names[K];if(T+=" %c".concat(oe),y.push(this.style.css(oe)),ve!=null){const xe="%c#".concat(ve);T+=xe,y.push(this.style.css(xe))}}const C=this.filtered,k=this.named.bind(this,l),Y=[T,...y];return jf(C,l,d,o,Y,HS(Y),k)}function HS(o){const l=o.slice(0);for(let d=1;d<l.length;d++)l[d]+=";background-color:#e0005a;padding:2px;color:white";return l}function VS(o,l){const d=g(g({},this.includes),this.include(l));let y="";for(let Y=0;Y<l.names.length;Y++){const{name:K,key:oe}=l.names[Y];y+=" ".concat(K),oe!=null&&(y+="#".concat(oe))}const T=this.filtered,C=this.named.bind(this,l),k=[y];return jf(T,l,d,o,k,k,C)}function jf(o,l,d,y,T,C,k){const Y=Wt(d,524),K=Wt(d,522),oe=Wt(d,521),ve=Wt(d,529),xe=Wt(d,545),Ae=Wt(d,265),je=Wt(d,268),Be=Wt(d,273),ut=Wt(d,289),gt=Wt(d,137),lt=Wt(d,145),wt=Wt(d,73),An=Wt(d,81),Hn=Y?y.error.bind(y,...T):o.bind(l,524),wn=K?y.error.bind(y,...T):o.bind(l,522),Bt=oe?y.error.bind(y,...T):o.bind(l,521),Pn=ve?y.error.bind(y,...T):o.bind(l,529),$n=xe?y.error.bind(y,...T):o.bind(l,545),xi=je?y.warn.bind(y,...C):o.bind(l,268),zr=Ae?y.warn.bind(y,...T):o.bind(l,265),Hr=Be?y.warn.bind(y,...T):o.bind(l,273),Vr=ut?y.warn.bind(y,...T):o.bind(l,273),Gr=gt?y.info.bind(y,...T):o.bind(l,137),Wr=lt?y.info.bind(y,...T):o.bind(l,145),sn=wt?y.debug.bind(y,...T):o.bind(l,73),Jn=An?y.debug.bind(y,...T):o.bind(l,81),jt={_hmm:Hn,_todo:wn,_error:Bt,errorDev:Pn,errorPublic:$n,_kapow:xi,_warn:zr,warnDev:Hr,warnPublic:Vr,_debug:Gr,debugDev:Wr,_trace:sn,traceDev:Jn,lazy:{_hmm:Y?Gt(Hn):Hn,_todo:K?Gt(wn):wn,_error:oe?Gt(Bt):Bt,errorDev:ve?Gt(Pn):Pn,errorPublic:xe?Gt($n):$n,_kapow:je?Gt(xi):xi,_warn:Ae?Gt(zr):zr,warnDev:Be?Gt(Hr):Hr,warnPublic:ut?Gt(Vr):Vr,_debug:gt?Gt(Gr):Gr,debugDev:lt?Gt(Wr):Wr,_trace:wt?Gt(sn):sn,traceDev:An?Gt(Jn):Jn},named:k,utilFor:{internal(){return{debug:jt._debug,error:jt._error,warn:jt._warn,trace:jt._trace,named(Ui,Fi){return jt.named(Ui,Fi).utilFor.internal()}}},dev(){return{debug:jt.debugDev,error:jt.errorDev,warn:jt.warnDev,trace:jt.traceDev,named(Ui,Fi){return jt.named(Ui,Fi).utilFor.dev()}}},public(){return{error:jt.errorPublic,warn:jt.warnPublic,debug(Ui,Fi){jt._warn('(public "debug" filtered out) '.concat(Ui),Fi)},trace(Ui,Fi){jt._warn('(public "trace" filtered out) '.concat(Ui),Fi)},named(Ui,Fi){return jt.named(Ui,Fi).utilFor.public()}}}}};return jt}var Xf=Wf(console,{});Xf.configureLogging({dev:!0,min:64});var Na=Xf.getLogger().named("Theatre.js (default logger)").utilFor.dev(),qf=new WeakMap;function GS(o){const l=qf.get(o);if(l)return l;const d=new Map;return qf.set(o,d),Yf([],o,d),d}function Yf(o,l,d){for(const[y,T]of Object.entries(l.props))if(!Da(T)){const C=[...o,y];d.set(JSON.stringify(C),d.size),Kf(C,T,d)}for(const[y,T]of Object.entries(l.props))if(Da(T)){const C=[...o,y];d.set(JSON.stringify(C),d.size),Kf(C,T,d)}}function Kf(o,l,d){if(l.type==="compound")Yf(o,l,d);else{if(l.type==="enum")throw new Error("Enums aren't supported yet");d.set(JSON.stringify(o),d.size)}}function Zf(o){return typeof o=="object"&&o!==null&&Object.keys(o).length===0}var WS=class{constructor(o,l,d,y,T){this.sheetTemplate=o,b(this,"address"),b(this,"type","Theatre_SheetObjectTemplate"),b(this,"_config"),b(this,"_temp_actions_atom"),b(this,"_cache",new ir),b(this,"project"),b(this,"pointerToSheetState"),b(this,"pointerToStaticOverrides"),this.address=x(g({},o.address),{objectKey:l}),this._config=new an.Atom(y),this._temp_actions_atom=new an.Atom(T),this.project=o.project,this.pointerToSheetState=this.sheetTemplate.project.pointers.historic.sheetsById[this.address.sheetId],this.pointerToStaticOverrides=this.pointerToSheetState.staticOverrides.byObject[this.address.objectKey]}get staticConfig(){return this._config.get()}get configPointer(){return this._config.pointer}get _temp_actions(){return this._temp_actions_atom.get()}get _temp_actionsPointer(){return this._temp_actions_atom.pointer}createInstance(o,l,d){return this._config.set(d),new FS(o,this,l)}reconfigure(o){this._config.set(o)}_temp_setActions(o){this._temp_actions_atom.set(o)}getDefaultValues(){return this._cache.get("getDefaultValues()",()=>(0,an.prism)(()=>{const o=(0,an.val)(this.configPointer);return Sl(o)}))}getStaticValues(){return this._cache.get("getStaticValues",()=>(0,an.prism)(()=>{var o;const l=(o=(0,an.val)(this.pointerToStaticOverrides))!=null?o:{};return(0,an.val)(this.configPointer).deserializeAndSanitize(l)||{}}))}getArrayOfValidSequenceTracks(){return this._cache.get("getArrayOfValidSequenceTracks",()=>(0,an.prism)(()=>{const o=this.project.pointers.historic.sheetsById[this.address.sheetId],l=(0,an.val)(o.sequence.tracksByObject[this.address.objectKey].trackIdByPropPath);if(!l)return re;const d=[];if(!l)return re;const y=(0,an.val)(this.configPointer),T=Object.entries(l);for(const[k,Y]of T){const K=jS(k);if(!K)continue;const oe=Jl(y,K);oe&&US(oe)&&d.push({pathToProp:K,trackId:Y})}const C=GS(y);return d.sort((k,Y)=>{const K=k.pathToProp,oe=Y.pathToProp,ve=C.get(JSON.stringify(K)),xe=C.get(JSON.stringify(oe));return ve>xe?1:-1}),d.length===0?re:d}))}getMapOfValidSequenceTracks_forStudio(){return this._cache.get("getMapOfValidSequenceTracks_forStudio",()=>(0,an.prism)(()=>{const o=(0,an.val)(this.getArrayOfValidSequenceTracks());let l={};for(const{pathToProp:d,trackId:y}of o)vs(l,d,y);return l}))}getStaticButNotSequencedOverrides(){return this._cache.get("getStaticButNotSequencedOverrides",()=>(0,an.prism)(()=>{const o=(0,an.val)(this.getStaticValues()),l=(0,an.val)(this.getArrayOfValidSequenceTracks()),d=Ax(o);for(const{pathToProp:y}of l){Gf(d,y);let T=y.slice(0,-1);for(;T.length>0;){const C=pa(d,T);if(!Zf(C))break;Gf(d,T),T=T.slice(0,-1)}}if(!Zf(d))return d}))}getDefaultsAtPointer(o){const{path:l}=(0,an.getPointerParts)(o),d=this.getDefaultValues().getValue();return pa(d,l)}};function jS(o){try{return JSON.parse(o)}catch{Na.warn("property ".concat(JSON.stringify(o)," cannot be parsed. Skipping."));return}}var $f=ln(),XS=OS(o=>JSON.stringify(o));A(O());var qS=class extends Error{},wo=class extends qS{},Jf=ln(),YS=ln(),KS=ln(),mn=ln();function sr(){let o,l;const d=new Promise((T,C)=>{o=k=>{T(k),y.status="resolved"},l=k=>{C(k),y.status="rejected"}}),y={resolve:o,reject:l,promise:d,status:"pending"};return y}var ZS=()=>{},Oa=ZS,$S=ln(),JS=class{constructor(){b(this,"_stopPlayCallback",Oa),b(this,"_state",new $S.Atom({position:0,playing:!1})),b(this,"statePointer"),this.statePointer=this._state.pointer}destroy(){}pause(){this._stopPlayCallback(),this.playing=!1,this._stopPlayCallback=Oa}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.setByPointer(l=>l.position,o)}getCurrentPosition(){return this._state.get().position}get playing(){return this._state.get().playing}set playing(o){this._state.setByPointer(l=>l.playing,o)}play(o,l,d,y,T){this.playing&&this.pause(),this.playing=!0;const C=l[1]-l[0];{const Ae=this.getCurrentPosition();Ae<l[0]||Ae>l[1]?y==="normal"||y==="alternate"?this._updatePositionInState(l[0]):(y==="reverse"||y==="alternateReverse")&&this._updatePositionInState(l[1]):y==="normal"||y==="alternate"?Ae===l[1]&&this._updatePositionInState(l[0]):Ae===l[0]&&this._updatePositionInState(l[1])}const k=sr(),Y=T.time,K=C*o;let oe=this.getCurrentPosition()-l[0];(y==="reverse"||y==="alternateReverse")&&(oe=l[1]-this.getCurrentPosition());const ve=Ae=>{const Be=Math.max(Ae-Y,0)/1e3,ut=Math.min(Be*d+oe,K);if(ut!==K){const gt=Math.floor(ut/C);let lt=ut/C%1*C;if(y!=="normal")if(y==="reverse")lt=C-lt;else{const wt=gt%2===0;y==="alternate"?wt||(lt=C-lt):wt&&(lt=C-lt)}this._updatePositionInState(lt+l[0]),xe()}else{if(y==="normal")this._updatePositionInState(l[1]);else if(y==="reverse")this._updatePositionInState(l[0]);else{const gt=(o-1)%2===0;y==="alternate"?gt?this._updatePositionInState(l[1]):this._updatePositionInState(l[0]):gt?this._updatePositionInState(l[0]):this._updatePositionInState(l[1])}this.playing=!1,k.resolve(!0)}};this._stopPlayCallback=()=>{T.offThisOrNextTick(ve),T.offNextTick(ve),this.playing&&k.resolve(!1)};const xe=()=>T.onNextTick(ve);return T.onThisOrNextTick(ve),k.promise}playDynamicRange(o,l){this.playing&&this.pause(),this.playing=!0;const d=sr(),y=o.keepHot();d.promise.then(y,y);let T=l.time;const C=Y=>{const K=Math.max(Y-T,0);T=Y;const oe=K/1e3,ve=this.getCurrentPosition(),xe=o.getValue();if(ve<xe[0]||ve>xe[1])this.gotoPosition(xe[0]);else{let Ae=ve+oe;Ae>xe[1]&&(Ae=xe[0]+(Ae-xe[1])),this.gotoPosition(Ae)}k()};this._stopPlayCallback=()=>{l.offThisOrNextTick(C),l.offNextTick(C),d.resolve(!1)};const k=()=>l.onNextTick(C);return l.onThisOrNextTick(C),d.promise}},QS=ln(),eM="__TheatreJS_StudioBundle",Ql="__TheatreJS_CoreBundle",tM="__TheatreJS_Notifications",Ua=o=>(...l)=>{var d;switch(o){case"success":{Na.debug(l.slice(0,2).join(`
`));break}case"info":{Na.debug(l.slice(0,2).join(`
`));break}case"warning":{Na.warn(l.slice(0,2).join(`
`));break}}return typeof window<"u"?(d=window[tM])==null?void 0:d.notify[o](...l):void 0},Ss={warning:Ua("warning"),success:Ua("success"),info:Ua("info"),error:Ua("error")};typeof window<"u"&&(window.addEventListener("error",o=>{Ss.error("An error occurred","<pre>".concat(o.message,`</pre>

See **console** for details.`))}),window.addEventListener("unhandledrejection",o=>{Ss.error("An error occurred","<pre>".concat(o.reason,`</pre>

See **console** for details.`))}));var nM=class{constructor(o,l,d){this._decodedBuffer=o,this._audioContext=l,this._nodeDestination=d,b(this,"_mainGain"),b(this,"_state",new QS.Atom({position:0,playing:!1})),b(this,"statePointer"),b(this,"_stopPlayCallback",Oa),this.statePointer=this._state.pointer,this._mainGain=this._audioContext.createGain(),this._mainGain.connect(this._nodeDestination)}playDynamicRange(o,l){const d=sr();this._playing&&this.pause(),this._playing=!0;let y;const T=()=>{y==null||y(),y=this._loopInRange(o.getValue(),l).stop},C=o.onStale(T);return T(),this._stopPlayCallback=()=>{y==null||y(),C(),d.resolve(!1)},d.promise}_loopInRange(o,l){let y=this.getCurrentPosition();const T=o[1]-o[0];y<o[0]||y>o[1]?this._updatePositionInState(o[0]):y===o[1]&&this._updatePositionInState(o[0]),y=this.getCurrentPosition();const C=this._audioContext.createBufferSource();C.buffer=this._decodedBuffer,C.connect(this._mainGain),C.playbackRate.value=1,C.loop=!0,C.loopStart=o[0],C.loopEnd=o[1];const k=l.time;let Y=y-o[0];C.start(0,y);const K=xe=>{let ut=(Math.max(xe-k,0)/1e3*1+Y)/T%1*T;this._updatePositionInState(ut+o[0]),oe()},oe=()=>l.onNextTick(K);return l.onThisOrNextTick(K),{stop:()=>{C.stop(),C.disconnect(),l.offThisOrNextTick(K),l.offNextTick(K)}}}get _playing(){return this._state.get().playing}set _playing(o){this._state.setByPointer(l=>l.playing,o)}destroy(){}pause(){this._stopPlayCallback(),this._playing=!1,this._stopPlayCallback=Oa}gotoPosition(o){this._updatePositionInState(o)}_updatePositionInState(o){this._state.reduce(l=>x(g({},l),{position:o}))}getCurrentPosition(){return this._state.get().position}play(o,l,d,y,T){this._playing&&this.pause(),this._playing=!0;let C=this.getCurrentPosition();const k=l[1]-l[0];if(y!=="normal")throw new wo('Audio-controlled sequences can only be played in the "normal" direction. '+"'".concat(y,"' given."));C<l[0]||C>l[1]?this._updatePositionInState(l[0]):C===l[1]&&this._updatePositionInState(l[0]),C=this.getCurrentPosition();const Y=sr(),K=this._audioContext.createBufferSource();K.buffer=this._decodedBuffer,K.connect(this._mainGain),K.playbackRate.value=d,o>1e3&&(Ss.warning("Can't play sequences with audio more than 1000 times","The sequence will still play, but only 1000 times. The `iterationCount: ".concat(o,"` provided to `sequence.play()`\nis too high for a sequence with audio.\n\nTo fix this, either set `iterationCount` to a lower value, or remove the audio from the sequence."),[{url:"https://www.theatrejs.com/docs/latest/manual/audio",title:"Using Audio"},{url:"https://www.theatrejs.com/docs/latest/api/core#sequence.attachaudio",title:"Audio API"}]),o=1e3),o>1&&(K.loop=!0,K.loopStart=l[0],K.loopEnd=l[1]);const oe=T.time;let ve=C-l[0];const xe=k*o;K.start(0,C,xe-ve);const Ae=ut=>{const lt=Math.max(ut-oe,0)/1e3,wt=Math.min(lt*d+ve,xe);if(wt!==xe){let An=wt/k%1*k;this._updatePositionInState(An+l[0]),Be()}else this._updatePositionInState(l[1]),this._playing=!1,je(),Y.resolve(!0)},je=()=>{K.stop(),K.disconnect()};this._stopPlayCallback=()=>{je(),T.offThisOrNextTick(Ae),T.offNextTick(Ae),this._playing&&Y.resolve(!1)};const Be=()=>T.onNextTick(Ae);return T.onThisOrNextTick(Ae),Y.promise}},iM=ln(),Qf=0;function eu(o){var l;const d=k=>{y.tick(k)},y=new iM.Ticker({onActive(){var k;(k=o==null?void 0:o.start)==null||k.call(o)},onDormant(){var k;(k=o==null?void 0:o.stop)==null||k.call(o)}}),T={tick:d,id:Qf++,name:(l=o==null?void 0:o.name)!=null?l:"CustomRafDriver-".concat(Qf),type:"Theatre_RafDriver_PublicAPI"},C={type:"Theatre_RafDriver_PrivateAPI",publicApi:T,ticker:y,start:o==null?void 0:o.start,stop:o==null?void 0:o.stop};return fe(T,C),T}function rM(){let o=null;const y=eu({name:"DefaultCoreRafDriver",start:()=>{if(typeof window<"u"){const T=C=>{y.tick(C),o=window.requestAnimationFrame(T)};o=window.requestAnimationFrame(T)}else y.tick(0),setTimeout(()=>y.tick(1),0)},stop:()=>{typeof window<"u"&&o!==null&&window.cancelAnimationFrame(o)}});return y}var Fa;function ep(){return Fa||sM(rM()),Fa}function tp(){return ep().ticker}function sM(o){if(Fa)throw new Error("`setCoreRafDriver()` is already called.");Fa=$(o)}var oM=class{get type(){return"Theatre_Sequence_PublicAPI"}constructor(o){fe(this,o)}play(o){const l=$(this);if(l._project.isReady()){const d=o!=null&&o.rafDriver?$(o.rafDriver).ticker:tp();return l.play(o??{},d)}else{const d=sr();return d.resolve(!0),d.promise}}pause(){$(this).pause()}get position(){return $(this).position}set position(o){$(this).position=o}__experimental_getKeyframes(o){return $(this).getKeyframesOfSimpleProp(o)}async attachAudio(o){const{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:T}=await aM(o),C=new nM(y,l,T);return $(this).replacePlaybackController(C),{audioContext:l,destinationNode:d,decodedBuffer:y,gainNode:T}}get pointer(){return $(this).pointer}};async function aM(o){function l(){if(o.audioContext)return Promise.resolve(o.audioContext);const oe=new AudioContext;return oe.state==="running"||typeof window>"u"?Promise.resolve(oe):new Promise(ve=>{const xe=()=>{oe.resume().catch(Be=>{console.error(Be)})},Ae=["mousedown","keydown","touchstart"],je={capture:!0,passive:!1};Ae.forEach(Be=>{window.addEventListener(Be,xe,je)}),oe.addEventListener("statechange",()=>{oe.state==="running"&&(Ae.forEach(Be=>{window.removeEventListener(Be,xe,je)}),ve(oe))})})}async function d(){if(o.source instanceof AudioBuffer)return o.source;const oe=sr();if(typeof o.source!="string")throw new Error("Error validating arguments to sequence.attachAudio(). args.source must either be a string or an instance of AudioBuffer.");let ve;try{ve=await fetch(o.source)}catch(Be){throw console.error(Be),new Error("Could not fetch '".concat(o.source,"'. Network error logged above."))}let xe;try{xe=await ve.arrayBuffer()}catch(Be){throw console.error(Be),new Error("Could not read '".concat(o.source,"' as an arrayBuffer."))}(await y).decodeAudioData(xe,oe.resolve,oe.reject);let je;try{je=await oe.promise}catch(Be){throw console.error(Be),new Error("Could not decode ".concat(o.source," as an audio file."))}return je}const y=l(),T=d(),[C,k]=await Promise.all([y,T]),Y=o.destinationNode||C.destination,K=C.createGain();return K.connect(Y),{audioContext:C,decodedBuffer:k,gainNode:K,destinationNode:Y}}var cM=lM("Theatre_SheetObject");function lM(o){return l=>typeof l=="object"&&!!l&&l.type===o}var uM=class{constructor(o,l,d,y,T){this._project=o,this._sheet=l,this._lengthD=d,this._subUnitsPerUnitD=y,b(this,"address"),b(this,"publicApi"),b(this,"_playbackControllerBox"),b(this,"_prismOfStatePointer"),b(this,"_positionD"),b(this,"_positionFormatterD"),b(this,"_playableRangeD"),b(this,"pointer",(0,KS.pointer)({root:this,path:[]})),b(this,"$$isPointerToPrismProvider",!0),b(this,"_logger"),b(this,"closestGridPosition",C=>{const Y=1/this.subUnitsPerUnit;return parseFloat((Math.round(C/Y)*Y).toFixed(3))}),this._logger=o._logger.named("Sheet",l.address.sheetId).named("Instance",l.address.sheetInstanceId),this.address=x(g({},this._sheet.address),{sequenceName:"default"}),this.publicApi=new oM(this),this._playbackControllerBox=new YS.Atom(T??new JS),this._prismOfStatePointer=(0,mn.prism)(()=>this._playbackControllerBox.prism.getValue().statePointer),this._positionD=(0,mn.prism)(()=>{const C=this._prismOfStatePointer.getValue();return(0,mn.val)(C.position)}),this._positionFormatterD=(0,mn.prism)(()=>{const C=(0,mn.val)(this._subUnitsPerUnitD);return new hM(C)})}get type(){return"Theatre_Sequence"}pointerToPrism(o){const{path:l}=(0,Jf.getPointerParts)(o);if(l.length===0)return(0,mn.prism)(()=>({length:(0,mn.val)(this.pointer.length),playing:(0,mn.val)(this.pointer.playing),position:(0,mn.val)(this.pointer.position),subUnitsPerUnit:(0,mn.val)(this.pointer.subUnitsPerUnit)}));if(l.length>1)return(0,mn.prism)(()=>{});const[d]=l;return d==="length"?this._lengthD:d==="subUnitsPerUnit"?this._subUnitsPerUnitD:d==="position"?this._positionD:d==="playing"?(0,mn.prism)(()=>(0,mn.val)(this._prismOfStatePointer.getValue().playing)):(0,mn.prism)(()=>{})}getKeyframesOfSimpleProp(o){const{path:l,root:d}=(0,Jf.getPointerParts)(o);if(!cM(d))throw new wo("Argument prop must be a pointer to a SheetObject property");const y=(0,mn.val)(this._project.pointers.historic.sheetsById[this._sheet.address.sheetId].sequence.tracksByObject[d.address.objectKey]);if(!y)return[];const{trackData:T,trackIdByPropPath:C}=y,k=XS(l),Y=C[k];if(!Y)return[];const K=T[Y];return K?K.keyframes:[]}get positionFormatter(){return this._positionFormatterD.getValue()}get prismOfStatePointer(){return this._prismOfStatePointer}get length(){return this._lengthD.getValue()}get positionPrism(){return this._positionD}get position(){return this._playbackControllerBox.get().getCurrentPosition()}get subUnitsPerUnit(){return this._subUnitsPerUnitD.getValue()}get positionSnappedToGrid(){return this.closestGridPosition(this.position)}set position(o){let l=o;this.pause(),l>this.length&&(l=this.length);const d=this.length;this._playbackControllerBox.get().gotoPosition(l>d?d:l)}getDurationCold(){return this._lengthD.getValue()}get playing(){return(0,mn.val)(this._playbackControllerBox.get().statePointer.playing)}_makeRangeFromSequenceTemplate(){return(0,mn.prism)(()=>[0,(0,mn.val)(this._lengthD)])}playDynamicRange(o,l){return this._playbackControllerBox.get().playDynamicRange(o,l)}async play(o,l){const d=this.length,y=o&&o.range?o.range:[0,d],T=o&&typeof o.iterationCount=="number"?o.iterationCount:1,C=o&&typeof o.rate<"u"?o.rate:1,k=o&&o.direction?o.direction:"normal";return await this._play(T,[y[0],y[1]],C,k,l)}_play(o,l,d,y,T){return this._playbackControllerBox.get().play(o,l,d,y,T)}pause(){this._playbackControllerBox.get().pause()}replacePlaybackController(o){this.pause();const l=this._playbackControllerBox.get();this._playbackControllerBox.set(o);const d=l.getCurrentPosition();l.destroy(),o.gotoPosition(d)}},hM=class{constructor(o){this._fps=o}formatSubUnitForGrid(o){const l=o%1,d=1/this._fps;return Math.round(l/d)+"f"}formatFullUnitForGrid(o){let l=o,d="";if(l>=Ms){const T=Math.floor(l/Ms);d+=T+"h",l=l%Ms}if(l>=Ur){const T=Math.floor(l/Ur);d+=T+"m",l=l%Ur}if(l>=Or){const T=Math.floor(l/Or);d+=T+"s",l=l%Or}const y=1/this._fps;if(l>=y){const T=Math.floor(l/y);d+=T+"f",l=l%y}return d.length===0?"0s":d}formatForPlayhead(o){let l=o,d="";if(l>=Ms){const T=Math.floor(l/Ms);d+=Ao(T.toString(),2,"0")+"h",l=l%Ms}if(l>=Ur){const T=Math.floor(l/Ur);d+=Ao(T.toString(),2,"0")+"m",l=l%Ur}else d.length>0&&(d+="00m");if(l>=Or){const T=Math.floor(l/Or);d+=Ao(T.toString(),2,"0")+"s",l=l%Or}else d+="00s";const y=1/this._fps;if(l>=y){const T=Math.round(l/y);d+=Ao(T.toString(),2,"0")+"f",l=l%y}else l/y>.98?(d+=Ao("1",2,"0")+"f",l=l%y):d+="00f";return d.length===0?"00s00f":d}formatBasic(o){return o.toFixed(2)+"s"}},Or=1,Ur=Or*60,Ms=Ur*60,tu={};v(tu,{boolean:()=>cp,compound:()=>iu,file:()=>yM,image:()=>bM,number:()=>ap,rgba:()=>AM,string:()=>lp,stringLiteral:()=>IM});function np(o,l){return o.length<=l?o:o.substr(0,l-3)+"..."}var dM=o=>typeof o=="string"?'string("'.concat(np(o,10),'")'):typeof o=="number"?"number(".concat(np(String(o),10),")"):o===null?"null":o===void 0?"undefined":typeof o=="boolean"?String(o):Array.isArray(o)?"array":typeof o=="object"?"object":"unknown",ip=dM;function fM(o,{removeAlphaIfOpaque:l=!1}={}){const d=(o.a*255|256).toString(16).slice(1),y=(o.r*255|256).toString(16).slice(1)+(o.g*255|256).toString(16).slice(1)+(o.b*255|256).toString(16).slice(1)+(l&&d==="ff"?"":d);return"#".concat(y)}function nu(o){return x(g({},o),{toString(){return fM(this,{removeAlphaIfOpaque:!0})}})}function pM(o){return Object.fromEntries(Object.entries(o).map(([l,d])=>[l,nf(d,0,1)]))}function mM(o){function l(d){return d>=.0031308?1.055*d**(1/2.4)-.055:12.92*d}return pM({r:l(o.r),g:l(o.g),b:l(o.b),a:o.a})}function rp(o){function l(d){return d>=.04045?((d+.055)/(1+.055))**2.4:d/12.92}return{r:l(o.r),g:l(o.g),b:l(o.b),a:o.a}}function sp(o){let l=.4122214708*o.r+.5363325363*o.g+.0514459929*o.b,d=.2119034982*o.r+.6806995451*o.g+.1073969566*o.b,y=.0883024619*o.r+.2817188376*o.g+.6299787005*o.b,T=Math.cbrt(l),C=Math.cbrt(d),k=Math.cbrt(y);return{L:.2104542553*T+.793617785*C-.0040720468*k,a:1.9779984951*T-2.428592205*C+.4505937099*k,b:.0259040371*T+.7827717662*C-.808675766*k,alpha:o.a}}function gM(o){let l=o.L+.3963377774*o.a+.2158037573*o.b,d=o.L-.1055613458*o.a-.0638541728*o.b,y=o.L-.0894841775*o.a-1.291485548*o.b,T=l*l*l,C=d*d*d,k=y*y*y;return{r:4.0767416621*T-3.3077115913*C+.2309699292*k,g:-1.2684380046*T+2.6097574011*C-.3413193965*k,b:-.0041960863*T-.7034186147*C+1.707614701*k,a:o.alpha}}var Ni=Symbol("TheatrePropType_Basic");function op(o){return typeof o=="object"&&!!o&&o[Ni]==="TheatrePropType"}function _M(o){if(typeof o=="number")return ap(o);if(typeof o=="boolean")return cp(o);if(typeof o=="string")return lp(o);if(typeof o=="object"&&o){if(op(o))return o;if(Dv(o))return iu(o);throw new wo("This value is not a valid prop type: ".concat(ip(o)))}else throw new wo("This value is not a valid prop type: ".concat(ip(o)))}function vM(o){const l={};for(const d of Object.keys(o)){const y=o[d];op(y)?l[d]=y:l[d]=_M(y)}return l}var iu=(o,l={})=>{const d=vM(o),y=new WeakMap;return{type:"compound",props:d,valueType:null,[Ni]:"TheatrePropType",label:l.label,default:oS(d,C=>C.default),deserializeAndSanitize:C=>{if(typeof C!="object"||!C)return;if(y.has(C))return y.get(C);const k={};let Y=!1;for(const[K,oe]of Object.entries(d))if(Object.prototype.hasOwnProperty.call(C,K)){const ve=oe.deserializeAndSanitize(C[K]);ve!=null&&(Y=!0,k[K]=ve)}if(y.set(C,k),Y)return k}}},yM=(o,l={})=>{const d=(y,T,C)=>{var k;return{type:"file",id:((k=l.interpolate)!=null?k:Po)(y.id,T.id,C)}};return{type:"file",default:{type:"file",id:o},valueType:null,[Ni]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:xM}},xM=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="file"&&(l=!1),!!l)return o},bM=(o,l={})=>{const d=(y,T,C)=>{var k;return{type:"image",id:((k=l.interpolate)!=null?k:Po)(y.id,T.id,C)}};return{type:"image",default:{type:"image",id:o},valueType:null,[Ni]:"TheatrePropType",label:l.label,interpolate:d,deserializeAndSanitize:SM}},SM=o=>{if(!o)return;let l=!0;if(typeof o.id!="string"&&![null,void 0].includes(o.id)&&(l=!1),o.type!=="image"&&(l=!1),!!l)return o},ap=(o,l={})=>{var d;return x(g({type:"number",valueType:0,default:o,[Ni]:"TheatrePropType"},l||{}),{label:l.label,nudgeFn:(d=l.nudgeFn)!=null?d:LM,nudgeMultiplier:typeof l.nudgeMultiplier=="number"?l.nudgeMultiplier:void 0,interpolate:EM,deserializeAndSanitize:MM(l.range)})},MM=o=>o?l=>{if(typeof l=="number"&&isFinite(l))return nf(l,o[0],o[1])}:TM,TM=o=>typeof o=="number"&&isFinite(o)?o:void 0,EM=(o,l,d)=>o+d*(l-o),AM=(o={r:0,g:0,b:0,a:1},l={})=>{const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return{type:"rgba",valueType:null,default:nu(d),[Ni]:"TheatrePropType",label:l.label,interpolate:PM,deserializeAndSanitize:wM}},wM=o=>{if(!o)return;let l=!0;for(const y of["r","g","b","a"])(!Object.prototype.hasOwnProperty.call(o,y)||typeof o[y]!="number")&&(l=!1);if(!l)return;const d={};for(const y of["r","g","b","a"])d[y]=Math.min(Math.max(o[y],0),1);return nu(d)},PM=(o,l,d)=>{const y=sp(rp(o)),T=sp(rp(l)),C={L:(1-d)*y.L+d*T.L,a:(1-d)*y.a+d*T.a,b:(1-d)*y.b+d*T.b,alpha:(1-d)*y.alpha+d*T.alpha},k=mM(gM(C));return nu(k)},cp=(o,l={})=>{var d;return{type:"boolean",default:o,valueType:null,[Ni]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:RM}},RM=o=>typeof o=="boolean"?o:void 0;function Po(o){return o}var lp=(o,l={})=>{var d;return{type:"string",default:o,valueType:null,[Ni]:"TheatrePropType",label:l.label,interpolate:(d=l.interpolate)!=null?d:Po,deserializeAndSanitize:CM}};function CM(o){return typeof o=="string"?o:void 0}function IM(o,l,d={}){var y,T;return{type:"stringLiteral",default:o,valuesAndLabels:g({},l),[Ni]:"TheatrePropType",valueType:null,as:(y=d.as)!=null?y:"menu",label:d.label,interpolate:(T=d.interpolate)!=null?T:Po,deserializeAndSanitize(C){if(typeof C=="string"&&Object.prototype.hasOwnProperty.call(l,C))return C}}}var LM=({config:o,deltaX:l,deltaFraction:d,magnitude:y})=>{var T;const{range:C}=o;return!o.nudgeMultiplier&&C&&!C.includes(1/0)&&!C.includes(-1/0)?d*(C[1]-C[0])*y:l*y*((T=o.nudgeMultiplier)!=null?T:1)},DM=o=>o.replace(/^[\s\/]*/,"").replace(/[\s\/]*$/,"").replace(/\s*\/\s*/g," / ");function Ba(o,l){return DM(o)}A(z());var NM=class{get type(){return"Theatre_Sheet_PublicAPI"}constructor(o){fe(this,o)}object(o,l,d){const y=$(this),T=Ba(o),C=y.getObject(T),k=null,Y=d==null?void 0:d.__actions__THIS_API_IS_UNSTABLE_AND_WILL_CHANGE_IN_THE_NEXT_VERSION;if(C)return Y&&C.template._temp_setActions(Y),C.publicApi;{const K=iu(l);return y.createObject(T,k,K,Y).publicApi}}__experimental_getExistingObject(o){const l=$(this),d=Ba(o),y=l.getObject(d);return y==null?void 0:y.publicApi}get sequence(){return $(this).getSequence().publicApi}get project(){return $(this).project.publicApi}get address(){return g({},$(this).address)}detachObject(o){const l=$(this),d=Ba(o);if(!l.getObject(d)){Ss.warning(`Couldn't delete object "`.concat(d,'"'),'There is no object with key "'.concat(d,`".

To fix this, make sure you are calling \`sheet.deleteObject("`).concat(d,'")` with the correct key.')),console.warn('Object key "'.concat(d,'" does not exist.'));return}l.deleteObject(d)}},Ro=ln(),OM=class{constructor(o,l){this.template=o,this.instanceId=l,b(this,"_objects",new Ro.Atom({})),b(this,"_sequence"),b(this,"address"),b(this,"publicApi"),b(this,"project"),b(this,"objectsP",this._objects.pointer),b(this,"type","Theatre_Sheet"),b(this,"_logger"),this._logger=o.project._logger.named("Sheet",l),this._logger._trace("creating sheet"),this.project=o.project,this.address=x(g({},o.address),{sheetInstanceId:this.instanceId}),this.publicApi=new NM(this)}createObject(o,l,d,y={}){const C=this.template.getObjectTemplate(o,l,d,y).createInstance(this,l,d);return this._objects.setByPointer(k=>k[o],C),C}getObject(o){return this._objects.get()[o]}deleteObject(o){this._objects.reduce(l=>{const d=g({},l);return delete d[o],d})}getSequence(){if(!this._sequence){const o=(0,Ro.prism)(()=>{const d=(0,Ro.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.length);return UM(d)}),l=(0,Ro.prism)(()=>{const d=(0,Ro.val)(this.project.pointers.historic.sheetsById[this.address.sheetId].sequence.subUnitsPerUnit);return FM(d)});this._sequence=new uM(this.template.project,this,o,l)}return this._sequence}},UM=o=>typeof o=="number"&&isFinite(o)&&o>0?o:10,FM=o=>typeof o=="number"&&rS(o)&&o>=1&&o<=1e3?o:30,BM=class{constructor(o,l){this.project=o,b(this,"type","Theatre_SheetTemplate"),b(this,"address"),b(this,"_instances",new $f.Atom({})),b(this,"instancesP",this._instances.pointer),b(this,"_objectTemplates",new $f.Atom({})),b(this,"objectTemplatesP",this._objectTemplates.pointer),this.address=x(g({},o.address),{sheetId:l})}getInstance(o){let l=this._instances.get()[o];return l||(l=new OM(this,o),this._instances.setByPointer(d=>d[o],l)),l}getObjectTemplate(o,l,d,y){let T=this._objectTemplates.get()[o];return T||(T=new WS(this,o,l,d,y),this._objectTemplates.setByPointer(C=>C[o],T)),T}},ru=ln(),up=ln(),kM=o=>new Promise(l=>setTimeout(l,o)),zM=kM;function ri(o){for(var l=arguments.length,d=Array(l>1?l-1:0),y=1;y<l;y++)d[y-1]=arguments[y];throw Error("[Immer] minified error nr: "+o+(d.length?" "+d.map(function(T){return"'"+T+"'"}).join(","):"")+". Find the full error at: https://bit.ly/3cXEKWf")}function Fr(o){return!!o&&!!o[zn]}function Br(o){return!!o&&((function(l){if(!l||typeof l!="object")return!1;var d=Object.getPrototypeOf(l);if(d===null)return!0;var y=Object.hasOwnProperty.call(d,"constructor")&&d.constructor;return y===Object||typeof y=="function"&&Function.toString.call(y)===KM})(o)||Array.isArray(o)||!!o[xp]||!!o.constructor[xp]||ou(o)||au(o))}function HM(o){return Fr(o)||ri(23,o),o[zn].t}function Co(o,l,d){d===void 0&&(d=!1),Ts(o)===0?(d?Object.keys:yu)(o).forEach(function(y){d&&typeof y=="symbol"||l(y,o[y],o)}):o.forEach(function(y,T){return l(T,y,o)})}function Ts(o){var l=o[zn];return l?l.i>3?l.i-4:l.i:Array.isArray(o)?1:ou(o)?2:au(o)?3:0}function su(o,l){return Ts(o)===2?o.has(l):Object.prototype.hasOwnProperty.call(o,l)}function VM(o,l){return Ts(o)===2?o.get(l):o[l]}function hp(o,l,d){var y=Ts(o);y===2?o.set(l,d):y===3?(o.delete(l),o.add(d)):o[l]=d}function GM(o,l){return o===l?o!==0||1/o==1/l:o!=o&&l!=l}function ou(o){return qM&&o instanceof Map}function au(o){return YM&&o instanceof Set}function kr(o){return o.o||o.t}function cu(o){if(Array.isArray(o))return Array.prototype.slice.call(o);var l=ZM(o);delete l[zn];for(var d=yu(l),y=0;y<d.length;y++){var T=d[y],C=l[T];C.writable===!1&&(C.writable=!0,C.configurable=!0),(C.get||C.set)&&(l[T]={configurable:!0,writable:!0,enumerable:C.enumerable,value:o[T]})}return Object.create(Object.getPrototypeOf(o),l)}function lu(o,l){return l===void 0&&(l=!1),uu(o)||Fr(o)||!Br(o)||(Ts(o)>1&&(o.set=o.add=o.clear=o.delete=WM),Object.freeze(o),l&&Co(o,function(d,y){return lu(y,!0)},!0)),o}function WM(){ri(2)}function uu(o){return o==null||typeof o!="object"||Object.isFrozen(o)}function Oi(o){var l=$M[o];return l||ri(18,o),l}function dp(){return Io}function hu(o,l){l&&(Oi("Patches"),o.u=[],o.s=[],o.v=l)}function ka(o){du(o),o.p.forEach(jM),o.p=null}function du(o){o===Io&&(Io=o.l)}function fp(o){return Io={p:[],l:Io,h:o,m:!0,_:0}}function jM(o){var l=o[zn];l.i===0||l.i===1?l.j():l.O=!0}function fu(o,l){l._=l.p.length;var d=l.p[0],y=o!==void 0&&o!==d;return l.h.g||Oi("ES5").S(l,o,y),y?(d[zn].P&&(ka(l),ri(4)),Br(o)&&(o=za(l,o),l.l||Ha(l,o)),l.u&&Oi("Patches").M(d[zn],o,l.u,l.s)):o=za(l,d,[]),ka(l),l.u&&l.v(l.u,l.s),o!==yp?o:void 0}function za(o,l,d){if(uu(l))return l;var y=l[zn];if(!y)return Co(l,function(C,k){return pp(o,y,l,C,k,d)},!0),l;if(y.A!==o)return l;if(!y.P)return Ha(o,y.t,!0),y.t;if(!y.I){y.I=!0,y.A._--;var T=y.i===4||y.i===5?y.o=cu(y.k):y.o;Co(y.i===3?new Set(T):T,function(C,k){return pp(o,y,T,C,k,d)}),Ha(o,T,!1),d&&o.u&&Oi("Patches").R(y,d,o.u,o.s)}return y.o}function pp(o,l,d,y,T,C){if(Fr(T)){var k=za(o,T,C&&l&&l.i!==3&&!su(l.D,y)?C.concat(y):void 0);if(hp(d,y,k),!Fr(k))return;o.m=!1}if(Br(T)&&!uu(T)){if(!o.h.F&&o._<1)return;za(o,T),l&&l.A.l||Ha(o,T)}}function Ha(o,l,d){d===void 0&&(d=!1),o.h.F&&o.m&&lu(l,d)}function pu(o,l){var d=o[zn];return(d?kr(d):o)[l]}function mp(o,l){if(l in o)for(var d=Object.getPrototypeOf(o);d;){var y=Object.getOwnPropertyDescriptor(d,l);if(y)return y;d=Object.getPrototypeOf(d)}}function mu(o){o.P||(o.P=!0,o.l&&mu(o.l))}function gu(o){o.o||(o.o=cu(o.t))}function _u(o,l,d){var y=ou(l)?Oi("MapSet").N(l,d):au(l)?Oi("MapSet").T(l,d):o.g?(function(T,C){var k=Array.isArray(T),Y={i:k?1:0,A:C?C.A:dp(),P:!1,I:!1,D:{},l:C,t:T,k:null,o:null,j:null,C:!1},K=Y,oe=Va;k&&(K=[Y],oe=Ga);var ve=Proxy.revocable(K,oe),xe=ve.revoke,Ae=ve.proxy;return Y.k=Ae,Y.j=xe,Ae})(l,d):Oi("ES5").J(l,d);return(d?d.A:dp()).p.push(y),y}function XM(o){return Fr(o)||ri(22,o),(function l(d){if(!Br(d))return d;var y,T=d[zn],C=Ts(d);if(T){if(!T.P&&(T.i<4||!Oi("ES5").K(T)))return T.t;T.I=!0,y=gp(d,C),T.I=!1}else y=gp(d,C);return Co(y,function(k,Y){T&&VM(T.t,k)===Y||hp(y,k,l(Y))}),C===3?new Set(y):y})(o)}function gp(o,l){switch(l){case 2:return new Map(o);case 3:return Array.from(o)}return cu(o)}var _p,Io,vu=typeof Symbol<"u"&&typeof Symbol("x")=="symbol",qM=typeof Map<"u",YM=typeof Set<"u",vp=typeof Proxy<"u"&&Proxy.revocable!==void 0&&typeof Reflect<"u",yp=vu?Symbol.for("immer-nothing"):((_p={})["immer-nothing"]=!0,_p),xp=vu?Symbol.for("immer-draftable"):"__$immer_draftable",zn=vu?Symbol.for("immer-state"):"__$immer_state",KM=""+Object.prototype.constructor,yu=typeof Reflect<"u"&&Reflect.ownKeys?Reflect.ownKeys:Object.getOwnPropertySymbols!==void 0?function(o){return Object.getOwnPropertyNames(o).concat(Object.getOwnPropertySymbols(o))}:Object.getOwnPropertyNames,ZM=Object.getOwnPropertyDescriptors||function(o){var l={};return yu(o).forEach(function(d){l[d]=Object.getOwnPropertyDescriptor(o,d)}),l},$M={},Va={get:function(o,l){if(l===zn)return o;var d=kr(o);if(!su(d,l))return(function(T,C,k){var Y,K=mp(C,k);return K?"value"in K?K.value:(Y=K.get)===null||Y===void 0?void 0:Y.call(T.k):void 0})(o,d,l);var y=d[l];return o.I||!Br(y)?y:y===pu(o.t,l)?(gu(o),o.o[l]=_u(o.A.h,y,o)):y},has:function(o,l){return l in kr(o)},ownKeys:function(o){return Reflect.ownKeys(kr(o))},set:function(o,l,d){var y=mp(kr(o),l);if(y!=null&&y.set)return y.set.call(o.k,d),!0;if(!o.P){var T=pu(kr(o),l),C=T==null?void 0:T[zn];if(C&&C.t===d)return o.o[l]=d,o.D[l]=!1,!0;if(GM(d,T)&&(d!==void 0||su(o.t,l)))return!0;gu(o),mu(o)}return o.o[l]===d&&typeof d!="number"&&(d!==void 0||l in o.o)||(o.o[l]=d,o.D[l]=!0,!0)},deleteProperty:function(o,l){return pu(o.t,l)!==void 0||l in o.t?(o.D[l]=!1,gu(o),mu(o)):delete o.D[l],o.o&&delete o.o[l],!0},getOwnPropertyDescriptor:function(o,l){var d=kr(o),y=Reflect.getOwnPropertyDescriptor(d,l);return y&&{writable:!0,configurable:o.i!==1||l!=="length",enumerable:y.enumerable,value:d[l]}},defineProperty:function(){ri(11)},getPrototypeOf:function(o){return Object.getPrototypeOf(o.t)},setPrototypeOf:function(){ri(12)}},Ga={};Co(Va,function(o,l){Ga[o]=function(){return arguments[0]=arguments[0][0],l.apply(this,arguments)}}),Ga.deleteProperty=function(o,l){return Va.deleteProperty.call(this,o[0],l)},Ga.set=function(o,l,d){return Va.set.call(this,o[0],l,d,o[0])};var JM=(function(){function o(d){var y=this;this.g=vp,this.F=!0,this.produce=function(T,C,k){if(typeof T=="function"&&typeof C!="function"){var Y=C;C=T;var K=y;return function(je){var Be=this;je===void 0&&(je=Y);for(var ut=arguments.length,gt=Array(ut>1?ut-1:0),lt=1;lt<ut;lt++)gt[lt-1]=arguments[lt];return K.produce(je,function(wt){var An;return(An=C).call.apply(An,[Be,wt].concat(gt))})}}var oe;if(typeof C!="function"&&ri(6),k!==void 0&&typeof k!="function"&&ri(7),Br(T)){var ve=fp(y),xe=_u(y,T,void 0),Ae=!0;try{oe=C(xe),Ae=!1}finally{Ae?ka(ve):du(ve)}return typeof Promise<"u"&&oe instanceof Promise?oe.then(function(je){return hu(ve,k),fu(je,ve)},function(je){throw ka(ve),je}):(hu(ve,k),fu(oe,ve))}if(!T||typeof T!="object")return(oe=C(T))===yp?void 0:(oe===void 0&&(oe=T),y.F&&lu(oe,!0),oe);ri(21,T)},this.produceWithPatches=function(T,C){return typeof T=="function"?function(K){for(var oe=arguments.length,ve=Array(oe>1?oe-1:0),xe=1;xe<oe;xe++)ve[xe-1]=arguments[xe];return y.produceWithPatches(K,function(Ae){return T.apply(void 0,[Ae].concat(ve))})}:[y.produce(T,C,function(K,oe){k=K,Y=oe}),k,Y];var k,Y},typeof(d==null?void 0:d.useProxies)=="boolean"&&this.setUseProxies(d.useProxies),typeof(d==null?void 0:d.autoFreeze)=="boolean"&&this.setAutoFreeze(d.autoFreeze)}var l=o.prototype;return l.createDraft=function(d){Br(d)||ri(8),Fr(d)&&(d=XM(d));var y=fp(this),T=_u(this,d,void 0);return T[zn].C=!0,du(y),T},l.finishDraft=function(d,y){var T=d&&d[zn],C=T.A;return hu(C,y),fu(void 0,C)},l.setAutoFreeze=function(d){this.F=d},l.setUseProxies=function(d){d&&!vp&&ri(20),this.g=d},l.applyPatches=function(d,y){var T;for(T=y.length-1;T>=0;T--){var C=y[T];if(C.path.length===0&&C.op==="replace"){d=C.value;break}}var k=Oi("Patches").$;return Fr(d)?k(d,y):this.produce(d,function(Y){return k(Y,y.slice(T+1))})},o})(),Zn=new JM;Zn.produce,Zn.produceWithPatches.bind(Zn),Zn.setAutoFreeze.bind(Zn),Zn.setUseProxies.bind(Zn),Zn.applyPatches.bind(Zn),Zn.createDraft.bind(Zn),Zn.finishDraft.bind(Zn);var QM={currentProjectStateDefinitionVersion:"0.4.0"},xu=QM;async function eT(o,l,d){await zM(0),o.transaction(({drafts:y})=>{var T;const C=l.address.projectId;y.ephemeral.coreByProject[C]={lastExportedObject:null,loadingState:{type:"loading"}},y.ahistoric.coreByProject[C]={ahistoricStuff:""};function k(){y.ephemeral.coreByProject[C].loadingState={type:"loaded"},y.historic.coreByProject[C]={sheetsById:{},definitionVersion:xu.currentProjectStateDefinitionVersion,revisionHistory:[]}}function Y(xe){y.ephemeral.coreByProject[C].loadingState={type:"loaded"},y.historic.coreByProject[C]=xe}function K(){y.ephemeral.coreByProject[C].loadingState={type:"loaded"}}function oe(xe){y.ephemeral.coreByProject[C].loadingState={type:"browserStateIsNotBasedOnDiskState",onDiskState:xe}}const ve=(T=HM(y.historic))==null?void 0:T.coreByProject[l.address.projectId];ve?d&&ve.revisionHistory.indexOf(d.revisionHistory[0])==-1?oe(d):K():d?Y(d):k()})}function bp(){}function Sp(o){var l,d;const y=(l=o==null?void 0:o.logging)!=null&&l.internal?(d=o.logging.min)!=null?d:256:1/0,T=y<=128,C=y<=512,k=Wf(void 0,{_debug:T?console.debug.bind(console,"_coreLogger(TheatreInternalLogger) debug"):bp,_error:C?console.error.bind(console,"_coreLogger(TheatreInternalLogger) error"):bp});if(o){const{logger:Y,logging:K}=o;Y&&k.configureLogger(Y),K?k.configureLogging(K):k.configureLogging({dev:!1})}return k.getLogger().named("Theatre")}var tT=class{constructor(o,l={},d){this.config=l,this.publicApi=d,b(this,"pointers"),b(this,"_pointerProxies"),b(this,"address"),b(this,"_studioReadyDeferred"),b(this,"_assetStorageReadyDeferred"),b(this,"_readyPromise"),b(this,"_sheetTemplates",new up.Atom({})),b(this,"sheetTemplatesP",this._sheetTemplates.pointer),b(this,"_studio"),b(this,"assetStorage"),b(this,"type","Theatre_Project"),b(this,"_logger");var y;this._logger=Sp({logging:{dev:!0}}).named("Project",o),this._logger.traceDev("creating project"),this.address={projectId:o};const T=new up.Atom({ahistoric:{ahistoricStuff:""},historic:(y=l.state)!=null?y:{sheetsById:{},definitionVersion:xu.currentProjectStateDefinitionVersion,revisionHistory:[]},ephemeral:{loadingState:{type:"loaded"},lastExportedObject:null}});this._assetStorageReadyDeferred=sr(),this.assetStorage={getAssetUrl:C=>{var k;return"".concat((k=l.assets)==null?void 0:k.baseUrl,"/").concat(C)},createAsset:()=>{throw new Error("Please wait for Project.ready to use assets.")}},this._pointerProxies={historic:new ru.PointerProxy(T.pointer.historic),ahistoric:new ru.PointerProxy(T.pointer.ahistoric),ephemeral:new ru.PointerProxy(T.pointer.ephemeral)},this.pointers={historic:this._pointerProxies.historic.pointer,ahistoric:this._pointerProxies.ahistoric.pointer,ephemeral:this._pointerProxies.ephemeral.pointer},ae.add(o,this),this._studioReadyDeferred=sr(),this._readyPromise=Promise.all([this._studioReadyDeferred.promise,this._assetStorageReadyDeferred.promise]).then(()=>{}),l.state?setTimeout(()=>{this._studio||(this._studioReadyDeferred.resolve(void 0),this._assetStorageReadyDeferred.resolve(void 0),this._logger._trace("ready deferred resolved with no state"))},0):typeof window>"u"?console.error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. ')+"You can safely ignore this message if you're developing a Next.js/Remix project in development mode. But if you are shipping to your end-users, then you need to set config.state, otherwise your project's state will be empty and nothing will animate. Learn more at https://www.theatrejs.com/docs/latest/manual/projects#state"):setTimeout(()=>{if(!this._studio)throw new Error('Argument config.state in Theatre.getProject("'.concat(o,'", config) is empty. This is fine ')+"while you are using @theatre/core along with @theatre/studio. But since @theatre/studio "+'is not loaded, the state of project "'.concat(o,`" will be empty.

`)+`To fix this, you need to add @theatre/studio into the bundle and export the project's state. Learn how to do that at https://www.theatrejs.com/docs/latest/manual/projects#state
`)},1e3)}attachToStudio(o){if(this._studio){if(this._studio!==o)throw new Error("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));console.warn("Project ".concat(this.address.projectId," is already attached to studio ").concat(this._studio.address.studioId));return}this._studio=o,o.initialized.then(async()=>{var l;await eT(o,this,this.config.state),this._pointerProxies.historic.setPointer(o.atomP.historic.coreByProject[this.address.projectId]),this._pointerProxies.ahistoric.setPointer(o.atomP.ahistoric.coreByProject[this.address.projectId]),this._pointerProxies.ephemeral.setPointer(o.atomP.ephemeral.coreByProject[this.address.projectId]),await o.createAssetStorage(this,(l=this.config.assets)==null?void 0:l.baseUrl).then(d=>{this.assetStorage=d,this._assetStorageReadyDeferred.resolve(void 0)}),this._studioReadyDeferred.resolve(void 0)}).catch(l=>{throw console.error(l),l})}get isAttachedToStudio(){return!!this._studio}get ready(){return this._readyPromise}isReady(){return this._studioReadyDeferred.status==="resolved"&&this._assetStorageReadyDeferred.status==="resolved"}getOrCreateSheet(o,l="default"){let d=this._sheetTemplates.get()[o];return d||(d=new BM(this,o),this._sheetTemplates.reduce(y=>x(g({},y),{[o]:d}))),d.getInstance(l)}},nT=class{get type(){return"Theatre_Project_PublicAPI"}constructor(o,l={}){fe(this,new tT(o,l,this))}get ready(){return $(this).ready}get isReady(){return $(this).isReady()}get address(){return g({},$(this).address)}getAssetUrl(o){if(!this.isReady){console.error("Calling `project.getAssetUrl()` before `project.ready` is resolved, will always return `undefined`. Either use `project.ready.then(() => project.getAssetUrl())` or `await project.ready` before calling `project.getAssetUrl()`.");return}return o.id?$(this).assetStorage.getAssetUrl(o.id):void 0}sheet(o,l="default"){const d=Ba(o);return $(this).getOrCreateSheet(d,l).publicApi}};A(z());var Mp=ln(),bu=ln();function Tp(o,l={}){const d=ae.get(o);if(d)return d.publicApi;const T=Sp().named("Project",o);return l.state?(rT(o,l.state),T._debug("deep validated config.state on disk")):T._debug("no config.state"),new nT(o,l)}var iT=(o,l)=>{if(Array.isArray(l)||l==null||l.definitionVersion!==xu.currentProjectStateDefinitionVersion)throw new wo("Error validating conf.state in Theatre.getProject(".concat(JSON.stringify(o),", conf). The state seems to be formatted in a way that is unreadable to Theatre.js. Read more at https://www.theatrejs.com/docs/latest/manual/projects#state"))},rT=(o,l)=>{iT(o,l)};function Su(o,l,d){const y=d?$(d).ticker:tp();if((0,Mp.isPointer)(o))return(0,bu.pointerToPrism)(o).onChange(y,l,!0);if((0,bu.isPrism)(o))return o.onChange(y,l,!0);throw new Error("Called onChange(p) where p is neither a pointer nor a prism.")}function Ep(o){if((0,Mp.isPointer)(o))return(0,bu.pointerToPrism)(o).getValue();throw new Error("Called val(p) where p is not a pointer.")}var sT=class{constructor(){b(this,"_studio")}get type(){return"Theatre_CoreBundle"}get version(){return"0.7.2"}getBitsForStudio(o,l){if(this._studio)throw new Error("@theatre/core is already attached to @theatre/studio");this._studio=o;const d={projectsP:ae.atom.pointer.projects,privateAPI:$,coreExports:w,getCoreRafDriver:ep};l(d)}};oT();function oT(){if(typeof window>"u")return;const o=window[Ql];if(typeof o<"u")throw typeof o=="object"&&o&&typeof o.version=="string"?new Error(`It seems that the module '@theatre/core' is loaded more than once. This could have two possible causes:
1. You might have two separate versions of Theatre.js in node_modules.
2. Or this might be a bundling misconfiguration, in case you're using a bundler like Webpack/ESBuild/Rollup.

Note that it **is okay** to import '@theatre/core' multiple times. But those imports should point to the same module.`):new Error("The variable window.".concat(Ql," seems to be already set by a module other than @theatre/core."));const l=new sT;window[Ql]=l;const d=window[eM];d&&d!==null&&d.type==="Theatre_StudioBundle"&&d.registerCoreBundle(l)}/*! Bundled license information:

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
		*/})(Yo,Yo.exports)),Yo.exports}var tn=UC();let ch=null,sd=null;const n_=new Map;function FC(){return ch=tn.getProject("HumanBody Theatre"),sd=ch.sheet("Main"),{project:ch,sheet:sd}}function Ld(){return sd}function BC(r,e){const t=r.object("Camera",{position:tn.types.compound({x:tn.types.number(e.position.x,{range:[-50,50]}),y:tn.types.number(e.position.y,{range:[-10,20]}),z:tn.types.number(e.position.z,{range:[-50,50]})}),fov:tn.types.number(e.fov,{range:[10,120]})});return t.onValuesChange(n=>{e.position.set(n.position.x,n.position.y,n.position.z),e.fov=n.fov,e.updateProjectionMatrix()}),n_.set("Camera",t),t}function Sc(r,e,t){const n={position:tn.types.compound({x:tn.types.number(t.position.x,{range:[-20,20]}),y:tn.types.number(t.position.y,{range:[0,20]}),z:tn.types.number(t.position.z,{range:[-20,20]})}),intensity:tn.types.number(t.intensity,{range:[0,100]}),color:tn.types.rgba({r:t.color.r,g:t.color.g,b:t.color.b,a:1})},i=r.object(e,n);return i.onValuesChange(s=>{t.position.set(s.position.x,s.position.y,s.position.z),t.intensity=s.intensity,t.color.setRGB(s.color.r,s.color.g,s.color.b)}),n_.set(e,i),i}function Dd(r,e,t){const n=r.object(e,{position:tn.types.compound({x:tn.types.number(t.position.x,{range:[-20,20]}),y:tn.types.number(t.position.y,{range:[-5,10]}),z:tn.types.number(t.position.z,{range:[-20,20]})}),rotation:tn.types.compound({x:tn.types.number(0,{range:[-180,180]}),y:tn.types.number(0,{range:[-180,180]}),z:tn.types.number(0,{range:[-180,180]})}),scale:tn.types.number(1,{range:[.01,10]})});return n.onValuesChange(i=>{t.position.set(i.position.x,i.position.y,i.position.z),t.rotation.set(i.rotation.x*Math.PI/180,i.rotation.y*Math.PI/180,i.rotation.z*Math.PI/180),t.scale.setScalar(i.scale)}),n}function rg(r,e){if(e===zT)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),r;if(e===Qh||e===Tg){let t=r.getIndex();if(t===null){const a=[],c=r.getAttribute("position");if(c!==void 0){for(let u=0;u<c.count;u++)a.push(u);r.setIndex(a),t=r.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),r}const n=t.count-2,i=[];if(e===Qh)for(let a=1;a<=n;a++)i.push(t.getX(0)),i.push(t.getX(a)),i.push(t.getX(a+1));else for(let a=0;a<n;a++)a%2===0?(i.push(t.getX(a)),i.push(t.getX(a+1)),i.push(t.getX(a+2))):(i.push(t.getX(a+2)),i.push(t.getX(a+1)),i.push(t.getX(a)));i.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const s=r.clone();return s.setIndex(i),s.clearGroups(),s}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),r}class kC extends ls{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new WC(t)}),this.register(function(t){return new jC(t)}),this.register(function(t){return new eI(t)}),this.register(function(t){return new tI(t)}),this.register(function(t){return new nI(t)}),this.register(function(t){return new qC(t)}),this.register(function(t){return new YC(t)}),this.register(function(t){return new KC(t)}),this.register(function(t){return new ZC(t)}),this.register(function(t){return new GC(t)}),this.register(function(t){return new $C(t)}),this.register(function(t){return new XC(t)}),this.register(function(t){return new QC(t)}),this.register(function(t){return new JC(t)}),this.register(function(t){return new HC(t)}),this.register(function(t){return new iI(t)}),this.register(function(t){return new rI(t)})}load(e,t,n,i){const s=this;let a;if(this.resourcePath!=="")a=this.resourcePath;else if(this.path!==""){const h=$o.extractUrlBase(e);a=$o.resolveURL(h,this.path)}else a=$o.extractUrlBase(e);this.manager.itemStart(e);const c=function(h){i?i(h):console.error(h),s.manager.itemError(e),s.manager.itemEnd(e)},u=new wd(this.manager);u.setPath(this.path),u.setResponseType("arraybuffer"),u.setRequestHeader(this.requestHeader),u.setWithCredentials(this.withCredentials),u.load(e,function(h){try{s.parse(h,a,function(f){t(f),s.manager.itemEnd(e)},c)}catch(f){c(f)}},n,c)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,i){let s;const a={},c={},u=new TextDecoder;if(typeof e=="string")s=JSON.parse(e);else if(e instanceof ArrayBuffer)if(u.decode(new Uint8Array(e,0,4))===i_){try{a[vt.KHR_BINARY_GLTF]=new sI(e)}catch(p){i&&i(p);return}s=JSON.parse(a[vt.KHR_BINARY_GLTF].content)}else s=JSON.parse(u.decode(e));else s=e;if(s.asset===void 0||s.asset.version[0]<2){i&&i(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const h=new vI(s,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});h.fileLoader.setRequestHeader(this.requestHeader);for(let f=0;f<this.pluginCallbacks.length;f++){const p=this.pluginCallbacks[f](h);p.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),c[p.name]=p,a[p.name]=!0}if(s.extensionsUsed)for(let f=0;f<s.extensionsUsed.length;++f){const p=s.extensionsUsed[f],m=s.extensionsRequired||[];switch(p){case vt.KHR_MATERIALS_UNLIT:a[p]=new VC;break;case vt.KHR_DRACO_MESH_COMPRESSION:a[p]=new oI(s,this.dracoLoader);break;case vt.KHR_TEXTURE_TRANSFORM:a[p]=new aI;break;case vt.KHR_MESH_QUANTIZATION:a[p]=new cI;break;default:m.indexOf(p)>=0&&c[p]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+p+'".')}}h.setExtensions(a),h.setPlugins(c),h.parse(n,i)}parseAsync(e,t){const n=this;return new Promise(function(i,s){n.parse(e,t,i,s)})}}function zC(){let r={};return{get:function(e){return r[e]},add:function(e,t){r[e]=t},remove:function(e){delete r[e]},removeAll:function(){r={}}}}const vt={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class HC{constructor(e){this.parser=e,this.name=vt.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,i=t.length;n<i;n++){const s=t[n];s.extensions&&s.extensions[this.name]&&s.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,s.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let i=t.cache.get(n);if(i)return i;const s=t.json,u=((s.extensions&&s.extensions[this.name]||{}).lights||[])[e];let h;const f=new qe(16777215);u.color!==void 0&&f.setRGB(u.color[0],u.color[1],u.color[2],Fn);const p=u.range!==void 0?u.range:0;switch(u.type){case"directional":h=new Cc(f),h.target.position.set(0,0,-1),h.add(h.target);break;case"point":h=new Zg(f),h.distance=p;break;case"spot":h=new qR(f),h.distance=p,u.spot=u.spot||{},u.spot.innerConeAngle=u.spot.innerConeAngle!==void 0?u.spot.innerConeAngle:0,u.spot.outerConeAngle=u.spot.outerConeAngle!==void 0?u.spot.outerConeAngle:Math.PI/4,h.angle=u.spot.outerConeAngle,h.penumbra=1-u.spot.innerConeAngle/u.spot.outerConeAngle,h.target.position.set(0,0,-1),h.add(h.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+u.type)}return h.position.set(0,0,0),h.decay=2,ji(h,u),u.intensity!==void 0&&(h.intensity=u.intensity),h.name=t.createUniqueName(u.name||"light_"+e),i=Promise.resolve(h),t.cache.add(n,i),i}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,s=n.json.nodes[e],c=(s.extensions&&s.extensions[this.name]||{}).light;return c===void 0?null:this._loadLight(c).then(function(u){return n._getNodeRef(t.cache,c,u)})}}class VC{constructor(){this.name=vt.KHR_MATERIALS_UNLIT}getMaterialType(){return ci}extendParams(e,t,n){const i=[];e.color=new qe(1,1,1),e.opacity=1;const s=t.pbrMetallicRoughness;if(s){if(Array.isArray(s.baseColorFactor)){const a=s.baseColorFactor;e.color.setRGB(a[0],a[1],a[2],Fn),e.opacity=a[3]}s.baseColorTexture!==void 0&&i.push(n.assignTexture(e,"map",s.baseColorTexture,_n))}return Promise.all(i)}}class GC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name].emissiveStrength;return s!==void 0&&(t.emissiveIntensity=s),Promise.resolve()}}class WC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];if(a.clearcoatFactor!==void 0&&(t.clearcoat=a.clearcoatFactor),a.clearcoatTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatMap",a.clearcoatTexture)),a.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=a.clearcoatRoughnessFactor),a.clearcoatRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"clearcoatRoughnessMap",a.clearcoatRoughnessTexture)),a.clearcoatNormalTexture!==void 0&&(s.push(n.assignTexture(t,"clearcoatNormalMap",a.clearcoatNormalTexture)),a.clearcoatNormalTexture.scale!==void 0)){const c=a.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new Qe(c,c)}return Promise.all(s)}}class jC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.dispersion=s.dispersion!==void 0?s.dispersion:0,Promise.resolve()}}class XC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.iridescenceFactor!==void 0&&(t.iridescence=a.iridescenceFactor),a.iridescenceTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceMap",a.iridescenceTexture)),a.iridescenceIor!==void 0&&(t.iridescenceIOR=a.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),a.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=a.iridescenceThicknessMinimum),a.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=a.iridescenceThicknessMaximum),a.iridescenceThicknessTexture!==void 0&&s.push(n.assignTexture(t,"iridescenceThicknessMap",a.iridescenceThicknessTexture)),Promise.all(s)}}class qC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[];t.sheenColor=new qe(0,0,0),t.sheenRoughness=0,t.sheen=1;const a=i.extensions[this.name];if(a.sheenColorFactor!==void 0){const c=a.sheenColorFactor;t.sheenColor.setRGB(c[0],c[1],c[2],Fn)}return a.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=a.sheenRoughnessFactor),a.sheenColorTexture!==void 0&&s.push(n.assignTexture(t,"sheenColorMap",a.sheenColorTexture,_n)),a.sheenRoughnessTexture!==void 0&&s.push(n.assignTexture(t,"sheenRoughnessMap",a.sheenRoughnessTexture)),Promise.all(s)}}class YC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.transmissionFactor!==void 0&&(t.transmission=a.transmissionFactor),a.transmissionTexture!==void 0&&s.push(n.assignTexture(t,"transmissionMap",a.transmissionTexture)),Promise.all(s)}}class KC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.thickness=a.thicknessFactor!==void 0?a.thicknessFactor:0,a.thicknessTexture!==void 0&&s.push(n.assignTexture(t,"thicknessMap",a.thicknessTexture)),t.attenuationDistance=a.attenuationDistance||1/0;const c=a.attenuationColor||[1,1,1];return t.attenuationColor=new qe().setRGB(c[0],c[1],c[2],Fn),Promise.all(s)}}class ZC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const i=this.parser.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=i.extensions[this.name];return t.ior=s.ior!==void 0?s.ior:1.5,Promise.resolve()}}class $C{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];t.specularIntensity=a.specularFactor!==void 0?a.specularFactor:1,a.specularTexture!==void 0&&s.push(n.assignTexture(t,"specularIntensityMap",a.specularTexture));const c=a.specularColorFactor||[1,1,1];return t.specularColor=new qe().setRGB(c[0],c[1],c[2],Fn),a.specularColorTexture!==void 0&&s.push(n.assignTexture(t,"specularColorMap",a.specularColorTexture,_n)),Promise.all(s)}}class JC{constructor(e){this.parser=e,this.name=vt.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return t.bumpScale=a.bumpFactor!==void 0?a.bumpFactor:1,a.bumpTexture!==void 0&&s.push(n.assignTexture(t,"bumpMap",a.bumpTexture)),Promise.all(s)}}class QC{constructor(e){this.parser=e,this.name=vt.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Ai}extendMaterialParams(e,t){const n=this.parser,i=n.json.materials[e];if(!i.extensions||!i.extensions[this.name])return Promise.resolve();const s=[],a=i.extensions[this.name];return a.anisotropyStrength!==void 0&&(t.anisotropy=a.anisotropyStrength),a.anisotropyRotation!==void 0&&(t.anisotropyRotation=a.anisotropyRotation),a.anisotropyTexture!==void 0&&s.push(n.assignTexture(t,"anisotropyMap",a.anisotropyTexture)),Promise.all(s)}}class eI{constructor(e){this.parser=e,this.name=vt.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,i=n.textures[e];if(!i.extensions||!i.extensions[this.name])return null;const s=i.extensions[this.name],a=t.options.ktx2Loader;if(!a){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,s.source,a)}}class tI{constructor(e){this.parser=e,this.name=vt.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class nI{constructor(e){this.parser=e,this.name=vt.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,i=n.json,s=i.textures[e];if(!s.extensions||!s.extensions[t])return null;const a=s.extensions[t],c=i.images[a.source];let u=n.textureLoader;if(c.uri){const h=n.options.manager.getHandler(c.uri);h!==null&&(u=h)}return this.detectSupport().then(function(h){if(h)return n.loadTextureImage(e,a.source,u);if(i.extensionsRequired&&i.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class iI{constructor(e){this.name=vt.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const i=n.extensions[this.name],s=this.parser.getDependency("buffer",i.buffer),a=this.parser.options.meshoptDecoder;if(!a||!a.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return s.then(function(c){const u=i.byteOffset||0,h=i.byteLength||0,f=i.count,p=i.byteStride,m=new Uint8Array(c,u,h);return a.decodeGltfBufferAsync?a.decodeGltfBufferAsync(f,p,m,i.mode,i.filter).then(function(g){return g.buffer}):a.ready.then(function(){const g=new ArrayBuffer(f*p);return a.decodeGltfBuffer(new Uint8Array(g),f,p,m,i.mode,i.filter),g})})}else return null}}class rI{constructor(e){this.name=vt.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const i=t.meshes[n.mesh];for(const h of i.primitives)if(h.mode!==oi.TRIANGLES&&h.mode!==oi.TRIANGLE_STRIP&&h.mode!==oi.TRIANGLE_FAN&&h.mode!==void 0)return null;const a=n.extensions[this.name].attributes,c=[],u={};for(const h in a)c.push(this.parser.getDependency("accessor",a[h]).then(f=>(u[h]=f,u[h])));return c.length<1?null:(c.push(this.parser.createNodeMesh(e)),Promise.all(c).then(h=>{const f=h.pop(),p=f.isGroup?f.children:[f],m=h[0].count,g=[];for(const x of p){const M=new rt,v=new F,_=new Yt,A=new F(1,1,1),P=new IR(x.geometry,x.material,m);for(let b=0;b<m;b++)u.TRANSLATION&&v.fromBufferAttribute(u.TRANSLATION,b),u.ROTATION&&_.fromBufferAttribute(u.ROTATION,b),u.SCALE&&A.fromBufferAttribute(u.SCALE,b),P.setMatrixAt(b,M.compose(v,_,A));for(const b in u)if(b==="_COLOR_0"){const B=u[b];P.instanceColor=new nd(B.array,B.itemSize,B.normalized)}else b!=="TRANSLATION"&&b!=="ROTATION"&&b!=="SCALE"&&x.geometry.setAttribute(b,u[b]);Xt.prototype.copy.call(P,x),this.parser.assignFinalMaterial(P),g.push(P)}return f.isGroup?(f.clear(),f.add(...g),f):g[0]}))}}const i_="glTF",Vo=12,sg={JSON:1313821514,BIN:5130562};class sI{constructor(e){this.name=vt.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,Vo),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==i_)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const i=this.header.length-Vo,s=new DataView(e,Vo);let a=0;for(;a<i;){const c=s.getUint32(a,!0);a+=4;const u=s.getUint32(a,!0);if(a+=4,u===sg.JSON){const h=new Uint8Array(e,Vo+a,c);this.content=n.decode(h)}else if(u===sg.BIN){const h=Vo+a;this.body=e.slice(h,h+c)}a+=c}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class oI{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=vt.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,i=this.dracoLoader,s=e.extensions[this.name].bufferView,a=e.extensions[this.name].attributes,c={},u={},h={};for(const f in a){const p=od[f]||f.toLowerCase();c[p]=a[f]}for(const f in e.attributes){const p=od[f]||f.toLowerCase();if(a[f]!==void 0){const m=n.accessors[e.attributes[f]],g=Ks[m.componentType];h[p]=g.name,u[p]=m.normalized===!0}}return t.getDependency("bufferView",s).then(function(f){return new Promise(function(p,m){i.decodeDracoFile(f,function(g){for(const x in g.attributes){const M=g.attributes[x],v=u[x];v!==void 0&&(M.normalized=v)}p(g)},c,h,Fn,m)})})}}class aI{constructor(){this.name=vt.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class cI{constructor(){this.name=vt.KHR_MESH_QUANTIZATION}}class r_ extends sa{constructor(e,t,n,i){super(e,t,n,i)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,i=this.valueSize,s=e*i*3+i;for(let a=0;a!==i;a++)t[a]=n[s+a];return t}interpolate_(e,t,n,i){const s=this.resultBuffer,a=this.sampleValues,c=this.valueSize,u=c*2,h=c*3,f=i-t,p=(n-t)/f,m=p*p,g=m*p,x=e*h,M=x-h,v=-2*g+3*m,_=g-m,A=1-v,P=_-m+p;for(let b=0;b!==c;b++){const B=a[M+b+c],U=a[M+b+u]*f,O=a[x+b+c],z=a[x+b]*f;s[b]=A*B+P*U+v*O+_*z}return s}}const lI=new Yt;class uI extends r_{interpolate_(e,t,n,i){const s=super.interpolate_(e,t,n,i);return lI.fromArray(s).normalize().toArray(s),s}}const oi={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},Ks={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},og={9728:Un,9729:ti,9984:pg,9985:Mc,9986:Go,9987:Xi},ag={33071:_r,33648:Dc,10497:Qs},lh={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},od={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},pr={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},hI={CUBICSPLINE:void 0,LINEAR:ea,STEP:Qo},uh={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function dI(r){return r.DefaultMaterial===void 0&&(r.DefaultMaterial=new os({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:Zi})),r.DefaultMaterial}function Jr(r,e,t){for(const n in t.extensions)r[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function ji(r,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(r.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function fI(r,e,t){let n=!1,i=!1,s=!1;for(let h=0,f=e.length;h<f;h++){const p=e[h];if(p.POSITION!==void 0&&(n=!0),p.NORMAL!==void 0&&(i=!0),p.COLOR_0!==void 0&&(s=!0),n&&i&&s)break}if(!n&&!i&&!s)return Promise.resolve(r);const a=[],c=[],u=[];for(let h=0,f=e.length;h<f;h++){const p=e[h];if(n){const m=p.POSITION!==void 0?t.getDependency("accessor",p.POSITION):r.attributes.position;a.push(m)}if(i){const m=p.NORMAL!==void 0?t.getDependency("accessor",p.NORMAL):r.attributes.normal;c.push(m)}if(s){const m=p.COLOR_0!==void 0?t.getDependency("accessor",p.COLOR_0):r.attributes.color;u.push(m)}}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u)]).then(function(h){const f=h[0],p=h[1],m=h[2];return n&&(r.morphAttributes.position=f),i&&(r.morphAttributes.normal=p),s&&(r.morphAttributes.color=m),r.morphTargetsRelative=!0,r})}function pI(r,e){if(r.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)r.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(r.morphTargetInfluences.length===t.length){r.morphTargetDictionary={};for(let n=0,i=t.length;n<i;n++)r.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function mI(r){let e;const t=r.extensions&&r.extensions[vt.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+hh(t.attributes):e=r.indices+":"+hh(r.attributes)+":"+r.mode,r.targets!==void 0)for(let n=0,i=r.targets.length;n<i;n++)e+=":"+hh(r.targets[n]);return e}function hh(r){let e="";const t=Object.keys(r).sort();for(let n=0,i=t.length;n<i;n++)e+=t[n]+":"+r[t[n]]+";";return e}function ad(r){switch(r){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function gI(r){return r.search(/\.jpe?g($|\?)/i)>0||r.search(/^data\:image\/jpeg/)===0?"image/jpeg":r.search(/\.webp($|\?)/i)>0||r.search(/^data\:image\/webp/)===0?"image/webp":r.search(/\.ktx2($|\?)/i)>0||r.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const _I=new rt;class vI{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new zC,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,i=-1,s=!1,a=-1;if(typeof navigator<"u"){const c=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(c)===!0;const u=c.match(/Version\/(\d+)/);i=n&&u?parseInt(u[1],10):-1,s=c.indexOf("Firefox")>-1,a=s?c.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&i<17||s&&a<98?this.textureLoader=new jR(this.options.manager):this.textureLoader=new $R(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new wd(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,i=this.json,s=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(a){return a._markDefs&&a._markDefs()}),Promise.all(this._invokeAll(function(a){return a.beforeRoot&&a.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(a){const c={scene:a[0][i.scene||0],scenes:a[0],animations:a[1],cameras:a[2],asset:i.asset,parser:n,userData:{}};return Jr(s,c,i),ji(c,i),Promise.all(n._invokeAll(function(u){return u.afterRoot&&u.afterRoot(c)})).then(function(){for(const u of c.scenes)u.updateMatrixWorld();e(c)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let i=0,s=t.length;i<s;i++){const a=t[i].joints;for(let c=0,u=a.length;c<u;c++)e[a[c]].isBone=!0}for(let i=0,s=e.length;i<s;i++){const a=e[i];a.mesh!==void 0&&(this._addNodeRef(this.meshCache,a.mesh),a.skin!==void 0&&(n[a.mesh].isSkinnedMesh=!0)),a.camera!==void 0&&this._addNodeRef(this.cameraCache,a.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const i=n.clone(),s=(a,c)=>{const u=this.associations.get(a);u!=null&&this.associations.set(c,u);for(const[h,f]of a.children.entries())s(f,c.children[h])};return s(n,i),i.name+="_instance_"+e.uses[t]++,i}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const i=e(t[n]);if(i)return i}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let i=0;i<t.length;i++){const s=e(t[i]);s&&n.push(s)}return n}getDependency(e,t){const n=e+":"+t;let i=this.cache.get(n);if(!i){switch(e){case"scene":i=this.loadScene(t);break;case"node":i=this._invokeOne(function(s){return s.loadNode&&s.loadNode(t)});break;case"mesh":i=this._invokeOne(function(s){return s.loadMesh&&s.loadMesh(t)});break;case"accessor":i=this.loadAccessor(t);break;case"bufferView":i=this._invokeOne(function(s){return s.loadBufferView&&s.loadBufferView(t)});break;case"buffer":i=this.loadBuffer(t);break;case"material":i=this._invokeOne(function(s){return s.loadMaterial&&s.loadMaterial(t)});break;case"texture":i=this._invokeOne(function(s){return s.loadTexture&&s.loadTexture(t)});break;case"skin":i=this.loadSkin(t);break;case"animation":i=this._invokeOne(function(s){return s.loadAnimation&&s.loadAnimation(t)});break;case"camera":i=this.loadCamera(t);break;default:if(i=this._invokeOne(function(s){return s!=this&&s.getDependency&&s.getDependency(e,t)}),!i)throw new Error("Unknown type: "+e);break}this.cache.add(n,i)}return i}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,i=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(i.map(function(s,a){return n.getDependency(e,a)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[vt.KHR_BINARY_GLTF].body);const i=this.options;return new Promise(function(s,a){n.load($o.resolveURL(t.uri,i.path),s,void 0,function(){a(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const i=t.byteLength||0,s=t.byteOffset||0;return n.slice(s,s+i)})}loadAccessor(e){const t=this,n=this.json,i=this.json.accessors[e];if(i.bufferView===void 0&&i.sparse===void 0){const a=lh[i.type],c=Ks[i.componentType],u=i.normalized===!0,h=new c(i.count*a);return Promise.resolve(new nn(h,a,u))}const s=[];return i.bufferView!==void 0?s.push(this.getDependency("bufferView",i.bufferView)):s.push(null),i.sparse!==void 0&&(s.push(this.getDependency("bufferView",i.sparse.indices.bufferView)),s.push(this.getDependency("bufferView",i.sparse.values.bufferView))),Promise.all(s).then(function(a){const c=a[0],u=lh[i.type],h=Ks[i.componentType],f=h.BYTES_PER_ELEMENT,p=f*u,m=i.byteOffset||0,g=i.bufferView!==void 0?n.bufferViews[i.bufferView].byteStride:void 0,x=i.normalized===!0;let M,v;if(g&&g!==p){const _=Math.floor(m/g),A="InterleavedBuffer:"+i.bufferView+":"+i.componentType+":"+_+":"+i.count;let P=t.cache.get(A);P||(M=new h(c,_*g,i.count*g/f),P=new wR(M,g/f),t.cache.add(A,P)),v=new Td(P,u,m%g/f,x)}else c===null?M=new h(i.count*u):M=new h(c,m,i.count*u),v=new nn(M,u,x);if(i.sparse!==void 0){const _=lh.SCALAR,A=Ks[i.sparse.indices.componentType],P=i.sparse.indices.byteOffset||0,b=i.sparse.values.byteOffset||0,B=new A(a[1],P,i.sparse.count*_),U=new h(a[2],b,i.sparse.count*u);c!==null&&(v=new nn(v.array.slice(),v.itemSize,v.normalized)),v.normalized=!1;for(let O=0,z=B.length;O<z;O++){const I=B[O];if(v.setX(I,U[O*u]),u>=2&&v.setY(I,U[O*u+1]),u>=3&&v.setZ(I,U[O*u+2]),u>=4&&v.setW(I,U[O*u+3]),u>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}v.normalized=x}return v})}loadTexture(e){const t=this.json,n=this.options,s=t.textures[e].source,a=t.images[s];let c=this.textureLoader;if(a.uri){const u=n.manager.getHandler(a.uri);u!==null&&(c=u)}return this.loadTextureImage(e,s,c)}loadTextureImage(e,t,n){const i=this,s=this.json,a=s.textures[e],c=s.images[t],u=(c.uri||c.bufferView)+":"+a.sampler;if(this.textureCache[u])return this.textureCache[u];const h=this.loadImageSource(t,n).then(function(f){f.flipY=!1,f.name=a.name||c.name||"",f.name===""&&typeof c.uri=="string"&&c.uri.startsWith("data:image/")===!1&&(f.name=c.uri);const m=(s.samplers||{})[a.sampler]||{};return f.magFilter=og[m.magFilter]||ti,f.minFilter=og[m.minFilter]||Xi,f.wrapS=ag[m.wrapS]||Qs,f.wrapT=ag[m.wrapT]||Qs,f.generateMipmaps=!f.isCompressedTexture&&f.minFilter!==Un&&f.minFilter!==ti,i.associations.set(f,{textures:e}),f}).catch(function(){return null});return this.textureCache[u]=h,h}loadImageSource(e,t){const n=this,i=this.json,s=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(p=>p.clone());const a=i.images[e],c=self.URL||self.webkitURL;let u=a.uri||"",h=!1;if(a.bufferView!==void 0)u=n.getDependency("bufferView",a.bufferView).then(function(p){h=!0;const m=new Blob([p],{type:a.mimeType});return u=c.createObjectURL(m),u});else if(a.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const f=Promise.resolve(u).then(function(p){return new Promise(function(m,g){let x=m;t.isImageBitmapLoader===!0&&(x=function(M){const v=new vn(M);v.needsUpdate=!0,m(v)}),t.load($o.resolveURL(p,s.path),x,void 0,g)})}).then(function(p){return h===!0&&c.revokeObjectURL(u),ji(p,a),p.userData.mimeType=a.mimeType||gI(a.uri),p}).catch(function(p){throw console.error("THREE.GLTFLoader: Couldn't load texture",u),p});return this.sourceCache[e]=f,f}assignTexture(e,t,n,i){const s=this;return this.getDependency("texture",n.index).then(function(a){if(!a)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(a=a.clone(),a.channel=n.texCoord),s.extensions[vt.KHR_TEXTURE_TRANSFORM]){const c=n.extensions!==void 0?n.extensions[vt.KHR_TEXTURE_TRANSFORM]:void 0;if(c){const u=s.associations.get(a);a=s.extensions[vt.KHR_TEXTURE_TRANSFORM].extendTexture(a,c),s.associations.set(a,u)}}return i!==void 0&&(a.colorSpace=i),e[t]=a,a})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const i=t.attributes.tangent===void 0,s=t.attributes.color!==void 0,a=t.attributes.normal===void 0;if(e.isPoints){const c="PointsMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Xg,Ti.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,u.sizeAttenuation=!1,this.cache.add(c,u)),n=u}else if(e.isLine){const c="LineBasicMaterial:"+n.uuid;let u=this.cache.get(c);u||(u=new Gc,Ti.prototype.copy.call(u,n),u.color.copy(n.color),u.map=n.map,this.cache.add(c,u)),n=u}if(i||s||a){let c="ClonedMaterial:"+n.uuid+":";i&&(c+="derivative-tangents:"),s&&(c+="vertex-colors:"),a&&(c+="flat-shading:");let u=this.cache.get(c);u||(u=n.clone(),s&&(u.vertexColors=!0),a&&(u.flatShading=!0),i&&(u.normalScale&&(u.normalScale.y*=-1),u.clearcoatNormalScale&&(u.clearcoatNormalScale.y*=-1)),this.cache.add(c,u),this.associations.set(u,this.associations.get(n))),n=u}e.material=n}getMaterialType(){return os}loadMaterial(e){const t=this,n=this.json,i=this.extensions,s=n.materials[e];let a;const c={},u=s.extensions||{},h=[];if(u[vt.KHR_MATERIALS_UNLIT]){const p=i[vt.KHR_MATERIALS_UNLIT];a=p.getMaterialType(),h.push(p.extendParams(c,s,t))}else{const p=s.pbrMetallicRoughness||{};if(c.color=new qe(1,1,1),c.opacity=1,Array.isArray(p.baseColorFactor)){const m=p.baseColorFactor;c.color.setRGB(m[0],m[1],m[2],Fn),c.opacity=m[3]}p.baseColorTexture!==void 0&&h.push(t.assignTexture(c,"map",p.baseColorTexture,_n)),c.metalness=p.metallicFactor!==void 0?p.metallicFactor:1,c.roughness=p.roughnessFactor!==void 0?p.roughnessFactor:1,p.metallicRoughnessTexture!==void 0&&(h.push(t.assignTexture(c,"metalnessMap",p.metallicRoughnessTexture)),h.push(t.assignTexture(c,"roughnessMap",p.metallicRoughnessTexture))),a=this._invokeOne(function(m){return m.getMaterialType&&m.getMaterialType(e)}),h.push(Promise.all(this._invokeAll(function(m){return m.extendMaterialParams&&m.extendMaterialParams(e,c)})))}s.doubleSided===!0&&(c.side=Gn);const f=s.alphaMode||uh.OPAQUE;if(f===uh.BLEND?(c.transparent=!0,c.depthWrite=!1):(c.transparent=!1,f===uh.MASK&&(c.alphaTest=s.alphaCutoff!==void 0?s.alphaCutoff:.5)),s.normalTexture!==void 0&&a!==ci&&(h.push(t.assignTexture(c,"normalMap",s.normalTexture)),c.normalScale=new Qe(1,1),s.normalTexture.scale!==void 0)){const p=s.normalTexture.scale;c.normalScale.set(p,p)}if(s.occlusionTexture!==void 0&&a!==ci&&(h.push(t.assignTexture(c,"aoMap",s.occlusionTexture)),s.occlusionTexture.strength!==void 0&&(c.aoMapIntensity=s.occlusionTexture.strength)),s.emissiveFactor!==void 0&&a!==ci){const p=s.emissiveFactor;c.emissive=new qe().setRGB(p[0],p[1],p[2],Fn)}return s.emissiveTexture!==void 0&&a!==ci&&h.push(t.assignTexture(c,"emissiveMap",s.emissiveTexture,_n)),Promise.all(h).then(function(){const p=new a(c);return s.name&&(p.name=s.name),ji(p,s),t.associations.set(p,{materials:e}),s.extensions&&Jr(i,p,s),p})}createUniqueName(e){const t=Ct.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,i=this.primitiveCache;function s(c){return n[vt.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(c,t).then(function(u){return cg(u,c,t)})}const a=[];for(let c=0,u=e.length;c<u;c++){const h=e[c],f=mI(h),p=i[f];if(p)a.push(p.promise);else{let m;h.extensions&&h.extensions[vt.KHR_DRACO_MESH_COMPRESSION]?m=s(h):m=cg(new hn,h,t),i[f]={primitive:h,promise:m},a.push(m)}}return Promise.all(a)}loadMesh(e){const t=this,n=this.json,i=this.extensions,s=n.meshes[e],a=s.primitives,c=[];for(let u=0,h=a.length;u<h;u++){const f=a[u].material===void 0?dI(this.cache):this.getDependency("material",a[u].material);c.push(f)}return c.push(t.loadGeometries(a)),Promise.all(c).then(function(u){const h=u.slice(0,u.length-1),f=u[u.length-1],p=[];for(let g=0,x=f.length;g<x;g++){const M=f[g],v=a[g];let _;const A=h[g];if(v.mode===oi.TRIANGLES||v.mode===oi.TRIANGLE_STRIP||v.mode===oi.TRIANGLE_FAN||v.mode===void 0)_=s.isSkinnedMesh===!0?new Gg(M,A):new Te(M,A),_.isSkinnedMesh===!0&&_.normalizeSkinWeights(),v.mode===oi.TRIANGLE_STRIP?_.geometry=rg(_.geometry,Tg):v.mode===oi.TRIANGLE_FAN&&(_.geometry=rg(_.geometry,Qh));else if(v.mode===oi.LINES)_=new jg(M,A);else if(v.mode===oi.LINE_STRIP)_=new fi(M,A);else if(v.mode===oi.LINE_LOOP)_=new LR(M,A);else if(v.mode===oi.POINTS)_=new DR(M,A);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+v.mode);Object.keys(_.geometry.morphAttributes).length>0&&pI(_,s),_.name=t.createUniqueName(s.name||"mesh_"+e),ji(_,s),v.extensions&&Jr(i,_,v),t.assignFinalMaterial(_),p.push(_)}for(let g=0,x=p.length;g<x;g++)t.associations.set(p[g],{meshes:e,primitives:g});if(p.length===1)return s.extensions&&Jr(i,p[0],s),p[0];const m=new Yi;s.extensions&&Jr(i,m,s),t.associations.set(m,{meshes:e});for(let g=0,x=p.length;g<x;g++)m.add(p[g]);return m})}loadCamera(e){let t;const n=this.json.cameras[e],i=n[n.type];if(!i){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new On(wg.radToDeg(i.yfov),i.aspectRatio||1,i.znear||1,i.zfar||2e6):n.type==="orthographic"&&(t=new bd(-i.xmag,i.xmag,i.ymag,-i.ymag,i.znear,i.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),ji(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let i=0,s=t.joints.length;i<s;i++)n.push(this._loadNodeShallow(t.joints[i]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(i){const s=i.pop(),a=i,c=[],u=[];for(let h=0,f=a.length;h<f;h++){const p=a[h];if(p){c.push(p);const m=new rt;s!==null&&m.fromArray(s.array,h*16),u.push(m)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[h])}return new ia(c,u)})}loadAnimation(e){const t=this.json,n=this,i=t.animations[e],s=i.name?i.name:"animation_"+e,a=[],c=[],u=[],h=[],f=[];for(let p=0,m=i.channels.length;p<m;p++){const g=i.channels[p],x=i.samplers[g.sampler],M=g.target,v=M.node,_=i.parameters!==void 0?i.parameters[x.input]:x.input,A=i.parameters!==void 0?i.parameters[x.output]:x.output;M.node!==void 0&&(a.push(this.getDependency("node",v)),c.push(this.getDependency("accessor",_)),u.push(this.getDependency("accessor",A)),h.push(x),f.push(M))}return Promise.all([Promise.all(a),Promise.all(c),Promise.all(u),Promise.all(h),Promise.all(f)]).then(function(p){const m=p[0],g=p[1],x=p[2],M=p[3],v=p[4],_=[];for(let A=0,P=m.length;A<P;A++){const b=m[A],B=g[A],U=x[A],O=M[A],z=v[A];if(b===void 0)continue;b.updateMatrix&&b.updateMatrix();const I=n._createAnimationTracks(b,B,U,O,z);if(I)for(let w=0;w<I.length;w++)_.push(I[w])}return new Bc(s,void 0,_)})}createNodeMesh(e){const t=this.json,n=this,i=t.nodes[e];return i.mesh===void 0?null:n.getDependency("mesh",i.mesh).then(function(s){const a=n._getNodeRef(n.meshCache,i.mesh,s);return i.weights!==void 0&&a.traverse(function(c){if(c.isMesh)for(let u=0,h=i.weights.length;u<h;u++)c.morphTargetInfluences[u]=i.weights[u]}),a})}loadNode(e){const t=this.json,n=this,i=t.nodes[e],s=n._loadNodeShallow(e),a=[],c=i.children||[];for(let h=0,f=c.length;h<f;h++)a.push(n.getDependency("node",c[h]));const u=i.skin===void 0?Promise.resolve(null):n.getDependency("skin",i.skin);return Promise.all([s,Promise.all(a),u]).then(function(h){const f=h[0],p=h[1],m=h[2];m!==null&&f.traverse(function(g){g.isSkinnedMesh&&g.bind(m,_I)});for(let g=0,x=p.length;g<x;g++)f.add(p[g]);return f})}_loadNodeShallow(e){const t=this.json,n=this.extensions,i=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const s=t.nodes[e],a=s.name?i.createUniqueName(s.name):"",c=[],u=i._invokeOne(function(h){return h.createNodeMesh&&h.createNodeMesh(e)});return u&&c.push(u),s.camera!==void 0&&c.push(i.getDependency("camera",s.camera).then(function(h){return i._getNodeRef(i.cameraCache,s.camera,h)})),i._invokeAll(function(h){return h.createNodeAttachment&&h.createNodeAttachment(e)}).forEach(function(h){c.push(h)}),this.nodeCache[e]=Promise.all(c).then(function(h){let f;if(s.isBone===!0?f=new Vc:h.length>1?f=new Yi:h.length===1?f=h[0]:f=new Xt,f!==h[0])for(let p=0,m=h.length;p<m;p++)f.add(h[p]);if(s.name&&(f.userData.name=s.name,f.name=a),ji(f,s),s.extensions&&Jr(n,f,s),s.matrix!==void 0){const p=new rt;p.fromArray(s.matrix),f.applyMatrix4(p)}else s.translation!==void 0&&f.position.fromArray(s.translation),s.rotation!==void 0&&f.quaternion.fromArray(s.rotation),s.scale!==void 0&&f.scale.fromArray(s.scale);return i.associations.has(f)||i.associations.set(f,{}),i.associations.get(f).nodes=e,f}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],i=this,s=new Yi;n.name&&(s.name=i.createUniqueName(n.name)),ji(s,n),n.extensions&&Jr(t,s,n);const a=n.nodes||[],c=[];for(let u=0,h=a.length;u<h;u++)c.push(i.getDependency("node",a[u]));return Promise.all(c).then(function(u){for(let f=0,p=u.length;f<p;f++)s.add(u[f]);const h=f=>{const p=new Map;for(const[m,g]of i.associations)(m instanceof Ti||m instanceof vn)&&p.set(m,g);return f.traverse(m=>{const g=i.associations.get(m);g!=null&&p.set(m,g)}),p};return i.associations=h(s),s})}_createAnimationTracks(e,t,n,i,s){const a=[],c=e.name?e.name:e.uuid,u=[];pr[s.path]===pr.weights?e.traverse(function(m){m.morphTargetInfluences&&u.push(m.name?m.name:m.uuid)}):u.push(c);let h;switch(pr[s.path]){case pr.weights:h=ro;break;case pr.rotation:h=as;break;case pr.position:case pr.scale:h=cs;break;default:switch(n.itemSize){case 1:h=ro;break;case 2:case 3:default:h=cs;break}break}const f=i.interpolation!==void 0?hI[i.interpolation]:ea,p=this._getArrayFromAccessor(n);for(let m=0,g=u.length;m<g;m++){const x=new h(u[m]+"."+pr[s.path],t.array,p,f);i.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(x),a.push(x)}return a}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=ad(t.constructor),i=new Float32Array(t.length);for(let s=0,a=t.length;s<a;s++)i[s]=t[s]*n;t=i}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const i=this instanceof as?uI:r_;return new i(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function yI(r,e,t){const n=e.attributes,i=new Ji;if(n.POSITION!==void 0){const c=t.json.accessors[n.POSITION],u=c.min,h=c.max;if(u!==void 0&&h!==void 0){if(i.set(new F(u[0],u[1],u[2]),new F(h[0],h[1],h[2])),c.normalized){const f=ad(Ks[c.componentType]);i.min.multiplyScalar(f),i.max.multiplyScalar(f)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const s=e.targets;if(s!==void 0){const c=new F,u=new F;for(let h=0,f=s.length;h<f;h++){const p=s[h];if(p.POSITION!==void 0){const m=t.json.accessors[p.POSITION],g=m.min,x=m.max;if(g!==void 0&&x!==void 0){if(u.setX(Math.max(Math.abs(g[0]),Math.abs(x[0]))),u.setY(Math.max(Math.abs(g[1]),Math.abs(x[1]))),u.setZ(Math.max(Math.abs(g[2]),Math.abs(x[2]))),m.normalized){const M=ad(Ks[m.componentType]);u.multiplyScalar(M)}c.max(u)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}i.expandByVector(c)}r.boundingBox=i;const a=new Ei;i.getCenter(a.center),a.radius=i.min.distanceTo(i.max)/2,r.boundingSphere=a}function cg(r,e,t){const n=e.attributes,i=[];function s(a,c){return t.getDependency("accessor",a).then(function(u){r.setAttribute(c,u)})}for(const a in n){const c=od[a]||a.toLowerCase();c in r.attributes||i.push(s(n[a],c))}if(e.indices!==void 0&&!r.index){const a=t.getDependency("accessor",e.indices).then(function(c){r.setIndex(c)});i.push(a)}return Mt.workingColorSpace!==Fn&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${Mt.workingColorSpace}" not supported.`),ji(r,e),yI(r,e,t),Promise.all(i).then(function(){return e.targets!==void 0?fI(r,e.targets,t):r})}class xI extends ls{constructor(e){super(e),this.animateBonePositions=!0,this.animateBoneRotations=!0}load(e,t,n,i){const s=this,a=new wd(s.manager);a.setPath(s.path),a.setRequestHeader(s.requestHeader),a.setWithCredentials(s.withCredentials),a.load(e,function(c){try{t(s.parse(c))}catch(u){i?i(u):console.error(u),s.manager.itemError(e)}},n,i)}parse(e){function t(g){c(g)!=="HIERARCHY"&&console.error("THREE.BVHLoader: HIERARCHY expected.");const x=[],M=i(g,c(g),x);c(g)!=="MOTION"&&console.error("THREE.BVHLoader: MOTION expected.");let v=c(g).split(/[\s]+/);const _=parseInt(v[1]);isNaN(_)&&console.error("THREE.BVHLoader: Failed to read number of frames."),v=c(g).split(/[\s]+/);const A=parseFloat(v[2]);isNaN(A)&&console.error("THREE.BVHLoader: Failed to read frame time.");for(let P=0;P<_;P++)v=c(g).split(/[\s]+/),n(v,P*A,M);return x}function n(g,x,M){if(M.type==="ENDSITE")return;const v={time:x,position:new F,rotation:new Yt};M.frames.push(v);const _=new Yt,A=new F(1,0,0),P=new F(0,1,0),b=new F(0,0,1);for(let B=0;B<M.channels.length;B++)switch(M.channels[B]){case"Xposition":v.position.x=parseFloat(g.shift().trim());break;case"Yposition":v.position.y=parseFloat(g.shift().trim());break;case"Zposition":v.position.z=parseFloat(g.shift().trim());break;case"Xrotation":_.setFromAxisAngle(A,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Yrotation":_.setFromAxisAngle(P,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;case"Zrotation":_.setFromAxisAngle(b,parseFloat(g.shift().trim())*Math.PI/180),v.rotation.multiply(_);break;default:console.warn("THREE.BVHLoader: Invalid channel type.")}for(let B=0;B<M.children.length;B++)n(g,x,M.children[B])}function i(g,x,M){const v={name:"",type:"",frames:[]};M.push(v);let _=x.split(/[\s]+/);_[0].toUpperCase()==="END"&&_[1].toUpperCase()==="SITE"?(v.type="ENDSITE",v.name="ENDSITE"):(v.name=_[1],v.type=_[0].toUpperCase()),c(g)!=="{"&&console.error("THREE.BVHLoader: Expected opening { after type & name"),_=c(g).split(/[\s]+/),_[0]!=="OFFSET"&&console.error("THREE.BVHLoader: Expected OFFSET but got: "+_[0]),_.length!==4&&console.error("THREE.BVHLoader: Invalid number of values for OFFSET.");const A=new F(parseFloat(_[1]),parseFloat(_[2]),parseFloat(_[3]));if((isNaN(A.x)||isNaN(A.y)||isNaN(A.z))&&console.error("THREE.BVHLoader: Invalid values of OFFSET."),v.offset=A,v.type!=="ENDSITE"){_=c(g).split(/[\s]+/),_[0]!=="CHANNELS"&&console.error("THREE.BVHLoader: Expected CHANNELS definition.");const P=parseInt(_[1]);v.channels=_.splice(2,P),v.children=[]}for(;;){const P=c(g);if(P==="}")return v;v.children.push(i(g,P,M))}}function s(g,x){const M=new Vc;if(x.push(M),M.position.add(g.offset),M.name=g.name,g.type!=="ENDSITE")for(let v=0;v<g.children.length;v++)M.add(s(g.children[v],x));return M}function a(g){const x=[];for(let M=0;M<g.length;M++){const v=g[M];if(v.type==="ENDSITE")continue;const _=[],A=[],P=[];for(let b=0;b<v.frames.length;b++){const B=v.frames[b];_.push(B.time),A.push(B.position.x+v.offset.x),A.push(B.position.y+v.offset.y),A.push(B.position.z+v.offset.z),P.push(B.rotation.x),P.push(B.rotation.y),P.push(B.rotation.z),P.push(B.rotation.w)}u.animateBonePositions&&x.push(new cs(v.name+".position",_,A)),u.animateBoneRotations&&x.push(new as(v.name+".quaternion",_,P))}return new Bc("animation",-1,x)}function c(g){let x;for(;(x=g.shift().trim()).length===0;);return x}const u=this,h=e.split(/[\r\n]+/g),f=t(h),p=[];s(f[0],p);const m=a(f);return{skeleton:new ia(p),clip:m}}}const s_=new kC,bI=new xI;let so=0;async function SI(r,e){return new Promise((t,n)=>{s_.load(r,i=>{const s=i.scene;e.add(s),s.traverse(u=>{u.isMesh&&(u.castShadow=!0,u.receiveShadow=!0)}),so++;const a=`Asset ${so}`,c=Ld();c&&Dd(c,a,s),t(s)},void 0,i=>n(i))})}async function MI(r,e){const t=URL.createObjectURL(r);try{return await SI(t,e)}finally{URL.revokeObjectURL(t)}}const TI=[{color:13935988,roughness:.55,metalness:0},{color:13935988,roughness:.55,metalness:0},{color:1118481,roughness:.8,metalness:0},{color:657930,roughness:.1,metalness:0},{color:16052456,roughness:.2,metalness:0},{color:16052456,roughness:.05,metalness:0,opacity:.3,transparent:!0},{color:4881051,roughness:.15,metalness:0},{color:11885162,roughness:.7,metalness:0},{color:15789280,roughness:.3,metalness:0},{color:14723210,roughness:.4,metalness:0},{color:14723210,roughness:.4,metalness:0}];function Lc(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Float32Array(t.buffer)}function o_(r){const e=atob(r),t=new Uint8Array(e.length);for(let n=0;n<e.length;n++)t[n]=e.charCodeAt(n);return new Uint32Array(t.buffer)}function cd(r){for(let e=0;e<r.length;e+=3){const t=r[e+1],n=r[e+2];r[e+1]=n,r[e+2]=-t}}function EI(r){const e=Lc(r.vertices),t=o_(r.faces);cd(e);const n=new hn,i=new nn(e,3),s=new nn(t,1);if(n.setAttribute("position",i),n.setIndex(s),r.uvs){const f=Lc(r.uvs);n.setAttribute("uv",new nn(f,2))}if(r.normals){const f=Lc(r.normals);cd(f),n.setAttribute("normal",new nn(f,3))}else n.computeVertexNormals();const a=TI.map(f=>new os({color:f.color,roughness:f.roughness,metalness:f.metalness,side:Gn,transparent:f.transparent||!1,opacity:f.opacity!==void 0?f.opacity:1})),c=r.groups||[];let u;if(s&&c.length>0){for(const f of c)n.addGroup(f.start,f.count,f.materialIndex);u=new Te(n,a)}else u=new Te(n,a[0]);u.castShadow=!0,u.receiveShadow=!0;const h=new Yi;return h.add(u),h}async function dh(r,e,t){const n=new URLSearchParams;if(e.body_type&&n.set("body_type",e.body_type),e.morphs&&typeof e.morphs=="object")for(const[m,g]of Object.entries(e.morphs))g!=null&&n.set(`morph_${m}`,String(g));if(e.user_morphs&&typeof e.user_morphs=="object")for(const[m,g]of Object.entries(e.user_morphs))g!=null&&n.set(`morph_${m}`,String(g));const i=["age","mass","tone","height"],s=e.meta||{};for(const m of i){const g=s[m]??e[`meta_${m}`];g!=null&&n.set(`meta_${m}`,String(g))}const a=`/api/character/mesh/?${n.toString()}`,c=await fetch(a);if(!c.ok)throw new Error(`Character mesh API error: ${c.status}`);const u=await c.json(),h=EI(u);if(r.add(h),e.hair_style&&e.hair_style.url)try{const m=await AI(e.hair_style.url);m.userData.isHair=!0,m.traverse(g=>{g.isMesh&&(g.userData.isHair=!0)}),h.add(m),console.log("✓ Hair loaded:",e.hair_style.name)}catch(m){console.error("Failed to load hair:",m)}if(e.garments&&Array.isArray(e.garments))for(const m of e.garments)try{const g=await wI(m,e.body_type);g.userData.isGarment=!0,h.add(g),console.log("✓ Garment loaded:",m.id)}catch(g){console.error("Failed to load garment:",m.id,g)}so++;const f=t||`Character ${so}`,p=Ld();return p&&Dd(p,f,h),h}async function AI(r){return new Promise((e,t)=>{s_.load(r,n=>{const i=n.scene;i.traverse(s=>{if(s.isMesh&&(s.castShadow=!0,s.receiveShadow=!0,s.material)){if(s.material.color){const a=s.material.color;a.r>.9&&a.g>.9&&a.b>.9&&s.material.color.setRGB(.1,.08,.06)}s.material.roughness===void 0&&(s.material.roughness=.8),s.material.metalness===void 0&&(s.material.metalness=0)}}),e(i)},void 0,n=>t(n))})}async function wI(r,e){const{id:t,offset:n=.006,stiffness:i=.8,color:s=[.3,.35,.5],roughness:a=.8,metalness:c=0}=r,u=s[0]??.3,h=s[1]??.35,f=s[2]??.5,p=`garment_id=${encodeURIComponent(t)}&body_type=${encodeURIComponent(e)}&offset=${n}&stiffness=${i}&color_r=${u.toFixed(3)}&color_g=${h.toFixed(3)}&color_b=${f.toFixed(3)}`,m=await fetch(`/api/character/garment/fit/?${p}`);if(!m.ok)throw new Error(`Garment fit API error: ${m.status}`);const g=await m.json();if(g.error)throw new Error(g.error);const x=Lc(g.vertices);cd(x);const M=o_(g.faces),v=new hn;v.setAttribute("position",new nn(x,3)),v.setIndex(new nn(M,1)),v.computeVertexNormals();const _=new qe(g.color[0],g.color[1],g.color[2]),A=new os({color:_,roughness:a,metalness:c,side:Gn,polygonOffset:!0,polygonOffsetFactor:-1,polygonOffsetUnit:-1}),P=new Te(v,A);return P.castShadow=!0,P.receiveShadow=!0,P}function PI(r,e,t){const n=bI.parse(r),i=new hC(n.skeleton.bones[0]);i.skeleton=n.skeleton,i.visible=!0,i.userData.isRig=!0,i.renderOrder=999,i.material&&(i.material.depthTest=!1,i.material.depthWrite=!1);const s=n.skeleton.bones[0];s.userData.isRig=!0,e.add(s),e.add(i);const a=new $g(s),c=a.clipAction(n.clip);c.setLoop(gd),c.play(),c.paused=!0,so++;const u=Ld();u&&Dd(u,t||`BVH ${so}`,s);const h=n.clip.duration||1;return{mixer:a,action:c,skeleton:i,clip:n.clip,rootBone:s,duration:h}}class RI{constructor(e){this._canvas=e,this._recorder=null,this._chunks=[]}start(e=30){const t=this._canvas.captureStream(e);this._chunks=[];const n=MediaRecorder.isTypeSupported("video/webm;codecs=vp9")?"video/webm;codecs=vp9":"video/webm;codecs=vp8";this._recorder=new MediaRecorder(t,{mimeType:n,videoBitsPerSecond:8e6}),this._recorder.ondataavailable=i=>{i.data.size>0&&this._chunks.push(i.data)},this._recorder.start()}stop(){return new Promise(e=>{this._recorder.onstop=()=>{const t=new Blob(this._chunks,{type:"video/webm"});this._chunks=[],e(t)},this._recorder.stop()})}get isRecording(){var e;return((e=this._recorder)==null?void 0:e.state)==="recording"}async stopAndDownload(e="theatre-export.webm"){const t=await this.stop(),n=URL.createObjectURL(t),i=document.createElement("a");i.href=n,i.download=e,i.click(),URL.revokeObjectURL(n)}}async function CI(){const r=await fetch("/api/character/scenes/");if(!r.ok)throw new Error(`Scene list error: ${r.status}`);return(await r.json()).scenes||[]}async function II(r){const e=await fetch(`/api/character/scene/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Scene load error: ${e.status}`);return e.json()}async function LI(r,e){const t=await fetch("/api/character/scene/save/",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:r,data:e})});if(!t.ok){const n=await t.json().catch(()=>({}));throw new Error(n.error||`Scene save error: ${t.status}`)}return t.json()}async function DI(){const r=await fetch("/api/character/models/");if(!r.ok)throw new Error(`Model list error: ${r.status}`);return(await r.json()).presets||[]}async function lg(r){const e=await fetch(`/api/character/model/${encodeURIComponent(r)}/`);if(!e.ok)throw new Error(`Model load error: ${e.status}`);return e.json()}async function NI(){const r=await fetch("/api/character/animations/");if(!r.ok)throw new Error(`Animation list error: ${r.status}`);return(await r.json()).categories||{}}async function OI(r,e){const t=`/api/character/bvh/${encodeURIComponent(r)}/${encodeURIComponent(e)}/`,n=await fetch(t);if(!n.ok)throw new Error(`BVH load error: ${n.status}`);return n.text()}const fh={ballet_stage:{name:"Ballet Stage",description:"Warme Spotlights, theatralisch dunkel",camera:{position:{x:0,y:1.6,z:5},fov:35},lights:{spotLeft:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:-3,y:6,z:3}},spotRight:{intensity:60,color:{r:1,g:.933,b:.867},position:{x:3,y:6,z:3}},backLight:{intensity:25,color:{r:.4,g:.267,b:.667},position:{x:0,y:5,z:-4}}}},studio_bright:{name:"Studio Bright",description:"Helle, gleichmäßige Beleuchtung für Details",camera:{position:{x:0,y:1.6,z:4},fov:40},lights:{spotLeft:{intensity:80,color:{r:1,g:1,b:1},position:{x:-2,y:5,z:4}},spotRight:{intensity:80,color:{r:1,g:1,b:1},position:{x:2,y:5,z:4}},backLight:{intensity:30,color:{r:.9,g:.95,b:1},position:{x:0,y:4,z:-3}}}},cinematic_moody:{name:"Cinematic Moody",description:"Dramatisches Film-noir-Licht, starke Schatten",camera:{position:{x:2,y:1.4,z:4},fov:28},lights:{spotLeft:{intensity:15,color:{r:1,g:.8,b:.6},position:{x:-4,y:7,z:2}},spotRight:{intensity:2,color:{r:.6,g:.7,b:.9},position:{x:4,y:3,z:3}},backLight:{intensity:10,color:{r:.3,g:.5,b:1},position:{x:1,y:6,z:-5}}}},fashion_show:{name:"Fashion Show",description:"Laufsteg-Beleuchtung, kühles Weiß von oben",camera:{position:{x:0,y:1.2,z:6},fov:50},lights:{spotLeft:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:-2,y:8,z:2}},spotRight:{intensity:10,color:{r:.95,g:.97,b:1},position:{x:2,y:8,z:2}},backLight:{intensity:5,color:{r:1,g:1,b:1},position:{x:0,y:3,z:-2}}}},sunset_warm:{name:"Sunset Warm",description:"Goldene Stunde, warmes Orange-Gold",camera:{position:{x:-1,y:1.5,z:4.5},fov:42},lights:{spotLeft:{intensity:14,color:{r:1,g:.7,b:.4},position:{x:-5,y:4,z:3}},spotRight:{intensity:6,color:{r:1,g:.85,b:.7},position:{x:3,y:5,z:2}},backLight:{intensity:8,color:{r:.8,g:.4,b:.6},position:{x:2,y:5,z:-4}}}}};function ph(r,e,t,n){console.log(`[Preset] Applying: ${r.name}`),e.position.set(r.camera.position.x,r.camera.position.y,r.camera.position.z),e.fov=r.camera.fov,e.updateProjectionMatrix(),n&&(n.target.set(0,.9,0),n.update()),mh(t.spotLeft,r.lights.spotLeft),mh(t.spotRight,r.lights.spotRight),mh(t.backLight,r.lights.backLight),console.log(`✓ Preset "${r.name}" applied (direct Three.js)`)}function mh(r,e){r&&(r.intensity=e.intensity,r.color.setRGB(e.color.r,e.color.g,e.color.b),r.position.set(e.position.x,e.position.y,e.position.z))}window.addEventListener("DOMContentLoaded",()=>{const r=document.getElementById("theatre-canvas");if(!r){console.error("theatre-canvas not found");return}const{scene:e,camera:t,renderer:n,controls:i,lights:s,lightIcons:a,transformControls:c}=OC(r);window.scene=e,window.lights=s,window.lightIcons=a,window.transformControls=c,window.activeMixer=null,window.isPlaying=!1,window.currentTime=0,window.animDuration=1;const u=new Jg,h=new Qe;let f=null,p=null;const m=[];let g=null,x=null;async function M(){try{const[V,L]=await Promise.all([fetch("/api/character/skeleton/"),fetch("/api/character/skin-weights/")]);V.ok&&(g=await V.json()),L.ok&&(x=await L.json()),console.log("✓ Loaded skeleton and skin weights")}catch(V){console.warn("Failed to load skeleton/weights:",V)}}M();function v(V,L,J,W){const he=new(void 0)().parse(V),me=new $g(L),Le=me.clipAction(he.clip);Le.setLoop(gd),Le.play(),Le.paused=!0;const Ke=he.clip.duration||1;return console.log("✓ BVH animation loaded on SkinnedMesh:",W,Ke+"s"),{mixer:me,action:Le,duration:Ke}}function _(V){if(!g||!x)return console.warn("Cannot convert to SkinnedMesh: skeleton/weights not loaded"),null;if(V.userData.isSkinnedMesh)return console.log("Already a SkinnedMesh"),V.userData.skinnedMesh;const L=V.children.find(Xe=>Xe.isMesh);if(!L)return console.warn("No mesh found in character group"),null;console.log("Converting to SkinnedMesh...");const J=L.geometry.clone(),W=J.attributes.position.count,ie=new Float32Array(W*4),he=new Float32Array(W*4);for(let Xe=0;Xe<W;Xe++){const Ht=x.indices[Xe]||[0,0,0,0],Bn=x.weights[Xe]||[1,0,0,0];ie[Xe*4+0]=Ht[0],ie[Xe*4+1]=Ht[1],ie[Xe*4+2]=Ht[2],ie[Xe*4+3]=Ht[3],he[Xe*4+0]=Bn[0],he[Xe*4+1]=Bn[1],he[Xe*4+2]=Bn[2],he[Xe*4+3]=Bn[3]}J.setAttribute("skinIndex",new zt(ie,4)),J.setAttribute("skinWeight",new zt(he,4));const me=[],Le=[];for(const Xe of g.bones){const Ht=new Vc;Ht.name=Xe.name,Ht.position.fromArray(Xe.position),Ht.quaternion.fromArray(Xe.quaternion),Ht.scale.fromArray(Xe.scale),me.push(Ht);const Bn=new rt;Xe.inverse&&Bn.fromArray(Xe.inverse),Le.push(Bn)}for(let Xe=0;Xe<g.bones.length;Xe++){const Ht=g.bones[Xe].parent;Ht>=0&&me[Ht].add(me[Xe])}const Ke=new ia(me,Le),bt=me[0],et=L.material,Et=new Gg(J,et);Et.castShadow=!0,Et.receiveShadow=!0,Et.add(bt),Et.bind(Ke);const $t=L.position.clone(),Tn=L.rotation.clone(),Kt=L.scale.clone();return V.remove(L),Et.position.copy($t),Et.rotation.copy(Tn),Et.scale.copy(Kt),V.add(Et),V.userData.isSkinnedMesh=!0,V.userData.skinnedMesh=Et,V.userData.skeleton=Ke,V.userData.rootBone=bt,console.log("✓ Converted to SkinnedMesh with",me.length,"bones"),Et}r.addEventListener("click",V=>{const L=r.getBoundingClientRect();h.x=(V.clientX-L.left)/L.width*2-1,h.y=-((V.clientY-L.top)/L.height)*2+1,u.setFromCamera(h,t);const J=[a.spotLeftIcon,a.spotRightIcon,a.backLightIcon],W=u.intersectObjects(J,!0);if(W.length>0){let he=W[0].object;for(;he.parent&&!he.userData.light;)he=he.parent;if(he.userData.light){f=he,p=null,c.attach(he),console.log("✓ Licht ausgewählt:",he.userData.light),Ue(he.userData.light);return}}const ie=u.intersectObjects(m,!0);if(ie.length>0){let he=ie[0].object;for(;he.parent&&!he.userData.isCharacter;)he=he.parent;if(he.userData.isCharacter){p=he,f=null,c.attach(he),console.log("✓ Character ausgewählt:",he.userData.presetName),Ye(he);return}}c.detach(),f=null,p=null,pt()});const{sheet:A}=FC();BC(A,t),Sc(A,"Spot Left",s.spotLeft),Sc(A,"Spot Right",s.spotRight),Sc(A,"Back Light",s.backLight);const P=new RI(n.domElement);let b=null,B=null;const U=new JR;document.querySelectorAll(".menu-item").forEach(V=>{const L=V.querySelector(".menu-dropdown");L&&(V.addEventListener("click",J=>{J.stopPropagation(),document.querySelectorAll(".menu-item").forEach(W=>W.classList.remove("active")),V.classList.toggle("active")}),L.addEventListener("click",J=>{J.stopPropagation()}))}),document.addEventListener("click",()=>{document.querySelectorAll(".menu-item").forEach(V=>V.classList.remove("active"))}),document.querySelectorAll("[data-preset]").forEach(V=>{V.addEventListener("click",()=>{const L=V.getAttribute("data-preset"),J=fh[L];J?(ph(J,t,s,i),console.log("✓ Applied preset:",J.name),document.querySelectorAll(".menu-item").forEach(W=>W.classList.remove("active"))):console.error("Preset not found:",L)})}),document.querySelectorAll(".panel-tab").forEach(V=>{V.addEventListener("click",()=>{const L=V.getAttribute("data-tab");document.querySelectorAll(".panel-tab").forEach(W=>W.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(W=>W.classList.remove("active")),V.classList.add("active");const J=document.getElementById(L);J&&J.classList.add("active")})});const O=document.getElementById("btn-translate-mode"),z=document.getElementById("btn-rotate-mode"),I=document.getElementById("btn-toggle-lights");O&&O.addEventListener("click",()=>{c.setMode("translate"),O.classList.add("active"),z.classList.remove("active")}),z&&z.addEventListener("click",()=>{c.setMode("rotate"),z.classList.add("active"),O.classList.remove("active")});let w=!0;I&&I.addEventListener("click",()=>{w=!w,Object.values(a).forEach(V=>{V.visible=w}),w?I.classList.add("active"):I.classList.remove("active")});const H=document.getElementById("btn-toggle-model");let ee=!0;H&&H.addEventListener("click",()=>{ee=!ee,e.traverse(V=>{V.isMesh&&!V.userData.isGarment&&!V.userData.isHair&&!V.userData.isRig&&(V.visible=ee)}),H.classList.toggle("active",ee)});const Q=document.getElementById("btn-toggle-clothes");let ae=!0;Q&&Q.addEventListener("click",()=>{ae=!ae,e.traverse(V=>{V.isMesh&&(V.userData.isGarment||V.userData.isHair)&&(V.visible=ae)}),Q.classList.toggle("active",ae)});const ce=document.getElementById("btn-toggle-rig");let $=!1;ce&&ce.addEventListener("click",()=>{$=!$,e.traverse(V=>{(V.isSkeletonHelper||V.userData.isRig)&&(V.visible=$)}),ce.classList.toggle("active",$)});const fe=document.getElementById("btn-play-animation");fe&&fe.addEventListener("click",()=>{const V=document.getElementById("btnPlayPause");V&&V.click()});function re(V){const L=document.getElementById(V);L&&(L.style.display="flex")}function ye(V){const L=document.getElementById(V);L&&(L.style.display="none")}document.querySelectorAll("[data-close-modal]").forEach(V=>{V.addEventListener("click",()=>{var L;(L=V.closest(".theatre-modal-overlay"))==null||L.style.removeProperty("display")})}),document.querySelectorAll(".theatre-modal-overlay").forEach(V=>{V.addEventListener("click",L=>{L.target===V&&V.style.removeProperty("display")})});const Me=document.getElementById("menu-scene-load");Me&&Me.addEventListener("click",async()=>{const V=document.getElementById("scene-list-body");V.innerHTML='<div class="loading-msg">Lade Scenes...</div>',re("modal-scene-load");try{const L=await CI();if(L.length===0){V.innerHTML='<div class="loading-msg">Keine Scenes gefunden.</div>';return}V.innerHTML="";for(const J of L){const W=document.createElement("div");W.style.cssText="padding:10px 14px;border-radius:6px;cursor:pointer;color:#ccc;font-size:0.85rem;",W.innerHTML=`<span>${J.label||J.name}</span>`,W.addEventListener("click",()=>Ne(J.name)),W.addEventListener("mouseenter",()=>W.style.background="rgba(124, 92, 191, 0.2)"),W.addEventListener("mouseleave",()=>W.style.background=""),V.appendChild(W)}}catch(L){V.innerHTML=`<div class="loading-msg">Fehler: ${L.message}</div>`}});async function Ne(V){ye("modal-scene-load");try{const L=await II(V);if(console.log("Scene loaded:",V,L),L.characters&&Array.isArray(L.characters))for(const J of L.characters){const W=await dh(e,J,J.name||V);W.userData.isCharacter=!0,W.userData.presetName=J.name||V,W.userData.bodyType=J.body_type||"Unknown",m.push(W)}}catch(L){console.error("Scene load error:",L),alert("Scene laden fehlgeschlagen: "+L.message)}}const Ze=document.getElementById("menu-scene-save"),ht=document.getElementById("scene-save-btn"),le=document.getElementById("scene-save-name");Ze&&Ze.addEventListener("click",()=>{re("modal-scene-save"),le&&(le.value="",le.focus())}),ht&&le&&(ht.addEventListener("click",async()=>{const V=le.value.trim();if(V){ht.disabled=!0,ht.textContent="Speichere...";try{const L={camera:{position:t.position.toArray(),fov:t.fov,target:i.target.toArray()},lights:{spotLeft:{position:s.spotLeft.position.toArray(),intensity:s.spotLeft.intensity,color:"#"+s.spotLeft.color.getHexString()},spotRight:{position:s.spotRight.position.toArray(),intensity:s.spotRight.intensity,color:"#"+s.spotRight.color.getHexString()},backLight:{position:s.backLight.position.toArray(),intensity:s.backLight.intensity,color:"#"+s.backLight.color.getHexString()}},characters:[]},J=await LI(V,L);console.log("Scene saved:",J),ye("modal-scene-save")}catch(L){console.error("Scene save error:",L),alert("Scene speichern fehlgeschlagen: "+L.message)}ht.disabled=!1,ht.textContent="Speichern"}}),le.addEventListener("keydown",V=>{V.key==="Enter"&&ht.click()}));const ge=document.getElementById("model-list"),Oe=document.getElementById("menu-model-load");async function Se(){try{const V=await DI();if(V.length===0){ge.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Modelle gefunden.</div>';return}ge.innerHTML="";for(const L of V){const J=document.createElement("div");J.className="anim-item",J.textContent=L.label||L.name,J.addEventListener("click",async()=>{try{const W=await lg(L.name),ie=await dh(e,W,L.name);ie.userData.isCharacter=!0,ie.userData.presetName=L.name,ie.userData.bodyType=W.body_type||"Unknown",m.push(ie),console.log("Model loaded:",L.name),document.querySelectorAll("#model-list .anim-item").forEach(he=>he.classList.remove("active")),J.classList.add("active")}catch(W){console.error("Model load error:",W),alert("Modell laden fehlgeschlagen: "+W.message)}}),ge.appendChild(J)}}catch(V){ge.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${V.message}</div>`}}Se(),Oe&&Oe.addEventListener("click",()=>{document.querySelectorAll(".panel-tab").forEach(J=>J.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(J=>J.classList.remove("active"));const V=document.querySelector('[data-tab="tab-models"]'),L=document.getElementById("tab-models");V&&V.classList.add("active"),L&&L.classList.add("active")});const We=document.getElementById("anim-tree");async function tt(){try{const V=await NI(),L=Object.keys(V);if(L.length===0){We.innerHTML='<div style="padding:12px;color:var(--text-muted);font-size:0.8rem;">Keine Animationen gefunden.</div>';return}We.innerHTML="";for(const J of L){const W=V[J],ie=document.createElement("div");ie.className="anim-cat";const he=document.createElement("div");he.className="anim-cat-header",he.innerHTML=`<i class="fas fa-chevron-right"></i> ${J} (${W.length})`,he.addEventListener("click",()=>{ie.classList.toggle("open")}),ie.appendChild(he);const me=document.createElement("div");me.className="anim-cat-body";for(const Le of W){const Ke=document.createElement("div");Ke.className="anim-item",Ke.textContent=Le.name,Ke.addEventListener("click",async()=>{await st(Le.category,Le.name),document.querySelectorAll("#anim-tree .anim-item").forEach(bt=>bt.classList.remove("active")),Ke.classList.add("active")}),me.appendChild(Ke)}ie.appendChild(me),We.appendChild(ie)}}catch(V){We.innerHTML=`<div style="padding:12px;color:#e74c3c;font-size:0.8rem;">Fehler: ${V.message}</div>`}}async function st(V,L){try{const J=await OI(V,L);let W=null;p&&(W=_(p));const{mixer:ie,action:he,duration:me}=W?v(J,W,e,`${V}/${L}`):PI(J,e,`${V}/${L}`);b&&b.stopAllAction(),b=ie,B=he,window.activeMixer=b,Ee(me),ue=!1,pe=0,de=me,window.isPlaying=!1,window.currentTime=0,window.animDuration=me,ct(),console.log("Animation loaded:",V,L,me)}catch(J){console.error("Animation load error:",J),alert("Animation laden fehlgeschlagen: "+J.message)}}tt();const Tt=document.getElementById("menu-add-glb"),ot=document.getElementById("glb-file-input");Tt&&ot&&(Tt.addEventListener("click",()=>ot.click()),ot.addEventListener("change",async()=>{const V=ot.files[0];if(V){try{await MI(V,e)}catch(L){console.error("GLB load error:",L),alert("Fehler beim Laden der GLB-Datei: "+L.message)}ot.value=""}})),document.querySelectorAll("[data-preset]").forEach(V=>{V.addEventListener("click",()=>{const L=V.getAttribute("data-preset"),J=fh[L];J?(ph(J,t,s,i),console.log("✓ Applied preset:",J.name)):console.error("Preset not found:",L)})});const Ot=document.getElementById("menu-add-light");let X=0;Ot&&Ot.addEventListener("click",()=>{X++;const V=new Zg(16777215,1,15);V.position.set((Math.random()-.5)*6,2+Math.random()*3,(Math.random()-.5)*6),e.add(V);const L=new Te(new ra(.08,8,8),new ci({color:16776960}));V.add(L),Sc(A,`Light ${X}`,V)});const Qt=document.getElementById("menu-export-video");Qt&&Qt.addEventListener("click",async()=>{P.isRecording?(Qt.innerHTML='<i class="fas fa-file-video"></i> Export Video',await P.stopAndDownload()):(P.start(30),Qt.innerHTML='<i class="fas fa-stop"></i> Stop Recording')});const at=document.getElementById("btnPlayPause"),dt=document.getElementById("btnStop"),Ve=document.getElementById("btnFrameBack"),xt=document.getElementById("btnFrameFwd"),Fe=document.getElementById("timelineSlider"),N=document.getElementById("timeCurrent"),E=document.getElementById("timeDuration"),Z=document.getElementById("playIcon");let ue=!1,pe=0,de=1,De=1;function Ee(V){de=V||1,E.textContent=Re(de),Fe.max=de}function Re(V){const L=Math.floor(V/60),J=Math.floor(V%60);return`${String(L).padStart(2,"0")}:${String(J).padStart(2,"0")}`}function ct(){N.textContent=Re(pe),Fe.value=pe,Z&&(Z.className=ue?"fas fa-pause":"fas fa-play")}function _e(V){!b||!B||(pe=Math.max(0,Math.min(V,de)),B.time=pe,b.update(0),ct())}at&&at.addEventListener("click",()=>{b&&(ue=!ue,window.isPlaying=ue,ue&&B?(B.paused=!1,B.play()):B&&(B.paused=!0),ct())}),dt&&dt.addEventListener("click",()=>{b&&(ue=!1,pe=0,_e(0),B&&(B.stop(),B.paused=!0),ct())}),Ve&&Ve.addEventListener("click",()=>{_e(pe-1/30)}),xt&&xt.addEventListener("click",()=>{_e(pe+1/30)}),Fe&&(Fe.addEventListener("mousedown",()=>{}),Fe.addEventListener("mouseup",()=>{}),Fe.addEventListener("input",()=>{const V=parseFloat(Fe.value);_e(V)})),document.querySelectorAll(".speed-btn").forEach(V=>{V.addEventListener("click",()=>{const L=parseFloat(V.getAttribute("data-speed"));De=L,b&&(b.timeScale=L),document.querySelectorAll(".speed-btn").forEach(J=>J.classList.remove("active")),V.classList.add("active")})}),document.addEventListener("keydown",V=>{V.target.tagName!=="INPUT"&&(V.code==="Space"?(V.preventDefault(),at&&at.click()):V.code==="ArrowLeft"?(V.preventDefault(),Ve&&Ve.click()):V.code==="ArrowRight"&&(V.preventDefault(),xt&&xt.click()))});async function Ce(){try{const V=await fetch("/api/settings/theatre/");if(!V.ok)return;const L=await V.json();if(L.preset){const J=fh[L.preset];J&&(ph(J,t,s,i),console.log("✓ Auto-applied preset:",J.name))}if(L.model)try{const J=await lg(L.model),W=await dh(e,J,L.model);if(W.userData.isCharacter=!0,W.userData.presetName=L.model,W.userData.bodyType=J.body_type||"Unknown",m.push(W),console.log("✓ Auto-loaded model:",L.model),L.animation){const[ie,he]=L.animation.split("/");ie&&he&&(await st(ie,he),console.log("✓ Auto-loaded animation:",L.animation))}}catch(J){console.warn("Auto-load model/animation failed:",J)}}catch(V){console.warn("Failed to load Theatre defaults:",V)}}setTimeout(Ce,500);function Ue(V){document.querySelectorAll(".panel-tab").forEach(Xe=>Xe.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Xe=>Xe.classList.remove("active"));const L=document.querySelector('[data-tab="tab-properties"]'),J=document.getElementById("tab-properties");L&&L.classList.add("active"),J&&J.classList.add("active");const W=document.getElementById("properties-content");if(!W)return;const ie=V===s.spotLeft?"Spot Left":V===s.spotRight?"Spot Right":V===s.backLight?"Back Light":"Light",he="#"+V.color.getHexString();W.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-lightbulb"></i> ${ie}
                </h3>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Intensität: <span id="light-intensity-value">${V.intensity.toFixed(1)}</span>
                    </label>
                    <input type="range" id="light-intensity" min="0" max="100" step="1" value="${V.intensity}"
                           style="width:100%;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Farbe
                    </label>
                    <input type="color" id="light-color" value="${he}"
                           style="width:100%;height:32px;border-radius:4px;border:1px solid var(--border);background:var(--bg-primary);cursor:pointer;" />
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="light-pos-x" value="${V.position.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-pos-y" value="${V.position.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-pos-z" value="${V.position.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="light-rot-x" value="${(V.rotation.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="light-rot-y" value="${(V.rotation.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="light-rot-z" value="${(V.rotation.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Ziehe das Licht-Icon in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const me=document.getElementById("light-intensity"),Le=document.getElementById("light-intensity-value"),Ke=document.getElementById("light-color"),bt=document.getElementById("light-pos-x"),et=document.getElementById("light-pos-y"),Et=document.getElementById("light-pos-z");if(me&&(me.oninput=Xe=>{V.intensity=parseFloat(Xe.target.value),Le.textContent=V.intensity.toFixed(1)}),Ke&&(Ke.oninput=Xe=>{V.color.setHex(parseInt(Xe.target.value.substring(1),16)),f&&f.children.forEach(Ht=>{Ht.material&&(Ht.material.color.copy(V.color),Ht.material.emissive&&Ht.material.emissive.copy(V.color))})}),bt&&et&&Et){const Xe=()=>{V.position.set(parseFloat(bt.value),parseFloat(et.value),parseFloat(Et.value)),f&&(f.position.copy(V.position),f.lookAt(V.target.position))};bt.oninput=Xe,et.oninput=Xe,Et.oninput=Xe}const $t=document.getElementById("light-rot-x"),Tn=document.getElementById("light-rot-y"),Kt=document.getElementById("light-rot-z");if($t&&Tn&&Kt){const Xe=()=>{V.rotation.set(parseFloat($t.value)*Math.PI/180,parseFloat(Tn.value)*Math.PI/180,parseFloat(Kt.value)*Math.PI/180),f&&f.rotation.copy(V.rotation)};$t.oninput=Xe,Tn.oninput=Xe,Kt.oninput=Xe}}function Ye(V){document.querySelectorAll(".panel-tab").forEach(Kt=>Kt.classList.remove("active")),document.querySelectorAll(".tab-pane").forEach(Kt=>Kt.classList.remove("active"));const L=document.querySelector('[data-tab="tab-properties"]'),J=document.getElementById("tab-properties");L&&L.classList.add("active"),J&&J.classList.add("active");const W=document.getElementById("properties-content");if(!W)return;const ie=V.userData.presetName||"Character",he=V.userData.bodyType||"Unknown",me=V.position,Le=V.rotation;W.innerHTML=`
            <div style="padding:16px;">
                <h3 style="font-size:0.9rem;margin-bottom:16px;color:var(--accent-purple);border-bottom:1px solid var(--border);padding-bottom:8px;">
                    <i class="fas fa-user"></i> ${ie}
                </h3>

                <div style="margin-bottom:16px;font-size:0.8rem;">
                    <span style="color:var(--text-muted);">Body Type:</span>
                    <span style="color:var(--text);margin-left:8px;">${he}</span>
                </div>

                <!-- Meta Sliders (Age, Mass, Tone, Height) -->
                <div style="margin-bottom:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <h4 style="font-size:0.8rem;margin-bottom:12px;color:var(--text);">
                        <i class="fas fa-sliders-h"></i> Meta-Parameter
                    </h4>
                    <div id="meta-sliders-container"></div>
                </div>

                <div style="margin-bottom:16px;">
                    <label style="display:block;font-size:0.8rem;color:var(--text-muted);margin-bottom:6px;">
                        Position
                    </label>
                    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;font-size:0.75rem;">
                        <div>
                            <span style="color:var(--text-muted);">X:</span>
                            <input type="number" id="char-pos-x" value="${me.x.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-pos-y" value="${me.y.toFixed(2)}" step="0.1"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-pos-z" value="${me.z.toFixed(2)}" step="0.1"
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
                            <input type="number" id="char-rot-x" value="${(Le.x*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Y:</span>
                            <input type="number" id="char-rot-y" value="${(Le.y*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                        <div>
                            <span style="color:var(--text-muted);">Z:</span>
                            <input type="number" id="char-rot-z" value="${(Le.z*180/Math.PI).toFixed(1)}" step="5"
                                   style="width:100%;padding:4px;background:var(--bg-primary);border:1px solid var(--border);border-radius:4px;color:var(--text);" />
                        </div>
                    </div>
                </div>

                <div style="font-size:0.75rem;color:var(--text-muted);margin-top:20px;padding-top:12px;border-top:1px solid var(--border);">
                    <i class="fas fa-info-circle"></i> Nutze die Transform-Controls in der Szene um Position/Rotation zu ändern
                </div>
            </div>
        `;const Ke=document.getElementById("char-pos-x"),bt=document.getElementById("char-pos-y"),et=document.getElementById("char-pos-z");if(Ke&&bt&&et){const Kt=()=>{V.position.set(parseFloat(Ke.value),parseFloat(bt.value),parseFloat(et.value))};Ke.oninput=Kt,bt.oninput=Kt,et.oninput=Kt}const Et=document.getElementById("char-rot-x"),$t=document.getElementById("char-rot-y"),Tn=document.getElementById("char-rot-z");if(Et&&$t&&Tn){const Kt=()=>{V.rotation.set(parseFloat(Et.value)*Math.PI/180,parseFloat($t.value)*Math.PI/180,parseFloat(Tn.value)*Math.PI/180)};Et.oninput=Kt,$t.oninput=Kt,Tn.oninput=Kt}Ie(V)}function Ie(V){const L=document.getElementById("meta-sliders-container");if(!L)return;const J={age:{min:-1,max:1,label:"Alter",step:.01},mass:{min:-1,max:1,label:"Gewicht",step:.01},tone:{min:-1,max:1,label:"Muskeltonus",step:.01},height:{min:-1,max:1,label:"Höhe",step:.01}},W=V.userData.meta||{age:0,mass:0,tone:0,height:0};let ie="";for(const[he,me]of Object.entries(J)){const Le=W[he]||0,Ke=me.min,bt=me.max;ie+=`
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:0.75rem;">
                        <span style="color:var(--text-muted);">${me.label}</span>
                        <span id="meta-${he}-value" style="color:var(--text);">${Le.toFixed(2)}</span>
                    </div>
                    <input type="range" id="meta-${he}" min="${Ke}" max="${bt}" step="${me.step}" value="${Le}"
                           style="width:100%;cursor:pointer;" />
                </div>
            `}L.innerHTML=ie;for(const he of Object.keys(J)){const me=document.getElementById(`meta-${he}`),Le=document.getElementById(`meta-${he}-value`);me&&Le&&(me.oninput=()=>{const Ke=parseFloat(me.value);Le.textContent=Ke.toFixed(2),W[he]=Ke,V.userData.meta=W,console.log("Meta changed:",he,Ke)})}}function pt(){const V=document.getElementById("properties-content");V&&(V.innerHTML=`
            <div style="padding:20px;color:var(--text-muted);font-size:0.85rem;text-align:center;">
                <i class="fas fa-hand-pointer" style="font-size:2rem;margin-bottom:10px;opacity:0.3;"></i>
                <p>Klicke auf ein Licht-Icon oder Character in der Szene<br>um Eigenschaften zu bearbeiten.</p>
            </div>
        `)}function it(){requestAnimationFrame(it);const V=U.getDelta();if(b&&ue&&(b.update(V*De),pe=B?B.time:0,pe>=de&&(pe=0,B&&(B.time=0)),ct()),f&&f.userData.light){const L=f.userData.light;L.position.copy(f.position),f.lookAt(L.target.position)}i.update(),n.render(e,t)}it()});
